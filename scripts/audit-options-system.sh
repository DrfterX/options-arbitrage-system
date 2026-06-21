#!/bin/bash
# Critiq 代码审计 - 期货期权系统
# 使用 DeepSeek V4 Flash API

set -e

PROJECT_DIR="/Users/ayong/projects/auto-company_test"
AUDIT_TARGET="/Users/ayong/options_arbitrage_system"
LOG_DIR="${PROJECT_DIR}/logs"
DATE=$(date +%Y%m%d)
REPORT_FILE="${LOG_DIR}/audit-report-${DATE}.md"

cd "$PROJECT_DIR"

# 加载配置
source .env

export OPENAI_API_KEY="${DEEPSEEK_API_KEY}"
export OPENAI_API_BASE="${DEEPSEEK_API_URL}"

echo "🔍 开始审计: ${AUDIT_TARGET}"
echo "📄 报告文件: ${REPORT_FILE}"

# 创建审计报告头部
cat > "$REPORT_FILE" << EOF
# Critiq 代码审计报告

**审计目标**: ${AUDIT_TARGET}  
**审计时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**审计引擎**: Critiq (Auto Company)  
**底层模型**: DeepSeek V4 Flash  
**审计员**: CEO/CTO/FullStack 多智能体协作  

---

## 1. 项目结构概览

EOF

# 扫描项目结构
echo '### 目录结构' >> "$REPORT_FILE"
find "$AUDIT_TARGET" -type f -name "*.py" -o -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" 2>/dev/null | head -50 >> "$REPORT_FILE"

echo '

## 2. 代码质量分析

' >> "$REPORT_FILE"

echo "✅ 审计任务已初始化，准备启动 Claude CLI 进行深度审计..."
echo ""
echo "运行以下命令启动审计:"
echo "  cd ${PROJECT_DIR} && ./start-auto-loop.sh"
