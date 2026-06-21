# P1 期权面板 UI/UX 修复方案

## 目标

修复期权信号仪表盘（options.drifter.indevs.in）的 4 个 UI/UX 问题：IV 柱状图显示、代码格式/中文名、策略详情图标、评分排序与透明度。

## 问题诊断

### 1. IV 柱状图显示问题

**根因分析**：
- 当前 echarts 配置中 `barWidth: '70%'` + `barCategoryGap: '25%'` 在品种过多时（>30）导致柱重叠/挤压
- X 轴标签 `interval` 用 `Math.max(0, Math.floor(IV_DATA.length / 18))`，品种多时跳过太多
- `rotate: 30` 后长中文名显示不全（截断或换行错位）
- `bottom: 140` 预留空间在 18+ 品种时仍然不够

**修复方向**：
- 动态调整柱宽：品种 > 40 时缩到 `50%`，> 60 时缩到 `35%`
- X 轴标签优化：中文名换行用 `/` 分隔而非 `\n`，减少行高
- `bottom` 根据品种数动态计算（`Math.min(140, 60 + IV_DATA.length * 2)`）
- 图例过多时启用 echarts 自带滚动

### 2. 代码格式 / 中文名

**根因分析**：
- 策略类型（`s.strategy`）英文下划线格式如 `iron_condor`、`vertical_spread`，模板只用 `|replace('_', ' ')` 转成空格
- 需要中文映射表（线 D 要求）
- `s.name` 中文名已由后端 `_enrich_options_signals()` 使用 `SYMBOL_NAMES` 字典添加，但合约显示格式可能不一致

**修复方向**：
- 添加前端 or 后端策略类型中文映射表：
  - `iron_condor` → `铁鹰策略`
  - `vertical_spread` → `垂直价差`
  - `calendar_spread` → `日历价差`
  - `covered_call` → `备兑看涨`
  - `protective_put` → `保护看跌`
  - `straddle` → `跨式策略`
  - `strangle` → `宽跨式`
- 品种名显示优化：如果 `s.name` 存在，优先在 table/card 显示中文名 + symbol

### 3. 策略详情图标

**根因分析**：
- 当前策略详情触发是表格中的 `📋` emoji (line 873)，无交互提示
- 缺失 hover tooltip 提示"查看详情"
- 卡片 view（右侧）未提供详情入口，只能通过左侧表格查看

**修复方向**：
- 详情图标改为更直观的 `ⓘ` 或 `🔍`，加 `title="查看策略详情"`
- 卡片（option-card）也添加详情触发入口（右下角小图标）
- `showStratDetailFromData()` 函数使用 `window._signalsData` 按 idx 查找，需确保索引与 cards 一致

### 4. 评分排序与透明度

**根因分析**：
- 后台传入的 `options` 按数据库查询顺序，前端 **没有排序**
- 高评分（≥70）和低评分（<50）用不同颜色区分，但未按 `unified_score` 降序排列
- "透明度" 可能指低评分策略应降低视觉权重（如 opacity 减小）

**修复方向**：
- SSR 渲染时按 `unified_score DESC` 降序排列（后端排序最可靠）
- 评分分数 ≤30 时 card/row 的 `opacity: 0.6`，引导注意力到高评分策略
- Score < 30 的策略应排在最后（但仍在列表中，不隐藏）

## 拆解步骤

### Step D.1 — IV 柱状图自适应显示（1 Cycle, ≤20min）

**目标**：修复 IV 柱状图在品种多时显示错乱的问题

**改动文件**：
- `web/templates/options_dashboard.html` — initIV() 函数

**具体修改**：
1. 动态柱宽：`barWidth` 使用 `Math.min(70, Math.max(30, 2800 / IV_DATA.length))`
2. X 轴标签换行优化：`formatter` 中中文名用 ` · `（中间点）而非 `\n`
3. X 轴 `bottom` 动态计算：`Math.max(60, Math.min(200, 50 + IV_DATA.length * 2.5))`
4. X 轴标签间隔自适应：品种 > 50 时 `interval: Math.floor(IV_DATA.length / 30)`，否则 0

**产出**：options_dashboard.html 更新 + 视觉验证截图

### Step D.2 — 策略类型中文名 + 品种代码格式化（1 Cycle, ≤20min）

**目标**：策略类型显示中文而非英文，品种代码格式统一

**改动文件**：
- `web/templates/options_dashboard.html` — Jinja2 模板 + SSR 渲染
- 或在 `web/app.py` — 后端 `_enrich_options_signals()` 添加映射

**具体修改**：
1. 在 `_enrich_options_signals()` 或前端添加策略类型中文映射
2. 模板中 `s.strategy|replace('_', ' ')` → `s.strategy_cn`（后端映射）
3. 卡片/表格中的中文名优先显示（已有 `s.name`，需保证在模板中渲染正确）
4. 合约格式统一：移除多余空格，主连合约加 `cont` 标记

**产出**：app.py 或 HTML 变更 + 页面截图验证

### Step D.3 — 策略详情图标与交互增强（1 Cycle, ≤15min）

**目标**：详情图标更清晰、右侧卡片也支持查看详情

**改动文件**：
- `web/templates/options_dashboard.html`

**具体修改**：
1. `📋` 改为 `🔍` + `title="查看策略评分分解"`
2. 右侧策略卡片（`option-card`）底部添加详情按钮
3. 修复 `showStratDetailFromData()` 将 idx 映射到 cards 数据
4. Popup 关闭体验优化：点外部区域直接关闭

**产出**：HTML 变更 + 交互验证

### Step D.4 — 评分排序与透明度降权（1 Cycle, ≤15min）

**目标**：策略按评分降序排列，低分降透明度

**改动文件**：
- `web/templates/options_dashboard.html` — 前端排序 + 透明度
- `web/app.py` — 后端排序（可选，更可靠）

**具体修改**：
1. 后端 `api_options_signals()` 和模板渲染按 `unified_score` DESC 排序
2. 评分 ≤30 的 card 添加 `opacity: 0.6`（CSS 类 `.strength-dim`）
3. 评分 ≤30 的 table row 添加 `opacity: 0.55`

**产出**：app.py 或 HTML 变更 + 排序验证

## 依赖顺序

```
D.1 (IV 图) ── 无依赖，可先做
D.2 (中文名) ── 无依赖，可先做
   ├── D.3 (详情图标) ── 依赖 D.2（中文名正确后图标上下文更清晰）
   └── D.4 (评分排序) ── 无依赖，可独立做
```

推荐顺序：**D.1 → D.2 → D.3 → D.4**
也可并行：D.1 和 D.2 可互换顺序

## 验证方法

每个步骤完成后：
1. 本地访问 options.drifter.indevs.in 验证
2. 检查 15m/1h 自动刷新后渲染是否保持正确
3. 跨浏览器检查（Chrome/Firefox）

## 涉及文件

| 文件 | 用途 | 改动步骤 |
|------|------|---------|
| `projects/options_arbitrage_system/web/templates/options_dashboard.html` | 期权仪表盘模板 | D.1, D.2, D.3, D.4 |
| `projects/options_arbitrage_system/web/app.py` | 后端 (可选改动) | D.2, D.4 |
| `projects/options_arbitrage_system/web/static/options.css` | 期权面板 CSS | D.3, D.4 |