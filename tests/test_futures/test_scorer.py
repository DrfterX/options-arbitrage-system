"""测试 futures/scorer.py 的 evaluate() 和 _calculate_sl_tp()

从旧期货项目迁移，调整了导入路径和 db 参数。
"""

import pytest
from unittest.mock import patch, MagicMock

from futures.scorer import evaluate, _calculate_sl_tp, SignalResult
from config.settings import LEVEL1_TIMEFRAME, LEVEL2_TIMEFRAME, LEVEL3_TIMEFRAME
from core.db import Database
from tests.conftest import T1, T2, T3

# 共享的测试用内存数据库（所有DB函数都被mock，db实例不重要）
_test_db: Database = Database(":memory:")


# ═══════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════

def make_l1_struct(direction: str = "LONG", state: str = "LEG3") -> dict:
    """构造 Level1 N型结构。"""
    return {
        "direction": direction,
        "state": state,
        "point_a_time": T1,
        "point_a_price": 90.0,
        "point_b_time": T2,
        "point_b_price": 110.0,
        "point_c_time": T3,
        "point_c_price": 95.0,
    }


def make_l2_struct(direction: str = "LONG", state: str = "LEG3") -> dict:
    """构造 Level2 N型结构。"""
    return {
        "direction": direction,
        "state": state,
        "point_a_time": T1,
        "point_a_price": 3500.0,
        "point_b_time": T2,
        "point_b_price": 3600.0,
        "point_c_time": T3,
        "point_c_price": 3550.0,
    }


def make_l3_struct(direction: str = "LONG", state: str = "LEG3") -> dict:
    """构造 Level3 N型结构。"""
    return {
        "direction": direction,
        "state": state,
        "point_a_time": T1,
        "point_a_price": 3520.0,
        "point_b_time": T2,
        "point_b_price": 3580.0,
        "point_c_time": T3,
        "point_c_price": 3540.0,
    }


def make_macd_result(passed: bool = True, desc: str = "MACD OK") -> dict:
    """构造 MACD轨迹检查结果。"""
    return {
        "passed": passed,
        "leg1": {"passed": passed, "detail": desc},
        "leg2": {"passed": passed, "detail": desc},
        "leg3": {"passed": True, "detail": "leg3 ok"},
        "description": desc,
    }


def make_breakout_result(
    triggered: bool = True,
    is_fresh: bool = True,
    direction: str = "LONG",
    breakout_price: float = 3580.0,
    trigger_price: float = 3585.0,
) -> dict:
    """构造突破检测结果。"""
    return {
        "triggered": triggered,
        "is_fresh": is_fresh,
        "direction": direction,
        "breakout_price": breakout_price,
        "trigger_price": trigger_price,
        "trigger_time": T3,
        "detail": "test breakout",
        "current_price": trigger_price,
    }


def make_stability_result(stable: bool = True) -> dict:
    """构造3分钟稳定性结果。"""
    return {
        "stable": stable,
        "stats": {
            "switch_count": 1 if stable else 5,
            "dominant_color": "RED" if stable else "BLUE",
        },
        "reason": None if stable else "too many switches",
    }


# ═══════════════════════════════════════════════════════
# 1. Level1未通过 → overall_score=0.0, signal_type=NONE
# ═══════════════════════════════════════════════════════
class TestLevel1Fail:

    @patch("futures.scorer._get_active_n_structure", return_value=None)
    def test_no_l1_structure(self, mock_get: MagicMock) -> None:
        """无周线活跃N型 → score=0.0, NONE"""
        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0.0
        assert result.signal_type == "NONE"
        assert result.direction == "NONE"
        assert result.level1["passed"] is False

    @patch("futures.scorer._get_active_n_structure")
    def test_l1_wrong_state(self, mock_get: MagicMock) -> None:
        """L1状态为COMPLETED → score=0.0, NONE"""
        mock_get.return_value = make_l1_struct(state="COMPLETED")
        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0.0
        assert result.signal_type == "NONE"

    @patch("futures.scorer._get_active_n_structure")
    def test_l1_state_idle(self, mock_get: MagicMock) -> None:
        """L1状态为IDLE → score=0.0, NONE"""
        mock_get.return_value = make_l1_struct(state="IDLE")
        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0.0
        assert result.signal_type == "NONE"

    @patch("futures.scorer._get_active_n_structure")
    def test_l1_state_leg1(self, mock_get: MagicMock) -> None:
        """L1状态为LEG1 → score=0.0, NONE"""
        mock_get.return_value = make_l1_struct(state="LEG1")
        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0.0
        assert result.signal_type == "NONE"


# ═══════════════════════════════════════════════════════
# 2. Level1通过+Level2未通过 → overall_score=0.3, signal_type=WATCH
# ═══════════════════════════════════════════════════════
class TestLevel1PassLevel2Fail:

    @patch("futures.scorer._check_bonus", return_value=[])
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l2_no_structure(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """L2无活跃N型 → score=0.3, WATCH"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct()
            return None  # L2无结构

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)

        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0.3
        assert result.signal_type == "WATCH"
        assert result.level1["passed"] is True
        assert result.level2["passed"] is False

    @patch("futures.scorer._check_bonus", return_value=[])
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l2_direction_mismatch(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """L2方向不一致 → score=0.3, WATCH"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            return make_l2_struct(direction="SHORT")  # 方向不一致

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)

        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0.3
        assert result.signal_type == "WATCH"

    @patch("futures.scorer._check_bonus", return_value=[])
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l2_macd_not_passed(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """L2 MACD轨迹未通过 → score=0.3, WATCH"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            return make_l2_struct(direction="LONG")

        def macd_side_effect(symbol, contract, n_struct, tf, direction, db):
            if tf == "1d":  # L1 MACD
                return make_macd_result(passed=True)
            return make_macd_result(passed=False)  # L2 MACD未通过

        mock_get.side_effect = get_struct_side_effect
        mock_macd.side_effect = macd_side_effect

        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0.3
        assert result.signal_type == "WATCH"


# ═══════════════════════════════════════════════════════
# 3. Level1+2通过+Level3未突破 → overall_score=0.6, signal_type=CANDIDATE
# ═══════════════════════════════════════════════════════
class TestLevel3NoBreakout:

    @patch("futures.scorer._check_bonus", return_value=[])
    @patch("futures.scorer.check_realtime_breakout")
    @patch("futures.scorer.check_3m_stability")
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l3_no_breakout(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_stability: MagicMock,
        mock_breakout: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """L3突破未触发 → score=0.6, CANDIDATE"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            elif timeframe == LEVEL2_TIMEFRAME:
                return make_l2_struct(direction="LONG")
            return make_l3_struct(direction="LONG")

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)
        mock_stability.return_value = make_stability_result(stable=True)
        mock_breakout.return_value = make_breakout_result(triggered=False, is_fresh=False)

        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0.6
        assert result.signal_type == "CANDIDATE"

    @patch("futures.scorer._check_bonus", return_value=[])
    @patch("futures.scorer.check_realtime_breakout")
    @patch("futures.scorer.check_3m_stability")
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l3_not_stable(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_stability: MagicMock,
        mock_breakout: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """L3 3分钟不稳定 → score=0.6, CANDIDATE"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            elif timeframe == LEVEL2_TIMEFRAME:
                return make_l2_struct(direction="LONG")
            return make_l3_struct(direction="LONG")

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)
        mock_stability.return_value = make_stability_result(stable=False)
        mock_breakout.return_value = make_breakout_result(triggered=True, is_fresh=True)

        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0.6
        assert result.signal_type == "CANDIDATE"


# ═══════════════════════════════════════════════════════
# 4. 全通过 → overall_score=1.0, signal_type=ENTRY
# ═══════════════════════════════════════════════════════
class TestAllLevelsPass:

    @patch("futures.scorer._check_bonus", return_value=[])
    @patch("futures.scorer.check_realtime_breakout")
    @patch("futures.scorer.check_3m_stability")
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_all_pass_long(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_stability: MagicMock,
        mock_breakout: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """全通过LONG → score=1.0, ENTRY"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            elif timeframe == LEVEL2_TIMEFRAME:
                return make_l2_struct(direction="LONG")
            return make_l3_struct(direction="LONG")

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)
        mock_stability.return_value = make_stability_result(stable=True)
        mock_breakout.return_value = make_breakout_result(
            triggered=True, is_fresh=True, direction="LONG",
            breakout_price=3580.0, trigger_price=3585.0,
        )

        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 1.0
        assert result.signal_type == "ENTRY"
        assert result.direction == "LONG"
        assert result.entry_price == 3585.0
        assert result.stop_loss is not None
        assert result.take_profit is not None

    @patch("futures.scorer._check_bonus", return_value=[])
    @patch("futures.scorer.check_realtime_breakout")
    @patch("futures.scorer.check_3m_stability")
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_all_pass_short(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_stability: MagicMock,
        mock_breakout: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """全通过SHORT → score=1.0, ENTRY"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="SHORT")
            elif timeframe == LEVEL2_TIMEFRAME:
                return make_l2_struct(direction="SHORT")
            return make_l3_struct(direction="SHORT")

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)
        mock_stability.return_value = make_stability_result(stable=True)
        mock_breakout.return_value = make_breakout_result(
            triggered=True, is_fresh=True, direction="SHORT",
            breakout_price=3520.0, trigger_price=3515.0,
        )

        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 1.0
        assert result.signal_type == "ENTRY"
        assert result.direction == "SHORT"


# ═══════════════════════════════════════════════════════
# 5. 止损止盈计算 — LONG方向
# ═══════════════════════════════════════════════════════
class TestSLTPLong:

    def test_long_sl_tp(self) -> None:
        """LONG: SL=A点, TP=entry + height*0.5"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="LONG")
        result.entry_price = 3600.0
        n_struct = {"point_a_price": 3500.0, "point_b_price": 3600.0}
        sl, tp = _calculate_sl_tp(result, n_struct)
        assert sl == 3500.0
        assert tp == 3650.0

    def test_long_sl_tp_small_height(self) -> None:
        """LONG: 小高度"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="LONG")
        result.entry_price = 3550.0
        n_struct = {"point_a_price": 3540.0, "point_b_price": 3560.0}
        sl, tp = _calculate_sl_tp(result, n_struct)
        assert sl == 3540.0
        assert tp == 3560.0


# ═══════════════════════════════════════════════════════
# 6. 止损止盈计算 — SHORT方向
# ═══════════════════════════════════════════════════════
class TestSLTPShort:

    def test_short_sl_tp(self) -> None:
        """SHORT: SL=A点, TP=entry - height*0.5"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="SHORT")
        result.entry_price = 3500.0
        n_struct = {"point_a_price": 3600.0, "point_b_price": 3500.0}
        sl, tp = _calculate_sl_tp(result, n_struct)
        assert sl == 3600.0
        assert tp == 3450.0

    def test_short_sl_tp_small_height(self) -> None:
        """SHORT: 小高度"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="SHORT")
        result.entry_price = 3550.0
        n_struct = {"point_a_price": 3560.0, "point_b_price": 3540.0}
        sl, tp = _calculate_sl_tp(result, n_struct)
        assert sl == 3560.0
        assert tp == 3540.0


# ═══════════════════════════════════════════════════════
# 7. 加分项验证
# ═══════════════════════════════════════════════════════
class TestBonusScoring:

    def test_sl_tp_none_direction(self) -> None:
        """无效方向 → SL/TP = None"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="NONE")
        result.entry_price = 3550.0
        n_struct = {"point_a_price": 3500.0, "point_b_price": 3600.0}
        sl, tp = _calculate_sl_tp(result, n_struct)
        assert sl is None
        assert tp is None

    def test_sl_tp_missing_prices(self) -> None:
        """缺少价格 → SL/TP = None"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="LONG")
        result.entry_price = 3550.0
        n_struct = {"point_a_price": None, "point_b_price": 3600.0}
        sl, tp = _calculate_sl_tp(result, n_struct)
        assert sl is None
        assert tp is None

    def test_sl_tp_missing_entry(self) -> None:
        """缺少入场价 → SL/TP = None"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="LONG")
        result.entry_price = None
        n_struct = {"point_a_price": 3500.0, "point_b_price": 3600.0}
        sl, tp = _calculate_sl_tp(result, n_struct)
        assert sl is None
        assert tp is None

    @patch("futures.scorer._check_bonus", return_value=[
        {"check": "1mon+1w", "passed": True, "score": 0.15, "detail": "ok"},
        {"check": "1d+1h", "passed": False, "score": 0, "detail": "fail"},
    ])
    @patch("futures.scorer.check_realtime_breakout")
    @patch("futures.scorer.check_3m_stability")
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_bonus_adds_to_score(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_stability: MagicMock,
        mock_breakout: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """加分项被正确加到overall_score上"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            elif timeframe == LEVEL2_TIMEFRAME:
                return make_l2_struct(direction="LONG")
            return make_l3_struct(direction="LONG")

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)
        mock_stability.return_value = make_stability_result(stable=True)
        mock_breakout.return_value = make_breakout_result(
            triggered=True, is_fresh=True, direction="LONG",
        )

        result = evaluate("RB", "rb2510", _test_db)
        # 基础分1.0 + bonus 0.15 = 1.15 → capped at 1.0
        assert result.overall_score == 1.0
        assert len(result.bonus) == 2
        assert result.bonus[0]["score"] == 0.15
        assert result.bonus[1]["score"] == 0

    @patch("futures.scorer._check_bonus", return_value=[
        {"check": "1mon+1w", "passed": True, "score": 0.15, "detail": "ok"},
    ])
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_bonus_on_level2_fail(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """Level2失败时，加分项仍被加到0.3上"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            return None  # L2无结构

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)

        result = evaluate("RB", "rb2510", _test_db)
        # 0.3 + 0.15 = 0.45 (浮点精度)
        assert result.overall_score == pytest.approx(0.45)
        assert result.signal_type == "WATCH"

    @patch("futures.scorer._check_bonus", return_value=[
        {"check": "1d+1h", "passed": True, "score": 0.10, "detail": "ok"},
        {"check": "1mon+1w", "passed": True, "score": 0.15, "detail": "ok"},
    ])
    @patch("futures.scorer.check_realtime_breakout")
    @patch("futures.scorer.check_3m_stability")
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_bonus_capped_at_1(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_stability: MagicMock,
        mock_breakout: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """加分项使分数超过1.0 → 被capped"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            elif timeframe == LEVEL2_TIMEFRAME:
                return make_l2_struct(direction="LONG")
            return make_l3_struct(direction="LONG")

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)
        mock_stability.return_value = make_stability_result(stable=True)
        mock_breakout.return_value = make_breakout_result(
            triggered=True, is_fresh=True, direction="LONG",
        )

        result = evaluate("RB", "rb2510", _test_db)
        # 1.0 + 0.10 + 0.15 = 1.25 → capped at 1.0
        assert result.overall_score == 1.0
