"""
core 包 — 数据库 + Schema + 品种注册 + 持仓追踪 + 风控引擎。

导出 Database 连接工厂、ALL_TABLES schema 定义、PositionTracker、PositionRiskManager。
"""

from .db import Database
from .position_tracker import PositionTracker
from .risk_manager import PositionRiskManager, RiskCheckTriggerResult
from .schema import ALL_TABLES
