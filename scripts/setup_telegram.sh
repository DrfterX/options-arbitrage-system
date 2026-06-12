#!/bin/bash
# ══════════════════════════════════════════════════════════════
# Telegram 推送配置助手
#
# 用法: bash scripts/setup_telegram.sh
#
# 该脚本引导你完成 Telegram Bot 创建，并将配置写入 .env。
# 完成后自动发送测试消息验证连通性。
# ══════════════════════════════════════════════════════════════

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       🤖 Telegram 推送配置助手                          ║"
echo "║       期权期货交易系统 — 信号推送到手机                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── 步骤 1：创建 Bot ──────────────────────────────────────────
echo -e "${BOLD}步骤 1 — 创建 Telegram Bot${NC}"
echo ""
echo "请在手机上打开 Telegram，按以下步骤操作："
echo ""
echo -e "  ${CYAN}1.${NC} 搜索 ${BOLD}@BotFather${NC}（官方机器人）"
echo -e "  ${CYAN}2.${NC} 发送 ${BOLD}/newbot${NC}"
echo -e "  ${CYAN}3.${NC} 按提示设置 Bot 名称（如 "期权交易信号"）"
echo -e "  ${CYAN}4.${NC} 设置用户名（如 "my_options_bot"，必须以 bot 结尾）"
echo -e "  ${CYAN}5.${NC} BotFather 会返回一个 token，类似："
echo -e "     ${YELLOW}1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456${NC}"
echo ""

read -rp "粘贴你的 Bot Token（粘贴后按回车）: " BOT_TOKEN
BOT_TOKEN="$(echo "$BOT_TOKEN" | tr -d '[:space:]')"

if [ -z "$BOT_TOKEN" ]; then
    echo -e "${YELLOW}⚠ 未输入 Token，跳过 Bot 创建步骤。${NC}"
    echo "  你可以稍后手动编辑 .env 填入 TELEGRAM_BOT_TOKEN"
    BOT_TOKEN=""
fi

# ── 步骤 2：获取 Chat ID ──────────────────────────────────────
echo ""
echo -e "${BOLD}步骤 2 — 获取 Chat ID${NC}"
echo ""
echo "现在需要获取你的 Telegram Chat ID："
echo ""
echo -e "  ${CYAN}1.${NC} 在 Telegram 中找到你刚创建的 Bot"
echo -e "  ${CYAN}2.${NC} 给它发一条消息，比如 ${BOLD}/start${NC} 或 "你好""
echo ""
echo -e "  ${CYAN}3.${NC} 在浏览器打开以下地址（把 <token> 换成你的 token）："
echo ""

if [ -n "$BOT_TOKEN" ]; then
    echo -e "     ${BOLD}https://api.telegram.org/bot${BOT_TOKEN}/getUpdates${NC}"
else
    echo -e "     ${BOLD}https://api.telegram.org/bot<你的token>/getUpdates${NC}"
fi

echo ""
echo -e "  ${CYAN}4.${NC} 在返回的 JSON 中找到 ${BOLD}"chat":{"id":-1001234567890}${NC}"
echo -e "     那个数字（可能有负号）就是你的 Chat ID"
echo ""

read -rp "粘贴你的 Chat ID（粘贴后按回车）: " CHAT_ID
CHAT_ID="$(echo "$CHAT_ID" | tr -d '[:space:]')"

if [ -z "$CHAT_ID" ]; then
    echo -e "${YELLOW}⚠ 未输入 Chat ID，跳过。${NC}"
    echo "  你可以稍后手动编辑 .env 填入 TELEGRAM_CHAT_ID"
    CHAT_ID=""
fi

# ── 步骤 3：写入 .env ──────────────────────────────────────────
if [ -n "$BOT_TOKEN" ] || [ -n "$CHAT_ID" ]; then
    echo ""
    echo -e "${BOLD}步骤 3 — 写入 .env 配置${NC}"

    # 删除 .env 中旧的 Telegram 配置行（如果存在）
    if [ -f "$ENV_FILE" ]; then
        # 备份
        cp "$ENV_FILE" "${ENV_FILE}.bak"
        # 移除已取消注释的 Telegram 配置行（确保不会重复）
        sed -i '' '/^TELEGRAM_BOT_TOKEN=/d' "$ENV_FILE"
        sed -i '' '/^TELEGRAM_CHAT_ID=/d' "$ENV_FILE"
    fi

    # 追加配置到 .env
    {
        echo ""
        echo "# ══════════════════════════════════════════════════════════════"
        echo "# Telegram Bot 配置（由 setup_telegram.sh 自动生成）"
        echo "# ══════════════════════════════════════════════════════════════"
        if [ -n "$BOT_TOKEN" ]; then
            echo "TELEGRAM_BOT_TOKEN=${BOT_TOKEN}"
        fi
        if [ -n "$CHAT_ID" ]; then
            echo "TELEGRAM_CHAT_ID=${CHAT_ID}"
        fi
    } >> "$ENV_FILE"

    echo -e "  ${GREEN}✅ 已写入 $ENV_FILE${NC}"
    echo "  备份文件: ${ENV_FILE}.bak"

    # ── 步骤 4：验证连通性 ────────────────────────────────────
    if [ -n "$BOT_TOKEN" ] && [ -n "$CHAT_ID" ]; then
        echo ""
        echo -e "${BOLD}步骤 4 — 发送测试消息验证连通性${NC}"

        # 切换到项目目录
        cd "$PROJECT_DIR"

        # 读取 .env 确保 sed 后的新配置生效
        export TELEGRAM_BOT_TOKEN="$BOT_TOKEN"
        export TELEGRAM_CHAT_ID="$CHAT_ID"

        # 发送测试消息
        TEST_MSG="✅ *Auto Company 测试消息*\n\nTelegram 推送配置成功！\n系统将在下一次全量扫描时自动推送交易信号。\n\n时间: $(date '+%Y-%m-%d %H:%M:%S')"

        if command -v "$PROJECT_DIR/.venv/bin/python" &>/dev/null; then
            PYTHON="$PROJECT_DIR/.venv/bin/python"
        else
            PYTHON="python3"
        fi

        RESULT=$($PYTHON -c "
import os, sys
sys.path.insert(0, '$PROJECT_DIR')
from signals.telegram_notifier import send_message
os.environ['TELEGRAM_BOT_TOKEN'] = '$BOT_TOKEN'
os.environ['TELEGRAM_CHAT_ID'] = '$CHAT_ID'
# 重新加载模块（清除之前 import 时的缓存）
import importlib
import signals.telegram_notifier as tn
importlib.reload(tn)
ok = tn.send_message('$TEST_MSG', parse_mode='Markdown')
sys.exit(0 if ok else 1)
" 2>&1) || true

        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✅ 测试消息发送成功！${NC}"
            echo -e "  ${GREEN}   请查看你的 Telegram 消息。${NC}"
        else
            echo -e "  ${YELLOW}⚠ 发送失败，请检查：${NC}"
            echo "    1. Token 是否正确（注意冒号前后的字符要完整）"
            echo "    2. Chat ID 是否正确（可能有负号）"
            echo "    3. 网络是否能访问 api.telegram.org"
            echo "    4. 运行: curl -s \"https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/getMe\""
        fi
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ${GREEN}完成！${NC}                                                    ║"
echo "║                                                          ║"
echo "║  推送配置已保存到 .env                                    ║"
echo "║  下次全量扫描将自动启用 Telegram 推送                     ║"
echo "║                                                          ║"
echo "║  手动触发扫描测试:                                        ║"
echo "║    bash scripts/auto_scan.sh all                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
