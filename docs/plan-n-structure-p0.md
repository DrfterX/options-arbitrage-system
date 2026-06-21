# Plan: N 型结构算法定义修正 + 动态刷新机制 (P0)

## 目标

**最终目标**：N 型结构的 A/B/C 三点定位完全符合正确定义，且行情更新后结构自动重算。

**本轮（Plan Cycle）产出**：本计划文件 + 共识更新。

---

## 现状分析

### 1. 算法定义现状

`futures/n_structure.py` 的 `_find_n_structure_forward()` 已经实现了**正确的向前非重叠扫描算法**：
- A = 第一个极值点（上升 N 型的低点/下降 N 型的高点）
- B = 交替类型（与 A 相反的极值），即第一笔的终点
- C = 与 A 同类型，即第二笔的终点
- 方向：B > A → LONG, B < A → SHORT
- C 不可突破 A（LONG: C > A, SHORT: C < A）
- 非重叠约束：找到 C 后跳到 C 之后继续扫描

**结论：算法定义基本上已与 User Directives 一致。**

但仍需：
- ✅ 与 User Directives 的 N 型正确定义逐条对照验证
- 🔲 `dynamic_restructure()` 的 A 突破迁移逻辑是否需要保留或简化
- 📝 编写单元测试覆盖边界情况

### 2. 动态刷新现状

当前刷新机制有两条路径：

**路径 A — API 驱动（pull-based）**
- `web/app.py` 每个 API 路由前调用 `_restructure_active_structures()`
- 包括：`/`（首页）、`/api/matrix`、`/api/n-structures`、`/api/klines`、`/api/premium/*`
- `/api/klines` 额外调用 `restructure_active_for_symbol()` 做品种级刷新
- 前端 5 分钟自动刷新 matrix，K 线弹窗 60s 刷新

**路径 B — Pipeline 驱动（batch）**
- `orchestrator.data_refresh()`：采集 → 聚合 → MACD → 极值点 → N 型结构（5 步完整链）
- 通过 `collect_all(trigger_restructure=True)` 也会触发

**核心缺失：没有数据到达后立即触发的实时重算机制。**
- 如果数据采集器在两次 pipeline 运行间写入了新 K 线，N 型结构直到下次 API 调用或 pipeline 运行才会更新
- 对依赖 N 型结构做实时决策（如突破检测、信号评分）的场景，这个延迟不可接受

### 3. K 线浮窗 A/B/C 标注现状

`futures_dashboard.html` 的 `drawKline()` 已经在 Canvas 上绘制：
- A/B/C 三个端点（彩色圆点 + 价格标签）
- A→B 和 B→C 线段（虚线）
- C→最新价作为第三笔方向提示（虚线 + 箭头）

**待验证：** A/B/C 的时间戳定位是否正确匹配 K 线端点的高/低价。

---

## 拆解步骤

每个步骤是一个 Cycle 能独立完成的粒度（≤20 分钟）。

### Step 1 — 验证 + 测试算法正确性

| 子任务 | 预期耗时 | 产出物 |
|--------|---------|--------|
| 1.1 编写单元测试，覆盖上升/下降 N 型 + 边界情况 | 15min | `tests/test_futures/test_n_structure.py` 新增用例 |
| 1.2 运行测试，验证当前算法是否符合定义 | 5min | 测试结果报告 |

**验证清单（逐条对照 User Directives）：**
- [ ] 上升 N 型：A=最低点, B=A之后第一笔最高点, C=B之后第二笔低点
- [ ] C > A（C 不能低于 A）成立
- [ ] 下降 N 型：A=最高点, B=A之后第一笔最低点, C=B之后第二笔高点
- [ ] C < A（C 不能高于 A）成立
- [ ] A→B→C 构成 V 型线段
- [ ] 从 C 到最新价是潜在第三笔
- [ ] 非重叠扫描：找到 C 后继续扫描后续结构
- [ ] `dynamic_restructure()` 的 A 突破迁移逻辑保持定义一致性

### Step 2 — 实现数据写后自动重算

| 子任务 | 预期耗时 | 产出物 |
|--------|---------|--------|
| 2.1 在数据采集路径中增加 N 型结构自触发的钩子 | 20min | `data/futures_collector.py` 改动 |
| 2.2 在 `futures_klines` 写入后触发对应品种的 restructure | 15min | 新模块或钩子 |

**设计方案：**
- **不引入 DB trigger**（SQLite 不适用于生产级 trigger 模式）
- 在 `futures_collector.py` 的 K 线写入方法中，写入成功后调用 `restructure_active_for_symbol()`
- 这样每次数据插入后立即重算，数据在 DB 中始终是最新的
- 限频控制：已有 `_should_full_recalc()` 的 30 秒间隔保护

### Step 3 — 增量刷新优化

| 子任务 | 预期耗时 | 产出物 |
|--------|---------|--------|
| 3.1 检查 `_restructure_active_structures()` 在 `/api/matrix` 高频调用性能 | 10min | 性能分析结果 |
| 3.2 如有性能问题：为 API 调用增加增量刷新模式 | 15min | 代码优化 |

**注意：** 当前 `restructure_all_active()` 调用 `restructure_active_for_symbol()`，
内部通过 `_should_full_recalc()` 做 30 秒频率控制，理论上不会有过热风险。
此步骤主要为验证和微调。

### Step 4 — K 线浮窗 A/B/C 标注验证与修正

| 子任务 | 预期耗时 | 产出物 |
|--------|---------|--------|
| 4.1 验证 A/B/C 时间戳定位到正确的 K 线端点（最值） | 10min | 验证报告 |
| 4.2 修正任何定位偏差 | 15min | `futures_dashboard.html` 改动 |

**验证点：**
- A 点的价格是否是目标 K 线端点（高/低）的极值
- B 点、C 点同理
- Canvas 渲染位置是否正确

---

## 依赖顺序

```
Step 1 (验证算法) ──→ Step 2 (动态刷新) ──→ Step 3 (增量优化) ──→ Step 4 (K线标注)
      │                      │                       │                     │
      ▼                      ▼                       ▼                     ▼
  必须优先          可以独立进行            可以独立进行         依赖 Step 1 确认
  验证算法定义      但依赖 Step 1            但依赖 Step 2        算法正确后验证
```

**最小可行第一 Cycle：** Step 1（验证 + 测试算法正确性）

---

## 风险 / Open Questions

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 算法已正确，User Directives 与代码同步不同步 | 中 | 浪费时间验证 | 快速运行测试验证，不要过度分析 |
| `dynamic_restructure()` 的逻辑与正确定义冲突 | 中 | 需要较大改动 | Step 1 中重点测试 A 突破前后的一致性 |
| 实时刷新增加 DB 写入压力 | 低 | 性能下降 | 已有 30s 频率控制，可进一步加限频 |
| 期权的 N 型结构是否也需要同样修正？ | 中 | 遗漏 | 在 Step 1 验证后做同类排查 |

---

## 当前 Step

**Step 1 — 验证 + 测试算法正确性**

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 1.1 | 编写单元测试，覆盖上升/下降 N 型 + 边界情况 | 15min | 测试代码 |
| 1.2 | 运行测试，验证当前算法是否符合定义 | 5min | 测试结果 |

当前 Cycle 计划：Step 1.1 编写 N 型结构单元测试。