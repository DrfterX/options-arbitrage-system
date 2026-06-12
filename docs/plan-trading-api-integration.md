# Plan: 实盘交易 API 调研与集成规划

## 目标
完成期权期货交易信号系统的实盘交易 API 接入可行性研究，输出选型报告 + 架构设计 + 成本分析，为下一阶段实盘执行铺路。

## 背景
- 信号系统已稳定运行（N 型检测 + Black-76 期权策略，65 品种扫描）
- 当前所有信号为 WATCH 级别（0.30-0.40 分），需降低阈值或提升信号质量才能产生 ENTRY
- 从"只出信号"到"实盘执行"的关键一跳：需要选型并接入实盘交易 API
- 时间：深夜 01:44 CST，全量扫描时间阻塞，正好做这事儿

## 调研团队
- **research-thompson**: 调研各 API 方案对比（CTP/掘金/TQSdk/XTQuant/vnpy）
- **cto-vogels**: 设计集成架构（风控/订单/仓位管理 + API 封装）
- **cfo-campbell**: 评估成本和单位经济（最少启动资金、月费、手续费估算）

## 拆解步骤

### 步骤 1：API 调研产出（本轮 - 已完成派发）
- 产出：`docs/research/trading-api-comparison.md`
- 输出：详细对比表 + 评分矩阵 + TOP 2 推荐

### 步骤 2：架构设计产出（本轮 - 已完成派发）
- 产出：`docs/research/trading-api-integration-architecture.md`
- 输出：推荐架构 + 目录设计 + 风控哨兵 + 订单状态机 + ADR

### 步骤 3：成本分析产出（本轮 - 已完成派发）
- 产出：`docs/cfo/trading-api-cost-analysis.md`
- 输出：各方案成本对比 + 三个资金场景经济模型 + 最小可行资金量

### 步骤 4：CEO 决策会议（下一周期）
- 召集：ceo-bezos + critic-munger 评审调研结果
- 决策：选哪个 API？预期投入多少资金？
- 产出：`docs/ceo/trading-api-decision.md`

### 步骤 5：实盘模块开发（下下周期开始）
- 根据决策结果开始 coding
- `trading/` 模块 + 风控哨兵实现

## 依赖顺序
步骤 1/2/3 可并行（本周期）
→ 步骤 4（下周期）
→ 步骤 5（下下周期）
