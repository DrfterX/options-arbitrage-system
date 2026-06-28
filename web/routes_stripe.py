"""Stripe 付费订阅 Blueprint。"""

import os
from flask import Blueprint, jsonify, request
from web.stripe_handler import (
    create_checkout_session, ensure_premium_table,
    handle_webhook, create_customer_portal_session, check_premium_status,
)

stripe_bp = Blueprint("stripe", __name__)


def _init_stripe_bp(_db):
    """注入 db 依赖并注册路由。"""

    @stripe_bp.route("/api/create-checkout-session", methods=["POST"])
    def api_create_checkout_session():
        data = request.get_json() or {}
        email = data.get("email", "")
        tier = data.get("tier", "premium")
        if tier not in ("pro", "premium"):
            return jsonify({"error": "无效 tier，可选: pro / premium"}), 400
        ensure_premium_table(_db)
        base_url = os.environ.get("SIGNALS_BASE_URL", "https://signals.drifter.indevs.in")
        result = create_checkout_session(_db, email=email, tier=tier, base_url=base_url)
        if "error" in result:
            return jsonify(result), 500
        return jsonify(result)

    @stripe_bp.route("/api/stripe-webhook", methods=["POST"])
    def api_stripe_webhook():
        payload = request.get_data()
        sig_header = request.headers.get("stripe-signature", "")
        result = handle_webhook(_db, payload, sig_header)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)

    @stripe_bp.route("/api/customer-portal", methods=["POST"])
    def api_customer_portal():
        data = request.get_json() or {}
        email = data.get("email", "")
        if not email:
            return jsonify({"error": "缺少 email"}), 400
        base_url = os.environ.get("SIGNALS_BASE_URL", "https://signals.drifter.indevs.in")
        result = create_customer_portal_session(_db, email=email, base_url=base_url)
        if "error" in result:
            return jsonify(result), 500
        return jsonify(result)

    @stripe_bp.route("/api/premium/status")
    def api_premium_status():
        session_id = request.args.get("session_id", "")
        email = request.args.get("email", "")
        result = check_premium_status(_db, session_id=session_id, email=email)
        return jsonify(result)

    @stripe_bp.route("/api/premium/verify-token", methods=["POST"])
    def api_premium_verify_token():
        data = request.get_json() or {}
        token = data.get("token", "")
        # token 验证直接查表
        conn = _db.get_conn()
        row = conn.execute(
            "SELECT email FROM premium_subscriptions WHERE token=? AND status='active'",
            (token,),
        ).fetchone()
        if row:
            return jsonify({"valid": True, "email": row["email"]})
        return jsonify({"valid": False}), 401

    @stripe_bp.route("/api/premium/token")
    def api_premium_token():
        session_id = request.args.get("session_id", "")
        if not session_id:
            return jsonify({"error": "缺少 session_id"}), 400
        ensure_premium_table(_db)
        conn = _db.get_conn()
        row = conn.execute(
            "SELECT token FROM premium_subscriptions WHERE session_id=? AND status='active'",
            (session_id,),
        ).fetchone()
        if row and row["token"]:
            return jsonify({"token": row["token"]})
        return jsonify({"token": None}), 404

    return stripe_bp