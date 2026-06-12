# Auto Company Consensus

## Last Updated
2026-06-13 01:46 CST

## Project Owner & Strategic Direction

**当前运行者：阿勇**（非原作者 MaxMiksa，原始框架已 fork 自用）
**核心使命：自动驾驶开发「期权期货交易系统」**

### 优先级铁律（不可违反）
1. **期权期货交易系统（`~/options_arbitrage_system/`）** — 最高优先级，Auto Company 全体 Agent 的首要任务
2. **critiq（代码审查 CLI）** — 已发布，保留为通用开发工具，无新功能开发
3. **monito（API 监控）** — 保留，但重新定位为期权系统的**基础设施监控层**，非独立产品
4. **任何新想法** — 必须先回答「这个想法对期权期货系统有什么直接帮助？」。不能创造新的独立产品。
5. **snapog（OG 图生成）** — ❌ **永久停止开发。** 仅保留代码存档，不作为活跃项目维护。

## What We Did This Cycle (Cycle #11)

**实现 Step 5.3 — API 端点（positions CRUD + stats）**

### 实际完成
- ✅ `web/app.py` — 新增 5 个 Paper Trading 持仓 API 端点：
  - `GET /api/positions` — 当前持仓列表（open）
  - `GET /api/positions/history` — 历史平仓（支持 limit/offset 分页）
  - `POST /api/positions/open` — 手动建仓（含字段校验 + 去重检查，返回 409 冲突）
  - `POST /api/positions/close` — 平仓（支持 stop_loss/take_profit/signal_expired/manual 原因）
  - `GET /api/positions/stats` — 胜率/总盈亏/开平仓数统计
- ✅ 健康检查 API — `positions` 和 `trades` 表已加入监控列表
- ✅ 全链路集成测试通过（建仓 → 查询 → 平仓 → 统计 → 去重检查）

## Key Decisions Made
1. **API 路径设计** — `/api/positions` 前缀（与现有 `/api/signals` 等风格统一）
2. **去重检查逻辑** — 同一 contract + direction 仅能有一个 open 状态的持仓（已 close 的不影响重新开仓）
3. **平仓原因枚举** — 限定 `stop_loss` / `take_profit` / `signal_expired` / `manual` 四种，不合规返回 400
4. **`_get_position_tracker()`** — 沿用现有 `_get_hub()` 模式，每请求创建新实例

## Active Projects
- **✅ 期权期货交易系统**（`/Users/ayong/options_arbitrage_system/`）— **最高优先级**
  - ✅ Pipeline 自动运行（launchd 每 30 分钟全量扫描）
  - ✅ 6 个活跃 ENTRY 信号
  - ✅ macOS 桌面通知已上线
  - ✅ Dashboard 信号矩阵 + IV 图表 + 回测 + 健康面板
  - ❌ Telegram → 降为低优先级，用户自行配置
  - ✅ **Step 5.3 完成：** 持仓 API（CRUD + stats）5 个端点

- **✅ critiq（代码审查 CLI）** — v0.1.1 已发布到 npm，功能冻结

- **🔧 monito（API 监控基础设施）** — 已部署到 CF Workers

- **🗄️ snapog** — 已存档，不维护，不开发

## Next Action
**Step 5 — 实现 ENTRY 信号持仓追踪系统（Paper Trading）**（共 6 个 Cycle）

| # | 子任务 | 预期耗时 | 产出物 | 状态 |
|---|--------|---------|--------|------|
| 5.1 | 数据模型与 DB 迁移（positions + trades 表） | 15min | core/position_tracker.py + DB schema | ✅ 完成 |
| 5.2 | PositionTracker 核心逻辑（CRUD + PnL） | 20min | 完整的追踪模块 | ✅ 完成 |
| 5.3 | API 端点（positions CRUD + stats） | 15min | Flask API 路由 | ✅ 完成 |
| 5.4 | Dashboard 持仓看板 UI | 20min | 持仓卡片 + 历史表格 + 统计 | 📋 待开始 |
| 5.5 | 自动建仓集成（Pipeline 自动追踪 ENTRY） | 15min | orchestrator.py 集成 | 📋 待开始 |
| 5.6 | Critic Review（Munger 审查） | 10min | review 报告 | 📋 待开始 |

**当前：Cycle 11 — ✅ Step 5.3 完成，待 Cycle 12 开始 Step 5.4**

**Step 5.4 的详细任务（Dashboard 持仓看板 UI）：**
1. 在 `templates/dashboard.html` 中添加持仓面板区域
2. 前端 JS 调用 `GET /api/positions` 和 `GET /api/positions/stats` 渲染持仓卡片
3. 前端 JS 调用 `GET /api/positions/history` 渲染历史平仓表格
4. 添加持仓统计小部件（胜率/总盈亏/开仓数）

## Company State
- Mission: 自动驾驶开发期权期货交易系统
- Tech Stack: Python + Flask + SQLite + Bash + launchd
- System: 62 品种期货信号系统 + 商品期权套利引擎
- DB: trading_system.db — 15 张表（含新增 positions + trades）
- Active ENTRY Signals: 5 futures（SC/PX/LC/AU）+ 1 option（MA Iron Condor）
- Paper Trading: ✅ 持仓 API 就绪（5 个端点，含 CRUD + stats）
- Pipeline: ✅ 自动运行（launchd 每 30 分钟全量扫描）
- Web Dashboard: ✅ localhost:5100
- Notifications: ✅ macOS 桌面通知
- Revenue: $0
- Users: 1（阿勇）

## Open Questions
- ❓ 止损逻辑具体参数？→ 留到 Step 5.6 讨论
- ❓ 自动建仓触发条件（新 ENTRY 信号出现即建仓 vs 等待 1 个扫描周期确认）？→ 留到 Step 5.5 决定