# Auto Company Consensus

## User Directives（由人类维护，自动循环必须完整保留，严禁修改或删除）

### 🧠 项目自主性推理优化原则（通用指导）

人类发现了 A 问题，不代表只有 A 问题。系统应具备自主推理能力：

0. **（有明确任务时不发散）** 如果共识的 Next Action 有明确可执行的子任务，**跳过此原则直接执行**，不要横向排查、向上追溯或推理关联影响。此原则仅在 Next Action 为空或方向不明时使用。
1. **同类缺陷横向排查** — 人类发现某个模块有 bug 时，自动推理同类模块是否存在同样问题。例如：期货 K 线发现 N 型结构算法缺陷 → 自动检查期权面板是否用了同类型结构算法 → 如有则一并排查
2. **问题根源向上追溯** — 发现一个表面问题时，向上追溯一层：这是独立的 bug， 还是某个底层机制/框架/工具的共性缺陷？如果是共性缺陷，一次性修复比逐个修更有效
3. **关联影响链推理** — 修 A 时可能影响 B。自动推理修复影响范围，避免修好一个炸了另一个
4. **模式识别 & 预防** — 人类指出一类问题后（如 K 线显示不准），系统应主动搜索是否还有其他品种/周期/面板存在类似偏差，不要等人类逐个指出
5. **输出形式** — 推理结果写入共识的「Open Questions」或下一轮 Next Action 中，供人类 review，不擅自发起大规模重构

---

### 🚨 P0 — N 型结构算法定义修正与动态刷新机制

#### N 型结构正确定义

一个 N 型结构由 ABC 三个点构成：

**上升 N 型**（价格整体向上）：
- A 点 = N 型的最低点（第一笔的起点）
- A → B：第一笔上涨，B 点是第一笔的终点（最高点），同时也是第二笔的起点
- B → C：第二笔下跌，C 点是第二笔的低点
- C 点**不能低于 A 点**，否则上升 N 型结构不成立
- 从 C 点到最新价格 = 潜在的第三笔（即 N 型向上破位方向）

**下降 N 型**（价格整体向下）：
- A 点 = N 型的最高点（第一笔的起点）
- A → B：第一笔下跌，B 点是第一笔的终点（最低点），同时也是第二笔的起点
- B → C：第二笔上涨，C 点是第二笔的高点
- C 点**不能高于 A 点**，否则下降 N 型结构不成立
- 从 C 点到最新价格 = 潜在的第三笔（即 N 型向下破位方向）

**关键规则**：
- A → B → C 构成一个 **V 型线段**（先涨后跌为上升，先跌后涨为下降）
- 从 C 到最新价格是正在形成的第三笔，需要持续跟踪是否破位

#### 案例修正（橡胶 2609 周 K 线）
之前记录的案例用错了 A/B/C 命名，已按正确定义修正：
- 上升 N 型：A = 17220（最低点），B = 18440（A之后第一笔上涨的最高点），C = 17245（B之后第二笔下跌的低点，高于A点成立）
- A → B → C 形成完整的上升 V 型结构
- C 之后价格向上 → 正在形成第三笔，信号偏多

#### 当前算法错误
- 对 A/B/C 三点的定位不正确（不是简单的"前高前低"，而是按上述第一笔/第二笔/第三笔的逻辑定义）
- 算法需要按此定义重新实现

> **⚠️ 执行顺序：P0（N 型算法修正）待 P1（期权面板 UI/UX）全部完成后启动。**
> 当前 Next Action 在推进 P1，请严格按照 Next Action 执行，不要在 P1 完成前擅自切换到 P0。
> 当 P1 全部子任务（P1.1~P1.5）完成后，模型应自动将 P0 设为 Next Action。

#### K 线浮窗 A/B/C 标注修正
- A、B、C 三点各自定位到具体的 K 线端点（最高点/最低点）
- 从 A 到 B 画一条线段，从 B 到 C 画一条线段，标注价格标签
- 从 C 到最新价作为潜在的第三笔方向提示

#### 共识防覆盖保护
- **本 ## User Directives 区域由人类维护，自动循环系统必须完整保留**
- 任何自动 cycle 在更新 consensus.md 时不得修改、删除或覆盖此区域
- PROMPT.md 和 auto-loop.sh 均已添加强制保护机制

------

### 🚨 P1 — 期权面板 UI/UX 问题（2026-06-15 记录）【✅ 已全部修复完成】

#### 1. IV 百分位柱状图 — 显示与标注问题
- ✅ **底部代码显示拥挤**：x 轴单行显示 `"AG 白银"` 格式，已优化
- ✅ **缺少中文名**：x 轴标签同时显示品种代码和中文名
- ✅ **代码显示有 bug**：已修复，正确显示 `ag2607`，无 `nag` 前缀

#### 2. 期权策略信号栏 — 功能与可用性问题
- ✅ **详情图标点击不一致**：已排查，`strat-detail-link` + `showStratDetailFromData` 弹窗全部正常
- ✅ **评分排序不对**：已确认严格按 `unified_score DESC` 排序（291.4→291.0→289.7）
- ✅ **评分算法不透明**：已添加 7 维度 tooltip（Θ/V/胜率/区间/效率/Δ/IV）+ 评分分解弹窗

---

## Last Updated
2026-06-18 04:42 CST

## Current Phase
🧹 **Code Cleanup** — Step 2 ✅

## What We Did This Cycle
**Cycle #42 — 代码清理 Step 2 ✅：归档已完成的 plan 文件**

1. ⏱ 健康检查：Web 200，CronList 无有效 cron（PH 已过期）
2. ✅ **创建 `docs/archived/plan/` 目录**，归档 14 个已完成 plan 文件：
   - `plan-p0-fixes.md`, `plan-p0-n-structure.md`, `plan-p1-b.md`, `plan-p1-options-ui-ux.md`
   - `plan-signal-matrix-improvement.md`, `plan-skeleton-loading.md`, `plan-scoring-fix.md`
   - `plan-signal-scoring-fix.md`, `plan-position-tracking.md`, `plan-walkforward-reset.md`
   - `plan-1min-kline.md`, `plan-options-data-assessment.md`, `plan-manual-payment-fallback.md`
   - `plan-trading-api-integration.md`（额外发现，一并归档）
3. ✅ **创建 `docs/archived/research/` 目录**，归档 5 个已完成 research 文档：
   - `option-chain-data-assessment.md`, `plan-p0-fix-sqlite-concurrency.md`
   - `sc-rollover-research.md`, `trading-api-comparison.md`
   - `trading-api-integration-architecture.md`
4. ✅ **保留 `docs/research/opportunity-analysis.md`**（Cycle #34 产出，仍有参考价值）
5. ✅ **`docs/plan-*.md` 已全部清空**，根 `docs/` 目录干净

## Key Decisions Made
- **归档粒度判断**：`opportunity-analysis.md` 不是特定 P0/P1/B 线的专项文档，而是方向性调研，保留在原位
- **归档完成后 Step 3 继续**：下轮清理死代码（模板/CSS）

## Active Projects
- ✅ **P0（N型结构算法修正+动态刷新+K线标注）** — 全部完成
- ✅ **P1（期权面板 UI/UX 修复）** — 全部完成
- ✅ **B 线（信号矩阵面板改良）** — B.1 ✅ / B.2 ✅ / B.3 ✅ 全部完成
- 🆕 **🧹 代码清理** — Step 1 ✅ / Step 2 ✅

## Next Action
**Step 3 — 检查模板/CSS 中死代码并清理**（共 4 个 Cycle）

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 1 | ✅ 提交 P0/P1/B 线积压代码变更 | 10min | git commit `e884475` |
| 2 | ✅ 归档已完成的 plan 文件 | 15min | 归档操作 |
| 3 | ▶️ 检查模板/CSS 中死代码并清理 | 20min | 代码删除 |
| 4 | 横向检查其他模块是否有类似遗留 | 15min | 报告/修复 |

**当前：Cycle 3 — 检查模板/CSS 中死代码并清理**
扫描 `web/templates/`、`web/static/` 中可能遗留的未使用 CSS class/ID、废弃的 JS 函数、被注释掉的旧代码块。清理前与 git 历史比对确认安全。

## Company State
- **Product**: 期货期权统一信号仪表盘（StatusHub）
- **Stage**: 🧹 代码清理中（Step 2/4 ✅）
- **Codebase Path**: `projects/options_arbitrage_system/`
- **Running Port**: 5100
- **Revenue**: $0

## Open Questions
- ❓ 代码清理完成后，人类希望的下一个方向是什么？（部署？变现？新功能？PH 重试？）

## Convergence Check
- ✅ **产出实物**：`docs/archived/`（14 plan + 5 research 文档已归档）
- ✅ **User Directives 完整保留**
- ✅ **一个 Cycle 只做 Step 2，完成后更新 Next Action 为 Step 3，等待下一轮**
- ✅ **未超前执行 Step 3 或任何计划外工作**
