# Plan: monito Dashboard

## 目标

为已登录用户构建一个功能完整的 Dashboard（控制面板），用于管理 monitors、查看监控状态、管理计费和账户设置。

## 背景调研

### 现有技术栈
- Cloudflare Workers + Hono（SSR API）
- D1 SQLite 数据库
- 用户认证：API Key (localStorage) + Magic Link 登录
- 产品页：SSR'd HTML（`product-page.ts` 内联模板字符串）
- 状态页：独立的 Cloudflare Pages 站点（`monito-5sy.pages.dev`）
- Stripe 计费集成完成（Pro $9/mo, Team $24/mo）

### 已有 API 资源
| API | Auth | 用途 |
|-----|------|------|
| `GET /api/status` | No | 公共状态概览 |
| `GET /api/uptime?window=` | No | 全局 uptime（1h/24h/7d/30d） |
| `GET /api/monitors` | Yes | 用户 monitors 列表 |
| `GET /api/monitors/:id` | Yes | 单个 monitor |
| `GET /api/monitors/:id/checks?limit=` | Yes | 检查历史 |
| `GET /api/monitors/:id/uptime?window=` | Yes | 单个 monitor uptime |
| `POST /api/monitors` | Yes | 创建 monitor |
| `DELETE /api/monitors/:id` | Yes | 删除 monitor |
| `POST /api/stripe/create-checkout` | Yes | 创建 Stripe Checkout |
| `GET /api/confirm-payment` | No | 确认支付结果 |

### 需要新增的 API（Dashboard 推导出的缺口）
| API | 说明 |
|-----|------|
| `GET /api/user/me` | 当前用户信息（plan、email、monitor limit、api_keys） |
| `PUT /api/user/settings` | 更新用户设置（alert email、name） |
| `POST /api/auth/rotate-key` | 轮换 API key |

---

## 一、Persona 与用户场景（Interaction Cooper）

### Primary Persona：独立开发者阿勇
- **背景**：全栈开发者，运营多个 API 服务（自家项目 + 客户项目）
- **目标**：确保 API 持续在线，在用户发现问题之前就收到告警
- **痛点**：不想花时间配置复杂的监控系统，需要"开箱即用"
- **技术能力**：能理解 HTTP 状态码、响应时间、uptime 百分比

### 核心场景（按优先级排列）

1. **快速查看全局状态** → 打开 Dashboard 一眼看清所有 monitor 的状态概览
2. **创建新 monitor** → 输入 URL、名称、检查间隔，立即开始监控
3. **调查故障** → 看到某个 monitor 变红，点击查看最近检查记录和 uptime 趋势
4. **管理告警设置** → 配置 Slack webhook 和告警邮箱
5. **管理账户和计费** → 查看当前 plan、升级到 Pro、管理 API keys

### 导航结构

```
Dashboard
├── 📊 Overview（概览）        ← 首页/默认视图
│   ├── Status cards（总 monitor 数、up/down、uptime %）
│   ├── Recent activity feed（最近检查动态）
│   └── Top monitors by latency
│
├── 🔍 Monitors（监控列表）
│   ├── Full list with search/filter
│   ├── Per-monitor: name, URL, status, latency, uptime bar, last checked
│   └── + Create Monitor button
│
├── 📈 Monitor Detail          ← 点击某个 monitor 进入
│   ├── Current status + latency
│   ├── Uptime charts（24h/7d/30d tabs）
│   ├── Recent checks table
│   ├── Edit/Delete actions
│   └── Alert config（email/Slack）
│
├── ⚙️ Settings（设置）
│   ├── Profile（name, email）
│   ├── API Keys（view, rotate, copy）
│   └── Alert defaults（default email, Slack webhook URL）
│
└── 💳 Billing（计费）
    ├── Current plan & usage
    ├── Upgrade to Pro / Team CTA
    └── Payment history
```

---

## 二、功能定义与页面结构（Product Norman）

### Overview 页（MVP 核心）
- **信息**：总 monitors 数、当前 up/down 计数、全局 uptime %
- **操作**：无直接操作，纯信息展示
- **Loading**: 骨架屏
- **Empty**（首次无 monitor）：引导创建第一个 monitor 的 CTA
- **Error**: 静默重试，显示"数据加载中…"

### Monitors 列表页（MVP 核心）
- **信息**：所有 monitor 的列表（名称、URL、状态、延迟、uptime 条、最后检查时间）
- **操作**：创建 monitor（弹窗或独立表单）、点击进入详情、搜索/筛选
- **状态设计**：
  - Empty: 大号 "+" CTA + 引导文字 "添加你的第一个端点"
  - Error: 显示错误提示，保留已有列表（如果已加载过的数据）

### Monitor 详情页（MVP 核心）
- **信息**：monitor 基本信息 + 状态 + uptime 图表 + 最近检查记录
- **操作**：编辑名称/URL/间隔、删除、配置告警
- **注意事项**：删除需要二次确认（"确定删除？不可撤销"）

### Settings 页（MVP 基础）
- **信息**：用户信息、API key（掩码显示）
- **操作**：复制 API key、rotate key、更新设置
- **安全**：API key 默认掩码显示（只显示后 4 位），点击显示完整 key

### Billing 页（迭代 1）
- **信息**：当前 plan、用量（monitors 数/限制）、支付信息
- **操作**：切换月付/年付、点击升级

---

## 三、视觉设计与布局（UI Duarte）

### 设计语言
- **延续产品页的工业监控主题**，保持一致品牌体验
  - 深色背景（#0a0e14）保持不变
  - 绿色（#22c55e）表示正常运行
  - 红色（#ef4444）表示故障
  - JetBrains Mono 等宽字体用于数据和标签
  - Inter 字体用于正文
- **Dashboard 专属进化**：
  - 加入更多数据可视化元素（迷你图表、sparklines）
  - 增强的信息密度（比营销页更紧凑）
  - 导航系统（sidebar）区分于公开页

### 布局方案

**Desktop（≥ 900px）**：
```
┌──────────────┬──────────────────────────────────────────┐
│              │  Dashboard                                │
│   Sidebar    │  ┌───────┐ ┌───────┐ ┌───────┐           │
│              │  │ Up 12  │ │ Down 1 │ │ 99.8% │           │
│  📊 Overview │  └───────┘ └───────┘ └───────┘           │
│  🔍 Monitors │                                           │
│  ⚙️ Settings │  ┌─ Monitor List ──────────────────────┐  │
│  💳 Billing  │  │ Name       Status  Latency  Uptime  │  │
│              │  │ API A      ● up    123ms    99.9%   │  │
│              │  │ API B      ● up    45ms     100%    │  │
│              │  └─────────────────────────────────────┘  │
│  M monito    │                                           │
└──────────────┴──────────────────────────────────────────┘
```

**Mobile（< 768px）**：
- Sidebar 收起为 hamburger menu
- 内容单列布局
- 数据卡片从上到下排列

### 核心组件
- **StatusCard**: 显示统计数字（up/down/total/uptime%）的矩形卡片
- **MonitorRow**: 列表中每行显示 monitor 信息（状态点、名称、延迟、uptime 条）
- **UptimeBar**: 水平进度条表示 uptime 百分比
- **StatusDot**: 绿色/红色/黄色圆点表示当前状态
- **EmptyState**: 大号图标 + 引导文字 + CTA
- **ErrorState**: 感叹号 + 错误描述 + 重试按钮
- **SkeletonCard**: 加载中的占位卡片（灰色脉冲动画）

### 响应式断点
| 断点 | 说明 |
|------|------|
| ≥ 900px | Desktop sidebar layout |
| 768-899px | Narrow sidebar or collapsible |
| < 768px | Mobile single column, hamburger nav |

---

## 四、技术架构（CTO Vogels）

### 架构选型：SSR + 客户端增强（Worker 内嵌）

**推荐方案：Hono SSR + 客户端 JS 增强（inline script）**
- Dashboard 作为新的 SSR 路由 `/dashboard/*` 添加到现有 Worker
- HTML shell 由 Worker 渲染
- 数据通过客户端 JS 调用现有 API（/api/monitors、/api/uptime）获取
- 优点：零额外基础设施、共享认证、隔离部署

**不选 SPA 的理由**：
- 需要额外的前端构建步骤和部署（增加复杂性）
- monito 当前的构建流程不支持前端 bundler（只有 esbuild 打包 Worker）
- 引入 React/Vue 会增加 Worker bundle size，影响冷启动

**不选纯 MPA 的理由**：
- Dashboard 数据是动态的，每次整页刷新浪费 Worker CPU
- 前后端耦合过紧，修改 UI 需要改 Worker 代码

**不选 Cloudflare Pages 的理由**：
- 需要单独部署、跨域认证、维护两套部署流程
- 用户认证状态需要在 Pages 和 Worker 之间传递，复杂度高

### 路由设计

| 路由 | Handler | 说明 |
|------|---------|------|
| `GET /dashboard` | SSR → HTML | Overview 页（SSR shell + client data fetch） |
| `GET /dashboard/monitors` | SSR → HTML | Monitors 列表页 |
| `GET /dashboard/monitors/:id` | SSR → HTML | Monitor 详情页 |
| `GET /dashboard/settings` | SSR → HTML | 设置页 |
| `GET /dashboard/billing` | SSR → HTML | 计费页 |

所有 Dashboard 路由共享一个 auth 中间件：检查 localStorage 中的 API key → 未认证则重定向到产品页

### 数据流设计

```
Browser                    Worker (Hono)              D1
  │                            │                       │
  ├─ GET /dashboard ──────────→│                       │
  │                            ├─ SSR HTML shell ──────│
  │←─── HTML (with inline JS) ─┤                       │
  │                            │                       │
  ├─ fetch(/api/monitors) ───→│                       │
  │   (x-api-key in header)    ├─ SELECT monitors ────→│
  │                            │←─── results ──────────┤
  │←─── JSON monitors ────────┤                       │
  │                            │                       │
  ├─ client renders data ──── │                       │
```

### 安全考虑
- API Key 存储在 localStorage（现有模式，不改变）
- 所有 `/dashboard/*` 路由通过中间件验证 auth（检查 x-api-key header）
- 未认证 → 返回 401 + 客户端重定向到产品页
- 敏感操作（delete monitor、rotate key）需要额外确认步骤
- 输入防 XSS：所有用户输入插入 DOM 前转义（使用 textContent, 不直接用 innerHTML）
- CSRF：API 使用 x-api-key header 认证，天然防 CSRF

### 故障模式
| 故障 | Dashboard 行为 |
|------|---------------|
| Worker 挂掉 | 页面打不开，用户看到 Cloudflare 502 |
| D1 超时 | API 返回 500，Dashboard 显示"数据加载失败" + 重试按钮 |
| API Key 过期 | 401 响应，Dashboard 清除 key 并跳转到产品页注册 |
| Stripe 未配置 | Billing 页显示"Stripe 暂未配置"提示 |

---

## 五、实现方案（Fullstack DHH）

### 技术选型
- **框架**：无额外框架，纯 HTML + CSS + vanilla JS（inline script）
- **样式**：复用现有 CSS 变量系统（`:root` 变量），Dashboard 专属样式后置
- **图表**：用 Canvas 或 SVG 绘制 uptime bars，无需第三方库
- **构建**：通过现有 `direct-encode.mjs` 脚本将 HTML 编码到 .ts 文件

### 文件结构
```
src/
├── index.ts                    # 主入口（新增 /dashboard/* 路由）
├── product-page.ts             # 产品页（不变）
├── dashboard-page.ts           # Dashboard HTML（新文件, auto-generated）
├── stripe.ts                   # Stripe 模块（不变）
└── ...
dashboard/
└── index.html                  # Dashboard HTML 源文件（手工编写）
```

### 实现步骤（按 Cycle 拆解）

**Step 3.1 — 设计 Dashboard 布局与路由（✅ 当前 Cycle #95）**
- 产出计划文档（本文件）
- 更新共识

**Step 3.2 — 创建 Dashboard HTML 基础框架（Cycle #96, ~20min）**
- 编写 `dashboard/index.html`：完整的 HTML shell（sidebar nav + 内容区）
- 复用产品页 CSS 变量 + 新增 Dashboard 专属样式（sidebar, nav, cards）
- 新增 `/dashboard`、`/dashboard/monitors` 等 SSR 路由
- 通过 `direct-encode.mjs` 生成 `src/dashboard-page.ts`

**Step 3.3 — Overview 页：状态卡片 + 实时数据（Cycle #97, ~20min）**
- Overview 页 HTML（3 个 status cards：total/up/down/uptime）
- 客户端 JS：`fetch(/api/status)` 填充数据
- Loading skeleton + Error + Empty 状态处理
- 自动刷新（每 30 秒）

**Step 3.4 — Monitors 列表页（Cycle #98, ~20min）**
- Monitors 列表 HTML（表格/卡片布局）
- 客户端 JS：`fetch(/api/monitors)` + 列表渲染
- 创建 monitor 表单（弹窗或 inline）
- 搜索/筛选功能
- 状态、延迟、uptime 条的展示

**Step 3.5 — Monitor 详情页（Cycle #99, ~20min）**
- Monitor 详情 HTML（基本信息 + uptime 图表 + 检查记录）
- Uptime chart（SVG/Canvas, 24h/7d/30d 切换）
- 最近检查记录表
- 编辑/删除功能

**Step 3.6 — Settings 页（Cycle #100, ~15min）**
- 用户信息展示
- API key 查看/复制/轮换
- 告警设置（默认邮箱、Slack webhook URL）

**Step 3.7 — Billing 页（Cycle #101, ~15min）**
- 当前 plan 展示 + 用量
- Upgrade CTA（复用现有 `upgradeToPro()`）
- 支付成功状态

**Step 3.8 — 响应式 + 打磨（Cycle #102, ~15min）**
- Mobile navbar (hamburger)
- 各页面 responsive 调整
- 动效（sidebar 展开收起、页面切换过渡）

### 总工时估算
| Step | 任务 | 预估工时 |
|------|------|---------|
| 3.1 | 计划文档 | 15min ✅ |
| 3.2 | Dashboard 框架 | 20min |
| 3.3 | Overview 页 | 20min |
| 3.4 | Monitors 列表 | 20min |
| 3.5 | Monitor 详情 | 20min |
| 3.6 | Settings 页 | 15min |
| 3.7 | Billing 页 | 15min |
| 3.8 | 响应式打磨 | 15min |
| **Total** | | **~2h（8 cycles）** |

### What NOT to do（防止 Scope Creep）
- ❌ 不要改用 React/Vue/Svelte — vanilla JS 足够
- ❌ 不要引入 Chart.js 等图表库 — uptime bars 可以用 CSS/SVG 实现
- ❌ 不要做实时 WebSocket — 30 秒 polling 足够
- ❌ 不要做多用户/团队功能 — 那是 Team plan 的内容
- ❌ 不要重构现有产品页 — 专注 Dashboard
- ❌ 不要做 PWA/离线功能
- ❌ 不要做 dark mode toggle — 已经默认深色

---

## 依赖关系与顺序

```
3.1 Plan（当前）──→ 3.2 框架 ──→ 3.3 Overview
                      │            │
                      │            └──→ 3.4 Monitors 列表
                      │                     │
                      │                     └──→ 3.5 Monitor 详情
                      │                              │
                      │                              ├──→ 3.6 Settings
                      │                              └──→ 3.7 Billing
                      │                                       │
                      └──────────────────────────────────────→ 3.8 打磨
```

3.2 是所有页面的前置——必须先创建框架路由和 sidebar nav。
3.3–3.7 可以按任意顺序实现，但推荐的顺序遵循用户使用频率（Overview 最重要 → Monitors → Detail → Settings → Billing）。
3.8 是最后的打磨步骤。

---

## 共识 Next Action 格式

```markdown
## Next Action
**Step 3 — Dashboard 开发**

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 3.1 | 设计 Dashboard 布局与路由 | 15min | 计划文档 ✅ |
| 3.2 | 创建 Dashboard HTML/CSS 基础框架 | 20min | dashboard/index.html + dashboard-page.ts |
| 3.3 | Overview 页：状态卡片 + 实时数据 | 20min | Overview 页面代码 |
| 3.4 | Monitors 列表页 + 创建表单 | 20min | Monitors 页面代码 |
| 3.5 | Monitor 详情页 + uptime 图表 | 20min | 详情页面代码 |
| 3.6 | Settings 页（Profile + API Keys） | 15min | Settings 页面代码 |
| 3.7 | Billing 页（Plan + Upgrade） | 15min | Billing 页面代码 |
| 3.8 | 响应式打磨 + 动效 | 15min | 完善代码 |

**当前：Cycle 95 — Step 3.1 设计 Dashboard 布局与路由（✅ 已完成计划文档）**
下一步：Cycle 96 — Step 3.2 创建 Dashboard HTML/CSS 基础框架
```