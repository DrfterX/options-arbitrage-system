"""
集中式交易日历 — 以四大期货交易所（上期所/大商所/郑商所/中金所）的
实际交易日数据为判断依据，数据源来自新浪财经（其交易日历即交易所公告汇总）。

数据获取方式：
  akshare.tool_trade_date_hist_sina()
  → 覆盖 1990-12-19 至今公开的所有交易日，包含年份跨度和调休补班

底层策略（多级降级）：
  1. AKShare 新浪日历（来源：交易所官方公告汇总）→ 最权威
  2. chinese_calendar 库（国务院公告 + 自动调休处理）→ 备选
  3. 纯周末判断（仅判周六日）→ 最终保底

可被 Python 代码 import 调用，也可以作为 CLI 脚本使用：

    python core/market_calendar.py                     # 判断今天
    python core/market_calendar.py today               # 今天是否有夜盘
    python core/market_calendar.py 2026-10-01          # 判断指定日期
    python core/market_calendar.py 2026-10-01 night    # 指定日期当天是否有夜盘

返回码：
  默认模式：0 = 交易日，1 = 非交易日
  night 模式：0 = 有夜盘，1 = 无夜盘
"""

import datetime
import logging
import os
import pickle
import sys
import time
from typing import Optional, Literal

import akshare as ak
import pandas as pd

logger = logging.getLogger(__name__)

# ============================================================
# 交易日数据缓存（避免每次判断都请求网络）
# ============================================================
_CACHE_FILE = os.path.join(os.path.dirname(__file__), ".trading_days_cache.pkl")
_CACHE_TTL = 86400 * 7  # 每周刷新一次（国务院/交易所节前1-2周出公告）


def _load_cached_trading_days() -> Optional[set[datetime.date]]:
    """从本地缓存加载交易日集合。"""
    try:
        if os.path.exists(_CACHE_FILE):
            mtime = os.path.getmtime(_CACHE_FILE)
            if time.time() - mtime < _CACHE_TTL:
                with open(_CACHE_FILE, "rb") as f:
                    return pickle.load(f)
    except Exception as e:
        logger.warning("交易日缓存读取失败: %s", e)
    return None


def _save_trading_days_cache(days: set[datetime.date]) -> None:
    """保存交易日集合到本地缓存。"""
    try:
        with open(_CACHE_FILE, "wb") as f:
            pickle.dump(days, f)
    except Exception as e:
        logger.warning("交易日缓存写入失败: %s", e)


def _fetch_trading_days_from_exchanges() -> set[datetime.date]:
    """
    通过 AKShare 获取新浪交易日历。
    新浪交易日历的数据来源 = 交易所官方公告汇总。

    返回：所有已知交易日的 set[datetime.date]
    """
    df: pd.DataFrame = ak.tool_trade_date_hist_sina()
    return set(df["trade_date"].tolist())


def _get_trading_days() -> set[datetime.date]:
    """获取交易日集合，优先走缓存。"""
    cached = _load_cached_trading_days()
    if cached is not None:
        return cached
    exchange_days = _fetch_trading_days_from_exchanges()
    _save_trading_days_cache(exchange_days)
    return exchange_days


# ============================================================
# 备选方案：chinese_calendar 库（国务院公告）
# ============================================================
try:
    from chinese_calendar import is_workday as _chinese_calendar_is_workday

    _HAS_CHINESE_CALENDAR = True
except ImportError:
    _HAS_CHINESE_CALENDAR = False

    def _chinese_calendar_is_workday(dt: datetime.date) -> bool:
        """降级：仅判断周末"""
        return dt.weekday() < 5


# ============================================================
# 公开 API
# ============================================================


def is_trading_day(dt: Optional[datetime.date] = None) -> bool:
    """判断 *dt*（默认今天）是否为中国期货交易日。

    数据来源优先级：
      1. 四大交易所官方交易日历（via AKShare 新浪财经，含调休补班）
      2. chinese_calendar 库（国务院公告，pip install chinese_calendar）
      3. 周末判断（仅过滤周六日）

    Returns:
        True = 期货交易日，False = 非交易日
    """
    if dt is None:
        dt = datetime.date.today()

    # ---- 策略 1：AKShare 交易所日历 ----
    try:
        exchange_days = _get_trading_days()
        return dt in exchange_days
    except Exception as e:
        logger.warning("AKShare 交易日历降级（策略1→策略2）: %s", e)

    # ---- 策略 2：chinese_calendar ----
    try:
        return _chinese_calendar_is_workday(dt)
    except Exception as e:
        logger.warning("chinese_calendar 降级（策略2→策略3）: %s", e)

    # ---- 策略 3：纯周末判断（保底）----
    return dt.weekday() < 5


def has_night_session(dt: Optional[datetime.date] = None) -> bool:
    """判断 *dt*（默认今天）是否有夜盘交易。

    规则：法定节假日/周末的前一个交易日，夜盘取消。
    即如果明天（次日）是非交易日，则今天没有夜盘。

    Returns:
        True = 有夜盘，False = 无夜盘（节前/周末前交易日）
    """
    if dt is None:
        dt = datetime.date.today()

    # 今天本身如果不是交易日，也谈不上夜盘
    if not is_trading_day(dt):
        return False

    # 明天如果是非交易日 → 今晚夜盘取消
    tomorrow = dt + datetime.timedelta(days=1)
    return is_trading_day(tomorrow)


# ============================================================
# 交易时段检测
# ============================================================

# 日盘交易时间窗口（北京时间）
# 上午连续：09:00-11:30（中间不拆分）
# 下午连续：13:30-15:00
_DAY_SESSION_WINDOWS = [
    (9 * 60 + 0, 11 * 60 + 30),    # 09:00-11:30
    (13 * 60 + 30, 15 * 60 + 0),    # 13:30-15:00
]

# 夜盘交易时间窗口（北京时间）
# 绝大多数品种统一 21:00-23:00
_NIGHT_SESSION_WINDOWS = [
    (21 * 60 + 0, 23 * 60 + 0),     # 21:00-23:00
]


def _current_bj_minutes() -> int:
    """返回当前北京时间距离 00:00 的分钟数。"""
    bj_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    return bj_now.hour * 60 + bj_now.minute


def get_current_session() -> Literal["day", "night", "closed"]:
    """判断当前所在的交易时段。

    返回:
        "day"   — 日盘交易时段（北京时间 09:00-11:30 或 13:30-15:00，且今天为交易日）
        "night" — 夜盘交易时段（北京时间 21:00-23:00，且今天有夜盘）
        "closed" — 非交易时段（非交易日 / 日盘间隙 / 夜盘结束后）
    """
    today = datetime.date.today()
    now_minutes = _current_bj_minutes()

    # 先检查是否在日盘窗口
    if is_trading_day(today):
        for start, end in _DAY_SESSION_WINDOWS:
            if start <= now_minutes < end:
                return "day"

    # 再检查是否在夜盘窗口（需要有夜盘的交易日）
    if has_night_session(today):
        for start, end in _NIGHT_SESSION_WINDOWS:
            if start <= now_minutes < end:
                return "night"

    return "closed"


def refresh_cache() -> None:
    """强制刷新交易日缓存（通常在每年国务院/交易所发布新公告后手动调用）。"""
    try:
        os.remove(_CACHE_FILE)
    except Exception as e:
        logger.warning("刷新缓存失败: %s", e)


# ============================================================
# CLI 入口
# ============================================================


def main() -> int:
    mode = "trading_day"
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "today":
            dt = datetime.date.today()
            mode = "night"
        elif arg == "night" and len(sys.argv) > 2:
            dt = datetime.date.fromisoformat(sys.argv[2])
            mode = "night"
        else:
            dt = datetime.date.fromisoformat(arg)
    else:
        dt = datetime.date.today()

    if mode == "night":
        return 0 if has_night_session(dt) else 1
    return 0 if is_trading_day(dt) else 1


if __name__ == "__main__":
    sys.exit(main())
