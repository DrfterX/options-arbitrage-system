#!/bin/bash
# ══════════════════════════════════════════════════════════════
# 期权期货系统自动扫描脚本 — 供 launchd / cron 调用
# 用法: scripts/auto_scan.sh [mode]
#   mode: all | futures | options (默认: all)
# ══════════════════════════════════════════════════════════════
set -euo pipefail

PROJECT_DIR="/Users/ayong/options_arbitrage_system"
LOG_DIR="$HOME/.hermes/logs"
MODE="${1:-all}"

mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"

TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="$LOG_DIR/scan_${MODE}_${TIMESTAMP}.log"

echo "=== [$TIMESTAMP] 开始 $MODE 扫描 ===" >> "$LOG_FILE"

# 激活虚环境并运行扫描
"$PROJECT_DIR/.venv/bin/python" -m pipeline.orchestrator --mode "$MODE" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?
echo "=== 扫描完成 (exit=$EXIT_CODE) ===" >> "$LOG_FILE"

# macOS 本地通知（无 Telegram 时的桌面提醒补充）
if [ $EXIT_CODE -eq 0 ]; then
    SIGNAL_COUNT=$(grep -c "🚨\|ENTRY\|CANDIDATE" "$LOG_FILE" 2>/dev/null || echo 0)
    osascript -e "display notification \"${MODE}扫描完成 (exit=$EXIT_CODE)\" with title \"期权期货系统\" subtitle \"$SIGNAL_COUNT 条信号\"" 2>/dev/null || true
fi

# 清理7天前的扫描日志
find "$LOG_DIR" -name "scan_*.log" -mtime +7 -delete 2>/dev/null || true

exit $EXIT_CODE
