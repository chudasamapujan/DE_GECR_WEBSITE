"""
Simple Sample Data Creation using direct SQL
Creates sample data to test the connected dashboards
"""

import sqlite3
import random
from datetime import datetime, timedelta, date

def create_sample_data_sql():
    """Create sample data using direct SQL"""
    
    # Connect to the existing database
    conn = sqlite3.connect('instance/gec_rajkot.db')
    cursor = conn.cursor()
    
    print("Creating sample data using direct SQL...")
    
    # Check if sample data already exists
    cursor.execute("SELECT COUNT(*) FROM subjects")
    existing_subjects = cursor.fetchone()[0]
    
    if existing_subjects > 0:
        print(f"Sample data already exists ({existing_subjects} subjects found). Skipping creation.")
        conn.close()
        return
    
    # Get existing faculty and student IDs
    cursor.execute("SELECT faculty_id, name, email FROM faculty")
    faculty_data = cursor.fetchall()
    
    cursor.execute("SELECT student_id, name, roll_no, semester FROM students")
    student_data = cursor.fetchall()
    
    if not faculty_data or not student_data:
        print("No faculty or students found. Please register users first.")
        conn.close()
        return
    
    faculty_ids = [f[0] for f in faculty_data]
    
    # Create subjects
    subjects_data = [
        ("Database Management Systems", "Computer Science", 5),
        ("Software Engineering", "Computer Science", 5),
        ("Computer Networks", "Computer Science", 5),
        ("Machine Learning", "Computer Science", 7),
        ("Web Technologies", "Computer Science", 7),
        ("Data Structures", "Computer Science", 3),
    ]
    
    subject_ids = []
    for i, (subject_name, department, semester) in enumerate(subjects_data):
        faculty_id = faculty_ids[i % len(faculty_ids)]
        cursor.execute(
            "INSERT INTO subjects (subject_name, department, semester, faculty_id) VALUES (?, ?, ?, ?)",
            (subject_name, department, semester, faculty_id)
        )
        subject_ids.append(cursor.lastrowid)
    
    print(f"Created {len(subjects_data)} subjects")
    
    # Create timetable entries
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '14:00-15:00', '15:00-16:00', '16:00-17:00']
    
    timetable_count = 0
    for subject_id in subject_ids:
        # Get faculty for this subject
        cursor.execute("SELECT faculty_id, department, semester FROM subjects WHERE subject_id = ?", (subject_id,))
        faculty_id, department, semester = cursor.fetchone()
        
        # Each subject gets 2-3 time slots per week
        num_slots = random.randint(2, 3)
        selected_days = random.sample(days, num_slots)
        
        for day in selected_days:
            time_slot = random.choice(time_slots)
            
            cursor.execute(
                "INSERT INTO timetable (department, semester, day_of_week, subject_id, faculty_id, time_slot) VALUES (?, ?, ?, ?, ?, ?)",
                (department, semester, day, subject_id, faculty_id, time_slot)
            )
            timetable_count += 1
    
    print(f"Created {timetable_count} timetable entries")
    
    # Create attendance records
    attendance_count = 0
    for student_id, name, roll_no, semester in student_data:
        # Get subjects for student's semester
        cursor.execute("SELECT subject_id FROM subjects WHERE semester = ?", (semester,))
        semester_subjects = [row[0] for row in cursor.fetchall()]
        
        # Create attendance for last 30 days
        for i in range(30):
            date_obj = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            for subject_id in semester_subjects:
                # 85% chance of being present
                status = 'Present' if random.random() > 0.15 else 'Absent'
                
                cursor.execute(
                    "INSERT INTO attendance (student_id, subject_id, date, status) VALUES (?, ?, ?, ?)",
                    (student_id, subject_id, date_obj, status)
                )
                attendance_count += 1
    
    print(f"Created {attendance_count} attendance records")
    
    # Create assignments
    assignment_count = 0
    assignment_ids = []
    for subject_id in subject_ids:
        # Get faculty for this subject
        cursor.execute("SELECT faculty_id FROM subjects WHERE subject_id = ?", (subject_id,))
        faculty_id = cursor.fetchone()[0]
        
        # Each subject gets 2-3 assignments
        num_assignments = random.randint(2, 3)
        
        for j in range(num_assignments):
            due_date = (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
            
            cursor.execute("SELECT subject_name FROM subjects WHERE subject_id = ?", (subject_id,))
            subject_name = cursor.fetchone()[0]
            
            cursor.execute(
                "INSERT INTO assignments (subject_id, faculty_id, title, description, due_date) VALUES (?, ?, ?, ?, ?)",
                (subject_id, faculty_id, f"{subject_name} Assignment {j+1}", f"Assignment on {subject_name} topics", due_date)
            )
            assignment_ids.append(cursor.lastrowid)
            assignment_count += 1
    
    print(f"Created {assignment_count} assignments")
    
    # Create submissions
    submission_count = 0
    for student_id, name, roll_no, semester in student_data:
        # Get assignments for student's semester
        cursor.execute("""
            SELECT a.assignment_id 
            FROM assignments a 
            JOIN subjects s ON a.subject_id = s.subject_id 
            WHERE s.semester = ?
        """, (semester,))
        student_assignments = [row[0] for row in cursor.fetchall()]
        
        # Submit 70% of assignments
        num_to_submit = int(len(student_assignments) * 0.7)
        submitted_assignments = random.sample(student_assignments, num_to_submit)
        
        for assignment_id in submitted_assignments:
            # Random grade
            grades = ['A+', 'A', 'B+', 'B', 'C+', 'C']
            grade = random.choice(grades)
            submitted_at = (datetime.now() - timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d')
            
            cursor.execute(
                "INSERT INTO submissions (assignment_id, student_id, submitted_at, file_path, grade) VALUES (?, ?, ?, ?, ?)",
                (assignment_id, student_id, submitted_at, "sample_submission.pdf", grade)
            )
            submission_count += 1
    
    print(f"Created {submission_count} submissions")
    
    # Create messages/announcements
    message_contents = [
        ("Exam Schedule Update", "Mid-term exam schedule has been revised. Check the notice board."),
        ("Library Closure", "The central library will be closed this Saturday for maintenance."),
        ("Guest Lecture", "Dr. Sharma will deliver a guest lecture on AI trends next Friday."),
        ("Assignment Deadline", "Database assignment deadline extended by 2 days."),
        ("Workshop Announcement", "Workshop on Machine Learning basics this weekend."),
    ]
    
    message_count = 0
    for title, content in message_contents:
        faculty_id = random.choice(faculty_ids)
        timestamp = (datetime.now() - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            "INSERT INTO messages (sender_id, sender_type, receiver_id, receiver_type, message, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (faculty_id, 'faculty', None, 'student', f"{title}: {content}", timestamp)
        )
        message_count += 1
    
    print(f"Created {message_count} messages")
    
    # Create fee records
    for student_id, name, roll_no, semester in student_data:
        cursor.execute(
            "INSERT INTO fees (student_id, amount, status, due_date) VALUES (?, ?, ?, ?)",
            (student_id, 50000, random.choice(['Paid', 'Pending']), '2024-12-31')
        )
    
    # Create salary records
    for faculty_id, name, email in faculty_data:
        cursor.execute(
            "INSERT INTO salary (faculty_id, month, amount, status) VALUES (?, ?, ?, ?)",
            (faculty_id, 'November', 75000, 'Paid')
        )
    
    print("Created fee and salary records")
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print("\n✅ Sample data creation completed successfully!")
    print("\nSummary:")
    print(f"- {len(subjects_data)} subjects")
    print(f"- {timetable_count} timetable entries")
    print(f"- {attendance_count} attendance records")
    print(f"- {assignment_count} assignments")
    print(f"- {submission_count} submissions")
    print(f"- {message_count} messages")
    print(f"- Fee and salary records for all users")

if __name__ == '__main__':
    create_sample_data_sql()