# 手动支付回退方案 — 实现记录

## 背景
Stripe 集成因缺少 API Keys 阻塞 3+ cycles。根据收敛规则 #5，实现手动支付替代方案。

## 实现内容

### 1. 管理员面板 `/admin`
- **路由**: `GET /admin` → `admin_panel.html`
- **鉴权**: 管理员密码（环境变量 `ADMIN_PASSWORD`，默认 `autocompany2024`）
- **功能**: 
  - 输入用户邮箱 → 生成 Pro Token
  - Token 自动复制到剪贴板
  - 订阅记录列表（ID、Email、状态、时间）

### 2. Admin API 端点
| 端点 | 方法 | 功能 | 鉴权 |
|------|------|------|------|
| `/api/admin/verify-password` | POST | 验证管理员密码 | - |
| `/api/admin/generate-token` | POST | 生成 Pro Token 写入数据库 | 密码 |
| `/api/admin/list-subscriptions` | GET | 列出所有订阅 | 密码 query param |

### 3. Premium Gating
三个 Premium API endpoints 加上 `@require_premium` 装饰器：
- `/api/premium/recommendations`
- `/api/premium/breakout-alerts`
- `/api/premium/top-options`

Token 传递方式（按优先级）：
1. `Authorization: Bearer <token>` 请求头
2. `?token=<token>` URL query parameter

### 4. Portal 支付区
portal.html 新增：
- Token 输入框 + 验证按钮（`#tokenInput` + `#verifyTokenBtn`）
- `verifyManualToken()`: 调用 `/api/premium/verify-token` 验证并解锁 Premium
- 页面加载时自动检查 `localStorage` 中的 `premium_token`
- Premium 内容加载函数增加 `?token=` query param

### 5. 支付流程
```
用户联系管理员 → 转账 $19 (微信/支付宝)
         ↓
管理员登录 /admin → 输入用户邮箱 → 生成 Token
         ↓
管理员将 Token 发送给用户
         ↓
用户在 signals.drifter.indevs.in 门户页输入 Token
         ↓
Token 验证通过 → Premium 内容解锁
```

## 文件变更
| 文件 | 变更说明 |
|------|---------|
| `web/app.py` | 新增 90 行：ADMIN_PASSWORD 配置、3 个 admin 路由、`@require_premium` ×3 |
| `web/templates/admin_panel.html` | **新建**：管理员面板模板（密码登录 + Token 生成 + 订阅列表）|
| `web/templates/portal.html` | 新增 Token 输入区 + verifyManualToken() + Premium 加载函数 Token 传参 |
| `web/templates/dashboard.html` | K线浮窗 A/B/C 标注：data-at/bt/ct 属性支持 |
| `web/templates/options_dashboard.html` | IV 区域布局优化 |

## 验证结果
- ✅ 管理员密码验证 → `{"ok": true/false}`
- ✅ Token 生成 → 返回 `secrets.token_urlsafe(32)` 级别密码
- ✅ Premium 无 Token → HTTP 401
- ✅ Premium + Bearer Token → HTTP 200
- ✅ Premium + query param Token → HTTP 200
- ✅ Token 验证 → `{"valid": true, "premium": true}`
- ✅ 订阅列表 → 所有记录正确返回