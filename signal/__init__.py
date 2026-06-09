"""
信号中心模块 — 统一信号管理、消息格式化与分级推送调度。

导出:
    SignalHub: 统一信号中心（存储、去重、查询）
    UnifiedFormatter: 统一消息格式化器
    dispatch: 分级推送调度函数
"""

from signal.hub import SignalHub
from signal.formatter import UnifiedFormatter
from signal.dispatcher import dispatch

__all__ = [
    "SignalHub",
    "UnifiedFormatter",
    "dispatch",
]
