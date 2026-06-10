"""
数据库连接工厂 Database。

提供统一的 SQLite 连接获取、表初始化与迁移入口。
所有模块通过此工厂获取连接，避免分散创建连接。
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional

from .schema import ALL_TABLES, INDEXES

logger = logging.getLogger(__name__)

# ============================================================
# 连接缓存
#
# 根因：unable to open database file 不是锁竞争（SQLITE_BUSY），
# 而是 macOS WAL 模式下快速 open/close 连接 WAL checkpoint 竞争
# 导致的 SQLITE_CANTOPEN。data_refresh() 中 200+ 次短连接反复
# connect/disconnect 触发此 bug。busy_timeout/timeout 只解决
# 锁竞争，对此无效。
#
# 修复：Database 实例持有单一长连接，所有调用复用该连接，
# 避免重复 connect/disconnect。
#
# 原理：
# - sqlite3.Connection.__exit__ 只做 commit/rollback，不 close
# - 系统是单线程串行执行，无并发安全顾虑
# - 提供显式的 close() 方法用于测试清理
# ============================================================


class Database:
    """数据库连接工厂。

    封装 SQLite 连接创建、WAL 模式开启、外键约束启用，
    以及表初始化等操作。内部维护一个长连接避免频繁 connect/disconnect
    导致的 macOS WAL 竞争（unable to open database file）。

    Attributes:
        db_path: 数据库文件路径字符串。
    """

    def __init__(self, db_path) -> None:
        """初始化数据库连接工厂。

        Args:
            db_path: SQLite 数据库文件路径（str 或 Path）。
        """
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    def get_conn(self, timeout: float = 30.0) -> sqlite3.Connection:
        """获取数据库连接。

        返回缓存的唯一连接（首次调用时创建），已配置：
        - ``row_factory = sqlite3.Row``（返回 dict-like 对象）
        - ``PRAGMA journal_mode=WAL``（写前日志模式）
        - ``PRAGMA foreign_keys=ON``（外键约束）
        - ``PRAGMA busy_timeout``（等待锁释放超时，默认 5 秒）

        Notes:
            sqlite3.Connection 被 ``with`` 上下文使用时，
            ``__exit__`` 只执行 commit/rollback，**不调用 close**。
            因此长连接在 `with` 退出后继续可用，无需拦截 close。

        Args:
            timeout: 连接超时秒数，默认 30 秒。

        Returns:
            配置好的 sqlite3.Connection 对象。
        """
        if self._conn is not None:
            return self._conn

        conn = sqlite3.connect(self.db_path, timeout=timeout)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")

        self._conn = conn
        logger.debug("数据库连接已创建: %s (缓存)", self.db_path)
        return conn

    def close(self) -> None:
        """关闭缓存的数据库连接（如有）。

        供测试 teardown 和应用退出时调用。
        `with get_conn()` 上下文不会触发此关闭。
        """
        if self._conn is not None:
            try:
                self._conn.commit()
                self._conn.close()
                logger.debug("数据库连接已关闭: %s", self.db_path)
            except Exception as e:
                logger.warning("关闭数据库连接异常: %s", e)
            finally:
                self._conn = None

    def init_all_tables(self) -> None:
        """创建所有表（如果不存在）并建立索引。

        幂等操作：重复调用不会破坏已有数据。
        遍历 ALL_TABLES 字典执行每条 CREATE TABLE 语句，
        然后执行 INDEXES 中的索引创建语句。
        """
        with self.get_conn() as conn:
            for table_name, create_sql in ALL_TABLES.items():
                conn.execute(create_sql)
                logger.debug("表 %s 已就绪", table_name)
            for index_sql in INDEXES:
                conn.execute(index_sql)
            conn.commit()
        logger.info("数据库初始化完成：%d 张表，%d 个索引",
                     len(ALL_TABLES), len(INDEXES))

    def migrate_from_old(self, old_db_path: str) -> dict:
        """从旧数据库迁移数据（预留接口）。

        Args:
            old_db_path: 旧数据库文件路径。

        Returns:
            迁移统计字典，包含各表迁移行数。
        """
        logger.warning("migrate_from_old 尚未实现，old_db_path=%s", old_db_path)
        return {"status": "not_implemented", "tables": {}}
