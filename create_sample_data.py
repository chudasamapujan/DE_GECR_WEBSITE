"""
Sample Data Creation Script
Creates sample data to test the connected dashboards and pages
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.gecr_models import (
    Student, Faculty, Subject, Timetable, Attendance, 
    Assignment, Submission, Message, Fee, Salary
)
from database import db, init_database
from flask import Flask
from datetime import datetime, timedelta, date, time
import random

def create_sample_data():
    """Create comprehensive sample data for testing"""
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./instance/gec_rajkot.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        print("Creating sample data...")
        
        # Check if we already have sample data
        existing_subjects = Subject.query.count()
        if existing_subjects > 0:
            print(f"Sample data already exists ({existing_subjects} subjects found). Skipping creation.")
            return
        
        # Create sample subjects
        subjects_data = [
            {"name": "Database Management Systems", "code": "CS301", "semester": 5, "credits": 4},
            {"name": "Software Engineering", "code": "CS302", "semester": 5, "credits": 3},
            {"name": "Computer Networks", "code": "CS303", "semester": 5, "credits": 4},
            {"name": "Machine Learning", "code": "CS401", "semester": 7, "credits": 4},
            {"name": "Web Technologies", "code": "CS402", "semester": 7, "credits": 3},
            {"name": "Data Structures", "code": "CS201", "semester": 3, "credits": 4},
        ]
        
        # Get existing faculty and students
        test_faculty = Faculty.query.filter_by(email='test.faculty@faculty.gecrajkot.ac.in').first()
        pujan_faculty = Faculty.query.filter_by(email='pujanchudashama@gmail.com').first()
        
        test_student = Student.query.filter_by(roll_no='test.student').first()
        pujan_student = Student.query.filter_by(roll_no='230200143013').first()
        
        if not test_faculty or not pujan_faculty:
            print("Faculty not found. Please register faculty first.")
            return
        
        if not test_student or not pujan_student:
            print("Students not found. Please register students first.")
            return
        
        # Create subjects
        created_subjects = []
        for subject_data in subjects_data:
            # Alternate between faculty members
            faculty_id = test_faculty.faculty_id if len(created_subjects) % 2 == 0 else pujan_faculty.faculty_id
            
            subject = Subject(
                name=subject_data["name"],
                code=subject_data["code"],
                semester=subject_data["semester"],
                credits=subject_data["credits"],
                faculty_id=faculty_id
            )
            db.session.add(subject)
            created_subjects.append(subject)
        
        db.session.commit()
        print(f"Created {len(created_subjects)} subjects")
        
        # Create timetable entries
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_slots = [
            (time(9, 0), time(10, 0)),
            (time(10, 0), time(11, 0)),
            (time(11, 0), time(12, 0)),
            (time(14, 0), time(15, 0)),
            (time(15, 0), time(16, 0)),
            (time(16, 0), time(17, 0))
        ]
        
        timetable_entries = []
        for i, subject in enumerate(created_subjects):
            # Each subject gets 2-3 time slots per week
            num_slots = random.randint(2, 3)
            selected_days = random.sample(days, num_slots)
            
            for day in selected_days:
                start_time, end_time = random.choice(time_slots)
                room = f"Room {random.randint(101, 305)}"
                
                timetable = Timetable(
                    subject_id=subject.subject_id,
                    faculty_id=subject.faculty_id,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                    room=room
                )
                db.session.add(timetable)
                timetable_entries.append(timetable)
        
        db.session.commit()
        print(f"Created {len(timetable_entries)} timetable entries")
        
        # Create attendance records
        students = [test_student, pujan_student]
        attendance_records = []
        
        # Create attendance for last 30 days
        for i in range(30):
            date_obj = date.today() - timedelta(days=i)
            
            for student in students:
                # Only create attendance for subjects matching student's semester
                student_subjects = [s for s in created_subjects if s.semester == student.semester]
                
                for subject in student_subjects:
                    # 85% chance of being present
                    is_present = random.random() > 0.15
                    
                    attendance = Attendance(
                        student_id=student.student_id,
                        subject_id=subject.subject_id,
                        date=date_obj,
                        is_present=is_present
                    )
                    db.session.add(attendance)
                    attendance_records.append(attendance)
        
        db.session.commit()
        print(f"Created {len(attendance_records)} attendance records")
        
        # Create assignments
        assignments = []
        for subject in created_subjects:
            # Each subject gets 2-3 assignments
            num_assignments = random.randint(2, 3)
            
            for j in range(num_assignments):
                due_date = datetime.now() + timedelta(days=random.randint(1, 30))
                max_marks = random.choice([50, 75, 100])
                
                assignment = Assignment(
                    subject_id=subject.subject_id,
                    faculty_id=subject.faculty_id,
                    title=f"{subject.name} Assignment {j+1}",
                    description=f"Assignment on {subject.name} topics",
                    max_marks=max_marks,
                    due_date=due_date,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 10))
                )
                db.session.add(assignment)
                assignments.append(assignment)
        
        db.session.commit()
        print(f"Created {len(assignments)} assignments")
        
        # Create submissions
        submissions = []
        for student in students:
            # Get assignments for student's semester
            student_assignments = []
            for assignment in assignments:
                assignment_subject = Subject.query.get(assignment.subject_id)
                if assignment_subject.semester == student.semester:
                    student_assignments.append(assignment)
            
            # Submit 70% of assignments
            num_to_submit = int(len(student_assignments) * 0.7)
            submitted_assignments = random.sample(student_assignments, num_to_submit)
            
            for assignment in submitted_assignments:
                # Random marks between 60-95% of max marks
                marks = random.randint(int(assignment.max_marks * 0.6), int(assignment.max_marks * 0.95))
                
                submission = Submission(
                    assignment_id=assignment.assignment_id,
                    student_id=student.student_id,
                    submission_text=f"Submission for {assignment.title}",
                    submitted_at=datetime.now() - timedelta(days=random.randint(1, 5)),
                    marks=marks
                )
                db.session.add(submission)
                submissions.append(submission)
        
        db.session.commit()
        print(f"Created {len(submissions)} submissions")
        
        # Create messages/announcements
        messages = []
        message_contents = [
            ("Exam Schedule Update", "Mid-term exam schedule has been revised. Check the notice board."),
            ("Library Closure", "The central library will be closed this Saturday for maintenance."),
            ("Guest Lecture", "Dr. Sharma will deliver a guest lecture on AI trends next Friday."),
            ("Assignment Deadline", "Database assignment deadline extended by 2 days."),
            ("Workshop Announcement", "Workshop on Machine Learning basics this weekend."),
        ]
        
        for title, content in message_contents:
            message = Message(
                sender_id=test_faculty.faculty_id,
                sender_type='faculty',
                recipient_type='student',
                subject=title,
                content=content,
                sent_at=datetime.now() - timedelta(days=random.randint(1, 7))
            )
            db.session.add(message)
            messages.append(message)
        
        db.session.commit()
        print(f"Created {len(messages)} messages")
        
        # Create fee records
        for student in students:
            fee = Fee(
                student_id=student.student_id,
                semester=student.semester,
                amount=50000,  # 50k per semester
                paid=random.choice([True, False]),
                due_date=date(2024, 12, 31)
            )
            db.session.add(fee)
        
        db.session.commit()
        print("Created fee records")
        
        # Create salary records
        for faculty in [test_faculty, pujan_faculty]:
            salary = Salary(
                faculty_id=faculty.faculty_id,
                amount=75000,  # 75k per month
                month=11,  # November
                year=2024,
                paid=True
            )
            db.session.add(salary)
        
        db.session.commit()
        print("Created salary records")
        
        print("\n✅ Sample data creation completed successfully!")
        print("\nSummary:")
        print(f"- {len(created_subjects)} subjects")
        print(f"- {len(timetable_entries)} timetable entries")
        print(f"- {len(attendance_records)} attendance records")
        print(f"- {len(assignments)} assignments")
        print(f"- {len(submissions)} submissions")
        print(f"- {len(messages)} messages")
        print(f"- Fee and salary records for all users")

if __name__ == '__main__':
    create_sample_data()