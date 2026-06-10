#!/bin/bash
# Auto Company 期权期货系统 — 一键启动所有服务
#
set -e

PROJECT_DIR="/Users/ayong/options_arbitrage_system"
cd "$PROJECT_DIR"

echo "=== Auto Company 服务启动 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 检查 .venv
if [ ! -f ".venv/bin/python" ]; then
    echo "❌ .venv 不存在，请先运行: python3 -m venv .venv && source .venv/bin/activate && pip install -e ."
    exit 1
fi
echo "✅ .venv 就绪"

# 2. 检查数据库
if [ ! -f "trading_system.db" ]; then
    echo "❌ 数据库不存在，请先初始化: .venv/bin/python scripts/init_db.py"
    exit 1
fi
echo "✅ 数据库就绪"

# 3. 清理旧 pm2 进程
if command -v pm2 &>/dev/null; then
    pm2 delete options-trading 2>/dev/null || true
fi

# 4. 启动 Web 看板
export PATH="$HOME/.workbuddy/binaries/node/versions/22.22.2/bin:$PATH"
pm2 start web/app.py \
    --interpreter .venv/bin/python \
    --cwd "$PROJECT_DIR" \
    --name "options-trading" \
    -- 127.0.0.1 5100

sleep 2

# 5. 验证
echo ""
echo "检查看板..."
if curl -s --max-time 3 http://127.0.0.1:5100/ >/dev/null 2>&1; then
    echo "✅ Web 看板已启动: http://localhost:5100"
else
    echo "⚠️ 看板未响应，请检查 pm2 status"
    pm2 status options-trading
fi

echo ""
echo "=== 服务启动完成 ==="
echo "看板: http://localhost:5100"
echo "管理: pm2 status / pm2 logs options-trading"
echo "扫描: bash scripts/quick_scan.sh"
echo "收盘: .venv/bin/python -m pipeline.orchestrator --mode eod"