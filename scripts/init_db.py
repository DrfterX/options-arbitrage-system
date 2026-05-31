#!/usr/bin/env python3
"""初始化数据库：创建表 + 注册 60 品种。

用法::

    python scripts/init_db.py

功能:
    1. 创建 trading_system.db 中的 10 张表及索引
    2. 向 symbols 表写入 60 个默认品种
    3. 输出验证信息（总数、有期权品种数）

幂等：重复运行不会产生重复数据。
"""

import sys
import logging
from pathlib import Path

# 将项目根目录加入 sys.path，确保可 import config / core
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.logging_config import setup_logging
from config.settings import DB_PATH, LOG_PATH, LOG_LEVEL
from config.contracts import ContractRegistry
from core.db import Database

logger = logging.getLogger(__name__)


def main() -> None:
    """主入口：初始化数据库表结构并注册品种。"""
    setup_logging(LOG_PATH, LOG_LEVEL)

    # 1. 创建表
    logger.info("初始化数据库...")
    db = Database(DB_PATH)
    db.init_all_tables()
    logger.info("10 张表创建完成")

    # 2. 注册品种
    logger.info("注册品种母表...")
    registry = ContractRegistry(str(DB_PATH))
    count = registry.refresh_from_akshare()
    logger.info("品种注册完成: %d 个品种", count)

    # 3. 验证
    all_sym = registry.get_all()
    with_options = registry.get_with_options()
    logger.info("总品种: %d", len(all_sym))
    logger.info("有期权品种: %d", len(with_options))

    # 打印摘要
    print(f"\n{'='*50}")
    print(f"数据库初始化完成")
    print(f"{'='*50}")
    print(f"DB 路径: {DB_PATH}")
    print(f"品种总数: {len(all_sym)}")
    print(f"有期权品种: {len(with_options)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
