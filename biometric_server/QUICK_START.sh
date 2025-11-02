#!/bin/bash

# BIOMETRIC SYSTEM - QUICK REFERENCE GUIDE
# Use this for quick commands

# Make executable
chmod +x /workspaces/openbr/biometric_server/start.sh

# ============================================
# QUICK COMMANDS
# ============================================

# 1. START THE SERVER (EASIEST)
# cd /workspaces/openbr/biometric_server
# ./start.sh

# 2. ACCESS DASHBOARD
# Open browser: http://localhost:5000

# 3. TEST ENDPOINTS (curl commands)

# Health check
# curl http://localhost:5000/api/health

# Get system status
# curl http://localhost:5000/api/status

# Get all employees
# curl http://localhost:5000/api/employees

# Get today's attendance
# curl http://localhost:5000/api/attendance/today

# ============================================
# EXAMPLE: Add Employee via Command Line
# ============================================
# curl -X POST http://localhost:5000/api/employees \
#   -F "emp_id=EMP001" \
#   -F "name=John Doe" \
#   -F "department=IT" \
#   -F "photo=@/path/to/photo.jpg"

# ============================================
# EXAMPLE: Record Attendance Punch
# ============================================
# curl -X POST http://localhost:5000/api/attendance/punch \
#   -H "Content-Type: application/json" \
#   -d '{
#     "emp_id": "EMP001",
#     "punch_type": "IN",
#     "confidence": 0.95
#   }'

# ============================================
# TROUBLESHOOTING
# ============================================

# If port 5000 is in use:
# sudo lsof -i :5000
# sudo kill -9 <PID>

# Check database
# sqlite3 /tmp/attendance.db ".tables"

# View recent punches
# sqlite3 /tmp/attendance.db "SELECT * FROM attendance LIMIT 10;"

# Delete all data (for fresh start)
# rm /tmp/attendance.db
# killall python3  # restart server

echo "✓ Biometric System Quick Reference Guide Ready"
echo ""
echo "Next steps:"
echo "1. cd /workspaces/openbr/biometric_server"
echo "2. ./start.sh"
echo "3. Open http://localhost:5000 in your browser"
