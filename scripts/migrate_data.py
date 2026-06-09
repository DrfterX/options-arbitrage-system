#!/usr/bin/env python3
"""数据迁移: 从旧两项目的DB迁移到新统一 trading_system.db。

迁移来源：
  - 旧期货DB: ``~/options_arbitrage_system/futures_signal/futures_kline.db``
  - 旧IV DB:   ``~/projects/options_arbitrage_system/iv_history.db``
  - 旧信号JSON: ``~/projects/options_arbitrage_system/signals.json``

所有迁移使用 INSERT OR IGNORE，重复执行幂等。
"""

import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.db import Database
from config.settings import DB_PATH

logger = logging.getLogger(__name__)

# 旧DB路径
OLD_FUTURES_DB: Path = Path.home() / "options_arbitrage_system/futures_signal/futures_kline.db"
OLD_IV_DB: Path = Path.home() / "projects/options_arbitrage_system/iv_history.db"
OLD_SIGNALS_JSON: Path = Path.home() / "projects/options_arbitrage_system/signals.json"


def _old_conn(db_path: Path) -> sqlite3.Connection:
    """打开旧数据库连接（只读安全）。"""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _migrate_table(
    old_conn: sqlite3.Connection,
    new_conn: sqlite3.Connection,
    table: str,
) -> int:
    """迁移单张表：INSERT OR IGNORE 所有行。

    Args:
        old_conn: 旧数据库连接。
        new_conn: 新数据库连接。
        table: 表名。

    Returns:
        迁移行数。
    """
    try:
        rows = old_conn.execute(f"SELECT * FROM {table}").fetchall()
    except sqlite3.OperationalError as e:
        logger.debug("表 %s 不存在于旧DB，跳过: %s", table, e)
        return 0

    if not rows:
        return 0

    columns = list(rows[0].keys())
    placeholders = ",".join(["?" for _ in columns])
    col_names = ",".join(columns)

    count: int = 0
    for row in rows:
        values = [row[c] for c in columns]
        try:
            new_conn.execute(
                f"INSERT OR IGNORE INTO {table} ({col_names}) VALUES ({placeholders})",
                values,
            )
            count += 1
        except sqlite3.OperationalError as e:
            logger.debug("行插入失败 %s: %s", table, e)

    new_conn.commit()
    return count


def migrate_futures_kline(db: Database) -> None:
    """迁移期货K线数据（幂等：INSERT OR IGNORE）。

    迁移表：futures_klines, futures_macd, futures_swing_points,
    futures_n_structures, futures_signals。
    """
    if not OLD_FUTURES_DB.exists():
        logger.warning("旧期货DB不存在: %s", OLD_FUTURES_DB)
        return

    logger.info("迁移旧期货数据: %s", OLD_FUTURES_DB)
    old_conn = _old_conn(OLD_FUTURES_DB)
    new_conn = db.get_conn()

    tables: list[str] = [
        "futures_klines",
        "futures_macd",
        "futures_swing_points",
        "futures_n_structures",
        "futures_signals",
    ]

    try:
        for table in tables:
            count = _migrate_table(old_conn, new_conn, table)
            if count > 0:
                logger.info("  %s: 迁移 %d 条", table, count)
            else:
                logger.info("  %s: 跳过（无数据或表不存在）", table)
    finally:
        new_conn.close()
        old_conn.close()


def migrate_iv_history(db: Database) -> None:
    """迁移IV历史数据。

    从旧 iv_history.db 迁移到新统一DB的 iv_history 表。
    """
    if not OLD_IV_DB.exists():
        logger.warning("旧IV DB不存在: %s", OLD_IV_DB)
        return

    logger.info("迁移旧IV数据: %s", OLD_IV_DB)
    old_conn = _old_conn(OLD_IV_DB)
    new_conn = db.get_conn()

    try:
        try:
            rows = old_conn.execute("SELECT * FROM iv_history").fetchall()
        except sqlite3.OperationalError as e:
            logger.warning("iv_history 表不存在于旧DB: %s", e)
            return

        if not rows:
            logger.info("  iv_history: 无数据")
            return

        count: int = 0
        for row in rows:
            new_conn.execute(
                """INSERT OR IGNORE INTO iv_history
                   (symbol, contract, date, time, futures_price, atm_strike,
                    atm_call_iv, atm_put_iv, avg_iv, top5_call_iv, top5_put_iv, top5_avg_iv)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["symbol"],
                    row["contract"],
                    row["date"],
                    row["time"],
                    row["futures_price"],
                    row["atm_strike"],
                    row["atm_call_iv"],
                    row["atm_put_iv"],
                    row["avg_iv"] if "avg_iv" in row.keys() else 0,
                    row["top5_call_iv"] if "top5_call_iv" in row.keys() else 0,
                    row["top5_put_iv"] if "top5_put_iv" in row.keys() else 0,
                    row["top5_avg_iv"] if "top5_avg_iv" in row.keys() else 0,
                ),
            )
            count += 1
        new_conn.commit()
        logger.info("  iv_history: 迁移 %d 条", count)
    finally:
        new_conn.close()
        old_conn.close()


def migrate_options_signals(db: Database) -> None:
    """迁移期权策略信号JSON。

    从旧 signals.json 迁移到新DB的 options_signals 表。
    """
    if not OLD_SIGNALS_JSON.exists():
        logger.warning("旧信号JSON不存在: %s", OLD_SIGNALS_JSON)
        return

    logger.info("迁移旧期权信号: %s", OLD_SIGNALS_JSON)
    with open(OLD_SIGNALS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    signals = data.get("signals", [])
    if not signals:
        logger.info("  options_signals: 无信号数据")
        return

    new_conn = db.get_conn()
    count: int = 0
    try:
        for s in signals:
            sd = s.get("strategy_details", {})
            if isinstance(sd, str):
                try:
                    sd = json.loads(sd)
                except (json.JSONDecodeError, TypeError):
                    sd = {}

            new_conn.execute(
                """INSERT OR IGNORE INTO options_signals
                   (symbol, contract, strategy, signal_type, strength, reason,
                    futures_price, iv_avg, iv_percentile, iv_level,
                    net_delta, net_theta, net_vega, max_profit, max_loss,
                    unified_score, strategy_details, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    s.get("symbol", ""),
                    s.get("contract", ""),
                    s.get("strategy", ""),
                    s.get("signal_type", "WATCH"),
                    s.get("strength", 0),
                    s.get("reason", ""),
                    s.get("futures_price", 0),
                    s.get("implied_vol", s.get("iv_avg", 0)),
                    s.get("vol_percentile", s.get("iv_percentile", 0)),
                    s.get("iv_level", "正常"),
                    s.get("delta", s.get("net_delta", 0)),
                    s.get("theta", s.get("net_theta", 0)),
                    s.get("vega", s.get("net_vega", 0)),
                    s.get("max_profit", 0),
                    s.get("max_loss", 0),
                    s.get("unified_score", 0),
                    json.dumps(sd, ensure_ascii=False),
                    s.get("timestamp", ""),
                ),
            )
            count += 1
        new_conn.commit()
        logger.info("  options_signals: 迁移 %d 条", count)
    finally:
        new_conn.close()


def main() -> None:
    """执行完整数据迁移。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger.info("开始数据迁移...")
    db = Database(DB_PATH)
    migrate_futures_kline(db)
    migrate_iv_history(db)
    migrate_options_signals(db)
    logger.info("迁移完成")


if __name__ == "__main__":
    main()
