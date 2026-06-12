# Auto Company Consensus

## Last Updated
2026-06-13 02:50 CST

## Project Owner & Strategic Direction

**当前运行者：阿勇**（非原作者 MaxMiksa，原始框架已 fork 自用）
**核心使命：自动驾驶开发「期权期货交易系统」**

### 优先级铁律（不可违反）
1. **期权期货交易系统（`~/options_arbitrage_system/`）** — 最高优先级，Auto Company 全体 Agent 的首要任务
2. **critiq（代码审查 CLI）** — 已发布，保留为通用开发工具，无新功能开发
3. **monito（API 监控）** — 保留，但重新定位为期权系统的**基础设施监控层**，非独立产品
4. **任何新想法** — 必须先回答「这个想法对期权期货系统有什么直接帮助？」。不能创造新的独立产品。
5. **snapog（OG 图生成）** — ❌ **永久停止开发。** 仅保留代码存档，不作为活跃项目维护。

## What We Did This Cycle (Cycle #20)

**Step 6.2 — 期权 PnL 修复（净权利金替代期货价 + 合约乘数）**

### 具体产出

1. **`pipeline/orchestrator.py`** — 期权 ENTRY 自动建仓使用净权利金：
   - 从 `sig["strategy_details"]["net_cost"]` 取期权的净权利金作为入场价
   - 兜底使用 `abs(net_cost)`，避免 negative net_cost（信用价差）导致 PnL 反向
   - 兼容 `strategy_details` 为空或 `net_cost` 为 0 的情况（回退到 futures_price）

2. **`core/position_tracker.py`** — PnL 计算支持合约乘数：
   - `_calculate_pnl()` 新增 `multiplier=1` 参数
   - 期货 PnL 公式：`(price_diff) × quantity × multiplier`
   - 期权 PnL 公式：`(premium_diff) × quantity`（multiplier=1，因 net_cost 已是货币金额）
   - `_get_multiplier()` 从 `ContractRegistry` 查询期货合约乘数（带缓存）
   - 期权 `signal_type` 返回 multiplier=1
   - `update_pnl()` 和 `close_position()` 均传递 multiplier 给 `_calculate_pnl()`
   - `get_open_positions()` 返回后端计算的 `unrealized_pnl`（含乘数）

3. **`web/static/style.css` + `web/templates/dashboard.html`** — 前端适配：
   - 前端使用后端返回的 `p.unrealized_pnl`（兜底自算）
   - 新增免责声明：`期货 PnL 已含合约乘数 · 期权 PnL 为净权利金（不含合约乘数）`

## Key Decisions Made
1. **合约乘数动态查询**：从 `ContractRegistry.get_multiplier()` 实时查询，无需 schema 变更
2. **期权 multiplier=1**：期权 PnL 基于净权利金（净值），不是价格乘合约乘数
3. **前端 PnL 来源**：优先使用后端 `unrealized_pnl`，兼容旧数据兜底自算
4. **短期不做 Black-Scholes**：期权 PnL 用净值直接计算，待后续评估是否需要非线性定价模型

## Active Projects
- **✅ 期权期货交易系统**（`/Users/ayong/options_arbitrage_system/`）— **最高优先级**
  - ✅ Pipeline 自动运行（launchd 每 30 分钟全量扫描）
  - ✅ 6 个活跃 ENTRY 信号
  - ✅ macOS 桌面通知已上线
  - ✅ Dashboard 信号矩阵 + IV 图表 + 回测 + 健康面板
  - ✅ Step 5.5: Auto-open paper trading for ENTRY signals
  - ✅ Step 5.6: Munger review completed
  - ✅ Step 6.1: 原子事务修复完成（P0 #1）
  - ✅ **Step 6.2: 期权 PnL 修复完成（P0 #2）**
  - ❌ Telegram → 降为低优先级，用户自行配置

- **✅ critiq（代码审查 CLI）** — v0.1.1 已发布到 npm，功能冻结

- **🔧 monito（API 监控基础设施）** — 已部署到 CF Workers

- **🗄️ snapog** — 已存档，不维护，不开发

## Next Action
**Step 6 — 修复 P0/P1 缺陷（Munger 审查跟进）**（共 7 个子任务）

| # | 子任务 | 预期耗时 | 产出物 | 状态 |
|---|--------|---------|--------|------|
| 6.1 | 开/平仓原子事务 | 15min | position_tracker.py | ✅ 完成 |
| 6.2 | 期权 PnL 修复（净权利金替代期货价） | 15min | orchestrator.py + position_tracker.py | ✅ 完成 |
| 6.3 | 部分平仓支持（remaining_quantity） | 30min | schema.py + position_tracker.py + app.py | 📋 待开始 |
| 6.4 | 去重原子约束（UNIQUE partial index） | 5min | schema.py | 📋 待开始 |
| 6.5 | 持久化 unrealized_pnl | 20min | schema.py + pos_tracker + app + dashboard | 📋 待开始 |
| 6.6 | 其他 P1 快速修复 | 15min | 多文件 | 📋 待开始 |
| 6.7 | 最终验证 + Consensus 更新 | 10min | 测试 + consensus.md | 📋 待开始 |

**当前：Cycle 21 — Step 6.3 部分平仓支持**

**Step 6.3 的详细任务：**
1. `positions` 表新增 `remaining_quantity INTEGER DEFAULT quantity` 字段（schema.py + DB migration）
2. `open_position()` 初始化 `remaining_quantity = quantity`
3. `close_position()` 支持 `partial_quantity` 参数：部分平仓时减少 remaining_quantity 而非全量 close
4. 全量平仓时 remaining_quantity 归零 → status='closed'
5. `web/app.py` API 支持 `partial_quantity` 字段
6. PnL 计算使用 close 的 quantity（部分平仓时）

## Company State
- Mission: 自动驾驶开发期权期货交易系统
- Tech Stack: Python + Flask + SQLite + Bash + launchd
- System: 62 品种期货信号系统 + 商品期权套利引擎
- DB: trading_system.db — 13 张表（含 positions + trades）
- Active ENTRY Signals: 5 futures（SC/PX/LC/AU）+ 1 option（MA Iron Condor）
- Paper Trading: ✅ 持仓追踪引擎 + 原子事务保护 + 合约乘数 PnL
- Pipeline: ✅ 自动运行（launchd 每 30 分钟全量扫描）
- Web Dashboard: ✅ localhost:5100（含持仓看板 + PnL 含乘数 + 期权免责声明）
- Active Positions: 1 open（SC2607 LONG）, 1 closed（已盈利 +10.0→已含乘数）
- Notifications: ✅ macOS 桌面通知
- Revenue: $0
- Users: 1（阿勇）

## Open Questions
- ❓ 期权 PnL 中期是否要引入非线性定价模型（Black-Scholes）？→ 留到 6.2 之后决定
