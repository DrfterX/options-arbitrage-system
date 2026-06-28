#!/usr/bin/env python3
"""P0 子任务 1.3 — 校验 K 线算法夜盘判定完整性"""
import sqlite3
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))

def bjt_str(ts):
    """转换 Unix 秒为北京时间字符串"""
    if ts is None:
        return "N/A"
    return datetime.fromtimestamp(ts, tz=BJT).strftime('%Y-%m-%d %H:%M:%S')

def main():
    conn = sqlite3.connect('trading_system.db')
    conn.row_factory = sqlite3.Row

    # 5 个夜盘品种 + 2 个非夜盘品种
    night_symbols = ['RB', 'MA', 'AG', 'SC', 'I']
    non_night_symbols = ['AP', 'CJ']

    errors = []

    for sym in night_symbols:
        # 检查 is_night 标记
        row = conn.execute('SELECT is_night FROM symbols WHERE symbol=?', (sym,)).fetchone()
        if row and row['is_night'] != 1:
            errors.append(f'{sym}: is_night={row["is_night"]} (expected 1)')
        elif not row:
            errors.append(f'{sym}: not found in symbols table')

        # 获取最近 5 根日 K 线
        klines = conn.execute(
            'SELECT timestamp, open, high, low, close FROM futures_klines '
            'WHERE symbol=? AND timeframe="1d" ORDER BY timestamp DESC LIMIT 20',
            (sym,)
        ).fetchall()

        print(f'\n=== {sym} (夜盘) 最近 {len(klines)} 根 1d K线 ===')
        
        # 检查：每个交易日应该只有 1 根日 K 线
        # 先统计不同日期数量
        seen_dates = set()
        for k in klines:
            dt = datetime.fromtimestamp(k['timestamp'], tz=BJT)
            date_str = dt.strftime('%Y-%m-%d')
            seen_dates.add(date_str)
        
        # 如果同一天有多根 K 线，报告错误
        date_counts = {}
        for k in klines:
            dt = datetime.fromtimestamp(k['timestamp'], tz=BJT)
            date_str = dt.strftime('%Y-%m-%d')
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        multi_dates = {d: c for d, c in date_counts.items() if c > 1}
        if multi_dates:
            for d, c in sorted(multi_dates.items()):
                errors.append(f'{sym} 1d: 日期 {d} 有 {c} 根 K 线（预期 1）')
            print(f'  ⚠️  同一日期多K线: {multi_dates}')
        else:
            print(f'  ✅ 无重复日期')
        
        for k in klines[:10]:
            ts_str = bjt_str(k['timestamp'])
            close_time = ts_str[11:16]  # HH:MM
            
            # 检查 high >= low 和价格 > 0
            if k['high'] < k['low']:
                errors.append(f'{sym} @ {ts_str}: high({k["high"]}) < low({k["low"]})')
            if k['high'] <= 0 or k['low'] <= 0 or k['open'] <= 0 or k['close'] <= 0:
                errors.append(f'{sym} @ {ts_str}: 价格 <= 0')
            
            print(f'  {ts_str} | O={k["open"]:.1f} H={k["high"]:.1f} L={k["low"]:.1f} C={k["close"]:.1f} | 收盘BJT={close_time}')
        
        if len(klines) > 0:
            # 检查收盘时间是否合理
            # 夜盘品种收盘时间应在 23:00/01:00/02:30 或日盘 15:00
            last_k = klines[0]
            dt = datetime.fromtimestamp(last_k['timestamp'], tz=BJT)
            h, m = dt.hour, dt.minute
            valid_close_times = [
                (15, 0),   # 日盘收盘
                (23, 0),   # 夜盘 23:00
                                (23, 0),   # 夜盘 23:00
                (1, 0),    # 凌晨 01:00
                (2, 30),   # 凌晨 02:30
            ]
            # 特殊情况当天收盘在 23:00-23:59，则检查
            is_valid_close = False
            for vh, vm in valid_close_times:
                if h == vh and m == vm:
                    is_valid_close = True
                    break
            # 对于 RB(23:00收盘)检查 23:00
            # 如果最新K线是今天日盘 15:00 收盘也是合理的
            # 补充：检查非15:00非夜盘时间的收盘
            if not (h == 15 and m == 0) and not is_valid_close:
                errors.append(f'{sym} 1d: 最新收盘时间 {h:02d}:{m:02d} 不在预期范围内')

    for sym in non_night_symbols:
        row = conn.execute('SELECT is_night FROM symbols WHERE symbol=?', (sym,)).fetchone()
        if row and row['is_night'] != 0:
            errors.append(f'{sym}: is_night={row["is_night"]} (expected 0)')
        elif not row:
            errors.append(f'{sym}: not found in symbols table')

        klines = conn.execute(
            'SELECT timestamp, open, high, low, close FROM futures_klines '
            'WHERE symbol=? AND timeframe="1d" ORDER BY timestamp DESC LIMIT 10',
            (sym,)
        ).fetchall()

        print(f'\n=== {sym} (无夜盘) 最近 {len(klines)} 根 1d K线 ===')
        
        # 检查重复日期
        date_counts = {}
        for k in klines:
            dt = datetime.fromtimestamp(k['timestamp'], tz=BJT)
            date_str = dt.strftime('%Y-%m-%d')
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        multi_dates = {d: c for d, c in date_counts.items() if c > 1}
        if multi_dates:
            for d, c in sorted(multi_dates.items()):
                errors.append(f'{sym} 1d: 日期 {d} 有 {c} 根 K 线（预期 1）')
        
        for k in klines:
            ts_str = bjt_str(k['timestamp'])
            close_time = ts_str[11:16]
            if k['high'] < k['low']:
                errors.append(f'{sym} @ {ts_str}: high < low')
            if k['high'] <= 0:
                errors.append(f'{sym} @ {ts_str}: price <= 0')
            
            # 无夜盘品种应收盘在 15:00
            dt = datetime.fromtimestamp(k['timestamp'], tz=BJT)
            if dt.hour != 15 or dt.minute != 0:
                errors.append(f'{sym} 1d: 收盘 {close_time} 应为 15:00')
            
            print(f'  {ts_str} | O={k["open"]:.1f} H={k["high"]:.1f} L={k["low"]:.1f} C={k["close"]:.1f} | 收盘BJT={close_time}')

    print(f'\n{"="*60}')
    if errors:
        print(f'\nFAILED: {len(errors)} errors found:')
        for e in errors:
            print(f'  ❌ {e}')
    else:
        print('\nSUCCESS: All checks passed!')

    conn.close()
    return len(errors)

if __name__ == '__main__':
    exit(main())
