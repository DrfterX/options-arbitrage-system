"""
比例价差策略计算器 — 共享模块。

核心理念:
- 买入腿: ATM或近虚值 (Delta 0.30~0.70)
- 卖出腿: 远虚值 (Delta 0.15~0.35)
- 配比: 1:2
- Delta中性: |组合Delta| <= 0.10
- 高IV入场: IV >= 25%
- 流动性: 单腿OI >= 300
- 盈利来源: Theta decay + Vega Short (做空波动率)
"""

import math
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from config.settings import MIN_IV, MAX_DELTA_ABS, MIN_OI, MAX_MARGIN, MAX_COST_RATIO
from config.contracts import ContractRegistry
from options.pricing import normal_cdf

logger = logging.getLogger(__name__)

# 卖出:买入配比
RATIO: int = 2


# ---- 数据类 ----


@dataclass
class OptionLeg:
    """单个期权腿数据。

    Attributes:
        strike: 执行价。
        bid: 买价。
        ask: 卖价。
        mid: 中间价。
        delta: Delta。
        gamma: Gamma。
        theta: Theta。
        vega: Vega。
        iv: 隐含波动率（小数）。
        oi: 持仓量。
        volume: 成交量。
    """

    strike: float
    bid: float
    ask: float
    mid: float
    delta: float
    gamma: float
    theta: float
    vega: float
    iv: float
    oi: int
    volume: int


@dataclass
class RatioSpread:
    """比例价差策略完整数据。

    Attributes:
        symbol: 品种代码。
        contract: 合约代码。
        underlying: 标的价格。
        iv_avg: 平均隐含波动率。
        days_to_expiry: 到期天数。
        buy_leg: 买入腿。
        sell_leg: 卖出腿。
        net_delta: 组合Delta。
        net_gamma: 组合Gamma。
        net_theta: 组合Theta。
        net_vega: 组合Vega。
        net_cost: 净成本（正=支出，负=收入）。
        max_profit: 最大利润。
        breakeven_low: 下盈亏平衡点。
        breakeven_high: 上盈亏平衡点。
        profit_zone_width: 盈利区间宽度。
        win_rate: 胜率。
        score: 综合评分。
    """

    symbol: str
    contract: str
    underlying: float
    iv_avg: float
    days_to_expiry: int
    buy_leg: OptionLeg
    sell_leg: OptionLeg
    net_delta: float
    net_gamma: float
    net_theta: float
    net_vega: float
    net_cost: float
    max_profit: float
    breakeven_low: float
    breakeven_high: float
    profit_zone_width: float
    win_rate: float
    score: float
    score_components: dict = field(default_factory=dict)


# ---- 合约乘数查询 ----


def get_contract_multiplier(registry: ContractRegistry, symbol: str) -> int:
    """通过品种注册表查询合约乘数。

    Args:
        registry: ContractRegistry 实例。
        symbol: 品种代码。

    Returns:
        合约乘数，查询失败返回 1。
    """
    return registry.get_multiplier(symbol)


# ---- 期权数据解析 ----


def parse_option_from_market_data(
    opt_dict: dict,
    is_call: bool = True,
) -> Optional[OptionLeg]:
    """从市场监控数据格式解析期权为 OptionLeg。

    适配 data_fetcher 返回的期权数据格式::

        {
            'strike': float,
            'call_put': 'C'|'P',
            'price': float,
            'bid': float, 'ask': float,
            'volume': int, 'oi': int,
            'delta': float, 'gamma': float, 'theta': float, 'vega': float,
            'iv': float
        }

    Args:
        opt_dict: 原始期权数据字典。
        is_call: 是否看涨期权。

    Returns:
        OptionLeg 实例，解析失败返回 None。
    """
    cp = opt_dict.get("call_put", "C" if is_call else "P")
    if (is_call and cp != "C") or (not is_call and cp != "P"):
        return None

    strike = opt_dict.get("strike")
    if strike is None or strike <= 0:
        return None

    bid = opt_dict.get("bid", 0) or 0
    ask = opt_dict.get("ask", 0) or 0
    price = opt_dict.get("price", 0) or 0

    if bid > 0 and ask > 0 and bid < ask * 3:
        mid = (bid + ask) / 2.0
    elif price > 0:
        mid = price
        bid = price * 0.95
        ask = price * 1.05
    else:
        return None

    delta = opt_dict.get("delta", 0) or 0
    gamma = opt_dict.get("gamma", 0) or 0
    theta = opt_dict.get("theta", 0) or 0
    vega = opt_dict.get("vega", 0) or 0
    iv = opt_dict.get("iv", 0) or 0
    oi = opt_dict.get("oi", 0) or 0
    volume = opt_dict.get("volume", 0) or 0

    if oi < MIN_OI:
        return None

    return OptionLeg(
        strike=float(strike),
        bid=bid,
        ask=ask,
        mid=mid,
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        iv=iv / 100.0 if iv > 1 else iv,
        oi=int(oi),
        volume=int(volume),
    )


# ---- 核心计算 ----


def calc_call_ratio_spread(
    symbol: str,
    contract: str,
    underlying: float,
    iv_avg: float,
    dte: int,
    buy: OptionLeg,
    sell: OptionLeg,
    registry: ContractRegistry,
) -> Optional[RatioSpread]:
    """计算 Call Ratio Spread（买1低行权价Call, 卖2高行权价Call）。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        underlying: 标的价格。
        iv_avg: 平均隐含波动率。
        dte: 到期天数。
        buy: 买入腿。
        sell: 卖出腿。
        registry: ContractRegistry 实例。

    Returns:
        RatioSpread 实例，不满足条件时返回 None。
    """
    if buy.strike >= sell.strike:
        return None

    net_delta = buy.delta - RATIO * sell.delta
    if abs(net_delta) > MAX_DELTA_ABS:
        return None

    avg_iv = (buy.iv + sell.iv) / 2
    if avg_iv < MIN_IV and sell.iv < MIN_IV:
        return None

    net_cost = buy.mid - RATIO * sell.mid
    if net_cost > underlying * MAX_COST_RATIO:
        return None

    net_gamma = buy.gamma - RATIO * sell.gamma
    net_theta = buy.theta - RATIO * sell.theta
    net_vega = buy.vega - RATIO * sell.vega

    breakeven_low = buy.strike + net_cost
    breakeven_high = 2 * sell.strike - buy.strike - net_cost

    max_profit = sell.strike - buy.strike - net_cost
    if max_profit <= 0:
        return None

    profit_zone_width = breakeven_high - breakeven_low
    if profit_zone_width <= 0:
        return None

    t = dte / 365.0
    if t <= 0 or iv_avg <= 0:
        return None

    sigma_sqrt_t = iv_avg * math.sqrt(t)

    if breakeven_low > 0:
        d_low = (
            math.log(breakeven_low / underlying) - 0.5 * iv_avg * iv_avg * t
        ) / sigma_sqrt_t
    else:
        d_low = -999.0

    if breakeven_high > 0:
        d_high = (
            math.log(breakeven_high / underlying) - 0.5 * iv_avg * iv_avg * t
        ) / sigma_sqrt_t
    else:
        return None

    win_rate = normal_cdf(d_high) - normal_cdf(d_low)

    contract_multiplier = get_contract_multiplier(registry, symbol)
    margin_estimate = underlying * contract_multiplier * 0.15 * RATIO
    if margin_estimate > MAX_MARGIN:
        return None

    theta_score = max(0, -net_theta) / underlying * 100
    vega_score = max(0, -net_vega) / underlying * 100
    width_score = profit_zone_width / underlying * 100

    score = (
        min(theta_score * 200, 40)
        + min(vega_score * 200, 30)
        + win_rate * 20
        + width_score * 10
    )

    return RatioSpread(
        symbol=symbol,
        contract=contract,
        underlying=underlying,
        iv_avg=iv_avg,
        days_to_expiry=dte,
        buy_leg=buy,
        sell_leg=sell,
        net_delta=net_delta,
        net_gamma=net_gamma,
        net_theta=net_theta,
        net_vega=net_vega,
        net_cost=net_cost,
        max_profit=max_profit,
        breakeven_low=breakeven_low,
        breakeven_high=breakeven_high,
        profit_zone_width=profit_zone_width,
        win_rate=win_rate,
        score=score,
        score_components={
            "theta": round(min(theta_score * 200, 40), 1),
            "vega": round(min(vega_score * 200, 30), 1),
            "win_rate": round(win_rate * 20, 1),
            "width": round(width_score * 10, 1),
        },
    )


def calc_put_ratio_spread(
    symbol: str,
    contract: str,
    underlying: float,
    iv_avg: float,
    dte: int,
    buy: OptionLeg,
    sell: OptionLeg,
    registry: ContractRegistry,
) -> Optional[RatioSpread]:
    """计算 Put Ratio Spread（买1高行权价Put, 卖2低行权价Put）。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        underlying: 标的价格。
        iv_avg: 平均隐含波动率。
        dte: 到期天数。
        buy: 买入腿。
        sell: 卖出腿。
        registry: ContractRegistry 实例。

    Returns:
        RatioSpread 实例，不满足条件时返回 None。
    """
    if buy.strike <= sell.strike:
        return None

    net_delta = buy.delta - RATIO * sell.delta
    if abs(net_delta) > MAX_DELTA_ABS:
        return None

    avg_iv = (buy.iv + sell.iv) / 2
    if avg_iv < MIN_IV and sell.iv < MIN_IV:
        return None

    net_cost = buy.mid - RATIO * sell.mid
    if net_cost > underlying * MAX_COST_RATIO:
        return None

    net_gamma = buy.gamma - RATIO * sell.gamma
    net_theta = buy.theta - RATIO * sell.theta
    net_vega = buy.vega - RATIO * sell.vega

    breakeven_high = buy.strike - net_cost
    breakeven_low = 2 * sell.strike - buy.strike + net_cost

    max_profit = buy.strike - sell.strike - net_cost
    if max_profit <= 0:
        return None

    profit_zone_width = breakeven_high - breakeven_low
    if profit_zone_width <= 0:
        return None

    t = dte / 365.0
    if t <= 0 or iv_avg <= 0:
        return None

    sigma_sqrt_t = iv_avg * math.sqrt(t)

    if breakeven_low > 0:
        d_low = (
            math.log(breakeven_low / underlying) - 0.5 * iv_avg * iv_avg * t
        ) / sigma_sqrt_t
    else:
        d_low = -999.0

    if breakeven_high > 0:
        d_high = (
            math.log(breakeven_high / underlying) - 0.5 * iv_avg * iv_avg * t
        ) / sigma_sqrt_t
    else:
        return None

    win_rate = normal_cdf(d_high) - normal_cdf(d_low)

    contract_multiplier = get_contract_multiplier(registry, symbol)
    margin_estimate = underlying * contract_multiplier * 0.15 * RATIO
    if margin_estimate > MAX_MARGIN:
        return None

    theta_score = max(0, -net_theta) / underlying * 100
    vega_score = max(0, -net_vega) / underlying * 100
    width_score = profit_zone_width / underlying * 100

    score = (
        min(theta_score * 200, 40)
        + min(vega_score * 200, 30)
        + win_rate * 20
        + width_score * 10
    )

    return RatioSpread(
        symbol=symbol,
        contract=contract,
        underlying=underlying,
        iv_avg=iv_avg,
        days_to_expiry=dte,
        buy_leg=buy,
        sell_leg=sell,
        net_delta=net_delta,
        net_gamma=net_gamma,
        net_theta=net_theta,
        net_vega=net_vega,
        net_cost=net_cost,
        max_profit=max_profit,
        breakeven_low=breakeven_low,
        breakeven_high=breakeven_high,
        profit_zone_width=profit_zone_width,
        win_rate=win_rate,
        score=score,
        score_components={
            "theta": round(min(theta_score * 200, 40), 1),
            "vega": round(min(vega_score * 200, 30), 1),
            "win_rate": round(win_rate * 20, 1),
            "width": round(width_score * 10, 1),
        },
    )


# ---- 共享的"找腿+过滤"逻辑 ----


def _evaluate_call_spreads(
    symbol: str,
    contract: str,
    underlying: float,
    iv_avg: float,
    dte: int,
    calls: List[OptionLeg],
    registry: ContractRegistry,
    return_all: bool = False,
) -> List[RatioSpread]:
    """Evaluate all Call Ratio Spreads from pre-parsed OptionLeg lists.

    Args:
        return_all: True 返回所有合格策略（按评分降序），
                    False 只返回最佳策略（列表形式，最多1个）。
    """
    results: List[RatioSpread] = []

    buy_candidates = [
        b for b in calls if b.delta is not None and 0.30 <= b.delta <= 0.70
    ]
    sell_candidates = [
        s for s in calls if s.delta is not None and 0.15 <= s.delta <= 0.35
    ]

    for buy in buy_candidates:
        for sell in sell_candidates:
            if sell.strike <= buy.strike:
                continue
            if (sell.strike - buy.strike) / underlying > 0.30:
                continue
            spread = calc_call_ratio_spread(
                symbol, contract, underlying, iv_avg, dte, buy, sell, registry
            )
            if spread:
                results.append(spread)

    if not results:
        return []

    results.sort(key=lambda x: x.score, reverse=True)
    return results if return_all else [results[0]]


def _evaluate_put_spreads(
    symbol: str,
    contract: str,
    underlying: float,
    iv_avg: float,
    dte: int,
    puts: List[OptionLeg],
    registry: ContractRegistry,
    return_all: bool = False,
) -> List[RatioSpread]:
    """Evaluate all Put Ratio Spreads from pre-parsed OptionLeg lists."""
    results: List[RatioSpread] = []

    buy_candidates = [
        b for b in puts if b.delta is not None and -0.70 <= b.delta <= -0.30
    ]
    sell_candidates = [
        s for s in puts if s.delta is not None and -0.35 <= s.delta <= -0.15
    ]

    for buy in buy_candidates:
        for sell in sell_candidates:
            if sell.strike >= buy.strike:
                continue
            if (buy.strike - sell.strike) / underlying > 0.30:
                continue
            spread = calc_put_ratio_spread(
                symbol, contract, underlying, iv_avg, dte, buy, sell, registry
            )
            if spread:
                results.append(spread)

    if not results:
        return []

    results.sort(key=lambda x: x.score, reverse=True)
    return results if return_all else [results[0]]


def _parse_options_data(
    options_data: List[Dict],
    parser: Callable = parse_option_from_market_data,
) -> Tuple[List[OptionLeg], List[OptionLeg], float]:
    """Parse options data into calls/puts and extract avg IV.

    Returns:
        (calls, puts, iv_avg)
    """
    calls: List[OptionLeg] = []
    puts: List[OptionLeg] = []
    iv_list: List[float] = []

    for opt in options_data:
        c = parser(opt, is_call=True)
        p = parser(opt, is_call=False)
        if c:
            calls.append(c)
            iv_list.append(c.iv)
        if p:
            puts.append(p)
            iv_list.append(p.iv)

    iv_avg = sum(iv_list) / len(iv_list) if iv_list else 0.30
    return calls, puts, iv_avg


def find_all_strategies(
    symbol: str,
    contract: str,
    underlying: float,
    options_data: List[Dict],
    registry: ContractRegistry,
    iv_avg: Optional[float] = None,
    dte: int = 30,
    parser: Callable = parse_option_from_market_data,
) -> Tuple[List[RatioSpread], List[RatioSpread]]:
    """为单个品种寻找所有合格的 Call/Put 比例价差策略（按评分降序排列）。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        underlying: 标的价格。
        options_data: 期权数据列表。
        registry: ContractRegistry 实例。
        iv_avg: 平均隐含波动率（小数），None 时从数据中提取。
        dte: 距到期天数。
        parser: 数据解析函数。

    Returns:
        (call_spreads, put_spreads) — 各自按评分降序排列的列表。
    """
    if underlying <= 0 or not options_data:
        return [], []

    if iv_avg is None:
        _, _, iv_avg = _parse_options_data(options_data, parser=parser)

    calls, puts, _ = _parse_options_data(options_data, parser=parser)

    call_spreads = _evaluate_call_spreads(
        symbol, contract, underlying, iv_avg, dte, calls, registry, return_all=True
    )
    put_spreads = _evaluate_put_spreads(
        symbol, contract, underlying, iv_avg, dte, puts, registry, return_all=True
    )

    return call_spreads, put_spreads


def find_best_strategies(
    symbol: str,
    contract: str,
    underlying: float,
    options_data: List[Dict],
    registry: ContractRegistry,
    iv_avg: Optional[float] = None,
    dte: int = 30,
) -> Tuple[Optional[RatioSpread], Optional[RatioSpread]]:
    """为单个品种寻找最佳的 Call/Put 比例价差策略。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        underlying: 标的价格。
        options_data: 期权数据列表（市场监控格式）。
        registry: ContractRegistry 实例。
        iv_avg: 平均隐含波动率（小数），None 时从数据中提取。
        dte: 距到期天数。

    Returns:
        (best_call_spread, best_put_spread) — 各自最优的策略。
    """
    if underlying <= 0 or not options_data:
        return None, None

    if iv_avg is None:
        _, _, iv_avg = _parse_options_data(options_data)

    calls, puts, _ = _parse_options_data(options_data)

    best_calls = _evaluate_call_spreads(
        symbol, contract, underlying, iv_avg, dte, calls, registry, return_all=False
    )
    best_puts = _evaluate_put_spreads(
        symbol, contract, underlying, iv_avg, dte, puts, registry, return_all=False
    )

    return (
        best_calls[0] if best_calls else None,
        best_puts[0] if best_puts else None,
    )
