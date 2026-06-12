# SC2608 合约代码验证报告

> 任务: Step 8.2.1 — 验证 SC2608 合约代码在系统中正确生成
> 验证人: fullstack-dhh
> 日期: 2026-06-13

## 验证结果：✅ 通过

| 检查项 | 结果 | 备注 |
|--------|------|------|
| 合约代码格式 | ✅ 通过 | `SC2608` — symbol(SC) + 年(26) + 月(08) |
| AKShare 数据可获取 | ✅ 通过 | 1d/1h/15m/1m 均有数据 |
| 数据库写入 | ✅ 通过 | 已写入 `futures_klines` 表 |
| 风控系统兼容 | ✅ 通过 | `PositionTracker` / `PositionRiskManager` 按 `contract` 字段查询，无硬编码 |
| 合约乘数 | ✅ 通过 | SC 品种在 `ContractRegistry` 中乘数 = 1,000 |
| 去重约束 | ✅ 通过 | `UNIQUE(symbol, contract, timeframe, timestamp)` 确保无重复 |

## 数据采集确认

执行 `collect_symbol('SC', 'SC2608', ...)` 后，各周期数据量：

| 周期 | K 线数量 | 最早时间 | 最晚时间 | 最新收盘价 |
|------|---------|---------|---------|-----------|
| 1m | 1,023 | 2026-06-11 | 2026-06-14 | ~569.0 |
| 15m | 1,023 | 2026-05-06 | 2026-06-14 | ~569.0 |
| 1h | 1,023 | 2026-01-07 | 2026-06-14 | ~569.0 |
| 1d | 1,992 | 2018-03-25 | 2026-06-11 | ~553.5 |
| 3m | 348 | 2026-06-11 | 2026-06-12 | ~569.0 |

## SC2607 vs SC2608 价格对比

| 指标 | SC2607 | SC2608 |
|------|--------|--------|
| 最新 1m 收盘价 | ~564.9 | ~569.0 |
| 价差 (SC2608 - SC2607) | — | **+4.1** |
| 期限结构 | — | **Contango (远期升水)** |

> ⚠️ Contango 影响: 当前 SC2608 比 SC2607 高约 4.1 点，换月成本约 ¥4,100/手。
> 对比当前浮盈 ¥23,000，占浮盈约 17.8%。

## 技术验证详情

### 1. 合约代码格式
```
SC2608 = SC (品种) + 26 (年份) + 08 (月份)
```
格式与 SC2607 完全一致，系统所有查询都使用 `contract` 字段字符串匹配，无硬编码检查。

### 2. AKShare 可获取性
```python
fetch_klines('SC', 'SC2608', '1')  → 1,023 条 1m K线 ✅
fetch_klines('SC', 'SC2608', '15') → 1,023 条 15m K线 ✅
fetch_klines('SC', 'SC2608', '60') → 1,023 条 1h K线 ✅
fetch_klines('SC', 'SC2608', 'D')  → 1,992 条 1d K线 ✅
```

### 3. 数据库兼容性
- `futures_klines` 表: 使用 `symbol` + `contract` + `timeframe` + `timestamp` 四元组 UNIQUE 约束
- `positions` 表: 使用 `contract` 字段存储合约代码
- `risk_management` 表: 通过 `position_id` 关联持仓，间接使用合约代码
- 所有风控逻辑 (`PositionRiskManager`) 通过 `position_id` 查询，不依赖合约名称

### 4. 合约乘数
```python
ContractRegistry.get_multiplier('SC') → 1,000  # 正确
```

## 系统影响评估

| 影响面 | 风险 | 说明 |
|--------|------|------|
| 数据采集 | ✅ 无 | `collect_all()` 自动获取主力合约；SC2608 可通过 `collect_symbol()` 显式采集 |
| 持仓管理 | ✅ 无 | `open_position()` / `close_position()` 按 `contract` 字段操作 |
| 风控检查 | ✅ 无 | `check_all_positions()` 使用 `price_map[contract]` 获取价格 |
| PnL 计算 | ✅ 无 | `_calculate_pnl()` 使用 `symbol → multiplier` 映射，SC 品种乘数 1,000 |
| 信号系统 | ✅ 无 | 信号 pipeline 使用 `symbol` 和 `contract` 字段 |

## 结论

SC2608 合约代码在系统中完全兼容：
1. ✅ 合约代码格式正确 — 可直接用于建仓、平仓、风控
2. ✅ AKShare 数据可用 — 1m/15m/1h/1d 均能正常采集
3. ✅ 数据库约束兼容 — 无唯一性/外键冲突
4. ✅ 风控系统兼容 — 无需修改任何代码
5. ✅ 合约乘数正确 — 1,000 桶/手

**下一步建议：** 实现完整换月逻辑（平 SC2607 → 开 SC2608 原子事务）
