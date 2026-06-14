#!/usr/bin/env python3
"""
Step 1.4 — MACD 数据覆盖与阈值分析

分析 DB 中 MACD 数据和 K 线数据的实际覆盖情况。
解答两个核心问题：
1. 日线MACD腿1为什么 165/167 "转折前无MACD数据"？
2. 3m 数据是否真的不存在？

用法: uv run python scripts/macd_data_analysis.py
"""

import sys
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import Database
from config.settings import DB_PATH

TZ = timezone(timedelta(hours=8))  # Asia/Shanghai

def ts_to_cst(ts):
    """Unix秒 → CST 可读时间"""
    return datetime.fromtimestamp(ts, tz=TZ).strftime("%Y-%m-%d %H:%M")

def print_sep(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

db = Database(DB_PATH)

# =============================================================
# 1. MACD 数据整体覆盖
# =============================================================
print_sep("1. MACD 数据整体覆盖")

macd_timeframes = {}
with db.get_conn() as conn:
    for tf in ["1d", "1w", "15m", "1h", "3m"]:
        count = conn.execute(
            "SELECT COUNT(*) as cnt FROM futures_macd WHERE timeframe=?", (tf,)
        ).fetchone()["cnt"]
        earliest = conn.execute(
            "SELECT MIN(timestamp) as ts FROM futures_macd WHERE timeframe=?", (tf,)
        ).fetchone()["ts"]
        latest = conn.execute(
            "SELECT MAX(timestamp) as ts FROM futures_macd WHERE timeframe=?", (tf,)
        ).fetchone()["ts"]
        contracts = conn.execute(
            "SELECT COUNT(DISTINCT contract) as cnt FROM futures_macd WHERE timeframe=?", (tf,)
        ).fetchone()["cnt"]
        symbols = conn.execute(
            "SELECT COUNT(DISTINCT symbol) as cnt FROM futures_macd WHERE timeframe=?", (tf,)
        ).fetchone()["cnt"]
        macd_timeframes[tf] = {
            "count": count,
            "earliest": earliest,
            "latest": latest,
            "contracts": contracts,
            "symbols": symbols,
        }

for tf, info in sorted(macd_timeframes.items()):
    e = ts_to_cst(info["earliest"]) if info["earliest"] else "-"
    l = ts_to_cst(info["latest"]) if info["latest"] else "-"
    span = ""
    if info["earliest"] and info["latest"]:
        days = (info["latest"] - info["earliest"]) / 86400
        span = f" ({days:.0f} 天)"
    print(f"  MACD {tf:4s}: {info['count']:>8} 行 | 最早 {e} | 最晚 {l}{span} | {info['contracts']:>3} 合约 | {info['symbols']:>3} 品种")

# =============================================================
# 2. 1d MACD 数据 — 逐合约覆盖率
# =============================================================
print_sep("2. 1d MACD 逐合约分析与周线N结构A点时间对比")

# 获取周线 N 结构中每个合约的 swing point 时间
n_structures = {}
with db.get_conn() as conn:
    rows = conn.execute(
        """SELECT DISTINCT n.symbol, n.contract, n.point_a_time, n.point_b_time,
                  n.direction, n.state
           FROM futures_n_structures n
           WHERE n.timeframe='1w' AND n.state!='COMPLETED'
           ORDER BY n.symbol"""
    ).fetchall()
    for r in rows:
        key = (r["symbol"], r["contract"])
        n_structures[key] = {
            "point_a_time": r["point_a_time"],
            "point_b_time": r["point_b_time"],
            "direction": r["direction"],
            "state": r["state"],
        }
    print(f"  周线N型(非COMPLETED): {len(n_structures)} 个")

# 获取 1d MACD 的每个合约最早/最晚时间
macd_1d_by_contract = {}
with db.get_conn() as conn:
    rows = conn.execute(
        """SELECT symbol, contract,
                  MIN(timestamp) as earliest, MAX(timestamp) as latest,
                  COUNT(*) as cnt,
                  MIN(timestamp) as first_color_time
           FROM futures_macd
           WHERE timeframe='1d'
           GROUP BY symbol, contract
           ORDER BY earliest"""
    ).fetchall()
    for r in rows:
        key = (r["symbol"], r["contract"])
        macd_1d_by_contract[key] = {
            "earliest": r["earliest"],
            "latest": r["latest"],
            "count": r["cnt"],
        }
    print(f"  1d MACD 有数据的合约: {len(macd_1d_by_contract)} 个")

# 分析 N 结构的 A 点时间 vs MACD 最早时间
ok_count = 0
no_macd = 0
a_before_macd = 0  # A点早于MACD最早数据
a_covered = 0
no_a_time = 0

for key, n_info in n_structures.items():
    a_time = n_info["point_a_time"]
    if not a_time:
        no_a_time += 1
        continue
    if key not in macd_1d_by_contract:
        no_macd += 1
        continue
    macd_info = macd_1d_by_contract[key]
    macd_earliest = macd_info["earliest"]
    # 腿1需要A点前的MACD数据，窗口约3根日线=3天
    min_need = a_time - 3 * 86400  # 至少需要A点前3天的MACD
    if macd_earliest and macd_earliest <= min_need:
        a_covered += 1
    if macd_earliest and macd_earliest <= a_time:
        ok_count += 1
    else:
        a_before_macd += 1

print(f"\n  --- N型A点 vs 1d MACD 覆盖分析 ---")
total_n = len(n_structures)
print(f"  周线N型(非COMPLETED)总数: {total_n}")
print(f"  无A点时间:          {no_a_time}")
print(f"  合约无1d MACD数据:  {no_macd}")
print(f"  有MACD但A点早于MACD最早数据: {a_before_macd}")
print(f"  有MACD且A点晚于MACD最早数据: {ok_count}")
print(f"  腿1窗口(3天)可覆盖: {a_covered}")

# 显示10个典型样本
print(f"\n  --- 典型样本（最早/最晚MACD vs A点）---")
samples = []
for key, n_info in n_structures.items():
    a_time = n_info["point_a_time"]
    if not a_time:
        continue
    if key in macd_1d_by_contract:
        macd_info = macd_1d_by_contract[key]
        gap_days = (a_time - macd_info["earliest"]) / 86400 if macd_info["earliest"] else 0
        samples.append((gap_days, key[0], key[1], a_time, macd_info["earliest"], macd_info["count"]))
    else:
        samples.append((-99999, key[0], key[1], a_time, 0, 0))
samples.sort()

print(f"  {'合约':8s} | {'A点时间':20s} | {'MACD最早':20s} | {'差距(天)':8s} | {'行数':6s}")
print(f"  {'-'*8}-+-{'-'*20}-+-{'-'*20}-+-{'-'*8}-+-{'-'*6}")
for gap, sym, ctr, a_time, me, cnt in samples[:15]:
    a_str = ts_to_cst(a_time) if a_time else "-"
    m_str = ts_to_cst(me) if me else "无MACD数据"
    gap_str = f"{gap:.0f}" if gap > -9999 else "无MACD"
    print(f"  {sym+'_'+ctr:10s} | {a_str:20s} | {m_str:20s} | {gap_str:>8s} | {cnt:6d}")

# =============================================================
# 3. 3m 数据检查
# =============================================================
print_sep("3. 3m K线数据与MACD数据覆盖")

with db.get_conn() as conn:
    # K线数据
    k3m_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM futures_klines WHERE timeframe='3m'"
    ).fetchone()["cnt"]
    k3m_earliest = conn.execute(
        "SELECT MIN(timestamp) as ts FROM futures_klines WHERE timeframe='3m'"
    ).fetchone()["ts"]
    k3m_latest = conn.execute(
        "SELECT MAX(timestamp) as ts FROM futures_klines WHERE timeframe='3m'"
    ).fetchone()["ts"]
    k3m_contracts = conn.execute(
        "SELECT COUNT(DISTINCT contract) as cnt FROM futures_klines WHERE timeframe='3m'"
    ).fetchone()["cnt"]
    k3m_symbols = conn.execute(
        "SELECT COUNT(DISTINCT symbol) as cnt FROM futures_klines WHERE timeframe='3m'"
    ).fetchone()["cnt"]

    # MACD数据
    m3m_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM futures_macd WHERE timeframe='3m'"
    ).fetchone()["cnt"]
    m3m_earliest = conn.execute(
        "SELECT MIN(timestamp) as ts FROM futures_macd WHERE timeframe='3m'"
    ).fetchone()["ts"]
    m3m_latest = conn.execute(
        "SELECT MAX(timestamp) as ts FROM futures_macd WHERE timeframe='3m'"
    ).fetchone()["ts"]
    m3m_contracts = conn.execute(
        "SELECT COUNT(DISTINCT contract) as cnt FROM futures_macd WHERE timeframe='3m'"
    ).fetchone()["cnt"]

    print(f"  【3m K线】")
    print(f"    行数: {k3m_count}")
    print(f"    最早: {ts_to_cst(k3m_earliest) if k3m_earliest else 'N/A'}")
    print(f"    最晚: {ts_to_cst(k3m_latest) if k3m_latest else 'N/A'}")
    print(f"    合约数: {k3m_contracts}")
    print(f"    品种数: {k3m_symbols}")

    print(f"\n  【3m MACD】")
    print(f"    行数: {m3m_count}")
    print(f"    最早: {ts_to_cst(m3m_earliest) if m3m_earliest else 'N/A'}")
    print(f"    最晚: {ts_to_cst(m3m_latest) if m3m_latest else 'N/A'}")
    print(f"    合约数: {m3m_contracts}")
    print(f"    品种数: {m3m_contracts}")

    # 其他时间范围的K线和MACD
    print(f"\n  --- 各周期数据量对比（K线 / MACD）---")
    for tf in ["1m", "3m", "15m", "1h", "1d", "1w"]:
        k_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM futures_klines WHERE timeframe=?", (tf,)
        ).fetchone()["cnt"]
        m_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM futures_macd WHERE timeframe=?", (tf,)
        ).fetchone()["cnt"]
        k_earliest = conn.execute(
            "SELECT MIN(timestamp) as ts FROM futures_klines WHERE timeframe=?", (tf,)
        ).fetchone()["ts"]
        m_earliest = conn.execute(
            "SELECT MIN(timestamp) as ts FROM futures_macd WHERE timeframe=?", (tf,)
        ).fetchone()["ts"]
        k_str = ts_to_cst(k_earliest) if k_earliest else "无数据"
        m_str = ts_to_cst(m_earliest) if m_earliest else "无数据"
        print(f"    {tf:4s}: K线 {k_count:>8} 行(最早{k_str}) | MACD {m_count:>8} 行(最早{m_str})")

# =============================================================
# 4. MACD腿1失败原因深度分析 — 窗口 vs 数据可用性
# =============================================================
print_sep("4. MACD腿1失败原因深度解剖")

# 取一个无MACD数据的典型品种，分析窗口
with db.get_conn() as conn:
    sample = conn.execute(
        """SELECT n.symbol, n.contract, n.point_a_time, n.point_b_time,
                  n.direction, n.state
           FROM futures_n_structures n
           WHERE n.timeframe='1w' AND n.state='ACTIVE'
           LIMIT 1"""
    ).fetchone()
    if sample:
        sym = sample["symbol"]
        ctr = sample["contract"]
        a_time = sample["point_a_time"]
        b_time = sample["point_b_time"]
        ab_gap = abs(b_time - a_time) if b_time and a_time else 86400 * 30
        window_a = min(ab_gap // 3, 86400 * 30)
        min_window = 259200  # 3 days for "1d"
        window_a = max(window_a, min_window)

        print(f"  示例品种: {sym}_{ctr}")
        print(f"  A点时间: {ts_to_cst(a_time) if a_time else 'N/A'}")
        print(f"  B点时间: {ts_to_cst(b_time) if b_time else 'N/A'}")
        print(f"  AB间隔: {ab_gap/86400:.0f} 天")
        print(f"  window_a (查询A点前MACD窗口): {window_a/86400:.0f} 天")
        print(f"  查询范围: {ts_to_cst(a_time - window_a)} ~ {ts_to_cst(a_time)}")

        # 检查该品种是否有1d MACD数据
        macd_rows = conn.execute(
            """SELECT timestamp, color FROM futures_macd
               WHERE symbol=? AND contract=? AND timeframe='1d'
               ORDER BY timestamp ASC""",
            (sym, ctr)
        ).fetchall()
        print(f"  该品种1d MACD行数: {len(macd_rows)}")
        if macd_rows:
            first_ts = macd_rows[0]["timestamp"]
            last_ts = macd_rows[-1]["timestamp"]
            print(f"  最早MACD: {ts_to_cst(first_ts)}")
            print(f"  最晚MACD: {ts_to_cst(last_ts)}")
            print(f"  A点 vs 最早MACD差距: {(a_time - first_ts)/86400:.1f} 天")

            # 检查窗口内是否有MACD数据
            window_start = a_time - window_a
            covering = [r for r in macd_rows if window_start <= r["timestamp"] <= a_time]
            print(f"  窗口内MACD行数: {len(covering)}")
            if covering:
                print(f"  窗口内颜色: {[r['color'] for r in covering]}")
            else:
                print(f"  ❌ 窗口内无MACD数据！")
                # 检查最近的MACD距离
                recent = [r for r in macd_rows if r["timestamp"] <= a_time]
                if recent:
                    nearest = recent[-1]
                    gap = (a_time - nearest["timestamp"]) / 86400
                    print(f"  最近MACD数据在A点前 {gap:.1f} 天 ({ts_to_cst(nearest['timestamp'])})")
                else:
                    print(f"  所有MACD数据都在A点之后")

# =============================================================
# 5. 3m数据缺失的根本原因分析
# =============================================================
print_sep("5. 3m数据缺失根本原因")

print("  原因分析:")
print("  1. AKSHARE_PERIODS 不包含 '3m' (只有 1m, 15m, 1h, 1d, 1w)")
print("  2. 3m K线数据由 backfill_3m_data.py 从 1m K线合成")
print("  3. 3m MACD由 3m K线计算（仅在有3m K线时生成）")
print("  4. 存档保留策略: klines 3m=30天, macd=90天")

# 检查 1m K线数据，因为3m依赖它
with db.get_conn() as conn:
    k1m_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM futures_klines WHERE timeframe='1m'"
    ).fetchone()["cnt"]
    k1m_earliest = conn.execute(
        "SELECT MIN(timestamp) as ts FROM futures_klines WHERE timeframe='1m'"
    ).fetchone()["ts"]
    k1m_latest = conn.execute(
        "SELECT MAX(timestamp) as ts FROM futures_klines WHERE timeframe='1m'"
    ).fetchone()["ts"]
    k1m_contracts = conn.execute(
        "SELECT COUNT(DISTINCT contract) as cnt FROM futures_klines WHERE timeframe='1m'"
    ).fetchone()["cnt"]

    print(f"\n  1m K线: {k1m_count} 行, {k1m_contracts} 合约")
    if k1m_earliest:
        print(f"  1m K线范围: {ts_to_cst(k1m_earliest)} ~ {ts_to_cst(k1m_latest)}")
        covered_days = (k1m_latest - k1m_earliest) / 86400
        print(f"  覆盖天数: {covered_days:.0f} 天")

    # 检查 backfill_3m 是否运行过
    backfill_log = conn.execute(
        "SELECT value FROM system_config WHERE key='last_backfill_3m'"
    ).fetchone()
    if backfill_log:
        print(f"\n  上次3m回填: {backfill_log['value']}")
    else:
        print(f"\n  ⚠️ 没有找到 backfill_3m 运行记录")

    # 查询实际3m数据量最大的前5个合约
    top3m = conn.execute(
        """SELECT symbol, contract, COUNT(*) as cnt,
                  MIN(timestamp) as earliest, MAX(timestamp) as latest
           FROM futures_klines
           WHERE timeframe='3m'
           GROUP BY symbol, contract
           ORDER BY cnt DESC
           LIMIT 5"""
    ).fetchall()
    if top3m:
        print(f"\n  3m K线数据最多的5个合约:")
        for r in top3m:
            days = (r["latest"] - r["earliest"]) / 86400
            print(f"    {r['symbol']}_{r['contract']}: {r['cnt']} bars, {days:.1f}天 ({ts_to_cst(r['earliest'])} ~ {ts_to_cst(r['latest'])})")
    else:
        print(f"\n  没有任何3m K线数据")

print()
print("=" * 70)
print("  分析完成")
print("=" * 70)
