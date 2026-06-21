# 生产部署配置清单

> **产出时间**: 2026-06-18 Cycle #48 | **Step 1.1** — 检查生产部署所需配置

## 项目概要

- **应用**: StatusHub — 期货期权统一信号仪表盘
- **代码路径**: `projects/options_arbitrage_system/`
- **当前运行**: Flask dev server @ `0.0.0.0:5100`
- **数据库**: SQLite (`trading_system.db`)
- **依赖**: Python 3.10+ / Flask / NumPy / Pandas / SciPy / AKShare / Stripe

---

## 一、✅ 已有配置

| 项目 | 文件 | 状态 | 备注 |
|------|------|------|------|
| Procfile | `Procfile` | ✅ 存在 | `web: python web/app.py` — Heroku/PaaS 兼容 |
| 依赖清单 | `requirements.txt` | ✅ 存在 | 含 Flask/akshare/numpy/scipy/pandas/stripe |
| 包配置 | `pyproject.toml` | ✅ 存在 | setuptools 打包配置，含包搜索路径 |
| 环境变量模板 | `.env.template` | ✅ 存在 | Telegram/Stripe 配置说明 |
| 环境变量文件 | `.env` | ✅ 存在 | 当前运行配置（含默认值） |
| PM2 进程管理 | `ecosystem.config.cjs` | ✅ 存在 | 仅本地开发，含硬编码路径 |
| .gitignore | `.gitignore` | ✅ 存在 | 忽略 db/logs/venv/pycache |
| PORT 环境变量 | `web/app.py:1428` | ✅ 支持 | `os.environ.get("PORT", 5100)` |

---

## 二、❌ 缺失 / 需要新增

### 2.1 Docker 容器化

| 需求 | 文件 | 优先级 | 原因 |
|------|------|--------|------|
| Dockerfile | `Dockerfile` | **高** | 标准容器化部署所需 |
| .dockerignore | `.dockerignore` | 中 | 减少构建上下文大小 |
| Docker Compose | `docker-compose.yml` | 中 | 如需数据库/缓存多服务编排 |

### 2.2 生产级 Web 服务器

| 需求 | 现状 | 优先级 | 替代方案 |
|------|------|--------|---------|
| WSGI 服务器 | Flask dev server (`app.run()`) | **高** | 改用 `gunicorn` 或 `waitress` |
| 多 worker | 单进程单线程 | **高** | gunicorn `--workers=4` |

**当前问题**: `web/app.py` 用 `app.run()` 启动，这是 Flask 内置的开发服务器，**不适用于生产环境**：
- 单线程，无法处理并发请求
- 无自动 worker 重启
- 无请求超时控制
- 性能低下

### 2.3 健康检查端点

| 需求 | 现状 | 优先级 | 建议 |
|------|------|--------|------|
| `/health` 端点 | ❌ 不存在 | **高** | 简单返回 `{"status": "ok"}`，可以被负载均衡器/容器编排定期轮询 |
| 数据库连通性检查 | ❌ 不存在 | 中 | `/health` 应同时验证 DB 可连接 |

### 2.4 平台部署配置

| 平台 | 配置需求 | 优先级 | 备注 |
|------|---------|--------|------|
| **Heroku** | Procfile ✅ + runtime.txt | 低 | 不再免费，不推荐 |
| **Railway** | 无特殊配置文件 | **高** | 支持 Procfile 直接部署，免费额度够用 |
| **Fly.io** | `fly.toml` + Dockerfile | 中 | 需信用卡注册 |
| **Cloudflare Workers** | ❌ 不适用 | — | 产品是 Python Flask，非 Workers 兼容语言 |
| **VPS (自管)** | Dockerfile + Nginx 反代配置 | 中 | 需手动管理，但控制度高 |

### 2.5 数据库策略

| 需求 | 现状 | 优先级 | 建议 |
|------|------|--------|------|
| SQLite 生产可用性 | 正在使用 | **⚠️ 风险** | SQLite 不适合生产并发写入。选项：(A) 保持 SQLite + 定时备份 (B) 迁移到 PostgreSQL |
| 数据库备份方案 | ❌ 不存在 | **高** | 无论用 SQLite 还是 PG，都需要自动备份 |
| 初始化迁移脚本 | `scripts/init_db.py` ✅ | 已存在 | 首次部署时需运行 |

---

## 三、环境变量清单

| 变量名 | 必须 | 默认值 | 说明 |
|--------|------|--------|------|
| `PORT` | 否 | `5100` | 应用监听端口 |
| `ADMIN_PASSWORD` | 推荐 | `autocompany2024` | 管理面板密码（部署时建议修改） |
| `TELEGRAM_BOT_TOKEN` | 否 | — | Telegram Bot Token（可选推送） |
| `TELEGRAM_CHAT_ID` | 否 | — | Telegram Chat ID（可选推送） |
| `STRIPE_SECRET_KEY` | 否 | — | Stripe API Secret Key（付费订阅） |
| `STRIPE_WEBHOOK_SECRET` | 否 | — | Stripe Webhook Secret |
| `PREMIUM_PRICE_ID` | 否 | — | Stripe Price ID |
| `SIGNALS_BASE_URL` | 否 | `http://localhost:5100` | 支付回调 Base URL |

---

## 四、部署模式推荐

### 方案 A（推荐 🥇）：Railway（最快上线）

**理由**:
- Procfile 已有 → 零适配
- Flask 改 gunicorn → 一行命令
- SQLite 可以先用，后续迁移 PG
- Railway 免费额度足够跑这个应用
- 自带域名 + HTTPS

**所需操作**:
1. 添加 `gunicorn` 到依赖
2. 创建 `runtime.txt`（Python 版本声明）
3. Procfile 改为 `web: gunicorn web.app:app -w 4 -b 0.0.0.0:$PORT`
4. GitHub 连接 → Railway 自动部署

### 方案 B（自控 🥈）：VPS + Docker

**理由**:
- 完全控制，适合金融数据产品
- 可跑定时任务（数据采集）
- 成本：最低 $5/月 VPS（如 Hetzner）

**所需操作**:
1. 创建 Dockerfile
2. 配置 Nginx 反代 + HTTPS (Let's Encrypt)
3. 配置 systemd 或 PM2 自启动
4. 设置数据库定时备份

---

## 五、下一步决策点

Step 1.2 需要选择部署目标，以下是需回答的问题：

1. **数据库**：保持 SQLite + 自动备份？还是部署前迁移 PostgreSQL？
2. **Web 服务器**：直接上 gunicorn？还是用 Docker 打包后 gunicorn？
3. **平台**：选 Railway（最快上线）还是 VPS（完全控制）？
4. **上线范围**：先开放给限量试用用户，还是全面公开？

> **建议**：先用 Railway 上线（'Ship > Plan'），后续看流量决定是否迁移到自管 VPS。