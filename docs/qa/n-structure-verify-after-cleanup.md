# N 型结构算法全量验证报告 — （不带参数，默认模式）

> **生成时间**: 2026-06-26 03:31:22 CST
>
> 验证范围: 62 个主要品种 × 4 周期 = 248 条目
> 验证方法: 从 DB 读极值点 → `_merge_same_type()` → `_find_n_structure_forward()`
> 参数模式: （不带参数，默认模式）
> 方向预判: 否 · current_price传入: 否

## 📊 整体统计

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 全部通过 | 94 | 37.9% |
| ❌ 有失败条件 | 30 | 12.1% |
| ⚠️ 数据不足 | 124 | 50.0% |
| **总计** | **248** | **100%** |

### 📈 按周期统计

| 周期 | 通过 | 失败 | N/A | 合计 | 通过率 |
|------|------|------|-----|------|--------|
| 15m | 0 | 0 | 62 | 62 | — |
| 1h  | 0 | 0 | 62 | 62 | — |
| 1d  | 42 | 20 | 0 | 62 | 68% |
| 1w  | 52 | 10 | 0 | 62 | 84% |

## ❌ 未通过验证的品种×周期（{len(fail_list)} 条）

### A — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 5046.00 |
| B 价 | 4694.00 |
| C 价 | 4901.00 |
| 最新价 | 4935.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 30 | C 索引 | 32 |

**极值点序列** (swing: 60, merged: 26):
```
  [ 0] PEAK   price= 2908.00 time=09-02 15:00
  [ 1] TROUGH price= 2708.00 time=09-16 15:00
  [ 2] PEAK   price= 2771.00 time=09-22 15:00
  [ 3] TROUGH price= 2702.00 time=10-11 15:00
  [ 4] PEAK   price= 2900.00 time=10-13 15:00
  [ 5] TROUGH price= 2713.00 time=10-24 15:00
  [ 6] PEAK   price= 3189.00 time=10-31 15:00
  [ 7] TROUGH price= 2708.00 time=11-09 15:00
  [ 8] PEAK   price= 2775.00 time=11-14 15:00
  [ 9] TROUGH price= 2505.00 time=11-28 00:00
  [10] PEAK   price= 3035.00 time=12-26 00:00
  [11] TROUGH price= 2677.00 time=12-30 00:00
  [12] PEAK   price= 2796.00 time=01-05 00:00
  [13] TROUGH price= 2621.00 time=02-08 00:00
  [14] PEAK   price= 3503.00 time=02-10 00:00
  [15] TROUGH price= 3278.00 time=02-16 00:00
  [16] PEAK   price= 3513.00 time=03-03 00:00
  [17] TROUGH price= 3350.00 time=03-09 00:00
  [18] PEAK   price= 3806.00 time=04-24 00:00
  [19] TROUGH price= 3627.00 time=04-28 00:00
  [20] PEAK   price= 3832.00 time=05-12 00:00
  [21] TROUGH price= 3522.00 time=05-22 00:00
  [22] PEAK   price= 3787.00 time=05-24 00:00
  [23] TROUGH price= 3576.00 time=06-01 00:00
  [24] PEAK   price= 3735.00 time=06-06 00:00
  [25] TROUGH price= 3282.00 time=06-20 00:00
```

**失败详情:**
```
  ❌ 最新(4935.00) < C(4901.00) = False
```
---

### AG — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 15070.00 |
| B 价 | 20559.00 |
| C 价 | 17554.00 |
| 最新价 | 15622.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 50 | C 索引 | 52 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] PEAK   price= 6154.00 time=06-05 05:45
  [ 1] TROUGH price= 5632.00 time=06-26 05:45
  [ 2] PEAK   price= 7506.00 time=09-11 05:45
  [ 3] TROUGH price= 6495.00 time=10-30 05:45
  [ 4] PEAK   price= 7073.00 time=11-27 05:45
  [ 5] TROUGH price= 6193.00 time=01-04 05:45
  [ 6] PEAK   price= 6715.00 time=01-22 05:45
  [ 7] TROUGH price= 3710.00 time=06-25 05:45
  [ 8] PEAK   price= 4134.00 time=07-16 05:45
  [ 9] TROUGH price= 3897.00 time=08-06 05:45
  [10] PEAK   price= 5085.00 time=08-27 05:45
  [11] TROUGH price= 4246.00 time=10-15 05:45
  [12] PEAK   price= 4636.00 time=10-29 05:45
  [13] TROUGH price= 4049.00 time=12-03 05:45
  [14] PEAK   price= 4310.00 time=12-10 05:45
  [15] TROUGH price= 4010.00 time=01-07 05:45
  [16] PEAK   price= 4212.00 time=01-14 05:45
  [17] TROUGH price= 4040.00 time=01-28 05:45
  [18] PEAK   price= 4483.00 time=02-11 05:45
  [19] TROUGH price= 3989.00 time=04-15 05:45
  [20] PEAK   price= 4177.00 time=04-22 05:45
  [21] TROUGH price= 4038.00 time=05-06 05:45
  [22] PEAK   price= 4169.00 time=05-13 05:45
  [23] TROUGH price= 4019.00 time=06-03 05:45
  [24] PEAK   price= 4392.00 time=06-17 05:45
  [25] TROUGH price= 4260.00 time=07-01 05:45
  [26] PEAK   price= 4425.00 time=07-08 05:45
  [27] TROUGH price= 4075.00 time=08-19 05:45
  [28] PEAK   price= 4179.00 time=08-26 05:45
  [29] TROUGH price= 3724.00 time=09-23 05:45
  [30] PEAK   price= 3989.00 time=10-08 05:45
  [31] TROUGH price= 3155.00 time=11-04 05:45
  [32] PEAK   price= 3503.00 time=11-18 05:45
  [33] TROUGH price= 3229.00 time=11-25 05:45
  [34] PEAK   price= 3720.00 time=12-09 05:45
  [35] TROUGH price= 3366.00 time=12-23 05:45
  [36] PEAK   price= 3934.00 time=01-20 05:45
  [37] TROUGH price= 3375.00 time=03-10 05:45
  [38] PEAK   price= 3710.00 time=03-24 05:45
  [39] TROUGH price= 3427.00 time=04-21 05:45
  [40] PEAK   price= 3867.00 time=05-12 05:45
  [41] TROUGH price= 3520.00 time=06-09 05:45
  [42] PEAK   price= 3630.00 time=06-16 05:45
  [43] TROUGH price= 3150.00 time=07-21 05:45
  [44] PEAK   price= 3563.00 time=08-11 05:45
  [45] TROUGH price= 3236.00 time=08-25 05:45
  [46] PEAK   price= 3453.00 time=09-15 05:45
  [47] TROUGH price= 3273.00 time=09-29 05:45
  [48] PEAK   price= 3525.00 time=10-08 05:45
  [49] TROUGH price= 3170.00 time=11-17 05:45
  [50] PEAK   price= 3401.00 time=12-01 05:45 ← A
  [51] TROUGH price= 3222.00 time=12-15 05:45
  [52] PEAK   price= 3343.00 time=12-22 05:45 ← C
  [53] TROUGH price= 3250.00 time=12-29 05:45
  [54] PEAK   price= 3390.00 time=01-05 05:45
  [55] TROUGH price= 3262.00 time=01-12 05:45
  [56] PEAK   price= 3500.00 time=02-15 05:45
  [57] TROUGH price= 3304.00 time=02-23 05:45
  [58] PEAK   price= 3550.00 time=03-08 05:45
  [59] TROUGH price= 3332.00 time=04-05 05:45
  [60] PEAK   price= 3888.00 time=05-03 05:45
  [61] TROUGH price= 3546.00 time=05-24 05:45
  [62] PEAK   price= 4599.00 time=07-05 05:45
  [63] TROUGH price= 4243.00 time=07-19 05:45
  [64] PEAK   price= 4588.00 time=08-02 05:45
  [65] TROUGH price= 4040.00 time=08-23 05:45
  [66] PEAK   price= 4458.00 time=09-06 05:45
  [67] TROUGH price= 4210.00 time=09-13 05:45
  [68] PEAK   price= 4444.00 time=09-20 05:45
  [69] TROUGH price= 3952.00 time=10-10 05:45
  [70] PEAK   price= 4479.00 time=11-08 05:45
  [71] TROUGH price= 3943.00 time=12-20 05:45
  [72] PEAK   price= 4183.00 time=01-17 05:45
  [73] TROUGH price= 4020.00 time=01-24 05:45
  [74] PEAK   price= 4335.00 time=02-28 05:45
  [75] TROUGH price= 4018.00 time=03-07 05:45
  [76] PEAK   price= 4337.00 time=04-11 05:45
  [77] TROUGH price= 3875.00 time=05-02 05:45
  [78] PEAK   price= 4154.00 time=05-23 05:45
  [79] TROUGH price= 4052.00 time=05-31 05:45
```

**失败详情:**
```
  ❌ 最新(15622.00) > C(17554.00) = False
```
---

### AL — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 23100.00 |
| B 价 | 25675.00 |
| C 价 | 24020.00 |
| 最新价 | 23905.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 55 | C 索引 | 57 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] PEAK   price=17240.00 time=03-15 05:45
  [ 1] TROUGH price=16490.00 time=04-12 05:45
  [ 2] PEAK   price=16890.00 time=05-10 05:45
  [ 3] TROUGH price=16530.00 time=05-17 05:45
  [ 4] PEAK   price=17100.00 time=06-14 05:45
  [ 5] TROUGH price=16240.00 time=07-05 05:45
  [ 6] PEAK   price=16790.00 time=07-12 05:45
  [ 7] TROUGH price=16450.00 time=09-13 05:45
  [ 8] PEAK   price=22800.00 time=02-07 05:45
  [ 9] TROUGH price=18880.00 time=02-28 05:45
  [10] PEAK   price=24830.00 time=05-09 05:45
  [11] TROUGH price=18130.00 time=08-15 05:45
  [12] PEAK   price=21330.00 time=09-05 05:45
  [13] TROUGH price=19390.00 time=10-31 05:45
  [14] PEAK   price=20700.00 time=12-12 05:45
  [15] TROUGH price=19090.00 time=01-30 05:45
  [16] PEAK   price=20390.00 time=02-26 05:45
  [17] TROUGH price=19190.00 time=04-03 05:45
  [18] PEAK   price=20900.00 time=05-08 05:45
  [19] TROUGH price=18880.00 time=06-26 05:45
  [20] PEAK   price=19830.00 time=07-24 05:45
  [21] TROUGH price=18710.00 time=08-14 05:45
  [22] PEAK   price=19540.00 time=09-25 05:45
  [23] TROUGH price=18100.00 time=10-23 05:45
  [24] PEAK   price=18930.00 time=11-06 05:45
  [25] TROUGH price=17320.00 time=11-20 05:45
  [26] PEAK   price=18780.00 time=12-18 05:45
  [27] TROUGH price=18080.00 time=01-01 05:45
  [28] PEAK   price=18630.00 time=01-08 05:45
  [29] TROUGH price=18050.00 time=01-15 05:45
  [30] PEAK   price=21495.00 time=03-04 05:45
  [31] TROUGH price=18810.00 time=03-18 05:45
  [32] PEAK   price=19975.00 time=03-25 05:45
  [33] TROUGH price=18720.00 time=04-22 05:45
  [34] PEAK   price=19590.00 time=05-13 05:45
  [35] TROUGH price=18660.00 time=06-03 05:45
  [36] PEAK   price=19920.00 time=07-08 05:45
  [37] TROUGH price=13405.00 time=10-07 05:45
  [38] PEAK   price=14710.00 time=10-14 05:45
  [39] TROUGH price=13155.00 time=10-21 05:45
  [40] PEAK   price=14580.00 time=10-28 05:45
  [41] TROUGH price=13310.00 time=11-04 05:45
  [42] PEAK   price=13875.00 time=11-18 05:45
  [43] TROUGH price=10125.00 time=12-09 05:45
  [44] PEAK   price=12630.00 time=01-06 05:45
  [45] TROUGH price=11105.00 time=01-20 05:45
  [46] PEAK   price=12325.00 time=02-03 05:45
  [47] TROUGH price=11330.00 time=02-24 05:45
  [48] PEAK   price=13170.00 time=03-24 05:45
  [49] TROUGH price=12345.00 time=03-31 05:45
  [50] PEAK   price=13610.00 time=04-07 05:45
  [51] TROUGH price=12240.00 time=04-28 05:45
  [52] PEAK   price=13645.00 time=06-09 05:45
  [53] TROUGH price=13150.00 time=06-23 05:45
  [54] PEAK   price=13670.00 time=06-30 05:45
  [55] TROUGH price=13280.00 time=07-07 05:45 ← A
  [56] PEAK   price=15470.00 time=08-11 05:45
  [57] TROUGH price=14260.00 time=09-08 05:45 ← C
  [58] PEAK   price=15560.00 time=10-27 05:45
  [59] TROUGH price=15080.00 time=11-10 05:45
  [60] PEAK   price=16630.00 time=12-08 05:45
  [61] TROUGH price=16200.00 time=12-22 05:45
  [62] PEAK   price=18685.00 time=01-05 05:45
  [63] TROUGH price=15935.00 time=01-26 05:45
  [64] PEAK   price=17485.00 time=02-22 05:45
  [65] TROUGH price=16320.00 time=03-23 05:45
  [66] PEAK   price=17210.00 time=04-13 05:45
  [67] TROUGH price=14770.00 time=05-18 05:45
  [68] PEAK   price=15480.00 time=05-25 05:45
  [69] TROUGH price=14020.00 time=06-08 05:45
  [70] PEAK   price=15210.00 time=06-17 05:45
  [71] TROUGH price=14580.00 time=06-29 05:45
  [72] PEAK   price=15055.00 time=07-06 05:45
  [73] TROUGH price=14790.00 time=07-13 05:45
  [74] PEAK   price=15930.00 time=08-03 05:45
  [75] TROUGH price=15225.00 time=08-10 05:45
  [76] PEAK   price=16010.00 time=09-07 05:45
  [77] TROUGH price=15500.00 time=09-28 05:45
  [78] PEAK   price=17400.00 time=11-09 05:45
  [79] TROUGH price=15940.00 time=11-16 05:45
```

**失败详情:**
```
  ❌ 最新(23905.00) > C(24020.00) = False
```
---

### AP — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 9298.00 |
| B 价 | 7505.00 |
| C 价 | 7715.00 |
| 最新价 | 9485.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 18 | C 索引 | 32 |

**极值点序列** (swing: 60, merged: 23):
```
  [ 0] TROUGH price= 6471.00 time=02-23 00:00
  [ 1] PEAK   price= 7313.00 time=03-12 00:00
  [ 2] TROUGH price= 6892.00 time=03-15 00:00
  [ 3] PEAK   price= 7445.00 time=04-02 00:00
  [ 4] TROUGH price= 6978.00 time=04-12 00:00
  [ 5] PEAK   price= 9544.00 time=05-31 00:00
  [ 6] TROUGH price= 8580.00 time=06-11 00:00
  [ 7] PEAK   price=10206.00 time=06-19 00:00
  [ 8] TROUGH price= 9103.00 time=06-26 00:00
  [ 9] PEAK   price= 9715.00 time=06-29 00:00
  [10] TROUGH price= 9186.00 time=07-05 00:00
  [11] PEAK   price=12315.00 time=08-20 00:00
  [12] TROUGH price=11265.00 time=08-24 00:00
  [13] PEAK   price=12396.00 time=09-19 00:00
  [14] TROUGH price=10611.00 time=10-22 00:00
  [15] PEAK   price=12626.00 time=11-16 00:00
  [16] TROUGH price=11300.00 time=11-29 00:00
  [17] PEAK   price=11488.00 time=12-27 00:00
  [18] TROUGH price=10476.00 time=01-14 00:00 ← A
  [19] PEAK   price=11474.00 time=02-25 00:00
  [20] TROUGH price=10920.00 time=03-04 00:00
  [21] PEAK   price=11414.00 time=03-08 00:00
  [22] TROUGH price=11131.00 time=03-15 00:00
```

**失败详情:**
```
  ❌ 最新(9485.00) < C(7715.00) = False
```
---

### B — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3711.00 |
| B 价 | 3515.00 |
| C 价 | 3611.00 |
| 最新价 | 3858.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 30 | C 索引 | 32 |

**极值点序列** (swing: 60, merged: 20):
```
  [ 0] PEAK   price= 4170.00 time=09-19 00:00
  [ 1] TROUGH price= 4010.00 time=09-25 00:00
  [ 2] PEAK   price= 4600.00 time=11-15 00:00
  [ 3] TROUGH price= 4150.00 time=11-20 00:00
  [ 4] PEAK   price= 4938.00 time=01-14 00:00
  [ 5] TROUGH price= 4482.00 time=01-24 00:00
  [ 6] PEAK   price= 5538.00 time=03-04 00:00
  [ 7] TROUGH price= 4501.00 time=03-21 00:00
  [ 8] PEAK   price= 5050.00 time=03-26 00:00
  [ 9] TROUGH price= 3865.00 time=04-03 00:00
  [10] PEAK   price= 5399.00 time=04-09 00:00
  [11] TROUGH price= 4152.00 time=04-16 00:00
  [12] PEAK   price= 5199.00 time=04-18 00:00
  [13] TROUGH price= 4040.00 time=04-29 00:00
  [14] PEAK   price= 5414.00 time=05-13 00:00
  [15] TROUGH price= 4292.00 time=05-16 00:00
  [16] PEAK   price= 4660.00 time=05-27 00:00
  [17] TROUGH price= 4419.00 time=06-10 00:00
  [18] PEAK   price= 5595.00 time=06-16 00:00
  [19] TROUGH price= 4810.00 time=06-23 00:00
```

**失败详情:**
```
  ❌ 最新(3858.00) < C(3611.00) = False
```
---

### C — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2307.00 |
| B 价 | 2420.00 |
| C 价 | 2337.00 |
| 最新价 | 2335.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 40 | C 索引 | 52 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price= 1144.00 time=02-01 05:45
  [ 1] PEAK   price= 1355.00 time=03-29 05:45
  [ 2] TROUGH price= 1265.00 time=05-10 05:45
  [ 3] PEAK   price= 1306.00 time=05-24 05:45
  [ 4] TROUGH price= 1251.00 time=05-31 05:45
  [ 5] PEAK   price= 1308.00 time=06-14 05:45
  [ 6] TROUGH price= 1275.00 time=06-28 05:45
  [ 7] PEAK   price= 1305.00 time=07-05 05:45
  [ 8] TROUGH price= 1193.00 time=08-16 05:45
  [ 9] PEAK   price= 1301.00 time=10-11 05:45
  [10] TROUGH price= 1225.00 time=10-25 05:45
  [11] PEAK   price= 1325.00 time=11-01 05:45
  [12] TROUGH price= 1236.00 time=11-22 05:45
  [13] PEAK   price= 1398.00 time=01-03 05:45
  [14] TROUGH price= 1324.00 time=01-17 05:45
  [15] PEAK   price= 1538.00 time=02-07 05:45
  [16] TROUGH price= 1398.00 time=03-14 05:45
  [17] PEAK   price= 1453.00 time=04-04 05:45
  [18] TROUGH price= 1374.00 time=04-19 05:45
  [19] PEAK   price= 1554.00 time=05-30 05:45
  [20] TROUGH price= 1375.00 time=08-08 05:45
  [21] PEAK   price= 1429.00 time=08-15 05:45
  [22] TROUGH price= 1392.00 time=09-19 05:45
  [23] PEAK   price= 1754.00 time=11-21 05:45
  [24] TROUGH price= 1656.00 time=01-09 05:45
  [25] PEAK   price= 1795.00 time=01-16 05:45
  [26] TROUGH price= 1685.00 time=02-13 05:45
  [27] PEAK   price= 1744.00 time=02-26 05:45
  [28] TROUGH price= 1628.00 time=04-17 05:45
  [29] PEAK   price= 1745.00 time=05-22 05:45
  [30] TROUGH price= 1470.00 time=07-24 05:45
  [31] PEAK   price= 1689.00 time=09-11 05:45
  [32] TROUGH price= 1615.00 time=09-25 05:45
  [33] PEAK   price= 1675.00 time=10-09 05:45
  [34] TROUGH price= 1633.00 time=10-23 05:45
  [35] PEAK   price= 1816.00 time=11-20 05:45
  [36] TROUGH price= 1676.00 time=01-01 05:45
  [37] PEAK   price= 1850.00 time=01-08 05:45
  [38] TROUGH price= 1709.00 time=01-22 05:45
  [39] PEAK   price= 1827.00 time=02-13 05:45
  [40] TROUGH price= 1781.00 time=02-26 05:45 ← A
  [41] PEAK   price= 1900.00 time=03-04 05:45
  [42] TROUGH price= 1736.00 time=03-18 05:45
  [43] PEAK   price= 1958.00 time=03-25 05:45
  [44] TROUGH price= 1867.00 time=04-08 05:45
  [45] PEAK   price= 1990.00 time=05-06 05:45
  [46] TROUGH price= 1868.00 time=05-27 05:45
  [47] PEAK   price= 1953.00 time=07-08 05:45
  [48] TROUGH price= 1706.00 time=08-19 05:45
  [49] PEAK   price= 1864.00 time=08-26 05:45
  [50] TROUGH price= 1743.00 time=09-16 05:45
  [51] PEAK   price= 1799.00 time=09-23 05:45
  [52] TROUGH price= 1600.00 time=10-07 05:45 ← C
  [53] PEAK   price= 1710.00 time=10-14 05:45
  [54] TROUGH price= 1440.00 time=12-09 05:45
  [55] PEAK   price= 1707.00 time=02-17 05:45
  [56] TROUGH price= 1660.00 time=03-03 05:45
  [57] PEAK   price= 1725.00 time=03-17 05:45
  [58] TROUGH price= 1678.00 time=03-31 05:45
  [59] PEAK   price= 1706.00 time=04-07 05:45
  [60] TROUGH price= 1645.00 time=04-21 05:45
  [61] PEAK   price= 1689.00 time=05-12 05:45
  [62] TROUGH price= 1648.00 time=05-19 05:45
  [63] PEAK   price= 1692.00 time=06-02 05:45
  [64] TROUGH price= 1601.00 time=06-09 05:45
  [65] PEAK   price= 1637.00 time=06-23 05:45
  [66] TROUGH price= 1596.00 time=07-07 05:45
  [67] PEAK   price= 1778.00 time=08-25 05:45
  [68] TROUGH price= 1706.00 time=09-22 05:45
  [69] PEAK   price= 1755.00 time=10-13 05:45
  [70] TROUGH price= 1730.00 time=10-27 05:45
  [71] PEAK   price= 1881.00 time=12-15 05:45
  [72] TROUGH price= 1843.00 time=12-22 05:45
  [73] PEAK   price= 1936.00 time=01-05 05:45
  [74] TROUGH price= 1841.00 time=02-02 05:45
  [75] PEAK   price= 1883.00 time=02-23 05:45
  [76] TROUGH price= 1856.00 time=03-02 05:45
  [77] PEAK   price= 1946.00 time=04-06 05:45
  [78] TROUGH price= 1911.00 time=04-27 05:45
  [79] PEAK   price= 1984.00 time=05-18 05:45
```

**失败详情:**
```
  ❌ 最新(2335.00) > C(2337.00) = False
```
---

### CF — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 15170.00 |
| B 价 | 16955.00 |
| C 价 | 15855.00 |
| 最新价 | 15415.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 29 | C 索引 | 31 |

**极值点序列** (swing: 60, merged: 26):
```
  [ 0] PEAK   price=14645.00 time=09-06 15:00
  [ 1] TROUGH price=13835.00 time=09-13 15:00
  [ 2] PEAK   price=14680.00 time=09-20 15:00
  [ 3] TROUGH price=14155.00 time=09-21 15:00
  [ 4] PEAK   price=15735.00 time=10-26 15:00
  [ 5] TROUGH price=15000.00 time=10-28 15:00
  [ 6] PEAK   price=15490.00 time=11-14 15:00
  [ 7] TROUGH price=15005.00 time=11-17 15:00
  [ 8] PEAK   price=15500.00 time=11-22 00:00
  [ 9] TROUGH price=14640.00 time=12-02 00:00
  [10] PEAK   price=15675.00 time=12-19 00:00
  [11] TROUGH price=15030.00 time=12-22 00:00
  [12] PEAK   price=15565.00 time=01-13 00:00
  [13] TROUGH price=15150.00 time=01-19 00:00
  [14] PEAK   price=15795.00 time=02-06 00:00
  [15] TROUGH price=14540.00 time=03-06 00:00
  [16] PEAK   price=14980.00 time=03-10 00:00
  [17] TROUGH price=14255.00 time=03-23 00:00
  [18] PEAK   price=14660.00 time=03-31 00:00
  [19] TROUGH price=14350.00 time=04-11 00:00
  [20] PEAK   price=14790.00 time=04-20 00:00
  [21] TROUGH price=14110.00 time=05-08 00:00
  [22] PEAK   price=14495.00 time=05-15 00:00
  [23] TROUGH price=14165.00 time=05-22 00:00
  [24] PEAK   price=14880.00 time=06-15 00:00
  [25] TROUGH price=13930.00 time=07-21 00:00
```

**失败详情:**
```
  ❌ 最新(15415.00) > C(15855.00) = False
```
---

### CJ — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8720.00 |
| B 价 | 9265.00 |
| C 价 | 8880.00 |
| 最新价 | 8880.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 39 | C 索引 | 47 |

**极值点序列** (swing: 80, merged: 53):
```
  [ 0] PEAK   price=10935.00 time=05-21 00:00
  [ 1] TROUGH price= 9605.00 time=06-04 00:00
  [ 2] PEAK   price=10675.00 time=06-25 00:00
  [ 3] TROUGH price=10155.00 time=07-02 05:45
  [ 4] PEAK   price=10645.00 time=07-09 05:45
  [ 5] TROUGH price= 9995.00 time=07-23 00:00
  [ 6] PEAK   price=11000.00 time=08-06 05:45
  [ 7] TROUGH price=10525.00 time=08-27 05:45
  [ 8] PEAK   price=11555.00 time=09-03 00:00
  [ 9] TROUGH price= 9770.00 time=10-15 00:00
  [10] PEAK   price=11260.00 time=11-11 15:00
  [11] TROUGH price=10580.00 time=12-02 15:00
  [12] PEAK   price=11015.00 time=12-24 00:00
  [13] TROUGH price= 9890.00 time=02-03 15:00
  [14] PEAK   price=10665.00 time=02-17 15:00
  [15] TROUGH price=10275.00 time=02-24 15:00
  [16] PEAK   price=10710.00 time=02-25 00:00
  [17] TROUGH price=10200.00 time=03-09 15:00
  [18] PEAK   price=10580.00 time=03-16 15:00
  [19] TROUGH price= 9670.00 time=03-23 15:00
  [20] PEAK   price=10465.00 time=04-21 00:00
  [21] TROUGH price= 9845.00 time=05-26 00:00
  [22] PEAK   price=10170.00 time=06-08 15:00
  [23] TROUGH price= 8980.00 time=07-20 15:00
  [24] PEAK   price= 9365.00 time=07-27 15:00
  [25] TROUGH price= 8755.00 time=08-03 15:00
  [26] PEAK   price= 9530.00 time=08-10 15:00
  [27] TROUGH price= 8910.00 time=08-17 15:00
  [28] PEAK   price=10335.00 time=09-07 15:00
  [29] TROUGH price= 9680.00 time=09-28 15:00
  [30] PEAK   price=10250.00 time=10-12 15:00
  [31] TROUGH price= 9715.00 time=10-26 15:00
  [32] PEAK   price=10030.00 time=11-09 15:00
  [33] TROUGH price= 9595.00 time=11-16 15:00
  [34] PEAK   price=10075.00 time=11-17 00:00
  [35] TROUGH price= 9165.00 time=12-07 15:00
  [36] PEAK   price=10145.00 time=12-14 15:00
  [37] TROUGH price= 9705.00 time=12-21 15:00
  [38] PEAK   price=10445.00 time=01-04 15:00
  [39] TROUGH price= 9915.00 time=02-08 15:00 ← A
  [40] PEAK   price=10955.00 time=02-22 15:00
  [41] TROUGH price= 9620.00 time=03-29 15:00
  [42] PEAK   price=10345.00 time=04-19 15:00
  [43] TROUGH price= 8485.00 time=05-17 15:00
  [44] PEAK   price= 9470.00 time=05-18 05:45
  [45] TROUGH price= 8225.00 time=06-15 00:00
  [46] PEAK   price=15005.00 time=08-23 15:00
  [47] TROUGH price=13315.00 time=09-07 00:00 ← C
  [48] PEAK   price=16065.00 time=09-27 15:00
  [49] TROUGH price=13565.00 time=10-11 15:00
  [50] PEAK   price=16465.00 time=10-18 15:00
  [51] TROUGH price=12820.00 time=10-25 15:00
  [52] PEAK   price=17655.00 time=11-22 15:00
```

**失败详情:**
```
  ❌ 最新(8880.00) > C(8880.00) = False
```
---

### I — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 760.00 |
| B 价 | 820.00 |
| C 价 | 777.00 |
| 最新价 | 705.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 47 | C 索引 | 59 |

**极值点序列** (swing: 60, merged: 20):
```
  [ 0] TROUGH price=  913.00 time=10-29 00:00
  [ 1] PEAK   price=  957.00 time=11-04 00:00
  [ 2] TROUGH price=  925.00 time=11-18 00:00
  [ 3] PEAK   price=  956.00 time=12-05 00:00
  [ 4] TROUGH price=  885.00 time=12-23 00:00
  [ 5] PEAK   price=  920.00 time=12-30 00:00
  [ 6] TROUGH price=  843.00 time=01-21 00:00
  [ 7] PEAK   price=  885.00 time=01-23 00:00
  [ 8] TROUGH price=  844.00 time=02-12 00:00
  [ 9] PEAK   price=  878.00 time=02-18 00:00
  [10] TROUGH price=  705.00 time=03-12 00:00
  [11] PEAK   price=  833.00 time=04-08 00:00
  [12] TROUGH price=  695.00 time=05-20 00:00
  [13] PEAK   price=  729.00 time=05-26 00:00
  [14] TROUGH price=  656.00 time=06-17 00:00
  [15] PEAK   price=  725.00 time=07-15 00:00
  [16] TROUGH price=  662.00 time=07-24 00:00
  [17] PEAK   price=  692.00 time=08-05 00:00
  [18] TROUGH price=  570.00 time=09-10 00:00
  [19] PEAK   price=  605.00 time=09-15 00:00
```

**失败详情:**
```
  ❌ 最新(705.00) > C(777.00) = False
```
---

### J — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 1622.00 |
| B 价 | 1877.50 |
| C 价 | 1792.50 |
| 最新价 | 1732.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 29 | C 索引 | 31 |

**极值点序列** (swing: 60, merged: 20):
```
  [ 0] TROUGH price= 2255.00 time=05-06 00:00
  [ 1] PEAK   price= 2444.00 time=05-13 00:00
  [ 2] TROUGH price= 2345.00 time=05-24 00:00
  [ 3] PEAK   price= 2398.00 time=05-26 00:00
  [ 4] TROUGH price= 2270.00 time=06-21 00:00
  [ 5] PEAK   price= 2348.00 time=07-07 00:00
  [ 6] TROUGH price= 2276.00 time=07-22 00:00
  [ 7] PEAK   price= 2314.00 time=08-18 00:00
  [ 8] TROUGH price= 2142.00 time=08-23 00:00
  [ 9] PEAK   price= 2256.00 time=09-08 00:00
  [10] TROUGH price= 1888.00 time=10-20 00:00
  [11] PEAK   price= 2016.00 time=10-28 00:00
  [12] TROUGH price= 1888.00 time=11-10 00:00
  [13] PEAK   price= 2083.00 time=11-15 00:00
  [14] TROUGH price= 1951.00 time=11-24 00:00
  [15] PEAK   price= 2047.00 time=12-01 00:00
  [16] TROUGH price= 1911.00 time=12-15 00:00
  [17] PEAK   price= 2124.00 time=02-09 00:00
  [18] TROUGH price= 2036.00 time=02-16 00:00
  [19] PEAK   price= 2098.00 time=03-02 00:00
```

**失败详情:**
```
  ❌ 最新(1732.00) > C(1792.50) = False
```
---

### LC — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 142000.00 |
| B 价 | 167280.00 |
| C 价 | 152500.00 |
| 最新价 | 147220.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 28 | C 索引 | 32 |

**极值点序列** (swing: 60, merged: 30):
```
  [ 0] TROUGH price=192050.00 time=08-16 00:00
  [ 1] PEAK   price=204350.00 time=08-22 00:00
  [ 2] TROUGH price=180700.00 time=08-29 00:00
  [ 3] PEAK   price=193900.00 time=09-05 00:00
  [ 4] TROUGH price=145000.00 time=09-27 00:00
  [ 5] PEAK   price=175050.00 time=10-16 00:00
  [ 6] TROUGH price=85650.00 time=12-06 00:00
  [ 7] PEAK   price=113800.00 time=12-11 00:00
  [ 8] TROUGH price=95500.00 time=01-09 00:00
  [ 9] PEAK   price=106000.00 time=01-17 00:00
  [10] TROUGH price=92450.00 time=02-20 00:00
  [11] PEAK   price=125000.00 time=03-04 00:00
  [12] TROUGH price=105800.00 time=03-27 00:00
  [13] PEAK   price=117350.00 time=04-10 00:00
  [14] TROUGH price=106100.00 time=04-19 00:00
  [15] PEAK   price=117200.00 time=04-30 00:00
  [16] TROUGH price=101650.00 time=05-15 00:00
  [17] PEAK   price=109450.00 time=05-21 00:00
  [18] TROUGH price=86000.00 time=06-25 00:00
  [19] PEAK   price=96900.00 time=06-27 00:00
  [20] TROUGH price=71700.00 time=08-19 00:00
  [21] PEAK   price=79350.00 time=08-30 00:00
  [22] TROUGH price=69700.00 time=09-06 00:00
  [23] PEAK   price=79800.00 time=09-12 00:00
  [24] TROUGH price=73200.00 time=09-23 00:00
  [25] PEAK   price=84800.00 time=10-08 00:00
  [26] TROUGH price=68250.00 time=10-18 00:00
  [27] PEAK   price=87600.00 time=11-14 00:00
  [28] TROUGH price=73760.00 time=12-19 00:00 ← A
  [29] PEAK   price=81680.00 time=01-20 00:00
```

**失败详情:**
```
  ❌ 最新(147220.00) > C(152500.00) = False
```
---

### LH — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 11800.00 |
| B 价 | 9000.00 |
| C 价 | 11585.00 |
| 最新价 | 11950.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 49 | C 索引 | 51 |

**极值点序列** (swing: 80, merged: 49):
```
  [ 0] TROUGH price=24460.00 time=01-11 15:00
  [ 1] PEAK   price=29805.00 time=02-22 15:00
  [ 2] TROUGH price=26310.00 time=03-29 15:00
  [ 3] PEAK   price=27990.00 time=04-19 15:00
  [ 4] TROUGH price=16675.00 time=06-21 15:00
  [ 5] PEAK   price=19800.00 time=06-22 05:45
  [ 6] TROUGH price=17905.00 time=07-12 15:00
  [ 7] PEAK   price=19070.00 time=07-19 15:00
  [ 8] TROUGH price=17215.00 time=08-02 15:00
  [ 9] PEAK   price=17945.00 time=08-16 15:00
  [10] TROUGH price=13365.00 time=09-22 00:00
  [11] PEAK   price=17670.00 time=10-25 15:00
  [12] TROUGH price=15610.00 time=11-01 15:00
  [13] PEAK   price=16950.00 time=11-22 15:00
  [14] TROUGH price=13920.00 time=12-20 15:00
  [15] PEAK   price=14860.00 time=12-21 05:45
  [16] TROUGH price=13400.00 time=01-04 05:45
  [17] PEAK   price=14045.00 time=01-17 15:00
  [18] TROUGH price=13205.00 time=01-24 15:00
  [19] PEAK   price=14965.00 time=02-07 15:00
  [20] TROUGH price=13780.00 time=02-21 15:00
  [21] PEAK   price=14500.00 time=02-22 05:45
  [22] TROUGH price=12530.00 time=03-14 15:00
  [23] PEAK   price=13235.00 time=03-21 15:00
  [24] TROUGH price=12360.00 time=04-06 00:00
  [25] PEAK   price=19915.00 time=05-16 15:00
  [26] TROUGH price=18450.00 time=05-24 00:00
  [27] PEAK   price=19335.00 time=05-31 05:45
  [28] TROUGH price=18460.00 time=06-06 15:00
  [29] PEAK   price=23290.00 time=07-11 15:00
  [30] TROUGH price=19965.00 time=07-25 15:00
  [31] PEAK   price=23970.00 time=08-23 00:00
  [32] TROUGH price=22645.00 time=09-05 15:00
  [33] PEAK   price=23620.00 time=09-13 05:45
  [34] TROUGH price=21635.00 time=09-20 00:00
  [35] PEAK   price=24300.00 time=10-10 15:00
  [36] TROUGH price=20055.00 time=11-21 15:00
  [37] PEAK   price=21435.00 time=11-28 15:00
  [38] TROUGH price=14035.00 time=01-30 15:00
  [39] PEAK   price=17840.00 time=02-20 15:00
  [40] TROUGH price=14675.00 time=04-04 00:00
  [41] PEAK   price=17250.00 time=04-18 00:00
  [42] TROUGH price=15080.00 time=05-30 00:00
  [43] PEAK   price=16660.00 time=06-12 15:00
  [44] TROUGH price=14840.00 time=07-10 15:00
  [45] PEAK   price=17765.00 time=08-07 15:00
  [46] TROUGH price=16580.00 time=08-14 15:00
  [47] PEAK   price=17490.00 time=08-21 15:00
  [48] TROUGH price=16400.00 time=09-04 15:00
```

**失败详情:**
```
  ❌ 最新(11950.00) < C(11585.00) = False
```
---

### NI — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 132350.00 |
| B 价 | 155360.00 |
| C 价 | 140500.00 |
| 最新价 | 134540.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 25 | C 索引 | 31 |

**极值点序列** (swing: 60, merged: 20):
```
  [ 0] TROUGH price=92640.00 time=04-15 00:00
  [ 1] PEAK   price=115300.00 time=05-07 00:00
  [ 2] TROUGH price=96250.00 time=05-29 00:00
  [ 3] PEAK   price=102200.00 time=06-11 00:00
  [ 4] TROUGH price=75230.00 time=07-09 00:00
  [ 5] PEAK   price=87950.00 time=07-21 00:00
  [ 6] TROUGH price=79800.00 time=08-04 00:00
  [ 7] PEAK   price=84300.00 time=08-11 00:00
  [ 8] TROUGH price=74100.00 time=08-25 00:00
  [ 9] PEAK   price=80220.00 time=09-11 00:00
  [10] TROUGH price=75500.00 time=09-29 00:00
  [11] PEAK   price=81000.00 time=10-12 00:00
  [12] TROUGH price=63310.00 time=11-24 00:00
  [13] PEAK   price=72780.00 time=11-26 00:00
  [14] TROUGH price=66810.00 time=12-11 00:00
  [15] PEAK   price=71710.00 time=12-22 00:00
  [16] TROUGH price=67900.00 time=12-29 00:00
  [17] PEAK   price=70960.00 time=12-31 00:00
  [18] TROUGH price=65820.00 time=01-12 00:00
  [19] PEAK   price=70930.00 time=01-25 00:00
```

**失败详情:**
```
  ❌ 最新(134540.00) > C(140500.00) = False
```
---

### NI — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 131840.00 |
| B 价 | 155360.00 |
| C 价 | 140500.00 |
| 最新价 | 135100.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 59 | C 索引 | 61 |

**极值点序列** (swing: 80, merged: 72):
```
  [ 0] TROUGH price=92640.00 time=04-14 05:45
  [ 1] PEAK   price=115300.00 time=05-05 05:45
  [ 2] TROUGH price=96250.00 time=05-26 05:45
  [ 3] PEAK   price=102200.00 time=06-09 05:45
  [ 4] TROUGH price=75230.00 time=07-07 05:45
  [ 5] PEAK   price=87950.00 time=07-21 05:45
  [ 6] TROUGH price=79800.00 time=08-04 05:45
  [ 7] PEAK   price=84300.00 time=08-11 05:45
  [ 8] TROUGH price=74100.00 time=08-25 05:45
  [ 9] PEAK   price=80220.00 time=09-08 05:45
  [10] TROUGH price=75500.00 time=09-29 05:45
  [11] PEAK   price=81000.00 time=10-08 05:45
  [12] TROUGH price=63310.00 time=11-24 05:45
  [13] PEAK   price=71710.00 time=12-22 05:45
  [14] TROUGH price=65820.00 time=01-12 05:45
  [15] PEAK   price=70930.00 time=01-19 05:45
  [16] TROUGH price=64280.00 time=02-15 05:45
  [17] PEAK   price=75840.00 time=03-08 05:45
  [18] TROUGH price=65530.00 time=04-05 05:45
  [19] PEAK   price=76390.00 time=05-03 05:45
  [20] TROUGH price=66350.00 time=05-24 05:45
  [21] PEAK   price=85700.00 time=08-02 05:45
  [22] TROUGH price=77550.00 time=08-23 05:45
  [23] PEAK   price=81550.00 time=09-06 05:45
  [24] TROUGH price=77960.00 time=09-13 05:45
  [25] PEAK   price=83610.00 time=09-27 05:45
  [26] TROUGH price=79080.00 time=10-18 05:45
  [27] PEAK   price=99800.00 time=11-08 05:45
  [28] TROUGH price=83450.00 time=01-03 05:45
  [29] PEAK   price=88360.00 time=01-10 05:45
  [30] TROUGH price=81210.00 time=01-24 05:45
  [31] PEAK   price=92550.00 time=02-21 05:45
  [32] TROUGH price=79560.00 time=03-21 05:45
  [33] PEAK   price=86980.00 time=04-05 05:45
  [34] TROUGH price=74710.00 time=05-16 05:45
  [35] PEAK   price=78580.00 time=05-23 05:45
  [36] TROUGH price=71520.00 time=06-13 05:45
  [37] PEAK   price=77670.00 time=06-27 05:45
  [38] TROUGH price=73010.00 time=07-11 05:45
  [39] PEAK   price=97720.00 time=08-29 05:45
  [40] TROUGH price=82500.00 time=09-26 05:45
  [41] PEAK   price=97750.00 time=10-17 05:45
  [42] TROUGH price=91760.00 time=10-24 05:45
  [43] PEAK   price=103420.00 time=10-31 05:45
  [44] TROUGH price=86890.00 time=12-05 05:45
  [45] PEAK   price=102380.00 time=01-09 05:45
  [46] TROUGH price=95700.00 time=01-16 05:45
  [47] PEAK   price=107050.00 time=01-23 05:45
  [48] TROUGH price=97770.00 time=02-06 05:45
  [49] PEAK   price=106590.00 time=02-27 05:45
  [50] TROUGH price=95470.00 time=03-27 00:00
  [51] PEAK   price=109790.00 time=04-17 05:45
  [52] TROUGH price=102000.00 time=04-24 05:45
  [53] PEAK   price=120000.00 time=05-29 00:00
  [54] TROUGH price=107790.00 time=07-17 00:00
  [55] PEAK   price=115150.00 time=08-07 00:00
  [56] TROUGH price=99920.00 time=09-11 00:00
  [57] PEAK   price=106600.00 time=09-25 05:45
  [58] TROUGH price=102450.00 time=10-08 05:45
  [59] PEAK   price=107120.00 time=10-09 00:00 ← A
  [60] TROUGH price=87660.00 time=11-20 05:45
  [61] PEAK   price=93920.00 time=11-27 05:45 ← C
  [62] TROUGH price=88110.00 time=12-10 15:00
  [63] PEAK   price=91390.00 time=12-17 15:00
  [64] TROUGH price=86080.00 time=01-02 00:00
  [65] PEAK   price=106780.00 time=03-04 15:00
  [66] TROUGH price=99100.00 time=03-25 15:00
  [67] PEAK   price=104240.00 time=04-01 15:00
  [68] TROUGH price=97100.00 time=04-23 05:45
  [69] PEAK   price=100120.00 time=04-30 05:45
  [70] TROUGH price=94670.00 time=05-06 15:00
  [71] PEAK   price=102830.00 time=05-20 15:00
```

**失败详情:**
```
  ❌ 最新(135100.00) > C(140500.00) = False
```
---

### NR — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 12800.00 |
| B 价 | 14155.00 |
| C 价 | 13540.00 |
| 最新价 | 13470.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 25 | C 索引 | 29 |

**极值点序列** (swing: 60, merged: 30):
```
  [ 0] TROUGH price= 9700.00 time=08-26 00:00
  [ 1] PEAK   price=10475.00 time=09-04 00:00
  [ 2] TROUGH price= 9600.00 time=10-08 00:00
  [ 3] PEAK   price=11640.00 time=11-25 00:00
  [ 4] TROUGH price=10580.00 time=12-26 00:00
  [ 5] PEAK   price=11210.00 time=01-14 00:00
  [ 6] TROUGH price= 8300.00 time=02-04 00:00
  [ 7] PEAK   price= 9920.00 time=02-21 00:00
  [ 8] TROUGH price= 7345.00 time=04-01 00:00
  [ 9] PEAK   price= 8455.00 time=04-20 00:00
  [10] TROUGH price= 7790.00 time=04-22 00:00
  [11] PEAK   price= 8650.00 time=05-11 00:00
  [12] TROUGH price= 8190.00 time=05-14 00:00
  [13] PEAK   price= 9155.00 time=06-08 00:00
  [14] TROUGH price= 8625.00 time=06-15 00:00
  [15] PEAK   price= 8950.00 time=06-22 00:00
  [16] TROUGH price= 8445.00 time=06-29 00:00
  [17] PEAK   price= 9075.00 time=07-07 00:00
  [18] TROUGH price= 8490.00 time=07-24 00:00
  [19] PEAK   price= 9755.00 time=08-10 00:00
  [20] TROUGH price= 9240.00 time=08-24 00:00
  [21] PEAK   price=10005.00 time=09-02 00:00
  [22] TROUGH price= 9080.00 time=09-22 00:00
  [23] PEAK   price=12275.00 time=10-28 00:00
  [24] TROUGH price=10055.00 time=11-09 00:00
  [25] PEAK   price=10850.00 time=11-13 00:00 ← A
  [26] TROUGH price=10275.00 time=11-18 00:00
  [27] PEAK   price=11480.00 time=12-02 00:00
  [28] TROUGH price=10215.00 time=12-11 00:00
  [29] PEAK   price=11070.00 time=12-21 00:00 ← C
```

**失败详情:**
```
  ❌ 最新(13470.00) > C(13540.00) = False
```
---

### P — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 9208.00 |
| B 价 | 9570.00 |
| C 价 | 9332.00 |
| 最新价 | 9316.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 57 | C 索引 | 67 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] PEAK   price= 8970.00 time=11-13 05:45
  [ 1] TROUGH price= 8360.00 time=11-20 05:45
  [ 2] PEAK   price=10296.00 time=01-15 05:45
  [ 3] TROUGH price= 9138.00 time=01-22 05:45
  [ 4] PEAK   price=12992.00 time=03-04 05:45
  [ 5] TROUGH price= 9402.00 time=04-01 05:45
  [ 6] PEAK   price=11054.00 time=04-15 05:45
  [ 7] TROUGH price=10018.00 time=04-29 05:45
  [ 8] PEAK   price=11254.00 time=06-10 05:45
  [ 9] TROUGH price=10322.00 time=06-24 05:45
  [10] PEAK   price= 8150.00 time=08-19 05:45
  [11] TROUGH price= 4152.00 time=11-18 05:45
  [12] PEAK   price= 5716.00 time=01-06 05:45
  [13] TROUGH price= 4938.00 time=02-03 05:45
  [14] PEAK   price= 5586.00 time=02-10 05:45
  [15] TROUGH price= 5972.00 time=04-28 05:45
  [16] PEAK   price= 7086.00 time=05-12 05:45
  [17] TROUGH price= 5488.00 time=07-07 05:45
  [18] PEAK   price= 6766.00 time=08-11 05:45
  [19] TROUGH price= 5634.00 time=09-22 05:45
  [20] PEAK   price= 6282.00 time=10-20 05:45
  [21] TROUGH price= 5950.00 time=10-27 05:45
  [22] PEAK   price= 7466.00 time=01-05 05:45
  [23] TROUGH price= 6534.00 time=02-02 05:45
  [24] PEAK   price= 7104.00 time=03-09 05:45
  [25] TROUGH price= 6782.00 time=03-30 05:45
  [26] PEAK   price= 7078.00 time=04-27 05:45
  [27] TROUGH price= 6320.00 time=06-08 05:45
  [28] PEAK   price= 6540.00 time=06-22 05:45
  [29] TROUGH price= 6152.00 time=07-06 05:45
  [30] PEAK   price= 7378.00 time=08-10 05:45
  [31] TROUGH price= 6942.00 time=08-17 05:45
  [32] PEAK   price= 7970.00 time=09-21 05:45
  [33] TROUGH price= 7480.00 time=10-07 05:45
  [34] PEAK   price= 9772.00 time=11-09 05:45
  [35] TROUGH price= 8352.00 time=11-16 05:45
  [36] PEAK   price=10160.00 time=01-18 05:45
  [37] TROUGH price= 9306.00 time=01-25 05:45
  [38] PEAK   price=10296.00 time=02-09 05:45
  [39] TROUGH price= 8784.00 time=03-15 05:45
  [40] PEAK   price= 9560.00 time=04-06 05:45
  [41] TROUGH price= 8822.00 time=05-03 05:45
  [42] PEAK   price= 9476.00 time=05-31 05:45
  [43] TROUGH price= 8710.00 time=06-28 05:45
  [44] PEAK   price= 9298.00 time=08-02 05:45
  [45] TROUGH price= 8464.00 time=08-09 05:45
  [46] PEAK   price= 9120.00 time=08-30 05:45
  [47] TROUGH price= 7636.00 time=10-18 05:45
  [48] PEAK   price= 8180.00 time=10-25 05:45
  [49] TROUGH price= 7830.00 time=11-08 05:45
  [50] PEAK   price= 8354.00 time=11-15 05:45
  [51] TROUGH price= 7704.00 time=11-22 05:45
  [52] PEAK   price= 8030.00 time=12-06 05:45
  [53] TROUGH price= 7690.00 time=12-13 05:45
  [54] PEAK   price= 8220.00 time=01-10 05:45
  [55] TROUGH price= 8252.00 time=03-06 05:45
  [56] PEAK   price= 9034.00 time=04-10 05:45
  [57] TROUGH price= 7586.00 time=05-29 05:45 ← A
  [58] PEAK   price= 8344.00 time=07-03 05:45
  [59] TROUGH price= 7588.00 time=08-14 05:45
  [60] PEAK   price= 8352.00 time=09-04 05:45
  [61] TROUGH price= 6754.00 time=10-09 05:45
  [62] PEAK   price= 7350.00 time=10-23 05:45
  [63] TROUGH price= 6482.00 time=11-06 05:45
  [64] PEAK   price= 6900.00 time=12-04 05:45
  [65] TROUGH price= 6664.00 time=12-11 05:45
  [66] PEAK   price= 7044.00 time=12-25 05:45
  [67] TROUGH price= 6634.00 time=01-08 05:45 ← C
  [68] PEAK   price= 7252.00 time=01-29 05:45
  [69] TROUGH price= 6102.00 time=03-26 05:45
  [70] PEAK   price= 6410.00 time=04-09 05:45
  [71] TROUGH price= 5826.00 time=05-02 05:45
  [72] PEAK   price= 6382.00 time=06-04 05:45
  [73] TROUGH price= 5790.00 time=06-25 05:45
  [74] PEAK   price= 5982.00 time=07-09 05:45
  [75] TROUGH price= 5306.00 time=07-30 05:45
  [76] PEAK   price= 5862.00 time=08-27 05:45
  [77] TROUGH price= 5310.00 time=09-17 05:45
  [78] PEAK   price= 6374.00 time=10-29 05:45
  [79] TROUGH price= 6142.00 time=11-12 05:45
```

**失败详情:**
```
  ❌ 最新(9316.00) > C(9332.00) = False
```
---

### PB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 16195.00 |
| B 价 | 17005.00 |
| C 价 | 16400.00 |
| 最新价 | 16130.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 57 | C 索引 | 59 |

**极值点序列** (swing: 80, merged: 79):
```
  [ 0] TROUGH price=16190.00 time=05-03 05:45
  [ 1] PEAK   price=17370.00 time=05-24 05:45
  [ 2] TROUGH price=16455.00 time=06-14 05:45
  [ 3] PEAK   price=17855.00 time=07-26 05:45
  [ 4] TROUGH price=15200.00 time=08-09 05:45
  [ 5] PEAK   price=16995.00 time=08-30 05:45
  [ 6] TROUGH price=13590.00 time=09-27 05:45
  [ 7] PEAK   price=15725.00 time=10-25 05:45
  [ 8] TROUGH price=14605.00 time=11-08 05:45
  [ 9] PEAK   price=16185.00 time=11-29 05:45
  [10] TROUGH price=14810.00 time=12-13 05:45
  [11] PEAK   price=16440.00 time=01-30 05:45
  [12] TROUGH price=15530.00 time=02-14 05:45
  [13] PEAK   price=16385.00 time=02-28 05:45
  [14] TROUGH price=15350.00 time=04-05 05:45
  [15] PEAK   price=15950.00 time=05-02 05:45
  [16] TROUGH price=14885.00 time=05-29 05:45
  [17] PEAK   price=15935.00 time=06-12 05:45
  [18] TROUGH price=14310.00 time=06-26 05:45
  [19] PEAK   price=15130.00 time=07-24 05:45
  [20] TROUGH price=14490.00 time=08-14 05:45
  [21] PEAK   price=16700.00 time=09-11 05:45
  [22] TROUGH price=15105.00 time=10-30 05:45
  [23] PEAK   price=15580.00 time=11-06 05:45
  [24] TROUGH price=15035.00 time=01-15 05:45
  [25] PEAK   price=15625.00 time=01-29 05:45
  [26] TROUGH price=13425.00 time=04-16 05:45
  [27] PEAK   price=13925.00 time=05-07 05:45
  [28] TROUGH price=13405.00 time=05-14 05:45
  [29] PEAK   price=14125.00 time=06-04 05:45
  [30] TROUGH price=13800.00 time=06-13 05:45
  [31] PEAK   price=14375.00 time=06-18 05:45
  [32] TROUGH price=13820.00 time=06-25 05:45
  [33] PEAK   price=14280.00 time=07-02 05:45
  [34] TROUGH price=13450.00 time=07-23 05:45
  [35] PEAK   price=14960.00 time=08-13 05:45
  [36] TROUGH price=13805.00 time=09-10 05:45
  [37] PEAK   price=14550.00 time=10-22 05:45
  [38] TROUGH price=13840.00 time=12-03 05:45
  [39] PEAK   price=14575.00 time=12-17 05:45
  [40] TROUGH price=13925.00 time=01-07 05:45
  [41] PEAK   price=14340.00 time=01-21 05:45
  [42] TROUGH price=13495.00 time=03-11 05:45
  [43] PEAK   price=13860.00 time=03-25 05:45
  [44] TROUGH price=13615.00 time=04-01 05:45
  [45] PEAK   price=14420.00 time=04-22 05:45
  [46] TROUGH price=13915.00 time=05-27 05:45
  [47] PEAK   price=14480.00 time=06-03 05:45
  [48] TROUGH price=13660.00 time=06-17 05:45
  [49] PEAK   price=14275.00 time=06-24 05:45
  [50] TROUGH price=13860.00 time=07-01 05:45
  [51] PEAK   price=15510.00 time=07-29 05:45
  [52] TROUGH price=13620.00 time=09-16 05:45
  [53] PEAK   price=13980.00 time=10-08 05:45
  [54] TROUGH price=13340.00 time=10-14 05:45
  [55] PEAK   price=13885.00 time=12-02 05:45
  [56] TROUGH price=11770.00 time=01-13 05:45
  [57] PEAK   price=12695.00 time=01-20 05:45 ← A
  [58] TROUGH price=12225.00 time=02-10 05:45
  [59] PEAK   price=12625.00 time=02-17 05:45 ← C
  [60] TROUGH price=12090.00 time=02-26 05:45
  [61] PEAK   price=12370.00 time=03-10 05:45
  [62] TROUGH price=11995.00 time=03-17 05:45
  [63] PEAK   price=14025.00 time=05-05 05:45
  [64] TROUGH price=13095.00 time=05-19 05:45
  [65] PEAK   price=13295.00 time=06-09 05:45
  [66] TROUGH price=12650.00 time=06-16 05:45
  [67] PEAK   price=13290.00 time=06-23 05:45
  [68] TROUGH price=12270.00 time=07-07 05:45
  [69] PEAK   price=13290.00 time=07-14 05:45
  [70] TROUGH price=12535.00 time=07-21 05:45
  [71] PEAK   price=13860.00 time=08-18 05:45
  [72] TROUGH price=12725.00 time=08-25 05:45
  [73] PEAK   price=13775.00 time=09-01 05:45
  [74] TROUGH price=12995.00 time=09-15 05:45
  [75] PEAK   price=13880.00 time=10-20 05:45
  [76] TROUGH price=11800.00 time=11-17 05:45
  [77] PEAK   price=13175.00 time=12-08 05:45
  [78] TROUGH price=12640.00 time=12-15 05:45
```

**失败详情:**
```
  ❌ 最新(16130.00) > C(16400.00) = False
```
---

### PG — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 4203.00 |
| B 价 | 7407.00 |
| C 价 | 5185.00 |
| 最新价 | 4510.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 34 | C 索引 | 42 |

**极值点序列** (swing: 60, merged: 38):
```
  [ 0] PEAK   price= 3336.00 time=04-15 00:00
  [ 1] TROUGH price= 3065.00 time=04-22 00:00
  [ 2] PEAK   price= 3659.00 time=04-28 00:00
  [ 3] TROUGH price= 3168.00 time=05-18 00:00
  [ 4] PEAK   price= 3677.00 time=06-08 00:00
  [ 5] TROUGH price= 3268.00 time=06-12 00:00
  [ 6] PEAK   price= 3588.00 time=06-22 00:00
  [ 7] TROUGH price= 3437.00 time=06-29 00:00
  [ 8] PEAK   price= 4059.00 time=07-22 00:00
  [ 9] TROUGH price= 3760.00 time=08-03 00:00
  [10] PEAK   price= 4038.00 time=08-10 00:00
  [11] TROUGH price= 3476.00 time=08-20 00:00
  [12] PEAK   price= 3764.00 time=08-31 00:00
  [13] TROUGH price= 3359.00 time=09-11 00:00
  [14] PEAK   price= 3596.00 time=09-21 00:00
  [15] TROUGH price= 3333.00 time=09-22 00:00
  [16] PEAK   price= 3853.00 time=10-15 00:00
  [17] TROUGH price= 3655.00 time=10-30 00:00
  [18] PEAK   price= 3956.00 time=11-02 00:00
  [19] TROUGH price= 3444.00 time=11-20 00:00
  [20] PEAK   price= 4150.00 time=12-21 00:00
  [21] TROUGH price= 3696.00 time=12-30 00:00
  [22] PEAK   price= 4069.00 time=01-14 00:00
  [23] TROUGH price= 3253.00 time=01-29 00:00
  [24] PEAK   price= 3547.00 time=02-08 00:00
  [25] TROUGH price= 3259.00 time=02-10 00:00
  [26] PEAK   price= 4150.00 time=02-25 00:00
  [27] TROUGH price= 3804.00 time=03-09 00:00
  [28] PEAK   price= 4185.00 time=03-15 00:00
  [29] TROUGH price= 3684.00 time=04-06 00:00
  [30] PEAK   price= 3955.00 time=04-14 00:00
  [31] TROUGH price= 3633.00 time=04-27 00:00
  [32] PEAK   price= 4328.00 time=05-17 00:00
  [33] TROUGH price= 4001.00 time=05-20 00:00
  [34] PEAK   price= 4498.00 time=06-02 00:00 ← A
  [35] TROUGH price= 4245.00 time=06-08 00:00
  [36] PEAK   price= 5093.00 time=07-06 00:00
  [37] TROUGH price= 4741.00 time=07-09 00:00
```

**失败详情:**
```
  ❌ 最新(4510.00) > C(5185.00) = False
```
---

### PX — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 10600.00 |
| B 价 | 8766.00 |
| C 价 | 9742.00 |
| 最新价 | 10018.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 27 | C 索引 | 29 |

**极值点序列** (swing: 60, merged: 30):
```
  [ 0] TROUGH price= 8234.00 time=10-23 00:00
  [ 1] PEAK   price= 8700.00 time=11-06 00:00
  [ 2] TROUGH price= 8352.00 time=11-08 00:00
  [ 3] PEAK   price= 8840.00 time=11-17 00:00
  [ 4] TROUGH price= 8110.00 time=12-06 00:00
  [ 5] PEAK   price= 8426.00 time=12-12 00:00
  [ 6] TROUGH price= 8092.00 time=12-14 00:00
  [ 7] PEAK   price= 8742.00 time=01-02 00:00
  [ 8] TROUGH price= 8250.00 time=01-11 00:00
  [ 9] PEAK   price= 8754.00 time=01-24 00:00
  [10] TROUGH price= 8360.00 time=02-05 00:00
  [11] PEAK   price= 8660.00 time=02-28 00:00
  [12] TROUGH price= 8266.00 time=03-11 00:00
  [13] PEAK   price= 8582.00 time=03-20 00:00
  [14] TROUGH price= 8302.00 time=03-21 00:00
  [15] PEAK   price= 8896.00 time=04-03 00:00
  [16] TROUGH price= 8234.00 time=05-10 00:00
  [17] PEAK   price= 8746.00 time=05-30 00:00
  [18] TROUGH price= 8394.00 time=06-04 00:00
  [19] PEAK   price= 8774.00 time=07-04 00:00
  [20] TROUGH price= 7610.00 time=08-23 00:00
  [21] PEAK   price= 7910.00 time=08-27 00:00
  [22] TROUGH price= 6572.00 time=09-11 00:00
  [23] PEAK   price= 7812.00 time=10-08 00:00
  [24] TROUGH price= 6588.00 time=11-18 00:00
  [25] PEAK   price= 6952.00 time=11-21 00:00
  [26] TROUGH price= 6480.00 time=12-06 00:00
  [27] PEAK   price= 7656.00 time=01-16 00:00 ← A
  [28] TROUGH price= 7074.00 time=02-05 00:00
  [29] PEAK   price= 7460.00 time=02-12 00:00 ← C
```

**失败详情:**
```
  ❌ 最新(10018.00) < C(9742.00) = False
```
---

### RB — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 3005.00 |
| B 价 | 3167.00 |
| C 价 | 3083.00 |
| 最新价 | 3075.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 38 | C 索引 | 40 |

**极值点序列** (swing: 60, merged: 20):
```
  [ 0] TROUGH price= 3410.00 time=04-07 00:00
  [ 1] PEAK   price= 3678.00 time=05-11 00:00
  [ 2] TROUGH price= 3581.00 time=05-18 00:00
  [ 3] PEAK   price= 3940.00 time=06-11 00:00
  [ 4] TROUGH price= 3817.00 time=06-30 00:00
  [ 5] PEAK   price= 4968.00 time=08-04 00:00
  [ 6] TROUGH price= 3880.00 time=09-08 00:00
  [ 7] PEAK   price= 4078.00 time=09-10 00:00
  [ 8] TROUGH price= 3610.00 time=10-12 00:00
  [ 9] PEAK   price= 4014.00 time=10-27 00:00
  [10] TROUGH price= 3787.00 time=10-29 00:00
  [11] PEAK   price= 4144.00 time=11-10 00:00
  [12] TROUGH price= 4007.00 time=11-13 00:00
  [13] PEAK   price= 4572.00 time=11-26 00:00
  [14] TROUGH price= 4246.00 time=12-09 00:00
  [15] PEAK   price= 4650.00 time=01-07 00:00
  [16] TROUGH price= 4066.00 time=02-05 00:00
  [17] PEAK   price= 4848.00 time=03-26 00:00
  [18] TROUGH price= 4725.00 time=04-01 00:00
  [19] PEAK   price= 4898.00 time=04-13 00:00
```

**失败详情:**
```
  ❌ 最新(3075.00) > C(3083.00) = False
```
---

### RM — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2266.00 |
| B 价 | 2634.00 |
| C 价 | 2309.00 |
| 最新价 | 2239.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 49 | C 索引 | 53 |

**极值点序列** (swing: 80, merged: 79):
```
  [ 0] PEAK   price= 2618.00 time=01-15 05:45
  [ 1] TROUGH price= 2428.00 time=02-18 05:45
  [ 2] PEAK   price= 2639.00 time=02-19 05:45
  [ 3] TROUGH price= 2304.00 time=04-02 05:45
  [ 4] PEAK   price= 2443.00 time=04-16 05:45
  [ 5] TROUGH price= 2310.00 time=05-02 05:45
  [ 6] PEAK   price= 2412.00 time=05-21 05:45
  [ 7] TROUGH price= 2176.00 time=06-18 05:45
  [ 8] PEAK   price= 2326.00 time=07-16 05:45
  [ 9] TROUGH price= 2190.00 time=07-30 05:45
  [10] PEAK   price= 2550.00 time=08-27 05:45
  [11] TROUGH price= 2346.00 time=09-17 05:45
  [12] PEAK   price= 2556.00 time=10-08 05:45
  [13] TROUGH price= 2343.00 time=10-29 05:45
  [14] PEAK   price= 2711.00 time=01-14 05:45
  [15] TROUGH price= 2445.00 time=01-21 05:45
  [16] PEAK   price= 2610.00 time=03-04 05:45
  [17] TROUGH price= 2466.00 time=03-11 05:45
  [18] PEAK   price= 3118.00 time=05-27 05:45
  [19] TROUGH price= 2937.00 time=06-03 05:45
  [20] PEAK   price= 3116.00 time=06-17 05:45
  [21] TROUGH price= 2067.00 time=10-08 05:45
  [22] PEAK   price= 2372.00 time=10-28 05:45
  [23] TROUGH price= 2213.00 time=11-04 05:45
  [24] PEAK   price= 2358.00 time=11-11 05:45
  [25] TROUGH price= 2179.00 time=11-18 05:45
  [26] PEAK   price= 2302.00 time=11-25 05:45
  [27] TROUGH price= 2184.00 time=12-02 05:45
  [28] PEAK   price= 2377.00 time=12-09 05:45
  [29] TROUGH price= 2062.00 time=01-13 05:45
  [30] PEAK   price= 2418.00 time=02-24 05:45
  [31] TROUGH price= 2181.00 time=03-03 05:45
  [32] PEAK   price= 2334.00 time=03-10 05:45
  [33] TROUGH price= 2201.00 time=03-17 05:45
  [34] PEAK   price= 2301.00 time=03-31 05:45
  [35] TROUGH price= 2117.00 time=04-07 05:45
  [36] PEAK   price= 2284.00 time=05-05 05:45
  [37] TROUGH price= 2031.00 time=05-26 05:45
  [38] PEAK   price= 2125.00 time=06-02 05:45
  [39] TROUGH price= 1944.00 time=06-23 05:45
  [40] PEAK   price= 2401.00 time=07-14 05:45
  [41] TROUGH price= 2046.00 time=08-04 05:45
  [42] PEAK   price= 2224.00 time=08-11 05:45
  [43] TROUGH price= 1855.00 time=09-01 05:45
  [44] PEAK   price= 2067.00 time=09-15 05:45
  [45] TROUGH price= 1957.00 time=10-08 05:45
  [46] PEAK   price= 2028.00 time=10-13 05:45
  [47] TROUGH price= 1927.00 time=10-20 05:45
  [48] PEAK   price= 1997.00 time=11-03 05:45
  [49] TROUGH price= 1699.00 time=11-24 05:45 ← A
  [50] PEAK   price= 1927.00 time=12-01 05:45
  [51] TROUGH price= 1817.00 time=12-08 05:45
  [52] PEAK   price= 1947.00 time=12-22 05:45
  [53] TROUGH price= 1854.00 time=01-05 05:45 ← C
  [54] PEAK   price= 1985.00 time=01-26 05:45
  [55] TROUGH price= 1824.00 time=02-23 05:45
  [56] PEAK   price= 1998.00 time=03-08 05:45
  [57] TROUGH price= 1875.00 time=03-15 05:45
  [58] PEAK   price= 2035.00 time=03-22 05:45
  [59] TROUGH price= 1842.00 time=04-05 05:45
  [60] PEAK   price= 2296.00 time=04-19 05:45
  [61] TROUGH price= 2025.00 time=05-03 05:45
  [62] PEAK   price= 2443.00 time=05-17 05:45
  [63] TROUGH price= 2203.00 time=05-24 05:45
  [64] PEAK   price= 3003.00 time=06-28 05:45
  [65] TROUGH price= 2307.00 time=08-02 05:45
  [66] PEAK   price= 2463.00 time=08-16 05:45
  [67] TROUGH price= 2175.00 time=08-30 05:45
  [68] PEAK   price= 2335.00 time=09-20 05:45
  [69] TROUGH price= 2121.00 time=10-10 05:45
  [70] PEAK   price= 2361.00 time=10-25 05:45
  [71] TROUGH price= 2153.00 time=11-01 05:45
  [72] PEAK   price= 2553.00 time=11-29 05:45
  [73] TROUGH price= 2265.00 time=12-20 05:45
  [74] PEAK   price= 2496.00 time=01-03 05:45
  [75] TROUGH price= 2364.00 time=02-03 05:45
  [76] PEAK   price= 2538.00 time=02-07 05:45
  [77] TROUGH price= 2360.00 time=02-21 05:45
  [78] PEAK   price= 2493.00 time=03-07 05:45
```

**失败详情:**
```
  ❌ 最新(2239.00) > C(2309.00) = False
```
---

### RR — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 3610.00 |
| B 价 | 3541.00 |
| C 价 | 3591.00 |
| 最新价 | 3631.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 15 | C 索引 | 27 |

**极值点序列** (swing: 60, merged: 30):
```
  [ 0] TROUGH price= 3600.00 time=08-29 00:00
  [ 1] PEAK   price= 3709.00 time=09-06 00:00
  [ 2] TROUGH price= 3609.00 time=10-22 00:00
  [ 3] PEAK   price= 3649.00 time=10-31 00:00
  [ 4] TROUGH price= 3596.00 time=11-05 00:00
  [ 5] PEAK   price= 3756.00 time=11-19 00:00
  [ 6] TROUGH price= 3310.00 time=12-10 00:00
  [ 7] PEAK   price= 3475.00 time=12-17 00:00
  [ 8] TROUGH price= 3211.00 time=12-20 00:00
  [ 9] PEAK   price= 3373.00 time=01-14 00:00
  [10] TROUGH price= 3280.00 time=02-03 00:00
  [11] PEAK   price= 3552.00 time=02-24 00:00
  [12] TROUGH price= 3301.00 time=03-17 00:00
  [13] PEAK   price= 3700.00 time=03-30 00:00
  [14] TROUGH price= 3423.00 time=04-21 00:00
  [15] PEAK   price= 3524.00 time=04-24 00:00 ← A
  [16] TROUGH price= 3355.00 time=05-08 00:00
  [17] PEAK   price= 3483.00 time=05-28 00:00
  [18] TROUGH price= 3431.00 time=06-05 00:00
  [19] PEAK   price= 3470.00 time=06-09 00:00
  [20] TROUGH price= 3392.00 time=06-24 00:00
  [21] PEAK   price= 3500.00 time=07-14 00:00
  [22] TROUGH price= 3425.00 time=07-22 00:00
  [23] PEAK   price= 3613.00 time=07-28 00:00
  [24] TROUGH price= 3441.00 time=08-12 00:00
  [25] PEAK   price= 3529.00 time=09-02 00:00
  [26] TROUGH price= 3441.00 time=09-22 00:00
  [27] PEAK   price= 3480.00 time=10-09 00:00 ← C
  [28] TROUGH price= 3401.00 time=10-12 00:00
  [29] PEAK   price= 3567.00 time=10-27 00:00
```

**失败详情:**
```
  ❌ 最新(3631.00) < C(3591.00) = False
```
---

### RU — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 16480.00 |
| B 价 | 18395.00 |
| C 价 | 17220.00 |
| 最新价 | 16800.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 30 | C 索引 | 32 |

**极值点序列** (swing: 60, merged: 24):
```
  [ 0] PEAK   price=17260.00 time=09-08 15:00
  [ 1] TROUGH price=16390.00 time=09-13 15:00
  [ 2] PEAK   price=18735.00 time=10-18 15:00
  [ 3] TROUGH price=17390.00 time=10-27 15:00
  [ 4] PEAK   price=17840.00 time=11-04 15:00
  [ 5] TROUGH price=16680.00 time=11-18 15:00
  [ 6] PEAK   price=17520.00 time=11-28 00:00
  [ 7] TROUGH price=16710.00 time=11-30 00:00
  [ 8] PEAK   price=18210.00 time=12-12 00:00
  [ 9] TROUGH price=17400.00 time=12-15 00:00
  [10] PEAK   price=24480.00 time=02-10 00:00
  [11] TROUGH price=20550.00 time=02-24 00:00
  [12] PEAK   price=22170.00 time=03-03 00:00
  [13] TROUGH price=19850.00 time=03-20 00:00
  [14] PEAK   price=22320.00 time=04-20 00:00
  [15] TROUGH price=21350.00 time=04-27 00:00
  [16] PEAK   price=26375.00 time=05-15 00:00
  [17] TROUGH price=24600.00 time=05-22 00:00
  [18] PEAK   price=29980.00 time=05-30 00:00
  [19] TROUGH price=23400.00 time=06-20 00:00
  [20] PEAK   price=26300.00 time=07-07 00:00
  [21] TROUGH price=17860.00 time=09-11 00:00
  [22] PEAK   price=20090.00 time=09-19 00:00
  [23] TROUGH price=17920.00 time=09-25 00:00
```

**失败详情:**
```
  ❌ 最新(16800.00) > C(17220.00) = False
```
---

### SA — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 1274.00 |
| B 价 | 1175.00 |
| C 价 | 1234.00 |
| 最新价 | 1243.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 30 | C 索引 | 32 |

**极值点序列** (swing: 60, merged: 30):
```
  [ 0] PEAK   price= 1691.00 time=01-15 00:00
  [ 1] TROUGH price= 1509.00 time=02-03 00:00
  [ 2] PEAK   price= 1637.00 time=02-25 00:00
  [ 3] TROUGH price= 1501.00 time=03-09 00:00
  [ 4] PEAK   price= 1600.00 time=03-11 00:00
  [ 5] TROUGH price= 1322.00 time=04-14 00:00
  [ 6] PEAK   price= 1518.00 time=04-20 00:00
  [ 7] TROUGH price= 1398.00 time=05-11 00:00
  [ 8] PEAK   price= 1490.00 time=06-04 00:00
  [ 9] TROUGH price= 1358.00 time=07-01 00:00
  [10] PEAK   price= 1416.00 time=07-13 00:00
  [11] TROUGH price= 1288.00 time=07-21 00:00
  [12] PEAK   price= 1504.00 time=08-10 00:00
  [13] TROUGH price= 1339.00 time=08-17 00:00
  [14] PEAK   price= 1822.00 time=09-03 00:00
  [15] TROUGH price= 1655.00 time=09-16 00:00
  [16] PEAK   price= 1762.00 time=09-24 00:00
  [17] TROUGH price= 1508.00 time=11-11 00:00
  [18] PEAK   price= 1561.00 time=11-16 00:00
  [19] TROUGH price= 1317.00 time=12-14 00:00
  [20] PEAK   price= 1682.00 time=12-28 00:00
  [21] TROUGH price= 1573.00 time=12-29 00:00
  [22] PEAK   price= 1682.00 time=01-07 00:00
  [23] TROUGH price= 1489.00 time=01-13 00:00
  [24] PEAK   price= 1986.00 time=03-03 00:00
  [25] TROUGH price= 1784.00 time=03-05 00:00
  [26] PEAK   price= 2010.00 time=03-18 00:00
  [27] TROUGH price= 1818.00 time=04-08 00:00
  [28] PEAK   price= 2329.00 time=05-13 00:00
  [29] TROUGH price= 2028.00 time=05-20 00:00
```

**失败详情:**
```
  ❌ 最新(1243.00) < C(1234.00) = False
```
---

### SC — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 502.30 |
| B 价 | 588.60 |
| C 价 | 575.30 |
| 最新价 | 416.30 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 0 | C 索引 | 34 |

**极值点序列** (swing: 60, merged: 29):
```
  [ 0] TROUGH price=  397.70 time=04-09 00:00 ← A
  [ 1] PEAK   price=  493.80 time=05-23 00:00
  [ 2] TROUGH price=  456.60 time=05-28 00:00
  [ 3] PEAK   price=  483.90 time=06-01 00:00
  [ 4] TROUGH price=  455.80 time=06-06 00:00
  [ 5] PEAK   price=  476.30 time=06-11 00:00
  [ 6] TROUGH price=  453.70 time=06-22 00:00
  [ 7] PEAK   price=  510.00 time=07-02 00:00
  [ 8] TROUGH price=  487.00 time=07-09 00:00
  [ 9] PEAK   price=  511.50 time=07-11 00:00
  [10] TROUGH price=  478.50 time=07-17 00:00
  [11] PEAK   price=  550.00 time=08-08 00:00
  [12] TROUGH price=  480.00 time=08-20 00:00
  [13] PEAK   price=  598.50 time=10-10 00:00
  [14] TROUGH price=  406.60 time=12-07 00:00
  [15] PEAK   price=  437.30 time=12-10 00:00
  [16] TROUGH price=  351.60 time=12-25 00:00
  [17] PEAK   price=  442.20 time=01-22 00:00
  [18] TROUGH price=  413.00 time=01-29 00:00
  [19] PEAK   price=  467.90 time=02-18 00:00
  [20] TROUGH price=  426.20 time=03-06 00:00
  [21] PEAK   price=  465.00 time=03-21 00:00
  [22] TROUGH price=  446.90 time=03-29 00:00
  [23] PEAK   price=  482.80 time=04-11 00:00
  [24] TROUGH price=  464.80 time=04-16 00:00
  [25] PEAK   price=  508.30 time=04-26 00:00
  [26] TROUGH price=  465.30 time=05-06 00:00
  [27] PEAK   price=  521.50 time=05-20 00:00
  [28] TROUGH price=  406.00 time=06-18 00:00
```

**失败详情:**
```
  ❌ 最新(416.30) > C(575.30) = False
```
---

### SC — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 540.30 |
| B 价 | 585.80 |
| C 价 | 575.30 |
| 最新价 | 572.20 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 6 | C 索引 | 50 |

**极值点序列** (swing: 80, merged: 64):
```
  [ 0] TROUGH price=  397.70 time=04-03 00:00
  [ 1] PEAK   price=  493.80 time=05-22 00:00
  [ 2] TROUGH price=  453.70 time=06-19 00:00
  [ 3] PEAK   price=  511.50 time=07-10 00:00
  [ 4] TROUGH price=  478.50 time=07-17 00:00
  [ 5] PEAK   price=  550.00 time=08-07 00:00
  [ 6] TROUGH price=  480.00 time=08-14 00:00 ← A
  [ 7] PEAK   price=  598.50 time=10-09 00:00
  [ 8] TROUGH price=  406.60 time=12-04 05:45
  [ 9] PEAK   price=  430.80 time=12-18 05:45
  [10] TROUGH price=  351.60 time=12-25 00:00
  [11] PEAK   price=  442.20 time=01-22 00:00
  [12] TROUGH price=  413.00 time=01-29 00:00
  [13] PEAK   price=  467.90 time=02-12 00:00
  [14] TROUGH price=  426.20 time=03-05 00:00
  [15] PEAK   price=  465.00 time=03-19 05:45
  [16] TROUGH price=  446.90 time=03-26 05:45
  [17] PEAK   price=  482.80 time=04-09 05:45
  [18] TROUGH price=  464.80 time=04-16 05:45
  [19] PEAK   price=  508.30 time=04-23 05:45
  [20] TROUGH price=  465.30 time=04-30 05:45
  [21] PEAK   price=  521.50 time=05-14 00:00
  [22] TROUGH price=  406.00 time=06-18 00:00
  [23] PEAK   price=  455.30 time=06-25 05:45
  [24] TROUGH price=  423.60 time=07-02 05:45
  [25] PEAK   price=  462.20 time=07-09 00:00
  [26] TROUGH price=  413.10 time=07-16 05:45
  [27] PEAK   price=  449.70 time=07-30 05:45
  [28] TROUGH price=  399.60 time=08-06 00:00
  [29] PEAK   price=  496.00 time=09-17 00:00
  [30] TROUGH price=  431.50 time=10-08 00:00
  [31] PEAK   price=  463.40 time=11-04 15:00
  [32] TROUGH price=  441.80 time=11-18 15:00
  [33] PEAK   price=  465.80 time=11-25 15:00
  [34] TROUGH price=  445.40 time=12-02 15:00
  [35] PEAK   price=  529.80 time=01-06 15:00
  [36] TROUGH price=  381.40 time=02-03 15:00
  [37] PEAK   price=  422.00 time=02-17 15:00
  [38] TROUGH price=  213.20 time=03-17 00:00
  [39] PEAK   price=  304.90 time=04-07 00:00
  [40] TROUGH price=  205.10 time=04-28 00:00
  [41] PEAK   price=  267.30 time=05-06 05:45
  [42] TROUGH price=  236.30 time=05-11 15:00
  [43] PEAK   price=  298.10 time=06-02 05:45
  [44] TROUGH price=  259.50 time=06-09 05:45
  [45] PEAK   price=  302.80 time=06-16 05:45
  [46] TROUGH price=  286.00 time=07-14 05:45
  [47] PEAK   price=  305.70 time=07-20 15:00
  [48] TROUGH price=  277.10 time=08-03 15:00
  [49] PEAK   price=  299.90 time=08-25 00:00
  [50] TROUGH price=  242.70 time=09-07 15:00 ← C
  [51] PEAK   price=  281.30 time=09-15 05:45
  [52] TROUGH price=  253.90 time=09-28 15:00
  [53] PEAK   price=  277.30 time=10-12 15:00
  [54] TROUGH price=  215.00 time=10-27 00:00
  [55] PEAK   price=  322.70 time=12-15 05:45
  [56] TROUGH price=  286.50 time=12-21 15:00
  [57] PEAK   price=  422.20 time=02-22 15:00
  [58] TROUGH price=  385.40 time=03-01 15:00
  [59] PEAK   price=  444.60 time=03-02 00:00
  [60] TROUGH price=  372.70 time=03-22 15:00
  [61] PEAK   price=  409.00 time=03-29 15:00
  [62] TROUGH price=  379.40 time=04-06 05:45
  [63] PEAK   price=  479.00 time=07-05 15:00
```

**失败详情:**
```
  ❌ 最新(572.20) > C(575.30) = False
```
---

### SH — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 2685.00 |
| B 价 | 2041.00 |
| C 价 | 2147.00 |
| 最新价 | 2523.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 27 | C 索引 | 29 |

**极值点序列** (swing: 60, merged: 30):
```
  [ 0] TROUGH price= 2504.00 time=10-20 00:00
  [ 1] PEAK   price= 2752.00 time=11-10 00:00
  [ 2] TROUGH price= 2547.00 time=11-22 00:00
  [ 3] PEAK   price= 2692.00 time=11-30 00:00
  [ 4] TROUGH price= 2523.00 time=12-07 00:00
  [ 5] PEAK   price= 2972.00 time=12-22 00:00
  [ 6] TROUGH price= 2629.00 time=01-09 00:00
  [ 7] PEAK   price= 2858.00 time=01-22 00:00
  [ 8] TROUGH price= 2613.00 time=02-08 00:00
  [ 9] PEAK   price= 2733.00 time=02-21 00:00
  [10] TROUGH price= 2628.00 time=02-29 00:00
  [11] PEAK   price= 2752.00 time=03-11 00:00
  [12] TROUGH price= 2320.00 time=04-09 00:00
  [13] PEAK   price= 2484.00 time=04-22 00:00
  [14] TROUGH price= 2280.00 time=04-29 00:00
  [15] PEAK   price= 2978.00 time=05-21 00:00
  [16] TROUGH price= 2739.00 time=05-29 00:00
  [17] PEAK   price= 2865.00 time=05-31 00:00
  [18] TROUGH price= 2672.00 time=06-20 00:00
  [19] PEAK   price= 2765.00 time=06-27 00:00
  [20] TROUGH price= 2335.00 time=07-30 00:00
  [21] PEAK   price= 2491.00 time=08-06 00:00
  [22] TROUGH price= 2364.00 time=08-14 00:00
  [23] PEAK   price= 2539.00 time=08-20 00:00
  [24] TROUGH price= 2353.00 time=08-26 00:00
  [25] PEAK   price= 2598.00 time=09-06 00:00
  [26] TROUGH price= 2251.00 time=09-23 00:00
  [27] PEAK   price= 2865.00 time=10-21 00:00 ← A
  [28] TROUGH price= 2557.00 time=10-28 00:00
  [29] PEAK   price= 2742.00 time=11-01 00:00 ← C
```

**失败详情:**
```
  ❌ 最新(2523.00) < C(2147.00) = False
```
---

### SN — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 378500.00 |
| B 价 | 440590.00 |
| C 价 | 400300.00 |
| 最新价 | 375210.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 29 | C 索引 | 31 |

**极值点序列** (swing: 60, merged: 20):
```
  [ 0] TROUGH price=109300.00 time=04-17 00:00
  [ 1] PEAK   price=125910.00 time=05-07 00:00
  [ 2] TROUGH price=103710.00 time=07-08 00:00
  [ 3] PEAK   price=112360.00 time=07-29 00:00
  [ 4] TROUGH price=106390.00 time=08-06 00:00
  [ 5] PEAK   price=111350.00 time=08-11 00:00
  [ 6] TROUGH price=97210.00 time=09-02 00:00
  [ 7] PEAK   price=103760.00 time=09-14 00:00
  [ 8] TROUGH price=96220.00 time=09-29 00:00
  [ 9] PEAK   price=101000.00 time=10-15 00:00
  [10] TROUGH price=80000.00 time=11-24 00:00
  [11] PEAK   price=98580.00 time=12-22 00:00
  [12] TROUGH price=90110.00 time=01-08 00:00
  [13] PEAK   price=100990.00 time=01-28 00:00
  [14] TROUGH price=97030.00 time=02-15 00:00
  [15] PEAK   price=117600.00 time=03-08 00:00
  [16] TROUGH price=107610.00 time=03-11 00:00
  [17] PEAK   price=113780.00 time=03-18 00:00
  [18] TROUGH price=102700.00 time=04-01 00:00
  [19] PEAK   price=115960.00 time=04-22 00:00
```

**失败详情:**
```
  ❌ 最新(375210.00) > C(400300.00) = False
```
---

### V — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | SHORT |
| A 价 | 6364.00 |
| B 价 | 4929.00 |
| C 价 | 5371.00 |
| 最新价 | 5901.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 28 | C 索引 | 30 |

**极值点序列** (swing: 60, merged: 20):
```
  [ 0] PEAK   price= 7160.00 time=06-09 00:00
  [ 1] TROUGH price= 6715.00 time=06-23 00:00
  [ 2] PEAK   price= 8035.00 time=08-12 00:00
  [ 3] TROUGH price= 6160.00 time=09-28 00:00
  [ 4] PEAK   price= 6945.00 time=10-20 00:00
  [ 5] TROUGH price= 6660.00 time=11-02 00:00
  [ 6] PEAK   price= 7260.00 time=11-24 00:00
  [ 7] TROUGH price= 6750.00 time=11-27 00:00
  [ 8] PEAK   price= 7790.00 time=12-17 00:00
  [ 9] TROUGH price= 7340.00 time=01-07 00:00
  [10] PEAK   price= 8095.00 time=01-11 00:00
  [11] TROUGH price= 7255.00 time=02-02 00:00
  [12] PEAK   price= 7800.00 time=02-22 00:00
  [13] TROUGH price= 7330.00 time=03-16 00:00
  [14] PEAK   price= 8090.00 time=04-15 00:00
  [15] TROUGH price= 7100.00 time=05-18 00:00
  [16] PEAK   price= 7590.00 time=05-28 00:00
  [17] TROUGH price= 6900.00 time=06-07 00:00
  [18] PEAK   price= 7395.00 time=06-21 00:00
  [19] TROUGH price= 6790.00 time=07-19 00:00
```

**失败详情:**
```
  ❌ 最新(5901.00) < C(5371.00) = False
```
---

### ZN — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 23560.00 |
| B 价 | 25175.00 |
| C 价 | 24580.00 |
| 最新价 | 23550.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 30 | C 索引 | 32 |

**极值点序列** (swing: 60, merged: 20):
```
  [ 0] TROUGH price=28660.00 time=04-03 00:00
  [ 1] PEAK   price=33865.00 time=04-10 00:00
  [ 2] TROUGH price=31560.00 time=04-19 00:00
  [ 3] PEAK   price=35590.00 time=05-09 00:00
  [ 4] TROUGH price=25410.00 time=06-28 00:00
  [ 5] PEAK   price=29880.00 time=07-23 00:00
  [ 6] TROUGH price=26120.00 time=08-17 00:00
  [ 7] PEAK   price=27780.00 time=09-03 00:00
  [ 8] TROUGH price=25200.00 time=09-11 00:00
  [ 9] PEAK   price=27125.00 time=09-28 00:00
  [10] TROUGH price=25830.00 time=10-09 00:00
  [11] PEAK   price=26880.00 time=10-16 00:00
  [12] TROUGH price=16100.00 time=11-22 00:00
  [13] PEAK   price=19710.00 time=11-30 00:00
  [14] TROUGH price=17260.00 time=12-18 00:00
  [15] PEAK   price=19980.00 time=12-25 00:00
  [16] TROUGH price=18635.00 time=01-02 00:00
  [17] PEAK   price=21470.00 time=01-09 00:00
  [18] TROUGH price=17735.00 time=01-23 00:00
  [19] PEAK   price=21380.00 time=02-13 00:00
```

**失败详情:**
```
  ❌ 最新(23550.00) > C(24580.00) = False
```
---

## 📋 完整验证矩阵

| 品种 | 周期 | 方向 | A价 | B价 | C价 | 最新价 | 条件 | 判定 | DB方向 |
|------|------|------|------|------|------|--------|------|------|--------|
| A    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| A    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| A    | 1d  | SHORT |  5046.00 |  4694.00 |  4901.00 |  4935.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| A    | 1w  | LONG  |  4639.00 |  4797.00 |  4694.00 |  4739.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| AG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AG   | 1d  | LONG  | 17554.00 | 22134.00 | 17850.00 | 18583.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| AG   | 1w  | LONG  | 15070.00 | 20559.00 | 17554.00 | 15622.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| AL   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AL   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AL   | 1d  | SHORT | 25675.00 | 24160.00 | 25100.00 | 24660.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| AL   | 1w  | LONG  | 23100.00 | 25675.00 | 24020.00 | 23905.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| AO   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AO   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AO   | 1d  | LONG  |  2685.00 |  2913.00 |  2742.00 |  2822.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| AO   | 1w  | LONG  |  2760.00 |  2885.00 |  2808.00 |  2843.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| AP   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AP   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AP   | 1d  | SHORT |  9298.00 |  7505.00 |  7715.00 |  9485.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| AP   | 1w  | SHORT |  9298.00 |  7347.00 |  7799.00 |  7400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| AU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AU   | 1d  | LONG  |   929.10 |  1074.44 |   996.12 |  1048.36 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| AU   | 1w  | SHORT |  1205.78 |   929.10 |  1074.44 |   919.32 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| B    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| B    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| B    | 1d  | SHORT |  3711.00 |  3515.00 |  3611.00 |  3858.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| B    | 1w  | SHORT |  3994.00 |  3558.00 |  3711.00 |  3482.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| BR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| BR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| BR   | 1d  | SHORT | 16680.00 | 15110.00 | 16320.00 | 12035.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| BR   | 1w  | SHORT | 16680.00 | 13515.00 | 14880.00 | 12615.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| BU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| BU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| BU   | 1d  | SHORT |  4747.00 |  3950.00 |  4544.00 |  4409.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| BU   | 1w  | LONG  |  3530.00 |  4747.00 |  3950.00 |  4417.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| C    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| C    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| C    | 1d  | LONG  |  2258.00 |  2443.00 |  2361.00 |  2386.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| C    | 1w  | LONG  |  2307.00 |  2420.00 |  2337.00 |  2335.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| CF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CF   | 1d  | LONG  | 15170.00 | 16955.00 | 15855.00 | 15415.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| CF   | 1w  | SHORT | 17530.00 | 16585.00 | 16955.00 | 15675.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| CJ   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CJ   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CJ   | 1d  | LONG  |  8720.00 |  9265.00 |  8880.00 |  8905.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| CJ   | 1w  | LONG  |  8720.00 |  9265.00 |  8880.00 |  8880.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| CS   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CS   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CS   | 1d  | LONG  |  2503.00 |  2766.00 |  2705.00 |  2730.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| CS   | 1w  | LONG  |  2503.00 |  2842.00 |  2641.00 |  2714.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| CU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CU   | 1d  | SHORT | 108900.00 | 103000.00 | 107420.00 | 97030.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| CU   | 1w  | LONG  | 91500.00 | 108900.00 | 103350.00 | 104110.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| EB   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| EB   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| EB   | 1d  | SHORT | 11132.00 |  9300.00 | 10098.00 |  7966.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| EB   | 1w  | SHORT | 10098.00 |  8841.00 |  8995.00 |  8476.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| EG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| EG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| EG   | 1d  | SHORT |  5814.00 |  4613.00 |  5211.00 |  4826.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| EG   | 1w  | SHORT |  5211.00 |  4333.00 |  4661.00 |  4544.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| FG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| FG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| FG   | 1d  | SHORT |  1120.00 |  1027.00 |  1104.00 |  1094.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| FG   | 1w  | SHORT |  1120.00 |  1027.00 |  1104.00 |   989.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| HC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| HC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| HC   | 1d  | LONG  |  3181.00 |  3340.00 |  3261.00 |  3313.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| HC   | 1w  | LONG  |  3194.00 |  3348.00 |  3261.00 |  3380.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| I    | 1d  | LONG  |   760.00 |   820.00 |   777.00 |   705.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| I    | 1w  | LONG  |   748.00 |   831.50 |   748.50 |   771.50 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IF   | 1d  | LONG  |  4555.60 |  4768.00 |  4735.00 |  4907.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| IF   | 1w  | LONG  |  4307.20 |  4995.00 |  4735.00 |  4812.40 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IH   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IH   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IH   | 1d  | LONG  |  2750.80 |  3041.80 |  2791.20 |  2924.80 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IH   | 1w  | LONG  |  2750.80 |  3041.80 |  2870.00 |  2884.60 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IM   | 1d  | LONG  |  7120.20 |  8337.00 |  8056.00 |  8523.80 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IM   | 1w  | SHORT |  8908.80 |  8291.60 |  8664.80 |  8403.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| J    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| J    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| J    | 1d  | LONG  |  1622.00 |  1877.50 |  1792.50 |  1732.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| J    | 1w  | LONG  |  1717.00 |  1843.50 |  1719.00 |  1983.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| JD   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| JD   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| JD   | 1d  | SHORT |  3645.00 |  3505.00 |  3517.00 |  2945.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| JD   | 1w  | LONG  |  2885.00 |  3530.00 |  3165.00 |  4748.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| JM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| JM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| JM   | 1d  | LONG  |  1063.50 |  1294.00 |  1152.50 |  1176.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| JM   | 1w  | LONG  |  1063.50 |  1294.00 |  1152.50 |  1363.50 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| L    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| L    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| L    | 1d  | SHORT |  9407.00 |  7840.00 |  8521.00 |  7393.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| L    | 1w  | SHORT |  9523.00 |  7840.00 |  8521.00 |  7875.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| LC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LC   | 1d  | LONG  | 142000.00 | 167280.00 | 152500.00 | 147220.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| LC   | 1w  | LONG  | 152500.00 | 209880.00 | 157180.00 | 167400.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| LH   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LH   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LH   | 1d  | LONG  |  9000.00 | 11585.00 | 10625.00 | 11735.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| LH   | 1w  | SHORT | 11800.00 |  9000.00 | 11585.00 | 11950.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| LU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LU   | 1d  | SHORT |  5303.00 |  4515.00 |  4974.00 |  3770.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| LU   | 1w  | SHORT |  5350.00 |  4538.00 |  4974.00 |  3823.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| M    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| M    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| M    | 1d  | LONG  |  2933.00 |  3073.00 |  2960.00 |  3070.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| M    | 1w  | LONG  |  2852.00 |  3107.00 |  2870.00 |  2918.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| MA   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| MA   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| MA   | 1d  | SHORT |  3063.00 |  2827.00 |  2997.00 |  2847.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| MA   | 1w  | SHORT |  3063.00 |  2756.00 |  3049.00 |  2972.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| NI   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| NI   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| NI   | 1d  | LONG  | 132350.00 | 155360.00 | 140500.00 | 134540.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| NI   | 1w  | LONG  | 131840.00 | 155360.00 | 140500.00 | 135100.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| NR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| NR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| NR   | 1d  | LONG  | 12800.00 | 14155.00 | 13540.00 | 13470.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| NR   | 1w  | LONG  | 14490.00 | 16135.00 | 14810.00 | 14945.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| OI   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| OI   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| OI   | 1d  | LONG  |  9122.00 | 10030.00 |  9496.00 |  9833.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| OI   | 1w  | LONG  |  9003.00 | 10167.00 |  9122.00 |  9883.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| P    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| P    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| P    | 1d  | SHORT |  9858.00 |  9332.00 |  9825.00 |  9002.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| P    | 1w  | LONG  |  9208.00 |  9570.00 |  9332.00 |  9316.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| PB   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PB   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PB   | 1d  | SHORT | 17005.00 | 16400.00 | 16820.00 | 16655.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PB   | 1w  | LONG  | 16195.00 | 17005.00 | 16400.00 | 16130.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| PF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PF   | 1d  | SHORT |  8656.00 |  7422.00 |  7958.00 |  7008.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PF   | 1w  | SHORT |  8832.00 |  7558.00 |  8656.00 |  7274.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PG   | 1d  | LONG  |  4203.00 |  7407.00 |  5185.00 |  4510.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| PG   | 1w  | LONG  |  5420.00 |  5728.00 |  5423.00 |  5548.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| PK   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PK   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PK   | 1d  | LONG  |  8078.00 |  8324.00 |  8100.00 |  8358.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PK   | 1w  | SHORT |  8480.00 |  8100.00 |  8464.00 |  8302.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PP   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PP   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PP   | 1d  | LONG  |  6890.00 |  9980.00 |  8116.00 |  8671.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| PP   | 1w  | SHORT |  9980.00 |  8116.00 |  9088.00 |  8649.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PR   | 1d  | SHORT |  9018.00 |  7606.00 |  8074.00 |  6632.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PR   | 1w  | SHORT |  9018.00 |  8044.00 |  8508.00 |  6940.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PS   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PS   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PS   | 1d  | SHORT | 41750.00 | 36020.00 | 38835.00 | 35635.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PS   | 1w  | SHORT | 41750.00 | 36020.00 | 38835.00 | 35800.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| PX   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PX   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PX   | 1d  | SHORT | 10600.00 |  8766.00 |  9742.00 | 10018.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| PX   | 1w  | SHORT | 10084.00 |  8766.00 |  9742.00 |  8786.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| RB   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RB   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RB   | 1d  | LONG  |  3005.00 |  3167.00 |  3083.00 |  3075.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| RB   | 1w  | LONG  |  3083.00 |  3298.00 |  3136.00 |  3180.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| RM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RM   | 1d  | LONG  |  2212.00 |  2437.00 |  2309.00 |  2485.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| RM   | 1w  | LONG  |  2266.00 |  2634.00 |  2309.00 |  2239.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| RR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RR   | 1d  | SHORT |  3610.00 |  3541.00 |  3591.00 |  3631.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| RR   | 1w  | SHORT |  3737.00 |  3552.00 |  3634.00 |  3596.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| RU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RU   | 1d  | LONG  | 16480.00 | 18395.00 | 17220.00 | 16800.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| RU   | 1w  | LONG  | 15885.00 | 18395.00 | 17220.00 | 17330.00 | ✅ ✅ ✅ ✅ | ✅ | —     |
| SA   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SA   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SA   | 1d  | SHORT |  1274.00 |  1175.00 |  1234.00 |  1243.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| SA   | 1w  | SHORT |  1235.00 |  1146.00 |  1234.00 |  1152.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SC   | 1d  | LONG  |   502.30 |   588.60 |   575.30 |   416.30 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| SC   | 1w  | LONG  |   540.30 |   585.80 |   575.30 |   572.20 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| SF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SF   | 1d  | SHORT |  6190.00 |  5616.00 |  5922.00 |  5644.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| SF   | 1w  | LONG  |  5452.00 |  6196.00 |  5616.00 |  5880.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| SH   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SH   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SH   | 1d  | SHORT |  2685.00 |  2041.00 |  2147.00 |  2523.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| SH   | 1w  | SHORT |  2685.00 |  2041.00 |  2147.00 |  1889.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SI   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SI   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SI   | 1d  | LONG  |  8125.00 |  8750.00 |  8515.00 |  8850.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| SI   | 1w  | LONG  |  8125.00 |  9280.00 |  8405.00 |  8785.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| SM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SM   | 1d  | SHORT |  6720.00 |  6066.00 |  6276.00 |  5868.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SM   | 1w  | LONG  |  5714.00 |  6720.00 |  5832.00 |  6016.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SN   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SN   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SN   | 1d  | LONG  | 378500.00 | 440590.00 | 400300.00 | 375210.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| SN   | 1w  | SHORT | 469950.00 | 345000.00 | 464700.00 | 397880.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SP   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SP   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SP   | 1d  | SHORT |  5260.00 |  4944.00 |  5178.00 |  5088.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SP   | 1w  | SHORT |  5186.00 |  4788.00 |  4898.00 |  4868.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SR   | 1d  | SHORT |  5533.00 |  5259.00 |  5455.00 |  5406.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SR   | 1w  | SHORT |  5538.00 |  5339.00 |  5455.00 |  5314.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SS   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SS   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SS   | 1d  | SHORT | 15835.00 | 14600.00 | 15175.00 | 14180.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SS   | 1w  | SHORT | 15835.00 | 14600.00 | 15175.00 | 14385.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| TA   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| TA   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| TA   | 1d  | SHORT |  7270.00 |  6266.00 |  7072.00 |  6200.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| TA   | 1w  | SHORT |  7270.00 |  6010.00 |  6844.00 |  6302.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| UR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| UR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| UR   | 1d  | SHORT |  1954.00 |  1820.00 |  1905.00 |  1787.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| UR   | 1w  | SHORT |  2082.00 |  1811.00 |  1905.00 |  1793.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| V    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| V    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| V    | 1d  | SHORT |  6364.00 |  4929.00 |  5371.00 |  5901.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| V    | 1w  | SHORT |  6364.00 |  4929.00 |  5371.00 |  4706.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| Y    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| Y    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| Y    | 1d  | SHORT |  8727.00 |  8402.00 |  8682.00 |  8350.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| Y    | 1w  | SHORT |  8910.00 |  8358.00 |  8727.00 |  8320.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| ZN   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| ZN   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| ZN   | 1d  | LONG  | 23560.00 | 25175.00 | 24580.00 | 23550.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| ZN   | 1w  | SHORT | 26985.00 | 24210.00 | 24955.00 | 24620.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |

## 🔍 模式识别分析

**失败品种按失败次数排序:**

| 品种 | 失败数 |
|------|--------|
| NI | 2 |
| SC | 2 |
| A | 1 |
| AG | 1 |
| AL | 1 |
| AP | 1 |
| B | 1 |
| C | 1 |
| CF | 1 |
| CJ | 1 |
| I | 1 |
| J | 1 |
| LC | 1 |
| LH | 1 |
| NR | 1 |
| P | 1 |
| PB | 1 |
| PG | 1 |
| PX | 1 |
| RB | 1 |
| RM | 1 |
| RR | 1 |
| RU | 1 |
| SA | 1 |
| SH | 1 |
| SN | 1 |
| V | 1 |
| ZN | 1 |

**各周期失败条件分布:**

| 周期 | 失败总数 | C1 | C2 | C3 | C4 |
|------|----------|----|----|----|----|
| 15m | 0 | 0 | 0 | 0 | 0 |
| 1h  | 0 | 0 | 0 | 0 | 0 |
| 1d  | 20 | 0 | 0 | 0 | 20 |
| 1w  | 10 | 0 | 0 | 0 | 10 |

## 📌 结论

🔴 **发现 30 条标点失败的品种×周期组合。**

建议：
1. 优先排查条件4（最新价未突破 C 点）——行情自然现象，非算法问题
2. 排除条件4后，分析剩余的 C1/C2/C3 失败是否指向系统性算法偏差
3. 按 P0.2 计划进入算法调试修正
