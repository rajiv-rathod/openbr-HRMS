#!/bin/bash

##############################################################################
# 🚀 OpenBR Biometric + HRMS Integration - START ALL SERVERS
# 
# This script starts both the main biometric server and debug proxy
# Usage: ./START_ALL.sh
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 OpenBR Biometric Server - START ALL${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if requirements installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install -r requirements.txt -q
fi

# Kill any existing processes on ports 5000 and 5001
echo -e "${YELLOW}🛑 Stopping any existing servers...${NC}"
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
sleep 1

# Start main biometric server
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Starting Main Biometric Server (Port 5000)...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

nohup python3 app_secure.py > /tmp/app_secure.log 2>&1 &
APP_PID=$!
echo -e "${GREEN}✓ Process ID: $APP_PID${NC}"

# Wait for main server to start
sleep 3
if curl -s http://localhost:5000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Main Server is RUNNING ✓${NC}"
else
    echo -e "${RED}❌ Main Server failed to start${NC}"
    echo "Check logs: tail -f /tmp/app_secure.log"
    exit 1
fi

# Start debug proxy server
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Starting Debug Proxy Server (Port 5001)...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

nohup python3 debug_proxy.py > /tmp/debug_proxy.log 2>&1 &
PROXY_PID=$!
echo -e "${GREEN}✓ Process ID: $PROXY_PID${NC}"

# Wait for debug proxy to start
sleep 3
if curl -s http://localhost:5001/debug > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Debug Proxy is RUNNING ✓${NC}"
else
    echo -e "${RED}❌ Debug Proxy failed to start${NC}"
    echo "Check logs: tail -f /tmp/debug_proxy.log"
    exit 1
fi

# Print status
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓✓✓ ALL SERVERS STARTED SUCCESSFULLY ✓✓✓${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📍 URLS:${NC}"
echo -e "   Main Server:  ${GREEN}http://localhost:5000${NC}"
echo -e "   Debug Proxy:  ${GREEN}http://localhost:5001${NC}"
echo -e "   Debug UI:     ${GREEN}http://localhost:5001/debug${NC}"
echo ""
echo -e "${YELLOW}🔐 DEFAULT CREDENTIALS:${NC}"
echo -e "   Username: ${GREEN}admin${NC}"
echo -e "   Password: ${GREEN}admin123${NC}"
echo ""
echo -e "${YELLOW}📊 QUICK TEST:${NC}"
echo -e "   ${BLUE}curl -X POST http://localhost:5000/api/v1/api-token-auth/ \\${NC}"
echo -e "   ${BLUE}  -H \"Content-Type: application/json\" \\${NC}"
echo -e "   ${BLUE}  -d '{\"username\": \"admin\", \"password\": \"admin123\"}'${NC}"
echo ""
echo -e "${YELLOW}📝 LOGS:${NC}"
echo -e "   Main Server: ${GREEN}tail -f /tmp/app_secure.log${NC}"
echo -e "   Debug Proxy: ${GREEN}tail -f /tmp/debug_proxy.log${NC}"
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Ready for HRMS Integration! 🎉${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
