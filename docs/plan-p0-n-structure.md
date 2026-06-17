# P0 — N 型结构算法修正 Plan

## 目标

修复 N 型结构检测算法的三个核心问题：

1. **A/B/C 三点定义核对** — 验证 `detect_and_save` 的 swing point → 结构映射逻辑是否符合 User Directives 定义的"第一笔/第二笔/第三笔"模型
2. **动态刷新机制** — 行情更新后结构自动重算（核心问题：Web API 路径只用 `dynamic_restructure`，缺少 `detect_and_save` 全量重算）
3. **K 线浮窗 A/B/C 标注修正** — 标注定位方式从"价格最近匹配"改为"时间最近匹配"

---

## 代码审计摘要

### 当前架构

```
Pipeline 扫描 (orchestrator.py)                 Web API (app.py)
        │                                              │
        ├─ detect_and_save()  ← 全量重算                ├─ dynamic_restructure()  ← 仅迁移
        └─ dynamic_restructure() ← 增量迁移              │
                                                        └─ (从不调用 detect_and_save)
```

### 审计发现

| 检查项 | 状态 | 说明 |
|--------|------|------|
| `detect_and_save`: A/B/C 类型交替检查 | ✅ | 正确：`T,P,T→LONG`, `P,T,P→SHORT` |
| `detect_and_save`: A→B 方向判定 | ✅ | 正确：`pb > pa → LONG`, `pb < pa → SHORT` |
| `detect_and_save`: C 不突破 A 约束 | ✅ | 正确：`LONG: C > A`, `SHORT: C < A` |
| `detect_and_save`: 滑窗选择逻辑 | ⚠️ | 从末尾最多尝试 3 个窗口，仅检查有效三点的最低要求 — 可能漏掉更远但更符合"N 型"语义的起点 |
| `dynamic_restructure`: A 突破迁移 | ✅ | 正确迁移 old_B→new_A，向后找 new_B/new_C |
| **`dynamic_restructure`: C 点更新** | ❌ | **只检查 A 突破/B 反转，不检查是否有更新的同类型 swing point 应成为新的 C 点** |
| **Web API 路径** | ❌ | **`api_klines` / `_restructure_active_structures` 只调 `dynamic_restructure`，不调 `detect_and_save`** |
| **K 线标注定位** | ❌ | `findBarForNPoint` 用价格最近匹配，应改为时间最近匹配 |

### 核心问题：动态刷新为什么失效

假设行情更新后 swing points 变成了 `[T(100), P(120), T(105), T(99)]`：

1. Pipeline 已经跑过一次，当前活跃结构是：A=100, B=120, C=105 (LEG3, LONG)
2. 新的行情产生新 swing point: TROUGH(99)
3. Web API 请求到达，调用 `dynamic_restructure`
4. `dynamic_restructure` 检查：A=100，最新最低价=99 → A 被跌破 （99 < 100）→ 触发迁移
5. 这是 **正确的**：新的最低点 99 导致原来的上升 N 型失效

但如果新 swing point 是 TROUGH(106)（高于 A=100）：

1. 当前活跃结构：A=100, B=120, C=105 (LEG3, LONG)
2. 新 swing point: TROUGH(106)
3. `dynamic_restructure` 检查：A=100 未突破 (106 > 100)，B=120 未反转 → 原结构不变
4. 但此时 C 点应该从 105 更新为 106（更新后的最低点）
5. **`dynamic_restructure` 缺少"更新 C 点"逻辑** → 结构停留在旧 C=105 不变

---

## 拆解步骤

### Step 1 — 算法定义核对 & 修复（1 Cycle）

| 工作项 | 说明 |
|--------|------|
| 1.1 | 对照 User Directives 定义，审查 `detect_and_save` 的 A/B/C 定位逻辑 |
| 1.2 | 修复滑窗选择逻辑：从最新 swing point 回溯时，应按"第一笔→第二笔→第三笔"的语义定位，而不是简单取最近的交替三点 |
| 1.3 | 修复 C 点约束检查：确保 `C.price > A.price (LONG)` / `C.price < A.price (SHORT)` 严格成立 |
| 1.4 | 运行时验证：用橡胶 2609 周 K 线数据跑一遍，确认 A=17220, B=18440, C=17245 |
| 产出 | 算法修正后的 `n_structure.py` + 通过的单元测试 |

**涉及文件：** `futures/n_structure.py`, `tests/test_futures/test_n_structure.py`

### Step 2 — 动态刷新机制（1-2 Cycles）

| 工作项 | 说明 |
|--------|------|
| 2.1 | 在 `_restructure_active_structures()` 和 `api_klines()` 中，**在调用 `dynamic_restructure` 之前先调用 `detect_and_save`**，确保全量重算先行 |
| 2.2 | 增强 `dynamic_restructure`：增加 C 点检查逻辑 — 如果最新的 swing point 与 C 同类型且更极端，更新 C 点价格和时间 |
| 2.3 | 增加缓存保护：`detect_and_save` 是全量重算（较贵），但 Web API 路径下访问频繁。考虑在 `_restructure_active_structures` 中降低频率：每 N 秒只全量重算一次，动态迁移可实时 |
| 2.4 | 单元测试：验证新的动态刷新路径覆盖 C 点更新场景 |

**涉及文件：** `futures/n_structure.py`, `web/app.py`, `tests/test_futures/test_dynamic_restructure.py`

### Step 3 — K 线浮窗 A/B/C 标注修正（1 Cycle）

| 工作项 | 说明 |
|--------|------|
| 3.1 | 修复 `findBarForNPoint`：从按"价格最近匹配"改为按"时间最近匹配" — A/B/C 点应定位到其 `point_a_time` / `point_b_time` / `point_c_time` 所在的那根 K 线 |
| 3.2 | 修复 AP 接口：`api_klines` 需同时返回当前 N 型结构的 `point_a_time/price`、`point_b_time/price`、`point_c_time/price`，供前端时间匹配 |
| 3.3 | 增加 fallback：如果该时间戳在 K 线数据中没有精确匹配的 bar，用最接近时间戳的 bar |
| 3.4 | 线段标注保持：A→B 用虚线线段连接，B→C 用虚线线段连接，各自标注价格标签 |

**涉及文件：** `web/app.py`, `web/templates/futures_dashboard.html`

---

## 依赖关系

```
Step 1 (算法定义核对)
  │
  └──→ Step 2 (动态刷新) — 依赖算法定义正确后才能实现正确的动态重算
         │
         └──→ Step 3 (K线标注) — 依赖 Step 2 返回正确的 A/B/C 时间数据
```

**实际可以并行：** Step 1 和 Step 3 无代码依赖（前端标注和算法核算是独立的）。

**推荐执行顺序：** Step 1 → Step 2 → Step 3（先确保定义正确，再修复刷新，最后修标注）

---

## 风险与注意事项

| 风险 | 影响 | 缓解 |
|------|------|------|
| `detect_and_save` 全量重算频率过高 | API 响应变慢 | 加频率控制（每 30-60 秒内对同一 symbol/tf 只全量重算一次） |
| C 点更新逻辑与 A 突破迁移冲突 | 迁移后结构不正确 | 迁移逻辑只在 A 被突破时触发，C 点更新只在 A 未突破时 |
| 前端标注改时间匹配后浮窗显示异常 | 用户看到错误标记 | 确保 time<->bar 匹配有 fallback，价格标签锚点可靠 |
| P0 算法改动影响现有信号产生 | 已有做单逻辑变化 | 改动后跑一次全品种 N 型重算，对比新旧结果差异 |

---

## 测试策略

- **Step 1 验证**：用橡胶 2609 周线产出的 A/B/C 必须 = 17220/18440/17245
- **Step 2 验证**：构造 C 点需要更新的场景，确认 `dynamic_restructure` 正确更新 C 点价格和时间
- **Step 3 验证**：前端请求 `/api/klines?symbol=RU&timeframe=1w`，确认返回的 A/B/C 时间戳映射到正确的 K 线端点

---

## 如果只做一步

如果时间有限，**Step 2（动态刷新）是优先级最高的单独步骤**，因为它解决的是"行情更新后结构不自动更新"的核心问题。Step 2 中可以按以下简化方案执行：

在 `web/app.py` 的 `_restructure_active_structures` 中：

```python
# 在 dynamic_restructure 之前先调用 detect_and_save（带频率控制）
from futures.n_structure import detect_and_save
# 每 30 秒全量重算一次（用 DB 中的 updated_at 时间戳做门控）
# 其余时间增量更新走 dynamic_restructure 不变
```

这是改动最小、收益最大的修法。