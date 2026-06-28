#!/usr/bin/env python3
"""Check raw DB timestamps vs normalized timestamps"""
import sqlite3
from datetime import datetime, timezone
from collections import Counter
utc = timezone.utc

conn = sqlite3.connect('trading_system.db')
conn.row_factory = sqlite3.Row

print('=== 1d bars in DB (samples, UTC) ===')
bars = conn.execute("SELECT symbol, timestamp, open, close FROM futures_klines WHERE timeframe='1d' LIMIT 20").fetchall()
for b in bars:
    tod = b['timestamp'] % 86400
    dt = datetime.fromtimestamp(b['timestamp'], tz=utc)
    print(f"  {b['symbol']}: {dt} (tod={tod}s = {tod//3600}:{(tod%3600)//60:02d} UTC)")

print()
print('=== N-structure point timestamps (1d, first 10, UTC) ===')
ns = conn.execute("SELECT symbol, point_a_time, point_b_time, point_c_time FROM futures_n_structures WHERE timeframe='1d' AND state!='COMPLETED' LIMIT 10").fetchall()
for n in ns:
    for label, ts in [('A', n['point_a_time']), ('B', n['point_b_time']), ('C', n['point_c_time'])]:
        if ts:
            tod = ts % 86400
            dt = datetime.fromtimestamp(ts, tz=utc)
            print(f"  {n['symbol']} {label}: {dt} (tod={tod}s = {tod//3600}:{(tod%3600)//60:02d} UTC)")

# Critical: Check if N-structure timestamps match the NORMALIZED time
_TARGET_HOUR_SEC = 20700
_MIDNIGHT_SEC = 57600
_BJ_OFFSET = 28800

normalized_time_tod = (_MIDNIGHT_SEC + _TARGET_HOUR_SEC) % 86400  # 78300 = 21:45 UTC

print(f"\n=== Normalized time-of-day: {normalized_time_tod}s = {normalized_time_tod//3600}:{(normalized_time_tod%3600)//60:02d} UTC ===")
print(f"=== Raw bar time-of-day (16:00 UTC): {_MIDNIGHT_SEC}s ===\n")

# How many N-structure timestamps match the normalized time?
n_all = conn.execute("SELECT point_a_time, point_b_time, point_c_time FROM futures_n_structures WHERE timeframe='1d' AND state!='COMPLETED'").fetchall()
total_ts = 0
at_normalized = 0
at_midnight = 0
at_others = Counter()
for n in n_all:
    for ts in [n['point_a_time'], n['point_b_time'], n['point_c_time']]:
        if ts:
            total_ts += 1
            tod = ts % 86400
            if tod == normalized_time_tod:
                at_normalized += 1
            elif tod == _MIDNIGHT_SEC:
                at_midnight += 1
            else:
                at_others[tod] += 1

print(f"=== 1d N-structure timestamps distribution ===")
print(f"Total: {total_ts}")
print(f"At normalized time (21:45 UTC = {normalized_time_tod}s): {at_normalized} ({at_normalized/total_ts*100:.1f}%)")
print(f"At midnight (16:00 UTC = {_MIDNIGHT_SEC}s): {at_midnight} ({at_midnight/total_ts*100:.1f}%)")
for tod, cnt in sorted(at_others.most_common(10)):
    print(f"  Other tod={tod}s ({tod//3600}:{(tod%3600)//60:02d} UTC): {cnt}")

conn.close()