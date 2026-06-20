#!/usr/bin/env python3
"""
N 型结构算法全量验证脚本（P0.1）

对所有 main contract（symbol = contract）× 4 周期（15m/1h/1d/1w）：
1. 从 DB 读取极值点
2. 运行 _merge_same_type() + _find_n_structure_forward()（当前算法）
3. 验证 ABC 标点 + 4 个判定条件
4. 与 DB 中存储的活跃结构对比

输出: docs/qa/n-structure-verification.md

用法:
    cd projects/options_arbitrage_system
    python3 verify_n_structure.py
"""

import os, sys, sqlite3, time as time_module, argparse
from datetime import datetime, timezone, timedelta

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from futures.n_structure import _merge_same_type, _find_n_structure_forward, _determine_overall_direction
from core.db import Database
from config.settings import DETECT_WINDOWS as DW

DB_PATH = os.path.join(PROJECT_ROOT, "trading_system.db")
TIMEFRAMES = ["15m", "1h", "1d", "1w"]
CST = timezone(timedelta(hours=8))

def fmt_ts(ts):
    """Unix 秒 → CST"""
    if not ts: return "N/A"
    return datetime.fromtimestamp(ts, tz=CST).strftime("%m-%d %H:%M")

# ── 4 条件检查 ──

def check_long(a, b, c, latest):
    """上升 N 型 4 条件"""
    c1 = b > a
    c2 = c < b
    c3 = c > a
    c4 = latest > c if latest is not None else None
    return c1, c2, c3, c4

def check_short(a, b, c, latest):
    """下降 N 型 4 条件"""
    c1 = a > b
    c2 = c > b
    c3 = c < a
    c4 = latest < c if latest is not None else None
    return c1, c2, c3, c4

def check_all(direction, a, b, c, latest):
    if direction == "LONG":
        return check_long(a, b, c, latest)
    return check_short(a, b, c, latest)

def cond_symbols(conds):
    """✅/❌ for each condition"""
    return " ".join("✅" if c is True else "❌" if c is False else "—" for c in conds)

def fail_details(direction, c1, c2, c3, c4, a, b, c, latest, label=""):
    """Build failure detail lines"""
    descs = []
    if direction == "LONG":
        pairs = [
            (c1, f"B({b:.2f}) > A({a:.2f}) = {b > a}"),
            (c2, f"C({c:.2f}) < B({b:.2f}) = {c < b}"),
            (c3, f"C({c:.2f}) > A({a:.2f}) = {c > a}"),
            (c4, f"最新({latest:.2f}) > C({c:.2f}) = {latest > c}" if latest else "—"),
        ]
    else:
        pairs = [
            (c1, f"A({a:.2f}) > B({b:.2f}) = {a > b}"),
            (c2, f"C({c:.2f}) > B({b:.2f}) = {c > b}"),
            (c3, f"C({c:.2f}) < A({a:.2f}) = {c < a}"),
            (c4, f"最新({latest:.2f}) < C({c:.2f}) = {latest < c}" if latest else "—"),
        ]
    for ok, desc in pairs:
        if ok is False:
            descs.append(f"  {'[%s]' % label + ' ' if label else ''}❌ {desc}")
    return descs

def load_db_structures(db):
    """Load active structures from DB for comparison"""
    result = {}
    keys_with_dupes = set()
    key_count = {}
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM futures_n_structures WHERE state NOT IN ('COMPLETED', 'IDLE') ORDER BY symbol, contract, timeframe, id DESC"
        ).fetchall()
    for r in rows:
        key = (r["symbol"], r["contract"], r["timeframe"])
        key_count[key] = key_count.get(key, 0) + 1
        if key not in result:
            result[key] = dict(r)
    for k, c in key_count.items():
        if c > 1:
            keys_with_dupes.add(k)
    return result, keys_with_dupes

def main():
    parser = argparse.ArgumentParser(description="N型结构算法全量验证")
    parser.add_argument("--with-params", action="store_true",
                        help="传递 overall_direction + current_price 参数（P0.2方向优先+条件4整合）")
    parser.add_argument("--output", default="n-structure-verification",
                        help="输出文件名前缀（默认: n-structure-verification）")
    args = parser.parse_args()
    with_params = args.with_params
    output_prefix = args.output

    db = Database(DB_PATH)

    # Get main contracts (symbol == contract)
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT symbol FROM futures_swing_points WHERE symbol = contract ORDER BY symbol"
        ).fetchall()
    symbols = [r["symbol"] for r in rows]

    db_structs, db_dupe_keys = load_db_structures(db)
    all_results = []
    fail_list = []
    pass_count = fail_count = na_count = 0
    sym_fails = {}
    tf_fail_counts = {tf: {"c1":0,"c2":0,"c3":0,"c4":0} for tf in TIMEFRAMES}

    for sym in symbols:
        for tf in TIMEFRAMES:
            limit = DW.get(tf, 40)
            sp = []
            with db.get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM futures_swing_points WHERE symbol=? AND contract=? AND timeframe=? ORDER BY timestamp DESC LIMIT ?",
                    (sym, sym, tf, limit * 2)
                ).fetchall()
                sp = [dict(r) for r in reversed(rows)]

            if len(sp) < 3:
                all_results.append({"symbol": sym, "tf": tf, "overall": "⚠️", "dir": "—",
                    "a": "—", "b": "—", "c": "—", "latest": "—",
                    "conds": "—", "detail": f"极值点不足: {len(sp)}"})
                na_count += 1
                continue

            merged = _merge_same_type(sp)
            if len(merged) < 3:
                all_results.append({"symbol": sym, "tf": tf, "overall": "⚠️", "dir": "—",
                    "a": "—", "b": "—", "c": "—", "latest": "—",
                    "conds": "—", "detail": f"merge后不足: {len(merged)}"})
                na_count += 1
                continue

            # ── 方向预判 + 最新价读取 ─────────────────────────────
            overall_direction = None
            if with_params:
                overall_direction = _determine_overall_direction(merged)

            # 获取最新价（带 params 模式：先取再传；不带 params：仅用于后面的条件检查）
            latest = None
            with db.get_conn() as conn:
                r = conn.execute(
                    "SELECT close FROM futures_klines WHERE symbol=? AND contract=? AND timeframe=? ORDER BY timestamp DESC LIMIT 1",
                    (sym, sym, tf)
                ).fetchone()
                if r: latest = r["close"]

            best = _find_n_structure_forward(merged, overall_direction, latest if with_params else None)

            d = best["direction"]
            a, b, c = best["a"]["price"], best["b"]["price"], best["c"]["price"]
            conds = check_all(d, a, b, c, latest)
            ok = all(c is True for c in conds)

            details = []
            if latest is None:
                details.append("  ⚠️ 无最新K线数据")
                na_count += 1
            elif not ok:
                details = fail_details(d, *conds, a, b, c, latest)
                fail_count += 1
                sym_fails[sym] = sym_fails.get(sym, 0) + 1
                for i, ck in enumerate(conds):
                    if ck is False:
                        tf_fail_counts[tf][f"c{i+1}"] += 1
            else:
                pass_count += 1

            db_key = (sym, sym, tf)
            db_dir = db_structs[db_key]["direction"] if db_key in db_structs else "—"
            db_state = db_structs[db_key]["state"] if db_key in db_structs else "—"
            is_dupe = db_key in db_dupe_keys

            res = {
                "symbol": sym, "tf": tf, "overall": "✅" if ok else "❌",
                "dir": d, "a": a, "b": b, "c": c, "latest": latest,
                "conds": cond_symbols(conds),
                "detail": "\n".join(details),
                "db_dir": db_dir, "db_state": db_state, "is_dupe": is_dupe,
                "a_idx": best.get("a_idx"), "c_idx": best.get("c_idx"),
            }
            all_results.append(res)
            if not ok:
                fail_list.append(res)

    db.close()

    # ── GENERATE REPORT ──
    total = len(all_results)
    lines = []
    def out(s=""): lines.append(s)

    mode_label = "（P0.2 方向优先 + 条件4整合）" if with_params else "（不带参数，默认模式）"
    out(f"# N 型结构算法全量验证报告 — {mode_label}")
    out()
    out(f"> **生成时间**: {datetime.now(tz=CST).strftime('%Y-%m-%d %H:%M:%S')} CST")
    out(f">")
    out(f"> 验证范围: {len(symbols)} 个主要品种 × 4 周期 = {len(symbols * 4)} 条目")
    out(f"> 验证方法: 从 DB 读极值点 → `_merge_same_type()` → `_find_n_structure_forward()`")
    out(f"> 参数模式: {mode_label}")
    out(f"> {'方向预判: 是 · current_price传入: 是' if with_params else '方向预判: 否 · current_price传入: 否'}")
    out()

    # Summary
    out("## 📊 整体统计")
    out()
    out(f"| 状态 | 数量 | 占比 |")
    out(f"|------|------|------|")
    out(f"| ✅ 全部通过 | {pass_count} | {pass_count/total*100:.1f}% |")
    out(f"| ❌ 有失败条件 | {fail_count} | {fail_count/total*100:.1f}% |")
    out(f"| ⚠️ 数据不足 | {na_count} | {na_count/total*100:.1f}% |")
    out(f"| **总计** | **{total}** | **100%** |")
    out()

    # Per-TF
    out("### 📈 按周期统计")
    out()
    out(f"| 周期 | 通过 | 失败 | N/A | 合计 | 通过率 |")
    out(f"|------|------|------|-----|------|--------|")
    for tf in TIMEFRAMES:
        tfr = [r for r in all_results if r["tf"] == tf]
        tp = sum(1 for r in tfr if r["overall"] == "✅")
        tf_ = sum(1 for r in tfr if r["overall"] == "❌")
        tna = sum(1 for r in tfr if r["overall"] == "⚠️")
        valid = tp + tf_
        pct = f"{tp/valid*100:.0f}%" if valid > 0 else "—"
        out(f"| {tf:3s} | {tp} | {tf_} | {tna} | {len(tfr)} | {pct} |")
    out()

    # Failed details
    if fail_list:
        out("## ❌ 未通过验证的品种×周期（{len(fail_list)} 条）")
        out()
        for r in fail_list:
            out(f"### {r['symbol']} — {r['tf']}")
            out()
            out(f"| 指标 | 值 |")
            out(f"|------|-----|")
            out(f"| 算法方向 | {r['dir']} |")
            out(f"| A 价 | {r['a']:.2f} |")
            out(f"| B 价 | {r['b']:.2f} |")
            out(f"| C 价 | {r['c']:.2f} |")
            out(f"| 最新价 | {r['latest']:.2f} |")
            out(f"| DB 方向 | {r['db_dir']} (状态: {r['db_state']}) |")
            out(f"| A 索引 | {r['a_idx']} | C 索引 | {r['c_idx']} |")
            out()

            # Dump the ABC swing points for debugging
            limit = DW.get(r['tf'], 40)
            sp2 = []
            with Database(DB_PATH).get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM futures_swing_points WHERE symbol=? AND contract=? AND timeframe=? ORDER BY timestamp ASC LIMIT ?",
                    (r['symbol'], r['symbol'], r['tf'], limit * 2)
                ).fetchall()
                sp2 = [dict(rr) for rr in rows]
            merged2 = _merge_same_type(sp2)
            out(f"**极值点序列** (swing: {len(sp2)}, merged: {len(merged2)}):")
            out("```")
            for i, mp in enumerate(merged2):
                marker = ""
                if i == r['a_idx']: marker = " ← A"
                elif i == r['c_idx']: marker = " ← C"
                out(f"  [{i:2d}] {mp['point_type']:6s} price={mp['price']:>8.2f} time={fmt_ts(mp['timestamp'])}{marker}")
            out("```")
            out()

            out("**失败详情:**")
            out("```")
            out(r["detail"])
            out("```")
            out("---")
            out()

    # Full matrix
    out("## 📋 完整验证矩阵")
    out()
    out(f"| 品种 | 周期 | 方向 | A价 | B价 | C价 | 最新价 | 条件 | 判定 | DB方向 |")
    out(f"|------|------|------|------|------|------|--------|------|------|--------|")
    for r in all_results:
        if r["overall"] == "✅":
            out(f"| {r['symbol']:4s} | {r['tf']:3s} | {r['dir']:5s} | {r['a']:>8.2f} | {r['b']:>8.2f} | {r['c']:>8.2f} | {r['latest']:>8.2f} | {r['conds']} | {r['overall']} | {r['db_dir']:5s} |")
        elif r["overall"] == "❌":
            out(f"| {r['symbol']:4s} | {r['tf']:3s} | {r['dir']:5s} | {r['a']:>8.2f} | {r['b']:>8.2f} | {r['c']:>8.2f} | {r['latest']:>8.2f} | {r['conds']} | {r['overall']} | {r['db_dir']:5s} |")
        else:
            out(f"| {r['symbol']:4s} | {r['tf']:3s} | {'—':5s} | {'—':>8s} | {'—':>8s} | {'—':>8s} | {'—':>8s} | {'—':>6s} | {r['overall']} | {'—':5s} |")
    out()

    # Pattern analysis
    out("## 🔍 模式识别分析")
    out()
    if sym_fails:
        out("**失败品种按失败次数排序:**")
        out()
        out("| 品种 | 失败数 |")
        out("|------|--------|")
        for s, cnt in sorted(sym_fails.items(), key=lambda x: -x[1]):
            out(f"| {s} | {cnt} |")
        out()
    else:
        out("所有品种均通过验证。")
        out()

    out("**各周期失败条件分布:**")
    out()
    out("| 周期 | 失败总数 | C1 | C2 | C3 | C4 |")
    out("|------|----------|----|----|----|----|")
    for tf in TIMEFRAMES:
        c = tf_fail_counts[tf]
        total_tf_fails = sum(1 for r in all_results if r["tf"] == tf and r["overall"] == "❌")
        out(f"| {tf:3s} | {total_tf_fails} | {c['c1']} | {c['c2']} | {c['c3']} | {c['c4']} |")
    out()

    # Conclusions
    out("## 📌 结论")
    out()
    if fail_count == 0:
        out("✅ **所有品种 × 所有周期的 ABC 标点均满足 4 条判定条件，算法逻辑正确。**")
        out()
        out("无需进入 P0.2 算法修正阶段。可直接进入 P0.3 跨周期复验确认。")
    elif fail_count <= 3:
        out(f"⚠️ **发现 {fail_count} 条标点失败的品种×周期组合，数量较少。**")
        out()
        out("建议：")
        out("1. 人工检查组合同周期极值点序列，确认是否因 swing point 质量导致")
        out("2. 如确认 swing point 正确，则进入 P0.2 调试修正")
    else:
        out(f"🔴 **发现 {fail_count} 条标点失败的品种×周期组合。**")
        out()
        out("建议：")
        out("1. 优先排查条件4（最新价未突破 C 点）——行情自然现象，非算法问题")
        out("2. 排除条件4后，分析剩余的 C1/C2/C3 失败是否指向系统性算法偏差")
        out("3. 按 P0.2 计划进入算法调试修正")
    out()

    # Write report
    os.makedirs(os.path.join(PROJECT_ROOT, "docs", "qa"), exist_ok=True)
    report_path = os.path.join(PROJECT_ROOT, "docs", "qa", f"{output_prefix}.md")
    report_text = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"✅ 验证完成")
    print(f"   通过: {pass_count}  失败: {fail_count}  N/A: {na_count}  总计: {total}")
    print(f"   📄 报告: {report_path}")
    if fail_list:
        print(f"\n   ❌ 失败列表:")
        for r in fail_list:
            print(f"      {r['symbol']:4s} {r['tf']:3s} {r['dir']:5s} "
                  f"A={r['a']:.1f} B={r['b']:.1f} C={r['c']:.1f} 最新={r['latest']} "
                  f"| {r['conds']}")

if __name__ == "__main__":
    main()
