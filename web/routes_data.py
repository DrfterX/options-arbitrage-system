"""数据 API + Paper Trading + 健康检查 + 数据采集 + 回测 + Premium Content + 品种页 Blueprint。

通过函数工厂注入 db 依赖。
"""

import json, logging
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request
from core import PositionTracker

logger = logging.getLogger(__name__)


def _init_data_bp(_db):
    """注入 db 依赖并注册所有数据路由。"""
    from web.helpers import (
        _normalize_n_ts, _clean_contract_n_prefix,
        _enrich_iv_status, _enrich_options_signals, _get_futures_contract,
        _is_delayed_user, _delay_filter, _render_delayed_warning,
    )
    from config.symbol_data import SYMBOL_NAMES, STRATEGY_NAMES, SECTORS

    KLINE_COUNT = 60
    KLINE_MACD_BARS = 200

    bp = Blueprint("data", __name__)

    def _get_hub():
        from signals.hub import SignalHub
        return SignalHub(_db)

    def _get_iv_recorder():
        from data.iv_recorder import IVRecorder
        return IVRecorder(_db)

    def _get_position_tracker():
        return PositionTracker(_db)

    # ═══════════════════════ 信号矩阵 API ═══════════════════════
    # ... (large section, include inline)

    # ────────── /api/matrix ──────────
    @bp.route("/api/matrix")
    def api_matrix():
        conn = _db.get_conn()
        try:
            is_delayed = _is_delayed_user()
            delay_sig = _delay_filter("s.created_at")
            delay_n = _delay_filter("updated_at")
            rows = conn.execute(f'''SELECT s.symbol, s.contract, s.direction, s.signal_type,
                   s.level1_pass, s.level2_pass, s.level3_pass, s.score, s.created_at
                FROM futures_signals s
                INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                    ON s.symbol=l.symbol AND s.created_at=l.mt
                WHERE 1=1 {delay_sig} ORDER BY s.score DESC''').fetchall()
            signals = {}
            for r in rows:
                d = dict(r)
                signals[d["symbol"]] = {
                    "contract": d["contract"], "dir": d["direction"],
                    "type": d["signal_type"], "score": round(d["score"], 2) if d["score"] else 0,
                    "l1": bool(d["level1_pass"]), "l2": bool(d["level2_pass"]), "l3": bool(d["level3_pass"]),
                }
            from futures.shared import _get_active_n_structure as _get_active_ns
            signal_contracts = {
                sym: _clean_contract_n_prefix(info.get("contract", "")).upper()
                for sym, info in signals.items() if info.get("contract")
            }
            for sym in signals:
                if sym not in signal_contracts or not signal_contracts[sym]:
                    row = conn.execute("SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1", (sym,)).fetchone()
                    if row and row["contract"]:
                        signal_contracts[sym] = _clean_contract_n_prefix(row["contract"]).upper()
            TIMEFRAMES = ["15m", "1h", "1d", "1w"]
            structures = {}
            for sym, contract in signal_contracts.items():
                for tf in TIMEFRAMES:
                    ns = _get_active_ns(_db, sym, contract, tf)
                    if ns:
                        structures.setdefault(sym, {})[tf] = {
                            "dir": ns["direction"], "state": ns["state"],
                            "a": ns["point_a_price"], "b": ns["point_b_price"], "c": ns["point_c_price"],
                            "at": ns["point_a_time"], "bt": ns["point_b_time"], "ct": ns["point_c_time"],
                        }
            for sector_name, symbols in SECTORS.items():
                for sym in symbols:
                    if sym in signals or sym in structures:
                        continue
                    row = conn.execute("SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1", (sym,)).fetchone()
                    if not row or not row["contract"]:
                        continue
                    contract = _clean_contract_n_prefix(row["contract"]).upper()
                    for tf in TIMEFRAMES:
                        ns = _get_active_ns(_db, sym, contract, tf)
                        if ns:
                            structures.setdefault(sym, {})[tf] = {
                                "dir": ns["direction"], "state": ns["state"],
                                "a": ns["point_a_price"], "b": ns["point_b_price"], "c": ns["point_c_price"],
                                "at": ns["point_a_time"], "bt": ns["point_b_time"], "ct": ns["point_c_time"],
                            }
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
                                          "a": st["a"], "b": st["b"], "c": st["c"],
                                          "at": st["at"], "bt": st["bt"], "ct": st["ct"]})
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
            cards = []
            for row in rows[:15]:
                d = dict(row)
                cards.append({
                    "sym": d["symbol"], "name": SYMBOL_NAMES.get(d["symbol"], d["symbol"]),
                    "contract": d["contract"], "dir": d["direction"], "type": d["signal_type"],
                    "l1": bool(d["level1_pass"]), "l2": bool(d["level2_pass"]), "l3": bool(d["level3_pass"]),
                    "score": round(d["score"], 2) if d["score"] else 0,
                })
            return jsonify({"matrix": matrix, "cards": cards})
        finally:
            pass

    # ────────── /api/n-structures ──────────
    @bp.route("/api/n-structures")
    def api_n_structures():
        conn = _db.get_conn()
        try:
            is_delayed = _is_delayed_user()
            delay_n = _delay_filter("updated_at")
            delay_sig = _delay_filter("s.created_at")
            delay_klines = _delay_filter("timestamp", "int")
            n_rows = conn.execute(f'''SELECT symbol, contract, timeframe, direction, state,
                   point_a_price, point_b_price, point_c_price,
                   point_a_time, point_b_time, point_c_time, updated_at
                FROM futures_n_structures
                WHERE state NOT IN ('COMPLETED', 'IDLE') {delay_n}
                ORDER BY symbol, timeframe''').fetchall()
            sig_rows = conn.execute(f'''SELECT s.symbol, s.score FROM futures_signals s
                INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                    ON s.symbol=l.symbol AND s.created_at=l.mt
                WHERE 1=1 {delay_sig}''').fetchall()
            scores = {r["symbol"]: round(r["score"], 2) if r["score"] else 0 for r in sig_rows}
            price_rows = conn.execute(f'''SELECT symbol, close, timestamp FROM futures_klines
                WHERE timeframe='1d' {delay_klines}
                  AND (symbol, timestamp) IN (
                      SELECT symbol, MAX(timestamp) FROM futures_klines WHERE timeframe='1d' GROUP BY symbol
                  )''').fetchall()
            current_prices = {r["symbol"]: {"close": r["close"], "ts": r["timestamp"]} for r in price_rows}
            HOLDING_MAP = {"15m": {"label": "短线", "days": "1-3 天"}, "1h": {"label": "短中线", "days": "2-5 天"},
                           "1d": {"label": "中线", "days": "5-10 天"}, "1w": {"label": "长线", "days": "2-4 周"}}
            STATE_LABELS = {"LEG1": "第一笔形成中", "LEG2": "第二笔形成中", "LEG3": "第三笔形成中", "COMPLETED": "已完成", "IDLE": "待激活"}
            by_symbol = {}
            for r in n_rows:
                d = dict(r)
                if d.get("timeframe") in ("1d", "1w"):
                    _normalize_n_ts(d)
                sym = d["symbol"]
                tf = d["timeframe"]
                name = SYMBOL_NAMES.get(sym, sym)
                if sym not in by_symbol:
                    by_symbol[sym] = {"symbol": sym, "name": name, "contract": d["contract"], "score": scores.get(sym, 0), "timeframes": {}, "total_signal": 0}
                cur_price = current_prices.get(sym, {})
                cp = cur_price.get("close")
                c_price = d["point_c_price"]
                leg3_dir = None
                if cp and c_price:
                    leg3_dir = "LONG" if cp > c_price else "SHORT" if cp < c_price else "中性"
                hold = HOLDING_MAP.get(tf, {"label": "—", "days": "—"})
                by_symbol[sym]["timeframes"][tf] = {
                    "direction": d["direction"], "state": d["state"],
                    "state_label": STATE_LABELS.get(d["state"], d["state"]),
                    "a_price": d["point_a_price"], "b_price": d["point_b_price"], "c_price": d["point_c_price"],
                    "a_time": d["point_a_time"], "b_time": d["point_b_time"], "c_time": d["point_c_time"],
                    "leg3_dir": leg3_dir, "hold_label": hold["label"], "hold_days": hold["days"],
                    "current_price": cp, "price_time": cur_price.get("ts"), "updated_at": d.get("updated_at", ""),
                }
            for sym_data in by_symbol.values():
                sym_data["total_signal"] = sum(1 for tf_data in sym_data["timeframes"].values() if tf_data["direction"] and tf_data["state"] not in ("COMPLETED", "IDLE"))
            structures_list = sorted(by_symbol.values(), key=lambda x: (-x["score"], -x["total_signal"]))
            return jsonify(structures_list)
        finally:
            pass

    @bp.route("/api/klines")
    def api_klines():
        conn = _db.get_conn()
        try:
            sym = (request.args.get("symbol", "") or "").upper()
            tf = request.args.get("timeframe", "1d") or "1d"
            if not sym:
                return jsonify({"error": "缺少 symbol"}), 400
            delay_klines = _delay_filter("timestamp", "int")
            count = min(int(request.args.get("count", KLINE_COUNT)), 500)
            rows = conn.execute(f'''SELECT timestamp, open, high, low, close, volume
                FROM futures_klines WHERE symbol=? AND timeframe=? {delay_klines}
                ORDER BY timestamp DESC LIMIT ?''', (sym, tf, count)).fetchall()
            klines = [dict(r) for r in rows]
            klines.reverse()
            # MACD
            macd_count = KLINE_MACD_BARS
            mc_rows = conn.execute(f'''SELECT timestamp, macd, signal, histogram, color
                FROM futures_macd WHERE symbol=? AND timeframe=? ORDER BY timestamp DESC LIMIT ?''',
                (sym, tf, macd_count)).fetchall()
            macd_list = [dict(r) for r in mc_rows]
            macd_list.reverse()
            return jsonify({"klines": klines, "macd": macd_list})
        finally:
            pass

    @bp.route("/api/stats")
    def api_stats():
        conn = _db.get_conn()
        try:
            is_delayed = _is_delayed_user()
            delay_sig = _delay_filter("s.created_at")
            sig_rows = conn.execute(f'''SELECT s.symbol, s.direction, s.signal_type, s.score, s.level1_pass, s.level2_pass, s.level3_pass
                FROM futures_signals s
                INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                    ON s.symbol=l.symbol AND s.created_at=l.mt
                WHERE 1=1 {delay_sig} ORDER BY s.score DESC''').fetchall()
            signal_list = [dict(r) for r in sig_rows]
            long_count = sum(1 for s in signal_list if s["direction"] == "LONG")
            short_count = sum(1 for s in signal_list if s["direction"] == "SHORT")
            max_score = max((s["score"] for s in signal_list if s["score"]), default=0)
            sector_stats = []
            for sector_name, symbols in SECTORS.items():
                sec_rows = [s for s in signal_list if s["symbol"] in symbols]
                if not sec_rows: continue
                longs = sum(1 for s in sec_rows if s["direction"] == "LONG")
                shorts = sum(1 for s in sec_rows if s["direction"] == "SHORT")
                avg_score = sum(s["score"] for s in sec_rows) / len(sec_rows)
                sector_stats.append({"name": sector_name, "count": len(sec_rows), "long": longs, "short": shorts,
                                     "avg_score": round(avg_score, 2), "bias": "多" if longs > shorts else ("空" if shorts > longs else "平")})
            return jsonify({"total": len(signal_list), "long": long_count, "short": short_count, "max_score": max_score,
                            "signal_list": signal_list, "sector_stats": sector_stats})
        finally:
            pass

    @bp.route("/api/signals/futures")
    def api_futures_signals():
        conn = _db.get_conn()
        delay_sig = _delay_filter("s.created_at")
        rows = conn.execute(f'''SELECT s.* FROM futures_signals s ORDER BY s.created_at DESC LIMIT 50''').fetchall()
        return jsonify([dict(r) for r in rows])

    @bp.route("/api/signals/options")
    def api_options_signals():
        hub = _get_hub()
        is_delayed = _is_delayed_user()
        options = _enrich_options_signals([dict(s) for s in hub.get_recent_options(50, delay=is_delayed)])
        return jsonify(options)

    @bp.route("/api/iv/status")
    def api_iv_status():
        iv_recorder = _get_iv_recorder()
        iv_status = _enrich_iv_status(iv_recorder.get_all_status(days=180))
        return jsonify(iv_status)

    @bp.route("/api/summary")
    def api_summary():
        hub = _get_hub()
        iv_recorder = _get_iv_recorder()
        is_delayed = _is_delayed_user()
        options = _enrich_options_signals([dict(s) for s in hub.get_recent_options(15, delay=is_delayed)])
        iv_status = _enrich_iv_status(iv_recorder.get_all_status(days=180))
        return jsonify({"options": options, "iv_status": iv_status})

    @bp.route("/api/filter-stats")
    def api_filter_stats():
        conn = _db.get_conn()
        rows = conn.execute("SELECT push_level, COUNT(*) as c FROM filter_decision_log GROUP BY push_level ORDER BY c DESC").fetchall()
        return jsonify([dict(r) for r in rows])

    @bp.route("/api/filter-log")
    def api_filter_log():
        conn = _db.get_conn()
        rows = conn.execute("SELECT * FROM filter_decision_log ORDER BY created_at DESC LIMIT 50").fetchall()
        return jsonify([dict(r) for r in rows])

    # ────────── Paper Trading ──────────
    @bp.route("/api/positions")
    def api_positions():
        tracker = _get_position_tracker()
        positions = tracker.get_active_positions()
        return jsonify([dict(p) for p in positions])

    @bp.route("/api/positions/history")
    def api_positions_history():
        tracker = _get_position_tracker()
        history = tracker.get_closed_positions()
        return jsonify([dict(p) for p in history])

    @bp.route("/api/positions/open", methods=["POST"])
    def api_position_open():
        data = request.get_json() or {}
        try:
            tracker = _get_position_tracker()
            pos = tracker.open_position(data)
            return jsonify({"ok": True, "position": dict(pos) if pos else {}})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 400

    @bp.route("/api/positions/close", methods=["POST"])
    def api_position_close():
        data = request.get_json() or {}
        pid = data.get("position_id")
        if not pid:
            return jsonify({"ok": False, "error": "缺少 position_id"}), 400
        tracker = _get_position_tracker()
        try:
            result = tracker.close_position(pid, data.get("price"), data.get("reason", ""))
            return jsonify({"ok": True, "result": dict(result) if result else {}})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 400

    @bp.route("/api/positions/stats")
    def api_positions_stats():
        tracker = _get_position_tracker()
        stats = tracker.get_stats()
        return jsonify(stats)

    # ────────── 健康检查 ──────────
    @bp.route("/api/health")
    def api_health():
        conn = _db.get_conn()
        try:
            conn.execute("SELECT 1")
            db_ok = True
        except Exception:
            db_ok = False
        kline_count = conn.execute("SELECT COUNT(*) as c FROM futures_klines LIMIT 1").fetchone()["c"]
        signal_count = conn.execute("SELECT COUNT(*) as c FROM futures_signals LIMIT 1").fetchone()["c"]
        return jsonify({"status": "ok", "db": db_ok, "klines": kline_count, "signals": signal_count, "time": datetime.now().isoformat()})

    # ────────── 数据采集 ──────────
    @bp.route("/api/refresh", methods=["POST"])
    def api_refresh():
        from pipeline.orchestrator import Orchestrator
        from config.settings import SCAN_LIMIT
        mode = (request.args.get("mode") or request.json.get("mode") if request.is_json else "all") if False else "all"
        body = request.get_json() or {}
        mode = body.get("mode", "all")
        orch = Orchestrator()
        try:
            if mode == "futures":
                result = orch.run_futures_scan()
            elif mode == "options":
                result = orch.run_options_scan(limit=SCAN_LIMIT)
            elif mode == "eod":
                result = orch.run_eod()
            else:
                result = orch.run_all(limit=SCAN_LIMIT)
            return jsonify({"ok": True, "result": str(result)[:500]})
        except Exception as e:
            logger.error("数据采集失败: %s", e, exc_info=True)
            return jsonify({"ok": False, "error": str(e)}), 500

    # ────────── 回测 ──────────
    @bp.route("/api/backtest")
    def api_backtest():
        from futures.backtest import run_backtest as _run_backtest
        contract = request.args.get("contract", "")
        if not contract:
            return jsonify({"error": "缺少 contract"}), 400
        results = _run_backtest(contract)
        return jsonify(results)

    # ────────── Premium Content ──────────
    @bp.route("/api/premium/recommendations")
    def api_premium_recommendations():
        from web.stripe_handler import require_premium
        return require_premium(lambda: _premium_recommendations(_db))()

    @bp.route("/api/premium/breakout-alerts")
    def api_premium_breakout_alerts():
        from web.stripe_handler import require_premium
        return require_premium(lambda: _premium_breakout_alerts(_db))()

    @bp.route("/api/premium/top-options")
    def api_premium_top_options():
        from web.stripe_handler import require_premium
        return require_premium(lambda: _premium_top_options(_db))()

    # ────────── 品种页 ──────────
    @bp.route("/symbol/<symbol>")
    def symbol_page(symbol: str):
        sym = symbol.upper()
        conn = _db.get_conn()
        try:
            name = SYMBOL_NAMES.get(sym)
            if not name:
                return render_template("symbol_page.html", exists=False, symbol=sym, name=sym), 404
            sector_name = None
            for sn, symbols in SECTORS.items():
                if sym in symbols:
                    sector_name = sn
                    break
            sector_symbols = SECTORS.get(sector_name, []) if sector_name else []
            is_delayed = _is_delayed_user()
            delay_sig = _delay_filter("s.created_at")
            delay_n = _delay_filter("updated_at", "text", 15)
            row = conn.execute(f'''SELECT s.symbol, s.contract, s.direction, s.signal_type, s.score, s.level1_pass, s.level2_pass, s.level3_pass, s.created_at
                FROM futures_signals s
                INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l ON s.symbol=l.symbol AND s.created_at=l.mt
                WHERE s.symbol=? {delay_sig} ORDER BY s.score DESC LIMIT 1''', (sym,)).fetchone()
            signal = dict(row) if row else None
            n_rows = conn.execute(f'''SELECT timeframe, direction, state, point_a_price, point_b_price, point_c_price, point_a_time, point_b_time, point_c_time, updated_at
                FROM futures_n_structures WHERE symbol=? AND state NOT IN ('COMPLETED','IDLE') {delay_n} ORDER BY timeframe''', (sym,)).fetchall()
            n_structures = [dict(r) for r in n_rows]
            for ns in n_structures:
                if ns.get("timeframe") in ("1d", "1w"):
                    _normalize_n_ts(ns)
            price_row = conn.execute("SELECT close, timestamp FROM futures_klines WHERE symbol=? AND timeframe='1d' ORDER BY timestamp DESC LIMIT 1", (sym,)).fetchone()
            current_price = price_row["close"] if price_row else None
            price_time_str = datetime.fromtimestamp(price_row["timestamp"]).strftime("%m-%d %H:%M") if price_row else ""
            from data.iv_recorder import IVRecorder
            iv_recorder = IVRecorder(_db)
            iv_status = iv_recorder.get_latest_status(sym)
            if iv_status:
                for k in ("avg_iv", "atm_call_iv", "atm_put_iv", "top5_avg_iv"):
                    if iv_status.get(k) is not None:
                        iv_status[k] = round(iv_status[k] * 100, 1)
            opt_row = conn.execute("SELECT unified_score, strategy, signal_type, created_at FROM options_signals WHERE symbol=? ORDER BY created_at DESC LIMIT 1", (sym,)).fetchone()
            opt_signal = dict(opt_row) if opt_row else None
            if opt_signal:
                dir_map = {"BUY": "BULLISH", "SELL": "BEARISH"}
                opt_signal["dir_class"] = dir_map.get(opt_signal.get("signal_type", ""), "NEUTRAL")
            related = []
            for rsym in sector_symbols or []:
                rrow = conn.execute("SELECT direction, score FROM futures_signals WHERE symbol=? ORDER BY created_at DESC LIMIT 1", (rsym,)).fetchone()
                related.append({"symbol": rsym, "name": SYMBOL_NAMES.get(rsym, rsym), "direction": rrow["direction"] if rrow else None, "score": round(rrow["score"], 2) if rrow and rrow["score"] else 0})
            dir_label = {"LONG": "偏多↑", "SHORT": "偏空↓", "NEUTRAL": "中性"}
            sig_summary = ""
            if signal:
                sig_summary = f"信号{dir_label.get(signal['direction'], signal['direction'])}，评分{signal['score']}。"
            n_summary = ""
            for ns in n_structures:
                tf_label = {"15m": "15分钟", "1h": "1小时", "1d": "日线", "1w": "周线"}
                n_summary += f"{tf_label.get(ns['timeframe'], ns['timeframe'])}周期{dir_label.get(ns['direction'], ns['direction'])}（{ns['state']}）；"
            seo_desc = f"{name}（{sym}）期货期权实时信号 — {sig_summary} 多周期N型结构：{n_summary} 数据由信号矩阵自动生成。"
            seo_title = f"{name}（{sym}）实时期货信号 — N型结构多周期分析 | 信号矩阵"
            return render_template("symbol_page.html", exists=True, symbol=sym, name=name, sector=sector_name,
                signal=signal, n_structures=n_structures, current_price=current_price, price_time_str=price_time_str,
                iv_status=iv_status, opt_signal=opt_signal, related=related, seo_title=seo_title, seo_desc=seo_desc)
        finally:
            pass

    return bp