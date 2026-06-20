# N 型结构算法全量验证报告 — P0 Step 1.1

> **生成时间**: 2026-06-19 09:42:39 CST
>
> 验证范围: 267 个品种-合约对 × 4 周期 = 1068 条目
> 验证方法: 模块函数 `_get_swing_points()` → `_merge_same_type()` → `_find_n_structure_forward()`
> → 4 条件检查符合 User Directives 定义

## 📊 整体统计

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 全部通过 | 630 | 59.0% |
| ❌ 有失败条件 | 213 | 19.9% |
| ⚠️ 数据不足 | 225 | 21.1% |
| **总计** | **1068** | **100%** |

### 📈 按周期统计

| 周期 | 通过 | 失败 | N/A | 合计 | 通过率 |
|------|------|------|-----|------|--------|
| 15m | 135 | 57 | 75 | 267 | 70% |
| 1h  | 148 | 44 | 75 | 267 | 77% |
| 1d  | 215 | 51 | 1 | 267 | 81% |
| 1w  | 132 | 61 | 74 | 267 | 68% |

**各周期失败条件分布:**

| 周期 | 失败总数 | C1 | C2 | C3 | C4 |
|------|----------|----|----|----|----|
| 15m | 57 | 0 | 0 | 0 | 57 |
| 1h  | 44 | 0 | 0 | 0 | 44 |
| 1d  | 51 | 0 | 0 | 0 | 51 |
| 1w  | 61 | 0 | 0 | 0 | 28 |

**失败品种按失败次数排序:**

| 品种 | 失败数 |
|------|--------|
| EB | 26 |
| Y | 25 |
| P | 23 |
| L | 22 |
| PG | 22 |
| RB | 20 |
| TA | 11 |
| I | 6 |
| CF | 4 |
| CJ | 4 |
| AG | 3 |
| C | 3 |
| JD | 3 |
| LH | 3 |
| SN | 3 |
| A | 2 |
| B | 2 |
| BU | 2 |
| FG | 2 |
| LC | 2 |
| NI | 2 |
| OI | 2 |
| SC | 2 |
| SP | 2 |
| AL | 1 |
| AU | 1 |
| BR | 1 |
| CS | 1 |
| CU | 1 |
| M | 1 |
| MA | 1 |
| PB | 1 |
| PR | 1 |
| PS | 1 |
| RM | 1 |
| RR | 1 |
| SA | 1 |
| SI | 1 |
| SM | 1 |
| SR | 1 |
| SS | 1 |

## ❌ 未通过验证的品种×周期

共 213 条:

### A — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4701.00 @ 06-16 14:30 |
| B 价 | 4647.00 @ 06-17 21:30 |
| C 价 | 4668.00 @ 06-18 09:15 |
| 最新价 | 4672.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 27) |
| A 索引 | 19 | C 索引 | 25 |

**极值点序列** (swing: 40, merged: 27):
```
  [ 0] TROUGH price= 4727.00 time= 06-10 13:30
  [ 1] PEAK   price= 4769.00 time= 06-10 21:15
  [ 2] TROUGH price= 4725.00 time= 06-11 09:30
  [ 3] PEAK   price= 4745.00 time= 06-11 10:00
  [ 4] TROUGH price= 4728.00 time= 06-11 10:30
  [ 5] PEAK   price= 4766.00 time= 06-11 14:30
  [ 6] TROUGH price= 4749.00 time= 06-11 21:15
  [ 7] PEAK   price= 4774.00 time= 06-11 21:30
  [ 8] TROUGH price= 4721.00 time= 06-12 10:00
  [ 9] PEAK   price= 4754.00 time= 06-12 11:30
  [10] TROUGH price= 4734.00 time= 06-12 13:45
  [11] PEAK   price= 4754.00 time= 06-12 21:00
  [12] TROUGH price= 4732.00 time= 06-12 21:15
  [13] PEAK   price= 4752.00 time= 06-12 22:00
  [14] TROUGH price= 4726.00 time= 06-15 09:15
  [15] PEAK   price= 4795.00 time= 06-15 09:45
  [16] TROUGH price= 4702.00 time= 06-16 09:15
  [17] PEAK   price= 4725.00 time= 06-16 10:00
  [18] TROUGH price= 4687.00 time= 06-16 14:00
  [19] PEAK   price= 4701.00 time= 06-16 14:30 ← A
  [20] TROUGH price= 4684.00 time= 06-16 21:15
  [21] PEAK   price= 4711.00 time= 06-16 22:00
  [22] TROUGH price= 4687.00 time= 06-17 09:30
  [23] PEAK   price= 4706.00 time= 06-17 10:45
  [24] TROUGH price= 4647.00 time= 06-17 21:30
  [25] PEAK   price= 4668.00 time= 06-18 09:15 ← C
  [26] TROUGH price= 4616.00 time= 06-18 11:30
```

**失败详情:**
```
  ❌ C4 最新(4672.00) < C(4668.00) = False
```
---

### A — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4661.00 @ 06-09 00:00 |
| B 价 | 4774.00 @ 06-11 13:30 |
| C 价 | 4721.00 @ 06-12 09:00 |
| 最新价 | 4622.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 35 (merge 后: 21) |
| A 索引 | 16 | C 索引 | 18 |

**极值点序列** (swing: 35, merged: 21):
```
  [ 0] TROUGH price= 4560.00 time= 03-31 00:00
  [ 1] PEAK   price= 4697.00 time= 04-01 00:00
  [ 2] TROUGH price= 4606.00 time= 04-03 00:00
  [ 3] PEAK   price= 4928.00 time= 04-09 09:15
  [ 4] TROUGH price= 4746.00 time= 04-20 00:00
  [ 5] PEAK   price= 5046.00 time= 04-22 09:15
  [ 6] TROUGH price= 4862.00 time= 04-27 00:00
  [ 7] PEAK   price= 5009.00 time= 05-06 00:00
  [ 8] TROUGH price= 4756.00 time= 05-11 13:45
  [ 9] PEAK   price= 4854.00 time= 05-13 09:15
  [10] TROUGH price= 4694.00 time= 05-18 00:00
  [11] PEAK   price= 4799.00 time= 05-19 13:45
  [12] TROUGH price= 4715.00 time= 05-21 09:15
  [13] PEAK   price= 4901.00 time= 05-25 00:00
  [14] TROUGH price= 4688.00 time= 05-29 13:45
  [15] PEAK   price= 4806.00 time= 06-03 00:00
  [16] TROUGH price= 4661.00 time= 06-09 00:00 ← A
  [17] PEAK   price= 4774.00 time= 06-11 13:30
  [18] TROUGH price= 4721.00 time= 06-12 09:00 ← C
  [19] PEAK   price= 4796.00 time= 06-15 00:00
  [20] TROUGH price= 4684.00 time= 06-16 13:45
```

**失败详情:**
```
  ❌ C4 最新(4622.00) > C(4721.00) = False
```
---

### AG — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 17554.00 @ 04-30 00:00 |
| B 价 | 22134.00 @ 05-14 00:00 |
| C 价 | 17850.00 @ 05-20 00:00 |
| 最新价 | 15622.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 60 (merge 后: 60) |
| A 索引 | 55 | C 索引 | 57 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] PEAK   price= 6343.00 time= 12-04 00:00
  [ 1] TROUGH price= 5803.00 time= 12-13 00:00
  [ 2] PEAK   price= 6131.00 time= 12-25 00:00
  [ 3] TROUGH price= 5828.00 time= 01-05 00:00
  [ 4] PEAK   price= 5995.00 time= 01-15 00:00
  [ 5] TROUGH price= 5743.00 time= 01-23 00:00
  [ 6] PEAK   price= 5982.00 time= 01-31 00:00
  [ 7] TROUGH price= 5768.00 time= 02-07 00:00
  [ 8] PEAK   price= 5992.00 time= 02-19 00:00
  [ 9] TROUGH price= 5843.00 time= 03-01 00:00
  [10] PEAK   price= 7790.00 time= 04-15 00:00
  [11] TROUGH price= 6926.00 time= 05-06 00:00
  [12] PEAK   price= 8733.00 time= 05-21 00:00
  [13] TROUGH price= 7560.00 time= 06-14 00:00
  [14] PEAK   price= 8185.00 time= 06-21 00:00
  [15] TROUGH price= 7571.00 time= 06-27 00:00
  [16] PEAK   price= 8333.00 time= 07-12 00:00
  [17] TROUGH price= 6835.00 time= 08-06 00:00
  [18] PEAK   price= 7686.00 time= 08-27 00:00
  [19] TROUGH price= 6884.00 time= 09-09 00:00
  [20] PEAK   price= 7958.00 time= 09-27 00:00
  [21] TROUGH price= 7427.00 time= 10-10 00:00
  [22] PEAK   price= 8443.00 time= 10-23 00:00
  [23] TROUGH price= 7476.00 time= 11-14 00:00
  [24] PEAK   price= 7875.00 time= 11-25 00:00
  [25] TROUGH price= 7460.00 time= 11-28 00:00
  [26] PEAK   price= 8029.00 time= 12-12 00:00
  [27] TROUGH price= 7365.00 time= 12-20 00:00
  [28] PEAK   price= 7924.00 time= 01-17 00:00
  [29] TROUGH price= 7607.00 time= 01-24 00:00
  [30] PEAK   price= 8286.00 time= 02-17 00:00
  [31] TROUGH price= 7822.00 time= 03-03 00:00
  [32] PEAK   price= 8444.00 time= 03-19 00:00
  [33] TROUGH price= 8142.00 time= 03-24 00:00
  [34] PEAK   price= 8545.00 time= 03-28 00:00
  [35] TROUGH price= 7535.00 time= 04-07 00:00
  [36] PEAK   price= 8380.00 time= 04-24 00:00
  [37] TROUGH price= 7944.00 time= 05-15 00:00
  [38] PEAK   price= 8342.00 time= 05-22 00:00
  [39] TROUGH price= 8166.00 time= 05-29 00:00
  [40] PEAK   price= 9075.00 time= 06-18 00:00
  [41] TROUGH price= 8561.00 time= 06-25 00:00
  [42] PEAK   price= 9526.00 time= 07-23 00:00
  [43] TROUGH price= 8885.00 time= 08-01 00:00
  [44] PEAK   price= 9368.00 time= 08-14 00:00
  [45] TROUGH price= 9031.00 time= 08-20 00:00
  [46] PEAK   price=12366.00 time= 10-17 00:00
  [47] TROUGH price=11001.00 time= 10-28 00:00
  [48] PEAK   price=12664.00 time= 11-13 00:00
  [49] TROUGH price=11661.00 time= 11-21 00:00
  [50] PEAK   price=32382.00 time= 01-30 00:00
  [51] TROUGH price=17900.00 time= 02-06 00:00
  [52] PEAK   price=24500.00 time= 03-03 00:00
  [53] TROUGH price=15070.00 time= 03-23 00:00
  [54] PEAK   price=20559.00 time= 04-20 00:00
  [55] TROUGH price=17554.00 time= 04-30 00:00 ← A
  [56] PEAK   price=22134.00 time= 05-14 00:00
  [57] TROUGH price=17850.00 time= 05-20 00:00 ← C
  [58] PEAK   price=19288.00 time= 05-25 00:00
  [59] TROUGH price=17455.00 time= 05-28 00:00
```

**失败详情:**
```
  ❌ C4 最新(15622.00) > C(17850.00) = False
```
---

### AG — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 15070.00 @ 03-17 00:00 |
| B 价 | 20559.00 @ 04-14 00:00 |
| C 价 | 17554.00 @ 04-28 00:00 |
| 最新价 | 15622.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 80 (merge 后: 80) |
| A 索引 | 76 | C 索引 | 78 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price= 4252.00 time= 01-14 00:00
  [ 1] PEAK   price= 4584.00 time= 02-18 00:00
  [ 2] TROUGH price= 2857.00 time= 03-17 00:00
  [ 3] PEAK   price= 3832.00 time= 04-14 00:00
  [ 4] TROUGH price= 3533.00 time= 04-21 00:00
  [ 5] PEAK   price= 4519.00 time= 05-26 00:00
  [ 6] TROUGH price= 4141.00 time= 06-16 00:00
  [ 7] PEAK   price= 6877.00 time= 08-11 00:00
  [ 8] TROUGH price= 4690.00 time= 09-22 00:00
  [ 9] PEAK   price= 5458.00 time= 11-03 00:00
  [10] TROUGH price= 4625.00 time= 11-24 00:00
  [11] PEAK   price= 5805.00 time= 12-15 00:00
  [12] TROUGH price= 5051.00 time= 01-12 00:00
  [13] PEAK   price= 6085.00 time= 02-02 00:00
  [14] TROUGH price= 4971.00 time= 03-30 00:00
  [15] PEAK   price= 5992.00 time= 05-18 00:00
  [16] TROUGH price= 5312.00 time= 06-15 00:00
  [17] PEAK   price= 5583.00 time= 07-06 00:00
  [18] TROUGH price= 4930.00 time= 08-17 00:00
  [19] PEAK   price= 5308.00 time= 09-07 00:00
  [20] TROUGH price= 4595.00 time= 09-28 00:00
  [21] PEAK   price= 5114.00 time= 10-19 00:00
  [22] TROUGH price= 4738.00 time= 11-02 00:00
  [23] PEAK   price= 5234.00 time= 11-09 00:00
  [24] TROUGH price= 4588.00 time= 12-07 00:00
  [25] PEAK   price= 4916.00 time= 12-21 00:00
  [26] TROUGH price= 4596.00 time= 01-04 00:00
  [27] PEAK   price= 5424.00 time= 03-08 00:00
  [28] TROUGH price= 4913.00 time= 04-06 00:00
  [29] PEAK   price= 5339.00 time= 04-12 00:00
  [30] TROUGH price= 4564.00 time= 05-10 00:00
  [31] PEAK   price= 4853.00 time= 05-24 00:00
  [32] TROUGH price= 4018.00 time= 07-12 00:00
  [33] PEAK   price= 4595.00 time= 08-09 00:00
  [34] TROUGH price= 4094.00 time= 08-30 00:00
  [35] PEAK   price= 5443.00 time= 12-13 00:00
  [36] TROUGH price= 5123.00 time= 01-03 00:00
  [37] PEAK   price= 5397.00 time= 01-31 00:00
  [38] TROUGH price= 4756.00 time= 03-07 00:00
  [39] PEAK   price= 5868.00 time= 05-04 00:00
  [40] TROUGH price= 5270.00 time= 05-23 00:00
  [41] PEAK   price= 5739.00 time= 06-06 00:00
  [42] TROUGH price= 5395.00 time= 06-27 00:00
  [43] PEAK   price= 5983.00 time= 07-18 00:00
  [44] TROUGH price= 5538.00 time= 08-08 00:00
  [45] PEAK   price= 6030.00 time= 09-12 00:00
  [46] TROUGH price= 5594.00 time= 10-10 00:00
  [47] PEAK   price= 6343.00 time= 11-28 00:00
  [48] TROUGH price= 5743.00 time= 01-23 00:00
  [49] PEAK   price= 7790.00 time= 04-09 00:00
  [50] TROUGH price= 6926.00 time= 04-30 00:00
  [51] PEAK   price= 8733.00 time= 05-21 00:00
  [52] TROUGH price= 7560.00 time= 06-11 00:00
  [53] PEAK   price= 8333.00 time= 07-09 00:00
  [54] TROUGH price= 6835.00 time= 08-06 00:00
  [55] PEAK   price= 7686.00 time= 08-27 00:00
  [56] TROUGH price= 6884.00 time= 09-03 00:00
  [57] PEAK   price= 8443.00 time= 10-22 00:00
  [58] TROUGH price= 7460.00 time= 11-26 00:00
  [59] PEAK   price= 8029.00 time= 12-10 00:00
  [60] TROUGH price= 7365.00 time= 12-17 00:00
  [61] PEAK   price= 8286.00 time= 02-11 00:00
  [62] TROUGH price= 7822.00 time= 02-25 00:00
  [63] PEAK   price= 8545.00 time= 03-25 00:00
  [64] TROUGH price= 7535.00 time= 04-01 00:00
  [65] PEAK   price= 8380.00 time= 04-22 00:00
  [66] TROUGH price= 7944.00 time= 05-13 00:00
  [67] PEAK   price= 9075.00 time= 06-17 00:00
  [68] TROUGH price= 8561.00 time= 06-24 00:00
  [69] PEAK   price= 9526.00 time= 07-22 00:00
  [70] TROUGH price= 8885.00 time= 07-29 00:00
  [71] PEAK   price=12366.00 time= 10-14 00:00
  [72] TROUGH price=11001.00 time= 10-28 00:00
  [73] PEAK   price=32382.00 time= 01-27 00:00
  [74] TROUGH price=17900.00 time= 02-03 00:00
  [75] PEAK   price=24500.00 time= 03-03 00:00
  [76] TROUGH price=15070.00 time= 03-17 00:00 ← A
  [77] PEAK   price=20559.00 time= 04-14 00:00
  [78] TROUGH price=17554.00 time= 04-28 00:00 ← C
  [79] PEAK   price=22134.00 time= 05-12 00:00
```

**失败详情:**
```
  ❌ C4 最新(15622.00) > C(17554.00) = False
```
---

### AG — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 16235.00 @ 06-09 11:00 |
| B 价 | 16564.00 @ 06-09 22:00 |
| C 价 | 16561.00 @ 06-16 10:00 |
| 最新价 | 16506.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 39) |
| A 索引 | 20 | C 索引 | 34 |

**极值点序列** (swing: 50, merged: 39):
```
  [ 0] TROUGH price=18530.00 time= 05-27 02:00
  [ 1] PEAK   price=18877.00 time= 05-27 09:15
  [ 2] TROUGH price=18011.00 time= 05-27 21:15
  [ 3] PEAK   price=18272.00 time= 05-28 02:30
  [ 4] TROUGH price=17470.00 time= 05-28 13:45
  [ 5] PEAK   price=18587.00 time= 05-29 09:15
  [ 6] TROUGH price=18061.00 time= 05-29 22:00
  [ 7] PEAK   price=18480.00 time= 05-29 23:00
  [ 8] TROUGH price=18147.00 time= 06-01 09:15
  [ 9] PEAK   price=18348.00 time= 06-01 10:00
  [10] TROUGH price=17851.00 time= 06-01 22:00
  [11] PEAK   price=18338.00 time= 06-02 09:15
  [12] TROUGH price=17995.00 time= 06-02 10:00
  [13] PEAK   price=18512.00 time= 06-02 14:00
  [14] TROUGH price=17758.00 time= 06-03 22:00
  [15] PEAK   price=17967.00 time= 06-04 09:15
  [16] TROUGH price=17650.00 time= 06-04 15:00
  [17] PEAK   price=18220.00 time= 06-04 21:15
  [18] TROUGH price=15974.00 time= 06-08 13:45
  [19] PEAK   price=16604.00 time= 06-08 21:15
  [20] TROUGH price=16235.00 time= 06-09 11:00 ← A
  [21] PEAK   price=16564.00 time= 06-09 22:00
  [22] TROUGH price=15452.00 time= 06-10 00:00
  [23] PEAK   price=15777.00 time= 06-10 02:30
  [24] TROUGH price=15245.00 time= 06-10 11:00
  [25] PEAK   price=15832.00 time= 06-10 22:00
  [26] TROUGH price=15107.00 time= 06-11 10:42
  [27] PEAK   price=16190.00 time= 06-12 09:00
  [28] TROUGH price=15683.00 time= 06-12 09:30
  [29] PEAK   price=16215.00 time= 06-12 11:00
  [30] TROUGH price=15903.00 time= 06-12 21:00
  [31] PEAK   price=17077.00 time= 06-15 10:45
  [32] TROUGH price=16823.00 time= 06-15 14:00
  [33] PEAK   price=17136.00 time= 06-15 21:15
  [34] TROUGH price=16561.00 time= 06-16 10:00 ← C
  [35] PEAK   price=17077.00 time= 06-16 21:15
  [36] TROUGH price=16655.00 time= 06-17 21:15
  [37] PEAK   price=17210.00 time= 06-18 02:00
  [38] TROUGH price=16376.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(16506.00) > C(16561.00) = False
```
---

### AL — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 23940.00 @ 06-18 01:00 |
| B 价 | 23830.00 @ 06-18 09:15 |
| C 价 | 23915.00 @ 06-18 10:45 |
| 最新价 | 23980.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 26) |
| A 索引 | 22 | C 索引 | 24 |

**极值点序列** (swing: 40, merged: 26):
```
  [ 0] PEAK   price=24095.00 time= 06-11 13:30
  [ 1] TROUGH price=23990.00 time= 06-11 14:30
  [ 2] PEAK   price=24150.00 time= 06-11 21:45
  [ 3] TROUGH price=24080.00 time= 06-11 22:15
  [ 4] PEAK   price=24250.00 time= 06-12 09:00
  [ 5] TROUGH price=24120.00 time= 06-12 09:30
  [ 6] PEAK   price=24290.00 time= 06-12 10:45
  [ 7] TROUGH price=24145.00 time= 06-12 14:45
  [ 8] PEAK   price=24360.00 time= 06-15 09:15
  [ 9] TROUGH price=23725.00 time= 06-16 09:15
  [10] PEAK   price=23885.00 time= 06-16 10:15
  [11] TROUGH price=23780.00 time= 06-16 14:00
  [12] PEAK   price=23925.00 time= 06-16 22:00
  [13] TROUGH price=23845.00 time= 06-16 22:30
  [14] PEAK   price=23925.00 time= 06-17 00:15
  [15] TROUGH price=23860.00 time= 06-17 09:15
  [16] PEAK   price=23950.00 time= 06-17 10:45
  [17] TROUGH price=23855.00 time= 06-17 11:00
  [18] PEAK   price=23920.00 time= 06-17 13:45
  [19] TROUGH price=23850.00 time= 06-17 14:45
  [20] PEAK   price=23950.00 time= 06-17 21:30
  [21] TROUGH price=23860.00 time= 06-17 23:00
  [22] PEAK   price=23940.00 time= 06-18 01:00 ← A
  [23] TROUGH price=23830.00 time= 06-18 09:15
  [24] PEAK   price=23915.00 time= 06-18 10:45 ← C
  [25] TROUGH price=23820.00 time= 06-18 11:15
```

**失败详情:**
```
  ❌ C4 最新(23980.00) < C(23915.00) = False
```
---

### AU — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 929.10 @ 03-23 00:00 |
| B 价 | 1074.44 @ 04-20 00:00 |
| C 价 | 996.12 @ 04-30 00:00 |
| 最新价 | 919.32 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 60 (merge 后: 60) |
| A 索引 | 55 | C 索引 | 57 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] PEAK   price=  486.48 time= 12-04 00:00
  [ 1] TROUGH price=  467.70 time= 12-12 00:00
  [ 2] PEAK   price=  485.38 time= 12-28 00:00
  [ 3] TROUGH price=  476.32 time= 01-25 00:00
  [ 4] PEAK   price=  485.18 time= 02-05 00:00
  [ 5] TROUGH price=  478.52 time= 02-23 00:00
  [ 6] PEAK   price=  511.66 time= 03-11 00:00
  [ 7] TROUGH price=  503.36 time= 03-18 00:00
  [ 8] PEAK   price=  588.28 time= 04-15 00:00
  [ 9] TROUGH price=  542.20 time= 05-06 00:00
  [10] PEAK   price=  582.44 time= 05-20 00:00
  [11] TROUGH price=  550.46 time= 05-24 00:00
  [12] PEAK   price=  565.62 time= 06-07 00:00
  [13] TROUGH price=  543.52 time= 06-14 00:00
  [14] PEAK   price=  561.96 time= 06-21 00:00
  [15] TROUGH price=  544.00 time= 06-27 00:00
  [16] PEAK   price=  585.84 time= 07-17 00:00
  [17] TROUGH price=  551.16 time= 07-26 00:00
  [18] PEAK   price=  575.38 time= 08-05 00:00
  [19] TROUGH price=  545.44 time= 08-06 00:00
  [20] PEAK   price=  578.88 time= 08-21 00:00
  [21] TROUGH price=  567.04 time= 09-09 00:00
  [22] PEAK   price=  602.30 time= 09-27 00:00
  [23] TROUGH price=  587.32 time= 10-10 00:00
  [24] PEAK   price=  639.48 time= 10-30 00:00
  [25] TROUGH price=  592.12 time= 11-15 00:00
  [26] PEAK   price=  632.06 time= 12-12 00:00
  [27] TROUGH price=  608.88 time= 12-19 00:00
  [28] PEAK   price=  691.76 time= 02-11 00:00
  [29] TROUGH price=  666.96 time= 03-03 00:00
  [30] PEAK   price=  712.10 time= 03-20 00:00
  [31] TROUGH price=  701.00 time= 04-07 00:00
  [32] PEAK   price=  836.30 time= 04-22 00:00
  [33] TROUGH price=  774.48 time= 04-24 00:00
  [34] PEAK   price=  809.88 time= 05-08 00:00
  [35] TROUGH price=  732.64 time= 05-15 00:00
  [36] PEAK   price=  790.00 time= 06-03 00:00
  [37] TROUGH price=  767.08 time= 06-09 00:00
  [38] PEAK   price=  801.14 time= 06-13 00:00
  [39] TROUGH price=  760.58 time= 06-30 00:00
  [40] PEAK   price=  782.24 time= 07-03 00:00
  [41] TROUGH price=  765.22 time= 07-09 00:00
  [42] PEAK   price=  794.00 time= 07-23 00:00
  [43] TROUGH price=  766.86 time= 07-31 00:00
  [44] PEAK   price=  788.92 time= 08-11 00:00
  [45] TROUGH price=  770.38 time= 08-20 00:00
  [46] PEAK   price= 1001.96 time= 10-21 00:00
  [47] TROUGH price=  893.64 time= 10-29 00:00
  [48] PEAK   price=  970.58 time= 11-14 00:00
  [49] TROUGH price=  920.50 time= 11-18 00:00
  [50] PEAK   price= 1024.00 time= 12-29 00:00
  [51] TROUGH price=  964.00 time= 12-31 00:00
  [52] PEAK   price= 1258.72 time= 01-29 00:00
  [53] TROUGH price= 1005.40 time= 02-02 00:00
  [54] PEAK   price= 1205.78 time= 03-03 00:00
  [55] TROUGH price=  929.10 time= 03-23 00:00 ← A
  [56] PEAK   price= 1074.44 time= 04-20 00:00
  [57] TROUGH price=  996.12 time= 04-30 00:00 ← C
  [58] PEAK   price= 1046.36 time= 05-08 00:00
  [59] TROUGH price=  959.08 time= 05-28 00:00
```

**失败详情:**
```
  ❌ C4 最新(919.32) > C(996.12) = False
```
---

### B — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3416.00 @ 01-13 00:00 |
| B 价 | 3994.00 @ 03-10 00:00 |
| C 价 | 3558.00 @ 04-14 00:00 |
| 最新价 | 3482.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 80 (merge 后: 80) |
| A 索引 | 75 | C 索引 | 77 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] PEAK   price= 2954.00 time= 04-16 00:00
  [ 1] TROUGH price= 2676.00 time= 04-30 00:00
  [ 2] PEAK   price= 3238.00 time= 06-04 00:00
  [ 3] TROUGH price= 2955.00 time= 07-09 00:00
  [ 4] PEAK   price= 3486.00 time= 09-03 00:00
  [ 5] TROUGH price= 3120.00 time= 09-24 00:00
  [ 6] PEAK   price= 3470.00 time= 10-22 00:00
  [ 7] TROUGH price= 3111.00 time= 12-03 00:00
  [ 8] PEAK   price= 3347.00 time= 12-24 00:00
  [ 9] TROUGH price= 2896.00 time= 03-10 00:00
  [10] PEAK   price= 3355.00 time= 03-24 00:00
  [11] TROUGH price= 2813.00 time= 05-12 00:00
  [12] PEAK   price= 3526.00 time= 07-21 00:00
  [13] TROUGH price= 3218.00 time= 08-04 00:00
  [14] PEAK   price= 3809.00 time= 09-15 00:00
  [15] TROUGH price= 3484.00 time= 09-29 00:00
  [16] PEAK   price= 3851.00 time= 10-09 00:00
  [17] TROUGH price= 3637.00 time= 10-27 00:00
  [18] PEAK   price= 3986.00 time= 11-17 00:00
  [19] TROUGH price= 3453.00 time= 12-08 00:00
  [20] PEAK   price= 4626.00 time= 01-12 00:00
  [21] TROUGH price= 4013.00 time= 01-19 00:00
  [22] PEAK   price= 4631.00 time= 02-18 00:00
  [23] TROUGH price= 3837.00 time= 03-30 00:00
  [24] PEAK   price= 4490.00 time= 05-11 00:00
  [25] TROUGH price= 4106.00 time= 05-18 00:00
  [26] PEAK   price= 4433.00 time= 06-01 00:00
  [27] TROUGH price= 3887.00 time= 06-15 00:00
  [28] PEAK   price= 4594.00 time= 07-13 00:00
  [29] TROUGH price= 4260.00 time= 08-03 00:00
  [30] PEAK   price= 4574.00 time= 08-10 00:00
  [31] TROUGH price= 4077.00 time= 08-24 00:00
  [32] PEAK   price= 4720.00 time= 09-22 00:00
  [33] TROUGH price= 3906.00 time= 11-09 00:00
  [34] PEAK   price= 4484.00 time= 12-21 00:00
  [35] TROUGH price= 4229.00 time= 01-25 00:00
  [36] PEAK   price= 5711.00 time= 02-22 00:00
  [37] TROUGH price= 4842.00 time= 03-29 00:00
  [38] PEAK   price= 5446.00 time= 04-19 00:00
  [39] TROUGH price= 4959.00 time= 05-10 00:00
  [40] PEAK   price= 5667.00 time= 06-07 00:00
  [41] TROUGH price= 4360.00 time= 07-05 00:00
  [42] PEAK   price= 5798.00 time= 10-11 00:00
  [43] TROUGH price= 4847.00 time= 12-20 00:00
  [44] PEAK   price= 5226.00 time= 01-03 00:00
  [45] TROUGH price= 3949.00 time= 03-21 00:00
  [46] PEAK   price= 4342.00 time= 04-18 00:00
  [47] TROUGH price= 3709.00 time= 05-30 00:00
  [48] PEAK   price= 5460.00 time= 08-22 00:00
  [49] TROUGH price= 4337.00 time= 10-24 00:00
  [50] PEAK   price= 4723.00 time= 11-07 00:00
  [51] TROUGH price= 4246.00 time= 12-05 00:00
  [52] PEAK   price= 4518.00 time= 12-26 00:00
  [53] TROUGH price= 3506.00 time= 02-27 00:00
  [54] PEAK   price= 4033.00 time= 03-19 00:00
  [55] TROUGH price= 3673.00 time= 04-16 00:00
  [56] PEAK   price= 4235.00 time= 05-21 00:00
  [57] TROUGH price= 3396.00 time= 08-13 00:00
  [58] PEAK   price= 3799.00 time= 09-24 00:00
  [59] TROUGH price= 3531.00 time= 10-15 00:00
  [60] PEAK   price= 3953.00 time= 11-05 00:00
  [61] TROUGH price= 3152.00 time= 12-17 00:00
  [62] PEAK   price= 3658.00 time= 02-25 00:00
  [63] TROUGH price= 3422.00 time= 04-01 00:00
  [64] PEAK   price= 3753.00 time= 04-08 00:00
  [65] TROUGH price= 3481.00 time= 05-20 00:00
  [66] PEAK   price= 3776.00 time= 06-17 00:00
  [67] TROUGH price= 3557.00 time= 07-08 00:00
  [68] PEAK   price= 3925.00 time= 08-19 00:00
  [69] TROUGH price= 3544.00 time= 09-23 00:00
  [70] PEAK   price= 3820.00 time= 11-11 00:00
  [71] TROUGH price= 3669.00 time= 11-18 00:00
  [72] PEAK   price= 3829.00 time= 12-09 00:00
  [73] TROUGH price= 3403.00 time= 12-16 00:00
  [74] PEAK   price= 3558.00 time= 01-06 00:00
  [75] TROUGH price= 3416.00 time= 01-13 00:00 ← A
  [76] PEAK   price= 3994.00 time= 03-10 00:00
  [77] TROUGH price= 3558.00 time= 04-14 00:00 ← C
  [78] PEAK   price= 3711.00 time= 04-21 00:00
  [79] TROUGH price= 3515.00 time= 05-12 00:00
```

**失败详情:**
```
  ❌ C4 最新(3482.00) > C(3558.00) = False
```
---

### B — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3541.00 @ 06-17 14:45 |
| B 价 | 3560.00 @ 06-17 21:15 |
| C 价 | 3545.00 @ 06-17 22:15 |
| 最新价 | 3537.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 29) |
| A 索引 | 24 | C 索引 | 26 |

**极值点序列** (swing: 40, merged: 29):
```
  [ 0] TROUGH price= 3454.00 time= 06-09 23:00
  [ 1] PEAK   price= 3509.00 time= 06-10 22:30
  [ 2] TROUGH price= 3492.00 time= 06-11 09:30
  [ 3] PEAK   price= 3524.00 time= 06-11 10:45
  [ 4] TROUGH price= 3509.00 time= 06-11 13:30
  [ 5] PEAK   price= 3528.00 time= 06-11 21:00
  [ 6] TROUGH price= 3505.00 time= 06-11 21:30
  [ 7] PEAK   price= 3516.00 time= 06-11 22:15
  [ 8] TROUGH price= 3493.00 time= 06-12 09:15
  [ 9] PEAK   price= 3519.00 time= 06-12 11:00
  [10] TROUGH price= 3493.00 time= 06-12 13:45
  [11] PEAK   price= 3518.00 time= 06-12 14:45
  [12] TROUGH price= 3488.00 time= 06-15 09:15
  [13] PEAK   price= 3519.00 time= 06-15 10:00
  [14] TROUGH price= 3493.00 time= 06-15 11:00
  [15] PEAK   price= 3510.00 time= 06-15 14:15
  [16] TROUGH price= 3481.00 time= 06-15 21:15
  [17] PEAK   price= 3520.00 time= 06-16 09:15
  [18] TROUGH price= 3495.00 time= 06-16 10:00
  [19] PEAK   price= 3514.00 time= 06-16 11:30
  [20] TROUGH price= 3494.00 time= 06-16 14:00
  [21] PEAK   price= 3550.00 time= 06-16 22:15
  [22] TROUGH price= 3525.00 time= 06-16 22:45
  [23] PEAK   price= 3559.00 time= 06-17 14:30
  [24] TROUGH price= 3541.00 time= 06-17 14:45 ← A
  [25] PEAK   price= 3560.00 time= 06-17 21:15
  [26] TROUGH price= 3545.00 time= 06-17 22:15 ← C
  [27] PEAK   price= 3561.00 time= 06-17 23:00
  [28] TROUGH price= 3519.00 time= 06-18 11:30
```

**失败详情:**
```
  ❌ C4 最新(3537.00) > C(3545.00) = False
```
---

### BR — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 12870.00 @ 12-24 00:00 |
| B 价 | 15215.00 @ 01-21 00:00 |
| C 价 | 15115.00 @ 04-07 00:00 |
| 最新价 | 12845.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 31 (merge 后: 30) |
| A 索引 | 13 | C 索引 | 27 |

**极值点序列** (swing: 31, merged: 30):
```
  [ 0] PEAK   price=14600.00 time= 09-05 00:00
  [ 1] TROUGH price=12390.00 time= 10-10 00:00
  [ 2] PEAK   price=12630.00 time= 11-28 00:00
  [ 3] TROUGH price=11385.00 time= 12-05 00:00
  [ 4] PEAK   price=12935.00 time= 12-26 00:00
  [ 5] TROUGH price=11855.00 time= 01-23 00:00
  [ 6] PEAK   price=14545.00 time= 03-12 00:00
  [ 7] TROUGH price=12675.00 time= 04-23 00:00
  [ 8] PEAK   price=16715.00 time= 06-11 00:00
  [ 9] TROUGH price=13795.00 time= 08-06 00:00
  [10] PEAK   price=16650.00 time= 10-08 00:00
  [11] TROUGH price=12580.00 time= 11-19 00:00
  [12] PEAK   price=13910.00 time= 12-10 00:00
  [13] TROUGH price=12870.00 time= 12-24 00:00 ← A
  [14] PEAK   price=15215.00 time= 01-21 00:00
  [15] TROUGH price=10715.00 time= 04-15 00:00
  [16] PEAK   price=12650.00 time= 05-13 00:00
  [17] TROUGH price=10595.00 time= 06-03 00:00
  [18] PEAK   price=11780.00 time= 06-17 00:00
  [19] TROUGH price=10880.00 time= 07-01 00:00
  [20] PEAK   price=12525.00 time= 07-22 00:00
  [21] TROUGH price=11315.00 time= 07-29 00:00
  [22] PEAK   price=12250.00 time= 09-02 00:00
  [23] TROUGH price= 9990.00 time= 11-04 00:00
  [24] PEAK   price=14150.00 time= 01-27 00:00
  [25] TROUGH price=12530.00 time= 02-10 00:00
  [26] PEAK   price=18565.00 time= 03-24 00:00
  [27] TROUGH price=15115.00 time= 04-07 00:00 ← C
  [28] PEAK   price=16680.00 time= 04-28 00:00
  [29] TROUGH price=13075.00 time= 06-09 00:00
```

**失败详情:**
```
  ❌ C4 最新(12845.00) > C(15115.00) = False
```
---

### BU — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4197.00 @ 05-14 09:15 |
| B 价 | 4434.00 @ 05-20 00:00 |
| C 价 | 4242.00 @ 06-03 00:00 |
| 最新价 | 3941.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 36 (merge 后: 22) |
| A 索引 | 13 | C 索引 | 17 |

**极值点序列** (swing: 36, merged: 22):
```
  [ 0] PEAK   price= 4403.00 time= 03-23 00:00
  [ 1] TROUGH price= 3845.00 time= 03-24 00:00
  [ 2] PEAK   price= 4400.00 time= 03-31 00:00
  [ 3] TROUGH price= 3970.00 time= 04-02 09:15
  [ 4] PEAK   price= 4300.00 time= 04-02 13:45
  [ 5] TROUGH price= 3773.00 time= 04-09 00:00
  [ 6] PEAK   price= 4041.00 time= 04-13 09:15
  [ 7] TROUGH price= 3846.00 time= 04-15 09:15
  [ 8] PEAK   price= 3961.00 time= 04-16 09:15
  [ 9] TROUGH price= 3799.00 time= 04-17 09:15
  [10] PEAK   price= 4336.00 time= 04-29 09:15
  [11] TROUGH price= 4031.00 time= 05-08 00:00
  [12] PEAK   price= 4284.00 time= 05-12 13:45
  [13] TROUGH price= 4197.00 time= 05-14 09:15 ← A
  [14] PEAK   price= 4434.00 time= 05-20 00:00
  [15] TROUGH price= 4093.00 time= 05-27 13:45
  [16] PEAK   price= 4418.00 time= 06-01 13:45
  [17] TROUGH price= 4242.00 time= 06-03 00:00 ← C
  [18] PEAK   price= 4555.00 time= 06-08 00:00
  [19] TROUGH price= 4386.00 time= 06-10 00:00
  [20] PEAK   price= 4586.00 time= 06-11 10:30
  [21] TROUGH price= 3928.00 time= 06-17 13:45
```

**失败详情:**
```
  ❌ C4 最新(3941.00) > C(4242.00) = False
```
---

### BU — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3773.00 @ 04-06 08:00 |
| B 价 | 4434.00 @ 05-18 08:00 |
| C 价 | 4093.00 @ 05-25 09:15 |
| 最新价 | 3941.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 10 (merge 后: 6) |
| A 索引 | 1 | C 索引 | 3 |

**极值点序列** (swing: 10, merged: 6):
```
  [ 0] PEAK   price= 4403.00 time= 03-16 08:00
  [ 1] TROUGH price= 3773.00 time= 04-06 08:00 ← A
  [ 2] PEAK   price= 4434.00 time= 05-18 08:00
  [ 3] TROUGH price= 4093.00 time= 05-25 09:15 ← C
  [ 4] PEAK   price= 4586.00 time= 06-08 09:15
  [ 5] TROUGH price= 3909.00 time= 06-15 09:15
```

**失败详情:**
```
  ❌ C4 最新(3941.00) > C(4093.00) = False
```
---

### C — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2307.00 @ 05-20 00:00 |
| B 价 | 2420.00 @ 06-17 00:00 |
| C 价 | 2337.00 @ 04-07 00:00 |
| 最新价 | 2335.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 80 (merge 后: 80) |
| A 索引 | 65 | C 索引 | 77 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] PEAK   price= 1895.00 time= 10-29 00:00
  [ 1] TROUGH price= 1814.00 time= 11-26 00:00
  [ 2] PEAK   price= 1910.00 time= 12-03 00:00
  [ 3] TROUGH price= 1873.00 time= 12-17 00:00
  [ 4] PEAK   price= 1950.00 time= 01-14 00:00
  [ 5] TROUGH price= 1900.00 time= 02-18 00:00
  [ 6] PEAK   price= 2109.00 time= 04-21 00:00
  [ 7] TROUGH price= 2013.00 time= 05-19 00:00
  [ 8] PEAK   price= 2149.00 time= 06-16 00:00
  [ 9] TROUGH price= 2076.00 time= 06-30 00:00
  [10] PEAK   price= 2629.00 time= 10-13 00:00
  [11] TROUGH price= 2492.00 time= 11-03 00:00
  [12] PEAK   price= 2692.00 time= 12-01 00:00
  [13] TROUGH price= 2556.00 time= 12-15 00:00
  [14] PEAK   price= 2930.00 time= 01-12 00:00
  [15] TROUGH price= 2704.00 time= 01-26 00:00
  [16] PEAK   price= 2855.00 time= 02-18 00:00
  [17] TROUGH price= 2593.00 time= 03-30 00:00
  [18] PEAK   price= 2887.00 time= 05-11 00:00
  [19] TROUGH price= 2655.00 time= 05-25 00:00
  [20] PEAK   price= 2768.00 time= 06-08 00:00
  [21] TROUGH price= 2502.00 time= 07-20 00:00
  [22] PEAK   price= 2632.00 time= 08-10 00:00
  [23] TROUGH price= 2429.00 time= 09-22 00:00
  [24] PEAK   price= 2736.00 time= 11-09 00:00
  [25] TROUGH price= 2617.00 time= 11-23 00:00
  [26] PEAK   price= 2756.00 time= 12-14 00:00
  [27] TROUGH price= 2660.00 time= 12-28 00:00
  [28] PEAK   price= 2932.00 time= 03-01 00:00
  [29] TROUGH price= 2820.00 time= 03-29 00:00
  [30] PEAK   price= 3046.00 time= 04-26 00:00
  [31] TROUGH price= 2548.00 time= 07-19 00:00
  [32] PEAK   price= 2865.00 time= 09-20 00:00
  [33] TROUGH price= 2742.00 time= 09-27 00:00
  [34] PEAK   price= 2900.00 time= 11-01 00:00
  [35] TROUGH price= 2800.00 time= 11-15 00:00
  [36] PEAK   price= 2944.00 time= 11-29 00:00
  [37] TROUGH price= 2726.00 time= 12-20 00:00
  [38] PEAK   price= 2910.00 time= 01-10 00:00
  [39] TROUGH price= 2758.00 time= 02-07 00:00
  [40] PEAK   price= 2882.00 time= 02-21 00:00
  [41] TROUGH price= 2495.00 time= 05-09 00:00
  [42] PEAK   price= 2797.00 time= 07-04 00:00
  [43] TROUGH price= 2679.00 time= 07-18 00:00
  [44] PEAK   price= 2819.00 time= 08-08 00:00
  [45] TROUGH price= 2610.00 time= 08-15 00:00
  [46] PEAK   price= 2746.00 time= 08-29 00:00
  [47] TROUGH price= 2482.00 time= 10-17 00:00
  [48] PEAK   price= 2580.00 time= 11-21 00:00
  [49] TROUGH price= 2317.00 time= 01-16 00:00
  [50] PEAK   price= 2479.00 time= 02-20 00:00
  [51] TROUGH price= 2381.00 time= 03-26 00:00
  [52] PEAK   price= 2443.00 time= 04-02 00:00
  [53] TROUGH price= 2370.00 time= 04-16 00:00
  [54] PEAK   price= 2520.00 time= 06-25 00:00
  [55] TROUGH price= 2250.00 time= 08-06 00:00
  [56] PEAK   price= 2357.00 time= 08-27 00:00
  [57] TROUGH price= 2105.00 time= 09-18 00:00
  [58] PEAK   price= 2254.00 time= 10-29 00:00
  [59] TROUGH price= 2035.00 time= 12-03 00:00
  [60] PEAK   price= 2325.00 time= 02-11 00:00
  [61] TROUGH price= 2260.00 time= 02-25 00:00
  [62] PEAK   price= 2336.00 time= 03-04 00:00
  [63] TROUGH price= 2244.00 time= 03-25 00:00
  [64] PEAK   price= 2389.00 time= 05-06 00:00
  [65] TROUGH price= 2307.00 time= 05-20 00:00 ← A
  [66] PEAK   price= 2420.00 time= 06-17 00:00
  [67] TROUGH price= 2274.00 time= 07-15 00:00
  [68] PEAK   price= 2335.00 time= 07-22 00:00
  [69] TROUGH price= 2147.00 time= 08-19 00:00
  [70] PEAK   price= 2234.00 time= 09-09 00:00
  [71] TROUGH price= 2089.00 time= 10-09 00:00
  [72] PEAK   price= 2310.00 time= 12-02 00:00
  [73] TROUGH price= 2183.00 time= 12-23 00:00
  [74] PEAK   price= 2314.00 time= 01-20 00:00
  [75] TROUGH price= 2258.00 time= 01-27 00:00
  [76] PEAK   price= 2443.00 time= 03-03 00:00
  [77] TROUGH price= 2337.00 time= 04-07 00:00 ← C
  [78] PEAK   price= 2445.00 time= 04-21 00:00
  [79] TROUGH price= 2291.00 time= 06-02 00:00
```

**失败详情:**
```
  ❌ C4 最新(2335.00) > C(2337.00) = False
```
---

### C — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 2336.00 @ 06-17 21:15 |
| B 价 | 2321.00 @ 06-18 09:15 |
| C 价 | 2334.00 @ 06-18 10:15 |
| 最新价 | 2337.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 25) |
| A 索引 | 22 | C 索引 | 24 |

**极值点序列** (swing: 40, merged: 25):
```
  [ 0] PEAK   price= 2347.00 time= 06-10 10:00
  [ 1] TROUGH price= 2333.00 time= 06-10 13:30
  [ 2] PEAK   price= 2339.00 time= 06-10 21:00
  [ 3] TROUGH price= 2331.00 time= 06-10 22:45
  [ 4] PEAK   price= 2344.00 time= 06-11 10:45
  [ 5] TROUGH price= 2339.00 time= 06-11 11:15
  [ 6] PEAK   price= 2355.00 time= 06-11 21:15
  [ 7] TROUGH price= 2342.00 time= 06-11 22:45
  [ 8] PEAK   price= 2350.00 time= 06-12 09:15
  [ 9] TROUGH price= 2345.00 time= 06-12 10:00
  [10] PEAK   price= 2353.00 time= 06-12 13:45
  [11] TROUGH price= 2337.00 time= 06-12 21:00
  [12] PEAK   price= 2348.00 time= 06-12 22:00
  [13] TROUGH price= 2318.00 time= 06-15 14:45
  [14] PEAK   price= 2331.00 time= 06-15 22:15
  [15] TROUGH price= 2325.00 time= 06-16 09:15
  [16] PEAK   price= 2333.00 time= 06-16 09:30
  [17] TROUGH price= 2324.00 time= 06-16 21:15
  [18] PEAK   price= 2335.00 time= 06-16 21:30
  [19] TROUGH price= 2327.00 time= 06-17 10:00
  [20] PEAK   price= 2331.00 time= 06-17 13:45
  [21] TROUGH price= 2328.00 time= 06-17 14:15
  [22] PEAK   price= 2336.00 time= 06-17 21:15 ← A
  [23] TROUGH price= 2321.00 time= 06-18 09:15
  [24] PEAK   price= 2334.00 time= 06-18 10:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(2337.00) < C(2334.00) = False
```
---

### C — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 2353.00 @ 06-12 13:30 |
| B 价 | 2318.00 @ 06-15 14:00 |
| C 价 | 2335.00 @ 06-16 21:15 |
| 最新价 | 2337.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 37) |
| A 索引 | 30 | C 索引 | 32 |

**极值点序列** (swing: 50, merged: 37):
```
  [ 0] PEAK   price= 2343.00 time= 05-22 22:00
  [ 1] TROUGH price= 2311.00 time= 05-26 09:15
  [ 2] PEAK   price= 2327.00 time= 05-26 10:00
  [ 3] TROUGH price= 2311.00 time= 05-26 21:15
  [ 4] PEAK   price= 2324.00 time= 05-27 10:00
  [ 5] TROUGH price= 2305.00 time= 05-27 21:15
  [ 6] PEAK   price= 2334.00 time= 05-29 11:00
  [ 7] TROUGH price= 2317.00 time= 05-29 14:00
  [ 8] PEAK   price= 2329.00 time= 05-29 21:15
  [ 9] TROUGH price= 2317.00 time= 06-01 09:15
  [10] PEAK   price= 2336.00 time= 06-02 13:45
  [11] TROUGH price= 2322.00 time= 06-02 22:00
  [12] PEAK   price= 2335.00 time= 06-03 10:00
  [13] TROUGH price= 2291.00 time= 06-04 09:15
  [14] PEAK   price= 2332.00 time= 06-05 13:45
  [15] TROUGH price= 2315.00 time= 06-05 22:00
  [16] PEAK   price= 2331.00 time= 06-08 09:15
  [17] TROUGH price= 2321.00 time= 06-08 14:00
  [18] PEAK   price= 2344.00 time= 06-08 23:00
  [19] TROUGH price= 2334.00 time= 06-09 11:00
  [20] PEAK   price= 2347.00 time= 06-10 09:12
  [21] TROUGH price= 2333.00 time= 06-10 13:30
  [22] PEAK   price= 2341.00 time= 06-10 14:15
  [23] TROUGH price= 2331.00 time= 06-10 21:00
  [24] PEAK   price= 2344.00 time= 06-11 10:30
  [25] TROUGH price= 2338.00 time= 06-11 11:15
  [26] PEAK   price= 2355.00 time= 06-11 21:00
  [27] TROUGH price= 2342.00 time= 06-11 22:00
  [28] PEAK   price= 2351.00 time= 06-12 10:30
  [29] TROUGH price= 2345.00 time= 06-12 11:15
  [30] PEAK   price= 2353.00 time= 06-12 13:30 ← A
  [31] TROUGH price= 2318.00 time= 06-15 14:00
  [32] PEAK   price= 2335.00 time= 06-16 21:15 ← C
  [33] TROUGH price= 2327.00 time= 06-17 10:00
  [34] PEAK   price= 2336.00 time= 06-17 21:15
  [35] TROUGH price= 2321.00 time= 06-18 09:15
  [36] PEAK   price= 2338.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(2337.00) < C(2335.00) = False
```
---

### CF — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 15170.00 @ 04-03 00:00 |
| B 价 | 16955.00 @ 05-06 00:00 |
| C 价 | 15855.00 @ 05-22 00:00 |
| 最新价 | 15675.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 60 (merge 后: 60) |
| A 索引 | 56 | C 索引 | 58 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] TROUGH price=15315.00 time= 01-09 00:00
  [ 1] PEAK   price=16450.00 time= 02-28 00:00
  [ 2] TROUGH price=15865.00 time= 03-12 00:00
  [ 3] PEAK   price=16210.00 time= 03-18 00:00
  [ 4] TROUGH price=15810.00 time= 03-28 00:00
  [ 5] PEAK   price=16480.00 time= 04-11 00:00
  [ 6] TROUGH price=14840.00 time= 05-15 00:00
  [ 7] PEAK   price=15630.00 time= 05-29 00:00
  [ 8] TROUGH price=14340.00 time= 06-18 00:00
  [ 9] PEAK   price=14880.00 time= 07-02 00:00
  [10] TROUGH price=14380.00 time= 07-10 00:00
  [11] PEAK   price=14785.00 time= 07-16 00:00
  [12] TROUGH price=13990.00 time= 07-25 00:00
  [13] PEAK   price=14245.00 time= 08-01 00:00
  [14] TROUGH price=13200.00 time= 08-19 00:00
  [15] PEAK   price=13940.00 time= 09-04 00:00
  [16] TROUGH price=13220.00 time= 09-09 00:00
  [17] PEAK   price=14755.00 time= 10-08 00:00
  [18] TROUGH price=13920.00 time= 10-17 00:00
  [19] PEAK   price=14245.00 time= 10-24 00:00
  [20] TROUGH price=13860.00 time= 11-07 00:00
  [21] PEAK   price=14250.00 time= 11-08 00:00
  [22] TROUGH price=13835.00 time= 11-18 00:00
  [23] PEAK   price=14085.00 time= 11-29 00:00
  [24] TROUGH price=13315.00 time= 12-19 00:00
  [25] PEAK   price=13600.00 time= 01-03 00:00
  [26] TROUGH price=13330.00 time= 01-06 00:00
  [27] PEAK   price=13930.00 time= 02-21 00:00
  [28] TROUGH price=13450.00 time= 03-06 00:00
  [29] PEAK   price=13735.00 time= 03-13 00:00
  [30] TROUGH price=13540.00 time= 03-18 00:00
  [31] PEAK   price=13690.00 time= 04-02 00:00
  [32] TROUGH price=12315.00 time= 04-09 00:00
  [33] PEAK   price=13080.00 time= 04-25 00:00
  [34] TROUGH price=12675.00 time= 05-06 00:00
  [35] PEAK   price=13560.00 time= 05-21 00:00
  [36] TROUGH price=13200.00 time= 06-04 00:00
  [37] PEAK   price=13600.00 time= 06-11 00:00
  [38] TROUGH price=13425.00 time= 06-23 00:00
  [39] PEAK   price=13920.00 time= 06-30 00:00
  [40] TROUGH price=13685.00 time= 07-09 00:00
  [41] PEAK   price=14375.00 time= 07-18 00:00
  [42] TROUGH price=13535.00 time= 08-01 00:00
  [43] PEAK   price=14235.00 time= 08-13 00:00
  [44] TROUGH price=13940.00 time= 08-20 00:00
  [45] PEAK   price=14340.00 time= 08-29 00:00
  [46] TROUGH price=13155.00 time= 09-30 00:00
  [47] PEAK   price=13675.00 time= 10-30 00:00
  [48] TROUGH price=13380.00 time= 11-18 00:00
  [49] PEAK   price=15095.00 time= 01-07 00:00
  [50] TROUGH price=14395.00 time= 01-20 00:00
  [51] PEAK   price=15005.00 time= 01-29 00:00
  [52] TROUGH price=14500.00 time= 02-02 00:00
  [53] PEAK   price=15765.00 time= 03-13 00:00
  [54] TROUGH price=15035.00 time= 03-20 00:00
  [55] PEAK   price=15540.00 time= 04-01 00:00
  [56] TROUGH price=15170.00 time= 04-03 00:00 ← A
  [57] PEAK   price=16955.00 time= 05-06 00:00
  [58] TROUGH price=15855.00 time= 05-22 00:00 ← C
  [59] PEAK   price=16440.00 time= 06-03 00:00
```

**失败详情:**
```
  ❌ C4 最新(15675.00) > C(15855.00) = False
```
---

### CF — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 15035.00 @ 03-17 00:00 |
| B 价 | 16955.00 @ 05-06 00:00 |
| C 价 | 15855.00 @ 05-19 00:00 |
| 最新价 | 15675.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 80 (merge 后: 80) |
| A 索引 | 76 | C 索引 | 78 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price=12075.00 time= 08-06 00:00
  [ 1] PEAK   price=13285.00 time= 09-10 00:00
  [ 2] TROUGH price=11970.00 time= 09-24 00:00
  [ 3] PEAK   price=13215.00 time= 10-29 00:00
  [ 4] TROUGH price=12580.00 time= 11-19 00:00
  [ 5] PEAK   price=14450.00 time= 01-14 00:00
  [ 6] TROUGH price=12130.00 time= 02-04 00:00
  [ 7] PEAK   price=13510.00 time= 02-11 00:00
  [ 8] TROUGH price= 9935.00 time= 03-24 00:00
  [ 9] PEAK   price=11750.00 time= 04-07 00:00
  [10] TROUGH price=10855.00 time= 04-21 00:00
  [11] PEAK   price=12155.00 time= 06-02 00:00
  [12] TROUGH price=11600.00 time= 06-23 00:00
  [13] PEAK   price=13180.00 time= 08-25 00:00
  [14] TROUGH price=12215.00 time= 09-08 00:00
  [15] PEAK   price=15305.00 time= 10-13 00:00
  [16] TROUGH price=13920.00 time= 11-03 00:00
  [17] PEAK   price=15610.00 time= 01-05 00:00
  [18] TROUGH price=14735.00 time= 01-26 00:00
  [19] PEAK   price=17080.00 time= 02-23 00:00
  [20] TROUGH price=14285.00 time= 03-23 00:00
  [21] PEAK   price=16355.00 time= 05-11 00:00
  [22] TROUGH price=15300.00 time= 05-25 00:00
  [23] PEAK   price=16160.00 time= 06-08 00:00
  [24] TROUGH price=15400.00 time= 06-22 00:00
  [25] PEAK   price=18505.00 time= 08-17 00:00
  [26] TROUGH price=17030.00 time= 09-22 00:00
  [27] PEAK   price=22960.00 time= 10-12 00:00
  [28] TROUGH price=18935.00 time= 11-30 00:00
  [29] PEAK   price=22210.00 time= 02-07 00:00
  [30] TROUGH price=20640.00 time= 02-22 00:00
  [31] PEAK   price=22000.00 time= 03-22 00:00
  [32] TROUGH price=20995.00 time= 04-26 00:00
  [33] PEAK   price=22035.00 time= 05-05 00:00
  [34] TROUGH price=13560.00 time= 07-12 00:00
  [35] PEAK   price=15790.00 time= 08-16 00:00
  [36] TROUGH price=13195.00 time= 09-27 00:00
  [37] PEAK   price=13975.00 time= 10-11 00:00
  [38] TROUGH price=12270.00 time= 10-25 00:00
  [39] PEAK   price=15275.00 time= 01-31 00:00
  [40] TROUGH price=14085.00 time= 02-14 00:00
  [41] PEAK   price=14780.00 time= 02-28 00:00
  [42] TROUGH price=13715.00 time= 03-14 00:00
  [43] PEAK   price=17070.00 time= 06-06 00:00
  [44] TROUGH price=16120.00 time= 06-27 00:00
  [45] PEAK   price=17530.00 time= 08-01 00:00
  [46] TROUGH price=16585.00 time= 08-15 00:00
  [47] PEAK   price=17905.00 time= 08-29 00:00
  [48] TROUGH price=16910.00 time= 09-12 00:00
  [49] PEAK   price=17815.00 time= 10-09 00:00
  [50] TROUGH price=14740.00 time= 11-28 00:00
  [51] PEAK   price=16450.00 time= 02-27 00:00
  [52] TROUGH price=15810.00 time= 03-26 00:00
  [53] PEAK   price=16480.00 time= 04-09 00:00
  [54] TROUGH price=14840.00 time= 05-14 00:00
  [55] PEAK   price=15630.00 time= 05-28 00:00
  [56] TROUGH price=14340.00 time= 06-18 00:00
  [57] PEAK   price=14880.00 time= 07-02 00:00
  [58] TROUGH price=13200.00 time= 08-13 00:00
  [59] PEAK   price=14755.00 time= 10-08 00:00
  [60] TROUGH price=13920.00 time= 10-15 00:00
  [61] PEAK   price=14250.00 time= 11-05 00:00
  [62] TROUGH price=13315.00 time= 12-17 00:00
  [63] PEAK   price=13930.00 time= 02-18 00:00
  [64] TROUGH price=12315.00 time= 04-08 00:00
  [65] PEAK   price=13560.00 time= 05-20 00:00
  [66] TROUGH price=13200.00 time= 06-03 00:00
  [67] PEAK   price=14375.00 time= 07-15 00:00
  [68] TROUGH price=13535.00 time= 07-29 00:00
  [69] PEAK   price=14340.00 time= 08-26 00:00
  [70] TROUGH price=13155.00 time= 09-30 00:00
  [71] PEAK   price=13675.00 time= 10-28 00:00
  [72] TROUGH price=13380.00 time= 11-18 00:00
  [73] PEAK   price=15095.00 time= 01-06 00:00
  [74] TROUGH price=14395.00 time= 01-20 00:00
  [75] PEAK   price=15765.00 time= 03-10 00:00
  [76] TROUGH price=15035.00 time= 03-17 00:00 ← A
  [77] PEAK   price=16955.00 time= 05-06 00:00
  [78] TROUGH price=15855.00 time= 05-19 00:00 ← C
  [79] PEAK   price=16440.00 time= 06-02 00:00
```

**失败详情:**
```
  ❌ C4 最新(15675.00) > C(15855.00) = False
```
---

### CF — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 16005.00 @ 06-17 15:00 |
| B 价 | 16110.00 @ 06-17 21:15 |
| C 价 | 16015.00 @ 06-17 23:00 |
| 最新价 | 16010.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 25) |
| A 索引 | 20 | C 索引 | 22 |

**极值点序列** (swing: 40, merged: 25):
```
  [ 0] TROUGH price=15640.00 time= 06-10 14:00
  [ 1] PEAK   price=15715.00 time= 06-10 21:00
  [ 2] TROUGH price=15655.00 time= 06-11 09:00
  [ 3] PEAK   price=15720.00 time= 06-11 09:45
  [ 4] TROUGH price=15645.00 time= 06-11 11:15
  [ 5] PEAK   price=15800.00 time= 06-11 21:00
  [ 6] TROUGH price=15730.00 time= 06-11 22:00
  [ 7] PEAK   price=15820.00 time= 06-12 09:30
  [ 8] TROUGH price=15740.00 time= 06-12 10:45
  [ 9] PEAK   price=15805.00 time= 06-12 11:15
  [10] TROUGH price=15745.00 time= 06-12 13:45
  [11] PEAK   price=15840.00 time= 06-15 10:00
  [12] TROUGH price=15705.00 time= 06-15 14:45
  [13] PEAK   price=15790.00 time= 06-15 21:15
  [14] TROUGH price=15735.00 time= 06-15 22:15
  [15] PEAK   price=15780.00 time= 06-16 09:15
  [16] TROUGH price=15685.00 time= 06-16 09:30
  [17] PEAK   price=16090.00 time= 06-16 22:00
  [18] TROUGH price=15965.00 time= 06-17 10:45
  [19] PEAK   price=16045.00 time= 06-17 13:45
  [20] TROUGH price=16005.00 time= 06-17 15:00 ← A
  [21] PEAK   price=16110.00 time= 06-17 21:15
  [22] TROUGH price=16015.00 time= 06-17 23:00 ← C
  [23] PEAK   price=16100.00 time= 06-18 09:15
  [24] TROUGH price=15960.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(16010.00) > C(16015.00) = False
```
---

### CF — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 16440.00 @ 06-03 00:00 |
| B 价 | 15590.00 @ 06-10 00:00 |
| C 价 | 15840.00 @ 06-15 00:00 |
| 最新价 | 16010.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 26 (merge 后: 18) |
| A 索引 | 13 | C 索引 | 15 |

**极值点序列** (swing: 26, merged: 18):
```
  [ 0] TROUGH price=15120.00 time= 03-20 00:00
  [ 1] PEAK   price=15520.00 time= 03-23 09:15
  [ 2] TROUGH price=15300.00 time= 03-24 13:45
  [ 3] PEAK   price=15645.00 time= 03-31 09:15
  [ 4] TROUGH price=15205.00 time= 04-08 00:00
  [ 5] PEAK   price=16955.00 time= 05-06 00:00
  [ 6] TROUGH price=16255.00 time= 05-11 13:45
  [ 7] PEAK   price=16590.00 time= 05-13 13:45
  [ 8] TROUGH price=16005.00 time= 05-15 13:45
  [ 9] PEAK   price=16250.00 time= 05-19 09:15
  [10] TROUGH price=15855.00 time= 05-22 00:00
  [11] PEAK   price=16170.00 time= 05-26 13:45
  [12] TROUGH price=15970.00 time= 05-28 10:45
  [13] PEAK   price=16440.00 time= 06-03 00:00 ← A
  [14] TROUGH price=15590.00 time= 06-10 00:00
  [15] PEAK   price=15840.00 time= 06-15 00:00 ← C
  [16] TROUGH price=15685.00 time= 06-16 09:15
  [17] PEAK   price=16110.00 time= 06-17 13:45
```

**失败详情:**
```
  ❌ C4 最新(16010.00) < C(15840.00) = False
```
---

### CJ — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8720.00 @ 12-23 00:00 |
| B 价 | 9265.00 @ 01-09 00:00 |
| C 价 | 8880.00 @ 05-22 00:00 |
| 最新价 | 8880.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 60 (merge 后: 60) |
| A 索引 | 50 | C 索引 | 58 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] TROUGH price=15000.00 time= 12-15 00:00
  [ 1] PEAK   price=15675.00 time= 12-25 00:00
  [ 2] TROUGH price=11905.00 time= 02-07 00:00
  [ 3] PEAK   price=13170.00 time= 02-08 00:00
  [ 4] TROUGH price=12290.00 time= 02-26 00:00
  [ 5] PEAK   price=13175.00 time= 03-04 00:00
  [ 6] TROUGH price=11660.00 time= 04-02 00:00
  [ 7] PEAK   price=12830.00 time= 04-11 00:00
  [ 8] TROUGH price=12215.00 time= 04-17 00:00
  [ 9] PEAK   price=13215.00 time= 04-23 00:00
  [10] TROUGH price=12305.00 time= 04-26 00:00
  [11] PEAK   price=13100.00 time= 05-14 00:00
  [12] TROUGH price=10970.00 time= 06-19 00:00
  [13] PEAK   price=11635.00 time= 06-24 00:00
  [14] TROUGH price=10130.00 time= 07-10 00:00
  [15] PEAK   price=11035.00 time= 07-26 00:00
  [16] TROUGH price= 9865.00 time= 08-23 00:00
  [17] PEAK   price=10405.00 time= 08-28 00:00
  [18] TROUGH price= 9045.00 time= 09-18 00:00
  [19] PEAK   price=10400.00 time= 10-08 00:00
  [20] TROUGH price= 9510.00 time= 10-11 00:00
  [21] PEAK   price=10045.00 time= 10-16 00:00
  [22] TROUGH price= 9540.00 time= 10-28 00:00
  [23] PEAK   price=10760.00 time= 11-01 00:00
  [24] TROUGH price= 9230.00 time= 11-25 00:00
  [25] PEAK   price= 9730.00 time= 12-10 00:00
  [26] TROUGH price= 8940.00 time= 01-10 00:00
  [27] PEAK   price= 9400.00 time= 01-17 00:00
  [28] TROUGH price= 9100.00 time= 02-05 00:00
  [29] PEAK   price= 9580.00 time= 02-07 00:00
  [30] TROUGH price= 9175.00 time= 02-13 00:00
  [31] PEAK   price= 9530.00 time= 02-21 00:00
  [32] TROUGH price= 8930.00 time= 03-24 00:00
  [33] PEAK   price= 9215.00 time= 03-26 00:00
  [34] TROUGH price= 8830.00 time= 04-09 00:00
  [35] PEAK   price= 9555.00 time= 04-18 00:00
  [36] TROUGH price= 8850.00 time= 05-08 00:00
  [37] PEAK   price= 9235.00 time= 05-15 00:00
  [38] TROUGH price= 8560.00 time= 05-30 00:00
  [39] PEAK   price=11325.00 time= 07-02 00:00
  [40] TROUGH price=10175.00 time= 07-15 00:00
  [41] PEAK   price=11825.00 time= 08-11 00:00
  [42] TROUGH price=11200.00 time= 08-22 00:00
  [43] PEAK   price=11570.00 time= 09-01 00:00
  [44] TROUGH price=10580.00 time= 09-19 00:00
  [45] PEAK   price=11295.00 time= 09-26 00:00
  [46] TROUGH price=10660.00 time= 09-30 00:00
  [47] PEAK   price=11480.00 time= 10-17 00:00
  [48] TROUGH price= 8925.00 time= 12-04 00:00
  [49] PEAK   price= 9525.00 time= 12-08 00:00
  [50] TROUGH price= 8720.00 time= 12-23 00:00 ← A
  [51] PEAK   price= 9265.00 time= 01-09 00:00
  [52] TROUGH price= 8640.00 time= 01-21 00:00
  [53] PEAK   price= 9065.00 time= 02-02 00:00
  [54] TROUGH price= 8610.00 time= 02-11 00:00
  [55] PEAK   price= 9370.00 time= 03-09 00:00
  [56] TROUGH price= 8295.00 time= 04-07 00:00
  [57] PEAK   price= 9440.00 time= 05-13 00:00
  [58] TROUGH price= 8880.00 time= 05-22 00:00 ← C
  [59] PEAK   price= 9670.00 time= 06-03 00:00
```

**失败详情:**
```
  ❌ C4 最新(8880.00) > C(8880.00) = False
```
---

### CJ — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8610.00 @ 02-10 00:00 |
| B 价 | 9370.00 @ 03-03 00:00 |
| C 价 | 8880.00 @ 05-19 00:00 |
| 最新价 | 8880.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 79 (merge 后: 79) |
| A 索引 | 73 | C 索引 | 77 |

**极值点序列** (swing: 79, merged: 79):
```
  [ 0] PEAK   price=10935.00 time= 05-21 00:00
  [ 1] TROUGH price= 9605.00 time= 06-04 00:00
  [ 2] PEAK   price=10675.00 time= 06-25 00:00
  [ 3] TROUGH price= 9995.00 time= 07-23 00:00
  [ 4] PEAK   price=11555.00 time= 09-03 00:00
  [ 5] TROUGH price= 9770.00 time= 10-15 00:00
  [ 6] PEAK   price=11260.00 time= 11-12 00:00
  [ 7] TROUGH price=10580.00 time= 12-03 00:00
  [ 8] PEAK   price=11015.00 time= 12-24 00:00
  [ 9] TROUGH price= 9890.00 time= 02-04 00:00
  [10] PEAK   price=10710.00 time= 02-25 00:00
  [11] TROUGH price= 9670.00 time= 03-24 00:00
  [12] PEAK   price=10465.00 time= 04-21 00:00
  [13] TROUGH price= 9845.00 time= 05-26 00:00
  [14] PEAK   price=10170.00 time= 06-09 00:00
  [15] TROUGH price= 8755.00 time= 08-04 00:00
  [16] PEAK   price=10335.00 time= 09-08 00:00
  [17] TROUGH price= 9680.00 time= 09-29 00:00
  [18] PEAK   price=10250.00 time= 10-13 00:00
  [19] TROUGH price= 9715.00 time= 10-27 00:00
  [20] PEAK   price=10075.00 time= 11-17 00:00
  [21] TROUGH price= 9165.00 time= 12-08 00:00
  [22] PEAK   price=10445.00 time= 01-05 00:00
  [23] TROUGH price= 9915.00 time= 02-09 00:00
  [24] PEAK   price=10955.00 time= 02-23 00:00
  [25] TROUGH price= 9620.00 time= 03-30 00:00
  [26] PEAK   price=10345.00 time= 04-20 00:00
  [27] TROUGH price= 8225.00 time= 06-15 00:00
  [28] PEAK   price=15005.00 time= 08-24 00:00
  [29] TROUGH price=13315.00 time= 09-07 00:00
  [30] PEAK   price=16465.00 time= 10-19 00:00
  [31] TROUGH price=12820.00 time= 10-26 00:00
  [32] PEAK   price=17655.00 time= 11-23 00:00
  [33] TROUGH price=12350.00 time= 01-04 00:00
  [34] PEAK   price=14430.00 time= 02-15 00:00
  [35] TROUGH price=10980.00 time= 04-06 00:00
  [36] PEAK   price=13050.00 time= 05-17 00:00
  [37] TROUGH price=10235.00 time= 06-14 00:00
  [38] PEAK   price=12790.00 time= 07-12 00:00
  [39] TROUGH price=11635.00 time= 08-16 00:00
  [40] PEAK   price=12595.00 time= 09-13 00:00
  [41] TROUGH price=10765.00 time= 11-01 00:00
  [42] PEAK   price=11070.00 time= 12-06 00:00
  [43] TROUGH price= 9925.00 time= 12-20 00:00
  [44] PEAK   price=11005.00 time= 01-31 00:00
  [45] TROUGH price= 9315.00 time= 03-21 00:00
  [46] PEAK   price=10950.00 time= 05-04 00:00
  [47] TROUGH price= 9930.00 time= 05-23 00:00
  [48] PEAK   price=13845.00 time= 09-19 00:00
  [49] TROUGH price=12585.00 time= 10-10 00:00
  [50] PEAK   price=15730.00 time= 12-05 00:00
  [51] TROUGH price=11905.00 time= 02-06 00:00
  [52] PEAK   price=13175.00 time= 02-27 00:00
  [53] TROUGH price=11660.00 time= 04-02 00:00
  [54] PEAK   price=13215.00 time= 04-23 00:00
  [55] TROUGH price=10130.00 time= 07-09 00:00
  [56] PEAK   price=11035.00 time= 07-23 00:00
  [57] TROUGH price= 9045.00 time= 09-18 00:00
  [58] PEAK   price=10760.00 time= 10-29 00:00
  [59] TROUGH price= 9230.00 time= 11-19 00:00
  [60] PEAK   price= 9730.00 time= 12-10 00:00
  [61] TROUGH price= 8940.00 time= 01-07 00:00
  [62] PEAK   price= 9580.00 time= 02-05 00:00
  [63] TROUGH price= 8830.00 time= 04-08 00:00
  [64] PEAK   price= 9555.00 time= 04-15 00:00
  [65] TROUGH price= 8850.00 time= 05-06 00:00
  [66] PEAK   price= 9235.00 time= 05-13 00:00
  [67] TROUGH price= 8560.00 time= 05-27 00:00
  [68] PEAK   price=11825.00 time= 08-05 00:00
  [69] TROUGH price=10580.00 time= 09-16 00:00
  [70] PEAK   price=11480.00 time= 10-14 00:00
  [71] TROUGH price= 8720.00 time= 12-23 00:00
  [72] PEAK   price= 9265.00 time= 01-06 00:00
  [73] TROUGH price= 8610.00 time= 02-10 00:00 ← A
  [74] PEAK   price= 9370.00 time= 03-03 00:00
  [75] TROUGH price= 8295.00 time= 04-07 00:00
  [76] PEAK   price= 9440.00 time= 05-12 00:00
  [77] TROUGH price= 8880.00 time= 05-19 00:00 ← C
  [78] PEAK   price= 9670.00 time= 06-02 00:00
```

**失败详情:**
```
  ❌ C4 最新(8880.00) > C(8880.00) = False
```
---

### CJ — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8770.00 @ 06-17 13:45 |
| B 价 | 8595.00 @ 06-18 11:00 |
| C 价 | 8625.00 @ 06-18 13:45 |
| 最新价 | 8625.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 30) |
| A 索引 | 27 | C 索引 | 29 |

**极值点序列** (swing: 40, merged: 30):
```
  [ 0] TROUGH price= 9530.00 time= 06-02 09:30
  [ 1] PEAK   price= 9650.00 time= 06-02 10:00
  [ 2] TROUGH price= 9530.00 time= 06-02 14:15
  [ 3] PEAK   price= 9560.00 time= 06-02 14:45
  [ 4] TROUGH price= 9475.00 time= 06-03 09:15
  [ 5] PEAK   price= 9670.00 time= 06-03 13:45
  [ 6] TROUGH price= 9310.00 time= 06-04 11:15
  [ 7] PEAK   price= 9375.00 time= 06-04 11:30
  [ 8] TROUGH price= 8980.00 time= 06-08 10:15
  [ 9] PEAK   price= 9130.00 time= 06-09 09:45
  [10] TROUGH price= 9045.00 time= 06-09 10:45
  [11] PEAK   price= 9110.00 time= 06-09 13:45
  [12] TROUGH price= 8760.00 time= 06-10 09:00
  [13] PEAK   price= 8925.00 time= 06-11 09:00
  [14] TROUGH price= 8810.00 time= 06-11 11:15
  [15] PEAK   price= 8930.00 time= 06-11 14:30
  [16] TROUGH price= 8840.00 time= 06-12 09:00
  [17] PEAK   price= 8935.00 time= 06-12 09:45
  [18] TROUGH price= 8890.00 time= 06-12 10:30
  [19] PEAK   price= 8955.00 time= 06-12 11:15
  [20] TROUGH price= 8805.00 time= 06-15 09:15
  [21] PEAK   price= 8955.00 time= 06-15 11:15
  [22] TROUGH price= 8860.00 time= 06-15 13:45
  [23] PEAK   price= 8895.00 time= 06-15 15:00
  [24] TROUGH price= 8700.00 time= 06-16 10:00
  [25] PEAK   price= 8800.00 time= 06-16 14:00
  [26] TROUGH price= 8720.00 time= 06-17 09:15
  [27] PEAK   price= 8770.00 time= 06-17 13:45 ← A
  [28] TROUGH price= 8595.00 time= 06-18 11:00
  [29] PEAK   price= 8625.00 time= 06-18 13:45 ← C
```

**失败详情:**
```
  ❌ C4 最新(8625.00) < C(8625.00) = False
```
---

### CJ — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8505.00 @ 06-10 00:00 |
| B 价 | 8960.00 @ 06-15 00:00 |
| C 价 | 8700.00 @ 06-16 09:15 |
| 最新价 | 8615.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 30 (merge 后: 25) |
| A 索引 | 22 | C 索引 | 24 |

**极值点序列** (swing: 30, merged: 25):
```
  [ 0] TROUGH price= 8880.00 time= 02-09 09:15
  [ 1] PEAK   price= 9105.00 time= 02-11 13:45
  [ 2] TROUGH price= 8965.00 time= 02-24 09:15
  [ 3] PEAK   price= 9215.00 time= 02-27 09:15
  [ 4] TROUGH price= 9030.00 time= 03-02 09:15
  [ 5] PEAK   price= 9705.00 time= 03-09 09:15
  [ 6] TROUGH price= 9255.00 time= 03-10 09:15
  [ 7] PEAK   price= 9555.00 time= 03-12 09:15
  [ 8] TROUGH price= 9085.00 time= 03-19 09:15
  [ 9] PEAK   price= 9365.00 time= 03-23 10:45
  [10] TROUGH price= 8720.00 time= 04-09 00:00
  [11] PEAK   price= 8990.00 time= 04-10 09:15
  [12] TROUGH price= 8775.00 time= 04-15 09:15
  [13] PEAK   price= 9150.00 time= 04-22 00:00
  [14] TROUGH price= 8970.00 time= 04-24 00:00
  [15] PEAK   price= 9440.00 time= 05-13 00:00
  [16] TROUGH price= 9185.00 time= 05-13 09:15
  [17] PEAK   price= 9430.00 time= 05-13 13:45
  [18] TROUGH price= 8880.00 time= 05-22 00:00
  [19] PEAK   price= 9670.00 time= 06-03 00:00
  [20] TROUGH price= 8980.00 time= 06-08 00:00
  [21] PEAK   price= 9130.00 time= 06-09 00:00
  [22] TROUGH price= 8505.00 time= 06-10 00:00 ← A
  [23] PEAK   price= 8960.00 time= 06-15 00:00
  [24] TROUGH price= 8700.00 time= 06-16 09:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(8615.00) > C(8700.00) = False
```
---

### CS — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2688.00 @ 06-16 09:15 |
| B 价 | 2707.00 @ 06-17 09:15 |
| C 价 | 2700.00 @ 06-17 14:00 |
| 最新价 | 2698.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 36) |
| A 索引 | 31 | C 索引 | 33 |

**极值点序列** (swing: 50, merged: 36):
```
  [ 0] PEAK   price= 2680.00 time= 05-27 10:00
  [ 1] TROUGH price= 2656.00 time= 05-27 21:15
  [ 2] PEAK   price= 2666.00 time= 05-28 09:15
  [ 3] TROUGH price= 2656.00 time= 05-28 10:00
  [ 4] PEAK   price= 2691.00 time= 05-29 10:00
  [ 5] TROUGH price= 2678.00 time= 05-29 11:00
  [ 6] PEAK   price= 2695.00 time= 05-29 21:15
  [ 7] TROUGH price= 2680.00 time= 06-01 09:15
  [ 8] PEAK   price= 2693.00 time= 06-01 10:00
  [ 9] TROUGH price= 2682.00 time= 06-01 21:15
  [10] PEAK   price= 2695.00 time= 06-01 22:00
  [11] TROUGH price= 2682.00 time= 06-02 10:45
  [12] PEAK   price= 2701.00 time= 06-03 09:15
  [13] TROUGH price= 2649.00 time= 06-04 11:00
  [14] PEAK   price= 2710.00 time= 06-05 13:45
  [15] TROUGH price= 2689.00 time= 06-05 21:15
  [16] PEAK   price= 2731.00 time= 06-08 22:00
  [17] TROUGH price= 2718.00 time= 06-09 10:00
  [18] PEAK   price= 2739.00 time= 06-09 21:15
  [19] TROUGH price= 2721.00 time= 06-10 09:12
  [20] PEAK   price= 2736.00 time= 06-10 10:00
  [21] TROUGH price= 2705.00 time= 06-10 21:00
  [22] PEAK   price= 2729.00 time= 06-11 10:00
  [23] TROUGH price= 2714.00 time= 06-11 11:00
  [24] PEAK   price= 2729.00 time= 06-11 11:15
  [25] TROUGH price= 2714.00 time= 06-11 14:15
  [26] PEAK   price= 2738.00 time= 06-11 21:00
  [27] TROUGH price= 2720.00 time= 06-12 10:00
  [28] PEAK   price= 2732.00 time= 06-12 13:30
  [29] TROUGH price= 2680.00 time= 06-15 11:00
  [30] PEAK   price= 2697.00 time= 06-15 15:00
  [31] TROUGH price= 2688.00 time= 06-16 09:15 ← A
  [32] PEAK   price= 2707.00 time= 06-17 09:15
  [33] TROUGH price= 2700.00 time= 06-17 14:00 ← C
  [34] PEAK   price= 2711.00 time= 06-17 21:15
  [35] TROUGH price= 2691.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(2698.00) > C(2700.00) = False
```
---

### CU — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 104800.00 @ 06-04 14:00 |
| B 价 | 106800.00 @ 06-04 21:15 |
| C 价 | 104980.00 @ 06-17 09:15 |
| 最新价 | 104780.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 39) |
| A 索引 | 16 | C 索引 | 36 |

**极值点序列** (swing: 50, merged: 39):
```
  [ 0] TROUGH price=103620.00 time= 05-21 21:15
  [ 1] PEAK   price=105300.00 time= 05-22 14:00
  [ 2] TROUGH price=104420.00 time= 05-22 22:00
  [ 3] PEAK   price=106110.00 time= 05-25 09:15
  [ 4] TROUGH price=105050.00 time= 05-25 14:00
  [ 5] PEAK   price=106020.00 time= 05-25 21:15
  [ 6] TROUGH price=104570.00 time= 05-26 14:00
  [ 7] PEAK   price=105450.00 time= 05-27 11:00
  [ 8] TROUGH price=103520.00 time= 05-28 10:00
  [ 9] PEAK   price=105350.00 time= 05-29 09:15
  [10] TROUGH price=104280.00 time= 05-29 23:00
  [11] PEAK   price=105010.00 time= 06-01 10:00
  [12] TROUGH price=104680.00 time= 06-01 15:00
  [13] PEAK   price=107420.00 time= 06-02 22:00
  [14] TROUGH price=105050.00 time= 06-04 10:00
  [15] PEAK   price=105770.00 time= 06-04 13:45
  [16] TROUGH price=104800.00 time= 06-04 14:00 ← A
  [17] PEAK   price=106800.00 time= 06-04 21:15
  [18] TROUGH price=103350.00 time= 06-08 09:15
  [19] PEAK   price=104450.00 time= 06-08 11:00
  [20] TROUGH price=103790.00 time= 06-08 13:45
  [21] PEAK   price=104800.00 time= 06-08 21:15
  [22] TROUGH price=103900.00 time= 06-09 11:00
  [23] PEAK   price=105670.00 time= 06-09 22:00
  [24] TROUGH price=103510.00 time= 06-10 21:15
  [25] PEAK   price=104340.00 time= 06-10 22:00
  [26] TROUGH price=102640.00 time= 06-11 10:30
  [27] PEAK   price=103600.00 time= 06-11 11:15
  [28] TROUGH price=102830.00 time= 06-11 14:15
  [29] PEAK   price=105110.00 time= 06-12 11:00
  [30] TROUGH price=104250.00 time= 06-12 21:00
  [31] PEAK   price=106000.00 time= 06-15 10:45
  [32] TROUGH price=104610.00 time= 06-16 10:00
  [33] PEAK   price=105060.00 time= 06-16 13:45
  [34] TROUGH price=104450.00 time= 06-16 15:00
  [35] PEAK   price=105380.00 time= 06-16 22:00
  [36] TROUGH price=104980.00 time= 06-17 09:15 ← C
  [37] PEAK   price=105590.00 time= 06-17 10:45
  [38] TROUGH price=104430.00 time= 06-18 11:00
```

**失败详情:**
```
  ❌ C4 最新(104780.00) > C(104980.00) = False
```
---

### EB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8804.00 @ 07-23 00:00 |
| B 价 | 9383.00 @ 08-13 00:00 |
| C 价 | 9300.00 @ 04-14 00:00 |
| 最新价 | 8476.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 72 (merge 后: 72) |
| A 索引 | 50 | C 索引 | 70 |

**极值点序列** (swing: 72, merged: 72):
```
  [ 0] TROUGH price= 6872.00 time= 11-12 00:00
  [ 1] PEAK   price= 7494.00 time= 12-03 00:00
  [ 2] TROUGH price= 7237.00 time= 12-31 00:00
  [ 3] PEAK   price= 7587.00 time= 01-14 00:00
  [ 4] TROUGH price= 6497.00 time= 02-04 00:00
  [ 5] PEAK   price= 7078.00 time= 02-18 00:00
  [ 6] TROUGH price= 4338.00 time= 03-24 00:00
  [ 7] PEAK   price= 5988.00 time= 06-02 00:00
  [ 8] TROUGH price= 5070.00 time= 08-18 00:00
  [ 9] PEAK   price= 5880.00 time= 09-01 00:00
  [10] TROUGH price= 5421.00 time= 09-22 00:00
  [11] PEAK   price= 8435.00 time= 11-10 00:00
  [12] TROUGH price= 6011.00 time= 12-29 00:00
  [13] PEAK   price=10090.00 time= 02-23 00:00
  [14] TROUGH price= 7785.00 time= 03-16 00:00
  [15] PEAK   price=10242.00 time= 05-11 00:00
  [16] TROUGH price= 8195.00 time= 06-15 00:00
  [17] PEAK   price= 9587.00 time= 06-29 00:00
  [18] TROUGH price= 8252.00 time= 08-17 00:00
  [19] PEAK   price=10279.00 time= 10-12 00:00
  [20] TROUGH price= 7465.00 time= 11-23 00:00
  [21] PEAK   price= 9600.00 time= 02-07 00:00
  [22] TROUGH price= 8706.00 time= 02-15 00:00
  [23] PEAK   price=10608.00 time= 03-08 00:00
  [24] TROUGH price= 9334.00 time= 04-26 00:00
  [25] PEAK   price=11515.00 time= 06-07 00:00
  [26] TROUGH price= 7663.00 time= 08-16 00:00
  [27] PEAK   price= 9400.00 time= 09-20 00:00
  [28] TROUGH price= 7552.00 time= 11-01 00:00
  [29] PEAK   price= 8380.00 time= 11-15 00:00
  [30] TROUGH price= 7550.00 time= 11-29 00:00
  [31] PEAK   price= 9068.00 time= 01-30 00:00
  [32] TROUGH price= 8250.00 time= 02-07 00:00
  [33] PEAK   price= 8682.00 time= 02-21 00:00
  [34] TROUGH price= 8049.00 time= 03-14 00:00
  [35] PEAK   price= 8775.00 time= 04-11 00:00
  [36] TROUGH price= 6980.00 time= 06-13 00:00
  [37] PEAK   price= 9998.00 time= 09-12 00:00
  [38] TROUGH price= 8235.00 time= 10-10 00:00
  [39] PEAK   price= 8888.00 time= 11-14 00:00
  [40] TROUGH price= 7756.00 time= 12-05 00:00
  [41] PEAK   price= 8675.00 time= 12-19 00:00
  [42] TROUGH price= 8227.00 time= 01-09 00:00
  [43] PEAK   price= 9387.00 time= 02-19 00:00
  [44] TROUGH price= 8961.00 time= 02-27 00:00
  [45] PEAK   price= 9780.00 time= 04-16 00:00
  [46] TROUGH price= 9076.00 time= 05-07 00:00
  [47] PEAK   price= 9819.00 time= 05-28 00:00
  [48] TROUGH price= 9127.00 time= 06-25 00:00
  [49] PEAK   price= 9535.00 time= 07-02 00:00
  [50] TROUGH price= 8804.00 time= 07-23 00:00 ← A
  [51] PEAK   price= 9383.00 time= 08-13 00:00
  [52] TROUGH price= 8265.00 time= 09-10 00:00
  [53] PEAK   price= 9188.00 time= 10-08 00:00
  [54] TROUGH price= 8234.00 time= 11-26 00:00
  [55] PEAK   price= 8576.00 time= 12-03 00:00
  [56] TROUGH price= 8007.00 time= 01-07 00:00
  [57] PEAK   price= 8815.00 time= 02-05 00:00
  [58] TROUGH price= 6780.00 time= 04-08 00:00
  [59] PEAK   price= 7853.00 time= 05-13 00:00
  [60] TROUGH price= 6985.00 time= 06-03 00:00
  [61] PEAK   price= 7787.00 time= 06-10 00:00
  [62] TROUGH price= 7180.00 time= 06-24 00:00
  [63] PEAK   price= 7593.00 time= 07-22 00:00
  [64] TROUGH price= 6230.00 time= 11-11 00:00
  [65] PEAK   price= 6676.00 time= 12-02 00:00
  [66] TROUGH price= 6343.00 time= 12-16 00:00
  [67] PEAK   price= 8027.00 time= 01-27 00:00
  [68] TROUGH price= 7323.00 time= 02-10 00:00
  [69] PEAK   price=11132.00 time= 03-17 00:00
  [70] TROUGH price= 9300.00 time= 04-14 00:00 ← C
  [71] PEAK   price=10098.00 time= 04-28 00:00
```

**失败详情:**
```
  ❌ C4 最新(8476.00) > C(9300.00) = False
```
---

### EB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 5180.00 @ 04-20 13:45 |
| B 价 | 5700.00 @ 05-06 09:15 |
| C 价 | 5421.00 @ 05-06 11:30 |
| 最新价 | 5380.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 21 | C 索引 | 39 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 5324.00 time= 04-09 10:45
  [ 1] TROUGH price= 5232.00 time= 04-10 09:15
  [ 2] PEAK   price= 5512.00 time= 04-10 09:45
  [ 3] TROUGH price= 5232.00 time= 04-10 14:00
  [ 4] PEAK   price= 5609.00 time= 04-13 09:15
  [ 5] TROUGH price= 5389.00 time= 04-13 13:45
  [ 6] PEAK   price= 5566.00 time= 04-13 14:00
  [ 7] TROUGH price= 5128.00 time= 04-14 10:00
  [ 8] PEAK   price= 5259.00 time= 04-14 10:45
  [ 9] TROUGH price= 5170.00 time= 04-14 11:30
  [10] PEAK   price= 5265.00 time= 04-14 13:45
  [11] TROUGH price= 5071.00 time= 04-15 09:15
  [12] PEAK   price= 5292.00 time= 04-15 13:45
  [13] TROUGH price= 5181.00 time= 04-16 10:00
  [14] PEAK   price= 5250.00 time= 04-16 10:45
  [15] TROUGH price= 5146.00 time= 04-16 13:45
  [16] PEAK   price= 5382.00 time= 04-17 09:45
  [17] TROUGH price= 5220.00 time= 04-17 10:45
  [18] PEAK   price= 5299.00 time= 04-17 14:45
  [19] TROUGH price= 5134.00 time= 04-20 09:15
  [20] PEAK   price= 5241.00 time= 04-20 10:45
  [21] TROUGH price= 5180.00 time= 04-20 13:45 ← A
  [22] PEAK   price= 5250.00 time= 04-20 15:00
  [23] TROUGH price= 4567.00 time= 04-22 09:15
  [24] PEAK   price= 5088.00 time= 04-24 09:15
  [25] TROUGH price= 4881.00 time= 04-24 10:00
  [26] PEAK   price= 5043.00 time= 04-24 11:30
  [27] TROUGH price= 4907.00 time= 04-24 14:15
  [28] PEAK   price= 5074.00 time= 04-27 10:45
  [29] TROUGH price= 4991.00 time= 04-27 14:00
  [30] PEAK   price= 5044.00 time= 04-27 14:15
  [31] TROUGH price= 4950.00 time= 04-28 09:15
  [32] PEAK   price= 5085.00 time= 04-28 09:30
  [33] TROUGH price= 4970.00 time= 04-28 10:15
  [34] PEAK   price= 5140.00 time= 04-29 09:15
  [35] TROUGH price= 5077.00 time= 04-29 14:30
  [36] PEAK   price= 5220.00 time= 04-30 09:15
  [37] TROUGH price= 5138.00 time= 04-30 14:15
  [38] PEAK   price= 5700.00 time= 05-06 09:15
  [39] TROUGH price= 5421.00 time= 05-06 11:30 ← C
```

**失败详情:**
```
  ❌ C4 最新(5380.00) > C(5421.00) = False
```
---

### EB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 5382.00 @ 04-17 09:15 |
| B 价 | 4567.00 @ 04-22 09:15 |
| C 价 | 5088.00 @ 04-24 09:15 |
| 最新价 | 5380.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 14 (merge 后: 14) |
| A 索引 | 11 | C 索引 | 13 |

**极值点序列** (swing: 14, merged: 14):
```
  [ 0] TROUGH price= 6550.00 time= 02-04 09:00
  [ 1] PEAK   price= 7013.00 time= 02-05 09:00
  [ 2] TROUGH price= 6816.00 time= 02-12 13:45
  [ 3] PEAK   price= 7078.00 time= 02-21 09:15
  [ 4] TROUGH price= 6951.00 time= 02-24 09:15
  [ 5] PEAK   price= 7041.00 time= 02-26 09:15
  [ 6] TROUGH price= 6651.00 time= 03-02 09:15
  [ 7] PEAK   price= 6850.00 time= 03-03 09:15
  [ 8] TROUGH price= 4340.00 time= 03-30 13:45
  [ 9] PEAK   price= 5609.00 time= 04-13 09:15
  [10] TROUGH price= 5071.00 time= 04-15 09:15
  [11] PEAK   price= 5382.00 time= 04-17 09:15 ← A
  [12] TROUGH price= 4567.00 time= 04-22 09:15
  [13] PEAK   price= 5088.00 time= 04-24 09:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(5380.00) < C(5088.00) = False
```
---

### EB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9370.00 @ 04-21 11:30 |
| B 价 | 10277.00 @ 05-10 14:45 |
| C 价 | 10026.00 @ 05-12 10:00 |
| 最新价 | 9760.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 9 | C 索引 | 35 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 9184.00 time= 04-16 21:30
  [ 1] TROUGH price= 8930.00 time= 04-19 09:30
  [ 2] PEAK   price= 9297.00 time= 04-19 14:15
  [ 3] TROUGH price= 9205.00 time= 04-19 15:00
  [ 4] PEAK   price= 9438.00 time= 04-19 22:15
  [ 5] TROUGH price= 9206.00 time= 04-20 09:45
  [ 6] PEAK   price= 9475.00 time= 04-20 21:15
  [ 7] TROUGH price= 9265.00 time= 04-20 23:00
  [ 8] PEAK   price= 9419.00 time= 04-21 09:15
  [ 9] TROUGH price= 9370.00 time= 04-21 11:30 ← A
  [10] PEAK   price= 9597.00 time= 04-21 14:45
  [11] TROUGH price= 9279.00 time= 04-21 21:45
  [12] PEAK   price= 9390.00 time= 04-21 22:30
  [13] TROUGH price= 9175.00 time= 04-22 10:15
  [14] PEAK   price= 9341.00 time= 04-22 11:30
  [15] TROUGH price= 9152.00 time= 04-22 21:45
  [16] PEAK   price= 9220.00 time= 04-22 22:15
  [17] TROUGH price= 9101.00 time= 04-23 09:30
  [18] PEAK   price= 9355.00 time= 04-23 13:45
  [19] TROUGH price= 9280.00 time= 04-23 21:15
  [20] PEAK   price= 9530.00 time= 04-26 09:15
  [21] TROUGH price= 9120.00 time= 04-26 22:15
  [22] PEAK   price= 9200.00 time= 04-27 09:15
  [23] TROUGH price= 9046.00 time= 04-27 11:15
  [24] PEAK   price= 9271.00 time= 04-27 21:15
  [25] TROUGH price= 9114.00 time= 04-27 21:45
  [26] PEAK   price= 9209.00 time= 04-27 23:00
  [27] TROUGH price= 9111.00 time= 04-28 10:45
  [28] PEAK   price= 9368.00 time= 04-29 10:45
  [29] TROUGH price= 9193.00 time= 04-29 15:00
  [30] PEAK   price= 9293.00 time= 04-29 21:15
  [31] TROUGH price= 9180.00 time= 04-29 22:45
  [32] PEAK   price= 9254.00 time= 04-30 09:30
  [33] TROUGH price= 9070.00 time= 05-06 09:15
  [34] PEAK   price=10277.00 time= 05-10 14:45
  [35] TROUGH price=10026.00 time= 05-12 10:00 ← C
  [36] PEAK   price=10469.00 time= 05-12 23:00
  [37] TROUGH price= 9837.00 time= 05-14 14:00
  [38] PEAK   price=10598.00 time= 05-19 10:45
  [39] TROUGH price= 8514.00 time= 05-19 21:30
```

**失败详情:**
```
  ❌ C4 最新(9760.00) > C(10026.00) = False
```
---

### EB — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9070.00 @ 05-06 09:15 |
| B 价 | 10277.00 @ 05-10 14:00 |
| C 价 | 10026.00 @ 05-12 10:00 |
| 最新价 | 9760.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 43 | C 索引 | 45 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 8400.00 time= 03-18 14:00
  [ 1] TROUGH price= 7785.00 time= 03-19 15:00
  [ 2] PEAK   price= 8146.00 time= 03-22 21:15
  [ 3] TROUGH price= 7847.00 time= 03-23 21:15
  [ 4] PEAK   price= 8325.00 time= 03-24 23:00
  [ 5] TROUGH price= 8120.00 time= 03-25 21:15
  [ 6] PEAK   price= 8334.00 time= 03-25 22:00
  [ 7] TROUGH price= 8152.00 time= 03-26 11:00
  [ 8] PEAK   price= 8488.00 time= 03-26 22:00
  [ 9] TROUGH price= 8167.00 time= 03-29 13:45
  [10] PEAK   price= 8553.00 time= 03-31 09:15
  [11] TROUGH price= 8405.00 time= 03-31 11:00
  [12] PEAK   price= 8986.00 time= 04-01 21:15
  [13] TROUGH price= 8721.00 time= 04-02 13:45
  [14] PEAK   price= 9244.00 time= 04-06 23:00
  [15] TROUGH price= 8954.00 time= 04-07 10:00
  [16] PEAK   price= 9099.00 time= 04-07 13:45
  [17] TROUGH price= 8535.00 time= 04-09 09:15
  [18] PEAK   price= 8665.00 time= 04-09 22:00
  [19] TROUGH price= 8452.00 time= 04-12 09:15
  [20] PEAK   price= 8767.00 time= 04-12 21:15
  [21] TROUGH price= 8361.00 time= 04-13 09:15
  [22] PEAK   price= 8770.00 time= 04-13 23:00
  [23] TROUGH price= 8606.00 time= 04-14 09:15
  [24] PEAK   price= 9025.00 time= 04-15 09:15
  [25] TROUGH price= 8881.00 time= 04-15 11:00
  [26] PEAK   price= 9095.00 time= 04-16 09:15
  [27] TROUGH price= 8860.00 time= 04-16 11:00
  [28] PEAK   price= 9184.00 time= 04-16 21:15
  [29] TROUGH price= 8930.00 time= 04-19 09:15
  [30] PEAK   price= 9438.00 time= 04-19 22:00
  [31] TROUGH price= 9206.00 time= 04-20 09:15
  [32] PEAK   price= 9475.00 time= 04-20 21:15
  [33] TROUGH price= 9265.00 time= 04-20 23:00
  [34] PEAK   price= 9597.00 time= 04-21 14:00
  [35] TROUGH price= 9175.00 time= 04-22 10:00
  [36] PEAK   price= 9312.00 time= 04-22 21:15
  [37] TROUGH price= 9101.00 time= 04-23 09:15
  [38] PEAK   price= 9530.00 time= 04-26 09:15
  [39] TROUGH price= 9046.00 time= 04-27 11:00
  [40] PEAK   price= 9271.00 time= 04-27 21:15
  [41] TROUGH price= 9111.00 time= 04-28 10:45
  [42] PEAK   price= 9368.00 time= 04-29 10:45
  [43] TROUGH price= 9070.00 time= 05-06 09:15 ← A
  [44] PEAK   price=10277.00 time= 05-10 14:00
  [45] TROUGH price=10026.00 time= 05-12 10:00 ← C
  [46] PEAK   price=10469.00 time= 05-12 23:00
  [47] TROUGH price= 9837.00 time= 05-14 14:00
  [48] PEAK   price=10598.00 time= 05-19 10:45
  [49] TROUGH price= 8514.00 time= 05-19 21:30
```

**失败详情:**
```
  ❌ C4 最新(9760.00) > C(10026.00) = False
```
---

### EB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9046.00 @ 04-27 10:45 |
| B 价 | 10469.00 @ 05-12 13:45 |
| C 价 | 9837.00 @ 05-14 14:00 |
| 最新价 | 9760.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 14 (merge 后: 14) |
| A 索引 | 9 | C 索引 | 11 |

**极值点序列** (swing: 14, merged: 14):
```
  [ 0] PEAK   price= 9823.00 time= 03-08 09:15
  [ 1] TROUGH price= 8618.00 time= 03-10 10:45
  [ 2] PEAK   price= 9099.00 time= 03-11 13:45
  [ 3] TROUGH price= 7785.00 time= 03-19 13:45
  [ 4] PEAK   price= 9244.00 time= 04-06 13:45
  [ 5] TROUGH price= 8361.00 time= 04-13 09:15
  [ 6] PEAK   price= 9597.00 time= 04-21 13:45
  [ 7] TROUGH price= 9101.00 time= 04-23 09:15
  [ 8] PEAK   price= 9530.00 time= 04-26 09:15
  [ 9] TROUGH price= 9046.00 time= 04-27 10:45 ← A
  [10] PEAK   price=10469.00 time= 05-12 13:45
  [11] TROUGH price= 9837.00 time= 05-14 14:00 ← C
  [12] PEAK   price=10598.00 time= 05-19 10:45
  [13] TROUGH price= 8514.00 time= 05-19 21:30
```

**失败详情:**
```
  ❌ C4 最新(9760.00) > C(9837.00) = False
```
---

### EB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price=10130.00 time= 04-06 09:15
  [ 1] TROUGH price= 9377.00 time= 04-25 09:15
  [ 2] PEAK   price=10689.00 time= 05-05 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### EB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9089.00 @ 09-08 09:45 |
| B 价 | 9688.00 @ 09-13 09:30 |
| C 价 | 9570.00 @ 09-20 11:30 |
| 最新价 | 9350.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 33 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 8316.00 time= 08-23 11:30
  [ 1] TROUGH price= 8253.00 time= 08-23 14:15
  [ 2] PEAK   price= 8599.00 time= 08-24 09:15
  [ 3] TROUGH price= 8399.00 time= 08-24 10:45
  [ 4] PEAK   price= 8531.00 time= 08-24 14:45
  [ 5] TROUGH price= 8415.00 time= 08-24 21:45
  [ 6] PEAK   price= 8507.00 time= 08-25 10:00
  [ 7] TROUGH price= 8450.00 time= 08-25 11:15
  [ 8] PEAK   price= 8554.00 time= 08-25 14:00
  [ 9] TROUGH price= 8488.00 time= 08-25 21:15
  [10] PEAK   price= 8698.00 time= 08-25 21:45
  [11] TROUGH price= 8550.00 time= 08-26 09:15
  [12] PEAK   price= 8678.00 time= 08-26 09:45
  [13] TROUGH price= 8442.00 time= 08-26 21:15
  [14] PEAK   price= 9480.00 time= 08-29 09:30
  [15] TROUGH price= 8622.00 time= 08-29 10:45
  [16] PEAK   price= 8750.00 time= 08-29 14:00
  [17] TROUGH price= 8680.00 time= 08-29 14:30
  [18] PEAK   price= 9074.00 time= 08-30 09:15
  [19] TROUGH price= 8960.00 time= 08-30 11:30
  [20] PEAK   price= 9043.00 time= 08-30 21:15
  [21] TROUGH price= 8960.00 time= 08-30 22:15
  [22] PEAK   price= 9034.00 time= 08-30 23:00
  [23] TROUGH price= 8971.00 time= 08-31 09:15
  [24] PEAK   price= 9120.00 time= 08-31 13:45
  [25] TROUGH price= 8981.00 time= 08-31 15:00
  [26] PEAK   price= 9148.00 time= 08-31 21:15
  [27] TROUGH price= 9050.00 time= 09-01 09:15
  [28] PEAK   price= 9198.00 time= 09-01 21:45
  [29] TROUGH price= 9000.00 time= 09-02 10:15
  [30] PEAK   price= 9390.00 time= 09-07 09:15
  [31] TROUGH price= 9050.00 time= 09-07 21:45
  [32] PEAK   price= 9145.00 time= 09-07 22:45
  [33] TROUGH price= 9089.00 time= 09-08 09:45 ← A
  [34] PEAK   price= 9688.00 time= 09-13 09:30
  [35] TROUGH price= 8701.00 time= 09-13 21:15
  [36] PEAK   price= 9990.00 time= 09-20 09:30
  [37] TROUGH price= 9570.00 time= 09-20 11:30 ← C
  [38] PEAK   price= 9850.00 time= 09-23 14:15
  [39] TROUGH price= 8895.00 time= 09-23 14:45
```

**失败详情:**
```
  ❌ C4 最新(9350.00) > C(9570.00) = False
```
---

### EB — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8348.00 @ 12-22 10:00 |
| B 价 | 8154.00 @ 12-23 13:45 |
| C 价 | 8327.00 @ 12-28 11:00 |
| 最新价 | 8680.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 39 | C 索引 | 45 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 7996.00 time= 11-16 22:00
  [ 1] PEAK   price= 8120.00 time= 11-17 11:00
  [ 2] TROUGH price= 8006.00 time= 11-17 14:00
  [ 3] PEAK   price= 8243.00 time= 11-18 13:45
  [ 4] TROUGH price= 8045.00 time= 11-18 22:00
  [ 5] PEAK   price= 8188.00 time= 11-18 23:00
  [ 6] TROUGH price= 7928.00 time= 11-22 14:00
  [ 7] PEAK   price= 8030.00 time= 11-22 22:00
  [ 8] TROUGH price= 7792.00 time= 11-23 22:00
  [ 9] PEAK   price= 8006.00 time= 11-24 14:00
  [10] TROUGH price= 7716.00 time= 11-25 11:00
  [11] PEAK   price= 7840.00 time= 11-25 22:00
  [12] TROUGH price= 7550.00 time= 11-28 21:15
  [13] PEAK   price= 7743.00 time= 11-29 13:45
  [14] TROUGH price= 7574.00 time= 11-30 09:15
  [15] PEAK   price= 7964.00 time= 12-01 11:00
  [16] TROUGH price= 7902.00 time= 12-01 21:15
  [17] PEAK   price= 8155.00 time= 12-02 11:00
  [18] TROUGH price= 8035.00 time= 12-02 22:00
  [19] PEAK   price= 8190.00 time= 12-05 09:15
  [20] TROUGH price= 8065.00 time= 12-05 14:00
  [21] PEAK   price= 8170.00 time= 12-05 21:15
  [22] TROUGH price= 7831.00 time= 12-07 11:00
  [23] PEAK   price= 7926.00 time= 12-07 21:15
  [24] TROUGH price= 7825.00 time= 12-08 09:15
  [25] PEAK   price= 8215.00 time= 12-08 21:15
  [26] TROUGH price= 8104.00 time= 12-09 10:45
  [27] PEAK   price= 8316.00 time= 12-12 11:00
  [28] TROUGH price= 8097.00 time= 12-12 21:15
  [29] PEAK   price= 8232.00 time= 12-13 14:00
  [30] TROUGH price= 8131.00 time= 12-13 21:15
  [31] PEAK   price= 8349.00 time= 12-14 21:15
  [32] TROUGH price= 8174.00 time= 12-15 10:45
  [33] PEAK   price= 8364.00 time= 12-15 21:15
  [34] TROUGH price= 8016.00 time= 12-19 14:00
  [35] PEAK   price= 8097.00 time= 12-19 21:15
  [36] TROUGH price= 8000.00 time= 12-20 09:15
  [37] PEAK   price= 8122.00 time= 12-20 10:00
  [38] TROUGH price= 8019.00 time= 12-20 13:45
  [39] PEAK   price= 8348.00 time= 12-22 10:00 ← A
  [40] TROUGH price= 8154.00 time= 12-23 13:45
  [41] PEAK   price= 8360.00 time= 12-26 11:00
  [42] TROUGH price= 8250.00 time= 12-26 21:15
  [43] PEAK   price= 8380.00 time= 12-27 21:15
  [44] TROUGH price= 8247.00 time= 12-28 10:00
  [45] PEAK   price= 8327.00 time= 12-28 11:00 ← C
  [46] TROUGH price= 8192.00 time= 12-29 11:00
  [47] PEAK   price= 8485.00 time= 01-03 09:15
  [48] TROUGH price= 8100.00 time= 01-10 22:30
  [49] PEAK   price= 8887.00 time= 01-12 13:45
```

**失败详情:**
```
  ❌ C4 最新(8680.00) < C(8327.00) = False
```
---

### EB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 8243.00 time= 11-14 09:15
  [ 1] TROUGH price= 7550.00 time= 11-28 09:15
  [ 2] PEAK   price= 8887.00 time= 01-09 11:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### EB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 7950.00 @ 05-04 22:45 |
| B 价 | 8298.00 @ 05-08 21:45 |
| C 价 | 8170.00 @ 05-09 09:15 |
| 最新价 | 7770.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 34 | C 索引 | 36 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 8726.00 time= 04-17 10:00
  [ 1] PEAK   price= 8752.00 time= 04-17 11:00
  [ 2] TROUGH price= 8682.00 time= 04-17 14:00
  [ 3] PEAK   price= 8717.00 time= 04-17 14:45
  [ 4] TROUGH price= 8580.00 time= 04-18 09:15
  [ 5] PEAK   price= 8615.00 time= 04-18 09:30
  [ 6] TROUGH price= 8573.00 time= 04-18 10:45
  [ 7] PEAK   price= 8695.00 time= 04-19 09:15
  [ 8] TROUGH price= 8521.00 time= 04-19 21:15
  [ 9] PEAK   price= 8577.00 time= 04-19 21:30
  [10] TROUGH price= 8459.00 time= 04-20 13:45
  [11] PEAK   price= 8587.00 time= 04-20 21:15
  [12] TROUGH price= 8457.00 time= 04-21 09:45
  [13] PEAK   price= 8518.00 time= 04-21 14:15
  [14] TROUGH price= 8453.00 time= 04-21 21:15
  [15] PEAK   price= 8512.00 time= 04-21 21:30
  [16] TROUGH price= 8407.00 time= 04-24 09:30
  [17] PEAK   price= 8479.00 time= 04-25 09:15
  [18] TROUGH price= 8279.00 time= 04-26 09:15
  [19] PEAK   price= 8340.00 time= 04-26 14:00
  [20] TROUGH price= 8287.00 time= 04-26 22:15
  [21] PEAK   price= 8335.00 time= 04-26 23:00
  [22] TROUGH price= 8250.00 time= 04-27 10:00
  [23] PEAK   price= 8273.00 time= 04-27 10:45
  [24] TROUGH price= 8245.00 time= 04-27 11:30
  [25] PEAK   price= 8266.00 time= 04-27 13:45
  [26] TROUGH price= 8199.00 time= 04-27 21:15
  [27] PEAK   price= 8240.00 time= 04-27 22:30
  [28] TROUGH price= 8214.00 time= 04-28 09:15
  [29] PEAK   price= 8248.00 time= 04-28 10:00
  [30] TROUGH price= 8213.00 time= 04-28 14:00
  [31] PEAK   price= 8248.00 time= 04-28 15:00
  [32] TROUGH price= 7944.00 time= 05-04 09:15
  [33] PEAK   price= 8027.00 time= 05-04 21:15
  [34] TROUGH price= 7950.00 time= 05-04 22:45 ← A
  [35] PEAK   price= 8298.00 time= 05-08 21:45
  [36] TROUGH price= 8170.00 time= 05-09 09:15 ← C
  [37] PEAK   price= 8250.00 time= 05-10 09:15
  [38] TROUGH price= 7774.00 time= 05-16 21:45
  [39] PEAK   price= 8355.00 time= 05-17 21:15
```

**失败详情:**
```
  ❌ C4 最新(7770.00) > C(8170.00) = False
```
---

### EB — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 7944.00 @ 05-04 09:15 |
| B 价 | 8027.00 @ 05-04 21:15 |
| C 价 | 7950.00 @ 05-04 22:00 |
| 最新价 | 7770.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 44 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 8246.00 time= 03-21 14:00
  [ 1] PEAK   price= 8345.00 time= 03-22 13:45
  [ 2] TROUGH price= 8271.00 time= 03-22 22:00
  [ 3] PEAK   price= 8349.00 time= 03-23 09:15
  [ 4] TROUGH price= 8209.00 time= 03-24 09:15
  [ 5] PEAK   price= 8335.00 time= 03-24 13:45
  [ 6] TROUGH price= 8243.00 time= 03-24 21:15
  [ 7] PEAK   price= 8400.00 time= 03-27 09:15
  [ 8] TROUGH price= 8364.00 time= 03-27 14:00
  [ 9] PEAK   price= 8498.00 time= 03-28 14:00
  [10] TROUGH price= 8429.00 time= 03-28 21:15
  [11] PEAK   price= 8530.00 time= 03-29 21:15
  [12] TROUGH price= 8402.00 time= 03-30 11:00
  [13] PEAK   price= 8558.00 time= 03-30 22:00
  [14] TROUGH price= 8495.00 time= 03-31 21:15
  [15] PEAK   price= 8763.00 time= 04-03 09:15
  [16] TROUGH price= 8627.00 time= 04-03 21:15
  [17] PEAK   price= 8750.00 time= 04-04 15:00
  [18] TROUGH price= 8574.00 time= 04-06 09:15
  [19] PEAK   price= 8705.00 time= 04-07 09:15
  [20] TROUGH price= 8642.00 time= 04-07 21:15
  [21] PEAK   price= 8746.00 time= 04-10 09:15
  [22] TROUGH price= 8602.00 time= 04-10 11:00
  [23] PEAK   price= 8693.00 time= 04-10 22:00
  [24] TROUGH price= 8592.00 time= 04-11 11:00
  [25] PEAK   price= 8676.00 time= 04-11 14:00
  [26] TROUGH price= 8573.00 time= 04-11 23:00
  [27] PEAK   price= 8735.00 time= 04-13 09:15
  [28] TROUGH price= 8560.00 time= 04-13 22:00
  [29] PEAK   price= 8673.00 time= 04-14 09:15
  [30] TROUGH price= 8602.00 time= 04-14 14:00
  [31] PEAK   price= 8775.00 time= 04-14 22:00
  [32] TROUGH price= 8573.00 time= 04-18 10:45
  [33] PEAK   price= 8695.00 time= 04-19 09:15
  [34] TROUGH price= 8459.00 time= 04-20 13:45
  [35] PEAK   price= 8587.00 time= 04-20 21:15
  [36] TROUGH price= 8457.00 time= 04-21 09:15
  [37] PEAK   price= 8518.00 time= 04-21 14:00
  [38] TROUGH price= 8372.00 time= 04-24 21:15
  [39] PEAK   price= 8479.00 time= 04-25 09:15
  [40] TROUGH price= 8279.00 time= 04-26 09:15
  [41] PEAK   price= 8340.00 time= 04-26 14:00
  [42] TROUGH price= 8199.00 time= 04-27 21:15
  [43] PEAK   price= 8248.00 time= 04-28 10:00
  [44] TROUGH price= 7944.00 time= 05-04 09:15 ← A
  [45] PEAK   price= 8027.00 time= 05-04 21:15
  [46] TROUGH price= 7950.00 time= 05-04 22:00 ← C
  [47] PEAK   price= 8298.00 time= 05-08 21:45
  [48] TROUGH price= 7774.00 time= 05-16 21:15
  [49] PEAK   price= 8355.00 time= 05-17 21:15
```

**失败详情:**
```
  ❌ C4 最新(7770.00) > C(7950.00) = False
```
---

### EB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9064.00 @ 09-06 09:15 |
| B 价 | 9500.00 @ 09-06 21:45 |
| C 价 | 9380.00 @ 09-07 11:30 |
| 最新价 | 9047.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 34 | C 索引 | 36 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 8611.00 time= 08-24 10:00
  [ 1] PEAK   price= 8704.00 time= 08-24 13:45
  [ 2] TROUGH price= 8520.00 time= 08-24 21:45
  [ 3] PEAK   price= 8594.00 time= 08-24 23:00
  [ 4] TROUGH price= 8541.00 time= 08-25 09:30
  [ 5] PEAK   price= 8610.00 time= 08-25 10:45
  [ 6] TROUGH price= 8493.00 time= 08-25 14:45
  [ 7] PEAK   price= 8583.00 time= 08-25 21:15
  [ 8] TROUGH price= 8460.00 time= 08-25 22:45
  [ 9] PEAK   price= 8550.00 time= 08-28 09:15
  [10] TROUGH price= 8488.00 time= 08-28 10:00
  [11] PEAK   price= 8530.00 time= 08-28 11:15
  [12] TROUGH price= 8470.00 time= 08-28 14:00
  [13] PEAK   price= 8584.00 time= 08-28 22:45
  [14] TROUGH price= 8468.00 time= 08-29 10:00
  [15] PEAK   price= 8565.00 time= 08-29 13:45
  [16] TROUGH price= 8496.00 time= 08-29 21:15
  [17] PEAK   price= 8701.00 time= 08-30 10:45
  [18] TROUGH price= 8642.00 time= 08-30 13:45
  [19] PEAK   price= 8688.00 time= 08-30 15:00
  [20] TROUGH price= 8601.00 time= 08-30 21:15
  [21] PEAK   price= 8653.00 time= 08-30 22:30
  [22] TROUGH price= 8580.00 time= 08-31 10:45
  [23] PEAK   price= 8634.00 time= 08-31 11:00
  [24] TROUGH price= 8580.00 time= 08-31 14:30
  [25] PEAK   price= 8880.00 time= 09-01 10:45
  [26] TROUGH price= 8818.00 time= 09-01 21:15
  [27] PEAK   price= 8984.00 time= 09-04 09:15
  [28] TROUGH price= 8870.00 time= 09-04 09:45
  [29] PEAK   price= 8976.00 time= 09-04 21:30
  [30] TROUGH price= 8938.00 time= 09-04 22:15
  [31] PEAK   price= 9005.00 time= 09-05 09:15
  [32] TROUGH price= 8955.00 time= 09-05 10:15
  [33] PEAK   price= 9100.00 time= 09-05 21:30
  [34] TROUGH price= 9064.00 time= 09-06 09:15 ← A
  [35] PEAK   price= 9500.00 time= 09-06 21:45
  [36] TROUGH price= 9380.00 time= 09-07 11:30 ← C
  [37] PEAK   price= 9430.00 time= 09-07 21:15
  [38] TROUGH price= 9278.00 time= 09-08 14:15
  [39] PEAK   price=10166.00 time= 09-14 14:45
```

**失败详情:**
```
  ❌ C4 最新(9047.00) > C(9380.00) = False
```
---

### EB — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8898.00 @ 09-04 14:30 |
| B 价 | 9500.00 @ 09-06 21:15 |
| C 价 | 9380.00 @ 09-07 11:30 |
| 最新价 | 9047.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 44 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 8023.00 time= 07-27 21:15
  [ 1] PEAK   price= 8405.00 time= 07-31 09:15
  [ 2] TROUGH price= 8269.00 time= 07-31 11:00
  [ 3] PEAK   price= 8464.00 time= 07-31 22:00
  [ 4] TROUGH price= 8262.00 time= 08-01 21:15
  [ 5] PEAK   price= 8492.00 time= 08-02 11:00
  [ 6] TROUGH price= 8198.00 time= 08-03 14:00
  [ 7] PEAK   price= 8437.00 time= 08-04 09:15
  [ 8] TROUGH price= 8183.00 time= 08-04 22:00
  [ 9] PEAK   price= 8315.00 time= 08-07 21:15
  [10] TROUGH price= 8174.00 time= 08-08 10:00
  [11] PEAK   price= 8352.00 time= 08-08 14:00
  [12] TROUGH price= 8226.00 time= 08-08 21:15
  [13] PEAK   price= 8394.00 time= 08-09 10:45
  [14] TROUGH price= 8323.00 time= 08-09 13:45
  [15] PEAK   price= 8532.00 time= 08-10 09:15
  [16] TROUGH price= 8431.00 time= 08-10 11:00
  [17] PEAK   price= 8546.00 time= 08-10 14:00
  [18] TROUGH price= 8382.00 time= 08-11 09:15
  [19] PEAK   price= 8507.00 time= 08-11 21:15
  [20] TROUGH price= 8221.00 time= 08-15 10:00
  [21] PEAK   price= 8325.00 time= 08-15 14:00
  [22] TROUGH price= 8242.00 time= 08-16 09:15
  [23] PEAK   price= 8362.00 time= 08-16 21:15
  [24] TROUGH price= 8213.00 time= 08-17 10:45
  [25] PEAK   price= 8689.00 time= 08-17 23:00
  [26] TROUGH price= 8423.00 time= 08-18 21:15
  [27] PEAK   price= 8696.00 time= 08-21 21:15
  [28] TROUGH price= 8574.00 time= 08-22 09:15
  [29] PEAK   price= 8643.00 time= 08-22 10:45
  [30] TROUGH price= 8502.00 time= 08-22 14:00
  [31] PEAK   price= 8745.00 time= 08-23 14:00
  [32] TROUGH price= 8576.00 time= 08-23 21:15
  [33] PEAK   price= 8704.00 time= 08-24 13:45
  [34] TROUGH price= 8520.00 time= 08-24 21:15
  [35] PEAK   price= 8610.00 time= 08-25 10:45
  [36] TROUGH price= 8460.00 time= 08-25 22:00
  [37] PEAK   price= 8584.00 time= 08-28 22:00
  [38] TROUGH price= 8468.00 time= 08-29 10:00
  [39] PEAK   price= 8701.00 time= 08-30 10:45
  [40] TROUGH price= 8580.00 time= 08-31 10:45
  [41] PEAK   price= 8880.00 time= 09-01 10:45
  [42] TROUGH price= 8818.00 time= 09-01 21:15
  [43] PEAK   price= 8984.00 time= 09-04 09:15
  [44] TROUGH price= 8898.00 time= 09-04 14:30 ← A
  [45] PEAK   price= 9500.00 time= 09-06 21:15
  [46] TROUGH price= 9380.00 time= 09-07 11:30 ← C
  [47] PEAK   price= 9430.00 time= 09-07 21:15
  [48] TROUGH price= 9278.00 time= 09-08 14:15
  [49] PEAK   price=10166.00 time= 09-14 14:45
```

**失败详情:**
```
  ❌ C4 最新(9047.00) > C(9380.00) = False
```
---

### EB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8502.00 @ 08-22 13:45 |
| B 价 | 9500.00 @ 09-06 13:45 |
| C 价 | 9278.00 @ 09-08 14:15 |
| 最新价 | 9047.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 9 | C 索引 | 13 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] PEAK   price= 7903.00 time= 07-14 09:15
  [ 1] TROUGH price= 7672.00 time= 07-17 13:45
  [ 2] PEAK   price= 8082.00 time= 07-21 13:45
  [ 3] TROUGH price= 7842.00 time= 07-24 13:45
  [ 4] PEAK   price= 8492.00 time= 08-02 10:45
  [ 5] TROUGH price= 8174.00 time= 08-08 09:15
  [ 6] PEAK   price= 8546.00 time= 08-10 13:45
  [ 7] TROUGH price= 8213.00 time= 08-17 10:45
  [ 8] PEAK   price= 8689.00 time= 08-17 13:45
  [ 9] TROUGH price= 8502.00 time= 08-22 13:45 ← A
  [10] PEAK   price= 8745.00 time= 08-23 13:45
  [11] TROUGH price= 8460.00 time= 08-25 13:45
  [12] PEAK   price= 9500.00 time= 09-06 13:45
  [13] TROUGH price= 9278.00 time= 09-08 14:15 ← C
  [14] PEAK   price=10166.00 time= 09-14 14:45
```

**失败详情:**
```
  ❌ C4 最新(9047.00) > C(9278.00) = False
```
---

### EB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8485.00 @ 12-28 10:00 |
| B 价 | 8393.00 @ 12-28 11:30 |
| C 价 | 8435.00 @ 12-28 13:45 |
| 最新价 | 9000.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 32 | C 索引 | 34 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 8165.00 time= 12-15 11:30
  [ 1] TROUGH price= 8097.00 time= 12-15 14:30
  [ 2] PEAK   price= 8146.00 time= 12-15 21:15
  [ 3] TROUGH price= 8075.00 time= 12-15 21:45
  [ 4] PEAK   price= 8198.00 time= 12-18 10:45
  [ 5] TROUGH price= 8146.00 time= 12-18 14:00
  [ 6] PEAK   price= 8250.00 time= 12-18 21:15
  [ 7] TROUGH price= 8156.00 time= 12-19 09:45
  [ 8] PEAK   price= 8200.00 time= 12-19 10:45
  [ 9] TROUGH price= 8168.00 time= 12-19 11:00
  [10] PEAK   price= 8237.00 time= 12-19 14:15
  [11] TROUGH price= 8179.00 time= 12-19 21:15
  [12] PEAK   price= 8570.00 time= 12-20 22:45
  [13] TROUGH price= 8430.00 time= 12-21 09:45
  [14] PEAK   price= 8583.00 time= 12-21 13:45
  [15] TROUGH price= 8419.00 time= 12-21 21:30
  [16] PEAK   price= 8605.00 time= 12-22 10:45
  [17] TROUGH price= 8468.00 time= 12-22 21:15
  [18] PEAK   price= 8544.00 time= 12-22 21:30
  [19] TROUGH price= 8485.00 time= 12-22 22:15
  [20] PEAK   price= 8661.00 time= 12-25 09:15
  [21] TROUGH price= 8463.00 time= 12-25 11:15
  [22] PEAK   price= 8614.00 time= 12-25 21:15
  [23] TROUGH price= 8522.00 time= 12-26 09:45
  [24] PEAK   price= 8591.00 time= 12-26 14:15
  [25] TROUGH price= 8530.00 time= 12-26 14:45
  [26] PEAK   price= 8639.00 time= 12-26 22:30
  [27] TROUGH price= 8538.00 time= 12-27 09:30
  [28] PEAK   price= 8592.00 time= 12-27 10:15
  [29] TROUGH price= 8555.00 time= 12-27 13:45
  [30] PEAK   price= 8588.00 time= 12-27 14:15
  [31] TROUGH price= 8433.00 time= 12-28 09:15
  [32] PEAK   price= 8485.00 time= 12-28 10:00 ← A
  [33] TROUGH price= 8393.00 time= 12-28 11:30
  [34] PEAK   price= 8435.00 time= 12-28 13:45 ← C
  [35] TROUGH price= 8320.00 time= 12-29 10:45
  [36] PEAK   price= 8527.00 time= 01-02 14:15
  [37] TROUGH price= 8240.00 time= 01-05 09:45
  [38] PEAK   price= 8600.00 time= 01-10 21:15
  [39] TROUGH price= 7935.00 time= 01-12 11:30
```

**失败详情:**
```
  ❌ C4 最新(9000.00) < C(8435.00) = False
```
---

### EB — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8570.00 @ 12-20 22:00 |
| B 价 | 8430.00 @ 12-21 09:15 |
| C 价 | 8527.00 @ 01-02 14:00 |
| 最新价 | 9000.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 34 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 8448.00 time= 11-23 10:45
  [ 1] TROUGH price= 8355.00 time= 11-23 22:00
  [ 2] PEAK   price= 8464.00 time= 11-24 09:15
  [ 3] TROUGH price= 8315.00 time= 11-24 14:00
  [ 4] PEAK   price= 8445.00 time= 11-27 09:15
  [ 5] TROUGH price= 8121.00 time= 11-27 22:00
  [ 6] PEAK   price= 8216.00 time= 11-28 10:00
  [ 7] TROUGH price= 8014.00 time= 11-28 22:00
  [ 8] PEAK   price= 8145.00 time= 11-29 09:15
  [ 9] TROUGH price= 8033.00 time= 11-29 14:00
  [10] PEAK   price= 8122.00 time= 11-29 22:00
  [11] TROUGH price= 8023.00 time= 11-30 10:00
  [12] PEAK   price= 8192.00 time= 11-30 21:15
  [13] TROUGH price= 7905.00 time= 12-01 11:00
  [14] PEAK   price= 7989.00 time= 12-01 21:15
  [15] TROUGH price= 7842.00 time= 12-04 09:15
  [16] PEAK   price= 8005.00 time= 12-04 10:00
  [17] TROUGH price= 7760.00 time= 12-05 09:15
  [18] PEAK   price= 7934.00 time= 12-06 10:00
  [19] TROUGH price= 7871.00 time= 12-06 14:00
  [20] PEAK   price= 8035.00 time= 12-06 15:00
  [21] TROUGH price= 7825.00 time= 12-07 09:15
  [22] PEAK   price= 8134.00 time= 12-08 10:45
  [23] TROUGH price= 8010.00 time= 12-11 09:15
  [24] PEAK   price= 8148.00 time= 12-11 14:00
  [25] TROUGH price= 7975.00 time= 12-11 22:00
  [26] PEAK   price= 8176.00 time= 12-12 14:00
  [27] TROUGH price= 7931.00 time= 12-13 15:00
  [28] PEAK   price= 8247.00 time= 12-14 09:15
  [29] TROUGH price= 8045.00 time= 12-14 22:00
  [30] PEAK   price= 8165.00 time= 12-15 11:00
  [31] TROUGH price= 8075.00 time= 12-15 21:15
  [32] PEAK   price= 8250.00 time= 12-18 21:15
  [33] TROUGH price= 8156.00 time= 12-19 09:15
  [34] PEAK   price= 8570.00 time= 12-20 22:00 ← A
  [35] TROUGH price= 8430.00 time= 12-21 09:15
  [36] PEAK   price= 8583.00 time= 12-21 13:45
  [37] TROUGH price= 8419.00 time= 12-21 21:15
  [38] PEAK   price= 8605.00 time= 12-22 10:45
  [39] TROUGH price= 8468.00 time= 12-22 21:15
  [40] PEAK   price= 8661.00 time= 12-25 09:15
  [41] TROUGH price= 8463.00 time= 12-25 11:00
  [42] PEAK   price= 8614.00 time= 12-25 21:15
  [43] TROUGH price= 8522.00 time= 12-26 09:15
  [44] PEAK   price= 8639.00 time= 12-26 22:00
  [45] TROUGH price= 8200.00 time= 01-02 09:15
  [46] PEAK   price= 8527.00 time= 01-02 14:00 ← C
  [47] TROUGH price= 8240.00 time= 01-05 09:30
  [48] PEAK   price= 8600.00 time= 01-10 21:15
  [49] TROUGH price= 7935.00 time= 01-12 11:30
```

**失败详情:**
```
  ❌ C4 最新(9000.00) < C(8527.00) = False
```
---

### EB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8818.00 @ 11-13 09:15 |
| B 价 | 7760.00 @ 12-04 09:15 |
| C 价 | 8661.00 @ 12-25 09:15 |
| 最新价 | 9000.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 4 (merge 后: 4) |
| A 索引 | 0 | C 索引 | 2 |

**极值点序列** (swing: 4, merged: 4):
```
  [ 0] PEAK   price= 8818.00 time= 11-13 09:15 ← A
  [ 1] TROUGH price= 7760.00 time= 12-04 09:15
  [ 2] PEAK   price= 8661.00 time= 12-25 09:15 ← C
  [ 3] TROUGH price= 7935.00 time= 01-09 21:15
```

**失败详情:**
```
  ❌ C4 最新(9000.00) < C(8661.00) = False
```
---

### EB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 9780.00 time= 04-15 09:15
  [ 1] TROUGH price= 9130.00 time= 05-13 09:15
  [ 2] PEAK   price=10130.00 time= 05-20 09:30
```

**失败详情:**
```
算法无有效3点结构
```
---

### EB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9105.00 @ 08-22 13:45 |
| B 价 | 9400.00 @ 08-26 13:45 |
| C 价 | 9270.00 @ 08-28 10:45 |
| 最新价 | 8890.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 16 (merge 后: 16) |
| A 索引 | 12 | C 索引 | 14 |

**极值点序列** (swing: 16, merged: 16):
```
  [ 0] TROUGH price= 9120.00 time= 07-10 10:45
  [ 1] PEAK   price= 9305.00 time= 07-11 13:45
  [ 2] TROUGH price= 9081.00 time= 07-16 13:45
  [ 3] PEAK   price= 9190.00 time= 07-18 13:45
  [ 4] TROUGH price= 8805.00 time= 07-25 13:45
  [ 5] PEAK   price= 9358.00 time= 08-01 09:15
  [ 6] TROUGH price= 9064.00 time= 08-08 13:45
  [ 7] PEAK   price= 9381.00 time= 08-13 09:15
  [ 8] TROUGH price= 9150.00 time= 08-15 09:15
  [ 9] PEAK   price= 9372.00 time= 08-15 13:45
  [10] TROUGH price= 9121.00 time= 08-20 10:45
  [11] PEAK   price= 9312.00 time= 08-21 13:45
  [12] TROUGH price= 9105.00 time= 08-22 13:45 ← A
  [13] PEAK   price= 9400.00 time= 08-26 13:45
  [14] TROUGH price= 9270.00 time= 08-28 10:45 ← C
  [15] PEAK   price= 9508.00 time= 08-30 13:45
```

**失败详情:**
```
  ❌ C4 最新(8890.00) > C(9270.00) = False
```
---

### EB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 8805.00 time= 07-22 09:15
  [ 1] PEAK   price= 9508.00 time= 08-26 09:15
  [ 2] TROUGH price= 8438.00 time= 09-09 09:45
```

**失败详情:**
```
算法无有效3点结构
```
---

### EB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8574.00 @ 12-19 13:45 |
| B 价 | 8048.00 @ 12-30 09:15 |
| C 价 | 8325.00 @ 01-03 10:45 |
| 最新价 | 8510.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 12 (merge 后: 12) |
| A 索引 | 9 | C 索引 | 11 |

**极值点序列** (swing: 12, merged: 12):
```
  [ 0] TROUGH price= 8285.00 time= 11-04 10:45
  [ 1] PEAK   price= 8495.00 time= 11-05 13:45
  [ 2] TROUGH price= 8190.00 time= 11-11 10:45
  [ 3] PEAK   price= 8324.00 time= 11-13 10:45
  [ 4] TROUGH price= 8205.00 time= 11-14 13:45
  [ 5] PEAK   price= 8488.00 time= 11-25 09:15
  [ 6] TROUGH price= 8234.00 time= 11-27 09:15
  [ 7] PEAK   price= 8575.00 time= 12-04 13:45
  [ 8] TROUGH price= 8330.00 time= 12-09 10:45
  [ 9] PEAK   price= 8574.00 time= 12-19 13:45 ← A
  [10] TROUGH price= 8048.00 time= 12-30 09:15
  [11] PEAK   price= 8325.00 time= 01-03 10:45 ← C
```

**失败详情:**
```
  ❌ C4 最新(8510.00) < C(8325.00) = False
```
---

### EB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 8190.00 time= 11-11 09:15
  [ 1] PEAK   price= 8575.00 time= 12-02 09:15
  [ 2] TROUGH price= 8048.00 time= 12-30 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### EB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8008.00 @ 04-01 13:45 |
| B 价 | 6831.00 @ 04-09 09:15 |
| C 价 | 7543.00 @ 04-14 09:15 |
| 最新价 | 7680.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 16 (merge 后: 16) |
| A 索引 | 9 | C 索引 | 11 |

**极值点序列** (swing: 16, merged: 16):
```
  [ 0] TROUGH price= 7968.00 time= 03-05 13:45
  [ 1] PEAK   price= 8198.00 time= 03-07 13:45
  [ 2] TROUGH price= 7858.00 time= 03-12 13:45
  [ 3] PEAK   price= 8097.00 time= 03-17 09:15
  [ 4] TROUGH price= 7897.00 time= 03-18 10:45
  [ 5] PEAK   price= 8012.00 time= 03-20 09:15
  [ 6] TROUGH price= 7715.00 time= 03-21 13:45
  [ 7] PEAK   price= 7933.00 time= 03-24 13:45
  [ 8] TROUGH price= 7667.00 time= 03-26 13:45
  [ 9] PEAK   price= 8008.00 time= 04-01 13:45 ← A
  [10] TROUGH price= 6831.00 time= 04-09 09:15
  [11] PEAK   price= 7543.00 time= 04-14 09:15 ← C
  [12] TROUGH price= 7272.00 time= 04-16 13:45
  [13] PEAK   price= 7509.00 time= 04-23 13:45
  [14] TROUGH price= 7058.00 time= 05-06 13:45
  [15] PEAK   price= 8035.00 time= 05-19 14:45
```

**失败详情:**
```
  ❌ C4 最新(7680.00) < C(7543.00) = False
```
---

### EB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 7042.00 @ 09-05 13:45 |
| B 价 | 6694.00 @ 09-05 22:30 |
| C 价 | 6990.00 @ 09-15 09:30 |
| 最新价 | 6990.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 37 | C 索引 | 39 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 7247.00 time= 08-21 21:15
  [ 1] PEAK   price= 7350.00 time= 08-22 09:15
  [ 2] TROUGH price= 7303.00 time= 08-22 09:45
  [ 3] PEAK   price= 7405.00 time= 08-22 22:30
  [ 4] TROUGH price= 7306.00 time= 08-25 10:00
  [ 5] PEAK   price= 7347.00 time= 08-25 11:00
  [ 6] TROUGH price= 7285.00 time= 08-25 13:45
  [ 7] PEAK   price= 7321.00 time= 08-25 14:30
  [ 8] TROUGH price= 7291.00 time= 08-25 21:15
  [ 9] PEAK   price= 7323.00 time= 08-25 22:00
  [10] TROUGH price= 7278.00 time= 08-26 09:15
  [11] PEAK   price= 7327.00 time= 08-26 10:45
  [12] TROUGH price= 7192.00 time= 08-26 21:15
  [13] PEAK   price= 7244.00 time= 08-26 22:15
  [14] TROUGH price= 7181.00 time= 08-27 10:45
  [15] PEAK   price= 7208.00 time= 08-27 11:15
  [16] TROUGH price= 7080.00 time= 08-27 21:45
  [17] PEAK   price= 7117.00 time= 08-27 22:45
  [18] TROUGH price= 7087.00 time= 08-28 09:15
  [19] PEAK   price= 7127.00 time= 08-28 10:45
  [20] TROUGH price= 7101.00 time= 08-28 13:45
  [21] PEAK   price= 7136.00 time= 08-28 21:15
  [22] TROUGH price= 7061.00 time= 08-28 22:45
  [23] PEAK   price= 7093.00 time= 08-29 09:15
  [24] TROUGH price= 7006.00 time= 08-29 11:15
  [25] PEAK   price= 7031.00 time= 08-29 21:15
  [26] TROUGH price= 6867.00 time= 09-01 13:45
  [27] PEAK   price= 6942.00 time= 09-01 14:30
  [28] TROUGH price= 6887.00 time= 09-01 23:00
  [29] PEAK   price= 6890.00 time= 09-02 14:00
  [30] TROUGH price= 6865.00 time= 09-02 21:15
  [31] PEAK   price= 6906.00 time= 09-02 21:30
  [32] TROUGH price= 6870.00 time= 09-03 09:15
  [33] PEAK   price= 6985.00 time= 09-03 14:45
  [34] TROUGH price= 6900.00 time= 09-03 21:15
  [35] PEAK   price= 6935.00 time= 09-03 22:30
  [36] TROUGH price= 6890.00 time= 09-04 15:00
  [37] PEAK   price= 7042.00 time= 09-05 13:45 ← A
  [38] TROUGH price= 6694.00 time= 09-05 22:30
  [39] PEAK   price= 6990.00 time= 09-15 09:30 ← C
```

**失败详情:**
```
  ❌ C4 最新(6990.00) < C(6990.00) = False
```
---

### EB — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 7042.00 @ 09-05 13:45 |
| B 价 | 6694.00 @ 09-05 22:00 |
| C 价 | 6990.00 @ 09-15 09:30 |
| 最新价 | 6990.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 49) |
| A 索引 | 46 | C 索引 | 48 |

**极值点序列** (swing: 50, merged: 49):
```
  [ 0] PEAK   price= 7442.00 time= 07-30 09:15
  [ 1] TROUGH price= 7282.00 time= 07-31 21:15
  [ 2] PEAK   price= 7373.00 time= 07-31 22:00
  [ 3] TROUGH price= 7215.00 time= 08-04 09:15
  [ 4] PEAK   price= 7315.00 time= 08-04 14:00
  [ 5] TROUGH price= 7243.00 time= 08-04 21:15
  [ 6] PEAK   price= 7288.00 time= 08-05 10:00
  [ 7] TROUGH price= 7243.00 time= 08-05 11:00
  [ 8] PEAK   price= 7299.00 time= 08-05 14:00
  [ 9] TROUGH price= 7234.00 time= 08-05 22:00
  [10] PEAK   price= 7331.00 time= 08-06 10:45
  [11] TROUGH price= 7278.00 time= 08-06 15:00
  [12] PEAK   price= 7355.00 time= 08-06 22:00
  [13] TROUGH price= 7274.00 time= 08-07 10:45
  [14] PEAK   price= 7315.00 time= 08-07 11:00
  [15] TROUGH price= 7208.00 time= 08-08 22:00
  [16] PEAK   price= 7360.00 time= 08-12 13:45
  [17] TROUGH price= 7271.00 time= 08-12 22:00
  [18] PEAK   price= 7327.00 time= 08-13 09:15
  [19] TROUGH price= 7280.00 time= 08-13 11:00
  [20] PEAK   price= 7325.00 time= 08-13 22:00
  [21] TROUGH price= 7223.00 time= 08-14 15:00
  [22] PEAK   price= 7269.00 time= 08-14 21:15
  [23] TROUGH price= 7190.00 time= 08-15 09:15
  [24] PEAK   price= 7260.00 time= 08-15 14:00
  [25] TROUGH price= 7180.00 time= 08-18 09:15
  [26] PEAK   price= 7242.00 time= 08-19 09:15
  [27] TROUGH price= 7205.00 time= 08-19 10:45
  [28] PEAK   price= 7252.00 time= 08-19 13:45
  [29] TROUGH price= 7160.00 time= 08-19 22:00
  [30] PEAK   price= 7200.00 time= 08-20 10:00
  [31] TROUGH price= 7135.00 time= 08-20 11:00
  [32] PEAK   price= 7318.00 time= 08-20 14:00
  [33] TROUGH price= 7247.00 time= 08-21 21:15
  [34] PEAK   price= 7405.00 time= 08-22 22:00
  [35] TROUGH price= 7285.00 time= 08-25 13:45
  [36] PEAK   price= 7323.00 time= 08-25 22:00
  [37] TROUGH price= 7278.00 time= 08-26 09:15
  [38] PEAK   price= 7327.00 time= 08-26 10:45
  [39] TROUGH price= 7080.00 time= 08-27 21:15
  [40] PEAK   price= 7136.00 time= 08-28 21:15
  [41] TROUGH price= 6867.00 time= 09-01 13:45
  [42] PEAK   price= 6942.00 time= 09-01 14:00
  [43] TROUGH price= 6865.00 time= 09-02 21:15
  [44] PEAK   price= 6985.00 time= 09-03 14:00
  [45] TROUGH price= 6890.00 time= 09-04 15:00
  [46] PEAK   price= 7042.00 time= 09-05 13:45 ← A
  [47] TROUGH price= 6694.00 time= 09-05 22:00
  [48] PEAK   price= 6990.00 time= 09-15 09:30 ← C
```

**失败详情:**
```
  ❌ C4 最新(6990.00) < C(6990.00) = False
```
---

### FG — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 984.00 @ 06-12 14:00 |
| B 价 | 1020.00 @ 06-15 11:00 |
| C 价 | 999.00 @ 06-16 14:00 |
| 最新价 | 978.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 33) |
| A 索引 | 28 | C 索引 | 30 |

**极值点序列** (swing: 50, merged: 33):
```
  [ 0] TROUGH price= 1058.00 time= 05-13 13:45
  [ 1] PEAK   price= 1070.00 time= 05-13 14:00
  [ 2] TROUGH price= 1041.00 time= 05-14 11:00
  [ 3] PEAK   price= 1055.00 time= 05-14 22:00
  [ 4] TROUGH price= 1021.00 time= 05-18 09:15
  [ 5] PEAK   price= 1045.00 time= 05-18 10:00
  [ 6] TROUGH price= 1007.00 time= 05-20 13:45
  [ 7] PEAK   price= 1040.00 time= 05-21 11:00
  [ 8] TROUGH price= 1013.00 time= 05-22 11:00
  [ 9] PEAK   price= 1056.00 time= 05-25 09:15
  [10] TROUGH price= 1017.00 time= 05-26 14:00
  [11] PEAK   price= 1042.00 time= 05-27 14:00
  [12] TROUGH price= 1032.00 time= 05-28 09:15
  [13] PEAK   price= 1054.00 time= 05-29 10:45
  [14] TROUGH price= 1044.00 time= 05-29 14:00
  [15] PEAK   price= 1065.00 time= 05-29 22:00
  [16] TROUGH price= 1037.00 time= 06-02 10:00
  [17] PEAK   price= 1054.00 time= 06-02 22:00
  [18] TROUGH price= 1042.00 time= 06-03 10:45
  [19] PEAK   price= 1052.00 time= 06-03 21:15
  [20] TROUGH price= 1000.00 time= 06-08 10:00
  [21] PEAK   price= 1011.00 time= 06-08 14:00
  [22] TROUGH price=  983.00 time= 06-10 09:12
  [23] PEAK   price=  999.00 time= 06-10 10:00
  [24] TROUGH price=  982.00 time= 06-11 09:00
  [25] PEAK   price=  998.00 time= 06-11 13:30
  [26] TROUGH price=  984.00 time= 06-12 09:00
  [27] PEAK   price=  995.00 time= 06-12 11:00
  [28] TROUGH price=  984.00 time= 06-12 14:00 ← A
  [29] PEAK   price= 1020.00 time= 06-15 11:00
  [30] TROUGH price=  999.00 time= 06-16 14:00 ← C
  [31] PEAK   price= 1014.00 time= 06-16 21:15
  [32] TROUGH price=  975.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(978.00) > C(999.00) = False
```
---

### FG — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | LONG (状态: LEG2) |
| DB 重复行 | 否 |
| 极值点数量 | 6 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 6, merged: 3):
```
  [ 0] TROUGH price= 1047.00 time= 04-13 08:00
  [ 1] PEAK   price= 1104.00 time= 04-20 08:00
  [ 2] TROUGH price=  975.00 time= 06-15 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### I — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 760.00 @ 08-20 00:00 |
| B 价 | 820.00 @ 09-22 00:00 |
| C 价 | 777.00 @ 05-27 00:00 |
| 最新价 | 771.50 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 60 (merge 后: 60) |
| A 索引 | 47 | C 索引 | 59 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] PEAK   price=  865.50 time= 09-04 00:00
  [ 1] TROUGH price=  823.50 time= 09-08 00:00
  [ 2] PEAK   price=  881.50 time= 09-15 00:00
  [ 3] TROUGH price=  812.50 time= 10-10 00:00
  [ 4] PEAK   price=  995.00 time= 11-15 00:00
  [ 5] TROUGH price=  945.00 time= 11-20 00:00
  [ 6] PEAK   price=  998.50 time= 11-23 00:00
  [ 7] TROUGH price=  900.50 time= 12-06 00:00
  [ 8] PEAK   price= 1025.50 time= 01-03 00:00
  [ 9] TROUGH price=  920.50 time= 01-18 00:00
  [10] PEAK   price= 1006.00 time= 01-29 00:00
  [11] TROUGH price=  762.00 time= 03-18 00:00
  [12] PEAK   price=  854.50 time= 03-25 00:00
  [13] TROUGH price=  728.00 time= 04-01 00:00
  [14] PEAK   price=  902.00 time= 05-07 00:00
  [15] TROUGH price=  851.00 time= 05-15 00:00
  [16] PEAK   price=  925.50 time= 05-22 00:00
  [17] TROUGH price=  797.00 time= 06-13 00:00
  [18] PEAK   price=  840.00 time= 06-18 00:00
  [19] TROUGH price=  791.00 time= 06-25 00:00
  [20] PEAK   price=  870.00 time= 07-04 00:00
  [21] TROUGH price=  688.50 time= 08-19 00:00
  [22] PEAK   price=  767.50 time= 08-30 00:00
  [23] TROUGH price=  662.00 time= 09-09 00:00
  [24] PEAK   price=  712.50 time= 09-13 00:00
  [25] TROUGH price=  657.50 time= 09-24 00:00
  [26] PEAK   price=  844.50 time= 10-08 00:00
  [27] TROUGH price=  739.50 time= 10-24 00:00
  [28] PEAK   price=  801.00 time= 11-08 00:00
  [29] TROUGH price=  734.00 time= 11-18 00:00
  [30] PEAK   price=  833.00 time= 12-10 00:00
  [31] TROUGH price=  743.00 time= 01-09 00:00
  [32] PEAK   price=  830.50 time= 02-11 00:00
  [33] TROUGH price=  790.00 time= 02-17 00:00
  [34] PEAK   price=  844.00 time= 02-21 00:00
  [35] TROUGH price=  753.50 time= 03-21 00:00
  [36] PEAK   price=  797.00 time= 04-01 00:00
  [37] TROUGH price=  670.50 time= 04-09 00:00
  [38] PEAK   price=  731.00 time= 04-23 00:00
  [39] TROUGH price=  691.00 time= 05-08 00:00
  [40] PEAK   price=  738.50 time= 05-15 00:00
  [41] TROUGH price=  690.50 time= 06-03 00:00
  [42] PEAK   price=  713.50 time= 06-06 00:00
  [43] TROUGH price=  689.50 time= 06-16 00:00
  [44] PEAK   price=  835.50 time= 07-22 00:00
  [45] TROUGH price=  770.50 time= 08-08 00:00
  [46] PEAK   price=  803.50 time= 08-13 00:00
  [47] TROUGH price=  760.00 time= 08-20 00:00 ← A
  [48] PEAK   price=  820.00 time= 09-22 00:00
  [49] TROUGH price=  760.00 time= 10-21 00:00
  [50] PEAK   price=  810.50 time= 10-30 00:00
  [51] TROUGH price=  756.00 time= 11-10 00:00
  [52] PEAK   price=  804.50 time= 12-02 00:00
  [53] TROUGH price=  748.00 time= 12-15 00:00
  [54] PEAK   price=  831.50 time= 01-08 00:00
  [55] TROUGH price=  736.00 time= 02-24 00:00
  [56] PEAK   price=  831.00 time= 03-25 00:00
  [57] TROUGH price=  748.50 time= 04-09 00:00
  [58] PEAK   price=  826.50 time= 05-11 00:00
  [59] TROUGH price=  777.00 time= 05-27 00:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(771.50) > C(777.00) = False
```
---

### I — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 780.50 @ 02-07 08:00 |
| B 价 | 624.00 @ 02-21 08:00 |
| C 价 | 755.00 @ 08-08 08:00 |
| 最新价 | 865.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 11 (merge 后: 11) |
| A 索引 | 0 | C 索引 | 6 |

**极值点序列** (swing: 11, merged: 11):
```
  [ 0] PEAK   price=  780.50 time= 02-07 08:00 ← A
  [ 1] TROUGH price=  624.00 time= 02-21 08:00
  [ 2] PEAK   price=  915.00 time= 04-06 08:00
  [ 3] TROUGH price=  711.00 time= 05-09 08:00
  [ 4] PEAK   price=  882.50 time= 06-06 08:00
  [ 5] TROUGH price=  598.00 time= 07-11 08:00
  [ 6] PEAK   price=  755.00 time= 08-08 08:00 ← C
  [ 7] TROUGH price=  652.00 time= 08-29 08:00
  [ 8] PEAK   price=  745.50 time= 10-10 08:00
  [ 9] TROUGH price=  599.50 time= 10-31 08:00
  [10] PEAK   price=  900.00 time= 01-09 08:00
```

**失败详情:**
```
  ❌ C4 最新(865.00) < C(755.00) = False
```
---

### I — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 623.50 @ 08-29 08:00 |
| B 价 | 936.00 @ 03-13 08:00 |
| C 价 | 844.00 @ 03-20 08:00 |
| 最新价 | 839.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 9 (merge 后: 9) |
| A 索引 | 3 | C 索引 | 7 |

**极值点序列** (swing: 9, merged: 9):
```
  [ 0] PEAK   price=  846.00 time= 06-06 08:00
  [ 1] TROUGH price=  590.00 time= 07-11 08:00
  [ 2] PEAK   price=  732.00 time= 08-08 08:00
  [ 3] TROUGH price=  623.50 time= 08-29 08:00 ← A
  [ 4] PEAK   price=  702.50 time= 10-10 08:00
  [ 5] TROUGH price=  577.00 time= 10-31 08:00
  [ 6] PEAK   price=  936.00 time= 03-13 08:00
  [ 7] TROUGH price=  844.00 time= 03-20 08:00 ← C
  [ 8] PEAK   price=  914.00 time= 04-17 08:00
```

**失败详情:**
```
  ❌ C4 最新(839.00) > C(844.00) = False
```
---

### I — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 884.00 @ 03-13 08:00 |
| B 价 | 665.50 @ 05-22 08:00 |
| C 价 | 875.50 @ 07-24 08:00 |
| 最新价 | 940.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 8 (merge 后: 8) |
| A 索引 | 4 | C 索引 | 6 |

**极值点序列** (swing: 8, merged: 8):
```
  [ 0] PEAK   price=  677.00 time= 10-10 08:00
  [ 1] TROUGH price=  554.00 time= 10-31 08:00
  [ 2] PEAK   price=  859.00 time= 01-30 08:00
  [ 3] TROUGH price=  789.50 time= 02-13 08:00
  [ 4] PEAK   price=  884.00 time= 03-13 08:00 ← A
  [ 5] TROUGH price=  665.50 time= 05-22 08:00
  [ 6] PEAK   price=  875.50 time= 07-24 08:00 ← C
  [ 7] TROUGH price=  808.00 time= 08-07 08:00
```

**失败详情:**
```
  ❌ C4 最新(940.00) < C(875.50) = False
```
---

### I — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 820.00 @ 09-22 08:00 |
| B 价 | 760.00 @ 10-21 08:00 |
| C 价 | 810.50 @ 10-30 08:00 |
| 最新价 | 832.50 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 21 (merge 后: 21) |
| A 索引 | 15 | C 索引 | 17 |

**极值点序列** (swing: 21, merged: 21):
```
  [ 0] TROUGH price=  738.00 time= 02-05 08:00
  [ 1] PEAK   price=  769.50 time= 02-13 08:00
  [ 2] TROUGH price=  726.00 time= 02-17 08:00
  [ 3] PEAK   price=  772.50 time= 02-21 08:00
  [ 4] TROUGH price=  697.50 time= 03-21 08:00
  [ 5] PEAK   price=  732.00 time= 04-01 08:00
  [ 6] TROUGH price=  652.00 time= 04-09 08:00
  [ 7] PEAK   price=  702.00 time= 04-23 08:00
  [ 8] TROUGH price=  665.50 time= 05-08 08:00
  [ 9] PEAK   price=  701.50 time= 05-15 08:00
  [10] TROUGH price=  655.00 time= 06-03 08:00
  [11] PEAK   price=  806.00 time= 07-22 08:00
  [12] TROUGH price=  749.00 time= 07-31 08:00
  [13] PEAK   price=  803.50 time= 08-13 08:00
  [14] TROUGH price=  760.00 time= 08-20 08:00
  [15] PEAK   price=  820.00 time= 09-22 08:00 ← A
  [16] TROUGH price=  760.00 time= 10-21 08:00
  [17] PEAK   price=  810.50 time= 10-30 08:00 ← C
  [18] TROUGH price=  756.00 time= 11-10 08:00
  [19] PEAK   price=  804.50 time= 12-02 08:00
  [20] TROUGH price=  741.50 time= 01-06 08:00
```

**失败详情:**
```
  ❌ C4 最新(832.50) < C(810.50) = False
```
---

### I — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 820.00 @ 09-22 08:00 |
| B 价 | 756.00 @ 11-10 08:00 |
| C 价 | 804.50 @ 12-01 08:00 |
| 最新价 | 832.50 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 10 (merge 后: 10) |
| A 索引 | 6 | C 索引 | 8 |

**极值点序列** (swing: 10, merged: 10):
```
  [ 0] PEAK   price=  772.50 time= 02-17 08:00
  [ 1] TROUGH price=  697.50 time= 03-17 08:00
  [ 2] PEAK   price=  732.00 time= 03-31 08:00
  [ 3] TROUGH price=  652.00 time= 04-07 08:00
  [ 4] PEAK   price=  701.50 time= 05-12 08:00
  [ 5] TROUGH price=  655.00 time= 06-03 08:00
  [ 6] PEAK   price=  820.00 time= 09-22 08:00 ← A
  [ 7] TROUGH price=  756.00 time= 11-10 08:00
  [ 8] PEAK   price=  804.50 time= 12-01 08:00 ← C
  [ 9] TROUGH price=  741.50 time= 01-05 08:00
```

**失败详情:**
```
  ❌ C4 最新(832.50) < C(804.50) = False
```
---

### JD — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3688.00 @ 11-05 00:00 |
| B 价 | 3500.00 @ 11-19 00:00 |
| C 价 | 3530.00 @ 03-24 00:00 |
| 最新价 | 4748.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 80 (merge 后: 80) |
| A 索引 | 63 | C 索引 | 77 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price= 4020.00 time= 06-12 00:00
  [ 1] PEAK   price= 4274.00 time= 06-26 00:00
  [ 2] TROUGH price= 3752.00 time= 07-31 00:00
  [ 3] PEAK   price= 4410.00 time= 11-20 00:00
  [ 4] TROUGH price= 3390.00 time= 01-02 00:00
  [ 5] PEAK   price= 3531.00 time= 01-08 00:00
  [ 6] TROUGH price= 3260.00 time= 02-11 00:00
  [ 7] PEAK   price= 3559.00 time= 03-12 00:00
  [ 8] TROUGH price= 3413.00 time= 03-26 00:00
  [ 9] PEAK   price= 4578.00 time= 05-28 00:00
  [10] TROUGH price= 4288.00 time= 06-25 00:00
  [11] PEAK   price= 4908.00 time= 07-16 00:00
  [12] TROUGH price= 4115.00 time= 08-06 00:00
  [13] PEAK   price= 4645.00 time= 09-17 00:00
  [14] TROUGH price= 4298.00 time= 09-24 00:00
  [15] PEAK   price= 4925.00 time= 10-22 00:00
  [16] TROUGH price= 3373.00 time= 01-07 00:00
  [17] PEAK   price= 4093.00 time= 02-04 00:00
  [18] TROUGH price= 2951.00 time= 03-17 00:00
  [19] PEAK   price= 3499.00 time= 04-07 00:00
  [20] TROUGH price= 2530.00 time= 05-26 00:00
  [21] PEAK   price= 4382.00 time= 07-21 00:00
  [22] TROUGH price= 3320.00 time= 09-01 00:00
  [23] PEAK   price= 4136.00 time= 10-27 00:00
  [24] TROUGH price= 3628.00 time= 11-24 00:00
  [25] PEAK   price= 4730.00 time= 02-18 00:00
  [26] TROUGH price= 4108.00 time= 04-06 00:00
  [27] PEAK   price= 5081.00 time= 04-20 00:00
  [28] TROUGH price= 4645.00 time= 06-01 00:00
  [29] PEAK   price= 4897.00 time= 06-15 00:00
  [30] TROUGH price= 4229.00 time= 08-17 00:00
  [31] PEAK   price= 4796.00 time= 10-19 00:00
  [32] TROUGH price= 4430.00 time= 11-02 00:00
  [33] PEAK   price= 4650.00 time= 11-16 00:00
  [34] TROUGH price= 4033.00 time= 12-14 00:00
  [35] PEAK   price= 4189.00 time= 01-04 00:00
  [36] TROUGH price= 4006.00 time= 01-18 00:00
  [37] PEAK   price= 4462.00 time= 03-08 00:00
  [38] TROUGH price= 4204.00 time= 03-15 00:00
  [39] PEAK   price= 4969.00 time= 04-06 00:00
  [40] TROUGH price= 3957.00 time= 08-09 00:00
  [41] PEAK   price= 4566.00 time= 10-11 00:00
  [42] TROUGH price= 4211.00 time= 11-08 00:00
  [43] PEAK   price= 4516.00 time= 11-29 00:00
  [44] TROUGH price= 4155.00 time= 12-20 00:00
  [45] PEAK   price= 4490.00 time= 01-31 00:00
  [46] TROUGH price= 4291.00 time= 02-14 00:00
  [47] PEAK   price= 4477.00 time= 03-14 00:00
  [48] TROUGH price= 4031.00 time= 06-13 00:00
  [49] PEAK   price= 4479.00 time= 08-01 00:00
  [50] TROUGH price= 4116.00 time= 08-15 00:00
  [51] PEAK   price= 4697.00 time= 09-19 00:00
  [52] TROUGH price= 4165.00 time= 11-07 00:00
  [53] PEAK   price= 4425.00 time= 11-21 00:00
  [54] TROUGH price= 3182.00 time= 01-23 00:00
  [55] PEAK   price= 3657.00 time= 03-05 00:00
  [56] TROUGH price= 3122.00 time= 04-02 00:00
  [57] PEAK   price= 4145.00 time= 05-07 00:00
  [58] TROUGH price= 3842.00 time= 06-18 00:00
  [59] PEAK   price= 4149.00 time= 07-02 00:00
  [60] TROUGH price= 3868.00 time= 07-23 00:00
  [61] PEAK   price= 4075.00 time= 07-30 00:00
  [62] TROUGH price= 3434.00 time= 10-08 00:00
  [63] PEAK   price= 3688.00 time= 11-05 00:00 ← A
  [64] TROUGH price= 3500.00 time= 11-19 00:00
  [65] PEAK   price= 3745.00 time= 12-10 00:00
  [66] TROUGH price= 3171.00 time= 01-07 00:00
  [67] PEAK   price= 3344.00 time= 02-05 00:00
  [68] TROUGH price= 2872.00 time= 04-01 00:00
  [69] PEAK   price= 3094.00 time= 04-15 00:00
  [70] TROUGH price= 2869.00 time= 05-27 00:00
  [71] PEAK   price= 3691.00 time= 07-22 00:00
  [72] TROUGH price= 2907.00 time= 09-02 00:00
  [73] PEAK   price= 3197.00 time= 09-09 00:00
  [74] TROUGH price= 2771.00 time= 10-09 00:00
  [75] PEAK   price= 3420.00 time= 11-11 00:00
  [76] TROUGH price= 2873.00 time= 12-23 00:00
  [77] PEAK   price= 3530.00 time= 03-24 00:00 ← C
  [78] TROUGH price= 3165.00 time= 04-07 00:00
  [79] PEAK   price= 4936.00 time= 05-26 00:00
```

**失败详情:**
```
  ❌ C4 最新(4748.00) < C(3530.00) = False
```
---

### JD — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4271.00 @ 06-17 09:15 |
| B 价 | 4307.00 @ 06-17 10:45 |
| C 价 | 4278.00 @ 06-17 13:45 |
| 最新价 | 4168.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 27) |
| A 索引 | 22 | C 索引 | 24 |

**极值点序列** (swing: 40, merged: 27):
```
  [ 0] TROUGH price= 4355.00 time= 06-03 09:30
  [ 1] PEAK   price= 4416.00 time= 06-03 10:00
  [ 2] TROUGH price= 4368.00 time= 06-03 11:15
  [ 3] PEAK   price= 4415.00 time= 06-03 14:15
  [ 4] TROUGH price= 4388.00 time= 06-03 15:00
  [ 5] PEAK   price= 4482.00 time= 06-04 09:45
  [ 6] TROUGH price= 4278.00 time= 06-05 09:15
  [ 7] PEAK   price= 4395.00 time= 06-05 14:00
  [ 8] TROUGH price= 4260.00 time= 06-08 10:45
  [ 9] PEAK   price= 4294.00 time= 06-08 13:30
  [10] TROUGH price= 4205.00 time= 06-09 10:00
  [11] PEAK   price= 4367.00 time= 06-10 09:30
  [12] TROUGH price= 4276.00 time= 06-10 10:45
  [13] PEAK   price= 4338.00 time= 06-10 14:00
  [14] TROUGH price= 4215.00 time= 06-12 09:00
  [15] PEAK   price= 4281.00 time= 06-12 10:45
  [16] TROUGH price= 4233.00 time= 06-12 13:30
  [17] PEAK   price= 4267.00 time= 06-12 14:45
  [18] TROUGH price= 4185.00 time= 06-15 09:15
  [19] PEAK   price= 4303.00 time= 06-16 09:30
  [20] TROUGH price= 4271.00 time= 06-16 10:45
  [21] PEAK   price= 4293.00 time= 06-16 11:15
  [22] TROUGH price= 4271.00 time= 06-17 09:15 ← A
  [23] PEAK   price= 4307.00 time= 06-17 10:45
  [24] TROUGH price= 4278.00 time= 06-17 13:45 ← C
  [25] PEAK   price= 4299.00 time= 06-17 14:45
  [26] TROUGH price= 4152.00 time= 06-18 13:45
```

**失败详情:**
```
  ❌ C4 最新(4168.00) > C(4278.00) = False
```
---

### JD — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4215.00 @ 06-12 09:00 |
| B 价 | 4281.00 @ 06-12 10:30 |
| C 价 | 4271.00 @ 06-17 09:15 |
| 最新价 | 4168.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 38) |
| A 索引 | 31 | C 索引 | 35 |

**极值点序列** (swing: 50, merged: 38):
```
  [ 0] PEAK   price= 3543.00 time= 04-23 11:00
  [ 1] TROUGH price= 3491.00 time= 04-24 10:00
  [ 2] PEAK   price= 3574.00 time= 04-28 10:00
  [ 3] TROUGH price= 3547.00 time= 04-28 13:45
  [ 4] PEAK   price= 3671.00 time= 04-30 11:00
  [ 5] TROUGH price= 3592.00 time= 04-30 14:00
  [ 6] PEAK   price= 3653.00 time= 05-06 09:15
  [ 7] TROUGH price= 3554.00 time= 05-06 14:00
  [ 8] PEAK   price= 3663.00 time= 05-08 09:15
  [ 9] TROUGH price= 3580.00 time= 05-08 15:00
  [10] PEAK   price= 3784.00 time= 05-12 10:00
  [11] TROUGH price= 3682.00 time= 05-13 13:45
  [12] PEAK   price= 3814.00 time= 05-15 09:15
  [13] TROUGH price= 3717.00 time= 05-18 09:15
  [14] PEAK   price= 3844.00 time= 05-19 11:00
  [15] TROUGH price= 3783.00 time= 05-19 13:45
  [16] PEAK   price= 4020.00 time= 05-22 15:00
  [17] TROUGH price= 3891.00 time= 05-25 14:00
  [18] PEAK   price= 4132.00 time= 05-27 10:45
  [19] TROUGH price= 4055.00 time= 05-28 11:15
  [20] PEAK   price= 4454.00 time= 06-02 09:15
  [21] TROUGH price= 4354.00 time= 06-02 14:00
  [22] PEAK   price= 4482.00 time= 06-04 09:15
  [23] TROUGH price= 4275.00 time= 06-05 10:00
  [24] PEAK   price= 4395.00 time= 06-05 14:00
  [25] TROUGH price= 4205.00 time= 06-09 10:00
  [26] PEAK   price= 4367.00 time= 06-10 09:00
  [27] TROUGH price= 4276.00 time= 06-10 10:30
  [28] PEAK   price= 4357.00 time= 06-10 11:15
  [29] TROUGH price= 4260.00 time= 06-11 10:30
  [30] PEAK   price= 4294.00 time= 06-11 11:15
  [31] TROUGH price= 4215.00 time= 06-12 09:00 ← A
  [32] PEAK   price= 4281.00 time= 06-12 10:30
  [33] TROUGH price= 4185.00 time= 06-15 09:15
  [34] PEAK   price= 4303.00 time= 06-16 09:15
  [35] TROUGH price= 4271.00 time= 06-17 09:15 ← C
  [36] PEAK   price= 4307.00 time= 06-17 10:45
  [37] TROUGH price= 4152.00 time= 06-18 13:45
```

**失败详情:**
```
  ❌ C4 最新(4168.00) > C(4271.00) = False
```
---

### L — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 7365.00 time= 12-02 09:15
  [ 1] TROUGH price= 7085.00 time= 12-30 09:15
  [ 2] PEAK   price= 7380.00 time= 01-06 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### L — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 7310.00 @ 08-04 13:45 |
| B 价 | 6935.00 @ 08-13 13:45 |
| C 价 | 7210.00 @ 08-20 13:45 |
| 最新价 | 7330.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 11 (merge 后: 11) |
| A 索引 | 6 | C 索引 | 8 |

**极值点序列** (swing: 11, merged: 11):
```
  [ 0] PEAK   price= 7485.00 time= 07-07 13:45
  [ 1] TROUGH price= 7150.00 time= 07-10 13:45
  [ 2] PEAK   price= 7430.00 time= 07-13 13:45
  [ 3] TROUGH price= 6905.00 time= 07-24 13:45
  [ 4] PEAK   price= 7170.00 time= 07-29 09:15
  [ 5] TROUGH price= 6930.00 time= 07-30 13:45
  [ 6] PEAK   price= 7310.00 time= 08-04 13:45 ← A
  [ 7] TROUGH price= 6935.00 time= 08-13 13:45
  [ 8] PEAK   price= 7210.00 time= 08-20 13:45 ← C
  [ 9] TROUGH price= 7040.00 time= 08-24 09:15
  [10] PEAK   price= 7840.00 time= 09-02 13:45
```

**失败详情:**
```
  ❌ C4 最新(7330.00) < C(7210.00) = False
```
---

### L — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 6905.00 @ 07-20 09:15 |
| B 价 | 7840.00 @ 08-31 09:15 |
| C 价 | 7330.00 @ 09-07 09:15 |
| 最新价 | 7330.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | 0 | C 索引 | 2 |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 6905.00 time= 07-20 09:15 ← A
  [ 1] PEAK   price= 7840.00 time= 08-31 09:15
  [ 2] TROUGH price= 7330.00 time= 09-07 09:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(7330.00) > C(7330.00) = False
```
---

### L — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8250.00 @ 04-30 14:00 |
| B 价 | 8610.00 @ 05-07 13:45 |
| C 价 | 8350.00 @ 05-11 10:00 |
| 最新价 | 7920.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 42 | C 索引 | 44 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 8480.00 time= 03-25 14:00
  [ 1] PEAK   price= 8650.00 time= 03-25 22:00
  [ 2] TROUGH price= 8525.00 time= 03-26 11:00
  [ 3] PEAK   price= 8810.00 time= 03-26 23:00
  [ 4] TROUGH price= 8560.00 time= 03-29 14:00
  [ 5] PEAK   price= 8730.00 time= 03-30 10:00
  [ 6] TROUGH price= 8500.00 time= 03-30 21:15
  [ 7] PEAK   price= 8595.00 time= 03-31 09:15
  [ 8] TROUGH price= 8410.00 time= 04-01 09:15
  [ 9] PEAK   price= 8650.00 time= 04-01 21:15
  [10] TROUGH price= 8550.00 time= 04-01 23:00
  [11] PEAK   price= 8755.00 time= 04-02 14:00
  [12] TROUGH price= 8615.00 time= 04-06 11:00
  [13] PEAK   price= 8850.00 time= 04-06 22:00
  [14] TROUGH price= 8765.00 time= 04-07 10:00
  [15] PEAK   price= 8905.00 time= 04-07 14:00
  [16] TROUGH price= 8520.00 time= 04-09 09:15
  [17] PEAK   price= 8605.00 time= 04-09 14:00
  [18] TROUGH price= 8160.00 time= 04-13 15:00
  [19] PEAK   price= 8255.00 time= 04-13 21:15
  [20] TROUGH price= 8145.00 time= 04-14 11:00
  [21] PEAK   price= 8400.00 time= 04-14 23:00
  [22] TROUGH price= 8270.00 time= 04-15 13:45
  [23] PEAK   price= 8465.00 time= 04-16 10:00
  [24] TROUGH price= 8310.00 time= 04-16 14:00
  [25] PEAK   price= 8455.00 time= 04-19 11:00
  [26] TROUGH price= 8320.00 time= 04-19 14:00
  [27] PEAK   price= 8425.00 time= 04-19 21:15
  [28] TROUGH price= 8095.00 time= 04-21 21:15
  [29] PEAK   price= 8215.00 time= 04-21 22:00
  [30] TROUGH price= 8135.00 time= 04-22 10:45
  [31] PEAK   price= 8215.00 time= 04-22 21:15
  [32] TROUGH price= 8125.00 time= 04-23 09:15
  [33] PEAK   price= 8290.00 time= 04-26 13:45
  [34] TROUGH price= 8120.00 time= 04-26 22:00
  [35] PEAK   price= 8310.00 time= 04-27 21:15
  [36] TROUGH price= 8225.00 time= 04-28 09:15
  [37] PEAK   price= 8345.00 time= 04-29 09:15
  [38] TROUGH price= 8260.00 time= 04-29 11:00
  [39] PEAK   price= 8380.00 time= 04-29 21:15
  [40] TROUGH price= 8245.00 time= 04-29 22:00
  [41] PEAK   price= 8340.00 time= 04-30 11:00
  [42] TROUGH price= 8250.00 time= 04-30 14:00 ← A
  [43] PEAK   price= 8610.00 time= 05-07 13:45
  [44] TROUGH price= 8350.00 time= 05-11 10:00 ← C
  [45] PEAK   price= 8420.00 time= 05-11 13:45
  [46] TROUGH price= 8325.00 time= 05-12 10:00
  [47] PEAK   price= 8450.00 time= 05-12 21:15
  [48] TROUGH price= 8315.00 time= 05-13 10:00
  [49] PEAK   price= 8495.00 time= 05-14 21:45
```

**失败详情:**
```
  ❌ C4 最新(7920.00) > C(8350.00) = False
```
---

### L — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8295.00 @ 08-23 13:45 |
| B 价 | 8085.00 @ 08-27 09:15 |
| C 价 | 8250.00 @ 08-30 09:15 |
| 最新价 | 8545.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 13 (merge 后: 13) |
| A 索引 | 9 | C 索引 | 11 |

**极值点序列** (swing: 13, merged: 13):
```
  [ 0] TROUGH price= 8025.00 time= 07-07 13:45
  [ 1] PEAK   price= 8435.00 time= 07-12 09:15
  [ 2] TROUGH price= 8130.00 time= 07-15 09:15
  [ 3] PEAK   price= 8500.00 time= 07-22 09:15
  [ 4] TROUGH price= 8055.00 time= 07-27 13:45
  [ 5] PEAK   price= 8355.00 time= 07-30 09:15
  [ 6] TROUGH price= 7980.00 time= 08-03 13:45
  [ 7] PEAK   price= 8435.00 time= 08-17 13:45
  [ 8] TROUGH price= 8110.00 time= 08-20 13:45
  [ 9] PEAK   price= 8295.00 time= 08-23 13:45 ← A
  [10] TROUGH price= 8085.00 time= 08-27 09:15
  [11] PEAK   price= 8250.00 time= 08-30 09:15 ← C
  [12] TROUGH price= 8005.00 time= 08-31 13:45
```

**失败详情:**
```
  ❌ C4 最新(8545.00) < C(8250.00) = False
```
---

### L — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8500.00 @ 07-19 09:15 |
| B 价 | 7980.00 @ 08-02 09:15 |
| C 价 | 8435.00 @ 08-16 09:15 |
| 最新价 | 8545.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 4 (merge 后: 4) |
| A 索引 | 0 | C 索引 | 2 |

**极值点序列** (swing: 4, merged: 4):
```
  [ 0] PEAK   price= 8500.00 time= 07-19 09:15 ← A
  [ 1] TROUGH price= 7980.00 time= 08-02 09:15
  [ 2] PEAK   price= 8435.00 time= 08-16 09:15 ← C
  [ 3] TROUGH price= 8005.00 time= 08-30 09:15
```

**失败详情:**
```
  ❌ C4 最新(8545.00) < C(8435.00) = False
```
---

### L — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 8712.00 time= 03-14 09:15
  [ 1] PEAK   price= 9368.00 time= 03-28 09:15
  [ 2] TROUGH price= 8531.00 time= 05-09 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### L — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 7979.00 @ 08-08 13:45 |
| B 价 | 7755.00 @ 08-10 13:45 |
| C 价 | 7919.00 @ 08-30 09:15 |
| 最新价 | 8400.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 12 (merge 后: 12) |
| A 索引 | 6 | C 索引 | 10 |

**极值点序列** (swing: 12, merged: 12):
```
  [ 0] PEAK   price= 8396.00 time= 07-08 13:45
  [ 1] TROUGH price= 7543.00 time= 07-15 13:45
  [ 2] PEAK   price= 8022.00 time= 07-18 13:45
  [ 3] TROUGH price= 7582.00 time= 07-21 13:45
  [ 4] PEAK   price= 8184.00 time= 07-29 13:45
  [ 5] TROUGH price= 7727.00 time= 08-05 13:45
  [ 6] PEAK   price= 7979.00 time= 08-08 13:45 ← A
  [ 7] TROUGH price= 7755.00 time= 08-10 13:45
  [ 8] PEAK   price= 7986.00 time= 08-15 09:15
  [ 9] TROUGH price= 7599.00 time= 08-17 13:45
  [10] PEAK   price= 7919.00 time= 08-30 09:15 ← C
  [11] TROUGH price= 7766.00 time= 08-31 13:45
```

**失败详情:**
```
  ❌ C4 最新(8400.00) < C(7919.00) = False
```
---

### L — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8278.00 @ 12-12 13:45 |
| B 价 | 8088.00 @ 12-13 13:45 |
| C 价 | 8261.00 @ 12-15 13:45 |
| 最新价 | 8278.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 16 (merge 后: 16) |
| A 索引 | 10 | C 索引 | 12 |

**极值点序列** (swing: 16, merged: 16):
```
  [ 0] PEAK   price= 7950.00 time= 11-04 13:45
  [ 1] TROUGH price= 7687.00 time= 11-08 13:45
  [ 2] PEAK   price= 7840.00 time= 11-09 10:45
  [ 3] TROUGH price= 7641.00 time= 11-10 13:45
  [ 4] PEAK   price= 7994.00 time= 11-18 13:45
  [ 5] TROUGH price= 7751.00 time= 11-21 13:45
  [ 6] PEAK   price= 8061.00 time= 11-25 13:45
  [ 7] TROUGH price= 7855.00 time= 11-28 13:45
  [ 8] PEAK   price= 8230.00 time= 12-05 09:15
  [ 9] TROUGH price= 7953.00 time= 12-07 13:45
  [10] PEAK   price= 8278.00 time= 12-12 13:45 ← A
  [11] TROUGH price= 8088.00 time= 12-13 13:45
  [12] PEAK   price= 8261.00 time= 12-15 13:45 ← C
  [13] TROUGH price= 7977.00 time= 12-23 13:45
  [14] PEAK   price= 8709.00 time= 01-03 09:15
  [15] TROUGH price= 7959.00 time= 01-11 09:30
```

**失败详情:**
```
  ❌ C4 最新(8278.00) < C(8261.00) = False
```
---

### L — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 7932.00 time= 03-20 09:15
  [ 1] PEAK   price= 8335.00 time= 04-24 09:15
  [ 2] TROUGH price= 7900.00 time= 05-08 09:30
```

**失败详情:**
```
算法无有效3点结构
```
---

### L — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8369.00 @ 09-04 21:15 |
| B 价 | 8460.00 @ 09-04 23:00 |
| C 价 | 8400.00 @ 09-05 14:15 |
| 最新价 | 8337.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 44 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 8146.00 time= 07-26 21:15
  [ 1] PEAK   price= 8206.00 time= 07-27 13:45
  [ 2] TROUGH price= 8156.00 time= 07-27 15:00
  [ 3] PEAK   price= 8247.00 time= 07-28 21:15
  [ 4] TROUGH price= 8153.00 time= 07-31 10:00
  [ 5] PEAK   price= 8240.00 time= 07-31 21:15
  [ 6] TROUGH price= 8172.00 time= 08-01 10:00
  [ 7] PEAK   price= 8303.00 time= 08-02 11:00
  [ 8] TROUGH price= 8125.00 time= 08-03 14:00
  [ 9] PEAK   price= 8226.00 time= 08-04 09:15
  [10] TROUGH price= 8179.00 time= 08-04 11:00
  [11] PEAK   price= 8223.00 time= 08-04 14:00
  [12] TROUGH price= 8092.00 time= 08-08 10:00
  [13] PEAK   price= 8143.00 time= 08-08 11:00
  [14] TROUGH price= 8074.00 time= 08-08 21:15
  [15] PEAK   price= 8226.00 time= 08-09 21:15
  [16] TROUGH price= 8173.00 time= 08-10 10:00
  [17] PEAK   price= 8205.00 time= 08-10 14:00
  [18] TROUGH price= 8134.00 time= 08-10 21:15
  [19] PEAK   price= 8176.00 time= 08-11 10:45
  [20] TROUGH price= 8138.00 time= 08-11 11:00
  [21] PEAK   price= 8181.00 time= 08-11 21:15
  [22] TROUGH price= 8071.00 time= 08-14 14:00
  [23] PEAK   price= 8132.00 time= 08-15 09:15
  [24] TROUGH price= 8075.00 time= 08-15 11:00
  [25] PEAK   price= 8143.00 time= 08-15 14:00
  [26] TROUGH price= 8070.00 time= 08-16 09:15
  [27] PEAK   price= 8102.00 time= 08-16 10:45
  [28] TROUGH price= 8058.00 time= 08-17 09:15
  [29] PEAK   price= 8411.00 time= 08-21 14:00
  [30] TROUGH price= 8355.00 time= 08-21 22:00
  [31] PEAK   price= 8468.00 time= 08-23 14:00
  [32] TROUGH price= 8359.00 time= 08-23 21:15
  [33] PEAK   price= 8429.00 time= 08-24 14:00
  [34] TROUGH price= 8338.00 time= 08-24 21:15
  [35] PEAK   price= 8428.00 time= 08-25 21:15
  [36] TROUGH price= 8225.00 time= 08-29 10:45
  [37] PEAK   price= 8269.00 time= 08-29 13:45
  [38] TROUGH price= 8232.00 time= 08-29 21:15
  [39] PEAK   price= 8315.00 time= 08-30 21:15
  [40] TROUGH price= 8290.00 time= 08-31 14:00
  [41] PEAK   price= 8435.00 time= 09-01 10:00
  [42] TROUGH price= 8384.00 time= 09-01 21:15
  [43] PEAK   price= 8448.00 time= 09-01 22:00
  [44] TROUGH price= 8369.00 time= 09-04 21:15 ← A
  [45] PEAK   price= 8460.00 time= 09-04 23:00
  [46] TROUGH price= 8400.00 time= 09-05 14:15 ← C
  [47] PEAK   price= 8460.00 time= 09-06 10:45
  [48] TROUGH price= 8280.00 time= 09-08 11:30
  [49] PEAK   price= 8500.00 time= 09-08 21:15
```

**失败详情:**
```
  ❌ C4 最新(8337.00) > C(8400.00) = False
```
---

### L — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 7820.00 time= 12-04 09:15
  [ 1] PEAK   price= 8317.00 time= 12-25 09:15
  [ 2] TROUGH price= 7761.00 time= 01-02 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### L — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8346.00 @ 05-06 14:15 |
| B 价 | 8479.00 @ 05-08 09:15 |
| C 价 | 8350.00 @ 05-09 13:45 |
| 最新价 | 8350.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 12 (merge 后: 12) |
| A 索引 | 9 | C 索引 | 11 |

**极值点序列** (swing: 12, merged: 12):
```
  [ 0] PEAK   price= 8300.00 time= 03-01 13:45
  [ 1] TROUGH price= 8132.00 time= 03-06 09:15
  [ 2] PEAK   price= 8226.00 time= 03-08 13:45
  [ 3] TROUGH price= 8107.00 time= 03-13 13:45
  [ 4] PEAK   price= 8376.00 time= 03-20 10:45
  [ 5] TROUGH price= 8173.00 time= 03-27 13:45
  [ 6] PEAK   price= 8541.00 time= 04-19 10:45
  [ 7] TROUGH price= 8321.00 time= 04-24 13:45
  [ 8] PEAK   price= 8500.00 time= 04-30 10:45
  [ 9] TROUGH price= 8346.00 time= 05-06 14:15 ← A
  [10] PEAK   price= 8479.00 time= 05-08 09:15
  [11] TROUGH price= 8350.00 time= 05-09 13:45 ← C
```

**失败详情:**
```
  ❌ C4 最新(8350.00) > C(8350.00) = False
```
---

### L — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8137.00 @ 09-03 10:15 |
| B 价 | 8175.00 @ 09-03 15:00 |
| C 价 | 8170.00 @ 09-05 13:45 |
| 最新价 | 7660.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 28 | C 索引 | 36 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 8121.00 time= 08-21 11:00
  [ 1] PEAK   price= 8199.00 time= 08-21 23:00
  [ 2] TROUGH price= 8158.00 time= 08-22 09:15
  [ 3] PEAK   price= 8183.00 time= 08-22 11:30
  [ 4] TROUGH price= 8136.00 time= 08-22 15:00
  [ 5] PEAK   price= 8162.00 time= 08-22 21:45
  [ 6] TROUGH price= 8137.00 time= 08-22 22:30
  [ 7] PEAK   price= 8161.00 time= 08-23 09:15
  [ 8] TROUGH price= 8095.00 time= 08-23 14:30
  [ 9] PEAK   price= 8150.00 time= 08-26 09:15
  [10] TROUGH price= 8100.00 time= 08-26 09:45
  [11] PEAK   price= 8191.00 time= 08-26 21:15
  [12] TROUGH price= 8164.00 time= 08-27 09:15
  [13] PEAK   price= 8190.00 time= 08-27 11:00
  [14] TROUGH price= 8168.00 time= 08-27 11:30
  [15] PEAK   price= 8192.00 time= 08-27 14:00
  [16] TROUGH price= 8167.00 time= 08-27 23:00
  [17] PEAK   price= 8195.00 time= 08-28 10:15
  [18] TROUGH price= 8174.00 time= 08-28 11:15
  [19] PEAK   price= 8190.00 time= 08-28 14:15
  [20] TROUGH price= 8151.00 time= 08-28 21:30
  [21] PEAK   price= 8207.00 time= 08-29 14:15
  [22] TROUGH price= 8183.00 time= 08-29 15:00
  [23] PEAK   price= 8204.00 time= 08-30 09:15
  [24] TROUGH price= 8185.00 time= 08-30 10:15
  [25] PEAK   price= 8201.00 time= 08-30 13:45
  [26] TROUGH price= 8102.00 time= 09-02 15:00
  [27] PEAK   price= 8150.00 time= 09-03 09:45
  [28] TROUGH price= 8137.00 time= 09-03 10:15 ← A
  [29] PEAK   price= 8175.00 time= 09-03 15:00
  [30] TROUGH price= 8107.00 time= 09-03 21:30
  [31] PEAK   price= 8175.00 time= 09-04 09:30
  [32] TROUGH price= 8050.00 time= 09-04 10:45
  [33] PEAK   price= 8192.00 time= 09-04 11:00
  [34] TROUGH price= 8080.00 time= 09-04 23:00
  [35] PEAK   price= 8186.00 time= 09-05 10:45
  [36] TROUGH price= 8170.00 time= 09-05 13:45 ← C
  [37] PEAK   price= 8189.00 time= 09-05 14:45
  [38] TROUGH price= 8168.00 time= 09-05 22:15
  [39] PEAK   price= 8198.00 time= 09-09 10:45
```

**失败详情:**
```
  ❌ C4 最新(7660.00) > C(8170.00) = False
```
---

### L — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8050.00 @ 09-04 10:45 |
| B 价 | 8192.00 @ 09-04 11:00 |
| C 价 | 8080.00 @ 09-04 23:00 |
| 最新价 | 7660.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 49) |
| A 索引 | 45 | C 索引 | 47 |

**极值点序列** (swing: 50, merged: 49):
```
  [ 0] PEAK   price= 8319.00 time= 07-26 10:00
  [ 1] TROUGH price= 8215.00 time= 07-29 11:00
  [ 2] PEAK   price= 8256.00 time= 07-29 14:00
  [ 3] TROUGH price= 8156.00 time= 07-30 22:00
  [ 4] PEAK   price= 8327.00 time= 08-01 09:15
  [ 5] TROUGH price= 8260.00 time= 08-01 14:00
  [ 6] PEAK   price= 8295.00 time= 08-01 21:15
  [ 7] TROUGH price= 8248.00 time= 08-02 09:15
  [ 8] PEAK   price= 8305.00 time= 08-02 15:00
  [ 9] TROUGH price= 8206.00 time= 08-05 09:15
  [10] PEAK   price= 8285.00 time= 08-05 11:00
  [11] TROUGH price= 8203.00 time= 08-05 21:15
  [12] PEAK   price= 8255.00 time= 08-06 09:15
  [13] TROUGH price= 8197.00 time= 08-07 09:15
  [14] PEAK   price= 8238.00 time= 08-07 10:45
  [15] TROUGH price= 8154.00 time= 08-07 22:00
  [16] PEAK   price= 8206.00 time= 08-08 11:00
  [17] TROUGH price= 8139.00 time= 08-09 09:15
  [18] PEAK   price= 8220.00 time= 08-09 11:00
  [19] TROUGH price= 8106.00 time= 08-12 10:00
  [20] PEAK   price= 8240.00 time= 08-13 09:15
  [21] TROUGH price= 8153.00 time= 08-14 09:15
  [22] PEAK   price= 8215.00 time= 08-14 10:00
  [23] TROUGH price= 8119.00 time= 08-15 10:00
  [24] PEAK   price= 8220.00 time= 08-15 23:00
  [25] TROUGH price= 8136.00 time= 08-16 21:15
  [26] PEAK   price= 8186.00 time= 08-19 09:15
  [27] TROUGH price= 8150.00 time= 08-19 10:45
  [28] PEAK   price= 8185.00 time= 08-19 14:00
  [29] TROUGH price= 8086.00 time= 08-20 13:45
  [30] PEAK   price= 8180.00 time= 08-20 22:00
  [31] TROUGH price= 8121.00 time= 08-21 11:00
  [32] PEAK   price= 8199.00 time= 08-21 23:00
  [33] TROUGH price= 8095.00 time= 08-23 14:00
  [34] PEAK   price= 8191.00 time= 08-26 21:15
  [35] TROUGH price= 8164.00 time= 08-27 09:15
  [36] PEAK   price= 8192.00 time= 08-27 14:00
  [37] TROUGH price= 8167.00 time= 08-27 23:00
  [38] PEAK   price= 8195.00 time= 08-28 10:00
  [39] TROUGH price= 8151.00 time= 08-28 21:15
  [40] PEAK   price= 8207.00 time= 08-29 14:00
  [41] TROUGH price= 8180.00 time= 08-30 09:15
  [42] PEAK   price= 8201.00 time= 08-30 13:45
  [43] TROUGH price= 8102.00 time= 09-02 15:00
  [44] PEAK   price= 8175.00 time= 09-03 15:00
  [45] TROUGH price= 8050.00 time= 09-04 10:45 ← A
  [46] PEAK   price= 8192.00 time= 09-04 11:00
  [47] TROUGH price= 8080.00 time= 09-04 23:00 ← C
  [48] PEAK   price= 8198.00 time= 09-09 10:45
```

**失败详情:**
```
  ❌ C4 最新(7660.00) > C(8080.00) = False
```
---

### L — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 8537.00 time= 12-02 09:15
  [ 1] TROUGH price= 8289.00 time= 12-09 09:15
  [ 2] PEAK   price= 8580.00 time= 12-30 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### L — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 7322.00 @ 04-29 11:15 |
| B 价 | 7474.00 @ 05-14 10:00 |
| C 价 | 7453.00 @ 05-14 10:45 |
| 最新价 | 7330.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 22 | C 索引 | 38 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 7327.00 time= 04-21 09:30
  [ 1] PEAK   price= 7362.00 time= 04-21 15:00
  [ 2] TROUGH price= 7317.00 time= 04-21 22:00
  [ 3] PEAK   price= 7358.00 time= 04-22 09:30
  [ 4] TROUGH price= 7321.00 time= 04-22 11:15
  [ 5] PEAK   price= 7341.00 time= 04-22 14:15
  [ 6] TROUGH price= 7306.00 time= 04-22 21:15
  [ 7] PEAK   price= 7374.00 time= 04-23 09:15
  [ 8] TROUGH price= 7345.00 time= 04-23 10:45
  [ 9] PEAK   price= 7394.00 time= 04-23 14:30
  [10] TROUGH price= 7361.00 time= 04-23 22:30
  [11] PEAK   price= 7377.00 time= 04-24 09:30
  [12] TROUGH price= 7351.00 time= 04-24 11:00
  [13] PEAK   price= 7379.00 time= 04-24 11:30
  [14] TROUGH price= 7316.00 time= 04-24 14:15
  [15] PEAK   price= 7385.00 time= 04-25 09:15
  [16] TROUGH price= 7331.00 time= 04-25 21:15
  [17] PEAK   price= 7383.00 time= 04-28 09:30
  [18] TROUGH price= 7357.00 time= 04-28 10:15
  [19] PEAK   price= 7374.00 time= 04-28 14:00
  [20] TROUGH price= 7330.00 time= 04-28 21:30
  [21] PEAK   price= 7349.00 time= 04-29 09:30
  [22] TROUGH price= 7322.00 time= 04-29 11:15 ← A
  [23] PEAK   price= 7350.00 time= 04-29 14:15
  [24] TROUGH price= 7320.00 time= 04-29 15:00
  [25] PEAK   price= 7345.00 time= 04-29 21:15
  [26] TROUGH price= 7310.00 time= 04-30 10:45
  [27] PEAK   price= 7429.00 time= 05-06 09:15
  [28] TROUGH price= 7230.00 time= 05-06 14:45
  [29] PEAK   price= 7270.00 time= 05-06 21:30
  [30] TROUGH price= 7240.00 time= 05-06 22:30
  [31] PEAK   price= 7305.00 time= 05-07 09:30
  [32] TROUGH price= 7250.00 time= 05-07 10:45
  [33] PEAK   price= 7275.00 time= 05-07 13:45
  [34] TROUGH price= 7250.00 time= 05-07 14:15
  [35] PEAK   price= 7300.00 time= 05-07 21:15
  [36] TROUGH price= 7177.00 time= 05-09 22:45
  [37] PEAK   price= 7474.00 time= 05-14 10:00
  [38] TROUGH price= 7453.00 time= 05-14 10:45 ← C
  [39] PEAK   price= 7520.00 time= 05-16 09:15
```

**失败详情:**
```
  ❌ C4 最新(7330.00) > C(7453.00) = False
```
---

### L — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 7348.00 @ 04-18 09:15 |
| B 价 | 7291.00 @ 04-18 13:45 |
| C 价 | 7305.00 @ 05-07 09:15 |
| 最新价 | 7330.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 29 | C 索引 | 47 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 7652.00 time= 03-21 15:00
  [ 1] PEAK   price= 7743.00 time= 03-24 14:00
  [ 2] TROUGH price= 7685.00 time= 03-25 21:15
  [ 3] PEAK   price= 7727.00 time= 03-26 09:15
  [ 4] TROUGH price= 7646.00 time= 03-26 13:45
  [ 5] PEAK   price= 7719.00 time= 03-27 09:15
  [ 6] TROUGH price= 7689.00 time= 03-27 13:45
  [ 7] PEAK   price= 7735.00 time= 03-28 09:15
  [ 8] TROUGH price= 7615.00 time= 03-31 10:45
  [ 9] PEAK   price= 7722.00 time= 04-01 10:00
  [10] TROUGH price= 7662.00 time= 04-01 22:00
  [11] PEAK   price= 7746.00 time= 04-02 13:45
  [12] TROUGH price= 7378.00 time= 04-07 09:15
  [13] PEAK   price= 7465.00 time= 04-07 11:00
  [14] TROUGH price= 7319.00 time= 04-07 15:00
  [15] PEAK   price= 7437.00 time= 04-07 22:00
  [16] TROUGH price= 7107.00 time= 04-09 09:15
  [17] PEAK   price= 7275.00 time= 04-09 14:00
  [18] TROUGH price= 7140.00 time= 04-09 21:15
  [19] PEAK   price= 7404.00 time= 04-10 09:15
  [20] TROUGH price= 7271.00 time= 04-10 21:15
  [21] PEAK   price= 7365.00 time= 04-11 15:00
  [22] TROUGH price= 7320.00 time= 04-11 22:00
  [23] PEAK   price= 7391.00 time= 04-14 21:15
  [24] TROUGH price= 7321.00 time= 04-15 09:15
  [25] PEAK   price= 7370.00 time= 04-15 10:45
  [26] TROUGH price= 7266.00 time= 04-16 15:00
  [27] PEAK   price= 7347.00 time= 04-17 11:00
  [28] TROUGH price= 7302.00 time= 04-17 15:00
  [29] PEAK   price= 7348.00 time= 04-18 09:15 ← A
  [30] TROUGH price= 7291.00 time= 04-18 13:45
  [31] PEAK   price= 7376.00 time= 04-18 23:00
  [32] TROUGH price= 7317.00 time= 04-21 22:00
  [33] PEAK   price= 7358.00 time= 04-22 09:15
  [34] TROUGH price= 7306.00 time= 04-22 21:15
  [35] PEAK   price= 7394.00 time= 04-23 14:00
  [36] TROUGH price= 7361.00 time= 04-23 22:00
  [37] PEAK   price= 7379.00 time= 04-24 11:00
  [38] TROUGH price= 7316.00 time= 04-24 14:00
  [39] PEAK   price= 7385.00 time= 04-25 09:15
  [40] TROUGH price= 7331.00 time= 04-25 21:15
  [41] PEAK   price= 7383.00 time= 04-28 09:15
  [42] TROUGH price= 7330.00 time= 04-28 21:15
  [43] PEAK   price= 7350.00 time= 04-29 14:00
  [44] TROUGH price= 7320.00 time= 04-29 15:00
  [45] PEAK   price= 7429.00 time= 05-06 09:15
  [46] TROUGH price= 7230.00 time= 05-06 14:00
  [47] PEAK   price= 7305.00 time= 05-07 09:15 ← C
  [48] TROUGH price= 7177.00 time= 05-09 22:00
  [49] PEAK   price= 7520.00 time= 05-16 09:15
```

**失败详情:**
```
  ❌ C4 最新(7330.00) < C(7305.00) = False
```
---

### L — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 7027.00 @ 09-08 22:15 |
| B 价 | 7176.00 @ 09-10 14:30 |
| C 价 | 7122.00 @ 09-11 10:45 |
| 最新价 | 7050.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 7351.00 time= 08-21 22:30
  [ 1] TROUGH price= 7311.00 time= 08-22 14:15
  [ 2] PEAK   price= 7361.00 time= 08-22 23:00
  [ 3] TROUGH price= 7339.00 time= 08-25 10:00
  [ 4] PEAK   price= 7395.00 time= 08-26 09:30
  [ 5] TROUGH price= 7336.00 time= 08-26 21:15
  [ 6] PEAK   price= 7360.00 time= 08-26 22:30
  [ 7] TROUGH price= 7336.00 time= 08-27 10:45
  [ 8] PEAK   price= 7349.00 time= 08-27 11:30
  [ 9] TROUGH price= 7284.00 time= 08-27 21:45
  [10] PEAK   price= 7304.00 time= 08-27 22:45
  [11] TROUGH price= 7290.00 time= 08-28 09:15
  [12] PEAK   price= 7319.00 time= 08-28 11:00
  [13] TROUGH price= 7300.00 time= 08-28 14:15
  [14] PEAK   price= 7320.00 time= 08-28 21:15
  [15] TROUGH price= 7293.00 time= 08-28 22:45
  [16] PEAK   price= 7309.00 time= 08-29 09:15
  [17] TROUGH price= 7230.00 time= 08-29 15:00
  [18] PEAK   price= 7276.00 time= 08-29 21:15
  [19] TROUGH price= 7173.00 time= 09-01 09:30
  [20] PEAK   price= 7222.00 time= 09-01 21:45
  [21] TROUGH price= 7199.00 time= 09-01 23:00
  [22] PEAK   price= 7220.00 time= 09-02 09:30
  [23] TROUGH price= 7190.00 time= 09-02 10:45
  [24] PEAK   price= 7215.00 time= 09-02 14:00
  [25] TROUGH price= 7200.00 time= 09-02 15:00
  [26] PEAK   price= 7222.00 time= 09-02 22:15
  [27] TROUGH price= 7207.00 time= 09-02 22:45
  [28] PEAK   price= 7230.00 time= 09-03 09:15
  [29] TROUGH price= 7160.00 time= 09-03 22:45
  [30] PEAK   price= 7180.00 time= 09-04 11:00
  [31] TROUGH price= 7155.00 time= 09-05 11:30
  [32] PEAK   price= 7199.00 time= 09-05 14:15
  [33] TROUGH price= 7138.00 time= 09-05 21:15
  [34] PEAK   price= 7217.00 time= 09-08 21:15
  [35] TROUGH price= 7027.00 time= 09-08 22:15 ← A
  [36] PEAK   price= 7176.00 time= 09-10 14:30
  [37] TROUGH price= 7122.00 time= 09-11 10:45 ← C
  [38] PEAK   price= 7145.00 time= 09-11 14:45
  [39] TROUGH price= 7050.00 time= 09-12 13:45
```

**失败详情:**
```
  ❌ C4 最新(7050.00) > C(7122.00) = False
```
---

### L — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 6838.00 @ 12-02 13:45 |
| B 价 | 6172.00 @ 12-23 13:45 |
| C 价 | 6387.00 @ 12-24 13:45 |
| 最新价 | 6520.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 12 (merge 后: 12) |
| A 索引 | 7 | C 索引 | 9 |

**极值点序列** (swing: 12, merged: 12):
```
  [ 0] TROUGH price= 6756.00 time= 11-13 09:15
  [ 1] PEAK   price= 6896.00 time= 11-14 09:15
  [ 2] TROUGH price= 6771.00 time= 11-18 13:45
  [ 3] PEAK   price= 6854.00 time= 11-20 13:45
  [ 4] TROUGH price= 6731.00 time= 11-21 13:45
  [ 5] PEAK   price= 6825.00 time= 11-24 13:45
  [ 6] TROUGH price= 6697.00 time= 11-25 13:45
  [ 7] PEAK   price= 6838.00 time= 12-02 13:45 ← A
  [ 8] TROUGH price= 6172.00 time= 12-23 13:45
  [ 9] PEAK   price= 6387.00 time= 12-24 13:45 ← C
  [10] TROUGH price= 6264.00 time= 12-26 09:15
  [11] PEAK   price= 6676.00 time= 01-14 13:45
```

**失败详情:**
```
  ❌ C4 最新(6520.00) < C(6387.00) = False
```
---

### L — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8150.00 @ 04-23 14:00 |
| B 价 | 8216.00 @ 04-24 09:15 |
| C 价 | 8198.00 @ 05-11 21:45 |
| 最新价 | 8091.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 29 | C 索引 | 45 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 9208.00 time= 03-30 09:15
  [ 1] TROUGH price= 8512.00 time= 03-31 11:00
  [ 2] PEAK   price= 8698.00 time= 03-31 23:00
  [ 3] TROUGH price= 8491.00 time= 04-01 09:15
  [ 4] PEAK   price= 8694.00 time= 04-01 11:00
  [ 5] TROUGH price= 8373.00 time= 04-01 14:00
  [ 6] PEAK   price= 8876.00 time= 04-02 21:15
  [ 7] TROUGH price= 8393.00 time= 04-02 22:00
  [ 8] PEAK   price= 9407.00 time= 04-07 13:45
  [ 9] TROUGH price= 8362.00 time= 04-08 21:15
  [10] PEAK   price= 8669.00 time= 04-09 09:15
  [11] TROUGH price= 8213.00 time= 04-10 22:00
  [12] PEAK   price= 8649.00 time= 04-13 09:15
  [13] TROUGH price= 8222.00 time= 04-14 09:15
  [14] PEAK   price= 8343.00 time= 04-14 11:00
  [15] TROUGH price= 8252.00 time= 04-14 14:00
  [16] PEAK   price= 8390.00 time= 04-14 21:15
  [17] TROUGH price= 8228.00 time= 04-15 09:15
  [18] PEAK   price= 8382.00 time= 04-15 10:45
  [19] TROUGH price= 8214.00 time= 04-16 09:15
  [20] PEAK   price= 8384.00 time= 04-16 22:00
  [21] TROUGH price= 8044.00 time= 04-17 21:15
  [22] PEAK   price= 8274.00 time= 04-20 09:15
  [23] TROUGH price= 8048.00 time= 04-20 21:15
  [24] PEAK   price= 8179.00 time= 04-21 11:00
  [25] TROUGH price= 8113.00 time= 04-22 09:15
  [26] PEAK   price= 8233.00 time= 04-22 11:00
  [27] TROUGH price= 8146.00 time= 04-23 09:15
  [28] PEAK   price= 8220.00 time= 04-23 11:00
  [29] TROUGH price= 8150.00 time= 04-23 14:00 ← A
  [30] PEAK   price= 8216.00 time= 04-24 09:15
  [31] TROUGH price= 8111.00 time= 04-24 22:00
  [32] PEAK   price= 8312.00 time= 04-27 21:15
  [33] TROUGH price= 8240.00 time= 04-27 22:00
  [34] PEAK   price= 8485.00 time= 04-28 21:15
  [35] TROUGH price= 8340.00 time= 04-29 11:00
  [36] PEAK   price= 8545.00 time= 04-30 09:15
  [37] TROUGH price= 8430.00 time= 04-30 10:00
  [38] PEAK   price= 8543.00 time= 04-30 14:00
  [39] TROUGH price= 8476.00 time= 05-06 09:15
  [40] PEAK   price= 8542.00 time= 05-06 10:45
  [41] TROUGH price= 8150.00 time= 05-07 11:00
  [42] PEAK   price= 8190.00 time= 05-07 14:00
  [43] TROUGH price= 8050.00 time= 05-07 22:00
  [44] PEAK   price= 8265.00 time= 05-11 13:45
  [45] TROUGH price= 8198.00 time= 05-11 21:45 ← C
  [46] PEAK   price= 8342.00 time= 05-13 10:00
  [47] TROUGH price= 8161.00 time= 05-15 10:00
  [48] PEAK   price= 8688.00 time= 05-18 09:15
  [49] TROUGH price= 8090.00 time= 05-18 21:15
```

**失败详情:**
```
  ❌ C4 最新(8091.00) > C(8198.00) = False
```
---

### L — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8044.00 @ 04-17 13:45 |
| B 价 | 8233.00 @ 04-22 10:45 |
| C 价 | 8111.00 @ 04-24 13:45 |
| 最新价 | 8091.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 16 (merge 后: 16) |
| A 索引 | 10 | C 索引 | 12 |

**极值点序列** (swing: 16, merged: 16):
```
  [ 0] TROUGH price= 7448.00 time= 03-10 10:45
  [ 1] PEAK   price= 8893.00 time= 03-16 10:45
  [ 2] TROUGH price= 8358.00 time= 03-18 13:45
  [ 3] PEAK   price= 9523.00 time= 03-23 13:45
  [ 4] TROUGH price= 8340.00 time= 03-25 09:15
  [ 5] PEAK   price= 9208.00 time= 03-30 09:15
  [ 6] TROUGH price= 8373.00 time= 04-01 13:45
  [ 7] PEAK   price= 9407.00 time= 04-07 13:45
  [ 8] TROUGH price= 8213.00 time= 04-10 13:45
  [ 9] PEAK   price= 8649.00 time= 04-13 09:15
  [10] TROUGH price= 8044.00 time= 04-17 13:45 ← A
  [11] PEAK   price= 8233.00 time= 04-22 10:45
  [12] TROUGH price= 8111.00 time= 04-24 13:45 ← C
  [13] PEAK   price= 8545.00 time= 04-30 09:15
  [14] TROUGH price= 8050.00 time= 05-07 13:45
  [15] PEAK   price= 8688.00 time= 05-18 09:15
```

**失败详情:**
```
  ❌ C4 最新(8091.00) > C(8111.00) = False
```
---

### LC — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 169800.00 @ 06-16 14:00 |
| B 价 | 171400.00 @ 06-16 14:30 |
| C 价 | 170160.00 @ 06-17 14:15 |
| 最新价 | 160500.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 27) |
| A 索引 | 18 | C 索引 | 24 |

**极值点序列** (swing: 40, merged: 27):
```
  [ 0] TROUGH price=162680.00 time= 06-09 11:15
  [ 1] PEAK   price=169200.00 time= 06-10 09:00
  [ 2] TROUGH price=165000.00 time= 06-10 13:30
  [ 3] PEAK   price=169260.00 time= 06-10 14:15
  [ 4] TROUGH price=166500.00 time= 06-11 09:00
  [ 5] PEAK   price=170900.00 time= 06-11 09:30
  [ 6] TROUGH price=168400.00 time= 06-11 10:30
  [ 7] PEAK   price=174500.00 time= 06-11 13:30
  [ 8] TROUGH price=171700.00 time= 06-11 14:00
  [ 9] PEAK   price=178000.00 time= 06-12 10:00
  [10] TROUGH price=176760.00 time= 06-12 13:45
  [11] PEAK   price=178740.00 time= 06-12 14:00
  [12] TROUGH price=174700.00 time= 06-12 14:45
  [13] PEAK   price=177900.00 time= 06-15 09:30
  [14] TROUGH price=172340.00 time= 06-15 10:45
  [15] PEAK   price=175780.00 time= 06-15 14:00
  [16] TROUGH price=168520.00 time= 06-16 09:45
  [17] PEAK   price=171800.00 time= 06-16 11:15
  [18] TROUGH price=169800.00 time= 06-16 14:00 ← A
  [19] PEAK   price=171400.00 time= 06-16 14:30
  [20] TROUGH price=169000.00 time= 06-17 09:15
  [21] PEAK   price=173560.00 time= 06-17 09:30
  [22] TROUGH price=171520.00 time= 06-17 11:00
  [23] PEAK   price=173140.00 time= 06-17 11:30
  [24] TROUGH price=170160.00 time= 06-17 14:15 ← C
  [25] PEAK   price=172500.00 time= 06-18 09:15
  [26] TROUGH price=163240.00 time= 06-18 11:30
```

**失败详情:**
```
  ❌ C4 最新(160500.00) > C(170160.00) = False
```
---

### LC — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 157180.00 @ 06-05 00:00 |
| B 价 | 178740.00 @ 06-12 13:30 |
| C 价 | 168460.00 @ 06-16 10:45 |
| 最新价 | 163420.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 32 (merge 后: 23) |
| A 索引 | 20 | C 索引 | 22 |

**极值点序列** (swing: 32, merged: 23):
```
  [ 0] TROUGH price=142560.00 time= 02-13 09:15
  [ 1] PEAK   price=186600.00 time= 02-26 09:15
  [ 2] TROUGH price=146080.00 time= 03-04 09:15
  [ 3] PEAK   price=161520.00 time= 03-05 09:15
  [ 4] TROUGH price=142600.00 time= 03-09 09:15
  [ 5] PEAK   price=167400.00 time= 03-11 09:15
  [ 6] TROUGH price=140000.00 time= 03-19 00:00
  [ 7] PEAK   price=175000.00 time= 03-30 00:00
  [ 8] TROUGH price=154560.00 time= 04-01 00:00
  [ 9] PEAK   price=165500.00 time= 04-07 00:00
  [10] TROUGH price=152500.00 time= 04-09 00:00
  [11] PEAK   price=181420.00 time= 04-20 13:45
  [12] TROUGH price=169620.00 time= 04-21 13:45
  [13] PEAK   price=184780.00 time= 04-27 09:15
  [14] TROUGH price=173500.00 time= 04-28 09:15
  [15] PEAK   price=209880.00 time= 05-13 00:00
  [16] TROUGH price=175200.00 time= 05-20 00:00
  [17] PEAK   price=187900.00 time= 05-25 00:00
  [18] TROUGH price=172380.00 time= 05-27 13:45
  [19] PEAK   price=182240.00 time= 05-29 09:15
  [20] TROUGH price=157180.00 time= 06-05 00:00 ← A
  [21] PEAK   price=178740.00 time= 06-12 13:30
  [22] TROUGH price=168460.00 time= 06-16 10:45 ← C
```

**失败详情:**
```
  ❌ C4 最新(163420.00) > C(168460.00) = False
```
---

### LH — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 11800.00 @ 02-03 00:00 |
| B 价 | 9000.00 @ 04-07 00:00 |
| C 价 | 11585.00 @ 04-21 00:00 |
| 最新价 | 11950.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 55 (merge 后: 55) |
| A 索引 | 50 | C 索引 | 52 |

**极值点序列** (swing: 55, merged: 55):
```
  [ 0] PEAK   price=29805.00 time= 02-23 00:00
  [ 1] TROUGH price=26310.00 time= 03-30 00:00
  [ 2] PEAK   price=27990.00 time= 04-20 00:00
  [ 3] TROUGH price=13365.00 time= 09-22 00:00
  [ 4] PEAK   price=17670.00 time= 10-26 00:00
  [ 5] TROUGH price=13205.00 time= 01-25 00:00
  [ 6] PEAK   price=14965.00 time= 02-08 00:00
  [ 7] TROUGH price=12360.00 time= 04-06 00:00
  [ 8] PEAK   price=19915.00 time= 05-17 00:00
  [ 9] TROUGH price=18450.00 time= 05-24 00:00
  [10] PEAK   price=23290.00 time= 07-12 00:00
  [11] TROUGH price=19965.00 time= 07-26 00:00
  [12] PEAK   price=23970.00 time= 08-23 00:00
  [13] TROUGH price=21635.00 time= 09-20 00:00
  [14] PEAK   price=24300.00 time= 10-11 00:00
  [15] TROUGH price=14035.00 time= 01-31 00:00
  [16] PEAK   price=17840.00 time= 02-21 00:00
  [17] TROUGH price=14675.00 time= 04-04 00:00
  [18] PEAK   price=17250.00 time= 04-18 00:00
  [19] TROUGH price=15080.00 time= 05-30 00:00
  [20] PEAK   price=16660.00 time= 06-13 00:00
  [21] TROUGH price=14840.00 time= 07-11 00:00
  [22] PEAK   price=17765.00 time= 08-08 00:00
  [23] TROUGH price=16400.00 time= 09-05 00:00
  [24] PEAK   price=17295.00 time= 09-12 00:00
  [25] TROUGH price=13240.00 time= 12-05 00:00
  [26] PEAK   price=14975.00 time= 12-12 00:00
  [27] TROUGH price=13375.00 time= 01-09 00:00
  [28] PEAK   price=14275.00 time= 01-23 00:00
  [29] TROUGH price=13365.00 time= 02-19 00:00
  [30] PEAK   price=18650.00 time= 04-09 00:00
  [31] TROUGH price=17235.00 time= 04-30 00:00
  [32] PEAK   price=18700.00 time= 05-28 00:00
  [33] TROUGH price=17185.00 time= 06-25 00:00
  [34] PEAK   price=19365.00 time= 07-30 00:00
  [35] TROUGH price=14950.00 time= 10-15 00:00
  [36] PEAK   price=15745.00 time= 11-12 00:00
  [37] TROUGH price=12505.00 time= 12-17 00:00
  [38] PEAK   price=13195.00 time= 12-31 00:00
  [39] TROUGH price=12600.00 time= 01-07 00:00
  [40] PEAK   price=13305.00 time= 02-05 00:00
  [41] TROUGH price=12840.00 time= 02-18 00:00
  [42] PEAK   price=13785.00 time= 03-18 00:00
  [43] TROUGH price=13170.00 time= 04-01 00:00
  [44] PEAK   price=14645.00 time= 04-08 00:00
  [45] TROUGH price=13350.00 time= 06-03 00:00
  [46] PEAK   price=15150.00 time= 07-22 00:00
  [47] TROUGH price=11080.00 time= 12-02 00:00
  [48] PEAK   price=12160.00 time= 01-13 00:00
  [49] TROUGH price=11155.00 time= 01-27 00:00
  [50] PEAK   price=11800.00 time= 02-03 00:00 ← A
  [51] TROUGH price= 9000.00 time= 04-07 00:00
  [52] PEAK   price=11585.00 time= 04-21 00:00 ← C
  [53] TROUGH price=10625.00 time= 05-26 00:00
  [54] PEAK   price=12220.00 time= 06-02 00:00
```

**失败详情:**
```
  ❌ C4 最新(11950.00) < C(11585.00) = False
```
---

### LH — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 10080.00 @ 06-11 13:30 |
| B 价 | 10235.00 @ 06-15 09:15 |
| C 价 | 10100.00 @ 06-16 09:15 |
| 最新价 | 9900.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 38) |
| A 索引 | 33 | C 索引 | 35 |

**极值点序列** (swing: 50, merged: 38):
```
  [ 0] PEAK   price=11455.00 time= 04-24 13:45
  [ 1] TROUGH price=11090.00 time= 04-28 10:00
  [ 2] PEAK   price=11455.00 time= 04-29 09:15
  [ 3] TROUGH price=11185.00 time= 04-30 09:15
  [ 4] PEAK   price=11425.00 time= 05-06 09:15
  [ 5] TROUGH price=11335.00 time= 05-07 09:15
  [ 6] PEAK   price=11460.00 time= 05-07 10:00
  [ 7] TROUGH price=11115.00 time= 05-11 09:15
  [ 8] PEAK   price=11315.00 time= 05-11 10:45
  [ 9] TROUGH price=10740.00 time= 05-13 10:00
  [10] PEAK   price=10935.00 time= 05-14 09:15
  [11] TROUGH price=10710.00 time= 05-14 11:00
  [12] PEAK   price=10870.00 time= 05-15 09:15
  [13] TROUGH price=10680.00 time= 05-18 09:15
  [14] PEAK   price=10945.00 time= 05-19 14:00
  [15] TROUGH price=10725.00 time= 05-20 10:00
  [16] PEAK   price=11200.00 time= 05-22 15:00
  [17] TROUGH price=10715.00 time= 05-27 09:15
  [18] PEAK   price=10795.00 time= 05-27 10:45
  [19] TROUGH price=10630.00 time= 05-27 15:00
  [20] PEAK   price=10755.00 time= 05-28 10:00
  [21] TROUGH price=10680.00 time= 05-28 13:45
  [22] PEAK   price=10780.00 time= 05-29 09:15
  [23] TROUGH price=10675.00 time= 05-29 11:00
  [24] PEAK   price=10760.00 time= 06-01 09:15
  [25] TROUGH price=10435.00 time= 06-03 09:15
  [26] PEAK   price=10695.00 time= 06-03 11:00
  [27] TROUGH price=10090.00 time= 06-08 09:15
  [28] PEAK   price=10260.00 time= 06-09 13:30
  [29] TROUGH price=10165.00 time= 06-09 14:15
  [30] PEAK   price=10320.00 time= 06-10 10:00
  [31] TROUGH price=10115.00 time= 06-11 10:00
  [32] PEAK   price=10165.00 time= 06-11 11:15
  [33] TROUGH price=10080.00 time= 06-11 13:30 ← A
  [34] PEAK   price=10235.00 time= 06-15 09:15
  [35] TROUGH price=10100.00 time= 06-16 09:15 ← C
  [36] PEAK   price=10195.00 time= 06-16 14:00
  [37] TROUGH price= 9865.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(9900.00) > C(10100.00) = False
```
---

### LH — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 10080.00 @ 06-11 13:30 |
| B 价 | 12190.00 @ 06-15 00:00 |
| C 价 | 10100.00 @ 06-16 09:15 |
| 最新价 | 9960.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 37 (merge 后: 27) |
| A 索引 | 24 | C 索引 | 26 |

**极值点序列** (swing: 37, merged: 27):
```
  [ 0] TROUGH price=12085.00 time= 02-09 09:15
  [ 1] PEAK   price=12285.00 time= 02-12 10:45
  [ 2] TROUGH price=12040.00 time= 02-24 09:15
  [ 3] PEAK   price=12530.00 time= 02-27 13:45
  [ 4] TROUGH price=12285.00 time= 03-02 09:15
  [ 5] PEAK   price=12430.00 time= 03-04 09:15
  [ 6] TROUGH price=12090.00 time= 03-06 09:15
  [ 7] PEAK   price=12390.00 time= 03-09 09:15
  [ 8] TROUGH price=10880.00 time= 03-24 00:00
  [ 9] PEAK   price=11385.00 time= 03-26 00:00
  [10] TROUGH price=10075.00 time= 04-07 00:00
  [11] PEAK   price=10590.00 time= 04-10 00:00
  [12] TROUGH price=10150.00 time= 04-13 00:00
  [13] PEAK   price=11540.00 time= 04-20 13:45
  [14] TROUGH price=11085.00 time= 04-22 09:15
  [15] PEAK   price=11585.00 time= 04-23 00:00
  [16] TROUGH price=11085.00 time= 04-28 00:00
  [17] PEAK   price=11465.00 time= 05-07 00:00
  [18] TROUGH price=10665.00 time= 05-18 00:00
  [19] PEAK   price=11200.00 time= 05-22 00:00
  [20] TROUGH price=10630.00 time= 05-27 13:45
  [21] PEAK   price=12220.00 time= 06-03 00:00
  [22] TROUGH price=10090.00 time= 06-08 09:15
  [23] PEAK   price=12095.00 time= 06-10 00:00
  [24] TROUGH price=10080.00 time= 06-11 13:30 ← A
  [25] PEAK   price=12190.00 time= 06-15 00:00
  [26] TROUGH price=10100.00 time= 06-16 09:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(9960.00) > C(10100.00) = False
```
---

### M — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2933.00 @ 04-20 00:00 |
| B 价 | 3073.00 @ 05-13 00:00 |
| C 价 | 2960.00 @ 05-26 00:00 |
| 最新价 | 2918.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 60 (merge 后: 60) |
| A 索引 | 56 | C 索引 | 58 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] TROUGH price= 3821.00 time= 12-01 00:00
  [ 1] PEAK   price= 3981.00 time= 12-08 00:00
  [ 2] TROUGH price= 3311.00 time= 12-22 00:00
  [ 3] PEAK   price= 3384.00 time= 12-28 00:00
  [ 4] TROUGH price= 2988.00 time= 01-18 00:00
  [ 5] PEAK   price= 3085.00 time= 01-25 00:00
  [ 6] TROUGH price= 2928.00 time= 01-30 00:00
  [ 7] PEAK   price= 3415.00 time= 03-21 00:00
  [ 8] TROUGH price= 3199.00 time= 03-28 00:00
  [ 9] PEAK   price= 3659.00 time= 05-24 00:00
  [10] TROUGH price= 3432.00 time= 06-04 00:00
  [11] PEAK   price= 3532.00 time= 06-07 00:00
  [12] TROUGH price= 3321.00 time= 06-24 00:00
  [13] PEAK   price= 3421.00 time= 07-03 00:00
  [14] TROUGH price= 3071.00 time= 07-16 00:00
  [15] PEAK   price= 3197.00 time= 07-23 00:00
  [16] TROUGH price= 2862.00 time= 08-13 00:00
  [17] PEAK   price= 3145.00 time= 09-09 00:00
  [18] TROUGH price= 3008.00 time= 09-11 00:00
  [19] PEAK   price= 3177.00 time= 09-30 00:00
  [20] TROUGH price= 2930.00 time= 10-28 00:00
  [21] PEAK   price= 3026.00 time= 10-30 00:00
  [22] TROUGH price= 2952.00 time= 11-05 00:00
  [23] PEAK   price= 3116.00 time= 11-08 00:00
  [24] TROUGH price= 2549.00 time= 12-19 00:00
  [25] PEAK   price= 2731.00 time= 01-02 00:00
  [26] TROUGH price= 2613.00 time= 01-09 00:00
  [27] PEAK   price= 2953.00 time= 02-10 00:00
  [28] TROUGH price= 2820.00 time= 02-13 00:00
  [29] PEAK   price= 2985.00 time= 02-21 00:00
  [30] TROUGH price= 2864.00 time= 02-26 00:00
  [31] PEAK   price= 3025.00 time= 03-04 00:00
  [32] TROUGH price= 2822.00 time= 03-12 00:00
  [33] PEAK   price= 2935.00 time= 03-20 00:00
  [34] TROUGH price= 2806.00 time= 03-27 00:00
  [35] PEAK   price= 3168.00 time= 04-08 00:00
  [36] TROUGH price= 3004.00 time= 04-18 00:00
  [37] PEAK   price= 3075.00 time= 04-24 00:00
  [38] TROUGH price= 2861.00 time= 05-20 00:00
  [39] PEAK   price= 3087.00 time= 06-17 00:00
  [40] TROUGH price= 2921.00 time= 06-26 00:00
  [41] PEAK   price= 3121.00 time= 07-23 00:00
  [42] TROUGH price= 2963.00 time= 07-29 00:00
  [43] PEAK   price= 3190.00 time= 08-13 00:00
  [44] TROUGH price= 3027.00 time= 08-28 00:00
  [45] PEAK   price= 3097.00 time= 09-12 00:00
  [46] TROUGH price= 2852.00 time= 10-22 00:00
  [47] PEAK   price= 3107.00 time= 11-17 00:00
  [48] TROUGH price= 2719.00 time= 12-25 00:00
  [49] PEAK   price= 2827.00 time= 01-08 00:00
  [50] TROUGH price= 2710.00 time= 01-19 00:00
  [51] PEAK   price= 2809.00 time= 01-29 00:00
  [52] TROUGH price= 2715.00 time= 02-05 00:00
  [53] PEAK   price= 3204.00 time= 03-13 00:00
  [54] TROUGH price= 2870.00 time= 04-01 00:00
  [55] PEAK   price= 3001.00 time= 04-10 00:00
  [56] TROUGH price= 2933.00 time= 04-20 00:00 ← A
  [57] PEAK   price= 3073.00 time= 05-13 00:00
  [58] TROUGH price= 2960.00 time= 05-26 00:00 ← C
  [59] PEAK   price= 3010.00 time= 05-29 00:00
```

**失败详情:**
```
  ❌ C4 最新(2918.00) > C(2960.00) = False
```
---

### MA — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2917.00 @ 06-09 13:45 |
| B 价 | 3074.00 @ 06-11 13:30 |
| C 价 | 2971.00 @ 06-12 09:00 |
| 最新价 | 2567.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 33 (merge 后: 20) |
| A 索引 | 17 | C 索引 | 19 |

**极值点序列** (swing: 33, merged: 20):
```
  [ 0] PEAK   price= 3119.00 time= 03-23 00:00
  [ 1] TROUGH price= 2762.00 time= 03-25 00:00
  [ 2] PEAK   price= 3160.00 time= 03-30 00:00
  [ 3] TROUGH price= 2762.00 time= 04-01 00:00
  [ 4] PEAK   price= 3235.00 time= 04-08 00:00
  [ 5] TROUGH price= 2740.00 time= 04-13 00:00
  [ 6] PEAK   price= 2972.00 time= 04-13 09:15
  [ 7] TROUGH price= 2798.00 time= 04-17 13:45
  [ 8] PEAK   price= 3063.00 time= 05-06 00:00
  [ 9] TROUGH price= 2827.00 time= 05-07 09:15
  [10] PEAK   price= 2931.00 time= 05-11 13:45
  [11] TROUGH price= 2849.00 time= 05-14 13:45
  [12] PEAK   price= 2997.00 time= 05-19 09:15
  [13] TROUGH price= 2760.00 time= 05-27 13:45
  [14] PEAK   price= 2951.00 time= 06-01 13:45
  [15] TROUGH price= 2855.00 time= 06-05 00:00
  [16] PEAK   price= 3049.00 time= 06-08 00:00
  [17] TROUGH price= 2917.00 time= 06-09 13:45 ← A
  [18] PEAK   price= 3074.00 time= 06-11 13:30
  [19] TROUGH price= 2971.00 time= 06-12 09:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(2567.00) > C(2971.00) = False
```
---

### NI — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 132350.00 @ 03-09 00:00 |
| B 价 | 155360.00 @ 05-06 00:00 |
| C 价 | 140500.00 @ 05-18 00:00 |
| 最新价 | 135100.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 60 (merge 后: 60) |
| A 索引 | 53 | C 索引 | 59 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] PEAK   price=148270.00 time= 04-22 00:00
  [ 1] TROUGH price=140160.00 time= 05-09 00:00
  [ 2] PEAK   price=160500.00 time= 05-21 00:00
  [ 3] TROUGH price=132470.00 time= 06-26 00:00
  [ 4] PEAK   price=139380.00 time= 07-04 00:00
  [ 5] TROUGH price=124030.00 time= 07-25 00:00
  [ 6] PEAK   price=133960.00 time= 08-01 00:00
  [ 7] TROUGH price=126360.00 time= 08-14 00:00
  [ 8] PEAK   price=132960.00 time= 08-28 00:00
  [ 9] TROUGH price=119300.00 time= 09-11 00:00
  [10] PEAK   price=138800.00 time= 10-08 00:00
  [11] TROUGH price=122270.00 time= 11-01 00:00
  [12] PEAK   price=130470.00 time= 11-08 00:00
  [13] TROUGH price=122110.00 time= 11-18 00:00
  [14] PEAK   price=128990.00 time= 11-26 00:00
  [15] TROUGH price=124060.00 time= 12-03 00:00
  [16] PEAK   price=129980.00 time= 12-13 00:00
  [17] TROUGH price=121800.00 time= 12-20 00:00
  [18] PEAK   price=126930.00 time= 12-27 00:00
  [19] TROUGH price=120400.00 time= 01-06 00:00
  [20] PEAK   price=129460.00 time= 01-20 00:00
  [21] TROUGH price=122610.00 time= 02-05 00:00
  [22] PEAK   price=127950.00 time= 02-10 00:00
  [23] TROUGH price=123000.00 time= 02-14 00:00
  [24] PEAK   price=135960.00 time= 03-14 00:00
  [25] TROUGH price=128130.00 time= 03-20 00:00
  [26] PEAK   price=132270.00 time= 03-31 00:00
  [27] TROUGH price=115450.00 time= 04-07 00:00
  [28] PEAK   price=126850.00 time= 04-24 00:00
  [29] TROUGH price=118630.00 time= 05-29 00:00
  [30] PEAK   price=123180.00 time= 06-09 00:00
  [31] TROUGH price=116670.00 time= 06-23 00:00
  [32] PEAK   price=123100.00 time= 07-04 00:00
  [33] TROUGH price=118800.00 time= 07-09 00:00
  [34] PEAK   price=125370.00 time= 07-28 00:00
  [35] TROUGH price=119180.00 time= 08-04 00:00
  [36] PEAK   price=123110.00 time= 08-13 00:00
  [37] TROUGH price=119230.00 time= 08-22 00:00
  [38] PEAK   price=123810.00 time= 09-02 00:00
  [39] TROUGH price=119880.00 time= 09-12 00:00
  [40] PEAK   price=123550.00 time= 09-16 00:00
  [41] TROUGH price=120670.00 time= 09-23 00:00
  [42] PEAK   price=124880.00 time= 10-10 00:00
  [43] TROUGH price=120520.00 time= 10-20 00:00
  [44] PEAK   price=122650.00 time= 10-27 00:00
  [45] TROUGH price=113980.00 time= 11-21 00:00
  [46] PEAK   price=118700.00 time= 12-01 00:00
  [47] TROUGH price=111700.00 time= 12-17 00:00
  [48] PEAK   price=151750.00 time= 01-15 00:00
  [49] TROUGH price=138000.00 time= 01-19 00:00
  [50] PEAK   price=152500.00 time= 01-26 00:00
  [51] TROUGH price=129650.00 time= 02-02 00:00
  [52] PEAK   price=142870.00 time= 02-25 00:00
  [53] TROUGH price=132350.00 time= 03-09 00:00 ← A
  [54] PEAK   price=140340.00 time= 03-13 00:00
  [55] TROUGH price=128800.00 time= 03-20 00:00
  [56] PEAK   price=138860.00 time= 03-26 00:00
  [57] TROUGH price=131840.00 time= 04-08 00:00
  [58] PEAK   price=155360.00 time= 05-06 00:00
  [59] TROUGH price=140500.00 time= 05-18 00:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(135100.00) > C(140500.00) = False
```
---

### NI — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 128800.00 @ 03-17 00:00 |
| B 价 | 155360.00 @ 05-06 00:00 |
| C 价 | 140500.00 @ 05-12 00:00 |
| 最新价 | 135100.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 80 (merge 后: 80) |
| A 索引 | 77 | C 索引 | 79 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] PEAK   price=102830.00 time= 05-21 00:00
  [ 1] TROUGH price=94280.00 time= 06-04 00:00
  [ 2] PEAK   price=149190.00 time= 09-03 00:00
  [ 3] TROUGH price=103360.00 time= 12-03 00:00
  [ 4] PEAK   price=114200.00 time= 12-24 00:00
  [ 5] TROUGH price=100670.00 time= 02-03 00:00
  [ 6] PEAK   price=107050.00 time= 02-11 00:00
  [ 7] TROUGH price=89550.00 time= 03-31 00:00
  [ 8] PEAK   price=123930.00 time= 09-01 00:00
  [ 9] TROUGH price=110620.00 time= 09-22 00:00
  [10] PEAK   price=125670.00 time= 10-27 00:00
  [11] TROUGH price=114020.00 time= 11-03 00:00
  [12] PEAK   price=137280.00 time= 01-19 00:00
  [13] TROUGH price=128840.00 time= 02-02 00:00
  [14] PEAK   price=149350.00 time= 02-18 00:00
  [15] TROUGH price=118000.00 time= 03-16 00:00
  [16] PEAK   price=127750.00 time= 04-06 00:00
  [17] TROUGH price=118750.00 time= 04-20 00:00
  [18] PEAK   price=135570.00 time= 05-06 00:00
  [19] TROUGH price=122570.00 time= 05-18 00:00
  [20] PEAK   price=148780.00 time= 07-27 00:00
  [21] TROUGH price=138020.00 time= 08-10 00:00
  [22] PEAK   price=155140.00 time= 09-07 00:00
  [23] TROUGH price=135700.00 time= 09-28 00:00
  [24] PEAK   price=161600.00 time= 10-19 00:00
  [25] TROUGH price=139630.00 time= 11-02 00:00
  [26] PEAK   price=156480.00 time= 11-23 00:00
  [27] TROUGH price=139930.00 time= 12-14 00:00
  [28] PEAK   price=281250.00 time= 03-22 00:00
  [29] TROUGH price=205500.00 time= 04-12 00:00
  [30] PEAK   price=246000.00 time= 04-19 00:00
  [31] TROUGH price=194360.00 time= 05-10 00:00
  [32] PEAK   price=226500.00 time= 06-07 00:00
  [33] TROUGH price=142500.00 time= 07-12 00:00
  [34] PEAK   price=183990.00 time= 07-26 00:00
  [35] TROUGH price=159000.00 time= 08-30 00:00
  [36] PEAK   price=202800.00 time= 09-20 00:00
  [37] TROUGH price=176000.00 time= 10-11 00:00
  [38] PEAK   price=234870.00 time= 01-03 00:00
  [39] TROUGH price=200130.00 time= 01-10 00:00
  [40] PEAK   price=226700.00 time= 01-31 00:00
  [41] TROUGH price=171350.00 time= 03-14 00:00
  [42] PEAK   price=198880.00 time= 04-18 00:00
  [43] TROUGH price=153050.00 time= 05-30 00:00
  [44] PEAK   price=174340.00 time= 06-13 00:00
  [45] TROUGH price=153700.00 time= 06-27 00:00
  [46] PEAK   price=174220.00 time= 07-25 00:00
  [47] TROUGH price=161230.00 time= 08-15 00:00
  [48] PEAK   price=173980.00 time= 09-05 00:00
  [49] TROUGH price=121880.00 time= 11-21 00:00
  [50] PEAK   price=132350.00 time= 01-23 00:00
  [51] TROUGH price=122000.00 time= 01-30 00:00
  [52] PEAK   price=143100.00 time= 03-12 00:00
  [53] TROUGH price=128600.00 time= 03-26 00:00
  [54] PEAK   price=160500.00 time= 05-21 00:00
  [55] TROUGH price=124030.00 time= 07-23 00:00
  [56] PEAK   price=132960.00 time= 08-27 00:00
  [57] TROUGH price=119300.00 time= 09-10 00:00
  [58] PEAK   price=138800.00 time= 10-08 00:00
  [59] TROUGH price=122110.00 time= 11-12 00:00
  [60] PEAK   price=129980.00 time= 12-10 00:00
  [61] TROUGH price=120400.00 time= 12-31 00:00
  [62] PEAK   price=129460.00 time= 01-14 00:00
  [63] TROUGH price=122610.00 time= 02-05 00:00
  [64] PEAK   price=135960.00 time= 03-11 00:00
  [65] TROUGH price=115450.00 time= 04-01 00:00
  [66] PEAK   price=126850.00 time= 04-22 00:00
  [67] TROUGH price=116670.00 time= 06-17 00:00
  [68] PEAK   price=125370.00 time= 07-22 00:00
  [69] TROUGH price=119230.00 time= 08-19 00:00
  [70] PEAK   price=123810.00 time= 09-02 00:00
  [71] TROUGH price=119880.00 time= 09-09 00:00
  [72] PEAK   price=124880.00 time= 10-09 00:00
  [73] TROUGH price=111700.00 time= 12-16 00:00
  [74] PEAK   price=152500.00 time= 01-20 00:00
  [75] TROUGH price=129650.00 time= 01-27 00:00
  [76] PEAK   price=142870.00 time= 02-24 00:00
  [77] TROUGH price=128800.00 time= 03-17 00:00 ← A
  [78] PEAK   price=155360.00 time= 05-06 00:00
  [79] TROUGH price=140500.00 time= 05-12 00:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(135100.00) > C(140500.00) = False
```
---

### OI — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9775.00 @ 06-17 13:45 |
| B 价 | 9827.00 @ 06-17 21:15 |
| C 价 | 9780.00 @ 06-17 21:45 |
| 最新价 | 9685.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 26) |
| A 索引 | 21 | C 索引 | 23 |

**极值点序列** (swing: 40, merged: 26):
```
  [ 0] PEAK   price= 9966.00 time= 06-11 10:00
  [ 1] TROUGH price= 9909.00 time= 06-11 10:45
  [ 2] PEAK   price= 9980.00 time= 06-11 14:00
  [ 3] TROUGH price= 9922.00 time= 06-11 21:00
  [ 4] PEAK   price= 9960.00 time= 06-11 22:30
  [ 5] TROUGH price= 9820.00 time= 06-12 09:30
  [ 6] PEAK   price= 9908.00 time= 06-12 11:15
  [ 7] TROUGH price= 9849.00 time= 06-12 13:45
  [ 8] PEAK   price= 9887.00 time= 06-12 14:45
  [ 9] TROUGH price= 9836.00 time= 06-12 21:15
  [10] PEAK   price= 9899.00 time= 06-12 21:45
  [11] TROUGH price= 9784.00 time= 06-15 09:30
  [12] PEAK   price= 9874.00 time= 06-15 13:45
  [13] TROUGH price= 9750.00 time= 06-15 21:30
  [14] PEAK   price= 9813.00 time= 06-16 09:15
  [15] TROUGH price= 9759.00 time= 06-16 09:30
  [16] PEAK   price= 9830.00 time= 06-16 11:15
  [17] TROUGH price= 9796.00 time= 06-16 14:00
  [18] PEAK   price= 9895.00 time= 06-16 22:15
  [19] TROUGH price= 9758.00 time= 06-17 09:30
  [20] PEAK   price= 9819.00 time= 06-17 11:15
  [21] TROUGH price= 9775.00 time= 06-17 13:45 ← A
  [22] PEAK   price= 9827.00 time= 06-17 21:15
  [23] TROUGH price= 9780.00 time= 06-17 21:45 ← C
  [24] PEAK   price= 9835.00 time= 06-17 23:00
  [25] TROUGH price= 9667.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(9685.00) > C(9780.00) = False
```
---

### OI — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9750.00 @ 06-15 21:15 |
| B 价 | 9895.00 @ 06-16 22:00 |
| C 价 | 9758.00 @ 06-17 09:15 |
| 最新价 | 9685.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 36) |
| A 索引 | 31 | C 索引 | 33 |

**极值点序列** (swing: 50, merged: 36):
```
  [ 0] PEAK   price= 9675.00 time= 05-26 10:00
  [ 1] TROUGH price= 9617.00 time= 05-26 11:00
  [ 2] PEAK   price= 9728.00 time= 05-27 11:00
  [ 3] TROUGH price= 9651.00 time= 05-27 14:00
  [ 4] PEAK   price= 9898.00 time= 05-28 15:00
  [ 5] TROUGH price= 9834.00 time= 05-29 09:15
  [ 6] PEAK   price= 9924.00 time= 05-29 10:00
  [ 7] TROUGH price= 9868.00 time= 05-29 14:00
  [ 8] PEAK   price= 9975.00 time= 06-01 09:15
  [ 9] TROUGH price= 9909.00 time= 06-01 21:15
  [10] PEAK   price=10007.00 time= 06-02 11:00
  [11] TROUGH price= 9943.00 time= 06-02 21:15
  [12] PEAK   price=10415.00 time= 06-03 22:00
  [13] TROUGH price=10248.00 time= 06-04 11:00
  [14] PEAK   price=10351.00 time= 06-04 21:15
  [15] TROUGH price= 9973.00 time= 06-05 14:00
  [16] PEAK   price=10147.00 time= 06-05 22:00
  [17] TROUGH price= 9870.00 time= 06-09 13:45
  [18] PEAK   price= 9943.00 time= 06-09 22:00
  [19] TROUGH price= 9871.00 time= 06-10 10:30
  [20] PEAK   price= 9927.00 time= 06-10 11:00
  [21] TROUGH price= 9859.00 time= 06-10 13:30
  [22] PEAK   price= 9995.00 time= 06-11 09:00
  [23] TROUGH price= 9909.00 time= 06-11 10:30
  [24] PEAK   price= 9980.00 time= 06-11 14:00
  [25] TROUGH price= 9820.00 time= 06-12 09:00
  [26] PEAK   price= 9908.00 time= 06-12 11:00
  [27] TROUGH price= 9839.00 time= 06-12 11:15
  [28] PEAK   price= 9908.00 time= 06-12 14:15
  [29] TROUGH price= 9784.00 time= 06-15 09:15
  [30] PEAK   price= 9874.00 time= 06-15 13:45
  [31] TROUGH price= 9750.00 time= 06-15 21:15 ← A
  [32] PEAK   price= 9895.00 time= 06-16 22:00
  [33] TROUGH price= 9758.00 time= 06-17 09:15 ← C
  [34] PEAK   price= 9835.00 time= 06-17 23:00
  [35] TROUGH price= 9667.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(9685.00) > C(9758.00) = False
```
---

### P — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4526.00 @ 04-30 13:45 |
| B 价 | 4370.00 @ 05-07 09:15 |
| C 价 | 4424.00 @ 05-13 14:00 |
| 最新价 | 4746.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 31 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 4958.00 time= 04-10 09:15
  [ 1] PEAK   price= 5020.00 time= 04-10 10:15
  [ 2] TROUGH price= 4896.00 time= 04-10 15:00
  [ 3] PEAK   price= 4972.00 time= 04-13 09:15
  [ 4] TROUGH price= 4820.00 time= 04-14 09:15
  [ 5] PEAK   price= 4896.00 time= 04-14 10:45
  [ 6] TROUGH price= 4828.00 time= 04-15 09:15
  [ 7] PEAK   price= 4894.00 time= 04-15 09:45
  [ 8] TROUGH price= 4858.00 time= 04-15 11:15
  [ 9] PEAK   price= 4890.00 time= 04-15 13:45
  [10] TROUGH price= 4860.00 time= 04-15 14:15
  [11] PEAK   price= 4940.00 time= 04-16 11:00
  [12] TROUGH price= 4772.00 time= 04-17 09:15
  [13] PEAK   price= 4952.00 time= 04-20 09:15
  [14] TROUGH price= 4884.00 time= 04-20 11:15
  [15] PEAK   price= 4932.00 time= 04-20 14:30
  [16] TROUGH price= 4700.00 time= 04-21 11:00
  [17] PEAK   price= 4754.00 time= 04-21 14:15
  [18] TROUGH price= 4634.00 time= 04-22 09:15
  [19] PEAK   price= 4762.00 time= 04-22 11:15
  [20] TROUGH price= 4590.00 time= 04-22 14:45
  [21] PEAK   price= 4702.00 time= 04-23 09:30
  [22] TROUGH price= 4638.00 time= 04-23 11:00
  [23] PEAK   price= 4800.00 time= 04-24 09:15
  [24] TROUGH price= 4514.00 time= 04-27 13:45
  [25] PEAK   price= 4608.00 time= 04-28 09:15
  [26] TROUGH price= 4530.00 time= 04-28 09:30
  [27] PEAK   price= 4592.00 time= 04-29 10:00
  [28] TROUGH price= 4484.00 time= 04-30 09:15
  [29] PEAK   price= 4566.00 time= 04-30 10:00
  [30] TROUGH price= 4506.00 time= 04-30 11:00
  [31] PEAK   price= 4526.00 time= 04-30 13:45 ← A
  [32] TROUGH price= 4474.00 time= 04-30 14:15
  [33] PEAK   price= 4530.00 time= 04-30 15:00
  [34] TROUGH price= 4370.00 time= 05-07 09:15
  [35] PEAK   price= 4530.00 time= 05-11 09:15
  [36] TROUGH price= 4390.00 time= 05-12 15:00
  [37] PEAK   price= 4424.00 time= 05-13 14:00 ← C
  [38] TROUGH price= 4390.00 time= 05-14 11:00
  [39] PEAK   price= 4648.00 time= 05-18 09:15
```

**失败详情:**
```
  ❌ C4 最新(4746.00) < C(4424.00) = False
```
---

### P — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4800.00 @ 04-24 09:15 |
| B 价 | 4370.00 @ 05-07 09:15 |
| C 价 | 4530.00 @ 05-11 09:15 |
| 最新价 | 4746.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 24 (merge 后: 24) |
| A 索引 | 20 | C 索引 | 22 |

**极值点序列** (swing: 24, merged: 24):
```
  [ 0] PEAK   price= 5910.00 time= 02-07 13:45
  [ 1] TROUGH price= 5476.00 time= 02-14 09:15
  [ 2] PEAK   price= 5622.00 time= 02-18 09:15
  [ 3] TROUGH price= 5386.00 time= 02-20 09:15
  [ 4] PEAK   price= 5552.00 time= 02-21 09:15
  [ 5] TROUGH price= 4946.00 time= 03-03 13:45
  [ 6] PEAK   price= 5254.00 time= 03-05 13:45
  [ 7] TROUGH price= 4778.00 time= 03-10 09:15
  [ 8] PEAK   price= 5002.00 time= 03-10 13:45
  [ 9] TROUGH price= 4530.00 time= 03-13 09:15
  [10] PEAK   price= 4868.00 time= 03-18 10:45
  [11] TROUGH price= 4540.00 time= 03-23 09:15
  [12] PEAK   price= 4918.00 time= 03-25 13:45
  [13] TROUGH price= 4718.00 time= 03-26 13:45
  [14] PEAK   price= 5042.00 time= 03-31 09:15
  [15] TROUGH price= 4782.00 time= 04-03 13:45
  [16] PEAK   price= 5122.00 time= 04-09 10:45
  [17] TROUGH price= 4772.00 time= 04-17 09:15
  [18] PEAK   price= 4952.00 time= 04-20 09:15
  [19] TROUGH price= 4590.00 time= 04-22 13:45
  [20] PEAK   price= 4800.00 time= 04-24 09:15 ← A
  [21] TROUGH price= 4370.00 time= 05-07 09:15
  [22] PEAK   price= 4530.00 time= 05-11 09:15 ← C
  [23] TROUGH price= 4390.00 time= 05-12 13:45
```

**失败详情:**
```
  ❌ C4 最新(4746.00) < C(4530.00) = False
```
---

### P — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 4530.00 time= 03-09 09:15
  [ 1] PEAK   price= 5122.00 time= 04-07 09:15
  [ 2] TROUGH price= 4370.00 time= 05-06 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### P — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 6014.00 @ 08-19 13:45 |
| B 价 | 5790.00 @ 08-21 13:45 |
| C 价 | 5946.00 @ 08-25 10:45 |
| 最新价 | 6500.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 10 | C 索引 | 12 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] PEAK   price= 5118.00 time= 07-07 09:15
  [ 1] TROUGH price= 4928.00 time= 07-13 09:15
  [ 2] PEAK   price= 5824.00 time= 07-24 09:15
  [ 3] TROUGH price= 5536.00 time= 07-30 13:45
  [ 4] PEAK   price= 6004.00 time= 08-04 13:45
  [ 5] TROUGH price= 5842.00 time= 08-05 13:45
  [ 6] PEAK   price= 6088.00 time= 08-06 13:45
  [ 7] TROUGH price= 5664.00 time= 08-11 13:45
  [ 8] PEAK   price= 5988.00 time= 08-17 09:15
  [ 9] TROUGH price= 5852.00 time= 08-18 13:45
  [10] PEAK   price= 6014.00 time= 08-19 13:45 ← A
  [11] TROUGH price= 5790.00 time= 08-21 13:45
  [12] PEAK   price= 5946.00 time= 08-25 10:45 ← C
  [13] TROUGH price= 5770.00 time= 08-25 13:45
  [14] PEAK   price= 6228.00 time= 08-31 13:45
```

**失败详情:**
```
  ❌ C4 最新(6500.00) < C(5946.00) = False
```
---

### P — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 7444.00 @ 12-25 13:45 |
| B 价 | 7162.00 @ 12-29 13:45 |
| C 价 | 7388.00 @ 12-30 09:15 |
| 最新价 | 7550.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 14 (merge 后: 14) |
| A 索引 | 10 | C 索引 | 12 |

**极值点序列** (swing: 14, merged: 14):
```
  [ 0] PEAK   price= 6616.00 time= 11-09 09:15
  [ 1] TROUGH price= 6378.00 time= 11-09 13:45
  [ 2] PEAK   price= 7028.00 time= 11-19 13:45
  [ 3] TROUGH price= 6554.00 time= 11-24 09:15
  [ 4] PEAK   price= 6876.00 time= 11-30 09:15
  [ 5] TROUGH price= 6394.00 time= 12-02 13:45
  [ 6] PEAK   price= 6848.00 time= 12-07 13:45
  [ 7] TROUGH price= 6612.00 time= 12-08 13:45
  [ 8] PEAK   price= 7140.00 time= 12-18 13:45
  [ 9] TROUGH price= 6854.00 time= 12-22 13:45
  [10] PEAK   price= 7444.00 time= 12-25 13:45 ← A
  [11] TROUGH price= 7162.00 time= 12-29 13:45
  [12] PEAK   price= 7388.00 time= 12-30 09:15 ← C
  [13] TROUGH price= 7000.00 time= 01-06 21:15
```

**失败详情:**
```
  ❌ C4 最新(7550.00) < C(7388.00) = False
```
---

### P — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 7028.00 time= 11-16 09:15
  [ 1] TROUGH price= 6394.00 time= 11-30 09:15
  [ 2] PEAK   price= 8046.00 time= 01-04 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### P — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 8302.00 time= 03-22 09:15
  [ 1] TROUGH price= 7200.00 time= 03-29 09:15
  [ 2] PEAK   price= 9928.00 time= 05-10 10:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### P — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 9078.00 @ 08-30 09:45 |
| B 价 | 8900.00 @ 08-30 11:30 |
| C 价 | 8944.00 @ 08-30 15:00 |
| 最新价 | 9000.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 33 | C 索引 | 35 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 8928.00 time= 08-16 10:15
  [ 1] PEAK   price= 9008.00 time= 08-16 11:30
  [ 2] TROUGH price= 8822.00 time= 08-16 21:15
  [ 3] PEAK   price= 9066.00 time= 08-17 13:45
  [ 4] TROUGH price= 8686.00 time= 08-18 11:30
  [ 5] PEAK   price= 8774.00 time= 08-18 14:15
  [ 6] TROUGH price= 8646.00 time= 08-18 21:15
  [ 7] PEAK   price= 8728.00 time= 08-18 22:30
  [ 8] TROUGH price= 8650.00 time= 08-19 09:15
  [ 9] PEAK   price= 8798.00 time= 08-19 11:00
  [10] TROUGH price= 8580.00 time= 08-19 22:45
  [11] PEAK   price= 8670.00 time= 08-20 09:30
  [12] TROUGH price= 8614.00 time= 08-20 11:00
  [13] PEAK   price= 8752.00 time= 08-20 14:15
  [14] TROUGH price= 8650.00 time= 08-20 15:00
  [15] PEAK   price= 8742.00 time= 08-20 21:30
  [16] TROUGH price= 8490.00 time= 08-23 09:45
  [17] PEAK   price= 8760.00 time= 08-23 14:15
  [18] TROUGH price= 8676.00 time= 08-23 14:45
  [19] PEAK   price= 8804.00 time= 08-23 21:15
  [20] TROUGH price= 8676.00 time= 08-24 09:15
  [21] PEAK   price= 8938.00 time= 08-24 22:45
  [22] TROUGH price= 8860.00 time= 08-25 09:15
  [23] PEAK   price= 8910.00 time= 08-25 10:00
  [24] TROUGH price= 8854.00 time= 08-25 10:45
  [25] PEAK   price= 9104.00 time= 08-25 21:30
  [26] TROUGH price= 8934.00 time= 08-26 10:45
  [27] PEAK   price= 9012.00 time= 08-26 14:00
  [28] TROUGH price= 8900.00 time= 08-26 21:45
  [29] PEAK   price= 8970.00 time= 08-26 22:15
  [30] TROUGH price= 8738.00 time= 08-27 09:15
  [31] PEAK   price= 8946.00 time= 08-27 14:15
  [32] TROUGH price= 8896.00 time= 08-27 21:15
  [33] PEAK   price= 9078.00 time= 08-30 09:45 ← A
  [34] TROUGH price= 8900.00 time= 08-30 11:30
  [35] PEAK   price= 8944.00 time= 08-30 15:00 ← C
  [36] TROUGH price= 8850.00 time= 08-30 21:15
  [37] PEAK   price= 9140.00 time= 08-31 14:15
  [38] TROUGH price= 8764.00 time= 09-02 09:30
  [39] PEAK   price= 9500.00 time= 09-07 11:00
```

**失败详情:**
```
  ❌ C4 最新(9000.00) < C(8944.00) = False
```
---

### P — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 9924.00 @ 01-05 23:00 |
| B 价 | 9760.00 @ 01-06 11:30 |
| C 价 | 9798.00 @ 01-06 13:45 |
| 最新价 | 10258.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 34 | C 索引 | 36 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 9298.00 time= 12-22 14:15
  [ 1] TROUGH price= 9240.00 time= 12-22 14:45
  [ 2] PEAK   price= 9358.00 time= 12-22 21:30
  [ 3] TROUGH price= 9304.00 time= 12-22 22:15
  [ 4] PEAK   price= 9400.00 time= 12-22 22:45
  [ 5] TROUGH price= 9268.00 time= 12-23 09:30
  [ 6] PEAK   price= 9310.00 time= 12-23 13:45
  [ 7] TROUGH price= 9230.00 time= 12-23 14:00
  [ 8] PEAK   price= 9278.00 time= 12-23 15:00
  [ 9] TROUGH price= 9182.00 time= 12-23 21:45
  [10] PEAK   price= 9320.00 time= 12-24 09:15
  [11] TROUGH price= 9276.00 time= 12-24 10:45
  [12] PEAK   price= 9402.00 time= 12-24 21:15
  [13] TROUGH price= 9270.00 time= 12-27 14:15
  [14] PEAK   price= 9338.00 time= 12-27 22:00
  [15] TROUGH price= 9292.00 time= 12-27 22:30
  [16] PEAK   price= 9398.00 time= 12-28 09:15
  [17] TROUGH price= 9280.00 time= 12-28 11:00
  [18] PEAK   price= 9452.00 time= 12-28 21:15
  [19] TROUGH price= 9320.00 time= 12-29 09:15
  [20] PEAK   price= 9362.00 time= 12-29 10:15
  [21] TROUGH price= 9276.00 time= 12-29 11:30
  [22] PEAK   price= 9328.00 time= 12-29 13:45
  [23] TROUGH price= 9284.00 time= 12-29 21:15
  [24] PEAK   price= 9360.00 time= 12-29 22:15
  [25] TROUGH price= 9332.00 time= 12-30 09:15
  [26] PEAK   price= 9428.00 time= 12-30 11:15
  [27] TROUGH price= 9356.00 time= 12-30 14:00
  [28] PEAK   price= 9450.00 time= 12-30 21:15
  [29] TROUGH price= 9418.00 time= 12-31 09:15
  [30] PEAK   price= 9554.00 time= 12-31 10:15
  [31] TROUGH price= 9480.00 time= 12-31 11:00
  [32] PEAK   price= 9938.00 time= 01-04 21:15
  [33] TROUGH price= 9822.00 time= 01-05 09:45
  [34] PEAK   price= 9924.00 time= 01-05 23:00 ← A
  [35] TROUGH price= 9760.00 time= 01-06 11:30
  [36] PEAK   price= 9798.00 time= 01-06 13:45 ← C
  [37] TROUGH price= 9748.00 time= 01-06 15:00
  [38] PEAK   price=10566.00 time= 01-06 21:15
  [39] TROUGH price= 9186.00 time= 01-10 21:15
```

**失败详情:**
```
  ❌ C4 最新(10258.00) < C(9798.00) = False
```
---

### P — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price=10018.00 time= 11-15 09:15
  [ 1] TROUGH price= 8690.00 time= 12-13 09:15
  [ 2] PEAK   price=10566.00 time= 01-04 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### P — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 7710.00 @ 11-21 10:45 |
| B 价 | 8664.00 @ 11-30 13:45 |
| C 价 | 7820.00 @ 12-29 10:45 |
| 最新价 | 7618.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 14 (merge 后: 14) |
| A 索引 | 3 | C 索引 | 11 |

**极值点序列** (swing: 14, merged: 14):
```
  [ 0] PEAK   price= 8674.00 time= 11-04 13:45
  [ 1] TROUGH price= 8120.00 time= 11-10 10:45
  [ 2] PEAK   price= 8626.00 time= 11-11 13:45
  [ 3] TROUGH price= 7710.00 time= 11-21 10:45 ← A
  [ 4] PEAK   price= 8664.00 time= 11-30 13:45
  [ 5] TROUGH price= 7418.00 time= 12-12 13:45
  [ 6] PEAK   price= 7812.00 time= 12-14 13:45
  [ 7] TROUGH price= 7482.00 time= 12-20 13:45
  [ 8] PEAK   price= 7724.00 time= 12-22 09:15
  [ 9] TROUGH price= 7408.00 time= 12-23 09:15
  [10] PEAK   price= 8044.00 time= 12-27 13:45
  [11] TROUGH price= 7820.00 time= 12-29 10:45 ← C
  [12] PEAK   price= 8102.00 time= 12-30 13:45
  [13] TROUGH price= 7472.00 time= 01-03 21:15
```

**失败详情:**
```
  ❌ C4 最新(7618.00) > C(7820.00) = False
```
---

### P — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 7766.00 @ 08-30 11:00 |
| B 价 | 7952.00 @ 08-31 14:00 |
| C 价 | 7816.00 @ 08-31 22:00 |
| 最新价 | 7624.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 45 | C 索引 | 47 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 7640.00 time= 07-24 09:15
  [ 1] TROUGH price= 7518.00 time= 07-24 10:00
  [ 2] PEAK   price= 7776.00 time= 07-25 11:00
  [ 3] TROUGH price= 7638.00 time= 07-25 21:15
  [ 4] PEAK   price= 7858.00 time= 07-27 09:15
  [ 5] TROUGH price= 7710.00 time= 07-27 11:00
  [ 6] PEAK   price= 7778.00 time= 07-27 14:00
  [ 7] TROUGH price= 7566.00 time= 07-28 11:00
  [ 8] PEAK   price= 7668.00 time= 07-28 21:15
  [ 9] TROUGH price= 7430.00 time= 07-31 14:00
  [10] PEAK   price= 7486.00 time= 07-31 22:00
  [11] TROUGH price= 7436.00 time= 08-01 10:00
  [12] PEAK   price= 7680.00 time= 08-02 11:00
  [13] TROUGH price= 7416.00 time= 08-03 22:00
  [14] PEAK   price= 7616.00 time= 08-04 10:00
  [15] TROUGH price= 7502.00 time= 08-04 14:00
  [16] PEAK   price= 7664.00 time= 08-07 09:15
  [17] TROUGH price= 7406.00 time= 08-07 21:15
  [18] PEAK   price= 7462.00 time= 08-08 09:15
  [19] TROUGH price= 7274.00 time= 08-08 21:15
  [20] PEAK   price= 7528.00 time= 08-09 22:00
  [21] TROUGH price= 7402.00 time= 08-10 11:00
  [22] PEAK   price= 7496.00 time= 08-10 22:00
  [23] TROUGH price= 7344.00 time= 08-11 14:00
  [24] PEAK   price= 7508.00 time= 08-14 10:00
  [25] TROUGH price= 7346.00 time= 08-14 13:45
  [26] PEAK   price= 7634.00 time= 08-15 21:15
  [27] TROUGH price= 7548.00 time= 08-16 09:15
  [28] PEAK   price= 7664.00 time= 08-16 21:15
  [29] TROUGH price= 7568.00 time= 08-17 09:15
  [30] PEAK   price= 7720.00 time= 08-18 10:45
  [31] TROUGH price= 7610.00 time= 08-18 21:15
  [32] PEAK   price= 7812.00 time= 08-21 09:15
  [33] TROUGH price= 7612.00 time= 08-22 14:00
  [34] PEAK   price= 7722.00 time= 08-22 21:15
  [35] TROUGH price= 7576.00 time= 08-23 09:15
  [36] PEAK   price= 7676.00 time= 08-23 11:00
  [37] TROUGH price= 7610.00 time= 08-23 21:15
  [38] PEAK   price= 7800.00 time= 08-24 10:00
  [39] TROUGH price= 7672.00 time= 08-24 22:00
  [40] PEAK   price= 7930.00 time= 08-28 09:15
  [41] TROUGH price= 7720.00 time= 08-28 21:15
  [42] PEAK   price= 7858.00 time= 08-29 11:00
  [43] TROUGH price= 7752.00 time= 08-29 15:00
  [44] PEAK   price= 7846.00 time= 08-30 09:15
  [45] TROUGH price= 7766.00 time= 08-30 11:00 ← A
  [46] PEAK   price= 7952.00 time= 08-31 14:00
  [47] TROUGH price= 7816.00 time= 08-31 22:00 ← C
  [48] PEAK   price= 7928.00 time= 09-01 13:45
  [49] TROUGH price= 7624.00 time= 09-06 21:45
```

**失败详情:**
```
  ❌ C4 最新(7624.00) > C(7816.00) = False
```
---

### P — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 7858.00 time= 07-24 09:15
  [ 1] TROUGH price= 7274.00 time= 08-07 09:15
  [ 2] PEAK   price= 7952.00 time= 08-28 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### P — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 7460.00 @ 08-14 10:45 |
| B 价 | 8190.00 @ 08-27 10:45 |
| C 价 | 8000.00 @ 08-29 09:15 |
| 最新价 | 7802.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 11 | C 索引 | 13 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] PEAK   price= 8106.00 time= 07-03 13:45
  [ 1] TROUGH price= 7560.00 time= 07-10 10:45
  [ 2] PEAK   price= 7954.00 time= 07-17 10:45
  [ 3] TROUGH price= 7732.00 time= 07-19 13:45
  [ 4] PEAK   price= 8038.00 time= 07-23 09:15
  [ 5] TROUGH price= 7632.00 time= 07-29 09:15
  [ 6] PEAK   price= 7948.00 time= 07-30 10:45
  [ 7] TROUGH price= 7736.00 time= 08-01 10:45
  [ 8] PEAK   price= 7998.00 time= 08-02 13:45
  [ 9] TROUGH price= 7542.00 time= 08-06 13:45
  [10] PEAK   price= 7774.00 time= 08-09 13:45
  [11] TROUGH price= 7460.00 time= 08-14 10:45 ← A
  [12] PEAK   price= 8190.00 time= 08-27 10:45
  [13] TROUGH price= 8000.00 time= 08-29 09:15 ← C
  [14] PEAK   price= 8454.00 time= 08-30 13:45
```

**失败详情:**
```
  ❌ C4 最新(7802.00) > C(8000.00) = False
```
---

### P — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 8038.00 time= 07-22 09:15
  [ 1] TROUGH price= 7460.00 time= 08-12 09:15
  [ 2] PEAK   price= 8454.00 time= 08-26 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### P — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 9988.00 @ 01-07 13:45 |
| B 价 | 9750.00 @ 01-09 09:30 |
| C 价 | 9940.00 @ 01-09 22:00 |
| 最新价 | 9954.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 9758.00 time= 12-19 09:15
  [ 1] PEAK   price= 9860.00 time= 12-19 10:15
  [ 2] TROUGH price= 9494.00 time= 12-19 15:00
  [ 3] PEAK   price= 9648.00 time= 12-19 21:15
  [ 4] TROUGH price= 9572.00 time= 12-19 22:00
  [ 5] PEAK   price= 9610.00 time= 12-19 22:45
  [ 6] TROUGH price= 9518.00 time= 12-20 11:15
  [ 7] PEAK   price= 9614.00 time= 12-20 13:45
  [ 8] TROUGH price= 9286.00 time= 12-20 22:30
  [ 9] PEAK   price= 9412.00 time= 12-23 09:30
  [10] TROUGH price= 9360.00 time= 12-23 10:45
  [11] PEAK   price= 9692.00 time= 12-23 21:15
  [12] TROUGH price= 9612.00 time= 12-23 22:15
  [13] PEAK   price= 9678.00 time= 12-24 11:30
  [14] TROUGH price= 9614.00 time= 12-24 13:45
  [15] PEAK   price= 9784.00 time= 12-24 21:15
  [16] TROUGH price= 9604.00 time= 12-25 11:00
  [17] PEAK   price= 9708.00 time= 12-25 14:30
  [18] TROUGH price= 9638.00 time= 12-25 21:15
  [19] PEAK   price= 9708.00 time= 12-26 09:15
  [20] TROUGH price= 9648.00 time= 12-26 10:00
  [21] PEAK   price= 9776.00 time= 12-26 13:45
  [22] TROUGH price= 9730.00 time= 12-26 14:15
  [23] PEAK   price= 9862.00 time= 12-26 21:30
  [24] TROUGH price= 9812.00 time= 12-27 14:45
  [25] PEAK   price= 9884.00 time= 12-27 21:15
  [26] TROUGH price= 9732.00 time= 12-30 09:15
  [27] PEAK   price= 9850.00 time= 12-30 11:00
  [28] TROUGH price= 9812.00 time= 12-30 14:00
  [29] PEAK   price= 9900.00 time= 12-30 15:00
  [30] TROUGH price= 9960.00 time= 12-31 13:45
  [31] PEAK   price=10094.00 time= 01-02 09:15
  [32] TROUGH price= 9490.00 time= 01-02 22:45
  [33] PEAK   price=10028.00 time= 01-06 10:15
  [34] TROUGH price= 9890.00 time= 01-06 15:00
  [35] PEAK   price= 9988.00 time= 01-07 13:45 ← A
  [36] TROUGH price= 9750.00 time= 01-09 09:30
  [37] PEAK   price= 9940.00 time= 01-09 22:00 ← C
  [38] TROUGH price= 9750.00 time= 01-10 11:30
  [39] PEAK   price=10800.00 time= 01-15 09:45
```

**失败详情:**
```
  ❌ C4 最新(9954.00) < C(9940.00) = False
```
---

### P — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8534.00 @ 04-29 21:15 |
| B 价 | 8060.00 @ 05-06 09:15 |
| C 价 | 8450.00 @ 05-12 15:00 |
| 最新价 | 8724.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 33 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 8738.00 time= 04-14 21:15
  [ 1] PEAK   price= 8772.00 time= 04-14 22:45
  [ 2] TROUGH price= 8666.00 time= 04-15 11:15
  [ 3] PEAK   price= 8736.00 time= 04-15 13:45
  [ 4] TROUGH price= 8674.00 time= 04-15 21:15
  [ 5] PEAK   price= 8752.00 time= 04-16 09:30
  [ 6] TROUGH price= 8598.00 time= 04-16 14:30
  [ 7] PEAK   price= 8668.00 time= 04-16 21:15
  [ 8] TROUGH price= 8642.00 time= 04-16 22:45
  [ 9] PEAK   price= 8726.00 time= 04-17 13:45
  [10] TROUGH price= 8682.00 time= 04-17 21:15
  [11] PEAK   price= 8740.00 time= 04-17 21:45
  [12] TROUGH price= 8592.00 time= 04-18 09:45
  [13] PEAK   price= 8672.00 time= 04-18 10:45
  [14] TROUGH price= 8532.00 time= 04-18 21:15
  [15] PEAK   price= 8590.00 time= 04-18 23:00
  [16] TROUGH price= 8516.00 time= 04-21 11:15
  [17] PEAK   price= 8556.00 time= 04-21 14:30
  [18] TROUGH price= 8444.00 time= 04-21 23:00
  [19] PEAK   price= 8584.00 time= 04-22 10:15
  [20] TROUGH price= 8524.00 time= 04-22 11:15
  [21] PEAK   price= 8622.00 time= 04-22 14:30
  [22] TROUGH price= 8534.00 time= 04-22 23:00
  [23] PEAK   price= 8614.00 time= 04-23 09:30
  [24] TROUGH price= 8512.00 time= 04-23 11:00
  [25] PEAK   price= 8584.00 time= 04-23 13:45
  [26] TROUGH price= 8532.00 time= 04-23 21:30
  [27] PEAK   price= 8800.00 time= 04-25 11:15
  [28] TROUGH price= 8636.00 time= 04-28 09:15
  [29] PEAK   price= 8686.00 time= 04-28 10:15
  [30] TROUGH price= 8554.00 time= 04-28 21:15
  [31] PEAK   price= 8592.00 time= 04-28 23:00
  [32] TROUGH price= 8566.00 time= 04-29 09:15
  [33] PEAK   price= 8534.00 time= 04-29 21:15 ← A
  [34] TROUGH price= 8452.00 time= 04-30 09:15
  [35] PEAK   price= 8798.00 time= 04-30 15:00
  [36] TROUGH price= 8060.00 time= 05-06 09:15
  [37] PEAK   price= 8450.00 time= 05-12 15:00 ← C
  [38] TROUGH price= 8316.00 time= 05-13 22:00
  [39] PEAK   price= 8920.00 time= 05-16 10:15
```

**失败详情:**
```
  ❌ C4 最新(8724.00) < C(8450.00) = False
```
---

### P — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8800.00 @ 04-25 10:45 |
| B 价 | 8060.00 @ 05-06 09:15 |
| C 价 | 8450.00 @ 05-12 14:00 |
| 最新价 | 8724.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 14 (merge 后: 14) |
| A 索引 | 11 | C 索引 | 13 |

**极值点序列** (swing: 14, merged: 14):
```
  [ 0] TROUGH price= 8748.00 time= 03-05 10:45
  [ 1] PEAK   price= 9282.00 time= 03-10 09:15
  [ 2] TROUGH price= 8878.00 time= 03-11 13:45
  [ 3] PEAK   price= 9180.00 time= 03-17 09:15
  [ 4] TROUGH price= 8926.00 time= 03-19 13:45
  [ 5] PEAK   price= 9180.00 time= 03-20 13:45
  [ 6] TROUGH price= 8782.00 time= 03-26 09:15
  [ 7] PEAK   price= 9346.00 time= 04-02 09:15
  [ 8] TROUGH price= 8510.00 time= 04-09 13:45
  [ 9] PEAK   price= 8830.00 time= 04-11 09:15
  [10] TROUGH price= 8444.00 time= 04-21 13:45
  [11] PEAK   price= 8800.00 time= 04-25 10:45 ← A
  [12] TROUGH price= 8060.00 time= 05-06 09:15
  [13] PEAK   price= 8450.00 time= 05-12 14:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(8724.00) < C(8450.00) = False
```
---

### P — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9386.00 @ 08-28 09:30 |
| B 价 | 9452.00 @ 08-28 10:00 |
| C 价 | 9446.00 @ 09-09 21:15 |
| 最新价 | 9446.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 19 | C 索引 | 39 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 9532.00 time= 08-22 09:15
  [ 1] TROUGH price= 9484.00 time= 08-22 09:30
  [ 2] PEAK   price= 9514.00 time= 08-22 10:15
  [ 3] TROUGH price= 9432.00 time= 08-22 14:30
  [ 4] PEAK   price= 9532.00 time= 08-22 21:15
  [ 5] TROUGH price= 9468.00 time= 08-22 22:00
  [ 6] PEAK   price= 9594.00 time= 08-25 09:15
  [ 7] TROUGH price= 9490.00 time= 08-25 11:15
  [ 8] PEAK   price= 9534.00 time= 08-25 14:30
  [ 9] TROUGH price= 9412.00 time= 08-26 09:15
  [10] PEAK   price= 9478.00 time= 08-26 10:00
  [11] TROUGH price= 9384.00 time= 08-26 21:15
  [12] PEAK   price= 9450.00 time= 08-26 22:15
  [13] TROUGH price= 9380.00 time= 08-26 22:45
  [14] PEAK   price= 9472.00 time= 08-27 09:30
  [15] TROUGH price= 9430.00 time= 08-27 10:15
  [16] PEAK   price= 9464.00 time= 08-27 11:30
  [17] TROUGH price= 9400.00 time= 08-27 21:45
  [18] PEAK   price= 9458.00 time= 08-27 22:15
  [19] TROUGH price= 9386.00 time= 08-28 09:30 ← A
  [20] PEAK   price= 9452.00 time= 08-28 10:00
  [21] TROUGH price= 9338.00 time= 08-28 14:00
  [22] PEAK   price= 9380.00 time= 08-28 14:30
  [23] TROUGH price= 9290.00 time= 08-28 23:00
  [24] PEAK   price= 9336.00 time= 08-29 09:30
  [25] TROUGH price= 9262.00 time= 08-29 13:45
  [26] PEAK   price= 9332.00 time= 08-29 15:00
  [27] TROUGH price= 9182.00 time= 08-29 22:00
  [28] PEAK   price= 9378.00 time= 09-01 09:30
  [29] TROUGH price= 9300.00 time= 09-01 14:00
  [30] PEAK   price= 9450.00 time= 09-01 21:45
  [31] TROUGH price= 9346.00 time= 09-02 10:15
  [32] PEAK   price= 9402.00 time= 09-03 11:00
  [33] TROUGH price= 9308.00 time= 09-04 10:15
  [34] PEAK   price= 9400.00 time= 09-04 11:30
  [35] TROUGH price= 9300.00 time= 09-05 11:15
  [36] PEAK   price= 9408.00 time= 09-05 11:30
  [37] TROUGH price= 9320.00 time= 09-08 09:45
  [38] PEAK   price= 9494.00 time= 09-09 10:45
  [39] TROUGH price= 9446.00 time= 09-09 21:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(9446.00) > C(9446.00) = False
```
---

### P — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 9104.00 time= 07-21 09:15
  [ 1] TROUGH price= 8746.00 time= 08-04 09:15
  [ 2] PEAK   price= 9694.00 time= 08-18 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### P — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8290.00 @ 01-05 13:45 |
| B 价 | 8380.00 @ 01-06 09:15 |
| C 价 | 8362.00 @ 01-07 13:45 |
| 最新价 | 8244.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 8458.00 time= 12-18 10:45
  [ 1] TROUGH price= 8352.00 time= 12-18 15:00
  [ 2] PEAK   price= 8396.00 time= 12-18 22:15
  [ 3] TROUGH price= 8264.00 time= 12-19 11:00
  [ 4] PEAK   price= 8308.00 time= 12-19 13:45
  [ 5] TROUGH price= 8230.00 time= 12-19 21:15
  [ 6] PEAK   price= 8352.00 time= 12-22 09:45
  [ 7] TROUGH price= 8292.00 time= 12-22 11:00
  [ 8] PEAK   price= 8468.00 time= 12-22 21:45
  [ 9] TROUGH price= 8372.00 time= 12-23 09:15
  [10] PEAK   price= 8522.00 time= 12-23 21:30
  [11] TROUGH price= 8458.00 time= 12-23 23:00
  [12] PEAK   price= 8518.00 time= 12-24 11:00
  [13] TROUGH price= 8484.00 time= 12-24 11:15
  [14] PEAK   price= 8518.00 time= 12-24 14:00
  [15] TROUGH price= 8474.00 time= 12-24 14:45
  [16] PEAK   price= 8558.00 time= 12-25 09:15
  [17] TROUGH price= 8510.00 time= 12-25 11:30
  [18] PEAK   price= 8572.00 time= 12-25 21:15
  [19] TROUGH price= 8518.00 time= 12-25 22:15
  [20] PEAK   price= 8546.00 time= 12-26 09:15
  [21] TROUGH price= 8472.00 time= 12-26 10:00
  [22] PEAK   price= 8576.00 time= 12-26 11:15
  [23] TROUGH price= 8532.00 time= 12-26 15:00
  [24] PEAK   price= 8582.00 time= 12-26 21:15
  [25] TROUGH price= 8498.00 time= 12-29 11:15
  [26] PEAK   price= 8542.00 time= 12-29 11:30
  [27] TROUGH price= 8494.00 time= 12-29 15:00
  [28] PEAK   price= 8560.00 time= 12-29 21:15
  [29] TROUGH price= 8518.00 time= 12-29 22:30
  [30] PEAK   price= 8658.00 time= 12-30 13:45
  [31] TROUGH price= 8596.00 time= 12-30 21:30
  [32] PEAK   price= 8618.00 time= 12-30 23:00
  [33] TROUGH price= 8064.00 time= 01-05 09:15
  [34] PEAK   price= 8438.00 time= 01-05 10:45
  [35] TROUGH price= 8290.00 time= 01-05 13:45 ← A
  [36] PEAK   price= 8380.00 time= 01-06 09:15
  [37] TROUGH price= 8362.00 time= 01-07 13:45 ← C
  [38] PEAK   price= 8680.00 time= 01-13 14:15
  [39] TROUGH price= 8244.00 time= 01-15 22:15
```

**失败详情:**
```
  ❌ C4 最新(8244.00) > C(8362.00) = False
```
---

### P — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 9340.00 @ 05-14 21:15 |
| B 价 | 8994.00 @ 05-15 21:15 |
| C 价 | 9230.00 @ 05-18 14:15 |
| 最新价 | 9230.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 9392.00 time= 04-21 11:30
  [ 1] PEAK   price= 9606.00 time= 04-21 14:15
  [ 2] TROUGH price= 9524.00 time= 04-21 21:45
  [ 3] PEAK   price= 9673.00 time= 04-22 09:30
  [ 4] TROUGH price= 9604.00 time= 04-22 10:45
  [ 5] PEAK   price= 9684.00 time= 04-22 11:30
  [ 6] TROUGH price= 9560.00 time= 04-22 14:00
  [ 7] PEAK   price= 9678.00 time= 04-22 21:15
  [ 8] TROUGH price= 9486.00 time= 04-23 10:00
  [ 9] PEAK   price= 9593.00 time= 04-23 11:15
  [10] TROUGH price= 9506.00 time= 04-23 21:15
  [11] PEAK   price= 9620.00 time= 04-23 22:00
  [12] TROUGH price= 9490.00 time= 04-24 14:30
  [13] PEAK   price= 9561.00 time= 04-24 21:30
  [14] TROUGH price= 9520.00 time= 04-24 22:00
  [15] PEAK   price= 9650.00 time= 04-27 09:15
  [16] TROUGH price= 9476.00 time= 04-27 21:30
  [17] PEAK   price= 9542.00 time= 04-28 09:45
  [18] TROUGH price= 9410.00 time= 04-28 11:15
  [19] PEAK   price= 9500.00 time= 04-28 21:15
  [20] TROUGH price= 9380.00 time= 04-28 23:00
  [21] PEAK   price= 9568.00 time= 04-29 21:15
  [22] TROUGH price= 9490.00 time= 04-29 22:45
  [23] PEAK   price= 9558.00 time= 04-30 09:15
  [24] TROUGH price= 9515.00 time= 04-30 10:15
  [25] PEAK   price= 9579.00 time= 04-30 13:45
  [26] TROUGH price= 9523.00 time= 04-30 15:00
  [27] PEAK   price= 9679.00 time= 05-06 09:15
  [28] TROUGH price= 9050.00 time= 05-06 21:15
  [29] PEAK   price= 9450.00 time= 05-07 14:45
  [30] TROUGH price= 9375.00 time= 05-07 21:45
  [31] PEAK   price= 9438.00 time= 05-11 09:15
  [32] TROUGH price= 8880.00 time= 05-11 21:30
  [33] PEAK   price= 9337.00 time= 05-11 22:45
  [34] TROUGH price= 9297.00 time= 05-12 15:00
  [35] PEAK   price= 9340.00 time= 05-14 21:15 ← A
  [36] TROUGH price= 8994.00 time= 05-15 21:15
  [37] PEAK   price= 9230.00 time= 05-18 14:15 ← C
  [38] TROUGH price= 9216.00 time= 05-19 13:45
  [39] PEAK   price= 9230.00 time= 05-19 14:00
```

**失败详情:**
```
  ❌ C4 最新(9230.00) < C(9230.00) = False
```
---

### P — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9151.00 @ 06-15 21:15 |
| B 价 | 9429.00 @ 06-16 22:00 |
| C 价 | 9318.00 @ 06-17 10:45 |
| 最新价 | 9301.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 37 |

**极值点序列** (swing: 50, merged: 40):
```
  [ 0] PEAK   price= 9594.00 time= 05-18 14:00
  [ 1] TROUGH price= 9494.00 time= 05-18 21:15
  [ 2] PEAK   price= 9706.00 time= 05-19 14:00
  [ 3] TROUGH price= 9584.00 time= 05-20 10:00
  [ 4] PEAK   price= 9857.00 time= 05-20 13:45
  [ 5] TROUGH price= 9423.00 time= 05-22 09:15
  [ 6] PEAK   price= 9546.00 time= 05-22 11:00
  [ 7] TROUGH price= 9333.00 time= 05-25 09:15
  [ 8] PEAK   price= 9540.00 time= 05-26 09:15
  [ 9] TROUGH price= 9433.00 time= 05-26 14:00
  [10] PEAK   price= 9578.00 time= 05-27 14:15
  [11] TROUGH price= 9470.00 time= 05-27 21:15
  [12] PEAK   price= 9642.00 time= 05-28 21:15
  [13] TROUGH price= 9572.00 time= 05-28 23:00
  [14] PEAK   price= 9626.00 time= 05-29 14:00
  [15] TROUGH price= 9573.00 time= 05-29 14:15
  [16] PEAK   price= 9760.00 time= 06-01 23:00
  [17] TROUGH price= 9694.00 time= 06-02 10:00
  [18] PEAK   price= 9735.00 time= 06-02 13:45
  [19] TROUGH price= 9664.00 time= 06-02 22:00
  [20] PEAK   price= 9778.00 time= 06-03 09:15
  [21] TROUGH price= 9683.00 time= 06-03 11:00
  [22] PEAK   price= 9825.00 time= 06-03 21:15
  [23] TROUGH price= 9286.00 time= 06-08 09:15
  [24] PEAK   price= 9456.00 time= 06-08 13:45
  [25] TROUGH price= 9222.00 time= 06-09 13:45
  [26] PEAK   price= 9325.00 time= 06-09 21:15
  [27] TROUGH price= 9243.00 time= 06-10 09:12
  [28] PEAK   price= 9320.00 time= 06-10 11:00
  [29] TROUGH price= 9220.00 time= 06-10 13:30
  [30] PEAK   price= 9405.00 time= 06-11 09:00
  [31] TROUGH price= 9341.00 time= 06-11 11:00
  [32] PEAK   price= 9420.00 time= 06-11 14:00
  [33] TROUGH price= 9321.00 time= 06-12 09:00
  [34] PEAK   price= 9404.00 time= 06-12 14:15
  [35] TROUGH price= 9151.00 time= 06-15 21:15 ← A
  [36] PEAK   price= 9429.00 time= 06-16 22:00
  [37] TROUGH price= 9318.00 time= 06-17 10:45 ← C
  [38] PEAK   price= 9411.00 time= 06-17 23:00
  [39] TROUGH price= 9221.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(9301.00) > C(9318.00) = False
```
---

### PB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 16195.00 @ 03-10 00:00 |
| B 价 | 17005.00 @ 05-06 00:00 |
| C 价 | 16400.00 @ 05-19 00:00 |
| 最新价 | 16130.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 80 (merge 后: 80) |
| A 索引 | 77 | C 索引 | 79 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] PEAK   price=15515.00 time= 01-14 00:00
  [ 1] TROUGH price=13815.00 time= 02-04 00:00
  [ 2] PEAK   price=15200.00 time= 03-03 00:00
  [ 3] TROUGH price=12620.00 time= 03-17 00:00
  [ 4] PEAK   price=14235.00 time= 04-14 00:00
  [ 5] TROUGH price=13425.00 time= 04-21 00:00
  [ 6] PEAK   price=16585.00 time= 08-04 00:00
  [ 7] TROUGH price=14050.00 time= 10-27 00:00
  [ 8] PEAK   price=15900.00 time= 11-24 00:00
  [ 9] TROUGH price=14065.00 time= 12-22 00:00
  [10] PEAK   price=16145.00 time= 02-23 00:00
  [11] TROUGH price=14600.00 time= 03-09 00:00
  [12] PEAK   price=15475.00 time= 03-30 00:00
  [13] TROUGH price=14610.00 time= 04-13 00:00
  [14] PEAK   price=15885.00 time= 05-06 00:00
  [15] TROUGH price=14900.00 time= 06-08 00:00
  [16] PEAK   price=16420.00 time= 07-20 00:00
  [17] TROUGH price=14055.00 time= 09-22 00:00
  [18] PEAK   price=16330.00 time= 10-19 00:00
  [19] TROUGH price=14585.00 time= 11-16 00:00
  [20] PEAK   price=15870.00 time= 12-14 00:00
  [21] TROUGH price=15050.00 time= 01-04 00:00
  [22] PEAK   price=15875.00 time= 01-18 00:00
  [23] TROUGH price=14690.00 time= 02-08 00:00
  [24] PEAK   price=16465.00 time= 03-08 00:00
  [25] TROUGH price=14910.00 time= 03-15 00:00
  [26] PEAK   price=15875.00 time= 03-29 00:00
  [27] TROUGH price=15305.00 time= 04-12 00:00
  [28] PEAK   price=15900.00 time= 05-05 00:00
  [29] TROUGH price=14680.00 time= 05-17 00:00
  [30] PEAK   price=15310.00 time= 06-07 00:00
  [31] TROUGH price=14800.00 time= 06-21 00:00
  [32] PEAK   price=15375.00 time= 06-28 00:00
  [33] TROUGH price=14345.00 time= 07-12 00:00
  [34] PEAK   price=15450.00 time= 08-09 00:00
  [35] TROUGH price=14795.00 time= 08-30 00:00
  [36] PEAK   price=15195.00 time= 09-13 00:00
  [37] TROUGH price=14820.00 time= 09-27 00:00
  [38] PEAK   price=15510.00 time= 10-18 00:00
  [39] TROUGH price=15055.00 time= 10-25 00:00
  [40] PEAK   price=16045.00 time= 11-29 00:00
  [41] TROUGH price=15410.00 time= 12-13 00:00
  [42] PEAK   price=16205.00 time= 12-27 00:00
  [43] TROUGH price=15080.00 time= 02-14 00:00
  [44] PEAK   price=15500.00 time= 02-21 00:00
  [45] TROUGH price=15120.00 time= 03-07 00:00
  [46] PEAK   price=15450.00 time= 03-14 00:00
  [47] TROUGH price=15015.00 time= 05-30 00:00
  [48] PEAK   price=17540.00 time= 08-29 00:00
  [49] TROUGH price=16080.00 time= 10-10 00:00
  [50] PEAK   price=17195.00 time= 11-14 00:00
  [51] TROUGH price=15405.00 time= 12-05 00:00
  [52] PEAK   price=16730.00 time= 01-23 00:00
  [53] TROUGH price=15790.00 time= 02-20 00:00
  [54] PEAK   price=19175.00 time= 05-21 00:00
  [55] TROUGH price=18415.00 time= 06-11 00:00
  [56] PEAK   price=20050.00 time= 07-16 00:00
  [57] TROUGH price=16245.00 time= 09-18 00:00
  [58] PEAK   price=17100.00 time= 10-08 00:00
  [59] TROUGH price=16450.00 time= 10-15 00:00
  [60] PEAK   price=17910.00 time= 12-03 00:00
  [61] TROUGH price=16305.00 time= 01-07 00:00
  [62] PEAK   price=17805.00 time= 03-18 00:00
  [63] TROUGH price=16165.00 time= 04-08 00:00
  [64] PEAK   price=17085.00 time= 04-22 00:00
  [65] TROUGH price=16625.00 time= 05-06 00:00
  [66] PEAK   price=17050.00 time= 05-13 00:00
  [67] TROUGH price=16525.00 time= 06-03 00:00
  [68] PEAK   price=17315.00 time= 07-01 00:00
  [69] TROUGH price=16615.00 time= 07-29 00:00
  [70] PEAK   price=17840.00 time= 11-11 00:00
  [71] TROUGH price=15885.00 time= 11-25 00:00
  [72] PEAK   price=17380.00 time= 12-02 00:00
  [73] TROUGH price=16680.00 time= 12-16 00:00
  [74] PEAK   price=17860.00 time= 01-06 00:00
  [75] TROUGH price=16400.00 time= 01-27 00:00
  [76] PEAK   price=17020.00 time= 03-03 00:00
  [77] TROUGH price=16195.00 time= 03-10 00:00 ← A
  [78] PEAK   price=17005.00 time= 05-06 00:00
  [79] TROUGH price=16400.00 time= 05-19 00:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(16130.00) > C(16400.00) = False
```
---

### PG — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3717.00 @ 12-30 14:00 |
| B 价 | 3953.00 @ 01-07 11:00 |
| C 价 | 3814.00 @ 01-11 11:15 |
| 最新价 | 3620.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 30 | C 索引 | 38 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 3883.00 time= 12-18 21:15
  [ 1] PEAK   price= 4104.00 time= 12-21 09:30
  [ 2] TROUGH price= 3977.00 time= 12-21 11:15
  [ 3] PEAK   price= 4049.00 time= 12-21 14:15
  [ 4] TROUGH price= 3883.00 time= 12-21 21:30
  [ 5] PEAK   price= 3975.00 time= 12-22 09:15
  [ 6] TROUGH price= 3914.00 time= 12-22 09:30
  [ 7] PEAK   price= 3991.00 time= 12-22 11:00
  [ 8] TROUGH price= 3867.00 time= 12-22 14:30
  [ 9] PEAK   price= 3955.00 time= 12-22 21:30
  [10] TROUGH price= 3746.00 time= 12-23 10:15
  [11] PEAK   price= 3908.00 time= 12-23 21:15
  [12] TROUGH price= 3838.00 time= 12-23 21:45
  [13] PEAK   price= 3904.00 time= 12-24 09:15
  [14] TROUGH price= 3828.00 time= 12-24 14:00
  [15] PEAK   price= 3920.00 time= 12-24 15:00
  [16] TROUGH price= 3851.00 time= 12-25 09:15
  [17] PEAK   price= 3923.00 time= 12-25 13:45
  [18] TROUGH price= 3894.00 time= 12-25 15:00
  [19] PEAK   price= 3950.00 time= 12-25 21:15
  [20] TROUGH price= 3865.00 time= 12-25 22:45
  [21] PEAK   price= 3920.00 time= 12-28 09:45
  [22] TROUGH price= 3783.00 time= 12-28 14:30
  [23] PEAK   price= 3844.00 time= 12-28 21:45
  [24] TROUGH price= 3820.00 time= 12-28 22:00
  [25] PEAK   price= 3850.00 time= 12-28 23:00
  [26] TROUGH price= 3810.00 time= 12-29 09:15
  [27] PEAK   price= 3701.00 time= 12-29 21:15
  [28] TROUGH price= 3654.00 time= 12-29 22:00
  [29] PEAK   price= 3740.00 time= 12-30 09:30
  [30] TROUGH price= 3717.00 time= 12-30 14:00 ← A
  [31] PEAK   price= 3743.00 time= 12-30 21:15
  [32] TROUGH price= 3680.00 time= 12-30 22:00
  [33] PEAK   price= 3722.00 time= 12-31 09:15
  [34] TROUGH price= 3686.00 time= 12-31 09:30
  [35] PEAK   price= 3759.00 time= 12-31 14:15
  [36] TROUGH price= 3707.00 time= 12-31 15:00
  [37] PEAK   price= 3953.00 time= 01-07 11:00
  [38] TROUGH price= 3814.00 time= 01-11 11:15 ← C
  [39] PEAK   price= 4013.00 time= 01-13 22:15
```

**失败详情:**
```
  ❌ C4 最新(3620.00) > C(3814.00) = False
```
---

### PG — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3654.00 @ 12-29 22:00 |
| B 价 | 3743.00 @ 12-30 21:15 |
| C 价 | 3680.00 @ 12-30 22:00 |
| 最新价 | 3620.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 49) |
| A 索引 | 43 | C 索引 | 45 |

**极值点序列** (swing: 50, merged: 49):
```
  [ 0] PEAK   price= 3691.00 time= 11-25 09:15
  [ 1] TROUGH price= 3643.00 time= 11-25 22:00
  [ 2] PEAK   price= 3727.00 time= 11-26 09:15
  [ 3] TROUGH price= 3648.00 time= 11-26 21:15
  [ 4] PEAK   price= 3730.00 time= 11-26 22:00
  [ 5] TROUGH price= 3674.00 time= 11-27 21:15
  [ 6] PEAK   price= 3770.00 time= 11-30 09:15
  [ 7] TROUGH price= 3670.00 time= 11-30 14:00
  [ 8] PEAK   price= 3803.00 time= 12-01 10:45
  [ 9] TROUGH price= 3645.00 time= 12-02 10:00
  [10] PEAK   price= 3745.00 time= 12-02 21:15
  [11] TROUGH price= 3661.00 time= 12-03 11:00
  [12] PEAK   price= 3689.00 time= 12-03 21:15
  [13] TROUGH price= 3666.00 time= 12-04 14:00
  [14] PEAK   price= 3918.00 time= 12-08 09:15
  [15] TROUGH price= 3852.00 time= 12-08 21:15
  [16] PEAK   price= 3905.00 time= 12-09 14:00
  [17] TROUGH price= 3696.00 time= 12-09 15:00
  [18] PEAK   price= 3758.00 time= 12-10 09:15
  [19] TROUGH price= 3716.00 time= 12-10 15:00
  [20] PEAK   price= 3986.00 time= 12-14 09:15
  [21] TROUGH price= 3867.00 time= 12-15 10:00
  [22] PEAK   price= 3922.00 time= 12-15 13:45
  [23] TROUGH price= 3837.00 time= 12-16 10:00
  [24] PEAK   price= 3895.00 time= 12-16 13:45
  [25] TROUGH price= 3783.00 time= 12-17 10:00
  [26] PEAK   price= 3850.00 time= 12-17 11:00
  [27] TROUGH price= 3875.00 time= 12-18 10:00
  [28] PEAK   price= 3997.00 time= 12-18 11:00
  [29] TROUGH price= 3883.00 time= 12-18 21:15
  [30] PEAK   price= 4104.00 time= 12-21 09:15
  [31] TROUGH price= 3977.00 time= 12-21 11:00
  [32] PEAK   price= 4049.00 time= 12-21 14:00
  [33] TROUGH price= 3883.00 time= 12-21 21:15
  [34] PEAK   price= 3991.00 time= 12-22 11:00
  [35] TROUGH price= 3746.00 time= 12-23 10:00
  [36] PEAK   price= 3908.00 time= 12-23 21:15
  [37] TROUGH price= 3828.00 time= 12-24 14:00
  [38] PEAK   price= 3920.00 time= 12-24 15:00
  [39] TROUGH price= 3851.00 time= 12-25 09:15
  [40] PEAK   price= 3950.00 time= 12-25 21:15
  [41] TROUGH price= 3783.00 time= 12-28 14:00
  [42] PEAK   price= 3850.00 time= 12-28 23:00
  [43] TROUGH price= 3654.00 time= 12-29 22:00 ← A
  [44] PEAK   price= 3743.00 time= 12-30 21:15
  [45] TROUGH price= 3680.00 time= 12-30 22:00 ← C
  [46] PEAK   price= 3953.00 time= 01-07 11:00
  [47] TROUGH price= 3814.00 time= 01-11 11:15
  [48] PEAK   price= 4013.00 time= 01-13 22:15
```

**失败详情:**
```
  ❌ C4 最新(3620.00) > C(3680.00) = False
```
---

### PG — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3463.00 @ 11-16 09:15 |
| B 价 | 4104.00 @ 12-21 09:15 |
| C 价 | 3654.00 @ 12-28 09:15 |
| 最新价 | 3620.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 4 (merge 后: 4) |
| A 索引 | 0 | C 索引 | 2 |

**极值点序列** (swing: 4, merged: 4):
```
  [ 0] TROUGH price= 3463.00 time= 11-16 09:15 ← A
  [ 1] PEAK   price= 4104.00 time= 12-21 09:15
  [ 2] TROUGH price= 3654.00 time= 12-28 09:15 ← C
  [ 3] PEAK   price= 4013.00 time= 01-11 11:15
```

**失败详情:**
```
  ❌ C4 最新(3620.00) > C(3654.00) = False
```
---

### PG — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 4030.00 time= 03-08 09:15
  [ 1] TROUGH price= 3684.00 time= 04-06 09:15
  [ 2] PEAK   price= 4250.00 time= 05-10 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### PG — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 5117.00 @ 08-30 21:15 |
| B 价 | 5050.00 @ 08-30 22:00 |
| C 价 | 5078.00 @ 08-31 10:00 |
| 最新价 | 5200.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 5022.00 time= 08-19 09:15
  [ 1] PEAK   price= 5103.00 time= 08-19 09:45
  [ 2] TROUGH price= 5032.00 time= 08-19 10:45
  [ 3] PEAK   price= 5092.00 time= 08-19 14:00
  [ 4] TROUGH price= 4970.00 time= 08-19 21:30
  [ 5] PEAK   price= 5022.00 time= 08-19 22:00
  [ 6] TROUGH price= 4950.00 time= 08-19 22:45
  [ 7] PEAK   price= 5002.00 time= 08-20 09:15
  [ 8] TROUGH price= 4933.00 time= 08-20 13:45
  [ 9] PEAK   price= 4980.00 time= 08-20 15:00
  [10] TROUGH price= 4887.00 time= 08-20 21:15
  [11] PEAK   price= 4974.00 time= 08-23 09:15
  [12] TROUGH price= 4905.00 time= 08-23 09:45
  [13] PEAK   price= 5018.00 time= 08-23 11:30
  [14] TROUGH price= 4964.00 time= 08-23 15:00
  [15] PEAK   price= 5063.00 time= 08-23 22:00
  [16] TROUGH price= 4993.00 time= 08-24 09:30
  [17] PEAK   price= 5040.00 time= 08-24 10:15
  [18] TROUGH price= 4961.00 time= 08-24 14:45
  [19] PEAK   price= 5031.00 time= 08-24 22:00
  [20] TROUGH price= 4950.00 time= 08-25 10:45
  [21] PEAK   price= 5024.00 time= 08-25 14:00
  [22] TROUGH price= 4948.00 time= 08-25 22:30
  [23] PEAK   price= 5046.00 time= 08-26 10:15
  [24] TROUGH price= 5002.00 time= 08-26 14:15
  [25] PEAK   price= 5063.00 time= 08-26 21:15
  [26] TROUGH price= 4955.00 time= 08-26 21:30
  [27] PEAK   price= 5138.00 time= 08-27 13:45
  [28] TROUGH price= 5093.00 time= 08-27 14:30
  [29] PEAK   price= 5160.00 time= 08-27 21:15
  [30] TROUGH price= 5105.00 time= 08-27 21:30
  [31] PEAK   price= 5153.00 time= 08-27 22:15
  [32] TROUGH price= 5079.00 time= 08-30 09:15
  [33] PEAK   price= 5136.00 time= 08-30 10:45
  [34] TROUGH price= 5082.00 time= 08-30 11:30
  [35] PEAK   price= 5117.00 time= 08-30 21:15 ← A
  [36] TROUGH price= 5050.00 time= 08-30 22:00
  [37] PEAK   price= 5078.00 time= 08-31 10:00 ← C
  [38] TROUGH price= 5030.00 time= 08-31 14:00
  [39] PEAK   price= 5210.00 time= 09-03 09:30
```

**失败详情:**
```
  ❌ C4 最新(5200.00) < C(5078.00) = False
```
---

### PG — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4514.00 @ 12-30 14:00 |
| B 价 | 5106.00 @ 01-07 14:00 |
| C 价 | 4800.00 @ 01-11 11:15 |
| 最新价 | 4685.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 46 | C 索引 | 48 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 4532.00 time= 11-16 22:00
  [ 1] PEAK   price= 4795.00 time= 11-17 21:15
  [ 2] TROUGH price= 4624.00 time= 11-18 11:00
  [ 3] PEAK   price= 4701.00 time= 11-18 14:00
  [ 4] TROUGH price= 4630.00 time= 11-18 21:15
  [ 5] PEAK   price= 4878.00 time= 11-19 11:00
  [ 6] TROUGH price= 4669.00 time= 11-19 21:15
  [ 7] PEAK   price= 4868.00 time= 11-22 09:15
  [ 8] TROUGH price= 4515.00 time= 11-23 15:00
  [ 9] PEAK   price= 4847.00 time= 11-25 14:00
  [10] TROUGH price= 4490.00 time= 11-26 21:15
  [11] PEAK   price= 4679.00 time= 11-29 09:15
  [12] TROUGH price= 4420.00 time= 11-30 09:15
  [13] PEAK   price= 4511.00 time= 11-30 10:45
  [14] TROUGH price= 4262.00 time= 11-30 21:15
  [15] PEAK   price= 4378.00 time= 12-01 14:00
  [16] TROUGH price= 4225.00 time= 12-01 22:00
  [17] PEAK   price= 4318.00 time= 12-02 13:45
  [18] TROUGH price= 4104.00 time= 12-02 22:00
  [19] PEAK   price= 4228.00 time= 12-03 11:00
  [20] TROUGH price= 4118.00 time= 12-06 10:00
  [21] PEAK   price= 4620.00 time= 12-08 09:15
  [22] TROUGH price= 4473.00 time= 12-08 11:00
  [23] PEAK   price= 4565.00 time= 12-08 21:15
  [24] TROUGH price= 4320.00 time= 12-09 21:15
  [25] PEAK   price= 4413.00 time= 12-10 09:15
  [26] TROUGH price= 4277.00 time= 12-10 14:00
  [27] PEAK   price= 4533.00 time= 12-13 09:15
  [28] TROUGH price= 4391.00 time= 12-13 10:00
  [29] PEAK   price= 4497.00 time= 12-13 21:15
  [30] TROUGH price= 4353.00 time= 12-14 10:00
  [31] PEAK   price= 4453.00 time= 12-14 22:00
  [32] TROUGH price= 4342.00 time= 12-15 11:00
  [33] PEAK   price= 4484.00 time= 12-16 09:15
  [34] TROUGH price= 4425.00 time= 12-16 14:00
  [35] PEAK   price= 4587.00 time= 12-17 09:15
  [36] TROUGH price= 4271.00 time= 12-20 21:15
  [37] PEAK   price= 4476.00 time= 12-22 09:15
  [38] TROUGH price= 4347.00 time= 12-22 21:15
  [39] PEAK   price= 4568.00 time= 12-23 21:15
  [40] TROUGH price= 4478.00 time= 12-24 11:00
  [41] PEAK   price= 4678.00 time= 12-24 21:15
  [42] TROUGH price= 4501.00 time= 12-27 11:00
  [43] PEAK   price= 4720.00 time= 12-28 21:15
  [44] TROUGH price= 4596.00 time= 12-29 13:45
  [45] PEAK   price= 4655.00 time= 12-29 21:15
  [46] TROUGH price= 4514.00 time= 12-30 14:00 ← A
  [47] PEAK   price= 5106.00 time= 01-07 14:00
  [48] TROUGH price= 4800.00 time= 01-11 11:15 ← C
  [49] PEAK   price= 5030.00 time= 01-11 21:15
```

**失败详情:**
```
  ❌ C4 最新(4685.00) > C(4800.00) = False
```
---

### PG — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 5717.00 @ 08-23 22:45 |
| B 价 | 5622.00 @ 08-24 09:15 |
| C 价 | 5708.00 @ 09-01 21:15 |
| 最新价 | 5747.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 15 | C 索引 | 39 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 5341.00 time= 08-18 15:00
  [ 1] PEAK   price= 5389.00 time= 08-18 21:15
  [ 2] TROUGH price= 5343.00 time= 08-18 22:30
  [ 3] PEAK   price= 5411.00 time= 08-18 23:00
  [ 4] TROUGH price= 5360.00 time= 08-19 10:15
  [ 5] PEAK   price= 5413.00 time= 08-19 13:45
  [ 6] TROUGH price= 5382.00 time= 08-19 21:15
  [ 7] PEAK   price= 5478.00 time= 08-19 21:45
  [ 8] TROUGH price= 5391.00 time= 08-22 09:15
  [ 9] PEAK   price= 5495.00 time= 08-22 10:45
  [10] TROUGH price= 5437.00 time= 08-22 14:15
  [11] PEAK   price= 5532.00 time= 08-22 21:15
  [12] TROUGH price= 5446.00 time= 08-22 21:45
  [13] PEAK   price= 5639.00 time= 08-23 09:45
  [14] TROUGH price= 5541.00 time= 08-23 14:45
  [15] PEAK   price= 5717.00 time= 08-23 22:45 ← A
  [16] TROUGH price= 5622.00 time= 08-24 09:15
  [17] PEAK   price= 5755.00 time= 08-24 11:30
  [18] TROUGH price= 5691.00 time= 08-24 21:15
  [19] PEAK   price= 5769.00 time= 08-24 22:15
  [20] TROUGH price= 5707.00 time= 08-24 22:45
  [21] PEAK   price= 5812.00 time= 08-25 09:15
  [22] TROUGH price= 5737.00 time= 08-25 11:30
  [23] PEAK   price= 5794.00 time= 08-25 14:00
  [24] TROUGH price= 5708.00 time= 08-25 21:45
  [25] PEAK   price= 5746.00 time= 08-25 22:45
  [26] TROUGH price= 5697.00 time= 08-26 09:15
  [27] PEAK   price= 5760.00 time= 08-26 11:15
  [28] TROUGH price= 5652.00 time= 08-26 22:15
  [29] PEAK   price= 5785.00 time= 08-29 09:15
  [30] TROUGH price= 5663.00 time= 08-29 21:15
  [31] PEAK   price= 5740.00 time= 08-29 22:15
  [32] TROUGH price= 5687.00 time= 08-30 09:45
  [33] PEAK   price= 5766.00 time= 08-30 11:00
  [34] TROUGH price= 5713.00 time= 08-30 13:45
  [35] PEAK   price= 5785.00 time= 08-30 15:00
  [36] TROUGH price= 5675.00 time= 08-30 22:15
  [37] PEAK   price= 5863.00 time= 08-31 15:00
  [38] TROUGH price= 5620.00 time= 09-01 11:15
  [39] PEAK   price= 5708.00 time= 09-01 21:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(5747.00) < C(5708.00) = False
```
---

### PG — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 5760.00 @ 08-26 11:00 |
| B 价 | 5652.00 @ 08-26 22:00 |
| C 价 | 5708.00 @ 09-01 21:15 |
| 最新价 | 5747.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 48) |
| A 索引 | 39 | C 索引 | 47 |

**极值点序列** (swing: 50, merged: 48):
```
  [ 0] TROUGH price= 5210.00 time= 07-22 21:15
  [ 1] PEAK   price= 5330.00 time= 07-22 23:00
  [ 2] TROUGH price= 5105.00 time= 07-25 14:00
  [ 3] PEAK   price= 5425.00 time= 07-26 21:15
  [ 4] TROUGH price= 5244.00 time= 07-27 10:45
  [ 5] PEAK   price= 5326.00 time= 07-27 13:45
  [ 6] TROUGH price= 5249.00 time= 07-27 22:00
  [ 7] PEAK   price= 5496.00 time= 07-28 11:00
  [ 8] TROUGH price= 5331.00 time= 07-29 14:00
  [ 9] PEAK   price= 5546.00 time= 07-29 23:00
  [10] TROUGH price= 5230.00 time= 08-01 21:15
  [11] PEAK   price= 5319.00 time= 08-02 10:00
  [12] TROUGH price= 5215.00 time= 08-02 11:00
  [13] PEAK   price= 5488.00 time= 08-03 21:15
  [14] TROUGH price= 5094.00 time= 08-05 21:15
  [15] PEAK   price= 5221.00 time= 08-08 10:00
  [16] TROUGH price= 5123.00 time= 08-08 21:15
  [17] PEAK   price= 5244.00 time= 08-09 09:15
  [18] TROUGH price= 5159.00 time= 08-09 11:00
  [19] PEAK   price= 5234.00 time= 08-09 21:15
  [20] TROUGH price= 5118.00 time= 08-10 09:15
  [21] PEAK   price= 5207.00 time= 08-10 11:00
  [22] TROUGH price= 4979.00 time= 08-10 22:00
  [23] PEAK   price= 5302.00 time= 08-12 15:00
  [24] TROUGH price= 5226.00 time= 08-12 22:00
  [25] PEAK   price= 5352.00 time= 08-15 09:15
  [26] TROUGH price= 5219.00 time= 08-15 21:15
  [27] PEAK   price= 5324.00 time= 08-16 09:15
  [28] TROUGH price= 5175.00 time= 08-17 09:15
  [29] PEAK   price= 5495.00 time= 08-22 10:45
  [30] TROUGH price= 5437.00 time= 08-22 14:00
  [31] PEAK   price= 5639.00 time= 08-23 09:15
  [32] TROUGH price= 5541.00 time= 08-23 14:00
  [33] PEAK   price= 5755.00 time= 08-24 11:00
  [34] TROUGH price= 5691.00 time= 08-24 21:15
  [35] PEAK   price= 5812.00 time= 08-25 09:15
  [36] TROUGH price= 5737.00 time= 08-25 11:00
  [37] PEAK   price= 5794.00 time= 08-25 14:00
  [38] TROUGH price= 5697.00 time= 08-26 09:15
  [39] PEAK   price= 5760.00 time= 08-26 11:00 ← A
  [40] TROUGH price= 5652.00 time= 08-26 22:00
  [41] PEAK   price= 5785.00 time= 08-29 09:15
  [42] TROUGH price= 5663.00 time= 08-29 21:15
  [43] PEAK   price= 5785.00 time= 08-30 15:00
  [44] TROUGH price= 5675.00 time= 08-30 22:00
  [45] PEAK   price= 5863.00 time= 08-31 15:00
  [46] TROUGH price= 5620.00 time= 09-01 11:00
  [47] PEAK   price= 5708.00 time= 09-01 21:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(5747.00) < C(5708.00) = False
```
---

### PG — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 4 (merge 后: 4) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 4, merged: 4):
```
  [ 0] TROUGH price= 5001.00 time= 07-11 09:15
  [ 1] PEAK   price= 5546.00 time= 07-25 09:15
  [ 2] TROUGH price= 4979.00 time= 08-08 09:15
  [ 3] PEAK   price= 5863.00 time= 08-29 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### PG — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4532.00 @ 03-24 14:00 |
| B 价 | 4423.00 @ 03-24 21:15 |
| C 价 | 4530.00 @ 05-09 22:00 |
| 最新价 | 4660.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 0 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 4532.00 time= 03-24 14:00 ← A
  [ 1] TROUGH price= 4423.00 time= 03-24 21:15
  [ 2] PEAK   price= 4544.00 time= 03-28 09:15
  [ 3] TROUGH price= 4485.00 time= 03-28 21:15
  [ 4] PEAK   price= 4550.00 time= 03-29 09:15
  [ 5] TROUGH price= 4446.00 time= 03-29 11:00
  [ 6] PEAK   price= 4570.00 time= 03-29 22:00
  [ 7] TROUGH price= 4481.00 time= 03-30 11:00
  [ 8] PEAK   price= 4548.00 time= 03-31 09:15
  [ 9] TROUGH price= 4406.00 time= 03-31 23:00
  [10] PEAK   price= 4653.00 time= 04-03 11:00
  [11] TROUGH price= 4605.00 time= 04-03 14:00
  [12] PEAK   price= 4705.00 time= 04-04 13:45
  [13] TROUGH price= 4594.00 time= 04-06 09:15
  [14] PEAK   price= 4652.00 time= 04-06 21:15
  [15] TROUGH price= 4552.00 time= 04-07 11:00
  [16] PEAK   price= 4642.00 time= 04-07 22:00
  [17] TROUGH price= 4499.00 time= 04-10 14:00
  [18] PEAK   price= 4600.00 time= 04-11 09:15
  [19] TROUGH price= 4559.00 time= 04-11 11:00
  [20] PEAK   price= 4605.00 time= 04-11 14:00
  [21] TROUGH price= 4556.00 time= 04-11 22:00
  [22] PEAK   price= 4787.00 time= 04-13 11:00
  [23] TROUGH price= 4722.00 time= 04-13 22:00
  [24] PEAK   price= 4771.00 time= 04-14 10:00
  [25] TROUGH price= 4682.00 time= 04-17 10:00
  [26] PEAK   price= 4744.00 time= 04-17 14:00
  [27] TROUGH price= 4669.00 time= 04-18 09:15
  [28] PEAK   price= 4755.00 time= 04-18 14:00
  [29] TROUGH price= 4681.00 time= 04-18 21:15
  [30] PEAK   price= 4752.00 time= 04-19 11:00
  [31] TROUGH price= 4607.00 time= 04-20 13:45
  [32] PEAK   price= 4758.00 time= 04-21 22:00
  [33] TROUGH price= 4641.00 time= 04-24 10:00
  [34] PEAK   price= 4824.00 time= 04-24 22:00
  [35] TROUGH price= 4761.00 time= 04-25 11:00
  [36] PEAK   price= 4811.00 time= 04-25 15:00
  [37] TROUGH price= 4738.00 time= 04-25 21:15
  [38] PEAK   price= 4770.00 time= 04-26 10:00
  [39] TROUGH price= 4711.00 time= 04-26 11:00
  [40] PEAK   price= 4835.00 time= 04-28 15:00
  [41] TROUGH price= 4283.00 time= 05-04 23:00
  [42] PEAK   price= 4555.00 time= 05-08 11:00
  [43] TROUGH price= 4339.00 time= 05-08 15:00
  [44] PEAK   price= 4540.00 time= 05-08 22:00
  [45] TROUGH price= 4458.00 time= 05-09 21:45
  [46] PEAK   price= 4530.00 time= 05-09 22:00 ← C
  [47] TROUGH price= 4423.00 time= 05-11 09:15
  [48] PEAK   price= 4494.00 time= 05-11 15:00
  [49] TROUGH price= 4088.00 time= 05-18 21:45
```

**失败详情:**
```
  ❌ C4 最新(4660.00) < C(4530.00) = False
```
---

### PG — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 4297.00 time= 03-13 09:15
  [ 1] PEAK   price= 4835.00 time= 04-24 09:15
  [ 2] TROUGH price= 4088.00 time= 05-15 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### PG — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4950.00 @ 09-01 09:15 |
| B 价 | 4770.00 @ 09-01 21:45 |
| C 价 | 4930.00 @ 09-01 23:00 |
| 最新价 | 5050.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 33 | C 索引 | 35 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 4508.00 time= 08-18 11:30
  [ 1] PEAK   price= 4552.00 time= 08-18 14:30
  [ 2] TROUGH price= 4468.00 time= 08-18 21:15
  [ 3] PEAK   price= 4551.00 time= 08-18 21:45
  [ 4] TROUGH price= 4400.00 time= 08-21 10:00
  [ 5] PEAK   price= 4699.00 time= 08-21 22:45
  [ 6] TROUGH price= 4508.00 time= 08-22 09:45
  [ 7] PEAK   price= 4550.00 time= 08-22 15:00
  [ 8] TROUGH price= 4460.00 time= 08-22 21:15
  [ 9] PEAK   price= 4580.00 time= 08-23 13:45
  [10] TROUGH price= 4479.00 time= 08-23 21:15
  [11] PEAK   price= 4545.00 time= 08-23 21:30
  [12] TROUGH price= 4484.00 time= 08-24 09:45
  [13] PEAK   price= 4528.00 time= 08-24 10:15
  [14] TROUGH price= 4402.00 time= 08-24 21:15
  [15] PEAK   price= 4471.00 time= 08-24 23:00
  [16] TROUGH price= 4402.00 time= 08-25 11:30
  [17] PEAK   price= 4439.00 time= 08-25 14:15
  [18] TROUGH price= 4366.00 time= 08-25 15:00
  [19] PEAK   price= 4472.00 time= 08-25 22:15
  [20] TROUGH price= 4427.00 time= 08-25 23:00
  [21] PEAK   price= 4746.00 time= 08-28 15:00
  [22] TROUGH price= 4570.00 time= 08-28 21:30
  [23] PEAK   price= 4658.00 time= 08-28 22:30
  [24] TROUGH price= 4580.00 time= 08-29 09:30
  [25] PEAK   price= 4634.00 time= 08-29 10:45
  [26] TROUGH price= 4609.00 time= 08-29 14:00
  [27] PEAK   price= 4655.00 time= 08-29 14:15
  [28] TROUGH price= 4611.00 time= 08-29 21:15
  [29] PEAK   price= 4772.00 time= 08-30 11:00
  [30] TROUGH price= 4730.00 time= 08-30 15:00
  [31] PEAK   price= 4884.00 time= 08-30 22:45
  [32] TROUGH price= 4787.00 time= 08-31 10:15
  [33] PEAK   price= 4950.00 time= 09-01 09:15 ← A
  [34] TROUGH price= 4770.00 time= 09-01 21:45
  [35] PEAK   price= 4930.00 time= 09-01 23:00 ← C
  [36] TROUGH price= 4880.00 time= 09-04 11:00
  [37] PEAK   price= 4935.00 time= 09-04 11:15
  [38] TROUGH price= 4800.00 time= 09-05 21:15
  [39] PEAK   price= 5010.00 time= 09-06 13:45
```

**失败详情:**
```
  ❌ C4 最新(5050.00) < C(4930.00) = False
```
---

### PG — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4820.00 @ 12-26 09:15 |
| B 价 | 4930.00 @ 12-27 10:00 |
| C 价 | 4856.00 @ 12-28 09:15 |
| 最新价 | 4413.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 46 | C 索引 | 48 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 4910.00 time= 11-21 15:00
  [ 1] PEAK   price= 4988.00 time= 11-22 09:15
  [ 2] TROUGH price= 4740.00 time= 11-22 21:15
  [ 3] PEAK   price= 4893.00 time= 11-23 10:00
  [ 4] TROUGH price= 4789.00 time= 11-23 14:00
  [ 5] PEAK   price= 4892.00 time= 11-24 10:00
  [ 6] TROUGH price= 4768.00 time= 11-24 21:15
  [ 7] PEAK   price= 4860.00 time= 11-27 09:15
  [ 8] TROUGH price= 4749.00 time= 11-27 11:00
  [ 9] PEAK   price= 4824.00 time= 11-27 14:00
  [10] TROUGH price= 4760.00 time= 11-27 22:00
  [11] PEAK   price= 4826.00 time= 11-28 10:00
  [12] TROUGH price= 4776.00 time= 11-28 11:00
  [13] PEAK   price= 4875.00 time= 11-29 09:15
  [14] TROUGH price= 4732.00 time= 11-30 10:00
  [15] PEAK   price= 4860.00 time= 11-30 22:00
  [16] TROUGH price= 4711.00 time= 12-01 09:15
  [17] PEAK   price= 4760.00 time= 12-01 14:00
  [18] TROUGH price= 4578.00 time= 12-04 10:00
  [19] PEAK   price= 4708.00 time= 12-05 10:45
  [20] TROUGH price= 4625.00 time= 12-05 21:15
  [21] PEAK   price= 4706.00 time= 12-06 14:00
  [22] TROUGH price= 4506.00 time= 12-07 10:00
  [23] PEAK   price= 4901.00 time= 12-08 22:00
  [24] TROUGH price= 4804.00 time= 12-11 10:00
  [25] PEAK   price= 4886.00 time= 12-11 14:00
  [26] TROUGH price= 4721.00 time= 12-11 22:00
  [27] PEAK   price= 4830.00 time= 12-12 13:45
  [28] TROUGH price= 4637.00 time= 12-13 09:15
  [29] PEAK   price= 4830.00 time= 12-14 11:00
  [30] TROUGH price= 4752.00 time= 12-15 10:00
  [31] PEAK   price= 4815.00 time= 12-15 11:00
  [32] TROUGH price= 4654.00 time= 12-18 09:15
  [33] PEAK   price= 4847.00 time= 12-18 22:00
  [34] TROUGH price= 4752.00 time= 12-19 11:00
  [35] PEAK   price= 4857.00 time= 12-20 09:15
  [36] TROUGH price= 4814.00 time= 12-20 10:45
  [37] PEAK   price= 4929.00 time= 12-20 21:15
  [38] TROUGH price= 4826.00 time= 12-21 09:15
  [39] PEAK   price= 4899.00 time= 12-21 13:45
  [40] TROUGH price= 4811.00 time= 12-21 21:15
  [41] PEAK   price= 4945.00 time= 12-22 10:45
  [42] TROUGH price= 4867.00 time= 12-22 14:00
  [43] PEAK   price= 4968.00 time= 12-22 21:15
  [44] TROUGH price= 4853.00 time= 12-25 09:15
  [45] PEAK   price= 4918.00 time= 12-25 21:15
  [46] TROUGH price= 4820.00 time= 12-26 09:15 ← A
  [47] PEAK   price= 4930.00 time= 12-27 10:00
  [48] TROUGH price= 4856.00 time= 12-28 09:15 ← C
  [49] PEAK   price= 4978.00 time= 01-02 09:15
```

**失败详情:**
```
  ❌ C4 最新(4413.00) > C(4856.00) = False
```
---

### PG — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4506.00 @ 12-07 09:15 |
| B 价 | 4901.00 @ 12-08 13:45 |
| C 价 | 4637.00 @ 12-13 09:15 |
| 最新价 | 4413.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 9 | C 索引 | 11 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] PEAK   price= 5194.00 time= 11-01 13:45
  [ 1] TROUGH price= 4988.00 time= 11-08 09:15
  [ 2] PEAK   price= 5283.00 time= 11-09 13:45
  [ 3] TROUGH price= 5116.00 time= 11-13 13:45
  [ 4] PEAK   price= 5232.00 time= 11-15 13:45
  [ 5] TROUGH price= 5014.00 time= 11-17 09:15
  [ 6] PEAK   price= 5199.00 time= 11-20 13:45
  [ 7] TROUGH price= 4740.00 time= 11-22 13:45
  [ 8] PEAK   price= 4875.00 time= 11-29 09:15
  [ 9] TROUGH price= 4506.00 time= 12-07 09:15 ← A
  [10] PEAK   price= 4901.00 time= 12-08 13:45
  [11] TROUGH price= 4637.00 time= 12-13 09:15 ← C
  [12] PEAK   price= 4968.00 time= 12-22 13:45
  [13] TROUGH price= 4820.00 time= 12-26 09:15
  [14] PEAK   price= 4978.00 time= 01-02 09:15
```

**失败详情:**
```
  ❌ C4 最新(4413.00) > C(4637.00) = False
```
---

### PG — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4433.00 @ 11-27 13:45 |
| B 价 | 4371.00 @ 11-28 13:45 |
| C 价 | 4422.00 @ 12-19 13:45 |
| 最新价 | 4698.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 6 | C 索引 | 12 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] PEAK   price= 4460.00 time= 11-04 13:45
  [ 1] TROUGH price= 4261.00 time= 11-06 13:45
  [ 2] PEAK   price= 4419.00 time= 11-14 13:45
  [ 3] TROUGH price= 4208.00 time= 11-18 09:15
  [ 4] PEAK   price= 4475.00 time= 11-20 13:45
  [ 5] TROUGH price= 4376.00 time= 11-26 13:45
  [ 6] PEAK   price= 4433.00 time= 11-27 13:45 ← A
  [ 7] TROUGH price= 4371.00 time= 11-28 13:45
  [ 8] PEAK   price= 4501.00 time= 12-02 13:45
  [ 9] TROUGH price= 4309.00 time= 12-06 13:45
  [10] PEAK   price= 4498.00 time= 12-12 13:45
  [11] TROUGH price= 4372.00 time= 12-13 13:45
  [12] PEAK   price= 4422.00 time= 12-19 13:45 ← C
  [13] TROUGH price= 4333.00 time= 12-20 13:45
  [14] PEAK   price= 4706.00 time= 12-31 10:45
```

**失败详情:**
```
  ❌ C4 最新(4698.00) < C(4422.00) = False
```
---

### PG — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4551.00 @ 04-24 09:30 |
| B 价 | 4695.00 @ 04-29 21:45 |
| C 价 | 4624.00 @ 04-30 09:15 |
| 最新价 | 4600.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 22 | C 索引 | 38 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 4407.00 time= 04-16 13:45
  [ 1] PEAK   price= 4501.00 time= 04-16 22:00
  [ 2] TROUGH price= 4446.00 time= 04-17 09:45
  [ 3] PEAK   price= 4506.00 time= 04-17 14:00
  [ 4] TROUGH price= 4475.00 time= 04-17 15:00
  [ 5] PEAK   price= 4528.00 time= 04-18 09:15
  [ 6] TROUGH price= 4497.00 time= 04-18 11:30
  [ 7] PEAK   price= 4524.00 time= 04-18 14:00
  [ 8] TROUGH price= 4498.00 time= 04-18 21:30
  [ 9] PEAK   price= 4545.00 time= 04-21 11:30
  [10] TROUGH price= 4505.00 time= 04-21 14:15
  [11] PEAK   price= 4537.00 time= 04-21 22:15
  [12] TROUGH price= 4516.00 time= 04-21 22:45
  [13] PEAK   price= 4545.00 time= 04-22 09:15
  [14] TROUGH price= 4518.00 time= 04-22 11:15
  [15] PEAK   price= 4543.00 time= 04-22 21:15
  [16] TROUGH price= 4509.00 time= 04-22 21:45
  [17] PEAK   price= 4579.00 time= 04-23 09:30
  [18] TROUGH price= 4541.00 time= 04-23 11:15
  [19] PEAK   price= 4591.00 time= 04-23 15:00
  [20] TROUGH price= 4553.00 time= 04-23 21:15
  [21] PEAK   price= 4575.00 time= 04-23 22:15
  [22] TROUGH price= 4551.00 time= 04-24 09:30 ← A
  [23] PEAK   price= 4568.00 time= 04-24 10:15
  [24] TROUGH price= 4537.00 time= 04-24 14:00
  [25] PEAK   price= 4560.00 time= 04-24 14:45
  [26] TROUGH price= 4520.00 time= 04-24 22:45
  [27] PEAK   price= 4559.00 time= 04-25 11:15
  [28] TROUGH price= 4512.00 time= 04-25 21:15
  [29] PEAK   price= 4575.00 time= 04-28 09:15
  [30] TROUGH price= 4533.00 time= 04-28 11:00
  [31] PEAK   price= 4556.00 time= 04-28 13:45
  [32] TROUGH price= 4527.00 time= 04-28 21:15
  [33] PEAK   price= 4563.00 time= 04-28 21:30
  [34] TROUGH price= 4547.00 time= 04-28 22:30
  [35] PEAK   price= 4570.00 time= 04-29 10:00
  [36] TROUGH price= 4546.00 time= 04-29 13:45
  [37] PEAK   price= 4695.00 time= 04-29 21:45
  [38] TROUGH price= 4624.00 time= 04-30 09:15 ← C
  [39] PEAK   price= 4800.00 time= 05-06 09:15
```

**失败详情:**
```
  ❌ C4 最新(4600.00) > C(4624.00) = False
```
---

### PG — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4748.00 @ 04-07 09:15 |
| B 价 | 4288.00 @ 04-09 13:45 |
| C 价 | 4591.00 @ 04-23 13:45 |
| 最新价 | 4600.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 12 (merge 后: 12) |
| A 索引 | 8 | C 索引 | 10 |

**极值点序列** (swing: 12, merged: 12):
```
  [ 0] PEAK   price= 4466.00 time= 03-03 13:45
  [ 1] TROUGH price= 4364.00 time= 03-04 13:45
  [ 2] PEAK   price= 4568.00 time= 03-14 10:45
  [ 3] TROUGH price= 4499.00 time= 03-14 13:45
  [ 4] PEAK   price= 4584.00 time= 03-18 13:45
  [ 5] TROUGH price= 4481.00 time= 03-19 13:45
  [ 6] PEAK   price= 4667.00 time= 03-27 09:15
  [ 7] TROUGH price= 4565.00 time= 03-31 09:15
  [ 8] PEAK   price= 4748.00 time= 04-07 09:15 ← A
  [ 9] TROUGH price= 4288.00 time= 04-09 13:45
  [10] PEAK   price= 4591.00 time= 04-23 13:45 ← C
  [11] TROUGH price= 4512.00 time= 04-25 13:45
```

**失败详情:**
```
  ❌ C4 最新(4600.00) < C(4591.00) = False
```
---

### PG — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3902.00 @ 08-27 10:45 |
| B 价 | 3680.00 @ 08-29 13:45 |
| C 价 | 3779.00 @ 09-03 13:45 |
| 最新价 | 3790.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 16 (merge 后: 16) |
| A 索引 | 12 | C 索引 | 14 |

**极值点序列** (swing: 16, merged: 16):
```
  [ 0] PEAK   price= 4119.00 time= 07-10 13:45
  [ 1] TROUGH price= 3972.00 time= 07-17 13:45
  [ 2] PEAK   price= 4054.00 time= 07-21 10:45
  [ 3] TROUGH price= 3930.00 time= 07-22 09:15
  [ 4] PEAK   price= 4067.00 time= 07-25 13:45
  [ 5] TROUGH price= 3953.00 time= 07-28 09:15
  [ 6] PEAK   price= 4115.00 time= 07-30 13:45
  [ 7] TROUGH price= 3768.00 time= 08-08 13:45
  [ 8] PEAK   price= 3895.00 time= 08-15 10:45
  [ 9] TROUGH price= 3812.00 time= 08-18 13:45
  [10] PEAK   price= 3926.00 time= 08-20 13:45
  [11] TROUGH price= 3849.00 time= 08-25 13:45
  [12] PEAK   price= 3902.00 time= 08-27 10:45 ← A
  [13] TROUGH price= 3680.00 time= 08-29 13:45
  [14] PEAK   price= 3779.00 time= 09-03 13:45 ← C
  [15] TROUGH price= 3701.00 time= 09-10 09:15
```

**失败详情:**
```
  ❌ C4 最新(3790.00) < C(3779.00) = False
```
---

### PG — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4226.00 @ 12-17 10:00 |
| B 价 | 4182.00 @ 12-17 21:15 |
| C 价 | 4225.00 @ 01-05 09:15 |
| 最新价 | 4255.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 31 | C 索引 | 47 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 4164.00 time= 11-13 09:15
  [ 1] PEAK   price= 4296.00 time= 11-13 22:00
  [ 2] TROUGH price= 4231.00 time= 11-14 21:15
  [ 3] PEAK   price= 4337.00 time= 11-17 21:15
  [ 4] TROUGH price= 4279.00 time= 11-18 10:00
  [ 5] PEAK   price= 4342.00 time= 11-19 14:00
  [ 6] TROUGH price= 4273.00 time= 11-19 21:15
  [ 7] PEAK   price= 4343.00 time= 11-20 13:45
  [ 8] TROUGH price= 4261.00 time= 11-21 11:00
  [ 9] PEAK   price= 4297.00 time= 11-21 14:00
  [10] TROUGH price= 4190.00 time= 11-21 23:00
  [11] PEAK   price= 4255.00 time= 11-25 09:15
  [12] TROUGH price= 4202.00 time= 11-25 21:15
  [13] PEAK   price= 4307.00 time= 11-26 14:00
  [14] TROUGH price= 4246.00 time= 11-27 11:00
  [15] PEAK   price= 4431.00 time= 11-28 14:00
  [16] TROUGH price= 4321.00 time= 12-01 14:00
  [17] PEAK   price= 4350.00 time= 12-01 21:15
  [18] TROUGH price= 4270.00 time= 12-03 14:00
  [19] PEAK   price= 4336.00 time= 12-04 21:15
  [20] TROUGH price= 4253.00 time= 12-05 10:45
  [21] PEAK   price= 4336.00 time= 12-08 09:15
  [22] TROUGH price= 4175.00 time= 12-09 21:15
  [23] PEAK   price= 4275.00 time= 12-10 09:15
  [24] TROUGH price= 4240.00 time= 12-10 15:00
  [25] PEAK   price= 4307.00 time= 12-11 09:15
  [26] TROUGH price= 4069.00 time= 12-12 14:00
  [27] PEAK   price= 4172.00 time= 12-12 22:00
  [28] TROUGH price= 4169.00 time= 12-15 21:15
  [29] PEAK   price= 4231.00 time= 12-16 11:00
  [30] TROUGH price= 4197.00 time= 12-17 09:15
  [31] PEAK   price= 4226.00 time= 12-17 10:00 ← A
  [32] TROUGH price= 4182.00 time= 12-17 21:15
  [33] PEAK   price= 4240.00 time= 12-18 14:00
  [34] TROUGH price= 4210.00 time= 12-18 21:15
  [35] PEAK   price= 4245.00 time= 12-19 09:15
  [36] TROUGH price= 4195.00 time= 12-19 21:15
  [37] PEAK   price= 4290.00 time= 12-22 21:15
  [38] TROUGH price= 4152.00 time= 12-23 10:00
  [39] PEAK   price= 4326.00 time= 12-25 21:15
  [40] TROUGH price= 4231.00 time= 12-26 10:00
  [41] PEAK   price= 4247.00 time= 12-26 21:15
  [42] TROUGH price= 4149.00 time= 12-29 15:00
  [43] PEAK   price= 4238.00 time= 12-29 21:15
  [44] TROUGH price= 4172.00 time= 12-30 14:00
  [45] PEAK   price= 4235.00 time= 12-30 21:15
  [46] TROUGH price= 4148.00 time= 12-31 14:00
  [47] PEAK   price= 4225.00 time= 01-05 09:15 ← C
  [48] TROUGH price= 4185.00 time= 01-05 14:15
  [49] PEAK   price= 4235.00 time= 01-06 10:00
```

**失败详情:**
```
  ❌ C4 最新(4255.00) < C(4225.00) = False
```
---

### PG — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 6756.00 @ 04-07 09:15 |
| B 价 | 5563.00 @ 04-08 13:45 |
| C 价 | 6025.00 @ 04-13 09:15 |
| 最新价 | 6259.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 8 | C 索引 | 10 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] PEAK   price= 5808.00 time= 03-09 13:45
  [ 1] TROUGH price= 4956.00 time= 03-10 09:15
  [ 2] PEAK   price= 5858.00 time= 03-16 10:45
  [ 3] TROUGH price= 5503.00 time= 03-18 13:45
  [ 4] PEAK   price= 7407.00 time= 03-24 09:15
  [ 5] TROUGH price= 6242.00 time= 03-25 09:15
  [ 6] PEAK   price= 6909.00 time= 03-27 13:45
  [ 7] TROUGH price= 6050.00 time= 04-01 13:45
  [ 8] PEAK   price= 6756.00 time= 04-07 09:15 ← A
  [ 9] TROUGH price= 5563.00 time= 04-08 13:45
  [10] PEAK   price= 6025.00 time= 04-13 09:15 ← C
  [11] TROUGH price= 5640.00 time= 04-15 09:15
  [12] PEAK   price= 5885.00 time= 04-16 09:15
  [13] TROUGH price= 5545.00 time= 04-17 13:45
  [14] PEAK   price= 6017.00 time= 04-24 09:15
```

**失败详情:**
```
  ❌ C4 最新(6259.00) < C(6025.00) = False
```
---

### PG — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4771.00 @ 06-17 13:45 |
| B 价 | 4966.00 @ 06-17 22:00 |
| C 价 | 4921.00 @ 06-17 22:15 |
| 最新价 | 4790.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 24) |
| A 索引 | 20 | C 索引 | 22 |

**极值点序列** (swing: 40, merged: 24):
```
  [ 0] TROUGH price= 5480.00 time= 06-09 23:00
  [ 1] PEAK   price= 5620.00 time= 06-10 10:00
  [ 2] TROUGH price= 5425.00 time= 06-10 13:45
  [ 3] PEAK   price= 5765.00 time= 06-11 09:00
  [ 4] TROUGH price= 5652.00 time= 06-11 09:30
  [ 5] PEAK   price= 5732.00 time= 06-11 11:15
  [ 6] TROUGH price= 5642.00 time= 06-11 13:30
  [ 7] PEAK   price= 5720.00 time= 06-11 21:15
  [ 8] TROUGH price= 5631.00 time= 06-11 21:45
  [ 9] PEAK   price= 5679.00 time= 06-11 22:30
  [10] TROUGH price= 5369.00 time= 06-12 09:45
  [11] PEAK   price= 5455.00 time= 06-12 11:15
  [12] TROUGH price= 5317.00 time= 06-12 13:45
  [13] PEAK   price= 5442.00 time= 06-12 22:45
  [14] TROUGH price= 5105.00 time= 06-15 10:45
  [15] PEAK   price= 5309.00 time= 06-16 09:15
  [16] TROUGH price= 5097.00 time= 06-16 13:45
  [17] PEAK   price= 5165.00 time= 06-16 14:00
  [18] TROUGH price= 4952.00 time= 06-16 21:30
  [19] PEAK   price= 5038.00 time= 06-16 22:00
  [20] TROUGH price= 4771.00 time= 06-17 13:45 ← A
  [21] PEAK   price= 4966.00 time= 06-17 22:00
  [22] TROUGH price= 4921.00 time= 06-17 22:15 ← C
  [23] PEAK   price= 4978.00 time= 06-17 23:00
```

**失败详情:**
```
  ❌ C4 最新(4790.00) > C(4921.00) = False
```
---

### PG — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 5255.00 @ 06-09 09:15 |
| B 价 | 5313.00 @ 06-09 15:00 |
| C 价 | 5310.00 @ 06-11 13:45 |
| 最新价 | 5129.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 41 | C 索引 | 47 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 5176.00 time= 04-22 21:15
  [ 1] TROUGH price= 5092.00 time= 04-23 09:15
  [ 2] PEAK   price= 5455.00 time= 04-24 09:15
  [ 3] TROUGH price= 5277.00 time= 04-24 21:15
  [ 4] PEAK   price= 5683.00 time= 04-28 21:15
  [ 5] TROUGH price= 5533.00 time= 04-28 22:00
  [ 6] PEAK   price= 5725.00 time= 04-30 14:00
  [ 7] TROUGH price= 5552.00 time= 05-06 09:15
  [ 8] PEAK   price= 5758.00 time= 05-06 13:45
  [ 9] TROUGH price= 5344.00 time= 05-07 22:00
  [10] PEAK   price= 5463.00 time= 05-08 09:15
  [11] TROUGH price= 5352.00 time= 05-08 14:00
  [12] PEAK   price= 5830.00 time= 05-12 21:15
  [13] TROUGH price= 5756.00 time= 05-13 09:15
  [14] PEAK   price= 5823.00 time= 05-13 10:45
  [15] TROUGH price= 5702.00 time= 05-13 14:00
  [16] PEAK   price= 5798.00 time= 05-13 21:15
  [17] TROUGH price= 5560.00 time= 05-14 15:00
  [18] PEAK   price= 5806.00 time= 05-15 14:00
  [19] TROUGH price= 5734.00 time= 05-15 22:00
  [20] PEAK   price= 5902.00 time= 05-18 09:15
  [21] TROUGH price= 5744.00 time= 05-18 21:15
  [22] PEAK   price= 5936.00 time= 05-19 21:15
  [23] TROUGH price= 5673.00 time= 05-21 14:00
  [24] PEAK   price= 5748.00 time= 05-21 21:15
  [25] TROUGH price= 5322.00 time= 05-25 11:00
  [26] PEAK   price= 5390.00 time= 05-25 21:15
  [27] TROUGH price= 5330.00 time= 05-26 11:00
  [28] PEAK   price= 5422.00 time= 05-26 22:00
  [29] TROUGH price= 5102.00 time= 05-27 21:15
  [30] PEAK   price= 5279.00 time= 05-28 21:15
  [31] TROUGH price= 5147.00 time= 05-29 22:00
  [32] PEAK   price= 5360.00 time= 06-01 10:00
  [33] TROUGH price= 5292.00 time= 06-01 14:00
  [34] PEAK   price= 5514.00 time= 06-02 09:15
  [35] TROUGH price= 5326.00 time= 06-02 13:45
  [36] PEAK   price= 5513.00 time= 06-03 14:00
  [37] TROUGH price= 5149.00 time= 06-04 22:00
  [38] PEAK   price= 5402.00 time= 06-05 11:00
  [39] TROUGH price= 5242.00 time= 06-05 22:00
  [40] PEAK   price= 5560.00 time= 06-08 14:00
  [41] TROUGH price= 5255.00 time= 06-09 09:15 ← A
  [42] PEAK   price= 5313.00 time= 06-09 15:00
  [43] TROUGH price= 5179.00 time= 06-09 22:00
  [44] PEAK   price= 5290.00 time= 06-10 10:00
  [45] TROUGH price= 5138.00 time= 06-10 14:00
  [46] PEAK   price= 5406.00 time= 06-11 09:15
  [47] TROUGH price= 5310.00 time= 06-11 13:45 ← C
  [48] PEAK   price= 5381.00 time= 06-11 21:15
  [49] TROUGH price= 5042.00 time= 06-12 13:45
```

**失败详情:**
```
  ❌ C4 最新(5129.00) > C(5310.00) = False
```
---

### PR — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 5844.00 @ 08-12 00:00 |
| B 价 | 9282.00 @ 03-10 00:00 |
| C 价 | 7690.00 @ 04-07 00:00 |
| 最新价 | 7088.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 20 (merge 后: 19) |
| A 索引 | 12 | C 索引 | 16 |

**极值点序列** (swing: 20, merged: 19):
```
  [ 0] TROUGH price= 5736.00 time= 09-10 00:00
  [ 1] PEAK   price= 6820.00 time= 10-08 00:00
  [ 2] TROUGH price= 6052.00 time= 12-03 00:00
  [ 3] PEAK   price= 6540.00 time= 01-14 00:00
  [ 4] TROUGH price= 6180.00 time= 02-05 00:00
  [ 5] PEAK   price= 6452.00 time= 02-11 00:00
  [ 6] TROUGH price= 5272.00 time= 04-08 00:00
  [ 7] PEAK   price= 6220.00 time= 05-13 00:00
  [ 8] TROUGH price= 5762.00 time= 06-10 00:00
  [ 9] PEAK   price= 6262.00 time= 06-17 00:00
  [10] TROUGH price= 5836.00 time= 07-01 00:00
  [11] PEAK   price= 6140.00 time= 07-22 00:00
  [12] TROUGH price= 5844.00 time= 08-12 00:00 ← A
  [13] PEAK   price= 6104.00 time= 08-26 00:00
  [14] TROUGH price= 5486.00 time= 10-21 00:00
  [15] PEAK   price= 9282.00 time= 03-10 00:00
  [16] TROUGH price= 7690.00 time= 04-07 00:00 ← C
  [17] PEAK   price= 9018.00 time= 04-28 00:00
  [18] TROUGH price= 7416.00 time= 06-02 00:00
```

**失败详情:**
```
  ❌ C4 最新(7088.00) > C(7690.00) = False
```
---

### PS — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 34375.00 @ 05-06 00:00 |
| B 价 | 39340.00 @ 05-13 00:00 |
| C 价 | 36020.00 @ 05-12 00:00 |
| 最新价 | 35840.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 19 (merge 后: 19) |
| A 索引 | 3 | C 索引 | 17 |

**极值点序列** (swing: 19, merged: 19):
```
  [ 0] PEAK   price=45190.00 time= 01-14 00:00
  [ 1] TROUGH price=42820.00 time= 02-05 00:00
  [ 2] PEAK   price=44795.00 time= 02-25 00:00
  [ 3] TROUGH price=34375.00 time= 05-06 00:00 ← A
  [ 4] PEAK   price=39340.00 time= 05-13 00:00
  [ 5] TROUGH price=30400.00 time= 06-24 00:00
  [ 6] PEAK   price=55605.00 time= 07-22 00:00
  [ 7] TROUGH price=48220.00 time= 08-26 00:00
  [ 8] PEAK   price=56790.00 time= 09-09 00:00
  [ 9] TROUGH price=47720.00 time= 10-09 00:00
  [10] PEAK   price=56655.00 time= 10-28 00:00
  [11] TROUGH price=51150.00 time= 11-11 00:00
  [12] PEAK   price=59200.00 time= 11-25 00:00
  [13] TROUGH price=52625.00 time= 12-09 00:00
  [14] PEAK   price=61985.00 time= 12-16 00:00
  [15] TROUGH price=31070.00 time= 04-07 00:00
  [16] PEAK   price=46345.00 time= 04-21 00:00
  [17] TROUGH price=36020.00 time= 05-12 00:00 ← C
  [18] PEAK   price=39030.00 time= 06-09 00:00
```

**失败详情:**
```
  ❌ C4 最新(35840.00) > C(36020.00) = False
```
---

### RB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3760.00 @ 01-09 14:45 |
| B 价 | 3795.00 @ 01-09 21:45 |
| C 价 | 3789.00 @ 01-09 23:00 |
| 最新价 | 3770.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 34 | C 索引 | 36 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 3718.00 time= 12-24 11:30
  [ 1] PEAK   price= 3728.00 time= 12-24 14:00
  [ 2] TROUGH price= 3715.00 time= 12-24 22:45
  [ 3] PEAK   price= 3729.00 time= 12-25 11:00
  [ 4] TROUGH price= 3683.00 time= 12-25 23:00
  [ 5] PEAK   price= 3741.00 time= 12-26 11:30
  [ 6] TROUGH price= 3726.00 time= 12-26 21:15
  [ 7] PEAK   price= 3765.00 time= 12-27 21:15
  [ 8] TROUGH price= 3745.00 time= 12-27 21:45
  [ 9] PEAK   price= 3791.00 time= 12-30 10:15
  [10] TROUGH price= 3778.00 time= 12-30 11:15
  [11] PEAK   price= 3789.00 time= 12-30 13:45
  [12] TROUGH price= 3778.00 time= 12-30 14:30
  [13] PEAK   price= 3800.00 time= 12-31 09:15
  [14] TROUGH price= 3741.00 time= 01-02 15:00
  [15] PEAK   price= 3752.00 time= 01-02 21:45
  [16] TROUGH price= 3739.00 time= 01-02 22:00
  [17] PEAK   price= 3752.00 time= 01-03 11:15
  [18] TROUGH price= 3748.00 time= 01-03 15:00
  [19] PEAK   price= 3766.00 time= 01-03 22:30
  [20] TROUGH price= 3749.00 time= 01-06 11:00
  [21] PEAK   price= 3757.00 time= 01-06 13:45
  [22] TROUGH price= 3747.00 time= 01-06 21:15
  [23] PEAK   price= 3750.00 time= 01-07 09:30
  [24] TROUGH price= 3743.00 time= 01-07 11:00
  [25] PEAK   price= 3752.00 time= 01-07 14:00
  [26] TROUGH price= 3747.00 time= 01-07 14:45
  [27] PEAK   price= 3767.00 time= 01-08 09:45
  [28] TROUGH price= 3754.00 time= 01-08 13:45
  [29] PEAK   price= 3762.00 time= 01-08 14:15
  [30] TROUGH price= 3755.00 time= 01-08 23:00
  [31] PEAK   price= 3769.00 time= 01-09 09:30
  [32] TROUGH price= 3765.00 time= 01-09 10:15
  [33] PEAK   price= 3778.00 time= 01-09 11:15
  [34] TROUGH price= 3760.00 time= 01-09 14:45 ← A
  [35] PEAK   price= 3795.00 time= 01-09 21:45
  [36] TROUGH price= 3789.00 time= 01-09 23:00 ← C
  [37] PEAK   price= 3886.00 time= 01-10 14:15
  [38] TROUGH price= 3778.00 time= 01-13 14:15
  [39] PEAK   price= 3990.00 time= 01-15 09:45
```

**失败详情:**
```
  ❌ C4 最新(3770.00) > C(3789.00) = False
```
---

### RB — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3635.00 @ 10-13 11:00 |
| B 价 | 3611.00 @ 10-14 09:15 |
| C 价 | 3630.00 @ 10-14 10:45 |
| 最新价 | 3645.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 44 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 3796.00 time= 08-27 09:15
  [ 1] TROUGH price= 3761.00 time= 08-27 21:15
  [ 2] PEAK   price= 3829.00 time= 08-31 09:15
  [ 3] TROUGH price= 3802.00 time= 09-01 11:00
  [ 4] PEAK   price= 3817.00 time= 09-01 21:15
  [ 5] TROUGH price= 3786.00 time= 09-01 22:00
  [ 6] PEAK   price= 3839.00 time= 09-03 09:15
  [ 7] TROUGH price= 3788.00 time= 09-04 09:15
  [ 8] PEAK   price= 3806.00 time= 09-04 11:00
  [ 9] TROUGH price= 3795.00 time= 09-04 13:45
  [10] PEAK   price= 3813.00 time= 09-04 21:15
  [11] TROUGH price= 3792.00 time= 09-07 10:00
  [12] PEAK   price= 3807.00 time= 09-07 13:45
  [13] TROUGH price= 3787.00 time= 09-07 14:00
  [14] PEAK   price= 3810.00 time= 09-08 09:15
  [15] TROUGH price= 3755.00 time= 09-08 21:15
  [16] PEAK   price= 3784.00 time= 09-09 09:15
  [17] TROUGH price= 3722.00 time= 09-09 15:00
  [18] PEAK   price= 3760.00 time= 09-10 09:15
  [19] TROUGH price= 3714.00 time= 09-10 14:00
  [20] PEAK   price= 3771.00 time= 09-11 21:15
  [21] TROUGH price= 3733.00 time= 09-14 14:00
  [22] PEAK   price= 3757.00 time= 09-14 21:15
  [23] TROUGH price= 3652.00 time= 09-17 09:15
  [24] PEAK   price= 3672.00 time= 09-17 10:45
  [25] TROUGH price= 3646.00 time= 09-17 14:00
  [26] PEAK   price= 3686.00 time= 09-18 09:15
  [27] TROUGH price= 3580.00 time= 09-21 22:00
  [28] PEAK   price= 3622.00 time= 09-22 10:00
  [29] TROUGH price= 3612.00 time= 09-22 13:45
  [30] PEAK   price= 3640.00 time= 09-22 21:15
  [31] TROUGH price= 3592.00 time= 09-23 14:00
  [32] PEAK   price= 3637.00 time= 09-23 21:15
  [33] TROUGH price= 3617.00 time= 09-24 09:15
  [34] PEAK   price= 3639.00 time= 09-24 14:00
  [35] TROUGH price= 3620.00 time= 09-24 21:15
  [36] PEAK   price= 3635.00 time= 09-25 13:45
  [37] TROUGH price= 3596.00 time= 09-25 21:15
  [38] PEAK   price= 3632.00 time= 09-28 11:00
  [39] TROUGH price= 3605.00 time= 09-28 22:00
  [40] PEAK   price= 3628.00 time= 09-29 21:15
  [41] TROUGH price= 3591.00 time= 09-30 14:00
  [42] PEAK   price= 3650.00 time= 10-09 09:15
  [43] TROUGH price= 3595.00 time= 10-13 09:15
  [44] PEAK   price= 3635.00 time= 10-13 11:00 ← A
  [45] TROUGH price= 3611.00 time= 10-14 09:15
  [46] PEAK   price= 3630.00 time= 10-14 10:45 ← C
  [47] TROUGH price= 3615.00 time= 10-14 13:45
  [48] PEAK   price= 3630.00 time= 10-14 21:15
  [49] TROUGH price= 3610.00 time= 10-15 13:45
```

**失败详情:**
```
  ❌ C4 最新(3645.00) < C(3630.00) = False
```
---

### RB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4221.00 @ 01-11 15:00 |
| B 价 | 4148.00 @ 01-11 22:45 |
| C 价 | 4175.00 @ 01-13 15:00 |
| 最新价 | 4192.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 33 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 4156.00 time= 12-25 09:15
  [ 1] PEAK   price= 4255.00 time= 12-25 11:15
  [ 2] TROUGH price= 4210.00 time= 12-25 13:45
  [ 3] PEAK   price= 4279.00 time= 12-25 21:45
  [ 4] TROUGH price= 4196.00 time= 12-28 10:45
  [ 5] PEAK   price= 4225.00 time= 12-28 11:30
  [ 6] TROUGH price= 4178.00 time= 12-28 21:30
  [ 7] PEAK   price= 4221.00 time= 12-28 22:30
  [ 8] TROUGH price= 4169.00 time= 12-29 10:15
  [ 9] PEAK   price= 4184.00 time= 12-29 13:45
  [10] TROUGH price= 4155.00 time= 12-29 14:45
  [11] PEAK   price= 4180.00 time= 12-29 21:15
  [12] TROUGH price= 4111.00 time= 12-29 22:00
  [13] PEAK   price= 4190.00 time= 12-29 23:00
  [14] TROUGH price= 4162.00 time= 12-30 10:15
  [15] PEAK   price= 4229.00 time= 12-30 21:15
  [16] TROUGH price= 4181.00 time= 12-30 23:00
  [17] PEAK   price= 4270.00 time= 12-31 10:45
  [18] TROUGH price= 4211.00 time= 12-31 13:45
  [19] PEAK   price= 4300.00 time= 01-04 09:15
  [20] TROUGH price= 4180.00 time= 01-04 10:45
  [21] PEAK   price= 4249.00 time= 01-04 21:30
  [22] TROUGH price= 4220.00 time= 01-05 11:15
  [23] PEAK   price= 4279.00 time= 01-05 21:30
  [24] TROUGH price= 4209.00 time= 01-06 11:00
  [25] PEAK   price= 4240.00 time= 01-06 21:30
  [26] TROUGH price= 4215.00 time= 01-06 22:45
  [27] PEAK   price= 4249.00 time= 01-07 10:00
  [28] TROUGH price= 4240.00 time= 01-07 13:45
  [29] PEAK   price= 4298.00 time= 01-08 14:45
  [30] TROUGH price= 4213.00 time= 01-11 09:15
  [31] PEAK   price= 4260.00 time= 01-11 10:45
  [32] TROUGH price= 4187.00 time= 01-11 14:45
  [33] PEAK   price= 4221.00 time= 01-11 15:00 ← A
  [34] TROUGH price= 4148.00 time= 01-11 22:45
  [35] PEAK   price= 4223.00 time= 01-12 14:15
  [36] TROUGH price= 4132.00 time= 01-13 14:30
  [37] PEAK   price= 4175.00 time= 01-13 15:00 ← C
  [38] TROUGH price= 4160.00 time= 01-14 22:30
  [39] PEAK   price= 4260.00 time= 01-15 09:45
```

**失败详情:**
```
  ❌ C4 最新(4192.00) < C(4175.00) = False
```
---

### RB — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4221.00 @ 12-28 22:00 |
| B 价 | 4111.00 @ 12-29 22:00 |
| C 价 | 4175.00 @ 01-13 15:00 |
| 最新价 | 4192.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 49) |
| A 索引 | 34 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 49):
```
  [ 0] PEAK   price= 3928.00 time= 11-17 21:15
  [ 1] TROUGH price= 3886.00 time= 11-18 10:45
  [ 2] PEAK   price= 3956.00 time= 11-19 11:00
  [ 3] TROUGH price= 3926.00 time= 11-19 14:00
  [ 4] PEAK   price= 4005.00 time= 11-20 23:00
  [ 5] TROUGH price= 3896.00 time= 11-23 21:15
  [ 6] PEAK   price= 3924.00 time= 11-24 09:15
  [ 7] TROUGH price= 3858.00 time= 11-25 21:15
  [ 8] PEAK   price= 3954.00 time= 11-26 22:00
  [ 9] TROUGH price= 3919.00 time= 11-27 11:00
  [10] PEAK   price= 3937.00 time= 11-27 21:15
  [11] TROUGH price= 3890.00 time= 11-30 09:15
  [12] PEAK   price= 3944.00 time= 11-30 10:45
  [13] TROUGH price= 3872.00 time= 11-30 23:00
  [14] PEAK   price= 3939.00 time= 12-02 09:15
  [15] TROUGH price= 3886.00 time= 12-02 21:15
  [16] PEAK   price= 3914.00 time= 12-03 11:00
  [17] TROUGH price= 3832.00 time= 12-03 22:00
  [18] PEAK   price= 4002.00 time= 12-07 21:15
  [19] TROUGH price= 3942.00 time= 12-08 21:15
  [20] PEAK   price= 4298.00 time= 12-11 10:00
  [21] TROUGH price= 4071.00 time= 12-14 21:15
  [22] PEAK   price= 4229.00 time= 12-15 21:15
  [23] TROUGH price= 4183.00 time= 12-16 14:00
  [24] PEAK   price= 4282.00 time= 12-17 11:00
  [25] TROUGH price= 4230.00 time= 12-17 14:00
  [26] PEAK   price= 4544.00 time= 12-21 09:15
  [27] TROUGH price= 4452.00 time= 12-21 21:15
  [28] PEAK   price= 4678.00 time= 12-22 09:15
  [29] TROUGH price= 4242.00 time= 12-23 21:15
  [30] PEAK   price= 4268.00 time= 12-24 14:00
  [31] TROUGH price= 4156.00 time= 12-25 09:15
  [32] PEAK   price= 4279.00 time= 12-25 21:15
  [33] TROUGH price= 4178.00 time= 12-28 21:15
  [34] PEAK   price= 4221.00 time= 12-28 22:00 ← A
  [35] TROUGH price= 4111.00 time= 12-29 22:00
  [36] PEAK   price= 4300.00 time= 01-04 09:15
  [37] TROUGH price= 4180.00 time= 01-04 10:45
  [38] PEAK   price= 4249.00 time= 01-04 21:15
  [39] TROUGH price= 4220.00 time= 01-05 11:15
  [40] PEAK   price= 4279.00 time= 01-05 21:15
  [41] TROUGH price= 4209.00 time= 01-06 11:00
  [42] PEAK   price= 4298.00 time= 01-08 14:00
  [43] TROUGH price= 4148.00 time= 01-11 22:00
  [44] PEAK   price= 4223.00 time= 01-12 14:00
  [45] TROUGH price= 4132.00 time= 01-13 14:30
  [46] PEAK   price= 4175.00 time= 01-13 15:00 ← C
  [47] TROUGH price= 4160.00 time= 01-14 22:00
  [48] PEAK   price= 4260.00 time= 01-15 09:15
```

**失败详情:**
```
  ❌ C4 最新(4192.00) < C(4175.00) = False
```
---

### RB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4676.00 @ 12-07 13:45 |
| B 价 | 4494.00 @ 12-09 13:45 |
| C 价 | 4597.00 @ 12-29 13:45 |
| 最新价 | 4650.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 4 | C 索引 | 10 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] PEAK   price= 4466.00 time= 11-11 13:45
  [ 1] TROUGH price= 4108.00 time= 11-16 13:45
  [ 2] PEAK   price= 4535.00 time= 11-24 13:45
  [ 3] TROUGH price= 4295.00 time= 11-26 13:45
  [ 4] PEAK   price= 4676.00 time= 12-07 13:45 ← A
  [ 5] TROUGH price= 4494.00 time= 12-09 13:45
  [ 6] PEAK   price= 4726.00 time= 12-20 09:15
  [ 7] TROUGH price= 4623.00 time= 12-22 10:45
  [ 8] PEAK   price= 4705.00 time= 12-24 09:15
  [ 9] TROUGH price= 4518.00 time= 12-27 13:45
  [10] PEAK   price= 4597.00 time= 12-29 13:45 ← C
  [11] TROUGH price= 4499.00 time= 01-04 09:15
  [12] PEAK   price= 4675.00 time= 01-06 13:45
  [13] TROUGH price= 4495.00 time= 01-10 13:45
  [14] PEAK   price= 4710.00 time= 01-13 09:45
```

**失败详情:**
```
  ❌ C4 最新(4650.00) < C(4597.00) = False
```
---

### RB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 5053.00 @ 05-11 15:00 |
| B 价 | 5010.00 @ 05-12 14:30 |
| C 价 | 5025.00 @ 05-13 09:15 |
| 最新价 | 5070.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 36 | C 索引 | 38 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 5165.00 time= 04-21 22:30
  [ 1] TROUGH price= 5112.00 time= 04-22 10:00
  [ 2] PEAK   price= 5143.00 time= 04-22 10:45
  [ 3] TROUGH price= 5115.00 time= 04-22 11:15
  [ 4] PEAK   price= 5138.00 time= 04-22 14:00
  [ 5] TROUGH price= 5105.00 time= 04-22 21:15
  [ 6] PEAK   price= 5143.00 time= 04-22 21:30
  [ 7] TROUGH price= 4986.00 time= 04-25 10:45
  [ 8] PEAK   price= 5047.00 time= 04-25 11:30
  [ 9] TROUGH price= 4971.00 time= 04-25 22:30
  [10] PEAK   price= 5062.00 time= 04-26 11:30
  [11] TROUGH price= 5025.00 time= 04-26 14:45
  [12] PEAK   price= 5075.00 time= 04-26 21:15
  [13] TROUGH price= 5040.00 time= 04-26 22:45
  [14] PEAK   price= 5070.00 time= 04-27 09:15
  [15] TROUGH price= 5030.00 time= 04-27 14:15
  [16] PEAK   price= 5080.00 time= 04-27 21:15
  [17] TROUGH price= 5025.00 time= 04-27 22:30
  [18] PEAK   price= 5072.00 time= 04-28 09:30
  [19] TROUGH price= 5035.00 time= 04-28 13:45
  [20] PEAK   price= 5179.00 time= 04-29 10:15
  [21] TROUGH price= 5170.00 time= 04-29 15:00
  [22] PEAK   price= 5212.00 time= 05-05 09:15
  [23] TROUGH price= 5193.00 time= 05-05 10:45
  [24] PEAK   price= 5223.00 time= 05-05 21:15
  [25] TROUGH price= 5150.00 time= 05-06 09:45
  [26] PEAK   price= 5181.00 time= 05-06 11:00
  [27] TROUGH price= 5051.00 time= 05-06 21:15
  [28] PEAK   price= 5139.00 time= 05-09 14:15
  [29] TROUGH price= 5087.00 time= 05-09 21:15
  [30] PEAK   price= 5116.00 time= 05-09 22:15
  [31] TROUGH price= 5055.00 time= 05-10 09:15
  [32] PEAK   price= 5110.00 time= 05-10 10:45
  [33] TROUGH price= 5020.00 time= 05-10 23:00
  [34] PEAK   price= 5047.00 time= 05-11 10:15
  [35] TROUGH price= 5040.00 time= 05-11 11:30
  [36] PEAK   price= 5053.00 time= 05-11 15:00 ← A
  [37] TROUGH price= 5010.00 time= 05-12 14:30
  [38] PEAK   price= 5025.00 time= 05-13 09:15 ← C
  [39] TROUGH price= 4980.00 time= 05-13 11:30
```

**失败详情:**
```
  ❌ C4 最新(5070.00) < C(5025.00) = False
```
---

### RB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3822.00 @ 09-02 10:45 |
| B 价 | 3993.00 @ 09-13 09:15 |
| C 价 | 3836.00 @ 09-21 09:15 |
| 最新价 | 3730.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 10 (merge 后: 10) |
| A 索引 | 5 | C 索引 | 7 |

**极值点序列** (swing: 10, merged: 10):
```
  [ 0] PEAK   price= 4155.00 time= 08-08 13:45
  [ 1] TROUGH price= 4033.00 time= 08-10 13:45
  [ 2] PEAK   price= 4199.00 time= 08-15 09:15
  [ 3] TROUGH price= 3924.00 time= 08-19 13:45
  [ 4] PEAK   price= 4125.00 time= 08-26 13:45
  [ 5] TROUGH price= 3822.00 time= 09-02 10:45 ← A
  [ 6] PEAK   price= 3993.00 time= 09-13 09:15
  [ 7] TROUGH price= 3836.00 time= 09-21 09:15 ← C
  [ 8] PEAK   price= 3990.00 time= 09-29 13:45
  [ 9] TROUGH price= 3780.00 time= 10-12 13:45
```

**失败详情:**
```
  ❌ C4 最新(3730.00) > C(3836.00) = False
```
---

### RB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 4360.00 @ 01-13 13:45 |
| B 价 | 4261.00 @ 01-16 10:00 |
| C 价 | 4320.00 @ 01-16 11:30 |
| 最新价 | 4320.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 37 | C 索引 | 39 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 3968.00 time= 12-23 14:45
  [ 1] PEAK   price= 4004.00 time= 12-23 21:15
  [ 2] TROUGH price= 3947.00 time= 12-26 09:15
  [ 3] PEAK   price= 4020.00 time= 12-26 21:45
  [ 4] TROUGH price= 3990.00 time= 12-26 22:00
  [ 5] PEAK   price= 4061.00 time= 12-27 10:15
  [ 6] TROUGH price= 4014.00 time= 12-27 11:15
  [ 7] PEAK   price= 4051.00 time= 12-27 13:45
  [ 8] TROUGH price= 4032.00 time= 12-27 14:30
  [ 9] PEAK   price= 4058.00 time= 12-27 21:45
  [10] TROUGH price= 4011.00 time= 12-28 09:15
  [11] PEAK   price= 4045.00 time= 12-28 11:30
  [12] TROUGH price= 4026.00 time= 12-28 14:15
  [13] PEAK   price= 4063.00 time= 12-28 21:15
  [14] TROUGH price= 4006.00 time= 12-28 21:45
  [15] PEAK   price= 4030.00 time= 12-29 09:15
  [16] TROUGH price= 4012.00 time= 12-29 10:15
  [17] PEAK   price= 4150.00 time= 12-30 15:00
  [18] TROUGH price= 4051.00 time= 01-03 09:15
  [19] PEAK   price= 4082.00 time= 01-03 10:45
  [20] TROUGH price= 4083.00 time= 01-03 15:00
  [21] PEAK   price= 4108.00 time= 01-03 21:30
  [22] TROUGH price= 4045.00 time= 01-04 13:45
  [23] PEAK   price= 4060.00 time= 01-04 21:15
  [24] TROUGH price= 4017.00 time= 01-05 09:15
  [25] PEAK   price= 4053.00 time= 01-05 11:00
  [26] TROUGH price= 4025.00 time= 01-05 11:30
  [27] PEAK   price= 4146.00 time= 01-06 22:15
  [28] TROUGH price= 4105.00 time= 01-09 09:30
  [29] PEAK   price= 4130.00 time= 01-09 10:45
  [30] TROUGH price= 4107.00 time= 01-09 11:30
  [31] PEAK   price= 4153.00 time= 01-09 21:30
  [32] TROUGH price= 4122.00 time= 01-09 23:00
  [33] PEAK   price= 4175.00 time= 01-10 15:00
  [34] TROUGH price= 4141.00 time= 01-10 21:15
  [35] PEAK   price= 4322.00 time= 01-11 14:45
  [36] TROUGH price= 4220.00 time= 01-11 22:45
  [37] PEAK   price= 4360.00 time= 01-13 13:45 ← A
  [38] TROUGH price= 4261.00 time= 01-16 10:00
  [39] PEAK   price= 4320.00 time= 01-16 11:30 ← C
```

**失败详情:**
```
  ❌ C4 最新(4320.00) < C(4320.00) = False
```
---

### RB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3524.00 @ 10-12 11:30 |
| B 价 | 3482.00 @ 10-12 14:45 |
| C 价 | 3520.00 @ 10-12 21:30 |
| 最新价 | 3530.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 33 | C 索引 | 35 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 3750.00 time= 09-20 10:45
  [ 1] PEAK   price= 3764.00 time= 09-20 13:45
  [ 2] TROUGH price= 3752.00 time= 09-20 14:00
  [ 3] PEAK   price= 3769.00 time= 09-20 21:15
  [ 4] TROUGH price= 3739.00 time= 09-21 09:15
  [ 5] PEAK   price= 3752.00 time= 09-21 09:30
  [ 6] TROUGH price= 3687.00 time= 09-21 21:15
  [ 7] PEAK   price= 3713.00 time= 09-21 21:30
  [ 8] TROUGH price= 3696.00 time= 09-22 09:30
  [ 9] PEAK   price= 3716.00 time= 09-22 13:45
  [10] TROUGH price= 3697.00 time= 09-22 14:00
  [11] PEAK   price= 3725.00 time= 09-22 14:45
  [12] TROUGH price= 3696.00 time= 09-22 21:15
  [13] PEAK   price= 3712.00 time= 09-25 09:15
  [14] TROUGH price= 3659.00 time= 09-25 10:45
  [15] PEAK   price= 3668.00 time= 09-25 21:15
  [16] TROUGH price= 3640.00 time= 09-25 21:45
  [17] PEAK   price= 3658.00 time= 09-26 09:30
  [18] TROUGH price= 3605.00 time= 09-26 14:15
  [19] PEAK   price= 3627.00 time= 09-26 21:15
  [20] TROUGH price= 3612.00 time= 09-27 09:30
  [21] PEAK   price= 3627.00 time= 09-27 10:45
  [22] TROUGH price= 3607.00 time= 09-27 15:00
  [23] PEAK   price= 3643.00 time= 09-28 09:15
  [24] TROUGH price= 3606.00 time= 09-28 11:15
  [25] PEAK   price= 3631.00 time= 09-28 14:45
  [26] TROUGH price= 3560.00 time= 10-09 10:45
  [27] PEAK   price= 3581.00 time= 10-09 23:00
  [28] TROUGH price= 3541.00 time= 10-10 14:30
  [29] PEAK   price= 3573.00 time= 10-10 21:15
  [30] TROUGH price= 3498.00 time= 10-11 14:45
  [31] PEAK   price= 3527.00 time= 10-11 23:00
  [32] TROUGH price= 3501.00 time= 10-12 10:45
  [33] PEAK   price= 3524.00 time= 10-12 11:30 ← A
  [34] TROUGH price= 3482.00 time= 10-12 14:45
  [35] PEAK   price= 3520.00 time= 10-12 21:30 ← C
  [36] TROUGH price= 3490.00 time= 10-13 09:15
  [37] PEAK   price= 3520.00 time= 10-13 14:30
  [38] TROUGH price= 3490.00 time= 10-13 22:00
  [39] PEAK   price= 3530.00 time= 10-16 11:30
```

**失败详情:**
```
  ❌ C4 最新(3530.00) < C(3520.00) = False
```
---

### RB — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3524.00 @ 10-12 11:00 |
| B 价 | 3482.00 @ 10-12 14:00 |
| C 价 | 3520.00 @ 10-12 21:30 |
| 最新价 | 3530.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 44 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 3703.00 time= 08-29 13:45
  [ 1] TROUGH price= 3672.00 time= 08-29 21:15
  [ 2] PEAK   price= 3704.00 time= 08-30 09:15
  [ 3] TROUGH price= 3677.00 time= 08-30 11:00
  [ 4] PEAK   price= 3746.00 time= 08-31 09:15
  [ 5] TROUGH price= 3719.00 time= 08-31 14:00
  [ 6] PEAK   price= 3795.00 time= 09-01 23:00
  [ 7] TROUGH price= 3741.00 time= 09-04 21:15
  [ 8] PEAK   price= 3778.00 time= 09-05 11:00
  [ 9] TROUGH price= 3732.00 time= 09-05 14:00
  [10] PEAK   price= 3755.00 time= 09-05 23:00
  [11] TROUGH price= 3731.00 time= 09-06 10:00
  [12] PEAK   price= 3758.00 time= 09-06 21:15
  [13] TROUGH price= 3720.00 time= 09-07 11:00
  [14] PEAK   price= 3747.00 time= 09-07 14:00
  [15] TROUGH price= 3674.00 time= 09-08 21:15
  [16] PEAK   price= 3740.00 time= 09-11 21:15
  [17] TROUGH price= 3723.00 time= 09-12 10:00
  [18] PEAK   price= 3746.00 time= 09-12 21:15
  [19] TROUGH price= 3696.00 time= 09-13 14:00
  [20] PEAK   price= 3731.00 time= 09-13 21:15
  [21] TROUGH price= 3711.00 time= 09-14 10:45
  [22] PEAK   price= 3764.00 time= 09-15 15:00
  [23] TROUGH price= 3733.00 time= 09-15 22:00
  [24] PEAK   price= 3790.00 time= 09-19 09:15
  [25] TROUGH price= 3761.00 time= 09-19 11:00
  [26] PEAK   price= 3776.00 time= 09-19 15:00
  [27] TROUGH price= 3755.00 time= 09-19 21:15
  [28] PEAK   price= 3773.00 time= 09-20 09:15
  [29] TROUGH price= 3750.00 time= 09-20 10:45
  [30] PEAK   price= 3769.00 time= 09-20 21:15
  [31] TROUGH price= 3687.00 time= 09-21 21:15
  [32] PEAK   price= 3725.00 time= 09-22 14:00
  [33] TROUGH price= 3605.00 time= 09-26 14:00
  [34] PEAK   price= 3627.00 time= 09-27 10:45
  [35] TROUGH price= 3607.00 time= 09-27 15:00
  [36] PEAK   price= 3643.00 time= 09-28 09:15
  [37] TROUGH price= 3606.00 time= 09-28 11:00
  [38] PEAK   price= 3631.00 time= 09-28 14:00
  [39] TROUGH price= 3560.00 time= 10-09 10:45
  [40] PEAK   price= 3581.00 time= 10-09 23:00
  [41] TROUGH price= 3541.00 time= 10-10 14:00
  [42] PEAK   price= 3573.00 time= 10-10 21:15
  [43] TROUGH price= 3498.00 time= 10-11 14:00
  [44] PEAK   price= 3524.00 time= 10-12 11:00 ← A
  [45] TROUGH price= 3482.00 time= 10-12 14:00
  [46] PEAK   price= 3520.00 time= 10-12 21:30 ← C
  [47] TROUGH price= 3490.00 time= 10-13 09:15
  [48] PEAK   price= 3520.00 time= 10-13 14:00
  [49] TROUGH price= 3490.00 time= 10-13 22:00
```

**失败详情:**
```
  ❌ C4 最新(3530.00) < C(3520.00) = False
```
---

### RB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 3630.00 time= 08-14 09:15
  [ 1] PEAK   price= 3795.00 time= 08-28 09:15
  [ 2] TROUGH price= 3482.00 time= 10-09 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### RB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3943.00 @ 01-09 14:00 |
| B 价 | 3931.00 @ 01-09 15:00 |
| C 价 | 3938.00 @ 01-11 21:30 |
| 最新价 | 3946.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 30 | C 索引 | 36 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 4061.00 time= 12-26 14:30
  [ 1] TROUGH price= 4039.00 time= 12-26 21:15
  [ 2] PEAK   price= 4052.00 time= 12-26 22:30
  [ 3] TROUGH price= 4023.00 time= 12-26 23:00
  [ 4] PEAK   price= 4061.00 time= 12-27 21:15
  [ 5] TROUGH price= 4043.00 time= 12-27 22:45
  [ 6] PEAK   price= 4058.00 time= 12-28 09:30
  [ 7] TROUGH price= 4043.00 time= 12-28 13:45
  [ 8] PEAK   price= 4053.00 time= 12-28 14:15
  [ 9] TROUGH price= 4033.00 time= 12-28 14:45
  [10] PEAK   price= 4057.00 time= 12-28 23:00
  [11] TROUGH price= 4040.00 time= 12-29 10:45
  [12] PEAK   price= 4063.00 time= 12-29 11:30
  [13] TROUGH price= 3980.00 time= 12-29 15:00
  [14] PEAK   price= 4048.00 time= 01-02 10:45
  [15] TROUGH price= 4034.00 time= 01-02 13:45
  [16] PEAK   price= 4050.00 time= 01-02 22:30
  [17] TROUGH price= 4039.00 time= 01-03 09:30
  [18] PEAK   price= 4050.00 time= 01-03 10:00
  [19] TROUGH price= 4033.00 time= 01-03 21:15
  [20] PEAK   price= 4046.00 time= 01-04 09:45
  [21] TROUGH price= 4015.00 time= 01-04 13:45
  [22] PEAK   price= 4035.00 time= 01-04 14:30
  [23] TROUGH price= 4010.00 time= 01-04 22:15
  [24] PEAK   price= 4027.00 time= 01-04 23:00
  [25] TROUGH price= 3957.00 time= 01-05 21:30
  [26] PEAK   price= 3990.00 time= 01-08 09:15
  [27] TROUGH price= 3937.00 time= 01-08 13:45
  [28] PEAK   price= 3967.00 time= 01-08 14:15
  [29] TROUGH price= 3938.00 time= 01-09 10:15
  [30] PEAK   price= 3943.00 time= 01-09 14:00 ← A
  [31] TROUGH price= 3931.00 time= 01-09 15:00
  [32] PEAK   price= 3950.00 time= 01-09 22:15
  [33] TROUGH price= 3880.00 time= 01-10 15:00
  [34] PEAK   price= 3915.00 time= 01-11 09:45
  [35] TROUGH price= 3905.00 time= 01-11 10:15
  [36] PEAK   price= 3938.00 time= 01-11 21:30 ← C
  [37] TROUGH price= 3900.00 time= 01-12 10:00
  [38] PEAK   price= 3942.00 time= 01-12 21:45
  [39] TROUGH price= 3870.00 time= 01-15 10:45
```

**失败详情:**
```
  ❌ C4 最新(3946.00) < C(3938.00) = False
```
---

### RB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 4052.00 time= 11-20 09:15
  [ 1] TROUGH price= 3854.00 time= 12-04 09:15
  [ 2] PEAK   price= 4063.00 time= 12-25 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### RB — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3320.00 @ 10-11 21:15 |
| B 价 | 3440.00 @ 10-14 13:45 |
| C 价 | 3388.00 @ 10-14 21:30 |
| 最新价 | 3381.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 36 | C 索引 | 38 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 3063.00 time= 09-18 13:45
  [ 1] PEAK   price= 3106.00 time= 09-18 14:45
  [ 2] TROUGH price= 3074.00 time= 09-18 21:15
  [ 3] PEAK   price= 3128.00 time= 09-19 09:15
  [ 4] TROUGH price= 3068.00 time= 09-19 10:00
  [ 5] PEAK   price= 3165.00 time= 09-19 21:30
  [ 6] TROUGH price= 3110.00 time= 09-20 10:15
  [ 7] PEAK   price= 3138.00 time= 09-20 10:45
  [ 8] TROUGH price= 3029.00 time= 09-23 21:15
  [ 9] PEAK   price= 3049.00 time= 09-23 22:15
  [10] TROUGH price= 3030.00 time= 09-23 22:45
  [11] PEAK   price= 3107.00 time= 09-24 09:15
  [12] TROUGH price= 3060.00 time= 09-24 10:45
  [13] PEAK   price= 3205.00 time= 09-25 09:15
  [14] TROUGH price= 3120.00 time= 09-25 21:15
  [15] PEAK   price= 3162.00 time= 09-25 22:45
  [16] TROUGH price= 3139.00 time= 09-25 23:00
  [17] PEAK   price= 3165.00 time= 09-26 10:45
  [18] TROUGH price= 3138.00 time= 09-26 11:15
  [19] PEAK   price= 3210.00 time= 09-26 21:15
  [20] TROUGH price= 3178.00 time= 09-26 22:00
  [21] PEAK   price= 3206.00 time= 09-27 09:30
  [22] TROUGH price= 3182.00 time= 09-27 10:45
  [23] PEAK   price= 3212.00 time= 09-27 11:30
  [24] TROUGH price= 3180.00 time= 09-27 14:00
  [25] PEAK   price= 3659.00 time= 10-08 10:45
  [26] TROUGH price= 3315.00 time= 10-08 14:00
  [27] PEAK   price= 3440.00 time= 10-08 21:15
  [28] TROUGH price= 3390.00 time= 10-09 11:30
  [29] PEAK   price= 3450.00 time= 10-09 13:45
  [30] TROUGH price= 3313.00 time= 10-09 21:15
  [31] PEAK   price= 3412.00 time= 10-10 09:15
  [32] TROUGH price= 3390.00 time= 10-10 10:00
  [33] PEAK   price= 3425.00 time= 10-10 13:45
  [34] TROUGH price= 3371.00 time= 10-10 15:00
  [35] PEAK   price= 3380.00 time= 10-11 15:00
  [36] TROUGH price= 3320.00 time= 10-11 21:15 ← A
  [37] PEAK   price= 3440.00 time= 10-14 13:45
  [38] TROUGH price= 3388.00 time= 10-14 21:30 ← C
  [39] PEAK   price= 3440.00 time= 10-15 14:00
```

**失败详情:**
```
  ❌ C4 最新(3381.00) > C(3388.00) = False
```
---

### RB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 4 (merge 后: 4) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 4, merged: 4):
```
  [ 0] TROUGH price= 3044.00 time= 08-12 09:15
  [ 1] PEAK   price= 3289.00 time= 08-26 09:15
  [ 2] TROUGH price= 2921.00 time= 09-09 09:15
  [ 3] PEAK   price= 3659.00 time= 10-08 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### RB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3080.00 @ 04-25 13:45 |
| B 价 | 3025.00 @ 04-30 13:45 |
| C 价 | 3074.00 @ 05-07 09:15 |
| 最新价 | 3075.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 18 (merge 后: 18) |
| A 索引 | 13 | C 索引 | 15 |

**极值点序列** (swing: 18, merged: 18):
```
  [ 0] TROUGH price= 3186.00 time= 03-11 09:15
  [ 1] PEAK   price= 3274.00 time= 03-14 13:45
  [ 2] TROUGH price= 3134.00 time= 03-20 09:15
  [ 3] PEAK   price= 3228.00 time= 03-26 09:15
  [ 4] TROUGH price= 3132.00 time= 04-01 09:15
  [ 5] PEAK   price= 3190.00 time= 04-03 09:15
  [ 6] TROUGH price= 2962.00 time= 04-09 09:15
  [ 7] PEAK   price= 3069.00 time= 04-10 13:45
  [ 8] TROUGH price= 3000.00 time= 04-18 13:45
  [ 9] PEAK   price= 3042.00 time= 04-21 13:45
  [10] TROUGH price= 3000.00 time= 04-22 13:45
  [11] PEAK   price= 3066.00 time= 04-23 13:45
  [12] TROUGH price= 3019.00 time= 04-24 13:45
  [13] PEAK   price= 3080.00 time= 04-25 13:45 ← A
  [14] TROUGH price= 3025.00 time= 04-30 13:45
  [15] PEAK   price= 3074.00 time= 05-07 09:15 ← C
  [16] TROUGH price= 2976.00 time= 05-09 13:45
  [17] PEAK   price= 3062.00 time= 05-12 13:45
```

**失败详情:**
```
  ❌ C4 最新(3075.00) < C(3074.00) = False
```
---

### RB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 2991.00 time= 09-08 09:15
  [ 1] PEAK   price= 3107.00 time= 09-22 09:15
  [ 2] TROUGH price= 2972.00 time= 09-29 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### RB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3160.00 @ 12-01 09:15 |
| B 价 | 3056.00 @ 12-08 09:15 |
| C 价 | 3147.00 @ 12-22 09:15 |
| 最新价 | 3165.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 4 (merge 后: 4) |
| A 索引 | 0 | C 索引 | 2 |

**极值点序列** (swing: 4, merged: 4):
```
  [ 0] PEAK   price= 3160.00 time= 12-01 09:15 ← A
  [ 1] TROUGH price= 3056.00 time= 12-08 09:15
  [ 2] PEAK   price= 3147.00 time= 12-22 09:15 ← C
  [ 3] TROUGH price= 3050.00 time= 01-05 09:15
```

**失败详情:**
```
  ❌ C4 最新(3165.00) < C(3147.00) = False
```
---

### RB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 3167.00 time= 03-16 09:15
  [ 1] TROUGH price= 3061.00 time= 04-07 09:15
  [ 2] PEAK   price= 3195.00 time= 05-11 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### RB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2949.00 @ 03-23 08:00 |
| B 价 | 3278.00 @ 05-04 08:00 |
| C 价 | 3119.00 @ 06-08 09:15 |
| 最新价 | 3099.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 9 (merge 后: 6) |
| A 索引 | 1 | C 索引 | 3 |

**极值点序列** (swing: 9, merged: 6):
```
  [ 0] PEAK   price= 3189.00 time= 03-16 08:00
  [ 1] TROUGH price= 2949.00 time= 03-23 08:00 ← A
  [ 2] PEAK   price= 3278.00 time= 05-04 08:00
  [ 3] TROUGH price= 3119.00 time= 06-08 09:15 ← C
  [ 4] PEAK   price= 3195.00 time= 06-11 13:30
  [ 5] TROUGH price= 3089.00 time= 06-15 09:15
```

**失败详情:**
```
  ❌ C4 最新(3099.00) > C(3119.00) = False
```
---

### RM — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 2289.00 @ 06-17 09:30 |
| B 价 | 2281.00 @ 06-17 10:45 |
| C 价 | 2284.00 @ 06-18 09:15 |
| 最新价 | 2286.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 29) |
| A 索引 | 23 | C 索引 | 27 |

**极值点序列** (swing: 40, merged: 29):
```
  [ 0] TROUGH price= 2230.00 time= 06-10 13:45
  [ 1] PEAK   price= 2249.00 time= 06-10 22:00
  [ 2] TROUGH price= 2228.00 time= 06-11 09:30
  [ 3] PEAK   price= 2261.00 time= 06-11 21:30
  [ 4] TROUGH price= 2248.00 time= 06-12 09:00
  [ 5] PEAK   price= 2258.00 time= 06-12 09:45
  [ 6] TROUGH price= 2248.00 time= 06-12 10:15
  [ 7] PEAK   price= 2258.00 time= 06-12 11:00
  [ 8] TROUGH price= 2249.00 time= 06-12 13:45
  [ 9] PEAK   price= 2260.00 time= 06-12 14:30
  [10] TROUGH price= 2252.00 time= 06-12 21:00
  [11] PEAK   price= 2275.00 time= 06-12 22:00
  [12] TROUGH price= 2255.00 time= 06-15 09:15
  [13] PEAK   price= 2276.00 time= 06-15 10:00
  [14] TROUGH price= 2256.00 time= 06-15 11:30
  [15] PEAK   price= 2268.00 time= 06-15 14:15
  [16] TROUGH price= 2255.00 time= 06-15 21:15
  [17] PEAK   price= 2273.00 time= 06-15 23:00
  [18] TROUGH price= 2263.00 time= 06-16 09:15
  [19] PEAK   price= 2278.00 time= 06-16 11:15
  [20] TROUGH price= 2273.00 time= 06-16 21:15
  [21] PEAK   price= 2291.00 time= 06-16 22:00
  [22] TROUGH price= 2277.00 time= 06-16 22:45
  [23] PEAK   price= 2289.00 time= 06-17 09:30 ← A
  [24] TROUGH price= 2281.00 time= 06-17 10:45
  [25] PEAK   price= 2289.00 time= 06-17 11:00
  [26] TROUGH price= 2265.00 time= 06-17 21:30
  [27] PEAK   price= 2284.00 time= 06-18 09:15 ← C
  [28] TROUGH price= 2267.00 time= 06-18 10:45
```

**失败详情:**
```
  ❌ C4 最新(2286.00) < C(2284.00) = False
```
---

### RR — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3610.00 @ 12-15 00:00 |
| B 价 | 3541.00 @ 02-02 00:00 |
| C 价 | 3591.00 @ 05-29 00:00 |
| 最新价 | 3603.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 60 (merge 后: 60) |
| A 索引 | 45 | C 索引 | 57 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] TROUGH price= 3448.00 time= 10-19 00:00
  [ 1] PEAK   price= 3630.00 time= 10-31 00:00
  [ 2] TROUGH price= 3508.00 time= 11-13 00:00
  [ 3] PEAK   price= 3584.00 time= 11-16 00:00
  [ 4] TROUGH price= 3471.00 time= 12-06 00:00
  [ 5] PEAK   price= 3553.00 time= 12-15 00:00
  [ 6] TROUGH price= 3490.00 time= 12-19 00:00
  [ 7] PEAK   price= 3555.00 time= 12-28 00:00
  [ 8] TROUGH price= 3492.00 time= 01-02 00:00
  [ 9] PEAK   price= 3571.00 time= 01-10 00:00
  [10] TROUGH price= 3492.00 time= 01-22 00:00
  [11] PEAK   price= 3590.00 time= 02-19 00:00
  [12] TROUGH price= 3418.00 time= 03-18 00:00
  [13] PEAK   price= 3629.00 time= 04-11 00:00
  [14] TROUGH price= 3556.00 time= 04-19 00:00
  [15] PEAK   price= 3625.00 time= 04-29 00:00
  [16] TROUGH price= 3461.00 time= 06-18 00:00
  [17] PEAK   price= 3529.00 time= 07-02 00:00
  [18] TROUGH price= 3450.00 time= 07-30 00:00
  [19] PEAK   price= 3543.00 time= 08-07 00:00
  [20] TROUGH price= 3432.00 time= 09-03 00:00
  [21] PEAK   price= 3528.00 time= 09-05 00:00
  [22] TROUGH price= 3463.00 time= 09-11 00:00
  [23] PEAK   price= 3504.00 time= 09-25 00:00
  [24] TROUGH price= 3454.00 time= 10-11 00:00
  [25] PEAK   price= 3562.00 time= 10-28 00:00
  [26] TROUGH price= 3417.00 time= 12-06 00:00
  [27] PEAK   price= 3515.00 time= 12-18 00:00
  [28] TROUGH price= 3396.00 time= 12-27 00:00
  [29] PEAK   price= 3598.00 time= 02-18 00:00
  [30] TROUGH price= 3470.00 time= 03-21 00:00
  [31] PEAK   price= 3694.00 time= 06-03 00:00
  [32] TROUGH price= 3562.00 time= 06-25 00:00
  [33] PEAK   price= 3607.00 time= 07-04 00:00
  [34] TROUGH price= 3584.00 time= 07-10 00:00
  [35] PEAK   price= 3636.00 time= 07-21 00:00
  [36] TROUGH price= 3600.00 time= 08-19 00:00
  [37] PEAK   price= 3618.00 time= 09-08 00:00
  [38] TROUGH price= 3595.00 time= 09-12 00:00
  [39] PEAK   price= 3627.00 time= 09-30 00:00
  [40] TROUGH price= 3561.00 time= 10-31 00:00
  [41] PEAK   price= 3597.00 time= 11-05 00:00
  [42] TROUGH price= 3569.00 time= 11-10 00:00
  [43] PEAK   price= 3601.00 time= 11-14 00:00
  [44] TROUGH price= 3577.00 time= 11-18 00:00
  [45] PEAK   price= 3610.00 time= 12-15 00:00 ← A
  [46] TROUGH price= 3593.00 time= 12-24 00:00
  [47] PEAK   price= 3668.00 time= 01-15 00:00
  [48] TROUGH price= 3541.00 time= 02-02 00:00
  [49] PEAK   price= 3672.00 time= 03-09 00:00
  [50] TROUGH price= 3543.00 time= 03-24 00:00
  [51] PEAK   price= 3737.00 time= 03-25 00:00
  [52] TROUGH price= 3552.00 time= 04-08 00:00
  [53] PEAK   price= 3613.00 time= 04-13 00:00
  [54] TROUGH price= 3560.00 time= 04-21 00:00
  [55] PEAK   price= 3634.00 time= 05-07 00:00
  [56] TROUGH price= 3536.00 time= 05-27 00:00
  [57] PEAK   price= 3591.00 time= 05-29 00:00 ← C
  [58] TROUGH price= 3523.00 time= 06-05 00:00
  [59] PEAK   price= 3618.00 time= 06-08 00:00
```

**失败详情:**
```
  ❌ C4 最新(3603.00) < C(3591.00) = False
```
---

### SA — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 1146.00 @ 02-24 00:00 |
| B 价 | 1330.00 @ 03-03 00:00 |
| C 价 | 1175.00 @ 05-19 00:00 |
| 最新价 | 1152.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 69 (merge 后: 69) |
| A 索引 | 63 | C 索引 | 67 |

**极值点序列** (swing: 69, merged: 69):
```
  [ 0] PEAK   price= 1691.00 time= 01-14 00:00
  [ 1] TROUGH price= 1509.00 time= 02-03 00:00
  [ 2] PEAK   price= 1637.00 time= 02-25 00:00
  [ 3] TROUGH price= 1322.00 time= 04-14 00:00
  [ 4] PEAK   price= 1490.00 time= 06-02 00:00
  [ 5] TROUGH price= 1288.00 time= 07-21 00:00
  [ 6] PEAK   price= 1822.00 time= 09-01 00:00
  [ 7] TROUGH price= 1655.00 time= 09-15 00:00
  [ 8] PEAK   price= 1749.00 time= 10-13 00:00
  [ 9] TROUGH price= 1317.00 time= 12-08 00:00
  [10] PEAK   price= 1682.00 time= 12-22 00:00
  [11] TROUGH price= 1489.00 time= 01-12 00:00
  [12] PEAK   price= 2010.00 time= 03-16 00:00
  [13] TROUGH price= 1818.00 time= 04-06 00:00
  [14] PEAK   price= 2329.00 time= 05-11 00:00
  [15] TROUGH price= 2028.00 time= 05-18 00:00
  [16] PEAK   price= 2320.00 time= 06-01 00:00
  [17] TROUGH price= 2130.00 time= 06-15 00:00
  [18] PEAK   price= 3648.00 time= 10-12 00:00
  [19] TROUGH price= 2160.00 time= 01-04 00:00
  [20] PEAK   price= 3177.00 time= 02-08 00:00
  [21] TROUGH price= 2396.00 time= 03-15 00:00
  [22] PEAK   price= 3269.00 time= 04-19 00:00
  [23] TROUGH price= 2700.00 time= 05-10 00:00
  [24] PEAK   price= 3165.00 time= 06-07 00:00
  [25] TROUGH price= 2402.00 time= 07-12 00:00
  [26] PEAK   price= 2678.00 time= 07-26 00:00
  [27] TROUGH price= 2223.00 time= 08-16 00:00
  [28] PEAK   price= 2443.00 time= 08-23 00:00
  [29] TROUGH price= 2244.00 time= 09-06 00:00
  [30] PEAK   price= 2558.00 time= 10-10 00:00
  [31] TROUGH price= 2282.00 time= 10-25 00:00
  [32] PEAK   price= 3069.00 time= 01-30 00:00
  [33] TROUGH price= 2845.00 time= 02-07 00:00
  [34] PEAK   price= 2994.00 time= 02-21 00:00
  [35] TROUGH price= 1550.00 time= 05-23 00:00
  [36] PEAK   price= 2207.00 time= 07-25 00:00
  [37] TROUGH price= 1508.00 time= 08-08 00:00
  [38] PEAK   price= 2074.00 time= 08-29 00:00
  [39] TROUGH price= 1652.00 time= 10-24 00:00
  [40] PEAK   price= 2666.00 time= 11-28 00:00
  [41] TROUGH price= 1808.00 time= 01-09 00:00
  [42] PEAK   price= 2166.00 time= 01-23 00:00
  [43] TROUGH price= 1751.00 time= 02-27 00:00
  [44] PEAK   price= 1969.00 time= 03-05 00:00
  [45] TROUGH price= 1727.00 time= 03-26 00:00
  [46] PEAK   price= 2320.00 time= 04-23 00:00
  [47] TROUGH price= 2091.00 time= 05-14 00:00
  [48] PEAK   price= 2471.00 time= 05-21 00:00
  [49] TROUGH price= 1317.00 time= 09-18 00:00
  [50] PEAK   price= 1754.00 time= 10-08 00:00
  [51] TROUGH price= 1393.00 time= 12-03 00:00
  [52] PEAK   price= 1530.00 time= 12-10 00:00
  [53] TROUGH price= 1379.00 time= 01-07 00:00
  [54] PEAK   price= 1585.00 time= 02-25 00:00
  [55] TROUGH price= 1266.00 time= 04-08 00:00
  [56] PEAK   price= 1392.00 time= 04-22 00:00
  [57] TROUGH price= 1147.00 time= 06-24 00:00
  [58] PEAK   price= 1457.00 time= 07-22 00:00
  [59] TROUGH price= 1252.00 time= 09-09 00:00
  [60] PEAK   price= 1352.00 time= 09-16 00:00
  [61] TROUGH price= 1088.00 time= 12-09 00:00
  [62] PEAK   price= 1277.00 time= 01-06 00:00
  [63] TROUGH price= 1146.00 time= 02-24 00:00 ← A
  [64] PEAK   price= 1330.00 time= 03-03 00:00
  [65] TROUGH price= 1123.00 time= 04-07 00:00
  [66] PEAK   price= 1274.00 time= 05-06 00:00
  [67] TROUGH price= 1175.00 time= 05-19 00:00 ← C
  [68] PEAK   price= 1234.00 time= 05-26 00:00
```

**失败详情:**
```
  ❌ C4 最新(1152.00) > C(1175.00) = False
```
---

### SC — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 431.80 @ 10-21 00:00 |
| B 价 | 838.40 @ 03-17 00:00 |
| C 价 | 592.00 @ 04-14 00:00 |
| 最新价 | 572.20 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 80 (merge 后: 80) |
| A 索引 | 74 | C 索引 | 78 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price=  397.70 time= 04-03 00:00
  [ 1] PEAK   price=  493.80 time= 05-22 00:00
  [ 2] TROUGH price=  453.70 time= 06-19 00:00
  [ 3] PEAK   price=  511.50 time= 07-10 00:00
  [ 4] TROUGH price=  478.50 time= 07-17 00:00
  [ 5] PEAK   price=  550.00 time= 08-07 00:00
  [ 6] TROUGH price=  480.00 time= 08-14 00:00
  [ 7] PEAK   price=  598.50 time= 10-09 00:00
  [ 8] TROUGH price=  351.60 time= 12-25 00:00
  [ 9] PEAK   price=  442.20 time= 01-22 00:00
  [10] TROUGH price=  413.00 time= 01-29 00:00
  [11] PEAK   price=  467.90 time= 02-12 00:00
  [12] TROUGH price=  426.20 time= 03-05 00:00
  [13] PEAK   price=  521.50 time= 05-14 00:00
  [14] TROUGH price=  406.00 time= 06-18 00:00
  [15] PEAK   price=  462.20 time= 07-09 00:00
  [16] TROUGH price=  399.60 time= 08-06 00:00
  [17] PEAK   price=  496.00 time= 09-17 00:00
  [18] TROUGH price=  431.50 time= 10-08 00:00
  [19] PEAK   price=  529.80 time= 01-07 00:00
  [20] TROUGH price=  381.40 time= 02-04 00:00
  [21] PEAK   price=  422.00 time= 02-18 00:00
  [22] TROUGH price=  213.20 time= 03-17 00:00
  [23] PEAK   price=  304.90 time= 04-07 00:00
  [24] TROUGH price=  205.10 time= 04-28 00:00
  [25] PEAK   price=  305.70 time= 07-21 00:00
  [26] TROUGH price=  277.10 time= 08-04 00:00
  [27] PEAK   price=  299.90 time= 08-25 00:00
  [28] TROUGH price=  242.70 time= 09-08 00:00
  [29] PEAK   price=  277.30 time= 10-13 00:00
  [30] TROUGH price=  215.00 time= 10-27 00:00
  [31] PEAK   price=  444.60 time= 03-02 00:00
  [32] TROUGH price=  372.70 time= 03-23 00:00
  [33] PEAK   price=  479.00 time= 07-06 00:00
  [34] TROUGH price=  395.20 time= 08-17 00:00
  [35] PEAK   price=  546.50 time= 10-12 00:00
  [36] TROUGH price=  417.50 time= 11-30 00:00
  [37] PEAK   price=  823.60 time= 03-08 00:00
  [38] TROUGH price=  602.40 time= 04-06 00:00
  [39] PEAK   price=  787.20 time= 06-14 00:00
  [40] TROUGH price=  621.00 time= 07-12 00:00
  [41] PEAK   price=  752.40 time= 08-23 00:00
  [42] TROUGH price=  602.30 time= 09-27 00:00
  [43] PEAK   price=  709.50 time= 10-11 00:00
  [44] TROUGH price=  655.70 time= 10-18 00:00
  [45] PEAK   price=  722.50 time= 11-01 00:00
  [46] TROUGH price=  495.00 time= 12-06 00:00
  [47] PEAK   price=  571.60 time= 12-27 00:00
  [48] TROUGH price=  513.80 time= 02-07 00:00
  [49] PEAK   price=  589.70 time= 03-07 00:00
  [50] TROUGH price=  480.60 time= 03-14 00:00
  [51] PEAK   price=  606.50 time= 04-11 00:00
  [52] TROUGH price=  485.30 time= 05-04 00:00
  [53] PEAK   price=  758.00 time= 09-12 00:00
  [54] TROUGH price=  643.90 time= 10-10 00:00
  [55] PEAK   price=  700.70 time= 10-17 00:00
  [56] TROUGH price=  519.70 time= 12-12 00:00
  [57] PEAK   price=  599.50 time= 01-23 00:00
  [58] TROUGH price=  551.40 time= 02-06 00:00
  [59] PEAK   price=  682.80 time= 04-09 00:00
  [60] TROUGH price=  566.50 time= 06-04 00:00
  [61] PEAK   price=  641.10 time= 07-02 00:00
  [62] TROUGH price=  492.20 time= 09-10 00:00
  [63] PEAK   price=  587.50 time= 10-08 00:00
  [64] TROUGH price=  510.60 time= 10-29 00:00
  [65] PEAK   price=  639.50 time= 01-14 00:00
  [66] TROUGH price=  502.30 time= 03-04 00:00
  [67] PEAK   price=  558.50 time= 04-01 00:00
  [68] TROUGH price=  444.00 time= 04-08 00:00
  [69] PEAK   price=  506.00 time= 04-22 00:00
  [70] TROUGH price=  447.50 time= 05-27 00:00
  [71] PEAK   price=  588.60 time= 06-17 00:00
  [72] TROUGH price=  468.80 time= 09-02 00:00
  [73] PEAK   price=  502.50 time= 09-16 00:00
  [74] TROUGH price=  431.80 time= 10-21 00:00 ← A
  [75] PEAK   price=  472.20 time= 11-11 00:00
  [76] TROUGH price=  411.00 time= 01-06 00:00
  [77] PEAK   price=  838.40 time= 03-17 00:00
  [78] TROUGH price=  592.00 time= 04-14 00:00 ← C
  [79] PEAK   price=  695.70 time= 04-28 00:00
```

**失败详情:**
```
  ❌ C4 最新(572.20) > C(592.00) = False
```
---

### SC — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 411.00 @ 01-06 00:00 |
| B 价 | 823.00 @ 03-16 09:30 |
| C 价 | 585.20 @ 04-13 09:30 |
| 最新价 | 550.90 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 64 (merge 后: 64) |
| A 索引 | 59 | C 索引 | 61 |

**极值点序列** (swing: 64, merged: 64):
```
  [ 0] PEAK   price=  496.00 time= 09-17 00:00
  [ 1] TROUGH price=  431.50 time= 10-08 00:00
  [ 2] PEAK   price=  529.80 time= 01-07 00:00
  [ 3] TROUGH price=  381.40 time= 02-04 00:00
  [ 4] PEAK   price=  422.00 time= 02-18 00:00
  [ 5] TROUGH price=  213.20 time= 03-17 00:00
  [ 6] PEAK   price=  304.90 time= 04-07 00:00
  [ 7] TROUGH price=  205.10 time= 04-28 00:00
  [ 8] PEAK   price=  305.70 time= 07-21 00:00
  [ 9] TROUGH price=  277.10 time= 08-04 00:00
  [10] PEAK   price=  299.90 time= 08-25 00:00
  [11] TROUGH price=  242.70 time= 09-08 00:00
  [12] PEAK   price=  277.30 time= 10-13 00:00
  [13] TROUGH price=  215.00 time= 10-27 00:00
  [14] PEAK   price=  444.60 time= 03-02 00:00
  [15] TROUGH price=  372.70 time= 03-23 00:00
  [16] PEAK   price=  479.00 time= 07-06 00:00
  [17] TROUGH price=  395.20 time= 08-17 00:00
  [18] PEAK   price=  546.50 time= 10-12 00:00
  [19] TROUGH price=  417.50 time= 11-30 00:00
  [20] PEAK   price=  823.60 time= 03-08 00:00
  [21] TROUGH price=  602.40 time= 04-06 00:00
  [22] PEAK   price=  787.20 time= 06-14 00:00
  [23] TROUGH price=  621.00 time= 07-12 00:00
  [24] PEAK   price=  752.40 time= 08-23 00:00
  [25] TROUGH price=  602.30 time= 09-27 00:00
  [26] PEAK   price=  709.50 time= 10-11 00:00
  [27] TROUGH price=  655.70 time= 10-18 00:00
  [28] PEAK   price=  722.50 time= 11-01 00:00
  [29] TROUGH price=  495.00 time= 12-06 00:00
  [30] PEAK   price=  571.60 time= 12-27 00:00
  [31] TROUGH price=  513.80 time= 02-07 00:00
  [32] PEAK   price=  589.70 time= 03-07 00:00
  [33] TROUGH price=  480.60 time= 03-14 00:00
  [34] PEAK   price=  606.50 time= 04-11 00:00
  [35] TROUGH price=  485.30 time= 05-04 00:00
  [36] PEAK   price=  758.00 time= 09-12 00:00
  [37] TROUGH price=  643.90 time= 10-10 00:00
  [38] PEAK   price=  700.70 time= 10-17 00:00
  [39] TROUGH price=  519.70 time= 12-12 00:00
  [40] PEAK   price=  599.50 time= 01-23 00:00
  [41] TROUGH price=  551.40 time= 02-06 00:00
  [42] PEAK   price=  682.80 time= 04-09 00:00
  [43] TROUGH price=  566.50 time= 06-04 00:00
  [44] PEAK   price=  641.10 time= 07-02 00:00
  [45] TROUGH price=  492.20 time= 09-10 00:00
  [46] PEAK   price=  587.50 time= 10-08 00:00
  [47] TROUGH price=  510.60 time= 10-29 00:00
  [48] PEAK   price=  639.50 time= 01-14 00:00
  [49] TROUGH price=  502.30 time= 03-04 00:00
  [50] PEAK   price=  558.50 time= 04-01 00:00
  [51] TROUGH price=  444.00 time= 04-08 00:00
  [52] PEAK   price=  506.00 time= 04-22 00:00
  [53] TROUGH price=  447.50 time= 05-27 00:00
  [54] PEAK   price=  588.60 time= 06-17 00:00
  [55] TROUGH price=  468.80 time= 09-02 00:00
  [56] PEAK   price=  502.50 time= 09-16 00:00
  [57] TROUGH price=  431.80 time= 10-21 00:00
  [58] PEAK   price=  472.20 time= 11-11 00:00
  [59] TROUGH price=  411.00 time= 01-06 00:00 ← A
  [60] PEAK   price=  823.00 time= 03-16 09:30
  [61] TROUGH price=  585.20 time= 04-13 09:30 ← C
  [62] PEAK   price=  695.70 time= 04-27 09:30
  [63] TROUGH price=  547.60 time= 06-08 09:15
```

**失败详情:**
```
  ❌ C4 最新(550.90) > C(585.20) = False
```
---

### SI — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8480.00 @ 06-09 00:00 |
| B 价 | 8875.00 @ 06-15 00:00 |
| C 价 | 8600.00 @ 06-17 09:15 |
| 最新价 | 8545.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 35 (merge 后: 23) |
| A 索引 | 20 | C 索引 | 22 |

**极值点序列** (swing: 35, merged: 23):
```
  [ 0] TROUGH price= 8315.00 time= 02-13 09:15
  [ 1] PEAK   price= 8560.00 time= 02-25 10:45
  [ 2] TROUGH price= 8205.00 time= 03-03 13:45
  [ 3] PEAK   price= 8965.00 time= 03-09 10:45
  [ 4] TROUGH price= 8620.00 time= 03-10 09:15
  [ 5] PEAK   price= 8830.00 time= 03-12 10:45
  [ 6] TROUGH price= 8335.00 time= 03-19 00:00
  [ 7] PEAK   price= 8900.00 time= 03-26 00:00
  [ 8] TROUGH price= 8345.00 time= 04-07 09:15
  [ 9] PEAK   price= 8515.00 time= 04-07 10:45
  [10] TROUGH price= 8285.00 time= 04-10 00:00
  [11] PEAK   price= 8750.00 time= 04-20 00:00
  [12] TROUGH price= 8515.00 time= 04-24 00:00
  [13] PEAK   price= 9280.00 time= 05-11 00:00
  [14] TROUGH price= 8405.00 time= 05-18 00:00
  [15] PEAK   price= 8560.00 time= 05-21 09:15
  [16] TROUGH price= 8420.00 time= 05-22 09:15
  [17] PEAK   price= 8815.00 time= 06-03 00:00
  [18] TROUGH price= 8555.00 time= 06-05 00:00
  [19] PEAK   price= 8835.00 time= 06-08 00:00
  [20] TROUGH price= 8480.00 time= 06-09 00:00 ← A
  [21] PEAK   price= 8875.00 time= 06-15 00:00
  [22] TROUGH price= 8600.00 time= 06-17 09:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(8545.00) > C(8600.00) = False
```
---

### SM — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 5730.00 @ 02-24 09:15 |
| B 价 | 6756.00 @ 03-23 08:00 |
| C 价 | 5832.00 @ 05-11 08:00 |
| 最新价 | 5832.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 10 (merge 后: 5) |
| A 索引 | 0 | C 索引 | 2 |

**极值点序列** (swing: 10, merged: 5):
```
  [ 0] TROUGH price= 5730.00 time= 02-24 09:15 ← A
  [ 1] PEAK   price= 6756.00 time= 03-23 08:00
  [ 2] TROUGH price= 5832.00 time= 05-11 08:00 ← C
  [ 3] PEAK   price= 6114.00 time= 06-01 09:15
  [ 4] TROUGH price= 5780.00 time= 06-15 09:15
```

**失败详情:**
```
  ❌ C4 最新(5832.00) > C(5832.00) = False
```
---

### SN — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 378500.00 @ 04-30 00:00 |
| B 价 | 440590.00 @ 05-14 00:00 |
| C 价 | 400300.00 @ 05-20 00:00 |
| 最新价 | 397880.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 60 (merge 后: 60) |
| A 索引 | 56 | C 索引 | 58 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] TROUGH price=206820.00 time= 02-06 00:00
  [ 1] PEAK   price=232980.00 time= 03-19 00:00
  [ 2] TROUGH price=221620.00 time= 03-26 00:00
  [ 3] PEAK   price=286690.00 time= 04-22 00:00
  [ 4] TROUGH price=248120.00 time= 04-24 00:00
  [ 5] PEAK   price=290520.00 time= 05-20 00:00
  [ 6] TROUGH price=268880.00 time= 05-24 00:00
  [ 7] PEAK   price=282650.00 time= 05-30 00:00
  [ 8] TROUGH price=257380.00 time= 06-06 00:00
  [ 9] PEAK   price=278420.00 time= 06-13 00:00
  [10] TROUGH price=261620.00 time= 06-26 00:00
  [11] PEAK   price=284820.00 time= 07-12 00:00
  [12] TROUGH price=237830.00 time= 07-31 00:00
  [13] PEAK   price=271130.00 time= 08-26 00:00
  [14] TROUGH price=246130.00 time= 09-05 00:00
  [15] PEAK   price=271490.00 time= 10-08 00:00
  [16] TROUGH price=250480.00 time= 10-22 00:00
  [17] PEAK   price=264360.00 time= 11-06 00:00
  [18] TROUGH price=231500.00 time= 11-29 00:00
  [19] PEAK   price=251980.00 time= 12-12 00:00
  [20] TROUGH price=239200.00 time= 12-19 00:00
  [21] PEAK   price=253370.00 time= 01-10 00:00
  [22] TROUGH price=243050.00 time= 01-15 00:00
  [23] PEAK   price=268330.00 time= 02-24 00:00
  [24] TROUGH price=253220.00 time= 02-27 00:00
  [25] PEAK   price=291510.00 time= 03-14 00:00
  [26] TROUGH price=273320.00 time= 03-25 00:00
  [27] PEAK   price=299990.00 time= 04-02 00:00
  [28] TROUGH price=235720.00 time= 04-10 00:00
  [29] PEAK   price=268590.00 time= 05-21 00:00
  [30] TROUGH price=248800.00 time= 06-03 00:00
  [31] PEAK   price=266240.00 time= 06-11 00:00
  [32] TROUGH price=258510.00 time= 06-20 00:00
  [33] PEAK   price=272000.00 time= 06-27 00:00
  [34] TROUGH price=260510.00 time= 07-09 00:00
  [35] PEAK   price=269000.00 time= 07-14 00:00
  [36] TROUGH price=260640.00 time= 07-17 00:00
  [37] PEAK   price=275960.00 time= 07-24 00:00
  [38] TROUGH price=262910.00 time= 08-01 00:00
  [39] PEAK   price=272000.00 time= 08-12 00:00
  [40] TROUGH price=265040.00 time= 08-22 00:00
  [41] PEAK   price=279010.00 time= 09-01 00:00
  [42] TROUGH price=268010.00 time= 09-10 00:00
  [43] PEAK   price=275030.00 time= 09-15 00:00
  [44] TROUGH price=267310.00 time= 09-19 00:00
  [45] PEAK   price=290640.00 time= 10-10 00:00
  [46] TROUGH price=277280.00 time= 10-20 00:00
  [47] PEAK   price=289590.00 time= 10-27 00:00
  [48] TROUGH price=279200.00 time= 11-05 00:00
  [49] PEAK   price=299980.00 time= 11-13 00:00
  [50] TROUGH price=316730.00 time= 12-30 00:00
  [51] PEAK   price=469950.00 time= 01-30 00:00
  [52] TROUGH price=345000.00 time= 02-06 00:00
  [53] PEAK   price=464700.00 time= 03-02 00:00
  [54] TROUGH price=322580.00 time= 03-23 00:00
  [55] PEAK   price=399600.00 time= 04-21 00:00
  [56] TROUGH price=378500.00 time= 04-30 00:00 ← A
  [57] PEAK   price=440590.00 time= 05-14 00:00
  [58] TROUGH price=400300.00 time= 05-20 00:00 ← C
  [59] PEAK   price=451860.00 time= 06-03 00:00
```

**失败详情:**
```
  ❌ C4 最新(397880.00) > C(400300.00) = False
```
---

### SN — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 420830.00 @ 06-16 15:00 |
| B 价 | 426350.00 @ 06-16 21:15 |
| C 价 | 423400.00 @ 06-17 23:30 |
| 最新价 | 414330.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 23) |
| A 索引 | 12 | C 索引 | 20 |

**极值点序列** (swing: 40, merged: 23):
```
  [ 0] TROUGH price=394240.00 time= 06-11 10:45
  [ 1] PEAK   price=413660.00 time= 06-12 09:00
  [ 2] TROUGH price=406250.00 time= 06-12 14:30
  [ 3] PEAK   price=412470.00 time= 06-12 21:15
  [ 4] TROUGH price=409400.00 time= 06-12 22:00
  [ 5] PEAK   price=414350.00 time= 06-12 23:15
  [ 6] TROUGH price=412330.00 time= 06-13 00:00
  [ 7] PEAK   price=427320.00 time= 06-15 11:00
  [ 8] TROUGH price=422830.00 time= 06-15 13:45
  [ 9] PEAK   price=427560.00 time= 06-15 21:15
  [10] TROUGH price=419810.00 time= 06-16 10:15
  [11] PEAK   price=423510.00 time= 06-16 13:45
  [12] TROUGH price=420830.00 time= 06-16 15:00 ← A
  [13] PEAK   price=426350.00 time= 06-16 21:15
  [14] TROUGH price=419820.00 time= 06-16 22:45
  [15] PEAK   price=422750.00 time= 06-17 00:30
  [16] TROUGH price=420800.00 time= 06-17 09:15
  [17] PEAK   price=424260.00 time= 06-17 10:45
  [18] TROUGH price=420560.00 time= 06-17 21:15
  [19] PEAK   price=426350.00 time= 06-17 22:45
  [20] TROUGH price=423400.00 time= 06-17 23:30 ← C
  [21] PEAK   price=424960.00 time= 06-18 00:45
  [22] TROUGH price=412310.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(414330.00) > C(423400.00) = False
```
---

### SN — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 419820.00 @ 06-16 22:00 |
| B 价 | 424260.00 @ 06-17 10:45 |
| C 价 | 420560.00 @ 06-17 21:15 |
| 最新价 | 414330.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 37 |

**极值点序列** (swing: 50, merged: 40):
```
  [ 0] PEAK   price=430150.00 time= 05-26 11:00
  [ 1] TROUGH price=422800.00 time= 05-27 00:00
  [ 2] PEAK   price=429960.00 time= 05-27 09:15
  [ 3] TROUGH price=418580.00 time= 05-27 14:00
  [ 4] PEAK   price=422970.00 time= 05-28 09:15
  [ 5] TROUGH price=416030.00 time= 05-28 10:00
  [ 6] PEAK   price=433530.00 time= 05-29 01:00
  [ 7] TROUGH price=423060.00 time= 05-29 14:00
  [ 8] PEAK   price=428150.00 time= 05-29 23:00
  [ 9] TROUGH price=424050.00 time= 06-01 09:15
  [10] PEAK   price=451300.00 time= 06-03 00:00
  [11] TROUGH price=445120.00 time= 06-03 09:15
  [12] PEAK   price=451630.00 time= 06-03 11:00
  [13] TROUGH price=440540.00 time= 06-03 22:00
  [14] PEAK   price=447490.00 time= 06-03 23:00
  [15] TROUGH price=429470.00 time= 06-04 14:00
  [16] PEAK   price=444650.00 time= 06-04 14:15
  [17] TROUGH price=420350.00 time= 06-05 09:15
  [18] PEAK   price=424580.00 time= 06-05 11:15
  [19] TROUGH price=403190.00 time= 06-05 22:00
  [20] PEAK   price=406740.00 time= 06-08 09:15
  [21] TROUGH price=396610.00 time= 06-08 14:00
  [22] PEAK   price=404730.00 time= 06-08 21:15
  [23] TROUGH price=396000.00 time= 06-09 09:15
  [24] PEAK   price=409800.00 time= 06-09 21:15
  [25] TROUGH price=390110.00 time= 06-10 10:45
  [26] PEAK   price=403900.00 time= 06-10 22:00
  [27] TROUGH price=394240.00 time= 06-11 10:30
  [28] PEAK   price=413660.00 time= 06-12 09:00
  [29] TROUGH price=406250.00 time= 06-12 14:00
  [30] PEAK   price=427320.00 time= 06-15 11:00
  [31] TROUGH price=422830.00 time= 06-15 13:45
  [32] PEAK   price=427560.00 time= 06-15 21:15
  [33] TROUGH price=419810.00 time= 06-16 10:00
  [34] PEAK   price=426350.00 time= 06-16 21:15
  [35] TROUGH price=419820.00 time= 06-16 22:00 ← A
  [36] PEAK   price=424260.00 time= 06-17 10:45
  [37] TROUGH price=420560.00 time= 06-17 21:15 ← C
  [38] PEAK   price=426350.00 time= 06-17 22:00
  [39] TROUGH price=412310.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(414330.00) > C(420560.00) = False
```
---

### SP — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4882.00 @ 06-16 10:15 |
| B 价 | 4956.00 @ 06-16 21:30 |
| C 价 | 4936.00 @ 06-16 22:45 |
| 最新价 | 4866.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 24) |
| A 索引 | 15 | C 索引 | 17 |

**极值点序列** (swing: 40, merged: 24):
```
  [ 0] PEAK   price= 4890.00 time= 06-10 14:15
  [ 1] TROUGH price= 4838.00 time= 06-10 21:00
  [ 2] PEAK   price= 4870.00 time= 06-10 22:30
  [ 3] TROUGH price= 4842.00 time= 06-11 09:15
  [ 4] PEAK   price= 4890.00 time= 06-11 10:00
  [ 5] TROUGH price= 4860.00 time= 06-11 11:00
  [ 6] PEAK   price= 4906.00 time= 06-11 14:30
  [ 7] TROUGH price= 4868.00 time= 06-11 22:00
  [ 8] PEAK   price= 4896.00 time= 06-12 11:00
  [ 9] TROUGH price= 4868.00 time= 06-12 14:00
  [10] PEAK   price= 4948.00 time= 06-12 22:15
  [11] TROUGH price= 4918.00 time= 06-15 09:15
  [12] PEAK   price= 4940.00 time= 06-15 10:15
  [13] TROUGH price= 4908.00 time= 06-15 14:00
  [14] PEAK   price= 4922.00 time= 06-15 22:15
  [15] TROUGH price= 4882.00 time= 06-16 10:15 ← A
  [16] PEAK   price= 4956.00 time= 06-16 21:30
  [17] TROUGH price= 4936.00 time= 06-16 22:45 ← C
  [18] PEAK   price= 4950.00 time= 06-17 09:30
  [19] TROUGH price= 4932.00 time= 06-17 10:00
  [20] PEAK   price= 4950.00 time= 06-17 10:45
  [21] TROUGH price= 4928.00 time= 06-17 14:45
  [22] PEAK   price= 4962.00 time= 06-17 22:15
  [23] TROUGH price= 4874.00 time= 06-18 11:15
```

**失败详情:**
```
  ❌ C4 最新(4866.00) > C(4936.00) = False
```
---

### SP — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4872.00 @ 05-29 22:00 |
| B 价 | 4908.00 @ 06-01 10:45 |
| C 价 | 4882.00 @ 06-16 10:00 |
| 最新价 | 4866.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 41) |
| A 索引 | 8 | C 索引 | 36 |

**极值点序列** (swing: 50, merged: 41):
```
  [ 0] TROUGH price= 4954.00 time= 05-25 22:00
  [ 1] PEAK   price= 4988.00 time= 05-26 11:00
  [ 2] TROUGH price= 4958.00 time= 05-26 14:00
  [ 3] PEAK   price= 4990.00 time= 05-26 21:15
  [ 4] TROUGH price= 4960.00 time= 05-26 23:00
  [ 5] PEAK   price= 4992.00 time= 05-27 10:00
  [ 6] TROUGH price= 4938.00 time= 05-28 11:00
  [ 7] PEAK   price= 4976.00 time= 05-28 14:00
  [ 8] TROUGH price= 4872.00 time= 05-29 22:00 ← A
  [ 9] PEAK   price= 4908.00 time= 06-01 10:45
  [10] TROUGH price= 4844.00 time= 06-02 10:00
  [11] PEAK   price= 4892.00 time= 06-02 21:15
  [12] TROUGH price= 4850.00 time= 06-03 10:45
  [13] PEAK   price= 4878.00 time= 06-03 14:15
  [14] TROUGH price= 4810.00 time= 06-04 10:45
  [15] PEAK   price= 4848.00 time= 06-04 14:00
  [16] TROUGH price= 4788.00 time= 06-04 22:00
  [17] PEAK   price= 4862.00 time= 06-05 10:00
  [18] TROUGH price= 4834.00 time= 06-05 14:15
  [19] PEAK   price= 4886.00 time= 06-05 21:15
  [20] TROUGH price= 4820.00 time= 06-08 14:00
  [21] PEAK   price= 4862.00 time= 06-08 21:15
  [22] TROUGH price= 4820.00 time= 06-09 10:00
  [23] PEAK   price= 4896.00 time= 06-09 21:15
  [24] TROUGH price= 4858.00 time= 06-10 13:30
  [25] PEAK   price= 4890.00 time= 06-10 14:00
  [26] TROUGH price= 4838.00 time= 06-10 21:00
  [27] PEAK   price= 4890.00 time= 06-11 10:00
  [28] TROUGH price= 4860.00 time= 06-11 11:00
  [29] PEAK   price= 4906.00 time= 06-11 14:00
  [30] TROUGH price= 4868.00 time= 06-11 14:15
  [31] PEAK   price= 4906.00 time= 06-11 15:00
  [32] TROUGH price= 4868.00 time= 06-11 23:00
  [33] PEAK   price= 4896.00 time= 06-12 11:00
  [34] TROUGH price= 4868.00 time= 06-12 14:00
  [35] PEAK   price= 4948.00 time= 06-12 22:00
  [36] TROUGH price= 4882.00 time= 06-16 10:00 ← C
  [37] PEAK   price= 4956.00 time= 06-16 21:15
  [38] TROUGH price= 4928.00 time= 06-17 14:00
  [39] PEAK   price= 4962.00 time= 06-17 22:00
  [40] TROUGH price= 4850.00 time= 06-18 14:00
```

**失败详情:**
```
  ❌ C4 最新(4866.00) > C(4882.00) = False
```
---

### SR — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 5312.00 @ 06-08 09:15 |
| B 价 | 5348.00 @ 06-08 21:15 |
| C 价 | 5332.00 @ 06-17 14:00 |
| 最新价 | 5320.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 38) |
| A 索引 | 19 | C 索引 | 35 |

**极值点序列** (swing: 50, merged: 38):
```
  [ 0] PEAK   price= 5376.00 time= 05-22 11:00
  [ 1] TROUGH price= 5350.00 time= 05-22 21:15
  [ 2] PEAK   price= 5378.00 time= 05-25 09:15
  [ 3] TROUGH price= 5339.00 time= 05-25 13:45
  [ 4] PEAK   price= 5408.00 time= 05-27 10:00
  [ 5] TROUGH price= 5351.00 time= 05-28 09:15
  [ 6] PEAK   price= 5419.00 time= 05-28 23:00
  [ 7] TROUGH price= 5390.00 time= 05-29 14:00
  [ 8] PEAK   price= 5454.00 time= 06-01 10:45
  [ 9] TROUGH price= 5430.00 time= 06-01 21:15
  [10] PEAK   price= 5451.00 time= 06-01 22:00
  [11] TROUGH price= 5417.00 time= 06-02 10:00
  [12] PEAK   price= 5455.00 time= 06-03 09:15
  [13] TROUGH price= 5427.00 time= 06-03 10:00
  [14] PEAK   price= 5446.00 time= 06-03 14:00
  [15] TROUGH price= 5368.00 time= 06-04 14:00
  [16] PEAK   price= 5390.00 time= 06-04 21:15
  [17] TROUGH price= 5317.00 time= 06-05 09:15
  [18] PEAK   price= 5353.00 time= 06-05 13:45
  [19] TROUGH price= 5312.00 time= 06-08 09:15 ← A
  [20] PEAK   price= 5348.00 time= 06-08 21:15
  [21] TROUGH price= 5303.00 time= 06-09 22:00
  [22] PEAK   price= 5322.00 time= 06-10 09:12
  [23] TROUGH price= 5301.00 time= 06-10 13:30
  [24] PEAK   price= 5322.00 time= 06-10 21:00
  [25] TROUGH price= 5277.00 time= 06-11 13:30
  [26] PEAK   price= 5298.00 time= 06-11 14:00
  [27] TROUGH price= 5273.00 time= 06-12 09:00
  [28] PEAK   price= 5331.00 time= 06-12 11:00
  [29] TROUGH price= 5303.00 time= 06-15 09:15
  [30] PEAK   price= 5325.00 time= 06-15 10:00
  [31] TROUGH price= 5311.00 time= 06-15 14:15
  [32] PEAK   price= 5335.00 time= 06-15 21:15
  [33] TROUGH price= 5307.00 time= 06-16 09:15
  [34] PEAK   price= 5354.00 time= 06-16 22:00
  [35] TROUGH price= 5332.00 time= 06-17 14:00 ← C
  [36] PEAK   price= 5353.00 time= 06-17 21:15
  [37] TROUGH price= 5310.00 time= 06-18 11:00
```

**失败详情:**
```
  ❌ C4 最新(5320.00) > C(5332.00) = False
```
---

### SS — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 15140.00 @ 06-18 09:15 |
| B 价 | 15040.00 @ 06-18 10:00 |
| C 价 | 15125.00 @ 06-18 13:45 |
| 最新价 | 15195.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 26) |
| A 索引 | 23 | C 索引 | 25 |

**极值点序列** (swing: 40, merged: 26):
```
  [ 0] TROUGH price=14345.00 time= 06-11 11:00
  [ 1] PEAK   price=14430.00 time= 06-11 13:30
  [ 2] TROUGH price=14380.00 time= 06-11 14:15
  [ 3] PEAK   price=14730.00 time= 06-12 09:00
  [ 4] TROUGH price=14640.00 time= 06-12 09:15
  [ 5] PEAK   price=14725.00 time= 06-12 10:45
  [ 6] TROUGH price=14660.00 time= 06-12 13:30
  [ 7] PEAK   price=14710.00 time= 06-12 14:30
  [ 8] TROUGH price=14635.00 time= 06-12 21:45
  [ 9] PEAK   price=14670.00 time= 06-12 22:30
  [10] TROUGH price=14620.00 time= 06-13 00:00
  [11] PEAK   price=15075.00 time= 06-15 22:00
  [12] TROUGH price=15025.00 time= 06-15 22:45
  [13] PEAK   price=15060.00 time= 06-15 23:45
  [14] TROUGH price=14985.00 time= 06-16 09:15
  [15] PEAK   price=15185.00 time= 06-16 11:00
  [16] TROUGH price=15155.00 time= 06-16 14:00
  [17] PEAK   price=15315.00 time= 06-16 23:45
  [18] TROUGH price=15150.00 time= 06-17 10:00
  [19] PEAK   price=15230.00 time= 06-17 14:30
  [20] TROUGH price=15035.00 time= 06-17 21:30
  [21] PEAK   price=15140.00 time= 06-17 22:15
  [22] TROUGH price=15090.00 time= 06-17 23:00
  [23] PEAK   price=15140.00 time= 06-18 09:15 ← A
  [24] TROUGH price=15040.00 time= 06-18 10:00
  [25] PEAK   price=15125.00 time= 06-18 13:45 ← C
```

**失败详情:**
```
  ❌ C4 最新(15195.00) < C(15125.00) = False
```
---

### TA — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 3098.00 time= 03-30 09:15
  [ 1] PEAK   price= 3534.00 time= 04-13 09:15
  [ 2] TROUGH price= 3028.00 time= 04-20 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### TA — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3410.00 @ 09-11 22:45 |
| B 价 | 3386.00 @ 09-14 09:30 |
| C 价 | 3400.00 @ 09-14 10:45 |
| 最新价 | 3450.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 36 | C 索引 | 38 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 3574.00 time= 08-25 21:15
  [ 1] TROUGH price= 3556.00 time= 08-26 09:15
  [ 2] PEAK   price= 3578.00 time= 08-26 21:30
  [ 3] TROUGH price= 3546.00 time= 08-27 11:00
  [ 4] PEAK   price= 3554.00 time= 08-27 14:30
  [ 5] TROUGH price= 3544.00 time= 08-27 21:15
  [ 6] PEAK   price= 3556.00 time= 08-27 21:30
  [ 7] TROUGH price= 3486.00 time= 08-28 15:00
  [ 8] PEAK   price= 3524.00 time= 08-31 11:15
  [ 9] TROUGH price= 3500.00 time= 08-31 14:45
  [10] PEAK   price= 3534.00 time= 08-31 21:15
  [11] TROUGH price= 3492.00 time= 09-01 09:30
  [12] PEAK   price= 3540.00 time= 09-01 14:00
  [13] TROUGH price= 3492.00 time= 09-01 21:15
  [14] PEAK   price= 3560.00 time= 09-01 21:45
  [15] TROUGH price= 3542.00 time= 09-02 09:30
  [16] PEAK   price= 3590.00 time= 09-02 21:15
  [17] TROUGH price= 3500.00 time= 09-03 21:15
  [18] PEAK   price= 3524.00 time= 09-03 22:15
  [19] TROUGH price= 3496.00 time= 09-04 14:30
  [20] PEAK   price= 3510.00 time= 09-04 21:15
  [21] TROUGH price= 3486.00 time= 09-07 09:15
  [22] PEAK   price= 3506.00 time= 09-07 11:30
  [23] TROUGH price= 3492.00 time= 09-07 14:00
  [24] PEAK   price= 3516.00 time= 09-08 09:15
  [25] TROUGH price= 3498.00 time= 09-08 10:45
  [26] PEAK   price= 3516.00 time= 09-08 14:15
  [27] TROUGH price= 3430.00 time= 09-08 21:15
  [28] PEAK   price= 3466.00 time= 09-08 22:45
  [29] TROUGH price= 3412.00 time= 09-09 15:00
  [30] PEAK   price= 3456.00 time= 09-09 21:15
  [31] TROUGH price= 3388.00 time= 09-10 21:45
  [32] PEAK   price= 3400.00 time= 09-10 22:15
  [33] TROUGH price= 3354.00 time= 09-11 09:45
  [34] PEAK   price= 3430.00 time= 09-11 10:45
  [35] TROUGH price= 3358.00 time= 09-11 13:45
  [36] PEAK   price= 3410.00 time= 09-11 22:45 ← A
  [37] TROUGH price= 3386.00 time= 09-14 09:30
  [38] PEAK   price= 3400.00 time= 09-14 10:45 ← C
  [39] TROUGH price= 3388.00 time= 09-14 11:15
```

**失败详情:**
```
  ❌ C4 最新(3450.00) < C(3400.00) = False
```
---

### TA — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4536.00 @ 05-17 21:15 |
| B 价 | 4646.00 @ 05-18 09:15 |
| C 价 | 4592.00 @ 05-18 11:00 |
| 最新价 | 4578.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 4554.00 time= 04-22 11:15
  [ 1] TROUGH price= 4444.00 time= 04-22 14:15
  [ 2] PEAK   price= 4550.00 time= 04-22 21:30
  [ 3] TROUGH price= 4520.00 time= 04-22 22:30
  [ 4] PEAK   price= 4556.00 time= 04-23 09:45
  [ 5] TROUGH price= 4504.00 time= 04-23 11:15
  [ 6] PEAK   price= 4548.00 time= 04-23 13:45
  [ 7] TROUGH price= 4512.00 time= 04-23 14:30
  [ 8] PEAK   price= 4636.00 time= 04-26 09:15
  [ 9] TROUGH price= 4494.00 time= 04-26 22:30
  [10] PEAK   price= 4756.00 time= 04-27 23:00
  [11] TROUGH price= 4690.00 time= 04-28 09:30
  [12] PEAK   price= 4806.00 time= 04-28 22:45
  [13] TROUGH price= 4748.00 time= 04-29 10:45
  [14] PEAK   price= 4850.00 time= 04-29 21:30
  [15] TROUGH price= 4730.00 time= 04-29 22:45
  [16] PEAK   price= 4790.00 time= 04-30 09:30
  [17] TROUGH price= 4708.00 time= 04-30 13:45
  [18] PEAK   price= 4870.00 time= 05-06 13:45
  [19] TROUGH price= 4788.00 time= 05-06 15:00
  [20] PEAK   price= 4864.00 time= 05-06 22:45
  [21] TROUGH price= 4816.00 time= 05-07 09:45
  [22] PEAK   price= 4908.00 time= 05-07 13:45
  [23] TROUGH price= 4770.00 time= 05-07 21:15
  [24] PEAK   price= 4882.00 time= 05-10 09:15
  [25] TROUGH price= 4770.00 time= 05-10 14:15
  [26] PEAK   price= 4804.00 time= 05-10 15:00
  [27] TROUGH price= 4722.00 time= 05-11 09:15
  [28] PEAK   price= 4762.00 time= 05-11 13:45
  [29] TROUGH price= 4630.00 time= 05-11 21:15
  [30] PEAK   price= 4844.00 time= 05-12 22:30
  [31] TROUGH price= 4524.00 time= 05-14 09:45
  [32] PEAK   price= 4610.00 time= 05-14 22:00
  [33] TROUGH price= 4566.00 time= 05-17 09:15
  [34] PEAK   price= 4600.00 time= 05-17 11:00
  [35] TROUGH price= 4536.00 time= 05-17 21:15 ← A
  [36] PEAK   price= 4646.00 time= 05-18 09:15
  [37] TROUGH price= 4592.00 time= 05-18 11:00 ← C
  [38] PEAK   price= 4680.00 time= 05-18 14:30
  [39] TROUGH price= 2849.00 time= 05-18 21:30
```

**失败详情:**
```
  ❌ C4 最新(4578.00) > C(4592.00) = False
```
---

### TA — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4444.00 @ 04-22 13:45 |
| B 价 | 4908.00 @ 05-07 13:45 |
| C 价 | 4630.00 @ 05-11 13:45 |
| 最新价 | 4578.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 10 | C 索引 | 12 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] TROUGH price= 4410.00 time= 03-10 13:45
  [ 1] PEAK   price= 4634.00 time= 03-15 09:15
  [ 2] TROUGH price= 4430.00 time= 03-16 13:45
  [ 3] PEAK   price= 4584.00 time= 03-18 13:45
  [ 4] TROUGH price= 4246.00 time= 03-24 09:15
  [ 5] PEAK   price= 4490.00 time= 03-26 13:45
  [ 6] TROUGH price= 4308.00 time= 04-01 10:45
  [ 7] PEAK   price= 4560.00 time= 04-06 13:45
  [ 8] TROUGH price= 4314.00 time= 04-12 10:45
  [ 9] PEAK   price= 4658.00 time= 04-20 13:45
  [10] TROUGH price= 4444.00 time= 04-22 13:45 ← A
  [11] PEAK   price= 4908.00 time= 05-07 13:45
  [12] TROUGH price= 4630.00 time= 05-11 13:45 ← C
  [13] PEAK   price= 4844.00 time= 05-12 13:45
  [14] TROUGH price= 4524.00 time= 05-14 09:15
```

**失败详情:**
```
  ❌ C4 最新(4578.00) > C(4630.00) = False
```
---

### TA — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 6640.00 @ 09-14 14:15 |
| B 价 | 6770.00 @ 09-14 21:30 |
| C 价 | 6700.00 @ 09-14 22:30 |
| 最新价 | 6658.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 36 | C 索引 | 38 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 6154.00 time= 08-25 10:15
  [ 1] PEAK   price= 6244.00 time= 08-25 14:00
  [ 2] TROUGH price= 6170.00 time= 08-25 15:00
  [ 3] PEAK   price= 6206.00 time= 08-25 21:45
  [ 4] TROUGH price= 6092.00 time= 08-26 09:15
  [ 5] PEAK   price= 6184.00 time= 08-26 14:00
  [ 6] TROUGH price= 6106.00 time= 08-26 21:45
  [ 7] PEAK   price= 6178.00 time= 08-29 09:45
  [ 8] TROUGH price= 6010.00 time= 08-29 14:30
  [ 9] PEAK   price= 6178.00 time= 08-30 09:15
  [10] TROUGH price= 6120.00 time= 08-30 10:45
  [11] PEAK   price= 6214.00 time= 08-30 15:00
  [12] TROUGH price= 6150.00 time= 08-30 21:15
  [13] PEAK   price= 6276.00 time= 08-31 11:30
  [14] TROUGH price= 6228.00 time= 08-31 21:15
  [15] PEAK   price= 6294.00 time= 08-31 23:00
  [16] TROUGH price= 6246.00 time= 09-01 09:15
  [17] PEAK   price= 6350.00 time= 09-01 14:45
  [18] TROUGH price= 6220.00 time= 09-01 22:15
  [19] PEAK   price= 6296.00 time= 09-02 11:30
  [20] TROUGH price= 6222.00 time= 09-02 14:30
  [21] PEAK   price= 6648.00 time= 09-05 21:15
  [22] TROUGH price= 6400.00 time= 09-06 11:15
  [23] PEAK   price= 6508.00 time= 09-06 15:00
  [24] TROUGH price= 6354.00 time= 09-07 10:45
  [25] PEAK   price= 6402.00 time= 09-07 11:30
  [26] TROUGH price= 6330.00 time= 09-07 21:15
  [27] PEAK   price= 6366.00 time= 09-07 22:45
  [28] TROUGH price= 6330.00 time= 09-08 09:45
  [29] PEAK   price= 6400.00 time= 09-08 11:00
  [30] TROUGH price= 6366.00 time= 09-08 21:15
  [31] PEAK   price= 6460.00 time= 09-08 22:30
  [32] TROUGH price= 6390.00 time= 09-08 23:00
  [33] PEAK   price= 6796.00 time= 09-13 15:00
  [34] TROUGH price= 6684.00 time= 09-13 23:00
  [35] PEAK   price= 6724.00 time= 09-14 11:00
  [36] TROUGH price= 6640.00 time= 09-14 14:15 ← A
  [37] PEAK   price= 6770.00 time= 09-14 21:30
  [38] TROUGH price= 6700.00 time= 09-14 22:30 ← C
  [39] PEAK   price= 6750.00 time= 09-15 13:45
```

**失败详情:**
```
  ❌ C4 最新(6658.00) > C(6700.00) = False
```
---

### TA — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 6366.00 @ 09-08 21:15 |
| B 价 | 6796.00 @ 09-13 15:00 |
| C 价 | 6684.00 @ 09-13 23:00 |
| 最新价 | 6658.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 49) |
| A 索引 | 43 | C 索引 | 45 |

**极值点序列** (swing: 50, merged: 49):
```
  [ 0] PEAK   price= 5974.00 time= 07-29 23:00
  [ 1] TROUGH price= 5752.00 time= 08-01 09:15
  [ 2] PEAK   price= 5896.00 time= 08-01 14:00
  [ 3] TROUGH price= 5772.00 time= 08-01 21:15
  [ 4] PEAK   price= 5924.00 time= 08-02 11:00
  [ 5] TROUGH price= 5736.00 time= 08-02 14:00
  [ 6] PEAK   price= 5954.00 time= 08-03 21:15
  [ 7] TROUGH price= 5762.00 time= 08-04 09:15
  [ 8] PEAK   price= 5870.00 time= 08-04 11:00
  [ 9] TROUGH price= 5514.00 time= 08-05 21:15
  [10] PEAK   price= 5896.00 time= 08-09 09:15
  [11] TROUGH price= 5740.00 time= 08-10 13:45
  [12] PEAK   price= 6102.00 time= 08-15 09:15
  [13] TROUGH price= 6014.00 time= 08-15 11:00
  [14] PEAK   price= 6060.00 time= 08-15 15:00
  [15] TROUGH price= 5848.00 time= 08-15 22:00
  [16] PEAK   price= 5984.00 time= 08-16 11:00
  [17] TROUGH price= 5860.00 time= 08-17 09:15
  [18] PEAK   price= 5962.00 time= 08-17 13:45
  [19] TROUGH price= 5874.00 time= 08-17 21:15
  [20] PEAK   price= 6008.00 time= 08-18 21:15
  [21] TROUGH price= 5824.00 time= 08-19 21:15
  [22] PEAK   price= 5950.00 time= 08-22 11:00
  [23] TROUGH price= 5868.00 time= 08-22 21:15
  [24] PEAK   price= 6216.00 time= 08-24 21:15
  [25] TROUGH price= 6124.00 time= 08-24 22:00
  [26] PEAK   price= 6244.00 time= 08-25 14:00
  [27] TROUGH price= 6092.00 time= 08-26 09:15
  [28] PEAK   price= 6184.00 time= 08-26 14:00
  [29] TROUGH price= 6010.00 time= 08-29 14:00
  [30] PEAK   price= 6178.00 time= 08-30 09:15
  [31] TROUGH price= 6120.00 time= 08-30 10:45
  [32] PEAK   price= 6276.00 time= 08-31 11:00
  [33] TROUGH price= 6228.00 time= 08-31 21:15
  [34] PEAK   price= 6350.00 time= 09-01 14:00
  [35] TROUGH price= 6220.00 time= 09-01 22:00
  [36] PEAK   price= 6296.00 time= 09-02 11:00
  [37] TROUGH price= 6222.00 time= 09-02 14:00
  [38] PEAK   price= 6648.00 time= 09-05 21:15
  [39] TROUGH price= 6400.00 time= 09-06 11:00
  [40] PEAK   price= 6508.00 time= 09-06 15:00
  [41] TROUGH price= 6330.00 time= 09-07 21:15
  [42] PEAK   price= 6400.00 time= 09-08 11:00
  [43] TROUGH price= 6366.00 time= 09-08 21:15 ← A
  [44] PEAK   price= 6796.00 time= 09-13 15:00
  [45] TROUGH price= 6684.00 time= 09-13 23:00 ← C
  [46] PEAK   price= 6724.00 time= 09-14 11:00
  [47] TROUGH price= 6640.00 time= 09-14 14:00
  [48] PEAK   price= 6770.00 time= 09-14 21:15
```

**失败详情:**
```
  ❌ C4 最新(6658.00) > C(6684.00) = False
```
---

### TA — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 6148.00 time= 07-24 09:15
  [ 1] TROUGH price= 5732.00 time= 08-07 09:15
  [ 2] PEAK   price= 6232.00 time= 08-28 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### TA — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 5656.00 @ 01-11 09:30 |
| B 价 | 5762.00 @ 01-12 10:15 |
| C 价 | 5732.00 @ 01-12 13:45 |
| 最新价 | 5724.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 34 | C 索引 | 36 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 5866.00 time= 12-26 23:00
  [ 1] PEAK   price= 5916.00 time= 12-27 10:15
  [ 2] TROUGH price= 5884.00 time= 12-27 13:45
  [ 3] PEAK   price= 5920.00 time= 12-27 14:45
  [ 4] TROUGH price= 5872.00 time= 12-27 21:30
  [ 5] PEAK   price= 5894.00 time= 12-27 22:15
  [ 6] TROUGH price= 5868.00 time= 12-28 09:15
  [ 7] PEAK   price= 5938.00 time= 12-28 10:15
  [ 8] TROUGH price= 5892.00 time= 12-28 11:00
  [ 9] PEAK   price= 5936.00 time= 12-28 15:00
  [10] TROUGH price= 5870.00 time= 12-28 22:00
  [11] PEAK   price= 5902.00 time= 12-28 23:00
  [12] TROUGH price= 5840.00 time= 12-29 09:30
  [13] PEAK   price= 5880.00 time= 12-29 13:45
  [14] TROUGH price= 5844.00 time= 12-29 14:45
  [15] PEAK   price= 5988.00 time= 01-02 09:15
  [16] TROUGH price= 5878.00 time= 01-02 13:45
  [17] PEAK   price= 5928.00 time= 01-02 21:15
  [18] TROUGH price= 5800.00 time= 01-03 13:45
  [19] PEAK   price= 5902.00 time= 01-04 10:15
  [20] TROUGH price= 5832.00 time= 01-04 11:30
  [21] PEAK   price= 5872.00 time= 01-04 14:45
  [22] TROUGH price= 5788.00 time= 01-05 10:00
  [23] PEAK   price= 5868.00 time= 01-05 14:30
  [24] TROUGH price= 5820.00 time= 01-05 21:30
  [25] PEAK   price= 5896.00 time= 01-05 22:15
  [26] TROUGH price= 5676.00 time= 01-08 22:45
  [27] PEAK   price= 5704.00 time= 01-09 09:45
  [28] TROUGH price= 5672.00 time= 01-09 10:00
  [29] PEAK   price= 5708.00 time= 01-09 11:30
  [30] TROUGH price= 5662.00 time= 01-09 14:15
  [31] PEAK   price= 5724.00 time= 01-10 10:00
  [32] TROUGH price= 5682.00 time= 01-10 14:15
  [33] PEAK   price= 5706.00 time= 01-10 21:30
  [34] TROUGH price= 5656.00 time= 01-11 09:30 ← A
  [35] PEAK   price= 5762.00 time= 01-12 10:15
  [36] TROUGH price= 5732.00 time= 01-12 13:45 ← C
  [37] PEAK   price= 5750.00 time= 01-15 09:15
  [38] TROUGH price= 5710.00 time= 01-15 09:45
  [39] PEAK   price= 5760.00 time= 01-15 11:00
```

**失败详情:**
```
  ❌ C4 最新(5724.00) > C(5732.00) = False
```
---

### TA — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 5128.00 @ 01-13 09:30 |
| B 价 | 5034.00 @ 01-13 21:45 |
| C 价 | 5100.00 @ 01-14 09:30 |
| 最新价 | 5120.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 4784.00 time= 12-26 10:15
  [ 1] PEAK   price= 4802.00 time= 12-26 11:30
  [ 2] TROUGH price= 4778.00 time= 12-26 15:00
  [ 3] PEAK   price= 4818.00 time= 12-26 22:15
  [ 4] TROUGH price= 4748.00 time= 12-27 10:15
  [ 5] PEAK   price= 4762.00 time= 12-27 11:15
  [ 6] TROUGH price= 4732.00 time= 12-27 14:45
  [ 7] PEAK   price= 4760.00 time= 12-27 21:15
  [ 8] TROUGH price= 4738.00 time= 12-30 09:15
  [ 9] PEAK   price= 4778.00 time= 12-30 10:00
  [10] TROUGH price= 4754.00 time= 12-30 14:00
  [11] PEAK   price= 4780.00 time= 12-30 21:15
  [12] TROUGH price= 4752.00 time= 12-30 22:00
  [13] PEAK   price= 4774.00 time= 12-30 22:45
  [14] TROUGH price= 4760.00 time= 12-31 10:15
  [15] PEAK   price= 4902.00 time= 01-02 11:15
  [16] TROUGH price= 4870.00 time= 01-02 13:45
  [17] PEAK   price= 4920.00 time= 01-02 21:15
  [18] TROUGH price= 4890.00 time= 01-03 09:45
  [19] PEAK   price= 4910.00 time= 01-03 10:45
  [20] TROUGH price= 4870.00 time= 01-03 21:15
  [21] PEAK   price= 4982.00 time= 01-06 09:30
  [22] TROUGH price= 4890.00 time= 01-06 14:30
  [23] PEAK   price= 4924.00 time= 01-06 21:15
  [24] TROUGH price= 4810.00 time= 01-07 11:15
  [25] PEAK   price= 4838.00 time= 01-07 21:15
  [26] TROUGH price= 4798.00 time= 01-07 22:15
  [27] PEAK   price= 4830.00 time= 01-08 09:15
  [28] TROUGH price= 4810.00 time= 01-08 10:15
  [29] PEAK   price= 4980.00 time= 01-09 13:45
  [30] TROUGH price= 4946.00 time= 01-09 21:15
  [31] PEAK   price= 5012.00 time= 01-10 09:15
  [32] TROUGH price= 4942.00 time= 01-10 11:15
  [33] PEAK   price= 5050.00 time= 01-10 21:15
  [34] TROUGH price= 5020.00 time= 01-10 23:00
  [35] PEAK   price= 5128.00 time= 01-13 09:30 ← A
  [36] TROUGH price= 5034.00 time= 01-13 21:45
  [37] PEAK   price= 5100.00 time= 01-14 09:30 ← C
  [38] TROUGH price= 5054.00 time= 01-14 13:45
  [39] PEAK   price= 5114.00 time= 01-14 21:45
```

**失败详情:**
```
  ❌ C4 最新(5120.00) < C(5100.00) = False
```
---

### TA — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 4948.00 time= 03-24 09:15
  [ 1] TROUGH price= 4016.00 time= 04-07 09:15
  [ 2] PEAK   price= 5100.00 time= 05-12 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### TA — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 6060.00 @ 05-29 13:45 |
| B 价 | 6352.00 @ 06-03 00:00 |
| C 价 | 6130.00 @ 06-05 00:00 |
| 最新价 | 5856.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 37 (merge 后: 24) |
| A 索引 | 19 | C 索引 | 21 |

**极值点序列** (swing: 37, merged: 24):
```
  [ 0] PEAK   price= 6930.00 time= 03-16 00:00
  [ 1] TROUGH price= 6252.00 time= 03-20 00:00
  [ 2] PEAK   price= 7042.00 time= 03-23 00:00
  [ 3] TROUGH price= 6174.00 time= 03-25 00:00
  [ 4] PEAK   price= 6918.00 time= 03-30 00:00
  [ 5] TROUGH price= 6226.00 time= 04-01 00:00
  [ 6] PEAK   price= 6816.00 time= 04-08 00:00
  [ 7] TROUGH price= 6010.00 time= 04-14 00:00
  [ 8] PEAK   price= 6444.00 time= 04-16 13:45
  [ 9] TROUGH price= 6172.00 time= 04-17 13:45
  [10] PEAK   price= 6844.00 time= 05-06 00:00
  [11] TROUGH price= 6308.00 time= 05-08 13:45
  [12] PEAK   price= 6566.00 time= 05-11 13:45
  [13] TROUGH price= 6252.00 time= 05-14 00:00
  [14] PEAK   price= 6550.00 time= 05-18 00:00
  [15] TROUGH price= 6314.00 time= 05-18 13:45
  [16] PEAK   price= 6448.00 time= 05-21 13:45
  [17] TROUGH price= 5876.00 time= 05-25 00:00
  [18] PEAK   price= 6230.00 time= 05-28 10:45
  [19] TROUGH price= 6060.00 time= 05-29 13:45 ← A
  [20] PEAK   price= 6352.00 time= 06-03 00:00
  [21] TROUGH price= 6130.00 time= 06-05 00:00 ← C
  [22] PEAK   price= 6470.00 time= 06-08 00:00
  [23] TROUGH price= 5716.00 time= 06-17 13:45
```

**失败详情:**
```
  ❌ C4 最新(5856.00) > C(6130.00) = False
```
---

### Y — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 6696.00 @ 12-31 09:15 |
| B 价 | 7140.00 @ 01-02 09:15 |
| C 价 | 6720.00 @ 01-07 09:15 |
| 最新价 | 6600.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 47 | C 索引 | 49 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 6434.00 time= 11-20 22:00
  [ 1] TROUGH price= 6378.00 time= 11-21 10:00
  [ 2] PEAK   price= 6406.00 time= 11-21 13:45
  [ 3] TROUGH price= 6304.00 time= 11-22 09:15
  [ 4] PEAK   price= 6418.00 time= 11-22 21:15
  [ 5] TROUGH price= 6158.00 time= 11-26 13:45
  [ 6] PEAK   price= 6254.00 time= 11-27 11:00
  [ 7] TROUGH price= 6194.00 time= 11-27 14:00
  [ 8] PEAK   price= 6250.00 time= 11-28 11:00
  [ 9] TROUGH price= 6198.00 time= 11-28 14:00
  [10] PEAK   price= 6274.00 time= 11-28 21:15
  [11] TROUGH price= 6216.00 time= 11-29 10:45
  [12] PEAK   price= 6302.00 time= 11-29 14:00
  [13] TROUGH price= 6190.00 time= 12-02 14:00
  [14] PEAK   price= 6240.00 time= 12-02 21:15
  [15] TROUGH price= 6170.00 time= 12-03 09:15
  [16] PEAK   price= 6250.00 time= 12-03 15:00
  [17] TROUGH price= 6216.00 time= 12-04 09:15
  [18] PEAK   price= 6274.00 time= 12-04 10:00
  [19] TROUGH price= 6220.00 time= 12-04 14:00
  [20] PEAK   price= 6314.00 time= 12-05 15:00
  [21] TROUGH price= 6260.00 time= 12-06 09:15
  [22] PEAK   price= 6452.00 time= 12-09 11:00
  [23] TROUGH price= 6388.00 time= 12-09 15:00
  [24] PEAK   price= 6440.00 time= 12-09 23:00
  [25] TROUGH price= 6358.00 time= 12-10 14:00
  [26] PEAK   price= 6404.00 time= 12-10 15:00
  [27] TROUGH price= 6342.00 time= 12-11 11:00
  [28] PEAK   price= 6582.00 time= 12-13 14:00
  [29] TROUGH price= 6482.00 time= 12-13 21:15
  [30] PEAK   price= 6544.00 time= 12-16 09:15
  [31] TROUGH price= 6468.00 time= 12-16 10:00
  [32] PEAK   price= 6626.00 time= 12-17 10:00
  [33] TROUGH price= 6594.00 time= 12-17 14:00
  [34] PEAK   price= 6640.00 time= 12-17 21:15
  [35] TROUGH price= 6558.00 time= 12-18 22:00
  [36] PEAK   price= 6632.00 time= 12-19 09:15
  [37] TROUGH price= 6538.00 time= 12-19 21:15
  [38] PEAK   price= 6646.00 time= 12-20 11:00
  [39] TROUGH price= 6514.00 time= 12-23 11:00
  [40] PEAK   price= 6550.00 time= 12-23 14:00
  [41] TROUGH price= 6488.00 time= 12-24 10:00
  [42] PEAK   price= 6530.00 time= 12-24 14:00
  [43] TROUGH price= 6482.00 time= 12-25 22:45
  [44] PEAK   price= 6718.00 time= 12-30 09:15
  [45] TROUGH price= 6652.00 time= 12-30 11:00
  [46] PEAK   price= 6790.00 time= 12-30 22:00
  [47] TROUGH price= 6696.00 time= 12-31 09:15 ← A
  [48] PEAK   price= 7140.00 time= 01-02 09:15
  [49] TROUGH price= 6720.00 time= 01-07 09:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(6600.00) > C(6720.00) = False
```
---

### Y — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 6512.00 time= 11-11 09:15
  [ 1] TROUGH price= 6158.00 time= 11-25 09:15
  [ 2] PEAK   price= 7140.00 time= 12-30 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### Y — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 5400.00 @ 04-28 15:00 |
| B 价 | 5450.00 @ 04-29 09:15 |
| C 价 | 5406.00 @ 04-30 10:45 |
| 最新价 | 5394.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 34 | C 索引 | 38 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 5502.00 time= 04-08 14:30
  [ 1] PEAK   price= 5696.00 time= 04-09 11:00
  [ 2] TROUGH price= 5628.00 time= 04-10 09:15
  [ 3] PEAK   price= 5726.00 time= 04-10 10:45
  [ 4] TROUGH price= 5638.00 time= 04-10 13:45
  [ 5] PEAK   price= 5746.00 time= 04-13 09:15
  [ 6] TROUGH price= 5578.00 time= 04-14 10:00
  [ 7] PEAK   price= 5616.00 time= 04-14 10:45
  [ 8] TROUGH price= 5532.00 time= 04-15 09:15
  [ 9] PEAK   price= 5666.00 time= 04-15 10:00
  [10] TROUGH price= 5584.00 time= 04-15 11:30
  [11] PEAK   price= 5632.00 time= 04-15 14:00
  [12] TROUGH price= 5602.00 time= 04-15 14:45
  [13] PEAK   price= 5748.00 time= 04-16 10:45
  [14] TROUGH price= 5562.00 time= 04-17 10:15
  [15] PEAK   price= 5660.00 time= 04-17 15:00
  [16] TROUGH price= 5512.00 time= 04-20 13:45
  [17] PEAK   price= 5552.00 time= 04-20 14:15
  [18] TROUGH price= 5364.00 time= 04-21 11:15
  [19] PEAK   price= 5418.00 time= 04-21 14:15
  [20] TROUGH price= 5354.00 time= 04-22 09:15
  [21] PEAK   price= 5430.00 time= 04-22 09:30
  [22] TROUGH price= 5368.00 time= 04-22 15:00
  [23] PEAK   price= 5526.00 time= 04-23 15:00
  [24] TROUGH price= 5480.00 time= 04-24 09:15
  [25] PEAK   price= 5520.00 time= 04-24 10:15
  [26] TROUGH price= 5480.00 time= 04-24 10:45
  [27] PEAK   price= 5514.00 time= 04-24 14:45
  [28] TROUGH price= 5412.00 time= 04-27 09:15
  [29] PEAK   price= 5468.00 time= 04-27 10:45
  [30] TROUGH price= 5422.00 time= 04-27 13:45
  [31] PEAK   price= 5480.00 time= 04-27 14:15
  [32] TROUGH price= 5410.00 time= 04-28 10:00
  [33] PEAK   price= 5440.00 time= 04-28 11:00
  [34] TROUGH price= 5400.00 time= 04-28 15:00 ← A
  [35] PEAK   price= 5450.00 time= 04-29 09:15
  [36] TROUGH price= 5390.00 time= 04-29 14:30
  [37] PEAK   price= 5444.00 time= 04-30 09:30
  [38] TROUGH price= 5406.00 time= 04-30 10:45 ← C
  [39] PEAK   price= 5480.00 time= 05-08 14:45
```

**失败详情:**
```
  ❌ C4 最新(5394.00) > C(5406.00) = False
```
---

### Y — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8650.00 @ 01-06 22:30 |
| B 价 | 8886.00 @ 01-07 09:30 |
| C 价 | 8680.00 @ 01-13 10:15 |
| 最新价 | 8296.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 37 | C 索引 | 39 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 8096.00 time= 12-16 21:30
  [ 1] TROUGH price= 8054.00 time= 12-16 22:00
  [ 2] PEAK   price= 8164.00 time= 12-17 10:45
  [ 3] TROUGH price= 8106.00 time= 12-17 14:00
  [ 4] PEAK   price= 8460.00 time= 12-18 21:15
  [ 5] TROUGH price= 8366.00 time= 12-18 22:00
  [ 6] PEAK   price= 8452.00 time= 12-21 09:15
  [ 7] TROUGH price= 8362.00 time= 12-21 11:15
  [ 8] PEAK   price= 8414.00 time= 12-21 14:45
  [ 9] TROUGH price= 8246.00 time= 12-21 21:30
  [10] PEAK   price= 8444.00 time= 12-22 11:15
  [11] TROUGH price= 8210.00 time= 12-22 15:00
  [12] PEAK   price= 8322.00 time= 12-23 09:15
  [13] TROUGH price= 8270.00 time= 12-23 10:00
  [14] PEAK   price= 8636.00 time= 12-23 21:15
  [15] TROUGH price= 8582.00 time= 12-23 23:00
  [16] PEAK   price= 8728.00 time= 12-24 14:15
  [17] TROUGH price= 8650.00 time= 12-24 14:30
  [18] PEAK   price= 8740.00 time= 12-25 09:15
  [19] TROUGH price= 8660.00 time= 12-25 11:30
  [20] PEAK   price= 8744.00 time= 12-25 21:15
  [21] TROUGH price= 8602.00 time= 12-25 23:00
  [22] PEAK   price= 8700.00 time= 12-28 09:15
  [23] TROUGH price= 8620.00 time= 12-28 10:15
  [24] PEAK   price= 8650.00 time= 12-28 11:00
  [25] TROUGH price= 8538.00 time= 12-28 14:45
  [26] PEAK   price= 8624.00 time= 12-28 21:15
  [27] TROUGH price= 8508.00 time= 12-29 15:00
  [28] PEAK   price= 8746.00 time= 12-30 09:15
  [29] TROUGH price= 8602.00 time= 12-30 15:00
  [30] PEAK   price= 8692.00 time= 12-31 11:00
  [31] TROUGH price= 8622.00 time= 12-31 14:00
  [32] PEAK   price= 8864.00 time= 01-04 10:45
  [33] TROUGH price= 8726.00 time= 01-04 14:45
  [34] PEAK   price= 8830.00 time= 01-04 22:45
  [35] TROUGH price= 8706.00 time= 01-05 09:15
  [36] PEAK   price= 8822.00 time= 01-06 09:15
  [37] TROUGH price= 8650.00 time= 01-06 22:30 ← A
  [38] PEAK   price= 8886.00 time= 01-07 09:30
  [39] TROUGH price= 8680.00 time= 01-13 10:15 ← C
```

**失败详情:**
```
  ❌ C4 最新(8296.00) > C(8680.00) = False
```
---

### Y — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8650.00 @ 01-06 22:15 |
| B 价 | 8886.00 @ 01-07 09:30 |
| C 价 | 8680.00 @ 01-13 10:00 |
| 最新价 | 8296.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 49) |
| A 索引 | 46 | C 索引 | 48 |

**极值点序列** (swing: 50, merged: 49):
```
  [ 0] TROUGH price= 7616.00 time= 11-24 10:00
  [ 1] PEAK   price= 7824.00 time= 11-25 09:15
  [ 2] TROUGH price= 7758.00 time= 11-25 14:00
  [ 3] PEAK   price= 7828.00 time= 11-25 22:00
  [ 4] TROUGH price= 7742.00 time= 11-26 09:15
  [ 5] PEAK   price= 7832.00 time= 11-26 21:15
  [ 6] TROUGH price= 7680.00 time= 11-27 14:00
  [ 7] PEAK   price= 7910.00 time= 11-30 09:15
  [ 8] TROUGH price= 7604.00 time= 12-01 09:15
  [ 9] PEAK   price= 7776.00 time= 12-01 21:15
  [10] TROUGH price= 7642.00 time= 12-02 10:45
  [11] PEAK   price= 7770.00 time= 12-02 11:00
  [12] TROUGH price= 7620.00 time= 12-02 21:15
  [13] PEAK   price= 8056.00 time= 12-04 22:00
  [14] TROUGH price= 7942.00 time= 12-07 10:00
  [15] PEAK   price= 8030.00 time= 12-07 14:00
  [16] TROUGH price= 7828.00 time= 12-08 09:15
  [17] PEAK   price= 7920.00 time= 12-08 11:00
  [18] TROUGH price= 7734.00 time= 12-08 21:15
  [19] PEAK   price= 7844.00 time= 12-10 09:15
  [20] TROUGH price= 7754.00 time= 12-10 14:00
  [21] PEAK   price= 7966.00 time= 12-11 14:00
  [22] TROUGH price= 7874.00 time= 12-11 23:00
  [23] PEAK   price= 8058.00 time= 12-14 21:15
  [24] TROUGH price= 7924.00 time= 12-15 11:00
  [25] PEAK   price= 8164.00 time= 12-17 10:45
  [26] TROUGH price= 8106.00 time= 12-17 14:00
  [27] PEAK   price= 8460.00 time= 12-18 21:15
  [28] TROUGH price= 8354.00 time= 12-21 09:15
  [29] PEAK   price= 8414.00 time= 12-21 14:00
  [30] TROUGH price= 8246.00 time= 12-21 21:15
  [31] PEAK   price= 8444.00 time= 12-22 11:00
  [32] TROUGH price= 8210.00 time= 12-22 15:00
  [33] PEAK   price= 8740.00 time= 12-25 09:15
  [34] TROUGH price= 8660.00 time= 12-25 11:00
  [35] PEAK   price= 8744.00 time= 12-25 21:15
  [36] TROUGH price= 8508.00 time= 12-29 15:00
  [37] PEAK   price= 8746.00 time= 12-30 09:15
  [38] TROUGH price= 8602.00 time= 12-30 15:00
  [39] PEAK   price= 8692.00 time= 12-31 11:00
  [40] TROUGH price= 8622.00 time= 12-31 14:00
  [41] PEAK   price= 8864.00 time= 01-04 10:45
  [42] TROUGH price= 8726.00 time= 01-04 14:00
  [43] PEAK   price= 8830.00 time= 01-04 22:00
  [44] TROUGH price= 8706.00 time= 01-05 09:15
  [45] PEAK   price= 8822.00 time= 01-06 09:15
  [46] TROUGH price= 8650.00 time= 01-06 22:15 ← A
  [47] PEAK   price= 8886.00 time= 01-07 09:30
  [48] TROUGH price= 8680.00 time= 01-13 10:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(8296.00) > C(8680.00) = False
```
---

### Y — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8210.00 @ 12-22 13:45 |
| B 价 | 8744.00 @ 12-25 13:45 |
| C 价 | 8508.00 @ 12-29 13:45 |
| 最新价 | 8296.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 9 | C 索引 | 11 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] PEAK   price= 7596.00 time= 11-09 09:15
  [ 1] TROUGH price= 7350.00 time= 11-10 13:45
  [ 2] PEAK   price= 8036.00 time= 11-20 09:15
  [ 3] TROUGH price= 7616.00 time= 11-24 09:15
  [ 4] PEAK   price= 7910.00 time= 11-30 09:15
  [ 5] TROUGH price= 7604.00 time= 12-01 09:15
  [ 6] PEAK   price= 8056.00 time= 12-04 13:45
  [ 7] TROUGH price= 7734.00 time= 12-08 13:45
  [ 8] PEAK   price= 8460.00 time= 12-18 13:45
  [ 9] TROUGH price= 8210.00 time= 12-22 13:45 ← A
  [10] PEAK   price= 8744.00 time= 12-25 13:45
  [11] TROUGH price= 8508.00 time= 12-29 13:45 ← C
  [12] PEAK   price= 8864.00 time= 01-04 10:45
  [13] TROUGH price= 8650.00 time= 01-06 13:45
  [14] PEAK   price= 8886.00 time= 01-07 09:30
```

**失败详情:**
```
  ❌ C4 最新(8296.00) > C(8508.00) = False
```
---

### Y — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9260.00 @ 08-30 22:30 |
| B 价 | 9718.00 @ 09-07 15:00 |
| C 价 | 9622.00 @ 09-08 09:15 |
| 最新价 | 9580.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 33 | C 索引 | 37 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 9410.00 time= 08-17 22:45
  [ 1] TROUGH price= 9212.00 time= 08-18 11:30
  [ 2] PEAK   price= 9288.00 time= 08-18 14:15
  [ 3] TROUGH price= 9238.00 time= 08-18 14:45
  [ 4] PEAK   price= 9278.00 time= 08-18 21:15
  [ 5] TROUGH price= 9170.00 time= 08-19 09:15
  [ 6] PEAK   price= 9318.00 time= 08-19 11:00
  [ 7] TROUGH price= 9244.00 time= 08-19 11:15
  [ 8] PEAK   price= 9300.00 time= 08-19 14:15
  [ 9] TROUGH price= 9088.00 time= 08-19 22:45
  [10] PEAK   price= 9166.00 time= 08-20 09:15
  [11] TROUGH price= 9114.00 time= 08-20 10:00
  [12] PEAK   price= 9242.00 time= 08-20 14:30
  [13] TROUGH price= 9166.00 time= 08-20 15:00
  [14] PEAK   price= 9252.00 time= 08-20 21:30
  [15] TROUGH price= 9000.00 time= 08-23 09:15
  [16] PEAK   price= 9192.00 time= 08-23 11:15
  [17] TROUGH price= 9148.00 time= 08-23 15:00
  [18] PEAK   price= 9258.00 time= 08-23 21:15
  [19] TROUGH price= 9106.00 time= 08-23 23:00
  [20] PEAK   price= 9368.00 time= 08-24 22:15
  [21] TROUGH price= 9300.00 time= 08-25 09:15
  [22] PEAK   price= 9342.00 time= 08-25 10:00
  [23] TROUGH price= 9292.00 time= 08-25 10:45
  [24] PEAK   price= 9518.00 time= 08-25 22:00
  [25] TROUGH price= 9330.00 time= 08-26 14:45
  [26] PEAK   price= 9408.00 time= 08-26 22:00
  [27] TROUGH price= 9264.00 time= 08-27 09:15
  [28] PEAK   price= 9426.00 time= 08-27 11:30
  [29] TROUGH price= 9326.00 time= 08-27 22:00
  [30] PEAK   price= 9474.00 time= 08-30 09:30
  [31] TROUGH price= 9240.00 time= 08-30 21:15
  [32] PEAK   price= 9326.00 time= 08-30 21:30
  [33] TROUGH price= 9260.00 time= 08-30 22:30 ← A
  [34] PEAK   price= 9484.00 time= 08-31 14:45
  [35] TROUGH price= 9250.00 time= 09-02 09:30
  [36] PEAK   price= 9718.00 time= 09-07 15:00
  [37] TROUGH price= 9622.00 time= 09-08 09:15 ← C
  [38] PEAK   price= 9720.00 time= 09-08 15:00
  [39] TROUGH price= 9200.00 time= 09-10 13:45
```

**失败详情:**
```
  ❌ C4 最新(9580.00) > C(9622.00) = False
```
---

### Y — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9326.00 @ 08-27 22:00 |
| B 价 | 9718.00 @ 09-07 15:00 |
| C 价 | 9622.00 @ 09-08 09:15 |
| 最新价 | 9580.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 49) |
| A 索引 | 40 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 49):
```
  [ 0] TROUGH price= 8832.00 time= 07-26 11:00
  [ 1] PEAK   price= 9184.00 time= 07-27 11:00
  [ 2] TROUGH price= 8926.00 time= 07-28 21:15
  [ 3] PEAK   price= 9026.00 time= 07-29 21:15
  [ 4] TROUGH price= 8886.00 time= 07-30 09:15
  [ 5] PEAK   price= 8990.00 time= 07-30 15:00
  [ 6] TROUGH price= 8530.00 time= 08-03 09:15
  [ 7] PEAK   price= 8682.00 time= 08-03 13:45
  [ 8] TROUGH price= 8558.00 time= 08-03 21:15
  [ 9] PEAK   price= 8872.00 time= 08-04 21:15
  [10] TROUGH price= 8790.00 time= 08-05 09:15
  [11] PEAK   price= 8900.00 time= 08-05 21:15
  [12] TROUGH price= 8810.00 time= 08-06 09:15
  [13] PEAK   price= 9046.00 time= 08-06 22:00
  [14] TROUGH price= 8864.00 time= 08-09 21:15
  [15] PEAK   price= 9054.00 time= 08-10 11:00
  [16] TROUGH price= 9024.00 time= 08-11 11:00
  [17] PEAK   price= 9320.00 time= 08-11 21:15
  [18] TROUGH price= 9204.00 time= 08-12 10:00
  [19] PEAK   price= 9260.00 time= 08-12 14:00
  [20] TROUGH price= 9194.00 time= 08-12 21:15
  [21] PEAK   price= 9284.00 time= 08-13 09:15
  [22] TROUGH price= 9136.00 time= 08-13 11:00
  [23] PEAK   price= 9502.00 time= 08-16 09:15
  [24] TROUGH price= 9290.00 time= 08-16 21:15
  [25] PEAK   price= 9446.00 time= 08-17 14:00
  [26] TROUGH price= 9170.00 time= 08-19 09:15
  [27] PEAK   price= 9318.00 time= 08-19 11:00
  [28] TROUGH price= 9088.00 time= 08-19 22:00
  [29] PEAK   price= 9252.00 time= 08-20 21:15
  [30] TROUGH price= 9000.00 time= 08-23 09:15
  [31] PEAK   price= 9258.00 time= 08-23 21:15
  [32] TROUGH price= 9106.00 time= 08-23 23:00
  [33] PEAK   price= 9368.00 time= 08-24 22:00
  [34] TROUGH price= 9292.00 time= 08-25 10:45
  [35] PEAK   price= 9518.00 time= 08-25 22:00
  [36] TROUGH price= 9330.00 time= 08-26 14:00
  [37] PEAK   price= 9408.00 time= 08-26 22:00
  [38] TROUGH price= 9264.00 time= 08-27 09:15
  [39] PEAK   price= 9426.00 time= 08-27 11:00
  [40] TROUGH price= 9326.00 time= 08-27 22:00 ← A
  [41] PEAK   price= 9474.00 time= 08-30 09:15
  [42] TROUGH price= 9240.00 time= 08-30 21:15
  [43] PEAK   price= 9484.00 time= 08-31 14:00
  [44] TROUGH price= 9250.00 time= 09-02 09:15
  [45] PEAK   price= 9718.00 time= 09-07 15:00
  [46] TROUGH price= 9622.00 time= 09-08 09:15 ← C
  [47] PEAK   price= 9720.00 time= 09-08 15:00
  [48] TROUGH price= 9200.00 time= 09-10 13:45
```

**失败详情:**
```
  ❌ C4 最新(9580.00) > C(9622.00) = False
```
---

### Y — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 9502.00 @ 08-16 09:15 |
| B 价 | 9000.00 @ 08-23 09:15 |
| C 价 | 9484.00 @ 08-31 13:45 |
| 最新价 | 9580.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 14 (merge 后: 14) |
| A 索引 | 7 | C 索引 | 11 |

**极值点序列** (swing: 14, merged: 14):
```
  [ 0] TROUGH price= 8362.00 time= 07-06 13:45
  [ 1] PEAK   price= 9122.00 time= 07-19 09:15
  [ 2] TROUGH price= 8798.00 time= 07-19 13:45
  [ 3] PEAK   price= 9184.00 time= 07-27 10:45
  [ 4] TROUGH price= 8530.00 time= 08-03 09:15
  [ 5] PEAK   price= 9320.00 time= 08-11 13:45
  [ 6] TROUGH price= 9136.00 time= 08-13 10:45
  [ 7] PEAK   price= 9502.00 time= 08-16 09:15 ← A
  [ 8] TROUGH price= 9000.00 time= 08-23 09:15
  [ 9] PEAK   price= 9518.00 time= 08-25 13:45
  [10] TROUGH price= 9240.00 time= 08-30 13:45
  [11] PEAK   price= 9484.00 time= 08-31 13:45 ← C
  [12] TROUGH price= 9250.00 time= 09-02 09:15
  [13] PEAK   price= 9720.00 time= 09-08 15:00
```

**失败详情:**
```
  ❌ C4 最新(9580.00) < C(9484.00) = False
```
---

### Y — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 11710.00 @ 04-29 13:45 |
| B 价 | 11396.00 @ 05-05 10:45 |
| C 价 | 11464.00 @ 05-05 22:00 |
| 最新价 | 11478.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 34 | C 索引 | 38 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price=10846.00 time= 04-13 21:15
  [ 1] TROUGH price=10750.00 time= 04-13 22:00
  [ 2] PEAK   price=11036.00 time= 04-14 09:15
  [ 3] TROUGH price=10852.00 time= 04-14 22:00
  [ 4] PEAK   price=11056.00 time= 04-15 13:45
  [ 5] TROUGH price=10980.00 time= 04-15 14:30
  [ 6] PEAK   price=11174.00 time= 04-15 22:30
  [ 7] TROUGH price=10970.00 time= 04-18 10:00
  [ 8] PEAK   price=11234.00 time= 04-19 14:30
  [ 9] TROUGH price=11042.00 time= 04-19 22:00
  [10] PEAK   price=11218.00 time= 04-20 10:45
  [11] TROUGH price=11034.00 time= 04-20 14:30
  [12] PEAK   price=11264.00 time= 04-21 11:00
  [13] TROUGH price=11176.00 time= 04-21 13:45
  [14] PEAK   price=11236.00 time= 04-21 14:15
  [15] TROUGH price=11124.00 time= 04-21 21:15
  [16] PEAK   price=11310.00 time= 04-21 23:00
  [17] TROUGH price=11142.00 time= 04-22 14:15
  [18] PEAK   price=11704.00 time= 04-22 21:15
  [19] TROUGH price=11340.00 time= 04-22 22:15
  [20] PEAK   price=11484.00 time= 04-25 09:15
  [21] TROUGH price=11306.00 time= 04-25 10:45
  [22] PEAK   price=11416.00 time= 04-25 11:15
  [23] TROUGH price=10960.00 time= 04-25 22:30
  [24] PEAK   price=11390.00 time= 04-26 21:45
  [25] TROUGH price=11242.00 time= 04-26 22:30
  [26] PEAK   price=11372.00 time= 04-27 09:45
  [27] TROUGH price=11318.00 time= 04-27 10:45
  [28] PEAK   price=11760.00 time= 04-27 21:15
  [29] TROUGH price=11328.00 time= 04-28 10:45
  [30] PEAK   price=11548.00 time= 04-28 21:15
  [31] TROUGH price=11470.00 time= 04-28 21:45
  [32] PEAK   price=11724.00 time= 04-29 10:45
  [33] TROUGH price=11626.00 time= 04-29 11:00
  [34] PEAK   price=11710.00 time= 04-29 13:45 ← A
  [35] TROUGH price=11650.00 time= 04-29 14:00
  [36] PEAK   price=11722.00 time= 05-05 09:15
  [37] TROUGH price=11396.00 time= 05-05 10:45
  [38] PEAK   price=11464.00 time= 05-05 22:00 ← C
  [39] TROUGH price=10980.00 time= 05-10 09:15
```

**失败详情:**
```
  ❌ C4 最新(11478.00) < C(11464.00) = False
```
---

### Y — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 11724.00 @ 04-29 10:45 |
| B 价 | 11396.00 @ 05-05 10:45 |
| C 价 | 11464.00 @ 05-05 22:00 |
| 最新价 | 11478.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 46 | C 索引 | 48 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price=10534.00 time= 03-16 14:00
  [ 1] TROUGH price=10226.00 time= 03-17 14:00
  [ 2] PEAK   price=10572.00 time= 03-18 10:45
  [ 3] TROUGH price=10180.00 time= 03-18 21:15
  [ 4] PEAK   price=10426.00 time= 03-21 09:15
  [ 5] TROUGH price=10234.00 time= 03-21 21:15
  [ 6] PEAK   price=10470.00 time= 03-22 10:45
  [ 7] TROUGH price=10208.00 time= 03-23 09:15
  [ 8] PEAK   price=10334.00 time= 03-23 11:00
  [ 9] TROUGH price=10240.00 time= 03-23 14:00
  [10] PEAK   price=10718.00 time= 03-24 09:15
  [11] TROUGH price=10232.00 time= 03-25 09:15
  [12] PEAK   price=10388.00 time= 03-25 21:15
  [13] TROUGH price=10244.00 time= 03-28 09:15
  [14] PEAK   price=10450.00 time= 03-28 10:00
  [15] TROUGH price=10192.00 time= 03-29 09:15
  [16] PEAK   price=10326.00 time= 03-29 13:45
  [17] TROUGH price=10060.00 time= 03-29 21:15
  [18] PEAK   price=10296.00 time= 03-30 22:00
  [19] TROUGH price=10142.00 time= 03-31 09:15
  [20] PEAK   price=10380.00 time= 03-31 21:15
  [21] TROUGH price=10062.00 time= 04-01 14:00
  [22] PEAK   price=10558.00 time= 04-06 22:00
  [23] TROUGH price=10360.00 time= 04-07 13:45
  [24] PEAK   price=10584.00 time= 04-08 09:15
  [25] TROUGH price=10500.00 time= 04-08 11:00
  [26] PEAK   price=10720.00 time= 04-11 09:15
  [27] TROUGH price=10562.00 time= 04-11 10:00
  [28] PEAK   price=10636.00 time= 04-11 13:45
  [29] TROUGH price=10542.00 time= 04-11 21:15
  [30] PEAK   price=11036.00 time= 04-14 09:15
  [31] TROUGH price=10852.00 time= 04-14 22:00
  [32] PEAK   price=11174.00 time= 04-15 22:00
  [33] TROUGH price=10970.00 time= 04-18 10:00
  [34] PEAK   price=11234.00 time= 04-19 14:00
  [35] TROUGH price=11042.00 time= 04-19 22:00
  [36] PEAK   price=11218.00 time= 04-20 10:45
  [37] TROUGH price=11034.00 time= 04-20 14:00
  [38] PEAK   price=11264.00 time= 04-21 11:00
  [39] TROUGH price=11124.00 time= 04-21 21:15
  [40] PEAK   price=11310.00 time= 04-21 23:00
  [41] TROUGH price=11142.00 time= 04-22 14:00
  [42] PEAK   price=11704.00 time= 04-22 21:15
  [43] TROUGH price=10960.00 time= 04-25 22:00
  [44] PEAK   price=11760.00 time= 04-27 21:15
  [45] TROUGH price=11328.00 time= 04-28 10:45
  [46] PEAK   price=11724.00 time= 04-29 10:45 ← A
  [47] TROUGH price=11396.00 time= 05-05 10:45
  [48] PEAK   price=11464.00 time= 05-05 22:00 ← C
  [49] TROUGH price=10980.00 time= 05-10 09:15
```

**失败详情:**
```
  ❌ C4 最新(11478.00) < C(11464.00) = False
```
---

### Y — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9084.00 @ 12-29 10:45 |
| B 价 | 9186.00 @ 12-29 21:15 |
| C 价 | 9106.00 @ 12-30 10:00 |
| 最新价 | 8702.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 33 | C 索引 | 35 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 9200.00 time= 12-14 21:15
  [ 1] TROUGH price= 9156.00 time= 12-14 21:45
  [ 2] PEAK   price= 9202.00 time= 12-15 09:15
  [ 3] TROUGH price= 8992.00 time= 12-15 23:00
  [ 4] PEAK   price= 9102.00 time= 12-16 09:30
  [ 5] TROUGH price= 8902.00 time= 12-16 21:30
  [ 6] PEAK   price= 8950.00 time= 12-16 22:45
  [ 7] TROUGH price= 8850.00 time= 12-19 14:30
  [ 8] PEAK   price= 8906.00 time= 12-19 21:15
  [ 9] TROUGH price= 8836.00 time= 12-19 22:45
  [10] PEAK   price= 8898.00 time= 12-20 09:45
  [11] TROUGH price= 8700.00 time= 12-20 22:30
  [12] PEAK   price= 8798.00 time= 12-21 09:30
  [13] TROUGH price= 8730.00 time= 12-21 10:00
  [14] PEAK   price= 8776.00 time= 12-21 11:00
  [15] TROUGH price= 8716.00 time= 12-21 11:15
  [16] PEAK   price= 8804.00 time= 12-21 14:30
  [17] TROUGH price= 8716.00 time= 12-21 23:00
  [18] PEAK   price= 8774.00 time= 12-22 10:00
  [19] TROUGH price= 8662.00 time= 12-22 15:00
  [20] PEAK   price= 8700.00 time= 12-22 22:30
  [21] TROUGH price= 8554.00 time= 12-23 11:15
  [22] PEAK   price= 8616.00 time= 12-23 14:00
  [23] TROUGH price= 8568.00 time= 12-23 14:30
  [24] PEAK   price= 8846.00 time= 12-26 10:15
  [25] TROUGH price= 8804.00 time= 12-26 11:15
  [26] PEAK   price= 8850.00 time= 12-26 13:45
  [27] TROUGH price= 8804.00 time= 12-26 21:15
  [28] PEAK   price= 9178.00 time= 12-27 21:15
  [29] TROUGH price= 9084.00 time= 12-28 09:15
  [30] PEAK   price= 9172.00 time= 12-28 14:30
  [31] TROUGH price= 9090.00 time= 12-28 22:00
  [32] PEAK   price= 9142.00 time= 12-28 22:30
  [33] TROUGH price= 9084.00 time= 12-29 10:45 ← A
  [34] PEAK   price= 9186.00 time= 12-29 21:15
  [35] TROUGH price= 9106.00 time= 12-30 10:00 ← C
  [36] PEAK   price= 9188.00 time= 12-30 14:30
  [37] TROUGH price= 8986.00 time= 01-03 09:30
  [38] PEAK   price= 9230.00 time= 01-03 21:15
  [39] TROUGH price= 8698.00 time= 01-12 21:15
```

**失败详情:**
```
  ❌ C4 最新(8702.00) > C(9106.00) = False
```
---

### Y — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9084.00 @ 12-29 10:45 |
| B 价 | 9186.00 @ 12-29 21:15 |
| C 价 | 9106.00 @ 12-30 10:00 |
| 最新价 | 8702.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 43 | C 索引 | 45 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 9400.00 time= 11-11 14:00
  [ 1] TROUGH price= 9078.00 time= 11-14 14:00
  [ 2] PEAK   price= 9192.00 time= 11-15 11:00
  [ 3] TROUGH price= 9044.00 time= 11-15 14:00
  [ 4] PEAK   price= 9298.00 time= 11-16 09:15
  [ 5] TROUGH price= 9088.00 time= 11-16 22:00
  [ 6] PEAK   price= 9282.00 time= 11-18 10:45
  [ 7] TROUGH price= 9006.00 time= 11-21 11:00
  [ 8] PEAK   price= 9094.00 time= 11-21 15:00
  [ 9] TROUGH price= 8912.00 time= 11-21 22:00
  [10] PEAK   price= 9134.00 time= 11-22 21:15
  [11] TROUGH price= 8988.00 time= 11-23 13:45
  [12] PEAK   price= 9316.00 time= 11-25 09:15
  [13] TROUGH price= 9004.00 time= 11-28 09:15
  [14] PEAK   price= 9500.00 time= 11-29 22:00
  [15] TROUGH price= 9408.00 time= 11-30 10:45
  [16] PEAK   price= 9572.00 time= 11-30 22:00
  [17] TROUGH price= 9186.00 time= 12-02 21:15
  [18] PEAK   price= 9418.00 time= 12-05 10:00
  [19] TROUGH price= 9156.00 time= 12-06 09:15
  [20] PEAK   price= 9346.00 time= 12-06 22:00
  [21] TROUGH price= 9222.00 time= 12-07 10:45
  [22] PEAK   price= 9310.00 time= 12-07 11:00
  [23] TROUGH price= 9230.00 time= 12-07 15:00
  [24] PEAK   price= 9344.00 time= 12-08 10:00
  [25] TROUGH price= 9214.00 time= 12-08 14:00
  [26] PEAK   price= 9378.00 time= 12-08 22:00
  [27] TROUGH price= 8936.00 time= 12-12 14:00
  [28] PEAK   price= 9222.00 time= 12-14 09:15
  [29] TROUGH price= 9156.00 time= 12-14 10:00
  [30] PEAK   price= 9202.00 time= 12-15 09:15
  [31] TROUGH price= 8992.00 time= 12-15 23:00
  [32] PEAK   price= 9102.00 time= 12-16 09:15
  [33] TROUGH price= 8860.00 time= 12-19 09:15
  [34] PEAK   price= 8906.00 time= 12-19 21:15
  [35] TROUGH price= 8700.00 time= 12-20 22:00
  [36] PEAK   price= 8798.00 time= 12-21 09:15
  [37] TROUGH price= 8716.00 time= 12-21 11:00
  [38] PEAK   price= 8804.00 time= 12-21 14:00
  [39] TROUGH price= 8554.00 time= 12-23 11:00
  [40] PEAK   price= 9178.00 time= 12-27 21:15
  [41] TROUGH price= 9084.00 time= 12-28 09:15
  [42] PEAK   price= 9172.00 time= 12-28 14:00
  [43] TROUGH price= 9084.00 time= 12-29 10:45 ← A
  [44] PEAK   price= 9186.00 time= 12-29 21:15
  [45] TROUGH price= 9106.00 time= 12-30 10:00 ← C
  [46] PEAK   price= 9188.00 time= 12-30 14:00
  [47] TROUGH price= 8986.00 time= 01-03 09:15
  [48] PEAK   price= 9230.00 time= 01-03 21:15
  [49] TROUGH price= 8698.00 time= 01-12 21:15
```

**失败详情:**
```
  ❌ C4 最新(8702.00) > C(9106.00) = False
```
---

### Y — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8936.00 @ 12-12 13:45 |
| B 价 | 9222.00 @ 12-14 09:15 |
| C 价 | 8986.00 @ 01-03 09:15 |
| 最新价 | 8702.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 15 (merge 后: 15) |
| A 索引 | 9 | C 索引 | 13 |

**极值点序列** (swing: 15, merged: 15):
```
  [ 0] PEAK   price= 9748.00 time= 11-04 13:45
  [ 1] TROUGH price= 9044.00 time= 11-15 13:45
  [ 2] PEAK   price= 9298.00 time= 11-16 09:15
  [ 3] TROUGH price= 8912.00 time= 11-21 13:45
  [ 4] PEAK   price= 9316.00 time= 11-25 09:15
  [ 5] TROUGH price= 9004.00 time= 11-28 09:15
  [ 6] PEAK   price= 9572.00 time= 11-30 13:45
  [ 7] TROUGH price= 9156.00 time= 12-06 09:15
  [ 8] PEAK   price= 9378.00 time= 12-08 13:45
  [ 9] TROUGH price= 8936.00 time= 12-12 13:45 ← A
  [10] PEAK   price= 9222.00 time= 12-14 09:15
  [11] TROUGH price= 8554.00 time= 12-23 10:45
  [12] PEAK   price= 9178.00 time= 12-27 13:45
  [13] TROUGH price= 8986.00 time= 01-03 09:15 ← C
  [14] PEAK   price= 9230.00 time= 01-03 14:45
```

**失败详情:**
```
  ❌ C4 最新(8702.00) > C(8986.00) = False
```
---

### Y — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] TROUGH price= 8912.00 time= 11-21 09:15
  [ 1] PEAK   price= 9572.00 time= 11-28 09:15
  [ 2] TROUGH price= 8554.00 time= 12-19 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### Y — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 7690.00 @ 05-04 09:30 |
| B 价 | 8100.00 @ 05-04 10:00 |
| C 价 | 7982.00 @ 05-04 13:45 |
| 最新价 | 7890.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 32 | C 索引 | 34 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 8002.00 time= 04-14 22:30
  [ 1] PEAK   price= 8118.00 time= 04-17 09:15
  [ 2] TROUGH price= 8026.00 time= 04-17 10:15
  [ 3] PEAK   price= 8126.00 time= 04-17 22:00
  [ 4] TROUGH price= 8086.00 time= 04-17 22:45
  [ 5] PEAK   price= 8176.00 time= 04-18 09:15
  [ 6] TROUGH price= 8114.00 time= 04-18 10:15
  [ 7] PEAK   price= 8232.00 time= 04-18 13:45
  [ 8] TROUGH price= 8210.00 time= 04-18 21:15
  [ 9] PEAK   price= 8266.00 time= 04-18 21:30
  [10] TROUGH price= 8132.00 time= 04-19 11:00
  [11] PEAK   price= 8170.00 time= 04-19 11:30
  [12] TROUGH price= 8102.00 time= 04-19 21:30
  [13] PEAK   price= 8160.00 time= 04-19 22:45
  [14] TROUGH price= 8000.00 time= 04-20 11:30
  [15] PEAK   price= 8050.00 time= 04-20 22:00
  [16] TROUGH price= 7870.00 time= 04-21 21:15
  [17] PEAK   price= 7940.00 time= 04-21 21:30
  [18] TROUGH price= 7788.00 time= 04-24 09:15
  [19] PEAK   price= 7916.00 time= 04-24 22:15
  [20] TROUGH price= 7720.00 time= 04-25 11:15
  [21] PEAK   price= 7816.00 time= 04-25 14:30
  [22] TROUGH price= 7698.00 time= 04-25 22:45
  [23] PEAK   price= 8008.00 time= 04-26 21:30
  [24] TROUGH price= 7960.00 time= 04-26 22:30
  [25] PEAK   price= 8012.00 time= 04-27 09:15
  [26] TROUGH price= 7750.00 time= 04-27 21:45
  [27] PEAK   price= 7826.00 time= 04-27 23:00
  [28] TROUGH price= 7780.00 time= 04-28 09:15
  [29] PEAK   price= 7818.00 time= 04-28 10:45
  [30] TROUGH price= 7712.00 time= 04-28 14:15
  [31] PEAK   price= 8092.00 time= 04-28 15:00
  [32] TROUGH price= 7690.00 time= 05-04 09:30 ← A
  [33] PEAK   price= 8100.00 time= 05-04 10:00
  [34] TROUGH price= 7982.00 time= 05-04 13:45 ← C
  [35] PEAK   price= 8008.00 time= 05-04 21:15
  [36] TROUGH price= 7860.00 time= 05-05 11:15
  [37] PEAK   price= 8050.00 time= 05-08 14:00
  [38] TROUGH price= 7592.00 time= 05-11 09:45
  [39] PEAK   price= 8118.00 time= 05-11 21:15
```

**失败详情:**
```
  ❌ C4 最新(7890.00) > C(7982.00) = False
```
---

### Y — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 8318.00 time= 07-24 09:15
  [ 1] TROUGH price= 7874.00 time= 08-07 09:15
  [ 2] PEAK   price= 8990.00 time= 08-28 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### Y — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 7786.00 @ 04-12 13:45 |
| B 价 | 7394.00 @ 04-19 13:45 |
| C 价 | 7678.00 @ 04-24 09:15 |
| 最新价 | 7680.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 12 (merge 后: 12) |
| A 索引 | 6 | C 索引 | 8 |

**极值点序列** (swing: 12, merged: 12):
```
  [ 0] PEAK   price= 7948.00 time= 03-18 09:15
  [ 1] TROUGH price= 7764.00 time= 03-19 13:45
  [ 2] PEAK   price= 8030.00 time= 03-21 09:15
  [ 3] TROUGH price= 7624.00 time= 03-27 13:45
  [ 4] PEAK   price= 7930.00 time= 04-02 13:45
  [ 5] TROUGH price= 7566.00 time= 04-12 09:15
  [ 6] PEAK   price= 7786.00 time= 04-12 13:45 ← A
  [ 7] TROUGH price= 7394.00 time= 04-19 13:45
  [ 8] PEAK   price= 7678.00 time= 04-24 09:15 ← C
  [ 9] TROUGH price= 7492.00 time= 04-25 13:45
  [10] PEAK   price= 7950.00 time= 05-06 09:15
  [11] TROUGH price= 7328.00 time= 05-09 13:45
```

**失败详情:**
```
  ❌ C4 最新(7680.00) < C(7678.00) = False
```
---

### Y — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 7672.00 @ 12-24 13:45 |
| B 价 | 7776.00 @ 12-25 09:15 |
| C 价 | 7684.00 @ 12-25 23:00 |
| 最新价 | 7550.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 44 | C 索引 | 46 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 8772.00 time= 11-08 13:45
  [ 1] PEAK   price= 8954.00 time= 11-11 09:15
  [ 2] TROUGH price= 8248.00 time= 11-14 09:15
  [ 3] PEAK   price= 8350.00 time= 11-14 21:15
  [ 4] TROUGH price= 8228.00 time= 11-15 11:00
  [ 5] PEAK   price= 8360.00 time= 11-15 21:15
  [ 6] TROUGH price= 8072.00 time= 11-18 21:15
  [ 7] PEAK   price= 8306.00 time= 11-19 14:00
  [ 8] TROUGH price= 8166.00 time= 11-20 10:45
  [ 9] PEAK   price= 8268.00 time= 11-20 14:00
  [10] TROUGH price= 8086.00 time= 11-21 11:00
  [11] PEAK   price= 8182.00 time= 11-21 21:15
  [12] TROUGH price= 7988.00 time= 11-22 09:15
  [13] PEAK   price= 8084.00 time= 11-22 10:45
  [14] TROUGH price= 7976.00 time= 11-22 21:15
  [15] PEAK   price= 8106.00 time= 11-25 10:00
  [16] TROUGH price= 7986.00 time= 11-25 22:00
  [17] PEAK   price= 8128.00 time= 11-26 13:45
  [18] TROUGH price= 8028.00 time= 11-26 15:00
  [19] PEAK   price= 8124.00 time= 11-27 21:15
  [20] TROUGH price= 8024.00 time= 11-28 09:15
  [21] PEAK   price= 8270.00 time= 11-29 11:00
  [22] TROUGH price= 8040.00 time= 12-02 22:00
  [23] PEAK   price= 8116.00 time= 12-03 09:15
  [24] TROUGH price= 8002.00 time= 12-03 11:00
  [25] PEAK   price= 8124.00 time= 12-03 23:00
  [26] TROUGH price= 7930.00 time= 12-05 10:00
  [27] PEAK   price= 8058.00 time= 12-05 13:45
  [28] TROUGH price= 8002.00 time= 12-05 21:15
  [29] PEAK   price= 8060.00 time= 12-05 22:00
  [30] TROUGH price= 7958.00 time= 12-06 13:45
  [31] PEAK   price= 8048.00 time= 12-06 21:15
  [32] TROUGH price= 7944.00 time= 12-09 10:45
  [33] PEAK   price= 8090.00 time= 12-09 22:00
  [34] TROUGH price= 7954.00 time= 12-10 21:15
  [35] PEAK   price= 8148.00 time= 12-11 22:00
  [36] TROUGH price= 8046.00 time= 12-12 10:45
  [37] PEAK   price= 8088.00 time= 12-12 21:15
  [38] TROUGH price= 7982.00 time= 12-16 09:15
  [39] PEAK   price= 8056.00 time= 12-16 11:00
  [40] TROUGH price= 7484.00 time= 12-19 14:00
  [41] PEAK   price= 7650.00 time= 12-20 21:15
  [42] TROUGH price= 7576.00 time= 12-20 22:00
  [43] PEAK   price= 7724.00 time= 12-24 11:00
  [44] TROUGH price= 7672.00 time= 12-24 13:45 ← A
  [45] PEAK   price= 7776.00 time= 12-25 09:15
  [46] TROUGH price= 7684.00 time= 12-25 23:00 ← C
  [47] PEAK   price= 7842.00 time= 12-27 11:00
  [48] TROUGH price= 7728.00 time= 12-30 09:15
  [49] PEAK   price= 7902.00 time= 01-02 09:15
```

**失败详情:**
```
  ❌ C4 最新(7550.00) > C(7684.00) = False
```
---

### Y — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8040.00 @ 04-25 11:00 |
| B 价 | 7850.00 @ 04-28 13:45 |
| C 价 | 7916.00 @ 04-28 23:00 |
| 最新价 | 7950.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 45 | C 索引 | 47 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 7992.00 time= 03-21 10:45
  [ 1] PEAK   price= 8032.00 time= 03-21 14:00
  [ 2] TROUGH price= 7902.00 time= 03-24 09:15
  [ 3] PEAK   price= 7944.00 time= 03-24 15:00
  [ 4] TROUGH price= 7900.00 time= 03-24 21:15
  [ 5] PEAK   price= 7960.00 time= 03-25 09:15
  [ 6] TROUGH price= 7858.00 time= 03-25 14:00
  [ 7] PEAK   price= 7904.00 time= 03-26 10:45
  [ 8] TROUGH price= 7856.00 time= 03-26 14:00
  [ 9] PEAK   price= 7914.00 time= 03-26 21:15
  [10] TROUGH price= 7868.00 time= 03-27 09:15
  [11] PEAK   price= 8036.00 time= 03-28 09:15
  [12] TROUGH price= 7928.00 time= 03-28 22:00
  [13] PEAK   price= 8000.00 time= 03-31 09:15
  [14] TROUGH price= 7946.00 time= 03-31 11:00
  [15] PEAK   price= 8008.00 time= 03-31 14:00
  [16] TROUGH price= 7890.00 time= 04-01 10:00
  [17] PEAK   price= 8066.00 time= 04-02 09:15
  [18] TROUGH price= 7636.00 time= 04-07 15:00
  [19] PEAK   price= 7710.00 time= 04-07 22:00
  [20] TROUGH price= 7632.00 time= 04-08 14:00
  [21] PEAK   price= 7686.00 time= 04-08 21:15
  [22] TROUGH price= 7550.00 time= 04-09 09:15
  [23] PEAK   price= 7702.00 time= 04-10 09:15
  [24] TROUGH price= 7644.00 time= 04-10 21:15
  [25] PEAK   price= 7700.00 time= 04-10 22:00
  [26] TROUGH price= 7658.00 time= 04-11 10:00
  [27] PEAK   price= 7756.00 time= 04-14 10:00
  [28] TROUGH price= 7690.00 time= 04-15 11:00
  [29] PEAK   price= 7724.00 time= 04-15 13:45
  [30] TROUGH price= 7694.00 time= 04-15 21:15
  [31] PEAK   price= 7760.00 time= 04-16 09:15
  [32] TROUGH price= 7668.00 time= 04-16 14:00
  [33] PEAK   price= 7804.00 time= 04-17 22:00
  [34] TROUGH price= 7702.00 time= 04-18 21:15
  [35] PEAK   price= 7814.00 time= 04-21 09:15
  [36] TROUGH price= 7732.00 time= 04-21 11:00
  [37] PEAK   price= 7790.00 time= 04-21 15:00
  [38] TROUGH price= 7754.00 time= 04-21 23:00
  [39] PEAK   price= 7868.00 time= 04-22 14:00
  [40] TROUGH price= 7812.00 time= 04-23 10:00
  [41] PEAK   price= 7892.00 time= 04-23 15:00
  [42] TROUGH price= 7856.00 time= 04-23 23:00
  [43] PEAK   price= 7920.00 time= 04-24 11:00
  [44] TROUGH price= 7878.00 time= 04-24 14:00
  [45] PEAK   price= 8040.00 time= 04-25 11:00 ← A
  [46] TROUGH price= 7850.00 time= 04-28 13:45
  [47] PEAK   price= 7916.00 time= 04-28 23:00 ← C
  [48] TROUGH price= 7858.00 time= 04-29 15:00
  [49] PEAK   price= 8140.00 time= 05-06 21:15
```

**失败详情:**
```
  ❌ C4 最新(7950.00) < C(7916.00) = False
```
---

### Y — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | — |
| A 价 | N/A @ N/A |
| B 价 | N/A @ N/A |
| C 价 | N/A @ N/A |
| 最新价 | N/A |
| 条件判定 | — |
| DB 方向 | — (状态: —) |
| DB 重复行 | 否 |
| 极值点数量 | 3 (merge 后: 3) |
| A 索引 | — | C 索引 | — |

**极值点序列** (swing: 3, merged: 3):
```
  [ 0] PEAK   price= 8136.00 time= 03-17 09:15
  [ 1] TROUGH price= 7550.00 time= 04-07 09:15
  [ 2] PEAK   price= 8140.00 time= 05-06 09:15
```

**失败详情:**
```
算法无有效3点结构
```
---

### Y — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8490.00 @ 09-05 15:00 |
| B 价 | 7916.00 @ 09-08 21:15 |
| C 价 | 8268.00 @ 09-11 10:00 |
| 最新价 | 8268.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 35 | C 索引 | 39 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] TROUGH price= 8380.00 time= 08-20 10:15
  [ 1] PEAK   price= 8420.00 time= 08-20 10:45
  [ 2] TROUGH price= 8390.00 time= 08-20 13:45
  [ 3] PEAK   price= 8458.00 time= 08-20 14:00
  [ 4] TROUGH price= 8424.00 time= 08-20 21:15
  [ 5] PEAK   price= 8464.00 time= 08-20 21:45
  [ 6] TROUGH price= 8436.00 time= 08-20 22:15
  [ 7] PEAK   price= 8466.00 time= 08-20 22:45
  [ 8] TROUGH price= 8388.00 time= 08-21 13:45
  [ 9] PEAK   price= 8516.00 time= 08-22 09:15
  [10] TROUGH price= 8468.00 time= 08-22 11:15
  [11] PEAK   price= 8512.00 time= 08-22 21:15
  [12] TROUGH price= 8446.00 time= 08-22 22:00
  [13] PEAK   price= 8560.00 time= 08-25 10:45
  [14] TROUGH price= 8502.00 time= 08-25 11:15
  [15] PEAK   price= 8584.00 time= 08-25 21:45
  [16] TROUGH price= 8530.00 time= 08-26 09:15
  [17] PEAK   price= 8574.00 time= 08-26 11:15
  [18] TROUGH price= 8462.00 time= 08-26 22:45
  [19] PEAK   price= 8516.00 time= 08-27 09:30
  [20] TROUGH price= 8474.00 time= 08-27 11:15
  [21] PEAK   price= 8498.00 time= 08-27 13:45
  [22] TROUGH price= 8440.00 time= 08-27 21:45
  [23] PEAK   price= 8474.00 time= 08-27 22:15
  [24] TROUGH price= 8444.00 time= 08-28 09:15
  [25] PEAK   price= 8482.00 time= 08-28 10:00
  [26] TROUGH price= 8438.00 time= 08-28 11:30
  [27] PEAK   price= 8464.00 time= 08-28 21:15
  [28] TROUGH price= 8388.00 time= 08-29 09:15
  [29] PEAK   price= 8434.00 time= 08-29 11:15
  [30] TROUGH price= 8400.00 time= 08-29 11:30
  [31] PEAK   price= 8516.00 time= 08-29 21:15
  [32] TROUGH price= 8350.00 time= 08-29 22:15
  [33] PEAK   price= 8460.00 time= 09-03 11:00
  [34] TROUGH price= 8390.00 time= 09-04 21:30
  [35] PEAK   price= 8490.00 time= 09-05 15:00 ← A
  [36] TROUGH price= 7916.00 time= 09-08 21:15
  [37] PEAK   price= 8650.00 time= 09-09 21:15
  [38] TROUGH price= 8222.00 time= 09-10 09:30
  [39] PEAK   price= 8268.00 time= 09-11 10:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(8268.00) < C(8268.00) = False
```
---

### Y — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 8490.00 @ 09-05 15:00 |
| B 价 | 7916.00 @ 09-08 21:15 |
| C 价 | 8268.00 @ 09-11 10:00 |
| 最新价 | 8268.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | SHORT (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 45 | C 索引 | 49 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] TROUGH price= 8114.00 time= 07-25 13:45
  [ 1] PEAK   price= 8160.00 time= 07-25 21:15
  [ 2] TROUGH price= 8062.00 time= 07-28 09:15
  [ 3] PEAK   price= 8168.00 time= 07-28 22:00
  [ 4] TROUGH price= 8100.00 time= 07-29 10:00
  [ 5] PEAK   price= 8280.00 time= 07-30 09:15
  [ 6] TROUGH price= 8216.00 time= 07-30 10:45
  [ 7] PEAK   price= 8260.00 time= 07-30 13:45
  [ 8] TROUGH price= 8168.00 time= 07-31 21:15
  [ 9] PEAK   price= 8296.00 time= 08-01 21:15
  [10] TROUGH price= 8210.00 time= 08-04 09:15
  [11] PEAK   price= 8264.00 time= 08-04 13:45
  [12] TROUGH price= 8222.00 time= 08-04 21:15
  [13] PEAK   price= 8362.00 time= 08-05 21:15
  [14] TROUGH price= 8302.00 time= 08-05 22:00
  [15] PEAK   price= 8486.00 time= 08-06 21:15
  [16] TROUGH price= 8366.00 time= 08-07 11:00
  [17] PEAK   price= 8442.00 time= 08-08 09:15
  [18] TROUGH price= 8352.00 time= 08-11 09:15
  [19] PEAK   price= 8484.00 time= 08-11 21:15
  [20] TROUGH price= 8422.00 time= 08-11 23:00
  [21] PEAK   price= 8692.00 time= 08-13 10:00
  [22] TROUGH price= 8526.00 time= 08-13 22:00
  [23] PEAK   price= 8614.00 time= 08-14 10:00
  [24] TROUGH price= 8512.00 time= 08-14 21:15
  [25] PEAK   price= 8638.00 time= 08-15 22:00
  [26] TROUGH price= 8544.00 time= 08-18 15:00
  [27] PEAK   price= 8612.00 time= 08-19 10:45
  [28] TROUGH price= 8380.00 time= 08-20 10:00
  [29] PEAK   price= 8466.00 time= 08-20 22:00
  [30] TROUGH price= 8388.00 time= 08-21 13:45
  [31] PEAK   price= 8516.00 time= 08-22 09:15
  [32] TROUGH price= 8446.00 time= 08-22 22:00
  [33] PEAK   price= 8584.00 time= 08-25 21:15
  [34] TROUGH price= 8530.00 time= 08-26 09:15
  [35] PEAK   price= 8574.00 time= 08-26 11:00
  [36] TROUGH price= 8440.00 time= 08-27 21:15
  [37] PEAK   price= 8482.00 time= 08-28 10:00
  [38] TROUGH price= 8438.00 time= 08-28 11:00
  [39] PEAK   price= 8464.00 time= 08-28 21:15
  [40] TROUGH price= 8388.00 time= 08-29 09:15
  [41] PEAK   price= 8516.00 time= 08-29 21:15
  [42] TROUGH price= 8350.00 time= 08-29 22:00
  [43] PEAK   price= 8460.00 time= 09-03 11:00
  [44] TROUGH price= 8390.00 time= 09-04 21:15
  [45] PEAK   price= 8490.00 time= 09-05 15:00 ← A
  [46] TROUGH price= 7916.00 time= 09-08 21:15
  [47] PEAK   price= 8650.00 time= 09-09 21:15
  [48] TROUGH price= 8222.00 time= 09-10 09:15
  [49] PEAK   price= 8268.00 time= 09-11 10:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(8268.00) < C(8268.00) = False
```
---

### Y — 15m

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8074.00 @ 01-05 13:45 |
| B 价 | 8278.00 @ 01-07 22:45 |
| C 价 | 8228.00 @ 01-08 22:00 |
| 最新价 | 8228.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 40 (merge 后: 40) |
| A 索引 | 37 | C 索引 | 39 |

**极值点序列** (swing: 40, merged: 40):
```
  [ 0] PEAK   price= 8140.00 time= 12-17 09:45
  [ 1] TROUGH price= 8090.00 time= 12-17 11:00
  [ 2] PEAK   price= 8124.00 time= 12-17 13:45
  [ 3] TROUGH price= 8074.00 time= 12-17 21:15
  [ 4] PEAK   price= 8106.00 time= 12-18 09:15
  [ 5] TROUGH price= 8038.00 time= 12-18 14:00
  [ 6] PEAK   price= 8056.00 time= 12-18 14:15
  [ 7] TROUGH price= 7882.00 time= 12-19 11:30
  [ 8] PEAK   price= 7958.00 time= 12-19 21:15
  [ 9] TROUGH price= 7942.00 time= 12-19 22:30
  [10] PEAK   price= 7998.00 time= 12-22 09:15
  [11] TROUGH price= 7972.00 time= 12-22 11:30
  [12] PEAK   price= 8028.00 time= 12-22 21:15
  [13] TROUGH price= 7962.00 time= 12-23 09:45
  [14] PEAK   price= 7998.00 time= 12-23 11:15
  [15] TROUGH price= 7970.00 time= 12-23 14:00
  [16] PEAK   price= 8016.00 time= 12-23 21:15
  [17] TROUGH price= 7980.00 time= 12-24 09:15
  [18] PEAK   price= 8026.00 time= 12-24 10:15
  [19] TROUGH price= 7988.00 time= 12-24 15:00
  [20] PEAK   price= 8016.00 time= 12-25 09:15
  [21] TROUGH price= 7988.00 time= 12-25 10:00
  [22] PEAK   price= 8070.00 time= 12-25 21:15
  [23] TROUGH price= 8038.00 time= 12-26 10:00
  [24] PEAK   price= 8078.00 time= 12-26 14:00
  [25] TROUGH price= 8054.00 time= 12-26 15:00
  [26] PEAK   price= 8094.00 time= 12-26 22:15
  [27] TROUGH price= 8050.00 time= 12-29 09:45
  [28] PEAK   price= 8074.00 time= 12-29 11:00
  [29] TROUGH price= 8034.00 time= 12-29 21:15
  [30] PEAK   price= 8088.00 time= 12-29 22:30
  [31] TROUGH price= 8064.00 time= 12-30 09:15
  [32] PEAK   price= 8168.00 time= 12-30 13:45
  [33] TROUGH price= 8130.00 time= 12-30 14:30
  [34] PEAK   price= 8164.00 time= 12-30 21:15
  [35] TROUGH price= 8100.00 time= 12-31 10:15
  [36] PEAK   price= 8130.00 time= 01-05 10:45
  [37] TROUGH price= 8074.00 time= 01-05 13:45 ← A
  [38] PEAK   price= 8278.00 time= 01-07 22:45
  [39] TROUGH price= 8228.00 time= 01-08 22:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(8228.00) > C(8228.00) = False
```
---

### Y — 1h

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8184.00 @ 12-15 09:15 |
| B 价 | 8230.00 @ 12-15 11:00 |
| C 价 | 8228.00 @ 01-08 22:00 |
| 最新价 | 8228.00 |
| 条件判定 | ✅ ✅ ✅ ❌ |
| DB 方向 | LONG (状态: LEG3) |
| DB 重复行 | 否 |
| 极值点数量 | 50 (merge 后: 50) |
| A 索引 | 27 | C 索引 | 49 |

**极值点序列** (swing: 50, merged: 50):
```
  [ 0] PEAK   price= 8298.00 time= 11-12 14:00
  [ 1] TROUGH price= 8240.00 time= 11-12 23:00
  [ 2] PEAK   price= 8332.00 time= 11-13 22:00
  [ 3] TROUGH price= 8246.00 time= 11-14 15:00
  [ 4] PEAK   price= 8284.00 time= 11-14 23:00
  [ 5] TROUGH price= 8224.00 time= 11-17 09:15
  [ 6] PEAK   price= 8308.00 time= 11-17 14:00
  [ 7] TROUGH price= 8268.00 time= 11-17 22:00
  [ 8] PEAK   price= 8402.00 time= 11-18 21:15
  [ 9] TROUGH price= 8140.00 time= 11-21 21:15
  [10] PEAK   price= 8204.00 time= 11-24 10:45
  [11] TROUGH price= 8130.00 time= 11-24 21:15
  [12] PEAK   price= 8194.00 time= 11-25 11:00
  [13] TROUGH price= 8080.00 time= 11-25 22:00
  [14] PEAK   price= 8160.00 time= 11-26 13:45
  [15] TROUGH price= 8134.00 time= 11-26 21:15
  [16] PEAK   price= 8298.00 time= 12-01 09:15
  [17] TROUGH price= 8252.00 time= 12-01 21:15
  [18] PEAK   price= 8312.00 time= 12-02 11:00
  [19] TROUGH price= 8252.00 time= 12-02 21:15
  [20] PEAK   price= 8308.00 time= 12-03 13:45
  [21] TROUGH price= 8222.00 time= 12-04 10:00
  [22] PEAK   price= 8310.00 time= 12-05 21:15
  [23] TROUGH price= 8176.00 time= 12-09 21:15
  [24] PEAK   price= 8250.00 time= 12-10 11:00
  [25] TROUGH price= 8198.00 time= 12-10 14:00
  [26] PEAK   price= 8276.00 time= 12-11 21:15
  [27] TROUGH price= 8184.00 time= 12-15 09:15 ← A
  [28] PEAK   price= 8230.00 time= 12-15 11:00
  [29] TROUGH price= 8090.00 time= 12-17 11:00
  [30] PEAK   price= 8106.00 time= 12-18 09:15
  [31] TROUGH price= 7882.00 time= 12-19 11:00
  [32] PEAK   price= 8028.00 time= 12-22 21:15
  [33] TROUGH price= 7962.00 time= 12-23 09:15
  [34] PEAK   price= 8016.00 time= 12-23 21:15
  [35] TROUGH price= 7980.00 time= 12-24 09:15
  [36] PEAK   price= 8026.00 time= 12-24 10:00
  [37] TROUGH price= 7988.00 time= 12-24 15:00
  [38] PEAK   price= 8016.00 time= 12-25 09:15
  [39] TROUGH price= 7988.00 time= 12-25 10:00
  [40] PEAK   price= 8070.00 time= 12-25 21:15
  [41] TROUGH price= 8038.00 time= 12-26 10:00
  [42] PEAK   price= 8094.00 time= 12-26 22:00
  [43] TROUGH price= 8034.00 time= 12-29 21:15
  [44] PEAK   price= 8168.00 time= 12-30 13:45
  [45] TROUGH price= 8094.00 time= 12-31 14:00
  [46] PEAK   price= 8130.00 time= 01-05 10:45
  [47] TROUGH price= 8074.00 time= 01-05 13:45
  [48] PEAK   price= 8278.00 time= 01-07 22:00
  [49] TROUGH price= 8228.00 time= 01-08 22:00 ← C
```

**失败详情:**
```
  ❌ C4 最新(8228.00) > C(8228.00) = False
```
---

## 📋 完整验证矩阵

| 品种 | 周期 | 方向 | A 价 | B 价 | C 价 | 最新 | 条件 | 判定 | DB 方向 | A 时间 | C 时间 |
|------|------|------|------|------|------|------|------|------|--------|--------|--------|
| A    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| A    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| A    | 1d  | SHORT |  5046.00 |  4694.00 |  4901.00 |  4739.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-23 00:00 | 05-25 00:00 |
| A    | 1w  | LONG  |  4068.00 |  4986.00 |  4550.00 |  4739.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 07-08 00:00 | 03-24 00:00 |
| **A   ** | 15m | SHORT |  4701.00 |  4647.00 |  4668.00 |  4672.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-16 14:30 | 06-18 09:15 |
| A    | 1h  | SHORT |  4746.00 |  4661.00 |  4725.00 |  4672.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-09 10:00 | 06-16 10:00 |
| **A   ** | 1d  | LONG  |  4661.00 |  4774.00 |  4721.00 |  4622.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-09 00:00 | 06-12 09:00 |
| A    | 1w  | SHORT |  4901.00 |  4661.00 |  4796.00 |  4622.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-18 08:00 | 06-11 13:30 |
| AG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| AG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **AG  ** | 1d  | LONG  | 17554.00 | 22134.00 | 17850.00 | 15622.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 04-30 00:00 | 05-20 00:00 |
| **AG  ** | 1w  | LONG  | 15070.00 | 20559.00 | 17554.00 | 15622.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 03-17 00:00 | 04-28 00:00 |
| AG   | 15m | SHORT | 16879.00 | 16477.00 | 16592.00 | 16506.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-17 14:15 | 06-18 13:45 |
| **AG  ** | 1h  | LONG  | 16235.00 | 16564.00 | 16561.00 | 16506.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-09 11:00 | 06-16 10:00 |
| AG   | 1d  | SHORT | 18512.00 | 15107.00 | 17210.00 | 16506.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-02 13:45 | 06-17 13:45 |
| AG   | 1w  | SHORT | 22134.00 | 15107.00 | 17210.00 | 16506.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-11 08:00 | 06-15 09:15 |
| AL   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| AL   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| AL   | 1d  | SHORT | 25675.00 | 24160.00 | 25100.00 | 23905.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-17 00:00 | 05-14 00:00 |
| AL   | 1w  | SHORT | 26185.00 | 23100.00 | 25675.00 | 23905.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-27 00:00 | 04-14 00:00 |
| **AL  ** | 15m | SHORT | 23940.00 | 23830.00 | 23915.00 | 23980.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-18 01:00 | 06-18 10:45 |
| AL   | 1h  | LONG  | 23780.00 | 23950.00 | 23850.00 | 23980.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-16 14:00 | 06-17 14:00 |
| AL   | 1d  | SHORT | 24840.00 | 23825.00 | 24360.00 | 23860.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-02 13:45 | 06-15 09:15 |
| AL   | 1w  | SHORT | 25700.00 | 24075.00 | 24825.00 | 23860.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-13 08:00 | 06-01 09:15 |
| AO   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| AO   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| AO   | 1d  | LONG  |  2685.00 |  2913.00 |  2742.00 |  2898.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-25 00:00 | 06-05 00:00 |
| AO   | 1w  | LONG  |  2685.00 |  2913.00 |  2742.00 |  2898.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-19 00:00 | 06-02 00:00 |
| AP   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| AP   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| AP   | 1d  | SHORT |  9298.00 |  7505.00 |  7715.00 |  7400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 10-30 00:00 | 05-13 00:00 |
| AP   | 1w  | SHORT |  8437.00 |  7738.00 |  7799.00 |  7400.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 07-22 00:00 | 06-02 00:00 |
| AP   | 15m | LONG  |  7651.00 |  7715.00 |  7665.00 |  7682.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 09:15 | 06-18 14:00 |
| AP   | 1h  | SHORT |  7731.00 |  7640.00 |  7711.00 |  7682.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-15 09:15 | 06-16 11:00 |
| AP   | 1d  | SHORT |  7903.00 |  7306.00 |  7731.00 |  7692.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-04 09:15 | 06-15 09:15 |
| AP   | 1w  | SHORT |  8729.00 |  7365.00 |  7903.00 |  7692.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 06-01 09:15 |
| AU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| AU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **AU  ** | 1d  | LONG  |   929.10 |  1074.44 |   996.12 |   919.32 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 03-23 00:00 | 04-30 00:00 |
| AU   | 1w  | SHORT |  1258.72 |   929.10 |  1074.44 |   919.32 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-27 00:00 | 04-14 00:00 |
| AU   | 15m | SHORT |   949.70 |   943.54 |   943.58 |   937.24 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-17 22:45 | 06-18 10:15 |
| AU   | 1h  | SHORT |   948.66 |   939.12 |   945.82 |   937.24 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-16 21:15 | 06-17 09:15 |
| AU   | 1d  | SHORT |   987.96 |   934.80 |   954.50 |   937.24 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-05 00:00 | 06-10 00:00 |
| AU   | 1w  | SHORT |  1048.82 |   885.48 |   953.46 |   937.24 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-04 08:00 | 06-15 09:15 |
| B    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| B    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| B    | 1d  | SHORT |  3994.00 |  3558.00 |  3711.00 |  3482.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-13 00:00 | 04-22 00:00 |
| **B   ** | 1w  | LONG  |  3416.00 |  3994.00 |  3558.00 |  3482.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 01-13 00:00 | 04-14 00:00 |
| **B   ** | 15m | LONG  |  3541.00 |  3560.00 |  3545.00 |  3537.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-17 14:45 | 06-17 22:15 |
| B    | 1h  | SHORT |  3568.00 |  3543.00 |  3561.00 |  3537.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-27 10:00 | 06-17 23:00 |
| B    | 1d  | SHORT |  3611.00 |  3448.00 |  3528.00 |  3524.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-03 00:00 | 06-11 13:30 |
| B    | 1w  | SHORT |  3711.00 |  3448.00 |  3561.00 |  3524.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-20 08:00 | 06-15 09:15 |
| BR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| BR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| BR   | 1d  | SHORT | 16680.00 | 15110.00 | 16320.00 | 12845.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-30 00:00 | 05-18 00:00 |
| **BR  ** | 1w  | LONG  | 12870.00 | 15215.00 | 15115.00 | 12845.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 12-24 00:00 | 04-07 00:00 |
| BU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| BU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| BU   | 1d  | LONG  |  3530.00 |  4747.00 |  3950.00 |  4417.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-30 00:00 | 04-08 00:00 |
| BU   | 1w  | LONG  |  3251.00 |  4747.00 |  3950.00 |  4417.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-10 00:00 | 04-07 00:00 |
| BU   | 15m | SHORT |  4007.00 |  3965.00 |  4003.00 |  3943.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 22:00 | 06-17 23:00 |
| BU   | 1h  | SHORT |  4163.00 |  4073.00 |  4114.00 |  3943.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-26 09:15 | 06-16 15:00 |
| **BU  ** | 1d  | LONG  |  4197.00 |  4434.00 |  4242.00 |  3941.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 05-14 09:15 | 06-03 00:00 |
| **BU  ** | 1w  | LONG  |  3773.00 |  4434.00 |  4093.00 |  3941.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 04-06 08:00 | 05-25 09:15 |
| C    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| C    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| C    | 1d  | SHORT |  2443.00 |  2361.00 |  2416.00 |  2335.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-09 00:00 | 03-23 00:00 |
| **C   ** | 1w  | LONG  |  2307.00 |  2420.00 |  2337.00 |  2335.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 05-20 00:00 | 04-07 00:00 |
| **C   ** | 15m | SHORT |  2336.00 |  2321.00 |  2334.00 |  2337.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-17 21:15 | 06-18 10:15 |
| **C   ** | 1h  | SHORT |  2353.00 |  2318.00 |  2335.00 |  2337.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-12 13:30 | 06-16 21:15 |
| C    | 1d  | LONG  |  2291.00 |  2355.00 |  2317.00 |  2333.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-04 00:00 | 06-15 00:00 |
| C    | 1w  | SHORT |  2445.00 |  2291.00 |  2355.00 |  2333.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-20 08:00 | 06-08 09:15 |
| CF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| CF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **CF  ** | 1d  | LONG  | 15170.00 | 16955.00 | 15855.00 | 15675.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 04-03 00:00 | 05-22 00:00 |
| **CF  ** | 1w  | LONG  | 15035.00 | 16955.00 | 15855.00 | 15675.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 03-17 00:00 | 05-19 00:00 |
| **CF  ** | 15m | LONG  | 16005.00 | 16110.00 | 16015.00 | 16010.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-17 15:00 | 06-17 23:00 |
| CF   | 1h  | SHORT | 16095.00 | 15970.00 | 16090.00 | 16010.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-28 09:15 | 06-16 22:00 |
| **CF  ** | 1d  | SHORT | 16440.00 | 15590.00 | 15840.00 | 16010.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-03 00:00 | 06-15 00:00 |
| CF   | 1w  | SHORT | 16385.00 | 15590.00 | 16110.00 | 16010.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-01 09:15 | 06-15 09:15 |
| CJ   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| CJ   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **CJ  ** | 1d  | LONG  |  8720.00 |  9265.00 |  8880.00 |  8880.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 12-23 00:00 | 05-22 00:00 |
| **CJ  ** | 1w  | LONG  |  8610.00 |  9370.00 |  8880.00 |  8880.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 02-10 00:00 | 05-19 00:00 |
| **CJ  ** | 15m | SHORT |  8770.00 |  8595.00 |  8625.00 |  8625.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-17 13:45 | 06-18 13:45 |
| CJ   | 1h  | SHORT |  8955.00 |  8700.00 |  8800.00 |  8625.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 11:00 | 06-16 14:00 |
| **CJ  ** | 1d  | LONG  |  8505.00 |  8960.00 |  8700.00 |  8615.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-10 00:00 | 06-16 09:15 |
| CJ   | 1w  | SHORT |  9705.00 |  8720.00 |  9440.00 |  8615.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-09 09:15 | 05-11 08:00 |
| CS   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| CS   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| CS   | 1d  | LONG  |  2503.00 |  2766.00 |  2705.00 |  2714.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-03 00:00 | 03-18 00:00 |
| CS   | 1w  | LONG  |  2503.00 |  2842.00 |  2641.00 |  2714.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-03 00:00 | 05-26 00:00 |
| CS   | 15m | SHORT |  2711.00 |  2697.00 |  2708.00 |  2698.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 21:45 | 06-18 09:45 |
| **CS  ** | 1h  | LONG  |  2688.00 |  2707.00 |  2700.00 |  2698.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-16 09:15 | 06-17 14:00 |
| CS   | 1d  | SHORT |  2739.00 |  2705.00 |  2738.00 |  2700.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-09 13:45 | 06-11 13:30 |
| CS   | 1w  | SHORT |  2787.00 |  2718.00 |  2739.00 |  2700.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 06-08 09:15 |
| CU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| CU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| CU   | 1d  | SHORT | 108900.00 | 103000.00 | 107420.00 | 104110.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-13 00:00 | 06-03 00:00 |
| CU   | 1w  | LONG  | 77700.00 | 114160.00 | 91500.00 | 104110.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 07-15 00:00 | 03-17 00:00 |
| CU   | 15m | SHORT | 105010.00 | 104250.00 | 104850.00 | 104780.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-12 14:15 | 06-18 13:45 |
| **CU  ** | 1h  | LONG  | 104800.00 | 106800.00 | 104980.00 | 104780.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-04 14:00 | 06-17 09:15 |
| CU   | 1d  | LONG  | 102640.00 | 106000.00 | 104450.00 | 104590.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-11 10:30 | 06-16 13:45 |
| CU   | 1w  | LONG  | 102640.00 | 106000.00 | 104430.00 | 104590.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-08 09:15 | 06-16 09:15 |
| EB   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EB   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EB   | 1d  | SHORT | 11132.00 |  9300.00 | 10098.00 |  8476.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-23 00:00 | 04-29 00:00 |
| **EB  ** | 1w  | LONG  |  8804.00 |  9383.00 |  9300.00 |  8476.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 07-23 00:00 | 04-14 00:00 |
| **EB  ** | 15m | LONG  |  5180.00 |  5700.00 |  5421.00 |  5380.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 04-20 13:45 | 05-06 11:30 |
| EB   | 1h  | LONG  |  5077.00 |  5220.00 |  5138.00 |  5380.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-29 14:00 | 04-30 14:00 |
| **EB  ** | 1d  | SHORT |  5382.00 |  4567.00 |  5088.00 |  5380.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 04-17 09:15 | 04-24 09:15 |
| EB   | 1w  | SHORT |  7078.00 |  4340.00 |  5609.00 |  5380.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 02-17 09:15 | 04-13 09:15 |
| EB   | 15m | LONG  |  5240.00 |  5465.00 |  5403.00 |  5883.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-31 21:15 | 09-02 14:30 |
| EB   | 1h  | LONG  |  5240.00 |  5465.00 |  5403.00 |  5883.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-31 21:15 | 09-02 14:30 |
| EB   | 1d  | LONG  |  5092.00 |  5438.00 |  5240.00 |  5883.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-18 13:45 | 08-31 13:45 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EB   | 15m | LONG  |  6200.00 |  6400.00 |  6350.00 |  6606.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-04 11:00 | 01-05 14:30 |
| EB   | 1h  | LONG  |  6200.00 |  6400.00 |  6350.00 |  6606.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-04 11:00 | 01-05 14:30 |
| EB   | 1d  | SHORT |  6924.00 |  6570.00 |  6638.00 |  6606.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-15 13:45 | 12-25 09:15 |
| EB   | 1w  | SHORT |  8433.00 |  6021.00 |  6670.00 |  6606.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-16 09:15 | 01-04 09:15 |
| **EB  ** | 15m | LONG  |  9370.00 | 10277.00 | 10026.00 |  9760.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-21 11:30 | 05-12 10:00 |
| **EB  ** | 1h  | LONG  |  9070.00 | 10277.00 | 10026.00 |  9760.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 05-06 09:15 | 05-12 10:00 |
| **EB  ** | 1d  | LONG  |  9046.00 | 10469.00 |  9837.00 |  9760.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-27 10:45 | 05-14 14:00 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EB   | 15m | LONG  |  8713.00 |  8890.00 |  8795.00 |  9230.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-30 21:45 | 08-31 15:00 |
| EB   | 1h  | LONG  |  8475.00 |  8837.00 |  8713.00 |  9230.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-26 10:00 | 08-30 21:15 |
| EB   | 1d  | LONG  |  8360.00 |  8741.00 |  8449.00 |  9230.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-19 13:45 | 08-26 13:45 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EB   | 15m | SHORT |  9300.00 |  8153.00 |  8756.00 |  8550.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-07 21:30 | 01-17 10:45 |
| EB   | 1h  | SHORT |  9300.00 |  8153.00 |  8756.00 |  8550.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-07 21:15 | 01-17 10:45 |
| EB   | 1d  | LONG  |  7696.00 |  8336.00 |  8115.00 |  8550.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-22 13:45 | 12-27 13:45 |
| EB   | 1w  | LONG  |  7466.00 |  9300.00 |  8153.00 |  8550.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-29 09:15 | 01-10 14:15 |
| EB   | 15m | LONG  |  9706.00 | 10147.00 | 10006.00 | 10100.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-10 10:15 | 05-16 14:15 |
| EB   | 1h  | SHORT | 10689.00 |  9706.00 | 10147.00 | 10100.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-05 09:15 | 05-13 15:00 |
| EB   | 1d  | LONG  |  9612.00 | 10130.00 |  9706.00 | 10100.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-31 13:45 | 05-10 09:30 |
| **EB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **EB  ** | 15m | LONG  |  9089.00 |  9688.00 |  9570.00 |  9350.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 09-08 09:45 | 09-20 11:30 |
| EB   | 1h  | LONG  |  8701.00 |  9990.00 |  8895.00 |  9350.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-13 21:15 | 09-23 14:15 |
| EB   | 1d  | LONG  |  8335.00 |  9480.00 |  9050.00 |  9350.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-10 13:45 | 09-07 13:45 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EB   | 15m | LONG  |  8271.00 |  8316.00 |  8279.00 |  8680.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-28 14:15 | 12-30 10:45 |
| **EB  ** | 1h  | SHORT |  8348.00 |  8154.00 |  8327.00 |  8680.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-22 10:00 | 12-28 11:00 |
| EB   | 1d  | LONG  |  8154.00 |  8380.00 |  8192.00 |  8680.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-23 13:45 | 12-29 10:45 |
| **EB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **EB  ** | 15m | LONG  |  7950.00 |  8298.00 |  8170.00 |  7770.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 05-04 22:45 | 05-09 09:15 |
| **EB  ** | 1h  | LONG  |  7944.00 |  8027.00 |  7950.00 |  7770.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 05-04 09:15 | 05-04 22:00 |
| EB   | 1d  | SHORT |  8775.00 |  7944.00 |  8298.00 |  7770.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-14 13:45 | 05-08 13:45 |
| EB   | 1w  | SHORT |  8775.00 |  7944.00 |  8355.00 |  7770.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-10 09:15 | 05-16 09:15 |
| **EB  ** | 15m | LONG  |  9064.00 |  9500.00 |  9380.00 |  9047.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 09-06 09:15 | 09-07 11:30 |
| **EB  ** | 1h  | LONG  |  8898.00 |  9500.00 |  9380.00 |  9047.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 09-04 14:30 | 09-07 11:30 |
| **EB  ** | 1d  | LONG  |  8502.00 |  9500.00 |  9278.00 |  9047.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-22 13:45 | 09-08 14:15 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **EB  ** | 15m | SHORT |  8485.00 |  8393.00 |  8435.00 |  9000.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-28 10:00 | 12-28 13:45 |
| **EB  ** | 1h  | SHORT |  8570.00 |  8430.00 |  8527.00 |  9000.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-20 22:00 | 01-02 14:00 |
| EB   | 1d  | LONG  |  7760.00 |  8661.00 |  8200.00 |  9000.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-05 09:15 | 01-02 09:15 |
| **EB  ** | 1w  | SHORT |  8818.00 |  7760.00 |  8661.00 |  9000.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 11-13 09:15 | 12-25 09:15 |
| EB   | 15m | LONG  |  9181.00 | 10130.00 |  9512.00 |  9549.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-13 09:45 | 05-23 10:15 |
| EB   | 1h  | LONG  |  9181.00 | 10130.00 |  9512.00 |  9549.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-13 09:15 | 05-23 10:15 |
| EB   | 1d  | SHORT |  9780.00 |  9452.00 |  9610.00 |  9549.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-19 09:15 | 04-25 10:45 |
| **EB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| EB   | 15m | SHORT |  9305.00 |  9080.00 |  9138.00 |  8890.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-26 09:15 | 09-05 22:45 |
| EB   | 1h  | SHORT |  9355.00 |  9041.00 |  9092.00 |  8890.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-27 14:00 | 09-06 22:30 |
| **EB  ** | 1d  | LONG  |  9105.00 |  9400.00 |  9270.00 |  8890.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-22 13:45 | 08-28 10:45 |
| **EB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| EB   | 15m | LONG  |  8083.00 |  8141.00 |  8091.00 |  8510.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-31 10:45 | 12-31 15:00 |
| EB   | 1h  | LONG  |  8083.00 |  8325.00 |  8118.00 |  8510.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-31 10:45 | 01-08 22:30 |
| **EB  ** | 1d  | SHORT |  8574.00 |  8048.00 |  8325.00 |  8510.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-19 13:45 | 01-03 10:45 |
| **EB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| EB   | 15m | LONG  |  7273.00 |  7596.00 |  7462.00 |  7680.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-24 22:45 | 05-13 10:00 |
| EB   | 1h  | LONG  |  7100.00 |  7596.00 |  7462.00 |  7680.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-08 14:00 | 05-13 10:00 |
| **EB  ** | 1d  | SHORT |  8008.00 |  6831.00 |  7543.00 |  7680.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-01 13:45 | 04-14 09:15 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **EB  ** | 15m | SHORT |  7042.00 |  6694.00 |  6990.00 |  6990.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 09-05 13:45 | 09-15 09:30 |
| **EB  ** | 1h  | SHORT |  7042.00 |  6694.00 |  6990.00 |  6990.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 09-05 13:45 | 09-15 09:30 |
| EB   | 1d  | SHORT |  7360.00 |  6865.00 |  7042.00 |  6990.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-12 13:45 | 09-05 13:45 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EB   | 15m | LONG  |  6681.00 |  6820.00 |  6775.00 |  6982.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-08 14:15 | 01-09 22:00 |
| EB   | 1h  | LONG  |  6586.00 |  6728.00 |  6679.00 |  6982.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-05 14:00 | 01-07 09:15 |
| EB   | 1d  | LONG  |  6454.00 |  6675.00 |  6586.00 |  6982.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-01 13:45 | 01-05 13:45 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EB   | 15m | SHORT |  9905.00 |  9757.00 |  9834.00 |  9108.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-22 21:15 | 05-11 10:45 |
| EB   | 1h  | SHORT |  9903.00 |  9560.00 |  9834.00 |  9108.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-20 13:45 | 05-11 10:45 |
| EB   | 1d  | SHORT | 10553.00 |  9555.00 | 10060.00 |  9108.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-09 13:45 | 04-15 10:45 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EB   | 15m | SHORT |  7881.00 |  7816.00 |  7877.00 |  7790.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 21:15 | 06-17 22:30 |
| EB   | 1h  | SHORT |  8208.00 |  7742.00 |  7881.00 |  7790.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-15 14:00 | 06-17 21:15 |
| EB   | 1d  | SHORT |  8995.00 |  8415.00 |  8685.00 |  7746.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-03 00:00 | 06-11 13:30 |
| EB   | 1w  | SHORT | 10679.00 |  9125.00 |  9938.00 |  7746.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-23 08:00 | 04-27 08:00 |
| EB   | 15m | LONG  |  8213.00 |  8321.00 |  8252.00 |  8278.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-12 09:45 | 06-12 21:15 |
| EB   | 1h  | LONG  |  8205.00 |  8431.00 |  8213.00 |  8278.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-10 14:00 | 06-12 09:15 |
| EB   | 1d  | SHORT |  8692.00 |  8273.00 |  8597.00 |  8278.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-03 10:45 | 06-08 13:45 |
| EB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| EG   | 1d  | SHORT |  5814.00 |  4613.00 |  5211.00 |  4544.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-08 00:00 | 05-06 00:00 |
| EG   | 1w  | SHORT |  5814.00 |  4613.00 |  5211.00 |  4544.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-07 00:00 | 05-06 00:00 |
| EG   | 15m | LONG  |  4152.00 |  4263.00 |  4161.00 |  4209.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 13:45 | 06-18 10:00 |
| EG   | 1h  | SHORT |  4341.00 |  4152.00 |  4263.00 |  4209.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 14:00 | 06-17 21:15 |
| EG   | 1d  | SHORT |  4855.00 |  4335.00 |  4661.00 |  4185.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-18 09:15 | 06-08 00:00 |
| EG   | 1w  | SHORT |  5474.00 |  4693.00 |  5211.00 |  4185.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 05-04 08:00 |
| FG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| FG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| FG   | 1d  | SHORT |  1163.00 |   954.00 |  1104.00 |   989.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-09 00:00 | 04-23 00:00 |
| FG   | 1w  | SHORT |  1163.00 |   954.00 |  1104.00 |   989.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-03 00:00 | 04-21 00:00 |
| FG   | 15m | SHORT |  1007.00 |   987.00 |   993.00 |   978.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 10:00 | 06-18 09:45 |
| **FG  ** | 1h  | LONG  |   984.00 |  1020.00 |   999.00 |   978.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-12 14:00 | 06-16 14:00 |
| FG   | 1d  | SHORT |  1061.00 |   982.00 |  1020.00 |   985.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-29 13:45 | 06-15 00:00 |
| **FG  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | LONG  |          — |          — |
| FU   | 15m | SHORT |  3920.00 |  3855.00 |  3904.00 |  3888.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-01 14:30 | 06-02 11:30 |
| FU   | 1h  | LONG  |  3690.00 |  3860.00 |  3735.00 |  3888.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-27 22:00 | 05-29 21:15 |
| FU   | 1d  | LONG  |  3597.00 |  4068.00 |  3700.00 |  3888.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-02 09:15 | 05-08 00:00 |
| FU   | 1w  | SHORT |  4447.00 |  3408.00 |  4107.00 |  3888.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 04-27 08:00 |
| HC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| HC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| HC   | 1d  | LONG  |  3181.00 |  3340.00 |  3261.00 |  3380.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-24 00:00 | 04-10 00:00 |
| HC   | 1w  | LONG  |  3194.00 |  3348.00 |  3261.00 |  3380.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-09 00:00 | 04-07 00:00 |
| HC   | 15m | SHORT |  3354.00 |  3345.00 |  3350.00 |  3329.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-11 13:30 | 06-17 22:15 |
| HC   | 1h  | SHORT |  3389.00 |  3375.00 |  3377.00 |  3329.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-15 10:00 | 06-16 14:00 |
| HC   | 1d  | SHORT |  3443.00 |  3339.00 |  3412.00 |  3325.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-25 09:15 | 06-01 13:45 |
| HC   | 1w  | LONG  |  3259.00 |  3504.00 |  3319.00 |  3325.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-06 08:00 | 06-15 09:15 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **I   ** | 1d  | LONG  |   760.00 |   820.00 |   777.00 |   771.50 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-20 00:00 | 05-27 00:00 |
| I    | 1w  | LONG  |   748.00 |   831.50 |   748.50 |   771.50 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-09 00:00 | 04-07 00:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | LONG  |   599.50 |   864.50 |   815.00 |   865.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-01 08:00 | 12-20 08:00 |
| **I   ** | 1w  | SHORT |   780.50 |   624.00 |   755.00 |   865.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 02-07 08:00 | 08-08 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | SHORT |   890.00 |   828.50 |   867.50 |   839.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-30 08:00 | 05-09 08:00 |
| **I   ** | 1w  | LONG  |   623.50 |   936.00 |   844.00 |   839.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-29 08:00 | 03-20 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | LONG  |   675.50 |   841.00 |   793.50 |   940.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-05 08:00 | 07-10 08:00 |
| **I   ** | 1w  | SHORT |   884.00 |   665.50 |   875.50 |   940.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 03-13 08:00 | 07-24 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | LONG  |   941.00 |  1026.00 |   990.00 |  1030.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-28 08:00 | 12-18 08:00 |
| I    | 1w  | LONG  |   757.50 |   836.50 |   812.50 |  1030.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-13 08:00 | 10-09 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | SHORT |   975.50 |   915.00 |   931.00 |   895.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-08 08:00 | 04-25 08:00 |
| I    | 1w  | LONG  |   751.00 |   931.00 |   872.50 |   895.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-01 08:00 | 04-29 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | SHORT |   819.00 |   728.00 |   804.50 |   715.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-25 08:00 | 08-05 08:00 |
| I    | 1w  | SHORT |   870.00 |   700.00 |   786.50 |   715.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 07-01 08:00 | 08-26 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | LONG  |   734.00 |   833.00 |   750.50 |   771.50 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-18 08:00 | 01-08 08:00 |
| I    | 1w  | LONG  |   734.00 |   833.00 |   750.50 |   771.50 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-18 08:00 | 01-06 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | LONG  |   711.50 |   780.00 |   754.00 |   780.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-09 08:00 | 05-09 08:00 |
| I    | 1w  | SHORT |   844.00 |   753.50 |   797.00 |   780.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 02-17 08:00 | 03-31 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | LONG  |   689.50 |   835.50 |   774.00 |   816.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-16 08:00 | 07-31 08:00 |
| I    | 1w  | LONG  |   689.50 |   835.50 |   781.00 |   816.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-16 08:00 | 08-18 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **I   ** | 1d  | SHORT |   820.00 |   760.00 |   810.50 |   832.50 | ✅ ✅ ✅ ❌ | ❌ | —     | 09-22 08:00 | 10-30 08:00 |
| **I   ** | 1w  | SHORT |   820.00 |   756.00 |   804.50 |   832.50 | ✅ ✅ ✅ ❌ | ❌ | —     | 09-22 08:00 | 12-01 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | LONG  |   748.00 |   831.50 |   769.50 |   831.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-15 08:00 | 04-14 08:00 |
| I    | 1w  | LONG  |   748.00 |   831.50 |   769.50 |   831.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-15 08:00 | 04-13 08:00 |
| I    | 15m | SHORT |   764.50 |   743.00 |   748.50 |   747.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-08 22:00 | 06-17 23:00 |
| I    | 1h  | SHORT |   765.50 |   743.00 |   749.50 |   747.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-09 21:15 | 06-18 13:45 |
| I    | 1d  | SHORT |   787.00 |   756.00 |   778.50 |   745.50 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-02 08:00 | 06-10 00:00 |
| I    | 1w  | LONG  |   715.00 |   808.50 |   721.00 |   745.50 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-10 08:00 | 02-24 08:00 |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| I    | 1d  | LONG  |   711.50 |   779.00 |   731.50 |   763.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-24 08:00 | 04-10 08:00 |
| I    | 1w  | LONG  |   711.50 |   779.00 |   731.50 |   763.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-24 08:00 | 04-07 08:00 |
| IF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| IF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| IF   | 1d  | LONG  |  4555.60 |  4768.00 |  4735.00 |  4862.80 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-02 00:00 | 05-19 00:00 |
| IF   | 1w  | LONG  |  4307.20 |  4995.00 |  4735.00 |  4862.80 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-17 00:00 | 05-19 00:00 |
| IH   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| IH   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| IH   | 1d  | LONG  |  2750.80 |  3041.80 |  2791.20 |  2899.80 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-23 00:00 | 06-08 00:00 |
| IH   | 1w  | SHORT |  3181.20 |  2750.80 |  3041.80 |  2899.80 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-13 00:00 | 05-12 00:00 |
| IM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| IM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| IM   | 1d  | LONG  |  7120.20 |  8337.00 |  8056.00 |  8510.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-23 00:00 | 04-28 00:00 |
| IM   | 1w  | LONG  |  7120.20 |  8908.80 |  7962.00 |  8510.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-17 00:00 | 06-02 00:00 |
| J    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| J    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| J    | 1d  | LONG  |  1717.00 |  1843.50 |  1792.50 |  1983.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-19 00:00 | 04-28 00:00 |
| J    | 1w  | LONG  |  1673.00 |  1818.00 |  1719.00 |  1983.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-07 00:00 | 05-19 00:00 |
| J    | 15m | SHORT |  2084.50 |  2035.00 |  2067.50 |  2019.50 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 14:45 | 06-17 22:30 |
| J    | 1h  | SHORT |  2126.00 |  2055.00 |  2098.00 |  2019.50 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-12 11:00 | 06-17 11:00 |
| J    | 1d  | LONG  |  1789.00 |  1835.50 |  1821.00 |  1986.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-13 09:15 | 05-26 13:45 |
| J    | 1w  | LONG  |  1719.00 |  2130.50 |  1983.50 |  1986.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-18 08:00 | 06-15 09:15 |
| JD   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| JD   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| JD   | 1d  | LONG  |  2885.00 |  3517.00 |  3356.00 |  4748.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-05 00:00 | 03-19 00:00 |
| **JD  ** | 1w  | SHORT |  3688.00 |  3500.00 |  3530.00 |  4748.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 11-05 00:00 | 03-24 00:00 |
| **JD  ** | 15m | LONG  |  4271.00 |  4307.00 |  4278.00 |  4168.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-17 09:15 | 06-17 13:45 |
| **JD  ** | 1h  | LONG  |  4215.00 |  4281.00 |  4271.00 |  4168.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-12 09:00 | 06-17 09:15 |
| JD   | 1d  | SHORT |  4713.00 |  4185.00 |  4307.00 |  4186.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-15 00:00 | 06-17 10:45 |
| JD   | 1w  | LONG  |  3320.00 |  4793.00 |  4152.00 |  4186.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-06 08:00 | 06-15 09:15 |
| JM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| JM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| JM   | 1d  | LONG  |  1122.00 |  1212.00 |  1152.50 |  1363.50 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-16 00:00 | 05-25 00:00 |
| JM   | 1w  | LONG  |  1063.50 |  1294.00 |  1152.50 |  1363.50 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 02-24 00:00 | 05-19 00:00 |
| JM   | 15m | SHORT |  1362.00 |  1338.00 |  1348.00 |  1274.50 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 11:00 | 06-17 14:45 |
| JM   | 1h  | SHORT |  1408.00 |  1360.50 |  1379.00 |  1274.50 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 14:15 | 06-15 09:15 |
| JM   | 1d  | SHORT |  1486.50 |  1322.50 |  1408.00 |  1264.50 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-05 13:45 | 06-12 10:30 |
| JM   | 1w  | LONG  |  1152.50 |  1486.50 |  1259.50 |  1264.50 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-18 08:00 | 06-15 09:15 |
| L    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 1d  | LONG  |  7634.00 |  7746.00 |  7655.00 |  7875.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-21 00:00 | 05-28 00:00 |
| L    | 1w  | SHORT |  8335.00 |  8057.00 |  8149.00 |  7875.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-23 00:00 | 06-02 00:00 |
| L    | 15m | SHORT |  7295.00 |  7210.00 |  7290.00 |  7240.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-06 11:30 | 01-13 15:00 |
| L    | 1h  | SHORT |  7380.00 |  7160.00 |  7290.00 |  7240.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-08 09:15 | 01-13 15:00 |
| L    | 1d  | LONG  |  7085.00 |  7380.00 |  7160.00 |  7240.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-31 13:45 | 01-09 13:45 |
| **L   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| L    | 15m | SHORT |  6580.00 |  6400.00 |  6450.00 |  6200.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-07 09:30 | 05-07 22:15 |
| L    | 1h  | SHORT |  6580.00 |  6155.00 |  6545.00 |  6200.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-07 09:15 | 05-14 11:00 |
| L    | 1d  | SHORT |  6580.00 |  6155.00 |  6545.00 |  6200.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-07 09:15 | 05-14 11:00 |
| L    | 1w  | SHORT |  7045.00 |  5350.00 |  6660.00 |  6200.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 02-17 09:15 | 04-13 09:15 |
| L    | 15m | SHORT |  7840.00 |  7570.00 |  7665.00 |  7330.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-02 14:30 | 09-03 21:30 |
| L    | 1h  | SHORT |  7840.00 |  7570.00 |  7665.00 |  7330.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-02 14:00 | 09-03 21:15 |
| **L   ** | 1d  | SHORT |  7310.00 |  6935.00 |  7210.00 |  7330.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 08-04 13:45 | 08-20 13:45 |
| **L   ** | 1w  | LONG  |  6905.00 |  7840.00 |  7330.00 |  7330.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 07-20 09:15 | 09-07 09:15 |
| L    | 15m | SHORT |  7735.00 |  7650.00 |  7690.00 |  7500.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-04 10:15 | 01-12 10:45 |
| L    | 1h  | SHORT |  7950.00 |  7780.00 |  7875.00 |  7500.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-05 21:15 | 01-07 14:15 |
| L    | 1d  | SHORT |  8200.00 |  7700.00 |  7990.00 |  7500.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-11 13:45 | 12-21 09:15 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 15m | SHORT |  8610.00 |  8535.00 |  8580.00 |  7920.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-07 13:45 | 05-10 09:30 |
| **L   ** | 1h  | LONG  |  8250.00 |  8610.00 |  8350.00 |  7920.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-30 14:00 | 05-11 10:00 |
| L    | 1d  | SHORT |  8810.00 |  8410.00 |  8465.00 |  7920.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-26 13:45 | 04-16 09:15 |
| L    | 1w  | SHORT |  8905.00 |  8095.00 |  8610.00 |  7920.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-06 09:15 | 05-06 09:15 |
| L    | 15m | LONG  |  8115.00 |  8405.00 |  8300.00 |  8545.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-31 09:30 | 09-06 11:30 |
| L    | 1h  | LONG  |  8315.00 |  8500.00 |  8370.00 |  8545.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 07-21 10:45 | 09-07 21:15 |
| **L   ** | 1d  | SHORT |  8295.00 |  8085.00 |  8250.00 |  8545.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-23 13:45 | 08-30 09:15 |
| **L   ** | 1w  | SHORT |  8500.00 |  7980.00 |  8435.00 |  8545.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 07-19 09:15 | 08-16 09:15 |
| L    | 15m | SHORT |  8830.00 |  8755.00 |  8818.00 |  8800.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-12 21:45 | 01-13 14:45 |
| L    | 1h  | LONG  |  8577.00 |  8830.00 |  8755.00 |  8800.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-10 21:30 | 01-13 11:15 |
| L    | 1d  | SHORT |  8880.00 |  8577.00 |  8830.00 |  8800.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-07 10:45 | 01-12 14:30 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 15m | LONG  |  8589.00 |  8700.00 |  8602.00 |  8663.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-10 21:30 | 05-16 10:45 |
| L    | 1h  | SHORT |  8737.00 |  8670.00 |  8700.00 |  8663.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-28 09:15 | 05-11 22:00 |
| L    | 1d  | SHORT |  8980.00 |  8531.00 |  8700.00 |  8663.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-05 13:45 | 05-11 14:30 |
| **L   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| L    | 15m | LONG  |  7870.00 |  8150.00 |  8050.00 |  8400.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-02 14:45 | 09-05 21:15 |
| L    | 1h  | LONG  |  8037.00 |  8110.00 |  8050.00 |  8400.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-03 09:15 | 09-05 21:15 |
| **L   ** | 1d  | SHORT |  7979.00 |  7755.00 |  7919.00 |  8400.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-08 13:45 | 08-30 09:15 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 15m | LONG  |  7959.00 |  8110.00 |  8093.00 |  8278.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-11 09:30 | 01-12 23:00 |
| L    | 1h  | LONG  |  8066.00 |  8139.00 |  8093.00 |  8278.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-27 21:15 | 01-12 23:00 |
| **L   ** | 1d  | SHORT |  8278.00 |  8088.00 |  8261.00 |  8278.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-12 13:45 | 12-15 13:45 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 15m | SHORT |  8335.00 |  8100.00 |  8196.00 |  8020.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-28 14:45 | 05-05 14:30 |
| L    | 1h  | SHORT |  8305.00 |  8100.00 |  8196.00 |  8020.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-25 15:00 | 05-05 14:00 |
| L    | 1d  | SHORT |  8206.00 |  8100.00 |  8200.00 |  8020.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-13 09:15 | 05-08 14:15 |
| **L   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| L    | 15m | LONG  |  8280.00 |  8500.00 |  8330.00 |  8337.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-08 11:30 | 09-12 10:45 |
| **L   ** | 1h  | LONG  |  8369.00 |  8460.00 |  8400.00 |  8337.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 09-04 21:15 | 09-05 14:15 |
| L    | 1d  | LONG  |  8058.00 |  8468.00 |  8225.00 |  8337.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-17 09:15 | 08-29 10:45 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 15m | SHORT |  8013.00 |  7800.00 |  7936.00 |  7920.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-08 09:15 | 01-11 21:15 |
| L    | 1h  | SHORT |  8203.00 |  7761.00 |  7936.00 |  7920.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-21 14:00 | 01-11 21:15 |
| L    | 1d  | SHORT |  8253.00 |  8012.00 |  8232.00 |  7920.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-10 09:15 | 11-16 13:45 |
| **L   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| L    | 15m | SHORT |  8482.00 |  8462.00 |  8479.00 |  8350.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-29 14:15 | 05-08 09:45 |
| L    | 1h  | SHORT |  8489.00 |  8463.00 |  8479.00 |  8350.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-29 22:00 | 05-08 09:15 |
| **L   ** | 1d  | LONG  |  8346.00 |  8479.00 |  8350.00 |  8350.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 05-06 14:15 | 05-09 13:45 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **L   ** | 15m | LONG  |  8137.00 |  8175.00 |  8170.00 |  7660.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 09-03 10:15 | 09-05 13:45 |
| **L   ** | 1h  | LONG  |  8050.00 |  8192.00 |  8080.00 |  7660.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 09-04 10:45 | 09-04 23:00 |
| L    | 1d  | SHORT |  8220.00 |  8086.00 |  8199.00 |  7660.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-15 13:45 | 08-21 13:45 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 15m | SHORT |  8541.00 |  8350.00 |  8441.00 |  8200.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-31 09:30 | 01-07 21:15 |
| L    | 1h  | SHORT |  8465.00 |  8422.00 |  8450.00 |  8200.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-25 10:45 | 01-13 09:30 |
| L    | 1d  | SHORT |  8580.00 |  8350.00 |  8450.00 |  8200.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-03 13:45 | 01-13 09:30 |
| **L   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **L   ** | 15m | LONG  |  7322.00 |  7474.00 |  7453.00 |  7330.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-29 11:15 | 05-14 10:45 |
| **L   ** | 1h  | SHORT |  7348.00 |  7291.00 |  7305.00 |  7330.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-18 09:15 | 05-07 09:15 |
| L    | 1d  | LONG  |  7266.00 |  7376.00 |  7306.00 |  7330.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-16 13:45 | 04-22 13:45 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **L   ** | 15m | LONG  |  7027.00 |  7176.00 |  7122.00 |  7050.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 09-08 22:15 | 09-11 10:45 |
| L    | 1h  | SHORT |  7199.00 |  7138.00 |  7176.00 |  7050.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-05 14:00 | 09-10 14:30 |
| L    | 1d  | SHORT |  7353.00 |  7209.00 |  7230.00 |  7050.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-12 10:45 | 09-03 09:15 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 15m | LONG  |  6451.00 |  6676.00 |  6482.00 |  6520.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-12 22:30 | 01-15 21:45 |
| L    | 1h  | LONG  |  6460.00 |  6589.00 |  6482.00 |  6520.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-12 14:00 | 01-15 21:45 |
| **L   ** | 1d  | SHORT |  6838.00 |  6172.00 |  6387.00 |  6520.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 12-02 13:45 | 12-24 13:45 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 15m | SHORT |  8688.00 |  8090.00 |  8123.00 |  8091.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-18 09:15 | 05-19 09:30 |
| **L   ** | 1h  | LONG  |  8150.00 |  8216.00 |  8198.00 |  8091.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 04-23 14:00 | 05-11 21:45 |
| **L   ** | 1d  | LONG  |  8044.00 |  8233.00 |  8111.00 |  8091.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 04-17 13:45 | 04-24 13:45 |
| L    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| L    | 15m | SHORT |  7514.00 |  7330.00 |  7373.00 |  7206.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 22:00 | 06-17 23:00 |
| L    | 1h  | SHORT |  7977.00 |  7591.00 |  7668.00 |  7206.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 22:00 | 06-15 14:15 |
| L    | 1d  | SHORT |  8149.00 |  7787.00 |  8051.00 |  7242.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-08 00:00 | 06-11 13:30 |
| L    | 1w  | SHORT |  9312.00 |  7840.00 |  8521.00 |  7242.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 05-04 08:00 |
| LC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| LC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| LC   | 1d  | LONG  | 145000.00 | 175050.00 | 152500.00 | 167400.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-27 00:00 | 04-09 00:00 |
| LC   | 1w  | LONG  | 145000.00 | 175050.00 | 157180.00 | 167400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-26 00:00 | 06-02 00:00 |
| **LC  ** | 15m | LONG  | 169800.00 | 171400.00 | 170160.00 | 160500.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-16 14:00 | 06-17 14:15 |
| LC   | 1h  | SHORT | 178740.00 | 172340.00 | 175780.00 | 160500.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 14:00 | 06-15 14:00 |
| **LC  ** | 1d  | LONG  | 157180.00 | 178740.00 | 168460.00 | 163420.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-05 00:00 | 06-16 10:45 |
| LC   | 1w  | LONG  | 152500.00 | 209880.00 | 157180.00 | 163420.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-06 08:00 | 06-01 09:15 |
| LH   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| LH   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| LH   | 1d  | LONG  |  9000.00 | 11585.00 | 10625.00 | 11950.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-13 00:00 | 05-27 00:00 |
| **LH  ** | 1w  | SHORT | 11800.00 |  9000.00 | 11585.00 | 11950.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 02-03 00:00 | 04-21 00:00 |
| LH   | 15m | SHORT | 10235.00 | 10120.00 | 10195.00 |  9900.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-15 09:30 | 06-15 15:00 |
| **LH  ** | 1h  | LONG  | 10080.00 | 10235.00 | 10100.00 |  9900.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-11 13:30 | 06-16 09:15 |
| **LH  ** | 1d  | LONG  | 10080.00 | 12190.00 | 10100.00 |  9960.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-11 13:30 | 06-16 09:15 |
| LH   | 1w  | SHORT | 12220.00 | 10080.00 | 12190.00 |  9960.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-01 09:15 | 06-11 10:45 |
| LU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| LU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| LU   | 1d  | SHORT |  5303.00 |  4515.00 |  4974.00 |  3954.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-06 00:00 | 06-08 00:00 |
| LU   | 1w  | SHORT |  5350.00 |  4538.00 |  4974.00 |  3954.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-12 00:00 | 06-02 00:00 |
| M    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| M    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **M   ** | 1d  | LONG  |  2933.00 |  3073.00 |  2960.00 |  2918.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 04-20 00:00 | 05-26 00:00 |
| M    | 1w  | SHORT |  3087.00 |  2921.00 |  3073.00 |  2918.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-17 00:00 | 05-12 00:00 |
| M    | 15m | SHORT |  2967.00 |  2936.00 |  2943.00 |  2942.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 11:00 | 06-18 14:00 |
| M    | 1h  | LONG  |  2926.00 |  2942.00 |  2929.00 |  2942.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 13:30 | 06-15 21:15 |
| M    | 1d  | SHORT |  3042.00 |  2979.00 |  3010.00 |  2941.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-30 00:00 | 05-29 09:15 |
| M    | 1w  | SHORT |  3073.00 |  2887.00 |  2967.00 |  2941.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-11 08:00 | 06-15 09:15 |
| MA   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| MA   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| MA   | 1d  | SHORT |  3063.00 |  2827.00 |  2997.00 |  2972.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 05-20 00:00 |
| MA   | 1w  | SHORT |  3063.00 |  2756.00 |  3049.00 |  2972.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 06-02 00:00 |
| MA   | 15m | SHORT |  2682.00 |  2603.00 |  2634.00 |  2566.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 22:00 | 06-17 14:00 |
| MA   | 1h  | SHORT |  3043.00 |  2652.00 |  2687.00 |  2566.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 21:00 | 06-16 15:00 |
| **MA  ** | 1d  | LONG  |  2917.00 |  3074.00 |  2971.00 |  2567.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-09 13:45 | 06-12 09:00 |
| MA   | 1w  | SHORT |  3235.00 |  2827.00 |  2997.00 |  2567.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-06 08:00 | 05-18 08:00 |
| NI   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| NI   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **NI  ** | 1d  | LONG  | 132350.00 | 155360.00 | 140500.00 | 135100.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 03-09 00:00 | 05-18 00:00 |
| **NI  ** | 1w  | LONG  | 128800.00 | 155360.00 | 140500.00 | 135100.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 03-17 00:00 | 05-12 00:00 |
| NI   | 15m | SHORT | 136190.00 | 135180.00 | 136060.00 | 135850.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-18 10:15 | 06-18 14:00 |
| NI   | 1h  | LONG  | 135280.00 | 135930.00 | 135410.00 | 135850.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-17 11:00 | 06-17 14:15 |
| NI   | 1d  | SHORT | 145880.00 | 137700.00 | 140520.00 | 135290.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-03 00:00 | 06-08 10:45 |
| NI   | 1w  | SHORT | 155670.00 | 133140.00 | 137390.00 | 135290.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-04 08:00 | 06-15 09:15 |
| NR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| NR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| NR   | 1d  | LONG  | 12800.00 | 14155.00 | 13540.00 | 14945.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-02 00:00 | 04-17 00:00 |
| NR   | 1w  | LONG  | 12765.00 | 15625.00 | 14490.00 | 14945.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-17 00:00 | 05-19 00:00 |
| NR   | 15m | SHORT | 15670.00 | 15325.00 | 15460.00 | 15410.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 10:45 | 06-17 23:00 |
| NR   | 1h  | LONG  | 15100.00 | 15310.00 | 15265.00 | 15410.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-08 14:00 | 06-18 14:00 |
| NR   | 1d  | LONG  | 14490.00 | 16135.00 | 14740.00 | 15350.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-22 00:00 | 06-10 13:30 |
| NR   | 1w  | LONG  | 14490.00 | 16135.00 | 15005.00 | 15350.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-18 08:00 | 06-15 09:15 |
| OI   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| OI   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| OI   | 1d  | LONG  |  9122.00 | 10030.00 |  9496.00 |  9883.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-08 00:00 | 05-18 00:00 |
| OI   | 1w  | SHORT | 10167.00 |  9122.00 | 10030.00 |  9883.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-03 00:00 | 05-06 00:00 |
| **OI  ** | 15m | LONG  |  9775.00 |  9827.00 |  9780.00 |  9685.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-17 13:45 | 06-17 21:45 |
| **OI  ** | 1h  | LONG  |  9750.00 |  9895.00 |  9758.00 |  9685.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-15 21:15 | 06-17 09:15 |
| OI   | 1d  | SHORT |  9995.00 |  9750.00 |  9895.00 |  9701.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-11 09:00 | 06-16 13:45 |
| OI   | 1w  | LONG  |  9582.00 |  9911.00 |  9667.00 |  9701.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-23 08:00 | 06-15 09:15 |
| P    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| P    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| P    | 1d  | SHORT |  9858.00 |  9332.00 |  9825.00 |  9316.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-20 00:00 | 06-04 00:00 |
| P    | 1w  | SHORT | 10168.00 |  9200.00 |  9993.00 |  9316.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-31 00:00 | 05-06 00:00 |
| P    | 15m | LONG  |  6420.00 |  6600.00 |  6478.00 |  6500.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-02 14:00 | 01-13 14:00 |
| P    | 1h  | LONG  |  6394.00 |  6600.00 |  6478.00 |  6500.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-03 21:15 | 01-13 14:00 |
| P    | 1d  | LONG  |  6100.00 |  6870.00 |  6306.00 |  6500.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-25 13:45 | 01-06 13:45 |
| P    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **P   ** | 15m | SHORT |  4526.00 |  4370.00 |  4424.00 |  4746.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-30 13:45 | 05-13 14:00 |
| P    | 1h  | LONG  |  4370.00 |  4530.00 |  4390.00 |  4746.00 | ✅ ✅ ✅ ✅ | ✅ | —     | 05-07 09:15 | 05-12 15:00 |
| **P   ** | 1d  | SHORT |  4800.00 |  4370.00 |  4530.00 |  4746.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-24 09:15 | 05-11 09:15 |
| **P   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| P    | 15m | LONG  |  5974.00 |  6176.00 |  6126.00 |  6500.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-28 21:15 | 08-31 10:15 |
| P    | 1h  | LONG  |  5790.00 |  6072.00 |  5974.00 |  6500.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-21 21:15 | 08-28 21:15 |
| **P   ** | 1d  | SHORT |  6014.00 |  5790.00 |  5946.00 |  6500.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-19 13:45 | 08-25 10:45 |
| P    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| P    | 15m | LONG  |  7000.00 |  7710.00 |  7444.00 |  7550.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-06 21:15 | 01-08 11:00 |
| P    | 1h  | LONG  |  6896.00 |  7118.00 |  7000.00 |  7550.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-21 21:15 | 01-06 21:15 |
| **P   ** | 1d  | SHORT |  7444.00 |  7162.00 |  7388.00 |  7550.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-25 13:45 | 12-30 09:15 |
| **P   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| P    | 15m | LONG  |  8068.00 |  8384.00 |  8310.00 |  9344.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-28 10:15 | 04-29 11:30 |
| P    | 1h  | LONG  |  8068.00 |  8414.00 |  8280.00 |  9344.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-28 10:00 | 04-29 22:00 |
| P    | 1d  | LONG  |  7310.00 |  8512.00 |  8046.00 |  9344.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-12 13:45 | 04-26 13:45 |
| **P   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **P   ** | 15m | SHORT |  9078.00 |  8900.00 |  8944.00 |  9000.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-30 09:45 | 08-30 15:00 |
| P    | 1h  | SHORT |  9104.00 |  8738.00 |  9078.00 |  9000.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-25 21:15 | 08-30 09:15 |
| P    | 1d  | LONG  |  8738.00 |  9140.00 |  8764.00 |  9000.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-27 09:15 | 09-02 09:15 |
| P    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **P   ** | 15m | SHORT |  9924.00 |  9760.00 |  9798.00 | 10258.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 01-05 23:00 | 01-06 13:45 |
| P    | 1h  | LONG  |  9280.00 |  9938.00 |  9748.00 | 10258.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-28 11:00 | 01-06 15:00 |
| P    | 1d  | LONG  |  8946.00 |  9400.00 |  9182.00 | 10258.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-20 13:45 | 12-23 13:45 |
| **P   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| P    | 15m | LONG  | 14108.00 | 15700.00 | 14500.00 | 15516.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-10 10:00 | 05-12 21:15 |
| P    | 1h  | LONG  | 14108.00 | 15700.00 | 14500.00 | 15516.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-10 10:00 | 05-12 21:15 |
| P    | 1d  | SHORT | 16440.00 | 14108.00 | 15700.00 | 15516.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-05 09:15 | 05-12 09:15 |
| P    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| P    | 15m | SHORT |  9000.00 |  7838.00 |  8280.00 |  8196.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-06 09:15 | 09-13 14:15 |
| P    | 1h  | SHORT |  9000.00 |  7838.00 |  8280.00 |  8196.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-06 09:15 | 09-13 14:15 |
| P    | 1d  | LONG  |  7650.00 |  8848.00 |  7726.00 |  8196.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 07-22 13:45 | 08-04 09:15 |
| P    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| P    | 15m | SHORT |  7816.00 |  7472.00 |  7730.00 |  7618.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-26 22:15 | 01-12 15:00 |
| P    | 1h  | SHORT |  8102.00 |  7472.00 |  7960.00 |  7618.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-30 15:00 | 01-06 15:00 |
| **P   ** | 1d  | LONG  |  7710.00 |  8664.00 |  7820.00 |  7618.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 11-21 10:45 | 12-29 10:45 |
| P    | 1w  | SHORT |  8664.00 |  7408.00 |  8102.00 |  7618.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-28 09:15 | 12-26 09:15 |
| P    | 15m | SHORT |  7636.00 |  7602.00 |  7632.00 |  7336.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-08 13:45 | 05-08 21:15 |
| P    | 1h  | SHORT |  7636.00 |  7500.00 |  7598.00 |  7336.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-08 13:45 | 05-09 14:00 |
| P    | 1d  | SHORT |  7960.00 |  7604.00 |  7918.00 |  7336.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-12 10:45 | 04-19 09:15 |
| P    | 1w  | LONG  |  7026.00 |  7960.00 |  7130.00 |  7336.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-20 09:15 | 05-04 09:15 |
| P    | 15m | SHORT |  7952.00 |  7816.00 |  7928.00 |  7624.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-31 14:15 | 09-01 13:45 |
| **P   ** | 1h  | LONG  |  7766.00 |  7952.00 |  7816.00 |  7624.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 08-30 11:00 | 08-31 22:00 |
| P    | 1d  | LONG  |  7416.00 |  7664.00 |  7576.00 |  7624.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-03 13:45 | 08-23 09:15 |
| **P   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| P    | 15m | SHORT |  7142.00 |  7102.00 |  7138.00 |  7132.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-26 10:45 | 01-02 21:15 |
| P    | 1h  | SHORT |  7220.00 |  6844.00 |  7138.00 |  7132.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-28 09:15 | 01-02 21:15 |
| P    | 1d  | SHORT |  7458.00 |  7202.00 |  7236.00 |  7132.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-07 10:45 | 12-27 13:45 |
| P    | 1w  | SHORT |  7664.00 |  6732.00 |  7236.00 |  7132.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-13 09:15 | 12-25 09:15 |
| P    | 15m | SHORT |  7800.00 |  7520.00 |  7738.00 |  7700.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-08 10:45 | 05-13 22:30 |
| P    | 1h  | SHORT |  7898.00 |  7700.00 |  7800.00 |  7700.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-29 21:15 | 05-06 09:15 |
| P    | 1d  | LONG  |  7622.00 |  7922.00 |  7626.00 |  7700.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-22 13:45 | 04-25 13:45 |
| P    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| P    | 15m | SHORT |  8454.00 |  7620.00 |  8004.00 |  7802.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-30 15:00 | 09-05 22:00 |
| P    | 1h  | SHORT |  8178.00 |  8000.00 |  8004.00 |  7802.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-26 15:00 | 09-05 22:00 |
| **P   ** | 1d  | LONG  |  7460.00 |  8190.00 |  8000.00 |  7802.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-14 10:45 | 08-29 09:15 |
| **P   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **P   ** | 15m | SHORT |  9988.00 |  9750.00 |  9940.00 |  9954.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 01-07 13:45 | 01-09 22:00 |
| P    | 1h  | LONG  |  9732.00 | 10094.00 |  9750.00 |  9954.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-30 09:15 | 01-09 09:30 |
| P    | 1d  | LONG  |  9286.00 | 10094.00 |  9490.00 |  9954.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-20 13:45 | 01-02 13:45 |
| P    | 1w  | SHORT | 10338.00 |  9450.00 | 10094.00 |  9954.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-11 09:15 | 12-30 09:15 |
| **P   ** | 15m | SHORT |  8534.00 |  8060.00 |  8450.00 |  8724.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 04-29 21:15 | 05-12 15:00 |
| P    | 1h  | LONG  |  8060.00 |  8450.00 |  8316.00 |  8724.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-06 09:15 | 05-13 22:00 |
| **P   ** | 1d  | SHORT |  8800.00 |  8060.00 |  8450.00 |  8724.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-25 10:45 | 05-12 14:00 |
| P    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **P   ** | 15m | LONG  |  9386.00 |  9452.00 |  9446.00 |  9446.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 08-28 09:30 | 09-09 21:15 |
| P    | 1h  | LONG  |  9308.00 |  9408.00 |  9320.00 |  9446.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-04 10:15 | 09-08 09:45 |
| P    | 1d  | SHORT |  9462.00 |  9266.00 |  9450.00 |  9446.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-13 09:15 | 09-01 13:45 |
| **P   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **P   ** | 15m | LONG  |  8290.00 |  8380.00 |  8362.00 |  8244.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 01-05 13:45 | 01-07 13:45 |
| P    | 1h  | SHORT |  8582.00 |  8064.00 |  8380.00 |  8244.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-26 21:15 | 01-06 09:15 |
| P    | 1d  | SHORT |  8808.00 |  8230.00 |  8658.00 |  8244.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-05 13:45 | 12-30 13:45 |
| P    | 1w  | SHORT |  8902.00 |  8230.00 |  8658.00 |  8244.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-17 09:15 | 12-29 09:15 |
| **P   ** | 15m | SHORT |  9340.00 |  8994.00 |  9230.00 |  9230.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 05-14 21:15 | 05-18 14:15 |
| P    | 1h  | SHORT |  9438.00 |  8880.00 |  9340.00 |  9230.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-11 09:15 | 05-14 21:15 |
| P    | 1d  | SHORT |  9679.00 |  8880.00 |  9340.00 |  9230.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 09:15 | 05-14 21:15 |
| P    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| P    | 15m | SHORT |  9429.00 |  9318.00 |  9411.00 |  9301.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 22:15 | 06-17 23:00 |
| **P   ** | 1h  | LONG  |  9151.00 |  9429.00 |  9318.00 |  9301.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-15 21:15 | 06-17 10:45 |
| P    | 1d  | SHORT |  9825.00 |  9208.00 |  9420.00 |  9272.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-03 13:45 | 06-11 13:30 |
| P    | 1w  | SHORT | 10168.00 |  9200.00 |  9993.00 |  9272.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-30 08:00 | 05-04 08:00 |
| PB   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PB   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PB   | 1d  | SHORT | 17005.00 | 16400.00 | 16820.00 | 16130.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 05-25 00:00 |
| **PB  ** | 1w  | LONG  | 16195.00 | 17005.00 | 16400.00 | 16130.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 03-10 00:00 | 05-19 00:00 |
| PB   | 15m | SHORT | 16420.00 | 16390.00 | 16405.00 | 16375.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 23:45 | 06-18 14:00 |
| PB   | 1h  | SHORT | 16520.00 | 16350.00 | 16405.00 | 16375.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 21:15 | 06-18 14:00 |
| PB   | 1d  | SHORT | 16720.00 | 16055.00 | 16520.00 | 16380.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-03 00:00 | 06-17 13:45 |
| PB   | 1w  | SHORT | 17020.00 | 16400.00 | 16820.00 | 16380.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-04 08:00 | 05-25 09:15 |
| PF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PF   | 1d  | SHORT |  8832.00 |  7802.00 |  8656.00 |  7348.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-23 00:00 | 04-08 00:00 |
| PF   | 1w  | SHORT |  8832.00 |  7558.00 |  8546.00 |  7348.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-17 00:00 | 05-06 00:00 |
| PG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 1d  | LONG  |  4203.00 |  7407.00 |  5185.00 |  5548.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-05 00:00 | 04-20 00:00 |
| PG   | 1w  | LONG  |  3985.00 |  7407.00 |  5185.00 |  5548.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-09 00:00 | 04-14 00:00 |
| **PG  ** | 15m | LONG  |  3717.00 |  3953.00 |  3814.00 |  3620.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-30 14:00 | 01-11 11:15 |
| **PG  ** | 1h  | LONG  |  3654.00 |  3743.00 |  3680.00 |  3620.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-29 22:00 | 12-30 22:00 |
| PG   | 1d  | SHORT |  4104.00 |  3746.00 |  3950.00 |  3620.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-21 09:15 | 12-25 13:45 |
| **PG  ** | 1w  | LONG  |  3463.00 |  4104.00 |  3654.00 |  3620.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 11-16 09:15 | 12-28 09:15 |
| PG   | 15m | LONG  |  3980.00 |  4217.00 |  4043.00 |  4150.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-30 09:45 | 05-07 10:45 |
| PG   | 1h  | LONG  |  3940.00 |  4130.00 |  3980.00 |  4150.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-28 11:00 | 04-30 09:15 |
| PG   | 1d  | LONG  |  3755.00 |  3934.00 |  3853.00 |  4150.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-19 13:45 | 04-21 13:45 |
| **PG  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **PG  ** | 15m | SHORT |  5117.00 |  5050.00 |  5078.00 |  5200.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-30 21:15 | 08-31 10:00 |
| PG   | 1h  | LONG  |  4961.00 |  5031.00 |  5030.00 |  5200.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-24 14:00 | 08-31 14:00 |
| PG   | 1d  | LONG  |  4948.00 |  5160.00 |  5030.00 |  5200.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-25 13:45 | 08-31 13:45 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 15m | LONG  |  4600.00 |  4655.00 |  4640.00 |  4685.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-29 21:15 | 12-31 10:45 |
| **PG  ** | 1h  | LONG  |  4514.00 |  5106.00 |  4800.00 |  4685.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-30 14:00 | 01-11 11:15 |
| PG   | 1d  | LONG  |  4271.00 |  4720.00 |  4514.00 |  4685.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-20 13:45 | 12-30 13:45 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 15m | LONG  |  5935.00 |  6088.00 |  5997.00 |  6250.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-28 11:30 | 04-28 22:30 |
| PG   | 1h  | LONG  |  5935.00 |  6304.00 |  6005.00 |  6250.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-28 11:00 | 05-09 09:15 |
| PG   | 1d  | LONG  |  5924.00 |  6301.00 |  6050.00 |  6250.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-29 13:45 | 04-19 13:45 |
| PG   | 1w  | SHORT |  6743.00 |  5523.00 |  6388.00 |  6250.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-07 09:15 | 04-18 09:15 |
| **PG  ** | 15m | SHORT |  5717.00 |  5622.00 |  5708.00 |  5747.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-23 22:45 | 09-01 21:15 |
| **PG  ** | 1h  | SHORT |  5760.00 |  5652.00 |  5708.00 |  5747.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-26 11:00 | 09-01 21:15 |
| PG   | 1d  | LONG  |  4979.00 |  5352.00 |  5175.00 |  5747.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-10 13:45 | 08-17 09:15 |
| **PG  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| PG   | 15m | LONG  |  3857.00 |  4357.00 |  4014.00 |  4540.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-03 09:15 | 01-09 11:30 |
| PG   | 1h  | LONG  |  3857.00 |  4357.00 |  4014.00 |  4540.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-03 09:15 | 01-09 11:30 |
| PG   | 1d  | SHORT |  4690.00 |  4406.00 |  4555.00 |  4540.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-14 13:45 | 12-27 13:45 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 15m | LONG  |  4410.00 |  4530.00 |  4423.00 |  4660.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-09 09:15 | 05-11 09:15 |
| **PG  ** | 1h  | SHORT |  4532.00 |  4423.00 |  4530.00 |  4660.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 03-24 14:00 | 05-09 22:00 |
| PG   | 1d  | LONG  |  4406.00 |  4705.00 |  4499.00 |  4660.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-31 13:45 | 04-10 13:45 |
| **PG  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **PG  ** | 15m | SHORT |  4950.00 |  4770.00 |  4930.00 |  5050.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 09-01 09:15 | 09-01 23:00 |
| PG   | 1h  | LONG  |  4787.00 |  4950.00 |  4800.00 |  5050.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-31 10:00 | 09-05 21:15 |
| PG   | 1d  | LONG  |  3963.00 |  4699.00 |  4366.00 |  5050.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-08 13:45 | 08-25 13:45 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 15m | SHORT |  4831.00 |  4610.00 |  4647.00 |  4413.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-19 21:45 | 01-05 22:15 |
| **PG  ** | 1h  | LONG  |  4820.00 |  4930.00 |  4856.00 |  4413.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-26 09:15 | 12-28 09:15 |
| **PG  ** | 1d  | LONG  |  4506.00 |  4901.00 |  4637.00 |  4413.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-07 09:15 | 12-13 09:15 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 15m | SHORT |  4660.00 |  4420.00 |  4532.00 |  4523.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-23 11:15 | 05-08 10:00 |
| PG   | 1h  | SHORT |  4692.00 |  4639.00 |  4676.00 |  4523.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-25 21:15 | 04-29 14:00 |
| PG   | 1d  | SHORT |  4770.00 |  4555.00 |  4709.00 |  4523.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-21 13:45 | 04-25 09:15 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 15m | SHORT |  4994.00 |  4449.00 |  4900.00 |  4800.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-30 22:00 | 09-11 10:45 |
| PG   | 1h  | SHORT |  4994.00 |  4449.00 |  4900.00 |  4800.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-30 22:00 | 09-11 10:45 |
| PG   | 1d  | LONG  |  4506.00 |  4662.00 |  4612.00 |  4800.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 07-17 13:45 | 08-28 13:45 |
| PG   | 1w  | LONG  |  4406.00 |  4662.00 |  4427.00 |  4800.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 07-22 09:15 | 08-12 09:15 |
| PG   | 15m | LONG  |  4496.00 |  4706.00 |  4640.00 |  4698.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-30 15:00 | 01-02 09:15 |
| PG   | 1h  | LONG  |  4456.00 |  4706.00 |  4640.00 |  4698.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-27 14:00 | 01-02 09:15 |
| **PG  ** | 1d  | SHORT |  4433.00 |  4371.00 |  4422.00 |  4698.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 11-27 13:45 | 12-19 13:45 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **PG  ** | 15m | LONG  |  4551.00 |  4695.00 |  4624.00 |  4600.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-24 09:30 | 04-30 09:15 |
| PG   | 1h  | LONG  |  4520.00 |  4559.00 |  4527.00 |  4600.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-24 22:00 | 04-28 21:15 |
| **PG  ** | 1d  | SHORT |  4748.00 |  4288.00 |  4591.00 |  4600.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-07 09:15 | 04-23 13:45 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 15m | LONG  |  3701.00 |  3798.00 |  3750.00 |  3790.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-10 10:00 | 09-17 09:15 |
| PG   | 1h  | SHORT |  3839.00 |  3811.00 |  3830.00 |  3790.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-13 11:00 | 09-19 21:30 |
| **PG  ** | 1d  | SHORT |  3902.00 |  3680.00 |  3779.00 |  3790.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-27 10:45 | 09-03 13:45 |
| PG   | 1w  | SHORT |  3926.00 |  3680.00 |  3830.00 |  3790.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-18 09:15 | 09-15 11:15 |
| PG   | 15m | LONG  |  4172.00 |  4235.00 |  4185.00 |  4255.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-30 14:15 | 01-05 14:30 |
| **PG  ** | 1h  | SHORT |  4226.00 |  4182.00 |  4225.00 |  4255.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 12-17 10:00 | 01-05 09:15 |
| PG   | 1d  | LONG  |  4069.00 |  4231.00 |  4182.00 |  4255.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-12 13:45 | 12-17 13:45 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PG   | 15m | LONG  |  6106.00 |  6257.00 |  6193.00 |  6259.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-29 11:30 | 04-29 22:45 |
| PG   | 1h  | LONG  |  5880.00 |  6207.00 |  6041.00 |  6259.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-27 21:15 | 04-29 09:15 |
| **PG  ** | 1d  | SHORT |  6756.00 |  5563.00 |  6025.00 |  6259.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-07 09:15 | 04-13 09:15 |
| PG   | 1w  | SHORT |  7407.00 |  5545.00 |  6381.00 |  6259.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-23 09:15 | 05-06 09:45 |
| **PG  ** | 15m | LONG  |  4771.00 |  4966.00 |  4921.00 |  4790.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-17 13:45 | 06-17 22:15 |
| PG   | 1h  | SHORT |  5165.00 |  4771.00 |  4978.00 |  4790.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 14:00 | 06-17 23:00 |
| PG   | 1d  | SHORT |  5975.00 |  5423.00 |  5765.00 |  4830.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-08 00:00 | 06-11 09:00 |
| PG   | 1w  | SHORT |  6835.00 |  5185.00 |  6271.00 |  4830.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 05-18 08:00 |
| PG   | 15m | SHORT |  5381.00 |  5299.00 |  5350.00 |  5129.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-11 21:30 | 06-11 22:45 |
| **PG  ** | 1h  | LONG  |  5255.00 |  5313.00 |  5310.00 |  5129.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-09 09:15 | 06-11 13:45 |
| PG   | 1d  | SHORT |  5830.00 |  5102.00 |  5514.00 |  5129.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-12 13:45 | 06-02 09:15 |
| PG   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PK   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PK   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PK   | 1d  | LONG  |  7992.00 |  8480.00 |  8100.00 |  8344.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-02 00:00 | 05-25 00:00 |
| PK   | 1w  | LONG  |  7854.00 |  8480.00 |  8100.00 |  8344.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-03 00:00 | 05-19 00:00 |
| PP   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PP   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PP   | 1d  | LONG  |  6890.00 |  9980.00 |  8116.00 |  8649.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-12 00:00 | 04-21 00:00 |
| PP   | 1w  | SHORT |  9088.00 |  8337.00 |  9008.00 |  8649.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-19 00:00 | 06-02 00:00 |
| PP   | 15m | SHORT |  8016.00 |  7795.00 |  7875.00 |  7647.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 22:00 | 06-17 14:30 |
| PP   | 1h  | SHORT |  8691.00 |  7853.00 |  8016.00 |  7647.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 22:00 | 06-16 22:00 |
| PP   | 1d  | SHORT |  9008.00 |  8556.00 |  8789.00 |  7713.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-08 00:00 | 06-11 09:00 |
| PP   | 1w  | SHORT |  9378.00 |  8116.00 |  9088.00 |  7713.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-23 08:00 | 05-18 08:00 |
| PR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PR   | 1d  | SHORT |  9018.00 |  7606.00 |  8074.00 |  7088.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-29 00:00 | 06-01 00:00 |
| **PR  ** | 1w  | LONG  |  5844.00 |  9282.00 |  7690.00 |  7088.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 08-12 00:00 | 04-07 00:00 |
| PS   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PS   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PS   | 1d  | SHORT | 41750.00 | 36020.00 | 38835.00 | 35840.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-08 00:00 | 05-21 00:00 |
| **PS  ** | 1w  | LONG  | 34375.00 | 39340.00 | 36020.00 | 35840.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 05-06 00:00 | 05-12 00:00 |
| PX   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PX   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| PX   | 1d  | SHORT |  9742.00 |  8876.00 |  9342.00 |  8786.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-29 00:00 | 05-18 00:00 |
| PX   | 1w  | LONG  |  8394.00 |  8774.00 |  8766.00 |  8786.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-04 00:00 | 04-14 00:00 |
| PX   | 15m | LONG  |  7994.00 |  8206.00 |  8136.00 |  8170.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-17 13:45 | 06-18 09:15 |
| PX   | 1h  | LONG  |  8070.00 |  8144.00 |  8134.00 |  8170.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-16 11:00 | 06-18 13:45 |
| PX   | 1d  | SHORT |  9032.00 |  7988.00 |  8206.00 |  8180.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-10 09:12 | 06-17 13:45 |
| PX   | 1w  | SHORT | 10420.00 |  8752.00 | 10066.00 |  8180.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 04-27 08:00 |
| RB   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RB   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RB   | 1d  | LONG  |  3005.00 |  3167.00 |  3083.00 |  3180.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-24 00:00 | 04-10 00:00 |
| RB   | 1w  | LONG  |  3083.00 |  3298.00 |  3136.00 |  3180.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-07 00:00 | 05-26 00:00 |
| **RB  ** | 15m | LONG  |  3760.00 |  3795.00 |  3789.00 |  3770.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 01-09 14:45 | 01-09 23:00 |
| RB   | 1h  | LONG  |  3743.00 |  3767.00 |  3754.00 |  3770.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-07 11:00 | 01-08 13:45 |
| RB   | 1d  | LONG  |  3683.00 |  3800.00 |  3739.00 |  3770.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-25 13:45 | 01-02 13:45 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RB   | 15m | SHORT |  3444.00 |  3405.00 |  3438.00 |  3400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-12 14:15 | 05-13 09:45 |
| RB   | 1h  | LONG  |  3371.00 |  3418.00 |  3388.00 |  3400.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-11 21:15 | 05-12 13:45 |
| RB   | 1d  | SHORT |  3586.00 |  3480.00 |  3550.00 |  3400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-17 09:15 | 04-23 09:15 |
| RB   | 1w  | SHORT |  3591.00 |  3254.00 |  3586.00 |  3400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 09:15 | 04-13 09:15 |
| RB   | 15m | LONG  |  3595.00 |  3635.00 |  3611.00 |  3645.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 10-13 09:15 | 10-14 09:15 |
| **RB  ** | 1h  | SHORT |  3635.00 |  3611.00 |  3630.00 |  3645.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 10-13 11:00 | 10-14 10:45 |
| RB   | 1d  | LONG  |  3580.00 |  3639.00 |  3591.00 |  3645.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-21 13:45 | 09-30 13:45 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **RB  ** | 15m | SHORT |  4221.00 |  4148.00 |  4175.00 |  4192.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 01-11 15:00 | 01-13 15:00 |
| **RB  ** | 1h  | SHORT |  4221.00 |  4111.00 |  4175.00 |  4192.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 12-28 22:00 | 01-13 15:00 |
| RB   | 1d  | SHORT |  4678.00 |  4111.00 |  4300.00 |  4192.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-22 09:15 | 01-04 09:15 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RB   | 15m | SHORT |  5949.00 |  5861.00 |  5915.00 |  5581.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-11 14:15 | 05-11 23:00 |
| RB   | 1h  | SHORT |  6198.00 |  5820.00 |  5949.00 |  5581.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-10 21:15 | 05-11 14:00 |
| RB   | 1d  | LONG  |  5080.00 |  5410.00 |  5301.00 |  5581.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-19 13:45 | 04-28 13:45 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RB   | 15m | LONG  |  5580.00 |  5700.00 |  5650.00 |  5780.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 10-13 22:00 | 10-14 14:45 |
| RB   | 1h  | LONG  |  5492.00 |  5596.00 |  5580.00 |  5780.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-13 22:00 | 10-13 22:00 |
| RB   | 1d  | LONG  |  5359.00 |  5950.00 |  5671.00 |  5780.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-15 09:15 | 09-24 13:45 |
| RB   | 1w  | LONG  |  4929.00 |  5980.00 |  5580.00 |  5780.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-16 09:15 | 10-11 09:15 |
| RB   | 15m | LONG  |  4522.00 |  4702.00 |  4601.00 |  4650.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-11 09:15 | 01-12 21:15 |
| RB   | 1h  | LONG  |  4495.00 |  4646.00 |  4601.00 |  4650.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-10 15:00 | 01-12 21:15 |
| **RB  ** | 1d  | SHORT |  4676.00 |  4494.00 |  4597.00 |  4650.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 12-07 13:45 | 12-29 13:45 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **RB  ** | 15m | SHORT |  5053.00 |  5010.00 |  5025.00 |  5070.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 05-11 15:00 | 05-13 09:15 |
| RB   | 1h  | SHORT |  5139.00 |  5055.00 |  5110.00 |  5070.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-09 14:00 | 05-10 10:45 |
| RB   | 1d  | LONG  |  5018.00 |  5199.00 |  5051.00 |  5070.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-13 13:45 | 05-06 13:45 |
| RB   | 1w  | LONG  |  4681.00 |  5209.00 |  4971.00 |  5070.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-14 09:15 | 04-25 09:15 |
| RB   | 15m | SHORT |  3830.00 |  3700.00 |  3826.00 |  3730.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 10-14 13:45 | 10-17 14:15 |
| RB   | 1h  | SHORT |  3960.00 |  3780.00 |  3850.00 |  3730.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-23 14:00 | 10-12 21:15 |
| **RB  ** | 1d  | LONG  |  3822.00 |  3993.00 |  3836.00 |  3730.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 09-02 10:45 | 09-21 09:15 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **RB  ** | 15m | SHORT |  4360.00 |  4261.00 |  4320.00 |  4320.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 01-13 13:45 | 01-16 11:30 |
| RB   | 1h  | LONG  |  4141.00 |  4322.00 |  4220.00 |  4320.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-10 21:15 | 01-11 22:45 |
| RB   | 1d  | LONG  |  4006.00 |  4150.00 |  4016.00 |  4320.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-28 13:45 | 01-04 13:45 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RB   | 15m | SHORT |  3550.00 |  3416.00 |  3490.00 |  3482.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-10 21:15 | 05-11 14:00 |
| RB   | 1h  | SHORT |  3604.00 |  3416.00 |  3490.00 |  3482.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-09 22:00 | 05-11 14:00 |
| RB   | 1d  | SHORT |  4002.00 |  3491.00 |  3630.00 |  3482.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-18 09:15 | 05-08 13:45 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **RB  ** | 15m | SHORT |  3524.00 |  3482.00 |  3520.00 |  3530.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 10-12 11:30 | 10-12 21:30 |
| **RB  ** | 1h  | SHORT |  3524.00 |  3482.00 |  3520.00 |  3530.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 10-12 11:00 | 10-12 21:30 |
| RB   | 1d  | SHORT |  3768.00 |  3642.00 |  3746.00 |  3530.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-24 13:45 | 09-12 13:45 |
| **RB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **RB  ** | 15m | SHORT |  3943.00 |  3931.00 |  3938.00 |  3946.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 01-09 14:00 | 01-11 21:30 |
| RB   | 1h  | LONG  |  3858.00 |  3885.00 |  3880.00 |  3946.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-05 11:00 | 01-10 15:00 |
| RB   | 1d  | LONG  |  3860.00 |  3940.00 |  3918.00 |  3946.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-29 13:45 | 12-15 13:45 |
| **RB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| RB   | 15m | SHORT |  3570.00 |  3405.00 |  3430.00 |  3411.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-13 21:15 | 05-15 14:30 |
| RB   | 1h  | SHORT |  3520.00 |  3475.00 |  3496.00 |  3411.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-09 11:00 | 05-10 21:15 |
| RB   | 1d  | SHORT |  3625.00 |  3552.00 |  3606.00 |  3411.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-18 10:45 | 04-25 09:15 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **RB  ** | 15m | LONG  |  3320.00 |  3440.00 |  3388.00 |  3381.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 10-11 21:15 | 10-14 21:30 |
| RB   | 1h  | LONG  |  3313.00 |  3425.00 |  3320.00 |  3381.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 10-09 21:15 | 10-11 21:15 |
| RB   | 1d  | LONG  |  3144.00 |  3659.00 |  3313.00 |  3381.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-23 13:45 | 10-09 13:45 |
| **RB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| RB   | 15m | LONG  |  3125.00 |  3150.00 |  3130.00 |  3220.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-09 10:15 | 01-10 14:15 |
| RB   | 1h  | LONG  |  3120.00 |  3186.00 |  3170.00 |  3220.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-09 22:00 | 01-13 14:00 |
| RB   | 1d  | SHORT |  3355.00 |  3241.00 |  3312.00 |  3220.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-03 09:15 | 12-30 13:45 |
| RB   | 1w  | SHORT |  3372.00 |  3194.00 |  3312.00 |  3220.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-09 09:15 | 12-30 09:15 |
| RB   | 15m | LONG  |  2976.00 |  3062.00 |  3045.00 |  3075.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-09 21:15 | 05-13 09:45 |
| RB   | 1h  | LONG  |  2977.00 |  3062.00 |  3030.00 |  3075.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-09 09:15 | 05-13 14:00 |
| **RB  ** | 1d  | SHORT |  3080.00 |  3025.00 |  3074.00 |  3075.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-25 13:45 | 05-07 09:15 |
| RB   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RB   | 15m | SHORT |  3001.00 |  2972.00 |  2977.00 |  2950.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 10-13 21:30 | 10-14 14:00 |
| RB   | 1h  | SHORT |  3030.00 |  2875.00 |  3001.00 |  2950.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 10-10 21:15 | 10-13 21:30 |
| RB   | 1d  | SHORT |  3107.00 |  2972.00 |  3040.00 |  2950.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-22 09:15 | 10-09 13:45 |
| **RB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| RB   | 15m | LONG  |  3101.00 |  3138.00 |  3132.00 |  3165.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-08 21:15 | 01-12 21:15 |
| RB   | 1h  | LONG  |  3106.00 |  3138.00 |  3125.00 |  3165.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-07 21:15 | 01-14 09:15 |
| RB   | 1d  | LONG  |  3050.00 |  3138.00 |  3088.00 |  3165.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-06 09:15 | 01-09 09:15 |
| **RB  ** | 1w  | SHORT |  3160.00 |  3056.00 |  3147.00 |  3165.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-01 09:15 | 12-22 09:15 |
| RB   | 15m | SHORT |  3172.00 |  3150.00 |  3155.00 |  3150.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-14 09:30 | 05-15 10:15 |
| RB   | 1h  | SHORT |  3182.00 |  3133.00 |  3175.00 |  3150.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-08 10:00 | 05-13 10:45 |
| RB   | 1d  | LONG  |  3112.00 |  3151.00 |  3141.00 |  3150.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-27 13:45 | 05-12 13:45 |
| **RB  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| RB   | 15m | SHORT |  3135.00 |  3107.00 |  3116.00 |  3102.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-10 10:15 | 06-17 22:15 |
| RB   | 1h  | SHORT |  3170.00 |  3136.00 |  3146.00 |  3102.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-15 10:00 | 06-17 11:00 |
| RB   | 1d  | SHORT |  3218.00 |  3120.00 |  3187.00 |  3099.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-25 00:00 | 06-03 00:00 |
| **RB  ** | 1w  | LONG  |  2949.00 |  3278.00 |  3119.00 |  3099.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 03-23 08:00 | 06-08 09:15 |
| RB   | 15m | LONG  |  3151.00 |  3190.00 |  3173.00 |  3187.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-11 14:00 | 06-12 14:30 |
| RB   | 1h  | LONG  |  3165.00 |  3180.00 |  3173.00 |  3187.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-03 10:45 | 06-12 14:00 |
| RB   | 1d  | LONG  |  3136.00 |  3189.00 |  3142.00 |  3187.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-27 09:15 | 06-09 13:45 |
| RB   | 1w  | LONG  |  3083.00 |  3298.00 |  3136.00 |  3187.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-07 09:15 | 05-25 09:15 |
| RM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RM   | 1d  | SHORT |  2634.00 |  2212.00 |  2437.00 |  2239.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-13 00:00 | 05-06 00:00 |
| RM   | 1w  | LONG  |  2195.00 |  2634.00 |  2212.00 |  2239.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-13 00:00 | 03-31 00:00 |
| **RM  ** | 15m | SHORT |  2289.00 |  2281.00 |  2284.00 |  2286.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-17 09:30 | 06-18 09:15 |
| RM   | 1h  | LONG  |  2254.00 |  2274.00 |  2255.00 |  2286.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-05 09:15 | 06-15 21:15 |
| RM   | 1d  | LONG  |  2214.00 |  2291.00 |  2265.00 |  2272.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-09 13:45 | 06-17 13:45 |
| RM   | 1w  | SHORT |  2437.00 |  2214.00 |  2291.00 |  2272.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-04 08:00 | 06-15 09:15 |
| RR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **RR  ** | 1d  | SHORT |  3610.00 |  3541.00 |  3591.00 |  3603.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 12-15 00:00 | 05-29 00:00 |
| RR   | 1w  | SHORT |  3668.00 |  3541.00 |  3618.00 |  3603.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-13 00:00 | 06-02 00:00 |
| RU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| RU   | 1d  | LONG  | 16480.00 | 18395.00 | 17220.00 | 17330.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-17 00:00 | 05-22 00:00 |
| RU   | 1w  | LONG  | 14910.00 | 17600.00 | 15885.00 | 17330.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-02 00:00 | 03-17 00:00 |
| RU   | 15m | SHORT | 17860.00 | 17640.00 | 17785.00 | 17750.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-15 09:15 | 06-18 14:15 |
| RU   | 1h  | LONG  | 17540.00 | 17860.00 | 17555.00 | 17750.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-12 13:30 | 06-16 09:15 |
| RU   | 1d  | LONG  | 17220.00 | 18440.00 | 17245.00 | 17750.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-22 00:00 | 06-10 00:00 |
| RU   | 1w  | LONG  | 17220.00 | 18440.00 | 17555.00 | 17750.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-18 08:00 | 06-15 09:15 |
| SA   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SA   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SA   | 1d  | SHORT |  1274.00 |  1175.00 |  1234.00 |  1152.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 06-01 00:00 |
| **SA  ** | 1w  | LONG  |  1146.00 |  1330.00 |  1175.00 |  1152.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 02-24 00:00 | 05-19 00:00 |
| SA   | 15m | SHORT |  1170.00 |  1160.00 |  1168.00 |  1127.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 21:15 | 06-17 10:00 |
| SA   | 1h  | SHORT |  1198.00 |  1175.00 |  1177.00 |  1127.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-19 14:00 | 06-15 11:00 |
| SA   | 1d  | SHORT |  1234.00 |  1144.00 |  1164.00 |  1136.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-01 09:15 | 06-11 13:30 |
| SA   | 1w  | SHORT |  1274.00 |  1175.00 |  1233.00 |  1136.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-04 08:00 | 06-01 09:15 |
| SC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SC   | 1d  | SHORT |   691.40 |   575.30 |   619.60 |   572.20 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-20 00:00 | 06-02 00:00 |
| **SC  ** | 1w  | LONG  |   431.80 |   838.40 |   592.00 |   572.20 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 10-21 00:00 | 04-14 00:00 |
| SC   | 15m | SHORT |   511.50 |   422.10 |   507.50 |   502.20 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-18 02:30 | 06-18 11:00 |
| SC   | 1h  | SHORT |   529.20 |   518.10 |   524.00 |   502.20 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 09:15 | 06-16 15:00 |
| SC   | 1d  | SHORT |   617.00 |   561.50 |   596.40 |   502.20 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-08 00:00 | 06-11 09:15 |
| SC   | 1w  | SHORT |   809.40 |   587.50 |   694.90 |   502.20 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 04-27 08:00 |
| SC   | 15m | SHORT |   563.60 |   549.40 |   552.30 |   550.90 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 11:00 | 06-13 00:00 |
| SC   | 1h  | SHORT |   591.10 |   553.30 |   564.80 |   550.90 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 00:00 | 06-12 22:00 |
| SC   | 1d  | SHORT |   618.00 |   561.50 |   598.90 |   550.90 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-08 13:45 | 06-11 09:15 |
| **SC  ** | 1w  | LONG  |   411.00 |   823.00 |   585.20 |   550.90 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 01-06 00:00 | 04-13 09:30 |
| SF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SF   | 1d  | SHORT |  6190.00 |  5616.00 |  5922.00 |  5880.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-23 00:00 | 05-07 00:00 |
| SF   | 1w  | LONG  |  5452.00 |  6196.00 |  5616.00 |  5880.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 02-24 00:00 | 04-07 00:00 |
| SF   | 15m | LONG  |  5790.00 |  5818.00 |  5794.00 |  5802.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 10:15 | 06-18 13:45 |
| SF   | 1h  | SHORT |  5826.00 |  5718.00 |  5818.00 |  5802.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-15 09:15 | 06-16 14:15 |
| SF   | 1d  | SHORT |  6008.00 |  5826.00 |  5996.00 |  5800.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-04 00:00 | 06-10 10:30 |
| SF   | 1w  | SHORT |  6292.00 |  5616.00 |  6086.00 |  5800.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-23 09:15 | 05-18 08:00 |
| SH   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SH   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SH   | 1d  | SHORT |  2685.00 |  2041.00 |  2147.00 |  1889.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-24 00:00 | 04-23 00:00 |
| SH   | 1w  | SHORT |  2598.00 |  2251.00 |  2300.00 |  1889.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-03 00:00 | 12-23 00:00 |
| SH   | 15m | SHORT |  1883.00 |  1843.00 |  1876.00 |  1847.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-15 21:15 | 06-16 21:15 |
| SH   | 1h  | SHORT |  1905.00 |  1865.00 |  1876.00 |  1847.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-10 10:30 | 06-16 21:15 |
| SH   | 1d  | SHORT |  1965.00 |  1842.00 |  1918.00 |  1831.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-02 13:45 | 06-11 10:30 |
| SH   | 1w  | SHORT |  2725.00 |  2041.00 |  2147.00 |  1831.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 04-20 08:00 |
| SI   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SI   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SI   | 1d  | LONG  |  8235.00 |  8790.00 |  8515.00 |  8785.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-19 00:00 | 04-24 00:00 |
| SI   | 1w  | SHORT |  9280.00 |  8405.00 |  8835.00 |  8785.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 06-02 00:00 |
| SI   | 15m | SHORT |  8700.00 |  8600.00 |  8670.00 |  8560.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-16 13:45 | 06-17 10:45 |
| SI   | 1h  | SHORT |  8630.00 |  8540.00 |  8610.00 |  8560.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-28 14:00 | 06-18 14:00 |
| **SI  ** | 1d  | LONG  |  8480.00 |  8875.00 |  8600.00 |  8545.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-09 00:00 | 06-17 09:15 |
| SI   | 1w  | LONG  |  8405.00 |  8875.00 |  8535.00 |  8545.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-18 09:15 | 06-15 09:15 |
| SM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SM   | 1d  | SHORT |  6720.00 |  6066.00 |  6276.00 |  6016.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-24 00:00 | 04-17 00:00 |
| SM   | 1w  | SHORT |  6720.00 |  5832.00 |  6114.00 |  6016.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-24 00:00 | 06-02 00:00 |
| SM   | 15m | LONG  |  5796.00 |  5828.00 |  5812.00 |  5822.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-17 11:15 | 06-18 13:45 |
| SM   | 1h  | SHORT |  6006.00 |  5934.00 |  5998.00 |  5822.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-10 14:00 | 06-12 10:00 |
| SM   | 1d  | SHORT |  6114.00 |  5900.00 |  6040.00 |  5832.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-04 00:00 | 06-10 00:00 |
| **SM  ** | 1w  | LONG  |  5730.00 |  6756.00 |  5832.00 |  5832.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 02-24 09:15 | 05-11 08:00 |
| SN   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SN   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **SN  ** | 1d  | LONG  | 378500.00 | 440590.00 | 400300.00 | 397880.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 04-30 00:00 | 05-20 00:00 |
| SN   | 1w  | SHORT | 464700.00 | 322580.00 | 451860.00 | 397880.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 02-24 00:00 | 06-02 00:00 |
| **SN  ** | 15m | LONG  | 420830.00 | 426350.00 | 423400.00 | 414330.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-16 15:00 | 06-17 23:30 |
| **SN  ** | 1h  | LONG  | 419820.00 | 424260.00 | 420560.00 | 414330.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-16 22:00 | 06-17 21:15 |
| SN   | 1d  | SHORT | 431960.00 | 416030.00 | 427560.00 | 412500.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-26 00:00 | 06-15 13:45 |
| SN   | 1w  | SHORT | 441000.00 | 401190.00 | 427560.00 | 412500.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-11 08:00 | 06-15 09:15 |
| SP   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SP   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SP   | 1d  | SHORT |  5260.00 |  4944.00 |  5178.00 |  4868.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-24 00:00 | 04-21 00:00 |
| SP   | 1w  | SHORT |  5436.00 |  4944.00 |  5186.00 |  4868.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-03 00:00 | 05-12 00:00 |
| **SP  ** | 15m | LONG  |  4882.00 |  4956.00 |  4936.00 |  4866.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 06-16 10:15 | 06-16 22:45 |
| **SP  ** | 1h  | LONG  |  4872.00 |  4908.00 |  4882.00 |  4866.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 05-29 22:00 | 06-16 10:00 |
| SP   | 1d  | LONG  |  4788.00 |  4898.00 |  4838.00 |  4886.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-04 13:45 | 06-10 13:30 |
| SP   | 1w  | SHORT |  5186.00 |  4788.00 |  4962.00 |  4886.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-11 08:00 | 06-15 09:15 |
| SR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SR   | 1d  | SHORT |  5533.00 |  5259.00 |  5455.00 |  5314.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-30 00:00 | 06-03 00:00 |
| SR   | 1w  | SHORT |  5538.00 |  5339.00 |  5455.00 |  5314.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-12 00:00 | 06-02 00:00 |
| SR   | 15m | SHORT |  5353.00 |  5322.00 |  5345.00 |  5320.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 21:30 | 06-18 09:45 |
| **SR  ** | 1h  | LONG  |  5312.00 |  5348.00 |  5332.00 |  5320.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-08 09:15 | 06-17 14:00 |
| SR   | 1d  | SHORT |  5472.00 |  5373.00 |  5455.00 |  5318.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 09:15 | 06-03 00:00 |
| SR   | 1w  | SHORT |  5538.00 |  5273.00 |  5354.00 |  5318.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-11 08:00 | 06-15 09:15 |
| SS   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SS   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| SS   | 1d  | SHORT | 15835.00 | 14600.00 | 15175.00 | 14385.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 06-03 00:00 |
| SS   | 1w  | SHORT | 15835.00 | 14600.00 | 15175.00 | 14385.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 06-02 00:00 |
| **SS  ** | 15m | SHORT | 15140.00 | 15040.00 | 15125.00 | 15195.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 06-18 09:15 | 06-18 13:45 |
| SS   | 1h  | LONG  | 15035.00 | 15140.00 | 15040.00 | 15195.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-17 21:15 | 06-18 10:00 |
| SS   | 1d  | LONG  | 14290.00 | 15315.00 | 15035.00 | 15090.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-10 13:45 | 06-17 13:45 |
| SS   | 1w  | LONG  | 13595.00 | 15870.00 | 14600.00 | 15090.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 05-18 08:00 |
| TA   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 1d  | LONG  |  5858.00 |  5996.00 |  5876.00 |  6302.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 02-26 00:00 | 05-25 00:00 |
| TA   | 1w  | SHORT |  6844.00 |  5876.00 |  6470.00 |  6302.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 06-02 00:00 |
| TA   | 15m | SHORT |  4868.00 |  4836.00 |  4840.00 |  4836.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-13 13:45 | 01-15 09:30 |
| TA   | 1h  | SHORT |  4902.00 |  4766.00 |  4864.00 |  4836.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-24 22:00 | 01-10 21:15 |
| TA   | 1d  | LONG  |  4804.00 |  5060.00 |  4830.00 |  4836.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-23 10:45 | 01-10 09:30 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | LONG  |  3344.00 |  3556.00 |  3478.00 |  3518.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-12 11:15 | 05-18 11:30 |
| TA   | 1h  | LONG  |  3452.00 |  3558.00 |  3478.00 |  3518.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-19 09:15 | 05-18 11:00 |
| TA   | 1d  | LONG  |  3120.00 |  3440.00 |  3298.00 |  3518.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-28 09:15 | 05-13 09:15 |
| **TA  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **TA  ** | 15m | SHORT |  3410.00 |  3386.00 |  3400.00 |  3450.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 09-11 22:45 | 09-14 10:45 |
| TA   | 1h  | SHORT |  3516.00 |  3412.00 |  3456.00 |  3450.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-08 14:00 | 09-09 21:15 |
| TA   | 1d  | SHORT |  3702.00 |  3570.00 |  3618.00 |  3450.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-07 13:45 | 08-18 09:15 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | LONG  |  3892.00 |  3970.00 |  3898.00 |  3940.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-14 22:00 | 01-15 14:00 |
| TA   | 1h  | SHORT |  3982.00 |  3892.00 |  3970.00 |  3940.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-13 21:15 | 01-15 09:15 |
| TA   | 1d  | LONG  |  3620.00 |  3970.00 |  3776.00 |  3940.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-29 10:45 | 01-11 13:45 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **TA  ** | 15m | LONG  |  4536.00 |  4646.00 |  4592.00 |  4578.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 05-17 21:15 | 05-18 11:00 |
| TA   | 1h  | SHORT |  4844.00 |  4524.00 |  4610.00 |  4578.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-12 22:00 | 05-14 22:00 |
| **TA  ** | 1d  | LONG  |  4444.00 |  4908.00 |  4630.00 |  4578.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 04-22 13:45 | 05-11 13:45 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | LONG  |  4760.00 |  4970.00 |  4794.00 |  4852.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-01 22:15 | 09-14 13:45 |
| TA   | 1h  | LONG  |  4648.00 |  4780.00 |  4700.00 |  4852.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-10 15:00 | 09-13 21:15 |
| TA   | 1d  | SHORT |  5190.00 |  4908.00 |  5006.00 |  4852.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 07-16 13:45 | 08-25 09:15 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | LONG  |  5194.00 |  5338.00 |  5214.00 |  5278.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-13 13:45 | 01-14 22:15 |
| TA   | 1h  | LONG  |  5194.00 |  5338.00 |  5214.00 |  5278.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-13 13:45 | 01-14 22:15 |
| TA   | 1d  | LONG  |  4856.00 |  5046.00 |  5000.00 |  5278.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-15 13:45 | 01-06 13:45 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | SHORT |  7046.00 |  6720.00 |  6920.00 |  6782.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-13 21:15 | 05-17 09:15 |
| TA   | 1h  | LONG  |  6622.00 |  7046.00 |  6720.00 |  6782.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-12 10:45 | 05-16 10:00 |
| TA   | 1d  | LONG  |  5918.00 |  6660.00 |  6218.00 |  6782.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-25 13:45 | 05-10 09:15 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **TA  ** | 15m | LONG  |  6640.00 |  6770.00 |  6700.00 |  6658.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 09-14 14:15 | 09-14 22:30 |
| **TA  ** | 1h  | LONG  |  6366.00 |  6796.00 |  6684.00 |  6658.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 09-08 21:15 | 09-13 23:00 |
| TA   | 1d  | LONG  |  5824.00 |  6244.00 |  6010.00 |  6658.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-19 13:45 | 08-29 13:45 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | LONG  |  5446.00 |  5550.00 |  5460.00 |  5484.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-13 10:45 | 01-16 11:15 |
| TA   | 1h  | LONG  |  5424.00 |  5528.00 |  5460.00 |  5484.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-29 10:00 | 01-16 11:00 |
| TA   | 1d  | LONG  |  5312.00 |  5534.00 |  5424.00 |  5484.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-15 09:15 | 12-29 09:15 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | SHORT |  5720.00 |  5446.00 |  5550.00 |  5484.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-11 23:00 | 05-16 10:00 |
| TA   | 1h  | LONG  |  5446.00 |  5550.00 |  5474.00 |  5484.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-15 11:15 | 05-16 14:15 |
| TA   | 1d  | SHORT |  6578.00 |  6150.00 |  6332.00 |  5484.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-03 09:15 | 04-11 13:45 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | LONG  |  6004.00 |  6160.00 |  6130.00 |  6390.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-08 11:30 | 09-11 15:00 |
| TA   | 1h  | LONG  |  6130.00 |  6342.00 |  6280.00 |  6390.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-11 15:00 | 09-13 14:00 |
| TA   | 1d  | LONG  |  5984.00 |  6232.00 |  6026.00 |  6390.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-28 09:15 | 09-04 13:45 |
| **TA  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **TA  ** | 15m | LONG  |  5656.00 |  5762.00 |  5732.00 |  5724.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 01-11 09:30 | 01-12 13:45 |
| TA   | 1h  | LONG  |  5656.00 |  5762.00 |  5710.00 |  5724.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-11 09:15 | 01-15 09:15 |
| TA   | 1d  | LONG  |  5586.00 |  5768.00 |  5656.00 |  5724.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-05 13:45 | 01-11 09:15 |
| TA   | 1w  | LONG  |  5536.00 |  5988.00 |  5656.00 |  5724.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-11 09:15 | 01-08 09:15 |
| TA   | 15m | LONG  |  5796.00 |  5820.00 |  5808.00 |  5828.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-09 14:00 | 05-16 22:45 |
| TA   | 1h  | LONG  |  5740.00 |  5770.00 |  5746.00 |  5828.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-13 09:15 | 05-15 21:15 |
| TA   | 1d  | SHORT |  6068.00 |  5900.00 |  6058.00 |  5828.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-02 13:45 | 04-16 13:45 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | SHORT |  4780.00 |  4502.00 |  4740.00 |  4716.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-10 09:45 | 09-12 14:45 |
| TA   | 1h  | SHORT |  5010.00 |  4836.00 |  4930.00 |  4716.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-04 23:00 | 09-06 14:00 |
| TA   | 1d  | SHORT |  5620.00 |  5224.00 |  5424.00 |  4716.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-13 09:15 | 08-26 13:45 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **TA  ** | 15m | SHORT |  5128.00 |  5034.00 |  5100.00 |  5120.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 01-13 09:30 | 01-14 09:30 |
| TA   | 1h  | LONG  |  4942.00 |  5128.00 |  5034.00 |  5120.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-10 11:15 | 01-13 21:15 |
| TA   | 1d  | LONG  |  4732.00 |  4982.00 |  4798.00 |  5120.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-27 13:45 | 01-07 13:45 |
| TA   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| TA   | 15m | LONG  |  4920.00 |  5012.00 |  4940.00 |  4970.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 05-16 15:00 | 05-19 14:00 |
| TA   | 1h  | SHORT |  4990.00 |  4956.00 |  4986.00 |  4970.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-15 15:00 | 05-16 09:15 |
| TA   | 1d  | LONG  |  4246.00 |  4670.00 |  4412.00 |  4970.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-22 13:45 | 05-06 09:15 |
| **TA  ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| TA   | 15m | SHORT |  4628.00 |  4598.00 |  4622.00 |  4544.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-10 14:00 | 09-11 10:15 |
| TA   | 1h  | SHORT |  4628.00 |  4598.00 |  4622.00 |  4544.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 09-10 14:00 | 09-11 10:00 |
| TA   | 1d  | SHORT |  4742.00 |  4500.00 |  4628.00 |  4544.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-12 13:45 | 09-10 13:45 |
| TA   | 1w  | SHORT |  4952.00 |  4630.00 |  4894.00 |  4544.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 07-21 09:15 | 08-18 09:15 |
| TA   | 15m | SHORT |  5114.00 |  4946.00 |  5012.00 |  4960.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-14 23:00 | 01-16 10:15 |
| TA   | 1h  | SHORT |  5088.00 |  5006.00 |  5012.00 |  4960.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-24 10:00 | 01-16 10:00 |
| TA   | 1d  | SHORT |  5172.00 |  5002.00 |  5164.00 |  4960.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-06 13:45 | 01-09 13:45 |
| TA   | 1w  | LONG  |  4584.00 |  5270.00 |  4946.00 |  4960.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-15 09:15 | 01-12 09:15 |
| TA   | 15m | SHORT |  6562.00 |  6494.00 |  6546.00 |  6534.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-15 14:30 | 05-18 23:00 |
| TA   | 1h  | SHORT |  6596.00 |  6520.00 |  6562.00 |  6534.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-22 11:00 | 05-15 14:00 |
| TA   | 1d  | LONG  |  6406.00 |  7270.00 |  6482.00 |  6534.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-20 09:15 | 05-08 13:45 |
| TA   | 1w  | SHORT |  7270.00 |  6184.00 |  7010.00 |  6534.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-23 09:15 | 05-06 09:15 |
| TA   | 15m | LONG  |  5728.00 |  5820.00 |  5806.00 |  5868.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-16 21:15 | 06-18 09:15 |
| TA   | 1h  | LONG  |  5716.00 |  5872.00 |  5824.00 |  5868.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-17 13:45 | 06-18 13:45 |
| **TA  ** | 1d  | LONG  |  6060.00 |  6352.00 |  6130.00 |  5856.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 05-29 13:45 | 06-05 00:00 |
| TA   | 1w  | SHORT |  7042.00 |  5962.00 |  6844.00 |  5856.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 05-04 08:00 |
| UR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| UR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| UR   | 1d  | SHORT |  1954.00 |  1820.00 |  1905.00 |  1793.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-09 00:00 | 05-27 00:00 |
| UR   | 1w  | SHORT |  2082.00 |  1811.00 |  1905.00 |  1793.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-21 00:00 | 05-26 00:00 |
| UR   | 15m | LONG  |  1782.00 |  1814.00 |  1799.00 |  1813.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-11 09:15 | 06-18 13:45 |
| UR   | 1h  | LONG  |  1790.00 |  1825.00 |  1799.00 |  1813.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-02 15:00 | 06-18 13:45 |
| UR   | 1d  | SHORT |  1905.00 |  1758.00 |  1865.00 |  1809.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-27 09:15 | 06-08 00:00 |
| UR   | 1w  | SHORT |  1967.00 |  1864.00 |  1881.00 |  1809.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-09 09:15 | 05-25 08:00 |
| V    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| V    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| V    | 1d  | SHORT |  6364.00 |  4929.00 |  5371.00 |  4706.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-23 00:00 | 04-29 00:00 |
| V    | 1w  | SHORT |  6364.00 |  4929.00 |  5371.00 |  4706.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-17 00:00 | 04-28 00:00 |
| V    | 15m | SHORT |  4641.00 |  4611.00 |  4635.00 |  4616.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-17 21:45 | 06-18 10:45 |
| V    | 1h  | SHORT |  4759.00 |  4608.00 |  4686.00 |  4616.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-12 13:30 | 06-17 09:15 |
| V    | 1d  | SHORT |  5032.00 |  4652.00 |  4722.00 |  4614.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-01 10:45 | 06-10 13:30 |
| V    | 1w  | SHORT |  6380.00 |  4984.00 |  5371.00 |  4614.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-16 08:00 | 04-27 08:00 |
| Y    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| Y    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| Y    | 1d  | SHORT |  8727.00 |  8402.00 |  8682.00 |  8320.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 05-20 00:00 |
| Y    | 1w  | SHORT |  8727.00 |  8402.00 |  8630.00 |  8320.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 00:00 | 06-02 00:00 |
| Y    | 15m | SHORT |  7140.00 |  6720.00 |  6882.00 |  6600.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-02 09:15 | 01-07 15:00 |
| **Y   ** | 1h  | LONG  |  6696.00 |  7140.00 |  6720.00 |  6600.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-31 09:15 | 01-07 09:15 |
| Y    | 1d  | LONG  |  6342.00 |  6646.00 |  6482.00 |  6600.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-11 10:45 | 12-25 13:45 |
| **Y   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **Y   ** | 15m | LONG  |  5400.00 |  5450.00 |  5406.00 |  5394.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-28 15:00 | 04-30 10:45 |
| Y    | 1h  | SHORT |  5480.00 |  5400.00 |  5450.00 |  5394.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-27 14:00 | 04-29 09:15 |
| Y    | 1d  | SHORT |  5606.00 |  5276.00 |  5526.00 |  5394.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-25 13:45 | 04-23 13:45 |
| Y    | 1w  | LONG  |  5114.00 |  5748.00 |  5320.00 |  5394.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-09 09:15 | 05-06 09:15 |
| Y    | 15m | LONG  |  6544.00 |  6690.00 |  6640.00 |  6890.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 09-01 09:15 | 09-02 22:00 |
| Y    | 1h  | LONG  |  6582.00 |  6690.00 |  6640.00 |  6890.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-28 22:00 | 09-02 22:00 |
| Y    | 1d  | LONG  |  6316.00 |  6690.00 |  6544.00 |  6890.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-25 13:45 | 09-01 09:15 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **Y   ** | 15m | LONG  |  8650.00 |  8886.00 |  8680.00 |  8296.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 01-06 22:30 | 01-13 10:15 |
| **Y   ** | 1h  | LONG  |  8650.00 |  8886.00 |  8680.00 |  8296.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 01-06 22:15 | 01-13 10:00 |
| **Y   ** | 1d  | LONG  |  8210.00 |  8744.00 |  8508.00 |  8296.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-22 13:45 | 12-29 13:45 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| Y    | 15m | LONG  |  9002.00 |  9086.00 |  9050.00 |  9210.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-29 11:30 | 05-11 10:15 |
| Y    | 1h  | LONG  |  9002.00 |  9086.00 |  9050.00 |  9210.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-29 11:00 | 05-11 10:15 |
| Y    | 1d  | LONG  |  8932.00 |  9542.00 |  9050.00 |  9210.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-26 13:45 | 05-11 09:30 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **Y   ** | 15m | LONG  |  9260.00 |  9718.00 |  9622.00 |  9580.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-30 22:30 | 09-08 09:15 |
| **Y   ** | 1h  | LONG  |  9326.00 |  9718.00 |  9622.00 |  9580.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 08-27 22:00 | 09-08 09:15 |
| **Y   ** | 1d  | SHORT |  9502.00 |  9000.00 |  9484.00 |  9580.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 08-16 09:15 | 08-31 13:45 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| Y    | 15m | LONG  |  9026.00 |  9798.00 |  9054.00 |  9370.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-06 15:00 | 01-10 09:15 |
| Y    | 1h  | LONG  |  9026.00 |  9798.00 |  9054.00 |  9370.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 01-06 15:00 | 01-10 09:15 |
| Y    | 1d  | LONG  |  8970.00 |  9722.00 |  9066.00 |  9370.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 11-05 13:45 | 12-30 13:45 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **Y   ** | 15m | SHORT | 11710.00 | 11396.00 | 11464.00 | 11478.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-29 13:45 | 05-05 22:00 |
| **Y   ** | 1h  | SHORT | 11724.00 | 11396.00 | 11464.00 | 11478.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 04-29 10:45 | 05-05 22:00 |
| Y    | 1d  | LONG  | 10188.00 | 11704.00 | 10960.00 | 11478.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-15 13:45 | 04-25 13:45 |
| Y    | 1w  | LONG  | 10060.00 | 11760.00 | 10980.00 | 11478.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-28 09:15 | 05-09 09:30 |
| Y    | 15m | SHORT | 10440.00 | 10360.00 | 10400.00 | 10100.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-26 10:45 | 09-06 09:15 |
| Y    | 1h  | SHORT | 10446.00 | 10302.00 | 10400.00 | 10100.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-24 14:00 | 09-06 09:15 |
| Y    | 1d  | LONG  |  9814.00 | 10094.00 |  9900.00 | 10100.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-15 13:45 | 09-02 09:15 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **Y   ** | 15m | LONG  |  9084.00 |  9186.00 |  9106.00 |  8702.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-29 10:45 | 12-30 10:00 |
| **Y   ** | 1h  | LONG  |  9084.00 |  9186.00 |  9106.00 |  8702.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-29 10:45 | 12-30 10:00 |
| **Y   ** | 1d  | LONG  |  8936.00 |  9222.00 |  8986.00 |  8702.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-12 13:45 | 01-03 09:15 |
| **Y   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **Y   ** | 15m | LONG  |  7690.00 |  8100.00 |  7982.00 |  7890.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 05-04 09:30 | 05-04 13:45 |
| Y    | 1h  | LONG  |  7856.00 |  7954.00 |  7860.00 |  7890.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-22 11:00 | 05-05 11:15 |
| Y    | 1d  | SHORT |  8318.00 |  8002.00 |  8266.00 |  7890.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-11 13:45 | 04-18 13:45 |
| Y    | 1w  | LONG  |  7564.00 |  8416.00 |  7592.00 |  7890.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 03-20 09:15 | 05-08 09:15 |
| Y    | 15m | SHORT |  8834.00 |  8690.00 |  8740.00 |  8564.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-31 14:45 | 08-31 22:45 |
| Y    | 1h  | SHORT |  8862.00 |  8704.00 |  8826.00 |  8564.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-29 11:00 | 08-30 09:15 |
| Y    | 1d  | LONG  |  8026.00 |  8578.00 |  8338.00 |  8564.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-03 13:45 | 08-23 09:15 |
| **Y   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| Y    | 15m | SHORT |  7952.00 |  7810.00 |  7900.00 |  7710.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-26 10:15 | 01-02 09:15 |
| Y    | 1h  | SHORT |  7988.00 |  7912.00 |  7960.00 |  7710.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-28 09:15 | 12-28 14:00 |
| Y    | 1d  | SHORT |  8268.00 |  8128.00 |  8136.00 |  7710.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-07 10:45 | 12-12 09:15 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| Y    | 15m | SHORT |  7750.00 |  7328.00 |  7710.00 |  7680.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-07 21:30 | 05-15 22:00 |
| Y    | 1h  | SHORT |  7750.00 |  7328.00 |  7710.00 |  7680.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-07 21:30 | 05-15 22:00 |
| **Y   ** | 1d  | SHORT |  7786.00 |  7394.00 |  7678.00 |  7680.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 04-12 13:45 | 04-24 09:15 |
| Y    | 1w  | SHORT |  8030.00 |  7394.00 |  7950.00 |  7680.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 03-18 09:15 | 05-06 09:15 |
| Y    | 15m | SHORT |  7800.00 |  7588.00 |  7750.00 |  7540.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-30 21:45 | 09-05 22:00 |
| Y    | 1h  | SHORT |  7800.00 |  7588.00 |  7750.00 |  7540.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-30 21:15 | 09-05 22:00 |
| Y    | 1d  | LONG  |  7322.00 |  7476.00 |  7358.00 |  7540.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 08-16 13:45 | 08-22 09:15 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| Y    | 15m | SHORT |  7804.00 |  7740.00 |  7790.00 |  7550.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 12-30 21:15 | 12-31 10:15 |
| **Y   ** | 1h  | LONG  |  7672.00 |  7776.00 |  7684.00 |  7550.00 | ✅ ✅ ✅ ❌ | ❌ | —     | 12-24 13:45 | 12-25 23:00 |
| Y    | 1d  | SHORT |  8270.00 |  7930.00 |  8148.00 |  7550.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-29 10:45 | 12-11 13:45 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| Y    | 15m | LONG  |  7860.00 |  7998.00 |  7892.00 |  7950.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-30 09:15 | 05-07 14:45 |
| **Y   ** | 1h  | SHORT |  8040.00 |  7850.00 |  7916.00 |  7950.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 04-25 11:00 | 04-28 23:00 |
| Y    | 1d  | LONG  |  7668.00 |  8040.00 |  7850.00 |  7950.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-16 13:45 | 04-28 13:45 |
| **Y   ** | 1w  | —     |      N/A |      N/A |      N/A |      N/A | — | ❌ | —     |          — |          — |
| **Y   ** | 15m | SHORT |  8490.00 |  7916.00 |  8268.00 |  8268.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 09-05 15:00 | 09-11 10:00 |
| **Y   ** | 1h  | SHORT |  8490.00 |  7916.00 |  8268.00 |  8268.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT | 09-05 15:00 | 09-11 10:00 |
| Y    | 1d  | SHORT |  8584.00 |  8350.00 |  8460.00 |  8268.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 08-25 13:45 | 09-03 10:45 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| **Y   ** | 15m | LONG  |  8074.00 |  8278.00 |  8228.00 |  8228.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 01-05 13:45 | 01-08 22:00 |
| **Y   ** | 1h  | LONG  |  8184.00 |  8230.00 |  8228.00 |  8228.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  | 12-15 09:15 | 01-08 22:00 |
| Y    | 1d  | LONG  |  7882.00 |  8168.00 |  8074.00 |  8228.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 12-19 10:45 | 01-05 13:45 |
| Y    | 1w  | SHORT |  8402.00 |  7882.00 |  8278.00 |  8228.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 11-17 09:15 | 01-05 10:00 |
| Y    | 15m | SHORT |  8490.00 |  8455.00 |  8473.00 |  8400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 04-20 15:00 | 05-08 22:30 |
| Y    | 1h  | SHORT |  8651.00 |  8023.00 |  8505.00 |  8400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 10:00 | 05-11 22:30 |
| Y    | 1d  | SHORT |  8651.00 |  8023.00 |  8505.00 |  8400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-06 09:15 | 05-11 13:45 |
| Y    | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| Y    | 15m | LONG  |  8310.00 |  8396.00 |  8352.00 |  8355.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-16 14:00 | 06-17 09:15 |
| Y    | 1h  | LONG  |  8270.00 |  8415.00 |  8321.00 |  8355.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-15 21:15 | 06-18 14:00 |
| Y    | 1d  | SHORT |  8630.00 |  8272.00 |  8383.00 |  8339.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-03 13:45 | 06-11 13:30 |
| Y    | 1w  | SHORT |  8682.00 |  8272.00 |  8415.00 |  8339.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 05-18 08:00 | 06-15 09:15 |
| ZC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| ZC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| ZC   | 1d  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| ZC   | 1w  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| ZN   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| ZN   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |          — |          — |
| ZN   | 1d  | LONG  | 23560.00 | 25175.00 | 24580.00 | 24620.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 04-30 00:00 | 05-28 00:00 |
| ZN   | 1w  | SHORT | 26985.00 | 22350.00 | 25355.00 | 24620.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 01-27 00:00 | 06-02 00:00 |
| ZN   | 15m | SHORT | 24860.00 | 24680.00 | 24780.00 | 24770.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-18 00:45 | 06-18 14:15 |
| ZN   | 1h  | LONG  | 24635.00 | 24740.00 | 24680.00 | 24770.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  | 06-16 21:15 | 06-18 11:00 |
| ZN   | 1d  | LONG  | 24070.00 | 24890.00 | 24600.00 | 24710.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-11 13:30 | 06-17 10:45 |
| ZN   | 1w  | SHORT | 25355.00 | 24070.00 | 24925.00 | 24710.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT | 06-01 09:15 | 06-15 09:15 |

## 🔍 模式识别分析

**失败品种**: 41 个品种有失败条目。

- **EB**: 26 次失败 — 1w(—), 15m(✅ ✅ ✅ ❌), 1d(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌)
- **Y**: 25 次失败 — 1h(✅ ✅ ✅ ❌), 1w(—), 15m(✅ ✅ ✅ ❌), 1d(✅ ✅ ✅ ❌)
- **P**: 23 次失败 — 15m(✅ ✅ ✅ ❌), 1d(✅ ✅ ✅ ❌), 1w(—), 1h(✅ ✅ ✅ ❌)
- **L**: 22 次失败 — 1w(—), 1d(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌), 15m(✅ ✅ ✅ ❌)
- **PG**: 22 次失败 — 15m(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌), 1w(—), 1d(✅ ✅ ✅ ❌)
- **RB**: 20 次失败 — 15m(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌), 1d(✅ ✅ ✅ ❌), 1w(✅ ✅ ✅ ❌)
- **TA**: 11 次失败 — 1w(—), 15m(✅ ✅ ✅ ❌), 1d(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌)
- **I**: 6 次失败 — 1d(✅ ✅ ✅ ❌), 1w(✅ ✅ ✅ ❌)
- **CF**: 4 次失败 — 1d(✅ ✅ ✅ ❌), 1w(✅ ✅ ✅ ❌), 15m(✅ ✅ ✅ ❌)
- **CJ**: 4 次失败 — 1d(✅ ✅ ✅ ❌), 1w(✅ ✅ ✅ ❌), 15m(✅ ✅ ✅ ❌)
- **AG**: 3 次失败 — 1d(✅ ✅ ✅ ❌), 1w(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌)
- **C**: 3 次失败 — 1w(✅ ✅ ✅ ❌), 15m(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌)
- **JD**: 3 次失败 — 1w(✅ ✅ ✅ ❌), 15m(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌)
- **LH**: 3 次失败 — 1w(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌), 1d(✅ ✅ ✅ ❌)
- **SN**: 3 次失败 — 1d(✅ ✅ ✅ ❌), 15m(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌)
- **A**: 2 次失败 — 15m(✅ ✅ ✅ ❌), 1d(✅ ✅ ✅ ❌)
- **B**: 2 次失败 — 1w(✅ ✅ ✅ ❌), 15m(✅ ✅ ✅ ❌)
- **BU**: 2 次失败 — 1d(✅ ✅ ✅ ❌), 1w(✅ ✅ ✅ ❌)
- **FG**: 2 次失败 — 1h(✅ ✅ ✅ ❌), 1w(—)
- **LC**: 2 次失败 — 15m(✅ ✅ ✅ ❌), 1d(✅ ✅ ✅ ❌)
- **NI**: 2 次失败 — 1d(✅ ✅ ✅ ❌), 1w(✅ ✅ ✅ ❌)
- **OI**: 2 次失败 — 15m(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌)
- **SC**: 2 次失败 — 1w(✅ ✅ ✅ ❌)
- **SP**: 2 次失败 — 15m(✅ ✅ ✅ ❌), 1h(✅ ✅ ✅ ❌)
- **AL**: 1 次失败 — 15m(✅ ✅ ✅ ❌)
- **AU**: 1 次失败 — 1d(✅ ✅ ✅ ❌)
- **BR**: 1 次失败 — 1w(✅ ✅ ✅ ❌)
- **CS**: 1 次失败 — 1h(✅ ✅ ✅ ❌)
- **CU**: 1 次失败 — 1h(✅ ✅ ✅ ❌)
- **M**: 1 次失败 — 1d(✅ ✅ ✅ ❌)
- **MA**: 1 次失败 — 1d(✅ ✅ ✅ ❌)
- **PB**: 1 次失败 — 1w(✅ ✅ ✅ ❌)
- **PR**: 1 次失败 — 1w(✅ ✅ ✅ ❌)
- **PS**: 1 次失败 — 1w(✅ ✅ ✅ ❌)
- **RM**: 1 次失败 — 15m(✅ ✅ ✅ ❌)
- **RR**: 1 次失败 — 1d(✅ ✅ ✅ ❌)
- **SA**: 1 次失败 — 1w(✅ ✅ ✅ ❌)
- **SI**: 1 次失败 — 1d(✅ ✅ ✅ ❌)
- **SM**: 1 次失败 — 1w(✅ ✅ ✅ ❌)
- **SR**: 1 次失败 — 1h(✅ ✅ ✅ ❌)
- **SS**: 1 次失败 — 15m(✅ ✅ ✅ ❌)

**条件失败分布分析**:

- C1 (第一笔方向): 0 次
- C2 (第二笔方向): 0 次
- C3 (C 不破 A):  0 次
- C4 (最新价方向): 180 次

## 📌 结论

🔴 **发现 213 条标点失败的品种×周期组合。**

建议：
1. 优先排查 C4（最新价未突破 C 点）— 行情自然现象
2. 排除 C4 后，分析其余 C1/C2/C3 失败是否指向系统性算法偏差
3. 按计划进入 Step 3 修复
