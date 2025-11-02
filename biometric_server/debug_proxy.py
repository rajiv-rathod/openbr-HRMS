"""
Debug Proxy Server - Captures all HRMS requests for analysis & forwards to real server
Runs on port 5001
"""

import os
import json
import sqlite3
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Forward requests to real server on port 5000
REAL_SERVER = "http://localhost:5000"

# Debug log file
DEBUG_LOG_FILE = '/workspaces/openbr/biometric_server/debug_requests.log'
DEBUG_DB = '/workspaces/openbr/biometric_server/debug_requests.db'

# ==================== DATABASE ====================

def init_debug_db():
    """Initialize debug database"""
    conn = sqlite3.connect(DEBUG_DB)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME,
                  method TEXT,
                  url TEXT,
                  path TEXT,
                  headers TEXT,
                  body TEXT,
                  ip_address TEXT,
                  user_agent TEXT,
                  response_status INTEGER,
                  response_body TEXT)''')
    
    conn.commit()
    conn.close()

def log_request(method, url, path, headers, body, ip_address, user_agent, response_status, response_body):
    """Log request to database and file"""
    timestamp = datetime.now().isoformat()
    
    # Convert headers to dict string
    headers_dict = dict(headers)
    headers_str = json.dumps(headers_dict, default=str)
    body_str = body if isinstance(body, str) else json.dumps(body, default=str)
    response_body_str = response_body if isinstance(response_body, str) else json.dumps(response_body, default=str)
    
    # Save to database
    conn = sqlite3.connect(DEBUG_DB)
    c = conn.cursor()
    c.execute('''INSERT INTO requests 
                 (timestamp, method, url, path, headers, body, ip_address, user_agent, response_status, response_body)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
             (timestamp, method, url, path, headers_str, body_str, ip_address, user_agent, response_status, response_body_str))
    conn.commit()
    conn.close()
    
    # Save to log file
    log_entry = f"""
================================================================================
[{timestamp}] {method} {path}
================================================================================
IP Address: {ip_address}
User Agent: {user_agent}

📋 HEADERS:
{json.dumps(headers_dict, indent=2, default=str)}

📝 REQUEST BODY:
{body_str if body_str else "(empty)"}

✅ RESPONSE STATUS: {response_status}

📤 RESPONSE BODY:
{response_body_str if response_body_str else "(empty)"}

"""
    
    with open(DEBUG_LOG_FILE, 'a') as f:
        f.write(log_entry)
    
    print(f"✓ Logged: {method} {path} -> {response_status}")

# ==================== ROUTES ====================

@app.route('/')
def root():
    """Root page - redirect to debug dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🐛 HRMS Debug Proxy</title>
        <style>
            body { font-family: monospace; margin: 20px; background: #1e1e1e; color: #d4d4d4; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #4ec9b0; }
            .card { background: #252526; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 3px solid #4ec9b0; }
            .status { color: #ce9178; }
            .method { color: #569cd6; font-weight: bold; }
            pre { background: #1e1e1e; border: 1px solid #3e3e42; padding: 10px; overflow-x: auto; }
            .refresh { display: inline-block; padding: 10px 20px; background: #0e639c; color: white; text-decoration: none; border-radius: 3px; }
            .refresh:hover { background: #1177bb; }
            .clear-btn { background: #d16969; }
        </style>
        <script>
            setInterval(function() {
                fetch('/debug/latest')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('requests').innerHTML = data.html;
                    });
            }, 2000);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🐛 HRMS Debug Proxy Server</h1>
            <div class="card">
                <p><strong>Status:</strong> <span class="status">🟢 RUNNING</span></p>
                <p><strong>Port:</strong> 5001</p>
                <p><strong>Debug Log:</strong> <code>debug_requests.log</code></p>
                <p><strong>Database:</strong> <code>debug_requests.db</code></p>
                <hr>
                <a class="refresh" href="/debug">View All Requests</a>
                <a class="refresh clear-btn" href="/debug/clear">Clear Logs</a>
            </div>
            
            <h2>📡 Configure Your HRMS</h2>
            <div class="card">
                <p><strong>ZKTeco Api URL:</strong></p>
                <pre>https://weary-crypt-5jrjxprjv5xhvxvq-5001.app.github.dev/api/v1/api-token-auth/</pre>
                <p><strong>Username:</strong> <code>admin</code></p>
                <p><strong>Password:</strong> <code>admin123</code></p>
                <p><em>Then click "Generate Token" and check the debug logs</em></p>
            </div>
            
            <h2>📊 Live Request Feed</h2>
            <div id="requests" class="card">
                <p>Waiting for requests...</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/debug')
def debug_dashboard():
    """Show all captured requests"""
    conn = sqlite3.connect(DEBUG_DB)
    c = conn.cursor()
    c.execute('SELECT * FROM requests ORDER BY id DESC LIMIT 50')
    requests_data = c.fetchall()
    conn.close()
    
    html = '<h2>📋 Captured Requests (Latest 50)</h2>'
    if not requests_data:
        html += '<p>No requests captured yet</p>'
    else:
        for req in requests_data:
            req_id, timestamp, method, url, path, headers, body, ip, ua, status, response = req
            try:
                headers_obj = json.loads(headers)
                body_obj = json.loads(body) if body else {}
                response_obj = json.loads(response) if response else {}
            except:
                headers_obj = {}
                body_obj = body
                response_obj = response
            
            html += f'''
            <div style="border: 1px solid #3e3e42; padding: 15px; margin: 10px 0; border-radius: 3px;">
                <p><strong>[{timestamp}]</strong> 
                <span class="method">{method}</span> 
                <code>{path}</code> 
                → <span class="status">{status}</span></p>
                <p><strong>IP:</strong> {ip} | <strong>User Agent:</strong> {ua[:60]}...</p>
                <details>
                    <summary>Headers</summary>
                    <pre>{json.dumps(headers_obj, indent=2, default=str)}</pre>
                </details>
                <details>
                    <summary>Request Body</summary>
                    <pre>{json.dumps(body_obj, indent=2, default=str) if body_obj else "(empty)"}</pre>
                </details>
                <details>
                    <summary>Response ({status})</summary>
                    <pre>{json.dumps(response_obj, indent=2, default=str) if response_obj else "(empty)"}</pre>
                </details>
            </div>
            '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Dashboard</title>
        <style>
            body {{ font-family: monospace; margin: 20px; background: #1e1e1e; color: #d4d4d4; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            h2 {{ color: #4ec9b0; }}
            details {{ margin: 10px 0; }}
            summary {{ cursor: pointer; padding: 5px; background: #252526; border-radius: 3px; }}
            pre {{ background: #1e1e1e; border: 1px solid #3e3e42; padding: 10px; overflow-x: auto; font-size: 11px; }}
            .status {{ color: #4ec9b0; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" style="color: #4ec9b0; text-decoration: none;">← Back to Home</a>
            {html}
        </div>
    </body>
    </html>
    '''

@app.route('/debug/latest')
def debug_latest():
    """API endpoint for live updates"""
    conn = sqlite3.connect(DEBUG_DB)
    c = conn.cursor()
    c.execute('SELECT * FROM requests ORDER BY id DESC LIMIT 10')
    requests_data = c.fetchall()
    conn.close()
    
    html = ''
    if not requests_data:
        html = '<p style="color: #666;">Waiting for requests...</p>'
    else:
        for req in requests_data:
            req_id, timestamp, method, url, path, headers, body, ip, ua, status, response = req
            try:
                body_obj = json.loads(body) if body else {}
                username = body_obj.get('username', '?')
            except:
                username = '?'
            
            status_color = '#4ec9b0' if status == 200 else '#ce9178'
            html += f'<p><strong>[{timestamp}]</strong> <span style="color: #569cd6;">{method}</span> {path} → <span style="color: {status_color};">{status}</span> (user: {username}, ip: {ip})</p>'
    
    return jsonify({'html': html})

@app.route('/debug/clear', methods=['GET', 'POST'])
def debug_clear():
    """Clear debug logs"""
    if os.path.exists(DEBUG_LOG_FILE):
        os.remove(DEBUG_LOG_FILE)
    
    conn = sqlite3.connect(DEBUG_DB)
    c = conn.cursor()
    c.execute('DELETE FROM requests')
    conn.commit()
    conn.close()
    
    return '''
    <html>
    <body style="font-family: monospace; margin: 20px;">
        <h2>✓ Debug logs cleared!</h2>
        <a href="/debug">Back to Debug Dashboard</a>
    </body>
    </html>
    '''

# ==================== CAPTURE ALL REQUESTS ====================

@app.route('/api/v1/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def capture_api_request(subpath):
    """Capture all API requests"""
    
    # Parse request
    method = request.method
    url = request.url
    path = request.path
    headers = request.headers
    ip_address = request.remote_addr
    user_agent = request.user_agent.string if request.user_agent else 'Unknown'
    
    # Get body
    try:
        if request.is_json:
            body = request.get_json()
        else:
            body = request.get_data(as_text=True)
    except:
        body = ''
    
    # Generate response
    response_body = {
        'status': 'captured',
        'message': 'Request captured by debug proxy',
        'request_id': datetime.now().timestamp(),
        'method': method,
        'path': path,
        'body_received': body,
        'headers_received': dict(headers)
    }
    
    response_status = 200
    
    # Log the request
    log_request(method, url, path, headers, body, ip_address, user_agent, response_status, response_body)
    
    return jsonify(response_body), response_status

# ==================== STARTUP ====================

if __name__ == '__main__':
    init_debug_db()
    
    print("=" * 70)
    print("🐛 HRMS DEBUG PROXY SERVER")
    print("=" * 70)
    print()
    print("📍 Running on: http://127.0.0.1:5001")
    print()
    print("🔗 Configure your HRMS to use:")
    print("   URL: https://weary-crypt-5jrjxprjv5xhvxvq-5001.app.github.dev/api/v1/api-token-auth/")
    print()
    print("📊 Dashboard: http://127.0.0.1:5001/debug")
    print()
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=False)
