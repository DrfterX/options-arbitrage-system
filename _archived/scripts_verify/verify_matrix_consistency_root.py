#!/usr/bin/env python3
"""
A.3 全量交叉比对验证 — Matrix 数据 vs Klines 弹窗 N 型结构数据

验证目标：
1. 对每个品种×周期，Matrix 中的 N 型结构数据与 /api/klines 返回的是否一致
2. 计算差异类型和数量
3. 确认 A.1/A.2 修复后，Cat1（Matrix 有数据但弹窗不可绘制）和 Cat2（方向/ABC 不一致）是否消除

输出: docs/qa/n-structure-matrix-filter-verify.md
"""

import os, sys, json, sqlite3, time as time_module, re
from datetime import datetime, timezone, timedelta

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from futures.shared import _get_active_n_structure
from futures.n_structure import _determine_overall_direction, _merge_same_type, _find_n_structure_forward
from core.db import Database

# ── 从 web/app.py 内联（避免 Flask 初始化触发缺失依赖） ──

SYMBOL_NAMES = {
    "CU":"沪铜","AL":"沪铝","ZN":"沪锌","PB":"沪铅","NI":"沪镍","SN":"沪锡",
    "AU":"黄金","AG":"白银","RB":"螺纹钢","HC":"热卷","I":"铁矿","J":"焦炭","JM":"焦煤",
    "BU":"沥青","FU":"燃油","LU":"低硫燃油","SC":"原油","RU":"橡胶","NR":"20号胶",
    "BR":"丁二烯","SP":"纸浆","SS":"不锈钢","M":"豆粕","Y":"豆油","A":"豆一","B":"豆二",
    "P":"棕榈油","C":"玉米","CS":"玉米淀粉","JD":"鸡蛋","LH":"生猪","CF":"棉花",
    "SR":"白糖","TA":"PTA","MA":"甲醇","FG":"玻璃","SA":"纯碱","UR":"尿素",
    "PX":"对二甲苯","SM":"硅锰","SF":"硅铁","AP":"苹果","CJ":"红枣","RM":"菜粕",
    "OI":"菜油","EB":"苯乙烯","EG":"乙二醇","PG":"LPG","PP":"聚丙烯","V":"PVC",
    "L":"塑料","SH":"烧碱","SI":"工业硅","LC":"碳酸锂","AO":"氧化铝",
}

SECTORS = {
    "有色金属":{"CU","AL","ZN","PB","NI","SN","AO"},
    "贵金属":{"AU","AG"},
    "黑色系":{"RB","HC","I","J","JM","SS","SM","SF"},
    "能源":{"BU","FU","LU","SC"},
    "化工":{"TA","MA","SA","UR","PX","EB","EG","PG","PP","V","L","SH","BR"},
    "农产品":{"M","Y","A","B","P","C","CS","JD","LH","RM","OI","CF","SR","AP","CJ"},
    "橡胶":{"RU","NR"},
    "玻璃建材":{"FG"},
    "新能源":{"SI","LC"},
}

def _clean_contract_n_prefix(contract: str) -> str:
    """清洗合约前缀: ag/nag2607 → ag2607, nag2607 → ag2607。"""
    c = contract or ""
    c = re.sub(r'^[A-Za-z0-9]+/', '', c)
    c = re.sub(r'^[nN]', '', c)
    return c

CST = timezone(timedelta(hours=8))
TIMEFRAMES = ["15m", "1h", "1d", "1w"]

def fmt_ts(ts):
    if not ts:
        return "N/A"
    return datetime.fromtimestamp(ts, tz=CST).strftime("%m-%d %H:%M")

def fmt_price(p):
    if p is None:
        return "N/A"
    return f"{p:.2f}"

def get_contract_from_n_structures(db, sym):
    """从 n_structures 表获取品种的最新合约。"""
    conn = db.get_conn()
    row = conn.execute(
        "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
        (sym,),
    ).fetchone()
    return row["contract"] if row and row["contract"] else ""

def get_contract_from_klines(db, sym):
    """从 klines 表获取品种的主力合约（与 _get_futures_contract 一致）。"""
    conn = db.get_conn()
    row = conn.execute(
        "SELECT contract FROM futures_klines WHERE symbol=? AND timeframe='1d' ORDER BY timestamp DESC LIMIT 1",
        (sym,),
    ).fetchone()
    return row["contract"] if row else ""

def get_matrix_structures(db):
    """模拟 Matrix 的数据获取逻辑，返回 {symbol: {tf: struct}}。"""
    conn = db.get_conn()

    # 最新信号
    rows = conn.execute('''
        SELECT s.symbol, s.contract, s.direction, s.score
        FROM futures_signals s
        INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
            ON s.symbol=l.symbol AND s.created_at=l.mt
    ''').fetchall()
    signals = {}
    for r in rows:
        d = dict(r)
        signals[d["symbol"]] = {
            "contract": d["contract"], "dir": d["direction"],
            "score": round(d["score"], 2) if d["score"] else 0,
        }

    # 信号合约映射
    signal_contracts = {}
    for sym, info in signals.items():
        c = _clean_contract_n_prefix(info.get("contract", "")).upper()
        if c:
            signal_contracts[sym] = c

    # 补全缺合约品种
    for sym in signals:
        if sym not in signal_contracts or not signal_contracts[sym]:
            row = conn.execute(
                "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
                (sym,),
            ).fetchone()
            if row and row["contract"]:
                signal_contracts[sym] = _clean_contract_n_prefix(row["contract"]).upper()

    # 查询 N 型结构
    structures = {}
    for sym, contract in signal_contracts.items():
        for tf in TIMEFRAMES:
            ns = _get_active_n_structure(db, sym, contract, tf)
            if ns:
                structures.setdefault(sym, {})[tf] = {
                    "contract": contract,
                    "dir": ns["direction"], "state": ns["state"],
                    "a": ns["point_a_price"], "b": ns["point_b_price"], "c": ns["point_c_price"],
                    "at": ns["point_a_time"], "bt": ns["point_b_time"], "ct": ns["point_c_time"],
                }

    # 对无信号但有活跃 N 型结构的品种也纳入
    for sector_name, symbols in SECTORS.items():
        for sym in symbols:
            if sym in signals or sym in structures:
                continue
            row = conn.execute(
                "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
                (sym,),
            ).fetchone()
            if not row or not row["contract"]:
                continue
            contract = _clean_contract_n_prefix(row["contract"]).upper()
            for tf in TIMEFRAMES:
                ns = _get_active_n_structure(db, sym, contract, tf)
                if ns:
                    structures.setdefault(sym, {})[tf] = {
                        "contract": contract,
                        "dir": ns["direction"], "state": ns["state"],
                        "a": ns["point_a_price"], "b": ns["point_b_price"], "c": ns["point_c_price"],
                        "at": ns["point_a_time"], "bt": ns["point_b_time"], "ct": ns["point_c_time"],
                    }

    return structures, signals

def get_klines_structures(db):
    """模拟 Klines API 的数据获取逻辑，返回 {symbol: {tf: struct}}。"""


    structures = {}
    for sector_name, symbols in SECTORS.items():
        for sym in symbols:
            contract = get_contract_from_klines(db, sym)
            if not contract:
                continue
            for tf in TIMEFRAMES:
                ns = _get_active_n_structure(db, sym, contract, tf)
                if ns:
                    structures.setdefault(sym, {})[tf] = {
                        "contract": contract,
                        "dir": ns["direction"], "state": ns["state"],
                        "a": ns["point_a_price"], "b": ns["point_b_price"], "c": ns["point_c_price"],
                        "at": ns["point_a_time"], "bt": ns["point_b_time"], "ct": ns["point_c_time"],
                    }
            # 有些品种 klines 表可能没有合约记录，尝试从 n_structures 取
            if sym not in structures:
                contract2 = get_contract_from_n_structures(db, sym)
                if contract2 and contract2 != contract:
                    for tf in TIMEFRAMES:
                        ns = _get_active_n_structure(db, sym, contract2, tf)
                        if ns:
                            structures.setdefault(sym, {})[tf] = {
                                "contract": contract2,
                                "dir": ns["direction"], "state": ns["state"],
                                "a": ns["point_a_price"], "b": ns["point_b_price"], "c": ns["point_c_price"],
                                "at": ns["point_a_time"], "bt": ns["point_b_time"], "ct": ns["point_c_time"],
                            }

    return structures

def compare_structures(matrix_structs, klines_structs):
    """
    比较 Matrix vs Klines 的 N 型结构数据。
    返回差异列表。
    """
    all_symbols = set(matrix_structs.keys()) | set(klines_structs.keys())
    all_tfs = TIMEFRAMES

    differences = []
    cat1 = 0  # Matrix 有但 Klines 没有
    cat2 = 0  # 方向/ABC 不一致
    cat3 = 0  # Klines 有但 Matrix 没有
    match = 0  # 完全一致

    for sym in sorted(all_symbols):
        for tf in all_tfs:
            m = matrix_structs.get(sym, {}).get(tf)
            k = klines_structs.get(sym, {}).get(tf)

            if m and not k:
                cat1 += 1
                differences.append({
                    "type": "CAT1_Matrix有Klines无",
                    "symbol": sym, "tf": tf,
                    "matrix_contract": m.get("contract", ""),
                    "klines_contract": klines_structs.get(sym, {}).get(list(klines_structs.get(sym, {}).keys())[0], {}).get("contract", "") if klines_structs.get(sym) else "",
                    "detail": f"Matrix: {m['dir']} A={fmt_price(m['a'])} B={fmt_price(m['b'])} C={fmt_price(m['c'])} | Klines: 无结构",
                })
            elif k and not m:
                cat3 += 1
                differences.append({
                    "type": "CAT3_Klines有Matrix无",
                    "symbol": sym, "tf": tf,
                    "matrix_contract": matrix_structs.get(sym, {}).get(list(matrix_structs.get(sym, {}).keys())[0], {}).get("contract", "") if matrix_structs.get(sym) else "",
                    "klines_contract": k.get("contract", ""),
                    "detail": f"Klines: {k['dir']} A={fmt_price(k['a'])} B={fmt_price(k['b'])} C={fmt_price(k['c'])} | Matrix: 无结构",
                })
            elif m and k:
                # 比较方向
                dir_match = m["dir"] == k["dir"]
                # 比较 ABC 价格
                a_match = abs(m["a"] - k["a"]) < 0.01 if m["a"] and k["a"] else (m["a"] == k["a"])
                b_match = abs(m["b"] - k["b"]) < 0.01 if m["b"] and k["b"] else (m["b"] == k["b"])
                c_match = abs(m["c"] - k["c"]) < 0.01 if m["c"] and k["c"] else (m["c"] == k["c"])

                if dir_match and a_match and b_match and c_match:
                    match += 1
                else:
                    cat2 += 1
                    issues = []
                    if not dir_match:
                        issues.append(f"dir: {m['dir']}≠{k['dir']}")
                    if not a_match:
                        issues.append(f"A: {fmt_price(m['a'])}≠{fmt_price(k['a'])}")
                    if not b_match:
                        issues.append(f"B: {fmt_price(m['b'])}≠{fmt_price(k['b'])}")
                    if not c_match:
                        issues.append(f"C: {fmt_price(m['c'])}≠{fmt_price(k['c'])}")
                    differences.append({
                        "type": "CAT2_数据不一致",
                        "symbol": sym, "tf": tf,
                        "matrix_contract": m.get("contract", ""),
                        "klines_contract": k.get("contract", ""),
                        "issues": issues,
                        "detail": f"Matrix: {m['dir']} A={fmt_price(m['a'])} B={fmt_price(m['b'])} C={fmt_price(m['c'])} | "
                                  f"Klines: {k['dir']} A={fmt_price(k['a'])} B={fmt_price(k['b'])} C={fmt_price(k['c'])} | "
                                  f"差异: {'; '.join(issues)}",
                    })

    return {
        "match": match,
        "cat1": cat1,
        "cat2": cat2,
        "cat3": cat3,
        "total": match + cat1 + cat2 + cat3,
        "differences": differences,
    }

def main():
    db_path = os.path.join(PROJECT_ROOT, "trading_system.db")
    db = Database(db_path)

    print("=" * 70)
    print("A.3 全量交叉比对验证 — Matrix vs Klines N 型结构一致性")
    print("=" * 70)

    # Step 1: 获取 Matrix 数据结构
    print("\n[1/3] 获取 Matrix 矩阵数据结构...")
    start = time_module.time()
    matrix_structs, signals = get_matrix_structures(db)
    matrix_time = time_module.time() - start
    matrix_count = sum(len(tfs) for tfs in matrix_structs.values())
    print(f"  → {len(matrix_structs)} 个品种, {matrix_count} 个周期单元格")
    print(f"  → 耗时: {matrix_time:.1f}s")

    # Step 2: 获取 Klines 数据结构
    print("\n[2/3] 获取 Klines 弹窗数据结构...")
    start = time_module.time()
    klines_structs = get_klines_structures(db)
    klines_time = time_module.time() - start
    klines_count = sum(len(tfs) for tfs in klines_structs.values())
    print(f"  → {len(klines_structs)} 个品种, {klines_count} 个周期单元格")
    print(f"  → 耗时: {klines_time:.1f}s")

    # Step 3: 比较
    print("\n[3/3] 交叉比对分析...")
    result = compare_structures(matrix_structs, klines_structs)

    # 输出报告
    total_possible = len(set(list(matrix_structs.keys()) + list(klines_structs.keys()))) * 4

    # 构建 Markdown 报告
    md = [
        "# A.3 全量交叉比对验证 — Matrix vs Klines N 型结构一致性",
        "",
        f"**验证时间**: {datetime.now(tz=CST).strftime('%Y-%m-%d %H:%M CST')}",
        f"**脚本**: `verify_matrix_consistency.py`",
        "",
        "## 验证目的",
        "",
        "确认 A.1/A.2 修复后（Matrix SSR+API 路径均复用 `_get_active_n_structure` 过滤）的效果：",
        "- Matrix 中的 N 型结构是否与 Klines 弹窗 API 返回的结构一致",
        "- 消除 Cat1（Matrix 有数据但弹窗不可绘制）和 Cat2（方向/ABC 不一致）差异",
        "",
        "## 数据规模",
        "",
        f"| 来源 | 品种数 | 周期单元格数 |",
        f"|------|--------|-------------|",
        f"| Matrix 矩阵 | {len(matrix_structs)} | {matrix_count} |",
        f"| Klines 弹窗 | {len(klines_structs)} | {klines_count} |",
        f"| 可能配对总数 | {len(set(list(matrix_structs.keys()) + list(klines_structs.keys())))} | {total_possible} |",
        "",
        "## 比对结果摘要",
        "",
        f"| 类别 | 数量 | 说明 |",
        f"|------|------|------|",
        f"| ✅ 完全一致 | {result['match']} | Matrix 与 Klines 方向+ABC 价格完全一致 |",
        f"| ❌ CAT1 Matrix有Klines无 | {result['cat1']} | Matrix 有 N 型结构但 Klines 弹窗没有 |",
        f"| ❌ CAT2 数据不一致 | {result['cat2']} | 方向或 ABC 价格不一致 |",
        f"| ⚠️ CAT3 Klines有Matrix无 | {result['cat3']} | Klines 有结构但 Matrix 矩阵未展示 |",
        f"| **总计（有差异）** | {result['cat1'] + result['cat2'] + result['cat3']} | |",
        "",
    ]

    if result["cat1"] == 0 and result["cat2"] == 0 and result["cat3"] == 0:
        md += [
            "## 🎉 验证结论：全部通过",
            "",
            f"所有 {result['match']} 个有数据的周期单元格完全一致，",
            "**Matrix 与 Klines 弹窗的 N 型结构数据已完全对齐。**",
            "",
            "A.1/A.2 修复（统一使用 `_get_active_n_structure` 过滤）已成功消除所有差异。",
            "",
        ]
    else:
        md += [
            "## ❌ 差异详情",
            "",
        ]

        if result["cat1"] > 0:
            md += [
                "### CAT1 — Matrix 有结构但 Klines 弹窗无",
                "",
                "| 品种 | 周期 | Matrix 数据 | 可能原因 |",
                "|------|------|-------------|---------|",
            ]
            for d in result["differences"]:
                if d["type"] == "CAT1_Matrix有Klines无":
                    reason = f"Matrix 用合约({d['matrix_contract']}) vs Klines 用合约({d['klines_contract']})"
                    md.append(f"| {d['symbol']} | {d['tf']} | {d['detail']} | {reason} |")
            md.append("")

        if result["cat2"] > 0:
            md += [
                "### CAT2 — 方向/ABC 数据不一致",
                "",
                "| 品种 | 周期 | 差异项 | Matrix 数据 | Klines 数据 |",
                "|------|------|--------|-------------|-------------|",
            ]
            for d in result["differences"]:
                if d["type"] == "CAT2_数据不一致":
                    issues = "; ".join(d.get("issues", []))
                    md.append(f"| {d['symbol']} | {d['tf']} | {issues} | {d['detail'].split('|')[0].strip()} | {d['detail'].split('|')[1].strip() if '|' in d['detail'] else ''} |")
            md.append("")

        if result["cat3"] > 0:
            md += [
                "### CAT3 — Klines 有结构但 Matrix 无",
                "",
                "| 品种 | 周期 | Klines 数据 | 可能原因 |",
                "|------|------|-------------|---------|",
            ]
            for d in result["differences"]:
                if d["type"] == "CAT3_Klines有Matrix无":
                    reason = f"Matrix 用合约({d['matrix_contract']}) vs Klines 用合约({d['klines_contract']})"
                    md.append(f"| {d['symbol']} | {d['tf']} | {d['detail']} | {reason} |")
            md.append("")

    # 合约差异分析
    md += [
        "## 合约差异分析",
        "",
        "分析 Matrix 和 Klines 路径使用合约的差异：",
        "",
        "| 品种 | Matrix 合约 | Klines 合约 | 是否一致 |",
        "|------|-------------|-------------|---------|",
    ]

    all_syms = sorted(set(matrix_structs.keys()) | set(klines_structs.keys()))
    contract_mismatch = 0
    for sym in all_syms:
        m_contracts = set()
        for tf_data in matrix_structs.get(sym, {}).values():
            if "contract" in tf_data and tf_data["contract"]:
                m_contracts.add(tf_data["contract"])
        k_contracts = set()
        for tf_data in klines_structs.get(sym, {}).values():
            if "contract" in tf_data and tf_data["contract"]:
                k_contracts.add(tf_data["contract"])

        m_c = ", ".join(sorted(m_contracts)) if m_contracts else "(无)"
        k_c = ", ".join(sorted(k_contracts)) if k_contracts else "(无)"
        ok = "✅" if m_contracts == k_contracts else "⚠️"
        if ok == "⚠️":
            contract_mismatch += 1
        md.append(f"| {sym} | {m_c} | {k_c} | {ok} |")

    md += [
        "",
        f"**合约不一致品种数**: {contract_mismatch}",
        "",
    ]

    # 根因分析
    if result["cat1"] > 0 or result["cat2"] > 0 or result["cat3"] > 0:
        md += [
            "## 根因分析",
            "",
            "### Matrix 路径合约来源",
            "1. **信号表** `futures_signals.contract` → 经 `_clean_contract_n_prefix` 清洗",
            "2. **N 结构表** `futures_n_structures.contract` → 经 `_clean_contract_n_prefix` 清洗（信号无合约时的备选）",
            "",
            "### Klines 路径合约来源",
            "1. **K 线表** `futures_klines.contract`（最新 1d K 线记录的合约）→ 不经 n 前缀清洗",
            "2. 如无 → **N 结构表**备选",
            "",
            "### 差异根因",
            "当同一个品种的信号合约 ≠ K 线表合约时，`_get_active_n_structure(db, sym, contract, tf)` 传入的 contract 不同，",
            "可能导致不同的 N 结构数据（不同合约的 K 线形态不同）。",
            "",
        ]

    # 附录
    md += [
        "## 附录：全量数据",
        "",
        "### Matrix 包含的所有品种×周期",
        "",
        "| 品种 | 周期 | 方向 | 状态 | A | B | C |",
        "|------|------|------|------|---|---|---|",
    ]
    for sym in sorted(matrix_structs.keys()):
        for tf in TIMEFRAMES:
            if tf in matrix_structs[sym]:
                s = matrix_structs[sym][tf]
                md.append(f"| {sym} | {tf} | {s['dir']} | {s['state']} | {fmt_price(s['a'])} | {fmt_price(s['b'])} | {fmt_price(s['c'])} |")
            else:
                md.append(f"| {sym} | {tf} | — | — | — | — | — |")

    md += [
        "",
        "### Klines 包含的所有品种×周期",
        "",
        "| 品种 | 周期 | 方向 | 状态 | A | B | C |",
        "|------|------|------|------|---|---|---|",
    ]
    for sym in sorted(klines_structs.keys()):
        for tf in TIMEFRAMES:
            if tf in klines_structs[sym]:
                s = klines_structs[sym][tf]
                md.append(f"| {sym} | {tf} | {s['dir']} | {s['state']} | {fmt_price(s['a'])} | {fmt_price(s['b'])} | {fmt_price(s['c'])} |")
            else:
                md.append(f"| {sym} | {tf} | — | — | — | — | — |")

    report = "\n".join(md)

    # 写文件
    docs_dir = os.path.join(PROJECT_ROOT, "docs", "qa")
    os.makedirs(docs_dir, exist_ok=True)
    report_path = os.path.join(docs_dir, "n-structure-matrix-filter-verify.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n{'=' * 70}")
    print(f"✅ 验证完成")
    print(f"  Match: {result['match']}")
    print(f"  CAT1:  {result['cat1']}")
    print(f"  CAT2:  {result['cat2']}")
    print(f"  CAT3:  {result['cat3']}")
    print(f"  Report: {report_path}")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()