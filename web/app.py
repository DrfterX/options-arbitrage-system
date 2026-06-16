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
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, render_template, jsonify, request

from core import PositionTracker
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

def _enrich_iv_status(status_list):
    """为 IV 状态列表添加中文名 + 清洗上期所合约 n 前缀。"""
    import re
    for item in status_list:
        sym = (item.get("symbol") or "").upper()
        item["name"] = SYMBOL_NAMES.get(sym, item.get("symbol", ""))
        # 上期所主力合约 n 前缀清洗: nag2607 → ag2607
        item["contract"] = re.sub(r'^[nN]', '', item.get("contract", ""))
    return status_list


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


def _get_position_tracker():
    """创建 Paper Trading 持仓追踪器实例。"""
    return PositionTracker(db)


@app.route("/")
def index() -> str:
    """信号矩阵门户 — 根据 Host 头选择模板。

      - futures.drifter.indevs.in → futures_dashboard.html（仅期货数据）
      - options.drifter.indevs.in → options_dashboard.html（仅期权数据）
      - signals.drifter.indevs.in → portal.html（期货×期权门户入口页）
      - 其他/默认 → dashboard.html（完整统一看板，含期货+期权）
    """
    conn = db.get_conn()
    try:
        # 0. 动态重算：所有活跃 N 型结构（确保初始页面显示最新数据）
        _restructure_active_structures(conn)

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

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 根据 Host 头选择模板
        host = request.headers.get("Host", "")
        if "futures.drifter.indevs.in" in host:
            # 期货独立面板 — 不加载期权/IV 数据
            return render_template("futures_dashboard.html",
                now=now, matrix=matrix, cards=cards,
                long_count=long_count, short_count=short_count,
                total_signals=len(signal_list), max_score=max_score,
                sector_stats=sector_stats)
        elif "options.drifter.indevs.in" in host:
            # 期权独立面板 — 只加载期权/IV 数据
            hub = _get_hub()
            options = [dict(s) for s in hub.get_recent_options(20)]

            iv_recorder = _get_iv_recorder()
            iv_status = _enrich_iv_status(iv_recorder.get_all_status(days=180))

            return render_template("options_dashboard.html",
                now=now, options=options,
                iv_status=iv_status, iv_json=json.dumps(iv_status, ensure_ascii=False))
        elif "signals.drifter.indevs.in" in host:
            # 信号矩阵门户页 — 期货×期权入口，数据由 JS 实时拉取
            return render_template("portal.html", now=now)
        else:
            # 统一看板（默认）— 含期权信号 + IV 状态
            hub = _get_hub()
            options = [dict(s) for s in hub.get_recent_options(15)]

            iv_recorder = _get_iv_recorder()
            iv_status = _enrich_iv_status(iv_recorder.get_all_status(days=180))

            return render_template("dashboard.html",
                now=now, matrix=matrix, cards=cards,
                long_count=long_count, short_count=short_count,
                total_signals=len(signal_list), max_score=max_score,
                sector_stats=sector_stats, options=options,
                iv_status=iv_status, iv_json=json.dumps(iv_status, ensure_ascii=False))
    finally:
        pass  # 连接由 Database 管理生命周期


# ── N 型结构动态重算辅助 ───────────────────────────────────────


def _restructure_active_structures(conn):
    """对所有有活跃 N 型结构的品种执行动态重算（A 突破迁移）。

    KISS 原则：在 API 读取 N 型结构前按需刷新，不引入后台进程。
    仅对活跃（非 COMPLETED/IDLE）结构执行，开销可控。

    修复 v2：在 dynamic_restructure 前先增量更新极值点（swing points），
    确保 N 型检测基于最新 K 线数据，而非上次 pipeline 运行时的快照。
    """
    try:
        from futures.n_structure import dynamic_restructure
        from futures.swing_points import incremental_update

        active = conn.execute(
            """SELECT DISTINCT symbol, contract FROM futures_n_structures
               WHERE state NOT IN ('COMPLETED', 'IDLE')"""
        ).fetchall()

        if not active:
            return

        timeframes = ["15m", "1h", "1d", "1w"]
        for row in active:
            sym, contract = row["symbol"], row["contract"]
            # 0. 先刷新极值点 — 确保 dynamic_restructure 基于最新 swing points
            for tf in timeframes:
                try:
                    incremental_update(sym, contract, tf, db)
                except Exception:
                    pass  # 单周期极值点失败不阻塞整体
            # 0.5. 刷新周线K线聚合 — 日线→周线（确保周线包含本周最新价格）
            #      否则周线数据停留在上周五收盘，dynamic_restructure 使用旧数据
            try:
                from futures.aggregator import aggregate_klines
                aggregate_klines(sym, contract, db, "1d", "1w", limit=14)
            except Exception:
                pass  # 周线聚合失败不阻塞后续重算
            # 1. 再执行 N 型动态重算
            for tf in timeframes:
                try:
                    dynamic_restructure(sym, contract, tf, db)
                except Exception:
                    pass  # 单品种/周期失败不阻塞整体
    except Exception:
        pass  # 动态重算整体失败不阻塞矩阵渲染


def _get_futures_contract(conn, symbol: str) -> str:
    """获取品种的主力合约代码。"""
    row = conn.execute(
        "SELECT contract FROM futures_klines WHERE symbol=? AND timeframe='1d' ORDER BY timestamp DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    return row["contract"] if row else ""


@app.route("/api/matrix")
def api_matrix():
    """多周期信号矩阵：品种×周期(15m/1h/1d/1w) N型状态 + 共振。

    每次请求先触发 N 型结构动态重算，确保矩阵显示最新结构。
    """
    conn = db.get_conn()
    try:
        # 0. 动态重算：对所有有活跃结构的品种执行 A 突破迁移
        _restructure_active_structures(conn)

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


def _bar_key(bar, tf):
    """生成 bar 的周期键（同日期→同key）。"""
    dt = datetime.fromtimestamp(bar["t"])
    if tf == "1d":
        return dt.strftime("%Y-%m-%d")
    iso = dt.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _compute_realtime_bar(conn, sym, sub_tf, days):
    """从子周期K线计算当前进行中的日/周 K 线。

    Args:
        conn: DB 连接
        sym: 品种代码
        sub_tf: 子周期（"1h"→1d, "1d"→1w）
        days: 回溯天数（0=今天, 7=本周）

    Returns:
        {"key": str, "bar": dict} 或 None（无数据时）
    """
    import time
    now_ts = int(time.time())
    bj_offset = 8 * 3600

    if days == 0:
        # 当日 0 点（北京时间）
        period_start = ((now_ts + bj_offset) // 86400) * 86400 - bj_offset
    else:
        # 本周一 0 点（北京时间）
        bj_ts = now_ts + bj_offset
        weekday = datetime.fromtimestamp(bj_ts).weekday()
        period_start = bj_ts - weekday * 86400
        period_start = (period_start // 86400) * 86400 - bj_offset

    rows = conn.execute(
        """SELECT timestamp, open, high, low, close, volume
           FROM futures_klines
           WHERE symbol=? AND timeframe=? AND timestamp>=?
           ORDER BY timestamp ASC""",
        (sym, sub_tf, period_start),
    ).fetchall()

    # 过滤无效行
    rows = [r for r in rows if r["open"] and r["high"] and r["low"] and r["close"] and r["open"] > 0]
    if not rows:
        return None

    # 聚合为单根K线
    o = rows[0]["open"]
    h = max(r["high"] for r in rows)
    l = min(r["low"] for r in rows)
    c = rows[-1]["close"]
    v = sum(r["volume"] or 0 for r in rows)

    bar = {"t": rows[0]["timestamp"], "o": o, "h": h, "l": l, "c": c, "v": v}

    # 生成周期 key（与 _bar_key 一致）
    dt = datetime.fromtimestamp(bar["t"])
    if days == 7:
        iso = dt.isocalendar()
        key = f"{iso[0]}-W{iso[1]:02d}"
    else:
        key = dt.strftime("%Y-%m-%d")

    return {"key": key, "bar": bar}


@app.route("/api/klines")
def api_klines():
    """获取各品种各周期K线数据（浮窗蜡烛图用）。

    每次请求先触发 N 型结构动态重算，确保 K 线图中的 A/B/C 标记最新。
    """
    sym = request.args.get("symbol")
    tf = request.args.get("timeframe", "1h")
    if not sym:
        return jsonify({"error": "symbol required"}), 400

    conn = db.get_conn()
    try:
        # 0. 先刷新极值点，再动态重算该品种的 N 型结构（确保标记线基于最新 swing points）
        try:
            from futures.n_structure import dynamic_restructure
            from futures.swing_points import incremental_update
            contract = _get_futures_contract(conn, sym)
            if contract:
                incremental_update(sym, contract, tf, db)
                dynamic_restructure(sym, contract, tf, db)
        except Exception:
            pass  # 重算失败不阻塞 K 线返回

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

            # ── 实时日/周 K 线注入 ──
            # 用子周期 K 线（1h→1d, 1d→1w）计算当前进行中周期并追加
            if tf == "1d":
                rt_bars = _compute_realtime_bar(conn, sym, "1h", days=0)
            else:
                rt_bars = _compute_realtime_bar(conn, sym, "1d", days=7)
            if rt_bars:
                rt_key = rt_bars["key"]
                # 如果最后一条 DB bar 属于同一周期 → 替换；否则追加
                if bars and _bar_key(bars[-1], tf) == rt_key:
                    bars[-1] = rt_bars["bar"]
                else:
                    bars.append(rt_bars["bar"])
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
    status = _enrich_iv_status(iv_recorder.get_all_status())
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


# ─── Paper Trading 持仓 API ─────────────────────────────────


@app.route("/api/positions")
def api_positions():
    """获取当前持仓列表（status='open'）。"""
    tracker = _get_position_tracker()
    positions = tracker.get_open_positions()
    return jsonify(positions)


@app.route("/api/positions/history")
def api_positions_history():
    """获取历史平仓记录（status='closed'）。"""
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    tracker = _get_position_tracker()
    positions = tracker.get_closed_positions(limit=limit, offset=offset)
    return jsonify(positions)


@app.route("/api/positions/open", methods=["POST"])
def api_position_open():
    """手动建仓。"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体为空"}), 400

    required = ["symbol", "contract", "direction", "entry_price", "entry_time"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"缺少必填字段: {', '.join(missing)}"}), 400

    direction = data["direction"].upper()
    if direction not in ("LONG", "SHORT"):
        return jsonify({"error": "direction 必须为 LONG 或 SHORT"}), 400

    tracker = _get_position_tracker()
    position_id = tracker.open_position(
        symbol=data["symbol"],
        contract=data["contract"],
        direction=direction,
        entry_price=float(data["entry_price"]),
        entry_time=int(data["entry_time"]),
        signal_id=int(data.get("signal_id", 0)),
        signal_type=data.get("signal_type", "futures"),
        quantity=int(data.get("quantity", 1)),
        stop_loss=float(data.get("stop_loss", 0)),
        take_profit=float(data.get("take_profit", 0)),
    )
    if position_id is None:
        return jsonify({"error": "持仓已存在（同一合约+方向已有未平仓）"}), 409
    return jsonify({"position_id": position_id}), 201


@app.route("/api/positions/close", methods=["POST"])
def api_position_close():
    """平仓。"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体为空"}), 400

    required = ["position_id", "close_price", "close_time"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"缺少必填字段: {', '.join(missing)}"}), 400

    reason = data.get("reason", "manual")
    if reason not in ("stop_loss", "take_profit", "signal_expired", "manual"):
        return jsonify({"error": f"无效的平仓原因: {reason}"}), 400

    partial_qty = data.get("partial_quantity")
    if partial_qty is not None:
        partial_qty = int(partial_qty)

    tracker = _get_position_tracker()
    success = tracker.close_position(
        position_id=int(data["position_id"]),
        close_price=float(data["close_price"]),
        close_time=int(data["close_time"]),
        reason=reason,
        partial_quantity=partial_qty,
    )
    if not success:
        return jsonify({"error": "持仓不存在或已平仓"}), 404
    return jsonify({"status": "closed", "partial": partial_qty is not None})


@app.route("/api/positions/stats")
def api_positions_stats():
    """获取 Paper Trading 综合统计（胜率/总盈亏等）。"""
    tracker = _get_position_tracker()
    stats = tracker.get_stats()
    return jsonify(stats)


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
            "positions", "trades",
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
