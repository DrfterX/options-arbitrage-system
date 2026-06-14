"""测试 futures/scorer.py 的 evaluate() — 离散3分制版

从旧期货项目迁移，调整了导入路径和 db 参数。
3分硬条件：Level1+L2+L3全通过=3分(ENTRY)，有加分=4分(ADD_POSITION)，不足3分=NONE。
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
# 1. Level1未通过 → overall_score=0, signal_type=NONE
# ═══════════════════════════════════════════════════════
class TestLevel1Fail:

    @patch("futures.scorer._get_active_n_structure", return_value=None)
    def test_no_l1_structure(self, mock_get: MagicMock) -> None:
        """无周线活跃N型 → score=0, NONE"""
        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0
        assert result.signal_type == "NONE"
        assert result.direction == "NONE"
        assert result.level1["passed"] is False

    @patch("futures.scorer._get_active_n_structure")
    def test_l1_wrong_state(self, mock_get: MagicMock) -> None:
        """L1状态为COMPLETED → score=0, NONE"""
        mock_get.return_value = make_l1_struct(state="COMPLETED")
        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0
        assert result.signal_type == "NONE"

    @patch("futures.scorer._get_active_n_structure")
    def test_l1_state_idle(self, mock_get: MagicMock) -> None:
        """L1状态为IDLE → score=0, NONE"""
        mock_get.return_value = make_l1_struct(state="IDLE")
        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0
        assert result.signal_type == "NONE"

    @patch("futures.scorer._get_active_n_structure")
    def test_l1_state_leg1(self, mock_get: MagicMock) -> None:
        """L1状态为LEG1 → score=0, NONE"""
        mock_get.return_value = make_l1_struct(state="LEG1")
        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 0
        assert result.signal_type == "NONE"


# ═══════════════════════════════════════════════════════
# 2. Level1通过+Level2未通过 → NONE（删除降级路径）
# ═══════════════════════════════════════════════════════
class TestLevel1PassLevel2Fail:

    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l2_no_structure(
        self, mock_macd: MagicMock, mock_get: MagicMock,
    ) -> None:
        """L2无活跃N型 → score=1, NONE（旧: 0.3, WATCH）"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct()
            return None  # L2无结构

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)

        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 1  # 只有Level1的1分
        assert result.signal_type == "NONE"
        assert result.level1["passed"] is True
        assert result.level2["passed"] is False

    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l2_direction_mismatch(
        self, mock_macd: MagicMock, mock_get: MagicMock,
    ) -> None:
        """L2方向不一致 → score=1, NONE"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            return make_l2_struct(direction="SHORT")  # 方向不一致

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)

        result = evaluate("RB", "rb2510", _test_db)
        assert result.overall_score == 1
        assert result.signal_type == "NONE"

    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l2_macd_not_passed(
        self, mock_macd: MagicMock, mock_get: MagicMock,
    ) -> None:
        """L2 MACD轨迹未通过 → score=1（仅L1通过），NONE"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            elif timeframe == LEVEL2_TIMEFRAME:
                return make_l2_struct(direction="LONG")
            return None  # L3无结构（Level2通过后会走到Level3）

        def macd_side_effect(symbol, contract, n_struct, tf, direction, db):
            if tf == "1d":  # L1 MACD
                return make_macd_result(passed=True)
            return make_macd_result(passed=False)  # L2 MACD未通过

        mock_get.side_effect = get_struct_side_effect
        mock_macd.side_effect = macd_side_effect

        result = evaluate("RB", "rb2510", _test_db)
        # MACD未通过 → Level2不得分 → score=1仅L1
        # < 3分 → NONE
        assert result.overall_score == 1
        assert result.signal_type == "NONE"
        assert result.level2["passed"] is False
        assert result.level2["macd_passed"] is False


# ═══════════════════════════════════════════════════════
# 3. Level1+2通过+Level3未突破 → NONE（删除降级路径）
# ═══════════════════════════════════════════════════════
class TestLevel3NoBreakout:

    @patch("futures.scorer.check_realtime_breakout")
    @patch("futures.scorer.check_3m_stability")
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l3_no_breakout(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_stability: MagicMock,
        mock_breakout: MagicMock,
    ) -> None:
        """L3突破未触发 → score=2, NONE（旧: 0.6, CANDIDATE）"""

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
        assert result.overall_score == 2  # Level1+2通过=2分
        assert result.signal_type == "NONE"  # 不足3分 → NONE

    @patch("futures.scorer.check_realtime_breakout")
    @patch("futures.scorer.check_3m_stability")
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_l3_not_stable(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_stability: MagicMock,
        mock_breakout: MagicMock,
    ) -> None:
        """L3 3分钟不稳定 → score=2, NONE（旧: 0.6, CANDIDATE）"""

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
        assert result.overall_score == 2
        assert result.signal_type == "NONE"


# ═══════════════════════════════════════════════════════
# 4. 全通过 → overall_score=3, signal_type=ENTRY（3分入场）
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
        """全通过LONG，无加分 → score=3, ENTRY"""

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
        assert result.overall_score == 3  # 3分入场
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
        """全通过SHORT，无加分 → score=3, ENTRY"""

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
        assert result.overall_score == 3
        assert result.signal_type == "ENTRY"
        assert result.direction == "SHORT"


# ═══════════════════════════════════════════════════════
# 5. 止损止盈计算 — LONG方向
# ═══════════════════════════════════════════════════════
class TestSLTPLong:

    def test_long_leg2_sl_tp(self) -> None:
        """LONG LEG2: SL=C点, TP=entry + L1振幅(600)=4205"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="LONG")
        result.entry_price = 3605.0
        n_struct = {
            "point_a_price": 3500.0,
            "point_b_price": 3600.0,
            "point_c_price": 3530.0,
            "state": "LEG2",
        }
        l1_struct = {"point_a_price": 3200.0, "point_b_price": 3800.0}
        sl, tp = _calculate_sl_tp(result, n_struct, l1_struct)
        assert sl == 3530.0  # C点（最近极值）
        assert tp == pytest.approx(4205.0)  # 3605 + 600(振幅)

    def test_long_leg3_sl_tp(self) -> None:
        """LONG LEG3: SL=B点, TP=entry + L1振幅(600)=4255"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="LONG")
        result.entry_price = 3655.0
        n_struct = {
            "point_a_price": 3500.0,
            "point_b_price": 3600.0,
            "point_c_price": 3650.0,
            "state": "LEG3",
        }
        l1_struct = {"point_a_price": 3200.0, "point_b_price": 3800.0}
        sl, tp = _calculate_sl_tp(result, n_struct, l1_struct)
        assert sl == 3600.0  # B点（突破点变支撑）
        assert tp == pytest.approx(4255.0)  # 3655 + 600(振幅)

    def test_long_leg2_no_c_price(self) -> None:
        """LONG LEG2无C点: SL兜底B点, TP=entry + L1振幅(600)=4210"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="LONG")
        result.entry_price = 3610.0
        n_struct = {
            "point_a_price": 3500.0,
            "point_b_price": 3600.0,
            "state": "LEG2",
        }
        l1_struct = {"point_a_price": 3200.0, "point_b_price": 3800.0}
        sl, tp = _calculate_sl_tp(result, n_struct, l1_struct)
        assert sl == 3600.0  # 兜底用B点
        assert tp == pytest.approx(4210.0)  # 3610 + 600(振幅)


# ═══════════════════════════════════════════════════════
# 6. 止损止盈计算 — SHORT方向
# ═══════════════════════════════════════════════════════
class TestSLTPShort:

    def test_short_leg2_sl_tp(self) -> None:
        """SHORT LEG2: SL=C点(最近极值), TP=entry - L1振幅(600)=2915"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="SHORT")
        result.entry_price = 3515.0
        n_struct = {
            "point_a_price": 3600.0,
            "point_b_price": 3500.0,
            "point_c_price": 3580.0,
            "state": "LEG2",
        }
        l1_struct = {"point_a_price": 3800.0, "point_b_price": 3200.0}
        sl, tp = _calculate_sl_tp(result, n_struct, l1_struct)
        assert sl == 3580.0  # C点（最近极值）
        assert tp == pytest.approx(2915.0)  # 3515 - 600(振幅)

    def test_short_leg3_sl_tp(self) -> None:
        """SHORT LEG3: SL=B点(突破点变阻力), TP=entry - L1振幅(600)=2915"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="SHORT")
        result.entry_price = 3515.0
        n_struct = {
            "point_a_price": 3600.0,
            "point_b_price": 3500.0,
            "point_c_price": 3580.0,
            "state": "LEG3",
        }
        l1_struct = {"point_a_price": 3800.0, "point_b_price": 3200.0}
        sl, tp = _calculate_sl_tp(result, n_struct, l1_struct)
        assert sl == 3500.0  # B点（突破点变阻力）
        assert tp == pytest.approx(2915.0)  # 3515 - 600(振幅)

    def test_short_leg2_no_c_price(self) -> None:
        """SHORT LEG2无C点: SL兜底B点, TP=entry - L1振幅(600)=2915"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="SHORT")
        result.entry_price = 3515.0
        n_struct = {
            "point_a_price": 3600.0,
            "point_b_price": 3500.0,
            "state": "LEG2",
        }
        l1_struct = {"point_a_price": 3800.0, "point_b_price": 3200.0}
        sl, tp = _calculate_sl_tp(result, n_struct, l1_struct)
        assert sl == 3500.0  # 兜底用B点
        assert tp == pytest.approx(2915.0)  # 3515 - 600(振幅)


# ═══════════════════════════════════════════════════════
# 7. 加分项验证
# ═══════════════════════════════════════════════════════
class TestBonusScoring:

    def test_sl_tp_none_direction(self) -> None:
        """无效方向 → SL/TP = None"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="NONE")
        result.entry_price = 3550.0
        n_struct = {"point_a_price": 3500.0, "point_b_price": 3600.0}
        l1_struct = {"point_a_price": 3200.0, "point_b_price": 3800.0}
        sl, tp = _calculate_sl_tp(result, n_struct, l1_struct)
        assert sl is None
        assert tp is None

    def test_sl_tp_missing_prices(self) -> None:
        """缺少价格 → SL/TP = None"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="LONG")
        result.entry_price = 3550.0
        n_struct = {"point_a_price": None, "point_b_price": 3600.0}
        sl, tp = _calculate_sl_tp(result, n_struct, l1_struct={})
        assert sl is None
        assert tp is None

    def test_sl_tp_missing_entry(self) -> None:
        """缺少入场价 → SL/TP = None"""
        result = SignalResult(symbol="RB", contract="rb2510", direction="LONG")
        result.entry_price = None
        n_struct = {"point_a_price": 3500.0, "point_b_price": 3600.0}
        sl, tp = _calculate_sl_tp(result, n_struct, l1_struct={})
        assert sl is None
        assert tp is None

    @patch("futures.scorer._check_bonus", return_value=[
        {"check": "1mon+1w", "passed": True, "score": 1, "detail": "ok"},
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
        """3分+加分项通过 → 4分加仓(ADD_POSITION)"""

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
        # 3分 + 1加分 → 4分加仓
        assert result.overall_score == 4
        assert result.signal_type == "ADD_POSITION"
        assert len(result.bonus) == 2
        assert result.bonus[0]["score"] == 1
        assert result.bonus[1]["score"] == 0

    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_bonus_on_level2_fail(
        self, mock_macd: MagicMock, mock_get: MagicMock,
    ) -> None:
        """Level2失败 → score=1, NONE（删除降级路径，加分不补缺分）"""

        def get_struct_side_effect(db, symbol, contract, timeframe):
            if timeframe == LEVEL1_TIMEFRAME:
                return make_l1_struct(direction="LONG")
            return None  # L2无结构

        mock_get.side_effect = get_struct_side_effect
        mock_macd.return_value = make_macd_result(passed=True)

        result = evaluate("RB", "rb2510", _test_db)
        # Level2失败，只有Level1的1分，不足3分 → NONE
        assert result.overall_score == 1
        assert result.signal_type == "NONE"

    @patch("futures.scorer._check_bonus", return_value=[
        {"check": "1d+1h", "passed": True, "score": 1, "detail": "ok"},
        {"check": "1mon+1w", "passed": True, "score": 1, "detail": "ok"},
    ])
    @patch("futures.scorer.check_realtime_breakout")
    @patch("futures.scorer.check_3m_stability")
    @patch("futures.scorer._get_active_n_structure")
    @patch("futures.scorer.check_macd_trajectory")
    def test_bonus_capped_at_4(
        self, mock_macd: MagicMock, mock_get: MagicMock, mock_stability: MagicMock,
        mock_breakout: MagicMock, mock_bonus: MagicMock,
    ) -> None:
        """3分+多个加分项 → 4分（有加分就4分加仓，不累加）"""

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
        # 3分+加分→4分加仓，不累加到5分
        assert result.overall_score == 4
        assert result.signal_type == "ADD_POSITION"
