#!/usr/bin/env python3
"""P0 子任务 1.6 — 验证夜盘时段 K 线覆盖完整性"""
import sqlite3
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))

def bjt_str(ts):
    d = datetime.fromtimestamp(ts, tz=BJT)
    return d.strftime('%Y-%m-%d %H:%M:%S'), d.weekday()

def main():
    conn = sqlite3.connect('trading_system.db')
    conn.row_factory = sqlite3.Row

    # 夜盘品种 (不同夜盘时段)
    # RB: SHFE 21:00-23:00
    # CU: SHFE 21:00-次日01:00
    # AU: SHFE 21:00-次日02:30
    # SC: INE 21:00-次日02:30
    # MA: ZCE 21:00-23:00
    # I:  DCE 21:00-23:00
    night_symbols = ['RB', 'CU', 'AU', 'SC', 'MA', 'I']

    errors = []

    for sym in night_symbols:
        print(f'\n{"="*60}')
        print(f'=== {sym} 15m K线夜盘时段验证 ===')

        # 获取所有15m数据，按天分组
        rows = conn.execute('''
            SELECT timestamp, open, high, low, close, volume
            FROM futures_klines
            WHERE symbol=? AND timeframe='15m'
            ORDER BY timestamp DESC
        ''', (sym,)).fetchall()

        if not rows:
            print(f'  ⚠️  无15m数据')
            errors.append(f'{sym}: 无15m数据')
            continue

        # 按日期分组
        day_groups = {}
        for r in rows:
            dt = datetime.fromtimestamp(r['timestamp'], tz=BJT)
            date_key = dt.strftime('%Y-%m-%d')
            if date_key not in day_groups:
                day_groups[date_key] = []
            day_groups[date_key].append({
                'ts': r['timestamp'],
                'dt': dt,
                'o': r['open'],
                'h': r['high'],
                'l': r['low'],
                'c': r['close'],
                'v': r['volume'],
            })

        # 取最近3个交易日
        sorted_dates = sorted(day_groups.keys(), reverse=True)[:3]
        for date_key in sorted_dates:
            klines = day_groups[date_key]
            klines.sort(key=lambda x: x['dt'])

            hours = [k['dt'].hour for k in klines]
            first_k = klines[0]
            last_k = klines[-1]
            first_time = first_k['dt'].strftime('%H:%M')
            last_time = last_k['dt'].strftime('%H:%M')

            print(f'\n  日期 {date_key} ({len(klines)}根K线):')
            print(f'    首根: {first_time} | O={first_k["o"]:.1f} H={first_k["h"]:.1f} L={first_k["l"]:.1f} C={first_k["c"]:.1f}')
            print(f'    尾根: {last_time} | O={last_k["o"]:.1f} H={last_k["h"]:.1f} L={last_k["l"]:.1f} C={last_k["c"]:.1f}')

            # 打印时间分布
            time_ranges = []
            for k in klines:
                time_ranges.append(k['dt'].strftime('%H:%M'))
            
            # 检查是否覆盖了夜盘
            has_night = any(21 <= k['dt'].hour or k['dt'].hour < 3 for k in klines)
            has_day = any(9 <= k['dt'].hour <= 15 for k in klines)

            if has_night:
                night_klines = [k for k in klines if k['dt'].hour >= 21 or k['dt'].hour < 3]
                night_start = night_klines[0]['dt'].strftime('%H:%M')
                night_end = night_klines[-1]['dt'].strftime('%H:%M')
                print(f'    夜盘: ✅ {night_start}~{night_end} ({len(night_klines)}根)')
            else:
                print(f'    夜盘: ❌ 无夜盘时段数据')
                errors.append(f'{sym} {date_key}: 缺少夜盘时段K线')

            if has_day:
                day_klines = [k for k in klines if 9 <= k['dt'].hour <= 15]
                day_start = day_klines[0]['dt'].strftime('%H:%M')
                day_end = day_klines[-1]['dt'].strftime('%H:%M')
                print(f'    日盘: ✅ {day_start}~{day_end} ({len(day_klines)}根)')

            # 检查15m间距连续性
            gaps = []
            for i in range(1, len(klines)):
                diff = klines[i]['dt'] - klines[i-1]['dt']
                diff_minutes = diff.total_seconds() / 60
                if diff_minutes > 20:  # 超过20分钟就算gap
                    gap_start = klines[i-1]['dt'].strftime('%H:%M')
                    gap_end = klines[i]['dt'].strftime('%H:%M')
                    gaps.append(f'{gap_start}~{gap_end} ({diff_minutes:.0f}分)')
            
            if gaps:
                print(f'    时间间隙: ⚠️  {len(gaps)}处')
                for g in gaps[:5]:
                    print(f'      - {g}')
            else:
                print(f'    时间间隙: ✅ 连续无间隙')

            # 检查数据质量
            quality_issues = 0
            for k in klines:
                if k['h'] < k['l']:
                    quality_issues += 1
                if k['h'] <= 0 or k['l'] <= 0:
                    quality_issues += 1
            if quality_issues:
                print(f'    数据质量: ⚠️  {quality_issues}处问题')
                errors.append(f'{sym} {date_key}: {quality_issues}处数据质量问题')

    # 非夜盘品种对比
    non_night_symbols = ['AP', 'CJ']
    for sym in non_night_symbols:
        print(f'\n{"="*60}')
        print(f'=== {sym} (非夜盘) 15m K线验证 ===')
        rows = conn.execute('''
            SELECT timestamp, open, high, low, close, volume
            FROM futures_klines
            WHERE symbol=? AND timeframe='15m'
            ORDER BY timestamp DESC LIMIT 20
        ''', (sym,)).fetchall()
        if not rows:
            print(f'  ⚠️  无15m数据')
            continue
        print(f'  共{len(rows)}根K线')
        for r in rows[:8]:
            ts_str, wd = bjt_str(r['timestamp'])
            wd_names = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
            print(f'  {ts_str} {wd_names[wd]} | O={r["o"]:.1f} H={r["h"]:.1f} L={r["l"]:.1f} C={r["c"]:.1f} V={r["v"]}')

    print(f'\n{"="*60}')
    if errors:
        print(f'\n❌ FAILED: {len(errors)} issues found:')
        for e in errors:
            print(f'  - {e}')
    else:
        print('\n✅ SUCCESS: All night session coverage checks passed!')

    conn.close()
    return len(errors)

if __name__ == '__main__':
    exit(main())
