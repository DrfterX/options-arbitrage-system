"""
三级嵌套验证评分引擎（★ P0指令覆盖：3分硬条件入场制 — Cycle #59）。

核心逻辑：
  Level1 = 周线N型结构 + 日线MACD颜色轨迹验证（红→绿→红→减弱）
  Level2 = 小时线N型结构 + 15分钟MACD颜色轨迹验证
  Level3 = 15分钟N型结构 + 3分钟MACD验证 + 15分钟突破B点
   加分 = 月线+周线MACD / 日线+小时线MACD 等更大周期配合

评分规则（P0指令覆盖 Cycle #35 梯度策略）：
  score=3(L1+L2+L3+MACD硬) → ENTRY
  score=4(+加分项)         → ADD_POSITION
  score<3                  → NONE
  3分是硬性入场条件，缺一分都不行。加分不计入基础分。

所有DB访问通过 ``db: Database`` 参数完成。
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.db import Database
from config.settings import (
    COLOR_BLUE,
    COLOR_RED,
    LEVEL1_TIMEFRAME,
    LEVEL1_MACD_TIMEFRAME,
    LEVEL2_TIMEFRAME,
    LEVEL2_MACD_TIMEFRAME,
    LEVEL3_TIMEFRAME,
    BONUS_CHECKS,
)
from futures.color_tracker import check_color_sequence, check_macd_trajectory, check_3m_stability
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
        "3m": 5 * 86400,
        "15m": 5 * 86400,
        "1h": 14 * 86400,
        "1d": 45 * 86400,
        "1w": 90 * 86400,
    }

    with db.get_conn() as conn:
        row = conn.execute(
            """SELECT * FROM futures_n_structures
               WHERE symbol=? AND timeframe=? AND state!='COMPLETED'
               ORDER BY updated_at DESC LIMIT 1""",
            (symbol, timeframe),
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
                 AND k.contract != s.symbol
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
class DiagnosticLevel:
    """诊断模式下的单级检查详细追踪记录。"""

    passed: bool
    reasons: List[str]
    data: Dict[str, Any]

    def __init__(self, passed: bool = False, name: str = ""):
        self.passed = passed
        self.reasons = []
        self.data = {}
        self.name = name

    def log(self, msg: str) -> None:
        self.reasons.append(msg)

    def set_data(self, key: str, value: Any) -> None:
        self.data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "reasons": self.reasons,
            "data": self.data,
        }


@dataclass
class SignalResult:
    """三级验证信号结果（离散3分制）。

    Attributes:
        symbol: 品种代码。
        contract: 合约代码。
        direction: LONG / SHORT / NONE。
        level1: Level1 验证结果。
        level2: Level2 验证结果。
        level3: Level3 验证结果。
        bonus: 加分项列表。
        overall_score: 综合评分（0-4 整数：0=NONE, 1=L1, 2=L1+L2, 3=ENTRY, 4=加仓）。
        signal_type: NONE / ENTRY / ADD_POSITION。
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
    overall_score: int = 0
    signal_type: str = "NONE"
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    diagnostic: Optional[dict] = None


# ─── 内部辅助 ────────────────────────────────────────────────


def _calculate_sl_tp(
    result: SignalResult, n_struct: Dict[str, Any], l1_struct: Dict[str, Any]
) -> tuple:
    """计算止损止盈，基于入场级别的N型结构（15分钟），止盈用大周期（周线）第一笔幅度推算。

    原则：
      - SL 永远用「最近有效极值点」，而非结构起点 A：
        - LEG2 状态：C 点（最近反向极值）为最合理止损位
        - LEG3 状态：B 点（突破点位变支撑/阻力）为最合理止损位
      - TP = 入场价 ± 大周期第一笔幅度（Level1 A→B 波幅）
        天然获得 1:10~1:30+ 超大盈亏比，替代固定 2:1。

    Returns:
        (sl, tp) 或 (None, None)。
    """
    direction = result.direction
    entry_price = result.entry_price
    a_price = n_struct.get("point_a_price")
    b_price = n_struct.get("point_b_price")
    c_price = n_struct.get("point_c_price")
    state = n_struct.get("state", "LEG2")

    if a_price is None or b_price is None or entry_price is None:
        return None, None

    # 止损位：LEG3 用 B 点，LEG2 用 C 点（最近极值），兜底用 B
    if state == "LEG3":
        sl = b_price
    else:
        sl = c_price if c_price is not None else b_price

    if sl is None:
        return None, None

    # 止盈位：大周期（Level1）第一笔 A→B 幅度推算第三笔目标
    l1_a = l1_struct.get("point_a_price")
    l1_b = l1_struct.get("point_b_price")
    if l1_a is not None and l1_b is not None:
        amplitude = abs(l1_b - l1_a)

        if direction == "LONG":
            tp = entry_price + amplitude
        elif direction == "SHORT":
            tp = entry_price - amplitude
        else:
            return None, None
    else:
        # 兜底：无法获取Level1波幅则用固定 2:1
        risk = abs(entry_price - sl)
        if direction == "LONG":
            tp = entry_price + risk * 2.0
        elif direction == "SHORT":
            tp = entry_price - risk * 2.0
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


# ─── 评分重置检查 ──────────────────────────────────────


def _check_structure_invalidation(
    symbol: str,
    contract: str,
    direction: str,
    db: Database,
    timeframe: str = LEVEL1_TIMEFRAME,
) -> bool:
    """检查大周期结构是否已被破坏（第4笔破坏第2笔终点）。

    LONG: 最新收盘价跌破 point_b_price 的 99% → 结构失效
    SHORT: 最新收盘价升破 point_b_price 的 101% → 结构失效

    Args:
        symbol: 品种代码
        contract: 合约代码
        direction: 当前方向
        db: Database 实例
        timeframe: 检查的周期（默认 Level1=周线）

    Returns:
        True = 结构已破坏，评分应重置
    """
    n_struct = _get_active_n_structure(db, symbol, contract, timeframe)
    if n_struct is None or n_struct.get("direction") != direction:
        return False

    b_price = n_struct.get("point_b_price")
    if b_price is None:
        return False

    with db.get_conn() as conn:
        row = conn.execute(
            """SELECT close FROM futures_klines
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp DESC LIMIT 1""",
            (symbol, contract, timeframe),
        ).fetchone()

    if row is None:
        return False

    close = row["close"]

    if direction == "LONG":
        return close < b_price * 0.99
    elif direction == "SHORT":
        return close > b_price * 1.01

    return False


def _check_reverse_n_structure(
    symbol: str,
    contract: str,
    direction: str,
    db: Database,
) -> bool:
    """检查是否出现足够强的反向N型结构。

    反向结构至少达到 Level1（N型 + MACD配合）→ 当前方向评分应重置。

    Args:
        symbol: 品种代码
        contract: 合约代码
        direction: 当前方向
        db: Database 实例

    Returns:
        True = 反向结构达开仓条件，评分应重置
    """
    if direction == "NONE":
        return False

    reverse_dir = "SHORT" if direction == "LONG" else "LONG"

    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_n_structures
               WHERE symbol=? AND timeframe=? AND direction=?
                 AND state IN ('LEG2', 'LEG3')
               ORDER BY updated_at DESC""",
            (symbol, LEVEL1_TIMEFRAME, reverse_dir),
        ).fetchall()

    if not rows:
        return False

    for row in rows:
        n_struct = dict(row)
        try:
            # L1 MACD 用品种级合约（symbol）而非具体合约（contract）
            macd_result = check_macd_trajectory(
                symbol, symbol, n_struct, LEVEL1_MACD_TIMEFRAME, reverse_dir, db
            )
            if macd_result.get("passed"):
                return True
        except Exception as e:
            logger.warning("反向结构检查异常: %s", e)
            continue

    return False


def _check_reverse_l2_structure(
    symbol: str,
    contract: str,
    direction: str,
    db: Database,
) -> bool:
    """检查 Level2 是否出现反向 N 型结构（小时线倒 N + 15min MACD 配合）。

    L2 反向结构比 L1（周线）更早出现，是趋势破坏的早期预警。
    触发条件：L2 上存在与当前反向的 N 型结构，且 15min MACD 轨迹验证通过。

    Args:
        symbol: 品种代码
        contract: 合约代码
        direction: 当前方向
        db: Database 实例

    Returns:
        True = L2 反向结构达触发条件
    """
    if direction == "NONE":
        return False

    reverse_dir = "SHORT" if direction == "LONG" else "LONG"

    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_n_structures
               WHERE symbol=? AND timeframe=? AND direction=?
                 AND state IN ('LEG2', 'LEG3')
               ORDER BY updated_at DESC""",
            (symbol, LEVEL2_TIMEFRAME, reverse_dir),
        ).fetchall()

    if not rows:
        return False

    for row in rows:
        n_struct = dict(row)
        try:
            macd_result = check_macd_trajectory(
                symbol,
                contract,
                n_struct,
                LEVEL2_MACD_TIMEFRAME,
                reverse_dir,
                db,
            )
            if macd_result.get("passed"):
                return True
        except Exception as e:
            logger.warning("L2反向结构检查异常: %s", e)
            continue

    return False


def _apply_score_reset(
    symbol: str,
    contract: str,
    direction: str,
    db: Database,
) -> bool:
    """评分重置检查主函数。

    组合五个重置条件，任一满足即重置评分：

    | # | 条件 | 层级 | 敏感度 |
    |---|------|------|--------|
    | 1 | L1 结构失效（周线 B 点突破） | L1 | 高（价格到位） |
    | 2 | L1 MACD 翻转（日线颜色翻转为反向） | L1 | **高（领先指标）** |
    | 3 | L2 趋势破坏（小时线 B 点突破 + 15min MACD 翻转） | L2 | 中 |
    | 4 | 反向 N 型结构（倒 N + MACD 配合达开仓条件） | L1 | 最高 |
    | 5 | 反向结构出现在 L2 级别（小时线倒 N + 15min MACD） | L2 | 中 |

    Args:
        symbol: 品种代码
        contract: 合约代码
        direction: 当前评估方向
        db: Database 实例

    Returns:
        True = 需要重置评分
    """
    if direction == "NONE":
        return False

    # ── 条件 1: L1 结构失效（周线 B 点被突破） ────────────
    if _check_structure_invalidation(symbol, contract, direction, db):
        logger.info(
            "评分重置: %s %s %s — L1结构失效(周线B点被突破)",
            symbol, contract, direction,
        )
        return True

    # ── 条件 2: L1 MACD 翻转（日线颜色与方向矛盾） ──────────
    if _check_macd_trend_break(
        symbol, contract, direction, db, LEVEL1_MACD_TIMEFRAME, n=8
    ):
        logger.info(
            "评分重置: %s %s %s — L1 MACD翻转(日线颜色反转)",
            symbol, contract, direction,
        )
        return True

    # ── 条件 3: L2 趋势破坏（小时线结构 + 15min MACD） ─────
    if _check_l2_trend_break(symbol, contract, direction, db):
        logger.info(
            "评分重置: %s %s %s — L2趋势破坏(小时线N型/MACD翻转)",
            symbol, contract, direction,
        )
        return True

    # ── 条件 4: L1 反向 N 型结构 ──────────────────────
    if _check_reverse_n_structure(symbol, contract, direction, db):
        logger.info(
            "评分重置: %s %s %s — 反向结构(L1)达开仓条件",
            symbol, contract, direction,
        )
        return True

    # ── 条件 5: L2 反向 N 型结构 ──────────────────────
    if _check_reverse_l2_structure(symbol, contract, direction, db):
        logger.info(
            "评分重置: %s %s %s — 反向结构(L2)达开仓条件",
            symbol, contract, direction,
        )
        return True

    return False


def _check_macd_trend_break(
    symbol: str,
    contract: str,
    direction: str,
    db: Database,
    macd_timeframe: str,
    n: int = 8,
) -> bool:
    """检查 MACD 主体颜色是否已翻转（趋势破坏的领先指标）。

    LONG 应主体为 RED（多头动量），若主体转为 BLUE → 趋势破坏
    SHORT 应主体为 BLUE（空头动量），若主体转为 RED → 趋势破坏

    此检查比价格突破 B 点更早触发，用于在趋势真正反转前重置评分。

    Args:
        symbol: 品种代码
        contract: 合约代码
        direction: 当前方向
        db: Database 实例
        macd_timeframe: MACD 周期（如 '1d', '15m'）
        n: 读取的柱体数量

    Returns:
        True = MACD 主体颜色与方向矛盾，趋势可能破坏
    """
    if direction not in ("LONG", "SHORT"):
        return False

    seq = check_color_sequence(symbol, contract, macd_timeframe, db, n=n)
    dominant = seq.get("dominant_color")
    if dominant is None or dominant not in (COLOR_RED, COLOR_BLUE):
        return False

    if direction == "LONG":
        # LONG 期望 RED（多头），若主体为 BLUE → 趋势翻转
        return dominant == COLOR_BLUE
    else:  # SHORT
        # SHORT 期望 BLUE（空头），若主体为 RED → 趋势翻转
        return dominant == COLOR_RED


def _check_l2_trend_break(
    symbol: str,
    contract: str,
    direction: str,
    db: Database,
) -> bool:
    """检查 Level2（小时线 N 型 + 15min MACD）趋势是否已破坏。

    比 L1 更敏感的趋势破坏信号，包含两类条件：

    条件 A: L2 N 型结构 B 点被突破（价格突破小时线极值）
    条件 B: L2 MACD 轨迹不再验证当前方向（15min MACD 颜色序列矛盾）

    Args:
        symbol: 品种代码
        contract: 合约代码
        direction: 当前方向
        db: Database 实例

    Returns:
        True = L2 趋势已破坏
    """
    # 条件 A: L2 N 型结构 B 点突破
    if _check_structure_invalidation(
        symbol, contract, direction, db, timeframe=LEVEL2_TIMEFRAME
    ):
        return True

    # 条件 B: L2 MACD 颜色翻转（15min 级别）
    if _check_macd_trend_break(
        symbol, contract, direction, db, LEVEL2_MACD_TIMEFRAME, n=12
    ):
        return True

    return False


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
    diagnostic: bool = False,
) -> SignalResult:
    """完整三级嵌套验证（离散3分硬条件制）。

    Level1 通过=1分，Level2+MACD通过=2分，Level3通过=3分。
    3分是硬性入场条件，缺一分都不行。加分项不计入基础分。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        db: Database 实例。
        diagnostic: 是否启用诊断模式（记录各级详细失败原因）。

    Returns:
        SignalResult 实例。diagnostic=True 时 result.diagnostic 包含诊断详情。
    """
    score = 0
    result = SignalResult(symbol=symbol, contract=contract, direction="NONE")
    dl1 = DiagnosticLevel(name="level1")
    dl2 = DiagnosticLevel(name="level2")
    dl3 = DiagnosticLevel(name="level3")

    # ═══════════════════════════════════════════════════
    # Level1: 周线N型定方向 + 日线MACD轨迹验证
    # ═══════════════════════════════════════════════════
    l1_struct = _get_active_n_structure(db, symbol, contract, LEVEL1_TIMEFRAME)

    if l1_struct is None or l1_struct.get("state") not in ("LEG2", "LEG3"):
        reason = (
            "无周线活跃N型结构"
            if l1_struct is None
            else f"状态{l1_struct['state']}不可用"
        )
        result.level1 = {
            "passed": False,
            "reason": reason,
            "n_structure": l1_struct,
        }
        if diagnostic:
            dl1.passed = False
            dl1.log(reason)
            if l1_struct:
                state = l1_struct.get("state", "UNKNOWN")
                dl1.log(f"周线N型状态={state}（需LEG2或LEG3）")
                dl1.set_data("l1_state", state)
            else:
                dl1.log("无任何活跃周线N型结构记录")
                dl1.set_data("l1_state", "NO_STRUCTURE")
        result.diagnostic = {d.name: d.to_dict() for d in [dl1, dl2, dl3]} if diagnostic else None
        result.overall_score = 0
        result.signal_type = "NONE"
        return result

    direction = l1_struct["direction"]
    result.direction = direction

    # Level1 MACD: 使用品种级合约名（symbol）而非具体合约（contract）
    # 原因：日线 MACD 数据以品种级存储（如 symbol=EB, contract=EB），
    # 从 2019 年起连续完整。具体合约级（如 EB2609）的 MACD 仅覆盖其自身存续期，
    # 可能不覆盖 N 型结构 Point A 的时间窗口，导致"转折前无MACD数据"误报。
    # 参见: docs/macd-data-analysis.md
    l1_macd = check_macd_trajectory(
        symbol, symbol, l1_struct, LEVEL1_MACD_TIMEFRAME, direction, db
    )
    l1_macd_passed = l1_macd.get("passed", False)

    result.level1 = {
        "passed": l1_macd_passed,
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

    if not l1_macd_passed:
        reason = f"周线MACD轨迹未验证: {l1_macd.get('description', '')}"
        result.level1["reason"] = reason
        if diagnostic:
            dl1.passed = False
            dl1.log(reason)
            dl1.log(f"MACD腿1={l1_macd['leg1']['passed']}({l1_macd['leg1']['detail']})")
            dl1.log(f"MACD腿2={l1_macd['leg2']['passed']}({l1_macd['leg2']['detail']})")
            dl1.log(f"MACD腿3={l1_macd['leg3']['passed']}({l1_macd['leg3']['detail']})")
            dl1.set_data("macd_passed_leg1", l1_macd["leg1"]["passed"])
            dl1.set_data("macd_passed_leg2", l1_macd["leg2"]["passed"])
            dl1.set_data("macd_passed_leg3", l1_macd["leg3"]["passed"])
            dl1.set_data("macd_lower_tf", l1_macd.get("lower_tf", "1d"))
        result.diagnostic = {d.name: d.to_dict() for d in [dl1, dl2, dl3]} if diagnostic else None
        result.overall_score = 0
        result.signal_type = "NONE"
        return result

    score = 1  # Level1 N型+MACD双通过 → 1分

    if diagnostic:
        dl1.passed = True
        dl1.log(f"周线{direction}N型({l1_struct['state']}) + 日线MACD轨迹验证通过")
        dl1.set_data("direction", direction)
        dl1.set_data("l1_state", l1_struct["state"])

    # ═══════════════════════════════════════════════════
    # Level2: 小时线N型确认 + 15分钟MACD轨迹验证（硬条件）
    # ═══════════════════════════════════════════════════
    l2_struct = _get_active_n_structure(db, symbol, contract, LEVEL2_TIMEFRAME)

    l2_result: Dict[str, Any] = {"passed": False}
    l2_macd_passed = False

    if l2_struct and l2_struct.get("direction") == direction:
        if diagnostic:
            dl2.log(f"小时线N型可用: state={l2_struct['state']}, direction={l2_struct['direction']}")
            dl2.set_data("l2_state", l2_struct["state"])
            dl2.set_data("l2_direction", l2_struct["direction"])

        l2_macd = check_macd_trajectory(
            symbol, contract, l2_struct, LEVEL2_MACD_TIMEFRAME, direction, db
        )
        l2_macd_passed = l2_macd.get("passed", False)

        if diagnostic:
            dl2.log(f"15m MACD轨迹: {'通过' if l2_macd_passed else '未通过'}")
            dl2.log(f"  leg1={l2_macd['leg1']['passed']}({l2_macd['leg1']['detail']})")
            dl2.log(f"  leg2={l2_macd['leg2']['passed']}({l2_macd['leg2']['detail']})")
            dl2.log(f"  leg3={l2_macd['leg3']['passed']}({l2_macd['leg3']['detail']})")
            dl2.set_data("macd_passed_leg1", l2_macd["leg1"]["passed"])
            dl2.set_data("macd_passed_leg2", l2_macd["leg2"]["passed"])
            dl2.set_data("macd_passed_leg3", l2_macd["leg3"]["passed"])

        if l2_macd_passed:
            score = 2  # MACD通过 → Level2完整通过，+1分

        l2_result = {
            "passed": l2_macd_passed,
            "direction": direction,
            "state": l2_struct["state"],
            "n_structure": {
                "point_a_price": l2_struct["point_a_price"],
                "point_b_price": l2_struct["point_b_price"],
                "point_c_price": l2_struct.get("point_c_price"),
            },
            "macd_trajectory": l2_macd,
            "macd_passed": l2_macd_passed,
            "description": _level2_description(
                direction, l2_struct["state"], l2_macd
            ),
        }
    elif l2_struct:
        l2_result = {
            "passed": False,
            "reason": f"小时线方向{l2_struct.get('direction')}不匹配周线{direction}",
        }
        if diagnostic:
            dl2.passed = False
            dl2.log(f"小时线方向{l2_struct.get('direction')}不匹配周线{direction}")
            dl2.set_data("l2_direction", l2_struct.get("direction"))
            dl2.set_data("expected_direction", direction)
    else:
        l2_result = {
            "passed": False,
            "reason": "小时线无活跃N型结构",
        }
        if diagnostic:
            dl2.passed = False
            dl2.log("小时线无活跃N型结构")
            dl2.set_data("l2_state", "NO_STRUCTURE")

    result.level2 = l2_result

    if diagnostic:
        dl2.passed = l2_macd_passed
        if l2_macd_passed:
            dl2.log(f"Level2通过: 小时{l2_struct['state']} + 15m MACD验证通过 → score=2")

    if score < 2:
        # 不足2分 → NONE（降级路径已删除）
        if diagnostic:
            result.diagnostic = {d.name: d.to_dict() for d in [dl1, dl2, dl3]} if diagnostic else None
        result.overall_score = score
        result.signal_type = "NONE"
        return result

    # ═══════════════════════════════════════════════════
    # Level3: 15分钟N型入场 + 3分钟MACD稳定 + 突破 → 3分
    # ═══════════════════════════════════════════════════
    l3_struct = _get_active_n_structure(db, symbol, contract, LEVEL3_TIMEFRAME)

    l3_result: Dict[str, Any] = {"passed": False}

    if l3_struct and l3_struct.get("direction") == direction:
        if diagnostic:
            dl3.log(f"15m N型可用: state={l3_struct['state']}, direction={direction}")
            dl3.set_data("l3_state", l3_struct["state"])
            dl3.set_data("l3_direction", direction)
            dl3.set_data("point_B", l3_struct.get("point_b_price"))
            dl3.set_data("point_C", l3_struct.get("point_c_price"))

        stability = check_3m_stability(symbol, contract, direction, db)
        breakout = check_realtime_breakout(symbol, contract, l3_struct, db)

        if diagnostic:
            stable = stability.get("stable", False)
            stats = stability.get("stats", {})
            dl3.log(f"3m稳定: {'✅' if stable else '❌'}")
            dl3.log(f"  数据bars={stats.get('total', '?')}, 切换={stats.get('switch_count', '?')}/{stats.get('max_switches', '?')}")
            dl3.log(f"  主体颜色={stats.get('dominant_color', '?')}, 期望={stats.get('expected_color', '?')}")
            dl3.log(f"  switch_ok={stats.get('switch_ok')}, color_ok={stats.get('color_ok')}")
            dl3.set_data("stability_passed", stable)
            dl3.set_data("3m_total_bars", stats.get("total"))
            dl3.set_data("3m_switch_count", stats.get("switch_count"))
            dl3.set_data("3m_dominant_color", stats.get("dominant_color"))
            dl3.set_data("3m_timeframe", stats.get("timeframe"))

            triggered = breakout.get("triggered", False)
            dl3.log(f"15m突破B点: {'✅' if triggered else '❌'}")
            dl3.log(f"  当前价={breakout.get('trigger_price', '?')}, B点={breakout.get('breakout_price', '?')}")
            dl3.log(f"  detail={breakout.get('detail', '?')}")
            dl3.set_data("breakout_triggered", triggered)
            dl3.set_data("current_price", breakout.get("trigger_price"))
            dl3.set_data("B_price", breakout.get("breakout_price"))

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
            score = 3  # Level3 通过 → 3分，满足入场条件
            result.entry_price = breakout.get("trigger_price")
            sl, tp = _calculate_sl_tp(result, l3_struct, l1_struct)
            result.stop_loss = sl
            result.take_profit = tp
            if diagnostic:
                dl3.passed = True
                dl3.log(f"Level3全部通过 → score=3 (ENTRY)")
                dl3.log(f"入场价={result.entry_price}, SL={sl}, TP={tp}")
        elif diagnostic:
            if not stability.get("stable"):
                dl3.log("⚠ 3m稳定性未通过 → L3阻塞")
            if not breakout.get("triggered"):
                dl3.log("⚠ 15m突破未触发 → L3阻塞")
    else:
        l3_result = {
            "passed": False,
            "reason": "15分钟无活跃N型或方向不一致",
        }
        if diagnostic:
            dl3.passed = False
            if l3_struct:
                dl3.log(f"15m N型方向{l3_struct.get('direction')}不匹配{direction}")
                dl3.set_data("l3_direction", l3_struct.get("direction"))
                dl3.set_data("expected_direction", direction)
            else:
                dl3.log("15分钟无活跃N型结构")
                dl3.set_data("l3_state", "NO_STRUCTURE")

    result.level3 = l3_result

    # ═══════════════════════════════════════════════════
    # 加分项（单独计算，不影响入场条件，用于4分加仓判定）
    # ═══════════════════════════════════════════════════
    result.bonus = _check_bonus(symbol, contract, direction, db)
    bonus_total = sum(b["score"] for b in result.bonus if b["passed"])

    # ═══════════════════════════════════════════════════
    # 评分重置检查（结构性失效覆盖）
    # 若价格已突破B点或形成反向N型，清除当前评分
    # ═══════════════════════════════════════════════════
    if score >= 1 and direction != "NONE":
        if _apply_score_reset(symbol, contract, direction, db):
            if diagnostic:
                dl3.log("评分重置触发 — 所有评分清零")
                dl3.set_data("score_reset", True)
                result.diagnostic = {d.name: d.to_dict() for d in [dl1, dl2, dl3]}
            result.overall_score = 0
            result.signal_type = "NONE"
            return result

    # ═══════════════════════════════════════════════════
    # 最终评分判定（P0指令：3分硬条件入场制 — Cycle #59）
    #
    # 覆盖 Cycle #35 的梯度策略决策（2分入场）。根据原始笔记要求：
    #   - 3分是硬性入场条件——缺一分都不行
    #   - 加分单独计算，不能用来补齐基础3分中的缺分
    #
    # score=3(L1+L2+L3+MACD硬) → ENTRY
    # score=4(+加分项)         → ADD_POSITION
    # score<3                  → NONE
    # ═══════════════════════════════════════════════════
    if score >= 3 and bonus_total > 0:
        result.overall_score = 4
        result.signal_type = "ADD_POSITION"
    elif score >= 3:
        result.overall_score = score
        result.signal_type = "ENTRY"
    else:
        result.overall_score = score
        result.signal_type = "NONE"

    if diagnostic:
        result.diagnostic = {d.name: d.to_dict() for d in [dl1, dl2, dl3]}

    return result


def scan_all_contracts(db: Database, diagnostic: bool = False) -> List[SignalResult]:
    """扫描所有主力合约，返回按 overall_score 降序排列的结果。

    Args:
        db: Database 实例。
        diagnostic: 是否启用诊断模式。

    Returns:
        信号结果列表，按评分降序。
    """
    contracts = _get_all_main_contracts(db)
    results: List[SignalResult] = []

    for mc in contracts:
        symbol = mc["symbol"]
        contract_code = mc["contract_code"]
        try:
            sr = evaluate(symbol, contract_code, db, diagnostic=diagnostic)
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
