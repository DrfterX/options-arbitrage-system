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
from config.contracts import ContractRegistry

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
        self.registry = ContractRegistry(str(db.db_path))
        self._multiplier_cache: dict[str, int] = {}
        self._ensure_migration()

    def _ensure_migration(self) -> None:
        """确保数据库 schema 已迁至最新版本。

        当前迁移:
          1. positions 表添加 remaining_quantity 列（部分平仓支持）。
          2. positions 表添加 unrealized_pnl 列（持久化浮动盈亏）。
        """
        conn = self.db.get_conn()
        try:
            cols = [r["name"] for r in conn.execute("PRAGMA table_info(positions)").fetchall()]

            # 迁移 1: remaining_quantity 列
            if "remaining_quantity" not in cols:
                logger.info("DB迁移: positions 表添加 remaining_quantity 列")
                conn.execute(
                    "ALTER TABLE positions ADD COLUMN remaining_quantity "
                    "INTEGER DEFAULT 0"
                )
                # 已有 open 持仓的 remaining_quantity = quantity
                conn.execute(
                    "UPDATE positions SET remaining_quantity = quantity "
                    "WHERE remaining_quantity IS NULL OR remaining_quantity = 0"
                )
                conn.commit()
                logger.info("DB迁移完成: remaining_quantity 列已添加并初始化")

            # 迁移 2: unrealized_pnl 列
            if "unrealized_pnl" not in cols:
                logger.info("DB迁移: positions 表添加 unrealized_pnl 列")
                conn.execute(
                    "ALTER TABLE positions ADD COLUMN unrealized_pnl "
                    "REAL DEFAULT 0"
                )
                # 初始化已有 open 持仓的 unrealized_pnl
                for pos in conn.execute(
                    "SELECT id, direction, entry_price, current_price, "
                    "       quantity, remaining_quantity, signal_type, symbol "
                    "FROM positions WHERE status='open' AND current_price > 0"
                ).fetchall():
                    pos = dict(pos)
                    act_qty = pos.get("remaining_quantity", pos["quantity"]) or pos["quantity"]
                    multiplier = self._get_multiplier(pos["symbol"], pos.get("signal_type", "futures"))
                    pnl = self._calculate_pnl(
                        pos["direction"], pos["entry_price"],
                        pos["current_price"], act_qty, multiplier,
                    )
                    conn.execute(
                        "UPDATE positions SET unrealized_pnl=? WHERE id=?",
                        (pnl, pos["id"]),
                    )
                conn.commit()
                logger.info("DB迁移完成: unrealized_pnl 列已添加并初始化")
        except Exception as e:
            logger.warning("DB迁移异常(可忽略): %s", e)
            conn.rollback()

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
        signal_id: Optional[int] = None,
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
            signal_id: 关联的信号 ID（None 表示手动建仓）。
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
        try:
            cursor = conn.execute(
                """
                INSERT INTO positions
                    (symbol, contract, direction, entry_price, entry_time,
                     quantity, remaining_quantity, signal_id, signal_type,
                     stop_loss, take_profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (symbol, contract, direction, entry_price, entry_time,
                 quantity, quantity, signal_id, signal_type, stop_loss, take_profit),
            )
            position_id = cursor.lastrowid

            # 同一事务内写入 trade 流水
            self._record_trade(position_id, "open", entry_price, entry_time, "signal_entry")
            conn.commit()
        except Exception:
            conn.rollback()
            logger.error("建仓失败: %s %s @ %.2f, 已回滚", contract, direction, entry_price)
            raise

        logger.info("新建持仓 #%d: %s %s @ %.2f (signal_id=%d, remaining=%d)",
                     position_id, contract, direction, entry_price, signal_id, quantity)
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
        partial_quantity: Optional[int] = None,
    ) -> bool:
        """平仓：关闭持仓（或部分平仓）并记录交易流水。

        Args:
            position_id: 持仓 ID。
            close_price: 平仓价格。
            close_time: 平仓时间（Unix 秒）。
            reason: 平仓原因，可选值:
                - 'stop_loss' — 止损
                - 'take_profit' — 止盈
                - 'signal_expired' — 信号消失
                - 'manual' — 手动平仓
            partial_quantity: 部分平仓手数。None 或 >= remaining_quantity 时为全量平仓。

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

        remaining = position.get("remaining_quantity", position["quantity"])
        qty_to_close = remaining if partial_quantity is None else min(partial_quantity, remaining)

        # 计算 PnL（使用实际平仓手数）
        multiplier = self._get_multiplier(position["symbol"], position.get("signal_type", "futures"))
        pnl = self._calculate_pnl(
            position["direction"],
            position["entry_price"],
            close_price,
            qty_to_close,
            multiplier,
        )

        conn = self.db.get_conn()
        try:
            new_remaining = remaining - qty_to_close
            if new_remaining <= 0:
                # 全量平仓
                conn.execute(
                    """
                    UPDATE positions
                    SET status='closed', current_price=?, remaining_quantity=0,
                        closed_at=datetime('now'), updated_at=datetime('now')
                    WHERE id=?
                    """,
                    (close_price, position_id),
                )
                logger.info("全量平仓 #%d: %s %s, qty=%d, PnL=%.2f, 原因=%s",
                             position_id, position["contract"], position["direction"],
                             qty_to_close, pnl, reason)
            else:
                # 部分平仓：减少 remaining_quantity，保持 status='open'
                conn.execute(
                    """
                    UPDATE positions
                    SET current_price=?, remaining_quantity=?,
                        updated_at=datetime('now')
                    WHERE id=?
                    """,
                    (close_price, new_remaining, position_id),
                )
                logger.info("部分平仓 #%d: %s %s, qty=%d/%d, PnL=%.2f, 原因=%s",
                             position_id, position["contract"], position["direction"],
                             qty_to_close, qty_to_close + new_remaining, pnl, reason)

            # 同一事务内记录平仓流水
            self._record_trade(position_id, "close", close_price, close_time, reason, pnl)
            conn.commit()
        except Exception:
            conn.rollback()
            logger.error("平仓失败 #%d: %s %s, 已回滚",
                         position_id, position["contract"], position["direction"])
            raise
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
        positions = [dict(r) for r in rows]
        # 使用 DB 存储的 unrealized_pnl，旧记录（值为 0）则实时计算
        for pos in positions:
            # remaining_quantity 兜底：旧数据可能为 0 → 用 quantity
            act_qty = pos.get("remaining_quantity", pos["quantity"]) or pos["quantity"]
            pos["remaining_quantity"] = act_qty
            stored_pnl = pos.get("unrealized_pnl", 0) or 0
            if stored_pnl != 0:
                pos["unrealized_pnl"] = stored_pnl
            elif pos.get("current_price") and pos["current_price"] > 0:
                multiplier = self._get_multiplier(pos["symbol"], pos.get("signal_type", "futures"))
                pos["unrealized_pnl"] = self._calculate_pnl(
                    pos["direction"], pos["entry_price"],
                    pos["current_price"], act_qty, multiplier,
                )
            else:
                pos["unrealized_pnl"] = 0.0
        return positions

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

    def get_position_by_signal(self, signal_id: Optional[int] = None) -> Optional[dict[str, Any]]:
        """根据信号 ID 查询已建仓的持仓。

        Args:
            signal_id: 信号 ID。None 或 0 时返回 None（手动建仓无关联信号）。

        Returns:
            持仓字典，或 None。
        """
        if not signal_id:
            return None
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

        # 使用 remaining_quantity 计算浮动盈亏（部分平仓后剩余仓位）
        act_qty = position.get("remaining_quantity", position["quantity"]) or position["quantity"]
        multiplier = self._get_multiplier(position["symbol"], position.get("signal_type", "futures"))
        pnl = self._calculate_pnl(
            position["direction"],
            position["entry_price"],
            current_price,
            act_qty,
            multiplier,
        )

        conn = self.db.get_conn()
        conn.execute(
            "UPDATE positions SET current_price=?, unrealized_pnl=?, "
            "updated_at=datetime('now') WHERE id=?",
            (current_price, pnl, position_id),
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
                pos["unrealized_pnl"] = None
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

    def _get_multiplier(self, symbol: str, signal_type: str = "futures") -> int:
        """获取合约乘数。

        期货：从 ContractRegistry 查询品种的合约乘数。
        期权：期权 PnL 基于净权利金（净值），合约乘数 = 1。

        Args:
            symbol: 品种代码。
            signal_type: 信号类型，'futures' 或 'options'。

        Returns:
            合约乘数。期权始终返回 1。
        """
        if signal_type == "options":
            return 1
        if symbol not in self._multiplier_cache:
            try:
                self._multiplier_cache[symbol] = self.registry.get_multiplier(symbol)
            except Exception:
                logger.warning("查询合约乘数失败 %s, 使用默认值 1", symbol)
                self._multiplier_cache[symbol] = 1
        return self._multiplier_cache[symbol]

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
        """记录一笔交易流水。

        注意：此方法**不执行 conn.commit()**，由调用方（open_position / close_position）
        在原子事务的 try 块中统一 commit。切勿在此处添加独立 commit，否则会破坏事务原子性。
        """
        conn = self.db.get_conn()
        cursor = conn.execute(
            "INSERT INTO trades (position_id, action, price, time, reason, pnl) VALUES (?, ?, ?, ?, ?, ?)",
            (position_id, action, price, time, reason, pnl),
        )
        return cursor.lastrowid

    @staticmethod
    def _calculate_pnl(
        direction: str,
        entry_price: float,
        current_price: float,
        quantity: int,
        multiplier: int = 1,
    ) -> float:
        """计算盈亏金额。

        LONG: (current - entry) * quantity * multiplier
        SHORT: (entry - current) * quantity * multiplier

        期货盈亏 = 价格差 × 手数 × 合约乘数
        期权盈亏 = 净值差 × 手数（合约乘数 = 1，因 net_cost 已是货币金额）
        """
        if direction == "LONG":
            return round((current_price - entry_price) * quantity * multiplier, 2)
        else:
            return round((entry_price - current_price) * quantity * multiplier, 2)
