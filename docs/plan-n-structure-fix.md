# Plan: N 型结构算法 — 完整审计与修复状态 (Cycle #250)

## 结论先行

**P0 N 型算法修复已全部完成。** 代码已验证实现 User Directives 中定义的全部 4 条判定条件。88 个测试全部通过。**无需额外代码改动。**

---

## 一、算法与 User Directives 逐条对照

### 上升 N 型判定

| # | 条件 | User Directives 要求 | 代码位置 | 状态 |
|---|------|---------------------|---------|:----:|
| 1 | B > A（第一笔上涨） | B 点价格 > A 点价格 | `_determine_direction()` → `n_structure.py:56` | ✅ |
| 2 | C < B（第二笔下跌） | C 点价格 < B 点价格 | `_find_n_structure_forward()` → `n_structure.py:236-237` | ✅ 显式检查 |
| 3 | C > A（C 不破 A） | C 点价格 > A 点价格 | `_find_n_structure_forward()` → `n_structure.py:228-229` | ✅ |
| 4 | 最新价 > C（第三笔向上） | 最新价 > C 点价格 | `detect_and_save()` → `n_structure.py:318-320`<br>`_get_active_n_structure()` → `shared.py:101-103` | ✅ |
| 5 | 方向-点类型一致性 | LONG → A=TROUGH | `_find_n_structure_forward()` → `n_structure.py:218-220` | ✅ |

### 下降 N 型判定

| # | 条件 | User Directives 要求 | 代码位置 | 状态 |
|---|------|---------------------|---------|:----:|
| 1 | A > B（第一笔下跌） | A 点价格 > B 点价格 | `_determine_direction()` → `n_structure.py:56-58` | ✅ |
| 2 | C > B（第二笔上涨） | C 点价格 > B 点价格 | `_find_n_structure_forward()` → `n_structure.py:238-239` | ✅ 显式检查 |
| 3 | C < A（C 不高于 A） | C 点价格 < A 点价格 | `_find_n_structure_forward()` → `n_structure.py:230-231` | ✅ |
| 4 | 最新价 < C（第三笔向下） | 最新价 < C 点价格 | `detect_and_save()` → `n_structure.py:325-330`<br>`_get_active_n_structure()` → `shared.py:104-105` | ✅ |
| 5 | 方向-点类型一致性 | SHORT → A=PEAK | `_find_n_structure_forward()` → `n_structure.py:218-220` | ✅ |

---

## 二、完整实现链（算法 → DB → API → 前端渲染）

### 2.1 核心检测引擎：`futures/n_structure.py`

| 函数 | 职责 | 状态 |
|------|------|:----:|
| `_determine_direction()` | 方向判定（B>A→LONG, B<A→SHORT） | ✅ |
| `_merge_same_type()` | 合并连续同向极值点，保留最极端值 | ✅ |
| `_find_n_structure_forward()` | **核心：前向非重叠扫描**，满足全部 4 条件 + 方向-类型一致性 | ✅ |
| `detect_and_save()` | 全量检测 + 条件 4 确认 + DB 写入 | ✅ |
| `dynamic_restructure()` | A 突破迁移 / B 反穿 COMPLETED / C 滑动 | ✅ |
| `_update_c_point()` | C 点滑动更新（不突破 A 前提下） | ✅ |
| `restructure_all_active()` | 遍历所有活跃结构逐个重算 | ✅ |

### 2.2 结构有效性校验：`futures/shared.py`

| 检查项 | 实现 | 状态 |
|--------|------|:----:|
| 时间新鲜度 | FRESHNESS 窗口检查 | ✅ |
| C 不破 A | `c_price <= a_price` (LONG) → None | ✅ |
| 极端止损 | 最新收盘突破 A → None | ✅ |
| **条件 4（第三笔方向）** | latest_close vs c_price，`skip_condition4` 参数控制 | ✅ |

### 2.3 前端渲染：`web/templates/futures_dashboard.html`

| 功能 | 实现 | 状态 |
|------|------|:----:|
| `drawKline()` | Canvas 绘制 ABC 端点 + 连线 + 价格标签 | ✅ |
| 线段 A→B, B→C | 实线连接，颜色区分（黄/紫/粉） | ✅ |
| C→最新价第三笔方向 | 实线 + 箭头，LONG 红色 / SHORT 绿色 | ✅ |
| 60s 自动刷新 | N 型数据随 API 重请求自动更新 | ✅ |
| 价格标签 | A/B/C 价格标注在端点上方 | ✅ |

---

## 三、测试覆盖

| 测试文件 | 用例数 | 覆盖内容 | 状态 |
|---------|:------:|---------|:----:|
| `test_n_structure.py` | 55 | 方向判定、4 条件检查、向前扫描、连续趋势防护、橡胶案例、条件 4 | ✅ |
| `test_dynamic_restructure.py` | 23 | A 突破迁移、B 反穿、C 滑动、多周期 | ✅ |
| `test_integration_n_structure.py` | 10 | 端到端：数据写入 → 结构检测 → 动态重算 | ✅ |
| **总计** | **88** | | **✅ 全部通过** |

---

## 四、核心算法流程图（简化）

```
极值点序列 → merge_same_type → 前向非重叠扫描
    │
    for each A (merged[i]):
        for each B (merged[j], j>i, type≠A.type):
            direction = _determine_direction(A.price, B.price)
            # 方向-类型一致性校验
            if (LONG and A≠TROUGH) or (SHORT and A≠PEAK): continue
            for each C (merged[k], k>j, type=A.type):
                # 检查 C 不破 A
                # 检查 B→C 方向（LONG: C<B, SHORT: C>B）
                # 找到有效结构 → 非重叠跳转
    │
    ↓ (找到结构)
    condition 4 检查: 最新价 vs C 点
    │
    ↓ (通过)
    DB 写入 + API 返回
```

---

## 五、P0 剩余事项

| 事项 | 严重度 | 说明 |
|------|:-----:|------|
| User Directives 清理 | 文档 | P0 算法已修复验证，User Directives 中"当前算法错误"描述需人类确认移除 |
| `_determine_direction()` A==B 边界 | 🔷 Low | A.price==B.price 时返回 LONG 默认值，概率极低，后备逻辑优雅降级，不阻至 |

---

## 六、结论

**P0 全部完成。** 代码已实现 User Directives 的全部 4 条判定条件 + 方向-类型一致性校验。88 个测试通过。前端渲染正确。

建议 Next Action：**关闭 P0**，进入下一方向（等待社区反馈 / 雪球发布 / 新功能开发 / 功能优化）。
