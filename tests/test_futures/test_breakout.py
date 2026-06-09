"""测试 futures/n_structure.py 的 check_realtime_breakout() 突破检测。

从旧期货项目迁移，调整了导入路径和 db 参数。
"""

import pytest
from unittest.mock import patch, MagicMock

from futures.n_structure import check_realtime_breakout
from core.db import Database
from tests.conftest import make_kline, T1, T2, T3

_test_db: Database = Database(":memory:")


# ═══════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════

def make_long_n_struct(b_price: float = 3580.0) -> dict:
    """构造做多的N型结构。"""
    return {
        "direction": "LONG",
        "state": "LEG3",
        "point_a_price": 3520.0,
        "point_b_price": b_price,
        "point_c_price": 3540.0,
    }


def make_short_n_struct(b_price: float = 3520.0) -> dict:
    """构造做空的N型结构。"""
    return {
        "direction": "SHORT",
        "state": "LEG3",
        "point_a_price": 3580.0,
        "point_b_price": b_price,
        "point_c_price": 3560.0,
    }


# ═══════════════════════════════════════════════════════
# 1. 正常突破（prev未突破 + last已突破）
# ═══════════════════════════════════════════════════════
class TestNormalBreakout:

    @patch("futures.n_structure._get_klines")
    def test_long_normal_breakout(self, mock_klines: MagicMock) -> None:
        """LONG: prev未突破(3575<B=3580), last已突破(3585>B=3580) → triggered=True, is_fresh=True"""
        mock_klines.return_value = [
            make_kline(T1, 3575.0),  # prev: 未突破
            make_kline(T2, 3585.0),  # last: 已突破
        ]
        result = check_realtime_breakout("RB", "rb2510", make_long_n_struct(), _test_db)
        assert result["triggered"] is True
        assert result["is_fresh"] is True
        assert result["direction"] == "LONG"
        assert result["trigger_price"] == 3585.0

    @patch("futures.n_structure._get_klines")
    def test_short_normal_breakout(self, mock_klines: MagicMock) -> None:
        """SHORT: prev未突破(3525>B=3520), last已突破(3515<=B=3520) → triggered=True, is_fresh=True"""
        mock_klines.return_value = [
            make_kline(T1, 3525.0),  # prev: 未突破(>B)
            make_kline(T2, 3515.0),  # last: 已突破(<=B)
        ]
        result = check_realtime_breakout("RB", "rb2510", make_short_n_struct(), _test_db)
        assert result["triggered"] is True
        assert result["is_fresh"] is True
        assert result["direction"] == "SHORT"
        assert result["trigger_price"] == 3515.0


# ═══════════════════════════════════════════════════════
# 2. 连续突破（prev也突破）→ 非新鲜
# ═══════════════════════════════════════════════════════
class TestContinuousBreakout:

    @patch("futures.n_structure._get_klines")
    def test_long_continuous_breakout(self, mock_klines: MagicMock) -> None:
        """LONG: prev也突破(3585>B) + last也突破(3590>B) → triggered=False, is_fresh=False"""
        mock_klines.return_value = [
            make_kline(T1, 3585.0),  # prev: 已突破
            make_kline(T2, 3590.0),  # last: 也突破
        ]
        result = check_realtime_breakout("RB", "rb2510", make_long_n_struct(), _test_db)
        assert result["triggered"] is False
        assert result["is_fresh"] is False

    @patch("futures.n_structure._get_klines")
    def test_short_continuous_breakout(self, mock_klines: MagicMock) -> None:
        """SHORT: prev也突破(3515<=B) + last也突破(3510<=B) → triggered=False"""
        mock_klines.return_value = [
            make_kline(T1, 3515.0),  # prev: 已突破
            make_kline(T2, 3510.0),  # last: 也突破
        ]
        result = check_realtime_breakout("RB", "rb2510", make_short_n_struct(), _test_db)
        assert result["triggered"] is False
        assert result["is_fresh"] is False


# ═══════════════════════════════════════════════════════
# 3. 只有1根bar → 不crash
# ═══════════════════════════════════════════════════════
class TestSingleBar:

    @patch("futures.n_structure._get_klines")
    def test_single_bar_long_breakout(self, mock_klines: MagicMock) -> None:
        """只有1根bar且突破 → triggered=True（prev=None → not prev_breaks）"""
        mock_klines.return_value = [
            make_kline(T1, 3590.0),  # 已突破
        ]
        result = check_realtime_breakout("RB", "rb2510", make_long_n_struct(), _test_db)
        assert result["triggered"] is True
        assert result["is_fresh"] is True

    @patch("futures.n_structure._get_klines")
    def test_single_bar_no_breakout(self, mock_klines: MagicMock) -> None:
        """只有1根bar且未突破 → triggered=False"""
        mock_klines.return_value = [
            make_kline(T1, 3570.0),  # 未突破
        ]
        result = check_realtime_breakout("RB", "rb2510", make_long_n_struct(), _test_db)
        assert result["triggered"] is False
        assert result["is_fresh"] is False


# ═══════════════════════════════════════════════════════
# 4. 空bar列表 → 不crash
# ═══════════════════════════════════════════════════════
class TestEmptyBars:

    @patch("futures.n_structure._get_klines")
    def test_empty_bar_list(self, mock_klines: MagicMock) -> None:
        """空K线列表 → triggered=False, 不crash"""
        mock_klines.return_value = []
        result = check_realtime_breakout("RB", "rb2510", make_long_n_struct(), _test_db)
        assert result["triggered"] is False
        assert "无法获取" in result["detail"]


# ═══════════════════════════════════════════════════════
# 5. prev_bar价格恰好等于B点
# ═══════════════════════════════════════════════════════
class TestExactEquality:

    @patch("futures.n_structure._get_klines")
    def test_long_prev_equals_b_not_breakout(self, mock_klines: MagicMock) -> None:
        """LONG: prev close恰好等于B(>=算突破) → prev_breaks=True"""
        mock_klines.return_value = [
            make_kline(T1, 3580.0),  # prev: == B → >= B → 算突破
            make_kline(T2, 3590.0),  # last: 已突破
        ]
        result = check_realtime_breakout("RB", "rb2510", make_long_n_struct(b_price=3580.0), _test_db)
        assert result["triggered"] is False
        assert result["is_fresh"] is False

    @patch("futures.n_structure._get_klines")
    def test_short_prev_equals_b_counts_as_breakout(self, mock_klines: MagicMock) -> None:
        """SHORT: prev close恰好等于B(<=算突破) → prev_breaks=True"""
        mock_klines.return_value = [
            make_kline(T1, 3520.0),  # prev: == B → <= B → 算突破
            make_kline(T2, 3510.0),  # last: 已突破
        ]
        result = check_realtime_breakout("RB", "rb2510", make_short_n_struct(b_price=3520.0), _test_db)
        assert result["triggered"] is False
        assert result["is_fresh"] is False

    @patch("futures.n_structure._get_klines")
    def test_long_last_equals_b_is_breakout(self, mock_klines: MagicMock) -> None:
        """LONG: last close恰好等于B → >= B → 算突破"""
        mock_klines.return_value = [
            make_kline(T1, 3570.0),  # prev: 未突破
            make_kline(T2, 3580.0),  # last: == B → >= B → 算突破
        ]
        result = check_realtime_breakout("RB", "rb2510", make_long_n_struct(b_price=3580.0), _test_db)
        assert result["triggered"] is True
        assert result["is_fresh"] is True

    @patch("futures.n_structure._get_klines")
    def test_no_n_structure(self, mock_klines: MagicMock) -> None:
        """无N型结构 → triggered=False"""
        mock_klines.return_value = [
            make_kline(T1, 3570.0),
            make_kline(T2, 3590.0),
        ]
        result = check_realtime_breakout("RB", "rb2510", None, _test_db)
        assert result["triggered"] is False

    @patch("futures.n_structure._get_klines")
    def test_n_structure_no_b_price(self, mock_klines: MagicMock) -> None:
        """N型结构无B点价格 → triggered=False"""
        mock_klines.return_value = [
            make_kline(T1, 3570.0),
            make_kline(T2, 3590.0),
        ]
        n_struct = {"direction": "LONG", "point_b_price": None}
        result = check_realtime_breakout("RB", "rb2510", n_struct, _test_db)
        assert result["triggered"] is False
