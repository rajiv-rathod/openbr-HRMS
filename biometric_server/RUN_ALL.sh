#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🚀 OpenBR Biometric HRMS Integration Server${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -q flask PyJWT opencv-python numpy requests 2>/dev/null

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}Starting servers...${NC}"
echo ""

# Kill any existing processes on ports 5000 and 5001
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:5001 | xargs kill -9 2>/dev/null
sleep 1

# Start main server (port 5000)
echo -e "${YELLOW}🔵 Starting Main Biometric Server (port 5000)...${NC}"
python3 app_secure.py > /tmp/app_secure.log 2>&1 &
APP_PID=$!
echo -e "${GREEN}✅ Started (PID: $APP_PID)${NC}"
sleep 2

# Start debug proxy (port 5001)
echo -e "${YELLOW}🟣 Starting Debug Proxy Server (port 5001)...${NC}"
python3 debug_proxy.py > /tmp/debug_proxy.log 2>&1 &
DEBUG_PID=$!
echo -e "${GREEN}✅ Started (PID: $DEBUG_PID)${NC}"
sleep 2

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✅ All servers running!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${BLUE}📍 Main Server:${NC}   http://localhost:5000"
echo -e "${BLUE}🐛 Debug Proxy:${NC}   http://localhost:5001"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo "   Main:  tail -f /tmp/app_secure.log"
echo "   Debug: tail -f /tmp/debug_proxy.log"
echo ""
echo -e "${YELLOW}🔐 Default Credentials:${NC}"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo -e "${YELLOW}🌐 Public URLs:${NC}"
echo "   Main:  https://weary-crypt-5jrjxprjv5xhvxvq-5000.app.github.dev/"
echo "   Debug: https://weary-crypt-5jrjxprjv5xhvxvq-5001.app.github.dev/"
echo ""
echo -e "${YELLOW}📊 Test Commands:${NC}"
echo "   curl http://localhost:5000/api/v1/health"
echo "   curl -X POST http://localhost:5000/api/v1/api-token-auth/ -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}'"
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "Press Ctrl+C to stop all servers"
echo -e "${BLUE}================================================${NC}"
echo ""

# Keep running
wait
