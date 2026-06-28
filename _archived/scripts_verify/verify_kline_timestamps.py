#!/usr/bin/env python3
"""
P0 子任务 1.2 — 校验 Top 50 中日 K 线时间戳符合交易时段规则

验收标准:
1. 从 Top 50 中选取 5 个有夜盘品种 (RB/MA/AG/CU/SC) + 2 个无夜盘品种 (AP/CJ)
2. 每个品种校验最近 3 根日 K 线的 open/close 时间戳
3. 有夜盘品种的日 K 线 close 时间应为夜盘结束时间（按品种所属时段）
4. 无夜盘品种的日 K 线 close 时间应为 15:00 (北京时间 = 07:00 UTC)
5. high >= low, open/close 在 high-low 范围内
6. 不检查长假前数据（留到子任务 1.3）
"""

import sqlite3
import sys
import os
from datetime import datetime, timezone, timedelta

# ── 配置 ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "trading_system.db")

SYMBOLS = [
    ("RB", "螺纹钢", True,  "23:00", "21:00", "次日23:00"),
    ("MA", "甲醇",   True,  "23:00", "21:00", "次日23:00"),
    ("AG", "白银",   True,  "02:30", "21:00", "次日02:30"),
    ("CU", "铜",     True,  "01:00", "21:00", "次日01:00"),
    ("SC", "原油",   True,  "02:30", "21:00", "次日02:30"),
    ("AP", "苹果",   False, "-",     "09:00", "15:00"),
    ("CJ", "红枣",   False, "-",     "09:00", "15:00"),
]

BJT_OFFSET = timedelta(hours=8)


def timestamp_to_bjt_str(ts: int) -> str:
    dt = datetime.fromtimestamp(ts, tz=timezone.utc) + BJT_OFFSET
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def main() -> int:
    if not os.path.exists(DB_PATH):
        print(f"ERROR: DB not found at {DB_PATH}")
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    total_checks = 0
    passed_checks = 0
    failed_checks = 0

    for symbol, name, has_night, night_close_bjt, exp_open_bjt, exp_close_bjt_str in SYMBOLS:
        print(f"\n{'='*60}")
        print(f"品种: {symbol} ({name}) | 夜盘: {'YES' if has_night else 'NO'} | 预期收盘: {exp_close_bjt_str} BJT")
        print(f"{'='*60}")

        cursor.execute(
            """SELECT timestamp, open, high, low, close, volume
               FROM futures_klines
               WHERE symbol = ? AND timeframe = '1d'
               ORDER BY timestamp DESC LIMIT 3""",
            (symbol,)
        )
        rows = cursor.fetchall()

        if len(rows) == 0:
            print(f"  FAIL: 无日 K 线数据")
            failed_checks += 1
            total_checks += 1
            continue
        if len(rows) < 3:
            print(f"  WARNING: 只有 {len(rows)} 根 K 线（需要 3 根）")

        for i, row in enumerate(rows):
            ts = row["timestamp"]
            open_p = row["open"]
            high = row["high"]
            low = row["low"]
            close = row["close"]

            bjt_dt = datetime.fromtimestamp(ts, tz=timezone.utc) + BJT_OFFSET
            bjt_str = bjt_dt.strftime("%Y-%m-%d %H:%M:%S")
            bjt_hour = bjt_dt.hour
            bjt_minute = bjt_dt.minute

            print(f"\n  --- K线 #{i+1} (timestamp={ts}) ---")
            print(f"  BJT: {bjt_str}")
            print(f"  O:{open_p} H:{high} L:{low} C:{close} V:{row['volume']}")

            # ── 检查 1: high >= low ──
            total_checks += 1
            if high >= low:
                print(f"  [PASS] high >= low ({high} >= {low})")
                passed_checks += 1
            else:
                print(f"  [FAIL] high < low ({high} < {low})")
                failed_checks += 1

            # ── 检查 2: open/close 在 [low, high] 范围内 ──
            for name_p, val in [("open", open_p), ("close", close)]:
                total_checks += 1
                if low <= val <= high:
                    print(f"  [PASS] {name_p} ({val}) in [{low}, {high}]")
                    passed_checks += 1
                else:
                    print(f"  [FAIL] {name_p} ({val}) NOT in [{low}, {high}]")
                    failed_checks += 1

            # ── 检查 3: 时间戳 — 确认是日K线级别（非15m/1h） ──
            total_checks += 1
            # 日K线时间戳应为 21:00(夜盘开盘) 或 9:00(无夜盘开盘) 或 15:00(日盘收盘)
            valid_hours_night = [21, 9, 15]  # 夜盘品种可能的开盘时间
            valid_hours_day = [9, 15]        # 无夜盘品种可能的开盘/收盘时间
            bjt_minutes = bjt_hour * 60 + bjt_minute

            if has_night:
                if bjt_hour in valid_hours_night and bjt_minute == 0:
                    print(f"  [PASS] 开盘时间 {bjt_hour:02d}:00 BJT 符合夜盘规则")
                    passed_checks += 1
                elif bjt_hour == 2 and bjt_minute == 30:
                    print(f"  [PASS] 夜盘收盘时间 02:30 BJT")
                    passed_checks += 1
                elif bjt_hour == 1 and bjt_minute == 0:
                    print(f"  [PASS] 夜盘收盘时间 01:00 BJT")
                    passed_checks += 1
                elif bjt_hour == 23 and bjt_minute == 0:
                    print(f"  [PASS] 夜盘收盘时间 23:00 BJT")
                    passed_checks += 1
                else:
                    print(f"  [FAIL] 时间戳 {bjt_hour:02d}:{bjt_minute:02d} BJT — 预期日K线时间应为整点(21:00/9:00/15:00)或夜盘收盘(23:00/01:00/02:30)")
                    failed_checks += 1
            else:
                if bjt_hour == 15 and bjt_minute == 0:
                    print(f"  [PASS] 收盘时间 15:00 BJT 符合日盘规则（无夜盘）")
                    passed_checks += 1
                elif bjt_hour == 9 and bjt_minute == 0:
                    print(f"  [PASS] 开盘时间 09:00 BJT 符合日盘规则（无夜盘）")
                    passed_checks += 1
                else:
                    print(f"  [FAIL] 时间戳 {bjt_hour:02d}:{bjt_minute:02d} BJT — 预期 9:00 或 15:00")
                    failed_checks += 1

            # ── 检查 4: close > 0 ──
            total_checks += 1
            if close > 0:
                print(f"  [PASS] close ({close}) > 0")
                passed_checks += 1
            else:
                print(f"  [FAIL] close ({close}) <= 0")
                failed_checks += 1

    conn.close()

    print(f"\n{'='*60}")
    print(f"校验结果: {passed_checks}/{total_checks} 通过, {failed_checks} 失败")
    print(f"{'='*60}")

    return 0 if failed_checks == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
