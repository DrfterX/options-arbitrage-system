import sqlite3

conn = sqlite3.connect('trading_system.db')
conn.row_factory = sqlite3.Row

# Check symbols table for night/non-night
print('=== Symbols is_night check ===')
cur = conn.execute("SELECT symbol, is_night FROM symbols WHERE symbol IN ('RB','MA','AG','SC','I','AP','CJ','CF','TA','CU')")
for r in cur.fetchall():
    print(dict(r))

# Check timeframes available
print('\n=== Timeframes ===')
cur = conn.execute("SELECT DISTINCT timeframe FROM futures_klines LIMIT 10")
for r in cur.fetchall():
    print(r['timeframe'])

# Check RB (night) last 5 daily klines
print('\n=== RB (night variety) last 5 daily klines (timestamp, open, high, low, close) ===')
cur = conn.execute(
    "SELECT timestamp, open, high, low, close FROM futures_klines WHERE symbol='RB' AND timeframe='1d' ORDER BY timestamp DESC LIMIT 5"
)
for r in cur.fetchall():
    print(dict(r))
    # print timestamp as readable
    import datetime
    ts = r['timestamp']
    bjt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=8)
    print(f"  -> BJT: {bjt}")

# Check MA (night, ZCE) last 5 daily klines
print('\n=== MA (ZCE night variety) last 5 daily klines ===')
cur = conn.execute(
    "SELECT timestamp, open, high, low, close FROM futures_klines WHERE symbol='MA' AND timeframe='1d' ORDER BY timestamp DESC LIMIT 5"
)
for r in cur.fetchall():
    print(dict(r))
    import datetime
    ts = r['timestamp']
    bjt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=8)
    print(f"  -> BJT: {bjt}")

# Check AG (night, SHFE) last 5 daily klines
print('\n=== AG (SHFE night, 02:30 close) last 5 daily klines ===')
cur = conn.execute(
    "SELECT timestamp, open, high, low, close FROM futures_klines WHERE symbol='AG' AND timeframe='1d' ORDER BY timestamp DESC LIMIT 5"
)
for r in cur.fetchall():
    print(dict(r))
    import datetime
    ts = r['timestamp']
    bjt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=8)
    print(f"  -> BJT: {bjt}")

# Check SC (INE night, 02:30 close) last 5 daily klines
print('\n=== SC (INE night, 02:30 close) last 5 daily klines ===')
cur = conn.execute(
    "SELECT timestamp, open, high, low, close FROM futures_klines WHERE symbol='SC' AND timeframe='1d' ORDER BY timestamp DESC LIMIT 5"
)
for r in cur.fetchall():
    print(dict(r))
    import datetime
    ts = r['timestamp']
    bjt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=8)
    print(f"  -> BJT: {bjt}")

# Check I (DCE night, 23:00 close) last 5 daily klines
print('\n=== I (DCE night, 23:00 close) last 5 daily klines ===')
cur = conn.execute(
    "SELECT timestamp, open, high, low, close FROM futures_klines WHERE symbol='I' AND timeframe='1d' ORDER BY timestamp DESC LIMIT 5"
)
for r in cur.fetchall():
    print(dict(r))
    import datetime
    ts = r['timestamp']
    bjt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=8)
    print(f"  -> BJT: {bjt}")

# Check AP (non-night) last 5 daily klines
print('\n=== AP (non-night variety) last 5 daily klines ===')
cur = conn.execute(
    "SELECT timestamp, open, high, low, close FROM futures_klines WHERE symbol='AP' AND timeframe='1d' ORDER BY timestamp DESC LIMIT 5"
)
for r in cur.fetchall():
    print(dict(r))
    import datetime
    ts = r['timestamp']
    bjt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=8)
    print(f"  -> BJT: {bjt}")

# Check CJ (non-night) last 5 daily klines
print('\n=== CJ (non-night variety) last 5 daily klines ===')
cur = conn.execute(
    "SELECT timestamp, open, high, low, close FROM futures_klines WHERE symbol='CJ' AND timeframe='1d' ORDER BY timestamp DESC LIMIT 5"
)
for r in cur.fetchall():
    print(dict(r))
    import datetime
    ts = r['timestamp']
    bjt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=8)
    print(f"  -> BJT: {bjt}")

# Check logical errors: high < low or price <= 0
print('\n=== Logical errors? (high < low or price <= 0) ===')
cur = conn.execute(
    "SELECT COUNT(*) as cnt FROM futures_klines WHERE high < low OR high <= 0 OR low <= 0 OR open <= 0 OR close <= 0"
)
print('Count of errors:', cur.fetchone()['cnt'])

conn.close()
print('\nDone!')
