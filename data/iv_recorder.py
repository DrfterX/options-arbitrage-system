"""
IV 历史记录模块 — 记录每个品种的 ATM IV，支持百分位计算。

使用 Database 统一连接工厂，表 ``iv_history`` 由 T01 schema 管理。
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Optional

from core.db import Database

logger = logging.getLogger(__name__)

# ── 百分位计算阈值 ─────────────────────────────────────────
MIN_SAMPLES_FOR_PERCENTILE = 20   # 至少需要20个交易日数据才能计算百分位
EXTREME_HIGH_MIN_IV = 0.18       # 极端高IV的绝对值下限（18%），低于此值不判极端高
EXTREME_LOW_MAX_IV = 0.40        # 极端低IV的绝对值上限（40%），高于此值不判极端低


class IVRecorder:
    """IV 历史记录器。

    从 T01 的 schema 使用已存在的 ``iv_history`` 表，
    通过 Database 获取连接，不再自行建表。

    Attributes:
        db: Database 连接工厂实例。
    """

    def __init__(self, db: Database) -> None:
        """初始化 IV 记录器。

        Args:
            db: Database 连接工厂。
        """
        self.db = db

    # ── 保存快照 ─────────────────────────────────────────────

    def save_snapshot(
        self,
        symbol: str,
        contract: str,
        price: float,
        calls: List[dict],
        puts: List[dict],
    ) -> bool:
        """保存当前 IV 快照到 ``iv_history`` 表。

        从 calls/puts 中提取 ATM IV 和 Top5 均值。

        Args:
            symbol: 品种代码。
            contract: 合约代码。
            price: 当前期货价格。
            calls: 看涨期权列表，每项含 ``{'strike', 'iv', 'price'}``。
            puts: 看跌期权列表，每项含 ``{'strike', 'iv', 'price'}``。

        Returns:
            保存成功返回 True，无数据返回 False。
        """
        if not calls and not puts:
            return False

        # 合并所有期权，找最接近期货价的ATM档
        all_opts: List[tuple] = []
        for c in calls:
            all_opts.append(("C", c["strike"], c["iv"], c["price"]))
        for p in puts:
            all_opts.append(("P", p["strike"], p["iv"], p["price"]))

        atm_opt = min(all_opts, key=lambda x: abs(x[1] - price))
        atm_strike = atm_opt[1]

        # ATM Call IV（价差<50的最近档）
        atm_call_iv = next(
            (c["iv"] for c in calls if abs(c["strike"] - price) < 50), 0.0
        )
        atm_put_iv = next(
            (p["iv"] for p in puts if abs(p["strike"] - price) < 50), 0.0
        )

        # Top5 平均 IV
        top5_call_iv = (
            sum(c["iv"] for c in calls) / len(calls) if calls else 0.0
        )
        top5_put_iv = (
            sum(p["iv"] for p in puts) / len(puts) if puts else 0.0
        )
        top5_avg_iv = (
            (top5_call_iv + top5_put_iv) / 2 if (calls or puts) else 0.0
        )
        avg_iv = (top5_call_iv + top5_put_iv) / 2

        today = date.today().isoformat()
        now = datetime.now().strftime("%H:%M:%S")

        conn = self.db.get_conn()
        try:
            conn.execute(
                """INSERT OR REPLACE INTO iv_history
                   (symbol, contract, date, time, futures_price, atm_strike,
                    atm_call_iv, atm_put_iv, avg_iv, top5_call_iv, top5_put_iv, top5_avg_iv)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    symbol,
                    contract,
                    today,
                    now,
                    price,
                    atm_strike,
                    atm_call_iv,
                    atm_put_iv,
                    avg_iv,
                    top5_call_iv,
                    top5_put_iv,
                    top5_avg_iv,
                ),
            )
            conn.commit()
            logger.debug("IV快照已保存: %s %s avg_iv=%.4f", symbol, contract, avg_iv)
            return True
        except Exception as e:
            logger.error("save_snapshot %s 失败: %s", symbol, e)
            return False
        finally:
            conn.close()

    # ── 查询历史 ─────────────────────────────────────────────

    def get_history(self, symbol: str, days: int = 30) -> List[dict]:
        """查询品种过去 N 天的 IV 历史。

        Args:
            symbol: 品种代码。
            days: 查询天数，默认 30。

        Returns:
            IV 历史记录列表（按日期降序），每项为字典。
        """
        conn = self.db.get_conn()
        try:
            rows = conn.execute(
                """SELECT * FROM iv_history
                   WHERE symbol=? ORDER BY date DESC LIMIT ?""",
                (symbol, days),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ── IV 百分位 ────────────────────────────────────────────

    def calc_percentile(
        self, symbol: str, current_iv: float, days: int = 30
    ) -> Optional[dict]:
        """计算当前 IV 在历史中的百分位和等级。

        Args:
            symbol: 品种代码。
            current_iv: 当前 IV 值（小数，如 0.25）。
            days: 回溯天数，默认 30。

        Returns:
            百分位统计字典，含 ``percentile`` / ``level`` / ``samples`` 等。
            历史数据不足 ``MIN_SAMPLES_FOR_PERCENTILE`` 条时返回 None。
        """
        history = self.get_history(symbol, days)
        if len(history) < MIN_SAMPLES_FOR_PERCENTILE:
            if len(history) > 0:
                logger.debug(
                    "%s 历史IV样本不足: %d条 (需要≥%d)",
                    symbol, len(history), MIN_SAMPLES_FOR_PERCENTILE,
                )
            return None

        # 取 avg_iv 列并排序
        ivs = sorted([h["avg_iv"] for h in history if h["avg_iv"] > 0])
        if not ivs:
            return None

        n = len(ivs)
        pct = sum(1 for iv in ivs if iv <= current_iv) / n * 100

        level = self._determine_iv_level(pct, current_iv)

        return {
            "symbol": symbol,
            "current_iv": round(current_iv, 4),
            "min_iv": round(ivs[0], 4),
            "p25": round(ivs[n // 4], 4),
            "p50": round(ivs[n // 2], 4),
            "p75": round(ivs[3 * n // 4], 4),
            "max_iv": round(ivs[-1], 4),
            "percentile": round(pct, 1),
            "samples": n,
            "level": level,
        }

    @staticmethod
    def _determine_iv_level(pct: float, current_iv: float) -> str:
        """根据百分位和绝对值确定IV等级。

        在百分位判定基础上，增加绝对值合理性校验：
        - 极端高要求 IV >= EXTREME_HIGH_MIN_IV（默认18%），否则降级为"偏高"
        - 极端低要求 IV <= EXTREME_LOW_MAX_IV（默认40%），否则降级为"偏低"
        """
        if pct >= 90:
            if current_iv < EXTREME_HIGH_MIN_IV:
                return "偏高"  # 绝对值过低，不可能是极端高
            return "极端高"
        if pct >= 70:
            return "偏高"
        if pct >= 30:
            return "正常"
        if pct >= 10:
            return "偏低"
        # 极端低
        if current_iv > EXTREME_LOW_MAX_IV:
            return "偏低"  # 绝对值过高，不可能是极端低
        return "极端低"

    # ── 所有品种 IV 状态 ─────────────────────────────────────

    def get_all_status(self, days: int = 30) -> List[dict]:
        """获取所有品种当前 IV 状态（百分位+等级+价格）。

        查询每个品种的最新 IV 快照，计算历史百分位和等级。

        Args:
            days: 回溯天数，默认 30。

        Returns:
            IV 状态列表，每项含 symbol / contract / current_iv / percentile /
            level / futures_price / samples 等。
        """
        conn = self.db.get_conn()
        try:
            # 获取每个品种最新一条记录
            rows = conn.execute(
                """SELECT DISTINCT symbol, contract FROM iv_history
                   WHERE date = (SELECT MAX(date) FROM iv_history)
                   ORDER BY symbol"""
            ).fetchall()

            results: List[dict] = []
            for r in rows:
                hist = conn.execute(
                    """SELECT * FROM iv_history
                       WHERE symbol=? ORDER BY date DESC LIMIT ?""",
                    (r["symbol"], days),
                ).fetchall()

                if not hist:
                    continue

                latest = dict(hist[0])
                ivs = sorted(
                    [h["avg_iv"] for h in hist if h["avg_iv"] > 0]
                )
                if not ivs:
                    continue

                current_iv = latest["avg_iv"]
                n = len(ivs)

                if n >= MIN_SAMPLES_FOR_PERCENTILE:
                    pct = sum(1 for iv in ivs if iv <= current_iv) / n * 100
                    level = self._determine_iv_level(pct, current_iv)
                else:
                    pct = 0.0
                    level = "数据不足"

                results.append({
                    "symbol": r["symbol"],
                    "contract": r["contract"],
                    "current_iv": round(current_iv, 4),
                    "min_iv": round(ivs[0], 4) if n >= MIN_SAMPLES_FOR_PERCENTILE else 0.0,
                    "max_iv": round(ivs[-1], 4) if n >= MIN_SAMPLES_FOR_PERCENTILE else 0.0,
                    "p50": (
                        round(ivs[n // 2], 4)
                        if n >= MIN_SAMPLES_FOR_PERCENTILE
                        else round(current_iv, 4)
                    ),
                    "percentile": round(pct, 1),
                    "level": level,
                    "futures_price": latest["futures_price"],
                    "samples": n,
                })

            return results

        finally:
            conn.close()


# ============================================================
# 模块自测入口
# ============================================================

if __name__ == "__main__":
    from config.settings import DB_PATH

    db = Database(DB_PATH)
    recorder = IVRecorder(db)

    # 获取所有品种 IV 状态
    status_list = recorder.get_all_status()
    for s in status_list:
        logger.info(
            "%s IV=%.1f%% pct=%.0f%% level=%s (n=%d)",
            s["symbol"],
            s["current_iv"] * 100,
            s["percentile"],
            s["level"],
            s["samples"],
        )
