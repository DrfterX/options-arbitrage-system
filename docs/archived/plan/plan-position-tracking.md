# Plan: ENTRY 信号持仓追踪系统（Paper Trading）

## 目标
为期货 ENTRY 信号和期权 ENTRY 信号建立持仓追踪系统，自动记录建仓信号、追踪盈亏、展示 Dashboard 看板。

## 背景
- 系统当前有 6 个 ENTRY 信号（5 期货 + 1 期权），但无法追踪「是否建仓」「当前盈亏」「是否止损/止盈」
- 用户需要知道「系统推荐做什么」和「实际持仓表现如何」

## 拆解步骤

### Step 1 — 数据模型与数据库迁移（1 Cycle）
**产出物：** `core/position_tracker.py` + DB schema 更新
- 新增 `positions` 表：symbol, contract, direction, entry_price, entry_time, quantity, status (open/closed), signal_id
- 新增 `trades` 表：position_id, action (open/close), price, time, reason, pnl
- 用 SQLite migration 方式添加（CREATE TABLE IF NOT EXISTS）

### Step 2 — 核心模块：PositionTracker（1 Cycle）
**产出物：** `core/position_tracker.py` 完整实现
- `open_position(signal_id, ...)` — 根据 ENTRY 信号创建持仓
- `close_position(position_id, price, reason)` — 平仓
- `get_open_positions()` — 获取所有持仓
- `get_closed_positions()` — 历史平仓
- `update_pnl()` — 用最新行情更新浮动盈亏

### Step 3 — API 端点（1 Cycle）
**产出物：** `web/app.py` 新增 API
- `GET /api/positions` — 当前持仓列表
- `GET /api/positions/history` — 历史平仓
- `POST /api/positions/open` — 手动建仓（从信号创建）
- `POST /api/positions/close` — 平仓
- `GET /api/positions/stats` — 胜率/总盈亏统计

### Step 4 — Dashboard 持仓看板（1 Cycle）
**产出物：** `web/templates/dashboard.html` 更新
- 「当前持仓」卡片：symbol, direction, entry_price, current_price, pnl%, duration
- 「历史平仓」表格：symbol, direction, entry/exit price, pnl, win/loss
- 「交易统计」卡片：胜率、总盈亏、最大回撤、Sharpe（简化版）

### Step 5 — 自动建仓集成（1 Cycle）
**产出物：** `pipeline/orchestrator.py` 更新
- 扫描完成后，自动对新 ENTRY 信号创建 paper trading 持仓
- ENTRY 信号消失 → 自动平仓
- 避免重复建仓（按 signal_id 去重）

### Step 6 — Critic Review（1 Cycle）
**产出物：** `docs/critic/position-tracking-review.md`
- Munger 审查：数据准确性、回测合理性、误报处理
- 修正后合并

## 依赖顺序
Step 1 → Step 2 → Step 3 → Step 4
                ↓
             Step 5 (可并行于 Step 3/4)
             
Step 6 最后做

## 技术方案
- **数据库：** SQLite，新表 `positions` + `trades`
- **后端：** Python `core/position_tracker.py`，使用已有 `Database` 类
- **API：** Flask blueprint 或直接在 `app.py` 添加路由
- **前端：** 服务端渲染（Jinja2），复用当前 Dashboard 样式
- **数据流：** ENTRY 信号 → PositionTracker → DB → API → Dashboard

## 风险
1. **重复信号问题：** 同一品种可能连续多个周期出 ENTRY，需按 contract+方向去重
2. **价格获取：** 浮动盈亏需要实时价格，当前只有扫描时的价格。方案：用最后一次扫描价近似
3. **假突破：** 15m 级别信号可能很快反转，持仓几小时后可能巨亏。方案：paper trading 允许人工操作
