#!/usr/bin/env python3
"""Check what timeframe the RB daily klines actually are"""
import sqlite3
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))

def bjt_str(ts):
    return datetime.fromtimestamp(ts, tz=BJT).strftime('%Y-%m-%d %H:%M:%S')

conn = sqlite3.connect('trading_system.db')
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT timeframe, timestamp, open, high, low, close "
    "FROM futures_klines "
    "WHERE symbol='RB' AND timestamp > 1000000000 "
    "ORDER BY timestamp DESC LIMIT 20"
).fetchall()

print("RB - last 20 klines (all timeframes):")
for r in rows:
    ts = bjt_str(r['timestamp'])
    print(f"{r['timeframe']:5s} | {ts} | O={r['open']:.1f} H={r['high']:.1f} L={r['low']:.1f} C={r['close']:.1f}")
print()

# Check 1d specifically
rows1d = conn.execute(
    "SELECT DISTINCT timestamp FROM futures_klines "
    "WHERE symbol='RB' AND timeframe='1d' AND timestamp > 1000000000 "
    "ORDER BY timestamp DESC LIMIT 10"
).fetchall()
print("RB - 1d timestamps:")
for r in rows1d:
    print(f"  {r['timestamp']} -> {bjt_str(r['timestamp'])}")

conn.close()
