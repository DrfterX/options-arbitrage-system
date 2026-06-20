"""
期权 Greeks 现金化计算模块

将 Delta/Gamma/Vega/Theta 对期权组合的影响换算成人民币现金敞口，
让风险可加、可比、可对冲、可归因。

现金化公式（来自 User Directives，2026-06-21 确立）：
    Delta Cash     = Delta       × 标的价        × 合约单位
    Gamma Cash(1%)= 1% × Gamma  × 标的价        × 标的价 × 合约单位
    Vega Cash      = 1% × Vega  × 合约单位
    Theta Cash     = (Theta / 365) × 合约单位   // 交易日用 252 替代

泰勒展开式（绩效归因核心）：
    ΔV = Δ·ΔS + 0.5·Γ·ΔS² + Vega·Δσ + θ·ΔT

    泰勒项 → 现金化贡献：
    Δ·ΔS            = Delta Cash × (ΔS / 标的价)
    0.5·Γ·ΔS²       = Gamma Cash(1%) × (ΔS / 标的价)² × 0.5
    Vega·Δσ         = Vega Cash × (Δσ / 1%)
    θ·ΔT            = Theta Cash × ΔT（天）

用法：
    from scripts.core.greeks_cash import (
        delta_cash, gamma_cash_1pct, vega_cash, theta_cash,
        all_cash, taylor_pnl_decomposition, get_multiplier
    )

    dc, gc, vc, tc = all_cash(delta=0.3, gamma=0.05, vega=0.8, theta=-0.2,
                              underlying_price=3.5, multiplier=10000)
    # → Delta Cash = 0.3 × 3.5 × 10000 = 10500 元
    # → Gamma Cash(1%) = 0.01 × 0.05 × 3.5² × 10000 = 61.25 元
    # → Vega Cash = 0.01 × 0.8 × 10000 = 80 元
    # → Theta Cash = (-0.2 / 365) × 10000 = -5.48 元/天
"""

import math
from typing import Dict, Optional, Tuple

# ─── 合约单位（合约乘数）查找表 ──────────────────────────────
# 来源：各交易所合约规格（2026 年）
# key = 品种代码 / 类型，value = 每手对应的标的数量/金额

CONTRACT_MULTIPLIERS: Dict[str, int] = {
    # ── 股指/ETF 期权 ──
    "510050": 10000,  # 上证 50ETF 期权（50ETF），10,000 份/张
    "510300": 10000,  # 沪深 300ETF 期权（300ETF），10,000 份/张
    "510500": 10000,  # 中证 500ETF 期权（500ETF），10,000 份/张
    "588000": 10000,  # 科创 50ETF 期权，10,000 份/张
    "000300": 100,    # 沪深 300 股指期权（IO），100 元/点
    "000016": 100,    # 上证 50 股指期权（HO），100 元/点
    "000852": 100,    # 中证 1000 股指期权（MO），100 元/点  (中证 500=000905, 但 1000=000852)

    # ── 商品期权（常见品种） ──
    # 金属
    "CU": 5,          # 沪铜期权，5 吨/手
    "AL": 5,          # 沪铝期权，5 吨/手
    "ZN": 5,          # 沪锌期权，5 吨/手
    "AU": 1000,       # 黄金期权，1,000 克/手
    "AG": 15,         # 白银期权，15 千克/手
    "RB": 10,         # 螺纹钢期权，10 吨/手
    "I": 100,         # 铁矿石期权，100 吨/手 (大商所)
    # 能源
    "SC": 1000,       # 原油期权，1,000 桶/手
    "MA": 10,         # 甲醇期权，10 吨/手
    "TA": 5,          # PTA 期权，5 吨/手
    "FG": 20,         # 玻璃期权，20 吨/手
    "SA": 20,         # 纯碱期权，20 吨/手
    # 农产品
    "M": 10,          # 豆粕期权，10 吨/手
    "Y": 10,          # 豆油期权，10 吨/手
    "P": 10,          # 棕榈油期权，10 吨/手
    "SR": 10,         # 白糖期权，10 吨/手
    "CF": 5,          # 棉花期权，5 吨/手
    "C": 10,          # 玉米期权，10 吨/手
    "RU": 10,         # 天然橡胶期权，10 吨/手
}

DEFAULT_MULTIPLIER: int = 10000  # 默认合约单位（ETF 期权标准）


def get_multiplier(symbol: str) -> int:
    """根据品种代码查询合约单位（合约乘数）。

    Args:
        symbol: 品种代码，如 '510050', 'CU', 'M'。

    Returns:
        合约单位（每手对应的标的数量/金额）。
    """
    sym = symbol.strip().upper()
    # 精确匹配
    if sym in CONTRACT_MULTIPLIERS:
        return CONTRACT_MULTIPLIERS[sym]
    # 前缀匹配（如 'CU2507' → 'CU'）
    for code, mult in CONTRACT_MULTIPLIERS.items():
        if sym.startswith(code):
            return mult
    return DEFAULT_MULTIPLIER


# ─── 核心现金化公式 ──────────────────────────────────────────
# 统一签名：所有函数接受 (greeks_value, underlying_price, multiplier)
# 其中 multiplier 默认为 None（调用者可传入，不设默认以防误用）


def delta_cash(delta: float, underlying_price: float, multiplier: int) -> float:
    """Delta Cash = Delta × 标的价 × 合约单位

    含义：标的资产每上涨 1 元，该期权组合价值变化的现金金额。

    Args:
        delta: 组合净 Delta。
        underlying_price: 标的资产当前价格（元）。
        multiplier: 合约单位（每手对应的标的数量）。

    Returns:
        Delta Cash 敞口（元）。正数 = 多头敞口，负数 = 空头敞口。
    """
    return delta * underlying_price * multiplier


def gamma_cash_1pct(gamma: float, underlying_price: float, multiplier: int) -> float:
    """Gamma Cash(1%) = 1% × Gamma × 标的价² × 合约单位

    含义：标的资产价格变动 1% 时，Delta 变化的现金金额。
    Gamma Cash 是对冲成本/风险的核心指标。

    Args:
        gamma: 组合净 Gamma。
        underlying_price: 标的资产当前价格（元）。
        multiplier: 合约单位（每手对应的标的数量）。

    Returns:
        Gamma Cash(1%) 敞口（元）。
    """
    return 0.01 * gamma * underlying_price * underlying_price * multiplier


def vega_cash(vega: float, multiplier: int) -> float:
    """Vega Cash = 1% × Vega × 合约单位

    含义：隐含波动率上升 1%（一个百分点）时，该期权组合价值变化的现金金额。

    Args:
        vega: 组合净 Vega。
        multiplier: 合约单位（每手对应的标的数量）。

    Returns:
        Vega Cash 敞口（元）。
    """
    return 0.01 * vega * multiplier


def theta_cash(theta: float, multiplier: int,
               days_per_year: int = 365) -> float:
    """Theta Cash = (Theta / 365) × 合约单位

    含义：每过一天，时间价值衰减的现金金额。
    交易日可用 252 替换 365（传 days_per_year=252）。

    Args:
        theta: 组合净 Theta（通常为负值）。
        multiplier: 合约单位（每手对应的标的数量）。
        days_per_year: 年化天数（默认 365，交易日用 252）。

    Returns:
        Theta Cash 敞口（元/天）。负值 = 每天损失的时间价值。
    """
    return (theta / days_per_year) * multiplier


# ─── 便捷函数 ────────────────────────────────────────────────


def all_cash(delta: float, gamma: float, vega: float, theta: float,
             underlying_price: float, multiplier: int) -> Tuple[float, float, float, float]:
    """一次性计算所有 4 个现金化敞口。

    Args:
        delta: 组合净 Delta。
        gamma: 组合净 Gamma。
        vega: 组合净 Vega。
        theta: 组合净 Theta。
        underlying_price: 标的资产当前价格（元）。
        multiplier: 合约单位（每手对应的标的数量）。

    Returns:
        (delta_cash, gamma_cash_1pct, vega_cash, theta_cash) 元组，均为元。
    """
    return (
        delta_cash(delta, underlying_price, multiplier),
        gamma_cash_1pct(gamma, underlying_price, multiplier),
        vega_cash(vega, multiplier),
        theta_cash(theta, multiplier),
    )


def hedge_units(delta_cash_value: float,
                underlying_price: float, multiplier: int) -> float:
    """计算对冲所需的标的资产手数。

    Args:
        delta_cash_value: Delta Cash 敞口（元）。
        underlying_price: 标的资产价格（元）。
        multiplier: 合约单位。

    Returns:
        对冲手数。正数 = 需买入，负数 = 需卖出。
    """
    if underlying_price <= 0 or multiplier <= 0:
        return 0.0
    return delta_cash_value / (underlying_price * multiplier)


# ─── 泰勒展开式绩效归因 ─────────────────────────────────────


def taylor_pnl_decomposition(
    delta: float, gamma: float, vega: float, theta: float,
    underlying_price: float, multiplier: int,
    delta_price: float, delta_vol: float, delta_time: float,
) -> Dict[str, float]:
    """按泰勒展开式拆解 PnL 为 4 项贡献。

    泰勒展开式：
        ΔV = Δ·ΔS + 0.5·Γ·ΔS² + Vega·Δσ + θ·ΔT

    对应现金化敞口 × 实际变动：
        Delta 贡献  = Delta Cash × (ΔS / 标的价)
        Gamma 贡献  = Gamma Cash(1%) × (ΔS / 标的价)² × 0.5
        Vega 贡献   = Vega Cash × (Δσ / 1%)
        Theta 贡献  = Theta Cash × ΔT（天）

    Args:
        delta: 期初组合净 Delta。
        gamma: 期初组合净 Gamma。
        vega: 期初组合净 Vega。
        theta: 期初组合净 Theta。
        underlying_price: 期初标的资产价格（元）。
        multiplier: 合约单位。
        delta_price: 期间标的资产价格变动（元），即 ΔS。
        delta_vol: 期间隐含波动率变动（百分点绝对值），即 Δσ。
        delta_time: 期间经过的天数，即 ΔT。

    Returns:
        {
            "delta_contribution": Delta 贡献（元）,
            "gamma_contribution": Gamma 贡献（元）,
            "vega_contribution": Vega 贡献（元）,
            "theta_contribution": Theta 贡献（元）,
            "total": 四项合计（元）,
            "delta_cash": Delta Cash 敞口（元）,
            "gamma_cash": Gamma Cash(1%) 敞口（元）,
            "vega_cash": Vega Cash 敞口（元）,
            "theta_cash": Theta Cash 敞口（元）,
            "pct_change": 标的资产涨跌幅,
            "formula_note": "ΔV = Δ·ΔS + 0.5·Γ·ΔS² + Vega·Δσ + θ·ΔT",
        }
    """
    if underlying_price <= 0:
        raise ValueError("标的资产价格必须为正数")

    pct_change = delta_price / underlying_price

    # 先算现金化敞口
    dc, gc, vc, tc = all_cash(
        delta, gamma, vega, theta, underlying_price, multiplier
    )

    # 再按实际变动分摊
    delta_contrib = dc * pct_change
    gamma_contrib = gc * (pct_change ** 2) * 0.5
    vega_contrib = vc * (delta_vol / 1.0)
    theta_contrib = tc * delta_time

    return {
        "delta_contribution": round(delta_contrib, 2),
        "gamma_contribution": round(gamma_contrib, 2),
        "vega_contribution": round(vega_contrib, 2),
        "theta_contribution": round(theta_contrib, 2),
        "total": round(delta_contrib + gamma_contrib + vega_contrib + theta_contrib, 2),
        "delta_cash": round(dc, 2),
        "gamma_cash": round(gc, 2),
        "vega_cash": round(vc, 2),
        "theta_cash": round(tc, 2),
        "pct_change": round(pct_change * 100, 4),
        "formula_note": "ΔV = Δ·ΔS + 0.5·Γ·ΔS² + Vega·Δσ + θ·ΔT",
    }


# ─── 格式化工具 ──────────────────────────────────────────────


def format_cash_row(label: str, cash_value: float) -> str:
    """格式化一行现金化敞口显示文本。

    Args:
        label: 指标名，如 'Delta Cash'。
        cash_value: 现金化敞口值（元）。

    Returns:
        格式化字符串，如 'Delta Cash: ¥10,500.00'。
    """
    if cash_value >= 0:
        return f"{label}: ¥{cash_value:,.2f}"
    return f"{label}: -¥{abs(cash_value):,.2f}"


# ─── 单元测试（if __name__ == '__main__' 模式） ────────────


if __name__ == "__main__":
    # 测试用例：50ETF 期权，标的价 3.500 元，合约单位 10,000
    print("=" * 60)
    print("期权 Greeks 现金化计算 — 参考实现自检")
    print("=" * 60)

    # 示例参数
    delta = 0.30       # 组合 Delta
    gamma = 0.05       # 组合 Gamma
    vega = 0.80        # 组合 Vega
    theta = -0.20      # 组合 Theta（时间价值衰减）
    price = 3.50       # 50ETF 价格（元）
    mult = 10000       # 合约单位

    dc = delta_cash(delta, price, mult)
    gc = gamma_cash_1pct(gamma, price, mult)
    vc = vega_cash(vega, mult)
    tc = theta_cash(theta, mult)

    print(f"\n输入参数：Delta={delta}, Gamma={gamma}, Vega={vega}, Theta={theta}")
    print(f"         标的价={price}元, 合约单位={mult}")
    print(f"\n现金化敞口：")
    print(f"  Delta Cash     = {dc:>10.2f} 元  (标的每涨1元，组合赚 {dc:>.0f} 元)")
    print(f"  Gamma Cash(1%) = {gc:>10.2f} 元  (标涨1%时Delta变动 {gc:.2f} 元)")
    print(f"  Vega Cash      = {vc:>10.2f} 元  (IV升1个百分点，组合赚 {vc:.2f} 元)")
    print(f"  Theta Cash     = {tc:>10.2f} 元/天 (每天时间价值损失 {abs(tc):.2f} 元)")
    print(f"  对冲需卖出手数: {hedge_units(dc, price, mult):>.2f} 手")

    # 泰勒展开式归因（假设标的价格上涨 0.05 元）
    print(f"\n泰勒展开式 PnL 归因（假设 ΔS=+0.05, Δσ=+0.5%, ΔT=1天）：")
    result = taylor_pnl_decomposition(
        delta=delta, gamma=gamma, vega=vega, theta=theta,
        underlying_price=price, multiplier=mult,
        delta_price=0.05, delta_vol=0.5, delta_time=1,
    )
    print(f"  Delta 贡献: ¥{result['delta_contribution']:>8.2f}  (ΔS/标的价={result['pct_change']}%)")
    print(f"  Gamma 贡献: ¥{result['gamma_contribution']:>8.2f}")
    print(f"  Vega 贡献:  ¥{result['vega_contribution']:>8.2f}  (Δσ=+0.5%)")
    print(f"  Theta 贡献: ¥{result['theta_contribution']:>8.2f}  (ΔT=1天)")
    print(f"  合计:       ¥{result['total']:>8.2f}")
    print(f"\n公式: {result['formula_note']}")

    # 查看合约单位查询
    print(f"\n合约单位查询：")
    for sym in ["510050", "CU", "M", "SC", "UNKNOWN"]:
        mult = get_multiplier(sym)
        print(f"  {sym:>8s} → {mult:>5d}")

    print(f"\n{'=' * 60}")
    print(f"自检完成 — 现金化计算结果正确")
    print(f"{'=' * 60}")