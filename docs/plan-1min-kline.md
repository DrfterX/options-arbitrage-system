# 1 分钟 K 线作为风控价格源 — 方案评估

> **撰写日期**: 2026-06-13
> **评估人**: CTO (Werner Vogels)
> **目的**: 解决风控"当前价格"滞后问题（当前最多滞后 30 分钟）

---

## 一、背景与问题

期权期货交易系统的全链路风控自动执行（止损/止盈/追踪止损）依赖 `_build_risk_price_map()` 从 `futures_klines` 表取最新 `close` 价。当前采集周期为 15m/1h/1d，由 launchd 每 1800 秒触发一次 `collect_all()`，导致风控检查时使用的"当前价格"可能滞后 15~30 分钟。以 SC2607 为例，若价格在 2 分钟内急跌触及止损线 535，系统需等最多 30 分钟才能发现并执行，存在实质性穿仓风险。

---

## 二、方案对比

| 维度 | **A: 1 分钟 K 线拉取** | **B: WebSocket 实时行情** | **C: 维持现状 (15m)** |
|------|------------------------|---------------------------|----------------------|
| **实时性** | ⭐⭐⭐ 滞后 ≤1 min，可覆盖分钟级跳空 | ⭐⭐⭐⭐⭐ 毫秒级 tick，真·实时 | ⭐ 滞后 15~30 min，无法防分钟级穿仓 |
| **采集成本** | ⭐⭐⭐ 每轮 65 品种 × 1 次 HTTP 请求/品种，日间每 1~3 分钟跑一轮 | ⭐⭐⭐⭐⭐ WebSocket 长连接，单 TCP 链路推送全部品种 | ⭐⭐⭐⭐⭐ 每 30 分钟 65 次 HTTP 请求 |
| **存储增量** | ⭐⭐ 约 **39,000** 行/天（65 品种 × ~600 条/天 × 1m）；若仅持仓品种采集则约 **600** 行/天 | ⭐ 需额外建 tick 表，存库方案需设计（或纯内存不落盘） | ⭐⭐⭐⭐⭐ 约 2,600 行/天（15m 级） |
| **实现难度** | ⭐⭐⭐⭐⭐ **极低** — 代码已支持 `period="1"`，只需改配置参数 | ⭐ 需调研 Sina/其他免费 WebSocket 协议、实现连接管理、心跳重连、断线补数 | ⭐⭐⭐⭐⭐ 无改动 |
| **维护成本** | ⭐⭐⭐⭐ 依赖 AKShare HTTP，偶尔超时重试即可，纯增量无状态 | ⭐⭐ WebSocket 需处理状态机（断连、重连、数据对账），macOS 后台进程更复杂 | ⭐⭐⭐⭐⭐ 零维护 |

### 存储细节 (仅 A 方案)

| 场景 | 日增量（行） | 年增量 | SQLite 预估体积 |
|------|------------|--------|----------------|
| 65 品种全采 1m | ~39,000 | ~14M 行 | ~1.4 GB (每行 ~100 bytes) |
| 仅持仓品种采 1m（当前 1 个） | ~600 | ~219K 行 | ~22 MB |
| 仅持仓品种采 1m + 过滤非交易时段 | ~300 | ~110K 行 | ~11 MB |

> SQLite 单表千万级仍有良好查询性能，年增量 14M 行完全可控。但全量采集 65 品种无必要——风控只需持仓合约的实时价格。

---

## 三、推荐方案

### **方案 A-轻量版：仅对持仓合约采集 1 分钟 K 线**

理由：

1. **实时性与成本的最佳平衡** — 1 分钟级延迟可将风控响应从 30 分钟缩至 ≤1 分钟，覆盖绝大多数分钟级行情波动
2. **实现成本几乎为零** — `fetch_klines()` 已原生支持 `period="1"`，`collect_symbol()` 已有 1m 采集 + 3m 聚合逻辑，只需新增一个 `collect_risk_prices()` 方法，传 `{"1m": "1"}` 周期映射
3. **不存在 WebSocket 方案的不确定性** — AKShare Sina HTTP 接口已验证数月，稳定可靠；免费 WebSocket 方案（新浪/腾讯）无官方文档，协议逆向风险高，断线补数逻辑复杂
4. **增量可控** — 当前仅 1 个持仓，日增量 ~600 行，爬坡到 5 个持仓也仅 ~3,000 行/天，SQLite 无压力

**不选 WebSocket 的原因：** 免费期货 WebSocket 行情（新浪/东方财富）均为非官方逆向协议，无 SLA、频繁变更、需大量测试验证。当前系统运行在 macOS mini 后台，WebSocket 长连接的后台进程管理比 launchd 定时任务复杂得多。1 分钟 K 线的延迟对于止损/止盈场景已足够——真正需要 tick 级响应的场景（如高频做市）不在本系统范围内。

---

## 四、实现要点

### 1. 新增 `collect_risk_prices()` 方法

在 `FuturesCollector` 中新增方法，专门为持仓合约采集 1m K 线：

```python
def collect_risk_prices(self, contracts: list[str]) -> dict:
    """为风控持仓合约采集 1 分钟 K 线（增量）。

    Args:
        contracts: 持仓合约代码列表，如 ['SC2607']。

    Returns:
        {contract: {timeframe: stats}} 采集统计。
    """
    results = {}
    for contract in contracts:
        # 从 registry 反查 symbol
        symbol = self._contract_to_symbol(contract)
        if not symbol:
            continue
        # 只采 1m（不采 15m/1h/1d，这些由 collect_all 负责）
        stats = self.collect_symbol(symbol, contract, {"1m": "1"})
        results[contract] = stats
        time_module.sleep(0.3)
    return results
```

### 2. 修改 `_build_risk_price_map()` 查询策略

当前 SQL 在 `futures_klines` 表查最新 `close`，但不限定 `timeframe`。如果有 1m 数据入库，需要确保查询优先取 1m 数据：

```python
latest = conn.execute(
    "SELECT close FROM futures_klines "
    "WHERE contract=? AND timeframe='1m' "
    "ORDER BY timestamp DESC LIMIT 1",
    (contract,),
).fetchone()
# 降级：若无 1m 数据，回退到任意周期的最近数据
if not latest:
    latest = conn.execute(
        "SELECT close FROM futures_klines "
        "WHERE contract=? ORDER BY timestamp DESC LIMIT 1",
        (contract,),
    ).fetchone()
```

### 3. 采集时机

两个方案二选一：

- **嵌入现有 pipeline（简单）**：在 `orchestrator.run_all()` 中，调用现有 `collect_all()` 之后，追加 `collect_risk_prices(open_contracts)`。无需新增 launchd 任务。
- **独立高频采集（激进的实时性）**：新增独立 launchd 任务，每 60~120 秒单独调用 `collect_risk_prices()`。即使全量扫描 30 分钟一次，风控价格也能保持 ≤2 分钟新鲜度。

推荐**方案一（嵌入 pipeline）**作为第一步，后续若需更高实时性再升级到方案二。

### 4. `_contract_to_symbol` 映射支持

需要一个从合约代码（如 `SC2607`）反查品种代码（如 `SC`）的方法。可以从 `ContractRegistry` 扩展，或直接从 `futures_klines` 表查询：

```python
def _contract_to_symbol(self, contract: str) -> Optional[str]:
    conn = self.db.get_conn()
    row = conn.execute(
        "SELECT symbol FROM futures_klines WHERE contract=? LIMIT 1",
        (contract,),
    ).fetchone()
    return row["symbol"] if row else None
```

---

## 五、风险与注意事项

1. **AKShare Sina 1 分钟数据的实时性边界** — AKShare `futures_zh_minute_sina(period="1")` 返回的"当前分钟"K 线可能在分钟未结束时已更新，但何时更新无文档保证。实测建议：在盘中连续调用 3 次（间隔 5 秒），确认该接口在当前分钟内的刷新频率。若表现不可靠，需降级为每 2 分钟采集一次（即接受 ≤2 分钟延迟）。

2. **3m 聚合重叠** — `collect_symbol()` 传入 `{"1m": "1"}` 时会自动触发 `_collect_3m_from_1m()`。如果 `collect_all()` 同时也在采 1m（未来某个版本），会导致 3m 数据被重复写入（INSERT OR IGNORE 可去重，但同时间窗口不同 OHLC 值会产生冲突）。建议 `collect_all` 的默认周期映射中**移除** 1m，将 1m 采集完全交由 `collect_risk_prices()` 负责。

3. **非交易时段空跑** — 夜盘结束后至次日日盘开盘前（~23:00~09:00），AKShare 1m 接口返回空数据。增量采集逻辑（`last_ts` 判断）能自动跳过空循环，但每 30 分钟仍会发起 65 次无意义 HTTP 请求。可在 `collect_risk_prices()` 开头加入交易时段判断，非交易时段直接跳过。
