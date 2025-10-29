"""
Attendance Configuration Module
Manages ZKTeco-compatible settings for biometric attendance system
"""

import json
import os
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class AttendanceConfig:
    """
    Configuration class for biometric attendance system.
    Compatible with ZKTeco API configuration format.
    
    Attributes:
        api_url: ZKTeco API URL endpoint
        username: API authentication username
        password: API authentication password
        auth_token: Authentication token for API access
        openbr_sdk_path: Path to OpenBR SDK (default: /usr/local/lib)
        face_recognition_threshold: Similarity threshold for face matching (0.0 - 1.0)
        employee_db_path: Path to employee face database
        attendance_log_path: Path to store attendance logs
    """
    
    api_url: str = "http://localhost:8080/api/attendance"
    username: str = "admin"
    password: str = "admin123"
    auth_token: str = ""
    openbr_sdk_path: str = "/usr/local/lib"
    face_recognition_threshold: float = 0.7
    employee_db_path: str = "./data/employees"
    attendance_log_path: str = "./logs/attendance.json"
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AttendanceConfig':
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to configuration JSON file
            
        Returns:
            AttendanceConfig instance
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config_path: Path where to save the configuration
        """
        os.makedirs(os.path.dirname(config_path) or '.', exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(asdict(self), f, indent=4)
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    def validate(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.api_url:
            raise ValueError("API URL is required")
        
        if not self.username:
            raise ValueError("Username is required")
        
        if not (0.0 <= self.face_recognition_threshold <= 1.0):
            raise ValueError("Face recognition threshold must be between 0.0 and 1.0")
        
        return True
    
    def get_zkteco_format(self) -> dict:
        """
        Get configuration in ZKTeco compatible format.
        
        Returns:
            Dictionary with ZKTeco-compatible fields
        """
        return {
            "ZKTeco Api URL": self.api_url,
            "Username": self.username,
            "Password": self.password,
            "Auth Token": self.auth_token
        }
    
    def display_config(self) -> str:
        """
        Display configuration in a readable format.
        
        Returns:
            Formatted configuration string
        """
        zk_format = self.get_zkteco_format()
        output = ["=" * 50]
        output.append("Biometric Attendance Configuration")
        output.append("=" * 50)
        output.append("\nZKTeco API Settings:")
        output.append(f"  ZKTeco Api URL: {zk_format['ZKTeco Api URL']}")
        output.append(f"  Username: {zk_format['Username']}")
        output.append(f"  Password: {'*' * len(zk_format['Password'])}")
        output.append(f"  Auth Token: {zk_format['Auth Token'][:20] + '...' if len(zk_format['Auth Token']) > 20 else zk_format['Auth Token']}")
        output.append("\nOpenBR Settings:")
        output.append(f"  SDK Path: {self.openbr_sdk_path}")
        output.append(f"  Recognition Threshold: {self.face_recognition_threshold}")
        output.append(f"  Employee DB: {self.employee_db_path}")
        output.append(f"  Attendance Log: {self.attendance_log_path}")
        output.append("=" * 50)
        
        return "\n".join(output)
