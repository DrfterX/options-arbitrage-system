# Plan: Step 6 — 完善监控配置

> 文档类型: 实施计划 (Cycle #20)
> 创建日期: 2026-06-12
> 状态: 已批准

---

## 目标

**实现基于 `check_interval` 的智能检查频率控制**，让不同 monitor 按不同频率被检查，同时修复 Docker Hub 被限流（429）问题和 httpstat.us/503 的 CF 520 误报问题。

## 核心发现（Cycle #20 分析）

### 问题 1：间隔过滤从未实现 ⚠️

`getActiveMonitors()` 的 SQL 是 `SELECT * FROM monitors WHERE status IN ('unknown', 'up', 'down')` — 所有活跃 monitor 每次 cron 都被检查。虽然每个 monitor 有 `check_interval` 字段，但谁也没用它过滤。

影响：Docker Hub 每分钟被请求一次，触发 429 限流。

### 问题 2：Docker Hub 429 被误判为 "up" 

`checker.ts` 认为 `response.status >= 200 && response.status < 500` 就是成功。429 在 200-500 范围内，所以被记为 "up"。实际上是限流状态。

### 问题 3：httpstat.us/503 被 CF 返回 520

CF 边缘拦截 `/503` 路径返回 520（`html httpstat.us/503 - 520 from cloudflare`）。这是 CF 的 HTTP 状态码测试页面被边缘阻断，不是我们 monitor 的问题。

## 实施步骤

### 步骤 1：修改 `db.ts` — `getActiveMonitors()` 添加间隔过滤

```typescript
// 现在的 SQL：
"SELECT * FROM monitors WHERE status IN ('unknown', 'up', 'down')"

// 改为：
"SELECT * FROM monitors WHERE status IN ('unknown', 'up', 'down')
   AND (last_check_at IS NULL 
     OR datetime(last_check_at, '+' || CAST(check_interval AS TEXT) || ' seconds') <= datetime('now'))"
```

逻辑：
- `last_check_at IS NULL` → 从未检查过的 monitor（新添加的），需要立即检查
- `last_check_at + check_interval <= now` → 距离上次检查已经过了它的间隔周期，可以再查

这个 SQL 在 D1 上测试过语义正确。12 个 monitor 的小数据集不需要索引优化。

### 步骤 2：更新 Docker Hub 的检查间隔为 120s

通过 `wrangler d1` 或 API 直接执行 UPDATE：

```sql
UPDATE monitors SET check_interval = 120 WHERE url LIKE '%hub.docker.com%'
```

减少频率可以缓解 429 限流。

另外，在 checker.ts 中给 429 打一个元数据标记，不多做处理但便于后续诊断。

### 步骤 3：替换 httpstat.us/503 为更稳定的端点

httpstat.us 被 Cloudflare 边缘误拦截返回 520。替换为 `httpstat.us/503?sleep=100` 或改用 HTTPBin：

目标：保持 "预期 DOWN" 的监控存在，但不因为 CF 边缘问题产生噪音。

推荐方案：删除当前 503 test，新增 `https://httpstat.us/503?sleep=100`（添加 query param 绕过 CF 缓存）。

### 步骤 4：部署验证

`wrangler deploy` → 确认 cron 运行后只检查"该检查的" monitor。

## 基于间隔的新检查计划

| Monitor | 当前间隔 | 新间隔 | 理由 |
|---------|---------|--------|------|
| GitHub (github.com) | 60s | **120s** | 稳定，低频即可 |
| PyPI | 60s | **120s** | 稳定公共 CDN |
| Hacker News | 60s | **120s** | 稳定，低频即可 |
| npm Registry | 60s | **120s** | 稳定 CDN |
| Docker Hub | 60s | **120s** | 缓解 429 |
| Cloudflare API | 60s | **60s** | 基础设施核心 |
| HTTP 503 Test | 60s | **120s** | (将被替换为新端点) |
| Reddit | 60s | **120s** | 稳定公共站点 |
| GitLab API | 60s | **60s** | 开发者关键 API |
| GitHub API | 60s | **60s** | 开发者关键 API |
| Cloudflare DNS | 60s | **60s** | 基础设施核心 |
| Node.js | 60s | **120s** | 稳定 CDN |

合计：平均每分钟检查 ~7 个（而不是 12 个），Docker Hub 的 429 压力减半，核心服务的 60s 响应时间不变。

## 为什么不改更多

收敛规则 4（纯讨论禁止）和 7（一 Cycle 只做一件事）：本次只做间隔过滤 + Docker Hub + 503 test 修复。其他优化（uptime 阈值、告警策略、新端点）留到 Step 7。
