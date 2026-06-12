# K 线渲染链路分析报告

> 撰写时间: 2026-06-13 (Cycle #1)
> 目的: 定位「浮窗 K 线形态与标准行情软件不一致」的根因

## 一、完整链路概览

```
AKShare (数据源)
  → futures_collector.py (采集 & 3m聚合)
    → futures_klines SQLite 表 (原始 3m/15m/1h/1d 数据)
      → aggregator.py (3m→15m→1h→1d→1w 聚合)
        → futures_klines 表 (所有周期)
          → web/app.py /api/klines (REST API)
            → dashboard.html drawKline() (Canvas 渲染)
```

## 二、各环节深入分析

### 1. 数据源 — AKShare Sina 期货接口

**分钟线**: `ak.futures_zh_minute_sina(symbol=contract, period=period)`
- period="15" → 15分钟线, "60" → 60分钟线
- 需要具体合约代码（含年月后缀，如 RB2610）
- 返回 datetime, open, high, low, close, volume

**日线**: `ak.futures_zh_daily_sina(symbol=f"{symbol}0")`
- 使用主力连续合约（如 RB0）
- 返回 date, open, high, low, close, volume

**已知问题**:
- `futures_main_sina()` 在 2026-06-11 确认不可用（全线故障），已添加 DB 回退机制
- AKShare Sina 数据的 K 线收盘时间点可能与交易所官方对齐方式有差异
- 数据量有限（深交所最多返回 ~5000 条分钟线）

### 2. 采集 — `data/futures_collector.py`

**增量采集逻辑**:
- 查询 DB 最新时间戳 → 只拉取 `last_ts - 2h` 之后的数据
- 初始采集最近 7 天数据
- 3m 从 1m 聚合（`aggregate_3m_from_1m`），180 秒窗口对齐

**潜在问题**:
- `start_dt = datetime.fromtimestamp(last_ts, tz=MARKET_TZ) - timedelta(hours=2)`：减 2 小时可能遗漏边界
- 1m 数据只当 `timeframe == "1m"` 配置时才会采集，非默认周期

### 3. 聚合引擎 — `futures/aggregator.py`

**交易时段感知聚合** (v2 核心改进):
- 15m/1h：检测交易时段边界（上午休盘 10:15-10:30、午休 11:30-13:30、夜盘收盘→日盘开盘）
- 日线：按交易边界切分，非纯日历日
- 周线：UTC 周对齐（ISO 周）

**关键函数**: `_is_trading_boundary()`

**检查跨交易边界**:
1. 日期不同当天 → 检查是否在同一夜盘内
2. 同天 → 检查 5 个休盘区间
3. 夜盘收盘切分

**⚠️ 聚合层潜在问题**:
- `_is_trading_boundary()` 的逻辑非常复杂，可能有边界条件 bug
- 夜盘收盘后 → 日盘开盘前（03:00→09:00）的数据可能被错误地归入同一个日 K 线
- `_aggregate_bar()` 简单取首开/最高/最低/尾收/量和，如果分组错误，整根 K 线就错了
- 3m→15m 聚合使用 `(ts // period) * period` 时间对齐 + 边界检测，两组条件冲突可能导致分组错乱

### 4. API 层 — `web/app.py` `/api/klines`

```sql
SELECT k.timestamp, k.open, k.high, k.low, k.close, k.volume
FROM futures_klines k
INNER JOIN (
    SELECT symbol, timeframe, timestamp, MAX(rowid) as max_rowid
    FROM futures_klines
    WHERE symbol=? AND timeframe=?
    GROUP BY symbol, timeframe, timestamp
) sub ON k.rowid = sub.max_rowid
ORDER BY k.timestamp DESC
```

**去重逻辑**: 在 `(symbol, timeframe, timestamp)` 同组内取 `MAX(rowid)`（最后写入的行）
- ✅ 基本正确
- ⚠️ 但如果同一 timestamp 有不同 OHLC 值（如聚合后重新写入），只保留最后一条，可能导致数据丢失

**日线/周线去重逻辑**:
```python
if tf in ("1d", "1w"):
    seen = {}
    for bar in bars:
        dt = datetime.fromtimestamp(bar["t"])
        key = "YYYY-mm-dd" / "YYYY-Www"
        if key not in seen or bar["t"] > seen[key]["t"]:
            seen[key] = bar
    bars = sorted(seen.values(), key=lambda x: x["t"])
```
- 按日历日/周去重，非交易时段感知
- 保留同一天内的最新时间戳数据

### 5. 前端渲染 — `dashboard.html` `drawKline()`

**Canvas 原生绘制**（未使用 ECharts）：

**坐标映射**:
```javascript
var priceToY = function(p) { return 10 + (1 - (p - pmin) / prange) * (H - 30); };
```
- 上下留白 10px 顶部 / 20px 底部 (volume + 价格标签)
- 线性映射，基本正确

**K 线绘制**:
- 影线：垂直线 h→l
- 实体：fillRect 从 o→c（或 c→o，取决于涨跌）
- 颜色：涨红(`#f04438`) 跌绿(`#22c55e`) — 中国标准 ✅
- 成交量：底部缩放的条形，高度映射到 15px 最大

**⚠️ 渲染层关键问题**:

**问题 1: Bar 间距计算逻辑可疑**
```javascript
if (i > 0 && bar.t && bars[i-1].t) {
    var timeGap = bar.t - bars[i-1].t;
    var normalGap = (i > 1 && bars[i-1].t && bars[i-2].t) ? 
        (bars[i-1].t - bars[i-2].t) : gap * 5;
    x = (timeGap > normalGap * 2.5) 
        ? prevX + gap + Math.min(barW * 3, gap * 0.3) 
        : prevX + gap;
}
```
- `x = prevX + gap` 这个 `gap` 是 `chartW / bars.length` — 这是等间距分配，与时间无关
- 但时间断档时（如夜盘→次日夜盘），间距调整非常小（`Math.min(barW * 3, gap * 0.3)`），视觉上几乎看不出断档
- **标准行情软件会明显拉开断档间隔**，此处视觉差异是「形态不一致」的根因之一

**问题 2: 价格精度**
```javascript
ctx.fillText((pmax - (i / 4) * prange).toFixed(1), chartLeft - 4, y + 3);
```
- `toFixed(1)` 写死了 1 位小数。对于股指期货（如 IF，价格 5000+）1 位足够，但对贵金属（AU, 小数点后两位）不够精确
- 不同品种价格精度不同，写死可能导致价格标签与真实 OHLC 值不匹配

**问题 3: 成交量的时间戳展示**
- 浮窗只显示 `#根K线 | 最新: close`，没有时间轴

**问题 4: 无 N 型结构叠加**
- 浮窗标题显示 A/B/C 价格，但 K 线图上没有标注 N 型结构的 A/B/C 点位置
- 标准交易软件会在图上标记结构起点/终点

## 三、根因判断

### 可能性排序 (从高到低)

| 优先级 | 可能原因 | 影响范围 | 证据 |
|--------|---------|---------|------|
| **P0** | **聚合引擎边界条件 bug** | 所有周期的 K 线形态 | `_is_trading_boundary()` 逻辑复杂, 夜盘→日盘过渡可能分组错误 |
| **P0** | **数据源 vs 标准软件的 OHLC 差异** | 单根 K 线的开高低收 | AKShare Sina 的数据定义可能与交易所官方或主流软件的复权/对齐方式不同 |
| **P1** | **Canvas 坐标映射问题** | 浮窗显示 | `drawKline()` 的坐标计算可能存在品种特定的缩放误差 |
| **P2** | **API 去重丢失数据** | 部分时间窗口缺失 | `MAX(rowid)` 去重可能丢弃有效数据 |
| **P2** | **日线/周线按日历对齐** | 日线/周线 | 应按交易时段对齐而非自然日历日 |

### 最可能根因

**聚合引擎的 `_is_trading_boundary()` 在交易时段检测上有边界条件 bug，导致 3m→15m→1h→1d 的聚合分组错误**。例如：
- 夜盘收盘 @23:00 → 次日日盘 @09:00 之间，6 分钟线的数据（23:00-23:06 的零星数据）被归入错误的聚合分组
- 日线聚合按交易边界切分，如果边界检测少了某个品种的特殊夜盘时间，会导致整根日 K 线数据跨天

## 四、验证方案

### Step 1: 数据层验证（无需外部网站）
1. 直接从 DB 查询某个品种（如 AG、RB）的原始 3m 数据
2. 手动验证最近一根 15m/1h 的 OHLC 是否由正确的 3m 分组聚合生成
3. 对比 `futures_klines` 表中同一品种在同一时段的不同周期的 open/high/low/close

### Step 2: 对照验证
1. 从东方财富/同花顺网页获取同一品种同一周期的 K 线截图
2. 对比 DB 中对应周期最后 24 根 K 线的 OHLC 数据

### Step 3: 渲染验证
1. 用 ECharts 替代 Canvas 渲染同一 JSON 数据
2. 看形态是否改善（排除渲染层的干扰）

## 五、修复路径建议

### 短期修复（~1 Cycle）
1. 在 `aggregator.py` 中添加调试日志，输出每个聚合分组的起止时间
2. 针对怀疑有问题的品种（如 AG 或 RB），跑一次聚合并检查分组边界

### 中期改进（2-3 Cycles）
1. 重写 `_is_trading_boundary()` 为更简明的按品种查询交易时段表
2. 在前端加入 ECharts K 线备用渲染模式，与 Canvas 对照
3. 在 API 端加入时间轴标签，避免前端自行计算 bar 间距

### 长期（可选）
1. 从交易所官方 API 或另一个数据源获取 K 线，与 AKShare 做交叉验证
2. 建立 K 线形态自动化测试（与标准数据对比）
