"""
简单动量基线对照 — 证明 N 型结构有超额预测力，非简单趋势跟踪。

实验方案：
  1. 对每个品种运行 N 型结构回测（复用 n_backtest.run_symbol_backtest）
  2. 在每个 N 型入场点计算各动量窗口（5/10/20/60 日）的方向预测
  3. 对比 N 型 vs 各窗口动量的准确率
  4. McNemar 检验配对差异的统计显著性

用法：
    uv run python futures/momentum_baseline.py

预期输出：
  - 各品种 + 各 lookahead 天数的对比表
  - McNemar 检验结果（chi2, p-value, significant）
  - 聚合汇总（跨品种）
"""

import json
import logging
import sys
from typing import Any, Dict, List, Optional, Tuple

from core.db import Database
from config.settings import DB_PATH
from futures.n_backtest import run_symbol_backtest, run_multi_symbol_backtest

logger = logging.getLogger(__name__)

# ─── 实验配置 ───────────────────────────────────────────────

MOMENTUM_WINDOWS = [5, 10, 20, 60]  # 动量窗口（交易日数）
LOOKAHEAD_DAYS = [1, 2, 5, 10, 20]  # 与 n_backtest 一致

TARGET_SYMBOLS: List[Tuple[str, str]] = [
    ("P", "P"),
    ("RB", "RB"),
    ("Y", "Y"),
    ("EB", "EB"),
    ("L", "L"),
    ("PG", "PG"),
    ("TA", "TA"),
]

# 常规 McNemar 临界值（自由度 1）
CHI2_CRIT_005 = 3.841
CHI2_CRIT_001 = 6.635


# ─── 动量预测器 ─────────────────────────────────────────────


def _kline_ts_to_idx(klines: List[Dict], ts: int) -> Optional[int]:
    """二分查找 kline timestamp → 索引。"""
    lo, hi = 0, len(klines) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        t = klines[mid]["timestamp"]
        if t == ts:
            return mid
        elif t < ts:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


def _get_klines_for_backtest(db: Database, symbol: str, contract: str) -> List[Dict]:
    """加载品种 1d Kline（与 n_backtest._load_klines 逻辑一致）。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT timestamp, open, high, low, close, volume
               FROM futures_klines
               WHERE symbol=? AND contract=? AND timeframe='1d'
               ORDER BY timestamp ASC""",
            (symbol, contract),
        ).fetchall()
    return [dict(r) for r in rows]


def _compute_momentum_prediction(
    klines: List[Dict], entry_idx: int, window: int
) -> Optional[str]:
    """计算简单动量方向预测。

    定义：
        direction = LONG if close[t] > close[t-N] else SHORT

    参数：
        klines: 按时间升序排列的 1d K 线列表。
        entry_idx: 入场点（N 型 C 点）在 klines 中的索引。
        window: 动量回溯窗口，即过去 N 个交易日。

    返回：
        预测方向或 None（数据不足）。
    """
    if entry_idx < window:
        return None

    past_close = klines[entry_idx - window]["close"]
    current_close = klines[entry_idx]["close"]

    return "LONG" if current_close > past_close else "SHORT"


def _check_prediction_outcome(
    klines: List[Dict], entry_idx: int, direction: str, lookahead: int
) -> Optional[bool]:
    """验证一个预测是否正确。

    Args:
        klines: K 线列表。
        entry_idx: 入场索引。
        direction: 预测方向。
        lookahead: 向前看天数。

    Returns:
        True=正确, False=错误, None=数据不足无法验证。
    """
    exit_idx = entry_idx + lookahead
    if exit_idx >= len(klines):
        return None

    entry_price = klines[entry_idx]["close"]
    exit_price = klines[exit_idx]["close"]

    if direction == "LONG":
        return exit_price > entry_price
    else:
        return exit_price < entry_price


# ─── McNemar 检验 ───────────────────────────────────────────


def _run_mcnemar(
    contingencies: Dict[str, int],
) -> Dict[str, Any]:
    """运行 McNemar 检验。

    四格表：
        - a (both_correct): N 型和动量都正确
        - b (n_only): N 型正确、动量错误
        - c (mom_only): N 型错误、动量正确
        - d (both_wrong): 双方都错误

    统计量（连续校正）：
        χ² = (|b-c| - 1)² / (b+c)，自由度 1

    Args:
        contingencies: 汇总后的四格表计数字典。

    Returns:
        含 chi2 / p_value / significant 的字典。
    """
    b = contingencies.get("n_only", 0)
    c = contingencies.get("mom_only", 0)
    a = contingencies.get("both_correct", 0)
    d = contingencies.get("both_wrong", 0)
    total = a + b + c + d

    if b + c == 0:
        return {
            "a_both_correct": a,
            "b_n_only": b,
            "c_mom_only": c,
            "d_both_wrong": d,
            "total": total,
            "chi2": 0.0,
            "p_value_approx": 1.0,
            "significant": False,
            "n_accuracy": None,
            "mom_accuracy": None,
        }

    chi2 = (abs(b - c) - 1) ** 2 / (b + c)

    # 近似 p-value（χ²(1) 分布）：直接用临界值判断
    significant_005 = chi2 > CHI2_CRIT_005
    significant_001 = chi2 > CHI2_CRIT_001

    # 估算 p_value 范围
    if chi2 > CHI2_CRIT_001:
        p_range = "p < 0.01"
    elif chi2 > CHI2_CRIT_005:
        p_range = "p < 0.05"
    else:
        p_range = "p ≥ 0.05"

    n_acc = a + b
    mom_acc = a + c
    n_accuracy = round(n_acc / total * 100, 1) if total else 0
    mom_accuracy = round(mom_acc / total * 100, 1) if total else 0

    return {
        "a_both_correct": a,
        "b_n_only": b,
        "c_mom_only": c,
        "d_both_wrong": d,
        "total": total,
        "chi2": round(chi2, 4),
        "p_value_range": p_range,
        "significant_005": significant_005,
        "significant_001": significant_001,
        "n_accuracy": n_accuracy,
        "mom_accuracy": mom_accuracy,
    }


# ─── 单品种对照实验 ─────────────────────────────────────────


def run_symbol_comparison(
    db: Database,
    symbol: str,
    contract: str,
) -> Dict[str, Any]:
    """对单个品种运行 N 型 vs 动量对照实验。

    Args:
        db: Database 实例。
        symbol: 品种代码。
        contract: 合约代码。

    Returns:
        含逐动量窗口对比结果的字典。
    """
    # 1. 加载 K 线数据（用于动量计算）
    klines = _get_klines_for_backtest(db, symbol, contract)
    if len(klines) < max(MOMENTUM_WINDOWS) + max(LOOKAHEAD_DAYS) + 5:
        return {
            "symbol": symbol,
            "contract": contract,
            "error": f"K 线不足: {len(klines)}",
            "total_n_structures": 0,
            "by_momentum": {},
        }

    # 2. 运行 N 型结构回测，获取所有预测
    n_result = run_symbol_backtest(
        db, symbol, contract,
        lookahead_days=LOOKAHEAD_DAYS,
    )

    if n_result.get("error") or not n_result.get("predictions"):
        return {
            "symbol": symbol,
            "contract": contract,
            "error": n_result.get("error", "无 N 型预测"),
            "total_n_structures": n_result.get("total_structures", 0),
            "by_momentum": {},
        }

    predictions = n_result["predictions"]
    total_structures = n_result["total_structures"]

    # 3. 构建 entry_time → kline 索引映射
    ts_idx_map = {k["timestamp"]: i for i, k in enumerate(klines)}

    # 4. 对每个动量窗口 x lookahead 天数做对比
    results_by_momentum: Dict[str, Any] = {}

    for mw in MOMENTUM_WINDOWS:
        mw_key = f"mom_{mw}d"
        lookahead_results: Dict[str, Any] = {}

        for ld in LOOKAHEAD_DAYS:
            ld_key = f"lookahead_{ld}d"
            contingencies = {
                "both_correct": 0,
                "n_only": 0,
                "mom_only": 0,
                "both_wrong": 0,
            }
            skipped = 0

            for pred in predictions:
                entry_ts = pred["entry_time"]
                entry_idx = ts_idx_map.get(entry_ts)
                if entry_idx is None:
                    skipped += 1
                    continue

                direction = pred["direction"]

                # 动量预测
                mom_direction = _compute_momentum_prediction(
                    klines, entry_idx, mw
                )
                if mom_direction is None:
                    skipped += 1
                    continue

                # 结果验证
                n_outcome = _check_prediction_outcome(
                    klines, entry_idx, direction, ld
                )
                mom_outcome = _check_prediction_outcome(
                    klines, entry_idx, mom_direction, ld
                )
                if n_outcome is None or mom_outcome is None:
                    skipped += 1
                    continue

                # 四格表计数
                if n_outcome and mom_outcome:
                    contingencies["both_correct"] += 1
                elif n_outcome and not mom_outcome:
                    contingencies["n_only"] += 1
                elif not n_outcome and mom_outcome:
                    contingencies["mom_only"] += 1
                else:
                    contingencies["both_wrong"] += 1

            mcnemar = _run_mcnemar(contingencies)
            mcnemar["skipped"] = skipped
            lookahead_results[ld_key] = mcnemar

        # 额外：计算 N 型自身准确率（来自 backtest 结果）
        n_accuracy = n_result.get("accuracy", {})
        n_accuracy_summary = {}
        for ld in LOOKAHEAD_DAYS:
            ld_key = f"{ld}d"
            acc_entry = n_accuracy.get(ld_key, {})
            n_accuracy_summary[ld_key] = {
                "accuracy": acc_entry.get("accuracy", 0),
                "total": acc_entry.get("total", 0),
            }

        results_by_momentum[mw_key] = {
            "momentum_window": mw,
            "lookahead_results": lookahead_results,
        }

    return {
        "symbol": symbol,
        "contract": contract,
        "total_n_structures": total_structures,
        "klines_total": len(klines),
        "n_accuracy": n_accuracy_summary,
        "by_momentum": results_by_momentum,
    }


# ─── 多品种聚合 ─────────────────────────────────────────────


def run_multi_symbol_comparison(
    db: Database,
    symbols: Optional[List[Tuple[str, str]]] = None,
) -> Dict[str, Any]:
    """运行多品种对照实验并聚合。

    Args:
        db: Database 实例。
        symbols: [(symbol, contract)] 列表，默认 TARGET_SYMBOLS。

    Returns:
        含各品种结果 + 跨品种聚合的字典。
    """
    if symbols is None:
        symbols = TARGET_SYMBOLS

    by_symbol: Dict[str, Any] = {}
    errors: List[str] = []

    for sym, ctr in symbols:
        print(f"\n  {'='*55}")
        print(f"  {sym} ({ctr}) — 加载中...")
        print(f"  {'='*55}")

        result = run_symbol_comparison(db, sym, ctr)

        if result.get("error"):
            print(f"  ❌ 错误: {result['error']}")
            errors.append(f"{sym}: {result['error']}")
            by_symbol[sym] = result
            continue

        print(f"  N 型结构: {result['total_n_structures']} 个")
        print(f"  K 线总量: {result['klines_total']} 根")

        by_symbol[sym] = result

    # 聚合：跨品种按动量窗口 + lookahead 汇总
    aggregated = _aggregate_results(by_symbol)

    return {
        "symbols_tested": len(symbols),
        "symbols_succeeded": len(symbols) - len(errors),
        "symbols_errors": len(errors),
        "error_details": errors,
        "by_symbol": by_symbol,
        "aggregated": aggregated,
    }


def _aggregate_results(
    by_symbol: Dict[str, Any],
) -> Dict[str, Any]:
    """跨品种聚合四格表，计算全局 McNemar 检验。

    将各品种的 contingencies 直接相加，得到"全世界"的配对结果，
    然后对每个 (动量窗口, lookahead) 组合运行 McNemar 检验。
    """
    aggregated: Dict[str, Any] = {}

    for mw in MOMENTUM_WINDOWS:
        mw_key = f"mom_{mw}d"
        aggregated[mw_key] = {"momentum_window": mw, "lookahead_results": {}}

        for ld in LOOKAHEAD_DAYS:
            ld_key = f"lookahead_{ld}d"

            # 聚合四格表
            agg_cont = {
                "both_correct": 0,
                "n_only": 0,
                "mom_only": 0,
                "both_wrong": 0,
            }

            for sym, result in by_symbol.items():
                if result.get("error"):
                    continue
                bm = result.get("by_momentum", {}).get(mw_key, {})
                lr = bm.get("lookahead_results", {}).get(ld_key, {})
                agg_cont["both_correct"] += lr.get("a_both_correct", 0)
                agg_cont["n_only"] += lr.get("b_n_only", 0)
                agg_cont["mom_only"] += lr.get("c_mom_only", 0)
                agg_cont["both_wrong"] += lr.get("d_both_wrong", 0)

            mcnemar = _run_mcnemar(agg_cont)
            aggregated[mw_key]["lookahead_results"][ld_key] = mcnemar

    return aggregated


# ─── 输出格式化 ─────────────────────────────────────────────


def _fmt_pct(val: float) -> str:
    """格式化百分比。"""
    return f"{val:6.1f}%"


def _fmt_bool(val: bool) -> str:
    """格式化布尔值为符号。"""
    return "✅" if val else "❌"


def print_summary(result: Dict[str, Any]) -> None:
    """打印人类可读的结果摘要。"""
    by_symbol = result.get("by_symbol", {})
    aggregated = result.get("aggregated", {})

    # ================================================================
    # 1. 各品种概览
    # ================================================================
    print(f"\n{'='*70}")
    print("  S.2.2.2 动量基线对照 — 各品种 N 型准确率")
    print(f"{'='*70}")

    header = f"  {'品种':>4} | {'结构数':>6} | "
    for ld in LOOKAHEAD_DAYS:
        header += f"{ld:>2}d_acc | "
    print(header)
    print(f"  {'-'*4}-+-{'-'*6}-+-" + "-" * (len(LOOKAHEAD_DAYS) * 9))

    for sym in [s[0] for s in TARGET_SYMBOLS]:
        sym_result = by_symbol.get(sym, {})
        if sym_result.get("error"):
            print(f"  {sym:>4} | ❌ {sym_result.get('error', '')}")
            continue

        n_acc = sym_result.get("n_accuracy", {})
        n_structs = sym_result.get("total_n_structures", 0)

        line = f"  {sym:>4} | {n_structs:>6} | "
        for ld in LOOKAHEAD_DAYS:
            acc_entry = n_acc.get(f"{ld}d", {})
            acc = acc_entry.get("accuracy", 0)
            line += f"{acc:>6.1f}% | "
        print(line)

    # ================================================================
    # 2. 跨品种聚合 — McNemar 检验结果
    # ================================================================
    print(f"\n{'='*70}")
    print("  跨品种 McNemar 检验（N 型 vs 动量）")
    print(f"{'='*70}")

    for mw in MOMENTUM_WINDOWS:
        mw_key = f"mom_{mw}d"
        agg_mw = aggregated.get(mw_key, {})
        print(f"\n  ─── 动量窗口 = {mw:>2} 日 ───")

        header = (
            f"  {'Lookahead':>10} | {'N型准确率':>10} | {'动量准确率':>10} | "
            f"{'N仅对':>6} | {'动仅对':>6} | {'McNemar χ²':>10} | {'p 值':>10} | {'显著':>6}"
        )
        print(header)
        print(f"  {'-'*10}-+-{'─'*10}-+-{'─'*10}-+-{'─'*6}-+-{'─'*6}-+-{'─'*10}-+-{'─'*10}-+-{'─'*6}")

        for ld in LOOKAHEAD_DAYS:
            ld_key = f"lookahead_{ld}d"
            lr = agg_mw.get("lookahead_results", {}).get(ld_key, {})
            if not lr:
                continue

            n_acc = lr.get("n_accuracy", 0)
            mom_acc = lr.get("mom_accuracy", 0)
            b = lr.get("b_n_only", 0)
            c = lr.get("c_mom_only", 0)
            chi2 = lr.get("chi2", 0)
            p_range = lr.get("p_value_range", "N/A")
            sig = lr.get("significant_005", False)

            print(
                f"  {f'{ld:>2}d':>10} | {_fmt_pct(n_acc):>10} | {_fmt_pct(mom_acc):>10} | "
                f"{b:>6} | {c:>6} | {chi2:>10.4f} | {p_range:>10} | {_fmt_bool(sig):>6}"
            )

    # ================================================================
    # 3. 关键判断：N 型是否显著超越所有动量窗口？
    # ================================================================
    print(f"\n{'='*70}")
    print("  结论判断")
    print(f"{'='*70}")

    min_gap_1d = float("inf")
    min_gap_5d = float("inf")
    sig_all = True

    for mw in MOMENTUM_WINDOWS:
        mw_key = f"mom_{mw}d"
        agg_mw = aggregated.get(mw_key, {})

        # 1d gap
        lr_1d = agg_mw.get("lookahead_results", {}).get("lookahead_1d", {})
        n_1d = lr_1d.get("n_accuracy", 0)
        m_1d = lr_1d.get("mom_accuracy", 0)
        gap_1d = n_1d - m_1d
        sig_1d = lr_1d.get("significant_005", False)

        # 5d gap
        lr_5d = agg_mw.get("lookahead_results", {}).get("lookahead_5d", {})
        n_5d = lr_5d.get("n_accuracy", 0)
        m_5d = lr_5d.get("mom_accuracy", 0)
        gap_5d = n_5d - m_5d
        sig_5d = lr_5d.get("significant_005", False)

        min_gap_1d = min(min_gap_1d, gap_1d)
        min_gap_5d = min(min_gap_5d, gap_5d)
        if not sig_1d:
            sig_all = False

        n_plus = "  ✅" if gap_1d > 0 else "  ⚠️"
        print(f"  mom={mw:>2}d: N型 1d {n_1d:.1f}% vs 动量 {m_1d:.1f}% "
              f"(差距 {gap_1d:+.1f}pct{sig_1d and ' ✅ 显著' or ' ❌ 不显著'})")
        print(f"           N型 5d {n_5d:.1f}% vs 动量 {m_5d:.1f}% "
              f"(差距 {gap_5d:+.1f}pct{sig_5d and ' ✅ 显著' or ' ❌ 不显著'})")

    passes_min_gap = min_gap_1d >= 5.0 or min_gap_5d >= 5.0
    passes_sig = sig_all

    print(f"\n  {'─'*50}")
    print(f"  判断标准：N 型至少比所有动量窗口高出 ≥ 5pct")
    print(f"  最小 1d 差距: {min_gap_1d:+.1f}pct")
    print(f"  最小 5d 差距: {min_gap_5d:+.1f}pct")
    print(f"  所有窗口统计显著: {'是 ✅' if passes_sig else '否 ⚠️'}")

    if passes_min_gap:
        print(f"\n  ✅ 结论: N 型结构显著超越所有动量窗口 — 具有超额预测力")
    else:
        print(f"\n  ⚠️  结论: N 型未能超越所有动量窗口 ≥ 5pct")

    if not passes_sig:
        print(f"  ⚠️  注意: 部分动量窗口差异未达统计显著性（McNemar p ≥ 0.05）")


# ─── CLI 入口 ───────────────────────────────────────────────


def main():
    """CLI 入口：运行动量基线对照并输出结果。"""
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    db = Database(DB_PATH)

    # 检查数据库连接
    with db.get_conn() as conn:
        count = conn.execute(
            "SELECT COUNT(*) as cnt FROM futures_klines WHERE timeframe='1d'"
        ).fetchone()["cnt"]
    print(f"1d Kline 总量: {count}")
    print(f"品种: {', '.join(s[0] for s in TARGET_SYMBOLS)}")
    print(f"动量窗口: {MOMENTUM_WINDOWS}")
    print(f"Lookahead 天数: {LOOKAHEAD_DAYS}")

    result = run_multi_symbol_comparison(db)
    print_summary(result)

    # 输出 JSON 摘要
    print(f"\n{'='*70}")
    print("  JSON 摘要（跨品种聚合）")
    print(f"{'='*70}")
    print(json.dumps(result.get("aggregated", {}), ensure_ascii=False, indent=2))

    return result


if __name__ == "__main__":
    result = main()
    sys.exit(0)