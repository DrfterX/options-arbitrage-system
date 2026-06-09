"""
N型结构检测引擎 + 15分钟突破检测。

状态机: IDLE → LEG1 → LEG2 → LEG3 → COMPLETED

N型定义：
  正N型(LONG): A < B < C 上升结构
  倒N型(SHORT): A > B > C 下降结构

A=起点, B=折返点, C=当前端点。
每个LEG由两个极值点构成：
  LEG1: A点确认（第一个极值）
  LEG2: B点确认（反向极值）
  LEG3: C点确认（同向极值，第三段运行中）
  COMPLETED: 第三个极值后出现反向极值

15分钟入场触发：价格突破B点
  做空：跌破B点
  做多：突破B点

所有DB访问通过 ``db: Database`` 参数完成。
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from core.db import Database
from config.settings import DETECT_WINDOWS, LEVEL3_TIMEFRAME

logger = logging.getLogger(__name__)


class NState(Enum):
    """N型结构状态枚举。"""

    IDLE = "IDLE"
    LEG1 = "LEG1"
    LEG2 = "LEG2"
    LEG3 = "LEG3"
    COMPLETED = "COMPLETED"


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


# ─── DB 内部辅助 ─────────────────────────────────────────────


def _get_swing_points(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    limit: int = 80,
) -> List[Dict[str, Any]]:
    """读取极值点，按时间升序。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_swing_points
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp DESC LIMIT ?""",
            (symbol, contract, timeframe, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def _get_klines(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    limit: int = 2,
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


def _save_n_structure(db: Database, ns: Dict[str, Any]) -> int:
    """保存N型结构，返回id。

    如果存在同 symbol+contract+timeframe 的活跃结构则更新。
    """
    with db.get_conn() as conn:
        existing = conn.execute(
            """SELECT id FROM futures_n_structures
               WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED'
               ORDER BY id DESC LIMIT 1""",
            (ns["symbol"], ns["contract"], ns["timeframe"]),
        ).fetchone()

        if existing:
            ns["id"] = existing["id"]
            conn.execute(
                """UPDATE futures_n_structures SET
                   direction=:direction, state=:state,
                   point_a_time=:point_a_time, point_a_price=:point_a_price,
                   point_b_time=:point_b_time, point_b_price=:point_b_price,
                   point_c_time=:point_c_time, point_c_price=:point_c_price,
                   updated_at=datetime('now')
                   WHERE id=:id""",
                ns,
            )
            conn.commit()
            return existing["id"]

        cur = conn.execute(
            """INSERT INTO futures_n_structures
               (symbol, contract, timeframe, direction, state,
                point_a_time, point_a_price,
                point_b_time, point_b_price,
                point_c_time, point_c_price)
               VALUES (:symbol, :contract, :timeframe, :direction, :state,
                       :point_a_time, :point_a_price,
                       :point_b_time, :point_b_price,
                       :point_c_time, :point_c_price)""",
            ns,
        )
        conn.commit()
        return cur.lastrowid


def _get_active_n_structure(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
) -> Optional[Dict[str, Any]]:
    """获取未完成的活跃N型结构。

    额外校验：
      1. 时间新鲜度
      2. 结构有效性（C不可突破A）
      3. 极端止损检查（当前收盘已突破A点则失效）
    """
    import time as time_module

    now = int(time_module.time())

    freshness: Dict[str, int] = {
        "3m": 2 * 86400,
        "15m": 2 * 86400,
        "1h": 7 * 86400,
        "1d": 30 * 86400,
        "1w": 60 * 86400,
    }

    with db.get_conn() as conn:
        row = conn.execute(
            """SELECT * FROM futures_n_structures
               WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED'
               ORDER BY updated_at DESC LIMIT 1""",
            (symbol, contract, timeframe),
        ).fetchone()

        if not row:
            return None

        ns = dict(row)

        freshness_cutoff = freshness.get(timeframe, 60 * 86400)
        latest_ts = ns.get("point_c_time") or ns.get("point_b_time")
        if latest_ts and (now - latest_ts) > freshness_cutoff:
            return None

        a_price = ns.get("point_a_price")
        c_price = ns.get("point_c_price")
        if ns["direction"] == "SHORT" and a_price and c_price and c_price >= a_price:
            return None
        if ns["direction"] == "LONG" and a_price and c_price and c_price <= a_price:
            return None

        last_kline = conn.execute(
            """SELECT close FROM futures_klines
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp DESC LIMIT 1""",
            (symbol, contract, timeframe),
        ).fetchone()

        if last_kline and a_price:
            if ns["direction"] == "SHORT" and last_kline["close"] >= a_price:
                return None
            if ns["direction"] == "LONG" and last_kline["close"] <= a_price:
                return None

        return ns


# ─── 核心：N型检测 ────────────────────────────────────────────


def detect_and_save(
    symbol: str,
    contract: str,
    timeframe: str,
    db: Database,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """从极值点运行N型状态机，保存最新结构。

    哲学：只看当下——从最新极值点反推当前形成中的结构。
    只要3个极值点交替出现（峰↔谷↔峰 或 谷↔峰↔谷），就视为有效。
    连续的同向极值点合并：以最极端值为准。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期。
        db: Database 实例。
        limit: 读取的极值点数量，默认用 DETECT_WINDOWS。

    Returns:
        N型结构字典，含 state/direction/point_abc/ is_active。
    """
    if limit is None:
        limit = DETECT_WINDOWS.get(timeframe, 40)

    swing_points = _get_swing_points(db, symbol, contract, timeframe, limit=limit * 2)

    if len(swing_points) < 3:
        return {"state": NState.IDLE.value, "is_active": False}

    # 同向合并
    filtered: List[Dict[str, Any]] = []
    for sp in swing_points:
        if filtered and sp["point_type"] == filtered[-1]["point_type"]:
            prev = filtered[-1]
            if sp["point_type"] == "TROUGH":
                if sp["price"] < prev["price"]:
                    filtered[-1] = sp
            else:  # PEAK
                if sp["price"] > prev["price"]:
                    filtered[-1] = sp
        else:
            filtered.append(sp)

    if len(filtered) < 3:
        return {"state": NState.IDLE.value, "is_active": False}

    # 从最新往前滑窗，找第一个有效的3点结构
    best: Optional[List[Dict[str, Any]]] = None
    n = len(filtered)
    for start in range(n - 3, max(n - 5, -1), -1):
        trio = filtered[start : start + 3]
        types = [p["point_type"] for p in trio]
        if not (types[0] != types[1] and types[1] != types[2]):
            continue

        pa, pb, pc = trio[0], trio[1], trio[2]
        direction = _determine_direction(pa["price"], pb["price"])

        if direction == "LONG" and pc["price"] <= pa["price"]:
            continue
        if direction == "SHORT" and pc["price"] >= pa["price"]:
            continue

        best = trio
        break

    if best is None:
        return {
            "state": NState.IDLE.value,
            "is_active": False,
            "reason": "无有效3点结构",
        }

    pa, pb, pc = best[0], best[1], best[2]
    direction = _determine_direction(pa["price"], pb["price"])

    # 状态判定
    if direction == "LONG":
        if pc["price"] >= pb["price"]:
            state = NState.LEG3.value
        else:
            state = NState.LEG2.value
    else:  # SHORT
        if pc["price"] <= pb["price"]:
            state = NState.LEG3.value
        else:
            state = NState.LEG2.value

    # COMPLETED 判定
    a_idx = next(
        (
            i
            for i, fp in enumerate(filtered)
            if fp["timestamp"] == best[0]["timestamp"]
            and fp["point_type"] == best[0]["point_type"]
        ),
        -1,
    )
    if a_idx > 0 and filtered[a_idx - 1]["point_type"] == best[0]["point_type"]:
        state = NState.COMPLETED.value

    ns = {
        "symbol": symbol,
        "contract": contract,
        "timeframe": timeframe,
        "direction": direction,
        "state": state,
        "point_a_time": pa["timestamp"],
        "point_a_price": pa["price"],
        "point_b_time": pb["timestamp"],
        "point_b_price": pb["price"],
        "point_c_time": pc["timestamp"],
        "point_c_price": pc["price"],
    }

    _save_n_structure(db, ns)
    ns["is_active"] = state not in (NState.COMPLETED.value, NState.IDLE.value)
    return ns


# ─── 突破检测 ────────────────────────────────────────────────


def check_15m_breakout(
    n_structure: Dict[str, Any], current_price: float
) -> Dict[str, Any]:
    """检测15分钟价格是否突破N型B点。

    Args:
        n_structure: N型结构字典。
        current_price: 当前价格。

    Returns:
        突破检测结果字典。
    """
    if not n_structure or not n_structure.get("point_b_price"):
        return {"triggered": False, "detail": "无活跃N型"}

    direction = n_structure["direction"]
    b_price = n_structure["point_b_price"]

    if direction == "SHORT":
        triggered = current_price <= b_price
        detail = (
            f"做空等待跌破B={b_price}" if not triggered else f"已跌破B={b_price}"
        )
    else:
        triggered = current_price >= b_price
        detail = (
            f"做多等待突破B={b_price}" if not triggered else f"已突破B={b_price}"
        )

    return {
        "triggered": triggered,
        "direction": direction,
        "breakout_price": b_price,
        "current_price": current_price,
        "detail": detail,
    }


def get_current_price(
    symbol: str, contract: str, timeframe: str, db: Database
) -> Optional[float]:
    """获取最近收盘价。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期。
        db: Database 实例。

    Returns:
        最近收盘价，无数据时返回 None。
    """
    klines = _get_klines(db, symbol, contract, timeframe, limit=1)
    return klines[-1]["close"] if klines else None


def get_last_bar(
    symbol: str, contract: str, timeframe: str, db: Database
) -> Optional[Dict[str, Any]]:
    """获取最后一条已收盘的K线。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期。
        db: Database 实例。

    Returns:
        最新完整K线字典。
    """
    klines = _get_klines(db, symbol, contract, timeframe, limit=2)
    if len(klines) >= 2:
        return klines[-1]
    elif len(klines) == 1:
        return klines[0]
    return None


def check_realtime_breakout(
    symbol: str,
    contract: str,
    n_structure: Dict[str, Any],
    db: Database,
) -> Dict[str, Any]:
    """实时K线突破检测：仅基于最新一根收盘的15m K线。

    相比 check_15m_breakout：
    1. 只取最新一根15m bar的close，不查任意时刻的"当前价"
    2. 新鲜度：仅当前一根bar未突破、最新bar突破时才视为新信号

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        n_structure: N型结构字典。
        db: Database 实例。

    Returns:
        突破检测结果字典。
    """
    bars = _get_klines(db, symbol, contract, LEVEL3_TIMEFRAME, limit=2)
    if not bars or len(bars) < 1:
        return {"triggered": False, "detail": "无法获取最新K线"}

    if not n_structure or not n_structure.get("point_b_price"):
        return {"triggered": False, "detail": "无活跃N型"}

    direction = n_structure["direction"]
    b_price = n_structure["point_b_price"]

    last_bar = bars[-1]
    prev_bar = bars[-2] if len(bars) >= 2 else None
    close_price = last_bar["close"]
    bar_ts = last_bar["timestamp"]

    if direction == "SHORT":
        last_breaks = close_price <= b_price
        prev_breaks = prev_bar is not None and prev_bar["close"] <= b_price
    else:
        last_breaks = close_price >= b_price
        prev_breaks = prev_bar is not None and prev_bar["close"] >= b_price

    is_fresh = last_breaks and not prev_breaks

    if last_breaks:
        detail = f"最新bar({bar_ts})收盘{close_price}触及B={b_price}"
        if is_fresh:
            detail += " ✅ 新突破"
        elif prev_breaks:
            detail += f" ⚠️ 前根bar({prev_bar['timestamp']})已突破，非新信号"
    else:
        detail = f"最新bar收盘{close_price}未突破B={b_price}"

    return {
        "triggered": is_fresh,
        "direction": direction,
        "breakout_price": b_price,
        "trigger_price": close_price,
        "trigger_time": bar_ts,
        "is_fresh": is_fresh,
        "detail": detail,
    }
