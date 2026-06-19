"""
Bot 多用户订阅管理模块。

管理 Telegram Bot 用户的订阅生命周期：
- subscribe / unsubscribe
- 订阅状态追踪（trial / active / expired）
- 用户偏好设置（哪些品种/等级的信号）
- 批量获取活跃订阅者用于定时推送

依赖 ``core.db.Database`` 获取数据库连接。

用法::

    from signals.bot_subscription import BotSubscription

    mgr = BotSubscription(db)
    mgr.subscribe(chat_id="12345", username="trader1")
    mgr.unsubscribe(chat_id="12345")
    subs = mgr.get_active_subscribers()
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from core.db import Database

logger = logging.getLogger(__name__)

# 免费试用天数
_TRIAL_DAYS = 7


class BotSubscription:
    """Bot 订阅管理器。

    封装 bot_subscribers 表的所有操作。
    通过 Database 获取连接，不自行管理连接生命周期。

    Attributes:
        db: Database 连接工厂实例。
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    # ── 订阅 / 取消 ──────────────────────────────────────────

    def subscribe(
        self,
        chat_id: str,
        username: str = "",
        first_name: str = "",
        preferences: Optional[dict] = None,
    ) -> bool:
        """注册新订阅用户（幂等）。

        如果 chat_id 已存在则更新状态为 trial（取消后的重新订阅）。
        新订阅默认获得 7 天免费试用。

        Args:
            chat_id: Telegram Chat ID。
            username: Telegram 用户名（可选）。
            first_name: Telegram 显示名（可选）。
            preferences: 用户偏好（JSON dict）。

        Returns:
            True 表示注册成功。
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        trial_end = (datetime.now(timezone.utc) + timedelta(days=_TRIAL_DAYS)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        prefs_json = json.dumps(preferences or {}, ensure_ascii=False)

        conn = self.db.get_conn()
        try:
            # 检查是否已存在
            existing = conn.execute(
                "SELECT id FROM bot_subscribers WHERE telegram_chat_id = ?",
                (chat_id,),
            ).fetchone()

            if existing:
                # 重新激活
                conn.execute(
                    """UPDATE bot_subscribers
                       SET status = 'trial',
                           telegram_username = ?,
                           first_name = ?,
                           trial_end_at = ?,
                           preferences = ?,
                           updated_at = ?
                       WHERE telegram_chat_id = ?""",
                    (username, first_name, trial_end, prefs_json, now, chat_id),
                )
                logger.info("订阅已重新激活: chat_id=%s", chat_id)
            else:
                # 新订阅
                conn.execute(
                    """INSERT INTO bot_subscribers
                       (telegram_chat_id, telegram_username, first_name,
                        status, subscribed_at, trial_end_at, preferences)
                       VALUES (?, ?, ?, 'trial', ?, ?, ?)""",
                    (chat_id, username, first_name, now, trial_end, prefs_json),
                )
                logger.info("新订阅: chat_id=%s username=%s trial_end=%s",
                            chat_id, username, trial_end)

            conn.commit()
            return True
        except Exception as e:
            logger.error("订阅失败 chat_id=%s: %s", chat_id, e)
            return False

    def unsubscribe(self, chat_id: str) -> bool:
        """取消订阅。

        Args:
            chat_id: Telegram Chat ID。

        Returns:
            True 表示操作成功（无论用户是否存在）。
        """
        conn = self.db.get_conn()
        try:
            conn.execute(
                """UPDATE bot_subscribers
                   SET status = 'cancelled', updated_at = datetime('now')
                   WHERE telegram_chat_id = ?""",
                (chat_id,),
            )
            conn.commit()
            logger.info("已取消订阅: chat_id=%s", chat_id)
            return True
        except Exception as e:
            logger.error("取消订阅失败 chat_id=%s: %s", chat_id, e)
            return False

    # ── 查询 ──────────────────────────────────────────────────

    def get_subscriber(self, chat_id: str) -> Optional[dict]:
        """获取单个订阅者信息。

        Args:
            chat_id: Telegram Chat ID。

        Returns:
            订阅者字典（含所有字段），或 None（不存在）。
        """
        conn = self.db.get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM bot_subscribers WHERE telegram_chat_id = ?",
                (chat_id,),
            ).fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error("查询订阅者失败 chat_id=%s: %s", chat_id, e)
            return None

    def get_active_subscribers(self) -> list[dict]:
        """获取所有活跃订阅者（status 为 trial 或 active）。

        自动排除已过期 trial 的订阅者。

        Returns:
            活跃订阅者字典列表。
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn = self.db.get_conn()
        try:
            rows = conn.execute(
                """SELECT * FROM bot_subscribers
                   WHERE status IN ('trial', 'active')
                     AND (trial_end_at = '' OR trial_end_at >= ?)
                   ORDER BY subscribed_at ASC""",
                (now,),
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error("查询活跃订阅者失败: %s", e)
            return []

    def get_all_subscribers(self) -> list[dict]:
        """获取所有订阅者（含已取消）。

        Returns:
            所有订阅者字典列表。
        """
        conn = self.db.get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM bot_subscribers ORDER BY subscribed_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error("查询全部订阅者失败: %s", e)
            return []

    def count_active(self) -> int:
        """统计活跃订阅者数量。

        Returns:
            活跃订阅者数量。
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn = self.db.get_conn()
        try:
            row = conn.execute(
                """SELECT COUNT(*) as cnt FROM bot_subscribers
                   WHERE status IN ('trial', 'active')
                     AND (trial_end_at = '' OR trial_end_at >= ?)""",
                (now,),
            ).fetchone()
            return row["cnt"] if row else 0
        except Exception as e:
            logger.error("统计活跃订阅者失败: %s", e)
            return 0

    # ── 状态管理 ──────────────────────────────────────────────

    def expire_trials(self) -> int:
        """将所有过期的 trial 标记为 expired。

        Returns:
            被过期处理的订阅者数量。
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn = self.db.get_conn()
        try:
            cur = conn.execute(
                """UPDATE bot_subscribers
                   SET status = 'expired', updated_at = ?
                   WHERE status = 'trial'
                     AND trial_end_at != ''
                     AND trial_end_at < ?""",
                (now, now),
            )
            conn.commit()
            count: int = cur.rowcount
            if count:
                logger.info("过期 trial 用户: %d 个", count)
            return count
        except Exception as e:
            logger.error("过期 trial 处理失败: %s", e)
            return 0

    def upgrade_to_active(self, chat_id: str) -> bool:
        """将用户从 trial 升级为 active（付费后调用）。

        Args:
            chat_id: Telegram Chat ID。

        Returns:
            True 表示升级成功。
        """
        conn = self.db.get_conn()
        try:
            conn.execute(
                """UPDATE bot_subscribers
                   SET status = 'active', expires_at = ?,
                       updated_at = datetime('now')
                   WHERE telegram_chat_id = ?""",
                # 付费用户默认 30 天有效期
                ((datetime.now(timezone.utc) + timedelta(days=30)).strftime(
                    "%Y-%m-%d %H:%M:%S"), chat_id),
            )
            conn.commit()
            logger.info("用户升级为 active: chat_id=%s", chat_id)
            return True
        except Exception as e:
            logger.error("升级失败 chat_id=%s: %s", chat_id, e)
            return False

    # ── 推送统计 ──────────────────────────────────────────────

    def record_push(self, chat_id: str) -> bool:
        """记录一次推送（递增信号计数 + 更新时间戳）。

        Args:
            chat_id: Telegram Chat ID。

        Returns:
            True 表示记录成功。
        """
        conn = self.db.get_conn()
        try:
            conn.execute(
                """UPDATE bot_subscribers
                   SET signals_pushed = signals_pushed + 1,
                       last_pushed_at = datetime('now'),
                       updated_at = datetime('now')
                   WHERE telegram_chat_id = ?""",
                (chat_id,),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error("记录推送失败 chat_id=%s: %s", chat_id, e)
            return False

    # ── 偏好设置 ──────────────────────────────────────────────

    def set_preferences(self, chat_id: str, preferences: dict) -> bool:
        """更新用户推送偏好。

        Args:
            chat_id: Telegram Chat ID。
            preferences: 偏好字典，例如:
                {"symbols": ["RB", "RU"], "max_daily": 3, "levels": ["ENTRY", "CANDIDATE"]}

        Returns:
            True 表示更新成功。
        """
        prefs_json = json.dumps(preferences, ensure_ascii=False)
        conn = self.db.get_conn()
        try:
            conn.execute(
                """UPDATE bot_subscribers
                   SET preferences = ?, updated_at = datetime('now')
                   WHERE telegram_chat_id = ?""",
                (prefs_json, chat_id),
            )
            conn.commit()
            logger.info("偏好已更新: chat_id=%s prefs=%s", chat_id, prefs_json)
            return True
        except Exception as e:
            logger.error("更新偏好失败 chat_id=%s: %s", chat_id, e)
            return False

    def get_preferences(self, chat_id: str) -> dict:
        """获取用户推送偏好。

        Args:
            chat_id: Telegram Chat ID。

        Returns:
            偏好字典（空 dict 表示无偏好 / 用户不存在）。
        """
        sub = self.get_subscriber(chat_id)
        if sub and sub.get("preferences"):
            try:
                return json.loads(sub["preferences"])
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
