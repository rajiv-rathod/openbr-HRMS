#!/usr/bin/env python3
"""
Example: Running the REST API Server
Demonstrates how to start the API server with ZKTeco-compatible interface
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from hrms_attendance.config.settings import AttendanceConfig
from hrms_attendance.api.flask_api import run_api_server


def main():
    """Run the API server"""
    
    print("=" * 70)
    print("HRMS Biometric Attendance - API Server")
    print("=" * 70)
    
    # Create configuration
    config = AttendanceConfig(
        api_url="http://localhost:8080/api/attendance",
        username="admin",
        password="admin123",
        auth_token="sample_token_12345",
        employee_db_path="./data/employees",
        attendance_log_path="./logs/attendance.json",
        face_recognition_threshold=0.7
    )
    
    print("\nAPI Configuration:")
    print(config.display_config())
    
    print("\n" + "=" * 70)
    print("Available API Endpoints:")
    print("=" * 70)
    print("\nHealth Check:")
    print("  GET  /api/attendance/health")
    print("\nConfiguration:")
    print("  GET  /api/attendance/config")
    print("\nEmployee Management:")
    print("  GET  /api/attendance/employees")
    print("  GET  /api/attendance/employees/<employee_id>")
    print("  POST /api/attendance/enroll")
    print("\nAttendance Operations:")
    print("  POST /api/attendance/verify")
    print("  GET  /api/attendance/logs")
    print("  GET  /api/attendance/report")
    
    print("\n" + "=" * 70)
    print("Authentication:")
    print("=" * 70)
    print("\nOption 1 - Using Headers:")
    print("  X-Username: admin")
    print("  X-Password: admin123")
    print("\nOption 2 - Using Token:")
    print("  Authorization: Bearer sample_token_12345")
    
    print("\n" + "=" * 70)
    print("Example cURL Commands:")
    print("=" * 70)
    
    print("\n1. Health Check:")
    print("   curl http://localhost:8080/api/attendance/health")
    
    print("\n2. List Employees:")
    print("   curl -H 'X-Username: admin' -H 'X-Password: admin123' \\")
    print("        http://localhost:8080/api/attendance/employees")
    
    print("\n3. Enroll Employee:")
    print("   curl -X POST -H 'Content-Type: application/json' \\")
    print("        -H 'X-Username: admin' -H 'X-Password: admin123' \\")
    print("        -d '{\"employee_id\":\"EMP001\",\"name\":\"John Doe\",")
    print("            \"face_image_path\":\"./data/sample_faces/john_doe.jpg\"}' \\")
    print("        http://localhost:8080/api/attendance/enroll")
    
    print("\n4. Verify Attendance:")
    print("   curl -X POST -H 'Content-Type: application/json' \\")
    print("        -H 'X-Username: admin' -H 'X-Password: admin123' \\")
    print("        -d '{\"face_image_path\":\"./data/sample_faces/john_doe.jpg\",")
    print("            \"attendance_type\":\"check-in\"}' \\")
    print("        http://localhost:8080/api/attendance/verify")
    
    print("\n" + "=" * 70)
    print("\nStarting API Server...")
    print("=" * 70 + "\n")
    
    try:
        # Run the API server
        run_api_server(config, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure Flask is installed: pip install flask flask-cors")


if __name__ == '__main__':
    main()
