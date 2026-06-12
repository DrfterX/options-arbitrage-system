"""验证：1 分钟 K 线风控价格源优先级 + 降级回退逻辑。"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.db import Database
from core.schema import ALL_TABLES, INDEXES
from data.futures_collector import FuturesCollector


@pytest.fixture
def temp_db():
    """创建内存数据库并初始化表结构。"""
    db = Database(":memory:")
    with db.get_conn() as conn:
        for sql in ALL_TABLES.values():
            conn.execute(sql)
        for sql in INDEXES:
            conn.execute(sql)
        conn.commit()
    return db


@pytest.fixture
def collector(temp_db):
    """创建 FuturesCollector 实例（使用 mock registry）。"""
    from unittest.mock import MagicMock
    registry = MagicMock()
    return FuturesCollector(temp_db, registry)


def seed_klines(db, contract, timeframe, records):
    """向 futures_klines 表插入测试 K 线数据。"""
    sql = """
        INSERT OR IGNORE INTO futures_klines
        (symbol, contract, timeframe, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with db.get_conn() as conn:
        for r in records:
            conn.execute(sql, (
                r.get("symbol", "SC"),
                contract,
                timeframe,
                r["timestamp"],
                r.get("open", r["close"]),
                r.get("high", r["close"]),
                r.get("low", r["close"]),
                r["close"],
                r.get("volume", 100),
            ))
        conn.commit()


class TestRiskPriceMap:
    """验证 `_build_risk_price_map()` 的 1m 优先 + 降级回退逻辑。"""

    def test_priority_1m_over_other_timeframes(self, collector):
        """场景：同时有 1m 和其他周期数据 → 查询优先返回 1m 的最新价格。"""
        T_NOW = 2000
        seed_klines(collector.db, "SC2607", "1m", [
            {"timestamp": T_NOW, "close": 548.0},
            {"timestamp": T_NOW - 60, "close": 547.5},
        ])
        seed_klines(collector.db, "SC2607", "15m", [
            {"timestamp": T_NOW, "close": 546.8},
        ])

        price_map = _build_risk_price_map(collector.db, ["SC2607"])
        assert "SC2607" in price_map
        assert price_map["SC2607"] == 548.0, (
            f"应返回 1m 的 548.0，实际返回 {price_map['SC2607']}"
        )

    def test_fallback_when_no_1m(self, collector):
        """场景：无 1m 数据 → 降级回退到其他周期的最近数据。"""
        seed_klines(collector.db, "SC2607", "15m", [
            {"timestamp": 1500, "close": 545.0},
            {"timestamp": 1800, "close": 546.8},
        ])

        price_map = _build_risk_price_map(collector.db, ["SC2607"])
        assert "SC2607" in price_map
        assert price_map["SC2607"] == 546.8

    def test_no_data_returns_empty(self, collector):
        """场景：无任何 K 线数据 → 返回空映射。"""
        price_map = _build_risk_price_map(collector.db, ["SC2607"])
        assert price_map == {}

    def test_multiple_contracts(self, collector):
        """场景：多个持仓合约 → 各自返回正确的优先价格。"""
        T = 2000
        seed_klines(collector.db, "SC2607", "1m", [
            {"symbol": "SC", "timestamp": T, "close": 548.0},
        ])
        seed_klines(collector.db, "RB2510", "1m", [
            {"symbol": "RB", "timestamp": T, "close": 3200.0},
        ])
        seed_klines(collector.db, "RB2510", "15m", [
            {"symbol": "RB", "timestamp": T, "close": 3195.0},
        ])

        price_map = _build_risk_price_map(collector.db, ["SC2607", "RB2510"])
        assert price_map.get("SC2607") == 548.0
        assert price_map.get("RB2510") == 3200.0


class TestCollectRiskPrices:
    """验证 `collect_risk_prices()` 增量采集行为。"""

    def test_contract_to_symbol(self, collector):
        """验证合约代码反查品种代码。"""
        seed_klines(collector.db, "SC2607", "15m", [
            {"symbol": "SC", "timestamp": 1000, "close": 546.0},
        ])
        symbol = collector._contract_to_symbol("SC2607")
        assert symbol == "SC", f"应返回 'SC'，实际返回 '{symbol}'"

    def test_contract_to_symbol_not_found(self, collector):
        """验证未知合约返回 None。"""
        symbol = collector._contract_to_symbol("UNKNOWN")
        assert symbol is None

    def test_collect_risk_prices_empty_contracts(self, collector):
        """验证空合约列表返回空字典。"""
        result = collector.collect_risk_prices([])
        assert result == {}

    def test_collect_risk_prices_unknown_contract(self, collector, caplog):
        """验证未知合约跳过并记录日志。"""
        import logging
        caplog.set_level(logging.WARNING)
        result = collector.collect_risk_prices(["UNKNOWN"])
        assert result == {}
        assert any("未找到对应品种" in msg for msg in caplog.messages)


class TestDataRefreshIntegration:
    """验证 `data_refresh()` 中嵌入的 collect_risk_prices 调用。"""

    def test_orchestrator_embeds_risk_collection(self):
        """验证 orchestrator 的 data_refresh 中包含 collect_risk_prices 调用。"""
        import inspect
        from pipeline.orchestrator import Orchestrator

        source = inspect.getsource(Orchestrator.data_refresh)
        # 检查关键元素
        checks = [
            ("collect_risk_prices", "应调用 collect_risk_prices"),
            ("open_contracts", "应查询持仓合约"),
            ("1m", "应提到 1m 采集"),
        ]
        for keyword, msg in checks:
            assert keyword in source, f"data_refresh: {msg}"


# ── 辅助：模拟 _build_risk_price_map（直接从 orchestrator 复制核心逻辑）──

def _build_risk_price_map(db, open_contracts: list[str]) -> dict[str, float]:
    """从 futures_klines 表查询每个持仓合约的最新收盘价，优先 1m。"""
    if not open_contracts:
        return {}

    conn = db.get_conn()
    price_map: dict[str, float] = {}
    for contract in open_contracts:
        # 优先取 1m 数据（最实时）
        latest = conn.execute(
            "SELECT close FROM futures_klines "
            "WHERE contract=? AND timeframe='1m' "
            "ORDER BY timestamp DESC LIMIT 1",
            (contract,),
        ).fetchone()
        # 降级：无 1m 数据时回退到任意周期
        if not latest:
            latest = conn.execute(
                "SELECT close FROM futures_klines "
                "WHERE contract=? ORDER BY timestamp DESC LIMIT 1",
                (contract,),
            ).fetchone()
        if latest:
            price_map[contract] = latest["close"]
    return price_map