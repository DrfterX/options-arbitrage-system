# N 型结构算法诊断报告

> **撰写**: Cycle #43 (2026-06-15) + Cycle #44 (2026-06-16 更新)
> **作者**: fullstack-dhh (源码逆向分析) + Cycle #44 补充
> **Reviewers**: cto-vogels (架构), critic-munger (风险)
> **关联**: User Directives → 🚨 P0 N 型结构算法缺乏动态刷新机制

---

## 1. 完整数据链路追踪

```
K线采集 (futures_collector) ──→ futures_klines 表
        ↓
聚合 (aggregator) ──→ 15m/1h/1d/1w K线
        ↓
MACD (macd.py)
        ↓
极值点检测 (swing_points.detect_swing_points) ──→ futures_swing_points 表
        ↓
N 型结构检测 (n_structure.detect_and_save) ──→ futures_n_structures 表
        ↓
N 型信号管道 (n_signal_pipeline.scan_symbol) ──→ 读取已保存结构 → 检测15m突破
        ↓
Web API (app.py api_matrix) ──→ 从 DB 读取结构 → JSON → 前端渲染
        ↓
前端 (futures_dashboard.html) ──→ Canvas 2D 绘制 K 线浮窗
```

**数据生产端**（刷新管线，由 orchestrator.data_refresh() 驱动）:
```
采集K线 → 聚合 → MACD → 极值点 → N型结构 (全集, 500行+代码)
```

**数据消费端**（信号扫描 + 前端显示）:
- n_signal_pipeline.py: 只读 `_get_active_n_structure()`，**不重新计算**
- app.py api_matrix: 直接查 `futures_n_structures` 表，**不重新计算**

---

## 2. 核心问题定位

### 问题 1：N 型结构的唯一刷新点是 `data_refresh()` — 且只在 orchestrator 全量扫描时触发

在 `orchestrator.py` 中，`data_refresh()` 是唯一调用 `detect_and_save()` 的地方：

```python
[5/5] 检测N型结构
for each (symbol, contract):
    for each timeframe (3m, 15m, 1h, 1d, 1w):
        detect_and_save(sym, contract, tf, db)
```

而 `data_refresh()` 只在 `run_futres_scan(refresh=True)` 和 `run_n_signal_scan(refresh=True)` 时执行。
auto-loop 配置 `LOOP_INTERVAL="30"`（每 30 秒？分钟？），**两次扫描之间 N 型结构完全静止**。

**结论**: 即使行情持续更新（K 线数据持续写入），N 型结构不变。

### 问题 2：`_get_active_n_structure()` 的"新鲜度检查"有致命盲区

```python
def _get_active_n_structure(db, symbol, contract, timeframe):
    # ✅ 时间新鲜度检查 — 大周期内有效
    # ✅ C 未突破 A 的检查 — 结构完全失效时返回 None
    # ✅ 收盘价未突破 A 的止损检查 — 极端行情保护
    # ❌ 未检查：A 是否已被新高/新低超越 → 应该结构迁移
    # ❌ 未检查：是否有新的极值点改变了结构格局
```

**橡胶2609 案例**（原文佐证）:
- 原始: A=18395(PEAK), B=17220(TROUGH), C=18440(新PEAK)
- `_get_active_n_structure()` 检查 C(18440) > A(18395) → ✅ 通过（C 没破 A，LONG 结构仍有效）
- **但真正的语义问题**: 当价格突破旧 A 时，A 应当向前迁移（B→新A, C→新B）

### 问题 3：`n_signal_pipeline.scan_symbol()` 从不触发结构重算

```
scan_symbol():
    1. _get_active_n_structure()   ← 只从 DB 读已保存的结构
    2. check_realtime_breakout()   ← 只检测突破
    3. 计算评分/推送               ← 不关心结构是否已过时
```

即使 swing_points 表有新极值点，`scan_symbol()` 也不调用 `detect_and_save()`。

### 问题 4：`detect_and_save()` 逻辑本身在静态分析下是正确的

```python
detect_and_save():
    1. 读取 swing_points (从 DB 拿最新 80 个极值点)
    2. 同向合并（连续同类型取最极端的）
    3. 从最新端往前滑窗找第一个有效的交替3点结构
    4. 保存到 futures_n_structures
```

如果 swing_points 已更新，`detect_and_save()` 能找到正确结构。**问题不是算法逻辑，而是它没有被频繁调用**。

### 问题 5（连带）：K 线绘制偏差

| 问题 | 根因 |
|------|------|
| 长上影十字 K 显示偏差 | `/api/klines` 读出的是完整的 OHLC 数据（来自 DB），绘制逻辑正确。但 N 型结构 A/B/C 点数据过期 → 用户看到老结构套新 K 线 → 感觉"绘制不准" |
| 实时周 K 线缺失 | 聚合器 `aggregator.py` 按完整交易周合并，当前未完成的周 K 线不会生成。需要增量聚合逻辑 |
| 日线浮窗最新 K 线显示一半 | `/api/klines` 返回已收盘的完整 K 线，未包含进行中的分时数据 |

**本质**: 这些都是算法层问题引起的前端表象。K 线绘制代码本身（Canvas 2D）逻辑正确。

### 问题 6（新发现 — Cycle #44）：自动调度管线已断 — launchd 路径指向旧目录

**整个 `data_refresh()` 管道从未被自动触发过**，原因是调度器的脚本路径指向旧目录。

**`com.auto-company.options-scan`**（每 30 分钟触发一次全量扫描的 launchd 任务）:

```
plist 路径: /Users/ayong/options_arbitrage_system/scripts/auto_scan.sh  ✗
实际项目:   /Users/ayong/projects/auto-company_test/projects/options_arbitrage_system/  ✓
```

`auto_scan.sh` 内硬编码 `PROJECT_DIR="/Users/ayong/options_arbitrage_system"`，Python 找不到模块。

**验证**: `launchctl list | grep options-scan` → exit code 78（路径或模块不可用）。

**这意味着 `detect_and_save()` 只在 Claude 手动触发 `run_futures_scan()` 时跑，其余时间结构静止。**

《橡胶2609 案例》的真实场景：
1. 某个时刻 Claude 手动触发扫描 → A=18395, B=17220 被保存
2. 行情继续更新（3m K线持续写入 DB）
3. 价格突破 18440 > 18395
4. **但 `detect_and_save()` 不在运行** → 结构永远是旧的
5. 用户访问面板 → 看到老结构套新 K 线 → "绘制有偏差"

**修复这个路径问题比实现 `dynamic_restructure()` 更紧迫，因为它恢复了整个管线的自动刷新。**

---

## 3. 诊断结论

| # | 问题 | 严重度 | 修复难度 |
|---|------|--------|---------|
| C.1 | N 型结构只在 `data_refresh()` 中刷新 | **致命** | 中 |
| C.2 | `_get_active_n_structure()` 无结构迁移检查 | **致命** | 低 |
| C.3 | 信号管道从不触发结构重算 | **致命** | 低 |
| C.4 | 无实时周 K 线（等周五收盘才生成） | 重要 | 低 |
| C.5 | 刷新机制无增量设计 | 重要 | 中 |

---

## 4. 修复方案概要

### 核心思路：在数据管线的末梢增加「结构新鲜度验证」步骤

```
现有管线:
  采集K线 → 聚合 → MACD → 极值点 → detect_and_save [结束]

改进管线:
  采集K线 → 聚合 → MACD → 极值点 → detect_and_save
                                    → dynamic_restructure [新增]
                                      ↑
                                  每次 API 访问/信号扫描也触发
```

### 新增函数：`dynamic_restructure(db, symbol, contract, timeframe)`

1. 读取当前活跃 N 型结构 + 最新 K 线
2. 检查 A 点是否被突破（LONG: 最新 high > A_price，SHORT: 最新 low < A_price）
3. 如突破 → 结构迁移：old_B → new_A, 新极值点 → new_B
4. 重新计算方向 + 状态
5. 更新 DB（同 `_save_n_structure` 路径）
6. 所有周期共用同一套逻辑

### 触发时机（三路保障）

| 时机 | 方式 | 说明 |
|------|------|------|
| ① `data_refresh()` 末尾 | 已有管线自动触发 | 当前周期的末尾加入，确保每次全量扫描都校验一次 |
| ② `/api/matrix` 和 `/` 路由 | API 层调用 | 每次前端拉取数据时触发轻量级校验 |
| ③ `scan_symbol()` 之前 | 信号扫描触发 | 在检查突破前先确保结构是最新的 |

### 刷新机制改进（与算法修复分开的独立改进）

1. **K 线浮窗增量刷新** — Canvas 只重绘最新数据，不整页刷新（前端 JS 已有局部更新能力）
2. **取消 1 分钟自动整页刷新** — 改为事件驱动（用户交互时刷新，不轮询）
3. **信号更新时触发全局刷新** — N 型结构变化时推送 WebSocket 或 SSE 通知

---

## 5. 修复步骤（5 步）

| 步 | 任务 | 文件 | 预期耗时 | 依赖 | 优先级 |
|----|------|------|---------|------|--------|
| 1 | **修复 launchd 路径 + 恢复自动调度** | `scripts/auto_scan.sh` | 5min | 无 | 🚨 P0 |
| 2 | 实现 `dynamic_restructure()` 函数 | `futures/n_structure.py` | 20min | 无 | 重要 |
| 3 | 在 `data_refresh()` 末尾集成调用 | `pipeline/orchestrator.py` | 5min | 步2 | 重要 |
| 4 | K 线显示修复 + 实时周 K 线 + 浮窗优化 | 多文件 | 20min | 步2 | 后续 |
| 5 | 多品种多周期验证修复效果 | 运行 + 观察 | 15min | 步1~4 | 验收 |

**总计**: 5 个 Cycle，每个 ≤ 20min

**Cycle #44 发现**: 步1（修复 launchd）比 `dynamic_restructure()` 更优先 — 
前者恢复 30 分钟自动 N 型刷新，后者增加实时性。应先进 Step 1 再进 Step 2。

---

## 6. 风险与边界条件

### 迁移逻辑边界
- **同向迁移**: 仅在趋势方向的价格超越 A 点时才迁移（LONG: price > A, SHORT: price < A）
- **反向迁移**: 如果价格反向突破 B（回到 A 的反方向），结构应标记为失效（COMPLETED + 清空）
- **最小结构长度**: 迁移后至少保留 3 个点（A→B→C），不足则等待

### 一致性保证
- `detect_and_save()`（全量）和 `dynamic_restructure()`（增量）使用同一套 `_save_n_structure()` 保存路径
- 两者不应互相覆盖：`dynamic_restructure()` 应该在 `detect_and_save()` 已正确输出时跳过

### 性能考虑
- `dynamic_restructure()` 只读取 1 条活跃结构 + 1 条最新 K 线 — O(1)
- 不会在 API 层造成可见延迟
- `data_refresh()` 中的调用已存在批量循环，不增加额外复杂度
