"""
信号推送适配器 — 在扫描完成后触发广播。

orchestrator.py 已内置广播调用（扫描结束后自动推送 ENTRY 信号 + 日报），
此文件提供独立触发能力，用于定时调度或手动触发批量推送。

用法（手动触发）:
    python scripts/bot_signal_push.py --mode all
"""

import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from signals.telegram_notifier import broadcast

logger = logging.getLogger(__name__)


def push_signals_if_enabled(mode: str = "all") -> int:
    """扫描完成后推送信号给所有订阅用户。

    Args:
        mode: 扫描模式 (all/futures/options)

    Returns:
        成功推送的用户数
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token or token == "PLACEHOLDER":
        logger.info("TELEGRAM_BOT_TOKEN 未配置，跳过推送")
        return 0

    label = {"all": "全品种", "futures": "期货", "options": "期权"}.get(mode, mode)
    msg = f"📊 *Drifter 信号更新 ({label})*\n\n扫描完成，查看最新信号。\n🌐 https://futures.drifter.indevs.in"
    count = broadcast(msg)
    logger.info("信号广播完成: %d 用户推送", count)
    return count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="信号推送触发脚本")
    parser.add_argument("--mode", default="all", choices=["all", "futures", "options"])
    args = parser.parse_args()

    count = push_signals_if_enabled(mode=args.mode)
    print(f"推送完成: {count} 用户")