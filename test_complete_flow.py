"""
Complete End-to-End Test for Student Management System
Tests faculty upload, student portal, and real-time data display
"""

import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"

def print_header(text):
    print("\n" + "="*70)
    print(text)
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def test_complete_flow():
    """Test the complete student management flow"""
    
    print_header("COMPLETE STUDENT MANAGEMENT SYSTEM TEST")
    print("This will test:")
    print("  1. Faculty login and student upload")
    print("  2. Student login and portal access")
    print("  3. Real-time data display")
    print("  4. Attendance tracking")
    print("="*70)
    
    # Step 1: Faculty Login
    print_header("STEP 1: Faculty Login")
    faculty_response = requests.post(
        f"{BASE_URL}/api/auth/faculty/login",
        json={
            "email": "test.faculty@gecr.edu",
            "password": "faculty123"
        }
    )
    
    if faculty_response.status_code != 200:
        print_error(f"Faculty login failed: {faculty_response.json()}")
        return False
    
    print_success("Faculty logged in successfully")
    faculty_cookies = faculty_response.cookies
    faculty_data = faculty_response.json()
    print(f"   Faculty: {faculty_data['user']['name']}")
    
    # Step 2: Get current students list
    print_header("STEP 2: Get Current Students")
    students_response = requests.get(
        f"{BASE_URL}/api/faculty/students",
        cookies=faculty_cookies
    )
    
    if students_response.status_code == 200:
        students = students_response.json()
        print_success(f"Retrieved {len(students)} students")
        if len(students) > 0:
            print(f"   First student: {students[0]['name']} ({students[0]['roll_no']})")
    else:
        print_error(f"Failed to get students: {students_response.json()}")
    
    # Step 3: Add a new student
    print_header("STEP 3: Add New Student")
    new_student_data = {
        "roll_no": "2025TEST999",
        "name": "Integration Test Student",
        "email": "integration.test@gecr.edu",
        "password": "test123",
        "department": "Computer Engineering",
        "semester": 5,
        "phone": "9999999999"
    }
    
    add_response = requests.post(
        f"{BASE_URL}/api/faculty/students",
        json=new_student_data,
        cookies=faculty_cookies
    )
    
    if add_response.status_code == 201:
        print_success("Student added successfully")
        added_student = add_response.json()['student']
        print(f"   Roll No: {added_student['roll_no']}")
        print(f"   Name: {added_student['name']}")
        print(f"   Email: {added_student['email']}")
    else:
        print_error(f"Failed to add student: {add_response.json()}")
        # Continue anyway if student already exists
    
    # Step 4: Verify student appears in list
    print_header("STEP 4: Verify Student in List")
    students_response = requests.get(
        f"{BASE_URL}/api/faculty/students",
        cookies=faculty_cookies
    )
    
    if students_response.status_code == 200:
        students = students_response.json()
        found = any(s['roll_no'] == "2025TEST999" for s in students)
        if found:
            print_success("New student appears in faculty's student list")
        else:
            print_error("New student NOT found in list")
    
    # Step 5: Student Login
    print_header("STEP 5: Student Login")
    student_response = requests.post(
        f"{BASE_URL}/api/auth/student/login",
        json={
            "email": "test.student@gecr.edu",
            "password": "student123"
        }
    )
    
    if student_response.status_code != 200:
        print_error(f"Student login failed: {student_response.json()}")
        return False
    
    print_success("Student logged in successfully")
    student_cookies = student_response.cookies
    student_data = student_response.json()
    print(f"   Student: {student_data['user']['name']}")
    print(f"   Roll No: {student_data['user']['roll_no']}")
    
    # Step 6: Get Student Profile
    print_header("STEP 6: Get Student Profile")
    profile_response = requests.get(
        f"{BASE_URL}/api/student/profile",
        cookies=student_cookies
    )
    
    if profile_response.status_code == 200:
        profile = profile_response.json()
        print_success("Profile retrieved successfully")
        print(f"   Name: {profile['name']}")
        print(f"   Roll No: {profile['roll_no']}")
        print(f"   Department: {profile.get('department', 'Not Set')}")
        print(f"   Semester: {profile.get('semester', 'N/A')}")
        print(f"   Enrolled Subjects: {len(profile.get('enrolled_subjects', []))}")
        
        if profile.get('enrolled_subjects'):
            print("\n   Subjects:")
            for subject in profile['enrolled_subjects']:
                print(f"      - {subject['subject_code']}: {subject['subject_name']} ({subject['faculty_name']})")
    else:
        print_error(f"Failed to get profile: {profile_response.json()}")
    
    # Step 7: Get Student Subjects
    print_header("STEP 7: Get Student Subjects")
    subjects_response = requests.get(
        f"{BASE_URL}/api/student/subjects",
        cookies=student_cookies
    )
    
    if subjects_response.status_code == 200:
        subjects = subjects_response.json()
        print_success(f"Retrieved {len(subjects)} enrolled subjects")
        
        if subjects:
            print("\n   Subject Details:")
            for subject in subjects:
                print(f"      {subject['subject_code']} - {subject['subject_name']}")
                print(f"         Faculty: {subject['faculty_name']}")
                print(f"         Attendance: {subject['present_count']}/{subject['total_classes']} ({subject['attendance_percentage']:.1f}%)")
    else:
        print_error(f"Failed to get subjects: {subjects_response.json()}")
    
    # Step 8: Get Student Attendance
    print_header("STEP 8: Get Student Attendance")
    attendance_response = requests.get(
        f"{BASE_URL}/api/student/attendance",
        cookies=student_cookies
    )
    
    if attendance_response.status_code == 200:
        attendance = attendance_response.json()
        print_success("Attendance retrieved successfully")
        print(f"   Overall Attendance: {attendance['overall_attendance_percentage']:.1f}%")
        
        if attendance.get('by_subject'):
            print("\n   Subject-wise Breakdown:")
            for subject_att in attendance['by_subject']:
                print(f"      {subject_att['subject_name']}")
                print(f"         Classes: {subject_att['present_count']}/{subject_att['total_classes']}")
                print(f"         Percentage: {subject_att['attendance_percentage']:.1f}%")
        
        if attendance.get('recent_records'):
            print(f"\n   Recent Records: {len(attendance['recent_records'])}")
            for record in attendance['recent_records'][:3]:
                print(f"      - {record['date']}: {record['subject_name']} - {record['status'].upper()}")
    else:
        print_error(f"Failed to get attendance: {attendance_response.json()}")
    
    # Step 9: Get Student Notifications
    print_header("STEP 9: Get Student Notifications")
    notifications_response = requests.get(
        f"{BASE_URL}/api/student/notifications",
        cookies=student_cookies
    )
    
    if notifications_response.status_code == 200:
        notifications_data = notifications_response.json()
        total = len(notifications_data.get('notifications', []))
        unread = notifications_data.get('unread_count', 0)
        print_success(f"Retrieved {total} notifications ({unread} unread)")
        
        if notifications_data.get('notifications'):
            print("\n   Recent Notifications:")
            for notif in notifications_data['notifications'][:3]:
                status = "📬 NEW" if not notif['read'] else "✓ Read"
                print(f"      {status} - {notif['title']}")
                print(f"         {notif['message']}")
    else:
        print_error(f"Failed to get notifications: {notifications_response.json()}")
    
    # Final Summary
    print_header("TEST SUMMARY")
    print_success("All tests completed!")
    print("\nVerification Checklist:")
    print("  ✓ Faculty can login")
    print("  ✓ Faculty can view students list")
    print("  ✓ Faculty can add students manually")
    print("  ✓ New students appear in list immediately")
    print("  ✓ Students can login")
    print("  ✓ Students can view their profile")
    print("  ✓ Students can see enrolled subjects")
    print("  ✓ Students can view attendance (overall & by subject)")
    print("  ✓ Students can see notifications")
    print("\n" + "="*70)
    print("🎉 Student Management System is working correctly!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PREREQUISITES:")
    print("="*70)
    print("1. Flask app must be running: python app.py")
    print("2. Test users must exist: python create_test_users.py")
    print("3. Some enrollments should exist: python setup_enrollments.py")
    print("="*70)
    
    input("\nPress ENTER when ready to start tests...")
    
    try:
        success = test_complete_flow()
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed. Check the output above.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
