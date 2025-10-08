#!/usr/bin/env python3

"""
Database Debug Script
Check current database users and troubleshoot login issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.gecr_models import Student, Faculty
from database import db, init_database
from flask import Flask

def check_database():
    # Initialize Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/gec_rajkot.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    init_database(app)
    
    with app.app_context():
        print("=== DATABASE DEBUG ===")
        print()
        
        # Check students
        students = Student.query.all()
        print(f"STUDENTS ({len(students)} total):")
        for s in students:
            print(f"  ID: {s.student_id}")
            print(f"  Roll: {s.roll_no}")
            print(f"  Email: {s.email}")
            print(f"  Name: {s.name}")
            print(f"  Department: {s.department}")
            print(f"  Semester: {s.semester}")
            print()
        
        # Check faculties
        faculties = Faculty.query.all()
        print(f"FACULTIES ({len(faculties)} total):")
        for f in faculties:
            print(f"  ID: {f.faculty_id}")
            print(f"  Email: {f.email}")
            print(f"  Name: {f.name}")
            print(f"  Department: {f.department}")
            print(f"  Designation: {f.designation}")
            print()
        
        # Test authentication
        print("=== AUTHENTICATION TEST ===")
        
        # Test student authentication
        if students:
            test_student = students[0]
            print(f"Testing student authentication:")
            print(f"  Email: {test_student.email}")
            print(f"  Roll: {test_student.roll_no}")
            
            # Test password check
            test_password = "password123"
            result = test_student.check_password(test_password)
            print(f"  Password check for '{test_password}': {result}")
            
            # Test email lookup
            lookup_student = Student.find_by_email(test_student.email)
            print(f"  Email lookup successful: {lookup_student is not None}")
            
            # Test roll lookup
            lookup_roll = Student.find_by_roll_no(test_student.roll_no)
            print(f"  Roll lookup successful: {lookup_roll is not None}")
            print()
        
        # Test faculty authentication
        if faculties:
            test_faculty = faculties[0]
            print(f"Testing faculty authentication:")
            print(f"  Email: {test_faculty.email}")
            
            # Test password check
            test_password = "password123"
            result = test_faculty.check_password(test_password)
            print(f"  Password check for '{test_password}': {result}")
            
            # Test email lookup
            lookup_faculty = Faculty.find_by_email(test_faculty.email)
            print(f"  Email lookup successful: {lookup_faculty is not None}")
            print()

if __name__ == '__main__':
    check_database()