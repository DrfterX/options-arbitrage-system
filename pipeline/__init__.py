"""
管线程调度模块 — 统一信号扫描与推送管线。

导出:
    Orchestrator: 统一调度器（期货+期权扫描合并管线）
    main: argparse 入口函数
"""

from pipeline.orchestrator import Orchestrator, main

__all__ = [
    "Orchestrator",
    "main",
]
