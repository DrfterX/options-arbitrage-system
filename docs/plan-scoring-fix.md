# N 型信号评分算法修复计划

## 目标
修复 Level2 MACD 轨迹验证过于严格导致 100% 信号 score=0.30 的问题

## 诊断发现

### 1. 信号管道现状
- **Level1 (周线N型)**: 887/887 通过 ✅ — 周线N型结构正常
- **Level2 (小时线N型+15m MACD)**: **0/887 通过** ❌ — 这是全部瓶颈
- **Level2 失败原因分布**:
  - "小时线无活跃N型结构" — 约一半品种
  - "小时线方向不匹配周线方向" — 约 20 个品种
  - "MACD轨迹未配合" — 29 个品种，**全部在腿1(A转折点)失败**

### 2. 核心问题：MACD轨迹腿1(A点)验证不通过

手动检测 10 个有 L1+L2 方向一致的品种，**全部腿1失败**。

**15m MACD 在小时线N型A点处的颜色过渡不成立的原因：**

| 品种 | L1方向 | 期望腿1 | 实际腿1 | 失败模式 |
|------|--------|---------|---------|---------|
| RB2609 | LONG | A前BLUE→A后RED | A后仍BLUE | MACD滞后于价格 |
| P2609 | LONG | A前BLUE→A后RED | A前已RED | A前MACD已反转 |
| I2609 | LONG | A前BLUE→A后RED | A前已RED | 同上 |
| AU2608 | SHORT | A前RED→A后BLUE | A前已BLUE | A前MACD已反转 |
| CF2609 | SHORT | A前RED→A后BLUE | A前已BLUE | 同上 |
| SR2609 | LONG | A前BLUE→A后RED | A前已RED | 同上 |

**根本原因：** MACD 的 15 分钟颜色变化比小时线 N 型结构的极值点慢半拍到一拍。当 N 型结构在小时线上确认 A 点时，15 分钟 MACD 可能已经提前反转，或者还在之前的颜色中滞后。要求 A 极值点前 3 根 15m MACD 柱体主体为一种颜色、后 3 根主为另一种颜色，在真实行情中几乎不成立。

### 3. 现象量化

```
65 合约 → 60 L1可过 → 29 L1+L2方向一致 → 0 MACD轨迹通过 → 0 Level2通过
                                                  ↑
                                           这是断裂点
```

- 历史 9,502 条信号中只有 29 条（全部 CU 品种）L2 通过 score=0.6
- 29 条历史高评分信号全部来自同一品种 CU（铜），说明该品种的 MACD 正好匹配了规则，但其他 51 个品种不匹配

## 改造方案

### 变更1：Level2 通过条件放宽

**当前:** L2 N型方向匹配 + MACD轨迹两腿全部通过 → Level2 passed
**改为:** L2 N型方向匹配 → Level2 passed（MACD轨迹变成评分因素而非硬门槛）

具体改动 (`futures/scorer.py`):

```python
# OLD — MACD轨迹是硬门槛
if l2_macd.get("passed"):
    l2_result["passed"] = True
else:
    l2_result["passed"] = False

# NEW — N型方向匹配即通过Level2，MACD轨迹参与评分
l2_result = {"passed": True, ...}  # 方向匹配即通过
```

### 变更2：Level2 评分公式调整

- L2 N型方向匹配 → score=0.5（而不是当前不合格时的0.3）
- MACD轨迹通过 → score=0.6
- 加分项 +0.10~0.15

### 变更3：评分阶段流水线

```
Level1 通过 → score=0.3
  + L2方向匹配 → score=0.5 (CANDIDATE)
    + L2 MACD轨迹通过 → score=0.6 (CANDIDATE)
      + L3 N型存在 → 保持0.6
        + L3突破触发 → score=1.0 (ENTRY)
  + 加分项 → score+=0.10~0.15
```

## 预期效果

- Level2 通过率: 0% → ~45% (29/65 品种有方向一致的 L2 N 型)
- 信号评分分布: 从全部 0.30 变为 0.30~0.60 分布
- 有 CANDIDATE 信号的品种数量: 0 → ~29
- ENTRY 信号仍然需要 Level3 突破触发，不会虚增

## 风险

- MACD轨迹验证的弱化可能增加假信号，但 Level2 本身仅是 CANDIDATE 评级（不可交易），突破触发仍需 Level3 15分钟突破确认
- 若 ENTRY 信号质量下降，可回退并加强 Level3 门槛
