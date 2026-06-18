"""
StatusHub 公开数据 API — v1 Blueprint。

为开发者提供程序化访问期货信号、N 型结构热力图、期权 IV 等数据的端点。
与内部 API 完全隔离（独立 Blueprint），公开 API 的失败不影响内部看板。

架构原则:
  - 所有端点统一返回 {data, meta} 或 {error}
  - 认证通过 X-API-Key Header
  - 速率限制通过内存滑动窗口（零外部依赖）
  - CORS 开放 v1 端点
  - 端点级 TTL 缓存（30s/300s）

端点:
  - GET /api/v1/market/heatmap   — 市场信号热力图（✅ 已实现）
  - GET /api/v1/signals/top      — 评分最高信号排行（✅ 已实现）
  - GET /api/v1/options/iv-summary — 期权 IV 状态快照（✅ 已实现）
"""

import logging
import time
import secrets
from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, jsonify, request, current_app

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 统一错误处理
# ---------------------------------------------------------------------------


class PublicAPIError(Exception):
    """公开 API 统一异常类。

    Attributes:
        code: 机器可读错误码 (UNAUTHORIZED, RATE_LIMITED, ...)
        message: 人类可读错误描述（中文）
        status_code: HTTP 状态码
        details: 可选附加信息
    """

    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

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

SECTORS = {
    "有色": ["CU","AL","ZN","PB","NI","SN","AO"],
    "贵金属": ["AU","AG"],
    "黑色": ["RB","HC","I","J","JM","SS","SF","SM"],
    "能源化工": ["BU","FU","LU","SC","RU","NR","BR","TA","MA","FG","SA","UR","PX","EB","EG","PG","PP","V","L","SP","SH"],
    "农产品": ["M","Y","A","B","P","C","CS","JD","LH","CF","SR","AP","CJ","RM","OI"],
    "新能源": ["SI","LC"],
}

TIMEFRAMES = ["15m", "1h", "1d", "1w"]

# 速率限制配置: {端点路径: (max_requests, window_seconds)}
RATE_LIMITS: dict[str, tuple[int, int]] = {
    "/api/v1/market/heatmap": (10, 60),
    "/api/v1/signals/top": (30, 60),
    "/api/v1/options/iv-summary": (30, 60),
}


def _utc_now_iso() -> str:
    """返回当前 UTC 时间的 ISO 8601 格式。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# 参数校验
# ---------------------------------------------------------------------------


def _validate_limit(limit: int, max_limit: int = 100) -> tuple[int | None, dict | None]:
    if limit < 1 or limit > max_limit:
        return None, {"code": "INVALID_PARAMS", "message": f"limit 必须在 1-{max_limit} 之间"}
    return limit, None


def _validate_direction(direction: str | None) -> tuple[str | None, dict | None]:
    if direction and direction not in ("LONG", "SHORT"):
        return None, {"code": "INVALID_PARAMS", "message": "direction 必须为 LONG 或 SHORT"}
    return direction, None


def _validate_sector(sector: str | None) -> tuple[str | None, dict | None]:
    if sector and sector not in SECTORS:
        return None, {"code": "INVALID_PARAMS", "message": f"无效的板块 '{sector}'，可选: {', '.join(SECTORS)}"}
    return sector, None


# ---------------------------------------------------------------------------
# 速率限制（内存滑动窗口）
# ---------------------------------------------------------------------------

_rate_limit_store: dict[str, list[float]] = {}  # key -> [timestamp, ...]


def _rate_limit_check(endpoint_path: str, key: str = "default") -> dict | None:
    """检查给定 endpoint + key 是否超限。

    使用内存滑动窗口实现，零外部依赖。

    Args:
        endpoint_path: API 端点路径，如 "/api/v1/market/heatmap"
        key: 限流键（API Key 或 IP）

    Returns:
        None（未超限）或错误 dict（超限时）
    """
    limits = RATE_LIMITS.get(endpoint_path)
    if not limits:
        return None  # 无限制

    max_req, window_sec = limits
    store_key = f"{endpoint_path}:{key}"
    now = time.time()
    cutoff = now - window_sec

    # 获取并清理过期记录
    records = _rate_limit_store.get(store_key, [])
    records = [t for t in records if t > cutoff]
    records.append(now)
    _rate_limit_store[store_key] = records

    # 限制存储大小（防止内存泄漏）
    if len(_rate_limit_store) > 10000:
        _clean_rate_limit_store()

    if len(records) > max_req:
        retry_after = int(window_sec - (now - records[0]))
        return {
            "code": "RATE_LIMITED",
            "message": f"速率超限，请 {retry_after} 秒后重试",
            "retry_after_seconds": max(retry_after, 1),
        }
    return None


def _clean_rate_limit_store():
    """清理过期和超量限流记录（防内存泄漏）。"""
    now = time.time()
    stale_keys = []
    for store_key, records in list(_rate_limit_store.items()):
        # 清除过期记录
        fresh = [t for t in records if t > now - 120]
        if fresh:
            _rate_limit_store[store_key] = fresh
        else:
            stale_keys.append(store_key)
    for k in stale_keys:
        _rate_limit_store.pop(k, None)


# ---------------------------------------------------------------------------
# 缓存层
# ---------------------------------------------------------------------------

_cache: dict[str, dict] = {}
_CACHE_MAX_ENTRIES = 1000


def _cache_set(key: str, data, ttl_seconds: int = 30):
    if len(_cache) >= _CACHE_MAX_ENTRIES:
        sorted_keys = sorted(_cache.keys(), key=lambda k: _cache[k]["ts"])
        for old_key in sorted_keys[:200]:
            _cache.pop(old_key, None)
    _cache[key] = {"data": data, "ts": time.time(), "ttl": ttl_seconds}


def _cache_get(key: str):
    entry = _cache.get(key)
    if entry is None:
        return None
    if time.time() - entry["ts"] > entry["ttl"]:
        _cache.pop(key, None)
        return None
    return entry["data"]


def cached(ttl_seconds: int = 30):
    """端点级缓存装饰器（惰性过期，限成功响应）。"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"v1:{func.__name__}:{hash(frozenset(request.args.items()))}"
            cached_data = _cache_get(key)
            if cached_data is not None:
                return cached_data
            result = func(*args, **kwargs)
            # 只有成功响应才缓存
            if isinstance(result, tuple) and len(result) >= 2:
                resp, status_code = result[0], result[1]
                if status_code == 200:
                    _cache_set(key, result, ttl_seconds)
            else:
                _cache_set(key, result, ttl_seconds)
            return result
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# API Key 认证
# ---------------------------------------------------------------------------


def _get_db():
    return current_app.config.get("DB_INSTANCE")


def _get_api_key_from_header() -> str | None:
    return request.headers.get("X-API-Key") or request.headers.get("x-api-key")


def _validate_api_key(api_key: str, db) -> dict | None:
    """校验 API Key，返回 key_info 或 None。"""
    if not db:
        return None
    conn = db.get_conn()
    try:
        row = conn.execute(
            "SELECT id, api_key, tier, is_active FROM api_keys WHERE api_key=?",
            (api_key,),
        ).fetchone()
        if not row or not row["is_active"]:
            return None
        conn.execute("UPDATE api_keys SET last_used=datetime('now') WHERE id=?", (row["id"],))
        conn.commit()
        return {"key_id": row["id"], "tier": row["tier"]}
    except Exception:
        return None


def require_api_key(f):
    """API Key 认证 + 速率限制装饰器。"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # ── 认证 ──
        api_key = _get_api_key_from_header()
        if not api_key:
            return _error_response("UNAUTHORIZED", "缺少 API Key，请在 X-API-Key Header 中传入", 401)
        db = _get_db()
        if not db:
            return _error_response("INTERNAL_ERROR", "数据库未就绪", 500)
        key_info = _validate_api_key(api_key, db)
        if not key_info:
            return _error_response("UNAUTHORIZED", "API Key 无效或已停用", 401)
        request.api_key_info = key_info

        # ── 速率限制（基于 API Key） ──
        endpoint = request.path
        rate_err = _rate_limit_check(endpoint, key=api_key)
        if rate_err:
            return _error_response(
                rate_err["code"],
                rate_err["message"],
                429,
                {"retry_after_seconds": rate_err["retry_after_seconds"]},
            )
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# 统一响应组装
# ---------------------------------------------------------------------------


def _error_response(code: str, message: str, status_code: int = 400, details: dict | None = None) -> tuple:
    body = {
        "error": {"code": code, "message": message},
        "meta": {"requested_at": _utc_now_iso()},
    }
    if details:
        body["error"]["details"] = details
    return jsonify(body), status_code


def _success_response(data, status_code: int = 200) -> tuple:
    body = {
        "data": data,
        "meta": {"requested_at": _utc_now_iso()},
    }
    return jsonify(body), status_code


# ---------------------------------------------------------------------------
# 创建 Blueprint
# ---------------------------------------------------------------------------


def _build_bp(db):
    """创建公开 API Blueprint。

    Args:
        db: core.db.Database 实例

    Returns:
        Flask Blueprint 对象
    """
    bp = Blueprint("public_api", __name__, url_prefix="/api/v1")

    # 注入 db 到 app config（供认证中间件使用）
    @bp.record_once
    def _set_db(state):
        state.app.config.setdefault("DB_INSTANCE", db)
        # 注册 flask-cors（在 BP 层面）
        try:
            from flask_cors import CORS
            CORS(state.app, resources={r"/api/v1/*": {"origins": "*"}})
            logger.info("[PUBLIC_API] CORS 已启用: /api/v1/*")
        except ImportError:
            logger.warning("[PUBLIC_API] flask-cors 未安装，CORS 未启用")

        # 确保 api_keys 表存在
        try:
            conn = db.get_conn()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key     TEXT    NOT NULL UNIQUE,
                    name        TEXT    NOT NULL,
                    email       TEXT,
                    tier        TEXT    NOT NULL DEFAULT 'free',
                    is_active   INTEGER NOT NULL DEFAULT 1,
                    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                    last_used   TEXT
                )
            """)
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(api_key)")
            conn.commit()
            logger.info("[PUBLIC_API] api_keys 表已就绪")
        except Exception as e:
            logger.warning("[PUBLIC_API] api_keys 表初始化失败: %s", e)

    # ── 统一错误处理器 ──
    @bp.errorhandler(PublicAPIError)
    def handle_public_api_error(error):
        return _error_response(error.code, error.message, error.status_code, error.details)

    @bp.errorhandler(429)
    def handle_rate_limit(error):
        return _error_response("RATE_LIMITED", "请求频率超过限制，请稍后重试", 429)

    @bp.errorhandler(404)
    def handle_not_found(error):
        return _error_response("NOT_FOUND", "请求的资源不存在", 404)

    @bp.errorhandler(405)
    def handle_method_not_allowed(error):
        return _error_response("METHOD_NOT_ALLOWED", "不支持的请求方法", 405)

    # ===================================================================
    #  GET /api/v1/market/heatmap — 市场信号热力图
    # ===================================================================
    @bp.route("/market/heatmap", methods=["GET"])
    @require_api_key
    @cached(ttl_seconds=30)
    def api_v1_heatmap():
        """市场信号热力图：按板块/品种返回多周期 N 型结构方向矩阵 + 共振分数。

        Query Parameters:
            sector (str, optional): 按板块筛选，如 "贵金属"
            sort_by (str, optional): 排序字段，默认 "score"，可选 "symbol", "name"
            limit (int, optional): 最大返回条数，默认 50，上限 100

        Returns:
            JSON with {data, meta}
        """
        conn = db.get_conn()
        try:
            # ── 1. 参数解析与校验 ──
            sector_filter = (request.args.get("sector") or "").strip()
            sort_by = (request.args.get("sort_by") or "score").strip()
            limit_raw = request.args.get("limit", 50, type=int)

            if sector_filter:
                _, err = _validate_sector(sector_filter)
                if err:
                    return _error_response(err["code"], err["message"], 400)

            validated_limit, err = _validate_limit(limit_raw, 100)
            if err:
                return _error_response(err["code"], err["message"], 400)
            limit = validated_limit

            if sort_by not in ("score", "symbol"):
                return _error_response("INVALID_PARAMS", "sort_by 必须为 score 或 symbol", 400)

            # ── 2. 查询最新期货信号 ──
            sig_rows = conn.execute('''
                SELECT s.symbol, s.contract, s.direction, s.signal_type,
                       s.level1_pass, s.level2_pass, s.level3_pass, s.score, s.created_at
                FROM futures_signals s
                INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
                    ON s.symbol=l.symbol AND s.created_at=l.mt
                ORDER BY s.score DESC
            ''').fetchall()

            signals: dict[str, dict] = {}
            for r in sig_rows:
                d = dict(r)
                signals[d["symbol"]] = {
                    "contract": d["contract"],
                    "direction": d["direction"],
                    "signal_type": d["signal_type"],
                    "score": round(d["score"], 2) if d["score"] else 0,
                    "levels": {
                        "l1": bool(d["level1_pass"]),
                        "l2": bool(d["level2_pass"]),
                        "l3": bool(d["level3_pass"]),
                    },
                }

            # ── 3. 查询 N 型结构 ──
            n_rows = conn.execute('''
                SELECT symbol, timeframe, direction, state,
                       point_a_price, point_b_price, point_c_price,
                       point_a_time, point_b_time, point_c_time, updated_at
                FROM futures_n_structures
                ORDER BY symbol, timeframe
            ''').fetchall()

            structures: dict[str, dict] = {}
            for r in n_rows:
                d = dict(r)
                structures.setdefault(d["symbol"], {})[d["timeframe"]] = {
                    "direction": d["direction"],
                    "state": d["state"],
                    "point_a": {"price": d["point_a_price"], "time": d["point_a_time"]},
                    "point_b": {"price": d["point_b_price"], "time": d["point_b_time"]},
                    "point_c": {"price": d["point_c_price"], "time": d["point_c_time"]},
                }

            # ── 4. 按板块组装 ──
            sectors_to_include: list[tuple[str, list[str]]] = []
            if sector_filter:
                syms = SECTORS.get(sector_filter, [])
                sectors_to_include = [(sector_filter, syms)]
            else:
                sectors_to_include = [(n, syms) for n, syms in SECTORS.items()]

            sector_summaries = []
            all_signals = []

            for sec_name, syms in sectors_to_include:
                sector_items = []
                for sym in syms:
                    if sym not in signals and sym not in structures:
                        continue
                    sig = signals.get(sym, {})
                    sym_name = SYMBOL_NAMES.get(sym, sym)

                    n_struct_data = None
                    if sym in structures:
                        n_struct_data = structures[sym]

                    entry = {
                        "symbol": sym,
                        "name": sym_name,
                        "contract": sig.get("contract", ""),
                        "sector": sec_name,
                        "direction": sig.get("direction"),
                        "signal_type": sig.get("signal_type"),
                        "score": sig.get("score", 0),
                        "levels": sig.get("levels", {"l1": False, "l2": False, "l3": False}),
                        "n_structure": n_struct_data,
                    }
                    sector_items.append(entry)
                    all_signals.append(entry)

                if sector_items:
                    long_c = sum(1 for s in sector_items if s.get("direction") == "LONG")
                    short_c = sum(1 for s in sector_items if s.get("direction") == "SHORT")
                    sector_summaries.append({
                        "name": sec_name,
                        "count": len(sector_items),
                        "long": long_c,
                        "short": short_c,
                        "bias": "多" if long_c > short_c else ("空" if short_c > long_c else "平"),
                    })

            # ── 5. 排序与截断 ──
            if sort_by == "score":
                all_signals.sort(key=lambda x: x.get("score", 0), reverse=True)
            else:
                all_signals.sort(key=lambda x: x.get("symbol", ""))
            all_signals = all_signals[:limit]

            # ── 6. 组装 ──
            return _success_response({
                "signals": all_signals,
                "summary": {
                    "total": len(all_signals),
                    "long_count": sum(1 for s in all_signals if s.get("direction") == "LONG"),
                    "short_count": sum(1 for s in all_signals if s.get("direction") == "SHORT"),
                    "sectors": sector_summaries,
                },
            })
        except Exception as e:
            logger.exception("[PUBLIC_API] heatmap 异常: %s", e)
            return _error_response("INTERNAL_ERROR", "服务器内部错误", 500)

    # ===================================================================
    #  GET /api/v1/signals/top — 高评分信号排行
    # ===================================================================
    @bp.route("/signals/top", methods=["GET"])
    @require_api_key
    @cached(ttl_seconds=30)
    def api_v1_signals_top():
        """评分最高信号排行：返回按评分排序的期货信号列表。

        Query Parameters:
            direction (str, optional): 筛选方向 "LONG" 或 "SHORT"
            min_score (float, optional): 最低评分，默认 0
            limit (int, optional): 最大返回条数，默认 50，上限 100

        Returns:
            JSON with {data, meta}
        """
        conn = db.get_conn()
        try:
            # ── 1. 参数解析与校验 ──
            direction_raw = (request.args.get("direction") or "").strip().upper()
            min_score_raw = request.args.get("min_score", "0")
            limit_raw = request.args.get("limit", 50, type=int)

            validated_direction, err = _validate_direction(direction_raw if direction_raw else None)
            if err:
                return _error_response(err["code"], err["message"], 400)
            direction = validated_direction

            try:
                min_score = float(min_score_raw)
            except (ValueError, TypeError):
                return _error_response("INVALID_PARAMS", "min_score 必须为数字", 400)
            if min_score < 0:
                return _error_response("INVALID_PARAMS", "min_score 不能为负数", 400)

            validated_limit, err = _validate_limit(limit_raw, 100)
            if err:
                return _error_response(err["code"], err["message"], 400)
            limit = validated_limit

            # ── 2. 构建查询 ──
            where_clauses = ["s.score >= ?"]
            params: list = [min_score]

            if direction:
                where_clauses.append("s.direction = ?")
                params.append(direction)

            where_sql = " AND ".join(where_clauses)

            rows = conn.execute(f'''
                SELECT s.symbol, s.contract, s.direction, s.signal_type,
                       s.level1_pass, s.level2_pass, s.level3_pass,
                       s.score, s.entry_price, s.stop_loss, s.take_profit,
                       s.detail, s.created_at
                FROM futures_signals s
                INNER JOIN (
                    SELECT symbol, MAX(created_at) mt
                    FROM futures_signals s2
                    WHERE {where_sql.replace('s.', 's2.')}
                    GROUP BY symbol
                ) l ON s.symbol = l.symbol AND s.created_at = l.mt
                ORDER BY s.score DESC
                LIMIT ?
            ''', params + [limit]).fetchall()

            # ── 3. 组装结果 ──
            signals = []
            for r in rows:
                d = dict(r)
                signals.append({
                    "symbol": d["symbol"],
                    "name": SYMBOL_NAMES.get(d["symbol"], d["symbol"]),
                    "contract": d["contract"],
                    "direction": d["direction"],
                    "signal_type": d["signal_type"],
                    "score": round(d["score"], 2) if d["score"] else 0,
                    "levels": {
                        "l1": bool(d["level1_pass"]),
                        "l2": bool(d["level2_pass"]),
                        "l3": bool(d["level3_pass"]),
                    },
                    "entry_price": d["entry_price"],
                    "stop_loss": d["stop_loss"],
                    "take_profit": d["take_profit"],
                    "detail": d.get("detail", ""),
                    "created_at": d["created_at"],
                })

            return _success_response({
                "total": len(signals),
                "direction_filter": direction if direction else "ALL",
                "min_score": min_score,
                "signals": signals,
            })
        except Exception as e:
            logger.exception("[PUBLIC_API] signals/top 异常: %s", e)
            return _error_response("INTERNAL_ERROR", "服务器内部错误", 500)

    # ===================================================================
    #  GET /api/v1/options/iv-summary — 期权 IV 快照
    # ===================================================================
    @bp.route("/options/iv-summary", methods=["GET"])
    @require_api_key
    @cached(ttl_seconds=300)
    def api_v1_options_iv():
        """期权 IV 状态快照：所有期权品种的最新 IV 百分位和等级。

        通过 IVRecorder 的 get_all_status() 获取每个品种最新的 IV 快照，
        计算历史百分位和等级（极端高/偏高/正常/偏低/极端低）。

        Query Parameters:
            days (int, optional): 回溯天数计算百分位，默认 30
            sort_by (str, optional): 排序字段，默认 "percentile"，可选 "current_iv"
            limit (int, optional): 最大返回条数，默认 50，上限 100

        Returns:
            JSON with {data, meta}
        """
        conn = db.get_conn()
        try:
            # ── 1. 参数解析与校验 ──
            days_raw = request.args.get("days", 30, type=int)
            sort_by = (request.args.get("sort_by") or "percentile").strip()
            limit_raw = request.args.get("limit", 50, type=int)

            if days_raw < 1 or days_raw > 365:
                return _error_response("INVALID_PARAMS", "days 必须在 1-365 之间", 400)
            days = days_raw

            if sort_by not in ("percentile", "current_iv"):
                return _error_response("INVALID_PARAMS", "sort_by 必须为 percentile 或 current_iv", 400)

            validated_limit, err = _validate_limit(limit_raw, 100)
            if err:
                return _error_response(err["code"], err["message"], 400)
            limit = validated_limit

            # ── 2. 获取 IV 数据 ──
            from data.iv_recorder import IVRecorder
            iv_recorder = IVRecorder(db)
            status_list = iv_recorder.get_all_status(days=days)

            # ── 3. 组装 ──
            results = []
            for s in status_list:
                results.append({
                    "symbol": s["symbol"],
                    "name": SYMBOL_NAMES.get(s["symbol"], s["symbol"]),
                    "contract": s.get("contract", ""),
                    "current_iv": s.get("current_iv", 0),
                    "percentile": s.get("percentile", None),
                    "level": s.get("level", "未知"),
                    "futures_price": s.get("futures_price", 0),
                    "samples": s.get("samples", 0),
                    "range": {
                        "min": s.get("min_iv", 0),
                        "p25": s.get("p25", 0),
                        "p50": s.get("p50", 0),
                        "p75": s.get("p75", 0),
                        "max": s.get("max_iv", 0),
                    },
                })

            # ── 4. 排序 ──
            if sort_by == "percentile":
                results.sort(key=lambda x: x.get("percentile") if x.get("percentile") is not None else -1, reverse=True)
            else:
                results.sort(key=lambda x: x.get("current_iv", 0), reverse=True)

            results = results[:limit]

            # ── 5. 统计 ──
            level_counts: dict[str, int] = {}
            for r in results:
                lvl = r["level"]
                level_counts[lvl] = level_counts.get(lvl, 0) + 1

            return _success_response({
                "total": len(results),
                "days": days,
                "level_summary": level_counts,
                "iv_data": results,
            })
        except Exception as e:
            logger.exception("[PUBLIC_API] iv-summary 异常: %s", e)
            return _error_response("INTERNAL_ERROR", "服务器内部错误", 500)

    return bp