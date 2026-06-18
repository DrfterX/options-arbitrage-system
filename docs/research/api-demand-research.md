# StatusHub 公开数据 API — 需求调研报告

> **分析师**: research-thompson (Ben Thompson 思维模型)  
> **日期**: 2026-06-18  
> **周期**: Phase 2 — 公开 API 渠道  
> **前置**: SEO ✅ GitHub ✅ → **Public API ◀** → TradingView

---

## 执行摘要

本报告调研了 StatusHub 代码库现有 API 结构、竞品定价模型，并提出了 3 个面向开发者的公开 API 端点。这些端点均可基于现有数据在 1-2 小时内完成实现，零额外数据源依赖。

| 端点 | 数据价值 | 速率限制(Free/Pro) | 实现难度 |
|------|---------|-------------------|---------|
| `GET /api/v1/market/heatmap` | ⭐⭐⭐ 多周期信号矩阵(核心差异化) | 10 / 60 req/min | 🔧 低 |
| `GET /api/v1/signals/top` | ⭐⭐ 高评分信号(可直接交易参考) | 30 / 300 req/min | 🔧 很低 |
| `GET /api/v1/options/iv-summary` | ⭐⭐ IV 百分位(期权策略入场判断) | 30 / 300 req/min | 🔧 很低 |

---

## 1. 代码库现状分析

### 1.1 当前技术栈

| 组件 | 实现 |
|------|------|
| 框架 | Flask + Jinja2 + ECharts |
| 数据库 | SQLite (14 表, `trading_system.db`) |
| 数据量 | 62 万+ K 线、212 期货信号、2357 N 型结构、2310 期权信号 |
| 部署 | Cloudflare Workers/Pages (via `futures.drifter.indevs.in`) |

### 1.2 已有内部 API 端点

所有端点均在 `web/app.py` 中定义为 Flask route，当前供前端 ECharts 使用：

| 端点 | 用途 | 鉴权 |
|------|------|------|
| `GET /api/matrix` | 多周期信号矩阵 (65 品种 × 4 周期) | 无 |
| `GET /api/n-structures` | N 型结构展开列表 | 无 |
| `GET /api/klines?symbol=X&timeframe=Y` | K 线数据 | 无 |
| `GET /api/stats` | 板块统计 | 无 |
| `GET /api/signals/futures` | 期货信号列表 | 无 |
| `GET /api/signals/options` | 期权信号列表 | 无 |
| `GET /api/iv/status` | IV 状态 | 无 |
| `GET /api/summary` | 汇总概览 | 无 |
| `GET /api/health` | 健康检查 | 无 |
| `GET /api/filter-stats` | SmartFilter 统计 | 无 |
| `GET /api/positions*` | Paper Trading 持仓 (6 个子端点) | 无 |
| `GET /api/backtest` | 全量回测结果 | 无 |
| `GET /api/iron-ore/*` | 铁矿石专属 API (5 个子端点) | 无 |
| `GET /api/premium/*` | Premium 付费内容 (3 个子端点) | Bearer Token |
| `POST /api/create-checkout-session` | Stripe 支付 | 无 |

### 1.3 现有 API 的问题

1. **命名不一致**: 混合 snake_case 和简短名 (`/api/iv/status`, `/api/n-structures`)
2. **无版本前缀**: 所有端点裸 `/api/`，无法向后兼容
3. **无速率限制**: 当前无任何限流，数据采集者可随意抓取
4. **无文档**: 没有任何 OpenAPI/Swagger 或 Markdown 文档
5. **内部耦合**: 响应格式为前端定制，包含前端渲染字段(如中文名)，不适合程序化调用
6. **无 CORS 策略**: 未显式设置，开发者无法从浏览器直接调用

### 1.4 可用于公开 API 的数据资产

| 数据 | 表 | 行数 | 更新频率 | 差异化价值 |
|------|-----|------|---------|-----------|
| N 型结构状态 | `futures_n_structures` | 2,357 | 实时重算 | ⭐⭐⭐ **核心 IP** |
| 期货信号(含评分) | `futures_signals` | 212 | 每管线运行 | ⭐⭐⭐ 交易参考 |
| K 线(6 周期) | `futures_klines` | 621,450 | 实时 | ⭐⭐ 基础数据 |
| 期权策略信号 | `options_signals` | 2,310 | 日频 | ⭐⭐ 独有 |
| IV 历史 | `iv_history` | 4,503 | 日频 | ⭐⭐ 独有 |
| 波峰/波谷 | `futures_swing_points` | — | 实时 | ⭐ 技术分析 |

---

## 2. 竞品 API 定价分析

### 2.1 定价模式全景

| 平台 | Free Tier | 价格 | 核心限制 | 数据覆盖 |
|------|----------|------|---------|---------|
| **CoinGecko** | ✅ 无需 API 可读 | $0 (Demo) | 10K calls/月, 100/min | Crypto 现货+衍生品 |
| **Alpha Vantage** | ✅ 注册即可用 | $0 | 5 calls/min, 500/day | 股票/外汇/加密货币 |
| **Twelvedata** | ✅ 注册即可用 | $0 | 800 calls/day | 股票/期货/外汇 |
| **Polygon.io** | ❌ 已关闭免费 | $29+/月起步 | 无免费 | 股票/期权/期货 |
| **CoinMarketCap** | ✅ 注册即可用 | $0 | 333 calls/day | Crypto 全数据 |
| **IEX Cloud** | ✅ 注册即可用 | $0 | 50K calls/月 | 美股 |
| **Finnhub** | ✅ 注册即可用 | $0 | 60 calls/min | 全球股票/期货 |
| **Yahoo Finance (非官方)** | ✅ 无需注册 | $0 | 无官方限制 | 全球市场(不稳定) |

### 2.2 关键发现

**发现 1: "免费但限速" 是标准模式**
所有成功的公开 API 都采用 Free tier → Paid tier 的漏斗模型。免费层的价值不在于收入，而在于：
- **养成开发者习惯**（开发者用你的数据构建项目后很难迁移）
- **病毒传播**（每个使用 API 的应用都是你的推广渠道）
- **GitHub 生态**（API 驱动的开源项目天然带有 StatusHub 的引用）

**发现 2: 中国期货数据存在巨大空白**
上述所有竞品都**不覆盖中国商品期货市场**。Alpha Vantage 和 Twelvedata 虽号称支持期货，但品种以欧美为主。StatusHub 覆盖的 65 个中国期货品种 + 期权是**独一无二的差异化**。

**发现 3: 结构化信号比原始行情更有价值**
CoinGecko/CryptoCompare 等提供原始行情数据的 API 已经饱和。但**将原始数据加工为"信号"的 API 极少**——这正是 StatusHub 的 N 型结构分析、期权策略评分的竞争壁垒。

### 2.3 推荐定价策略

```
┌─────────────────────────────────────────────────────┐
│                   StatusHub API                      │
├──────────────┬──────────────────┬───────────────────┤
│    Free       │     Pro ($9/mo)  │   Enterprise      │
│               │                  │                   │
│  10 req/min   │  100 req/min     │   Custom SLA      │
│  Historical   │  Real-time push  │   Dedicated infra │
│  1d latency   │  WebSocket       │   White-label     │
│               │  Historical CSV  │   On-prem         │
└──────────────┴──────────────────┴───────────────────┘
```

**关键原则**:
- Free tier **不需要 API key** — 降低使用摩擦
- Free tier 返回延迟 1-5 分钟的缓存数据（不影响开发体验）
- Pro tier 通过现有 Stripe 支付通道处理

---

## 3. 推荐端点: 详细设计

### 端点 1: 市场信号热力图 `GET /api/v1/market/heatmap`

**描述**: 65+ 品种的多周期 N 型结构方向矩阵 + 共振分数。这是 StatusHub 最核心的差异化数据——开发者调用一次即可了解全市场多空格局。

**为什么是 #1**: 无竞品提供此数据。CoinGecko 有 "trending" 但基于社交热度，我们基于真实的结构化价格分析。这是开发者 5 分钟就能理解的杀手级 API。

**请求**:

```
GET /api/v1/market/heatmap
  ?sector=贵金属           # 可选: 按板块过滤
  &min_resonance=2         # 可选: 最小共振数
  &timeframes=15m,1h,1d   # 可选: 指定周期
```

**响应 (示例)**:

```json
{
  "generated_at": "2026-06-18T10:30:00+08:00",
  "data_freshness": "live",
  "total_symbols": 65,
  "total_active_structures": 47,
  "sectors": [
    {
      "name": "贵金属",
      "bias": "多",
      "active_count": 2,
      "symbols": [
        {
          "symbol": "AU",
          "name": "黄金",
          "contract": "ag2607",
          "overall_score": 0.95,
          "direction": "LONG",
          "resonance": 3,
          "timeframes": {
            "15m": { "direction": "LONG", "state": "LEG3", "a": 885.0, "b": 892.0, "c": 887.52 },
            "1h":  { "direction": "LONG", "state": "LEG2", "a": 880.0, "b": 890.0, "c": null },
            "1d":  { "direction": "SHORT", "state": "LEG1", "a": null, "b": null, "c": null },
            "1w":  { "direction": null, "state": "IDLE" }
          }
        }
      ]
    }
  ]
}
```

**速率限制**: Free 10 req/min | Pro 60 req/min  
**缓存**: 30 秒 (实时数据, 但不需要毫秒级精度)  
**实现**: 约 60 行 Python — 复用 `web/app.py` 中 `api_matrix()` 的查询逻辑，增加格式转换和过滤参数

**开发者 5 分钟上手**:

```bash
# 只需 curl，无需注册，无需 API key
curl https://futures.drifter.indevs.in/api/v1/market/heatmap?sector=贵金属

# 输出一目了然: 黄金 3 周期共振看多 → 买入信号
```

---

### 端点 2: 高评分信号 TOP N `GET /api/v1/signals/top`

**描述**: 按评分降序返回当前最值得关注的期货信号，含方向、入场价、止损止盈参考。开发者可直接开发自动化策略。

**请求**:

```
GET /api/v1/signals/top
  ?limit=10                # 可选: 返回数量 (默认 10, 最大 50)
  &min_score=0.5           # 可选: 最小评分筛选
  &direction=LONG          # 可选: 按方向过滤
```

**响应 (示例)**:

```json
{
  "generated_at": "2026-06-18T10:30:00+08:00",
  "total_active": 42,
  "returned": 10,
  "signals": [
    {
      "symbol": "AU",
      "name": "黄金",
      "contract": "ag2607",
      "direction": "SHORT",
      "signal_type": "ENTRY",
      "score": 1.0,
      "entry_price": 887.52,
      "stop_loss": 901.68,
      "take_profit": 859.20,
      "levels_passed": { "L1": true, "L2": true, "L3": true },
      "generated_at": "2026-06-18T09:15:00+08:00"
    }
  ]
}
```

**速率限制**: Free 30 req/min | Pro 300 req/min  
**缓存**: 60 秒  
**实现**: 约 30 行 Python — 已有 `/api/signals/futures` 和 `hub.get_recent_futures()`，仅需增加过滤参数和响应格式精简

**开发者 5 分钟上手**:

```bash
# 获取目前评分最高的 5 个做多信号
curl "https://futures.drifter.indevs.in/api/v1/signals/top?limit=5&direction=LONG"

# 结果可直接用于自动跟单系统
```

---

### 端点 3: 期权 IV 快照 `GET /api/v1/options/iv-summary`

**描述**: 所有期权品种的隐含波动率(IV)百分位和等级。买方寻找低 IV 入场(IV 百分位 < 20%)，卖方在高 IV (百分位 > 80%) 时更有优势。

**请求**:

```
GET /api/v1/options/iv-summary
  ?min_iv_pct=80           # 可选: 筛选 IV 百分位 ≥ 80 的品种
  &max_iv_pct=20           # 可选: 筛选 IV 百分位 ≤ 20 的品种
  &sort_by=iv_percentile   # 可选: 排序字段
```

**响应 (示例)**:

```json
{
  "generated_at": "2026-06-18T10:30:00+08:00",
  "total_symbols": 22,
  "summary": {
    "high_iv_count": 3,
    "mid_iv_count": 12,
    "low_iv_count": 7
  },
  "iv_status": [
    {
      "symbol": "MA",
      "name": "甲醇",
      "contract": "MA2609",
      "iv_percentile": 85.3,
      "iv_level": "高位",
      "iv_avg": 0.32,
      "best_for": "卖方策略 (卖跨/铁鹰)"
    },
    {
      "symbol": "RB",
      "name": "螺纹钢",
      "contract": "RB2610",
      "iv_percentile": 12.7,
      "iv_level": "低位",
      "iv_avg": 0.18,
      "best_for": "买方策略 (买入跨式)"
    }
  ]
}
```

**速率限制**: Free 30 req/min | Pro 300 req/min  
**缓存**: 300 秒 (IV 变化缓慢, 无需高频刷新)  
**实现**: 约 40 行 Python — 现有 `/api/iv/status` 端点和 `iv_recorder.get_all_status()` 可直接复用

**开发者 5 分钟上手**:

```bash
# 找到 IV 低于 20% 的品种 (适合期权买方)
curl "https://futures.drifter.indevs.in/api/v1/options/iv-summary?max_iv_pct=20"

# 结果: "螺纹钢 IV 12.7% — 历史低位, 考虑买入跨式"
```

---

## 4. 实现路径

### 4.1 架构建议

```
web/
├── app.py                  # 现有 Flask app (不动现有路由)
├── iron_ore_api.py         # 现有 Blueprint (不动)
├── stripe_handler.py       # 现有 Stripe (不动)
└── public_api.py           # 新文件: 公开 API Blueprint
    └── bp = Blueprint("public_api", __name__, url_prefix="/api/v1")
        ├── GET /market/heatmap       → api_v1_heatmap()
        ├── GET /signals/top           → api_v1_signals_top()
        └── GET /options/iv-summary   → api_v1_options_iv()

web/public_api.py:
    - 新建 Blueprint, url_prefix="/api/v1"
    - 所有端点返回 JSON, 统一格式: { "generated_at", "data": ... }
    - 错误格式统一: { "error": "...", "code": 429 }
    - 速率限制中间件 (Redis 或内存滑动窗口)
    - CORS: 开放所有来源, 允许 GET
    - Cache-Control 头: s-maxage=XX
    - 可选: API key 支持 (对 free tier 可忽略)
```

### 4.2 实现步序

| 步骤 | 内容 | 预计时间 |
|------|------|---------|
| 1 | 新建 `web/public_api.py`，创建 Blueprint | 5 min |
| 2 | 实现 `api_v1_heatmap()` — 复用 `api_matrix()` 逻辑 | 20 min |
| 3 | 实现 `api_v1_signals_top()` — 包装 `hub.get_recent_futures()` | 10 min |
| 4 | 实现 `api_v1_options_iv()` — 包装 `iv_recorder.get_all_status()` | 10 min |
| 5 | 速率限制中间件 | 15 min |
| 6 | CORS + Cache-Control 头 | 5 min |
| 7 | 单元测试 | 15 min |
| 8 | 部署 | 5 min |
| **总计** | | **~85 min** |

### 4.3 速率限制设计

对 Free tier (无 API key):

```python
# 内存滑动窗口实现 (无需 Redis, 单进程足够)
RATE_LIMITS = {
    "/api/v1/market/heatmap":   (10, 60),    # 10 req / 60 sec
    "/api/v1/signals/top":      (30, 60),    # 30 req / 60 sec
    "/api/v1/options/iv-summary": (30, 60),  # 30 req / 60 sec
}

# 返回 429 Too Many Requests + Retry-After 头
```

Pro tier 通过 Bearer Token 识别，速率限制提升 10x。

### 4.4 安全性考虑

| 风险 | 缓解措施 |
|------|---------|
| 数据库压力 | 端点级缓存 + 速率限制 + 数据库查询优化 |
| 恶意抓取 | 封 IP (可通过 Cloudflare WAF 实现) |
| 数据滥用 | Terms of Service 禁止转售原始数据 |
| SQL 注入 | 已使用参数化查询 (SQLite 安全) |

---

## 5. 增长预期

### 5.1 渠道效果

```
GitHub README → 开发者发现 API → curl 测试 (5分钟)
                                     ↓
                            Fork/Star GitHub 仓库
                                     ↓
                           在个人项目中使用 API
                                     ↓
                            Twitter/Reddit 分享
                                     ↓
                           更多开发者发现 → 飞轮
```

### 5.2 关键指标

| 指标 | 目标 (上线 30 天) |
|------|------------------|
| 唯一 IP 调用数 | 500+ |
| API 调用总量 | 10,000+ |
| GitHub Star 增长 | +15-30 |
| Developer 注册 (Pro) | 3-5 个 |
| 公开 API 相关问题 (GitHub Issues) | 5+ (好信号) |

### 5.3 搜索引擎效果

每个公开 API 端点会在 Google 上被索引为独立页面。当开发者搜索 `"futures n structure api"`、`"中国期货信号 API"`、`"options IV percentile API"` 等关键词时，StatusHub 的 API 文档会出现在搜索结果中——这是**免费且永久的 SEO 流量**。

---

## 附录 A: 竞品 API 端点对比

| 功能需求 | CoinGecko | Alpha Vantage | Twelvedata | **StatusHub (本周)** |
|---------|-----------|---------------|------------|-------------------|
| 行情 K 线 | ✅ | ✅ | ✅ | ✅ 6 周期 |
| 技术指标 | ❌ | ✅ (20+) | ✅ (100+) | ✅ N 型结构(独有) |
| 期货数据 | ❌ (仅 Crypto) | ⚠️ 有限 | ⚠️ 欧美为主 | ✅ **中国全品种** |
| 期权数据 | ❌ | ❌ | ❌ | ✅ 策略+IV |
| 信号评分 | ❌ | ❌ | ❌ | ✅ **三级评分** |
| 多周期共振 | ❌ | ❌ | ❌ | ✅ **核心差异化** |
| 无需注册 | ✅ | ❌ | ❌ | ✅ **设计目标** |
| 中文支持 | ❌ | ❌ | ❌ | ✅ |

## 附录 B: 已有数据字段映射

| 公开 API 字段 | 数据库字段 | 所在表 |
|--------------|-----------|--------|
| symbol | `symbol` | `futures_n_structures` |
| direction | `direction` | `futures_n_structures` |
| state | `state` | `futures_n_structures` |
| point_a/b/c_price | `point_a/b/c_price` | `futures_n_structures` |
| score | `score` | `futures_signals` |
| entry_price | `entry_price` | `futures_signals` |
| stop_loss | `stop_loss` | `futures_signals` |
| take_profit | `take_profit` | `futures_signals` |
| iv_percentile | — (由 `_calc_percentile()` 计算) | `iv_history` (原始数据) |
| iv_level | `iv_level` | `options_signals` |

---

*下一阶段建议: 在 3 个端点验证渠道效果后，扩展到 TradingView Pine Script 适配器（Phase 3）。*