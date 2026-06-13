"""
Paper Trading 回测引擎 — N 型结构 + 15m 突破入场策略。

基于 docs/strategy/p1-b-paper-trading-spec.md（S.2.2.3）规格实现。
在历史 1d + 15m K 线数据上逐 bar 回放 N 型检测和 15m 突破入场。

用法:
    python -m futures.n_paper_backtest              # 全部7个品种
    python -m futures.n_paper_backtest --symbol RB  # 单品种
"""

import csv
import json
import logging
import math
import sqlite3
import sys
import time as time_module
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─── 常量 ──────────────────────────────────────────────────

TARGET_SYMBOLS = ["RB", "Y", "P", "EB", "L", "PG", "TA"]

SWING_WINDOW = 5           # 1d 极值检测窗口
FRESHNESS_1D_S = 30 * 86400  # N 型新鲜度 30 天
SIGNAL_EXPIRY_S = 10 * 86400  # 信号有效期 10 天

TIMEFRAME_1D = "1d"
TIMEFRAME_15M = "15m"

SECTOR_MAP: Dict[str, str] = {
    "RB": "黑色", "Y": "农产品", "P": "农产品",
    "EB": "能化", "L": "能化", "PG": "能化", "TA": "能化",
}

# 评分权重
SCORE_WEIGHTS = {
    "win_rate": 0.30,
    "profit_ratio": 0.25,
    "total_return": 0.20,
    "max_drawdown": 0.15,
    "sharpe": 0.10,
}

# 路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "trading_system.db"
OUTPUT_DIR = PROJECT_ROOT / "data" / "paper_trading"


# ═══════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════

@dataclass
class KlineBar:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass
class SwingPoint:
    timestamp: int
    price: float
    point_type: str  # PEAK | TROUGH


@dataclass
class NStr:
    """N 型结构（内存版，不写 DB）。"""
    symbol: str
    direction: str       # LONG | SHORT
    pa_time: int
    pa_price: float
    pb_time: int
    pb_price: float
    pc_time: int
    pc_price: float
    detected_ts: int     # 检测时的 1d bar 时间戳

    @property
    def b_price(self) -> float:
        return self.pb_price

    @property
    def a_price(self) -> float:
        return self.pa_price

    @property
    def c_price(self) -> float:
        return self.pc_price

    def ref_dist(self) -> float:
        return max(abs(self.pb_price - self.pa_price),
                   abs(self.pc_price - self.pb_price))

    def target_1(self) -> float:
        d = self.ref_dist()
        return self.pb_price + d if self.direction == "LONG" else self.pb_price - d

    def target_2(self) -> float:
        d = self.ref_dist()
        return self.pb_price + 2 * d if self.direction == "LONG" else self.pb_price - 2 * d

    def valid(self, close_1d: float) -> bool:
        """C 未突破 A 且最新收盘未突破 A。"""
        if self.direction == "LONG":
            return self.pc_price > self.pa_price and close_1d > self.pa_price
        return self.pc_price < self.pa_price and close_1d < self.pa_price

    def fresh(self, now: int) -> bool:
        return (now - self.pc_time) <= FRESHNESS_1D_S


@dataclass
class Trade:
    symbol: str
    direction: str
    entry_time: int
    entry_price: float
    exit_time: int
    exit_price: float
    qty: int = 1
    pnl: float = 0.0
    pnl_pct: float = 0.0
    exit_reason: str = ""
    b_price: float = 0.0
    a_price: float = 0.0
    c_price: float = 0.0
    sl_price: float = 0.0
    tp1_price: float = 0.0
    tp2_price: float = 0.0
    atr_entry: float = 0.0


@dataclass
class PerfSummary:
    symbol: str = "ALL"
    trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    total_return_pct: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_ratio: float = 0.0
    max_dd_pct: float = 0.0
    sharpe: float = 0.0
    long_trades: int = 0
    short_trades: int = 0
    long_win_rate: float = 0.0
    short_win_rate: float = 0.0
    score: float = 0.0
    score_details: Dict[str, float] = field(default_factory=dict)
    signal_count: int = 0


# ═══════════════════════════════════════════════════════════
# 极值点检测（复刻 swing_points.detect_swing_points）
# ═══════════════════════════════════════════════════════════

def _detect_swing_points(klines: List[KlineBar], wn: int = SWING_WINDOW) -> List[SwingPoint]:
    if len(klines) < wn * 2 + 1:
        return []
    pts: List[SwingPoint] = []
    n = len(klines)
    for i in range(wn, n - wn + 1):
        c = klines[i]
        lh = max(k.high for k in klines[i - wn:i])
        ll = min(k.low for k in klines[i - wn:i])
        rb = klines[i + 1:i + wn + 1]
        rh = max(k.high for k in rb)
        rl = min(k.low for k in rb)
        same_peak = False

        if c.high > lh and c.high >= rh:
            if not pts or pts[-1].point_type != "PEAK":
                pts.append(SwingPoint(c.timestamp, c.high, "PEAK"))
            elif c.high > pts[-1].price:
                pts[-1].price = c.high
                pts[-1].timestamp = c.timestamp
            same_peak = True

        if c.low < ll and c.low <= rl:
            if not pts:
                if not same_peak:
                    pts.append(SwingPoint(c.timestamp, c.low, "TROUGH"))
            elif pts[-1].point_type == "TROUGH":
                if c.low < pts[-1].price:
                    pts[-1].price = c.low
                    pts[-1].timestamp = c.timestamp
            elif not same_peak:
                pts.append(SwingPoint(c.timestamp, c.low, "TROUGH"))
    return pts


def _merge_same(pts: List[SwingPoint]) -> List[SwingPoint]:
    out: List[SwingPoint] = []
    for p in pts:
        if out and p.point_type == out[-1].point_type:
            prev = out[-1]
            if p.point_type == "TROUGH":
                if p.price < prev.price:
                    out[-1] = p
            elif p.price > prev.price:
                out[-1] = p
        else:
            out.append(p)
    return out


def _detect_n(sym: str, klines_1d: List[KlineBar], lookback: int = 40) -> Optional[NStr]:
    """在 1d K 线序列上检测最新 N 型结构。"""
    if len(klines_1d) < SWING_WINDOW * 2 + 1:
        return None
    pts = _detect_swing_points(klines_1d[-lookback:], SWING_WINDOW)
    if len(pts) < 3:
        return None
    filtered = _merge_same(pts)
    if len(filtered) < 3:
        return None

    best: Optional[Tuple[SwingPoint, SwingPoint, SwingPoint]] = None
    n = len(filtered)
    for start in range(n - 3, max(n - 5, -1), -1):
        trio = filtered[start:start + 3]
        tt = [p.point_type for p in trio]
        if not (tt[0] != tt[1] and tt[1] != tt[2]):
            continue
        pa, pb, pc = trio
        dr = "LONG" if pb.price > pa.price else "SHORT"
        if dr == "LONG" and pc.price <= pa.price:
            continue
        if dr == "SHORT" and pc.price >= pa.price:
            continue
        best = (pa, pb, pc)
        break
    if best is None:
        return None
    pa, pb, pc = best
    dr = "LONG" if pb.price > pa.price else "SHORT"
    return NStr(sym, dr, pa.timestamp, pa.price, pb.timestamp, pb.price,
                pc.timestamp, pc.price, klines_1d[-1].timestamp)


# ═══════════════════════════════════════════════════════════
# ATR
# ═══════════════════════════════════════════════════════════

def _calc_atr(bars: List[KlineBar], period: int = 14) -> float:
    if len(bars) < period + 1:
        return 0.0
    trs = []
    for i in range(1, len(bars)):
        hl = bars[i].high - bars[i].low
        hc = abs(bars[i].high - bars[i - 1].close)
        lc = abs(bars[i].low - bars[i - 1].close)
        trs.append(max(hl, hc, lc))
    if len(trs) < period:
        return sum(trs) / len(trs) if trs else 0.0
    return sum(trs[-period:]) / period


# ═══════════════════════════════════════════════════════════
# 持仓模拟
# ═══════════════════════════════════════════════════════════

class Position:
    """单笔持仓。"""

    def __init__(self, symbol: str, direction: str, entry_time: int,
                 entry_price: float, ns: NStr, atr: float, qty: int = 1):
        self.symbol = symbol
        self.direction = direction
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.qty = qty
        self.remaining = qty
        self.ns = ns
        self.atr = atr

        if direction == "LONG":
            self.sl = min(ns.c_price, entry_price - 1.5 * atr)
            self.struct_sl = ns.a_price
        else:
            self.sl = max(ns.c_price, entry_price + 1.5 * atr)
            self.struct_sl = ns.a_price

        self.tp1 = ns.target_1()
        self.tp2 = ns.target_2()

        self.trail_active = False
        self.trail_hi = entry_price
        self.trail_lo = entry_price
        self.trail_dist = 1.0 * atr

        self.closed = False
        self.exit_ts: Optional[int] = None
        self.exit_price: Optional[float] = None
        self.exit_reason = ""
        self.total_pnl = 0.0

    def step(self, bar: KlineBar, close_1d: float) -> Optional[Trade]:
        """更新持仓。返回 None 表示继续持有，返回 Trade 表示已平仓。"""
        if self.closed:
            return None

        self.trail_hi = max(self.trail_hi, bar.high)
        self.trail_lo = min(self.trail_lo, bar.low)

        # 结构止损
        if self.direction == "LONG" and close_1d <= self.struct_sl:
            return self._close(bar.close, "STRUCTURE_STOP", bar.timestamp)
        if self.direction == "SHORT" and close_1d >= self.struct_sl:
            return self._close(bar.close, "STRUCTURE_STOP", bar.timestamp)

        # 硬止损
        if self.direction == "LONG" and bar.low <= self.sl:
            return self._close(self.sl, "HARD_STOP", bar.timestamp)
        if self.direction == "SHORT" and bar.high >= self.sl:
            return self._close(self.sl, "HARD_STOP", bar.timestamp)

        # 1:1 部分止盈（触发后激活跟踪）
        if not self.trail_active:  # 未激活 = 还没到 1:1
            if self.direction == "LONG" and bar.high >= self.tp1:
                self.trail_active = True
                half = self.qty // 2
                if half >= 1:
                    self.remaining = self.qty - half
                    pnl = half * (self.tp1 - self.entry_price)
                    t = Trade(self.symbol, self.direction, self.entry_time,
                              self.entry_price, bar.timestamp, self.tp1, half,
                              pnl, pnl / (self.entry_price * half) * 100,
                              "TAKE_PROFIT_1",
                              self.ns.b_price, self.ns.a_price, self.ns.c_price,
                              self.sl, self.tp1, self.tp2, self.atr)
                    self.total_pnl += pnl
                    return t
            elif self.direction == "SHORT" and bar.low <= self.tp1:
                self.trail_active = True
                half = self.qty // 2
                if half >= 1:
                    self.remaining = self.qty - half
                    pnl = half * (self.entry_price - self.tp1)
                    t = Trade(self.symbol, self.direction, self.entry_time,
                              self.entry_price, bar.timestamp, self.tp1, half,
                              pnl, pnl / (self.entry_price * half) * 100,
                              "TAKE_PROFIT_1",
                              self.ns.b_price, self.ns.a_price, self.ns.c_price,
                              self.sl, self.tp1, self.tp2, self.atr)
                    self.total_pnl += pnl
                    return t

        # 跟踪止损
        if self.trail_active and self.remaining > 0:
            if self.direction == "LONG":
                ts = self.trail_hi - self.trail_dist
                if bar.low <= ts:
                    return self._close(ts, "TRAILING_STOP", bar.timestamp)
            else:
                ts = self.trail_lo + self.trail_dist
                if bar.high >= ts:
                    return self._close(ts, "TRAILING_STOP", bar.timestamp)

        # 1:2 目标（剩余仓位）
        if self.remaining > 0:
            if self.direction == "LONG" and bar.high >= self.tp2:
                return self._close(self.tp2, "TAKE_PROFIT_2", bar.timestamp)
            if self.direction == "SHORT" and bar.low <= self.tp2:
                return self._close(self.tp2, "TAKE_PROFIT_2", bar.timestamp)

        return None

    def _close(self, price: float, reason: str, ts: int) -> Trade:
        self.closed = True
        self.exit_ts = ts
        self.exit_price = price
        self.exit_reason = reason
        if self.direction == "LONG":
            pnl = self.remaining * (price - self.entry_price)
            pct = (price / self.entry_price - 1) * 100
        else:
            pnl = self.remaining * (self.entry_price - price)
            pct = (1 - price / self.entry_price) * 100
        self.total_pnl += pnl
        return Trade(self.symbol, self.direction, self.entry_time,
                     self.entry_price, ts, price, self.remaining,
                     pnl, pct, reason,
                     self.ns.b_price, self.ns.a_price, self.ns.c_price,
                     self.sl, self.tp1, self.tp2, self.atr)

    def force_close(self, price: float, ts: int) -> Trade:
        if self.closed:
            t = Trade(self.symbol, self.direction, self.entry_time,
                      self.entry_price, ts, price, 0, 0, 0, "EXPIRED",
                      self.ns.b_price, self.ns.a_price, self.ns.c_price,
                      self.sl, self.tp1, self.tp2, self.atr)
            t.pnl = self.total_pnl
            return t
        return self._close(price, "EXPIRED", ts)


# ═══════════════════════════════════════════════════════════
# 数据加载
# ═══════════════════════════════════════════════════════════

def _load_klines(db_path: str, symbol: str, tf: str) -> List[KlineBar]:
    bars: List[KlineBar] = []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT timestamp, open, high, low, close, volume
               FROM futures_klines
               WHERE symbol=? AND timeframe=?
               ORDER BY timestamp ASC""",
            (symbol, tf),
        ).fetchall()
    for r in rows:
        bars.append(KlineBar(r["timestamp"], r["open"], r["high"],
                             r["low"], r["close"], r["volume"] or 0))
    return bars


def _get_contract(db_path: str, symbol: str) -> str:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT contract FROM futures_klines WHERE symbol=? AND timeframe='1d' ORDER BY timestamp DESC LIMIT 1",
            (symbol,),
        ).fetchone()
    return row[0] if row else symbol


def load_one(db_path: str, symbol: str) -> Dict[str, Any]:
    """加载单品种的 1d + 15m 数据。"""
    ctr = _get_contract(db_path, symbol)
    k1d = _load_klines(db_path, symbol, "1d")
    k15 = _load_klines(db_path, symbol, "15m")
    logger.info("加载 %s (%s): 1d=%d, 15m=%d", symbol, ctr, len(k1d), len(k15))
    return dict(symbol=symbol, contract=ctr, k1d=k1d, k15=k15)


def load_all(db_path: str) -> Dict[str, Dict[str, Any]]:
    """加载全部 7 个品种数据（为 run_all 预加载）。"""
    data: Dict[str, Dict[str, Any]] = {}
    for sym in TARGET_SYMBOLS:
        data[sym] = load_one(db_path, sym)
    return data


# ═══════════════════════════════════════════════════════════
# 评分
# ═══════════════════════════════════════════════════════════

def _score_5d(perf: PerfSummary) -> float:
    """5 维评分，返回总分 (0-100)。"""
    def _lin(v, x0, y0, x1, y1):
        if x1 == x0:
            return 100.0 if v >= x0 else 0.0
        s = y0 + (v - x0) * (y1 - y0) / (x1 - x0)
        return max(0.0, min(100.0, s))

    wr = _lin(perf.win_rate * 100, 0, 0, 60, 100)     # 胜率 0%→0, 60%→100
    pr = _lin(perf.profit_ratio, 0, 0, 2.0, 100)       # 盈亏比 0→0, 2.0→100
    tr = _lin(perf.total_return_pct, 0, 0, 20, 100)    # 收益率 0%→0, 20%→100
    dd = _lin(perf.max_dd_pct * 100, 20, 0, 5, 100)    # 回撤 20%→0, 5%→100
    sr = _lin(perf.sharpe, 0, 0, 1.5, 100)             # Sharpe 0→0, 1.5→100

    perf.score_details = {
        "wr_score": round(wr, 1),
        "pr_score": round(pr, 1),
        "tr_score": round(tr, 1),
        "dd_score": round(dd, 1),
        "sr_score": round(sr, 1),
    }

    total = (wr * 0.30 + pr * 0.25 + tr * 0.20 + dd * 0.15 + sr * 0.10)
    perf.score = round(total, 1)
    return perf.score


# ═══════════════════════════════════════════════════════════
# 绩效计算
# ═══════════════════════════════════════════════════════════

def _calc_perf(symbol: str, trades: List[Trade], capital: float) -> PerfSummary:
    s = PerfSummary(symbol=symbol)
    s.trades = len(trades)
    if not trades:
        return s

    s.wins = sum(1 for t in trades if t.pnl > 0)
    s.losses = s.trades - s.wins
    s.win_rate = s.wins / s.trades if s.trades > 0 else 0

    wins = [t.pnl for t in trades if t.pnl > 0]
    losses = [t.pnl for t in trades if t.pnl <= 0]
    s.total_pnl = sum(t.pnl for t in trades)
    s.avg_win = sum(wins) / len(wins) if wins else 0
    avg_l = abs(sum(losses) / len(losses)) if losses else 1
    s.avg_loss = avg_l
    s.profit_ratio = s.avg_win / avg_l if avg_l > 0 else 0

    s.total_return_pct = s.total_pnl / capital * 100

    eq = capital
    peak = eq
    max_dd = 0.0
    rets = []
    for t in trades:
        eq += t.pnl
        rets.append(t.pnl / capital)
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak
        max_dd = max(max_dd, dd)
    s.max_dd_pct = max_dd

    if len(rets) > 1:
        avg_r = sum(rets) / len(rets)
        std_r = math.sqrt(sum((r - avg_r)**2 for r in rets) / (len(rets) - 1)) if len(rets) > 1 else 0.001
        s.sharpe = (avg_r / std_r) * math.sqrt(252) if std_r > 0 else 0

    s.long_trades = sum(1 for t in trades if t.direction == "LONG")
    s.short_trades = sum(1 for t in trades if t.direction == "SHORT")
    lw = sum(1 for t in trades if t.direction == "LONG" and t.pnl > 0)
    sw = sum(1 for t in trades if t.direction == "SHORT" and t.pnl > 0)
    s.long_win_rate = lw / s.long_trades if s.long_trades > 0 else 0
    s.short_win_rate = sw / s.short_trades if s.short_trades > 0 else 0

    _score_5d(s)
    return s


def _aggregate(trades: List[Trade], summaries: List[PerfSummary], capital: float) -> PerfSummary:
    agg = _calc_perf("ALL", trades, capital)
    agg.signal_count = sum(s.signal_count for s in summaries)
    return agg


# ═══════════════════════════════════════════════════════════
# 核心回测逻辑
# ═══════════════════════════════════════════════════════════

def run_symbol(
    sym_data: Dict[str, Any], capital: float = 100000.0
) -> Tuple[PerfSummary, List[Trade]]:
    """单个品种 Paper Trading 回测。

    Args:
        sym_data: load_one() 返回的品种数据。

    Returns:
        (PerfSummary, 交易记录列表)
    """
    symbol = sym_data["symbol"]
    k1d = sym_data["k1d"]
    k15 = sym_data["k15"]

    if len(k1d) < 20 or len(k15) < 20:
        logger.warning("数据不足: %s (1d=%d, 15m=%d)", symbol, len(k1d), len(k15))
        return PerfSummary(symbol=symbol), []

    k15_start = k15[0].timestamp
    k15_end = k15[-1].timestamp
    logger.info("回测 %s (%s): 1d=%d, 15m=%d [%s ~ %s]",
                symbol, sym_data.get("contract", ""), len(k1d), len(k15),
                datetime.fromtimestamp(k15_start, tz=timezone.utc).strftime("%m-%d"),
                datetime.fromtimestamp(k15_end, tz=timezone.utc).strftime("%m-%d"))

    # ── 单遍 Bar-by-Bar 回放 ──
    # 沿 15m 时间轴逐 bar 推进，按交易日更新 1d N 型检测
    # 每根 15m bar 只与当前活跃 N 型配对
    all_trades: List[Trade] = []
    signal_count = 0
    n_count = 0

    active_ns: Optional[NStr] = None      # 当前活跃 N 型
    ns_signal_expiry: int = 0             # 当前信号过期时间
    position: Optional[Position] = None   # 当前持仓
    last_trading_day = 0                  # 上一个交易日标识
    k1d_idx = max(0, next(
        (ki for ki, b in enumerate(k1d) if b.timestamp >= k15_start - 60 * 86400),
        len(k1d) - 1) - 2)

    # 缓存的 N 型去重
    processed_ns: set = set()

    # Pullback 入场状态机
    pb_phase: Optional[str] = None        # None / "BREAKOUT" / "PULLBACK"
    pb_b_price: float = 0.0              # 被突破的 B 点价格
    pb_atr: float = 0.0                  # 突破时刻的 ATR
    pb_ns_ts: int = 0                    # 关联 N 型的 pc_time（用于身份校验）

    def _get_1d_close(ts: int) -> float:
        nonlocal k1d_idx
        while k1d_idx < len(k1d) - 1 and k1d[k1d_idx + 1].timestamp <= ts:
            k1d_idx += 1
        return k1d[k1d_idx].close

    for bi, bar in enumerate(k15):
        ts = bar.timestamp
        trading_day = ts // 86400

        # ── 新交易日 → 更新 N 型检测 ──
        if trading_day != last_trading_day:
            last_trading_day = trading_day
            close_1d = _get_1d_close(ts)
            # 只有没有活跃结构时才检测新的
            if active_ns is None:
                ns = _detect_n(symbol, k1d[:k1d_idx + 1], lookback=40)
                if ns and ns.fresh(ts) and ns.valid(close_1d):
                    key = (ns.direction, ns.pa_time, ns.pb_time)
                    if key not in processed_ns:
                        processed_ns.add(key)
                        active_ns = ns
                        ns_signal_expiry = ns.pc_time + SIGNAL_EXPIRY_S
                        n_count += 1
                        logger.debug("  [%s] N型 #%d %s: A=%.0f B=%.0f C=%.0f",
                                     symbol, n_count, ns.direction,
                                     ns.a_price, ns.b_price, ns.c_price)
            else:
                # 检查已有结构是否仍有效
                if not active_ns.valid(close_1d) or not active_ns.fresh(ts):
                    logger.debug("  [%s] N型过期/失效", symbol)
                    active_ns = None

        # ── 跳过预热 ──
        if bi < 5 and active_ns is None:
            continue

        close_1d = _get_1d_close(ts)

        # ── 管理持仓 ──
        if position is not None and not position.closed:
            tr = position.step(bar, close_1d)
            if tr is not None:
                all_trades.append(tr)
                if position.closed:
                    position = None
        elif position is not None and position.closed:
            position = None

        # ── 入场检测（无持仓且活跃 N 型且信号未过期） ──
        if position is None and active_ns is not None and ts <= ns_signal_expiry:
            if not active_ns.valid(close_1d) or not active_ns.fresh(ts):
                active_ns = None
                pb_phase = None
                continue

            if bi > 0:
                prev = k15[bi - 1]
                if active_ns.direction == "LONG":
                    this_brk = bar.close >= active_ns.b_price
                    prev_brk = prev.close >= active_ns.b_price
                else:
                    this_brk = bar.close <= active_ns.b_price
                    prev_brk = prev.close <= active_ns.b_price

                is_fresh = this_brk and not prev_brk
            else:
                is_fresh = False

            # ── Pullback 入场状态机 ──
            # IDLE → BREAKOUT (B 突破) → PULLBACK (回撤到 B±0.3×ATR) → re-break 入场
            # N 型变更时重置
            if pb_phase is not None and active_ns.pc_time != pb_ns_ts:
                pb_phase = None

            if pb_phase is None:
                # IDLE: 等待首次 B 点突破
                if is_fresh:
                    pb_phase = "BREAKOUT"
                    pb_b_price = active_ns.b_price
                    pb_ns_ts = active_ns.pc_time
                    pb_atr = _calc_atr(k15[max(0, bi - 20):bi + 1], 14)
                    if pb_atr <= 0:
                        pb_atr = abs(active_ns.b_price - active_ns.a_price) * 0.02
                    logger.debug("  [%s] Pullback: BREAKOUT @ B=%.0f ATR=%.1f",
                                 symbol, pb_b_price, pb_atr)

            elif pb_phase == "BREAKOUT":
                # BREAKOUT: 已突破 B，等待价格回撤到 B ± 0.3×ATR 范围
                pb_low = pb_b_price - 0.3 * pb_atr
                pb_high = pb_b_price + 0.3 * pb_atr
                if bar.low <= pb_high and bar.high >= pb_low:
                    pb_phase = "PULLBACK"
                    logger.debug("  [%s] Pullback: PULLBACK (touched %.0f~%.0f zone) @ %.0f",
                                 symbol, pb_low, pb_high, bar.close)

            elif pb_phase == "PULLBACK":
                # PULLBACK: 回撤完成，等待 B 点二次突破（同方向）→ 入场
                if is_fresh:
                    atr = pb_atr
                    position = Position(symbol, active_ns.direction, ts,
                                        bar.close, active_ns, atr, qty=1)
                    signal_count += 1
                    logger.debug("  [%s] 入场 %s @ %.0f (Pullback entry)",
                                 symbol, active_ns.direction, bar.close)
                    # 入场后释放 N 型 + 重置 pullback 状态
                    active_ns = None
                    pb_phase = None

        else:
            # 不在入场窗口或有持仓 → 重置 pullback 状态
            pb_phase = None

    # 过期平仓
    if position is not None and not position.closed:
        tr = position.force_close(k15[-1].close, k15[-1].timestamp)
        all_trades.append(tr)

    perf = _calc_perf(symbol, all_trades, capital)
    perf.signal_count = signal_count
    logger.info("  N型=%d 信号=%d 交易=%d 胜率=%.1f%% PnL=%.0f",
                n_count, signal_count, perf.trades,
                perf.win_rate * 100, perf.total_pnl)
    return perf, all_trades


# ═══════════════════════════════════════════════════════════
# 多品种 / 全量回测
# ═══════════════════════════════════════════════════════════

def run_all(db_path: str, capital: float = 100000.0) -> Tuple[PerfSummary, List[PerfSummary], List[Trade]]:
    summaries: List[PerfSummary] = []
    all_trades: List[Trade] = []

    data = load_all(db_path)

    for sym in TARGET_SYMBOLS:
        logger.info("===== %s =====", sym)
        sym_data = data.get(sym)
        if not sym_data:
            summaries.append(PerfSummary(symbol=sym))
            continue
        perf, trades = run_symbol(sym_data, capital)
        summaries.append(perf)
        all_trades.extend(trades)

    agg = _aggregate(all_trades, summaries, capital)
    return agg, summaries, all_trades


def save_results(trades: List[Trade], agg: PerfSummary, summaries: List[PerfSummary],
                 db_path: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / "n_paper_trades.csv"
    json_path = OUTPUT_DIR / "n_paper_summary.json"

    # CSV
    if trades:
        fields = ["symbol", "direction", "entry_time", "entry_price",
                  "exit_time", "exit_price", "qty", "pnl", "pnl_pct",
                  "exit_reason", "b_price", "a_price", "c_price",
                  "sl_price", "tp1_price", "tp2_price", "atr_entry"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for t in trades:
                row = {k: getattr(t, k, "") for k in fields}
                row["entry_time"] = datetime.fromtimestamp(t.entry_time, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                row["exit_time"] = datetime.fromtimestamp(t.exit_time, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                w.writerow(row)
        logger.info("CSV: %s (%d 笔)", csv_path, len(trades))

    # JSON
    jdata: Dict[str, Any] = {
        "aggregate": {
            "trades": agg.trades, "wins": agg.wins, "losses": agg.losses,
            "win_rate_pct": round(agg.win_rate * 100, 1),
            "total_pnl": round(agg.total_pnl, 2),
            "total_return_pct": round(agg.total_return_pct, 2),
            "profit_ratio": round(agg.profit_ratio, 2),
            "max_dd_pct": round(agg.max_dd_pct * 100, 2),
            "sharpe": round(agg.sharpe, 2),
            "signal_count": agg.signal_count,
            "score": agg.score,
            "score_details": agg.score_details,
            "grade": "PASS" if agg.score >= 75 else ("WATCH" if agg.score >= 50 else "FAIL"),
        },
        "per_symbol": {},
    }
    for s in summaries:
        jdata["per_symbol"][s.symbol] = {
            "trades": s.trades, "win_rate_pct": round(s.win_rate * 100, 1),
            "total_pnl": round(s.total_pnl, 2),
            "total_return_pct": round(s.total_return_pct, 2),
            "profit_ratio": round(s.profit_ratio, 2),
            "max_dd_pct": round(s.max_dd_pct * 100, 2),
            "sharpe": round(s.sharpe, 2),
            "signal_count": s.signal_count,
            "score": s.score,
        }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(jdata, f, ensure_ascii=False, indent=2)
    logger.info("JSON: %s", json_path)


def print_report(agg: PerfSummary, summaries: List[PerfSummary]) -> None:
    print("\n" + "=" * 60)
    print("  P1-B Paper Trading 回测报告")
    print("=" * 60)

    print(f"\nN型/信号总数:   {agg.signal_count}")
    print(f"交易次数:        {agg.trades}")
    print(f"胜率:            {agg.win_rate * 100:.1f}%")
    print(f"  多头:          {agg.long_trades}次 ({agg.long_win_rate * 100:.0f}%)")
    print(f"  空头:          {agg.short_trades}次 ({agg.short_win_rate * 100:.0f}%)")
    print(f"总 PnL:          {agg.total_pnl:+.2f}")
    print(f"总收益率:        {agg.total_return_pct:+.2f}%")
    print(f"盈亏比:          {agg.profit_ratio:.2f}")
    print(f"最大回撤:        {agg.max_dd_pct * 100:.2f}%")
    print(f"Sharpe:          {agg.sharpe:.2f}")
    print(f"评分:            {agg.score}/100")
    for k, v in agg.score_details.items():
        print(f"  {k}: {v}")
    grade = "PASS ✅" if agg.score >= 75 else "WATCH ⏳" if agg.score >= 50 else "FAIL ❌"
    print(f"等级:            {grade}")

    print(f"\n{'Sym':>4} {'Trades':>7} {'Win%':>7} {'PnL':>10} {'Ret%':>8} {'DD%':>7} {'Sharpe':>7}")
    for s in summaries:
        if s.trades > 0:
            print(f"{s.symbol:>4} {s.trades:>7} {s.win_rate*100:>6.1f}% "
                  f"{s.total_pnl:>+9.0f} {s.total_return_pct:>+7.2f}% "
                  f"{s.max_dd_pct*100:>6.2f}% {s.sharpe:>7.2f}")
        else:
            print(f"{s.symbol:>4} {'无交易':>7}")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                        datefmt="%H:%M:%S")

    import argparse
    parser = argparse.ArgumentParser(description="P1-B Paper Trading 回测引擎")
    parser.add_argument("--symbol", "-s", default="", help="单品种")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="数据库路径")
    parser.add_argument("--capital", "-c", type=float, default=100000.0, help="初始资金")
    args = parser.parse_args()

    db_path = args.db

    if args.symbol:
        if args.symbol not in TARGET_SYMBOLS:
            print(f"不支持 {args.symbol}，可选: {', '.join(TARGET_SYMBOLS)}")
            sys.exit(1)
        sym_data = load_one(db_path, args.symbol)
        perf, trades = run_symbol(sym_data, args.capital)
        print_report(perf, [perf])
        save_results(trades, perf, [perf], db_path)
    else:
        start = time_module.time()
        agg, summaries, trades = run_all(db_path, args.capital)
        print_report(agg, summaries)
        save_results(trades, agg, summaries, db_path)
        elapsed = time_module.time() - start
        print(f"耗时: {elapsed:.1f}s")


if __name__ == "__main__":
    main()