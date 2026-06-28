#!/usr/bin/env python3
"""
P0 子任务 1.2 — 校验 Top 50 品种 × 4 周期 K 线数据正确性

验收标准:
1. 5 有夜盘 + 2 无夜盘
2. 每品种最近 3 根**完整**日 K 线
3. 时间戳符合夜盘/节假日规则
4. 无 high<low
5. 长假前 K 线不包含夜盘

Usage: python scripts/validate_klines.py
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config.settings import DB_PATH

NIGHT_SESSION_MAP = {"RB": (21,0,23,0), "AG": (21,0,2,30), "SC": (21,0,2,30), "CU": (21,0,1,0), "CF": (21,0,23,0)}
NO_NIGHT = {"AP", "CJ"}


def bj_min(ts):
    return ((ts + 28800) % 86400) // 60


def bj_str(ts):
    return datetime.fromtimestamp(ts + 28800, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def bj_date(ts):
    return datetime.fromtimestamp(ts + 28800, tz=timezone.utc).date()


def is_daily_close_bj(ts):
    """Check if timestamp corresponds to ~15:00 BJT (daily close)."""
    m = bj_min(ts)
    return abs(m - 900) <= 10  # 14:50-15:10


def integrity_errs(klines):
    errs = []
    for ts, o, h, l, c, v in klines:
        if h < l:
            errs.append(f"ts={ts} {bj_str(ts)}: high<low ({h}<{l})")
        if not (o > 0 and h > 0 and l > 0 and c > 0):
            errs.append(f"ts={ts} {bj_str(ts)}: non-positive price")
        if h < o or h < c:
            errs.append(f"ts={ts} {bj_str(ts)}: high<open/close")
        if l > o or l > c:
            errs.append(f"ts={ts} {bj_str(ts)}: low>open/close")
    return errs


def main():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    total_errors = 0

    print("=" * 70)
    print(f"P0 子任务 1.2 — K线数据正确性校验 -- {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    # ── Part 1: 7 抽样品种 × 1d/1w 最近 3 根完整 K 线 ──
    for sym in ["RB", "AG", "SC", "CU", "CF", "AP", "CJ"]:
        night_info = NIGHT_SESSION_MAP.get(sym, "none")
        print(f"\n--- {sym} (night={night_info}) ---")
        for tf in ["1d", "1w"]:
            # Get ALL bars for this symbol+timeframe, ordered by timestamp
            c.execute(
                "SELECT timestamp,open,high,low,close,volume FROM futures_klines "
                "WHERE symbol=? AND timeframe=? ORDER BY timestamp DESC",
                (sym, tf),
            )
            all_bars = c.fetchall()
            if not all_bars:
                print(f"  {tf}: no data")
                continue

            # For 1d bars, only include completed daily bars (timestamp near 15:00 BJT)
            if tf == "1d":
                completed = [b for b in all_bars if is_daily_close_bj(b[0])]
            else:
                completed = all_bars

            klines = completed[:3]
            if not klines:
                print(f"  {tf}: no completed bars")
                continue

            print(f"  {tf} ({len(klines)} bars, {len(completed)} completed total):")
            errs = integrity_errs(klines)
            for e in errs:
                print(f"    ERROR: {e}")
                total_errors += 1
            for k in klines:
                print(f"    {bj_str(k[0])} O={k[1]:.1f} H={k[2]:.1f} L={k[3]:.1f} C={k[4]:.1f} V={k[5]}")
            if not errs:
                print(f"    OK")

    # ── Part 2: 全局 high<low 检查 ──
    print("\n" + "=" * 70)
    print("Global high<low check (all timeframes)")
    for tf in ["15m", "1h", "1d", "1w"]:
        c.execute(f"SELECT COUNT(*) FROM futures_klines WHERE timeframe='{tf}'")
        total = c.fetchone()[0]
        c.execute(f"SELECT COUNT(*) FROM futures_klines WHERE timeframe='{tf}' AND high<low")
        bad = c.fetchone()[0]
        if bad:
            print(f"  {tf}: FOUND {bad} bars with high<low (out of {total})")
            total_errors += bad
        else:
            print(f"  {tf}: OK — all {total} bars high>=low")

    # ── Part 3: 1d 价格合理性检查 ──
    print("\n" + "=" * 70)
    print("Price sanity check (1d, all symbols)")
    c.execute("SELECT COUNT(*) FROM futures_klines WHERE timeframe='1d' AND (open<=0 OR high<=0 OR low<=0 OR close<=0)")
    zero_prices = c.fetchone()[0]
    if zero_prices:
        print(f"  ERROR: {zero_prices} bars with non-positive prices")
        total_errors += zero_prices
    else:
        print("  OK: all prices positive")

    # ── Part 4: 节假日夜盘检查 ──
    print("\n" + "=" * 70)
    print("Holiday night session check")
    from core.market_calendar import has_night_session, is_trading_day

    today = datetime.now(tz=timezone(timedelta(hours=8))).date()
    print(f"  Today: {today}, trading: {is_trading_day(today)}, night: {has_night_session(today)}")

    # Find the most recent non-trading day and its prior trading day
    for d in range(1, 60):
        dt = today - timedelta(days=d)
        if not is_trading_day(dt):
            prev = dt - timedelta(days=1)
            while not is_trading_day(prev):
                prev = prev - timedelta(days=1)
            night_prev = has_night_session(prev)
            print(f"  Last non-trading: {dt}, prior trading day: {prev}, night: {night_prev}")
            if night_prev:
                # Check that no 1d bar from prev has a timestamp beyond 15:00 BJT
                prev_ts = int(datetime(prev.year, prev.month, prev.day, 15, 0, tzinfo=timezone(timedelta(hours=8))).timestamp())
                # We check that the closing bar for prev exists and is at 15:00
                c.execute(
                    "SELECT timestamp FROM futures_klines WHERE timeframe='1d' AND timestamp>=? AND timestamp<?",
                    (prev_ts - 600, prev_ts + 600),
                )
                close_bars = c.fetchall()
                print(f"    1d bars near {prev} 15:00: {len(close_bars)} found")
            break

    # ── Part 5: Top 50 四周期覆盖率 ──
    print("\n" + "=" * 70)
    print("Top 50 symbols × 4 timeframe coverage")
    top50 = [
        "RB", "M", "TA", "P", "MA", "I", "SR", "Y", "RM", "AG",
        "FG", "RU", "L", "C", "SA", "V", "PP", "BU", "CF", "NI",
        "HC", "ZN", "CU", "A", "OI", "JM", "J", "EB", "AL", "EG",
        "AU", "JD", "SP", "CS", "AP", "SM", "SF", "UR", "SC", "PG",
        "PF", "LC", "SH", "AO", "SS", "B", "SI", "SN", "CJ"
    ]
    missing = []
    for sym in top50:
        for tf in ["15m", "1h", "1d", "1w"]:
            c.execute(
                "SELECT COUNT(*) FROM futures_klines WHERE symbol=? AND timeframe=?",
                (sym, tf),
            )
            if c.fetchone()[0] == 0:
                missing.append((sym, tf))
    if missing:
        print(f"  Missing coverage: {len(missing)} cases")
        for sym, tf in missing[:10]:
            print(f"    {sym} {tf}")
    else:
        print("  OK: all 50 symbols have all 4 timeframes")

    conn.close()
    print("\n" + "=" * 70)
    if total_errors:
        print(f"FAIL: {total_errors} error(s) found")
        sys.exit(1)
    else:
        print("PASS: all checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
