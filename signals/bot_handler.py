"""
Bot 命令处理器 — 解析 Telegram Update 并路由到对应处理函数。

指令:
    /start      — 欢迎 + 功能介绍 + 订阅引导
    /subscribe  — 订阅信号推送
    /unsubscribe — 取消订阅
    /help       — 帮助
    /status     — 查看订阅状态

依赖:
    - signals.bot_subscription.BotSubscription (多用户订阅管理)
    - core.db.Database (数据库连接)
    - requests (发送回复消息)
"""

import logging
from pathlib import Path
from typing import Any

import requests

from core.db import Database
from signals.bot_subscription import BotSubscription

logger = logging.getLogger(__name__)

# ── 项目根路径 ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── 消息模板（Critic 风险缓释已集成） ──────────────────────────────────────

WELCOME_MSG = (
    "🤖 *Drifter 期货信号 Bot* 🧪 Beta\n\n"
    "实时期货信号推送至您的手机！\n\n"
    "📊 *支持的品种:*\n"
    "• 橡胶(RU) • 螺纹钢(RB) • 铁矿石(I) • 更多接入中\n\n"
    "*命令列表:*\n"
    "/subscribe — 📥 订阅信号推送\n"
    "/unsubscribe — 📤 取消订阅\n"
    "/status — 📋 查看订阅状态\n"
    "/help — ❓ 使用帮助\n\n"
    "🌐 Web 版: https://futures.drifter.indevs.in\n\n"
    "⭐ *Pro 版本即将推出！* 更多品种、更多信号类型、个性化推送。"
)

SUBSCRIBE_SUCCESS = (
    "✅ *订阅成功！*\n\n"
    "您已成功订阅 Drifter 期货信号推送 🎉\n\n"
    "📬 您将收到以下推送:\n"
    "• 🚨 ENTRY 信号（入场信号）\n"
    "• ⚠️ CANDIDATE 信号（关注信号）\n"
    "• 📊 每日汇总报告\n\n"
    "🧪 *Beta 说明:* 信号质量为实验性，仅供参考，不构成投资建议。\n\n"
    "⭐ *Pro 即将推出* — 更多指标、个性化设置！"
)

SUBSCRIBE_ALREADY = (
    "ℹ️ 您已经订阅了信号推送。\n"
    "使用 /status 查看订阅详情。"
)

UNSUBSCRIBE_SUCCESS = (
    "✅ *已取消订阅。*\n\n"
    "不再收到信号推送。如需重新订阅，发送 /subscribe。"
)

HELP_MSG = (
    "❓ *帮助*\n\n"
    "*命令:*\n"
    "/subscribe — 📥 订阅信号\n"
    "/unsubscribe — 📤 取消订阅\n"
    "/status — 📋 查看状态\n"
    "/help — ❓ 显示此帮助\n\n"
    "*推送内容:*\n"
    "• 🚨 ENTRY: 强入场信号\n"
    "• ⚠️ CANDIDATE: 关注信号\n"
    "• 👀 WATCH: 观察信号\n"
    "• 📊 每日汇总\n\n"
    "🧪 Beta 版本，功能持续完善中。"
)

UNKNOWN_CMD = (
    "未知命令: `{cmd}`\n发送 /help 查看可用命令。"
)


# ── 数据库 ──────────────────────────────────────────────────────────────

def _get_db() -> Database:
    """获取数据库实例（复用项目已有的 Database 类）。"""
    db_path = BASE_DIR / "trading_system.db"
    return Database(str(db_path))


# ── Telegram API 工具 ──────────────────────────────────────────────────

def send_message(api_base: str, chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
    """发送消息到指定聊天。"""
    try:
        resp = requests.post(
            f"{api_base}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text[:4096],       # Telegram 单条消息上限 4096 字符
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            },
            timeout=8,
        )
        result = resp.json()
        ok = result.get("ok", False)
        if not ok:
            logger.warning("sendMessage 失败 [chat_id=%d]: %s", chat_id, result.get("description"))
        return ok
    except Exception as e:
        logger.error("sendMessage 异常 [chat_id=%d]: %s", chat_id, e)
        return False


# ── 命令处理器 ─────────────────────────────────────────────────────────

def handle_start(api_base: str, chat_id: int, user_name: str) -> None:
    """处理 /start — 欢迎消息 + 功能介绍 + 订阅引导。"""
    send_message(api_base, chat_id, WELCOME_MSG)
    logger.info("/start: chat_id=%d user=%s", chat_id, user_name)


def handle_subscribe(api_base: str, chat_id: int, user_name: str) -> None:
    """处理 /subscribe — 订阅信号推送。"""
    db = _get_db()
    mgr = BotSubscription(db)

    existing = mgr.get_subscriber(str(chat_id))
    if existing and existing.get("status") in ("trial", "active"):
        send_message(api_base, chat_id, SUBSCRIBE_ALREADY)
        logger.info("/subscribe: 重复订阅 chat_id=%d", chat_id)
        return

    ok = mgr.subscribe(str(chat_id), username=user_name)
    if ok:
        send_message(api_base, chat_id, SUBSCRIBE_SUCCESS)
        logger.info("/subscribe: 订阅成功 chat_id=%d user=%s", chat_id, user_name)
    else:
        send_message(api_base, chat_id, "❌ 订阅失败，请稍后重试。", parse_mode="")


def handle_unsubscribe(api_base: str, chat_id: int) -> None:
    """处理 /unsubscribe — 取消订阅。"""
    db = _get_db()
    mgr = BotSubscription(db)
    mgr.unsubscribe(str(chat_id))
    send_message(api_base, chat_id, UNSUBSCRIBE_SUCCESS)
    logger.info("/unsubscribe: 取消订阅 chat_id=%d", chat_id)


def handle_status(api_base: str, chat_id: int) -> None:
    """处理 /status — 查看订阅状态。"""
    db = _get_db()
    mgr = BotSubscription(db)
    sub = mgr.get_subscriber(str(chat_id))

    if sub:
        status = sub.get("status", "unknown")
        pushed = sub.get("signals_pushed", 0)
        subscribed_at = sub.get("subscribed_at", "unknown")
        status_msg = (
            f"📋 *订阅状态*\n\n"
            f"状态: {'✅ 活跃' if status in ('trial', 'active') else '❌ 已取消'}\n"
            f"已接收信号: {pushed} 条\n"
            f"订阅时间: {subscribed_at}\n\n"
            f"🧪 Beta | ⭐ Pro 即将推出"
        )
        send_message(api_base, chat_id, status_msg)
    else:
        send_message(
            api_base, chat_id,
            "❌ 您尚未订阅。发送 /subscribe 开始接收信号。\n\n"
            "🧪 Beta | ⭐ Pro 即将推出"
        )
    logger.info("/status: chat_id=%d sub=%s", chat_id, sub.get("status") if sub else "none")


# ── 主调度入口 ─────────────────────────────────────────────────────────

def handle_update(update: dict[str, Any], api_base: str) -> None:
    """处理单个 Telegram Update — 解析消息并路由到对应命令处理器。"""
    message = update.get("message")
    if not message:
        return

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    if not chat_id:
        return

    # 解析消息文本
    text = (message.get("text") or "").strip()
    user_name = chat.get("username", "") or chat.get("first_name", "")

    if not text:
        return

    # 命令路由（支持带参数的命令，如 /subscribe ru）
    cmd = text.split()[0].lower()

    handlers = {
        "/start": lambda: handle_start(api_base, chat_id, user_name),
        "/subscribe": lambda: handle_subscribe(api_base, chat_id, user_name),
        "/unsubscribe": lambda: handle_unsubscribe(api_base, chat_id),
        "/status": lambda: handle_status(api_base, chat_id),
        "/help": lambda: send_message(api_base, chat_id, HELP_MSG),
    }

    handler = handlers.get(cmd)
    if handler:
        handler()
    else:
        send_message(api_base, chat_id, UNKNOWN_CMD.format(cmd=cmd.split()[0]))