"""
Routes Package Initialization
Imports all route blueprints for GEC Rajkot Website
Author: GEC Rajkot Development Team
"""

from .auth_routes import auth_bp
from .student_routes import student_bp
from .faculty_routes import faculty_bp

__all__ = ['auth_bp', 'student_bp', 'faculty_bp']