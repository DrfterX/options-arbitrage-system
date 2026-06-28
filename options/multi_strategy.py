"""
多策略计算器 — Short Strangle + Iron Condor。

复用 ratio_spread_calculator 的 OptionLeg / normal_cdf / get_contract_multiplier。

策略说明:
- Short Strangle (卖虚值Call+卖虚值Put): 做空波动率, 双向收权利金
- Iron Condor (铁鹰): Short Strangle + 保护腿, 风险有限

按IV水平匹配:
  极端高(≥90%): Iron Condor > Short Strangle > Ratio Spread
  偏高(70-90%):  Ratio Spread > Short Strangle
  正常(30-70%):  Ratio Spread
  数据不足:      仅 Ratio Spread（不做波动率方向博弈）
"""

import math
import logging
from typing import Any, Dict, List, Optional

from config.settings import MIN_IV, MAX_DELTA_ABS, MIN_OI, MAX_MARGIN, CALL_DELTA_RANGE, PUT_DELTA_RANGE
from config.contracts import ContractRegistry
from options.pricing import calc_win_rate
from options.ratio_spread import (
    OptionLeg,
    get_contract_multiplier,
    parse_option_from_market_data,
)

logger = logging.getLogger(__name__)

# 保护腿最低持仓量
OI_PROTECTION_MIN: int = 200
# 最小翼宽比例 (1% of underlying)
WING_WIDTH_MIN_PCT: float = 0.01


# ====== 统一评分 (v3, 适用于所有策略类型) ======


def calc_unified_score(
    underlying: float,
    margin: float,
    net_theta: float,
    net_vega: float,
    win_rate: float,
    profit_zone_width: float,
    max_profit: float,
    percentile: float,
    net_delta: float,
) -> dict:
    """跨策略统一评分 (0-100)，返回含维度分解的 dict。

    各维度:
    - Theta贡献: 25 (做空波动率核心收益)
    - Vega贡献: 20 (IV回落收益)
    - 胜率: 20
    - 盈利区间: 10
    - 资本效率: 15
    - Delta中性: 10
    - IV奖励: 封顶到100

    Args:
        underlying: 标的价格。
        margin: 保证金。
        net_theta: 组合Theta。
        net_vega: 组合Vega。
        win_rate: 胜率。
        profit_zone_width: 盈利区间宽度。
        max_profit: 最大利润。
        percentile: IV百分位。
        net_delta: 组合Delta。

    Returns:
        {"score": 综合评分(0-100), "components": {"theta": ..., "vega": ..., ...}}。
    """
    theta_contrib = max(0, -net_theta) / underlying * 100
    theta_score = min(theta_contrib * 150, 25)

    vega_contrib = max(0, -net_vega) / underlying * 100
    vega_score = min(vega_contrib * 150, 20)

    win_score = win_rate * 20

    width_pct = profit_zone_width / underlying * 100
    width_score = min(width_pct * 10, 10)

    margin_eff = max_profit / max(margin, 1) * 100
    eff_score = min(margin_eff * 5, 15)

    delta_abs = abs(net_delta)
    delta_score = max(0, 10 * (1 - delta_abs / 0.10))

    pct_bonus = (
        10
        if percentile >= 90
        else 7
        if percentile >= 80
        else 5
        if percentile >= 70
        else 3
        if percentile >= 30
        else 0
    )

    score = (
        theta_score
        + vega_score
        + win_score
        + width_score
        + eff_score
        + delta_score
        + pct_bonus
    )

    return {
        "score": min(score, 100),
        "components": {
            "theta": round(theta_score, 1),
            "vega": round(vega_score, 1),
            "win_rate": round(win_score, 1),
            "width": round(width_score, 1),
            "efficiency": round(eff_score, 1),
            "delta": round(delta_score, 1),
            "iv_bonus": round(pct_bonus, 1),
        },
        "schema": {
            "theta": 25,
            "vega": 20,
            "win_rate": 20,
            "width": 10,
            "efficiency": 15,
            "delta": 10,
            "iv_bonus": 10,
        },
    }


# ====== Short Strangle ======


def find_best_short_strangle(
    symbol: str,
    contract: str,
    underlying: float,
    iv_avg: float,
    dte: int,
    options_data: List[Dict],
    registry: ContractRegistry,
    iv_percentile: float = 50.0,
) -> Optional[Dict[str, Any]]:
    """寻找最佳 Short Strangle（卖虚值Call + 卖虚值Put）。

    筛选条件:
    - OTM Call delta 0.12~0.30
    - OTM Put delta -0.30~-0.12
    - |组合Delta| <= 0.10
    - 两腿 OI >= 300
    - 保证金 <= MAX_MARGIN
    - DTE >= 10

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        underlying: 标的价格。
        iv_avg: 平均隐含波动率。
        dte: 到期天数。
        options_data: 期权数据列表。
        registry: ContractRegistry 实例。

    Returns:
        统一格式的策略dict, 或None。
    """
    if dte < 10:
        return None

    calls: List[OptionLeg] = []
    puts: List[OptionLeg] = []
    for opt in options_data:
        c = parse_option_from_market_data(opt, is_call=True)
        p = parse_option_from_market_data(opt, is_call=False)
        if c:
            calls.append(c)
        if p:
            puts.append(p)

    if not calls or not puts:
        return None

    best: Optional[Dict[str, Any]] = None
    best_score: float = 0.0

    for call in calls:
        if call.delta is None or not (CALL_DELTA_RANGE[0] <= call.delta <= CALL_DELTA_RANGE[1]):
            continue
        if call.strike <= underlying:
            continue

        for put in puts:
            if put.delta is None or not (PUT_DELTA_RANGE[0] <= put.delta <= PUT_DELTA_RANGE[1]):
                continue
            if put.strike >= underlying:
                continue
            if put.strike >= call.strike:
                continue

            net_delta = -call.delta + (-put.delta)
            if abs(net_delta) > MAX_DELTA_ABS:
                continue

            result = _calc_short_strangle(
                symbol, contract, underlying, iv_avg, dte,
                call, put, net_delta, registry, iv_percentile,
            )
            if result and result["score"] > best_score:
                best_score = result["score"]
                best = result

    return best


def _calc_short_strangle(
    symbol: str,
    contract: str,
    underlying: float,
    iv_avg: float,
    dte: int,
    call: OptionLeg,
    put: OptionLeg,
    net_delta_in: float,
    registry: ContractRegistry,
    iv_percentile: float = 50.0,
) -> Optional[Dict[str, Any]]:
    """计算 Short Strangle 指标。"""
    mult = get_contract_multiplier(registry, symbol)

    credit = (call.mid + put.mid) * mult
    if credit <= 0:
        return None

    net_theta = -call.theta - put.theta
    net_vega = -call.vega - put.vega

    breakeven_low = put.strike - credit / mult
    breakeven_high = call.strike + credit / mult
    profit_zone_width = breakeven_high - breakeven_low

    max_profit = credit

    margin = underlying * mult * 0.15 + credit
    margin += underlying * mult * 0.10
    margin = min(margin, MAX_MARGIN)

    if margin >= MAX_MARGIN:
        return None

    win_rate = calc_win_rate(underlying, iv_avg, dte, breakeven_low, breakeven_high)
    if win_rate <= 0:
        return None

    score_result = calc_unified_score(
        underlying, margin, net_theta, net_vega,
        win_rate, profit_zone_width, max_profit,
        percentile=iv_percentile, net_delta=net_delta_in,
    )

    return {
        "type": "short_strangle",
        "symbol": symbol,
        "contract": contract,
        "underlying": underlying,
        "iv_avg": iv_avg,
        "days_to_expiry": dte,
        "net_delta": round(net_delta_in, 4),
        "net_theta": round(net_theta, 4),
        "net_vega": round(net_vega, 4),
        "net_gamma": round(-call.gamma - put.gamma, 4),
        "net_cost": -round(credit, 2),
        "max_profit": round(max_profit, 2),
        "max_loss": None,  # 无限亏损（前端显示为"—"）
        "breakeven_low": round(breakeven_low, 2),
        "breakeven_high": round(breakeven_high, 2),
        "profit_zone_width": round(profit_zone_width, 2),
        "win_rate": round(win_rate, 4),
        "score": round(score_result["score"], 1),
        "score_components": score_result["components"],
        "score_schema": score_result["schema"],
        "margin_required": round(margin, 0),
        "description": (
            f"Short Strangle(卖Call@{call.strike:.0f} 卖Put@{put.strike:.0f})"
        ),
        "legs_detail": (
            f"卖Call@{call.strike:.0f} x1, 卖Put@{put.strike:.0f} x1"
        ),
        "strikes": [put.strike, call.strike],
    }


# ====== Iron Condor ======


def find_best_iron_condor(
    symbol: str,
    contract: str,
    underlying: float,
    iv_avg: float,
    dte: int,
    options_data: List[Dict],
    registry: ContractRegistry,
    iv_percentile: float = 50.0,
) -> Optional[Dict[str, Any]]:
    """寻找最佳 Iron Condor（卖宽跨+买保护, 风险有限）。

    4条腿: 卖Put@K1 + 买Put@K0 + 卖Call@K4 + 买Call@K5
    其中 K0 < K1 < underlying < K4 < K5

    - 短腿: delta 0.12~0.30 (OTM)
    - 长腿: 短腿外1档 (保护)
    - 两翼宽度大致相等

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        underlying: 标的价格。
        iv_avg: 平均隐含波动率。
        dte: 到期天数。
        options_data: 期权数据列表。
        registry: ContractRegistry 实例。

    Returns:
        统一格式的策略dict, 或None。
    """
    if dte < 10:
        return None

    calls: List[OptionLeg] = []
    puts: List[OptionLeg] = []
    for opt in options_data:
        c = parse_option_from_market_data(opt, is_call=True)
        p = parse_option_from_market_data(opt, is_call=False)
        if c:
            calls.append(c)
        if p:
            puts.append(p)

    if len(calls) < 2 or len(puts) < 2:
        return None

    calls.sort(key=lambda x: x.strike)
    puts.sort(key=lambda x: x.strike, reverse=True)

    best: Optional[Dict[str, Any]] = None
    best_score: float = 0.0

    for short_call in calls:
        if short_call.delta is None or not (0.12 <= short_call.delta <= 0.30):
            continue
        if short_call.strike <= underlying:
            continue

        long_call_candidates = [
            c
            for c in calls
            if c.strike > short_call.strike and c.oi >= OI_PROTECTION_MIN
        ]
        if not long_call_candidates:
            continue

        for short_put in puts:
            if short_put.delta is None or not (-0.30 <= short_put.delta <= -0.12):
                continue
            if short_put.strike >= underlying:
                continue

            long_put_candidates = [
                p
                for p in puts
                if p.strike < short_put.strike and p.oi >= OI_PROTECTION_MIN
            ]
            if not long_put_candidates:
                continue

            for long_call in long_call_candidates:
                call_wing = long_call.strike - short_call.strike
                if call_wing <= 0:
                    continue

                for long_put in long_put_candidates:
                    put_wing = short_put.strike - long_put.strike
                    if put_wing <= 0:
                        continue

                    max_wing = max(call_wing, put_wing)
                    min_wing = min(call_wing, put_wing)
                    if min_wing / max_wing < 0.5:
                        continue

                    if (
                        call_wing < underlying * WING_WIDTH_MIN_PCT
                        or put_wing < underlying * WING_WIDTH_MIN_PCT
                    ):
                        continue

                    if short_put.strike >= short_call.strike:
                        continue

                    result = _calc_iron_condor(
                        symbol, contract, underlying, iv_avg, dte,
                        short_put, long_put, short_call, long_call,
                        call_wing, put_wing, registry, iv_percentile,
                    )
                    if result and result["score"] > best_score:
                        best_score = result["score"]
                        best = result

    return best


def _calc_iron_condor(
    symbol: str,
    contract: str,
    underlying: float,
    iv_avg: float,
    dte: int,
    short_put: OptionLeg,
    long_put: OptionLeg,
    short_call: OptionLeg,
    long_call: OptionLeg,
    call_wing: float,
    put_wing: float,
    registry: ContractRegistry,
    iv_percentile: float = 50.0,
) -> Optional[Dict[str, Any]]:
    """计算 Iron Condor 指标。"""
    mult = get_contract_multiplier(registry, symbol)

    credit = (
        short_put.mid + short_call.mid - long_put.mid - long_call.mid
    ) * mult
    if credit <= 0:
        return None

    net_delta = (
        -short_call.delta
    ) + (-short_put.delta) + long_call.delta + long_put.delta
    net_theta = (
        -short_call.theta
    ) + (-short_put.theta) + long_call.theta + long_put.theta
    net_vega = (
        -short_call.vega
    ) + (-short_put.vega) + long_call.vega + long_put.vega

    if abs(net_delta) > MAX_DELTA_ABS:
        return None

    max_profit = credit
    call_side_loss = call_wing * mult - credit
    put_side_loss = put_wing * mult - credit
    max_loss = max(call_side_loss, put_side_loss)
    if max_loss <= 0:
        return None

    breakeven_low = short_put.strike - credit / mult
    breakeven_high = short_call.strike + credit / mult
    profit_zone_width = breakeven_high - breakeven_low

    margin = max(call_wing, put_wing) * mult
    margin = min(margin, MAX_MARGIN)
    if margin >= MAX_MARGIN:
        return None

    win_rate = calc_win_rate(underlying, iv_avg, dte, breakeven_low, breakeven_high)
    if win_rate <= 0:
        return None

    score_result = calc_unified_score(
        underlying, margin, net_theta, net_vega,
        win_rate, profit_zone_width, max_profit,
        percentile=iv_percentile, net_delta=net_delta,
    )

    return {
        "type": "iron_condor",
        "symbol": symbol,
        "contract": contract,
        "underlying": underlying,
        "iv_avg": iv_avg,
        "days_to_expiry": dte,
        "net_delta": round(net_delta, 4),
        "net_theta": round(net_theta, 4),
        "net_vega": round(net_vega, 4),
        "net_gamma": round(-short_call.gamma - short_put.gamma + long_call.gamma + long_put.gamma, 4),
        "net_cost": -round(credit, 2),
        "max_profit": round(max_profit, 2),
        "max_loss": round(max_loss, 2),
        "breakeven_low": round(breakeven_low, 2),
        "breakeven_high": round(breakeven_high, 2),
        "profit_zone_width": round(profit_zone_width, 2),
        "win_rate": round(win_rate, 4),
        "score": round(score_result["score"], 1),
        "score_components": score_result["components"],
        "score_schema": score_result["schema"],
        "margin_required": round(margin, 0),
        "description": (
            f"Iron Condor(买Put@{long_put.strike:.0f} "
            f"卖Put@{short_put.strike:.0f} "
            f"卖Call@{short_call.strike:.0f} "
            f"买Call@{long_call.strike:.0f})"
        ),
        "legs_detail": (
            f"买Put@{long_put.strike:.0f} x1, "
            f"卖Put@{short_put.strike:.0f} x1, "
            f"卖Call@{short_call.strike:.0f} x1, "
            f"买Call@{long_call.strike:.0f} x1"
        ),
        "strikes": [
            long_put.strike,
            short_put.strike,
            short_call.strike,
            long_call.strike,
        ],
    }
