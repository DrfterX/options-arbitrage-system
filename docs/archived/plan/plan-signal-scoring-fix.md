# Plan: 信号评分系统 contract 匹配修复

**发现日期**: 2026-06-11  
**调查人**: Auto Company

---

## 目标

修复期货信号评分系统（`scorer.py`）导致大量信号被 score=0.30 阻塞的根本原因——contract 名称不匹配。

## 背景

共识中记录了"82 条今日信号全部 score=0.30"的问题。经全量数据分析，**实际更严重**：

| score | 条数 | 占比 | 说明 |
|-------|------|------|------|
| 0.60 | 29 | 0.3% | CU2607（全部重复，同一品种） |
| 0.40 | 329 | 3.5% | 加分项部分命中 |
| 0.30 | 8631 | 91.8% | **被Level2阻塞** |
| 0.00 | 412 | 4.4% | 周线N型不存在 |

## 根因分析

### `_get_all_main_contracts()` 返回大量纯品种名

当前代码（scorer.py:99-116）：

```sql
SELECT DISTINCT s.symbol, k.contract as contract_code
FROM symbols s
INNER JOIN (...) k ON s.symbol = k.symbol
WHERE s.has_options = 1
```

返回 62 个 `(symbol, contract_code)` 组合。其中约 52 个为**纯品种名**（contract_code = symbol，如 CU）。

### N 型结构 contract 命名不一致

| 周期 | 存储的 contract | 示例 |
|------|----------------|------|
| 周线(1w) | 纯品种名 **或** 具体合约名 | `CU` 或 `CU2607` |
| 日线(1d) | 纯品种名 **或** 具体合约名 | 同上 |
| 小时线(1h) | **仅**具体合约名 | `CU2607` |
| 15分钟(15m) | **仅**具体合约名 | `CU2607` |

### 评分链断裂点

当 `contract_code = 'CU'`（纯品种名）：

```
Level1: _get_active_n_structure(db, 'CU', 'CU', '1w')   → 找到 ✅ (周线存在纯品种名)
Level2: _get_active_n_structure(db, 'CU', 'CU', '1h')   → None ❌ (小时线只有 CU2607)
```

→ 89.3% 的信号堵在这一步。

### 修复验证

对 48 个有小时线 N 型的具体合约进行方向一致性检查：

| 结果 | 数量 |
|------|------|
| 方向一致（可过Level2） | **25** |
| 方向不一致（仍堵） | 23 |
| 无小时线数据 | 14 |

修复后能从 25 个品种获得有效信号，而非现在的只有 1 个（CU2607）。

---

## 修复步骤（单一 Cycle 可完成）

### Step 1：修改 `_get_all_main_contracts()` —— 排除纯品种名

**文件**: `futures/scorer.py`  
**修改位置**: `_get_all_main_contracts()` 函数的 SQL 查询（第 115 行附近）

```diff
WHERE s.has_options = 1
+  AND k.contract != s.symbol
```

### Step 2：添加信号去重（次要）

**文件**: `futures/scorer.py`  
**修改位置**: `_save_signal()` 函数

添加 `INSERT OR IGNORE` 或先查后插逻辑，防止同一天同一品种反复写入相同信号。

### Step 3：增加日志以验证修复

**文件**: `futures/scorer.py`  
**修改位置**: `scan_all_contracts()` 函数末尾

输出 "修复后品种数: X, 过Level1: Y, 过Level2: Z, 过Level3: W" 的汇总日志。

---

## 预期效果

- 信号总数从 ~9401 大幅减少（纯品种名噪声信号不再产生）
- score≥0.30 的信号全部来自可验证的具体合约
- CU2607（铜）应该保持 score=0.60
- 新增 a1 个品种（如 RB2609、M2609 等）可能获得 score=0.40~0.60

## 风险

1. **AO/BR/IF/IH/IM/LU/PF/PK/PR/PS/ZC 等 11 个品种只有纯品种名 klines** —— 修复后这些品种无信号输出。但它们本来也只有周线/日线 N 型，小时线不存在，无论怎样都只能 score=0.30。过滤掉反而减少噪声。
2. **信号总量大幅减少**可能从指标上看着"信号变少了"，但实质质量提高了。