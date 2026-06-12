# Paper Trading 持仓追踪系统 — 逆向审查报告

**审查者：** critic-munger（逆向思考顾问）
**审查日期：** 2026-06-13
**审查范围：** core/position_tracker.py / core/schema.py (positions + trades) / pipeline/orchestrator.py (自动建仓) / web/app.py (POSITIONS API) / web/templates/dashboard.html (持仓看板 JS) / core/db.py

---

## 审查结论

**不通过。** 系统暴露了两个致命数据缺陷和一个设计盲区：

1. **事务非原子性** — 持仓开/平在多步操作中拆分 commit，crash 后产生无法修复的残缺数据
2. **期权 PnL 公式错误** — 使用标的期货价格替代期权权利金，净值数字完全失真
3. **数据模型不支持部分平仓** — 真实交易中分批平仓是常态，当前模型无法处理

以下是完整分析。

---

## 关键风险列表

### [P0] 持仓开/平操作非原子事务 — crash 产生孤儿数据

**问题描述：**
`open_position()` 和 `close_position()` 都分为两个独立事务：

**open_position()：**
1. `INSERT INTO positions` → `conn.commit()`（事务1）
2. `_record_trade('open', ...)` → `conn.commit()`（事务2）

**close_position()：**
1. `UPDATE positions SET status='closed'` → `conn.commit()`（事务1）
2. `_record_trade('close', ...)` → `conn.commit()`（事务2）

**影响范围：**
- 事务 1 成功、事务 2 失败 → position 已标记 closed 但 **平仓流水永久丢失** → 该笔盈亏永远无法计入统计
- `get_stats()` 从 trades 表查询 PnL，但 closed 持仓没有对应流水 → PnL 统计偏离
- 开仓同样：存在无 trade 记录的幽灵持仓，无法审计

**修复建议：**
```python
conn = self.db.get_conn()
try:
    cursor = conn.execute("INSERT INTO positions ...", (...))
    conn.execute("INSERT INTO trades ...", (...))
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

从第一条 INSERT 到最后一次 commit 之间禁止任何独立 commit。

---

### [P0] 期权持仓使用期货价格作为入场价 — PnL 完全错误

**问题描述：**
`orchestrator.py` 第 667 行：
```python
opt_entry_price = sig["futures_price"]  # ← 这是标的期货价格
...
entry_price=opt_entry_price,            # ← 存为持仓入场价
```

然后 `_calculate_pnl()` 用这个期货价格计算线性 PnL：
```
LONG: (当前期货价 − 入场期货价) × 手数
```

但期权策略的盈亏是非线性的，正确入场价应该是**策略净权利金**。

**影响范围：**
- 所有期权持仓的浮动盈亏和已实现盈亏数字都是错误的
- 一个盈利的期权策略可能在系统里显示为亏损，反之亦然
- Dashboard 显示的期权 PnL 对真实交易的参考价值为零
- 此外，即使对于期货，`_calculate_pnl()` 也没有乘以合约乘数 `symbols.multiplier`

**修复建议：**
1. 短期：期权入场价从策略 `strategy_details.net_cost` 获取净权利金
2. 中长期：扩展 positions 表增加 `option_type` / `net_premium` / 策略详情字段，PnL 基于期权定价
3. PnL 公式增加合约乘数因子

---

### [P0] 数据模型不支持部分平仓

**问题描述：**
- `close_position()` 只支持一次性全平：将 `status` 设为 `closed`
- 无 `remaining_quantity` / `closed_quantity` 字段
- 持仓页面上没有"平仓手数"输入项
- `/api/positions/close` API 的请求体中不包含手数

**影响范围：**
- 真实交易中分批平仓（先平 2 手留 3 手）是常规操作
- 强行调用两次 `close_position()` → 第二次被 `status='closed'` 检查拒绝
- 或第一次调用就将所有仓位标记为平仓 → 剩余仓位丢失

**修复建议：**
- `positions` 表增加 `remaining_quantity INTEGER DEFAULT quantity`
- `close_position()` 增加 `partial_quantity` 参数
- 当 `partial_quantity < remaining_quantity` 时，仅减少 `remaining_quantity`，不改变 `status`
- 仅当 `remaining_quantity == 0` 时标记 `status = 'closed'`

---

### [P1] 去重逻辑 check-then-insert 非原子

**问题描述：**
```python
dup = self._find_open_position(contract, direction)  # 检查
if dup is not None: return None
# ← 在此处并发窗口
cursor = conn.execute("INSERT INTO positions ...")    # 插入
```

单线程管线下不会触发，但 pipeline 的 cron 配置 (`*/30 * * * *`) 在极端情况下可能重叠。

**影响范围：**
- 两次 pipeline 同时运行 → 同一合约+方向插入两条未平仓
- 后续 PnL 计算和 Dashboard 展示错乱

**修复建议：**
增加数据库层约束：
```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_positions_active_unique
    ON positions(contract, direction) WHERE status='open'
```
SQLite 3.30.0+ 支持部分索引。

---

### [P1] `signal_id INTEGER DEFAULT 0` 导致查询歧义

**问题描述：**
- `signal_id` 默认值 0 不是合法的信号 ID（AUTOINCREMENT 从 1 开始）
- 无 `FOREIGN KEY` 约束，可以引用不存在的信号
- `get_position_by_signal(0)` 返回最后一条 `signal_id=0` 的持仓——可能是多头，可能是空头，完全不明确
- 手动建仓 API 调用时 `signal_id` 不传则默认 0，所有手动建仓的 signal_id=0 无法区分

**修复建议：**
- 默认值改为 `NULL`
- 增加 `FOREIGN KEY (signal_id) REFERENCES futures_signals(id)` 约束（options 信号无法约束，需另做处理）
- `get_position_by_signal()` 处理 `signal_id IS NULL` 的情况

---

### [P1] 浮动盈亏未持久化 — 前端重复计算

**问题描述：**
`update_pnl()` 只存 `current_price`，丢弃 PnL 结果：
```python
pnl = self._calculate_pnl(...)
conn.execute("UPDATE positions SET current_price=?, updated_at=datetime('now') WHERE id=?", ...)
# pnl 变量被丢弃
```

Dashboard JS 完全重算了相同公式：
```javascript
var pnlVal = (p.current_price && p.current_price > 0)
    ? (p.direction === 'LONG' ? p.current_price - p.entry_price : p.entry_price - p.current_price) * (p.quantity || 1)
    : 0;
```

**影响范围：**
- 公式在两端重复定义——改一个不记得改另一个就静默不一致
- `current_price=0` 时 PnL 显示为 0，伪装为盈亏平衡
- API `/api/positions` 响应中不包含 `unrealized_pnl` 字段，调用者必须自行推导

**修复建议：**
- `positions` 表增加 `unrealized_pnl REAL DEFAULT 0`
- `update_pnl()` 将此值写入数据库
- API 返回中包含 `unrealized_pnl`
- 前端仅展示，不计算

---

### [P1] 期权方向映射使用 side 而非 net_delta

**问题描述：**
```python
side = sd.get("side", "")
direction = "LONG" if side == "call" else ("SHORT" if side == "put" else "")
```

Call ratio spread → LONG，Put ratio spread → SHORT。

但比率价差的实际方向：
| 策略 | 典型净 Delta | 实际方向 |
|------|-------------|---------|
| 看涨比率价差 (1:2) | 负（空） | SHORT |
| 看跌比率价差 (1:2) | 正（多） | LONG |

当前映射可能完全相反。`net_delta` 已在策略结果中可用，可以直接使用。

**修复建议：**
```python
direction = "LONG" if sig.get("net_delta", 0) > 0 else "SHORT"
```

---

### [P1] `entry_price = 0` 建仓静默跳过 + 无日志区分

**问题描述：**
```python
if entry_price > 0 and direction in ("LONG", "SHORT"):
    # ...建仓
```

如果 `SignalResult.entry_price` 为 0 或 `None`，跳过但只体现在 debug 日志中，Dashboard 和用户完全不知情。`futures_signals` 表的 `entry_price REAL DEFAULT 0` 意味着如果评分器未正确设置该字段（记录进数据库时默认 0），**所有该品种的 ENTRY 信号都不会被跟踪**且无告警。

**影响范围：**
- 评分器缺失 entry_price 输出 → 静默不建仓
- 运维人员无法从 Dashboard 感知
- 只有查看 application 日志才能发现

**修复建议：**
- 跳过时输出 `logger.warning` 级别日志
- 增加该品种的建仓失败计数，暴露在 Dashboard 上

---

### [P1] `batch_update_pnl` 价格缺失时 PnL 伪装为 0

**问题描述：**
```python
if price is not None:
    pos["unrealized_pnl"] = self.update_pnl(pos["id"], price)
else:
    pos["unrealized_pnl"] = 0.0  # ← 不可知 = 0
```

如果 `price_map` 缺少某合约的行情价格，PnL 显示 0.00，伪装成"盈亏平衡"。用户无法区分"真的持平"和"还没有数据"。

**修复建议：** 返回 `None` 而非 0.0，前端展示为"—"。

---

### [P2] `entry_time` 与 `closed_at` 类型不一致

**问题描述：**

| 字段 | 类型 | 来源 |
|------|------|------|
| `entry_time` | INTEGER (Unix秒) | 外部传入 |
| `closed_at` | TEXT (`datetime('now')`) | SQLite 函数 |
| `opened_at` | TEXT (`datetime('now')`) | DEFAULT 值 |

无法直接用 SQL 计算持仓时长：`closed_at - entry_time` 是类型错误。Dashboard 展示时 `entry_time` 用 JS 解析，`closed_at` 直接作为字符串显示，格式不同。

**修复建议：** 统一时间类型，建议全部改为 INTEGER (Unix秒)。

---

### [P2] Dashboard 与 Backend 的 PnL 公式重复定义

**问题描述：**
前端的 PnL 计算逻辑（dashboard.html 第 573-576 行）是后端 `_calculate_pnl()` 的完整副本。任何一方的修改都需要同步到另一方。

**影响范围：**
- 修改 PnL 逻辑（如加入手续费或合约乘数）需要同时改两个地方
- 修改后可能存在一段时间的静默不匹配

**修复建议：** 由后端计算并通过 API 下发 `unrealized_pnl`，前端纯展示。

---

## 边界场景分析

### 场景 1：多合约同品种
由于去重基于 `contract + direction`，SC2607 LONG 和 SC2608 LONG 可以同时存在——这是正确的。同合约同方向被阻止。

### 场景 2：negative quantity
`_calculate_pnl()` 使用 `(price_diff) × quantity`。如果 quantity = -1，PnL 符号反转。DDL 无 `CHECK(quantity > 0)` 约束。极端情况下外部代码传入负数可导致 PnL 含义颠倒。

### 场景 3：entry_price = 0
Dashboard 第 579 行 `p.entry_price > 0` 防止了 PnL 百分比除零，但绝对 PnL 仍然按 `(current - 0) × 1 = current` 显示。如果 entry_price 真的为 0，那绝对 PnL 显示的是价格本身而非盈亏。

### 场景 4：关闭已平仓或不存在的持仓
`close_position()` 返回 `False`，API 返回 404。但"不存在"和"已平仓"是两个不同的语义，当前共用 404。建议：不存在 → 404，已平仓 → 409。

### 场景 5：pipeline 重叠运行
cron 配置 `*/30 * * * *` 在 `data_refresh()` 耗时较长时（30+ 品种的聚合 + MACD + 极值点 + N型）可能覆盖。虽然当前单线程不会有竞争，但两次 pipeline 实例并发写入同一个 SQLite 时，外键等约束可能因连接不同而失效——因为 `PRAGMA foreign_keys` 是 per-connection 设置。

### 场景 6：5 分钟全页硬刷新
Dashboard 第 264 行 `setTimeout(function() { location.reload(); }, 300000)`。如果用户正在阅读持仓看板，页面会突然重置。打开的 K-line 弹窗丢失。

### 场景 7：期权中性策略从不建仓
`short_strangle` / `iron_condor` 始终被跳过。如果将来某个中性策略信号强度极高（ENTRY），它也不会被 paper trading 覆盖。这不是 bug，但需要明确文档记录此限制。

---

## 改进建议（按优先级）

| 排序 | 优先级 | 内容 | 预估时 |
|------|--------|------|--------|
| 1 | P0 | 开/平仓改为原子事务（一个 conn.commit() 包裹所有操作） | 15min |
| 2 | P0 | 期权持仓使用净权利金而非期货价格作为 entry_price | 15min |
| 3 | P0 | positions 表增加 `remaining_quantity`，支持部分平仓 | 30min |
| 4 | P1 | 增加 `UNIQUE(contract, direction) WHERE status='open'` 唯一索引 | 5min |
| 5 | P1 | 持久化 unrealized_pnl 到 positions 表，前端纯展示 | 20min |
| 6 | P1 | `signal_id` 默认值改为 NULL，增加 FK 约束 | 10min |
| 7 | P1 | 期权方向使用 net_delta 替代 side 映射 | 5min |
| 8 | P1 | `entry_price=0` 跳过时输出 warning 日志 | 5min |
| 9 | P1 | batch_update_pnl 缺失价格时返回 None 而非 0 | 5min |
| 10 | P2 | 统一 `entry_time` / `closed_at` 为 INTEGER (Unix秒) | 10min |
| 11 | P2 | PnL 公式增加合约乘数因子 | 10min |
| 12 | P2 | 关闭不存在的持仓返回 404，已平仓返回 409 | 5min |

---

## 最终建议

这是一个有不错架构骨架但**数据完整性存在致命缺陷**的系统。以下是我的最终裁定：

1. **错误的事务边界**（P0 #1）是绝不可放过的红线——任何数据写入系统如果容忍 crash 后产生不可修复的数据裂痕，就不应该上线。修复成本极低（一行 try/except 包裹两个操作），没有理由不做。

2. **期权 PnL 错误**（P0 #2）意味着整个期权 paper trading 的盈亏展示是虚假的。如果团队决定快速上线，至少要明确标注"期权 PnL 暂不准确"。

3. **无部分平仓**（P0 #3）是设计盲区——分批操作是交易常规，当前模型强行推广到实盘会直接阻断用户流程。

4. 其余 P1 问题是可接受的 tech debt，可以分批次优化。

**建议推进计划：** 修复 #1 → #2 → #3（P0 三件套），然后上线。其余 P1/P2 问题标记为"Known Issues"在后续 cycle 中逐步解决。

> *"我相信有自主神经系统——那些自动处理基本功能的系统。如果你的持仓追踪系统连事务完整性都不能保证，那它就不是在帮你跟踪，而是在帮你创造问题。"* — 经过 Munger 改造
