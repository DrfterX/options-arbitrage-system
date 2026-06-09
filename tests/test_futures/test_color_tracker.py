"""测试 futures/color_tracker.py 的 MACD轨迹验证和3分钟稳定性。

从旧期货项目迁移，调整了导入路径和 db 参数。
"""

import pytest
from unittest.mock import patch, MagicMock

from futures.color_tracker import (
    check_macd_trajectory, check_3m_stability, check_color_sequence,
)
from config.settings import (
    COLOR_RED, COLOR_BLUE, TRANSITION_WINDOW_BEFORE, TRANSITION_WINDOW_AFTER,
)
from core.db import Database
from tests.conftest import make_macd_row, T1, T2, T3, T4, T5, T6

_test_db: Database = Database(":memory:")


# ═══════════════════════════════════════════════════════
# 辅助：构造 MACD 数据序列
# ═══════════════════════════════════════════════════════

def make_red_rows(n: int, start_ts: int = 1000, gap: int = 100,
                  histogram_start: float = 5.0) -> list:
    """构造 n 根 RED MACD 数据（histogram 递减模拟减弱）。"""
    return [
        make_macd_row(start_ts + i * gap, COLOR_RED,
                      histogram=histogram_start - i * 0.3)
        for i in range(n)
    ]


def make_blue_rows(n: int, start_ts: int = 1000, gap: int = 100,
                   histogram_start: float = -5.0) -> list:
    """构造 n 根 BLUE MACD 数据（histogram 递增模拟减弱）。"""
    return [
        make_macd_row(start_ts + i * gap, COLOR_BLUE,
                      histogram=histogram_start + i * 0.3)
        for i in range(n)
    ]


# ═══════════════════════════════════════════════════════
# 1. 腿1+腿2都通过
# ═══════════════════════════════════════════════════════
class TestMacdTrajectoryBothLegsPass:

    @patch("futures.color_tracker._get_macd_in_range")
    def test_short_both_legs_pass(self, mock_get_macd: MagicMock) -> None:
        """做空：A点前RED，后BLUE → 腿1通过；B点前BLUE，后RED → 腿2通过"""
        before_a = make_red_rows(5, start_ts=T1 - 500, gap=100, histogram_start=5.0)
        after_a = make_blue_rows(8, start_ts=T1, gap=100, histogram_start=-5.0)
        before_b = make_blue_rows(5, start_ts=T2 - 500, gap=100, histogram_start=-5.0)
        after_b = make_red_rows(8, start_ts=T2, gap=100, histogram_start=5.0)
        after_c = make_red_rows(6, start_ts=T3, gap=100, histogram_start=3.0)

        mock_get_macd.side_effect = [before_a, after_a, before_b, after_b, after_c]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["passed"] is True
        assert result["leg1"]["passed"] is True
        assert result["leg2"]["passed"] is True

    @patch("futures.color_tracker._get_macd_in_range")
    def test_long_both_legs_pass(self, mock_get_macd: MagicMock) -> None:
        """做多：A点前BLUE，后RED → 腿1通过；B点前RED，后BLUE → 腿2通过"""
        before_a = make_blue_rows(5, start_ts=T1 - 500, gap=100, histogram_start=-5.0)
        after_a = make_red_rows(8, start_ts=T1, gap=100, histogram_start=5.0)
        before_b = make_red_rows(5, start_ts=T2 - 500, gap=100, histogram_start=5.0)
        after_b = make_blue_rows(8, start_ts=T2, gap=100, histogram_start=-5.0)
        after_c = make_blue_rows(6, start_ts=T3, gap=100, histogram_start=-3.0)

        mock_get_macd.side_effect = [before_a, after_a, before_b, after_b, after_c]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "LONG", _test_db)
        assert result["passed"] is True
        assert result["leg1"]["passed"] is True
        assert result["leg2"]["passed"] is True


# ═══════════════════════════════════════════════════════
# 2. 腿1不通过（转折前主体颜色不对）
# ═══════════════════════════════════════════════════════
class TestMacdTrajectoryLeg1Fail:

    @patch("futures.color_tracker._get_macd_in_range")
    def test_leg1_wrong_dominant_color(self, mock_get_macd: MagicMock) -> None:
        """做空腿1：转折前主体应为RED但实际是BLUE → 不通过"""
        before_a = make_blue_rows(5, start_ts=T1 - 500, gap=100, histogram_start=-5.0)
        after_a = make_blue_rows(8, start_ts=T1, gap=100, histogram_start=-5.0)
        before_b = make_blue_rows(5, start_ts=T2 - 500, gap=100, histogram_start=-5.0)
        after_b = make_red_rows(8, start_ts=T2, gap=100, histogram_start=5.0)
        after_c = make_red_rows(6, start_ts=T3, gap=100, histogram_start=3.0)

        mock_get_macd.side_effect = [before_a, after_a, before_b, after_b, after_c]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["passed"] is False
        assert result["leg1"]["passed"] is False
        assert "RED" in result["leg1"]["detail"] or "BLUE" in result["leg1"]["detail"]

    @patch("futures.color_tracker._get_macd_in_range")
    def test_leg1_no_data_before_pivot(self, mock_get_macd: MagicMock) -> None:
        """转折前无MACD数据 → 腿1不通过"""
        mock_get_macd.side_effect = [
            [],  # before_a: 无数据
            make_blue_rows(8, start_ts=T1, gap=100),
            make_blue_rows(5, start_ts=T2 - 500, gap=100),
            make_red_rows(8, start_ts=T2, gap=100),
            make_red_rows(6, start_ts=T3, gap=100),
        ]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["leg1"]["passed"] is False


# ═══════════════════════════════════════════════════════
# 3. 腿2不通过
# ═══════════════════════════════════════════════════════
class TestMacdTrajectoryLeg2Fail:

    @patch("futures.color_tracker._get_macd_in_range")
    def test_leg2_wrong_dominant_color(self, mock_get_macd: MagicMock) -> None:
        """做空腿2：B点前主体应为BLUE但实际是RED → 不通过"""
        before_a = make_red_rows(5, start_ts=T1 - 500, gap=100, histogram_start=5.0)
        after_a = make_blue_rows(8, start_ts=T1, gap=100, histogram_start=-5.0)
        # B点前应为BLUE但实际是RED
        before_b = make_red_rows(5, start_ts=T2 - 500, gap=100, histogram_start=5.0)
        after_b = make_red_rows(8, start_ts=T2, gap=100, histogram_start=5.0)
        after_c = make_red_rows(6, start_ts=T3, gap=100, histogram_start=3.0)

        mock_get_macd.side_effect = [before_a, after_a, before_b, after_b, after_c]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["passed"] is False
        assert result["leg2"]["passed"] is False


# ═══════════════════════════════════════════════════════
# 4. 窗口恰好够用（边界值测试）
# ═══════════════════════════════════════════════════════
class TestMacdTrajectoryBoundaryWindow:

    @patch("futures.color_tracker._get_macd_in_range")
    def test_exactly_enough_data_for_window(self, mock_get_macd: MagicMock) -> None:
        """数据量恰好等于TRANSITION_WINDOW_BEFORE/AFTER → 不截断"""
        before_a = make_red_rows(TRANSITION_WINDOW_BEFORE,
                                 start_ts=T1 - 500, gap=100, histogram_start=5.0)
        after_a = make_blue_rows(TRANSITION_WINDOW_AFTER,
                                 start_ts=T1, gap=100, histogram_start=-5.0)
        before_b = make_blue_rows(TRANSITION_WINDOW_BEFORE,
                                  start_ts=T2 - 500, gap=100, histogram_start=-5.0)
        after_b = make_red_rows(TRANSITION_WINDOW_AFTER,
                                start_ts=T2, gap=100, histogram_start=5.0)
        after_c = make_red_rows(6, start_ts=T3, gap=100, histogram_start=3.0)

        mock_get_macd.side_effect = [before_a, after_a, before_b, after_b, after_c]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["leg1"]["passed"] is True
        assert result["leg2"]["passed"] is True


# ═══════════════════════════════════════════════════════
# 5. 数据不足BEFORE窗口 → 不crash
# ═══════════════════════════════════════════════════════
class TestMacdTrajectoryInsufficientData:

    @patch("futures.color_tracker._get_macd_in_range")
    def test_insufficient_before_window_no_crash(self, mock_get_macd: MagicMock) -> None:
        """before数据不足TRANSITION_WINDOW_BEFORE → 不crash"""
        before_a = make_red_rows(2, start_ts=T1 - 200, gap=100, histogram_start=5.0)
        after_a = make_blue_rows(8, start_ts=T1, gap=100, histogram_start=-5.0)
        before_b = make_blue_rows(3, start_ts=T2 - 300, gap=100, histogram_start=-5.0)
        after_b = make_red_rows(8, start_ts=T2, gap=100, histogram_start=5.0)
        after_c = make_red_rows(6, start_ts=T3, gap=100, histogram_start=3.0)

        mock_get_macd.side_effect = [before_a, after_a, before_b, after_b, after_c]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        # 不应crash
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert isinstance(result, dict)
        assert "passed" in result

    @patch("futures.color_tracker._get_macd_in_range")
    def test_empty_data_no_crash(self, mock_get_macd: MagicMock) -> None:
        """所有数据为空 → 不crash"""
        mock_get_macd.return_value = []

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }

        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["passed"] is False


# ═══════════════════════════════════════════════════════
# 6. 回归测试：TRANSITION_WINDOW_BEFORE/AFTER参数生效
# ═══════════════════════════════════════════════════════
class TestTransitionWindowParameters:

    @patch("futures.color_tracker._get_macd_in_range")
    def test_before_window_slicing(self, mock_get_macd: MagicMock) -> None:
        """验证 before 数据被截取为 TRANSITION_WINDOW_BEFORE 根"""
        before_a_data = [
            make_macd_row(T1 - 1000 + i * 100, COLOR_RED, histogram=5.0 - i * 0.3)
            for i in range(10)
        ]
        after_a = make_blue_rows(8, start_ts=T1, gap=100, histogram_start=-5.0)
        before_b = make_blue_rows(5, start_ts=T2 - 500, gap=100, histogram_start=-5.0)
        after_b = make_red_rows(8, start_ts=T2, gap=100, histogram_start=5.0)
        after_c = make_red_rows(6, start_ts=T3, gap=100, histogram_start=3.0)

        mock_get_macd.side_effect = [before_a_data, after_a, before_b, after_b, after_c]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["leg1"]["passed"] is True

    @patch("futures.color_tracker._get_macd_in_range")
    def test_after_window_slicing(self, mock_get_macd: MagicMock) -> None:
        """验证 after 数据被截取为 TRANSITION_WINDOW_AFTER 根"""
        before_a = make_red_rows(5, start_ts=T1 - 500, gap=100, histogram_start=5.0)
        after_a_data = []
        for i in range(15):
            if i < 10:
                after_a_data.append(make_macd_row(T1 + i * 100, COLOR_BLUE, histogram=-5.0 + i * 0.3))
            else:
                after_a_data.append(make_macd_row(T1 + i * 100, COLOR_RED, histogram=5.0))

        before_b = make_blue_rows(5, start_ts=T2 - 500, gap=100, histogram_start=-5.0)
        after_b = make_red_rows(8, start_ts=T2, gap=100, histogram_start=5.0)
        after_c = make_red_rows(6, start_ts=T3, gap=100, histogram_start=3.0)

        mock_get_macd.side_effect = [before_a, after_a_data, before_b, after_b, after_c]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["leg1"]["passed"] is True

    @patch("futures.color_tracker._get_macd_in_range")
    def test_window_params_values(self, mock_get_macd: MagicMock) -> None:
        """验证窗口参数确实被用于截取"""
        before_a_mixed = []
        for i in range(10):
            if i < 5:
                before_a_mixed.append(make_macd_row(T1 - 1000 + i * 100, COLOR_BLUE, histogram=-5.0))
            else:
                before_a_mixed.append(make_macd_row(T1 - 1000 + i * 100, COLOR_RED, histogram=5.0))

        after_a = make_blue_rows(8, start_ts=T1, gap=100, histogram_start=-5.0)
        before_b = make_blue_rows(5, start_ts=T2 - 500, gap=100, histogram_start=-5.0)
        after_b = make_red_rows(8, start_ts=T2, gap=100, histogram_start=5.0)
        after_c = make_red_rows(6, start_ts=T3, gap=100, histogram_start=3.0)

        mock_get_macd.side_effect = [before_a_mixed, after_a, before_b, after_b, after_c]

        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
            "point_c_time": T3,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["leg1"]["passed"] is True


# ═══════════════════════════════════════════════════════
# 7. check_3m_stability 测试
# ═══════════════════════════════════════════════════════
class Test3mStability:

    @patch("futures.color_tracker._get_recent_macd_colors")
    def test_stable_long(self, mock_colors: MagicMock) -> None:
        """做多：RED为主 + 切换次数≤3 → stable"""
        mock_colors.return_value = [
            COLOR_RED, COLOR_RED, COLOR_RED, COLOR_RED,
            COLOR_BLUE, COLOR_RED, COLOR_RED, COLOR_RED,
        ]
        result = check_3m_stability("RB", "rb2510", "LONG", _test_db)
        assert result["stable"] is True
        assert result["stats"]["dominant_color"] == COLOR_RED
        assert result["stats"]["color_ok"] is True

    @patch("futures.color_tracker._get_recent_macd_colors")
    def test_stable_short(self, mock_colors: MagicMock) -> None:
        """做空：BLUE为主 + 切换次数≤3 → stable"""
        mock_colors.return_value = [
            COLOR_BLUE, COLOR_BLUE, COLOR_BLUE, COLOR_BLUE,
            COLOR_RED, COLOR_BLUE, COLOR_BLUE, COLOR_BLUE,
        ]
        result = check_3m_stability("RB", "rb2510", "SHORT", _test_db)
        assert result["stable"] is True
        assert result["stats"]["dominant_color"] == COLOR_BLUE
        assert result["stats"]["color_ok"] is True

    @patch("futures.color_tracker._get_recent_macd_colors")
    def test_unstable_wrong_color(self, mock_colors: MagicMock) -> None:
        """做多但BLUE为主 → unstable"""
        mock_colors.return_value = [
            COLOR_BLUE, COLOR_BLUE, COLOR_BLUE, COLOR_BLUE,
            COLOR_BLUE, COLOR_BLUE, COLOR_BLUE, COLOR_RED,
        ]
        result = check_3m_stability("RB", "rb2510", "LONG", _test_db)
        assert result["stable"] is False
        assert result["stats"]["color_ok"] is False

    @patch("futures.color_tracker._get_recent_macd_colors")
    def test_unstable_too_many_switches(self, mock_colors: MagicMock) -> None:
        """切换次数超过限制 → unstable"""
        mock_colors.return_value = [
            COLOR_RED, COLOR_BLUE, COLOR_RED, COLOR_BLUE,
            COLOR_RED, COLOR_BLUE, COLOR_RED, COLOR_RED,
        ]
        result = check_3m_stability("RB", "rb2510", "LONG", _test_db)
        assert result["stable"] is False
        assert result["stats"]["switch_ok"] is False

    @patch("futures.color_tracker._get_recent_macd_colors")
    def test_invalid_direction(self, mock_colors: MagicMock) -> None:
        """无效方向 → stable=False"""
        result = check_3m_stability("RB", "rb2510", "INVALID", _test_db)
        assert result["stable"] is False
        assert "无效方向" in result["reason"]

    @patch("futures.color_tracker._get_recent_macd_colors")
    def test_empty_colors(self, mock_colors: MagicMock) -> None:
        """无颜色数据 → stable=False"""
        mock_colors.return_value = []
        result = check_3m_stability("RB", "rb2510", "LONG", _test_db)
        assert result["stable"] is False


# ═══════════════════════════════════════════════════════
# 8. N型结构数据不完整
# ═══════════════════════════════════════════════════════
class TestMacdTrajectoryMissingData:

    @patch("futures.color_tracker._get_macd_in_range")
    def test_missing_a_time(self, mock_get_macd: MagicMock) -> None:
        """缺少A点时间 → passed=False"""
        n_struct = {
            "point_a_time": None,
            "point_b_time": T2,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "SHORT", _test_db)
        assert result["passed"] is False
        assert "缺" in result["leg1"]["detail"]

    @patch("futures.color_tracker._get_macd_in_range")
    def test_missing_direction(self, mock_get_macd: MagicMock) -> None:
        """缺少方向 → passed=False"""
        n_struct = {
            "point_a_time": T1,
            "point_b_time": T2,
        }
        result = check_macd_trajectory("RB", "rb2510", n_struct, "1d", "", _test_db)
        assert result["passed"] is False
