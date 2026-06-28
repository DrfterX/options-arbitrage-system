#!/usr/bin/env python3
"""Temp check script."""
import sqlite3
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))

conn = sqlite3.connect('projects/options_arbitrage_system/trading_system.db')
c = conn.cursor()

symbols = ['RB','MA','AG','CU','SC','AP','CJ']
for sym in symbols:
    print(f'=== {sym} ===')
    rows = c.execute('SELECT DISTINCT date(datetime(timestamp, "unixepoch")) as d FROM futures_klines WHERE symbol=? AND timeframe=? ORDER BY d DESC LIMIT 3', (sym, '1d')).fetchall()
    for r in rows:
        day = r[0]
        bars = c.execute('SELECT timestamp, open, high, low, close FROM futures_klines WHERE symbol=? AND timeframe=? AND date(datetime(timestamp, "unixepoch"))=? ORDER BY timestamp', (sym, '1d', day)).fetchall()
        for b in bars[:1]:
            dt = datetime.fromtimestamp(b[0], tz=BJT)
            tstr = dt.strftime('%Y-%m-%d %H:%M')
            print(f'  {tstr}: O={b[1]:.1f} H={b[2]:.1f} L={b[3]:.1f} C={b[4]:.1f}')
conn.close()
