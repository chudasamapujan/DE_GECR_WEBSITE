from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import Student
from utils import format_response, paginate_results
from validators import StudentProfileUpdateSchema

student_bp = Blueprint('student', __name__)

# Initialize schemas
profile_update_schema = StudentProfileUpdateSchema()

@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get student profile"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'student':
            return format_response(False, 'Access denied', 403)
        
        student_id = get_jwt_identity()
        student = Student.find_by_id(student_id)
        
        if not student:
            return format_response(False, 'Student not found', 404)
        
        # Remove sensitive data
        student.pop('password', None)
        student['_id'] = str(student['_id'])
        
        return format_response(
            True,
            'Profile retrieved successfully',
            200,
            {'profile': student}
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update student profile"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'student':
            return format_response(False, 'Access denied', 403)
        
        student_id = get_jwt_identity()
        
        # Validate request data
        data = profile_update_schema.load(request.json)
        
        # Update profile
        result = Student.update_profile(student_id, data)
        
        if result.modified_count == 0:
            return format_response(False, 'No changes made or student not found', 400)
        
        # Get updated profile
        updated_student = Student.find_by_id(student_id)
        updated_student.pop('password', None)
        updated_student['_id'] = str(updated_student['_id'])
        
        return format_response(
            True,
            'Profile updated successfully',
            200,
            {'profile': updated_student}
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get student dashboard data"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'student':
            return format_response(False, 'Access denied', 403)
        
        student_id = get_jwt_identity()
        student = Student.find_by_id(student_id)
        
        if not student:
            return format_response(False, 'Student not found', 404)
        
        # Prepare dashboard data
        dashboard_data = {
            'welcome_message': f"Welcome back, {student.get('firstName', '')} {student.get('lastName', '')}!",
            'student_info': {
                'name': f"{student.get('firstName', '')} {student.get('lastName', '')}",
                'enrollmentNumber': student.get('enrollmentNumber'),
                'branch': student.get('branch'),
                'semester': student.get('semester'),
                'email': student.get('email'),
                'phone': student.get('phone')
            },
            'quick_stats': {
                'total_subjects': 6,  # This would come from subjects collection
                'attendance_percentage': 85,  # This would come from attendance collection
                'pending_assignments': 3,  # This would come from assignments collection
                'upcoming_exams': 2  # This would come from exams collection
            },
            'recent_activities': [
                {
                    'type': 'assignment',
                    'title': 'Data Structures Assignment 3',
                    'due_date': '2024-01-15',
                    'status': 'pending'
                },
                {
                    'type': 'exam',
                    'title': 'Database Management System - Mid Sem',
                    'date': '2024-01-20',
                    'status': 'upcoming'
                }
            ],
            'announcements': [
                {
                    'title': 'Holiday Notice',
                    'content': 'College will remain closed on Republic Day',
                    'date': '2024-01-10',
                    'priority': 'medium'
                }
            ]
        }
        
        return format_response(
            True,
            'Dashboard data retrieved successfully',
            200,
            dashboard_data
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@student_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    """Get student's subjects"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'student':
            return format_response(False, 'Access denied', 403)
        
        student_id = get_jwt_identity()
        student = Student.find_by_id(student_id)
        
        if not student:
            return format_response(False, 'Student not found', 404)
        
        # Mock subjects data - replace with actual database query
        subjects = [
            {
                'id': '1',
                'name': 'Data Structures and Algorithms',
                'code': 'CS301',
                'credits': 4,
                'faculty': 'Dr. Smith',
                'attendance': 88
            },
            {
                'id': '2',
                'name': 'Database Management Systems',
                'code': 'CS302',
                'credits': 3,
                'faculty': 'Dr. Johnson',
                'attendance': 92
            },
            {
                'id': '3',
                'name': 'Computer Networks',
                'code': 'CS303',
                'credits': 3,
                'faculty': 'Dr. Brown',
                'attendance': 85
            }
        ]
        
        return format_response(
            True,
            'Subjects retrieved successfully',
            200,
            {'subjects': subjects}
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@student_bp.route('/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    """Get student's attendance"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'student':
            return format_response(False, 'Access denied', 403)
        
        student_id = get_jwt_identity()
        subject_id = request.args.get('subject_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Mock attendance data - replace with actual database query
        attendance_records = [
            {
                'id': '1',
                'date': '2024-01-10',
                'subject': 'Data Structures',
                'status': 'present',
                'time': '10:00 AM'
            },
            {
                'id': '2',
                'date': '2024-01-09',
                'subject': 'Database Systems',
                'status': 'present',
                'time': '11:00 AM'
            },
            {
                'id': '3',
                'date': '2024-01-08',
                'subject': 'Computer Networks',
                'status': 'absent',
                'time': '02:00 PM'
            }
        ]
        
        # Mock pagination
        total = len(attendance_records)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_records = attendance_records[start:end]
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
            'has_next': end < total,
            'has_prev': page > 1
        }
        
        return format_response(
            True,
            'Attendance retrieved successfully',
            200,
            {
                'attendance': paginated_records,
                'pagination': pagination_info
            }
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@student_bp.route('/assignments', methods=['GET'])
@jwt_required()
def get_assignments():
    """Get student's assignments"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'student':
            return format_response(False, 'Access denied', 403)
        
        student_id = get_jwt_identity()
        status = request.args.get('status', 'all')  # all, pending, submitted, graded
        
        # Mock assignments data - replace with actual database query
        assignments = [
            {
                'id': '1',
                'title': 'Array Implementation',
                'subject': 'Data Structures',
                'due_date': '2024-01-15',
                'status': 'pending',
                'marks': None,
                'total_marks': 20
            },
            {
                'id': '2',
                'title': 'ER Diagram Design',
                'subject': 'Database Systems',
                'due_date': '2024-01-12',
                'status': 'submitted',
                'submitted_date': '2024-01-11',
                'marks': 18,
                'total_marks': 20
            }
        ]
        
        # Filter by status
        if status != 'all':
            assignments = [a for a in assignments if a['status'] == status]
        
        return format_response(
            True,
            'Assignments retrieved successfully',
            200,
            {'assignments': assignments}
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@student_bp.route('/grades', methods=['GET'])
@jwt_required()
def get_grades():
    """Get student's grades"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'student':
            return format_response(False, 'Access denied', 403)
        
        student_id = get_jwt_identity()
        semester = request.args.get('semester')
        
        # Mock grades data - replace with actual database query
        grades = {
            'current_semester': {
                'semester': 5,
                'subjects': [
                    {
                        'name': 'Data Structures',
                        'code': 'CS301',
                        'internal_marks': 18,
                        'external_marks': 85,
                        'total_marks': 103,
                        'grade': 'A+',
                        'credits': 4
                    },
                    {
                        'name': 'Database Systems',
                        'code': 'CS302',
                        'internal_marks': 19,
                        'external_marks': 78,
                        'total_marks': 97,
                        'grade': 'A',
                        'credits': 3
                    }
                ],
                'sgpa': 8.5,
                'total_credits': 22
            },
            'overall': {
                'cgpa': 8.2,
                'total_credits': 90
            }
        }
        
        return format_response(
            True,
            'Grades retrieved successfully',
            200,
            grades
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)