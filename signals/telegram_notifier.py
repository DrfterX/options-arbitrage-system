"""
Telegram 推送通知模块。

通过 Bot API 推送交易信号通知。支持 **多用户订阅**：
- 推送时遍历所有活跃订阅者，逐人发送
- 支持单用户测试（指定 chat_id）
- 静默跳过未配置 Bot Token 的环境

配置文件在项目根目录 .env：
    TELEGRAM_BOT_TOKEN=your_bot_token
    TELEGRAM_CHAT_ID=your_chat_id         # 兼容旧版单用户配置

如未配置则静默跳过（不报错），方便无 token 环境使用。
"""

import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# 从环境变量读取配置
_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() or None
_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID", "").strip() or None

_API_BASE = "https://api.telegram.org/bot{token}/sendMessage"
_TIMEOUT = 8  # 秒


def _is_configured() -> bool:
    """检查 Telegram Bot Token 是否已配置。

    Returns:
        True 当 BOT_TOKEN 已设置。
    """
    return bool(_BOT_TOKEN)


def send_message(
    text: str,
    parse_mode: str = "Markdown",
    chat_id: Optional[str] = None,
) -> bool:
    """发送文本消息到指定 Telegram 聊天。

    如果提供了 chat_id 则发送给该用户；
    否则使用旧版单用户模式（TELEGRAM_CHAT_ID）。

    Args:
        text: 消息内容（最长 4096 字符，超出自动截断）。
        parse_mode: 解析模式，默认 ``'Markdown'``，可选 ``'HTML'`` 或 ``''``。
        chat_id: 目标聊天 ID。为 None 时使用 TELEGRAM_CHAT_ID。

    Returns:
        True 发送成功，False 配置缺失或发送失败。
    """
    target_chat = chat_id or _CHAT_ID
    if not _BOT_TOKEN or not target_chat:
        logger.debug(
            "Telegram 未配置 (BOT_TOKEN=%s CHAT_ID=%s)，跳过推送",
            bool(_BOT_TOKEN), bool(target_chat),
        )
        return False

    url = _API_BASE.format(token=_BOT_TOKEN)
    payload = {
        "chat_id": target_chat,
        "text": text[:4096],  # Telegram 限制 4096 字符
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if data.get("ok"):
            logger.info("Telegram 推送成功: chat=%s %d 字符", target_chat, len(text))
            return True
        else:
            logger.warning("Telegram API 返回错误: %s", data.get("description", "未知"))
            return False
    except requests.RequestException as e:
        logger.warning("Telegram 推送失败 (网络错误): %s", e)
        return False


def broadcast(text: str, parse_mode: str = "Markdown") -> int:
    """广播消息给所有活跃订阅者。

    自动从 bot_subscribers 表获取活跃用户列表，
    逐人发送消息并更新推送计数。

    Args:
        text: 消息内容。
        parse_mode: 解析模式。

    Returns:
        发送成功的用户数。
    """
    try:
        from core.db import Database
        from signals.bot_subscription import BotSubscription

        db = Database(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "trading_system.db"
        ))
        mgr = BotSubscription(db)
        subscribers = mgr.get_active_subscribers()
    except Exception as e:
        logger.error("获取订阅者列表失败: %s", e)
        # 回退到单用户模式
        if send_message(text, parse_mode):
            return 1
        return 0

    if not subscribers:
        logger.info("broadcast: 无活跃订阅者，跳过")
        # 即使无订阅者也发送给管理员（兼容旧版）
        if _CHAT_ID and send_message(text, parse_mode, chat_id=_CHAT_ID):
            return 1
        return 0

    success = 0
    for sub in subscribers:
        chat_id = sub.get("telegram_chat_id")
        if not chat_id:
            continue
        try:
            if send_message(text, parse_mode, chat_id=chat_id):
                mgr.record_push(chat_id)
                success += 1
        except Exception as e:
            logger.error("广播失败 chat=%s: %s", chat_id, e)

    logger.info("broadcast: %d/%d 用户推送成功", success, len(subscribers))
    return success


def send_message_to_user(text: str, chat_id: str, parse_mode: str = "Markdown") -> bool:
    """发送消息给指定用户（不经过订阅列表）。

    Args:
        text: 消息内容。
        chat_id: 目标 Chat ID。
        parse_mode: 解析模式。

    Returns:
        True 发送成功。
    """
    return send_message(text, parse_mode=parse_mode, chat_id=chat_id)


def send_signal(
    symbol: str,
    direction: str,
    signal_type: str,
    score: float,
    contract: str = "",
    entry_price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    details: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> bool:
    """发送交易信号通知。

    Args:
        symbol: 品种代码，如 'RB'。
        direction: 方向，'LONG' 或 'SHORT'。
        signal_type: 信号等级，'ENTRY' / 'CANDIDATE' / 'WATCH'。
        score: 评分 (0~1)。
        contract: 合约代码，如 'rb2510'。
        entry_price: 入场价格。
        stop_loss: 止损价格。
        take_profit: 止盈价格。
        details: 附加详情文本。
        chat_id: 目标 Chat ID（None 则用旧版单用户模式）。

    Returns:
        True 发送成功，False 配置缺失或失败。
    """
    dir_cn = "🟢 做多" if direction == "LONG" else ("🔴 做空" if direction == "SHORT" else "⚪ 观望")
    level_icon = {"ENTRY": "🚨", "CANDIDATE": "⚠️", "WATCH": "👀"}.get(signal_type, "📊")

    lines = [
        f"{level_icon} *{symbol}* {dir_cn}",
        f"   等级: {signal_type}  |  评分: {score:.2f}",
    ]
    if contract:
        lines.append(f"   合约: {contract}")
    if entry_price is not None:
        ep = f"入场: {entry_price:.1f}"
        if stop_loss is not None:
            ep += f"  止损: {stop_loss:.1f}"
        if take_profit is not None:
            ep += f"  止盈: {take_profit:.1f}"
        lines.append(f"   {ep}")
    if details:
        lines.append(f"   {details}")

    text = "\n".join(lines)
    return send_message(text, parse_mode="Markdown", chat_id=chat_id)


def send_daily_summary(summary_text: str, chat_id: Optional[str] = None) -> bool:
    """发送日报总结。

    Args:
        summary_text: 格式化后的日报文本。
        chat_id: 目标 Chat ID（None 则用旧版单用户模式）。

    Returns:
        True 发送成功，False 配置缺失或失败。
    """
    # 日报通常较长，在前面加个标题
    header = "📊 *Auto Company 日报*\n\n"
    return send_message(header + summary_text, parse_mode="Markdown", chat_id=chat_id)


# 快捷函数 — 只在配置齐全时可用
__all__ = [
    "send_message",
    "send_signal",
    "send_daily_summary",
    "send_message_to_user",
    "broadcast",
]