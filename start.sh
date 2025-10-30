#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI 交易系统 - 一键启动${NC}"
echo -e "${BLUE}========================================${NC}\n"

PROJECT_DIR="/Users/cuiqingsong/Desktop/222"
VENV="$PROJECT_DIR/.venv/bin/python3"

# 检查虚拟环境
if [ ! -f "$VENV" ]; then
    echo -e "${RED}❌ 虚拟环境不存在: $VENV${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 检测到虚拟环境${NC}\n"

# 启动交易系统
echo -e "${YELLOW}启动交易系统...${NC}"
echo "运行命令: $VENV $PROJECT_DIR/crypto_trading_bot_enhanced.py"
$VENV "$PROJECT_DIR/crypto_trading_bot_enhanced.py" > "$PROJECT_DIR/outputs/trading_system.log" 2>&1 &
TRADER_PID=$!
echo -e "${GREEN}✅ 交易系统已启动 (PID: $TRADER_PID)${NC}\n"

# 等待一秒
sleep 2

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 交易系统已启动${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "📊 ${BLUE}交易系统日志${NC}: tail -f outputs/trading_*.log"
echo -e "\n${YELLOW}按 Ctrl+C 停止${NC}\n"

# 保持脚本运行，跟随交易进程
wait $TRADER_PID
