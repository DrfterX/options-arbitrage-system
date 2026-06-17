# Plan: Step 6 — Fix P0 Issues from Munger Review

## 目标
修复 Paper Trading 持仓追踪系统的 3 个 P0 致命缺陷，达到可上线标准。

## 背景
Munger 审查（critic-munger, Cycle #16）发现 Step 5 完整实现中存在 3 个 P0 数据完整性问题：

| P0 | 问题 | 影响 |
|----|------|------|
| #1 | 开/平仓非原子事务 | Crash 后产生无法修复的孤儿数据 |
| #2 | 期权持仓使用期货价格而非净权利金 | 期权 PnL 完全错误 |
| #3 | 不支持部分平仓 | 真实交易分批操作无法处理 |

## 拆解步骤

| # | 子任务 | 预期耗时 | 产出物 | 范围 |
|---|--------|---------|--------|------|
| 6.1 | 开/平仓原子事务 | 15min | position_tracker.py | open_position + close_position 改为 try/except + 单 commit |
| 6.2 | 期权 PnL 修复 | 15min | orchestrator.py + position_tracker.py | 期权入场价用 strategy_details.net_cost，短期标注免责 |
| 6.3 | 部分平仓支持 | 30min | schema.py + position_tracker.py + web/app.py | remaining_quantity 字段 + partial close API |
| 6.4 | 去重原子约束 (UNIQUE partial index) | 5min | schema.py | 增加 `WHERE status='open'` 唯一索引 |
| 6.5 | 持久化 unrealized_pnl | 20min | schema.py + position_tracker.py + web/app.py + dashboard.html | 表字段 + API 返回 + 前端纯展示 |
| 6.6 | 其他 P1 快速修复 | 15min | 多文件 | signal_id NULL, net_delta, entry_price=0 日志 |
| 6.7 | 最终验证 + Consensus 更新 | 10min | consensus.md | 运行验证，确认所有修复生效 |

## 依赖顺序
- 6.1 → 6.3（在修改 close_position 前需要原子事务基础）
- 6.2 → 独立
- 6.3 → 6.5（remaining_quantity 影响 PnL 展示）
- 6.4 → 独立
- 6.5 → 6.6（先修 P0 再修 P1）
- 6.7 → 所有

## 设计决策
1. **P0 #1（原子事务）**：使用 try/except/rollback 模式，内部 `_record_trade` 不独立 commit
2. **P0 #2（期权 PnL）**：短期方案 — 从 `strategy_details.net_cost` 获取净权利金，Dashboard 标注"期权 PnL 为净值（不含合约乘数）"
3. **P0 #3（部分平仓）**：`positions` 表加 `remaining_quantity INTEGER DEFAULT quantity`，`close_position(partial_quantity=...)` 逻辑
