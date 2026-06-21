# P0.1 — N 型结构算法偏差分析

> **目标**：分析 `futures/n_structure.py` 当前 N 型算法实现与 User Directives 正确定义之间的偏差，不修改代码。
>
> 本文档为后续 P0.2（重写方向判断 + ABC 标点逻辑）、P0.3（逐周期验证）、P0.4（动态重算触发）提供技术依据。

---

## 1. User Directives 核心定义回顾

### 上升 N 型
1. A = 最低点（TROUGH）
2. A → B：第一笔上涨，B = 第一笔终点（PEAK）
3. B → C：第二笔下跌，C = 第二笔低点（TROUGH）
4. C > A（否则上升 N 型不成立）
5. 最新价 > C（潜在第三笔向上破位）

### 下降 N 型
1. A = 最高点（PEAK）
2. A → B：第一笔下跌，B = 第一笔终点（TROUGH）
3. B → C：第二笔上涨，C = 第二笔高点（PEAK）
4. C < A（否则下降 N 型不成立）
5. 最新价 < C（潜在第三笔向下破位）

### 关键原则
- **先判断方向（上升/下降），再按方向逻辑筛选满足条件的 ABC 三点**
- 所有周期（15m/1h/1d/1w）算法逻辑一致

---

## 2. 当前代码架构总览

```
futures/n_structure.py (1010 行)
├── 方向判断: _determine_direction()          # A→B 价格比较
├── 辅助: _get_swing_points(), _get_klines()
├── 核心检测: _merge_same_type() → _find_n_structure_forward() → detect_and_save()
│   ├── _merge_same_type():       合并连续同向极值
│   ├── _find_n_structure_forward(): 前向非重叠扫描 ABC
│   └── detect_and_save():        读取极值 + 全量检测 + 条件4 + DB 写入
├── 动态重算: dynamic_restructure() → _update_c_point()
│   ├── dynamic_restructure():    A 突破/B 反穿/C 滑动处理
│   └── _update_c_point():        C 点滑动 + 阈值防突破 + 结构优度验证
├── 共享入口: restructure_active_for_symbol()
└── 突破检测: check_15m_breakout(), check_realtime_breakout()

futures/shared.py → _get_active_n_structure()  # 读取活跃结构 + 多重校验
web/app.py → API 层 → 返回 ABC 点到前端 K 线浮窗
```

---

## 3. 逐项偏差分析

### 3.1 偏差 A —「方向优先」语义 vs 实际实现

| | User Directives 要求 | 当前实现 |
|---|---|---|
| **方向判断时机** | 先判断整体方向（上升/下降），再筛选 ABC 点 | 从 A→B 价格比较局部判断方向 |
| **判断依据** | 整体 swing point 序列形态 + 最新趋势 | 仅靠 A→B 两个点的价格高低 |
| **影响** | 方向与整体趋势一致 | 可能找到局部方向正确但整体趋势矛盾的 ABC |

**代码位置**：`_determine_direction()` (第 46-58 行) + `_find_n_structure_forward()` (第 252-256 行)

**具体场景演示**：

```
极值序列: TROUGH(90) → PEAK(100) → TROUGH(85) → PEAK(95) → TROUGH(80)
           ↑原始最低点  ↑反弹高点    ↑创新低      ↑反弹但更低  ↑再创新低

整体趋势: 持续下跌（每个 PEAK 更低，每个 TROUGH 更低）

算法选 A=TROUGH(90), B=PEAK(100):
  direction = LONG (100 > 90)
  C=TROUGH(85): C < B(85<100✓), C < A(85<90→INVALID!)

跳过此组合，尝试:
  A=TROUGH(90), B=PEAK(95) (跳过 PEAK100):
  direction = LONG (95 > 90)
  C=TROUGH(80): C < B(80<95✓), C < A(80<90→INVALID!)

最终 → IDLE
```

**问题**：整体是下跌趋势，但算法试图从 TROUGH(90) 开始找上升 N 型，全部失败后才可能找到下降结构（如 A=PEAK(100) → B=TROUGH(85) → C=PEAK(95)）。效率低下且在某些边界可能选错。

**本质问题**：算法没有预先识别"当前是上升还是下降趋势"，而让方向从局部 A→B 推断。

---

### 3.2 偏差 B — 方向-类型一致性检查的粒度问题

**代码位置**：`_find_n_structure_forward()` 第 262-264 行

```python
if (direction == "LONG" and a["point_type"] != "TROUGH") or \
   (direction == "SHORT" and a["point_type"] != "PEAK"):
    continue  # 跳过当前 B，尝试下一个 B
```

**问题**：当方向与 A 类型不匹配时，`continue` 跳过的是**当前 B**（继续 b loop），而不是跳过当前 A 尝试下一个 A。这意味着：

- A=PEAK, direction=LONG（即第一笔上涨但起点是高点→矛盾）
- 代码会尝试不同的 B（后续 TROUGH），但 A 仍是 PEAK 不会变
- 对于 TROUGH→TROUGH→...→PEAK 的情况，只有第一个 TROUGH 是有效的 A，但代码会遍历所有 TROUGH 和 PEAK 组合

**实际影响**：极端情况下，如果当前 A 类型错误但附近有多个交替类型极值，算法会在同一点上循环多次，直到 b loop 耗尽才 `i += 1` 换 A。这会浪费算力但不改变最终结果。

**严重程度**：低。最终结果不受影响（会试到正确组合），但效率略低。

---

### 3.3 偏差 C — 条件 4（第三笔方向确认）的位置

| | User Directives 要求 | 当前实现 |
|---|---|---|
| **条件 4 位置** | 定义中的第 5 条，是 N 型判定的一部分 | 在 `detect_and_save()` 中（第 362-384 行），不在 `_find_n_structure_forward()` 中 |
| **检查阶段** | 算法筛选时 | DB 写入前 |
| **影响** | 方向+ABC 标点同时考虑最新价 | ABC 先标好，最后才检查最新价 |

**代码位置**：`detect_and_save()` 第 362-384 行

**问题**：如果用一个「方向优先」的算法，方向判断时就应该考虑最新价是否在 C 的合理方向（上升 N 型的最新价应高于 C）。目前的实现把条件 4 放在最后，意味着算法先选 ABC 再判断是否有效，可能导致：

- 选了 ABC，但条件 4 不满足 → IDLE → C 点白选了
- 如果有更好的候选结构满足条件 4，但被第一个找到的结构提前截断了（非重叠扫描）

**严重程度**：中。非重叠扫描可能在条件 4 检查之前就锁定了结构。

---

### 3.4 偏差 D — COMPLETED 判定逻辑可能过度严格

**代码位置**：`detect_and_save()` 第 390 行

```python
if best["a_idx"] > 0 and merged[best["a_idx"] - 1]["point_type"] == pa["point_type"]:
    state = NState.COMPLETED.value
```

**问题**：如果 A 的前一个极值点与 A 同类型，就判定为 COMPLETED。但 "A 的前一个点同类型" 不一定意味着旧结构已结束，也可能只是合并过程中被保留下来的相邻极值。

**示例**：`TROUGH(95) → TROUGH(90) → PEAK(110) → TROUGH(100)`
合并后：`TROUGH(90) → PEAK(110) → TROUGH(100)`
- a_idx = 0（TROUGH90），前一个不存在 → LEG3 ✓

但如果：`TROUGH(100) → TROUGH(90) → PEAK(110) → TROUGH(100)`（没有合并，都是交替）
- A=TROUGH(90) at idx=1，merged[0]=TROUGH(100)，同类型 → COMPLETED

这就把有效的上升 N 型（90→110→100）标记为已完成，不合理。

**严重程度**：中。可能导致有效结构被过早标记为 COMPLETED，从 K 线图上消失。

---

### 3.5 偏差 E — 非重叠扫描可能跳过有效候选

**代码位置**：`_find_n_structure_forward()` 第 291 行

```python
i = c_idx + 1  # 非重叠：下一结构从 C 之后开始
```

**问题**：找到 ABC 后跳到 C 之后。如果 C 和下一个有效 A 之间还有更好的 A 候选，会被跳过。

**示例**：
```
P(100) → T(80) → P(110) → T(95) → P(105) → T(90)
                 ^^^^^^^^
             被 C 位置截断
```

算法先找到 P100→T80→P110（SHORT），跳到 C=P110 之后，T95 被跳过。但如果 T95 才是更好的起点，就被遗漏了。

**实际上**：非重叠扫描是**有意的设计选择**，User Directives 没有要求全局最优，所以这不一定是"偏差"。

**严重程度**：低。属于设计取舍，不是 bug。

---

### 3.6 偏差 F — dynamic_restructure 的 A 突破检测使用 K 线数据而非极值点

**代码位置**：`dynamic_restructure()` 第 590-597 行

```python
latest_high = max(k["high"] for k in klines)
latest_low = min(k["low"] for k in klines)

a_broken = (direction == "LONG" and latest_low < a_price) or \
           (direction == "SHORT" and latest_high > a_price)
```

**问题**：A 突破检测使用最新 K 线的最高/最低价，而不是极值点。这意味着：
- 如果某根 K 线的影线短暂突破了 A 点，即使实体价格没有真正确认突破，也会判定 A 被突破
- 极值点检测已经过滤了噪声（需要左右各 N 根 K 线确认），但 A 突破检测直接使用未过滤的 K 线数据

**影响**：可能产生误触发迁移。

**严重程度**：中。可能导致结构在不应迁移时迁移。

---

### 3.7 偏差 G — 方向-类型一致性检查在 migration 与 detect 之间不一致

**detect_and_save** 通过 `_determine_direction()` + 类型检查来确保方向匹配。

**dynamic_restructure** 有独立的类型检查（第 686-693 行）：
```python
if (new_direction == "LONG" and new_a_type != "TROUGH") or \
   (new_direction == "SHORT" and new_a_type != "PEAK"):
    # fallback to detect_and_save
```

两者逻辑一致，但 `dynamic_restructure` 的 new_A = old_B 的固定逻辑（第 655-657 行）：
```python
old_b_type = "PEAK" if direction == "LONG" else "TROUGH"
new_a_price = b_price
```

这意味着迁移后的新 A 始终是 old_B 的价格。如果 old_B 是 PEAK，迁移后新 A 也是 PEAK（满足 SHORT 需要 A=PEAK），但如果新方向是 LONG，就会 fallback。这是正确的。

**严重程度**：低。逻辑一致。

---

## 4. 跨周期验证风险

### 4.1 当前算法结构

`_find_n_structure_forward()` 完全与周期无关——它只处理 `merged` 极值点列表，不关心是 15m 还是 1w。

**风险**：不同周期的 swing point 密度不同：
- 15m：极值点多，合并后序列长，前向扫描能找到更多结构
- 1w：极值点少，可能只有 3-5 个点，选择空间小

**影响**：15m 周期可能因极值点密集 + 非重叠扫描而"锁定"在早期结构上，即使后续出现了更好的候选。

### 4.2 swing point 检测的周期差异

`futures/swing_points.py` 的 `detect_swing_points()` 使用可配置的 `window_n`（SWING_WINDOWS）。不同周期的窗口大小不同，导致：
- 大窗口（周线）：只检测大幅波动，极值点数量少
- 小窗口（15m）：检测细微波动，极值点数量多

这本身不是 bug，但需要确保 `_find_n_structure_forward()` 在不同密度的极值点序列下都能正确选点。

---

## 5. 动态刷新机制分析

### 5.1 当前刷新路径

```
新 K 线到达
  → restructure_active_for_symbol()
    → incremental_update()     # 更新极值点
    → aggregate_klines()       # 聚合周线
    → detect_and_save()        # 全量重算（限频 5 秒）
    → dynamic_restructure()    # 增量迁移（不限频）
```

### 5.2 刷新链的关键依赖

| 步骤 | 输入 | 产出 | 问题 |
|---|---|---|---|
| ① 新 K 线 → DB | 数据采集器 | `futures_klines` 表插入 | 可能失败但不阻塞 |
| ② `incremental_update` | K 线数据 | `futures_swing_points` 更新 | 窗口大小依赖配置 |
| ③ `aggregate_klines` (周线) | 日 K 线 | 周 K 线聚合 | 仅周线周期需要 |
| ④ `detect_and_save` | 极值点 | 新 N 型结构 | **限频 5 秒** |
| ⑤ `dynamic_restructure` | 活跃结构 + K 线 | 结构迁移/滑动 | A 突破用 K 线数据 |

**主要问题**：步骤 ④ 限频 5 秒意味着在最坏情况下，新 K 线到达后最多 5 秒才能触发全量重算。对于 15m 周期这个延迟可以接受，但对于更敏感的实时场景可能有延迟。

### 5.3 条件 4 破坏的刷新盲区

当条件 4 不满足 → `detect_and_save` 返回 IDLE → `dynamic_restructure` 读不到活跃结构（`_get_active_n_structure` 返回 None）→ 回退到全量重算。

这本身是正确的，但意味着：
1. 行情小幅回调导致条件 4 暂时不满足 → 结构被标记 IDLE
2. 行情恢复 → 触发新的 `detect_and_save`
3. 新结构可能与旧结构方向相同但 ABC 点不同

**结果**：K 线浮窗上的 ABC 标签可能在小幅回调后跳变。

---

## 6. 与前端 K 线浮窗的接口分析

### API 返回格式（`web/app.py` 第 1363-1365 行）

```javascript
("A", d["point_a_price"]),
("B", d["point_b_price"]),
("C", d["point_c_price"]),
```

前端 `drawKline()` 函数（`futures_dashboard.html` 第 1370 行）接收 `nA, nB, nC, nDir, nAt, nBt, nCt`，通过时间戳匹配 K 线位置，画 A→B→C 线段。

### 潜在问题

1. **ABC 时间戳与 K 线对齐**：前端通过时间戳 `nAt/nBt/nCt` 在 K 线数组中定位 ABC 位置。如果时间戳不精确（如 swing point 的 timestamp 是 K 线开盘时间或极值点检测时间），可能导致标记线画在错误位置。
2. **无最新价标记**：API 不返回最新价/最新价位置，前端无法在 K 线上画 C→最新价的第三笔方向线。

---

## 7. 总结：需要修复的核心问题

| 编号 | 偏差 | 严重程度 | 影响范围 | 修复方案方向 |
|------|------|---------|---------|------------|
| **A** | 方向不是优先判断而是从 A→B 推断 | 🔴 **高** | 所有周期全部品种 | P0.2: 加整体方向预判 |
| **C** | 条件 4 检查在 detect 最后而非算法核心 | 🟡 中 | 条件 4 敏感场景 | P0.2: 整合到核心算法 |
| **D** | COMPLETED 判定可能过度严格 | 🟡 中 | 交替序列短的周期 | P0.2: 改判定条件 |
| **F** | A 突破检测使用 K 线而非极值点 | 🟡 中 | dynamic_restructure | P0.4: 改用极值点 |
| **G** | 非重叠扫描跳过候选 | 🟢 低 | 极值点密集周期 | 设计取舍，可不修 |
| **H** | 动态重算限频 + 条件 4 刷新盲区 | 🟡 中 | 实时性 | P0.4: 优化限频策略 |

### 修复优先级

1. **P0.2 核心算法重写**：
   - 实现方向优先（先判断上升/下降整体趋势，再筛选 ABC）
   - 将条件 4 整合到核心算法中
   - 修复 COMPLETED 过度判定

2. **P0.3 逐周期验证**：
   - 对每个活跃品种 × 每个周期验证 ABC 标点
   - 用修改后的算法重新计算，对比 DB 中的旧数据

3. **P0.4 动态重算优化**：
   - A 突破检测改用极值点
   - 优化条件 4 刷新盲区
   - 适当调整限频策略