"""
期权计算公共数学模块。

集中管理所有纯数学计算函数：Black-76定价、Greeks、隐含波动率、胜率计算。
只依赖 math 标准库，不依赖项目内部数据类。

注意：data/options_collector.py 中已有这些函数的副本用于数据采集，
此模块是策略引擎可引用的"正式版本"。
"""

import math
import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# ==================== 基础数学 ====================


def normal_cdf(x: float) -> float:
    """标准正态累积分布函数（精度 ~1.5e-7）。

    使用 math.erf 实现。

    Args:
        x: 输入值。

    Returns:
        N(x) 值。
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_pdf(x: float) -> float:
    """标准正态概率密度函数。

    Args:
        x: 输入值。

    Returns:
        φ(x) 值。
    """
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


# ==================== 输入校验 ====================


def _validate_inputs(
    *,
    t: Optional[float] = None,
    sigma: Optional[float] = None,
    price: Optional[float] = None,
    strike: Optional[float] = None,
) -> None:
    """统一输入校验，数值不合规抛出 ValueError。

    Args:
        t: 到期时间（年）。
        sigma: 波动率（小数）。
        price: 价格。
        strike: 执行价。
    """
    if t is not None and t <= 0:
        raise ValueError(f"到期时间 t={t} 必须 > 0")
    if sigma is not None and sigma <= 0:
        raise ValueError(f"波动率 sigma={sigma} 必须 > 0")
    if price is not None and price <= 0:
        raise ValueError(f"价格 price={price} 必须 > 0")
    if strike is not None and strike <= 0:
        raise ValueError(f"执行价 strike={strike} 必须 > 0")


# ==================== Black-76 定价 ====================


def black_price(
    F: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    is_call: bool,
) -> float:
    """Black-76 期货期权定价公式。

    假设标的物为期货价格 F，到期时间 T（年），无风险利率 r，
    波动率 sigma。适用于商品期货期权。

    Args:
        F: 期货价格（标的物远期价格）。
        K: 执行价。
        T: 到期时间（年）。
        r: 无风险利率（小数，如 0.03）。
        sigma: 波动率（小数，如 0.25）。
        is_call: True=看涨, False=看跌。

    Returns:
        期权理论价格。
    """
    _validate_inputs(t=T, sigma=sigma, strike=K)

    if T <= 0 or sigma <= 0:
        return 0.0

    d1 = (math.log(F / K) + 0.5 * sigma * sigma * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    discount = math.exp(-r * T)

    if is_call:
        return discount * (F * normal_cdf(d1) - K * normal_cdf(d2))
    else:
        return discount * (K * normal_cdf(-d2) - F * normal_cdf(-d1))


def black_greeks(
    F: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    is_call: bool,
) -> Dict[str, float]:
    """Black-76 期货期权的 Greeks 计算。

    Args:
        F: 期货价格。
        K: 执行价。
        T: 到期时间（年）。
        r: 无风险利率。
        sigma: 波动率。
        is_call: True=看涨, False=看跌。

    Returns:
        包含 delta/gamma/theta/vega/rho 的字典。
    """
    _validate_inputs(t=T, sigma=sigma, strike=K)

    if T <= 0 or sigma <= 0:
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "vega": 0.0,
            "rho": 0.0,
        }

    sqrt_t = math.sqrt(T)
    d1 = (math.log(F / K) + 0.5 * sigma * sigma * T) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t

    discount = math.exp(-r * T)
    pdf_d1 = normal_pdf(d1)

    # Delta
    if is_call:
        delta = discount * normal_cdf(d1)
    else:
        delta = discount * (normal_cdf(d1) - 1.0)

    # Gamma (same for call and put)
    gamma = discount * pdf_d1 / (F * sigma * sqrt_t)

    # Vega (per 1% change in sigma, scaled to per-unit)
    vega = F * discount * pdf_d1 * sqrt_t * 0.01

    # Theta (per day)
    theta_call = (
        -F * discount * pdf_d1 * sigma / (2.0 * sqrt_t)
        - r * K * discount * normal_cdf(d2)
        + r * F * discount * normal_cdf(d1)
    )
    theta_put = (
        -F * discount * pdf_d1 * sigma / (2.0 * sqrt_t)
        + r * K * discount * normal_cdf(-d2)
        - r * F * discount * normal_cdf(-d1)
    )
    theta = (theta_call if is_call else theta_put) / 365.0

    # Rho (per 1% change in rate)
    if is_call:
        rho = K * T * discount * normal_cdf(d2) * 0.01
    else:
        rho = -K * T * discount * normal_cdf(-d2) * 0.01

    return {
        "delta": round(delta, 6),
        "gamma": round(gamma, 6),
        "theta": round(theta, 6),
        "vega": round(vega, 6),
        "rho": round(rho, 6),
    }


# ==================== 隐含波动率 ====================


def calc_iv(
    market_price: float,
    F: float,
    K: float,
    T: float,
    r: float,
    is_call: bool,
    tolerance: float = 1e-6,
    max_iterations: int = 100,
) -> float:
    """Newton-Raphson 法计算隐含波动率。

    Args:
        market_price: 市场期权价格。
        F: 期货价格。
        K: 执行价。
        T: 到期时间（年）。
        r: 无风险利率。
        is_call: True=看涨, False=看跌。
        tolerance: 收敛容差。
        max_iterations: 最大迭代次数。

    Returns:
        隐含波动率（小数），计算失败返回 0。
    """
    if market_price <= 0 or T <= 0:
        return 0.0

    # 初始猜测
    sigma = 0.3
    for _ in range(max_iterations):
        price = black_price(F, K, T, r, sigma, is_call)
        diff = price - market_price

        if abs(diff) < tolerance:
            return round(sigma, 6)

        # Vega = ∂price/∂σ
        # d1 term
        d1 = (math.log(F / K) + 0.5 * sigma * sigma * T) / (sigma * math.sqrt(T))
        discount = math.exp(-r * T)
        vega = F * discount * normal_pdf(d1) * math.sqrt(T)

        if abs(vega) < 1e-12:
            break

        sigma = sigma - diff / vega

        if sigma <= 0.001:
            sigma = 0.001
        if sigma > 5.0:
            sigma = 5.0

    # 最后尝试
    final_price = black_price(F, K, T, r, sigma, is_call)
    if abs(final_price - market_price) < tolerance * 100:
        return round(sigma, 6)

    logger.debug("IV 未收敛: market=%.4f, model=%.4f, sigma=%.4f", market_price, final_price, sigma)
    return 0.0


# ==================== 胜率计算 ====================


def calc_win_rate(
    underlying: float,
    iv_avg: float,
    dte: int,
    breakeven_low: float,
    breakeven_high: float,
) -> float:
    """对数正态到期价格胜率（通用）。

    假设标的物价格服从对数正态分布，
    计算到期时价格落在盈亏平衡区间内的概率。

    Args:
        underlying: 标的物当前价格。
        iv_avg: 平均隐含波动率（小数形式，如 0.25）。
        dte: 到期天数。
        breakeven_low: 下盈亏平衡点。
        breakeven_high: 上盈亏平衡点。

    Returns:
        胜率 (0~1)，无效输入返回 0。
    """
    t = dte / 365.0
    if t <= 0 or iv_avg <= 0 or breakeven_low >= breakeven_high:
        return 0.0
    sigma_sqrt_t = iv_avg * math.sqrt(t)
    d_low = (
        math.log(max(breakeven_low, 1.0) / underlying) - 0.5 * iv_avg * iv_avg * t
    ) / sigma_sqrt_t
    d_high = (
        math.log(breakeven_high / underlying) - 0.5 * iv_avg * iv_avg * t
    ) / sigma_sqrt_t
    return normal_cdf(d_high) - normal_cdf(d_low)
