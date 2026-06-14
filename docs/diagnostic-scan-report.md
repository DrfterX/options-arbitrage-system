# N型K线结构交易系统 — 诊断扫描报告

> 基于 `scan_all_contracts(diagnostic=True)` 生成

> 运行时间: 2026-06-15 03:30 CST

> 扫描品种: 204 个主力合约


## 一、评分分布总览


| 评分 | 合约数 | 占比 |
|------|--------|------|
| NONE (score=0) | 204 | 100.0% |

| 评分范围 | 数量 |
|----------|------|
| score=3+ (ENTRY) | 0 |
| score=2 (L2通过) | 0 |
| score=1 (L1通过) | 0 |
| score=0 (NONE)   | 204 |

### 方向分布

- LONG: 62 (30.4%)
- NONE: 35 (17.2%)
- SHORT: 107 (52.5%)

## 二、三级验证漏斗

```
  204 个主力合约
    │
    ├─ L1通过: 0/204 (0.0%)
    │   └─ 失败: 204
    │
    ├─ L2通过: 0/204 (0.0%)
    │   └─ 失败: 204
    │
    ├─ L3通过: 0/204 (0.0%)
    │   └─ 失败: 204
    │
    └─ ENTRY (score>=3): 0
```

## 三、各级失败原因明细


### Level1 — 周线N型+日线MACD


| 原因 | 出现次数 |
|------|---------|
| `MACD腿2=False(B点(SHORT): 转折前主体RED，期望BLUE)` | 73 |
| `周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLUE | 腿2❌B点(LONG): MACD仍RED且histogram未反转(最` | 55 |
| `MACD腿1=False(A点(LONG): 转折前主体RED，期望BLUE)` | 55 |
| `MACD腿3=True(已变蓝(空头确认))` | 54 |
| `无周线活跃N型结构` | 35 |
| `无任何活跃周线N型结构记录` | 35 |
| `周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且histogram未反转(最近3根均值141.63) | 腿2❌B点(SHORT): 转` | 21 |
| `MACD腿1=False(A点(SHORT): MACD仍RED且histogram未反转(最近3根均值141.63))` | 21 |
| `MACD腿3=True(红柱减弱(75.2→45.8))` | 21 |
| `MACD腿1=True(A点(SHORT): MACD仍RED,但histogram已转负(动量向下))` | 21 |
| `周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且histogram未反转(最近3根均值127.55) | 腿2❌B点(SHORT): 转` | 21 |
| `MACD腿1=False(A点(SHORT): MACD仍RED且histogram未反转(最近3根均值127.55))` | 21 |
| `周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且histogram未反转(最近3根均值8.42) | 腿2❌B点(SHORT): MAC` | 21 |
| `MACD腿1=False(A点(SHORT): MACD仍RED且histogram未反转(最近3根均值8.42))` | 21 |
| `MACD腿2=False(B点(SHORT): MACD仍BLUE且histogram未反转(最近3根均值-20.67))` | 21 |
| `MACD腿3=True(已变红(多头确认))` | 20 |
| `周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但histogram已转负(动量向下) | 腿2❌B点(SHORT): 转折前主体RED，` | 20 |
| `MACD腿2=False(B点(LONG): MACD仍RED且histogram未反转(最近3根均值10.90))` | 20 |
| `MACD腿3=True(蓝柱减弱(13.8→11.1))` | 20 |
| `MACD腿3=False(红柱未减弱(7.3→20.2))` | 19 |

### Level2 — 小时线N型+15mMACD


_无失败记录（全部通过）_


### Level3 — 15mN型+3m稳定+突破


_无失败记录（全部通过）_


## 四、MACD 腿级通过率


### Level1（日线MACD）


| 检查项 | 计数 |
|--------|------|
| macd_passed_leg2=False | 166 |
| macd_passed_leg1=False | 147 |
| macd_passed_leg3=True | 121 |
| macd_passed_leg3=False | 48 |
| macd_passed_leg1=True | 22 |
| macd_passed_leg2=True | 3 |

### Level2（15mMACD）


_无MACD腿级数据_


### MACD腿通过率汇总

- Level1(日线MACD):
  - 腿1通过: 22/169 (13.0%)
  - 腿2通过: 3/169 (1.8%)
  - 腿3通过: 121/169 (71.6%)
- Level2(15mMACD):

## 五、3m 数据质量分析


_无3m数据_


## 六、突破价 vs B点对比


_无突破对比数据_


## 七、品种级诊断概览


| 品种 | L1 | L2 | L3 | Score | 方向 | 问题摘要 |
|------|----|----|----|-------|------|---------|
| A      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| AG     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): MACD仍BLUE且hist; L2:失败 |
| AL     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| AP     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| AU     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| B      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| BU     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| C      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| CF     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| CJ     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): MACD仍BLUE且hist; L2:失败 |
| CS     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| CU     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| EG     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| FG     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): 转折前主体BLUE，期望R; L2:失败 |
| HC     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): MACD仍BLUE且hist; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| I      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| J      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): MACD仍BLUE且hist; L2:失败 |
| JD     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): MACD仍BLUE且hist; L2:失败 |
| JM     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| L      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| LC     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| LH     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): MACD仍BLUE且hist; L2:失败 |
| M      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| MA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): RED(2根)→BLUE(1; L2:失败 |
| NI     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): MACD仍BLUE且hist; L2:失败 |
| NR     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| OI     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| P      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| PB     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): 转折前主体BLUE，期望R; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| PG     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| PP     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| PX     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RB     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| RM     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| RU     | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| SA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): 转折前主体BLUE，期望R; L2:失败 |
| SC     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| SC     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| SF     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| SH     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| SI     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| SM     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| SN     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1A点(SHORT): MACD仍RED,但hist; L2:失败 |
| SP     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): 转折前主体BLUE，期望R; L2:失败 |
| SR     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| SS     | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| TA     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| UR     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| V      | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | -     | L1:无周线活跃N型结构; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| Y      | ❌ | ❌ | ❌ | 0 | LONG  | L1:周线MACD轨迹未验证: 腿1❌A点(LONG): 转折前主体RED，期望BLU; L2:失败 |
| ZN     | ❌ | ❌ | ❌ | 0 | SHORT | L1:周线MACD轨迹未验证: 腿1❌A点(SHORT): MACD仍RED且hist; L2:失败 |

## 八、已知问题与改进建议


### 已知问题

- 3m数据周期异常: 204 品种受影响

### 主要瓶颈分析

- 🟠 **第二瓶颈：Level2** — L1通过但L2失败比例高（小时线N型或15mMACD）
- ❌ **L3完全阻塞** — 无品种通过Level3（3m数据或15m突破）

### 建议优先处理

- **1. 3m数据问题（阻塞）** — 无3m数据→L3永远无法通过→0 ENTRY
- **2. MACD 70%阈值分析** — 统计各周期MACD颜色分布，判断70%是否过严
- **3. 评分重置触发分析** — 检查是否误杀了有效信号
- **4. 周线N型结构窗口** — 当前SWING_WINDOWS["1w"]=2，窗口极窄