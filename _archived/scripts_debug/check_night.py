import sqlite3
from datetime import datetime, timezone, timedelta

conn = sqlite3.connect('projects/options_arbitrage_system/trading_system.db')
c = conn.cursor()

def check_night_coverage(sym, max_hour_lookback=2):
    print(f'=== {sym} 15m last 50 rows ===')
    c.execute('SELECT timestamp FROM futures_klines WHERE symbol = ? AND timeframe = "15m" ORDER BY timestamp DESC LIMIT 50', (sym,))
    tss = [r[0] for r in c.fetchall()]
    if not tss:
        print(f'  No data for {sym} 15m')
        return
    tss.sort()
    min_cst = datetime.fromtimestamp(min(tss), tz=timezone.utc) + timedelta(hours=8)
    max_cst = datetime.fromtimestamp(max(tss), tz=timezone.utc) + timedelta(hours=8)
    print(f'  CST range: {min_cst} ~ {max_cst}')
    night_rows = []
    day_rows = 0
    for ts in tss:
        dt_cst = datetime.fromtimestamp(ts, tz=timezone.utc) + timedelta(hours=8)
        hour = dt_cst.hour
        if hour >= 21 or hour < max_hour_lookback:
            night_rows.append(dt_cst)
        else:
            day_rows += 1
    print(f'  Night: {len(night_rows)}, Day: {day_rows}')
    for dt in night_rows[:8]:
        print(f'    NIGHT CST:{dt}')
    if len(night_rows) > 8:
        print(f'    ... and {len(night_rows)-8} more')
    print()

check_night_coverage('RB', 2)
check_night_coverage('CU', 1)
check_night_coverage('AU', 2)
conn.close()
