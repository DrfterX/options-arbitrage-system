"""
Telegram 推送通知模块。

通过 Bot API 推送交易信号通知。
配置文件在项目根目录 .env：
    TELEGRAM_BOT_TOKEN=your_bot_token
    TELEGRAM_CHAT_ID=your_chat_id

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
    """检查 Telegram 推送是否已配置。

    Returns:
        True 当 BOT_TOKEN 和 CHAT_ID 均已设置。
    """
    return bool(_BOT_TOKEN and _CHAT_ID)


def send_message(text: str, parse_mode: str = "Markdown") -> bool:
    """发送文本消息到已配置的 Telegram 聊天。

    Args:
        text: 消息内容（最长 4096 字符，超出自动截断）。
        parse_mode: 解析模式，默认 ``'Markdown'``，可选 ``'HTML'`` 或 ``''``。

    Returns:
        True 发送成功，False 配置缺失或发送失败。
    """
    if not _is_configured():
        logger.debug("Telegram 未配置 (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID)，跳过推送")
        return False

    url = _API_BASE.format(token=_BOT_TOKEN)
    payload = {
        "chat_id": _CHAT_ID,
        "text": text[:4096],  # Telegram 限制 4096 字符
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if data.get("ok"):
            logger.info("Telegram 推送成功: %d 字符", len(text))
            return True
        else:
            logger.warning("Telegram API 返回错误: %s", data.get("description", "未知"))
            return False
    except requests.RequestException as e:
        logger.warning("Telegram 推送失败 (网络错误): %s", e)
        return False


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
    return send_message(text, parse_mode="Markdown")


def send_daily_summary(summary_text: str) -> bool:
    """发送日报总结。

    Args:
        summary_text: 格式化后的日报文本。

    Returns:
        True 发送成功，False 配置缺失或失败。
    """
    # 日报通常较长，在前面加个标题
    header = "📊 *Auto Company 日报*\n\n"
    return send_message(header + summary_text, parse_mode="Markdown")


# 快捷函数 — 只在配置齐全时可用
__all__ = [
    "send_message",
    "send_signal",
    "send_daily_summary",
    "send_alert",
]