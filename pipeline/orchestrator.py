"""
统一调度管线 Orchestrator。

整合期货信号扫描 + 期权策略扫描的完整管线：
    1. 期货扫描：scan_all_contracts → SignalHub.record_futures_signal → 分级推送
    2. 期权扫描：OptionsCollector → 策略计算 → 风控 → SignalHub → 分级推送
    3. 全量扫描：期货 + 期权
    4. 收盘总结：日报格式化输出

入口：``python -m pipeline.orchestrator --mode all``
"""

import argparse
import logging
import os
import time as time_module
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.db import Database
from core.position_tracker import PositionTracker
from core.risk_manager import PositionRiskManager, RiskCheckTriggerResult
from config.settings import DB_PATH, DEDUP_HOURS, SCAN_LIMIT
from config.contracts import ContractRegistry
from data.futures_collector import FuturesCollector
from data.options_collector import OptionsCollector
from data.iv_recorder import IVRecorder
from signals.hub import SignalHub
from signals.formatter import UnifiedFormatter
from signals.dispatcher import dispatch
from signals.smart_filter import SmartFilter
from signals.macos_notifier import notify_signal_summary
from pipeline.n_signal_pipeline import NSignalPipeline as _NSignalPipeline

logger = logging.getLogger(__name__)


class Orchestrator:
    """统一调度器：期货+期权扫描合并管线。

    按需实例化各子系统，提供三种运行模式：
        - ``run_futures_scan()``: 仅期货信号扫描
        - ``run_options_scan(limit)``: 仅期权策略扫描
        - ``run_all(limit)``: 全量扫描
        - ``run_eod()``: 收盘总结模式

    Attributes:
        db: Database 连接工厂。
        registry: ContractRegistry 品种注册表。
        futures_collector: FuturesCollector 期货K线采集器。
        options_collector: OptionsCollector 期权数据采集器。
        iv_recorder: IVRecorder IV历史记录器。
        hub: SignalHub 信号中心。
        formatter: UnifiedFormatter 消息格式化器。
    """

    def __init__(self) -> None:
        """初始化调度器，子系统按需懒加载（首次使用时创建）。"""
        self.db: Database = Database(DB_PATH)
        self._registry: Optional[ContractRegistry] = None
        self._futures_collector: Optional[FuturesCollector] = None
        self._options_collector: Optional[OptionsCollector] = None
        self._iv_recorder: Optional[IVRecorder] = None
        self._hub: Optional[SignalHub] = None
        self._position_tracker: Optional[PositionTracker] = None
        self._risk_manager: Optional[PositionRiskManager] = None
        self._formatter: Optional[UnifiedFormatter] = None
        self._smart_filter: Optional["SmartFilter"] = None
        # ── Telegram 推送模式自动检测 ──────────────────────────
        self._safe_auto_execute: bool = not self._check_telegram_config()
        self._enable_telegram: bool = self._check_telegram_config()
        if self._enable_telegram:
            logger.info("Telegram 推送已配置，启用 Telegram 推送模式")
        else:
            logger.info(
                "Telegram 未配置 (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 为空)，"
                "推送回退到 stdout 模式"
            )

    # ── 懒加载 property ─────────────────────────────────────
    @property
    def registry(self) -> ContractRegistry:
        if self._registry is None:
            self._registry = ContractRegistry(str(DB_PATH))
        return self._registry

    @property
    def futures_collector(self) -> FuturesCollector:
        if self._futures_collector is None:
            self._futures_collector = FuturesCollector(self.db, self.registry)
        return self._futures_collector

    @property
    def options_collector(self) -> OptionsCollector:
        if self._options_collector is None:
            self._options_collector = OptionsCollector(self.registry)
        return self._options_collector

    @property
    def iv_recorder(self) -> IVRecorder:
        if self._iv_recorder is None:
            self._iv_recorder = IVRecorder(self.db)
        return self._iv_recorder

    @property
    def hub(self) -> SignalHub:
        if self._hub is None:
            self._hub = SignalHub(self.db)
        return self._hub

    @property
    def position_tracker(self) -> PositionTracker:
        if self._position_tracker is None:
            self._position_tracker = PositionTracker(self.db)
        return self._position_tracker

    @property
    def risk_manager(self) -> PositionRiskManager:
        if self._risk_manager is None:
            self._risk_manager = PositionRiskManager(self.db, self.position_tracker)
        return self._risk_manager

    @property
    def formatter(self) -> UnifiedFormatter:
        if self._formatter is None:
            self._formatter = UnifiedFormatter()
        return self._formatter

    @staticmethod
    def _check_telegram_config() -> bool:
        """检查 Telegram 推送配置是否齐全。

        优先从 config.settings 读取，兜底读 os.environ。

        Returns:
            True 当 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 均已设置。
        """
        from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            return True
        # 兜底读环境变量（settings 已通过 _load_dotenv() 加载 .env）
        tok = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        cid = os.environ.get("TELEGRAM_CHAT_ID", "")
        return bool(tok and cid)

    @property
    def _push_mode(self) -> str:
        """推送模式：Telegram 已配置时返回 ``'telegram'``，否则 ``'stdout'``。"""
        return "telegram" if self._enable_telegram else "stdout"

    @property
    def smart_filter(self) -> "SmartFilter":
        """懒初始化 SmartFilter 实例。"""
        if self._smart_filter is None:
            self._smart_filter = SmartFilter()
        return self._smart_filter

    # ── 风控检查 ──────────────────────────────────────────────

    def _build_risk_price_map(self) -> dict[str, float]:
        """为当前 Open 持仓构建 {contract: current_price} 价格映射。

        从 futures_klines 表查询每个持仓合约的最新收盘价。
        **优先取 timeframe='1m' 的数据**（最实时）；找不到 1m 数据时
        降级回退到任意周期的最近数据。

        若某合约无 K 线数据，跳过该持仓（风控检查会记录为"无价格数据"）。

        Returns:
            {contract: current_price} 字典，可能为空。
        """
        with self.db.get_conn() as conn:
            open_positions = conn.execute(
                "SELECT DISTINCT contract FROM positions WHERE status='open'"
            ).fetchall()
            if not open_positions:
                return {}

            price_map: dict[str, float] = {}
            for row in open_positions:
                contract = row["contract"]
                # ── 优先取 1m 数据（最实时） ────────────────────────────
                latest = conn.execute(
                    "SELECT close FROM futures_klines "
                    "WHERE contract=? AND timeframe='1m' "
                    "ORDER BY timestamp DESC LIMIT 1",
                    (contract,),
                ).fetchone()
                # ── 降级：无 1m 数据时回退到任意周期 ──────────────────
                if not latest:
                    latest = conn.execute(
                        "SELECT close FROM futures_klines "
                        "WHERE contract=? ORDER BY timestamp DESC LIMIT 1",
                        (contract,),
                    ).fetchone()
                if latest:
                    price_map[contract] = latest["close"]
            return price_map

    def _handle_risk_results(self, results: list[RiskCheckTriggerResult]) -> None:
        """处理风控检查结果：记录日志 + 发送桌面/Telegram 通知。

        只处理 is_triggered() == True 的结果。
        Telegram 推送最多 5 条防刷屏；仅 critical/warning 级别推送。

        Args:
            results: check_all_positions() 的完整返回列表。
        """
        triggered = [r for r in results if r.is_triggered()]
        if not triggered:
            logger.info("风控检查: %d 持仓全部正常，无触发", len(results))
            return

        # 1. 日志（所有触发）
        for r in triggered:
            logger.warning(
                "风控触发 #%d %s %s: action=%s price=%.2f trigger=%.2f alert=%s[%d] %s",
                r.position_id, r.contract, r.direction,
                r.action, r.current_price, r.trigger_price,
                r.alert_level, r.alert_count, r.reason,
            )

        # 2. macOS 桌面通知（更详细信息）
        critical = [r for r in triggered if r.alert_level == "critical"]
        warning = [r for r in triggered if r.alert_level == "warning"]
        info_level = [r for r in triggered if r.alert_level == "info"]

        # 标题：显示最严重持仓 + 统计
        top = triggered[0]
        subtitle = f"#{top.position_id} {top.contract} {UnifiedFormatter._ACTION_CN.get(top.action, top.action)}"
        # 正文：分组摘要
        summary = UnifiedFormatter.format_risk_group_summary(triggered)

        from signals.macos_notifier import notify
        notify(
            title="风控告警",
            subtitle=subtitle,
            text=summary,
            sound=True,
        )

        # 3. Telegram 推送（仅 critical/warning，最多 5 条）
        #    每条使用结构化格式，多条时加汇总头
        if self._enable_telegram:
            push_list = (critical + warning)[:5]
            if len(push_list) > 1:
                # 多条：先发送一条汇总消息
                group_summary = UnifiedFormatter.format_risk_group_summary(push_list)
                header = (
                    f"🚨 **风控批量告警 ({len(push_list)} 条)**\n"
                    f"{group_summary}\n"
                    f"{'─' * 20}"
                )
                dispatch(header, level="URGENT", mode="telegram")

            for r in push_list:
                msg = UnifiedFormatter.format_risk_alert(r)
                dispatch(msg, level="URGENT", mode="telegram")

    # ── 风控自动执行 ──────────────────────────────────────────

    def _check_and_handle_phase1_abort(self) -> Optional[str]:
        """检查 Phase 1 废弃条件，触发时推送告警并记录到 DB。

        Phase 1 废弃条件（二选一）：
          1. 超过 30 天未达 100 笔且胜率未达标 → 废弃
          2. 达成 100 笔但胜率 < 57% → 废弃

        触发时自动执行：
          - 写入 system_config 表（phase1_abort_reason / gradient_strategy_enabled=0）
          - macOS 桌面通知
          - Telegram 推送（如已配置）

        Returns:
            None = 继续运行；str = 废弃原因描述。
        """
        from futures.win_tracker import check_phase1_abort_condition

        # 先检查是否已废弃（避免重复告警）
        with self.db.get_conn() as conn:
            existing = conn.execute(
                "SELECT value FROM system_config WHERE key='gradient_strategy_enabled'"
            ).fetchone()
        if existing and existing["value"] == "0":
            return None  # 已废弃，不再重复触发

        abort_reason = check_phase1_abort_condition(self.db)
        if abort_reason is None:
            return None

        logger.critical("Phase 1 废弃条件触发: %s", abort_reason)

        # 1. 记录到 DB
        now_ts = int(time_module.time())
        with self.db.get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)",
                ("phase1_abort_reason", abort_reason),
            )
            conn.execute(
                "INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)",
                ("phase1_abort_time", str(now_ts)),
            )
            conn.execute(
                "INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)",
                ("gradient_strategy_enabled", "0"),
            )
            conn.commit()

        # 2. macOS 桌面通知
        from signals.macos_notifier import notify
        notify(
            title="🚨 Phase 1 废弃",
            subtitle=abort_reason[:100],
            text=abort_reason,
            sound=True,
        )

        # 3. Telegram 推送（如已配置）
        if self._enable_telegram:
            dispatch(
                f"🚨 **Phase 1 废弃**\n\n{abort_reason}\n\n"
                f"梯度策略已自动关闭。请评估是否需要替代方向。",
                level="URGENT",
                mode="telegram",
            )

        # 4. stdout 醒目日志
        print("=" * 60)
        print(f"  🚨 PHASE 1 ABORTED: {abort_reason}")
        print("  gradient_strategy_enabled → 0 (自动关闭)")
        print("=" * 60)

        return abort_reason

    def _execute_single_trigger(
        self,
        result: RiskCheckTriggerResult,
        close_time: int,
    ) -> bool:
        """执行单个持仓的自动平仓，失败时重试一次。

        Args:
            result: 风控触发结果（含 position_id/action/current_price）。
            close_time: 平仓时间戳（Unix 秒）。

        Returns:
            True 平仓成功，False 失败（重试耗尽）。
        """
        position_id = result.position_id
        close_price = result.current_price

        for attempt in range(2):  # 最多 2 次（首次 + 1 次重试）
            try:
                ok = self.position_tracker.close_position(
                    position_id=position_id,
                    close_price=close_price,
                    close_time=close_time,
                    reason=result.action,  # 'stop_loss' / 'take_profit' / 'trailing_stop'
                )
                if ok:
                    logger.info(
                        "风控自动平仓成功 #%d: %s %s action=%s price=%.2f (attempt=%d)",
                        position_id, result.contract, result.direction,
                        result.action, close_price, attempt + 1,
                    )
                    # 设置 auto_execute=0 + execute_at 防重入（audit trail）
                    with self.db.get_conn() as conn:
                        conn.execute(
                            "UPDATE risk_management SET auto_execute=0, "
                            "execute_at=?, updated_at=datetime('now') "
                            "WHERE position_id=?",
                            (close_time, position_id),
                        )
                        conn.commit()
                    return True
                else:
                    logger.warning(
                        "风控自动平仓返回失败 #%d (attempt=%d): 持仓可能已平仓",
                        position_id, attempt + 1,
                    )
                    # 返回 False 但非异常 → 不重试，可能是已平仓
                    return False
            except Exception as e:
                logger.error(
                    "风控自动平仓异常 #%d (attempt=%d): %s",
                    position_id, attempt + 1, e,
                )

        # 重试耗尽 → 紧急通知（macOS + Telegram）
        logger.critical(
            "风控自动平仓失败(重试耗尽) #%d: %s %s action=%s price=%.2f — 请手动处理！",
            position_id, result.contract, result.direction, result.action, close_price,
        )

        from signals.macos_notifier import notify
        notify(
            title="⚠️ 风控平仓失败",
            subtitle=f"#{position_id} {result.contract} {result.action}",
            text=f"自动平仓失败，请手动处理！",
            sound=True,
        )

        if self._enable_telegram:
            dispatch(
                f"⚠️ **风控平仓失败**\n"
                f"持仓 #{position_id} {result.contract} {result.direction}\n"
                f"动作: {result.action} @ {close_price}\n"
                f"请手动处理！",
                level="URGENT",
                mode="telegram",
            )
        return False

    def _execute_risk_triggers(self, results: list[RiskCheckTriggerResult]) -> None:
        """执行风控触发的自动平仓。

        流程:
            1. 检查全局 kill_switch（system_config 表，关闭时跳过所有执行）
            2. 过滤 is_triggered() == True 且 auto_execute == True 的持仓
            3. 逐一调用 _execute_single_trigger 平仓
            4. 失败自动重试 1 次 + 紧急通知

        Args:
            results: check_all_positions() 的完整返回列表。
        """
        # 1. 检查全局 kill_switch
        conn = self.db.get_conn()
        ks = conn.execute(
            "SELECT value FROM system_config WHERE key='kill_switch'"
        ).fetchone()
        if ks is None or ks["value"] != "1":
            logger.info("风控自动执行: kill_switch 已关闭，跳过自动平仓")
            return

        # 2. 过滤可执行持仓
        executable = [r for r in results if r.is_triggered() and r.auto_execute]
        if not executable:
            return

        logger.info(
            "风控自动执行: %d/%d 持仓需平仓",
            len(executable), len(results),
        )

        now_ts = int(time_module.time())
        for r in executable:
            self._execute_single_trigger(r, now_ts)

    # ── 数据刷新 ──────────────────────────────────────────────

    def data_refresh(self) -> dict:
        """刷新所有品种数据：采集K线 → 聚合 → MACD → 极值点 → N型结构。

        在期货评分前执行，确保信号基于最新数据。

        Returns:
            刷新统计字典。
        """
        logger.info("=" * 50)
        logger.info("数据刷新: 采集 → 聚合 → MACD → 极值点 → N型结构")
        logger.info("=" * 50)
        _t0 = time_module.time()

        from futures.aggregator import aggregate_all
        from futures.macd import calculate_all_timeframes
        from futures.swing_points import update_all_timeframes
        from futures.n_structure import detect_and_save, dynamic_restructure

        # 1. 采集K线
        logger.info("[1/5] 采集K线数据...")
        # trigger_restructure=False: Pipeline 后续步骤 2-5 已包含
        # 聚合→MACD→极值点→N 型重算，避免在此重复触发
        collect_stats = self.futures_collector.collect_all(trigger_restructure=False)

        # 1.5 风控价格采集：为持仓合约采集 1m K 线（更实时价格）
        try:
            with self.db.get_conn() as conn:
                open_contracts = [
                    r["contract"]
                    for r in conn.execute(
                        "SELECT DISTINCT contract FROM positions WHERE status='open'"
                    ).fetchall()
                ]
            if open_contracts:
                logger.info(
                    "[1.5/5] 采集风控价格(1m K线): %s", open_contracts
                )
                risk_stats = self.futures_collector.collect_risk_prices(
                    open_contracts
                )
                logger.info(
                    "  风控价格采集完成: %d 个持仓合约", len(risk_stats)
                )
        except Exception as e:
            logger.warning("风控价格采集异常(已跳过): %s", e)

        # 2. 获取已采集的合约
        with self.db.get_conn() as conn:
            contracts = conn.execute(
                "SELECT DISTINCT symbol, contract FROM futures_klines ORDER BY symbol"
            ).fetchall()

        total = len(contracts)
        if total == 0:
            logger.warning("无品种数据，跳过数据刷新")
            return {}

        logger.info("[2/5] 聚合K线 (%d 品种)...", total)
        agg_total = 0
        for idx, row in enumerate(contracts, 1):
            sym, contract = row["symbol"], row["contract"]
            try:
                c = aggregate_all(sym, contract, self.db)
                agg_total += sum(c.values())
            except Exception as e:
                logger.warning("  聚合失败 %s: %s", sym, e)
            if idx % 10 == 0:
                logger.info("  聚合进度 [%d/%d]", idx, total)

        logger.info("[3/5] 计算MACD (%d 品种)...", total)
        macd_total = 0
        for idx, row in enumerate(contracts, 1):
            sym, contract = row["symbol"], row["contract"]
            try:
                c = calculate_all_timeframes(sym, contract, self.db)
                macd_total += sum(c.values())
            except Exception as e:
                logger.warning("  MACD失败 %s: %s", sym, e)
            if idx % 10 == 0:
                logger.info("  MACD进度 [%d/%d]", idx, total)

        logger.info("[4/5] 更新极值点 (%d 品种)...", total)
        swing_total = 0
        for idx, row in enumerate(contracts, 1):
            sym, contract = row["symbol"], row["contract"]
            try:
                c = update_all_timeframes(sym, contract, self.db)
                swing_total += sum(c.values())
            except Exception as e:
                logger.warning("  极值点失败 %s: %s", sym, e)
            if idx % 10 == 0:
                logger.info("  极值点进度 [%d/%d]", idx, total)

        logger.info("[5/5] 检测N型结构 (%d 品种)...", total)
        n_total = 0
        timeframes = ["3m", "15m", "1h", "1d", "1w"]
        for idx, row in enumerate(contracts, 1):
            sym, contract = row["symbol"], row["contract"]
            for tf in timeframes:
                try:
                    ns = detect_and_save(sym, contract, tf, self.db)
                    if ns.get("is_active"):
                        n_total += 1
                    # 动态重算：检查活跃结构是否需要 A 突破迁移
                    try:
                        dynamic_restructure(sym, contract, tf, self.db)
                    except Exception as e2:
                        logger.debug("  动态重算跳过 %s %s: %s", sym, tf, e2)
                except Exception as e:
                    logger.warning("  N型失败 %s %s: %s", sym, tf, e)
            if idx % 10 == 0:
                logger.info("  N型进度 [%d/%d]", idx, total)

        elapsed = time_module.time() - _t0
        logger.info("数据刷新完成: 品种=%d 聚合=%d MACD=%d 极值点=%d N型=%d (耗时 %.1fs)",
                    total, agg_total, macd_total, swing_total, n_total, elapsed)

        return {
            "collect_stats": collect_stats,
            "contracts": total,
            "aggregated": agg_total,
            "macd": macd_total,
            "swing_points": swing_total,
            "n_structures": n_total,
            "elapsed_seconds": round(elapsed, 1),
        }

    # ── 期货信号扫描 ──────────────────────────────────────────

    def run_futures_scan(self, refresh: bool = True) -> list:
        """运行期货信号扫描。

        流程：
            0. （新增）``data_refresh()`` 刷新K线 → N型结构数据
            1. 调用 ``futures.scorer.scan_all_contracts`` 扫描所有主力合约
            2. 对信号类型非 NONE 的结果写入 futures_signals
            3. 生成去重指纹，检查是否已推送
            4. ENTRY/CANDIDATE 信号分级推送

        Args:
            refresh: 是否在扫描前刷新数据，默认 True。

        Returns:
            SignalResult 列表（按评分降序）。
        """
        if refresh:
            self.data_refresh()
        from futures.scorer import scan_all_contracts

        logger.info("开始期货信号扫描...")
        results = scan_all_contracts(self.db)
        logger.info("期货信号扫描完成: %d 个品种, %d 个非NONE信号",
                     len(results),
                     sum(1 for r in results if getattr(r, "signal_type", "NONE") != "NONE"))

        pushed_count: int = 0
        suppressed_count: int = 0
        for r in results:
            signal_type = getattr(r, "signal_type", "NONE")
            if signal_type == "NONE":
                continue

            # 写入信号表（始终写入，保证数据完整性）
            signal_id = self.hub.record_futures_signal(r)
            if signal_id < 0:
                continue

            # 去重检查
            fingerprint = f"{r.symbol}_{r.contract}_{signal_type}"
            if not self.hub.check_duplicate(fingerprint, hours=DEDUP_HOURS):
                # ── SmartFilter 回测驱动过滤 ──────────────────
                level1_pass = (
                    r.level1.get("passed", False)
                    if isinstance(r.level1, dict) else False
                )
                level2_pass = (
                    r.level2.get("passed", False)
                    if isinstance(r.level2, dict) else False
                )
                decision = self.smart_filter.evaluate(
                    symbol=r.symbol,
                    score=r.overall_score,
                    level1_pass=level1_pass,
                    level2_pass=level2_pass,
                    signal_type=signal_type,
                    direction=getattr(r, "direction", ""),
                )

                # ── 记录过滤决策到数据库 ──────────────────────
                self.hub.record_filter_decision(
                    fingerprint=fingerprint,
                    symbol=r.symbol,
                    contract=r.contract,
                    score=r.overall_score,
                    level1_pass=level1_pass,
                    level2_pass=level2_pass,
                    signal_type=signal_type,
                    direction=getattr(r, "direction", ""),
                    should_push=decision.should_push,
                    push_level=decision.push_level,
                    reason=decision.reason,
                    confidence=decision.confidence,
                    boost_factor=decision.boost_factor,
                )

                if not decision.should_push:
                    logger.info(
                        "被过滤抑制: %s %s score=%.2f (reason: %s)",
                        r.symbol, signal_type, r.overall_score, decision.reason,
                    )
                    suppressed_count += 1
                    continue

                # ── 推送 ──────────────────────────────────────
                msg = self.formatter.format_futures_signal(r)
                dispatch(msg, level=decision.push_level, mode=self._push_mode)

                # 记录推送
                self.hub.record_push(
                    fingerprint=fingerprint,
                    symbol=r.symbol,
                    contract=r.contract,
                    strategy_type="N_signals",
                    strikes=[],
                    score=getattr(r, "overall_score", 0.0),
                )
                pushed_count += 1

                # ── Paper Trading 自动建仓（仅 ENTRY 信号） ──
                if signal_type == "ENTRY":
                    entry_price = getattr(r, "entry_price", 0) or 0
                    direction = getattr(r, "direction", "")
                    if entry_price > 0 and direction in ("LONG", "SHORT"):
                        pos_id = self.position_tracker.open_position(
                            symbol=r.symbol,
                            contract=r.contract,
                            direction=direction,
                            entry_price=entry_price,
                            entry_time=int(time_module.time()),
                            signal_id=signal_id,
                            signal_type="futures",
                            quantity=1,
                            stop_loss=getattr(r, "stop_loss", 0) or 0,
                            take_profit=getattr(r, "take_profit", 0) or 0,
                        )
                        if pos_id:
                            logger.info("自动建仓 #%d: %s %s @ %.2f (ENTRY futures)",
                                        pos_id, r.contract, direction, entry_price)
                            # 初始化浮动盈亏
                            self.position_tracker.update_pnl(pos_id, entry_price)
                    elif entry_price <= 0:
                        logger.warning("跳过期货建仓 %s %s: entry_price=%s (无效或缺失)",
                                       r.symbol, r.contract, entry_price)

                # 避免 API 过载
                if pushed_count > 1:
                    time_module.sleep(0.3)

        logger.info("期货扫描完成: %d 条推送, %d 条被过滤抑制", pushed_count, suppressed_count)

        # ── Telegram 广播：ENTRY 信号汇总推送至所有订阅用户 ──────────
        if self._enable_telegram:
            try:
                from signals.telegram_notifier import broadcast as tg_broadcast
                entry_results = [
                    (r.symbol, r.contract, getattr(r, "direction", ""), r.overall_score)
                    for r in results
                    if getattr(r, "signal_type", "NONE") == "ENTRY"
                ]
                if entry_results:
                    lines = ["🚀 *期货 ENTRY 信号汇总*\n"]
                    for sym, con, direction, score in entry_results:
                        dir_icon = "🟢" if direction == "LONG" else "🔴"
                        lines.append(f"{dir_icon} {sym}({con}) {direction} 评分={score:.1f}")
                    lines.append(f"\n共 {len(entry_results)} 条 ENTRY 信号")
                    tg_broadcast("\n".join(lines))
            except Exception as e:
                logger.warning("ENTRY 广播异常(已跳过): %s", e)

        # ── Phase 1 废弃条件检查 ──────────────────────────────
        try:
            self._check_and_handle_phase1_abort()
        except Exception as e:
            logger.error("Phase 1 废弃检查异常(已跳过): %s", e)

        # ── 风控检查 + 自动执行：为 open 持仓检查 SL/TP/Trailing ────────
        try:
            price_map = self._build_risk_price_map()
            if price_map:
                risk_results = self.risk_manager.check_all_positions(price_map)
                self._handle_risk_results(risk_results)
                self._execute_risk_triggers(risk_results)
        except Exception as e:
            logger.error("风控检查异常(已跳过): %s", e)

        return results

    # ── N 型信号管道 ──────────────────────────────────────────

    def run_n_signal_scan(self, refresh: bool = True) -> list:
        """运行 N 型信号管道（轻量级 N 型 15m B 点突破扫描）。

        相比 run_futures_scan（三级嵌套评分），本管道：
          - 仅依赖 1d N 型结构 + 15m B 点突破
          - 不运行全量 MACD/颜色轨迹验证
          - 适合高频扫描（每 15m 一次）

        流程：
            0. （可选）``data_refresh()`` 刷新数据
            1. 创建 ``NSignalPipeline`` 实例
            2. 调用 ``scan()`` 扫描所有活跃 N 型结构
            3. 去重 + 推送

        Args:
            refresh: 是否在扫描前刷新数据，默认 True。

        Returns:
            NBreakoutSignal 列表（已推送的信号）。
        """
        if refresh:
            self.data_refresh()

        logger.info("开始 N 型信号管道扫描...")
        pipeline = _NSignalPipeline(self.db, self.hub)
        signals = pipeline.scan()
        logger.info("N 型信号管道完成: %d 个信号推送", len(signals))
        return signals

    # ── 期权策略扫描 ──────────────────────────────────────────

    def run_options_scan(self, limit: int = 15) -> list:
        """运行期权策略扫描。

        流程：
            1. 获取 TOP40 期货行情 → OptionsCollector.get_top40_futures()
            2. 获取 IV 状态 → IVRecorder.get_all_status()
            3. 遍历品种 → OptionsCollector.get_option_chain()
            4. 策略计算 (ratio_spread / short_strangle / iron_condor)
            5. 风控检查 → RiskManager.evaluate_signal()
            6. 计算统一评分 → calc_unified_score()
            7. 写入 options_signals 表
            8. 去重推送

        Args:
            limit: 扫描品种数上限，默认 15。

        Returns:
            期权策略信号字典列表。
        """
        logger.info("开始期权策略扫描 (limit=%d)...", limit)

        # 1. 获取 TOP40 期货
        top40 = self.options_collector.get_top40_futures()
        if not top40:
            logger.warning("无期货行情数据，跳过期权扫描")
            return []

        # 2. 获取 IV 状态（构建 symbol → IV状态 映射）
        iv_status_list = self.iv_recorder.get_all_status(days=180)
        iv_status_map: Dict[str, dict] = {
            s["symbol"]: s for s in iv_status_list
        }

        results: list = []
        scanned: int = 0
        pushed_count: int = 0

        for fu in top40[:limit]:
            symbol: str = fu["code"]
            contract: str = fu.get("contract", symbol)
            futures_price: float = fu["price"]
            opt_name: str = self.registry.get_option_name(symbol)

            if not opt_name:
                logger.debug("  %s: 无期权映射，跳过", symbol)
                continue

            scanned += 1
            logger.info("  [%d/%d] %s(%s) ¥%.1f", scanned, limit, fu["name"], contract, futures_price)

            # 3. 获取期权链
            try:
                calls, puts = self.options_collector.get_option_chain(
                    opt_name, contract, futures_price, symbol=symbol
                )
            except Exception as e:
                logger.warning("  获取期权链失败 %s: %s", symbol, e)
                continue

            if not calls and not puts:
                logger.debug("  %s: 无期权数据", symbol)
                continue

            # 合并期权数据为统一格式
            options_data: List[dict] = []
            iv_sum: float = 0.0
            iv_count: int = 0
            for c in calls:
                options_data.append({
                    "call_put": "C",
                    "strike": c["strike"],
                    "price": c["price"],
                    "bid": c.get("price", 0) * 0.95,
                    "ask": c.get("price", 0) * 1.05,
                    "volume": 0,
                    "oi": c.get("oi", 0),
                    "delta": c.get("delta", 0),
                    "gamma": c.get("gamma", 0),
                    "theta": c.get("theta", 0),
                    "vega": c.get("vega", 0),
                    "iv": c.get("iv", 0) * 100,  # ratio_spread.py expects percentage
                })
                iv_sum += c.get("iv", 0)
                iv_count += 1
            for p in puts:
                options_data.append({
                    "call_put": "P",
                    "strike": p["strike"],
                    "price": p["price"],
                    "bid": p.get("price", 0) * 0.95,
                    "ask": p.get("price", 0) * 1.05,
                    "volume": 0,
                    "oi": p.get("oi", 0),
                    "delta": p.get("delta", 0),
                    "gamma": p.get("gamma", 0),
                    "theta": p.get("theta", 0),
                    "vega": p.get("vega", 0),
                    "iv": p.get("iv", 0) * 100,
                })
                iv_sum += p.get("iv", 0)
                iv_count += 1

            iv_avg: float = iv_sum / max(iv_count, 1)

            # 4. IV 状态
            iv_status = iv_status_map.get(symbol, {})
            iv_percentile: float = iv_status.get("percentile", 50.0)
            iv_level: str = iv_status.get("level", "正常")

            # 5. 策略计算
            from options.ratio_spread import find_all_strategies, get_contract_multiplier
            from options.multi_strategy import find_best_short_strangle, find_best_iron_condor

            dte: int = 30  # 默认到期天数估计
            # 估算 DTE
            from data.options_collector import estimate_expiry
            from datetime import date
            try:
                expiry = estimate_expiry(contract)
                dte = max((expiry - date.today()).days, 1)
            except Exception:
                pass

            # 比例价差
            try:
                call_spreads, put_spreads = find_all_strategies(
                    symbol, contract, futures_price, options_data, self.registry,
                    iv_avg=iv_avg, dte=dte,
                )
            except Exception as e:
                logger.warning("  比例价差计算异常 %s: %s", symbol, e)
                call_spreads, put_spreads = [], []

            # 宽跨式
            try:
                strangle = find_best_short_strangle(
                    symbol, contract, futures_price, iv_avg, dte,
                    options_data, self.registry, iv_percentile=iv_percentile,
                )
            except Exception as e:
                logger.warning("  ShortStrangle计算异常 %s: %s", symbol, e)
                strangle = None

            # 铁鹰式
            try:
                iron_condor = find_best_iron_condor(
                    symbol, contract, futures_price, iv_avg, dte,
                    options_data, self.registry, iv_percentile=iv_percentile,
                )
            except Exception as e:
                logger.warning("  IronCondor计算异常 %s: %s", symbol, e)
                iron_condor = None

            # 6. 风控检查 + 信号分类
            from options.risk_manager import RiskManager
            rm = RiskManager()

            # 收集所有策略
            all_strategies: List[Dict[str, Any]] = []
            for spread in call_spreads:
                all_strategies.append({
                    "symbol": symbol,
                    "contract": contract,
                    "strategy": "ratio_spread",
                    "signal_type": "WATCH",
                    "strength": spread.score,
                    "reason": f"看涨比例价差 评分:{spread.score:.1f}",
                    "futures_price": futures_price,
                    "iv_avg": iv_avg,
                    "iv_percentile": iv_percentile,
                    "iv_level": iv_level,
                    "net_delta": spread.net_delta,
                    "net_theta": spread.net_theta,
                    "net_vega": spread.net_vega,
                    "max_profit": spread.max_profit,
                    "max_loss": spread.max_profit * 3 + spread.net_cost,
                    "unified_score": spread.score,
                    "description": f"Call RatioSpread K1={spread.buy_leg.strike:.0f} K2={spread.sell_leg.strike:.0f}",
                    "strategy_details": {
                        "type": "ratio_spread",
                        "side": "call",
                        "underlying": spread.underlying,
                        "iv_avg": iv_avg,
                        "days_to_expiry": dte,
                        "buy_strike": spread.buy_leg.strike,
                        "sell_strike": spread.sell_leg.strike,
                        "net_delta": spread.net_delta,
                        "net_theta": spread.net_theta,
                        "net_vega": spread.net_vega,
                        "net_cost": spread.net_cost,
                        "max_profit": spread.max_profit,
                        "max_loss": spread.max_profit * 3 + spread.net_cost,
                        "breakeven_low": spread.breakeven_low,
                        "breakeven_high": spread.breakeven_high,
                        "profit_zone_width": spread.profit_zone_width,
                        "win_rate": spread.win_rate,
                        "score": spread.score,
                        "score_components": spread.score_components or {},
                        "score_schema": spread.score_schema or {},
                        "margin_required": round(spread.underlying * get_contract_multiplier(self.registry, symbol) * 0.15 * 2, 0),
                        "description": f"Call RatioSpread K1={spread.buy_leg.strike:.0f} K2={spread.sell_leg.strike:.0f}",
                        "legs_detail": f"买Call@{spread.buy_leg.strike:.0f} x1, 卖Call@{spread.sell_leg.strike:.0f} x2",
                        "strikes": [spread.buy_leg.strike, spread.sell_leg.strike],
                    },
                    "strikes": [spread.buy_leg.strike, spread.sell_leg.strike],
                })

            for spread in put_spreads:
                all_strategies.append({
                    "symbol": symbol,
                    "contract": contract,
                    "strategy": "ratio_spread",
                    "signal_type": "WATCH",
                    "strength": spread.score,
                    "reason": f"看跌比例价差 评分:{spread.score:.1f}",
                    "futures_price": futures_price,
                    "iv_avg": iv_avg,
                    "iv_percentile": iv_percentile,
                    "iv_level": iv_level,
                    "net_delta": spread.net_delta,
                    "net_theta": spread.net_theta,
                    "net_vega": spread.net_vega,
                    "max_profit": spread.max_profit,
                    "max_loss": spread.max_profit * 3 + spread.net_cost,
                    "unified_score": spread.score,
                    "description": f"Put RatioSpread K1={spread.buy_leg.strike:.0f} K2={spread.sell_leg.strike:.0f}",
                    "strategy_details": {
                        "type": "ratio_spread",
                        "side": "put",
                        "underlying": spread.underlying,
                        "iv_avg": iv_avg,
                        "days_to_expiry": dte,
                        "buy_strike": spread.buy_leg.strike,
                        "sell_strike": spread.sell_leg.strike,
                        "net_delta": spread.net_delta,
                        "net_theta": spread.net_theta,
                        "net_vega": spread.net_vega,
                        "net_cost": spread.net_cost,
                        "max_profit": spread.max_profit,
                        "max_loss": spread.max_profit * 3 + spread.net_cost,
                        "breakeven_low": spread.breakeven_low,
                        "breakeven_high": spread.breakeven_high,
                        "profit_zone_width": spread.profit_zone_width,
                        "win_rate": spread.win_rate,
                        "score": spread.score,
                        "score_components": spread.score_components or {},
                        "score_schema": spread.score_schema or {},
                        "margin_required": round(spread.underlying * get_contract_multiplier(self.registry, symbol) * 0.15 * 2, 0),
                        "description": f"Put RatioSpread K1={spread.buy_leg.strike:.0f} K2={spread.sell_leg.strike:.0f}",
                        "legs_detail": f"买Put@{spread.buy_leg.strike:.0f} x1, 卖Put@{spread.sell_leg.strike:.0f} x2",
                        "strikes": [spread.sell_leg.strike, spread.buy_leg.strike],
                    },
                    "strikes": [spread.sell_leg.strike, spread.buy_leg.strike],
                })

            if strangle:
                all_strategies.append({
                    "symbol": symbol,
                    "contract": contract,
                    "strategy": "short_strangle",
                    "signal_type": "WATCH",
                    "strength": strangle.get("score", 0),
                    "reason": strangle.get("description", ""),
                    "futures_price": futures_price,
                    "iv_avg": iv_avg,
                    "iv_percentile": iv_percentile,
                    "iv_level": iv_level,
                    "net_delta": strangle.get("net_delta", 0),
                    "net_theta": strangle.get("net_theta", 0),
                    "net_vega": strangle.get("net_vega", 0),
                    "max_profit": strangle.get("max_profit", 0),
                    "max_loss": strangle.get("max_loss", 0),
                    "unified_score": strangle.get("score", 0),
                    "description": strangle.get("description", ""),
                    "strategy_details": strangle,
                    "strikes": strangle.get("strikes", []),
                })

            if iron_condor:
                all_strategies.append({
                    "symbol": symbol,
                    "contract": contract,
                    "strategy": "iron_condor",
                    "signal_type": "WATCH",
                    "strength": iron_condor.get("score", 0),
                    "reason": iron_condor.get("description", ""),
                    "futures_price": futures_price,
                    "iv_avg": iv_avg,
                    "iv_percentile": iv_percentile,
                    "iv_level": iv_level,
                    "net_delta": iron_condor.get("net_delta", 0),
                    "net_theta": iron_condor.get("net_theta", 0),
                    "net_vega": iron_condor.get("net_vega", 0),
                    "max_profit": iron_condor.get("max_profit", 0),
                    "max_loss": iron_condor.get("max_loss", 0),
                    "unified_score": iron_condor.get("score", 0),
                    "description": iron_condor.get("description", ""),
                    "strategy_details": iron_condor,
                    "strikes": iron_condor.get("strikes", []),
                })

            # 7. 风控 + 信号等级划分
            for sig in all_strategies:
                risk_result = rm.evaluate_signal(sig)
                risk_dict = risk_result.to_dict()

                # 合并风控结果到 signal
                sig["risk_passed"] = risk_result.passed
                sig["risk_score"] = risk_result.score
                sig["risk_warnings"] = risk_result.warnings
                if "details" in sig:
                    sig["details"].update(risk_dict.get("details", {}))
                else:
                    sig["details"] = risk_dict.get("details", {})

                # 信号等级划分
                score_val: float = sig.get("unified_score", 0)
                if risk_result.passed and score_val > 70:
                    sig["signal_type"] = "ENTRY"
                elif risk_result.passed or score_val > 40:
                    sig["signal_type"] = "CANDIDATE"
                else:
                    sig["signal_type"] = "WATCH"

                # 8. 写入数据库
                signal_id = self.hub.record_options_signal(sig)
                if signal_id >= 0:
                    results.append(sig)

                # 9. 去重推送（仅 ENTRY）
                if sig["signal_type"] == "ENTRY":
                    strikes = sorted(sig.get("strikes", []))
                    fingerprint = (
                        f"{symbol}_{contract}_{sig['strategy']}_"
                        f"{'_'.join(str(s) for s in strikes)}"
                    )
                    if not self.hub.check_duplicate(fingerprint, hours=DEDUP_HOURS):
                        msg = self.formatter.format_options_strategy(sig)
                        dispatch(msg, level="ENTRY", mode=self._push_mode)
                        self.hub.record_push(
                            fingerprint=fingerprint,
                            symbol=symbol,
                            contract=contract,
                            strategy_type=sig["strategy"],
                            strikes=strikes,
                            score=score_val,
                        )
                        pushed_count += 1

                        # ── Paper Trading 自动建仓（仅策略方向明确的 ENTRY 期权信号） ──
                        strategy_name = sig.get("strategy", "")
                        direction = ""
                        if strategy_name == "ratio_spread":
                            # 使用 net_delta 而非 side 判断方向（P1 #7）
                            net_delta = sig.get("net_delta", 0) or 0
                            direction = "LONG" if net_delta > 0 else (
                                "SHORT" if net_delta < 0 else ""
                            )
                        # short_strangle / iron_condor 为中性策略，跳过自动建仓
                        if direction and sig.get("futures_price", 0) > 0:
                            # 修复 P0 #2: 期权建仓使用净权利金（net_cost），而非期货价格
                            strategy_details = sig.get("strategy_details", {})
                            if isinstance(strategy_details, dict):
                                net_cost = strategy_details.get("net_cost", 0)
                                opt_entry_price = abs(net_cost) if net_cost != 0 else sig["futures_price"]
                            else:
                                opt_entry_price = sig["futures_price"]
                            opt_pos_id = self.position_tracker.open_position(
                                symbol=symbol,
                                contract=contract,
                                direction=direction,
                                entry_price=opt_entry_price,
                                entry_time=int(time_module.time()),
                                signal_id=signal_id,
                                signal_type="options",
                                quantity=1,
                            )
                            if opt_pos_id:
                                logger.info(
                                    "自动建仓 #%d: %s %s @ %.2f (ENTRY option %s)",
                                    opt_pos_id, contract, direction,
                                    opt_entry_price, strategy_name,
                                )
                                self.position_tracker.update_pnl(opt_pos_id, opt_entry_price)

                        time_module.sleep(0.3)

            # 品种间隔
            if scanned < limit:
                time_module.sleep(0.5)

        logger.info("期权扫描完成: %d 品种, %d 策略, %d 条推送",
                     scanned, len(results), pushed_count)
        return results

    # ── 全量扫描 ──────────────────────────────────────────────

    def run_all(self, limit: int = 15) -> dict:
        """运行全量扫描（期货+期权）。

        Args:
            limit: 期权扫描品种数上限。

        Returns:
            扫描结果汇总字典:
            ``{'futures': SignalResult列表, 'options': 期权策略列表}``。
        """
        logger.info("=" * 50)
        logger.info("全量扫描开始 limit=%d", limit)
        logger.info("=" * 50)

        futures_results = self.run_futures_scan()
        options_results = self.run_options_scan(limit=limit)

        # 汇总
        futures_entry = sum(
            1 for r in futures_results
            if getattr(r, "signal_type", "NONE") == "ENTRY"
        )
        options_entry = sum(
            1 for o in options_results if o.get("signal_type") == "ENTRY"
        )

        futures_candidate = sum(
            1 for r in futures_results
            if getattr(r, "signal_type", "NONE") == "CANDIDATE"
        )
        options_candidate = sum(
            1 for o in options_results if o.get("signal_type") == "CANDIDATE"
        )

        logger.info("全量扫描完成: 期货ENTRY=%d CANDIDATE=%d, 期权ENTRY=%d CANDIDATE=%d",
                     futures_entry, futures_candidate, options_entry, options_candidate)

        # ── 风控检查 + 自动执行：为 open 持仓检查 SL/TP/Trailing ────────
        try:
            price_map = self._build_risk_price_map()
            if price_map:
                risk_results = self.risk_manager.check_all_positions(price_map)
                self._handle_risk_results(risk_results)
                self._execute_risk_triggers(risk_results)
        except Exception as e:
            logger.error("风控检查异常(已跳过): %s", e)

        # macOS 本地通知（无需配置，后台 launchd 也能弹窗）
        notify_signal_summary(
            futures_entry=futures_entry,
            futures_candidate=futures_candidate,
            options_entry=options_entry,
            options_candidate=options_candidate,
            total_scanned=len(futures_results),
            sound=(futures_entry + options_entry > 0),
        )

        return {
            "futures": futures_results,
            "options": options_results,
        }

    # ── 收盘总结 ──────────────────────────────────────────────

    def run_eod(self) -> str:
        """收盘总结模式。

        执行全量扫描并格式化日报，通过 dispatch(level='DAILY') 输出。

        Returns:
            格式化后的日报字符串。
        """
        logger.info("收盘总结模式启动...")
        all_results = self.run_all()

        futures_results = all_results["futures"]
        options_results = all_results["options"]
        scanned = len(futures_results)

        daily_msg = self.formatter.format_daily_summary(
            futures_results, options_results, scanned
        )

        # IV 排名附加
        iv_status = self.iv_recorder.get_all_status(days=180)
        if iv_status:
            iv_rank_msg = self.formatter.format_iv_rank(iv_status)
            daily_msg = daily_msg + "\n\n" + iv_rank_msg

        dispatch(daily_msg, level="DAILY", mode=self._push_mode)

        # ── Telegram 广播：日报推送至所有订阅用户 ────────────────────
        if self._enable_telegram:
            try:
                from signals.telegram_notifier import broadcast as tg_broadcast
                tg_broadcast(daily_msg)
            except Exception as e:
                logger.warning("日报广播异常(已跳过): %s", e)

        return daily_msg


def main() -> None:
    """命令行入口。

    用法::

        python -m pipeline.orchestrator --mode all
        python -m pipeline.orchestrator --mode futures
        python -m pipeline.orchestrator --mode options --limit 10
        python -m pipeline.orchestrator --mode eod
    """
    parser = argparse.ArgumentParser(
        description="期货期权统一交易信号平台",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["futures", "options", "all", "eod", "n_signal"],
        default="all",
        help="运行模式: futures=期货扫描, options=期权扫描, all=全量, eod=收盘总结, n_signal=N型信号管道 (默认: all)",
    )
    parser.add_argument(
        "--symbol",
        type=str,
        help="查询单个品种（预留）",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=SCAN_LIMIT,
        help=f"期权扫描品种数上限 (默认: {SCAN_LIMIT})",
    )
    parser.add_argument(
        "--daily-report",
        action="store_true",
        help="输出日报格式",
    )

    args = parser.parse_args()

    # 初始化日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    orch = Orchestrator()

    if args.mode == "futures":
        logger.info("运行模式: 期货信号扫描")
        orch.run_futures_scan()
    elif args.mode == "n_signal":
        logger.info("运行模式: N 型信号管道")
        orch.run_n_signal_scan()
    elif args.mode == "options":
        logger.info("运行模式: 期权策略扫描 limit=%d", args.limit)
        orch.run_options_scan(args.limit)
    elif args.mode == "all":
        logger.info("运行模式: 全量扫描 limit=%d", args.limit)
        orch.run_all(args.limit)
    elif args.mode == "eod":
        logger.info("运行模式: 收盘总结")
        orch.run_eod()


if __name__ == "__main__":
    main()
