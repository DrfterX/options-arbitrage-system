"""
一次性脚本：为全品种生成 3m 数据链路
1. 收集 1m K线（→自动聚合生成 3m K线 via _collect_3m_from_1m）
2. MACD 计算（3m）
3. 极值点更新（3m）
4. N型结构检测（3m）

用法: python scripts/backfill_3m_data.py
"""

import sys
import time as time_module
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.db import Database
from config.settings import DB_PATH
from config.contracts import ContractRegistry
from data.futures_collector import FuturesCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("backfill_3m")

db = Database(str(DB_PATH))
registry = ContractRegistry(str(DB_PATH))
collector = FuturesCollector(db, registry)

# Step 1: 收集 1m 数据（含自动 3m 聚合）
logger.info("=" * 50)
logger.info("Step 1: 采集 1m K线 → 自动生成 3m")
logger.info("=" * 50)
stats = collector.collect_all(period_map={"1m": "1", "15m": "15", "1h": "60", "1d": "D"})

# Step 2: 再次调用 3m→15m→... 聚合（让已有 3m 数据参与聚合）
logger.info("=" * 50)
logger.info("Step 2: 3m→15m→1h→1d→1w 聚合")
logger.info("=" * 50)
from futures.aggregator import aggregate_all
conn = db.get_conn()
contracts = conn.execute(
    "SELECT DISTINCT symbol, contract FROM futures_klines ORDER BY symbol"
).fetchall()
conn.close()

for idx, row in enumerate(contracts, 1):
    sym, contract = row["symbol"], row["contract"]
    try:
        c = aggregate_all(sym, contract, db)
        if any(v > 0 for v in c.values()):
            logger.info("  [%d/%d] %s/%s: 聚合 %s", idx, len(contracts), sym, contract, c)
        if idx % 10 == 0:
            logger.info("  聚合进度 [%d/%d]", idx, len(contracts))
    except Exception as e:
        logger.warning("  聚合失败 %s: %s", sym, e)

# Step 3: MACD 计算（所有周期，含 3m）
logger.info("=" * 50)
logger.info("Step 3: MACD 计算（含 3m）")
logger.info("=" * 50)
from futures.macd import calculate_all_timeframes

macd_total = 0
for idx, row in enumerate(contracts, 1):
    sym, contract = row["symbol"], row["contract"]
    try:
        c = calculate_all_timeframes(sym, contract, db)
        macd_total += sum(c.values())
        if c.get("3m", 0) > 0:
            logger.info("  [%d/%d] %s/%s: MACD 3m=%d", idx, len(contracts), sym, contract, c.get("3m", 0))
    except Exception as e:
        logger.warning("  MACD失败 %s: %s", sym, e)
    if idx % 10 == 0:
        logger.info("  MACD进度 [%d/%d]", idx, len(contracts))
logger.info("MACD 总计: %d 条", macd_total)

# Step 4: 极值点更新（所有周期）
logger.info("=" * 50)
logger.info("Step 4: 极值点更新")
logger.info("=" * 50)
from futures.swing_points import update_all_timeframes
swing_total = 0
for idx, row in enumerate(contracts, 1):
    sym, contract = row["symbol"], row["contract"]
    try:
        c = update_all_timeframes(sym, contract, db)
        swing_total += sum(c.values())
    except Exception as e:
        logger.warning("  极值点失败 %s: %s", sym, e)
    if idx % 10 == 0:
        logger.info("  极值点进度 [%d/%d]", idx, len(contracts))
logger.info("极值点总计: %d 条", swing_total)

# Step 5: N型结构检测（含 3m）
logger.info("=" * 50)
logger.info("Step 5: N型结构检测（含 3m）")
logger.info("=" * 50)
from futures.n_structure import detect_and_save
timeframes = ["3m", "15m", "1h", "1d", "1w"]
n_total = 0
for idx, row in enumerate(contracts, 1):
    sym, contract = row["symbol"], row["contract"]
    for tf in timeframes:
        try:
            ns = detect_and_save(sym, contract, tf, db)
            if ns.get("is_active"):
                n_total += 1
        except Exception as e:
            logger.warning("  N型失败 %s %s: %s", sym, tf, e)
    if idx % 10 == 0:
        logger.info("  N型进度 [%d/%d]", idx, len(contracts))
logger.info("N型结构活跃数: %d", n_total)

# 最终验证
logger.info("=" * 50)
logger.info("最终验证：3m MACD 数据")
logger.info("=" * 50)
with db.get_conn() as conn:
    total_3m_macd = conn.execute(
        "SELECT COUNT(DISTINCT symbol || '|' || contract) as cnt FROM futures_macd WHERE timeframe='3m'"
    ).fetchone()["cnt"]
    total_3m_n = conn.execute(
        "SELECT COUNT(*) as cnt FROM futures_n_structures WHERE timeframe='3m'"
    ).fetchone()["cnt"]
    total_macd_rows = conn.execute(
        "SELECT COUNT(*) as cnt FROM futures_macd WHERE timeframe='3m'"
    ).fetchone()["cnt"]

logger.info("3m MACD 品种数: %d", total_3m_macd)
logger.info("3m MACD 总条数: %d", total_macd_rows)
logger.info("3m N型结构总数: %d", total_3m_n)
print()
print(f"=== 3m 数据刷新完成 ===")
print(f"  3m MACD 品种: {total_3m_macd} / {len(contracts)}")
print(f"  3m N型结构: {total_3m_n}")
