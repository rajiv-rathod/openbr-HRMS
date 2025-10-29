# HRMS Biometric Attendance Module

A comprehensive biometric attendance system for HRMS using OpenBR face recognition, with ZKTeco-compatible API interface.

## Overview

This module provides a complete biometric attendance solution that:
- Uses OpenBR for face recognition and verification
- Provides ZKTeco-compatible API configuration
- Manages employee enrollment and attendance tracking
- Offers REST API for integration with HRMS systems
- Supports both check-in and check-out operations
- Generates detailed attendance reports

## Features

### ✓ ZKTeco-Compatible Configuration
- **ZKTeco Api URL**: Configure API endpoint
- **Username**: API authentication username
- **Password**: Secure password authentication
- **Auth Token**: Token-based authentication support

### ✓ Biometric Operations
- Employee face enrollment
- Real-time attendance verification
- Face recognition with configurable threshold
- Support for multiple employees

### ✓ Attendance Management
- Automatic attendance logging
- Check-in/Check-out tracking
- Historical attendance records
- Detailed attendance reports
- Employee database management

### ✓ REST API Interface
- Health check endpoint
- Employee management APIs
- Attendance verification APIs
- Report generation APIs
- Token and credential-based authentication

## Installation

### Prerequisites

1. **OpenBR**: The biometric recognition library
   ```bash
   # Follow OpenBR installation guide at:
   # http://openbiometrics.org/docs/install/
   ```

2. **Python Dependencies** (for API server):
   ```bash
   pip install flask flask-cors
   ```

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/rajiv-rathod/openbr-HRMS.git
   cd openbr-HRMS
   ```

2. The HRMS attendance module is located in `hrms_attendance/`

3. Ensure OpenBR is built and installed (or use simulation mode for testing)

## Quick Start

### 1. Basic Usage Example

```python
from hrms_attendance.config.settings import AttendanceConfig
from hrms_attendance.core.attendance import AttendanceManager

# Create configuration
config = AttendanceConfig(
    api_url="http://localhost:8080/api/attendance",
    username="admin",
    password="admin123",
    auth_token="your_secure_token",
    employee_db_path="./data/employees",
    attendance_log_path="./logs/attendance.json"
)

# Initialize manager
manager = AttendanceManager(config)

# Enroll an employee
manager.enroll_employee(
    employee_id="EMP001",
    name="John Doe",
    face_image_path="/path/to/face/image.jpg",
    department="Engineering",
    designation="Software Engineer"
)

# Verify attendance
success, employee, score = manager.verify_attendance(
    face_image_path="/path/to/face/image.jpg",
    attendance_type="check-in"
)

if success:
    print(f"Attendance verified for {employee.name}")
```

### 2. Running the Examples

Run the basic usage example:
```bash
cd hrms_attendance/examples
python basic_usage.py
```

Run the API server:
```bash
cd hrms_attendance/examples
python run_api_server.py
```

## Configuration

### Configuration File Format

Create a JSON configuration file:

```json
{
    "api_url": "http://localhost:8080/api/attendance",
    "username": "admin",
    "password": "admin123",
    "auth_token": "your_secure_token_here",
    "openbr_sdk_path": "/usr/local/lib",
    "face_recognition_threshold": 0.7,
    "employee_db_path": "./data/employees",
    "attendance_log_path": "./logs/attendance.json"
}
```

### Loading Configuration

```python
from hrms_attendance.config.settings import AttendanceConfig

# Load from file
config = AttendanceConfig.from_file('config/attendance_config.json')

# Or create programmatically
config = AttendanceConfig(
    api_url="http://localhost:8080/api/attendance",
    username="admin",
    password="admin123"
)

# Save configuration
config.save_to_file('config/attendance_config.json')

# Display configuration
print(config.display_config())
```

## API Reference

### REST API Endpoints

#### Health Check
```
GET /api/attendance/health
```
Check if the service is running.

**Response:**
```json
{
    "status": "ok",
    "service": "HRMS Biometric Attendance",
    "version": "1.0.0",
    "timestamp": "2025-10-29T18:00:00"
}
```

#### Get Configuration
```
GET /api/attendance/config
Headers: X-Username, X-Password
```
Get current ZKTeco-compatible configuration.

**Response:**
```json
{
    "ZKTeco Api URL": "http://localhost:8080/api/attendance",
    "Username": "admin",
    "Password": "admin123",
    "Auth Token": "your_token"
}
```

#### List Employees
```
GET /api/attendance/employees
Headers: X-Username, X-Password
```
Get list of all enrolled employees.

**Response:**
```json
{
    "count": 3,
    "employees": [
        {
            "employee_id": "EMP001",
            "name": "John Doe",
            "department": "Engineering",
            "designation": "Software Engineer",
            "is_active": true
        }
    ]
}
```

#### Enroll Employee
```
POST /api/attendance/enroll
Headers: X-Username, X-Password, Content-Type: application/json
```

**Request Body:**
```json
{
    "employee_id": "EMP001",
    "name": "John Doe",
    "face_image_path": "/path/to/image.jpg",
    "department": "Engineering",
    "designation": "Software Engineer",
    "email": "john@example.com",
    "phone": "+1-555-0101"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Employee John Doe enrolled successfully",
    "employee_id": "EMP001"
}
```

#### Verify Attendance
```
POST /api/attendance/verify
Headers: X-Username, X-Password, Content-Type: application/json
```

**Request Body:**
```json
{
    "face_image_path": "/path/to/image.jpg",
    "attendance_type": "check-in"
}
```

**Response (Success):**
```json
{
    "success": true,
    "employee": {
        "employee_id": "EMP001",
        "name": "John Doe",
        "department": "Engineering"
    },
    "confidence_score": 0.95,
    "attendance_type": "check-in",
    "timestamp": "2025-10-29T18:00:00"
}
```

#### Get Attendance Logs
```
GET /api/attendance/logs?employee_id=EMP001&start_date=2025-10-01&end_date=2025-10-31
Headers: X-Username, X-Password
```

**Response:**
```json
{
    "count": 20,
    "logs": [
        {
            "employee_id": "EMP001",
            "name": "John Doe",
            "timestamp": "2025-10-29T09:00:00",
            "attendance_type": "check-in",
            "confidence_score": 0.95,
            "status": "success"
        }
    ]
}
```

#### Generate Report
```
GET /api/attendance/report?start_date=2025-10-01&end_date=2025-10-31
Headers: X-Username, X-Password
```

**Response:**
```json
{
    "report": "Formatted text report...",
    "generated_at": "2025-10-29T18:00:00"
}
```

## Testing the System

### Without Building OpenBR

The system includes a simulation mode that works without a full OpenBR installation. This is perfect for testing your HRMS integration:

```bash
cd hrms_attendance/examples
python basic_usage.py
```

This will:
1. Create sample employee records
2. Simulate face enrollment
3. Simulate attendance verification
4. Generate attendance reports
5. Save all data to local files

### With OpenBR Built

For production use with actual face recognition:

1. Build and install OpenBR following the official guide
2. Ensure `libopenbr.so` or `libopenbr.dylib` is in your library path
3. Run the examples - OpenBR will be automatically used

## Integration with HRMS

### Using the API

1. Start the API server:
   ```bash
   python hrms_attendance/examples/run_api_server.py
   ```

2. Configure your HRMS to use the endpoints:
   - Base URL: `http://localhost:8080/api/attendance`
   - Username: `admin`
   - Password: `admin123`
   - Auth Token: `your_token`

3. Use the REST API from your HRMS application

### Using the Python Module

```python
from hrms_attendance import AttendanceManager, AttendanceConfig

# In your HRMS code
config = AttendanceConfig.from_file('path/to/config.json')
manager = AttendanceManager(config)

# Integrate with your employee management
def on_employee_hired(employee_data):
    manager.enroll_employee(
        employee_id=employee_data['id'],
        name=employee_data['name'],
        face_image_path=employee_data['photo_path']
    )

# Integrate with your attendance system
def process_biometric_scan(image_path):
    success, employee, score = manager.verify_attendance(image_path)
    if success:
        # Record attendance in your HRMS database
        record_attendance(employee.employee_id, datetime.now())
```

## ZKTeco Compatibility

This module provides a ZKTeco-compatible interface, making it easy to switch between testing with OpenBR and production ZKTeco devices:

### Configuration Fields Match ZKTeco
- **ZKTeco Api URL** → API endpoint
- **Username** → Authentication username
- **Password** → Authentication password
- **Auth Token** → Token for API access

### Similar API Structure
The REST API follows patterns similar to ZKTeco devices, making integration straightforward.

## Directory Structure

```
hrms_attendance/
├── __init__.py              # Module initialization
├── config/                  # Configuration management
│   ├── __init__.py
│   └── settings.py          # AttendanceConfig class
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── attendance.py        # AttendanceManager class
│   └── employee.py          # Employee data model
├── api/                     # REST API
│   ├── __init__.py
│   └── flask_api.py         # Flask-based API
└── examples/                # Usage examples
    ├── __init__.py
    ├── basic_usage.py       # Basic usage example
    └── run_api_server.py    # API server example
```

## Data Storage

### Employee Database
Located at `employee_db_path` (default: `./data/employees/`)
- `employees.json`: Employee records
- `<employee_id>_template.br`: Face templates

### Attendance Logs
Located at `attendance_log_path` (default: `./logs/attendance.json`)
- JSON format with timestamp, employee info, and status

## Security Notes

1. **Change Default Credentials**: Always change the default username/password in production
2. **Use HTTPS**: Deploy the API behind HTTPS in production
3. **Secure Token Storage**: Store auth tokens securely
4. **Face Template Security**: Protect face template files with appropriate permissions
5. **API Rate Limiting**: Consider adding rate limiting in production

## Troubleshooting

### OpenBR Not Found
If you see "Could not initialize OpenBR", the system will run in simulation mode. This is fine for testing but requires OpenBR for actual face recognition.

### Flask Not Installed
Install Flask to use the API server:
```bash
pip install flask flask-cors
```

### Permission Errors
Ensure the application has write permissions for:
- Employee database directory
- Attendance log directory
- Configuration directory

## Support

For issues or questions:
1. Check the examples in `hrms_attendance/examples/`
2. Review the API documentation above
3. Ensure all prerequisites are installed
4. Check file permissions for data directories

## License

This module is part of the OpenBR HRMS project and follows the same license as OpenBR (Apache 2.0).

## Author

HRMS Development Team
Built on top of OpenBR (Open Biometrics Recognition)
