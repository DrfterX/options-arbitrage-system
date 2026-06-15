"""测试期货信号回测引擎。"""
import os
import time
import pytest
import sqlite3
from unittest.mock import patch
from datetime import datetime

from futures.backtest import (
    run_backtest,
    _find_entry_price,
    _find_exit_prices,
    _build_kline_map,
    SCORE_BANDS,
    _compute_summary,
    _compute_by_score_band,
    _compute_by_symbol,
)


class FakeSqliteRow(dict):
    """模拟 sqlite3.Row — 支持 dict() 和键访问，同时是 dict 的子类。"""

    def __init__(self, mapping):
        super().__init__(mapping)
        self._mapping = mapping

    def __getitem__(self, key):
        if isinstance(key, int):
            keys = list(self._mapping.keys())
            return self._mapping[keys[key]]
        return self._mapping[key]

    def keys(self):
        return self._mapping.keys()


class FakeConn:
    """模拟 SQLite 连接的快速回测测试夹具。"""

    def __init__(self):
        self._closed = False

    def close(self):
        self._closed = True


class FakeDb:
    """模拟 Database 类，供回测逻辑使用。"""

    def __init__(self, klines=None, signals=None):
        self.klines = klines or []
        self.signals = signals or []
        self._conn = None

    def get_conn(self):
        """返回一个带 execute 闭包的模拟连接。"""
        klines = self.klines
        signals = self.signals
        _cls = [False]

        class FakeCursor:
            def __init__(self, result):
                self._result = result

            def fetchall(self):
                return self._result

            def fetchone(self):
                return self._result[0] if self._result else None

            def __iter__(self):
                return iter(self._result)

        class FakeConn2:
            def close(self):
                _cls[0] = True

            def execute(self, sql, params=None):
                sql_upper = sql.strip().upper()
                if "FUTURES_KLINES" in sql_upper and "TIMEFRAME='1D'" in sql_upper:
                    return FakeCursor([FakeSqliteRow(r) for r in klines])
                elif "FUTURES_SIGNALS" in sql_upper:
                    return FakeCursor([FakeSqliteRow(r) for r in signals])
                return FakeCursor([])

        self._conn = FakeConn2()
        return self._conn

    @property
    def conn(self):
        return self._conn


class TestFindEntryExit:
    """测试入场/退出价查找逻辑。"""

    def test_find_entry_price_normal(self):
        klines = [
            (1000, 100.0),
            (2000, 101.0),
            (3000, 102.0),
            (4000, 103.0),
        ]
        # 信号在 2500 — 应匹配 2000 时段的 101.0
        price = _find_entry_price(klines, 2500)
        assert price == 101.0

    def test_find_entry_price_before_first(self):
        klines = [(2000, 100.0)]
        price = _find_entry_price(klines, 1000)
        assert price == 100.0

    def test_find_entry_price_empty(self):
        price = _find_entry_price([], 1000)
        assert price is None

    def test_find_exit_prices_normal(self):
        klines = [
            (1000, 100.0),
            (2000, 101.0),
            (3000, 102.0),
            (4000, 103.0),
            (5000, 104.0),
        ]
        exits = _find_exit_prices(klines, 1, [1, 2, 5])
        assert exits["1"] == 102.0
        assert exits["2"] == 103.0
        assert exits["5"] is None  # 超出范围

    def test_find_exit_prices_edge(self):
        klines = [(1000, 100.0)]
        exits = _find_exit_prices(klines, 0, [1, 2])
        assert exits["1"] is None
        assert exits["2"] is None


class TestBuildKlineMap:
    """测试 Kline map 构建。"""

    def test_empty(self):
        klines = []
        # 用真实 db 测试构建逻辑，用空 klines
        # 直接测试内部逻辑——无 klines 时返回空 dict
        assert True  # 测试占位符


class TestComputeSummary:
    """测试汇总统计。"""

    def test_empty(self):
        r = _compute_summary([], [1, 2, 5, 10])
        assert r["total_signals"] == 0

    def test_long_only(self):
        trades = [
            {
                "direction": "LONG",
                "score": 0.5,
                "trades": {
                    "1": {"correct": True, "return_pct": 1.0},
                    "2": {"correct": True, "return_pct": 2.0},
                    "5": {"correct": False, "return_pct": -0.5},
                    "10": {"correct": True, "return_pct": 3.0},
                },
            }
        ]
        r = _compute_summary(trades, [1, 2, 5, 10])
        assert r["long_pct"] == 100.0
        assert r["short_pct"] == 0.0
        assert r["1d"]["accuracy"] == 100.0
        assert r["2d"]["accuracy"] == 100.0
        assert r["5d"]["accuracy"] == 0.0


class TestComputeByScoreBand:
    """测试评分区间统计。"""

    def test_band_filtering(self):
        trades = [
            {"score": 0.25, "trades": {"1": {"correct": True, "return_pct": 1.0}}},
            {"score": 0.35, "trades": {"1": {"correct": False, "return_pct": -1.0}}},
            {"score": 0.45, "trades": {"1": {"correct": True, "return_pct": 0.5}}},
            {"score": 0.55, "trades": {"1": {"correct": True, "return_pct": 2.0}}},
            {"score": 0.65, "trades": {"1": {"correct": False, "return_pct": -2.0}}},
        ]
        bands = _compute_by_score_band(trades, [1])
        names = {b["band"]: b for b in bands}
        assert "0(NONE)" in names
        assert names["0(NONE)"]["1d_acc"] == 60.0


class TestRunBacktest:
    """回测引擎集成测试。"""

    def test_empty_db(self):
        db = FakeDb(klines=[], signals=[])
        result = run_backtest(db)
        assert result["valid_trades"] == 0
        assert result["summary"]["total_signals"] == 0

    def test_single_trade(self):
        """一个 LONG 信号，当天 100 买入，1天后 102。"""
        # 信号时间 2026-06-01 10:00:00 = 1748761200
        # 日线时间
        klines = [
            {"symbol": "I", "contract": "I2609", "timeframe": "1d",
             "timestamp": 1780243200, "close": 100.0},  # 2026-06-01 00:00:00 UTC
            {"symbol": "I", "contract": "I2609", "timeframe": "1d",
             "timestamp": 1780329600, "close": 102.0},  # 2026-06-02 00:00:00 UTC
        ]
        signals = [
            {"id": 1, "symbol": "I", "contract": "I2609",
             "direction": "LONG", "signal_type": "WATCH",
             "level1_pass": 1, "level2_pass": 0, "level3_pass": 0,
             "score": 0.3,
             "created_at": "2026-06-01 10:00:00"},
        ]
        db = FakeDb(klines=klines, signals=signals)
        result = run_backtest(db)
        assert result["valid_trades"] == 1
        assert result["summary"]["1d"]["correct"] == 1
        assert result["summary"]["1d"]["accuracy"] == 100.0

    def test_short_trade(self):
        """一个 SHORT 信号，当天 100 卖出，1天后 98 → 正确。"""
        klines = [
            {"symbol": "I", "contract": "I2609", "timeframe": "1d",
             "timestamp": 1780243200, "close": 100.0},
            {"symbol": "I", "contract": "I2609", "timeframe": "1d",
             "timestamp": 1780329600, "close": 98.0},
        ]
        signals = [
            {"id": 1, "symbol": "I", "contract": "I2609",
             "direction": "SHORT", "signal_type": "WATCH",
             "level1_pass": 1, "level2_pass": 0, "level3_pass": 0,
             "score": 0.3,
             "created_at": "2026-06-01 10:00:00"},
        ]
        db = FakeDb(klines=klines, signals=signals)
        result = run_backtest(db)
        assert result["valid_trades"] == 1
        assert result["summary"]["1d"]["correct"] == 1

    def test_wrong_direction(self):
        """LONG 但价格跌了 → 错误。"""
        klines = [
            {"symbol": "I", "contract": "I2609", "timeframe": "1d",
             "timestamp": 1780243200, "close": 100.0},
            {"symbol": "I", "contract": "I2609", "timeframe": "1d",
             "timestamp": 1780329600, "close": 98.0},
        ]
        signals = [
            {"id": 1, "symbol": "I", "contract": "I2609",
             "direction": "LONG", "signal_type": "WATCH",
             "level1_pass": 1, "level2_pass": 0, "level3_pass": 0,
             "score": 0.3,
             "created_at": "2026-06-01 10:00:00"},
        ]
        db = FakeDb(klines=klines, signals=signals)
        result = run_backtest(db)
        assert result["valid_trades"] == 1
        assert result["summary"]["1d"]["correct"] == 0
        assert result["summary"]["1d"]["accuracy"] == 0.0

    def test_cache(self):
        """检查缓存机制。"""
        db = FakeDb(klines=[], signals=[])
        r1 = run_backtest(db)
        # 立即调用应命中缓存
        r2 = run_backtest(db)
        assert r1["elapsed_seconds"] == r2["elapsed_seconds"]


class TestClosestKlineSearch:
    """测试二分查找逻辑的边界情况。"""

    def test_exact_timestamp(self):
        """信号时间与某根 K 线完全对齐。"""
        klines = [
            (100, 10.0),
            (200, 11.0),
            (300, 12.0),
        ]
        # signal_epoch = 200, bisect_right - 1 = 1 -> 11.0
        assert _find_entry_price(klines, 200) == 11.0

    def test_between_klines(self):
        """信号在两根 K 线之间。"""
        klines = [
            (100, 10.0),
            (200, 11.0),
            (300, 12.0),
        ]
        # signal_epoch = 150, bisect_right - 1 = 0 -> 10.0
        assert _find_entry_price(klines, 150) == 10.0

    def test_after_last(self):
        """信号在所有 K 线之后。"""
        klines = [
            (100, 10.0),
            (200, 11.0),
        ]
        assert _find_entry_price(klines, 999) == 11.0


class TestRunBacktestEndToEnd:
    """集成测试：模拟一个小型数据库。"""

    def test_stub(self):
        """占位 — 真正的集成测试在 test_backtest_real_data 中。"""
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])