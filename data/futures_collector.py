"""
期货K线数据采集模块 — 使用 AKShare 获取期货K线数据。

提供增量采集能力，支持 1m / 15m / 1h / 1d 周期及 3m 聚合。
通过 Database 工厂获取连接，通过 ContractRegistry 获取品种信息。
"""

import time as time_module
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd

from config.settings import (
    AKSHARE_PERIODS,
    AKSHARE_RETRY,
    MARKET_TZ,
)
from core.db import Database
from config.contracts import ContractRegistry

logger = logging.getLogger(__name__)

try:
    import akshare as ak  # type: ignore[import-untyped]

    AK_AVAILABLE = True
except ImportError:
    AK_AVAILABLE = False
    logger.warning("akshare 未安装，请执行 pip install akshare")

# ============================================================
# 合约缓存（减少API调用，运行时从 AKShare 动态获取）
# ============================================================
_CONTRACT_CACHE: Dict[str, str] = {}

# ============================================================
# 周期映射常量
# ============================================================

# AKShare Sina期货K线 period 参数（本地副本，独立于 config）
PERIOD_MAP_SINA: Dict[str, str] = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "60m": "60",
    "1h": "60",
    "D": "D",
    "1d": "D",
    "W": "W",
    "1w": "W",
    "M": "M",
}

# 反向映射: AKShare period -> 内部 timeframe
SINA_PERIOD_TO_TF: Dict[str, str] = {
    v: k for k, v in PERIOD_MAP_SINA.items() if k in AKSHARE_PERIODS
}
SINA_PERIOD_TO_TF.setdefault("1", "1m")
SINA_PERIOD_TO_TF.setdefault("15", "15m")
SINA_PERIOD_TO_TF.setdefault("60", "1h")
SINA_PERIOD_TO_TF.setdefault("D", "1d")


# ============================================================
# 辅助函数
# ============================================================

def _ensure_akshare() -> None:
    """检查 akshare 是否可用，不可用时抛出 ImportError。"""
    if not AK_AVAILABLE:
        raise ImportError("akshare 未安装，请执行 pip install akshare")


def _parse_akshare_timestamp(date_val) -> Optional[int]:
    """将 AKShare 返回的日期时间解析为 Unix 秒时间戳（UTC）。

    支持格式:
      - ``'2025-01-15 09:01:00'``
      - ``'2025-01-15'``
      - ``pd.Timestamp``
      - ``int`` / ``float``（已为时间戳）

    Args:
        date_val: AKShare 返回的日期时间值。

    Returns:
        Unix 秒时间戳，解析失败返回 None。
    """
    if date_val is None:
        return None

    if isinstance(date_val, (int, float)):
        return int(date_val)

    if isinstance(date_val, pd.Timestamp):
        if date_val.tzinfo is None:
            date_val = date_val.tz_localize(MARKET_TZ)
        return int(date_val.timestamp())

    if isinstance(date_val, str):
        date_str = date_val.strip()
        for fmt in [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d",
            "%Y%m%d",
        ]:
            try:
                dt = datetime.strptime(date_str, fmt).replace(tzinfo=MARKET_TZ)
                return int(dt.timestamp())
            except ValueError:
                continue

    return None


def _period_to_timeframe(period: str) -> str:
    """AKShare period 字符串 → 内部 timeframe 名称。

    Args:
        period: AKShare period 字符串（如 ``'1'``, ``'15'``, ``'D'``）。

    Returns:
        内部 timeframe 名称（如 ``'1m'``, ``'15m'``, ``'1d'``）。
    """
    return SINA_PERIOD_TO_TF.get(period, period)


def _timeframe_to_sina_period(timeframe: str) -> str:
    """内部 timeframe 名称 → AKShare Sina period 字符串。

    Args:
        timeframe: 内部 timeframe 名称（如 ``'15m'``, ``'1h'``）。

    Returns:
        AKShare period 字符串（如 ``'15'``, ``'60'``）。
    """
    return PERIOD_MAP_SINA.get(timeframe, timeframe)


def fetch_klines(
    symbol: str,
    contract: str,
    period: str,
    start_date: Optional[str] = None,
) -> List[dict]:
    """使用 AKShare 获取期货K线数据。

    Args:
        symbol: 品种代码，如 ``'RB'``。
        contract: 合约代码，如 ``'RB2610'``（分钟线用）或 ``'RB0'``（日线主力连续用）。
        period: AKShare period 参数，如 ``'1'``, ``'15'``, ``'60'``, ``'D'``。
        start_date: 起始日期字符串 ``'20250101'``，可选。

    Returns:
        K线数据列表，每项包含 symbol / contract / timeframe / timestamp /
        open / high / low / close / volume。
    """
    _ensure_akshare()

    # ── 分钟线需真实合约代码（含年月后缀，如 "RB2610"）───────────
    if period != "D" and not any(c.isdigit() for c in contract):
        logger.warning(
            "%s/%s period=%s: 合约代码无效(缺少年月数字后缀)，跳过分钟线采集",
            symbol, contract, period,
        )
        return []

    # ── 重试采集 ────────────────────────────────────────────────
    max_retries = AKSHARE_RETRY
    for attempt in range(max_retries + 1):
        try:
            if period == "D":
                # 日线用主力连续合约
                df = ak.futures_zh_daily_sina(symbol=f"{symbol}0")
                date_col = "date"
                timeframe = "1d"
            else:
                # 分钟线用具体合约
                df = ak.futures_zh_minute_sina(symbol=contract, period=period)
                date_col = "datetime"
                timeframe = _period_to_timeframe(period)

            if df is None or df.empty:
                logger.warning("%s period=%s: 无数据", contract, period)
                return []

            results: List[dict] = []
            for _, row in df.iterrows():
                ts = _parse_akshare_timestamp(row.get(date_col))
                if ts is None:
                    continue

                volume_raw = row.get("volume", 0)
                try:
                    volume = int(float(volume_raw))
                except (ValueError, TypeError):
                    volume = 0

                results.append({
                    "symbol": symbol,
                    "contract": contract,
                    "timeframe": timeframe,
                    "timestamp": ts,
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": volume,
                })

            results.sort(key=lambda r: r["timestamp"])
            logger.info("%s period=%s: 获取 %d 条K线", contract, period, len(results))
            return results

        except Exception as e:
            if attempt < max_retries:
                wait = 1.0 * (attempt + 1)
                logger.warning(
                    "fetch_klines %s/%s period=%s, attempt %d/%d failed (%s), "
                    "retrying in %.0fs",
                    symbol, contract, period,
                    attempt + 1, max_retries + 1, e,
                    wait,
                )
                time_module.sleep(wait)
            else:
                logger.error(
                    "fetch_klines %s/%s period=%s, all %d attempts failed: %s",
                    symbol, contract, period,
                    max_retries + 1, e,
                )
                return []

    return []


# ============================================================
# FuturesCollector
# ============================================================

class FuturesCollector:
    """期货K线采集器。

    提供增量采集能力：遍历品种 → 查询最新时间戳 → 增量获取 → 写入数据库。
    通过 Database 获取连接，通过 ContractRegistry 获取品种信息。

    Attributes:
        db: Database 连接工厂实例。
        registry: ContractRegistry 品种注册表实例。
    """

    def __init__(self, db: Database, registry: ContractRegistry) -> None:
        """初始化期货K线采集器。

        Args:
            db: Database 连接工厂。
            registry: 品种注册表。
        """
        self.db = db
        self.registry = registry

    # ── 内部数据库操作 ───────────────────────────────────────

    def _batch_insert_klines(self, rows: List[dict]) -> int:
        """批量插入K线数据（INSERT OR IGNORE 去重）。

        Args:
            rows: K线数据列表。

        Returns:
            实际插入的行数。
        """
        if not rows:
            return 0

        sql = """
            INSERT OR IGNORE INTO futures_klines
            (symbol, contract, timeframe, timestamp, open, high, low, close, volume)
            VALUES (:symbol, :contract, :timeframe, :timestamp, :open, :high, :low, :close, :volume)
        """
        conn = self.db.get_conn()
        try:
            cursor = conn.executemany(sql, rows)
            conn.commit()
            return cursor.rowcount
        finally:
            pass  # 连接由 Database 管理生命周期

    def _get_last_kline_timestamp(
        self, symbol: str, contract: str, timeframe: str
    ) -> Optional[int]:
        """查询指定品种/合约/周期的最新K线时间戳。

        Args:
            symbol: 品种代码。
            contract: 合约代码。
            timeframe: 周期。

        Returns:
            最新 Unix 秒时间戳，无数据返回 None。
        """
        conn = self.db.get_conn()
        try:
            row = conn.execute(
                """SELECT MAX(timestamp) as max_ts
                   FROM futures_klines
                   WHERE symbol=? AND contract=? AND timeframe=?""",
                (symbol, contract, timeframe),
            ).fetchone()
            return row["max_ts"] if row and row["max_ts"] is not None else None
        finally:
            pass  # 连接由 Database 管理生命周期

    # ── 采集核心 ─────────────────────────────────────────────

    def collect_symbol(
        self,
        symbol: str,
        contract: str,
        period_map: Optional[Dict[str, str]] = None,
    ) -> dict:
        """采集单品种所有周期的K线数据（增量更新）。

        增量逻辑：
          - 查询数据库中该合约该周期的最新时间戳
          - 只请求最新时间戳之后的数据
          - 如果DB无数据，采集最近约7天数据

        Args:
            symbol: 品种代码，如 ``'RB'``。
            contract: 合约代码，如 ``'RB2610'``。
            period_map: 周期映射 ``{timeframe: AKShare period}``，
                默认 ``{'15m': '15', '1h': '60', '1d': 'D'}``。

        Returns:
            各周期采集结果统计:
            ``{timeframe: {'fetched': int, 'saved': int, 'error': str|None, 'last_ts': int|None}}``
        """
        if period_map is None:
            period_map = {"15m": "15", "1h": "60", "1d": "D"}

        _ensure_akshare()
        result_stats: dict = {}

        for timeframe, period in period_map.items():
            try:
                # 检查数据库中已有数据的最新时间戳
                last_ts = self._get_last_kline_timestamp(symbol, contract, timeframe)

                # 计算起始日期
                if last_ts is not None:
                    start_dt = datetime.fromtimestamp(last_ts, tz=MARKET_TZ) - timedelta(
                        hours=2
                    )
                else:
                    start_dt = datetime.now(tz=MARKET_TZ) - timedelta(days=7)

                start_str = start_dt.strftime("%Y%m%d")

                # 采集K线
                klines = fetch_klines(symbol, contract, period, start_date=start_str)
                fetched = len(klines)

                # 增量过滤
                if last_ts is not None:
                    new_klines = [k for k in klines if k["timestamp"] > last_ts]
                else:
                    new_klines = klines

                saved = 0
                if new_klines:
                    self._batch_insert_klines(new_klines)
                    saved = len(new_klines)

                result_stats[timeframe] = {
                    "fetched": fetched,
                    "saved": saved,
                    "error": None,
                    "last_ts": last_ts,
                }

                # 1m数据额外聚合生成3m
                if timeframe == "1m":
                    self._collect_3m_from_1m(symbol, contract, klines)

            except Exception as e:
                result_stats[timeframe] = {
                    "fetched": 0,
                    "saved": 0,
                    "error": str(e),
                    "last_ts": None,
                }
                logger.error(
                    "collect_symbol %s/%s %s: %s", symbol, contract, timeframe, e
                )

        return result_stats

    def _collect_3m_from_1m(
        self, symbol: str, contract: str, klines_1m: List[dict]
    ) -> None:
        """用1m数据聚合生成3m并写入数据库（增量）。

        Args:
            symbol: 品种代码。
            contract: 合约代码。
            klines_1m: 1分钟K线数据列表。
        """
        klines_3m = self.aggregate_3m_from_1m(symbol, contract, klines_1m)
        if not klines_3m:
            return

        last_3m_ts = self._get_last_kline_timestamp(symbol, contract, "3m")
        if last_3m_ts is not None:
            klines_3m = [k for k in klines_3m if k["timestamp"] > last_3m_ts]

        if klines_3m:
            self._batch_insert_klines(klines_3m)
            logger.info(
                "%s period=3m: 聚合生成 %d 条", contract, len(klines_3m)
            )

    # ── 3m聚合 ───────────────────────────────────────────────

    @staticmethod
    def aggregate_3m_from_1m(
        symbol: str,
        contract: str,
        kline_rows: List[dict],
    ) -> List[dict]:
        """从1分钟K线数据聚合生成3分钟K线。

        按180秒窗口对齐分组，取首开、最高、最低、尾收、量和。

        Args:
            symbol: 品种代码。
            contract: 合约代码。
            kline_rows: 含 ``timeframe='1m'`` 的K线数据。

        Returns:
            3分钟K线数据列表。
        """
        if not kline_rows:
            return []

        rows_1m = [r for r in kline_rows if r.get("timeframe") == "1m"]
        rows_1m.sort(key=lambda r: r["timestamp"])

        if len(rows_1m) < 3:
            return []

        results: List[dict] = []
        base_ts = rows_1m[0]["timestamp"]
        group_ts = base_ts - (base_ts % 180)  # 对齐到3分钟边界
        group: List[dict] = []

        for row in rows_1m:
            ts = row["timestamp"]
            if ts >= group_ts + 180:
                if group:
                    results.append({
                        "symbol": symbol,
                        "contract": contract,
                        "timeframe": "3m",
                        "timestamp": group_ts,
                        "open": group[0]["open"],
                        "high": max(r["high"] for r in group),
                        "low": min(r["low"] for r in group),
                        "close": group[-1]["close"],
                        "volume": sum(r["volume"] for r in group),
                    })
                group_ts = ts - (ts % 180)
                group = []
            group.append(row)

        # 处理最后一个不完整组
        if group and len(group) >= 3:
            results.append({
                "symbol": symbol,
                "contract": contract,
                "timeframe": "3m",
                "timestamp": group_ts,
                "open": group[0]["open"],
                "high": max(r["high"] for r in group),
                "low": min(r["low"] for r in group),
                "close": group[-1]["close"],
                "volume": sum(r["volume"] for r in group),
            })

        return results

    # ── 全量采集 ─────────────────────────────────────────────

    def collect_all(self, period_map: Optional[Dict[str, str]] = None) -> dict:
        """遍历所有品种，增量采集所有周期的K线数据。

        通过 ``self.registry.get_all()`` 获取品种列表。
        合约代码优先从 ``_CONTRACT_CACHE`` 获取，缓存未命中时通过
        ``ak.futures_main_sina()`` 动态查询。

        Args:
            period_map: 周期映射 ``{timeframe: AKShare period}``，
                默认 ``{'15m': '15', '1h': '60', '1d': 'D'}``。

        Returns:
            采集汇总统计 ``{symbol: {timeframe: {fetched, saved, error, last_ts}}}``。
        """
        if period_map is None:
            period_map = {"15m": "15", "1h": "60", "1d": "D"}

        _ensure_akshare()

        # 获取全部品种
        symbols = self.registry.get_all()
        if not symbols:
            logger.warning("ContractRegistry 中无品种数据")
            return {}

        total_stats: dict = {}
        total_symbols = len(symbols)

        logger.info(
            "collect_all: 开始采集 %d 个品种, 周期: %s",
            total_symbols,
            list(period_map.keys()),
        )

        for idx, sym_info in enumerate(symbols, 1):
            symbol = sym_info["symbol"]
            name = sym_info.get("name", symbol)

            # 合约代码获取：缓存优先 → AKShare动态查询
            contract = _CONTRACT_CACHE.get(symbol.lower(), symbol)
            if contract == symbol or symbol.upper() == contract:
                # 缓存未命中，尝试从 AKShare 获取主力合约
                try:
                    main_df = ak.futures_main_sina(symbol=symbol.lower())
                    if main_df is not None and not main_df.empty:
                        contract = str(main_df.iloc[-1].get("contract", symbol))
                        _CONTRACT_CACHE[symbol.lower()] = contract
                except Exception as e:
                    logger.warning(
                        "collect_all %s: futures_main_sina 查询失败, 回退品种代码: %s",
                        symbol, e,
                    )
                    # ── DB回退合约解析 ────────────────────────────
                    # futures_main_sina 全线故障（2026-06-11确认），
                    # 从 futures_klines 表查询该品种最近使用的分钟线合约代码
                    try:
                        conn = self.db.get_conn()
                        fallback_row = conn.execute(
                            """SELECT contract, MAX(timestamp) as max_ts
                               FROM futures_klines
                               WHERE symbol=? AND timeframe IN ('15m','1h')
                               GROUP BY contract
                               ORDER BY max_ts DESC
                               LIMIT 1""",
                            (symbol,),
                        ).fetchone()
                        if fallback_row and fallback_row["contract"]:
                            contract = fallback_row["contract"]
                            _CONTRACT_CACHE[symbol.lower()] = contract
                            logger.info(
                                "collect_all %s: DB回退合约 %s "
                                "(来自 futures_klines 表)",
                                symbol, contract,
                            )
                    except Exception as e2:
                        logger.warning(
                            "collect_all %s: DB回退合约查询失败: %s",
                            symbol, e2,
                        )

            logger.info(
                "[%d/%d] %s (%s) 合约: %s", idx, total_symbols, symbol, name, contract
            )

            stats = self.collect_symbol(symbol, contract, period_map)
            total_stats[symbol] = stats

            # 请求间隔，避免被API限流
            if idx < total_symbols:
                time_module.sleep(0.5)

        # 汇总
        total_fetched = sum(
            tf_stats.get("fetched", 0)
            for sym_stats in total_stats.values()
            for tf_stats in sym_stats.values()
        )
        total_saved = sum(
            tf_stats.get("saved", 0)
            for sym_stats in total_stats.values()
            for tf_stats in sym_stats.values()
        )

        logger.info(
            "采集完成: %d 个品种, 共获取 %d 条K线，新增保存 %d 条",
            total_symbols,
            total_fetched,
            total_saved,
        )

        return total_stats

    # ── 便捷采集入口 ─────────────────────────────────────────

    def collect_day(self, timeframe: str = "1d") -> dict:
        """每日盘后增量采集全部品种日线数据。

        Args:
            timeframe: 周期，默认 ``'1d'``。

        Returns:
            采集汇总统计。
        """
        return self.collect_all(period_map={timeframe: "D"})

    def collect_15m_night(self) -> dict:
        """夜盘期间增量采集15分钟线。

        Returns:
            采集汇总统计。
        """
        return self.collect_all(period_map={"15m": "15"})


# ============================================================
# 模块自测入口
# ============================================================

if __name__ == "__main__":
    from config.settings import DB_PATH

    db = Database(DB_PATH)
    registry = ContractRegistry(str(DB_PATH))
    collector = FuturesCollector(db, registry)
    collector.collect_all()
