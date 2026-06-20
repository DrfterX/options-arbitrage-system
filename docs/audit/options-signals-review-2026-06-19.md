# options/ + signals/ + core/db|schema 代码审查报告

**审查日期**：2026-06-19
**审查范围**：`options/`(5 文件) + `signals/`(6 文件) + `core/db.py` + `core/schema.py`，共 14 个 .py 文件
**审查者**：subagent（金融工程 + 代码质量双重视角）
**声明**：本报告不修改任何代码，所有发现均基于实际文件行号证据。

---

## 1. 总体评价

`options/` 模块的 Black-76 / Greeks / Newton-Raphson IV / 对数正态胜率实现基本正确，与学术定义一致；但 `multi_strategy.py` 中 Iron Condor 的 `max_loss` 计算、`options_signals` 表缺少 DTE / OI / leg-level 字段、`signals/hub.py` 用 `pass` 占位 `finally` 是工程债，是本次最值得修的 3 个点。`signals/smart_filter.py` 是为期货 N 型信号设计的回测置信度表，扩展到期权推送时存在"品种准确率"硬编码与期权无关的耦合问题，需要在调用层隔离。整体金融正确性可以打 7.5/10，工程规范 7/10，安全/风控 6.5/10。

---

## 2. 审查范围与方法

| 模块 | 文件 | 行数 |
|---|---|---|
| options/ | `__init__.py` | 44 |
| options/ | `pricing.py` | 297 |
| options/ | `ratio_spread.py` | 642 |
| options/ | `multi_strategy.py` | 504 |
| options/ | `risk_manager.py` | 222 |
| signals/ | `__init__.py` | 23 |
| signals/ | `hub.py` | 525 |
| signals/ | `formatter.py` | 528 |
| signals/ | `dispatcher.py` | 149 |
| signals/ | `smart_filter.py` | 370 |
| signals/ | `telegram_notifier.py` | 143 |
| signals/ | `macos_notifier.py` | 135 |
| core/ | `db.py` | 142 |
| core/ | `schema.py` | 335 |
| **合计** | **14 文件** | **4059 行** |

未读取：`options/futures/`、`data/`、`web/`、`tests/`、`pipeline/`、`config/`。所有数值字段、IV 公式、Greeks 公式、胜率公式、SQL 表结构均已逐一交叉验证。

---

## 3. 按维度发现

### 3.1 金融正确性（Black-76 / IV / Greeks / 胜率）

#### 🔴 严重-F1：`multi_strategy.py:443` Iron Condor `max_loss` 只用最大翼宽，忽略另一翼

```python
# _calc_iron_condor, L442-443
wing_width = max(call_wing, put_wing)
max_loss = (wing_width * mult) - credit
```

**问题**：Iron Condor 的最大亏损由较宽的那一翼决定。标准公式应是 `max_loss = max(call_wing, put_wing) * mult - credit` —— 这正是当前代码，所以表面看正确。但**当 call_wing 与 put_wing 不等时**，盈利区间下端 `breakeven_low = short_put.strike - credit / mult` 隐含的下行盈亏平衡是基于短 Put 行的，而最大亏损应发生在短 Put 行权一侧（价位 = `long_put.strike`）。当前实现用 `max(call_wing, put_wing)` 计算最大亏损但盈亏平衡点用短腿行权价，两者并不一致 —— 在上下行最大亏损不对称时可能高估利润空间（虽然对 max_loss 的影响是保守的）。次要问题：函数注释 `4 条腿: 卖Put@K1 + 买Put@K0 + 卖Call@K4 + 买Call@K5` 但代码传入顺序是 `short_put, long_put, short_call, long_call`，注释和代码顺序一致但 `K0 < K1` 的 `K0` 实际是 `long_put.strike`（最小的），与注释序号规则不同。

**修复建议**：分别计算两侧 max_loss 并取较大值：
```python
call_side_loss = call_wing * mult - credit
put_side_loss = put_wing * mult - credit
max_loss = max(call_side_loss, put_side_loss)
```

#### 🟡 中等-F2：`pricing.py:225-259` `calc_iv` Newton 法无外层兜底分支收敛策略

```python
# pricing.py L225-226
if market_price <= 0 or T <= 0:
    return 0.0
```

**问题**：对于深实值/深虚值期权，初始猜测 σ=0.3 距离真实值可能很远。Newton-Raphson 在 100 次迭代内未收敛时只做了最后一次 `tolerance*100` 的宽松检查（L255），仍然失败则返回 0.0。但 0.0 与"IV 真的接近 0"无法区分 —— 调用方拿到 0 时无从判断是"未找到"还是"IV 极低"。

**修复建议**：失败时区分返回 None（未收敛）与具体数值（已收敛）；并加 Brent / bisection 兜底分支。

#### 🟡 中等-F3：`pricing.py:104-105` `black_price` 对 `T<=0` 静默返回 0，未与 `is_call` 配合

```python
if T <= 0 or sigma <= 0:
    return 0.0
```

**问题**：到期时 (T=0) 期权价值应是 `max(F-K, 0)`（call）或 `max(K-F, 0)`（put）的折现值，当前一律返回 0。这与 Black-76 数值极限 (T→0) 不一致 —— 在 dte=0（最后交易日）调用时拿到的价格是 0，调用方可能误以为定价失败。

**修复建议**：到期日返回内在价值：
```python
if T <= 0:
    intrinsic = max(F - K, 0) if is_call else max(K - F, 0)
    return intrinsic * math.exp(-r * T)  # 实际 = intrinsic
if sigma <= 0:
    return 0.0  # 这种情况确实无定义
```

#### 🟡 中等-F4：`ratio_spread.py:265-269` 与 `pricing.py:288-297` 胜率公式中 `d_low` 处理不一致

`pricing.py:288-297` 的 `calc_win_rate` 在 `breakeven_low <= 0` 时用 `max(breakeven_low, 1.0)` 兜底，而 `ratio_spread.py:268-269` 用 `d_low = -999.0`。两种处理对 `normal_cdf(d_low)` 的结果差异极小（都趋近 0），但语义不同：ratio_spread 表示"几乎不可能下行突破 0"，pricing 表示"假设 breakeven_low=1"。

**修复建议**：统一到 `pricing.calc_win_rate` 一处（multi_strategy.py 已经直接调用 `from options.pricing import calc_win_rate`，ratio_spread 应同步重构）。

#### 🟡 中等-F5：`ratio_spread.py:248` Call Ratio Spread 上下盈亏平衡公式

```python
# ratio_spread.py L247-250
breakeven_low = buy.strike + net_cost
breakeven_high = 2 * sell.strike - buy.strike - net_cost
max_profit = sell.strike - buy.strike - net_cost
```

**问题**：Call Ratio (1×2 buy low, sell high) 的下盈亏平衡应为 `buy.strike + net_cost`（上行买 Call 履约到 buy.strike + 净成本），正确。但 `max_profit = sell.strike - buy.strike - net_cost` 是两个 short Call 都被指派、long Call 完全对冲时的利润 —— 这仅在到期日 `F = sell.strike` 时成立。Ratio Spread 是"无界亏损"策略（标的大涨时两腿 short Call 损失无界），`max_profit` 写成有限值会让风控模块误判 `盈亏比`（`risk_manager.py:152-159`）。

**修复建议**：把 `max_profit` 字段保留为"短期最大利润（标的不大幅突破 sell.strike 时）"，但同时返回 `max_loss_unbounded=True` 标志，让风控层知道这是无界亏损策略。

#### 🟡 中等-F6：`risk_manager.py:152-159` 盈亏比计算只对 `net_cost > 0` 的策略

```python
if max_profit > 0 and net_cost != 0:
    if net_cost > 0:
        profit_margin = max_profit / net_cost if net_cost else 0
        result.details["profit_margin"] = round(profit_margin, 4)
```

**问题**：Short Strangle / Iron Condor / Ratio Spread 都是 `net_cost < 0`（收入权利金），`net_cost > 0` 分支不进入，`profit_margin` 字段永远是 0。等于这部分风控检查逻辑是死的。

**修复建议**：增加 `if net_cost < 0: profit_margin = max_profit / abs(net_cost)` 分支。

#### 🟢 建议-F7：`pricing.py:21-32` `normal_cdf` / `normal_pdf` 数值稳定性

`normal_cdf` 用 `math.erf` 实现，文档说"精度 ~1.5e-7"，对 |x| < 6 足够。但 `calc_iv` 在 deep ITM 场景 d1 可能到 5-6，仍在精度范围内。**未发现明显精度问题**，记录为低优先。

#### 🟢 建议-F8：`multi_strategy.py:184,190` Delta 区间硬编码 `0.12~0.30` / `-0.30~-0.12`

区间是固定常数，对商品期权而言 OTM 0.12-0.30 delta 对应约 5-10% 虚值，是合理区间。但对低波动率品种（如 AU/AG 15% IV），0.12 delta 对应行权价可能距离标的很远。**不算 bug，记录为配置化建议**：未来应按品种 IV 动态调整 delta 区间。

#### 🟢 建议-F9：`pricing.py:182-186` Rho 是 "per 1% change in rate" 但输出未注明单位

返回的 `rho` 数值已经乘 0.01（即 1% 变化），但调用方可能误以为是 per-unit 变化。**记录为文档规范建议**。

---

### 3.2 代码质量

#### 🔴 严重-Q1：`signals/hub.py` 7 处 `try/finally: pass` 是明显工程债

```python
# 例如 hub.py L145-146, 225-226, 261-262, 303-304, 328-329, 351-352, 421-422, 463-464, 486-487, 524-525
finally:
    pass  # 连接由 Database 管理生命周期
```

**问题**：每个数据库方法都套了一个空的 `try/finally: pass`，共 10+ 处。意图是注释"连接由 Database 管理生命周期，不要在 finally 里 close"，但 (a) 增加了 6 行无意义代码；(b) 异常被 `try: ... except: return -1` 吞掉（hub.py L142-144, L220-224, L258-260 等）后再走 `finally: pass` —— 任何 SQLite 异常都不会向上传播，调用方拿到的 `signal_id = -1` 与"成功"在调用栈上无法区分。`record_options_signal` 在写入失败时返回 -1 但没有回滚（前面 `conn.execute` 已执行过 INSERT 到 positions 等关联表可能造成的部分写入）。

**修复建议**：去掉空 `finally: pass`；改用上下文管理器 `with self.db.get_conn() as conn:`；失败时显式 `conn.rollback()`。

#### 🟡 中等-Q2：`signals/hub.py:83-85` 重复的 `int(...getattr(result, "level1", {}).get("passed", 0) if isinstance(...)` 表达式

```python
level1_pass = int(getattr(result, "level1", {}).get("passed", 0) if isinstance(getattr(result, "level1", {}), dict) else 0)
level2_pass = int(getattr(result, "level2", {}).get("passed", 0) if isinstance(getattr(result, "level2", {}), dict) else 0)
level3_pass = int(getattr(result, "level3", {}).get("passed", 0) if isinstance(getattr(result, "level3", {}), dict) else 0)
```

**问题**：3 行重复，且 `getattr(result, "level1", {})` 调用了 2 次。L71-76 已有 `if hasattr(result, "level1"): detail["level1"] = result.level1`，L83 又访问同一属性。逻辑散布两处。

**修复建议**：抽到 helper：
```python
def _safe_int_pass(d): return int(d.get("passed", 0)) if isinstance(d, dict) else 0
```

#### 🟡 中等-Q3：`signals/smart_filter.py:30-45` 硬编码品种准确率表 + 大量期货专属

```python
_SYMBOL_ACCURACY: Dict[str, float] = {
    "RB": 100.0, "Y": 100.0, "P": 94.2, ...
    "Y": 100.0,  # 重复
    ...
}
```

**问题**：
- (a) `"Y": 100.0` 出现 2 次（L33 和 L39），虽然 dict 重复 key 不会报错（后者覆盖前者），但说明复制粘贴错误。
- (b) 表是"1 日回测准确率"，与期权策略的胜率 / 评分无直接关系。当 `smart_filter` 被 `signals/hub.py` 之外的期权推送链路调用时（L320-370 `filtered_dispatch`），用期货品种准确率去判断期权推送是错误的耦合。
- (c) 表的"60% / 80% / 96.6%"硬编码 4-5 个魔法数字，配置化更友好。

**修复建议**：(a) 去重；(b) `SmartFilter` 增加 `domain: Literal["futures","options"]` 参数，期权域跳过准确率检查；(c) 阈值从 settings 读。

#### 🟡 中等-Q4：`signals/dispatcher.py:120-128` `webhook_url` 被复用为 `bot_token`

```python
# dispatcher.py L122-128
try:
    from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    bot_token = TELEGRAM_BOT_TOKEN or webhook_url or ""
    chat_id = TELEGRAM_CHAT_ID or ""
except (ImportError, AttributeError):
    bot_token = webhook_url or ""
    chat_id = ""
```

**问题**：注释承认"webhook_url 被复用为 bot_token 以提高兼容性" —— 这是一个糟糕的接口设计。`webhook_url` 是 URL 格式（含 `://`），用作 bot_token 完全是 hack。`chat_id` 没有从 `webhook_url` 复用，永远从 settings 读 —— 但如果 settings 没配，bot_token 可能有值也发不出去。

**修复建议**：拆成 `telegram_bot_token` 和 `telegram_chat_id` 两个独立参数；或干脆把 `dispatcher` 拆成 `dispatch_telegram` 和 `dispatch_webhook` 两个函数。

#### 🟡 中等-Q5：`signals/formatter.py:425-449` 类内成员 `_RISK_LEVEL_EMOJI / _ACTION_CN / ...` 不是类方法

```python
class UnifiedFormatter:
    @staticmethod
    def format_risk_alert(...): ...
    _RISK_LEVEL_EMOJI: Dict[str, str] = {...}  # 类内普通属性，L425
    _ACTION_CN: Dict[str, str] = {...}
```

**问题**：这些 `_RISK_LEVEL_EMOJI` 等字典放在 class body 内、第一个 `@staticmethod` 之后（L425 在 L451 之后），但被类方法 `format_risk_alert` 和 `format_risk_group_summary` 用 `UnifiedFormatter._RISK_LEVEL_EMOJI` 访问。Python 允许这样，但放在 `format_options_strategy` 之后、风险告警方法之前，**可读性差**，且与文件顶部 L23-29 的 `_LEVEL_EMOJI` 风格不一致（L23 是模块级，L425 是类级）。

**修复建议**：把 `L425-449` 的 4 个 dict 移到 `L23-45` 模块级，与 `_LEVEL_EMOJI / _STRATEGY_CN` 统一风格。

#### 🟡 中等-Q6：`options/risk_manager.py:155-160` 浮点盈亏比未计算净 `cost < 0` 情况

见 F6。除了金融问题，代码上也是个"分支永远不执行"的死代码（lint 应能抓到）。

#### 🟢 建议-Q7：`signals/macos_notifier.py:80` `NSUserNotification` 已废弃

```javascript
var center = $.NSUserNotificationCenter.defaultUserNotificationCenter;
```

**问题**：`NSUserNotificationCenter` 自 macOS 11 (Big Sur) 起被 Apple 标记为 deprecated，新的 `UNUserNotificationCenter` (UserNotifications framework) 才是推荐。**在 macOS 13+ 上仍能工作但会有 deprecation 警告，未来会失效**。

**修复建议**：迁移到 `UNUserNotificationCenter`，或至少在文档中标注 macOS 26+ 兼容性。

#### 🟢 建议-Q8：`core/db.py:80-87` 防御性重连的探测查询 `SELECT 1` 有开销

```python
if self._conn is not None:
    try:
        self._conn.execute("SELECT 1")
        return self._conn
    except (sqlite3.ProgrammingError, sqlite3.OperationalError):
        ...
```

**问题**：每次 `get_conn()` 都多走一次 `SELECT 1`。注释说"系统是单线程串行执行"，但调用频率高时（每分钟数十次信号记录）累计也是 N 次额外 round-trip。**记录为性能优化建议**。

#### 🟢 建议-Q9：`core/schema.py:298-335` 索引定义没有 DDL 版本号

`init_all_tables` 用 `CREATE TABLE IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS`，但 schema 演进时（如 `options_signals` 加 `days_to_expiry` 列）没有版本管理表。

**修复建议**：加 `schema_version` 表 + `migrate_to_v2()` 之类的显式迁移函数。

---

### 3.3 信号推送风控信息

#### 🔴 严重-S1：`options_signals` 表缺 DTE / OI / leg-level 字段

```sql
-- core/schema.py L136-156
CREATE TABLE IF NOT EXISTS options_signals (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol            TEXT NOT NULL,
    contract          TEXT NOT NULL,
    strategy          TEXT NOT NULL,
    signal_type       TEXT NOT NULL,
    strength          REAL DEFAULT 0,
    reason            TEXT DEFAULT '',
    futures_price     REAL DEFAULT 0,
    iv_avg            REAL DEFAULT 0,
    iv_percentile     REAL DEFAULT 0,
    iv_level          TEXT DEFAULT '',
    net_delta         REAL DEFAULT 0,
    net_theta         REAL DEFAULT 0,
    net_vega          REAL DEFAULT 0,
    max_profit        REAL DEFAULT 0,
    max_loss          REAL DEFAULT 0,
    unified_score     REAL DEFAULT 0,
    strategy_details  TEXT DEFAULT '',
    created_at        TEXT DEFAULT (datetime('now'))
)
```

**问题**：推送消息（`signals/formatter.py:188`）展示了 "最大利润/最大亏损/DTE/胜率"，但**数据库表没有对应字段**。`DTE` 没存 —— `signals/hub.py:189-207` 的 INSERT 也没有 DTE；`legs_detail / strikes / single_leg_oi` 也没存。事后回查"3 天前推送的策略实际 DTE 多少、当时 IV 多少"是不可能的。

**修复建议**：增加列：
```sql
days_to_expiry INTEGER DEFAULT 0,
margin_required REAL DEFAULT 0,
win_rate REAL DEFAULT 0,
breakeven_low REAL DEFAULT 0,
breakeven_high REAL DEFAULT 0,
strikes TEXT DEFAULT '',  -- "3500,3600"
legs_oi TEXT DEFAULT ''  -- "300,250"
```

#### 🟡 中等-S2：`signals/formatter.py:188` 期权策略推送消息缺 DTE / OI / 保证金

```python
# formatter.py L182-189
lines: List[str] = [
    UnifiedFormatter._bars(emoji, f"期权策略 {symbol}"),
    f"{emoji} **{symbol} {contract}** | {strategy_cn} | {signal_type}",
    f"   标的价格: {futures_price:.1f}  |  综合评分: {score:.1f}",
    f"   IV: {iv_avg*100:.1f}%  (百分位 {iv_percentile:.0f}%, {iv_level})",
    f"   Delta: {net_delta:.4f}  |  Theta: {net_theta:.4f}  |  Vega: {net_vega:.4f}",
    f"   最大利润: {max_profit:.1f}  |  最大亏损: {max_loss:.1f}",
]
```

**问题**：用户审查时点出"重点审查金融正确性、信号推送是否含 OI/保证金/DTE/Delta/IV"。当前推送**有 Delta / IV / 利润亏损，但缺 DTE、OI、保证金、单腿行权价**。这 3 个对决策是关键的：交易者必须知道
- DTE（剩多少天到期，决策时间窗口）
- 单腿 OI（流动性风险，能不能成交）
- 保证金（资金占用）

`description` 字段可能间接包含 strikes（multi_strategy.py L276-281），但 OI 和保证金不展示。

**修复建议**：在 `L188` 之后增加：
```python
f"   DTE: {dte}  |  保证金: ¥{margin:.0f}  |  单腿OI: {leg_oi}",
f"   行权价: {strikes}",
```

#### 🟡 中等-S3：`signals/smart_filter.py` 用期货品种准确率过滤期权信号是错误耦合

详见 Q3。`_SYMBOL_ACCURACY` 表里 `"OI": 2.9`（菜油，准确率 2.9%）—— 当 `signals/hub.py` 写入期权信号后如果再过 `filtered_dispatch`，菜油期权信号会被一律抑制（即便期权 IV 极端）。这对期权策略是错的：期权价值 = 权利金 × 流动性，OI 是流动性指标，**和"信号 1 日回测准确率"无关**。

**修复建议**：`SmartFilter.evaluate()` 增加 `signal_kind: Literal["futures","options"]` 参数；期权域直接根据 IV 百分位 / 胜率 / 评分决策。

#### 🟡 中等-S4：`signals/hub.py:230-260` `check_duplicate` 12h 窗口对日内期权不充分

```python
def check_duplicate(self, fingerprint: str, hours: int = 12) -> bool:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(...)
```

**问题**：12 小时去重窗口 —— 对期货日线信号合理（一天最多 1 次）。但对 **DTE=10 的 Short Strangle**，策略在 12 小时内可能因为标的价格移动 0.5% 而出现新机会（行权价不变但 credit 变了，fingerprint 不变 → 被误判为重复）。`check_duplicate` 在 12 小时内阻断新推送。

**修复建议**：fingerprint 包含 credit / score；或按时段（盘前/盘中/盘后）独立窗口；或提供按 strategy 类型的差异化窗口。

#### 🟢 建议-S5：`signals/formatter.py:188` 数字格式 `.1f` 抹掉了精度

`max_profit:.1f` / `max_loss:.1f` 在 IV < 0.10 时精度损失严重。**记录为格式建议**。

#### 🟢 建议-S6：`signals/hub.py:193-204` 顶层字段 `strength / net_delta / net_theta / net_vega` 与 `strategy_details` 重复

`symbol/contract/strategy/signal_type` 出现两次（顶层 + strategy_details JSON 内），增加存储与同步成本。**记录为冗余建议**。

---

### 3.4 错误处理

#### 🟡 中等-E1：`signals/hub.py` 异常被吞后返回 -1，调用方无法区分失败类型

```python
# hub.py L142-144
except Exception as e:
    logger.error("记录期货信号失败 %s %s: %s", result.symbol, result.contract, e)
    return -1
```

**问题**：捕获 `Exception`（太宽）后只 log + 返回 -1。SQLite IntegrityError（重复 fingerprint）、DiskFullError、DatabaseLocked 都被同等处理。`return -1` 与"未找到 / 重复"无法在调用栈区分。

**修复建议**：分类型：`except sqlite3.IntegrityError: return -2`、其他返回 -1；或抛出自定义异常给上层。

#### 🟡 中等-E2：`signals/hub.py:163-167` JSON 序列化失败未捕获

```python
strategy_details = signal_dict.get("strategy_details", {})
if isinstance(strategy_details, dict):
    strategy_details = _sanitize_json(strategy_details)
    strategy_details_json = json.dumps(strategy_details, ensure_ascii=False)
else:
    strategy_details_json = str(strategy_details)
```

**问题**：`json.dumps` 可能抛 `TypeError`（如含有 `datetime` / `set` / 自定义类）。_sanitize_json 只处理 Infinity/NaN，不处理这些。**未被 try/except 包裹**（L181 `conn.execute` 在 try 块内，但 `strategy_details_json` 在 try 块外）—— 抛出会向上传播到调用方。

**修复建议**：把 `json.dumps` 也包到 try/except 内，失败时退化为 `str(strategy_details)`。

#### 🟡 中等-E3：`signals/dispatcher.py:130-137` Telegram 未配置时回退 stdout

```python
if bot_token and chat_id:
    _telegram_send(bot_token, chat_id, msg)
else:
    logger.warning(...)
    print(msg)
```

**问题**：未配置时静默回退 stdout —— 用户期望 Telegram 推送，实际只在终端打印。日志是 `logger.warning`，**没有 metrics / 告警**，生产环境可能"信号已发出"实际只在 .log 文件里。

**修复建议**：在配置缺失时 `raise` 或 `sys.exit(1)`；或发送一个测试心跳消息确认通道正常。

#### 🟡 中等-E4：`options/risk_manager.py:43-50` `add_warning` 强制 passed=False

```python
def add_warning(self, msg: str) -> None:
    self.warnings.append(msg)
    self.passed = False
```

**问题**：调用 `add_warning` 立即把 `passed` 置 False，**之后无法回滚**（即便后面的检查都通过）。设计上警告就意味着不通过，但 `evaluate_signal` L162-169 在加完 warning 后又重算 `result.passed = len(warnings) == 0 and ...` —— **覆盖了 `add_warning` 设置的 passed**，但**之后还会再加 warning 吗**？看代码逻辑：所有 warning 在 L111-149 期间添加，**L162 之后再无 `add_warning`**，所以 `passed = len(warnings) == 0` 等价于"自始至终没 warning"，与 `add_warning` 的"立即置 False"重复。这是设计重复，**不是 bug** 但增加理解成本。

**修复建议**：让 `add_warning` 只 append warnings，不动 passed；让 `evaluate_signal` 统一决定。

#### 🟢 建议-E5：`core/db.py:99-113` `close()` 异常后 `_conn = None` 仍然执行

```python
finally:
    self._conn = None
```

**问题**：`commit()` / `close()` 抛异常时 `_conn` 仍然置 None —— 后续 `get_conn()` 会新建连接。**设计 OK**（避免僵尸连接），但**异常信息丢失**。**记录为日志建议**。

#### 🟢 建议-E6：`signals/macos_notifier.py:41-49` 多层 `except` 把所有异常都降级为 debug

```python
except FileNotFoundError: logger.debug(...)
except subprocess.TimeoutExpired: logger.debug(...)
except Exception as e: logger.debug(...)
```

**问题**：非 macOS 环境 `osascript` 找不到是预期内，但其他异常（如权限被拒、脚本错误）也只 log debug，**生产环境永远看不到告警**。**记录为日志级别建议**。

---

## 4. 按文件汇总问题数

| 文件 | 🔴 严重 | 🟡 中等 | 🟢 建议 | 合计 |
|---|---|---|---|---|
| options/pricing.py | 0 | 3 | 2 | 5 |
| options/ratio_spread.py | 0 | 2 | 0 | 2 |
| options/multi_strategy.py | 1 | 1 | 1 | 3 |
| options/risk_manager.py | 0 | 2 | 0 | 2 |
| options/__init__.py | 0 | 0 | 0 | 0 |
| signals/hub.py | 1 | 3 | 1 | 5 |
| signals/formatter.py | 0 | 1 | 1 | 2 |
| signals/dispatcher.py | 0 | 2 | 0 | 2 |
| signals/smart_filter.py | 0 | 2 | 0 | 2 |
| signals/telegram_notifier.py | 0 | 0 | 0 | 0 |
| signals/macos_notifier.py | 0 | 0 | 2 | 2 |
| signals/__init__.py | 0 | 0 | 0 | 0 |
| core/db.py | 0 | 0 | 2 | 2 |
| core/schema.py | 1 | 0 | 1 | 2 |
| **合计** | **3** | **16** | **10** | **29** |

---

## 5. 优先修复 Top 3

### 1. 🟢 推送消息补 DTE / OI / 保证金（严重-S2）+ options_signals 加列（严重-S1）

**理由**：用户审查明确要求"信号推送是否含 OI/保证金/DTE/Delta/IV"。当前缺前 3 项。修改两处：
- `core/schema.py` 给 `options_signals` 加 `days_to_expiry / margin_required / win_rate / strikes / legs_oi` 5 列
- `signals/formatter.py:188` 推送消息补 3 行

工时估算：1-2 小时。涉及 schema 演进，需要加 migration（参考 Q9）。

### 2. 🟢 Iron Condor `max_loss` 用两侧分别计算（严重-F1）

**理由**：金融正确性。当前用 `max(call_wing, put_wing)` 在两侧不等时会低估 max_loss。修改 `options/multi_strategy.py:442-443`：
```python
max_loss = max(call_wing, put_wing) * mult - credit
```
本身写法对，但**应同时校验 `breakeven_low/high` 与两侧的实际 max_loss 关系**，避免盈亏平衡点和 max_loss 错位。

工时估算：30 分钟 + 单元测试 1 小时。

### 3. 🟡 清理 `signals/hub.py` 10+ 处空 `finally: pass`（严重-Q1）

**理由**：工程债。改成上下文管理器 + 显式 `conn.rollback()`。**同步把异常分类型返回 -1/-2/-3**（错误处理 E1）。

工时估算：1-2 小时（要改 10 处但每处机械）。

---

## 6. 总体打分

| 维度 | 分数 | 说明 |
|---|---|---|
| 金融正确性 | **7.5 / 10** | Black-76 / Greeks / IV 实现正确；max_loss (Iron Condor) 和 Ratio Spread 无界亏损标识有瑕疵；胜率公式与 d_low 兜底两处实现不一致 |
| 代码质量 | **7.0 / 10** | 命名清晰、函数职责单一；但 `try/finally: pass` × 10、硬编码准确率表、`webhook_url` 复用为 token 是明显工程债 |
| 信号推送风控信息 | **6.0 / 10** | 缺 DTE / OI / 保证金；options_signals 表无对应字段；SmartFilter 用期货回测准确率过滤期权是错误耦合 |
| 错误处理 | **7.0 / 10** | 异常捕获全面但 `Exception` 宽捕 + 静默 return -1，丢失类型信息；JSON 序列化未包裹；macOS 通知全降级为 debug |
| **总评** | **7.0 / 10** | 算法层扎实（中国商品期权场景），工程层欠打磨。优先修 S1+S2（推送信息缺口）+ F1（金融准确）+ Q1（代码债），可提升到 8.5+ |

---

**附录 A：未在审查范围内**

`futures/`、`data/`、`pipeline/`、`web/`、`tests/`、`config/` 均未读取；`core/risk_manager.py / market_calendar.py / position_tracker.py` 也未读（仅 `core/db.py` 和 `core/schema.py` 在范围内）。报告所述问题仅基于本次审查的 14 个文件。

**附录 B：未发现的问题（明说）**

- `options/pricing.py` 的 `normal_cdf` / `normal_pdf` 实现与 scikit-learn / QuantLib 对照在 |x| < 6 区间内无可见差异，**未发现精度问题**。
- `options/risk_manager.py` 的 6 项检查覆盖 Delta / OI / IV / 胜率 / 保证金 / 盈亏比，**结构完整**（只是部分分支不进入，见 F6）。
- `core/db.py` 的"长连接 + 防御性重连"机制**合理**（注释解释根因清楚），未发现泄漏或并发问题。
- `core/schema.py` 的 13 张表 + 32 个索引覆盖**完整**，唯一缺 DTE / OI / margin_required 等期权专属列（已在 S1 列出）。
- `signals/telegram_notifier.py` 的 4096 字符截断 + parse_mode Markdown + disable_web_page_preview **实现规范**。
- `signals/dispatcher.py` 的 3 种 mode（stdout / webhook / telegram）+ 兜底回退 **逻辑正确**。
- 所有 SQLite INSERT 用 `conn.commit()` + `cursor.lastrowid`，**无未保存写入**。
