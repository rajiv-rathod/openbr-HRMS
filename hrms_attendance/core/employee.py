"""
Employee data model for attendance system
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
import json


@dataclass
class Employee:
    """
    Employee data model.
    
    Attributes:
        employee_id: Unique employee identifier
        name: Employee full name
        department: Department name
        designation: Job designation/title
        face_template_path: Path to enrolled face template
        email: Employee email address
        phone: Employee phone number
        enrolled_date: Date when biometric was enrolled
        is_active: Whether the employee is active
    """
    
    employee_id: str
    name: str
    department: str = ""
    designation: str = ""
    face_template_path: str = ""
    email: str = ""
    phone: str = ""
    enrolled_date: str = ""
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize default values"""
        if not self.enrolled_date:
            self.enrolled_date = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert employee to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Employee':
        """Create employee from dictionary"""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert employee to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Employee':
        """Create employee from JSON string"""
        return cls.from_dict(json.loads(json_str))
