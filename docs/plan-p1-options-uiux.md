# P1 — 期权面板 UI/UX 修复计划

## 目标
修复期权面板的 IV 百分位柱状图显示问题和策略信号栏可用性问题，共 2 大类 6 个子项。

## 当前代码分析摘要

### IV 柱状图（ECharts）
- **File**: `web/templates/options_dashboard.html` (line 713-785)
- **Data**: `IV_DATA` 来自 `{{ iv_json|safe }}` — 经过 `_enrich_iv_status()` 处理
- **xAxis 当前**：`rotate: 45`, 2-line labels (`SYM\n中文名`), `grid.bottom: 110`
- **问题**：底部 label 仍拥挤；contract 字段在上期所品种含 `n` 前缀

### 策略信号表（SSR + JS 刷新）
- **File**: `web/templates/options_dashboard.html` (line 548-580 SSR, 1092-1135 JS)
- **Data**: SSR 用 `{{ options[:20] }}` (未排序), JS 刷新用 `/api/signals/options?limit=20`
- **问题**：SSR 不排序；detail icon 在部分场景无反应

### 后端数据处理
- **File**: `web/app.py`
  - `_enrich_iv_status()`: 添加中文名 + 清洗 `n` 前缀（仅 IV 数据，options signals 不受益）
  - `options_dashboard` route: `hub.get_recent_options(20)` 返回**未排序**信号

---

## 拆解步骤

### Step P1.1 — IV 柱状图修复

#### P1.1.1 修复底部 xAxis label 拥挤（1 Cycle）
- **问题**：45° 旋转 + 2 行 label 在品种多时重叠
- **方案**：
  - 增加 `grid.bottom` 从 110 → 140
  - 调小 xAxis label `fontSize` 从 9 → 8
  - 可选：xAxis label 仅显示符号（简短），中文名移到 tooltip 单独行
- **产出物**：`options_dashboard.html` 中 ECharts option 修改
- **预期耗时**：10min

#### P1.1.2 修复合约代码显示 `n` 前缀（1 Cycle）
- **问题**：上期所主力合约如 `nag2607` 未经清洗
- **分析**：
  - `_enrich_iv_status()` 已对 IV 数据清洗 `n` 前缀
  - 但 `options` 信号数据（`hub.get_recent_options()`）**没有**经过清洗
  - 策略表的 `s.contract` 显示原始 `nag2607` → 用户看到 `ag/nag2607`
- **方案**：
  - 在 `options_dashboard` route 中，对 `options` 也执行 `n` 前缀清洗
  - 或新建共享函数 `_clean_contract_prefix()`
- **产出物**：`web/app.py` options route 添加合同清洗
- **预期耗时**：10min

#### P1.1.3 添加中文名标注（1 Cycle）
- **问题**：xAxis 已有中文名但可读性仍不够
- **方案**：
  - 保留当前 `SYM\n中文名` 格式
  - 增加 `rotate: 35`（减少旋转角度提高可读性）
  - 确保 tooltip 中的中文名和合约号分开显示
- **产出物**：`options_dashboard.html` 中 xAxis formatter 优化
- **预期耗时**：10min

### Step P1.2 — 策略信号栏修复

#### P1.2.1 修复详情图标点击不一致（1-2 Cycles）
- **问题**：部分策略信号的详情图标点击无反应
- **分析**：
  - 「详情」列为 `<td class="strat-detail-link" onclick="showStratDetailFromData(this)" data-idx="...">`
  - `showStratDetailFromData()` 使用 `window._signalsData[idx]` 查找数据
  - **根因推测**：5 分钟 JS 刷新后，`renderOptionsSignals()` 对 signals 排序取前 20 条
    - 重渲染后 `data-idx` 设为 `signals.indexOf(s)`（在完整 signals 数组中的索引）
    - SSR 初始渲染时 `data-idx` 设为 Jinja2 `loop.index0`（在 options[:20] 中的索引）
    - 两者理论上都应该正确指向 `_signalsData` 中对应信号
  - **潜在 Bug 1**：`options` 列表项若 `unified_score` 为 0 或缺失，popup fallback 模式仍然显示——理论上不应导致点击无反应
  - **潜在 Bug 2**：`showStratDetailFromData` 中 `!signals[idx]` 检查：若 signals[idx] 是 `null`/`undefined` 则静默返回
  - **需要排查**：实际 `_signalsData` 中哪些 idx 指向有效数据，哪些不是
- **方案**：
  - Step 1: 在函数入口添加 `console.warn` 日志排查——哪些 idx 无效
  - Step 2: 修复数据一致性——确保 `_signalsData` 始终保持最新
  - Step 3: 启用前端 `onclick` 调试，确认点击事件是否触发
- **产出物**：修复后的 js 代码 + 浏览器调试
- **预期耗时**：15-20min

#### P1.2.2 SSR 按评分排序（1 Cycle）
- **问题**：SSR 初始渲染未按评分排序
- **当前状态**：`renderOptionsSignals()` JS 函数按评分排序取前 20，但只在 5 分钟刷新后生效
- **方案**：
  - 在 `app.py` options route 中，对 `hub.get_recent_options()` 结果按 `unified_score` 降序排列
  - 或修改 Jinja2 模板的 `for` 循环，使用 `sort(attribute='unified_score', reverse=True)`
  - Jinja2 用 `{% for s in options|sort(attribute='unified_score', reverse=True) %}` 最简洁
- **产出物**：`web/app.py` 或 `options_dashboard.html` 排序修复
- **预期耗时**：5min

#### P1.2.3 评分算法透明度确认（0.5 Cycle）
- **问题**：User Directives 记录"评分算法不透明"
- **当前状态**：**已实现** ✅ — 表头 `评分` 列已有 tooltip，包含完整的评分维度分解：
  - Θ 时间衰减 (≤25分)、V 波动率做空 (≤20分)、胜率 (≤20分) 等
  - 详情弹窗还有各维度明细分解
- **排查**：
  - 验证 tooltip 是否正确显示（CSS `.score-tooltip` 类）
  - 验证 tooltip 内容是否准确反映后端评分算法
- **产出物**：验证记录（option）或修复
- **预期耗时**：5min

---

## 依赖顺序

```
P1.1.1 (xAxis 拥挤) ─┐
P1.1.2 (n 前缀) ─────┤ 无依赖关系，可并行
P1.1.3 (中文名) ─────┘
                      ↓
P1.2.1 (详情图标) ────┬ 无明显依赖
P1.2.2 (排序) ────────┤
P1.2.3 (评分透明度) ──┘
```

全部子任务之间无严格依赖，可按任意顺序执行。

---

## 预期耗时汇总

| 子任务 | 预期耗时 | 复杂度 |
|--------|---------|--------|
| P1.1.1 xAxis 拥挤 | 10min | ⭐ |
| P1.1.2 n 前缀清洗 | 10min | ⭐ |
| P1.1.3 中文名标注 | 10min | ⭐ |
| P1.2.1 详情图标修复 | 15-20min | ⭐⭐ |
| P1.2.2 评分排序 | 5min | ⭐ |
| P1.2.3 评分透明度 | 5min | ⭐ |
| **合计** | **55-60min** | |

---

## 团队推荐

| 执行步骤 | 推荐 Agent | 职责 |
|---------|-----------|------|
| P1.1 IV 图表修复 | `ui-duarte` + `fullstack-dhh` | 视觉 + 数据清洗 |
| P1.2 策略信号修复 | `fullstack-dhh` + `qa-bach` | 代码修复 + 验证 |
| 总体 review | `qa-bach` | 回归测试 |

---

## 风险提示

1. **P1.2.1 详情图标** — 根因可能不在前端，需排查后端 `get_recent_options` 是否返回完整数据
2. **User Directives 的 P0（N 型算法）** — 当前不应启动，P1 完成后自动推进
3. **共识保护** — 更新 consensus.md 时 User Directives 区域必须完整保留
