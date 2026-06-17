# 交易 API 集成架构设计

## 概览

本文档评估三个实盘交易接入方案，给出推荐架构、新增模块设计、风控哨兵规范、订单状态机、集成路线图和关键决策记录（ADR）。

## 需求背景

- **当前状态**：信号系统已稳定运行（N 型期货 + Black-76 期权，65 品种），SQLite 长连接缓存 + numpy 签名修复已验证通过。所有信号为 WATCH/CANDIDATE/ENTRY 三级，通过 SmartFilter 回测过滤后推送。
- **目标**：从"只出信号"到"实盘执行"，即信号产生 → 风控审批 → 订单执行 → 仓位管理 → 盈亏跟踪。
- **约束**：独立开发者（1 人），最小可行资金量，boring technology first，monolith first。

## 1. 架构方案评估

### 方案 A：通过 vnpy 中间层

vnpy 是 Python 量化交易领域最成熟的框架之一，已封装 CTP（中国期货市场）、XTQuant（期权）、TQSdk（天勤）等 SDK。

| 维度 | 评估 |
|------|------|
| **复杂度** | 中等 — 需要部署独立的 vnpy 进程，通过 IPC/REST 与当前信号系统通信 |
| **开发量** | 3-4 Cycles — vnpy 封装层 + 进程管理 + 信号转订单适配器 |
| **优势** | 接入成本低（CTP/XT/TQ 全部现成），风控模块内置，社区成熟 bug 少 |
| **风险** | vnpy 引入 300+ 依赖（pandas/numpy/mongodb/rabbitmq...），与当前 uv venv 环境冲突风险高；vnpy 的架构强耦合 MongoDB + Event Engine，偏离当前 SQLite 架构；需要额外维护一个 Python 进程的生命周期；独立开发者调试 vnpy 内部问题极耗时 |
| **维护成本** | 高 — vnpy 版本升级可能引入破坏性变更 |

**结论：否决。** 对独立开发者而言，vnpy 的重量级架构是"大炮打蚊子"。300+ 依赖在 uv 签名修复场景下是运维噩梦。信号系统 full scan 只需 3 分钟，vnpy 的 Event Engine 循环长期运行完全多余。

### 方案 B：直接封装交易 API（推荐）

在现有信号系统中新增 `trading/` 模块，直接通过具体交易 API 的 Python SDK 进行交易。

| 维度 | 评估 |
|------|------|
| **复杂度** | 低 — 新增一个包，依赖只增加目标 SDK（1-2 个 pip 包） |
| **开发量** | 2-3 Cycles — 风控哨兵 + 订单管理 + 具体 API 封装 |
| **优势** | 零额外框架依赖，与现有 SQLite 架构天然一致，风控逻辑可复用现有 RiskManager 思路，调试路径短（全在同一个进程） |
| **风险** | 需要自研风控哨兵和订单管理（但信号系统已部分实现）；API 版本变更需手动适配 |
| **维护成本** | 低 — 一个包，几百行代码 |

**结论：推荐。** 与当前架构完全兼容（SQLite + Flask + 单体），不引入任何运行时依赖。风控和订单管理在信号系统已有雏形（RiskManager + SignalHub），扩展即可。

### 方案 C：用交易平台 SDK 替换数据层

直接用天勤/掘金 SDK 替代当前 AKShare 数据采集层，数据+交易统一。

| 维度 | 评估 |
|------|------|
| **复杂度** | 高 — 需要重写所有 data/ 模块（futures_collector / options_collector / iv_recorder） |
| **开发量** | 5+ Cycles — 数据层迁移 + 适配 + 回测验证 |
| **优势** | 数据与交易同源，减少不一致性 |
| **风险** | AKShare 已稳定运行，全面替换涉及 regression；天勤/掘金数据格式与当前系统不完全兼容（K线聚合/MACD/N型检测均依赖当前数据格式）；代价远大于收益 |
| **维护成本** | 高 — 切换数据源后所有回测数据需要重新对齐 |

**结论：否决。** 信号系统最宝贵的资产是 6000+ 回测记录和稳定的数据管线。为了交易接口全面替换数据层是本末倒置。数据层面改进可做增量（如新增一个交易数据源），不破坏现有管线。

### 方案对比矩阵

| 准则 | 方案 A (vnpy) | 方案 B (直封 API) | 方案 C (换数据层) |
|------|:---:|:---:|:---:|
| 开发周期 | 3-4 | **2-3** | 5+ |
| 新增依赖 | 300+ | **1-2** | 1-2 |
| 与现有架构兼容 | 低 | **高** | 低 |
| 风控成熟度 | 高 | 中（需自研） | 低 |
| 运维负担 | 高 | **低** | 中 |
| 回调验证风险 | 低 | **低** | 高 |
| 独立开发者友好度 | 低 | **高** | 中 |
| **综合评分** | 5/10 | **9/10** | 4/10 |

---

## 2. 推荐方案 — 直接封装交易 API

### 架构总览

```text
┌─────────────────────────────────────────────────────────────────┐
│                        信号系统 (现有)                            │
│                                                                  │
│  pipeline/orchestrator.py                                        │
│    ├── futures.scorer ──→ SignalHub ──→ SmartFilter ──→ dispatch │
│    └── options.multi_strategy ──→ RiskManager ──→ SignalHub      │
│         SignalHub ──→ dispatch                                   │
│                                                                  │
│  信号入库后，由 TradingOrchestrator 读取、风控、执行                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   交易执行层 (trading/ 新增)                       │
│                                                                  │
│  TradingOrchestrator (扫描信号表 → 策略级别风控 → 执行)          │
│    ├── trading/sentinel.py     — 风控哨兵（防过度/防自成交/防极    │
│    │                            端行情/日亏损上限）               │
│    ├── trading/order_manager.py — 订单状态机 + 数据库管理         │
│    ├── trading/broker_*.py     — 具体交易 API 封装               │
│    │        ├── broker_ctp.py        (CTP-Python SDK)            │
│    │        ├── broker_tq.py         (天勤 TQSdk)               │
│    │        └── broker_sim.py        (模拟器，回测用)             │
│    └── trading/models.py       — 订单/仓位/风控数据模型           │
│                                                                  │
│  交易执行状态写入 SQLite 新表： orders / positions / trades       │
└─────────────────────────────────────────────────────────────────┘
```

### 数据流

```text
信号管道：
  Orchestrator.run_all()
    → futures/options 扫描
    → SignalHub 写入 futures_signals / options_signals
    → SmartFilter + dispatch (推送通知)

交易管道（新）：
  TradingOrchestrator.poll()          [定时触发 / cron 驱动]
    → 读取信号表 (signal_type='ENTRY', 未执行)
    → Sentinel.evaluate(signal)       [风控哨兵检查]
    → OrderManager.create_order()     [创建订单状态机]
    → Broker.place_order()            [发送到交易所]
    → OrderManager.sync_status()      [轮询/回调更新状态]
    → PositionManager.update()        [更新持仓]
```

### 新增目录结构

```text
trading/
├── __init__.py
├── orchestrator.py        # TradingOrchestrator — 交易管线调度
├── sentinel.py            # 风控哨兵 — 交易前/中/后三层防护
├── order_manager.py       # 订单管理器 — 状态机引擎 + CRUD
├── position_manager.py    # 仓位管理器 — 持仓跟踪 + 风险聚合
├── models.py              # 数据模型: Order / Position / SentinelRecord
├── broker_base.py         # Broker 抽象基类
├── broker_sim.py          # 模拟交易器（回测/沙箱用）
├── BrokerCtp.py           # CTP 封装（可选接入）
├── broker_tq.py           # 天勤 TQSdk 封装（推荐首选）
└── db.py                  # trading 表 DDL + 初始化
```

### 核心类设计

```python
# trading/sentinel.py
class Sentinel:
    """风控哨兵 — 三层防御。

    第一层：交易前 PreTrade 检查
      - 日亏损限额 (daily_loss_limit)
      - 总持仓上限 (max_total_positions)
      - 品种集中度 (max_symbol_concentration)
      - 自成交检查 (self_trade_check)
      - 极端行情检查 (extreme_market_check)
      - 信号时效检查 (signal_freshness, 超过 N 分钟的信号不执行)

    第二层：交易中 MidTrade 检查
      - 订单价格偏离检查 (price_slippage > N% 则取消)
      - 对手方流动性检查 (订单簿深度)

    第三层：每日全局限制
      - 每日最大交易次数
      - 每日最大亏损金额
      - 最大敞口比例
    """

# trading/order_manager.py
class OrderManager:
    """订单管理器 — 完整的订单生命周期管理。

    维护 orders 表，驱动状态机流转：
      PENDING → SUBMITTED → PARTIAL_FILLED → FILLED
                        → CANCELLED
                        → REJECTED
    """

# trading/position_manager.py
class PositionManager:
    """仓位管理器 — 跟踪开仓、减仓、平仓。

    维护 positions 表，支持：
      - 按品种聚合持仓
      - 实时盈亏计算
      - 自动止损检查（价格止损 + 时间止损）
      - 策略级平仓信号触发
    """

# trading/broker_base.py
class BrokerBase(ABC):
    """Broker 抽象基类 — 所有交易 API 封装必须实现以下接口。"""

    @abstractmethod
    def place_order(self, order: Order) -> OrderResult: ...
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool: ...
    @abstractmethod
    def get_order_status(self, order_id: str) -> OrderStatus: ...
    @abstractmethod
    def get_positions(self) -> list[Position]: ...
    @abstractmethod
    def get_account_info(self) -> AccountInfo: ...
    @abstractmethod
    def get_market_data(self, symbol: str) -> MarketData: ...
```

---

## 3. 风控哨兵设计

### 三层防御体系

```
                         ┌──────────────────────┐
                         │   Layer 1: PreTrade   │
                         │   每笔交易前检查        │
                         └──────────┬───────────┘
                                    │ PASS
                                    ▼
                         ┌──────────────────────┐
                         │   Layer 2: MidTrade   │
                         │   订单发出后监控       │
                         └──────────┬───────────┘
                                    │ PASS / 持续
                                    ▼
                         ┌──────────────────────┐
                         │   Layer 3: Daily      │
                         │   全局限制             │
                         └──────────────────────┘
```

### Layer 1 — 交易前检查（PreTrade）

| 检查项 | 阈值 | 说明 |
|--------|------|------|
| 日亏损限额 | `max_daily_loss = INITIAL_CAPITAL * 0.05` | 当日已实现亏损 + 浮动亏损超限则禁一切新开仓 |
| 总持仓上限 | `max_open_positions = 3` | 同时持仓品种数上限，独立开发者精力有限 |
| 品种集中度 | `max_symbol_exposure = 0.4` | 单一品种暴露不超过总资金的 40% |
| 自成交检查 | 同品种同方向已有仓位 | 防止信号系统重复产生同方向信号时自成交 |
| 极端行情检查 | 涨跌幅 > N% / 价格 > M 标准差 | 涨跌停板附近、重大行情爆发时禁用新开仓 |
| 信号时效检查 | 信号产生时间 > 15 分钟 | 过期信号不执行（市场已变） |
| 仓位冲突检查 | 已有反向仓位时需确认 | 同品种反手需要明确信号级别 (ENTRY 以上) |

### Layer 2 — 交易中检查（MidTrade）

| 检查项 | 阈值 | 说明 |
|--------|------|------|
| 价格偏离 | 成交价 vs 信号入场价 > 0.5% | 订单价格偏离过大自动撤单重发或取消 |
| 流动性枯竭 | 订单簿深度不足 | 挂单 N 秒未成交则撤单（避免市价单滑点） |
| 断线重连 | WebSocket 断开 | 自动重连 + 状态同步（查询所有未结订单） |

### Layer 3 — 每日全局限制（Daily Limits）

| 限制项 | 默认值 | 说明 |
|--------|--------|------|
| 每日最大交易次数 | 5 (开+平) | 防过度交易，由独立开发者精力的实际限制决定 |
| 每日最大亏损 | 初始资金的 5% | 单日达到止损线后自动熔断，当日不再开新仓 |
| 最大敞口 | 总资金的 60% | 总保证金 / 总资金不超过 60% |
| 策略最大同时持仓数 | 2 个品种 | 新系统调试阶段，多策略并行会增加不可控性 |

### 实现设计

```python
# trading/sentinel.py — 关键设计

class Sentinel:
    def __init__(self, db: Database):
        self.db = db
        # 从 system_config 表加载配置（可动态调整）
        self.config = self._load_config()

    def check_trade(self, signal: dict) -> SentinelResult:
        """Layer 1: 交易前完整检查。返回 PASS/BLOCK 及原因。"""
        checks = [
            self._check_daily_loss(),        # 日亏损限额
            self._check_max_positions(),      # 总持仓上限
            self._check_symbol_concentration(signal["symbol"]),  # 品种集中度
            self._check_self_trade(signal),    # 自成交
            self._check_extreme_market(signal["symbol"]),  # 极端行情
            self._check_signal_freshness(signal),  # 信号时效
        ]
        failed = [c for c in checks if not c.passed]
        return SentinelResult(
            passed=len(failed) == 0,
            blocked_by=failed,
            timestamp=datetime.now(MARKET_TZ),
        )

    def check_order(self, order: Order, market_data: MarketData) -> SentinelResult:
        """Layer 2: 订单发出前价格偏离检查。"""
        deviation = abs(order.price - market_data.last_price) / market_data.last_price
        if deviation > self.config["max_price_deviation"]:
            return SentinelResult(
                passed=False,
                blocked_by=[f"Price deviation {deviation:.2%} > {self.config['max_price_deviation']:.2%}"],
            )
        return SentinelResult(passed=True)

    def can_trade_today(self) -> bool:
        """Layer 3: 每日全局限制检查。"""
        stats = self._get_daily_stats()
        checks = [
            stats["daily_loss"] <= self.config["max_daily_loss"],
            stats["trade_count"] <= self.config["max_daily_trades"],
            stats["total_exposure"] <= self.config["max_exposure"],
        ]
        return all(checks)
```

### Sentinel 配置存储

所有风控参数存储在新表 `sentinel_config` 中，可在运行时通过 Web 看板调整：

```sql
CREATE TABLE sentinel_config (
    key         TEXT PRIMARY KEY,
    value       REAL NOT NULL,
    description TEXT DEFAULT '',
    updated_at  TEXT DEFAULT (datetime('now'))
);
```

默认配置初始化：

| key | value | description |
|-----|-------|-------------|
| max_daily_loss | 500.0 | 每日最大亏损（元） |
| max_daily_trades | 5 | 每日最大交易次数 |
| max_open_positions | 3 | 最大同时持仓品种数 |
| max_symbol_exposure | 0.4 | 单一品种最大资金占比 |
| max_total_exposure | 0.6 | 总资金最大敞口比例 |
| max_price_deviation | 0.005 | 订单价格最大偏离（0.5%） |
| signal_max_age_minutes | 15 | 信号最长有效时间（分钟） |
| extreme_market_stddev | 3.0 | 极端行情检测标准差倍数 |

---

## 4. 订单状态机

### 状态转换图

```text
                         ┌──────────┐
                         │  PENDING │  ← 订单创建成功，尚未提交到券商
                         └────┬─────┘
                              │ submit()
                              ▼
                         ┌──────────┐
                         │ SUBMITTED│  ← 已发送到券商/交易所，等待确认
                         └────┬─────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
              ┌──────────┐ ┌──────┐ ┌────────┐
              │PARTIAL   │ │FILLED│ │REJECTED│
              │_FILLED   │ │      │ │        │
              └────┬─────┘ └──────┘ └────────┘
                   │ 剩余部分  │          ▲
                   │ 撤单     │          │
                   ▼         │          │
              ┌──────────┐   │          │
              │CANCELLED │   │          │
              └──────────┘   │          │
                             │          │
              ┌──────────┐   │          │
              │CANCELLED │◄──┘          │
              │ (partial)│              │
              └──────────┘              │
                                        │
                    ┌──────────┐         │
                    │CANCELLED │◄────────┘  ← 用户手动撤单
                    └──────────┘
```

### 状态定义

| 状态 | 含义 | 可操作 |
|------|------|--------|
| `PENDING` | 订单创建，尚未提交到券商 | cancel → CANCELLED; submit → SUBMITTED |
| `SUBMITTED` | 已发送交易所，等待成交 | cancel → CANCELLED; 部分成交 → PARTIAL_FILLED; 全部成交 → FILLED; 拒绝 → REJECTED |
| `PARTIAL_FILLED` | 部分成交，剩余部分仍在市场 | cancel_remaining → CANCELLED; 全部成交 → FILLED |
| `FILLED` | 全部成交（终态） | 无 |
| `CANCELLED` | 已撤单（终态） | 无 |
| `REJECTED` | 被交易所拒绝（终态），记录拒绝原因 | 无 |

### 订单数据库表

```sql
CREATE TABLE orders (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id           INTEGER,                -- 关联信号 ID (futures_signals 或 options_signals)
    signal_type         TEXT NOT NULL,            -- 'futures' / 'options'
    symbol              TEXT NOT NULL,            -- 品种代码
    contract            TEXT NOT NULL,            -- 合约代码
    direction           TEXT NOT NULL,            -- 'BUY' / 'SELL' / 'OPEN_LONG' / 'CLOSE_LONG' / 'OPEN_SHORT' / 'CLOSE_SHORT'
    order_type          TEXT NOT NULL DEFAULT 'LIMIT',  -- 'LIMIT' / 'MARKET' / 'STOP'
    price               REAL,                    -- 限价单价格（市价单为 NULL）
    volume              INTEGER NOT NULL,         -- 手数
    filled_volume       INTEGER DEFAULT 0,       -- 已成交手数
    status              TEXT NOT NULL DEFAULT 'PENDING',  -- 状态机当前状态
    strategy            TEXT NOT NULL,            -- 策略类型
    strategy_details    TEXT DEFAULT '{}',        -- 策略详情 JSON
    broker_order_id     TEXT DEFAULT '',          -- 券商端订单 ID
    broker              TEXT DEFAULT '',          -- 券商名称 ('sim' / 'tq' / 'ctp')
    reject_reason       TEXT DEFAULT '',          -- 拒绝原因
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_signal ON orders(signal_id);
CREATE INDEX idx_orders_symbol ON orders(symbol);
```

### 仓位表

```sql
CREATE TABLE positions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol          TEXT NOT NULL,
    contract        TEXT NOT NULL,
    direction       TEXT NOT NULL,           -- 'LONG' / 'SHORT'
    volume          INTEGER NOT NULL,        -- 持仓手数
    avg_entry_price REAL NOT NULL,           -- 平均开仓价
    current_price   REAL,                    -- 最新价
    unrealized_pnl  REAL DEFAULT 0,          -- 浮动盈亏
    realized_pnl    REAL DEFAULT 0,          -- 已实现盈亏
    strategy        TEXT NOT NULL,           -- 所属策略
    opened_at       TEXT DEFAULT (datetime('now')),
    closed_at       TEXT,                    -- 平仓时间（平仓后更新）
    is_active       INTEGER DEFAULT 1,       -- 1=持仓中, 0=已平仓
    UNIQUE(symbol, contract, direction, is_active)
);

CREATE INDEX idx_positions_active ON positions(is_active);
CREATE INDEX idx_positions_symbol ON positions(symbol);
```

### 成交记录表

```sql
CREATE TABLE trades (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,        -- 关联订单
    position_id     INTEGER,                 -- 关联持仓
    symbol          TEXT NOT NULL,
    contract        TEXT NOT NULL,
    direction       TEXT NOT NULL,
    price           REAL NOT NULL,
    volume          INTEGER NOT NULL,
    commission      REAL DEFAULT 0,          -- 手续费
    traded_at       TEXT DEFAULT (datetime('now')),
    broker_trade_id TEXT DEFAULT ''          -- 券商端成交 ID
);

CREATE INDEX idx_trades_order ON trades(order_id);
CREATE INDEX idx_trades_position ON trades(position_id);
```

---

## 5. 集成路线图

### 阶段 1: 风控哨兵 + 订单状态机（1 Cycle）

目标：风控系统和订单管理就绪，连接模拟交易器。

```text
Cycle 任务：
1. 创建 trading/ 包：__init__.py, models.py, db.py
2. 实现订单状态机（OrderManager）
3. 实现风控哨兵（Sentinel）— 三层防御
4. 实现模拟交易器（BrokerSim）
5. 实现仓位管理器（PositionManager）
6. 新增数据库表：orders / positions / trades / sentinel_config
7. 新增 Web 看板页面：风控状态、模拟持仓
8. 集成测试：信号 → 风控 → 订单状态机全链路
```

**产出：** 全链路模拟交易可运行，Web 看板可查看模拟持仓和盈亏。

### 阶段 2: 接入天勤 TQSdk（1-2 Cycles）

目标：连接真实市场数据 API，开通模拟交易账户。

```text
Cycle 1 任务：
1. 安装 TQSdk pip 包
2. 实现 BrokerTQ (broker_tq.py) — place_order / cancel / sync
3. 实现 MarketDataProvider — 实时行情接入
4. 实盘/模拟账户切换机制
5. 集成测试：模拟账户真实成交

Cycle 2 任务（如需）：
1. 异常处理强化 — 断线重连 / 超时 / 限流
2. 日志和监控 — 所有交易操作写 audit_log
3. Telegram 交易通知（开仓/平仓/止损/风控阻断）
```

**先接入天勤的原因：**
- TQSdk 是最轻量的交易 SDK（vs CTP 的复杂认证和网络环境）
- 提供模拟账户，零资金风险验证全链路
- 数据 + 交易同源，减少数据不一致
- 文档完善，独立开发者友好

### 阶段 3: 实盘运行（1 Cycle）

目标：最小资金实盘验证。

```text
Cycle 任务：
1. 账户注资（建议 5000-10000 元起始）
2. 配置实盘参数（天勤实盘账户）
3. 配置风控参数（更保守的初期设置）
4. 第一天手动监控交易执行
5. 参数微调（滑点、超时、异常处理）
```

### 阶段 4: CTP 接入（可选，2 Cycles）

目标：如果需要更低延迟或 CTP 特有功能（期权组合保证金、做市商接口等）。

```text
Cycle 1 任务：
1. 安装 CTP-Python SDK
2. 实现 BrokerCTP (broker_ctp.py)
3. 实现 Broker 路由层（根据品种/策略自动选择券商）

Cycle 2 任务：
1. 端到端测试（CTP 模拟环境）
2. 故障切换逻辑（TQ ↔ CTP 自动切换）
```

---

## 6. 关键决策记录（ADR）

### ADR-001：直接封装交易 API 而非使用 vnpy

- **状态：已决定**
- **背景：** 需要从信号系统走向实盘交易，接入 CTP/天勤等交易 API。
- **方案对比：**
  - vnpy：成熟但 300+ 依赖、独立进程、MongoDB 架构，与当前 SQLite 完全不兼容
  - 直接封装：零额外框架依赖，与当前架构完美匹配
- **决策：采用直接封装方案。** 独立开发者场景下，简单性是最重要的架构属性。
- **风险：** 自研风控和订单管理需要从零做到生产级。缓解措施：第 1 阶段只做模拟交易，逐步积累信任；风控哨兵设计为防御性（默认阻断，需显式放行）。
- **假设：** 中国期货市场单账户交易频率不会超过每天 5 笔订单（基于信号系统当前 ENTRY 产出率），自研系统完全够用。

### ADR-002：首期接入天勤 TQSdk 而非 CTP

- **状态：已决定**
- **背景：** 需要选择第一个实盘交易接口。
- **理由：**
  - 天勤提供模拟账户，零资金风险运行全链路验证
  - TQSdk 通过 WebSocket + REST 连接，不需要 CTP 的专线/前置机
  - 天勤提供完整的期货行情 + 期权链数据，可替代部分 AKShare 调用
  - CTP 认证流程复杂，需要期货公司营业部开通，独立开发者时间成本高
- **后续：** 资金量大或需要期权组合保证金时，再考虑 CTP。

### ADR-003：信号直接产生订单，不引入交易信号队列

- **状态：已决定**
- **背景：** 信号系统与交易系统之间的数据传递方式。
- **方案对比：**
  - 信号表轮询（当前选择）：TradingOrchestrator 定期扫描 signal 表，读取未执行信号
  - 消息队列（RabbitMQ/Redis）：信号系统发布，交易系统订阅
- **决策：采用 SQLite 轮询。** 当前信号产生频率低（全量扫描 3 分钟一次），每天 ENTRY 信号个位数。引入消息队列是在不需要的地方增加复杂度。
- **风险：** 轮询延迟取决于轮询间隔（设计为 30 秒）。对于日内交易信号，30 秒延迟可接受。如果未来需要亚秒级响应，可升级为 SQLite WAL 模式的 `NOTIFY` 或文件监听。

### ADR-004：风控默认阻断（Default Deny）

- **状态：已决定**
- **背景：** 风控哨兵的设计哲学。
- **设计：** 所有检查项默认阻断交易，仅当显式通过时才放行。检查失败时记录原因到 `sentinel_log` 表。
- **理由：** 信号系统初期 ENTRY 率低，误阻断的代价远小于误放行。独立开发者没有实时盯盘能力，防御性风控是必要的。
- **例外：** 已有持仓的止损/平仓信号不受风控限制。止损是最高优行动。

### ADR-005：初始资金策略 — 保守进入

- **状态：待 CFO 确认**
- **背景：** 最小可行资金量。
- **建议：**
  - 模拟交易阶段：零资金，验证全链路稳定性
  - 实盘 Phase 1（1-2 周）：5000 元，仅交易 1-2 个高信度品种（RB/Y/P）
  - Phase 2（3-4 周）：10000 元，扩展至 3 个品种
  - Phase 3（稳定后）：按策略表现逐步加仓
- **理由：** 信号系统当前 ENTRY 评分 0.30-0.40，未达到 0.55+ 的推送阈值。即使降低阈值，也需要实盘验证信号质量。初始资金应等于"能为策略验证支付的学费"。

---

## 7. 关键假设与风险登记

### 假设（如果这些不成立，需要重新评估架构）

| 假设 | 影响 |
|------|------|
| 信号系统 ENTRY 率 < 5 次/天 | 低频率下单系统完全够用；如果信号量激增，需加限流 |
| 天勤 TQSdk 稳定可用 | 如果 TQ 服务中断，需要 Broker 自动切换 |
| 单品种，非高频（持仓周期 1 天 ~ 1 周） | 如果转向高频，SQLite 锁和轮询延迟需要重新设计 |
| SQLite 足够处理交易记录 | 读写量很小，SQLite 完全胜任 |

### 风险登记

| 风险 | 概率 | 严重度 | 缓解措施 |
|------|------|--------|----------|
| 天勤 API 变更/下线 | 低 | 高 | Broker 抽象层设计为可插拔；同时了解 CTP 接入方案 |
| 信号质量差导致持续亏损 | 中 | 高 | 风控日亏损限额 5%；信号时效检查 15 分钟 |
| 网络中断导致订单状态未知 | 中 | 中 | 启动时查询未结订单；30 秒超时自动撤单 |
| SQLite 写入竞争（读多写少场景） | 低 | 中 | WAL 模式（已有）；定期 checkpoint |
| 账户权限问题（期货公司开户） | 中 | 中 | 先用天勤模拟账户跑通链路；同时准备 CTP 开户材料 |

---

## 附录 A：信号 ID → 订单的精确连接

当前信号系统的 `futures_signals` 和 `options_signals` 表都有自增 ID 和完整字段。订单通过 `signal_id + signal_type` 字段关联到具体信号。

```sql
-- 查询信号驱动的所有订单
SELECT o.*, fs.symbol, fs.signal_type, fs.score
FROM orders o
LEFT JOIN futures_signals fs ON o.signal_id = fs.id AND o.signal_type = 'futures'
WHERE o.signal_type = 'futures';
```

## 附录 B：配置变更

`config/settings.py` 新增配置项：

```python
# ── 交易执行配置 ──────────────────────────────────────────────
TRADING_ENABLED = False           # 总开关（False 时 TradingOrchestrator 仅模拟）
TRADING_BROKER = "sim"            # "sim" | "tq" | "ctp"
TRADING_POLL_INTERVAL = 30        # 信号轮询间隔（秒）
TRADING_INITIAL_CAPITAL = 5000    # 初始资金（元）
TRADING_MAX_DAILY_LOSS = 500      # 每日最大亏损
TRADING_MAX_DAILY_TRADES = 5      # 每日最大交易次数
TRADING_MAX_OPEN_POSITIONS = 3    # 最大同时持仓数
TRADING_MAX_SYMBOL_EXPOSURE = 0.4 # 单品种暴露上限
TRADING_SIGNAL_MAX_AGE = 15       # 信号有效时间（分钟）

# ── TQSdk 配置 ─────────────────────────────────────────────────
TQ_BROKER_ID = ""                 # 天勤账号
TQ_PASSWORD = ""                  # 天勤密码
TQ_ACCOUNT_ID = ""                # 天勤资金账号

# ── CTP 配置（预留）─────────────────────────────────────────────
CTP_BROKER_ID = ""                # 期货公司编码
CTP_PASSWORD = ""                 # 交易密码
CTP_APP_ID = ""                   # 应用 ID
CTP_AUTH_CODE = ""                # 授权码
CTP_FRONT_ADDR = ""               # 交易前置机地址
CTP_MD_FRONT_ADDR = ""            # 行情前置机地址