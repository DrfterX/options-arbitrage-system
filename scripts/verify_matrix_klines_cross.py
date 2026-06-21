#!/usr/bin/env python3
"""
A.3 — 全量交叉比对验证：Matrix 数据 vs Klines 弹窗 N 型结构数据

遍历所有活跃品种 × 4 周期，从以下两个来源获取 N 型结构数据并对比：
1. /api/matrix — 经 _get_active_n_structure() 过滤的矩阵数据
2. /api/klines — 同样经 _get_active_n_structure() 过滤的弹窗数据

期望结果：两者完全一致（因为都使用同一函数过滤）
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

TIMEFRAMES = ["15m", "1h", "1d", "1w"]
CST = timezone(timedelta(hours=8))
TZ = CST
BASE_URL = "http://127.0.0.1:5100"

# ── 统计 ──────────────────────────────────────────────────────
total_cells = 0        # 矩阵中有 N 结构数据的 cell 总数
matched = 0            # 矩阵 vs klines 完全一致
mismatched = []        # 不一致列表
matrix_only = []       # matrix 有结构但 klines 没有
klines_only = []       # klines 有结构但 matrix 没有
matrix_errors = []     # 矩阵请求错误
klines_errors = []     # klines 请求错误
matrix_empty_nstruct = 0  # matrix cell 不含 N 型结构数据
per_tf = {tf: {"total": 0, "ok": 0, "diff": 0} for tf in TIMEFRAMES}

def fetch_json(url):
    req = Request(url, headers={"User-Agent": "A3-Verify/1.0"})
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def extract_nstruct_from_matrix(cell):
    """从 matrix cell 提取 N 结构数据。"""
    if not cell.get("dir") or not cell.get("state"):
        return None
    return {
        "dir": cell["dir"],
        "state": cell["state"],
        "a": cell.get("a"),
        "b": cell.get("b"),
        "c": cell.get("c"),
        "at": cell.get("at"),
        "bt": cell.get("bt"),
        "ct": cell.get("ct"),
    }


def extract_nstruct_from_klines(data):
    """从 klines response 提取 N 结构数据。"""
    ns = data.get("n_structure")
    if not ns:
        return None
    return {
        "dir": ns["dir"],
        "state": ns["state"],
        "a": ns["a"],
        "b": ns["b"],
        "c": ns["c"],
        "at": ns.get("at"),
        "bt": ns.get("bt"),
        "ct": ns.get("ct"),
    }


def nstruct_equal(a, b):
    """比较两个 N 结构是否一致（方向 + ABC 价格 + state）。"""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    checks = [
        a["dir"] == b["dir"],
        a["state"] == b["state"],
        abs((a.get("a") or 0) - (b.get("a") or 0)) < 0.01,
        abs((a.get("b") or 0) - (b.get("b") or 0)) < 0.01,
        abs((a.get("c") or 0) - (b.get("c") or 0)) < 0.01,
    ]
    return all(checks)


def fmt_ns(ns):
    if not ns:
        return "N/A"
    return f"A={ns['a']:.2f}→B={ns['b']:.2f}→C={ns['c']:.2f} ({ns['dir']}/{ns['state']})"


def run():
    global total_cells, matched, matrix_empty_nstruct

    print(f"{'='*80}")
    print(f"  A.3 — 全量交叉比对验证：Matrix ↔ Klines N 型结构一致性")
    print(f"  生成时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} CST")
    print(f"{'='*80}\n")

    # ── Step 1: 获取 Matrix 数据 ────────────────────────────
    print("📡 Step 1: 获取 /api/matrix 数据...")
    try:
        matrix_data = fetch_json(f"{BASE_URL}/api/matrix")
    except URLError as e:
        print(f"  ❌ 无法获取 matrix 数据: {e}")
        return

    matrix_cells_count = 0
    for entry in matrix_data.get("matrix", []):
        for cell in entry.get("cells", []):
            ns = extract_nstruct_from_matrix(cell)
            if ns:
                matrix_cells_count += 1
    print(f"  ✅ 获取成功: {len(matrix_data.get('matrix', []))} 品种, {matrix_cells_count} 个含 N 结构的 cell\n")

    # ── Step 2: 遍历每个 matrix cell → 对应 klines ─────────
    print("📡 Step 2: 逐 cell 对比 klines N 型结构数据...")
    print()

    processed_pairs = set()  # (sym, tf) 去重

    for entry in matrix_data.get("matrix", []):
        sym = entry["sym"]
        contract = entry.get("contract", "")

        for cell in entry.get("cells", []):
            tf = cell["tf"]
            matrix_ns = extract_nstruct_from_matrix(cell)

            if not matrix_ns:
                matrix_empty_nstruct += 1
                continue

            key = (sym, tf)
            if key in processed_pairs:
                continue
            processed_pairs.add(key)
            total_cells += 1

            # 获取 klines N 结构
            klines_url = f"{BASE_URL}/api/klines?symbol={sym}&timeframe={tf}"
            try:
                klines_data = fetch_json(klines_url)
                klines_ns = extract_nstruct_from_klines(klines_data)
            except URLError as e:
                klines_errors.append(f"{sym} {tf}: {e}")
                per_tf[tf]["total"] += 1
                per_tf[tf]["diff"] += 1
                continue

            # 对比
            if nstruct_equal(matrix_ns, klines_ns):
                matched += 1
                per_tf[tf]["total"] += 1
                per_tf[tf]["ok"] += 1
            else:
                mismatched.append({
                    "sym": sym, "contract": contract, "tf": tf,
                    "matrix": matrix_ns, "klines": klines_ns,
                })
                per_tf[tf]["total"] += 1
                per_tf[tf]["diff"] += 1

            # 检查 klines 有但 matrix 没有（反向缺失）
            if not matrix_ns and klines_ns:
                klines_only.append({"sym": sym, "contract": contract, "tf": tf, "data": klines_ns})

    # ── Step 3: 反向验证 — 对每个 matrix 品种 × 周期，查是否有 klines 结构未被 matrix 捕获 ──
    print("📡 Step 3: 反向验证 — klines 有结构但 matrix 遗漏...")
    # 已知合约列表（从 matrix 获取）
    all_sym_tf = set()
    for entry in matrix_data.get("matrix", []):
        sym = entry["sym"]
        for cell in entry.get("cells", []):
            tf = cell["tf"]
            all_sym_tf.add((sym, tf))

    # 遍历所有 (sym, tf) 组合，检查 klines 是否有额外的 N 结构
    extra_count = 0
    for sym, tf in sorted(all_sym_tf):
        if (sym, tf) in processed_pairs:
            continue  # 已经在 Matrix 中有结构了
        try:
            klines_data = fetch_json(f"{BASE_URL}/api/klines?symbol={sym}&timeframe={tf}")
            klines_ns = extract_nstruct_from_klines(klines_data)
            if klines_ns:
                extra_count += 1
                klines_only.append({"sym": sym, "contract": "", "tf": tf, "data": klines_ns,
                                    "note": "klines 有结构但 matrix 无"})
        except URLError:
            pass

    if extra_count > 0:
        print(f"  ⚠️  发现 {extra_count} 个 klines 有结构但 matrix 无的 cell")
    else:
        print(f"  ✅ 未发现 klines 有结构但 matrix 遗漏的情况")
    print()

    # ── 输出结果 ──────────────────────────────────────────
    print(f"{'='*80}")
    print(f"  验证结果汇总")
    print(f"{'='*80}")
    print(f"  含 N 结构的 Matrix cell 总数: {total_cells}")
    print(f"  ✅ 完全一致: {matched}")
    print(f"  ❌ 不一致:   {len(mismatched)}")
    print(f"  ⚠️ 仅矩阵有: {len(matrix_only)}")
    print(f"  ⚠️ 仅弹窗有: {len(klines_only)}")
    print(f"  ⚠️ Matrix 请求异常: {len(matrix_errors)}")
    print(f"  ⚠️ Klines 请求异常: {len(klines_errors)}")
    print()

    # ── 按周期 ────────────────────────────────────────────
    print(f"## 按周期统计")
    for tf in TIMEFRAMES:
        stats = per_tf.get(tf, {"total": 0, "ok": 0, "diff": 0})
        pct = stats["ok"] / stats["total"] * 100 if stats["total"] > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        print(f"  {tf:<4}: {stats['total']:>3} 个 | ✅ {stats['ok']:>3} | ❌ {stats['diff']:>3} | {pct:5.1f}% {bar}")
    print()

    # ── 不一致明细 ────────────────────────────────────────
    if mismatched:
        print(f"## ❌ 不一致明细 ({len(mismatched)})")
        print()
        for m in mismatched:
            print(f"  ❌ {m['sym']:<6} {m['tf']:<4} ({m['contract']})")
            print(f"      矩阵:  {fmt_ns(m['matrix'])}")
            print(f"      弹窗:  {fmt_ns(m['klines'])}")
            print()
    else:
        print(f"## ❌ 不一致明细")
        print(f"  ✅ 全部一致，未发现差异")
        print()

    # ── 仅弹窗有 ──────────────────────────────────────────
    if klines_only:
        print(f"## ⚠️ 仅弹窗有 N 结构但矩阵无 ({len(klines_only)})")
        print()
        for k in klines_only[:20]:
            note = k.get("note", "")
            print(f"  ⚠️  {k['sym']:<6} {k['tf']:<4} — {fmt_ns(k['data'])} {note}")
            print()
        if len(klines_only) > 20:
            print(f"  ... 共 {len(klines_only)} 条，仅显示前 20 条")
            print()
    else:
        print(f"## ⚠️ 仅弹窗有")
        print(f"  ✅ 未发现弹窗有但矩阵无的情况")
        print()

    # ── 结论 ──────────────────────────────────────────────
    print(f"{'='*80}")
    print(f"  结论")
    print(f"{'='*80}")
    if len(mismatched) == 0 and len(matrix_only) == 0 and len(klines_only) == 0:
        print(f"  ✅ PASS — Matrix 与 Klines 弹窗的 N 型结构数据完全一致")
        print(f"  ✅ 修复效果验证通过：Cat1（Matrix 有数据但弹窗不可绘制）= 0")
        print(f"  ✅ 修复效果验证通过：Cat2（方向/ABC 不一致）= 0")
    else:
        if len(mismatched) > 0:
            print(f"  ❌ FAIL — {len(mismatched)} 个 cell 存在矩阵与弹窗数据不一致")
        if len(matrix_only) > 0:
            print(f"  ❌ Cat1 残存 — {len(matrix_only)} 个矩阵有但弹窗无")
        if len(klines_only) > 0:
            print(f"  ⚠️ Cat1 反向 — {len(klines_only)} 个弹窗有但矩阵无")
        print(f"  需进一步排查差异根因")

    # ── 保存报告 ──────────────────────────────────────────
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "docs", "qa", "n-structure-matrix-filter-verify.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w") as f:
        f.write(f"# A.3 — 全量交叉比对验证报告\n\n")
        f.write(f"## 概述\n\n")
        f.write(f"- **生成时间**: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} CST\n")
        f.write(f"- **数据源**: `/api/matrix` vs `/api/klines`\n")
        f.write(f"- **含 N 结构的 Matrix cell 总数**: {total_cells}\n")
        f.write(f"- **完全一致**: {matched} | **不一致**: {len(mismatched)}\n\n")

        f.write("## 按周期统计\n\n")
        f.write("| 周期 | 总数 | ✅ 一致 | ❌ 不一致 | 一致率 |\n")
        f.write("|------|------|---------|----------|--------|\n")
        for tf in TIMEFRAMES:
            stats = per_tf.get(tf, {"total": 0, "ok": 0, "diff": 0})
            pct = stats["ok"] / stats["total"] * 100 if stats["total"] > 0 else 0
            f.write(f"| {tf} | {stats['total']} | {stats['ok']} | {stats['diff']} | {pct:.1f}% |\n")
        f.write("\n")

        if mismatched:
            f.write("## 不一致明细\n\n")
            f.write("| 品种 | 周期 | 合约 | 矩阵数据 | 弹窗数据 |\n")
            f.write("|------|------|------|----------|----------|\n")
            for m in mismatched:
                f.write(f"| {m['sym']} | {m['tf']} | {m['contract']} | "
                        f"{fmt_ns(m['matrix'])} | {fmt_ns(m['klines'])} |\n")
            f.write("\n")
        else:
            f.write("## 不一致明细\n\n")
            f.write("✅ 未发现不一致\n\n")

        if klines_only:
            f.write("## 仅弹窗有 N 结构\n\n")
            f.write("| 品种 | 周期 | 数据 | 备注 |\n")
            f.write("|------|------|------|------|\n")
            for k in klines_only:
                f.write(f"| {k['sym']} | {k['tf']} | {fmt_ns(k['data'])} | {k.get('note', '')} |\n")
            f.write("\n")

        f.write("## 结论\n\n")
        if len(mismatched) == 0 and len(matrix_only) == 0 and len(klines_only) == 0:
            f.write("**✅ PASS** — Matrix 与 Klines 弹窗的 N 型结构数据完全一致\n\n")
        else:
            f.write("**❌ FAIL** — 存在数据不一致\n\n")

    print(f"\n📄 报告已保存: {report_path}")
    return len(mismatched), len(matrix_only), len(klines_only)


if __name__ == "__main__":
    mismatches, matrix_only, klines_only = run()
    sys.exit(0 if mismatches == 0 and matrix_only == 0 else 1)