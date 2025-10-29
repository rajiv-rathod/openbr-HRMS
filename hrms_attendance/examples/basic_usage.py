#!/usr/bin/env python3
"""
Example: Basic usage of HRMS Biometric Attendance Module
Demonstrates employee enrollment and attendance verification
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from hrms_attendance.config.settings import AttendanceConfig
from hrms_attendance.core.attendance import AttendanceManager


def main():
    """Main example function"""
    
    print("=" * 70)
    print("HRMS Biometric Attendance - Basic Usage Example")
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
    
    print("\n" + config.display_config())
    
    # Save configuration for reference
    config.save_to_file('./config/attendance_config.json')
    print("\n✓ Configuration saved to: ./config/attendance_config.json")
    
    # Initialize attendance manager
    print("\n" + "=" * 70)
    print("Initializing Attendance Manager...")
    print("=" * 70)
    manager = AttendanceManager(config)
    
    # Example 1: Enroll employees
    print("\n" + "=" * 70)
    print("Example 1: Enrolling Employees")
    print("=" * 70)
    
    # Note: In real usage, you would provide actual face image paths
    # For this example, we'll create dummy image files
    
    dummy_images = {
        'EMP001': './data/sample_faces/john_doe.jpg',
        'EMP002': './data/sample_faces/jane_smith.jpg',
        'EMP003': './data/sample_faces/bob_johnson.jpg'
    }
    
    # Create dummy image files for demonstration
    os.makedirs('./data/sample_faces', exist_ok=True)
    for emp_id, img_path in dummy_images.items():
        if not os.path.exists(img_path):
            with open(img_path, 'w') as f:
                f.write(f"DUMMY_IMAGE_DATA_{emp_id}")
    
    employees_to_enroll = [
        {
            'employee_id': 'EMP001',
            'name': 'John Doe',
            'department': 'Engineering',
            'designation': 'Software Engineer',
            'email': 'john.doe@company.com',
            'phone': '+1-555-0101',
            'face_image_path': dummy_images['EMP001']
        },
        {
            'employee_id': 'EMP002',
            'name': 'Jane Smith',
            'department': 'HR',
            'designation': 'HR Manager',
            'email': 'jane.smith@company.com',
            'phone': '+1-555-0102',
            'face_image_path': dummy_images['EMP002']
        },
        {
            'employee_id': 'EMP003',
            'name': 'Bob Johnson',
            'department': 'Sales',
            'designation': 'Sales Executive',
            'email': 'bob.johnson@company.com',
            'phone': '+1-555-0103',
            'face_image_path': dummy_images['EMP003']
        }
    ]
    
    for emp in employees_to_enroll:
        try:
            manager.enroll_employee(**emp)
        except Exception as e:
            print(f"✗ Error enrolling {emp['name']}: {e}")
    
    # Example 2: List all employees
    print("\n" + "=" * 70)
    print("Example 2: Listing All Employees")
    print("=" * 70)
    
    employees = manager.list_employees()
    print(f"\nTotal Employees: {len(employees)}")
    print(f"{'ID':<10} {'Name':<20} {'Department':<15} {'Status'}")
    print("-" * 60)
    for emp in employees:
        status = "Active" if emp.is_active else "Inactive"
        print(f"{emp.employee_id:<10} {emp.name:<20} {emp.department:<15} {status}")
    
    # Example 3: Verify attendance
    print("\n" + "=" * 70)
    print("Example 3: Verifying Attendance")
    print("=" * 70)
    
    # Simulate attendance verification
    test_image = dummy_images['EMP001']
    print(f"\nVerifying attendance with image: {test_image}")
    
    success, matched_emp, score = manager.verify_attendance(
        face_image_path=test_image,
        attendance_type="check-in"
    )
    
    if success and matched_emp:
        print(f"\n✓ Attendance verified successfully!")
        print(f"  Employee: {matched_emp.name}")
        print(f"  ID: {matched_emp.employee_id}")
        print(f"  Department: {matched_emp.department}")
        print(f"  Confidence: {score:.2%}")
    else:
        print(f"\n✗ Attendance verification failed")
        print(f"  Confidence: {score:.2%}")
    
    # Example 4: Get attendance logs
    print("\n" + "=" * 70)
    print("Example 4: Viewing Attendance Logs")
    print("=" * 70)
    
    logs = manager.get_attendance_logs()
    print(f"\nTotal Log Entries: {len(logs)}")
    if logs:
        print("\nRecent Attendance Logs:")
        for log in logs[-5:]:  # Show last 5 entries
            print(f"  {log['timestamp'][:19]} - {log['name']} ({log['employee_id']}) - {log['attendance_type']} - {log['status']}")
    
    # Example 5: Generate report
    print("\n" + "=" * 70)
    print("Example 5: Generating Attendance Report")
    print("=" * 70)
    
    report = manager.generate_attendance_report()
    print("\n" + report)
    
    # Cleanup
    manager.cleanup()
    
    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
    print("\nNote: This example runs in simulation mode.")
    print("For actual face recognition, ensure OpenBR is properly built and installed.")
    print("\nConfiguration and data have been saved to:")
    print("  - Config: ./config/attendance_config.json")
    print("  - Employee DB: ./data/employees/")
    print("  - Attendance Logs: ./logs/attendance.json")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
