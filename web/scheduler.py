"""
轻量级后台调度器 — 定期自动触发数据采集 + N 型重算。

作为 daemon 线程与 Flask 应用并行运行。
使用 system_config 表（DB 级 key-value）做分布式锁，
防止 gunicorn 多 worker 下重复执行。

调度策略：
  - 每 5 分钟检查一次是否达到刷新间隔
  - 默认刷新间隔：30 分钟
  - 启动后随机延迟 0~120s，让多个 worker 错开
"""

import logging
import random
import threading
import time

logger = logging.getLogger(__name__)

# ── 配置 ──────────────────────────────────────────────────────────
REFRESH_INTERVAL = 30 * 60      # 两次刷新之间的最小间隔（秒）
CHECK_INTERVAL = 5 * 60         # 调度器检查周期（秒）
STARTUP_DELAY_MAX = 120         # 启动随机延迟上限（秒）

# system_config key 名称
_KEY_LAST_RUN = "scheduler_last_run"
_KEY_RUNNING  = "scheduler_running"


def _needs_refresh(db) -> bool:
    """检查是否到达刷新时间。"""
    conn = db.get_conn()
    row = conn.execute(
        "SELECT value FROM system_config WHERE key = ?", (_KEY_LAST_RUN,)
    ).fetchone()
    if row is None:
        return True  # 从未运行过
    last_run = float(row[0])
    return (time.time() - last_run) >= REFRESH_INTERVAL


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


def _scheduler_loop(db) -> None:
    """调度器主循环。"""
    # 启动随机延迟 — 让多个 gunicorn worker 错开
    delay = random.uniform(0, STARTUP_DELAY_MAX)
    logger.info("⏳ [调度器] 启动延迟 %.0f 秒", delay)
    time.sleep(delay)

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
    logger.info(
        "✅ 数据刷新调度器已启动（每 %d 分钟检查一次，采集间隔 %d 分钟）",
        CHECK_INTERVAL // 60, REFRESH_INTERVAL // 60,
    )
    return t
