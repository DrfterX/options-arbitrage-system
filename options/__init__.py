"""
期权模块 — 策略计算与风险管理。

导出期权定价、比例价差、多策略、风险管理的关键函数和类。
"""

from options.pricing import black_price, black_greeks, calc_iv, normal_cdf, calc_win_rate
from options.ratio_spread import (
    OptionLeg,
    RatioSpread,
    find_best_strategies,
    find_all_strategies,
    get_contract_multiplier,
    parse_option_from_market_data,
)
from options.multi_strategy import (
    find_best_short_strangle,
    find_best_iron_condor,
    calc_unified_score,
)
from options.risk_manager import RiskCheckResult, RiskManager

__all__ = [
    # pricing
    "black_price",
    "black_greeks",
    "calc_iv",
    "normal_cdf",
    "calc_win_rate",
    # ratio_spread
    "OptionLeg",
    "RatioSpread",
    "find_best_strategies",
    "find_all_strategies",
    "get_contract_multiplier",
    "parse_option_from_market_data",
    # multi_strategy
    "find_best_short_strangle",
    "find_best_iron_condor",
    "calc_unified_score",
    # risk_manager
    "RiskCheckResult",
    "RiskManager",
]
