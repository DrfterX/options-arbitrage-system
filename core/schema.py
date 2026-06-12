"""
统一数据库 Schema — 10 张表的完整 CREATE TABLE 语句。

所有 timestamp 字段统一存储 Unix 秒（UTC），显示时转换为 Asia/Shanghai。
"""

# ============================================================
# 10 张表的 DDL 定义
# key = 表名, value = CREATE TABLE 语句
# ============================================================
ALL_TABLES: dict[str, str] = {
    # ── 1. 品种母表 ──────────────────────────────────────────
    "symbols": """
        CREATE TABLE IF NOT EXISTS symbols (
            symbol       TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            option_name  TEXT DEFAULT '',
            exchange     TEXT NOT NULL,
            category     TEXT NOT NULL,
            multiplier   INTEGER DEFAULT 1,
            has_options  INTEGER DEFAULT 0,
            is_night     INTEGER DEFAULT 0,
            updated_at   TEXT DEFAULT (datetime('now'))
        )
    """,

    # ── 2. 期货K线 ───────────────────────────────────────────
    "futures_klines": """
        CREATE TABLE IF NOT EXISTS futures_klines (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol     TEXT NOT NULL,
            contract   TEXT NOT NULL,
            timeframe  TEXT NOT NULL,
            timestamp  INTEGER NOT NULL,
            open       REAL NOT NULL,
            high       REAL NOT NULL,
            low        REAL NOT NULL,
            close      REAL NOT NULL,
            volume     INTEGER DEFAULT 0,
            UNIQUE(symbol, contract, timeframe, timestamp)
        )
    """,

    # ── 3. MACD指标 ──────────────────────────────────────────
    "futures_macd": """
        CREATE TABLE IF NOT EXISTS futures_macd (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol     TEXT NOT NULL,
            contract   TEXT NOT NULL,
            timeframe  TEXT NOT NULL,
            timestamp  INTEGER NOT NULL,
            macd       REAL NOT NULL,
            signal     REAL NOT NULL,
            histogram  REAL NOT NULL,
            color      TEXT DEFAULT '',
            UNIQUE(symbol, contract, timeframe, timestamp)
        )
    """,

    # ── 4. 波峰波谷 ──────────────────────────────────────────
    "futures_swing_points": """
        CREATE TABLE IF NOT EXISTS futures_swing_points (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol     TEXT NOT NULL,
            contract   TEXT NOT NULL,
            timeframe  TEXT NOT NULL,
            timestamp  INTEGER NOT NULL,
            price      REAL NOT NULL,
            point_type TEXT NOT NULL,
            UNIQUE(symbol, contract, timeframe, timestamp)
        )
    """,

    # ── 5. N型结构 ───────────────────────────────────────────
    "futures_n_structures": """
        CREATE TABLE IF NOT EXISTS futures_n_structures (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol         TEXT NOT NULL,
            contract       TEXT NOT NULL,
            timeframe      TEXT NOT NULL,
            direction      TEXT NOT NULL,
            state          TEXT NOT NULL,
            point_a_time   INTEGER NOT NULL,
            point_a_price  REAL NOT NULL,
            point_b_time   INTEGER NOT NULL,
            point_b_price  REAL NOT NULL,
            point_c_time   INTEGER NOT NULL,
            point_c_price  REAL NOT NULL,
            created_at     TEXT DEFAULT (datetime('now')),
            updated_at     TEXT DEFAULT (datetime('now'))
        )
    """,

    # ── 6. 期货信号 ──────────────────────────────────────────
    "futures_signals": """
        CREATE TABLE IF NOT EXISTS futures_signals (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol       TEXT NOT NULL,
            contract     TEXT NOT NULL,
            direction    TEXT NOT NULL,
            signal_type  TEXT NOT NULL,
            level1_pass  INTEGER DEFAULT 0,
            level2_pass  INTEGER DEFAULT 0,
            level3_pass  INTEGER DEFAULT 0,
            entry_price  REAL DEFAULT 0,
            stop_loss    REAL DEFAULT 0,
            take_profit  REAL DEFAULT 0,
            score        REAL DEFAULT 0,
            detail       TEXT DEFAULT '',
            fingerprint  TEXT DEFAULT '',
            created_at   TEXT DEFAULT (datetime('now'))
        )
    """,

    # ── 7. IV历史 ────────────────────────────────────────────
    "iv_history": """
        CREATE TABLE IF NOT EXISTS iv_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol          TEXT NOT NULL,
            contract        TEXT NOT NULL,
            date            TEXT NOT NULL,
            time            TEXT NOT NULL,
            futures_price   REAL NOT NULL,
            atm_strike      REAL NOT NULL,
            atm_call_iv     REAL DEFAULT 0,
            atm_put_iv      REAL DEFAULT 0,
            avg_iv          REAL DEFAULT 0,
            top5_call_iv    REAL DEFAULT 0,
            top5_put_iv     REAL DEFAULT 0,
            top5_avg_iv     REAL DEFAULT 0
        )
    """,

    # ── 8. 期权信号 ──────────────────────────────────────────
    "options_signals": """
        CREATE TABLE IF NOT EXISTS options_signals (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol            TEXT NOT NULL,
            contract          TEXT NOT NULL,
            strategy          TEXT NOT NULL,
            signal_type       TEXT NOT NULL,
            strength          REAL DEFAULT 0,
            reason            TEXT DEFAULT '',
            futures_price     REAL DEFAULT 0,
            iv_avg            REAL DEFAULT 0,
            iv_percentile     REAL DEFAULT 0,
            iv_level          TEXT DEFAULT '',
            net_delta         REAL DEFAULT 0,
            net_theta         REAL DEFAULT 0,
            net_vega          REAL DEFAULT 0,
            max_profit        REAL DEFAULT 0,
            max_loss          REAL DEFAULT 0,
            unified_score     REAL DEFAULT 0,
            strategy_details  TEXT DEFAULT '',
            created_at        TEXT DEFAULT (datetime('now'))
        )
    """,

    # ── 9. 推送日志 ──────────────────────────────────────────
    "signal_push_log": """
        CREATE TABLE IF NOT EXISTS signal_push_log (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint    TEXT NOT NULL,
            symbol         TEXT NOT NULL,
            contract       TEXT NOT NULL,
            strategy_type  TEXT NOT NULL,
            strikes        TEXT DEFAULT '',
            score          REAL DEFAULT 0,
            pushed_at      TEXT DEFAULT (datetime('now'))
        )
    """,

    # ── 10. 系统配置 ─────────────────────────────────────────
    "system_config": """
        CREATE TABLE IF NOT EXISTS system_config (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL,
            updated_at  TEXT DEFAULT (datetime('now'))
        )
    """,

    # ── 11. 过滤决策日志 ──────────────────────────────────────
    "filter_decision_log": """
        CREATE TABLE IF NOT EXISTS filter_decision_log (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint       TEXT NOT NULL,
            symbol            TEXT NOT NULL,
            contract          TEXT NOT NULL,
            score             REAL DEFAULT 0,
            level1_pass       INTEGER DEFAULT 0,
            level2_pass       INTEGER DEFAULT 0,
            signal_type       TEXT NOT NULL,
            direction         TEXT DEFAULT '',
            should_push       INTEGER DEFAULT 0,
            push_level        TEXT DEFAULT 'SUPPRESS',
            reason            TEXT DEFAULT '',
            confidence        REAL DEFAULT 0,
            boost_factor      REAL DEFAULT 1.0,
            created_at        TEXT DEFAULT (datetime('now'))
        )
    """,

    # ── 12. Paper Trading 持仓表 ──────────────────────────────
    "positions": """
        CREATE TABLE IF NOT EXISTS positions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol        TEXT NOT NULL,
            contract      TEXT NOT NULL,
            direction     TEXT NOT NULL CHECK(direction IN ('LONG','SHORT')),
            entry_price   REAL NOT NULL,
            entry_time    INTEGER NOT NULL,
            quantity      INTEGER DEFAULT 1,
            status        TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','closed')),
            signal_id     INTEGER DEFAULT 0,
            signal_type   TEXT NOT NULL DEFAULT 'futures' CHECK(signal_type IN ('futures','options')),
            current_price REAL DEFAULT 0,
            stop_loss     REAL DEFAULT 0,
            take_profit   REAL DEFAULT 0,
            opened_at     TEXT DEFAULT (datetime('now')),
            updated_at    TEXT DEFAULT (datetime('now')),
            closed_at     TEXT DEFAULT ''
        )
    """,

    # ── 13. Paper Trading 交易流水表 ──────────────────────────
    "trades": """
        CREATE TABLE IF NOT EXISTS trades (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            position_id  INTEGER NOT NULL,
            action       TEXT NOT NULL CHECK(action IN ('open','close')),
            price        REAL NOT NULL,
            time         INTEGER NOT NULL,
            reason       TEXT DEFAULT '',
            pnl          REAL DEFAULT 0,
            created_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE
        )
    """,
}

# ============================================================
# 索引定义（在 init_all_tables 后执行）
# ============================================================
INDEXES: list[str] = [
    "CREATE INDEX IF NOT EXISTS idx_symbols_exchange ON symbols(exchange)",
    "CREATE INDEX IF NOT EXISTS idx_symbols_category ON symbols(category)",
    "CREATE INDEX IF NOT EXISTS idx_symbols_has_options ON symbols(has_options)",
    "CREATE INDEX IF NOT EXISTS idx_futures_klines_sym_ctr_tf ON futures_klines(symbol, contract, timeframe)",
    "CREATE INDEX IF NOT EXISTS idx_futures_klines_ts ON futures_klines(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_futures_macd_sym_ctr_tf ON futures_macd(symbol, contract, timeframe)",
    "CREATE INDEX IF NOT EXISTS idx_futures_macd_ts ON futures_macd(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_futures_swing_sym_ctr_tf ON futures_swing_points(symbol, contract, timeframe)",
    "CREATE INDEX IF NOT EXISTS idx_futures_swing_ts ON futures_swing_points(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_futures_n_struct_sym_ctr_tf ON futures_n_structures(symbol, contract, timeframe)",
    "CREATE INDEX IF NOT EXISTS idx_futures_n_struct_state ON futures_n_structures(state)",
    "CREATE INDEX IF NOT EXISTS idx_futures_signals_sym ON futures_signals(symbol)",
    "CREATE INDEX IF NOT EXISTS idx_futures_signals_created ON futures_signals(created_at)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_futures_signals_fp ON futures_signals(fingerprint) WHERE fingerprint != ''",
    "CREATE INDEX IF NOT EXISTS idx_iv_history_sym ON iv_history(symbol)",
    "CREATE INDEX IF NOT EXISTS idx_iv_history_date ON iv_history(date)",
    "CREATE INDEX IF NOT EXISTS idx_options_signals_sym ON options_signals(symbol)",
    "CREATE INDEX IF NOT EXISTS idx_options_signals_created ON options_signals(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_signal_push_log_fp ON signal_push_log(fingerprint)",
    "CREATE INDEX IF NOT EXISTS idx_signal_push_log_pushed ON signal_push_log(pushed_at)",
    "CREATE INDEX IF NOT EXISTS idx_filter_log_created ON filter_decision_log(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_filter_log_symbol ON filter_decision_log(symbol)",
    "CREATE INDEX IF NOT EXISTS idx_filter_log_push_level ON filter_decision_log(push_level)",
    "CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status)",
    "CREATE INDEX IF NOT EXISTS idx_positions_signal ON positions(signal_id)",
    "CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)",
    "CREATE INDEX IF NOT EXISTS idx_trades_position ON trades(position_id)",
    "CREATE INDEX IF NOT EXISTS idx_trades_action ON trades(action)",
]
