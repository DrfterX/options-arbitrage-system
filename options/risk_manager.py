"""风险管理模块 — 评估策略信号的风险指标。

风控检查：Delta≤MAX_DELTA_ABS, OI≥MIN_OI, IV≥MIN_IV, 保证金≤MAX_MARGIN。
所有参数从 ``config.settings`` 导入。
"""

import logging
from typing import Any, Dict, List, Optional

from config.settings import MAX_DELTA_ABS, MIN_OI, MIN_IV, MAX_MARGIN

logger = logging.getLogger(__name__)


class RiskCheckResult:
    """风险管理检查结果。

    Attributes:
        passed: 是否通过风控。
        score: 风险评分（0-100，0=低风险）。
        details: 详细信息字典。
        warnings: 警告信息列表。
    """

    def __init__(
        self,
        passed: bool = True,
        score: float = 0.0,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """初始化风控结果。

        Args:
            passed: 是否通过。
            score: 风险评分。
            details: 详细信息。
        """
        self.passed = passed
        self.score = score
        self.details = details or {}
        self.warnings: List[str] = []

    def add_warning(self, msg: str) -> None:
        """添加警告信息，同时将 passed 设为 False。

        Args:
            msg: 警告信息。
        """
        self.warnings.append(msg)
        self.passed = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。

        Returns:
            含 passed/score/warnings/details 的字典。
        """
        return {
            "passed": self.passed,
            "score": round(self.score, 2),
            "warnings": self.warnings,
            "details": self.details,
        }


class RiskManager:
    """风险管理 — 在策略信号执行前进行风控检查。

    风控参数从 config.settings 导入：
    - MAX_DELTA_ABS: 组合Delta绝对值上限
    - MIN_OI: 期权最小持仓量
    - MIN_IV: 最低隐含波动率要求
    - MAX_MARGIN: 单策略最大保证金
    """

    def __init__(self) -> None:
        """初始化风险管理器，使用 settings 中的默认参数。"""
        self.max_total_delta: float = MAX_DELTA_ABS
        self.max_margin_per_strategy: float = MAX_MARGIN
        self.min_options_oi: int = MIN_OI
        self.min_iv: float = MIN_IV

    def evaluate_signal(
        self,
        signal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> RiskCheckResult:
        """评估单个策略信号。

        执行以下检查：
        1. Delta 中性检查（|组合Delta| ≤ MAX_DELTA_ABS）
        2. 保证金检查（保证金 ≤ MAX_MARGIN）
        3. 隐波水平检查（做空策略需 IV ≥ MIN_IV）
        4. 流动性检查（单腿OI ≥ MIN_OI）
        5. 胜率检查（≥ 50%）
        6. 盈亏比检查

        Args:
            signal: 策略信号字典。
            context: 可选上下文（保留用于扩展，当前未使用）。

        Returns:
            RiskCheckResult 实例。
        """
        result = RiskCheckResult(passed=True, score=0, details={})
        details: Dict[str, Any] = signal.get("details", {})

        # 1. Delta 中性检查
        net_delta = abs(details.get("net_delta", 0))
        result.details["net_delta"] = round(net_delta, 4)
        if net_delta > self.max_total_delta:
            result.add_warning(
                f"组合 Delta={net_delta:.4f} 超过限制 {self.max_total_delta}"
            )

        # 2. 保证金检查
        margin = details.get("max_margin", details.get("margin", 0))
        result.details["margin"] = int(margin)
        if margin > self.max_margin_per_strategy:
            result.add_warning(
                f"保证金 ¥{margin:,.0f} 超过限制 ¥{self.max_margin_per_strategy:,}"
            )

        # 3. 隐波水平检查（仅对做空波动率策略）
        strategy = signal.get("strategy", "")
        if "short" in strategy or "sell" in strategy or "ratio" in strategy:
            iv_avg = details.get("iv_avg", 0)
            result.details["iv_avg"] = round(iv_avg, 4)
            if iv_avg < self.min_iv:
                result.add_warning(
                    f"平均隐波 {iv_avg*100:.1f}% 低于最小阈值 {self.min_iv*100:.0f}%，"
                    f"做空波动率入场时机不佳"
                )

        # 4. 流动性检查
        oi_legs = details.get("oi_legs", [])
        if oi_legs:
            min_oi = min(oi_legs)
            result.details["min_leg_oi"] = int(min_oi)
            if min_oi < self.min_options_oi:
                result.add_warning(
                    f"某腿持仓量 {min_oi:.0f} 低于最低门槛 {self.min_options_oi}"
                )

        # 5. 胜率检查
        win_rate = details.get("win_rate", 0)
        result.details["win_rate"] = round(win_rate, 4)
        if win_rate > 0 and win_rate < 0.50:
            result.add_warning(f"策略胜率 {win_rate*100:.1f}% 低于50%")

        # 6. 盈亏比检查
        max_profit = details.get("max_profit", 0)
        net_cost = details.get("net_cost", 0)
        result.details["max_profit"] = round(max_profit, 2)
        result.details["net_cost"] = round(net_cost, 2)
        if max_profit > 0 and net_cost != 0:
            if net_cost > 0:
                profit_margin = max_profit / net_cost if net_cost else 0
                result.details["profit_margin"] = round(profit_margin, 4)

        # 计算综合风险分数
        penalty = len(result.warnings) * 15
        base_score: float = penalty
        base_score += net_delta * 100
        if margin > 0:
            base_score += (margin / self.max_margin_per_strategy) * 20

        result.score = min(base_score, 100)
        result.passed = len(result.warnings) == 0 and result.score < 50

        return result

    def evaluate_portfolio(
        self, signals: List[Dict[str, Any]]
    ) -> RiskCheckResult:
        """评估整个投资组合的聚合风险。

        Args:
            signals: 所有活跃信号列表。

        Returns:
            RiskCheckResult 实例。
        """
        result = RiskCheckResult(passed=True, score=0, details={})

        if not signals:
            result.details["message"] = "无活跃信号"
            return result

        # 聚合 Delta
        total_delta = sum(
            abs(s.get("details", {}).get("net_delta", 0)) for s in signals
        )
        result.details["total_absolute_delta"] = round(total_delta, 4)
        result.details["signal_count"] = len(signals)

        # 聚合保证金
        total_margin = sum(
            s.get("details", {}).get(
                "margin", s.get("details", {}).get("max_margin", 0)
            )
            for s in signals
        )
        result.details["total_margin"] = int(total_margin)

        if total_margin > self.max_margin_per_strategy * len(signals):
            result.add_warning(
                f"组合总保证金 ¥{total_margin:,.0f} 超出建议范围"
            )

        # 品种集中度
        symbols = [s.get("symbol", "") for s in signals]
        unique = set(symbols)
        if len(signals) > 3 and len(unique) < 2:
            result.add_warning(
                f"信号集中在 {len(unique)} 个品种, 分散度不足"
            )

        result.score = min(total_delta * 50 + len(result.warnings) * 15, 100)
        result.passed = len(result.warnings) == 0 and result.score < 60

        return result
