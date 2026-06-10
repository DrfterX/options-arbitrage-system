#!/bin/bash
# Auto Company 期权期货系统 — 一键快速扫描 + 推送
# 用法: bash scripts/quick_scan.sh [mode]
#   mode=futures: 仅期货  mode=options: 仅期权  mode=all: 全量 (默认)
#
set -e

PROJECT_DIR="/Users/ayong/options_arbitrage_system"
MODE="${1:-all}"
LOG_FILE="$PROJECT_DIR/scan_$(date +%Y%m%d_%H%M).log"

cd "$PROJECT_DIR"
source .venv/bin/activate

echo "=== Auto Company 快速扫描 ===" | tee -a "$LOG_FILE"
echo "模式: $MODE  时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 执行扫描
python -m pipeline.orchestrator --mode "$MODE" 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "扫描完成。日志: $LOG_FILE" | tee -a "$LOG_FILE"