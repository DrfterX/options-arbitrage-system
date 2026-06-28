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
import os
import re
import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, render_template, jsonify, request, abort

from core.db import Database
from config.settings import DB_PATH
from web.stripe_handler import require_premium
from web.iron_ore_api import _build_bp as _build_iron_bp
from web.public_api import _build_bp as _build_public_api_bp
from futures.backtest import run_backtest as _run_backtest

# Greeks 现金化 — 将 Delta/Vega/Theta 换算为人民币现金敞口
from scripts.core.greeks_cash import (
    delta_cash as _delta_cash,
    theta_cash as _theta_cash,
    vega_cash as _vega_cash,
    get_multiplier as _get_multiplier,
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
db = Database(DB_PATH)

# 自动初始化数据库表结构（幂等，container 首次启动时创建所有表）
try:
    db.init_all_tables()
    logger.info("✅ 数据库表结构已就绪")
except Exception as e:
    logger.warning("数据库表初始化异常（非致命）: %s", e)

# ─── N 型结构 1d/1w 时间戳归一化辅助 ──────────────────────────
# 对 1d/1w 周期，将 A/B/C 时间戳归一化到 05:45 UTC (= 13:45 BJT)，
# 与归一化后的 K 线时间戳对齐。确保前端 findBarForNPoint() 的几何
# 匹配识别到正确的 K 线 bar。
_BJ_OFFSET = 8 * 3600
_TARGET_HOUR_SEC = 20700  # 05:45 UTC = 13:45 BJT

def _normalize_n_ts(d: dict) -> None:
    """原地归一化 N 型结构字典的 1d/1w 时间戳。"""
    if d.get("timeframe") not in ("1d", "1w"):
        return
    for key in ("point_a_time", "point_b_time", "point_c_time"):
        ts = d.get(key)
        if ts is None:
            continue
        bj_midnight_utc = ((ts + _BJ_OFFSET) // 86400) * 86400 - _BJ_OFFSET
        d[key] = bj_midnight_utc + _TARGET_HOUR_SEC

# 管理员密码（从环境变量读取；未设置时所有管理请求自动拒绝 → fail-secure）
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


def _admin_pw_ok(candidate: str) -> bool:
    """时序安全地校验管理员密码。空 ADMIN_PASSWORD 时一律拒绝（fail-secure）。"""
    if not ADMIN_PASSWORD:
        return False
    return secrets.compare_digest(str(candidate or ""), ADMIN_PASSWORD)

# 注册 Blueprint
app.register_blueprint(_build_iron_bp(db))
app.register_blueprint(_build_public_api_bp(db))
from web.routes_blog import blog_bp
app.register_blueprint(blog_bp)
from web.routes_stripe import _init_stripe_bp
app.register_blueprint(_init_stripe_bp(db))
from web.routes_auth import _init_auth_bp
app.register_blueprint(_init_auth_bp(db))
from web.routes_data import _init_data_bp
app.register_blueprint(_init_data_bp(db))

from config.symbol_data import SYMBOL_NAMES, STRATEGY_NAMES, SECTORS
from web.helpers import (
    _normalize_n_ts, _admin_pw_ok, _clean_contract_n_prefix,
    _enrich_iv_status, _enrich_options_signals, _get_futures_contract,
    _is_delayed_user, _delay_filter, _render_delayed_warning,
)


# ─── 合约名清洗 → web.helpers ──────────────────-




KLINE_COUNT = 60
KLINE_MACD_BARS = 200  # MACD(12,26,9) 计算用的 K 线数量（大于 KLINE_COUNT，不显示在图上）

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
        # 0. 延迟判断
        is_delayed = _is_delayed_user()
        delayed_warning = _render_delayed_warning()
        delay_sig = _delay_filter("s.created_at")
        delay_n = _delay_filter("updated_at", "text", 15)  # futures_n_structures 用 updated_at

        # 1. 信号矩阵数据
        sig_rows = conn.execute(f'''
            SELECT s.symbol, s.contract, s.direction, s.signal_type,
                   s.level1_pass, s.level2_pass, s.level3_pass, s.score, s.created_at
            FROM futures_signals s
            INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                ON s.symbol=l.symbol AND s.created_at=l.mt
            WHERE 1=1 {delay_sig}
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

        # N型结构 — 使用 _get_active_n_structure 过滤（与弹窗数据来源一致）
        # 避免直接读全表导致的 stale/已过期结构出现在矩阵中
        from futures.shared import _get_active_n_structure as _get_active_ns

        # 构建信号合约映射（标准化合约名，去 n 前缀）
        signal_contracts = {
            sym: _clean_contract_n_prefix(info.get("contract", "")).upper()
            for sym, info in signals.items() if info.get("contract")
        }

        # 对有信号但缺合约的品种，从 N 结构表补全
        for sym in signals:
            if sym not in signal_contracts or not signal_contracts[sym]:
                row = conn.execute(
                    "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
                    (sym,),
                ).fetchone()
                if row and row["contract"]:
                    signal_contracts[sym] = _clean_contract_n_prefix(row["contract"]).upper()

        TIMEFRAMES = ["15m", "1h", "1d", "1w"]
        structures = {}
        for sym, contract in signal_contracts.items():
            for tf in TIMEFRAMES:
                ns = _get_active_ns(db, sym, contract, tf)
                if ns:
                    structures.setdefault(sym, {})[tf] = {
                        "dir": ns["direction"], "state": ns["state"],
                        "a": ns["point_a_price"], "b": ns["point_b_price"], "c": ns["point_c_price"],
                        "at": ns["point_a_time"], "bt": ns["point_b_time"], "ct": ns["point_c_time"],
                    }

        # 对无信号但有活跃 N 型结构的品种，也纳入矩阵
        for sector_name, symbols in SECTORS.items():
            for sym in symbols:
                if sym in signals or sym in structures:
                    continue
                row = conn.execute(
                    "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
                    (sym,),
                ).fetchone()
                if not row or not row["contract"]:
                    continue
                contract = _clean_contract_n_prefix(row["contract"]).upper()
                for tf in TIMEFRAMES:
                    ns = _get_active_ns(db, sym, contract, tf)
                    if ns:
                        structures.setdefault(sym, {})[tf] = {
                            "dir": ns["direction"], "state": ns["state"],
                            "a": ns["point_a_price"], "b": ns["point_b_price"], "c": ns["point_c_price"],
                            "at": ns["point_a_time"], "bt": ns["point_b_time"], "ct": ns["point_c_time"],
                        }

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
                                      "a": st["a"], "b": st["b"], "c": st["c"],
                                      "at": st["at"], "bt": st["bt"], "ct": st["ct"]})
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
                sector_stats=sector_stats,
                delayed_warning=delayed_warning,
                active_tab='futures')
        elif "options.drifter.indevs.in" in host:
            # 期权独立面板 — 只加载期权/IV 数据
            hub = _get_hub()
            options = _enrich_options_signals([dict(s) for s in hub.get_recent_options(20, delay=is_delayed)])

            iv_recorder = _get_iv_recorder()
            iv_status = _enrich_iv_status(iv_recorder.get_all_status(days=180))

            return render_template("options_dashboard.html",
                now=now, options=options,
                iv_status=iv_status, iv_json=json.dumps(iv_status, ensure_ascii=False),
                delayed_warning=delayed_warning,
                active_tab='options')
        elif "signals.drifter.indevs.in" in host:
            # 信号矩阵门户页 — 期货×期权入口，数据由 JS 实时拉取
            return render_template("portal.html", now=now, delayed_warning=delayed_warning,
                active_tab='overview')
        else:
            # 统一看板（默认）— 含期权信号 + IV 状态
            hub = _get_hub()
            options = _enrich_options_signals([dict(s) for s in hub.get_recent_options(15, delay=is_delayed)])

            iv_recorder = _get_iv_recorder()
            iv_status = _enrich_iv_status(iv_recorder.get_all_status(days=180))

            return render_template("dashboard.html",
                now=now, matrix=matrix, cards=cards,
                long_count=long_count, short_count=short_count,
                total_signals=len(signal_list), max_score=max_score,
                sector_stats=sector_stats, options=options,
                iv_status=iv_status, iv_json=json.dumps(iv_status, ensure_ascii=False),
                delayed_warning=delayed_warning,
                active_tab='overview')
    finally:
        pass  # 连接由 Database 管理生命周期


# ─── 调度器 + 启动 ──────────────────────────────────────────  

# 作为 daemon 线程与 gunicorn worker 并行运行。
# DB 级锁保证多 worker 下仅执行一次采集。
from web.scheduler import start_scheduler, start_incremental_heartbeat
try:
    start_scheduler(db)
except Exception as e:
    logger.warning("调度器启动失败（非致命）: %s", e)

# ─── N 型结构增量重算心跳线程 ───────────────────────
# 每 5 秒执行轻量增量重算，与主调度器并行运行。
# 主调度器负责全量数据采集；心跳线程负责新 K 线写入后
# 的增量 N 型结构状态迁移，最快 5s 内响应。
try:
    start_incremental_heartbeat(db)
except Exception as e:
    logger.warning("增量心跳启动失败（非致命）: %s", e)

# ─── Google Search Console 验证文件 ──────────────────────
# Google 的 HTML 文件验证方法要求在站点根目录放置 googleXXXXX.html 文件。
# 本路由将请求映射到 web/verification/ 目录，用户只需将验证文件放入该目录即可。

VERIFICATION_DIR = os.path.join(os.path.dirname(__file__), "verification")


@app.route("/<path:catch_path>")
def catch_all_verification(catch_path):
    """Catch-all: serve Google Search Console verification files at the root."""
    if re.match(r"^google[0-9a-f]{16,}\.html$", catch_path):
        fpath = os.path.join(VERIFICATION_DIR, catch_path)
        if os.path.exists(fpath):
            with open(fpath) as f:
                return f.read(), 200, {"Content-Type": "text/html"}
    abort(404)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5100))
    app.run(host="0.0.0.0", port=port, debug=False)

