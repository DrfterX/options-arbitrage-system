"""
持仓风控引擎核心 — PositionRiskManager.

基于 risk_management 表的数据，检查持仓是否触发止盈/止损/移动止损。
每个 Cycle 由 Pipeline 调用，为 Paper Trading 持仓提供自动化保护。

数据流向:
    Pipeline (orchestrator.py)
        → PositionRiskManager.check_all_positions(price_map)
            → 逐一检查持仓 SL/TP/Trailing
                → risk_management 表更新（alert_count/alert_level）
                    → 返回触发结果列表
                        → 通知模块发送告警
"""

import logging
from typing import Any, Optional

from .db import Database
from .position_tracker import PositionTracker

logger = logging.getLogger(__name__)


class RiskCheckTriggerResult:
    """单次风控检查的触发结果。

    Attributes:
        position_id: 持仓 ID。
        contract: 合约代码，如 'SC2607'。
        symbol: 品种代码，如 'SC'。
        action: 触发动作类型。
        current_price: 检查时的当前价格。
        trigger_price: 触发条件价格（SL/TP/Trail 价格）。
        alert_level: 告警级别。
        alert_count: 累计触发次数。
        reason: 触发原因描述。
        direction: 持仓方向。
    """

    def __init__(
        self,
        position_id: int,
        contract: str,
        symbol: str,
        direction: str,
        action: str = "none",
        current_price: float = 0,
        trigger_price: float = 0,
        alert_level: str = "none",
        alert_count: int = 0,
        reason: str = "",
    ) -> None:
        """初始化触发结果。"""
        self.position_id = position_id
        self.contract = contract
        self.symbol = symbol
        self.direction = direction
        self.action = action
        self.current_price = current_price
        self.trigger_price = trigger_price
        self.alert_level = alert_level
        self.alert_count = alert_count
        self.reason = reason

    def is_triggered(self) -> bool:
        """是否触发了任何动作（非 'none'）。

        Returns:
            True 表示该持仓需要关注（SL/TP/Trail 触发）。
        """
        return self.action != "none"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典（用于日志/通知格式化）。"""
        return {
            "position_id": self.position_id,
            "contract": self.contract,
            "symbol": self.symbol,
            "direction": self.direction,
            "action": self.action,
            "current_price": self.current_price,
            "trigger_price": self.trigger_price,
            "alert_level": self.alert_level,
            "alert_count": self.alert_count,
            "reason": self.reason,
        }

    def __repr__(self) -> str:
        status = "⚡" if self.is_triggered() else "✓"
        return (
            f"<RiskCheck #{self.position_id} {self.contract} "
            f"{self.direction} {status} "
            f"action={self.action} alert={self.alert_level}[{self.alert_count}]>"
        )


# 告警升级阈值（连续触发次数）
ALERT_THRESHOLDS: dict[str, int] = {
    "info": 1,
    "warning": 3,
    "critical": 5,
}


class PositionRiskManager:
    """持仓风控引擎。

    负责检查所有 Open 持仓的风控条件（SL/TP/Trailing），
    管理告警升级状态，为自动平仓提供决策依据。

    设计原则：与 PositionTracker 职责分离 —
    PositionRiskManager 只做**检查**和**告警**，
    PositionTracker 负责**执行**（建仓/平仓）。

    Attributes:
        db: Database 实例。
        tracker: PositionTracker 实例（用于查询持仓详细信息）。
    """

    def __init__(
        self,
        db: Database,
        tracker: Optional[PositionTracker] = None,
    ) -> None:
        """初始化风控引擎。

        Args:
            db: Database 实例，需已完成全部表迁移。
            tracker: 可选 PositionTracker 实例。未提供时内部创建。
        """
        self.db = db
        self.tracker = tracker or PositionTracker(db)

    # ════════════════════════════════════════════════════════════
    # 公开方法
    # ════════════════════════════════════════════════════════════

    def check_position(
        self,
        position_id: int,
        current_price: float,
    ) -> RiskCheckTriggerResult:
        """检查单个持仓的风控条件。

        按优先级检查：止损 > 止盈 > 移动止损。
        只有一个条件会被触发（优先级最高者）。

        每次触发更新 risk_management 表的 alert_count 和 alert_level，
        无触发时重置告警状态。

        Args:
            position_id: 持仓 ID。
            current_price: 当前最新价格。

        Returns:
            RiskCheckTriggerResult — 检查结果。
        """
        conn = self.db.get_conn()

        # 1. 获取持仓信息
        position = conn.execute(
            "SELECT * FROM positions WHERE id=?", (position_id,)
        ).fetchone()
        if position is None:
            return RiskCheckTriggerResult(
                position_id=position_id,
                contract="",
                symbol="",
                direction="",
                action="none",
                current_price=current_price,
                reason="持仓不存在",
            )

        pos = dict(position)
        if pos["status"] != "open":
            return RiskCheckTriggerResult(
                position_id=position_id,
                contract=pos.get("contract", ""),
                symbol=pos.get("symbol", ""),
                direction=pos.get("direction", ""),
                action="none",
                current_price=current_price,
                reason=f"持仓已平仓（status={pos['status']}）",
            )

        # 2. 获取风控参数
        rm = conn.execute(
            "SELECT * FROM risk_management WHERE position_id=?",
            (position_id,),
        ).fetchone()
        if rm is None:
            # 无风控记录：视为无保护持仓，不触发
            return RiskCheckTriggerResult(
                position_id=position_id,
                contract=pos.get("contract", ""),
                symbol=pos.get("symbol", ""),
                direction=pos.get("direction", ""),
                action="none",
                current_price=current_price,
                reason="无风控记录（SL/TP 未设置）",
            )

        rm_dict = dict(rm)
        direction = pos["direction"]
        contract = pos.get("contract", "")
        symbol = pos.get("symbol", "")

        # 3. 检查触发条件（优先级：止损 > 止盈 > 移动止损）
        result = self._evaluate_triggers(
            direction=direction,
            current_price=current_price,
            sl_price=rm_dict.get("sl_price", 0) or 0,
            tp_price=rm_dict.get("tp_price", 0) or 0,
            trail_activation_price=rm_dict.get("trail_activation_price", 0) or 0,
            trail_distance=rm_dict.get("trail_distance", 0) or 0,
            trail_step=rm_dict.get("trail_step", 0) or 0,
            last_check_price=rm_dict.get("last_check_price", 0) or 0,
        )

        # 4. 更新告警状态
        alert_level = rm_dict.get("alert_level", "none") or "none"
        alert_count = rm_dict.get("alert_count", 0) or 0

        if result["action"] != "none":
            # 有触发：升级告警
            alert_count += 1
            alert_level = self._escalate_alert(alert_count)
            reason = result["reason"]
        else:
            # 无触发：重置告警
            alert_count = 0
            alert_level = "none"
            reason = "正常"

        # 5. 持久化到数据库
        self._update_risk_record(
            conn=conn,
            position_id=position_id,
            current_price=current_price,
            alert_level=alert_level,
            alert_count=alert_count,
            alert_reason=reason,
            is_triggered=(result["action"] != "none"),
        )

        return RiskCheckTriggerResult(
            position_id=position_id,
            contract=contract,
            symbol=symbol,
            direction=direction,
            action=result["action"],
            current_price=current_price,
            trigger_price=result.get("trigger_price", 0),
            alert_level=alert_level,
            alert_count=alert_count,
            reason=reason,
        )

    def check_all_positions(
        self,
        price_map: dict[str, float],
    ) -> list[RiskCheckTriggerResult]:
        """批量检查所有 Open 持仓的风控条件。

        遍历所有 status='open' 的持仓，逐一调用 check_position。
        price_map 中缺失的持仓将被跳过（记录为 none）。

        Args:
            price_map: {contract: current_price} 映射。
                       合约代码必须与 positions 表中的 contract 字段一致。

        Returns:
            RiskCheckTriggerResult 列表，按 position_id 升序。
        """
        conn = self.db.get_conn()
        open_positions = conn.execute(
            "SELECT id, contract, symbol, direction FROM positions WHERE status='open' "
            "ORDER BY id"
        ).fetchall()

        results: list[RiskCheckTriggerResult] = []
        for pos in open_positions:
            contract = pos["contract"]
            current_price = price_map.get(contract)
            if current_price is None:
                logger.debug("跳过持仓 #%d %s: 无价格数据", pos["id"], contract)
                results.append(RiskCheckTriggerResult(
                    position_id=pos["id"],
                    contract=contract,
                    symbol=pos.get("symbol", ""),
                    direction=pos.get("direction", ""),
                    action="none",
                    current_price=0,
                    reason="无价格数据",
                ))
                continue

            result = self.check_position(pos["id"], current_price)
            results.append(result)

        # 汇总日志
        triggered = [r for r in results if r.is_triggered()]
        if triggered:
            levels = {r.alert_level for r in triggered}
            logger.info(
                "风控检查: %d/%d 持仓触发, 告警级别=%s",
                len(triggered), len(results),
                ", ".join(sorted(levels)),
            )
            for r in triggered:
                logger.warning(
                    "风控触发 #%d %s %s: %s @ %.2f (trigger=%.2f, alert=%s[%d])",
                    r.position_id, r.contract, r.direction,
                    r.action, r.current_price, r.trigger_price,
                    r.alert_level, r.alert_count,
                )
        else:
            logger.info("风控检查: %d 持仓全部正常", len(results))

        return results

    # ════════════════════════════════════════════════════════════
    # 内部方法
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def _evaluate_triggers(
        direction: str,
        current_price: float,
        sl_price: float = 0,
        tp_price: float = 0,
        trail_activation_price: float = 0,
        trail_distance: float = 0,
        trail_step: float = 0,
        last_check_price: float = 0,
    ) -> dict[str, Any]:
        """评估触发条件（纯计算，无副作用）。

        优先级：止损 > 止盈 > 移动止损

        规则:
            LONG:
                - 止损: current_price <= sl_price (sl_price > 0)
                - 止盈: current_price >= tp_price (tp_price > 0)
                - 移动止损: trail_activation_price > 0 且 current_price >= trail_activation_price
                  → 激活后最高价回落 trail_distance 则触发
            SHORT:
                - 止损: current_price >= sl_price (sl_price > 0)
                - 止盈: current_price <= tp_price (tp_price > 0)
                - 移动止损: trail_activation_price > 0 且 current_price <= trail_activation_price
                  → 激活后最低价反弹 trail_distance 则触发

        Args:
            direction: 'LONG' 或 'SHORT'。
            current_price: 当前价格。
            sl_price: 止损价（0=未设置）。
            tp_price: 止盈价（0=未设置）。
            trail_activation_price: 移动止损激活价（0=未设置）。
            trail_distance: 移动止损距离（点数）。
            trail_step: 移动止损步进（预留，当前未使用）。
            last_check_price: 上次检查价格（用于计算 trail 区间极值）。

        Returns:
            dict: {'action': str, 'trigger_price': float, 'reason': str}。
        """
        # 1. 止损检查（最高优先级）
        if sl_price > 0:
            if direction == "LONG" and current_price <= sl_price:
                return {
                    "action": "stop_loss",
                    "trigger_price": sl_price,
                    "reason": f"止损触发: LONG SL={sl_price} ≥ 当前价 {current_price}",
                }
            if direction == "SHORT" and current_price >= sl_price:
                return {
                    "action": "stop_loss",
                    "trigger_price": sl_price,
                    "reason": f"止损触发: SHORT SL={sl_price} ≤ 当前价 {current_price}",
                }

        # 2. 止盈检查
        if tp_price > 0:
            if direction == "LONG" and current_price >= tp_price:
                return {
                    "action": "take_profit",
                    "trigger_price": tp_price,
                    "reason": f"止盈触发: LONG TP={tp_price} ≤ 当前价 {current_price}",
                }
            if direction == "SHORT" and current_price <= tp_price:
                return {
                    "action": "take_profit",
                    "trigger_price": tp_price,
                    "reason": f"止盈触发: SHORT TP={tp_price} ≥ 当前价 {current_price}",
                }

        # 3. 移动止损检查
        if trail_activation_price > 0 and trail_distance > 0:
            if direction == "LONG" and current_price >= trail_activation_price:
                # 激活后追踪最高价
                # 用 last_check_price 作为最近的已知高点近似
                highest = max(last_check_price, current_price) if last_check_price > 0 else current_price
                trail_stop = highest - trail_distance
                if current_price <= trail_stop:
                    return {
                        "action": "trailing_stop",
                        "trigger_price": round(trail_stop, 2),
                        "reason": (
                            f"移动止损触发: LONG 最高 {highest} - 步距 {trail_distance}"
                            f" = {trail_stop:.2f} ≥ 当前价 {current_price}"
                        ),
                    }
            if direction == "SHORT" and current_price <= trail_activation_price:
                # 激活后追踪最低价
                lowest = min(last_check_price, current_price) if last_check_price > 0 else current_price
                trail_stop = lowest + trail_distance
                if current_price >= trail_stop:
                    return {
                        "action": "trailing_stop",
                        "trigger_price": round(trail_stop, 2),
                        "reason": (
                            f"移动止损触发: SHORT 最低 {lowest} + 步距 {trail_distance}"
                            f" = {trail_stop:.2f} ≤ 当前价 {current_price}"
                        ),
                    }

        return {"action": "none", "trigger_price": 0, "reason": ""}

    @staticmethod
    def _escalate_alert(alert_count: int) -> str:
        """根据连续触发次数升级告警级别。

        Args:
            alert_count: 连续触发次数。

        Returns:
            告警级: 'info' / 'warning' / 'critical'。
        """
        if alert_count >= ALERT_THRESHOLDS["critical"]:
            return "critical"
        if alert_count >= ALERT_THRESHOLDS["warning"]:
            return "warning"
        return "info"

    def _update_risk_record(
        self,
        conn,
        position_id: int,
        current_price: float,
        alert_level: str,
        alert_count: int,
        alert_reason: str,
        is_triggered: bool,
    ) -> None:
        """更新风控记录。

        在检查后持久化最新状态：检查时间、价格、告警级别、触发次数。

        Args:
            conn: 数据库连接。
            position_id: 持仓 ID。
            current_price: 检查时的当前价。
            alert_level: 新告警级别。
            alert_count: 更新后的触发次数。
            alert_reason: 触发原因（或"正常"）。
            is_triggered: 本轮是否有触发。
        """
        import time as time_module

        now_ts = int(time_module.time())
        conn.execute(
            """
            UPDATE risk_management SET
                last_check_time=?,
                last_check_price=?,
                alert_level=?,
                alert_count=?,
                alert_reason=?,
                updated_at=datetime('now')
            WHERE position_id=?
            """,
            (now_ts, current_price, alert_level, alert_count, alert_reason, position_id),
        )
        conn.commit()

        if is_triggered:
            logger.info("风控更新 #%d: alert=%s count=%d reason='%s'",
                        position_id, alert_level, alert_count, alert_reason)