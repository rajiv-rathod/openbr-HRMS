"""
HRMS Biometric Attendance Module
Using OpenBR for face recognition-based employee attendance tracking
Compatible with ZKTeco-like configuration
"""

__version__ = "1.0.0"
__author__ = "HRMS Development Team"

from .core.attendance import AttendanceManager
from .config.settings import AttendanceConfig

__all__ = ['AttendanceManager', 'AttendanceConfig']
