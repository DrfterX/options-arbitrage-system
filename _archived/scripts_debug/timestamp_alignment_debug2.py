#!/usr/bin/env python3
"""
Step 2.2 — 1d/1w 时间戳归一化深入分析

重点检查：
1. N 结构时间戳的分布（time-of-day 时段）
2. K 线 bar 时间戳归一化前后的分布
3. 偏差的根本原因（归一化不匹配 vs 原始时间戳不同）
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.db import Database
from config.settings import DB_PATH
from collections import Counter, defaultdict
from datetime import datetime

db = Database(DB_PATH)

_BJ_OFFSET = 8 * 3600
_TARGET_HOUR_SEC = 20700  # 05:45 UTC = 13:45 BJT
_MIDNIGHT_SEC = 57600  # 16:00 UTC = BJT 午夜

conn = db.get_conn()

# 获取有 N 型结构的品种
rows = conn.execute("""
    SELECT DISTINCT symbol, timeframe
    FROM futures_n_structures
    WHERE state != 'COMPLETED' AND timeframe IN ('1d','1w')
""").fetchall()

print("=" * 100)
print("1d/1w 时间戳对齐深度分析")
print("=" * 100)

# 1. N 结构时间戳的 time-of-day 分布
print("\n--- 1. N 结构时间戳 time-of-day 分布 ---")
tod_dist = Counter()
for r in rows:
    ns = conn.execute("""
        SELECT point_a_time, point_b_time, point_c_time
        FROM futures_n_structures
        WHERE symbol=? AND timeframe=? AND state!='COMPLETED'
        ORDER BY updated_at DESC LIMIT 1
    """, (r['symbol'], r['timeframe'])).fetchone()
    if not ns:
        continue
    for ts in [ns['point_a_time'], ns['point_b_time'], ns['point_c_time']]:
        if ts:
            tod = ts % 86400  # time of day in seconds
            tod_dist[tod] += 1

for tod, count in sorted(tod_dist.items()):
    h = tod // 3600
    m = (tod % 3600) // 60
    print(f"  {h:02d}:{m:02d} UTC ({tod:5d}s): {count} 个点")

# 2. K 线 bar 时间戳的 time-of-day 分布（1d）
print("\n--- 2. K 线 bar 时间戳 time-of-day 分布（1d）---")
tf = '1d'
bar_tod_dist = Counter()
syms_1d = [r['symbol'] for r in rows if r['timeframe'] == '1d']
for sym in syms_1d[:30]:  # 取前30个品种
    contract_row = conn.execute(
        "SELECT contract FROM futures_n_structures WHERE symbol=? AND timeframe=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
        (sym, tf)
    ).fetchone()
    if not contract_row:
        continue
    contract = contract_row['contract']
    bars = conn.execute("""
        SELECT timestamp FROM futures_klines
        WHERE symbol=? AND timeframe=? AND contract=?
        ORDER BY timestamp DESC LIMIT 30
    """, (sym, tf, contract)).fetchall()
    for b in bars:
        tod = b['timestamp'] % 86400
        bar_tod_dist[tod] += 1

for tod, count in sorted(bar_tod_dist.most_common(15)):
    h = tod // 3600
    m = (tod % 3600) // 60
    dt_str = datetime.fromtimestamp(tod + 1700000000).strftime('%H:%M UTC')  # dummy date for time display
    dt_dummy = datetime(2020, 1, 1) + __import__('datetime').timedelta(seconds=tod)
    print(f"  {dt_dummy:%H:%M} UTC ({tod:5d}s): {count} 个 bar")

# 3. 对比 N 结构时间戳 vs 归一化后 bar 时间戳
print("\n\n--- 3. 关键路径匹配测试（模拟 API 返回后的一致性）---")
print("检查: /api/klines 返回的 n_structure.at/bt/ct 与 bars[].t 的匹配情况")
print()

examples_shown = 0
for tf2 in ['1d', '1w']:
    print(f"\n=== {tf2} ===")
    tf_rows = [r for r in rows if r['timeframe'] == tf2]

    match_exact = 0
    match_after_norm = 0
    mismatch = 0
    details = []

    for r in tf_rows:
        sym = r['symbol']
        contract_row = conn.execute(
            "SELECT contract FROM futures_n_structures WHERE symbol=? AND timeframe=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
            (sym, tf2)
        ).fetchone()
        if not contract_row:
            continue
        contract = contract_row['contract']

        ns = conn.execute("""
            SELECT * FROM futures_n_structures
            WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED'
            ORDER BY updated_at DESC LIMIT 1
        """, (sym, contract, tf2)).fetchone()
        if not ns:
            continue
        ns = dict(ns)

        # 获取 K 线 bar
        bars = conn.execute("""
            SELECT timestamp, open, high, low, close, volume
            FROM futures_klines
            WHERE symbol=? AND timeframe=? AND contract=?
            ORDER BY timestamp DESC
        """, (sym, tf2, contract)).fetchall()

        if not bars:
            continue

        bar_list = [dict(b) for b in bars]

        # 去重+排序
        from datetime import datetime as dt2
        seen = {}
        for bar in bar_list:
            dtt = dt2.fromtimestamp(bar['timestamp'])
            if tf2 == '1d':
                key = dtt.strftime("%Y-%m-%d")
            else:
                iso = dtt.isocalendar()
                key = f"{iso[0]}-W{iso[1]:02d}"
            if key not in seen or bar['timestamp'] > seen[key]['timestamp']:
                seen[key] = bar
        bar_list = sorted(seen.values(), key=lambda x: x['timestamp'])

        # 时间戳归一化（模拟 API）
        for bar in bar_list:
            bar['t'] = bar['timestamp']
            ts = bar['timestamp']
            if ts % 86400 == _MIDNIGHT_SEC:
                bj_midnight_utc = ((ts + _BJ_OFFSET) // 86400) * 86400 - _BJ_OFFSET
                bar['t'] = bj_midnight_utc + _TARGET_HOUR_SEC

        # 取最后 200 条
        proc_bars = bar_list[-200:] if len(bar_list) > 200 else bar_list

        for label, ts_key in [('A', 'point_a_time'), ('B', 'point_b_time'), ('C', 'point_c_time')]:
            n_ts = ns.get(ts_key)
            if n_ts is None:
                continue

            # 在归一化后的 bars 中找最近匹配
            best_idx = -1
            best_dist = float('inf')
            for i, bar in enumerate(proc_bars):
                dist = abs(bar['t'] - n_ts)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i

            matched_bar_ts = proc_bars[best_idx]['t'] if best_idx >= 0 else None

            # 检查该 bar 是否与 N 结构 timestamps 在同一天/周
            d_n = dt2.fromtimestamp(n_ts)
            d_m = dt2.fromtimestamp(matched_bar_ts) if matched_bar_ts else None

            same_period = False
            if d_m:
                if tf2 == '1d':
                    same_period = d_n.strftime('%Y-%m-%d') == d_m.strftime('%Y-%m-%d')
                else:
                    same_period = d_n.isocalendar()[:2] == d_m.isocalendar()[:2]

            if best_dist <= 3600:
                match_exact += 1
            elif same_period and best_dist > 3600:
                # Same period but wrong time of day
                match_after_norm += 1
                if len(details) < 8:
                    details.append({
                        'sym': sym, 'pt': label, 'dist': best_dist,
                        'n_ts': n_ts, 'n_dt': d_n.strftime('%Y-%m-%d %H:%M'),
                        'm_dt': d_m.strftime('%Y-%m-%d %H:%M') if d_m else 'N/A',
                        'n_tod': n_ts % 86400, 'm_tod': matched_bar_ts % 86400 if matched_bar_ts else '?',
                        'n_norm': n_ts % 86400 == _MIDNIGHT_SEC,
                        'm_norm': matched_bar_ts % 86400 == _MIDNIGHT_SEC if matched_bar_ts else False,
                    })
            else:
                mismatch += 1

    total = match_exact + match_after_norm + mismatch
    print(f"  精确匹配 (≤1h): {match_exact}/{total}")
    print(f"  同周期但时间偏移: {match_after_norm}/{total}")
    print(f"  完全不匹配: {mismatch}/{total}")

    if details:
        print(f"\n  同周期时间偏移详情（按偏差排序）:")
        for d in sorted(details, key=lambda x: x['dist'])[:6]:
            n_ts_orig = d['n_ts']
            # 如果 N 结构时间戳本身是 16:00 UTC 格式但 bar 归一化到了 05:45 UTC
            m_norm_note = ""
            if d['m_tod'] == _MIDNIGHT_SEC:
                m_norm_note = " (在bar中是16:00→未归一化)"
            elif d['m_tod'] == _TARGET_HOUR_SEC:
                m_norm_note = " (在bar中是16:00→归一化到05:45)"
            elif d['m_tod'] == 0:
                m_norm_note = " (在bar中是00:00→未归一化)"

            n_norm_note = ""
            if d['n_tod'] == _MIDNIGHT_SEC:
                n_norm_note = " (N结构=16:00)"
            elif d['n_tod'] == _TARGET_HOUR_SEC:
                n_norm_note = " (N结构=05:45)"
            elif d['n_tod'] == 0:
                n_norm_note = " (N结构=00:00)"

            print(f"    {d['sym']} {d['pt']}: N={d['n_dt']}{n_norm_note}, bar={d['m_dt']}{m_norm_note}, 偏差={d['dist']}s")

conn.close()
print("\n\n分析完成")
