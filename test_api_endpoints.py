"""
Quick test to verify API endpoints are working
Run this after starting Flask app (python app.py)
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_faculty_login():
    """Test faculty login"""
    print("\n" + "="*70)
    print("TEST 1: Faculty Login")
    print("="*70)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/faculty/login",
        json={
            "email": "test.faculty@gecr.edu",  # Use test faculty
            "password": "faculty123"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        return response.cookies
    else:
        print("❌ Login failed!")
        return None

def test_get_students(cookies):
    """Test getting students list"""
    print("\n" + "="*70)
    print("TEST 2: Get Students List")
    print("="*70)
    
    response = requests.get(
        f"{BASE_URL}/api/faculty/students",
        cookies=cookies
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Error: {response.json()}")
        return []
    
    data = response.json()
    print(f"Students found: {len(data)}")
    
    if len(data) > 0:
        print(f"\nFirst student:")
        print(json.dumps(data[0], indent=2))
        print("✅ Students retrieved successfully!")
    else:
        print("⚠️ No students found")
    
    return data

def test_add_single_student(cookies):
    """Test adding a single student"""
    print("\n" + "="*70)
    print("TEST 3: Add Single Student")
    print("="*70)
    
    student_data = {
        "roll_no": "2024TEST001",
        "name": "Test Student API",
        "email": "test.api@student.gecr.edu",
        "password": "test123",
        "department": "Computer Engineering",
        "semester": 5,
        "phone": "9876543210"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/faculty/students",
        json=student_data,
        cookies=cookies
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Student added successfully!")
    else:
        print("❌ Failed to add student")

def test_student_login_and_profile():
    """Test student login and profile retrieval"""
    print("\n" + "="*70)
    print("TEST 4: Student Login & Profile")
    print("="*70)
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/student/login",
        json={
            "email": "test.student@gecr.edu",  # Use test student
            "password": "student123"
        }
    )
    
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        print(f"Response: {login_response.json()}")
        return
    
    cookies = login_response.cookies
    
    # Get profile
    profile_response = requests.get(
        f"{BASE_URL}/api/student/profile",
        cookies=cookies
    )
    
    print(f"Profile Status: {profile_response.status_code}")
    profile = profile_response.json()
    print(f"\nProfile Data:")
    print(json.dumps(profile, indent=2))
    
    if profile_response.status_code == 200:
        print("✅ Profile retrieved successfully!")
        print(f"   Student: {profile['name']}")
        print(f"   Enrolled Subjects: {len(profile.get('enrolled_subjects', []))}")
    
    # Get subjects
    subjects_response = requests.get(
        f"{BASE_URL}/api/student/subjects",
        cookies=cookies
    )
    
    print(f"\nSubjects Status: {subjects_response.status_code}")
    if subjects_response.status_code == 200:
        subjects = subjects_response.json()
        print(f"Subjects with attendance:")
        for subject in subjects:
            print(f"   - {subject['subject_name']}: {subject['attendance_percentage']}%")
        print("✅ Subjects retrieved successfully!")
    
    # Get attendance
    attendance_response = requests.get(
        f"{BASE_URL}/api/student/attendance",
        cookies=cookies
    )
    
    print(f"\nAttendance Status: {attendance_response.status_code}")
    if attendance_response.status_code == 200:
        attendance = attendance_response.json()
        print(f"Overall Attendance: {attendance['overall_attendance_percentage']}%")
        print(f"By Subject:")
        for subject_data in attendance['by_subject']:
            print(f"   - {subject_data['subject_name']}: {subject_data['attendance_percentage']}%")
        print("✅ Attendance retrieved successfully!")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("STUDENT MANAGEMENT API - ENDPOINT TESTS")
    print("="*70)
    print("Make sure Flask app is running (python app.py)")
    print("="*70)
    
    # Test faculty endpoints
    cookies = test_faculty_login()
    
    if cookies:
        test_get_students(cookies)
        test_add_single_student(cookies)
    
    # Test student endpoints
    test_student_login_and_profile()
    
    print("\n" + "="*70)
    print("✅ All API Tests Completed!")
    print("="*70)
    print("\nNext Steps:")
    print("1. Open browser: http://127.0.0.1:5000")
    print("2. Login as faculty: test.faculty@gecr.edu / faculty123")
    print("3. Go to Students page")
    print("4. Try uploading Excel or adding students manually")
    print("5. Login as student: TEST001 (email: test.student@gecr.edu) / student123")
    print("6. View profile and attendance")
    print("="*70)
