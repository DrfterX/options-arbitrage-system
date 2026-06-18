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

        # 1. 时间新鲜度检查
        freshness_cutoff = FRESHNESS.get(timeframe, 60 * 86400)
        latest_ts = ns.get("point_c_time") or ns.get("point_b_time")
        if latest_ts and (now - latest_ts) > freshness_cutoff:
            return None

        # 2. 结构有效性检查：C 不可突破 A
        a_price = ns.get("point_a_price")
        c_price = ns.get("point_c_price")
        if ns["direction"] == "SHORT" and a_price and c_price and c_price >= a_price:
            return None
        if ns["direction"] == "LONG" and a_price and c_price and c_price <= a_price:
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

        # 4. 第三笔方向确认（条件 4）：最新价与 C 点比较
        # LONG: 最新价必须 > C（确认第三笔向上破位）
        # SHORT: 最新价必须 < C（确认第三笔向下破位）
        # 注意：skip_condition4=True 供 dynamic_restructure 使用，避免 A 突破迁移被阻断
        if not skip_condition4 and last_kline and c_price:
            if ns["direction"] == "LONG" and last_kline["close"] <= c_price:
                return None
            if ns["direction"] == "SHORT" and last_kline["close"] >= c_price:
                return None

        return ns