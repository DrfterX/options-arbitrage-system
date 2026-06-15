"""
统一信号中心 SignalHub。

负责信号的存储、去重、查询与清理。
所有数据库操作通过 ``core.db.Database`` 工厂获取连接。
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from core.db import Database

logger = logging.getLogger(__name__)

# 去重指纹分隔符
_FINGERPRINT_SEP = "_"


class SignalHub:
    """统一信号中心：存储、查询、去重。

    管理 futures_signals / options_signals / signal_push_log 三张表。
    通过 Database 获取连接，不自行管理连接生命周期。

    Attributes:
        db: Database 连接工厂实例。
    """

    def __init__(self, db: Database) -> None:
        """初始化信号中心。

        Args:
            db: Database 连接工厂。
        """
        self.db = db

    # ── 期货信号 ──────────────────────────────────────────────

    def record_futures_signal(self, result) -> int:
        """将 SignalResult 写入 ``futures_signals`` 表。

        自动计算去重指纹并跳过完全相同的已存在信号。

        Args:
            result: ``futures.scorer.SignalResult`` dataclass 实例，
                包含 symbol / contract / direction / signal_type /
                level1/2/3_pass / entry_price / stop_loss / take_profit /
                overall_score 及 detail(JSON) 等字段。

        Returns:
            新插入记录的 signal_id（整数），或已有信号的 ID（去重命中），
            写入失败返回 -1。
        """
        detail: Dict[str, Any] = {}
        if hasattr(result, "level1"):
            detail["level1"] = result.level1
        if hasattr(result, "level2"):
            detail["level2"] = result.level2
        if hasattr(result, "level3"):
            detail["level3"] = result.level3
        if hasattr(result, "bonus"):
            detail["bonus"] = result.bonus

        detail_json = json.dumps(detail, ensure_ascii=False)

        direction = getattr(result, "direction", "NONE")
        signal_type = getattr(result, "signal_type", "NONE")

        level1_pass = int(getattr(result, "level1", {}).get("passed", 0) if isinstance(getattr(result, "level1", {}), dict) else 0)
        level2_pass = int(getattr(result, "level2", {}).get("passed", 0) if isinstance(getattr(result, "level2", {}), dict) else 0)
        level3_pass = int(getattr(result, "level3", {}).get("passed", 0) if isinstance(getattr(result, "level3", {}), dict) else 0)

        entry_price = getattr(result, "entry_price", None)
        stop_loss = getattr(result, "stop_loss", None)
        take_profit = getattr(result, "take_profit", None)
        score = getattr(result, "overall_score", 0.0)

        # ── 计算去重指纹 ──────────────────────────────────
        entry_str = f"{entry_price:.2f}" if entry_price else "0.00"
        fingerprint = f"{result.symbol}_{result.contract}_{direction}_{signal_type}_{entry_str}"

        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        conn = self.db.get_conn()
        try:
            # 去重检查：同一指纹的信号已存在则不重复插入
            existing = conn.execute(
                "SELECT id FROM futures_signals WHERE fingerprint = ? LIMIT 1",
                (fingerprint,),
            ).fetchone()
            if existing:
                logger.debug(
                    "期货信号去重命中: id=%d %s", existing["id"], fingerprint
                )
                return existing["id"]

            cur = conn.execute(
                """INSERT INTO futures_signals
                   (symbol, contract, direction, signal_type,
                    level1_pass, level2_pass, level3_pass,
                    entry_price, stop_loss, take_profit, score, detail,
                    fingerprint, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    result.symbol,
                    result.contract,
                    direction,
                    signal_type,
                    level1_pass,
                    level2_pass,
                    level3_pass,
                    entry_price,
                    stop_loss,
                    take_profit,
                    score,
                    detail_json,
                    fingerprint,
                    now_utc,
                ),
            )
            conn.commit()
            signal_id: int = cur.lastrowid or -1
            logger.info(
                "期货信号已记录: id=%d %s %s %s score=%.2f fp=%s",
                signal_id, result.symbol, result.contract, signal_type, score, fingerprint,
            )
            return signal_id
        except Exception as e:
            logger.error("记录期货信号失败 %s %s: %s", result.symbol, result.contract, e)
            return -1
        finally:
            pass  # 连接由 Database 管理生命周期

    # ── 期权信号 ──────────────────────────────────────────────

    def record_options_signal(self, signal_dict: dict) -> int:
        """将期权策略信号写入 ``options_signals`` 表。

        Args:
            signal_dict: 期权策略信号字典，至少包含:
                symbol, contract, strategy, signal_type, strength,
                reason, futures_price, iv_avg, iv_percentile, iv_level,
                net_delta, net_theta, net_vega, max_profit, max_loss,
                unified_score, strategy_details(JSON)。

        Returns:
            新插入记录的 signal_id（整数），写入失败返回 -1。
        """
        strategy_details = signal_dict.get("strategy_details", {})
        if isinstance(strategy_details, dict):
            strategy_details_json = json.dumps(strategy_details, ensure_ascii=False)
        else:
            strategy_details_json = str(strategy_details)

        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        conn = self.db.get_conn()
        try:
            cur = conn.execute(
                """INSERT INTO options_signals
                   (symbol, contract, strategy, signal_type, strength,
                    reason, futures_price, iv_avg, iv_percentile, iv_level,
                    net_delta, net_theta, net_vega, max_profit, max_loss,
                    unified_score, strategy_details, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    signal_dict.get("symbol", ""),
                    signal_dict.get("contract", ""),
                    signal_dict.get("strategy", ""),
                    signal_dict.get("signal_type", "WATCH"),
                    float(signal_dict.get("strength", 0)),
                    signal_dict.get("reason", ""),
                    float(signal_dict.get("futures_price", 0)),
                    float(signal_dict.get("iv_avg", 0)),
                    float(signal_dict.get("iv_percentile", 0)),
                    signal_dict.get("iv_level", ""),
                    float(signal_dict.get("net_delta", 0)),
                    float(signal_dict.get("net_theta", 0)),
                    float(signal_dict.get("net_vega", 0)),
                    float(signal_dict.get("max_profit", 0)),
                    float(signal_dict.get("max_loss", 0)),
                    float(signal_dict.get("unified_score", 0)),
                    strategy_details_json,
                    now_utc,
                ),
            )
            conn.commit()
            signal_id: int = cur.lastrowid or -1
            logger.info(
                "期权信号已记录: id=%d %s %s %s score=%.1f",
                signal_id,
                signal_dict.get("symbol"),
                signal_dict.get("contract"),
                signal_dict.get("strategy"),
                signal_dict.get("unified_score", 0),
            )
            return signal_id
        except Exception as e:
            logger.error(
                "记录期权信号失败 %s: %s", signal_dict.get("symbol"), e
            )
            return -1
        finally:
            pass  # 连接由 Database 管理生命周期

    # ── 去重 ──────────────────────────────────────────────────

    def check_duplicate(self, fingerprint: str, hours: int = 12) -> bool:
        """检查指纹在指定小时内是否已推送。

        指纹格式：``'{symbol}_{contract}_{strategy_type}_{sorted_strikes}'``
        如 ``'RB_RB2610_ratio_spread_3500.0_3600.0'``。

        Args:
            fingerprint: 去重指纹字符串。
            hours: 回溯小时数，默认 12（从 ``config.settings.DEDUP_HOURS`` 传入）。

        Returns:
            True 表示已推送（应跳过），False 表示未推送。
        """
        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=hours)
        ).strftime("%Y-%m-%d %H:%M:%S")

        conn = self.db.get_conn()
        try:
            row = conn.execute(
                """SELECT COUNT(*) as cnt FROM signal_push_log
                   WHERE fingerprint = ? AND pushed_at >= ?""",
                (fingerprint, cutoff),
            ).fetchone()
            is_dup: bool = bool(row and row["cnt"] > 0)
            if is_dup:
                logger.debug("去重命中: %s（%d小时内已推送）", fingerprint, hours)
            return is_dup
        except Exception as e:
            logger.warning("去重查询失败: %s", e)
            return False
        finally:
            pass  # 连接由 Database 管理生命周期

    def record_push(
        self,
        fingerprint: str,
        symbol: str,
        contract: str,
        strategy_type: str,
        strikes: list,
        score: float,
    ) -> bool:
        """记录一次推送。

        Args:
            fingerprint: 去重指纹。
            symbol: 品种代码。
            contract: 合约代码。
            strategy_type: 策略类型（如 ``'ratio_spread'`` / ``'N_signals'``）。
            strikes: 行权价列表（用于期权策略）。
            score: 评分。

        Returns:
            True 表示记录成功。
        """
        strikes_str = ",".join(str(s) for s in strikes)
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        conn = self.db.get_conn()
        try:
            conn.execute(
                """INSERT INTO signal_push_log
                   (fingerprint, symbol, contract, strategy_type, strikes, score, pushed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (fingerprint, symbol, contract, strategy_type, strikes_str, score, now_utc),
            )
            conn.commit()
            logger.debug("推送记录: %s", fingerprint)
            return True
        except Exception as e:
            logger.error("记录推送失败 %s: %s", fingerprint, e)
            return False
        finally:
            pass  # 连接由 Database 管理生命周期

    # ── 查询 ──────────────────────────────────────────────────

    def get_recent_futures(self, limit: int = 50) -> list:
        """获取最近期货信号。

        Args:
            limit: 返回条数上限，默认 50。

        Returns:
            期货信号字典列表（按 created_at 降序）。
        """
        conn = self.db.get_conn()
        try:
            rows = conn.execute(
                """SELECT * FROM futures_signals
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            pass  # 连接由 Database 管理生命周期

    def get_recent_options(self, limit: int = 50) -> list:
        """获取最近期权信号。

        Args:
            limit: 返回条数上限，默认 50。

        Returns:
            期权信号字典列表（按 created_at 降序）。
        """
        conn = self.db.get_conn()
        try:
            rows = conn.execute(
                """SELECT * FROM options_signals
                   ORDER BY unified_score DESC, created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            pass  # 连接由 Database 管理生命周期

    # ── 过滤决策日志 ──────────────────────────────────────────

    def record_filter_decision(
        self,
        fingerprint: str,
        symbol: str,
        contract: str,
        score: float,
        level1_pass: bool,
        level2_pass: bool,
        signal_type: str,
        direction: str,
        should_push: bool,
        push_level: str,
        reason: str,
        confidence: float,
        boost_factor: float,
    ) -> bool:
        """记录 SmartFilter 过滤决策到 filter_decision_log 表。

        Args:
            fingerprint: 去重指纹。
            symbol: 品种代码。
            contract: 合约代码。
            score: 信号评分。
            level1_pass: L1 是否通过。
            level2_pass: L2 是否通过。
            signal_type: 信号类型 (WATCH/CANDIDATE/ENTRY)。
            direction: 信号方向 (LONG/SHORT)。
            should_push: 是否推送。
            push_level: 推送等级 (HIGH/NORMAL/LOW/SUPPRESS)。
            reason: 决策理由。
            confidence: 综合置信度。
            boost_factor: 板块加权系数。

        Returns:
            True 表示记录成功。
        """
        conn = self.db.get_conn()
        try:
            conn.execute(
                """INSERT INTO filter_decision_log
                   (fingerprint, symbol, contract, score,
                    level1_pass, level2_pass, signal_type, direction,
                    should_push, push_level, reason, confidence, boost_factor)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    fingerprint,
                    symbol,
                    contract,
                    score,
                    int(level1_pass),
                    int(level2_pass),
                    signal_type,
                    direction,
                    int(should_push),
                    push_level,
                    reason,
                    confidence,
                    boost_factor,
                ),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error("记录过滤决策失败 %s: %s", symbol, e)
            return False
        finally:
            pass  # 连接由 Database 管理生命周期

    def get_filter_stats(self) -> dict:
        """获取 SmartFilter 统计汇总。

        Returns:
            dict: 总评估数/推送数/抑制数/各等级分布。
        """
        conn = self.db.get_conn()
        try:
            total = conn.execute(
                "SELECT COUNT(*) as c FROM filter_decision_log"
            ).fetchone()["c"]

            pushed = conn.execute(
                "SELECT COUNT(*) as c FROM filter_decision_log WHERE should_push=1"
            ).fetchone()["c"]

            suppressed = conn.execute(
                "SELECT COUNT(*) as c FROM filter_decision_log WHERE should_push=0"
            ).fetchone()["c"]

            levels = conn.execute(
                """SELECT push_level, COUNT(*) as c
                   FROM filter_decision_log
                   GROUP BY push_level
                   ORDER BY c DESC"""
            ).fetchall()

            return {
                "total": total,
                "pushed": pushed,
                "suppressed": suppressed,
                "levels": [dict(r) for r in levels],
            }
        finally:
            pass  # 连接由 Database 管理生命周期

    def get_recent_filter_log(self, limit: int = 20) -> list:
        """获取最近的过滤决策日志。

        Args:
            limit: 返回条数上限。

        Returns:
            过滤决策日志列表（按 created_at 降序）。
        """
        conn = self.db.get_conn()
        try:
            rows = conn.execute(
                """SELECT * FROM filter_decision_log
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            pass  # 连接由 Database 管理生命周期

    # ── 清理 ──────────────────────────────────────────────────

    def prune_old(self, days: int = 30) -> int:
        """清理超过指定天数的旧信号和推送日志。

        Args:
            days: 保留天数，默认 30。

        Returns:
            总共删除的行数。
        """
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=days)
        ).strftime("%Y-%m-%d %H:%M:%S")

        conn = self.db.get_conn()
        total_deleted: int = 0
        try:
            cur = conn.execute(
                "DELETE FROM futures_signals WHERE created_at < ?", (cutoff,)
            )
            total_deleted += cur.rowcount
            cur = conn.execute(
                "DELETE FROM options_signals WHERE created_at < ?", (cutoff,)
            )
            total_deleted += cur.rowcount
            cur = conn.execute(
                "DELETE FROM signal_push_log WHERE pushed_at < ?", (cutoff,)
            )
            total_deleted += cur.rowcount
            conn.commit()
            logger.info("清理旧数据: 删除 %d 条 (>%d天前)", total_deleted, days)
            return total_deleted
        except Exception as e:
            logger.error("清理旧数据失败: %s", e)
            return 0
        finally:
            pass  # 连接由 Database 管理生命周期
