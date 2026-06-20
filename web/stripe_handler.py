"""
Stripe 付费订阅集成模块 — Signals Premium $19/月。

提供:
  - create_checkout_session() — 创建 Stripe Checkout Session
  - handle_webhook() — 验证并处理 Stripe webhook 事件
  - check_premium_status() — 查询订阅状态
  - ensure_premium_table() — 建表 premium_subscriptions

环境变量:
  - STRIPE_SECRET_KEY: Stripe Secret Key (sk_test_xxx / sk_live_xxx)
  - STRIPE_WEBHOOK_SECRET: Stripe Webhook Signing Secret (whsec_xxx)
  - PREMIUM_PRICE_ID: Stripe Price ID for $19/mo subscription

数据库表:
  premium_subscriptions(
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id    TEXT NOT NULL UNIQUE,     -- Stripe Checkout Session ID
    customer_id   TEXT DEFAULT '',          -- Stripe Customer ID (cus_xxx)
    email         TEXT DEFAULT '',          -- 用户邮箱
    status        TEXT NOT NULL DEFAULT 'active',  -- active / expired / cancelled
    token         TEXT DEFAULT '',          -- Bearer Token (Step 2 使用)
    created_at    TEXT DEFAULT (datetime('now','localtime')),
    expires_at    TEXT DEFAULT ''           -- 过期时间
  )
"""

import logging
import os
import secrets
from functools import wraps
from typing import Optional

import stripe
from stripe._webhook import Webhook

logger = logging.getLogger(__name__)

# ─── Stripe 配置（全局 API Key） ───────────────────────────────

_configured: bool = False


def _ensure_configured() -> None:
    """确保 stripe.api_key 已配置（首次调用时从环境变量读取）。"""
    global _configured
    if not _configured:
        key = os.environ.get("STRIPE_SECRET_KEY", "")
        if not key:
            logger.warning("STRIPE_SECRET_KEY 未设置，Stripe 调用将失败")
        else:
            stripe.api_key = key
        _configured = True


# ─── 配置 ──────────────────────────────────────────────────────

def get_price_id() -> str:
    """获取 Premium 订阅 Price ID。"""
    return os.environ.get("PREMIUM_PRICE_ID", "price_premium_monthly")


def get_webhook_secret() -> str:
    """获取 Stripe Webhook Secret。"""
    return os.environ.get("STRIPE_WEBHOOK_SECRET", "")


# ─── 数据库 ────────────────────────────────────────────────────


PREMIUM_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS premium_subscriptions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id      TEXT NOT NULL UNIQUE,
        customer_id     TEXT DEFAULT '',
        subscription_id TEXT DEFAULT '',
        email           TEXT DEFAULT '',
        status          TEXT NOT NULL DEFAULT 'active',
        token           TEXT DEFAULT '',
        created_at      TEXT DEFAULT (datetime('now','localtime')),
        expires_at      TEXT DEFAULT ''
    )
"""


def ensure_premium_table(db) -> None:
    """创建 premium_subscriptions 表（如不存在），并执行增量迁移。"""
    conn = db.get_conn()
    conn.execute(PREMIUM_TABLE_DDL)
    # 增量迁移：为旧表补 subscription_id 列
    cols = {row[1] for row in conn.execute("PRAGMA table_info(premium_subscriptions)")}
    if "subscription_id" not in cols:
        conn.execute("ALTER TABLE premium_subscriptions ADD COLUMN subscription_id TEXT DEFAULT ''")
    if "tier" not in cols:
        conn.execute("ALTER TABLE premium_subscriptions ADD COLUMN tier TEXT DEFAULT 'premium'")
    conn.commit()


# ─── Checkout Session ──────────────────────────────────────────

STARTER_PRICE = 1900  # $19.00 in cents


def get_pro_price_id() -> str:
    """获取 Pro 订阅 Price ID。"""
    return os.environ.get("PRO_PRICE_ID", "price_pro_monthly")


def create_checkout_session(
    db,
    email: str = "",
    tier: str = "premium",
    base_url: str = "https://signals.drifter.indevs.in",
) -> dict:
    """创建 Stripe Checkout Session。

    Args:
        db: Database 实例。
        email: 用户邮箱（可选）。
        tier: "pro" ($9/mo) 或 "premium" ($19/mo)，默认 "premium"。
        base_url: 成功/取消回调 URL 的 base。

    Returns:
        dict: {"url": "checkout.stripe.com/..."} 或 {"error": "..."}
    """
    _ensure_configured()

    price_id = get_pro_price_id() if tier == "pro" else get_price_id()
    tier_label = "Pro" if tier == "pro" else "Premium"

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer_email=email or None,
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            success_url=f"{base_url}/premium/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/pricing?canceled=1",
            metadata={
                "source": "signals_premium",
                "tier": tier,
            },
            subscription_data={
                "metadata": {"source": "signals_premium", "tier": tier},
            },
        )

        logger.info("Stripe Checkout Session 创建: %s (tier=%s email=%s)", session.id, tier, email)
        return {"url": session.url}

    except stripe.StripeError as e:
        logger.error("Stripe Checkout Session 创建失败(%s): %s", tier_label, e)
        return {"error": str(e)}


# ─── Webhook ───────────────────────────────────────────────────

def handle_webhook(db, payload: bytes, sig_header: str) -> dict:
    """验证并处理 Stripe Webhook 事件。

    Args:
        db: Database 实例。
        payload: 原始请求体（bytes，未解析）。
        sig_header: ``stripe-signature`` 请求头的值。

    Returns:
        dict: {"received": True} 表示成功处理。
        若验证失败返回 {"error": "..."}，HTTP 调用方应返回 400。
    """
    secret = get_webhook_secret()
    if not secret:
        logger.warning("STRIPE_WEBHOOK_SECRET 未设置，跳过 webhook 验证")
        return {"error": "webhook secret not configured"}

    _ensure_configured()

    try:
        event = Webhook.construct_event(payload, sig_header, secret)
    except (stripe.StripeError, ValueError) as e:
        logger.error("Webhook 签名验证失败: %s", e)
        return {"error": f"signature verification failed: {e}"}

    event_type = event.get("type", "")
    logger.info("Webhook 收到事件: %s", event_type)

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(db, event["data"]["object"])
    elif event_type == "customer.subscription.updated":
        _handle_subscription_updated(db, event["data"]["object"])
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(db, event["data"]["object"])
    else:
        logger.info("忽略未处理的事件类型: %s", event_type)

    return {"received": True}


def _generate_token() -> str:
    """生成唯一的 Bearer Token。"""
    return secrets.token_urlsafe(32)


def _handle_checkout_completed(db, session: dict) -> None:
    """处理 checkout.session.completed 事件——记录支付成功并生成 Bearer Token。"""
    session_id = session.get("id", "")
    customer_id = session.get("customer", "") or ""
    subscription_id = session.get("subscription", "") or ""
    email = session.get("customer_details", {}).get("email", "") or ""
    status = session.get("status", "complete")
    token = _generate_token()
    tier = (session.get("metadata") or {}).get("tier", "premium")

    ensure_premium_table(db)
    conn = db.get_conn()

    try:
        conn.execute(
            """INSERT OR IGNORE INTO premium_subscriptions
               (session_id, customer_id, subscription_id, email, status, token, tier)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, customer_id, subscription_id, email,
             "active" if status == "complete" else status, token, tier),
        )
        conn.commit()
        logger.info("订阅记录已写入: session=%s email=%s tier=%s token=%s", session_id, email, tier, token[:8] + "...")
    except Exception as e:
        logger.error("写入订阅记录失败: %s", e)


def _handle_subscription_updated(db, subscription: dict) -> None:
    """处理 customer.subscription.updated——更新订阅状态。"""
    status = subscription.get("status", "")
    if status == "past_due":
        _update_subscription_status(db, subscription.get("id", ""), "past_due")
    elif status == "active":
        _update_subscription_status(db, subscription.get("id", ""), "active")
    logger.info("订阅已更新: id=%s status=%s", subscription.get("id", ""), status)


def _handle_subscription_deleted(db, subscription: dict) -> None:
    """处理 customer.subscription.deleted——标记订阅过期。"""
    _update_subscription_status(db, subscription.get("id", ""), "expired")
    logger.info("订阅已删除: id=%s", subscription.get("id", ""))


def _update_subscription_status(db, subscription_id: str, status: str) -> None:
    """更新订阅状态（优先按 subscription_id 关联，回退 customer_id）。"""
    conn = db.get_conn()
    conn.execute(
        "UPDATE premium_subscriptions SET status=? WHERE subscription_id=?",
        (status, subscription_id),
    )
    # 兼容旧数据（subscription_id 为空、靠 customer_id 关联的记录）
    conn.execute(
        "UPDATE premium_subscriptions SET status=?, subscription_id=? "
        "WHERE customer_id=? AND (subscription_id='' OR subscription_id IS NULL)",
        (status, subscription_id, subscription_id),
    )
    conn.commit()


# ─── 客户门户（管理订阅/取消/升级） ──────────────────────────


def create_customer_portal_session(
    db,
    email: str,
    base_url: str = "https://signals.drifter.indevs.in",
) -> dict:
    """创建 Stripe Customer Portal Session，返回管理门户链接。

    Args:
        db: Database 实例。
        email: 用户邮箱。
        base_url: 门户返回 URL。

    Returns:
        dict: {"url": "billing.stripe.com/..."} 或 {"error": "..."}
    """
    _ensure_configured()

    # 查询该 email 的 Stripe customer_id
    ensure_premium_table(db)
    conn = db.get_conn()
    row = conn.execute(
        "SELECT customer_id FROM premium_subscriptions WHERE email=? AND status='active' ORDER BY id DESC LIMIT 1",
        (email,),
    ).fetchone()

    customer_id = row["customer_id"] if row and row["customer_id"] else ""
    if not customer_id:
        logger.warning("未找到 %s 的 Stripe Customer，尝试创建临时门户", email)
        # Stripe 允许传入 email 自动关联或创建客户
        customer_id = email  # fallback: pass email as customer reference

    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{base_url}/pricing",
        )
        logger.info("Customer Portal 创建: email=%s url=%s", email, session.url)
        return {"url": session.url}
    except stripe.StripeError as e:
        logger.error("Customer Portal 创建失败: %s", e)
        return {"error": str(e)}


# ─── 状态查询 ──────────────────────────────────────────────────


def check_premium_status(db, session_id: str = "", email: str = "") -> dict:
    """查询订阅状态。

    Args:
        db: Database 实例。
        session_id: Stripe Checkout Session ID（优先）。
        email: 用户邮箱（备选）。

    Returns:
        dict: {
            "premium": bool,
            "session_id": str,
            "email": str,
            "status": str,
            "created_at": str or None,
        }
    """
    ensure_premium_table(db)
    conn = db.get_conn()

    try:
        if session_id:
            row = conn.execute(
                "SELECT * FROM premium_subscriptions WHERE session_id=?",
                (session_id,),
            ).fetchone()
        elif email:
            row = conn.execute(
                "SELECT * FROM premium_subscriptions WHERE email=? ORDER BY id DESC LIMIT 1",
                (email,),
            ).fetchone()
        else:
            return {"premium": False, "error": "session_id 或 email 至少提供一个"}

        if row and row["status"] == "active":
            return {
                "premium": True,
                "session_id": row["session_id"],
                "email": row["email"],
                "status": row["status"],
                "created_at": row["created_at"],
            }

        return {
            "premium": False,
            "session_id": session_id if row else "",
            "email": row["email"] if row else "",
            "status": row["status"] if row else "none",
            "created_at": row["created_at"] if row else None,
        }
    except Exception as e:
        logger.error("查询订阅状态失败: %s", e)
        return {"premium": False, "error": str(e)}


# ─── 直接验证（供 Step 2 鉴权装饰器调用） ──────────────────────


def verify_token(db, token: str) -> bool:
    """验证 Bearer Token 是否有效（预留，Step 2 实现）。"""
    if not token:
        return False
    ensure_premium_table(db)
    conn = db.get_conn()
    row = conn.execute(
        "SELECT id FROM premium_subscriptions WHERE token=? AND status='active'",
        (token,),
    ).fetchone()
    return row is not None


# ─── 鉴权装饰器 ────────────────────────────────────────────────


def require_premium(f):
    """Flask 路由装饰器：要求请求携带有效的 Premium Bearer Token。

    用法::

        @app.route("/api/premium/xxx")
        @require_premium
        def my_premium_api():
            return jsonify({"data": "..."})

    Token 通过以下方式获取（按优先级）:
      1. ``Authorization: Bearer <token>`` 请求头
      2. ``token`` URL query parameter
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, jsonify

        from web.app import db as _db

        token = ""
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
        if not token:
            token = request.args.get("token", "")

        if not token:
            return jsonify({"error": "缺少 token", "premium": False}), 401

        if not verify_token(_db, token):
            return jsonify({"error": "token 无效或已过期", "premium": False}), 403

        return f(*args, **kwargs)

    return decorated
