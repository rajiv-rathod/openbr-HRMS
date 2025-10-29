"""
Flask-based REST API for HRMS Biometric Attendance
ZKTeco-compatible API interface
"""

import os
import json
from datetime import datetime
from typing import Optional

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    Flask = None
    FLASK_AVAILABLE = False
    print("Flask not installed. API functionality will be limited.")
    print("Install with: pip install flask flask-cors")

from ..config.settings import AttendanceConfig
from ..core.attendance import AttendanceManager


def create_attendance_api(config: AttendanceConfig):
    """
    Create Flask API application for attendance management.
    
    Args:
        config: AttendanceConfig instance
        
    Returns:
        Flask app instance or None if Flask not available
    """
    if not FLASK_AVAILABLE:
        return None
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Initialize attendance manager
    manager = AttendanceManager(config)
    
    # Middleware for API authentication
    def authenticate():
        """Check API authentication"""
        auth_token = request.headers.get('Authorization', '')
        username = request.headers.get('X-Username', '')
        password = request.headers.get('X-Password', '')
        
        # Check token or username/password
        if config.auth_token:
            if auth_token != f"Bearer {config.auth_token}":
                if username != config.username or password != config.password:
                    return False
        else:
            if username != config.username or password != config.password:
                return False
        
        return True
    
    @app.route('/api/attendance/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'service': 'HRMS Biometric Attendance',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/attendance/config', methods=['GET'])
    def get_config():
        """Get current configuration (ZKTeco format)"""
        if not authenticate():
            return jsonify({'error': 'Unauthorized'}), 401
        
        return jsonify(config.get_zkteco_format())
    
    @app.route('/api/attendance/employees', methods=['GET'])
    def list_employees():
        """List all employees"""
        if not authenticate():
            return jsonify({'error': 'Unauthorized'}), 401
        
        employees = manager.list_employees()
        return jsonify({
            'count': len(employees),
            'employees': [emp.to_dict() for emp in employees]
        })
    
    @app.route('/api/attendance/employees/<employee_id>', methods=['GET'])
    def get_employee(employee_id: str):
        """Get employee details"""
        if not authenticate():
            return jsonify({'error': 'Unauthorized'}), 401
        
        employee = manager.get_employee(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify(employee.to_dict())
    
    @app.route('/api/attendance/enroll', methods=['POST'])
    def enroll_employee():
        """Enroll new employee"""
        if not authenticate():
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        required_fields = ['employee_id', 'name', 'face_image_path']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        try:
            success = manager.enroll_employee(
                employee_id=data['employee_id'],
                name=data['name'],
                face_image_path=data['face_image_path'],
                department=data.get('department', ''),
                designation=data.get('designation', ''),
                email=data.get('email', ''),
                phone=data.get('phone', '')
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f"Employee {data['name']} enrolled successfully",
                    'employee_id': data['employee_id']
                })
            else:
                return jsonify({'error': 'Enrollment failed'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/attendance/verify', methods=['POST'])
    def verify_attendance():
        """Verify attendance from face image"""
        if not authenticate():
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        if 'face_image_path' not in data:
            return jsonify({'error': 'Missing face_image_path'}), 400
        
        attendance_type = data.get('attendance_type', 'check-in')
        
        try:
            success, employee, score = manager.verify_attendance(
                face_image_path=data['face_image_path'],
                attendance_type=attendance_type
            )
            
            if success and employee:
                return jsonify({
                    'success': True,
                    'employee': employee.to_dict(),
                    'confidence_score': score,
                    'attendance_type': attendance_type,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Face verification failed',
                    'confidence_score': score
                }), 200  # Return 200 with success=false for failed verification
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/attendance/logs', methods=['GET'])
    def get_attendance_logs():
        """Get attendance logs with optional filters"""
        if not authenticate():
            return jsonify({'error': 'Unauthorized'}), 401
        
        employee_id = request.args.get('employee_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        logs = manager.get_attendance_logs(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'count': len(logs),
            'logs': logs
        })
    
    @app.route('/api/attendance/report', methods=['GET'])
    def generate_report():
        """Generate attendance report"""
        if not authenticate():
            return jsonify({'error': 'Unauthorized'}), 401
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        report = manager.generate_attendance_report(
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'report': report,
            'generated_at': datetime.now().isoformat()
        })
    
    return app


def run_api_server(config: AttendanceConfig, host: str = '0.0.0.0', port: int = 8080):
    """
    Run the API server.
    
    Args:
        config: AttendanceConfig instance
        host: Host to bind to
        port: Port to bind to
    """
    if not FLASK_AVAILABLE:
        print("Error: Flask is required to run the API server")
        print("Install with: pip install flask flask-cors")
        return
    
    app = create_attendance_api(config)
    if app:
        print(f"\n{'='*60}")
        print("HRMS Biometric Attendance API Server")
        print(f"{'='*60}")
        print(f"API URL: http://{host}:{port}")
        print(f"Username: {config.username}")
        print(f"Password: {'*' * len(config.password)}")
        if config.auth_token:
            print(f"Auth Token: {config.auth_token[:20]}...")
        print(f"{'='*60}\n")
        
        app.run(host=host, port=port, debug=False)
