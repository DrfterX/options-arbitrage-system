# Plan: N 型结构 K 线浮窗标点全周期验证

## 目标

对所有活跃期货品种 × 所有周期（15m/1h/1d/1w）逐一验证 K 线浮窗的 A/B/C 四点标点是否符合上升/下降 N 型判定条件。如发现错误，修复 `_find_n_structure_forward()` 算法并回归验证。

## 当前算法分析

### 正向扫描算法（`_find_n_structure_forward`）已经正确实现了 User Directives 定义的逻辑：

1. **方向优先**：A→B 先判断 `_determine_direction` — 已做 (line 212)
2. **方向-类型一致性**：LONG→A=TROUGH, SHORT→A=PEAK — 已做 (lines 218-220)
3. **C 不破 A**：LONG: C > A, SHORT: C < A — 已做 (lines 228-231)
4. **B→C 方向一致性**：LONG: C < B, SHORT: C > B — 已做 (lines 236-239)
5. **条件 4（最新价 vs C）**在 `detect_and_save()` 中 — 已做 (lines 314-335)
6. **非重叠扫描**：找到结构后从 C+1 继续 — 已做 (line 247)

### 潜在问题区域

以下区域可能引入标点错误，需要重点验证：

| 区域 | 问题 | 影响 |
|------|------|------|
| **A/B/C 标点的价格选择** | `_find_n_structure_forward` 选的点是 swing point 的价格，swing point 的高/低点类型决定了标点是 high 还是 low | 可能 A/B/C 价格选错了价格方向 |
| **Swing point 检测** | `swing_points.py` 的 window_n（1h=3, 1d=5, 1w=2）影响哪个 K 线被识别为极值点 | 不同周期 swing point 质量不同 |
| **`_get_active_n_structure` 检查** | `shared.py` 的 4 条件过滤可能筛掉了正确的结构 | 导致浮窗无数据或显示错误结构 |
| **前端 `drawKline` 时间匹配** | `findBarForNPoint` 用时间戳最近匹配，多根同时间 K 线可能匹配错误 | 标签贴错位置 |
| **条件 4 在 detect_and_save vs _get_active_n_structure 中同时检查** | 双重检查可能冲突 | 结构状态不一致 |

## 拆解步骤

| 步骤 | 任务 | 预期耗时 | 产出物 |
|------|------|---------|--------|
| **4.1** | 编写全品种×全周期验证脚本（SQL+API 调用），批量获取所有活跃品种的 N 型结构 + K 线数据 | 20min | 验证脚本 |
| **4.2** | 运行验证，输出带时间戳和价格的 A/B/C 标点 check 报告 | 15min | 验证报告 |
| **4.3** | 分析报告：筛查 A/B/C 四点不符合判定条件的品种×周期，区分"算法错误"vs"swing point 质量不足" | 20min | 错误分析 |
| **4.4** | 如发现算法错误 → 修复 `_find_n_structure_forward` 或 `_get_active_n_structure` 或 `dynamic_restructure` | 20min | 代码修改 |
| **4.5** | 回归验证：重新运行验证脚本确认修复后所有品种×周期均正确 | 15min | 验证报告 |

### 验证方法设计

验证脚本的核心逻辑（Python，直接连 DB）：

```python
# 伪代码
for symbol in active_symbols:
    for tf in ["15m", "1h", "1d", "1w"]:
        struct = _get_active_n_structure(db, symbol, contract, tf)
        if not struct: continue
        
        dir = struct["direction"]
        a, b, c = struct["point_a_price"], struct["point_b_price"], struct["point_c_price"]
        
        # 方向检查
        if dir == "LONG":
            assert b > a, "FAIL: LONG but B≤A"
            assert c < b, "FAIL: LONG but C≥B"
            assert c > a, "FAIL: LONG but C≤A"
        elif dir == "SHORT":
            assert a > b, "FAIL: SHORT but A≤B"
            assert c > b, "FAIL: SHORT but C≤B"
            assert c < a, "FAIL: SHORT but C≥A"
        
        # 条件 4：最新价 vs C
        last_kline = get_last_kline(db, symbol, contract, tf)
        if dir == "LONG":
            assert last_kline.close > c, "FAIL: COND4 LONG"
        else:
            assert last_kline.close < c, "FAIL: COND4 SHORT"

        # 确认 A/B/C 类型匹配（A=TROUGH/PEAK）
        a_swing = get_swing_at_time(db, symbol, contract, tf, struct["point_a_time"])
        expected_a_type = "TROUGH" if dir == "LONG" else "PEAK"
        assert a_swing.point_type == expected_a_type, f"FAIL: A type mismatch"
```

## 依赖顺序

- 4.1 → 4.2 → 4.3 → 4.4 → 4.5（严格线性）
- 如 4.3 发现"无算法错误，仅 swing point 质量不足"，则跳过 4.4，直接进入 4.5 确认

## 前置条件

- `/api/klines` 每次调用自动触发 `restructure_active_for_symbol`（force_full_recalc=True），确保数据新鲜
- 验证脚本直接读 DB（绕过 API），确保原始数据准确
- 需要拿到 `_get_active_n_structure` 的调用上下文（db 连接 + symbol → contract 映射）
