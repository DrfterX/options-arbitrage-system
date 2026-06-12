#!/usr/bin/env python3
"""
N型信号评分诊断 — 为什么全部 score=0.30？

关键发现（预热）：
- futures_signals 表用 created_at TEXT 列，没有 timestamp 列
- 表结构：id, symbol, contract, direction, signal_type,
  level1_pass, level2_pass, level3_pass, entry_price, stop_loss,
  take_profit, score, detail (JSON), created_at
"""

import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import Database
from config.settings import (
    LEVEL1_TIMEFRAME, LEVEL1_MACD_TIMEFRAME,
    LEVEL2_TIMEFRAME, LEVEL2_MACD_TIMEFRAME,
    LEVEL3_TIMEFRAME, LEVEL3_STABILITY_TIMEFRAME,
    DB_PATH,
)

db = Database(DB_PATH)

print("=" * 70)
print("1. 品种N型结构概览")
print("=" * 70)

with db.get_conn() as conn:
    contracts = conn.execute("""
        SELECT DISTINCT s.symbol, s.name, k.contract as contract_code
        FROM symbols s
        INNER JOIN (SELECT DISTINCT symbol, contract FROM futures_klines) k
          ON s.symbol = k.symbol
        WHERE s.has_options = 1 AND k.contract != s.symbol
        ORDER BY s.symbol
    """).fetchall()

l1_ok = 0
l2_ok_consistent = 0
for c in contracts:
    sym, name, contr = c["symbol"], c["name"], c["contract_code"]
    l1 = conn.execute(
        "SELECT state, direction FROM futures_n_structures "
        "WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED' "
        "ORDER BY updated_at DESC LIMIT 1",
        (sym, contr, LEVEL1_TIMEFRAME)
    ).fetchone()
    l2 = conn.execute(
        "SELECT state, direction FROM futures_n_structures "
        "WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED' "
        "ORDER BY updated_at DESC LIMIT 1",
        (sym, contr, LEVEL2_TIMEFRAME)
    ).fetchone()

    l1_s = f"L1:{l1['state']}/{l1['direction']}" if l1 else "L1:无"
    l2_s = f"L2:{l2['state']}/{l2['direction']}" if l2 else "L2:无"
    l1_passable = l1 and l1["state"] in ("LEG2", "LEG3")
    l2_ok = l1_passable and l2 and l2["direction"] == l1["direction"] and l2["state"] in ("LEG2", "LEG3")
    if l1_passable: l1_ok += 1
    if l2_ok: l2_ok_consistent += 1
    mark = "✅L1+L2" if l2_ok else ("✅L1" if l1_passable else "❌")
    print(f"  {sym:6s} {name:<8} {l1_s:20s} {l2_s:20s} {mark}")

print(f"\nL1(周线LEG2/3)可过: {l1_ok}/{len(contracts)}")
print(f"L1+L2方向一致且活跃: {l2_ok_consistent}/{len(contracts)}")

print()
print("=" * 70)
print("2. 今日信号评分诊断")
print("=" * 70)

with db.get_conn() as conn:
    # 用 created_at（TEXT, 'YYYY-MM-DD HH:MM:SS'）
    today = conn.execute(
        "SELECT * FROM futures_signals "
        "WHERE created_at >= '2026-06-11'"
    ).fetchall()
    print(f"今日信号: {len(today)} 条")

    score_dist = conn.execute(
        "SELECT score, COUNT(*) as cnt FROM futures_signals "
        "WHERE created_at >= '2026-06-11' GROUP BY score ORDER BY score"
    ).fetchall()
    print("评分分布:")
    for r in score_dist:
        print(f"  score={r['score']:.2f}: {r['cnt']} 条")

    # 分级通过率
    lev = conn.execute(
        "SELECT SUM(level1_pass) as l1, SUM(level2_pass) as l2, "
        "SUM(level3_pass) as l3, COUNT(*) as total "
        "FROM futures_signals WHERE created_at >= '2026-06-11'"
    ).fetchone()
    print(f"\nLevel通过率:")
    print(f"  Level1: {lev['l1']}/{lev['total']}")
    print(f"  Level2: {lev['l2']}/{lev['total']}")
    print(f"  Level3: {lev['l3']}/{lev['total']}")

    # 只看今天生成的信号detail，判断瓶颈在哪一级
    # 找 level1_pass=1 的信号
    l1_yes = conn.execute(
        "SELECT COUNT(*) as c FROM futures_signals "
        "WHERE created_at >= '2026-06-11' AND level1_pass=1"
    ).fetchone()['c']
    print(f"\nL1已通过品种: {l1_yes}")

    if l1_yes > 0:
        l2_fails = conn.execute(
            "SELECT symbol, contract, score, detail FROM futures_signals "
            "WHERE created_at >= '2026-06-11' AND level1_pass=1 AND level2_pass=0 "
            "LIMIT 10"
        ).fetchall()
        print(f"L1通过但L2失败的信号: {len(l2_fails)} 条示例:")
        for s in l2_fails:
            print(f"  {s['symbol']:6s} {s['contract']:10s} score={s['score']:.2f}")
            if s['detail']:
                d = json.loads(s['detail']) if isinstance(s['detail'], str) else s['detail']
                l2 = d.get('level2', {})
                reason = l2.get('reason', 'N/A')
                mt = l2.get('macd_trajectory', {})
                print(f"    reason: {reason}")
                for legk in ['leg1', 'leg2', 'leg3']:
                    leg = mt.get(legk, {})
                    if isinstance(leg, dict):
                        print(f"      {legk}: passed={leg.get('passed')} detail={leg.get('detail','')[:100]}")

print()
print("=" * 70)
print("3. 手动 evaluate 诊断（每个品种逐级fail点）")
print("=" * 70)

test_symbols = ["RB","P","MA","SC","I","AG","AU","CF","C","SR"]
with db.get_conn() as conn:
    for sym in test_symbols:
        # 找合约
        row = conn.execute(
            "SELECT contract FROM futures_klines WHERE symbol=? AND contract!=? "
            "GROUP BY contract ORDER BY MAX(timestamp) DESC LIMIT 1",
            (sym, sym)
        ).fetchone()
        if not row: continue
        contract = row['contract']

        # 直接查L1 N型结构
        l1 = conn.execute(
            "SELECT direction, state, point_a_price, point_b_price FROM futures_n_structures "
            "WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED' "
            "ORDER BY updated_at DESC LIMIT 1",
            (sym, contract, LEVEL1_TIMEFRAME)
        ).fetchone()

        if l1 and l1['state'] in ("LEG2", "LEG3"):
            direction = l1['direction']
            # L2 N型结构
            l2 = conn.execute(
                "SELECT direction, state, point_a_time, point_b_time, point_c_time "
                "FROM futures_n_structures "
                "WHERE symbol=? AND contract=? AND timeframe=? AND state!='COMPLETED' "
                "ORDER BY updated_at DESC LIMIT 1",
                (sym, contract, LEVEL2_TIMEFRAME)
            ).fetchone()

            if l2 and l2['direction'] == direction and l2['state'] in ("LEG2", "LEG3"):
                # 检查15m MACD轨迹验证
                a, b, c = l2['point_a_time'], l2['point_b_time'], l2['point_c_time']
                ab_gap = abs(b - a) if a and b else 86400 * 30
                window_b = min(ab_gap // 3, 86400 * 15)
                window_b = max(window_b, 3600)

                # 检查腿1: A点 - BLUE→RED (SHORT) 或 RED→BLUE (LONG)
                leg1_before = conn.execute(
                    "SELECT color, histogram FROM futures_macd "
                    "WHERE symbol=? AND timeframe='15m' AND timestamp>=? AND timestamp<=? "
                    "ORDER BY timestamp ASC",
                    (sym, a - window_b, a)
                ).fetchall()
                if len(leg1_before) > 3: leg1_before = leg1_before[-3:]

                leg1_after = conn.execute(
                    "SELECT color, histogram FROM futures_macd "
                    "WHERE symbol=? AND timeframe='15m' AND timestamp>=? AND timestamp<=? "
                    "ORDER BY timestamp ASC",
                    (sym, a, a + window_b)
                ).fetchall()
                if len(leg1_after) > 3: leg1_after = leg1_after[:3]

                leg1_colors_b = [r['color'] for r in leg1_before if r['color'] in ('RED','BLUE')]
                leg1_colors_a = [r['color'] for r in leg1_after if r['color'] in ('RED','BLUE')]

                if direction == 'SHORT':
                    expect_b = 'RED'  # A点为峰, 前面应是RED
                    expect_a = 'BLUE' # 之后应有BLUE
                    l1_b_dom = max(set(leg1_colors_b), key=leg1_colors_b.count) if leg1_colors_b else None
                    l1_a_dom = max(set(leg1_colors_a), key=leg1_colors_a.count) if leg1_colors_a else None
                    leg1_pass = l1_b_dom == 'RED' and l1_a_dom == 'BLUE'
                    if not leg1_pass:
                        print(f"  {sym:6s} {contract:10s} 📛 腿1失败: A前主体{l1_b_dom}(需RED) A后主体{l1_a_dom}(需BLUE)")
                        continue
                    leg1_detail = f"前{l1_b_dom}({len(leg1_colors_b)}根)→后{l1_a_dom}({len(leg1_colors_a)}根)"
                else:
                    expect_b = 'BLUE' # A点为谷, 前面应是BLUE
                    expect_a = 'RED'  # 之后应有RED
                    l1_b_dom = max(set(leg1_colors_b), key=leg1_colors_b.count) if leg1_colors_b else None
                    l1_a_dom = max(set(leg1_colors_a), key=leg1_colors_a.count) if leg1_colors_a else None
                    leg1_pass = l1_b_dom == 'BLUE' and l1_a_dom == 'RED'
                    if not leg1_pass:
                        print(f"  {sym:6s} {contract:10s} 📛 腿1失败: A前主体{l1_b_dom}(需BLUE) A后主体{l1_a_dom}(需RED)")
                        continue
                    leg1_detail = f"前{l1_b_dom}({len(leg1_colors_b)}根)→后{l1_a_dom}({len(leg1_colors_a)}根)"

                # 检查腿2: B点
                window_a = min(ab_gap // 3, 86400 * 30)
                window_a = max(window_a, 3600)

                leg2_before = conn.execute(
                    "SELECT color, histogram FROM futures_macd "
                    "WHERE symbol=? AND timeframe='15m' AND timestamp>=? AND timestamp<=? "
                    "ORDER BY timestamp ASC",
                    (sym, b - window_a, b)
                ).fetchall()
                if len(leg2_before) > 3: leg2_before = leg2_before[-3:]

                leg2_after = conn.execute(
                    "SELECT color, histogram FROM futures_macd "
                    "WHERE symbol=? AND timeframe='15m' AND timestamp>=? AND timestamp<=? "
                    "ORDER BY timestamp ASC",
                    (sym, b, b + window_a)
                ).fetchall()
                if len(leg2_after) > 3: leg2_after = leg2_after[:3]

                leg2_b_colors = [r['color'] for r in leg2_before if r['color'] in ('RED','BLUE')]
                leg2_a_colors = [r['color'] for r in leg2_after if r['color'] in ('RED','BLUE')]

                if direction == 'SHORT':
                    # B点为谷, 前应BLUE 后应RED
                    l2_b_dom = max(set(leg2_b_colors), key=leg2_b_colors.count) if leg2_b_colors else None
                    l2_a_dom = max(set(leg2_a_colors), key=leg2_a_colors.count) if leg2_a_colors else None
                    leg2_pass = l2_b_dom == 'BLUE' and l2_a_dom == 'RED'
                    stage = f"📛 腿2失败: B前主体{l2_b_dom}(需BLUE) B后主体{l2_a_dom}(需RED)" if not leg2_pass else ""
                else:
                    l2_b_dom = max(set(leg2_b_colors), key=leg2_b_colors.count) if leg2_b_colors else None
                    l2_a_dom = max(set(leg2_a_colors), key=leg2_a_colors.count) if leg2_a_colors else None
                    leg2_pass = l2_b_dom == 'RED' and l2_a_dom == 'BLUE'
                    stage = f"📛 腿2失败: B前主体{l2_b_dom}(需RED) B后主体{l2_a_dom}(需BLUE)" if not leg2_pass else ""

                if not leg2_pass:
                    print(f"  {sym:6s} {contract:10s} {stage}")
                else:
                    print(f"  {sym:6s} {contract:10s} ✅ L1+L2全过 (方向{direction})")
            elif l2:
                print(f"  {sym:6s} {contract:10s} 📛 L2方向/状态不匹配: dir={l2['direction']} state={l2['state']}")
            else:
                print(f"  {sym:6s} {contract:10s} 📛 无小时线N型结构")
        else:
            state = l1['state'] if l1 else '无'
            print(f"  {sym:6s}             📛 L1不过: state={state}")

print()
print("=" * 70)
print("4. 加分项(MACD更大周期配合)分析")
print("=" * 70)
with db.get_conn() as conn:
    from datetime import datetime as dt
    for tf, label in [("1w", "周线MACD"), ("1d", "日线MACD"), ("15m", "15分钟MACD")]:
        cnt = conn.execute(
            "SELECT COUNT(DISTINCT symbol) as c FROM futures_macd WHERE timeframe=?", (tf,)
        ).fetchone()['c']
        latest = conn.execute(
            "SELECT symbol, timestamp FROM futures_macd WHERE timeframe=? "
            "ORDER BY timestamp DESC LIMIT 3", (tf,)
        ).fetchall()
        print(f"\n{label} ({tf}): {cnt}品种有数据")
        for r in latest:
            ts_str = dt.fromtimestamp(r['timestamp']).strftime('%m-%d %H:%M') if r['timestamp'] else '?'
            print(f"  {r['symbol']:8s} 最新:{ts_str}")

    # 加分项配置要求 "1mon" 周期
    print("\n加分项检查 (BONUS_CHECKS): [(1mon, 1w, 0.15), (1d, 1h, 0.10)]")
    has_monthly = conn.execute(
        "SELECT COUNT(DISTINCT symbol) as c FROM futures_macd WHERE timeframe='1mon'"
    ).fetchone()['c']
    print(f"月线MACD数据: {has_monthly}品种有")
    has_1h = conn.execute(
        "SELECT COUNT(DISTINCT symbol) as c FROM futures_macd WHERE timeframe='1h'"
    ).fetchone()['c']
    print(f"小时线MACD数据: {has_1h}品种有")

print()
print("=" * 70)
print("5. 评分算法根因总结")
print("=" * 70)

with db.get_conn() as conn:
    all_sigs = conn.execute(
        "SELECT COUNT(*) as c FROM futures_signals"
    ).fetchone()['c']
    print(f"历史信号总量: {all_sigs}")

    if all_sigs > 0:
        hist_stats = conn.execute(
            "SELECT MIN(score) as min_s, MAX(score) as max_s, "
            "AVG(score) as avg_s, "
            "SUM(CASE WHEN level2_pass=1 THEN 1 ELSE 0 END) as l2_cnt "
            "FROM futures_signals"
        ).fetchone()
        print(f"历史评分范围: {hist_stats['min_s']:.2f} ~ {hist_stats['max_s']:.2f} (均值{hist_stats['avg_s']:.2f})")
        print(f"历史L2通过数: {hist_stats['l2_cnt']}")
        l2_passers = conn.execute(
            "SELECT symbol, score, direction FROM futures_signals "
            "WHERE level2_pass=1 ORDER BY score DESC LIMIT 10"
        ).fetchall()
        if l2_passers:
            print(f"历史L2通过信号 (TOP10):")
            for r in l2_passers:
                print(f"  {r['symbol']:6s} score={r['score']:.2f} dir={r['direction']}")

db.close()

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
