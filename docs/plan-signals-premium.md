# Plan: Signals Premium — 付费信号订阅服务

## 目标
在 signals.drifter.indevs.in 上增加付费订阅层，通过 Stripe Checkout 实现 $19/月付费墙，提供 Premium 精选信号内容。

## 技术背景

### 现有架构
- **后端**: Flask (Python) + SQLite, PM2 管理进程
- **前端**: Jinja2 模板 (portal.html, dashboard.html) + ECharts
- **部署**: PM2 → Nginx → Cloudflare 代理
- **数据库**: trading_system.db (SQLite)
- **支付参考**: `projects/monito/src/stripe.ts` — monito 有完整的 Stripe Checkout + Webhook 集成模式（Cloudflare Worker）

### 与 monito 的差异
monito 是 Cloudflare Worker (TypeScript)，Stripe 集成用 `stripe` npm 包 + `createFetchHttpClient()`。
Signals app 是 Flask (Python)，需要用 `stripe` Python 包，API 设计类似但语言栈不同。

## 拆解步骤

共 4 个 Cycle，每个 ≤20 分钟，一个 Cycle 独立完成。

### Step 1 — Stripe 后端集成

| 事项 | 内容 |
|------|------|
| **变更文件** | `web/app.py` (新增路由)、`requirements.txt` (加 stripe) |
| **新增文件** | 无（Stripe 逻辑直接嵌入 app.py 或新建 `web/stripe_handler.py`) |
| **具体改动** | ① `pip install stripe` → 更新 requirements.txt；② 新增 `POST /api/create-checkout-session` — 创建 Stripe Checkout Session（$19/月订阅），返回 session URL；③ 新增 `POST /api/stripe-webhook` — 处理 `checkout.session.completed` webhook，写入支付记录到 SQLite；④ 新增表 `premium_subscriptions(session_id, email, status, created_at)`；⑤ 配置 `STRIPE_SECRET_KEY` 和 `STRIPE_WEBHOOK_SECRET` 环境变量（.env 文件）；⑥ 新增 `GET /api/premium/status` — 检查 token/cookie 是否有效 |
| **产出物** | `web/stripe_handler.py`（Stripe 集成模块）|

### Step 2 — Premium 鉴权中间件 + 轻量认证

| 事项 | 内容 |
|------|------|
| **变更文件** | `web/app.py` (新增路由/中间件) |
| **具体改动** | ① 新增 `@require_premium` 装饰器，对 premium API 进行鉴权；② 成功支付后生成 Bearer Token（`secrets.token_urlsafe(32)`），存 SQLite；③ 前端 check 后存 localStorage，所有 premium 请求带 `Authorization: Bearer <token>` header；④ 提供 `/api/premium/verify-token?token=xxx` 供前端验证 |
| **产出物** | 鉴权装饰器 + Token 管理（放入 `web/stripe_handler.py`）|

### Step 3 — Premium UI（前端）

| 事项 | 内容 |
|------|------|
| **变更文件** | `web/templates/portal.html` |
| **具体改动** | ① 顶部导航新增 **Premium** tab（active 样式不同，金色标识）；② 点击 Premium → 未付费显示 Pricing Card 弹窗（$19/月，Stripe Checkout 按钮）；③ Pricing Card 设计：产品名 "Signals Premium"、功能列表（今日推荐/突破预警/TOP策略）、$19/mo CTA 按钮；④ 付费后 → Premium 内容页面（先空壳，Step 4 填充）；⑤ 添加必要的 CSS（portal.html 已有 terminal-luxe 风格） |
| **产出物** | `portal.html` 更新（Premium tab + Pricing Card）|

### Step 4 — Premium 内容 + 部署验证

| 事项 | 内容 |
|------|------|
| **变更文件** | `web/app.py` (新增 premium API endpoints)、`portal.html` |
| **具体改动** | ① 新增 `GET /api/premium/recommendations` — 今日推荐 3 品种（基于 N 型结构评分 + 共振）；② 新增 `GET /api/premium/breakout-alerts` — 距关键位 < 0.5% 的品种；③ 新增 `GET /api/premium/top-options` — 评分最高 2 个期权策略；④ 前端 Premium 页面展示以上 3 个板块；⑤ 部署：`pm2 restart options-trading` + curl 验证；⑥ 更新 `.env` 加入 Stripe Keys |
| **产出物** | Premium API + 内容页面 + 部署完成 |

## 不做事项（严格 MVP Scope）
- ❌ 用户注册系统 — Cookie/Token 鉴权即可
- ❌ 多级定价 — 只卖 $19/月 一个 SKU
- ❌ 后台管理面板 — 手动查 Stripe Dashboard
- ❌ 邮件通知
- ❌ 退款/取消流程 — 通过 Stripe Customer Portal 处理
- ❌ 自动续期提醒

## 协作流程

参照 `.claude/skills/team/SKILL.md` 的 Feature Development 流程：
`fullstack-dhh` → `qa-bach` → `devops-hightower`

鉴于 Stage 1-2 是纯后端，Stage 3 是前端，Stage 4 是混合，每步按需选人。

## 依赖顺序

```
Step 1 (Stripe后端)  ← 无依赖
Step 2 (鉴权中间件)  ← 依赖 Step 1（需要 stripe 包）
Step 3 (Premium UI)  ← 依赖 Step 2（需要 /api/premium/status）
Step 4 (内容+部署)   ← 依赖 Step 3（需要 Premium 页面框架）
```

## 风险

| 风险 | 影响 | 对策 |
|------|------|------|
| Stripe Python SDK 兼容问题 | 中 | Flask + stripe 包兼容性好，先行验证 |
| SQLite 并发写入 | 低 | PM2 single process, SQLite WAL mode |
| 国内用户 Stripe 支付 | 高 | Stripe 主要面向国际用户。MVP 先做 Stripe，后续加支付宝 |
| 无人付费 | 高 | 30 天止损线 → 恢复免费 |
