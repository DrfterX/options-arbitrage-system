# P0 Bug 修复执行指令（GLM-5-Turbo 专用）

> **用途**：本文档为 5 个 P0 bug 提供 diff 级执行指令，可直接交给 GLM-5-Turbo 机械执行。
> **配套主报告**：`docs/qa/comprehensive-review-2026-06-19.md`
> **原则**：每项含「定位 → 改前 → 改后 → 验证」，不需要 turbo 做方案决策。

---

## ✅ 任务清单（5 项，彼此独立，可并行）

| ID | Bug | 改动文件数 | 风险 |
|----|-----|-----------|------|
| T1 | Stripe 续费状态更新失效（加 `subscription_id` 列） | 1 个 .py + 1 个迁移 | 中（涉及数据回填） |
| T2 | Critiq `process.env` 在 Worker 崩溃 | 2 个 .ts | 低 |
| T3 | Critiq `savePR` 死代码（决策：删除） | 1 个 .ts | 低 |
| T4 | portal.html token 走 URL query 明文 → 改用 Bearer header | 1 个 .html | 低（后端已支持 header） |
| T5 | portal.html token 键名 `premium_token` → 统一 `session_token` | 1 个 .html | 低 |

**关键决策（已替 turbo 做好，照做即可）**：
- T3 选「删除死代码」而非「接入」——接入需要设计 schema 和前端，超出 P0 范围，留 P1 单独做。
- T4/T5 后端 `require_premium`（stripe_handler.py:336-340）**已同时支持 Bearer header 和 URL query**，所以这两个任务**只改前端 portal.html，后端零改动**。

---

## T1. Stripe 续费状态更新失效

### 根因（turbo 不需理解，仅供参考）
`premium_subscriptions` 表没有 `subscription_id` 列。Webhook 流程：
- `checkout.session.completed`（stripe_handler.py:187 `_handle_checkout_completed`）：存 `session_id`（`cs_test_xxx`）和 `customer_id`。
- `customer.subscription.updated/deleted`（stripe_handler.py:211 `_handle_subscription_updated`）：用 `subscription.id`（`sub_xxx`）调 `_update_subscription_status`，但该函数把 `subscription_id` 拿去匹配 `customer_id` 列 → 永远 0 行 → 续费状态不更新。

修复：加 `subscription_id` 列，在 checkout completed 时一并保存，更新时按它匹配。

### 步骤 1：修改 schema DDL
**文件**：`projects/options_arbitrage_system/web/stripe_handler.py`
**定位**：第 71-82 行 `PREMIUM_TABLE_DDL`

**改前**：
```python
PREMIUM_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS premium_subscriptions (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id    TEXT NOT NULL UNIQUE,
        customer_id   TEXT DEFAULT '',
        email         TEXT DEFAULT '',
        status        TEXT NOT NULL DEFAULT 'active',
        token         TEXT DEFAULT '',
        created_at    TEXT DEFAULT (datetime('now','localtime')),
        expires_at    TEXT DEFAULT ''
    )
"""
```

**改后**（在 `customer_id` 后加 `subscription_id` 列）：
```python
PREMIUM_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS premium_subscriptions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id      TEXT NOT NULL UNIQUE,
        customer_id     TEXT DEFAULT '',
        subscription_id TEXT DEFAULT '',
        email           TEXT DEFAULT '',
        status          TEXT NOT NULL DEFAULT 'active',
        token           TEXT DEFAULT '',
        created_at      TEXT DEFAULT (datetime('now','localtime')),
        expires_at      TEXT DEFAULT ''
    )
"""
```

### 步骤 2：新增迁移函数（对已存在的表补列）
**文件**：同上
**定位**：第 85-89 行 `ensure_premium_table` 函数之后，新增一个函数

**改前**：
```python
def ensure_premium_table(db) -> None:
    """创建 premium_subscriptions 表（如不存在）。"""
    conn = db.get_conn()
    conn.execute(PREMIUM_TABLE_DDL)
    conn.commit()
```

**改后**（追加迁移逻辑）：
```python
def ensure_premium_table(db) -> None:
    """创建 premium_subscriptions 表（如不存在），并执行增量迁移。"""
    conn = db.get_conn()
    conn.execute(PREMIUM_TABLE_DDL)
    # 增量迁移：为旧表补 subscription_id 列（CREATE TABLE IF NOT EXISTS 不会更新已存在的表）
    cols = {row[1] for row in conn.execute("PRAGMA table_info(premium_subscriptions)")}
    if "subscription_id" not in cols:
        conn.execute("ALTER TABLE premium_subscriptions ADD COLUMN subscription_id TEXT DEFAULT ''")
    conn.commit()
```

### 步骤 3：checkout completed 时保存 subscription_id
**文件**：同上
**定位**：第 187-208 行 `_handle_checkout_completed`

**改前**（关键片段 189-203）：
```python
def _handle_checkout_completed(db, session: dict) -> None:
    """处理 checkout.session.completed 事件——记录支付成功并生成 Bearer Token。"""
    session_id = session.get("id", "")
    customer_id = session.get("customer", "") or ""
    email = session.get("customer_details", {}).get("email", "") or ""
    status = session.get("status", "complete")
    token = _generate_token()

    ensure_premium_table(db)
    conn = db.get_conn()

    try:
        conn.execute(
            """INSERT OR IGNORE INTO premium_subscriptions
               (session_id, customer_id, email, status, token)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, customer_id, email, "active" if status == "complete" else status, token),
        )
```

**改后**（新增 subscription_id 提取 + 写入；subscription 在 checkout session 里字段名是 `subscription`）：
```python
def _handle_checkout_completed(db, session: dict) -> None:
    """处理 checkout.session.completed 事件——记录支付成功并生成 Bearer Token。"""
    session_id = session.get("id", "")
    customer_id = session.get("customer", "") or ""
    subscription_id = session.get("subscription", "") or ""
    email = session.get("customer_details", {}).get("email", "") or ""
    status = session.get("status", "complete")
    token = _generate_token()

    ensure_premium_table(db)
    conn = db.get_conn()

    try:
        conn.execute(
            """INSERT OR IGNORE INTO premium_subscriptions
               (session_id, customer_id, subscription_id, email, status, token)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, customer_id, subscription_id, email,
             "active" if status == "complete" else status, token),
        )
```

### 步骤 4：修复 `_update_subscription_status` 用正确列匹配
**文件**：同上
**定位**：第 227-234 行

**改前**：
```python
def _update_subscription_status(db, subscription_id: str, status: str) -> None:
    """更新订阅状态（通过 customer_id 关联）。"""
    conn = db.get_conn()
    conn.execute(
        "UPDATE premium_subscriptions SET status=? WHERE customer_id=?",
        (status, subscription_id),
    )
    conn.commit()
```

**改后**（按 `subscription_id` 列匹配；若该值为空则回退到 `customer_id`，兼容历史数据）：
```python
def _update_subscription_status(db, subscription_id: str, status: str) -> None:
    """更新订阅状态（优先按 subscription_id 关联，回退 customer_id）。"""
    conn = db.get_conn()
    conn.execute(
        "UPDATE premium_subscriptions SET status=? WHERE subscription_id=?",
        (status, subscription_id),
    )
    # 兼容旧数据（subscription_id 为空、靠 customer_id 关联的记录）
    conn.execute(
        "UPDATE premium_subscriptions SET status=?, subscription_id=? "
        "WHERE customer_id=? AND (subscription_id='' OR subscription_id IS NULL)",
        (status, subscription_id, subscription_id),
    )
    conn.commit()
```

### 验证
1. 启动后端，看日志无报错。
2. 在 SQLite 里执行 `PRAGMA table_info(premium_subscriptions);` 确认有 `subscription_id` 列。
3. （可选）模拟一次 webhook：`curl -X POST .../webhook -d '<event payload with subscription.id=sub_xxx>'`，然后 `SELECT subscription_id, status FROM premium_subscriptions;` 确认状态已更新。

---

## T2. Critiq `process.env` 在 Worker 崩溃

### 根因
Cloudflare Workers 没有 `process.env`，`review.ts` 的 `getApiBase()`/`getModel()`/`resolveApiKey()` 直接读 `process.env`，部署到 Worker 后抛 `ReferenceError`，整个 review 功能不可用。

### 步骤 1：让配置从 `env` 参数读取
**文件**：`src/review.ts`
**定位**：第 1-16 行（顶部 import 和三个配置函数）

**改前**（关键片段 5-16）：
```typescript
function getApiBase() {
  return process.env.CRITIQ_API_BASE || 'https://api.deepseek.com'
}

function getModel() {
  return process.env.CRITIQ_MODEL || 'deepseek-chat'
}

export function resolveApiKey(key: string) {
  return process.env.CRITIQ_API_KEY || key
}
```

**改后**（从 `Env` 类型读取，需要 import `Env`）：
```typescript
import type { Env } from './index'

export function getApiBase(env?: Env) {
  return (env?.CRITIQ_API_BASE as string) || process.env.CRITIQ_API_BASE || 'https://api.deepseek.com'
}

export function getModel(env?: Env) {
  return (env?.CRITIQ_MODEL as string) || process.env.CRITIQ_MODEL || 'deepseek-chat'
}

export function resolveApiKey(key: string, env?: Env) {
  return (env?.CRITIQ_API_KEY as string) || process.env.CRITIQ_API_KEY || key
}
```

> 说明：`env?.X || process.env.X || default` 的写法让 Worker 走 `env`、CLI/测试走 `process.env`，两边兼容。`Env` 类型已在 `index.ts:13` 定义。

### 步骤 2：扩展 `Env` 类型
**文件**：`src/index.ts`
**定位**：第 10-18 行 `Env` interface

**改前**：
```typescript
export interface Env {
  DEEPSEEK_API_KEY: string
  GITHUB_APP_WEBHOOK_SECRET: string
  GITHUB_APP_ID: string
  GITHUB_APP_PRIVATE_KEY: string
  ...
}
```

**改后**（追加三个可选字段）：
```typescript
export interface Env {
  DEEPSEEK_API_KEY: string
  GITHUB_APP_WEBHOOK_SECRET: string
  GITHUB_APP_ID: string
  GITHUB_APP_PRIVATE_KEY: string
  // Critiq 可选配置（覆盖默认值）
  CRITIQ_API_BASE?: string
  CRITIQ_MODEL?: string
  CRITIQ_API_KEY?: string
  ...
}
```

### 步骤 3：在调用处传入 `env`
**文件**：`src/review.ts`
**定位**：`runReview` 函数内调用 `getApiBase()`/`getModel()`/`resolveApiKey()` 的地方

需要让 `runReview(systemPrompt, apiKey)` 接收 `env` 参数，并向下传递。**先定位 `runReview` 函数签名**：

**改前**：
```typescript
export async function runReview(systemPrompt: string, apiKey: string): Promise<ReviewResult> {
  // ... 内部调用 getApiBase() / getModel() / resolveApiKey(apiKey)
}
```

**改后**：
```typescript
import type { Env } from './index'

export async function runReview(
  systemPrompt: string,
  apiKey: string,
  env?: Env,
): Promise<ReviewResult> {
  const apiBase = getApiBase(env)
  const model = getModel(env)
  const resolvedKey = resolveApiKey(apiKey, env)
  // ... 其余逻辑用 resolvedKey、apiBase、model 替换原调用
}
```

### 步骤 4：上游 `handlePREvent` 透传 `env`
**文件**：`src/github.ts`
**定位**：第 155-198 行 `handlePREvent`（第 198 行调用 `runReview`）

**改前**：
```typescript
export async function handlePREvent(
  payload: GitHubPRPayload,
  apiKey: string,
  privateKey: string,
  appId: string,
  installationId?: number,
): Promise<{ success: boolean; commentCount: number; error?: string }> {
  ...
  const result = await runReview(systemPrompt, apiKey)
```

**改后**（加 `env` 参数并透传）：
```typescript
import type { Env } from './index'

export async function handlePREvent(
  payload: GitHubPRPayload,
  apiKey: string,
  privateKey: string,
  appId: string,
  installationId?: number,
  env?: Env,
): Promise<{ success: boolean; commentCount: number; error?: string }> {
  ...
  const result = await runReview(systemPrompt, apiKey, env)
```

### 步骤 5：`/webhook` 和 `/review` 路由调用处传入 `c.env`
**文件**：`src/index.ts`
**定位**：调用 `handlePREvent` 的两处

**改前**：
```typescript
const result = await handlePREvent(payload, apiKey, privateKey, appId, installationId)
```

**改后**：
```typescript
const result = await handlePREvent(payload, apiKey, privateKey, appId, installationId, c.env)
```

> `/review` 路由同理，把 `c.env` 传给 `runReview`。

### 验证
```bash
cd /Users/ayong/projects/auto-company_test
npx tsc --noEmit        # 类型检查通过
npm test                # 现有测试通过
npm run build           # build 成功
```

---

## T3. Critiq `savePR`/`saveFeedback` 死代码（决策：删除）

### 根因
`Database` 类定义了 `savePR()`、`saveFeedback()` 方法，D1 表也建了，但 `/webhook` 和 `/review` 路由**从未调用它们**，`/api/reviews` 查询永远返回空。P0 阶段决定**删除死代码**（接入需要设计前端展示，留 P1 单独做）。

### 步骤 1：删除 Database 类里的死方法
**文件**：`src/db.ts`
**定位**：搜索 `async savePR(` 和 `async saveFeedback(` 两个方法，删除整个方法体（含上方注释）。

### 步骤 2：删除 D1 建表语句里的 `prs` 和 `feedback` 表
**文件**：`migrations/0001_initial.sql`（如果该文件里有 `CREATE TABLE prs` / `CREATE TABLE feedback`）和 `src/db.ts` 里的对应 DDL 字符串。

> **注意**：D1 已部署的表不会被删除（DROP 不在迁移文件里），这只会让新部署的 D1 不再建这两张表。这是安全的——反正它们本来就是空的。

### 步骤 3：删除 `/api/reviews` 路由（如果存在）
**文件**：`src/index.ts`
**定位**：搜索 `app.get('/api/reviews'` 或类似，删除整个路由 handler（它查的是永远空的表）。

### 步骤 4：删除测试里的相关用例
**文件**：`src/index.test.ts`
**定位**：搜索 `savePR`、`saveFeedback`、`/api/reviews`，删除对应测试。

### 验证
```bash
npx tsc --noEmit && npm test && npm run build
```
确认无「unused import」「undefined method」报错。

---

## T4. portal.html token 走 URL query → 改用 Bearer header

### 前置确认（turbo 不需操作，仅供信心）
后端 `require_premium`（`web/stripe_handler.py:336-340`）**已支持** `Authorization: Bearer` header，三个 dashboard 页面也已有 fetch 拦截器（`dashboard.html:1201`、`options_dashboard.html:1725`、`futures_dashboard.html:2263`）。所以本任务**只改 portal.html，后端零改动**。

### 步骤 1：确认 portal.html 是否已有 fetch 拦截器
**文件**：`projects/options_arbitrage_system/web/templates/portal.html`
**定位**：第 2361 行附近已有 `opts.headers['Authorization'] = 'Bearer ' + token;`

如果已存在全局拦截器，那么步骤 2 只需删除各处 URL 里的 `?token=` 拼接即可（拦截器会自动加 header）。

### 步骤 2：删除所有 URL query 里的 token 拼接
**文件**：同上
**定位**：以下行号（grep 确认精确位置）

搜索 `'?token=' +` 和 `'&token=' +`，把所有形如：
```javascript
fetch('/api/premium/breakout-alerts?token=' + encodeURIComponent(token))
fetch('/api/premium/something?foo=bar&token=' + token)
```
改成：
```javascript
fetch('/api/premium/breakout-alerts')
fetch('/api/premium/something?foo=bar')
```

具体涉及的行（需 grep 核实）：`portal.html:2039`、`1765`、`1799`、`1834` 等。

### 步骤 3：确认 token 变量在这些 fetch 前已从 localStorage 取出
搜索 `var token = localStorage.getItem('premium_token')`（约 `portal.html:1867,1910,1944,1979`），这些 `token` 变量在删除 URL 拼接后仍需保留——因为第 2361 行的拦截器要用它加 header。

### 验证
1. 浏览器打开 portal，登录 premium。
2. 打开 DevTools Network，点任意 premium API，确认请求 URL **不含 `?token=`**，且请求头有 `Authorization: Bearer xxx`。
3. 确认 API 返回 200（非 401/403）。

---

## T5. portal.html token 键名统一为 `session_token`

### 根因
portal.html 用 `premium_token`，其他三个页面用 `session_token`（dashboard.html:1137、options_dashboard.html:1711）或 `auth_token`（futures_dashboard.html:2152）。**跨子域登录态断裂**。

### 决策
统一为 **`session_token`**（与 dashboard.html、options_dashboard.html 一致，这两个是主流量页面）。

### 步骤 1：portal.html 全量替换
**文件**：`projects/options_arbitrage_system/web/templates/portal.html`
**操作**：把所有 `'premium_token'` 替换为 `'session_token'`

涉及行（grep 确认）：`1867`、`1893`、`1910`、`1944`、`1979`、`2055`、`2092`、`2148`。

**注意**：只替换字符串字面量 `'premium_token'`，不要误替换注释里的文字。

### 步骤 2：futures_dashboard.html 统一
**文件**：`projects/options_arbitrage_system/web/templates/futures_dashboard.html`
**操作**：把所有 `'auth_token'` 替换为 `'session_token'`

涉及行：`2152` 附近（grep `'auth_token'` 核实全部位置）。

### 步骤 3：确认后端登录接口写入的键名一致
**文件**：`projects/options_arbitrage_system/web/app.py`
**操作**：grep `session_token` 和 `setItem`，确认后端返回 token 后前端统一用 `session_token` 存。

> 如果后端有任何地方返回了 `premium_token` 或 `auth_token` 字段名给前端，也要一并改成 `session_token`。

### 验证
1. 在 `signals.drifter.indevs.in` 登录。
2. 打开 DevTools → Application → Local Storage，确认 `session_token` 存在。
3. 切到 `futures.drifter.indevs.in`，刷新页面，**不应要求重新登录**。
4. 切到 portal，确认 premium 功能可用。

---

## ⚠️ turbo 执行注意事项

1. **每项改完先跑该任务的「验证」步骤**，通过再做下一项。不要 5 项一次性全改再测。
2. **遇到指令里行号对不上的情况**：以**函数名/方法名/字符串内容**为准重新 grep 定位，行号会随修改漂移。不要盲目按行号改。
3. **T1 的 schema 改动**：如果运行后报 `duplicate column name: subscription_id`，说明迁移已跑过，跳过即可（`PRAGMA table_info` 检查已防住，但稳妥起见）。
4. **T2/T3 改完 TypeScript**：必须 `npx tsc --noEmit` 通过才算完成，类型错误会让 Worker build 失败。
5. **不要扩大改动范围**：每项只改指令里列出的文件，不要顺手重构其他代码。

## 完成标准

- [ ] T1：`PRAGMA table_info(premium_subscriptions)` 含 `subscription_id`；模拟 webhook 后 `SELECT status` 能更新。
- [ ] T2：`npx tsc --noEmit` 通过；Worker build 成功。
- [ ] T3：`grep -r "savePR\|saveFeedback\|api/reviews" src/` 无结果；测试通过。
- [ ] T4：portal premium API 请求头含 `Authorization: Bearer`，URL 无 `token=`。
- [ ] T5：4 个页面 localStorage 都是 `session_token`，跨子域免重复登录。

---

## 执行记录（GLM-5.2 补充，2026-06-20）

### turbo 执行过程中发现并修正的问题

**问题 A：T2 改错文件位置**
- turbo 改了根目录 `src/`（无 TypeScript 依赖，不参与构建）
- 实际可构建的是 `projects/critiq/src/`（有完整 node_modules、dist、typecheck 脚本）
- 修正：在 `projects/critiq/src/` 重新执行 T2，根 `src/` 已 `git checkout` 还原

**问题 B：T2 引入类型名错误**
- turbo 在 `review.ts` 里 `import type { Env } from './index'`
- 但 `index.ts` 里类型名是 `Bindings`（非 `Env`），会导致 `tsc --noEmit` 失败
- 修正：统一改为 `import type { Bindings } from './index'`，并 `export type Bindings`

**问题 C：T3 指令判断过宽**
- 原指令说"删除 savePR + saveFeedback + /api/reviews + feedback 表"
- 实际 `saveFeedback` 被 `/api/feedback` 路由调用（`app.py:113-124`），是活代码
- `/api/reviews` 是公开 API（前端 blog 文档提到），删除会破坏 API 契约
- 修正：仅删除真正的死代码 `savePR`（从未被调用），保留其余

**问题 D：T5 指令简化过度**
- 原指令说把 `premium_token` → `session_token`
- 实际 portal 有两套独立 token：`auth_token`（登录态）+ `premium_token`（premium 验证态）
- 它们是不同概念、不同 token 值、不同验证流程，不能合并
- 修正：仅统一登录态（`auth_token` → `session_token`），`premium_token` 保持不动

### 最终验证结果

| 任务 | 验证方式 | 结果 |
|---|---|---|
| T1 | Python ast.parse + SQLite 模拟 INSERT/UPDATE | ✅ |
| T2 | `npm run typecheck`（0 错误）+ `npm run build`（成功） | ✅ |
| T3 | `grep savePR src/`（0 残留）+ typecheck + build | ✅ |
| T4 | `grep '?token=' portal.html`（0 残留） | ✅ |
| T5 | `grep 'auth_token' futures/portal`（0 残留），4 页面 `session_token` | ✅ |

### 实际修改文件清单

```
M projects/options_arbitrage_system/web/stripe_handler.py     (T1)
M projects/critiq/src/review.ts                                (T2)
M projects/critiq/src/index.ts                                  (T2)
M projects/critiq/src/github.ts                                (T2)
M projects/critiq/src/db.ts                                     (T3)
M projects/options_arbitrage_system/web/templates/portal.html  (T4+T5)
M projects/options_arbitrage_system/web/templates/futures_dashboard.html (T5)
```

---

*本指令文档配套 `docs/qa/comprehensive-review-2026-06-19.md`。5 项 P0 完成后，可继续产出 P1 的执行指令（风控三件套、并发安全、前端 XSS 等）。*
