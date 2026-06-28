#!/usr/bin/env python3
"""Diagnose duplicate 1d klines."""
import sqlite3, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
db_path = os.path.join(ROOT, 'data', 'futures_options.db')
if not os.path.exists(db_path):
    print(f'DB not found at {db_path}')
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find duplicate 1d klines per symbol+date
cursor.execute("""
    SELECT symbol, date(datetime(timestamp, 'unixepoch', '+8 hours')) as bj_date,
           COUNT(*), GROUP_CONCAT(timestamp), GROUP_CONCAT(open), GROUP_CONCAT(close)
    FROM futures_klines
    WHERE timeframe = '1d'
    GROUP BY symbol, bj_date
    HAVING COUNT(*) > 1
    ORDER BY symbol, bj_date
    LIMIT 20
""")
rows = cursor.fetchall()
print(f"=== Found {len(rows)} symbol-dates with duplicate 1d klines ===")
for r in rows:
    print(f"{r[0]} {r[1]}: {r[2]} klines, timestamps={r[3]}, open={r[4]}, close={r[5]}")

# Sample a few distinct symbols' data
cursor.execute("SELECT DISTINCT symbol FROM futures_klines WHERE timeframe='1d' LIMIT 5")
symbols = [r[0] for r in cursor.fetchall()]
print(f"\n=== Sample symbols: {symbols} ===")
for sym in symbols[:2]:
    print(f"\n--- {sym} 1d klines (last 5) ---")
    cursor.execute("""
        SELECT datetime(timestamp, 'unixepoch', '+8 hours'), open, high, low, close, volume
        FROM futures_klines
        WHERE symbol=? AND timeframe='1d'
        ORDER BY timestamp DESC
        LIMIT 10
    """, (sym,))
    for r in cursor.fetchall():
        print(f"  {r}")

# Check total
cursor.execute("SELECT COUNT(*), COUNT(DISTINCT symbol) FROM futures_klines WHERE timeframe='1d'")
print(f"\nTotal 1d klines: {cursor.fetchall()[0]}")

# Check if data comes from collector or aggregator
# Look at the source of the most recent entries
cursor.execute("""
    SELECT symbol, datetime(timestamp, 'unixepoch', '+8 hours'), open, high, low, close, volume
    FROM futures_klines
    WHERE timeframe = '1d'
    ORDER BY timestamp DESC
    LIMIT 10
""")
print("\n=== Most recent 1d klines ===")
for r in cursor.fetchall():
    print(f"  {r}")

conn.close()
print("\nDone.")
