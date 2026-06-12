# Rollover 换月实现文档

## 概述

实现 `PositionTracker.rollover_position()` 方法，支持原子换月操作：在同一 SQLite 事务中关闭旧持仓合约（SC2607）并开立新合约（SC2608）持仓。

## 方法签名

```python
def rollover_position(
    self,
    old_position_id: int,
    new_symbol: str,
    new_contract: str,
    new_entry_price: float,
    close_price: float,
    close_time: int,
) -> Optional[int]
```

## 原子事务流程

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 旧仓 status='closed' | 设 SC2607 为 closed，记录 current_price |
| 2 | 旧仓 trade 流水 | INSERT reason='rollover'，计算实际 PnL |
| 3 | 新建仓 INSERT | 同方向/同数量 SC2608，无 SL/TP（继承到风控表） |
| 4 | 新仓 trade 流水 | INSERT action='open', reason='rollover' |
| 5 | 新仓风控记录 | 创建 risk_management 行，继承偏移后参数 |
| 6 | 旧仓风控锁定 | auto_execute=0 + execute_at 防重入 |

## 风控参数继承策略

使用 **绝对值点数偏移**（point offset）方法：

```
offset = old_parameter - old_entry_price
new_parameter = new_entry_price + offset
```

### SC2607 → SC2608 换月参数示例

| 参数 | SC2607 值 | Entry=525 | 偏移量 | SC2608 Entry=550.9 |
|------|-----------|-----------|--------|-------------------|
| SL | 535.0 | +10.0 | 同偏移 | 560.9 |
| TP | 570.0 | +45.0 | 同偏移 | 595.9 |
| TS Activation | 552.0 | +27.0 | 同偏移 | 577.9 |
| Trail Distance | 10.0 | — | 同值 | 10.0 |

## PnL 计算

SC2607 平仓盈亏（基于合约乘数 1000）：
```
PnL = (close_price - entry_price) × quantity × multiplier
    = (546.8 - 525.0) × 1 × 1000
    = ¥21,800（浮盈已锁定）
```

## Contango 影响

SC2608 入场价 (550.9) 比 SC2607 平仓价 (546.8) 高 4.1 点，
换月成本 = 4.1 × 1000 = ¥4,100/手，已从浮盈中扣除。

## 调用方式

```python
tracker = PositionTracker(db)
new_pos_id = tracker.rollover_position(
    old_position_id=2,      # SC2607 持仓 ID
    new_symbol="SC",
    new_contract="SC2608",
    new_entry_price=550.9,  # SC2608 最新价
    close_price=546.8,      # SC2607 最新价（平仓价）
    close_time=int(time.time()),
)
```

## 风险

- **失败回滚**：任何步骤失败时全量回滚，不会出现半换月状态
- **去重保护**：新合约已有 open 持仓时拒绝执行
- **防重入**：旧仓风控 auto_execute=0，防止换月后被再次操作
