"""
统一日志配置。

输出到 stdout + 文件，由其他模块通过 ``logging.getLogger(__name__)`` 使用。
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_file: Path, level: str = "INFO") -> None:
    """配置全局日志格式与输出目标。

    所有日志同时输出到 stdout（供 cron 管道捕获）和指定的日志文件。
    UTF-8 编码确保中文品种名称正常显示。

    Args:
        log_file: 日志文件路径（Path 对象）。
        level: 日志级别字符串，如 "DEBUG"、"INFO"、"WARNING"。
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file), encoding="utf-8"),
        ],
    )
