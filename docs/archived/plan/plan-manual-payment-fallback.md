# 手动支付回退方案 — 管理员解锁 + Premium Gating

## 目标
在不依赖 Stripe Keys 的情况下启动收入验证：人类通过管理员面板手动生成 Pro Token，实现付费墙。

## 背景
- Stripe 后端代码完整但阻塞于人类填入 Keys（连续 3+ cycles）
- 三个 Premium API endpoints 实际未经保护（无 `@require_premium` 装饰器）
- 收敛规则 #5 要求换方向

## 架构

```
浏览器 ←→ signals.drifter.indevs.in
                    │
                    ├── / → portal.html (含支付指引区)
                    ├── /admin → admin_panel.html (密码保护，手动生成 Pro Token)
                    ├── /api/admin/generate-token (POST, 需 admin 密码)
                    ├── /api/admin/verify-password (POST, 前端鉴权)
                    ├── /api/premium/recommendations → +@require_premium
                    ├── /api/premium/breakout-alerts → +@require_premium
                    └── /api/premium/top-options → +@require_premium
```

## 拆解步骤

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 1.1 | 添加管理员密码配置 + admin 路由骨架 | 15min | app.py 新增路由 |
| 1.2 | 创建 admin_panel.html 模板（密码登录 + token 生成表单 + 订阅列表） | 20min | HTML 模板 |
| 1.3 | 实现 `/api/admin/generate-token` + `/api/admin/verify-password` | 15min | API 端点 |
| 1.4 | 为 3 个 Premium endpoints 添加 `@require_premium` | 10min | 代码修改 |
| 1.5 | portal.html 添加支付信息区 + 更新 consensus | 15min | 前端修改 |
| **1.6** | **QA Bach 安全审查** | **15min** | 审查报告 |

**当前：Cycle #7 — Step 1.1 管理员面板骨架**