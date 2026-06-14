#!/usr/bin/env python3
"""
Step 1.3 — 完整诊断扫描报告生成器

使用 scorer.py 的 scan_all_contracts(diagnostic=True) 新诊断模式，
对所有品种运行一次完整 scoring 诊断，输出结构化报告。

用法: uv run python scripts/diagnostic_scan_step1.3.py
"""

import sys
import json
import os
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import Database
from config.settings import DB_PATH
from futures.scorer import scan_all_contracts


def analyze_diagnostics(results):
    """分析 scan_all_contracts(diagnostic=True) 的返回值，生成统计摘要。"""

    total = len(results)
    stats = {
        "total_contracts": total,
        "score_distribution": Counter(),
        "direction_distribution": Counter(),
        "level_pass": {"level1": Counter(), "level2": Counter(), "level3": Counter()},
        "fail_reasons": {"level1": Counter(), "level2": Counter(), "level3": Counter()},
        "macd_passes": {"level1": Counter(), "level2": Counter()},
        "macd_leg_passes": {"level1": Counter(), "level2": Counter()},
        "threem_bars": [],
        "threem_switch_counts": [],
        "breakout_vs_b": [],
        "known_issues": Counter(),
    }

    for r in results:
        stats["score_distribution"][r.overall_score] += 1
        stats["direction_distribution"][r.direction] += 1
        diag = r.diagnostic or {}

        # ── Level 分析 ──
        for lev_name, diag_key in [("level1", "level1"), ("level2", "level2"), ("level3", "level3")]:
            d = diag.get(diag_key, {})
            passed = d.get("passed", False)
            stats["level_pass"][lev_name][passed] += 1
            reasons = d.get("reasons", [])
            for reason in reasons:
                # 提取关键失败原因（简化归类）
                key = reason[:80]  # truncate
                stats["fail_reasons"][lev_name][key] += 1

        # ── L1 MACD 分析 ──
        d1 = diag.get("level1", {})
        d1_data = d1.get("data", {})
        if d1_data:
            for leg in ["macd_passed_leg1", "macd_passed_leg2", "macd_passed_leg3"]:
                val = d1_data.get(leg)
                if val is not None:
                    stats["macd_leg_passes"]["level1"][f"{leg}={val}"] += 1

        # ── L2 MACD 分析 ──
        d2 = diag.get("level2", {})
        d2_data = d2.get("data", {})
        if d2_data:
            for leg in ["macd_passed_leg1", "macd_passed_leg2", "macd_passed_leg3"]:
                val = d2_data.get(leg)
                if val is not None:
                    stats["macd_leg_passes"]["level2"][f"{leg}={val}"] += 1

        # ── 3m 数据分析 ──
        d3 = diag.get("level3", {})
        d3_data = d3.get("data", {})
        if d3_data:
            bars = d3_data.get("3m_total_bars")
            if bars is not None:
                stats["threem_bars"].append(bars)
            switches = d3_data.get("3m_switch_count")
            if switches is not None:
                stats["threem_switch_counts"].append(switches)

            # 突破 vs B 点
            current_price = d3_data.get("current_price")
            b_price = d3_data.get("B_price")
            if current_price and b_price:
                stats["breakout_vs_b"].append({
                    "symbol": r.symbol,
                    "contract": r.contract,
                    "current_price": current_price,
                    "b_price": b_price,
                    "pct_diff": round((current_price - b_price) / b_price * 100, 2),
                    "triggered": d3_data.get("breakout_triggered", False),
                })

        # ── 已知问题 ──
        if d3_data.get("3m_timeframe") != "3m":
            stats["known_issues"]["3m数据周期异常"] += 1
        if d3_data.get("l3_state") == "NO_STRUCTURE":
            stats["known_issues"]["15分钟无活跃N型结构"] += 1
        if d2_data.get("l2_state") == "NO_STRUCTURE":
            stats["known_issues"]["小时线无活跃N型结构"] += 1

    return stats


def compute_threem_bar_buckets(bars_list):
    """将 3m bar 数量分桶统计。"""
    buckets = Counter()
    for b in bars_list:
        if b <= 0:
            buckets["0（无数据）"] += 1
        elif b < 30:
            buckets["1-29（不足）"] += 1
        elif b < 100:
            buckets["30-99"] += 1
        elif b < 500:
            buckets["100-499"] += 1
        elif b < 2000:
            buckets["500-1999"] += 1
        else:
            buckets["2000+"] += 1
    return buckets


def count_symbol_fails(results):
    """按品种统计各 Level 失败原因的前置快照。"""
    per_sym = defaultdict(lambda: {"l1_fail": [], "l2_fail": [], "l3_fail": []})
    for r in results:
        sym = r.symbol
        diag = r.diagnostic or {}
        for lev, key in [("l1_fail", "level1"), ("l2_fail", "level2"), ("l3_fail", "level3")]:
            d = diag.get(key, {})
            if not d.get("passed", False):
                reasons = d.get("reasons", [])
                reason_str = "; ".join(reasons[:3]) if reasons else "未知"
                per_sym[sym][lev].append(reason_str)
    return dict(per_sym)


def generate_report(results, stats, sym_fails):
    """生成完整诊断报告 markdown。"""

    lines = []
    a = lines.append

    a("# N型K线结构交易系统 — 诊断扫描报告\n")
    a(f"> 基于 `scan_all_contracts(diagnostic=True)` 生成\n")
    a(f"> 运行时间: 2026-06-15 03:30 CST\n")
    a(f"> 扫描品种: {stats['total_contracts']} 个主力合约\n")

    # ═══════════════════════════════════════════════
    # 1. 摘要
    # ═══════════════════════════════════════════════
    a("\n## 一、评分分布总览\n")
    a("\n| 评分 | 合约数 | 占比 |")
    a("|------|--------|------|")
    for score in sorted(stats["score_distribution"]):
        cnt = stats["score_distribution"][score]
        pct = cnt / stats["total_contracts"] * 100
        label = {0: "NONE", 1: "L1通过", 2: "L2通过", 3: "ENTRY", 4: "ADD_POS"}.get(score, str(score))
        a(f"| {label} (score={score}) | {cnt} | {pct:.1f}% |")

    a("\n| 评分范围 | 数量 |")
    a("|----------|------|")
    cnt_3plus = stats["score_distribution"].get(3, 0) + stats["score_distribution"].get(4, 0)
    cnt_2 = stats["score_distribution"].get(2, 0)
    cnt_1 = stats["score_distribution"].get(1, 0)
    cnt_0 = stats["score_distribution"].get(0, 0)
    a(f"| score=3+ (ENTRY) | {cnt_3plus} |")
    a(f"| score=2 (L2通过) | {cnt_2} |")
    a(f"| score=1 (L1通过) | {cnt_1} |")
    a(f"| score=0 (NONE)   | {cnt_0} |")

    a("\n### 方向分布\n")
    for direction, cnt in sorted(stats["direction_distribution"].items()):
        a(f"- {direction}: {cnt} ({cnt/stats['total_contracts']*100:.1f}%)")

    # ═══════════════════════════════════════════════
    # 2. 分级通过漏斗
    # ═══════════════════════════════════════════════
    a("\n## 二、三级验证漏斗\n")

    l1_pass = stats["level_pass"]["level1"].get(True, 0)
    l2_pass = stats["level_pass"]["level2"].get(True, 0)
    l3_pass = stats["level_pass"]["level3"].get(True, 0)
    l1_fail = stats["level_pass"]["level1"].get(False, 0)
    l2_fail = stats["level_pass"]["level2"].get(False, 0)
    l3_fail = stats["level_pass"]["level3"].get(False, 0)

    a("```")
    a(f"  {stats['total_contracts']} 个主力合约")
    a(f"    │")
    a(f"    ├─ L1通过: {l1_pass}/{stats['total_contracts']} ({l1_pass/stats['total_contracts']*100:.1f}%)")
    a(f"    │   └─ 失败: {l1_fail}")
    a(f"    │")
    a(f"    ├─ L2通过: {l2_pass}/{stats['total_contracts']} ({l2_pass/stats['total_contracts']*100:.1f}%)")
    a(f"    │   └─ 失败: {l2_fail}")
    a(f"    │")
    a(f"    ├─ L3通过: {l3_pass}/{stats['total_contracts']} ({l3_pass/stats['total_contracts']*100:.1f}%)")
    a(f"    │   └─ 失败: {l3_fail}")
    a(f"    │")
    a(f"    └─ ENTRY (score>=3): {cnt_3plus}")
    a("```")

    if l1_pass > 0:
        a(f"\n- L1→L2 转化率: {l2_pass}/{l1_pass} = {l2_pass/l1_pass*100:.1f}%")
    if l2_pass > 0:
        a(f"\n- L2→L3 转化率: {l3_pass}/{l2_pass} = {l3_pass/l2_pass*100:.1f}%")

    # ═══════════════════════════════════════════════
    # 3. 各级失败原因统计
    # ═══════════════════════════════════════════════
    a("\n## 三、各级失败原因明细\n")

    for lev_name, lev_label in [("level1", "Level1 — 周线N型+日线MACD"),
                                  ("level2", "Level2 — 小时线N型+15mMACD"),
                                  ("level3", "Level3 — 15mN型+3m稳定+突破")]:
        a(f"\n### {lev_label}\n")
        reasons = stats["fail_reasons"][lev_name]
        if reasons:
            a("\n| 原因 | 出现次数 |")
            a("|------|---------|")
            for reason, cnt in reasons.most_common(20):
                a(f"| `{reason}` | {cnt} |")
        else:
            a("\n_无失败记录（全部通过）_\n")

    # ═══════════════════════════════════════════════
    # 4. MACD 分级通过率
    # ═══════════════════════════════════════════════
    a("\n## 四、MACD 腿级通过率\n")

    for level in ["level1", "level2"]:
        label = {"level1": "Level1（日线MACD）", "level2": "Level2（15mMACD）"}[level]
        a(f"\n### {label}\n")
        legs = stats["macd_leg_passes"][level]
        if legs:
            a("\n| 检查项 | 计数 |")
            a("|--------|------|")
            for key, cnt in legs.most_common():
                a(f"| {key} | {cnt} |")
        else:
            a("\n_无MACD腿级数据_\n")

    # 统计腿通过率
    a("\n### MACD腿通过率汇总\n")
    l1_total = stats["level_pass"]["level1"].get(True, 0) + stats["level_pass"]["level1"].get(False, 0)
    l2_total = stats["level_pass"]["level2"].get(True, 0) + stats["level_pass"]["level2"].get(False, 0)

    for level_label, level_key, total, level_pass_cnt in [
        ("Level1(日线MACD)", "level1", l1_total, l1_pass),
        ("Level2(15mMACD)", "level2", l2_total, l2_pass),
    ]:
        legs = stats["macd_leg_passes"][level_key]
        leg1_true = sum(v for k, v in legs.items() if "macd_passed_leg1=True" in k)
        leg1_false = sum(v for k, v in legs.items() if "macd_passed_leg1=False" in k)
        leg2_true = sum(v for k, v in legs.items() if "macd_passed_leg2=True" in k)
        leg2_false = sum(v for k, v in legs.items() if "macd_passed_leg2=False" in k)
        leg3_true = sum(v for k, v in legs.items() if "macd_passed_leg3=True" in k)
        leg3_false = sum(v for k, v in legs.items() if "macd_passed_leg3=False" in k)

        leg_total = leg1_true + leg1_false
        a(f"- {level_label}:")
        if leg_total > 0:
            a(f"  - 腿1通过: {leg1_true}/{leg_total} ({leg1_true/leg_total*100:.1f}%)")
            a(f"  - 腿2通过: {leg2_true}/{leg_total} ({leg2_true/leg_total*100:.1f}%)")
            a(f"  - 腿3通过: {leg3_true}/{leg_total} ({leg3_true/leg_total*100:.1f}%)")

    # ═══════════════════════════════════════════════
    # 5. 3m 数据分析
    # ═══════════════════════════════════════════════
    a("\n## 五、3m 数据质量分析\n")

    bars_list = stats["threem_bars"]
    if bars_list:
        buckets = compute_threem_bar_buckets(bars_list)
        a("\n| 3m数据量 (bars) | 品种数 |")
        a("|----------------|--------|")
        for bucket, cnt in sorted(buckets.items()):
            a(f"| {bucket} | {cnt} |")

        nonzero = [b for b in bars_list if b > 0]
        if nonzero:
            a(f"\n- 有数据的品种: {len(nonzero)}/{len(bars_list)}")
            a(f"- 最小 bars: {min(bars_list)}")
            a(f"- 最大 bars: {max(bars_list)}")
            a(f"- 平均 bars: {sum(bars_list)/len(bars_list):.0f}")
        else:
            a(f"\n- 所有品种 3m bars 均为 0（无数据）")
    else:
        a("\n_无3m数据_\n")

    switch_counts = stats["threem_switch_counts"]
    if switch_counts:
        nonzero_sw = [s for s in switch_counts if s is not None]
        if nonzero_sw:
            a(f"\n- 3m MACD切换次数: min={min(nonzero_sw)}, max={max(nonzero_sw)}, avg={sum(nonzero_sw)/len(nonzero_sw):.1f}")
            a(f"- 切换次数分布:")
            sw_buckets = Counter()
            for s in nonzero_sw:
                if s == 0: sw_buckets["0"] += 1
                elif s < 3: sw_buckets["1-2"] += 1
                elif s < 6: sw_buckets["3-5"] += 1
                else: sw_buckets["6+"] += 1
            for bucket, cnt in sorted(sw_buckets.items()):
                a(f"  - {bucket}: {cnt} 品种")

    # ═══════════════════════════════════════════════
    # 6. 突破价 vs B点
    # ═══════════════════════════════════════════════
    a("\n## 六、突破价 vs B点对比\n")

    bv = stats["breakout_vs_b"]
    if bv:
        triggered = [x for x in bv if x["triggered"]]
        not_triggered = [x for x in bv if not x["triggered"]]
        a(f"- 已突破B点: {len(triggered)} 品种")
        a(f"- 未突破B点: {len(not_triggered)} 品种")

        if not_triggered:
            a("\n未突破品种详情（TOP 10）:")
            a("\n| 品种 | 合约 | 当前价 | B点价 | 偏差% |")
            a("|------|------|--------|-------|-------|")
            for x in sorted(not_triggered, key=lambda x: abs(x["pct_diff"]))[:10]:
                a(f"| {x['symbol']} | {x['contract']} | {x['current_price']} | {x['b_price']} | {x['pct_diff']:+.2f}% |")

        if not_triggered:
            avg_dev = sum(abs(x["pct_diff"]) for x in not_triggered) / len(not_triggered)
            a(f"\n- 未突破品种平均偏差: {avg_dev:.2f}%")
    else:
        a("\n_无突破对比数据_\n")

    # ═══════════════════════════════════════════════
    # 7. 品种级详细
    # ═══════════════════════════════════════════════
    a("\n## 七、品种级诊断概览\n")

    a("\n| 品种 | L1 | L2 | L3 | Score | 方向 | 问题摘要 |")
    a("|------|----|----|----|-------|------|---------|")
    for r in results:
        diag = r.diagnostic or {}
        l1_ok = "✅" if diag.get("level1", {}).get("passed") else "❌"
        l2_ok = "✅" if diag.get("level2", {}).get("passed") else "❌"
        l3_ok = "✅" if diag.get("level3", {}).get("passed") else "❌"
        score = r.overall_score
        direction = r.direction if r.direction != "NONE" else "-"

        # 取最关键的失败原因
        issues = []
        for lev, name in [("level1", "L1"), ("level2", "L2"), ("level3", "L3")]:
            d = diag.get(lev, {})
            if not d.get("passed"):
                reasons = d.get("reasons", [])
                if reasons:
                    issue = reasons[0][:40]
                    issues.append(f"{name}:{issue}")
                else:
                    issues.append(f"{name}:失败")

        issue_str = "; ".join(issues[:2]) if issues else "-"
        a(f"| {r.symbol:6s} | {l1_ok} | {l2_ok} | {l3_ok} | {score} | {direction:5s} | {issue_str} |")

    # ═══════════════════════════════════════════════
    # 8. 已知问题与建议
    # ═══════════════════════════════════════════════
    a("\n## 八、已知问题与改进建议\n")

    a("\n### 已知问题\n")
    for issue, cnt in stats["known_issues"].most_common():
        a(f"- {issue}: {cnt} 品种受影响")

    a("\n### 主要瓶颈分析\n")

    if l1_fail > l2_fail and l1_fail > l3_fail:
        a("- 🔴 **最大瓶颈：Level1** — 多数品种止步于周线N型或日线MACD")
    if l2_fail > l1_fail or l2_fail >= l1_pass:
        a("- 🟠 **第二瓶颈：Level2** — L1通过但L2失败比例高（小时线N型或15mMACD）")
    if l3_fail > 0 and l3_pass == 0:
        a("- ❌ **L3完全阻塞** — 无品种通过Level3（3m数据或15m突破）")

    # 3m 数据问题
    if bars_list:
        pass_30 = sum(1 for b in bars_list if b >= 30)
        if pass_30 == 0:
            a("\n### ⛔ 3m 数据阻塞分析\n")
            a("\n**根本原因：** 数据库中没有3m数据或数据量不足30根。")
            a("当前3m数据日期范围（如果有）远不足以支撑历史回放。")
            a("\n**修复选项（Phase ① Step 4）：**")
            a("- **选项A（推荐）：** 从1m K线合成3m → 需要1m数据源")
            a("- **选项B（快速）：** L3降级为15m稳定性检查 → 立即可用但降低精度")
            a("- **选项C（保守）：** 等待自然积累3m数据 → 约30天才有4320 bars")

    a("\n### 建议优先处理\n")
    if cnt_3plus == 0:
        a("- **1. 3m数据问题（阻塞）** — 无3m数据→L3永远无法通过→0 ENTRY")
    a("- **2. MACD 70%阈值分析** — 统计各周期MACD颜色分布，判断70%是否过严")
    a("- **3. 评分重置触发分析** — 检查是否误杀了有效信号")
    a("- **4. 周线N型结构窗口** — 当前SWING_WINDOWS[\"1w\"]=2，窗口极窄")

    return "\n".join(lines)


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, "trading_system.db")

    print(f"📡 连接数据库: {db_path}")
    db = Database(db_path)

    print(f"🔍 执行 scan_all_contracts(diagnostic=True)...")
    results = scan_all_contracts(db, diagnostic=True)
    print(f"   ✅ 完成: {len(results)} 个合约评估")

    print(f"📊 分析诊断数据...")
    stats = analyze_diagnostics(results)
    sym_fails = count_symbol_fails(results)

    print(f"📝 生成报告...")
    report = generate_report(results, stats, sym_fails)

    # 写入 docs/ 目录
    docs_dir = os.path.join(project_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    report_path = os.path.join(docs_dir, "diagnostic-scan-report.md")
    with open(report_path, "w") as f:
        f.write(report)

    print(f"   ✅ 报告已写入: {report_path}")

    # 打印摘要到控制台
    print(f"\n{'='*60}")
    print(f"📋 诊断摘要")
    print(f"{'='*60}")
    total = len(results)
    l1_ok = stats["level_pass"]["level1"].get(True, 0)
    l2_ok = stats["level_pass"]["level2"].get(True, 0)
    l3_ok = stats["level_pass"]["level3"].get(True, 0)
    print(f"  Level1通过: {l1_ok}/{total} ({l1_ok/total*100:.1f}%)")
    print(f"  Level2通过: {l2_ok}/{total} ({l2_ok/total*100:.1f}%)")
    print(f"  Level3通过: {l3_ok}/{total} ({l3_ok/total*100:.1f}%)")

    score_3plus = stats["score_distribution"].get(3, 0) + stats["score_distribution"].get(4, 0)
    print(f"  ENTRY (score>=3): {score_3plus}")

    bars_list = stats["threem_bars"]
    if bars_list:
        print(f"  3m bars: min={min(bars_list)}, max={max(bars_list)}, avg={sum(bars_list)/len(bars_list):.0f}")
    else:
        print(f"  3m bars: 无数据")

    db.close()
    print(f"{'='*60}")
    print(f"✅ 诊断扫描完成")


if __name__ == "__main__":
    main()
