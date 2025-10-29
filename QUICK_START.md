# HRMS Biometric Attendance - Quick Start Guide

## For HRMS Software Testing

This guide helps you quickly test biometric attendance in your HRMS software using OpenBR, before purchasing ZKTeco hardware.

## 🎯 What You Get

A complete biometric attendance system with:

### ZKTeco-Compatible Fields:
- ✅ **ZKTeco Api URL**: `http://localhost:8080/api/attendance`
- ✅ **Username**: `admin`
- ✅ **Password**: `admin123`
- ✅ **Auth Token**: `your_secure_token`

### Features:
- ✅ Employee enrollment with face images
- ✅ Attendance check-in/check-out
- ✅ Attendance logs and reports
- ✅ REST API for integration
- ✅ Works without building OpenBR (simulation mode)

## 🚀 5-Minute Quick Start

### Step 1: Run the Example (1 minute)

```bash
cd hrms_attendance/examples
python3 basic_usage.py
```

**What this does:**
- Creates 3 sample employees
- Enrolls them with face templates
- Verifies attendance
- Generates a report
- Saves data to files

### Step 2: Check the Results (1 minute)

Files created:
- `config/attendance_config.json` - Configuration
- `data/employees/employees.json` - Employee database
- `logs/attendance.json` - Attendance records

View the configuration:
```bash
cat config/attendance_config.json
```

### Step 3: Test the API (3 minutes)

Start the API server:
```bash
cd hrms_attendance/examples
python3 run_api_server.py
```

Then in another terminal, test the API:

```bash
# Health check
curl http://localhost:8080/api/attendance/health

# Get configuration (ZKTeco format)
curl -H "X-Username: admin" -H "X-Password: admin123" \
     http://localhost:8080/api/attendance/config

# List employees
curl -H "X-Username: admin" -H "X-Password: admin123" \
     http://localhost:8080/api/attendance/employees
```

## 📋 Integration with Your HRMS

### Option A: Using the Configuration File

Your HRMS needs these fields (just like ZKTeco):

```json
{
    "ZKTeco Api URL": "http://localhost:8080/api/attendance",
    "Username": "admin",
    "Password": "admin123",
    "Auth Token": "sample_token_12345"
}
```

### Option B: Using the REST API

1. **Start the server:**
   ```bash
   python3 hrms_attendance/examples/run_api_server.py
   ```

2. **In your HRMS, call these endpoints:**

   **Enroll Employee:**
   ```http
   POST http://localhost:8080/api/attendance/enroll
   Headers: 
     X-Username: admin
     X-Password: admin123
     Content-Type: application/json
   Body: 
     {
       "employee_id": "EMP001",
       "name": "John Doe",
       "face_image_path": "/path/to/face.jpg",
       "department": "Engineering"
     }
   ```

   **Verify Attendance:**
   ```http
   POST http://localhost:8080/api/attendance/verify
   Headers:
     X-Username: admin
     X-Password: admin123
     Content-Type: application/json
   Body:
     {
       "face_image_path": "/path/to/face.jpg",
       "attendance_type": "check-in"
     }
   ```

   **Get Attendance Logs:**
   ```http
   GET http://localhost:8080/api/attendance/logs?employee_id=EMP001
   Headers:
     X-Username: admin
     X-Password: admin123
   ```

### Option C: Using Python Module

If your HRMS is Python-based:

```python
from hrms_attendance import AttendanceManager, AttendanceConfig

# Initialize
config = AttendanceConfig(
    api_url="http://localhost:8080/api/attendance",
    username="admin",
    password="admin123",
    auth_token="your_token"
)

manager = AttendanceManager(config)

# Enroll employee
manager.enroll_employee(
    employee_id="EMP001",
    name="John Doe",
    face_image_path="/path/to/face.jpg"
)

# Verify attendance
success, employee, score = manager.verify_attendance(
    face_image_path="/path/to/face.jpg",
    attendance_type="check-in"
)
```

## 🔧 Configuration in Your HRMS

### For Testing (No OpenBR build needed)
The system works in simulation mode - perfect for testing your HRMS!

### For Production
When ready for production:
1. Build OpenBR following official guide
2. Or switch to actual ZKTeco hardware
3. Your HRMS code doesn't change!

## 📊 Testing Scenarios

### Scenario 1: Employee Enrollment Flow
```bash
# Run the example
python3 hrms_attendance/examples/basic_usage.py

# Check employees were created
cat data/employees/employees.json
```

### Scenario 2: Attendance Verification
The example already demonstrates this with:
- Check-in event
- Logged with timestamp
- Stored in `logs/attendance.json`

### Scenario 3: Reports
```python
from hrms_attendance import AttendanceManager, AttendanceConfig

config = AttendanceConfig.from_file('config/attendance_config.json')
manager = AttendanceManager(config)

# Generate report
report = manager.generate_attendance_report()
print(report)
```

## 🎨 Customization

### Change Default Credentials

Edit the configuration:

```python
config = AttendanceConfig(
    api_url="http://your-server:8080/api/attendance",
    username="your_username",
    password="your_password",
    auth_token="your_secure_token"
)

config.save_to_file('config/attendance_config.json')
```

### Change Recognition Threshold

```python
config = AttendanceConfig(
    face_recognition_threshold=0.8  # More strict (0.0 to 1.0)
)
```

### Custom Data Paths

```python
config = AttendanceConfig(
    employee_db_path="/custom/path/employees",
    attendance_log_path="/custom/path/logs/attendance.json"
)
```

## 📝 Example HRMS Integration Code

Here's a complete example for your HRMS:

```python
# In your HRMS application

from hrms_attendance import AttendanceManager, AttendanceConfig
from datetime import datetime

# Initialize once at app startup
config = AttendanceConfig(
    api_url="http://localhost:8080/api/attendance",
    username="admin",
    password="admin123"
)
attendance_manager = AttendanceManager(config)

# When HR enrolls a new employee
def on_employee_hired(employee_data):
    """Called when HR adds a new employee"""
    try:
        attendance_manager.enroll_employee(
            employee_id=employee_data['employee_id'],
            name=employee_data['full_name'],
            face_image_path=employee_data['photo_path'],
            department=employee_data['department'],
            email=employee_data['email']
        )
        print(f"✓ Biometric enrolled for {employee_data['full_name']}")
    except Exception as e:
        print(f"✗ Enrollment failed: {e}")

# When employee uses biometric scanner
def process_attendance_scan(image_path, scan_type="check-in"):
    """Called when employee scans their face"""
    success, employee, confidence = attendance_manager.verify_attendance(
        face_image_path=image_path,
        attendance_type=scan_type
    )
    
    if success:
        # Record in your HRMS database
        save_attendance_to_database(
            employee_id=employee.employee_id,
            timestamp=datetime.now(),
            type=scan_type,
            status='present'
        )
        
        return {
            'success': True,
            'message': f"Welcome {employee.name}!",
            'employee': employee.to_dict(),
            'confidence': confidence
        }
    else:
        return {
            'success': False,
            'message': 'Face not recognized',
            'confidence': confidence
        }

# Generate daily attendance report
def get_daily_attendance_report(date):
    """Get attendance report for a specific date"""
    start = f"{date}T00:00:00"
    end = f"{date}T23:59:59"
    
    report = attendance_manager.generate_attendance_report(
        start_date=start,
        end_date=end
    )
    
    return report
```

## ❓ Common Questions

**Q: Do I need to build OpenBR?**
A: No! For testing your HRMS, it works in simulation mode.

**Q: Will this work exactly like ZKTeco?**
A: Yes! The configuration fields and API structure match ZKTeco for easy testing.

**Q: Can I test my entire HRMS now?**
A: Yes! Enroll employees, verify attendance, generate reports - everything works.

**Q: What happens when I switch to real ZKTeco?**
A: Just update the configuration URLs. Your HRMS code stays the same!

**Q: Is this production-ready?**
A: For testing, yes! For production with real face recognition, build OpenBR or use ZKTeco hardware.

## 📚 Next Steps

1. ✅ Run the quick start (above)
2. ✅ Test the API endpoints
3. ✅ Integrate with your HRMS
4. ✅ Test all attendance workflows
5. ✅ Deploy your HRMS for testing

## 📖 Full Documentation

- **Complete Guide**: `hrms_attendance/README.md`
- **API Reference**: See API section in README
- **Code Examples**: `hrms_attendance/examples/`

## 🆘 Need Help?

1. Check `hrms_attendance/README.md` for detailed docs
2. Run the examples: `python3 hrms_attendance/examples/basic_usage.py`
3. Review the code in `hrms_attendance/examples/`

## 🎉 You're Ready!

Your HRMS can now be fully tested with biometric attendance before purchasing any hardware!

**Quick command to get started:**
```bash
cd hrms_attendance/examples && python3 basic_usage.py
```

Happy testing! 🚀
