"""
IV历史数据回补脚本 — 从交易所API拉取历史商品期权IV数据。

数据来源:
  - CZCE (郑商所): option_hist_yearly_czce → 一年批量，自带隐含波动率
  - SHFE (上期所): option_vol_shfe → 按交易日，自带隐含波动率
  - DCE  (大商所): option_hist_dce (API不稳定，暂跳过)

用法:
  python scripts/backfill_iv_history.py --exchange czce
  python scripts/backfill_iv_history.py --exchange shfe --date 20260604
  python scripts/backfill_iv_history.py --all
"""

import argparse
import logging
import math
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.db import Database
from config.settings import DB_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── CZCE 品种映射: 代码 → 中文名 ──────────────────────────
CZCE_VARIETIES: Dict[str, str] = {
    "SR": "白糖期权",
    "CF": "棉花期权",
    "MA": "甲醇期权",
    "TA": "PTA期权",
    "RM": "菜籽粕期权",
    "OI": "菜籽油期权",
    "PK": "花生期权",
    "PX": "对二甲苯期权",
    "SH": "烧碱期权",
    "SA": "纯碱期权",
    "PF": "短纤期权",
    "SM": "锰硅期权",
    "SF": "硅铁期权",
    "UR": "尿素期权",
    "AP": "苹果期权",
    "CJ": "红枣期权",
    "FG": "玻璃期权",
    "PR": "瓶片期权",
}

# ── SHFE 品种映射: 中文名 (用于 option_vol_shfe) ──────────
SHFE_VARIETIES: List[str] = [
    "原油期权", "铜期权", "铝期权", "锌期权", "铅期权",
    "螺纹钢期权", "镍期权", "锡期权", "氧化铝期权", "黄金期权",
    "白银期权", "丁二烯橡胶期权", "天胶期权",
]

# ── SHFE 中文名 → 代码 ────────────────────────────────────
SHFE_NAME_TO_CODE: Dict[str, str] = {
    "原油期权": "sc", "铜期权": "cu", "铝期权": "al",
    "锌期权": "zn", "铅期权": "pb", "螺纹钢期权": "rb",
    "镍期权": "ni", "锡期权": "sn", "氧化铝期权": "ao",
    "黄金期权": "au", "白银期权": "ag", "丁二烯橡胶期权": "br",
    "天胶期权": "ru",
}


def backfill_czce(db: Database, year: int = 2026) -> int:
    """从郑商所年度数据回补IV历史。

    使用 option_hist_yearly_czce 批量获取全年期权数据，
    对每个交易日提取ATM(Delta≈0.5)期权的隐含波动率均值。

    Args:
        db: Database连接。
        year: 数据年份。

    Returns:
        成功写入的记录数。
    """
    import akshare as ak

    total_stored = 0

    for code, name in CZCE_VARIETIES.items():
        logger.info("── CZCE %s (%s) ──", code, name)
        try:
            df = ak.option_hist_yearly_czce(symbol=code, year=str(year))
        except Exception as e:
            logger.warning("  API调用失败: %s", e)
            continue

        if df is None or df.empty:
            logger.warning("  无数据")
            continue

        # 清理列名
        df.columns = [c.strip() for c in df.columns]

        if "交易日期" not in df.columns or "隐含波动率" not in df.columns:
            logger.warning("  缺少必要列")
            continue

        # 过滤有效IV & 转换数值列
        df = df[df["隐含波动率"].notna() & (df["隐含波动率"] > 0)]
        df["隐含波动率"] = df["隐含波动率"].astype(float) / 100.0
        df["DELTA"] = pd.to_numeric(df["DELTA"], errors="coerce")
        df["今结算"] = pd.to_numeric(df["今结算"], errors="coerce").fillna(0)
        df["持仓量"] = pd.to_numeric(df["持仓量"], errors="coerce").fillna(0)

        # 按日期分组，每天提取ATM期权IV
        daily_iv: Dict[str, dict] = {}
        for trade_date, group in df.groupby("交易日期"):
            trade_date_str = str(trade_date)[:10]
            # 取 Delta 最接近 0.5 的看涨和 -0.5 的看跌
            near_atm = group[
                (group["DELTA"].abs() >= 0.35) &
                (group["DELTA"].abs() <= 0.65) &
                (group["今结算"] > 0)
            ]
            if near_atm.empty:
                # 放宽范围
                near_atm = group[
                    (group["DELTA"].abs() >= 0.2) &
                    (group["DELTA"].abs() <= 0.8) &
                    (group["今结算"] > 0)
                ]
            if near_atm.empty:
                continue

            avg_iv = near_atm["隐含波动率"].mean()

            # 估算标的期货价格（用ATM call+put推）
            calls = near_atm[near_atm["DELTA"] > 0]
            puts = near_atm[near_atm["DELTA"] < 0]
            if not calls.empty and not puts.empty:
                # 取Delta最接近0.5的C/P配对
                best_call = calls.iloc[(calls["DELTA"] - 0.5).abs().argsort()[:1]]
                best_put = puts.iloc[(puts["DELTA"] + 0.5).abs().argsort()[:1]]
                if not best_call.empty and not best_put.empty:
                    c_settle = float(best_call["今结算"].iloc[0])
                    p_settle = float(best_put["今结算"].iloc[0])
                    k_call = _extract_strike(best_call["合约代码"].iloc[0])
                    k_put = _extract_strike(best_put["合约代码"].iloc[0])
                    # 使用Put-Call Parity: F ≈ C-P+K (取平均)
                    if k_call and k_put:
                        futures_est = (c_settle - p_settle + k_call + k_put) / 2
                    elif k_call:
                        futures_est = c_settle - p_settle + k_call
                    elif k_put:
                        futures_est = c_settle - p_settle + k_put
                    else:
                        futures_est = 0.0
                else:
                    futures_est = 0.0
            else:
                futures_est = 0.0

            # 使用最大OI合约的行权价作为atm_strike
            try:
                best_oi_idx = near_atm["持仓量"].astype(float).idxmax()
            except (ValueError, KeyError):
                best_oi_idx = near_atm.index[0]
            atm_strike = _extract_strike(
                near_atm.loc[best_oi_idx, "合约代码"]
            ) or 0.0

            daily_iv[trade_date_str] = {
                "symbol": code.lower(),
                "contract": _guess_contract(code, trade_date_str),
                "date": trade_date_str,
                "futures_price": futures_est,
                "atm_strike": float(atm_strike),
                "avg_iv": avg_iv,
            }

        # 写入数据库
        conn = db.get_conn()
        stored = 0
        try:
            for d, rec in sorted(daily_iv.items()):
                try:
                    conn.execute(
                        """INSERT OR REPLACE INTO iv_history
                           (symbol, contract, date, time, futures_price, atm_strike,
                            atm_call_iv, atm_put_iv, avg_iv,
                            top5_call_iv, top5_put_iv, top5_avg_iv)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            rec["symbol"],
                            rec["contract"],
                            rec["date"],
                            "15:00:00",
                            rec["futures_price"],
                            rec["atm_strike"],
                            rec["avg_iv"],
                            rec["avg_iv"],
                            rec["avg_iv"],
                            rec["avg_iv"],
                            rec["avg_iv"],
                            rec["avg_iv"],
                        ),
                    )
                    stored += 1
                except Exception as e:
                    logger.debug("  写入失败 %s: %s", d, e)
            conn.commit()
        finally:
            conn.close()

        logger.info("  写入 %d 条 (%d 个交易日)", stored, len(daily_iv))
        total_stored += stored
        time.sleep(2)  # 避免触发反爬

    return total_stored


def backfill_shfe(db: Database, start_date: str, end_date: str) -> int:
    """从上期所每日波动率数据回补IV历史。

    使用 option_vol_shfe 获取合约系列隐含波动率。

    Args:
        db: Database连接。
        start_date: 起始日期 (YYYYMMDD)。
        end_date: 结束日期 (YYYYMMDD)。

    Returns:
        成功写入的记录数。
    """
    import akshare as ak

    total_stored = 0

    # 生成交易日列表
    date_range = pd.bdate_range(start=start_date, end=end_date)

    for variety_name in SHFE_VARIETIES:
        code = SHFE_NAME_TO_CODE.get(variety_name, "").lower()
        if not code:
            continue
        logger.info("── SHFE %s (%s) ──", code, variety_name)

        stored = 0
        for dt in date_range:
            d_str = dt.strftime("%Y%m%d")
            try:
                df = ak.option_vol_shfe(
                    symbol=variety_name, trade_date=d_str
                )
            except Exception as e:
                logger.debug("  %s: %s", d_str, e)
                continue

            if df is None or df.empty:
                continue

            # 转换数值列
            df["隐含波动率"] = pd.to_numeric(df["隐含波动率"], errors="coerce")
            df["成交量"] = pd.to_numeric(df["成交量"], errors="coerce")

            # 取隐含波动率非零的行
            df_valid = df[df["隐含波动率"].notna() & (df["隐含波动率"] > 0)]
            if df_valid.empty:
                continue

            # 取中位数IV作为代表
            avg_iv = float(df_valid["隐含波动率"].median())

            # 取成交量最大的合约
            best = df_valid.loc[df_valid["成交量"].idxmax()]
            contract_series = str(best["合约系列"]) if "合约系列" in df.columns else ""

            conn = db.get_conn()
            try:
                conn.execute(
                    """INSERT OR REPLACE INTO iv_history
                       (symbol, contract, date, time, futures_price, atm_strike,
                        atm_call_iv, atm_put_iv, avg_iv,
                        top5_call_iv, top5_put_iv, top5_avg_iv)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        code,
                        contract_series,
                        dt.strftime("%Y-%m-%d"),
                        "15:00:00",
                        0.0,
                        0.0,
                        avg_iv,
                        avg_iv,
                        avg_iv,
                        avg_iv,
                        avg_iv,
                        avg_iv,
                    ),
                )
                conn.commit()
                stored += 1
            finally:
                conn.close()

            time.sleep(0.5)

        logger.info("  写入 %d 条", stored)
        total_stored += stored

    return total_stored


def _extract_strike(contract_code: str) -> Optional[float]:
    """从期权合约代码提取行权价。

    例如: SR607C4600 → 4600, rb2607C2600 → 2600
    """
    import re
    # 匹配末尾数字(行权价)
    m = re.search(r'[CP](\d+)$', contract_code)
    if m:
        return float(m.group(1))
    return None


def _guess_contract(code: str, date_str: str) -> str:
    """根据品种代码和日期推测主力合约。"""
    from datetime import datetime
    dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
    month = dt.month
    # 简单推测：取当前季度内最近的奇数月合约
    if month <= 3:
        m = "05"
    elif month <= 6:
        m = "09" if month >= 5 else "07"
    elif month <= 9:
        m = "09"
    else:
        m = "11" if month <= 11 else "01"
    year_suffix = str(dt.year)[2:]
    return f"{code.upper()}{year_suffix}{m}"


# ── DCE 品种数据 (通过Sina日线计算IV) ─────────────────────
DCE_SINA_VARIETIES: Dict[str, str] = {
    "c":  "玉米期权",
    "m":  "豆粕期权",
    "i":  "铁矿石期权",
    "pg": "液化石油气期权",
    "l":  "聚乙烯期权",
    "v":  "聚氯乙烯期权",
    "pp": "聚丙烯期权",
    "p":  "棕榈油期权",
    "a":  "黄大豆1号期权",
    "b":  "黄大豆2号期权",
    "y":  "豆油期权",
    "eg": "乙二醇期权",
    "eb": "苯乙烯期权",
    "jd": "鸡蛋期权",
    "cs": "玉米淀粉期权",
    "lh": "生猪期权",
}

# ── DCE常用ATM行权价参考（取近似主力合约当前价附近的整百数）──
DCE_ATM_STRIKES: Dict[str, int] = {
    "c":  2300, "m": 2800, "i": 700, "pg": 4000,
    "l":  7800, "v": 5100, "pp": 7000, "p": 7800,
    "a":  4200, "b": 3700, "y": 7800, "eg": 4000,
    "eb": 8000, "jd": 3500, "cs": 2500, "lh": 14000,
}


def backfill_dce_sina(db: Database) -> int:
    """通过Sina日线数据计算DCE品种历史IV。

    使用 futures_zh_daily_sina 获取期货结算价，
    option_commodity_hist_sina 获取期权收盘价，
    Black-76公式反推隐含波动率。

    Args:
        db: Database连接。

    Returns:
        成功写入的记录数。
    """
    import akshare as ak
    from scipy.stats import norm
    from scipy.optimize import brentq

    total_stored = 0

    for code, name in DCE_SINA_VARIETIES.items():
        logger.info("── DCE %s (%s) via Sina ──", code, name)

        atm_strike = DCE_ATM_STRIKES.get(code, 3000)
        fut_symbol = f"{code.upper()}2609"  # 假设09月主力

        # 1. 获取期货日线数据
        try:
            fut_df = ak.futures_zh_daily_sina(symbol=fut_symbol)
        except Exception as e:
            logger.warning("  期货数据获取失败 %s: %s", fut_symbol, e)
            # 尝试其他月份
            for m in ["2607", "2605", "2601", "2509"]:
                try:
                    fut_df = ak.futures_zh_daily_sina(
                        symbol=f"{code.upper()}{m}"
                    )
                    fut_symbol = f"{code.upper()}{m}"
                    break
                except Exception:
                    continue
            else:
                logger.warning("  所有期货合约都失败")
                continue

        if fut_df is None or fut_df.empty:
            continue

        # 2. 获取ATM期权日线
        call_sym = f"{code}2609C{atm_strike}"
        put_sym = f"{code}2609P{atm_strike}"

        try:
            call_df = ak.option_commodity_hist_sina(symbol=call_sym)
        except Exception:
            logger.debug("  %s 数据不可用", call_sym)
            call_df = None

        try:
            put_df = ak.option_commodity_hist_sina(symbol=put_sym)
        except Exception:
            logger.debug("  %s 数据不可用", put_sym)
            put_df = None

        if call_df is None and put_df is None:
            logger.warning("  无可用期权数据")
            continue

        # 3. 合并数据，按日期对齐
        fut_df = fut_df.set_index("date")
        opt_dates = set()
        if call_df is not None:
            opt_dates.update(call_df["date"].tolist())
        if put_df is not None:
            opt_dates.update(put_df["date"].tolist())

        conn = db.get_conn()
        stored = 0
        try:
            for d in sorted(opt_dates):
                d_str = str(d)[:10]
                if d_str not in fut_df.index:
                    continue

                settle = fut_df.loc[d_str, "settle"]
                if pd.isna(settle) or settle <= 0:
                    continue

                # 提取call和put的收盘价
                call_close = None
                put_close = None
                if call_df is not None:
                    c_row = call_df[call_df["date"] == d]
                    if not c_row.empty and c_row["close"].iloc[0] > 0:
                        call_close = float(c_row["close"].iloc[0])
                if put_df is not None:
                    p_row = put_df[put_df["date"] == d]
                    if not p_row.empty and p_row["close"].iloc[0] > 0:
                        put_close = float(p_row["close"].iloc[0])

                # 估算DTE (从日期推算)
                parts = d_str.split("-")
                exp_parts = [f"20{fut_symbol[-4:-2]}", fut_symbol[-2:]]
                try:
                    exp_date = date(int(exp_parts[0]), int(exp_parts[1]), 15)
                    dte = max((exp_date - date(int(parts[0]), int(parts[1]), int(parts[2]))).days, 1)
                except (ValueError, IndexError):
                    dte = 30

                # 计算IV
                avg_iv = 0.0
                iv_count = 0

                for opt_close, opt_type in [(call_close, "C"), (put_close, "P")]:
                    if opt_close is None or opt_close <= 0:
                        continue
                    try:
                        iv = _black76_iv(
                            price=opt_close,
                            F=float(settle),
                            K=float(atm_strike),
                            T=max(dte / 365.0, 0.005),
                            r=0.02,
                            option_type=opt_type,
                        )
                        if iv and iv > 0.001 and iv < 2.0:
                            avg_iv += iv
                            iv_count += 1
                    except Exception:
                        pass

                if iv_count == 0:
                    continue

                avg_iv /= iv_count

                conn.execute(
                    """INSERT OR REPLACE INTO iv_history
                       (symbol, contract, date, time, futures_price, atm_strike,
                        atm_call_iv, atm_put_iv, avg_iv,
                        top5_call_iv, top5_put_iv, top5_avg_iv)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        code, fut_symbol, d_str, "15:00:00",
                        float(settle), float(atm_strike),
                        avg_iv, avg_iv, avg_iv,
                        avg_iv, avg_iv, avg_iv,
                    ),
                )
                stored += 1

            conn.commit()
        finally:
            conn.close()

        logger.info("  写入 %d 条", stored)
        total_stored += stored
        time.sleep(2)

    return total_stored


def _black76_iv(price: float, F: float, K: float, T: float,
                r: float, option_type: str) -> Optional[float]:
    """Black-76 反推隐含波动率。"""
    from scipy.stats import norm
    from scipy.optimize import brentq

    if T <= 0 or price <= 0 or F <= 0 or K <= 0:
        return None

    def black76_price(sigma):
        d1 = (math.log(F / K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        if option_type == "C":
            return math.exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2))
        else:
            return math.exp(-r * T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1))

    # Intrinsic value (no time value → IV=0)
    if option_type == "C" and price <= max(0, (F - K) * math.exp(-r * T)):
        return 0.0
    if option_type == "P" and price <= max(0, (K - F) * math.exp(-r * T)):
        return 0.0

    try:
        iv = brentq(
            lambda s: black76_price(s) - price,
            0.001, 2.0, maxiter=100, xtol=1e-6,
        )
        return float(iv)
    except (ValueError, RuntimeError):
        return None


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="IV历史数据回补")
    parser.add_argument(
        "--exchange", choices=["czce", "shfe", "dce", "all"],
        default="all", help="目标交易所 (default: all)"
    )
    parser.add_argument(
        "--year", type=int, default=2026,
        help="CZCE数据年份 (default: 2026)"
    )
    parser.add_argument(
        "--start", type=str, default="20251201",
        help="SHFE起始日期 YYYYMMDD (default: 20251201)"
    )
    parser.add_argument(
        "--end", type=str, default=None,
        help="SHFE结束日期 YYYYMMDD (default: 今天)"
    )
    parser.add_argument(
        "--db", type=str, default=DB_PATH,
        help=f"数据库路径 (default: {DB_PATH})"
    )
    args = parser.parse_args()

    if args.end is None:
        args.end = date.today().strftime("%Y%m%d")

    db = Database(args.db)
    total = 0

    if args.exchange in ("czce", "all"):
        logger.info("========== CZCE 回补 (%d年) ==========", args.year)
        n = backfill_czce(db, year=args.year)
        logger.info("CZCE完成: %d 条", n)
        total += n

    if args.exchange in ("shfe", "all"):
        logger.info("========== SHFE 回补 (%s ~ %s) ==========",
                     args.start, args.end)
        n = backfill_shfe(db, start_date=args.start, end_date=args.end)
        logger.info("SHFE完成: %d 条", n)
        total += n

    if args.exchange in ("dce", "all"):
        logger.info("========== DCE 回补 (Sina日线+Black76) ==========")
        n = backfill_dce_sina(db)
        logger.info("DCE完成: %d 条", n)
        total += n

    logger.info("═══════════════════")
    logger.info("总计写入: %d 条", total)


if __name__ == "__main__":
    main()
