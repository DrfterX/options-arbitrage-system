"""
期货N型信号分析引擎 — 多周期MACD + 波峰波谷 + N型状态机 + 三级嵌套评分。

导出关键函数和类供外部调用。
"""

from futures.aggregator import aggregate_all
from futures.macd import calculate_macd, calculate_and_save, calculate_all_timeframes
from futures.swing_points import detect_swing_points, incremental_update, update_all_timeframes
from futures.n_structure import (
    NState,
    detect_and_save,
    check_15m_breakout,
    check_realtime_breakout,
)
from futures.scorer import SignalResult, evaluate, scan_all_contracts
from futures.color_tracker import (
    check_color_sequence,
    check_macd_trajectory,
    check_3m_stability,
)

__all__ = [
    # aggregator
    "aggregate_all",
    # macd
    "calculate_macd",
    "calculate_and_save",
    "calculate_all_timeframes",
    # swing_points
    "detect_swing_points",
    "incremental_update",
    "update_all_timeframes",
    # n_structure
    "NState",
    "detect_and_save",
    "check_15m_breakout",
    "check_realtime_breakout",
    # scorer
    "SignalResult",
    "evaluate",
    "scan_all_contracts",
    # color_tracker
    "check_color_sequence",
    "check_macd_trajectory",
    "check_3m_stability",
]
