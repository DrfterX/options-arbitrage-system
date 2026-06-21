#!/usr/bin/env python3
"""
N 型结构算法全量验证脚本（P0 Step 1.1）

对所有活跃 main contract（symbol == contract）× 4 周期（15m/1h/1d/1w）：
1. 使用模块函数 _get_swing_points() 读取极值点
2. _merge_same_type() + _find_n_structure_forward() 检测结构
3. 验证 ABC 标点 + 4 个判定条件
4. 输出：
   - docs/qa/n-structure-verification.md   （人类可读报告）
   - docs/qa/n-structure-verification.json （程序分析用 JSON）

用法:
    cd /path/to/project/root
    python3 scripts/verify_n_structure.py

依赖:
    cd projects/options_arbitrage_system 中已安装的依赖
"""

import json
import os
import sys
import time as time_module
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

# ── 路径设置 ─────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # 项目根目录（auto-company_test）
PROJECT_CODE = os.path.join(PROJECT_ROOT, "projects", "options_arbitrage_system")
sys.path.insert(0, PROJECT_CODE)

# ── 导入项目模块 ─────────────────────────────────────────────
from core.db import Database
from config.settings import SWING_WINDOWS, DETECT_WINDOWS
from futures.n_structure import (
    _get_swing_points,
    _merge_same_type,
    _find_n_structure_forward,
    _get_klines,
)

# ── 常量 ────────────────────────────────────────────────────
DB_PATH = os.path.join(PROJECT_CODE, "trading_system.db")
TIMEFRAMES = ["15m", "1h", "1d", "1w"]
CST = timezone(timedelta(hours=8))

OUTPUT_MD = os.path.join(PROJECT_CODE, "docs", "qa", "n-structure-verification.md")
OUTPUT_JSON = os.path.join(PROJECT_CODE, "docs", "qa", "n-structure-verification.json")


# ── 格式化辅助 ──────────────────────────────────────────────


def fmt_ts(ts: Optional[int]) -> str:
    """Unix 秒 → CST 可读字符串"""
    if ts is None:
        return "N/A"
    return datetime.fromtimestamp(ts, tz=CST).strftime("%m-%d %H:%M")


def fmt_ts_full(ts: Optional[int]) -> str:
    if ts is None:
        return "N/A"
    return datetime.fromtimestamp(ts, tz=CST).strftime("%Y-%m-%d %H:%M:%S")


# ── 4 条件检查 ──────────────────────────────────────────────


def check_long(a: float, b: float, c: float, latest: Optional[float]) -> tuple:
    """上升 N 型 4 条件"""
    c1 = b > a                          # B > A: 第一笔上涨
    c2 = c < b                          # C < B: 第二笔下跌
    c3 = c > a                          # C > A: C 不破 A
    c4 = latest > c if latest is not None else None  # 最新价 > C: 潜在第三笔向上
    return (c1, c2, c3, c4)


def check_short(a: float, b: float, c: float, latest: Optional[float]) -> tuple:
    """下降 N 型 4 条件"""
    c1 = a > b                          # A > B: 第一笔下跌
    c2 = c > b                          # C > B: 第二笔上涨
    c3 = c < a                          # C < A: C 不高于 A
    c4 = latest < c if latest is not None else None  # 最新价 < C: 潜在第三笔向下
    return (c1, c2, c3, c4)


def check_all(direction: str, a: float, b: float, c: float,
              latest: Optional[float]) -> tuple:
    if direction == "LONG":
        return check_long(a, b, c, latest)
    return check_short(a, b, c, latest)


def cond_symbols(conds: tuple) -> str:
    """✅/❌/— 图标"""
    return " ".join(
        "✅" if c is True else "❌" if c is False else "—" for c in conds
    )


def fmt_price(px: Optional[float]) -> str:
    """格式化价格，处理 None"""
    return f"{px:.2f}" if px is not None else "N/A"


def fmt_price_md(px: Optional[float], width: int = 8) -> str:
    """Markdown 表格列格式，处理 None"""
    return f"{px:>{width}.2f}" if px is not None else f"{'N/A':>{width}s}"


def fail_details(direction: str, c1: bool, c2: bool, c3: bool,
                 c4: Optional[bool], a: float, b: float, c: float,
                 latest: Optional[float]) -> List[str]:
    descs: List[str] = []
    if direction == "LONG":
        pairs = [
            (c1, f"C1 B({b:.2f}) > A({a:.2f}) = {b > a}"),
            (c2, f"C2 C({c:.2f}) < B({b:.2f}) = {c < b}"),
            (c3, f"C3 C({c:.2f}) > A({a:.2f}) = {c > a}"),
            (c4, f"C4 最新({latest:.2f}) > C({c:.2f}) = {latest > c}" if latest else "C4 —"),
        ]
    else:
        pairs = [
            (c1, f"C1 A({a:.2f}) > B({b:.2f}) = {a > b}"),
            (c2, f"C2 C({c:.2f}) > B({b:.2f}) = {c > b}"),
            (c3, f"C3 C({c:.2f}) < A({a:.2f}) = {c < a}"),
            (c4, f"C4 最新({latest:.2f}) < C({c:.2f}) = {latest < c}" if latest else "C4 —"),
        ]
    for ok, desc in pairs:
        if ok is False:
            descs.append(f"  ❌ {desc}")
    return descs


# ── 数据加载 ──────────────────────────────────────────────


def get_active_pairs(db: Database) -> List[tuple]:
    """"获取所有有数据结构记录的 (symbol, contract) 对（不含 symbol = contract 过滤）"""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT symbol, contract FROM futures_n_structures "
            "ORDER BY symbol, contract"
        ).fetchall()
    return [(r["symbol"], r["contract"]) for r in rows]


def get_latest_close(db: Database, symbol: str, contract: str,
                     timeframe: str) -> Optional[float]:
    """获取指定品种×周期的最新收盘价"""
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT close FROM futures_klines "
            "WHERE symbol=? AND contract=? AND timeframe=? "
            "ORDER BY timestamp DESC LIMIT 1",
            (symbol, contract, timeframe),
        ).fetchone()
    return row["close"] if row else None


def load_db_structures(db: Database) -> Dict[str, Dict[str, Any]]:
    """读取 DB 中所有活跃 N 型结构"""
    result: Dict[str, Dict[str, Any]] = {}
    dupes: set = set()
    key_count: Dict[str, int] = {}
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM futures_n_structures "
            "WHERE state NOT IN ('COMPLETED', 'IDLE') "
            "ORDER BY symbol, contract, timeframe, id DESC"
        ).fetchall()
    for r in rows:
        key = (r["symbol"], r["contract"], r["timeframe"])
        key_count[key] = key_count.get(key, 0) + 1
        if key not in result:
            result[key] = dict(r)
    for k, c in key_count.items():
        if c > 1:
            dupes.add(k)
    return result, dupes


# ── 验证单个品种×周期 ──────────────────────────────────────


def verify_one(db: Database, symbol: str, contract: str, tf: str,
               limit: int) -> dict:
    """验证单个品种×周期的 N 型结构标点。

    Returns:
        dict 包含验证结果，结构如 all_results[]。
    """
    # 1. 通过模块函数读极值点
    swing_points = _get_swing_points(db, symbol, contract, tf, limit=limit * 2)
    if len(swing_points) < 3:
        return {
            "symbol": symbol, "contract": contract, "tf": tf,
            "overall": "⚠️", "direction": "—",
            "a_price": None, "b_price": None, "c_price": None,
            "a_time": None, "b_time": None, "c_time": None,
            "latest": None,
            "conds": "—", "cond_details": {},
            "detail": f"极值点不足: {len(swing_points)}",
        }

    # 2. 合并连续同向极值点
    merged = _merge_same_type(swing_points)
    if len(merged) < 3:
        return {
            "symbol": symbol, "contract": contract, "tf": tf,
            "overall": "⚠️", "direction": "—",
            "a_price": None, "b_price": None, "c_price": None,
            "a_time": None, "b_time": None, "c_time": None,
            "latest": None,
            "conds": "—", "cond_details": {},
            "detail": f"merge后不足: {len(merged)}",
        }

    # 3. 前向非重叠扫描
    best = _find_n_structure_forward(merged)
    if best is None:
        return {
            "symbol": symbol, "contract": contract, "tf": tf,
            "overall": "❌", "direction": "—",
            "a_price": None, "b_price": None, "c_price": None,
            "a_time": None, "b_time": None, "c_time": None,
            "latest": None,
            "conds": "—", "cond_details": {},
            "detail": "算法无有效3点结构",
        }

    # 4. 获取最新价格
    latest = get_latest_close(db, symbol, contract, tf)

    d = best["direction"]
    a_px, b_px, c_px = best["a"]["price"], best["b"]["price"], best["c"]["price"]
    a_ts, b_ts, c_ts = best["a"]["timestamp"], best["b"]["timestamp"], best["c"]["timestamp"]

    # 5. 检查 4 条件
    conds = check_all(d, a_px, b_px, c_px, latest)
    ok = all(c is True for c in conds)

    details: List[str] = []
    if latest is None:
        details.append("  ⚠️ 无最新K线数据")
    elif not ok:
        details = fail_details(d, *conds, a_px, b_px, c_px, latest)

    # 6. 获取 swing points 序号
    a_idx = best.get("a_idx")
    c_idx = best.get("c_idx")

    return {
        "symbol": symbol, "contract": contract, "tf": tf,
        "overall": "✅" if ok else "❌",
        "direction": d,
        "a_price": round(a_px, 2),
        "b_price": round(b_px, 2),
        "c_price": round(c_px, 2),
        "a_time": a_ts,
        "b_time": b_ts,
        "c_time": c_ts,
        "a_time_str": fmt_ts(a_ts),
        "b_time_str": fmt_ts(b_ts),
        "c_time_str": fmt_ts(c_ts),
        "latest": round(latest, 2) if latest else None,
        "cond_c1": conds[0],
        "cond_c2": conds[1],
        "cond_c3": conds[2],
        "cond_c4": conds[3] if len(conds) > 3 else None,
        "conds": cond_symbols(conds),
        "detail": "\n".join(details),
        "a_idx": a_idx,
        "c_idx": c_idx,
    }


# ── 主流程 ────────────────────────────────────────────────


def main() -> None:
    db = Database(DB_PATH)
    pairs = get_active_pairs(db)
    db_structs, db_dupe_keys = load_db_structures(db)

    all_results: List[dict] = []
    fail_list: List[dict] = []
    pass_count = fail_count = na_count = 0
    sym_fails: Dict[str, int] = {}
    tf_fail_counts = {tf: {"c1": 0, "c2": 0, "c3": 0, "c4": 0}
                     for tf in TIMEFRAMES}

    print(f"🔍 开始验证 {len(pairs)} 个品种-合约对 × {len(TIMEFRAMES)} 周期 = {len(pairs) * len(TIMEFRAMES)} 条目...")
    print()

    for sym_idx, (sym, contract) in enumerate(pairs, 1):
        for tf in TIMEFRAMES:
            limit = DETECT_WINDOWS.get(tf, 40)
            res = verify_one(db, sym, contract, tf, limit)

            if res["overall"] == "⚠️":
                na_count += 1
            elif res["overall"] == "✅":
                pass_count += 1
            else:
                fail_count += 1
                sym_fails[sym] = sym_fails.get(sym, 0) + 1
                # 统计各周期各条件失败
                if latest := res.get("latest"):
                    conds = check_all(res["direction"],
                                      res["a_price"], res["b_price"],
                                      res["c_price"], latest)
                    for i, ck in enumerate(conds):
                        if ck is False:
                            tf_fail_counts[tf][f"c{i+1}"] += 1

            # 对比 DB 活跃结构
            db_key = (sym, contract, tf)
            db_entry = db_structs.get(db_key, {})
            res["db_direction"] = db_entry.get("direction", "—")
            res["db_state"] = db_entry.get("state", "—")
            res["db_dupe"] = db_key in db_dupe_keys

            # 获取极值点序列详情（用于调试）
            swing_points = _get_swing_points(db, sym, contract, tf, limit=limit * 2)
            merged = _merge_same_type(swing_points)
            res["swing_count"] = len(swing_points)
            res["merged_count"] = len(merged)

            all_results.append(res)
            if res["overall"] == "❌":
                fail_list.append(res)

            # 进度显示
            progress = f"  [{sym_idx}/{len(pairs)}] {sym}({contract}) {tf:3s} → {res['overall']}"
            if res["overall"] in ("✅", "❌"):
                progress += f"  dir={res['direction']}  A={res['a_price']}  B={res['b_price']}  C={res['c_price']}"
            if res["overall"] == "❌":
                progress += f"  | {res['conds']}"
            print(progress)

    db.close()

    # ── 统计 ────────────────────────────────────────────────
    total = len(all_results)
    print()
    print(f"✅ 验证完成")
    print(f"   通过: {pass_count}  失败: {fail_count}  N/A: {na_count}  总计: {total}")

    # ── 输出 JSON ───────────────────────────────────────────
    json_report = {
        "meta": {
            "generated_at": datetime.now(tz=CST).strftime("%Y-%m-%d %H:%M:%S %Z"),
            "pairs_count": len(pairs),
            "timeframes": TIMEFRAMES,
            "total_entries": total,
            "pass": pass_count,
            "fail": fail_count,
            "na": na_count,
        },
        "pairs": [[s, c] for s, c in pairs],
        "results": all_results,
        "fail_summary": {
            "by_symbol": dict(sorted(sym_fails.items(), key=lambda x: -x[1])),
            "by_timeframe": {
                tf: {
                    "total": sum(1 for r in all_results
                                 if r["tf"] == tf and r["overall"] == "❌"),
                    "by_condition": tf_fail_counts[tf],
                }
                for tf in TIMEFRAMES
            },
        },
    }
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)
    print(f"   📄 JSON: {OUTPUT_JSON}")

    # ── 输出 Markdown 报告 ─────────────────────────────────
    lines: List[str] = []
    def out(s: str = "") -> None:
        lines.append(s)

    out("# N 型结构算法全量验证报告 — P0 Step 1.1")
    out()
    out(f"> **生成时间**: {datetime.now(tz=CST).strftime('%Y-%m-%d %H:%M:%S')} CST")
    out(f">")
    out(f"> 验证范围: {len(pairs)} 个品种-合约对 × 4 周期 = {total} 条目")
    out(f"> 验证方法: 模块函数 `_get_swing_points()` → `_merge_same_type()` → `_find_n_structure_forward()`")
    out(f"> → 4 条件检查符合 User Directives 定义")
    out()

    # 整体统计
    out("## 📊 整体统计")
    out()
    out("| 状态 | 数量 | 占比 |")
    out("|------|------|------|")
    out(f"| ✅ 全部通过 | {pass_count} | {pass_count/total*100:.1f}% |")
    out(f"| ❌ 有失败条件 | {fail_count} | {fail_count/total*100:.1f}% |")
    out(f"| ⚠️ 数据不足 | {na_count} | {na_count/total*100:.1f}% |")
    out(f"| **总计** | **{total}** | **100%** |")
    out()

    # 按周期统计
    out("### 📈 按周期统计")
    out()
    out("| 周期 | 通过 | 失败 | N/A | 合计 | 通过率 |")
    out("|------|------|------|-----|------|--------|")
    for tf in TIMEFRAMES:
        tfr = [r for r in all_results if r["tf"] == tf]
        tp = sum(1 for r in tfr if r["overall"] == "✅")
        tf_ = sum(1 for r in tfr if r["overall"] == "❌")
        tna = sum(1 for r in tfr if r["overall"] == "⚠️")
        valid = tp + tf_
        pct = f"{tp/valid*100:.0f}%" if valid > 0 else "—"
        out(f"| {tf:3s} | {tp} | {tf_} | {tna} | {len(tfr)} | {pct} |")
    out()

    # 各周期条件分布
    out("**各周期失败条件分布:**")
    out()
    out("| 周期 | 失败总数 | C1 | C2 | C3 | C4 |")
    out("|------|----------|----|----|----|----|")
    for tf in TIMEFRAMES:
        c = tf_fail_counts[tf]
        total_tf_fails = sum(1 for r in all_results
                             if r["tf"] == tf and r["overall"] == "❌")
        out(f"| {tf:3s} | {total_tf_fails} | {c['c1']} | {c['c2']} | {c['c3']} | {c['c4']} |")
    out()

    # 失败品种统计
    if sym_fails:
        out("**失败品种按失败次数排序:**")
        out()
        out("| 品种 | 失败数 |")
        out("|------|--------|")
        for s, cnt in sorted(sym_fails.items(), key=lambda x: -x[1]):
            out(f"| {s} | {cnt} |")
        out()

    # 失败详情
    if fail_list:
        out("## ❌ 未通过验证的品种×周期")
        out()
        out(f"共 {len(fail_list)} 条:")
        out()
        for r in fail_list:
            out(f"### {r['symbol']} — {r['tf']}")
            out()
            out("| 指标 | 值 |")
            out("|------|-----|")
            out(f"| 算法方向 | {r['direction']} |")
            out(f"| A 价 | {fmt_price(r['a_price'])} @ {r.get('a_time_str', 'N/A')} |")
            out(f"| B 价 | {fmt_price(r['b_price'])} @ {r.get('b_time_str', 'N/A')} |")
            out(f"| C 价 | {fmt_price(r['c_price'])} @ {r.get('c_time_str', 'N/A')} |")
            out(f"| 最新价 | {fmt_price(r['latest'])} |")
            out(f"| 条件判定 | {r['conds']} |")
            out(f"| DB 方向 | {r['db_direction']} (状态: {r['db_state']}) |")
            out(f"| DB 重复行 | {'⚠️ 是' if r['db_dupe'] else '否'} |")
            out(f"| 极值点数量 | {r.get('swing_count', '?')} (merge 后: {r.get('merged_count', '?')}) |")
            out(f"| A 索引 | {r.get('a_idx', '—')} | C 索引 | {r.get('c_idx', '—')} |")
            out()

            # 极值点序列
            swing_points = _get_swing_points(
                Database(DB_PATH), r["symbol"], r.get("contract", r["symbol"]),
                r["tf"], limit=DETECT_WINDOWS.get(r["tf"], 40) * 2,
            )
            merged = _merge_same_type(swing_points)
            out(f"**极值点序列** (swing: {len(swing_points)}, merged: {len(merged)}):")
            out("```")
            for i, mp in enumerate(merged):
                marker = ""
                if r.get("a_idx") is not None and i == r["a_idx"]:
                    marker = " ← A"
                elif r.get("c_idx") is not None and i == r["c_idx"]:
                    marker = " ← C"
                out(f"  [{i:2d}] {mp['point_type']:6s} "
                    f"price={mp['price']:>8.2f} "
                    f"time={fmt_ts(mp['timestamp']):>12s}{marker}")
            out("```")
            out()

            out("**失败详情:**")
            out("```")
            out(r["detail"])
            out("```")
            out("---")
            out()

    # 完整验证矩阵
    out("## 📋 完整验证矩阵")
    out()
    out("| 品种 | 周期 | 方向 | A 价 | B 价 | C 价 | 最新 | 条件 | 判定 | DB 方向 | A 时间 | C 时间 |")
    out("|------|------|------|------|------|------|------|------|------|--------|--------|--------|")
    for r in all_results:
        if r["overall"] in ("✅", "❌"):
            bold = "**" if r["overall"] == "❌" else ""
            bold_close = "**" if r["overall"] == "❌" else ""
            out(f"| {bold}{r['symbol']:4s}{bold_close} | {r['tf']:3s} | {r['direction']:5s} "
                f"| {fmt_price_md(r['a_price'])} | {fmt_price_md(r['b_price'])} | {fmt_price_md(r['c_price'])} "
                f"| {fmt_price_md(r['latest'])} | {r['conds']} | {r['overall']} "
                f"| {r['db_direction']:5s} | {r.get('a_time_str', '—'):>10s} | {r.get('c_time_str', '—'):>10s} |")
        else:
            out(f"| {r['symbol']:4s} | {r['tf']:3s} | {'—':5s} "
                f"| {'—':>8s} | {'—':>8s} | {'—':>8s} "
                f"| {'—':>8s} | {'—':>6s} | {r['overall']} "
                f"| {'—':5s} | {'—':>10s} | {'—':>10s} |")
    out()

    # 模式识别分析
    out("## 🔍 模式识别分析")
    out()

    # 失败品种聚合
    if sym_fails:
        # 检查是否集中在特定品种
        sorted_syms = sorted(sym_fails.items(), key=lambda x: -x[1])
        out(f"**失败品种**: {len(sorted_syms)} 个品种有失败条目。")
        out()
        for s, cnt in sorted_syms:
            tf_detail = {}
            for r in fail_list:
                if r["symbol"] == s:
                    tf_detail[r["tf"]] = r["conds"]
            tf_str = ", ".join(f"{tf}({cond})" for tf, cond in tf_detail.items())
            out(f"- **{s}**: {cnt} 次失败 — {tf_str}")
        out()

    # 条件分布分析
    out("**条件失败分布分析**:")
    out()
    total_c_fails = {k: sum(tf_fail_counts[tf][k] for tf in TIMEFRAMES)
                     for k in ["c1", "c2", "c3", "c4"]}
    out(f"- C1 (第一笔方向): {total_c_fails['c1']} 次")
    out(f"- C2 (第二笔方向): {total_c_fails['c2']} 次")
    out(f"- C3 (C 不破 A):  {total_c_fails['c3']} 次")
    out(f"- C4 (最新价方向): {total_c_fails['c4']} 次")
    out()

    # 结论
    out("## 📌 结论")
    out()
    if fail_count == 0 and na_count == 0:
        out("✅ **所有品种 × 所有周期的 ABC 标点均满足 4 条判定条件，算法逻辑正确。**")
        out()
        out("可直接进入 Step 2 — 跨周期复验确认。")
    elif fail_count == 0 and na_count > 0:
        out(f"⚠️ **无失败条目，但有 {na_count} 条因数据不足无法验证。**")
        out()
        out("建议补充数据后重新验证。")
    elif fail_count <= 5:
        out(f"⚠️ **发现 {fail_count} 条标点失败的品种×周期组合，数量较少。**")
        out()
        out("建议：")
        out("1. 人工检查失败条目的极值点序列，确认是否因 swing point 质量导致")
        out("2. 如 swing point 正确则进入 Step 3 修复")
        out()
        if total_c_fails["c4"] == fail_count:
            out("> **注意：所有失败均来自 C4（最新价未突破 C 点）— 这通常是行情自然现象，非算法问题。**")
    else:
        out(f"🔴 **发现 {fail_count} 条标点失败的品种×周期组合。**")
        out()
        out("建议：")
        out("1. 优先排查 C4（最新价未突破 C 点）— 行情自然现象")
        out("2. 排除 C4 后，分析其余 C1/C2/C3 失败是否指向系统性算法偏差")
        out("3. 按计划进入 Step 3 修复")
    out()

    # 写入 Markdown 文件
    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    report_text = "\n".join(lines)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"   📄 MD:  {OUTPUT_MD}")


if __name__ == "__main__":
    main()