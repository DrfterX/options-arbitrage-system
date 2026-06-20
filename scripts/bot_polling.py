"""
Bot 轮询主循环 — pm2 进程，持续运行。

使用 Telegram Bot API 的 getUpdates long polling 模式：
每 2 秒轮询一次，用 offset 追踪已处理的 update_id，重启不丢消息。

用法:
    pm2 start scripts/bot_polling.py --interpreter .venv/bin/python --name "bot-polling"

配置:
    TELEGRAM_BOT_TOKEN (在 .env 中)
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

import requests

# 确保项目根在路径中（项目根 = 父目录的父目录）
PROJECT_DIR = Path(__file__).resolve().parent.parent
# 项目根（auto-company_test/ — 包含 .env 文件）
REPO_ROOT = PROJECT_DIR.parent.parent

sys.path.insert(0, str(PROJECT_DIR))

from signals.bot_handler import handle_update

logger = logging.getLogger(__name__)

# ── 配置 ─────────────────────────────────────────────────────────────
POLL_INTERVAL = 2          # 秒 — 轮询间隔
API_BASE = "https://api.telegram.org/bot{token}"
OFFSET_FILE = PROJECT_DIR / ".bot_offset"
ENV_FILE = REPO_ROOT / ".env"


def _get_token() -> str:
    """从环境变量或 .env 文件读取 TELEGRAM_BOT_TOKEN。"""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        # 尝试从 .env 加载
        try:
            from dotenv import load_dotenv
            load_dotenv(ENV_FILE)
        except ImportError:
            # 手动解析 .env
            if ENV_FILE.exists():
                for line in ENV_FILE.read_text().splitlines():
                    line = line.strip()
                    if line.startswith("TELEGRAM_BOT_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        token = os.getenv("TELEGRAM_BOT_TOKEN", token or "").strip()
    return token


def _load_offset() -> int:
    """从文件加载上次处理的 update_id（重启后不重复处理）。"""
    try:
        return int(OFFSET_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


def _save_offset(offset: int) -> None:
    """持久化当前 update_id（避免重启丢消息）。"""
    OFFSET_FILE.write_text(str(offset))


def poll_loop() -> None:
    """主轮询循环。"""
    token = _get_token()
    if not token or token == "PLACEHOLDER":
        logger.error("TELEGRAM_BOT_TOKEN 未配置！请在 .env 中设置 TELEGRAM_BOT_TOKEN")
        logger.error("Token 获取方式: Telegram @BotFather → /newbot")
        return

    api = API_BASE.format(token=token)
    offset = _load_offset()
    logger.info("Bot 轮询启动 | offset=%d | 项目根=%s", offset, PROJECT_DIR)

    # 启动前验证 Token 有效性
    try:
        me = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=8)
        if me.json().get("ok"):
            info = me.json().get("result", {})
            logger.info("Bot 身份已验证: @%s (%s)", info.get("username"), info.get("first_name"))
        else:
            logger.warning("Token 验证失败: %s", me.json().get("description"))
    except Exception as e:
        logger.warning("Token 验证请求失败（不影响轮询启动）: %s", e)

    while True:
        try:
            resp = requests.get(
                f"{api}/getUpdates",
                params={
                    "offset": offset + 1,          # 确认已处理的 update
                    "timeout": 10,                  # long polling（减少空响应）
                    "allowed_updates": json.dumps(["message", "callback_query"]),
                },
                timeout=15,
            )
            data = resp.json()

            if not data.get("ok"):
                logger.warning("getUpdates 返回错误: %s", data.get("description"))
                time.sleep(POLL_INTERVAL * 2)
                continue

            updates = data.get("result", [])
            for update in updates:
                update_id = update.get("update_id", 0)
                if update_id <= offset:
                    continue
                try:
                    handle_update(update, api)
                except Exception as e:
                    logger.exception("处理 update %d 失败: %s", update_id, e)
                offset = update_id
                _save_offset(offset)

        except requests.exceptions.Timeout:
            # Long polling 超时是正常的（无消息时 Telegram 保持连接直到 timeout）
            continue
        except requests.exceptions.ConnectionError as e:
            logger.warning("网络连接失败，5 秒后重试: %s", e)
            time.sleep(5)
            continue
        except Exception as e:
            logger.exception("轮询循环异常: %s", e)
            time.sleep(POLL_INTERVAL * 3)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    poll_loop()