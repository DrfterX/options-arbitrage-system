"""
期货信号回测引擎 — 历史预测准确性验证。

对 6430 条历史信号做方向预测回测：
  1. 每个有方向的信号 → 按信号时间最近日线收盘价 = 入场价
  2. 向前 N 个交易日（1/2/5/10）取收盘价作为退出价
  3. LONG：exit > entry → 正确；SHORT：exit < entry → 正确
  4. 按评分区间/信号类型/Level/品种/板块聚合统计准确率

用法：
    from core.db import Database
    from config.settings import DB_PATH
    from futures.backtest import run_backtest

    db = Database(DB_PATH)
    result = run_backtest(db)
    print(result["summary"])
"""

import bisect
import logging
import time as time_module
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─── 参数 ─────────────────────────────────────────────────

LOOKAHEAD_DAYS = [1, 2, 5, 10]

SCORE_BANDS: List[Tuple[float, float, str]] = [
    (0.00, 0.30, "0.00-0.30"),
    (0.30, 0.40, "0.30-0.40"),
    (0.40, 0.50, "0.40-0.50"),
    (0.50, 0.60, "0.50-0.60"),
    (0.60, 1.01, "0.60+"),
]

SECTOR_MAP: Dict[str, List[str]] = {
    "有色":   ["CU", "AL", "ZN", "PB", "NI", "SN", "AO"],
    "贵金属": ["AU", "AG"],
    "黑色":   ["RB", "HC", "I", "J", "JM", "SS", "SF", "SM"],
    "能源化工": ["BU", "FU", "LU", "SC", "RU", "NR", "BR", "TA", "MA",
                 "FG", "SA", "UR", "PX", "EB", "EG", "PG", "PP", "V", "L", "SP", "SH"],
    "农产品": ["M", "Y", "A", "B", "P", "C", "CS", "JD", "LH", "CF",
               "SR", "AP", "CJ", "RM", "OI"],
    "新能源": ["SI", "LC"],
}

# ─── 进程内缓存 ───────────────────────
# 缓存由 web/app.py 中的 get_cached_backtest() 管理，
# run_backtest() 本身是纯函数不读缓存。
# 此全局变量保留以供外部访问，但不用于内部逻辑。
_cache: Dict[str, Any] = {"result": None, "timestamp": 0}
_CACHE_TTL = 300  # 5 秒缓存（外部使用）

# ─── 辅助函数 ────────────────────────────────────────────


def _get_sector(symbol: str) -> str:
    for sector, symbols in SECTOR_MAP.items():
        if symbol in symbols:
            return sector
    return "其他"


def _build_kline_map(conn) -> Dict[str, List[Tuple[int, float]]]:
    """加载所有 1d kline 数据到内存。

    Returns:
        {(symbol, contract): [(timestamp, close), ...]}
    """
    rows = conn.execute(
        """SELECT symbol, contract, timestamp, close
           FROM futures_klines
           WHERE timeframe='1d' AND close IS NOT NULL
           ORDER BY symbol, contract, timestamp ASC"""
    ).fetchall()

    kline_map: Dict[str, List[Tuple[int, float]]] = {}
    for r in rows:
        key = f"{r['symbol']}|{r['contract']}"
        if key not in kline_map:
            kline_map[key] = []
        kline_map[key].append((r['timestamp'], r['close']))

    return kline_map


def _find_entry_price(
    klines: List[Tuple[int, float]], signal_epoch: int
) -> Optional[float]:
    """二分查找信号时间最近的日线（往前找）。"""
    if not klines:
        return None
    timestamps = [k[0] for k in klines]
    idx = bisect.bisect_right(timestamps, signal_epoch) - 1
    if idx < 0:
        return klines[0][1]
    return klines[idx][1]


def _find_exit_prices(
    klines: List[Tuple[int, float]], entry_idx: int, lookahead: List[int]
) -> Dict[str, Optional[float]]:
    """从 entry_idx 之后找 N 个交易日的收盘价。"""
    result: Dict[str, Optional[float]] = {}
    for days in lookahead:
        idx = entry_idx + days
        if idx < len(klines):
            result[str(days)] = klines[idx][1]
        else:
            result[str(days)] = None
    return result


# ─── 核心回测 ────────────────────────────────────────────


def run_backtest(
    db, lookahead_days: Optional[List[int]] = None
) -> Dict[str, Any]:
    """运行全量回测。

    Args:
        db: Database 实例。
        lookahead_days: 向前看交易日数，默认 [1, 2, 5, 10]。

    Returns:
        带 summary/by_score_band/by_signal_type/by_symbol/by_sector/by_level 的字典。
    """

    if lookahead_days is None:
        lookahead_days = LOOKAHEAD_DAYS

    conn = db.get_conn()
    try:
        start = time_module.time()

        # 1. 加载 kline 到内存
        kline_map = _build_kline_map(conn)

        # 2. 获取所有有方向的信号
        signal_rows = conn.execute(
            """SELECT id, symbol, contract, direction, signal_type,
                      level1_pass, level2_pass, level3_pass, score, created_at
               FROM futures_signals
               WHERE direction != 'NONE'
               ORDER BY created_at ASC"""
        ).fetchall()

        logger.info("回测加载 %d 条信号...", len(signal_rows))

        trades: List[Dict] = []
        skipped = 0

        for row in signal_rows:
            sig = dict(row)

            # 转换时间
            try:
                dt = datetime.strptime(sig['created_at'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.fromisoformat(sig['created_at'].replace(' ', 'T'))
            signal_epoch = int(dt.timestamp())

            key = f"{sig['symbol']}|{sig['contract']}"
            klines = kline_map.get(key)
            if not klines:
                skipped += 1
                continue

            # 入场价
            entry_price = _find_entry_price(klines, signal_epoch)
            if entry_price is None:
                skipped += 1
                continue

            # entry 在 kline 列表中的索引
            timestamps = [k[0] for k in klines]
            entry_idx = bisect.bisect_right(timestamps, signal_epoch) - 1
            if entry_idx < 0:
                skipped += 1
                continue

            # 退出价
            exit_prices = _find_exit_prices(klines, entry_idx, lookahead_days)

            # 计算盈亏
            trades_data: Dict[str, Dict] = {}
            for d in lookahead_days:
                dk = str(d)
                exit_p = exit_prices.get(dk)
                if exit_p is None:
                    trades_data[dk] = {"correct": None, "return_pct": None}
                else:
                    if sig['direction'] == 'LONG':
                        pnl = (exit_p - entry_price) / entry_price * 100
                        correct = exit_p > entry_price
                    else:
                        pnl = (entry_price - exit_p) / entry_price * 100
                        correct = exit_p < entry_price

                    trades_data[dk] = {
                        "correct": bool(correct),
                        "return_pct": round(pnl, 2),
                    }

            trades.append({
                "id": sig['id'],
                "symbol": sig['symbol'],
                "contract": sig['contract'],
                "direction": sig['direction'],
                "signal_type": sig['signal_type'],
                "score": round(sig['score'], 2),
                "level1_pass": bool(sig['level1_pass']),
                "level2_pass": bool(sig['level2_pass']),
                "level3_pass": bool(sig['level3_pass']),
                "created_at": sig['created_at'],
                "entry_price": round(entry_price, 2),
                "trades": trades_data,
            })

        elapsed = time_module.time() - start
        logger.info(
            "回测完成: %d 有效, %d 跳过, %.2f 秒",
            len(trades), skipped, elapsed,
        )

        # 3. 聚合统计
        result = {
            "summary": _compute_summary(trades, lookahead_days),
            "by_score_band": _compute_by_score_band(trades, lookahead_days),
            "by_signal_type": _compute_by_signal_type(trades, lookahead_days),
            "by_symbol": _compute_by_symbol(trades, lookahead_days),
            "by_sector": _compute_by_sector(trades, lookahead_days),
            "by_level": _compute_by_level(trades, lookahead_days),
            "total_signals": len(signal_rows),
            "valid_trades": len(trades),
            "skipped": skipped,
            "elapsed_seconds": round(elapsed, 2),
        }

        return result

    finally:
        conn.close()


# ─── 聚合函数 ────────────────────────────────────────────


def _compute_summary(
    trades: List[Dict], lookahead: List[int]
) -> Dict:
    total = len(trades)
    r = {"total_signals": total}

    long_count = sum(1 for t in trades if t["direction"] == "LONG")
    short_count = total - long_count
    r["long_pct"] = round(long_count / total * 100, 1) if total > 0 else 0
    r["short_pct"] = round(short_count / total * 100, 1) if total > 0 else 0

    for d in lookahead:
        dk = str(d)
        correct = sum(1 for t in trades
                      if t["trades"].get(dk) and t["trades"][dk]["correct"] is True)
        wrong = sum(1 for t in trades
                    if t["trades"].get(dk) and t["trades"][dk]["correct"] is False)
        valid = correct + wrong

        returns = [
            t["trades"][dk]["return_pct"]
            for t in trades
            if t["trades"].get(dk) and t["trades"][dk]["return_pct"] is not None
        ]

        r[f"{d}d"] = {
            "correct": correct,
            "wrong": wrong,
            "total": valid,
            "accuracy": round(correct / valid * 100, 1) if valid > 0 else 0,
            "avg_return": round(sum(returns) / len(returns), 2) if returns else 0,
            "max_return": round(max(returns), 2) if returns else 0,
            "min_return": round(min(returns), 2) if returns else 0,
        }

    return r


def _compute_by_score_band(
    trades: List[Dict], lookahead: List[int]
) -> List[Dict]:
    bands = []
    for low, high, label in SCORE_BANDS:
        filt = [t for t in trades if low <= t["score"] < high]
        if not filt:
            continue

        data: Dict = {
            "band": label,
            "count": len(filt),
            "avg_score": round(sum(t["score"] for t in filt) / len(filt), 2),
        }
        for d in lookahead:
            dk = str(d)
            corr = sum(1 for t in filt
                       if t["trades"].get(dk) and t["trades"][dk]["correct"] is True)
            wrg = sum(1 for t in filt
                      if t["trades"].get(dk) and t["trades"][dk]["correct"] is False)
            v = corr + wrg
            data[f"{d}d_acc"] = round(corr / v * 100, 1) if v > 0 else 0
            data[f"{d}d_total"] = v

        bands.append(data)
    return bands


def _compute_by_signal_type(
    trades: List[Dict], lookahead: List[int]
) -> List[Dict]:
    result = []
    for st in ("ENTRY", "CANDIDATE", "WATCH"):
        filt = [t for t in trades if t["signal_type"] == st]
        if not filt:
            continue
        data: Dict = {"signal_type": st, "count": len(filt)}
        for d in lookahead:
            dk = str(d)
            corr = sum(1 for t in filt
                       if t["trades"].get(dk) and t["trades"][dk]["correct"] is True)
            wrg = sum(1 for t in filt
                      if t["trades"].get(dk) and t["trades"][dk]["correct"] is False)
            v = corr + wrg
            data[f"{d}d_acc"] = round(corr / v * 100, 1) if v > 0 else 0
            data[f"{d}d_total"] = v
        result.append(data)
    return result


def _compute_by_symbol(
    trades: List[Dict], lookahead: List[int]
) -> List[Dict]:
    groups: Dict[str, List] = {}
    for t in trades:
        groups.setdefault(t["symbol"], []).append(t)

    result = []
    for sym, group in sorted(groups.items()):
        data: Dict = {"symbol": sym, "count": len(group)}
        for d in lookahead:
            dk = str(d)
            corr = sum(1 for t in group
                       if t["trades"].get(dk) and t["trades"][dk]["correct"] is True)
            wrg = sum(1 for t in group
                      if t["trades"].get(dk) and t["trades"][dk]["correct"] is False)
            v = corr + wrg
            data[f"{d}d_acc"] = round(corr / v * 100, 1) if v > 0 else 0
            data[f"{d}d_total"] = v
        result.append(data)

    result.sort(key=lambda x: x.get("1d_acc", 0), reverse=True)
    return result


def _compute_by_sector(
    trades: List[Dict], lookahead: List[int]
) -> List[Dict]:
    groups: Dict[str, List] = {}
    for t in trades:
        sector = _get_sector(t["symbol"])
        groups.setdefault(sector, []).append(t)

    result = []
    for sector, group in groups.items():
        data: Dict = {"sector": sector, "count": len(group)}
        for d in lookahead:
            dk = str(d)
            corr = sum(1 for t in group
                       if t["trades"].get(dk) and t["trades"][dk]["correct"] is True)
            wrg = sum(1 for t in group
                      if t["trades"].get(dk) and t["trades"][dk]["correct"] is False)
            v = corr + wrg
            data[f"{d}d_acc"] = round(corr / v * 100, 1) if v > 0 else 0
            data[f"{d}d_total"] = v
        result.append(data)

    result.sort(key=lambda x: x.get("1d_acc", 0), reverse=True)
    return result


def _compute_by_level(
    trades: List[Dict], lookahead: List[int]
) -> List[Dict]:
    levels: List[Tuple[str, Any]] = [
        ("L1_ONLY", lambda t: t["level1_pass"] and not t["level2_pass"]),
        ("L1+L2",   lambda t: t["level1_pass"] and t["level2_pass"] and not t["level3_pass"]),
        ("ALL_3",   lambda t: t["level1_pass"] and t["level2_pass"] and t["level3_pass"]),
    ]

    result = []
    for label, pred in levels:
        filt = [t for t in trades if pred(t)]
        if not filt:
            continue
        data: Dict = {"level": label, "count": len(filt)}
        for d in lookahead:
            dk = str(d)
            corr = sum(1 for t in filt
                       if t["trades"].get(dk) and t["trades"][dk]["correct"] is True)
            wrg = sum(1 for t in filt
                      if t["trades"].get(dk) and t["trades"][dk]["correct"] is False)
            v = corr + wrg
            data[f"{d}d_acc"] = round(corr / v * 100, 1) if v > 0 else 0
            data[f"{d}d_total"] = v
        result.append(data)

    return result


# ─── CLI 入口 ─────────────────────────────────────────────


def main():
    """CLI 调用：打印 JSON 回测报告到 stdout。"""
    import json
    from core.db import Database
    from config.settings import DB_PATH

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    db = Database(DB_PATH)
    result = run_backtest(db)
    # 不输出 trades 到 cli
    printable = {k: v for k, v in result.items() if k != "trades"}
    print(json.dumps(printable, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()