"""
信号中心模块 — 统一信号管理、消息格式化与分级推送调度。

导出:
    SignalHub: 统一信号中心（存储、去重、查询）
    UnifiedFormatter: 统一消息格式化器
    dispatch: 分级推送调度函数
    telegram_notifier: Telegram 推送模块
"""

from signals.hub import SignalHub
from signals.formatter import UnifiedFormatter
from signals.dispatcher import dispatch
from signals.telegram_notifier import send_message, send_signal, send_daily_summary

__all__ = [
    "SignalHub",
    "UnifiedFormatter",
    "dispatch",
    "send_message",
    "send_signal",
    "send_daily_summary",
]
