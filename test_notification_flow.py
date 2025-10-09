"""End-to-end test of the notification system"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test data
faculty_email = "chudasamapujan49@gmail.com"
faculty_password = "Pujan@123"

student_email = "chudasamapujan49@gmail.com"  # Same as we saw in logs
student_password = "Pujan@123"

def test_notification_flow():
    print("🧪 Starting End-to-End Notification Test\n")
    
    # Step 1: Faculty creates an announcement
    print("📝 Step 1: Faculty creates announcement...")
    try:
        # Login as faculty (session-based)
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/auth/login/faculty",
            data={
                'email': faculty_email,
                'password': faculty_password
            },
            allow_redirects=False
        )
        
        if login_response.status_code in [200, 302]:
            print("   ✅ Faculty logged in successfully")
        else:
            print(f"   ❌ Faculty login failed: {login_response.status_code}")
            return
        
        # Create announcement
        announcement_data = {
            'title': 'Test Announcement for Notifications',
            'message': 'This announcement should trigger notifications for all students!',
            'expires_at': '2025-12-31'
        }
        
        create_response = session.post(
            f"{BASE_URL}/api/faculty/announcements",
            json=announcement_data
        )
        
        if create_response.status_code == 201:
            print(f"   ✅ Announcement created: {create_response.json()}")
        else:
            print(f"   ❌ Failed to create announcement: {create_response.status_code}")
            print(f"      Response: {create_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error in faculty flow: {str(e)}")
        return
    
    print()
    
    # Step 2: Check if notifications were created
    print("🔍 Step 2: Checking if notifications were created...")
    try:
        from app import create_app
        from models.gecr_models import Notification
        
        app = create_app('development')
        with app.app_context():
            notifications = Notification.query.all()
            print(f"   ✅ Found {len(notifications)} total notifications in database")
            
            for notif in notifications:
                print(f"      - ID: {notif.notification_id}, User: {notif.user_id}, Title: {notif.title}")
    except Exception as e:
        print(f"   ❌ Error checking notifications: {str(e)}")
    
    print()
    
    # Step 3: Student retrieves notifications
    print("📬 Step 3: Student retrieves notifications...")
    try:
        # Login as student
        student_session = requests.Session()
        student_login = student_session.post(
            f"{BASE_URL}/auth/login/student",
            data={
                'email': student_email,
                'password': student_password
            },
            allow_redirects=False
        )
        
        if student_login.status_code in [200, 302]:
            print("   ✅ Student logged in successfully")
        else:
            print(f"   ❌ Student login failed: {student_login.status_code}")
            return
        
        # Get notifications
        notif_response = student_session.get(f"{BASE_URL}/api/student/notifications")
        
        if notif_response.status_code == 200:
            data = notif_response.json()
            print(f"   ✅ Retrieved notifications: {len(data['notifications'])} notifications")
            print(f"   ✅ Unread count: {data['unread_count']}")
            
            for notif in data['notifications']:
                print(f"      - {notif['title']} (Read: {notif['read']})")
        else:
            print(f"   ❌ Failed to get notifications: {notif_response.status_code}")
            print(f"      Response: {notif_response.text}")
            
    except Exception as e:
        print(f"   ❌ Error in student flow: {str(e)}")
    
    print()
    
    # Step 4: Mark notification as read
    print("✓ Step 4: Mark notification as read...")
    try:
        # Get the first notification ID
        notif_response = student_session.get(f"{BASE_URL}/api/student/notifications")
        if notif_response.status_code == 200:
            notifications = notif_response.json()['notifications']
            if notifications:
                first_notif_id = notifications[0]['notification_id']
                
                mark_read_response = student_session.post(
                    f"{BASE_URL}/api/student/notifications/{first_notif_id}/mark-read"
                )
                
                if mark_read_response.status_code == 200:
                    print(f"   ✅ Marked notification {first_notif_id} as read")
                    
                    # Verify unread count decreased
                    updated_response = student_session.get(f"{BASE_URL}/api/student/notifications")
                    if updated_response.status_code == 200:
                        updated_data = updated_response.json()
                        print(f"   ✅ New unread count: {updated_data['unread_count']}")
                else:
                    print(f"   ❌ Failed to mark as read: {mark_read_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error marking as read: {str(e)}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_notification_flow()
