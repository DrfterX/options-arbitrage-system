"""
15m K线数据回填脚本 — 获取多个历史合约的15m数据，拼接回填至数据库。

核心发现：
  AKShare Sina 分钟 API (futures_zh_minute_sina) 对每个合约代码都保留 ~1023 根 K 线。
  通过遍历历史主力合约，可以获取连续多年的 15m 数据。

策略：
  1. 对每个品种，确定主力合约的切换序列（按市场惯例：01→05→09→01 或 01→05→09→10→01 等）
  2. 依次获取每个合约的 15m 数据
  3. 按时间戳插入数据库（INSERT OR IGNORE 去重）
  4. 拼接后形成覆盖多年的 15m 时间序列

局限：
  - 合约间存在约 4-6 周的空窗期（合约退市 → 新合约成为主力之间）
  - 不同合约的价格不连续（升贴水差异），但 15m 仅用于入场时机判定（突破 B 点），
    N 型结构检测基于 1d（连续价格），因此价格不连续对策略影响有限
"""

import logging
import sqlite3
import time as time_module
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import akshare as ak

logger = logging.getLogger(__name__)

# ============================================================
# 合约月份序列（按交易所惯例）
# ============================================================

# 各品种的主力合约月份序列
# 大多数品种：01→05→09→01（隔季轮换）
# 部分品种：01→05→09→10→01 或 01→05→09→11→01
CONTRACT_MONTHS: Dict[str, List[int]] = {
    "RB": [1, 5, 10],     # 螺纹钢：01→05→10
    "Y":  [1, 5, 9],      # 豆油：01→05→09
    "P":  [1, 5, 9],      # 棕榈油：01→05→09
    "EB": [1, 5, 9],      # 苯乙烯：01→05→09
    "L":  [1, 5, 9],      # 聚乙烯：01→05→09
    "PG": [1, 5, 9],      # 液化气：01→05→09
    "TA": [1, 5, 9],      # PTA：01→05→09
}

# 起始年份（回填起点）
START_YEAR = 2020
END_YEAR = 2026


def generate_contracts(symbol: str, start_year: int = START_YEAR, end_year: int = END_YEAR) -> List[str]:
    """生成历史上可能的主力合约代码列表。

    Args:
        symbol: 品种代码（如 'RB'）。
        start_year: 起始年份。
        end_year: 结束年份。

    Returns:
        合约代码列表，按时间升序排列（如 ['RB2101', 'RB2105', ...]）。
    """
    months = CONTRACT_MONTHS.get(symbol, [1, 5, 9])
    contracts: List[str] = []
    for year in range(start_year, end_year + 1):
        yy = str(year)[-2:]
        for mm in months:
            contracts.append(f"{symbol}{yy}{mm:02d}")
    return contracts


def fetch_15m(symbol: str, contract: str) -> List[dict]:
    """获取单个合约的 15m K 线数据。

    Args:
        symbol: 品种代码（如 'RB'）。
        contract: 合约代码（如 'RB2501'）。

    Returns:
        K 线数据列表，每项包含 symbol / contract / timeframe / timestamp /
        open / high / low / close / volume。
    """
    try:
        df = ak.futures_zh_minute_sina(symbol=contract, period="15")
        if df is None or df.empty:
            logger.debug("  %s: 无数据", contract)
            return []
    except Exception as e:
        logger.debug("  %s: 获取失败 - %s", contract, e)
        return []

    results: List[dict] = []
    for _, row in df.iterrows():
        dt_str = str(row.get("datetime", ""))
        if not dt_str:
            continue
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            ts = int(dt.timestamp())
        except ValueError:
            continue

        results.append({
            "symbol": symbol,
            "contract": contract,
            "timeframe": "15m",
            "timestamp": ts,
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": int(float(row.get("volume", 0))),
        })

    results.sort(key=lambda r: r["timestamp"])
    logger.info("  %s: %d 条 15m K 线 [%s ~ %s]",
                contract, len(results),
                datetime.fromtimestamp(results[0]["timestamp"], tz=timezone.utc).strftime("%Y-%m-%d"),
                datetime.fromtimestamp(results[-1]["timestamp"], tz=timezone.utc).strftime("%Y-%m-%d"))
    return results


def insert_into_db(db_path: str, rows: List[dict]) -> int:
    """批量插入 K 线数据到数据库。

    Args:
        db_path: 数据库路径。
        rows: K 线数据列表。

    Returns:
        实际插入的行数。
    """
    if not rows:
        return 0

    sql = """
        INSERT OR IGNORE INTO futures_klines
        (symbol, contract, timeframe, timestamp, open, high, low, close, volume)
        VALUES (:symbol, :contract, :timeframe, :timestamp, :open, :high, :low, :close, :volume)
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.executemany(sql, rows)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def backfill_symbol(db_path: str, symbol: str) -> dict:
    """回填单个品种的 15m 历史数据。

    Args:
        db_path: 数据库路径。
        symbol: 品种代码。

    Returns:
        回填统计: {total_fetched, total_inserted, contracts_count, date_range}.
    """
    contracts = generate_contracts(symbol)
    logger.info("===== %s: 即将回填 %d 个合约 =====", symbol, len(contracts))

    total_fetched = 0
    total_inserted = 0
    contract_count = 0
    min_ts: Optional[int] = None
    max_ts: Optional[int] = None

    for contract in contracts:
        rows = fetch_15m(symbol, contract)
        if not rows:
            continue

        contract_count += 1
        total_fetched += len(rows)

        inserted = insert_into_db(db_path, rows)
        total_inserted += inserted

        if rows:
            c_min = rows[0]["timestamp"]
            c_max = rows[-1]["timestamp"]
            min_ts = c_min if min_ts is None else min(min_ts, c_min)
            max_ts = c_max if max_ts is None else max(max_ts, c_max)

        time_module.sleep(0.3)  # 限流间隔

    date_range_str = ""
    if min_ts and max_ts:
        date_range_str = (f"{datetime.fromtimestamp(min_ts, tz=timezone.utc).strftime('%Y-%m-%d')}"
                          f" ~ "
                          f"{datetime.fromtimestamp(max_ts, tz=timezone.utc).strftime('%Y-%m-%d')}")

    stats = {
        "symbol": symbol,
        "contracts_found": contract_count,
        "total_fetched": total_fetched,
        "total_inserted": total_inserted,
        "date_range": date_range_str,
    }

    logger.info("===== %s 完成: %d 合约, 获取 %d, 新增 %d [%s] =====",
                symbol, contract_count, total_fetched, total_inserted, date_range_str)
    return stats


def backfill_all(db_path: str, symbols: Optional[List[str]] = None) -> List[dict]:
    """回填所有品种的 15m 历史数据。

    Args:
        db_path: 数据库路径。
        symbols: 品种列表，默认全部目标品种。

    Returns:
        各品种回填统计列表。
    """
    if symbols is None:
        symbols = list(CONTRACT_MONTHS.keys())

    all_stats: List[dict] = []
    start = time_module.time()

    for sym in symbols:
        stats = backfill_symbol(db_path, sym)
        all_stats.append(stats)

    elapsed = time_module.time() - start
    total_fetched = sum(s["total_fetched"] for s in all_stats)
    total_inserted = sum(s["total_inserted"] for s in all_stats)

    logger.info("\n" + "=" * 60)
    logger.info("  全部完成: %d 品种, 获取 %d, 新增 %d, 耗时 %.0fs",
                len(all_stats), total_fetched, total_inserted, elapsed)
    logger.info("=" * 60)

    return all_stats


def print_results(stats_list: List[dict]) -> None:
    """打印回填结果报告。"""
    print("\n" + "=" * 60)
    print("  15m 数据回填报告")
    print("=" * 60)
    print(f"{'Sym':>4} {'合约数':>6} {'获取':>8} {'新增':>8}  日期范围")
    print("-" * 60)
    for s in stats_list:
        print(f"{s['symbol']:>4} {s['contracts_found']:>6} "
              f"{s['total_fetched']:>8} {s['total_inserted']:>8}  {s['date_range']}")
    print("=" * 60)


def verify_coverage(db_path: str) -> None:
    """验证回填后的 15m 数据覆盖情况。"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT symbol,
               COUNT(*) as cnt,
               MIN(timestamp) as min_ts,
               MAX(timestamp) as max_ts,
               ROUND((MAX(timestamp) - MIN(timestamp)) / 86400.0, 0) as days,
               COUNT(DISTINCT contract) as contracts
        FROM futures_klines
        WHERE timeframe = '15m'
        GROUP BY symbol
        ORDER BY symbol
    """).fetchall()
    conn.close()

    print("\n" + "=" * 60)
    print("  15m 数据覆盖验证")
    print("=" * 60)
    print(f"{'Sym':>4} {'Bar数':>8} {'天数':>6} {'合约':>6}  日期范围")
    print("-" * 60)
    for r in rows:
        min_dt = datetime.fromtimestamp(r["min_ts"], tz=timezone.utc).strftime("%Y-%m-%d")
        max_dt = datetime.fromtimestamp(r["max_ts"], tz=timezone.utc).strftime("%Y-%m-%d")
        print(f"{r['symbol']:>4} {r['cnt']:>8} {r['days']:>6} {r['contracts']:>6}  {min_dt} ~ {max_dt}")
    print("=" * 60)


def main():
    """CLI 入口。"""
    import argparse
    parser = argparse.ArgumentParser(description="15m K线历史数据回填工具")
    parser.add_argument("--symbol", "-s", help="单品种回填（默认全部）")
    parser.add_argument("--verify", "-v", action="store_true", help="仅验证数据覆盖")
    parser.add_argument("--db", default=str(Path(__file__).resolve().parent.parent / "trading_system.db"),
                        help="数据库路径")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        datefmt="%H:%M:%S")

    db_path = args.db

    if args.verify:
        verify_coverage(db_path)
        return

    if args.symbol:
        stats = backfill_symbol(db_path, args.symbol.upper())
        print_results([stats])
        verify_coverage(db_path)
    else:
        stats_list = backfill_all(db_path)
        print_results(stats_list)
        verify_coverage(db_path)


if __name__ == "__main__":
    main()
