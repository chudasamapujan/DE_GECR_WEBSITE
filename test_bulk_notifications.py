"""Test the bulk notification creation function"""
from app import create_app
from database import db
from models.gecr_models import Student, Notification

app = create_app('development')

def create_notifications_for_students_test(title, message, notification_type, link=None):
    """Test version of the notification creation function"""
    try:
        # Get all students
        students = Student.query.all()
        print(f"📊 Found {len(students)} students")
        
        # Create a notification for each student
        notifications = []
        for student in students:
            notif = Notification(
                user_id=student.student_id,
                user_type='student',
                title=title,
                message=message,
                notification_type=notification_type,
                link=link
            )
            notifications.append(notif)
            print(f"   ✅ Created notification for student {student.student_id}")
        
        # Bulk insert
        print(f"💾 Saving {len(notifications)} notifications...")
        db.session.bulk_save_objects(notifications)
        db.session.commit()
        
        print(f"✅ Successfully created {len(notifications)} notifications")
        return len(notifications)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

with app.app_context():
    # Clear existing test notifications first
    Notification.query.delete()
    db.session.commit()
    print("🧹 Cleared existing notifications\n")
    
    # Test the function
    count = create_notifications_for_students_test(
        title="📢 Test Announcement",
        message="This is a test message from the bulk creation function",
        notification_type='announcement',
        link='/student/dashboard'
    )
    
    print(f"\n📈 Result: {count} notifications created")
    
    # Verify
    all_notifications = Notification.query.all()
    print(f"✅ Verification: {len(all_notifications)} notifications in database")
    
    for notif in all_notifications:
        print(f"   - Notification {notif.notification_id}: User {notif.user_id}, Title: {notif.title}")
