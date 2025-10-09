"""
Simple test to demonstrate UI flow works
This just creates some sample data to show on the dashboards
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database import db
from models.gecr_models import Faculty, Student, Announcement, Event
from datetime import datetime, timedelta

app = create_app('development')

def create_sample_ui_data():
    """Create sample announcements and events for UI testing"""
    with app.app_context():
        print("🎨 Creating Sample UI Data\n")
        
        # Get or create a faculty member
        faculty = Faculty.query.first()
        if not faculty:
            faculty = Faculty(
                name='Dr. UI Test',
                email='uitest@gec.ac.in',
                department='Computer Science',
                phone='1234567890'
            )
            faculty.set_password('password123')
            db.session.add(faculty)
            db.session.commit()
            print("✅ Created test faculty")
        else:
            print(f"✅ Using existing faculty: {faculty.name}")
        
        # Create announcements
        announcements_data = [
            {
                'title': 'Mid-term Exam Schedule Released',
                'message': 'The mid-term examination schedule for all semesters has been published. Please check the notice board and student portal for details.',
                'expires_at': datetime.now() + timedelta(days=14)
            },
            {
                'title': 'Library Extended Hours',
                'message': 'The central library will remain open until 10 PM during exam weeks to facilitate student preparation.',
                'expires_at': datetime.now() + timedelta(days=30)
            },
            {
                'title': 'Placement Drive Next Week',
                'message': 'Major IT companies will be conducting campus interviews next week. Eligible students please register at the placement cell.',
                'expires_at': datetime.now() + timedelta(days=7)
            }
        ]
        
        print("\n📢 Creating Announcements:")
        for ann_data in announcements_data:
            # Check if announcement already exists
            existing = Announcement.query.filter_by(title=ann_data['title']).first()
            if not existing:
                ann = Announcement(
                    title=ann_data['title'],
                    message=ann_data['message'],
                    author_id=faculty.faculty_id,
                    expires_at=ann_data['expires_at']
                )
                db.session.add(ann)
                print(f"   ✅ {ann_data['title']}")
            else:
                print(f"   ⏭️  {ann_data['title']} (already exists)")
        
        # Create events
        events_data = [
            {
                'title': 'Tech Fest 2024',
                'description': 'Annual technical festival with coding competitions, project exhibitions, and guest lectures',
                'start_time': datetime.now() + timedelta(days=10),
                'end_time': datetime.now() + timedelta(days=12),
                'location': 'College Auditorium'
            },
            {
                'title': 'Guest Lecture on AI/ML',
                'description': 'Industry expert will discuss latest trends in Artificial Intelligence and Machine Learning',
                'start_time': datetime.now() + timedelta(days=3, hours=14),
                'end_time': datetime.now() + timedelta(days=3, hours=16),
                'location': 'Conference Hall B'
            },
            {
                'title': 'Sports Day',
                'description': 'Inter-department sports competition including cricket, football, and athletics',
                'start_time': datetime.now() + timedelta(days=20),
                'end_time': datetime.now() + timedelta(days=20, hours=8),
                'location': 'Sports Ground'
            }
        ]
        
        print("\n📅 Creating Events:")
        for event_data in events_data:
            # Check if event already exists
            existing = Event.query.filter_by(title=event_data['title']).first()
            if not existing:
                event = Event(
                    title=event_data['title'],
                    description=event_data['description'],
                    start_time=event_data['start_time'],
                    end_time=event_data['end_time'],
                    location=event_data['location'],
                    created_by=faculty.faculty_id
                )
                db.session.add(event)
                print(f"   ✅ {event_data['title']}")
            else:
                print(f"   ⏭️  {event_data['title']} (already exists)")
        
        db.session.commit()
        
        print("\n✨ Sample Data Created Successfully!")
        print("\n📊 Summary:")
        total_announcements = Announcement.query.count()
        total_events = Event.query.count()
        print(f"   Total Announcements: {total_announcements}")
        print(f"   Total Events: {total_events}")
        
        print("\n🎯 Next Steps:")
        print("   1. Start the Flask server: python app.py")
        print("   2. Login as faculty at /auth/login/faculty")
        print("   3. Visit /faculty/dashboard to see announcements")
        print("   4. Visit /faculty/manage-announcements to create more")
        print("   5. Login as student to see announcements on /student/dashboard")

if __name__ == '__main__':
    create_sample_ui_data()
