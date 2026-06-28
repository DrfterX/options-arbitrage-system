"""Admin 管理面板 + 用户注册/登录/Bot 订阅 + 免费试用 + 品种页 Blueprint。

所有路由通过函数工厂注入 db 依赖。
"""

import hashlib, json, logging, os, re, secrets, time as _time_mod
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, jsonify, render_template, request

logger = logging.getLogger(__name__)


def _init_auth_bp(_db):
    """注入 db 依赖并注册 Admin/Auth/Bot/Trial 路由。"""
    from web.stripe_handler import _generate_token, ensure_premium_table
    from web.helpers import _admin_pw_ok, SYMBOL_NAMES

    bp = Blueprint("auth", __name__)

    # ── 限流 ──────────────────────────────────────────────────
    _login_rate_limit: dict[str, list[float]] = {}

    def _check_login_rate_limit() -> bool:
        ip = request.remote_addr or "unknown"
        now = _time_mod.time()
        records = [t for t in _login_rate_limit.get(ip, []) if now - t < 300]
        if len(records) >= 5:
            return False
        records.append(now)
        _login_rate_limit[ip] = records
        return True

    def _generate_session_token() -> str:
        return secrets.token_urlsafe(48)

    def _ensure_session_table() -> None:
        conn = _db.get_conn()
        conn.execute("""CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
            expires_at TEXT NOT NULL,
            last_used_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES user_registrations(id) ON DELETE CASCADE
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(token)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at)")
        conn.commit()

    def _ensure_user_table() -> None:
        conn = _db.get_conn()
        conn.execute("""CREATE TABLE IF NOT EXISTS user_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
            last_login TEXT
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_registrations_email ON user_registrations(email)")
        conn.commit()

    def _is_registered_user() -> bool:
        token = ""
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
        if not token:
            token = request.args.get("token", "")
        if not token:
            return False
        conn = _db.get_conn()
        row = conn.execute(
            """SELECT id FROM user_sessions
               WHERE token = ? AND is_active = 1 AND expires_at > datetime('now', '+8 hours')""",
            (token,),
        ).fetchone()
        if row:
            conn.execute("UPDATE user_sessions SET last_used_at = datetime('now', '+8 hours') WHERE id = ?", (row["id"],))
            conn.commit()
            return True
        return False

    # ── 追踪辅助 ──────────────────────────────────────────────
    def _transparent_gif() -> bytes:
        return (b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
                b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00'
                b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')

    # ═══════════════════════ 路由 ═══════════════════════

    @bp.route("/api/track.gif")
    def api_track():
        url = request.args.get("url", request.referrer or "/")
        ref = request.args.get("ref", request.referrer or "")
        ua = request.user_agent.string if request.user_agent else ""
        ip = request.remote_addr or ""
        fp = hashlib.md5(f"{ip}|{ua}".encode()).hexdigest()[:16]
        try:
            conn = _db.get_conn()
            conn.execute(
                "INSERT INTO page_hits (url, referrer, user_agent, ip, session_id, visited_at) VALUES (?, ?, ?, ?, ?, ?)",
                (url, ref, ua, ip, fp, int(datetime.now().timestamp())),
            )
            conn.commit()
        except Exception as exc:
            logger.warning("track.gif error: %s", exc)
        return _transparent_gif(), 200, {"Content-Type": "image/gif", "Cache-Control": "no-store, no-cache, must-revalidate"}

    @bp.route("/api/stats/visits")
    def api_stats_visits():
        conn = _db.get_conn()
        total = conn.execute("SELECT COUNT(*) as c FROM page_hits").fetchone()["c"]
        today = conn.execute(
            "SELECT COUNT(*) as c FROM page_hits WHERE visited_at >= ?",
            (int(datetime.now().timestamp()) - 86400,),
        ).fetchone()["c"]
        top_pages = conn.execute(
            "SELECT url, COUNT(*) as c FROM page_hits GROUP BY url ORDER BY c DESC LIMIT 10"
        ).fetchall()
        top_refs = conn.execute(
            "SELECT referrer, COUNT(*) as c FROM page_hits WHERE referrer != '' GROUP BY referrer ORDER BY c DESC LIMIT 10"
        ).fetchall()
        return jsonify({
            "total": total, "today": today,
            "top_pages": [dict(r) for r in top_pages],
            "top_refs": [dict(r) for r in top_refs],
        })

    @bp.route("/analytics")
    def analytics_page():
        return render_template("analytics.html")

    @bp.route("/admin")
    def admin_panel():
        return render_template("admin_panel.html")

    @bp.route("/api/admin/verify-password", methods=["POST"])
    def api_admin_verify_password():
        data = request.get_json() or {}
        password = data.get("password", "")
        if _admin_pw_ok(password):
            return jsonify({"ok": True})
        return jsonify({"ok": False})

    @bp.route("/api/admin/generate-token", methods=["POST"])
    def api_admin_generate_token():
        from web.stripe_handler import _generate_token, ensure_premium_table
        data = request.get_json() or {}
        password = data.get("password", "")
        email = data.get("email", "")
        if not _admin_pw_ok(password):
            return jsonify({"error": "密码错误"}), 403
        if not email:
            return jsonify({"error": "缺少 email"}), 400
        token = _generate_token()
        ensure_premium_table(_db)
        conn = _db.get_conn()
        try:
            conn.execute(
                """INSERT INTO premium_subscriptions (session_id, customer_id, email, status, token) VALUES (?, ?, ?, ?, ?)""",
                (f"manual_{int(__import__('time').time())}", "manual", email, "active", token),
            )
            conn.commit()
            logger.info("管理员手动生成 Token: token=%s email=%s", token[:8] + "...", email)
            return jsonify({"token": token, "email": email})
        except Exception as e:
            conn.rollback()
            logger.error("生成 Token 失败: %s", e)
            return jsonify({"error": str(e)}), 500

    @bp.route("/api/admin/list-subscriptions")
    def api_admin_list_subscriptions():
        password = request.args.get("password", "")
        if not _admin_pw_ok(password):
            return jsonify({"error": "密码错误"}), 403
        ensure_premium_table(_db)
        conn = _db.get_conn()
        rows = conn.execute(
            "SELECT id, session_id, email, status, created_at, expires_at FROM premium_subscriptions ORDER BY id DESC"
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    @bp.route("/api/auth/register", methods=["POST"])
    def api_auth_register():
        _ensure_user_table()
        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "请输入有效的邮箱地址"}), 400
        if len(password) < 6:
            return jsonify({"error": "密码至少需要 6 个字符"}), 400
        import bcrypt
        pwd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn = _db.get_conn()
        try:
            conn.execute("INSERT INTO user_registrations (email, password_hash) VALUES (?, ?)", (email, pwd_hash))
            conn.commit()
            logger.info("新用户注册: %s", email)
            return jsonify({"ok": True, "email": email})
        except Exception:
            return jsonify({"error": "该邮箱已注册"}), 409

    @bp.route("/api/auth/login", methods=["POST"])
    def api_auth_login():
        _ensure_user_table()
        _ensure_session_table()
        if not _check_login_rate_limit():
            return jsonify({"error": "登录尝试过于频繁，请 5 分钟后再试"}), 429
        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        import bcrypt
        conn = _db.get_conn()
        row = conn.execute(
            "SELECT id, password_hash FROM user_registrations WHERE email = ?", (email,)
        ).fetchone()
        if not row or not bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
            return jsonify({"error": "邮箱或密码错误"}), 401
        token = _generate_session_token()
        expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M")
        conn.execute(
            "INSERT INTO user_sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (row["id"], token, expires_at),
        )
        conn.commit()
        conn.execute("UPDATE user_registrations SET last_login = datetime('now', '+8 hours') WHERE id = ?", (row["id"],))
        conn.commit()
        return jsonify({"ok": True, "token": token, "email": email})

    @bp.route("/api/auth/verify", methods=["POST"])
    def api_auth_verify():
        data = request.get_json() or {}
        token = data.get("token", "")
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
        if not token:
            return jsonify({"ok": False, "error": "缺少 token"}), 400
        conn = _db.get_conn()
        row = conn.execute(
            """SELECT u.email FROM user_sessions s JOIN user_registrations u ON s.user_id = u.id
               WHERE s.token = ? AND s.is_active = 1 AND s.expires_at > datetime('now', '+8 hours')""",
            (token,),
        ).fetchone()
        if row:
            return jsonify({"ok": True, "email": row["email"]})
        return jsonify({"ok": False, "error": "token 无效或已过期"}), 401

    @bp.route("/api/pricing/user-status")
    def api_pricing_user_status():
        token = ""
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
        if not token:
            token = request.args.get("token", "")
        is_logged_in = False
        email = ""
        if token:
            conn = _db.get_conn()
            row = conn.execute(
                """SELECT u.email FROM user_sessions s JOIN user_registrations u ON s.user_id = u.id
                   WHERE s.token = ? AND s.is_active = 1 AND s.expires_at > datetime('now', '+8 hours')""",
                (token,),
            ).fetchone()
            if row:
                is_logged_in = True
                email = row["email"]
        is_premium = False
        premium_email = email
        if is_logged_in:
            conn = _db.get_conn()
            ensure_premium_table(_db)
            p_row = conn.execute(
                "SELECT status FROM premium_subscriptions WHERE email = ? AND status = 'active'", (email,)
            ).fetchone()
            is_premium = p_row is not None
        return jsonify({"is_logged_in": is_logged_in, "email": email, "is_premium": is_premium})

    @bp.route("/telegram-webhook", methods=["POST"])
    def telegram_webhook():
        from signals.telegram_notifier import TelegramNotifier
        from signals.bot_handler import BotHandler
        notifier = TelegramNotifier(_db)
        handler = BotHandler(_db, notifier)
        body = request.get_data(as_text=True)
        content_type = request.content_type or ""
        if "application/json" in content_type:
            try:
                update = json.loads(body)
            except json.JSONDecodeError:
                return jsonify({"ok": False, "error": "无效 JSON"}), 400
        else:
            return jsonify({"ok": False, "error": "不支持的内容类型"}), 415
        logger.debug("Telegram webhook 收到: %s", json.dumps(update, ensure_ascii=False)[:200])
        try:
            handler.handle_update(update)
        except Exception as e:
            logger.error("Telegram webhook 处理异常: %s", e, exc_info=True)
        return jsonify({"ok": True})

    @bp.route("/api/bot/subscribe", methods=["POST"])
    def api_bot_subscribe():
        from signals.bot_subscription import BotSubscription
        data = request.get_json() or {}
        chat_id = data.get("telegram_chat_id", "").strip()
        if not chat_id:
            return jsonify({"ok": False, "error": "缺少 telegram_chat_id"}), 400
        mgr = BotSubscription(_db)
        success = mgr.subscribe(
            chat_id=chat_id,
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            preferences=data.get("preferences"),
        )
        if not success:
            return jsonify({"ok": False, "error": "订阅失败"}), 500
        return jsonify({"ok": True})

    @bp.route("/api/bot/unsubscribe", methods=["POST"])
    def api_bot_unsubscribe():
        from signals.bot_subscription import BotSubscription
        data = request.get_json() or {}
        chat_id = data.get("telegram_chat_id", "").strip()
        if not chat_id:
            return jsonify({"error": "缺少 telegram_chat_id"}), 400
        mgr = BotSubscription(_db)
        mgr.unsubscribe(chat_id)
        return jsonify({"ok": True, "message": "已取消订阅"})

    @bp.route("/api/subscribe", methods=["POST"])
    def api_subscribe():
        from signals.bot_subscription import BotSubscription
        data = request.get_json()
        if not data:
            return jsonify({"ok": False, "error": "请求体为空"}), 400
        chat_id = data.get("telegram_chat_id", "").strip()
        if not chat_id:
            return jsonify({"ok": False, "error": "缺少 telegram_chat_id"}), 400
        mgr = BotSubscription(_db)
        success = mgr.subscribe(
            chat_id=chat_id,
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            preferences=data.get("preferences"),
        )
        if not success:
            return jsonify({"ok": False, "error": "订阅失败，请稍后重试"}), 500
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

    @bp.route("/api/unsubscribe", methods=["POST"])
    def api_unsubscribe():
        from signals.bot_subscription import BotSubscription
        data = request.get_json()
        if not data:
            return jsonify({"ok": False, "error": "请求体为空"}), 400
        chat_id = data.get("telegram_chat_id", "").strip()
        if not chat_id:
            return jsonify({"ok": False, "error": "缺少 telegram_chat_id"}), 400
        mgr = BotSubscription(_db)
        mgr.unsubscribe(chat_id)
        return jsonify({"ok": True, "message": "已取消订阅"})

    @bp.route("/api/subscribe/status")
    def api_subscribe_status():
        from signals.bot_subscription import BotSubscription
        chat_id = request.args.get("chat_id", "").strip()
        if not chat_id:
            return jsonify({"ok": False, "error": "缺少 chat_id"}), 400
        mgr = BotSubscription(_db)
        sub = mgr.get_subscriber(chat_id)
        if sub:
            return jsonify({"ok": True, "data": sub})
        return jsonify({"ok": False, "error": "未找到订阅记录"}), 404

    @bp.route("/api/public/request-trial", methods=["POST"])
    def api_request_trial():
        from web.stripe_handler import _generate_token, ensure_premium_table
        data = request.get_json() or {}
        email = data.get("email", "").strip()
        token = _generate_token()
        ensure_premium_table(_db)
        expires_at = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
        conn = _db.get_conn()
        try:
            conn.execute(
                """INSERT INTO premium_subscriptions (session_id, customer_id, email, status, token, expires_at) VALUES (?, ?, ?, ?, ?, ?)""",
                (f"trial_{int(_time_mod.time())}", "trial", email or "trial@autocompany.ai", "active", token, expires_at),
            )
            conn.commit()
            logger.info("免费试用 Token: token=%s email=%s", token[:8] + "...", email or "(空)")
            return jsonify({"token": token, "days": 7, "expires_at": expires_at})
        except Exception as e:
            conn.rollback()
            logger.error("生成试用 Token 失败: %s", e)
            return jsonify({"error": str(e)}), 500

    return bp