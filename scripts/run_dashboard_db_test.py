import os
import sys

# Make sure project root is on sys.path so imports like `import app` work when
# this script is executed from the scripts/ directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from database import db
from models.gecr_models import Faculty, Student, Announcement, Event, Activity, Attendance
import json

app = create_app('testing')
from app import create_app
from database import db
from models.gecr_models import Faculty, Student
import json

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
    
    # create sample faculty and students
    f = Faculty(name='Prof Test', email='prof@test.local')
    f.set_password('password')
    db.session.add(f)
    s1 = Student(roll_no='S1001', name='Alice', email='alice@test.local')
    s1.set_password('p')
    s2 = Student(roll_no='S1002', name='Bob', email='bob@test.local')
    s2.set_password('p')
    db.session.add_all([s1, s2])
    db.session.commit()

    client = app.test_client()
    # Manually set a JWT-like session via headers isn't straightforward; faculty endpoints use JWT.
    # For testing, we'll monkeypatch get_jwt_identity via a small wrapper by logging in via session endpoints.
    with client.session_transaction() as sess:
        sess['user_id'] = f.faculty_id
        sess['user_type'] = 'faculty'
        sess['user_email'] = f.email
        sess['user_name'] = f.name

    # Create announcement
    ann_resp = client.post('/api/faculty/announcements', json={'title': 'Test Ann', 'message': 'Hello world'})
    print('Create announcement status:', ann_resp.status_code, ann_resp.get_json())

    # Create event
    ev_resp = client.post('/api/faculty/events', json={'title': 'Seminar', 'start_time': '2025-12-01T10:00:00', 'end_time': '2025-12-01T12:00:00', 'location': 'Auditorium'})
    print('Create event status:', ev_resp.status_code, ev_resp.get_json())

    # Mark attendance
    att_payload = {
        'subject_id': 1,
        'date': '2025-10-08',
        'attendance_data': [
            {'student_id': s1.student_id, 'status': 'present'},
            {'student_id': s2.student_id, 'status': 'absent'}
        ]
    }
    att_resp = client.post('/api/faculty/attendance', json=att_payload)
    print('Mark attendance status:', att_resp.status_code, att_resp.get_json())

    # List announcements/events/activities
    list_ann = client.get('/api/faculty/announcements')
    list_ev = client.get('/api/faculty/events')
    list_act = client.get('/api/faculty/activities')
    print('List announcements:', list_ann.status_code, list_ann.get_json())
    print('List events:', list_ev.status_code, list_ev.get_json())
    print('List activities:', list_act.status_code, list_act.get_json())

print('Dashboard DB test completed')
