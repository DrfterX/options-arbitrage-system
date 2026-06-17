# Plan: P1 — 期权面板 UI/UX 修复

## 目标

修复期权面板的 5 个 UI/UX 问题（由 2026-06-15 User Directives 记录）：

1. **IV 百分位柱状图** — 底部代码拥挤、缺中文名、代码格式 bug
2. **期权策略信号栏** — 详情图标点击不一致、评分排序问题、评分算法说明

---

## 代码审计摘要

### 当前架构

```
app.py (路由)                          options_dashboard.html (模板, 1318行)
  │                                              │
  ├─ /api/iv/status → IV_DATA                    ├─ IV 柱状图 (echarts, 行728-801)
  ├─ /api/signals/options → 信号数据              ├─ 策略信号表 (行564-595, SSR + JS动态)
  └─ index() → 渲染模板                            └─ 策略详情浮窗 (行696-703, 1190-1282)
```

### IV 柱状图审计

| 检查项 | 状态 | 说明 |
|--------|------|------|
| x-axis 中文名 | ✅ | 已实现：`formatter` 用 `sym + '\n' + cname` 双行显示 |
| x-axis 拥挤 | ⚠️ | `fontSize: 8`, `rotate: 35`, `interval: 0` — 30+ 品种全显示，bottom 180px 可能不够 |
| IV_DATA.name | ✅ | 后端返回 `name: "白银"` 等中文名，前端正确引用 |
| **contract 显示 bug** | ❌ | 某些品种显示为 `ag/nag2607` 格式（需排查数据来源） |

### 策略信号栏审计

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 评分排序 | ✅ | `(b.unified_score\|\|0) - (a.unified_score\|\|0)` = 降序，逻辑正确 |
| **详情点击不一致** | ❌ | `signals.indexOf(s)` 依赖对象引用比较，排序切片后可能找不到索引→返回 -1→popup 不弹 |
| 评分算法 tooltip | ✅ | 表头已有完整评分分解 tooltip（7 维度） |
| 评分分解 popup | ✅ | `detail.score_components` 在详情弹窗中显示各维度分数 |
| 初始渲染 data-idx | ✅ | SSR 用 `loop.index0` 正确绑定 |

---

## 拆解步骤

### Step P1.1 — IV 柱状图底部优化 + 中文名确认（~15min）

**问题**：底部代码拥挤、缺中文名尚未在所有浏览器/品种验证

**任务**：
1. 检查 x-axis 渲染：当前 `fontSize: 8, rotate: 35, interval: 0, bottom: 180`
   - 增加 `grid.bottom` 从 180 → 220（给双行标签更多空间）
   - 保持 `interval: 0`（全部显示）但降低 `fontSize: 7`
   - 验证 30+ 品种在 1920×1080 下是否清晰
2. 确认所有品种的 `name` 字段在后端都正确赋值（`_enrich_iv_status` → IV recorder）
3. 产出：代码变更 + 截图验证

**产出物**：`options_dashboard.html` 中 IV 柱状图 x-axis 配置修改

---

### Step P1.2 — 修复合约代码格式 bug（~15min）

**问题**：某些品种显示为 `ag/nag2607` 而非 `ag2607`

**任务**：
1. 排查问题来源：
   - 检查 `IV_DATA[i].contract` 值是否为 `"ag2607"`（目前 API 返回正确）
   - 排查 options 信号表中 `s.contract` 是否包含额外前缀
   - 检查 SSR 端 `options[:20]`→`options[:20] | tojson` 序列化中 contract 字段是否被污染
   - 检查 `_enrich_options_signals` 中是否拼接了 symbol + contract
2. 如果后端问题：修复 `_enrich_options_signals` 或 IV recorder
3. 如果前端问题：修复显示逻辑
4. 产出：代码变更 + API 验证

**产出物**：`options_dashboard.html` 或 `app.py` 中 contract 格式化逻辑修复

---

### Step P1.3 — 修复详情图标点击不一致（~20min）

**问题**：部分策略信号的详情图标点击无反应

**任务**：
1. 确认问题根因：
   - 检查 `showStratDetailFromData` 中 `signals.indexOf(s)` 的行为
   - 动态渲染时：`sorted = signals.slice().sort(...)`, 再用 `signals.indexOf(s)` — slice 保留引用应该可找到
   - 但 SSR 初始渲染用 `data-idx="{{ loop.index0 }}"`，与 `window._signalsData` 数组索引一致
   - 5min 刷新替换 `window._signalsData` 后，旧 data-idx 引用新数组不再有效
2. 修复方案：将 `data-idx` 替换为 `data-sym`+`data-strategy` 双键匹配，或用 `findIndex`
3. 产出：代码变更 + 浏览器验证

**产出物**：`options_dashboard.html` 中 `renderOptionsSignals` 和 `showStratDetailFromData` 修复

---

### Step P1.4 — 验证评分排序 + 评分算法展示（~10min）

**问题**：评分排序疑似不对 + 评分算法不透明

**任务**：
1. 验证排序：确认 `renderOptionsSignals` 和 `renderOptionCards` 都用 `(b.unified_score||0) - (a.unified_score||0)` 降序
2. 验证初始 SSR 排序：`app.py` → `index()` 中 options 列表传入模板前是否按 score DESC 排序
3. 确认评分算法 tooltip 在所有情况下都能显示（鼠标悬停表头 "评分" 列的 `i` 图标）
4. 评分不透明问题：已有完整 tooltip (7维度+总分+封顶规则)，但测试是否所有设备有效
5. 产出：验证记录，如有问题则修复

**产出物**：代码变更（如需要）+ 验证记录

---

### Step P1.5 — 全面验证 + 部署确认（~10min）

**任务**：
1. 使用正确 Host 头 `options.drifter.indevs.in` 验证期权面板页面
2. 验证 IV 柱状图渲染无重叠
3. 验证合约代码格式正确
4. 点击每条策略信号的详情图标确认能弹出
5. 确认评分降序排列
6. 产出：部署验证记录

**产出物**：验证通过报告

---

## 依赖顺序图

```
P1.1 (IV x-axis) ──→ P1.2 (contract bug) ──→ P1.3 (popup fix) ──→ P1.4 (sorting verify) ──→ P1.5 (verify)
     独立的               排查关联               核心功能修复            简单验证              最终验证
```

- P1.1 和 P1.2 无依赖关系，可交换顺序
- P1.3 需要理解数据流，排在 P1.2 之后更高效
- P1.4 是验证步骤，无需前置
- P1.5 是最终验证，依赖所有前置步骤完成

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|:----:|:----:|------|
| contract bug 根因在深层数据管道 | 低 | 中 | 前端可做 fallback 显示 `symbol+contract` |
| 详情弹窗是深层数据问题（strategy_details 为空） | 中 | 高 | 弹窗已有 fallback 模式（行1257-1268），确认 fallback 正确触发 |
| 评分 tooltip 在移动端不可用 | 低 | 低 | 桌面端为主，可忽略 |
