#!/usr/bin/env python3
"""
夜盘时段 K 线覆盖验证脚本 — P0 子任务 1.6

验证每个有夜盘品种的 15m K 线数据是否覆盖正确的夜盘时间窗口。

交易所夜盘规则:
  SHFE 普通品种 (rb/hc/ss/bu/ru/sp/fu): 21:00-23:00
  SHFE 金属 (cu/al/zn/pb/ni/sn): 21:00-次日01:00
  SHFE 贵金属 (au/ag): 21:00-次日02:30
  INE 原油 (sc): 21:00-次日02:30
  INE 其他 (nr): 21:00-23:00
  DCE 活跃 (i/m/y/p/l/pp/v/eg/eb/pg): 21:00-23:00
  CZCE 活跃 (CF/SR/RM/OI/MA/TA/PX): 21:00-23:00
"""

import sqlite3
import sys
from datetime import datetime

# 品种 -> (start_hour, end_hour) 北京时间闭区间，仅含 contracts.py 标记 is_night=1 的品种
NIGHT_SESSION_MAP = {
    # SHFE 普通 21-23
    "RB": (21, 23), "HC": (21, 23), "BU": (21, 23), "RU": (21, 23),
    # SHFE 金属 21-01
    "CU": (21, 1), "AL": (21, 1), "ZN": (21, 1),
    "PB": (21, 1), "NI": (21, 1), "SN": (21, 1),
    # SHFE 贵金属 21-02:30
    "AU": (21, 2), "AG": (21, 2),
    # INE 21-02:30
    "SC": (21, 2),
    # INE 其他 21-23
    "NR": (21, 23),
    # DCE 21-23
    "I": (21, 23), "M": (21, 23), "Y": (21, 23), "P": (21, 23),
    "L": (21, 23), "PP": (21, 23), "V": (21, 23),
    "EG": (21, 23), "EB": (21, 23), "PG": (21, 23),
    # CZCE 21-23
    "CF": (21, 23), "SR": (21, 23), "RM": (21, 23),
    "OI": (21, 23), "MA": (21, 23), "TA": (21, 23),
    "PX": (21, 23),
}


def is_night_hour(hour: int, start_h: int, end_h: int) -> bool:
    if start_h <= end_h:
        return start_h <= hour <= end_h
    else:
        return hour >= start_h or hour <= end_h


def main():
    db_path = "projects/options_arbitrage_system/trading_system.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    errors = []
    total = 0
    passed = 0

    for symbol, (start_h, end_h) in sorted(NIGHT_SESSION_MAP.items()):
        rows = conn.execute('''
            SELECT timestamp, datetime(timestamp, 'unixepoch', 'localtime') as bt
            FROM futures_klines
            WHERE symbol = ? AND timeframe = '15m'
            ORDER BY timestamp DESC
            LIMIT 100
        ''', (symbol,)).fetchall()

        if not rows:
            errors.append(f"{symbol}: No 15m data")
            continue

        night_rows = []
        for r in rows:
            bt_str = r["bt"]
            try:
                dt = datetime.strptime(bt_str, "%Y-%m-%d %H:%M:%S")
                if is_night_hour(dt.hour, start_h, end_h):
                    night_rows.append(bt_str)
            except ValueError:
                continue

        if not night_rows:
            errors.append(f"{symbol}: No night klines (expected {start_h}:00-{end_h}:00)")
            continue

        night_hours = set()
        for bt_str in night_rows:
            h = datetime.strptime(bt_str, "%Y-%m-%d %H:%M:%S").hour
            night_hours.add(h)

        if start_h <= end_h:
            expected = set(range(start_h, end_h + 1))
        else:
            expected = set(range(start_h, 24)) | set(range(0, end_h + 1))

        missing = sorted(expected - night_hours)
        if missing:
            errors.append(
                f"{symbol}: Missing hours {missing} "
                f"(expected {start_h}:00-{end_h}:00, have {sorted(night_hours)})"
            )
        else:
            passed += 1
            h_str = ",".join(f"{h:02d}:00" for h in sorted(night_hours))
            print(f"  ✅ {symbol}: [{h_str}] ({len(night_rows)} night klines)")

        total += 1

    conn.close()

    print(f"\n{'='*50}")
    print(f"夜盘覆盖验证结果: {passed}/{total} 通过")
    if errors:
        print(f"\n❌ 失败详情:")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("✅ 所有有夜盘品种的 15m K 线数据均覆盖正确的时间段")
        print(f"""
  关键验证点:
  - SHFE 21:00-23:00 (RB/HC/BU/RU): ✅ 覆盖 21,22,23 时
  - SHFE 21:00-01:00 (CU/AL/ZN/PB/NI/SN): ✅ 覆盖 21,22,23,00,01 时
  - SHFE 21:00-02:30 (AU/AG): ✅ 覆盖 21,22,23,00,01,02 时
  - INE 21:00-02:30 (SC): ✅ 覆盖 21,22,23,00,01,02 时
  - INE 21:00-23:00 (NR): ✅ 覆盖 21,22,23 时
  - DCE 21:00-23:00 (I/M/Y/P/L/PP/V/EG/EB/PG): ✅ 覆盖 21,22,23 时
  - CZCE 21:00-23:00 (CF/SR/RM/OI/MA/TA/PX): ✅ 覆盖 21,22,23 时
""")
        return 0


if __name__ == "__main__":
    sys.exit(main())
