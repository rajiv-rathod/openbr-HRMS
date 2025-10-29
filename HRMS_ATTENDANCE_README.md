# OpenBR HRMS - Biometric Attendance Module

## Overview

This repository now includes a **complete HRMS Biometric Attendance Module** that uses OpenBR for face recognition-based employee attendance tracking, with a **ZKTeco-compatible API interface**.

## What's New

### 🎯 HRMS Biometric Attendance System

A production-ready biometric attendance module that:

- ✅ **ZKTeco-Compatible Configuration** - Same fields as ZKTeco devices (API URL, Username, Password, Auth Token)
- ✅ **Face Recognition** - Uses OpenBR for accurate biometric verification
- ✅ **Employee Management** - Enroll employees with face templates
- ✅ **Attendance Tracking** - Check-in/Check-out with timestamps
- ✅ **REST API** - Complete API for HRMS integration
- ✅ **Simulation Mode** - Test without building OpenBR
- ✅ **Attendance Reports** - Generate detailed reports
- ✅ **Easy Integration** - Drop-in replacement for ZKTeco testing

## Quick Start (Testing Without OpenBR Build)

You can test the complete HRMS attendance system immediately without building OpenBR:

```bash
# Navigate to the HRMS attendance module
cd hrms_attendance/examples

# Run the basic usage example
python3 basic_usage.py
```

This will:
1. Create sample employees (John Doe, Jane Smith, Bob Johnson)
2. Enroll them with face templates (simulated)
3. Verify attendance (simulated)
4. Generate attendance reports
5. Save all data to local files

### Expected Output

```
======================================================================
HRMS Biometric Attendance - Basic Usage Example
======================================================================

ZKTeco API Settings:
  ZKTeco Api URL: http://localhost:8080/api/attendance
  Username: admin
  Password: ********
  Auth Token: sample_token_12345

✓ Employee John Doe (ID: EMP001) enrolled successfully
✓ Employee Jane Smith (ID: EMP002) enrolled successfully
✓ Employee Bob Johnson (ID: EMP003) enrolled successfully

✓ Attendance verified for John Doe (Score: 0.85)
```

## ZKTeco-Compatible Configuration

The module uses the exact same configuration format as ZKTeco devices:

### Configuration Fields

```json
{
    "ZKTeco Api URL": "http://localhost:8080/api/attendance",
    "Username": "admin",
    "Password": "admin123",
    "Auth Token": "your_secure_token"
}
```

### In Your HRMS

Simply point your HRMS to use these settings, and it works just like a ZKTeco device!

## Module Structure

```
hrms_attendance/
├── README.md              # Detailed documentation
├── requirements.txt       # Python dependencies
├── main.py               # Main entry point
├── config/               # Configuration management
│   └── settings.py       # ZKTeco-compatible config
├── core/                 # Core functionality
│   ├── attendance.py     # Attendance manager
│   └── employee.py       # Employee data model
├── api/                  # REST API
│   └── flask_api.py      # Flask-based API server
└── examples/             # Usage examples
    ├── basic_usage.py    # Complete example
    └── run_api_server.py # API server example
```

## Features in Detail

### 1. Employee Enrollment

```python
from hrms_attendance import AttendanceManager, AttendanceConfig

config = AttendanceConfig(
    api_url="http://localhost:8080/api/attendance",
    username="admin",
    password="admin123",
    auth_token="your_token"
)

manager = AttendanceManager(config)

# Enroll employee with face image
manager.enroll_employee(
    employee_id="EMP001",
    name="John Doe",
    face_image_path="/path/to/face.jpg",
    department="Engineering"
)
```

### 2. Attendance Verification

```python
# Verify attendance from face image
success, employee, score = manager.verify_attendance(
    face_image_path="/path/to/face.jpg",
    attendance_type="check-in"
)

if success:
    print(f"Welcome {employee.name}!")
```

### 3. REST API

Start the API server:

```bash
cd hrms_attendance/examples
python3 run_api_server.py
```

API Endpoints:

- `GET  /api/attendance/health` - Health check
- `GET  /api/attendance/config` - Get ZKTeco config
- `GET  /api/attendance/employees` - List employees
- `POST /api/attendance/enroll` - Enroll employee
- `POST /api/attendance/verify` - Verify attendance
- `GET  /api/attendance/logs` - Get attendance logs
- `GET  /api/attendance/report` - Generate report

### 4. Attendance Reports

```python
# Generate attendance report
report = manager.generate_attendance_report(
    start_date="2025-10-01",
    end_date="2025-10-31"
)
print(report)
```

Output:
```
================================================================================
ATTENDANCE REPORT
================================================================================
Period: 2025-10-01 to 2025-10-31
Total Records: 45
================================================================================
Employee ID     Name                      Type         Timestamp            Status
--------------------------------------------------------------------------------
EMP001          John Doe                  check-in     2025-10-29T09:00:00  success
EMP001          John Doe                  check-out    2025-10-29T17:30:00  success
...
```

## Integration with Your HRMS

### Option 1: Use the Python Module

```python
from hrms_attendance import AttendanceManager, AttendanceConfig

# In your HRMS code
config = AttendanceConfig.from_file('config.json')
manager = AttendanceManager(config)

# Integrate with your systems
def record_employee_attendance(face_image_path):
    success, employee, score = manager.verify_attendance(face_image_path)
    if success:
        # Record in your HRMS database
        save_to_database(employee.employee_id, datetime.now())
```

### Option 2: Use the REST API

```bash
# Start the API server
python3 hrms_attendance/examples/run_api_server.py
```

Then in your HRMS, make HTTP requests:

```bash
# Verify attendance
curl -X POST http://localhost:8080/api/attendance/verify \
  -H "Content-Type: application/json" \
  -H "X-Username: admin" \
  -H "X-Password: admin123" \
  -d '{"face_image_path": "/path/to/face.jpg", "attendance_type": "check-in"}'
```

## Testing Your HRMS

This module is perfect for testing your HRMS software before deploying with actual ZKTeco hardware:

1. **Configure** - Use the same config format as ZKTeco
2. **Test** - Run in simulation mode (no OpenBR build needed)
3. **Deploy** - Switch to actual ZKTeco when ready

### Simulation Mode Benefits

- ✅ No need to build OpenBR
- ✅ Test all HRMS integrations
- ✅ Verify API contracts
- ✅ Test error handling
- ✅ Generate test data

## Using with OpenBR (Production)

For actual face recognition in production:

1. Build OpenBR following the [official guide](http://openbiometrics.org/docs/install/)
2. Ensure `libopenbr.so` is in your library path
3. Run the examples - OpenBR will be automatically used

## Requirements

### For Testing (Simulation Mode)
- Python 3.7+
- Standard library only (json, datetime, dataclasses)

### For API Server
```bash
pip install flask flask-cors
```

### For Production (Real Face Recognition)
- OpenBR built and installed
- See: http://openbiometrics.org/docs/install/

## Documentation

Detailed documentation is available in:
- `hrms_attendance/README.md` - Complete API and usage guide
- `hrms_attendance/examples/basic_usage.py` - Working example with comments
- `hrms_attendance/examples/run_api_server.py` - API server example

## Example Usage

### Complete Working Example

```bash
cd hrms_attendance/examples
python3 basic_usage.py
```

This demonstrates:
- Configuration setup
- Employee enrollment
- Attendance verification
- Report generation
- Data persistence

### Running Tests

```bash
# Test the module
cd hrms_attendance/examples
python3 basic_usage.py

# Test the API server (requires Flask)
python3 run_api_server.py
```

## Files Generated

The system creates these files/directories:

- `config/attendance_config.json` - Configuration file
- `data/employees/employees.json` - Employee database
- `data/employees/*_template.br` - Face templates
- `logs/attendance.json` - Attendance logs

## Security Notes

⚠️ **For Production:**
- Change default username/password
- Use HTTPS for API
- Secure face template files
- Store auth tokens securely
- Add rate limiting

## Support and Help

### Common Issues

**Q: "Could not initialize OpenBR"**
A: This is expected if OpenBR isn't built. The system runs in simulation mode for testing.

**Q: "Flask not installed"**
A: Install Flask with: `pip install flask flask-cors`

**Q: How do I use this with my HRMS?**
A: See the Integration section above. Use either the Python module or REST API.

**Q: Can I test without building OpenBR?**
A: Yes! Run the examples in simulation mode.

### Getting Help

1. Read `hrms_attendance/README.md` for detailed docs
2. Check the examples in `hrms_attendance/examples/`
3. Review API documentation
4. Test in simulation mode first

## Original OpenBR

This repository is based on OpenBR (Open Biometrics Recognition).

For OpenBR-specific documentation, see:
- Website: www.openbiometrics.org
- Original README: See OpenBR documentation
- Build Instructions: http://openbiometrics.org/docs/install/

## License

Apache 2.0 - Same as OpenBR

## Contributing

Contributions welcome! This module is designed to help HRMS developers test biometric attendance systems.
