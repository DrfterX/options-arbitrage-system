# Plan: Discord Webhook Alerting

## 目标
为 monito 添加 Discord Webhook 告警支持，与现有的 Slack/Email 告警形成完整通知体系。

## 拆解步骤

### Step 1 — Discord Alert 模块 + 类型扩展（当前 Cycle ✅）

**产出物：**
- `src/discord-alerter.ts` — Discord Webhook 客户端（与 `slack-alerter.ts` 同构）
- `src/types.ts` 更新 — 在 `Monitor` 和 `CreateMonitorRequest` 中添加 `discord_webhook_url` 字段
- `src/index.ts` — 在 cron handler 中并行发送 Discord 告警

**具体内容：**
- discord-alerter.ts: 支持 down/recovery 两种告警类型，Discord Embed 格式，5s 超时
- types.ts: `discord_webhook_url: string | null` 字段
- index.ts cron: 在 `alertPromises` 中加入 Discord 发送（与 Slack 平行的模式）
- index.ts alert defaults API: `GET/PUT /api/user/alert-defaults` 增加 `discord_webhook_url`
- index.ts monitor create: 支持 `discord_webhook_url` 参数

### Step 2 — Dashboard UI 集成

**产出物：**
- `dashboard-page.ts` 更新 — Add Monitor 表单增加 Discord Webhook URL 输入框
- `dashboard-page.ts` 更新 — Settings 页增加 Discord Webhook URL 配置
- End-to-end 可用

### Step 3 — 文档更新 + 部署

**产出物：**
- 更新 API 文档（docs-page.ts 或 docs/）
- wrangler deploy 确认
- 更新 changelog

## 依赖关系
Step 1 → Step 2 → Step 3（串行依赖，每一步基于上一步）

## Cycle 分配
- **Cycle #105**: Step 1 — Discord Alert 模块 + 后端集成
- **Cycle #106**: Step 2 — Dashboard UI 集成
- **Cycle #107**: Step 3 — 文档 + 部署验证
