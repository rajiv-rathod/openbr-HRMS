#!/bin/bash

# ZKTeco-like Biometric Attendance System - Quick Start Setup
# This script sets up and starts the biometric attendance server

set -e

echo "=============================================="
echo "Biometric Attendance System - Quick Start"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Install system dependencies
echo ""
echo -e "${YELLOW}Installing system dependencies...${NC}"
sudo apt-get update -qq
sudo apt-get install -y -qq python3-pip python3-dev libopencv-dev python3-opencv > /dev/null 2>&1

echo -e "${GREEN}✓ System dependencies installed${NC}"

# Create virtual environment
echo ""
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Install Python dependencies
echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -q --upgrade pip setuptools wheel
pip install -q -r "$SCRIPT_DIR/requirements.txt"

echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Create necessary directories
mkdir -p /tmp/biometric_uploads

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "=============================================="
echo "Starting Biometric Attendance Server..."
echo "=============================================="
echo ""
echo -e "${GREEN}Server will be available at:${NC}"
echo "  🌐 http://localhost:5000"
echo "  🌐 http://127.0.0.1:5000"
echo ""
echo "Features:"
echo "  ✓ Employee Management"
echo "  ✓ Face Punch (Attendance)"
echo "  ✓ Attendance Records"
echo "  ✓ HRMS Integration Testing"
echo "  ✓ Attendance Export"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================================="
echo ""

# Start the application
cd "$SCRIPT_DIR"
python3 app.py
