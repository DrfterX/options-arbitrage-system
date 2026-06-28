import sqlite3, datetime

conn = sqlite3.connect('trading_system.db')
cur = conn.cursor()

# Check 15m min/max date
cur.execute('SELECT MIN(timestamp), MAX(timestamp) FROM futures_klines WHERE timeframe = "15m"')
r = cur.fetchone()
print('15m date range:', datetime.datetime.fromtimestamp(r[0]), '-', datetime.datetime.fromtimestamp(r[1]))

# Check 15m count by symbol
cur.execute('SELECT symbol, COUNT(*) FROM futures_klines WHERE timeframe = "15m" GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 5')
print('Top 5 symbols by 15m rows:', cur.fetchall())

# Check if there's 15m data between Jan 16 and Feb 25 2026
from_ts = int(datetime.datetime(2026,1,16).timestamp())
to_ts = int(datetime.datetime(2026,2,25,23,59).timestamp())
cur.execute('SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM futures_klines WHERE timeframe = "15m" AND timestamp >= ? AND timestamp <= ?', (from_ts, to_ts))
r = cur.fetchone()
print(f'15m rows Jan16-Feb25 2026: {r[0]}, min={datetime.datetime.fromtimestamp(r[1]) if r[1] else None}, max={datetime.datetime.fromtimestamp(r[2]) if r[2] else None}')

# Check date before and after
before_ts = int(datetime.datetime(2026,1,15,23,59).timestamp())
after_ts = int(datetime.datetime(2026,2,26).timestamp())
cur.execute('SELECT COUNT(*), MAX(timestamp) FROM futures_klines WHERE timeframe = "15m" AND timestamp <= ?', (before_ts,))
r1 = cur.fetchone()
print(f'15m rows before Jan 16 2026: {r1[0]}, last_ts={datetime.datetime.fromtimestamp(r1[1]) if r1[1] else None}')

cur.execute('SELECT COUNT(*), MIN(timestamp) FROM futures_klines WHERE timeframe = "15m" AND timestamp >= ?', (after_ts,))
r2 = cur.fetchone()
print(f'15m rows after Feb 25 2026: {r2[0]}, first_ts={datetime.datetime.fromtimestamp(r2[1]) if r2[1] else None}')

# Check 1d data range for same period
cur.execute('SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM futures_klines WHERE timeframe = "1d" AND timestamp >= ? AND timestamp <= ?', (from_ts, to_ts))
r = cur.fetchone()
print(f'1d rows Jan16-Feb25 2026: {r[0]}, min={datetime.datetime.fromtimestamp(r[1]) if r[1] else None}, max={datetime.datetime.fromtimestamp(r[2]) if r[2] else None}')

# Check if CF symbol has 15m data in that range
cur.execute('SELECT COUNT(*) FROM futures_klines WHERE timeframe = "15m" AND symbol = "CF" AND timestamp >= ? AND timestamp <= ?', (from_ts, to_ts))
r = cur.fetchone()
print(f'CF 15m rows Jan16-Feb25: {r[0]}')

conn.close()
