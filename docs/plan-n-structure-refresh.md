# Plan: N 型结构动态重算机制

> 调研日期: 2026-06-20 | Cycle #27 — 线 C 第一步：链路调研

---

## 0. 结论概要

**N 型结构后端重算已在所有 API 请求前自动触发**，不是「缺失」的环节。存在的是 **数据新鲜度** 和 **重算效率** 两个实际问题。

30s 自动更新链路**实际已就位**：
```
前端 30s 轮询 → /api/n-structures → restructure_all_active() → 
incremental_update → dynamic_restructure → 返回最新结构
```

瓶颈：**基础 K 线数据更新频次偏低（30 分钟一次）**，导致 30s 轮询在大部分时间做「相同数据的重复重算」。

---

## 1. 完整数据链路

### 3 条自动触发路径（实际已存在）

| # | 触发路径 | 触发频率 | 触发方式 | 重算范围 | 数据源 |
|---|---------|---------|---------|---------|-------|
| **1** | **API 请求重算** | **每 30s**（前端轮询） | `_restructure_active_structures()` → `restructure_all_active()` | **全品种全周期** | DB 已有数据 |
| **2** | **Scheduler 采集后重算** | 每 30 分钟（交易时段） | `FuturesCollector.collect_all(trigger_restructure=True)` 结束后调用 `restructure_all_active()` | 全品种全周期 | AKShare 新拉数据 |
| **3** | **单品种采集钩子** | 每个品种采集完成后（saved > 0） | `collect_symbol()` 内 inline 调用 `restructure_active_for_symbol()` | **单品种单合约** | 该品种新写入的 K 线 |

### 时序图

```
                          ┌─ 每 30 分钟（交易日白天/夜盘）
                          │
            Scheduler ────┤  collect_all()  ──→  collect_symbol()
            (5min心跳)     │                      │
                          └─                     │
                                                 ├── fetch_klines()     ← AKShare(Sina API)
                                                 ├── _batch_insert()    → futures_klines 表
                                                 └── restructure_active_for_symbol()  ← 🔴 采集后触发（Path 3）
                                                       │
                                                       ├── incremental_update()   → futures_swing_points
                                                       ├── aggregate_klines()      → 1d→1w / 1m→3m
                                                       ├── detect_and_save()       ← ⏱ 限频 5s
                                                       ├── dynamic_restructure()   ← A 突破迁移
                                                       └── _reactive_idle_structures()
                                                             │
                                                             ▼
                                                      futures_n_structures 表 ← 更新结果
                                                             │
                                                             ▼
  前端 ── 30s setInterval ──→ /api/n-structures ──→ _restructure_active_structures()
                                                            │
                                                            └── restructure_all_active()
                                                                  (同上的完整重算链路)
                                                                       │
                                                                       ▼
                                                              响应 JSON ← 最新结构数据
                                                                       │
                                                                       ▼
                                                              前端全量重绘
                                                              (Canvas/innerHTML)

                                                                  ╔═══════════════╗
                                                                  ║  ⏱ 30 分钟   ║
                                                                  ║  采集间隔     ║
                                                                  ╚═══════════════╝
```

### 关键代码定位

**文件** | **内容** | **行号**
--------|---------|---------
`web/app.py` | `_restructure_active_structures()` → `restructure_all_active()` | L416-432
`web/app.py` | `GET /api/n-structures` 路由 → 调用上方 | L547-670
`web/app.py` | `GET /api/klines` 路由 → `restructure_active_for_symbol()` | L741-862
`web/scheduler.py` | 5min 心跳循环，30min 采集间隔 | L168-194
`futures/n_structure.py` | `restructure_all_active()` — 全品种入口 | L1191-1232
`futures/n_structure.py` | `restructure_active_for_symbol()` — 单品种全流程 | L1128-1188
`futures/n_structure.py` | `dynamic_restructure()` — 增量状态迁移 | L730-939
`futures/n_structure.py` | `detect_and_save()` — 全量扫描（限频 5s） | L477-601
`data/futures_collector.py` | 采集钩子：`restructure_active_for_symbol()` per symbol | L392-403
`futures_dashboard.html` | 30s setInterval fetch `/api/n-structures` | L2136-2151
`futures_dashboard.html` | K 线弹窗 30s setInterval（visibilitychange 暂停） | L1687-1775

---

## 2. 问题诊断

### 2.1 ✅ 已确认：重算触发链路本身完整

Path 1（API 30s 轮询）的完整路径：
```
浏览器 setInterval(30s)
  → fetch('/api/n-structures')
    → _restructure_active_structures(db)
      → restructure_all_active(db)         ← 全品种重算
        → [每个活跃品种]
          incremental_update()              ← 从 futures_klines 更新 swing points
          aggregate_klines()                ← 刷新 1d→1w 聚合
          detect_and_save(限频 5s)          ← 全量扫描找新结构
          dynamic_restructure()             ← 增量状态迁移
          _reactive_idle_structures()       ← 重新激活
      → 查询 futures_n_structures 表返回结果
    → 前端 render() 全量重绘
```

### 2.2 ⚠️ 实际问题 1：K 线数据新鲜度不足

**核心矛盾**：
- 前端 **30s 轮询** → 后端每次自动重算
- 但 **基础 K 线数据** 每 **30 分钟** 才从交易所拉取一次
- 30s 轮询的 59/60 次在相同数据上重复重算

**时序示例（日盘）**：
```
09:00   采集+重算     ← 数据是新的
09:00:30 重算         ← 数据不变，结果不变
09:01:00 重算         ← 同上
...                    ← 连续 58 次无效重算
09:30   采集+重算     ← 终于有新数据
```

**例外**：`dynamic_restructure()` 和 `_update_c_point()` 在数据不更新时也做有意义的工作（C 点滑动、IDLE→ACTIVE 重激活），这部分不是浪费。但 `detect_and_save()`（全量扫描）每次都在扫描不变的数据集。

### 2.3 ⚠️ 实际问题 2：API 请求触发全品种全量重算

每次 30s 轮询触发 `restructure_all_active()`（全品种 × 全周期）：
- 62 个品种 × 4 个周期（15m/1h/1d/1w）= 248 个组合
- 每个组合执行 `incremental_update()` + `detect_and_save()`（限频）+ `dynamic_restructure()`
- 估测每次耗时 200-500ms

### 2.4 与共识问题的对照

> **共识 User Directives → 🚨 P0 — N 型结构算法缺乏动态刷新机制**

**实际现状**：动态刷新机制是存在的（3 条路径），并非「缺失」。改进空间在于：

| 问题 | 实际状态 |
|------|---------|
| "行情更新后不自动重算" | ❌ 说法不准确 — K 线写入后 `restructure_active_for_symbol()` 即触发 |
| "需要手动刷新页面" | ❌ 不准确 — 30s 自动轮询已经存在 |
| "数据更新不够及时" | ✅ 确实 — 采集频次 30 分钟跟不上 K 线变化 |
| "重算粒度太粗" | ✅ 确实 — 每次都是全品种全量，可做增量优化 |

---

## 3. 改动方案对比

### 方案 A：增加采集频次（最简单）

**改动**：将 `REFRESH_INTERVALS.day/night` 从 30 分钟改为 5 分钟

**影响文件**：仅 `web/scheduler.py` | **风险**：低 | **耗时**：5 分钟

**优点**：一行改动
**缺点**：AKShare API 可能有隐性频率限制；30s 轮询仍有大量重复

### 方案 B：分离重算与采集（推荐第一步）

**思路**：新增 `incremental_restructure_only()` 跳过 `detect_and_save()` 全量扫描，然后 API 触发时调用这个轻量版。

```python
def incremental_restructure_only(symbol, contract, db):
    """仅增量重算：跳过 detect_and_save 全量扫描"""
    incremental_update(symbol, contract, db)        # 更新 swing points
    aggregate_klines(symbol, contract, db)           # 刷新周期聚合
    dynamic_restructure(symbol, contract, db)        # 增量迁移
    _reactive_idle_structures(symbol, contract, db)  # 重激活
```

**影响文件**：`futures/n_structure.py` | **风险**：低 | **耗时**：15-20 分钟

### 方案 C：新增轻量心跳线程（推荐第二步）

**思路**：在 `scheduler.py` 中新增 5s 间隔的增量重算循环，遍历活跃品种执行 `incremental_restructure_only()`。

**影响文件**：`web/scheduler.py` + `futures/n_structure.py` | **风险**：中 | **耗时**：15 分钟

**优点**：
- 重算粒度从 30s 降到 5s
- 独立于前端请求（无人访问也自动更新）
- 不触发全量扫描

### 方案 D：API 端点去重算（推荐第三步）

**思路**：API 端点改为只读 `futures_n_structures` 表，不再触发任何重算。所有重算由心跳线程负责。

**影响文件**：`web/app.py` | **风险**：中 | **耗时**：10 分钟

**优点**：API 响应更快
**缺点**：需要心跳线程先就位（否则前端永远拿不到新结构）

---

## 4. 推荐实施路径

### 分层实施（推荐方案 B → C → D）

```
Step B:  分离增量函数        → 15-20 min
    ↓
Step C:  新增 5s 心跳线程   → 15 min
    ↓
Step D:  API 去重算          → 10 min
```

### Step 设计

**Step C.1 — 分离 `incremental_restructure_only()`**
```markdown
在 n_structure.py 中新增函数：
- 调用: incremental_update → aggregate_klines → dynamic_restructure → _reactive_idle_structures
- 跳过: detect_and_save（全量扫描）
- 不限频：没有全量扫描操作

后续使用场景：
- API 触发的 30s 轮询
- 新增的 5s 心跳线程
- 采集钩子（Path 3）
```

**Step C.2 — 新增 5s 心跳线程**
```python
# web/scheduler.py 新增
def _start_incremental_restructure_loop(db):
    """每 5 秒对活跃品种执行增量重算"""
    while True:
        try:
            from futures.n_structure import restructure_all_active_incremental
            restructure_all_active_incremental(db)  # 全品种增量版本
        except Exception:
            pass
        time.sleep(5)
```

**Step C.3 — API 端点去重算**
- `/api/n-structures`、`/api/matrix` 等端点：移除 `_restructure_active_structures()` 调用
- 直接查询 `futures_n_structures` 表返回
- 依赖 Step C.2 的心跳线程持续重算

### 延迟收益 vs 风险矩阵

| 指标 | 当前 | Step C.1 | +Step C.2 | +Step C.3 |
|------|------|----------|-----------|-----------|
| 重算粒度 | 30s（纯靠前端轮询） | 30s | **5s** ✅ | 5s |
| K 线数据源更新频次 | 30 分钟 | 30 分钟 | 30 分钟 | 30 分钟 |
| N 型状态机响应速度 | 30s | 30s | **5s** ✅ | 5s |
| API 响应速度 | 慢（含重算） | **快**（增量轻量）✅ | 不变 | **最快**（纯读表） |
| 实现复杂度 | — | 低 | 低-中 | 低 |

---

## 5. 建议的 Next Action

```markdown
## Next Action
**P0 线 C — Step C.1 分离增量重算逻辑**（共 3 个 Cycle）

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| ⏳ **C.1** | **分离 incremental_restructure_only()** | 15-20min | n_structure.py 新函数 |
| C.2 | 新增 5s 心跳重算线程 | 15min | scheduler.py 新线程 |
| C.3 | API 端点去重算 | 10min | app.py 移除触发调用 |

**当前：Step C.1 — 从 restructure_active_for_symbol() 中分离增量路径**
- 在 n_structure.py 中新增 `incremental_restructure_only(symbol, contract, db)`
- 调用链: incremental_update → aggregate_klines → dynamic_restructure → _reactive_idle_structures
- 跳过 detect_and_save（全量扫描），不限频
- 新增 `restructure_all_active_incremental(db)` 包装函数
- 验证：原有 `restructure_active_for_symbol()` 不受影响
```

---

## 附录：核心代码参考

### restructure_active_for_symbol() 当前实现（L1128-1188）

```python
def restructure_active_for_symbol(symbol, contract, db):
    """单品种全流程重算"""
    # 1. 增量更新极值点
    incremental_update(symbol, contract, db)
    
    # 2. 刷新 1d→1w 聚合
    from futures.aggregator import aggregate_klines
    aggregate_klines(symbol, contract, db)
    
    # 3. 全量扫描（限频 5s）
    detect_and_save(symbol, contract, db)  # ← 这是最重的一步
    
    # 4. 增量状态迁移
    dynamic_restructure(symbol, contract, db)
    
    # 5. 重新激活 IDLE 结构
    _reactive_idle_structures(symbol, contract, db)
    
    # 6. 清扫失效结构
    _sweep_stale_structures(symbol, contract, db)
```

### 前端轮询代码（futures_dashboard.html L2136-2151）

```javascript
function loadNStructures() {
    fetch('/api/n-structures', { cache: 'no-cache' })
        .then(function(r) { return r.json(); })
        .then(renderNStructures)
        .catch(function() {});
}

setInterval(function() {
    if (document.hidden) return;
    loadNStructures();
}, 30000);
```
