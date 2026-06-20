# N 型结构算法全量验证报告 — （P0.2 方向优先 + 条件4整合）

> **生成时间**: 2026-06-19 11:15:20 CST
>
> 验证范围: 62 个主要品种 × 4 周期 = 248 条目
> 验证方法: 从 DB 读极值点 → `_merge_same_type()` → `_find_n_structure_forward()`
> 参数模式: （P0.2 方向优先 + 条件4整合）
> 方向预判: 是 · current_price传入: 是

## 📊 整体统计

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 全部通过 | 107 | 43.1% |
| ❌ 有失败条件 | 17 | 6.9% |
| ⚠️ 数据不足 | 124 | 50.0% |
| **总计** | **248** | **100%** |

### 📈 按周期统计

| 周期 | 通过 | 失败 | N/A | 合计 | 通过率 |
|------|------|------|-----|------|--------|
| 15m | 0 | 0 | 62 | 62 | — |
| 1h  | 0 | 0 | 62 | 62 | — |
| 1d  | 56 | 6 | 0 | 62 | 90% |
| 1w  | 51 | 11 | 0 | 62 | 82% |

## ❌ 未通过验证的品种×周期（{len(fail_list)} 条）

### C — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2317.00 |
| B 价 | 2479.00 |
| C 价 | 2337.00 |
| 最新价 | 2335.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 11 | C 索引 | 57 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] PEAK   price= 1340.00 time=12-12 00:00
  [ 1] TROUGH price= 1266.00 time=12-21 00:00
  [ 2] PEAK   price= 1398.00 time=01-04 00:00
  [ 3] TROUGH price= 1331.00 time=01-11 00:00
  [ 4] PEAK   price= 1393.00 time=01-17 00:00
  [ 5] TROUGH price= 1324.00 time=01-19 00:00
  [ 6] PEAK   price= 1538.00 time=02-07 00:00
  [ 7] TROUGH price= 1398.00 time=03-17 00:00
  [ 8] PEAK   price= 1453.00 time=04-07 00:00
  [ 9] TROUGH price= 1374.00 time=04-20 00:00
  [10] PEAK   price= 1554.00 time=05-30 00:00
  [11] TROUGH price= 1451.00 time=06-20 00:00 ← A
  [12] PEAK   price= 1503.00 time=07-06 00:00
  [13] TROUGH price= 1375.00 time=08-14 00:00
  [14] PEAK   price= 1429.00 time=08-18 00:00
  [15] TROUGH price= 1388.00 time=08-30 00:00
  [16] PEAK   price= 1426.00 time=09-08 00:00
  [17] TROUGH price= 1392.00 time=09-25 00:00
  [18] PEAK   price= 1754.00 time=11-27 00:00
  [19] TROUGH price= 1564.00 time=12-04 00:00
  [20] PEAK   price= 1758.00 time=12-26 00:00
  [21] TROUGH price= 1656.00 time=01-10 00:00
  [22] PEAK   price= 1795.00 time=01-16 00:00
  [23] TROUGH price= 1694.00 time=01-30 00:00
  [24] PEAK   price= 1726.00 time=02-05 00:00
  [25] TROUGH price= 1685.00 time=02-15 00:00
  [26] PEAK   price= 1744.00 time=02-26 00:00
  [27] TROUGH price= 1679.00 time=03-12 00:00
  [28] PEAK   price= 1700.00 time=03-21 00:00
  [29] TROUGH price= 1630.00 time=04-02 00:00
  [30] PEAK   price= 1700.00 time=04-09 00:00
  [31] TROUGH price= 1628.00 time=04-18 00:00
  [32] PEAK   price= 1745.00 time=05-22 00:00
  [33] TROUGH price= 1487.00 time=07-12 00:00
  [34] PEAK   price= 1518.00 time=07-19 00:00
  [35] TROUGH price= 1470.00 time=07-26 00:00
  [36] PEAK   price= 1606.00 time=08-15 00:00
  [37] TROUGH price= 1541.00 time=08-17 00:00
  [38] PEAK   price= 1689.00 time=09-13 00:00
  [39] TROUGH price= 1615.00 time=09-25 00:00
  [40] PEAK   price= 1675.00 time=10-09 00:00
  [41] TROUGH price= 1633.00 time=10-23 00:00
  [42] PEAK   price= 1790.00 time=11-15 00:00
  [43] TROUGH price= 1708.00 time=11-20 00:00
  [44] PEAK   price= 1816.00 time=11-26 00:00
  [45] TROUGH price= 1726.00 time=12-07 00:00
  [46] PEAK   price= 1766.00 time=12-17 00:00
  [47] TROUGH price= 1676.00 time=01-02 00:00
  [48] PEAK   price= 1850.00 time=01-08 00:00
  [49] TROUGH price= 1709.00 time=01-22 00:00
  [50] PEAK   price= 1827.00 time=02-18 00:00
  [51] TROUGH price= 1781.00 time=02-28 00:00
  [52] PEAK   price= 1900.00 time=03-04 00:00
  [53] TROUGH price= 1736.00 time=03-20 00:00
  [54] PEAK   price= 1958.00 time=03-31 00:00
  [55] TROUGH price= 1867.00 time=04-09 00:00
  [56] PEAK   price= 1949.00 time=04-15 00:00
  [57] TROUGH price= 1899.00 time=04-22 00:00 ← C
  [58] PEAK   price= 1990.00 time=05-12 00:00
  [59] TROUGH price= 1868.00 time=05-30 00:00
```

**失败详情:**
```
  ❌ 最新(2335.00) > C(2337.00) = False
```
---

### C — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2258.00 |
| B 价 | 2443.00 |
| C 价 | 2337.00 |
| 最新价 | 2335.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 75 | C 索引 | 77 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price= 1735.00 time=03-27 00:00
  [ 1] PEAK   price= 1779.00 time=04-03 00:00
  [ 2] TROUGH price= 1724.00 time=04-24 00:00
  [ 3] PEAK   price= 1795.00 time=05-29 00:00
  [ 4] TROUGH price= 1751.00 time=06-12 00:00
  [ 5] PEAK   price= 1939.00 time=09-04 00:00
  [ 6] TROUGH price= 1840.00 time=10-09 00:00
  [ 7] PEAK   price= 1997.00 time=11-13 00:00
  [ 8] TROUGH price= 1802.00 time=01-15 00:00
  [ 9] PEAK   price= 1875.00 time=01-29 00:00
  [10] TROUGH price= 1780.00 time=02-19 00:00
  [11] PEAK   price= 2021.00 time=05-14 00:00
  [12] TROUGH price= 1909.00 time=07-09 00:00
  [13] PEAK   price= 1979.00 time=08-06 00:00
  [14] TROUGH price= 1810.00 time=09-24 00:00
  [15] PEAK   price= 1895.00 time=10-29 00:00
  [16] TROUGH price= 1814.00 time=11-26 00:00
  [17] PEAK   price= 1910.00 time=12-03 00:00
  [18] TROUGH price= 1873.00 time=12-17 00:00
  [19] PEAK   price= 1950.00 time=01-14 00:00
  [20] TROUGH price= 1900.00 time=02-18 00:00
  [21] PEAK   price= 2109.00 time=04-21 00:00
  [22] TROUGH price= 2013.00 time=05-19 00:00
  [23] PEAK   price= 2149.00 time=06-16 00:00
  [24] TROUGH price= 2076.00 time=06-30 00:00
  [25] PEAK   price= 2629.00 time=10-13 00:00
  [26] TROUGH price= 2492.00 time=11-03 00:00
  [27] PEAK   price= 2692.00 time=12-01 00:00
  [28] TROUGH price= 2556.00 time=12-15 00:00
  [29] PEAK   price= 2930.00 time=01-12 00:00
  [30] TROUGH price= 2704.00 time=01-26 00:00
  [31] PEAK   price= 2855.00 time=02-18 00:00
  [32] TROUGH price= 2593.00 time=03-30 00:00
  [33] PEAK   price= 2887.00 time=05-11 00:00
  [34] TROUGH price= 2655.00 time=05-25 00:00
  [35] PEAK   price= 2768.00 time=06-08 00:00
  [36] TROUGH price= 2502.00 time=07-20 00:00
  [37] PEAK   price= 2632.00 time=08-10 00:00
  [38] TROUGH price= 2429.00 time=09-22 00:00
  [39] PEAK   price= 2736.00 time=11-09 00:00
  [40] TROUGH price= 2617.00 time=11-23 00:00
  [41] PEAK   price= 2756.00 time=12-14 00:00
  [42] TROUGH price= 2660.00 time=12-28 00:00
  [43] PEAK   price= 2932.00 time=03-01 00:00
  [44] TROUGH price= 2820.00 time=03-29 00:00
  [45] PEAK   price= 3046.00 time=04-26 00:00
  [46] TROUGH price= 2548.00 time=07-19 00:00
  [47] PEAK   price= 2865.00 time=09-20 00:00
  [48] TROUGH price= 2742.00 time=09-27 00:00
  [49] PEAK   price= 2900.00 time=11-01 00:00
  [50] TROUGH price= 2800.00 time=11-15 00:00
  [51] PEAK   price= 2944.00 time=11-29 00:00
  [52] TROUGH price= 2726.00 time=12-20 00:00
  [53] PEAK   price= 2910.00 time=01-10 00:00
  [54] TROUGH price= 2758.00 time=02-07 00:00
  [55] PEAK   price= 2882.00 time=02-21 00:00
  [56] TROUGH price= 2495.00 time=05-09 00:00
  [57] PEAK   price= 2797.00 time=07-04 00:00
  [58] TROUGH price= 2679.00 time=07-18 00:00
  [59] PEAK   price= 2819.00 time=08-08 00:00
  [60] TROUGH price= 2610.00 time=08-15 00:00
  [61] PEAK   price= 2746.00 time=08-29 00:00
  [62] TROUGH price= 2482.00 time=10-17 00:00
  [63] PEAK   price= 2580.00 time=11-21 00:00
  [64] TROUGH price= 2317.00 time=01-16 00:00
  [65] PEAK   price= 2479.00 time=02-20 00:00
  [66] TROUGH price= 2381.00 time=03-26 00:00
  [67] PEAK   price= 2443.00 time=04-02 00:00
  [68] TROUGH price= 2370.00 time=04-16 00:00
  [69] PEAK   price= 2520.00 time=06-25 00:00
  [70] TROUGH price= 2250.00 time=08-06 00:00
  [71] PEAK   price= 2357.00 time=08-27 00:00
  [72] TROUGH price= 2105.00 time=09-18 00:00
  [73] PEAK   price= 2254.00 time=10-29 00:00
  [74] TROUGH price= 2035.00 time=12-03 00:00
  [75] PEAK   price= 2325.00 time=02-11 00:00 ← A
  [76] TROUGH price= 2260.00 time=02-25 00:00
  [77] PEAK   price= 2336.00 time=03-04 00:00 ← C
  [78] TROUGH price= 2244.00 time=03-25 00:00
  [79] PEAK   price= 2389.00 time=05-06 00:00
```

**失败详情:**
```
  ❌ 最新(2335.00) > C(2337.00) = False
```
---

### CF — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 15035.00 |
| B 价 | 16955.00 |
| C 价 | 15855.00 |
| 最新价 | 15675.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 76 | C 索引 | 78 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price=14850.00 time=03-20 00:00
  [ 1] PEAK   price=19250.00 time=05-29 00:00
  [ 2] TROUGH price=16045.00 time=07-03 00:00
  [ 3] PEAK   price=17555.00 time=08-07 00:00
  [ 4] TROUGH price=14670.00 time=11-06 00:00
  [ 5] PEAK   price=15520.00 time=11-20 00:00
  [ 6] TROUGH price=14650.00 time=12-25 00:00
  [ 7] PEAK   price=15480.00 time=01-15 00:00
  [ 8] TROUGH price=14950.00 time=02-12 00:00
  [ 9] PEAK   price=15645.00 time=02-19 00:00
  [10] TROUGH price=14995.00 time=03-26 00:00
  [11] PEAK   price=16225.00 time=04-09 00:00
  [12] TROUGH price=12720.00 time=06-04 00:00
  [13] PEAK   price=14300.00 time=06-25 00:00
  [14] TROUGH price=12075.00 time=08-06 00:00
  [15] PEAK   price=13285.00 time=09-10 00:00
  [16] TROUGH price=11970.00 time=09-24 00:00
  [17] PEAK   price=13215.00 time=10-29 00:00
  [18] TROUGH price=12580.00 time=11-19 00:00
  [19] PEAK   price=14450.00 time=01-14 00:00
  [20] TROUGH price=12130.00 time=02-04 00:00
  [21] PEAK   price=13510.00 time=02-11 00:00
  [22] TROUGH price= 9935.00 time=03-24 00:00
  [23] PEAK   price=11750.00 time=04-07 00:00
  [24] TROUGH price=10855.00 time=04-21 00:00
  [25] PEAK   price=12155.00 time=06-02 00:00
  [26] TROUGH price=11600.00 time=06-23 00:00
  [27] PEAK   price=13180.00 time=08-25 00:00
  [28] TROUGH price=12215.00 time=09-08 00:00
  [29] PEAK   price=15305.00 time=10-13 00:00
  [30] TROUGH price=13920.00 time=11-03 00:00
  [31] PEAK   price=15610.00 time=01-05 00:00
  [32] TROUGH price=14735.00 time=01-26 00:00
  [33] PEAK   price=17080.00 time=02-23 00:00
  [34] TROUGH price=14285.00 time=03-23 00:00
  [35] PEAK   price=16355.00 time=05-11 00:00
  [36] TROUGH price=15300.00 time=05-25 00:00
  [37] PEAK   price=16160.00 time=06-08 00:00
  [38] TROUGH price=15400.00 time=06-22 00:00
  [39] PEAK   price=18505.00 time=08-17 00:00
  [40] TROUGH price=17030.00 time=09-22 00:00
  [41] PEAK   price=22960.00 time=10-12 00:00
  [42] TROUGH price=18935.00 time=11-30 00:00
  [43] PEAK   price=22210.00 time=02-07 00:00
  [44] TROUGH price=20640.00 time=02-22 00:00
  [45] PEAK   price=22000.00 time=03-22 00:00
  [46] TROUGH price=20995.00 time=04-26 00:00
  [47] PEAK   price=22035.00 time=05-05 00:00
  [48] TROUGH price=13560.00 time=07-12 00:00
  [49] PEAK   price=15790.00 time=08-16 00:00
  [50] TROUGH price=13195.00 time=09-27 00:00
  [51] PEAK   price=13975.00 time=10-11 00:00
  [52] TROUGH price=12270.00 time=10-25 00:00
  [53] PEAK   price=15275.00 time=01-31 00:00
  [54] TROUGH price=14085.00 time=02-14 00:00
  [55] PEAK   price=14780.00 time=02-28 00:00
  [56] TROUGH price=13715.00 time=03-14 00:00
  [57] PEAK   price=17070.00 time=06-06 00:00
  [58] TROUGH price=16120.00 time=06-27 00:00
  [59] PEAK   price=17530.00 time=08-01 00:00
  [60] TROUGH price=16585.00 time=08-15 00:00
  [61] PEAK   price=17905.00 time=08-29 00:00
  [62] TROUGH price=16910.00 time=09-12 00:00
  [63] PEAK   price=17815.00 time=10-09 00:00
  [64] TROUGH price=14740.00 time=11-28 00:00
  [65] PEAK   price=16450.00 time=02-27 00:00
  [66] TROUGH price=15810.00 time=03-26 00:00
  [67] PEAK   price=16480.00 time=04-09 00:00
  [68] TROUGH price=14840.00 time=05-14 00:00
  [69] PEAK   price=15630.00 time=05-28 00:00
  [70] TROUGH price=14340.00 time=06-18 00:00
  [71] PEAK   price=14880.00 time=07-02 00:00
  [72] TROUGH price=13200.00 time=08-13 00:00
  [73] PEAK   price=14755.00 time=10-08 00:00
  [74] TROUGH price=13920.00 time=10-15 00:00
  [75] PEAK   price=14250.00 time=11-05 00:00
  [76] TROUGH price=13315.00 time=12-17 00:00 ← A
  [77] PEAK   price=13930.00 time=02-18 00:00
  [78] TROUGH price=12315.00 time=04-08 00:00 ← C
  [79] PEAK   price=13560.00 time=05-20 00:00
```

**失败详情:**
```
  ❌ 最新(15675.00) > C(15855.00) = False
```
---

### CJ — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8720.00 |
| B 价 | 9265.00 |
| C 价 | 8880.00 |
| 最新价 | 8880.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 50 | C 索引 | 58 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] PEAK   price=10935.00 time=05-27 00:00
  [ 1] TROUGH price= 9605.00 time=06-10 00:00
  [ 2] PEAK   price=10675.00 time=06-27 00:00
  [ 3] TROUGH price=10155.00 time=07-02 00:00
  [ 4] PEAK   price=10645.00 time=07-09 00:00
  [ 5] TROUGH price= 9995.00 time=07-24 00:00
  [ 6] PEAK   price=11000.00 time=08-12 00:00
  [ 7] TROUGH price=10505.00 time=08-14 00:00
  [ 8] PEAK   price=11555.00 time=09-04 00:00
  [ 9] TROUGH price=10060.00 time=09-23 00:00
  [10] PEAK   price=10580.00 time=10-15 00:00
  [11] TROUGH price= 9770.00 time=10-18 00:00
  [12] PEAK   price=11260.00 time=11-14 00:00
  [13] TROUGH price=10755.00 time=11-27 00:00
  [14] PEAK   price=11110.00 time=11-29 00:00
  [15] TROUGH price=10580.00 time=12-06 00:00
  [16] PEAK   price=11015.00 time=12-30 00:00
  [17] TROUGH price=10115.00 time=01-10 00:00
  [18] PEAK   price=10665.00 time=01-20 00:00
  [19] TROUGH price= 9890.00 time=02-04 00:00
  [20] PEAK   price=10665.00 time=02-20 00:00
  [21] TROUGH price=10275.00 time=02-27 00:00
  [22] PEAK   price=10710.00 time=03-02 00:00
  [23] TROUGH price= 9670.00 time=03-26 00:00
  [24] PEAK   price=10300.00 time=03-30 00:00
  [25] TROUGH price= 9835.00 time=04-08 00:00
  [26] PEAK   price=10270.00 time=04-09 00:00
  [27] TROUGH price= 9930.00 time=04-16 00:00
  [28] PEAK   price=10465.00 time=04-27 00:00
  [29] TROUGH price= 9845.00 time=06-01 00:00
  [30] PEAK   price=10170.00 time=06-11 00:00
  [31] TROUGH price= 8980.00 time=07-24 00:00
  [32] PEAK   price= 9365.00 time=07-31 00:00
  [33] TROUGH price= 8755.00 time=08-07 00:00
  [34] PEAK   price= 9530.00 time=08-11 00:00
  [35] TROUGH price= 8910.00 time=08-19 00:00
  [36] PEAK   price=10335.00 time=09-09 00:00
  [37] TROUGH price= 9680.00 time=09-30 00:00
  [38] PEAK   price=10250.00 time=10-14 00:00
  [39] TROUGH price= 9715.00 time=10-29 00:00
  [40] PEAK   price=10030.00 time=11-11 00:00
  [41] TROUGH price= 9595.00 time=11-17 00:00
  [42] PEAK   price=10075.00 time=11-23 00:00
  [43] TROUGH price= 9165.00 time=12-10 00:00
  [44] PEAK   price=10145.00 time=12-16 00:00
  [45] TROUGH price= 9705.00 time=12-22 00:00
  [46] PEAK   price=10445.00 time=01-08 00:00
  [47] TROUGH price= 9915.00 time=02-10 00:00
  [48] PEAK   price=10955.00 time=02-26 00:00
  [49] TROUGH price= 9620.00 time=04-02 00:00
  [50] PEAK   price=10345.00 time=04-20 00:00 ← A
  [51] TROUGH price= 8485.00 time=05-20 00:00
  [52] PEAK   price= 9470.00 time=05-24 00:00
  [53] TROUGH price= 8225.00 time=06-21 00:00
  [54] PEAK   price=13445.00 time=08-03 00:00
  [55] TROUGH price=12620.00 time=08-09 00:00
  [56] PEAK   price=15005.00 time=08-26 00:00
  [57] TROUGH price=13315.00 time=09-13 00:00
  [58] PEAK   price=16065.00 time=09-30 00:00 ← C
  [59] TROUGH price=13565.00 time=10-13 00:00
```

**失败详情:**
```
  ❌ 最新(8880.00) > C(8880.00) = False
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
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 71 | C 索引 | 77 |

**极值点序列** (swing: 79, merged: 79):
```
  [ 0] PEAK   price=10935.00 time=05-21 00:00
  [ 1] TROUGH price= 9605.00 time=06-04 00:00
  [ 2] PEAK   price=10675.00 time=06-25 00:00
  [ 3] TROUGH price= 9995.00 time=07-23 00:00
  [ 4] PEAK   price=11555.00 time=09-03 00:00
  [ 5] TROUGH price= 9770.00 time=10-15 00:00
  [ 6] PEAK   price=11260.00 time=11-12 00:00
  [ 7] TROUGH price=10580.00 time=12-03 00:00
  [ 8] PEAK   price=11015.00 time=12-24 00:00
  [ 9] TROUGH price= 9890.00 time=02-04 00:00
  [10] PEAK   price=10710.00 time=02-25 00:00
  [11] TROUGH price= 9670.00 time=03-24 00:00
  [12] PEAK   price=10465.00 time=04-21 00:00
  [13] TROUGH price= 9845.00 time=05-26 00:00
  [14] PEAK   price=10170.00 time=06-09 00:00
  [15] TROUGH price= 8755.00 time=08-04 00:00
  [16] PEAK   price=10335.00 time=09-08 00:00
  [17] TROUGH price= 9680.00 time=09-29 00:00
  [18] PEAK   price=10250.00 time=10-13 00:00
  [19] TROUGH price= 9715.00 time=10-27 00:00
  [20] PEAK   price=10075.00 time=11-17 00:00
  [21] TROUGH price= 9165.00 time=12-08 00:00
  [22] PEAK   price=10445.00 time=01-05 00:00
  [23] TROUGH price= 9915.00 time=02-09 00:00
  [24] PEAK   price=10955.00 time=02-23 00:00
  [25] TROUGH price= 9620.00 time=03-30 00:00
  [26] PEAK   price=10345.00 time=04-20 00:00
  [27] TROUGH price= 8225.00 time=06-15 00:00
  [28] PEAK   price=15005.00 time=08-24 00:00
  [29] TROUGH price=13315.00 time=09-07 00:00
  [30] PEAK   price=16465.00 time=10-19 00:00
  [31] TROUGH price=12820.00 time=10-26 00:00
  [32] PEAK   price=17655.00 time=11-23 00:00
  [33] TROUGH price=12350.00 time=01-04 00:00
  [34] PEAK   price=14430.00 time=02-15 00:00
  [35] TROUGH price=10980.00 time=04-06 00:00
  [36] PEAK   price=13050.00 time=05-17 00:00
  [37] TROUGH price=10235.00 time=06-14 00:00
  [38] PEAK   price=12790.00 time=07-12 00:00
  [39] TROUGH price=11635.00 time=08-16 00:00
  [40] PEAK   price=12595.00 time=09-13 00:00
  [41] TROUGH price=10765.00 time=11-01 00:00
  [42] PEAK   price=11070.00 time=12-06 00:00
  [43] TROUGH price= 9925.00 time=12-20 00:00
  [44] PEAK   price=11005.00 time=01-31 00:00
  [45] TROUGH price= 9315.00 time=03-21 00:00
  [46] PEAK   price=10950.00 time=05-04 00:00
  [47] TROUGH price= 9930.00 time=05-23 00:00
  [48] PEAK   price=13845.00 time=09-19 00:00
  [49] TROUGH price=12585.00 time=10-10 00:00
  [50] PEAK   price=15730.00 time=12-05 00:00
  [51] TROUGH price=11905.00 time=02-06 00:00
  [52] PEAK   price=13175.00 time=02-27 00:00
  [53] TROUGH price=11660.00 time=04-02 00:00
  [54] PEAK   price=13215.00 time=04-23 00:00
  [55] TROUGH price=10130.00 time=07-09 00:00
  [56] PEAK   price=11035.00 time=07-23 00:00
  [57] TROUGH price= 9045.00 time=09-18 00:00
  [58] PEAK   price=10760.00 time=10-29 00:00
  [59] TROUGH price= 9230.00 time=11-19 00:00
  [60] PEAK   price= 9730.00 time=12-10 00:00
  [61] TROUGH price= 8940.00 time=01-07 00:00
  [62] PEAK   price= 9580.00 time=02-05 00:00
  [63] TROUGH price= 8830.00 time=04-08 00:00
  [64] PEAK   price= 9555.00 time=04-15 00:00
  [65] TROUGH price= 8850.00 time=05-06 00:00
  [66] PEAK   price= 9235.00 time=05-13 00:00
  [67] TROUGH price= 8560.00 time=05-27 00:00
  [68] PEAK   price=11825.00 time=08-05 00:00
  [69] TROUGH price=10580.00 time=09-16 00:00
  [70] PEAK   price=11480.00 time=10-14 00:00
  [71] TROUGH price= 8720.00 time=12-23 00:00 ← A
  [72] PEAK   price= 9265.00 time=01-06 00:00
  [73] TROUGH price= 8610.00 time=02-10 00:00
  [74] PEAK   price= 9370.00 time=03-03 00:00
  [75] TROUGH price= 8295.00 time=04-07 00:00
  [76] PEAK   price= 9440.00 time=05-12 00:00
  [77] TROUGH price= 8880.00 time=05-19 00:00 ← C
  [78] PEAK   price= 9670.00 time=06-02 00:00
```

**失败详情:**
```
  ❌ 最新(8880.00) > C(8880.00) = False
```
---

### CS — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2705.00 |
| B 价 | 2827.00 |
| C 价 | 2727.00 |
| 最新价 | 2714.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 55 | C 索引 | 57 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] TROUGH price= 2624.00 time=01-06 00:00
  [ 1] PEAK   price= 2880.00 time=02-10 00:00
  [ 2] TROUGH price= 2580.00 time=02-25 00:00
  [ 3] PEAK   price= 3100.00 time=03-31 00:00
  [ 4] TROUGH price= 2914.00 time=04-15 00:00
  [ 5] PEAK   price= 3039.00 time=05-15 00:00
  [ 6] TROUGH price= 2815.00 time=06-15 00:00
  [ 7] PEAK   price= 2920.00 time=06-23 00:00
  [ 8] TROUGH price= 2820.00 time=06-30 00:00
  [ 9] PEAK   price= 2889.00 time=07-01 00:00
  [10] TROUGH price= 2756.00 time=07-08 00:00
  [11] PEAK   price= 2913.00 time=07-13 00:00
  [12] TROUGH price= 2334.00 time=08-13 00:00
  [13] PEAK   price= 2710.00 time=09-07 00:00
  [14] TROUGH price= 1890.00 time=10-23 00:00
  [15] PEAK   price= 2154.00 time=11-16 00:00
  [16] TROUGH price= 2057.00 time=11-20 00:00
  [17] PEAK   price= 2211.00 time=11-30 00:00
  [18] TROUGH price= 2028.00 time=12-10 00:00
  [19] PEAK   price= 2162.00 time=12-22 00:00
  [20] TROUGH price= 1997.00 time=12-28 00:00
  [21] PEAK   price= 2174.00 time=02-16 00:00
  [22] TROUGH price= 1991.00 time=02-29 00:00
  [23] PEAK   price= 2150.00 time=03-07 00:00
  [24] TROUGH price= 1896.00 time=03-31 00:00
  [25] PEAK   price= 2216.00 time=04-21 00:00
  [26] TROUGH price= 2005.00 time=05-03 00:00
  [27] PEAK   price= 2374.00 time=06-15 00:00
  [28] TROUGH price= 1870.00 time=07-08 00:00
  [29] PEAK   price= 1949.00 time=07-13 00:00
  [30] TROUGH price= 1766.00 time=07-29 00:00
  [31] PEAK   price= 1885.00 time=08-16 00:00
  [32] TROUGH price= 1663.00 time=09-08 00:00
  [33] PEAK   price= 1712.00 time=09-19 00:00
  [34] TROUGH price= 1600.00 time=09-28 00:00
  [35] PEAK   price= 1935.00 time=11-11 00:00
  [36] TROUGH price= 1821.00 time=11-25 00:00
  [37] PEAK   price= 1957.00 time=11-30 00:00
  [38] TROUGH price= 1768.00 time=12-22 00:00
  [39] PEAK   price= 1853.00 time=12-28 00:00
  [40] TROUGH price= 1743.00 time=01-03 00:00
  [41] PEAK   price= 1875.00 time=02-06 00:00
  [42] TROUGH price= 1787.00 time=02-17 00:00
  [43] PEAK   price= 1952.00 time=03-06 00:00
  [44] TROUGH price= 1861.00 time=03-13 00:00
  [45] PEAK   price= 2143.00 time=03-27 00:00
  [46] TROUGH price= 1974.00 time=04-11 00:00
  [47] PEAK   price= 2038.00 time=04-21 00:00
  [48] TROUGH price= 1933.00 time=05-04 00:00
  [49] PEAK   price= 1987.00 time=05-05 00:00
  [50] TROUGH price=    7.00 time=05-25 00:00
  [51] PEAK   price= 2059.00 time=06-28 00:00
  [52] TROUGH price= 1923.00 time=08-07 00:00
  [53] PEAK   price= 2056.00 time=08-23 00:00
  [54] TROUGH price= 1973.00 time=08-31 00:00
  [55] PEAK   price= 2047.00 time=09-06 00:00 ← A
  [56] TROUGH price= 1955.00 time=09-18 00:00
  [57] PEAK   price= 2050.00 time=10-09 00:00 ← C
  [58] TROUGH price= 1923.00 time=10-24 00:00
  [59] PEAK   price= 2186.00 time=11-15 00:00
```

**失败详情:**
```
  ❌ 最新(2714.00) > C(2727.00) = False
```
---

### EB — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 8007.00 |
| B 价 | 11132.00 |
| C 价 | 9300.00 |
| 最新价 | 8476.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 56 | C 索引 | 70 |

**极值点序列** (swing: 72, merged: 72):
```
  [ 0] TROUGH price= 6872.00 time=11-12 00:00
  [ 1] PEAK   price= 7494.00 time=12-03 00:00
  [ 2] TROUGH price= 7237.00 time=12-31 00:00
  [ 3] PEAK   price= 7587.00 time=01-14 00:00
  [ 4] TROUGH price= 6497.00 time=02-04 00:00
  [ 5] PEAK   price= 7078.00 time=02-18 00:00
  [ 6] TROUGH price= 4338.00 time=03-24 00:00
  [ 7] PEAK   price= 5988.00 time=06-02 00:00
  [ 8] TROUGH price= 5070.00 time=08-18 00:00
  [ 9] PEAK   price= 5880.00 time=09-01 00:00
  [10] TROUGH price= 5421.00 time=09-22 00:00
  [11] PEAK   price= 8435.00 time=11-10 00:00
  [12] TROUGH price= 6011.00 time=12-29 00:00
  [13] PEAK   price=10090.00 time=02-23 00:00
  [14] TROUGH price= 7785.00 time=03-16 00:00
  [15] PEAK   price=10242.00 time=05-11 00:00
  [16] TROUGH price= 8195.00 time=06-15 00:00
  [17] PEAK   price= 9587.00 time=06-29 00:00
  [18] TROUGH price= 8252.00 time=08-17 00:00
  [19] PEAK   price=10279.00 time=10-12 00:00
  [20] TROUGH price= 7465.00 time=11-23 00:00
  [21] PEAK   price= 9600.00 time=02-07 00:00
  [22] TROUGH price= 8706.00 time=02-15 00:00
  [23] PEAK   price=10608.00 time=03-08 00:00
  [24] TROUGH price= 9334.00 time=04-26 00:00
  [25] PEAK   price=11515.00 time=06-07 00:00
  [26] TROUGH price= 7663.00 time=08-16 00:00
  [27] PEAK   price= 9400.00 time=09-20 00:00
  [28] TROUGH price= 7552.00 time=11-01 00:00
  [29] PEAK   price= 8380.00 time=11-15 00:00
  [30] TROUGH price= 7550.00 time=11-29 00:00
  [31] PEAK   price= 9068.00 time=01-30 00:00
  [32] TROUGH price= 8250.00 time=02-07 00:00
  [33] PEAK   price= 8682.00 time=02-21 00:00
  [34] TROUGH price= 8049.00 time=03-14 00:00
  [35] PEAK   price= 8775.00 time=04-11 00:00
  [36] TROUGH price= 6980.00 time=06-13 00:00
  [37] PEAK   price= 9998.00 time=09-12 00:00
  [38] TROUGH price= 8235.00 time=10-10 00:00
  [39] PEAK   price= 8888.00 time=11-14 00:00
  [40] TROUGH price= 7756.00 time=12-05 00:00
  [41] PEAK   price= 8675.00 time=12-19 00:00
  [42] TROUGH price= 8227.00 time=01-09 00:00
  [43] PEAK   price= 9387.00 time=02-19 00:00
  [44] TROUGH price= 8961.00 time=02-27 00:00
  [45] PEAK   price= 9780.00 time=04-16 00:00
  [46] TROUGH price= 9076.00 time=05-07 00:00
  [47] PEAK   price= 9819.00 time=05-28 00:00
  [48] TROUGH price= 9127.00 time=06-25 00:00
  [49] PEAK   price= 9535.00 time=07-02 00:00
  [50] TROUGH price= 8804.00 time=07-23 00:00
  [51] PEAK   price= 9383.00 time=08-13 00:00
  [52] TROUGH price= 8265.00 time=09-10 00:00
  [53] PEAK   price= 9188.00 time=10-08 00:00
  [54] TROUGH price= 8234.00 time=11-26 00:00
  [55] PEAK   price= 8576.00 time=12-03 00:00
  [56] TROUGH price= 8007.00 time=01-07 00:00 ← A
  [57] PEAK   price= 8815.00 time=02-05 00:00
  [58] TROUGH price= 6780.00 time=04-08 00:00
  [59] PEAK   price= 7853.00 time=05-13 00:00
  [60] TROUGH price= 6985.00 time=06-03 00:00
  [61] PEAK   price= 7787.00 time=06-10 00:00
  [62] TROUGH price= 7180.00 time=06-24 00:00
  [63] PEAK   price= 7593.00 time=07-22 00:00
  [64] TROUGH price= 6230.00 time=11-11 00:00
  [65] PEAK   price= 6676.00 time=12-02 00:00
  [66] TROUGH price= 6343.00 time=12-16 00:00
  [67] PEAK   price= 8027.00 time=01-27 00:00
  [68] TROUGH price= 7323.00 time=02-10 00:00
  [69] PEAK   price=11132.00 time=03-17 00:00
  [70] TROUGH price= 9300.00 time=04-14 00:00 ← C
  [71] PEAK   price=10098.00 time=04-28 00:00
```

**失败详情:**
```
  ❌ 最新(8476.00) > C(9300.00) = False
```
---

### I — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 760.00 |
| B 价 | 820.00 |
| C 价 | 777.00 |
| 最新价 | 771.50 |
| DB 方向 | — (状态: —) |
| A 索引 | 47 | C 索引 | 59 |

**极值点序列** (swing: 60, merged: 60):
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
  [20] TROUGH price=  537.00 time=09-29 00:00
  [21] PEAK   price=  591.00 time=10-14 00:00
  [22] TROUGH price=  518.00 time=10-23 00:00
  [23] PEAK   price=  543.00 time=10-30 00:00
  [24] TROUGH price=  458.00 time=11-26 00:00
  [25] PEAK   price=  497.00 time=12-08 00:00
  [26] TROUGH price=  470.00 time=12-24 00:00
  [27] PEAK   price=  521.00 time=01-07 00:00
  [28] TROUGH price=  466.00 time=01-26 00:00
  [29] PEAK   price=  499.00 time=02-16 00:00
  [30] TROUGH price=  445.00 time=03-09 00:00
  [31] PEAK   price=  465.00 time=03-13 00:00
  [32] TROUGH price=  368.00 time=04-10 00:00
  [33] PEAK   price=  401.00 time=04-15 00:00
  [34] TROUGH price=  378.00 time=04-21 00:00
  [35] PEAK   price=  448.00 time=05-06 00:00
  [36] TROUGH price=  410.50 time=05-20 00:00
  [37] PEAK   price=  446.00 time=06-02 00:00
  [38] TROUGH price=  431.00 time=06-09 00:00
  [39] PEAK   price=  458.50 time=06-11 00:00
  [40] TROUGH price=  423.50 time=06-18 00:00
  [41] PEAK   price=  517.00 time=06-23 00:00
  [42] TROUGH price=  333.00 time=07-09 00:00
  [43] PEAK   price=  382.00 time=07-20 00:00
  [44] TROUGH price=  346.00 time=07-23 00:00
  [45] PEAK   price=  390.00 time=08-17 00:00
  [46] TROUGH price=  355.50 time=08-25 00:00
  [47] PEAK   price=  467.00 time=09-07 00:00 ← A
  [48] TROUGH price=  361.00 time=09-29 00:00
  [49] PEAK   price=  551.00 time=10-08 00:00
  [50] TROUGH price=  342.50 time=11-06 00:00
  [51] PEAK   price=  355.00 time=11-16 00:00
  [52] TROUGH price=  282.50 time=12-10 00:00
  [53] PEAK   price=  331.00 time=12-31 00:00
  [54] TROUGH price=  298.00 time=01-14 00:00
  [55] PEAK   price=  454.00 time=03-14 00:00
  [56] TROUGH price=  368.50 time=04-06 00:00
  [57] PEAK   price=  502.00 time=04-25 00:00
  [58] TROUGH price=  333.00 time=05-30 00:00
  [59] PEAK   price=  466.00 time=07-13 00:00 ← C
```

**失败详情:**
```
  ❌ 最新(771.50) > C(777.00) = False
```
---

### M — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2933.00 |
| B 价 | 3073.00 |
| C 价 | 2960.00 |
| 最新价 | 2918.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 56 | C 索引 | 58 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] PEAK   price= 2425.00 time=12-27 00:00
  [ 1] TROUGH price= 2309.00 time=12-30 00:00
  [ 2] PEAK   price= 2444.00 time=01-06 00:00
  [ 3] TROUGH price= 2235.00 time=01-18 00:00
  [ 4] PEAK   price= 2412.00 time=02-06 00:00
  [ 5] TROUGH price= 2272.00 time=02-08 00:00
  [ 6] PEAK   price= 2446.00 time=02-20 00:00
  [ 7] TROUGH price= 2318.00 time=02-27 00:00
  [ 8] PEAK   price= 2375.00 time=03-03 00:00
  [ 9] TROUGH price= 2249.00 time=03-17 00:00
  [10] PEAK   price= 2319.00 time=03-27 00:00
  [11] TROUGH price= 2080.00 time=04-18 00:00
  [12] PEAK   price= 2448.00 time=05-12 00:00
  [13] TROUGH price= 2252.00 time=06-01 00:00
  [14] PEAK   price= 2394.00 time=06-05 00:00
  [15] TROUGH price= 2266.00 time=06-27 00:00
  [16] PEAK   price= 2425.00 time=07-12 00:00
  [17] TROUGH price= 2205.00 time=08-14 00:00
  [18] PEAK   price= 2278.00 time=08-23 00:00
  [19] TROUGH price= 2222.00 time=08-29 00:00
  [20] PEAK   price= 2275.00 time=09-06 00:00
  [21] TROUGH price= 2198.00 time=09-13 00:00
  [22] PEAK   price= 2250.00 time=09-18 00:00
  [23] TROUGH price= 2202.00 time=09-27 00:00
  [24] PEAK   price= 2455.00 time=10-30 00:00
  [25] TROUGH price= 2419.00 time=11-14 00:00
  [26] PEAK   price= 2556.00 time=11-20 00:00
  [27] TROUGH price= 2279.00 time=12-07 00:00
  [28] PEAK   price= 2342.00 time=12-12 00:00
  [29] TROUGH price= 2268.00 time=12-19 00:00
  [30] PEAK   price= 2402.00 time=12-29 00:00
  [31] TROUGH price= 2305.00 time=01-10 00:00
  [32] PEAK   price= 2616.00 time=01-17 00:00
  [33] TROUGH price= 2545.00 time=01-30 00:00
  [34] PEAK   price= 2788.00 time=02-27 00:00
  [35] TROUGH price= 2636.00 time=03-16 00:00
  [36] PEAK   price= 2680.00 time=03-30 00:00
  [37] TROUGH price= 2431.00 time=04-19 00:00
  [38] PEAK   price= 2649.00 time=05-24 00:00
  [39] TROUGH price= 2474.00 time=06-13 00:00
  [40] PEAK   price= 2669.00 time=07-03 00:00
  [41] TROUGH price= 2553.00 time=07-10 00:00
  [42] PEAK   price= 2735.00 time=07-13 00:00
  [43] TROUGH price= 2541.00 time=07-26 00:00
  [44] PEAK   price= 3279.00 time=09-19 00:00
  [45] TROUGH price= 3061.00 time=10-09 00:00
  [46] PEAK   price= 3368.00 time=10-29 00:00
  [47] TROUGH price= 3258.00 time=11-05 00:00
  [48] PEAK   price= 3567.00 time=11-19 00:00
  [49] TROUGH price= 3087.00 time=12-04 00:00
  [50] PEAK   price= 3446.00 time=12-17 00:00
  [51] TROUGH price= 3257.00 time=12-21 00:00
  [52] PEAK   price= 3581.00 time=01-14 00:00
  [53] TROUGH price= 3168.00 time=01-24 00:00
  [54] PEAK   price= 3749.00 time=03-04 00:00
  [55] TROUGH price= 2983.00 time=04-02 00:00
  [56] PEAK   price= 3791.00 time=05-26 00:00 ← A
  [57] TROUGH price= 3570.00 time=06-03 00:00
  [58] PEAK   price= 4291.00 time=06-18 00:00 ← C
  [59] TROUGH price= 3818.00 time=06-24 00:00
```

**失败详情:**
```
  ❌ 最新(2918.00) > C(2960.00) = False
```
---

### NI — 1d

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 140160.00 |
| B 价 | 160500.00 |
| C 价 | 140500.00 |
| 最新价 | 135100.00 |
| DB 方向 | — (状态: —) |
| A 索引 | 1 | C 索引 | 59 |

**极值点序列** (swing: 60, merged: 60):
```
  [ 0] TROUGH price=92640.00 time=04-15 00:00
  [ 1] PEAK   price=115300.00 time=05-07 00:00 ← A
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
  [20] TROUGH price=64280.00 time=02-15 00:00
  [21] PEAK   price=69560.00 time=02-23 00:00
  [22] TROUGH price=66370.00 time=02-26 00:00
  [23] PEAK   price=75840.00 time=03-08 00:00
  [24] TROUGH price=67570.00 time=03-16 00:00
  [25] PEAK   price=70440.00 time=03-18 00:00
  [26] TROUGH price=65530.00 time=04-06 00:00
  [27] PEAK   price=76390.00 time=05-04 00:00
  [28] TROUGH price=66350.00 time=05-27 00:00
  [29] PEAK   price=84080.00 time=07-22 00:00
  [30] TROUGH price=78650.00 time=07-26 00:00
  [31] PEAK   price=85700.00 time=08-03 00:00
  [32] TROUGH price=77550.00 time=08-25 00:00
  [33] PEAK   price=81550.00 time=09-09 00:00
  [34] TROUGH price=77960.00 time=09-19 00:00
  [35] PEAK   price=83610.00 time=09-29 00:00
  [36] TROUGH price=79080.00 time=10-24 00:00
  [37] PEAK   price=99800.00 time=11-14 00:00
  [38] TROUGH price=88010.00 time=11-21 00:00
  [39] PEAK   price=99300.00 time=11-28 00:00
  [40] TROUGH price=90150.00 time=11-30 00:00
  [41] PEAK   price=97800.00 time=12-12 00:00
  [42] TROUGH price=83450.00 time=01-04 00:00
  [43] PEAK   price=88360.00 time=01-11 00:00
  [44] TROUGH price=81210.00 time=01-26 00:00
  [45] PEAK   price=92550.00 time=02-21 00:00
  [46] TROUGH price=87400.00 time=02-24 00:00
  [47] PEAK   price=91900.00 time=03-02 00:00
  [48] TROUGH price=79560.00 time=03-27 00:00
  [49] PEAK   price=86980.00 time=04-07 00:00
  [50] TROUGH price=74710.00 time=05-18 00:00
  [51] PEAK   price=78580.00 time=05-23 00:00
  [52] TROUGH price=71940.00 time=06-05 00:00
  [53] PEAK   price=74380.00 time=06-12 00:00
  [54] TROUGH price=71520.00 time=06-14 00:00
  [55] PEAK   price=77670.00 time=07-03 00:00
  [56] TROUGH price=73010.00 time=07-11 00:00
  [57] PEAK   price=97720.00 time=09-04 00:00
  [58] TROUGH price=82500.00 time=09-28 00:00
  [59] PEAK   price=97750.00 time=10-23 00:00 ← C
```

**失败详情:**
```
  ❌ 最新(135100.00) > C(140500.00) = False
```
---

### NI — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 128800.00 |
| B 价 | 155360.00 |
| C 价 | 140500.00 |
| 最新价 | 135100.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 77 | C 索引 | 79 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price=95470.00 time=03-27 00:00
  [ 1] PEAK   price=120000.00 time=05-29 00:00
  [ 2] TROUGH price=107790.00 time=07-17 00:00
  [ 3] PEAK   price=115150.00 time=08-07 00:00
  [ 4] TROUGH price=99920.00 time=09-11 00:00
  [ 5] PEAK   price=107120.00 time=10-09 00:00
  [ 6] TROUGH price=86080.00 time=01-02 00:00
  [ 7] PEAK   price=106780.00 time=03-05 00:00
  [ 8] TROUGH price=99100.00 time=03-26 00:00
  [ 9] PEAK   price=104240.00 time=04-02 00:00
  [10] TROUGH price=94670.00 time=05-07 00:00
  [11] PEAK   price=102830.00 time=05-21 00:00
  [12] TROUGH price=94280.00 time=06-04 00:00
  [13] PEAK   price=149190.00 time=09-03 00:00
  [14] TROUGH price=103360.00 time=12-03 00:00
  [15] PEAK   price=114200.00 time=12-24 00:00
  [16] TROUGH price=100670.00 time=02-03 00:00
  [17] PEAK   price=107050.00 time=02-11 00:00
  [18] TROUGH price=89550.00 time=03-31 00:00
  [19] PEAK   price=123930.00 time=09-01 00:00
  [20] TROUGH price=110620.00 time=09-22 00:00
  [21] PEAK   price=125670.00 time=10-27 00:00
  [22] TROUGH price=114020.00 time=11-03 00:00
  [23] PEAK   price=137280.00 time=01-19 00:00
  [24] TROUGH price=128840.00 time=02-02 00:00
  [25] PEAK   price=149350.00 time=02-18 00:00
  [26] TROUGH price=118000.00 time=03-16 00:00
  [27] PEAK   price=127750.00 time=04-06 00:00
  [28] TROUGH price=118750.00 time=04-20 00:00
  [29] PEAK   price=135570.00 time=05-06 00:00
  [30] TROUGH price=122570.00 time=05-18 00:00
  [31] PEAK   price=148780.00 time=07-27 00:00
  [32] TROUGH price=138020.00 time=08-10 00:00
  [33] PEAK   price=155140.00 time=09-07 00:00
  [34] TROUGH price=135700.00 time=09-28 00:00
  [35] PEAK   price=161600.00 time=10-19 00:00
  [36] TROUGH price=139630.00 time=11-02 00:00
  [37] PEAK   price=156480.00 time=11-23 00:00
  [38] TROUGH price=139930.00 time=12-14 00:00
  [39] PEAK   price=281250.00 time=03-22 00:00
  [40] TROUGH price=205500.00 time=04-12 00:00
  [41] PEAK   price=246000.00 time=04-19 00:00
  [42] TROUGH price=194360.00 time=05-10 00:00
  [43] PEAK   price=226500.00 time=06-07 00:00
  [44] TROUGH price=142500.00 time=07-12 00:00
  [45] PEAK   price=183990.00 time=07-26 00:00
  [46] TROUGH price=159000.00 time=08-30 00:00
  [47] PEAK   price=202800.00 time=09-20 00:00
  [48] TROUGH price=176000.00 time=10-11 00:00
  [49] PEAK   price=234870.00 time=01-03 00:00
  [50] TROUGH price=200130.00 time=01-10 00:00
  [51] PEAK   price=226700.00 time=01-31 00:00
  [52] TROUGH price=171350.00 time=03-14 00:00
  [53] PEAK   price=198880.00 time=04-18 00:00
  [54] TROUGH price=153050.00 time=05-30 00:00
  [55] PEAK   price=174340.00 time=06-13 00:00
  [56] TROUGH price=153700.00 time=06-27 00:00
  [57] PEAK   price=174220.00 time=07-25 00:00
  [58] TROUGH price=161230.00 time=08-15 00:00
  [59] PEAK   price=173980.00 time=09-05 00:00
  [60] TROUGH price=121880.00 time=11-21 00:00
  [61] PEAK   price=132350.00 time=01-23 00:00
  [62] TROUGH price=122000.00 time=01-30 00:00
  [63] PEAK   price=143100.00 time=03-12 00:00
  [64] TROUGH price=128600.00 time=03-26 00:00
  [65] PEAK   price=160500.00 time=05-21 00:00
  [66] TROUGH price=124030.00 time=07-23 00:00
  [67] PEAK   price=132960.00 time=08-27 00:00
  [68] TROUGH price=119300.00 time=09-10 00:00
  [69] PEAK   price=138800.00 time=10-08 00:00
  [70] TROUGH price=122110.00 time=11-12 00:00
  [71] PEAK   price=129980.00 time=12-10 00:00
  [72] TROUGH price=120400.00 time=12-31 00:00
  [73] PEAK   price=129460.00 time=01-14 00:00
  [74] TROUGH price=122610.00 time=02-05 00:00
  [75] PEAK   price=135960.00 time=03-11 00:00
  [76] TROUGH price=115450.00 time=04-01 00:00
  [77] PEAK   price=126850.00 time=04-22 00:00 ← A
  [78] TROUGH price=116670.00 time=06-17 00:00
  [79] PEAK   price=125370.00 time=07-22 00:00 ← C
```

**失败详情:**
```
  ❌ 最新(135100.00) > C(140500.00) = False
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
| A 索引 | 77 | C 索引 | 79 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] PEAK   price=19110.00 time=03-27 00:00
  [ 1] TROUGH price=18020.00 time=04-17 00:00
  [ 2] PEAK   price=20810.00 time=06-05 00:00
  [ 3] TROUGH price=17280.00 time=08-14 00:00
  [ 4] PEAK   price=19240.00 time=09-11 00:00
  [ 5] TROUGH price=17760.00 time=09-25 00:00
  [ 6] PEAK   price=19060.00 time=10-16 00:00
  [ 7] TROUGH price=17275.00 time=01-08 00:00
  [ 8] PEAK   price=17860.00 time=01-22 00:00
  [ 9] TROUGH price=16510.00 time=02-12 00:00
  [10] PEAK   price=17850.00 time=02-26 00:00
  [11] TROUGH price=15790.00 time=05-14 00:00
  [12] PEAK   price=16340.00 time=06-18 00:00
  [13] TROUGH price=15655.00 time=07-09 00:00
  [14] PEAK   price=17590.00 time=09-03 00:00
  [15] TROUGH price=16650.00 time=09-24 00:00
  [16] PEAK   price=15340.00 time=12-24 00:00
  [17] TROUGH price=14545.00 time=12-31 00:00
  [18] PEAK   price=15515.00 time=01-14 00:00
  [19] TROUGH price=13815.00 time=02-04 00:00
  [20] PEAK   price=15200.00 time=03-03 00:00
  [21] TROUGH price=12620.00 time=03-17 00:00
  [22] PEAK   price=14235.00 time=04-14 00:00
  [23] TROUGH price=13425.00 time=04-21 00:00
  [24] PEAK   price=16585.00 time=08-04 00:00
  [25] TROUGH price=14050.00 time=10-27 00:00
  [26] PEAK   price=15900.00 time=11-24 00:00
  [27] TROUGH price=14065.00 time=12-22 00:00
  [28] PEAK   price=16145.00 time=02-23 00:00
  [29] TROUGH price=14600.00 time=03-09 00:00
  [30] PEAK   price=15475.00 time=03-30 00:00
  [31] TROUGH price=14610.00 time=04-13 00:00
  [32] PEAK   price=15885.00 time=05-06 00:00
  [33] TROUGH price=14900.00 time=06-08 00:00
  [34] PEAK   price=16420.00 time=07-20 00:00
  [35] TROUGH price=14055.00 time=09-22 00:00
  [36] PEAK   price=16330.00 time=10-19 00:00
  [37] TROUGH price=14585.00 time=11-16 00:00
  [38] PEAK   price=15870.00 time=12-14 00:00
  [39] TROUGH price=15050.00 time=01-04 00:00
  [40] PEAK   price=15875.00 time=01-18 00:00
  [41] TROUGH price=14690.00 time=02-08 00:00
  [42] PEAK   price=16465.00 time=03-08 00:00
  [43] TROUGH price=14910.00 time=03-15 00:00
  [44] PEAK   price=15875.00 time=03-29 00:00
  [45] TROUGH price=15305.00 time=04-12 00:00
  [46] PEAK   price=15900.00 time=05-05 00:00
  [47] TROUGH price=14680.00 time=05-17 00:00
  [48] PEAK   price=15310.00 time=06-07 00:00
  [49] TROUGH price=14800.00 time=06-21 00:00
  [50] PEAK   price=15375.00 time=06-28 00:00
  [51] TROUGH price=14345.00 time=07-12 00:00
  [52] PEAK   price=15450.00 time=08-09 00:00
  [53] TROUGH price=14795.00 time=08-30 00:00
  [54] PEAK   price=15195.00 time=09-13 00:00
  [55] TROUGH price=14820.00 time=09-27 00:00
  [56] PEAK   price=15510.00 time=10-18 00:00
  [57] TROUGH price=15055.00 time=10-25 00:00
  [58] PEAK   price=16045.00 time=11-29 00:00
  [59] TROUGH price=15410.00 time=12-13 00:00
  [60] PEAK   price=16205.00 time=12-27 00:00
  [61] TROUGH price=15080.00 time=02-14 00:00
  [62] PEAK   price=15500.00 time=02-21 00:00
  [63] TROUGH price=15120.00 time=03-07 00:00
  [64] PEAK   price=15450.00 time=03-14 00:00
  [65] TROUGH price=15015.00 time=05-30 00:00
  [66] PEAK   price=17540.00 time=08-29 00:00
  [67] TROUGH price=16080.00 time=10-10 00:00
  [68] PEAK   price=17195.00 time=11-14 00:00
  [69] TROUGH price=15405.00 time=12-05 00:00
  [70] PEAK   price=16730.00 time=01-23 00:00
  [71] TROUGH price=15790.00 time=02-20 00:00
  [72] PEAK   price=19175.00 time=05-21 00:00
  [73] TROUGH price=18415.00 time=06-11 00:00
  [74] PEAK   price=20050.00 time=07-16 00:00
  [75] TROUGH price=16245.00 time=09-18 00:00
  [76] PEAK   price=17100.00 time=10-08 00:00
  [77] TROUGH price=16450.00 time=10-15 00:00 ← A
  [78] PEAK   price=17910.00 time=12-03 00:00
  [79] TROUGH price=16305.00 time=01-07 00:00 ← C
```

**失败详情:**
```
  ❌ 最新(16130.00) > C(16400.00) = False
```
---

### PS — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 34375.00 |
| B 价 | 39340.00 |
| C 价 | 36020.00 |
| 最新价 | 35840.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 3 | C 索引 | 17 |

**极值点序列** (swing: 19, merged: 19):
```
  [ 0] PEAK   price=45190.00 time=01-14 00:00
  [ 1] TROUGH price=42820.00 time=02-05 00:00
  [ 2] PEAK   price=44795.00 time=02-25 00:00
  [ 3] TROUGH price=34375.00 time=05-06 00:00 ← A
  [ 4] PEAK   price=39340.00 time=05-13 00:00
  [ 5] TROUGH price=30400.00 time=06-24 00:00
  [ 6] PEAK   price=55605.00 time=07-22 00:00
  [ 7] TROUGH price=48220.00 time=08-26 00:00
  [ 8] PEAK   price=56790.00 time=09-09 00:00
  [ 9] TROUGH price=47720.00 time=10-09 00:00
  [10] PEAK   price=56655.00 time=10-28 00:00
  [11] TROUGH price=51150.00 time=11-11 00:00
  [12] PEAK   price=59200.00 time=11-25 00:00
  [13] TROUGH price=52625.00 time=12-09 00:00
  [14] PEAK   price=61985.00 time=12-16 00:00
  [15] TROUGH price=31070.00 time=04-07 00:00
  [16] PEAK   price=46345.00 time=04-21 00:00
  [17] TROUGH price=36020.00 time=05-12 00:00 ← C
  [18] PEAK   price=39030.00 time=06-09 00:00
```

**失败详情:**
```
  ❌ 最新(35840.00) > C(36020.00) = False
```
---

### RM — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 2299.00 |
| B 价 | 2430.00 |
| C 价 | 2309.00 |
| 最新价 | 2239.00 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 73 | C 索引 | 79 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price= 2457.00 time=03-20 00:00
  [ 1] PEAK   price= 2734.00 time=04-03 00:00
  [ 2] TROUGH price= 2404.00 time=05-15 00:00
  [ 3] PEAK   price= 2564.00 time=05-29 00:00
  [ 4] TROUGH price= 2343.00 time=06-05 00:00
  [ 5] PEAK   price= 2604.00 time=06-26 00:00
  [ 6] TROUGH price= 2427.00 time=07-31 00:00
  [ 7] PEAK   price= 2575.00 time=08-07 00:00
  [ 8] TROUGH price= 2311.00 time=09-18 00:00
  [ 9] PEAK   price= 2642.00 time=10-09 00:00
  [10] TROUGH price= 2079.00 time=12-25 00:00
  [11] PEAK   price= 2197.00 time=01-02 00:00
  [12] TROUGH price= 2071.00 time=01-15 00:00
  [13] PEAK   price= 2216.00 time=02-12 00:00
  [14] TROUGH price= 2062.00 time=02-26 00:00
  [15] PEAK   price= 2254.00 time=03-05 00:00
  [16] TROUGH price= 2161.00 time=04-30 00:00
  [17] PEAK   price= 2629.00 time=06-04 00:00
  [18] TROUGH price= 2427.00 time=06-11 00:00
  [19] PEAK   price= 2624.00 time=06-25 00:00
  [20] TROUGH price= 2347.00 time=07-23 00:00
  [21] PEAK   price= 2545.00 time=08-13 00:00
  [22] TROUGH price= 2231.00 time=09-10 00:00
  [23] PEAK   price= 2429.00 time=10-22 00:00
  [24] TROUGH price= 2143.00 time=11-12 00:00
  [25] PEAK   price= 2354.00 time=01-07 00:00
  [26] TROUGH price= 2086.00 time=02-03 00:00
  [27] PEAK   price= 2581.00 time=03-24 00:00
  [28] TROUGH price= 2297.00 time=04-21 00:00
  [29] PEAK   price= 2415.00 time=04-28 00:00
  [30] TROUGH price= 2283.00 time=05-12 00:00
  [31] PEAK   price= 2413.00 time=06-02 00:00
  [32] TROUGH price= 2301.00 time=06-23 00:00
  [33] PEAK   price= 2527.00 time=07-21 00:00
  [34] TROUGH price= 2256.00 time=08-18 00:00
  [35] PEAK   price= 2498.00 time=09-08 00:00
  [36] TROUGH price= 2312.00 time=09-29 00:00
  [37] PEAK   price= 2607.00 time=11-17 00:00
  [38] TROUGH price= 2438.00 time=12-01 00:00
  [39] PEAK   price= 3166.00 time=01-12 00:00
  [40] TROUGH price= 2763.00 time=02-02 00:00
  [41] PEAK   price= 3088.00 time=02-23 00:00
  [42] TROUGH price= 2677.00 time=03-09 00:00
  [43] PEAK   price= 3218.00 time=05-06 00:00
  [44] TROUGH price= 2873.00 time=05-18 00:00
  [45] PEAK   price= 3091.00 time=06-08 00:00
  [46] TROUGH price= 2745.00 time=06-15 00:00
  [47] PEAK   price= 3162.00 time=07-13 00:00
  [48] TROUGH price= 2871.00 time=07-20 00:00
  [49] PEAK   price= 3041.00 time=08-10 00:00
  [50] TROUGH price= 2774.00 time=09-07 00:00
  [51] PEAK   price= 2965.00 time=09-14 00:00
  [52] TROUGH price= 2476.00 time=11-02 00:00
  [53] PEAK   price= 2798.00 time=11-16 00:00
  [54] TROUGH price= 2625.00 time=11-30 00:00
  [55] PEAK   price= 2998.00 time=12-14 00:00
  [56] TROUGH price= 2832.00 time=01-18 00:00
  [57] PEAK   price= 4310.00 time=03-22 00:00
  [58] TROUGH price= 3623.00 time=03-29 00:00
  [59] PEAK   price= 3881.00 time=04-19 00:00
  [60] TROUGH price= 3487.00 time=05-10 00:00
  [61] PEAK   price= 3895.00 time=06-07 00:00
  [62] TROUGH price= 2596.00 time=07-05 00:00
  [63] PEAK   price= 3270.00 time=09-27 00:00
  [64] TROUGH price= 2905.00 time=10-25 00:00
  [65] PEAK   price= 3238.00 time=11-08 00:00
  [66] TROUGH price= 2948.00 time=11-15 00:00
  [67] PEAK   price= 3194.00 time=12-06 00:00
  [68] TROUGH price= 2953.00 time=12-13 00:00
  [69] PEAK   price= 3291.00 time=01-17 00:00
  [70] TROUGH price= 2733.00 time=03-21 00:00
  [71] PEAK   price= 3119.00 time=05-23 00:00
  [72] TROUGH price= 2877.00 time=05-30 00:00
  [73] PEAK   price= 3846.00 time=07-18 00:00 ← A
  [74] TROUGH price= 3539.00 time=07-25 00:00
  [75] PEAK   price= 3983.00 time=08-15 00:00
  [76] TROUGH price= 2834.00 time=10-31 00:00
  [77] PEAK   price= 3105.00 time=11-07 00:00
  [78] TROUGH price= 2727.00 time=11-28 00:00
  [79] PEAK   price= 2957.00 time=12-26 00:00 ← C
```

**失败详情:**
```
  ❌ 最新(2239.00) > C(2309.00) = False
```
---

### SA — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 1146.00 |
| B 价 | 1330.00 |
| C 价 | 1175.00 |
| 最新价 | 1152.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 63 | C 索引 | 67 |

**极值点序列** (swing: 69, merged: 69):
```
  [ 0] PEAK   price= 1691.00 time=01-14 00:00
  [ 1] TROUGH price= 1509.00 time=02-03 00:00
  [ 2] PEAK   price= 1637.00 time=02-25 00:00
  [ 3] TROUGH price= 1322.00 time=04-14 00:00
  [ 4] PEAK   price= 1490.00 time=06-02 00:00
  [ 5] TROUGH price= 1288.00 time=07-21 00:00
  [ 6] PEAK   price= 1822.00 time=09-01 00:00
  [ 7] TROUGH price= 1655.00 time=09-15 00:00
  [ 8] PEAK   price= 1749.00 time=10-13 00:00
  [ 9] TROUGH price= 1317.00 time=12-08 00:00
  [10] PEAK   price= 1682.00 time=12-22 00:00
  [11] TROUGH price= 1489.00 time=01-12 00:00
  [12] PEAK   price= 2010.00 time=03-16 00:00
  [13] TROUGH price= 1818.00 time=04-06 00:00
  [14] PEAK   price= 2329.00 time=05-11 00:00
  [15] TROUGH price= 2028.00 time=05-18 00:00
  [16] PEAK   price= 2320.00 time=06-01 00:00
  [17] TROUGH price= 2130.00 time=06-15 00:00
  [18] PEAK   price= 3648.00 time=10-12 00:00
  [19] TROUGH price= 2160.00 time=01-04 00:00
  [20] PEAK   price= 3177.00 time=02-08 00:00
  [21] TROUGH price= 2396.00 time=03-15 00:00
  [22] PEAK   price= 3269.00 time=04-19 00:00
  [23] TROUGH price= 2700.00 time=05-10 00:00
  [24] PEAK   price= 3165.00 time=06-07 00:00
  [25] TROUGH price= 2402.00 time=07-12 00:00
  [26] PEAK   price= 2678.00 time=07-26 00:00
  [27] TROUGH price= 2223.00 time=08-16 00:00
  [28] PEAK   price= 2443.00 time=08-23 00:00
  [29] TROUGH price= 2244.00 time=09-06 00:00
  [30] PEAK   price= 2558.00 time=10-10 00:00
  [31] TROUGH price= 2282.00 time=10-25 00:00
  [32] PEAK   price= 3069.00 time=01-30 00:00
  [33] TROUGH price= 2845.00 time=02-07 00:00
  [34] PEAK   price= 2994.00 time=02-21 00:00
  [35] TROUGH price= 1550.00 time=05-23 00:00
  [36] PEAK   price= 2207.00 time=07-25 00:00
  [37] TROUGH price= 1508.00 time=08-08 00:00
  [38] PEAK   price= 2074.00 time=08-29 00:00
  [39] TROUGH price= 1652.00 time=10-24 00:00
  [40] PEAK   price= 2666.00 time=11-28 00:00
  [41] TROUGH price= 1808.00 time=01-09 00:00
  [42] PEAK   price= 2166.00 time=01-23 00:00
  [43] TROUGH price= 1751.00 time=02-27 00:00
  [44] PEAK   price= 1969.00 time=03-05 00:00
  [45] TROUGH price= 1727.00 time=03-26 00:00
  [46] PEAK   price= 2320.00 time=04-23 00:00
  [47] TROUGH price= 2091.00 time=05-14 00:00
  [48] PEAK   price= 2471.00 time=05-21 00:00
  [49] TROUGH price= 1317.00 time=09-18 00:00
  [50] PEAK   price= 1754.00 time=10-08 00:00
  [51] TROUGH price= 1393.00 time=12-03 00:00
  [52] PEAK   price= 1530.00 time=12-10 00:00
  [53] TROUGH price= 1379.00 time=01-07 00:00
  [54] PEAK   price= 1585.00 time=02-25 00:00
  [55] TROUGH price= 1266.00 time=04-08 00:00
  [56] PEAK   price= 1392.00 time=04-22 00:00
  [57] TROUGH price= 1147.00 time=06-24 00:00
  [58] PEAK   price= 1457.00 time=07-22 00:00
  [59] TROUGH price= 1252.00 time=09-09 00:00
  [60] PEAK   price= 1352.00 time=09-16 00:00
  [61] TROUGH price= 1088.00 time=12-09 00:00
  [62] PEAK   price= 1277.00 time=01-06 00:00
  [63] TROUGH price= 1146.00 time=02-24 00:00 ← A
  [64] PEAK   price= 1330.00 time=03-03 00:00
  [65] TROUGH price= 1123.00 time=04-07 00:00
  [66] PEAK   price= 1274.00 time=05-06 00:00
  [67] TROUGH price= 1175.00 time=05-19 00:00 ← C
  [68] PEAK   price= 1234.00 time=05-26 00:00
```

**失败详情:**
```
  ❌ 最新(1152.00) > C(1175.00) = False
```
---

### SC — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 431.80 |
| B 价 | 838.40 |
| C 价 | 592.00 |
| 最新价 | 572.20 |
| DB 方向 | LONG (状态: LEG3) |
| A 索引 | 74 | C 索引 | 78 |

**极值点序列** (swing: 80, merged: 80):
```
  [ 0] TROUGH price=  397.70 time=04-03 00:00
  [ 1] PEAK   price=  493.80 time=05-22 00:00
  [ 2] TROUGH price=  453.70 time=06-19 00:00
  [ 3] PEAK   price=  511.50 time=07-10 00:00
  [ 4] TROUGH price=  478.50 time=07-17 00:00
  [ 5] PEAK   price=  550.00 time=08-07 00:00
  [ 6] TROUGH price=  480.00 time=08-14 00:00
  [ 7] PEAK   price=  598.50 time=10-09 00:00
  [ 8] TROUGH price=  351.60 time=12-25 00:00
  [ 9] PEAK   price=  442.20 time=01-22 00:00
  [10] TROUGH price=  413.00 time=01-29 00:00
  [11] PEAK   price=  467.90 time=02-12 00:00
  [12] TROUGH price=  426.20 time=03-05 00:00
  [13] PEAK   price=  521.50 time=05-14 00:00
  [14] TROUGH price=  406.00 time=06-18 00:00
  [15] PEAK   price=  462.20 time=07-09 00:00
  [16] TROUGH price=  399.60 time=08-06 00:00
  [17] PEAK   price=  496.00 time=09-17 00:00
  [18] TROUGH price=  431.50 time=10-08 00:00
  [19] PEAK   price=  529.80 time=01-07 00:00
  [20] TROUGH price=  381.40 time=02-04 00:00
  [21] PEAK   price=  422.00 time=02-18 00:00
  [22] TROUGH price=  213.20 time=03-17 00:00
  [23] PEAK   price=  304.90 time=04-07 00:00
  [24] TROUGH price=  205.10 time=04-28 00:00
  [25] PEAK   price=  305.70 time=07-21 00:00
  [26] TROUGH price=  277.10 time=08-04 00:00
  [27] PEAK   price=  299.90 time=08-25 00:00
  [28] TROUGH price=  242.70 time=09-08 00:00
  [29] PEAK   price=  277.30 time=10-13 00:00
  [30] TROUGH price=  215.00 time=10-27 00:00
  [31] PEAK   price=  444.60 time=03-02 00:00
  [32] TROUGH price=  372.70 time=03-23 00:00
  [33] PEAK   price=  479.00 time=07-06 00:00
  [34] TROUGH price=  395.20 time=08-17 00:00
  [35] PEAK   price=  546.50 time=10-12 00:00
  [36] TROUGH price=  417.50 time=11-30 00:00
  [37] PEAK   price=  823.60 time=03-08 00:00
  [38] TROUGH price=  602.40 time=04-06 00:00
  [39] PEAK   price=  787.20 time=06-14 00:00
  [40] TROUGH price=  621.00 time=07-12 00:00
  [41] PEAK   price=  752.40 time=08-23 00:00
  [42] TROUGH price=  602.30 time=09-27 00:00
  [43] PEAK   price=  709.50 time=10-11 00:00
  [44] TROUGH price=  655.70 time=10-18 00:00
  [45] PEAK   price=  722.50 time=11-01 00:00
  [46] TROUGH price=  495.00 time=12-06 00:00
  [47] PEAK   price=  571.60 time=12-27 00:00
  [48] TROUGH price=  513.80 time=02-07 00:00
  [49] PEAK   price=  589.70 time=03-07 00:00
  [50] TROUGH price=  480.60 time=03-14 00:00
  [51] PEAK   price=  606.50 time=04-11 00:00
  [52] TROUGH price=  485.30 time=05-04 00:00
  [53] PEAK   price=  758.00 time=09-12 00:00
  [54] TROUGH price=  643.90 time=10-10 00:00
  [55] PEAK   price=  700.70 time=10-17 00:00
  [56] TROUGH price=  519.70 time=12-12 00:00
  [57] PEAK   price=  599.50 time=01-23 00:00
  [58] TROUGH price=  551.40 time=02-06 00:00
  [59] PEAK   price=  682.80 time=04-09 00:00
  [60] TROUGH price=  566.50 time=06-04 00:00
  [61] PEAK   price=  641.10 time=07-02 00:00
  [62] TROUGH price=  492.20 time=09-10 00:00
  [63] PEAK   price=  587.50 time=10-08 00:00
  [64] TROUGH price=  510.60 time=10-29 00:00
  [65] PEAK   price=  639.50 time=01-14 00:00
  [66] TROUGH price=  502.30 time=03-04 00:00
  [67] PEAK   price=  558.50 time=04-01 00:00
  [68] TROUGH price=  444.00 time=04-08 00:00
  [69] PEAK   price=  506.00 time=04-22 00:00
  [70] TROUGH price=  447.50 time=05-27 00:00
  [71] PEAK   price=  588.60 time=06-17 00:00
  [72] TROUGH price=  468.80 time=09-02 00:00
  [73] PEAK   price=  502.50 time=09-16 00:00
  [74] TROUGH price=  431.80 time=10-21 00:00 ← A
  [75] PEAK   price=  472.20 time=11-11 00:00
  [76] TROUGH price=  411.00 time=01-06 00:00
  [77] PEAK   price=  838.40 time=03-17 00:00
  [78] TROUGH price=  592.00 time=04-14 00:00 ← C
  [79] PEAK   price=  695.70 time=04-28 00:00
```

**失败详情:**
```
  ❌ 最新(572.20) > C(592.00) = False
```
---

### SS — 1w

| 指标 | 值 |
|------|-----|
| 算法方向 | LONG |
| A 价 | 13705.00 |
| B 价 | 15835.00 |
| C 价 | 14600.00 |
| 最新价 | 14385.00 |
| DB 方向 | SHORT (状态: LEG3) |
| A 索引 | 74 | C 索引 | 76 |

**极值点序列** (swing: 78, merged: 78):
```
  [ 0] TROUGH price=13765.00 time=12-03 00:00
  [ 1] PEAK   price=14860.00 time=12-31 00:00
  [ 2] TROUGH price=12920.00 time=02-03 00:00
  [ 3] PEAK   price=13650.00 time=02-11 00:00
  [ 4] TROUGH price=11680.00 time=03-17 00:00
  [ 5] PEAK   price=13730.00 time=05-06 00:00
  [ 6] TROUGH price=12570.00 time=06-09 00:00
  [ 7] PEAK   price=15470.00 time=09-01 00:00
  [ 8] TROUGH price=13805.00 time=09-22 00:00
  [ 9] PEAK   price=14925.00 time=10-27 00:00
  [10] TROUGH price=12860.00 time=11-17 00:00
  [11] PEAK   price=14365.00 time=12-08 00:00
  [12] TROUGH price=13090.00 time=12-22 00:00
  [13] PEAK   price=15045.00 time=01-05 00:00
  [14] TROUGH price=13870.00 time=02-02 00:00
  [15] PEAK   price=15680.00 time=02-18 00:00
  [16] TROUGH price=13675.00 time=03-02 00:00
  [17] PEAK   price=14735.00 time=03-30 00:00
  [18] TROUGH price=13765.00 time=04-13 00:00
  [19] PEAK   price=15890.00 time=05-11 00:00
  [20] TROUGH price=14780.00 time=05-25 00:00
  [21] PEAK   price=20180.00 time=07-27 00:00
  [22] TROUGH price=17310.00 time=08-24 00:00
  [23] PEAK   price=22425.00 time=09-22 00:00
  [24] TROUGH price=15480.00 time=12-07 00:00
  [25] PEAK   price=19065.00 time=01-18 00:00
  [26] TROUGH price=16920.00 time=01-25 00:00
  [27] PEAK   price=24785.00 time=03-08 00:00
  [28] TROUGH price=15105.00 time=08-16 00:00
  [29] PEAK   price=17670.00 time=09-13 00:00
  [30] TROUGH price=16215.00 time=10-11 00:00
  [31] PEAK   price=17880.00 time=10-18 00:00
  [32] TROUGH price=16265.00 time=11-08 00:00
  [33] PEAK   price=17835.00 time=12-13 00:00
  [34] TROUGH price=16210.00 time=12-20 00:00
  [35] PEAK   price=17470.00 time=01-30 00:00
  [36] TROUGH price=16305.00 time=02-07 00:00
  [37] PEAK   price=17045.00 time=02-21 00:00
  [38] TROUGH price=14405.00 time=04-04 00:00
  [39] PEAK   price=15700.00 time=05-09 00:00
  [40] TROUGH price=14430.00 time=05-23 00:00
  [41] PEAK   price=15400.00 time=06-13 00:00
  [42] TROUGH price=14560.00 time=06-27 00:00
  [43] PEAK   price=16200.00 time=08-22 00:00
  [44] TROUGH price=13010.00 time=12-05 00:00
  [45] PEAK   price=14185.00 time=12-19 00:00
  [46] TROUGH price=13505.00 time=01-09 00:00
  [47] PEAK   price=14430.00 time=01-23 00:00
  [48] TROUGH price=13450.00 time=02-06 00:00
  [49] PEAK   price=14210.00 time=02-27 00:00
  [50] TROUGH price=13150.00 time=03-26 00:00
  [51] PEAK   price=14645.00 time=04-16 00:00
  [52] TROUGH price=14005.00 time=05-14 00:00
  [53] PEAK   price=14955.00 time=05-28 00:00
  [54] TROUGH price=13735.00 time=06-18 00:00
  [55] PEAK   price=14325.00 time=07-02 00:00
  [56] TROUGH price=13670.00 time=07-16 00:00
  [57] PEAK   price=14170.00 time=07-30 00:00
  [58] TROUGH price=13495.00 time=08-13 00:00
  [59] PEAK   price=13930.00 time=08-27 00:00
  [60] TROUGH price=13060.00 time=09-10 00:00
  [61] PEAK   price=14315.00 time=10-08 00:00
  [62] TROUGH price=12760.00 time=12-31 00:00
  [63] PEAK   price=13690.00 time=03-11 00:00
  [64] TROUGH price=12530.00 time=04-08 00:00
  [65] PEAK   price=13120.00 time=05-13 00:00
  [66] TROUGH price=12315.00 time=06-24 00:00
  [67] PEAK   price=13280.00 time=08-05 00:00
  [68] TROUGH price=12700.00 time=08-19 00:00
  [69] PEAK   price=13140.00 time=09-16 00:00
  [70] TROUGH price=12255.00 time=11-18 00:00
  [71] PEAK   price=14955.00 time=01-20 00:00
  [72] TROUGH price=13420.00 time=01-27 00:00
  [73] PEAK   price=14410.00 time=02-24 00:00
  [74] TROUGH price=13705.00 time=03-17 00:00 ← A
  [75] PEAK   price=15835.00 time=05-06 00:00
  [76] TROUGH price=14600.00 time=05-19 00:00 ← C
  [77] PEAK   price=15175.00 time=06-02 00:00
```

**失败详情:**
```
  ❌ 最新(14385.00) > C(14600.00) = False
```
---

## 📋 完整验证矩阵

| 品种 | 周期 | 方向 | A价 | B价 | C价 | 最新价 | 条件 | 判定 | DB方向 |
|------|------|------|------|------|------|--------|------|------|--------|
| A    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| A    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| A    | 1d  | SHORT |  5046.00 |  4694.00 |  4901.00 |  4739.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| A    | 1w  | LONG  |  4494.00 |  4634.00 |  4550.00 |  4739.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| AG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AG   | 1d  | SHORT | 20559.00 | 17554.00 | 19288.00 | 15622.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| AG   | 1w  | LONG  | 11001.00 | 32382.00 | 15070.00 | 15622.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| AL   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AL   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AL   | 1d  | SHORT | 25075.00 | 23660.00 | 24840.00 | 23905.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| AL   | 1w  | SHORT | 26185.00 | 23100.00 | 25675.00 | 23905.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| AO   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AO   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AO   | 1d  | LONG  |  2685.00 |  2913.00 |  2742.00 |  2898.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| AO   | 1w  | LONG  |  2730.00 |  3136.00 |  2742.00 |  2898.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| AP   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AP   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AP   | 1d  | SHORT |  9298.00 |  7505.00 |  7715.00 |  7400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| AP   | 1w  | SHORT |  8140.00 |  7478.00 |  7799.00 |  7400.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| AU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| AU   | 1d  | SHORT |  1074.44 |   996.12 |  1046.36 |   919.32 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| AU   | 1w  | SHORT |  1258.72 |   929.10 |  1074.44 |   919.32 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| B    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| B    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| B    | 1d  | SHORT |  3613.00 |  3455.00 |  3611.00 |  3482.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| B    | 1w  | SHORT |  3994.00 |  3558.00 |  3711.00 |  3482.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| BR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| BR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| BR   | 1d  | SHORT | 18565.00 | 15115.00 | 16680.00 | 12845.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| BR   | 1w  | SHORT | 18565.00 | 15115.00 | 16680.00 | 12845.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| BU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| BU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| BU   | 1d  | LONG  |  3530.00 |  4747.00 |  3950.00 |  4417.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| BU   | 1w  | LONG  |  3598.00 |  4747.00 |  3950.00 |  4417.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| C    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| C    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| C    | 1d  | LONG  |  2317.00 |  2479.00 |  2337.00 |  2335.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| C    | 1w  | LONG  |  2258.00 |  2443.00 |  2337.00 |  2335.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| CF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CF   | 1d  | SHORT | 16955.00 | 15855.00 | 16440.00 | 15675.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| CF   | 1w  | LONG  | 15035.00 | 16955.00 | 15855.00 | 15675.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| CJ   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CJ   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CJ   | 1d  | LONG  |  8720.00 |  9265.00 |  8880.00 |  8880.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| CJ   | 1w  | LONG  |  8720.00 |  9265.00 |  8880.00 |  8880.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| CS   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CS   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CS   | 1d  | LONG  |  2705.00 |  2827.00 |  2727.00 |  2714.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| CS   | 1w  | LONG  |  2616.00 |  2692.00 |  2641.00 |  2714.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| CU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| CU   | 1d  | SHORT | 108900.00 | 103000.00 | 107420.00 | 104110.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| CU   | 1w  | LONG  | 77700.00 | 114160.00 | 91500.00 | 104110.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| EB   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| EB   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| EB   | 1d  | SHORT | 11132.00 |  9300.00 | 10098.00 |  8476.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| EB   | 1w  | LONG  |  8007.00 | 11132.00 |  9300.00 |  8476.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| EG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| EG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| EG   | 1d  | SHORT |  5626.00 |  4763.00 |  5211.00 |  4544.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| EG   | 1w  | SHORT |  5814.00 |  4613.00 |  5211.00 |  4544.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| FG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| FG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| FG   | 1d  | SHORT |  1163.00 |   954.00 |  1104.00 |   989.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| FG   | 1w  | SHORT |  1163.00 |   954.00 |  1104.00 |   989.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| HC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| HC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| HC   | 1d  | LONG  |  3282.00 |  3417.00 |  3351.00 |  3380.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| HC   | 1w  | LONG  |  3194.00 |  3348.00 |  3261.00 |  3380.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| I    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| I    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| I    | 1d  | LONG  |   760.00 |   820.00 |   777.00 |   771.50 | ✅ ✅ ✅ ❌ | ❌ | —     |
| I    | 1w  | LONG  |   748.00 |   831.50 |   748.50 |   771.50 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IF   | 1d  | SHORT |  4995.00 |  4735.00 |  4964.60 |  4862.80 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IF   | 1w  | SHORT |  4995.00 |  4735.00 |  4964.60 |  4862.80 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IH   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IH   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IH   | 1d  | LONG  |  2750.80 |  3041.80 |  2791.20 |  2899.80 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IH   | 1w  | SHORT |  3041.80 |  2791.20 |  2950.80 |  2899.80 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| IM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| IM   | 1d  | LONG  |  7120.20 |  8337.00 |  8056.00 |  8510.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| IM   | 1w  | LONG  |  7008.80 |  7409.60 |  7120.20 |  8510.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| J    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| J    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| J    | 1d  | LONG  |  1717.00 |  1843.50 |  1792.50 |  1983.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| J    | 1w  | LONG  |  1717.00 |  1843.50 |  1719.00 |  1983.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| JD   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| JD   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| JD   | 1d  | LONG  |  2885.00 |  3517.00 |  3356.00 |  4748.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| JD   | 1w  | LONG  |  2771.00 |  3420.00 |  2873.00 |  4748.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| JM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| JM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| JM   | 1d  | LONG  |  1122.00 |  1212.00 |  1152.50 |  1363.50 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| JM   | 1w  | LONG  |  1116.00 |  1318.00 |  1152.50 |  1363.50 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| L    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| L    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| L    | 1d  | SHORT |  9523.00 |  8340.00 |  9407.00 |  7875.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| L    | 1w  | SHORT |  9523.00 |  7840.00 |  8521.00 |  7875.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| LC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LC   | 1d  | LONG  | 145000.00 | 175050.00 | 152500.00 | 167400.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| LC   | 1w  | LONG  | 145000.00 | 175050.00 | 157180.00 | 167400.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| LH   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LH   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LH   | 1d  | LONG  |  9000.00 | 11585.00 | 10625.00 | 11950.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| LH   | 1w  | LONG  |  9000.00 | 11585.00 | 10625.00 | 11950.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| LU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| LU   | 1d  | SHORT |  5303.00 |  4515.00 |  4974.00 |  3954.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| LU   | 1w  | SHORT |  5350.00 |  4538.00 |  4974.00 |  3954.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| M    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| M    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| M    | 1d  | LONG  |  2933.00 |  3073.00 |  2960.00 |  2918.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| M    | 1w  | SHORT |  3087.00 |  2921.00 |  3073.00 |  2918.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| MA   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| MA   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| MA   | 1d  | SHORT |  3603.00 |  2751.00 |  3063.00 |  2972.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| MA   | 1w  | SHORT |  3063.00 |  2756.00 |  3049.00 |  2972.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| NI   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| NI   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| NI   | 1d  | LONG  | 140160.00 | 160500.00 | 140500.00 | 135100.00 | ✅ ✅ ✅ ❌ | ❌ | —     |
| NI   | 1w  | LONG  | 128800.00 | 155360.00 | 140500.00 | 135100.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| NR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| NR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| NR   | 1d  | LONG  | 14210.00 | 14975.00 | 14490.00 | 14945.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| NR   | 1w  | LONG  | 14210.00 | 14975.00 | 14490.00 | 14945.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| OI   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| OI   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| OI   | 1d  | LONG  |  9122.00 | 10030.00 |  9496.00 |  9883.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| OI   | 1w  | LONG  |  9299.00 | 10017.00 |  9496.00 |  9883.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| P    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| P    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| P    | 1d  | SHORT |  9858.00 |  9332.00 |  9825.00 |  9316.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| P    | 1w  | SHORT | 10168.00 |  9200.00 |  9993.00 |  9316.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PB   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PB   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PB   | 1d  | SHORT | 16885.00 | 16510.00 | 16820.00 | 16130.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PB   | 1w  | LONG  | 16195.00 | 17005.00 | 16400.00 | 16130.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| PF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PF   | 1d  | SHORT |  8832.00 |  7802.00 |  8656.00 |  7348.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PF   | 1w  | SHORT |  8832.00 |  7558.00 |  8546.00 |  7348.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PG   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PG   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PG   | 1d  | LONG  |  4203.00 |  7407.00 |  5185.00 |  5548.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| PG   | 1w  | LONG  |  3985.00 |  7407.00 |  5185.00 |  5548.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| PK   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PK   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PK   | 1d  | LONG  |  7992.00 |  8480.00 |  8100.00 |  8344.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| PK   | 1w  | LONG  |  7854.00 |  8480.00 |  8100.00 |  8344.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| PP   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PP   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PP   | 1d  | LONG  |  6890.00 |  9980.00 |  8116.00 |  8649.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| PP   | 1w  | SHORT |  9088.00 |  8337.00 |  9008.00 |  8649.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PR   | 1d  | SHORT |  9018.00 |  7606.00 |  8074.00 |  7088.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PR   | 1w  | SHORT |  9282.00 |  7690.00 |  9018.00 |  7088.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PS   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PS   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PS   | 1d  | SHORT | 46345.00 | 37690.00 | 41750.00 | 35840.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PS   | 1w  | LONG  | 34375.00 | 39340.00 | 36020.00 | 35840.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| PX   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PX   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| PX   | 1d  | SHORT | 10600.00 |  8766.00 |  9742.00 |  8786.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| PX   | 1w  | SHORT | 10600.00 |  8766.00 |  9742.00 |  8786.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| RB   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RB   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RB   | 1d  | LONG  |  3005.00 |  3167.00 |  3083.00 |  3180.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| RB   | 1w  | LONG  |  3005.00 |  3167.00 |  3083.00 |  3180.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| RM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RM   | 1d  | SHORT |  2634.00 |  2212.00 |  2437.00 |  2239.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| RM   | 1w  | LONG  |  2299.00 |  2430.00 |  2309.00 |  2239.00 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| RR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RR   | 1d  | SHORT |  3634.00 |  3536.00 |  3618.00 |  3603.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| RR   | 1w  | SHORT |  3668.00 |  3541.00 |  3618.00 |  3603.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| RU   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RU   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| RU   | 1d  | LONG  | 15885.00 | 17325.00 | 16480.00 | 17330.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| RU   | 1w  | LONG  | 14910.00 | 17600.00 | 15885.00 | 17330.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| SA   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SA   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SA   | 1d  | SHORT |  1274.00 |  1175.00 |  1234.00 |  1152.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SA   | 1w  | LONG  |  1146.00 |  1330.00 |  1175.00 |  1152.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| SC   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SC   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SC   | 1d  | SHORT |   691.40 |   575.30 |   619.60 |   572.20 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SC   | 1w  | LONG  |   431.80 |   838.40 |   592.00 |   572.20 | ✅ ✅ ✅ ❌ | ❌ | LONG  |
| SF   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SF   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SF   | 1d  | LONG  |  5616.00 |  5922.00 |  5690.00 |  5880.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SF   | 1w  | LONG  |  5452.00 |  6196.00 |  5616.00 |  5880.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| SH   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SH   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SH   | 1d  | SHORT |  2685.00 |  2041.00 |  2147.00 |  1889.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SH   | 1w  | SHORT |  2598.00 |  2251.00 |  2300.00 |  1889.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SI   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SI   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SI   | 1d  | LONG  |  8235.00 |  8790.00 |  8515.00 |  8785.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| SI   | 1w  | SHORT |  9280.00 |  8405.00 |  8835.00 |  8785.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SM   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SM   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SM   | 1d  | SHORT |  6420.00 |  6028.00 |  6276.00 |  6016.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SM   | 1w  | SHORT |  6720.00 |  5832.00 |  6114.00 |  6016.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SN   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SN   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SN   | 1d  | LONG  | 322580.00 | 399600.00 | 378500.00 | 397880.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| SN   | 1w  | SHORT | 469950.00 | 345000.00 | 464700.00 | 397880.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SP   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SP   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SP   | 1d  | SHORT |  5260.00 |  4944.00 |  5178.00 |  4868.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SP   | 1w  | SHORT |  5312.00 |  4926.00 |  5186.00 |  4868.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SR   | 1d  | SHORT |  5538.00 |  5339.00 |  5455.00 |  5314.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| SR   | 1w  | SHORT |  5538.00 |  5339.00 |  5455.00 |  5314.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SS   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SS   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| SS   | 1d  | SHORT | 15835.00 | 14600.00 | 15175.00 | 14385.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| SS   | 1w  | LONG  | 13705.00 | 15835.00 | 14600.00 | 14385.00 | ✅ ✅ ✅ ❌ | ❌ | SHORT |
| TA   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| TA   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| TA   | 1d  | SHORT |  7270.00 |  6266.00 |  7072.00 |  6302.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| TA   | 1w  | SHORT |  7270.00 |  6010.00 |  6844.00 |  6302.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| UR   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| UR   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| UR   | 1d  | SHORT |  1954.00 |  1820.00 |  1905.00 |  1793.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| UR   | 1w  | SHORT |  1954.00 |  1820.00 |  1905.00 |  1793.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| V    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| V    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| V    | 1d  | SHORT |  5178.00 |  4758.00 |  5032.00 |  4706.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| V    | 1w  | SHORT |  6364.00 |  4929.00 |  5371.00 |  4706.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| Y    | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| Y    | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| Y    | 1d  | SHORT |  8727.00 |  8402.00 |  8682.00 |  8320.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| Y    | 1w  | SHORT |  8727.00 |  8402.00 |  8630.00 |  8320.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |
| ZN   | 15m | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| ZN   | 1h  | —     |        — |        — |        — |        — |      — | ⚠️ | —     |
| ZN   | 1d  | LONG  | 24330.00 | 26315.00 | 24580.00 | 24620.00 | ✅ ✅ ✅ ✅ | ✅ | LONG  |
| ZN   | 1w  | SHORT | 26315.00 | 23010.00 | 25355.00 | 24620.00 | ✅ ✅ ✅ ✅ | ✅ | SHORT |

## 🔍 模式识别分析

**失败品种按失败次数排序:**

| 品种 | 失败数 |
|------|--------|
| C | 2 |
| CJ | 2 |
| NI | 2 |
| CF | 1 |
| CS | 1 |
| EB | 1 |
| I | 1 |
| M | 1 |
| PB | 1 |
| PS | 1 |
| RM | 1 |
| SA | 1 |
| SC | 1 |
| SS | 1 |

**各周期失败条件分布:**

| 周期 | 失败总数 | C1 | C2 | C3 | C4 |
|------|----------|----|----|----|----|
| 15m | 0 | 0 | 0 | 0 | 0 |
| 1h  | 0 | 0 | 0 | 0 | 0 |
| 1d  | 6 | 0 | 0 | 0 | 6 |
| 1w  | 11 | 0 | 0 | 0 | 11 |

## 📌 结论

🔴 **发现 17 条标点失败的品种×周期组合。**

建议：
1. 优先排查条件4（最新价未突破 C 点）——行情自然现象，非算法问题
2. 排除条件4后，分析剩余的 C1/C2/C3 失败是否指向系统性算法偏差
3. 按 P0.2 计划进入算法调试修正
