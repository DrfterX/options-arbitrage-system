# Auto Company Consensus

## Last Updated
2026-06-13 02:06 CST

## Project Owner & Strategic Direction

**当前运行者：阿勇**（非原作者 MaxMiksa，原始框架已 fork 自用）
**核心使命：自动驾驶开发「期权期货交易系统」**

### 优先级铁律（不可违反）
1. **期权期货交易系统（`~/options_arbitrage_system/`）** — 最高优先级，Auto Company 全体 Agent 的首要任务
2. **critiq（代码审查 CLI）** — 已发布，保留为通用开发工具，无新功能开发
3. **monito（API 监控）** — 保留，但重新定位为期权系统的**基础设施监控层**，非独立产品
4. **任何新想法** — 必须先回答「这个想法对期权期货系统有什么直接帮助？」。不能创造新的独立产品。
5. **snapog（OG 图生成）** — ❌ **永久停止开发。** 仅保留代码存档，不作为活跃项目维护。

## What We Did This Cycle (Cycle #14)

**实现 Step 5.5 — 自动建仓集成（Pipeline 自动追踪 ENTRY）**

### 具体产出
1. **`pipeline/orchestrator.py`** — 期货扫描循环（`run_futures_scan`）新增自动建仓逻辑：
   - SmartFilter 通过且 `signal_type == "ENTRY"` 时调用 `PositionTracker.open_position()`
   - 传参：`entry_price` / `stop_loss` / `take_profit`（从 SignalResult 获取）
   - 关联 `signal_id`（已记录信号），`signal_type="futures"`
   - 建仓后立即调用 `update_pnl()` 初始化浮动盈亏
2. **`pipeline/orchestrator.py`** — 期权扫描循环（`run_options_scan`）新增自动建仓逻辑：
   - 去重通过的 ENTRY 信号中，`ratio_spread` 按 side 方向建仓（call→LONG / put→SHORT）
   - 中性策略（short_strangle / iron_condor）跳过（无明确 LONG/SHORT 方向）
   - 使用 `futures_price` 作为入场参考价
3. **去重保障** — `open_position()` 内部 `_find_open_position()` 确保同合约+方向不重复建仓

### 决策：自动建仓触发条件
- **选择立即建仓**（不等待确认周期）
- 理由：Paper Trading 的目的是追踪信号表现，立即建仓能完整记录信号生命周期的真实表现

## Key Decisions Made
1. 自动建仓触发条件：新 ENTRY 信号出现即建仓，不等待确认周期
2. 期权中性策略（short_strangle / iron_condor）跳过自动建仓，因无明确 LONG/SHORT 方向
3. 建仓后立即初始化 PnL（`current_price = entry_price`），确保 Dashboard 持仓看板显示准确的初始状态

## Active Projects
- **✅ 期权期货交易系统**（`/Users/ayong/options_arbitrage_system/`）— **最高优先级**
  - ✅ Pipeline 自动运行（launchd 每 30 分钟全量扫描）
  - ✅ 6 个活跃 ENTRY 信号
  - ✅ macOS 桌面通知已上线
  - ✅ Dashboard 信号矩阵 + IV 图表 + 回测 + 健康面板 + 持仓看板
  - ✅ Paper Trading 全套：模型 → API → UI → 自动建仓
  - ❌ Telegram → 降为低优先级，用户自行配置

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
| 5.4 | Dashboard 持仓看板 UI | 20min | 持仓卡片 + 历史表格 + 统计 | ✅ 完成 |
| 5.5 | 自动建仓集成（Pipeline 自动追踪 ENTRY） | 15min | orchestrator.py 集成 | ✅ 完成 |
| 5.6 | Critic Review（Munger 审查） | 10min | review 报告 | 📋 待开始 |

**当前：Cycle 15 — Step 5.6 Critic Review（Munger 审查）**

**Step 5.6 的详细任务：**
1. 调用 critic-munger 对 Step 5 的整个持仓追踪系统进行逆向审查
2. 重点检查：数据一致性风险（positions vs trades 表）、自动建仓触发逻辑是否完备、有无遗漏的边界场景
3. 产出审查报告到 `docs/critic/paper_trading_review.md`

## Company State
- Mission: 自动驾驶开发期权期货交易系统
- Tech Stack: Python + Flask + SQLite + Bash + launchd
- System: 62 品种期货信号系统 + 商品期权套利引擎
- DB: trading_system.db — 13 张表（含 positions + trades）
- Active ENTRY Signals: 5 futures（SC/PX/LC/AU）+ 1 option（MA Iron Condor）
- Paper Trading: ✅ 持仓追踪引擎 + API 端点 + Dashboard UI + Pipeline 自动建仓
- Pipeline: ✅ 自动运行（launchd 每 30 分钟全量扫描，含自动建仓）
- Web Dashboard: ✅ localhost:5100（含持仓看板）
- Active Positions: 1 open（SC2607 LONG）, 1 closed（已盈利 +10.0）
- Notifications: ✅ macOS 桌面通知
- Revenue: $0
- Users: 1（阿勇）

## Open Questions
- ❓ 止损逻辑具体参数？→ 留到 Step 5.6 讨论
