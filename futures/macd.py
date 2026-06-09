"""
MACD计算模块 — 两色方案（仅RED/BLUE）。

红柱=MACD>0（多头），蓝柱=MACD≤0（空头）。
所有DB访问通过 ``db: Database`` 参数完成。
"""

import logging
from typing import Any, Dict, List, Optional

from core.db import Database
from config.settings import MACD_FAST, MACD_SLOW, MACD_SIGNAL, COLOR_RED, COLOR_BLUE

logger = logging.getLogger(__name__)


def _ema(data: List[float], period: int) -> List[float]:
    """计算指数移动平均（EMA）。

    Args:
        data: 价格序列。
        period: 周期参数。

    Returns:
        EMA 序列，长度与输入相同。
    """
    if not data:
        return []
    result = [data[0]]
    k = 2.0 / (period + 1)
    for v in data[1:]:
        result.append(v * k + result[-1] * (1 - k))
    return result


def get_color(macd_value: float) -> str:
    """两色方案：MACD>0→RED(多头)，MACD≤0→BLUE(空头)。

    Args:
        macd_value: MACD线值。

    Returns:
        'RED' 或 'BLUE'。
    """
    return COLOR_RED if macd_value > 0 else COLOR_BLUE


def calculate_macd(
    klines: List[Dict[str, Any]],
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal_period: int = MACD_SIGNAL,
) -> List[Dict[str, Any]]:
    """从K线close计算MACD，返回含颜色的结果。

    Args:
        klines: K线数据列表（需含 'close' 字段）。
        fast: 快线周期。
        slow: 慢线周期。
        signal_period: 信号线周期。

    Returns:
        MACD计算结果列表，每项含 macd/signal/histogram/color。
    """
    if len(klines) < slow + signal_period:
        return []

    closes = [k["close"] for k in klines]
    ema_fast = _ema(closes, fast)
    ema_slow = _ema(closes, slow)

    diffs = [ema_fast[i] - ema_slow[i] for i in range(len(closes))]
    dea = _ema(diffs[max(0, slow - 1) :], signal_period)

    start_idx = slow + signal_period - 1
    results: List[Dict[str, Any]] = []
    for i in range(start_idx, len(klines)):
        macd_val = diffs[i]
        dea_idx = i - slow + 1
        signal_val = dea[dea_idx] if dea_idx < len(dea) else dea[-1]
        histogram = macd_val - signal_val
        color = get_color(macd_val)
        results.append(
            {
                "symbol": klines[i].get("symbol", ""),
                "contract": klines[i].get("contract", ""),
                "timeframe": klines[i].get("timeframe", ""),
                "timestamp": klines[i]["timestamp"],
                "macd": round(macd_val, 6),
                "signal": round(signal_val, 6),
                "histogram": round(histogram, 6),
                "color": color,
            }
        )

    return results


def _get_klines(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    """读取K线数据，按时间升序返回。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_klines
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp DESC LIMIT ?""",
            (symbol, contract, timeframe, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def _batch_insert_macd(db: Database, rows: List[Dict[str, Any]]) -> None:
    """批量写入MACD结果。"""
    if not rows:
        return
    with db.get_conn() as conn:
        conn.executemany(
            """INSERT OR REPLACE INTO futures_macd
               (symbol, contract, timeframe, timestamp, macd, signal, histogram, color)
               VALUES (:symbol, :contract, :timeframe, :timestamp, :macd, :signal, :histogram, :color)""",
            rows,
        )
        conn.commit()


def calculate_and_save(
    symbol: str,
    contract: str,
    timeframe: str,
    db: Database,
    limit: int = 500,
) -> int:
    """从数据库读取K线→计算MACD→写入，返回写入条数。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期（如 '1d'）。
        db: Database 实例。
        limit: 读取K线的最大条数。

    Returns:
        写入的MACD记录条数。
    """
    klines = _get_klines(db, symbol, contract, timeframe, limit=limit)
    if len(klines) < MACD_SLOW + MACD_SIGNAL:
        logger.debug(
            "%s %s %s: K线不足 (%d < %d)",
            symbol,
            contract,
            timeframe,
            len(klines),
            MACD_SLOW + MACD_SIGNAL,
        )
        return 0

    macd_results = calculate_macd(klines)
    if not macd_results:
        return 0

    for r in macd_results:
        r["symbol"] = symbol
        r["contract"] = contract
        r["timeframe"] = timeframe

    _batch_insert_macd(db, macd_results)
    logger.debug("%s %s %s: MACD写入 %d 条", symbol, contract, timeframe, len(macd_results))
    return len(macd_results)


def calculate_all_timeframes(
    symbol: str,
    contract: str,
    db: Database,
) -> Dict[str, int]:
    """对所有周期计算MACD。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        db: Database 实例。

    Returns:
        各周期写入条数统计。
    """
    timeframes = ["3m", "15m", "1h", "1d", "1w"]
    result: Dict[str, int] = {}
    for tf in timeframes:
        count = calculate_and_save(symbol, contract, tf, db)
        result[tf] = count
    return result
