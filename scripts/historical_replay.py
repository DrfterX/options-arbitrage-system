"""
N型系统历史回放验证 — 月频扫描，模拟 evaluate() 全过程。

用法:
    uv run python scripts/historical_replay.py

输出:
    data/historical_replay/ 目录下的 JSON 结果
"""

import json
import logging
import os
import sqlite3
import sys
import time as time_module
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_ROOT / "trading_system.db")
OUTPUT_DIR = PROJECT_ROOT / "data" / "historical_replay"
TARGET_SYMBOLS = ["RB", "Y", "P", "EB", "L", "PG", "TA"]

# ─── 配色常量（从 macd.py 复刻） ──────────────────────────
COLOR_BLUE = "蓝"
COLOR_RED = "红"

# ─── 数据类 ────────────────────────────────────────────────

class ReplayResult:
    def __init__(self):
        self.symbol: str = ""
        self.month: str = ""       # "2024-01"
        self.timestamp: int = 0    # window end timestamp
        self.l1_passed: bool = False
        self.l1_reason: str = ""
        self.l2_passed: bool = False
        self.l3_passed: bool = False
        self.score: int = 0        # 0, 1, 2, 3
        self.direction: str = "NONE"
        self.l1_direction: str = ""
        self.l1_state: str = ""
        self.l2_state: str = ""
        self.l3_state: str = ""

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "month": self.month,
            "l1_passed": self.l1_passed,
            "l1_reason": self.l1_reason,
            "l1_direction": self.l1_direction,
            "l1_state": self.l1_state,
            "l2_passed": self.l2_passed,
            "l2_state": self.l2_state,
            "l3_passed": self.l3_passed,
            "l3_state": self.l3_state,
            "score": self.score,
            "direction": self.direction,
        }


# ═══════════════════════════════════════════════════════════
# 数据加载
# ═══════════════════════════════════════════════════════════

def load_klines_upto(db_path: str, symbol: str, tf: str, upto_ts: int) -> List[dict]:
    """加载截至 upto_ts 的 K 线数据（按时间升序）。"""
    rows = []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """SELECT timestamp, open, high, low, close, volume
               FROM futures_klines
               WHERE symbol=? AND timeframe=? AND timestamp <= ?
               ORDER BY timestamp ASC""",
            (symbol, tf, upto_ts),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def load_n_structures_upto(db_path: str, symbol: str, tf: str, upto_ts: int) -> List[dict]:
    """加载截至 upto_ts 的 N 型结构（按 updated_at 降序）。"""
    rows = []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """SELECT * FROM futures_n_structures
               WHERE symbol=? AND timeframe=? AND updated_at <= ?
               ORDER BY updated_at DESC""",
            (symbol, tf, upto_ts),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════
# MACD 计算（轻量版）
# ═══════════════════════════════════════════════════════════

def ema(values: List[float], period: int) -> float:
    if not values:
        return 0.0
    k = 2.0 / (period + 1)
    result = values[0]
    for v in values[1:]:
        result = v * k + result * (1 - k)
    return result


def compute_macd(klines: List[dict], fast: int = 12, slow: int = 26, signal_period: int = 9) -> List[dict]:
    """计算 MACD 系列。

    Returns:
        [{"dif": float, "dea": float, "macd": float, "color": str}, ...]
    """
    closes = [k["close"] for k in klines]
    if len(closes) < slow + signal_period:
        return []

    # EMA
    ema12 = []
    k12 = 2.0 / (fast + 1)
    e12 = closes[0]
    for c in closes:
        e12 = c * k12 + e12 * (1 - k12)
        ema12.append(e12)

    ema26 = []
    k26 = 2.0 / (slow + 1)
    e26 = closes[0]
    for c in closes:
        e26 = c * k26 + e26 * (1 - k26)
        ema26.append(e26)

    dif = [ema12[i] - ema26[i] for i in range(len(closes))]

    # DEA = EMA(DIF, 9)
    k_sig = 2.0 / (signal_period + 1)
    dea = []
    e_sig = dif[slow - 1]
    for i in range(slow - 1, len(dif)):
        e_sig = dif[i] * k_sig + e_sig * (1 - k_sig)
        dea.append(e_sig)
    # Pad front
    dea = [dea[0]] * (slow - 1) + dea

    macd = [2 * (dif[i] - dea[i]) for i in range(len(dif))]
    colors = ["红" if dif[i] > dea[i] else "蓝" for i in range(len(dif))]

    return [{"dif": dif[i], "dea": dea[i], "macd": macd[i], "color": colors[i]} for i in range(len(dif))]


# ═══════════════════════════════════════════════════════════
# 极值点检测（复刻 n_paper_backtest）
# ═══════════════════════════════════════════════════════════

def detect_swing_points(klines: List[dict], wn: int = 5) -> List[dict]:
    if len(klines) < wn * 2 + 1:
        return []
    pts = []
    n = len(klines)
    for i in range(wn, n - wn + 1):
        c = klines[i]
        lh = max(k["high"] for k in klines[i - wn:i])
        ll = min(k["low"] for k in klines[i - wn:i])
        rb = klines[i + 1:i + wn + 1]
        rh = max(k["high"] for k in rb)
        rl = min(k["low"] for k in rb)
        same_peak = False

        if c["high"] > lh and c["high"] >= rh:
            if not pts or pts[-1]["type"] != "PEAK":
                pts.append({"ts": c["timestamp"], "price": c["high"], "type": "PEAK"})
            elif c["high"] > pts[-1]["price"]:
                pts[-1]["price"] = c["high"]
                pts[-1]["ts"] = c["timestamp"]
            same_peak = True

        if c["low"] < ll and c["low"] <= rl:
            if not pts:
                if not same_peak:
                    pts.append({"ts": c["timestamp"], "price": c["low"], "type": "TROUGH"})
            elif pts[-1]["type"] == "TROUGH":
                if c["low"] < pts[-1]["price"]:
                    pts[-1]["price"] = c["low"]
                    pts[-1]["ts"] = c["timestamp"]
            elif not same_peak:
                pts.append({"ts": c["timestamp"], "price": c["low"], "type": "TROUGH"})
    return pts


def merge_same(pts: List[dict]) -> List[dict]:
    out = []
    for p in pts:
        if out and p["type"] == out[-1]["type"]:
            prev = out[-1]
            if p["type"] == "TROUGH":
                if p["price"] < prev["price"]:
                    out[-1] = p
            elif p["price"] > prev["price"]:
                out[-1] = p
        else:
            out.append(p)
    return out


def detect_n_structure(klines: List[dict], lookback: int = 40, wn: int = 5) -> Optional[dict]:
    """在 1d 或 1w K 线上检测最新 N 型结构。

    Returns:
        {"direction": str, "state": str, "point_a/b/c_price": float, "point_a/b/c_time": int}
        或 None
    """
    if len(klines) < wn * 2 + 2:
        return None
    pts = detect_swing_points(klines[-lookback:], wn)
    if len(pts) < 3:
        return None
    filtered = merge_same(pts)
    if len(filtered) < 3:
        return None

    best = None
    n = len(filtered)
    for start in range(n - 3, max(n - 5, -1), -1):
        trio = filtered[start:start + 3]
        tt = [p["type"] for p in trio]
        if not (tt[0] != tt[1] and tt[1] != tt[2]):
            continue
        pa, pb, pc = trio
        dr = "LONG" if pb["price"] > pa["price"] else "SHORT"
        if dr == "LONG" and pc["price"] <= pa["price"]:
            continue
        if dr == "SHORT" and pc["price"] >= pa["price"]:
            continue
        best = (pa, pb, pc)
        break

    if best is None:
        return None

    pa, pb, pc = best
    dr = "LONG" if pb["price"] > pa["price"] else "SHORT"

    # 判断 state: LEG2 (只有A-B-C) 或 LEG3 (有进一步延展)
    # 简化: 价格超过 C 算 LEG3（对比 klines[-1].close）
    close = klines[-1]["close"]
    is_leg3 = (dr == "LONG" and close > pc["price"]) or (dr == "SHORT" and close < pc["price"])

    return {
        "direction": dr,
        "state": "LEG3" if is_leg3 else "LEG2",
        "point_a_price": pa["price"],
        "point_b_price": pb["price"],
        "point_c_price": pc["price"],
        "point_a_time": pa["ts"],
        "point_b_time": pb["ts"],
        "point_c_time": pc["ts"],
    }


# ═══════════════════════════════════════════════════════════
# MACD 颜色轨迹验证（简化版）
# ═══════════════════════════════════════════════════════════

# MACD 轨迹模式常量
PATTERN_BULLISH = "红→绿→红→减弱"
PATTERN_BEARISH = "绿→红→绿→减弱"
PATTERN_RED = "红"
PATTERN_BLUE = "蓝"
PATTERN_PARALLEL = "红平行"
PATTERN_RED_ENHANCE = "红增强"
PATTERN_PARALLEL_UP = "红平行上升"
PATTERN_PARALLEL_DOWN = "蓝平行下降"
PATTERN_BLUE_ENHANCE = "蓝增强"


def check_color_sequence(macd_list: List[dict], n_struct: dict, direction: str) -> dict:
    """检查 MACD 颜色序列是否配合 N 型方向。

    简版复刻 color_tracker.check_color_sequence 的核心逻辑。
    """
    if len(macd_list) < 20:
        return {"passed": False, "description": "MACD数据不足"}

    last = macd_list[-1]
    last_color = last["color"]
    last_dif = last["dif"]

    # 统计最近一段时间的颜色分布
    recent = macd_list[-20:]
    red_count = sum(1 for m in recent if m["color"] == "红")
    blue_count = 20 - red_count

    if direction == "LONG":
        # 多头方向：期望近期 MACD 以红色为主
        if red_count >= 14:  # 70%+
            return {"passed": True, "description": f"多头MACD配合(红{red_count}/20)"}
        elif red_count >= 10 and last_color == "红" and last_dif > 0:
            return {"passed": True, "description": f"多头MACD偏多(红{red_count}/20)"}
        else:
            return {"passed": False, "description": f"多头MACD不配合(红{red_count}/20, last={last_color})"}
    else:
        # 空头方向：期望近期 MACD 以蓝色为主
        if blue_count >= 14:
            return {"passed": True, "description": f"空头MACD配合(蓝{blue_count}/20)"}
        elif blue_count >= 10 and last_color == "蓝" and last_dif < 0:
            return {"passed": True, "description": f"空头MACD偏空(蓝{blue_count}/20)"}
        else:
            return {"passed": False, "description": f"空头MACD不配合(蓝{blue_count}/20, last={last_color})"}


def check_macd_trajectory_replay(symbol: str, klines_macd_tf: List[dict], n_struct: dict, direction: str) -> dict:
    """在历史数据上检查 MACD 轨迹。

    使用提供的 MACD 周期 K 线数据。
    """
    macd_list = compute_macd(klines_macd_tf)
    if len(macd_list) < 26:
        return {"passed": False, "description": f"MACD数据不足({len(macd_list)})"}

    return check_color_sequence(macd_list, n_struct, direction)


# ═══════════════════════════════════════════════════════════
# 15m 突破检测
# ═══════════════════════════════════════════════════════════

def check_breakout(klines_15m: List[dict], n_struct: dict) -> dict:
    """检查 15m K 线上最后一次突破 N 型 B 点。

    Returns:
        {"triggered": bool, "trigger_price": float}
    """
    if len(klines_15m) < 3:
        return {"triggered": False, "trigger_price": 0}

    b_price = n_struct.get("point_b_price", 0)
    direction = n_struct.get("direction", "LONG")

    # 只检查最后几根 bar 的突破
    last_bars = klines_15m[-10:]

    for i in range(len(last_bars) - 1, 0, -1):
        curr = last_bars[i]
        prev = last_bars[i - 1]

        if direction == "LONG":
            curr_brk = curr["high"] >= b_price
            prev_brk = prev["high"] >= b_price
        else:
            curr_brk = curr["low"] <= b_price
            prev_brk = prev["low"] <= b_price

        if curr_brk and not prev_brk:
            tp = max(curr["close"], b_price) if direction == "LONG" else min(curr["close"], b_price)
            return {"triggered": True, "trigger_price": round(tp, 2)}

    # 如果没有新鲜突破，检查是否在 B 点之上（已有突破但未回撤）
    if direction == "LONG":
        for bar in reversed(last_bars):
            if bar["close"] >= b_price:
                return {"triggered": True, "trigger_price": round(bar["close"], 2)}
    else:
        for bar in reversed(last_bars):
            if bar["close"] <= b_price:
                return {"triggered": True, "trigger_price": round(bar["close"], 2)}

    return {"triggered": False, "trigger_price": 0}


# ═══════════════════════════════════════════════════════════
# 3m MACD 稳定性检测
# ═══════════════════════════════════════════════════════════

def check_3m_stability_replay(klines_3m: List[dict], direction: str) -> dict:
    """检查 3 分钟 MACD 稳定性。

    Returns:
        {"stable": bool, "description": str}
    """
    if len(klines_3m) < 30:
        return {"stable": False, "description": f"3m数据不足({len(klines_3m)})"}

    macd_list = compute_macd(klines_3m)
    if len(macd_list) < 26:
        return {"stable": False, "description": "3m MACD数据不足"}

    last_10 = macd_list[-10:]
    color_counts = defaultdict(int)
    for m in last_10:
        color_counts[m["color"]] += 1

    primary = "红" if direction == "LONG" else "蓝"
    primary_count = color_counts.get(primary, 0)

    stable = primary_count >= 7  # 70%+ consistent
    return {
        "stable": stable,
        "description": f"3m稳定: {primary}{primary_count}/10" if stable else f"3m不稳定: {primary}{primary_count}/10",
    }


# ═══════════════════════════════════════════════════════════
# 评分重置检查
# ═══════════════════════════════════════════════════════════

def check_score_reset(klines_1d: List[dict], n_struct_1w: dict, direction: str) -> bool:
    """检查大周期结构是否已被价格突破失效。

    LONG: 最新收盘跌破 B 点 99%
    SHORT: 最新收盘升破 B 点 101%
    """
    if not klines_1d:
        return False
    close = klines_1d[-1]["close"]
    b_price = n_struct_1w.get("point_b_price", 0)

    if direction == "LONG":
        return close < b_price * 0.99
    elif direction == "SHORT":
        return close > b_price * 1.01
    return False


# ═══════════════════════════════════════════════════════════
# 核心：逐月回放 evaluate()
# ═══════════════════════════════════════════════════════════

def run_monthly_replay(symbol: str, start_year: int = 2020, end_year: int = 2026) -> List[ReplayResult]:
    """对单个品种按月回放评估。

    每个月末时间窗口，模拟 evaluate() 的三级验证流程。
    """
    results: List[ReplayResult] = []

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year == end_year and month > 6:
                break
            if year == start_year and month < 1:
                continue

            # 该月最后一天的 23:59 UTC
            if month == 12:
                month_end_ts = int(datetime(year + 1, 1, 1, 0, 0, tzinfo=timezone.utc).timestamp()) - 60
            else:
                month_end_ts = int(datetime(year, month + 1, 1, 0, 0, tzinfo=timezone.utc).timestamp()) - 60

            month_str = f"{year}-{month:02d}"
            rr = ReplayResult()
            rr.symbol = symbol
            rr.month = month_str
            rr.timestamp = month_end_ts

            # ── 加载数据 ──
            k1w = load_klines_upto(DB_PATH, symbol, "1w", month_end_ts)
            k1d = load_klines_upto(DB_PATH, symbol, "1d", month_end_ts)
            k1h = load_klines_upto(DB_PATH, symbol, "1h", month_end_ts)
            k15m = load_klines_upto(DB_PATH, symbol, "15m", month_end_ts)
            k3m = load_klines_upto(DB_PATH, symbol, "3m", month_end_ts)

            # ── Level1: 周线 N 型 + 日线 MACD ──
            l1_n = detect_n_structure(k1w) if len(k1w) >= 20 else None

            if l1_n is None or l1_n.get("state") not in ("LEG2", "LEG3"):
                rr.l1_passed = False
                rr.l1_reason = "无周线N型" if l1_n is None else f"状态{l1_n['state']}不可用"
                rr.score = 0
                results.append(rr)
                continue

            direction = l1_n["direction"]
            rr.l1_direction = direction
            rr.l1_state = l1_n["state"]
            rr.l1_n_structure = l1_n

            # Level1 MACD 检查
            l1_macd_result = check_macd_trajectory_replay(symbol, k1d, l1_n, direction)

            if not l1_macd_result.get("passed", False):
                rr.l1_passed = False
                rr.l1_reason = f"日线MACD不配合: {l1_macd_result.get('description', '')}"
                rr.score = 0
                results.append(rr)
                continue

            rr.l1_passed = True
            rr.l1_reason = l1_macd_result.get("description", "pass")

            # ═══ Level1 通过 → score=1 ═══
            rr.score = 1
            rr.direction = direction

            # ── Level2: 小时线 N 型 + 15m MACD ──
            l2_n = detect_n_structure(k1h) if len(k1h) >= 20 else None

            if l2_n and l2_n.get("direction") == direction and l2_n.get("state") in ("LEG2", "LEG3"):
                l2_macd_result = check_macd_trajectory_replay(symbol, k15m, l2_n, direction)

                if l2_macd_result.get("passed", False):
                    rr.l2_passed = True
                    rr.l2_state = l2_n.get("state", "")
                    rr.score = 2  # Level2 通过 → score=2
                else:
                    rr.l2_state = l2_n.get("state", "")
            elif l2_n:
                rr.l2_state = l2_n.get("state", "")

            # ═══ Level2 通过 → check Level3 ═══
            if rr.score >= 2:
                # ── Level3: 15m N 型 + 3m MACD 稳定 + 突破 ──
                l3_n = detect_n_structure(k15m) if len(k15m) >= 20 else None

                if l3_n and l3_n.get("direction") == direction:
                    rr.l3_state = l3_n.get("state", "")

                    # 3m MACD 稳定
                    stability = check_3m_stability_replay(k3m, direction)
                    # 15m 突破
                    breakout = check_breakout(k15m, l3_n)

                    if breakout.get("triggered") and stability.get("stable"):
                        rr.l3_passed = True
                        rr.score = 3  # Level3 通过 → ENTRY
                    elif not stability.get("stable"):
                        rr.l3_reason = f"3m不稳定: {stability.get('description', '')}"
                    elif not breakout.get("triggered"):
                        rr.l3_reason = "15m未突破B点"
                else:
                    rr.l3_reason = "无15m N型" if l3_n is None else "方向不一致"

            # ── 评分重置检查 ──
            if rr.score >= 1:
                if check_score_reset(k1d, l1_n, direction):
                    rr.score = 0
                    rr.l1_reason += " | 价格已突破B点=重置"

            results.append(rr)

    logger.info(f"{symbol}: 扫描{len(results)}个月, "
                f"score>=2: {sum(1 for r in results if r.score >= 2)}, "
                f"score=3: {sum(1 for r in results if r.score >= 3)}")
    return results


# ═══════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results: Dict[str, List[dict]] = {}
    summary = {
        "total_symbols": 0,
        "total_months": 0,
        "by_symbol": {},
        "aggregate": {
            "score_0": 0,
            "score_1": 0,
            "score_2": 0,
            "score_3": 0,
            "max_score_reached": 0,
            "months_with_signal": 0,
            "total_months": 0,
        },
    }

    for sym in TARGET_SYMBOLS:
        logger.info(f"\n{'='*50}")
        logger.info(f"回放: {sym}")
        logger.info(f"{'='*50}")

        results = run_monthly_replay(sym, start_year=2020, end_year=2026)
        all_results[sym] = [r.to_dict() for r in results]

        # Per-symbol stats
        sym_stats = {
            "total_months": len(results),
            "score_0": sum(1 for r in results if r.score == 0),
            "score_1": sum(1 for r in results if r.score == 1),
            "score_2": sum(1 for r in results if r.score >= 2),
            "score_3": sum(1 for r in results if r.score >= 3),
            "max_score": max((r.score for r in results), default=0),
            "months_with_l1": sum(1 for r in results if r.l1_passed),
            "months_with_l2": sum(1 for r in results if r.l2_passed),
            "months_with_l3": sum(1 for r in results if r.l3_passed),
        }
        summary["by_symbol"][sym] = sym_stats

        # Aggregate
        summary["aggregate"]["score_0"] += sym_stats["score_0"]
        summary["aggregate"]["score_1"] += sym_stats["score_1"]
        summary["aggregate"]["score_2"] += sym_stats["score_2"]
        summary["aggregate"]["score_3"] += sym_stats["score_3"]
        summary["aggregate"]["max_score_reached"] = max(summary["aggregate"]["max_score_reached"], sym_stats["max_score"])
        summary["aggregate"]["total_months"] += sym_stats["total_months"]
        summary["total_symbols"] += 1

        # 打印详细统计
        logger.info(f"  Score=0: {sym_stats['score_0']:>3} | Score=1: {sym_stats['score_1']:>3} | Score>=2: {sym_stats['score_2']:>3} | Score=3: {sym_stats['score_3']:>3}")
        logger.info(f"  Max score: {sym_stats['max_score']} | L1 pass: {sym_stats['months_with_l1']} | L2 pass: {sym_stats['months_with_l2']} | L3 pass: {sym_stats['months_with_l3']}")

    # 直接计算
    score_ge2_months = 0
    score_3_months = 0
    for sym, sym_results in all_results.items():
        for r in sym_results:
            if r["score"] >= 2:
                score_ge2_months += 1
            if r["score"] >= 3:
                score_3_months += 1

    summary["aggregate"]["months_with_signal"] = score_ge2_months
    summary["aggregate"]["months_with_entry"] = score_3_months

    # 输出结果
    output = {
        "summary": summary,
        "per_symbol": all_results,
    }

    json_path = OUTPUT_DIR / "replay_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 打印总结报告
    print("\n" + "=" * 60)
    print("  历史回放验证结果")
    print("=" * 60)
    print(f"\n目标品种: {', '.join(TARGET_SYMBOLS)}")
    print(f"回放窗口: 2020-01 ~ 2026-06 (逐月)")
    print(f"总评估次数: {summary['aggregate']['total_months']}")
    print(f"\n{'='*40}")
    print(f"  评分分布")
    print(f"{'='*40}")
    print(f"  Score=0 (无信号):    {summary['aggregate']['score_0']:>4}")
    print(f"  Score=1 (L1 only):   {summary['aggregate']['score_1']:>4}")
    print(f"  Score>=2 (信号):     {score_ge2_months:>4}")
    print(f"  Score=3 (ENTRY):     {score_3_months:>4}")
    print(f"\n{'='*40}")
    print(f"  分品种")
    print(f"{'='*40}")
    print(f"  {'Sym':>4} | {'总月数':>6} | {'Score=0':>7} | {'Score=1':>7} | {'Score>=2':>8} | {'Score=3':>8} | {'Max':>4}")
    print(f"  {'-'*4}-+-{'-'*6}-+-{'-'*7}-+-{'-'*7}-+-{'-'*8}-+-{'-'*8}-+-{'-'*4}")
    for sym in TARGET_SYMBOLS:
        s = summary["by_symbol"].get(sym, {})
        print(f"  {sym:>4} | {s.get('total_months', 0):>6} | {s.get('score_0', 0):>7} | {s.get('score_1', 0):>7} | {s.get('score_2', 0):>8} | {s.get('score_3', 0):>8} | {s.get('max_score', 0):>4}")

    # Score>=2 详情
    print(f"\n{'='*60}")
    print(f"  Score>=2 信号详情")
    print(f"{'='*60}")
    for sym in TARGET_SYMBOLS:
        for r in all_results.get(sym, []):
            if r["score"] >= 2:
                print(f"  {sym:>4} {r['month']:>8} | score={r['score']} dir={r['direction']:>5} | L1={r['l1_state']:>5} L2={r['l2_state']:>5} L3={r['l3_state']:>5}")
                if r["score"] >= 3:
                    print(f"         ⭐ ENTRY 信号!")

    print(f"\n{'='*60}")
    print(f"  结论")
    print(f"{'='*60}")
    if score_ge2_months > 0:
        print(f"  ✅ 系统在历史回放中产生了 {score_ge2_months} 次 score>=2 信号")
        if score_3_months > 0:
            print(f"  ✅ 其中有 {score_3_months} 次 ENTRY(score=3) 信号，满足入场条件")
        else:
            print(f"  ❌ 但从未达到 ENTRY(score=3) 条件（Level3 未通过）")
    else:
        print(f"  ❌ 系统在历史回放中从未产生 score>=2 信号")
    print(f"\n  结果保存在: {json_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()