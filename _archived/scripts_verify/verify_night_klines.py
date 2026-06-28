#!/usr/bin/env python3
"""P0 子任务 1.6 — 验证夜盘时段 K 线覆盖完整性。"""
import sqlite3
import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MARKET_TZ, PROJECT_ROOT
from config.contracts import ContractRegistry

db_path = PROJECT_ROOT / 'trading_system.db'
conn = sqlite3.connect(str(db_path))

print('=' * 80)
print('P0 子任务 1.6 — 夜盘时段 K 线覆盖验证')
print('=' * 80)

# Step 1: Get symbols with is_night=1 from the database
cur = conn.execute('SELECT symbol, name, exchange FROM symbols WHERE is_night=1 ORDER BY symbol')
night_symbols = cur.fetchall()
print(f'\n有夜盘品种数: {len(night_symbols)}')

# Step 2: Check 15m kline data for each night symbol
print('\n' + '-' * 80)
print('15分钟 K 线时间戳范围检查（夜盘品种）')
print('-' * 80)

for symbol, name, exchange in night_symbols:
    # Check if data exists
    cur = conn.execute(
        'SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM futures_klines WHERE symbol=? AND timeframe=?',
        (symbol, '15m')
    )
    row = cur.fetchone()
    cnt, min_ts, max_ts = row
    
    if cnt == 0 or min_ts is None:
        print(f'  {symbol:6s} ({name:8s}) — 无 15m 数据')
        continue
    
    # Convert timestamps to Beijing time for readability
    min_dt = datetime.fromtimestamp(min_ts, tz=MARKET_TZ)
    max_dt = datetime.fromtimestamp(max_ts, tz=MARKET_TZ)
    
    # Sample recent timestamps (last 20)
    cur = conn.execute(
        'SELECT timestamp FROM futures_klines WHERE symbol=? AND timeframe=? ORDER BY timestamp DESC LIMIT 20',
        (symbol, '15m')
    )
    recent_ts = [r[0] for r in cur.fetchall()]
    
    # Analyze whether night session hours are covered
    # Night session: 21:00-23:00 for most, but varies by exchange
    night_hours_found = set()
    for ts in recent_ts:
        dt = datetime.fromtimestamp(ts, tz=MARKET_TZ)
        hour = dt.hour
        if hour >= 21 or hour < 3:
            night_hours_found.add(hour)
    
    print(f'  {symbol:6s} ({name:8s}) | exchange={exchange:5s} | count={cnt:5d} | '
          f'{min_dt.strftime("%Y-%m-%d %H:%M")} ~ {max_dt.strftime("%Y-%m-%d %H:%M")}')
    
    if night_hours_found:
        hours_str = ','.join(sorted([f'{h:02d}' for h in night_hours_found]))
        print(f'          夜盘时段覆盖: {hours_str} 时 ✅')
    else:
        print(f'          最近20根K线无夜盘时段数据 ❌')

# Step 3: Check non-night symbols for completeness
print('\n' + '-' * 80)
print('无夜盘品种（is_night=0）检查')
print('-' * 80)

cur = conn.execute('SELECT symbol, name FROM symbols WHERE is_night=0 ORDER BY symbol')
non_night = cur.fetchall()

for symbol, name in non_night:
    cur = conn.execute(
        'SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM futures_klines WHERE symbol=? AND timeframe=?',
        (symbol, '15m')
    )
    row = cur.fetchone()
    cnt, min_ts, max_ts = row
    
    if cnt == 0 or min_ts is None:
        print(f'  {symbol:6s} ({name:8s}) — 无 15m 数据')
        continue
    
    min_dt = datetime.fromtimestamp(min_ts, tz=MARKET_TZ)
    max_dt = datetime.fromtimestamp(max_ts, tz=MARKET_TZ)
    
    # Check if any timestamps fall in night hours (21:00-03:00) — should NOT happen
    cur = conn.execute(
        'SELECT timestamp FROM futures_klines WHERE symbol=? AND timeframe=? ORDER BY timestamp DESC LIMIT 20',
        (symbol, '15m')
    )
    recent_ts = [r[0] for r in cur.fetchall()]
    
    night_leak = False
    for ts in recent_ts:
        dt = datetime.fromtimestamp(ts, tz=MARKET_TZ)
        h = dt.hour
        if h >= 21 or h < 3:
            night_leak = True
            break
    
    status = '⚠️ 含夜盘时段数据（不应有）' if night_leak else '✅'
    print(f'  {symbol:6s} ({name:8s}) | count={cnt:5d} | '
          f'{min_dt.strftime("%Y-%m-%d %H:%M")} ~ {max_dt.strftime("%Y-%m-%d %H:%M")} | {status}')

print('\n' + '=' * 80)
print('验证完成')
print('=' * 80)

conn.close()
