"""
分级推送调度函数 dispatch。

支持按信号等级和推送模式输出消息。

等级定义:
    - URGENT: 立即推送（ENTRY 信号）
    - DAILY: 汇总推送（日报/EOD）
    - WATCH/CANDIDATE/ENTRY: 对应三级信号

模式:
    - stdout: 通过 print 输出（供 cron 管道捕获）
    - webhook: HTTP POST 到 webhook_url（Telegram Bot / 企业微信等）
    - telegram: 通过 Bot API 发送消息
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional

logger = logging.getLogger(__name__)


def _telegram_send(bot_token: str, chat_id: str, msg: str) -> bool:
    """通过 Telegram Bot API 发送消息。

    Args:
        bot_token: Bot Token（从 settings 获取）。
        chat_id: 目标聊天 ID。
        msg: 消息文本。

    Returns:
        True 表示发送成功。
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            result = json.loads(body)
            if result.get("ok"):
                logger.info("Telegram 推送成功 (len=%d)", len(msg))
                return True
            else:
                logger.warning("Telegram 推送返回异常: %s", body)
                return False
    except urllib.error.HTTPError as e:
        logger.error("Telegram HTTP %s: %s", e.code, e.read().decode()[:200])
        return False
    except Exception as e:
        logger.error("Telegram 网络异常: %s", e)
        return False


def _webhook_post(url: str, msg: str) -> bool:
    """通用 webhook POST 推送（支持企业微信、自定义回调等）。

    Args:
        url: Webhook URL。
        msg: 消息文本。

    Returns:
        True 表示发送成功。
    """
    payload = json.dumps({"msgtype": "text", "text": {"content": msg}}).encode("utf-8")
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            logger.info("Webhook 推送成功 (len=%d, status=%d)", len(msg), resp.status)
            return True
    except urllib.error.HTTPError as e:
        logger.error("Webhook HTTP %s: %s", e.code, e.read().decode()[:200])
        return False
    except Exception as e:
        logger.error("Webhook 网络异常: %s", e)
        return False


def dispatch(
    msg: str,
    level: str = "DAILY",
    mode: str = "stdout",
    webhook_url: Optional[str] = None,
) -> None:
    """按级别和模式推送消息。

    Args:
        msg: 要推送的消息内容。
        level: 信号等级，取 ``'WATCH'`` / ``'CANDIDATE'`` / ``'ENTRY'`` / ``'DAILY'``。
        mode: 推送模式，当前支持 ``'stdout'`` / ``'webhook'`` / ``'telegram'``。
        webhook_url: webhook URL（mode='webhook' 时使用；mode='telegram' 时作为 bot_token）。

    Raises:
        ValueError: 无效的 mode 参数。
    """
    if mode == "stdout":
        # stdout 模式：直接 print，供 cron 管道捕获
        print(msg)
        logger.debug("dispatch: level=%s mode=stdout len=%d", level, len(msg))

    elif mode == "telegram":
        # Telegram Bot 推送：webhook_url 被复用为 bot_token 以提高兼容性
        # 优先从 settings 获取 token/chat_id
        try:
            from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
            bot_token = TELEGRAM_BOT_TOKEN or webhook_url or ""
            chat_id = TELEGRAM_CHAT_ID or ""
        except (ImportError, AttributeError):
            bot_token = webhook_url or ""
            chat_id = ""

        if bot_token and chat_id:
            _telegram_send(bot_token, chat_id, msg)
        else:
            logger.warning(
                "dispatch: mode=telegram 但未配置 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID，"
                "回退到 stdout"
            )
            print(msg)

    elif mode in ("wechat", "webhook"):
        # 通用 webhook 推送
        if webhook_url:
            _webhook_post(webhook_url, msg)
        else:
            logger.warning(
                "dispatch: mode=%s 但未提供 webhook_url，回退到 stdout", mode
            )
            print(msg)
    else:
        raise ValueError(f"不支持的推送模式: {mode}，可选: stdout, webhook, telegram")
