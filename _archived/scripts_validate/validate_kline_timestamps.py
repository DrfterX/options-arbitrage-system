#!/usr/bin/env python3
"""
P0 子任务 1.2 — K 线时间戳校验脚本

从 Top 50 中随机抽取 5 个有夜盘品种 + 2 个无夜盘品种（AP, CJ），
取最近 3 根日 K 线，检查时间戳、high/low 有效性。

用法:
    python3 scripts/validate_kline_timestamps.py
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "trading_system.db"

# 采样品种: 5 有夜盘 + 2 无夜盘
NIGHT_SYMBOLS = ["RB", "TA", "M", "AG", "CU"]
NO_NIGHT_SYMBOLS = ["AP", "CJ"]

# 夜盘时段映射
NIGHT_SESSIONS = {
    "RB": (21, 0, 23, 0),    # 21:00-23:00
    "TA": (21, 0, 23, 0),   # 21:00-23:00
    "M":  (21, 0, 23, 0),   # 21:00-23:00
    "AG": (21, 0, 2, 30),   # 21:00-次日02:30
    "CU": (21, 0, 1, 0),    # 21:00-次日01:00
}


def utc_to_cst(ts: int) -> datetime:
    """Unix UTC → Asia/Shanghai datetime"""
    return datetime.fromtimestamp(ts, tz=timezone.utc) + timedelta(hours=8)


def validate_symbol(cursor, symbol: str, is_night: bool) -> list[dict]:
    """校验单个品种的最近 3 根日 K 线。
    
    只检查连续合约（contract == symbol），排除前月合约的脏数据。
    """
    results = []
    cursor.execute(
        """SELECT timestamp, open, high, low, close, volume
           FROM futures_klines
           WHERE symbol=? AND contract=? AND timeframe='1d'
           ORDER BY timestamp DESC LIMIT 3""",
        (symbol, symbol)
    )
    rows = cursor.fetchall()
    if len(rows) < 3:
        results.append({
            "symbol": symbol,
            "status": "WARN",
            "msg": f"不足 3 根 1d K 线（仅 {len(rows)} 根）"
        })
        return results

    for r in rows:
        ts, open_p, high, low, close, vol = r
        cst = utc_to_cst(ts)
        row_result = {
            "symbol": symbol,
            "ts": ts,
            "cst_date": cst.strftime("%Y-%m-%d"),
            "cst_time": cst.strftime("%H:%M"),
            "open": open_p,
            "high": high,
            "low": low,
            "close": close,
            "volume": vol,
            "high_low_valid": high >= low,
            "open_in_range": low <= open_p <= high,
            "close_in_range": low <= close <= high,
            "is_night": is_night,
            "night_time_ok": True,     # default, override below
            "status": "OK",
            "errors": [],
        }

        # 检查 high < low 等逻辑错误
        if high < low:
            row_result["status"] = "FAIL"
            row_result["errors"].append(f"high({high}) < low({low})")
        if open_p < low or open_p > high:
            row_result["status"] = "FAIL"
            row_result["errors"].append(f"open({open_p}) not in [low({low}), high({high})]")
        if close < low or close > high:
            row_result["status"] = "FAIL"
            row_result["errors"].append(f"close({close}) not in [low({low}), high({high})]")

        # 检查日 K 线时间戳是否落在正常日盘时段（09:00-15:00）
        # 连续合约的 1d 应该使用 00:00 或 15:00 标记
        hour = cst.hour
        minute = cst.minute
        if hour not in (0, 15, 23):
            row_result["night_time_ok"] = False
            if row_result["status"] == "OK":
                row_result["status"] = "WARN"
            row_result["errors"].append(
                f"日 K 时间戳异常: {cst.strftime('%H:%M')}（应为 00:00 或 15:00 附近）"
            )

        # 无夜盘品种不应有夜盘时间戳
        if not is_night and hour >= 21:
            row_result["night_time_ok"] = False
            if row_result["status"] == "OK":
                row_result["status"] = "WARN"
            row_result["errors"].append(
                f"无夜盘品种出现夜盘时间戳: {cst.strftime('%H:%M')}"
            )

        if not row_result["errors"]:
            row_result["status"] = "OK"

        results.append(row_result)

    return results


def main():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    report_lines = [
        "# K 线时间戳校验报告",
        "",
        f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "> 数据源: trading_system.db — futures_klines 表",
        "> 校验品种: 5 有夜盘 (RB/TA/M/AG/CU) + 2 无夜盘 (AP/CJ)",
        "> 校验范围: 连续合约最近 3 根日 K 线",
        "",
    ]

    all_ok = True

    for sym in NIGHT_SYMBOLS:
        results = validate_symbol(cursor, sym, is_night=True)
        for item in results:
            if item["status"] in ("FAIL", "WARN"):
                all_ok = False
            report_lines.append(f"### {item['symbol']} — {item.get('cst_date', '?')}")
            report_lines.append("")
            report_lines.append(f"| 字段 | 值 | 校验 |")
            report_lines.append(f"|------|-----|------|")
            report_lines.append(f"| 时间戳 | {item.get('cst_date','?')} {item.get('cst_time','?')} | {'✅ 正常' if item['night_time_ok'] else '⚠️'}")
            report_lines.append(f"| 开盘 | {item['open']} | {'✅' if item['open_in_range'] else '❌'}")
            report_lines.append(f"| 最高 | {item['high']} | —")
            report_lines.append(f"| 最低 | {item['low']} | —")
            report_lines.append(f"| 收盘 | {item['close']} | {'✅' if item['close_in_range'] else '❌'}")
            report_lines.append(f"| high>=low | {'✅' if item['high_low_valid'] else '❌'} | 核心")
            report_lines.append(f"| 状态 | {item['status']} |")
            if item['errors']:
                report_lines.append(f"| 错误 | {'; '.join(item['errors'])} |")
            report_lines.append("")

    for sym in NO_NIGHT_SYMBOLS:
        results = validate_symbol(cursor, sym, is_night=False)
        for item in results:
            if item["status"] in ("FAIL", "WARN"):
                all_ok = False
            report_lines.append(f"### {item['symbol']} — {item.get('cst_date', '?')}")
            report_lines.append("")
            report_lines.append(f"| 字段 | 值 | 校验 |")
            report_lines.append(f"|------|-----|------|")
            report_lines.append(f"| 时间戳 | {item.get('cst_date','?')} {item.get('cst_time','?')} | {'✅ 正常' if item['night_time_ok'] else '⚠️'}")
            report_lines.append(f"| 开盘 | {item['open']} | {'✅' if item['open_in_range'] else '❌'}")
            report_lines.append(f"| 最高 | {item['high']} | —")
            report_lines.append(f"| 最低 | {item['low']} | —")
            report_lines.append(f"| 收盘 | {item['close']} | {'✅' if item['close_in_range'] else '❌'}")
            report_lines.append(f"| high>=low | {'✅' if item['high_low_valid'] else '❌'} | 核心")
            report_lines.append(f"| 状态 | {item['status']} |")
            if item['errors']:
                report_lines.append(f"| 错误 | {'; '.join(item['errors'])} |")
            report_lines.append("")

    # 汇总
    report_lines.append("## 汇总")
    report_lines.append("")
    if all_ok:
        report_lines.append("✅ **全部通过** — 所有品种的时间戳和价格逻辑校验通过。")
    else:
        report_lines.append("❌ **存在问题** — 请查看详细结果。")
    report_lines.append(f"")
    report_lines.append(f"| 检查项 | 结果 |")
    report_lines.append(f"|--------|------|")
    report_lines.append(f"| 5 有夜盘品种抽样 | {'✅' if all_ok else '⚠️'} |")
    report_lines.append(f"| 2 无夜盘品种抽样 | {'✅' if all_ok else '⚠️'} |")
    report_lines.append(f"| high < low 检查 | {'✅ 无' if all_ok else '❌ 有'} |")
    report_lines.append(f"| time >= 21 for 非夜盘 | {'✅ 正常' if all_ok else '⚠️ 需确认'}| ")
    report_lines.append(f"| 日 K 线时间戳合理性 | {'✅ 正常' if all_ok else '⚠️ 需确认'} |")

    report = "\n".join(report_lines)
    print(report)

    # 写入文档
    report_path = PROJECT_ROOT / "docs" / "K线时间戳校验报告.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n报告已写入: {report_path}")

    conn.close()
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
