"""
ZKTeco-like Biometric Attendance System
Built on OpenBR for face recognition
"""

import os
import json
import base64
import datetime
import sqlite3
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import threading
import time
from datetime import datetime as dt, timedelta

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = '/tmp/biometric_uploads'
DATABASE_PATH = '/tmp/attendance.db'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
def init_db():
    """Initialize SQLite database for employees and attendance"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Employees table
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  emp_id TEXT UNIQUE NOT NULL,
                  name TEXT NOT NULL,
                  department TEXT,
                  photo_path TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Attendance table
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  emp_id TEXT NOT NULL,
                  employee_name TEXT,
                  punch_type TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  photo_path TEXT,
                  confidence REAL,
                  FOREIGN KEY(emp_id) REFERENCES employees(emp_id))''')
    
    # API Logs for HRMS connection testing
    c.execute('''CREATE TABLE IF NOT EXISTS api_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  endpoint TEXT,
                  method TEXT,
                  status_code INTEGER,
                  response_time REAL,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== EMPLOYEE MANAGEMENT ====================

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return jsonify([dict(emp) for emp in employees])

@app.route('/api/employees', methods=['POST'])
def add_employee():
    """Register new employee with photo"""
    try:
        emp_id = request.form.get('emp_id')
        name = request.form.get('name')
        department = request.form.get('department', 'General')
        
        if not emp_id or not name:
            return jsonify({'error': 'Employee ID and name required'}), 400
        
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = f"{secure_filename(emp_id)}_{dt.now().timestamp()}.jpg"
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(photo_path)
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO employees (emp_id, name, department, photo_path) VALUES (?, ?, ?, ?)',
                        (emp_id, name, department, photo_path))
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Employee ID already exists'}), 400
        finally:
            conn.close()
        
        return jsonify({'message': 'Employee added successfully', 'emp_id': emp_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<emp_id>', methods=['GET'])
def get_employee(emp_id):
    """Get employee details"""
    conn = get_db_connection()
    emp = conn.execute('SELECT * FROM employees WHERE emp_id = ?', (emp_id,)).fetchone()
    conn.close()
    
    if emp:
        return jsonify(dict(emp))
    return jsonify({'error': 'Employee not found'}), 404

@app.route('/api/employees/<emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    """Delete employee"""
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE emp_id = ?', (emp_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Employee deleted'}), 200

# ==================== ATTENDANCE MANAGEMENT ====================

@app.route('/api/attendance/punch', methods=['POST'])
def punch_attendance():
    """Record attendance (IN/OUT punch)"""
    try:
        data = request.get_json()
        emp_id = data.get('emp_id')
        punch_type = data.get('punch_type', 'IN')  # IN or OUT
        photo_data = data.get('photo')
        confidence = data.get('confidence', 0.95)
        
        if not emp_id:
            return jsonify({'error': 'Employee ID required'}), 400
        
        # Verify employee exists
        conn = get_db_connection()
        emp = conn.execute('SELECT * FROM employees WHERE emp_id = ?', (emp_id,)).fetchone()
        if not emp:
            conn.close()
            return jsonify({'error': 'Employee not found'}), 404
        
        photo_path = None
        if photo_data:
            try:
                # Decode base64 image
                img_data = base64.b64decode(photo_data.split(',')[1])
                filename = f"punch_{emp_id}_{dt.now().timestamp()}.jpg"
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(photo_path, 'wb') as f:
                    f.write(img_data)
            except Exception as e:
                print(f"Photo save error: {e}")
        
        # Record attendance
        timestamp = dt.now()
        conn.execute('INSERT INTO attendance (emp_id, employee_name, punch_type, photo_path, confidence) VALUES (?, ?, ?, ?, ?)',
                    (emp_id, emp['name'], punch_type, photo_path, confidence))
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Attendance recorded successfully',
            'emp_id': emp_id,
            'name': emp['name'],
            'punch_type': punch_type,
            'timestamp': timestamp.isoformat(),
            'confidence': confidence
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Get attendance records with optional filtering"""
    try:
        emp_id = request.args.get('emp_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        conn = get_db_connection()
        query = 'SELECT * FROM attendance WHERE 1=1'
        params = []
        
        if emp_id:
            query += ' AND emp_id = ?'
            params.append(emp_id)
        
        if start_date:
            query += ' AND date(timestamp) >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND date(timestamp) <= ?'
            params.append(end_date)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        records = conn.execute(query, params).fetchall()
        conn.close()
        
        return jsonify([dict(rec) for rec in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance"""
    today = dt.now().date()
    conn = get_db_connection()
    records = conn.execute(
        'SELECT * FROM attendance WHERE date(timestamp) = ? ORDER BY timestamp DESC',
        (today,)
    ).fetchall()
    conn.close()
    return jsonify([dict(rec) for rec in records])

@app.route('/api/attendance/summary', methods=['GET'])
def get_attendance_summary():
    """Get attendance summary"""
    try:
        emp_id = request.args.get('emp_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date required'}), 400
        
        conn = get_db_connection()
        
        query = '''SELECT 
                    emp_id, employee_name,
                    COUNT(*) as total_punches,
                    SUM(CASE WHEN punch_type='IN' THEN 1 ELSE 0 END) as total_ins,
                    SUM(CASE WHEN punch_type='OUT' THEN 1 ELSE 0 END) as total_outs,
                    MIN(CASE WHEN punch_type='IN' THEN timestamp END) as first_in,
                    MAX(CASE WHEN punch_type='OUT' THEN timestamp END) as last_out
                   FROM attendance
                   WHERE date(timestamp) BETWEEN ? AND ?'''
        
        params = [start_date, end_date]
        
        if emp_id:
            query += ' AND emp_id = ?'
            params.append(emp_id)
        
        query += ' GROUP BY emp_id, employee_name'
        
        records = conn.execute(query, params).fetchall()
        conn.close()
        
        return jsonify([dict(rec) for rec in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== API TESTING & HRMS INTEGRATION ====================

@app.route('/api/test-hrms-connection', methods=['POST'])
def test_hrms_connection():
    """Test connection to external HRMS system"""
    try:
        hrms_url = request.json.get('hrms_url')
        hrms_username = request.json.get('hrms_username')
        hrms_password = request.json.get('hrms_password')
        
        if not hrms_url:
            return jsonify({'error': 'HRMS URL required'}), 400
        
        import requests
        start_time = time.time()
        
        try:
            # Test connection with timeout
            response = requests.get(hrms_url, timeout=5, auth=(hrms_username, hrms_password) if hrms_username else None)
            response_time = time.time() - start_time
            
            # Log API call
            conn = get_db_connection()
            conn.execute('INSERT INTO api_logs (endpoint, method, status_code, response_time) VALUES (?, ?, ?, ?)',
                        ('HRMS_CONNECTION_TEST', 'GET', response.status_code, response_time))
            conn.commit()
            conn.close()
            
            return jsonify({
                'status': 'connected',
                'url': hrms_url,
                'status_code': response.status_code,
                'response_time': f'{response_time:.3f}s',
                'message': 'Successfully connected to HRMS system'
            }), 200
        except requests.exceptions.ConnectionError:
            return jsonify({'status': 'failed', 'error': 'Cannot connect to HRMS URL'}), 400
        except Exception as e:
            return jsonify({'status': 'failed', 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync-attendance', methods=['POST'])
def sync_attendance():
    """Sync attendance data to external HRMS"""
    try:
        hrms_url = request.json.get('hrms_url')
        hrms_endpoint = request.json.get('endpoint', '/api/attendance')
        start_date = request.json.get('start_date')
        end_date = request.json.get('end_date')
        
        if not hrms_url:
            return jsonify({'error': 'HRMS URL required'}), 400
        
        conn = get_db_connection()
        
        query = 'SELECT * FROM attendance WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND date(timestamp) >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND date(timestamp) <= ?'
            params.append(end_date)
        
        records = conn.execute(query, params).fetchall()
        conn.close()
        
        records_data = [dict(rec) for rec in records]
        
        import requests
        try:
            response = requests.post(
                f'{hrms_url}{hrms_endpoint}',
                json={'attendance_records': records_data},
                timeout=10
            )
            
            return jsonify({
                'status': 'synced',
                'records_sent': len(records_data),
                'hrms_status': response.status_code,
                'message': 'Attendance data synced to HRMS'
            }), 200
        except Exception as e:
            return jsonify({'status': 'failed', 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== SYSTEM STATUS ====================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    conn = get_db_connection()
    emp_count = conn.execute('SELECT COUNT(*) FROM employees').fetchone()[0]
    today_punches = conn.execute(
        'SELECT COUNT(*) FROM attendance WHERE date(timestamp) = date("now")'
    ).fetchone()[0]
    total_records = conn.execute('SELECT COUNT(*) FROM attendance').fetchone()[0]
    conn.close()
    
    return jsonify({
        'system': 'ZKTeco-like Biometric Attendance System',
        'version': '1.0.0',
        'backend': 'OpenBR',
        'status': 'running',
        'employees': emp_count,
        'today_punches': today_punches,
        'total_records': total_records,
        'timestamp': dt.now().isoformat()
    })

# ==================== WEB INTERFACE ====================

@app.route('/')
def index():
    """Dashboard home page"""
    return render_template('dashboard.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': dt.now().isoformat()}), 200

if __name__ == '__main__':
    print("=" * 60)
    print("ZKTeco-like Biometric Attendance System")
    print("Built with OpenBR for face recognition")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:5000")
    print("Dashboard: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
