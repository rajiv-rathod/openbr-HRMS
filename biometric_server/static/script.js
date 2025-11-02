// ==================== Global Variables ====================
let currentPhotoData = null;
let stream = null;

// ==================== Section Navigation ====================
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Deactivate all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected section
    document.getElementById(sectionId).classList.add('active');

    // Activate corresponding nav button
    event.target.classList.add('active');

    // Load data for each section
    if (sectionId === 'dashboard') {
        loadDashboard();
    } else if (sectionId === 'employees') {
        loadEmployees();
    } else if (sectionId === 'attendance') {
        loadAttendance();
    } else if (sectionId === 'test') {
        loadTestEmployees();
    }
}

// ==================== Dashboard ====================
function loadDashboard() {
    fetch('/api/status')
        .then(r => r.json())
        .then(data => {
            document.getElementById('stat-employees').textContent = data.employees;
            document.getElementById('stat-today').textContent = data.today_punches;
            document.getElementById('stat-records').textContent = data.total_records;
            document.getElementById('stat-status').textContent = data.status;

            const systemInfo = `
                <p><strong>System:</strong> ${data.system}</p>
                <p><strong>Version:</strong> ${data.version}</p>
                <p><strong>Backend:</strong> ${data.backend}</p>
                <p><strong>Status:</strong> <span style="color: #48bb78;">● ${data.status}</span></p>
                <p><strong>Last Updated:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
            `;
            document.getElementById('system-info').innerHTML = systemInfo;
        });

    loadTodayAttendance();
}

function loadTodayAttendance() {
    fetch('/api/attendance/today')
        .then(r => r.json())
        .then(data => {
            let html = '';
            if (data.length === 0) {
                html = '<p class="loading">No attendance records for today</p>';
            } else {
                data.forEach(record => {
                    const timestamp = new Date(record.timestamp).toLocaleString();
                    const badge = `<span class="badge badge-${record.punch_type === 'IN' ? 'in' : 'out'}">${record.punch_type}</span>`;
                    html += `
                        <div class="attendance-item">
                            <div class="attendance-info">
                                <h4>${record.employee_name}</h4>
                                <p>${record.emp_id} • ${timestamp}</p>
                            </div>
                            <div>${badge}</div>
                        </div>
                    `;
                });
            }
            document.getElementById('today-attendance').innerHTML = html;
        });
}

// ==================== Employee Management ====================
function showEmployeeForm() {
    document.getElementById('employee-form-container').style.display = 'block';
}

function hideEmployeeForm() {
    document.getElementById('employee-form-container').style.display = 'none';
    document.getElementById('employee-form').reset();
}

function loadEmployees() {
    fetch('/api/employees')
        .then(r => r.json())
        .then(data => {
            let html = '<table><thead><tr><th>Employee ID</th><th>Name</th><th>Department</th><th>Actions</th></tr></thead><tbody>';
            if (data.length === 0) {
                html = '<p class="loading">No employees registered yet</p>';
            } else {
                data.forEach(emp => {
                    html += `
                        <tr>
                            <td>${emp.emp_id}</td>
                            <td>${emp.name}</td>
                            <td>${emp.department || 'N/A'}</td>
                            <td class="action-buttons">
                                <button class="btn btn-danger" onclick="deleteEmployee('${emp.emp_id}')">Delete</button>
                            </td>
                        </tr>
                    `;
                });
                html += '</tbody></table>';
            }
            document.getElementById('employees-list').innerHTML = html;
        });
}

function addEmployee(event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append('emp_id', document.getElementById('emp-id').value);
    formData.append('name', document.getElementById('emp-name').value);
    formData.append('department', document.getElementById('emp-dept').value);

    const photoFile = document.getElementById('emp-photo').files[0];
    if (photoFile) {
        formData.append('photo', photoFile);
    }

    fetch('/api/employees', {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Employee registered successfully!');
            document.getElementById('employee-form').reset();
            hideEmployeeForm();
            loadEmployees();
            loadTestEmployees();
        }
    })
    .catch(e => alert('Error: ' + e));
}

function deleteEmployee(empId) {
    if (confirm('Delete this employee?')) {
        fetch(`/api/employees/${empId}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(() => {
                alert('Employee deleted');
                loadEmployees();
                loadTestEmployees();
            });
    }
}

// ==================== Attendance Management ====================
function loadAttendance() {
    fetch('/api/attendance?limit=50')
        .then(r => r.json())
        .then(data => {
            let html = '<table><thead><tr><th>Employee</th><th>Punch Type</th><th>Timestamp</th><th>Confidence</th></tr></thead><tbody>';
            if (data.length === 0) {
                html = '<p class="loading">No attendance records</p>';
            } else {
                data.forEach(record => {
                    const badge = `<span class="badge badge-${record.punch_type === 'IN' ? 'in' : 'out'}">${record.punch_type}</span>`;
                    const timestamp = new Date(record.timestamp).toLocaleString();
                    const confidence = (record.confidence * 100).toFixed(1);
                    html += `
                        <tr>
                            <td>${record.employee_name}<br/><small>${record.emp_id}</small></td>
                            <td>${badge}</td>
                            <td>${timestamp}</td>
                            <td>${confidence}%</td>
                        </tr>
                    `;
                });
                html += '</tbody></table>';
            }
            document.getElementById('attendance-list').innerHTML = html;
        });
}

function filterAttendance() {
    const empId = document.getElementById('filter-emp-id').value;
    const startDate = document.getElementById('filter-start').value;
    const endDate = document.getElementById('filter-end').value;

    let url = '/api/attendance?limit=1000';
    if (empId) url += `&emp_id=${empId}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;

    fetch(url)
        .then(r => r.json())
        .then(data => {
            let html = '<table><thead><tr><th>Employee</th><th>Punch Type</th><th>Timestamp</th><th>Confidence</th></tr></thead><tbody>';
            if (data.length === 0) {
                html = '<p class="loading">No records found</p>';
            } else {
                data.forEach(record => {
                    const badge = `<span class="badge badge-${record.punch_type === 'IN' ? 'in' : 'out'}">${record.punch_type}</span>`;
                    const timestamp = new Date(record.timestamp).toLocaleString();
                    const confidence = (record.confidence * 100).toFixed(1);
                    html += `
                        <tr>
                            <td>${record.employee_name}<br/><small>${record.emp_id}</small></td>
                            <td>${badge}</td>
                            <td>${timestamp}</td>
                            <td>${confidence}%</td>
                        </tr>
                    `;
                });
                html += '</tbody></table>';
            }
            document.getElementById('attendance-list').innerHTML = html;
        });
}

function generateSummary() {
    const startDate = document.getElementById('summary-start').value;
    const endDate = document.getElementById('summary-end').value;

    if (!startDate || !endDate) {
        alert('Please select both start and end dates');
        return;
    }

    let url = `/api/attendance/summary?start_date=${startDate}&end_date=${endDate}`;

    fetch(url)
        .then(r => r.json())
        .then(data => {
            let html = '<table><thead><tr><th>Employee</th><th>Total Punches</th><th>IN</th><th>OUT</th><th>First IN</th><th>Last OUT</th></tr></thead><tbody>';
            if (data.length === 0) {
                html = '<p class="loading">No data for selected period</p>';
            } else {
                data.forEach(record => {
                    const firstIn = record.first_in ? new Date(record.first_in).toLocaleTimeString() : '-';
                    const lastOut = record.last_out ? new Date(record.last_out).toLocaleTimeString() : '-';
                    html += `
                        <tr>
                            <td>${record.employee_name}<br/><small>${record.emp_id}</small></td>
                            <td>${record.total_punches}</td>
                            <td>${record.total_ins}</td>
                            <td>${record.total_outs}</td>
                            <td>${firstIn}</td>
                            <td>${lastOut}</td>
                        </tr>
                    `;
                });
                html += '</tbody></table>';
            }
            document.getElementById('summary-results').innerHTML = html;
        });
}

function exportAttendanceCSV() {
    const empId = document.getElementById('filter-emp-id').value;
    const startDate = document.getElementById('filter-start').value;
    const endDate = document.getElementById('filter-end').value;

    let url = '/api/attendance?limit=10000';
    if (empId) url += `&emp_id=${empId}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;

    fetch(url)
        .then(r => r.json())
        .then(data => {
            let csv = 'Employee ID,Name,Punch Type,Timestamp,Confidence\n';
            data.forEach(record => {
                csv += `${record.emp_id},${record.employee_name},${record.punch_type},${record.timestamp},${(record.confidence * 100).toFixed(1)}%\n`;
            });

            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `attendance_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
        });
}

// ==================== HRMS Integration ====================
function testHRMSConnection(event) {
    event.preventDefault();

    const url = document.getElementById('hrms-url').value;
    const username = document.getElementById('hrms-username').value;
    const password = document.getElementById('hrms-password').value;

    const resultDiv = document.getElementById('hrms-test-result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<p class="loading">Testing connection...</p>';

    fetch('/api/test-hrms-connection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            hrms_url: url,
            hrms_username: username,
            hrms_password: password
        })
    })
    .then(r => r.json())
    .then(data => {
        let html = `<h4>Connection Result</h4>`;
        if (data.status === 'connected') {
            html += `
                <div class="result-box success">
                    <h4>✓ Connected Successfully</h4>
                    <p><strong>URL:</strong> ${data.url}</p>
                    <p><strong>Status Code:</strong> ${data.status_code}</p>
                    <p><strong>Response Time:</strong> ${data.response_time}</p>
                    <p><strong>Message:</strong> ${data.message}</p>
                </div>
            `;
        } else {
            html += `
                <div class="result-box error">
                    <h4>✗ Connection Failed</h4>
                    <p><strong>Error:</strong> ${data.error}</p>
                </div>
            `;
        }
        resultDiv.innerHTML = html;
    })
    .catch(e => {
        resultDiv.innerHTML = `<div class="result-box error"><h4>Error</h4><p>${e}</p></div>`;
    });
}

function generateAuthToken() {
    const token = {
        type: 'Bearer',
        token: 'zekteco_' + Math.random().toString(36).substr(2) + '_' + Date.now(),
        expires: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        scopes: ['attendance.read', 'attendance.write', 'employees.read', 'employees.write']
    };

    const resultDiv = document.getElementById('token-result');
    resultDiv.style.display = 'block';
    document.getElementById('token-display').value = JSON.stringify(token, null, 2);
}

function copyToken() {
    const textarea = document.getElementById('token-display');
    textarea.select();
    document.execCommand('copy');
    alert('Token copied to clipboard!');
}

function syncAttendanceToHRMS() {
    const hrmsUrl = document.getElementById('hrms-url').value;
    const startDate = document.getElementById('sync-start').value;
    const endDate = document.getElementById('sync-end').value;

    if (!hrmsUrl || !startDate || !endDate) {
        alert('Please fill all fields');
        return;
    }

    const resultDiv = document.getElementById('sync-result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<p class="loading">Syncing attendance...</p>';

    fetch('/api/sync-attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            hrms_url: hrmsUrl,
            endpoint: '/api/attendance',
            start_date: startDate,
            end_date: endDate
        })
    })
    .then(r => r.json())
    .then(data => {
        let html = '';
        if (data.status === 'synced') {
            html += `
                <div class="result-box success">
                    <h4>✓ Sync Successful</h4>
                    <p><strong>Records Sent:</strong> ${data.records_sent}</p>
                    <p><strong>HRMS Status:</strong> ${data.hrms_status}</p>
                    <p><strong>Message:</strong> ${data.message}</p>
                </div>
            `;
        } else {
            html += `
                <div class="result-box error">
                    <h4>✗ Sync Failed</h4>
                    <p><strong>Error:</strong> ${data.error}</p>
                </div>
            `;
        }
        resultDiv.innerHTML = html;
    })
    .catch(e => {
        resultDiv.innerHTML = `<div class="result-box error"><h4>Error</h4><p>${e}</p></div>`;
    });
}

// ==================== Camera & Face Punch ====================
function startCamera() {
    const video = document.getElementById('camera');
    const constraints = {
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
    };

    navigator.mediaDevices.getUserMedia(constraints)
        .then(s => {
            stream = s;
            video.srcObject = stream;
            video.play();
        })
        .catch(err => {
            alert('Cannot access camera: ' + err.message);
        });
}

function capturePhoto() {
    const video = document.getElementById('camera');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    if (!stream) {
        alert('Please start camera first');
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    currentPhotoData = canvas.toDataURL('image/jpeg');

    const preview = document.getElementById('image-preview');
    preview.innerHTML = `<img src="${currentPhotoData}" alt="Captured photo">`;
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
        document.getElementById('camera').srcObject = null;
    }
}

function loadTestEmployees() {
    fetch('/api/employees')
        .then(r => r.json())
        .then(data => {
            let options = '<option value="">Select an employee...</option>';
            data.forEach(emp => {
                options += `<option value="${emp.emp_id}">${emp.name} (${emp.emp_id})</option>`;
            });
            document.getElementById('punch-emp-id').innerHTML = options;
        });
}

function submitPunch() {
    const empId = document.getElementById('punch-emp-id').value;
    const punchType = document.getElementById('punch-type').value;
    const confidence = parseFloat(document.getElementById('confidence-level').value);

    if (!empId) {
        alert('Please select an employee');
        return;
    }

    if (!currentPhotoData) {
        alert('Please capture a photo first');
        return;
    }

    const resultDiv = document.getElementById('punch-result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<p class="loading">Processing punch...</p>';

    fetch('/api/attendance/punch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            emp_id: empId,
            punch_type: punchType,
            photo: currentPhotoData,
            confidence: confidence
        })
    })
    .then(r => r.json())
    .then(data => {
        let html = '';
        if (!data.error) {
            html += `
                <div class="result-box success">
                    <h4>✓ Punch Recorded Successfully</h4>
                    <p><strong>Employee:</strong> ${data.name}</p>
                    <p><strong>Employee ID:</strong> ${data.emp_id}</p>
                    <p><strong>Punch Type:</strong> <span class="badge badge-${data.punch_type === 'IN' ? 'in' : 'out'}">${data.punch_type}</span></p>
                    <p><strong>Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                    <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                </div>
            `;
        } else {
            html += `
                <div class="result-box error">
                    <h4>✗ Error</h4>
                    <p>${data.error}</p>
                </div>
            `;
        }
        resultDiv.innerHTML = html;
        loadDashboard();
        loadAttendance();
    })
    .catch(e => {
        resultDiv.innerHTML = `<div class="result-box error"><h4>Error</h4><p>${e}</p></div>`;
    });
}

// Update confidence display
document.addEventListener('DOMContentLoaded', function() {
    const confidenceSlider = document.getElementById('confidence-level');
    if (confidenceSlider) {
        confidenceSlider.addEventListener('input', function() {
            document.getElementById('confidence-display').textContent = this.value;
        });
    }
});
