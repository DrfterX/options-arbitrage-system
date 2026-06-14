"""
B1 实验 — MFE 诊断分析。
分析 B 阶段所有回测结果的 MFE（最大有利偏移），确认 N 型策略是否有统计 edge。

用法:
    python futures/b1_mfe_analysis.py
"""
import csv
import json
import logging
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from futures.n_paper_backtest import DEFAULT_DB_PATH, OUTPUT_DIR, TARGET_SYMBOLS


@dataclass
class MfeResult:
    symbol: str
    direction: str
    entry_time: int
    exit_time: int
    entry_price: float
    exit_price: float
    exit_reason: str
    pnl: float
    mfe_pct: float      # 最大有利偏移（相对于入场价百分比）
    mae_pct: float      # 最大不利偏移（相对于入场价百分比）
    mfe_atr: float      # MFE 以 ATR 为单位
    mae_atr: float      # MAE 以 ATR 为单位
    atr: float


def get_klines_for_range(db_path: str, symbol: str, start_ts: int, end_ts: int) -> List[dict]:
    """获取指定时间范围内的 15m K 线。"""
    rows = []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT timestamp, open, high, low, close
               FROM futures_klines
               WHERE symbol=? AND timeframe='15m'
                 AND timestamp >= ? AND timestamp <= ?
               ORDER BY timestamp ASC""",
            (symbol, start_ts, end_ts),
        ).fetchall()
    return [dict(r) for r in rows]


def calc_atr(bars: List[dict], period: int = 14) -> float:
    """从 bar 列表计算 ATR。"""
    if len(bars) < period + 1:
        return 0.0
    trs = []
    for i in range(1, len(bars)):
        hl = bars[i]["high"] - bars[i]["low"]
        hc = abs(bars[i]["high"] - bars[i - 1]["close"])
        lc = abs(bars[i]["low"] - bars[i - 1]["close"])
        trs.append(max(hl, hc, lc))
    if not trs:
        return 0.0
    return sum(trs[-period:]) / period


def analyze_trade_mfe(trade: dict, klines: List[dict]) -> Optional[MfeResult]:
    """分析单笔交易的 MFE/MAE。"""
    if not klines:
        return None

    entry_price = trade["entry_price"]
    direction = trade["direction"]

    # 取入场前的 20 根 bar 计算 ATR
    atr = calc_atr(klines[:min(20, len(klines))], 14)
    if atr <= 0:
        atr = entry_price * 0.005  # fallback

    if direction == "LONG":
        max_price = max(k["high"] for k in klines)
        min_price = min(k["low"] for k in klines)
        mfe = max_price - entry_price
        mae = entry_price - min_price
    else:
        max_price = max(k["high"] for k in klines)
        min_price = min(k["low"] for k in klines)
        mfe = entry_price - min_price
        mae = max_price - entry_price

    mfe_pct = (mfe / entry_price) * 100
    mae_pct = (mae / entry_price) * 100
    mfe_atr = mfe / atr if atr > 0 else 0
    mae_atr = mae / atr if atr > 0 else 0

    return MfeResult(
        symbol=trade["symbol"],
        direction=direction,
        entry_time=trade["entry_time_int"],
        exit_time=trade["exit_time_int"],
        entry_price=entry_price,
        exit_price=trade["exit_price"],
        exit_reason=trade["exit_reason"],
        pnl=trade["pnl"],
        mfe_pct=round(mfe_pct, 2),
        mae_pct=round(mae_pct, 2),
        mfe_atr=round(mfe_atr, 2),
        mae_atr=round(mae_atr, 2),
        atr=round(atr, 2),
    )


def load_trades_csv(csv_path: Path) -> List[dict]:
    """从 CSV 加载交易记录。"""
    trades = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse timestamps
            try:
                from datetime import datetime
                et = datetime.strptime(row["entry_time"], "%Y-%m-%d %H:%M:%S")
                xt = datetime.strptime(row["exit_time"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            row["entry_time_int"] = int(et.timestamp())
            row["exit_time_int"] = int(xt.timestamp())
            row["entry_price"] = float(row["entry_price"])
            row["exit_price"] = float(row["exit_price"])
            row["pnl"] = float(row["pnl"])
            trades.append(row)
    return trades


def format_ts(ts: int) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def analyze_all(db_path: str = str(DEFAULT_DB_PATH)) -> Dict[str, List[MfeResult]]:
    """分析基线回测的 MFE（使用已有 CSV）。"""
    csv_path = OUTPUT_DIR / "n_paper_trades_p2.csv"
    if not csv_path.exists():
        print(f"❌ 未找到交易 CSV: {csv_path}")
        return {}

    trades = load_trades_csv(csv_path)
    print(f"已加载 {len(trades)} 笔交易")

    results: List[MfeResult] = []
    for t in trades:
        # 取交易期间加前后缓冲的 15m 数据
        buf = 7200  # 2 小时缓冲
        klines = get_klines_for_range(
            db_path, t["symbol"],
            t["entry_time_int"] - buf,
            t["exit_time_int"] + buf,
        )
        mfe = analyze_trade_mfe(t, klines)
        if mfe:
            results.append(mfe)

    return {"baseline": results}


def print_mfe_report(results: Dict[str, List[MfeResult]]):
    print("\n" + "=" * 70)
    print("  MFE 诊断分析报告（tp_mult=1.0 基线）")
    print("=" * 70)

    for label, mfes in results.items():
        if not mfes:
            print(f"\n  ❌ {label}: 无数据")
            continue

        n = len(mfes)
        wins = [m for m in mfes if m.pnl > 0]
        losses = [m for m in mfes if m.pnl <= 0]

        avg_mfe = sum(m.mfe_pct for m in mfes) / n
        avg_mae = sum(m.mae_pct for m in mfes) / n
        avg_mfe_atr = sum(m.mfe_atr for m in mfes) / n
        avg_mae_atr = sum(m.mae_atr for m in mfes) / n

        win_avg_mfe = sum(m.mfe_atr for m in wins) / len(wins) if wins else 0
        loss_avg_mfe = sum(m.mfe_atr for m in losses) / len(losses) if losses else 0
        win_avg_mae = sum(m.mae_atr for m in wins) / len(wins) if wins else 0
        loss_avg_mae = sum(m.mae_atr for m in losses) / len(losses) if losses else 0

        print(f"\n  {'─' * 50}")
        print(f"  📊 总体统计（{n} 笔交易）")
        print(f"  {'─' * 50}")
        print(f"  平均 MFE:    {avg_mfe:.2f}%  ({avg_mfe_atr:.2f} ATR)")
        print(f"  平均 MAE:    {avg_mae:.2f}%  ({avg_mae_atr:.2f} ATR)")
        print(f"  胜率:        {len(wins)/n*100:.1f}% ({len(wins)}W / {len(losses)}L)")

        print(f"\n  {'─' * 50}")
        print(f"  🏆 盈利交易 vs 💀 亏损交易")
        print(f"  {'─' * 50}")
        print(f"  {'':>20} {'盈利(avg)':>12} {'亏损(avg)':>12} {'差距':>10}")
        print(f"  {'MFE (ATR)':>20} {win_avg_mfe:>11.2f} {loss_avg_mfe:>11.2f} {win_avg_mfe - loss_avg_mfe:>+9.2f}")
        print(f"  {'MAE (ATR)':>20} {win_avg_mae:>11.2f} {loss_avg_mae:>11.2f} {win_avg_mae - loss_avg_mae:>+9.2f}")

        # MFE 分布
        mfe_buckets = {"0-0.5": 0, "0.5-1": 0, "1-2": 0, "2-3": 0, "3+": 0}
        for m in mfes:
            a = m.mfe_atr
            if a < 0.5: mfe_buckets["0-0.5"] += 1
            elif a < 1: mfe_buckets["0.5-1"] += 1
            elif a < 2: mfe_buckets["1-2"] += 1
            elif a < 3: mfe_buckets["2-3"] += 1
            else: mfe_buckets["3+"] += 1

        print(f"\n  MFE 分布（以 ATR 为单位）:")
        for k in ["0-0.5", "0.5-1", "1-2", "2-3", "3+"]:
            cnt = mfe_buckets[k]
            bar = "█" * cnt
            print(f"    {k:>6} ATR: {cnt:>2}笔 {bar}")

        # 关键：看亏损交易是否在反转前到达过有利区域
        loss_ever_profitable = sum(1 for m in losses if m.mfe_pct > 0)
        print(f"\n  🔍 亏损交易中曾经有利可图的: {loss_ever_profitable}/{len(losses)} "
              f"({loss_ever_profitable/len(losses)*100:.0f}% 如果入场时了结)" if losses else "  (无亏损交易)")

        # 出场原因分布
        reasons: Dict[str, int] = {}
        for m in mfes:
            reasons[m.exit_reason] = reasons.get(m.exit_reason, 0) + 1
        print(f"\n  出场原因分布:")
        for r, c in sorted(reasons.items(), key=lambda x: -x[1]):
            win_in_reason = sum(1 for m in mfes if m.exit_reason == r and m.pnl > 0)
            print(f"    {r:>20}: {c:>2}笔 (胜率 {win_in_reason/c*100:.0f}%)")

        # 分品种
        print(f"\n  {'─' * 50}")
        print(f"  分品种 MFE")
        print(f"  {'─' * 50}")
        syms: Dict[str, List[MfeResult]] = {}
        for m in mfes:
            syms.setdefault(m.symbol, []).append(m)
        print(f"  {'Sym':>4} {'Trades':>6} {'MFE(ATR)':>9} {'MAE(ATR)':>9} {'Win%':>6}")
        for sym in TARGET_SYMBOLS:
            sm = syms.get(sym, [])
            if not sm:
                continue
            avg_m = sum(s.mfe_atr for s in sm) / len(sm)
            avg_ma = sum(s.mae_atr for s in sm) / len(sm)
            wr = sum(1 for s in sm if s.pnl > 0) / len(sm) * 100
            print(f"  {sym:>4} {len(sm):>6} {avg_m:>8.2f} {avg_ma:>8.2f} {wr:>5.0f}%")

        # Edge 系数：MFE/MAE 比率
        edge_ratio = avg_mfe_atr / avg_mae_atr if avg_mae_atr > 0 else 0
        print(f"\n  {'─' * 50}")
        print(f"  🎯 Edge 判定")
        print(f"  {'─' * 50}")
        print(f"  MFE/MAE 比率: {edge_ratio:.2f} ( >1.5 表示有统计 edge)")
        if edge_ratio >= 1.5:
            print(f"  ✅ 策略存在统计 edge — 方向判断正确，问题在出场/风险控制")
        elif edge_ratio >= 1.0:
            print(f"  ⚠️ 弱 edge — MFE 略大于 MAE，可能需要更好的出场策略")
        else:
            print(f"  ❌ 无统计 edge — 价格在有利方向走的不如不利方向远")
            print(f"     说明 N 型结构的方向预测能力存疑")

        print()


def main():
    results = analyze_all()
    if results:
        print_mfe_report(results)


if __name__ == "__main__":
    main()