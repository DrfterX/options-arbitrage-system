"""
统一品种注册表 ContractRegistry。

提供品种母表管理：60 个国内期货品种的统一查询入口，
包含 symbol、中文名、期权名、交易所、品种类别、合约乘数、
是否有期权、是否有夜盘等信息。

数据持久化到 SQLite 的 symbols 表，首次使用时自动 seed。
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# ============================================================
# 60 个品种默认数据
# 格式: (symbol, name, option_name, exchange, category, multiplier, has_options, is_night)
# ============================================================
DEFAULT_SYMBOLS = [
    # ─── 上海期货交易所 (SHFE) ───
    ("CU", "铜", "铜期权", "SHFE", "金属", 5, 1, 1),
    ("AL", "铝", "铝期权", "SHFE", "金属", 5, 1, 1),
    ("ZN", "锌", "锌期权", "SHFE", "金属", 5, 1, 1),
    ("PB", "铅", "铅期权", "SHFE", "金属", 5, 1, 1),
    ("NI", "镍", "镍期权", "SHFE", "金属", 1, 1, 1),
    ("SN", "锡", "锡期权", "SHFE", "金属", 1, 1, 1),
    ("AU", "黄金", "黄金期权", "SHFE", "金属", 1000, 1, 1),
    ("AG", "白银", "白银期权", "SHFE", "金属", 15, 1, 1),
    ("RB", "螺纹钢", "螺纹钢期权", "SHFE", "黑色", 10, 1, 1),
    ("HC", "热轧卷板", "热轧卷板期权", "SHFE", "黑色", 10, 1, 1),
    ("RU", "橡胶", "橡胶期权", "SHFE", "能化", 10, 1, 1),
    ("BU", "沥青", "沥青期权", "SHFE", "能化", 10, 1, 1),
    ("SP", "纸浆", "纸浆期权", "SHFE", "能化", 10, 1, 1),
    ("BR", "合成橡胶", "合成橡胶期权", "SHFE", "能化", 5, 1, 1),
    ("SS", "不锈钢", "不锈钢期权", "SHFE", "金属", 5, 1, 1),
    ("AO", "氧化铝", "氧化铝期权", "SHFE", "金属", 20, 1, 1),

    # ─── 上海国际能源交易中心 (INE) ───
    ("SC", "原油", "原油期权", "INE", "能化", 1000, 1, 1),
    ("LU", "LU燃油", "LU燃油期权", "INE", "能化", 10, 1, 1),
    ("NR", "20号胶", "20号胶期权", "INE", "能化", 10, 1, 1),

    # ─── 大连商品交易所 (DCE) ───
    ("M", "豆粕", "豆粕期权", "DCE", "油脂", 10, 1, 1),
    ("C", "玉米", "玉米期权", "DCE", "农副", 10, 1, 1),
    ("CS", "玉米淀粉", "玉米淀粉期权", "DCE", "农副", 10, 1, 1),
    ("Y", "豆油", "豆油期权", "DCE", "油脂", 10, 1, 1),
    ("P", "棕榈油", "棕榈油期权", "DCE", "油脂", 10, 1, 1),
    ("I", "铁矿石", "铁矿石期权", "DCE", "黑色", 100, 1, 1),
    ("J", "焦炭", "焦炭期权", "DCE", "黑色", 100, 1, 1),
    ("JM", "焦煤", "焦煤期权", "DCE", "黑色", 60, 1, 1),
    ("L", "聚乙烯", "聚乙烯期权", "DCE", "能化", 5, 1, 1),
    ("V", "聚氯乙烯", "聚氯乙烯期权", "DCE", "能化", 5, 1, 1),
    ("PP", "聚丙烯", "聚丙烯期权", "DCE", "能化", 5, 1, 1),
    ("EG", "乙二醇", "乙二醇期权", "DCE", "能化", 10, 1, 1),
    ("EB", "苯乙烯", "苯乙烯期权", "DCE", "能化", 5, 1, 1),
    ("PG", "LPG", "液化石油气期权", "DCE", "能化", 20, 1, 1),
    ("LH", "生猪", "生猪期权", "DCE", "农副", 16, 1, 0),
    ("JD", "鸡蛋", "鸡蛋期权", "DCE", "农副", 10, 1, 0),
    ("A", "豆一", "豆一期权", "DCE", "油脂", 10, 1, 1),
    ("B", "豆二", "豆二期权", "DCE", "油脂", 10, 1, 1),
    ("RR", "粳米", "粳米期权", "DCE", "农副", 10, 1, 0),

    # ─── 郑州商品交易所 (CZCE) ───
    ("MA", "甲醇", "甲醇期权", "CZCE", "能化", 10, 1, 1),
    ("TA", "PTA", "PTA期权", "CZCE", "能化", 5, 1, 1),
    ("RM", "菜粕", "菜籽粕期权", "CZCE", "油脂", 10, 1, 1),
    ("CF", "棉花", "棉花期权", "CZCE", "农副", 5, 1, 1),
    ("SR", "白糖", "白糖期权", "CZCE", "农副", 10, 1, 1),
    ("OI", "菜籽油", "菜籽油期权", "CZCE", "油脂", 10, 1, 1),
    ("FG", "玻璃", "玻璃期权", "CZCE", "能化", 20, 1, 1),
    ("SA", "纯碱", "纯碱期权", "CZCE", "能化", 20, 1, 1),
    ("UR", "尿素", "尿素期权", "CZCE", "能化", 20, 1, 1),
    ("SH", "烧碱", "烧碱期权", "CZCE", "能化", 30, 1, 1),
    ("SF", "硅铁", "硅铁期权", "CZCE", "黑色", 5, 1, 0),
    ("SM", "锰硅", "锰硅期权", "CZCE", "黑色", 5, 1, 0),
    ("PK", "花生", "花生期权", "CZCE", "农副", 5, 1, 0),
    ("CJ", "红枣", "红枣期权", "CZCE", "农副", 5, 1, 0),
    ("PF", "短纤", "短纤期权", "CZCE", "能化", 5, 1, 1),
    ("PX", "对二甲苯", "对二甲苯期权", "CZCE", "能化", 5, 1, 1),
    ("PR", "瓶片", "瓶片期权", "CZCE", "能化", 5, 1, 1),
    ("AP", "苹果", "苹果期权", "CZCE", "农副", 10, 1, 0),

    # ─── 广州期货交易所 (GFEX) ───
    ("SI", "工业硅", "工业硅期权", "GFEX", "能化", 5, 1, 0),
    ("LC", "碳酸锂", "碳酸锂期权", "GFEX", "金属", 1, 1, 0),
    ("PS", "多晶硅", "多晶硅期权", "GFEX", "能化", 5, 1, 0),

    # ─── 中国金融期货交易所 (CFFEX) ───
    ("IF", "沪深300", "", "CFFEX", "股指", 300, 0, 0),
    ("IH", "上证50", "", "CFFEX", "股指", 300, 0, 0),
    ("IM", "中证1000", "", "CFFEX", "股指", 200, 0, 0),
]

# ============================================================
# 列名映射
# ============================================================
_COLUMNS = [
    "symbol", "name", "option_name", "exchange", "category",
    "multiplier", "has_options", "is_night",
]


class ContractRegistry:
    """统一品种注册表。

    管理 60 个国内期货品种的母表数据，提供按条件筛选的查询接口。
    数据存储于 SQLite 的 ``symbols`` 表中。

    内部缓存一个长连接，避免 macOS WAL 模式下短连接频繁
    connect/disconnect 触发的 SQLITE_CANTOPEN 竞争。

    Attributes:
        db_path: SQLite 数据库文件路径字符串。
    """

    def __init__(self, db_path: str) -> None:
        """初始化品种注册表。

        Args:
            db_path: SQLite 数据库文件路径。
        """
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._ensure_seeded()

    # ── 内部方法 ─────────────────────────────────────────────

    def _get_conn(self) -> sqlite3.Connection:
        """获取数据库连接（缓存单例，避免短连接 WAL 竞争）。

        与 core/db.py 同样的长连接策略：首次调用创建连接并缓存，
        后续复用。with 上下文退出时只 commit/rollback 不 close。
        """
        if self._conn is not None:
            try:
                self._conn.execute("SELECT 1")
                return self._conn
            except (sqlite3.ProgrammingError, sqlite3.OperationalError):
                self._conn = None

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        self._conn = conn
        return conn

    def _ensure_seeded(self) -> None:
        """确保 symbols 表存在且已填充默认品种数据。

        仅当表为空时才插入 DEFAULT_SYMBOLS，实现幂等。
        """
        with self._get_conn() as conn:
            # 先确保表存在
            conn.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    symbol     TEXT PRIMARY KEY,
                    name       TEXT NOT NULL,
                    option_name TEXT DEFAULT '',
                    exchange   TEXT NOT NULL,
                    category   TEXT NOT NULL,
                    multiplier INTEGER DEFAULT 1,
                    has_options INTEGER DEFAULT 0,
                    is_night   INTEGER DEFAULT 0,
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            """)
            cursor = conn.execute("SELECT COUNT(*) as cnt FROM symbols")
            row = cursor.fetchone()
            if row and row["cnt"] == 0:
                self._seed_defaults(conn)

    def _seed_defaults(self, conn: sqlite3.Connection) -> None:
        """向 symbols 表插入 DEFAULT_SYMBOLS 初始数据。"""
        sql = (
            "INSERT OR REPLACE INTO symbols "
            "(symbol, name, option_name, exchange, category, multiplier, has_options, is_night) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        )
        conn.executemany(sql, DEFAULT_SYMBOLS)
        conn.commit()
        logger.info("已写入 %d 个默认品种到 symbols 表", len(DEFAULT_SYMBOLS))

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """将 sqlite3.Row 转为普通字典。"""
        return dict(row) if row else {}

    def _rows_to_list(self, rows) -> List[dict]:
        """将 Row 迭代器转为字典列表。"""
        return [dict(r) for r in rows]

    # ── 公开查询接口 ─────────────────────────────────────────

    def get(self, symbol: str) -> dict:
        """查询单个品种信息。

        Args:
            symbol: 品种代码，如 'RB'、'CU'。

        Returns:
            品种信息字典，未找到时返回空字典。
        """
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM symbols WHERE symbol = ?", (symbol.upper(),)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row)

    def get_all(self) -> List[dict]:
        """获取全部品种。

        Returns:
            所有品种的字典列表，按 symbol 排序。
        """
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM symbols ORDER BY symbol")
            return self._rows_to_list(cursor.fetchall())

    def get_with_options(self) -> List[dict]:
        """获取已上市期权的品种。

        Returns:
            has_options=1 的品种字典列表。
        """
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM symbols WHERE has_options = 1 ORDER BY symbol"
            )
            return self._rows_to_list(cursor.fetchall())

    def get_night_symbols(self) -> Set[str]:
        """获取有夜盘的品种代码集合。

        Returns:
            包含夜盘品种 symbol 的集合，如 {'RB', 'CU', ...}。
        """
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT symbol FROM symbols WHERE is_night = 1"
            )
            return {r["symbol"] for r in cursor.fetchall()}

    def get_option_name(self, symbol: str) -> str:
        """查询品种的期权名称。

        Args:
            symbol: 品种代码。

        Returns:
            期权名称字符串，无期权时返回空字符串。
        """
        info = self.get(symbol)
        return info.get("option_name", "")

    def get_multiplier(self, symbol: str) -> int:
        """查询合约乘数。

        Args:
            symbol: 品种代码。

        Returns:
            合约乘数，未找到时返回 1。
        """
        info = self.get(symbol)
        return int(info.get("multiplier", 1))

    # ── AKShare 刷新接口 ─────────────────────────────────────

    def refresh_from_akshare(self) -> int:
        """从 AKShare 补充合约信息（预留实现）。

        当前实现：返回已注册的品种总数。
        后续可扩展为调用 akshare 获取主力合约映射并 Update symbols 表。

        Returns:
            已注册品种总数。
        """
        logger.info("refresh_from_akshare: 使用默认 seed 数据（AKShare 在线刷新预留）")
        return len(self.get_all())
