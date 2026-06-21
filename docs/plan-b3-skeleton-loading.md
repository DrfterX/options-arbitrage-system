# B.3 Skeleton Loading — 方案设计

## 目标
为期货信号矩阵页面（futures.drifter.indevs.in）提供完整的 Skeleton Loading 方案，消除所有数据加载过程中的空白/闪烁，提升感知加载速度。

---

## 1. 当前状态评估

### 已实现的部分
| 区域 | 实现方式 | 状态 |
|------|---------|------|
| Stats bar（统计数据栏） | SSR 直接渲染（Jinja2），无加载状态 | ✅ 无需求 |
| Sector stats（板块统计） | SSR 直接渲染 | ✅ 无需求 |
| Signal cards（信号卡片） | SSR 直接渲染 | ✅ 无需求 |
| **Matrix 5min 自动刷新** | `createMatrixSkeleton(8)` 生成骨架行 + 渐入动画 | ⚠️ 已实现但有改进空间 |
| SmartFilter stats | 内联 `span.skeleton` 占位符，JS 加载后替换 | ✅ 已实现 |
| SmartFilter log | 全宽 `div.skeleton` 行 | ✅ 已实现 |
| Positions panel | 内联 skeleton 占位符（stats + open cards + history table） | ✅ 已实现 |
| Backtest panel | 全宽 skeleton 块 | ✅ 已实现 |
| Health panel | 所有卡片内联 skeleton 占位符 | ✅ 已实现 |
| CSS 基础 | `skeleton-shimmer` 动画 + `.skeleton`/`.skeleton-inline`/`.skeleton-block`/`.skeleton-chart` 类 | ✅ 已实现 |

### 已实现的动画效果
- `@keyframes skeleton-shimmer` — 1.5s 渐变 shimmer
- `@keyframes skeleton-fade-in` — 0.3s 淡入 + 上移
- `skeleton-shimmer` 与 `skeleton-fade-in` 独立运行，互不冲突
- 骨架行有 `animation-delay` 实现级联效果（每行差 0.08s）
- `.matrix-section.is-loading` 添加加载指示灯（`mx-loading-dot`）+ 半透明矩阵

### 核心问题点

1. **`createMatrixSkeleton(8)` 固定 8 行**
   - 实际品种数可能远多于 8 个（现有约 20+ 品种）
   - 数据较少时（如 filtering），8 行 skeleton 过多，显得突兀
   - 需要根据预期品种数动态调整行数

2. **Stats bar 在 5min 刷新时无 skeleton**
   - 虽然 stats bar 是 SSR 渲染的，但 5min 自动刷新只刷新矩阵，不刷新 stats bar
   - 如果未来添加 stats bar 的客户端刷新，需要 skeleton 支持

3. **Signal cards section 无 skeleton**
   - SSR 渲染，当前无问题
   - 但如果未来添加卡片区域的动态刷新，需要 skeleton

4. **初始页面加载无骨架**
   - 当前依赖 SSR，首次加载速度直接取决于服务器响应
   - 对于慢网络或首次访问，页面完全空白直到 SSR 完成
   - 可添加 CSS-only 骨架屏（在 JS 加载前就显示）

---

## 2. 改进方案设计

### 2.1 Matrix skeleton 动态行数（B.3.2 实现）

**问题：** `createMatrixSkeleton(8)` 硬编码 8 行。

**方案：** 从 API 获取预期行数或从当前数据推断。

```javascript
// 改进方案 A — 从已知品种数量推断
function createMatrixSkeleton(count) {
  var n = count || 8;
  // ... 用 n 循环生成行
}

// 在 5min refresh 中：获取当前矩阵行数（从 DOM 或 API）
var currentRows = document.querySelectorAll('.matrix-table tbody tr:not(.sector-row)').length;
var skeletonCount = Math.max(currentRows, 8);
tbody.innerHTML = createMatrixSkeleton(skeletonCount);
```

**改进 B — 多样化的 skeleton 列宽度**
当前所有 skeleton 行使用相同的宽度模式。改进为：
- 品种名列：使用不同的随机宽度模拟真实数据
- 信号色块：保持正方形（28×28），与真实 cell 一致
- 共振列：变化宽度模拟共振条的不同长度

### 2.2 Sector separator rows in skeleton（B.3.2 实现）

**问题：** 当前 skeleton 行没有 sector 分隔行，而真实数据有。

**方案：** 在 skeleton 中每隔 3-4 行插入 sector 分隔行占位。

```javascript
// 在 createMatrixSkeleton 中
for (var i = 0; i < n; i++) {
  if (i > 0 && i % 4 === 0) {
    html += '<tr><td colspan="6" class="sector-label skeleton" style="height:22px">&nbsp;</td></tr>';
  }
  // ... 正常行
}
```

### 2.3 CSS-only 初始加载骨架屏（B.3.3 实现）

**方案：** 在 `<body>` 的第一个子元素添加纯 CSS 骨架屏：
- 只在页面加载时显示，JS 就绪后自动隐藏
- 不需要 JS 依赖，HTML + CSS 即可

```html
<!-- 在 <body> 开头（JS 加载前即可渲染） -->
<div id="initialSkeleton" class="initial-skeleton">
  <div class="is-topbar"></div>
  <div class="is-stats">
    <div class="is-stat"></div>
    <div class="is-stat"></div>
    <div class="is-stat"></div>
    <div class="is-stat"></div>
  </div>
  <div class="is-sectors">
    <div class="is-sector"></div>
    <div class="is-sector"></div>
    <div class="is-sector"></div>
  </div>
  <div class="is-matrix">
    <div class="is-matrix-row"></div>
    <div class="is-matrix-row"></div>
    <div class="is-matrix-row"></div>
  </div>
</div>
<style>
.initial-skeleton { ... shimmer ... }
/* JS 就绪后隐藏 */
</style>
```

然后在 JS 加载完成/SSR 渲染后隐藏：
```javascript
// 第一行 JS
document.getElementById('initialSkeleton')?.remove();
```

### 2.4 Stats bar 5min 刷新 skeleton

**当前：** Stats bar 只在 SSR 渲染，5min 刷新不更新 stats bar。

**方案：** 如果未来需要 stats bar 也自动刷新，添加 skeleton：
- 每个 stat-item 内的 `.value` 替换为 skeleton
- JS fetch 完成后替换回真实数据
- 使用与 SmartFilter 相同的 skeleton 模式

### 2.5 加载过渡效果改进

**当前：** 矩阵加载时使用 `opacity: .5` 过渡，略显生硬。

**方案：** 
- 用 skeleton 完全替换矩阵内容（而非半透明覆盖）
- 添加更平滑的过渡：skeleton → 真实数据的淡入
- skeleton 行使用更丰富的级联延迟（0.04s 递增）

---

## 3. 实施计划

| 步骤 | 内容 | 预期耗时 | 产出 |
|------|------|---------|------|
| **B.3.2** | 实现 Matrix skeleton 动态行数 + sector 分隔 + CSS-only 初始骨架 | 15min | `futures_dashboard.html` 修改 |
| **B.3.3** | 部署并验证 | 5min | 部署确认 |

### B.3.2 具体实现要点

1. **修改 `createMatrixSkeleton` 函数**：
   - 接受 `count` 参数替代硬编码 8
   - 每 4 行插入 sector 分隔行
   - 品种位列宽度多样化

2. **添加初始骨架屏 HTML**：
   - 在 `<body>` 第一个子元素插入 `#initialSkeleton`
   - CSS: `initial-skeleton` 使用相同的 shimmer 动画
   - JS 第一行移除：`document.getElementById('initialSkeleton')?.remove()`

3. **CSS 补充**：
   - 添加 `@keyframes skeleton-shimmer`（已在 `portal.html` 中定义，迁移到 `futures.css`）
   - 添加 `is-topbar`, `is-stats`, `is-matrix` 等初始骨架样式

### 不需要改动的内容
- SmartFilter、Positions、Backtest、Health 面板的 skeleton 已是完整状态，无需改动
- Stats bar（SSR 渲染）无需 skeleton
- Signal cards（SSR 渲染）无需 skeleton

---

## 4. 与设计系统一致性

- 所有 skeleton 使用与 portal.html 相同的 `@keyframes skeleton-shimmer` 动画
- 使用 futures.css 的配色体系（`var(--text3)` 等 token，而非硬编码色值）
- Skeleton 色值：`rgba(79, 91, 128, 0.07)` / `0.18` / `0.07` — 使用 futures.css 的 `--text3` 派生值
- 圆角使用 `var(--radius-sm)`（4px），与设计系统一致

---

## 5. 验收标准

1. ✅ 初始页面加载时立即显示 CSS-only 骨架屏，无空白阶段
2. ✅ JS 加载完成后骨架屏平滑消失，SSR 内容显示
3. ✅ 5min 矩阵自动刷新时 skeleton 行数与实际品种数匹配
4. ✅ Sector 分隔行在 skeleton 中有正确体现
5. ✅ 所有 skeleton 使用一致的 shimmer 动画
6. ✅ 骨架屏与真实数据间的过渡平滑，无闪烁
