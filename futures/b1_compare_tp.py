"""
B1 实验 — TP 倍数对比回测。
运行 tp_mult = 1, 1.5, 2, 3 四个版本的全场回测（7品种，Pullback 入场），输出评分对比。

用法:
    python futures/b1_compare_tp.py
"""
import json
import logging
import sys
import time as time_module
from pathlib import Path

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from futures.n_paper_backtest import (
    TARGET_SYMBOLS, DEFAULT_DB_PATH, OUTPUT_DIR,
    run_all, save_results, print_report,
)

TP_MULTS = [1.0, 1.5, 2.0, 3.0]
CAPITAL = 100000.0


def main():
    print("=" * 70)
    print("  B1 实验：TP 倍数对比回测（Pullback 入场）")
    print("=" * 70)
    print(f"  品种: {', '.join(TARGET_SYMBOLS)}")
    print(f"  资金: ¥{CAPITAL:,.0f}")
    print()

    results = {}

    for tp_mult in TP_MULTS:
        print(f"\n{'─' * 70}")
        print(f"  ▶ tp_mult = {tp_mult}×")
        print(f"{'─' * 70}")
        start = time_module.time()
        agg, summaries, trades = run_all(
            str(DEFAULT_DB_PATH), CAPITAL, entry_mode="pullback", tp_mult=tp_mult
        )
        elapsed = time_module.time() - start
        print_report(agg, summaries)

        # Save with unique suffix
        suffix = f"_tp{tp_mult}"
        csv_path = OUTPUT_DIR / f"n_paper_trades{suffix}.csv"
        json_path = OUTPUT_DIR / f"n_paper_summary{suffix}.json"

        # Manual save with tp_mult suffix
        from futures.n_paper_backtest import save_results
        # Quick JSON save
        jdata = {
            "tp_mult": tp_mult,
            "aggregate": {
                "trades": agg.trades, "wins": agg.wins, "losses": agg.losses,
                "win_rate_pct": round(agg.win_rate * 100, 1),
                "total_pnl": round(agg.total_pnl, 2),
                "total_return_pct": round(agg.total_return_pct, 2),
                "profit_ratio": round(agg.profit_ratio, 2),
                "max_dd_pct": round(agg.max_dd_pct * 100, 2),
                "sharpe": round(agg.sharpe, 2),
                "signal_count": agg.signal_count,
                "score": agg.score,
                "score_details": agg.score_details,
                "grade": "PASS" if agg.score >= 75 else ("WATCH" if agg.score >= 50 else "FAIL"),
            },
            "per_symbol": {},
        }
        for s in summaries:
            jdata["per_symbol"][s.symbol] = {
                "trades": s.trades, "win_rate_pct": round(s.win_rate * 100, 1),
                "total_pnl": round(s.total_pnl, 2),
                "total_return_pct": round(s.total_return_pct, 2),
                "profit_ratio": round(s.profit_ratio, 2),
                "max_dd_pct": round(s.max_dd_pct * 100, 2),
                "sharpe": round(s.sharpe, 2),
                "signal_count": s.signal_count,
                "score": s.score,
            }

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(jdata, f, ensure_ascii=False, indent=2)
        print(f"  JSON: {json_path}")

        results[tp_mult] = {
            "agg": agg, "summaries": summaries, "trades": trades,
            "elapsed": elapsed,
        }

    # ── 对比表 ──
    print(f"\n\n{'=' * 70}")
    print("  B1 评分对比汇总")
    print("=" * 70)

    header = f"  {'tp_mult':>8} | {'Trades':>6} | {'Win%':>6} | {'PnL':>10} | {'Ret%':>7} | {'DD%':>6} | {'Sharpe':>7} | {'Score':>6} | {'Grade':>6}"
    print(header)
    print(f"  {'─'*8}-+-{'─'*6}-+-{'─'*6}-+-{'─'*10}-+-{'─'*7}-+-{'─'*6}-+-{'─'*7}-+-{'─'*6}-+-{'─'*6}")

    best_score = -1
    best_tp = None
    all_pass = True

    for tp_mult in TP_MULTS:
        agg = results[tp_mult]["agg"]
        grade = "PASS ✅" if agg.score >= 75 else "WATCH ⏳" if agg.score >= 50 else "FAIL ❌"
        print(f"  {tp_mult:>7.1f}× | {agg.trades:>6} | {agg.win_rate*100:>5.1f}% | "
              f"{agg.total_pnl:>+9.0f} | {agg.total_return_pct:>+6.2f}% | "
              f"{agg.max_dd_pct*100:>5.2f}% | {agg.sharpe:>7.2f} | {agg.score:>5.0f} | {grade}")
        if agg.score > best_score:
            best_score = agg.score
            best_tp = tp_mult
        if agg.score < 52:
            all_pass = False

    print(f"\n  ⭐ 最佳: tp_mult={best_tp}× (评分 {best_score})")

    # 止损检查
    print(f"\n  {'=' * 70}")
    print(f"  止损条件检查（评分 < 52 → 永久停止 P 阶段）")
    print(f"  {'=' * 70}")
    if all_pass:
        print(f"  ✅ 所有参数评分 ≥ 52 — 可以继续")
    else:
        failing = [f"{tp}×" for tp in TP_MULTS if results[tp]["agg"].score < 52]
        print(f"  ❌ 以下参数评分 < 52: {', '.join(failing)}")
        if all(results[tp]["agg"].score < 52 for tp in TP_MULTS):
            print(f"  ⛔ 所有参数均低于 52 — 触发永久止损条件！")

    # 分维度对比
    print(f"\n\n  {'─' * 50}")
    print("  各维度评分对比")
    print(f"  {'─' * 50}")
    dims = [("wr_score", "胜率"), ("pr_score", "盈亏比"), ("tr_score", "收益"),
            ("dd_score", "回撤"), ("sr_score", "Sharpe")]
    for dim_key, dim_label in dims:
        vals = [(tp, results[tp]["agg"].score_details.get(dim_key, 0)) for tp in TP_MULTS]
        vs = " | ".join([f"{tp}×: {v:.1f}" for tp, v in vals])
        print(f"  {dim_label:>8}: {vs}")

    print(f"\n  ⏱ 总耗时: {sum(r['elapsed'] for r in results.values()):.1f}s")
    print()


if __name__ == "__main__":
    main()
