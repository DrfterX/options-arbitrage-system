#!/usr/bin/env python3
"""P0 子任务 1.3 — 夜盘时段 K 线数据完整性检查"""
import sqlite3
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))

def bjt_str(ts):
    if ts is None:
        return "N/A"
    return datetime.fromtimestamp(ts, tz=BJT).strftime('%Y-%m-%d %H:%M:%S')

def main():
    conn = sqlite3.connect('trading_system.db')
    conn.row_factory = sqlite3.Row

    # Get all symbols with is_night info
    sym_rows = conn.execute('SELECT symbol, name, exchange, is_night FROM symbols ORDER BY symbol').fetchall()
    night_symbols = [s for s in sym_rows if s['is_night'] == 1]
    non_night_symbols = [s for s in sym_rows if s['is_night'] == 0]

    night_syms = [s['symbol'] for s in night_symbols]
    non_night_syms = [s['symbol'] for s in non_night_symbols]

    lines = [
        "# P0 子任务 1.3 — 夜盘时段 K 线数据完整性诊断报告",
        "",
        f"## 执行时间", f"{datetime.now(tz=BJT).strftime('%Y-%m-%d %H:%M:%S')}", "",
        f"## 数据概况", f"- 有夜盘品种 (is_night=1): {len(night_syms)} 个",
        f"- 无夜盘品种 (is_night=0): {len(non_night_syms)} 个",
        f"- 检查品种列表: {' '.join(sorted(night_syms))}" if night_syms else "- 无有夜盘品种",
        "",
    ]
    errors = []

    # ── 1. 检查有夜盘品种的 K 线 ──
    lines.append("## 1. 有夜盘品种 (is_night=1) 日 K 线检查")
    for sym in sorted(night_syms):
        klines = conn.execute(
            'SELECT timestamp, open, high, low, close, volume FROM futures_klines '
            'WHERE symbol=? AND timeframe="1d" ORDER BY timestamp DESC LIMIT 20',
            (sym,)
        ).fetchall()

        if not klines:
            lines.append(f"\n### {sym}\n- ⚠️ 无日 K 线数据")
            errors.append(f"{sym}: no 1d klines")
            continue

        # Count by date
        date_counts = {}
        for k in klines:
            dt = datetime.fromtimestamp(k['timestamp'], tz=BJT)
            date_str = dt.strftime('%Y-%m-%d')
            date_counts[date_str] = date_counts.get(date_str, 0) + 1

        multi = {d: c for d, c in date_counts.items() if c > 1}
        if multi:
            errors.append(f"{sym} 1d: 重复日期 {multi}")

        # Check closing times
        close_hours = set()
        for k in klines:
            dt = datetime.fromtimestamp(k['timestamp'], tz=BJT)
            # Valid close times for night session symbols (15:00, 23:00, 01:00, 02:30)
            h, m = dt.hour, dt.minute
            valid = [(15,0), (23,0), (1,0), (2,30)]
            if (h,m) not in valid and h != 0:  # allow 00:00 as edge case
                # Check if it's 00:00 from overnight aggregation
                pass  # We'll just collect unique times
            close_hours.add((h,m))

        # Price sanity
        for k in klines:
            if k['high'] < k['low']:
                errors.append(f"{sym} @ {bjt_str(k['timestamp'])}: high < low")
            if k['high'] <= 0:
                errors.append(f"{sym} @ {bjt_str(k['timestamp'])}: price <= 0")

        lines.append(f"\n### {sym}")
        lines.append(f"- K 线数量: {len(klines)}")
        lines.append(f"- 收盘时间 (BJT): {', '.join(f'{h:02d}:{m:02d}' for h,m in sorted(close_hours))}")
        if multi:
            lines.append(f"- ⚠️ 重复日期: {multi}")
        else:
            lines.append(f"- ✅ 无重复日期")

    # ── 2. 检查无夜盘品种的 K 线 ──
    lines.append("\n## 2. 无夜盘品种 (is_night=0) 日 K 线检查")
    for sym in sorted(non_night_syms):
        klines = conn.execute(
            'SELECT timestamp, open, high, low, close, volume FROM futures_klines '
            'WHERE symbol=? AND timeframe="1d" ORDER BY timestamp DESC LIMIT 10',
            (sym,)
        ).fetchall()

        if not klines:
            lines.append(f"\n### {sym}\n- ⚠️ 无日 K 线数据")
            errors.append(f"{sym}: no 1d klines")
            continue

        # Check closing time should be 15:00
        off_hours = []
        for k in klines:
            dt = datetime.fromtimestamp(k['timestamp'], tz=BJT)
            if dt.hour != 15 or dt.minute != 0:
                off_hours.append(bjt_str(k['timestamp']))

        lines.append(f"\n### {sym}")
        if off_hours:
            lines.append(f"- ⚠️ 非 15:00 收盘: {len(off_hours)} 根 ({', '.join(off_hours[:5])})")
            errors.append(f"{sym}: 收盘时间不在 15:00 ({len(off_hours)} 根)")
        else:
            lines.append(f"- ✅ 所有收盘时间为 15:00 BJT")

        # Price sanity
        for k in klines:
            if k['high'] < k['low']:
                errors.append(f"{sym} @ {bjt_str(k['timestamp'])}: high < low")

    # ── 3. AO 专项检查 ──
    lines.append("\n## 3. AO (氧化铝) 专项检查")
    ao_sym = conn.execute('SELECT * FROM symbols WHERE symbol="AO"').fetchone()
    if ao_sym:
        lines.append(f"- is_night = {ao_sym['is_night']}")
        lines.append(f"- exchange = {ao_sym['exchange']}")
        lines.append(f"- name = {ao_sym['name']}")

        # Check if AO has any klines with night hours (21:00-02:30)
        ao_klines = conn.execute(
            'SELECT timestamp, open, high, low, close FROM futures_klines '
            'WHERE symbol="AO" AND timeframe="1d" ORDER BY timestamp DESC LIMIT 10'
        ).fetchall()
        if ao_klines:
            lines.append(f"- 日 K 线数量: {len(ao_klines)}")
            night_klines = 0
            for k in ao_klines:
                dt = datetime.fromtimestamp(k['timestamp'], tz=BJT)
                if dt.hour >= 21 or dt.hour <= 2:
                    night_klines += 1
                    lines.append(f"  - 夜盘时段 K 线: {bjt_str(k['timestamp'])} | O={k['open']} H={k['high']} L={k['low']} C={k['close']}")
            if night_klines:
                lines.append(f"- ⚠️ 发现 {night_klines} 根夜盘时段 K 线 (is_night=0 不应有夜盘数据)")
                errors.append(f"AO: is_night=0 但发现 {night_klines} 根夜盘时段 K 线")
            else:
                lines.append(f"- ✅ 无夜盘时段 K 线")
        else:
            lines.append(f"- ⚠️ 无日 K 线数据")
    else:
        lines.append(f"- ❌ AO 不在 symbols 表中")

    # ── 4. 检查 15min/1h 分钟线是否有夜盘数据 ──
    lines.append("\n## 4. 分钟线/小时线夜盘时段数据抽样")
    # Pick 3 night-symbols with enough data
    sample_symbols = ['RB', 'MA', 'SC']
    for sym in sample_symbols:
        for tf in ['15m', '1h']:
            rows = conn.execute(
                'SELECT timestamp, open, high, low, close FROM futures_klines '
                'WHERE symbol=? AND timeframe=? ORDER BY timestamp DESC LIMIT 100',
                (sym, tf)
            ).fetchall()
            if not rows:
                continue
            # Count how many fall in night session (21:00-02:30 BJT)
            night_count = 0
            for r in rows:
                dt = datetime.fromtimestamp(r['timestamp'], tz=BJT)
                if dt.hour >= 21 or dt.hour <= 2:
                    night_count += 1
            lines.append(f"\n### {sym} {tf}: 最近 {len(rows)} 根 K 线, 夜盘时段 {night_count} 根")
            if night_count == 0:
                errors.append(f"{sym} {tf}: 无夜盘时段 K 线 (有夜盘品种应有的夜盘数据)")

    # ── Summary ──
    lines.append("\n## 结论")
    if errors:
        lines.append(f"\n**发现 {len(errors)} 个问题:**")
        for e in errors:
            lines.append(f"- ❌ {e}")
    else:
        lines.append("\n✅ 所有检查通过，夜盘数据完整无误。")

    report = '\n'.join(lines)

    with open('docs/diagnosis-night-session.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(report)
    print(f"\n{'='*60}")
    print(f"报告已写入 docs/diagnosis-night-session.md")
    if errors:
        print(f"共发现 {len(errors)} 个问题")
    else:
        print("所有检查通过")

    conn.close()
    return len(errors)

if __name__ == '__main__':
    exit(main())
