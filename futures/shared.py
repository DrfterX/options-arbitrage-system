"""
期货信号分析引擎共享工具函数。

集中存放被多个模块引用的通用辅助函数，避免重复副本导致参数不一致。
"""

import logging
from typing import Any, Dict, Optional

from core.db import Database

logger = logging.getLogger(__name__)

# ─── N 型结构新鲜度窗口 ──────────────────────────────────────
# 各周期下结构被视为"活跃"的时间上限（秒）。
# 超出此窗口的结构被视为陈旧，需由 detect_and_save 全量重算。
FRESHNESS: Dict[str, int] = {
    "3m": 2 * 86400,   # 2 天
    "15m": 2 * 86400,  # 2 天
    "1h": 7 * 86400,   # 7 天
    "1d": 30 * 86400,  # 30 天
    "1w": 60 * 86400,  # 60 天
}

# ─── 条件 4 ε 阈值（防闪烁） ──────────────────────────────────
# 条件 4 要求 LONG 最新价 > C, SHORT 最新价 < C。
# 当价格在 C 附近微小波动时，严格的 >/< 会导致 IDLE↔ACTIVE 闪烁。
# ε 提供一个小缓冲区：
#   LONG: 最新价 > C - ε
#   SHORT: 最新价 < C + ε
COND4_EPSILON_RATIO = 0.001   # C 价的 0.1%
COND4_EPSILON_ABSOLUTE = 0.5  # 最小绝对 ε（单位：价格单位）


def cond4_epsilon(c_price: float) -> float:
    """计算条件 4 的 ε 缓冲区大小。

    ε = max(COND4_EPSILON_ABSOLUTE, C * COND4_EPSILON_RATIO)

    对于高价品种（如铜 ~100000），ε ≈ 100 (0.1%)
    对于低价品种（如玉米 ~2300），ε ≈ 2.3 (0.1%) 但最低 0.5

    Args:
        c_price: C 点价格。

    Returns:
        ε 值（价格单位）。
    """
    return max(COND4_EPSILON_ABSOLUTE, c_price * COND4_EPSILON_RATIO)


def _get_active_n_structure(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    skip_condition4: bool = False,
) -> Optional[Dict[str, Any]]:
    """获取未完成的活跃 N 型结构。

    额外校验：
      1. 时间新鲜度 — C/B 点时间在 freshness 窗口内
      2. 结构有效性 — C 点不可突破 A 点（LONG: C ≥ A；SHORT: C ≤ A）
      3. 极端止损检查 — 最新 K 线收盘价已突破 A 点则失效
      4. 第三笔方向确认 — 最新价必须与 C 点保持方向一致性（LONG: 价 > C；SHORT: 价 < C）

    Args:
        db: Database 实例。
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: K 线周期。
        skip_condition4: 是否跳过条件 4（第三笔方向确认）检查。
            当 True 时跳过，供 dynamic_restructure 使用；API 消费者保持默认 False。

    Returns:
        活跃 N 型结构字典，如无活跃结构则返回 None。
    """
    import time as time_module

    now = int(time_module.time())

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

        # 0. B→C 方向一致性检查（C2）— 必须在新鲜度检查之前执行
        # 第二笔（B→C）必须与方向定义一致：
        #   LONG: 第二笔下跌 → C 必须低于 B
        #   SHORT: 第二笔上涨 → C 必须高于 B
        # C2 不满足意味着算法标点偏差（如前期 dynamic_restructure 迁移产生的
        # A_type 不匹配 + C 方向错误），即使结构已陈旧也应标记 COMPLETED 并清除，
        # 防止 stale LEG3 行在 DB 持续残留。此检查必须在新鲜度过滤前执行，
        # 否则旧结构（超过 freshness 窗口）会提前返回 None，错过 C2 修复。
        c_price = ns.get("point_c_price")
        b_price = ns.get("point_b_price")
        a_price = ns.get("point_a_price")
        if ns["direction"] == "LONG" and c_price and b_price and c_price >= b_price:
            conn.execute(
                "UPDATE futures_n_structures SET state='COMPLETED', updated_at=datetime('now') WHERE id=?",
                (ns["id"],),
            )
            conn.commit()
            return None
        if ns["direction"] == "SHORT" and c_price and b_price and c_price <= b_price:
            conn.execute(
                "UPDATE futures_n_structures SET state='COMPLETED', updated_at=datetime('now') WHERE id=?",
                (ns["id"],),
            )
            conn.commit()
            return None

        # 1. 时间新鲜度检查
        freshness_cutoff = FRESHNESS.get(timeframe, 60 * 86400)
        latest_ts = ns.get("point_c_time") or ns.get("point_b_time")
        if latest_ts and (now - latest_ts) > freshness_cutoff:
            return None

        # 2. 结构有效性检查：C 不可突破 A
        # C3 检查：C 点不可突破 A 点（LONG: C > A, SHORT: C < A）。
        # 与 C2 检查同位 — 在新鲜度和收盘价检查之前执行，确保结构的基本
        # 几何有效性。C3 不满足意味着 C 被 dynamic_restructure 的 C-sliding
        # 推过了 A 边界（或初始扫描时使用了退选候选人的宽松模式），应标记
        # COMPLETED 并清除，防止 stale LEG3 行在 DB 持续残留。
        if ns["direction"] == "LONG" and c_price is not None and a_price is not None and c_price <= a_price:
            conn.execute(
                "UPDATE futures_n_structures SET state='COMPLETED', updated_at=datetime('now') WHERE id=?",
                (ns["id"],),
            )
            conn.commit()
            return None
        if ns["direction"] == "SHORT" and c_price is not None and a_price is not None and c_price >= a_price:
            conn.execute(
                "UPDATE futures_n_structures SET state='COMPLETED', updated_at=datetime('now') WHERE id=?",
                (ns["id"],),
            )
            conn.commit()
            return None

        # 3. 极端止损检查：当前收盘价已突破 A 点
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

        # 4. 第三笔方向确认（条件 4）— 带 ε 缓冲区防闪烁
        # LONG: 最新价必须 > C - ε（允许小幅回撤到 C 以下）
        # SHORT: 最新价必须 < C + ε（允许小幅反弹到 C 以上）
        # 注意：skip_condition4=True 供 dynamic_restructure 使用，避免 A 突破迁移被阻断
        if not skip_condition4 and last_kline and c_price:
            eps = cond4_epsilon(c_price)
            if ns["direction"] == "LONG" and last_kline["close"] <= c_price - eps:
                return None
            if ns["direction"] == "SHORT" and last_kline["close"] >= c_price + eps:
                return None

        # 5. 1d/1w 时间戳归一化（确保与归一化后的 K 线时间戳对齐）
        normalize_n_timestamps(ns)

        return ns


# ─── 1d/1w 时间戳归一化 ───────────────────────────────────────


def normalize_n_timestamps(ns: Dict[str, Any]) -> Dict[str, Any]:
    """归一化 N 型结构的 A/B/C 点时间戳（原地修改）。

    对 1d/1w 周期，将 N 型结构的 point_a_time/point_b_time/point_c_time
    从任意时间偏移归一化到 05:45 UTC (= 13:45 BJT)，与归一化后的 K 线
    时间戳对齐，确保前端 ``findBarForNPoint()`` 的几何匹配落在正确的 K 线 bar 上。

    ``_get_swing_points()`` 在计算新结构时已执行此归一化，但已存储的
    旧行可能在归一化代码添加前写入。此函数用于所有读取路径，确保无论
    结构是何时计算的，返回给前端的时间戳始终与 K 线对齐。

    Args:
        ns: N 型结构字典（会被原地修改）。

    Returns:
        同一字典引用（便于链式调用）。
    """
    tf = ns.get("timeframe")
    if tf not in ("1d", "1w"):
        return ns

    BJ_OFFSET = 8 * 3600       # 北京时间 UTC+8
    TARGET_HOUR_SEC = 20700     # 05:45 UTC = 13:45 BJT

    for key in ("point_a_time", "point_b_time", "point_c_time"):
        ts = ns.get(key)
        if ts is None:
            continue
        bj_midnight_utc = ((ts + BJ_OFFSET) // 86400) * 86400 - BJ_OFFSET
        ns[key] = bj_midnight_utc + TARGET_HOUR_SEC

    return ns