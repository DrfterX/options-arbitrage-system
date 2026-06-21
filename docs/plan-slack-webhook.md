# Plan: Slack Webhook 告警集成

## 目标
为 monito 添加 Slack Webhook 告警通知，使 monitor 在宕机或恢复时能发送 Slack 消息，作为现有邮件告警的补充通道。

---

## 架构决策

### Webhook URL 存储策略
**决策：Monitor Level（每个 monitor 独立配置）**
- 每个 monitor 添加可选的 `slack_webhook_url` 字段
- 优点：最灵活，用户可将不同 monitor 的告警发送到不同 Slack 频道
- 简单：不需要新增用户设置表，只需加一个字段
- 邮件和 Slack 并行发送，用户可两者都配、只配其一、或都不配

### Slack Payload 格式
使用 Slack Incoming Webhook 标准格式（`text` + `attachments`）：

**宕机告警：**
```json
{
  "text": "🔴 *DOWN:* Monitor Name",
  "attachments": [{
    "color": "danger",
    "fields": [
      {"title": "URL", "value": "https://...", "short": true},
      {"title": "Status", "value": "503", "short": true},
      {"title": "Response Time", "value": "5000ms", "short": true},
      {"title": "Consecutive Failures", "value": "3", "short": true}
    ],
    "footer": "Monito · API Health Monitor",
    "ts": 1234567890
  }]
}
```

**恢复告警：**
```json
{
  "text": "✅ *RECOVERED:* Monitor Name",
  "attachments": [{
    "color": "good",
    "fields": [
      {"title": "URL", "value": "https://...", "short": true},
      {"title": "Status Code", "value": "200", "short": true},
      {"title": "Response Time", "value": "45ms", "short": true}
    ],
    "footer": "Monito · API Health Monitor",
    "ts": 1234567890
  }]
}
```

### 错误处理
- Slack API 调用失败（超时、无效 URL）→ 记录错误日志，不影响 cron 继续执行
- 不重试：Slack webhook 是无状态的，如果失败说明 webhook URL 有问题或 Slack 暂时不可用
- 有效但无法送达 → Slack 内部处理，不关我们事

### 安全性
- `slack_webhook_url` 存储在 D1 数据库中（现有 Monitor 表）
- 通过现有的 API Key auth 保护（所有 monitor API 已经需要鉴权）
- 在记录 CRUD 时不返回完整 URL 给客户端（仅返回 `has_slack_webhook: boolean`）
- Slack webhook URL 本身就是半秘密的（包含随机 token）

### 与现有告警系统的关系
- **并行发送**：邮件 + Slack 共存，互不替代
- 用户可选择配置其中任一、或两种都配

---

## 拆解步骤

### Step 1 — 数据库迁移 + 类型定义（1 Cycle）
- 在 `Env` 接口中添加可选的 `SLACK_WEBHOOK_URL` 全局 fallback
- 在 `Monitor` 接口添加 `slack_webhook_url: string | null`
- 在 `CreateMonitorRequest` 添加 `slack_webhook_url?: string`
- 创建 D1 migration 添加 `slack_webhook_url TEXT` 列
- 在 `db.ts` 的 CRUD 中处理新字段

### Step 2 — Slack 告警发送模块（1 Cycle）
- 新建 `src/slack-alerter.ts`
- 实现 `sendSlackAlert(webhookUrl, monitor, type: 'down' | 'recovery')`
- 构建 Slack 兼容的 JSON payload
- 错误处理和日志记录
- 超时控制（5s timeout）

### Step 3 — 集成到 cron handler（1 Cycle）
- 在 `index.ts` 的 `/cron/check` 和 `scheduled` 中：
  - 检测 monitor 是否有 `slack_webhook_url`
  - 有则并行调用 email alert + slack alert
- 用 `ctx.waitUntil` / `c.executionCtx.waitUntil` 非阻塞发送
- 为 slack alerter 也添加 `AlertLog` 记录（可选）

### Step 4 — 前端/产品页面更新（1 Cycle）
- 更新 product page 的创建/编辑 monitor 表单
- 添加 Slack Webhook URL 输入框
- 显示当前已配 Slack（仅显示 `has_slack` 标记，不暴露 URL）
- 更新 CLI 工具支持 `--slack-webhook` 参数

---

## 依赖顺序

```
Step 1 (DB + Types)
    ↓
Step 2 (Slack Sender) ← 可并行
    ↓
Step 3 (Cron Integration)
    ↓
Step 4 (Frontend)
```

Step 1 和 Step 2 可以并行执行，但为简单起见顺序执行。

---

## 各步骤预期耗时

| Step | 内容 | 耗时 |
|------|------|------|
| 1 | DB migration + 类型 | 10-15min |
| 2 | Slack 发送模块 | 10-15min |
| 3 | Cron 集成 | 10-15min |
| 4 | 前端更新 | 10-15min |
| **Total** | | **40-60min** |