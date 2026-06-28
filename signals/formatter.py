"""
统一消息格式化器 UnifiedFormatter。

提供期货N型信号、期权策略信号的统一消息格式化，
以及日报、IV排名报告的格式化。

分级推送统一标准：
    - ENTRY (🔴): 期货三级全过 (score>=1.0) / 期权策略通过风控+评分>70
    - CANDIDATE (🟡): 期货L1+L2通过 / 期权有策略但未完全通过风控
    - WATCH (🔵): 期货仅L1通过 / 期权IV极端但无通过风控的策略
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.risk_manager import RiskCheckTriggerResult

logger = logging.getLogger(__name__)

# 信号等级 emoji 标记
_LEVEL_EMOJI: Dict[str, str] = {
    "ENTRY": "🔴",
    "CANDIDATE": "🟡",
    "WATCH": "🔵",
    "NONE": "⚪",
    "DAILY": "📊",
}

# 方向中文
_DIRECTION_CN: Dict[str, str] = {
    "LONG": "多头",
    "SHORT": "空头",
    "NONE": "无",
}

# 策略中文
_STRATEGY_CN: Dict[str, str] = {
    "ratio_spread": "比例价差",
    "call_ratio_spread": "看涨比例价差",
    "put_ratio_spread": "看跌比例价差",
    "short_strangle": "卖出宽跨式",
    "iron_condor": "铁鹰式",
}

# 风控告警 emoji / 中文
_RISK_LEVEL_EMOJI: Dict[str, str] = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🟢",
    "none": "⚪",
}

_ACTION_CN: Dict[str, str] = {
    "stop_loss": "止损触发",
    "take_profit": "止盈触发",
    "trailing_stop": "移动止损触发",
    "none": "正常",
}

_DIRECTION_ARROW: Dict[str, str] = {
    "LONG": "📈 多头",
    "SHORT": "📉 空头",
    "FLAT": "➖ 中性",
    "NONE": "",
}

_ACTION_SUGGESTION: Dict[str, str] = {
    "stop_loss": "⚠️ 建议评估是否手动平仓或调整止损位",
    "take_profit": "✅ 建议考虑部分或全部止盈，锁定利润",
    "trailing_stop": "👀 移动止损已触发，建议关注后续走势",
}


class UnifiedFormatter:
    """统一消息格式化器。

    所有方法均为静态方法，无状态，可直接类调用。
    """

    # 向后兼容：类级别引用（orchestrator.py 等外部通过 UnifiedFormatter._ACTION_CN 访问）
    _RISK_LEVEL_EMOJI = _RISK_LEVEL_EMOJI
    _ACTION_CN = _ACTION_CN
    _DIRECTION_ARROW = _DIRECTION_ARROW
    _ACTION_SUGGESTION = _ACTION_SUGGESTION

    @staticmethod
    def _bars(emoji: str, title: str) -> str:
        """生成分隔条。

        Args:
            emoji: emoji 标记。
            title: 标题文本。

        Returns:
            格式化后的分隔条。
        """
        return f"{emoji} {'─' * 8} {title} {'─' * 8} {emoji}"

    # ── 期货信号 ──────────────────────────────────────────────

    @staticmethod
    def format_futures_signal(result) -> str:
        """格式化期货N型信号消息（三级嵌套详情）。

        Args:
            result: ``futures.scorer.SignalResult`` dataclass 实例。

        Returns:
            格式化后的多行消息字符串。
        """
        symbol = getattr(result, "symbol", "?")
        contract = getattr(result, "contract", "?")
        direction = getattr(result, "direction", "NONE")
        signal_type = getattr(result, "signal_type", "NONE")
        emoji = _LEVEL_EMOJI.get(signal_type, "⚪")
        dir_cn = _DIRECTION_CN.get(direction, direction)
        score = getattr(result, "overall_score", 0.0)
        entry_price = getattr(result, "entry_price", None)
        stop_loss = getattr(result, "stop_loss", None)
        take_profit = getattr(result, "take_profit", None)

        lines: List[str] = [
            UnifiedFormatter._bars(emoji, f"期货信号 {symbol}"),
            f"{emoji} **{symbol} {contract}** | {dir_cn} | {signal_type}",
            f"   综合评分: {score:.2f}",
        ]

        # Level1 详情
        level1 = getattr(result, "level1", {})
        if isinstance(level1, dict):
            l1_desc = level1.get("description", "")
            l1_passed = "✅" if level1.get("passed") else "❌"
            lines.append(f"  Level1 (周线+日线MACD): {l1_passed}")
            if l1_desc:
                lines.append(f"    {l1_desc}")

        # Level2 详情
        level2 = getattr(result, "level2", {})
        if isinstance(level2, dict):
            l2_desc = level2.get("description", "")
            l2_passed = "✅" if level2.get("passed") else "❌"
            lines.append(f"  Level2 (小时线+15分钟MACD): {l2_passed}")
            if l2_desc:
                lines.append(f"    {l2_desc}")
            if not level2.get("passed") and level2.get("reason"):
                lines.append(f"    原因: {level2['reason']}")

        # Level3 详情
        level3 = getattr(result, "level3", {})
        if isinstance(level3, dict):
            l3_desc = level3.get("description", "")
            l3_passed = "✅" if level3.get("passed") else "❌"
            lines.append(f"  Level3 (15分钟+3分钟MACD): {l3_passed}")
            if l3_desc:
                lines.append(f"    {l3_desc}")
            if not level3.get("passed") and level3.get("reason"):
                lines.append(f"    原因: {level3['reason']}")

        # 入场/止损/止盈
        if entry_price is not None:
            ep_line = f"  入场: {entry_price:.2f}"
            if stop_loss is not None:
                ep_line += f"  |  止损: {stop_loss:.2f}"
            if take_profit is not None:
                ep_line += f"  |  止盈: {take_profit:.2f}"
            lines.append(ep_line)

        # 加分项
        bonus = getattr(result, "bonus", [])
        if bonus:
            bonus_passed = [b for b in bonus if isinstance(b, dict) and b.get("passed")]
            if bonus_passed:
                bonus_text = ", ".join(b.get("check", "?") for b in bonus_passed)
                lines.append(f"  加分项: {bonus_text}")

        return "\n".join(lines)

    # ── 期权策略 ──────────────────────────────────────────────

    @staticmethod
    def format_options_strategy(signal_dict: dict) -> str:
        """格式化期权策略消息。

        Args:
            signal_dict: 期权策略信号字典，包含:
                symbol, contract, strategy, signal_type, strength,
                futures_price, iv_avg, iv_percentile, iv_level,
                net_delta, net_theta, net_vega, max_profit, max_loss,
                unified_score, description 等。

        Returns:
            格式化后的多行消息字符串。
        """
        symbol = signal_dict.get("symbol", "?")
        contract = signal_dict.get("contract", "?")
        strategy = signal_dict.get("strategy", "?")
        signal_type = signal_dict.get("signal_type", "WATCH")
        emoji = _LEVEL_EMOJI.get(signal_type, "⚪")
        strategy_cn = _STRATEGY_CN.get(strategy, strategy)
        score = signal_dict.get("unified_score", signal_dict.get("score", 0))
        futures_price = signal_dict.get("futures_price", 0)
        iv_avg = signal_dict.get("iv_avg", 0)
        iv_percentile = signal_dict.get("iv_percentile", 0)
        iv_level = signal_dict.get("iv_level", "未知")
        net_delta = signal_dict.get("net_delta", 0)
        net_theta = signal_dict.get("net_theta", 0)
        net_vega = signal_dict.get("net_vega", 0)
        max_profit = signal_dict.get("max_profit", 0)
        max_loss = signal_dict.get("max_loss", 0)
        win_rate = signal_dict.get("win_rate", signal_dict.get("details", {}).get("win_rate", 0))
        days_to_expiry = signal_dict.get("days_to_expiry", 0)
        margin_required = signal_dict.get("margin_required", 0)
        description = signal_dict.get("description", "")
        reason = signal_dict.get("reason", "")

        lines: List[str] = [
            UnifiedFormatter._bars(emoji, f"期权策略 {symbol}"),
            f"{emoji} **{symbol} {contract}** | {strategy_cn} | {signal_type}",
            f"   标的价格: {futures_price:.1f}  |  综合评分: {score:.1f}",
            f"   IV: {iv_avg*100:.1f}%  (百分位 {iv_percentile:.0f}%, {iv_level})",
            f"   Delta: {net_delta:.4f}  |  Theta: {net_theta:.4f}  |  Vega: {net_vega:.4f}",
            f"   最大利润: {max_profit:.1f}  |  最大亏损: {max_loss:.1f}",
        ]

        if days_to_expiry and margin_required:
            lines.append(f"   DTE: {days_to_expiry}  |  保证金: ¥{margin_required:.0f}")
        elif days_to_expiry:
            lines.append(f"   DTE: {days_to_expiry}")
        elif margin_required:
            lines.append(f"   保证金: ¥{margin_required:.0f}")

        if isinstance(win_rate, (int, float)) and win_rate > 0:
            lines.append(f"   胜率: {win_rate*100:.1f}%")

        if description:
            lines.append(f"   策略: {description}")

        if reason:
            lines.append(f"   原因: {reason}")

        return "\n".join(lines)

    # ── 日报 ──────────────────────────────────────────────────

    @staticmethod
    def format_daily_summary(
        futures_results: list,
        options_results: list,
        scanned: int,
    ) -> str:
        """格式化日报消息（期货信号+期权策略合并）。

        Args:
            futures_results: SignalResult 列表。
            options_results: 期权策略信号字典列表。
            scanned: 扫描品种总数。

        Returns:
            格式化后的日报字符串。
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines: List[str] = [
            f"📊 {'=' * 10} 收盘总结 {now_str} {'=' * 10} 📊",
            f"扫描品种: {scanned}",
            "",
        ]

        # ── 期货部分 ──
        entry_futures = [
            r for r in futures_results
            if getattr(r, "signal_type", "NONE") == "ENTRY"
        ]
        candidate_futures = [
            r for r in futures_results
            if getattr(r, "signal_type", "NONE") == "CANDIDATE"
        ]
        watch_futures = [
            r for r in futures_results
            if getattr(r, "signal_type", "NONE") == "WATCH"
        ]

        lines.append("🔴 ─── 期货 ENTRY 信号 ───")
        if entry_futures:
            for r in entry_futures:
                direction = getattr(r, "direction", "NONE")
                dir_cn = _DIRECTION_CN.get(direction, direction)
                score = getattr(r, "overall_score", 0)
                ep = getattr(r, "entry_price", None)
                sl = getattr(r, "stop_loss", None)
                tp = getattr(r, "take_profit", None)
                line = f"  {r.symbol} {r.contract} {dir_cn} 评分:{score:.2f}"
                if ep:
                    line += f" 入场:{ep:.1f}"
                    if sl:
                        line += f" 止损:{sl:.1f}"
                    if tp:
                        line += f" 止盈:{tp:.1f}"
                lines.append(line)
        else:
            lines.append("  (无)")

        lines.append("")
        lines.append("🟡 ─── 期货 CANDIDATE 信号 ───")
        if candidate_futures:
            for r in candidate_futures:
                direction = getattr(r, "direction", "NONE")
                dir_cn = _DIRECTION_CN.get(direction, direction)
                score = getattr(r, "overall_score", 0)
                lines.append(f"  {r.symbol} {r.contract} {dir_cn} 评分:{score:.2f}")
        else:
            lines.append("  (无)")

        lines.append("")
        lines.append("🔵 ─── 期货 WATCH 信号 ───")
        if watch_futures:
            for r in watch_futures:
                direction = getattr(r, "direction", "NONE")
                dir_cn = _DIRECTION_CN.get(direction, direction)
                lines.append(f"  {r.symbol} {r.contract} {dir_cn}")
        else:
            lines.append("  (无)")

        # ── 期权部分 ──
        entry_options = [
            o for o in options_results
            if o.get("signal_type", "") == "ENTRY"
        ]
        candidate_options = [
            o for o in options_results
            if o.get("signal_type", "") == "CANDIDATE"
        ]
        watch_options = [
            o for o in options_results
            if o.get("signal_type", "") == "WATCH"
        ]

        lines.append("")
        lines.append("🔴 ─── 期权 ENTRY 策略 ───")
        if entry_options:
            for o in entry_options:
                strategy = o.get("strategy", "?")
                strategy_cn = _STRATEGY_CN.get(strategy, strategy)
                score = o.get("unified_score", o.get("score", 0))
                lines.append(
                    f"  {o.get('symbol','?')} {o.get('contract','?')} "
                    f"{strategy_cn} 评分:{score:.1f}"
                )
        else:
            lines.append("  (无)")

        lines.append("")
        lines.append("🟡 ─── 期权 CANDIDATE 策略 ───")
        if candidate_options:
            for o in candidate_options:
                strategy = o.get("strategy", "?")
                strategy_cn = _STRATEGY_CN.get(strategy, strategy)
                score = o.get("unified_score", o.get("score", 0))
                lines.append(
                    f"  {o.get('symbol','?')} {o.get('contract','?')} "
                    f"{strategy_cn} 评分:{score:.1f}"
                )
        else:
            lines.append("  (无)")

        lines.append("")
        lines.append("🔵 ─── 期权 WATCH 策略 ───")
        if watch_options:
            for o in watch_options:
                strategy = o.get("strategy", "?")
                strategy_cn = _STRATEGY_CN.get(strategy, strategy)
                lines.append(
                    f"  {o.get('symbol','?')} {o.get('contract','?')} "
                    f"{strategy_cn}"
                )
        else:
            lines.append("  (无)")

        # ── 统计摘要 ──
        total_entry = len(entry_futures) + len(entry_options)
        total_candidate = len(candidate_futures) + len(candidate_options)
        total_watch = len(watch_futures) + len(watch_options)

        lines.append("")
        lines.append(f"📊 {'=' * 10} 统计摘要 {'=' * 10} 📊")
        lines.append(f"  ENTRY: {total_entry} | CANDIDATE: {total_candidate} | WATCH: {total_watch}")
        lines.append(f"  (期货: E{len(entry_futures)} C{len(candidate_futures)} W{len(watch_futures)}"
                     f" | 期权: E{len(entry_options)} C{len(candidate_options)} W{len(watch_options)})")

        return "\n".join(lines)

    # ── IV 排名 ───────────────────────────────────────────────

    @staticmethod
    def format_iv_rank(iv_status_list: list) -> str:
        """格式化IV排名报告。

        Args:
            iv_status_list: IV 状态字典列表，每项含:
                symbol, contract, current_iv, percentile, level,
                futures_price, samples 等。

        Returns:
            格式化后的IV排名报告字符串。
        """
        lines: List[str] = [
            UnifiedFormatter._bars("📊", "IV 排名报告"),
            "",
        ]

        # 极端IV品种（排除数据不足的品种）
        extreme = [s for s in iv_status_list if s.get("level") in ("极端高", "极端低")]
        if extreme:
            lines.append("⚠️ 极端IV品种:")
            for s in extreme:
                lines.append(
                    f"  {s['symbol']} {s['contract']} "
                    f"IV={s['current_iv']*100:.1f}% "
                    f"(百分位{s['percentile']:.0f}%, {s['level']})"
                )
            lines.append("")

        # 数据不足品种
        insufficient = [s for s in iv_status_list if s.get("level") == "数据不足"]
        if insufficient:
            lines.append("⚪ 数据不足品种（历史样本<10条）:")
            for s in insufficient:
                lines.append(
                    f"  {s['symbol']} {s['contract']} "
                    f"IV={s['current_iv']*100:.1f}% (样本{s.get('samples', 0)}条)"
                )
            lines.append("")

        # 高IV TOP5
        high_iv = sorted(
            [s for s in iv_status_list if s.get("current_iv", 0) > 0],
            key=lambda x: x.get("current_iv", 0),
            reverse=True,
        )[:5]
        lines.append("📈 高IV TOP5:")
        for s in high_iv:
            lines.append(
                f"  {s['symbol']} {s['contract']} "
                f"IV={s['current_iv']*100:.1f}% "
                f"(百分位{s['percentile']:.0f}%, {s['level']})"
            )

        lines.append("")

        # 低IV TOP5
        low_iv = sorted(
            [s for s in iv_status_list if s.get("current_iv", 0) > 0],
            key=lambda x: x.get("current_iv", 0),
        )[:5]
        lines.append("📉 低IV TOP5:")
        for s in low_iv:
            lines.append(
                f"  {s['symbol']} {s['contract']} "
                f"IV={s['current_iv']*100:.1f}% "
                f"(百分位{s['percentile']:.0f}%, {s['level']})"
            )

        return "\n".join(lines)

    # ── 风控告警 ───────────────────────────────────────────────

    _RISK_LEVEL_EMOJI: Dict[str, str] = {
        "critical": "🔴",
        "warning": "🟡",
        "info": "🟢",
        "none": "⚪",
    }

    _ACTION_CN: Dict[str, str] = {
        "stop_loss": "止损触发",
        "take_profit": "止盈触发",
        "trailing_stop": "移动止损触发",
        "none": "正常",
    }

    _DIRECTION_ARROW: Dict[str, str] = {
        "LONG": "📈 多头",
        "SHORT": "📉 空头",
        "NONE": "—",
    }


    @staticmethod
    def format_risk_alert(r: "RiskCheckTriggerResult") -> str:
        """格式化单条风控触发告警消息。

        生成结构化的告警文本，包含持仓详情、价格对比、偏离幅度和建议操作。
        统一用于 Telegram / macOS 通知。

        Args:
            r: RiskCheckTriggerResult 实例（来自 core.risk_manager）。

        Returns:
            格式化后的多行告警消息字符串。
        """
        level_emoji = _RISK_LEVEL_EMOJI.get(r.alert_level, "⚪")
        action_cn = _ACTION_CN.get(r.action, r.action)
        dir_arrow = _DIRECTION_ARROW.get(r.direction, r.direction)
        suggestion = UnifiedFormatter._ACTION_SUGGESTION.get(r.action, "")

        # 价格偏离计算
        if r.trigger_price > 0 and r.current_price > 0:
            delta = r.current_price - r.trigger_price
            delta_pct = (delta / r.trigger_price) * 100
            delta_sign = "+" if delta >= 0 else ""
            delta_str = f"{delta_sign}{delta:.2f} ({delta_sign}{delta_pct:.1f}%)"
        else:
            delta_str = "—"

        lines: List[str] = [
            f"{level_emoji} **风控触发 #{r.position_id} {r.contract}** {dir_arrow}",
            f"  动作: {action_cn}  |  告警: {r.alert_level}[{r.alert_count}]",
            f"  当前价: {r.current_price:.2f}  |  触发价: {r.trigger_price:.2f}",
            f"  偏离: {delta_str}",
            f"  原因: {r.reason}",
        ]
        if suggestion:
            lines.append(f"  {suggestion}")

        return "\n".join(lines)

    @staticmethod
    def format_risk_group_summary(
        results: list,
    ) -> str:
        """格式化风控触发分组摘要（用于通知标题/副标题）。

        按告警级别统计触发数量，生成紧凑摘要。

        Args:
            results: RiskCheckTriggerResult 列表（仅 is_triggered()==True 的项）。

        Returns:
            摘要字符串，如 "🔴1 🔸 止损触发  |  🟡2 🔸 止盈触发"。
        """
        from collections import Counter
        action_counts: Counter = Counter()
        level_counts: Counter = Counter()
        for r in results:
            action_counts[r.action] += 1
            level_counts[r.alert_level] += 1

        level_parts: list[str] = []
        for level in ("critical", "warning", "info"):
            if level_counts.get(level, 0) > 0:
                emoji = UnifiedFormatter._RISK_LEVEL_EMOJI.get(level, "⚪")
                level_parts.append(f"{emoji}{level_counts[level]}")

        action_parts: list[str] = []
        for action in ("stop_loss", "take_profit", "trailing_stop"):
            cnt = action_counts.get(action, 0)
            if cnt > 0:
                cn = UnifiedFormatter._ACTION_CN.get(action, action)
                action_parts.append(f"{cnt} 🔸 {cn}")

        summary = " | ".join(level_parts) if level_parts else "触发"
        details = "  |  ".join(action_parts) if action_parts else ""
        if details:
            summary = f"{summary}  |  {details}"
        return summary
