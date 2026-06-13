"""
N 型结构参数优化实验 — swing_window_size 对预测准确率的影响。

实验方案：
  1. 对每个候选窗口值运行全量历史回测
  2. 评估 1d/5d/10d/20d 方向准确率及结构数量
  3. 品种：P（棕榈油，主力）+ RB（螺纹钢，验证）
  4. 结论：最优值相比默认(5)提升 ≥ 2pct 才切换

用法：
    uv run python futures/param_optim.py
"""

import json
import logging
import sys
from typing import Any, Dict, List

from core.db import Database
from config.settings import DB_PATH
from futures.n_backtest import run_symbol_backtest

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s %(message)s",
)

# ─── 实验配置 ─────────────────────────────────────────────

CANDIDATE_WINDOWS = [3, 5, 7, 10, 14, 20]
DEFAULT_WINDOW = 5

TEST_SYMBOLS = [
    ("P", "P"),   # 主力 — 棕榈油（92.5% WFA，最强）
    ("RB", "RB"), # 验证 — 螺纹钢（81-83% WFA）
]

LOOKAHEAD_DAYS = [1, 5, 10, 20]


def run_param_optim(
    db: Database,
) -> Dict[str, Any]:
    """对所有候选窗口值运行参数优化实验。

    Returns:
        按品种组织的优化结果。
    """
    results: Dict[str, List] = {}

    for symbol, contract in TEST_SYMBOLS:
        print(f"\n{'='*60}")
        print(f"  品种: {symbol} ({contract})")
        print(f"{'='*60}")

        symbol_results = []

        for sw in CANDIDATE_WINDOWS:
            result = run_symbol_backtest(
                db, symbol, contract,
                lookahead_days=LOOKAHEAD_DAYS,
                swing_window=sw,
            )

            acc = result.get("accuracy", {})
            n_structs = result.get("total_structures", 0)
            error = result.get("error")

            if error:
                print(f"  ❌ swing={sw:2d}: {error}")
                continue

            d1 = acc.get("1d", {}).get("accuracy", 0)
            d5 = acc.get("5d", {}).get("accuracy", 0)
            d10 = acc.get("10d", {}).get("accuracy", 0)
            d20 = acc.get("20d", {}).get("accuracy", 0)
            long_pct = acc.get("long_pct", 0)
            short_pct = acc.get("short_pct", 0)

            marker = " ⬅️ 默认" if sw == DEFAULT_WINDOW else ""
            print(f"  swing={sw:2d}{marker}: "
                  f"{n_structs:4d} 结构 | "
                  f"1d={d1:5.1f}% | 5d={d5:5.1f}% | "
                  f"10d={d10:5.1f}% | 20d={d20:5.1f}% | "
                  f"L={long_pct:.0f}% S={short_pct:.0f}%")

            symbol_results.append({
                "swing_window": sw,
                "total_structures": n_structs,
                "accuracy_1d": d1,
                "accuracy_5d": d5,
                "accuracy_10d": d10,
                "accuracy_20d": d20,
                "long_pct": long_pct,
                "short_pct": short_pct,
                "is_default": sw == DEFAULT_WINDOW,
            })

        results[symbol] = symbol_results

    return results


def analyze_results(results: Dict[str, List]) -> None:
    """分析实验结果并给出推荐。"""
    print(f"\n{'='*60}")
    print("  分析")
    print(f"{'='*60}")

    for symbol, rows in results.items():
        if not rows:
            continue

        print(f"\n  --- {symbol} ---")

        # 找 1d 准确率最优
        best_1d = max(rows, key=lambda r: r["accuracy_1d"])
        default_row = next(r for r in rows if r["is_default"])
        default_1d = default_row["accuracy_1d"]
        best_1d_gain = best_1d["accuracy_1d"] - default_1d

        # 找 5d 准确率最优
        best_5d = max(rows, key=lambda r: r["accuracy_5d"])
        default_5d = default_row["accuracy_5d"]
        best_5d_gain = best_5d["accuracy_5d"] - default_5d

        print(f"  默认(swing=5): 1d={default_1d:.1f}%, 5d={default_5d:.1f}%")
        print(f"  最佳 1d: swing={best_1d['swing_window']} "
              f"({best_1d['accuracy_1d']:.1f}%, "
              f"增益={best_1d_gain:+.1f}pct)")
        print(f"  最佳 5d: swing={best_5d['swing_window']} "
              f"({best_5d['accuracy_5d']:.1f}%, "
              f"增益={best_5d_gain:+.1f}pct)")

        # 结构数量趋势
        for r in rows:
            struct_change = ""
            if r != default_row:
                diff = r["total_structures"] - default_row["total_structures"]
                struct_change = f"({diff:+d} vs 默认)"
            print(f"    swing={r['swing_window']:2d}: {r['total_structures']:4d} 结构 "
                  f"{struct_change}")

        # 推荐判断
        if best_1d_gain >= 2.0:
            print(f"\n  ✅ 推荐: 切换至 swing={best_1d['swing_window']} "
                  f"(1d 增益 {best_1d_gain:+.1f}pct ≥ +2pct 阈值)")
        else:
            print(f"\n  ⏸️ 维持默认 swing=5 "
                  f"(最优增益 {best_1d_gain:+.1f}pct < +2pct 阈值)")

        # 结构数量稳定性检查
        min_structs = min(r["total_structures"] for r in rows)
        max_structs = max(r["total_structures"] for r in rows)
        if max_structs > 0 and min_structs / max_structs < 0.3:
            print(f"  ⚠️  注意: 结构数量波动大 "
                  f"(min={min_structs}, max={max_structs}) — "
                  f"窗口过大可能导致样本不足")


def main():
    """CLI 入口。"""
    db = Database(DB_PATH)

    # 检查数据库连接
    with db.get_conn() as conn:
        count = conn.execute(
            "SELECT COUNT(*) as cnt FROM futures_klines WHERE symbol=? AND timeframe='1d'",
            ("P",),
        ).fetchone()["cnt"]
    print(f"P 品种 1d Kline 数量: {count}")

    results = run_param_optim(db)
    analyze_results(results)

    # 输出 JSON 供后续分析
    print(f"\n{'='*60}")
    print("  JSON 摘要")
    print(f"{'='*60}")
    summary = {}
    for symbol, rows in results.items():
        summary[symbol] = [
            {
                "swing_window": r["swing_window"],
                "n_structures": r["total_structures"],
                "acc_1d": r["accuracy_1d"],
                "acc_5d": r["accuracy_5d"],
                "acc_10d": r["accuracy_10d"],
                "acc_20d": r["accuracy_20d"],
            }
            for r in rows
        ]

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # 汇总决策
    print(f"\n{'='*60}")
    print("  决策")
    print(f"{'='*60}")
    decisions = []
    for symbol, rows in results.items():
        if not rows:
            continue
        default = next(r for r in rows if r["is_default"])
        best = max(rows, key=lambda r: r["accuracy_1d"])
        gain = best["accuracy_1d"] - default["accuracy_1d"]
        should_switch = gain >= 2.0
        decisions.append({
            "symbol": symbol,
            "default_1d": default["accuracy_1d"],
            "best_swing": best["swing_window"],
            "best_1d": best["accuracy_1d"],
            "gain_pct": round(gain, 1),
            "should_switch": should_switch,
        })
        action = "✅ 切换" if should_switch else "⏸️ 维持默认"
        print(f"  {symbol}: {action} (最佳 swing={best['swing_window']}, "
              f"增益={gain:+.1f}pct)")

    return decisions


if __name__ == "__main__":
    decisions = main()
    # 如果任意品种需要切换，输出汇总
    if any(d["should_switch"] for d in decisions):
        print(f"\n  ⚡ 至少一个品种建议切换参数，需在 consensus 中记录")
    sys.exit(0)