"""
分级推送调度函数 dispatch。

支持按信号等级和推送模式输出消息。

等级定义:
    - URGENT: 立即推送（ENTRY 信号）
    - DAILY: 汇总推送（日报/EOD）
    - WATCH/CANDIDATE/ENTRY: 对应三级信号

模式:
    - stdout: 通过 print 输出（供 cron 管道捕获）
    - 预留: wechat/webhook 等
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


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
        mode: 推送模式，当前支持 ``'stdout'``。
        webhook_url: webhook URL（预留，mode='wechat' 时使用）。

    Raises:
        ValueError: 无效的 mode 参数。
    """
    if mode == "stdout":
        # stdout 模式：直接 print，供 cron 管道捕获
        print(msg)
        logger.debug("dispatch: level=%s mode=stdout len=%d", level, len(msg))
    elif mode in ("wechat", "webhook"):
        # 预留：webhook 推送
        if webhook_url:
            logger.info(
                "dispatch: level=%s mode=%s webhook=%s (预留，尚未实现)",
                level, mode, webhook_url,
            )
            # TODO: 实现 webhook POST 推送
        else:
            logger.warning(
                "dispatch: mode=%s 但未提供 webhook_url，回退到 stdout", mode
            )
            print(msg)
    else:
        raise ValueError(f"不支持的推送模式: {mode}，可选: stdout, wechat")
