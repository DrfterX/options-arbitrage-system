#!/usr/bin/env python3
"""Check: after dedup+normalization, are ALL 1d bars at consistent times?"""
import sqlite3
from datetime import datetime, timezone
from collections import Counter

utc = timezone.utc
conn = sqlite3.connect('trading_system.db')
conn.row_factory = sqlite3.Row

_BJ_OFFSET = 8 * 3600
_TARGET_HOUR_SEC = 20700
_MIDNIGHT_SEC = 57600

# Get symbols with 1d N-structures
symbols = [r['symbol'] for r in conn.execute(
    "SELECT DISTINCT symbol FROM futures_n_structures WHERE timeframe='1d' AND state!='COMPLETED'"
).fetchall()]

print(f"=== Checking 1d bars after dedup+normalization ({len(symbols)} symbols) ===\n")

bar_time_tods = Counter()
conflicts = 0
total_days = 0

for sym in symbols[:50]:  # take first 50
    contract_row = conn.execute(
        "SELECT contract FROM futures_n_structures WHERE symbol=? AND timeframe='1d' AND contract!='' ORDER BY updated_at DESC LIMIT 1",
        (sym,)
    ).fetchone()
    if not contract_row:
        continue
    contract = contract_row['contract']

    bars = conn.execute(
        "SELECT timestamp, open, high, low, close FROM futures_klines WHERE symbol=? AND timeframe='1d' AND contract=? ORDER BY timestamp DESC LIMIT 100",
        (sym, contract)
    ).fetchall()

    # Dedup by date (same as API)
    seen = {}
    for b in bars:
        dt = datetime.fromtimestamp(b['timestamp'], tz=utc)
        key = dt.strftime('%Y-%m-%d')
        if key not in seen or b['timestamp'] > seen[key]['timestamp']:
            seen[key] = {'timestamp': b['timestamp'], 'bar': b}

    # Apply normalization
    for key, val in seen.items():
        total_days += 1
        ts = val['timestamp']
        tod = ts % 86400
        if tod == _MIDNIGHT_SEC:
            # normalizes to 21:45 UTC
            bj_midnight_utc = ((ts + _BJ_OFFSET) // 86400) * 86400 - _BJ_OFFSET
            norm_ts = bj_midnight_utc + _TARGET_HOUR_SEC
            norm_tod = norm_ts % 86400
            bar_time_tods[norm_tod] += 1
        else:
            bar_time_tods[tod] += 1
            if tod != 20700:
                conflicts += 1
                if conflicts <= 10:
                    print(f"  {sym} day {key}: bar at {tod}s = {tod//3600}:{(tod%3600)//60:02d} UTC (NOT normalized)")

print(f"\nTotal days checked: {total_days}")
print(f"Bars NOT at 16:00 UTC (not normalized): {conflicts}")
print(f"\nTime-of-day distribution after dedup+normalization:")
for tod, cnt in bar_time_tods.most_common(15):
    h = tod // 3600
    m = (tod % 3600) // 60
    pct = cnt / total_days * 100
    print(f"  {h:02d}:{m:02d} UTC ({tod}s): {cnt} ({pct:.1f}%)")

conn.close()