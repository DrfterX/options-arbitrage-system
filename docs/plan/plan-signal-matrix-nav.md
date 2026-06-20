# Plan: 统一导航栏（B.2 — 信号矩阵面板改良）

## 目标

将 portal / futures / options / pricing / api_docs 五个页面的导航栏统一为**同一套 tab 式顶部导航**，让用户在三个产品面板 + 定价 + API 文档之间无缝切换。

## 现状分析

### 路由 → 模板映射

| 域名/路径 | 模板 | 当前导航状态 |
|-----------|------|-------------|
| `signals.drifter.indevs.in` (root) | `portal.html` | ✅ 有 topbar，但 SPA 式 `data-tab` spans |
| `futures.drifter.indevs.in` | `futures_dashboard.html` | ✅ `<a href>` 链接，较完整 |
| `options.drifter.indevs.in` | `options_dashboard.html` | ✅ `<a href>` 链接，较完整 |
| `/pricing` | `pricing.html` | ❌ **完全没有导航栏** |
| `/api/docs` | `api_docs.html` | ⚠️ 简化版 2-tab 导航 |
| 其他/默认 | `dashboard.html` (fallback) | ✅ `<a href>` 链接 + JS auto-active |

### 当前各面板 Tab 内容对比

| Tab | portal.html | futures_dashboard | options_dashboard | dashboard.html (fallback) | api_docs.html |
|-----|------------|-------------------|-------------------|--------------------------|---------------|
| 总览 | `◈ 总览` active (data-tab span) | `◈ 总览` `<a>` link | `◈ 总览` `<a>` link | `◈ 总览` `<a>` link | `◈ 信号矩阵` `<a>` |
| 期货 | `📈 期货` (data-tab span) | `📈 期货` active `<span>` | `📈 期货` `<a>` link | `📈 期货` `<a>` link | — |
| 期权 | `📉 期权` (data-tab span) | `📉 期权` `<a>` link | `📉 期权` active `<span>` | `📉 期权` `<a>` link | — |
| API | `⎔ API` `<a>` link | `⎔ API` `<a>` link | `⎔ API` `<a>` link | — | `⎔ API 文档` active |
| 定价 | `✦ Premium` (data-tab span) | `✦ 定价` premium-tab `<a>` | `✦ 定价` premium-tab `<a>` | `✦ 定价` premium-tab `<a>` | — |

### 右侧工具栏对比

| 元素 | portal | futures | options | dashboard (fallback) |
|------|--------|---------|---------|---------------------|
| user-plan-badge | ❌ | ✅ | ✅ | ✅ |
| data-badge (count) | `totalBadge` (JS 动态) | `symbolCount` (N 型品种) | `optionCount` (策略数) | `total_signals` 品种 |
| topbar-time | ✅ | ✅ | ✅ | ✅ |
| density-btn | ✅ | ✅ | ✅ | ✅ |
| reg-btn | ✅ | ❌ | ❌ | ❌ |
| login button | ❌ | ❌ | ✅ (hidden) | ✅ (hidden) |
| pricing topbar | ❌ 无 | ❌ 无 | ❌ 无 | ❌ 无 |

### 关键不一致问题

1. **导航模式不一致** — portal 用 `data-tab` SPA 切换，其他页面用 `<a href>` 跨页面跳转。导致：
   - portal 的 "Premium" tab 是纯前端切换（显示 premium 内容），而非跳转到 `/pricing`
   - 其他面板的 "定价" tab 直接跳转到 `/pricing`
2. **Tab 命名不一致** — portal 是 "Premium"，其他是 "定价"
3. **Tab 排序不一致** — portal 是 总览→期货→期权→API→Premium；其他去掉 Premium/定价 在期货和期权之间
4. **pricing 页面无导航** — 用户到定价页后无法直接跳回产品面板
5. **api_docs 导航不全** — 只有 信号矩阵 + API 文档，缺失其他产品入口
6. **portal 缺少 user-plan-badge** — 无法显示当前用户订阅状态
7. **JS auto-active 脚本** — dashboard.html 有，futures/options 用静态 hardcode active，portal 用 data-tab JS

## 设计方案

### 方案：统一为 `<a href>` 多页面导航

**理由**：三个产品面板已是独立域名，SPA 风格切换在此架构下不合理。统一为 `<a href>` 让浏览器标准行为接管导航。

### 统一后的 Tab 结构和排序（所有页面一致）

```
[◈ 总览]  [📈 期货]  [📉 期权]  [⎔ API]  [✦ 定价]
```

- "定价" 统一命名（替代 portal 的 "Premium"），保留 `.premium-tab` CSS class
- 当前页面用 `class="nav-tab active"`，Jinja2 模板变量控制

### 右侧工具栏统一

| 元素 | portal | futures | options | pricing | api_docs |
|------|--------|---------|---------|---------|----------|
| user-plan-badge | ✅ 新增 | ✅ 保留 | ✅ 保留 | ✅ 新增 | ❌ 不需要 |
| data-badge | ✅ 改为 static | ✅ 保留 | ✅ 保留 | ❌ 不需要 | ❌ 不需要 |
| topbar-time | ✅ 保留 | ✅ 保留 | ✅ 保留 | ✅ 新增 | ✅ 保留 |
| density-btn | ✅ 保留 | ✅ 保留 | ✅ 保留 | ❌ 不需要 | ❌ 不需要 |
| reg/login btn | 合并到 plan badge | — | — | — | — |

### Active tab 判定机制

统一使用 **Flask URL 域名检测**，在渲染时传入 `active_tab` 变量：

```python
host = request.host
if 'futures' in host: active_tab = 'futures'
elif 'options' in host: active_tab = 'options'
else: active_tab = 'overview'
# /pricing → 'pricing', /api/docs → 'api'
```

在模板中：

```html
<a href="https://signals.drifter.indevs.in" class="nav-tab {{ 'active' if active_tab == 'overview' }}">
  <span class="nav-tab-icon">◈</span> 总览
</a>
```

## 影响文件

| 文件 | 修改内容 |
|------|---------|
| `web/templates/portal.html` | nav-tabs 重构：data-tab spans → `<a>` links；"Premium" rename → "定价"；移除 SPA tab-JS；添加 user-plan-badge；添加 active tab Jinja2 判定 |
| `web/templates/futures_dashboard.html` | 微调：统一 tab 排序（确保与标准一致）；移除硬编码 active 改用 Jinja2 |
| `web/templates/options_dashboard.html` | 微调：同上 |
| `web/templates/dashboard.html` | 同步修改（fallback 模板） |
| `web/templates/pricing.html` | **新增完整 topbar**（与产品面板一致，不含 data-badge/density-btn） |
| `web/templates/api_docs.html` | 扩展导航（当前仅 2 tab → 完整 5 tab） |
| `web/app.py` | 为各路由添加 `active_tab` 模板变量 |

## 执行拆解

**共 2 个 Cycle**：

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| B.2.1 | ✅ Plan：读各面板导航栏现状 + 设计统一方案 | 15min | 本文档 |
| B.2.2 | 实现：统一 6 个模板的导航栏 + app.py 渲染变量 | 20min | 代码修改 + commit |

### B.2.2 实现细项

1. **app.py** — 为 5 个路由添加 `active_tab` 模板变量（portal→'overview', futures→'futures', options→'options', /pricing→'pricing', /api/docs→'api'）
2. **portal.html** — 替换 data-tab spans 为 `<a>` links，添加 user-plan-badge，重命名 "Premium" → "定价"
3. **futures_dashboard.html** — active tab 改用 Jinja2 变量
4. **options_dashboard.html** — active tab 改用 Jinja2 变量
5. **dashboard.html** — 同步更新
6. **pricing.html** — 新增完整 topbar（全 5 tab，不含 data-badge/density-btn）
7. **api_docs.html** — 扩展 nav-tabs 为完整 5 tab