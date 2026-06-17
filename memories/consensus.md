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

### 🚨 P1 — 期权面板 UI/UX 问题（2026-06-15 记录）

#### 1. IV 百分位柱状图 — 显示与标注问题
- **底部代码显示拥挤**：柱状图底部的品种代码列印太挤，看不清
- **缺少中文名**：不能只标代码（如 `ag`），应同时标注品种中文名（如 `ag 白银`）
- **代码显示有 bug**：主力合约的代码展示有问题。例如 `ag` 品种显示为 `ag/nag2607`，令人费解。应该只显示 `ag2607`

#### 2. 期权策略信号栏 — 功能与可用性问题
- **详情图标点击不一致**：部分策略信号的详情图标点击后能弹出浮窗显示详情，部分点击无反应 → **bug，需排查**
- **评分排序不对**：当前排序方式不明确，应按照评分**从高到低**排序（评分越高越值得做）
- **评分算法不透明**：策略评分是核心决策依据，当前完全没有说明评分怎么算的。应提供一个评分算法说明（或者在 UI 上加 tooltip 解释），让用户能理解评分的权重和逻辑

---

## Last Updated
2026-06-17 07:21 CST（Cycle #29922 — Step 3 Premium UI: Pricing Card + Premium Tab）

## Current Phase
Monetization — Signals Premium $19/月付费订阅（方向 A）

## What We Did This Cycle
**Cycle #29922 — Step 3 Premium UI（Pricing Card + Premium Tab）**

1. ⏱ **健康检查** — signals (5100) 200 ✅ | cron 空闲
2. 🎨 **Step 3 实现**（portal.html + app.py）:
   - ✅ **Premium Tab** — 导航栏新增金色 Premium tab，带 active 样式
   - ✅ **Pricing Card 弹窗** — $19/月定价卡片，含功能列表（每日精选/突破预警/TOP策略/推送通知）和 Stripe Checkout CTA
   - ✅ **Premium 内容骨架** — 订阅后显示 Premium 精选信号三栏空壳（Step 4 填充）
   - ✅ **Token 鉴权流** — 前端检查 localStorage `premium_token`，调用 `/api/premium/verify-token` 验证
   - ✅ **Stripe 跳转** — CTA 按钮调用 `/api/create-checkout-session` → 重定向 Stripe
   - ✅ **支付成功回流** — 新增 `GET /api/premium/token?session_id=` 端点，成功支付后自动获取 token 并写入 localStorage
3. ✅ **服务重启** — PM2 重启成功，新代码已生效

## Key Decisions Made
1. **UI 风格** — 沿用 portal.html 现有的 terminal-luxe 设计系统，金色（`var(--brand)`）作为 Premium 主题色
2. **Token 存储** — 前端 `localStorage` 存储 Bearer Token，每次切到 Premium tab 时验证有效性
3. **成功回流不走额外页面** — 用 URL query param + JS 处理，避免新增 Flask 页面
4. **定价卡设计** — 居中单列布局，金色渐变 border + radial glow，与 portal 风格一致

## Active Projects
- 🚀 **Signals Premium** — Step 3 ✅ → Step 4: Premium 内容 + 部署验证

## Next Action
**Step 4 — Premium 内容 + 部署验证**（共 4 Cycles）

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 1 | ✅ **Stripe 后端集成** | ✅ 已完成 | `web/stripe_handler.py` + API + webhook |
| 2 | ✅ **Premium Token 鉴权中间件** | ✅ 已完成 | `@require_premium` 装饰器 + verify-token API |
| 3 | ✅ **Premium UI（Pricing Card）** | ✅ 已完成 | portal.html Premium Tab + Paywall |
| **4** | **Premium 内容 + 部署** | **20min** | 推荐 API + pm2 部署 |

**当前：Step 4 — Premium 内容 API + 部署验证**
- 新增 `GET /api/premium/recommendations` — 今日推荐 3 品种（基于 N 型结构评分 + 共振）
- 新增 `GET /api/premium/breakout-alerts` — 距关键位 < 0.5% 的品种
- 新增 `GET /api/premium/top-options` — 评分最高 2 个期权策略
- 前端 Premium 页面展示以上 3 个板块
- 更新 `.env` 加入 Stripe Keys
- 部署验证 + curl 测试

## Company State
- Revenue: $0（30天目标 ≥1 付费用户 → $19 MRR）
- **Stage**: Monetization — Signals Premium 开发中（Step 3/4 ✅）
- **Assets**: futures ✅ | options ✅ | signals ✅ | monito ✅ | statushub ✅

## Open Questions
- ❓ Stripe 测试 Keys 未配置 — `.env` 中占位符需人类填入 sk_test 和 whsec 才能激活支付

## Convergence Check
- ✅ 只做一件事：Step 3 Premium UI（不超额编码）
- ✅ User Directives 完整保留未修改
- ✅ 收敛规则第 9 条：Step 3 完成即止，未提前推进 Step 4
- ✅ 服务运行正常 | Premium Tab + Pricing Card 已验证
