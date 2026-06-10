"""
智能信号过滤层 — 基于回测数据自动过滤信号推送。

6018 条历史回测数据驱动：
  - L1+L2 验证信号 96.6% 准确率 → 始终推送
  - 品种准确率 < 40% → 抑制（除非 L2 通过）
  - 能源化工板块 → 加权 + 优先推送
  - 评分 >= 0.60 → 提高推送优先级

用法:
    from signals.smart_filter import SmartFilter
    filter = SmartFilter()

    # 判断是否应该推送
    decision = filter.evaluate(symbol="RB", score=0.85,
                               level1_pass=True, level2_pass=True,
                               signal_type="ENTRY")
    if decision.should_push:
        dispatch(msg, level=decision.push_level, mode="stdout")
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# ─── 品种准确率表（回测 1 日准确率） ──────────────────────────
# 来源: futures.backtest._compute_by_symbol() 2026-06-01 回测数据
# 2026-06-10 更新 — 基于 5096 条有效回测
_SYMBOL_ACCURACY: Dict[str, float] = {
    # 高信度品种 (>= 80%)
    "RB": 100.0, "Y": 100.0, "P": 94.2,
    "EB": 84.6, "L": 84.6, "PG": 84.6, "TA": 84.6,
    # 中高信度 (60-80%)
    "CS": 68.3, "CU": 68.3, "LC": 68.3,
    "AG": 50.0, "AU": 50.0,
    "A": 50.0, "B": 31.7, "C": 0.0,  # 农产品差异大
    "M": 50.0, "Y": 100.0,
    "CF": 15.4, "SR": 50.0, "RM": 50.0, "OI": 2.9,
    "RU": 50.0, "NR": 0.0,
    # 低信度品种 (< 40%)
    "FG": 31.7, "SA": 28.8, "NI": 31.7,
    "J": 33.3, "JM": 50.0, "I": 50.0,
}

# 默认准确率（未在表中列出的品种）
_DEFAULT_ACCURACY = 50.0

# 板块加权系数
_SECTOR_BOOST: Dict[str, float] = {
    "能源化工": 1.15,  # +15% 权重 — 板块准确率 59.8%
    "贵金属": 1.0,
    "有色": 1.0,
    "黑色": 1.0,
    "农产品": 1.0,
    "新能源": 1.0,
}

# 板块映射
_SECTOR_MAP: Dict[str, str] = {
    "CU": "有色", "AL": "有色", "ZN": "有色", "PB": "有色",
    "NI": "有色", "SN": "有色", "AO": "有色",
    "AU": "贵金属", "AG": "贵金属",
    "RB": "黑色", "HC": "黑色", "I": "黑色", "J": "黑色",
    "JM": "黑色", "SS": "黑色", "SF": "黑色", "SM": "黑色",
    "BU": "能源化工", "FU": "能源化工", "LU": "能源化工",
    "SC": "能源化工", "RU": "能源化工", "NR": "能源化工",
    "BR": "能源化工", "TA": "能源化工", "MA": "能源化工",
    "FG": "能源化工", "SA": "能源化工", "UR": "能源化工",
    "PX": "能源化工", "EB": "能源化工", "EG": "能源化工",
    "PG": "能源化工", "PP": "能源化工", "V": "能源化工",
    "L": "能源化工", "SP": "能源化工", "SH": "能源化工",
    "M": "农产品", "Y": "农产品", "A": "农产品", "B": "农产品",
    "P": "农产品", "C": "农产品", "CS": "农产品",
    "JD": "农产品", "LH": "农产品", "CF": "农产品",
    "SR": "农产品", "AP": "农产品", "CJ": "农产品",
    "RM": "农产品", "OI": "农产品",
    "SI": "新能源", "LC": "新能源",
}

# 推送等级映射
_PUSH_LEVELS = ["HIGH", "NORMAL", "LOW", "SUPPRESS"]


class FilterDecision:
    """过滤决策结果。

    Attributes:
        should_push: 是否推送。
        push_level: 推送等级 (HIGH/NORMAL/LOW/SUPPRESS)。
        reason: 决策理由。
        confidence: 综合置信度 (0-100)。
        boost_factor: 板块加权系数。
    """

    __slots__ = ("should_push", "push_level", "reason", "confidence", "boost_factor")

    def __init__(
        self,
        should_push: bool = False,
        push_level: str = "SUPPRESS",
        reason: str = "",
        confidence: float = 0.0,
        boost_factor: float = 1.0,
    ):
        self.should_push = should_push
        self.push_level = push_level
        self.reason = reason
        self.confidence = confidence
        self.boost_factor = boost_factor

    def to_dict(self) -> dict:
        """转为字典便于序列化。"""
        return {
            "should_push": self.should_push,
            "push_level": self.push_level,
            "reason": self.reason,
            "confidence": round(self.confidence, 1),
            "boost_factor": round(self.boost_factor, 2),
        }

    def __repr__(self) -> str:
        return (
            f"FilterDecision(should_push={self.should_push}, "
            f"level={self.push_level}, conf={self.confidence:.1f}, "
            f"reason='{self.reason}')"
        )


class SmartFilter:
    """智能信号过滤层。

    基于回测数据的 5 条过滤规则：
        1. L1+L2 验证通过 → 始终推送 (HIGH)
        2. 高信度品种 (≥80%) → 正常推送
        3. 低信度品种 (<40%) → 抑制（除非规则 1 触发）
        4. 评分 ≥ 0.60 → 提高推送优先级
        5. 能源化工板块 → 加权

    此类无状态，可全局复用。
    """

    def __init__(self) -> None:
        logger.info("SmartFilter 初始化完成")

    def get_sector(self, symbol: str) -> str:
        """获取品种所属板块。"""
        return _SECTOR_MAP.get(symbol, "其他")

    def get_symbol_accuracy(self, symbol: str) -> float:
        """获取品种历史 1 日准确率。"""
        return _SYMBOL_ACCURACY.get(symbol, _DEFAULT_ACCURACY)

    def get_sector_boost(self, symbol: str) -> float:
        """获取板块加权系数。"""
        sector = self.get_sector(symbol)
        return _SECTOR_BOOST.get(sector, 1.0)

    def evaluate(
        self,
        symbol: str,
        score: float,
        level1_pass: bool = False,
        level2_pass: bool = False,
        level3_pass: bool = False,
        signal_type: str = "WATCH",
        direction: str = "",
    ) -> FilterDecision:
        """评估信号是否应该推送。

        Args:
            symbol: 品种代码。
            score: 信号评分 (0.0-1.0)。
            level1_pass: L1（周线+日线）是否通过。
            level2_pass: L2（小时线+15分钟）是否通过。
            level3_pass: L3（15分钟+3分钟）是否通过。
            signal_type: 信号类型 (NONE/WATCH/CANDIDATE/ENTRY)。
            direction: 信号方向 (LONG/SHORT)。

        Returns:
            FilterDecision 包含是否推送、等级和理由。
        """
        # ─── 规则 1: L1+L2 验证通过 → 始终推送 ───
        if level1_pass and level2_pass:
            confidence = 96.6  # 回测 96.6% 准确率
            return FilterDecision(
                should_push=True,
                push_level="HIGH",
                reason=f"L1+L2 验证通过 (历史准确率 {confidence}%)",
                confidence=confidence,
                boost_factor=self.get_sector_boost(symbol),
            )

        # ─── 规则 2 + 3: 按品种准确率过滤 ───
        acc = self.get_symbol_accuracy(symbol)

        # 低信度品种直接抑制
        if acc < 40.0:
            return FilterDecision(
                should_push=False,
                push_level="SUPPRESS",
                reason=f"品种 {symbol} 历史准确率 {acc:.1f}% (< 40%)，已自动抑制",
                confidence=acc,
                boost_factor=self.get_sector_boost(symbol),
            )

        # ─── 规则 4: 高评分加权 ───
        if score >= 0.60:
            boost = self.get_sector_boost(symbol)
            confidence = max(acc, 80.0) * boost

            # 高评分且高信度品种 → HIGH
            if acc >= 80.0:
                return FilterDecision(
                    should_push=True,
                    push_level="HIGH",
                    reason=f"评分 {score:.2f} >= 0.60，品种准确率 {acc:.1f}%",
                    confidence=min(confidence, 99.0),
                    boost_factor=boost,
                )

            # 高评分但中等信度 → NORMAL
            return FilterDecision(
                should_push=True,
                push_level="NORMAL",
                reason=f"评分 {score:.2f} >= 0.60（品种准确率 {acc:.1f}%）",
                confidence=min(confidence, 90.0),
                boost_factor=boost,
            )

        # ─── 中高信度品种正常推送 ───
        if acc >= 60.0:
            boost = self.get_sector_boost(symbol)
            return FilterDecision(
                should_push=True,
                push_level="NORMAL",
                reason=f"品种 {symbol} 准确率 {acc:.1f}% (≥ 60%)",
                confidence=acc * boost,
                boost_factor=boost,
            )

        # ─── ENTRY 信号即使中等信度也推送 ───
        if signal_type == "ENTRY":
            boost = self.get_sector_boost(symbol)
            return FilterDecision(
                should_push=True,
                push_level="NORMAL",
                reason=f"ENTRY 等级信号，品种准确率 {acc:.1f}%",
                confidence=max(acc * boost, 50.0),
                boost_factor=boost,
            )

        # ─── 其余信号低优先级推送 ───
        boost = self.get_sector_boost(symbol)
        effective_conf = acc * boost
        if effective_conf >= 50.0:
            return FilterDecision(
                should_push=True,
                push_level="LOW",
                reason=f"信号通过默认过滤（有效置信度 {effective_conf:.1f}%）",
                confidence=effective_conf,
                boost_factor=boost,
            )

        return FilterDecision(
            should_push=False,
            push_level="SUPPRESS",
            reason=f"综合置信度 {effective_conf:.1f}% < 50%，已抑制",
            confidence=effective_conf,
            boost_factor=boost,
        )

    def filter_signals(self, signals: list) -> list:
        """批量过滤信号列表。

        Args:
            signals: 信号字典列表，每项包含 symbol, score,
                    level1_pass, level2_pass, signal_type 等。

        Returns:
            添加了 filter_decision 字段的信号列表。
        """
        results = []
        for sig in signals:
            decision = self.evaluate(
                symbol=sig.get("symbol", ""),
                score=sig.get("score", 0.0),
                level1_pass=sig.get("level1_pass", False),
                level2_pass=sig.get("level2_pass", False),
                level3_pass=sig.get("level3_pass", False),
                signal_type=sig.get("signal_type", "WATCH"),
                direction=sig.get("direction", ""),
            )
            sig_with_decision = dict(sig)
            sig_with_decision["filter_decision"] = decision.to_dict()
            results.append(sig_with_decision)

        # 按置信度降序排列
        results.sort(
            key=lambda x: x["filter_decision"]["confidence"],
            reverse=True,
        )

        return results


# ─── 便捷方法 ─────────────────────────────────────────────────


def filtered_dispatch(
    symbol: str,
    score: float,
    level1_pass: bool,
    level2_pass: bool,
    level3_pass: bool,
    signal_type: str,
    msg: str,
    direction: str = "",
) -> bool:
    """便捷方法：评估 + 推送一体化。

    Args:
        symbol: 品种代码。
        score: 信号评分。
        level1_pass: L1 是否通过。
        level2_pass: L2 是否通过。
        level3_pass: L3 是否通过。
        signal_type: 信号类型。
        msg: 推送消息。
        direction: 方向。

    Returns:
        True 表示已推送，False 表示被过滤抑制。
    """
    from signals.dispatcher import dispatch

    filter_ = SmartFilter()
    decision = filter_.evaluate(
        symbol=symbol,
        score=score,
        level1_pass=level1_pass,
        level2_pass=level2_pass,
        level3_pass=level3_pass,
        signal_type=signal_type,
        direction=direction,
    )

    if decision.should_push:
        dispatch(msg, level=decision.push_level, mode="stdout")
        logger.info(
            "Filtered dispatch: %s %s -> %s (%s)",
            symbol, signal_type, decision.push_level, decision.reason,
        )
        return True

    logger.debug(
        "Filtered dispatch: %s %s SUPPRESSED (%s)",
        symbol, signal_type, decision.reason,
    )
    return False
