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
import sqlite3
import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, render_template, jsonify, request

from core import PositionTracker
from core.db import Database
from config.settings import DB_PATH
from web.stripe_handler import require_premium
from web.iron_ore_api import _build_bp as _build_iron_bp
from web.public_api import _build_bp as _build_public_api_bp
from futures.backtest import run_backtest as _run_backtest

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

# 注册铁矿石API Blueprint
app.register_blueprint(_build_iron_bp(db))

# 注册公开数据 API v1 Blueprint
app.register_blueprint(_build_public_api_bp(db))

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
    "PF":"花生仁","PK":"花生","PR":"聚丙烯",
}

STRATEGY_NAMES = {
    "iron_condor": "铁鹰策略",
    "vertical_spread": "垂直价差",
    "calendar_spread": "日历价差",
    "covered_call": "备兑看涨",
    "protective_put": "保护看跌",
    "straddle": "跨式策略",
    "strangle": "宽跨式",
    "short_strangle": "卖跨",
    "bull_put": "牛沽",
    "bear_call": "熊购",
    "ratio_spread": "比例价差",
}


def _clean_contract_n_prefix(contract: str) -> str:
    """清洗合约前缀: ag/nag2607 → ag2607, nag2607 → ag2607。"""
    import re
    c = contract or ""
    # 去掉 symbol/ 前缀 (如 ag/nag2607 → nag2607)
    c = re.sub(r'^[A-Za-z0-9]+/', '', c)
    # 去掉上期所 n 前缀 (如 nag2607 → ag2607)
    c = re.sub(r'^[nN]', '', c)
    return c


def _enrich_iv_status(status_list):
    """为 IV 状态列表添加中文名 + 清洗上期所合约 n 前缀。"""
    for item in status_list:
        sym = (item.get("symbol") or "").upper()
        item["name"] = SYMBOL_NAMES.get(sym, item.get("symbol", ""))
        # 上期所主力合约 n 前缀清洗: nag2607 → ag2607
        item["contract"] = _clean_contract_n_prefix(item.get("contract", ""))
    return status_list


def _enrich_options_signals(options_list):
    """清洗期权信号数据的合约 n 前缀 + 添加中文名 + 策略中文名 + 主连标记。"""
    for item in options_list:
        item["contract"] = _clean_contract_n_prefix(item.get("contract", ""))
        sym = (item.get("symbol") or "").upper()
        item["name"] = SYMBOL_NAMES.get(sym, item.get("symbol", ""))

        # 策略英文 → 中文映射
        strat = (item.get("strategy") or "").strip()
        item["strategy_cn"] = STRATEGY_NAMES.get(strat, strat.replace("_", " "))

        # 合约格式：主连合约（纯字母，无数字后缀）加 cont 标记
        cont = item.get("contract", "")
        if cont and not any(ch.isdigit() for ch in cont):
            item["contract"] = cont + " cont"
        else:
            # 移除多余空格
            item["contract"] = " ".join(cont.split())

    return options_list


SECTORS = {
    "有色": ["CU","AL","ZN","PB","NI","SN","AO"],
    "贵金属": ["AU","AG"],
    "黑色": ["RB","HC","I","J","JM","SS","SF","SM"],
    "能源化工": ["BU","FU","LU","SC","RU","NR","BR","TA","MA","FG","SA","UR","PX","EB","EG","PG","PP","V","L","SP","SH"],
    "农产品": ["M","Y","A","B","P","C","CS","JD","LH","CF","SR","AP","CJ","RM","OI"],
    "新能源": ["SI","LC"],
}

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


@app.route("/robots.txt")
def robots_txt():
    """robots.txt — 所有子域公开可抓取。"""
    return """User-agent: *
Allow: /
Sitemap: https://signals.drifter.indevs.in/sitemap.xml
""", 200, {"Content-Type": "text/plain"}


@app.route("/sitemap.xml")
def sitemap_xml():
    """sitemap.xml — 从数据库品种列表自动生成站点地图。

    每次请求查询 `futures_klines` 和 `options_signals` 表的最近更新时间，
    为三个子域（signals / futures / options）生成带最后修改日期的 URL。
    """
    conn = db.get_conn()
    try:
        fx = conn.execute("SELECT MAX(timestamp) FROM futures_klines").fetchone()
        ox = conn.execute(
            "SELECT MAX(created_at) FROM options_signals"
        ).fetchone()
        futures_ts = fx[0] if fx[0] else 0
        options_ts = ox[0] if ox[0] else ""

        def _fmt_date(ts_or_str):
            """将 Unix 时间戳或 ISO 字符串转为 YYYY-MM-DD。"""
            if not ts_or_str or ts_or_str == 0:
                return datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if isinstance(ts_or_str, str):
                try:
                    return datetime.fromisoformat(ts_or_str).strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
            return datetime.fromtimestamp(ts_or_str, tz=timezone.utc).strftime("%Y-%m-%d")

        futures_lastmod = _fmt_date(futures_ts)
        options_lastmod = _fmt_date(options_ts)
        portal_lastmod = max(futures_lastmod, options_lastmod)

        # 品种着陆页 URL 块 — 从 SYMBOL_NAMES 动态生成
        symbol_urls = "\n".join(
            f"""  <url>
    <loc>https://signals.drifter.indevs.in/symbol/{sym}</loc>
    <lastmod>{futures_lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>"""
            for sym in SYMBOL_NAMES
        )

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://signals.drifter.indevs.in/</loc>
    <lastmod>{portal_lastmod}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://signals.drifter.indevs.in/api/docs</loc>
    <lastmod>{portal_lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://futures.drifter.indevs.in/</loc>
    <lastmod>{futures_lastmod}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://options.drifter.indevs.in/</loc>
    <lastmod>{options_lastmod}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
{symbol_urls}
</urlset>"""
        return xml, 200, {
            "Content-Type": "application/xml",
            "Cache-Control": "public, max-age=3600",
        }
    except Exception:
        return (
            '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>',
            200,
            {"Content-Type": "application/xml"},
        )


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
                delayed_warning=delayed_warning)
        elif "options.drifter.indevs.in" in host:
            # 期权独立面板 — 只加载期权/IV 数据
            hub = _get_hub()
            options = _enrich_options_signals([dict(s) for s in hub.get_recent_options(20, delay=is_delayed)])

            iv_recorder = _get_iv_recorder()
            iv_status = _enrich_iv_status(iv_recorder.get_all_status(days=180))

            return render_template("options_dashboard.html",
                now=now, options=options,
                iv_status=iv_status, iv_json=json.dumps(iv_status, ensure_ascii=False),
                delayed_warning=delayed_warning)
        elif "signals.drifter.indevs.in" in host:
            # 信号矩阵门户页 — 期货×期权入口，数据由 JS 实时拉取
            return render_template("portal.html", now=now, delayed_warning=delayed_warning)
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
                delayed_warning=delayed_warning)
    finally:
        pass  # 连接由 Database 管理生命周期


# ─── 公开 API 文档页面 ───────────────────────────────────────────────


@app.route("/pricing")
def pricing_page():
    """定价/订阅页面 — 三档定价卡（免费 / Pro / Premium），Stripe Checkout 集成。"""
    return render_template("pricing.html")


@app.route("/premium/success")
def premium_success_page():
    """支付成功页 — 显示订阅确认信息。"""
    session_id = request.args.get("session_id", "")
    from web.stripe_handler import check_premium_status
    status = check_premium_status(db, session_id=session_id)
    return render_template("pricing.html", payment_success=status.get("premium", False))


@app.route("/subscribe")
def subscribe_page():
    """Bot 订阅着落页 — 引导用户通过 Telegram 订阅信号推送服务。"""
    return render_template("subscribe.html")


@app.route("/api/docs")
def api_docs():
    """公开数据 API v1 文档页面。"""
    return render_template("api_docs.html")


# ── N 型结构动态重算辅助 ───────────────────────────────────────



def _get_futures_contract(conn, symbol: str) -> str:
    """获取品种的合约代码（与矩阵面板同源）。

    优先级（与 /api/matrix 一致）：
      1. futures_signals 最新信号的合约（矩阵主数据源）
      2. futures_n_structures 表最近的合约
      3. futures_klines 表最近的 1d 合约（历史兼容）
    """
    row = conn.execute(
        "SELECT contract FROM futures_signals WHERE symbol=? AND contract!='' ORDER BY created_at DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    if row and row["contract"]:
        return _clean_contract_n_prefix(row["contract"]).upper()
    row = conn.execute(
        "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    if row and row["contract"]:
        return _clean_contract_n_prefix(row["contract"]).upper()
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
        # 0. 延迟判断
        is_delayed = _is_delayed_user()
        delay_sig = _delay_filter("s.created_at")
        delay_n = _delay_filter("updated_at")

        # 最新信号（每个品种取最新一条）
        rows = conn.execute(f'''
            SELECT s.symbol, s.contract, s.direction, s.signal_type,
                   s.level1_pass, s.level2_pass, s.level3_pass, s.score, s.created_at
            FROM futures_signals s
            INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                ON s.symbol=l.symbol AND s.created_at=l.mt
            WHERE 1=1 {delay_sig}
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

        # 构建矩阵
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


@app.route("/api/n-structures")
def api_n_structures():
    """N 型结构信号面板（F.1）—— 所有品种当前 N 型结构展开列表。

    返回按品种分组的结构数据，包含 ABC 价格、方向、状态、建议持有期。
    每次请求先触发动态重算，确保实时性。
    """
    conn = db.get_conn()
    try:
        is_delayed = _is_delayed_user()
        delay_n = _delay_filter("updated_at")
        delay_sig = _delay_filter("s.created_at")
        delay_klines = _delay_filter("timestamp", "int")

        n_rows = conn.execute(f'''
            SELECT symbol, contract, timeframe, direction, state,
                   point_a_price, point_b_price, point_c_price,
                   point_a_time, point_b_time, point_c_time, updated_at
            FROM futures_n_structures
            WHERE state NOT IN ('COMPLETED', 'IDLE') {delay_n}
            ORDER BY symbol, timeframe
        ''').fetchall()

        # 品种最新信号评分（含评分才有显示优先级）
        sig_rows = conn.execute(f'''
            SELECT s.symbol, s.score
            FROM futures_signals s
            INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                ON s.symbol=l.symbol AND s.created_at=l.mt
            WHERE 1=1 {delay_sig}
        ''').fetchall()
        scores = {r["symbol"]: round(r["score"], 2) if r["score"] else 0 for r in sig_rows}

        # 各品种当前价格
        price_rows = conn.execute(f'''
            SELECT symbol, close, timestamp
            FROM futures_klines
            WHERE timeframe='1d' {delay_klines}
              AND (symbol, timestamp) IN (
                  SELECT symbol, MAX(timestamp) FROM futures_klines WHERE timeframe='1d' GROUP BY symbol
              )
        ''').fetchall()
        current_prices = {r["symbol"]: {"close": r["close"], "ts": r["timestamp"]} for r in price_rows}

        # 建议持有期映射
        HOLDING_MAP = {
            "15m": {"label": "短线", "days": "1-3 天"},
            "1h":  {"label": "短中线", "days": "2-5 天"},
            "1d":  {"label": "中线", "days": "5-10 天"},
            "1w":  {"label": "长线", "days": "2-4 周"},
        }
        STATE_LABELS = {
            "LEG1": "第一笔形成中", "LEG2": "第二笔形成中",
            "LEG3": "第三笔形成中", "COMPLETED": "已完成",
            "IDLE": "待激活",
        }

        by_symbol = {}
        for r in n_rows:
            d = dict(r)
            if d.get("timeframe") in ("1d", "1w"):
                _normalize_n_ts(d)
            sym = d["symbol"]
            tf = d["timeframe"]
            name = SYMBOL_NAMES.get(sym, sym)
            if sym not in by_symbol:
                by_symbol[sym] = {
                    "symbol": sym, "name": name,
                    "contract": d["contract"],
                    "score": scores.get(sym, 0),
                    "timeframes": {},
                    "total_signal": 0,
                }
            # 计算 C→最新价的第三笔方向
            cur_price = current_prices.get(sym, {})
            cp = cur_price.get("close")
            c_price = d["point_c_price"]
            leg3_dir = None
            if cp and c_price:
                leg3_dir = "LONG" if cp > c_price else "SHORT" if cp < c_price else "中性"

            # 持有期
            hold = HOLDING_MAP.get(tf, {"label": "—", "days": "—"})

            # 最新 k 线时间（用于判断数据新鲜度）
            last_price_time = cur_price.get("ts")
            updated = d.get("updated_at", "")

            by_symbol[sym]["timeframes"][tf] = {
                "direction": d["direction"],
                "state": d["state"],
                "state_label": STATE_LABELS.get(d["state"], d["state"]),
                "a_price": d["point_a_price"],
                "b_price": d["point_b_price"],
                "c_price": d["point_c_price"],
                "a_time": d["point_a_time"],
                "b_time": d["point_b_time"],
                "c_time": d["point_c_time"],
                "leg3_dir": leg3_dir,
                "hold_label": hold["label"],
                "hold_days": hold["days"],
                "current_price": cp,
                "price_time": last_price_time,
                "updated_at": updated,
            }

        # 总信号数统计
        for sym_data in by_symbol.values():
            sym_data["total_signal"] = sum(
                1 for tf_data in sym_data["timeframes"].values()
                if tf_data["direction"] and tf_data["state"] not in ("COMPLETED", "IDLE")
            )

        # 排序：按评分降序
        structures_list = sorted(by_symbol.values(), key=lambda x: (-x["score"], -x["total_signal"]))

        return jsonify({
            "structures": structures_list,
            "count": len(structures_list),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
    finally:
        pass


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
        # 0. 延迟判断
        is_delayed = _is_delayed_user()
        delay_klines = _delay_filter("k.timestamp", "int")

        contract = _get_futures_contract(conn, sym)
        if contract:
            # 先尝试按合约过滤（bars 与 N-structure 同源），支持最佳对齐
            rows = conn.execute(f'''
                SELECT k.timestamp, k.open, k.high, k.low, k.close, k.volume
                FROM futures_klines k
                INNER JOIN (
                    SELECT symbol, timeframe, timestamp, contract, MAX(rowid) as max_rowid
                    FROM futures_klines
                    WHERE symbol=? AND timeframe=? AND contract=?
                    GROUP BY symbol, timeframe, timestamp, contract
                ) sub ON k.rowid = sub.max_rowid
                WHERE 1=1 {delay_klines}
                ORDER BY k.timestamp DESC
            ''', (sym, tf, contract)).fetchall()
            if not rows:
                # 合约过滤无数据时回退 symbol-only（如旧合约已无 klines 数据）
                rows = conn.execute(f'''
                    SELECT k.timestamp, k.open, k.high, k.low, k.close, k.volume
                    FROM futures_klines k
                    INNER JOIN (
                        SELECT symbol, timeframe, timestamp, MAX(rowid) as max_rowid
                        FROM futures_klines
                        WHERE symbol=? AND timeframe=?
                        GROUP BY symbol, timeframe, timestamp
                    ) sub ON k.rowid = sub.max_rowid
                    WHERE 1=1 {delay_klines}
                    ORDER BY k.timestamp DESC
                ''', (sym, tf)).fetchall()
        else:
            # 无合约时回退到 symbol-only 查询
            rows = conn.execute(f'''
                SELECT k.timestamp, k.open, k.high, k.low, k.close, k.volume
                FROM futures_klines k
                INNER JOIN (
                    SELECT symbol, timeframe, timestamp, MAX(rowid) as max_rowid
                    FROM futures_klines
                    WHERE symbol=? AND timeframe=?
                    GROUP BY symbol, timeframe, timestamp
                ) sub ON k.rowid = sub.max_rowid
                WHERE 1=1 {delay_klines}
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

            # ── 1d/1w 时间戳归一化 ──
            # 将 bar 的时间戳归一化到 05:45 UTC (= 13:45 BJT)，
            # 与 N-structure 时间戳对齐，确保前端几何匹配精准。
            _MIDNIGHT_SEC = 57600  # 16:00 UTC = BJT 午夜
            for bar in bars:
                ts = bar["t"]
                if ts % 86400 == _MIDNIGHT_SEC:
                    bj_midnight_utc = ((ts + _BJ_OFFSET) // 86400) * 86400 - _BJ_OFFSET
                    bar["t"] = bj_midnight_utc + _TARGET_HOUR_SEC
        else:
            bars.reverse()
        
        # 简化为前端用格式
        result = []
        for b in bars[-KLINE_MACD_BARS:]:
            result.append({
                "o": round(b["o"], 2), "c": round(b["c"], 2),
                "h": round(b["h"], 2), "l": round(b["l"], 2),
                "up": b["c"] >= b["o"], "v": b["v"],
                "t": b["t"],  # 时间戳，前端用于检测交易断档
            })
        
        # 1.5. 返回 N 型结构数据（只返回经条件4验证的活跃结构）
        from futures.shared import _get_active_n_structure
        n_struct = _get_active_n_structure(db, sym, contract or "", tf)

        # 1d/1w 周期：归一化 N 结构时间戳到 05:45 UTC，与 bar 时间戳对齐
        if tf in ("1d", "1w") and n_struct:
            _normalize_n_ts(n_struct)

        resp = {
            "symbol": sym, "timeframe": tf,
            "bars": result, "display_count": KLINE_COUNT,
        }
        if n_struct:
            resp["n_structure"] = {
                "dir": n_struct["direction"],
                "state": n_struct["state"],
                "a": n_struct["point_a_price"],
                "b": n_struct["point_b_price"],
                "c": n_struct["point_c_price"],
                "at": n_struct["point_a_time"],
                "bt": n_struct["point_b_time"],
                "ct": n_struct["point_c_time"],
            }

        return jsonify(resp)
    finally:
        pass  # 连接由 Database 管理生命周期


@app.route("/api/stats")
def api_stats():
    """板块统计 + 总体概览。"""
    conn = db.get_conn()
    try:
        is_delayed = _is_delayed_user()
        delay_sig = _delay_filter("s.created_at")
        rows = conn.execute(f'''
            SELECT s.symbol, s.direction, s.signal_type, s.score
            FROM futures_signals s
            INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                ON s.symbol=l.symbol AND s.created_at=l.mt
            WHERE 1=1 {delay_sig}
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
    signals = hub.get_recent_futures(limit, delay=_is_delayed_user())
    return jsonify([dict(s) for s in signals])


@app.route("/api/signals/options")
def api_options_signals():
    """获取最近期权信号列表。"""
    limit = request.args.get("limit", 20, type=int)
    hub = _get_hub()
    signals = hub.get_recent_options(limit, delay=_is_delayed_user())
    return jsonify(_enrich_options_signals([dict(s) for s in signals]))


@app.route("/api/iv/status")
def api_iv_status():
    """获取所有品种当前 IV 状态（百分位+等级）。"""
    iv_recorder = _get_iv_recorder()
    status = _enrich_iv_status(iv_recorder.get_all_status())
    return jsonify(status)


@app.route("/api/summary")
def api_summary():
    """获取看板汇总概览。"""
    is_delayed = _is_delayed_user()
    hub = _get_hub()
    iv_recorder = _get_iv_recorder()
    futures = hub.get_recent_futures(50, delay=is_delayed)
    options = hub.get_recent_options(50, delay=is_delayed)
    iv_status = iv_recorder.get_all_status()
    return jsonify({
        "futures_count": len(futures),
        "options_count": len(options),
        "iv_status": iv_status[:10],
    })


@app.route("/api/filter-stats")
def api_filter_stats():
    """获取 SmartFilter 统计汇总。"""
    is_delayed = _is_delayed_user()
    hub = _get_hub()
    stats = hub.get_filter_stats(delay=is_delayed)
    return jsonify(stats)


@app.route("/api/filter-log")
def api_filter_log():
    """获取最近过滤决策日志。"""
    limit = request.args.get("limit", 20, type=int)
    is_delayed = _is_delayed_user()
    hub = _get_hub()
    log = hub.get_recent_filter_log(limit, delay=is_delayed)
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


# ─── 数据采集 API ─────────────────────────────────────────────


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """触发全品种期货K线数据采集（AKShare）。

    受管理员密码保护，用于 Railway cron job 定期触发。
    采集所有活跃品种的 15m/1h/1d K线数据，完成后自动触发 N 型结构重算。

    注意：全品种采集约需 90~150 秒（60 品种 × 3 周期 × 0.5s 间隔），
    Railway cron 任务超时通常为 60s，因此本端点**不完全同步等待采集完成**。
    - 第一阶段：立即返回 HTTP 202（已接受），
      第二阶段：后台线程继续采集，完成后写入 DB。

    对于非 Railway cron（手动触发），提供 `?sync=true` 参数，
    将同步等待采集完成并返回完整统计。

    POST JSON body:
        password (str): 管理员密码。

    Query params:
        sync (bool): 是否同步等待（默认 false 异步返回）。
        period (str): 周期，可选 '15m' / '1h' / '1d' / 'all'，默认 'all'。

    Returns (同步):
        {"status": "ok", "stats": {...}}
    Returns (异步):
        {"status": "accepted", "message": "采集任务已启动"}
    """
    import threading
    import time as _time

    # 兼容无 Content-Type 的 POST 请求（如 curl 测试）
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        data = {}
    password = data.get("password", request.args.get("password", ""))
    sync = request.args.get("sync", "").lower() in ("true", "1", "yes")

    if password != ADMIN_PASSWORD:
        return jsonify({"error": "密码错误"}), 403

    # 周期选择
    period_arg = request.args.get("period", "all")
    period_map = {"15m": "15", "1h": "60", "1d": "D"}
    if period_arg != "all":
        if period_arg not in period_map:
            return jsonify({"error": f"无效周期: {period_arg}，可选: 15m/1h/1d/all"}), 400
        period_map = {period_arg: period_map[period_arg]}

    def _do_collect() -> dict:
        """执行采集并返回统计。"""
        from data.futures_collector import FuturesCollector
        from config.contracts import ContractRegistry

        start_ts = _time.time()
        registry = ContractRegistry(str(DB_PATH))
        collector = FuturesCollector(db, registry)
        stats = collector.collect_all(
            period_map=period_map,
            trigger_restructure=True,
        )
        elapsed = _time.time() - start_ts

        total_fetched = sum(
            tf_stats.get("fetched", 0)
            for sym_stats in stats.values()
            for tf_stats in sym_stats.values()
        )
        total_saved = sum(
            tf_stats.get("saved", 0)
            for sym_stats in stats.values()
            for tf_stats in sym_stats.values()
        )

        logger.info(
            "数据采集完成: %d 品种, %d 获取, %d 新增保存, 耗时 %.0fs",
            len(stats), total_fetched, total_saved, elapsed,
        )

        return {
            "status": "ok",
            "symbols_collected": len(stats),
            "total_fetched": total_fetched,
            "total_saved": total_saved,
            "elapsed_seconds": round(elapsed, 1),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    if sync:
        # 同步模式：等待采集完成
        try:
            result = _do_collect()
            return jsonify(result)
        except Exception as e:
            logger.error("数据采集异常(同步): %s", e)
            return jsonify({"error": str(e)}), 500
    else:
        # 异步模式：后台线程采集，立即返回 202
        try:
            t = threading.Thread(target=_do_collect, daemon=True)
            t.start()
            return jsonify({
                "status": "accepted",
                "message": "采集任务已启动，后台线程执行中",
                "periods": list(period_map.keys()),
            }), 202
        except Exception as e:
            logger.error("数据采集启动异常: %s", e)
            return jsonify({"error": str(e)}), 500


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


# ─── Premium Content API ───────────────────────────────────────


@app.route("/api/premium/recommendations")
@require_premium
def api_premium_recommendations():
    """Premium: 今日推荐 3 品种（基于 N 型结构共振 + 信号评分）。"""
    conn = db.get_conn()
    try:

        # 所有活跃（非 COMPLETED/IDLE）N型结构
        n_rows = conn.execute('''
            SELECT symbol, timeframe, direction, state,
                   point_a_price, point_b_price, point_c_price
            FROM futures_n_structures
            WHERE state NOT IN ('COMPLETED', 'IDLE')
            ORDER BY symbol, timeframe
        ''').fetchall()

        # 按品种聚合，计算共振
        struct_map = {}
        for r in n_rows:
            d = dict(r)
            sym = d["symbol"]
            if sym not in struct_map:
                struct_map[sym] = {"tfs": {}}
            struct_map[sym]["tfs"][d["timeframe"]] = {
                "dir": d["direction"], "state": d["state"],
                "a": d["point_a_price"], "b": d["point_b_price"], "c": d["point_c_price"],
            }

        # 最新信号评分
        sig_rows = conn.execute('''
            SELECT s.symbol, s.direction, s.score, s.contract
            FROM futures_signals s
            INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                ON s.symbol=l.symbol AND s.created_at=l.mt
        ''').fetchall()
        sig_map = {}
        for r in sig_rows:
            d = dict(r)
            sig_map[d["symbol"]] = d

        # 计算推荐
        TIMEFRAMES = ["15m", "1h", "1d", "1w"]
        candidates = []
        for sym, data in struct_map.items():
            dirs = [data["tfs"][tf]["dir"] for tf in TIMEFRAMES if tf in data["tfs"] and data["tfs"][tf]["dir"]]
            if not dirs:
                continue
            long_count = dirs.count("LONG")
            short_count = dirs.count("SHORT")
            dominant_dir = "LONG" if long_count >= short_count else "SHORT"
            resonance = max(long_count, short_count)
            sig = sig_map.get(sym, {})
            score = round(sig.get("score", 0), 2) if sig else 0

            candidates.append({
                "symbol": sym,
                "name": SYMBOL_NAMES.get(sym, sym),
                "direction": dominant_dir,
                "resonance": resonance,
                "timeframes": resonance,
                "score": score,
                "contract": sig.get("contract", ""),
                "levels": {tf: data["tfs"][tf] for tf in TIMEFRAMES if tf in data["tfs"]},
            })

        # 排序：共振从高到低 → 评分从高到低
        candidates.sort(key=lambda x: (x["resonance"], x["score"]), reverse=True)
        top = candidates[:3]

        return jsonify({
            "recommendations": top,
            "total_candidates": len(candidates),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
    finally:
        pass


@app.route("/api/premium/breakout-alerts")
@require_premium
def api_premium_breakout_alerts():
    """Premium: 距关键位 < 0.5% 的品种突破预警。

    比较最新收盘价与 N 型结构的 A/B/C 点价格，
    若距离任一关键位 < 0.5% 则视为接近突破。
    """
    conn = db.get_conn()
    try:

        # 活跃结构（含已完成的，因为突破可能发生在已形成的结构上）
        n_rows = conn.execute('''
            SELECT symbol, timeframe, direction, state,
                   point_a_price, point_b_price, point_c_price
            FROM futures_n_structures
            ORDER BY symbol, timeframe
        ''').fetchall()

        # 最新收盘价
        close_map = {}
        rows = conn.execute('''
            SELECT symbol, close FROM futures_klines
            WHERE (symbol, timestamp) IN (
                SELECT symbol, MAX(timestamp) FROM futures_klines WHERE timeframe='1d' GROUP BY symbol
            ) AND timeframe='1d'
        ''').fetchall()
        for r in rows:
            close_map[r["symbol"]] = r["close"]

        alerts = []
        seen = set()
        for r in n_rows:
            d = dict(r)
            sym = d["symbol"]
            price = close_map.get(sym)
            if not price or not price > 0:
                continue
            if sym in seen:
                continue
            seen.add(sym)

            # 检查所有点价格
            points = [
                ("A", d["point_a_price"]),
                ("B", d["point_b_price"]),
                ("C", d["point_c_price"]),
            ]
            for label, level_price in points:
                if not level_price or level_price <= 0:
                    continue
                dist_pct = abs(price - level_price) / level_price * 100
                if dist_pct <= 0.5:
                    direction = "LONG" if price > level_price else "SHORT"
                    alerts.append({
                        "symbol": sym,
                        "name": SYMBOL_NAMES.get(sym, sym),
                        "level": f"点{label}",
                        "level_price": round(level_price, 2),
                        "current_price": round(price, 2),
                        "direction": direction,
                        "distance_pct": round(dist_pct, 2),
                        "timeframe": d["timeframe"],
                        "state": d["state"],
                    })

        # 按距离排序（最近优先）
        alerts.sort(key=lambda x: x["distance_pct"])

        return jsonify({
            "alerts": alerts[:10],
            "total": len(alerts),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
    finally:
        pass


@app.route("/api/premium/top-options")
@require_premium
def api_premium_top_options():
    """Premium: 评分最高 2 个期权策略（按 unified_score 降序）。"""
    conn = db.get_conn()
    try:
        rows = conn.execute('''
            SELECT symbol, contract, strategy, unified_score,
                   net_theta, net_delta, iv_level, iv_avg,
                   max_profit, max_loss
            FROM options_signals
            ORDER BY unified_score DESC
            LIMIT 10
        ''').fetchall()

        # 去重：同一品种+策略只取最高分
        seen = set()
        top = []
        for r in rows:
            d = dict(r)
            key = f"{d['symbol']}_{d['strategy']}"
            if key in seen:
                continue
            seen.add(key)
            strat_label = {
                "iron_condor": "铁鹰", "short_strangle": "卖跨",
                "bull_put": "牛沽", "bear_call": "熊购",
                "covered_call": "备兑", "protective_put": "保护沽",
                "ratio_spread": "比例价差",
            }.get(d["strategy"], d["strategy"])
            top.append({
                "symbol": d["symbol"],
                "name": SYMBOL_NAMES.get(d["symbol"], d["symbol"]),
                "contract": d["contract"],
                "strategy": strat_label,
                "score": round(d["unified_score"], 1) if d["unified_score"] else 0,
                "net_theta": round(d["net_theta"], 4) if d["net_theta"] else 0,
                "net_delta": round(d["net_delta"], 4) if d["net_delta"] else 0,
                "iv_level": d["iv_level"] or "",
                "iv_pct": round(d["iv_avg"] * 100, 1) if d["iv_avg"] else 0,
            })
            if len(top) >= 2:
                break

        return jsonify({
            "options": top,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
    finally:
        pass


# ─── Stripe 付费订阅 API ─────────────────────────────────────


@app.route("/api/create-checkout-session", methods=["POST"])
def api_create_checkout_session():
    """创建 Stripe Checkout Session 并返回支付链接。

    POST JSON body:
        email (str): 用户邮箱
        tier (str): "pro" 或 "premium"，默认 "premium"

    Returns:
        {"url": "checkout.stripe.com/..."}
    """
    import os
    from web.stripe_handler import create_checkout_session, ensure_premium_table

    data = request.get_json() or {}
    email = data.get("email", "")
    tier = data.get("tier", "premium")

    if tier not in ("pro", "premium"):
        return jsonify({"error": "无效 tier，可选: pro / premium"}), 400

    ensure_premium_table(db)

    base_url = os.environ.get(
        "SIGNALS_BASE_URL",
        "https://signals.drifter.indevs.in",
    )

    result = create_checkout_session(db, email=email, tier=tier, base_url=base_url)
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@app.route("/api/stripe-webhook", methods=["POST"])
def api_stripe_webhook():
    """处理 Stripe Webhook（支付成功通知）。"""
    from web.stripe_handler import handle_webhook

    payload = request.get_data()
    sig_header = request.headers.get("stripe-signature", "")

    result = handle_webhook(db, payload, sig_header)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/api/customer-portal", methods=["POST"])
def api_customer_portal():
    """创建 Stripe Customer Portal 会话（管理订阅/取消/升级）。

    POST JSON body:
        email (str): 用户邮箱

    Returns:
        {"url": "billing.stripe.com/..."}
    """
    from web.stripe_handler import create_customer_portal_session

    data = request.get_json() or {}
    email = data.get("email", "")
    if not email:
        return jsonify({"error": "缺少 email"}), 400

    import os
    base_url = os.environ.get(
        "SIGNALS_BASE_URL",
        "https://signals.drifter.indevs.in",
    )
    result = create_customer_portal_session(db, email=email, base_url=base_url)
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@app.route("/api/premium/status")
def api_premium_status():
    """查询付费订阅状态。

    Query params:
        session_id (str): Stripe Checkout Session ID。
        email (str): 用户邮箱（备选）。
    """
    from web.stripe_handler import check_premium_status

    session_id = request.args.get("session_id", "")
    email = request.args.get("email", "")

    result = check_premium_status(db, session_id=session_id, email=email)
    return jsonify(result)


@app.route("/api/premium/verify-token", methods=["POST"])
def api_premium_verify_token():
    """验证 Premium Bearer Token 是否有效。

    POST JSON body:
        token (str): Bearer Token。

    Returns:
        {"valid": bool, "premium": bool}
    """
    from web.stripe_handler import verify_token

    data = request.get_json() or {}
    token = data.get("token", "")

    if not token:
        return jsonify({"valid": False, "premium": False, "error": "缺少 token"}), 400

    valid = verify_token(db, token)
    return jsonify({"valid": valid, "premium": valid})


@app.route("/api/premium/token")
def api_premium_token():
    """获取指定 session_id 的 Bearer Token（支付成功后前端存储用）。"""
    from web.stripe_handler import ensure_premium_table

    session_id = request.args.get("session_id", "")
    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    ensure_premium_table(db)
    conn = db.get_conn()
    row = conn.execute(
        "SELECT token FROM premium_subscriptions WHERE session_id=? AND status='active'",
        (session_id,),
    ).fetchone()

    if row and row["token"]:
        return jsonify({"token": row["token"]})
    return jsonify({"token": None}), 404


# ─── 分析追踪（轻量自建）───────────────────────────────────────


def _transparent_gif() -> bytes:
    """返回 1x1 透明 GIF 像素数据。"""
    return (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
        b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00'
        b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
        b'\x44\x01\x00\x3b'
    )


@app.route("/api/track.gif")
def api_track():
    """Tracking pixel — 1x1 透明 GIF，记录页面访问。

    查询参数:
        url: 当前页面路径 (默认 referrer)
        ref: 来源页面 (默认 "")
    返回 1x1 透明 GIF，不缓存。
    """
    url = request.args.get("url", request.referrer or "/")
    ref = request.args.get("ref", request.referrer or "")
    ua = request.user_agent.string if request.user_agent else ""
    ip = request.remote_addr or ""

    # 简单指纹：IP + UA → session_id（不精确但够用）
    fp = hashlib.md5(f"{ip}|{ua}".encode()).hexdigest()[:16]

    try:
        conn = db.get_conn()
        conn.execute(
            "INSERT INTO page_hits (url, referrer, user_agent, ip, session_id, visited_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (url, ref, ua, ip, fp, int(datetime.now().timestamp())),
        )
        conn.commit()
    except Exception as exc:
        logger.warning("track.gif error: %s", exc)

    return _transparent_gif(), 200, {
        "Content-Type": "image/gif",
        "Cache-Control": "no-store, no-cache, must-revalidate",
    }


@app.route("/api/stats/visits")
def api_stats_visits():
    """访问统计 JSON — 回答：有人来吗？从哪来？看了什么？"""
    conn = db.get_conn()
    now_ts = int(datetime.now().timestamp())
    today_start = now_ts - (now_ts % 86400)  # 当天 00:00 UTC
    week_ago = now_ts - 7 * 86400

    total = conn.execute("SELECT COUNT(*) FROM page_hits").fetchone()[0]
    unique = conn.execute(
        "SELECT COUNT(DISTINCT session_id) FROM page_hits"
    ).fetchone()[0]
    today = conn.execute(
        "SELECT COUNT(*) FROM page_hits WHERE visited_at >= ?", (today_start,)
    ).fetchone()[0]

    top_pages = conn.execute("""
        SELECT url, COUNT(*) as cnt FROM page_hits
        GROUP BY url ORDER BY cnt DESC LIMIT 10
    """).fetchall()

    top_refs = conn.execute("""
        SELECT referrer, COUNT(*) as cnt FROM page_hits
        WHERE referrer != '' GROUP BY referrer ORDER BY cnt DESC LIMIT 10
    """).fetchall()

    daily = conn.execute("""
        SELECT date(visited_at, 'unixepoch') as day, COUNT(*) as cnt
        FROM page_hits WHERE visited_at >= ?
        GROUP BY day ORDER BY day DESC LIMIT 30
    """, (week_ago,)).fetchall()

    return jsonify({
        "total": total,
        "unique": unique,
        "today": today,
        "top_pages": [dict(r) for r in top_pages],
        "top_refs": [dict(r) for r in top_refs],
        "daily": [dict(r) for r in daily],
    })


@app.route("/analytics")
def analytics_page():
    """简易分析面板页面。"""
    return render_template("analytics.html")


# ─── Admin 管理面板 API ────────────────────────────────────────


@app.route("/admin")
def admin_panel():
    """管理面板页面（密码保护，用于手动生成 Pro Token）。"""
    return render_template("admin_panel.html")


@app.route("/api/admin/verify-password", methods=["POST"])
def api_admin_verify_password():
    """验证管理员密码。"""
    data = request.get_json() or {}
    password = data.get("password", "")
    if password == ADMIN_PASSWORD:
        return jsonify({"ok": True})
    return jsonify({"ok": False})


@app.route("/api/admin/generate-token", methods=["POST"])
def api_admin_generate_token():
    """管理员手动生成 Pro Token 并写入数据库。

    POST JSON body:
        password (str): 管理员密码
        email (str): 用户邮箱

    Returns:
        {"token": "...", "email": "..."}
    """
    from web.stripe_handler import _generate_token, ensure_premium_table

    data = request.get_json() or {}
    password = data.get("password", "")
    email = data.get("email", "")

    if password != ADMIN_PASSWORD:
        return jsonify({"error": "密码错误"}), 403

    if not email:
        return jsonify({"error": "缺少 email"}), 400

    token = _generate_token()
    ensure_premium_table(db)

    conn = db.get_conn()
    try:
        conn.execute(
            """INSERT INTO premium_subscriptions
               (session_id, customer_id, email, status, token)
               VALUES (?, ?, ?, ?, ?)""",
            (f"manual_{int(__import__('time').time())}", "manual", email, "active", token),
        )
        conn.commit()
        logger.info("管理员手动生成 Token: token=%s email=%s", token[:8] + "...", email)
        return jsonify({"token": token, "email": email})
    except Exception as e:
        conn.rollback()
        logger.error("生成 Token 失败: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/list-subscriptions")
def api_admin_list_subscriptions():
    """列出所有 premium_subscriptions 记录（需密码验证）。"""
    password = request.args.get("password", "")

    if password != ADMIN_PASSWORD:
        return jsonify({"error": "密码错误"}), 403

    from web.stripe_handler import ensure_premium_table
    ensure_premium_table(db)

    conn = db.get_conn()
    rows = conn.execute(
        "SELECT id, session_id, email, status, created_at, expires_at FROM premium_subscriptions ORDER BY id DESC"
    ).fetchall()

    return jsonify([dict(r) for r in rows])


# ─── 用户注册 API ────────────────────────────────────────────────

# 登录限流：{ip: [timestamp, ...]}
_login_rate_limit: dict[str, list[float]] = {}
import time as _time_mod


def _check_login_rate_limit() -> bool:
    """检查同一 IP 5 分钟内失败次数是否超过 5 次。

    Returns:
        True 允许继续，False 触发限流。
    """
    ip = request.remote_addr or "unknown"
    now = _time_mod.time()
    records = [t for t in _login_rate_limit.get(ip, []) if now - t < 300]
    if len(records) >= 5:
        return False  # 限流
    records.append(now)
    _login_rate_limit[ip] = records
    return True


def _generate_session_token() -> str:
    """生成 URL-safe session token（48 bytes → 64 chars base64）。

    使用 secrets.token_urlsafe（CSPRNG），碰撞概率 < 2^-256。
    """
    import secrets
    return secrets.token_urlsafe(48)


def _ensure_session_table() -> None:
    """确保 user_sessions 表存在。"""
    conn = db.get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            token      TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
            expires_at TEXT NOT NULL,
            last_used_at TEXT,
            is_active  INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES user_registrations(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_sessions_token
        ON user_sessions(token)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id
        ON user_sessions(user_id)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_sessions_expires
        ON user_sessions(expires_at)
    """)


def _is_registered_user() -> bool:
    """检查当前请求是否来自已登录用户。

    Token 来源（按优先级）：
    1. Authorization: Bearer <token> Header
    2. token URL query parameter

    Returns:
        True 如果 token 有效且未过期。
    """
    token = ""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
    if not token:
        token = request.args.get("token", "")
    if not token:
        return False

    conn = db.get_conn()
    row = conn.execute(
        """SELECT id FROM user_sessions
           WHERE token = ? AND is_active = 1 AND expires_at > datetime('now', '+8 hours')""",
        (token,),
    ).fetchone()

    if row:
        # 静默更新 last_used_at
        conn.execute(
            "UPDATE user_sessions SET last_used_at = datetime('now', '+8 hours') WHERE id = ?",
            (row["id"],),
        )
        conn.commit()
        return True

    return False


def _is_delayed_user() -> bool:
    """返回 True 表示当前用户是免费层，需要数据延迟。"""
    return not _is_registered_user()


def _delay_filter(field: str, field_type: str = "text", minutes: int = 15) -> str:
    """生成 SQL 延迟过滤条件。

    Args:
        field: 时间戳字段名。
        field_type: 'text' (ISO datetime) 或 'int' (Unix timestamp)。
        minutes: 延迟分钟数，默认 15。

    Returns:
        SQL 片段，如 "AND created_at <= datetime('now', '-15 minutes')"。
        空串表示不延迟。
    """
    if not _is_delayed_user():
        return ""
    if field_type == "int":
        return f"AND {field} <= strftime('%s', 'now') - {minutes * 60}"
    return f"AND {field} <= datetime('now', '-{minutes} minutes')"


def _render_delayed_warning() -> str:
    """为模板渲染生成延迟提示文案（空串 = 不显示）。"""
    if _is_delayed_user():
        return "⏱️ 免费用户数据延迟约 15 分钟 · 注册/登录可查看实时数据"
    return ""


def _ensure_user_table() -> None:
    """确保 user_registrations 表存在。"""
    conn = db.get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
            last_login TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_registrations_email
        ON user_registrations(email)
    """)


@app.route("/api/auth/register", methods=["POST"])
def api_auth_register():
    """邮箱+密码注册。

    POST JSON body:
        email (str): 用户邮箱
        password (str): 密码（最少 6 位）

    Returns:
        {"ok": true, "email": "..."} 或 {"error": "..."}
    """
    _ensure_user_table()
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # ── 基本校验 ──
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "请输入有效的邮箱地址"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码至少需要 6 个字符"}), 400

    # ── 检查重复 ──
    conn = db.get_conn()
    existing = conn.execute(
        "SELECT id FROM user_registrations WHERE email = ?", (email,)
    ).fetchone()
    if existing:
        return jsonify({"error": "该邮箱已注册"}), 409

    # ── bcrypt 哈希 ──
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # ── 写入数据库 ──
    try:
        conn.execute(
            "INSERT INTO user_registrations (email, password_hash) VALUES (?, ?)",
            (email, pw_hash),
        )
        conn.commit()
        logger.info("新用户注册成功: email=%s", email)
        return jsonify({"ok": True, "email": email}), 201
    except Exception as e:
        conn.rollback()
        logger.error("注册失败: email=%s error=%s", email, e)
        return jsonify({"error": "注册失败，请稍后重试"}), 500


# ─── 用户登录 API ────────────────────────────────────────────────


@app.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    """邮箱+密码登录，返回 session token（30 天有效）。

    POST JSON body:
        email (str): 用户邮箱
        password (str): 密码

    Returns:
        {"ok": true, "token": "...", "email": "...", "expires_at": "..."} 或 {"error": "..."}
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # 基本校验
    if not email or not password:
        return jsonify({"error": "请提供邮箱和密码"}), 400

    # 限流检查
    if not _check_login_rate_limit():
        logger.warning("登录限流触发: ip=%s email=%s", request.remote_addr, email)
        return jsonify({"error": "登录尝试过于频繁，请稍后再试"}), 429

    conn = db.get_conn()

    # 查找用户
    user = conn.execute(
        "SELECT id, password_hash FROM user_registrations WHERE email = ?",
        (email,),
    ).fetchone()

    # 统一返回"邮箱或密码错误"（防止用户枚举）
    if not user:
        return jsonify({"error": "邮箱或密码错误"}), 401

    # bcrypt 验证
    try:
        if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            return jsonify({"error": "邮箱或密码错误"}), 401
    except Exception:
        return jsonify({"error": "邮箱或密码错误"}), 401

    # 确保 session 表存在
    _ensure_session_table()

    # 清理该用户的过期 session
    conn.execute(
        "UPDATE user_sessions SET is_active = 0 WHERE user_id = ? AND expires_at < datetime('now', '+8 hours')",
        (user["id"],),
    )
    conn.commit()

    # 生成新 token（30 天有效）
    token = _generate_session_token()
    expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M")

    conn.execute(
        """INSERT INTO user_sessions (user_id, token, expires_at, last_used_at)
           VALUES (?, ?, ?, datetime('now', '+8 hours'))""",
        (user["id"], token, expires_at),
    )
    conn.commit()

    # 更新 last_login
    conn.execute(
        "UPDATE user_registrations SET last_login = datetime('now', '+8 hours') WHERE id = ?",
        (user["id"],),
    )
    conn.commit()

    logger.info("用户登录成功: email=%s", email)
    return jsonify({
        "ok": True,
        "token": token,
        "email": email,
        "expires_at": expires_at,
    })


@app.route("/api/auth/verify", methods=["POST"])
def api_auth_verify():
    """验证 auth token 是否有效。

    前端每个页面加载时调用，用于判断是否显示延迟数据。
    返回 200 + JSON，不返回 401（简化前端错误处理）。

    POST JSON body:
        token (str): 存储的 auth token。

    Returns:
        {"valid": true, "email": "..."} 或 {"valid": false}。
    """
    data = request.get_json() or {}
    token = data.get("token", "")
    if not token:
        return jsonify({"valid": False})

    conn = db.get_conn()
    row = conn.execute(
        """SELECT u.email FROM user_sessions s
           JOIN user_registrations u ON s.user_id = u.id
           WHERE s.token = ? AND s.is_active = 1 AND s.expires_at > datetime('now', '+8 hours')""",
        (token,),
    ).fetchone()

    if row:
        # 静默更新 last_used_at
        conn.execute(
            "UPDATE user_sessions SET last_used_at = datetime('now', '+8 hours') WHERE token = ?",
            (token,),
        )
        conn.commit()
        return jsonify({"valid": True, "email": row["email"]})

    return jsonify({"valid": False})


# ─── 定价/订阅用户状态 API ────────────────────────────────────────


@app.route("/api/pricing/user-status")
def api_pricing_user_status():
    """查询当前用户的定价/订阅状态。

    Uses Authorization: Bearer <token> header (same as dashboard auth).

    Returns:
        {"logged_in": bool, "email": str, "plan": str,
         "trial_days_remaining": int, "registered_at": str,
         "premium": {"active": bool, "status": str, ...} or null}
    """
    token = ""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
    if not token:
        token = request.args.get("token", "")

    # 未登录
    if not token:
        return jsonify({
            "logged_in": False,
            "plan": "free",
            "trial_days_remaining": 0,
            "premium": None,
        })

    conn = db.get_conn()
    row = conn.execute(
        """SELECT u.email, u.created_at FROM user_sessions s
           JOIN user_registrations u ON s.user_id = u.id
           WHERE s.token = ? AND s.is_active = 1 AND s.expires_at > datetime('now', '+8 hours')""",
        (token,),
    ).fetchone()

    if not row:
        return jsonify({
            "logged_in": False,
            "plan": "free",
            "trial_days_remaining": 0,
            "premium": None,
        })

    email = row["email"]
    registered_at = row["created_at"] or ""

    # 计算剩余试用天数（注册日起 7 天）
    trial_days = 0
    if registered_at:
        try:
            reg_dt = datetime.strptime(registered_at, "%Y-%m-%d %H:%M")
            now_bj = datetime.now()
            elapsed = (now_bj - reg_dt).days
            trial_days = max(0, 7 - elapsed)
        except (ValueError, TypeError):
            trial_days = 0

    # 查询 Premium 订阅状态（按 email 匹配）
    premium = None
    try:
        p_row = conn.execute(
            """SELECT status, created_at, session_id, subscription_id, customer_id, tier
               FROM premium_subscriptions WHERE email = ? AND status = 'active'
               ORDER BY id DESC LIMIT 1""",
            (email,),
        ).fetchone()
        if p_row:
            premium = {
                "active": True,
                "status": p_row["status"],
                "created_at": p_row["created_at"],
                "session_id": p_row["session_id"],
                "tier": p_row.get("tier", "premium"),
            }
    except Exception:
        pass

    # 根据实际 tier 返回计划名称
    if premium:
        plan = premium.get("tier", "premium")
    else:
        plan = "free"

    return jsonify({
        "logged_in": True,
        "email": email,
        "plan": plan,
        "trial_days_remaining": trial_days,
        "registered_at": registered_at,
        "premium": premium,
    })


# ─── Bot 订阅管理 API ──────────────────────────────────────────


def _require_api_key(f):
    """API Key 认证装饰器（查 api_keys 表）。"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
        if not api_key:
            return jsonify({"ok": False, "error": "缺少 API Key，请在 X-API-Key Header 中传入"}), 401
        conn = db.get_conn()
        try:
            row = conn.execute(
                "SELECT id, tier FROM api_keys WHERE api_key=? AND is_active=1",
                (api_key,),
            ).fetchone()
            if not row:
                return jsonify({"ok": False, "error": "API Key 无效或已停用"}), 401
            conn.execute("UPDATE api_keys SET last_used=datetime('now') WHERE id=?", (row["id"],))
            conn.commit()
        except Exception:
            return jsonify({"ok": False, "error": "认证服务异常"}), 500
        return f(*args, **kwargs)
    return decorated


@app.route("/api/subscribe", methods=["POST"])
@_require_api_key
def api_subscribe():
    """Bot 订阅 — 注册 Telegram 推送订阅。

    POST JSON body:
        telegram_chat_id (str, required): Telegram 用户的 Chat ID。
        username (str, optional): Telegram 用户名。
        first_name (str, optional): Telegram 显示名。
        preferences (dict, optional): 推送偏好。

    Returns:
        {"ok": true, "status": "trial", "trial_end": "..."} 或 {"ok": false, "error": "..."}
    """
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "请求体为空"}), 400

    chat_id = data.get("telegram_chat_id", "").strip()
    if not chat_id:
        return jsonify({"ok": False, "error": "缺少 telegram_chat_id"}), 400

    from signals.bot_subscription import BotSubscription
    mgr = BotSubscription(db)

    success = mgr.subscribe(
        chat_id=chat_id,
        username=data.get("username", ""),
        first_name=data.get("first_name", ""),
        preferences=data.get("preferences"),
    )
    if not success:
        return jsonify({"ok": False, "error": "订阅失败，请稍后重试"}), 500

    # 返回订阅后状态
    sub = mgr.get_subscriber(chat_id)
    return jsonify({
        "ok": True,
        "data": {
            "telegram_chat_id": chat_id,
            "status": sub.get("status", "trial") if sub else "trial",
            "trial_end": sub.get("trial_end_at", "") if sub else "",
            "subscribed_at": sub.get("subscribed_at", "") if sub else "",
        },
    })


@app.route("/api/unsubscribe", methods=["POST"])
@_require_api_key
def api_unsubscribe():
    """Bot 取消订阅。

    POST JSON body:
        telegram_chat_id (str, required): 要取消的 Telegram Chat ID。

    Returns:
        {"ok": true, "message": "已取消订阅"} 或 {"ok": false, "error": "..."}
    """
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "请求体为空"}), 400

    chat_id = data.get("telegram_chat_id", "").strip()
    if not chat_id:
        return jsonify({"ok": False, "error": "缺少 telegram_chat_id"}), 400

    from signals.bot_subscription import BotSubscription
    mgr = BotSubscription(db)

    mgr.unsubscribe(chat_id)
    return jsonify({"ok": True, "message": "已取消订阅"})


@app.route("/api/subscribe/status")
@_require_api_key
def api_subscribe_status():
    """查询 Bot 订阅状态。

    Query params:
        chat_id (str): Telegram Chat ID。

    Returns:
        {"ok": true, "data": {...}} 或 {"ok": false, "error": "..."}
    """
    chat_id = request.args.get("chat_id", "").strip()
    if not chat_id:
        return jsonify({"ok": False, "error": "缺少 chat_id 参数"}), 400

    from signals.bot_subscription import BotSubscription
    mgr = BotSubscription(db)
    sub = mgr.get_subscriber(chat_id)

    if not sub:
        return jsonify({
            "ok": True,
            "data": {
                "telegram_chat_id": chat_id,
                "status": "not_found",
                "is_subscribed": False,
            },
        })

    return jsonify({
        "ok": True,
        "data": {
            "telegram_chat_id": sub["telegram_chat_id"],
            "telegram_username": sub.get("telegram_username", ""),
            "first_name": sub.get("first_name", ""),
            "status": sub["status"],
            "is_subscribed": sub["status"] in ("trial", "active"),
            "subscribed_at": sub.get("subscribed_at", ""),
            "trial_end_at": sub.get("trial_end_at", ""),
            "expires_at": sub.get("expires_at", ""),
            "signals_pushed": sub.get("signals_pushed", 0),
            "preferences": sub.get("preferences", "{}"),
        },
    })


# ─── 免费试用 API ────────────────────────────────────────────────


@app.route("/api/public/request-trial", methods=["POST"])
def api_request_trial():
    """公开发送的 API：生成 7 天免费试用 Token（无需人工介入）。

    POST JSON body:
        email (str, optional): 用户邮箱。

    Returns:
        {"token": "...", "days": 7, "expires_at": "..."} 或 {"error": "..."}
    """
    from web.stripe_handler import _generate_token, ensure_premium_table
    import time

    data = request.get_json() or {}
    email = data.get("email", "").strip()

    token = _generate_token()
    ensure_premium_table(db)

    expires_at = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")

    conn = db.get_conn()
    try:
        conn.execute(
            """INSERT INTO premium_subscriptions
               (session_id, customer_id, email, status, token, expires_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (f"trial_{int(time.time())}", "trial", email or "trial@autocompany.ai",
             "active", token, expires_at),
        )
        conn.commit()
        logger.info("免费试用 Token 已生成: token=%s email=%s", token[:8] + "...", email or "(空)")
        return jsonify({"token": token, "days": 7, "expires_at": expires_at})
    except Exception as e:
        conn.rollback()
        logger.error("生成试用 Token 失败: %s", e)
        return jsonify({"error": str(e)}), 500


# ─── 品种级 SEO 着陆页 ──────────────────────────────────────


@app.route("/symbol/<symbol>")
def symbol_page(symbol: str):
    """品种独立着陆页 — 显示指定品种的实时信号、N 型结构、期权 IV 状态。

    用于 SEO 搜索引擎索引，每个主力品种一个独立页面。
    """
    sym = symbol.upper()
    conn = db.get_conn()
    try:
        # 1. 验证品种是否存在
        name = SYMBOL_NAMES.get(sym)
        if not name:
            return render_template("symbol_page.html",
                exists=False, symbol=sym, name=sym), 404

        # 2. 查找所属板块
        sector_name = None
        sector_symbols = []
        for sn, symbols in SECTORS.items():
            if sym in symbols:
                sector_name = sn
                sector_symbols = [s for s in symbols if s != sym]
                break

        # 3. 最新信号
        sig_row = conn.execute(
            """SELECT contract, direction, signal_type, score,
                      level1_pass, level2_pass, level3_pass, created_at
               FROM futures_signals
               WHERE symbol=? ORDER BY created_at DESC LIMIT 1""",
            (sym,),
        ).fetchone()
        signal = dict(sig_row) if sig_row else None
        if signal:
            signal["score"] = round(signal["score"], 2) if signal["score"] else 0
            signal["l1"] = bool(signal["level1_pass"])
            signal["l2"] = bool(signal["level2_pass"])
            signal["l3"] = bool(signal["level3_pass"])

        # 4. N 型结构（所有 4 周期）
        n_rows = conn.execute("""
            SELECT timeframe, direction, state,
                   point_a_price, point_b_price, point_c_price,
                   point_a_time, point_b_time, point_c_time, updated_at
            FROM futures_n_structures
            WHERE symbol=? AND state NOT IN ('COMPLETED', 'IDLE')
            ORDER BY timeframe
        """, (sym,)).fetchall()
        n_structures = []
        for r in n_rows:
            d = dict(r)
            if d.get("timeframe") in ("1d", "1w"):
                _normalize_n_ts(d)
            n_structures.append(d)

        # 5. 当前价格（日线最新一条）
        price_row = conn.execute(
            """SELECT close, timestamp
               FROM futures_klines
               WHERE symbol=? AND timeframe='1d'
               ORDER BY timestamp DESC LIMIT 1""",
            (sym,),
        ).fetchone()
        current_price = round(price_row["close"], 2) if price_row else None
        price_time = price_row["timestamp"] if price_row else None
        price_time_str = datetime.fromtimestamp(price_time).strftime("%m/%d %H:%M") if price_time else ""

        # 6. 期权 IV 状态
        iv_status = None
        iv_row = conn.execute(
            """SELECT symbol, avg_iv, atm_call_iv, atm_put_iv, top5_avg_iv, date
               FROM iv_history
               WHERE symbol=? ORDER BY date DESC LIMIT 1""",
            (sym,),
        ).fetchone()
        if iv_row:
            iv_status = dict(iv_row)
            # IV 数据库存小数（0.318），转百分比展示
            for k in ("avg_iv", "atm_call_iv", "atm_put_iv", "top5_avg_iv"):
                if iv_status.get(k) is not None:
                    iv_status[k] = round(iv_status[k] * 100, 1)

        # 6b. 期权信号评分
        opt_row = conn.execute(
            """SELECT unified_score, strategy, signal_type, created_at
               FROM options_signals
               WHERE symbol=? ORDER BY created_at DESC LIMIT 1""",
            (sym,),
        ).fetchone()
        opt_signal = dict(opt_row) if opt_row else None
        # 映射 signal_type → CSS 风格类名
        if opt_signal:
            dir_map = {"BUY": "BULLISH", "SELL": "BEARISH"}
            opt_signal["dir_class"] = dir_map.get(opt_signal.get("signal_type", ""), "NEUTRAL")

        # 7. 同板块品种列表（含简要信号方向）
        related = []
        for rsym in sector_symbols or []:
            rrow = conn.execute(
                """SELECT direction, score
                   FROM futures_signals
                   WHERE symbol=? ORDER BY created_at DESC LIMIT 1""",
                (rsym,),
            ).fetchone()
            related.append({
                "symbol": rsym,
                "name": SYMBOL_NAMES.get(rsym, rsym),
                "direction": rrow["direction"] if rrow else None,
                "score": round(rrow["score"], 2) if rrow and rrow["score"] else 0,
            })

        # 8. 构建 SEO 描述
        dir_label = {"LONG": "偏多↑", "SHORT": "偏空↓", "NEUTRAL": "中性"}
        sig_summary = ""
        if signal:
            label = dir_label.get(signal["direction"], signal["direction"])
            sig_summary = f"信号{label}，评分{signal['score']}。"
        n_summary = ""
        for ns in n_structures:
            label = dir_label.get(ns["direction"], ns["direction"])
            tf_label = {"15m": "15分钟", "1h": "1小时", "1d": "日线", "1w": "周线"}
            n_summary += f"{tf_label.get(ns['timeframe'], ns['timeframe'])}周期{label}（{ns['state']}）；"

        seo_desc = f"{name}（{sym}）期货期权实时信号 — {sig_summary} 多周期N型结构：{n_summary} 数据由信号矩阵自动生成。"
        seo_title = f"{name}（{sym}）实时期货信号 — N型结构多周期分析 | 信号矩阵"

        return render_template("symbol_page.html",
            exists=True,
            symbol=sym, name=name, sector=sector_name,
            signal=signal, n_structures=n_structures,
            current_price=current_price, price_time_str=price_time_str,
            iv_status=iv_status, opt_signal=opt_signal,
            related=related, seo_title=seo_title, seo_desc=seo_desc,
        )
    finally:
        pass


# 确保 session 表在应用启动时存在（在 gunicorn import 时执行）
_ensure_session_table()

# ─── 后台数据采集调度器 ─────────────────────────────
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5100))
    app.run(host="0.0.0.0", port=port, debug=False)

