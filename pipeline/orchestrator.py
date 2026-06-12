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
from config.settings import DB_PATH, DEDUP_HOURS, SCAN_LIMIT
from config.contracts import ContractRegistry
from data.futures_collector import FuturesCollector
from data.options_collector import OptionsCollector
from data.iv_recorder import IVRecorder
from signals.hub import SignalHub
from signals.formatter import UnifiedFormatter
from signals.dispatcher import dispatch
from signals.smart_filter import SmartFilter

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
        """初始化调度器，创建所有子系统实例。"""
        self.db: Database = Database(DB_PATH)
        self.registry: ContractRegistry = ContractRegistry(str(DB_PATH))
        self.futures_collector: FuturesCollector = FuturesCollector(
            self.db, self.registry
        )
        self.options_collector: OptionsCollector = OptionsCollector(self.registry)
        self.iv_recorder: IVRecorder = IVRecorder(self.db)
        self.hub: SignalHub = SignalHub(self.db)
        self.formatter: UnifiedFormatter = UnifiedFormatter()
        self._smart_filter: Optional["SmartFilter"] = None
        # ── Telegram 推送模式自动检测 ──────────────────────────
        self._enable_telegram: bool = self._check_telegram_config()
        if self._enable_telegram:
            logger.info("Telegram 推送已配置，启用 Telegram 推送模式")
        else:
            logger.info(
                "Telegram 未配置 (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 为空)，"
                "推送回退到 stdout 模式"
            )

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
        from futures.n_structure import detect_and_save

        # 1. 采集K线
        logger.info("[1/5] 采集K线数据...")
        collect_stats = self.futures_collector.collect_all()

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
                # 避免 API 过载
                if pushed_count > 1:
                    time_module.sleep(0.3)

        logger.info("期货扫描完成: %d 条推送, %d 条被过滤抑制", pushed_count, suppressed_count)
        return results

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
            from options.ratio_spread import find_all_strategies
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
                    options_data, self.registry,
                )
            except Exception as e:
                logger.warning("  ShortStrangle计算异常 %s: %s", symbol, e)
                strangle = None

            # 铁鹰式
            try:
                iron_condor = find_best_iron_condor(
                    symbol, contract, futures_price, iv_avg, dte,
                    options_data, self.registry,
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
                        "buy_strike": spread.buy_leg.strike,
                        "sell_strike": spread.sell_leg.strike,
                        "net_cost": spread.net_cost,
                        "win_rate": spread.win_rate,
                        "net_delta": spread.net_delta,
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
                        "buy_strike": spread.buy_leg.strike,
                        "sell_strike": spread.sell_leg.strike,
                        "net_cost": spread.net_cost,
                        "win_rate": spread.win_rate,
                        "net_delta": spread.net_delta,
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

        logger.info("全量扫描完成: 期货ENTRY=%d, 期权ENTRY=%d",
                     futures_entry, options_entry)

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
        choices=["futures", "options", "all", "eod"],
        default="all",
        help="运行模式: futures=期货扫描, options=期权扫描, all=全量, eod=收盘总结 (默认: all)",
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
