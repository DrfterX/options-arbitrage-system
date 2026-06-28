#!/usr/bin/env python3
"""
夜盘时段 K 线数据校验脚本 — P0 子任务 1

抽样品种（8 个）：
- 有夜盘品种（6 个）：RB（上期所 21-23）、CU（上期所 21-01）、AU（上期所 21-02:30）、
  SC（能源 21-02:30）、MA（郑商所 21-23）、I（大商所 21-23）
- 无夜盘品种（2 个）：AP（郑商所）、CJ（郑商所）

校验内容：
1. 逻辑校验：high >= low, high >= open/close
2. 夜盘时段校验：有夜盘品种的 K 线 timestamp 应在对应夜盘时段内
3. 无夜盘品种校验：无夜盘品种不应包含 21:00 之后的 K 线
"""

import sqlite3
import sys
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))

# 数据库路径 — 包含真实数据的 379MB 数据库
DB_PATH = "projects/options_arbitrage_system/trading_system.db"

# 品种列表
NIGHT_SYMBOLS = ["RB", "CU", "AU", "SC", "MA", "I"]
NO_NIGHT_SYMBOLS = ["AP", "CJ"]
ALL_SYMBOLS = NIGHT_SYMBOLS + NO_NIGHT_SYMBOLS

# 夜盘时段定义（BJT 小时，浮点数以处理 02:30 等非整点结束）
# key=symbol, value=(start_hour, end_hour_float) 注意 end_hour 可能跨天
NIGHT_SESSIONS = {
    "RB": (21, 23),     # 21:00-23:00
    "CU": (21, 25),     # 21:00-次日01:00 (以 24h 计为 25)
    "AU": (21, 26.5),   # 21:00-次日02:30 (以 24h 计为 26.5)
    "SC": (21, 26.5),   # 21:00-次日02:30
    "MA": (21, 23),     # 21:00-23:00
    "I":  (21, 23),     # 21:00-23:00
}


def _to_bjt_str(ts: int) -> str:
    """Unix timestamp (UTC 秒) -> BJT 字符串 YYYY-MM-DD HH:MM"""
    dt = datetime.fromtimestamp(ts, tz=BJT)
    return dt.strftime("%Y-%m-%d %H:%M")


def _to_bjt_dt(ts: int) -> datetime:
    """Unix timestamp -> BJT datetime"""
    return datetime.fromtimestamp(ts, tz=BJT)


def _get_contract(conn, symbol: str) -> str:
    """获取品种的主力合约代码"""
    cur = conn.execute(
        "SELECT contract FROM futures_klines WHERE symbol=? ORDER BY timestamp DESC LIMIT 1",
        (symbol,)
    )
    row = cur.fetchone()
    if row:
        return row["contract"]
    # 回退：尝试任意合约
    cur = conn.execute(
        "SELECT contract FROM futures_klines WHERE symbol=? LIMIT 1",
        (symbol,)
    )
    row = cur.fetchone()
    return row["contract"] if row else None


def _get_recent_klines(conn, symbol: str, contract: str, days: int = 3) -> list:
    """获取最近 N 个交易日的 15m K 线（按 timestamp 倒序取最后 3 天）"""
    now_bjt = datetime.now(tz=BJT)
    start_bjt = now_bjt - timedelta(days=days * 2)  # 放宽到 2 倍天数以覆盖周末/节假日
    start_ts = int(start_bjt.timestamp())
    
    cur = conn.execute(
        """SELECT timestamp, open, high, low, close, volume
           FROM futures_klines
           WHERE symbol=? AND contract=? AND timeframe='15m' AND timestamp >= ?
           ORDER BY timestamp ASC""",
        (symbol, contract, start_ts)
    )
    rows = cur.fetchall()
    
    result = []
    for row in rows:
        result.append({
            "ts": row["timestamp"],
            "o": row["open"],
            "h": row["high"],
            "l": row["low"],
            "c": row["close"],
            "v": row["volume"]
        })
    return result


def _logical_checks(klines: list, symbol: str, date_key: str, errors: list) -> None:
    """对一组K线做逻辑校验: high>=low, open在合理范围等"""
    for k in klines:
        if k["h"] < k["l"]:
            errors.append(f"[{symbol}] {date_key} {_to_bjt_str(k['ts'])}: high({k['h']}) < low({k['l']})")
        if k["h"] < k["o"] or k["h"] < k["c"]:
            errors.append(f"[{symbol}] {date_key} {_to_bjt_str(k['ts'])}: high < open/close")


def _check_night_session_hours(klines: list, symbol: str, has_night: bool, errors: list) -> None:
    """
    校验夜盘时段：
    - 有夜盘品种：K 线时间应在对应夜盘时段内
    - 无夜盘品种：不应包含 21:00 后的 K 线
    """
    night_hours = NIGHT_SESSIONS.get(symbol)
    
    for k in klines:
        dt = _to_bjt_dt(k["ts"])
        hour = dt.hour
        minute = dt.minute
        hour_float = hour + minute / 60.0
        
        # 白天时段 9:00-15:00 跳过（日盘正常，15:00 是收盘K线）
        if 9 <= hour_float <= 15:
            continue
        
        local_time_str = dt.strftime("%H:%M")
        date_str = dt.strftime("%Y-%m-%d")
        
        if has_night and night_hours:
            start_h, end_h = night_hours
            # 判断是否在夜盘时段内
            if start_h <= 23:  # 同一天结束（RB/MA/I: 21-23）
                in_session = start_h <= hour_float <= end_h
            else:  # 跨天 — CU(end_h=25 → 01:00), AU/SC(end_h=26.5 → 02:30)
                in_session = hour_float >= start_h or hour_float <= (end_h - 24)
            
            if not in_session:
                # 非夜盘时段的 K 线（且不是日盘 9-15）— 15:00-21:00 休市
                if 15 < hour_float < 21:
                    errors.append(f"[{symbol}] {date_str} {local_time_str}: 休市时段(15:00-21:00)不应有K线数据")
        else:
            # 无夜盘品种 — 不应有 21:00 后的数据
            if hour_float >= 21 or hour_float < 3:
                errors.append(f"[{symbol}] {date_str} {local_time_str}: 无夜盘品种不应有夜盘时段K线")


def run_validation() -> dict:
    """运行完整的夜盘时段校验"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    results = {
        "total_errors": 0,
        "breakdown": {}
    }
    
    for symbol in ALL_SYMBOLS:
        contract = _get_contract(conn, symbol)
        if not contract:
            results["breakdown"][symbol] = {"status": "SKIP", "error": f"未找到合约数据"}
            continue
        
        klines = _get_recent_klines(conn, symbol, contract, days=3)
        if not klines:
            results["breakdown"][symbol] = {"status": "SKIP", "error": f"未找到最近K线数据"}
            continue
        
        errors = []
        has_night = symbol in NIGHT_SYMBOLS
        
        # 按交易日分组（BJT 日期）
        date_groups = {}
        for k in klines:
            dt = _to_bjt_dt(k["ts"])
            date_key = dt.strftime("%Y-%m-%d")
            if date_key not in date_groups:
                date_groups[date_key] = []
            date_groups[date_key].append(k)
        
        for date_key, day_klines in date_groups.items():
            _logical_checks(day_klines, symbol, date_key, errors)
            _check_night_session_hours(day_klines, symbol, has_night, errors)
        
        results["breakdown"][symbol] = {
            "status": "FAIL" if errors else "PASS",
            "contract": contract,
            "kline_count": len(klines),
            "trading_days": list(date_groups.keys()),
            "errors": errors
        }
        results["total_errors"] += len(errors)
    
    conn.close()
    return results


def print_results(results: dict) -> None:
    """输出可读的校验结果"""
    print("=" * 60)
    print("夜盘时段 K 线数据校验结果")
    print("=" * 60)
    
    for symbol, info in results["breakdown"].items():
        print(f"\n--- {symbol} ({info.get('status', 'UNKNOWN')}) ---")
        if "error" in info:
            print(f"  ⚠  {info['error']}")
            continue
        print(f"  合约: {info['contract']}")
        print(f"  K 线数: {info['kline_count']}")
        print(f"  交易日: {', '.join(info['trading_days'])}")
        if info["errors"]:
            for err in info["errors"]:
                print(f"  ✗ {err}")
        else:
            print(f"  ✓ 无错误")
    
    print("\n" + "=" * 60)
    print(f"总计错误数: {results['total_errors']}")
    if results['total_errors'] == 0:
        print("✓ 所有校验通过")
    else:
        print(f"✗ {results['total_errors']} 个错误需要处理")
    print("=" * 60)


if __name__ == "__main__":
    results = run_validation()
    print_results(results)
    sys.exit(1 if results["total_errors"] > 0 else 0)
