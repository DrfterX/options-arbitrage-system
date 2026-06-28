"""
N型结构检测引擎 + 15分钟突破检测。

状态机: IDLE → LEG1 → LEG2 → LEG3 → COMPLETED

N型定义：
  正N型(LONG): A=TROUGH, B=PEAK, C=TROUGH（上升V型）
  倒N型(SHORT): A=PEAK, B=TROUGH, C=PEAK（下降V型）

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
import time as time_module
from enum import Enum
from typing import Any, Dict, List, Optional

from core.db import Database
from config.settings import DETECT_WINDOWS, LEVEL3_TIMEFRAME
from futures.shared import _get_active_n_structure, cond4_epsilon, FRESHNESS
from futures.n_helpers import _determine_direction, _determine_overall_direction, _get_swing_points, _get_klines, _normalize_bar_timestamps

logger = logging.getLogger(__name__)


class NState(Enum):
    """N型结构状态枚举。"""

    IDLE = "IDLE"
    LEG1 = "LEG1"
    LEG2 = "LEG2"
    LEG3 = "LEG3"
    COMPLETED = "COMPLETED"




# ─── DB 内部辅助 ─────────────────────────────────────────────


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


# ─── 时间戳归一化 ────────────────────────────────────────────────


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


def _cleanup_stale_structures(symbol: str, contract: str, timeframe: str, db: Database) -> None:
    """清理残留的旧活跃 LEG3 行，保留最新一条（如有）。

    当 detect_and_save 返回 IDLE（条件 4 不满足等场景）时，
    不调用 _save_n_structure，但遗留的 LEG3 行需要被清理。
    """
    try:
        with db.get_conn() as conn:
            conn.execute(
                """UPDATE futures_n_structures SET state='COMPLETED', updated_at=datetime('now')
                   WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED'
                   AND id NOT IN (
                       SELECT id FROM futures_n_structures
                       WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED'
                       ORDER BY id DESC LIMIT 1
                   )""",
                (symbol, contract, timeframe, symbol, contract, timeframe),
            )
            conn.commit()
    except Exception:
        pass  # 清理失败不阻塞主流程


def _save_n_structure(db: Database, ns: Dict[str, Any]) -> int:
    """保存N型结构，返回id。

    如果存在同 symbol+contract+timeframe 的活跃结构则更新。
    """
    with db.get_conn() as conn:
        # ── 防御性清理：先将所有残留的旧活跃结构标记 COMPLETED ──────
        # 保留最新一条非 COMPLETED 行供后续 UPDATE，其余全部标记 COMPLETED。
        # 这解决了以下场景的堆积问题：
        #   1. detect_and_save 因 COMPLETED 判定写入 COMPLETED 状态后，
        #      下次调用发现无非 COMPLETED 行，走 INSERT 路径产生新行
        #   2. dynamic_restructure B-反转路径：先标记 COMPLETED 再调
        #      detect_and_save，每次都新增一行
        #   3. 多 Database 实例（数据采集器 + API Server）并发写入，
        #      各自连接未及时看到对方提交的行
        conn.execute(
            """UPDATE futures_n_structures SET state='COMPLETED', updated_at=datetime('now')
               WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED'
               AND id NOT IN (
                   SELECT id FROM futures_n_structures
                   WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED'
                   ORDER BY id DESC LIMIT 1
               )""",
            (ns["symbol"], ns["contract"], ns["timeframe"],
             ns["symbol"], ns["contract"], ns["timeframe"]),
        )

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


def _merge_same_type(swing_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """合并连续同向极值点，保留最极端值。"""
    merged: List[Dict[str, Any]] = []
    for sp in swing_points:
        if merged and sp["point_type"] == merged[-1]["point_type"]:
            prev = merged[-1]
            if sp["point_type"] == "TROUGH":
                if sp["price"] < prev["price"]:
                    merged[-1] = sp
            else:  # PEAK
                if sp["price"] > prev["price"]:
                    merged[-1] = sp
        else:
            merged.append(sp)
    return merged


def _find_n_structure_forward(
    merged: List[Dict[str, Any]],
    overall_direction: Optional[str] = None,
    current_price: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """前向非重叠扫描，返回最后一个有效的 N 型结构。

    方向优先（P0.2 改进）：
      1. 调用方先通过 _determine_overall_direction() 预判整体方向
      2. 本函数根据整体方向过滤 A 点类型：
         - LONG → 只选 TROUGH 作为 A
         - SHORT → 只选 PEAK 作为 A
      3. 如果 overall_direction 为 None（趋势不明），退回到 A→B 推断

    条件 4（第三笔方向确认）整合到扫描中（P0.2 改进）：
      - 当提供 current_price 时，优先选择满足条件 4 的 C 点
      - LONG：最新价 > C（第三笔向上破位）
      - SHORT：最新价 < C（第三笔向下破位）
      - 如果没有 C 满足条件 4，接受第一个有效的 ABC（由 detect_and_save 硬过滤）

    N 型结构的正确定义（上升 N 型示例）：
        A = 第一笔起点（最低点）
        A → B：第一笔上涨，B 是第一笔终点（最高点）
        B → C：第二笔下跌，C 是第二笔低点
        C > A（否则上升 N 型不成立）
        从 C 到最新价格 = 潜在的第三笔

    下降 N 型同理，方向相反。

    非重叠约束：一旦从 A 找到 C，下一个结构必须从 C 之后开始。
    这防止了"第三笔内部的小波动被误认为新结构"的滑动错误。

    Returns:
        结构字典（含 a/b/c/direction/index 信息）或 None。
    """
    merged_len = len(merged)
    structures: List[Dict[str, Any]] = []

    i = 0
    while i < merged_len - 2:
        a = merged[i]
        found = False

        # ── 方向优先过滤 ─────────────────────────────────────────
        # 如果预判了整体方向，A 的类型必须与方向匹配：
        #   LONG → A 必须是 TROUGH
        #   SHORT → A 必须是 PEAK
        if overall_direction == "LONG" and a["point_type"] != "TROUGH":
            i += 1
            continue
        if overall_direction == "SHORT" and a["point_type"] != "PEAK":
            i += 1
            continue

        for b_idx in range(i + 1, merged_len):
            if merged[b_idx]["point_type"] == a["point_type"]:
                continue  # 同类型，不是 B
            b = merged[b_idx]

            # ── 方向判定 ──────────────────────────────────────────
            # 优先使用整体方向（已由 _determine_overall_direction 预判）
            # 如果整体方向不确定，退回到 A→B 价格比较
            if overall_direction is not None:
                direction = overall_direction
            else:
                direction = _determine_direction(a["price"], b["price"])

            # ── 方向-点类型一致性校验 ────────────────────────────
            # User Directives 要求：LONG→A=TROUGH, SHORT→A=PEAK
            if (direction == "LONG" and a["point_type"] != "TROUGH") or \
               (direction == "SHORT" and a["point_type"] != "PEAK"):
                continue

            # ── 扫描 C 点（条件 4 整合）────────────────────────
            best_candidate: Optional[Dict[str, Any]] = None  # 退选候选人

            for c_idx in range(b_idx + 1, merged_len):
                if merged[c_idx]["point_type"] != a["point_type"]:
                    continue  # 不是与 A 同类型，不是 C
                c = merged[c_idx]

                # 条件 3：C 不可突破 A
                if direction == "LONG" and c["price"] <= a["price"]:
                    continue
                if direction == "SHORT" and c["price"] >= a["price"]:
                    continue

                # 条件 2：B→C 方向一致性（第二笔确认）
                # LONG: C 必须低于 B（第二笔下跌确认）
                if direction == "LONG" and c["price"] >= b["price"]:
                    continue
                # SHORT: C 必须高于 B（第二笔上涨确认）
                if direction == "SHORT" and c["price"] <= b["price"]:
                    continue

                # 记录当前 C 为有效候选人
                candidate = {
                    "direction": direction,
                    "a": a, "b": b, "c": c,
                    "a_idx": i, "b_idx": b_idx, "c_idx": c_idx,
                }

                # 条件 4（第三笔方向确认）整合，带 ε 缓冲区防闪烁：
                # LONG: 最新价 > C - ε（允许小幅回撤到 C 以下）
                # SHORT: 最新价 < C + ε（允许小幅反弹到 C 以上）
                cond4_ok = True
                if current_price is not None:
                    eps = cond4_epsilon(c["price"])
                    if direction == "LONG" and current_price <= c["price"] - eps:
                        cond4_ok = False
                    if direction == "SHORT" and current_price >= c["price"] + eps:
                        cond4_ok = False

                if cond4_ok:
                    # 条件 4 满足 → 立即接受此候选人
                    structures.append(candidate)
                    i = c_idx + 1  # 非重叠：从 C 之后继续
                    found = True
                    break  # c loop
                elif best_candidate is None:
                    # 条件 4 未满足，但记录为退选候选人
                    best_candidate = candidate

            if found:
                break  # b loop → 已找到 B+C

            # 遍历所有 C 后无满足条件 4 的候选人，使用退选候选人
            if best_candidate is not None:
                structures.append(best_candidate)
                i = best_candidate["c_idx"] + 1
                found = True
                break  # b loop

        if not found:
            i += 1  # 当前点不适合做 A，试下一个

    return structures[-1] if structures else None


def detect_and_save(
    symbol: str,
    contract: str,
    timeframe: str,
    db: Database,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """从极值点运行N型状态机，保存最新结构。

    哲学：前向非重叠扫描——从最早极值点开始，找到第一个有效的
    A→B→C 三笔结构，然后跳到 C 之后继续扫描后续结构。
    取最后一个有效结构作为当前 N 型结构。

    与旧版（逆向 C→B→A 滑动扫描）的区别：
    - 旧版从最新极值点反推，导致 A/B/C 随新极值点滑动
    - 新版定位 A 为第一笔的起点（最早端点），B 为第一笔终点，
      C 为第二笔终点，不再随第三笔内部的小波动而滑动

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期。
        db: Database 实例。
        limit: 读取的极值点数量，默认用 DETECT_WINDOWS。

    Returns:
        N型结构字典，含 state/direction/point_abc/is_active。
    """
    if limit is None:
        limit = DETECT_WINDOWS.get(timeframe, 40)

    swing_points = _get_swing_points(db, symbol, contract, timeframe, limit=limit * 2)

    if len(swing_points) < 3:
        _cleanup_stale_structures(symbol, contract, timeframe, db)
        return {"state": NState.IDLE.value, "is_active": False}

    merged = _merge_same_type(swing_points)

    if len(merged) < 3:
        _cleanup_stale_structures(symbol, contract, timeframe, db)
        return {"state": NState.IDLE.value, "is_active": False}

    # ── P0.2 方向优先改进 ──────────────────────────────────────
    # 1. 预判整体方向（上升/下降），确保 ABC 标点方向与整体趋势一致
    overall_direction = _determine_overall_direction(merged)

    # 2. 读取最新价，传递给扫描函数（条件 4 整合到 scan 内）
    current_price: Optional[float] = None
    try:
        klines = _get_klines(db, symbol, contract, timeframe, limit=1)
        if klines:
            current_price = klines[-1]["close"]
    except Exception as exc:
        logger.warning(
            "[detect_and_save] %s/%s %s: 读取最新价失败（%s）",
            symbol, contract, timeframe, exc,
        )

    # 3. 方向优先扫描：传入整体方向和最新价
    best = _find_n_structure_forward(merged, overall_direction, current_price)

    if best is None:
        _cleanup_stale_structures(symbol, contract, timeframe, db)
        return {
            "state": NState.IDLE.value,
            "is_active": False,
            "reason": "无有效3点结构",
        }

    pa, pb, pc = best["a"], best["b"], best["c"]
    direction = best["direction"]

    # ── 条件 4 硬过滤（带 ε 缓冲区防闪烁）───────────────────────
    # scan 内是"优先选满足条件 4 的 C"，但没有候选时接受第一个有效 C
    # 此处是硬过滤：不符合条件 4（带 ε 缓冲）→ IDLE
    # ε 防止「价格在 C 附近微小波动」导致 IDLE↔ACTIVE 闪烁
    try:
        if current_price is not None:
            eps = cond4_epsilon(pc["price"])
            if direction == "LONG" and current_price <= pc["price"] - eps:
                _cleanup_stale_structures(symbol, contract, timeframe, db)
                return {
                    "state": NState.IDLE.value,
                    "is_active": False,
                    "reason": f"条件4不满足：最新价{current_price}<=(C{pc['price']}-ε{eps:.2f})",
                }
            if direction == "SHORT" and current_price >= pc["price"] + eps:
                _cleanup_stale_structures(symbol, contract, timeframe, db)
                return {
                    "state": NState.IDLE.value,
                    "is_active": False,
                    "reason": f"条件4不满足：最新价{current_price}>=(C{pc['price']}+ε{eps:.2f})",
                }
    except Exception as exc:
        logger.warning(
            "[detect_and_save] %s/%s %s: 条件4检查跳过（%s）",
            symbol, contract, timeframe, exc,
        )

    # 状态判定 — 已有有效3点交替结构 → LEG3（第三段运行中）
    # P0.2 修复：移除了过度严格的 COMPLETED 判定。
    # 旧逻辑：A 之前还有同类型极值点 → COMPLETED
    # 问题：merge 后序列严格交替，此条件本质不会触发（死代码）。
    # 即使触发，也不意味着结构已结束——只有行情实际突破才意味着结束，
    # 而这由 dynamic_restructure 负责。
    state = NState.LEG3.value

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


def _mark_completed(active: dict, db: Database) -> None:
    """将活跃结构标记为 COMPLETED 并写入 DB。

    Args:
        active: 当前活跃 N 型结构字典（会被原地修改）。
        db: Database 实例。
    """
    active["state"] = NState.COMPLETED.value
    _save_n_structure(db, active)


def _update_c_point(active: dict, swing_points: list, db: Database) -> Optional[dict]:
    """更新 C 点 — 最新 swing point 与 C 同类型且更极端时滑动更新。

    场景：行情更新后形成新的 swing point，与当前 C 点同类型但更极端。
    例如 LONG（上升 N 型）：C=TROUGH，新 TROUGH 更低 → C 点更新到新位置。
    这符合"从 C 点到最新价格 = 第三笔"的语义 — A/B 保持，C 滑动。

    阈值防突破检查：
    如果 new_C 超越原 A 点（LONG: new_C_price < A_price; SHORT: new_C_price > A_price），
    说明第三笔回撤过深，结构已失效 → 标记 COMPLETED + 返回 None，
    让调用方触发全量重算。

    Args:
        active: 当前活跃 N 型结构字典（会被原地修改）。
        swing_points: 极值点列表（时间升序）。
        db: Database 实例。

    Returns:
        更新后的结构字典，或 None（无需更新 / 已标记 COMPLETED）。
    """
    if not swing_points:
        return None

    latest = swing_points[-1]
    # C 的类型：LONG=C=TROUGH, SHORT=C=PEAK
    if active["direction"] == "LONG":
        c_type = "TROUGH"
        more_extreme = latest["price"] < active["point_c_price"]
    else:
        c_type = "PEAK"
        more_extreme = latest["price"] > active["point_c_price"]

    if latest["point_type"] != c_type or not more_extreme:
        return None
    if latest["timestamp"] <= active["point_c_time"]:
        return None

    a_price = active["point_a_price"]

    # ── 阈值防突破检查：C 滑动超过 A 点时结构失效 ─────────────
    if active["direction"] == "LONG":
        # LONG: A=TROUGH（最低点）, C=TROUGH, C 不能低于 A
        if latest["price"] <= a_price:
            logger.info(
                "[_update_c_point] %s/%s %s: C point %.2f <= A %.2f, "
                "structure invalidated → COMPLETED",
                active["symbol"], active["contract"], active["timeframe"],
                latest["price"], a_price,
            )
            _mark_completed(active, db)
            return None
    else:
        # SHORT: A=PEAK（最高点）, C=PEAK, C 不能高于 A
        if latest["price"] >= a_price:
            logger.info(
                "[_update_c_point] %s/%s %s: C point %.2f >= A %.2f, "
                "structure invalidated → COMPLETED",
                active["symbol"], active["contract"], active["timeframe"],
                latest["price"], a_price,
            )
            _mark_completed(active, db)
            return None

    old_price = active["point_c_price"]
    active["point_c_price"] = latest["price"]
    active["point_c_time"] = latest["timestamp"]
    _save_n_structure(db, active)

    logger.info(
        "[dynamic_restructure] %s/%s %s: C point updated "
        "(%.2f → %.2f, %s)",
        active["symbol"], active["contract"], active["timeframe"],
        old_price, latest["price"], c_type,
    )

    # ── C 滑动后结构优度验证 ──────────────────────────────────
    # C 更新后，旧 A→B→C 组合可能因新极值点不再是全局最优。
    # 用全量极值点（limit=40）做前向非重叠扫描，验证当前结构
    # 的 A 点是否仍为最优起点。
    try:
        verify_sp = _get_swing_points(
            db, active["symbol"], active["contract"], active["timeframe"], limit=40,
        )
        if len(verify_sp) >= 3:
            merged = _merge_same_type(verify_sp)
            if len(merged) >= 3:
                best = _find_n_structure_forward(merged)
                if best is not None:
                    best_a = best["a"]
                    curr_a_price = active["point_a_price"]
                    curr_a_time = active["point_a_time"]
                    if best_a["price"] != curr_a_price or best_a["timestamp"] != curr_a_time:
                        logger.info(
                            "[_update_c_point] %s/%s %s: C slid to %.2f but better "
                            "structure exists (A %.2f@%s → %.2f@%s), "
                            "marking COMPLETED + fallback to detect_and_save",
                            active["symbol"], active["contract"], active["timeframe"],
                            latest["price"],
                            curr_a_price, curr_a_time,
                            best_a["price"], best_a["timestamp"],
                        )
                        _mark_completed(active, db)
                        return None
    except Exception as exc:
        logger.warning(
            "[_update_c_point] %s/%s %s: C-slide verification skipped (%s)",
            active["symbol"], active["contract"], active["timeframe"], exc,
        )

    return active


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
    active = _get_active_n_structure(db, symbol, contract, timeframe, skip_condition4=True)
    if not active:
        # 已被收盘价检查淘汰（方向翻转）→ 全量重算
        return detect_and_save(symbol, contract, timeframe, db)

    # 1.5 记录结构在 DB 中的状态 — detect_and_save 可能因条件4将结构标记为
    # IDLE（如 SHORT 结构最新价 >= C）。如果之后没有结构性变动（A 突破/
    # B 反穿/C 滑动），应保持 IDLE 状态而非无条件重激活。
    was_idle = active.get("state") == NState.IDLE.value

    # 2. 提取结构关键参数（在 _get_klines 之前，供 since_timestamp 使用）
    direction = active["direction"]
    a_price = active["point_a_price"]
    b_price = active["point_b_price"]
    b_time = active["point_b_time"]

    # 3. 读取点 B 之后的所有 K 线（修复：limit=3 会遗漏早期突破数据）
    #    limit=None = 不限制数量，since_timestamp=b_time = 从 B 点至今
    klines = _get_klines(db, symbol, contract, timeframe, limit=None, since_timestamp=b_time)
    if not klines:
        active['is_active'] = not was_idle
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
        #    注意：仅靠 kline 日内高低点会误报（wick 噪声、C 点滑动），
        #    必须同时检查 swing point 确认（PEAK < B_price / TROUGH > B_price）
        b_range = abs(b_price - a_price)
        if b_range > 0:
            # 读取 swing points 用于确认
            b_reversal_swings = _get_swing_points(db, symbol, contract, timeframe, limit=10)
            b_reversal_sp = [sp for sp in b_reversal_swings if sp["timestamp"] > b_time]

            # B 反转的 swing 确认：
            #   LONG: 最新 swing PEAK 必须低于 B_price（极值点确认回撤），且是最新极值点
            #   SHORT: 最新 swing TROUGH 必须高于 B_price
            #   **检查最新整体极值点**：如果最新极值点是 C 同类型（LONG=TROUGH, SHORT=PEAK），
            #   说明行情仍在 C 滑动方向，不应触发 B 反转。
            c_type = "TROUGH" if direction == "LONG" else "PEAK"
            reversal_type = "PEAK" if direction == "LONG" else "TROUGH"
            has_b_reversal_swing = False
            latest_sp = b_reversal_sp[-1] if b_reversal_sp else None
            if latest_sp is not None:
                # 最新极值点必须是反转类型（PEAK for LONG, TROUGH for SHORT），
                # 而不是 C 滑动类型（TROUGH for LONG, PEAK for SHORT）
                if latest_sp["point_type"] == reversal_type:
                    if direction == "LONG" and latest_sp["price"] < b_price:
                        has_b_reversal_swing = True
                    elif direction == "SHORT" and latest_sp["price"] > b_price:
                        has_b_reversal_swing = True

            b_broken = False
            if direction == "LONG" and latest_low < b_price and has_b_reversal_swing:
                if (b_price - latest_low) / b_range > 0.5:
                    b_broken = True
            if direction == "SHORT" and latest_high > b_price and has_b_reversal_swing:
                if (latest_high - b_price) / b_range > 0.5:
                    b_broken = True

            if b_broken:
                # B 反穿 → 标记 COMPLETED + 全量重算（方向可能翻转）
                completed = dict(active)
                completed["state"] = NState.COMPLETED.value
                _save_n_structure(db, completed)
                logger.info(
                    "[dynamic_restructure] %s/%s %s: B reversed "
                    "(b_price=%.2f, range=%.2f, 50%% threshold, swing confirmed) → "
                    "COMPLETED + full recalc",
                    symbol, contract, timeframe, b_price, b_range,
                )
                return detect_and_save(symbol, contract, timeframe, db)

        # 3.6 C 点更新 — A 未突破、B 未反穿时检查 C 点滑动
        c_updated = _update_c_point(
            active,
            _get_swing_points(db, symbol, contract, timeframe, limit=10),
            db,
        )
        if c_updated is not None:
            active['is_active'] = True
            return c_updated

        # 无结构性变动（A 未突破、B 未反穿、C 未滑动）→ 保持原状态
        # 如果 detect_and_save 因条件 4 不满足已标记 IDLE，则不要重激活
        active['is_active'] = not was_idle
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

    # 4d.25 A_type 一致性检查：新方向必须与 new_A 的 swing type 匹配
    # LONG → A=TROUGH, SHORT → A=PEAK
    # new_A 来自 old_B：原 LONG→old_B=PEAK→new_A=PEAK, 原 SHORT→old_B=TROUGH→new_A=TROUGH
    # 当新方向与 new_A 的类型不匹配时（如 LONG 方向但 A=PEAK），迁移结果无效，
    # 必须回退到 detect_and_save 重新从极值点扫描。
    new_a_type = old_b_type  # PEAK (原 LONG) 或 TROUGH (原 SHORT)
    if (new_direction == "LONG" and new_a_type != "TROUGH") or \
       (new_direction == "SHORT" and new_a_type != "PEAK"):
        logger.info(
            "[dynamic_restructure] %s/%s %s: A_type mismatch "
            "(direction=%s but A_type=%s) → fallback to detect_and_save",
            symbol, contract, timeframe, new_direction, new_a_type,
        )
        return detect_and_save(symbol, contract, timeframe, db)
    # 4d.5 C2 方向一致性检查：迁移后的 B→C 必须与方向定义一致
    #   LONG (A=T→B=P→C=T): 第二笔下跌 → C < B
    #   SHORT (A=P→B=T→C=P): 第二笔上涨 → C > B
    #   C2 不符 → 迁移结果无效，回退全量重算
    if new_direction == "LONG" and new_c["price"] >= new_b["price"]:
        logger.info(
            "[dynamic_restructure] %s/%s %s: C2 check failed "
            "(LONG C=%.2f >= B=%.2f) → fallback to detect_and_save",
            symbol, contract, timeframe, new_c["price"], new_b["price"],
        )
        return detect_and_save(symbol, contract, timeframe, db)
    if new_direction == "SHORT" and new_c["price"] <= new_b["price"]:
        logger.info(
            "[dynamic_restructure] %s/%s %s: C2 check failed "
            "(SHORT C=%.2f <= B=%.2f) → fallback to detect_and_save",
            symbol, contract, timeframe, new_c["price"], new_b["price"],
        )
        return detect_and_save(symbol, contract, timeframe, db)

    # 4e. 状态重判 — 迁移后的3点交替结构已有效，直接LEG3
    state = NState.LEG3.value

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


# ─── 共享重算入口（API + Data Collector 共用）───────────────────

# 频率控制：每 symbol/tf 全量重算最多每 15 秒一次
_last_detect_save: dict = {}
_DETECT_SAVE_INTERVAL = 5


def _should_full_recalc(symbol: str, timeframe: str, min_interval: int = _DETECT_SAVE_INTERVAL) -> bool:
    """检测是否应对指定 symbol/tf 执行全量重算（频率控制）。

    detect_and_save 是全量重算（较贵），在频繁调用下必须限频。
    用 (symbol, timeframe) 做 key，记录上次全量重算时间。

    Args:
        symbol: 品种代码。
        timeframe: 周期。
        min_interval: 最小间隔（秒），默认 15。

    Returns:
        True=应执行全量重算，False=跳过（距离上次不足 min_interval）。
    """
    key = (symbol, timeframe)
    now = time_module.time()
    last = _last_detect_save.get(key, 0)
    if now - last >= min_interval:
        _last_detect_save[key] = now
        return True
    return False


# ─── IDLE→ACTIVE 重激活 ───────────────────────────────────────


def _reactive_idle_structures(
    symbol: str,
    contract: str,
    timeframe: str,
    db: Database,
) -> Optional[Dict[str, Any]]:
    """检查 IDLE 结构是否可重激活（新行情满足条件 4）。

    P0.4 新增。detect_and_save 的条件 4 硬过滤会因行情回撤将结构标记为
    IDLE。当行情恢复后（价格回到 C 附近），此函数负责重新激活。

    重激活条件（带 ε 缓冲区）：
    - LONG: 最新价 > C_price - ε
    - SHORT: 最新价 < C_price + ε
    - 同时确保条件 3 仍然满足（C 未突破 A）

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期。
        db: Database 实例。

    Returns:
        重激活后的结构字典，或 None（无需重激活）。
    """
    # 1. 读取当前结构（skip_condition4=True 排除条件 4 干扰）
    active = _get_active_n_structure(
        db, symbol, contract, timeframe, skip_condition4=True,
    )
    if not active:
        return None

    # 2. 仅处理 detect_and_save 返回 IDLE 但 DB 中仍为 LEG3 的结构
    # _get_active_n_structure(skip_condition4=True) 会返回所有未 COMPLETED
    # 的结构，包括条件 4 不满足的。条件是 detect_and_save 写了 IDLE 状态
    # 到返回字典但没写 DB（_save_n_structure 没调），所以 active["state"]
    # 仍然是 LEG3。我们通过 _get_active_n_structure 返回 None 的条件 4 检查
    # 来判断结构是否处于 IDLE 状态。

    # 3. 读取最新价
    klines = _get_klines(db, symbol, contract, timeframe, limit=1)
    if not klines:
        return None
    current_price = klines[-1]["close"]

    direction = active["direction"]
    c_price = active["point_c_price"]
    a_price = active["point_a_price"]

    # 4. 条件 3 检查（C 不可突破 A）— 以防 detect_and_save 的清扫遗漏
    if direction == "LONG" and c_price is not None and a_price is not None and c_price <= a_price:
        return None
    if direction == "SHORT" and c_price is not None and a_price is not None and c_price >= a_price:
        return None

    # 5. 带 ε 的条件 4 检查
    eps = cond4_epsilon(c_price)
    cond4_ok = False
    if direction == "LONG" and current_price > c_price - eps:
        cond4_ok = True
    if direction == "SHORT" and current_price < c_price + eps:
        cond4_ok = True

    if not cond4_ok:
        return None  # 仍不满足条件 4，保持 IDLE

    # 6. 条件 4 已满足 → 全量重算确保标点最优
    # 使用 detect_and_save 重新执行完整的前向扫描，因为价格恢复后可能有
    # 更优的 A/B/C 标点组合。重算后会写 DB 并返回新的活跃结构。
    result = detect_and_save(symbol, contract, timeframe, db)
    if result.get("is_active"):
        logger.info(
            "[idle_reactive] %s/%s %s: IDLE→ACTIVE (price=%.2f, C=%.2f, eps=%.4f)",
            symbol, contract, timeframe, current_price, c_price, eps,
        )
    return result


# ─── Stale 结构清扫 ───────────────────────────────────────────


def _sweep_stale_structures(db: Database) -> int:
    """清扫 stale N 型结构 — 条件 3 违规的直接标记 COMPLETED。

    P0.4 新增。detect_and_save 基于当前行情扫描，对不满足条件 3 的
    结构返回 IDLE 但不修改 DB 状态（不调 _save_n_structure）。
    导致条件 3 违规（C 破 A）的结构在 DB 中仍保持 LEG3 状态残留。

    _sweep_stale_structures 主动扫描所有非 COMPLETED 的结构，
    检测条件 3 违规并标记 COMPLETED。

    Returns:
        清扫并标记 COMPLETED 的结构数量。
    """
    import time as time_module

    now = int(time_module.time())
    cleaned = 0

    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_n_structures
               WHERE state NOT IN ('COMPLETED', 'IDLE')
               ORDER BY symbol, contract, timeframe"""
        ).fetchall()

        if not rows:
            return 0

        for row in rows:
            ns = dict(row)
            a_price = ns.get("point_a_price")
            c_price = ns.get("point_c_price")
            direction = ns.get("direction", "LONG")

            if a_price is None or c_price is None:
                continue

            # 条件 3 检查：C 不可突破 A
            cond3_fail = (
                (direction == "LONG" and c_price <= a_price)
                or (direction == "SHORT" and c_price >= a_price)
            )

            if cond3_fail:
                conn.execute(
                    """UPDATE futures_n_structures
                       SET state='COMPLETED', updated_at=datetime('now')
                       WHERE id=?""",
                    (ns["id"],),
                )
                cleaned += 1
                continue

            # 极端新鲜度违规（2× freshness 窗口）→ 也该清扫
            freshness = FRESHNESS.get(ns.get("timeframe", "1d"), 30 * 86400) * 2
            latest_ts = ns.get("point_c_time") or ns.get("point_b_time")
            if latest_ts and (now - latest_ts) > freshness:
                conn.execute(
                    """UPDATE futures_n_structures
                       SET state='COMPLETED', updated_at=datetime('now')
                       WHERE id=?""",
                    (ns["id"],),
                )
                cleaned += 1

        conn.commit()

    if cleaned:
        logger.info("[sweep_stale] 清扫完成: %d 个结构标记为 COMPLETED", cleaned)
    return cleaned


def restructure_active_for_symbol(
    symbol: str,
    contract: str,
    db: Database,
    timeframes: Optional[list] = None,
    force_full_recalc: bool = False,
) -> None:
    """对指定 symbol 的所有周期执行 N 型结构动态重算。

    管线：incremental_update → detect_and_save（限频）→ dynamic_restructure
    与 ``web/app.py::_restructure_active_structures()`` 逻辑一致但限单品种，
    供数据采集器在插入新 K 线后同步调用。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        db: Database 实例。
        timeframes: 周期列表，默认 ``["15m", "1h", "1d", "1w"]``。
        force_full_recalc: 是否强制全量重算（跳过频率控制），默认 False（限频）。
    """
    from futures.swing_points import incremental_update
    from futures.aggregator import aggregate_klines

    if timeframes is None:
        timeframes = ["15m", "1h", "1d", "1w"]

    for tf in timeframes:
        try:
            incremental_update(symbol, contract, tf, db)
        except Exception:
            pass  # 单周期极值点失败不阻塞整体

    # 0.5. 刷新周线K线聚合 — 确保周线包含本周最新价格
    try:
        aggregate_klines(symbol, contract, db, "1d", "1w", limit=14)
    except Exception:
        pass  # 周线聚合失败不阻塞后续重算

    # 1. 全量重算（频率控制或强制）
    for tf in timeframes:
        try:
            if force_full_recalc or _should_full_recalc(symbol, tf):
                detect_and_save(symbol, contract, tf, db)
        except Exception:
            pass  # 全量重算失败不阻塞后续动态迁移
    # 2. 动态重算（含 C 点滑动 + A 突破迁移）
    for tf in timeframes:
        try:
            dynamic_restructure(symbol, contract, tf, db)
        except Exception:
            pass  # 单周期动态重算失败不阻塞整体

    # 3. IDLE→ACTIVE 重激活（P0.4 新增）
    # detect_and_save 的条件 4 硬过滤会将行情回撤的结构标记 IDLE。
    # 行情恢复后，_reactive_idle_structures 检查最新价是否重回 C 附近
    # （带 ε 缓冲区），如是则触发全量重算恢复活跃性。
    for tf in timeframes:
        try:
            _reactive_idle_structures(symbol, contract, tf, db)
        except Exception:
            pass  # 单周期重激活失败不阻塞整体


def incremental_restructure_only(
    symbol: str,
    contract: str,
    db: Database,
    timeframes: Optional[list] = None,
) -> None:
    """轻量级增量重算：跳过 detect_and_save 全量扫描，仅执行状态迁移。

    管线：incremental_update → aggregate_klines → dynamic_restructure
    → _reactive_idle_structures

    与 ``restructure_active_for_symbol()`` 的区别：
    - 不调用 detect_and_save（全量扫描限频 15s，是重算中最重的操作）
    - 不调用 _should_full_recalc 频率控制（没有 detect_and_save 需限频）
    - 适合高频调用场景：API 30s 轮询 / 新增心跳线程

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        db: Database 实例。
        timeframes: 周期列表，默认 ``["15m", "1h", "1d", "1w"]``。
    """
    from futures.swing_points import incremental_update
    from futures.aggregator import aggregate_klines

    if timeframes is None:
        timeframes = ["15m", "1h", "1d", "1w"]

    # 1. 增量更新极值点
    for tf in timeframes:
        try:
            incremental_update(symbol, contract, tf, db)
        except Exception:
            pass

    # 2. 刷新周线聚合
    try:
        aggregate_klines(symbol, contract, db, "1d", "1w", limit=14)
    except Exception:
        pass

    # 3. 增量状态迁移（跳过 detect_and_save 全量扫描）
    for tf in timeframes:
        try:
            dynamic_restructure(symbol, contract, tf, db)
        except Exception:
            pass

    # 4. IDLE→ACTIVE 重激活
    for tf in timeframes:
        try:
            _reactive_idle_structures(symbol, contract, tf, db)
        except Exception:
            pass


def restructure_all_active_incremental(db: Database) -> None:
    """对所有活跃品种执行轻量增量重算（跳过全量扫描）。

    读取 ``futures_n_structures`` 表中所有非 COMPLETED/IDLE 的结构，
    逐个调用 ``incremental_restructure_only()``。

    与 ``restructure_all_active()`` 的区别：
    - 不调用 detect_and_save 全量扫描
    - 不调用 _should_full_recalc 频率控制
    - 适合高频调用（API 30s 轮询 / 5s 心跳）

    Args:
        db: Database 实例。
    """
    try:
        # 先清扫 stale 结构
        try:
            swept = _sweep_stale_structures(db)
            if swept:
                logger.info("[restructure_all_active_incremental] 清扫 %d 个 stale 结构", swept)
        except Exception as exc:
            logger.warning("[restructure_all_active_incremental] 清扫异常(跳过): %s", exc)

        timeframes = ["15m", "1h", "1d", "1w"]

        active = db.get_conn().execute(
            """SELECT DISTINCT symbol, contract FROM futures_n_structures
               WHERE state NOT IN ('COMPLETED', 'IDLE')"""
        ).fetchall()

        if not active:
            return

        for row in active:
            sym, contract = row["symbol"], row["contract"]
            incremental_restructure_only(
                sym, contract, db, timeframes=timeframes,
            )
    except Exception:
        pass  # 整体失败不抛出


def restructure_all_active(db: Database) -> None:
    """对所有有活跃 N 型结构的品种执行动态重算 + stale 清扫。

    读取 ``futures_n_structures`` 表中所有非 COMPLETED/IDLE 的结构，
    逐个调用 ``restructure_active_for_symbol()``。

    P0.4 新增：调用前先执行 _sweep_stale_structures 清扫条件 3 违规
    的结构（C 破 A 但 DB 状态仍为 LEG3 的残留）。

    供 API 层（替代 ``web/app.py::_restructure_active_structures()``）
    和数据采集层共用。

    Args:
        db: Database 实例。
    """
    try:
        # P0.4: Stale 清扫 — 先干掉条件 3 违规的结构
        try:
            swept = _sweep_stale_structures(db)
            if swept:
                logger.info("[restructure_all_active] 清扫 %d 个 stale 结构", swept)
        except Exception as exc:
            logger.warning("[restructure_all_active] 清扫异常(跳过): %s", exc)

        timeframes = ["15m", "1h", "1d", "1w"]

        # 读活跃结构列表
        active = db.get_conn().execute(
            """SELECT DISTINCT symbol, contract FROM futures_n_structures
               WHERE state NOT IN ('COMPLETED', 'IDLE')"""
        ).fetchall()

        if not active:
            return

        for row in active:
            sym, contract = row["symbol"], row["contract"]
            restructure_active_for_symbol(
                sym, contract, db, timeframes=timeframes,
            )
    except Exception:
        pass  # 整体失败不抛出


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
