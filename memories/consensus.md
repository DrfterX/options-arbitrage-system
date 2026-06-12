# Auto Company Consensus

## Last Updated
2026-06-13 12:00 CST

## Project Owner & Strategic Direction

**当前运行者：阿勇**（非原作者 MaxMiksa，原始框架已 fork 自用）
**核心使命：自动驾驶开发「期权期货交易系统」**

### 优先级铁律（不可违反）
1. **期权期货交易系统（`~/options_arbitrage_system/`）** — 最高优先级，Auto Company 全体 Agent 的首要任务
2. **critiq（代码审查 CLI）** — 已发布，保留为通用开发工具，无新功能开发
3. **monito（API 监控）** — 保留，但重新定位为期权系统的**基础设施监控层**，非独立产品
4. **任何新想法** — 必须先回答「这个想法对期权期货系统有什么直接帮助？」。不能创造新的独立产品。
5. **snapog（OG 图生成）** — ❌ **永久停止开发。** 仅保留代码存档，不作为活跃项目维护。

## What We Did This Cycle (Cycle #22)

**修复 Step 6.4 — 去重原子约束（UNIQUE partial index）**

### 具体产出
1. **`core/schema.py`** — `INDEXES` 列表新增 UNIQUE partial index：
   ```sql
   CREATE UNIQUE INDEX IF NOT EXISTS idx_positions_open_uniq
   ON positions(contract, direction) WHERE status='open'
   ```
2. **双重保障**：Python `_find_open_position()` 防御性检查 + 数据库级 UNIQUE 约束
3. **影响**：同一合约+方向的重复 open 持仓在 SQL 层直接拒绝，`sqlite3.IntegrityError`

### 实际完成状态（共识修正）

**注意：** 共识文件曾严重滞后。以下为从 git log 恢复的实际完成情况：

| Cycle | 实际完成 | Commit |
|-------|---------|--------|
| #19 | Step 6.1 — 原子事务修复（P0 #1） | `b42c701` |
| #20 | Step 6.2 — 期权 PnL 修复（P0 #2） | `46857df` |
| #21 | Step 6.3 — 部分平仓支持（P0 #3） | `c93ad2f` |
| #22 | **Step 6.4 — 去重原子约束** | `b82b4a1` |

## Key Decisions Made
1. **数据库级约束 + 应用层检查双重保障**：即使 Python 层的 `_find_open_position()` 因并发或 bug 未拦截，SQLite 强制执行唯一性
2. **partial index 精确定位**：仅对 `status='open'` 的行施加唯一约束，已平仓持仓可以有相同合约+方向

## Active Projects
- **✅ 期权期货交易系统**（`/Users/ayong/options_arbitrage_system/`）— **最高优先级**
  - ✅ Pipeline 自动运行（launchd 每 30 分钟全量扫描）
  - ✅ Step 5.5: Auto-open paper trading for ENTRY signals
  - ✅ Step 5.6: Munger review completed
  - ✅ Step 6.1: 原子事务修复完成（P0 #1）
  - ✅ Step 6.2: 期权 PnL 修复完成（P0 #2）
  - ✅ Step 6.3: 部分平仓支持完成（P0 #3）
  - ✅ **Step 6.4: 去重原子约束完成**
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
| 6.4 | 去重原子约束（UNIQUE partial index） | 5min | schema.py | ✅ 完成 |
| 6.5 | 持久化 unrealized_pnl | 20min | schema.py + pos_tracker + app + dashboard | 📋 待开始 |
| 6.6 | 其他 P1 快速修复 | 15min | 多文件 | 📋 待开始 |
| 6.7 | 最终验证 + Consensus 更新 | 10min | 测试 + consensus.md | 📋 待开始 |

**当前：Cycle 23 — Step 6.5 持久化 unrealized_pnl**

**Step 6.5 的详细任务：**
1. `schema.py` — `positions` 表新增 `unrealized_pnl REAL DEFAULT 0` 列
2. `position_tracker.py` — `update_pnl()` 在更新 `current_price` 时同时持久化计算出的 `unrealized_pnl` 到数据库
3. `web/app.py` — `/api/positions` 返回时使用数据库存储的 `unrealized_pnl` 而非实时计算
4. `web/templates/dashboard.html` — 前端使用 `unrealized_pnl` 字段展示

## Company State
- Mission: 自动驾驶开发期权期货交易系统
- Tech Stack: Python + Flask + SQLite + Bash + launchd
- System: 62 品种期货信号系统 + 商品期权套利引擎
- DB: trading_system.db — 13 张表（含 positions + trades + remaining_quantity + UNIQUE partial index）
- Active ENTRY Signals: 5 futures（SC/PX/LC/AU）+ 1 option（MA Iron Condor）
- Paper Trading: ✅ 持仓追踪引擎 + 原子事务保护 + 合约乘数 PnL + 部分平仓 + 去重约束
- Pipeline: ✅ 自动运行（launchd 每 30 分钟全量扫描）
- Web Dashboard: ✅ localhost:5100
- Active Positions: 1 open（SC2607 LONG）
- Notifications: ✅ macOS 桌面通知
- Revenue: $0
- Users: 1（阿勇）

## Open Questions
- ❓ 期权 PnL 中期是否要引入非线性定价模型（Black-Scholes）？→ 留到 Step 6 所有 P0/P1 修复完成后评估