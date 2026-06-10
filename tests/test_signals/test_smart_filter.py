"""
智能信号过滤层 SmartFilter 测试。

覆盖 5 条核心过滤规则 + 4 个边界条件 + 1 个批量处理测试。
"""

import pytest
from typing import Any

from signals.smart_filter import FilterDecision, SmartFilter


# ─── 在每个测试前创建新的 SmartFilter 实例 ──────────────

def make_filter() -> SmartFilter:
    """返回一个干净的 SmartFilter 实例。"""
    return SmartFilter()


# ── Rule 1: L1+L2 验证通过 → 始终推送 HIGH ──────────────

class TestRule1L1L2Pass:
    """Rule 1: L1+L2 验证通过 → 始终推送 HIGH。"""

    def test_rb_l1_l2_pass(self) -> None:
        """RB 品种 L1+L2 通过 → HIGH。"""
        f = make_filter()
        d = f.evaluate("RB", score=0.5, level1_pass=True, level2_pass=True)
        assert d.should_push is True
        assert d.push_level == "HIGH"
        assert "96.6%" in d.reason
        assert d.confidence == 96.6

    def test_oi_l1_l2_pass(self) -> None:
        """OI 品种即使准确率 2.9%，L1+L2 通过也应当推送 HIGH。"""
        f = make_filter()
        d = f.evaluate("OI", score=0.5, level1_pass=True, level2_pass=True)
        assert d.should_push is True
        assert d.push_level == "HIGH"
        assert d.confidence == 96.6

    def test_sa_l1_l2_pass(self) -> None:
        """SA 品种即使准确率 28.8%，L1+L2 通过也应当推送 HIGH。"""
        f = make_filter()
        d = f.evaluate("SA", score=0.5, level1_pass=True, level2_pass=True)
        assert d.should_push is True
        assert d.push_level == "HIGH"

    def test_l1_l2_with_l3_also_pass(self) -> None:
        """L1+L2+L3 全通过也按 L1+L2 规则处理。"""
        f = make_filter()
        d = f.evaluate("RB", score=0.8, level1_pass=True, level2_pass=True, level3_pass=True)
        assert d.should_push is True
        assert d.push_level == "HIGH"

    def test_only_l1_pass_not_rule1(self) -> None:
        """只有 L1 → 不触发规则 1，进入后续规则。
        RB 准确率 100% + 评分 0.5 < 0.60 → NORMAL（准确率≥60% 规则）。"""
        f = make_filter()
        d = f.evaluate("RB", score=0.5, level1_pass=True, level2_pass=False)
        assert d.should_push is True
        assert d.push_level == "NORMAL"


# ── Rule 2 + 3: 品种准确率过滤 ──────────────────────────

class TestRule2and3AccuracyFilter:
    """Rule 2: 高信度 ≥80% → 正常推送。
       Rule 3: 低信度 <40% → 抑制。"""

    def test_rb_100_percent(self):
        """RB 准确率 100% → 高评分推 HIGH。"""
        f = make_filter()
        d = f.evaluate("RB", score=0.7, level1_pass=False, level2_pass=False)
        assert d.should_push is True
        assert d.push_level == "HIGH"
        assert d.confidence >= 80.0

    def test_ta_846_percent(self):
        """TA 准确率 84.6%，评分高 → HIGH。"""
        f = make_filter()
        d = f.evaluate("TA", score=0.65, level1_pass=False, level2_pass=False)
        assert d.should_push is True
        assert d.push_level == "HIGH"

    def test_p_942_percent_low_score(self):
        """P 准确率 94.2%，但评分 < 0.60 → NORMAL（非 HIGH）。"""
        f = make_filter()
        d = f.evaluate("P", score=0.4, level1_pass=False, level2_pass=False)
        assert d.should_push is True
        # 准确率 ≥60%，评分 <0.60 → NORMAL
        assert d.push_level == "NORMAL"

    def test_oi_29_percent_suppressed(self):
        """OI 准确率 2.9% < 40% → 抑制。"""
        f = make_filter()
        d = f.evaluate("OI", score=0.5, level1_pass=False, level2_pass=False)
        assert d.should_push is False
        assert d.push_level == "SUPPRESS"

    def test_cf_154_percent_suppressed(self):
        """CF 准确率 15.4% < 40% → 抑制。"""
        f = make_filter()
        d = f.evaluate("CF", score=0.5, level1_pass=False, level2_pass=False)
        assert d.should_push is False
        assert d.push_level == "SUPPRESS"

    def test_sa_288_percent_suppressed(self):
        """SA 准确率 28.8% < 40% → 抑制。"""
        f = make_filter()
        d = f.evaluate("SA", score=0.5, level1_pass=False, level2_pass=False)
        assert d.should_push is False
        assert d.push_level == "SUPPRESS"


# ── Rule 4: 高评分加权 ──────────────────────────────────

class TestRule4HighScore:
    """Rule 4: 评分 ≥ 0.60 提高优先级。"""

    def test_mid_accuracy_high_score(self):
        """中等信度品种 + 高评分 → NORMAL。"""
        f = make_filter()
        d = f.evaluate("CU", score=0.7, level1_pass=False, level2_pass=False)
        # CU 准确率 68.3%, ≥80%? No. 评分 ≥0.60? Yes → NORMAL
        assert d.should_push is True
        assert d.push_level == "NORMAL"

    def test_low_score_low_accuracy(self):
        """低评分 + 低于 60% 信度 → 抑制。"""
        f = make_filter()
        d = f.evaluate("NI", score=0.3, level1_pass=False, level2_pass=False)
        # NI 准确率 31.7% < 40% → SUPPRESS（规则 3 优先）
        assert d.should_push is False

    def test_mid_accuracy_low_score(self):
        """中等信度品种 60-80% + 低评分 → NORMAL。"""
        f = make_filter()
        d = f.evaluate("CS", score=0.3, level1_pass=False, level2_pass=False)
        # CS 准确率 68.3% >= 60% → NORMAL（规则 5）
        assert d.should_push is True
        assert d.push_level == "NORMAL"

    def test_default_accuracy_high_score(self):
        """未在表中列出的品种 + 高评分 → NORMAL。"""
        f = make_filter()
        d = f.evaluate("XX", score=0.75, level1_pass=False, level2_pass=False)
        assert d.should_push is True
        assert d.push_level == "NORMAL"


# ── Rule 5: ENTRY 信号 ──────────────────────────────────

class TestRule5EntrySignal:
    """ENTRY 信号始终推送（除非品种准确率 < 40%）。"""

    def test_ni_entry_suppressed(self):
        """NI（31.7%）ENTRY 类型：规则 3 (<40%) 优先 → 抑制。"""
        f = make_filter()
        d = f.evaluate("NI", score=0.5, level1_pass=False, level2_pass=False, signal_type="ENTRY")
        assert d.should_push is False

    def test_mid_entry_pushed(self):
        """CS（68.3%）ENTRY → NORMAL。"""
        f = make_filter()
        d = f.evaluate("CS", score=0.5, level1_pass=False, level2_pass=False, signal_type="ENTRY")
        assert d.should_push is True
        assert d.push_level == "NORMAL"

    def test_generic_signal_suppressed(self):
        """XXX 默认准确率 50% + 低评分 + 非 ENTRY → 低优先级推送。"""
        f = make_filter()
        d = f.evaluate("XX", score=0.3, level1_pass=False, level2_pass=False)
        # 有效置信度 50% * 1.0 = 50% ≥ 50% → LOW
        assert d.should_push is True
        assert d.push_level == "LOW"

    def test_unknown_very_low(self):
        """XX 默认 50% 的准确率，不开箱即用"""
        f = make_filter()
        d = f.evaluate("ZZ", score=0.1, level1_pass=False, level2_pass=False)
        # default_accuracy=50%, boost=1.0, effective=50% → LOW
        assert d.should_push is True


# ── 边界条件 ────────────────────────────────────────────

class TestEdgeCases:
    """边界条件测试。"""

    def test_empty_symbol(self):
        """空 symbol。"""
        f = make_filter()
        d = f.evaluate("", score=0.5, level1_pass=False, level2_pass=False)
        assert isinstance(d, FilterDecision)

    def test_zero_score(self):
        """0 评分。"""
        f = make_filter()
        d = f.evaluate("M", score=0.0, level1_pass=False, level2_pass=False)
        assert isinstance(d, FilterDecision)

    def test_max_score(self):
        """1.0 评分。"""
        f = make_filter()
        d = f.evaluate("CU", score=1.0, level1_pass=False, level2_pass=False)
        assert isinstance(d, FilterDecision)
        assert d.should_push is True

    def test_unknown_symbol(self):
        """未注册品种。"""
        f = make_filter()
        d = f.evaluate("QT", score=0.5, level1_pass=False, level2_pass=False)
        assert isinstance(d, FilterDecision)
        # 未知品种默认为 50% 准确率
        assert f.get_symbol_accuracy("QT") == 50.0

    def test_negative_score(self):
        """负评分。"""
        f = make_filter()
        d = f.evaluate("RB", score=-1.0, level1_pass=False, level2_pass=False)
        assert isinstance(d, FilterDecision)
        assert d.should_push is True  # RB 准确率 100%

    def test_high_accuracy_invalid_score(self):
        """高准确率 + 无 L1/L2 但分数极低。"""
        f = make_filter()
        d = f.evaluate("Y", score=0.0, level1_pass=False, level2_pass=False)
        # Y 准确率 100%，评分 0 → NORMAL（规则 5，准确率≥60%）
        assert d.should_push is True


# ── FilterDecision ───────────────────────────────────────

class TestFilterDecision:
    """FilterDecision 数据结构测试。"""

    def test_default_decision(self):
        """默认决策 → 不推送，SUPPRESS。"""
        d = FilterDecision()
        assert d.should_push is False
        assert d.push_level == "SUPPRESS"
        assert d.confidence == 0.0
        assert d.boost_factor == 1.0

    def test_to_dict(self):
        """to_dict() 序列化正确。"""
        d = FilterDecision(
            should_push=True, push_level="HIGH",
            reason="test", confidence=96.6, boost_factor=1.15,
        )
        di = d.to_dict()
        assert di["should_push"] is True
        assert di["push_level"] == "HIGH"
        assert di["confidence"] == 96.6
        assert di["boost_factor"] == 1.15

    def test_repr(self):
        """__repr__ 可读。"""
        d = FilterDecision(should_push=True)
        r = repr(d)
        assert "should_push=True" in r

    def test_slots(self):
        """__slots__ 生效，不能添加额外属性。"""
        d = FilterDecision()
        with pytest.raises(AttributeError):  # noqa: F821
            d.extra_field = 123


# ── 板块偏置 ────────────────────────────────────────────

class TestSectorBoost:
    """板块加权系数测试。"""

    def test_energy_sector_boost(self):
        """能源化工 boost = 1.15。"""
        f = make_filter()
        assert f.get_sector_boost("RB") == 1.0   # 黑色
        assert f.get_sector_boost("TA") == 1.15  # 能源化工
        assert f.get_sector_boost("MA") == 1.15  # 能源化工
        assert f.get_sector_boost("CU") == 1.0   # 有色
        assert f.get_sector_boost("LC") == 1.0   # 新能源

    def test_sector_mapping(self):
        """板块映射正确。"""
        f = make_filter()
        assert f.get_sector("RB") == "黑色"
        assert f.get_sector("TA") == "能源化工"
        assert f.get_sector("M") == "农产品"
        assert f.get_sector("AU") == "贵金属"
        assert f.get_sector("CU") == "有色"
        assert f.get_sector("SI") == "新能源"


# ── 符号准确率 ──────────────────────────────────────────

class TestSymbolAccuracy:
    """品种准确率查询测试。"""

    def test_known_symbols(self):
        """已知品种返回正确准确率。"""
        f = make_filter()
        assert f.get_symbol_accuracy("RB") == 100.0
        assert f.get_symbol_accuracy("P") == 94.2
        assert f.get_symbol_accuracy("TA") == 84.6
        assert f.get_symbol_accuracy("OI") == 2.9
        assert f.get_symbol_accuracy("CF") == 15.4
        assert f.get_symbol_accuracy("SA") == 28.8

    def test_unknown_symbol(self):
        """未知品种返回默认值。"""
        f = make_filter()
        assert f.get_symbol_accuracy("ZZ") == 50.0

    def test_case_sensitive(self):
        """准确率查询区分大小写。"""
        f = make_filter()
        assert f.get_symbol_accuracy("rb") == 50.0  # 小写不在表中


# ── filter_signals 批量处理 ─────────────────────────────

class TestFilterSignals:
    """批量过滤测试。"""

    def test_filter_signals_empty(self):
        """空列表返回空。"""
        f = make_filter()
        assert f.filter_signals([]) == []

    def test_filter_signals_single(self):
        """单个信号过滤。"""
        f = make_filter()
        sigs = [{"symbol": "RB", "score": 0.7, "level1_pass": True, "level2_pass": True}]
        result = f.filter_signals(sigs)
        assert len(result) == 1
        assert result[0]["filter_decision"]["should_push"] is True
        assert result[0]["filter_decision"]["push_level"] == "HIGH"

    def test_filter_signals_mixed(self):
        """混合信号列表按置信度排序。
        TA: 评分0.6 + 准确率84.6% ≥ 80% + 能源化工1.15倍 → HIGH (conf=84.6*1.15=97.3)
        RB: L1+L2 → HIGH (conf=96.6)
        OI: 2.9% → SUPPRESS
        排序: TA (97.3) > RB (96.6) > OI (2.9)"""
        f = make_filter()
        sigs = [
            {"symbol": "OI", "score": 0.5, "level1_pass": False, "level2_pass": False},
            {"symbol": "RB", "score": 0.7, "level1_pass": True, "level2_pass": True},
            {"symbol": "TA", "score": 0.6, "level1_pass": False, "level2_pass": False},
        ]
        result = f.filter_signals(sigs)
        assert len(result) == 3
        # TA 高评分+高信度+板块加权 → 最高置信度
        assert result[0]["symbol"] == "TA"
        assert result[0]["filter_decision"]["confidence"] > 96.0
        # RB L1+L2 → 次高
        assert result[1]["symbol"] == "RB"
        assert result[1]["filter_decision"]["confidence"] == 96.6

    def test_filter_signals_keeps_original(self):
        """原始字段保留，filter_decision 追加。"""
        f = make_filter()
        sigs = [{"symbol": "RB", "score": 0.7, "extra": "hello"}]
        result = f.filter_signals(sigs)
        assert result[0]["extra"] == "hello"
        assert "filter_decision" in result[0]


# ── 便捷方法 filtered_dispatch ──────────────────────────

class TestFilteredDispatch:
    """filtered_dispatch 便捷方法测试。"""

    def test_filtered_dispatch_rb(self):
        """RB 信号应返回 True（推送）。"""
        from signals.smart_filter import filtered_dispatch
        result = filtered_dispatch(
            symbol="RB", score=0.7,
            level1_pass=True, level2_pass=True, level3_pass=False,
            signal_type="ENTRY", msg="test RB signal",
        )
        assert result is True

    def test_filtered_dispatch_oi(self):
        """OI 信号应返回 False（抑制）。"""
        from signals.smart_filter import filtered_dispatch
        result = filtered_dispatch(
            symbol="OI", score=0.5,
            level1_pass=False, level2_pass=False, level3_pass=False,
            signal_type="WATCH", msg="test OI signal",
        )
        assert result is False
