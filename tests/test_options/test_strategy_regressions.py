"""测试 options/multi_strategy.py 的边界保证金判定与 pnl_report 合约分组。"""

from pathlib import Path

import pytest

from config.contracts import ContractRegistry
from options.multi_strategy import _calc_iron_condor, _calc_short_strangle
from options.pnl_report import _fetch_signals_grouped, build_pnl_report
from options.ratio_spread import OptionLeg


def make_leg(
    strike: float,
    mid: float,
    delta: float,
    gamma: float = 0.01,
    theta: float = -0.1,
    vega: float = 0.2,
    oi: int = 500,
) -> OptionLeg:
    """构造用于策略计算的最小 OptionLeg。"""
    return OptionLeg(
        strike=strike,
        bid=mid * 0.95,
        ask=mid * 1.05,
        mid=mid,
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        iv=0.3,
        oi=oi,
        volume=100,
    )


class TestMultiStrategyMarginBoundary:
    def _make_registry(self) -> ContractRegistry:
        """使用临时 sqlite 文件，避免 :memory: 多连接导致 symbols 表丢失。"""
        return ContractRegistry(str(Path("/tmp/options_arbitrage_test_contracts.db")))

    def test_short_strangle_rejects_when_raw_margin_hits_limit(self) -> None:
        """raw_margin 恰好达到 MAX_MARGIN 时应拒绝，而不是先截断再继续。"""
        registry = self._make_registry()
        call = make_leg(strike=4200, mid=20, delta=0.20)
        put = make_leg(strike=3600, mid=20, delta=-0.20)

        result = _calc_short_strangle(
            symbol="RB",
            contract="rb2601",
            underlying=3900,
            iv_avg=0.30,
            dte=30,
            call=call,
            put=put,
            net_delta_in=0.0,
            registry=registry,
        )

        assert result is None

    def test_short_strangle_accepts_when_raw_margin_below_limit(self) -> None:
        """raw_margin 低于 MAX_MARGIN 时应保留真实值并继续计算。"""
        registry = self._make_registry()
        call = make_leg(strike=4200, mid=10, delta=0.20)
        put = make_leg(strike=3600, mid=10, delta=-0.20)

        result = _calc_short_strangle(
            symbol="RB",
            contract="rb2601",
            underlying=3900,
            iv_avg=0.30,
            dte=30,
            call=call,
            put=put,
            net_delta_in=0.0,
            registry=registry,
        )

        assert result is not None
        assert result["margin_required"] == 9950
        assert result["net_gamma"] == pytest.approx(-0.02, abs=1e-6)

    def test_iron_condor_rejects_when_raw_margin_hits_limit(self) -> None:
        """iron condor 的 raw_margin 恰好达到 MAX_MARGIN 时也应拒绝。"""
        registry = self._make_registry()
        short_put = make_leg(strike=3600, mid=12, delta=-0.20)
        long_put = make_leg(strike=2600, mid=2, delta=-0.05)
        short_call = make_leg(strike=4200, mid=12, delta=0.20)
        long_call = make_leg(strike=5200, mid=2, delta=0.05)

        result = _calc_iron_condor(
            symbol="RB",
            contract="rb2601",
            underlying=3900,
            iv_avg=0.30,
            dte=30,
            short_put=short_put,
            long_put=long_put,
            short_call=short_call,
            long_call=long_call,
            call_wing=1000,
            put_wing=1000,
            registry=registry,
        )

        assert result is None

    def test_iron_condor_accepts_when_raw_margin_below_limit_and_exposes_net_gamma(self) -> None:
        """iron condor 在保证金低于阈值时应通过，并输出 net_gamma。"""
        registry = self._make_registry()
        short_put = make_leg(strike=3600, mid=12, delta=-0.20, gamma=0.02)
        long_put = make_leg(strike=2700, mid=2, delta=-0.05, gamma=0.01)
        short_call = make_leg(strike=4200, mid=12, delta=0.20, gamma=0.02)
        long_call = make_leg(strike=5100, mid=2, delta=0.05, gamma=0.01)

        result = _calc_iron_condor(
            symbol="RB",
            contract="rb2601",
            underlying=3900,
            iv_avg=0.30,
            dte=30,
            short_put=short_put,
            long_put=long_put,
            short_call=short_call,
            long_call=long_call,
            call_wing=900,
            put_wing=900,
            registry=registry,
        )

        assert result is not None
        assert result["margin_required"] == 9000
        assert result["net_gamma"] == pytest.approx(-0.02, abs=1e-6)


class TestPnlReportGrouping:
    def _insert_signal(
        self,
        temp_db,
        *,
        symbol: str,
        contract: str,
        strategy: str,
        futures_price: float,
        iv_avg: float,
        created_at: str,
    ) -> None:
        with temp_db.get_conn() as conn:
            conn.execute(
                """
                INSERT INTO options_signals (
                    symbol, contract, strategy, signal_type,
                    futures_price, iv_avg,
                    net_delta, net_theta, net_vega, net_gamma,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol,
                    contract,
                    strategy,
                    "WATCH",
                    futures_price,
                    iv_avg,
                    0.05,
                    -0.10,
                    -0.20,
                    0.01,
                    created_at,
                ),
            )
            conn.commit()

    def test_fetch_groups_by_symbol_contract_strategy(self, temp_db) -> None:
        """同 symbol+strategy 但不同 contract 必须分成不同组。"""
        self._insert_signal(
            temp_db,
            symbol="RB",
            contract="rb2601",
            strategy="ratio_spread",
            futures_price=3500,
            iv_avg=0.30,
            created_at="2026-06-20 09:00:00",
        )
        self._insert_signal(
            temp_db,
            symbol="RB",
            contract="rb2605",
            strategy="ratio_spread",
            futures_price=3520,
            iv_avg=0.31,
            created_at="2026-06-20 10:00:00",
        )

        groups = _fetch_signals_grouped(temp_db, limit_per_group=2)

        assert len(groups) == 2
        assert "RB|rb2601|ratio_spread" in groups
        assert "RB|rb2605|ratio_spread" in groups

    def test_build_report_does_not_cross_match_different_contracts(self, temp_db) -> None:
        """归因报告只能匹配同一 contract 的相邻信号。"""
        self._insert_signal(
            temp_db,
            symbol="RB",
            contract="rb2601",
            strategy="ratio_spread",
            futures_price=3500,
            iv_avg=0.30,
            created_at="2026-06-20 09:00:00",
        )
        self._insert_signal(
            temp_db,
            symbol="RB",
            contract="rb2601",
            strategy="ratio_spread",
            futures_price=3550,
            iv_avg=0.32,
            created_at="2026-06-21 09:00:00",
        )
        self._insert_signal(
            temp_db,
            symbol="RB",
            contract="rb2605",
            strategy="ratio_spread",
            futures_price=3600,
            iv_avg=0.35,
            created_at="2026-06-21 10:00:00",
        )

        report = build_pnl_report(temp_db, limit_groups=10, multiplier_override=10)

        assert report["total_records"] == 1
        assert report["attributions"][0]["contract"] == "rb2601"

    def test_build_report_skips_mismatched_group_entries_defensively(self, monkeypatch, temp_db) -> None:
        """即使分组函数失效，build_pnl_report 也要跳过 contract/strategy 不一致的数据。"""
        bad_groups = {
            "RB|broken|ratio_spread": [
                {
                    "symbol": "RB",
                    "contract": "rb2601",
                    "strategy": "ratio_spread",
                    "futures_price": 3500,
                    "iv_avg": 0.30,
                    "net_delta": 0.05,
                    "net_theta": -0.10,
                    "net_vega": -0.20,
                    "net_gamma": 0.01,
                    "created_at": "2026-06-20 09:00:00",
                },
                {
                    "symbol": "RB",
                    "contract": "rb2605",
                    "strategy": "iron_condor",
                    "futures_price": 3550,
                    "iv_avg": 0.32,
                    "net_delta": 0.04,
                    "net_theta": -0.11,
                    "net_vega": -0.21,
                    "net_gamma": 0.02,
                    "created_at": "2026-06-21 09:00:00",
                },
            ]
        }
        monkeypatch.setattr("options.pnl_report._fetch_signals_grouped", lambda db, limit_per_group=2: bad_groups)

        report = build_pnl_report(temp_db, limit_groups=10, multiplier_override=10)

        assert report["total_records"] == 0
        assert report["errors"]
        assert "分组数据不一致" in report["errors"][0]
