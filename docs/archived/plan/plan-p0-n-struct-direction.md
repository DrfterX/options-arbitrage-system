# P0 N 型算法方向判定 — 修复 Plan & 审计记录

**执行 Cycle**: #198
**状态**: ✅ 全部完成（Plan → Code → Test）

---

## 目标

修复 `futures/n_structure.py` 中 `_find_n_structure_forward()` 的方向判定缺陷：算法未先判断方向再标点，导致持续趋势可能被误识别为 N 型结构。

## 拆解步骤执行记录

| # | 子任务 | 预计耗时 | 实际耗时 | 状态 |
|---|--------|---------|---------|------|
| 0.1 | Plan: 查找算法代码 + 召集 CTO/CEO 出修复方案 | 15min | ~8min | ✅ |
| 0.2 | 按方案修改方向判定逻辑 | 20min | ~5min | ✅ CTO 直接实施 |
| 0.3 | 各周期验证 ABC 标点正确性 | 15min | — | ❌ CEO 决定关闭 |

## 审计发现

见 `docs/cto/p0-n-struct-direction-audit.md`

### 核心缺陷

`_determine_direction()` 从 A→B 价格差派生方向，但从未校验 A 的 `point_type` 是否与方向一致：
- LONG 要求 A=TROUGH(低点)，B=PEAK(高点)
- SHORT 要求 A=PEAK(高点)，B=TROUGH(低点)
- 持续下跌 `TROUGH(100)→PEAK(95)→TROUGH(90)` 会被误判为 SHORT N 型

### 修复方案

在 `_find_n_structure_forward` 中方向判断后、C 点查找前插入一致性校验：

```python
if (direction == "LONG" and a["point_type"] != "TROUGH") or \
   (direction == "SHORT" and a["point_type"] != "PEAK"):
    continue
```

## 测试结果

```
48 passed in 0.03s
```

- 46 个原有测试全部通过（零回归）
- 2 个新增测试验证持续趋势不被误识别的边界
- 所有周期（15m/1h/1d/1w）共用同一套检测逻辑，一修全修

## CEO 决策摘要

见 `docs/ceo/p0-n-struct-direction-decision.md`

1. ✅ 批准修复
2. ❌ 关闭 Step 0.3（逐周期验证 → 没必要，by construction 正确）
3. 📋 其他关联修复已评估并排定优先级

## 差异汇总

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| TROUGH→PEAK→TROUGH 且价格持续下跌 | 误判为 SHORT N 型 | 正确返回 None（非有效 N 型） |
| PEAK→TROUGH→PEAK 且价格持续上涨 | 误判为 LONG N 型 | 正确返回 None（非有效 N 型） |
| 正常 LONG (T↓→P↑→T↓, C>A) | 正确识别 | ✅ 不变 |
| 正常 SHORT (P↑→T↓→P↑, C<A) | 正确识别 | ✅ 不变 |