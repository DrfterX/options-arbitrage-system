# P0 Phase ① 评分系统重写计划

## 目标
将 N型K线结构交易系统的评分系统从允许 score≥2 入场改为 score≥3 硬条件入场，使三级嵌套验证各层都作为硬性门槛。

## CEO 决策
**GO** — 方向正确，3分硬条件入场是系统设计的核心假设（详见 `docs/ceo/p0-scoring-decision.md`）

## Critic Pre-Mortem
**有条件赞成** — 改动极小（3行），双向门决策，执行后需验证（详见 `docs/critic/p0-scoring-premortem.md`）

## 实施步骤

| Step | 名称 | 预期耗时 | 产出物 | 依赖 |
|------|------|---------|--------|------|
| N.1 | 代码修改：scorer.py + settings.py | 5min | 修改后的文件 | — |
| N.2 | 运行测试 + 修复断言 | 10min | 测试全部通过 | N.1 |
| N.3 | Pipeline 验证 | 5min | Pipeline 输出 + 确认 score≥3 信号存在 | N.2 |

**总预计：20 分钟**

## 详细步骤

### Step N.1 — 代码修改（~5分钟）

**文件 1: `futures/scorer.py` 第 848 行**
```python
# 旧:
if score >= 2:
# 新:
if score >= 3:
```

**文件 2: `futures/scorer.py` 第 851 行**
```python
# 旧:
    if score >= 3 and bonus_total > 0:
# 新:
    if bonus_total > 0:
```

**文件 3: `config/settings.py` 第 191 行**
```python
# 旧:
"entry_threshold": 2,
# 新:
"entry_threshold": 3,
```

### Step N.2 — 测试修复（~10分钟）

1. 运行 `python -m pytest futures/ -v -x`
2. 定位失败的测试（预期：score=2 → ENTRY 的断言需要改为 NONE）
3. 更新断言
4. 全量测试通过确认

### Step N.3 — Pipeline 验证（~5分钟）

1. 运行 `python -m futures.pipeline --mode futures`
2. 检查 scan 输出中 signal_type 的分布
3. 确认 score=3 的 ENTRY 信号存在
4. 记录基准数据供后续对比

## 回退方案

```
scorer.py: if score >= 2 (改回)
scorer.py: if score >= 3 and bonus_total > 0 (改回)
settings.py: entry_threshold = 2 (改回)
```
