"""
Routes Package Initialization
Imports all route blueprints for GEC Rajkot Website
Author: GEC Rajkot Development Team
"""

# Temporarily disabled during GECR migration
# from .auth_routes import auth_bp
# from .student_routes import student_bp
# from .faculty_routes import faculty_bp

# Create empty blueprints for now
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
student_bp = Blueprint('student', __name__)
faculty_bp = Blueprint('faculty', __name__)

__all__ = ['auth_bp', 'student_bp', 'faculty_bp']