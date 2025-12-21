"""
Script to create a test faculty account for development/testing
"""
from app import create_app
from database import db
from models.gecr_models import Faculty

def create_test_faculty():
    """Create a test faculty account"""
    app = create_app()
    with app.app_context():
        # Check if faculty already exists
        existing = Faculty.query.filter_by(email='test@gecrajkot.ac.in').first()
        if existing:
            print("Test faculty account already exists!")
            print(f"Email: test@gecrajkot.ac.in")
            print(f"Password: Test@123")
            return
        
        # Create test faculty
        faculty = Faculty(
            name='Test Faculty',
            email='test@gecrajkot.ac.in',
            department='Computer Engineering',
            designation='Assistant Professor',
            phone='1234567890'
        )
        faculty.set_password('Test@123')
        
        db.session.add(faculty)
        db.session.commit()
        
        print("✅ Test faculty account created successfully!")
        print(f"Email: test@gecrajkot.ac.in")
        print(f"Password: Test@123")
        print(f"Faculty ID: {faculty.faculty_id}")
        print(f"Department: {faculty.department}")

if __name__ == '__main__':
    create_test_faculty()
