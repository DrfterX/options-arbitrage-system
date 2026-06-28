"""
节假日夜盘取消逻辑验证 — 窄范围单元测试

只验证：
1. core.market_calendar.has_night_session() 在 2026 春节/国庆前后的返回值
2. futures.aggregator._is_trading_boundary() 在跨节假日边界的时序行为

不碰数据库、不刷全量数据。
"""

import pytest
from datetime import date, datetime, timezone, timedelta
from futures.aggregator import (
    _is_trading_boundary,
    _trading_breaks_for_symbol,
    _NIGHT_CLOSE_2300,
    _NIGHT_CLOSE_0100,
    _NIGHT_CLOSE_0230,
    _NIGHT_START,
    _DAY_OPEN_DEFAULT,
)
from core.market_calendar import has_night_session, is_trading_day

# ============================================================
# 辅助函数
# ============================================================

BJT = timezone(timedelta(hours=8))


def bjt_ts(year: int, month: int, day: int, hour: int = 0, minute: int = 0,
           second: int = 0) -> int:
    """北京时间 → Unix 时间戳（UTC）"""
    return int(datetime(year, month, day, hour, minute, second,
                        tzinfo=BJT).timestamp())


# ============================================================
# 1. has_night_session() 节假日校验
# ============================================================

class TestHasNightSessionHolidays:
    """验证 has_night_session() 在 2026 法定长假前后的返回值。

    规则：如果明天（次日）不是交易日，则今晚没有夜盘。
    注意：非交易日 (is_trading_day=False) 自动返回 False。
    """

    # ── 春节 2026-02-15~2026-02-23 ──

    def test_spring_festival_eve(self):
        """春节前最后交易日 2026-02-13（周五）→ 夜盘取消"""
        assert is_trading_day(date(2026, 2, 13)) is True
        assert has_night_session(date(2026, 2, 13)) is False

    def test_spring_festival_before_eve(self):
        """2026-02-12（周四）→ 正常有夜盘"""
        assert has_night_session(date(2026, 2, 12)) is True

    def test_spring_festival_after(self):
        """春节后首日 2026-02-24（周二）→ 正常有夜盘"""
        assert has_night_session(date(2026, 2, 24)) is True

    def test_spring_festival_mid_holiday(self):
        """假期中 2026-02-16（周一）→ 非交易日，无夜盘"""
        assert is_trading_day(date(2026, 2, 16)) is False
        assert has_night_session(date(2026, 2, 16)) is False

    # ── 国庆 2026-10-01~2026-10-07（推测）──

    def test_national_day_eve(self):
        """国庆前最后交易日 2026-09-30（周三）→ 夜盘取消"""
        assert is_trading_day(date(2026, 9, 30)) is True
        assert has_night_session(date(2026, 9, 30)) is False

    def test_national_day_before_eve(self):
        """2026-09-29（周二）→ 正常有夜盘"""
        assert has_night_session(date(2026, 9, 29)) is True

    def test_national_day_after(self):
        """国庆后首日 2026-10-08（周四）→ 正常有夜盘"""
        assert has_night_session(date(2026, 10, 8)) is True

    def test_national_day_mid_holiday(self):
        """假期中 2026-10-04（周日）→ 非交易日，无夜盘"""
        assert is_trading_day(date(2026, 10, 4)) is False
        assert has_night_session(date(2026, 10, 4)) is False

    # ── 常规周末 ──

    def test_friday_night_cancelled(self):
        """常规周五也因周六非交易日而无夜盘"""
        # 2026-10-09 是周五，次周六日非交易
        assert has_night_session(date(2026, 10, 9)) is False

    def test_non_trading_day_no_night(self):
        """非交易日本身没有夜盘概念（周日自动返回 False）"""
        # 不管明天是否是交易日，如果今天不是交易日，has_night_session 返回 False
        assert has_night_session(date(2026, 2, 8)) is False  # Sunday

    # ── 节前 vs 节后边界 ──

    def test_eve_is_not_regular_friday_for_spring(self):
        """春节前周五 2/13 夜盘取消 → 既是周五又是节前，结果一致"""
        assert has_night_session(date(2026, 2, 13)) is False

    def test_return_from_spring_festival_monday_night(self):
        """节后返回 2/24（周二），前一晚（周一 2/23）因假日无需特殊处理"""
        # 2/23 是假期最后一天，非交易日 → 无夜盘
        assert is_trading_day(date(2026, 2, 23)) is False
        assert has_night_session(date(2026, 2, 23)) is False


# ============================================================
# 2. _is_trading_boundary() 跨节假日边界行为
# ============================================================

class TestIsTradingBoundaryAcrossHolidays:
    """验证 _is_trading_boundary() 在跨节假日场景下的判断。

    _is_trading_boundary 检测两种边界：
    a) 跨天边界（夜盘连续跨午夜除外）
    b) 同天内的休盘区间（10:15-10:30, 11:30-13:30, 夜盘收→次日日开盘）

    注意：同日盘→夜盘（15:00→21:00）不通过 _is_trading_boundary 检测，
    而是由聚合器的 aligned_ts 变化自动处理的。
    """

    def setup_method(self):
        """获取 RB（23:00 夜盘品种）的交易 break 列表"""
        self.breaks_rb = _trading_breaks_for_symbol("RB")

    # ── 正常场景 ──

    def test_normal_night_to_day_boundary(self):
        """正常夜盘结束→次日日盘：22:45→次日09:00 跨天 → 是边界"""
        ts1 = bjt_ts(2026, 2, 12, 22, 45)   # 夜盘最后一根
        ts2 = bjt_ts(2026, 2, 13, 9, 0)      # 次日日盘第一根
        assert _is_trading_boundary(ts1, ts2, self.breaks_rb, _NIGHT_CLOSE_2300) is True

    def test_within_night_session_no_boundary(self):
        """同一夜盘内（跨午夜不中断）：22:30→22:45 → 非边界"""
        ts1 = bjt_ts(2026, 2, 12, 22, 30)
        ts2 = bjt_ts(2026, 2, 12, 22, 45)
        assert _is_trading_boundary(ts1, ts2, self.breaks_rb, _NIGHT_CLOSE_2300) is False

    def test_within_day_session_no_boundary(self):
        """同日盘内：10:00→10:15 → 非边界"""
        ts1 = bjt_ts(2026, 2, 12, 10, 0)
        ts2 = bjt_ts(2026, 2, 12, 10, 15)
        assert _is_trading_boundary(ts1, ts2, self.breaks_rb, _NIGHT_CLOSE_2300) is False

    def test_day_break_1015_to_1030(self):
        """日盘休盘 10:15-10:30：10:00→10:45 → 是边界"""
        ts1 = bjt_ts(2026, 2, 12, 10, 0)
        ts2 = bjt_ts(2026, 2, 12, 10, 45)
        assert _is_trading_boundary(ts1, ts2, self.breaks_rb, _NIGHT_CLOSE_2300) is True

    def test_lunch_break_boundary(self):
        """午休 11:30-13:30：11:15→13:45 → 是边界"""
        ts1 = bjt_ts(2026, 2, 12, 11, 15)
        ts2 = bjt_ts(2026, 2, 12, 13, 45)
        assert _is_trading_boundary(ts1, ts2, self.breaks_rb, _NIGHT_CLOSE_2300) is True

    # ── 跨春节假期场景 ──

    def test_spring_festival_gap_is_boundary(self):
        """春节假期跨多日：2/13 日盘→2/24 日盘 → 是边界"""
        ts1 = bjt_ts(2026, 2, 13, 14, 45)   # 节前最后一根 15m
        ts2 = bjt_ts(2026, 2, 24, 9, 0)      # 节后第一根
        assert _is_trading_boundary(ts1, ts2, self.breaks_rb, _NIGHT_CLOSE_2300) is True

    def test_spring_festival_eve_last_kline(self):
        """春节前最后交易日 2/13 日盘最后两根：14:30→14:45 → 非边界"""
        ts1 = bjt_ts(2026, 2, 13, 14, 30)
        ts2 = bjt_ts(2026, 2, 13, 14, 45)
        assert _is_trading_boundary(ts1, ts2, self.breaks_rb, _NIGHT_CLOSE_2300) is False

    # ── 跨国庆假期场景 ──

    def test_national_day_gap_is_boundary(self):
        """国庆假期跨多日：9/30 日盘收盘→10/8 日盘开盘 → 是边界"""
        ts1 = bjt_ts(2026, 9, 30, 14, 45)   # 节前最后一根
        ts2 = bjt_ts(2026, 10, 8, 9, 0)      # 节后第一根
        assert _is_trading_boundary(ts1, ts2, self.breaks_rb, _NIGHT_CLOSE_2300) is True

    # ── 跨午夜品种（CU 01:00 收盘）──

    def test_cu_midnight_no_boundary_within_session(self):
        """CU 夜盘跨午夜：23:00→次日 00:30（同一夜盘）→ 非边界"""
        breaks_cu = _trading_breaks_for_symbol("CU")
        ts1 = bjt_ts(2026, 2, 12, 23, 30)
        ts2 = bjt_ts(2026, 2, 13, 0, 30)
        assert _is_trading_boundary(ts1, ts2, breaks_cu, _NIGHT_CLOSE_0100) is False

    def test_cu_midnight_to_day_boundary(self):
        """CU 夜盘收盘→日盘：00:45→09:00 跨天 → 是边界"""
        breaks_cu = _trading_breaks_for_symbol("CU")
        ts1 = bjt_ts(2026, 2, 13, 0, 45)    # 夜盘最后一根
        ts2 = bjt_ts(2026, 2, 13, 9, 0)      # 日盘第一根
        assert _is_trading_boundary(ts1, ts2, breaks_cu, _NIGHT_CLOSE_0100) is True

    # ── AG 02:30 收盘品种 ──

    def test_ag_deep_night_boundary(self):
        """AG 跨午夜：02:15→09:00 跨天 → 是边界"""
        breaks_ag = _trading_breaks_for_symbol("AG")
        ts1 = bjt_ts(2026, 2, 13, 2, 15)     # 夜盘最后一根
        ts2 = bjt_ts(2026, 2, 13, 9, 0)       # 日盘第一根
        assert _is_trading_boundary(ts1, ts2, breaks_ag, _NIGHT_CLOSE_0230) is True

    def test_ag_deep_night_within_session(self):
        """AG 同一夜盘跨午夜：23:00→次日 02:00 → 非边界"""
        breaks_ag = _trading_breaks_for_symbol("AG")
        ts1 = bjt_ts(2026, 2, 12, 23, 30)
        ts2 = bjt_ts(2026, 2, 13, 2, 0)
        assert _is_trading_boundary(ts1, ts2, breaks_ag, _NIGHT_CLOSE_0230) is False

    # ── ZCE 品种（23:00 夜盘收盘）──

    def test_zce_night_close_to_next_day(self):
        """ZCE 23:00 夜盘→次日日盘：23:15→次日09:00 跨天 → 是边界"""
        breaks_zce = _trading_breaks_for_symbol("MA")
        ts1 = bjt_ts(2026, 2, 12, 23, 15)   # ZCE 夜盘最后 15m
        ts2 = bjt_ts(2026, 2, 13, 9, 0)       # 次日日盘第一根

    def test_zce_within_night_session(self):
        """ZCE 同一夜盘内：22:00→22:30 → 非边界"""
        breaks_zce = _trading_breaks_for_symbol("MA")
        ts1 = bjt_ts(2026, 2, 12, 22, 0)
        ts2 = bjt_ts(2026, 2, 12, 22, 30)

    # ── 日盘→夜盘过渡（14:45→21:00 由 aligned_ts 处理，非 is_trading_boundary 覆盖）──

    def test_day_to_night_same_day_not_boundary(self):
        """同日 14:45→21:00 — _is_trading_boundary 不检测日盘→夜盘过渡"""
        # 这个过渡由聚合器的 aligned_ts 变化自动处理
        ts1 = bjt_ts(2026, 2, 12, 14, 45)
        ts2 = bjt_ts(2026, 2, 12, 21, 0)
        assert _is_trading_boundary(ts1, ts2, self.breaks_rb, _NIGHT_CLOSE_2300) is False


# ============================================================
# 3. has_night_session + _is_trading_boundary 集成校验
# ============================================================

class TestHolidayNightSessionIntegration:
    """综合验证：has_night_session 和 _is_trading_boundary 协同工作。

    模拟 K 线聚合在节假日附近的行为：
    1. 采集层根据 has_night_session() 决定是否请求夜盘数据
    2. 聚合层检测跨交易日边界
    """

    def test_spring_festival_data_flow(self):
        """春节场景验证：节前一天无夜盘数据满足预期"""
        eve = date(2026, 2, 13)
        after = date(2026, 2, 24)

        # 节前一天没有夜盘
        assert has_night_session(eve) is False

        # 节后首日正常有夜盘
        assert has_night_session(after) is True

        # 节前最后日盘 K 线与节后首日 K 线之间必然跨边界
        breaks = _trading_breaks_for_symbol("RB")
        ts_eve_close = bjt_ts(2026, 2, 13, 14, 45)
        ts_after_open = bjt_ts(2026, 2, 24, 9, 0)
        assert _is_trading_boundary(
            ts_eve_close, ts_after_open, breaks, _NIGHT_CLOSE_2300
        ) is True

    def test_national_day_data_flow(self):
        """国庆场景验证：节前一天无夜盘数据满足预期"""
        eve = date(2026, 9, 30)
        after = date(2026, 10, 8)

        assert has_night_session(eve) is False
        assert has_night_session(after) is True

        breaks = _trading_breaks_for_symbol("RB")
        ts_eve_close = bjt_ts(2026, 9, 30, 14, 45)
        ts_after_open = bjt_ts(2026, 10, 8, 9, 0)
        assert _is_trading_boundary(
            ts_eve_close, ts_after_open, breaks, _NIGHT_CLOSE_2300
        ) is True

    def test_regular_weekday_night_existence(self):
        """普通周中交易日（周四）：有夜盘 + 跨夜检测正常"""
        dt = date(2026, 2, 12)  # 周四
        assert has_night_session(dt) is True

        breaks = _trading_breaks_for_symbol("RB")
        # 夜盘最后一根（22:45）→ 次日日盘第一根（9:00）→ 跨边界
        ts_night_end = bjt_ts(2026, 2, 12, 22, 45)
        ts_next_day = bjt_ts(2026, 2, 13, 9, 0)
        assert _is_trading_boundary(
            ts_night_end, ts_next_day, breaks, _NIGHT_CLOSE_2300
        ) is True
