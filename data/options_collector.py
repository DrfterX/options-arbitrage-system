"""
期权链数据采集模块 — 获取期货期权链原始数据及 Black-76 定价。

负责获取 TOP40 期货实时行情和期权链数据（含 IV 反推与 Greeks 计算）。
Black-76 定价函数作为数据采集的一部分，供后续策略引擎引用。
"""

import time
import math
import logging
import os
import sqlite3
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

from scipy.stats import norm  # type: ignore[import-untyped]
from scipy.optimize import brentq  # type: ignore[import-untyped]

from config.contracts import ContractRegistry
from config.settings import (
    SINA_API_TIMEOUT,
    SINA_API_RETRY,
    SLEEP_INTERVAL,
    AKSHARE_TIMEOUT,
    AKSHARE_RETRY,
)

logger = logging.getLogger(__name__)

try:
    import akshare as ak  # type: ignore[import-untyped]

    AK_AVAILABLE = True
except ImportError:
    AK_AVAILABLE = False
    logger.warning("akshare 未安装，请执行 pip install akshare")


# ============================================================
# API 重试工具
# ============================================================

def api_retry(fn, *args, retries: int = 2, delay: float = 1.0, **kwargs):
    """轻量级 API 重试装饰器/包装器。

    捕获 Exception，最多重试 ``retries`` 次，每次间隔 ``delay`` 秒。
    可以作为函数包装器直接调用。

    Args:
        fn: 要执行的函数。
        *args: 位置参数。
        retries: 最大重试次数（不含首次调用）。
        delay: 重试间隔秒数。
        **kwargs: 关键字参数。

    Returns:
        函数返回值。

    Raises:
        最后一次尝试的异常。
    """
    for attempt in range(retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if attempt < retries:
                logger.warning("retry %s (%d/%d): %s", fn.__name__, attempt + 1, retries, e)
                time.sleep(delay)
            else:
                logger.error("retry %s 耗尽: %s", fn.__name__, e)
                raise


def _ensure_akshare() -> None:
    """检查 akshare 是否可用。"""
    if not AK_AVAILABLE:
        raise ImportError("akshare 未安装，请执行 pip install akshare")


# ============================================================
# Black-76 定价模型
# ============================================================

def black_price(
    F: float, K: float, T: float, r: float, sigma: float, is_call: bool
) -> float:
    """Black-76 期货期权定价（委托 options/pricing.py）。"""
    from options.pricing import black_price as _bp
    return _bp(F, K, T, r, sigma, is_call)


def black_greeks(
    F: float, K: float, T: float, r: float, sigma: float, is_call: bool
) -> dict:
    """Black-76 Greeks（委托 options/pricing.py）。"""
    from options.pricing import black_greeks as _bg
    return _bg(F, K, T, r, sigma, is_call)


def calc_iv(
    mp: float, F: float, K: float, T: float, r: float, is_call: bool
) -> float:
    """从市场价格反推隐含波动率（Black-76 模型）。

    使用 brentq 迭代求解。若 mp ≤ 0 或 T ≤ 0 返回 0。
    主区间 [0.001, 8.0]，失败后扩展至 [0.0001, 20.0]，
    仍失败则用平价近似。

    Args:
        mp: 期权市场价格。
        F: 期货价格。
        K: 行权价。
        T: 到期时间（年）。
        r: 无风险利率。
        is_call: True 为看涨。

    Returns:
        隐含波动率（小数，如 0.25 代表 25%）。异常时返回近似值或 0。
    """
    if mp <= 0 or T <= 0:
        return 0.0

    # 主区间
    try:
        return float(
            brentq(
                lambda s: black_price(F, K, T, r, s, is_call) - mp,
                0.001,
                8.0,
                maxiter=200,
            )
        )
    except Exception:
        # 扩展区间
        try:
            return float(
                brentq(
                    lambda s: black_price(F, K, T, r, s, is_call) - mp,
                    0.0001,
                    20.0,
                    maxiter=200,
                )
            )
        except Exception:
            # 平价近似
            iv = abs((mp / (F * math.exp(-r * T))) * 2) if F > 0 else 0.0
            logger.debug(
                "calc_iv失败: mp=%.2f F=%.1f K=%.1f T=%.3f → 近似IV=%.2f%%",
                mp, F, K, T, iv * 100,
            )
            return iv


def estimate_expiry(contract: str) -> date:
    """估算期权到期日：合约月份前1个月的25日（保守估计）。

    例如合约 ``'RB2609'`` 表示2026年9月合约，
    到期日估算为2026年8月25日。

    注意：实际到期日因交易所/品种而异（SHFE 最后交易日为
    到期月第5日，DCE/CZCE 为第10日等），此处为统一保守估值。

    Args:
        contract: 合约代码，如 ``'RB2609'``。

    Returns:
        估算的到期日。
    """
    m = int(contract[-2:])
    y = int("20" + contract[-4:-2])
    em = m - 1 if m > 1 else 12
    ey = y if em < m else y - 1
    return date(ey, em, 25)


# ============================================================
# 线程安全单品种K线获取
# ============================================================

def _fetch_single_kline(
    px: str, co: str, name: str = ""
) -> Optional[dict]:
    """线程安全：获取单个品种15分钟K线（含重试）。

    供 ``OptionsCollector.get_top40_futures`` 在多线程中调用。

    Args:
        px: 品种代码。
        co: 合约代码。
        name: 品种中文名。

    Returns:
        期货行情字典 ``{'code', 'name', 'contract', 'price', 'oi', 'time'}``，
        失败返回 None。
    """
    nm = name if name else px
    for attempt in range(3):
        try:
            df = ak.futures_zh_minute_sina(symbol=co, period="15")
            if df is not None and not df.empty:
                la = df.iloc[-1]
                oi_val = float(la.get("hold", 0))
                price_val = float(la.get("close", 0))
                if oi_val > 0 and price_val > 0:
                    return {
                        "code": px,
                        "name": nm,
                        "contract": co,
                        "price": price_val,
                        "oi": oi_val,
                        "time": str(la.get("datetime", ""))[:19],
                    }
        except Exception:
            if attempt < 2:
                time.sleep(1.0 * (attempt + 1))
    return None


# ============================================================
# OptionsCollector
# ============================================================

class OptionsCollector:
    """期权数据采集器。

    获取期货实时行情和期权链数据（含 IV 反推与 Greeks 计算）。
    通过 ContractRegistry 获取品种→期权名映射。

    Attributes:
        registry: ContractRegistry 品种注册表实例。
        _contract_cache: 主力合约运行时缓存 ``{symbol: contract_code}``。
    """

    # 上次成功扫描的合约缓存（每月变化，不适合存DB）
    _contract_cache: Dict[str, str] = {}

    def __init__(self, registry: ContractRegistry) -> None:
        """初始化期权数据采集器。

        Args:
            registry: 品种注册表。
        """
        self.registry = registry

        # 首次初始化时填充缓存
        if not OptionsCollector._contract_cache:
            self._init_contract_cache()

    def _init_contract_cache(self) -> None:
        """从 registry 数据填充合约缓存。

        对每个品种探测当前活跃的主力合约代码（如 RB2609），
        而非仅缓存品种名。通过 Sina 15m K线验证合约有效性。

        ⚠ 关键：节流条件必须基于总 API 调用次数而非 resolved 计数，
          否则非交易时段 resolved=0 时全部调用背靠背执行 → 限流 → 0/59。
        """
        try:
            import akshare as ak
            from datetime import datetime

            all_symbols = self.registry.get_with_options()
            now = datetime.now()
            year_suffix = str(now.year)[2:]  # "26"

            # 按优先级排列的合约月份（根据当前月份调序）
            month = now.month
            if month <= 2:
                month_order = ["05", "03", "01", "07", "09"]
            elif month <= 5:
                month_order = ["09", "07", "05", "10", "01"]
            elif month <= 8:
                month_order = ["09", "07", "10", "11", "01"]
            elif month <= 11:
                month_order = ["01", "11", "09", "10", "03"]
            else:
                month_order = ["05", "03", "01", "07", "09"]

            resolved: int = 0
            call_count: int = 0  # 总 API 调用计数（不分成功/失败）
            for s in all_symbols:
                symbol = s["symbol"].upper()
                contract = None

                # 遍历可能的合约月份（最多尝试 3 个候选以快速失败）
                for m in month_order[:3]:
                    candidate = f"{symbol}{year_suffix}{m}"
                    call_count += 1
                    # ★ 节流：每 3 次调用暂停，不依赖 resolved 计数
                    if call_count % 3 == 0:
                        time.sleep(0.5)
                    elif call_count % 3 == 2:
                        time.sleep(0.15)
                    try:
                        df = ak.futures_zh_minute_sina(
                            symbol=candidate, period="15"
                        )
                        if df is not None and not df.empty:
                            oi = float(df.iloc[-1].get("hold", 0))
                            if oi > 0:
                                contract = candidate
                                break
                    except Exception:
                        continue

                # 尝试下一年份月份（仅当月候选全失败时，限 2 个）
                if contract is None:
                    next_year = str(now.year + 1)[2:]
                    for m in ["01", "03"]:
                        candidate = f"{symbol}{next_year}{m}"
                        call_count += 1
                        if call_count % 3 == 0:
                            time.sleep(0.5)
                        elif call_count % 3 == 2:
                            time.sleep(0.15)
                        try:
                            df = ak.futures_zh_minute_sina(
                                symbol=candidate, period="15"
                            )
                            if df is not None and not df.empty:
                                oi = float(df.iloc[-1].get("hold", 0))
                                if oi > 0:
                                    contract = candidate
                                    break
                        except Exception:
                            continue

                if contract:
                    OptionsCollector._contract_cache[symbol.lower()] = contract
                    resolved += 1
                else:
                    # 回退到品种名本身
                    OptionsCollector._contract_cache[symbol.lower()] = symbol

            logger.info(
                "合约缓存已初始化: %d/%d 品种成功解析主力合约 (API调用总次数=%d)",
                resolved, len(all_symbols), call_count,
            )
        except Exception as e:
            logger.warning("合约缓存初始化异常: %s (使用品种名回退)", e)
            # 回退方案
            try:
                all_symbols = self.registry.get_with_options()
                for s in all_symbols:
                    symbol = s["symbol"]
                    OptionsCollector._contract_cache[symbol.lower()] = symbol
            except Exception:
                pass

    # ── TOP40 期货行情 ───────────────────────────────────────

    def get_top40_futures(self, exclude: Optional[set] = None) -> List[dict]:
        """获取 TOP40 期货主力合约实时行情（Sina 15m K线，多线程）。

        从 registry 获取有期权的品种列表，对每个品种通过缓存查询合约代码，
        使用线程池并发获取15分钟K线最新行情。
        Sina不可用时回退到 futures_kline.db 缓存数据。

        Args:
            exclude: 排除的品种代码集合，默认排除
                ``{'AU','AG','CU','IF','IH','IC','IM'}``。

        Returns:
            TOP40 期货行情列表（按持仓量降序），每项含:
            ``{'code', 'name', 'contract', 'price', 'oi', 'time'}``。
        """
        _ensure_akshare()

        if exclude is None:
            exclude = {"AU", "AG", "CU", "IF", "IH", "IC", "IM"}

        results: List[dict] = []

        # 从 registry 获取有期权的品种列表
        option_symbols = self.registry.get_with_options()

        futures_map: dict = {}
        with ThreadPoolExecutor(max_workers=8) as pool:
            for s in option_symbols:
                symbol = s["symbol"]
                if symbol.upper() in exclude:
                    continue

                # 从缓存查合约
                co = OptionsCollector._contract_cache.get(
                    symbol.lower(), symbol
                )
                name = s.get("name", symbol)
                f = pool.submit(_fetch_single_kline, symbol, co, name)
                futures_map[f] = symbol

            for f in as_completed(futures_map):
                r = f.result()
                if r:
                    results.append(r)

        # Sina不可用时回退到 futures_kline.db
        if not results:
            results = self._fallback_futures_from_kline_db(option_symbols, exclude)

        results.sort(key=lambda x: x["oi"], reverse=True)
        return results[:40]

    def _fallback_futures_from_kline_db(
        self, option_symbols: list, exclude: set
    ) -> List[dict]:
        """从 futures_signal 的 kline 数据库回退读取最新行情。

        当 Sina API 不可用时使用此方式获取期货收盘价和持仓量。
        """
        kline_db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "futures_signal", "futures_kline.db",
        )

        if not os.path.exists(kline_db_path):
            # 尝试 alternate path（已归档的原项目）
            kline_db_path = os.path.expanduser(
                "~/options_arbitrage_system/futures_signal_ARCHIVED/futures_kline.db"
            )

        if not os.path.exists(kline_db_path):
            logger.debug("futures_kline.db 不存在，无法回退")
            return []

        results: List[dict] = []
        try:
            conn = sqlite3.connect(kline_db_path)
            # 取最新时间戳对应数据（15分钟K线）
            latest_ts_row = conn.execute(
                "SELECT MAX(timestamp) FROM futures_klines "
                "WHERE timeframe='15m' AND timestamp>0"
            ).fetchone()
            if not latest_ts_row or not latest_ts_row[0]:
                conn.close()
                return []
            latest_ts = latest_ts_row[0]

            # 获取该时间戳下所有品种数据
            rows = conn.execute(
                "SELECT symbol, contract, close, volume FROM futures_klines "
                "WHERE timeframe='15m' AND timestamp=? AND close>0 AND volume>0",
                (latest_ts,),
            ).fetchall()

            # 按品种取最新合约（最高volume作为OI近似）
            seen: Dict[str, tuple] = {}
            for r in rows:
                sym = r[0]
                if sym.upper() in exclude:
                    continue
                contract = r[1]
                close = r[2]
                vol = r[3]
                if sym not in seen or vol > seen[sym][3]:
                    seen[sym] = (sym, contract, close, vol)

            # 匹配 registry 中的中文名
            name_map = {s["symbol"]: s.get("name", s["symbol"]) for s in option_symbols}

            for sym, contract, close, oi in seen.values():
                name = name_map.get(sym, sym)
                ts_str = datetime.fromtimestamp(latest_ts).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                results.append({
                    "code": sym,
                    "name": name,
                    "contract": contract,
                    "price": close,
                    "oi": oi,
                    "time": ts_str,
                })

            conn.close()
            logger.info(
                "回退模式: 从 futures_kline.db 读取 %d 个品种行情", len(results)
            )
        except Exception as e:
            logger.warning("回退读取 futures_kline.db 失败: %s", e)

        return results

    # ── 期权链获取 ───────────────────────────────────────────

    def get_option_chain(
        self, symbol_name: str, contract: str, futures_price: float, symbol: str = ""
    ) -> Tuple[List[dict], List[dict]]:
        """获取期权链原始数据（含 IV + Greeks），多策略回退。

        策略顺序：
        1. Sina table API（主力月份，失败则试相邻月份 ±1/±2）
        2. SHFE exchange API（当品种为 SHFE 时）
        3. CZCE exchange API（当品种为 CZCE 时，用当日或前一日）

        Args:
            symbol_name: 期权名称（如 ``'螺纹钢期权'``）。
            contract: 合约代码（如 ``'RB2609'``）。
            futures_price: 标的价格。
            symbol: 品种代码（如 ``'RB'``），用于交易所判断。

        Returns:
            ``(calls, puts)`` 元组，每项为 Top5 期权字典列表。
        """
        # 获取交易所
        exchange = self._get_exchange_from_symbol(symbol)

        # 策略1: Sina table API — 多月份迭代
        contract_variants = self._expand_contract_months(contract)
        for cv in contract_variants:
            calls, puts = self._try_sina_table(symbol_name, cv, futures_price)
            if calls or puts:
                return calls, puts

        # 策略2: SHFE exchange API
        if exchange == "SHFE":
            calls, puts = self._try_shfe_api(symbol_name, futures_price, contract)
            if calls or puts:
                return calls, puts

        # 策略3: CZCE exchange API（用当日或前一日）
        if exchange == "CZCE":
            calls, puts = self._try_czce_api(symbol_name, futures_price, contract)
            if calls or puts:
                return calls, puts

        return [], []

    def _get_exchange_from_symbol(self, symbol: str) -> str:
        """通过品种代码获取交易所代码。"""
        if not symbol:
            return ""
        info = self.registry.get(symbol)
        return info.get("exchange", "") if info else ""

    def _expand_contract_months(self, contract: str) -> List[str]:
        """扩展合约月份：先原月份，再尝试相邻月份。

        如 ``'AG2609'`` → ``['AG2609', 'AG2610', 'AG2608', 'AG2611', 'AG2607']``
        """
        sym = contract[:-4]  # 'AG'
        try:
            year = int(contract[-4:-2])  # 26
            month = int(contract[-2:])  # 9
        except ValueError:
            return [contract]

        variants = [contract]
        for offset in [1, -1, 2, -2]:
            m = month + offset
            y = year
            if m > 12:
                m -= 12
                y += 1
            elif m < 1:
                m += 12
                y -= 1
            if 1 <= m <= 12:
                variants.append(f"{sym}{y:02d}{m:02d}")
        return variants

    def _try_sina_table(
        self, symbol_name: str, contract: str, futures_price: float
    ) -> Tuple[List[dict], List[dict]]:
        """尝试通过 Sina option_commodity_contract_table_sina 获取期权链。"""
        r = 0.02
        expiry = estimate_expiry(contract)
        T = max((expiry - date.today()).days, 1) / 365.0
        try:
            df = ak.option_commodity_contract_table_sina(
                symbol=symbol_name, contract=contract
            )
            if df is None or df.empty:
                return [], []
        except Exception as e:
            logger.debug("_try_sina_table: %s %s → %s", symbol_name, contract, e)
            return [], []

        return self._parse_sina_table(df, futures_price, T, r)

    @staticmethod
    def _parse_sina_table(
        df, futures_price: float, T: float, r: float
    ) -> Tuple[List[dict], List[dict]]:
        """解析 Sina 期权合约表 DataFrame 为 calls/puts 列表。"""
        opts: List[dict] = []
        for _, row in df.iterrows():
            strike = float(row["行权价"])
            for ot, cp, ic in [("C", "看涨合约", True), ("P", "看跌合约", False)]:
                oi = float(row.get(f"{cp}-持仓量", 0))
                price = float(row.get(f"{cp}-最新价", 0))
                code = row.get(f"{cp}-{cp}期权合约", "")
                if oi > 0 and price > 0:
                    iv = calc_iv(price, futures_price, strike, T, r, ic)
                    g = black_greeks(futures_price, strike, T, r, iv, ic)
                    intrinsic = (
                        max(0, futures_price - strike)
                        if ic
                        else max(0, strike - futures_price)
                    )
                    opts.append({
                        "type": ot,
                        "code": code,
                        "strike": strike,
                        "price": price,
                        "oi": oi,
                        "iv": iv,
                        "delta": g["delta"],
                        "gamma": g["gamma"],
                        "theta": g["theta"],
                        "vega": g["vega"],
                        "intrinsic": intrinsic,
                        "time_value": max(price - intrinsic, 0),
                    })

        calls = sorted(
            [o for o in opts if o["type"] == "C"],
            key=lambda x: x["oi"],
            reverse=True,
        )[:5]
        puts = sorted(
            [o for o in opts if o["type"] == "P"],
            key=lambda x: x["oi"],
            reverse=True,
        )[:5]
        return calls, puts

    def _try_shfe_api(
        self, symbol_name: str, futures_price: float, contract: str
    ) -> Tuple[List[dict], List[dict]]:
        """通过 SHFE option_hist_shfe 获取期权链（含交易所计算的德尔塔值）。"""
        today_str = date.today().strftime("%Y%m%d")
        try:
            df = ak.option_hist_shfe(symbol=symbol_name, trade_date=today_str)
            if df is None or df.empty:
                return [], []
        except Exception as e:
            logger.debug("_try_shfe_api: %s → %s", symbol_name, e)
            return [], []

        # 判断日期是否非交易日（数据全零或极少行）
        if len(df) < 50:
            return [], []

        return self._parse_exchange_options(df, futures_price, contract, exchange="SHFE")

    def _try_czce_api(
        self, symbol_name: str, futures_price: float, contract: str
    ) -> Tuple[List[dict], List[dict]]:
        """通过 CZCE option_hist_czce 获取期权链（含交易所计算的隐含波动率与德尔塔）。

        先尝试当日，失败则用前一日。
        """
        today_str = date.today().strftime("%Y%m%d")
        yesterday_str = (date.today().day - 1).__str__()  # 备用
        from datetime import timedelta
        yesterday_str = (date.today() - timedelta(days=1)).strftime("%Y%m%d")

        for dt in [today_str, yesterday_str]:
            try:
                df = ak.option_hist_czce(symbol=symbol_name, trade_date=dt)
                if df is not None and not df.empty and len(df) > 50:
                    return self._parse_exchange_options(df, futures_price, contract, exchange="CZCE")
            except Exception as e:
                logger.debug("_try_czce_api: %s %s → %s", symbol_name, dt, e)
        return [], []

    @staticmethod
    def _parse_exchange_options(
        df, futures_price: float, contract: str, exchange: str = "SHFE"
    ) -> Tuple[List[dict], List[dict]]:
        """解析交易所 API（SHFE/CZCE）返回的 DataFrame。

        SHFE 列: 合约代码, 收盘价, 持仓量, 德尔塔, 结算价, 行权量
        CZCE 列: 合约代码, 今收盘, 持仓量, DELTA, 隐含波动率

        Args:
            contract: 主力合约代码（如 AG2609），用于月份过滤。
        """
        r = 0.02
        opts: List[dict] = []

        # 提取目标月份（合约代码后缀，如 '2609'）
        target_month_suffix = contract[-4:] if len(contract) >= 4 else ""

        # 列名映射
        price_col = "收盘价" if exchange == "SHFE" else "今收盘"
        delta_col = "德尔塔" if exchange == "SHFE" else "DELTA"
        iv_col = None if exchange == "SHFE" else "隐含波动率"

        for _, row in df.iterrows():
            code = str(row.get("合约代码", ""))
            if not code:
                continue

            # 合约月份过滤 — 只保留与主力合约月份相关的合约
            if exchange == "SHFE":
                # SHFE: 'cu2607C76000' → code[2:6] = '2607'
                code_month = code[2:6]
            else:
                # CZCE: 'SA607C1000' → code[2]='6'(year), code[3:5]='07'(month) → '2607'
                code_month = f"2{code[2]}{code[3:5]}"

            if target_month_suffix and len(code_month) == 4:
                # 放宽月份匹配：允许 ±1 个月的偏差（期权月份可能略晚于主力合约月份）
                try:
                    target_m = int(target_month_suffix[2:])
                    code_m = int(code_month[2:])
                    diff = abs(code_m - target_m)
                    if diff > 0 and diff > 1 and min(diff, 12 - diff) > 1:
                        continue
                except ValueError:
                    pass

            # 解析期权类型和行权价
            cp_idx = -1
            for j, ch in enumerate(code):
                if ch in ("C", "P"):
                    cp_idx = j
                    break
            if cp_idx < 0:
                continue

            ot = code[cp_idx]
            try:
                strike = float(code[cp_idx + 1:])
            except (ValueError, TypeError):
                continue

            oi = float(row.get("持仓量", 0))
            price = float(row.get(price_col, 0))
            if oi <= 0 or price <= 0:
                continue

            # 估算 T
            try:
                opt_month = int(code_month[2:])
                opt_year = int("20" + code_month[:2])
                expiry_d = date(opt_year, opt_month, 25)
                if expiry_d <= date.today():
                    # 已到期 → 移入下个月
                    if opt_month == 12:
                        expiry_d = date(opt_year + 1, 1, 25)
                    else:
                        expiry_d = date(opt_year, opt_month + 1, 25)
                T = max((expiry_d - date.today()).days, 1) / 365.0
            except Exception:
                T = 30 / 365.0

            iv_val: float = 0.0
            # CZCE 带隐含波动率列
            if iv_col and iv_col in df.columns:
                raw_iv = row.get(iv_col)
                if raw_iv is not None:
                    try:
                        iv_val = float(raw_iv) / 100.0  # 百分比转小数
                    except (ValueError, TypeError):
                        iv_val = calc_iv(price, futures_price, strike, T, r, ot == "C")
                else:
                    iv_val = calc_iv(price, futures_price, strike, T, r, ot == "C")
            else:
                iv_val = calc_iv(price, futures_price, strike, T, r, ot == "C")

            if iv_val <= 0:
                continue

            g = black_greeks(futures_price, strike, T, r, iv_val, ot == "C")

            # 使用交易所计算的德尔塔（更精确）
            if delta_col in df.columns:
                raw_delta = row.get(delta_col)
                if raw_delta is not None:
                    try:
                        g["delta"] = float(raw_delta)
                    except (ValueError, TypeError):
                        pass

            intrinsic = (
                max(0, futures_price - strike)
                if ot == "C"
                else max(0, strike - futures_price)
            )
            opts.append({
                "type": ot,
                "code": code,
                "strike": strike,
                "price": price,
                "oi": oi,
                "iv": iv_val,
                "delta": g["delta"],
                "gamma": g["gamma"],
                "theta": g["theta"],
                "vega": g["vega"],
                "intrinsic": intrinsic,
                "time_value": max(price - intrinsic, 0),
            })

        calls = sorted(
            [o for o in opts if o["type"] == "C"],
            key=lambda x: x["oi"],
            reverse=True,
        )[:5]
        puts = sorted(
            [o for o in opts if o["type"] == "P"],
            key=lambda x: x["oi"],
            reverse=True,
        )[:5]
        return calls, puts

    # ── 到期日估算 ───────────────────────────────────────────

    @staticmethod
    def estimate_expiry(contract: str) -> date:
        """估算期权到期日（委托给模块级函数）。

        Args:
            contract: 合约代码。

        Returns:
            估算的到期日。
        """
        return estimate_expiry(contract)

    # ── 批量获取全市场数据 ───────────────────────────────────

    def get_all_market_data(self, limit: int = 20) -> List[dict]:
        """获取 TOP N 品种的完整市场数据（期货+期权链+希腊字母）。

        Args:
            limit: 获取品种数上限，默认 20。

        Returns:
            市场数据列表，每项含 futures / calls / puts 及汇总字段。
        """
        futures_list = self.get_top40_futures()
        results: List[dict] = []
        n = min(limit, len(futures_list))

        logger.info("获取 %d 个品种的期权链数据...", n)
        for i, fu in enumerate(futures_list[:n]):
            px = fu["code"]
            opt_name = self.registry.get_option_name(px)
            if not opt_name:
                logger.info(
                    "  [%d/%d] %s(%s) - 无期权映射,跳过", i + 1, n, fu["name"], fu["contract"]
                )
                continue

            logger.info(
                "  [%d/%d] %s(%s) ¥%.1f OI=%d",
                i + 1, n, fu["name"], fu["contract"], fu["price"], fu["oi"],
            )

            calls, puts = self.get_option_chain(opt_name, fu["contract"], fu["price"])
            if calls or puts:
                logger.info("Call x%d Put x%d", len(calls), len(puts))
                results.append({
                    "futures": fu,
                    "calls": calls,
                    "puts": puts,
                    "top_call_oi": calls[0]["oi"] if calls else 0,
                    "top_put_oi": puts[0]["oi"] if puts else 0,
                    "avg_call_iv": (
                        sum(c["iv"] for c in calls) / len(calls) if calls else 0
                    ),
                    "avg_put_iv": (
                        sum(p["iv"] for p in puts) / len(puts) if puts else 0
                    ),
                })
            else:
                logger.info("无期权数据")

            time.sleep(0.5)

        return results


# ============================================================
# 模块自测入口
# ============================================================

if __name__ == "__main__":
    import json
    from config.settings import DB_PATH

    registry = ContractRegistry(str(DB_PATH))
    collector = OptionsCollector(registry)
    data = collector.get_all_market_data(limit=5)
    logger.info("成功获取 %d 个品种", len(data))
    for d in data:
        fu = d["futures"]
        logger.info(
            "  %s(%s): ¥%.1f OI=%d Call5=%.1f%% Put5=%.1f%%",
            fu["name"],
            fu["contract"],
            fu["price"],
            fu["oi"],
            d["avg_call_iv"] * 100,
            d["avg_put_iv"] * 100,
        )
