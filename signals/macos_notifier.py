"""
macOS 本地桌面推送通知模块。

通过 ``osascript`` 调用 AppleScript ``display notification`` 显示通知，
该命令使用 macOS 现代通知 API（UNUserNotificationCenter），兼容 macOS 10.8+。

无需任何配置，系统内置可用。

依赖: macOS 系统，Python 标准库（无需第三方包）
"""

import json
import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


def _notify_osascript(
    title: str,
    subtitle: str,
    text: str,
    sound: bool = False,
) -> bool:
    """通过 osascript AppleScript ``display notification`` 发送通知。

    使用 AppleScript 内置命令，底层调度到 UNUserNotificationCenter。
    比 NSUserNotification (deprecated since macOS 11) 兼容性更好。

    Args:
        title: 通知标题。
        subtitle: 副标题。
        text: 正文内容。
        sound: 是否播放提示音。

    Returns:
        True 发送成功。
    """
    # 用 JSON 转义确保 Unicode/emoji 兼容
    safe_subtitle = json.dumps(subtitle)
    safe_text = json.dumps(text)
    safe_title = json.dumps(title)

    # AppleScript display notification 使用 UNUserNotificationCenter
    parts = [f"display notification {safe_text} with title {safe_title} subtitle {safe_subtitle}"]
    if sound:
        parts.append("sound name \"default\"")
    script = " ".join(parts)

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0
    except FileNotFoundError:
        logger.debug("osascript 不可用（非 macOS 环境）")
        return False
    except subprocess.TimeoutExpired:
        logger.debug("osascript 超时")
        return False
    except Exception as e:
        logger.debug("osascript 异常: %s", e)
        return False


def notify(
    title: str,
    subtitle: str = "",
    text: str = "",
    sound: bool = False,
) -> bool:
    """发送 macOS Notification Center 通知。

    Args:
        title: 通知标题（粗体显示）。
        subtitle: 副标题（小字）。
        text: 正文内容。
        sound: 是否播放提示音，默认 False。

    Returns:
        True 通知发送成功，False 失败（非 macOS / osascript 不可用）。
    """
    # 用 AppleScript display notification（底层 UNUserNotificationCenter）
    ok = _notify_osascript(title, subtitle, text, sound)
    if ok:
        logger.info("macOS 通知已发送: %s - %s", title, subtitle)
    return ok


def notify_signal_summary(
    futures_entry: int = 0,
    futures_candidate: int = 0,
    options_entry: int = 0,
    options_candidate: int = 0,
    total_scanned: int = 0,
    sound: bool = False,
) -> bool:
    """发送信号扫描摘要到 macOS 通知中心。

    Args:
        futures_entry: 期货 ENTRY 信号数。
        futures_candidate: 期货 CANDIDATE 信号数。
        options_entry: 期权 ENTRY 信号数。
        options_candidate: 期权 CANDIDATE 信号数。
        total_scanned: 扫描品种总数。
        sound: 有信号时是否播放提示音。

    Returns:
        True 通知发送成功。
    """
    total_signals = futures_entry + futures_candidate + options_entry + options_candidate
    if total_signals == 0:
        return notify(
            title="期权期货系统",
            subtitle=f"扫描完成 · {total_scanned} 品种",
            text="无新信号",
        )

    parts = []
    if futures_entry:
        parts.append(f"期货🚨{futures_entry}")
    if futures_candidate:
        parts.append(f"期货⚠️{futures_candidate}")
    if options_entry:
        parts.append(f"期权🚨{options_entry}")
    if options_candidate:
        parts.append(f"期权⚠️{options_candidate}")

    return notify(
        title="期权期货系统",
        subtitle=f"发现 {total_signals} 个信号 · {total_scanned} 品种扫描",
        text=" | ".join(parts),
        sound=sound or (futures_entry + options_entry > 0),
    )
