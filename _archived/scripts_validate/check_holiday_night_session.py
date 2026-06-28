#!/usr/bin/env python3
"""
P0 子任务 3 - 节假日夜盘取消规则校验

检查 2026-02-13 （春节前最后交易日）的夜盘时段 K 线
根据规则，这一天夜盘应取消，有夜盘品种不应包含 21:00 后的 K 线
"""

import sqlite3
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))
DB_PATH = "projects/options_arbitrage_system/trading_system.db"

# 春节假期 2026-02-15 ~ 2026-02-23，最后交易日 2026-02-13（周五）
CHECK_DATE = "2026-02-13"  # BJT

def bjt_ts(year, month, day, hour=0, minute=0, second=0):
    return int(datetime(year, month, day, hour, minute, second, tzinfo=BJT).timestamp())

# 有夜盘品种：分别来自不同交易所
NIGHT_SYMBOLS_TO_CHECK = ["RB", "CU", "MA", "I", "SC", "AU"]
# 无夜盘品种
NO_NIGHT_SYMBOLS = ["AP", "CJ"]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# 2026-02-13 全天范围 (BJT)
day_start = bjt_ts(2026, 2, 13, 0, 0)
day_end = bjt_ts(2026, 2, 14, 0, 0)

holiday_name = "春节"
print("=" * 70)
print(f"节假日夜盘取消规则校验 — {CHECK_DATE} ({holiday_name}前最后交易日)")
print("=" * 70)

all_pass = True

# 1. 校验有夜盘品种
for symbol in NIGHT_SYMBOLS_TO_CHECK:
    rows = conn.execute(
        """SELECT timestamp, open, high, low, close, volume, contract
           FROM futures_klines
           WHERE symbol=? AND timeframe='15m' AND timestamp>=? AND timestamp<?
           ORDER BY timestamp""",
        (symbol, day_start, day_end)
    ).fetchall()
    
    if not rows:
        print(f"\n--- {symbol} ---")
        print(f"  ⚠ 未找到 {CHECK_DATE} 的 K 线数据")
        all_pass = False
        continue
    
    # 分析时间分布
    night_klines = []  # 21:00 之后的 K 线
    session_start = 21.0
    for r in rows:
        dt = datetime.fromtimestamp(r["timestamp"], tz=BJT)
        hour_float = dt.hour + dt.minute / 60.0
        if hour_float >= session_start or hour_float < 3:
            night_klines.append(dt)
    
    print(f"\n--- {symbol} ({rows[0]['contract']}) ---")
    print(f"  {CHECK_DATE} K线总数: {len(rows)}")
    
    if night_klines:
        print(f"  ✗ 发现 {len(night_klines)} 根夜盘时段 K线（应被取消）:")
        for dt in night_klines[:5]:
            print(f"    {dt.strftime('%H:%M')}")
        if len(night_klines) > 5:
            print(f"    ... 还有 {len(night_klines)-5} 样")
        all_pass = False
    else:
        print(f"  ✓ 无夜盘时段 K线（符合节假日取消规则）")

# 2. 校验无夜盘品种（不应受影响）
for symbol in NO_NIGHT_SYMBOLS:
    rows = conn.execute(
        """SELECT timestamp, open, high, low, close, volume, contract
           FROM futures_klines
           WHERE symbol=? AND timeframe='15m' AND timestamp>=? AND timestamp<?
           ORDER BY timestamp""",
        (symbol, day_start, day_end)
    ).fetchall()
    
    if not rows:
        print(f"\n--- {symbol} ---")
        print(f"  ⚠ 未找到 {CHECK_DATE} 的 K 线数据")
        all_pass = False
        continue
    
    night_klines = []
    for r in rows:
        dt = datetime.fromtimestamp(r["timestamp"], tz=BJT)
        hour_float = dt.hour + dt.minute / 60.0
        if hour_float >= 21 or hour_float < 3:
            night_klines.append(dt)
    
    print(f"\n--- {symbol} ({rows[0]['contract']}) ---")
    print(f"  {CHECK_DATE} K线总数: {len(rows)}")
    
    if night_klines:
        print(f"  ✗ 发现 {len(night_klines)} 根夜盘时段 K线（无夜盘品种不应有）:")
        for dt in night_klines[:3]:
            print(f"    {dt.strftime('%H:%M')}")
        all_pass = False
    else:
        print(f"  ✓ 正常，无夜盘时段 K线")

print()
print("=" * 70)
if all_pass:
    print("✓ 所有校验通过：节假日夜盘取消规则得到正确执行")
else:
    print(f"✗ 部分校验未通过，需要进一步分析")
print("=" * 70)

conn.close()
