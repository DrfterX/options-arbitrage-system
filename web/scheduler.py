"""
轻量级后台调度器 — 定期自动触发数据采集 + N 型重算。

作为 daemon 线程与 Flask 应用并行运行。
使用 system_config 表（DB 级 key-value）做分布式锁，
防止 gunicorn 多 worker 下重复执行。

调度策略：
  - 每 5 分钟检查一次是否达到刷新间隔
  - 刷新间隔根据交易时段自适应调整：
    - 交易时段：30 分钟
    - 交易日间隙（15:00-21:00 / 23:00-09:00）：2 小时
    - 非交易日（周末/节假日）：6 小时
  - 启动后随机延迟 0~120s，让多个 worker 错开
"""

import logging
import random
import threading
import time

logger = logging.getLogger(__name__)

# ── 配置 ──────────────────────────────────────────────────────────
CHECK_INTERVAL = 5 * 60         # 调度器检查周期（秒）
STARTUP_DELAY_MAX = 120         # 启动随机延迟上限（秒）

# ── 会话→刷新间隔映射（懒加载，避免 import 环）────────────────────
_INTERVAL_CACHE = None

def _get_refresh_intervals():
    """懒加载 REFRESH_INTERVALS（延迟 import，避免模块加载时环依赖）。"""
    global _INTERVAL_CACHE
    if _INTERVAL_CACHE is None:
        from config.settings import REFRESH_INTERVALS as _ri
        _INTERVAL_CACHE = _ri
    return _INTERVAL_CACHE


def _get_current_session():
    """懒加载 get_current_session（延迟 import）。"""
    from core.market_calendar import get_current_session as _gcs
    return _gcs()


def _session_refresh_interval() -> int:
    """根据当前交易时段返回对应的刷新间隔（秒）。"""
    session = _get_current_session()
    intervals = _get_refresh_intervals()

    if session == "day":
        return intervals["day"]
    elif session == "night":
        return intervals["night"]
    else:
        # closed — 判断是否为交易日间隙还是非交易日
        from core.market_calendar import is_trading_day
        if is_trading_day():
            return intervals["gap"]    # 交易日间隙（15:00-21:00 或 23:00-09:00）
        return intervals["holiday"]    # 非交易日（周末/节假日）


# system_config key 名称
_KEY_LAST_RUN = "scheduler_last_run"
_KEY_RUNNING  = "scheduler_running"


def _needs_refresh(db) -> bool:
    """检查是否到达刷新时间（按当前交易时段对应的间隔判断）。"""
    conn = db.get_conn()
    row = conn.execute(
        "SELECT value FROM system_config WHERE key = ?", (_KEY_LAST_RUN,)
    ).fetchone()
    if row is None:
        return True  # 从未运行过
    last_run = float(row[0])
    interval = _session_refresh_interval()
    return (time.time() - last_run) >= interval


def _try_acquire_lock(db) -> bool:
    """尝试获取执行锁。成功返回 True。"""
    conn = db.get_conn()
    row = conn.execute(
        "SELECT value FROM system_config WHERE key = ?", (_KEY_RUNNING,)
    ).fetchone()
    if row and row[0] == "1":
        return False  # 另一 worker 正在运行
    conn.execute(
        "INSERT OR REPLACE INTO system_config (key, value, updated_at) "
        "VALUES (?, '1', datetime('now'))",
        (_KEY_RUNNING,),
    )
    conn.commit()
    return True


def _release_lock(db) -> None:
    """释放执行锁。"""
    conn = db.get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO system_config (key, value, updated_at) "
        "VALUES (?, '0', datetime('now'))",
        (_KEY_RUNNING,),
    )
    conn.commit()


def _update_last_run(db) -> None:
    """记录本轮运行时间。"""
    conn = db.get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO system_config (key, value, updated_at) "
        "VALUES (?, ?, datetime('now'))",
        (_KEY_LAST_RUN, str(time.time())),
    )
    conn.commit()


def _do_refresh(db) -> None:
    """执行全品种数据采集 + N 型重算。"""
    from data.futures_collector import FuturesCollector
    from config.contracts import ContractRegistry
    from config.settings import DB_PATH

    logger.info("🔄 [调度器] 开始周期性数据采集...")

    try:
        registry = ContractRegistry(str(DB_PATH))
        collector = FuturesCollector(db, registry)
        stats = collector.collect_all(
            period_map={"15m": "15", "1h": "60", "1d": "D"},
            trigger_restructure=True,
        )

        total_fetched = sum(
            tf_stats.get("fetched", 0)
            for sym_stats in stats.values()
            for tf_stats in sym_stats.values()
        )
        total_saved = sum(
            tf_stats.get("saved", 0)
            for sym_stats in stats.values()
            for tf_stats in sym_stats.values()
        )

        logger.info(
            "✅ [调度器] 周期采集完成: %d 品种, %d 获取, %d 新增保存",
            len(stats), total_fetched, total_saved,
        )
    except Exception as e:
        logger.error("❌ [调度器] 采集异常: %s", e)


def _session_label() -> str:
    """返回当前会话状态的友好标签（用于日志）。"""
    session = _get_current_session()
    interval = _session_refresh_interval()
    from core.market_calendar import is_trading_day
    if session == "closed" and is_trading_day():
        return f"closed (交易日间隙, 刷新间隔: {interval//60}分钟)"
    elif session == "closed":
        return f"closed (非交易日, 刷新间隔: {interval//60}分钟)"
    else:
        return f"{session} (交易时段, 刷新间隔: {interval//60}分钟)"


def _scheduler_loop(db) -> None:
    """调度器主循环。"""
    # 启动随机延迟 — 让多个 gunicorn worker 错开
    delay = random.uniform(0, STARTUP_DELAY_MAX)
    logger.info("⏳ [调度器] 启动延迟 %.0f 秒", delay)
    time.sleep(delay)

    # 启动时输出当前会话状态
    logger.info("📊 [调度器] 当前会话: %s", _session_label())

    while True:
        try:
            if _needs_refresh(db):
                if _try_acquire_lock(db):
                    try:
                        _do_refresh(db)
                        _update_last_run(db)
                    finally:
                        _release_lock(db)
                else:
                    logger.debug("[调度器] 锁被占用，跳过本轮")
            else:
                logger.debug("[调度器] 未到刷新时间，跳过")
        except Exception as e:
            logger.warning("[调度器] 检查异常: %s", e)

        time.sleep(CHECK_INTERVAL)


# ── 5s 增量重算心跳线程 ──────────────────────────────────────────

HEARTBEAT_INTERVAL = 5  # 心跳间隔（秒）


def _incremental_heartbeat_loop(db) -> None:
    """增量重算心跳循环 — 每 5 秒执行轻量 N 型结构状态迁移。

    独立于 ``_scheduler_loop()`` 运行，两者互不阻塞。
    本线程仅调用 ``restructure_all_active_incremental()``，跳过
    ``detect_and_save`` 全量扫描，每轮正常在数毫秒内完成。

    和主调度器的关系：
    - 主调度器负责全量数据采集 + 全量重算（30min~6h 一次）
    - 心跳线程负责新 K 线写入后的增量状态迁移（5s 一次）
    - 采集线程写入新 K 线后，心跳线程最快 5s 内重算 N 型结构
    """
    # 延迟 import 避免模块加载时环依赖
    from futures.n_structure import restructure_all_active_incremental as _recalc

    logger.info("💓 [心跳] 增量重算心跳线程启动（每 %d 秒）", HEARTBEAT_INTERVAL)

    while True:
        try:
            _recalc(db)
        except Exception as e:
            logger.warning("[心跳] 增量重算异常（已跳过）: %s", e)

        time.sleep(HEARTBEAT_INTERVAL)


def start_incremental_heartbeat(db) -> threading.Thread:
    """启动增量重算心跳线程（daemon 线程）。

    与 ``start_scheduler()`` 并行运行，两者互不阻塞。

    本函数在 :mod:`web.app` 中被调用，用法：:

        from web.scheduler import start_scheduler, start_incremental_heartbeat
        start_scheduler(db)
        start_incremental_heartbeat(db)
    """
    t = threading.Thread(
        target=_incremental_heartbeat_loop,
        args=(db,),
        daemon=True,
        name="n-structure-heartbeat",
    )
    t.start()
    logger.info("✅ 增量重算心跳线程已启动（间隔 %d 秒）", HEARTBEAT_INTERVAL)
    return t


def start_scheduler(db) -> threading.Thread:
    """启动后台调度器（daemon 线程）。

    在 gunicorn import 时每个 worker 都会调用此函数，
    但 daemon 线程 + DB 锁保证仅第一个执行采集逻辑。
    """
    t = threading.Thread(
        target=_scheduler_loop,
        args=(db,),
        daemon=True,
        name="data-refresh-scheduler",
    )
    t.start()
    session_info = _session_label()
    logger.info(
        "✅ 自适应调度器已启动（每 %d 分钟检查一次，当前会话: %s）",
        CHECK_INTERVAL // 60, session_info,
    )
    return t
