#!/usr/bin/env python3
"""
Step 2 — 时间戳对齐验证（H2 检查）

检查 K 线 bar 时间戳 vs N 型结构 A/B/C 时间戳的对齐度，
特别是 1d/1w 周期的时间戳归一化是否与 K 线 bar 对齐。
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.db import Database
from config.settings import DB_PATH
db = Database(DB_PATH)

_BJ_OFFSET = 8 * 3600
_TARGET_HOUR_SEC = 20700  # 05:45 UTC = 13:45 BJT
_MIDNIGHT_SEC = 57600  # 16:00 UTC = BJT 午夜


def normalize_ts(ts):
    """模拟 K 线 API 的 1d/1w 时间戳归一化"""
    if ts % 86400 == _MIDNIGHT_SEC:
        bj_midnight_utc = ((ts + _BJ_OFFSET) // 86400) * 86400 - _BJ_OFFSET
        return bj_midnight_utc + _TARGET_HOUR_SEC
    return ts


def findBarForNPoint(bars, targetTime):
    """模拟前端的 findBarForNPoint()"""
    if targetTime is None:
        return -1, None
    bestIdx = -1
    bestDist = float('inf')
    for i, bar in enumerate(bars):
        dist = abs(bar['t'] - targetTime)
        if dist < bestDist:
            bestDist = dist
            bestIdx = i
    return bestIdx, bestDist


# 1. 获取有活跃 N 型结构的品种列表
conn = db.get_conn()
rows = conn.execute("""
    SELECT DISTINCT symbol, timeframe, contract
    FROM futures_n_structures
    WHERE state != 'COMPLETED'
    ORDER BY symbol, timeframe
""").fetchall()

print(f"=== 有活跃 N 型结构的品种×周期数: {len(rows)} ===")
print()

# 按周期分组统计
from collections import defaultdict
by_tf = defaultdict(list)
for r in rows:
    by_tf[r['timeframe']].append(r['symbol'])

for tf in ['15m', '1h', '1d', '1w']:
    syms = by_tf.get(tf, [])
    print(f"  {tf}: {len(syms)} 个品种 ({', '.join(syms[:10])}{'...' if len(syms) > 10 else ''})")
print()

# 2. 对每个品种×周期检查时间戳对齐
# 重点关注 1d/1w
target_timeframes = ['1d', '1w', '1h', '15m']

results = []
for tf in target_timeframes:
    tf_rows = [r for r in rows if r['timeframe'] == tf]

    for r in tf_rows:
        sym = r['symbol']
        contract = r['contract']

        # 获取 N 型结构
        ns = conn.execute("""
            SELECT * FROM futures_n_structures
            WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED'
            ORDER BY updated_at DESC LIMIT 1
        """, (sym, contract, tf)).fetchone()

        if not ns:
            continue

        ns = dict(ns)
        a_ts = ns.get('point_a_time')
        b_ts = ns.get('point_b_time')
        c_ts = ns.get('point_c_time')

        # 获取 K 线 bar（模拟 API 查询）
        bars = conn.execute(f"""
            SELECT k.timestamp, k.open, k.high, k.low, k.close, k.volume
            FROM futures_klines k
            INNER JOIN (
                SELECT symbol, timeframe, timestamp, contract, MAX(rowid) as max_rowid
                FROM futures_klines
                WHERE symbol=? AND timeframe=? AND contract=?
                GROUP BY symbol, timeframe, timestamp, contract
            ) sub ON k.rowid = sub.max_rowid
            ORDER BY k.timestamp DESC
        """, (sym, tf, contract)).fetchall()

        if not bars or len(bars) < 3:
            continue

        # 模拟 API 的处理：去重、排序、时间戳归一化
        bar_list = [dict(b) for b in bars]

        if tf in ('1d', '1w'):
            # 去重
            from datetime import datetime
            seen = {}
            for bar in bar_list:
                dt = datetime.fromtimestamp(bar['timestamp'])
                if tf == '1d':
                    key = dt.strftime("%Y-%m-%d")
                else:
                    iso = dt.isocalendar()
                    key = f"{iso[0]}-W{iso[1]:02d}"
                if key not in seen or bar['timestamp'] > seen[key]['timestamp']:
                    seen[key] = bar
            bar_list = sorted(seen.values(), key=lambda x: x['timestamp'])
        else:
            bar_list.reverse()

        # 时间戳归一化（仅 1d/1w）
        for bar in bar_list:
            bar['t'] = bar['timestamp']
            if tf in ('1d', '1w'):
                ts = bar['timestamp']
                if ts % 86400 == _MIDNIGHT_SEC:
                    bj_midnight_utc = ((ts + _BJ_OFFSET) // 86400) * 86400 - _BJ_OFFSET
                    bar['t'] = bj_midnight_utc + _TARGET_HOUR_SEC

        # 取最后 200 条（模拟 KLINE_MACD_BARS）
        proc_bars = bar_list[-200:] if len(bar_list) > 200 else bar_list

        # 检查 A/B/C 时间戳在 bars 中的匹配情况
        for label, ts in [('A', a_ts), ('B', b_ts), ('C', c_ts)]:
            if ts is None:
                continue
            # 检查时间戳是否被归一化了
            bar_tss = [b['t'] for b in proc_bars]

            idx, dist = findBarForNPoint(proc_bars, ts)
            if idx >= 0:
                matched_bar = proc_bars[idx]
                matched_t = matched_bar['t']
                # 检查归一化后的时间戳和原始 N 结构时间戳是否一致
                norm_ts = normalize_ts(ts) if ts % 86400 == _MIDNIGHT_SEC else ts
                normalized = ts % 86400 == _MIDNIGHT_SEC

                row_data = {
                    'sym': sym, 'tf': tf,
                    'point': label,
                    'n_timestamp': ts,
                    'n_dt': datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M UTC') if ts else 'N/A',
                    'matched_t': matched_t,
                    'matched_dt': datetime.fromtimestamp(matched_t).strftime('%Y-%m-%d %H:%M UTC') if matched_t else 'N/A',
                    'distance_sec': dist,
                    'normalized': normalized,
                    'norm_ts': norm_ts,
                    'norm_dt': datetime.fromtimestamp(norm_ts).strftime('%Y-%m-%d %H:%M UTC') if normalized and norm_ts else 'N/A',
                    'count': len(proc_bars),
                    'direction': ns.get('direction'),
                }
                results.append(row_data)

# 3. 输出统计
print("=" * 120)
print("时间戳对齐诊断报告")
print("=" * 120)

# 按周期分类
for tf in target_timeframes:
    tf_results = [r for r in results if r['tf'] == tf]
    if not tf_results:
        continue

    print(f"\n--- {tf} ---")
    print(f"  总检查点数: {len(tf_results)}")

    # 检查时间戳对齐问题
    misaligned = [r for r in tf_results if r['distance_sec'] > 3600]  # >1小时偏差
    norm_mismatch = [r for r in tf_results if r['normalized'] and r['distance_sec'] > 3600]
    exact_match = [r for r in tf_results if r['distance_sec'] == 0]
    hour_match = [r for r in tf_results if 0 < r['distance_sec'] <= 3600]

    print(f"  完全匹配 (dist=0): {len(exact_match)}/{len(tf_results)}")
    if hour_match:
        print(f"  小时级匹配 (<3600s): {len(hour_match)}/{len(tf_results)}")
    if misaligned:
        print(f"  ❌ 偏差 > 1h: {len(misaligned)}/{len(tf_results)}")
        for r in misaligned[:8]:
            note = ""
            if r['normalized']:
                note = f" [归一化: {r['n_dt']} → {r['norm_dt']}, 匹配到 {r['matched_dt']}]"
            else:
                note = f" [未归一化, 但距离={r['distance_sec']}s]"
            print(f"    {r['sym']} {r['point']}: N结构={r['n_dt']}, 匹配bar={r['matched_dt']}{note}")

    if norm_mismatch:
        print(f"\n  🔍 归一化后对齐情况:")
        # 检查归一化后的时间戳是否在 bars 中
        for r in norm_mismatch[:5]:
            norm_ts = normalize_ts(r['n_timestamp'])
            # 用归一化后的时间戳重新匹配 bars
            print(f"    {r['sym']} {r['point']}: N原始={r['n_dt']} → 归一化={r['norm_dt']}, 实际匹配={r['matched_dt']} (偏差{r['distance_sec']}s)")

# 4. 关键总结
print("\n" + "=" * 120)
print("关键发现总结")
print("=" * 120)

for tf in target_timeframes:
    tf_results = [r for r in results if r['tf'] == tf]
    if not tf_results:
        continue
    n_mismatch = len([r for r in tf_results if r['distance_sec'] > 3600])
    n_ok = len([r for r in tf_results if r['distance_sec'] <= 3600])
    n_norm = len([r for r in tf_results if r['normalized']])
    n_norm_mismatch = len([r for r in tf_results if r['normalized'] and r['distance_sec'] > 3600])

    print(f"{tf}: {n_ok}✅/{n_mismatch}❌ (归一化{n_norm}例, 归一化偏差{n_norm_mismatch}例)")

print("\n分析完成")
