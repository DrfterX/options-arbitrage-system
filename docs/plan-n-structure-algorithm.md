# Plan: N 型结构算法定义修正

## 目标

按 User Directives 中 N 型结构的正确定义，修正算法中 A/B/C 三点定位逻辑，修复状态机判定错误，并同步修正前端 K 线浮窗 A/B/C 标注映射关系。

## 问题诊断

### Bug 1 (MAJOR): 前端 K 线 A/B/C 标注映射完全反转

**文件**: `web/templates/futures_dashboard.html`，第 642-656 行

当前代码错误的映射：
```javascript
// LONG: A=high, B=low, C=high  |  SHORT: A=low, B=high, C=low
var aIsHigh = (nDir === 'LONG');     // LONG A→high (错误)
var bIsHigh = (nDir !== 'LONG');     // LONG B→low  (错误)
var cIsHigh = (nDir === 'LONG');     // LONG C→high (错误)
```

**正确定义**（与算法 `n_structure.py` 一致）：
```
LONG:  A=TROUGH(低点), B=PEAK(高点), C=TROUGH(低点)
SHORT: A=PEAK(高点),  B=TROUGH(低点), C=PEAK(高点)
```

修正后的映射：
```javascript
// LONG: A=low, B=high, C=low   |   SHORT: A=high, B=low, C=high
var aIsHigh = (nDir !== 'LONG');  // A=TROUGH→low for LONG, A=PEAK→high for SHORT
var bIsHigh = (nDir === 'LONG');  // B=PEAK→high for LONG, B=TROUGH→low for SHORT
var cIsHigh = (nDir !== 'LONG');  // C=TROUGH→low for LONG, C=PEAK→high for SHORT
```

### Bug 2 (MEDIUM): `n_structure.py` — LEG3 状态判定条件对于 LONG 不可达

**文件**: `futures/n_structure.py`，第 241-250 行

```python
if direction == "LONG":
    if pc["price"] >= pb["price"]:  # ← C=TROUGH >= B=PEAK，理论上不可能达到
        state = NState.LEG3.value
```

LONG 方向时 C 是 TROUGH（低点），B 是 PEAK（高点），`C >= B` 需要 TROUGH ≥ PEAK，这在正常的交替极值点序列中不可能成立。因此 LEG3 状态对 LONG 而言**永远无法到达**。

修正：LEG3 应表示"C 点已确认 + 第三笔（C→最新价）正在运行"，不应要求 C ≥ B。

### Bug 3 (COSMETIC): 顶层文档注释错误

**文件**: `futures/n_structure.py`，第 6-8 行

```
正N型(LONG): A < B < C 上升结构
倒N型(SHORT): A > B > C 下降结构
```

应改为描述 V 型结构：
```
上升N型(A→B→C): A=TROUGH, B=PEAK, C=TROUGH (C > A 不破前低)
下降N型(A→B→C): A=PEAK, B=TROUGH, C=PEAK (C < A 不破前高)
```

### 范围排除：动态刷新机制

检查发现 `orchestrator.py` 的 `data_refresh()` 已正确处理动态刷新：
- Step [5/5] 对每个品种的每个周期先跑 `detect_and_save`，再跑 `dynamic_restructure`
- 此逻辑在 `run_futures_scan(refresh=True)` 时自动触发
- 循环 prompt 中描述的"动态刷新机制"问题实际由以上 Bug 1 & 2 导致（标注显示错误 + 状态机判定问题）
- **此轮只修正 Bug 1-3，不涉及管道调度修改**

## 拆解步骤

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| P0.1 | Plan 文档 | 1 Cycle | `docs/plan-n-structure-algorithm.md` ✅ 当前 |
| P0.2 | 修复前端 K 线 A/B/C 标注映射（Bug 1） | 15min | `futures_dashboard.html` |
| P0.3 | 修复 LEG3 状态判定逻辑（Bug 2）+ 文档注释（Bug 3） | 15min | `n_structure.py` |
| P0.4 | 运行测试验证全部通过 | 10min | 测试结果 ✅ |
| P0.5 | 部署到线上 | 10min | deploy commit |

## 测试覆盖

`test_n_structure.py` 和 `test_integration_n_structure.py` 覆盖了：
- 正向检测 (LONG/SHORT LEG2)
- A 突破迁移 (LONG→SHORT, SHORT→LONG)
- B 反转检测
- 多推连续场景

Bug 2 修正后需确认 LEG3 状态的测试正确性：
- `test_normal_long_leg3` 目前断言 `state == LEG2` (因为 LEG3 从不触发)
- 修正后可能需要调整此断言或确认 LEG3 在新逻辑中是否应该触发

## 依赖顺序

P0.2（前端标注）和 P0.3（算法逻辑）无依赖关系，可并行走。但为了安全优先修算法再修前端。
