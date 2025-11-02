#!/bin/bash

##############################################################################
# 🛑 OpenBR Biometric - STOP ALL SERVERS
#
# This script stops both the main biometric server and debug proxy
# Usage: ./STOP_ALL.sh
##############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}🛑 Stopping OpenBR Servers...${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"

# Kill processes on ports 5000 and 5001
echo -e "${YELLOW}🔴 Stopping Main Server (Port 5000)...${NC}"
if lsof -ti:5000 | xargs kill -9 2>/dev/null; then
    echo -e "${GREEN}✓ Main Server stopped${NC}"
else
    echo -e "${YELLOW}ℹ Main Server not running${NC}"
fi

echo -e "${YELLOW}🔴 Stopping Debug Proxy (Port 5001)...${NC}"
if lsof -ti:5001 | xargs kill -9 2>/dev/null; then
    echo -e "${GREEN}✓ Debug Proxy stopped${NC}"
else
    echo -e "${YELLOW}ℹ Debug Proxy not running${NC}"
fi

sleep 1

# Verify they are stopped
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Verifying all servers are stopped...${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"

if ps aux | grep -E "app_secure|debug_proxy" | grep -v grep > /dev/null; then
    echo -e "${RED}❌ Some processes still running${NC}"
    ps aux | grep -E "app_secure|debug_proxy" | grep -v grep
else
    echo -e "${GREEN}✓ All servers stopped successfully${NC}"
fi

echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
