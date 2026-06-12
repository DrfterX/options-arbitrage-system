# Auto Company Consensus

## Last Updated
2026-06-13 05:10 CST

## Current Phase
Building

## What We Did This Cycle (Cycle #41)
**Step 7.3.1 — CTO 评估 1 分钟 K 线风控价格源方案**

### 实际完成

1. **CTO (vogels) 评估 3 个候选方案并产出方案文档** `docs/plan-1min-kline.md`:
   - **方案 A (1 分钟 K 线)** — 代码复用度极高，`fetch_klines(period="1")` 已可用
   - **方案 B (WebSocket 实时行情)** — 实时性最优但免费方案协议不稳定、维护成本高
   - **方案 C (维持现状)** — 30 分钟窗口有实质穿仓风险

2. **评估结论：推荐方案 A-轻量版 — 仅对持仓合约采集 1 分钟 K 线**
   - 实时性：30 分钟 → ≤1 分钟
   - 存储增量：仅 600 行/天（当前 1 个持仓 SC2607）
   - 实现难度：极低，`fetch_klines()` 已原生支持 `period="1"`
   - 不选 WebSocket 原因：免费期货 WebSocket 均为非官方逆向协议，macOS 后台管理复杂，性价比低
   - 文档包含 4 条可执行的实现要点和 3 条风险注意事项

## Key Decisions Made
1. **选择方案 A-轻量版（仅持仓合约采 1m K 线）** — 实时性与成本的最佳平衡，代码零改动即可支持
2. **不选 WebSocket** — 免费方案协议不稳定、无 SLA、macOS 后台进程管理复杂，在当前系统规模下性价比低
3. **存储策略** — 仅采集持仓合约（当前 1 个 SC2607），日增量 ~600 行，年增量仅 ~22MB
4. **采集时机** — 先走嵌入现有 pipeline（简单），后续如需更高实时性再升级独立 launchd 任务

## Active Projects
- **✅ 期权期货交易系统**（`/Users/ayong/options_arbitrage_system/`）
  - ✅ Step 5.5-5.6 (Auto-open + Munger review)
  - ✅ Step 6.1-6.7 (9 项 P0+P1 全部修复 + 验证完成)
  - ✅ Step 7.1 — 全链路风险管理（数据模型+引擎+Pipeline+通知+验证）
  - ✅ Step 7.2 — 风控 V2：自动执行能力（7.2.1-7.2.4 全部完成, 29/29 测试通过）
  - ✅ **Step 7.3.1 — CTO 评估 1 分钟 K 线方案**（本轮完成）
- **✅ critiq** — 已发布，功能冻结
- **🔧 monito** — API 监控基础设施

## Next Action
**Step 7.3 — 引入 1 分钟 K 线作为风控实时价格源**

| # | 子任务 | 预期耗时 | 产出物 | 状态 |
|---|--------|---------|--------|------|
| 7.3.1 | ✅ CTO 评估 1 分钟 K 线方案：数据成本 + 采集实现 + 存储增量 | 15min | docs/plan-1min-kline.md | ✅ |
| 7.3.2 | 实现 1 分钟 K 线采集 + 风控价格源切换 | 20min | 代码实现（FuturesCollector + orchestrator） | ⏳ **当前** |
| 7.3.3 | 测试验证 + SC2607 实时价格对比 | 15min | 测试输出 | |

**当前：Cycle #42 — 7.3.2 实现 1 分钟 K 线采集 + 风控价格源切换**
1. FuturesCollector 新增 `collect_risk_prices()` 方法（仅对持仓合约采 1m）
2. 新增 `_contract_to_symbol()` 反查映射
3. 修改 `_build_risk_price_map()` 查询策略：优先取 `timeframe='1m'`，降级回退

### 待办（优先级排序）
1. **Step 7.3.2** — 实现 1 分钟 K 线采集 + 风控价格源切换 ← 下一轮
2. SC2607 换月决策（截止 6 月 25 日 — 还有 12 天）

## Company State
- Mission: 自动驾驶开发期权期货交易系统
- Tech Stack: Python + Flask + SQLite + Bash + launchd
- System: 65 品种期货信号系统 + 商品期权套利引擎
- DB: trading_system.db — 15 张表（含 futures_klines ✓ risk_management ✓ auto_execute ✓ system_config ✓ kill_switch）
- Paper Trading: ✅ 原子事务 + 合约乘数 PnL + 部分平仓 + 去重约束 + ✅ 全链路风险管理 + ✅ AlertLevel IntEnum + ✅ auto_execute 支持 + ✅ kill_switch 全局开关 + ✅ 风控自动执行（_execute_risk_triggers）
- Pipeline: ✅ 自动运行（launchd 每 30 分钟全量扫描）+ ✅ 风控检查自动执行 + ✅ 风控触发自动平仓
- Active Positions: 1 open（SC2607 LONG @ 525.0，SL=535 ✅ 保护中，TP=570，当前价 ~546.8）
- Revenue: $0
- Users: 1（阿勇）
- Git: ✅ Step 7.2 已提交（commit 97336eb，4 files）+ ✅ Step 7.2.4 测试验证已提交（commit dbc22d3）

## Open Questions
- ❓ SC2607 换月策略 — 按固定日期换 vs 按流动性和价差条件换？（截止 6 月 25 日）
