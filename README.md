# StatusHub — Unified Futures & Options Signal Dashboard

**期货期权统一信号仪表盘** — A real-time signal monitoring platform combining futures N-structure pattern analysis with commodity options arbitrage signals.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-lightgrey)

---

## Live Demo

| Service | URL | Description |
|---------|-----|-------------|
| 📊 **Main Dashboard** | [signals.drifter.indevs.in](https://signals.drifter.indevs.in/) | Multi-cycle signal matrix, resonance detection |
| 📈 **Futures Dashboard** | [futures.drifter.indevs.in](https://futures.drifter.indevs.in/) | K-line charts, N-structure pattern annotations |
| 📉 **Options Dashboard** | [options.drifter.indevs.in](https://options.drifter.indevs.in/) | IV percentile histogram, strategy scoring |

---

## Features

### 🎯 Multi-Cycle Signal Matrix
- Cycle coverage: 15min / 30min / 60min / 2h / 4h / 1d / 1w
- Bullish / bearish / neutral signal classification with color coding
- Cross-cycle resonance detection (multiple cycles aligning in same direction)
- Real-time signal updates from Chinese commodity futures data

### 🔍 N-Structure Pattern Analysis
- Automatic detection of N-type price structures (ABC pattern)
- Rising N-structure: bullish breakout tracking
- Falling N-structure: bearish breakdown tracking
- Visual annotations on K-line charts with price labels

### 📊 IV & Options Analytics
- Implied Volatility (IV) percentile histogram across contract months
- Options strategy scoring: 7-dimension evaluation (Θ, Vega, Win Rate, Range, Efficiency, Δ, IV)
- Multi-leg strategy analysis (vertical spreads, straddles, butterflies)
- Unified scoring with transparent breakdown

### 📈 Premium Tiers
- **Free Tier**: Core signal matrix + basic K-line views
- **Premium Tier**: Full options analytics, strategy details, real-time alerts (via Stripe)

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | Python 3.10+, Flask 3.0 |
| **Data Source** | AKShare (Sina Finance real-time API) |
| **Computation** | NumPy, SciPy, Pandas |
| **Database** | SQLite |
| **Frontend** | Server-side rendered HTML + vanilla JS + Chart.js |
| **Production Server** | Gunicorn |
| **Infrastructure** | Cloudflare Tunnel (hermes-web-chat) |
| **Payments** | Stripe |

---

## Architecture

```
                        ┌──────────────┐
                        │  AKShare API  │
                        │ (Sina/Futures)│
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │  Data Layer  │
                        │  (core/)     │
                        └──────┬───────┘
                               │
                   ┌───────────┼───────────┐
                   ▼           ▼           ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │ Futures  │ │ Options  │ │ Signals  │
            │ Pipeline │ │ Pipeline │ │ Pipeline │
            └────┬─────┘ └────┬─────┘ └────┬─────┘
                 │            │            │
                 ▼            ▼            ▼
            ┌─────────────────────────────────┐
            │         SQLite Database          │
            └──────────────┬──────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Flask Web  │
                    │  (web/app)  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Cloudflare │
                    │   Tunnel    │
                    └─────────────┘
```

---

## Screenshots

<!-- Screenshots to be added -->
| Dashboard | Preview |
|-----------|---------|
| **Signal Matrix** | *🖼️ Screenshot coming soon* |
| **Futures K-line** | *🖼️ Screenshot coming soon* |
| **Options Dashboard** | *🖼️ Screenshot coming soon* |

---

## Self-Deployment

### Prerequisites
- Python 3.10+
- Git
- (Optional) Cloudflare Tunnel for public access

### Quick Start

```bash
# Clone the repository
git clone https://github.com/DrfterX/options-arbitrage-system.git
cd options-arbitrage-system

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run data pipeline (download futures & options data)
python -m pipeline.run_all

# Start the web server
python web/app.py 0.0.0.0 5100

# Visit http://localhost:5100
```

### Production Deployment

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5100 web.app:app

# With Cloudflare Tunnel
cloudflared tunnel run
```

---

## Project Structure

```
├── web/                   # Flask web application
│   ├── app.py             # Main application & routes
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── dashboard.html         # Signal matrix view
│   │   ├── futures_dashboard.html # Futures K-line view
│   │   ├── options_dashboard.html # Options analytics view
│   │   ├── portal.html            # Landing page
│   │   └── admin_panel.html       # Admin panel
│   └── static/            # Static assets (CSS, JS)
├── core/                  # Core data models & database
├── futures/               # Futures N-structure analysis
├── options/               # Options analytics & pricing
├── signals/               # Signal generation & scoring
├── data/                  # Data fetching (AKShare)
├── config/                # App configuration & settings
├── pipeline/              # ETL pipeline orchestration
├── pyproject.toml         # Project metadata & dependencies
└── requirements.txt       # Python dependencies
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main dashboard (portal) |
| `GET /api/matrix` | Multi-cycle signal matrix JSON |
| `GET /api/klines` | K-line data for candlestick charts |
| `GET /api/stats` | Sector statistics & summary |
| `GET /api/signals/futures` | Latest futures signals |
| `GET /api/signals/options` | Latest options signals |
| `GET /api/iv/status` | IV status for all instruments |
| `GET /api/summary` | General overview summary |
| `GET /api/backtest` | Full backtest results |
| `GET /robots.txt` | Robots exclusion rules |
| `GET /sitemap.xml` | XML sitemap |

---

## License

[MIT](LICENSE) © Auto Company

---

# StatusHub — 期货期权统一信号仪表盘

## 📋 项目简介

StatusHub 是一个专为中国期货市场设计的统一信号监控平台，结合了期货 N 型结构模式分析与商品期权套利信号，帮助交易者快速把握多周期共振机会。

## 🔥 核心功能

### 🎯 多周期信号矩阵
- 覆盖 7 个周期：15分钟 / 30分钟 / 60分钟 / 2小时 / 4小时 / 日线 / 周线
- 红绿灰三色信号分类（看多/看空/中性）
- 跨周期共振检测：多个周期同向时触发共振提示
- 实时数据驱动，盘中持续更新

### 🔍 N 型结构分析
- 自动识别期货 K 线的 N 型价格结构（A→B→C 三段）
- 上升 N 型：价格整体向上，C 不破 A 的低点
- 下降 N 型：价格整体向下，C 不破 A 的高点
- K 线浮窗标注 A/B/C 三点的价格与位置

### 📊 IV 与期权分析
- 隐含波动率（IV）百分位柱状图：展示各合约月份的 IV 排序
- 期权策略评分系统：7 维度综合评估（Θ、Vega、胜率、盈亏区间、效率、Δ、IV）
- 多腿策略分析：垂直价差、跨式、蝶式等
- 评分透明可追溯，点击查看分解明细

### 💎 付费订阅
- **免费版**：核心信号矩阵 + 基础 K 线视图
- **高级版**：完整期权分析、策略详情、实时提醒（通过 Stripe 支付）

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python 3.10+, Flask 3.0 |
| 数据源 | AKShare（新浪财经实时 API） |
| 计算引擎 | NumPy, SciPy, Pandas |
| 数据库 | SQLite |
| 前端 | 服务端渲染 HTML + 原生 JS + Chart.js |
| 生产服务器 | Gunicorn |
| 基础设施 | Cloudflare Tunnel |
| 支付 | Stripe |

## 🚀 快速部署

```bash
# 克隆仓库
git clone https://github.com/DrfterX/options-arbitrage-system.git
cd options-arbitrage-system

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行数据管线
python -m pipeline.run_all

# 启动 Web 服务
python web/app.py 0.0.0.0 5100

# 访问 http://localhost:5100
```

## 🔗 产品链接

| 服务 | 地址 |
|------|------|
| 📊 **主看板** | [signals.drifter.indevs.in](https://signals.drifter.indevs.in/) |
| 📈 **期货看板** | [futures.drifter.indevs.in](https://futures.drifter.indevs.in/) |
| 📉 **期权看板** | [options.drifter.indevs.in](https://options.drifter.indevs.in/) |

## 📄 许可证

[MIT](LICENSE) © Auto Company
