# B.3 Skeleton Loading — 三面板评估记录

评估日期：2026-06-19

## 1. 总体架构

三个面板（Portal / Futures / Options）共用 `/static/style.css`，其中已包含：
- `.skeleton` 类定义（line 1430-1441）
- `@keyframes skeleton-shimmer`（line 1442-1445）
- `@keyframes card-enter`（line 1534-1537）

但三个面板各自在 inline `<style>` 中重复定义了这些内容。

---

## 2. 各面板 Skeleton 现状

### Portal（portal.html）

| 组件 | 是否有 Skeleton | 类型 |
|------|---------------|------|
| **Full-page initial skeleton** | ❌ 缺失 | — |
| **Stats 数值 (maxScore/long/short/total)** | ✅ | 内联 `.skeleton` 元素 |
| **Sector grid** | ✅ | 6 个 `.skeleton` 占位器 |
| **IV mini chart** | ✅ | `.skeleton-chart` |
| **Strategy list** | ✅ | 4 行 `.skeleton` 元素 |
| **Footer badge** | ✅ | 内联 `.skeleton` |
| **Section-level `.is-loading` 状态** | ❌ 缺失 | — |
| **Loading dot 指示器** | ❌ 缺失 | — |

**特点**：最简单。只有内联 skeleton 占位，没有全屏初始骨架屏，没有刷新时的 section 级 loading 状态管理。

### Futures（futures_dashboard.html）

| 组件 | 是否有 Skeleton | 类型 |
|------|---------------|------|
| **Full-page initial skeleton** | ✅ | `div.initial-skeleton`（topbar + stats + matrix rows）|
| **Stats 数值** | ✅ | 内联 `.skeleton` 元素 |
| **Matrix 信号表格** | ✅ | `.is-loading .matrix-table { opacity: .5 }` |
| **K-line 弹窗图表** | ✅ | `.skeleton-chart`（含蜡烛图占位 + Y 轴网格线）|
| **Positions 面板** | ✅ | `.pos-error` + loading 状态 |
| **Section-level `.is-loading` 状态** | ✅ | `matrix-section.is-loading` |
| **Loading dot 指示器** | ✅ | `mx-loading-dot` |

**特点**：最完整。有全屏骨架+局部刷新加载态+专用图表 skeleton。

### Options（options_dashboard.html）

| 组件 | 是否有 Skeleton | 类型 |
|------|---------------|------|
| **Full-page initial skeleton** | ✅ | `div.initial-skeleton`（含 IV chart / strategy grid / card area）|
| **Stats 数值** | ✅ | 内联 `.skeleton` 元素 |
| **IV chart** | ✅ | ECharts 容器 + initial-skeleton 占位 |
| **IV summary** | ✅ | 内联 `.skeleton` 元素 |
| **Strategy table** | ✅ | `.strategy-panel.is-loading` 控制 opacity |
| **Strategy cards** | ✅ | `.is-loading .options-cards { opacity: .5 }` |
| **SmartFilter** | ✅ | `.filter-section.is-loading` 控制 |
| **Health panel** | ✅ | `.cards-section.is-loading` 控制 |
| **Section-level `.is-loading` 状态** | ✅ | 4 个 section 各有独立控制 |
| **Loading dot 指示器** | ✅ | `loading-dot`（多个 section 共用动画）|

**特点**：最系统化。有完整 section 级 loading 状态管理，每个 section 独立控制。

---

## 3. 重复定义汇总

| 定义项 | style.css | futures_inline | options_inline | portal_inline |
|--------|-----------|---------------|---------------|--------------|
| `@keyframes skeleton-shimmer` | ✅ L1442 | ✅ (1.5s) | ✅ (1.5s) | ✅ (1.5s) |
| `.skeleton` 类 | ✅ L1430 | ✅ L71-72 | ✅ L440-453 | ✅ L874-888 |
| `@keyframes skeleton-fade-in` | ❌ | ✅ | ✅ | ❌ |
| `.initial-skeleton` | ❌ | ✅ | ✅ | ❌ |
| `.skeleton-chart` | ❌ | ✅ | ❌ | ✅ |
| `loading-dot` / `mx-loading-pulse` | ❌ | ✅ (mx-) | ✅ | ❌ |

---

## 4. 问题 & 冲突

### 4.1 style.css line 1667-1669 冲突
```css
.skeleton {
  animation: none !important;
}
```
注释说"避免 skeleton loading 状态下入场动画闪烁"，但这里**直接禁用了所有 `.skeleton` 元素的 shimmer 动画**。这意味着：
- 首次加载时，如果 `.skeleton` 元素在 DOM 中且没有 `is-loading` 父容器 → 不显示 shimmer
- 仅在 futures 和 options 的 `is-loading` 作用下（`.is-loading .skeleton { animation: skeleton-shimmer 1.5s ... }`）才重新启用

**这不是一个真正的 bug**（因为 futures/options 用 `.is-loading .skeleton` 覆盖了），但 Portal 没有 `is-loading` 机制，因此 portal 的 skeleton 实际上是静态的（永不 shimmer）。

### 4.2 Portal 缺少刷新态 skeleton
Portal 首次加载有内联 skeleton 占位，但数据刷新（fetch 过程中）没有 section 级的 loading 保护。Futures 和 Options 都有 `.is-loading` 机制在刷新时降低 opacity 防止闪烁。

### 4.3 动画速度不一致
- style.css `.skeleton`: `1.8s ease-in-out infinite`
- futures inline: `1.5s`
- options inline: `1.5s`
- portal inline: `1.5s`
- 但 style.css L1667 `.skeleton { animation: none !important }` 覆盖了上面的 1.8s

---

## 5. 统一化建议

### 可立即共享到 style.css 的内容（B.3.2）：
1. 删除三个面板 inline `<style>` 中重复的 `@keyframes skeleton-shimmer` 和 `.skeleton` 定义（style.css 已有）
2. 将 `@keyframes skeleton-fade-in` 统一到 style.css
3. 统一 `loading-dot` / `mx-loading-pulse` 动画到 style.css

### 需评估共享范围的（B.3.3/可选的）：
1. `initial-skeleton` 结构 → 三个面板结构不同，不容易模板化
2. `.skeleton-chart` → 只有 futures 和 portal 用，且结构不同

### Portal 缺失项（修复优先级）：
1. 无 `initial-skeleton` — 中等（portal 轻量，影响有限）
2. 无 `is-loading` 刷新态 — 低（portal 数据更新不频繁）
3. 无 `loading-dot` — 低

---

## 结论

**B.3.2 可做**：删除三面板 inline 中重复的 skeleton-shimmer + skeleton 类定义，统一到 style.css。清理 style.css L1667-1669 的 `.skeleton { animation: none !important }` 冲突（改用更精确的选择器避免覆盖 shimmer）。

**B.3.3 可选做**：Jinja2 macro 对于 shared skeleton 元素而言收益有限（current inline skeleton 已经是轻量级占位），主要价值是统一动画定义而非 HTML 结构。
