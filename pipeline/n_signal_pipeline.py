"""
N 型信号管道 — 定时扫描活跃 N 型结构的 15m B 点突破信号。

基于 S.2.2.5 规格实现：
    1. 读取 DB 中 1d 时段的活跃 N 型结构
    2. 对每个活跃结构检查 15m B 点突破（fresh breakout）
    3. 生成 SignalResult 兼容 futures_signals 表
    4. 去重 + 推送（Telegram / stdout）

接入 orchestrator：
    orch = Orchestrator()
    orch.run_n_signal_scan()   # 单独运行 N 型信号扫描

用法:
    python -m pipeline.n_signal_pipeline                          # 全部品种
    python -m pipeline.n_signal_pipeline --symbol RB              # 单品种
"""

import logging
import time as time_module
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.db import Database
from config.settings import DB_PATH, DEDUP_HOURS
from signals.hub import SignalHub
from signals.dispatcher import dispatch
from signals.formatter import UnifiedFormatter
from futures.n_structure import (
    _get_active_n_structure,
    check_15m_breakout,
    check_realtime_breakout,
    dynamic_restructure,
    get_current_price,
    get_last_bar,
)

logger = logging.getLogger(__name__)

# ── 常量 ───────────────────────────────────────────────────────

N_TIMEFRAME = "1d"           # N 型结构检测周期
BREAKOUT_TIMEFRAME = "15m"   # 突破检测周期
SIGNAL_EXPIRY_S = 10 * 86400  # 信号有效期 10 天
DEFAULT_FRESHNESS = 30 * 86400  # N 型新鲜度 30 天

# 信号等级 emoji
_LEVEL_EMOJI = {
    "ENTRY": "🔴",
    "CANDIDATE": "🟡",
    "WATCH": "🔵",
    "NONE": "⚪",
}

_DIRECTION_CN = {
    "LONG": "多头",
    "SHORT": "空头",
}


@dataclass
class NBreakoutSignal:
    """N 型突破信号结果（轻量版，用于内部传递）。

    Attributes:
        symbol: 品种代码。
        contract: 合约代码。
        direction: LONG / SHORT。
        signal_type: ENTRY / CANDIDATE / WATCH。
        score: 信号评分 (0-1)。
        n_structure: N 型结构字典（来自 DB）。
        breakout: 突破检测结果字典。
        entry_price: 入场价格（突破触发价）。
        stop_loss: 止损价。
        take_profit: 止盈价。
        fingerprint: 去重指纹。
    """
    symbol: str
    contract: str
    direction: str
    signal_type: str = "WATCH"
    score: float = 0.0
    n_structure: dict = field(default_factory=dict)
    breakout: dict = field(default_factory=dict)
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    fingerprint: str = ""


def _calc_sl_tp(
    direction: str,
    entry_price: float,
    n_structure: dict,
) -> tuple:
    """计算止损止盈价。

    止损：N 型结构 A 点（结构失效点）。
    止盈：参考距离（|B - A|）作为 1:1 目标。

    Args:
        direction: LONG / SHORT。
        entry_price: 入场价格。
        n_structure: N 型结构字典。

    Returns:
        (stop_loss, take_profit) 或 (None, None)。
    """
    a_price = n_structure.get("point_a_price")
    b_price = n_structure.get("point_b_price")

    if a_price is None or b_price is None or entry_price is None:
        return None, None

    # 参考距离 = max(|B-A|, |C-B|)
    c_price = n_structure.get("point_c_price")
    ref_dist = max(
        abs(b_price - a_price),
        abs(c_price - b_price) if c_price else abs(b_price - a_price),
    )
    if ref_dist <= 0:
        ref_dist = abs(b_price - a_price) * 0.02  # 兜底 2%

    if direction == "LONG":
        sl = a_price
        tp = entry_price + ref_dist
    else:
        sl = a_price
        tp = entry_price - ref_dist

    return round(sl, 2), round(tp, 2)


def _calc_score(n_structure: dict, breakout: dict) -> float:
    """计算 N 型突破信号评分 (0-1)。

    基础分 0.5 + 加分项：
      - LEG3 状态 +0.2（结构成熟）
      - N 型新鲜 < 7 天 +0.15
      - 突破距离 > 参考距离 50% +0.15

    Args:
        n_structure: N 型结构字典。
        breakout: 突破检测结果字典。

    Returns:
        [0, 1] 的评分。
    """
    score = 0.5

    # LEG3 状态加分（结构更成熟）
    state = n_structure.get("state", "")
    if state == "LEG3":
        score += 0.2

    # 新鲜度加分（7 天内）
    now = int(time_module.time())
    pc_time = n_structure.get("point_c_time") or n_structure.get("point_b_time", 0)
    if pc_time and (now - pc_time) < 7 * 86400:
        score += 0.15

    # 突破距离加分
    b_price = n_structure.get("point_b_price")
    a_price = n_structure.get("point_a_price")
    trigger_price = breakout.get("trigger_price", 0)
    if b_price and a_price and trigger_price:
        ref_dist = abs(b_price - a_price)
        if ref_dist > 0:
            brk_dist = abs(trigger_price - b_price)
            if brk_dist / ref_dist > 0.5:
                score += 0.15

    return min(round(score, 2), 1.0)


def _determine_signal_type(score: float, is_fresh: bool) -> str:
    """根据评分和新鲜度决定信号类型。

    Args:
        score: 综合评分 [0, 1]。
        is_fresh: 是否为新鲜突破。

    Returns:
        'ENTRY' / 'CANDIDATE' / 'WATCH'。
    """
    if is_fresh and score >= 0.7:
        return "ENTRY"
    elif score >= 0.5:
        return "CANDIDATE"
    return "WATCH"


def _build_fingerprint(symbol: str, contract: str, direction: str) -> str:
    """构建去重指纹。

    Args:
        symbol: 品种代码。
        contract: 合约代码。
        direction: 方向。

    Returns:
        指纹字符串。
    """
    return f"{symbol}_{contract}_{direction}_NSIGNAL"


def _format_signal_message(sig: NBreakoutSignal) -> str:
    """格式化 N 型突破信号为人类可读消息。

    Args:
        sig: NBreakoutSignal 实例。

    Returns:
        格式化后的多行消息字符串。
    """
    emoji = _LEVEL_EMOJI.get(sig.signal_type, "⚪")
    dir_cn = _DIRECTION_CN.get(sig.direction, sig.direction)

    lines = [
        f"{'─' * 8} N 型突破信号 {'─' * 8}",
        f"{emoji} **{sig.symbol} {sig.contract}** | {dir_cn} | {sig.signal_type}",
        f"   评分: {sig.score:.2f}",
        f"   入场: {sig.entry_price:.1f}" if sig.entry_price else "",
        f"   止损: {sig.stop_loss:.1f}" if sig.stop_loss else "",
        f"   止盈: {sig.take_profit:.1f}" if sig.take_profit else "",
        "",
    ]

    ns = sig.n_structure
    lines.append("N 型结构:")
    lines.append(f"   A: {ns.get('point_a_price', '?')} @ t={ns.get('point_a_time', '?')}")
    lines.append(f"   B: {ns.get('point_b_price', '?')} @ t={ns.get('point_b_time', '?')}")
    lines.append(f"   C: {ns.get('point_c_price', '?')} @ t={ns.get('point_c_time', '?')}")
    lines.append(f"   状态: {ns.get('state', '?')}")

    brk = sig.breakout
    if brk.get("triggered"):
        lines.append(f"\n✅ 突破: B={brk.get('breakout_price', '?')} 触发={brk.get('trigger_price', '?')}")

    lines.append("")
    lines.append(f"#{sig.fingerprint}")

    return "\n".join(line for line in lines if line)


# ═══════════════════════════════════════════════════════════════
# 核心扫描逻辑
# ═══════════════════════════════════════════════════════════════


class NSignalPipeline:
    """N 型信号扫描管道。

    定时（每 15m）扫描活跃 N 型结构的 15m B 点突破信号。

    Attributes:
        db: Database 实例。
        hub: SignalHub 实例。
        contract_registry: ContractRegistry 实例（可选）。
        target_symbols: 目标品种列表，None 表示全部。
    """

    def __init__(
        self,
        db: Database,
        hub: SignalHub,
        target_symbols: Optional[List[str]] = None,
    ) -> None:
        """初始化管道。

        Args:
            db: Database 连接工厂。
            hub: SignalHub 信号中心。
            target_symbols: 目标品种列表，None=全部（默认）。
        """
        self.db = db
        self.hub = hub
        self.target_symbols = target_symbols

    def _get_active_symbols(self) -> List[Dict[str, Any]]:
        """获取有活跃 N 型结构的品种列表。

        Returns:
            [{'symbol': str, 'contract': str}, ...]。
        """
        with self.db.get_conn() as conn:
            rows = conn.execute(
                """SELECT DISTINCT n.symbol, n.contract
                   FROM futures_n_structures n
                   WHERE n.timeframe = ?
                     AND n.state != 'COMPLETED'
                     AND n.state != 'IDLE'
                   ORDER BY n.symbol""",
                (N_TIMEFRAME,),
            ).fetchall()

        results = [dict(r) for r in rows]

        if self.target_symbols:
            results = [r for r in results if r["symbol"] in self.target_symbols]

        return results

    def _get_active_n_structure(self, symbol: str, contract: str) -> Optional[Dict]:
        """获取指定品种的活跃 N 型结构（1d）。

        Args:
            symbol: 品种代码。
            contract: 合约代码。

        Returns:
            N 型结构字典，或 None。
        """
        try:
            return _get_active_n_structure(self.db, symbol, contract, N_TIMEFRAME)
        except Exception as e:
            logger.warning("获取 N 型结构失败 %s: %s", symbol, e)
            return None

    def _check_breakout(self, symbol: str, contract: str, n_structure: dict) -> dict:
        """检查 15m B 点突破。

        Args:
            symbol: 品种代码。
            contract: 合约代码。
            n_structure: N 型结构字典。

        Returns:
            突破检测结果字典。
        """
        try:
            return check_realtime_breakout(symbol, contract, n_structure, self.db)
        except Exception as e:
            logger.warning("突破检测失败 %s: %s", symbol, e)
            return {"triggered": False, "detail": f"异常: {e}"}

    def _get_contract_for_symbol(self, symbol: str) -> Optional[str]:
        """获取品种的主力合约代码。

        Args:
            symbol: 品种代码。

        Returns:
            合约代码，或 None。
        """
        with self.db.get_conn() as conn:
            row = conn.execute(
                """SELECT contract FROM futures_klines
                   WHERE symbol = ? AND timeframe = '1d'
                   ORDER BY timestamp DESC LIMIT 1""",
                (symbol,),
            ).fetchone()
        return row["contract"] if row else None

    def scan_symbol(self, symbol: str, contract: str) -> Optional[NBreakoutSignal]:
        """扫描单个品种的 N 型突破信号。

        流程：
            0. 动态重算：检查 N 型结构是否需要 A 突破迁移（确保结构最新）
            1. 获取活跃 N 型结构（1d 周期）
            2. 检查 15m B 点突破
            3. 计算入场价、止损止盈
            4. 计算评分和信号类型
            5. 构建指纹

        Args:
            symbol: 品种代码。
            contract: 合约代码。

        Returns:
            NBreakoutSignal 或 None（无信号）。
        """
        # 0. 动态重算：检查 N 型结构是否需要 A 突破迁移
        #     确保 breakout 检测基于最新结构，而非可能已失效的旧结构
        try:
            dynamic_restructure(symbol, contract, N_TIMEFRAME, self.db)
        except Exception as e:
            logger.debug("  %s: 动态重算跳过 (%s)", symbol, e)

        # 1. 获取活跃 N 型结构
        n_structure = self._get_active_n_structure(symbol, contract)
        if not n_structure:
            logger.debug("  %s: 无活跃 N 型结构", symbol)
            return None

        direction = n_structure.get("direction", "")
        if direction not in ("LONG", "SHORT"):
            logger.debug("  %s: N 型方向无效: %s", symbol, direction)
            return None

        logger.debug("  %s: 活跃 N 型 %s (state=%s)", symbol, direction, n_structure.get("state"))

        # 2. 检查 15m B 点突破
        breakout = self._check_breakout(symbol, contract, n_structure)
        if not breakout.get("is_fresh", False):
            detail = breakout.get("detail", "")
            logger.debug("  %s: 无新鲜突破 (%s)", symbol, detail)
            return None

        # 3. 计算入场价、止损止盈
        trigger_price = breakout.get("trigger_price", 0)
        if not trigger_price:
            logger.debug("  %s: 突破价格无效", symbol)
            return None

        sl, tp = _calc_sl_tp(direction, trigger_price, n_structure)

        # 4. 计算评分和信号类型
        score = _calc_score(n_structure, breakout)
        is_fresh = breakout.get("is_fresh", False)
        signal_type = _determine_signal_type(score, is_fresh)

        # 5. 构建指纹
        fingerprint = _build_fingerprint(symbol, contract, direction)

        sig = NBreakoutSignal(
            symbol=symbol,
            contract=contract,
            direction=direction,
            signal_type=signal_type,
            score=score,
            n_structure=n_structure,
            breakout=breakout,
            entry_price=trigger_price,
            stop_loss=sl,
            take_profit=tp,
            fingerprint=fingerprint,
        )
        return sig

    def process_signal(self, sig: NBreakoutSignal) -> bool:
        """处理单个信号：去重 → 记录 → 推送。

        Args:
            sig: NBreakoutSignal 实例。

        Returns:
            True 表示已推送，False 表示被去重或跳过。
        """
        # 1. 去重检查
        if self.hub.check_duplicate(sig.fingerprint, hours=DEDUP_HOURS):
            logger.info("  去重跳过: %s", sig.fingerprint)
            return False

        # 2. 记录信号到 futures_signals
        #    构造 SignalResult 兼容格式
        from futures.scorer import SignalResult

        result = SignalResult(
            symbol=sig.symbol,
            contract=sig.contract,
            direction=sig.direction,
            signal_type=sig.signal_type,
            overall_score=sig.score,
            entry_price=sig.entry_price,
            stop_loss=sig.stop_loss,
            take_profit=sig.take_profit,
            level1={
                "passed": True,
                "direction": sig.direction,
                "state": sig.n_structure.get("state", ""),
                "n_structure": sig.n_structure,
                "description": (
                    f"{sig.direction} {sig.signal_type} "
                    f"N型突破 @ {sig.entry_price:.1f}"
                ),
            },
            level2={
                "passed": True,
                "breakout": sig.breakout,
                "description": (
                    f"15m B点突破: "
                    f"B={sig.breakout.get('breakout_price', '?')} "
                    f"触发={sig.entry_price:.1f}"
                ),
            },
            level3={},
            bonus=[],
        )

        signal_id = self.hub.record_futures_signal(result)
        if signal_id < 0:
            logger.warning("  记录信号失败: %s", sig.fingerprint)
            return False

        # 3. 推送
        msg = _format_signal_message(sig)
        push_level = "URGENT" if sig.signal_type == "ENTRY" else sig.signal_type
        dispatch(msg, level=push_level, mode="stdout")

        # 尝试 Telegram 推送（自动检测配置）
        try:
            dispatch(msg, level=push_level, mode="telegram")
        except Exception as e:
            logger.debug("  Telegram 推送尝试失败(可忽略): %s", e)

        # 4. 记录推送日志
        self.hub.record_push(
            fingerprint=sig.fingerprint,
            symbol=sig.symbol,
            contract=sig.contract,
            strategy_type="N_signals",
            strikes=[],
            score=sig.score,
        )

        logger.info(
            "  ✅ 已推送 %s %s %s score=%.2f signal_id=%d fp=%s",
            sig.symbol, sig.direction, sig.signal_type,
            sig.score, signal_id, sig.fingerprint,
        )
        return True

    def scan(self) -> List[NBreakoutSignal]:
        """运行完整扫描管道。

        Returns:
            所有已推送的信号列表。
        """
        logger.info("=" * 50)
        logger.info("N 型信号管道扫描开始")
        logger.info("=" * 50)

        _t0 = time_module.time()

        # 1. 获取活跃品种
        active = self._get_active_symbols()
        if not active:
            logger.info("无活跃 N 型结构，扫描结束")
            return []

        logger.info("活跃 N 型品种: %d 个", len(active))

        # 2. 逐品种扫描
        pushed_signals: List[NBreakoutSignal] = []
        for idx, row in enumerate(active, 1):
            symbol = row["symbol"]
            contract = row.get("contract") or self._get_contract_for_symbol(symbol)
            if not contract:
                logger.debug("  [%d/%d] %s: 无合约，跳过", idx, len(active), symbol)
                continue

            logger.info("  [%d/%d] %s (%s)", idx, len(active), symbol, contract)

            try:
                sig = self.scan_symbol(symbol, contract)
                if sig is not None:
                    pushed = self.process_signal(sig)
                    if pushed:
                        pushed_signals.append(sig)
            except Exception as e:
                logger.error("  扫描异常 %s: %s", symbol, e)

        elapsed = time_module.time() - _t0
        logger.info(
            "扫描完成: %d 品种, %d 信号推送 (%.1fs)",
            len(active), len(pushed_signals), elapsed,
        )
        return pushed_signals


# ═══════════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════════


def run_scan(
    db_path: str = str(DB_PATH),
    target_symbols: Optional[List[str]] = None,
) -> List[NBreakoutSignal]:
    """便捷入口：创建实例并运行扫描。

    Args:
        db_path: 数据库路径。
        target_symbols: 目标品种列表，None=全部。

    Returns:
        已推送的信号列表。
    """
    db = Database(db_path)
    hub = SignalHub(db)
    pipeline = NSignalPipeline(db, hub, target_symbols=target_symbols)
    return pipeline.scan()


def main() -> None:
    """命令行入口。

    用法::
        python -m pipeline.n_signal_pipeline                    # 全部品种
        python -m pipeline.n_signal_pipeline --symbol RB        # 单品种
        python -m pipeline.n_signal_pipeline --symbol RB,Y,P    # 多品种
    """
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="N 型信号管道")
    parser.add_argument("--symbol", "-s", default="", help="品种(逗号分隔, 默认全部)")
    parser.add_argument("--db", default=str(DB_PATH), help="数据库路径")
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbol.split(",") if s.strip()] if args.symbol else None

    signals = run_scan(db_path=args.db, target_symbols=symbols)
    print(f"\n共推送 {len(signals)} 个 N 型突破信号")


if __name__ == "__main__":
    main()
