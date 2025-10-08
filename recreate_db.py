"""
Simple script to recreate database with new GECR schema
"""

import os
from app import create_app
from database import db

def recreate_database():
    """Recreate database with new schema"""
    
    # Remove old database file
    db_path = 'instance/gec_rajkot.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed old database file")
    
    # Create app and new database
    app = create_app()
    with app.app_context():
        # Import new models
        from models.gecr_models import (
            Student, Faculty, Subject, Timetable, 
            Attendance, Assignment, Submission, 
            Message, Fee, Salary
        )
        
        # Create all tables
        db.create_all()
        print("Created new database with GECR schema")
        
        # Create test users
        test_student = Student(
            roll_no="test.student",
            name="Test Student",
            email="test.student@students.gecrajkot.ac.in",
            department="Computer Engineering",
            semester=5,
            phone="9999999999",
            fees_paid=True
        )
        test_student.set_password("password123")
        
        test_faculty = Faculty(
            name="Test Faculty",
            email="test.faculty@faculty.gecrajkot.ac.in",
            department="Computer Engineering",
            designation="Professor",
            salary=50000,
            phone="8888888888"
        )
        test_faculty.set_password("password123")
        
        db.session.add(test_student)
        db.session.add(test_faculty)
        db.session.commit()
        
        print("Created test users:")
        print("Student - Roll: test.student, Password: password123")
        print("Faculty - Email: test.faculty@faculty.gecrajkot.ac.in, Password: password123")
        
        print("Database recreation completed successfully!")

if __name__ == "__main__":
    recreate_database()