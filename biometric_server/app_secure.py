"""
ZKTeco-like Biometric Attendance System - SECURE VERSION
Built on OpenBR for face recognition with JWT Authentication
"""

import os
import json
import base64
import datetime
import sqlite3
import cv2
import numpy as np
import re
import requests
from flask import Flask, render_template, request, jsonify, send_file, redirect
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import threading
import time
from datetime import datetime as dt, timedelta
import jwt
import hashlib
import secrets

app = Flask(__name__)
CORS(app)

# ==================== REQUEST MIDDLEWARE ====================

    # Normalize incoming request paths (collapse multiple slashes, fix duplicated segments)
@app.before_request
def normalize_path():
    """Collapse duplicate slashes and common doubled segments introduced by some HRMS clients.

    If the normalized path differs from the incoming path, issue a 307 redirect so
    the original HTTP method and body are preserved (important for POST/PUT).
    
    EXCEPTION: Don't redirect doubled /api-token-auth paths - let them go directly to the handler
    so HRMS clients that don't follow POST redirects still work.
    """
    try:
        path = request.path
        
        # SKIP normalization for doubled api-token-auth paths - they have their own handler
        if '/api-token-auth//api-token-auth' in path:
            return  # Let the request through to the direct handler
        
        # Collapse multiple slashes to a single slash
        normalized = re.sub(r'/{2,}', '/', path)

        # Handle other doubled segment cases if needed
        normalized = normalized.replace('/api/v1/api-token-auth/api-token-auth', '/api/v1/api-token-auth')

        if normalized != path:
            qs = ('?' + request.query_string.decode()) if request.query_string else ''
            new_url = normalized + qs
            app.logger.debug(f"normalize_path: {path} -> {new_url}")
            return redirect(new_url, code=307)
    except Exception:
        # If anything goes wrong during normalization, don't block the request
        pass
@app.before_request
def fix_double_slashes():
    """Fix double slashes in URL paths for HRMS compatibility"""
    path = request.path
    if '//' in path:
        # Replace multiple slashes with single slash
        cleaned_path = path
        while '//' in cleaned_path:
            cleaned_path = cleaned_path.replace('//', '/')
        # Redirect to cleaned path
        return redirect(cleaned_path, code=307)

# ==================== SECURITY CONFIGURATION ====================

# Secret keys for JWT
JWT_SECRET_KEY = os.environ.get('JWT_SECRET', 'your-super-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# File Configuration
UPLOAD_FOLDER = '/tmp/biometric_uploads'
DATABASE_PATH = '/tmp/attendance.db'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize SQLite database with users table"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Users/Credentials table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  role TEXT DEFAULT 'user',
                  api_key TEXT UNIQUE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_login TIMESTAMP)''')
    
    # API Tokens table
    c.execute('''CREATE TABLE IF NOT EXISTS api_tokens
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  token TEXT UNIQUE NOT NULL,
                  token_type TEXT,
                  expires_at TIMESTAMP,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
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
    
    # API Logs table
    c.execute('''CREATE TABLE IF NOT EXISTS api_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  endpoint TEXT,
                  method TEXT,
                  status_code INTEGER,
                  response_time REAL,
                  ip_address TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    
    # Create default admin user if not exists
    try:
        c.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if not c.fetchone():
            default_password_hash = hash_password('admin123')
            api_key = generate_api_key()
            c.execute('''INSERT INTO users (username, password_hash, role, api_key)
                        VALUES (?, ?, ?, ?)''',
                     ('admin', default_password_hash, 'admin', api_key))
            conn.commit()
            print("✓ Default admin user created: username=admin, password=admin123")
            print(f"✓ Default API Key: {api_key}")
    except Exception as e:
        print(f"Admin user creation note: {e}")
    
    conn.close()

# ==================== SECURITY UTILITIES ====================

def hash_password(password):
    """Hash password using SHA256"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${password_hash.hex()}"

def verify_password(stored_hash, provided_password):
    """Verify provided password against stored hash"""
    try:
        salt, hash_hex = stored_hash.split('$')
        provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt.encode(), 100000)
        return provided_hash.hex() == hash_hex
    except Exception:
        return False

def generate_api_key():
    """Generate a secure API key"""
    return f"sk_{secrets.token_urlsafe(32)}"

def generate_jwt_token(username, role='user'):
    """Generate JWT token"""
    payload = {
        'username': username,
        'role': role,
        'iat': dt.utcnow(),
        'exp': dt.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # Store token in database
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=5, check_same_thread=False)
        c = conn.cursor()
        # Use INSERT OR REPLACE to avoid "UNIQUE constraint failed" if token already exists
        # (can happen during 307 redirects when the request is resent)
        c.execute('''INSERT OR REPLACE INTO api_tokens (username, token, token_type, expires_at)
                    VALUES (?, ?, ?, ?)''',
                 (username, token, 'jwt', payload['exp']))
        conn.commit()
        conn.close()
    except Exception as e:
        app.logger.warning(f"Failed to store token: {e}")
    
    return token

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_db_connection():
    """Get database connection"""
    # Add a timeout and allow connections from different threads to reduce "database is locked" errors
    conn = sqlite3.connect(DATABASE_PATH, timeout=5, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def log_api_call(username, endpoint, method, status_code, response_time):
    """Log API call for monitoring"""
    conn = get_db_connection()
    ip = request.remote_addr
    conn.execute('''INSERT INTO api_logs (username, endpoint, method, status_code, response_time, ip_address)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (username or 'anonymous', endpoint, method, status_code, response_time, ip))
    conn.commit()
    conn.close()

# ==================== AUTHENTICATION MIDDLEWARE ====================

def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        username = None
        
        # Check for token in header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Support both "Bearer TOKEN" and "Token TOKEN" formats
                # (Token format used by ZKTeco/HRMS)
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401
        
        # Check for API key in header
        elif 'X-API-Key' in request.headers:
            api_key = request.headers['X-API-Key']
            conn = get_db_connection()
            user = conn.execute('SELECT username, role FROM users WHERE api_key = ?', (api_key,)).fetchone()
            conn.close()
            if user:
                return f(user['username'], user['role'], *args, **kwargs)
            return jsonify({'error': 'Invalid API key'}), 401
        
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return f(payload['username'], payload['role'], *args, **kwargs)
    
    return decorated_function

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """User login - returns JWT token"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if not user or not verify_password(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = generate_jwt_token(username, user['role'])
        
        # Update last login
        conn = get_db_connection()
        conn.execute('UPDATE users SET last_login = ? WHERE username = ?', (dt.now(), username))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'token': token,
            'token_type': 'Bearer',
            'expires_in': JWT_EXPIRATION_HOURS * 3600,
            'username': username,
            'role': user['role']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _handle_token_auth():
    """Core token auth logic (shared by multiple routes)"""
    try:
        app.logger.info(f"🔐 Token auth request received from {request.remote_addr}")
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        app.logger.info(f"   Attempting login for user: {username}")
        
        if not username or not password:
            app.logger.warning(f"   ❌ Missing username or password")
            return jsonify({'error': 'Username and password required'}), 400
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if not user or not verify_password(user['password_hash'], password):
            app.logger.warning(f"   ❌ Invalid credentials for user: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        app.logger.info(f"   ✓ User authenticated: {username}")
        token = generate_jwt_token(username, user['role'])
        
        # Update last login
        conn = get_db_connection()
        conn.execute('UPDATE users SET last_login = ? WHERE username = ?', (dt.now(), username))
        conn.commit()
        conn.close()
        
        app.logger.info(f"   ✓ Token generated successfully for {username}")
        response = {
            'token': token,
            'user_id': username,
            'username': username,
            'role': user['role']
        }
        app.logger.info(f"   📤 Returning token: {token[:30]}...")
        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"   ❌ Error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/api-token-auth/', methods=['POST'])
@app.route('/api/v1/api-token-auth', methods=['POST'])
def api_token_auth():
    """HRMS-compatible token auth endpoint (alternative to /auth/login)"""
    app.logger.info(f"→ Route: /api/v1/api-token-auth")
    return _handle_token_auth()

# Direct handler for doubled paths (some HRMS clients don't follow 307 redirects on POST)
@app.route('/api/v1/api-token-auth//api-token-auth/', methods=['POST'])
@app.route('/api/v1/api-token-auth//api-token-auth', methods=['POST'])
def api_token_auth_doubled():
    """Direct handler for HRMS clients that double the path and don't follow redirects"""
    app.logger.info(f"→ Route: /api/v1/api-token-auth//api-token-auth (doubled)")
    return _handle_token_auth()

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """Register new user (admin only)"""
    try:
        # For now, registration disabled. Only admin can create users via CLI
        return jsonify({'error': 'Registration via API disabled. Contact admin.'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/auth/generate-api-key', methods=['POST'])
@require_auth
def generate_api_key_endpoint(username, role):
    """Generate new API key for user"""
    try:
        if role != 'admin':
            return jsonify({'error': 'Only admins can generate API keys'}), 403
        
        new_api_key = generate_api_key()
        conn = get_db_connection()
        conn.execute('UPDATE users SET api_key = ? WHERE username = ?', (new_api_key, username))
        conn.commit()
        conn.close()
        
        return jsonify({
            'api_key': new_api_key,
            'message': 'New API key generated successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== EMPLOYEE MANAGEMENT ====================

@app.route('/api/v1/employees', methods=['GET'])
@require_auth
def get_employees(username, role):
    """Get all employees"""
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return jsonify([dict(emp) for emp in employees])

@app.route('/api/v1/employees', methods=['POST'])
@require_auth
def add_employee(username, role):
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

@app.route('/api/v1/employees/<emp_id>', methods=['GET'])
@require_auth
def get_employee(username, role, emp_id):
    """Get employee details"""
    conn = get_db_connection()
    emp = conn.execute('SELECT * FROM employees WHERE emp_id = ?', (emp_id,)).fetchone()
    conn.close()
    
    if emp:
        return jsonify(dict(emp))
    return jsonify({'error': 'Employee not found'}), 404

@app.route('/api/v1/employees/<emp_id>', methods=['DELETE'])
@require_auth
def delete_employee(username, role, emp_id):
    """Delete employee"""
    if role != 'admin':
        return jsonify({'error': 'Only admins can delete employees'}), 403
    
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE emp_id = ?', (emp_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Employee deleted'}), 200

# ==================== ATTENDANCE MANAGEMENT ====================

@app.route('/api/v1/attendance/punch', methods=['POST'])
@require_auth
def punch_attendance(username, role):
    """Record attendance (IN/OUT punch)"""
    try:
        data = request.get_json()
        emp_id = data.get('emp_id')
        punch_type = data.get('punch_type', 'IN')
        photo_data = data.get('photo')
        confidence = data.get('confidence', 0.95)
        
        if not emp_id:
            return jsonify({'error': 'Employee ID required'}), 400
        
        conn = get_db_connection()
        emp = conn.execute('SELECT * FROM employees WHERE emp_id = ?', (emp_id,)).fetchone()
        if not emp:
            conn.close()
            return jsonify({'error': 'Employee not found'}), 404
        
        photo_path = None
        if photo_data:
            try:
                img_data = base64.b64decode(photo_data.split(',')[1])
                filename = f"punch_{emp_id}_{dt.now().timestamp()}.jpg"
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(photo_path, 'wb') as f:
                    f.write(img_data)
            except Exception as e:
                print(f"Photo save error: {e}")
        
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
            'confidence': confidence,
            'recorded_by': username
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/attendance', methods=['GET'])
@require_auth
def get_attendance(username, role):
    """Get attendance records with filtering"""
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

@app.route('/api/v1/attendance/today', methods=['GET'])
@require_auth
def get_today_attendance(username, role):
    """Get today's attendance"""
    today = dt.now().date()
    conn = get_db_connection()
    records = conn.execute(
        'SELECT * FROM attendance WHERE date(timestamp) = ? ORDER BY timestamp DESC',
        (today,)
    ).fetchall()
    conn.close()
    return jsonify([dict(rec) for rec in records])

@app.route('/api/v1/attendance/summary', methods=['GET'])
@require_auth
def get_attendance_summary(username, role):
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

# ==================== ZKTeco-Compatible TRANSACTIONS ENDPOINT ====================
# This endpoint is designed for HRMS integration with ZKTeco-compatible API format

@app.route('/iclock/api/transactions/', methods=['GET'])
@app.route('/iclock/api/transactions', methods=['GET'])
@require_auth
def get_transactions(username, role):
    """
    Get attendance transactions (ZKTeco-compatible endpoint)
    
    Query Parameters:
    - start_time: Unix timestamp (required)
    - end_time: Unix timestamp (required)
    - emp_id: Optional employee ID filter
    
    Returns:
    {
        "data": [
            {
                "employee_id": "E001",
                "check_in_time": "2024-01-20 09:00:00",
                "check_out_time": "2024-01-20 18:00:00",
                "device_id": "DEV001"
            }
        ]
    }
    """
    try:
        # Get time parameters
        start_time = request.args.get('start_time', type=int)
        end_time = request.args.get('end_time', type=int)
        emp_id = request.args.get('emp_id')
        
        if not start_time or not end_time:
            return jsonify({
                'error': 'start_time and end_time parameters required (Unix timestamps)'
            }), 400
        
        # Convert Unix timestamps to datetime strings
        from datetime import datetime as dt_class
        start_dt = dt_class.fromtimestamp(start_time)
        end_dt = dt_class.fromtimestamp(end_time)
        
        app.logger.info(f"🔍 GET /iclock/api/transactions/ - start_time={start_time} ({start_dt}), end_time={end_time} ({end_dt})")
        
        conn = get_db_connection()
        
        # Get all punch records in the time range
        if emp_id:
            records = conn.execute('''
                SELECT emp_id, employee_name, timestamp, punch_type 
                FROM attendance 
                WHERE emp_id = ? AND timestamp >= datetime(?, 'unixepoch') AND timestamp <= datetime(?, 'unixepoch')
                ORDER BY emp_id, timestamp
            ''', (emp_id, start_time, end_time)).fetchall()
        else:
            records = conn.execute('''
                SELECT emp_id, employee_name, timestamp, punch_type 
                FROM attendance 
                WHERE timestamp >= datetime(?, 'unixepoch') AND timestamp <= datetime(?, 'unixepoch')
                ORDER BY emp_id, timestamp
            ''', (start_time, end_time)).fetchall()
        
        # Format records for ZKTeco compatibility
        # Group punch IN/OUT pairs by employee
        employee_transactions = {}
        
        for rec in records:
            emp_id_val = rec['emp_id']
            emp_name = rec['employee_name']
            timestamp = rec['timestamp']
            punch_type = rec['punch_type']
            
            if emp_id_val not in employee_transactions:
                employee_transactions[emp_id_val] = {
                    'employee_id': emp_id_val,
                    'employee_name': emp_name,
                    'check_in_time': None,
                    'check_out_time': None,
                    'device_id': 'OpenBR'
                }
            
            if punch_type == 'IN':
                employee_transactions[emp_id_val]['check_in_time'] = timestamp
            elif punch_type == 'OUT':
                employee_transactions[emp_id_val]['check_out_time'] = timestamp
        
        # Convert to list format
        transactions = list(employee_transactions.values())
        
        conn.close()
        
        app.logger.info(f"✅ Returning {len(transactions)} transaction(s)")
        
        return jsonify({
            'data': transactions,
            'count': len(transactions),
            'start_time': start_time,
            'end_time': end_time
        })
        
    except Exception as e:
        app.logger.error(f"❌ Error in /iclock/api/transactions/: {str(e)}")
        return jsonify({'error': str(e), 'data': []}), 500

# ==================== SYSTEM STATUS ====================

@app.route('/api/v1/status', methods=['GET'])
@require_auth
def get_status(username, role):
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
        'version': '2.0.0',
        'backend': 'OpenBR',
        'status': 'running',
        'authenticated_as': username,
        'role': role,
        'employees': emp_count,
        'today_punches': today_punches,
        'total_records': total_records,
        'timestamp': dt.now().isoformat()
    })

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint (no auth required)"""
    return jsonify({'status': 'healthy', 'timestamp': dt.now().isoformat()}), 200

# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== ROOT & DASHBOARD ====================

@app.route('/')
def root():
    """Root endpoint - serve main dashboard home"""
    # If Accept header includes application/json, return JSON
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify({'status': 'healthy', 'message': 'OpenBR Biometric Server', 'version': '2.1.0', 'api_base': '/api/v1'})
    
    # Otherwise show home page
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login')
def login_page():
    """Login page"""
    try:
        return render_template('login.html')
    except Exception as e:
        return f"Error loading login page: {str(e)}", 500

@app.route('/dashboard')
def dashboard():
    """Dashboard page (main UI for HRMS integration)"""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/face-punch')
def face_punch_page():
    """Face punch web interface (requires authentication)"""
    try:
        return render_template('face_punch_enhanced.html')
    except Exception as e:
        return f"Error loading face punch interface: {str(e)}", 500

@app.route('/api/v1/punch-history', methods=['GET'])
@require_auth
def get_punch_history(username, role):
    """Get attendance punch history with optional filtering"""
    try:
        conn = get_db_connection()
        
        # Query parameters
        emp_id = request.args.get('emp_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        query = 'SELECT * FROM attendance WHERE 1=1'
        params = []
        
        if emp_id:
            query += ' AND emp_id = ?'
            params.append(emp_id)
        if start_date:
            query += ' AND DATE(timestamp) >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND DATE(timestamp) <= ?'
            params.append(end_date)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        records = conn.execute(query, params).fetchall()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'count': len(records),
            'data': [dict(record) for record in records]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/v1/sync/employees', methods=['POST'])
@require_auth
def sync_employees_from_hrms(username, role):
    """Sync employees FROM HRMS into OpenBR database"""
    try:
        data = request.get_json()
        hrms_url = data.get('hrms_url')
        hrms_token = data.get('hrms_token')
        
        if not hrms_url or not hrms_token:
            return jsonify({'error': 'HRMS URL and token required'}), 400
        
        try:
            # Fetch employees from HRMS
            response = requests.get(
                f"{hrms_url.rstrip('/')}/api/v1/employees",
                headers={'Authorization': f'Bearer {hrms_token}'},
                timeout=10
            )
            
            if response.status_code != 200:
                return jsonify({'error': f'Failed to fetch from HRMS: {response.status_code}'}), 400
            
            hrms_employees = response.json()
            if not isinstance(hrms_employees, list):
                hrms_employees = hrms_employees.get('data', [])
            
            conn = get_db_connection()
            synced = 0
            updated = 0
            
            for emp in hrms_employees:
                emp_id = emp.get('emp_id')
                if not emp_id:
                    continue
                
                # Check if employee exists
                existing = conn.execute('SELECT * FROM employees WHERE emp_id = ?', (emp_id,)).fetchone()
                
                if existing:
                    # Update existing employee
                    conn.execute('''
                        UPDATE employees 
                        SET name = ?, department = ?, email = ?, phone = ?
                        WHERE emp_id = ?
                    ''', (
                        emp.get('name', existing['name']),
                        emp.get('department', existing['department']),
                        emp.get('email', ''),
                        emp.get('phone', ''),
                        emp_id
                    ))
                    updated += 1
                else:
                    # Insert new employee
                    conn.execute('''
                        INSERT INTO employees (emp_id, name, department, email, phone, created_at)
                        VALUES (?, ?, ?, ?, ?, datetime('now'))
                    ''', (
                        emp_id,
                        emp.get('name', f'Employee {emp_id}'),
                        emp.get('department', 'N/A'),
                        emp.get('email', ''),
                        emp.get('phone', '')
                    ))
                    synced += 1
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'status': 'success',
                'synced': synced,
                'updated': updated,
                'total': synced + updated,
                'message': f'Synced {synced} new and updated {updated} existing employees'
            })
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Failed to connect to HRMS: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/v1/sync/hrms', methods=['POST'])
@require_auth
def sync_to_hrms(username, role):
    """Sync punches to remote HRMS system"""
    try:
        data = request.get_json()
        hrms_url = data.get('hrms_url')
        hrms_token = data.get('hrms_token')
        punch_ids = data.get('punch_ids', [])
        
        if not hrms_url or not hrms_token:
            return jsonify({'error': 'HRMS URL and token required'}), 400
        
        conn = get_db_connection()
        
        # Get punches to sync
        if punch_ids:
            placeholders = ','.join('?' * len(punch_ids))
            punches = conn.execute(
                f'SELECT * FROM attendance WHERE id IN ({placeholders})',
                punch_ids
            ).fetchall()
        else:
            # Sync all unsync'd punches from last 24 hours
            punches = conn.execute('''
                SELECT * FROM attendance 
                WHERE synced = 0 AND timestamp > datetime('now', '-1 day')
                ORDER BY timestamp DESC
            ''').fetchall()
        
        # Prepare payload
        synced_count = 0
        failed_count = 0
        errors = []
        
        for punch in punches:
            try:
                payload = {
                    'emp_id': punch['emp_id'],
                    'punch_type': punch['punch_type'],
                    'timestamp': punch['timestamp'],
                    'confidence': punch['confidence'],
                    'recorded_by': punch['recorded_by']
                }
                
                response = requests.post(
                    f"{hrms_url.rstrip('/')}/api/v1/attendance/sync",
                    json=payload,
                    headers={'Authorization': f'Bearer {hrms_token}'},
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    # Mark as synced
                    conn.execute('UPDATE attendance SET synced = 1 WHERE id = ?', (punch['id'],))
                    synced_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Punch {punch['id']}: {response.status_code}")
            except Exception as e:
                failed_count += 1
                errors.append(f"Punch {punch['id']}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'synced': synced_count,
            'failed': failed_count,
            'errors': errors[:10]  # Return first 10 errors
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/reports/daily', methods=['GET'])
@require_auth
def daily_report(username, role):
    """Generate daily attendance report"""
    try:
        date = request.args.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
        
        conn = get_db_connection()
        
        # Get daily punches grouped by employee
        report_data = conn.execute('''
            SELECT 
                a.emp_id,
                e.name,
                e.department,
                COUNT(*) as punch_count,
                GROUP_CONCAT(a.punch_type) as punch_types,
                MIN(a.timestamp) as first_punch,
                MAX(a.timestamp) as last_punch,
                AVG(a.confidence) as avg_confidence
            FROM attendance a
            LEFT JOIN employees e ON a.emp_id = e.emp_id
            WHERE DATE(a.timestamp) = ?
            GROUP BY a.emp_id
            ORDER BY a.emp_id
        ''', (date,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'date': date,
            'total_employees': len(report_data),
            'data': [dict(row) for row in report_data]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/reports/monthly', methods=['GET'])
@require_auth
def monthly_report(username, role):
    """Generate monthly attendance report"""
    try:
        year = int(request.args.get('year', datetime.datetime.now().year))
        month = int(request.args.get('month', datetime.datetime.now().month))
        
        conn = get_db_connection()
        
        # SQLite doesn't have YEAR/MONTH, use strftime instead
        month_str = f"{year}-{month:02d}"
        
        # Get monthly punches
        report_data = conn.execute('''
            SELECT 
                e.emp_id,
                e.name,
                e.department,
                COUNT(DISTINCT DATE(a.timestamp)) as days_present,
                COUNT(a.id) as total_punches,
                AVG(a.confidence) as avg_confidence
            FROM employees e
            LEFT JOIN attendance a ON e.emp_id = a.emp_id 
                AND strftime('%Y-%m', a.timestamp) = ?
            GROUP BY e.emp_id
            ORDER BY e.name
        ''', (month_str,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'period': f"{year}-{month:02d}",
            'total_employees': len(report_data),
            'data': [dict(row) for row in report_data]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/documentation')
def documentation():
    """API Documentation page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1, h2, h3 { color: #333; }
            pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            .endpoint { background: #e8f4f8; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0; }
            .method { display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; font-weight: bold; margin-right: 10px; }
            .post { background: #28a745; }
            .get { background: #007bff; }
            .delete { background: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 API Documentation</h1>
            
            <h2>1. Authentication - Login</h2>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/api/v1/auth/login</code>
                <p><strong>Get JWT Token</strong></p>
                <p>Request:</p>
                <pre>{
  "username": "admin",
  "password": "admin123"
}</pre>
                <p>Response:</p>
                <pre>{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "username": "admin",
  "role": "admin"
}</pre>
            </div>
            
            <h2>2. Attendance - Record Punch</h2>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/api/v1/attendance/punch</code>
                <p><strong>Record Face Punch (IN/OUT)</strong></p>
                <p>Headers: <code>Authorization: Bearer YOUR_TOKEN</code></p>
                <p>Request:</p>
                <pre>{
  "emp_id": "EMP001",
  "punch_type": "IN",
  "confidence": 0.95
}</pre>
                <p>Response:</p>
                <pre>{
  "message": "Attendance recorded successfully",
  "emp_id": "EMP001",
  "name": "John Doe",
  "punch_type": "IN",
  "timestamp": "2025-11-01T10:30:15",
  "confidence": 0.95
}</pre>
            </div>
            
            <h2>3. Attendance - Get Records</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/v1/attendance</code>
                <p><strong>Retrieve Attendance Records</strong></p>
                <p>Query Parameters:</p>
                <pre>?emp_id=EMP001&start_date=2025-01-01&end_date=2025-01-31&limit=100</pre>
                <p>Headers: <code>Authorization: Bearer YOUR_TOKEN</code></p>
            </div>
            
            <h2>4. Attendance - Today</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/v1/attendance/today</code>
                <p><strong>Get Today's Attendance Records</strong></p>
                <p>Headers: <code>Authorization: Bearer YOUR_TOKEN</code></p>
            </div>
            
            <h2>5. Employees - Get All</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/v1/employees</code>
                <p><strong>List All Employees</strong></p>
                <p>Headers: <code>Authorization: Bearer YOUR_TOKEN</code></p>
            </div>
            
            <h2>6. Employees - Add</h2>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/api/v1/employees</code>
                <p><strong>Register New Employee</strong></p>
                <p>Headers: <code>Authorization: Bearer YOUR_TOKEN</code></p>
                <p>Form Data:</p>
                <pre>emp_id: EMP001
name: John Doe
department: IT
photo: (binary file)</pre>
            </div>
            
            <h2>7. System - Status</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/v1/status</code>
                <p><strong>Get System Status</strong></p>
                <p>Headers: <code>Authorization: Bearer YOUR_TOKEN</code></p>
                <p>Response:</p>
                <pre>{
  "system": "ZKTeco-like Biometric Attendance System",
  "version": "2.0.0",
  "status": "running",
  "employees": 5,
  "today_punches": 12,
  "total_records": 156
}</pre>
            </div>
            
            <h2>8. System - Health Check</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/v1/health</code>
                <p><strong>Health Check (No Auth Required)</strong></p>
                <p>Response:</p>
                <pre>{"status": "healthy", "timestamp": "2025-11-01T10:30:00"}</pre>
            </div>
            
            <h2>🔑 Authentication Methods</h2>
            <h3>Method 1: JWT Bearer Token</h3>
            <p>Header: <code>Authorization: Bearer YOUR_TOKEN</code></p>
            <p>Get token from /auth/login endpoint</p>
            <p>Token expires in 24 hours</p>
            
            <h3>Method 2: API Key</h3>
            <p>Header: <code>X-API-Key: sk_JvDtmMw5HOh8w7QPen8V-YncxXqkaOhvyhdhuCUrjh8</code></p>
            <p>No expiration</p>
            
            <h2>📝 Example CURL Commands</h2>
            <h3>1. Login</h3>
            <pre>curl -X POST http://localhost:5000/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"admin","password":"admin123"}'</pre>
            
            <h3>2. Get Status</h3>
            <pre>curl http://localhost:5000/api/v1/status \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE"</pre>
            
            <h3>3. Record Punch</h3>
            <pre>curl -X POST http://localhost:5000/api/v1/attendance/punch \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -H "Content-Type: application/json" \\
  -d '{
    "emp_id": "EMP001",
    "punch_type": "IN",
    "confidence": 0.95
  }'</pre>
            
            <h3>4. Get Today's Attendance</h3>
            <pre>curl http://localhost:5000/api/v1/attendance/today \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE"</pre>
        </div>
    </body>
    </html>
    """
    return html

# ==================== STARTUP ====================

if __name__ == '__main__':
    init_db()
    
    print("=" * 70)
    print("ZKTeco-like Biometric Attendance System - SECURE VERSION")
    print("Built with OpenBR for face recognition (with JWT Authentication)")
    print("=" * 70)
    print()
    print("📋 DEFAULT CREDENTIALS (Change after first login!):")
    print("   Username: admin")
    print("   Password: admin123")
    print()
    print("🔑 API ENDPOINTS:")
    print("   Base URL: http://0.0.0.0:5000/api/v1")
    print()
    print("🔐 AUTHENTICATION METHODS:")
    print("   1. JWT Token: Authorization: Bearer <token>")
    print("   2. API Key: X-API-Key: <api_key>")
    print()
    print("📍 ACCESS:")
    print("   Local:   http://localhost:5000")
    print("   Network: http://[YOUR_IP]:5000")
    print()
    print("🌐 WEB PAGES:")
    print("   Dashboard:  http://localhost:5000/")
    print("   Docs:       http://localhost:5000/documentation")
    print()
    print("=" * 70)
    print("Starting server...")
    print("=" * 70)
    print()
    
    # Run in production mode (no reloader, debug off for stability)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
