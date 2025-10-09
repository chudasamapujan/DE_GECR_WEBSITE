"""Test script to verify notification system"""
from app import create_app
from database import db
from models.gecr_models import Student, Faculty, Notification

app = create_app('development')

with app.app_context():
    # Check how many students exist
    students = Student.query.all()
    print(f"✅ Found {len(students)} students in database")
    for student in students:
        print(f"   - Student ID: {student.student_id}, Email: {student.email}")
    
    print()
    
    # Check how many notifications exist
    notifications = Notification.query.all()
    print(f"✅ Found {len(notifications)} notifications in database")
    for notif in notifications:
        print(f"   - ID: {notif.notification_id}, User: {notif.user_id} ({notif.user_type})")
        print(f"     Type: {notif.notification_type}, Read: {notif.read}")
        print(f"     Title: {notif.title}")
        print(f"     Message: {notif.message[:100]}...")
        print()
    
    # Check unread notifications for student 1
    if students:
        student_id = students[0].student_id
        unread = Notification.query.filter_by(
            user_id=student_id,
            user_type='student',
            read=False
        ).count()
        print(f"✅ Student {student_id} has {unread} unread notifications")
