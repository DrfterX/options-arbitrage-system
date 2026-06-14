"""
Phase 1 滚动胜率监控模块（独立于信号引擎）。

职责：
  1. 读取 trades 表，统计已平仓交易的胜率
  2. 维护滚动窗口胜率（最后 10/25/50 笔）
  3. 与 phase1_win_rate_target（57%）比对
  4. 检查 30 天废弃条件
  5. 提供 get_phase1_status() 查询接口，供 orchestrator/notifier/日报调用

设计原则：
  - 只读 trades/positions 表，不写任何数据
  - 不依赖 scorer.py 或信号引擎
  - 仅关注交易结果统计，不涉及入场判断

用法:
    from futures.win_tracker import get_phase1_status, check_phase1_abort_condition
    status = get_phase1_status(db)
    abort_reason = check_phase1_abort_condition(db)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from core.db import Database
from config.settings import GRADIENT_STRATEGY

logger = logging.getLogger(__name__)


# ─── 数据结构 ──────────────────────────────────────────────────


@dataclass
class Phase1Status:
    """Phase 1 梯度策略胜率状态快照。

    Attributes:
        total_trades: 已平仓总笔数（action=close 有 pnl）。
        wins: 盈利笔数（pnl > 0）。
        losses: 亏损笔数（pnl <= 0，含保本）。
        win_rate: 整体胜率（小数，如 0.62）。
        target_win_rate: 目标胜率（来自 GRADIENT_STRATEGY）。
        total_pnl: 已平仓总盈亏。
        avg_pnl: 平均每笔盈亏。
        rolling_win_rate_10: 最近 10 笔滚动胜率。
        rolling_win_rate_25: 最近 25 笔滚动胜率。
        rolling_win_rate_50: 最近 50 笔滚动胜率。
        sample_size_target: 目标样本量（来自 GRADIENT_STRATEGY）。
        deadline_days: 截止天数（来自 GRADIENT_STRATEGY）。
        days_elapsed: 从首笔交易至今经过的天数。
        first_trade_time: 首笔平仓时间（Unix 秒）。
        last_trade_time: 最近一笔平仓时间（Unix 秒）。
        is_target_met: 整体胜率是否 >= 目标。
        is_expired: 超过截止天数且未达目标。
        is_completed: 是否达到目标样本量。
    """

    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    target_win_rate: float = 0.57
    total_pnl: float = 0.0
    avg_pnl: float = 0.0
    rolling_win_rate_10: float = 0.0
    rolling_win_rate_25: float = 0.0
    rolling_win_rate_50: float = 0.0
    sample_size_target: int = 100
    deadline_days: int = 30
    days_elapsed: float = 0.0
    first_trade_time: Optional[int] = None
    last_trade_time: Optional[int] = None
    is_target_met: bool = False
    is_expired: bool = False
    is_completed: bool = False

    @property
    def progress_pct(self) -> float:
        """样本量完成百分比（0~100）。"""
        if self.sample_size_target <= 0:
            return 0.0
        return min(100.0, round(self.total_trades / self.sample_size_target * 100, 1))

    @property
    def needed_to_target(self) -> int:
        """达到目标胜率还需的连续胜笔数（仅当未达标时有效）。"""
        if self.is_target_met or self.total_trades == 0:
            return 0
        # 解方程: (wins + x) / (total_trades + x) >= target
        # wins + x >= target * (total_trades + x)
        # wins + x >= target*total + target*x
        # x - target*x >= target*total - wins
        # x * (1 - target) >= target*total - wins
        target = self.target_win_rate
        numerator = target * self.total_trades - self.wins
        denominator = 1.0 - target
        if denominator <= 0 or numerator <= 0:
            return 0
        return int(numerator / denominator) + 1


# ─── 查询接口 ──────────────────────────────────────────────────


def get_phase1_status(db: Database) -> Phase1Status:
    """查询 Phase 1 梯度策略的胜率状态。

    从 trades 表读取全部已平仓记录（action='close' AND pnl IS NOT NULL），
    计算整体胜率、滚动窗口胜率、时间/样本量进度。

    Args:
        db: Database 实例。

    Returns:
        Phase1Status 数据类。若无平仓记录，所有字段为默认值。
    """
    gs = GRADIENT_STRATEGY
    target = gs.get("phase1_win_rate_target", 0.57)
    sample_size = gs.get("phase1_sample_size", 100)
    deadline_days = gs.get("phase1_deadline_days", 30)

    status = Phase1Status(
        target_win_rate=target,
        sample_size_target=sample_size,
        deadline_days=deadline_days,
    )

    # 1. 获取所有已平仓交易（按时间升序）
    conn = db.get_conn()
    close_trades = conn.execute(
        """SELECT pnl, time
           FROM trades
           WHERE action='close' AND pnl IS NOT NULL
           ORDER BY time ASC"""
    ).fetchall()

    if not close_trades:
        return status

    total = len(close_trades)
    pnls = [t["pnl"] for t in close_trades]
    wins_count = sum(1 for p in pnls if p > 0)
    losses_count = sum(1 for p in pnls if p <= 0)
    total_pnl = sum(pnls)

    status.total_trades = total
    status.wins = wins_count
    status.losses = losses_count
    status.win_rate = round(wins_count / total, 4) if total > 0 else 0.0
    status.total_pnl = round(total_pnl, 2)
    status.avg_pnl = round(total_pnl / total, 2) if total > 0 else 0.0
    status.first_trade_time = close_trades[0]["time"]
    status.last_trade_time = close_trades[-1]["time"]

    # 2. 滚动窗口胜率（最后 N 笔）
    if total >= 10:
        recent_10_pnls = [t["pnl"] for t in close_trades[-10:]]
        status.rolling_win_rate_10 = round(
            sum(1 for p in recent_10_pnls if p > 0) / 10, 4
        )
    else:
        status.rolling_win_rate_10 = round(wins_count / total, 4) if total > 0 else 0.0

    if total >= 25:
        recent_25_pnls = [t["pnl"] for t in close_trades[-25:]]
        status.rolling_win_rate_25 = round(
            sum(1 for p in recent_25_pnls if p > 0) / 25, 4
        )
    else:
        status.rolling_win_rate_25 = round(wins_count / total, 4) if total > 0 else 0.0

    if total >= 50:
        recent_50_pnls = [t["pnl"] for t in close_trades[-50:]]
        status.rolling_win_rate_50 = round(
            sum(1 for p in recent_50_pnls if p > 0) / 50, 4
        )
    else:
        status.rolling_win_rate_50 = round(wins_count / total, 4) if total > 0 else 0.0

    # 3. 目标判断
    status.is_target_met = status.win_rate >= target
    status.is_completed = total >= sample_size

    # 4. 废弃条件检查（时间维度）
    if status.first_trade_time:
        now_ts = int(datetime.now(timezone.utc).timestamp())
        days_elapsed = (now_ts - status.first_trade_time) / 86400.0
        status.days_elapsed = round(days_elapsed, 1)
        status.is_expired = (
            days_elapsed > deadline_days and not status.is_target_met
        )

    return status


def check_phase1_abort_condition(db: Database) -> Optional[str]:
    """检查 Phase 1 是否需要废弃。

    废弃条件（二选一，满足即触发）：
      1. 超过 30 天未达 100 笔且胜率未达标 → 废弃
      2. 达成 100 笔但胜率 < 57% → 废弃

    Args:
        db: Database 实例。

    Returns:
        None = 继续运行；str = 废弃原因描述。
    """
    status = get_phase1_status(db)

    # 条件 1: 超过 30 天且未达 100 笔
    if status.is_expired and not status.is_completed:
        return (
            f"Phase 1 废弃: {status.days_elapsed}天/{status.total_trades}笔, "
            f"未在{status.deadline_days}天内达成{status.sample_size_target}笔"
        )

    # 条件 2: 完成 100 笔但胜率不达标
    if status.is_completed and not status.is_target_met:
        return (
            f"Phase 1 废弃: {status.total_trades}笔 胜率{status.win_rate:.1%}, "
            f"低于目标{status.target_win_rate:.0%}"
        )

    return None


def get_win_trend(db: Database, window: int = 20) -> dict:
    """生成胜率趋势数据，用于日报/监控展示。

    以最近 N 笔为滑动窗口，生成每笔的累计胜率曲线摘要。

    Args:
        db: Database 实例。
        window: 滚动窗口大小（默认 20）。

    Returns:
        {
            "recent_win_rates": [最近 window 笔的每笔滚动胜率],
            "peak_win_rate": 期间最高滚动胜率,
            "trough_win_rate": 期间最低滚动胜率,
            "current_win_rate": 当前滚动胜率,
            "trend_direction": "up" | "down" | "flat",
        }
    """
    conn = db.get_conn()
    close_trades = conn.execute(
        """SELECT pnl, time
           FROM trades
           WHERE action='close' AND pnl IS NOT NULL
           ORDER BY time ASC"""
    ).fetchall()

    if len(close_trades) < window:
        return {
            "recent_win_rates": [],
            "peak_win_rate": 0.0,
            "trough_win_rate": 0.0,
            "current_win_rate": 0.0,
            "trend_direction": "flat",
        }

    # 滑动窗口胜率计算
    recent_rates = []
    pnls = [t["pnl"] for t in close_trades]
    for i in range(len(pnls) - window + 1):
        chunk = pnls[i : i + window]
        rate = sum(1 for p in chunk if p > 0) / window
        recent_rates.append(round(rate, 4))

    current = recent_rates[-1] if recent_rates else 0.0
    peak = max(recent_rates) if recent_rates else 0.0
    trough = min(recent_rates) if recent_rates else 0.0

    # 趋势方向判断：比较前半段和后半段均值
    mid = len(recent_rates) // 2
    if mid > 0:
        first_half = sum(recent_rates[:mid]) / mid
        second_half = sum(recent_rates[mid:]) / (len(recent_rates) - mid)
        diff = second_half - first_half
        if diff > 0.03:
            trend = "up"
        elif diff < -0.03:
            trend = "down"
        else:
            trend = "flat"
    else:
        trend = "flat"

    return {
        "recent_win_rates": recent_rates,
        "peak_win_rate": peak,
        "trough_win_rate": trough,
        "current_win_rate": current,
        "trend_direction": trend,
    }


def format_phase1_summary(status: Phase1Status) -> str:
    """格式化 Phase 1 胜率状态为可读文本，用于推送/日报。

    Args:
        status: Phase1Status 数据类。

    Returns:
        格式化的文本摘要。
    """
    lines = [
        "📊 Phase 1 胜率监控",
        f"  进度: {status.total_trades}/{status.sample_size_target} 笔 ({status.progress_pct}%)",
        f"  整体胜率: {status.win_rate:.1%} {'✅' if status.is_target_met else '❌'} 目标: {status.target_win_rate:.0%}",
        f"  滚动胜率: 10笔={status.rolling_win_rate_10:.0%} "
        f"25笔={status.rolling_win_rate_25:.0%} "
        f"50笔={status.rolling_win_rate_50:.0%}",
        f"  盈亏: 总{status.total_pnl:+.1f} 均{status.avg_pnl:+.2f}/笔",
    ]

    if status.total_trades > 0:
        lines.append(
            f"  时间: {status.days_elapsed}天 "
            f"({'⚠️超时' if status.is_expired else '⏳进行中'})"
        )
        if not status.is_target_met:
            need = status.needed_to_target
            lines.append(f"  还需连续胜 {need} 笔可达目标")

    if status.is_completed and status.is_target_met:
        lines.append("  🎉 Phase 1 达标！胜率和样本量均满足条件")
    elif status.is_expired:
        lines.append("  ❌ Phase 1 已超时废弃")

    return "\n".join(lines)
