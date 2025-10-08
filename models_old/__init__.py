"""
Models Package Initialization
Imports all models for GEC Rajkot Website
Author: GEC Rajkot Development Team
"""

from .student_model import Student
from .faculty_model import Faculty
from .otp_model import OTP

__all__ = ['Student', 'Faculty', 'OTP']