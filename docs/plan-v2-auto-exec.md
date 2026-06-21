# 风控 V2 自动执行方案设计

> **Munger 审查结论**: 条件性否决 — 方向正确，但当前方案有 3 个致命缺陷，修复后方可上线。
> 审查详情: `docs/critic/cycle37-auto-exec-v2-review.md`

## 目标
为风控引擎增加自动平仓执行能力，消除"告警模式"的根本缺陷 — 快速行情下告警来不及手工处理。

## 设计原则（修正版）

1. **告警与执行分离**：PositionRiskManager 只做检测，Orchestrator 负责执行调度
2. **SL/TP 本身就是安全边界** → 一旦触发即执行，不等待 N 次确认（Munger 建议）
3. **交易安全第一**：平仓操作必须事务安全；平仓失败必须重试/告警
4. **全局 Kill Switch**：一条 SQL 即可停止所有自动执行
5. **向后兼容**：auto_execute=0（默认）保持纯告警模式不变

## ⚠️ 与原始方案的关键变更（Munger 审查驱动）

| 项目 | 原始方案 | 修正后 |
|------|---------|--------|
| 执行时机 | alert_level=critical（5 次触发，约 2.5h） | **触发即执行**（SL/TP 本身就是安全边界） |
| 级别比较 | `alert_level >= execute_on_level`（字符串字典序） | `LEVEL_MAP[alert_level] >= LEVEL_MAP[execute_on_level]`（整数枚举） |
| 平仓事务 | 未明确顺序 | **先 close_position 成功 → 同事务设 auto_execute=0** |
| 全局开关 | 无 | `system_config` 加 `auto_execute_global` 控制行 |
| 失败重试 | 未考虑 | 最多重试 1 次，失败后紧急通知 |
| 价格数据 | `futures_klines` 收盘价（滞后 0-30min） | 最低使用 1 分钟 K 线，**标为待 CTO 评估** |

## 架构变更

### DB 层变更

#### risk_management 表新增字段

| 列名 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `auto_execute` | INTEGER | 0 | 是否启用自动平仓 (0=仅告警, 1=自动执行) |
| `execute_at` | INTEGER | NULL | 最近一次自动执行时间戳（审计） |

**移除**：`execute_on_level` — 不再需要分级执行，触发即执行。

#### system_config 表新增（全局 Kill Switch）

```sql
CREATE TABLE IF NOT EXISTS system_config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT OR IGNORE INTO system_config (key, value) VALUES ('auto_execute_global', '1');
```

### 告警等级枚举（修复字符串比较 bug）

```python
from enum import IntEnum

class AlertLevel(IntEnum):
    NONE = 0
    INFO = 1
    WARNING = 3
    CRITICAL = 5

# 使用数值比较，而非字符串字典序
# ALERT_THRESHOLDS 保持不变
```

### Pipeline (Orchestrator) 新增方法

```python
def _execute_risk_triggers(self, results: list[RiskCheckTriggerResult]) -> None:
    """自动平仓执行器。

    流程（事务安全）：
    1. 检查全局开关：system_config['auto_execute_global'] == '1'
    2. 过滤 is_triggered() == True 的结果
    3. 对于每个触发：
       a. 查询该持仓的 auto_execute 标志
       b. 如果 auto_execute=True:
          → 调用 self.position_tracker.close_position(
                position_id=r.position_id,
                close_price=r.current_price,
                close_time=int(time.time()),
                reason=r.action,  # 'stop_loss' / 'take_profit' / 'trailing_stop'
             )
          → 成功: 同一事务内设置 auto_execute=0（防循环平仓）
          → 失败: 保留 auto_execute=1，记录日志，发送紧急通知
          → 第二次失败: 升级为 Telegram 加急推送 "自动平仓失败，请人工干预"
    4. 更新 risk_management.execute_at 为执行时间戳
    """
```

### 数据流（最终版）

```
Pipeline run_futures_scan() / run_all()
  → risk_manager.check_all_positions(price_map)        # ① 检测（不变）
  → _handle_risk_results(risk_results)                 # ② 通知（不变）
  → _execute_risk_triggers(risk_results)                # ③ NEW: 自动执行
```

### API 层 — 设置 auto_execute 的入口

通过 `PositionTracker.set_risk_params()` 扩展：

```python
def set_risk_params(
    self,
    position_id: int,
    sl_price=None, tp_price=None,
    trail_activation_price=None, trail_distance=None, trail_step=None,
    alert_level=None, alert_reason="",
    auto_execute: bool | None = None,      # NEW
) -> bool:
```

### 全局开关控制

```python
# 获取全局开关
def _get_global_auto_execute(self) -> bool:
    conn = self.db.get_conn()
    row = conn.execute(
        "SELECT value FROM system_config WHERE key='auto_execute_global'"
    ).fetchone()
    return row and row['value'] == '1'

# 关闭所有自动执行（一条 SQL）
# UPDATE system_config SET value='0' WHERE key='auto_execute_global';
```

## 安全机制（Munger 驱动）

1. **默认不启用**：新持仓 auto_execute=0，用户手工开启
2. **事务安全**：close_position 成功后才更新 auto_execute=0（同一事务，防止平仓失败后裸奔）
3. **全局 Kill Switch**：system_config 表一行控制全部
4. **失败重试+升级告警**：第一次失败重试，第二次失败紧急通知
5. **审计追踪**：execute_at 记录执行时间，日志记录完整路径

### 安全机制流程图

```
触发条件满足 + auto_execute=1
  → 检查全局开关: ON?
    → NO: 跳过，仅告警
    → YES:
      → close_position(attempt #1)
        → SUCCESS: 同事务内 auto_execute=0, 发通知 "已自动平仓"
        → FAIL: 记录日志, 重试 (attempt #2)
          → SUCCESS: 同事务内 auto_execute=0, 发通知 "已自动平仓(重试成功)"
          → FAIL: 保留 auto_execute=1, 发紧急通知 "自动平仓失败，请人工干预"
```

## ⚠️ 待 CTO 评估：实时价格问题（Munger 条件 1）

**问题**：`_build_risk_price_map()` 从 `futures_klines` 取最新 close，这是已完成 K 线，在 3 分钟 K 线下最多滞后 3 分钟，在 Pipeline 30 分钟周期下最坏情况滞后 30+ 分钟。

**备选方案**：

| 方案 | 复杂度 | 滞后 | 说明 |
|------|--------|------|------|
| A: 1min kline | 低 | 0-1 min | 如果数据源已有 1 分钟 K 线，直接改用 |
| B: 实时 tick | 高 | 秒级 | 从数据源获取实时 tick/报价，需要 WebSocket |
| C: Pipeline 缩短 | 中 | 0-5 min | 独立风控 cron 每 5 分钟跑，不依赖全量扫描 |

**推荐**：方案 A（最低成本），先上线后再评估是否需要方案 B。

## 影响范围

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `core/risk_manager.py` | 小改 | AlertLevel IntEnum；RiskCheckTriggerResult 新增 auto_execute 字段 |
| `core/position_tracker.py` | 小改 | set_risk_params 支持 auto_execute 参数 |
| `pipeline/orchestrator.py` | 新增 | _execute_risk_triggers 方法 + _get_global_auto_execute |
| DB schema | 迁移 | risk_management 加 2 列；创建 system_config 表 |

## 不做的事（Scope 外）
- ❌ 实时 WebSocket 报价接入（V3 或 CTO 评估后决定）
- ❌ 部分平仓自动执行
- ❌ 期权组合自动平仓
- ❌ Web UI 控制面板

## 子任务拆解

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 7.2.1 | ✅ **设计+ Munger 审查** | 15min | 本文件 + docs/critic/cycle37-auto-exec-v2-review.md |
| 7.2.2 | 实现 DB 迁移 + PositionRiskManager 更新 | 20min | core/risk_manager.py 更新 |
| 7.2.3 | 实现 Orchestrator._execute_risk_triggers | 20min | pipeline/orchestrator.py 更新 |
| 7.2.4 | 测试验证 + 共识更新 | 15min | 测试输出 + consensus.md |
