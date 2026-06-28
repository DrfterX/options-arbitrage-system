"""
K线聚合引擎 — 从3分钟K线聚合生成15分钟→1小时→日线→周线。
v2: 交易时段感知聚合，支持各交易所不同夜盘/日盘切分。
所有函数通过 ``db: Database`` 参数访问数据库。
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from core.db import Database

logger = logging.getLogger(__name__)

# 各周期对应的秒数
PERIOD_SECONDS: Dict[str, int] = {
    "15m": 900,
    "1h": 3600,
    "1d": 86400,
    "1w": 604800,
}

# ---- 交易时段定义 ----
# 北京时间 (Asia/Shanghai) 的小时:分钟表示
# 各交易所/板块的夜间收盘时间不同

# 日盘共同时刻
_DAY_MORNING_START = (9, 0)     # 日盘上午开
_DAY_MORNING_BREAK = (10, 15)   # 上午休盘开始
_DAY_MORNING_RESUME = (10, 30)  # 上午休盘结束
_DAY_NOON_BREAK = (11, 30)     # 午休开始
_DAY_AFTERNOON_START = (13, 30) # 下午开盘
_DAY_CLOSE = (15, 0)            # 日盘收盘

# 夜盘收盘时间 (北京时间次日)
# key: 收盘时点; values: 适用交易所/品种集合示例
_NIGHT_CLOSE_2300 = 23 * 3600        # 23:00 (黑色/化工多数)
_NIGHT_CLOSE_0100 = 25 * 3600        # 01:00 (上期所有色)
_NIGHT_CLOSE_0230 = 26 * 3600 + 1800 # 02:30 (上期所贵金属/有色/INE原油)
_NIGHT_START = 21 * 3600             # 21:00 夜盘统一开盘

# 交易所→夜盘收盘秒(从当天0点算). CFFEX=0表示无夜盘
EXCHANGE_NIGHT_CLOSE: Dict[str, int] = {
    "SHFE": _NIGHT_CLOSE_0230,   # 默认按有色的2:30; 黑色品种需特殊处理
    "DCE": _NIGHT_CLOSE_2300,    # 23:00
    "CZCE": _NIGHT_CLOSE_2300,   # 23:00 (郑商所实际夜盘23:00收盘)
    "INE": _NIGHT_CLOSE_0230,    # 02:30
    "GFEX": 0,                   # 广期所无夜盘（如SI工业硅）
    "CFFEX": 0,                  # 无夜盘
}

# 部分品种夜盘收盘时间与交易所默认不同 (symbol → 夜盘收盘秒)
SYMBOL_NIGHT_CLOSE: Dict[str, int] = {
    # 上期所黑色/化工 → 23:00
    "RB": _NIGHT_CLOSE_2300, "HC": _NIGHT_CLOSE_2300,
    "BU": _NIGHT_CLOSE_2300, "FU": _NIGHT_CLOSE_2300,
    "RU": _NIGHT_CLOSE_2300, "NR": _NIGHT_CLOSE_2300,
    "SP": _NIGHT_CLOSE_2300, "BR": _NIGHT_CLOSE_2300,
    "SS": _NIGHT_CLOSE_2300,
    # 上期所有色品种 → 01:00
    "CU": _NIGHT_CLOSE_0100, "AL": _NIGHT_CLOSE_0100,
    "ZN": _NIGHT_CLOSE_0100, "PB": _NIGHT_CLOSE_0100,
    "NI": _NIGHT_CLOSE_0100, "SN": _NIGHT_CLOSE_0100,
    # 上期所有色/贵金属 → 02:30 (保持交易所默认)
    # 大商所多数 → 23:00 (保持交易所默认)
    "J": _NIGHT_CLOSE_2300, "JM": _NIGHT_CLOSE_2300,
    # 大商所豆类油脂 → 23:00
    # 郑商所 → 23:00 (品种级覆盖，已有7个CZCE品种在SYMBOL_NIGHT_CLOSE无则用交易所默认)
    # 无夜盘品种（在DCE/CZCE但有夜盘品种的交易所旗下）
    "JD": 0, "LH": 0,
    # SHFE 无夜盘品种 — 否则回退到 SHFE 默认的 02:30 会导致 K 线错误包含夜盘数据
    "AO": 0,
    "SF": 0, "SM": 0, "AP": 0, "CJ": 0,

    "ZC": _NIGHT_CLOSE_2300,  # 动力煤(已停但不影响)
}

# 日盘开盘时间 (CFFEX是9:30，其他是9:00)
_DAY_OPEN_CFFEX = 9 * 3600 + 1800  # 9:30
_DAY_OPEN_DEFAULT = 9 * 3600       # 9:00
CFFEX_SYMBOLS = {"IF", "IH", "IM", "IC", "TS", "TF", "T", "TL"}


def _get_exchange_night_close(symbol: str, exchange: str = "") -> int:
    """获取品种的夜盘收盘秒数（北京时间当天0点为基准）。0=无夜盘。"""
    if symbol in SYMBOL_NIGHT_CLOSE:
        return SYMBOL_NIGHT_CLOSE[symbol]
    if exchange and exchange in EXCHANGE_NIGHT_CLOSE:
        return EXCHANGE_NIGHT_CLOSE[exchange]
    return _NIGHT_CLOSE_2300  # 默认23:00（34/43夜盘品种）


def _trading_breaks_for_symbol(symbol: str, exchange: str = "") -> List[Tuple[int, int]]:
    """返回该品种的交易休盘区间 [(start_bj_sec, end_bj_sec), ...]。
    
    秒数统一为"北京时间当天秒数"，跨天休盘（夜盘收→日盘开）
    用次日秒数表示（如 23:00→次日09:00 表示为 (82800, 118800)）。
    """
    breaks = [
        # 日盘上午休盘 (同天)
        (_time_to_sec(*_DAY_MORNING_BREAK), _time_to_sec(*_DAY_MORNING_RESUME)),
        # 日盘午休 (同天)
        (_time_to_sec(*_DAY_NOON_BREAK), _time_to_sec(*_DAY_AFTERNOON_START)),
    ]
    
    night_close = _get_exchange_night_close(symbol, exchange)
    if night_close > 0:
        day_open = _DAY_OPEN_CFFEX if symbol in CFFEX_SYMBOLS else _DAY_OPEN_DEFAULT
        # 跨天：夜盘收盘 → 次日日盘开盘
        breaks.append((night_close, day_open + 86400))
    
    return breaks


def _time_to_sec(h: int, m: int) -> int:
    """北京时间 小时:分钟 → 当天秒数 (0~86399)"""
    return h * 3600 + m * 60


def _bj_seconds(timestamp: int) -> int:
    """Unix时间戳 → 北京时间当天的秒数 (0~86399)"""
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc) + timedelta(hours=8)
    return dt.hour * 3600 + dt.minute * 60 + dt.second


def _trading_date(ts: int) -> int:
    """返回时间戳对应的交易日YYYMMDD（北京时间夜盘21:00+归属下一日）。
    
    例：2026-06-26 01:00 BJ→20260626, 2026-06-26 22:00 BJ→20260627。
    使用整数键用于K线分组，避免浮点数/时间戳精度问题。
    """
    bj_dt = datetime.fromtimestamp(ts, tz=timezone.utc) + timedelta(hours=8)
    if bj_dt.hour >= 21:
        bj_dt += timedelta(days=1)
    return bj_dt.year * 10000 + bj_dt.month * 100 + bj_dt.day


def _is_trading_boundary(ts1: int, ts2: int, breaks: List[Tuple[int, int]],
                         night_close: int) -> bool:
    """检查 ts1→ts2 是否跨越了交易时段边界。
    
    使用绝对北京时间秒数比较（含日期），正确处理跨天边界。
    """
    dt1 = datetime.fromtimestamp(ts1, tz=timezone.utc) + timedelta(hours=8)
    dt2 = datetime.fromtimestamp(ts2, tz=timezone.utc) + timedelta(hours=8)
    
    # 1. 跨天（日期不同）
    if dt1.date() != dt2.date():
        # 夜盘延续到次日凌晨 (如 22:00→次日1:00) 不算跨天边界
        if night_close > 0:
            s1 = _bj_seconds(ts1)
            s2 = _bj_seconds(ts2)
            # 都在同一夜盘内（21:00开盘 ~ 夜盘收盘），不算跨天
            if s1 >= _NIGHT_START and s2 <= night_close and s2 < _DAY_OPEN_DEFAULT:
                return False
        return True
    
    # 2. 同天内检查休盘区间
    midnight1 = dt1.replace(hour=0, minute=0, second=0, microsecond=0)
    abs1 = dt1.hour * 3600 + dt1.minute * 60 + dt1.second
    abs2 = (dt2 - midnight1).total_seconds()
    
    for break_start, break_end in breaks:
        # 归一化到 ts1 当天：跨午夜break(>86400)减86400变成同天
        bs = break_start
        be = break_end
        day_base = (int(abs1) // 86400) * 86400
        while bs >= day_base + 86400:
            bs -= 86400
            be -= 86400
        # 只处理归一化后完全在ts1当天的break
        if be <= day_base + 86400 and abs1 <= bs and abs2 >= be:
            return True
    
    # 3. 夜盘收盘切分（同天场景：夜盘收盘后到日盘开盘前）
    if night_close > 0:
        nc = night_close % 86400
        if abs1 < nc and abs2 >= nc and abs2 < _NIGHT_START:
            return True
    
    return False


def _aggregate_bar(bars: List[Dict[str, Any]]) -> Dict[str, Any]:
    """将一组K线聚合为一根。"""
    if not bars:
        return {}
    return {
        "timestamp": bars[0]["timestamp"],
        "open": bars[0]["open"],
        "high": max(b["high"] for b in bars),
        "low": min(b["low"] for b in bars),
        "close": bars[-1]["close"],
        "volume": sum(b.get("volume", 0) or 0 for b in bars),
    }


def _get_klines(
    db: Database,
    symbol: str,
    contract: str,
    timeframe: str,
    limit: int = 2000,
) -> List[Dict[str, Any]]:
    """从数据库读取K线数据，按时间升序返回。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM futures_klines
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp DESC LIMIT ?""",
            (symbol, contract, timeframe, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def _batch_insert_klines(db: Database, rows: List[Dict[str, Any]]) -> None:
    """批量写入K线，INSERT OR REPLACE 允许更新已有K线（如周线跨日聚合更新）。"""
    if not rows:
        return
    with db.get_conn() as conn:
        conn.executemany(
            """INSERT OR REPLACE INTO futures_klines
               (symbol, contract, timeframe, timestamp, open, high, low, close, volume)
               VALUES (:symbol, :contract, :timeframe, :timestamp, :open, :high, :low, :close, :volume)""",
            rows,
        )
        conn.commit()


def _lookup_exchange(symbol: str) -> str:
    """从品种代码推断交易所（用于默认夜盘时间）。"""
    try:
        from config.contracts import ContractRegistry
        from config.settings import DB_PATH
        reg = ContractRegistry(str(DB_PATH))
        info = reg.get(symbol)
        if info:
            return info.get("exchange", "")
    except Exception:
        pass
    return ""


def aggregate_klines(
    symbol: str,
    contract: str,
    db: Database,
    from_tf: str = "3m",
    to_tf: str = "15m",
    limit: int = 2000,
) -> int:
    """交易时段感知的K线聚合。

    关键改进 vs v1:
    - 15m/1h 不再用纯数学时间对齐，改为检测交易时段边界
    - 夜盘收盘→日盘开盘自动切分
    - 日盘休盘（10:15/11:30）正确断K线
    - 不同品种不同夜盘收盘时间
    """
    src_klines = _get_klines(db, symbol, contract, from_tf, limit=limit)
    if not src_klines:
        return 0

    # 准备交易时段信息
    exchange = _lookup_exchange(symbol)
    night_close = _get_exchange_night_close(symbol, exchange)
    breaks = _trading_breaks_for_symbol(symbol, exchange)

    period = PERIOD_SECONDS.get(to_tf, 900)
    bars: List[Dict[str, Any]] = []
    current_group: List[Dict[str, Any]] = []
    current_aligned_ts: Optional[int] = None

    for k in src_klines:
        ts: int = k["timestamp"]

        if to_tf in ("15m", "1h"):
            # 交易时段感知的对齐
            aligned_ts = (ts // period) * period
            
            # 是否需要开始新K线？
            new_bar = False
            if current_aligned_ts is None:
                new_bar = True
            elif aligned_ts != current_aligned_ts:
                # 对齐区间变了 → 新周期
                new_bar = True
            # 检查是否跨交易边界（即使在同一对齐区间内）
            last_ts = current_group[-1]["timestamp"] if current_group else ts
            if not new_bar and _is_trading_boundary(last_ts, ts, breaks, night_close):
                new_bar = True

            if new_bar:
                if current_group:
                    bars.append(_aggregate_bar(current_group))
                current_group = [k]
                # 重新计算对齐（可能因边界而移位）
                current_aligned_ts = (ts // period) * period
            else:
                current_group.append(k)

        elif to_tf == "1d":
            # 日K：按交易日分组（夜盘21:00+归属下一交易日）
            trading_day = _trading_date(ts)
            if current_aligned_ts is None:
                current_aligned_ts = trading_day
                current_group.append(k)
            elif trading_day != current_aligned_ts:
                bars.append(_aggregate_bar(current_group))
                current_group = [k]
                current_aligned_ts = trading_day
            else:
                current_group.append(k)

        elif to_tf == "1w":
            # 使用北京时间（UTC+8）计算周起始，确保周日夜盘数据落入正确的周
            BJT_OFFSET = 8 * 3600
            bjt_ts = ts + BJT_OFFSET
            bjt_dt = datetime.fromtimestamp(bjt_ts, tz=timezone.utc)
            week_start = bjt_ts - (bjt_dt.weekday() * 86400) - bjt_dt.hour * 3600 - bjt_dt.minute * 60 - bjt_dt.second
            week_start -= BJT_OFFSET  # 转回 UTC 时间戳存储
            if week_start != current_aligned_ts:
                if current_group:
                    bars.append(_aggregate_bar(current_group))
                current_group = [k]
                current_aligned_ts = week_start
            else:
                current_group.append(k)

    if current_group:
        bars.append(_aggregate_bar(current_group))

    if not bars:
        return 0

    rows = [
        {
            "symbol": symbol,
            "contract": contract,
            "timeframe": to_tf,
            "timestamp": b["timestamp"],
            "open": b["open"],
            "high": b["high"],
            "low": b["low"],
            "close": b["close"],
            "volume": b["volume"],
        }
        for b in bars
    ]

    _batch_insert_klines(db, rows)
    logger.info(
        "聚合 %s %s (%s, 夜盘%s): %s→%s 写入 %d 条",
        symbol, contract, exchange,
        f"{night_close//3600:02d}:{(night_close%3600)//60:02d}" if night_close else "无",
        from_tf, to_tf, len(rows),
    )
    return len(rows)


def aggregate_all(symbol: str, contract: str, db: Database) -> Dict[str, int]:
    """按顺序聚合：3m→15m→1h→1d→1w。"""
    result: Dict[str, int] = {}
    steps = [("3m", "15m"), ("15m", "1h"), ("1h", "1d"), ("1d", "1w")]
    for from_tf, to_tf in steps:
        count = aggregate_klines(symbol, contract, db, from_tf, to_tf)
        result[f"{from_tf}_to_{to_tf}"] = count
    return result
