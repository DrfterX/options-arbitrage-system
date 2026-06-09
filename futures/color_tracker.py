"""
MACD两色序列追踪器。

提供颜色序列统计、MACD轨迹验证、3分钟稳定性检查。
所有DB访问通过 ``db: Database`` 参数完成。
"""

import logging
from collections import Counter
from typing import Any, Dict, List, Optional

from core.db import Database
from config.settings import (
    COLOR_RED,
    COLOR_BLUE,
    LEVEL3_STABILITY_TIMEFRAME,
    LEVEL3_STABILITY_WINDOW,
    LEVEL3_STABILITY_MAX_SWITCHES,
    TRANSITION_WINDOW_BEFORE,
    TRANSITION_WINDOW_AFTER,
)

logger = logging.getLogger(__name__)


# ─── DB 内部辅助 ─────────────────────────────────────────────


def _get_recent_macd_colors(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    n: int = 10,
) -> List[str]:
    """获取最近 n 根 MACD 的颜色序列（时间升序）。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT color FROM futures_macd
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp DESC LIMIT ?""",
            (symbol, contract, timeframe, n),
        ).fetchall()
    return [r["color"] for r in reversed(rows)]


def _get_macd_in_range(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    start_ts: int,
    end_ts: int,
) -> List[Dict[str, Any]]:
    """获取时间范围内的 MACD 数据（时间升序）。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_macd
               WHERE symbol=? AND contract=? AND timeframe=?
                 AND timestamp>=? AND timestamp<=?
               ORDER BY timestamp ASC""",
            (symbol, contract, timeframe, start_ts, end_ts),
        ).fetchall()
    return [dict(r) for r in rows]


# ─── 颜色序列统计 ────────────────────────────────────────────


def check_color_sequence(
    symbol: str,
    contract: str,
    timeframe: str,
    db: Database,
    n: int = 10,
) -> Dict[str, Any]:
    """返回最近 n 根 MACD 的颜色统计分析。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        timeframe: 周期。
        db: Database 实例。
        n: 读取的柱体数量。

    Returns:
        字典含 colors/dominant_color/switch_count/total。
    """
    colors = _get_recent_macd_colors(db, symbol, contract, timeframe, n=n)

    if not colors:
        return {
            "colors": [],
            "dominant_color": None,
            "switch_count": 0,
            "total": 0,
        }

    valid = [c for c in colors if c in (COLOR_RED, COLOR_BLUE)]
    if not valid:
        return {
            "colors": colors,
            "dominant_color": None,
            "switch_count": 0,
            "total": 0,
        }

    counter = Counter(valid)
    dominant_color = counter.most_common(1)[0][0]

    switch_count = 0
    for i in range(1, len(valid)):
        if valid[i] != valid[i - 1]:
            switch_count += 1

    return {
        "colors": colors,
        "dominant_color": dominant_color,
        "switch_count": switch_count,
        "total": len(valid),
    }


# ─── 内部辅助函数 ────────────────────────────────────────────


def _dominant_color(macd_rows: List[Dict[str, Any]]) -> Optional[str]:
    """取 MACD 数据行中的主体颜色。"""
    colors = [r["color"] for r in macd_rows if r["color"] in (COLOR_RED, COLOR_BLUE)]
    if not colors:
        return None
    return Counter(colors).most_common(1)[0][0]


def _has_color(macd_rows: List[Dict[str, Any]], target_color: str) -> bool:
    """MACD 数据中是否至少有一根目标颜色的柱体。"""
    return any(r["color"] == target_color for r in macd_rows)


def _check_weakening(
    macd_rows: List[Dict[str, Any]], direction: str
) -> tuple:
    """检查柱体是否在减弱（第三笔验证）。

    做空(SHORT): 红柱减弱或被蓝柱取代。
    做多(LONG):  蓝柱减弱或被红柱取代。

    Returns:
        (passed: bool, detail: str)
    """
    if not macd_rows:
        return False, "无MACD数据"

    colors = [r["color"] for r in macd_rows if r["color"] in (COLOR_RED, COLOR_BLUE)]
    if not colors:
        return False, "无有效颜色"

    dominant = Counter(colors).most_common(1)[0][0]

    if direction == "SHORT":
        if dominant == COLOR_BLUE:
            return True, "已变蓝(空头确认)"
        red_bars = [
            r
            for r in macd_rows
            if r["color"] == COLOR_RED and r.get("histogram") is not None
        ]
        if len(red_bars) < 3:
            return True, "红柱数少(可接受)"
        mid = len(red_bars) // 2
        first_avg = sum(abs(r["histogram"]) for r in red_bars[:mid]) / mid
        second_avg = (
            sum(abs(r["histogram"]) for r in red_bars[mid:]) / len(red_bars[mid:])
            if red_bars[mid:]
            else 0
        )
        if second_avg < first_avg * 0.85:
            return True, f"红柱减弱({first_avg:.1f}→{second_avg:.1f})"
        return False, f"红柱未减弱({first_avg:.1f}→{second_avg:.1f})"

    else:  # LONG
        if dominant == COLOR_RED:
            return True, "已变红(多头确认)"
        blue_bars = [
            r
            for r in macd_rows
            if r["color"] == COLOR_BLUE and r.get("histogram") is not None
        ]
        if len(blue_bars) < 3:
            return True, "蓝柱数少(可接受)"
        mid = len(blue_bars) // 2
        first_avg = sum(abs(r["histogram"]) for r in blue_bars[:mid]) / mid
        second_avg = (
            sum(abs(r["histogram"]) for r in blue_bars[mid:]) / len(blue_bars[mid:])
            if blue_bars[mid:]
            else 0
        )
        if second_avg < first_avg * 0.85:
            return True, f"蓝柱减弱({first_avg:.1f}→{second_avg:.1f})"
        return False, f"蓝柱未减弱({first_avg:.1f}→{second_avg:.1f})"


def _trend_from_histogram(
    macd_rows: List[Dict[str, Any]], direction: str
) -> Optional[str]:
    """基于 histogram 判断趋势方向（比MACD线快数倍）。"""
    if not macd_rows:
        return None
    half = len(macd_rows) // 2
    second_half = macd_rows[half:]
    positive = sum(1 for r in second_half if r.get("histogram", 0) > 0)
    negative = len(second_half) - positive
    if positive > negative * 2:
        return "RISING"
    elif negative > positive * 2:
        return "FALLING"
    return "MIXED"


def _check_pivot_transition(
    macd_before: List[Dict[str, Any]],
    macd_after: List[Dict[str, Any]],
    from_color: str,
    to_color: str,
    leg_label: str,
) -> tuple:
    """检查 MACD 在转折点处的颜色过渡。

    放宽规则：不要求 MACD 线翻零，但要求 histogram 方向已反转。

    Args:
        macd_before: 转折点前MACD数据。
        macd_after: 转折点后MACD数据。
        from_color: 过渡前颜色。
        to_color: 过渡后颜色。
        leg_label: 腿名称用于日志。

    Returns:
        (passed: bool, detail: str)
    """
    dominant_before = _dominant_color(macd_before)
    has_to_after = _has_color(macd_after, to_color)

    if dominant_before is None:
        return False, f"{leg_label}: 转折前无MACD数据"

    if dominant_before != from_color:
        return False, f"{leg_label}: 转折前主体{dominant_before}，期望{from_color}"

    if has_to_after:
        before_counts = Counter(
            r["color"] for r in macd_before if r["color"] in (COLOR_RED, COLOR_BLUE)
        )
        after_counts = Counter(
            r["color"] for r in macd_after if r["color"] in (COLOR_RED, COLOR_BLUE)
        )
        return True, (
            f"{leg_label}: {from_color}({before_counts.get(from_color, 0)}根)"
            f"→{to_color}({after_counts.get(to_color, 0)}根)"
        )

    if to_color == COLOR_BLUE:  # SHORT → 期望动量向下
        after_trend = _trend_from_histogram(macd_after, "SHORT")
        if after_trend == "FALLING":
            return True, f"{leg_label}: MACD仍{from_color},但histogram已转负(动量向下)"
    else:  # LONG → 期望动量向上
        after_trend = _trend_from_histogram(macd_after, "LONG")
        if after_trend == "RISING":
            return True, f"{leg_label}: MACD仍{from_color},但histogram已转正(动量向上)"

    after_hist_sum = (
        sum(r.get("histogram", 0) for r in macd_after[-3:])
        / max(len(macd_after[-3:]), 1)
    )
    return False, (
        f"{leg_label}: MACD仍{from_color}且histogram未反转"
        f"(最近3根均值{after_hist_sum:.2f})"
    )


# ─── 核心验证 ────────────────────────────────────────────────


def check_macd_trajectory(
    symbol: str,
    contract: str,
    n_structure: Dict[str, Any],
    lower_tf: str,
    direction: str,
    db: Database,
) -> Dict[str, Any]:
    """检查下级MACD颜色轨迹是否验证了N型结构的三笔。

    核心逻辑：
      做空(倒N): A峰→BLUE出现 | B谷→RED出现 | C第二峰→RED减弱或变BLUE
      做多(正N): A谷→RED出现 | B峰→BLUE出现 | C第二谷→BLUE减弱或变RED

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        n_structure: 上级N型结构。
        lower_tf: 下级MACD周期（如 '1d', '15m'）。
        direction: 'LONG' / 'SHORT'。
        db: Database 实例。

    Returns:
        轨迹验证结果字典。
    """
    a_time = n_structure.get("point_a_time")
    b_time = n_structure.get("point_b_time")
    c_time = n_structure.get("point_c_time")

    if not all([a_time, b_time, direction]):
        return {
            "passed": False,
            "leg1": {"passed": False, "detail": "缺A/B时间或方向"},
            "leg2": {"passed": False, "detail": ""},
            "leg3": {"passed": False, "detail": ""},
            "description": "N型结构数据不完整",
        }

    if direction == "SHORT":
        leg1_from, leg1_to = COLOR_RED, COLOR_BLUE
        leg2_from, leg2_to = COLOR_BLUE, COLOR_RED
        third_color_if_weaker = COLOR_RED
    else:
        leg1_from, leg1_to = COLOR_BLUE, COLOR_RED
        leg2_from, leg2_to = COLOR_RED, COLOR_BLUE
        third_color_if_weaker = COLOR_BLUE

    ab_gap = abs(b_time - a_time) if b_time and a_time else 86400 * 30
    bc_gap = abs(c_time - b_time) if c_time and b_time else 86400 * 15

    window_a = min(ab_gap // 3, 86400 * 30)
    window_b = min(min(ab_gap, bc_gap if c_time else ab_gap) // 3, 86400 * 15)
    window_c = min(bc_gap // 3 if c_time else 86400 * 30, 86400 * 30)

    min_window = {
        "3m": 600,
        "15m": 3600,
        "1h": 14400,
        "1d": 259200,
        "1w": 1209600,
    }.get(lower_tf, 86400)
    window_a = max(window_a, min_window)
    window_b = max(window_b, min_window)
    window_c = max(window_c, min_window)

    # 腿1: A转折点
    macd_before_a = _get_macd_in_range(
        db, symbol, contract, lower_tf, a_time - window_a, a_time
    )
    macd_after_a = _get_macd_in_range(
        db, symbol, contract, lower_tf, a_time, a_time + window_a
    )
    macd_before_a = (
        macd_before_a[-TRANSITION_WINDOW_BEFORE:]
        if len(macd_before_a) > TRANSITION_WINDOW_BEFORE
        else macd_before_a
    )
    macd_after_a = (
        macd_after_a[:TRANSITION_WINDOW_AFTER]
        if len(macd_after_a) > TRANSITION_WINDOW_AFTER
        else macd_after_a
    )
    leg1_passed, leg1_detail = _check_pivot_transition(
        macd_before_a, macd_after_a, leg1_from, leg1_to, f"A点({direction})"
    )

    # 腿2: B转折点
    macd_before_b = _get_macd_in_range(
        db, symbol, contract, lower_tf, b_time - window_b, b_time
    )
    macd_after_b = _get_macd_in_range(
        db, symbol, contract, lower_tf, b_time, b_time + window_b
    )
    macd_before_b = (
        macd_before_b[-TRANSITION_WINDOW_BEFORE:]
        if len(macd_before_b) > TRANSITION_WINDOW_BEFORE
        else macd_before_b
    )
    macd_after_b = (
        macd_after_b[:TRANSITION_WINDOW_AFTER]
        if len(macd_after_b) > TRANSITION_WINDOW_AFTER
        else macd_after_b
    )
    leg2_passed, leg2_detail = _check_pivot_transition(
        macd_before_b, macd_after_b, leg2_from, leg2_to, f"B点({direction})"
    )

    # 腿3: C点后弱化检查
    if c_time:
        macd_after_c = _get_macd_in_range(
            db, symbol, contract, lower_tf,
            c_time - min_window, c_time + window_c,
        )
        leg3_passed, leg3_detail = _check_weakening(macd_after_c, direction)
    else:
        recent = _get_recent_macd_colors(db, symbol, contract, lower_tf, n=10)
        if recent:
            # 获取最新的MACD数据行用于弱化检查
            now_ts = 9999999999
            hist_rows = _get_macd_in_range(
                db, symbol, contract, lower_tf, 0, now_ts,
            )
            hist_rows = hist_rows[-20:] if len(hist_rows) > 20 else hist_rows
            leg3_passed, leg3_detail = _check_weakening(hist_rows, direction)
        else:
            leg3_passed, leg3_detail = False, "C未形成且无MACD数据"

    overall = leg1_passed and leg2_passed

    parts = []
    if leg1_passed:
        parts.append(f"腿1{leg1_detail}")
    else:
        parts.append(f"腿1❌{leg1_detail}")
    if leg2_passed:
        parts.append(f"腿2{leg2_detail}")
    else:
        parts.append(f"腿2❌{leg2_detail}")
    if leg3_passed:
        parts.append(f"腿3{leg3_detail}")

    description = " | ".join(parts) if parts else "MACD轨迹检查异常"

    return {
        "passed": overall,
        "leg1": {"passed": leg1_passed, "detail": leg1_detail},
        "leg2": {"passed": leg2_passed, "detail": leg2_detail},
        "leg3": {"passed": leg3_passed, "detail": leg3_detail},
        "description": description,
        "lower_tf": lower_tf,
    }


def check_3m_stability(
    symbol: str,
    contract: str,
    direction: str,
    db: Database,
) -> Dict[str, Any]:
    """检查 3分钟 MACD 颜色稳定性（Level3 前置条件）。

    - 最近 LEVEL3_STABILITY_WINDOW 根的切换次数 ≤ LEVEL3_STABILITY_MAX_SWITCHES
    - 主体颜色与 direction 一致（做空→BLUE为主，做多→RED为主）

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        direction: 'LONG' 或 'SHORT'。
        db: Database 实例。

    Returns:
        稳定性检查结果字典。
    """
    if direction not in ("LONG", "SHORT"):
        return {
            "stable": False,
            "stats": {},
            "reason": f"无效方向: {direction}",
        }

    expected_color = COLOR_RED if direction == "LONG" else COLOR_BLUE
    seq_result = check_color_sequence(
        symbol, contract, LEVEL3_STABILITY_TIMEFRAME, db, n=LEVEL3_STABILITY_WINDOW
    )

    switch_count = seq_result["switch_count"]
    dominant = seq_result["dominant_color"]
    total = seq_result["total"]

    switch_ok = switch_count <= LEVEL3_STABILITY_MAX_SWITCHES
    color_ok = dominant == expected_color

    stable = switch_ok and color_ok

    reason = None
    if not stable:
        if not switch_ok:
            reason = (
                f"切换{switch_count}次(限{LEVEL3_STABILITY_MAX_SWITCHES})"
            )
        else:
            reason = f"主体{dominant},需{expected_color}"

    return {
        "stable": stable,
        "stats": {
            "timeframe": LEVEL3_STABILITY_TIMEFRAME,
            "window": LEVEL3_STABILITY_WINDOW,
            "total": total,
            "dominant_color": dominant,
            "expected_color": expected_color,
            "switch_count": switch_count,
            "max_switches": LEVEL3_STABILITY_MAX_SWITCHES,
            "switch_ok": switch_ok,
            "color_ok": color_ok,
            "colors": seq_result["colors"],
        },
        "reason": reason,
    }
