"""测试 options/pricing.py 的 Black-76 定价、Greeks 和 IV 反推。

新增单元测试，覆盖核心数学函数。
"""

import math
import pytest

from options.pricing import black_price, black_greeks, calc_iv, normal_cdf, normal_pdf


# ═══════════════════════════════════════════════════════
# 1. normal_cdf / normal_pdf 基础数学
# ═══════════════════════════════════════════════════════
class TestNormalDist:

    def test_normal_cdf_zero(self) -> None:
        """N(0) = 0.5"""
        assert normal_cdf(0) == pytest.approx(0.5, abs=1e-6)

    def test_normal_cdf_symmetry(self) -> None:
        """N(-x) = 1 - N(x)"""
        x = 1.5
        assert normal_cdf(-x) == pytest.approx(1.0 - normal_cdf(x), abs=1e-6)

    def test_normal_pdf_peak(self) -> None:
        """PDF 峰值在 x=0"""
        assert normal_pdf(0) == pytest.approx(1.0 / math.sqrt(2.0 * math.pi), abs=1e-6)


# ═══════════════════════════════════════════════════════
# 2. Black-76 定价
# ═══════════════════════════════════════════════════════
class TestBlackPrice:

    def test_atm_call(self) -> None:
        """ATM看涨期权价格"""
        price = black_price(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=True)
        assert price > 0
        assert price < 20

    def test_atm_put(self) -> None:
        """ATM看跌期权价格"""
        price = black_price(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=False)
        assert price > 0
        assert price < 20

    def test_put_call_parity(self) -> None:
        """看跌-看涨平价：C - P = exp(-rT) * (F - K)"""
        F, K, T, r, sigma = 100, 100, 0.5, 0.02, 0.2
        call = black_price(F, K, T, r, sigma, True)
        put = black_price(F, K, T, r, sigma, False)
        expected_diff = math.exp(-r * T) * (F - K)
        assert call - put == pytest.approx(expected_diff, abs=1e-10)

    def test_deep_itm_call(self) -> None:
        """深度实值看涨期权价格接近内在价值"""
        price = black_price(F=100, K=50, T=0.5, r=0.02, sigma=0.2, is_call=True)
        # 内在价值50，时间价值很小 → 价格应该 > 45
        assert price > 45

    def test_deep_otm_call(self) -> None:
        """深度虚值看涨期权价格接近0"""
        price = black_price(F=100, K=200, T=0.5, r=0.02, sigma=0.2, is_call=True)
        assert price < 5

    def test_zero_volatility(self) -> None:
        """波动率为0 → 抛出 ValueError"""
        with pytest.raises(ValueError, match="波动率"):
            black_price(F=100, K=90, T=0.5, r=0.02, sigma=0, is_call=True)

    def test_negative_time(self) -> None:
        """到期时间为0 → 返回内在价值（不再抛异常）"""
        price = black_price(F=100, K=100, T=0, r=0.02, sigma=0.2, is_call=True)
        assert price == 0.0  # ATM 内在价值 = 0

    def test_zero_time_itm(self) -> None:
        """到期日深度实值 → 返回内在价值"""
        price = black_price(F=100, K=50, T=0, r=0.02, sigma=0.2, is_call=True)
        assert price == pytest.approx(50.0 * math.exp(-0.02 * 0), abs=1e-9)  # = 50


# ═══════════════════════════════════════════════════════
# 3. Black-76 Greeks
# ═══════════════════════════════════════════════════════
class TestBlackGreeks:

    def test_delta_range(self) -> None:
        """Delta在 [-1, 1] 范围内"""
        greeks = black_greeks(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=True)
        assert -1 <= greeks["delta"] <= 1

    def test_atm_call_delta(self) -> None:
        """ATM看涨 Delta ≈ 0.5"""
        greeks = black_greeks(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=True)
        assert 0.45 < greeks["delta"] < 0.65

    def test_atm_put_delta(self) -> None:
        """ATM看跌 Delta ≈ -0.5"""
        greeks = black_greeks(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=False)
        assert -0.65 < greeks["delta"] < -0.45

    def test_gamma_positive(self) -> None:
        """Gamma 总是正数"""
        greeks_call = black_greeks(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=True)
        greeks_put = black_greeks(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=False)
        assert greeks_call["gamma"] > 0
        assert greeks_put["gamma"] > 0

    def test_vega_positive(self) -> None:
        """Vega 总是正数"""
        greeks = black_greeks(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=True)
        assert greeks["vega"] > 0

    def test_theta_negative(self) -> None:
        """Theta 通常是负数（时间衰减）"""
        greeks = black_greeks(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=True)
        assert greeks["theta"] < 0

    def test_zero_time_greeks(self) -> None:
        """到期时间为0 → 返回全零 Greeks（不再抛异常）"""
        greeks = black_greeks(F=100, K=100, T=0, r=0.02, sigma=0.2, is_call=True)
        for key in ("delta", "gamma", "theta", "vega", "rho"):
            assert greeks[key] == 0.0

    def test_deep_itm_call_delta(self) -> None:
        """深度实值看涨 Delta ≈ 1"""
        greeks = black_greeks(F=100, K=50, T=0.5, r=0.02, sigma=0.2, is_call=True)
        assert greeks["delta"] > 0.9

    def test_all_keys_present(self) -> None:
        """返回字典包含所有5个 Greek"""
        greeks = black_greeks(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=True)
        for key in ("delta", "gamma", "theta", "vega", "rho"):
            assert key in greeks


# ═══════════════════════════════════════════════════════
# 4. 隐含波动率
# ═══════════════════════════════════════════════════════
class TestCalcIV:

    def test_atm_call_iv(self) -> None:
        """ATM期权IV反推"""
        target_price = black_price(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=True)
        iv = calc_iv(target_price, F=100, K=100, T=0.5, r=0.02, is_call=True)
        assert abs(iv - 0.2) < 0.05

    def test_otm_put_iv(self) -> None:
        """虚值看跌IV反推"""
        target_price = black_price(F=100, K=90, T=0.25, r=0.02, sigma=0.3, is_call=False)
        iv = calc_iv(target_price, F=100, K=90, T=0.25, r=0.02, is_call=False)
        assert abs(iv - 0.3) < 0.05

    def test_invalid_price_zero(self) -> None:
        """market_price=0 → 返回0"""
        assert calc_iv(0, F=100, K=100, T=0.5, r=0.02, is_call=True) == 0.0

    def test_invalid_price_negative(self) -> None:
        """market_price为负 → 返回0"""
        assert calc_iv(-1.0, F=100, K=100, T=0.5, r=0.02, is_call=True) == 0.0

    def test_zero_time(self) -> None:
        """到期时间为0 → 返回0"""
        target_price = black_price(F=100, K=100, T=0.5, r=0.02, sigma=0.2, is_call=True)
        assert calc_iv(target_price, F=100, K=100, T=0, r=0.02, is_call=True) == 0.0

    def test_high_vol(self) -> None:
        """高波动率场景"""
        target_price = black_price(F=100, K=100, T=0.5, r=0.02, sigma=0.8, is_call=True)
        iv = calc_iv(target_price, F=100, K=100, T=0.5, r=0.02, is_call=True)
        assert abs(iv - 0.8) < 0.1

    def test_low_vol(self) -> None:
        """低波动率场景"""
        target_price = black_price(F=100, K=100, T=0.5, r=0.02, sigma=0.05, is_call=True)
        iv = calc_iv(target_price, F=100, K=100, T=0.5, r=0.02, is_call=True)
        assert abs(iv - 0.05) < 0.05
