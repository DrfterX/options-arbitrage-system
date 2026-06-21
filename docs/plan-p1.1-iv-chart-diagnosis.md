# P1.1a — IV 百分位柱状图诊断

## 诊断时间
2026-06-17，Cycle #135

## 代码位置
- 渲染函数：`initIV()` at options_dashboard.html L714-788
- 数据来源：`IV_DATA = JSON.parse('{{ iv_json|safe }}')` at L713
- 后端清洗：`_enrich_iv_status()` at app.py L50-58

## 问题诊断

### 问题 1：底部代码拥挤（需修复）
**当前设置：**
- xAxis 45 个品种，`fontSize: 9`, `rotate: 45°`
- 标签格式：`{cname|AG 白银}`（5-6 个中英文字符宽）
- `grid.bottom: 80` — 底部空间 80px
- `interval: 0` — 每个标签都显示
- 每个品种在 x 轴约占 ~22px（~1000px 容器 / 45）

**根因分析：**
- 每个标签 "AG 白银" 约 30px 宽，45° 旋转后投影约 21px
- 45 个标签 × 45° 旋转 = 标签间距非常紧张，视觉上拥挤
- 底部 margin 80px 对于 45° 旋转的标签来说偏低

### 问题 2：缺少中文名（已实现）
- 代码中已存在 `{cname|AG 白银}` 格式
- tooltip 也显示中文名
- 只是因为拥挤导致中文名看不清楚，非功能缺失

### 问题 3：ag/nag2607 代码显示 bug（已修复）
- `_enrich_iv_status()` L57 已用 `re.sub(r'^[nN]', '', contract)` 去除 n 前缀
- 当前 API 返回 `contract: "ag2607"` 正确
- 信号数据也正常（无 n 前缀）
- 该问题已被之前的 cycle 修复

## 修复方案

### 方案：两行显示 + 增加底部空间
1. xAxis formatter 返回 `sym + '\n' + cname`（两行显示）
2. `grid.bottom`: 80 → 110（为两行标签腾空间）
3. 移除 `rich` 样式（不再需要单行 rich text）
4. `lineHeight`: 14 → 12（两行紧凑显示）
5. 保持 `fontSize: 9`（可读性不受影响）

### 预期效果
- 每个标签仅 ~15px 宽（单字符宽度），远小于当前 30px+
- 45 个标签轻松排列无重叠
- 中文名仍保留，且可读性比当前拥挤单行更好