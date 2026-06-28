import sqlite3, os, sys
from datetime import datetime, timezone, timedelta

cwd = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(cwd, 'trading_system.db')
if not os.path.exists(DB):
    print('DB not found at', DB)
    sys.exit(1)

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', [r[0] for r in c.fetchall()])

# Check futures_klines
c.execute('PRAGMA table_info(futures_klines)')
cols = c.fetchall()
print('futures_klines columns:')
for r in cols:
    print(f'  {r[1]} ({r[2]})')

# Timeframe distribution
print()
c.execute('SELECT timeframe, COUNT(*) as cnt FROM futures_klines GROUP BY timeframe ORDER BY cnt DESC')
print('Timeframe distribution:')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]}')

# Check each symbol
for sym in ['RB','MA','AG','CU','SC','AP','CJ']:
    print(f'\n=== {sym} ===')
    c.execute('SELECT timeframe, COUNT(*) FROM futures_klines WHERE symbol=? GROUP BY timeframe', (sym,))
    tfs = c.fetchall()
    print('  timeframes:', {r[0]:r[1] for r in tfs})
    
    c.execute('SELECT timestamp, open, high, low, close, timeframe FROM futures_klines WHERE symbol=? AND timeframe="1d" ORDER BY timestamp DESC LIMIT 3', (sym,))
    rows = c.fetchall()
    for r in rows:
        bjt = datetime.fromtimestamp(r[0], tz=timezone.utc) + timedelta(hours=8)
        print(f'  ts={r[0]} bjt={bjt.strftime("%Y-%m-%d %H:%M")} o={r[1]} h={r[2]} l={r[3]} c={r[4]}')
    if not rows:
        print('  NO 1d DATA')
        # Check what timeframes have data
        c.execute('SELECT timeframe, timestamp, open, high, low, close FROM futures_klines WHERE symbol=? ORDER BY timestamp DESC LIMIT 3', (sym,))
        for r in c.fetchall():
            bjt = datetime.fromtimestamp(r[1], tz=timezone.utc) + timedelta(hours=8)
            print(f'  tf={r[0]} ts={r[1]} bjt={bjt.strftime("%Y-%m-%d %H:%M")} o={r[2]} h={r[3]} l={r[4]} c={r[5]}')

conn.close()
