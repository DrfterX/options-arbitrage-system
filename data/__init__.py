"""
数据层 — 采集+存储+IV记录。

提供期货K线采集、期权链采集、IV历史记录三大模块。
由于 pandas/numpy dylib 签名冲突，使用懒加载导入。
"""

from .iv_recorder import IVRecorder

# FuturesCollector 和 OptionsCollector 依赖 numpy/pandas，
# 在 web/app.py 等场景通过 from data.iv_recorder import IVRecorder 直接导入，
# 不会触发自动导入链。
_futures_collector = None
_options_collector = None


def get_futures_collector(db, registry):
    global _futures_collector
    if _futures_collector is None:
        from .futures_collector import FuturesCollector
        _futures_collector = FuturesCollector(db, registry)
    return _futures_collector


def get_options_collector(registry):
    global _options_collector
    if _options_collector is None:
        from .options_collector import OptionsCollector
        _options_collector = OptionsCollector(registry)
    return _options_collector


__all__ = [
    "IVRecorder",
    "get_futures_collector",
    "get_options_collector",
]
