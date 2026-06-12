"""
Paper Trading 持仓追踪模块 — PositionTracker.

根据 ENTRY 信号自动建仓、追踪盈亏、管理持仓生命周期。

数据流向:
    ENTRY 信号 (futures_signals/options_signals)
        → PositionTracker.open_position()
            → DB positions 表 (新持仓)
                → PositionTracker.update_pnl() (定时更新浮动盈亏)
                    → PositionTracker.close_position() (平仓)
                        → DB trades 表 (交易流水)
"""

import logging
from typing import Any, Optional

from .db import Database

logger = logging.getLogger(__name__)


class PositionTracker:
    """Paper Trading 持仓追踪器。

    管理期货/期权信号的持仓生命周期：建仓、平仓、盈亏计算。
    所有数据存储在 SQLite 的 positions + trades 两张表中。

    Attributes:
        db: Database 实例（从 core.db 导入的长连接工厂）。
    """

    def __init__(self, db: Database) -> None:
        """初始化 PositionTracker。

        Args:
            db: Database 实例，需已调用过 init_all_tables() 确保表存在。
        """
        self.db = db

    # ════════════════════════════════════════════════════════════
    # 建仓
    # ════════════════════════════════════════════════════════════

    def open_position(
        self,
        symbol: str,
        contract: str,
        direction: str,
        entry_price: float,
        entry_time: int,
        signal_id: int = 0,
        signal_type: str = "futures",
        quantity: int = 1,
        stop_loss: float = 0,
        take_profit: float = 0,
    ) -> Optional[int]:
        """根据信号创建一笔新的 Paper Trading 持仓。

        Args:
            symbol: 品种代码，如 'SC'。
            contract: 合约代码，如 'SC2607'。
            direction: 方向，'LONG' 或 'SHORT'。
            entry_price: 入场价格。
            entry_time: 入场时间（Unix 秒）。
            signal_id: 关联的信号 ID。
            signal_type: 信号类型，'futures' 或 'options'。
            quantity: 手数，默认 1。
            stop_loss: 止损价，默认 0（未设置）。
            take_profit: 止盈价，默认 0（未设置）。

        Returns:
            新建持仓的 ID；如果重复建仓则返回 None。
        """
        # 去重检查：同一 contract + direction + status='open' 不能重复建仓
        dup = self._find_open_position(contract, direction)
        if dup is not None:
            logger.warning("持仓已存在: %s %s (position_id=%s), 跳过重复建仓",
                           contract, direction, dup["id"])
            return None

        conn = self.db.get_conn()
        cursor = conn.execute(
            """
            INSERT INTO positions
                (symbol, contract, direction, entry_price, entry_time,
                 quantity, signal_id, signal_type, stop_loss, take_profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (symbol, contract, direction, entry_price, entry_time,
             quantity, signal_id, signal_type, stop_loss, take_profit),
        )
        conn.commit()
        position_id = cursor.lastrowid
        logger.info("新建持仓 #%d: %s %s @ %.2f (signal_id=%d)",
                     position_id, contract, direction, entry_price, signal_id)

        # 同时写入 trade 流水
        self._record_trade(position_id, "open", entry_price, entry_time, "signal_entry")
        return position_id

    # ════════════════════════════════════════════════════════════
    # 平仓
    # ════════════════════════════════════════════════════════════

    def close_position(
        self,
        position_id: int,
        close_price: float,
        close_time: int,
        reason: str = "manual",
    ) -> bool:
        """平仓：关闭持仓并记录交易流水。

        Args:
            position_id: 持仓 ID。
            close_price: 平仓价格。
            close_time: 平仓时间（Unix 秒）。
            reason: 平仓原因，可选值:
                - 'stop_loss' — 止损
                - 'take_profit' — 止盈
                - 'signal_expired' — 信号消失
                - 'manual' — 手动平仓

        Returns:
            True 平仓成功，False 持仓不存在或已平仓。
        """
        position = self._get_position_by_id(position_id)
        if position is None:
            logger.warning("持仓 #%d 不存在", position_id)
            return False
        if position["status"] == "closed":
            logger.warning("持仓 #%d 已平仓", position_id)
            return False

        # 计算 PnL
        pnl = self._calculate_pnl(
            position["direction"],
            position["entry_price"],
            close_price,
            position["quantity"],
        )

        conn = self.db.get_conn()
        conn.execute(
            """
            UPDATE positions
            SET status='closed', current_price=?, closed_at=datetime('now'),
                updated_at=datetime('now')
            WHERE id=?
            """,
            (close_price, position_id),
        )
        conn.commit()

        # 记录平仓流水
        self._record_trade(position_id, "close", close_price, close_time, reason, pnl)
        logger.info("平仓 #%d: %s %s, PnL=%.2f, 原因=%s",
                     position_id, position["contract"], position["direction"],
                     pnl, reason)
        return True

    # ════════════════════════════════════════════════════════════
    # 查询
    # ════════════════════════════════════════════════════════════

    def get_open_positions(self) -> list[dict[str, Any]]:
        """获取所有当前持仓（status='open'）。

        Returns:
            持仓字典列表，按 entry_time 降序。
        """
        conn = self.db.get_conn()
        rows = conn.execute(
            """
            SELECT p.*, COALESCE(
                (SELECT SUM(t.pnl) FROM trades t WHERE t.position_id = p.id AND t.action = 'close'),
                0
            ) AS realized_pnl
            FROM positions p
            WHERE p.status = 'open'
            ORDER BY p.entry_time DESC
            """,
        ).fetchall()
        return [dict(r) for r in rows]

    def get_closed_positions(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """获取历史平仓记录（status='closed'）。

        Args:
            limit: 返回条数上限。
            offset: 分页偏移量。

        Returns:
            平仓记录列表，按 closed_at 降序。
        """
        conn = self.db.get_conn()
        rows = conn.execute(
            """
            SELECT p.*,
              COALESCE(
                (SELECT SUM(t.pnl) FROM trades t WHERE t.position_id = p.id AND t.action = 'close'),
                0
              ) AS realized_pnl,
              COALESCE(
                (SELECT t.reason FROM trades t WHERE t.position_id = p.id AND t.action = 'close' LIMIT 1),
                ''
              ) AS close_reason
            FROM positions p
            WHERE p.status = 'closed'
            ORDER BY p.updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_position_by_signal(self, signal_id: int) -> Optional[dict[str, Any]]:
        """根据信号 ID 查询已建仓的持仓。

        Args:
            signal_id: 信号 ID。

        Returns:
            持仓字典，或 None。
        """
        conn = self.db.get_conn()
        row = conn.execute(
            "SELECT * FROM positions WHERE signal_id = ? ORDER BY id DESC LIMIT 1",
            (signal_id,),
        ).fetchone()
        return dict(row) if row else None

    # ════════════════════════════════════════════════════════════
    # 盈亏更新
    # ════════════════════════════════════════════════════════════

    def update_pnl(self, position_id: int, current_price: float) -> float:
        """更新指定持仓的浮动盈亏。

        Args:
            position_id: 持仓 ID。
            current_price: 当前最新价。

        Returns:
            当前浮动盈亏金额。
        """
        position = self._get_position_by_id(position_id)
        if position is None:
            return 0.0

        pnl = self._calculate_pnl(
            position["direction"],
            position["entry_price"],
            current_price,
            position["quantity"],
        )

        conn = self.db.get_conn()
        conn.execute(
            "UPDATE positions SET current_price=?, updated_at=datetime('now') WHERE id=?",
            (current_price, position_id),
        )
        conn.commit()
        return pnl

    def batch_update_pnl(
        self,
        price_map: dict[str, float],
    ) -> list[dict[str, Any]]:
        """批量更新所有持仓的浮动盈亏。

        Args:
            price_map: {contract: current_price} 映射。

        Returns:
            更新后的 open positions 列表（含 pnl 字段）。
        """
        positions = self.get_open_positions()
        for pos in positions:
            price = price_map.get(pos["contract"])
            if price is not None:
                pos["unrealized_pnl"] = self.update_pnl(pos["id"], price)
            else:
                pos["unrealized_pnl"] = 0.0
        return positions

    # ════════════════════════════════════════════════════════════
    # 统计
    # ════════════════════════════════════════════════════════════

    def get_stats(self) -> dict[str, Any]:
        """获取 Paper Trading 综合统计。

        Returns:
            统计字典:
                - total_positions: 总持仓数
                - open_positions: 当前持仓数
                - closed_positions: 已平仓数
                - wins: 盈利笔数
                - losses: 亏损笔数
                - win_rate: 胜率
                - total_pnl: 总盈亏
                - max_drawdown: 最大回撤（简化版）
        """
        conn = self.db.get_conn()

        # 总数
        total = conn.execute("SELECT COUNT(*) FROM positions").fetchone()[0]
        open_count = conn.execute(
            "SELECT COUNT(*) FROM positions WHERE status='open'"
        ).fetchone()[0]
        closed_count = total - open_count

        # 已平仓盈亏统计
        close_trades = conn.execute(
            """
            SELECT t.pnl FROM trades t
            JOIN positions p ON p.id = t.position_id
            WHERE t.action = 'close'
            """
        ).fetchall()
        total_pnl = sum(r["pnl"] for r in close_trades) if close_trades else 0.0
        wins = sum(1 for r in close_trades if r["pnl"] > 0)
        losses = sum(1 for r in close_trades if r["pnl"] <= 0)
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0.0

        return {
            "total_positions": total,
            "open_positions": open_count,
            "closed_positions": closed_count,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 4),
            "total_pnl": round(total_pnl, 2),
        }

    # ════════════════════════════════════════════════════════════
    # 内部工具方法
    # ════════════════════════════════════════════════════════════

    def _find_open_position(
        self,
        contract: str,
        direction: str,
    ) -> Optional[dict[str, Any]]:
        """查找同一合约 + 方向的未平仓持仓（用于去重）。"""
        conn = self.db.get_conn()
        row = conn.execute(
            "SELECT * FROM positions WHERE contract=? AND direction=? AND status='open' LIMIT 1",
            (contract, direction),
        ).fetchone()
        return dict(row) if row else None

    def _get_position_by_id(self, position_id: int) -> Optional[dict[str, Any]]:
        """根据 ID 查询持仓。"""
        conn = self.db.get_conn()
        row = conn.execute(
            "SELECT * FROM positions WHERE id=?", (position_id,)
        ).fetchone()
        return dict(row) if row else None

    def _record_trade(
        self,
        position_id: int,
        action: str,
        price: float,
        time: int,
        reason: str = "",
        pnl: float = 0,
    ) -> int:
        """记录一笔交易流水。"""
        conn = self.db.get_conn()
        cursor = conn.execute(
            "INSERT INTO trades (position_id, action, price, time, reason, pnl) VALUES (?, ?, ?, ?, ?, ?)",
            (position_id, action, price, time, reason, pnl),
        )
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def _calculate_pnl(
        direction: str,
        entry_price: float,
        current_price: float,
        quantity: int,
    ) -> float:
        """计算盈亏金额。

        LONG: (current - entry) * quantity
        SHORT: (entry - current) * quantity
        """
        if direction == "LONG":
            return round((current_price - entry_price) * quantity, 2)
        else:
            return round((entry_price - current_price) * quantity, 2)
