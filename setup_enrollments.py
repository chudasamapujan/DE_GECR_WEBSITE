"""
Setup Student Enrollments
Automatically enrolls students in subjects based on semester and department matching
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from models.gecr_models import Student, Subject, StudentEnrollment
from app import create_app

def enroll_students_by_semester():
    """
    Automatically enroll students in subjects matching their semester and department
    """
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("AUTOMATIC STUDENT ENROLLMENT SETUP")
        print("=" * 70)
        
        # Get all subjects
        subjects = Subject.query.all()
        print(f"\nFound {len(subjects)} subjects in database")
        
        if not subjects:
            print("❌ No subjects found. Please add subjects first using add_subjects.py")
            return
        
        # Get all students
        students = Student.query.all()
        print(f"Found {len(students)} students in database\n")
        
        if not students:
            print("❌ No students found. Please add students first.")
            return
        
        enrollments_created = 0
        enrollments_skipped = 0
        
        print("Processing enrollments...")
        print("-" * 70)
        
        for subject in subjects:
            print(f"\n📚 Subject: {subject.subject_name}")
            print(f"   Semester: {subject.semester}, Department: {subject.department}")
            
            # Find students matching this subject's semester and department
            matching_students = Student.query.filter_by(
                semester=subject.semester,
                department=subject.department
            ).all()
            
            if not matching_students:
                print(f"   ⚠️  No students match this subject's criteria")
                continue
            
            print(f"   Found {len(matching_students)} matching students")
            
            for student in matching_students:
                # Check if already enrolled
                existing = StudentEnrollment.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id
                ).first()
                
                if existing:
                    if existing.status == 'active':
                        enrollments_skipped += 1
                    else:
                        # Reactivate dropped enrollment
                        existing.status = 'active'
                        existing.enrollment_date = datetime.utcnow()
                        db.session.commit()
                        enrollments_created += 1
                        print(f"   ✓ Reactivated: {student.name} ({student.roll_no})")
                else:
                    # Create new enrollment
                    enrollment = StudentEnrollment(
                        student_id=student.student_id,
                        subject_id=subject.subject_id,
                        academic_year='2024-2025',
                        status='active'
                    )
                    db.session.add(enrollment)
                    enrollments_created += 1
                    print(f"   ✓ Enrolled: {student.name} ({student.roll_no})")
        
        db.session.commit()
        
        print("\n" + "=" * 70)
        print("ENROLLMENT SUMMARY")
        print("=" * 70)
        print(f"✅ New enrollments created: {enrollments_created}")
        print(f"⏭️  Already enrolled (skipped): {enrollments_skipped}")
        print(f"📊 Total active enrollments: {StudentEnrollment.query.filter_by(status='active').count()}")
        print("=" * 70)


def show_enrollment_status():
    """
    Display current enrollment status
    """
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 70)
        print("CURRENT ENROLLMENT STATUS")
        print("=" * 70)
        
        subjects = Subject.query.all()
        
        for subject in subjects:
            enrollments = StudentEnrollment.query.filter_by(
                subject_id=subject.subject_id,
                status='active'
            ).all()
            
            print(f"\n📚 {subject.subject_name}")
            print(f"   Semester: {subject.semester}, Department: {subject.department}")
            print(f"   Enrolled Students: {len(enrollments)}")
            
            if enrollments:
                for e in enrollments[:5]:  # Show first 5
                    print(f"      - {e.student.name} ({e.student.roll_no})")
                if len(enrollments) > 5:
                    print(f"      ... and {len(enrollments) - 5} more")


def enroll_specific_students():
    """
    Manually enroll specific students (by roll number) into specific subjects
    """
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 70)
        print("MANUAL STUDENT ENROLLMENT")
        print("=" * 70)
        
        # Example: Enroll specific students in specific subjects
        # You can modify this based on your needs
        
        enrollments_to_create = [
            # Format: (roll_no, subject_name)
            ('2020001', 'Database Management Systems'),
            ('2020001', 'Software Engineering'),
            ('2020001', 'Data Structures and Algorithms'),
            ('230200143013', 'Database Management Systems'),
            ('230200143013', 'Data Structures and Algorithms'),
            ('230200143013', 'Web Technologies'),
        ]
        
        for roll_no, subject_name in enrollments_to_create:
            student = Student.query.filter_by(roll_no=roll_no).first()
            subject = Subject.query.filter_by(subject_name=subject_name).first()
            
            if not student:
                print(f"❌ Student with roll number {roll_no} not found")
                continue
            
            if not subject:
                print(f"❌ Subject '{subject_name}' not found")
                continue
            
            # Check if already enrolled
            existing = StudentEnrollment.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).first()
            
            if existing:
                if existing.status == 'active':
                    print(f"⏭️  {student.name} already enrolled in {subject_name}")
                else:
                    existing.status = 'active'
                    db.session.commit()
                    print(f"✓ Reactivated: {student.name} in {subject_name}")
            else:
                enrollment = StudentEnrollment(
                    student_id=student.student_id,
                    subject_id=subject.subject_id,
                    academic_year='2024-2025',
                    status='active'
                )
                db.session.add(enrollment)
                db.session.commit()
                print(f"✅ Enrolled: {student.name} ({roll_no}) in {subject_name}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup student enrollments')
    parser.add_argument('--auto', action='store_true', help='Automatically enroll by semester/department match')
    parser.add_argument('--manual', action='store_true', help='Manually enroll specific students')
    parser.add_argument('--status', action='store_true', help='Show current enrollment status')
    
    args = parser.parse_args()
    
    if args.auto:
        enroll_students_by_semester()
    elif args.manual:
        enroll_specific_students()
    elif args.status:
        show_enrollment_status()
    else:
        # Default: run automatic enrollment
        print("No option specified. Running automatic enrollment...")
        print("Use --auto for automatic, --manual for manual, --status to view status")
        print()
        enroll_students_by_semester()
        show_enrollment_status()
