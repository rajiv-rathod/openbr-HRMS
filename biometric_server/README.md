# Biometric Attendance System - ZKTeco Clone

A complete biometric attendance system built on OpenBR for face recognition. This system is designed to be compatible with HRMS software and provides a web-based interface for testing and management.

## Features

### Core Functionality
- **Employee Management**: Register and manage employees with photos
- **Face Punch System**: Record attendance using face recognition with confidence levels
- **Attendance Tracking**: Complete attendance records with timestamps and punch types (IN/OUT)
- **Attendance Summary**: Generate reports for date ranges
- **CSV Export**: Export attendance data for further analysis

### HRMS Integration
- **Connection Testing**: Test connectivity to external HRMS systems
- **Auth Token Generation**: Generate authentication tokens for API access
- **Attendance Sync**: Sync attendance data to your HRMS server
- **RESTful API**: Well-documented endpoints for integration

### System Features
- **Web Dashboard**: User-friendly interface for all operations
- **Real-time Statistics**: Live employee count, punch records, system status
- **Database Logging**: API calls and connection attempts are logged
- **Multi-user Support**: Simultaneous access from multiple clients

## System Requirements

- Linux OS (Ubuntu 18.04+)
- Python 3.6+
- 2GB RAM minimum
- Webcam for face capture (optional for testing)

## Installation

### 1. Quick Start (Recommended)

```bash
cd /workspaces/openbr/biometric_server
chmod +x start.sh
./start.sh
```

This will:
- Check Python 3 installation
- Install system dependencies
- Create Python virtual environment
- Install required packages
- Start the server

### 2. Manual Installation

```bash
# Update system
sudo apt-get update
sudo apt-get install python3-pip python3-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create upload directory
mkdir -p /tmp/biometric_uploads

# Start server
python3 app.py
```

## Running the Server

### Option 1: Using Start Script
```bash
./start.sh
```

### Option 2: Manual Start
```bash
source venv/bin/activate
python3 app.py
```

The server will start on `http://localhost:5000`

## Usage

### Web Dashboard Access
- URL: `http://localhost:5000`
- No authentication required for testing (add security before production use)

### Main Sections

#### 1. Dashboard
- View system statistics
- See today's attendance
- Monitor system health

#### 2. Employee Management
- Add new employees with photos
- View all registered employees
- Delete employees

#### 3. Attendance
- View all attendance records
- Filter by employee/date range
- Generate attendance summary reports
- Export to CSV

#### 4. Face Punch Test
- Start camera and capture photo
- Select employee and punch type
- Record attendance with confidence level
- View punch results immediately

#### 5. HRMS Integration
- Test connection to external HRMS
- Generate authentication tokens
- Sync attendance data to HRMS
- View API integration guide

## API Endpoints

### Health Check
```
GET /api/health
Response: { "status": "healthy", "timestamp": "..." }
```

### System Status
```
GET /api/status
Response: {
  "system": "ZKTeco-like Biometric Attendance System",
  "version": "1.0.0",
  "backend": "OpenBR",
  "status": "running",
  "employees": 5,
  "today_punches": 12,
  "total_records": 156
}
```

### Employee Management
```
GET /api/employees                    # Get all employees
POST /api/employees                   # Add new employee
GET /api/employees/{emp_id}          # Get employee details
DELETE /api/employees/{emp_id}       # Delete employee
```

**Add Employee (POST /api/employees):**
```bash
curl -X POST http://localhost:5000/api/employees \
  -F "emp_id=EMP001" \
  -F "name=John Doe" \
  -F "department=IT" \
  -F "photo=@path/to/photo.jpg"
```

### Attendance Recording
```
POST /api/attendance/punch            # Record face punch
{
  "emp_id": "EMP001",
  "punch_type": "IN",
  "photo": "base64_encoded_image",
  "confidence": 0.95
}

GET /api/attendance                   # Get attendance records
GET /api/attendance?emp_id=EMP001&start_date=2024-01-01&end_date=2024-01-31

GET /api/attendance/today             # Get today's attendance

GET /api/attendance/summary           # Get attendance summary
?start_date=2024-01-01&end_date=2024-01-31
```

### HRMS Integration
```
POST /api/test-hrms-connection
{
  "hrms_url": "http://110.78.645.123:8080",
  "hrms_username": "optional_username",
  "hrms_password": "optional_password"
}

POST /api/sync-attendance
{
  "hrms_url": "http://your-hrms-server",
  "endpoint": "/api/attendance",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

## Testing with Your HRMS

### Step 1: Prepare Test Data
1. Go to **Employee Management**
2. Add 2-3 test employees with photos
3. Note their employee IDs

### Step 2: Test Face Punch
1. Go to **Face Punch Test**
2. Start camera
3. Capture a photo
4. Select an employee
5. Choose IN/OUT
6. Click "Submit Punch"
7. Verify record in **Attendance** section

### Step 3: Test HRMS Connection
1. Go to **HRMS Integration**
2. Enter your HRMS server URL (e.g., http://110.78.645.123:8080)
3. Click "Test Connection"
4. If successful, proceed to sync

### Step 4: Sync Attendance
1. In **HRMS Integration** → Sync Attendance
2. Select date range
3. Click "Sync Attendance"
4. Check your HRMS system for received data

## Database Schema

### employees table
```sql
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  emp_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  department TEXT,
  photo_path TEXT,
  created_at TIMESTAMP
)
```

### attendance table
```sql
CREATE TABLE attendance (
  id INTEGER PRIMARY KEY,
  emp_id TEXT NOT NULL,
  employee_name TEXT,
  punch_type TEXT,
  timestamp TIMESTAMP,
  photo_path TEXT,
  confidence REAL,
  FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
)
```

### api_logs table
```sql
CREATE TABLE api_logs (
  id INTEGER PRIMARY KEY,
  endpoint TEXT,
  method TEXT,
  status_code INTEGER,
  response_time REAL,
  timestamp TIMESTAMP
)
```

## Database Location
- SQLite database: `/tmp/attendance.db`
- Uploaded photos: `/tmp/biometric_uploads/`

## Troubleshooting

### Port 5000 Already in Use
```bash
# Find and kill process using port 5000
sudo lsof -i :5000
sudo kill -9 <PID>

# Or use different port by editing app.py
# Change: app.run(host='0.0.0.0', port=5000, debug=True)
# To: app.run(host='0.0.0.0', port=8000, debug=True)
```

### Camera Not Working
- Check permissions: `ls -la /dev/video*`
- Try different browser (Chrome/Firefox usually work best)
- Ensure browser has camera permissions

### Database Error
```bash
# Reset database
rm /tmp/attendance.db
# Restart server - new database will be created
```

### Python Package Issues
```bash
# Reinstall packages
pip install --upgrade --force-reinstall -r requirements.txt
```

## Integration with Your HRMS

### API Format for Your HRMS
Your HRMS should expect attendance data in this format:

```json
{
  "attendance_records": [
    {
      "emp_id": "EMP001",
      "employee_name": "John Doe",
      "punch_type": "IN",
      "timestamp": "2024-01-15 09:30:00",
      "confidence": 0.95
    }
  ]
}
```

### For Developers Integrating This System
1. Use the `/api/attendance/punch` endpoint to record punches from your client
2. Use `/api/attendance` to retrieve records
3. Use `/api/sync-attendance` to push data to your HRMS
4. All endpoints accept JSON and return JSON responses

## Production Deployment Notes

Before deploying to production:

1. **Add Authentication**: Implement JWT or API key authentication
2. **Enable HTTPS**: Use SSL certificates
3. **Database**: Consider PostgreSQL for better performance
4. **Security**: Add rate limiting, input validation
5. **Logging**: Implement comprehensive logging
6. **Backup**: Set up automated database backups
7. **Access Control**: Implement role-based permissions

## File Structure

```
biometric_server/
├── app.py                 # Main Flask application
├── start.sh              # Quick start script
├── requirements.txt      # Python dependencies
├── templates/
│   └── dashboard.html    # Web interface
└── static/
    ├── style.css         # Styling
    └── script.js         # Frontend logic
```

## Support

For issues or questions:
1. Check the logs: Monitor terminal output
2. Check database: `sqlite3 /tmp/attendance.db`
3. Review API responses in browser developer console

## License

This system is built on top of OpenBR which is released under the Apache 2.0 License.

## Version

- Version: 1.0.0
- Backend: OpenBR
- Frontend: HTML5/CSS3/JavaScript
- Backend Framework: Flask
- Database: SQLite

---

**Ready to test? Run `./start.sh` and navigate to `http://localhost:5000`**
