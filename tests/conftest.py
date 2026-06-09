"""共享fixture和路径配置。"""

import sys
import os
from pathlib import Path

# 确保项目根目录可导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import MagicMock

from core.db import Database
from core.schema import ALL_TABLES, INDEXES

# ─── 通用时间戳常量 ───
T1, T2, T3, T4, T5, T6 = 1000, 2000, 3000, 4000, 5000, 6000


# ─── 辅助函数：构造极值点 ───
def make_swing(point_type: str, price: float, ts: int) -> dict:
    """构造一个 swing_point 字典。

    Args:
        point_type: 极值类型 PEAK / TROUGH。
        price: 价格。
        ts: 时间戳。

    Returns:
        极值点字典。
    """
    return {"point_type": point_type, "price": price, "timestamp": ts}


def make_macd_row(timestamp: int, color: str, histogram: float = None) -> dict:
    """构造一个 MACD 行字典。

    Args:
        timestamp: 时间戳。
        color: RED 或 BLUE。
        histogram: histogram 值。

    Returns:
        MACD 行字典。
    """
    row: dict = {"timestamp": timestamp, "color": color}
    if histogram is not None:
        row["histogram"] = histogram
    return row


def make_kline(timestamp: int, close: float, open_: float = None,
               high: float = None, low: float = None) -> dict:
    """构造一个 K线 字典。

    Args:
        timestamp: 时间戳。
        close: 收盘价。
        open_: 开盘价（默认等于收盘价）。
        high: 最高价（默认等于收盘价）。
        low: 最低价（默认等于收盘价）。

    Returns:
        K线字典。
    """
    return {
        "timestamp": timestamp,
        "open": open_ or close,
        "high": high or close,
        "low": low or close,
        "close": close,
        "volume": 100,
    }


# ─── 标准N型结构 fixture ───
@pytest.fixture
def long_n_structure() -> dict:
    """正N型（做多）N型结构。"""
    return {
        "symbol": "RB",
        "contract": "rb2510",
        "timeframe": "1w",
        "direction": "LONG",
        "state": "LEG3",
        "point_a_time": T1,
        "point_a_price": 90.0,
        "point_b_time": T2,
        "point_b_price": 110.0,
        "point_c_time": T3,
        "point_c_price": 95.0,
    }


@pytest.fixture
def short_n_structure() -> dict:
    """倒N型（做空）N型结构。"""
    return {
        "symbol": "RB",
        "contract": "rb2510",
        "timeframe": "1w",
        "direction": "SHORT",
        "state": "LEG3",
        "point_a_time": T1,
        "point_a_price": 110.0,
        "point_b_time": T2,
        "point_b_price": 90.0,
        "point_c_time": T3,
        "point_c_price": 105.0,
    }


@pytest.fixture
def temp_db() -> Database:
    """创建临时内存数据库。

    Returns:
        已初始化所有表和索引的 Database 实例。
    """
    db = Database(":memory:")
    with db.get_conn() as conn:
        for sql in ALL_TABLES.values():
            conn.execute(sql)
        for sql in INDEXES:
            conn.execute(sql)
        conn.commit()
    return db


@pytest.fixture
def registry(temp_db: Database):
    """创建含62品种的 ContractRegistry（内存DB）。"""
    from config.contracts import ContractRegistry, DEFAULT_SYMBOLS

    reg = ContractRegistry(":memory:")
    # seed默认品种到内存DB
    with temp_db.get_conn() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO symbols "
            "(symbol, name, option_name, exchange, category, multiplier, has_options, is_night) "
            "VALUES (?,?,?,?,?,?,?,?)",
            DEFAULT_SYMBOLS,
        )
        conn.commit()
    return reg
