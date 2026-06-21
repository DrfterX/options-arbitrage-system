#!/usr/bin/env python3
"""
真实合约解析对齐验证 — 使用生产代码的 _get_futures_contract() 直接对比 Matrix 路径。

验证 Matrix SSR（/api/matrix）和 Klines API（/api/klines）的实际合约解析结果是否一致。
"""
import os, sys, json
from datetime import datetime, timezone, timedelta

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', 'projects', 'options_arbitrage_system')
sys.path.insert(0, PROJECT_ROOT)

from futures.shared import _get_active_n_structure
from core.db import Database

DB_PATH = os.path.join(PROJECT_ROOT, "trading_system.db")
db = Database(DB_PATH)
conn = db.get_conn()

SYMBOL_NAMES = {
    "CU":"沪铜","AL":"沪铝","ZN":"沪锌","PB":"沪铅","NI":"沪镍","SN":"沪锡",
    "AU":"黄金","AG":"白银","RB":"螺纹钢","HC":"热卷","I":"铁矿","J":"焦炭","JM":"焦煤",
    "BU":"沥青","FU":"燃油","LU":"低硫燃油","SC":"原油","RU":"橡胶","NR":"20号胶",
    "BR":"丁二烯","SP":"纸浆","SS":"不锈钢","M":"豆粕","Y":"豆油","A":"豆一","B":"豆二",
    "P":"棕榈油","C":"玉米","CS":"玉米淀粉","JD":"鸡蛋","LH":"生猪","CF":"棉花",
    "SR":"白糖","TA":"PTA","MA":"甲醇","FG":"玻璃","SA":"纯碱","UR":"尿素",
    "PX":"对二甲苯","SM":"硅锰","SF":"硅铁","AP":"苹果","CJ":"红枣","RM":"菜粕",
    "OI":"菜油","EB":"苯乙烯","EG":"乙二醇","PG":"LPG","PP":"聚丙烯","V":"PVC",
    "L":"塑料","SH":"烧碱","SI":"工业硅","LC":"碳酸锂","AO":"氧化铝",
    "PF":"花生仁","PK":"花生","PR":"聚丙烯",
}

SECTORS = {
    "有色金属":{"CU","AL","ZN","PB","NI","SN","AO"},
    "贵金属":{"AU","AG"},
    "黑色系":{"RB","HC","I","J","JM","SS","SM","SF"},
    "能源":{"BU","FU","LU","SC"},
    "化工":{"TA","MA","SA","UR","PX","EB","EG","PG","PP","V","L","SH","BR"},
    "农产品":{"M","Y","A","B","P","C","CS","JD","LH","RM","OI","CF","SR","AP","CJ"},
    "橡胶":{"RU","NR"},
    "玻璃建材":{"FG"},
    "新能源":{"SI","LC"},
}

TIMEFRAMES = ["15m", "1h", "1d", "1w"]

def _clean_contract_n_prefix(contract):
    import re
    c = contract or ""
    c = re.sub(r'^[A-Za-z0-9]+/', '', c)
    c = re.sub(r'^[nN]', '', c)
    return c

# ── 直接从 app.py 复制的 _get_futures_contract ──
def _get_futures_contract(conn, symbol):
    """与 app.py 完全一致的合约解析逻辑。"""
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

# ── Matrix 路径合约解析（与 /api/matrix 一致）──
def get_matrix_contracts(conn):
    """模拟 Matrix 的 signal_contracts 构建逻辑。"""
    rows = conn.execute('''
        SELECT s.symbol, s.contract
        FROM futures_signals s
        INNER JOIN (SELECT symbol, MAX(created_at) mt FROM futures_signals GROUP BY symbol) l
            ON s.symbol=l.symbol AND s.created_at=l.mt
        WHERE s.contract!=''
    ''').fetchall()

    contracts = {}
    for r in rows:
        contracts[r["symbol"]] = _clean_contract_n_prefix(r["contract"]).upper()

    # 补充缺合约品种
    for sym in list(contracts.keys()):
        if not contracts.get(sym):
            row = conn.execute(
                "SELECT contract FROM futures_n_structures WHERE symbol=? AND contract!='' ORDER BY updated_at DESC LIMIT 1",
                (sym,),
            ).fetchone()
            if row and row["contract"]:
                contracts[sym] = _clean_contract_n_prefix(row["contract"]).upper()

    return contracts

print("=" * 80)
print("真实合约解析对齐验证 — _get_futures_contract() vs Matrix")
print("=" * 80)
print(f"时间: {datetime.now(tz=timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M CST')}")
print()

# 获取所有有 N 结构的品种
all_syms = set()
for sector_symbols in SECTORS.values():
    all_syms.update(sector_symbols)

matrix_contracts = get_matrix_contracts(conn)

mismatches = []
missing_klines = []
missing_matrix = []

for sym in sorted(all_syms):
    klines_contract = _get_futures_contract(conn, sym)
    matrix_contract = matrix_contracts.get(sym, "")

    if klines_contract != matrix_contract:
        mismatches.append((sym, matrix_contract, klines_contract))

    # 检查 N 结构可访问性
    klines_has_structure = False
    matrix_has_structure = False

    for tf in TIMEFRAMES:
        if klines_contract:
            ns = _get_active_n_structure(db, sym, klines_contract, tf)
            if ns:
                klines_has_structure = True

        if matrix_contract:
            ns = _get_active_n_structure(db, sym, matrix_contract, tf)
            if ns:
                matrix_has_structure = True

    if not klines_contract and matrix_has_structure:
        missing_klines.append((sym, matrix_contract, "无合约"))
    elif klines_contract and not matrix_contract and klines_has_structure:
        missing_matrix.append((sym, klines_contract, "无合约"))

print(f"\n总品种数: {len(all_syms)}")
print(f"有 Matrix 合约的品种: {len(matrix_contracts)}")
print()

if not mismatches:
    print("✅ _get_futures_contract() 与 Matrix 合约完全一致 — 0 个不匹配")
else:
    print(f"❌ 合约不匹配: {len(mismatches)} 个")
    print(f"{'品种':<6} {'Matrix合约':<15} {'Klines合约':<15}")
    print("-" * 40)
    for sym, mc, kc in mismatches:
        print(f"{sym:<6} {mc:<15} {kc:<15}")

print()

if not missing_klines:
    print("✅ Matrix 有结构但 Klines 查不到的品种: 0")
else:
    print(f"⚠️ Matrix 有 N 结构但 Klines 路径查不到: {len(missing_klines)}")
    for sym, mc, _ in missing_klines:
        print(f"  {sym}: Matrix 合约={mc}")

if not missing_matrix:
    print("✅ Klines 有结构但 Matrix 查不到的品种: 0")
else:
    print(f"⚠️ Klines 有 N 结构但 Matrix 路径查不到: {len(missing_matrix)}")

print()
print("--- 个别品种合约对比 ---")
check_symbols = ['PF', 'PK', 'PR', 'SP', 'SC', 'I', 'NI', 'NR', 'M', 'AG', 'J']
for sym in check_symbols:
    kc = _get_futures_contract(conn, sym)
    mc = matrix_contracts.get(sym, "(无)")

    found_tfs = []
    for tf in TIMEFRAMES:
        ns = _get_active_n_structure(db, sym, kc or "NONE", tf)
        if ns:
            found_tfs.append(tf)

    found_tfs_m = []
    for tf in TIMEFRAMES:
        ns = _get_active_n_structure(db, sym, mc, tf)
        if ns:
            found_tfs_m.append(tf)

    match = "✅" if kc == mc else "⚠️"
    print(f"  {sym}: klines_contract={kc or '(空)'} matrix_contract={mc or '(空)'} {match}")
    if kc:
        print(f"    Klines路径 N结构: {found_tfs or '(无)'}")
    if mc:
        print(f"    Matrix路径 N结构: {found_tfs_m or '(无)'}")

print(f"\n{'=' * 80}")
print("验证完成")
