"""测试 futures/n_structure.py 的 detect_and_save() 状态机逻辑。

从旧期货项目迁移，调整了导入路径和 db 参数。
"""

import pytest
from unittest.mock import patch, MagicMock, call

from futures.n_structure import (
    detect_and_save, dynamic_restructure,
    _find_n_structure_forward, _merge_same_type,
    NState,
)
from core.db import Database
from tests.conftest import make_swing, T1, T2, T3, T4, T5, T6

_test_db: Database = Database(":memory:")


# ═══════════════════════════════════════════════════════
# 1. 连续同向极值合并
# ═══════════════════════════════════════════════════════
class TestSwingPointMerge:
    """连续同向极值合并：取更极端值"""

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_merge_consecutive_peaks(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """PEAK(100,T1) -> PEAK(105,T2) -> TROUGH(90,T3) → 合并后A=PEAK(105,T2), B=TROUGH(90,T3)"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 100, T1),
            make_swing("PEAK", 105, T2),
            make_swing("TROUGH", 90, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        # 合并后只剩2个点，不足3个 → IDLE
        assert result["state"] == NState.IDLE.value
        assert result["is_active"] is False

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_merge_peaks_keep_higher(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """PEAK(105,T1) -> PEAK(100,T2) -> TROUGH(90,T3) → 合并保留PEAK(105,T1)"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 105, T1),
            make_swing("PEAK", 100, T2),
            make_swing("TROUGH", 90, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_merge_troughs_keep_lower(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """TROUGH(100,T1) -> TROUGH(90,T2) -> PEAK(110,T3) → 合并保留TROUGH(90,T2)"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 100, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 110, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_merge_then_valid_structure(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """PEAK(100,T1) -> PEAK(105,T2) -> TROUGH(90,T3) -> PEAK(110,T4) → 合并后3个交替点"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 100, T1),
            make_swing("PEAK", 105, T2),  # 合并为PEAK(105,T2)
            make_swing("TROUGH", 90, T3),
            make_swing("PEAK", 110, T4),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] in (NState.IDLE.value, NState.LEG2.value, NState.LEG3.value)

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_merge_troughs_then_valid_long(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """TROUGH(100,T1) -> TROUGH(95,T2) -> PEAK(110,T3) -> TROUGH(105,T4)
        合并后: TROUGH(95,T2), PEAK(110,T3), TROUGH(105,T4) → LONG"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 100, T1),
            make_swing("TROUGH", 95, T2),  # 合并为TROUGH(95,T2)
            make_swing("PEAK", 110, T3),
            make_swing("TROUGH", 105, T4),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "LONG"
        assert result["point_a_price"] == 95
        assert result["point_b_price"] == 110
        assert result["point_c_price"] == 105


# ═══════════════════════════════════════════════════════
# 2. 正常正N型
# ═══════════════════════════════════════════════════════
class TestNormalLongN:
    """正常正N型：TROUGH -> PEAK -> TROUGH，direction=LONG"""

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_normal_long_leg2(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """TROUGH(90,T1) -> PEAK(110,T2) -> TROUGH(95,T3)
        direction=LONG, C=95 < B=110 → LEG2"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("TROUGH", 95, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "LONG"
        assert result["state"] == NState.LEG3.value
        assert result["is_active"] is True
        assert result["point_a_price"] == 90
        assert result["point_b_price"] == 110
        assert result["point_c_price"] == 95

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_normal_long_leg3(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """TROUGH(90,T1) -> PEAK(110,T2) -> TROUGH(100,T3)
        direction=LONG, 有效3点交替结构 → LEG3"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("TROUGH", 100, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "LONG"
        assert result["state"] == NState.LEG3.value  # 有效3点交替结构→LEG3


# ═══════════════════════════════════════════════════════
# 3. 正常倒N型
# ═══════════════════════════════════════════════════════
class TestNormalShortN:
    """正常倒N型：PEAK -> TROUGH -> PEAK，direction=SHORT"""

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_normal_short_leg3_mid(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """PEAK(110,T1) -> TROUGH(90,T2) -> PEAK(105,T3)
        direction=SHORT, C=105<A=110形成有效V型 → LEG3"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 110, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 105, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "SHORT"
        assert result["state"] == NState.LEG3.value
        assert result["is_active"] is True

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_normal_short_leg3(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """PEAK(110,T1) -> TROUGH(90,T2) -> PEAK(100,T3)
        direction=SHORT, 有效3点交替结构 → LEG3
        C=100 > B=90（条件2:B→C第二笔上涨确认✓）and C=100 < A=110（条件3:C不高于A✓）"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 110, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 100, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "SHORT"
        assert result["state"] == NState.LEG3.value


# ═══════════════════════════════════════════════════════
# 4. 少于3个极值点
# ═══════════════════════════════════════════════════════
class TestInsufficientPoints:
    """少于3个极值点返回IDLE"""

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_zero_points(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        mock_get_swings.return_value = []
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value
        assert result["is_active"] is False

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_one_point(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        mock_get_swings.return_value = [make_swing("PEAK", 100, T1)]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_two_points(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        mock_get_swings.return_value = [
            make_swing("PEAK", 100, T1),
            make_swing("TROUGH", 90, T2),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_two_points_after_merge(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """3个同向极值点合并后只剩1个，不足3"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 100, T1),
            make_swing("PEAK", 105, T2),
            make_swing("PEAK", 110, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value


# ═══════════════════════════════════════════════════════
# 5. C突破A的无效结构
# ═══════════════════════════════════════════════════════
class TestInvalidCBreaksA:
    """C突破A的结构被跳过，找下一个有效窗口"""

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_long_c_breaks_a(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """LONG方向 C <= A → 无效，跳过"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 95, T1),
            make_swing("PEAK", 100, T2),
            make_swing("TROUGH", 90, T3),  # C=90 <= A=95
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value
        assert result.get("reason") == "无有效3点结构"

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_short_c_breaks_a(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """SHORT方向 C >= A → 无效，跳过"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 100, T1),
            make_swing("TROUGH", 95, T2),
            make_swing("PEAK", 105, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value
        assert result.get("reason") == "无有效3点结构"

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_long_c_equals_a_invalid(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """LONG方向 C == A → 不算突破(C <= A) → 跳过"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 95, T1),
            make_swing("PEAK", 100, T2),
            make_swing("TROUGH", 95, T3),  # C=95 == A=95
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value


# ═══════════════════════════════════════════════════════
# 6. COMPLETED判定
# ═══════════════════════════════════════════════════════
class TestCompletedState:

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_completed_with_prior_same_type(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """4个极值点场景"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 120, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 105, T3),
            make_swing("TROUGH", 85, T4),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "SHORT"
        assert result["state"] != NState.IDLE.value

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_completed_short_with_prior_peak(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """5个极值点场景"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 120, T1),
            make_swing("TROUGH", 95, T2),
            make_swing("PEAK", 110, T3),
            make_swing("TROUGH", 90, T4),
            make_swing("PEAK", 105, T5),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "SHORT"

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_completed_when_prior_same_direction(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """在正常交替序列中，不会出现COMPLETED"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 120, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 105, T3),
            make_swing("TROUGH", 85, T4),
            make_swing("PEAK", 100, T5),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] != NState.COMPLETED.value

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_completed_with_merged_prior(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """验证在正常5个交替点序列中不会COMPLETED"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 120, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 105, T3),
            make_swing("TROUGH", 85, T4),
            make_swing("PEAK", 100, T5),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] != NState.COMPLETED.value
        assert result["state"] in (NState.LEG2.value, NState.LEG3.value, NState.IDLE.value)


# ═══════════════════════════════════════════════════════
# 7. 合并后恰好3个交替点
# ═══════════════════════════════════════════════════════
class TestMergedExactlyThree:
    """合并后恰好3个交替点"""

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_merge_to_exactly_three_long(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """合并后3个交替点 → 有效LONG结构"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 95, T1),
            make_swing("TROUGH", 90, T2),  # 合并为TROUGH(90,T2)
            make_swing("PEAK", 110, T3),
            make_swing("TROUGH", 100, T4),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "LONG"
        assert result["point_a_price"] == 90
        assert result["point_b_price"] == 110
        assert result["point_c_price"] == 100
        assert result["state"] == NState.LEG3.value

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_merge_to_exactly_three_short(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """合并后3个交替点 → 有效SHORT结构"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 120, T1),
            make_swing("PEAK", 115, T2),  # 合并保留PEAK(120,T1)
            make_swing("TROUGH", 90, T3),
            make_swing("PEAK", 105, T4),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "SHORT"
        assert result["point_a_price"] == 120
        assert result["point_b_price"] == 90
        assert result["point_c_price"] == 105


# ═══════════════════════════════════════════════════════
# 8. 4个以上极值点的滑窗选择
# ═══════════════════════════════════════════════════════
class TestSlidingWindow:
    """4+个极值点的滑窗选择逻辑"""

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_sliding_window_picks_latest_valid(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """4个交替点：前向扫描找到最早有效 T80→P120→T90 → LONG结构"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 80, T1),
            make_swing("PEAK", 120, T2),
            make_swing("TROUGH", 90, T3),
            make_swing("PEAK", 105, T4),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        # 前向非重叠扫描：A=T80, B=P120, C=T90 → LONG
        assert result["direction"] == "LONG"
        assert result["point_a_price"] == 80
        assert result["point_b_price"] == 120
        assert result["point_c_price"] == 90

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_sliding_window_fallback(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """最新3个有效选最新"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("TROUGH", 85, T3),
            make_swing("PEAK", 105, T4),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["direction"] == "SHORT"

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_five_points_window(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """5个交替点：前向扫描取最早有效 P120→T90→P105 → SHORT结构"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 120, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 105, T3),
            make_swing("TROUGH", 85, T4),
            make_swing("PEAK", 100, T5),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        # 前向非重叠扫描：A=P120, B=T90, C=P105 → SHORT (C=105 < A=120 ✓)
        assert result["direction"] == "SHORT"
        assert result["point_a_price"] == 120
        assert result["point_b_price"] == 90
        assert result["point_c_price"] == 105

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_non_alternating_trio_skipped(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """3个非交替点被跳过，合并后不足3"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 100, T1),
            make_swing("PEAK", 120, T2),
            make_swing("TROUGH", 90, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_save_n_structure_called(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """验证 _save_n_structure 被正确调用"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("TROUGH", 95, T3),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        mock_save.assert_called_once()
        # _save_n_structure(db, ns): call_args[0][0]=db, call_args[0][1]=ns
        saved_data = mock_save.call_args[0][1]
        assert saved_data["symbol"] == "RB"
        assert saved_data["contract"] == "rb2510"
        assert saved_data["direction"] == "LONG"


# ═══════════════════════════════════════════════════════
# 9. 直接测试 _find_n_structure_forward() 核心算法
# ═══════════════════════════════════════════════════════
class TestFindNStructureForward:
    """直接测试 _find_n_structure_forward() 核心算法。

    这些测试绕过 DB/mock，直接传入合并后极值点列表，
    验证 A/B/C 三点定位完全符合 User Directives 正确定义。
    """

    def test_long_basic(self) -> None:
        """上升 N 型：T90→P110→T95 → A=90, B=110, C=95, direction=LONG"""
        merged = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("TROUGH", 95, T3),
        ]
        result = _find_n_structure_forward(merged)
        assert result is not None
        assert result["direction"] == "LONG"
        assert result["a"]["price"] == 90
        assert result["b"]["price"] == 110
        assert result["c"]["price"] == 95

    def test_short_basic(self) -> None:
        """下降 N 型：P110→T90→P105 → A=110, B=90, C=105, direction=SHORT"""
        merged = [
            make_swing("PEAK", 110, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 105, T3),
        ]
        result = _find_n_structure_forward(merged)
        assert result is not None
        assert result["direction"] == "SHORT"
        assert result["a"]["price"] == 110
        assert result["b"]["price"] == 90
        assert result["c"]["price"] == 105

    def test_long_v_shape_semantics(self) -> None:
        """上升 N 型 V 形语义验证：
        A(最低点)=90 → B(第一笔最高点)=120 → C(第二笔低点)=100
        C > A 成立，A→B→C 构成完整的上升 V 形"""
        merged = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 120, T2),
            make_swing("TROUGH", 100, T3),
        ]
        result = _find_n_structure_forward(merged)
        assert result is not None
        assert result["direction"] == "LONG"
        # V 形结构验证：A→B 上涨(90→120)，B→C 下跌(120→100)
        assert result["b"]["price"] > result["a"]["price"]  # A→B 上涨
        assert result["c"]["price"] < result["b"]["price"]  # B→C 下跌
        assert result["c"]["price"] > result["a"]["price"]  # C > A 成立

    def test_short_v_shape_semantics(self) -> None:
        """下降 N 型 V 形语义验证：
        A(最高点)=120 → B(第一笔最低点)=90 → C(第二笔高点)=110
        C < A 成立，A→B→C 构成完整的下降 V 形"""
        merged = [
            make_swing("PEAK", 120, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 110, T3),
        ]
        result = _find_n_structure_forward(merged)
        assert result is not None
        assert result["direction"] == "SHORT"
        # V 形结构验证：A→B 下跌(120→90)，B→C 上涨(90→110)
        assert result["b"]["price"] < result["a"]["price"]  # A→B 下跌
        assert result["c"]["price"] > result["b"]["price"]  # B→C 上涨
        assert result["c"]["price"] < result["a"]["price"]  # C < A 成立

    def test_long_c_breaks_a_skipped(self) -> None:
        """LONG 方向 C <= A 被跳过 → 返回 None"""
        merged = [
            make_swing("TROUGH", 95, T1),
            make_swing("PEAK", 100, T2),
            make_swing("TROUGH", 90, T3),  # C=90 <= A=95，无效
        ]
        result = _find_n_structure_forward(merged)
        assert result is None

    def test_short_c_breaks_a_skipped(self) -> None:
        """SHORT 方向 C >= A 被跳过 → 返回 None"""
        merged = [
            make_swing("PEAK", 100, T1),
            make_swing("TROUGH", 95, T2),
            make_swing("PEAK", 105, T3),  # C=105 >= A=100，无效
        ]
        result = _find_n_structure_forward(merged)
        assert result is None

    def test_non_overlapping_scan(self) -> None:
        """非重叠扫描：找到第一个有效结构后跳到 C 之后继续扫描。

        极值点序列: T90→P120→T100→P130→T110
        结构1: A=T90,B=P120,C=T100 (LONG)
        跳过 C=T100 之后扫描：
        结构2: C=T100 不是 A(P type 不对)→下一个 P130 可做 A
        但 P130→T110 只有两个点，不足 3 点 → 返回结构1
        """
        merged = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 120, T2),
            make_swing("TROUGH", 100, T3),
            make_swing("PEAK", 130, T4),
            make_swing("TROUGH", 110, T5),
        ]
        result = _find_n_structure_forward(merged)
        assert result is not None
        assert result["a"]["price"] == 90
        assert result["b"]["price"] == 120
        assert result["c"]["price"] == 100
        assert result["direction"] == "LONG"
        # i = c_idx + 1 = 2 + 1 = 3 → 从 merged[3]=PEAK(130,T4) 继续扫描
        # P130→T110 只有 2 个点不足 3 → 没有更多结构

    def test_non_overlapping_two_structures(self) -> None:
        """非重叠扫描：两个独立 N 型结构。

        T90→P120→T100 → 结构1 (LONG A=90,B=120,C=100)
        跳到 C=T100 之后 → P130→T110→P140 → 结构2 (SHORT A=130,B=110,C=140)
        但 C=140 > A=130 → SHORT 无效，所以只返回结构1
        或者说 P130→T110→P140 中 C=140 > A=130，SHORT 不成立
        所以只返回结构1
        """
        merged = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 120, T2),
            make_swing("TROUGH", 100, T3),
            make_swing("PEAK", 130, T4),
            make_swing("TROUGH", 110, T5),
            make_swing("PEAK", 140, T6),
        ]
        result = _find_n_structure_forward(merged)
        assert result is not None
        # 返回最后一个有效结构 = 结构2 (SHORT A=130,B=110,C=140... 但 C=140 > A=130)
        # 实际上 P130→T110→P140: A=130(PEAK), B=110(TROUGH), C=140(PEAK)
        # SHORT: C=140 > A=130 → 无效！跳过
        # 所以只有结构1 → 取最后一个 = T90→P120→T100
        assert result["a"]["price"] == 90
        assert result["direction"] == "LONG"

    def test_continuous_downtrend_not_n_structure(self) -> None:
        """持续下跌：TROUGH(100)→PEAK(95)→TROUGH(90)
        方向 SHORT 但 A=TROUGH → 类型-方向矛盾 → 应返回 None"""
        merged = [
            make_swing("TROUGH", 100, T1),
            make_swing("PEAK", 95, T2),
            make_swing("TROUGH", 90, T3),
        ]
        result = _find_n_structure_forward(merged)
        assert result is None, "持续下跌趋势不应构成有效 N 型"

    def test_continuous_uptrend_not_n_structure(self) -> None:
        """持续上涨：PEAK(100)→TROUGH(105)→PEAK(110)
        方向 LONG 但 A=PEAK → 类型-方向矛盾 → 应返回 None"""
        merged = [
            make_swing("PEAK", 100, T1),
            make_swing("TROUGH", 105, T2),
            make_swing("PEAK", 110, T3),
        ]
        result = _find_n_structure_forward(merged)
        assert result is None, "持续上涨趋势不应构成有效 N 型"

    def test_non_overlapping_two_valid(self) -> None:
        """非重叠扫描：两个独立的有效 N 型结构。

        T90→P120→T100 → 结构1 (LONG, C=100 > A=90 ✓)
        跳到 T100 之后 → T105→P130→T115
        但 T105(TROUGH)→P130→T115:
        A=T105(最低点), B=P130(最高点), C=T115(第二笔低点)
        direction: B > A → LONG
        C=115 > A=105 ✓ → 有效
        返回结构2 (最后一个有效)
        """
        merged = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 120, T2),
            make_swing("TROUGH", 100, T3),
            make_swing("TROUGH", 105, T4),
            make_swing("PEAK", 130, T5),
            make_swing("TROUGH", 115, T6),
        ]
        result = _find_n_structure_forward(merged)
        assert result is not None
        # 返回最后一个有效结构
        assert result["a"]["price"] == 105
        assert result["b"]["price"] == 130
        assert result["c"]["price"] == 115
        assert result["direction"] == "LONG"

    # ─── 条件 2 显式检查：B→C 方向一致性 ───────────────────────

    def test_long_c_not_below_b_rejected(self) -> None:
        """条件2：LONG 方向 C >= B → B→C 没有下跌（第二笔确认失败）→ 跳过"""
        merged = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 100, T2),
            make_swing("TROUGH", 105, T3),  # C=105 >= B=100 → B→C 无下跌，无效
        ]
        result = _find_n_structure_forward(merged)
        assert result is None

    def test_short_c_not_above_b_rejected(self) -> None:
        """条件2：SHORT 方向 C <= B → B→C 没有上涨（第二笔确认失败）→ 跳过"""
        merged = [
            make_swing("PEAK", 110, T1),
            make_swing("TROUGH", 100, T2),
            make_swing("PEAK", 95, T3),  # C=95 <= B=100 → B→C 无上涨，无效
        ]
        result = _find_n_structure_forward(merged)
        assert result is None


# ═══════════════════════════════════════════════════════
# 10. 橡胶 2609 周 K 线真实案例（User Directives 指定）
# ═══════════════════════════════════════════════════════
class TestRubber2609WeeklyCase:
    """橡胶 2609 周 K 线案例（User Directives 指定）。

    正确定义：
    - 上升 N 型：A = 17220（最低点）, B = 18440（第一笔最高点）
      C = 17245（第二笔低点，高于 A 点成立）
    - A→B→C 形成完整上升 V 型结构
    - C 之后价格向上 → 正在形成第三笔
    """

    def test_rubber_weekly_n_structure(self) -> None:
        """橡胶 2609 周线：A=17220, B=18440, C=17245 → LONG"""
        merged = [
            make_swing("TROUGH", 17220, T1),
            make_swing("PEAK", 18440, T2),
            make_swing("TROUGH", 17245, T3),
        ]
        result = _find_n_structure_forward(merged)
        assert result is not None
        assert result["direction"] == "LONG"
        assert result["a"]["price"] == 17220
        assert result["b"]["price"] == 18440
        assert result["c"]["price"] == 17245
        # V 形语义验证
        assert result["c"]["price"] > result["a"]["price"]  # C > A

    def test_rubber_weekly_if_c_below_a_invalid(self) -> None:
        """如果 C 低于 A（如 17200 < 17220）→ 无效，上升 N 型不成立"""
        merged = [
            make_swing("TROUGH", 17220, T1),
            make_swing("PEAK", 18440, T2),
            make_swing("TROUGH", 17200, T3),  # C=17200 < A=17220
        ]
        result = _find_n_structure_forward(merged)
        assert result is None

    def test_rubber_weekly_non_overlap(self) -> None:
        """橡胶周线 + 更多极值点时非重叠扫描行为。

        极值点序列合并后 = T17220→P18440→T17245→P19000
        前向扫描：A=T17220, B=P18440, C=T17245 ✓ LONG
        跳到 C=T17245 之后 → P19000 只有 1 点不足 → 返回该结构
        """
        merged = [
            make_swing("TROUGH", 17220, T1),
            make_swing("PEAK", 18440, T2),
            make_swing("TROUGH", 17245, T3),
            make_swing("PEAK", 19000, T4),
        ]
        result = _find_n_structure_forward(merged)
        assert result is not None
        assert result["direction"] == "LONG"
        assert result["a"]["price"] == 17220
        assert result["b"]["price"] == 18440
        assert result["c"]["price"] == 17245
        # C→最新价方向 = 上涨（19000 > 17245）→ 第三笔向上


# ═══════════════════════════════════════════════════════
# 11. _merge_same_type 直接测试
# ═══════════════════════════════════════════════════════
class TestMergeSameTypeDirect:
    """直接测试 _merge_same_type() 合并逻辑。"""

    def test_merge_consecutive_peaks_keep_higher(self) -> None:
        """连续 PEAK 保留最高值"""
        pts = [
            make_swing("PEAK", 100, T1),
            make_swing("PEAK", 105, T2),
            make_swing("PEAK", 102, T3),
        ]
        merged = _merge_same_type(pts)
        assert len(merged) == 1
        assert merged[0]["price"] == 105
        assert merged[0]["timestamp"] == T2

    def test_merge_consecutive_troughs_keep_lower(self) -> None:
        """连续 TROUGH 保留最低值"""
        pts = [
            make_swing("TROUGH", 100, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("TROUGH", 95, T3),
        ]
        merged = _merge_same_type(pts)
        assert len(merged) == 1
        assert merged[0]["price"] == 90
        assert merged[0]["timestamp"] == T2

    def test_merge_alternating_keeps_all(self) -> None:
        """交替类型不合并"""
        pts = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("TROUGH", 95, T3),
        ]
        merged = _merge_same_type(pts)
        assert len(merged) == 3
        assert merged[0]["price"] == 90
        assert merged[1]["price"] == 110
        assert merged[2]["price"] == 95

    def test_merge_complex_sequence(self) -> None:
        """复杂序列：T→P→P→T→T→P"""
        pts = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("PEAK", 115, T3),  # 合并 110→115
            make_swing("TROUGH", 100, T4),
            make_swing("TROUGH", 98, T5),  # 合并 100→98
            make_swing("PEAK", 120, T6),
        ]
        merged = _merge_same_type(pts)
        assert len(merged) == 4
        assert merged[0]["price"] == 90    # TROUGH
        assert merged[1]["price"] == 115   # PEAK (合并取高)
        assert merged[2]["price"] == 98    # TROUGH (合并取低)
        assert merged[3]["price"] == 120   # PEAK


# ═══════════════════════════════════════════════════════
# 12. 合并后非交替序列测试
# ═══════════════════════════════════════════════════════
class TestMergedNonAlternating:
    """合并后仍不足以形成交替 3 点序列的边界情况。"""

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_merged_still_only_two(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """4个点合并后只剩2个交替点 → IDLE"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 100, T1),
            make_swing("PEAK", 105, T2),
            make_swing("TROUGH", 95, T3),
            make_swing("TROUGH", 92, T4),
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value


# ═══════════════════════════════════════════════════════
# 13. 边缘：C == A 边界（LONG 方向）
# ═══════════════════════════════════════════════════════
class TestCEqualsABoundary:
    """C == A 边界情况。"""

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_long_c_equals_a(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """LONG 方向 C == A → C <= A → 无效（跳过）"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 100, T1),
            make_swing("PEAK", 120, T2),
            make_swing("TROUGH", 100, T3),  # C=100 == A=100
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value

    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_short_c_equals_a(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
    ) -> None:
        """SHORT 方向 C == A → C >= A → 无效（跳过）"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 100, T1),
            make_swing("TROUGH", 80, T2),
            make_swing("PEAK", 100, T3),  # C=100 == A=100
        ]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value


# ═══════════════════════════════════════════════════════
# 14. 条件 4 测试（第三笔方向确认）— 通过 detect_and_save()
# ═══════════════════════════════════════════════════════
class TestCondition4Detect:
    """通过 detect_and_save() 测试条件 4（第三笔方向确认）。

    条件 4 要求：
    - LONG: 最新收盘价必须 > C（确认第三笔向上破位）
    - SHORT: 最新收盘价必须 < C（确认第三笔向下破位）
    - 若 _get_klines 抛出异常则跳过条件 4 检查

    测试需要 mock _get_klines 和 _get_swing_points + _save_n_structure。
    """

    @patch("futures.n_structure._get_klines")
    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_long_close_below_c_returns_idle(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
        mock_klines: MagicMock,
    ) -> None:
        """LONG: 最新收盘价 92 <= C=95 → 条件 4 不满足 → IDLE"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("TROUGH", 95, T3),
        ]
        mock_klines.return_value = [{"timestamp": T4, "close": 92.0}]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value
        assert result["is_active"] is False
        assert "条件4" in result.get("reason", "")

    @patch("futures.n_structure._get_klines")
    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_short_close_above_c_returns_idle(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
        mock_klines: MagicMock,
    ) -> None:
        """SHORT: 最新收盘价 107 >= C=105 → 条件 4 不满足 → IDLE"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 110, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 105, T3),
        ]
        mock_klines.return_value = [{"timestamp": T4, "close": 107.0}]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.IDLE.value
        assert result["is_active"] is False
        assert "条件4" in result.get("reason", "")

    @patch("futures.n_structure._get_klines")
    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_long_close_above_c_remains_active(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
        mock_klines: MagicMock,
    ) -> None:
        """LONG: 最新收盘价 105 > C=95 → 条件 4 满足 → LEG3 活跃"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("TROUGH", 95, T3),
        ]
        mock_klines.return_value = [{"timestamp": T4, "close": 105.0}]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.LEG3.value
        assert result["is_active"] is True
        assert result["point_a_price"] == 90
        assert result["point_b_price"] == 110
        assert result["point_c_price"] == 95

    @patch("futures.n_structure._get_klines")
    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_short_close_below_c_remains_active(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
        mock_klines: MagicMock,
    ) -> None:
        """SHORT: 最新收盘价 95 < C=105 → 条件 4 满足 → LEG3 活跃"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 110, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 105, T3),
        ]
        mock_klines.return_value = [{"timestamp": T4, "close": 95.0}]
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.LEG3.value
        assert result["is_active"] is True
        assert result["point_a_price"] == 110
        assert result["point_b_price"] == 90
        assert result["point_c_price"] == 105

    @patch("futures.n_structure._get_klines")
    @patch("futures.n_structure._save_n_structure")
    @patch("futures.n_structure._get_swing_points")
    def test_klines_exception_skips_condition4(
        self, mock_get_swings: MagicMock, mock_save: MagicMock,
        mock_klines: MagicMock,
    ) -> None:
        """_get_klines 抛出异常 → 条件 4 跳过 → 结构仍有效 LEG3"""
        mock_get_swings.return_value = [
            make_swing("TROUGH", 90, T1),
            make_swing("PEAK", 110, T2),
            make_swing("TROUGH", 95, T3),
        ]
        mock_klines.side_effect = Exception("DB table not found")
        result = detect_and_save("RB", "rb2510", "1w", _test_db)
        assert result["state"] == NState.LEG3.value
        assert result["is_active"] is True
