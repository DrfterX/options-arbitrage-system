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
from futures.shared import _get_active_n_structure

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
    since_timestamp: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """读取K线数据，按时间升序。

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


# ─── 动态重算 ────────────────────────────────────────────────


def dynamic_restructure(
    symbol: str,
    contract: str,
    timeframe: str,
    db: Database,
) -> Dict[str, Any]:
    """动态重算 N 型结构 — A 点被行情突破时执行结构迁移。

    当价格在同方向超越旧 A 点时执行增量迁移：
      1. old_B → new_A（原 B 点成为新结构的起点）
      2. 找 old_B 之后第一个交替类型极值点 → new_B
      3. 找 new_B 之后第一个交替类型极值点 → new_C
      4. 方向重算 + 状态重判 + DB 更新

    当无活跃结构（已被 _get_active_n_structure 的收盘价淘汰）或
    极值点不足以形成新 3 点结构时 → 回退 detect_and_save() 全量重算。

    所有周期共用同一套逻辑。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期。
        db: Database 实例。

    Returns:
        更新后的 N 型结构字典（含 is_active 标记）。
    """
    # 1. 读取当前活跃结构
    active = _get_active_n_structure(db, symbol, contract, timeframe)
    if not active:
        # 已被收盘价检查淘汰（方向翻转）→ 全量重算
        return detect_and_save(symbol, contract, timeframe, db)

    # 2. 提取结构关键参数（在 _get_klines 之前，供 since_timestamp 使用）
    direction = active["direction"]
    a_price = active["point_a_price"]
    b_price = active["point_b_price"]
    b_time = active["point_b_time"]

    # 3. 读取点 B 之后的所有 K 线（修复：limit=3 会遗漏早期突破数据）
    #    limit=None = 不限制数量，since_timestamp=b_time = 从 B 点至今
    klines = _get_klines(db, symbol, contract, timeframe, limit=None, since_timestamp=b_time)
    if not klines:
        active['is_active'] = True
        return active

    latest_high = max(k["high"] for k in klines)
    latest_low = min(k["low"] for k in klines)

    # 3. A 突破检查 — 结构的极端点被相反方向的价格超越触发迁移
    #    LONG: A=TROUGH（低点），最新最低价跌破 A → 原有低点失效，结构需迁移
    #    SHORT: A=PEAK（高点），最新最高价突破 A → 原有高点失效，结构需迁移
    a_broken = (direction == "LONG" and latest_low < a_price) or \
               (direction == "SHORT" and latest_high > a_price)

    if not a_broken:
        # 3.5 B 点反转检查 — 价格未突破 A 但反穿了 B 点
        #    场景：
        #      LONG: A=TROUGH→B=PEAK，价格从 B 大幅跌回，跌破 B_price
        #      SHORT: A=PEAK→B=TROUGH，价格从 B 大幅反弹，涨破 B_price
        #    回撤阈值：A→B 幅度的 50%
        b_range = abs(b_price - a_price)
        if b_range > 0:
            b_broken = (
                (direction == "LONG" and latest_high < b_price and
                 (b_price - latest_high) / b_range > 0.5)
            ) or (
                (direction == "SHORT" and latest_low > b_price and
                 (latest_low - b_price) / b_range > 0.5)
            )
            if b_broken:
                # B 反穿 → 标记 COMPLETED + 全量重算（方向可能翻转）
                completed = dict(active)
                completed["state"] = NState.COMPLETED.value
                _save_n_structure(db, completed)
                logger.info(
                    "[dynamic_restructure] %s/%s %s: B reversed "
                    "(b_price=%.2f, range=%.2f, 50%% threshold) → "
                    "COMPLETED + full recalc",
                    symbol, contract, timeframe, b_price, b_range,
                )
                return detect_and_save(symbol, contract, timeframe, db)

        active['is_active'] = True
        return active  # 结构仍有效，无需变动

    # 4. A 被突破 → 执行结构迁移
    swing_points = _get_swing_points(db, symbol, contract, timeframe, limit=40)

    # 只取 B 时间之后的极值点（_get_swing_points 已按时间升序）
    new_sp = [sp for sp in swing_points if sp["timestamp"] > b_time]

    if len(new_sp) < 2:
        # 极值点不足以形成新 3 点结构 → 回退全量检测
        return detect_and_save(symbol, contract, timeframe, db)

    # 4a. old_B → new_A
    #     LONG: A=TROUGH, B=PEAK → old_B(P) → new_A(P)
    #     SHORT: A=PEAK, B=TROUGH → old_B(T) → new_A(T)
    old_b_type = "PEAK" if direction == "LONG" else "TROUGH"
    new_a_price = b_price
    new_a_time = b_time

    # 4b. 找 new_B（与 new_A 交替类型）
    new_b_type = "TROUGH" if old_b_type == "PEAK" else "PEAK"
    new_b = next((sp for sp in new_sp if sp["point_type"] == new_b_type), None)
    if not new_b:
        return detect_and_save(symbol, contract, timeframe, db)

    # 4c. 找 new_C（与 new_B 交替类型）
    new_c_type = "PEAK" if new_b_type == "TROUGH" else "TROUGH"
    new_c = next(
        (sp for sp in new_sp
         if sp["timestamp"] > new_b["timestamp"]
         and sp["point_type"] == new_c_type),
        None,
    )
    if not new_c:
        # 不足 3 点 → 回退全量检测
        return detect_and_save(symbol, contract, timeframe, db)

    # 4d. 方向重算
    new_direction = _determine_direction(new_a_price, new_b["price"])

    # 4e. 状态重判
    if new_direction == "LONG":
        state = (
            NState.LEG3.value
            if new_c["price"] >= new_b["price"]
            else NState.LEG2.value
        )
    else:
        state = (
            NState.LEG3.value
            if new_c["price"] <= new_b["price"]
            else NState.LEG2.value
        )

    # 5. 构建迁移后结构
    migrated = {
        "symbol": symbol,
        "contract": contract,
        "timeframe": timeframe,
        "direction": new_direction,
        "state": state,
        "point_a_time": new_a_time,
        "point_a_price": new_a_price,
        "point_b_time": new_b["timestamp"],
        "point_b_price": new_b["price"],
        "point_c_time": new_c["timestamp"],
        "point_c_price": new_c["price"],
    }

    _save_n_structure(db, migrated)
    migrated["is_active"] = state not in (
        NState.COMPLETED.value,
        NState.IDLE.value,
    )

    logger.info(
        "[dynamic_restructure] %s/%s %s: %s→%s | "
        "A %.2f→%.2f B %.2f→%.2f C %.2f→%.2f",
        symbol, contract, timeframe,
        direction, new_direction,
        a_price, new_a_price,
        b_price, new_b["price"],
        active.get("point_c_price", 0), new_c["price"],
    )

    return migrated


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
