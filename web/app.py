"""
Flask Web 看板应用 — 期货期权统一信号平台。

提供:
  - ``/`` — 统一看板首页。
  - ``/api/matrix`` — 多周期信号矩阵（品种×周期色块+共振）。
  - ``/api/klines`` — K线数据（用于浮窗蜡烛图）。
  - ``/api/stats`` — 板块统计 + 品种汇总。
  - ``/api/signals/futures`` — 最近期货信号 JSON。
  - ``/api/signals/options`` — 最近期权信号 JSON。
  - ``/api/iv/status`` — 所有品种 IV 状态 JSON。
  - ``/api/summary`` — 汇总概览 JSON。
  - ``/api/backtest`` — 全量回测结果 JSON。
"""

import logging
import json
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, jsonify, request

from core.db import Database
from config.settings import DB_PATH
from web.iron_ore_api import _build_bp
from futures.backtest import run_backtest as _run_backtest

logger = logging.getLogger(__name__)

app = Flask(__name__)
db = Database(DB_PATH)

# 注册铁矿石API Blueprint
app.register_blueprint(_build_bp(db))

SYMBOL_NAMES = {
    "CU":"沪铜","AL":"沪铝","ZN":"沪锌","PB":"沪铅","NI":"沪镍","SN":"沪锡",
    "AU":"黄金","AG":"白银","RB":"螺纹钢","HC":"热卷","I":"铁矿","J":"焦炭","JM":"焦煤",
    "BU":"沥青","FU":"燃油","LU":"低硫燃油","SC":"原油","RU":"橡胶","NR":"20号胶",
    "BR":"丁二烯","SP":"纸浆","SS":"不锈钢","M":"豆粕","Y":"豆油","A":"豆一","B":"豆二",
    "P":"棕榈油","C":"玉米","CS":"玉米淀粉","JD":"鸡蛋","LH":"生猪","CF":"棉花",
    "SR":"白糖","TA":"PTA","MA":"甲醇","FG":"玻璃","SA":"纯碱","UR":"尿素",
    "PX":"对二甲苯","SM":"硅锰","SF":"硅铁","AP":"苹果","CJ":"红枣","RM":"菜粕",
    "OI":"菜油","EB":"苯乙烯","EG":"乙二醇","PG":"LPG","PP":"聚丙烯","V":"PVC",
    "L":"塑料","SH":"烧碱","SI":"工业硅","LC":"碳酸锂","AO":"氧化铝",
}

SECTORS = {
    "有色": ["CU","AL","ZN","PB","NI","SN","AO"],
    "贵金属": ["AU","AG"],
    "黑色": ["RB","HC","I","J","JM","SS","SF","SM"],
    "能源化工": ["BU","FU","LU","SC","RU","NR","BR","TA","MA","FG","SA","UR","PX","EB","EG","PG","PP","V","L","SP","SH"],
    "农产品": ["M","Y","A","B","P","C","CS","JD","LH","CF","SR","AP","CJ","RM","OI"],
    "新能源": ["SI","LC"],
}

KLINE_COUNT = 24

def _get_hub():
    from signals.hub import SignalHub
    return SignalHub(db)


def _get_iv_recorder():
    from data.iv_recorder import IVRecorder
    return IVRecorder(db)


@app.route("/")
def index() -> str:
    """统一看板首页 — 服务端渲染，数据嵌入HTML。"""
    conn = db.get_conn()
    try:
        # 1. 信号矩阵数据
        sig_rows = conn.execute('''
            SELECT s.symbol, s.contract, s.direction, s.signal_type,
                   s.level1_pass, s.level2_pass, s.level3_pass, s.score, s.created_at
            FROM futures_signals s
            INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                ON s.symbol=l.symbol AND s.created_at=l.mt
            ORDER BY s.score DESC
        ''').fetchall()
        signals = {}
        for r in sig_rows:
            d = dict(r)
            signals[d["symbol"]] = {
                "contract": d["contract"], "dir": d["direction"],
                "type": d["signal_type"], "score": round(d["score"], 2) if d["score"] else 0,
                "l1": bool(d["level1_pass"]), "l2": bool(d["level2_pass"]), "l3": bool(d["level3_pass"]),
            }
        
        n_rows = conn.execute('''
            SELECT symbol, timeframe, direction, state,
                   point_a_price, point_b_price, point_c_price, updated_at
            FROM futures_n_structures
            WHERE updated_at > datetime('now', '-30 days')
            ORDER BY symbol, timeframe
        ''').fetchall()
        structures = {}
        for r in n_rows:
            d = dict(r)
            structures.setdefault(d["symbol"], {})[d["timeframe"]] = {
                "dir": d["direction"], "state": d["state"],
                "a": d["point_a_price"], "b": d["point_b_price"], "c": d["point_c_price"],
            }

        TIMEFRAMES = ["15m", "1h", "1d", "1w"]
        matrix = []
        for sector_name, symbols in SECTORS.items():
            for sym in symbols:
                # 必须有 N型结构 或 最新信号 才显示该品种
                if sym not in structures and sym not in signals:
                    continue
                name = SYMBOL_NAMES.get(sym, sym)
                sig = signals.get(sym, {})
                cells = []
                for tf in TIMEFRAMES:
                    if sym in structures and tf in structures[sym]:
                        st = structures[sym][tf]
                        cells.append({"tf": tf, "dir": st["dir"], "state": st["state"],
                                      "a": st["a"], "b": st["b"], "c": st["c"]})
                    else:
                        # 没有N型结构但有信号数据，用信号方向填充
                        cells.append({"tf": tf, "dir": sig.get("dir") if sig else None, "state": None})
                dirs = [c["dir"] for c in cells if c["dir"]]
                resonance = max(dirs.count("LONG"), dirs.count("SHORT"))
                matrix.append({
                    "sym": sym, "name": name, "contract": sig.get("contract", ""),
                    "sector": sector_name, "score": sig.get("score", 0),
                    "dir": sig.get("dir"), "resonance": resonance, "cells": cells,
                })
        matrix.sort(key=lambda x: (x["resonance"], x["score"]), reverse=True)
        
        # 2. 信号卡片
        cards = []
        for r in sig_rows[:15]:
            d = dict(r)
            cards.append({
                "sym": d["symbol"], "name": SYMBOL_NAMES.get(d["symbol"], d["symbol"]),
                "contract": d["contract"], "dir": d["direction"], "type": d["signal_type"],
                "l1": bool(d["level1_pass"]), "l2": bool(d["level2_pass"]),
                "l3": bool(d["level3_pass"]),
                "score": round(d["score"], 2) if d["score"] else 0,
            })
        
        # 3. 统计数据
        signal_list = [dict(r) for r in sig_rows]
        long_count = sum(1 for s in signal_list if s["direction"] == "LONG")
        short_count = sum(1 for s in signal_list if s["direction"] == "SHORT")
        max_score = max((s["score"] for s in signal_list), default=0)
        
        sector_stats = []
        for sector_name, symbols in SECTORS.items():
            sec_rows = [s for s in signal_list if s["symbol"] in symbols]
            if not sec_rows:
                continue
            longs = sum(1 for s in sec_rows if s["direction"] == "LONG")
            shorts = sum(1 for s in sec_rows if s["direction"] == "SHORT")
            avg_score = sum(s["score"] for s in sec_rows) / len(sec_rows)
            sector_stats.append({
                "name": sector_name, "count": len(sec_rows),
                "long": longs, "short": shorts,
                "avg_score": round(avg_score, 2),
                "bias": "多" if longs > shorts else ("空" if shorts > longs else "平"),
            })
        
        # 4. 期权信号
        hub = _get_hub()
        options = [dict(s) for s in hub.get_recent_options(15)]
        
        # 5. IV状态
        iv_recorder = _get_iv_recorder()
        iv_status = iv_recorder.get_all_status(days=180)
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return render_template("dashboard.html",
            now=now, matrix=matrix, cards=cards,
            long_count=long_count, short_count=short_count,
            total_signals=len(signal_list), max_score=max_score,
            sector_stats=sector_stats, options=options,
            iv_status=iv_status, iv_json=json.dumps(iv_status, ensure_ascii=False))
    finally:
        pass  # 连接由 Database 管理生命周期


@app.route("/api/matrix")
def api_matrix():
    """多周期信号矩阵：品种×周期(15m/1h/1d/1w) N型状态 + 共振。"""
    conn = db.get_conn()
    try:
        # 最新信号（每个品种取最新一条）
        rows = conn.execute('''
            SELECT s.symbol, s.contract, s.direction, s.signal_type,
                   s.level1_pass, s.level2_pass, s.level3_pass, s.score, s.created_at
            FROM futures_signals s
            INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                ON s.symbol=l.symbol AND s.created_at=l.mt
            ORDER BY s.score DESC
        ''').fetchall()
        signals = {}
        for r in rows:
            d = dict(r)
            signals[d["symbol"]] = {
                "contract": d["contract"], "dir": d["direction"],
                "type": d["signal_type"], "score": round(d["score"], 2) if d["score"] else 0,
                "l1": bool(d["level1_pass"]), "l2": bool(d["level2_pass"]), "l3": bool(d["level3_pass"]),
            }

        # N型结构（每个品种×周期最新状态）
        n_rows = conn.execute('''
            SELECT symbol, timeframe, direction, state,
                   point_a_price, point_b_price, point_c_price, updated_at
            FROM futures_n_structures
            WHERE updated_at > datetime('now', '-30 days')
            ORDER BY symbol, timeframe
        ''').fetchall()

        structures = {}
        for r in n_rows:
            d = dict(r)
            structures.setdefault(d["symbol"], {})[d["timeframe"]] = {
                "dir": d["direction"], "state": d["state"],
                "a": d["point_a_price"], "b": d["point_b_price"], "c": d["point_c_price"],
            }

        # 构建矩阵
        TIMEFRAMES = ["15m", "1h", "1d", "1w"]
        matrix = []
        for sector_name, symbols in SECTORS.items():
            for sym in symbols:
                if sym not in structures:
                    continue
                name = SYMBOL_NAMES.get(sym, sym)
                sig = signals.get(sym, {})
                
                cells = []
                for tf in TIMEFRAMES:
                    if sym in structures and tf in structures[sym]:
                        st = structures[sym][tf]
                        cells.append({"tf": tf, "dir": st["dir"], "state": st["state"],
                                      "a": st["a"], "b": st["b"], "c": st["c"]})
                    else:
                        cells.append({"tf": tf, "dir": None, "state": None})
                
                dirs = [c["dir"] for c in cells if c["dir"]]
                resonance = max(dirs.count("LONG"), dirs.count("SHORT"))
                matrix.append({
                    "sym": sym, "name": name, "contract": sig.get("contract", ""),
                    "sector": sector_name, "score": sig.get("score", 0),
                    "dir": sig.get("dir"), "resonance": resonance, "cells": cells,
                })
        
        matrix.sort(key=lambda x: (x["resonance"], x["score"]), reverse=True)

        # 信号卡片
        cards = []
        for row in rows[:15]:
            d = dict(row)
            cards.append({
                "sym": d["symbol"], "name": SYMBOL_NAMES.get(d["symbol"], d["symbol"]),
                "contract": d["contract"], "dir": d["direction"], "type": d["signal_type"],
                "l1": bool(d["level1_pass"]), "l2": bool(d["level2_pass"]),
                "l3": bool(d["level3_pass"]),
                "score": round(d["score"], 2) if d["score"] else 0,
            })

        return jsonify({"matrix": matrix, "cards": cards})
    finally:
        pass  # 连接由 Database 管理生命周期


@app.route("/api/klines")
def api_klines():
    """获取各品种各周期K线数据（浮窗蜡烛图用）。"""
    sym = request.args.get("symbol")
    tf = request.args.get("timeframe", "1h")
    if not sym:
        return jsonify({"error": "symbol required"}), 400
    
    conn = db.get_conn()
    try:
        rows = conn.execute('''
            SELECT k.timestamp, k.open, k.high, k.low, k.close, k.volume
            FROM futures_klines k
            INNER JOIN (
                SELECT symbol, timeframe, timestamp, MAX(rowid) as max_rowid
                FROM futures_klines
                WHERE symbol=? AND timeframe=?
                GROUP BY symbol, timeframe, timestamp
            ) sub ON k.rowid = sub.max_rowid
            ORDER BY k.timestamp DESC
        ''', (sym, tf)).fetchall()
        
        bars = []
        for r in rows:
            d = dict(r)
            if d["open"] and d["high"] and d["low"] and d["close"] and d["open"] > 0:
                bars.append({
                    "t": d["timestamp"], "o": d["open"], "h": d["high"],
                    "l": d["low"], "c": d["close"], "v": d["volume"] or 0,
                })
        
        # 日线/周线按日期去重
        if tf in ("1d", "1w"):
            seen = {}
            for bar in bars:
                dt = datetime.fromtimestamp(bar["t"])
                if tf == "1d":
                    key = dt.strftime("%Y-%m-%d")
                else:
                    iso = dt.isocalendar()
                    key = f"{iso[0]}-W{iso[1]:02d}"
                if key not in seen or bar["t"] > seen[key]["t"]:
                    seen[key] = bar
            bars = sorted(seen.values(), key=lambda x: x["t"])
        else:
            bars.reverse()
        
        # 简化为前端用格式
        result = []
        for b in bars[-KLINE_COUNT:]:
            result.append({
                "o": round(b["o"], 2), "c": round(b["c"], 2),
                "h": round(b["h"], 2), "l": round(b["l"], 2),
                "up": b["c"] >= b["o"], "v": b["v"],
                "t": b["t"],  # 时间戳，前端用于检测交易断档
            })
        
        return jsonify({"symbol": sym, "timeframe": tf, "bars": result})
    finally:
        pass  # 连接由 Database 管理生命周期


@app.route("/api/stats")
def api_stats():
    """板块统计 + 总体概览。"""
    conn = db.get_conn()
    try:
        rows = conn.execute('''
            SELECT s.symbol, s.direction, s.signal_type, s.score
            FROM futures_signals s
            INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                ON s.symbol=l.symbol AND s.created_at=l.mt
        ''').fetchall()
        
        signals = [dict(r) for r in rows]
        long_count = sum(1 for s in signals if s["direction"] == "LONG")
        short_count = sum(1 for s in signals if s["direction"] == "SHORT")
        
        sector_stats = []
        for sector_name, symbols in SECTORS.items():
            sector_rows = [s for s in signals if s["symbol"] in symbols]
            longs = sum(1 for s in sector_rows if s["direction"] == "LONG")
            shorts = sum(1 for s in sector_rows if s["direction"] == "SHORT")
            avg_score = sum(s["score"] for s in sector_rows) / len(sector_rows) if sector_rows else 0
            sector_stats.append({
                "name": sector_name, "count": len(sector_rows),
                "long": longs, "short": shorts,
                "avg_score": round(avg_score, 2),
                "bias": "多" if longs > shorts else ("空" if shorts > longs else "平"),
            })
        
        return jsonify({
            "total": len(signals), "long": long_count, "short": short_count,
            "max_score": max((s["score"] for s in signals), default=0),
            "sectors": sector_stats,
        })
    finally:
        pass  # 连接由 Database 管理生命周期


@app.route("/api/signals/futures")
def api_futures_signals():
    """获取最近期货信号列表。"""
    limit = request.args.get("limit", 20, type=int)
    hub = _get_hub()
    signals = hub.get_recent_futures(limit)
    return jsonify([dict(s) for s in signals])


@app.route("/api/signals/options")
def api_options_signals():
    """获取最近期权信号列表。"""
    limit = request.args.get("limit", 20, type=int)
    hub = _get_hub()
    signals = hub.get_recent_options(limit)
    return jsonify([dict(s) for s in signals])


@app.route("/api/iv/status")
def api_iv_status():
    """获取所有品种当前 IV 状态（百分位+等级）。"""
    iv_recorder = _get_iv_recorder()
    status = iv_recorder.get_all_status()
    return jsonify(status)


@app.route("/api/summary")
def api_summary():
    """获取看板汇总概览。"""
    hub = _get_hub()
    iv_recorder = _get_iv_recorder()
    futures = hub.get_recent_futures(50)
    options = hub.get_recent_options(50)
    iv_status = iv_recorder.get_all_status()
    return jsonify({
        "futures_count": len(futures),
        "options_count": len(options),
        "iv_status": iv_status[:10],
    })


@app.route("/api/filter-stats")
def api_filter_stats():
    """获取 SmartFilter 统计汇总。"""
    hub = _get_hub()
    stats = hub.get_filter_stats()
    return jsonify(stats)


@app.route("/api/filter-log")
def api_filter_log():
    """获取最近过滤决策日志。"""
    limit = request.args.get("limit", 20, type=int)
    hub = _get_hub()
    log = hub.get_recent_filter_log(limit)
    return jsonify(log)


# ─── 健康检查 API ────────────────────────────────────────────

_APP_START_TIME = None  # set at module init below
import time as _time
_APP_START_TIME = _time.time()

_HEALTH_CACHE: dict = {"result": None, "timestamp": 0}


@app.route("/api/health")
def api_health():
    """系统健康检查：DB连通性 + 数据流状态 + 管线存活。"""
    import time as time_module

    now = time_module.time()
    if _HEALTH_CACHE["result"] and (now - _HEALTH_CACHE["timestamp"]) < 15:
        return jsonify(_HEALTH_CACHE["result"])

    try:
        conn = db.get_conn()
        # 基础连通性
        conn.execute("SELECT 1").fetchone()

        # 各表行数
        tables_info = {}
        for table_name in [
            "futures_klines", "futures_signals", "futures_n_structures",
            "futures_macd", "futures_swing_points", "options_signals",
            "iv_history", "filter_decision_log", "signal_push_log",
        ]:
            count = conn.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            tables_info[table_name] = count

        # 最新信号时间
        last_signal = conn.execute(
            "SELECT MAX(created_at) FROM futures_signals"
        ).fetchone()[0]

        # 最新K线时间
        last_kline = conn.execute(
            "SELECT datetime(MAX(timestamp), 'unixepoch') FROM futures_klines"
        ).fetchone()[0]

        # 最新N型结构时间
        last_n_structure = conn.execute(
            "SELECT MAX(updated_at) FROM futures_n_structures"
        ).fetchone()[0]

        uptime_seconds = int(now - _APP_START_TIME)

        sectors = [
            "futures_klines", "futures_signals", "futures_n_structures",
            "futures_swing_points", "options_signals", "iv_history",
        ]
        status = "healthy"
        issues = []
        for tbl in sectors:
            if tables_info.get(tbl, 0) == 0:
                issues.append(f"{tbl} 无数据")
        if tables_info.get("futures_signals", 0) == 0:
            status = "degraded"
        if issues:
            status = "degraded" if status == "healthy" else status

        result = {
            "status": status,
            "uptime": uptime_seconds,
            "uptime_human": f"{uptime_seconds // 3600}h{(uptime_seconds % 3600) // 60}m{uptime_seconds % 60}s",
            "tables": tables_info,
            "total_rows": sum(tables_info.values()),
            "last_signal": last_signal,
            "last_kline": last_kline,
            "last_n_structure": last_n_structure,
            "issues": issues,
        }
        _HEALTH_CACHE["result"] = result
        _HEALTH_CACHE["timestamp"] = now
        return jsonify(result)
    except Exception as e:
        logger.error("健康检查异常: %s", e)
        return jsonify({"status": "error", "error": str(e)}), 500


# ─── 回测 API ─────────────────────────────────────────────


_BACKTEST_CACHE: dict = {"result": None, "timestamp": 0}


@app.route("/api/backtest")
def api_backtest():
    """获取全量信号回测结果（带 300 秒缓存）。"""
    import time as time_module

    now = time_module.time()
    force = request.args.get("force", "").lower() == "true"

    if not force and _BACKTEST_CACHE["result"] and (now - _BACKTEST_CACHE["timestamp"]) < 300:
        return jsonify(_BACKTEST_CACHE["result"])

    try:
        result = _run_backtest(db)
    except Exception as e:
        logger.error("回测异常: %s", e)
        return jsonify({"error": str(e)}), 500

    printable = {k: v for k, v in result.items() if k != "trades"}
    _BACKTEST_CACHE["result"] = printable
    _BACKTEST_CACHE["timestamp"] = now
    return jsonify(printable)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5100, debug=False)
