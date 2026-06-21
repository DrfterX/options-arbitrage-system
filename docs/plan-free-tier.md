# Plan: A.5 免费层限制接入 — 15 分钟数据延迟

| 作者 | CTO (Werner Vogels) + Team Lead |
|------|------|
| 日期 | 2026-06-18 |
| 状态 | 已审定，待实现 |
| 影响范围 | `web/app.py`, `web/templates/*.html` |

---

## 目标

为未注册/未登录用户实施 15 分钟数据延迟，以促使注册转化。已注册登录用户返回实时数据，Premium 用户不受影响。

## 用户身份层级

```
Anonymous（未登录）  → 15 分钟延迟数据
Registered（已登录） → 实时数据（session token 识别）
Premium（付费订阅）  → 实时数据 + Premium 专属数据（premium token 识别）
```

## 拆解步骤（每个步骤 ≤ 20 分钟）

| # | 子任务 | 预期耗时 | 产出物 | 依赖 |
|---|--------|---------|--------|------|
| A.5.1 | **后端基础设施：登录 API + Session 表** | 15 min | `app.py` 新增代码 | 无 |
| A.5.2 | **鉴权中间件 + 数据端点延迟注入** | 15 min | `app.py` 修改 | A.5.1 |
| A.5.3 | **前端提示条 + 登录弹窗** | 15 min | HTML 模板修改 | A.5.1 |
| A.5.4 | **端到端验证** | 10 min | curl + 浏览器测试 | A.5.2 + A.5.3 |

## 步骤详情

### A.5.1 — 后端基础设施：Session 表 + 登录 API

**文件**: `web/app.py`

1. 添加 `_ensure_session_table()` 函数创建 `user_sessions` 表

```sql
CREATE TABLE IF NOT EXISTS user_sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    token      TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
    expires_at TEXT NOT NULL,
    is_active  INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES user_registrations(id)
);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(token);
```

2. 添加 `_generate_session_token()` → `secrets.token_urlsafe(48)`

3. 添加 `POST /api/auth/login` 端点
   - 验证 email + bcrypt password
   - 生成 session token（30 天有效期）
   - 清理该用户过期 session
   - 返回 `{ok, token, email, expires_at}`

4. 添加 `_is_registered_user()` 辅助函数
   - 检查 `Authorization: Bearer <token>` → 查 `user_sessions` 表
   - 检查 `token` query param → 同上
   - 返回 True/False

### A.5.2 — 数据端点延迟注入

**文件**: `web/app.py`

对以下端点添加延迟条件，在数据查询 WHERE 子句中追加 `AND created_at <= datetime('now', '-15 minutes')`（TEXT 字段）或 `AND timestamp <= strftime('%s', 'now') - 900`（INTEGER 字段）：

| 端点 | 数据表 | 时间戳字段 | 类型 |
|------|--------|-----------|------|
| `/` (index) | futures_signals | created_at | TEXT |
| `/api/matrix` | futures_signals | created_at | TEXT |
| `/api/n-structures` | futures_n_structures | updated_at | TEXT |
| `/api/klines` | futures_klines | timestamp | INTEGER |
| `/api/stats` | futures_signals | created_at | TEXT |
| `/api/signals/futures` | futures_signals | created_at | TEXT |
| `/api/signals/options` | options_signals | created_at | TEXT |
| `/api/summary` | 多种 | 混合 | 混合 |
| `/api/filter-stats` | filter_decision_log | created_at | TEXT |
| `/api/filter-log` | filter_decision_log | created_at | TEXT |

**不延迟的端点**: `/api/health`, `/api/auth/*`, `/api/premium/*`, `/api/public/*`, `/admin`, `/api/admin/*`, Stripe 端点, Paper Trading POST 端点, robots.txt, sitemap.xml

**实现方式**:
```python
# 在每个端点入口处
is_delayed = not _is_registered_user()

# 在 SQL 查询中
if is_delayed:
    delay_sql = "AND created_at <= datetime('now', '-15 minutes')"
else:
    delay_sql = ""

rows = conn.execute(f'''
    SELECT ...
    FROM futures_signals
    WHERE 1=1 {delay_sql}
    ORDER BY ...
''').fetchall()
```

### A.5.3 — 前端提示条 + 登录弹窗

**文件**: `web/templates/futures_dashboard.html`, `web/templates/options_dashboard.html`, `web/templates/dashboard.html`, `web/templates/portal.html`

1. 在模板中接收 `is_delayed` 变量
2. 添加免费层提示条（仅在 `is_delayed = True` 时显示）：
   - 位置：页面顶部，topbar 下方
   - 文案：`⏱️ 免费用户数据延迟约 15 分钟 · 注册/登录 查看实时数据`
   - 样式：琥珀色警告条，与 terminal-luxe 风格一致
3. 登录弹窗（portal.html 已有注册弹窗，添加登录弹窗）
   - 邮箱 + 密码输入
   - 登录成功后存储 token 到 `localStorage['session_token']`
   - 自动刷新数据

### A.5.4 — 端到端验证

1. curl 测试登录流程
2. curl 验证未登录返回延迟数据
3. curl 验证登录后返回实时数据
4. 浏览器验证前端提示条正常显示

## 回滚方案

如果延迟导致生产问题：
1. 在 `_is_registered_user()` 中直接 `return True`（所有用户被视为"已注册"→无延迟）
2. PM2 重启：`pm2 restart options-trading`
3. 恢复时间 < 30 秒

## 注意事项

- session token 与 premium token 是互相独立的鉴权机制
- 前端需要在 `localStorage` 存储 session token（与 premium token 分开存储）
- 延迟只影响查询结果，不影响数据写入（数据采集 pipeline 不受影响）
- 延迟时间以数据库服务器时间为准（UTC+8 北京时间）