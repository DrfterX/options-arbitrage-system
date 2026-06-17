"""验证：数据写入触发 N 型结构动态重算钩子。

覆盖两种写入路径：
1. ``collect_symbol`` 主写入路径（各时间周期有 saved > 0 时触发）
2. ``_collect_3m_from_1m`` 3m 聚合写入路径（聚合数据写入后触发）
3. ``saved == 0`` 时不触发（无新数据时不浪费计算）
"""

import sys
import os
from unittest.mock import patch, MagicMock, ANY

import pytest

# ── 确保能找到项目模块 ──────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.db import Database
from core.schema import ALL_TABLES, INDEXES
from data.futures_collector import FuturesCollector


# ── 固定测试参数 ────────────────────────────────────────────
SYMBOL = "RB"
CONTRACT = "RB2510"
NOW = 1_000_000_000


@pytest.fixture
def db():
    """内存数据库 + 完整表结构。"""
    _db = Database(":memory:")
    with _db.get_conn() as conn:
        for sql in ALL_TABLES.values():
            conn.execute(sql)
        for sql in INDEXES:
            conn.execute(sql)
        conn.commit()
    return _db


@pytest.fixture
def collector(db):
    """Mock registry + FuturesCollector 实例。"""
    registry = MagicMock()
    return FuturesCollector(db, registry)


# ═══════════════════════════════════════════════════════════
# 1. collect_symbol 主写入钩子
# ═══════════════════════════════════════════════════════════

class TestCollectSymbolHook:
    """验证 collect_symbol 中 saved > 0 时触发结构重算。"""

    @patch("data.futures_collector.fetch_klines")
    @patch("futures.n_structure.restructure_active_for_symbol")
    def test_triggers_restructure_when_data_saved(
        self,
        mock_restructure: MagicMock,
        mock_fetch: MagicMock,
        collector: FuturesCollector,
    ) -> None:
        """场景：首次采集（无存量）→ 所有 K 线均为新数据 → saved > 0 → 触发重算。"""
        # 模拟 AKShare 返回 3 条 K 线（15m 周期）
        mock_fetch.return_value = [
            {"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "15m",
             "timestamp": NOW, "open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000},
            {"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "15m",
             "timestamp": NOW + 900, "open": 103, "high": 108, "low": 102, "close": 107, "volume": 1200},
            {"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "15m",
             "timestamp": NOW + 1800, "open": 107, "high": 110, "low": 106, "close": 109, "volume": 800},
        ]

        result = collector.collect_symbol(SYMBOL, CONTRACT)

        # 验证重算被调用（至少对 15m 周期调用）
        mock_restructure.assert_any_call(SYMBOL, CONTRACT, collector.db)
        # 验证采集成功
        assert result["15m"]["saved"] == 3, "应保存 3 条新 K 线"
        assert result["15m"]["error"] is None, "不应有错误"

    @patch("data.futures_collector.fetch_klines")
    @patch("futures.n_structure.restructure_active_for_symbol")
    def test_does_not_trigger_when_no_new_data(
        self,
        mock_restructure: MagicMock,
        mock_fetch: MagicMock,
        collector: FuturesCollector,
    ) -> None:
        """场景：全部周期均有存量数据 + 新采集数据均不晚于存量 → saved == 0 → 不触发重算。"""
        # 为所有周期预填数据（三个周期：15m, 1h, 1d）
        for tf in ["15m", "1h", "1d"]:
            with collector.db.get_conn() as conn:
                conn.execute(
                    """INSERT INTO futures_klines
                       (symbol, contract, timeframe, timestamp, open, high, low, close, volume)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (SYMBOL, CONTRACT, tf, NOW, 100, 105, 99, 103, 1000),
                )
                conn.commit()

        # fetch_klines 返回的数据 timestamp == NOW（<= 存量最后时间戳）→ 全被过滤掉
        mock_fetch.return_value = [
            {"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "15m",
             "timestamp": NOW, "open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000},
        ]

        result = collector.collect_symbol(SYMBOL, CONTRACT)

        # 3 个周期全部 saved == 0 → 不触发重算
        mock_restructure.assert_not_called()
        for tf in ["15m", "1h", "1d"]:
            assert result[tf]["saved"] == 0, f"{tf} saved 应为 0"

    @patch("data.futures_collector.fetch_klines")
    @patch("futures.n_structure.restructure_active_for_symbol")
    def test_triggers_once_per_timeframe_with_data(
        self,
        mock_restructure: MagicMock,
        mock_fetch: MagicMock,
        collector: FuturesCollector,
    ) -> None:
        """场景：多周期均有新数据 → 每个 cycle 都会触发重算（多个保存点）。"""
        # 分批返回数据：第一次调用（15m）→ 3条，第二次（1h）→ 2条，第三次（1d）→ 1条
        mock_fetch.side_effect = [
            # 15m
            [{"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "15m",
              "timestamp": NOW, "open": 100, "close": 103, "high": 105, "low": 99, "volume": 1000}],
            # 1h
            [{"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "1h",
              "timestamp": NOW, "open": 100, "close": 103, "high": 105, "low": 99, "volume": 1000}],
            # 1d
            [{"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "1d",
              "timestamp": NOW, "open": 100, "close": 103, "high": 105, "low": 99, "volume": 1000}],
        ]

        collector.collect_symbol(SYMBOL, CONTRACT)

        # 每个周期 saved > 0 都会调用一次 restructure
        assert mock_restructure.call_count == 3, (
            f"3 个周期均 saved>0，应调 3 次，实际 {mock_restructure.call_count} 次"
        )


# ═══════════════════════════════════════════════════════════
# 2. _collect_3m_from_1m 3m 聚合钩子
# ═══════════════════════════════════════════════════════════

class TestCollect3mHook:
    """验证 _collect_3m_from_1m 写入后触发 3m 重算。"""

    @patch("data.futures_collector.FuturesCollector._get_last_kline_timestamp")
    @patch("data.futures_collector.FuturesCollector.aggregate_3m_from_1m")
    @patch("futures.n_structure.restructure_active_for_symbol")
    def test_triggers_restructure_with_3m_timeframe(
        self,
        mock_restructure: MagicMock,
        mock_aggregate: MagicMock,
        mock_last_ts: MagicMock,
        collector: FuturesCollector,
    ) -> None:
        """场景：3m 聚合有新数据 → 触发 restructure_active_for_symbol(timeframes=["3m"])。"""
        # 模拟聚合返回 2 条 3m K 线
        mock_aggregate.return_value = [
            {"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "3m",
             "timestamp": NOW, "open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000},
            {"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "3m",
             "timestamp": NOW + 180, "open": 103, "high": 108, "low": 102, "close": 106, "volume": 1200},
        ]
        # 模拟无存量 3m 数据（全部为新数据）
        mock_last_ts.return_value = None

        collector._collect_3m_from_1m(SYMBOL, CONTRACT, [])

        # 验证调用了 restructure_active_for_symbol，且 timeframes=["3m"]
        mock_restructure.assert_called_once_with(
            SYMBOL, CONTRACT, collector.db, timeframes=["3m"],
        )

    @patch("data.futures_collector.FuturesCollector._get_last_kline_timestamp")
    @patch("data.futures_collector.FuturesCollector.aggregate_3m_from_1m")
    @patch("futures.n_structure.restructure_active_for_symbol")
    def test_no_restructure_when_no_new_3m(
        self,
        mock_restructure: MagicMock,
        mock_aggregate: MagicMock,
        mock_last_ts: MagicMock,
        collector: FuturesCollector,
    ) -> None:
        """场景：聚合结果均为存量数据 → klines_3m 为空 → 不触发重算。"""
        # 聚合返回 1 条
        mock_aggregate.return_value = [
            {"symbol": SYMBOL, "contract": CONTRACT, "timeframe": "3m",
             "timestamp": NOW, "open": 100, "close": 103, "high": 105, "low": 99, "volume": 1000},
        ]
        # 但最新时间戳晚于或等于聚合结果 → 过滤后为空
        mock_last_ts.return_value = NOW

        collector._collect_3m_from_1m(SYMBOL, CONTRACT, [])

        mock_restructure.assert_not_called()

    @patch("data.futures_collector.FuturesCollector._get_last_kline_timestamp")
    @patch("data.futures_collector.FuturesCollector.aggregate_3m_from_1m")
    @patch("futures.n_structure.restructure_active_for_symbol")
    def test_aggregate_empty_no_restructure(
        self,
        mock_restructure: MagicMock,
        mock_aggregate: MagicMock,
        mock_last_ts: MagicMock,
        collector: FuturesCollector,
    ) -> None:
        """场景：聚合结果为 None → klines_3m 为空 → 不触发重算。"""
        mock_aggregate.return_value = None

        collector._collect_3m_from_1m(SYMBOL, CONTRACT, [])

        mock_restructure.assert_not_called()
        mock_last_ts.assert_not_called()