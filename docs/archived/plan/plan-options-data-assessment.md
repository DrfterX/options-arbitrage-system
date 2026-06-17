# Plan: 期权链数据接入评估 + 合约缓存 Bug 修复

## 目标
解决期权扫描在非交易时段 0/59 解析的合约缓存初始化 Bug，并完成期权链数据源评估报告

## 调研结论（已前置完成）

### 根因分析
期权扫描在非交易时段失败的根本原因**不是数据源问题**，而是 `_init_contract_cache()` 的一个副作用 Bug：

```
if resolved > 0 and resolved % 5 == 0:
    time.sleep(1.0)
```

`resolved` 初始为 0 → `resolved > 0` 永远不成立 → **295 次背靠背 API 调用无节流** → Sina 限流 → 全空 → 0/59 → `get_top40_futures()` 返回空 → "无期货行情数据，跳过期权扫描"

### 实测验证
- `futures_zh_minute_sina(RB2609, "15")` ✅ 非交易时段正常返回数据
- `option_commodity_contract_table_sina(螺纹钢期权, RB2609)` ✅ 返回 19 行数据
- **API 本身正常，是我们调用方式有问题**

### 第二问题：SQLite 并发冲突
`data_refresh()` 过程中出现大量 `unable to open database file` 错误（61MB WAL 模式下的连接竞争）。这会在后续修复后影响全量扫描。

## 拆解步骤

### 步骤 1：修复 _init_contract_cache() （本周期）
- 切换节流条件：基于调用次数而非 resolved 计数
- 将并发线程池用于 cache 初始化（替代串行 295 次）
- 设置合理的品种级别节流间隔

### 步骤 2：写入期权链数据源评估报告 （本周期）
- 回答 Next Action 的 4 个具体问题
- 包含实测数据和备选方向评估

### 步骤 3：修复 SQLite 并发冲突 （下一周期）
- 评估 db.py 连接工厂是否存在连接泄漏
- 考虑连接池或顺序执行策略

## 依赖顺序
步骤 1 → 步骤 2（报告包含修复效果可并行）
步骤 3 独立，可后续处理