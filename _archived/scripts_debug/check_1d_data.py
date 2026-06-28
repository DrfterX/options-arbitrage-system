#!/usr/bin/env python3
"""Quick check of 1d kline data - what timestamps exist."""
import sqlite3
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))

conn = sqlite3.connect('projects/options_arbitrage_system/trading_system.db')
conn.row_factory = sqlite3.Row

syms = ['RB', 'MA', 'AG', 'CU', 'SC', 'AP', 'CJ']

for sym in syms:
    print(f'\n=== {sym} 1d data ===')
    rows = conn.execute(
        'SELECT DISTINCT date(datetime(timestamp, \"unixepoch\")) as d '
        'FROM futures_klines WHERE symbol=? AND timeframe=? ORDER BY d DESC LIMIT 3',
        (sym, '1d')
    ).fetchall()
    
    for r in rows:
        day = r['d']
        bars = conn.execute(
            'SELECT timestamp, open, high, low, close '
            'FROM futures_klines WHERE symbol=? AND timeframe=? '
            'AND date(datetime(timestamp, \"unixepoch\"))=? ORDER BY timestamp',
            (sym, '1d', day)
        ).fetchall()
        times = []
        for b in bars:
            dt = datetime.fromtimestamp(b['timestamp'], tz=BJT)
            times.append(dt.strftime('%H:%M'))
        print(f'  {day}: {len(bars)} bars at {times}')
        
        # Show first bar
        if bars:
            b = bars[0]
            print(f"    O={b['open']:.1f} H={b['high']:.1f} L={b['low']:.1f} C={b['close']:.1f}")

conn.close()
print('\nDone.')
