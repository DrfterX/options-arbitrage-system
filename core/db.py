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


class Database:
    """数据库连接工厂。

    封装 SQLite 连接创建、WAL 模式开启、外键约束启用，
    以及表初始化等操作。

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

    def get_conn(self) -> sqlite3.Connection:
        """获取数据库连接。

        每次调用返回新连接，已配置：
        - ``row_factory = sqlite3.Row``（返回 dict-like 对象）
        - ``PRAGMA journal_mode=WAL``（写前日志模式）
        - ``PRAGMA foreign_keys=ON``（外键约束）

        Returns:
            配置好的 sqlite3.Connection 对象。
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

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
