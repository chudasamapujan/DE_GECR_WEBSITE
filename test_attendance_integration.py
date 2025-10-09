"""
Integration test for attendance upload feature
Checks database setup and creates sample data for testing
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_setup():
    """
    Check if database has required tables and sample data
    """
    from database import db
    from models.gecr_models import Student, Subject, Faculty, Attendance
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Database Setup Check")
        print("=" * 60)
        
        # Check tables exist
        print("\n✓ Checking tables...")
        
        try:
            student_count = Student.query.count()
            print(f"  - Students table: {student_count} records")
            
            faculty_count = Faculty.query.count()
            print(f"  - Faculty table: {faculty_count} records")
            
            subject_count = Subject.query.count()
            print(f"  - Subjects table: {subject_count} records")
            
            attendance_count = Attendance.query.count()
            print(f"  - Attendance table: {attendance_count} records")
            
        except Exception as e:
            print(f"  ❌ Error checking tables: {e}")
            return False
        
        # Check if we have students with roll numbers
        print("\n✓ Checking student data...")
        students = Student.query.limit(5).all()
        
        if not students:
            print("  ⚠️ No students found in database!")
            print("  Creating sample students...")
            create_sample_data()
        else:
            print(f"  - Found {len(students)} students (showing first 5):")
            for s in students:
                print(f"    • Roll: {s.roll_no}, Name: {s.name}, Email: {s.email}")
        
        # Check subjects
        print("\n✓ Checking subject data...")
        subjects = Subject.query.limit(5).all()
        
        if subjects:
            print(f"  - Found {len(subjects)} subjects:")
            for subj in subjects:
                print(f"    • ID: {subj.subject_id}, Name: {subj.name}, Code: {subj.code}")
        else:
            print("  ⚠️ No subjects found!")
        
        return True

def create_sample_data():
    """
    Create sample students, faculty, and subjects for testing
    """
    from database import db
    from models.gecr_models import Student, Subject, Faculty
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("Creating Sample Data")
        print("=" * 60)
        
        try:
            # Create subjects
            print("\n✓ Creating subjects...")
            subjects = [
                Subject(code='CS101', name='Database Management Systems', credits=4, semester=5),
                Subject(code='CS102', name='Software Engineering', credits=4, semester=5),
                Subject(code='CS103', name='Data Structures', credits=4, semester=3),
            ]
            
            for subj in subjects:
                existing = Subject.query.filter_by(code=subj.code).first()
                if not existing:
                    db.session.add(subj)
                    print(f"  + Created subject: {subj.code} - {subj.name}")
            
            db.session.commit()
            
            # Create students
            print("\n✓ Creating students...")
            students = [
                Student(
                    roll_no='2020001',
                    name='Aarav Patel',
                    email='aarav.patel@student.gecr.edu',
                    password='hashed_password_1',
                    enrollment_no='220001',
                    semester=5,
                    branch='Computer Engineering'
                ),
                Student(
                    roll_no='2020002',
                    name='Diya Shah',
                    email='diya.shah@student.gecr.edu',
                    password='hashed_password_2',
                    enrollment_no='220002',
                    semester=5,
                    branch='Computer Engineering'
                ),
                Student(
                    roll_no='2020003',
                    name='Arjun Mehta',
                    email='arjun.mehta@student.gecr.edu',
                    password='hashed_password_3',
                    enrollment_no='220003',
                    semester=5,
                    branch='Computer Engineering'
                ),
                Student(
                    roll_no='2020004',
                    name='Ananya Desai',
                    email='ananya.desai@student.gecr.edu',
                    password='hashed_password_4',
                    enrollment_no='220004',
                    semester=5,
                    branch='Computer Engineering'
                ),
                Student(
                    roll_no='2020005',
                    name='Vihaan Kumar',
                    email='vihaan.kumar@student.gecr.edu',
                    password='hashed_password_5',
                    enrollment_no='220005',
                    semester=5,
                    branch='Computer Engineering'
                ),
            ]
            
            for student in students:
                existing = Student.query.filter_by(roll_no=student.roll_no).first()
                if not existing:
                    db.session.add(student)
                    print(f"  + Created student: {student.roll_no} - {student.name}")
            
            db.session.commit()
            
            # Create faculty
            print("\n✓ Creating faculty...")
            faculty = Faculty(
                name='Dr. Rajesh Kumar',
                email='rajesh.kumar@gecr.edu',
                department='Computer Engineering',
                designation='Professor',
                password='hashed_password_faculty'
            )
            
            existing_faculty = Faculty.query.filter_by(email=faculty.email).first()
            if not existing_faculty:
                db.session.add(faculty)
                db.session.commit()
                print(f"  + Created faculty: {faculty.name} ({faculty.email})")
            
            print("\n✅ Sample data created successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating sample data: {e}")
            import traceback
            traceback.print_exc()

def test_attendance_model():
    """
    Test creating attendance records directly
    """
    from database import db
    from models.gecr_models import Student, Subject, Attendance
    from app import create_app
    from datetime import date
    
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("Testing Attendance Model")
        print("=" * 60)
        
        # Get first student and subject
        student = Student.query.first()
        subject = Subject.query.first()
        
        if not student or not subject:
            print("❌ Need students and subjects to test!")
            return
        
        print(f"\n✓ Using student: {student.name} (Roll: {student.roll_no})")
        print(f"✓ Using subject: {subject.name} (Code: {subject.code})")
        
        # Create test attendance
        test_date = date.today()
        
        # Check if attendance already exists
        existing = Attendance.query.filter_by(
            student_id=student.student_id,
            subject_id=subject.subject_id,
            date=test_date
        ).first()
        
        if existing:
            print(f"\n✓ Attendance already exists for today: {existing.status}")
            print(f"  Updating to 'Present'...")
            existing.status = 'Present'
        else:
            attendance = Attendance(
                student_id=student.student_id,
                subject_id=subject.subject_id,
                date=test_date,
                status='Present'
            )
            db.session.add(attendance)
            print(f"\n✓ Creating new attendance record...")
        
        try:
            db.session.commit()
            print(f"✅ Attendance saved successfully!")
            
            # Verify
            saved = Attendance.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id,
                date=test_date
            ).first()
            
            if saved:
                print(f"\n✓ Verification:")
                print(f"  - Student: {saved.student.name}")
                print(f"  - Subject: {saved.subject.name}")
                print(f"  - Date: {saved.date}")
                print(f"  - Status: {saved.status}")
        
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving attendance: {e}")

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("ATTENDANCE UPLOAD - DATABASE INTEGRATION TEST")
    print("=" * 60)
    
    # Check database setup
    check_database_setup()
    
    # Test attendance model
    test_attendance_model()
    
    print("\n" + "=" * 60)
    print("✅ Integration test completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start Flask app: python app.py")
    print("2. Login as faculty: rajesh.kumar@gecr.edu")
    print("3. Go to /faculty/attendance page")
    print("4. Upload sample Excel file with roll numbers: 2020001-2020005")
    print("=" * 60)
