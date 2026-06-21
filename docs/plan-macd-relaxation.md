# MACD 轨迹容错方案 — Plan Document

> 作者: fullstack-dhh (DHH 思维模型)
> 日期: 2026-06-15
> 状态: Plan Only — 待 critic-munger 评审后进入实现

---

## 背景

P2 重构完成后，策略验证发现两个关键数据：

1. **204 个主力合约实时扫描**: Level1 MACD 通过率 0% — 腿2 通过率仅 1.8%
2. **17 个历史 N 型结构验证**: MACD 轨迹 100% 拒绝

核心瓶颈在 `_check_pivot_transition` 函数。它负责验证 N 型结构 A/B 转折点处的 MACD 颜色过渡是否匹配方向期望。当前逻辑过于严格，导致系统在历史上从未产出过任何信号。

---

## Part A — 当前逻辑的严格点清单

以下按代码执行路径逐一列出每个拒绝条件。

### 严格点 #1: 窗口锁定 3 根 K 线

- **位置**: `check_macd_trajectory` 第 356-365、376-385 行
- **代码**: `macd_before_a[-TRANSITION_WINDOW_BEFORE:]` + `macd_after_a[:TRANSITION_WINDOW_AFTER]`
- **值**: `TRANSITION_WINDOW_BEFORE = 3`, `TRANSITION_WINDOW_AFTER = 3` (settings.py 第 168-169 行)
- **问题**: `check_macd_trajectory` 根据 N 型结构时间跨度算出了动态窗口（如 30 天），然后立刻又被截断到仅 3 根 K 线。日线周期下 3 根 = 3 天，周线结构跨月甚至跨季度的 A→B 时间差在这 3 天窗口内根本看不到颜色过渡。
- **诊断数据**: 腿1 (A 点) 通过率仅 13.0%, 腿2 (B 点) 通过率仅 1.8%
- **拒绝贡献**: ~87% 的 A 点失败可直接或间接归因于窗口过小

### 严格点 #2: 转折前主体颜色必须 100% 等于期望颜色

- **位置**: `_check_pivot_transition` 第 247-248 行
- **代码**: `if dominant_before != from_color: return False`
- **问题**: `_dominant_color` 取 3 根 K 线的众数颜色，要求严格等于 `from_color`。但 MACD 过渡是渐变过程，3 根区间内可能 2RED+1BLUE（dominant=RED）但系统期望 BLUE（LONG 方向 A 点）— 立即拒绝。
- **诊断数据**: `"转折前主体RED，期望BLUE"` 是所有 LONG 方向结构腿1 失败的核心原因
- **拒绝贡献**: 极高 — 几乎所有 LONG 方向 A 点因此拒绝

### 严格点 #3: 转折后至少需要 1 根目标颜色柱体

- **位置**: `_check_pivot_transition` 第 242、250 行
- **代码**: `has_to_after = _has_color(macd_after, to_color)` — 只要没有 1 根就进入 fallback
- **问题**: 在 3 根窗口要求看到 1 根目标颜色的 MACD 柱体。但在趋势转折初期，MACD 颜色可能尚未完全切换，只有 histogram 先于颜色反转。
- **诊断数据**: 当前 fallback 有一定帮助但不够 — `"MACD仍RED且histogram未反转"` 是第二大拒绝原因
- **拒绝贡献**: 中等

### 严格点 #4: Histogram Fallback 条件不对称

- **位置**: `_check_pivot_transition` 第 262-270 行
- **代码**:
  ```python
  if to_color == COLOR_BLUE:  # SHORT → 期望动量向下
      after_trend = _trend_from_histogram(macd_after, "SHORT")
      if after_trend == "FALLING": return True
  ```
- **问题**: `_trend_from_histogram` 要求后一半数据中 positive > negative * 2 或 negative > positive * 2 才判定 RISING/FALLING。这个 2:1 阈值对 3 根窗口数据太苛刻。3 根数据分割成两半后，后半段最多 1-2 根，统计意义弱。
- **拒绝贡献**: 高 — 即使 fallback 路径也无法通过

### 严格点 #5: W 型底部完全无法处理

- **位置**: 整个 `_check_pivot_transition` 无此逻辑
- **问题**: 在底部区域（LONG 方向 A 点），MACD 常呈现 RED→BLUE→RED (W 底) 模式。系统期望 N 型结构 A 点为转折前 BLUE→转折后 RED，但实际数据在转折前 3 根内 dominant_before=RED（因刚从 BLUE 转回 RED），与期望 BLUE 矛盾。
- **诊断数据**: RB 品种 15 个 LONG 结构全部在 A 点失败，原因都是 `"转折前主体RED，期望BLUE"`
- **拒绝贡献**: 对 LONG 方向影响极大

### 严格点 #6: W 型顶部同样无法处理

- **位置**: 同上
- **问题**: 顶部区域（SHORT 方向 A 点或 LONG 方向 B 点），MACD 呈 BLUE→RED→BLUE 模式。3 根窗口恰好覆盖转折后第一次 BLUE→RED 回撤阶段，导致 dominant_before 或 histogram 不符合预期。
- **诊断数据**: SHORT 方向的 `"转折前主体BLUE，期望RED"` 和 `"MACD仍BLUE且histogram未反转"` 频发
- **拒绝贡献**: 对 SHORT 方向影响大

### 严格点 #7: 3 根窗口内 color count 信息未用于评分

- **位置**: `_check_pivot_transition` 第 251-260 行
- **问题**: 当 `has_to_after=True` 时，已统计了 before/after 各颜色计数用于描述信息，但**这些计数未用于评分**——即使 after 窗口中只有 1/3 是目标颜色，也视为完全通过。反过来也成立——即使 after 窗口中 3/3 都是目标颜色但 before 不是纯 from_color，直接拒绝。

### 各严格点对 204 合约扫描的拒绝贡献估算

基于诊断报告第 4 节的 MACD 腿通过率数据（169 个有 L1 结构的合约）：

| 严格点 | 腿影响 | 拒绝贡献 (占 169 中) | 比例 |
|--------|--------|-------------------|------|
| #1 窗口过小 | 腿1+腿2 | ≈147 次腿1失败 | ~87% |
| #2 颜色要求 100% | 腿1+腿2 | ≈55 次 A 点 LONG 失败 | ~33% |
| #5 W 型底部容缺 | 腿1 (LONG) | ≈50 次 RB/LONG 类失败 | ~30% |
| #4 Histogram 阈值 | 腿1+腿2 fallback | ≈55+73 次失败 | ~76% |
| #3 需要 1 根目标色 | 腿2 after | ≈73 次 B 点失败 | ~43% |
| #6 W 型顶部容缺 | 腿1 (SHORT)+腿2 | ≈42 次 B 点 SHORT 失败 | ~25% |

> 注：同一合约的腿1+腿2同时通过才算 Level1 MACD 通过。腿1 通过率 13%，腿2 通过率 1.8%，两者交集导致 0 次整体通过。

---

## Part B — 三种容错模式设计

### 模式 1: 严格模式 (STRICT) — 当前行为，保持不变

**配置参数**:
```python
MACD_RELAXATION = "STRICT"
TRANSITION_WINDOW_BEFORE = 3      # 固定
TRANSITION_WINDOW_AFTER = 3       # 固定
TRANSITION_COLOR_THRESHOLD = 1.0  # 100% 主体颜色匹配
TRANSITION_AFTER_REQUIRED = 1     # 至少 1 根
W_SHAPE_TOLERANCE = False
HISTOGRAM_BIAS_RATIO = 2.0        # 2:1
```

**逻辑**: 同当前代码。

### 模式 2: 中等模式 (MODERATE) — 推荐默认

#### 2a. 窗口自适应

**设计**: `check_macd_trajectory` 已计算动态窗口 `window_a/window_b` 但被随后截断。修正方案：让 `TRANSITION_WINDOW_BEFORE/AFTER` 成为**基于 N 型结构时间跨度的比例缩放**，而非固定值。

**算法伪代码**:

```python
def _compute_transition_window(
    pivot_time: int,
    leg_gap: int,         # AB 或 BC 时间间隔 (秒)
    timeframe: str,       # "1d", "15m" 等
    min_bars: int = 3,    # 最少 K 线数
    max_bars: int = 10,   # 最多 K 线数
) -> int:
    """
    根据 N 型结构腿长动态计算转折点前后读取的 K 线数量。
    
    原则: 结构跨度越大，窗口越宽（捕捉渐变色过渡）
    比例: 取腿长的 1/10，限制在 [min_bars, max_bars] 区间
    """
    # 将时间间隔换算为 K 线根数
    timeframe_seconds = {
        "3m": 180, "15m": 900, "1h": 3600,
        "1d": 86400, "1w": 604800,
    }.get(timeframe, 86400)
    
    # 腿长折合多少根 K 线
    leg_bars = leg_gap // timeframe_seconds
    
    # 动态窗口: 取腿长的 1/5, 最少 min_bars, 最多 max_bars
    window = max(min_bars, min(leg_bars // 5, max_bars))
    return window
```

**调用方式**: 在 `_check_pivot_transition` 中不再读 settings 固定值，而是由 `check_macd_trajectory` 传入动态计算的窗口大小。

**参数建议**:
- 日线周期: `min_bars=3, max_bars=10`
- 15 分钟周期: `min_bars=3, max_bars=15`
- 周跨月结构: 窗口放大到 8-10 根，约 1.5 个月的数据，可以捕捉完整颜色过渡

#### 2b. 颜色比例阈值

**设计**: 将 `dominant_before == from_color` 的硬条件改为**比例阈值**。检查转折前窗口中 `from_color` 占比是否 ≥ 阈值。

**算法伪代码**:

```python
def _color_ratio(colors: List[str], target_color: str) -> float:
    """返回 target_color 在序列中的占比。"""
    valid = [c for c in colors if c in (COLOR_RED, COLOR_BLUE)]
    if not valid:
        return 0.0
    return sum(1 for c in valid if c == target_color) / len(valid)


def _check_color_transition(
    macd_before: List[Dict],
    macd_after: List[Dict],
    from_color: str,
    to_color: str,
    before_threshold: float,   # 转折前 from_color 最低占比
    after_threshold: float,    # 转折后 to_color 最低占比
) -> Tuple[bool, str, dict]:
    """基于比例阈值的颜色过渡检查。
    
    Returns:
        (passed, detail, stats_dict)
    """
    before_colors = [r["color"] for r in macd_before]
    after_colors = [r["color"] for r in macd_after]
    
    before_ratio = _color_ratio(before_colors, from_color)
    after_ratio = _color_ratio(after_colors, to_color)
    
    stats = {
        "before_ratio": before_ratio,
        "after_ratio": after_ratio,
        "before_n": len(before_colors),
        "after_n": len(after_colors),
    }
    
    if before_ratio >= before_threshold and after_ratio >= after_threshold:
        return True, (
            f"{from_color}占{len(macd_before)}中的{before_ratio:.0%}"
            f"→{to_color}占{len(macd_after)}中的{after_ratio:.0%}"
        ), stats
    
    return False, (
        f"{from_color}占{before_ratio:.0%}(需>{before_threshold:.0%})"
        f", {to_color}占{after_ratio:.0%}(需>{after_threshold:.0%})"
    ), stats
```

**参数建议**:
- MODERATE 模式: `before_threshold=0.6`, `after_threshold=0.2`
- 即转折前 ≥60% from_color, 转折后 ≥20% to_color

#### 2c. W 型容错

**设计**: 当第一次颜色检查不通过时，启动 W 型检测逻辑：检查转折后 2 倍窗口范围内是否存在 `from_color → to_color → from_color → to_color` 模式（即两次过渡）。

**算法伪代码**:

```python
def _detect_w_shape(
    macd_before: List[Dict],
    macd_after: List[Dict],
    from_color: str,
    to_color: str,
    extended_after: Optional[List[Dict]] = None,  # 转折后 2x 窗口数据
) -> Tuple[bool, str]:
    """W 型底部/顶部容错检测。
    
    适用场景:
    - LONG A 点: 期望 BLUE→RED, 但底部出现 RED→BLUE→RED
    - SHORT B 点: 期望 BLUE→RED, 但顶部出现 RED→BLUE→RED
    
    检测方法: 在 extended_after 中找 to_color 的连续段
    """
    if not extended_after:
        return False, "无扩展数据"
    
    after_colors = [r["color"] for r in extended_after 
                    if r["color"] in (COLOR_RED, COLOR_BLUE)]
    
    if len(after_colors) < 4:
        return False, "扩展数据不足"
    
    # 检查是否有 to_color 的稳定段
    # 即: ...from_color, to_color, from_color, to_color...
    # 或者: ...from_color, [from→to 过渡], to_color...
    
    # 方法: 找最后 N 根中 to_color 占比
    lookback = min(5, len(after_colors) // 2)
    recent = after_colors[-lookback:]
    to_ratio = sum(1 for c in recent if c == to_color) / len(recent)
    
    # W 型判定: 转折后延展区间内存在 to_color 的稳定段
    if to_ratio >= 0.4:
        return True, f"W型容错: 转折后扩展窗口{lookback}根中{to_color}占{to_ratio:.0%}"
    
    return False, f"W型未确认: {to_color}仅占扩展窗口的{to_ratio:.0%}"
```

**集成到 `_check_pivot_transition`**:

```
原有路径: dominant_before check → has_to_after → fallback
新增路径: 首次失败 → W 型检测 (extended_after) → 通过/继续 → fallback
```

**参数建议**:
- `W_SHAPE_EXTEND_MULTIPLIER = 2` — 扩展窗口宽度
- `W_SHAPE_TO_RATIO = 0.4` — 扩展窗口后半段中 to_color 占比阈值

#### 2d. 累计 histogram 动量检查 (加强版 fallback)

**设计**: 当前 fallback 仅检查转折后 histogram 方向，且 2:1 阈值对 3 根窗口太严格。加强版：比较转折**前** vs **后**的 histogram 累计动量变化。

**算法伪代码**:

```python
def _histogram_momentum(
    macd_before: List[Dict],
    macd_after: List[Dict],
    direction: str,            # "LONG" / "SHORT"
    short_window: int = 3,     # 短期窗口
    long_window: int = 8,      # 长期窗口 
) -> Tuple[bool, str]:
    """基于 histogram 累计动量的方向变化检测。
    
    原理: histogram = MACD快线 - MACD慢线
    方向变化 = histogram 趋势从递增转为递减 (反之亦然)
    
    Args:
        macd_before: 转折前数据 (动态窗口, 可能 5-10 根)
        macd_after: 转折后数据
        direction: N 型结构方向
    
    Returns:
        (is_transitioning, detail)
    """
    if len(macd_before) < 2 or len(macd_after) < 2:
        return False, "数据不足"
    
    # 转折前最近 short_window 根的 histogram 均值
    before_recent = [r.get("histogram", 0) for r in macd_before[-short_window:]]
    before_mean = sum(before_recent) / max(len(before_recent), 1)
    
    # 转折后最近 short_window 根的 histogram 均值
    after_recent = [r.get("histogram", 0) for r in macd_after[-short_window:]]
    after_mean = sum(after_recent) / max(len(after_recent), 1)
    
    # 检查方向: LONG 期望 after > before (histogram 从负转正/增大)
    #           SHORT 期望 after < before (histogram 从正转负/减小)
    delta = after_mean - before_mean
    
    if direction == "LONG":
        # 预期 histogram 上升
        threshold = abs(before_mean) * 0.15 + 1.0  # 最小偏移
        if delta > threshold:
            return True, (
                f"histogram动量: {before_mean:.1f}→{after_mean:.1f}"
                f"(Δ={delta:+.1f}), 突破阈值{threshold:.1f}"
            )
        elif delta > 0:
            return False, (
                f"histogram动量: {before_mean:.1f}→{after_mean:.1f}"
                f"(Δ={delta:+.1f}), 方向正确但未达阈值"
            )
        else:
            return False, (
                f"histogram动量: {before_mean:.1f}→{after_mean:.1f}"
                f"(Δ={delta:+.1f}), 方向错误(需正向)"
            )
    else:  # SHORT
        threshold = abs(before_mean) * 0.15 + 1.0
        if delta < -threshold:
            return True, (
                f"histogram动量: {before_mean:.1f}→{after_mean:.1f}"
                f"(Δ={delta:+.1f}), 突破阈值{threshold:.1f}"
            )
        # ...对称的失败分支
```

**相比当前 fallback 的优势**:
1. 使用绝对值比较而非正负比例 — 避免 3 根窗口统计无效
2. 引入 before 数据作为基线 — 检测**增量变化**
3. 非线性阈值 — 大波动时需更大动量才通过，小波动时更敏感

### 模式 3: 宽松模式 (RELAXED) — 放弃颜色过渡，仅看 histogram 方向

**设计**: 完全跳过 `_dominant_color` 和 `_has_color` 的颜色过渡检查，仅使用加权 histogram 趋势变化判定。

**算法伪代码**:

```python
def _check_macd_trend_relaxed(
    macd_before: List[Dict],
    macd_after: List[Dict],
    from_color: str,
    to_color: str,
    leg_label: str,
) -> Tuple[bool, str]:
    """宽松模式: 仅检查 histogram 加权趋势。
    
    不再要求颜色过渡，仅检查 histogram 的累计动量方向
    是否符合 N 型结构三笔的期望。
    """
    before_hist = [r.get("histogram", 0) for r in macd_before]
    after_hist = [r.get("histogram", 0) for r in macd_after]
    
    # 对近期的 histogram 加权 (最近 K 线权重更高)
    def weighted_slope(hist: List[float]) -> float:
        """加权线性回归斜率。越近权重越大。"""
        n = len(hist)
        if n < 3:
            # 数据不足时直接看最后 - 最前
            return hist[-1] - hist[0] if n >= 2 else 0
        
        weights = [(i + 1) / n for i in range(n)]  # 线性递增权重
        weighted_x = sum(i * w for i, w in enumerate(weights))
        weighted_y = sum(v * w for v, w in zip(hist, weights))
        weighted_xx = sum(i * i * w for i, w in enumerate(weights))
        weighted_xy = sum(i * v * w for i, (v, w) in enumerate(zip(hist, weights)))
        
        denom = weighted_xx - weighted_x * weighted_x / sum(weights)
        if abs(denom) < 1e-10:
            return 0
        return (weighted_xy - weighted_x * weighted_y / sum(weights)) / denom * n
    
    before_slope = weighted_slope(before_hist)
    after_slope = weighted_slope(after_hist)
    
    before_mean = sum(before_hist) / max(len(before_hist), 1)
    after_mean = sum(after_hist) / max(len(after_hist), 1)
    
    # 判断方向变化
    # N 型 LONG (正N): A 点应看到从负趋势转为正趋势
    #                   B 点应看到从正趋势转为负趋势
    # C 点的弱化: 趋势斜率变缓或反转
    
    # A 点 (底部): histogram 从负/下降转为上升
    # B 点 (顶部): histogram 从正/上升转为下降
    
    # 斜率变化方向
    slope_delta = after_slope - before_slope
    
    # 均值变化方向
    mean_delta = after_mean - before_mean
    
    # 方向判定 (与 N 型方向无关 — 仅与是 A 点还是 B 点有关)
    # 这里简化: 通过 from/to 颜色推断是 A 点还是 B 点
    # A 点: from=BLUE,to=RED (LONG) 或 from=RED,to=BLUE (SHORT)
    # B 点: from=RED,to=BLUE (LONG) 或 from=BLUE,to=RED (SHORT)
    
    is_peak = (from_color == COLOR_RED and to_color == COLOR_BLUE)  # 顶部转折
    is_valley = (from_color == COLOR_BLUE and to_color == COLOR_RED)  # 底部转折
    
    if is_valley:
        # 底部: 期望斜率从负转正, histogram 从下降转上升
        direction_match = (slope_delta > 0) or (mean_delta > 0)
    elif is_peak:
        # 顶部: 期望斜率从正转负, histogram 从上升转下降
        direction_match = (slope_delta < 0) or (mean_delta < 0)
    else:
        direction_match = False
    
    if direction_match:
        return True, (
            f"宽松: before斜率{before_slope:.1f}→after斜率{after_slope:.1f}"
            f" (Δ={slope_delta:+.1f}), before均值{before_mean:.1f}→{after_mean:.1f}"
        )
    
    return False, (
        f"宽松未通过: before斜率{before_slope:.1f}→after斜率{after_slope:.1f}"
        f" (Δ={slope_delta:+.1f}), 期望{'↑' if is_valley else '↓'}"
    )
```

**关键差异**: 不依赖 MACD 颜色红/蓝分类，只依赖 histogram 这个 **连续值**。histogram 方向变化比颜色变化提前数个 K 线，且不存在"颜色边界"的阶梯函数问题。

---

### 模式切换架构

在 `settings.py` 中新增配置:

```python
# ============================================================
# MACD 轨迹容错模式
# ============================================================
MACD_RELAXATION_MODE = "MODERATE"     # "STRICT" | "MODERATE" | "RELAXED"

# 中等模式参数
MACD_MODERATE_PARAMS = {
    "transition_min_bars": 3,
    "transition_max_bars_before": 10,      # 取决于周期
    "transition_max_bars_after": 15,
    "before_color_threshold": 0.60,        # 转折前 from_color 最低占比
    "after_color_threshold": 0.20,         # 转折后 to_color 最低占比
    "w_shape_enabled": True,
    "w_shape_extend_multiplier": 2,
    "w_shape_to_ratio": 0.40,
    "histogram_momentum_threshold": 0.15,  # 动量阈值 (比值)
    "histogram_min_abs_threshold": 1.0,    # 最小绝对阈值
}

# 宽松模式参数
MACD_RELAXED_PARAMS = {
    "histogram_window_before": 5,
    "histogram_window_after": 5,
    "weighted_slope_threshold": 0.0,
}
```

在 `color_tracker.py` 中 `_check_pivot_transition` 内部:

```python
def _check_pivot_transition(
    macd_before: List[Dict],
    macd_after: List[Dict],
    from_color: str,
    to_color: str,
    leg_label: str,
    extended_after: Optional[List[Dict]] = None,   # 新增: 扩展窗口
    mode: str = "MODERATE",
) -> Tuple[bool, str]:
    
    if mode == "RELAXED":
        return _check_macd_trend_relaxed(macd_before, macd_after, from_color, to_color, leg_label)
    
    # STRICT 或 MODERATE: 先做颜色过渡检查
    if mode == "MODERATE":
        threshold = settings.MACD_MODERATE_PARAMS["before_color_threshold"]
        # 使用比例阈值检查...
        passed, detail, stats = _check_color_transition(...)
        if passed:
            return True, detail
        
        # MODERATE 模式: W 型容错
        if w_shape_enabled and extended_after:
            w_passed, w_detail = _detect_w_shape(macd_before, macd_after, from_color, to_color, extended_after)
            if w_passed:
                return True, w_detail
        
        # MODERATE 模式: histogram 动量检查 (加强版 fallback)
        momentum_passed, momentum_detail = _histogram_momentum(macd_before, macd_after, direction)
        if momentum_passed:
            return True, momentum_detail
        
        return False, f"MODERATE模式全部失败: {detail}"
    
    # STRICT: 当前逻辑不变
    ...
```

---

## Part C — 每种的收益/风险分析

### 模式 1: 严格模式 (STRICT)

| 指标 | 估算值 | 依据 |
|------|--------|------|
| Level1 MACD 通过率 | 0/169 (0%) | 当前扫描数据 |
| 预计历史信号通过 | 0/17 (0%) | 当前验证数据 |
| 假信号风险 | 极低 | 未改变 |
| 适用场景 | 已实盘盈利需收紧 | 当前不存在此场景 |

**结论**: 当前模式不可用。不产生任何信号 = 系统不是"保守"而是"死亡"。

---

### 模式 2: 中等模式 (MODERATE)

**预期信号提升**:

| 改善点 | 当前通过率 | 预计提高到 | 计算逻辑 |
|--------|-----------|-----------|---------|
| 窗口自适应 (3→8根) | 腿1: 13.0% | → ~35% | 3根窗口内看到颜色过渡的概率约 13%；扩大后用比例阈值可覆盖更多渐变情况 |
| 颜色比例阈值 (100%→60%) | 腿1: 13.0% | → ~40% | `"转折前主体RED，期望BLUE"` 类失败中至少有 60% 来自比例不达标但接近的情况 |
| W 型容错 | 腿1 LONG: ~0% | → ~25% | RB 等 LONG 方向的 W 底结构可被捕捉 |
| histogram 加强动量 | 当前 fallback 约 50% 挽救率 | → ~70% | 比较 before/after 累计动量的方法比纯 after 方向判断更敏感 |

**腿通过率预估**:

| 腿 | 当前 | MODERATE 预估 |
|----|------|-------------|
| 腿1 (A 点) | 13.0% (22/169) | 30-40% (51-68/169) |
| 腿2 (B 点) | 1.8% (3/169) | 15-25% (25-42/169) |
| 腿3 (C 点弱化) | 71.6% | 不变 (这部分已足够好) |

**Level1 整体通过率预估**: 腿1 ∩ 腿2 = 30-40% × 15-25% = **4.5-10%** (当前 0%)

对应 169 个有 L1 结构的合约: **8-17 个通过 L1**
按梯度策略 (L1+L2 → ENTRY): 过滤出小时线 N 型方向匹配的 ≈ 30-40%，预计 **2-6 个信号**

**假信号风险**:

| 风险因素 | 评估 | 缓解 |
|---------|------|------|
| 窗口扩大引入噪声 | 低-中 | max_bars 上限限制 (10根/15根) + 比例阈值下限 (60%) 提供安全垫 |
| 比例阈值 60% 可能接受纯噪声信号 | 低 | 60% 意味着 8 根窗口中有 ≥5 根 from_color, 统计显著 |
| W 型容错误判 | 中 | 需要在扩展窗口中 to_color 稳定占比 ≥40% 才判定 |
| Histogram 动量 false positive | 低-中 | baseline 阈值 (abs(before_mean) * 0.15 + 1.0) 避免小波动通过 |

**参数可调性**:

| 参数 | 调节方向 | 效果 |
|------|---------|------|
| `before_color_threshold` | 0.50-0.80 | 低=更宽松, 高=更严格 |
| `after_color_threshold` | 0.10-0.40 | 低=更容易接受过渡 |
| `transition_max_bars_before` | 5-15 | 大=看得更远, 但噪声更多 |
| `w_shape_to_ratio` | 0.30-0.60 | 低=容易接受 W 型, 高=更难 |
| `histogram_momentum_threshold` | 0.05-0.30 | 低=灵敏, 高=迟钝 |

**建议默认**: `before_threshold=0.60, after_threshold=0.20, max_bars=10, w_ratio=0.40`

---

### 模式 3: 宽松模式 (RELAXED)

**预期信号提升**:

| 腿 | MODERATE | RELAXED 预估 |
|----|---------|-------------|
| 腿1 (A 点) | 30-40% | 60-80% |
| 腿2 (B 点) | 15-25% | 40-60% |
| Level1 整体 | 4.5-10% | 24-48% |

对应 169 合约: **40-80 个通过 L1** → L2 过滤后估计 **12-32 个信号**

**假信号风险**:

| 风险因素 | 评估 | 说明 |
|---------|------|------|
| 放弃颜色约束 = 放弃核心信号逻辑 | **高** | 系统设计原文"没有MACD的红蓝变化配合的K线结构，是不稳定的结构" — RELAXED 模式直接违背此原则 |
| Histogram 斜率 + 均值双重检查仍可能导致方向判断错误 | 中-高 | 趋势背景强时 histogram 的任何小幅波动都会产生方向信号 |
| 假阳性信号比例可能接近 70% | 中-高 | 宽松模式下通过大量无效 N 型结构，回测验证必须严格 |

**适用场景**: 仅在 MODERATE 模式仍然信号不足且 CEO 明确批准的情况下考虑。

**参数可调性**: 极高 — `window_before/after`、`weight_scheme`、`slope_threshold` 全部可调。

---

### 推荐方案

```
选择: MODERATE 模式

理由:
1. 保留颜色过渡作为核心信号逻辑 — 不违背原始设计原则
2. 通过比例阈值 + W 型容错 + 增强动量检查，预期提升 L1 通过率到 5-10%
3. 参数分级的三个层次递进放松:
   Level 1: 扩大窗口 (最安全，仅影响数据量不影响逻辑)
   Level 2: 比例阈值 (适度放松，有统计基础)
   Level 3: W 型 + histogram 动量 (最宽松，但保留颜色检查作为前提)
4. 所有参数在 settings.py 中统一配置，可实盘调优
```

---

---
## Munger 评审意见

**评审者:** Charlie Munger (Critic)
**评审对象:** MACD 轨迹容错方案（Plan Document）
**前置依赖:** [Pre-Mortem: P0 信号系统三方向选择](docs/critic/p0_signal_premortem.md)

---

### ⚠️ 前置声明：我正在否决我自己的警告

在 P0 Pre-Mortem 中，我写过这样一段话：

> **选项 B（适度放宽）最危险。** 它是唯一一个让你在没有新增信息的情况下持续做出决策的选项。它在调一个没有数据支撑的阈值，每次调整都是"猜测 — 验证 — 再猜测"的无限循环。**B 是不可证伪的——任何结果都可以归因为"阈值还没调对"。B 是虚假的精确。这是最危险的。**

现在这份 Plan Document 正是 **选项 B**。

这样一来，我的立场就很尴尬了：要么坚持原来的否决，让系统继续零信号；要么承认情况变了，需要重新评估。我选择后者——但附加硬性条件。

---

### 致命缺陷

#### 缺陷 #1：Plan B 本质上是"用参数替换硬编码"——这不是放松，是换一种方式严格

当前 MACD 轨迹检查的问题在于：**TRANSITION_WINDOW_BEFORE/AFTER = 3 根 K 线让动态窗口计算变得毫无意义**。这是一个 bug，不是设计选择——你在第 331-347 行花了 17 行计算基于 N 型结构跨度的动态窗口（比如 30 天），然后在第 356-365 行用 2 行截断到 3 天。**87% 的腿 1 失败直接源于这个截断。**

修复这个 bug（让窗口大小与 N 型结构跨度成正比）本身就是完整的"修正方案"，不需要引入比例阈值、W 型容错、histogram 动量等 9 个可调参数。

**结论：真正的问题是 bug，不是设计缺陷。修复 bug 就够了。Plan 给出的 3 种模式 × 9 个参数是对一个简单 bug 的过度工程化响应。**

#### 缺陷 #2：W 型容错 = 在震荡市接受假信号

W 型（RED→BLUE→RED→BLUE）出现的时候，意味着 MACD **根本没有决定方向**。底部反复、顶部反复——这是典型的区间震荡特征。震荡市中趋势跟踪系统的预期胜率 < 50%。

如果 W 型通过，以下场景会出现假信号：
1. 市场在底部区域反复（MACD RED→BLUE→RED→BLUE→RED），系统认为"底部确认"入场做多，然后市场继续下跌
2. 顶部区域类似：系统认为"顶部确认"入场做空，然后市场继续上涨

DHH 的设计者说 "在底部区域 MACD 常呈现 W 底模式"——这句话是对的。但正是因为它"常呈现 W 底"，说明它不是一个可靠的信号。

**W 型容错应该在另一种条件下启用：反向验证。即最终一次过渡是目标方向且有数据支持，而不是简单地在扩展窗口内找 to_color 占比 ≥ 40%。**

#### 缺陷 #3：RELAXED 模式违背了系统原始设计原则

原始笔记白纸黑字：

> "没有 MACD 的红蓝变化配合的 K 线结构，是不稳定的结构……即使出现结构突破，也视为无效信号。"

P2 重构（GAP #4）专门将 MACD 恢复为阻断性条件。现在 RELAXED 模式完全放弃颜色检查，只靠 histogram 斜率。

**histogram 斜率是一个 MACD 计算的中间值**——它比颜色变化灵敏，但也比颜色变化更嘈杂。用加权线性回归的斜率值决定信号是否通过，等于把信号系统建立在一个嘈杂的派生指标上。

而且，加权线性回归的参数（权重方案、窗口大小、斜率阈值）**没有一个基于任何市场数据**。每个都是猜测值。

#### 缺陷 #4：三种模式 + 9 个参数 = 不可证伪的迭代陷阱

| 参数 | 建议值 | 可调范围 | 调优依据？ |
|------|--------|---------|----------|
| before_color_threshold | 0.60 | 0.50-0.80 | 纯猜测 |
| after_color_threshold | 0.20 | 0.10-0.40 | 纯猜测 |
| transition_max_bars_before | 10 | 5-15 | 纯猜测 |
| w_shape_to_ratio | 0.40 | 0.30-0.60 | 纯猜测 |
| histogram_momentum_threshold | 0.15 | 0.05-0.30 | 纯猜测 |
| histogram_min_abs_threshold | 1.0 | 未说明 | 纯猜测 |

**9 个参数 × 每个参数 5 种取值 = 约 200 万种组合。** 回测一次 15 分钟，全部回完需要 5,700 天。没有人会这样做——实际操作中会在 3-5 次调整后找到一个"看起来不错"的组合。

这正是我在 Pre-Mortem 中警告的："**无法证伪的迭代陷阱——阈值越调越细（"试试 0.7 而不是 0.5"），每次都有理由、每次都无法确认是否真的改善。这是量化系统最常见的死法。**"

#### 缺陷 #5：模式选择权交给用户 = 责任转移

> "用户可选择严格/中等/宽松模式"

在实际交易中：
- 用户选了 STRICT → 0 信号 → 用户骂系统没用
- 用户选了 MODERATE → 偶尔有信号 → 用户会想"如果 RECLAXED 会不会更好？"
- 用户最终一定切换到 RELAXED

**把模式选择交给用户，等于说"我们的系统不能自动判断该用哪个模式"。** 这不是用户的选择，是系统设计者的放弃。

合理的做法：**系统基于市场状态自动选择模式**。高波动 + 趋势明确 → 可用 RELAXED；低波动 + 震荡 → 必须 STRICT。

---

### 容放过宽的后果

#### 1. 历史 0 信号并不代表 MACD 太严格

可能的原因（未被排除）：
- N 型结构检测本身的质量问题——如果 N 型结构的方向判断与 MACD 方向不一致，MACD 只是做了分内的事
- 历史时间点选择偏差——17 个时间点是否足够代表所有市场状况？
- RB 单一品种偏差——204 合约扫描中 RB 的结构占比多少？

结论：**在排除 N 型结构本身的问题之前，不能断定 MACD 是唯一的瓶颈。**

#### 2. 信号密度增加 = 胜率稀释

原始数据：
- STRICT 下的 2 分信号：40 条历史，60.9% 胜率
- MODERATE 预估 L1 通过率提升 5-10%
- L1+L2 预估通过率：2-6 个信号/扫描

但这些新通过的信号是 STRICT 过滤掉的低质量信号。它们的真实胜率未知。如果新信号的胜率只有 45-50%（因为 W 型容错放进来了震荡市信号），**混合胜率会迅速跌破 57% 盈亏平衡线**。

简单的贝叶斯计算：
- 假设 STRICT 信号: 100 个 × 60.9% = 61 胜
- MODERATE 新增: 假设 50 个 × 48% = 24 胜（保守估计）
- 混合: 150 个, 85 胜 = **56.7% — 低于 57% 盈亏平衡线**

这意味着 MODERATE 模式下的梯度策略（CEO 裁定的 L1+L2 → ENTRY）**可能无法达到新的 57% 的盈亏平衡要求**。

#### 3. W 型容错在震荡市的假信号率

回测场景：某品种在 2000-2200 区间震荡 3 个月，MACD 频繁 RED↔BLUE 切换约 10 次。
- MODERATE 模式开启 W 型容错
- 每一次 RED→BLUE→RED→BLUE 序列 W 型判定通过
- 在 3 个月震荡期内，可能产生 8-12 个假信号
- 每个假信号损失 1%（总资本的 1% 风险敞口）
- 3 个月累计损失 8-12%
- 然后一个真信号来了，盈利 3-5%（结构止盈天然 1:10+）

**即使有超大的盈亏比，8 个亏损信号对一个盈利信号也是毁灭性的。**

---

### 不可放松的底线

#### 底线 #1：方向一致性 — MACD 与 N 型结构的趋势方向必须一致

- LONG 信号：MACD 不能整体偏蓝（空头）。允许 RED 比例略低于 100%，但不能 RED < BLUE
- SHORT 信号：MACD 不能整体偏红（多头）。允许 BLUE 比例略低于 100%，但不能 BLUE < RED

**绝对不可接受**: RELAXED 模式的 histogram-only 检查。失去了颜色方向约束就等于失去了 N 型结构的 MACD 验证。

#### 底线 #2：第 1 腿（A 点过渡）的 direction 检查不能放松

A 点是 N 型结构的方向定调。如果 A 点的 MACD 过渡方向错误（比如 LONG 结构下 A 点前后都是 RED = 多头），整个结构的方向判断就是错误的。

允许放松：窗口扩大、比例阈值从 100% → 60%（在正确方向内）
绝对禁止：放弃方向检查、允许 histogram-only 替代

#### 底线 #3：第 3 腿（C 点弱化）应该保持当前逻辑

目前腿 3 的通过率是 71.6%，已经很好。不要动。

#### 底线 #4：3 分钟稳定性检查保持原样

Level3 的 `check_3m_stability` 是最后一层安全网。它默认 `LEVEL3_STABILITY_MAX_SWITCHES = 3`（切换次数 ≤ 3），已经不算严格了。**这个不动。**

#### 底线 #5：评分重置机制不因 MACD 放松而改变

如果 MACD 放松后，评分重置的标准也随之放松，等于打开了"进来容易、出去也容易"的双重泄洪闸。评分重置仍然应该基于严格的价格突破 + MACD 颜色翻转。

---

### 结论：CONDITIONAL GO

**评审结果: CONDITIONAL GO — 但需要剥离方案中的危险部分。**

#### ✅ 批准的部分

**修复动态窗口截断 bug** — 这是真正的瓶颈，也是唯一不妥协的改进

具体操作：
1. 删除 `_check_pivot_transition` 中的 `TRANSITION_WINDOW_BEFORE/AFTER` 截断
2. 将 `check_macd_trajectory` 计算出的动态窗口（`window_a/window_b`）直接作为 K 线数量传入
3. 保持 `dominant_before == from_color` 的硬条件不变——窗口扩大后，这个问题自然缓解
4. 保持 histogram fallback 不变——窗口扩大后 2:1 阈值不再苛刻

预期效果：仅通过修复窗口 bug，腿 1 通过率从 13% 提升至约 30-35%（动态窗口 8-10 根 vs 当前 3 根的 2-3x 数据量）。

#### ❌ 拒绝/需修改的部分

| 项目 | 裁决 | 理由 |
|------|------|------|
| W 型容错 | **拒绝** | 震荡市假信号风险不可接受。W 型 = 方向不确定 |
| RELAXED 模式 | **拒绝** | 违反原始设计。放弃颜色检查 = 放弃 MACD 验证核心逻辑 |
| 三模式用户可选 | **修改** | 改为自动模式（市场状态驱动），或默认只用修复版 STRICT |
| 比例阈值 60% | **有条件批准** | 前提：必须先确认"转折前主体≠from_color"中有多少是因为 3 根窗口不够。修复窗口后测一次，如果还不行再考虑降到 80% |
| histogram 动量加强 | **有条件批准** | 可以作为 fallback 保留，但阈值必须基于负样本校准，不能凭感觉设 0.15 |
| after_color_threshold = 0.20 | **修改为 0.33** | 窗口扩大后 10 根 K 线中有 3+ 根目标颜色才合理。20% (=2/10) 统计意义太弱 |

#### 执行建议

**Step 1: 只修窗口 bug（1 小时）**
```python
# 改动位置: color_tracker.py, _check_pivot_transition 和 check_macd_trajectory
# 改动内容: 动态窗口不再被 TRANSITION_WINDOW_BEFORE/AFTER 截断
# 保留: 所有当前逻辑不变，包括 dominant_color 硬条件、histogram 2:1 阈值
```

**Step 2: 回测验证（15 分钟）**
如果修复后 L1 通过率 ≥ 5%（即 169 中 ≥ 8 个），**保持 STRICT 模式上线**，不需要进一步放松。

**Step 3: 仅当修复后仍 < 5% 时，才考虑比例阈值（1 小时）**
从 `before_color_threshold = 0.80` 开始，逐步测试。**绝对不碰 W 型和 RELAXED。**

**Step 4: 100 笔实验的监控指标增加一项**
除了滚动胜率外，跟踪新 MACD 参数带来的**新增信号的平均胜率**。如果新增信号的胜率 < 45%，说明放进来的是噪声，立即回退。

---

**最后一句：** 一个好的交易系统就像一把狙击枪——宁可不开枪，也不要打偏。修复窗口 bug 能让枪的瞄准镜从"看不见靶子"变成"看得清靶子"。而 W 型容错和 RELAXED 模式等于给狙击枪装了个霰弹枪管——你会打到更多东西，但大部分是鸟，不是目标。

当前 `check_macd_trajectory` 第 331-347 行已有动态窗口计算逻辑:

```python
ab_gap = abs(b_time - a_time)          # AB 时间间隔
bc_gap = abs(c_time - b_time)          # BC 时间间隔

window_a = min(ab_gap // 3, 86400 * 30)
window_b = min(min(ab_gap, bc_gap) // 3, 86400 * 15)
window_c = min(bc_gap // 3, 86400 * 30)
```

但第 356-365 行立刻将数据截断到 `TRANSITION_WINDOW_BEFORE/AFTER = 3` 根。

**问题**: 日线周期下 `window_a` 可能是 30 天 (30 根 K 线)，但收缩到 3 根后丢失了 90% 的数据。

**修正**: 不再截断 — 将动态窗口计算的 K 线数直接传入 `_check_pivot_transition`。