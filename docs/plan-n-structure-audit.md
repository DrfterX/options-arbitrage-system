# P0 — N 型结构算法审计与验证计划

**Cycle**: #241
**状态**: 📋 计划编制中
**范围**: 验证 N 型结构算法在所有周期的正确性 + 动态刷新机制有效性

---

## 背景

User Directives（2026-06-18 更新）提出：
> ABC 点已标出来了，线段也连上了，但算法判定逻辑需要再修。
> 核心问题：算法没有先判断是上升 N 型还是下降 N 型，导致标点混乱

此前 P0 已于 Cycle #198-205 按 `docs/plan-n-structure-fix.md` 执行完成，包括：
- P0.1: 方向判定算法修复 ✅
- P0.2: 所有周期验证 ✅（CEO 决定关闭）
- P0.3: 动态刷新机制 ✅

但人类仍在 consensus 中标记为待修复。本计划进行一次完整审计验证。

---

## 审计方法

### 阶段 1：代码审计（已验证）

已在 Cycle #241 执行：

| 检查项 | 状态 | 详请 |
|--------|:----:|------|
| `_find_n_structure_forward()` 前向扫描 | ✅ | 从最早极值点开始前向扫描，非重叠 |
| `_determine_direction()` 方向判定 | ✅ | B > A → LONG, B < A → SHORT |
| 方向-点类型一致性校验 | ✅ | LONG→A=TROUGH, SHORT→A=PEAK (n_structure.py L218-220) |
| C 不破 A（LONG: C > A, SHORT: C < A） | ✅ | L228-230 |
| B→C 方向确认（LONG: C < B, SHORT: C > B） | ✅ | L236-239 |
| 条件4（最新价 vs C 点） | ✅ | detect_and_save L318-330 |
| 动态重算（`dynamic_restructure`） | ✅ | A突破迁移 / B反穿COMPLETED / C滑动 |
| 接入点（API + Data Collector + Pipeline） | ✅ | 4个独立触发点 |

### 阶段 2：测试审计（已验证）

| 测试套件 | 用例数 | 状态 |
|---------|:------:|:----:|
| `test_n_structure.py` | 55 | ✅ 全部通过 |
| `test_dynamic_restructure.py` | 23 | ✅ 全部通过 |
| `test_integration_n_structure.py` | 10 | ✅ 全部通过 |
| **总计** | **88** | **✅ 全部通过** |

### 阶段 3：生产数据验证（已验证）

RU2609 在 2026-06-18 19:10 CST 实时 API 返回：

| 周期 | 方向 | A | B | C | 条件验证 |
|:----:|:----:|:---:|:---:|:----:|:--------:|
| 15m | SHORT | 17860 | 17660 | 17785 | C>A❌(SHORT不需) C<A✅ C>B✅ last<C✅ |
| 1h | SHORT | 17665 | 17465 | 17650 | C<A✅ C>B✅ last<C? 17750>17650 ⚠️ |
| 1d | **LONG** | **17220** | **18440** | **17245** | **C>A✅ C<B✅ last>C✅** |
| 1w | **LONG** | **17220** | **18440** | **17555** | **C>A✅ C<B✅ last>C✅** |

**关键发现**：日线和周线的 ABC 标点与 User Directives 完全一致（A=17220, B=18440, C=17245/17555）。

**1h 异常发现**：最新价 17750 > C=17650，对 SHORT 方向应使条件4（latest < C）不满足。可能的解释：
- 1h K 线最新收盘价可能不同步（数据库 close vs 实时 close）
- 或 dynamic_restructure 后结构尚未被条件4淘汰（`skip_condition4=True` 在 `dynamic_restructure` 中跳过）

### 阶段 4：横向排查（建议）

根据 User Directives 中的「项目自主性推理优化原则」第 0 条：当 Next Action 明确时不发散。当前 Next Action 明确为 P0 审计 → 横向排查推迟到发现实际 bug 后。

---

## 结论

### 算法正确性：✅ 已验证通过

算法（`_find_n_structure_forward`）已正确实现 User Directives 中定义的全部 4 条判定条件，包括先判定方向再标点。88 个测试全部通过。生产数据验证 RU2609 日线/周线 ABC 标点正确。

### 动态刷新机制：✅ 已验证通过

- API `/api/klines` 每请求调 `restructure_active_for_symbol(force_full_recalc=True)`
- Data Collector 每 K 线插入后调 `restructure_all_active()`
- Pipeline 每信号扫描调 `dynamic_restructure()`

### 唯一未关闭项：1h SHORT 条件4 检查

1h 周期的 SHORT 结构最新价 > C 但仍在活跃。需排查：
- 是 `skip_condition4` 的标志问题？
- 还是 `_get_active_n_structure` 的条件4已淘汰但 `dynamic_restructure` 重新写了？

---

## 建议 Next Action

**Step 2 — 修复 1h SHORT 条件4 异常 + 关闭 P0**

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 2.1 | 定位 1h SHORT 条件4失效根因 | 15min | bug 分析 |
| 2.2 | 修复 bug | 10min | 代码修复 |
| 2.3 | 更新 plan-n-structure-fix.md 标记 P0 完成 | 5min | 文档更新 |

**当前：Cycle #241 — [计划阶段✅] 等待进入执行阶段**

---

## 执行记录（Cycle #257）

**根因定位**：`dynamic_restructure()` 无条件将 `is_active` 设为 `True`（即使 `detect_and_save` 已因条件4将结构标记为 IDLE），导致条件4不满足的结构被重新激活。

**修复**：添加 `was_idle` 标志位追踪 DB 状态，无结构性变动时保持 IDLE 状态。

**验证**：`dynamic_restructure` 测试从 23 → 24 个（新增 `test_was_idle_no_reactivation`），全部 89 个 N 型结构测试通过。全部 186 个期货测试通过。

**✅ P0 全线关闭**