#!/usr/bin/env python3
"""
N 型标注跨周期不一致诊断脚本 — Step 1.1

对每个品种 × 每个周期（15m/1h/1d/1w），采集：
  - matrix 路径用的合约 vs klines API 用的合约是否一致
  - _get_active_n_structure() 返回的 A/B/C 价格和时间戳
  - 各周期有/无活跃结构的覆盖率

用法:
  cd projects/options_arbitrage_system
  uv run python scripts/debug/n_structure_annotation_debug.py

输出:
  - stdout: 诊断摘要
  - docs/qa/n-structure-annotation-diagnostic.md: 完整统计报告
"""

import json
import logging
import os
import sys
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# 将项目根加入 sys.path（确保模块可导入）
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _PROJECT_ROOT)

from config.settings import DB_PATH
from core.db import Database
from futures.shared import _get_active_n_structure as _get_active_ns
from futures.shared import normalize_n_timestamps

# ─── 引用 web/app.py 中的关键函数 ────────────────────────────────
# 为避免循环依赖，内联合约解析函数

def _clean_contract_n_prefix(contract: str) -> str:
    """清洗合约前缀: ag/nag2607 → ag2607, nag2607 → ag2607。"""
    import re
    c = contract or ""
    c = re.sub(r'^[A-Za-z0-9]+/', '', c)
    c = re.sub(r'^[nN]', '', c)
    return c


def _get_futures_contract(conn, symbol: str) -> str:
    """获取品种的合约代码（与 /api/klines 一致）。"""
    row = conn.execute(
        "SELECT contract FROM futures_signals WHERE symbol=? AND contract!='' ORDER BY created_at DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    if row and row["contract"]:
        return _clean_contract_n_prefix(row["contract"]).upper()
    row = conn.execute(
        "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    if row and row["contract"]:
        return _clean_contract_n_prefix(row["contract"]).upper()
    row = conn.execute(
        "SELECT contract FROM futures_klines WHERE symbol=? AND timeframe='1d' ORDER BY timestamp DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    return row["contract"] if row else ""


def _get_matrix_contract(conn, symbol: str) -> str:
    """获取品种在 matrix 路径用的合约（与 /api/matrix 一致）。

    优先级:
      1. futures_signals 最新信号的合约
      2. futures_n_structures 表最近的合约（无信号 fallback）
    """
    row = conn.execute(
        "SELECT contract FROM futures_signals WHERE symbol=? AND contract!='' ORDER BY created_at DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    if row and row["contract"]:
        return _clean_contract_n_prefix(row["contract"]).upper()
    row = conn.execute(
        "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    if row and row["contract"]:
        return _clean_contract_n_prefix(row["contract"]).upper()
    return ""


# ─── SECTORS（来自 web/app.py） ──────────────────────────────────

SECTORS = {
    "有色": ["CU", "AL", "ZN", "PB", "NI", "SN", "AO"],
    "贵金属": ["AU", "AG"],
    "黑色": ["RB", "HC", "I", "J", "JM", "SS", "SF", "SM"],
    "能源化工": ["BU", "FU", "LU", "SC", "RU", "NR", "BR", "TA", "MA", "FG", "SA", "UR", "PX", "EB", "EG", "PG", "PP", "V", "L", "SP", "SH"],
    "农产品": ["M", "Y", "A", "B", "P", "C", "CS", "JD", "LH", "CF", "SR", "AP", "CJ", "RM", "OI"],
    "新能源": ["SI", "LC"],
}

TIMEFRAMES = ["15m", "1h", "1d", "1w"]

SYMBOL_NAMES = {
    "CU": "沪铜", "AL": "沪铝", "ZN": "沪锌", "PB": "沪铅", "NI": "沪镍", "SN": "沪锡",
    "AU": "黄金", "AG": "白银", "RB": "螺纹钢", "HC": "热卷", "I": "铁矿", "J": "焦炭", "JM": "焦煤",
    "BU": "沥青", "FU": "燃油", "LU": "低硫燃油", "SC": "原油", "RU": "橡胶", "NR": "20号胶",
    "BR": "丁二烯", "SP": "纸浆", "SS": "不锈钢", "M": "豆粕", "Y": "豆油", "A": "豆一", "B": "豆二",
    "P": "棕榈油", "C": "玉米", "CS": "玉米淀粉", "JD": "鸡蛋", "LH": "生猪", "CF": "棉花",
    "SR": "白糖", "TA": "PTA", "MA": "甲醇", "FG": "玻璃", "SA": "纯碱", "UR": "尿素",
    "PX": "对二甲苯", "SM": "硅锰", "SF": "硅铁", "AP": "苹果", "CJ": "红枣", "RM": "菜粕",
    "OI": "菜油", "EB": "苯乙烯", "EG": "乙二醇", "PG": "LPG", "PP": "聚丙烯", "V": "PVC",
    "L": "塑料", "SH": "烧碱", "SI": "工业硅", "LC": "碳酸锂", "AO": "氧化铝",
    "PF": "花生仁", "PK": "花生", "PR": "聚丙烯",
}


def _collect_symbols():
    """从 SECTORS 收集所有唯一品种代码（保持顺序）。"""
    seen = set()
    symbols = []
    for sector, syms in SECTORS.items():
        for sym in syms:
            if sym not in seen:
                seen.add(sym)
                symbols.append(sym)
    return symbols


def _fmt_ts(ts: Optional[int]) -> str:
    """将时间戳格式化为可读时间。"""
    if ts is None:
        return "N/A"
    try:
        from datetime import datetime, timezone
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except (OverflowError, OSError):
        return str(ts)


def main():
    """
    主诊断流程：

    1. 连接到 DB
    2. 对每个品种 × 每个周期：
       a. 获取 matrix 合约 / klines 合约
       b. 比较是否一致
       c. 调用 _get_active_n_structure 获取 A/B/C 数据
    3. 输出统计报告
    """
    print("=" * 75)
    print("  N 型标注跨周期不一致 — 数据采集诊断")
    print("=" * 75)

    db = Database(DB_PATH)
    conn = db.get_conn()
    symbols = _collect_symbols()

    print(f"\n📋 品种总数: {len(symbols)}")
    print(f"📋 周期: {', '.join(TIMEFRAMES)}")

    # ─── 数据采集 ────────────────────────────────────────────────
    # 存储结构:
    #   results[sym][tf] = {
    #       "matrix_contract": str,
    #       "klines_contract": str,
    #       "contract_match": bool,
    #       "has_n_structure": bool,
    #       "n_dir": str | None,
    #       "n_state": str | None,
    #       "point_a": float | None,
    #       "point_b": float | None,
    #       "point_c": float | None,
    #       "point_a_time": int | None,
    #       "point_b_time": int | None,
    #       "point_c_time": int | None,
    #   }

    results: Dict[str, Dict[str, Dict[str, Any]]] = {}
    contract_mismatches: List[Dict[str, Any]] = []

    for sym in symbols:
        sym_results: Dict[str, Dict[str, Any]] = {}

        # 获取两路合约
        matrix_contract = _get_matrix_contract(conn, sym)
        klines_contract = _get_futures_contract(conn, sym)
        contract_match = matrix_contract == klines_contract

        if not contract_match:
            contract_mismatches.append({
                "symbol": sym,
                "matrix_contract": matrix_contract,
                "klines_contract": klines_contract,
            })

        for tf in TIMEFRAMES:
            info: Dict[str, Any] = {
                "matrix_contract": matrix_contract,
                "klines_contract": klines_contract,
                "contract_match": contract_match,
                "has_n_structure": False,
                "n_dir": None,
                "n_state": None,
                "point_a": None,
                "point_b": None,
                "point_c": None,
                "point_a_time": None,
                "point_b_time": None,
                "point_c_time": None,
            }

            # 用 klines 合约调用 _get_active_n_structure
            # （与弹窗实际行为一致）
            ns = None
            if klines_contract:
                try:
                    ns = _get_active_ns(db, sym, klines_contract, tf)
                except Exception as e:
                    print(f"  ⚠️ _get_active_n_structure error: {sym}/{tf} — {e}")

            if ns:
                info["has_n_structure"] = True
                info["n_dir"] = ns.get("direction")
                info["n_state"] = ns.get("state")
                info["point_a"] = ns.get("point_a_price")
                info["point_b"] = ns.get("point_b_price")
                info["point_c"] = ns.get("point_c_price")
                info["point_a_time"] = ns.get("point_a_time")
                info["point_b_time"] = ns.get("point_b_time")
                info["point_c_time"] = ns.get("point_c_time")

            sym_results[tf] = info

        results[sym] = sym_results

    # ─── 统计 ────────────────────────────────────────────────────
    total = len(symbols) * len(TIMEFRAMES)  # 理论最大单元数
    tf_stats: Dict[str, Dict[str, int]] = {}

    for tf in TIMEFRAMES:
        tf_stats[tf] = {
            "total": len(symbols),
            "with_n": 0,
            "without_n": 0,
            "contract_mismatch": 0,
        }

    for sym in symbols:
        for tf in TIMEFRAMES:
            info = results[sym][tf]
            if info["has_n_structure"]:
                tf_stats[tf]["with_n"] += 1
            else:
                tf_stats[tf]["without_n"] += 1
            if not info["contract_match"]:
                tf_stats[tf]["contract_mismatch"] += 1

    # 合约不一致统计
    mismatch_syms = set(m["symbol"] for m in contract_mismatches)
    contract_match_count = len(symbols) - len(mismatch_syms)
    contract_mismatch_count = len(mismatch_syms)

    # ─── 输出概要 ────────────────────────────────────────────────
    print(f"\n{'='*75}")
    print("  📊 诊断统计摘要")
    print(f"{'='*75}")

    print(f"\n── 合约解析一致性 ──")
    print(f"  品种总数:              {len(symbols)}")
    print(f"  合约一致 (matrix=klines): {contract_match_count}")
    print(f"  合约不一致:             {contract_mismatch_count}")

    if contract_mismatches:
        print(f"\n  合约不一致清单:")
        for m in contract_mismatches:
            print(f"    ❌ {m['symbol']:4s}: matrix='{m['matrix_contract']}' vs klines='{m['klines_contract']}'")
        # 显示样本合约数据以排查根因
        print(f"\n  合约不一致品种的 DB 样本:")
        for m in contract_mismatches[:5]:
            sym = m["symbol"]
            rows = conn.execute(
                "SELECT contract, created_at FROM futures_signals WHERE symbol=? AND contract!='' ORDER BY created_at DESC LIMIT 3",
                (sym,),
            ).fetchall()
            print(f"\n  {sym}:")
            for r in rows:
                print(f"    signals: {r['contract']:20s} (created_at={r['created_at']})")
            rows = conn.execute(
                "SELECT contract, updated_at FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 3",
                (sym,),
            ).fetchall()
            for r in rows:
                print(f"    n_structs: {r['contract']:20s} (updated_at={r['updated_at']})")

    print(f"\n── 各周期 N 型结构覆盖率 ──")
    print(f"  {'周期':6s} | {'总数':6s} | {'有结构':8s} | {'无结构':8s} | {'覆盖率':8s} | {'合约不一致':10s}")
    print(f"  {'-'*6}-+-{'-'*6}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}")
    for tf in TIMEFRAMES:
        s = tf_stats[tf]
        cov = s["with_n"] / max(s["total"], 1) * 100
        print(f"  {tf:6s} | {s['total']:6d} | {s['with_n']:8d} | {s['without_n']:8d} | {cov:7.1f}% | {s['contract_mismatch']:10d}")

    print(f"\n── 品种级 N 型结构覆盖率（跨周期） ──")
    sym_coverage = {}
    for sym in symbols:
        n_count = sum(1 for tf in TIMEFRAMES if results[sym][tf]["has_n_structure"])
        sym_coverage[sym] = n_count
        bar = "█" * n_count + "░" * (len(TIMEFRAMES) - n_count)
        print(f"  {sym:4s} [{bar}] {n_count}/{len(TIMEFRAMES)}")

    # 识别"部分标注"的品种（1-3 个周期有 N 型结构）
    partial = {sym: cnt for sym, cnt in sym_coverage.items() if 0 < cnt < len(TIMEFRAMES)}
    full = {sym: cnt for sym, cnt in sym_coverage.items() if cnt == len(TIMEFRAMES)}
    zero = {sym: cnt for sym, cnt in sym_coverage.items() if cnt == 0}

    print(f"\n  全周期标注 ({len(full)}): {', '.join(sorted(full.keys()))}")
    print(f"  部分标注 ({len(partial)}): {', '.join(sorted(partial.keys()))}")
    print(f"  无标注 ({len(zero)}): {', '.join(sorted(zero.keys()))}")

    # ─── 详细检查：部分标注品种的 N 结构细节 ─────────────────────
    print(f"\n{'='*75}")
    print("  🔍 部分标注品种 — 各周期 N 结构详细数据")
    print(f"{'='*75}")

    for sym in sorted(partial.keys()):
        print(f"\n── {sym} ({SYMBOL_NAMES.get(sym, '')}) ──")
        print(f"  Matrix contract: '{results[sym]['15m']['matrix_contract']}'")
        print(f"  Klines contract: '{results[sym]['15m']['klines_contract']}'")
        print(f"  合约匹配: {'✅' if results[sym]['15m']['contract_match'] else '❌'}")
        print(f"  {'周期':6s} | {'方向':7s} | {'状态':12s} | {'A价':10s} | {'B价':10s} | {'C价':10s} | {'A时间':24s} | {'B时间':24s} | {'C时间':24s}")
        print(f"  {'-'*6}-+-{'-'*7}-+-{'-'*12}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*24}-+-{'-'*24}-+-{'-'*24}")
        for tf in TIMEFRAMES:
            info = results[sym][tf]
            marker = "✅" if info["has_n_structure"] else "⬜"
            a_ts = _fmt_ts(info["point_a_time"])
            b_ts = _fmt_ts(info["point_b_time"])
            c_ts = _fmt_ts(info["point_c_time"])
            a_p = f"{info['point_a']:.2f}" if info["point_a"] else "N/A"
            b_p = f"{info['point_b']:.2f}" if info["point_b"] else "N/A"
            c_p = f"{info['point_c']:.2f}" if info["point_c"] else "N/A"
            print(f"  {marker} {tf:4s} | {str(info['n_dir'] or 'N/A'):7s} | {str(info['n_state'] or 'N/A'):12s} | {a_p:>10s} | {b_p:>10s} | {c_p:>10s} | {a_ts:24s} | {b_ts:24s} | {c_ts:24s}")

    # ─── 全标注品种的 ABC 参数概览 ──────────────────────────────
    print(f"\n{'='*75}")
    print("  📋 全标注品种各周期 ABC 价格与方向")
    print(f"{'='*75}")

    for sym in sorted(full.keys()):
        print(f"\n── {sym} ({SYMBOL_NAMES.get(sym, '')}) ──")
        for tf in TIMEFRAMES:
            info = results[sym][tf]
            dir_str = info["n_dir"] or "?"
            a_p = f"{info['point_a']:.2f}" if info["point_a"] else "?"
            b_p = f"{info['point_b']:.2f}" if info["point_b"] else "?"
            c_p = f"{info['point_c']:.2f}" if info["point_c"] else "?"
            print(f"  {tf:4s} [{dir_str:5s}] A={a_p:>10s} → B={b_p:>10s} → C={c_p:>10s}")

    # ─── 检查方向一致性 ──────────────────────────────────────────
    print(f"\n{'='*75}")
    print("  🔄 跨周期方向一致性检查")
    print(f"{'='*75}")

    dir_inconsistent = []
    for sym in sorted(symbols):
        dirs = {}
        for tf in TIMEFRAMES:
            info = results[sym][tf]
            if info["has_n_structure"] and info["n_dir"]:
                dirs[tf] = info["n_dir"]
        unique_dirs = set(dirs.values())
        if len(unique_dirs) > 1:
            dir_inconsistent.append((sym, dirs))
            print(f"\n  ❌ {sym}: {' | '.join(f'{tf}={d}' for tf, d in sorted(dirs.items()))}")
        elif len(unique_dirs) == 1:
            pass  # 一致的不需要显示

    if not dir_inconsistent:
        print(f"  ✅ 所有有结构的品种跨周期方向一致")

    # ─── H1 合约不一致诊断 ──────────────────────────────────────
    print(f"\n{'='*75}")
    print("  🩺 H1 假设诊断：合约解析不一致")
    print(f"{'='*75}")

    if contract_mismatch_count == 0:
        print(f"\n  ✅ 所有品种 matrix 与 klines 合约解析一致 — H1 不成立")
        print(f"     N 型标注不一致的原因不是合约解析差异")
    else:
        print(f"\n  ⚠️ 发现 {contract_mismatch_count} 个品种合约解析不一致")
        print(f"     H1 可能是部分品种标注不一致的根因")
        print(f"\n     建议排查方向:")
        print(f"     1. _get_futures_contract() 的 fallback 链（signals→n_structs→klines）")
        print(f"        是否与 matrix 的 fallback 链行为不一致")
        print(f"     2. 两路径最后一条记录的先后顺序差异")
        print(f"     3. _clean_contract_n_prefix 的清洗结果是否一致")

    # ─── H3 C4 过滤差异诊断 ──────────────────────────────────────
    print(f"\n{'='*75}")
    print("  🩺 H3 假设诊断：C4 条件过滤差异")
    print(f"{'='*75}")

    # 对无 N 型结构的 (sym, tf) 对，检查 DB 是否有 LEG3 行被 C4 过滤
    c4_filtered = []
    for sym in symbols:
        for tf in TIMEFRAMES:
            info = results[sym][tf]
            if info["has_n_structure"]:
                continue
            # 检查是否有 LEG3 行但被条件 4 过滤
            contract = info["klines_contract"] or ""
            if not contract:
                continue
            row = conn.execute(
                """SELECT id, direction, state, point_a_price, point_b_price, point_c_price,
                          point_a_time, point_b_time, point_c_time, updated_at
                   FROM futures_n_structures
                   WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED'
                   ORDER BY updated_at DESC LIMIT 1""",
                (sym, contract, tf),
            ).fetchone()
            if row:
                ns = dict(row)
                # 检查 C4: LONG 最新价 <= C - eps → 被过滤
                last_kline = conn.execute(
                    "SELECT close FROM futures_klines WHERE symbol=? AND contract=? AND timeframe=? ORDER BY timestamp DESC LIMIT 1",
                    (sym, contract, tf),
                ).fetchone()
                if last_kline and ns.get("point_c_price"):
                    c_price = ns["point_c_price"]
                    eps = max(0.5, c_price * 0.001)
                    direction = ns["direction"]
                    lk = last_kline["close"]
                    if direction == "LONG" and lk <= c_price - eps:
                        c4_filtered.append((sym, tf, "LONG", c_price, lk))
                    elif direction == "SHORT" and lk >= c_price + eps:
                        c4_filtered.append((sym, tf, "SHORT", c_price, lk))

    print(f"\n  被 C4 过滤的 (品种, 周期) 数: {len(c4_filtered)}")
    if c4_filtered:
        print(f"  前 20 个:")
        for sym, tf, dir_, cp, lp in c4_filtered[:20]:
            print(f"    {sym:4s} {tf:4s} [{dir_:5s}] C价={cp:.2f} 最新价={lp:.2f}")
        # 按周期统计
        tf_c4 = defaultdict(int)
        for sym, tf, dir_, cp, lp in c4_filtered:
            tf_c4[tf] += 1
        print(f"\n  按周期统计:")
        for tf in TIMEFRAMES:
            print(f"    {tf}: {tf_c4.get(tf, 0)}")

    # ─── 输出报告到文件 ──────────────────────────────────────────
    report_path = os.path.join(_PROJECT_ROOT, "..", "docs", "qa", "n-structure-annotation-diagnostic.md")
    report_path = os.path.normpath(report_path)

    print(f"\n{'='*75}")
    print(f"  📝 正在写诊断报告: {report_path}")
    print(f"{'='*75}")

    _write_report(report_path, symbols, TIMEFRAMES, results, tf_stats,
                  contract_mismatches, contract_match_count, contract_mismatch_count,
                  partial, full, zero, sym_coverage, dir_inconsistent, c4_filtered)

    conn.close()
    print(f"\n✅ 诊断完成")


def _write_report(report_path: str, symbols: List[str], TIMEFRAMES: List[str],
                  results: Dict, tf_stats: Dict, contract_mismatches: List,
                  contract_match_count: int, contract_mismatch_count: int,
                  partial: Dict, full: Dict, zero: Dict, sym_coverage: Dict,
                  dir_inconsistent: List, c4_filtered: list):
    """将诊断结果写入 Markdown 报告文件。"""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = []
    lines.append("# N 型标注跨周期不一致 — 诊断报告")
    lines.append("")
    lines.append(f"**生成时间**: {now}")
    lines.append(f"**脚本**: `scripts/debug/n_structure_annotation_debug.py`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 数据采集总览")
    lines.append("")
    lines.append(f"- **品种总数**: {len(symbols)}")
    lines.append(f"- **周期**: {', '.join(TIMEFRAMES)}")
    lines.append(f"- **理论最大单元数**: {len(symbols) * len(TIMEFRAMES)}")
    lines.append("")

    # ─── 合约一致性 ───
    lines.append("## 1. 合约解析一致性（H1 检查）")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|----|")
    lines.append(f"| 品种总数 | {len(symbols)} |")
    lines.append(f"| 合约一致 (matrix=klines) | {contract_match_count} |")
    lines.append(f"| 合约不一致 | {contract_mismatch_count} |")
    lines.append("")

    if contract_mismatches:
        lines.append("### 合约不一致清单")
        lines.append("")
        lines.append(f"| 品种 | matrix 合约 | klines 合约 |")
        lines.append(f"|------|------------|-------------|")
        for m in contract_mismatches:
            lines.append(f"| {m['symbol']} | `{m['matrix_contract']}` | `{m['klines_contract']}` |")
        lines.append("")

    lines.append("### H1 结论")
    if contract_mismatch_count == 0:
        lines.append("")
        lines.append("> ✅ **H1 不成立**: 所有品种 matrix 与 klines 合约解析一致。")
        lines.append("> N 型标注不一致的根因不在合约解析层。")
    else:
        lines.append("")
        lines.append(f"> ⚠️ **H1 部分成立**: {contract_mismatch_count} 个品种合约解析不一致。")
        lines.append("> 可能是部分品种标注不一致的根因。")
    lines.append("")

    # ─── 覆盖率 ───
    lines.append("## 2. 各周期 N 型结构覆盖率")
    lines.append("")
    lines.append(f"| 周期 | 总数 | 有结构 | 无结构 | 覆盖率 | 合约不一致 |")
    lines.append(f"|------|------|--------|--------|--------|------------|")
    for tf in TIMEFRAMES:
        s = tf_stats[tf]
        cov = s["with_n"] / max(s["total"], 1) * 100
        lines.append(f"| {tf} | {s['total']} | {s['with_n']} | {s['without_n']} | {cov:.1f}% | {s['contract_mismatch']} |")
    lines.append("")

    lines.append("## 3. 品种级覆盖率")
    lines.append("")
    lines.append(f"| 状态 | 数量 | 品种 |")
    lines.append(f"|------|------|------|")
    lines.append(f"| 全周期标注 ({len(TIMEFRAMES)}/{len(TIMEFRAMES)}) | {len(full)} | {', '.join(sorted(full.keys()))} |")
    lines.append(f"| 部分标注 (1-{len(TIMEFRAMES)-1}/{len(TIMEFRAMES)}) | {len(partial)} | {', '.join(sorted(partial.keys()))} |")
    lines.append(f"| 无标注 (0/{len(TIMEFRAMES)}) | {len(zero)} | {', '.join(sorted(zero.keys()))} |")
    lines.append("")

    # ─── 部分标注品种详细数据 ───
    if partial:
        lines.append("## 4. 部分标注品种详细诊断")
        lines.append("")
        for sym in sorted(partial.keys()):
            lines.append(f"### {sym} — 部分周期标注")
            lines.append("")
            info_15m = results[sym]["15m"]
            lines.append(f"- Matrix contract: `{info_15m['matrix_contract']}`")
            lines.append(f"- Klines contract: `{info_15m['klines_contract']}`")
            lines.append(f"- 合约匹配: {'✅' if info_15m['contract_match'] else '❌'}")
            lines.append("")
            lines.append(f"| 周期 | 有结构 | 方向 | 状态 | A 价 | B 价 | C 价 | A 时间 | B 时间 | C 时间 |")
            lines.append(f"|------|--------|------|------|------|------|------|--------|--------|--------|")
            for tf in TIMEFRAMES:
                info = results[sym][tf]
                marker = "✅" if info["has_n_structure"] else "⬜"
                a_p = f"{info['point_a']:.2f}" if info["point_a"] else "-"
                b_p = f"{info['point_b']:.2f}" if info["point_b"] else "-"
                c_p = f"{info['point_c']:.2f}" if info["point_c"] else "-"
                a_ts = _fmt_ts(info["point_a_time"])
                b_ts = _fmt_ts(info["point_b_time"])
                c_ts = _fmt_ts(info["point_c_time"])
                lines.append(f"| {tf} | {marker} | {info['n_dir'] or '-'} | {info['n_state'] or '-'} | {a_p} | {b_p} | {c_p} | {a_ts} | {b_ts} | {c_ts} |")
            lines.append("")

    # ─── 方向一致性 ───
    lines.append("## 5. 跨周期方向一致性")
    lines.append("")
    if dir_inconsistent:
        lines.append(f"### ⚠️ 发现 {len(dir_inconsistent)} 个品种跨周期方向不一致")
        lines.append("")
        lines.append(f"| 品种 | 方向分布 |")
        lines.append(f"|------|----------|")
        for sym, dirs in dir_inconsistent:
            dir_str = " | ".join(f"{tf}={d}" for tf, d in sorted(dirs.items()))
            lines.append(f"| {sym} | {dir_str} |")
    else:
        lines.append("✅ 所有有结构的品种跨周期方向一致。")
    lines.append("")

    # ─── C4 过滤 ───
    lines.append("## 6. C4 过滤差异诊断（H3 检查）")
    lines.append("")
    tf_c4 = defaultdict(int)
    for sym, tf, dir_, cp, lp in c4_filtered:
        tf_c4[tf] += 1
    lines.append(f"被 C4 过滤的 (品种, 周期) 总数: **{len(c4_filtered)}**")
    lines.append("")
    lines.append(f"| 周期 | C4 过滤数 |")
    lines.append(f"|------|-----------|")
    for tf in TIMEFRAMES:
        lines.append(f"| {tf} | {tf_c4.get(tf, 0)} |")
    lines.append("")

    if c4_filtered:
        lines.append("### C4 过滤样本（前 20）")
        lines.append("")
        lines.append(f"| 品种 | 周期 | 方向 | C 价 | 最新价 |")
        lines.append(f"|------|------|------|------|--------|")
        for sym, tf, dir_, cp, lp in c4_filtered[:20]:
            lines.append(f"| {sym} | {tf} | {dir_} | {cp:.2f} | {lp:.2f} |")
        lines.append("")

    # ─── 初步判断 ───
    lines.append("## 7. 初步判断")
    lines.append("")

    # 自动给出初步判断
    judgments = []
    if contract_mismatch_count > 0:
        judgments.append(f"- **H1 （合约不一致）**: ❌ 发现 {contract_mismatch_count} 个品种不一致 → 可解释部分品种的标注偏差")
    else:
        judgments.append(f"- **H1 （合约不一致）**: ✅ 所有合约一致 → H1 不成立，标注不一致另有根因")

    if len(c4_filtered) > 0:
        c4_by_tf = ", ".join(f"{tf}={tf_c4.get(tf,0)}" for tf in TIMEFRAMES)
        judgments.append(f"- **H3 （C4 过滤波动）**: ⚠️ 发现 {len(c4_filtered)} 个 (品种×周期) 被 C4 过滤 ({c4_by_tf}) → 可解释无标注现象")
    else:
        judgments.append(f"- **H3 （C4 过滤波动）**: ✅ 无 C4 过滤 → 无标注另有原因")

    # 部分标注品种的合约一致性交叉检查
    partial_mismatch = sum(1 for sym in partial if not results[sym]["15m"]["contract_match"])
    if partial:
        judgments.append(f"- **部分标注品种 ({len(partial)}) 中合约不一致数**: {partial_mismatch}")
        if partial_mismatch > 0:
            judgments.append(f"  → 合约不一致可能解释了部分品种的'部分无标注'")
        else:
            judgments.append(f"  → 合约不一致不能解释'部分无标注'，需排查 H2/H4")

    for j in judgments:
        lines.append(j)
    lines.append("")

    # ─── 后续步骤建议 ───
    lines.append("## 8. 后续建议")
    lines.append("")
    lines.append("### Step 2 — 时间戳对齐验证（H2 检查）")
    lines.append("")
    lines.append("对部分标注品种（优先选合约一致的品种），检查：")
    lines.append("1. K 线 bar 时间戳的前 3 个和后 3 个样本")
    lines.append("2. N 结构 A/B/C 时间戳与 K 线 bar 的匹配度")
    lines.append("3. 1d/1w 周期时间戳归一化是否与 K 线 bar 对齐")
    lines.append("4. `findBarForNPoint()` 能否正确定位到预期 bar")
    lines.append("")
    lines.append("### Step 3 — 根因定论 + 修复方案")
    lines.append("")
    lines.append("基于 Step 1 和 Step 2 的数据确定根因，给出修复方案。")
    lines.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  ✅ 报告已写入: {report_path}")


if __name__ == "__main__":
    main()
