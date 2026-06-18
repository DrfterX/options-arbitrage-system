# B.4 设计 Token 统一 + 微交互打磨

## 目标
对期货（金色#f0b429）、期权（紫色#a855f7）、总览页三个面板进行底层设计 token 统一，同时打磨微交互体验，提升专业交易仪表盘的精致度。

## 当前状态（已评估）

### 已存在的 CSS 设计系统
- 期货面板：`futures_dashboard.html` 内嵌 CSS 变量（`--accent: #f0b429` 金色系）
- 期权面板：`options_dashboard.html` 内嵌 CSS 变量（`--accent: #a855f7` 紫色系）
- 总览页：`portal.html` 内嵌 CSS 变量
- 每个面板有自己的 CSS 变量定义，部分重叠但不一致

### 差距分析
| 设计 Token | 期货 | 期权 | 总览 | 是否统一 |
|-----------|------|------|------|---------|
| `--accent` | #f0b429 金 | #a855f7 紫 | — | ❌ 各自定义 |
| 间距 (padding/margin) | 隐式 | 隐式 | 隐式 | ❌ 无统一间距系统 |
| 圆角 | `border-radius: 6px` | 不一 | 不一 | ❌ |
| 字体 | 隐式 fallback | 隐式 | 隐式 | ❌ 无 Token |
| 阴影 | 隐式 | 隐式 | 隐式 | ❌ |
| 数据密度切换 | 无 | 无 | 无 | ❌ 新增功能 |

### micro-interaction 差距
| 交互 | 期货 | 期权 | 总览 | 建议 |
|------|------|------|------|------|
| hover 反馈 | 有（简单） | 有（简单） | 有（简单） | 统一+增强 |
| 数字过渡动画 | 无 | 无 | 无 | 新增 |
| 数据刷新指示 | 脉冲点 | 无 | 无 | 统一 |
| 页面加载入场 | 无 | 无 | 无 | 新增 stagger |
| 切换/点击反馈 | 有 | 有 | 有 | 统一节奏 |

## 设计方案

### 设计方向（遵循 frontend-design.md）
- **Tone**: 专业交易仪表盘 — 精密、克制、数据密度高。类似 Bloomberg Terminal 现代版。
- **Typography**: 等宽字体（`font-mono`）用于数据值，标题沿用当前 sans-serif
- **Motion**: 页面加载 stagger reveal + 数据刷新数字过渡 + 统一 hover 反馈
- **Differentiation**: 保持期货金暖/期权紫冷的品牌差异，统一底层 token 变量

### 底层 Token 变量（共享 `:root`）

```css
/* 间距系统 (4px 基准) */
--space-1: 4px;  --space-2: 8px;  --space-3: 12px;
--space-4: 16px; --space-5: 24px; --space-6: 32px;

/* 圆角系统 */
--radius-sm: 4px;  --radius-md: 6px;
--radius-lg: 10px; --radius-xl: 14px;

/* 阴影层级 */
--shadow-sm: 0 1px 3px rgba(0,0,0,.3);
--shadow-md: 0 4px 12px rgba(0,0,0,.35);
--shadow-lg: 0 8px 24px rgba(0,0,0,.4);

/* 字体栈 */
--font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', 'Consolas', monospace;
--font-sans: -apple-system, 'Helvetica Neue', 'Segoe UI', Roboto, sans-serif;

/* 过渡 */
--transition-fast: 150ms ease;
--transition-normal: 250ms ease;
```

### 面板专属 Token（保持品牌差异性）
```css
/* 期货 — 金色暖调 */
.futures-theme { --accent: #f0b429; --accent-dim: #c49420; --bg-card: #1a1d23; }

/* 期权 — 紫色冷调 */
.options-theme { --accent: #a855f7; --accent-dim: #7c3aed; --bg-card: #1a1d23; }

/* 总览 — 中性蓝灰 */
.portal-theme { --accent: #60a5fa; --accent-dim: #3b82f6; }
```

## 执行步骤（分 3 个 Cycle）

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| 4.1 | 设计 token 提取 — 将共享 token 提取为 `<style id="design-tokens">` 内嵌块，应用到 portal/futures/options 三个模板 | 15min | 三个模板的 CSS 变量统一 |
| 4.2 | 数据密度切换 — 添加紧凑/舒适模式切换按钮 + localStorage 持久化 + CSS 变量联动 | 15min | 密度切换功能 |
| 4.3 | 微交互打磨 — 页面加载 stagger reveal、hover 增强、数字过渡动画 | 15min | 动画 CSS + JS |

**依赖关系**: 4.1 → 4.2 → 4.3（token 提取是后续步骤的前提）

## 当前 Cycle
**Cycle #245 — 执行 4.1：设计 token 提取**

### 具体操作
1. 将共享 token（间距/圆角/阴影/字体/过渡）提取为 `<style id="design-tokens">`
2. 每个面板只保留专属 token（`--accent` 品牌色）
3. 保持一致但简洁：不引入外部依赖，纯 CSS 变量方案

### 涉及文件
- `web/templates/dashboard.html`（信号总览）
- `web/templates/futures_dashboard.html`
- `web/templates/options_dashboard.html`
- `web/templates/portal.html`
