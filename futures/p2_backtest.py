"""
P2 全场回测 — Phase ①+②+③ 信号算法验证。

扫描全市场合约，用新的离散评分系统评估信号质量：
  1. scan_all_contracts() 获取所有合约的当前评分
  2. 统计评分分布（0/1/2/3/4）
  3. 对 ENTRY 信号（score≥2）验证入场价/SL/TP/RR
  4. 按品种/板块聚合

用法：
    cd projects/options_arbitrage_system
    python -m futures.p2_backtest
"""

import json
import logging
import sys
import time
from collections import Counter
from typing import Any, Dict, List

from core.db import Database
from config.settings import DB_PATH
from futures.scorer import scan_all_contracts

logger = logging.getLogger(__name__)


def _get_sector(symbol: str) -> str:
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
    for sector, symbols in SECTOR_MAP.items():
        if symbol in symbols:
            return sector
    return "其他"


def run_p2_backtest(db: Database) -> Dict[str, Any]:
    """运行 P2 全场回测。"""
    start = time.time()

    # 1. 全市场扫描
    print("🔄 扫描全市场合约...")
    results = scan_all_contracts(db, diagnostic=False)
    elapsed = time.time() - start
    print(f"✅ 扫描完成: {len(results)} 合约, {elapsed:.2f}s")

    # 2. 评分分布
    score_dist = Counter(r.overall_score for r in results)
    signal_type_dist = Counter(r.signal_type for r in results)

    # 3. ENTRY 信号详情
    entries = [r for r in results if r.signal_type == "ENTRY"]
    add_positions = [r for r in results if r.signal_type == "ADD_POSITION"]

    # 4. 按板块聚合
    sector_stats: Dict[str, Dict] = {}
    for r in results:
        sec = _get_sector(r.symbol)
        if sec not in sector_stats:
            sector_stats[sec] = {"total": 0, "entry": 0, "scores": []}
        sector_stats[sec]["total"] += 1
        sector_stats[sec]["scores"].append(r.overall_score)
        if r.signal_type in ("ENTRY", "ADD_POSITION"):
            sector_stats[sec]["entry"] += 1

    # 5. ENTRY 信号详情（含 R/R）
    entry_details = []
    for e in entries:
        rr = None
        if e.entry_price and e.stop_loss and e.take_profit:
            risk = abs(e.entry_price - e.stop_loss)
            reward = abs(e.take_profit - e.entry_price)
            rr = round(reward / risk, 2) if risk > 0 else None

        entry_details.append({
            "symbol": e.symbol,
            "contract": e.contract,
            "direction": e.direction,
            "score": e.overall_score,
            "entry_price": e.entry_price,
            "stop_loss": e.stop_loss,
            "take_profit": e.take_profit,
            "risk_reward": rr,
        })

    # 6. 按方向分布
    dir_dist = Counter(r.direction for r in results if r.direction != "NONE")

    return {
        "summary": {
            "total_contracts": len(results),
            "elapsed_seconds": round(elapsed, 2),
            "score_distribution": {
                str(k): v for k, v in sorted(score_dist.items())
            },
            "signal_type_distribution": dict(signal_type_dist),
            "direction_distribution": dict(dir_dist),
            "entry_count": len(entries),
            "add_position_count": len(add_positions),
            "entry_pct": round(len(entries) / max(len(results), 1) * 100, 2),
        },
        "sector_stats": [
            {
                "sector": sec,
                "total": stats["total"],
                "entries": stats["entry"],
                "avg_score": round(sum(stats["scores"]) / len(stats["scores"]), 2),
                "score_distribution": dict(Counter(stats["scores"])),
            }
            for sec, stats in sorted(sector_stats.items())
        ],
        "entry_signals": entry_details,
        "raw_scores": [r.overall_score for r in results],
    }


def main():
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    db = Database(DB_PATH)
    result = run_p2_backtest(db)

    # ── 打印摘要 ──
    s = result["summary"]
    print("\n" + "=" * 60)
    print("📊 P2 全场回测报告")
    print("=" * 60)
    print(f"总合约数: {s['total_contracts']}")
    print(f"耗时: {s['elapsed_seconds']}s")
    print()
    print(f"评分分布:")
    for score, count in sorted(s["score_distribution"].items()):
        bar = "█" * count
        print(f"  score={score}: {count:>4} {bar}")
    print()
    print(f"信号类型:")
    for st, count in sorted(s["signal_type_distribution"].items()):
        print(f"  {st}: {count}")
    print(f"方向分布: {s['direction_distribution']}")
    print(f"\nENTRY信号: {s['entry_count']} ({s['entry_pct']}%)")
    print(f"ADD_POSITION: {s['add_position_count']}")
    print()

    # ── 板块 ──
    print("-" * 60)
    print("板块统计:")
    print(f"{'板块':<10} {'总数':>5} {'ENTRY':>6} {'均分':>5}")
    print("-" * 30)
    for sec in result["sector_stats"]:
        print(f"{sec['sector']:<10} {sec['total']:>5} {sec['entries']:>6} {sec['avg_score']:>5}")

    # ── ENTRY 信号 ──
    print("\n" + "-" * 60)
    print(f"ENTRY 信号明细 ({len(result['entry_signals'])}):")
    if result["entry_signals"]:
        print(f"{'品种':<8} {'合约':<12} {'方向':<8} {'分':>2} {'入场价':>10} {'SL':>10} {'TP':>10} {'R/R':>6}")
        print("-" * 70)
        for e in result["entry_signals"]:
            rr_str = str(e["risk_reward"]) if e["risk_reward"] else "N/A"
            print(f"{e['symbol']:<8} {e['contract']:<12} {e['direction']:<8} "
                  f"{e['score']:>2} {str(e['entry_price'] or 'N/A'):>10} "
                  f"{str(e['stop_loss'] or 'N/A'):>10} {str(e['take_profit'] or 'N/A'):>10} "
                  f"{rr_str:>6}")
    else:
        print("  无 ENTRY 信号")

    # ── JSON 输出 ──
    printable = {k: v for k, v in result.items() if k != "raw_scores"}
    print("\n" + "=" * 60)
    print(json.dumps(printable, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
