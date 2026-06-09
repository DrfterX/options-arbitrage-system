"""
波峰波谷检测引擎 — 方案B（增量逐笔修正）。

使用滑动窗口检测PEAK（峰）和TROUGH（谷）。
所有DB访问通过 ``db: Database`` 参数完成。
"""

import logging
from typing import Any, Dict, List, Optional

from core.db import Database
from config.settings import SWING_WINDOWS

logger = logging.getLogger(__name__)


def detect_swing_points(
    klines: List[Dict[str, Any]], window_n: int
) -> List[Dict[str, Any]]:
    """滑动窗口检测峰谷。

    Args:
        klines: K线数据（按时间升序）。
        window_n: 左右各看 n 根 K 线。

    Returns:
        极值点列表，每项含 timestamp/price/point_type(PEAK/TROUGH)。
    """
    if len(klines) < window_n * 2 + 1:
        return []

    points: List[Dict[str, Any]] = []
    n = len(klines)
    same_bar_type: Optional[str] = None

    for i in range(window_n, n - window_n + 1):
        center = klines[i]
        left_high = max(k["high"] for k in klines[i - window_n : i])
        left_low = min(k["low"] for k in klines[i - window_n : i])

        right_bars = klines[i + 1 : i + window_n + 1]
        if not right_bars:
            break
        right_high = max(k["high"] for k in right_bars)
        right_low = min(k["low"] for k in right_bars)

        same_bar_type = None

        # 峰：当前高点 > 左最高，且 >= 右最高
        if center["high"] > left_high and center["high"] >= right_high:
            if not points:
                points.append(
                    {
                        "timestamp": center["timestamp"],
                        "price": center["high"],
                        "point_type": "PEAK",
                    }
                )
                same_bar_type = "PEAK"
            elif points[-1]["point_type"] == "PEAK":
                if center["high"] > points[-1]["price"]:
                    points[-1]["price"] = center["high"]
                    points[-1]["timestamp"] = center["timestamp"]
                same_bar_type = "PEAK"
            else:
                points.append(
                    {
                        "timestamp": center["timestamp"],
                        "price": center["high"],
                        "point_type": "PEAK",
                    }
                )
                same_bar_type = "PEAK"

        # 谷：当前低点 < 左最低，且 <= 右最低
        if center["low"] < left_low and center["low"] <= right_low:
            if not points:
                if (
                    same_bar_type != "PEAK"
                    or not points
                    or points[-1]["timestamp"] != center["timestamp"]
                ):
                    points.append(
                        {
                            "timestamp": center["timestamp"],
                            "price": center["low"],
                            "point_type": "TROUGH",
                        }
                    )
            elif points[-1]["point_type"] == "TROUGH":
                if (
                    same_bar_type != "PEAK"
                    or not points
                    or points[-1]["timestamp"] != center["timestamp"]
                ):
                    if center["low"] < points[-1]["price"]:
                        points[-1]["price"] = center["low"]
                        points[-1]["timestamp"] = center["timestamp"]
            else:
                if (
                    same_bar_type != "PEAK"
                    or not points
                    or points[-1]["timestamp"] != center["timestamp"]
                ):
                    points.append(
                        {
                            "timestamp": center["timestamp"],
                            "price": center["low"],
                            "point_type": "TROUGH",
                        }
                    )

    return points


def _get_klines(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    limit: int = 2000,
) -> List[Dict[str, Any]]:
    """读取K线数据，按时间升序。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_klines
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp DESC LIMIT ?""",
            (symbol, contract, timeframe, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def _get_swing_points(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    limit: int = 200,
) -> List[Dict[str, Any]]:
    """读取已有极值点，按时间升序。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_swing_points
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp DESC LIMIT ?""",
            (symbol, contract, timeframe, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def _save_swing_points(db: Database, rows: List[Dict[str, Any]]) -> None:
    """保存极值点到数据库。"""
    if not rows:
        return
    with db.get_conn() as conn:
        conn.executemany(
            """INSERT OR REPLACE INTO futures_swing_points
               (symbol, contract, timeframe, timestamp, price, point_type)
               VALUES (:symbol, :contract, :timeframe, :timestamp, :price, :point_type)""",
            rows,
        )
        conn.commit()


def incremental_update(
    symbol: str,
    contract: str,
    timeframe: str,
    db: Database,
    window_n: Optional[int] = None,
) -> int:
    """增量更新波峰波谷。

    读取已有极值点+最近K线，重新检测整个窗口。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期。
        db: Database 实例。
        window_n: 滑动窗口大小，None时从SWING_WINDOWS配置读取。

    Returns:
        新增的极值点数量。
    """
    if window_n is None:
        window_n = SWING_WINDOWS.get(timeframe, 3)

    existing = _get_swing_points(db, symbol, contract, timeframe, limit=200)

    limit_map: Dict[str, int] = {
        "3m": 3000,
        "15m": 2000,
        "1h": 2000,
        "1d": 5000,
        "1w": 1000,
    }
    klines = _get_klines(
        db, symbol, contract, timeframe, limit=limit_map.get(timeframe, 2000)
    )
    if len(klines) < window_n * 2 + 1:
        return 0

    new_points = detect_swing_points(klines, window_n)
    if not new_points:
        return 0

    existing_set: set = set()
    for ep in existing:
        existing_set.add((ep["timestamp"], ep["point_type"]))

    to_save: List[Dict[str, Any]] = []
    for np in new_points:
        key = (np["timestamp"], np["point_type"])
        if key not in existing_set:
            np["symbol"] = symbol
            np["contract"] = contract
            np["timeframe"] = timeframe
            to_save.append(np)
            existing_set.add(key)

    if to_save:
        _save_swing_points(db, to_save)

    logger.debug(
        "%s %s %s: 新增 %d 个极值点",
        symbol,
        contract,
        timeframe,
        len(to_save),
    )
    return len(to_save)


def update_all_timeframes(
    symbol: str, contract: str, db: Database
) -> Dict[str, int]:
    """对所有周期增量更新波峰波谷。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        db: Database 实例。

    Returns:
        各周期新增极值点数量统计。
    """
    result: Dict[str, int] = {}
    for tf in ["3m", "15m", "1h", "1d", "1w"]:
        count = incremental_update(symbol, contract, tf, db)
        result[tf] = count
    return result
