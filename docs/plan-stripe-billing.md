# Plan: Step 2 — Stripe 计费集成

**Cycle**: #83 (Plan Cycle)
**Status**: 计划完成，待执行
**前置输入**:
- `docs/cfo/stripe-pricing-validation.md` — CFO 定价验证
- `docs/product/stripe-integration-flow.md` — Product 用户流程设计
- `docs/critic/stripe-premortem.md` — Critic Pre-Mortem（Cycle #29，条件已变化）
- `docs/plan-monito-saas-stripe.md` — 旧版计划（Cycle #29 DEFER）

---

## 目标

为 monito 接入 Stripe 计费，让 Pro plan（$5/mo）可购买。

## 上下文变化（重要）

上一轮 Pre-Mortem（Cycle #29）DEFER Stripe，因为当时 waitlist=3、没有注册流程。
**当前状态完全不同：**
- ✅ 注册流程已上线（POST /api/auth/signup）
- ✅ Magic Link 登录已上线
- ✅ API Key 自动生成 + 展示
- ✅ 产品页注册 CTA 已完成
- ✅ 已有用户系统（users表、plan字段、updateUserPlan）
- ✅ 12 个 monitors 持续运行中
- ⚠️ 0 个外部用户注册（仍需获客）

**结论**：Stripe 集成的先决条件（注册流程）已具备。但获客仍是瓶颈。建议：
- **先完成 Stripe 集成**（因为注册流程通了，就差收钱）
- **并行启动获客**（下一轮写技术博客/HN 发布）

---

## 技术架构决策

### 1. Stripe 集成方式

| 方案 | 优势 | 劣势 | 选择 |
|------|------|------|------|
| **Stripe Checkout（托管）** | 无需 PCI 合规，Stripe 处理 UI | 跳转到 Stripe 页面 | ✅ 推荐 |
| Stripe Elements（嵌入式） | 不跳转页面 | 需更多前端代码，PCI SA-A 合规 | ❌ 初期的复杂度 |

**决策**：使用 Stripe Checkout（托管支付页），Workers 端只创建 Checkout Session + 处理 Webhook。

### 2. Stripe SDK vs REST API

| 方案 | 优势 | 劣势 |
|------|------|------|
| **stripe-node SDK** | 官方签名验证、类型安全、自动重试 | Workers 兼容性需 `nodejs_compat` flag |
| Raw REST API | 无依赖、轻量 | 需手写签名验证、无类型安全 |

**决策**：使用 **stripe-node SDK**（已确认 `nodejs_compat` 兼容）。Pre-Mortem 指出 raw REST 的签名验证在 Workers 中需要特殊处理，SDK 规避了这个问题。

```bash
npm install stripe
```

### 3. Webhook CPU 超时问题

Pre-Mortem 指出的关键风险：Workers Free plan 的 CPU 时间限制（10ms/请求）。

**缓解方案**：
- Stripe Webhook 处理用 `c.req.raw` 获取原始 body
- Webhook 签名验证用 SDK 的 `stripe.webhooks.constructEvent()`
- 签名验证 + D1 查询 + D1 写入 在 Workers Paid 的 50ms CPU 限制下可行
- **当前先部署到现有 Workers，观察 CPU 消耗**
- 如果超时，再考虑升级 Workers Paid（$5/mo，和 Pro plan 同一价格）

### 4. 直接确认支付（Avoid Webhook Delay）

Product 设计中的关键方案：用户在 Stripe Checkout 成功后重定向回来时，**不等 webhook**，主动调用 Stripe API 验证 session 并升级 plan。

```
用户支付成功 → 重定向到 /payment/success?session_id=cs_xxx
  → 前端 GET /api/confirm-payment?session_id=cs_xxx
    → 后端用 Stripe SDK 查 session 状态
      → payment_status === 'paid' → 直接 updateUserPlan
    → 返回 plan 已升级
```

**这是 P0，因为：**
- Webhook 可能有延迟（秒级到分钟级）
- 用户付了钱但 plan 没更新 = 最差的体验
- Stripe API 查询是同步的，立即知道结果

---

## 定价方案（最终版）

| Plan | 价格 | Monitors | 检查间隔 | 告警 | 历史数据 |
|------|------|----------|---------|------|---------|
| Free | $0/月 | 5 | 5min | Email | 7天 |
| **Pro** | **$9/月**（年付 $90/年 = $7.5/月） | **20** | **1min** | **Email+Slack** | **30天** |
| Team | $24/月（年付 $240/年 = $20/月） | 50 | 30s | All+Webhook | 90天 |

> **重要**：根据共识中的 Open Questions，Pro plan 定价从 $5/mo 调整为 **$9/mo**。这更接近竞品水平（Pulsetic $9/mo、BetterStack $12/mo），且单位经济仍然极佳（毛利率 > 99%）。

### Stripe Price ID 配置

需要在 Stripe Dashboard 创建以下 Product 和 Price：

| Product | Price | Lookup Key | 类型 |
|---------|-------|------------|------|
| monito Pro | $9/月 | `pro_monthly` |  recurring |
| monito Pro | $90/年 (save 17%) | `pro_yearly` | recurring |
| monito Team | $24/月 | `team_monthly` | recurring |
| monito Team | $240/年 (save 17%) | `team_yearly` | recurring |

### 备用 Price ID（未激活，为未来调价预留）

| Product | Price | Lookup Key |
|---------|-------|------------|
| monito Pro (涨价备选) | $12/月 | `pro_monthly_v2` |
| monito Pro (涨价备选) | $120/年 | `pro_yearly_v2` |

---

## 拆解步骤（共 4 个 Cycle）

### **Cycle 1: Step 2.1 — Stripe Checkout Session + 基础模块**

| 子任务 | 预期耗时 | 文件 |
|--------|---------|------|
| npm install stripe + types 更新 | 5min | package.json, src/types.ts |
| src/stripe.ts — Stripe API 客户端 | 20min | src/stripe.ts |
| POST /api/stripe/create-checkout 端点 | 20min | src/index.ts |
| wrangler.toml 新增 STRIPE_SECRET_KEY | 5min | wrangler.toml |

**产出物**: `src/stripe.ts` + create-checkout 端点

### **Cycle 2: Step 2.2 — Stripe Webhook 处理**

| 子任务 | 预期耗时 | 文件 |
|--------|---------|------|
| POST /api/stripe/webhook 端点 | 15min | src/index.ts |
| Webhook 签名验证（SDK 原生） | 10min | src/stripe.ts |
| checkout.session.completed → updateUserPlan | 15min | src/stripe.ts |
| customer.subscription.deleted → 降级 free | 10min | src/stripe.ts |
| invoice.payment_failed → 日志 | 5min | src/stripe.ts |

**产出物**: Webhook 端点 + plan 更新逻辑

### **Cycle 3: Step 2.3 — 产品页定价 + 支付成功页**

| 子任务 | 预期耗时 | 文件 |
|--------|---------|------|
| 产品页添加 Pricing 段落 | 20min | scripts/generate-product-page.mjs |
| GET /payment/success HTML 路由 | 15min | src/index.ts |
| GET /api/confirm-payment 端点 | 15min | src/index.ts |
| 产品页 "Upgrade to Pro" CTA | 10min | scripts/generate-product-page.mjs |

**产出物**: 产品页 Pricing 展示 + 支付成功页

### **Cycle 4: Step 2.4 — 余下端点 + 集成测试**

| 子任务 | 预期耗时 | 文件 |
|--------|---------|------|
| GET /api/user 端点（展示 plan） | 15min | src/index.ts |
| 403 LIMIT_REACHED 响应加 upgrade_url | 10min | src/index.ts |
| POST /api/create-portal-session | 15min | src/index.ts |
| Stripe webhook 本地测试 | 20min | — |

**产出物**: 全链路闭环（注册 → 使用 → 被限制 → 升级 → 成功）

---

## 技术详情

### src/stripe.ts 模块设计

```typescript
// src/stripe.ts — Stripe API 客户端
import Stripe from 'stripe'

// 延迟初始化（Workers 冷启动优化）
let _stripe: Stripe | null = null
function getStripe(secretKey: string): Stripe {
  if (!_stripe) {
    _stripe = new Stripe(secretKey, {
      apiVersion: '2025-02-24',
      httpClient: Stripe.createFetchHttpClient(), // Workers 兼容
    })
  }
  return _stripe
}

// Price ID 常量（通过 env 或硬编码）
export const PRICE_IDS = {
  pro_monthly: 'price_pro_monthly',
  pro_yearly: 'price_pro_yearly',
  team_monthly: 'price_team_monthly',
  team_yearly: 'price_team_yearly',
} as const

// 创建 Checkout Session
export async function createCheckoutSession(
  stripeSecretKey: string,
  userId: string,
  userEmail: string,
  priceId: string,
  baseUrl: string
) {
  const stripe = getStripe(stripeSecretKey)
  return stripe.checkout.sessions.create({
    mode: 'subscription',
    customer_email: userEmail,
    client_reference_id: userId,
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${baseUrl}/payment/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${baseUrl}/pricing`,
    metadata: { user_id: userId },
  })
}

// 验证 Webhook 签名并解析事件
export async function constructWebhookEvent(
  stripeSecretKey: string,
  body: string | Buffer,
  signature: string,
  webhookSecret: string
) {
  const stripe = getStripe(stripeSecretKey)
  return stripe.webhooks.constructEvent(body, signature, webhookSecret)
}

// 确认支付（同步查询 Stripe Session）
export async function confirmPaymentSession(
  stripeSecretKey: string,
  sessionId: string
) {
  const stripe = getStripe(stripeSecretKey)
  return stripe.checkout.sessions.retrieve(sessionId)
}
```

### Webhook 路由设计（Hono）

```typescript
// src/index.ts — Webhook 路由
app.post('/api/stripe/webhook', async (c) => {
  const signature = c.req.header('stripe-signature')
  if (!signature) return c.json({ error: 'Missing stripe-signature' }, 400)

  const body = await c.req.text() // 原始 body（签名验证需要）
  const event = constructWebhookEvent(
    c.env.STRIPE_SECRET_KEY,
    body,
    signature,
    c.env.STRIPE_WEBHOOK_SECRET
  )

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object
      const userId = session.metadata?.user_id || session.client_reference_id
      if (userId) {
        await updateUserPlan(c.env.DB, userId, 'pro', 20)
      }
      break
    }
    case 'customer.subscription.deleted': {
      // 获取 customer_id → 查找用户 → 降级为 free
      // ...
      break
    }
  }

  return c.json({ received: true })
})
```

### 新增环境变量

```toml
# wrangler.toml — 新增
# secrets (wrangler secret put):
# STRIPE_SECRET_KEY       — Stripe Secret Key (sk_test_xxx / sk_live_xxx)
# STRIPE_WEBHOOK_SECRET   — Stripe Webhook Signing Secret (whsec_xxx)
```

### 幂等性处理

Stripe SDK 自动处理重试幂等性（`Idempotency-Key` header）。Webhook 处理本身是幂等的：
- `UPDATE users SET plan = 'pro'` — 执行多次结果不变
- `customer.subscription.deleted` — 多次执行也只会更新一次 plan

### 降级策略

当用户取消订阅后：
1. plan 降级为 'free'，max_monitors 设为 5
2. 超过 5 个的 monitors → **不删除，暂停检查**（Cron checker 中过滤）
3. 在 monitors 表加 `suspended_at` 字段，标记暂停
4. 30 天 grace period：用户重新订阅后恢复
5. 30 天后：清理被暂停的老 monitors 及其 check 记录

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| Workers CPU 超时导致 webhook 失败 | 低-中 | 高 | 使用 /api/confirm-payment 同步 fallback |
| Stripe SDK 在 Workers 中的兼容性问题 | 低 | 中 | 已确认 `nodejs_compat` + `createFetchHttpClient()` |
| 没有前端 dashboard，管理订阅困难 | 高 | 中 | 用 Stripe Customer Portal + /payment/manage 路由 |
| 0 个付费用户（获客瓶颈）| 中 | 中 | Stripe 集成后立即启动获客（博客/HN/Dev.to）|

---

## 执行清单（Cycle 1-4）

- [x] **Cycle 1**: npm install stripe, src/stripe.ts, create-checkout 端点 ✅
- [ ] **Cycle 2**: Webhook 端点, 签名验证, plan 升级/降级
- [ ] **Cycle 3**: 产品页 Pricing 段落, 支付成功页, confirm-payment
- [ ] **Cycle 4**: GET /api/user, upgrade_url, Customer Portal, 集成测试
- [ ] Staging 测试：在 staging 环境完成 E2E Checkout → Webhook 测试
- [ ] 上线后运行 `wrangler secret put STRIPE_SECRET_KEY`
- [ ] 上线后运行 `wrangler secret put STRIPE_WEBHOOK_SECRET`
- [ ] Stripe Dashboard 中配置 Webhook endpoint → `POST /api/stripe/webhook`