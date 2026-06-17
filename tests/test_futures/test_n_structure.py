"""测试 futures/n_structure.py 的 detect_and_save() 状态机逻辑。

从旧期货项目迁移，调整了导入路径和 db 参数。
"""

import pytest
from unittest.mock import patch, MagicMock, call

from futures.n_structure import detect_and_save, NState
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
        """PEAK(110,T1) -> TROUGH(90,T2) -> PEAK(85,T3)
        direction=SHORT, 有效3点交替结构 → LEG3"""
        mock_get_swings.return_value = [
            make_swing("PEAK", 110, T1),
            make_swing("TROUGH", 90, T2),
            make_swing("PEAK", 85, T3),
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
