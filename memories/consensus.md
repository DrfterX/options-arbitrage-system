# Auto Company Consensus

## Last Updated
2026-06-13 04:01 CST

## Project Owner & Strategic Direction

**当前运行者：阿勇**
**核心使命：自动驾驶开发「期权期货交易系统」**

### 优先级铁律（不可违反）
1. **期权期货交易系统（`~/options_arbitrage_system/`）** — 最高优先级
2. **critiq（代码审查 CLI）** — 已发布，功能冻结
3. **monito（API 监控）** — 期权系统的基础设施监控层
4. 新想法必须先回答「对期权期货系统有什么直接帮助？」
5. **snapog** — ❌ 永久停止开发

## What We Did This Cycle (Cycle #30)
**Step 7.1.2 — 风控引擎核心实现 ✅**

### 实际完成
1. **`core/risk_manager.py`** — 完整的 PositionRiskManager 类（18278 bytes）：
   - `RiskCheckTriggerResult` 数据类 + `is_triggered()` / `to_dict()` 方法
   - `check_position(position_id, current_price)` — 单持仓检查（按优先级 SL > TP > Trailing）
   - `check_all_positions(price_map)` — 批量检查所有 open 持仓
   - `_evaluate_triggers()` — 三种触发模式纯计算函数（LONG/SHORT 双向支持）
   - `_escalate_alert()` — 告警升级：info(≥1次) → warning(≥3次) → critical(≥5次)
   - `_update_risk_record()` — 持久化检查时间/价格/告警状态
2. **验证**：8 项功能测试全部通过
3. **提交**：7dfd2b6 — 含 Step 7.1.1（schema/position_tracker）+ Step 7.1.2（risk_manager.py）完整提交

## Key Decisions Made
1. **`core/__init__.py` 已导出** PositionRiskManager 和 RiskCheckTriggerResult，其他模块可直接 `from core.risk_manager import ...`
2. **PositionRiskManager 只做检查** — 与 PositionTracker 职责分离（检查 vs 执行）
3. **无触发时重置告警** — 连续触发才升级，正常恢复后归零，避免积累假告警
4. **移动止损 trail** — 用 last_check_price 追踪极值，激活后价格突破 trail_distance 才触发

## Active Projects
- **✅ 期权期货交易系统**（`/Users/ayong/options_arbitrage_system/`）
  - ✅ Pipeline 自动运行（launchd 每 30 分钟全量扫描）
  - ✅ Step 5.5-5.6 (Auto-open + Munger review)
  - ✅ Step 6.1-6.7 (9 项 P0+P1 全部修复 + 验证完成)
  - ✅ **Step 7.1.1 — 风控数据模型（DDL + 代码）**
  - ✅ **Step 7.1.2 — 风控引擎核心（PositionRiskManager）**
  - ⏳ **Step 7.1.3 — Pipeline 接入风控检查（下一轮）**
- **✅ critiq** — 已发布，功能冻结
- **🔧 monito** — API 监控基础设施

## Next Action
**Step 7.1 — 自动化风险管理（共 6 个子任务）**

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 7.1.1 ✅ | 设计风控模块数据模型（risk_management 表） | 15min | DDL + 代码 |
| 7.1.2 ✅ | 风控引擎核心：SL/TP 检查、追保通知 | 20min | risk_manager.py |
| 7.1.3 | **Pipeline 接入风控检查步骤** | **15min** | **orchestrator.py 修改** |
| 7.1.4 | 风控通知格式升级 | 10min | notification.py 修改 |
| 7.1.5 | 验证：模拟 SC2607 SL/TP 触发 | 10min | 测试 |
| 7.1.6 | 共识更新 + 桌面通知验证 | 10min | consensus.md |

**当前：Cycle 31 — Step 7.1.3 Pipeline 接入风控检查**
修改 `pipeline/orchestrator.py`：
- 在 `run_all()` / `run_futures_scan()` 的适当位置调用 `PositionRiskManager.check_all_positions(price_map)`
- 获取期货最新价作为 price_map 输入
- 触发时记录日志 + 调用 notify 模块发送告警
- 不在此步骤实现自动平仓（V2）

## Company State
- Mission: 自动驾驶开发期权期货交易系统
- Tech Stack: Python + Flask + SQLite + Bash + launchd
- System: 65 品种期货信号系统 + 商品期权套利引擎
- DB: trading_system.db — 14 张表（含 risk_management）
- Paper Trading: ✅ 原子事务 + 合约乘数 PnL + 部分平仓 + 去重约束 + **风控数据模型 + 风控引擎**
- Pipeline: ✅ 自动运行（launchd 每 30 分钟全量扫描）
- Active Positions: 1 open（SC2607 LONG @ 525.0，SL=0 TP=0 ⚠️ 待风控引擎保护）
- Revenue: $0
- Users: 1（阿勇）

## Open Questions
- ❓ 风控引擎发现触发时，自动平仓还是只发送告警？→ 先用告警模式，V2 加自动执行
- ❓ trailing_stop 初始参数在哪配置？→ 先代码配置，后续加 web 界面