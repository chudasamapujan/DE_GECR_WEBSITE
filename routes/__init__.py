"""
Routes Package Initialization
Imports route blueprints for GEC Rajkot Website
Author: GEC Rajkot Development Team
"""

from flask import Blueprint

# Import the blueprint implementations for auth, student, faculty, attendance, enrollment and subject routes
from .auth_routes import auth_bp
from .student_routes import student_bp
from .faculty_routes import faculty_bp
from .attendance_routes import attendance_bp
from .enrollment_routes import enrollment_bp
from .subject_routes import subject_bp

__all__ = ['auth_bp', 'student_bp', 'faculty_bp', 'attendance_bp', 'enrollment_bp', 'subject_bp']