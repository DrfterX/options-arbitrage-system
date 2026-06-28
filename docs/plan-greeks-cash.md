# 期权 Greeks 现金化 — 补全计划

## 背景

共识要求将 Greeks 现金化标准应用到期权策略决策流程中。当前完成度：
- `greeks_cash.py` 已实现全部 4 个现金化函数（delta/gamma/vega/theta_cash）
- `app.py` 的 `_enrich_options_signals()` 已计算 delta/vega/theta Cash
- **缺失**: `net_gamma` 未存入 DB，gamma_cash 无法计算，options 面板不完整

## 分步实施计划

### Step 1: DB Schema + 迁移（core/schema.py + core/db.py）
- 在 `options_signals` 表添加 `net_gamma REAL DEFAULT 0` 字段
- 在 `db.py` 的 `init_all_tables()` 中添加 ALTER TABLE 迁移逻辑
- **影响**: 新信号写入时开始存储 gamma 值

### Step 2: 策略引擎 Gamma 计算（options/multi_strategy.py）
- Short Strangle: 在 `_calc_short_strangle()` 中添加 `net_gamma = -call.gamma - put.gamma`
- Iron Condor: 在 `_calc_iron_condor()` 中添加 `net_gamma = (-short_call.gamma) + (-short_put.gamma) + long_call.gamma + long_put.gamma`
- 两函数返回 dict 中追加 `net_gamma` 键
- **影响**: 策略计算时包含组合 Gamma 暴露

### Step 3: Pipeline 传递 Gamma（pipeline/orchestrator.py）
- 在 `run_options_scan()` 中每个策略信号 dict 添加 `net_gamma` 字段
- Short Strangle / Iron Condor: 从策略结果读取
- Ratio Spread: 从 spread 对象读取（需确认 OptionLeg/RatioSpread 类是否带 gamma）
- **影响**: 管线写入 DB 时包含 gamma

### Step 4: SignalHub 写入 Gamma（signals/hub.py）
- `record_options_signal()` 的 INSERT 语句添加 `net_gamma` 占位符
- `_safe_float()` 处理 `signal_dict.get("net_gamma", 0)`
- **影响**: DB 中存储 gamma 值

### Step 5: 前端展示 Gamma Cash（web/app.py）
- `_enrich_options_signals()` 添加 `gamma_cash` 计算
- 导入 `gamma_cash_1pct` 函数
- **影响**: options 面板显示 gamma_cash

---

## 当前执行：Step 1 — DB Schema + 迁移
