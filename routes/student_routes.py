"""
Student Routes for GEC Rajkot Website
Handles student-specific API endpoints
Author: GEC Rajkot Development Team
"""

from flask import Blueprint, request, jsonify, current_app, session
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from datetime import datetime
from functools import wraps

# Import models (will be available once database is set up)
# from models import Student
# from database import db

student_bp = Blueprint('student', __name__, url_prefix='/api/student')

def get_current_user_email():
    """Get current user email from JWT or session"""
    try:
        # Try JWT first
        email = get_jwt_identity()
        if email:
            return email
    except Exception:
        pass
    
    # Fall back to session
    return session.get('user_email')

def get_current_student_id():
    """Get current student ID from session or by looking up email"""
    # Try session first
    if 'user_id' in session and session.get('user_type') == 'student':
        return session['user_id']
    
    # Try to get from JWT and look up in database
    try:
        email = get_jwt_identity()
        if email:
            from models.gecr_models import Student
            student = Student.find_by_email(email)
            return student.student_id if student else None
    except Exception:
        pass
    
    return None

def require_student_auth():
    """
    Decorator to ensure the current user is authenticated as student.
    Supports both JWT tokens and session-based authentication.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Try JWT first
            try:
                verify_jwt_in_request(optional=True)
                claims = get_jwt()
                if claims and claims.get('user_type') == 'student':
                    return f(*args, **kwargs)
            except Exception:
                pass
            
            # Fall back to session-based auth
            if 'user_id' in session and session.get('user_type') == 'student':
                return f(*args, **kwargs)
            
            return jsonify({'error': 'Student authentication required'}), 401
        return wrapper
    return decorator

@student_bp.route('/dashboard', methods=['GET'])

@require_student_auth()
def get_dashboard():
    """
    Get student dashboard data
    Returns overview information for the student dashboard
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Student dashboard endpoint ready',
            'email': current_user_email,
            'dashboard_data': {
                'quick_stats': {
                    'attendance_percentage': 85.5,
                    'assignments_pending': 3,
                    'upcoming_exams': 2,
                    'total_subjects': 6
                },
                'recent_activities': [
                    {
                        'type': 'assignment',
                        'title': 'Math Assignment 3',
                        'due_date': '2024-01-15',
                        'status': 'pending'
                    },
                    {
                        'type': 'attendance',
                        'title': 'Physics Lab',
                        'date': '2024-01-10',
                        'status': 'present'
                    }
                ],
                'announcements': [
                    {
                        'title': 'Mid-term Exam Schedule Released',
                        'date': '2024-01-08',
                        'priority': 'high'
                    }
                ]
            },
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
        # Uncomment when models are available:
        """
        student = Student.find_by_email(current_user_email)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get dashboard data
        dashboard_data = {
            'student_info': student.to_dict(),
            'quick_stats': {
                'attendance_percentage': student.get_attendance_percentage(),
                'assignments_pending': student.get_pending_assignments_count(),
                'upcoming_exams': student.get_upcoming_exams_count(),
                'total_subjects': student.get_enrolled_subjects_count()
            },
            'recent_activities': student.get_recent_activities(),
            'announcements': student.get_announcements(),
            'schedule': student.get_today_schedule()
        }
        
        return jsonify(dashboard_data), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Student dashboard error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/profile', methods=['GET'])
@require_student_auth()
def get_profile():
    """
    Get student profile information with enrolled subjects
    """
    try:
        from database import db
        from models.gecr_models import Student, StudentEnrollment
        
        current_user_email = get_current_user_email()
        student = Student.find_by_email(current_user_email) if current_user_email else None
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get student dict
        student_dict = student.to_dict()
        
        # Get enrolled subjects
        enrolled_subjects = student.get_enrolled_subjects()
        student_dict['enrolled_subjects'] = [
            {
                'subject_id': subj.subject_id,
                'subject_name': subj.subject_name,
                'department': subj.department,
                'semester': subj.semester,
                'faculty_name': subj.faculty.name if subj.faculty else None
            }
            for subj in enrolled_subjects
        ]
        
        return jsonify(student_dict), 200
        
    except Exception as e:
        current_app.logger.error(f"Student profile error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/profile', methods=['PUT'])

@require_student_auth()
def update_profile():
    """
    Update student profile information
    """
    try:
        current_user_email = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate updateable fields
        allowed_fields = [
            'first_name', 'last_name', 'phone', 'address', 'blood_group',
            'guardian_name', 'guardian_phone', 'emergency_contact'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Student profile update endpoint ready',
            'email': current_user_email,
            'update_data': update_data,
            'note': 'Database models not yet connected'
        }), 200
        
        # Uncomment when models are available:
        """
        student = Student.find_by_email(current_user_email)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        student.update_from_dict(update_data)
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'student': student.to_dict()
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Student profile update error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/attendance', methods=['GET'])
@require_student_auth()
def get_attendance():
    """
    Get student attendance records with percentage by subject
    Query parameters: subject_id, start_date, end_date
    """
    try:
        from database import db
        from models.gecr_models import Student, Attendance, Subject, StudentEnrollment
        from datetime import datetime, timedelta
        
        current_user_email = get_current_user_email()
        student = Student.find_by_email(current_user_email) if current_user_email else None
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get query parameters
        subject_id = request.args.get('subject_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Attendance.query.filter_by(student_id=student.student_id)
        
        # Filter by subject
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        # Filter by date range
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date >= start)
            except:
                pass
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date <= end)
            except:
                pass
        
        # Get attendance records
        attendance_records = query.order_by(Attendance.date.desc()).all()
        
        # Group by subject and calculate percentages
        subject_attendance = {}
        
        for record in attendance_records:
            subject_id_key = record.subject_id
            if subject_id_key not in subject_attendance:
                subject = Subject.query.get(subject_id_key)
                subject_attendance[subject_id_key] = {
                    'subject_id': subject_id_key,
                    'subject_name': subject.subject_name if subject else 'Unknown',
                    'total_classes': 0,
                    'present_count': 0,
                    'absent_count': 0,
                    'late_count': 0,
                    'attendance_percentage': 0,
                    'records': []
                }
            
            subject_attendance[subject_id_key]['total_classes'] += 1
            
            if record.status == 'Present':
                subject_attendance[subject_id_key]['present_count'] += 1
            elif record.status == 'Absent':
                subject_attendance[subject_id_key]['absent_count'] += 1
            elif record.status == 'Late':
                subject_attendance[subject_id_key]['late_count'] += 1
            
            subject_attendance[subject_id_key]['records'].append({
                'date': record.date.strftime('%Y-%m-%d'),
                'status': record.status,
                'attendance_id': record.attendance_id
            })
        
        # Calculate percentages
        for subj_data in subject_attendance.values():
            if subj_data['total_classes'] > 0:
                subj_data['attendance_percentage'] = round(
                    (subj_data['present_count'] / subj_data['total_classes']) * 100, 2
                )
        
        # Calculate overall attendance
        total_all = len(attendance_records)
        present_all = sum(1 for r in attendance_records if r.status == 'Present')
        overall_percentage = round((present_all / total_all * 100), 2) if total_all > 0 else 0
        
        return jsonify({
            'overall_attendance_percentage': overall_percentage,
            'total_classes_attended': total_all,
            'present_count': present_all,
            'by_subject': list(subject_attendance.values()),
            'recent_records': [
                {
                    'date': r.date.strftime('%Y-%m-%d'),
                    'subject_name': r.subject.subject_name if r.subject else 'Unknown',
                    'status': r.status
                }
                for r in attendance_records[:10]  # Last 10 records
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Student attendance error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500
        year = request.args.get('year')
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Student attendance endpoint ready',
            'email': current_user_email,
            'filters': {
                'subject_id': subject_id,
                'month': month,
                'year': year
            },
            'sample_attendance': [
                {
                    'date': '2024-01-10',
                    'subject': 'Mathematics',
                    'status': 'present',
                    'lecture_type': 'theory'
                },
                {
                    'date': '2024-01-09',
                    'subject': 'Physics',
                    'status': 'absent',
                    'lecture_type': 'lab'
                }
            ],
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
        # Uncomment when models are available:
        """
        student = Student.find_by_email(current_user_email)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get attendance records with filters
        attendance_records = student.get_attendance(
            subject_id=subject_id,
            month=month,
            year=year
        )
        
        # Calculate attendance summary
        attendance_summary = student.get_attendance_summary(
            subject_id=subject_id,
            month=month,
            year=year
        )
        
        return jsonify({
            'attendance_records': [record.to_dict() for record in attendance_records],
            'attendance_summary': attendance_summary
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Student attendance error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/subjects', methods=['GET'])
@require_student_auth()
def get_subjects():
    """
    Get student's enrolled subjects with attendance stats
    """
    try:
        from database import db
        from models.gecr_models import Student, StudentEnrollment, Attendance
        
        current_user_email = get_current_user_email()
        student = Student.find_by_email(current_user_email) if current_user_email else None
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get enrolled subjects
        enrollments = StudentEnrollment.query.filter_by(
            student_id=student.student_id,
            status='active'
        ).all()
        
        subjects_list = []
        for enrollment in enrollments:
            subject = enrollment.subject
            if not subject:
                continue
            
            # Calculate attendance for this subject
            total_classes = Attendance.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id
            ).count()
            
            present_count = Attendance.query.filter_by(
                student_id=student.student_id,
                subject_id=subject.subject_id,
                status='Present'
            ).count()
            
            attendance_percentage = round((present_count / total_classes * 100), 2) if total_classes > 0 else 0
            
            subjects_list.append({
                'id': subject.subject_id,  # Add 'id' field
                'subject_id': subject.subject_id,
                'subject_code': subject.subject_code,  # Add subject_code
                'subject_name': subject.subject_name,
                'department': subject.department,
                'semester': subject.semester,
                'faculty_id': subject.faculty_id,
                'faculty_name': subject.faculty.name if subject.faculty else None,
                'enrollment_date': enrollment.enrollment_date.strftime('%Y-%m-%d') if enrollment.enrollment_date else None,
                'total_classes': total_classes,
                'present_count': present_count,
                'attendance_percentage': attendance_percentage
            })
        
        return jsonify(subjects_list), 200  # Return array directly
        
    except Exception as e:
        current_app.logger.error(f"Student subjects error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/assignments', methods=['GET'])
@require_student_auth()
def get_assignments():
    """
    Get student assignments
    Query parameters: status, subject_id, due_date
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Get query parameters
        status = request.args.get('status')  # pending, submitted, graded
        subject_id = request.args.get('subject_id')
        due_date = request.args.get('due_date')
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Student assignments endpoint ready',
            'email': current_user_email,
            'filters': {
                'status': status,
                'subject_id': subject_id,
                'due_date': due_date
            },
            'sample_assignments': [
                {
                    'id': 1,
                    'title': 'Calculus Problem Set 3',
                    'subject': 'Mathematics',
                    'due_date': '2024-01-15',
                    'status': 'pending',
                    'max_marks': 50
                },
                {
                    'id': 2,
                    'title': 'Physics Lab Report',
                    'subject': 'Physics',
                    'due_date': '2024-01-12',
                    'status': 'submitted',
                    'max_marks': 25,
                    'obtained_marks': 22
                }
            ],
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
        # Uncomment when models are available:
        """
        student = Student.find_by_email(current_user_email)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get assignments with filters
        assignments = student.get_assignments(
            status=status,
            subject_id=subject_id,
            due_date=due_date
        )
        
        return jsonify({
            'assignments': [assignment.to_dict() for assignment in assignments]
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Student assignments error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/grades', methods=['GET'])

@require_student_auth()
def get_grades():
    """
    Get student grades and academic performance
    Query parameters: semester, subject_id, exam_type
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Get query parameters
        semester = request.args.get('semester')
        subject_id = request.args.get('subject_id')
        exam_type = request.args.get('exam_type')  # mid_term, final, assignment, etc.
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Student grades endpoint ready',
            'email': current_user_email,
            'filters': {
                'semester': semester,
                'subject_id': subject_id,
                'exam_type': exam_type
            },
            'sample_grades': {
                'current_semester': 3,
                'cgpa': 8.5,
                'semester_grades': [
                    {
                        'subject': 'Mathematics',
                        'mid_term': 42,
                        'final': 78,
                        'total': 120,
                        'grade': 'A'
                    },
                    {
                        'subject': 'Physics',
                        'mid_term': 38,
                        'final': 72,
                        'total': 110,
                        'grade': 'B+'
                    }
                ]
            },
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
        # Uncomment when models are available:
        """
        student = Student.find_by_email(current_user_email)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get grades with filters
        grades = student.get_grades(
            semester=semester,
            subject_id=subject_id,
            exam_type=exam_type
        )
        
        # Calculate academic summary
        academic_summary = student.get_academic_summary()
        
        return jsonify({
            'grades': [grade.to_dict() for grade in grades],
            'academic_summary': academic_summary
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Student grades error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/schedule', methods=['GET'])

@require_student_auth()
def get_schedule():
    """
    Get student class schedule
    Query parameters: date, week
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Get query parameters
        date = request.args.get('date')  # YYYY-MM-DD format
        week = request.args.get('week')  # week number
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Student schedule endpoint ready',
            'email': current_user_email,
            'filters': {
                'date': date,
                'week': week
            },
            'sample_schedule': {
                'today': [
                    {
                        'time': '09:00-10:00',
                        'subject': 'Mathematics',
                        'faculty': 'Dr. Smith',
                        'room': 'Room 101',
                        'type': 'lecture'
                    },
                    {
                        'time': '11:00-12:00',
                        'subject': 'Physics Lab',
                        'faculty': 'Prof. Johnson',
                        'room': 'Lab 202',
                        'type': 'practical'
                    }
                ],
                'week_schedule': {
                    'monday': [],
                    'tuesday': [],
                    'wednesday': [],
                    'thursday': [],
                    'friday': [],
                    'saturday': []
                }
            },
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
        # Uncomment when models are available:
        """
        student = Student.find_by_email(current_user_email)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        if date:
            schedule = student.get_schedule_by_date(date)
        elif week:
            schedule = student.get_schedule_by_week(week)
        else:
            schedule = student.get_current_week_schedule()
        
        return jsonify({
            'schedule': schedule
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Student schedule error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/events', methods=['GET'])

@require_student_auth()
def get_events():
    """
    Get college events and announcements for students
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Student events endpoint ready',
            'email': current_user_email,
            'sample_events': [
                {
                    'id': 1,
                    'title': 'Annual Tech Fest 2024',
                    'description': 'Join us for the biggest tech event of the year',
                    'date': '2024-02-15',
                    'time': '10:00 AM',
                    'venue': 'Main Auditorium',
                    'type': 'festival',
                    'registration_required': True
                },
                {
                    'id': 2,
                    'title': 'Career Guidance Session',
                    'description': 'Industry experts will guide on career opportunities',
                    'date': '2024-01-20',
                    'time': '2:00 PM',
                    'venue': 'Conference Hall',
                    'type': 'seminar',
                    'registration_required': False
                }
            ],
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Student events error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/resources', methods=['GET'])

@require_student_auth()
def get_resources():
    """
    Get academic resources for students (notes, materials, etc.)
    Query parameters: subject_id, resource_type
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Get query parameters
        subject_id = request.args.get('subject_id')
        resource_type = request.args.get('resource_type')  # notes, books, videos, etc.
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Student resources endpoint ready',
            'email': current_user_email,
            'filters': {
                'subject_id': subject_id,
                'resource_type': resource_type
            },
            'sample_resources': [
                {
                    'id': 1,
                    'title': 'Calculus Notes - Chapter 5',
                    'subject': 'Mathematics',
                    'type': 'notes',
                    'upload_date': '2024-01-08',
                    'uploaded_by': 'Dr. Smith',
                    'file_url': '/resources/math_ch5_notes.pdf'
                },
                {
                    'id': 2,
                    'title': 'Physics Reference Book',
                    'subject': 'Physics',
                    'type': 'book',
                    'upload_date': '2024-01-05',
                    'uploaded_by': 'Prof. Johnson',
                    'file_url': '/resources/physics_ref_book.pdf'
                }
            ],
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Student resources error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/announcements', methods=['GET'])
@require_student_auth()
def get_announcements():
    """
    Get announcements for students
    Returns active announcements created by faculty
    """
    try:
        from models.gecr_models import Announcement
        from datetime import datetime
        
        # Get announcements that haven't expired
        anns = Announcement.query.filter(
            (Announcement.expires_at.is_(None)) | 
            (Announcement.expires_at > datetime.utcnow())
        ).order_by(Announcement.created_at.desc()).limit(20).all()
        
        return jsonify({
            'announcements': [a.to_dict() for a in anns]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Student announcements error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/upcoming-events', methods=['GET'])
@require_student_auth()
def get_upcoming_events():
    """
    Get upcoming events for students
    Returns events that haven't occurred yet
    """
    try:
        from models.gecr_models import Event
        from datetime import datetime
        
        # Get upcoming events
        events = Event.query.filter(
            Event.start_time > datetime.utcnow()
        ).order_by(Event.start_time.asc()).limit(20).all()
        
        return jsonify({
            'events': [e.to_dict() for e in events]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Student events error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/events/<int:event_id>/register', methods=['POST'])
@require_student_auth()
def register_for_event(event_id):
    """Register the current student for an event"""
    try:
        from models.gecr_models import Event, EventRegistration, Student, Notification
        from database import db

        student_id = get_current_student_id()
        if not student_id:
            return jsonify({'error': 'Student not found or not authenticated'}), 401

        # Ensure event exists and is upcoming
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        from datetime import datetime
        if event.start_time and event.start_time <= datetime.utcnow():
            return jsonify({'error': 'Cannot register for past or ongoing events'}), 400

        # Prevent duplicate registration
        existing = EventRegistration.query.filter_by(event_id=event_id, student_id=student_id).first()
        if existing:
            return jsonify({'message': 'Already registered'}), 200

        # Create registration
        registration = EventRegistration(event_id=event_id, student_id=student_id)
        db.session.add(registration)
        db.session.commit()

        # Create notification for the faculty who created the event
        try:
            if event.created_by:
                student = Student.query.get(student_id)
                notif = Notification(
                    user_id=event.created_by,
                    user_type='faculty',
                    title=f"New RSVP for {event.title}",
                    message=f"{student.name} ({student.email}) registered for '{event.title}'",
                    notification_type='event_rsvp',
                    link=f"/faculty/events#{event.event_id}"
                )
                db.session.add(notif)
                db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to create faculty notification: {e}")

        return jsonify({'message': 'Registered successfully', 'registration_id': registration.registration_id}), 201

    except Exception as e:
        current_app.logger.error(f"Event registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/my-attendance', methods=['GET'])
@require_student_auth()
def get_my_attendance():
    """
    Get attendance records for the logged-in student
    Query parameters: subject_id, start_date, end_date
    """
    try:
        from models.gecr_models import Attendance, Subject
        from database import db
        
        student_id = get_current_student_id()
        if not student_id:
            return jsonify({'error': 'Student not found'}), 404
        
        subject_id = request.args.get('subject_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Attendance.query.filter_by(student_id=student_id)
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        attendance_records = query.order_by(Attendance.date.desc()).all()
        
        # Calculate statistics
        total = len(attendance_records)
        present = len([a for a in attendance_records if a.status == 'present'])
        percentage = (present / total * 100) if total > 0 else 0
        
        return jsonify({
            'attendance_records': [a.to_dict() for a in attendance_records],
            'statistics': {
                'total_classes': total,
                'present': present,
                'absent': total - present,
                'percentage': round(percentage, 2)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Student attendance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/recent-activities', methods=['GET'])
@require_student_auth()
def get_recent_activities():
    """
    Get recent activities (updates from faculty)
    """
    try:
        from models.gecr_models import Activity
        
        activities = Activity.query.order_by(
            Activity.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'activities': [a.to_dict() for a in activities]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Student activities error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/notifications', methods=['GET'])
@require_student_auth()
def get_notifications():
    """
    Get notifications for the student
    Query parameters: unread_only (boolean), limit (int)
    """
    try:
        from models.gecr_models import Notification
        
        student_id = get_current_student_id()
        if not student_id:
            return jsonify({'error': 'Student not found'}), 404
        
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 20))
        
        query = Notification.query.filter_by(
            user_id=student_id,
            user_type='student'
        )
        
        if unread_only:
            query = query.filter_by(read=False)
        
        notifications = query.order_by(
            Notification.created_at.desc()
        ).limit(limit).all()
        
        # Count unread notifications
        unread_count = Notification.query.filter_by(
            user_id=student_id,
            user_type='student',
            read=False
        ).count()
        
        return jsonify({
            'notifications': [n.to_dict() for n in notifications],
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get notifications error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/notifications/<int:notification_id>/mark-read', methods=['POST'])
@require_student_auth()
def mark_notification_read(notification_id):
    """
    Mark a notification as read
    """
    try:
        from models.gecr_models import Notification
        from database import db
        
        student_id = get_current_student_id()
        if not student_id:
            return jsonify({'error': 'Student not found'}), 404
        
        notification = Notification.query.filter_by(
            notification_id=notification_id,
            user_id=student_id,
            user_type='student'
        ).first()
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        notification.read = True
        db.session.commit()
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Mark notification read error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@student_bp.route('/notifications/mark-all-read', methods=['POST'])
@require_student_auth()
def mark_all_notifications_read():
    """
    Mark all notifications as read for the student
    """
    try:
        from models.gecr_models import Notification
        from database import db
        
        student_id = get_current_student_id()
        if not student_id:
            return jsonify({'error': 'Student not found'}), 404
        
        Notification.query.filter_by(
            user_id=student_id,
            user_type='student',
            read=False
        ).update({'read': True})
        
        db.session.commit()
        
        return jsonify({'message': 'All notifications marked as read'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Mark all notifications read error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Error handlers for the student blueprint
@student_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Student access required'}), 403