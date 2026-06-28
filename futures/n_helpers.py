"""N型结构检测引擎 - 工具函数（从 n_structure.py 提取）。"""

import logging
from typing import Any, Dict, List, Optional
from core.db import Database

logger = logging.getLogger(__name__)

def _determine_direction(point_a_price: float, point_b_price: float) -> str:
    """判断N型方向。

    Args:
        point_a_price: A点价格。
        point_b_price: B点价格。

    Returns:
        'LONG'（正N）或 'SHORT'（倒N）。
    """
    if point_b_price > point_a_price:
        return "LONG"
    return "SHORT"


def _determine_overall_direction(merged: List[Dict[str, Any]]) -> Optional[str]:
    """从合并后的极值点序列预判整体方向。

    User Directives 要求「先判断方向（上升/下降），再按方向筛选 ABC」。
    与 _determine_direction（仅看 A→B 两点）不同，本函数从整体趋势判断方向，
    确保 ABC 标点的方向与整体趋势一致。

    判断逻辑：
    1. 取最近的 2 个 PEAK 和 2 个 TROUGH
    2. 如果最近 PEAK > 前一个 PEAK 且最近 TROUGH > 前一个 TROUGH → LONG
    3. 如果最近 PEAK < 前一个 PEAK 且最近 TROUGH < 前一个 TROUGH → SHORT
    4. 数据不足 4 个点或趋势不明 → 返回 None（由调用方退回到 A→B 推断）

    Returns:
        'LONG' / 'SHORT' / None（不确定）。
    """
    if len(merged) < 4:
        return None  # 数据不足以判断整体趋势

    # 取最近的 2 个 PEAK 和 2 个 TROUGH
    peaks = [p for p in merged if p["point_type"] == "PEAK"]
    troughs = [t for t in merged if t["point_type"] == "TROUGH"]

    if len(peaks) >= 2 and len(troughs) >= 2:
        last_two_peaks = peaks[-2:]
        last_two_troughs = troughs[-2:]

        peak_up = last_two_peaks[-1]["price"] > last_two_peaks[-2]["price"]
        trough_up = last_two_troughs[-1]["price"] > last_two_troughs[-2]["price"]

        if peak_up and trough_up:
            return "LONG"
        if not peak_up and not trough_up:
            return "SHORT"

    # 趋势不明 → 由调用方退回到 A→B 推断
    return None


def _get_swing_points(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    limit: int = 80,
) -> List[Dict[str, Any]]:
    """读取极值点，按时间升序。

    对 1d/1w 周期的极值点自动执行时间戳归一化（与 K 线归一化一致），
    确保历史极值点的时间戳与归一化后的 K 线时间戳对齐。
    """
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_swing_points
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp DESC LIMIT ?""",
            (symbol, contract, timeframe, limit),
        ).fetchall()
    points = [dict(r) for r in reversed(rows)]

    # ── 1d/1w 时间戳归一化（仅午夜线 16:00 UTC = BJT 00:00） ───
    if timeframe in ("1d", "1w"):
        BJ_OFFSET = 8 * 3600
        MIDNIGHT_SEC = 57600  # 16:00 UTC = BJT 00:00
        TARGET_HOUR_SEC = 20700  # 05:45 UTC = 13:45 BJT
        for p in points:
            ts = p["timestamp"]
            if ts % 86400 == MIDNIGHT_SEC or ts % 86400 == 0:
                bj_midnight_utc = ((ts + BJ_OFFSET) // 86400) * 86400 - BJ_OFFSET
                p["timestamp"] = bj_midnight_utc + TARGET_HOUR_SEC

    return points


def _get_klines(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    limit: int = 2,
    since_timestamp: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """读取K线数据，按时间升序。

    对 1d/1w 周期自动执行时间戳归一化：
    AKShare 日线数据的时间戳在北京时间午夜 (16:00 UTC)，
    而交易时段聚合的 K 线在 01~06 时 UTC。
    归一化将所有 1d/1w K 线的时间戳对齐到北京时间日期的 13:45 BJT (05:45 UTC)，
    确保 N 型结构检测到的 A/B/C 点时间戳与前端 K 线图一致。

    Args:
        db: Database 实例。
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期。
        limit: 返回的最大行数，None=不限制。
        since_timestamp: 可选，只返回 >= 该时间戳的K线。
    """
    with db.get_conn() as conn:
        query = """SELECT * FROM futures_klines
                   WHERE symbol=? AND contract=? AND timeframe=?"""
        params: list = [symbol, contract, timeframe]
        if since_timestamp is not None:
            query += " AND timestamp >= ?"
            params.append(since_timestamp)
        query += " ORDER BY timestamp DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        rows = conn.execute(query, params).fetchall()
    klines = [dict(r) for r in reversed(rows)]

    # ── 1d/1w 时间戳归一化 ───────────────────────────────────────
    # AKShare 日线数据的时间戳在北京午夜（16:00 UTC），
    # 而交易时段聚合的 K 线在 01:xx~06:xx UTC。
    # 归一化到北京时间日期的 13:45 BJT (05:45 UTC)，消除歧义。
    if timeframe in ("1d", "1w"):
        _normalize_bar_timestamps(klines, timeframe)

    return klines


def _normalize_bar_timestamps(
    klines: List[Dict[str, Any]], timeframe: str
) -> None:
    """归一化 1d/1w K 线时间戳到标准边界。

    AKShare 日线数据的时间戳在北京时间午夜（16:00 UTC，即北京日期
    的 00:00），而交易时段聚合的 K 线在 01:xx~06:xx UTC。
    归一化只修正午夜线：将其时间戳对齐到同一北京日期的 05:45 UTC
    (13:45 BJT)，与聚合时段线一致。

    对同一北京日期有多根 K 线的场景（AKShare 午夜线 + 聚合时段线），
    去重保留收盘价更高的一根（含完整交易时段数据）。

    Args:
        klines: K 线列表（会被原地修改）。
        timeframe: 周期（仅 1d/1w 执行归一化）。
    """
    if timeframe not in ("1d", "1w"):
        return

    BJ_OFFSET = 8 * 3600  # 北京时间 UTC+8
    MIDNIGHT_SEC = 57600   # 16:00 UTC = 午夜 BJT
    TARGET_HOUR_SEC = 20700  # 05:45 UTC = 13:45 BJT

    # 第一遍：仅修正午夜时间戳（16:00 UTC = BJT 00:00）
    for k in klines:
        ts = k["timestamp"]
        if ts % 86400 == MIDNIGHT_SEC or ts % 86400 == 0:
            bj_midnight_utc = ((ts + BJ_OFFSET) // 86400) * 86400 - BJ_OFFSET
            k["timestamp"] = bj_midnight_utc + TARGET_HOUR_SEC

    # 第二遍：按相同时间戳去重（保留最近一条——含完整交易时段数据）
    seen: dict = {}  # timestamp → index (保留最后一条)
    for idx, k in enumerate(klines):
        seen[k["timestamp"]] = idx
    # 重建列表，只保留 seen 中的最后一条
    kept = [klines[idx] for idx in sorted(seen.values())]
    klines[:] = kept


