# OpenBR HRMS - Biometric Attendance System

## 🎉 NEW: HRMS Biometric Attendance Module

**Test your HRMS software's biometric attendance features without purchasing hardware!**

This repository now includes a complete **HRMS Biometric Attendance System** with ZKTeco-compatible configuration for easy testing and integration.

### ✨ Key Features

- ✅ **ZKTeco-Compatible Configuration** - Same fields: API URL, Username, Password, Auth Token
- ✅ **Simulation Mode** - Works immediately without building OpenBR
- ✅ **Complete REST API** - 8 endpoints for HRMS integration
- ✅ **Python Module** - Direct integration option
- ✅ **Comprehensive Documentation** - 4 detailed guides included

### 🚀 Quick Start (5 Minutes)

```bash
# Run the example
cd hrms_attendance/examples
python3 basic_usage.py
```

This will:
- Enroll 3 sample employees
- Verify attendance with face recognition
- Generate attendance reports
- Save all data to files

### 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide
- **[hrms_attendance/README.md](hrms_attendance/README.md)** - Complete API documentation
- **[INTEGRATION_CHECKLIST.md](INTEGRATION_CHECKLIST.md)** - Step-by-step integration
- **[SUMMARY.md](SUMMARY.md)** - Full feature summary

### 🎯 Perfect For

- Testing HRMS biometric features
- Development without hardware
- Demos and prototypes
- Pre-deployment validation

### 📖 Configuration Example

```json
{
    "ZKTeco Api URL": "http://localhost:8080/api/attendance",
    "Username": "admin",
    "Password": "admin123",
    "Auth Token": "your_secure_token"
}
```

---

## Original OpenBR

**www.openbiometrics.org**

1) Identify the latest stable [release tag](https://github.com/biometrics/openbr/releases) such as "v1.1.0"

2) Download all OpenBR source code and switch to that release tag:

    $ git clone https://github.com/biometrics/openbr.git
    $ cd openbr
    $ git checkout <tag>   (eg: git checkout v1.1.0)
    $ git submodule init
    $ git submodule update
    
3) Build OpenBR by following the **[Build Instructions](http://openbiometrics.org/docs/install/)** for your OS.
