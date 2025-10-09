"""Test script to manually create a notification and verify it works"""
from app import create_app
from database import db
from models.gecr_models import Student, Notification

app = create_app('development')

with app.app_context():
    try:
        # Get first student
        student = Student.query.first()
        
        if not student:
            print("❌ No student found in database")
            exit(1)
        
        print(f"✅ Found student: ID={student.student_id}, Email={student.email}")
        
        # Manually create a notification
        notif = Notification(
            user_id=student.student_id,
            user_type='student',
            title="📢 Test Notification",
            message="This is a test notification to verify the system works",
            notification_type='announcement',
            link='/student/dashboard'
        )
        
        db.session.add(notif)
        db.session.commit()
        
        print(f"✅ Created notification with ID: {notif.notification_id}")
        
        # Verify it was created
        notif_check = Notification.query.filter_by(notification_id=notif.notification_id).first()
        
        if notif_check:
            print(f"✅ Notification verified in database:")
            print(f"   - ID: {notif_check.notification_id}")
            print(f"   - User: {notif_check.user_id} ({notif_check.user_type})")
            print(f"   - Title: {notif_check.title}")
            print(f"   - Message: {notif_check.message}")
            print(f"   - Type: {notif_check.notification_type}")
            print(f"   - Read: {notif_check.read}")
            print(f"   - Link: {notif_check.link}")
        else:
            print("❌ Notification NOT found in database after commit")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
