"""
三级嵌套验证评分引擎。

核心逻辑：
  Level1 = 周线N型结构 + 日线MACD颜色轨迹验证（红→绿→红→减弱）
  Level2 = 小时线N型结构 + 15分钟MACD颜色轨迹验证
  Level3 = 15分钟N型结构 + 3分钟MACD验证 + 15分钟突破15分钟B点
   加分 = 月线+周线MACD / 日线+小时线MACD 等更大周期配合

所有DB访问通过 ``db: Database`` 参数完成。
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.db import Database
from config.settings import (
    LEVEL1_TIMEFRAME,
    LEVEL1_MACD_TIMEFRAME,
    LEVEL2_TIMEFRAME,
    LEVEL2_MACD_TIMEFRAME,
    LEVEL3_TIMEFRAME,
    BONUS_CHECKS,
    LEVEL1_MIN_SCORE,
    LEVEL2_MIN_SCORE,
    LEVEL3_MIN_SCORE,
)
from futures.color_tracker import check_macd_trajectory, check_3m_stability
from futures.n_structure import check_realtime_breakout

logger = logging.getLogger(__name__)


# ─── DB 内部辅助 ─────────────────────────────────────────────


def _get_active_n_structure(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
) -> Optional[Dict[str, Any]]:
    """获取未完成的活跃N型结构。"""
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


def _get_all_main_contracts(db: Database) -> List[Dict[str, Any]]:
    """获取所有有K线数据的主力合约。"""
    with db.get_conn() as conn:
        # 从 symbols 表获取已上市期权的品种
        rows = conn.execute(
            """SELECT DISTINCT
                 s.symbol,
                 s.name,
                 s.option_name,
                 k.contract as contract_code
               FROM symbols s
               INNER JOIN (
                 SELECT DISTINCT symbol, contract
                 FROM futures_klines
               ) k ON s.symbol = k.symbol
               WHERE s.has_options = 1
               ORDER BY s.symbol"""
        ).fetchall()
    return [dict(r) for r in rows]


def _save_signal(db: Database, sig: Dict[str, Any]) -> int:
    """保存期货信号到数据库。"""
    detail_json = json.dumps(sig.get("detail", {}), ensure_ascii=False)
    with db.get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO futures_signals
               (symbol, contract, direction, signal_type,
                level1_pass, level2_pass, level3_pass,
                entry_price, stop_loss, take_profit, score, detail)
               VALUES (?,?,?,?, ?,?,?, ?,?,?,?,?)""",
            (
                sig["symbol"],
                sig["contract"],
                sig["direction"],
                sig["signal_type"],
                int(sig.get("level1_pass", 0)),
                int(sig.get("level2_pass", 0)),
                int(sig.get("level3_pass", 0)),
                sig.get("entry_price"),
                sig.get("stop_loss"),
                sig.get("take_profit"),
                sig.get("score", 0),
                detail_json,
            ),
        )
        conn.commit()
        return cur.lastrowid


# ─── 数据类 ──────────────────────────────────────────────────


@dataclass
class SignalResult:
    """三级验证信号结果。

    Attributes:
        symbol: 品种代码。
        contract: 合约代码。
        direction: LONG / SHORT / NONE。
        level1: Level1 验证结果。
        level2: Level2 验证结果。
        level3: Level3 验证结果。
        bonus: 加分项列表。
        overall_score: 综合评分。
        signal_type: NONE / WATCH / CANDIDATE / ENTRY。
        entry_price: 入场价。
        stop_loss: 止损价。
        take_profit: 止盈价。
    """

    symbol: str
    contract: str
    direction: str = "NONE"
    level1: dict = field(default_factory=dict)
    level2: dict = field(default_factory=dict)
    level3: dict = field(default_factory=dict)
    bonus: list = field(default_factory=list)
    overall_score: float = 0.0
    signal_type: str = "NONE"
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


# ─── 内部辅助 ────────────────────────────────────────────────


def _calculate_sl_tp(
    result: SignalResult, n_struct: Dict[str, Any]
) -> tuple:
    """计算止损止盈，基于入场级别的N型结构（15分钟）。

    原理：
      - SL = A点（结构极值）
      - TP = 入场价 ± (A-B高度) * 0.5

    Returns:
        (sl, tp) 或 (None, None)。
    """
    direction = result.direction
    entry_price = result.entry_price
    a_price = n_struct.get("point_a_price")
    b_price = n_struct.get("point_b_price")

    if a_price is None or b_price is None or entry_price is None:
        return None, None

    sl = a_price

    if direction == "LONG":
        height = abs(b_price - a_price)
        tp = entry_price + height * 0.5
    elif direction == "SHORT":
        height = abs(a_price - b_price)
        tp = entry_price - height * 0.5
    else:
        return None, None

    return round(sl, 2), round(tp, 2)


def _check_bonus(
    symbol: str,
    contract: str,
    direction: str,
    db: Database,
) -> List[Dict[str, Any]]:
    """检查加分项（更大周期N型+MACD配合）。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        direction: 方向。
        db: Database 实例。

    Returns:
        加分项检查结果列表。
    """
    bonuses: List[Dict[str, Any]] = []
    for n_tf, macd_tf, score in BONUS_CHECKS:
        try:
            n_struct = _get_active_n_structure(db, symbol, contract, n_tf)
            if n_struct and n_struct.get("direction") == direction:
                macd_result = check_macd_trajectory(
                    symbol, contract, n_struct, macd_tf, direction, db
                )
                if macd_result.get("passed"):
                    bonuses.append(
                        {
                            "check": f"{n_tf}N型+{macd_tf}MACD",
                            "passed": True,
                            "score": score,
                            "detail": macd_result.get("description", ""),
                        }
                    )
                else:
                    bonuses.append(
                        {
                            "check": f"{n_tf}N型+{macd_tf}MACD",
                            "passed": False,
                            "score": 0,
                            "detail": f"MACD轨迹未配合: {macd_result.get('description', '')}",
                        }
                    )
            else:
                bonuses.append(
                    {
                        "check": f"{n_tf}N型+{macd_tf}MACD",
                        "passed": False,
                        "score": 0,
                        "detail": "无活跃N型或方向不一致",
                    }
                )
        except Exception as e:
            logger.warning("加分项检查异常: %s", e)
            bonuses.append(
                {
                    "check": f"{n_tf}N型+{macd_tf}MACD",
                    "passed": False,
                    "score": 0,
                    "detail": f"检查异常: {e}",
                }
            )
    return bonuses


def _level1_description(
    direction: str, state: str, macd: Dict[str, Any]
) -> str:
    """构建 Level1 描述。"""
    dir_cn = "正N做多" if direction == "LONG" else "倒N做空"
    macd_desc = macd.get("description", "")
    if macd_desc:
        return f"周线{dir_cn} ({state}) | 日线MACD: {macd_desc}"
    return f"周线{dir_cn} ({state})"


def _level2_description(
    direction: str, state: str, macd: Dict[str, Any]
) -> str:
    """构建 Level2 描述。"""
    dir_cn = "正N做多" if direction == "LONG" else "倒N做空"
    macd_desc = macd.get("description", "")
    if macd_desc:
        return f"小时线{dir_cn} ({state}) | 15分钟MACD: {macd_desc}"
    return f"小时线{dir_cn} ({state})"


def _level3_description(
    direction: str,
    state: str,
    stability: Dict[str, Any],
    breakout: Dict[str, Any],
) -> str:
    """构建 Level3 描述。"""
    dir_cn = "正N做多" if direction == "LONG" else "倒N做空"
    b_detail = breakout.get("detail", "")
    s_detail = ""
    if stability.get("stable"):
        stats = stability.get("stats", {})
        s_detail = (
            f"3m稳定(切换{stats.get('switch_count', '?')}次,"
            f"主体{stats.get('dominant_color', '?')})"
        )
    else:
        s_detail = stability.get("reason", "3m不稳定")
    return f"15分钟{dir_cn} ({state}) | {s_detail} | {b_detail}"


# ─── 核心：三维嵌套验证 ──────────────────────────────────────


def evaluate(
    symbol: str,
    contract: str,
    db: Database,
) -> SignalResult:
    """完整三级嵌套验证。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        db: Database 实例。

    Returns:
        SignalResult 信号结果。
    """
    result = SignalResult(symbol=symbol, contract=contract, direction="NONE")

    # ═══════════════════════════════════════════════════
    # Level1: 周线N型定方向 + 日线MACD轨迹验证
    # ═══════════════════════════════════════════════════
    l1_struct = _get_active_n_structure(db, symbol, contract, LEVEL1_TIMEFRAME)

    if l1_struct is None or l1_struct.get("state") not in ("LEG2", "LEG3"):
        result.level1 = {
            "passed": False,
            "reason": (
                "无周线活跃N型结构"
                if l1_struct is None
                else f"状态{l1_struct['state']}不可用"
            ),
            "n_structure": l1_struct,
        }
        result.overall_score = 0.0
        result.signal_type = "NONE"
        return result

    direction = l1_struct["direction"]
    result.direction = direction

    l1_macd = check_macd_trajectory(
        symbol, contract, l1_struct, LEVEL1_MACD_TIMEFRAME, direction, db
    )

    result.level1 = {
        "passed": True,
        "direction": direction,
        "state": l1_struct["state"],
        "n_structure": {
            "point_a_price": l1_struct["point_a_price"],
            "point_b_price": l1_struct["point_b_price"],
            "point_c_price": l1_struct.get("point_c_price"),
            "point_a_time": l1_struct["point_a_time"],
            "point_b_time": l1_struct["point_b_time"],
        },
        "macd_trajectory": l1_macd,
        "description": _level1_description(
            direction, l1_struct["state"], l1_macd
        ),
    }

    # ═══════════════════════════════════════════════════
    # Level2: 小时线N型确认 + 15分钟MACD轨迹验证
    # ═══════════════════════════════════════════════════
    l2_struct = _get_active_n_structure(db, symbol, contract, LEVEL2_TIMEFRAME)

    l2_result: Dict[str, Any] = {"passed": False}
    if l2_struct and l2_struct.get("direction") == direction:
        l2_macd = check_macd_trajectory(
            symbol, contract, l2_struct, LEVEL2_MACD_TIMEFRAME, direction, db
        )
        if l2_macd.get("passed"):
            l2_result = {
                "passed": True,
                "direction": direction,
                "state": l2_struct["state"],
                "n_structure": {
                    "point_a_price": l2_struct["point_a_price"],
                    "point_b_price": l2_struct["point_b_price"],
                    "point_c_price": l2_struct.get("point_c_price"),
                },
                "macd_trajectory": l2_macd,
                "description": _level2_description(
                    direction, l2_struct["state"], l2_macd
                ),
            }
        else:
            l2_result = {
                "passed": False,
                "reason": (
                    f"小时线MACD轨迹未配合: {l2_macd.get('description', '')}"
                ),
                "macd_trajectory": l2_macd,
            }
    elif l2_struct:
        l2_result = {
            "passed": False,
            "reason": f"小时线方向{l2_struct.get('direction')}不匹配周线{direction}",
        }
    else:
        l2_result = {
            "passed": False,
            "reason": "小时线无活跃N型结构",
        }

    result.level2 = l2_result

    if not l2_result["passed"]:
        result.overall_score = 0.3
        result.signal_type = "WATCH"
        result.bonus = _check_bonus(symbol, contract, direction, db)
        bonus_total = sum(b["score"] for b in result.bonus if b["passed"])
        result.overall_score = min(0.3 + bonus_total, 1.0)
        return result

    # ═══════════════════════════════════════════════════
    # Level3: 15分钟N型入场 + 3分钟MACD稳定 + 突破
    # ═══════════════════════════════════════════════════
    l3_struct = _get_active_n_structure(db, symbol, contract, LEVEL3_TIMEFRAME)

    l3_result: Dict[str, Any] = {"passed": False}

    if l3_struct and l3_struct.get("direction") == direction:
        stability = check_3m_stability(symbol, contract, direction, db)
        breakout = check_realtime_breakout(symbol, contract, l3_struct, db)

        l3_result = {
            "passed": False,
            "direction": direction,
            "state": l3_struct["state"],
            "n_structure": {
                "point_a_price": l3_struct["point_a_price"],
                "point_b_price": l3_struct["point_b_price"],
                "point_c_price": l3_struct.get("point_c_price"),
            },
            "stability": stability,
            "breakout": breakout,
            "description": _level3_description(
                direction, l3_struct["state"], stability, breakout
            ),
        }

        if breakout.get("triggered") and stability.get("stable"):
            l3_result["passed"] = True
            result.overall_score = 1.0
            result.signal_type = "ENTRY"
            result.entry_price = breakout.get("trigger_price")
            sl, tp = _calculate_sl_tp(result, l3_struct)
            result.stop_loss = sl
            result.take_profit = tp
        else:
            result.overall_score = 0.6
            result.signal_type = "CANDIDATE"
    else:
        l3_result = {
            "passed": False,
            "reason": "15分钟无活跃N型或方向不一致",
        }
        result.overall_score = 0.6
        result.signal_type = "CANDIDATE"

    result.level3 = l3_result

    # ═══════════════════════════════════════════════════
    # 加分项
    # ═══════════════════════════════════════════════════
    result.bonus = _check_bonus(symbol, contract, direction, db)
    bonus_total = sum(b["score"] for b in result.bonus if b["passed"])
    result.overall_score = min(result.overall_score + bonus_total, 1.0)

    return result


def scan_all_contracts(db: Database) -> List[SignalResult]:
    """扫描所有主力合约，返回按 overall_score 降序排列的结果。

    Args:
        db: Database 实例。

    Returns:
        信号结果列表，按评分降序。
    """
    contracts = _get_all_main_contracts(db)
    results: List[SignalResult] = []

    for mc in contracts:
        symbol = mc["symbol"]
        contract_code = mc["contract_code"]
        try:
            sr = evaluate(symbol, contract_code, db)
            results.append(sr)
        except Exception as e:
            logger.warning("评估 %s %s 异常: %s", symbol, contract_code, e)
            results.append(
                SignalResult(
                    symbol=symbol,
                    contract=contract_code,
                    direction="NONE",
                    level1={"passed": False, "reason": f"评估异常: {e}"},
                )
            )

    results.sort(key=lambda x: x.overall_score, reverse=True)
    return results
