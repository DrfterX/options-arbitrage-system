#!/usr/bin/env python3
"""P0 子任务 1.3 — 校验 K 线算法夜盘判定完整性（数据层验证）"""

import sqlite3
from config.settings import DB_PATH

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

print("=== 1. Check AP (no night) 1d: distinct days ===")
days = conn.execute("""
    SELECT DISTINCT date(datetime(timestamp, 'unixepoch')) as day
    FROM futures_klines WHERE symbol='AP' AND timeframe='1d'
    ORDER BY day DESC LIMIT 10
""").fetchall()
for d in days:
    day = d["day"]
    cnt = conn.execute("SELECT COUNT(*) FROM futures_klines WHERE symbol='AP' AND timeframe='1d' AND date(datetime(timestamp, 'unixepoch'))=?", (day,)).fetchone()[0]
    print(f"  {day}: {cnt} rows")

print()
print("=== 2. Check CJ (no night) 1d: distinct days ===")
days = conn.execute("""
    SELECT DISTINCT date(datetime(timestamp, 'unixepoch')) as day
    FROM futures_klines WHERE symbol='CJ' AND timeframe='1d'
    ORDER BY day DESC LIMIT 10
""").fetchall()
for d in days:
    day = d["day"]
    cnt = conn.execute("SELECT COUNT(*) FROM futures_klines WHERE symbol='CJ' AND timeframe='1d' AND date(datetime(timestamp, 'unixepoch'))=?", (day,)).fetchone()[0]
    print(f"  {day}: {cnt} rows")

print()
print("=== 3. Check AG (night to 02:30) 1d ===")
days = conn.execute("""
    SELECT DISTINCT date(datetime(timestamp, 'unixepoch')) as day
    FROM futures_klines WHERE symbol='AG' AND timeframe='1d'
    ORDER BY day DESC LIMIT 5
""").fetchall()
for d in days:
    day = d["day"]
    rows = conn.execute("SELECT time(datetime(timestamp, 'unixepoch')) as t, open, high, low, close FROM futures_klines WHERE symbol='AG' AND timeframe='1d' AND date(datetime(timestamp, 'unixepoch'))=? ORDER BY timestamp", (day,)).fetchall()
    print(f"  {day}: {len(rows)} rows")
    for r in rows:
        print(f"    {r['t']} O={r['open']:.2f} H={r['high']:.2f} L={r['low']:.2f} C={r['close']:.2f}")

print()
print("=== 4. Data integrity check ===")
bads = conn.execute("SELECT COUNT(*) as cnt FROM futures_klines WHERE timeframe='1d' AND (high < low OR open <= 0 OR close <= 0)").fetchone()["cnt"]
print(f"  Rows with high<low or price<=0: {bads}")

print()
print("=== 5. RB 1d timestamps on 2026-06-22 ===")
rows = conn.execute("SELECT timestamp, time(datetime(timestamp, 'unixepoch')) as t FROM futures_klines WHERE symbol='RB' AND timeframe='1d' AND date(datetime(timestamp, 'unixepoch'))='2026-06-22' ORDER BY timestamp").fetchall()
for r in rows:
    print(f"  {r['t']}")

print()
print("=== 6. SC (night to 02:30, INE) 1d ===")
days = conn.execute("""
    SELECT DISTINCT date(datetime(timestamp, 'unixepoch')) as day
    FROM futures_klines WHERE symbol='SC' AND timeframe='1d'
    ORDER BY day DESC LIMIT 5
""").fetchall()
for d in days:
    day = d["day"]
    rows = conn.execute("SELECT time(datetime(timestamp, 'unixepoch')) as t, open, high, low, close FROM futures_klines WHERE symbol='SC' AND timeframe='1d' AND date(datetime(timestamp, 'unixepoch'))=? ORDER BY timestamp", (day,)).fetchall()
    print(f"  {day}: {len(rows)} rows")
    for r in rows:
        print(f"    {r['t']} O={r['open']:.2f} H={r['high']:.2f} L={r['low']:.2f} C={r['close']:.2f}")

print()
print("=== 7. I (night to 23:00, DCE) 1d ===")
days = conn.execute("""
    SELECT DISTINCT date(datetime(timestamp, 'unixepoch')) as day
    FROM futures_klines WHERE symbol='I' AND timeframe='1d'
    ORDER BY day DESC LIMIT 5
""").fetchall()
for d in days:
    day = d["day"]
    rows = conn.execute("SELECT time(datetime(timestamp, 'unixepoch')) as t, open, high, low, close FROM futures_klines WHERE symbol='I' AND timeframe='1d' AND date(datetime(timestamp, 'unixepoch'))=? ORDER BY timestamp", (day,)).fetchall()
    print(f"  {day}: {len(rows)} rows")
    for r in rows:
        print(f"    {r['t']} O={r['open']:.2f} H={r['high']:.2f} L={r['low']:.2f} C={r['close']:.2f}")

print()
print("=== 8. MA (night to 23:00, CZCE) 1d ===")
days = conn.execute("""
    SELECT DISTINCT date(datetime(timestamp, 'unixepoch')) as day
    FROM futures_klines WHERE symbol='MA' AND timeframe='1d'
    ORDER BY day DESC LIMIT 5
""").fetchall()
for d in days:
    day = d["day"]
    rows = conn.execute("SELECT time(datetime(timestamp, 'unixepoch')) as t, open, high, low, close FROM futures_klines WHERE symbol='MA' AND timeframe='1d' AND date(datetime(timestamp, 'unixepoch'))=? ORDER BY timestamp", (day,)).fetchall()
    print(f"  {day}: {len(rows)} rows")
    for r in rows:
        print(f"    {r['t']} O={r['open']:.2f} H={r['high']:.2f} L={r['low']:.2f} C={r['close']:.2f}")

conn.close()
print()
print("=== VERIFICATION COMPLETE ===")
