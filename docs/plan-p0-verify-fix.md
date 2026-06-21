# P0(续) — N 型结构算法全周期验证修复

## 目标

对期货面板中所有活跃品种 × 所有周期（15m/1h/1d/1w），使用 **Live API** 验证 K 线浮窗的 A/B/C 四点标点符合 User Directives 定义的 N 型判定条件，修复发现的任何算法 / 数据问题。

## 上一轮验证结论（2026-06-19）

| 条件 | 失败数（248 条） | 说明 |
|------|:----------------:|------|
| C1 (方向) | 0 ✅ | 核心算法正确 |
| C2 (B→C 方向) | 0 ✅ | 核心算法正确 |
| C3 (C 不破 A) | **0** ✅ | ⚠️ 但验证脚本的 contract 过滤 bug 导致 124 条未验证 |
| C4 (第三笔方向) | 24 ❌ | 全为自然行情现象（第三笔未破位），非算法 bug |

**但 User Directives 确认 1h 仍有问题，且验证脚本有 bug，需要修复后重新验证。**

## 拆解步骤

### Step 1 — 修复 `_get_active_n_structure()` 缺失的 C3 防御性检查（1 Cycle）

**已确认问题**：
- `futures/shared.py` 中 `_get_active_n_structure()` 有 C2 检查但没有 C3 检查
- 动态重算的 `_update_c_point()` 虽有 C3 边界检查，但 `_get_active_n_structure` 缺了防御性 C3 校验
- 导致 C 点被 C-sliding 推过 A 后，结构仍被 API 返回

**产出物**：修复后的 `shared.py`

### Step 2 — 修复验证脚本 contract 过滤 bug + 重新验证（1 Cycle）

**已确认问题**：
- `scripts/verify_n_structure.py` 第 133 行 `WHERE symbol = contract` 过于严格
- 许多活跃品种（如 RU/RU2609, AG/AG2608）的主要合同不同名
- 导致 124/248 条标记为 N/A（实际上 swing points 存在）

**修复方案**：改为从 `futures_n_structures` 取活跃品种的 `(symbol, contract)` 对

**产出物**：修复后的验证脚本 + 新报告

### Step 3 — 根据验证结果修复发现的问题（1~2 Cycles）

基于 Step 2 的重新验证结果：
- 如仅 NI/CU 等个别品种问题 → 定点修复
- 如多个品种普遍存在 → 进一步排查

### Step 4 — 前端验证 + 更新共识（1 Cycle）

- K 线浮窗确认修复后的 ABC 标点
- 记录残留 C4 失败（正常现象）
- 更新共识标记 P0 全部完成

## 依赖顺序

```
Step 1 (C3修复) → Step 2 (脚本修复+重验) → Step 3 (问题修复) → Step 4 (验证)
```

Step 1 和 Step 2 可并行执行（不同文件）。

## 当前：Cycle #425 — Step 1：修复 C3 防御性检查

修复 `futures/shared.py` 中 `_get_active_n_structure()`，在 C2 检查之后添加 C3 检查，对 C 突破 A 的结构标记 COMPLETED 并返回 None。
