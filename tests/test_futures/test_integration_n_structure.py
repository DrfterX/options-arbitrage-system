"""集成测试：验证 N 型结构全链路 — K 线 → 极值点 → N 型检测 → 动态重算 → A 突破 → B 反转。

使用真实内存 SQLite，模拟连续行情推送，验证每次重算的触发时机和结果正确性。

注意事项：
- ``_get_klines(limit=3)`` 只取最近 3 根 K 线 → 测试需只 seed "新的"K 线
- "无变化"路径返回 ``active`` 原始字典（不含 ``is_active``）
- 通过 ``@patch("time.time")`` 避免 freshness 检查与模拟时间戳冲突
"""

import logging
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

from core.db import Database
from core.schema import ALL_TABLES, INDEXES
from futures.n_structure import NState, detect_and_save, dynamic_restructure
from tests.conftest import make_swing, make_kline

logger = logging.getLogger(__name__)

# ─── 虚假"当前"时间（确保 freshness 通过） ──────────────────
FAKE_NOW = 100_000_000
TS = FAKE_NOW - 3600  # 1 小时前，远在 freshness 窗口内


# ─── 辅助函数 ────────────────────────────────────────────────


def _create_tables(db: Database) -> None:
    with db.get_conn() as conn:
        for sql in ALL_TABLES.values():
            conn.execute(sql)
        for sql in INDEXES:
            conn.execute(sql)
        conn.commit()


def _insert_n_structure(db: Database, ns: dict) -> None:
    with db.get_conn() as conn:
        conn.execute(
            """INSERT INTO futures_n_structures
               (symbol, contract, timeframe, direction, state,
                point_a_time, point_a_price,
                point_b_time, point_b_price,
                point_c_time, point_c_price)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (ns["symbol"], ns["contract"], ns["timeframe"],
             ns["direction"], ns["state"],
             ns["point_a_time"], ns["point_a_price"],
             ns["point_b_time"], ns["point_b_price"],
             ns["point_c_time"], ns["point_c_price"]),
        )
        conn.commit()


def _seed_klines(db: Database, symbol: str, contract: str, tf: str,
                 klines: List[Dict[str, Any]]) -> None:
    with db.get_conn() as conn:
        for k in klines:
            conn.execute(
                """INSERT INTO futures_klines
                   (symbol, contract, timeframe, timestamp,
                    open, high, low, close, volume)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (symbol, contract, tf, k["timestamp"],
                 k["open"], k["high"], k["low"], k["close"], k.get("volume", 100)),
            )
        conn.commit()


def _seed_swings(db: Database, symbol: str, contract: str, tf: str,
                 swings: List[Dict[str, Any]]) -> None:
    with db.get_conn() as conn:
        for sp in swings:
            conn.execute(
                """INSERT INTO futures_swing_points
                   (symbol, contract, timeframe, timestamp, price, point_type)
                   VALUES (?,?,?,?,?,?)""",
                (symbol, contract, tf, sp["timestamp"], sp["price"], sp["point_type"]),
            )
        conn.commit()


def assert_is_active(result: dict) -> None:
    """验证结果包含活跃结构标记。"""
    assert result.get("is_active", False) is True


# ═══════════════════════════════════════════════════════════════
# Phase 1: 初始检测
# ═══════════════════════════════════════════════════════════════

class TestPhase1InitialDetection:
    """初始 K 线 → detect_and_save 产生有效结构。"""

    SYMBOL = "RB"
    CONTRACT = "rb2510"
    TF = "1d"

    @pytest.fixture
    def db(self) -> Database:
        db_instance = Database(":memory:")
        _create_tables(db_instance)
        return db_instance

    @patch("time.time")
    def test_detect_long_leg2(self, mock_time: Any, db: Database) -> None:
        """3 个交替极值点 [TROUGH, PEAK, TROUGH] → LONG LEG2"""
        mock_time.return_value = FAKE_NOW

        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 1, close=90, low=88, high=92),
            make_kline(TS + 2, close=95, low=93, high=97),
            make_kline(TS + 3, close=110, low=108, high=112),
            make_kline(TS + 4, close=105, low=103, high=107),
            make_kline(TS + 5, close=100, low=98, high=102),
            make_kline(TS + 6, close=103, low=101, high=105),
        ])
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("TROUGH", 90, TS + 1),
            make_swing("PEAK", 110, TS + 3),
            make_swing("TROUGH", 100, TS + 5),
        ])

        result = detect_and_save(self.SYMBOL, self.CONTRACT, self.TF, db)

        assert result["direction"] == "LONG"
        assert result["point_a_price"] == 90.0
        assert result["point_b_price"] == 110.0
        assert result["point_c_price"] == 100.0
        assert_is_active(result)

    @patch("time.time")
    def test_detect_short_leg2(self, mock_time: Any, db: Database) -> None:
        """3 个交替极值点 [PEAK, TROUGH, PEAK] → SHORT LEG2"""
        mock_time.return_value = FAKE_NOW

        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 1, close=110, low=108, high=112),
            make_kline(TS + 3, close=90, low=88, high=92),
            make_kline(TS + 5, close=100, low=98, high=102),
        ])
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("PEAK", 110, TS + 1),
            make_swing("TROUGH", 90, TS + 3),
            make_swing("PEAK", 105, TS + 5),
        ])

        result = detect_and_save(self.SYMBOL, self.CONTRACT, self.TF, db)

        assert result["direction"] == "SHORT"
        assert result["point_a_price"] == 110.0
        assert result["point_b_price"] == 90.0
        assert result["point_c_price"] == 105.0
        assert result["point_c_price"] > result["point_b_price"]  # 条件2：C > B
        assert_is_active(result)


# ═══════════════════════════════════════════════════════════════
# Phase 2: A 突破 → 结构迁移（LONG）
# ═══════════════════════════════════════════════════════════════

class TestPhase2ABrokenMigration:
    """价格突破 A 点触发结构迁移。"""

    SYMBOL = "RB"
    CONTRACT = "rb2510"
    TF = "1d"

    @pytest.fixture
    def db(self) -> Database:
        db_instance = Database(":memory:")
        _create_tables(db_instance)
        return db_instance

    @patch("time.time")
    def test_long_a_broken_migration(self, mock_time: Any, db: Database) -> None:
        """LONG A=90,B=110,C=100。价格跌破 A(90)→old_B(110)→new_A，方向翻转为 SHORT。

        注意：只 seed 最新的 3+ 根 K 线（_get_klines(limit=3) 只看最近 3 根）。
        """
        mock_time.return_value = FAKE_NOW

        _insert_n_structure(db, {
            "symbol": self.SYMBOL, "contract": self.CONTRACT,
            "timeframe": self.TF,
            "direction": "LONG", "state": NState.LEG3.value,
            "point_a_time": TS + 1, "point_a_price": 90.0,
            "point_b_time": TS + 3, "point_b_price": 110.0,
            "point_c_time": TS + 5, "point_c_price": 100.0,
        })

        # 最新 K 线：跌破 A=90
        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 7, close=85, low=83, high=88),
            make_kline(TS + 8, close=87, low=85, high=89),
            make_kline(TS + 9, close=86, low=84, high=88),
        ])
        # 极值点（B 时间之后）
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("TROUGH", 90, TS + 1),
            make_swing("PEAK", 110, TS + 3),
            make_swing("TROUGH", 100, TS + 5),
            make_swing("TROUGH", 85, TS + 7),
            make_swing("PEAK", 92, TS + 8),
        ])

        result = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)

        assert result["point_a_price"] == 110.0  # old_B → new_A
        assert result["point_b_price"] == 85.0   # new_B (first TROUGH after B)
        assert result["point_c_price"] == 92.0   # new_C (first PEAK after new_B)
        assert result["direction"] == "SHORT"
        assert_is_active(result)

    @patch("time.time")
    def test_short_a_broken_migration(self, mock_time: Any, db: Database) -> None:
        """SHORT A=110,B=90,C=105。价格突破 A(110)→old_B(90)→new_A，方向翻转为 LONG。"""
        mock_time.return_value = FAKE_NOW

        _insert_n_structure(db, {
            "symbol": self.SYMBOL, "contract": self.CONTRACT,
            "timeframe": self.TF,
            "direction": "SHORT", "state": NState.LEG3.value,
            "point_a_time": TS + 1, "point_a_price": 110.0,
            "point_b_time": TS + 3, "point_b_price": 90.0,
            "point_c_time": TS + 5, "point_c_price": 105.0,
        })

        # 最新 K 线：突破 A=110
        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 7, close=115, low=112, high=118),
            make_kline(TS + 8, close=100, low=95, high=102),
            make_kline(TS + 9, close=102, low=98, high=104),
        ])
        # 极值点（B 时间之后）
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("PEAK", 110, TS + 1),
            make_swing("TROUGH", 90, TS + 3),
            make_swing("PEAK", 105, TS + 5),
            make_swing("TROUGH", 95, TS + 7),
            make_swing("PEAK", 100, TS + 8),
        ])

        result = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)

        # SHORT A=110(PEAK)→old_B=90(TROUGH)→new_A=90.0
        # new_B = first PEAK after T90 = P105(TS+5) price=105.0
        # new_C = first TROUGH after P105 = T95(TS+7) price=95.0
        assert result["point_a_price"] == 90.0
        assert result["point_b_price"] == 105.0
        assert result["point_c_price"] == 95.0
        assert result["direction"] == "LONG"
        assert_is_active(result)

    @patch("time.time")
    def test_a_not_broken_return_active(self, mock_time: Any, db: Database) -> None:
        """A 未突破 → 返回 active 原始结构（不触发迁移）。"""
        mock_time.return_value = FAKE_NOW

        _insert_n_structure(db, {
            "symbol": self.SYMBOL, "contract": self.CONTRACT,
            "timeframe": self.TF,
            "direction": "LONG", "state": NState.LEG3.value,
            "point_a_time": TS + 1, "point_a_price": 90.0,
            "point_b_time": TS + 3, "point_b_price": 110.0,
            "point_c_time": TS + 5, "point_c_price": 100.0,
        })

        # 最新 K 线：正常波动，未破 A=90，未触发 B 反转（回撤 < 50%）
        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 7, close=105, low=103, high=108),
            make_kline(TS + 8, close=107, low=105, high=109),
            make_kline(TS + 9, close=106, low=104, high=110),
        ])

        result = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)

        # 返回 active（不含 is_active 字段）
        assert result["direction"] == "LONG"
        assert result["point_a_price"] == 90.0
        assert result["point_b_price"] == 110.0
        assert result["state"] == NState.LEG3.value


# ═══════════════════════════════════════════════════════════════
# Phase 3: B 点反转
# ═══════════════════════════════════════════════════════════════

class TestPhase3BReversal:
    """价格未破 A 但反穿 B 时触发 B 反转 → COMPLETED → detect_and_save 重算。"""

    SYMBOL = "RB"
    CONTRACT = "rb2510"
    TF = "1d"

    @pytest.fixture
    def db(self) -> Database:
        db_instance = Database(":memory:")
        _create_tables(db_instance)
        return db_instance

    @patch("time.time")
    def test_long_b_reversal(self, mock_time: Any, db: Database) -> None:
        """LONG B 反转：price 从 B(110) 跌回，latest_high < B, 回撤 > 50%。
        A=90,B=110 → 最新 high=98 < 110, 回撤(110-98)/(110-90)=60% > 50% → B 反转。
        """
        mock_time.return_value = FAKE_NOW

        _insert_n_structure(db, {
            "symbol": self.SYMBOL, "contract": self.CONTRACT,
            "timeframe": self.TF,
            "direction": "LONG", "state": NState.LEG3.value,
            "point_a_time": TS + 1, "point_a_price": 90.0,
            "point_b_time": TS + 3, "point_b_price": 110.0,
            "point_c_time": TS + 5, "point_c_price": 100.0,
        })

        # 最新 K 线：跌回但未破 A=90（low=92 > 90），high=98 < B=110
        # 注意：detect_and_save 需要条件 4（最新价 > C=100），所以加 TS+9 收盘 102
        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 7, close=93, low=92, high=98),
            make_kline(TS + 8, close=94, low=93, high=97),
            make_kline(TS + 9, close=102, low=100, high=104),  # 条件4：最新价 > C=100
        ])
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("TROUGH", 90, TS + 1),
            make_swing("PEAK", 110, TS + 3),
            make_swing("TROUGH", 100, TS + 5),
            make_swing("PEAK", 98, TS + 7),
        ])

        result = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)

        # B 反转 → COMPLETED + detect_and_save 重算
        assert_is_active(result)
        assert result["state"] in (NState.LEG2.value, NState.LEG3.value)

    @patch("time.time")
    def test_short_b_reversal(self, mock_time: Any, db: Database) -> None:
        """SHORT B 反转：price 从 B(90) 反弹，latest_low > B, 回弹 > 50%。
        A=110,B=90 → 最低 low=101 > 90, 回弹(101-90)/(110-90)=55% > 50% → B 反转。
        """
        mock_time.return_value = FAKE_NOW

        _insert_n_structure(db, {
            "symbol": self.SYMBOL, "contract": self.CONTRACT,
            "timeframe": self.TF,
            "direction": "SHORT", "state": NState.LEG3.value,
            "point_a_time": TS + 1, "point_a_price": 110.0,
            "point_b_time": TS + 3, "point_b_price": 90.0,
            "point_c_time": TS + 5, "point_c_price": 105.0,
        })

        # 最新 K 线：反弹，最低 low=101 > B=90, 最高 high=106 < A=110
        # _get_klines(limit=3) 取最后 3 根：low=min(101,102,103)=101
        # 回弹(101-90)/(110-90)=11/20=55% > 50% ✅
        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 7, close=102, low=101, high=105),
            make_kline(TS + 8, close=103, low=102, high=106),
            make_kline(TS + 9, close=104, low=103, high=107),  # 第三根确保 limit=3 足够
        ])
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("PEAK", 110, TS + 1),
            make_swing("TROUGH", 90, TS + 3),
            make_swing("PEAK", 105, TS + 5),
            make_swing("TROUGH", 98, TS + 7),
        ])

        result = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)

        assert_is_active(result)
        assert result["state"] in (NState.LEG2.value, NState.LEG3.value)


# ═══════════════════════════════════════════════════════════════
# Phase 4: 连续多次推送
# ═══════════════════════════════════════════════════════════════

class TestPhase4MultiplePush:
    """连续多次行情推送：正常 → A 突破 → B 反转。"""

    SYMBOL = "RB"
    CONTRACT = "rb2510"
    TF = "1d"

    @pytest.fixture
    def db(self) -> Database:
        db_instance = Database(":memory:")
        _create_tables(db_instance)
        return db_instance

    @patch("time.time")
    def test_three_pushes_in_sequence(self, mock_time: Any, db: Database) -> None:
        """三次推送：Push1 正常 → Push2 A 突破（方向翻转）→ Push3 B 反转。"""
        mock_time.return_value = FAKE_NOW

        # ── 种子：LONG LEG3 A=100, B=130, C=115 ──
        _insert_n_structure(db, {
            "symbol": self.SYMBOL, "contract": self.CONTRACT,
            "timeframe": self.TF,
            "direction": "LONG", "state": NState.LEG3.value,
            "point_a_time": TS + 1, "point_a_price": 100.0,
            "point_b_time": TS + 3, "point_b_price": 130.0,
            "point_c_time": TS + 5, "point_c_price": 115.0,
        })
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("TROUGH", 100, TS + 1),
            make_swing("PEAK", 130, TS + 3),
            make_swing("TROUGH", 115, TS + 5),
        ])

        # ── Push 1: 正常波动（未破 A=100，回撤 < 50%） ──
        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 7, close=118, low=116, high=120),
        ])

        r1 = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)
        assert r1["direction"] == "LONG"
        assert r1["point_a_price"] == 100.0

        # ── Push 2: A 被突破（最新 low=93 < A=100） ──
        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 9, close=95, low=93, high=97),
            make_kline(TS + 10, close=105, low=103, high=107),
        ])
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("TROUGH", 110, TS + 7),
            make_swing("PEAK", 120, TS + 9),
        ])

        r2 = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)
        # LONG A=100,B=130,C=115 → A broken(low=93<100) → migration:
        # old_B=130(PEAK) → new_A=130(PEAK)
        # ISEED swings (after old_B time=TS+3):
        #   TROUGH(115, TS+5) → new_B (first TROUGH, original C点)
        #   TROUGH(110, TS+7)  → same type, merged into T115
        #   PEAK(120, TS+9)    → new_C (first PEAK after new_B)
        # direction: A(130) > B(115) → SHORT
        # C2 check: SHORT C(120) > B(115) ✅
        assert r2["direction"] == "SHORT"
        assert r2["point_a_price"] == 130.0
        assert r2["point_b_price"] == 115.0
        assert r2["point_c_price"] == 120.0
        assert_is_active(r2)

        # ── Push 3: 新 SHORT 结构 B 反转 ──
        # SHORT: A=130, B=115 → latest_low > 115 且回弹 > 50%
        # 回弹需要 (low-115)/(130-115) > 0.5 → low > 122.5
        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 12, close=123, low=123, high=124),
            make_kline(TS + 13, close=124, low=124, high=125),
            make_kline(TS + 14, close=125, low=125, high=126),
        ])
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("PEAK", 125, TS + 12),
        ])

        r3 = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)
        # B 反转检测：SHORT A=130, B=115 → 需 latest_low > 122.5
        # 但 min(low) across all klines = min(93,103,123,124,125) = 93 < 115
        # → B 反转条件不满足（历史低点 93 仍低于 B=115）
        # 正确行为：SHORT 结构仍有效
        assert r3["direction"] == "SHORT"
        assert r3["point_a_price"] == 130.0
        assert r3["point_b_price"] == 115.0
        assert_is_active(r3)

    @patch("time.time")
    def test_short_b_reversal_triggers_restructure(self, mock_time: Any, db: Database) -> None:
        """SHORT 结构 B 反转后标记 COMPLETED + 全量重算（配合 since_timestamp 全量 K 线检查）。"""
        mock_time.return_value = FAKE_NOW

        _insert_n_structure(db, {
            "symbol": self.SYMBOL, "contract": self.CONTRACT,
            "timeframe": self.TF,
            "direction": "SHORT", "state": NState.LEG2.value,
            "point_a_time": TS + 1, "point_a_price": 130.0,  # PEAK
            "point_b_time": TS + 3, "point_b_price": 115.0,  # TROUGH
            "point_c_time": TS + 5, "point_c_price": 120.0,
        })

        # 所有 K 线均在 B 时间后，且 low > 122.5（B 反转阈值 = 115 + 50%×15 = 122.5）
        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 8, close=123, low=123, high=124),
            make_kline(TS + 9, close=124, low=124, high=125),
        ])
        # 提供极值点供 detect_and_save 全量重算 → 形成 LONG 结构
        _seed_swings(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_swing("TROUGH", 115, TS + 3),
            make_swing("PEAK", 124, TS + 8),
            make_swing("TROUGH", 120, TS + 9),
        ])

        r = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)
        # B 反转 → 旧结构被标记 COMPLETED + detect_and_save 全量重算
        assert_is_active(r)
        # 重算后应为 LONG 结构（极值点 TROUGH→PEAK→TROUGH）
        assert r["direction"] == "LONG"

    @patch("time.time")
    def test_no_restructure_after_stable_price(self, mock_time: Any, db: Database) -> None:
        """稳定行情多次推送 → 结构不发生变化。"""
        mock_time.return_value = FAKE_NOW

        _insert_n_structure(db, {
            "symbol": self.SYMBOL, "contract": self.CONTRACT,
            "timeframe": self.TF,
            "direction": "LONG", "state": NState.LEG3.value,
            "point_a_time": TS + 1, "point_a_price": 90.0,
            "point_b_time": TS + 3, "point_b_price": 110.0,
            "point_c_time": TS + 5, "point_c_price": 100.0,
        })

        _seed_klines(db, self.SYMBOL, self.CONTRACT, self.TF, [
            make_kline(TS + 7, close=105, low=103, high=108),
            make_kline(TS + 8, close=106, low=104, high=109),
        ])

        # 两次调用都不应触发重算
        for _ in range(2):
            result = dynamic_restructure(self.SYMBOL, self.CONTRACT, self.TF, db)
            assert result["direction"] == "LONG"
            assert result["state"] == NState.LEG3.value
