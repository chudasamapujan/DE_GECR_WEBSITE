"""
Test script to verify dashboard data functions work correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models.gecr_models import Student, Faculty
from dashboard_data import get_student_dashboard_data, get_faculty_dashboard_data

def test_dashboard_functions():
    """Test dashboard data functions with actual database data"""
    app = create_app()
    with app.app_context():
        print("Testing Dashboard Data Functions...")
        print("=" * 50)
        
        # Test student dashboard
        print("\n1. Testing Student Dashboard:")
        students = Student.query.limit(2).all()
        
        if students:
            for student in students:
                print(f"\nTesting student: {student.name} (ID: {student.student_id})")
                try:
                    data = get_student_dashboard_data(student.student_id)
                    if data:
                        print(f"✅ Student dashboard data loaded successfully")
                        print(f"   - Attendance: {data['attendance_percentage']:.1f}%")
                        print(f"   - CGPA: {data['cgpa']:.2f}")
                        print(f"   - Pending assignments: {len(data['pending_assignments'])}")
                        print(f"   - Current subjects: {len(data['current_subjects'])}")
                        print(f"   - Today's schedule: {len(data['today_schedule'])}")
                        print(f"   - Recent messages: {len(data['recent_messages'])}")
                    else:
                        print(f"❌ No data returned for student {student.name}")
                except Exception as e:
                    print(f"❌ Error loading student dashboard: {str(e)}")
        else:
            print("❌ No students found in database")
        
        # Test faculty dashboard
        print("\n2. Testing Faculty Dashboard:")
        faculty = Faculty.query.limit(2).all()
        
        if faculty:
            for fac in faculty:
                print(f"\nTesting faculty: {fac.name} (ID: {fac.faculty_id})")
                try:
                    data = get_faculty_dashboard_data(fac.faculty_id)
                    if data:
                        print(f"✅ Faculty dashboard data loaded successfully")
                        print(f"   - Faculty subjects: {len(data['faculty_subjects'])}")
                        print(f"   - Total students: {data['total_students']}")
                        print(f"   - Total assignments: {data['total_assignments']}")
                        print(f"   - Pending submissions: {len(data['pending_submissions'])}")
                        print(f"   - Recent assignments: {len(data['recent_assignments'])}")
                        print(f"   - Recent messages: {len(data['recent_messages'])}")
                    else:
                        print(f"❌ No data returned for faculty {fac.name}")
                except Exception as e:
                    print(f"❌ Error loading faculty dashboard: {str(e)}")
        else:
            print("❌ No faculty found in database")
        
        print("\n" + "=" * 50)
        print("Dashboard testing completed!")

if __name__ == '__main__':
    test_dashboard_functions()