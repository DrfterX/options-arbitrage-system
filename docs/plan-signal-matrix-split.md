# Plan: 信号矩阵面板拆分为期货/期权双页面

## 目标
将 `https://signals.drifter.indevs.in/`（期货+期权合一的单一页面）拆分为两个独立域名页面：
- 期货面板 → `futures.drifter.indevs.in`
- 期权面板 → `options.drifter.indevs.in`

## 现状分析

### 代码结构
- **后端**: `projects/options_arbitrage_system/web/app.py` — 单一 Flask 应用，单路由 `/`
- **前端**: `projects/options_arbitrage_system/web/templates/dashboard.html` — 单页面，包含期货信号矩阵 + 期权策略卡片
- **样式**: `projects/options_arbitrage_system/web/static/style.css` — 统一样式
- **部署**: PM2 单实例 5100 端口（`ecosystem.config.cjs`），域名转发在基础设施层

### 页面内容分布

| 模块 | 期货 | 期权 |
|------|------|------|
| 统计栏 (stats-bar) | 品种数/多空比/最高评分 | ❌ 无期权特有统计 |
| SmartFilter 防火墙 | ✅ 期货信号过滤 | ❌ 不适用 |
| 板块统计 | 有色/贵金属/黑色/能源化工/农产品/新能源 | ❌ 不适用 |
| 多周期信号矩阵 | 期货品种×4周期(15m/1h/1d/1w)N型结构+共振 | ❌ 不适用 |
| 信号卡片 | 最新15条期货信号 | ❌ 不适用 |
| 期权策略区 | ❌ | iron_condor/short_strangle/ratio_spread |
| 期权 IV 数据 | ❌ | IV百分位+等级+Greeks |
| 持仓看板 | ✅ 期货持仓 | ❌ 不适用 |
| 健康面板 | ✅ 系统状态 | ✅ 系统状态（公用） |

### 后端数据天然分离
- `futures_*` 表：`futures_klines`, `futures_signals`, `futures_n_structures`, `futures_macd`, `futures_swing_points`
- `options_*` 表：`options_signals`, `iv_history`

### API 端点分布

| 端点 | 期货 | 期权 | 公用 |
|------|------|------|------|
| `/api/matrix` | ✅ | ❌ | ❌ |
| `/api/klines` | ✅ | ❌ | ❌ |
| `/api/stats` | ✅ | ❌ | ❌ |
| `/api/signals/futures` | ✅ | ❌ | ❌ |
| `/api/signals/options` | ❌ | ✅ | ❌ |
| `/api/iv/status` | ❌ | ✅ | ❌ |
| `/api/summary` | ✅ | ✅ | ❌ |
| `/api/filter-stats` | ✅ | ❌ | ❌ |
| `/api/filter-log` | ✅ | ❌ | ❌ |
| `/api/positions*` | ✅ | ❌ | ❌ |
| `/api/health` | ❌ | ❌ | ✅ |
| `/api/backtest` | ✅ | ❌ | ❌ |

## 设计方案

### 方案选择：同一 Flask App + 域名路由（推荐）

**理由**：保持后端单一部署，减少运维复杂度；API 层不变，只改前端路由和模板渲染。

**架构**：

```
futures.drifter.indevs.in ─┐
options.drifter.indevs.in ─┼──→ Reverse Proxy ──→ Flask App (:5100)
                                    │
                                    ├── Host: futures.drifter → 渲染 futures_dashboard.html
                                    └── Host: options.drifter  → 渲染 options_dashboard.html
```

如果反向代理不支持域名路由，则 PM2 启两个实例：

```
futures.drifter.indevs.in ──→ PM2 Instance 1 (:5101) → Flask (futures 模式)
options.drifter.indevs.in ───→ PM2 Instance 2 (:5102) → Flask (options 模式)
```

## 拆解步骤（按执行顺序）

### Step 1 — 期货面板 HTML 剥离 + API 精简（1 Cycle）
**产出物**: `web/templates/futures_dashboard.html`
- 从 `dashboard.html` 中剥离期货信号矩阵、板块统计、SmartFilter、持仓看板 + 健康面板
- 移除期权策略卡片和 IV 相关 JS
- 保留公共组件（统计栏、健康面板）

### Step 2 — 期货面板 Flask 路由 + 部署测试（1 Cycle）
**产出物**: 修改 `web/app.py`，部署测试
- 新增 `/` 路由检测 host → 选择模板
- 或新增 `--mode` 启动参数
- 部署到 `futures.drifter.indevs.in` 验证

### Step 3 — 期权面板 HTML 剥离 + 优化（1 Cycle）
**产出物**: `web/templates/options_dashboard.html`
- 从 `dashboard.html` 中剥离期权策略卡片 + IV 状态 + Greeks
- 移除期货信号矩阵、板块统计、SmartFilter
- 保留健康面板
- 增强期权统计：IV 趋势图、策略收益分布等如果项目自主决定

### Step 4 — 期权面板 Flask 路由 + 部署测试（1 Cycle）
**产出物**: 修改 `web/app.py`，部署测试
- 配置 `options.drifter.indevs.in` 路由到期权页面
- 验证独立运行

### Step 5 — 原 unified 页面保留或重定向（0.5 Cycle）
- 原 `signals.drifter.indevs.in` 改为期货面板
- 或保留为统一入口并添加跳转链接

## 依赖关系

```
Step 1 (期货 HTML) ──→ Step 2 (期货部署)
                                              → Step 5 (原页处理)
Step 3 (期权 HTML) ──→ Step 4 (期权部署)
```

Step 1/3 无依赖，可并行；Step 2/4 无依赖，可并行；Step 5 依赖所有前置步骤完成。

## 风险与注意事项

1. **前端设计规则**：这是一个前端交付，必须在使用 `frontend-design.md` 后进入代码实现（收敛规则第6条）
2. **反向代理配置**：需要确认当前域名的反向代理机制（nginx/Caddy/Cloudflare Tunnel/其他）——目前不确定，可能需要 DevOps 介入
3. **域名 DNS**: 需要为 `futures.drifter.indevs.in` 和 `options.drifter.indevs.in` 添加 DNS 记录
4. **API 兼容**: API 端点不变，但期权面板需要新增期权特有统计端点（如 IV 趋势历史）
5. **SmartFilter 归属**：防火墙是针对期货信号过滤的，期权面板不应包含

## 其他需求（项目自主决定）
- 期权面板添加 IV 趋势图
- 期权面板添加 Greeks 概览面板
- 统一导航栏让两个面板间互相跳转
