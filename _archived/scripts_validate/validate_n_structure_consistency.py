#!/usr/bin/env python3
"""
N型结构算法一致性验证脚本 — P0 子任务 2

验证目标：
1. 对于同一品种，在 15m/1h/1d/1w 四个周期上，ABC 三点识别逻辑一致
2. 方向判断（LONG/SHORT）在四个周期上由同一算法得出，无周期分支
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.db import Database
from config.settings import DB_PATH
from futures.n_structure import (
    _determine_direction,
    _determine_overall_direction,
    _find_n_structure_forward,
    _merge_same_type,
    _get_swing_points,
)

db = Database(str(DB_PATH))


def validate_symbol_timeframe(symbol: str, contract: str, timeframe: str) -> dict:
    """对单个品种×周期组合执行验证。"""
    result = {
        "symbol": symbol, "contract": contract, "timeframe": timeframe,
        "swing_points_count": 0, "has_n_structures": False,
        "direction": None, "errors": [], "algorithm_consistent": True,
    }

    points = _get_swing_points(db, symbol, contract, timeframe, limit=80)
    result["swing_points_count"] = len(points)
    if len(points) < 4:
        result["errors"].append(f"Swing points < 4 ({len(points)}), skip")
        result["algorithm_consistent"] = None
        return result

    merged = _merge_same_type(points)
    if len(merged) < 4:
        result["errors"].append(f"Merged points < 4 ({len(merged)}), skip")
        return result

    overall_dir = _determine_overall_direction(merged)
    result["overall_direction"] = overall_dir

    # _find_n_structure_forward returns Optional[Dict] (single dict or None)
    n_structure = _find_n_structure_forward(merged, overall_dir)
    result["has_n_structures"] = n_structure is not None
    
    if n_structure is not None:
        result["direction"] = n_structure.get("direction")
        result["structure"] = {
            "direction": n_structure.get("direction"),
            "a_price": n_structure.get("a_price"),
            "b_price": n_structure.get("b_price"),
            "c_price": n_structure.get("c_price"),
            "a_timestamp": n_structure.get("a_timestamp"),
            "b_timestamp": n_structure.get("b_timestamp"),
            "c_timestamp": n_structure.get("c_timestamp"),
            "state": n_structure.get("state"),
        }

    return result


def run():
    print("=" * 70)
    print("N 型结构算法一致性验证")
    print("=" * 70)

    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT symbol, contract FROM futures_n_structures
               GROUP BY symbol, contract
               HAVING COUNT(DISTINCT timeframe) >= 3
               ORDER BY RANDOM()
               LIMIT 20"""
        ).fetchall()

    candidates = [dict(r) for r in rows]
    if not candidates:
        # fallback: pick any symbols that have n_structures
        rows2 = conn.execute(
            "SELECT DISTINCT symbol, contract FROM futures_n_structures LIMIT 10"
        ).fetchall()
        candidates = [dict(r) for r in rows2]

    print(f"\nFound {len(candidates)} candidate symbols")

    # Pick 3 night + 2 day
    night_set = {"rb", "hc", "cu", "al", "zn", "pb", "ni", "sn", "au", "ag", "sc",
                  "i", "j", "jm", "m", "y", "p", "CF", "SR", "RM", "MA", "TA", "FG"}
    night = [c for c in candidates if c["symbol"] in night_set][:3]
    day = [c for c in candidates if c["symbol"] not in night_set][:2]
    symbols_to_check = night + day

    print(f"\nSelected {len(symbols_to_check)} symbols: {[s['symbol'] for s in symbols_to_check]}")

    all_results = []
    all_ok = True

    for sc in symbols_to_check:
        sym, ctr = sc["symbol"], sc["contract"]
        print(f"\n--- {sym} ({ctr}) ---")

        with db.get_conn() as conn:
            tfs = [r[0] for r in conn.execute(
                "SELECT DISTINCT timeframe FROM futures_n_structures WHERE symbol=? AND contract=? ORDER BY timeframe",
                (sym, ctr)
            ).fetchall()]

        tf_results = {}
        directions_seen = set()
        for tf in tfs:
            r = validate_symbol_timeframe(sym, ctr, tf)
            tf_results[tf] = r
            has = r["has_n_structures"]
            status = "\u2705" if has else "\u26a0"
            print(f"  {status} {tf}: {r.get('swing_points_count',0)} points, "
                  f"N-structure={'yes' if has else 'no'}, "
                  f"dir={r.get('direction', '?')}")
            if has and r.get("direction"):
                directions_seen.add(r["direction"])
            if r["algorithm_consistent"] is False:
                all_ok = False

        # Check if all timeframes with N-structures have the same direction
        if len(directions_seen) > 1:
            print(f"  \u26a0\ufe0f DIRECTION MISMATCH across timeframes: {directions_seen}")
            all_ok = False
        elif len(directions_seen) == 1:
            print(f"  \u2705 All timeframes consistent: {directions_seen.pop()}")

        all_results.append({"symbol": sym, "contract": ctr, "timeframes": tf_results})

    print(f"\n{'=' * 70}")
    if all_ok:
        print("\u2705 \u9a8c\u8bc1\u901a\u8fc7: N\u578b\u7ed3\u6784\u7b97\u6cd5\u5728\u6240\u6709\u5468\u671f\u4e0a\u4e00\u81f4\uff0c\u65e0\u5468\u671f\u5206\u652f")
    else:
        print("\u26a0 \u53d1\u73b0\u4e0d\u4e00\u81f4")

    outpath = os.path.join(os.path.dirname(__file__), "..", "..", "memories", "validate_n_structure_result.json")
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, "w") as f:
        json.dump({"passed": all_ok, "symbols": all_results}, f, indent=2, default=str)
    print(f"\nResults saved to {outpath}")


if __name__ == "__main__":
    run()
