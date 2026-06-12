# Auto Company Consensus

## Last Updated
2026-06-13 02:57 CST

## Project Owner & Strategic Direction

**当前运行者：阿勇**（非原作者 MaxMiksa，原始框架已 fork 自用）
**核心使命：自动驾驶开发「期权期货交易系统」**

### 优先级铁律（不可违反）
1. **期权期货交易系统（`~/options_arbitrage_system/`）** — 最高优先级，Auto Company 全体 Agent 的首要任务
2. **critiq（代码审查 CLI）** — 已发布，保留为通用开发工具，无新功能开发
3. **monito（API 监控）** — 保留，但重新定位为期权系统的**基础设施监控层**，非独立产品
4. **任何新想法** — 必须先回答「这个想法对期权期货系统有什么直接帮助？」。不能创造新的独立产品。
5. **snapog（OG 图生成）** — ❌ **永久停止开发。** 仅保留代码存档，不作为活跃项目维护。

## What We Did This Cycle (Cycle #21)

**Step 6.3 — 部分平仓支持（P0 #3 Munger 致命缺陷）**

### 具体产出
1. **`core/schema.py`** — `positions` 表新增 `remaining_quantity INTEGER DEFAULT 0` 列

2. **`core/position_tracker.py`** — 完整部分平仓逻辑：
   - `_ensure_migration()` — 自动检测并执行 ALTER TABLE + 初始化已有持仓的 `remaining_quantity = quantity`
   - `open_position()` — INSERT 时写入 `remaining_quantity = quantity`
   - `close_position(partial_quantity=...)` — 新增参数：
     - `None` 或 `>= remaining_quantity` → 全量平仓（status='closed', remaining_quantity=0）
     - `< remaining_quantity` → 部分平仓（减少 remaining_quantity，保持 status='open'）
     - PnL 按实际平仓手数计算
   - `update_pnl()` / `get_open_positions()` — 浮动盈亏使用 `remaining_quantity`

3. **`web/app.py`** — `/api/positions/close` API 接受 `partial_quantity` 字段

4. **`web/templates/dashboard.html`** — 持仓卡片数量显示改为 `剩余/总量 手` 格式

## Key Decisions Made
1. **`remaining_quantity = 0` 而非 NULL**：避免 NULL 判断，已平仓设 0
2. **部分平仓不开放重新建仓**：`remaining_quantity > 0` 但 `status='open'`，同合约+方向去重检查仍在
3. **原子事务保护延续**：部分平仓的 UPDATE + _record_trade 仍在同一 try/except + 单 commit

## Active Projects
- **✅ 期权期货交易系统**（`/Users/ayong/options_arbitrage_system/`）— **最高优先级**
  - ✅ Pipeline 自动运行（launchd 每 30 分钟全量扫描）
  - ✅ 6 个活跃 ENTRY 信号
  - ✅ macOS 桌面通知已上线
  - ✅ Dashboard 信号矩阵 + IV 图表 + 回测 + 健康面板
  - ✅ Step 5.5: Auto-open paper trading for ENTRY signals
  - ✅ Step 5.6: Munger review completed
  - ✅ Step 6.1: 原子事务修复完成（P0 #1）
  - ✅ Step 6.2: 期权 PnL 修复完成（P0 #2）
  - ✅ **Step 6.3: 部分平仓支持完成（P0 #3）**
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
| 6.3 | 部分平仓支持（remaining_quantity） | 30min | schema.py + position_tracker.py + app.py + dashboard | ✅ 完成 |
| 6.4 | 去重原子约束（UNIQUE partial index） | 5min | schema.py | 📋 待开始 |
| 6.5 | 持久化 unrealized_pnl | 20min | schema.py + pos_tracker + app + dashboard | 📋 待开始 |
| 6.6 | 其他 P1 快速修复 | 15min | 多文件 | 📋 待开始 |
| 6.7 | 最终验证 + Consensus 更新 | 10min | 测试 + consensus.md | 📋 待开始 |

**当前：Cycle 22 — Step 6.4 去重原子约束**

**Step 6.4 的详细任务：**
1. `schema.py` — positions 表增加 UNIQUE partial index：
   `CREATE UNIQUE INDEX IF NOT EXISTS idx_positions_open_uniq ON positions(contract, direction) WHERE status='open'`
2. 现有 `_find_open_position()` 防御性检查保留
3. 验证：INSERT 同一合约方向 open 持仓应报 `sqlite3.IntegrityError`

## Company State
- Mission: 自动驾驶开发期权期货交易系统
- Tech Stack: Python + Flask + SQLite + Bash + launchd
- System: 62 品种期货信号系统 + 商品期权套利引擎
- DB: trading_system.db — 13 张表（含 positions + trades + remaining_quantity）
- Active ENTRY Signals: 5 futures（SC/PX/LC/AU）+ 1 option（MA Iron Condor）
- Paper Trading: ✅ 持仓追踪引擎 + 原子事务保护 + 合约乘数 PnL + 部分平仓
- Pipeline: ✅ 自动运行（launchd 每 30 分钟全量扫描）
- Web Dashboard: ✅ localhost:5100（含持仓看板 + 部分平仓显示）
- Active Positions: 1 open（SC2607 LONG, remaining=1）
- Notifications: ✅ macOS 桌面通知
- Revenue: $0
- Users: 1（阿勇）

## Open Questions
- ❓ 期权 PnL 中期是否要引入非线性定价模型（Black-Scholes）？→ 留到 Step 6 所有 P0/P1 修复完成后评估
