"""
Walk-Forward 回测：评分重置机制验证。

零侵入 scorer.py — 通过 HistoricalDatabase 时间过滤包装器
让评估引擎"穿越"到历史时刻运行 evaluate()。

模块结构：
  HistoricalDatabase       — 时间过滤 Database 包装器
  run_scorer_at_timestamp() — 在历史时间点跑 evaluate()
  main()                   — CLI 入口
"""

import json
import logging
import re
import sqlite3
import time as time_module
from typing import Any, Dict, List, Optional, Tuple

from core.db import Database

logger = logging.getLogger(__name__)

# ─── 验证参数 ───────────────────────────────────────────────

LOOKAHEAD_DAYS = [1, 2, 5, 10, 20]

# ─── 7 品种 Walk-Forward 配置 ──────────────────────────────
# 覆盖 5 大板块：黑色 / 有色 / 贵金属 / 能化 / 油脂
# 全部使用连续合约（symbol 自身）以获得最长历史数据

TARGET_SYMBOLS = [
    ("RB", "RB", "螺纹钢", "黑色"),
    ("CU", "CU", "铜",     "有色"),
    ("AU", "AU", "黄金",   "贵金属"),
    ("AG", "AG", "白银",   "贵金属"),
    ("MA", "MA", "甲醇",   "能化"),
    ("TA", "TA", "PTA",    "能化"),
    ("I",  "I",  "铁矿石", "黑色"),
]

# 多时间窗口配置（训练期 / 验证期 / 标签）
WINDOW_CONFIGS = [
    (3, 6,  "3y+6m"),    # 基准：3 年训练 + 6 月验证
    (2, 3,  "2y+3m"),    # 敏捷：2 年训练 + 3 月验证
    (5, 12, "5y+12m"),   # 长期：5 年训练 + 12 月验证
]

# 需要时间过滤的表及其对应的时间列
TIME_FILTER_COLUMNS: Dict[str, str] = {
    "futures_klines": "timestamp",
    "futures_n_structures": "point_c_time",  # C点确认时间 = 结构形成时间
    "futures_macd": "timestamp",
    "futures_swing_points": "timestamp",
}

# ─── SQL 拦截代理 ─────────────────────────────────────────

_SELECT_RE = re.compile(r"^\s*SELECT\b", re.IGNORECASE)


class _TimeFilteredConnection:
    """代理 sqlite3.Connection，拦截 SELECT 查询追加时间过滤。

    对涉及 futures_klines / futures_n_structures / futures_macd
    等表的查询，自动追加 ``AND {time_col} <= ?``，限制数据在
    历史时间点之前。
    """

    def __init__(self, conn: sqlite3.Connection, current_ts: int) -> None:
        self._conn = conn
        self._current_ts = current_ts

    # ── execute 拦截 ─────────────────────────────────────

    def execute(
        self, sql: str, parameters: Any = None
    ) -> sqlite3.Cursor:
        new_sql, params = self._rewrite(sql, parameters)
        # _rewrite 返回 (sql, params)：
        # - SELECT:  params 永远是 list（经 _to_list 统一化）
        # - 非 SELECT: params 保持原始类型（如 dict），不改动
        return self._conn.execute(new_sql, params)

    def executemany(
        self, sql: str, parameters: Any = None
    ) -> sqlite3.Cursor:
        # 不拦截 INSERT/UPDATE
        return self._conn.executemany(sql, parameters or [])

    def executescript(self, sql: str) -> sqlite3.Cursor:
        return self._conn.executescript(sql)

    # ── 上下文管理 ───────────────────────────────────────

    def __enter__(self) -> "_TimeFilteredConnection":
        return self

    def __exit__(self, *args: Any) -> None:
        pass  # 不关闭底层连接

    # ── 代理常用属性 ─────────────────────────────────────

    @property
    def row_factory(self) -> Any:
        return self._conn.row_factory

    @row_factory.setter
    def row_factory(self, value: Any) -> None:
        self._conn.row_factory = value

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        pass  # 由 Database 管理生命周期

    def cursor(self) -> sqlite3.Cursor:
        return self._conn.cursor()

    # ── 内部重写 ─────────────────────────────────────────

    def _rewrite(self, sql: str, parameters: Any = None) -> Tuple[str, Any]:
        """检测 SQL 中的目标表，追加时间过滤条件。

        SELECT 查询：重写 SQL + 参数转换为 list（为插入时间参数做准备）。
        非 SELECT 查询：不动 params（原生传递，如 dict→INSERT）。

        返回:
            (重写后的SQL, params) — params 类型取决于 SQL 类型。
        """
        if not _SELECT_RE.match(sql):
            return sql, parameters

        # 检查是否涉及需要过滤的表
        for table, ts_col in TIME_FILTER_COLUMNS.items():
            if table not in sql:
                continue

            params = self._to_list(parameters)
            sql_clean = sql.rstrip("; \t\n\r")
            condition = f"AND {ts_col} <= ?"

            # 找到插入位置（ORDER BY / LIMIT 之前）
            insert_pos = self._find_insert_pos(sql_clean)
            sql_clean = (
                sql_clean[:insert_pos]
                + condition + " "
                + sql_clean[insert_pos:]
            )

            # 计算插入位置之前有多少个 ? 参数
            # 从 SQL 开头到 insert_pos 之间，在引号外部的 ? 数量
            before_sql = sql_clean[:insert_pos]
            # 确保 ? 不是在字符串字面量或注释中（简单版：统计所有 ?）
            # 为了安全，统计原始 SQL 中 insert_pos 之前的 ? 数量
            # insert_pos 在加了 condition 之前就已确定
            param_count_before = sql[:insert_pos].count("?")
            insert_param_at = min(param_count_before, len(params))
            params.insert(insert_param_at, self._current_ts)

            return sql_clean, params

        return sql, self._to_list(parameters)

    @staticmethod
    def _find_insert_pos(sql: str) -> int:
        """找到 WHERE 条件插入位置：ORDER BY / LIMIT 之前，或末尾。"""
        # ORDER BY 优先
        m = re.search(r"\bORDER\s+BY\b", sql, re.IGNORECASE)
        if m:
            return m.start()
        # LIMIT（无 ORDER BY 时）
        m = re.search(r"\bLIMIT\b", sql, re.IGNORECASE)
        if m:
            return m.start()
        # 无排序/限制——追加末尾
        return len(sql)

    @staticmethod
    def _to_list(parameters: Any) -> list:
        """统一 parameters 为 list 格式。"""
        if parameters is None:
            return []
        if isinstance(parameters, (list, tuple)):
            return list(parameters)
        return [parameters]


# ─── HistoricalDatabase ────────────────────────────────────


class HistoricalDatabase:
    """时间过滤 Database 包装器。

    包装真实 Database，使所有 K线/N型结构/MACD/Swing 查询都
    限制在 ``_current_ts`` 之前的数据。用于 Walk-Forward 回测
    中的历史回放。

    用法:
        db = Database(DB_PATH)
        hist_db = HistoricalDatabase(db, target_timestamp)
        result = scorer.evaluate("RB", "RB", hist_db)
    """

    def __init__(self, real_db: Database, current_ts: int) -> None:
        self._real_db = real_db
        self._current_ts = current_ts

    def set_timestamp(self, ts: int) -> None:
        """更改当前时间点。"""
        self._current_ts = ts

    @property
    def current_ts(self) -> int:
        return self._current_ts

    def get_conn(self) -> _TimeFilteredConnection:
        """返回时间过滤代理连接。"""
        real_conn = self._real_db.get_conn()
        return _TimeFilteredConnection(real_conn, self._current_ts)

    # ── 代理 Database 方法 ───────────────────────────────

    @property
    def db_path(self) -> str:
        return self._real_db.db_path

    def close(self) -> None:
        self._real_db.close()

    def init_all_tables(self) -> None:
        self._real_db.init_all_tables()


# ─── 价格验证 ─────────────────────────────────────────────


def _load_klines_since(
    db: Database, symbol: str, contract: str, since_ts: int
) -> List[Dict[str, Any]]:
    """加载指定时间点之后的 1d K线（时间升序）。"""
    with db.get_conn() as conn:
        rows = conn.execute(
            """SELECT timestamp, open, high, low, close, volume
               FROM futures_klines
               WHERE symbol=? AND contract=? AND timeframe=?
                 AND timestamp >= ?
               ORDER BY timestamp ASC""",
            (symbol, contract, "1d", since_ts),
        ).fetchall()
    return [dict(r) for r in rows]


def _verify_forward(
    klines: List[Dict[str, Any]],
    entry_ts: int,
    entry_price: float,
    direction: str,
    lookahead: List[int],
) -> Dict[str, Dict]:
    """从 entry_ts 起，向前 N 个交易日验证方向预测。

    Returns:
        { "1d": {"correct": True, "return_pct": 0.5}, "2d": ... }
    """
    # 找到 entry_ts 对应的 kline 索引
    entry_idx: Optional[int] = None
    for i, k in enumerate(klines):
        if k["timestamp"] >= entry_ts:
            entry_idx = i
            break

    if entry_idx is None:
        return {str(d): {"correct": None, "return_pct": None} for d in lookahead}

    trades: Dict[str, Dict] = {}
    for d in lookahead:
        exit_idx = entry_idx + d
        if exit_idx >= len(klines):
            trades[str(d)] = {"correct": None, "return_pct": None}
            continue

        exit_price = klines[exit_idx]["close"]
        if direction == "LONG":
            pnl = (exit_price - entry_price) / entry_price * 100
            correct = exit_price > entry_price
        else:  # SHORT
            pnl = (entry_price - exit_price) / entry_price * 100
            correct = exit_price < entry_price

        trades[str(d)] = {
            "correct": correct,
            "return_pct": round(pnl, 2),
        }

    return trades


# ─── run_scorer_at_timestamp ──────────────────────────────


def run_scorer_at_timestamp(
    symbol: str,
    contract: str,
    db: Database,
    ts: int,
    enable_reset: bool = True,
    level1_only: bool = False,
) -> Dict[str, Any]:
    """在历史时间点运行 scorer.evaluate()。

    工作流程:
      1. 创建 HistoricalDatabase，设置时间 = ts
      2. 临时修补 ``time.time()`` 使 scorer 内新鲜度检查使用历史时间
      3. 调用 scorer.evaluate() 获取 SignalResult
      4. 检查后续 N 个交易日价格走势
      5. 记录是否触发了评分重置

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        db: 真实 Database（用于价格验证）。
        ts: 历史时间戳（Unix 秒）。
        enable_reset: True=带评分重置, False=绕过重置。

    Returns:
        结构化字典：
        {
            "timestamp": ts,
            "signal": SignalResult 的 dict 格式,
            "enable_reset": bool,
            "reset_triggered": bool,   # 本次评估是否触发了重置
            "forward_verification": {   # 后续 N 日价格验证
                "1d": {"correct": bool|None, "return_pct": float|None},
                ...
            },
        }
    """
    # ── 延迟导入（避免循环依赖） ─────────────────────────
    import futures.scorer as scorer_module
    from futures.n_structure import detect_and_save
    from config.settings import (
        LEVEL1_TIMEFRAME, LEVEL1_MACD_TIMEFRAME,
        LEVEL2_TIMEFRAME, LEVEL3_TIMEFRAME,
    )

    # ── 1. 创建历史数据库 ───────────────────────────────
    hist_db = HistoricalDatabase(db, ts)

    # ── 2. 修补 time.time（全局级别） ──────────────────
    # scorer._get_active_n_structure 内部执行
    #   import time as time_module
    #   now = int(time_module.time())
    # 修补全局 time.time（而非 time_module）以影响所有
    # 模块内部的 ``import time; time.time`` 调用。
    import time as _real_time
    orig_time = _real_time.time
    _real_time.time = lambda: float(ts)

    # ── 3. 修补 _apply_score_reset（如需绕过） ──────────
    orig_apply_reset = scorer_module._apply_score_reset
    if not enable_reset:
        scorer_module._apply_score_reset = lambda *a, **kw: False

    reset_triggered = False
    level1_direction = "NONE"
    level1_signal = None  # 仅 level1_only 时设置

    try:
        # ── 3.5 运行 N 型结构检测（通过时间过滤数据库） ──
        # 历史时间点无 N 型结构，需要从当时的 swing points 检测生成
        if level1_only:
            # Level1-only：只需周线 N 型 + 日线 MACD
            try:
                detect_and_save(symbol, contract, LEVEL1_TIMEFRAME, hist_db)
            except Exception as e:
                logger.debug("N型检测 %s %s 异常: %s", symbol, LEVEL1_TIMEFRAME, e)

            # 获取 Level1 结构 + MACD 用于方向判别
            try:
                from futures.shared import FRESHNESS as _wf_freshness
                # Walk-Forward 模式下跳过新鲜度检查（60天窗口对历史回测太短）
                _orig_freshness_1w = _wf_freshness.get("1w")
                _wf_freshness["1w"] = 100 * 365 * 86400  # 100年

                from futures.shared import _get_active_n_structure
                l1_struct = _get_active_n_structure(
                    hist_db, symbol, contract, LEVEL1_TIMEFRAME
                )

                # 恢复原始新鲜度
                if _orig_freshness_1w is not None:
                    _wf_freshness["1w"] = _orig_freshness_1w

                if l1_struct and l1_struct.get("state") in ("LEG2", "LEG3"):
                    level1_direction = l1_struct["direction"]
                    from futures.color_tracker import check_macd_trajectory
                    l1_macd = check_macd_trajectory(
                        symbol, symbol, l1_struct,
                        LEVEL1_MACD_TIMEFRAME, level1_direction, hist_db
                    )
                    level1_signal = {
                        "direction": level1_direction,
                        "state": l1_struct["state"],
                        "entry_price": l1_struct.get("point_b_price"),
                        "macd_passed": l1_macd.get("passed", False),
                        "macd_description": l1_macd.get("description", ""),
                        "n_structure": {
                            "point_a_price": l1_struct["point_a_price"],
                            "point_b_price": l1_struct["point_b_price"],
                            "point_c_price": l1_struct.get("point_c_price"),
                        },
                    }
            except Exception as e:
                logger.debug("Level1-only 评估 %s 异常: %s", symbol, e)
        else:
            for tf in (LEVEL1_TIMEFRAME, LEVEL2_TIMEFRAME, LEVEL3_TIMEFRAME):
                try:
                    detect_and_save(symbol, contract, tf, hist_db)
                except Exception as e:
                    logger.debug("N型检测 %s %s 异常: %s", symbol, tf, e)

        # ── 4. 运行 evaluate ────────────────────────────
        signal_result = scorer_module.evaluate(symbol, contract, hist_db)

        # ── 4.5 Level1-only 前进验证 ──────────────────
        if level1_only and level1_signal is not None:
            direction = level1_direction
            entry_price = level1_signal["entry_price"]
            level1_signal["forward_verification"] = {}
            if entry_price is not None and direction != "NONE":
                klines = _load_klines_since(db, symbol, contract, ts)
                level1_signal["forward_verification"] = _verify_forward(
                    klines, ts, entry_price, direction, LOOKAHEAD_DAYS
                )

        # 判断是否触发了重置（仅在 enable_reset=True 时有意义）
        if enable_reset and signal_result.direction != "NONE":
            # 重新运行并临时绕过重置，对比结果
            time_module.time = lambda: float(ts)
            scorer_module._apply_score_reset = lambda *a, **kw: False

            no_reset_result = scorer_module.evaluate(symbol, contract, hist_db)
            # 如果带重置比不带重置的分低，说明重置触发了
            reset_triggered = (
                no_reset_result.overall_score > signal_result.overall_score
                and signal_result.overall_score == 0
            )

        # ── 5. 价格验证 ────────────────────────────────
        entry_price = signal_result.entry_price
        direction = signal_result.direction

        forward: Dict[str, Any] = {}
        if entry_price is not None and direction != "NONE":
            klines = _load_klines_since(db, symbol, contract, ts)
            forward = _verify_forward(
                klines, ts, entry_price, direction, LOOKAHEAD_DAYS
            )
        else:
            forward = {str(d): {"correct": None, "return_pct": None}
                       for d in LOOKAHEAD_DAYS}

    finally:
        # ── 6. 恢复修补 ────────────────────────────────
        _real_time.time = orig_time
        scorer_module._apply_score_reset = orig_apply_reset

    # ── 7. 组装结果 ────────────────────────────────────
    from dataclasses import asdict

    return {
        "timestamp": ts,
        "symbol": symbol,
        "contract": contract,
        "signal": asdict(signal_result),
        "enable_reset": enable_reset,
        "reset_triggered": reset_triggered,
        "forward_verification": forward,
        "level1_only": level1_only,
        "level1_signal": level1_signal,
    }


# ─── 聚合统计 ─────────────────────────────────────────────


def _aggregate_accuracy(
    results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """聚合一组时间点评估结果的准确率统计。

    Args:
        results: run_scorer_at_timestamp 的结果列表。

    Returns:
        {
            "total_checkpoints": N,
            "signal_count": N,         # 有方向信号的次数
            "reset_trigger_count": N,
            "accuracy_1d": 55.0,
            "accuracy_5d": 52.0,
            ...
        }
    """
    # 兼容 Level1-only 模式（signal 存在 level1_signal 中）
    def _get_direction(r: Dict) -> str:
        l1s = r.get("level1_signal")
        if r.get("level1_only") and l1s:
            return l1s.get("direction", "NONE")
        return r.get("signal", {}).get("direction", "NONE")

    def _get_forward_verification(r: Dict) -> Dict:
        l1s = r.get("level1_signal")
        if r.get("level1_only") and l1s:
            return l1s.get("forward_verification", {})
        return r.get("forward_verification", {})

    signals = [r for r in results if _get_direction(r) != "NONE"]
    total = len(results)
    signal_count = len(signals)
    reset_count = sum(1 for r in results if r.get("reset_triggered"))

    acc: Dict[str, Any] = {
        "total_checkpoints": total,
        "signal_count": signal_count,
        "signal_rate": round(signal_count / total * 100, 1) if total else 0,
        "reset_trigger_count": reset_count,
    }

    for d in LOOKAHEAD_DAYS:
        dk = str(d)
        correct = sum(
            1 for s in signals
            if _get_forward_verification(s).get(dk, {}).get("correct") is True
        )
        wrong = sum(
            1 for s in signals
            if _get_forward_verification(s).get(dk, {}).get("correct") is False
        )
        valid = correct + wrong

        returns = [
            _get_forward_verification(s)[dk]["return_pct"]
            for s in signals
            if _get_forward_verification(s).get(dk, {}).get("return_pct") is not None
        ]

        acc[f"accuracy_{d}d"] = round(correct / valid * 100, 1) if valid else 0
        acc[f"signals_{d}d"] = valid
        acc[f"avg_return_{d}d"] = round(sum(returns) / len(returns), 2) if returns else 0

    return acc


# ─── Walk-Forward 主流程 ──────────────────────────────────


def _get_klines_time_range(db: Database) -> Tuple[int, int]:
    """从 futures_klines 表获取数据最早/最晚时间戳。

    Returns:
        (first_ts, last_ts) — Unix 秒。
    """
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT MIN(timestamp) as first_ts, MAX(timestamp) as last_ts FROM futures_klines"
        ).fetchone()
    if row is None or row["first_ts"] is None:
        return 0, 0
    return int(row["first_ts"]), int(row["last_ts"])


def _ts_to_date_str(ts: int) -> str:
    """Unix 秒 → 'YYYY-MM' 字符串。"""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m")


def run_walkforward_with_reset(
    symbol: str,
    contract: str,
    db: Database,
    train_years: int = 3,
    valid_months: int = 6,
    lookahead_days: Optional[List[int]] = None,
    level1_only: bool = False,
) -> Dict[str, Any]:
    """Walk-Forward 验证：评分重置机制 vs 无重置的准确率对比。

    架构：
        在历史时间点上滑动折叠地执行 scorer.evaluate()，每个时间点
        分别运行 with_reset / without_reset，对比准确率差异。

    折叠划分（参考 n_backtest.run_walkforward）：
        Fold 1: [─── 训练 3y ───][─── 验证 6m ───]
        Fold 2:        [─── 3y ───][─── 6m ───]
        Fold 3:               [─── 3y ───][─── 6m ───]

    在每个 fold 的验证期内，按日步进，每个时间点：
      - 创建 HistoricalDatabase
      - 调 with_reset=True  的 run_scorer_at_timestamp
      - 调 with_reset=False 的 run_scorer_at_timestamp
      - 记录信号方向和后续 N 日价格验证

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        db: Database 实例（真实数据库，由 HistoricalDatabase 包装）。
        train_years: 训练期年数。
        valid_months: 验证期月数。
        lookahead_days: 向前看交易日数（默认 [1,2,5,10,20]）。

    Returns:
        结构化报告：
        {
            "symbol": "RB",
            "total_checkpoints": 1500,
            "folds": [
                {
                    "train_start": "2018-01",
                    "train_end": "2020-12",
                    "valid_start": "2021-01",
                    "valid_end": "2021-06",
                    "with_reset": { "total_signals": 45, "accuracy_1d": 62.3, ... },
                    "without_reset": { ... },
                    "improvement": { "accuracy_1d": 6.5, ... },
                }
            ],
            "avg_improvement": { "accuracy_1d": 4.2, ... },
        }
    """
    if lookahead_days is None:
        lookahead_days = LOOKAHEAD_DAYS

    # ── 1. 确定时间范围 ────────────────────────────────
    first_ts, last_ts = _get_klines_time_range(db)
    if first_ts == 0 or last_ts == 0:
        return {"error": "No kline data found in database"}

    logger.info(
        "Walk-Forward: %s 时间范围 %s ~ %s",
        symbol,
        _ts_to_date_str(first_ts),
        _ts_to_date_str(last_ts),
    )

    # 训练期至少要有一个 fold 的验证期在数据范围内
    train_seconds = train_years * 365 * 86400
    valid_seconds = valid_months * 30 * 86400
    window_seconds = train_seconds + valid_seconds

    if first_ts + window_seconds > last_ts:
        logger.warning(
            "数据不足: 需要 %dy+%dm (%ds)，可用 %ds",
            train_years, valid_months, window_seconds,
            last_ts - first_ts,
        )
        return {
            "error": (
                f"Insufficient data: need {train_years}y+{valid_months}m "
                f"({window_seconds}s), available {last_ts - first_ts}s"
            )
        }

    # ── 2. 生成折叠 ────────────────────────────────────
    folds: List[Dict[str, Any]] = []
    fold_start = first_ts

    while fold_start + window_seconds <= last_ts:
        train_end = fold_start + train_seconds
        valid_end = train_end + valid_seconds

        # 验证期内的每日步进检查点
        checkpoints: List[int] = []
        ck = train_end
        while ck < valid_end:
            checkpoints.append(ck)
            ck += 86400  # 每日步进

        if not checkpoints:
            fold_start += window_seconds // 2
            continue

        logger.info(
            "Fold: train=%s~%s valid=%s~%s (%d checkpoints)",
            _ts_to_date_str(int(fold_start)),
            _ts_to_date_str(int(train_end)),
            _ts_to_date_str(int(train_end)),
            _ts_to_date_str(int(valid_end)),
            len(checkpoints),
        )

        # ── 3. 在每个检查点运行 with/without reset ─────
        with_results: List[Dict[str, Any]] = []
        without_results: List[Dict[str, Any]] = []

        for idx, ck_ts in enumerate(checkpoints):
            if idx % 50 == 0:
                logger.info(
                    "  checkpoint %d/%d @ %s",
                    idx + 1, len(checkpoints),
                    _ts_to_date_str(ck_ts),
                )

            wr = run_scorer_at_timestamp(symbol, contract, db, ck_ts, enable_reset=True, level1_only=level1_only)
            wo = run_scorer_at_timestamp(symbol, contract, db, ck_ts, enable_reset=False, level1_only=level1_only)
            with_results.append(wr)
            without_results.append(wo)

        # ── 4. 聚合本 fold ────────────────────────────
        w_acc = _aggregate_accuracy(with_results)
        wo_acc = _aggregate_accuracy(without_results)

        improvement: Dict[str, Any] = {}
        for d in lookahead_days:
            dk = f"accuracy_{d}d"
            w_val = w_acc.get(dk, 0)
            wo_val = wo_acc.get(dk, 0)
            improvement[dk] = round(w_val - wo_val, 1)

        folds.append({
            "train_start": _ts_to_date_str(int(fold_start)),
            "train_end": _ts_to_date_str(int(train_end)),
            "valid_start": _ts_to_date_str(int(train_end)),
            "valid_end": _ts_to_date_str(int(valid_end)),
            "checkpoints": len(checkpoints),
            "with_reset": {k: w_acc[k] for k in w_acc if k != "total_checkpoints"},
            "without_reset": {k: wo_acc[k] for k in wo_acc if k != "total_checkpoints"},
            "improvement": improvement,
        })

        # 滑动半个窗口
        fold_start += window_seconds // 2

    # ── 5. 全量聚合 ────────────────────────────────────
    total_checkpoints = sum(f["checkpoints"] for f in folds)
    avg_improvement: Dict[str, Any] = {}
    for d in lookahead_days:
        dk = f"accuracy_{d}d"
        values = [f["improvement"].get(dk, 0) for f in folds]
        avg_improvement[dk] = round(sum(values) / len(values), 1) if values else 0

    return {
        "symbol": symbol,
        "contract": contract,
        "total_checkpoints": total_checkpoints,
        "folds": folds,
        "avg_improvement": avg_improvement,
    }


# ─── 多品种聚合报告 ────────────────────────────────────────


def _build_grouped_report(
    all_results: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """将多品种/多窗口结果整理为结构化报告。

    Args:
        all_results: {symbol: {window_label: walkforward_result, ...}, ...}

    Returns:
        含 summary、by_symbol、by_window、by_sector 的报告字典。
    """
    from datetime import datetime, timezone

    report: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "symbols_tested": len(all_results),
        "by_symbol": [],
        "by_window": {},
        "by_sector": {},
        "all_results": all_results,
    }

    # ── by_symbol: 每个品种的最佳窗口准确率 ────────────────
    for sym, windows in sorted(all_results.items()):
        entry = {"symbol": sym}
        best_acc_1d = 0
        best_window = None
        for wl, result in windows.items():
            if "error" in result:
                continue
            acc_1d = result.get("avg_improvement", {}).get("accuracy_1d", 0)
            if acc_1d > best_acc_1d:
                best_acc_1d = acc_1d
                best_window = wl
            entry[wl] = {
                "folds": result.get("total_checkpoints", 0),
                "improvement_1d": result.get("avg_improvement", {}).get("accuracy_1d", 0),
                "improvement_5d": result.get("avg_improvement", {}).get("accuracy_5d", 0),
            }
        entry["best_window"] = best_window
        entry["best_improvement_1d"] = best_acc_1d
        report["by_symbol"].append(entry)

    # ── by_window: 每个窗口在所有品种上的均值 ─────────────
    for wl in [c[2] for c in WINDOW_CONFIGS]:
        improvements = []
        for sym, windows in all_results.items():
            result = windows.get(wl, {})
            if "error" not in result:
                imp = result.get("avg_improvement", {})
                improvements.append(imp.get("accuracy_1d", 0))
        report["by_window"][wl] = {
            "symbol_count": len(improvements),
            "avg_improvement_1d": round(sum(improvements) / len(improvements), 1) if improvements else 0,
        }

    # ── by_sector: 按板块聚合 ──────────────────────────────
    sector_map: Dict[str, List[float]] = {}
    for sym, _contract, _name, sector in TARGET_SYMBOLS:
        if sym not in sector_map:
            sector_map[sector] = []
        windows = all_results.get(sym, {})
        for wl, result in windows.items():
            if "error" not in result:
                imp = result.get("avg_improvement", {})
                sector_map[sector].append(imp.get("accuracy_1d", 0))

    for sector, values in sector_map.items():
        report["by_sector"][sector] = {
            "symbol_count": len([s for s, _, _, sec in TARGET_SYMBOLS if sec == sector]),
            "avg_improvement_1d": round(sum(values) / len(values), 1) if values else 0,
        }

    return report


def run_batch_walkforward(
    db: Database,
    symbols: Optional[List[str]] = None,
    level1_only: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """批量运行多品种/多窗口 Walk-Forward 回测。

    Args:
        db: Database 实例。
        symbols: 品种代码列表（如 ['RB', 'CU']），默认全部 7 个。

    Returns:
        {symbol: {window_label: result_dict, ...}, ...}
        每项结果同 run_walkforward_with_reset() 返回值。
    """
    # 解析目标品种
    if symbols is None:
        targets = TARGET_SYMBOLS  # (symbol, contract, name, sector)
    else:
        targets = [
            t for t in TARGET_SYMBOLS if t[0] in symbols
        ]

    logger.info("===== 批量 Walk-Forward 回测启动 =====")
    logger.info("品种: %s", ", ".join(f"{s[0]}({s[2]})" for s in targets))
    logger.info("窗口: %s", ", ".join(c[2] for c in WINDOW_CONFIGS))

    all_results: Dict[str, Dict[str, Any]] = {}

    for sym, contract, name, sector in targets:
        logger.info("──── %s(%s) ────", sym, name)
        window_results: Dict[str, Any] = {}

        for train_years, valid_months, label in WINDOW_CONFIGS:
            logger.info("  窗口 %s (%dy+%dm)...", label, train_years, valid_months)
            try:
                result = run_walkforward_with_reset(
                    sym, contract, db,
                    train_years=train_years,
                    valid_months=valid_months,
                    level1_only=level1_only,
                )
                window_results[label] = result
                if "error" in result:
                    logger.warning("    ❌ %s", result["error"])
                else:
                    imp = result.get("avg_improvement", {})
                    logger.info(
                        "    ✅ folds=%d, imp_1d=%.1f%%",
                        result.get("total_checkpoints", 0),
                        imp.get("accuracy_1d", 0),
                    )
            except Exception as e:
                logger.error("    ❌ 异常: %s", e)
                window_results[label] = {"error": str(e)}

        all_results[sym] = window_results

    logger.info("===== 批量 Walk-Forward 回测完成 =====")
    return all_results


def main() -> None:
    """CLI 入口：在指定时间点运行 scorer.evaluate()。

    用法:
        python -m futures.scorer_walkforward --symbol RB --ts 1700000000
        python -m futures.scorer_walkforward --symbol RB --today  # 近24h
        python -m futures.scorer_walkforward --symbol RB --walkforward  # Walk-Forward
    """
    import argparse
    from config.settings import DB_PATH

    parser = argparse.ArgumentParser(
        description="Walk-Forward 回测：评分重置机制验证"
    )
    parser.add_argument("--symbol", "-s", required=True, help="品种代码")
    parser.add_argument("--contract", "-c", default=None, help="合约代码")
    parser.add_argument("--ts", type=int, default=None,
                        help="历史时间戳（Unix秒）")
    parser.add_argument("--today", action="store_true",
                        help="使用当前时间（近24h）")
    parser.add_argument("--no-reset", action="store_true",
                        help="绕过评分重置")
    parser.add_argument("--compare", action="store_true",
                        help="同时跑 with/without reset 并对比")
    parser.add_argument("--walkforward", action="store_true",
                        help="运行 Walk-Forward 回测（含所有 fold）")
    parser.add_argument("--train-years", type=int, default=3,
                        help="Walk-Forward 训练期年数（默认 3）")
    parser.add_argument("--valid-months", type=int, default=6,
                        help="Walk-Forward 验证期月数（默认 6）")
    parser.add_argument("--compact", action="store_true",
                        help="简洁输出")
    parser.add_argument("--batch", nargs="*", default=None,
                        help="批量运行 7 品种/多窗口 Walk-Forward（可指定品种，如 --batch RB CU）")
    parser.add_argument("--level1-only", action="store_true",
                        help="仅使用 Level1（周线 N 型 + 日线 MACD），不需要更低周期数据，提高历史信号覆盖率")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )

    contract = args.contract or args.symbol

    if args.today:
        ts = int(time_module.time()) - 86400
    elif args.ts:
        ts = args.ts
    else:
        ts = int(time_module.time()) - 86400

    db = Database(DB_PATH)

    if args.batch is not None:
        symbols = args.batch if args.batch else None  # None = 全部 7 个
        all_results = run_batch_walkforward(db, symbols=symbols, level1_only=args.level1_only)
        report = _build_grouped_report(all_results)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    if args.walkforward:
        result = run_walkforward_with_reset(
            args.symbol, contract, db,
            train_years=args.train_years,
            valid_months=args.valid_months,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.compare:
        # 同时跑 with/without reset 并对比
        with_reset = run_scorer_at_timestamp(
            args.symbol, contract, db, ts, enable_reset=True
        )
        without_reset = run_scorer_at_timestamp(
            args.symbol, contract, db, ts, enable_reset=False
        )

        result = {
            "symbol": args.symbol,
            "contract": contract,
            "timestamp": ts,
            "with_reset": {
                "signal": with_reset.get("signal"),
                "reset_triggered": with_reset.get("reset_triggered"),
                "forward_verification": with_reset.get("forward_verification"),
            },
            "without_reset": {
                "signal": without_reset.get("signal"),
                "reset_triggered": without_reset.get("reset_triggered"),
                "forward_verification": without_reset.get("forward_verification"),
            },
        }
    else:
        result = run_scorer_at_timestamp(
            args.symbol, contract, db, ts,
            enable_reset=not args.no_reset,
        )

    if args.compact and "forward_verification" in result:
        result["forward_verification_summary"] = _aggregate_accuracy([result])
        if isinstance(result, dict):
            pass
        else:
            result.pop("forward_verification", None)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()