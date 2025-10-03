from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import Faculty, Student
from utils import format_response, paginate_results
from validators import FacultyProfileUpdateSchema

faculty_bp = Blueprint('faculty', __name__)

# Initialize schemas
profile_update_schema = FacultyProfileUpdateSchema()

@faculty_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get faculty profile"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        faculty = Faculty.find_by_id(faculty_id)
        
        if not faculty:
            return format_response(False, 'Faculty not found', 404)
        
        # Remove sensitive data
        faculty.pop('password', None)
        faculty['_id'] = str(faculty['_id'])
        
        return format_response(
            True,
            'Profile retrieved successfully',
            200,
            {'profile': faculty}
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@faculty_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update faculty profile"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        
        # Validate request data
        data = profile_update_schema.load(request.json)
        
        # Update profile
        result = Faculty.update_profile(faculty_id, data)
        
        if result.modified_count == 0:
            return format_response(False, 'No changes made or faculty not found', 400)
        
        # Get updated profile
        updated_faculty = Faculty.find_by_id(faculty_id)
        updated_faculty.pop('password', None)
        updated_faculty['_id'] = str(updated_faculty['_id'])
        
        return format_response(
            True,
            'Profile updated successfully',
            200,
            {'profile': updated_faculty}
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@faculty_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get faculty dashboard data"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        faculty = Faculty.find_by_id(faculty_id)
        
        if not faculty:
            return format_response(False, 'Faculty not found', 404)
        
        # Prepare dashboard data
        dashboard_data = {
            'welcome_message': f"Welcome back, Dr. {faculty.get('firstName', '')} {faculty.get('lastName', '')}!",
            'faculty_info': {
                'name': f"Dr. {faculty.get('firstName', '')} {faculty.get('lastName', '')}",
                'facultyId': faculty.get('facultyId'),
                'department': faculty.get('department'),
                'designation': faculty.get('designation'),
                'email': faculty.get('email'),
                'phone': faculty.get('phone')
            },
            'quick_stats': {
                'total_subjects': 3,  # This would come from subjects collection
                'total_students': 150,  # This would come from students enrolled in faculty's subjects
                'pending_assignments': 12,  # This would come from assignments collection
                'upcoming_classes': 5  # This would come from schedule collection
            },
            'recent_activities': [
                {
                    'type': 'assignment',
                    'title': 'Database Design Assignment graded',
                    'count': 25,
                    'date': '2024-01-10'
                },
                {
                    'type': 'attendance',
                    'title': 'Attendance marked for CS302',
                    'count': 45,
                    'date': '2024-01-10'
                }
            ],
            'today_schedule': [
                {
                    'time': '10:00 AM - 11:00 AM',
                    'subject': 'Database Management Systems',
                    'class': 'CS 5th Sem A',
                    'room': 'Lab 301'
                },
                {
                    'time': '02:00 PM - 03:00 PM',
                    'subject': 'Software Engineering',
                    'class': 'CS 7th Sem B',
                    'room': 'Room 205'
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

@faculty_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    """Get faculty's subjects"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        
        # Mock subjects data - replace with actual database query
        subjects = [
            {
                'id': '1',
                'name': 'Database Management Systems',
                'code': 'CS302',
                'credits': 3,
                'semester': 5,
                'branch': 'Computer Science',
                'students_enrolled': 45,
                'schedule': {
                    'days': ['Monday', 'Wednesday', 'Friday'],
                    'time': '10:00 AM - 11:00 AM',
                    'room': 'Lab 301'
                }
            },
            {
                'id': '2',
                'name': 'Software Engineering',
                'code': 'CS401',
                'credits': 4,
                'semester': 7,
                'branch': 'Computer Science',
                'students_enrolled': 38,
                'schedule': {
                    'days': ['Tuesday', 'Thursday'],
                    'time': '02:00 PM - 04:00 PM',
                    'room': 'Room 205'
                }
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

@faculty_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    """Get students enrolled in faculty's subjects"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        subject_id = request.args.get('subject_id')
        branch = request.args.get('branch')
        semester = request.args.get('semester')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Mock students data - replace with actual database query
        students = [
            {
                'id': '1',
                'enrollmentNumber': '220001',
                'name': 'John Doe',
                'email': 'john.doe@student.gec.ac.in',
                'branch': 'Computer Science',
                'semester': 5,
                'phone': '9876543210',
                'attendance_percentage': 88
            },
            {
                'id': '2',
                'enrollmentNumber': '220002',
                'name': 'Jane Smith',
                'email': 'jane.smith@student.gec.ac.in',
                'branch': 'Computer Science',
                'semester': 5,
                'phone': '9876543211',
                'attendance_percentage': 92
            }
        ]
        
        # Filter students based on parameters
        if subject_id:
            # Filter by subject enrollment
            pass
        if branch:
            students = [s for s in students if s['branch'].lower() == branch.lower()]
        if semester:
            students = [s for s in students if s['semester'] == int(semester)]
        
        # Mock pagination
        total = len(students)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_students = students[start:end]
        
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
            'Students retrieved successfully',
            200,
            {
                'students': paginated_students,
                'pagination': pagination_info
            }
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@faculty_bp.route('/attendance', methods=['POST'])
@jwt_required()
def mark_attendance():
    """Mark attendance for students"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        data = request.json
        
        required_fields = ['subject_id', 'date', 'attendance_data']
        for field in required_fields:
            if field not in data:
                return format_response(False, f'Missing required field: {field}', 400)
        
        # Mock attendance marking - replace with actual database operations
        subject_id = data['subject_id']
        date = data['date']
        attendance_data = data['attendance_data']  # List of {student_id, status}
        
        # Validate attendance data
        for record in attendance_data:
            if 'student_id' not in record or 'status' not in record:
                return format_response(False, 'Invalid attendance data format', 400)
            if record['status'] not in ['present', 'absent', 'late']:
                return format_response(False, 'Invalid attendance status', 400)
        
        # Here you would save attendance records to database
        # attendance_collection.insert_many([...])
        
        return format_response(
            True,
            'Attendance marked successfully',
            200,
            {
                'subject_id': subject_id,
                'date': date,
                'total_students': len(attendance_data),
                'present_count': len([r for r in attendance_data if r['status'] == 'present'])
            }
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@faculty_bp.route('/assignments', methods=['GET'])
@jwt_required()
def get_assignments():
    """Get assignments created by faculty"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        subject_id = request.args.get('subject_id')
        
        # Mock assignments data - replace with actual database query
        assignments = [
            {
                'id': '1',
                'title': 'Database Design Project',
                'subject': 'Database Management Systems',
                'subject_id': '1',
                'due_date': '2024-01-20',
                'total_marks': 50,
                'submitted_count': 35,
                'total_students': 45,
                'status': 'active'
            },
            {
                'id': '2',
                'title': 'ER Diagram Creation',
                'subject': 'Database Management Systems',
                'subject_id': '1',
                'due_date': '2024-01-15',
                'total_marks': 20,
                'submitted_count': 42,
                'total_students': 45,
                'status': 'closed'
            }
        ]
        
        # Filter by subject if provided
        if subject_id:
            assignments = [a for a in assignments if a['subject_id'] == subject_id]
        
        return format_response(
            True,
            'Assignments retrieved successfully',
            200,
            {'assignments': assignments}
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@faculty_bp.route('/assignments', methods=['POST'])
@jwt_required()
def create_assignment():
    """Create new assignment"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        data = request.json
        
        required_fields = ['title', 'subject_id', 'due_date', 'total_marks', 'description']
        for field in required_fields:
            if field not in data:
                return format_response(False, f'Missing required field: {field}', 400)
        
        # Mock assignment creation - replace with actual database operations
        assignment_data = {
            'title': data['title'],
            'subject_id': data['subject_id'],
            'faculty_id': faculty_id,
            'due_date': data['due_date'],
            'total_marks': data['total_marks'],
            'description': data['description'],
            'instructions': data.get('instructions', ''),
            'attachments': data.get('attachments', []),
            'created_at': '2024-01-10T10:00:00Z',
            'status': 'active'
        }
        
        # Here you would save assignment to database
        # assignment_id = assignments_collection.insert_one(assignment_data).inserted_id
        
        return format_response(
            True,
            'Assignment created successfully',
            201,
            {'assignment': assignment_data}
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@faculty_bp.route('/grades', methods=['PUT'])
@jwt_required()
def update_grades():
    """Update student grades"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        data = request.json
        
        required_fields = ['assignment_id', 'grades']
        for field in required_fields:
            if field not in data:
                return format_response(False, f'Missing required field: {field}', 400)
        
        # Validate grades data
        grades = data['grades']  # List of {student_id, marks, feedback}
        for grade in grades:
            if 'student_id' not in grade or 'marks' not in grade:
                return format_response(False, 'Invalid grade data format', 400)
        
        # Mock grade update - replace with actual database operations
        assignment_id = data['assignment_id']
        
        # Here you would update grades in database
        # grades_collection.update_many([...])
        
        return format_response(
            True,
            'Grades updated successfully',
            200,
            {
                'assignment_id': assignment_id,
                'graded_count': len(grades)
            }
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@faculty_bp.route('/schedule', methods=['GET'])
@jwt_required()
def get_schedule():
    """Get faculty's class schedule"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        
        # Mock schedule data - replace with actual database query
        schedule = [
            {
                'day': 'Monday',
                'classes': [
                    {
                        'time': '10:00 AM - 11:00 AM',
                        'subject': 'Database Management Systems',
                        'subject_code': 'CS302',
                        'class': 'CS 5th Sem A',
                        'room': 'Lab 301',
                        'students_count': 45
                    },
                    {
                        'time': '4:00 PM - 5:00 PM',
                        'subject': 'Data Structures',
                        'subject_code': 'CS301',
                        'class': 'CS 3rd Sem A',
                        'room': 'Lab 205',
                        'students_count': 42
                    }
                ]
            },
            {
                'day': 'Tuesday',
                'classes': [
                    {
                        'time': '2:00 PM - 4:00 PM',
                        'subject': 'Software Engineering',
                        'subject_code': 'CS401',
                        'class': 'CS 7th Sem B',
                        'room': 'Room 205',
                        'students_count': 38
                    }
                ]
            },
            {
                'day': 'Wednesday',
                'classes': [
                    {
                        'time': '10:00 AM - 11:00 AM',
                        'subject': 'Database Management Systems',
                        'subject_code': 'CS302',
                        'class': 'CS 5th Sem A',
                        'room': 'Lab 301',
                        'students_count': 45
                    },
                    {
                        'time': '11:00 AM - 12:00 PM',
                        'subject': 'Web Technologies',
                        'subject_code': 'CS403',
                        'class': 'CS 7th Sem A',
                        'room': 'Lab 302',
                        'students_count': 35
                    }
                ]
            },
            {
                'day': 'Thursday',
                'classes': [
                    {
                        'time': '2:00 PM - 4:00 PM',
                        'subject': 'Software Engineering',
                        'subject_code': 'CS401',
                        'class': 'CS 7th Sem B',
                        'room': 'Room 205',
                        'students_count': 38
                    }
                ]
            },
            {
                'day': 'Friday',
                'classes': [
                    {
                        'time': '10:00 AM - 11:00 AM',
                        'subject': 'Database Management Systems',
                        'subject_code': 'CS302',
                        'class': 'CS 5th Sem A',
                        'room': 'Lab 301',
                        'students_count': 45
                    },
                    {
                        'time': '11:00 AM - 12:00 PM',
                        'subject': 'Web Technologies',
                        'subject_code': 'CS403',
                        'class': 'CS 7th Sem A',
                        'room': 'Lab 302',
                        'students_count': 35
                    }
                ]
            }
        ]
        
        return format_response(
            True,
            'Schedule retrieved successfully',
            200,
            {'schedule': schedule}
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@faculty_bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    """Get faculty events and announcements"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        
        # Mock events data - replace with actual database query
        events = [
            {
                'id': '1',
                'title': 'Faculty Meeting',
                'description': 'Monthly department meeting to discuss academic progress',
                'date': '2024-01-20',
                'time': '3:00 PM',
                'location': 'Conference Room A',
                'type': 'meeting',
                'priority': 'high'
            },
            {
                'id': '2',
                'title': 'Mid-term Exam Schedule Release',
                'description': 'Exam schedule for 5th and 7th semester students',
                'date': '2024-01-18',
                'time': '10:00 AM',
                'location': 'Notice Board',
                'type': 'announcement',
                'priority': 'medium'
            },
            {
                'id': '3',
                'title': 'Research Paper Submission Deadline',
                'description': 'Last date for submitting research papers for international conference',
                'date': '2024-01-25',
                'time': '5:00 PM',
                'location': 'Online Portal',
                'type': 'deadline',
                'priority': 'high'
            }
        ]
        
        return format_response(
            True,
            'Events retrieved successfully',
            200,
            {'events': events}
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)

@faculty_bp.route('/resources', methods=['GET'])
@jwt_required()
def get_resources():
    """Get teaching resources and materials"""
    try:
        # Verify user type
        jwt_data = get_jwt()
        if jwt_data.get('user_type') != 'faculty':
            return format_response(False, 'Access denied', 403)
        
        faculty_id = get_jwt_identity()
        
        # Mock resources data - replace with actual database query
        resources = [
            {
                'id': '1',
                'title': 'Database Design Templates',
                'description': 'ER diagram templates and database design guidelines',
                'type': 'template',
                'subject': 'CS302',
                'upload_date': '2024-01-10',
                'file_size': '2.5 MB',
                'downloads': 45
            },
            {
                'id': '2',
                'title': 'Software Engineering Methodology Guide',
                'description': 'Complete guide to software development methodologies',
                'type': 'guide',
                'subject': 'CS401',
                'upload_date': '2024-01-08',
                'file_size': '5.2 MB',
                'downloads': 38
            },
            {
                'id': '3',
                'title': 'Data Structures Algorithm Examples',
                'description': 'Implementation examples for common data structures',
                'type': 'example',
                'subject': 'CS301',
                'upload_date': '2024-01-05',
                'file_size': '3.8 MB',
                'downloads': 42
            }
        ]
        
        return format_response(
            True,
            'Resources retrieved successfully',
            200,
            {'resources': resources}
        )
        
    except Exception as e:
        return format_response(False, str(e), 500)