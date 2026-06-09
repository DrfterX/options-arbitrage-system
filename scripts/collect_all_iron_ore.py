"""
一次性采集所有铁矿石合约数据。
铁矿石合约在 DCE 挂牌，每年 1/5/9 月交割。
运行: python scripts/collect_all_iron_ore.py
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.db import Database
from config.settings import DB_PATH
import akshare as ak
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
logger = logging.getLogger(__name__)


def generate_iron_ore_contracts() -> list[str]:
    """生成铁矿石理论合约列表 (IYYMM, 1/5/9月)。

    覆盖 2023-2027 年所有 I 系列合约。
    """
    contracts = []
    current_year = datetime.now().year
    for y in range(2023, current_year + 2):
        for m in ("01", "05", "09"):
            code = f"I{str(y)[-2:]}{m}"
            contracts.append(code)
    return contracts


def collect_all():
    """采集所有铁矿石合约的日线、小时、15分钟K线。"""
    db = Database(str(DB_PATH))
    all_contracts = generate_iron_ore_contracts()
    logger.info(f"铁矿石理论合约: {all_contracts}")

    # 先查已有合约，避免重复
    conn = db.get_conn()
    existing = set()
    try:
        rows = conn.execute(
            "SELECT DISTINCT contract FROM futures_klines WHERE symbol='I'"
        ).fetchall()
        existing = {r["contract"] for r in rows}
        logger.info(f"已有数据合约: {sorted(existing)}")
    finally:
        conn.close()

    timeframes_map = {
        "1d": "daily",
        "1h": "60",
        "15m": "15",
    }

    collected = 0
    for contract in all_contracts:
        if contract in existing:
            logger.info(f"  [{contract}] 已存在，跳过")
            continue

        for tf_label, tf_param in timeframes_map.items():
            try:
                # AKShare 新浪期货分钟/日线接口
                if tf_label == "1d":
                    df = ak.futures_zh_daily_sina(symbol=contract)
                else:
                    df = ak.futures_zh_minute_sina(symbol=contract, period=tf_param)

                if df is None or df.empty:
                    logger.warning(f"  [{contract}] {tf_label} 无数据")
                    continue

                conn = db.get_conn()
                try:
                    for _, row in df.iterrows():
                        ts = int(pd.Timestamp(row["date"]).timestamp())
                        conn.execute(
                            """
                            INSERT OR IGNORE INTO futures_klines
                            (symbol, contract, timeframe, timestamp, open, high, low, close, volume)
                            VALUES (?,?,?,?,?,?,?,?,?)
                            """,
                            (
                                "I", contract, tf_label, ts,
                                float(row.get("open", 0)),
                                float(row.get("high", 0)),
                                float(row.get("low", 0)),
                                float(row.get("close", 0)),
                                int(row.get("volume", 0)),
                            ),
                        )
                    conn.commit()
                    logger.info(f"  [{contract}] {tf_label} ✓ {len(df)} 条")
                    collected += 1
                finally:
                    conn.close()

            except Exception as e:
                logger.warning(f"  [{contract}] {tf_label} 失败: {e}")
                # 如果某个合约没有数据（比如还没挂牌），跳过
                if "不存在" in str(e) or "not found" in str(e).lower():
                    break  # 这个合约还没挂牌，剩下的周期也不用试了

    logger.info(f"完成！新增 {collected} 个数据批次")


if __name__ == "__main__":
    import pandas as pd  # akshare 依赖
    collect_all()
