"""
N型结构历史回测器 — 在历史时间点重建 N 型结构并评估方向预测力。

与 ``run_backtest()``（测试 Scorer 滤波后信号）不同，本回测器直接测试
N 型模式**本身**的预测能力：

工作流程：
  1. 加载品种的 1d K线 + 计算全量波峰波谷
  2. 按时间顺序在每个新极值点形成时重建 N 型结构（**只在 C 点确认后评估**）
  3. 记录结构方向（LONG/SHORT）作为方向预测
  4. 检查后续 N 个交易日价格是否按预测方向移动
  5. 支持 Walk-Forward 训练/验证划分
  6. 支持多品种批量回测

用法：
    from core.db import Database
    from config.settings import DB_PATH
    from futures.n_backtest import run_symbol_backtest, run_multi_symbol_backtest

    db = Database(DB_PATH)
    result = run_symbol_backtest(db, "RB", "RB")
    print(result["accuracy"])
"""

import bisect
import json
import logging
import time as time_module
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from core.db import Database
from config.settings import SWING_WINDOWS, DETECT_WINDOWS
from futures.swing_points import detect_swing_points

logger = logging.getLogger(__name__)

# ─── 配置 ───────────────────────────────────────────────────

LOOKAHEAD_DAYS = [1, 2, 5, 10, 20]
TIMEFRAME = "1d"
SWING_WINDOW_N = SWING_WINDOWS.get(TIMEFRAME, 5)

# ─── N 型结构重建（纯函数，无 DB 副作用） ────────────────


def _merge_same_type(points: List[Dict]) -> List[Dict]:
    """合并相邻同向极值点——取更极端值。"""
    merged: List[Dict] = []
    for sp in points:
        if merged and sp["point_type"] == merged[-1]["point_type"]:
            prev = merged[-1]
            if sp["point_type"] == "TROUGH":
                if sp["price"] < prev["price"]:
                    merged[-1] = sp
            else:  # PEAK
                if sp["price"] > prev["price"]:
                    merged[-1] = sp
        else:
            merged.append(sp)
    return merged


def _detect_n_structure(swing_points: List[Dict]) -> Optional[Dict]:
    """从极值点列表中检测 N 型结构（纯函数版 detect_and_save）。

    逻辑与 futures/n_structure.py::detect_and_save 一致：
    1. 合并同向相邻点
    2. 从最新往前滑窗找第一个有效 3 点交替结构
    3. 校验 A→B→C 方向合理

    Args:
        swing_points: 按时间升序排列的极值点列表。

    Returns:
        N 型结构字典（含 direction / point_a/b/c），或 None。
    """
    if len(swing_points) < 3:
        return None

    filtered = _merge_same_type(swing_points)
    if len(filtered) < 3:
        return None

    # 从最新往前滑窗（最多看 5 组）
    n = len(filtered)
    best = None
    for start in range(n - 3, max(n - 5, -1), -1):
        trio = filtered[start: start + 3]
        types = [p["point_type"] for p in trio]
        if not (types[0] != types[1] and types[1] != types[2]):
            continue

        pa, pb, pc = trio[0], trio[1], trio[2]
        direction = "LONG" if pb["price"] > pa["price"] else "SHORT"

        # C 不可突破 A（正向结构要求）
        if direction == "LONG" and pc["price"] <= pa["price"]:
            continue
        if direction == "SHORT" and pc["price"] >= pa["price"]:
            continue

        best = trio
        break

    if best is None:
        return None

    pa, pb, pc = best[0], best[1], best[2]
    direction = "LONG" if pb["price"] > pa["price"] else "SHORT"

    return {
        "direction": direction,
        "point_a_time": pa["timestamp"],
        "point_a_price": pa["price"],
        "point_b_time": pb["timestamp"],
        "point_b_price": pb["price"],
        "point_c_time": pc["timestamp"],
        "point_c_price": pc["price"],
    }


# ─── 数据加载 ─────────────────────────────────────────────


def _load_klines(db: Database, symbol: str, contract: str) -> List[Dict]:
    """加载指定品种的 1d K线（按时间升序）。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT timestamp, open, high, low, close, volume
               FROM futures_klines
               WHERE symbol=? AND contract=? AND timeframe=?
               ORDER BY timestamp ASC""",
            (symbol, contract, TIMEFRAME),
        ).fetchall()
    return [dict(r) for r in rows]


def _ts_to_date_str(ts: int) -> str:
    """Unix 时间戳 → YYYY-MM-DD 字符串。"""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


# ─── 单品种回测 ───────────────────────────────────────────


def run_symbol_backtest(
    db: Database,
    symbol: str,
    contract: str,
    lookahead_days: Optional[List[int]] = None,
    swing_window: Optional[int] = None,
) -> Dict[str, Any]:
    """对单个品种运行 N 型结构历史回测。

    核心逻辑：
      1. 从全量 1d K线计算所有波峰波谷
      2. 按时间顺序遍历每个极值点
      3. 每遇到一个新极值点，用**当前已知**的所有极值点重建 N 型结构
      4. 如果新结构与前一个不同，记录方向预测并检查后续价格

    Args:
        db: Database 实例。
        symbol: 品种代码。
        contract: 合约代码。
        lookahead_days: 向前看的交易日数。
        swing_window: 波峰波谷检测窗口大小，默认使用全局 SWING_WINDOW_N(5)。

    Returns:
        包含 accuracy / predictions / stats 的字典。
    """
    if lookahead_days is None:
        lookahead_days = LOOKAHEAD_DAYS

    sw = swing_window if swing_window is not None else SWING_WINDOW_N

    klines = _load_klines(db, symbol, contract)
    if len(klines) < sw * 2 + 5:
        return {
            "symbol": symbol,
            "contract": contract,
            "error": f"K线不足: {len(klines)} (最少需要 {sw * 2 + 5})",
            "total_structures": 0,
            "predictions": [],
            "accuracy": {},
        }

    # 1. 全量极值点检测
    all_swing_points = detect_swing_points(klines, sw)
    if len(all_swing_points) < 3:
        return {
            "symbol": symbol,
            "contract": contract,
            "error": f"极值点不足: {len(all_swing_points)}",
            "total_structures": 0,
            "predictions": [],
            "accuracy": {},
        }

    # 2. kline timestamp → kline index 映射
    ts_to_idx: Dict[int, int] = {k["timestamp"]: i for i, k in enumerate(klines)}

    # 3. 逐个极值点评估 N 型结构
    prev_key: Optional[Tuple] = None  # (a_ts, b_ts, c_ts) — 防重复
    predictions: List[Dict] = []
    max_lookahead = max(lookahead_days)

    for i in range(2, len(all_swing_points)):
        # 仅使用到当前 i 为止的极值点
        available = all_swing_points[: i + 1]
        struct = _detect_n_structure(available)
        if struct is None:
            continue

        # 去重：结构不变则跳过
        key = (struct["point_a_time"], struct["point_b_time"], struct["point_c_time"])
        if key == prev_key:
            continue
        prev_key = key

        # C 点对应的 kline index
        c_idx = ts_to_idx.get(struct["point_c_time"])
        if c_idx is None:
            continue

        # 确保有足够后续数据验证
        if c_idx + max_lookahead >= len(klines):
            break  # 后面的结构更晚，更不可能有足够数据

        entry_price = klines[c_idx]["close"]

        # 向前验证
        trades_data: Dict[str, Dict] = {}
        for d in lookahead_days:
            exit_idx = c_idx + d
            if exit_idx >= len(klines):
                trades_data[str(d)] = {"correct": None, "return_pct": None}
                continue

            exit_price = klines[exit_idx]["close"]
            if struct["direction"] == "LONG":
                pnl = (exit_price - entry_price) / entry_price * 100
                correct = bool(exit_price > entry_price)
            else:  # SHORT
                pnl = (entry_price - exit_price) / entry_price * 100
                correct = bool(exit_price < entry_price)

            trades_data[str(d)] = {
                "correct": correct,
                "return_pct": round(pnl, 2),
            }

        predictions.append({
            "direction": struct["direction"],
            "entry_time": struct["point_c_time"],
            "entry_date": _ts_to_date_str(struct["point_c_time"]),
            "entry_price": round(entry_price, 2),
            "point_a": (struct["point_a_time"], round(struct["point_a_price"], 2)),
            "point_b": (struct["point_b_time"], round(struct["point_b_price"], 2)),
            "point_c": (struct["point_c_time"], round(struct["point_c_price"], 2)),
            "swing_idx": i,
            "trades": trades_data,
        })

    # 4. 聚合统计
    accuracy = _compute_accuracy(predictions, lookahead_days)
    by_direction = _compute_by_direction(predictions, lookahead_days)
    by_decade = _compute_by_decade(predictions, lookahead_days)

    return {
        "symbol": symbol,
        "contract": contract,
        "klines": len(klines),
        "swing_points": len(all_swing_points),
        "total_structures": len(predictions),
        "predictions": predictions,
        "accuracy": accuracy,
        "by_direction": by_direction,
        "by_decade": by_decade,
    }


# ─── Walk-Forward 回测 ────────────────────────────────────


def run_walkforward(
    db: Database,
    symbol: str,
    contract: str,
    train_years: int = 3,
    valid_months: int = 6,
    lookahead_days: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Walk-Forward 验证：训练期划分 + 验证期独立评估。

    数据按时间顺序分为「训练期 + 验证期」：
      训练期 → 统计 N 型结构准确率基线
      验证期 → 在「未见数据」上评估预测力（更贴近实盘）

    如果总数据不足一个完整窗口，退化为普通回测 + 标注。

    Args:
        db: Database 实例。
        symbol: 品种代码。
        contract: 合约代码。
        train_years: 每个训练期的年数。
        valid_months: 每个验证期的月数。
        lookahead_days: 向前看交易日数。

    Returns:
        含 train/valid 分区结果的字典。
    """
    if lookahead_days is None:
        lookahead_days = LOOKAHEAD_DAYS

    # 先跑全量回测获取所有预测
    full = run_symbol_backtest(db, symbol, contract, lookahead_days)
    if full.get("error") or not full.get("predictions"):
        return full

    # 按 entry_time 排序预测
    predictions = sorted(full["predictions"], key=lambda p: p["entry_time"])
    if not predictions:
        return full

    # 确定时间范围
    first_ts = predictions[0]["entry_time"]
    last_ts = predictions[-1]["entry_time"]

    train_seconds = train_years * 365 * 86400
    valid_seconds = valid_months * 30 * 86400
    window_seconds = train_seconds + valid_seconds

    # 滑动窗口划分：train → valid → train → valid ...
    folds: List[Dict] = []
    fold_start = first_ts

    while fold_start + window_seconds <= last_ts:
        train_end = fold_start + train_seconds
        valid_end = train_end + valid_seconds

        train_preds = [
            p for p in predictions
            if fold_start <= p["entry_time"] < train_end
        ]
        valid_preds = [
            p for p in predictions
            if train_end <= p["entry_time"] < valid_end
        ]

        if train_preds and valid_preds:
            train_acc = _compute_accuracy(train_preds, lookahead_days)
            valid_acc = _compute_accuracy(valid_preds, lookahead_days)
            folds.append({
                "train_start": _ts_to_date_str(int(fold_start)),
                "train_end": _ts_to_date_str(int(train_end)),
                "valid_start": _ts_to_date_str(int(train_end)),
                "valid_end": _ts_to_date_str(int(valid_end)),
                "train_structures": len(train_preds),
                "valid_structures": len(valid_preds),
                "train_accuracy": train_acc,
                "valid_accuracy": valid_acc,
            })

        # 滑动半个窗口
        fold_start += window_seconds // 2

    return {
        "symbol": symbol,
        "contract": contract,
        "total_structures": len(predictions),
        "folds": folds,
        "avg_train_accuracy": _avg_fold_accuracy(folds, "train"),
        "avg_valid_accuracy": _avg_fold_accuracy(folds, "valid"),
    }


# ─── 批量回测 ─────────────────────────────────────────────


def run_multi_symbol_backtest(
    db: Database,
    symbols: List[Tuple[str, str]],
    lookahead_days: Optional[List[int]] = None,
    walkforward: bool = False,
) -> Dict[str, Any]:
    """多品种批量 N 型结构回测。

    Args:
        db: Database 实例。
        symbols: [(symbol, contract), ...] 列表。
        lookahead_days: 向前看交易日数。
        walkforward: 是否运行 Walk-Forward。

    Returns:
        聚合结果字典。
    """
    if lookahead_days is None:
        lookahead_days = LOOKAHEAD_DAYS

    start = time_module.time()
    results: List[Dict] = []
    errors = 0

    for sym, ctr in symbols:
        try:
            if walkforward:
                result = run_walkforward(db, sym, ctr, lookahead_days=lookahead_days)
            else:
                result = run_symbol_backtest(db, sym, ctr, lookahead_days)
            results.append(result)
            # Log appropriate accuracy summary
            if walkforward:
                t1d = result.get("avg_train_accuracy", {}).get("avg_train_accuracy", {}).get("1d_avg", 0)
                v1d = result.get("avg_valid_accuracy", {}).get("avg_valid_accuracy", {}).get("1d_avg", 0)
                logger.info("%s: %d 结构, WFA train=%.1f%% valid=%.1f%% 1d",
                             sym, result.get("total_structures", 0), t1d, v1d)
            else:
                logger.info("%s: %d 结构, %.1f%% 1d 准确率",
                             sym, result.get("total_structures", 0),
                             result.get("accuracy", {}).get("1d", {}).get("accuracy", 0))
        except Exception as e:
            logger.error("%s 回测异常: %s", sym, e)
            results.append({"symbol": sym, "contract": ctr, "error": str(e)})

    # 聚合（WFA 模式不聚合 accuracy，因为各品种 fold 结构不同）
    if walkforward:
        wfa_by_symbol = []
        for r in results:
            if r.get("error"):
                continue
            wfa_by_symbol.append({
                "symbol": r["symbol"],
                "contract": r.get("contract", ""),
                "total_structures": r.get("total_structures", 0),
                "avg_train_accuracy": r.get("avg_train_accuracy", {}),
                "avg_valid_accuracy": r.get("avg_valid_accuracy", {}),
            })
        return {
            "mode": "walkforward",
            "symbols_count": len(symbols),
            "success_count": len(symbols) - errors,
            "error_count": errors,
            "by_symbol": wfa_by_symbol,
            "elapsed_seconds": round(time_module.time() - start, 2),
        }

    # 非 WFA 模式：聚合 accuracy
    all_preds: List[Dict] = []
    total_klines = 0
    total_swings = 0
    total_structs = 0

    for r in results:
        if r.get("error"):
            errors += 1
            continue
        total_klines += r.get("klines", 0)
        total_swings += r.get("swing_points", 0)
        total_structs += r.get("total_structures", 0)
        all_preds.extend(r.get("predictions", []))

    elapsed = time_module.time() - start

    return {
        "symbols_count": len(symbols),
        "success_count": len(symbols) - errors,
        "error_count": errors,
        "total_klines": total_klines,
        "total_swing_points": total_swings,
        "total_structures": total_structs,
        "accuracy": _compute_accuracy(all_preds, lookahead_days),
        "by_symbol": [
            {
                "symbol": r["symbol"],
                "contract": r.get("contract", ""),
                "structures": r.get("total_structures", 0),
                "accuracy": r.get("accuracy", {}),
            }
            for r in results
            if not r.get("error")
        ],
        "elapsed_seconds": round(elapsed, 2),
    }


# ─── 聚合函数 ─────────────────────────────────────────────


def _compute_accuracy(
    predictions: List[Dict], lookahead: List[int]
) -> Dict[str, Any]:
    """计算预测准确率聚合。"""
    total = len(predictions)
    result: Dict = {"total_structures": total}

    long_count = sum(1 for p in predictions if p["direction"] == "LONG")
    short_count = total - long_count
    result["long_pct"] = round(long_count / total * 100, 1) if total else 0
    result["short_pct"] = round(short_count / total * 100, 1) if total else 0

    for d in lookahead:
        dk = str(d)
        correct = sum(
            1 for p in predictions
            if p["trades"].get(dk) and p["trades"][dk]["correct"] is True
        )
        wrong = sum(
            1 for p in predictions
            if p["trades"].get(dk) and p["trades"][dk]["correct"] is False
        )
        valid = correct + wrong

        returns = [
            p["trades"][dk]["return_pct"]
            for p in predictions
            if p["trades"].get(dk) and p["trades"][dk]["return_pct"] is not None
        ]

        result[f"{d}d"] = {
            "correct": correct,
            "wrong": wrong,
            "total": valid,
            "accuracy": round(correct / valid * 100, 1) if valid else 0,
            "avg_return": round(sum(returns) / len(returns), 2) if returns else 0,
            "max_return": round(max(returns), 2) if returns else 0,
            "min_return": round(min(returns), 2) if returns else 0,
        }

    return result


def _compute_by_direction(
    predictions: List[Dict], lookahead: List[int]
) -> Dict[str, Any]:
    """按方向拆分的准确率。"""
    result = {}
    for direction in ("LONG", "SHORT"):
        filt = [p for p in predictions if p["direction"] == direction]
        if not filt:
            continue
        result[direction] = _compute_accuracy(filt, lookahead)
    return result


def _compute_by_decade(
    predictions: List[Dict], lookahead: List[int]
) -> List[Dict]:
    """按年代（2010s / 2020s）拆分的准确率。"""
    groups: Dict[str, List] = {}
    for p in predictions:
        year = _ts_to_date_str(p["entry_time"])[:4]
        decade = f"{year[:3]}0s"
        groups.setdefault(decade, []).append(p)

    result = []
    for decade in sorted(groups.keys()):
        entry = {"decade": decade, "count": len(groups[decade])}
        acc = _compute_accuracy(groups[decade], lookahead)
        for d in lookahead:
            entry[f"{d}d_acc"] = acc.get(f"{d}d", {}).get("accuracy", 0)
        result.append(entry)
    return result


def _avg_fold_accuracy(
    folds: List[Dict], phase: str
) -> Dict[str, Any]:
    """计算 Walk-Forward 折叠平均准确率。"""
    key = f"avg_{phase}_accuracy"
    if not folds:
        return {key: 0, "folds": 0}

    # 取 1d 和 5d 准确率平均
    d1_accs = []
    d5_accs = []
    for f in folds:
        d1 = f.get(f"{phase}_accuracy", {}).get("1d", {}).get("accuracy", 0)
        d5 = f.get(f"{phase}_accuracy", {}).get("5d", {}).get("accuracy", 0)
        d1_accs.append(d1)
        d5_accs.append(d5)

    return {
        key: {
            "folds": len(folds),
            f"1d_avg": round(sum(d1_accs) / len(d1_accs), 1) if d1_accs else 0,
            f"5d_avg": round(sum(d5_accs) / len(d5_accs), 1) if d5_accs else 0,
            f"1d_range": [round(min(d1_accs), 1), round(max(d1_accs), 1)] if d1_accs else [0, 0],
            f"5d_range": [round(min(d5_accs), 1), round(max(d5_accs), 1)] if d5_accs else [0, 0],
        }
    }


# ─── CLI 入口 ─────────────────────────────────────────────


def main():
    """CLI 入口：运行回测并输出 JSON 报告。"""
    import argparse

    parser = argparse.ArgumentParser(description="N 型结构历史回测器")
    parser.add_argument("--symbol", "-s", help="品种代码，不传则全量回测")
    parser.add_argument("--contract", "-c", default=None,
                        help="合约代码，默认同 symbol")
    parser.add_argument("--walkforward", "-w", action="store_true",
                        help="运行 Walk-Forward 验证")
    parser.add_argument("--lookahead", "-l", type=int, nargs="*",
                        default=[1, 2, 5, 10, 20],
                        help="向前看交易日数")
    parser.add_argument("--compact", action="store_true",
                        help="简洁输出（不包含逐条预测明细）")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )

    from config.settings import DB_PATH
    db = Database(DB_PATH)

    TARGET_SYMBOLS = [
        ("RB", "RB"), ("Y", "Y"), ("P", "P"),
        ("EB", "EB"), ("L", "L"), ("PG", "PG"), ("TA", "TA"),
    ]

    if args.symbol:
        contract = args.contract or args.symbol
        if args.walkforward:
            result = run_walkforward(db, args.symbol, contract,
                                     lookahead_days=args.lookahead)
        else:
            result = run_symbol_backtest(db, args.symbol, contract,
                                         lookahead_days=args.lookahead)
    else:
        result = run_multi_symbol_backtest(
            db, TARGET_SYMBOLS,
            lookahead_days=args.lookahead,
            walkforward=args.walkforward,
        )

    if args.compact and "predictions" in result:
        result.pop("predictions", None)
    # WFA 结果里 predictions 是从 full 拿的，需要清理
    if args.compact and "folds" in result:
        for f in result.get("folds", []):
            f.get("train_accuracy", {}).pop("total_structures", None)
            f.get("valid_accuracy", {}).pop("total_structures", None)

    # 确保预测列表不输出到终端（太多）
    if "predictions" in result and not args.symbol:
        pred_count = len(result["predictions"])
        result.pop("predictions")
        result["_prediction_count"] = pred_count

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()