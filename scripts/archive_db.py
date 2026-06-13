#!/usr/bin/env python3
"""
数据库归档脚本 — 按保留策略清理过期数据并回收空间。

用法:
    uv run python scripts/archive_db.py              # 执行归档（默认 dry_run=False）
    uv run python scripts/archive_db.py --dry-run     # 预览模式（只统计，不删除）
    uv run python scripts/archive_db.py --vacuum-only # 仅执行 VACUUM（不清理数据）

执行计划（launchd / cron）:
    每月 1 日凌晨 3:00:
    0 3 1 * * cd /path/to/system && uv run python scripts/archive_db.py >> archive.log 2>&1
"""

import argparse
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_PATH, ARCHIVE_RETENTION, LOG_LEVEL
from core.db import Database

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("archive_db")


def human_size(path: str) -> str:
    """返回文件的人类可读大小。"""
    size = os.path.getsize(path)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def count_rows(conn: sqlite3.Connection, table: str,
               where: str = "", params: tuple = ()) -> int:
    """统计表中符合条件的行数。"""
    sql = f"SELECT COUNT(*) FROM {table}"
    if where:
        sql += f" WHERE {where}"
    row = conn.execute(sql, params).fetchone()
    return row[0] if row else 0


def delete_rows(conn: sqlite3.Connection, table: str,
                where: str, params: tuple) -> int:
    """删除表中符合条件的行，返回删除行数。"""
    cursor = conn.execute(f"DELETE FROM {table} WHERE {where}", params)
    return cursor.rowcount


def archive_klines(conn: sqlite3.Connection, dry_run: bool) -> dict:
    """归档 futures_klines：按 timeframe 保留策略删除过期分钟级 K 线。"""
    results = {}
    retention = ARCHIVE_RETENTION.get("klines_by_timeframe", {})
    now_ts = int(time.time())

    for timeframe, days in retention.items():
        if days < 0:
            results[timeframe] = {"action": "kept", "rows": 0}
            continue

        cutoff = now_ts - days * 86400
        where = "timeframe = ? AND timestamp < ?"
        params = (timeframe, cutoff)

        if dry_run:
            count = count_rows(conn, "futures_klines", where, params)
            results[timeframe] = {"action": "would_delete", "rows": count}
        else:
            deleted = delete_rows(conn, "futures_klines", where, params)
            results[timeframe] = {"action": "deleted", "rows": deleted}

    return results


def archive_derived(conn: sqlite3.Connection, dry_run: bool,
                    table: str, ts_column: str,
                    days: int, ts_type: str = "unix") -> dict:
    """归档衍生数据表。

    Args:
        table: 表名
        ts_column: 时间戳列名
        days: 保留天数（-1 永久）
        ts_type: "unix" (INTEGER) | "iso" (TEXT datetime) | "date" (TEXT YYYY-MM-DD)
    """
    if days < 0:
        return {"action": "kept", "rows": 0}

    now = datetime.now(timezone.utc)

    if ts_type == "unix":
        cutoff_ts = int(now.timestamp()) - days * 86400
        where = f"{ts_column} < ?"
        params = (cutoff_ts,)
    elif ts_type == "date":
        cutoff_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
        where = f"{ts_column} < ?"
        params = (cutoff_date,)
    else:
        cutoff_iso = (now - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        where = f"{ts_column} < ?"
        params = (cutoff_iso,)

    if dry_run:
        count = count_rows(conn, table, where, params)
        return {"action": "would_delete", "rows": count}
    else:
        deleted = delete_rows(conn, table, where, params)
        return {"action": "deleted", "rows": deleted}


def vacuum_db(db_path: str) -> dict:
    """执行 VACUUM 回收磁盘空间。使用独立连接执行。"""
    before = human_size(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("VACUUM")
    conn.close()
    after = human_size(db_path)
    return {"before": before, "after": after, "vacuumed": True}


def print_summary(results: dict, elapsed: float):
    """打印归档摘要。"""
    total_deleted = 0
    log.info("═" * 55)
    log.info("  DB 归档结果摘要")
    log.info("═" * 55)

    if "klines" in results:
        k = results["klines"]
        log.info("  📊 futures_klines:")
        for tf, r in k.items():
            action_icon = "🗑️" if r["rows"] > 0 else "✅"
            log.info(f"    {action_icon} {tf}: {r['rows']:,} rows {r['action']}")
            total_deleted += r["rows"]

    for table_key in ["macd", "swing_points", "iv_history",
                       "signal_push_log", "filter_decision_log"]:
        if table_key in results:
            r = results[table_key]
            action_icon = "🗑️" if r["rows"] > 0 else "✅"
            log.info(f"  {action_icon} {table_key}: {r['rows']:,} rows {r['action']}")
            total_deleted += r["rows"]

    if "vacuum" in results:
        v = results["vacuum"]
        log.info(f"  🧹 VACUUM: {v['before']} → {v['after']}")

    log.info("─" * 55)
    log.info(f"  总计清理: {total_deleted:,} 行")
    log.info(f"  耗时: {elapsed:.2f}s")
    log.info("═" * 55)


def main():
    parser = argparse.ArgumentParser(description="交易系统数据库归档")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际删除")
    parser.add_argument("--vacuum-only", action="store_true", help="仅执行 VACUUM")
    args = parser.parse_args()

    start = time.time()

    if not DB_PATH.exists():
        log.error(f"数据库不存在: {DB_PATH}")
        sys.exit(1)

    db = Database(str(DB_PATH))
    conn = db.get_conn()

    log.info(f"数据库: {DB_PATH} ({human_size(str(DB_PATH))})")
    if args.dry_run:
        log.info("🔍 DRY-RUN 模式 — 仅统计，不删除")
    if args.vacuum_only:
        log.info("🧹 VACUUM-ONLY 模式 — 仅回收空间")

    results = {}

    if not args.vacuum_only:
        # 1. K 线归档
        results["klines"] = archive_klines(conn, args.dry_run)

        # 2. MACD 指标（INTEGER unix timestamp）
        macd_days = ARCHIVE_RETENTION.get("macd", 90)
        results["macd"] = archive_derived(conn, args.dry_run,
                                          "futures_macd", "timestamp",
                                          macd_days, "unix")

        # 3. 波峰波谷（INTEGER unix timestamp）
        swing_days = ARCHIVE_RETENTION.get("swing_points", 90)
        results["swing_points"] = archive_derived(conn, args.dry_run,
                                                  "futures_swing_points",
                                                  "timestamp", swing_days, "unix")

        # 4. IV 历史（TEXT date YYYY-MM-DD）
        iv_days = ARCHIVE_RETENTION.get("iv_history", 180)
        results["iv_history"] = archive_derived(conn, args.dry_run,
                                                "iv_history", "date",
                                                iv_days, "date")

        # 5. 推送日志（TEXT datetime ISO）
        push_days = ARCHIVE_RETENTION.get("signal_push_log", 30)
        results["signal_push_log"] = archive_derived(conn, args.dry_run,
                                                     "signal_push_log",
                                                     "pushed_at",
                                                     push_days, "iso")

        # 6. 过滤决策日志（TEXT datetime ISO）
        filter_days = ARCHIVE_RETENTION.get("filter_decision_log", 30)
        results["filter_decision_log"] = archive_derived(conn, args.dry_run,
                                                         "filter_decision_log",
                                                         "created_at",
                                                         filter_days, "iso")

        log.info("当前数据行数:")
        for tbl in ["futures_klines", "futures_macd", "futures_swing_points",
                     "iv_history", "signal_push_log", "filter_decision_log",
                     "futures_n_structures", "futures_signals", "options_signals"]:
            cnt = count_rows(conn, tbl)
            log.info(f"  {tbl}: {cnt:,}")

    # 7. VACUUM（先 commit 再 vacuum）
    if not args.dry_run:
        conn.commit()
        results["vacuum"] = vacuum_db(str(DB_PATH))
    else:
        results["vacuum"] = {"before": human_size(str(DB_PATH)),
                             "after": "N/A", "vacuumed": False}

    elapsed = time.time() - start
    print_summary(results, elapsed)

    db.close()


if __name__ == "__main__":
    main()