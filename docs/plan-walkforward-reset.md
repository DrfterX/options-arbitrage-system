# Walk-Forward 回测：评分重置机制验证

## 目标

验证评分重置机制（_apply_score_reset / _check_structure_invalidation / _check_reverse_n_structure）是否提升信号准确率。

**核心问题：** 在 3 分制下，当 Level1 方向仍有效但价格结构已劣化时，重置评分能否避免虚假信号？

## 设计方案

### 核心思路：时间过滤数据库

不修改 scorer.py 一行代码，通过 **HistoricalDatabase 包装器** 让评估引擎"穿越"到历史时刻：

```
               ┌────────────────────────┐
               │  scorer.evaluate()     │
               │  (无修改, 纯 DB 读取)    │
               └────────┬───────────────┘
                        │ db.get_conn()
               ┌────────▼───────────────┐
               │  HistoricalDatabase    │
               │  · 持有一个 _current_ts │
               │  · 所有查询 WHERE ts<=  │
               └────────┬───────────────┘
                        │ 真实 DB 连接
               ┌────────▼───────────────┐
               │  trading_system.db     │
               └────────────────────────┘
```

### 模块结构

```
futures/scorer_walkforward.py   ← 新文件
├── HistoricalDatabase           # 时间过滤 Database 包装器
│   · 继承 Database 的接口
│   · get_conn() 返回的 connection 所有查询追加 _current_ts 过滤
│   · set_timestamp(ts) 改变当前时间点
│
├── run_scorer_at_timestamp()    # 在某个历史时间点运行 evaluate()
│   · 设置 HistoricalDatabase 的时间
│   · 调用 scorer.evaluate() 获取 SignalResult
│   · 检查后续 N 个交易日的价格走势
│   · 记录: 是否有信号、方向、是否触发了重置
│
├── run_walkforward_with_reset() # Walk-Forward 主入口
│   · 时间序列遍历 + fold 划分
│   · 每个时间点同时跑 with_reset / without_reset
│   · 聚合准确率
│
└── main()                       # CLI 入口
    · --symbol RB
    · --compare  (输出对比结果)
    · --compact (简洁输出)
```

### Walk-Forward 折叠设计

参考 n_backtest.py 的 `run_walkforward()` 模式：

```
Fold 1:  [─── 训练 3年 ───][── 验证 6月 ───]
Fold 2:         [─── 训练 3年 ───][── 验证 6月 ───]
Fold 3:                [─── 训练 3年 ───][── 验证 6月 ───]
...
```

- **训练期**: 不用于参数调优（重置机制无可调参数），仅统计 baseline 准确率
- **验证期**: 在未见数据上评估 with_reset vs without_reset 的准确率差异
- **滑动步长**: 窗口一半（~1.75年）
- **最小训练结构数**: 少于 20 个信号的结构不纳入统计

### 核心指标

| 指标 | 计算方式 | 含义 |
|------|---------|------|
| 信号准确率 | 预测方向正确次数 / 总信号数 | 方向预测质量 |
| 信号密度 | 信号数 / 交易天数 | 交易频率 |
| 平均盈亏比 | 平均盈利幅度 / 平均亏损幅度 | 盈亏质量 |
| 重置触发率 | 触发重置的信号 / 总信号 | 重置活跃度 |
| 重置准确率提升 | with_reset_acc - without_reset_acc | 重置贡献 |


## 实施步骤

### Step 1: 实现 HistoricalDatabase + run_scorer_at_timestamp()

**实现细节：**

1. **HistoricalDatabase 类**:
   - 包装真实 Database 实例
   - get_conn() 返回一个代理 connection，拦截 execute() 方法
   - 对涉及 futures_klines、futures_n_structures、futures_signals 的查询自动追加 `AND timestamp <= _current_ts`
   - 对其他表（symbols 等静态表）不拦截

2. **run_scorer_at_timestamp(symbol, contract, db, ts, enable_reset)**:
   - `enable_reset=True` → 调用当前 scorer（含重置）
   - `enable_reset=False` → 临时绕过 `_apply_score_reset()` 调用
   - 记录 SignalResult + 后续 N 日价格验证
   - 返回包含准确率的结构化字典

### Step 2: Walk-Forward 主流程

1. 确定时间范围：基于 futures_klines 表中该品种的最早/最晚数据
2. 生成 fold 划分（训练期 3年 + 验证期 6月，滑动半窗口）
3. 在每个 fold 内按日步进，对每个时间点分别跑 with_reset/without_reset
4. 聚合各 fold 的准确率

### Step 3: 报告输出

输出 JSON:
```json
{
  "symbol": "RB",
  "total_checkpoints": 1500,
  "folds": [
    {
      "train_start": "2018-01",
      "train_end": "2020-12",
      "valid_start": "2021-01",
      "valid_end": "2021-06",
      "with_reset": { "total_signals": 45, "accuracy_1d": 62.3, "accuracy_5d": 58.1 },
      "without_reset": { "total_signals": 52, "accuracy_1d": 55.8, "accuracy_5d": 52.3 },
      "reset_improvement": { "accuracy_1d": 6.5, "accuracy_5d": 5.8 }
    }
  ],
  "avg_improvement": { "accuracy_1d": 4.2, "accuracy_5d": 3.1 }
}
```

---

## 关键决策记录

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 时间过滤方案 | HistoricalDatabase vs DB 视图 vs 全量重建 | HistoricalDatabase | 零侵入 scorer，不写 DB 迁移，可复用现有数据 |
| 重置控制方式 | 参数开关 vs 猴子补丁 | 参数开关 | 在调用层面控制，不改 scorer 代码 |
| 验证粒度 | 每日 vs 每周 vs 每新极值点 | 每日 | 与 scorer 的实时运行最接近 |
| 时间过滤范围 | 全部表 vs 仅 klines 和 n_structures | 仅 klines 和 n_structures | symbols 等静态表不包含时间戳 |
| 提升指标 | 绝对提升 vs 相对提升 | 绝对提升（百分点） | 更直观，直接反映重置贡献 |
