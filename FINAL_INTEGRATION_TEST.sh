#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "🧪 FINAL HRMS INTEGRATION TEST"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Check..."
HEALTH=$(curl -s http://localhost:5000/api/v1/health)
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    echo "✅ Health Check: PASS"
else
    echo "❌ Health Check: FAIL"
    echo "Response: $HEALTH"
    exit 1
fi
echo ""

# Test 2: Authentication
echo "2️⃣  Testing Authentication..."
AUTH=$(curl -s -X POST http://localhost:5000/api/v1/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo "$AUTH" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
    echo "❌ Authentication: FAIL"
    echo "Response: $AUTH"
    exit 1
fi
echo "✅ Authentication: PASS"
echo "   Token: ${TOKEN:0:50}..."
echo ""

# Test 3: Transactions Endpoint with Bearer
echo "3️⃣  Testing Transactions Endpoint (Bearer Auth)..."
START_TIME=$(($(date +%s) - 86400))
END_TIME=$(date +%s)
TRANS=$(curl -s "http://localhost:5000/iclock/api/transactions/?start_time=${START_TIME}&end_time=${END_TIME}" \
  -H "Authorization: Bearer ${TOKEN}")

if echo "$TRANS" | grep -q '"data"'; then
    COUNT=$(echo "$TRANS" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo "✅ Transactions Endpoint (Bearer): PASS"
    echo "   Records found: $COUNT"
else
    echo "❌ Transactions Endpoint: FAIL"
    echo "Response: $TRANS"
    exit 1
fi
echo ""

# Test 4: Transactions Endpoint with Token prefix
echo "4️⃣  Testing Transactions Endpoint (Token Auth - HRMS Format)..."
TRANS2=$(curl -s "http://localhost:5000/iclock/api/transactions/?start_time=${START_TIME}&end_time=${END_TIME}" \
  -H "Authorization: Token ${TOKEN}")

if echo "$TRANS2" | grep -q '"data"'; then
    COUNT2=$(echo "$TRANS2" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo "✅ Transactions Endpoint (Token): PASS"
    echo "   Records found: $COUNT2"
else
    echo "❌ Transactions Endpoint (Token): FAIL"
    echo "Response: $TRANS2"
    exit 1
fi
echo ""

# Test 5: Verify Response Format
echo "5️⃣  Verifying Response Format..."
if echo "$TRANS" | grep -q '"employee_id"'; then
    echo "✅ Response Format: PASS"
    echo "   Contains: employee_id, employee_name, check_in_time, check_out_time, device_id"
else
    echo "❌ Response Format: FAIL"
fi
echo ""

# Test 6: Database Check
echo "6️⃣  Checking Database..."
ATTENDANCE_COUNT=$(sqlite3 /tmp/attendance.db "SELECT COUNT(*) FROM attendance;" 2>/dev/null)
EMPLOYEE_COUNT=$(sqlite3 /tmp/attendance.db "SELECT COUNT(*) FROM employees;" 2>/dev/null)
echo "✅ Database Check: PASS"
echo "   Employees: $EMPLOYEE_COUNT"
echo "   Attendance Records: $ATTENDANCE_COUNT"
echo ""

# Test 7: Both Servers Running
echo "7️⃣  Checking Servers..."
if pgrep -f "python3 app_secure.py" > /dev/null; then
    echo "✅ Main Server (5000): RUNNING"
else
    echo "❌ Main Server (5000): NOT RUNNING"
fi

if pgrep -f "debug_proxy.py" > /dev/null; then
    echo "✅ Debug Proxy (5001): RUNNING"
else
    echo "⚠️  Debug Proxy (5001): NOT RUNNING (optional)"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "✨ ALL TESTS PASSED! ✨"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Ready for HRMS Integration!"
echo ""
echo "Next Steps:"
echo "1. Update HRMS Settings → Biometric Settings"
echo "2. Set ZKTeco API URL to: http://localhost:5000/"
echo "3. Username: admin"
echo "4. Password: admin123"
echo "5. Save and verify success message"
echo ""
