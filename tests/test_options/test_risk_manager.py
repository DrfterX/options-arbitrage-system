"""测试 options/risk_manager.py 的 RiskManager 风控检查。

新增单元测试，覆盖单信号评估和组合评估。
"""

import pytest

from options.risk_manager import RiskManager, RiskCheckResult


# ═══════════════════════════════════════════════════════
# 辅助：构造策略信号
# ═══════════════════════════════════════════════════════

def make_signal(
    symbol: str = "RB",
    strategy: str = "ratio_spread",
    net_delta: float = 0.05,
    margin: float = 5000,
    net_theta: float = -0.1,
    net_vega: float = -0.5,
    win_rate: float = 0.6,
    max_profit: float = 200,
    iv_avg: float = 0.35,
    oi_legs: list = None,
) -> dict:
    """构造一个策略信号字典。"""
    return {
        "symbol": symbol,
        "contract": "rb2510",
        "strategy": strategy,
        "signal_type": "CANDIDATE",
        "strength": 0.7,
        "details": {
            "net_delta": net_delta,
            "margin": margin,
            "max_margin": margin,
            "net_theta": net_theta,
            "net_vega": net_vega,
            "win_rate": win_rate,
            "max_profit": max_profit,
            "iv_avg": iv_avg,
            "oi_legs": oi_legs or [500, 500],
        },
    }


# ═══════════════════════════════════════════════════════
# 1. RiskCheckResult 基础
# ═══════════════════════════════════════════════════════
class TestRiskCheckResult:

    def test_default_passed(self) -> None:
        """默认 passed=True"""
        result = RiskCheckResult()
        assert result.passed is True
        assert result.score == 0.0
        assert result.warnings == []

    def test_add_warning(self) -> None:
        """添加警告将 passed 设为 False"""
        result = RiskCheckResult()
        result.add_warning("测试警告")
        assert result.passed is False
        assert len(result.warnings) == 1

    def test_to_dict(self) -> None:
        """to_dict 返回正确结构"""
        result = RiskCheckResult(passed=True, score=15.5, details={"delta": 0.05})
        result.add_warning("警告1")
        d = result.to_dict()
        assert d["passed"] is False
        assert d["score"] == 15.5
        assert len(d["warnings"]) == 1
        assert d["details"]["delta"] == 0.05


# ═══════════════════════════════════════════════════════
# 2. evaluate_signal: 正常通过
# ═══════════════════════════════════════════════════════
class TestEvaluateSignalPass:

    def test_ratio_spread_pass(self) -> None:
        """ratio_spread 策略全部通过风控"""
        mgr = RiskManager()
        signal = make_signal(
            symbol="RB", strategy="ratio_spread",
            net_delta=0.05, margin=5000, net_theta=-0.1,
            net_vega=-0.5, win_rate=0.6, max_profit=200, iv_avg=0.35,
        )
        result = mgr.evaluate_signal(signal, {})
        assert result.passed is True

    def test_delta_neutral_pass(self) -> None:
        """Delta中性接近0 → 通过"""
        mgr = RiskManager()
        signal = make_signal(net_delta=0.02)
        result = mgr.evaluate_signal(signal, {})
        assert result.passed is True

    def test_low_margin_pass(self) -> None:
        """保证金在限额内 → 通过"""
        mgr = RiskManager()
        signal = make_signal(margin=3000)
        result = mgr.evaluate_signal(signal, {})
        assert result.passed is True


# ═══════════════════════════════════════════════════════
# 3. evaluate_signal: 风控拒绝
# ═══════════════════════════════════════════════════════
class TestEvaluateSignalFail:

    def test_delta_too_high(self) -> None:
        """Delta 超过限制 → 不通过"""
        mgr = RiskManager()
        signal = make_signal(net_delta=0.5)
        result = mgr.evaluate_signal(signal, {})
        assert result.passed is False

    def test_margin_too_high(self) -> None:
        """保证金超过限制 → 不通过"""
        mgr = RiskManager()
        signal = make_signal(margin=50000)
        result = mgr.evaluate_signal(signal, {})
        assert result.passed is False

    def test_win_rate_too_low(self) -> None:
        """胜率低于50% → 不通过"""
        mgr = RiskManager()
        signal = make_signal(win_rate=0.30)
        result = mgr.evaluate_signal(signal, {})
        assert result.passed is False

    def test_low_iv_for_short_strategy(self) -> None:
        """做空波动率策略IV过低 → 不通过"""
        mgr = RiskManager()
        signal = make_signal(strategy="short_strangle", iv_avg=0.15)
        result = mgr.evaluate_signal(signal, {})
        assert result.passed is False

    def test_low_oi(self) -> None:
        """持仓量过低 → 不通过"""
        mgr = RiskManager()
        signal = make_signal(oi_legs=[50, 500])
        result = mgr.evaluate_signal(signal, {})
        assert result.passed is False


# ═══════════════════════════════════════════════════════
# 4. evaluate_signal: 边界值
# ═══════════════════════════════════════════════════════
class TestEvaluateSignalBoundary:

    def test_delta_at_limit(self) -> None:
        """Delta 恰好等于限制值"""
        mgr = RiskManager()
        mgr.max_total_delta = 0.10
        signal = make_signal(net_delta=0.10)
        result = mgr.evaluate_signal(signal, {})
        # net_delta=0.10 不大于 0.10 → 通过（不触发超限）
        assert "Delta" not in str(result.warnings)

    def test_margin_at_limit(self) -> None:
        """保证金恰好等于限制值"""
        mgr = RiskManager()
        mgr.max_margin_per_strategy = 10000
        signal = make_signal(margin=10000)
        result = mgr.evaluate_signal(signal, {})
        # margin=10000 不大于 10000 → 不触发
        assert "保证金" not in str(result.warnings)

    def test_no_oi_legs(self) -> None:
        """无持仓量数据 → 跳过OI检查"""
        mgr = RiskManager()
        signal = make_signal(oi_legs=[])
        result = mgr.evaluate_signal(signal, {})
        # 不触发OI检查，其他项通过
        assert result.passed is True

    def test_zero_win_rate_skip(self) -> None:
        """win_rate=0 → 跳过胜率检查"""
        mgr = RiskManager()
        signal = make_signal(win_rate=0)
        result = mgr.evaluate_signal(signal, {})
        # win_rate=0 不触发胜率检查（only if >0 and <0.50）
        assert "胜率" not in str(result.warnings)

    def test_non_short_strategy_skip_iv(self) -> None:
        """非做空策略跳过IV检查"""
        mgr = RiskManager()
        signal = make_signal(strategy="butterfly", iv_avg=0.10)
        result = mgr.evaluate_signal(signal, {})
        assert result.passed is True


# ═══════════════════════════════════════════════════════
# 5. evaluate_portfolio: 组合评估
# ═══════════════════════════════════════════════════════
class TestEvaluatePortfolio:

    def test_empty_portfolio(self) -> None:
        """空信号列表 → 通过"""
        mgr = RiskManager()
        result = mgr.evaluate_portfolio([])
        assert result.passed is True
        assert "无活跃信号" in result.details.get("message", "")

    def test_single_signal_portfolio(self) -> None:
        """单信号组合 → 无集中度警告"""
        mgr = RiskManager()
        signals = [make_signal()]
        result = mgr.evaluate_portfolio(signals)
        assert result.passed is True

    def test_concentration_warning(self) -> None:
        """品种集中度过高 → 警告"""
        mgr = RiskManager()
        signals = [
            make_signal(symbol="RB"),
            make_signal(symbol="RB"),
            make_signal(symbol="RB"),
            make_signal(symbol="RB"),
        ]
        result = mgr.evaluate_portfolio(signals)
        assert result.passed is False
        assert "分散度" in str(result.warnings)

    def test_diversified_portfolio(self) -> None:
        """分散组合 → 无警告"""
        mgr = RiskManager()
        signals = [
            make_signal(symbol="RB"),
            make_signal(symbol="CU"),
            make_signal(symbol="M"),
            make_signal(symbol="MA"),
        ]
        result = mgr.evaluate_portfolio(signals)
        assert result.passed is True

    def test_statistics_correct(self) -> None:
        """统计数据正确"""
        mgr = RiskManager()
        signals = [
            make_signal(net_delta=0.1),
            make_signal(net_delta=0.2),
        ]
        result = mgr.evaluate_portfolio(signals)
        assert result.details["total_absolute_delta"] == 0.3
        assert result.details["signal_count"] == 2


# ═══════════════════════════════════════════════════════
# 6. RiskManager 自定义参数
# ═══════════════════════════════════════════════════════
class TestRiskManagerCustom:

    def test_custom_delta_limit(self) -> None:
        """自定义Delta限制"""
        mgr = RiskManager()
        mgr.max_total_delta = 0.30
        signal = make_signal(net_delta=0.25)
        result = mgr.evaluate_signal(signal, {})
        assert "Delta" not in str(result.warnings)

    def test_custom_margin_limit(self) -> None:
        """自定义保证金限制"""
        mgr = RiskManager()
        mgr.max_margin_per_strategy = 50000
        signal = make_signal(margin=30000)
        result = mgr.evaluate_signal(signal, {})
        assert "保证金" not in str(result.warnings)
