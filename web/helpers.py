"""Web 辅助函数 — 从 app.py 提取的公共工具函数。"""

import os
import re
import secrets
from config.symbol_data import SYMBOL_NAMES, STRATEGY_NAMES
from scripts.core.greeks_cash import (
    delta_cash as _delta_cash,
    theta_cash as _theta_cash,
    vega_cash as _vega_cash,
    get_multiplier as _get_multiplier,
)

# ─── 管理员密码 ───────────────────────────────────────────────────
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


def _admin_pw_ok(candidate: str) -> bool:
    """时序安全地校验管理员密码。"""
    if not ADMIN_PASSWORD:
        return False
    return secrets.compare_digest(str(candidate or ""), ADMIN_PASSWORD)


# ─── N 型结构时间戳归一化 ──────────────────────────────────────────
_BJ_OFFSET = 8 * 3600
_TARGET_HOUR_SEC = 20700  # 05:45 UTC = 13:45 BJT


def _normalize_n_ts(d: dict) -> None:
    """原地归一化 N 型结构字典的 1d/1w 时间戳。"""
    if d.get("timeframe") not in ("1d", "1w"):
        return
    for key in ("point_a_time", "point_b_time", "point_c_time"):
        ts = d.get(key)
        if ts is None:
            continue
        bj_midnight_utc = ((ts + _BJ_OFFSET) // 86400) * 86400 - _BJ_OFFSET
        d[key] = bj_midnight_utc + _TARGET_HOUR_SEC


# ─── 合约名清洗 ───────────────────────────────────────────────────
def _clean_contract_n_prefix(contract: str) -> str:
    """清洗合约前缀: ag/nag2607 → ag2607, nag2607 → ag2607。"""
    c = contract or ""
    c = re.sub(r"^[A-Za-z0-9]+/", "", c)
    c = re.sub(r"^[nN]", "", c)
    return c


# ─── 数据清洗 ─────────────────────────────────────────────────────
def _enrich_iv_status(status_list):
    """为 IV 状态列表添加中文名 + 清洗合约前缀。"""
    for item in status_list:
        sym = (item.get("symbol") or "").upper()
        item["name"] = SYMBOL_NAMES.get(sym, item.get("symbol", ""))
        item["contract"] = _clean_contract_n_prefix(item.get("contract", ""))
    return status_list


def _enrich_options_signals(options_list):
    """清洗期权信号 + 添加中文名/策略中文名/主连标记 + Greeks 现金化。"""
    for item in options_list:
        item["contract"] = _clean_contract_n_prefix(item.get("contract", ""))
        sym = (item.get("symbol") or "").upper()
        item["name"] = SYMBOL_NAMES.get(sym, item.get("symbol", ""))

        strat = (item.get("strategy") or "").strip()
        item["strategy_cn"] = STRATEGY_NAMES.get(strat, strat.replace("_", " "))

        cont = item.get("contract", "")
        if cont and not any(ch.isdigit() for ch in cont):
            item["contract"] = cont + " cont"
        else:
            item["contract"] = " ".join(cont.split())

        # Greeks 现金化
        delta_raw = item.get("net_delta", 0) or 0
        theta_raw = item.get("net_theta", 0) or 0
        vega_raw = item.get("net_vega", 0) or 0
        price = item.get("futures_price", 0) or 0
        multiplier = _get_multiplier(sym)
        if price > 0 and multiplier > 0:
            item["delta_cash"] = round(_delta_cash(delta_raw, price, multiplier), 2)
            item["theta_cash"] = round(_theta_cash(theta_raw, multiplier), 2)
            item["vega_cash"] = round(_vega_cash(vega_raw, multiplier), 2)
        else:
            item["delta_cash"] = 0.0
            item["theta_cash"] = 0.0
            item["vega_cash"] = 0.0

    return options_list


# ─── 合约解析辅助 ─────────────────────────────────────────────────
def _get_futures_contract(conn, symbol: str) -> str:
    """获取品种的合约代码。"""
    row = conn.execute(
        "SELECT contract FROM futures_signals WHERE symbol=? AND contract!='' ORDER BY created_at DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    if row and row["contract"]:
        return _clean_contract_n_prefix(row["contract"]).upper()
    row = conn.execute(
        "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    if row and row["contract"]:
        return _clean_contract_n_prefix(row["contract"]).upper()
    row = conn.execute(
        "SELECT contract FROM futures_klines WHERE symbol=? AND timeframe='1d' ORDER BY timestamp DESC LIMIT 1",
        (symbol,),
    ).fetchone()
    return row["contract"] if row else ""


# ─── 延迟用户过滤 ─────────────────────────────────────────────────
def _is_delayed_user() -> bool:
    return False  # placeholder for future paywall logic


def _delay_filter(field: str, field_type: str = "text", minutes: int = 15) -> str:
    return ""  # placeholder


def _render_delayed_warning() -> str:
    return ""
