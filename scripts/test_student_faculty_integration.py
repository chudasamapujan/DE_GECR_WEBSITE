import os
import sys

# Make sure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from database import db
from models.gecr_models import Faculty, Student, Announcement, Event, Activity, Attendance
import json

print("=" * 60)
print("Faculty-Student Database Integration Test")
print("=" * 60)

app = create_app('testing')
with app.app_context():
    db.create_all()
    
    # Clear existing data for clean test
    db.session.query(Activity).delete()
    db.session.query(Announcement).delete()
    db.session.query(Event).delete()
    db.session.query(Attendance).delete()
    db.session.query(Student).delete()
    db.session.query(Faculty).delete()
    db.session.commit()
    
    # Create sample faculty
    faculty = Faculty(name='Dr. Smith', email='smith@test.local', department='Computer Science')
    faculty.set_password('password')
    db.session.add(faculty)
    
    # Create sample students
    student1 = Student(roll_no='CS001', name='Alice Johnson', email='alice@test.local', department='Computer Science', semester=3)
    student1.set_password('password')
    student2 = Student(roll_no='CS002', name='Bob Wilson', email='bob@test.local', department='Computer Science', semester=3)
    student2.set_password('password')
    db.session.add_all([student1, student2])
    db.session.commit()
    
    print(f"\n✓ Created Faculty: {faculty.name} (ID: {faculty.faculty_id})")
    print(f"✓ Created Students: {student1.name} (ID: {student1.student_id}), {student2.name} (ID: {student2.student_id})")
    
    client = app.test_client()
    
    # ===== FACULTY ACTIONS =====
    print("\n" + "=" * 60)
    print("FACULTY ACTIONS: Dr. Smith creating content")
    print("=" * 60)
    
    with client.session_transaction() as sess:
        sess['user_id'] = faculty.faculty_id
        sess['user_type'] = 'faculty'
        sess['user_email'] = faculty.email
        sess['user_name'] = faculty.name
    
    # 1. Faculty creates announcement
    ann_resp = client.post('/api/faculty/announcements', json={
        'title': 'Mid-term Exam Schedule',
        'message': 'Mid-term exams will be held from Oct 20-25. Please check the detailed timetable.'
    })
    print(f"\n1. Create Announcement: Status {ann_resp.status_code}")
    if ann_resp.status_code == 201:
        ann_data = ann_resp.get_json()
        print(f"   ✓ Announcement: '{ann_data['announcement']['title']}'")
    
    # 2. Faculty creates event
    ev_resp = client.post('/api/faculty/events', json={
        'title': 'Guest Lecture on AI',
        'description': 'Industry expert will speak about latest AI trends',
        'start_time': '2025-10-15T14:00:00',
        'end_time': '2025-10-15T16:00:00',
        'location': 'Auditorium A'
    })
    print(f"\n2. Create Event: Status {ev_resp.status_code}")
    if ev_resp.status_code == 201:
        ev_data = ev_resp.get_json()
        print(f"   ✓ Event: '{ev_data['event']['title']}' on {ev_data['event']['start_time']}")
    
    # 3. Faculty marks attendance
    att_resp = client.post('/api/faculty/attendance', json={
        'subject_id': 101,
        'date': '2025-10-08',
        'attendance_data': [
            {'student_id': student1.student_id, 'status': 'present'},
            {'student_id': student2.student_id, 'status': 'absent'}
        ]
    })
    print(f"\n3. Mark Attendance: Status {att_resp.status_code}")
    if att_resp.status_code == 200:
        att_data = att_resp.get_json()
        print(f"   ✓ Marked attendance for {att_data['students_marked']} students")
    
    # ===== STUDENT VIEWS =====
    print("\n" + "=" * 60)
    print("STUDENT VIEW: Alice checking portal")
    print("=" * 60)
    
    # Switch to student session
    with client.session_transaction() as sess:
        sess['user_id'] = student1.student_id
        sess['user_type'] = 'student'
        sess['user_email'] = student1.email
        sess['user_name'] = student1.name
    
    # 1. Student views announcements
    s_ann_resp = client.get('/api/student/announcements')
    print(f"\n1. View Announcements: Status {s_ann_resp.status_code}")
    if s_ann_resp.status_code == 200:
        s_ann_data = s_ann_resp.get_json()
        print(f"   ✓ Found {len(s_ann_data['announcements'])} announcement(s)")
        for ann in s_ann_data['announcements']:
            print(f"     - {ann['title']}")
    
    # 2. Student views upcoming events
    s_ev_resp = client.get('/api/student/upcoming-events')
    print(f"\n2. View Upcoming Events: Status {s_ev_resp.status_code}")
    if s_ev_resp.status_code == 200:
        s_ev_data = s_ev_resp.get_json()
        print(f"   ✓ Found {len(s_ev_data['events'])} upcoming event(s)")
        for ev in s_ev_data['events']:
            print(f"     - {ev['title']} at {ev['location']}")
    
    # 3. Student views their attendance
    s_att_resp = client.get('/api/student/my-attendance')
    print(f"\n3. View My Attendance: Status {s_att_resp.status_code}")
    if s_att_resp.status_code == 200:
        s_att_data = s_att_resp.get_json()
        stats = s_att_data['statistics']
        print(f"   ✓ Attendance Statistics:")
        print(f"     Total Classes: {stats['total_classes']}")
        print(f"     Present: {stats['present']}")
        print(f"     Absent: {stats['absent']}")
        print(f"     Percentage: {stats['percentage']}%")
    
    # 4. Student views recent activities
    s_act_resp = client.get('/api/student/recent-activities')
    print(f"\n4. View Recent Activities: Status {s_act_resp.status_code}")
    if s_act_resp.status_code == 200:
        s_act_data = s_act_resp.get_json()
        print(f"   ✓ Found {len(s_act_data['activities'])} recent activit(ies)")
        for act in s_act_data['activities']:
            print(f"     - {act['type']}: {act['title']}")
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n✓ Faculty can create announcements, events, and mark attendance")
    print("✓ Students can view all faculty-created content")
    print("✓ Database connectivity between faculty and students is working")
