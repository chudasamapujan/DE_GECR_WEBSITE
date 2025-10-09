"""
Create test users with known passwords for testing
"""

from models.gecr_models import Faculty, Student
from database import db
from app import create_app

app = create_app()

with app.app_context():
    # Check if test faculty exists
    faculty = Faculty.query.filter_by(email='test.faculty@gecr.edu').first()
    if not faculty:
        faculty = Faculty(
            name='Test Faculty',
            email='test.faculty@gecr.edu',
            phone='1234567890',
            department='Computer Engineering',
            designation='Assistant Professor'
        )
        faculty.set_password('faculty123')  # Set password
        db.session.add(faculty)
        print("✅ Created test faculty: test.faculty@gecr.edu / faculty123")
    else:
        # Update password
        faculty.set_password('faculty123')
        print("✅ Updated test faculty password: test.faculty@gecr.edu / faculty123")
    
    # Check if test student exists
    student = Student.query.filter_by(roll_no='TEST001').first()
    if not student:
        student = Student(
            roll_no='TEST001',
            name='Test Student',
            email='test.student@gecr.edu',
            department='Computer Engineering',
            semester=5,
            phone='0987654321'
        )
        student.set_password('student123')  # Set password
        db.session.add(student)
        print("✅ Created test student: TEST001 / student123")
    else:
        # Update password
        student.set_password('student123')
        print("✅ Updated test student password: TEST001 / student123")
    
    db.session.commit()
    
    print("\n" + "="*60)
    print("Test users ready!")
    print("="*60)
    print("\nFaculty Login:")
    print("  Email: test.faculty@gecr.edu")
    print("  Password: faculty123")
    print("\nStudent Login:")
    print("  Roll No: TEST001")
    print("  Email: test.student@gecr.edu")
    print("  Password: student123")
    print("="*60)
    
    # Verify passwords work
    print("\nVerifying passwords...")
    print(f"Faculty password check: {faculty.check_password('faculty123')}")
    print(f"Student password check: {student.check_password('student123')}")
