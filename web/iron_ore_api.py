"""
铁矿石期货专属 API — 实时行情/年化贴水率/价格百分位。

在 web/app.py 中注册:

    from web.iron_ore_api import create_iron_ore_bp
    app.register_blueprint(create_iron_ore_bp(db))

端点:
  - /api/iron-ore/realtime    实时行情（所有活跃合约）
  - /api/iron-ore/discount    年化贴水率（近远月价差法）
  - /api/iron-ore/percentile  价格历史百分位（30d/90d/1y）
  - /api/iron-ore/contracts   活跃合约列表
  - /api/iron-ore/kline-history  历史K线（供Chart用）
"""

import logging
from datetime import datetime, date
from typing import Optional

import numpy as np
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

# 无硬编码合约 — 改由 _get_active_contracts() 从数据库动态发现
# 规则: 取日线数据中最新的 3 个合约，按到期日排序，最新=主力

TIMEFRAMES_MAP = {
    "1d": "日线",
    "1h": "小时",
    "15m": "15分钟",
}


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _discover_active_contracts(conn) -> list:
    """从数据库动态发现铁矿石活跃合约。

    从数据库动态发现所有有日线数据的铁矿石合约。
    按最新数据时间降序，第一个标记为主力合约。
    返回 [{"symbol": "I2609", "is_main": True}, ...]
    """
    rows = conn.execute(
        """
        SELECT contract, COUNT(*) as cnt, MAX(timestamp) as latest
        FROM futures_klines
        WHERE symbol='I' AND timeframe='1d'
        GROUP BY contract
        ORDER BY latest DESC, cnt DESC
        """
    ).fetchall()

    result = []
    for i, r in enumerate(rows):
        result.append({"symbol": r["contract"], "is_main": (i == 0)})
    return result

def _estimate_expiry(contract: str) -> str:
    """根据合约代码估算到期日。

    铁矿石在大商所，交割月第10个交易日。这里简化用第15天。
    I2509 → 2025-09-15
    """
    year_prefix = "20" + contract[1:3]
    month = contract[3:5]
    return f"{year_prefix}-{month}-15"


def _calc_annualized_discount(
    near_price: float, far_price: float, days_between: int
) -> float:
    """年化贴水率 = (近月价-远月价)/近月价/日差×365×100%"""
    if days_between <= 0 or near_price <= 0:
        return 0.0
    return round((near_price - far_price) / near_price / days_between * 365 * 100, 2)


def _calc_percentile(prices: list, current: float) -> dict:
    """计算当前价格在一组历史价格中的百分位和等级。"""
    arr = np.array(prices, dtype=np.float64)
    n = len(arr)
    if n == 0:
        return {"pct": 50.0, "level": "无数据", "min": 0.0, "max": 0.0, "samples": 0}

    arr_sorted = np.sort(arr)
    # 百分位 = 低于当前价格的样本占比
    pct = np.searchsorted(arr_sorted, current) / n * 100.0

    if pct >= 80:
        level = "高位"
    elif pct >= 50:
        level = "中高"
    elif pct >= 20:
        level = "中等"
    else:
        level = "低位"

    return {
        "pct": round(float(pct), 1),
        "level": level,
        "min": round(float(arr_sorted[0]), 1),
        "max": round(float(arr_sorted[-1]), 1),
        "samples": n,
    }


def _get_latest_close(db, contract: str) -> Optional[float]:
    """获取合约最近一条日线收盘价。"""
    row = db.execute(
        """
        SELECT close FROM futures_klines
        WHERE symbol='I' AND contract=? AND timeframe='1d'
        ORDER BY timestamp DESC LIMIT 1
        """,
        (contract,),
    ).fetchone()
    return float(row["close"]) if row and row["close"] else None


def _get_prev_close(db, contract: str) -> Optional[float]:
    """获取合约前一日收盘价。"""
    row = db.execute(
        """
        SELECT close FROM futures_klines
        WHERE symbol='I' AND contract=? AND timeframe='1d'
        ORDER BY timestamp DESC LIMIT 1 OFFSET 1
        """,
        (contract,),
    ).fetchone()
    return float(row["close"]) if row and row["close"] else None


def _build_bp(db):
    """创建 Blueprint，注入数据库依赖。"""
    bp = Blueprint("iron_ore", __name__)

    # -----------------------------------------------------------------------
    # /api/iron-ore/realtime
    # -----------------------------------------------------------------------
    @bp.route("/api/iron-ore/realtime")
    def realtime():
        """铁矿石所有活跃合约实时行情。"""
        conn = db.get_conn()
        try:
            active = _discover_active_contracts(conn)
            if not active:
                return jsonify({"error": "铁矿石合约暂无数据"}), 503

            contracts = []
            for info in active:
                symbol = info["symbol"]
                is_main = info["is_main"]

                row = conn.execute(
                    """
                    SELECT timestamp, open, high, low, close, volume
                    FROM futures_klines
                    WHERE symbol='I' AND contract=? AND timeframe='1d'
                    ORDER BY timestamp DESC LIMIT 1
                    """,
                    (symbol,),
                ).fetchone()
                if row is None or row["close"] is None:
                    continue

                change = 0.0
                change_pct = 0.0
                prev_close = _get_prev_close(conn, symbol)
                if prev_close and prev_close > 0:
                    change = round(row["close"] - prev_close, 1)
                    change_pct = round(change / prev_close * 100, 2)

                expiry = _estimate_expiry(symbol)
                days_left = (datetime.strptime(expiry, "%Y-%m-%d").date() - date.today()).days

                contracts.append(
                    {
                        "symbol": symbol,
                        "is_main": is_main,
                        "price": round(row["close"], 1),
                        "change": change,
                        "change_pct": change_pct,
                        "open": round(row["open"], 1) if row["open"] else None,
                        "high": round(row["high"], 1) if row["high"] else None,
                        "low": round(row["low"], 1) if row["low"] else None,
                        "volume": row["volume"] or 0,
                        "expiry_date": expiry,
                        "days_to_expiry": days_left,
                    }
                )

            main_symbol = active[0]["symbol"] if active else "I2609"
            updated = datetime.fromtimestamp(
                max(
                    (conn.execute(
                        "SELECT MAX(timestamp) FROM futures_klines WHERE symbol='I' AND timeframe='1d'"
                    ).fetchone()[0] or 0),
                    0,
                )
            ).isoformat()

            return jsonify(
                {
                    "contracts": contracts,
                    "main_contract": main_symbol,
                    "updated_at": updated,
                }
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # /api/iron-ore/discount
    # -----------------------------------------------------------------------
    @bp.route("/api/iron-ore/discount")
    def discount():
        """年化贴水率（近远月合约价差法）。

        仅对未到期且到期日顺序正确的合约对计算。
        """
        conn = db.get_conn()
        try:
            today = date.today()
            all_contracts = _discover_active_contracts(conn)

            # 只保留尚未到期且有交易数据的合约
            active = []
            for info in all_contracts:
                sym = info["symbol"]
                exp_date = datetime.strptime(_estimate_expiry(sym), "%Y-%m-%d").date()
                if exp_date <= today:
                    continue  # 已到期，跳过
                price = _get_latest_close(conn, sym)
                if price is None:
                    continue
                active.append({"symbol": sym, "is_main": info["is_main"], "expiry": exp_date, "price": price})

            spreads = []
            for i in range(len(active) - 1):
                near = active[i]
                far = active[i + 1]

                # 确保近月先到期
                if near["expiry"] >= far["expiry"]:
                    continue

                days = (far["expiry"] - near["expiry"]).days
                spread = round(near["price"] - far["price"], 1)
                spread_pct = round(spread / near["price"] * 100, 2)
                annual_rate = _calc_annualized_discount(near["price"], far["price"], days)

                spreads.append(
                    {
                        "near_contract": near["symbol"],
                        "far_contract": far["symbol"],
                        "near_price": near["price"],
                        "far_price": far["price"],
                        "spread": spread,
                        "spread_pct": spread_pct,
                        "days_between": days,
                        "annualized_rate": annual_rate,
                    }
                )

            overall = spreads[0]["annualized_rate"] if spreads else 0.0
            status = "backwardation" if overall > 0 else ("contango" if overall < 0 else "flat")

            return jsonify(
                {
                    "current_spreads": spreads,
                    "contango_status": status,
                    "active_count": len(active),
                    "calculation_note": "仅计算未到期活跃合约对。年化贴水率=(近月价-远月价)/近月价/日差×365×100%。正值=贴水(Backwardation)，负值=升水(Contango)。",
                }
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # /api/iron-ore/percentile
    # -----------------------------------------------------------------------
    @bp.route("/api/iron-ore/percentile")
    def percentile():
        """价格历史百分位。"""
        contract = request.args.get("contract")
        conn = db.get_conn()
        try:
            # 未指定合约时自动使用主力合约
            if not contract:
                active = _discover_active_contracts(conn)
                contract = active[0]["symbol"] if active else "I2609"

            rows = conn.execute(
                """
                SELECT timestamp, close FROM futures_klines
                WHERE symbol='I' AND contract=? AND timeframe='1d'
                ORDER BY timestamp ASC
                """,
                (contract,),
            ).fetchall()

            if not rows:
                return jsonify({"error": f"合约 {contract} 无数据"}), 404

            closes = [float(r["close"]) for r in rows if r["close"] is not None]
            if not closes:
                return jsonify({"error": "无有效收盘价"}), 404

            current_price = closes[-1]

            result = {"contract": contract, "current_price": round(current_price, 1), "percentiles": {}}

            # 百分位区间
            for label, window_days in [("30d", 30), ("90d", 90), ("1y", 365)]:
                window_prices = closes[-window_days:] if len(closes) >= window_days else closes
                result["percentiles"][label] = _calc_percentile(window_prices, current_price)

            return jsonify(result)
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # /api/iron-ore/contracts
    # -----------------------------------------------------------------------
    @bp.route("/api/iron-ore/contracts")
    def contracts():
        """活跃合约列表（从数据库动态发现）。"""
        conn = db.get_conn()
        try:
            active = _discover_active_contracts(conn)
            contracts_list = []
            for info in active:
                symbol = info["symbol"]
                expiry = _estimate_expiry(symbol)
                days = (datetime.strptime(expiry, "%Y-%m-%d").date() - date.today()).days
                contracts_list.append(
                    {
                        "symbol": symbol,
                        "is_main": info["is_main"],
                        "expiry": expiry,
                        "days_left": max(days, 0),
                    }
                )
            return jsonify({"contracts": contracts_list})
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # /api/iron-ore/kline-history
    # -----------------------------------------------------------------------
    @bp.route("/api/iron-ore/kline-history")
    def kline_history():
        """铁矿石历史K线（给ECharts用）。"""
        contract = request.args.get("contract")
        timeframe = request.args.get("timeframe", "1d")
        days = request.args.get("days", 90, type=int)

        conn = db.get_conn()
        try:
            if not contract:
                active = _discover_active_contracts(conn)
                contract = active[0]["symbol"] if active else "I2609"

            rows = conn.execute(
                """
                SELECT timestamp, open, high, low, close, volume
                FROM futures_klines
                WHERE symbol='I' AND contract=? AND timeframe=?
                ORDER BY timestamp DESC LIMIT ?
                """,
                (contract, timeframe, days),
            ).fetchall()

            bars = []
            for r in reversed(rows):
                if all(r[k] is not None for k in ("open", "high", "low", "close")):
                    bars.append(
                        {
                            "t": r["timestamp"],
                            "o": round(r["open"], 1),
                            "h": round(r["high"], 1),
                            "l": round(r["low"], 1),
                            "c": round(r["close"], 1),
                            "v": r["volume"] or 0,
                        }
                    )

            return jsonify(
                {"contract": contract, "timeframe": timeframe, "bars": bars, "count": len(bars)}
            )
        finally:
            conn.close()

    return bp
