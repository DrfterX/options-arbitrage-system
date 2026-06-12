"""
统一全局配置 — 合并期货N型信号系统与期权套利系统的所有配置参数。

所有路径以 PROJECT_ROOT 为基准相对定位。
时间戳统一存储 Unix 秒（UTC），显示时转换为 Asia/Shanghai。
"""

import os
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

# ============================================================
# .env 文件自动加载（纯 Python 实现，不依赖 python-dotenv）
# ============================================================
def _load_dotenv() -> None:
    """加载项目根目录的 .env 文件到环境变量（若存在）。

    .env 文件格式：
        KEY=VALUE            # 基本赋值
        export KEY=VALUE     # Bash export 语法（兼容）
        # 注释行              # 注释
        空行跳过

    已存在的环境变量不会被覆盖（os.environ 优先级高于 .env 文件）。
    """
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 去掉 export 前缀（兼容 bash export 语法）
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # 去掉引号
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key and key not in os.environ:
                os.environ[key] = value


# ============================================================
# 路径
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "trading_system.db"
LOG_PATH = PROJECT_ROOT / "trading_system.log"

# 加载 .env 文件（环境变量优先级高于 .env）
_load_dotenv()

# ============================================================
# 时区
# ============================================================
MARKET_TZ = ZoneInfo("Asia/Shanghai")

# ============================================================
# 交易日历（仅用于 cron，盘中判断由 pipeline 自行处理）
# ============================================================
TRADING_CALENDAR = {
    "day_start": "09:00",
    "day_end": "15:00",
    "night_start": "21:00",
    "night_end": "23:00",
}

# ============================================================
# 数据源配置
# ============================================================
DATA_SOURCE = "akshare"
SINA_API_TIMEOUT = 10
SINA_API_RETRY = 3
AKSHARE_TIMEOUT = 5
AKSHARE_RETRY = 2
SLEEP_INTERVAL = 0.3  # Sina 限流间隔

# ============================================================
# 数据验证
# ============================================================
DATA_VALIDATION = {
    "futures_price_min": 1,
    "futures_price_max": 1000000,
    "options_price_min": 0.01,
    "options_price_max": 10000,
    "min_options_count": 4,
}

# ============================================================
# 品种筛选门槛
# ============================================================
FUTURES_OI_MIN = 50000
OPTIONS_OI_MIN = 300
MIN_OI = 300
MIN_IV = 0.25  # 小数，即 25%
MAX_DELTA_ABS = 0.10
MAX_MARGIN = 10000
MARGIN_MAX = 10000
MAX_COST_RATIO = 0.05
MIN_WIN_RATE = 0.50

# ============================================================
# 策略参数
# ============================================================
STRATEGY_PARAMS = {
    "volatility_threshold": 0.3,
    "volatility_percentile_threshold": 0.8,
    "delta_neutral_tolerance": 0.1,
    "spread_threshold": 0.02,
    "position_limit": 100,
    "profit_target": 0.05,
    "stop_loss": 0.1,
}

# ============================================================
# MACD 参数（两色方案：红柱=MACD>0多头，蓝柱=MACD<0空头）
# ============================================================
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
COLOR_RED = "RED"
COLOR_BLUE = "BLUE"

# ============================================================
# 波峰波谷检测窗口 n 值
# ============================================================
SWING_WINDOWS = {
    "3m": 3,
    "15m": 3,
    "1h": 4,
    "1d": 5,
    "1w": 2,
}

# ============================================================
# detect_and_save 滑动窗口（避免历史极值干扰 N 型状态机）
# ============================================================
DETECT_WINDOWS = {
    "15m": 20,
    "1h": 25,
    "1d": 30,
    "1w": 40,
}

# ============================================================
# 三级嵌套验证配置
# ============================================================
LEVEL1_TIMEFRAME = "1w"
LEVEL1_MACD_TIMEFRAME = "1d"
LEVEL2_TIMEFRAME = "1h"
LEVEL2_MACD_TIMEFRAME = "15m"
LEVEL3_TIMEFRAME = "15m"
LEVEL3_STABILITY_TIMEFRAME = "15m"
LEVEL3_STABILITY_WINDOW = 8
LEVEL3_STABILITY_MAX_SWITCHES = 3

# ============================================================
# MACD 轨迹验证参数
# ============================================================
TRANSITION_WINDOW_BEFORE = 3
TRANSITION_WINDOW_AFTER = 3

# ============================================================
# 加分项配置
# ============================================================
BONUS_CHECKS = [
    ("1mon", "1w", 0.15),
    ("1d", "1h", 0.10),
]

# ============================================================
# 三级验证评分门槛
# ============================================================
LEVEL1_MIN_SCORE = 0.3
LEVEL2_MIN_SCORE = 0.6
LEVEL3_MIN_SCORE = 1.0

# ============================================================
# 推送配置
# ============================================================
PUSH_CONFIG = {
    "enabled": True,
    "channels": ["stdout"],  # 通过 cron stdout 管道推送到微信
}
DEDUP_HOURS = 12
PUSHED_LOG = os.path.expanduser("~/.hermes/options_pushed.json")

# ── Telegram Bot 配置（推送实时信号用）─────────────────────
# 参考：https://core.telegram.org/bots/api
# 创建 Bot: @BotFather → /newbot → 获取 token
# 获取 chat_id: 给 bot 发消息后访问 https://api.telegram.org/bot<token>/getUpdates
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")  # 例: "123456:ABC-DEF1234..."
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")      # 例: "-1001234567890"

# ============================================================
# 监控配置
# ============================================================
MONITOR_INTERVAL = 60
SCAN_LIMIT = 15

# ============================================================
# 回测 IV 策略映射
# ============================================================
IV_STRATEGY_MAP = {
    "极端高": ["iron_condor", "short_strangle", "ratio_spread"],
    "偏高": ["ratio_spread", "short_strangle"],
    "正常": ["ratio_spread"],
}

# ============================================================
# AKShare 周期映射
# ============================================================
AKSHARE_PERIODS = ["1m", "15m", "1h", "1d", "1w"]
PERIOD_MAP_SINA = {
    "1m": "1", "5m": "5", "15m": "15", "30m": "30",
    "60m": "60", "1h": "60", "D": "D", "1d": "D",
    "W": "W", "1w": "W", "M": "M",
}

# ============================================================
# 日志
# ============================================================
LOG_LEVEL = "INFO"
