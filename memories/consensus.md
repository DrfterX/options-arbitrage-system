# Auto Company Consensus

## Last Updated
2026-06-13 02:29 CST

## Project Owner & Strategic Direction

**当前运行者：阿勇**（非原作者 MaxMiksa，原始框架已 fork 自用）
**核心使命：自动驾驶开发「期权期货交易系统」**

### 优先级铁律（不可违反）
1. **期权期货交易系统（`~/options_arbitrage_system/`）** — 最高优先级，Auto Company 全体 Agent 的首要任务
2. **critiq（代码审查 CLI）** — 已发布，保留为通用开发工具，无新功能开发
3. **monito（API 监控）** — 保留，但重新定位为期权系统的**基础设施监控层**，非独立产品
4. **任何新想法** — 必须先回答「这个想法对期权期货系统有什么直接帮助？」。不能创造新的独立产品。
5. **snapog（OG 图生成）** — ❌ **永久停止开发。** 仅保留代码存档，不作为活跃项目维护。

## What We Did This Cycle (Cycle #16)

**实现 Step 5.6 — Critic Review（Munger 审查）**

### 具体产出
1. **`docs/critic/paper_trading_review.md`** — critic-munger 对 Step 5 Paper Trading 持仓追踪系统的完整逆向审查报告
2. 发现 **3 个 P0（致命）缺陷** 和 **6 个 P1（高风险）问题**

### 审查核心发现

**P0 致命缺陷（必须修复后才能视为完成 Paper Trading）：**
1. **事务非原子性** — `open_position()` 和 `close_position()` 拆分两次独立 commit，crash 后产生孤儿数据（trade 丢失 → PnL 统计偏离）
2. **期权 PnL 公式错误** — 使用 `futures_price`（标的期货价格）而非策略净权利金作为入场价，期权盈亏数字完全失真
3. **不支持部分平仓** — 数据模型缺少 `remaining_quantity`，只能全平无法分批

**P1 高风险（可分批修复）：**
4. 去重逻辑 check-then-insert 非原子（缺部分唯一索引）
5. `signal_id DEFAULT 0` 导致查询歧义
6. 浮动盈亏未持久化，前后端公式重复
7. 期权方向使用 `side`（call/put）而非 `net_delta`，映射可能反向
8. `entry_price=0` 跳过建仓时无告警
9. `batch_update_pnl` 缺失价格时 PnL 伪装为 0

### Munger 建议
> 不通过。修复 P0 三件套后上线，P1/P2 标记为 Known Issues 逐步优化。

## Key Decisions Made
1. Step 5.6 审查完成，Munger 判定「不通过」— 需要先修复 P0 缺陷
2. 修复 P0 三件套作为 Step 6，其余 P1/P2 项后续逐步处理
3. 修复顺序：原子事务(15min) → 期权入场价(15min) → 部分平仓(30min)

## Active Projects
- **✅ 期权期货交易系统**（`/Users/ayong/options_arbitrage_system/`）— **最高优先级**
  - ✅ Pipeline 自动运行（launchd 每 30 分钟全量扫描）
  - ✅ 6 个活跃 ENTRY 信号
  - ✅ macOS 桌面通知已上线
  - ✅ Dashboard 信号矩阵 + IV 图表 + 回测 + 健康面板 + 持仓看板
  - ✅ Paper Trading 全套：模型 → API → UI → 自动建仓
  - ✅ Step 5.6 — Munger 审查完成（发现 3 个 P0 缺陷）
  - ❌ Telegram → 降为低优先级，用户自行配置

- **✅ critiq（代码审查 CLI）** — v0.1.1 已发布到 npm，功能冻结

- **🔧 monito（API 监控基础设施）** — 已部署到 CF Workers

- **🗄️ snapog** — 已存档，不维护，不开发

## Next Action
**Step 6 — 修复 Paper Trading P0 缺陷（Munger Review Findings）**（共 3 个 Cycle）

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 6.1 | 原子事务修复 — open_position/close_position 包为单事务 | 15min | position_tracker.py 修改 |
| 6.2 | 期权入场价修复 — 使用 net_cost/权利金而非 futures_price | 15min | orchestrator.py + schema 修改 |
| 6.3 | 部分平仓支持 — positions 表加 remaining_quantity | 30min | 数据模型 + logic + API |

**当前：Cycle 17 — Step 6.1 原子事务修复**

**Step 6.1 的详细任务：**
1. 修改 `core/position_tracker.py` 的 `open_position()`：将 INSERT INTO positions 和 _record_trade('open') 合并到一个 conn.commit() 中
2. 修改 `close_position()`：将 UPDATE positions SET status='closed' 和 _record_trade('close') 合并到一个 conn.commit() 中
3. 两处函数使用 try/except 包裹，异常时执行 conn.rollback()
4. 移除中间多余的 commit() 调用

## Company State
- Mission: 自动驾驶开发期权期货交易系统
- Tech Stack: Python + Flask + SQLite + Bash + launchd
- System: 62 品种期货信号系统 + 商品期权套利引擎
- DB: trading_system.db — 13 张表（含 positions + trades）
- Active ENTRY Signals: 5 futures（SC/PX/LC/AU）+ 1 option（MA Iron Condor）
- Paper Trading: ✅ 持仓追踪引擎 + API + Dashboard + 自动建仓（待修复 3 个 P0 缺陷）
- Pipeline: ✅ 自动运行（launchd 每 30 分钟全量扫描）
- Web Dashboard: ✅ localhost:5100
- Active Positions: 1 open（SC2607 LONG）, 1 closed（已盈利 +10.0）
- Notifications: ✅ macOS 桌面通知
- Revenue: $0
- Users: 1（阿勇）

## Open Questions
- ❓ 期权中性策略（short_strangle / iron_condor）的 paper trading 如何追踪？→ 留到 Step 6.3 讨论
- ❓ 止损/止盈自动触发逻辑何时实现？→ 留到修复 P0 后规划
