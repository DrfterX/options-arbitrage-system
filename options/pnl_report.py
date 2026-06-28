"""
每日损益归因报告模块 — 按泰勒展开式拆解期权策略 P&L。

从 DB 中读取连续两天的期权信号数据，按 User Directives 确立的 4 项泰勒展开
现金化公式归因：

    ΔV = Δ·ΔS + 0.5·Γ·ΔS² + Vega·Δσ + θ·ΔT

依赖 ``scripts.core.greeks_cash.taylor_pnl_decomposition`` 执行核心计算，
本模块负责数据配对和报告组装。

用法:
    from options.pnl_report import build_pnl_report
    report = build_pnl_report(db)
    print(report["total_records"], "条归因记录")
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from scripts.core.greeks_cash import (
    delta_cash as _delta_cash,
    gamma_cash_1pct as _gamma_cash_1pct,
    vega_cash as _vega_cash,
    theta_cash as _theta_cash,
    taylor_pnl_decomposition as _taylor_pnl,
)

logger = logging.getLogger(__name__)

# ─── 数据查询 ────────────────────────────────────────────────


def _fetch_signals_grouped(db: Any, limit_per_group: int = 2) -> Dict[str, List[dict]]:
    """从 DB 按 (symbol, contract, strategy) 分组获取最近的期权信号。

    Args:
        db: Database 实例。
        limit_per_group: 每组最多取多少条（至少 2 条才能配对）。

    Returns:
        {(symbol, contract, strategy): [dict, ...]} — 按 created_at ASC 排序。
    """
    conn = db.get_conn()
    rows = conn.execute(
        """SELECT id, symbol, contract, strategy, futures_price, iv_avg,
                  net_delta, net_theta, net_vega, net_gamma,
                  created_at
           FROM options_signals
           ORDER BY symbol, contract, strategy, created_at DESC"""
    ).fetchall()

    # 分组
    groups: Dict[str, List[dict]] = {}
    for row in rows:
        d = dict(row)
        key = f"{d['symbol']}|{d.get('contract', '')}|{d['strategy']}"
        if key not in groups:
            groups[key] = []
        if len(groups[key]) < limit_per_group:
            groups[key].append(d)

    # 每组按时间升序（旧的在前，新的在后），方便配对
    for key in groups:
        groups[key].sort(key=lambda x: x.get("created_at", ""))
    return groups


def _safe_float(val: Any, default: float = 0.0) -> float:
    """安全转换为 float。"""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _days_between(t1: str, t2: str) -> float:
    """计算两个 ISO 时间戳相隔的天数。

    Args:
        t1: 较早时间（如 "2026-06-20 09:15:00"）。
        t2: 较晚时间（如 "2026-06-21 09:15:00"）。

    Returns:
        相隔天数（浮点数，最小 1h = 0.0417）。
    """
    try:
        fmt = "%Y-%m-%d %H:%M:%S"
        dt1 = datetime.strptime(t1[:19], fmt)
        dt2 = datetime.strptime(t2[:19], fmt)
        delta = (dt2 - dt1).total_seconds()
        return max(delta / 86400.0, 0.0)
    except (ValueError, TypeError):
        return 0.0


# ─── 归因计算 ────────────────────────────────────────────────


def _attribution_for_pair(
    older: dict,
    newer: dict,
    multiplier: int,
) -> Optional[Dict[str, Any]]:
    """对一对相邻信号计算 P&L 泰勒展开归因。

    Args:
        older: 较早的信号（期初基线）。
        newer: 较新的信号（期末）。
        multiplier: 合约乘数。

    Returns:
        归因字典或 None（数据不足以计算时跳过）。
    """
    # ── 期初基础数据
    s0 = _safe_float(older.get("futures_price"))
    delta0 = _safe_float(older.get("net_delta"))
    gamma0 = _safe_float(older.get("net_gamma"))
    vega0 = _safe_float(older.get("net_vega"))
    theta0 = _safe_float(older.get("net_theta"))

    # ── 期末数据
    s1 = _safe_float(newer.get("futures_price"))
    iv1 = _safe_float(newer.get("iv_avg"))
    iv0 = _safe_float(older.get("iv_avg"))

    # ── 计算变动量
    if s0 <= 0 or s1 <= 0:
        logger.debug("跳过归因（价格无效）: %s/%s", older.get("symbol"), older.get("strategy"))
        return None

    delta_price = s1 - s0          # ΔS
    delta_vol = iv1 - iv0          # Δσ（百分点绝对值）
    days = _days_between(
        str(older.get("created_at", "")),
        str(newer.get("created_at", "")),
    )
    delta_time = max(days, 0.0)    # ΔT（天）

    # 如果 ΔS 和 ΔT 都接近 0，信号没有任何变化，跳过
    if abs(delta_price) < 0.001 and delta_time < 0.01:
        logger.debug("跳过归因（无变化）: %s/%s", older.get("symbol"), older.get("strategy"))
        return None

    try:
        result = _taylor_pnl(
            delta=delta0,
            gamma=gamma0,
            vega=vega0,
            theta=theta0,
            underlying_price=s0,
            multiplier=multiplier,
            delta_price=delta_price,
            delta_vol=delta_vol,
            delta_time=delta_time,
        )
    except (ValueError, ZeroDivisionError) as e:
        logger.warning("归因计算失败: %s/%s — %s", older.get("symbol"), older.get("strategy"), e)
        return None

    result["symbol"] = older.get("symbol", "")
    result["contract"] = older.get("contract", "")
    result["strategy"] = older.get("strategy", "")
    result["period_start"] = str(older.get("created_at", ""))
    result["period_end"] = str(newer.get("created_at", ""))
    result["futures_price_start"] = round(s0, 2)
    result["futures_price_end"] = round(s1, 2)
    result["iv_start"] = round(iv0 * 100, 2) if iv0 else 0.0
    result["iv_end"] = round(iv1 * 100, 2) if iv1 else 0.0
    result["iv_change_pct"] = round(delta_vol * 100, 2)
    result["days_elapsed"] = round(delta_time, 4)
    result["total_pnl"] = result.pop("total", 0.0)

    return result


# ─── 公共 API ────────────────────────────────────────────────


def build_pnl_report(
    db: Any,
    limit_groups: int = 20,
    multiplier_override: Optional[int] = None,
) -> Dict[str, Any]:
    """构建每日损益归因报告。

    逻辑：
    1. 从 DB 按 (symbol, contract, strategy) 分组取最近信号
    2. 每组内相邻两条配对（期初 → 期末）
    3. 调用 ``greeks_cash.taylor_pnl_decomposition()`` 计算 4 项贡献

    Args:
        db: Database 实例（含 get_conn() 方法）。
        limit_groups: 最多处理多少组（默认 20，防 DB 空扫描）。
        multiplier_override: 可选 — 强制所有品种使用统一合约乘数。
                            不传则从 ``get_multiplier(symbol)`` 自动查询。

    Returns:
        {
            "report_date": "2026-06-21",
            "generated_at": "2026-06-21T14:30:00",
            "total_records": 12,
            "attributions": [ ... ],     # 归因列表
            "summary": {
                "total_pnl": 1849.75,
                "total_delta_contrib": 1500.00,
                "total_gamma_contrib": 4.50,
                "total_vega_contrib": 400.00,
                "total_theta_contrib": -54.75,
                "strategy_count": 5,
            },
            "errors": ["..."],           # 非致命错误提示
        }
    """
    from scripts.core.greeks_cash import get_multiplier as _get_multiplier

    groups = _fetch_signals_grouped(db, limit_per_group=2)

    attributions: List[Dict[str, Any]] = []
    errors: List[str] = []

    processed = 0
    for key, signals in groups.items():
        if len(signals) < 2:
            continue

        processed += 1
        if processed > limit_groups:
            errors.append(f"超出处理上限，跳过组: {key}")
            break

        older = signals[0]
        newer = signals[1]
        symbol = older.get("symbol", "")

        # 防御式检查：即使上游分组逻辑被改坏，也不能跨 contract/strategy 错配归因。
        older_contract = str(older.get("contract", "") or "")
        newer_contract = str(newer.get("contract", "") or "")
        older_strategy = str(older.get("strategy", "") or "")
        newer_strategy = str(newer.get("strategy", "") or "")
        if older_contract != newer_contract or older_strategy != newer_strategy:
            errors.append(
                "分组数据不一致，已跳过: "
                f"{key} | older=({older_contract},{older_strategy}) "
                f"newer=({newer_contract},{newer_strategy})"
            )
            continue

        # 确定合约乘数
        if multiplier_override is not None:
            mult = multiplier_override
        else:
            mult = _get_multiplier(symbol)

        attr = _attribution_for_pair(older, newer, multiplier=mult)
        if attr is None:
            continue

        attributions.append(attr)

    # ── 汇总 ──
    total_pnl = sum(a.get("total_pnl", 0) for a in attributions)
    total_delta = sum(a.get("delta_contribution", 0) for a in attributions)
    total_gamma = sum(a.get("gamma_contribution", 0) for a in attributions)
    total_vega = sum(a.get("vega_contribution", 0) for a in attributions)
    total_theta = sum(a.get("theta_contribution", 0) for a in attributions)

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "report_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "generated_at": now_utc,
        "total_records": len(attributions),
        "attributions": attributions,
        "summary": {
            "total_pnl": round(total_pnl, 2),
            "total_delta_contrib": round(total_delta, 2),
            "total_gamma_contrib": round(total_gamma, 2),
            "total_vega_contrib": round(total_vega, 2),
            "total_theta_contrib": round(total_theta, 2),
            "strategy_count": len(attributions),
        },
        "errors": errors,
    }


# ─── 自检（单元测试） ──────────────────────────────────────

if __name__ == "__main__":
    # 快速验证核心函数在无 DB 时的行为
    print("=" * 60)
    print("P&L 归因报告模块 — 自检")
    print("=" * 60)

    from core.db import Database
    from scripts.core.greeks_cash import get_multiplier
    from pathlib import Path

    # 自动定位项目根目录（从当前文件向上找 data/）
    self_path = Path(__file__).resolve()
    project_root = self_path.parent.parent  # options/ → options_arbitrage_system/
    db_path = str(project_root / "data" / "options.db")

    db = Database(db_path)

    # 检查 DB 是否存在
    import os
    if not os.path.exists(db_path):
        print(f"\n⚠  DB 文件不存在: {db_path}")
        print("   请先运行完整系统生成数据后测试。")
        print("   跳过自检。")
        exit(0)

    db.init_all_tables()

    report = build_pnl_report(db, limit_groups=5)

    print(f"\n报告日期: {report['report_date']}")
    print(f"归因数:   {report['total_records']} 条")
    print(f"汇总 PnL: ¥{report['summary']['total_pnl']:,.2f}")
    print(f"  Delta:  ¥{report['summary']['total_delta_contrib']:,.2f}")
    print(f"  Gamma:  ¥{report['summary']['total_gamma_contrib']:,.2f}")
    print(f"  Vega:   ¥{report['summary']['total_vega_contrib']:,.2f}")
    print(f"  Theta:  ¥{report['summary']['total_theta_contrib']:,.2f}")
    print(f"策略数:   {report['summary']['strategy_count']}")

    for i, a in enumerate(report["attributions"][:5]):
        print(f"\n  [{i+1}] {a['symbol']} - {a['strategy']}")
        print(f"      PnL: ¥{a['total_pnl']:>8.2f}")
        print(f"      Δ:   ¥{a['delta_contribution']:>8.2f}  "
              f"Γ: ¥{a['gamma_contribution']:>8.2f}  "
              f"ν: ¥{a['vega_contribution']:>8.2f}  "
              f"θ: ¥{a['theta_contribution']:>8.2f}")
        print(f"      标价: {a['futures_price_start']} → {a['futures_price_end']}  "
              f"({a['days_elapsed']:.1f}天)")

    errors = report.get("errors", [])
    if errors:
        print(f"\n⚠  非致命错误: {len(errors)}")
        for e in errors:
            print(f"  - {e}")

    print(f"\n{'=' * 60}")
    print("自检完成")
    print(f"{'=' * 60}")
