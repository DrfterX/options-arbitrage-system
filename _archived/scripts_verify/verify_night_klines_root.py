#!/usr/bin/env python3
"""
P0 子任务 1.3 — 校验 K 线算法夜盘判定完整性（数据层验证）

从 DB 读取指定品种日 K 线，检查:
1. 有夜盘品种 (RB/MA/AG/SC/I) 收盘时间戳是否符合夜盘规则
2. 无夜盘品种 (AP/CJ) 收盘时间戳是否整齐在 15:00 BJT
3. 所有 K 线 high>=low 且价格>0
"""

import os
import sqlite3
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_SCRIPT_DIR, "trading_system.db")


def ts_to_sh(ts: int) -> datetime:
    return datetime.fromtimestamp(ts, tz=BJT)


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 目标品种
    night_symbols = ["RB", "MA", "AG", "SC", "I"]
    non_night_symbols = ["AP", "CJ"]
    all_symbols = night_symbols + non_night_symbols

    # 1. 检查 symbols 表标记
    print("=" * 70)
    print("1. SYMBOLS 表 is_night 标记")
    print("=" * 70)
    for sym in all_symbols:
        r = conn.execute(
            "SELECT symbol, name, exchange, is_night FROM symbols WHERE symbol=?",
            (sym,),
        ).fetchone()
        if r:
            expected = "是" if sym in night_symbols else "否"
            actual = "是" if r["is_night"] else "否"
            status = "✓" if (r["is_night"] == 1 and sym in night_symbols) or (r["is_night"] == 0 and sym in non_night_symbols) else "✗"
            print(f"  {sym} ({r['name']}, {r['exchange']}): is_night={r['is_night']} (应为: {expected}, 实际: {actual}) {status}")
        else:
            print(f"  {sym}: NOT FOUND")

    # 2. 检查日 K 线
    print()
    print("=" * 70)
    print("2. 日 K 线时间戳校验 (最近 5 根)")
    print("=" * 70)
    print()

    all_pass = True

    for sym in all_symbols:
        # 找主力合约（数据最多的）
        contract_row = conn.execute(
            "SELECT contract, COUNT(*) as cnt FROM futures_klines "
            "WHERE symbol=? AND timeframe='1d' GROUP BY contract ORDER BY cnt DESC LIMIT 1",
            (sym,),
        ).fetchone()
        if not contract_row:
            print(f"  {sym}: ❌ 无日 K 线数据")
            all_pass = False
            continue

        contract = contract_row["contract"]
        klines = conn.execute(
            "SELECT timestamp, open, high, low, close, volume FROM futures_klines "
            "WHERE symbol=? AND contract=? AND timeframe='1d' "
            "ORDER BY timestamp DESC LIMIT 5",
            (sym, contract),
        ).fetchall()

        print(f"  === {sym} (合约={contract}, is_night={sym in night_symbols}) ===")

        for k in klines:
            dt = ts_to_sh(k["timestamp"])
            open_ = k["open"]
            high = k["high"]
            low = k["low"]
            close = k["close"]
            volume = k["volume"]

            # 检查价格逻辑
            price_ok = True
            issues = []
            if high < low:
                issues.append(f"high({high}) < low({low})")
                price_ok = False
            if open_ <= 0:
                issues.append(f"open({open_}) <= 0")
                price_ok = False
            if high <= 0:
                issues.append(f"high({high}) <= 0")
                price_ok = False
            if low <= 0:
                issues.append(f"low({low}) <= 0")
                price_ok = False
            if close <= 0:
                issues.append(f"close({close}) <= 0")
                price_ok = False

            price_status = "✓" if price_ok else f"✗ {'; '.join(issues)}"

            # 收盘时间戳检查
            close_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            hour = dt.hour
            minute = dt.minute

            if sym in night_symbols:
                # 有夜盘品种：收盘应在 15:00 或 23:00 或 01:00 或 02:30
                expected_times = {
                    "RB": ["15:00", "23:00"],  # SHFE 21-23
                    "MA": ["15:00", "23:00"],  # ZCE 21-23:00
                    "AG": ["15:00", "02:30"],  # SHFE 21-02:30
                    "SC": ["15:00", "02:30"],  # INE 21-02:30
                    "I": ["15:00", "23:00"],   # DCE 21-23
                }
                expected = expected_times.get(sym, ["15:00"])
                time_str = f"{hour:02d}:{minute:02d}"
                if time_str in expected:
                    night_status = "✓"
                elif hour == 15 and minute == 0:
                    night_status = "✓"
                else:
                    night_status = f"⚠ 收盘 {time_str} 不在预期 {expected} 中"
                    all_pass = False
            else:
                # 无夜盘品种：收盘应在 15:00
                if hour == 15 and minute == 0:
                    night_status = "✓"
                else:
                    night_status = f"⚠ 无夜盘品种收盘时间不是 15:00 (实际 {hour:02d}:{minute:02d})"
                    all_pass = False

            print(f"    {close_time} | O={open_:.1f} H={high:.1f} L={low:.1f} C={close:.1f} V={volume} | 价格: {price_status} | 收盘: {night_status}")

        print()

    # 总结
    print("=" * 70)
    if all_pass:
        print("✅ 所有检查通过！")
    else:
        print(f"❌ 存在异常，请复查")
    print("=" * 70)

    conn.close()
    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
