# 期货面板各周期 N 型标注不一致 — 调查与修复计划

## 目标

定位期货面板多周期浮窗（15m/1h/1d/1w）中 N 型标注不一致的根因（部分周期标对、部分标错、部分未标），给出修复方案并修复。

## 当前已知

- ✅ **方向优先算法本身已验证通过**：全周期 C1/C2/C3 100% 通过率
- ❌ **UI 渲染不一致**：同一品种在不同时间周期的浮窗中，A/B/C 标注出现有时正确、有时错误、有时缺失

## 数据架构

```
Matrix/Api(/api/matrix) → Template(data-*属性) → showKlinePopup()
                                                        ↓
                                            /api/klines → _get_active_n_structure() → drawKline()
```

关键路径：
- `/api/matrix` 通过 `signal_contracts` 解析合约 → 调用 `_get_active_n_structure()` → 渲染 `data-a/b/c/at/bt/ct`
- `/api/klines` 通过 `_get_futures_contract()` 解析合约（fallback 链） → 调用 `_get_active_n_structure()` → 返回 `n_structure`
- `drawKline()` 通过 `findBarForNPoint()`（时间戳最近匹配）定位 A/B/C 在 K 线图上的位置

## 潜在根因（需验证）

| # | 假设 | 影响 |
|---|------|------|
| H1 | **合约解析不一致**：`/api/matrix` 和 `/api/klines` 对同一 symbol 可能解析出不同合约 | 矩阵 `data-*` 用 contract A 的数据，弹窗 API 用 contract B 的数据 |
| H2 | **15m/1h vs 1d/1w 时间戳对齐差异**：1d/1w 做了时间戳归一化（→05:45UTC），但如果 K 线 bar 时间戳未归一化或归一化规则不同，`findBarForNPoint()` 找错 bar | 标注画在错误位置 |
| H3 | **C4 过滤差异**：某些周期最新价刚好在 C 点附近波动，C4 时通过时不通过 | 同一品种某些周期有标注、某些没有 |
| H4 | **1d/1w 日线去重 + 实时 K 线注入**：实时 K 线注入后的时间戳可能与其他 bar 不一致 | 最近 bar 时间戳偏移，N 型 C 点定位错误 |
| H5 | **`_get_active_n_structure()` 内部 C1/C2/C3 修复标记 COMPLETED**：跨周期时一个周期的修复标记可能影响其他周期 | 不适用（各周期独立 DB 行） |

## 调查步骤

### Step 1 — 诊断脚本：采集全量数据（1 Cycle）

**产出**：`docs/qa/n-structure-annotation-diagnostic.md`

编写 Python 诊断脚本 `scripts/debug/n_structure_annotation_debug.py`，对每个品种 × 每个周期：

1. 调用 `_get_futures_contract(conn, sym)` 获取 `/api/klines` 用的合约
2. 调用 `_get_active_n_structure(db, sym, contract, tf)` 获取 N 结构
3. 如果存在，输出 A/B/C 时间戳和价格
4. 对比 matrix API 合约 vs klines API 合约是否一致
5. 输出每周期覆盖率统计（有 N 结构 / 无 N 结构）

**预期耗时**：15 分钟

### Step 2 — 时间戳对齐验证（1 Cycle）

**产出**：更新 `docs/qa/n-structure-annotation-diagnostic.md`

对每个有 N 结构的品种 × 周期：

1. 调用 `/api/klines` 般的 K 线查询（同步 SQL）
2. 输出 K 线 bar 的前 3 个和后 3 个时间戳
3. 输出 N 结构 A/B/C 时间戳
4. 检查 `findBarForNPoint()` 能否正确定位到预期 bar
5. 重点检查 1d/1w 时间戳归一化是否与 K 线 bar 对齐

**预期耗时**：15 分钟

### Step 3 — 根因定论 + 修复方案（1 Cycle）

**产出**：`docs/qa/n-structure-annotation-fix.md`

基于 Step 1 & 2 数据：

1. 确认根因（H1-H4 中哪个/哪些成立）
2. 如果 H1（合约不一致）：统一两路径的合约解析逻辑
3. 如果 H2（时间戳对齐）：修复 1d/1w 时间戳归一化在 K 线 bar 端的条件判断
4. 如果 H3（C4 波动）：评估是否在弹窗场景放宽 C4（skip_condition4）

**预期耗时**：15 分钟

### Step 4 — 实施修复（1-2 Cycle）

根据 Step 3 确定的根因实施修复，包括：
- 代码修改
- 验证（调用 API 确认修复效果）
- 更新共识

**预期耗时**：15-30 分钟

## 依赖顺序

```
Step 1 (数据采集) → Step 2 (时间戳对齐) → Step 3 (根因定论) → Step 4 (修复)
```

Step 1 和 Step 2 可以合并为一次诊断，如果脚本一次性采集足够的数据。

## 总预计

3-5 个 Cycle（含修复实施）
