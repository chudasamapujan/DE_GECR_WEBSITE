"""
Faculty Routes for GEC Rajkot Website
Handles faculty-specific API endpoints
Author: GEC Rajkot Development Team
"""

from flask import Blueprint, request, jsonify, current_app, session
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from datetime import datetime
from functools import wraps

# Import models (will be available once database is set up)
# from models import Faculty, Student
# from database import db

faculty_bp = Blueprint('faculty', __name__, url_prefix='/api/faculty')

def create_notifications_for_students(title, message, notification_type, link=None):
    """
    Create notifications for all students
    """
    try:
        from models.gecr_models import Student, Notification
        from database import db
        
        # Get all students
        students = Student.query.all()
        
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
        
        # Bulk insert
        db.session.bulk_save_objects(notifications)
        db.session.commit()
        
        current_app.logger.info(f"Created {len(notifications)} notifications for {notification_type}")
        return len(notifications)
    except Exception as e:
        current_app.logger.error(f"Create notifications error: {str(e)}")
        return 0



# Email notification functions removed - no longer sending emails


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

def get_current_faculty_id():
    """Get current faculty ID from session or by looking up email"""
    # Try session first
    if 'user_id' in session and session.get('user_type') == 'faculty':
        return session['user_id']
    
    # Try to get from JWT and look up in database
    try:
        email = get_jwt_identity()
        if email:
            from models.gecr_models import Faculty
            faculty = Faculty.find_by_email(email)
            return faculty.faculty_id if faculty else None
    except Exception:
        pass
    
    return None

def require_faculty_auth():
    """
    Decorator to ensure the current user is authenticated as faculty.
    Supports both JWT tokens and session-based authentication.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Try JWT first
            try:
                verify_jwt_in_request(optional=True)
                claims = get_jwt()
                if claims and claims.get('user_type') == 'faculty':
                    current_app.logger.info(f"Faculty auth via JWT: {claims.get('sub')}")
                    return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.warning(f"JWT auth failed: {str(e)}")
            
            # Fall back to session-based auth
            if 'user_id' in session and session.get('user_type') == 'faculty':
                current_app.logger.info(f"Faculty auth via session: {session.get('user_id')}")
                return f(*args, **kwargs)
            
            current_app.logger.error(f"Faculty auth failed - session: {dict(session)}, JWT claims: {get_jwt() if hasattr(request, 'jwt') else 'none'}")
            return jsonify({'error': 'Faculty authentication required'}), 401
        return wrapper
    return decorator

@faculty_bp.route('/dashboard', methods=['GET'])
@require_faculty_auth()
def get_dashboard():
    """
    Get faculty dashboard data
    Returns overview information for the faculty dashboard
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Faculty dashboard endpoint ready',
            'email': current_user_email,
            'dashboard_data': {
                'quick_stats': {
                    'total_students': 120,
                    'subjects_taught': 3,
                    'pending_assignments': 15,
                    'attendance_today': 85
                },
                'recent_activities': [
                    {
                        'type': 'assignment',
                        'title': 'Assignment 3 submissions',
                        'count': 25,
                        'subject': 'Mathematics'
                    },
                    {
                        'type': 'attendance',
                        'title': 'Today\'s attendance marked',
                        'count': 42,
                        'subject': 'Physics'
                    }
                ],
                'upcoming_classes': [
                    {
                        'subject': 'Mathematics',
                        'time': '10:00 AM',
                        'room': 'Room 101',
                        'type': 'lecture'
                    },
                    {
                        'subject': 'Physics Lab',
                        'time': '2:00 PM',
                        'room': 'Lab 202',
                        'type': 'practical'
                    }
                ]
            },
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
        # Uncomment when models are available:
        """
        faculty = Faculty.find_by_email(current_user_email)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get dashboard data
        dashboard_data = {
            'faculty_info': faculty.to_dict(),
            'quick_stats': {
                'total_students': faculty.get_total_students(),
                'subjects_taught': len(faculty.get_subjects_taught()),
                'pending_assignments': faculty.get_pending_assignments_count(),
                'attendance_today': faculty.get_today_attendance_count()
            },
            'recent_activities': faculty.get_recent_activities(),
            'upcoming_classes': faculty.get_upcoming_classes(),
            'notifications': faculty.get_notifications()
        }
        
        return jsonify(dashboard_data), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Faculty dashboard error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/events/<int:event_id>/registrations', methods=['GET'])
@require_faculty_auth()
def get_event_registrations(event_id):
    """Get registrations for a specific event (faculty-only)"""
    try:
        from models.gecr_models import Event, EventRegistration

        faculty_id = get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not authenticated'}), 401

        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        if event.created_by != faculty_id:
            return jsonify({'error': 'Access denied'}), 403

        regs = EventRegistration.query.filter_by(event_id=event_id).order_by(EventRegistration.registered_at.desc()).all()

        return jsonify({'registrations': [r.to_dict() for r in regs]}), 200

    except Exception as e:
        current_app.logger.error(f"Get event registrations error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/notifications/unread-count', methods=['GET'])
@require_faculty_auth()
def faculty_unread_notifications_count():
    """Return unread notifications count for the logged-in faculty"""
    try:
        from models.gecr_models import Notification

        faculty_id = get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not authenticated'}), 401

        count = Notification.query.filter_by(user_id=faculty_id, user_type='faculty', read=False).count()
        return jsonify({'unread_count': count}), 200

    except Exception as e:
        current_app.logger.error(f"Faculty unread notifications error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/notifications', methods=['GET'])
@require_faculty_auth()
def faculty_get_notifications():
    """Return recent notifications for the logged-in faculty.
    Query params: limit (int, default 5), unread_only (bool)
    """
    try:
        from models.gecr_models import Notification

        faculty_id = get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not authenticated'}), 401

        limit = int(request.args.get('limit', 5))
        unread_only = request.args.get('unread_only', 'true').lower() in ('1', 'true', 'yes')

        query = Notification.query.filter_by(user_id=faculty_id, user_type='faculty')
        if unread_only:
            query = query.filter_by(read=False)

        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

        return jsonify({'notifications': [n.to_dict() for n in notifications]}), 200

    except Exception as e:
        current_app.logger.error(f"Get faculty notifications error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@faculty_bp.route('/profile', methods=['GET'])
@require_faculty_auth()
def get_profile():
    """
    Get faculty profile information
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Faculty profile endpoint ready',
            'email': current_user_email,
            'note': 'Database models not yet connected'
        }), 200
        
        # Uncomment when models are available:
        """
        faculty = Faculty.find_by_email(current_user_email)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        return jsonify({
            'faculty': faculty.to_dict()
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Faculty profile error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@faculty_bp.route('/profile', methods=['PUT'])
@require_faculty_auth()
def update_profile():
    """
    Update faculty profile information
    """
    try:
        current_user_email = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate updateable fields
        allowed_fields = [
            'first_name', 'last_name', 'phone', 'address', 'qualification',
            'specialization', 'experience_years', 'office_room', 'office_hours',
            'research_interests', 'publications', 'research_projects',
            'office_phone', 'personal_website', 'linkedin_profile'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Faculty profile update endpoint ready',
            'email': current_user_email,
            'update_data': update_data,
            'note': 'Database models not yet connected'
        }), 200
        
        # Uncomment when models are available:
        """
        faculty = Faculty.find_by_email(current_user_email)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        faculty.update_from_dict(update_data)
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'faculty': faculty.to_dict()
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Faculty profile update error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@faculty_bp.route('/subjects/<int:subject_id>/enrollments', methods=['GET'])
@require_faculty_auth()
def get_subject_enrollments(subject_id):
    """
    Get all students enrolled in a specific subject
    Faculty can only see enrollments for subjects they teach
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject, StudentEnrollment, Student
        
        current_user_email = get_current_user_email()
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        if not faculty_id:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get subject and verify faculty teaches it
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        if subject.faculty_id != faculty_id:
            return jsonify({'error': 'You are not authorized to view enrollments for this subject'}), 403
        
        # Get all enrollments for this subject
        enrollments = StudentEnrollment.query.filter_by(subject_id=subject_id).all()
        
        enrollment_list = []
        for enrollment in enrollments:
            enrollment_dict = enrollment.to_dict()
            # Add student details
            student = enrollment.student
            if student:
                enrollment_dict['student_email'] = student.email
                enrollment_dict['student_semester'] = student.semester
                enrollment_dict['student_department'] = student.department
            enrollment_list.append(enrollment_dict)
        
        return jsonify({
            'subject_id': subject_id,
            'subject_name': subject.subject_name,
            'total_enrollments': len(enrollment_list),
            'enrollments': enrollment_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get subject enrollments error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/subjects/<int:subject_id>/enrollments', methods=['POST'])
@require_faculty_auth()
def add_student_enrollment(subject_id):
    """
    Enroll a student in a subject
    Expected JSON: {"student_id": 1, "academic_year": "2024-2025"}
    or {"roll_no": "2020001", "academic_year": "2024-2025"}
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject, StudentEnrollment, Student
        
        current_user_email = get_current_user_email()
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        if not faculty_id:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get subject and verify faculty teaches it
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        if subject.faculty_id != faculty_id:
            return jsonify({'error': 'You are not authorized to manage enrollments for this subject'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get student by ID or roll number
        student = None
        if 'student_id' in data:
            student = Student.query.get(data['student_id'])
        elif 'roll_no' in data:
            student = Student.query.filter_by(roll_no=data['roll_no']).first()
        else:
            return jsonify({'error': 'student_id or roll_no required'}), 400
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Check if already enrolled
        existing = StudentEnrollment.query.filter_by(
            student_id=student.student_id,
            subject_id=subject_id
        ).first()
        
        if existing:
            if existing.status == 'active':
                return jsonify({'error': 'Student already enrolled in this subject'}), 400
            else:
                # Reactivate enrollment
                existing.status = 'active'
                existing.enrollment_date = datetime.utcnow()
                db.session.commit()
                return jsonify({
                    'message': 'Enrollment reactivated',
                    'enrollment': existing.to_dict()
                }), 200
        
        # Create new enrollment
        enrollment = StudentEnrollment(
            student_id=student.student_id,
            subject_id=subject_id,
            academic_year=data.get('academic_year', '2024-2025'),
            status='active'
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'message': 'Student enrolled successfully',
            'enrollment': enrollment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Add student enrollment error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@faculty_bp.route('/subjects/<int:subject_id>/enrollments/<int:enrollment_id>', methods=['DELETE'])
@require_faculty_auth()
def remove_student_enrollment(subject_id, enrollment_id):
    """
    Remove (deactivate) a student from a subject
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject, StudentEnrollment
        
        current_user_email = get_current_user_email()
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        if not faculty_id:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get subject and verify faculty teaches it
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        if subject.faculty_id != faculty_id:
            return jsonify({'error': 'You are not authorized to manage enrollments for this subject'}), 403
        
        # Get enrollment
        enrollment = StudentEnrollment.query.get(enrollment_id)
        if not enrollment or enrollment.subject_id != subject_id:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        # Deactivate instead of delete (preserve history)
        enrollment.status = 'dropped'
        db.session.commit()
        
        return jsonify({
            'message': 'Student removed from subject',
            'enrollment': enrollment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Remove student enrollment error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/subjects/<int:subject_id>/enrollments/bulk-upload', methods=['POST'])
@require_faculty_auth()
def bulk_upload_enrollments(subject_id):
    """
    Bulk upload students to a subject from Excel or CSV file
    Expects file with columns: enrollment_no or roll_no (required), name (optional)
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject, Student, StudentEnrollment
        from sqlalchemy import or_
        import pandas as pd
        from werkzeug.utils import secure_filename
        import os
        
        current_user_email = get_current_user_email()
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        if not faculty_id:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Verify faculty teaches this subject
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        if subject.faculty_id != faculty_id:
            return jsonify({'error': 'You are not authorized to manage enrollments for this subject'}), 403
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        allowed_extensions = {'.xlsx', '.xls', '.csv'}
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file format. Only Excel (.xlsx, .xls) and CSV (.csv) files are allowed'}), 400
        
        # Read file into pandas DataFrame
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'error': f'Failed to read file: {str(e)}'}), 400
        
        # Validate required columns
        enrollment_col = None
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ['enrollment_no', 'enrollment', 'enroll_no', 'roll_no', 'rollno', 'roll no']:
                enrollment_col = col
                break
        
        if not enrollment_col:
            return jsonify({'error': 'File must contain an "enrollment_no" or "roll_no" column'}), 400
        
        # Process enrollments
        added_count = 0
        skipped_count = 0
        not_found = []
        
        for index, row in df.iterrows():
            enrollment_no = str(row[enrollment_col]).strip()
            
            if pd.isna(enrollment_no) or not enrollment_no or enrollment_no.lower() == 'nan':
                continue
            
            # Find student by enrollment number
            student = Student.query.filter(
                or_(
                    Student.enrollment_no == enrollment_no,
                    Student.roll_no == enrollment_no
                )
            ).first()
            
            if not student:
                not_found.append(enrollment_no)
                continue
            
            # Check if already enrolled
            existing = StudentEnrollment.query.filter_by(
                student_id=student.student_id,
                subject_id=subject_id
            ).first()
            
            if existing:
                # If dropped, reactivate
                if existing.status == 'dropped':
                    existing.status = 'active'
                    added_count += 1
                else:
                    skipped_count += 1
                continue
            
            # Create new enrollment
            new_enrollment = StudentEnrollment(
                student_id=student.student_id,
                subject_id=subject_id,
                status='active'
            )
            db.session.add(new_enrollment)
            added_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'added': added_count,
            'skipped': skipped_count,
            'not_found': not_found,
            'message': f'Successfully added {added_count} students'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Bulk upload enrollments error: {str(e)}")
        return jsonify({'error': f'Failed to process upload: {str(e)}'}), 500


@faculty_bp.route('/enrollment-requests', methods=['GET'])
@require_faculty_auth()
def get_enrollment_requests():
    """
    Get all pending enrollment requests for faculty's subjects
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject, StudentEnrollment, Student
        
        current_user_email = get_current_user_email()
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        if not faculty_id:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get all subjects taught by this faculty
        faculty_subjects = Subject.query.filter_by(faculty_id=faculty_id).all()
        subject_ids = [s.subject_id for s in faculty_subjects]
        
        if not subject_ids:
            return jsonify({
                'success': True,
                'requests': [],
                'total_requests': 0
            }), 200
        
        # Get all pending enrollments for these subjects
        pending_enrollments = StudentEnrollment.query.filter(
            StudentEnrollment.subject_id.in_(subject_ids),
            StudentEnrollment.status == 'pending'
        ).all()
        
        requests_data = []
        for enrollment in pending_enrollments:
            student = enrollment.student
            subject = enrollment.subject
            
            requests_data.append({
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': student.name if student else 'Unknown',
                'student_roll_no': student.roll_no if student else 'N/A',
                'student_email': student.email if student else 'N/A',
                'student_department': student.department if student else 'N/A',
                'student_semester': student.semester if student else 'N/A',
                'subject_id': enrollment.subject_id,
                'subject_name': subject.subject_name if subject else 'Unknown',
                'subject_department': subject.department if subject else 'N/A',
                'subject_semester': subject.semester if subject else 'N/A',
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'status': enrollment.status
            })
        
        return jsonify({
            'success': True,
            'requests': requests_data,
            'total_requests': len(requests_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get enrollment requests error: {str(e)}")
        return jsonify({'error': f'Failed to fetch enrollment requests: {str(e)}'}), 500


@faculty_bp.route('/enrollment-requests/<int:enrollment_id>/approve', methods=['POST'])
@require_faculty_auth()
def approve_enrollment_request(enrollment_id):
    """
    Approve a pending enrollment request
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject, StudentEnrollment, Notification
        
        current_user_email = get_current_user_email()
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        if not faculty_id:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get enrollment
        enrollment = StudentEnrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'error': 'Enrollment request not found'}), 404
        
        # Verify faculty teaches this subject
        subject = Subject.query.get(enrollment.subject_id)
        if not subject or subject.faculty_id != faculty_id:
            return jsonify({'error': 'You are not authorized to approve this request'}), 403
        
        # Check if status is pending
        if enrollment.status != 'pending':
            return jsonify({'error': f'Enrollment is already {enrollment.status}'}), 400
        
        # Approve the enrollment
        enrollment.status = 'active'
        
        # Send notification to student
        notification = Notification(
            user_id=enrollment.student_id,
            user_type='student',
            title='Enrollment Approved',
            message=f'Your enrollment request for {subject.subject_name} has been approved by {faculty.name}.',
            notification_type='enrollment_approved',
            read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Enrollment request approved successfully',
            'enrollment': {
                'enrollment_id': enrollment.enrollment_id,
                'status': enrollment.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Approve enrollment error: {str(e)}")
        return jsonify({'error': f'Failed to approve enrollment: {str(e)}'}), 500


@faculty_bp.route('/enrollment-requests/<int:enrollment_id>/reject', methods=['POST'])
@require_faculty_auth()
def reject_enrollment_request(enrollment_id):
    """
    Reject a pending enrollment request
    Expects JSON: {"reason": "optional rejection reason"}
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject, StudentEnrollment, Notification
        
        current_user_email = get_current_user_email()
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        if not faculty_id:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get enrollment
        enrollment = StudentEnrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'error': 'Enrollment request not found'}), 404
        
        # Verify faculty teaches this subject
        subject = Subject.query.get(enrollment.subject_id)
        if not subject or subject.faculty_id != faculty_id:
            return jsonify({'error': 'You are not authorized to reject this request'}), 403
        
        # Check if status is pending
        if enrollment.status != 'pending':
            return jsonify({'error': f'Enrollment is already {enrollment.status}'}), 400
        
        # Get rejection reason if provided
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        # Reject the enrollment
        enrollment.status = 'rejected'
        
        # Send notification to student
        notification = Notification(
            user_id=enrollment.student_id,
            user_type='student',
            title='Enrollment Request Rejected',
            message=f'Your enrollment request for {subject.subject_name} has been rejected. Reason: {reason}',
            notification_type='enrollment_rejected',
            read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Enrollment request rejected',
            'enrollment': {
                'enrollment_id': enrollment.enrollment_id,
                'status': enrollment.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Reject enrollment error: {str(e)}")
        return jsonify({'error': f'Failed to reject enrollment: {str(e)}'}), 500


@faculty_bp.route('/students', methods=['GET'])
@require_faculty_auth()
def get_students():
    """
    Get students - optionally filtered by subject, semester, or search query
    Query parameters: subject_id, semester, search
    """
    try:
        from database import db
        from models.gecr_models import Student, StudentEnrollment, Subject
        
        current_app.logger.info("=== Faculty Students API Called ===")
        current_user_email = get_current_user_email()
        current_app.logger.info(f"User: {current_user_email}")
        
        # Get query parameters
        subject_id = request.args.get('subject_id', type=int)
        semester = request.args.get('semester', type=int)
        search = request.args.get('search', '')
        current_app.logger.info(f"Params: subject_id={subject_id}, semester={semester}, search={search}")
        
        # Build query
        query = Student.query
        
        # Filter by subject enrollment if subject_id provided
        if subject_id:
            # Get students enrolled in this subject
            enrolled_student_ids = db.session.query(StudentEnrollment.student_id).filter_by(
                subject_id=subject_id,
                status='active'
            ).all()
            enrolled_ids = [sid[0] for sid in enrolled_student_ids]
            query = query.filter(Student.student_id.in_(enrolled_ids))
        
        # Filter by semester
        if semester:
            query = query.filter_by(semester=semester)
        
        # Search by name, roll_no, or email
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Student.name.ilike(search_pattern),
                    Student.roll_no.ilike(search_pattern),
                    Student.email.ilike(search_pattern)
                )
            )
        
        students = query.order_by(Student.name).all()
        current_app.logger.info(f"Found {len(students)} students")
        
        # Get attendance percentage for each student
        student_list = []
        for idx, student in enumerate(students):
            try:
                current_app.logger.info(f"Processing student {idx+1}/{len(students)}: {student.name}")
                student_dict = student.to_dict()
                
                # Calculate attendance percentage using proper ORM
                from models.gecr_models import Attendance
                
                # Simpler query that works across SQLAlchemy versions
                # Get unique class dates for this student
                total_classes_query = db.session.query(
                    Attendance.subject_id,
                    Attendance.date
                ).filter(
                    Attendance.student_id == student.student_id
                ).distinct()
                
                total_classes = total_classes_query.count()
                
                present_count = db.session.query(db.func.count(Attendance.attendance_id)).filter(
                    Attendance.student_id == student.student_id,
                    Attendance.status == 'present'
                ).scalar() or 0
                
                attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
                student_dict['attendance_percentage'] = round(attendance_percentage, 2)
                
                # Get enrolled subjects count
                enrolled_count = StudentEnrollment.query.filter_by(
                    student_id=student.student_id,
                    status='active'
                ).count()
                student_dict['enrolled_subjects_count'] = enrolled_count
                
                student_list.append(student_dict)
                
            except Exception as student_error:
                current_app.logger.error(f"Error processing student {student.name}: {str(student_error)}")
                import traceback
                traceback.print_exc()
                # Continue with other students
        
        current_app.logger.info(f"Successfully processed {len(student_list)} students")
        return jsonify(student_list), 200
        
    except Exception as e:
        current_app.logger.error(f"Faculty students error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@faculty_bp.route('/students', methods=['POST'])
@require_faculty_auth()
def add_student():
    """
    Add a new student manually
    Expected JSON: {
        "roll_no": "2020001",
        "name": "John Doe",
        "email": "john@student.gecr.edu",
        "password": "password123",
        "department": "Computer Engineering",
        "semester": 5,
        "phone": "1234567890"
    }
    """
    try:
        from database import db
        from models.gecr_models import Student, Notification
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['roll_no', 'name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if student already exists
        existing_student = Student.query.filter(
            db.or_(
                Student.roll_no == data['roll_no'],
                Student.email == data['email']
            )
        ).first()
        
        if existing_student:
            return jsonify({'error': 'Student with this roll number or email already exists'}), 400
        
        # Create new student
        student = Student(
            roll_no=data['roll_no'],
            name=data['name'],
            email=data['email'],
            department=data.get('department'),
            semester=data.get('semester'),
            phone=data.get('phone'),
            email_notifications_enabled=data.get('email_notifications_enabled', True)
        )
        student.set_password(data['password'])
        
        db.session.add(student)
        db.session.commit()
        
        # Create welcome notification
        try:
            notification = Notification(
                user_id=student.student_id,
                user_type='student',
                title='Welcome to GEC Rajkot!',
                message=f'Welcome {student.name}! Your account has been created successfully. Your roll number is {student.roll_no}.',
                notification_type='system',
                link='/student/profile'
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to create welcome notification: {e}")
        
        return jsonify({
            'message': 'Student added successfully',
            'student': student.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Add student error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@faculty_bp.route('/students/upload', methods=['POST'])
@require_faculty_auth()
def upload_students_excel():
    """
    Upload multiple students from Excel file
    Expected form data:
        - file: Excel file (.xlsx or .xls)
    
    Excel format:
        - Columns: Roll No, Name, Email, Password, Department, Semester, Phone
    """
    try:
        import os
        from werkzeug.utils import secure_filename
        from database import db
        from models.gecr_models import Student, Notification, Faculty
        
        # Get current faculty for activity logging
        current_user_email = get_current_user_email()
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        allowed_extensions = {'.xlsx', '.xls'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file format. Please upload .xlsx or .xls file'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_dir = os.path.join(current_app.root_path, 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_path = os.path.join(temp_dir, f"students_{datetime.now().timestamp()}_{filename}")
        file.save(temp_path)
        
        try:
            # Parse Excel file
            from utils.student_parser import parse_students_excel
            result = parse_students_excel(temp_path)
            
            if result['errors']:
                return jsonify({
                    'error': 'Errors found in Excel file',
                    'details': result['errors']
                }), 400
            
            students_data = result.get('students', [])
            if not students_data:
                return jsonify({'error': 'No student records found in Excel file'}), 400
            
            # Create students
            created_students = []
            skipped = []
            errors = []
            
            for student_data in students_data:
                try:
                    # Check if student already exists
                    existing = Student.query.filter(
                        db.or_(
                            Student.roll_no == student_data['roll_no'],
                            Student.email == student_data['email']
                        )
                    ).first()
                    
                    if existing:
                        skipped.append({
                            'roll_no': student_data['roll_no'],
                            'reason': 'Already exists'
                        })
                        continue
                    
                    # Create student
                    student = Student(
                        roll_no=student_data['roll_no'],
                        name=student_data['name'],
                        email=student_data['email'],
                        department=student_data.get('department'),
                        semester=student_data.get('semester'),
                        phone=student_data.get('phone'),
                        email_notifications_enabled=True
                    )
                    student.set_password(student_data.get('password', 'student123'))
                    
                    db.session.add(student)
                    db.session.flush()  # Get student_id
                    
                    # Create welcome notification
                    notification = Notification(
                        user_id=student.student_id,
                        user_type='student',
                        title='Welcome to GEC Rajkot!',
                        message=f'Welcome {student.name}! Your account has been created. Roll No: {student.roll_no}',
                        notification_type='system',
                        link='/student/profile'
                    )
                    db.session.add(notification)
                    
                    created_students.append(student.to_dict())
                    
                except Exception as e:
                    errors.append({
                        'roll_no': student_data.get('roll_no', 'Unknown'),
                        'error': str(e)
                    })
            
            db.session.commit()
            
            # Log activity
            if faculty_id:
                try:
                    from models.gecr_models import Activity
                    activity = Activity(
                        type='student_upload',
                        title='Students uploaded from Excel',
                        details=f'Created {len(created_students)} students, Skipped {len(skipped)}, Errors {len(errors)}',
                        created_by=faculty_id
                    )
                    db.session.add(activity)
                    db.session.commit()
                except:
                    pass
            
            return jsonify({
                'message': 'Students upload completed',
                'created': len(created_students),
                'skipped': len(skipped),
                'errors': len(errors),
                'students': created_students,
                'skipped_details': skipped,
                'error_details': errors
            }), 200
            
        finally:
            # Clean up temp file
            try:
                os.remove(temp_path)
            except Exception as e:
                current_app.logger.error(f"Failed to remove temp file: {e}")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Students upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@faculty_bp.route('/attendance', methods=['GET'])
@require_faculty_auth()
def get_attendance():
    """
    Get attendance records for faculty's classes
    Query parameters: subject_id, date, semester
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Get query parameters
        subject_id = request.args.get('subject_id')
        date = request.args.get('date')
        semester = request.args.get('semester')
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Faculty attendance view endpoint ready',
            'email': current_user_email,
            'filters': {
                'subject_id': subject_id,
                'date': date,
                'semester': semester
            },
            'sample_attendance': {
                'class_info': {
                    'subject': 'Mathematics',
                    'date': '2024-01-10',
                    'total_students': 45,
                    'present': 38,
                    'absent': 7
                },
                'attendance_list': [
                    {
                        'student_id': 1,
                        'enrollment_number': 'CS2021001',
                        'name': 'John Doe',
                        'status': 'present'
                    },
                    {
                        'student_id': 2,
                        'enrollment_number': 'CS2021002',
                        'name': 'Jane Smith',
                        'status': 'absent'
                    }
                ]
            },
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Faculty attendance view error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@faculty_bp.route('/attendance', methods=['POST'])
@require_faculty_auth()
def mark_attendance():
    """
    Mark attendance for a class
    Expected JSON: {
        "subject_id": 1,
        "date": "2024-01-10",
        "attendance_data": [
            {"student_id": 1, "status": "present"},
            {"student_id": 2, "status": "absent"}
        ]
    }
    """
    try:
        current_user_email = get_current_user_email()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        subject_id = data.get('subject_id')
        date = data.get('date')
        attendance_data = data.get('attendance_data', [])
        
        # Validate required fields
        if not all([subject_id, date, attendance_data]):
            return jsonify({'error': 'Subject ID, date, and attendance data are required'}), 400
        
        # Persist attendance records using Attendance model
        from database import db
        from models.gecr_models import Faculty, Attendance, Student

        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not found'}), 404

        # Very basic save loop (could be optimized/batched)
        marked = 0
        errors = []
        for entry in attendance_data:
            sid = entry.get('student_id')
            status = entry.get('status')
            try:
                # Ensure student exists
                student = Student.query.get(sid)
                if not student:
                    errors.append({'student_id': sid, 'error': 'Student not found'})
                    continue

                att = Attendance(student_id=sid, subject_id=subject_id, date=datetime.fromisoformat(date).date() if 'T' not in date and ' ' not in date else datetime.fromisoformat(date), status=status)
                db.session.add(att)
                marked += 1
            except Exception as e:
                errors.append({'student_id': sid, 'error': str(e)})

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to commit attendance: {e}")
            return jsonify({'error': 'Failed to save attendance', 'details': str(e)}), 500

        # Record an activity
        try:
            from models.gecr_models import Activity
            act = Activity(type='attendance', title=f'Attendance marked for subject {subject_id} on {date}', details=f'Marked {marked} students', created_by=faculty_id)
            db.session.add(act)
            db.session.commit()
        except Exception:
            db.session.rollback()

        return jsonify({
            'message': 'Attendance marked successfully',
            'subject_id': subject_id,
            'date': date,
            'students_marked': marked,
            'errors': errors
        }), 200
        
        # Uncomment when models are available:
        """
        faculty = Faculty.find_by_email(current_user_email)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Verify faculty teaches this subject
        if not faculty.teaches_subject(subject_id):
            return jsonify({'error': 'You are not authorized to mark attendance for this subject'}), 403
        
        # Mark attendance
        result = faculty.mark_attendance(subject_id, date, attendance_data)
        
        return jsonify({
            'message': 'Attendance marked successfully',
            'marked_count': result['marked_count'],
            'errors': result.get('errors', [])
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Attendance marking error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@faculty_bp.route('/attendance/upload', methods=['POST'])
@require_faculty_auth()
def upload_attendance_excel():
    """
    Upload attendance data from Excel file
    Expected form data:
        - file: Excel file (.xlsx or .xls)
        - subject_id: Subject ID for which attendance is being marked
    
    Excel format:
        - First row: Roll No, [Date1], [Date2], ...
        - Each row: student roll number, attendance status (P/A/L)
    """
    try:
        import os
        from werkzeug.utils import secure_filename
        from database import db
        from models.gecr_models import Faculty, Attendance, Student
        from utils.excel_parser import parse_attendance_excel
        
        # Get current faculty
        current_user_email = get_current_user_email()
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        if not faculty_id:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        allowed_extensions = {'.xlsx', '.xls'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file format. Please upload .xlsx or .xls file'}), 400
        
        # Get subject_id from form data
        subject_id = request.form.get('subject_id')
        if not subject_id:
            return jsonify({'error': 'Subject ID is required'}), 400
        
        try:
            subject_id = int(subject_id)
        except ValueError:
            return jsonify({'error': 'Invalid subject ID'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_dir = os.path.join(current_app.root_path, 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_path = os.path.join(temp_dir, f"{faculty_id}_{datetime.now().timestamp()}_{filename}")
        file.save(temp_path)
        
        try:
            # Parse Excel file
            result = parse_attendance_excel(temp_path)
            
            if result['errors']:
                return jsonify({
                    'error': 'Errors found in Excel file',
                    'details': result['errors'],
                    'dates_found': [d.strftime('%Y-%m-%d') for d in result.get('dates', [])]
                }), 400
            
            records = result.get('records', [])
            if not records:
                return jsonify({'error': 'No attendance records found in Excel file'}), 400
            
            # Map roll numbers to student IDs and validate enrollment
            roll_numbers = list(set([r['student_roll_no'] for r in records]))
            students_dict = {}
            not_enrolled = []
            
            # Import StudentEnrollment model
            from models.gecr_models import StudentEnrollment, Subject
            
            # Verify faculty teaches this subject
            subject = Subject.query.get(subject_id)
            if not subject:
                return jsonify({'error': 'Subject not found'}), 404
            
            if subject.faculty_id != faculty_id:
                return jsonify({'error': 'You are not authorized to mark attendance for this subject'}), 403
            
            for roll_no in roll_numbers:
                student = Student.query.filter_by(roll_no=roll_no).first()
                if student:
                    # Check if student is enrolled in this subject
                    enrollment = StudentEnrollment.query.filter_by(
                        student_id=student.student_id,
                        subject_id=subject_id,
                        status='active'
                    ).first()
                    
                    if enrollment:
                        students_dict[roll_no] = student.student_id
                    else:
                        not_enrolled.append(roll_no)
                        current_app.logger.warning(f"Student {roll_no} not enrolled in subject {subject_id}")
                else:
                    current_app.logger.warning(f"Student with roll number {roll_no} not found")
            
            # Create attendance records
            attendance_objects = []
            skipped = 0
            not_enrolled_count = len(not_enrolled)
            
            for record in records:
                roll_no = record['student_roll_no']
                if roll_no not in students_dict:
                    skipped += 1
                    continue
                
                # Check if attendance already exists for this student, subject, and date
                existing = Attendance.query.filter_by(
                    student_id=students_dict[roll_no],
                    subject_id=subject_id,
                    date=record['date']
                ).first()
                
                if existing:
                    # Update existing record
                    existing.status = record['status']
                else:
                    # Create new record
                    att = Attendance(
                        student_id=students_dict[roll_no],
                        subject_id=subject_id,
                        date=record['date'],
                        status=record['status']
                    )
                    attendance_objects.append(att)
            
            # Bulk insert new records
            if attendance_objects:
                db.session.bulk_save_objects(attendance_objects)
            
            db.session.commit()
            
            # Create activity log
            try:
                from models.gecr_models import Activity
                dates_str = ', '.join([d.strftime('%Y-%m-%d') for d in result['dates']])
                activity = Activity(
                    type='attendance_upload',
                    title=f'Attendance uploaded for subject {subject_id}',
                    details=f'Uploaded {len(attendance_objects)} records for dates: {dates_str}',
                    created_by=faculty_id
                )
                db.session.add(activity)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Failed to log activity: {e}")
            
            return jsonify({
                'message': 'Attendance uploaded successfully',
                'records_inserted': len(attendance_objects),
                'records_updated': result['total_records'] - len(attendance_objects) - skipped - not_enrolled_count,
                'records_skipped': skipped,
                'not_enrolled': not_enrolled_count,
                'not_enrolled_students': not_enrolled if not_enrolled else [],
                'dates': [d.strftime('%Y-%m-%d') for d in result['dates']],
                'total_students': len(students_dict),
                'subject_id': subject_id,
                'subject_name': subject.subject_name
            }), 200
            
        finally:
            # Clean up temp file
            try:
                os.remove(temp_path)
            except Exception as e:
                current_app.logger.error(f"Failed to remove temp file: {e}")
        
    except Exception as e:
        current_app.logger.error(f"Attendance upload error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@faculty_bp.route('/assignments', methods=['GET'])
@require_faculty_auth()
def get_assignments():
    """
    Get assignments created by faculty
    Query parameters: subject_id, status
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Get query parameters
        subject_id = request.args.get('subject_id')
        status = request.args.get('status')  # active, closed, graded
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Faculty assignments endpoint ready',
            'email': current_user_email,
            'filters': {
                'subject_id': subject_id,
                'status': status
            },
            'sample_assignments': [
                {
                    'id': 1,
                    'title': 'Calculus Problem Set 3',
                    'subject': 'Mathematics',
                    'due_date': '2024-01-15',
                    'max_marks': 50,
                    'submissions': 25,
                    'total_students': 45,
                    'status': 'active'
                },
                {
                    'id': 2,
                    'title': 'Physics Lab Report',
                    'subject': 'Physics',
                    'due_date': '2024-01-12',
                    'max_marks': 25,
                    'submissions': 42,
                    'total_students': 42,
                    'status': 'graded'
                }
            ],
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Faculty assignments error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/announcements', methods=['POST'])
@require_faculty_auth()
def create_announcement():
    try:
        current_user_email = get_current_user_email()
        data = request.get_json() or {}
        title = data.get('title')
        message = data.get('message')
        expires_at_str = data.get('expires_at')
        
        if not title or not message:
            return jsonify({'error': 'Title and message are required'}), 400

        from database import db
        from models.gecr_models import Faculty, Announcement
        from datetime import datetime
        
        faculty = Faculty.find_by_email(current_user_email) if current_user_email else None
        author_id = faculty.faculty_id if faculty else get_current_faculty_id()

        # Parse expires_at if provided
        expires_at = None
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            except:
                pass

        ann = Announcement(
            title=title, 
            message=message, 
            author_id=author_id,
            expires_at=expires_at
        )
        db.session.add(ann)
        db.session.commit()

        # Create in-app notifications for all students
        notif_count = create_notifications_for_students(
            title=f"📢 New Announcement: {title}",
            message=message[:200],  # Truncate long messages
            notification_type='announcement',
            link='/student/dashboard'
        )

        # Email notifications removed - no longer sending emails

        return jsonify({'message': 'Announcement created', 'announcement_id': ann.announcement_id, 'announcement': ann.to_dict()}), 201

    except Exception as e:
        current_app.logger.error(f"Create announcement error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/announcements', methods=['GET'])
@require_faculty_auth()
def list_announcements():
    try:
        from models.gecr_models import Announcement
        anns = Announcement.query.order_by(Announcement.created_at.desc()).limit(50).all()
        return jsonify({'announcements': [a.to_dict() for a in anns]}), 200
    except Exception as e:
        current_app.logger.error(f"List announcements error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/announcements/<int:announcement_id>', methods=['PUT'])
@require_faculty_auth()
def update_announcement(announcement_id):
    """
    Update an existing announcement
    """
    try:
        from database import db
        from models.gecr_models import Announcement, Faculty
        
        user_email = get_current_user_email()
        faculty = Faculty.find_by_email(user_email) if user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Check if faculty is the author
        if announcement.author_id != faculty_id:
            return jsonify({'error': 'Unauthorized - You can only edit your own announcements'}), 403
        
        data = request.get_json() or {}
        
        # Update fields
        if 'title' in data:
            announcement.title = data['title']
        if 'message' in data:
            announcement.message = data['message']
        if 'expires_at' in data:
            announcement.expires_at = datetime.fromisoformat(data['expires_at']) if data['expires_at'] else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Announcement updated successfully',
            'announcement': announcement.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update announcement error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/announcements/<int:announcement_id>', methods=['DELETE'])
@require_faculty_auth()
def delete_announcement(announcement_id):
    """
    Delete an announcement
    """
    try:
        from database import db
        from models.gecr_models import Announcement, Faculty
        
        user_email = get_current_user_email()
        faculty = Faculty.find_by_email(user_email) if user_email else None
        faculty_id = faculty.faculty_id if faculty else get_current_faculty_id()
        
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Check if faculty is the author
        if announcement.author_id != faculty_id:
            return jsonify({'error': 'Unauthorized - You can only delete your own announcements'}), 403
        
        db.session.delete(announcement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Announcement deleted successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete announcement error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/events', methods=['POST'])
@require_faculty_auth()
def create_event():
    try:
        data = request.get_json() or {}
        title = data.get('title')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        location = data.get('location')
        description = data.get('description', '')

        if not title or not start_time:
            return jsonify({'error': 'Title and start_time are required'}), 400

        from database import db
        from models.gecr_models import Faculty, Event
        user_email = get_current_user_email()
        faculty = Faculty.find_by_email(user_email) if user_email else None
        created_by = faculty.faculty_id if faculty else get_current_faculty_id()

        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time) if end_time else None

        ev = Event(
            title=title,
            description=description,
            start_time=start_dt,
            end_time=end_dt,
            location=location,
            created_by=created_by
        )
        db.session.add(ev)
        db.session.commit()

        # Create in-app notifications for all students
        event_time = start_dt.strftime('%B %d, %Y at %I:%M %p')
        create_notifications_for_students(
            title=f"📅 New Event: {title}",
            message=f"{description} - {event_time}" + (f" at {location}" if location else ""),
            notification_type='event',
            link='/student/events'
        )

        # Email notifications removed - no longer sending emails

        return jsonify({'message': 'Event created', 'event_id': ev.event_id, 'event': ev.to_dict()}), 201

    except Exception as e:
        current_app.logger.error(f"Create event error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/events', methods=['GET'])
@require_faculty_auth()
def list_events():
    try:
        from models.gecr_models import Event, EventRegistration

        faculty_id = get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not authenticated'}), 401

        # Return events created by this faculty with registration counts
        evs = Event.query.filter_by(created_by=faculty_id).order_by(Event.start_time.asc()).all()

        events_with_counts = []
        for e in evs:
            reg_count = EventRegistration.query.filter_by(event_id=e.event_id).count()
            d = e.to_dict()
            d['registration_count'] = reg_count
            events_with_counts.append(d)

        return jsonify({'events': events_with_counts, 'events_count': len(events_with_counts)}), 200
    except Exception as e:
        current_app.logger.error(f"List events error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/events/<int:event_id>', methods=['PUT'])
@require_faculty_auth()
def update_event(event_id):
    """Update an event (faculty can only update their own events)"""
    try:
        from database import db
        from models.gecr_models import Event

        faculty_id = get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not authenticated'}), 401

        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        if event.created_by != faculty_id:
            return jsonify({'error': 'Access denied - you can only update your own events'}), 403

        data = request.get_json() or {}

        # Update fields
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'start_time' in data:
            event.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            event.end_time = datetime.fromisoformat(data['end_time']) if data['end_time'] else None
        if 'location' in data:
            event.location = data['location']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Event updated successfully',
            'event': event.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update event error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/events/<int:event_id>', methods=['DELETE'])
@require_faculty_auth()
def delete_event(event_id):
    """Delete an event (faculty can only delete their own events)"""
    try:
        from database import db
        from models.gecr_models import Event, EventRegistration

        faculty_id = get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not authenticated'}), 401

        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        if event.created_by != faculty_id:
            return jsonify({'error': 'Access denied - you can only delete your own events'}), 403

        # Delete all registrations first
        EventRegistration.query.filter_by(event_id=event_id).delete()

        # Delete the event
        db.session.delete(event)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Event deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete event error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/events/<int:event_id>/registrations/download', methods=['GET'])
@require_faculty_auth()
def download_event_registrations(event_id):
    """Download event registrations as CSV"""
    try:
        from models.gecr_models import Event, EventRegistration
        import csv
        from io import StringIO
        from flask import make_response

        faculty_id = get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not authenticated'}), 401

        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        if event.created_by != faculty_id:
            return jsonify({'error': 'Access denied'}), 403

        registrations = EventRegistration.query.filter_by(event_id=event_id).order_by(EventRegistration.registered_at.desc()).all()

        # Create CSV
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['Roll No', 'Name', 'Email', 'Department', 'Semester', 'Registered At'])

        for reg in registrations:
            writer.writerow([
                reg.student.roll_no if reg.student else '-',
                reg.student.name if reg.student else '-',
                reg.student.email if reg.student else '-',
                reg.student.department if reg.student else '-',
                reg.student.semester if reg.student else '-',
                reg.registered_at.strftime('%Y-%m-%d %H:%M:%S') if reg.registered_at else '-'
            ])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=event_{event_id}_registrations.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    except Exception as e:
        current_app.logger.error(f"Download registrations error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/notifications/<int:notification_id>/mark-read', methods=['POST'])
@require_faculty_auth()
def faculty_mark_notification_read(notification_id):
    try:
        from database import db
        from models.gecr_models import Notification

        faculty_id = get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not authenticated'}), 401

        notif = Notification.query.filter_by(notification_id=notification_id, user_id=faculty_id, user_type='faculty').first()
        if not notif:
            return jsonify({'error': 'Notification not found'}), 404

        notif.read = True
        db.session.commit()
        return jsonify({'message': 'Notification marked read'}), 200
    except Exception as e:
        current_app.logger.error(f"Faculty mark notification read error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/notifications/mark-all-read', methods=['POST'])
@require_faculty_auth()
def faculty_mark_all_notifications_read():
    try:
        from database import db
        from models.gecr_models import Notification

        faculty_id = get_current_faculty_id()
        if not faculty_id:
            return jsonify({'error': 'Faculty not authenticated'}), 401

        Notification.query.filter_by(user_id=faculty_id, user_type='faculty', read=False).update({'read': True})
        db.session.commit()
        return jsonify({'message': 'All notifications marked as read'}), 200
    except Exception as e:
        current_app.logger.error(f"Faculty mark all notifications read error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/activities', methods=['GET'])
@require_faculty_auth()
def list_activities():
    try:
        from models.gecr_models import Activity
        acts = Activity.query.order_by(Activity.created_at.desc()).limit(50).all()
        return jsonify({'activities': [a.to_dict() for a in acts]}), 200
    except Exception as e:
        current_app.logger.error(f"List activities error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@faculty_bp.route('/assignments', methods=['POST'])
@require_faculty_auth()
def create_assignment():
    """
    Create a new assignment
    Expected JSON: {
        "title": "Assignment Title",
        "description": "Assignment description",
        "subject_id": 1,
        "due_date": "2024-01-15",
        "max_marks": 50,
        "instructions": "Detailed instructions"
    }
    """
    try:
        current_user_email = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'subject_id', 'due_date', 'max_marks']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Assignment creation endpoint ready',
            'email': current_user_email,
            'assignment_data': data,
            'note': 'Database models not yet connected'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Assignment creation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@faculty_bp.route('/assignments/<int:assignment_id>/submissions', methods=['GET'])
@require_faculty_auth()
def get_assignment_submissions(assignment_id):
    """
    Get submissions for a specific assignment
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Assignment submissions endpoint ready',
            'email': current_user_email,
            'assignment_id': assignment_id,
            'sample_submissions': [
                {
                    'id': 1,
                    'student_name': 'John Doe',
                    'enrollment_number': 'CS2021001',
                    'submission_date': '2024-01-14',
                    'status': 'submitted',
                    'file_url': '/submissions/assignment1_john.pdf',
                    'marks': None
                },
                {
                    'id': 2,
                    'student_name': 'Jane Smith',
                    'enrollment_number': 'CS2021002',
                    'submission_date': '2024-01-13',
                    'status': 'graded',
                    'file_url': '/submissions/assignment1_jane.pdf',
                    'marks': 45
                }
            ],
            'note': 'Database models not yet connected - showing sample data'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Assignment submissions error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@faculty_bp.route('/grades', methods=['POST'])
@require_faculty_auth()
def grade_submission():
    """
    Grade a student submission
    Expected JSON: {
        "submission_id": 1,
        "marks": 45,
        "feedback": "Good work, but can improve on..."
    }
    """
    try:
        current_user_email = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        submission_id = data.get('submission_id')
        marks = data.get('marks')
        feedback = data.get('feedback', '')
        
        # Validate required fields
        if not all([submission_id, marks is not None]):
            return jsonify({'error': 'Submission ID and marks are required'}), 400
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Grading endpoint ready',
            'email': current_user_email,
            'submission_id': submission_id,
            'marks': marks,
            'feedback': feedback,
            'note': 'Database models not yet connected'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Grading error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@faculty_bp.route('/schedule', methods=['GET'])
@require_faculty_auth()
def get_schedule():
    """
    Get faculty teaching schedule
    Query parameters: date, week
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Get query parameters
        date = request.args.get('date')  # YYYY-MM-DD format
        week = request.args.get('week')  # week number
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Faculty schedule endpoint ready',
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
                        'class': 'CS-3A',
                        'room': 'Room 101',
                        'type': 'lecture'
                    },
                    {
                        'time': '11:00-12:00',
                        'subject': 'Physics Lab',
                        'class': 'CS-3B',
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
        
    except Exception as e:
        current_app.logger.error(f"Faculty schedule error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/timetable', methods=['GET'])
@require_faculty_auth()
def get_faculty_timetable():
    """
    Get all timetable entries for the logged-in faculty
    """
    try:
        from models.gecr_models import Faculty, Timetable, Subject, StudentEnrollment
        from database import db
        
        current_user_email = get_jwt_identity()
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get all timetable entries for this faculty
        timetable_entries = Timetable.query.filter_by(faculty_id=faculty.faculty_id).all()
        
        # Enrich with subject details and enrollment count
        result = []
        for entry in timetable_entries:
            subject = Subject.query.get(entry.subject_id)
            enrollment_count = StudentEnrollment.query.filter_by(
                subject_id=entry.subject_id,
                status='active'
            ).count()
            
            # Parse time_slot (format: "HH:MM-HH:MM")
            start_time, end_time = '09:00', '10:00'
            if entry.time_slot and '-' in entry.time_slot:
                parts = entry.time_slot.split('-')
                if len(parts) == 2:
                    start_time = parts[0].strip()
                    end_time = parts[1].strip()
            
            result.append({
                'timetable_id': entry.timetable_id,
                'subject_id': entry.subject_id,
                'subject_name': subject.subject_name if subject else 'Unknown',
                'subject_code': subject.subject_code if subject else 'N/A',
                'day_of_week': entry.day_of_week,
                'start_time': start_time,
                'end_time': end_time,
                'time_slot': entry.time_slot,
                'room': getattr(entry, 'room', None),
                'class_type': getattr(entry, 'class_type', 'Lecture'),
                'department': entry.department,
                'semester': entry.semester,
                'enrollment_count': enrollment_count
            })
        
        return jsonify({
            'timetable': result,
            'total': len(result)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get timetable error: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/timetable', methods=['POST'])
@require_faculty_auth()
def create_timetable_entry():
    """
    Create a new timetable entry for the faculty
    """
    try:
        from models.gecr_models import Faculty, Timetable, Subject
        from database import db
        
        current_user_email = get_jwt_identity()
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['subject_id', 'day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get subject to fetch department and semester
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Verify faculty teaches this subject
        if subject.faculty_id != faculty.faculty_id:
            return jsonify({'error': 'You are not assigned to teach this subject'}), 403
        
        # Create time_slot string
        time_slot = f"{data['start_time']}-{data['end_time']}"
        
        # Check for time conflicts
        existing = Timetable.query.filter_by(
            faculty_id=faculty.faculty_id,
            day_of_week=data['day_of_week'],
            time_slot=time_slot
        ).first()
        
        if existing:
            return jsonify({'error': 'You already have a class scheduled at this time'}), 409
        
        # Create new timetable entry
        new_entry = Timetable(
            department=subject.department or faculty.department,
            semester=subject.semester,
            day_of_week=data['day_of_week'],
            subject_id=data['subject_id'],
            faculty_id=faculty.faculty_id,
            time_slot=time_slot
        )
        
        # Add optional fields if they exist in the model
        if 'room' in data and hasattr(Timetable, 'room'):
            setattr(new_entry, 'room', data['room'])
        if 'class_type' in data and hasattr(Timetable, 'class_type'):
            setattr(new_entry, 'class_type', data['class_type'])
        
        db.session.add(new_entry)
        db.session.commit()
        
        current_app.logger.info(f"Timetable entry created: {new_entry.timetable_id} by {current_user_email}")
        
        return jsonify({
            'message': 'Timetable entry created successfully',
            'timetable_id': new_entry.timetable_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Create timetable error: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/timetable/<int:timetable_id>', methods=['GET'])
@require_faculty_auth()
def get_timetable_entry(timetable_id):
    """
    Get a specific timetable entry
    """
    try:
        from models.gecr_models import Faculty, Timetable, Subject
        from database import db
        
        current_user_email = get_jwt_identity()
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        entry = Timetable.query.get(timetable_id)
        
        if not entry:
            return jsonify({'error': 'Timetable entry not found'}), 404
        
        # Verify faculty owns this entry
        if entry.faculty_id != faculty.faculty_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        subject = Subject.query.get(entry.subject_id)
        
        # Parse time_slot
        start_time, end_time = '09:00', '10:00'
        if entry.time_slot and '-' in entry.time_slot:
            parts = entry.time_slot.split('-')
            if len(parts) == 2:
                start_time = parts[0].strip()
                end_time = parts[1].strip()
        
        return jsonify({
            'entry': {
                'timetable_id': entry.timetable_id,
                'subject_id': entry.subject_id,
                'subject_name': subject.subject_name if subject else 'Unknown',
                'subject_code': subject.subject_code if subject else 'N/A',
                'day_of_week': entry.day_of_week,
                'start_time': start_time,
                'end_time': end_time,
                'time_slot': entry.time_slot,
                'room': getattr(entry, 'room', None),
                'class_type': getattr(entry, 'class_type', 'Lecture'),
                'department': entry.department,
                'semester': entry.semester
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get timetable entry error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/timetable/<int:timetable_id>', methods=['PUT'])
@require_faculty_auth()
def update_timetable_entry(timetable_id):
    """
    Update a timetable entry
    """
    try:
        from models.gecr_models import Faculty, Timetable, Subject
        from database import db
        
        current_user_email = get_jwt_identity()
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        entry = Timetable.query.get(timetable_id)
        
        if not entry:
            return jsonify({'error': 'Timetable entry not found'}), 404
        
        # Verify faculty owns this entry
        if entry.faculty_id != faculty.faculty_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'subject_id' in data:
            subject = Subject.query.get(data['subject_id'])
            if not subject:
                return jsonify({'error': 'Subject not found'}), 404
            if subject.faculty_id != faculty.faculty_id:
                return jsonify({'error': 'You are not assigned to teach this subject'}), 403
            
            entry.subject_id = data['subject_id']
            entry.department = subject.department or faculty.department
            entry.semester = subject.semester
        
        if 'day_of_week' in data:
            entry.day_of_week = data['day_of_week']
        
        if 'start_time' in data and 'end_time' in data:
            time_slot = f"{data['start_time']}-{data['end_time']}"
            
            # Check for conflicts (excluding current entry)
            conflict = Timetable.query.filter(
                Timetable.timetable_id != timetable_id,
                Timetable.faculty_id == faculty.faculty_id,
                Timetable.day_of_week == entry.day_of_week,
                Timetable.time_slot == time_slot
            ).first()
            
            if conflict:
                return jsonify({'error': 'Time conflict with another class'}), 409
            
            entry.time_slot = time_slot
        
        if 'room' in data and hasattr(entry, 'room'):
            setattr(entry, 'room', data['room'])
        
        if 'class_type' in data and hasattr(entry, 'class_type'):
            setattr(entry, 'class_type', data['class_type'])
        
        db.session.commit()
        
        current_app.logger.info(f"Timetable entry updated: {timetable_id} by {current_user_email}")
        
        return jsonify({'message': 'Timetable entry updated successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Update timetable error: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/timetable/<int:timetable_id>', methods=['DELETE'])
@require_faculty_auth()
def delete_timetable_entry(timetable_id):
    """
    Delete a timetable entry
    """
    try:
        from models.gecr_models import Faculty, Timetable
        from database import db
        
        current_user_email = get_jwt_identity()
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        entry = Timetable.query.get(timetable_id)
        
        if not entry:
            return jsonify({'error': 'Timetable entry not found'}), 404
        
        # Verify faculty owns this entry
        if entry.faculty_id != faculty.faculty_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(entry)
        db.session.commit()
        
        current_app.logger.info(f"Timetable entry deleted: {timetable_id} by {current_user_email}")
        
        return jsonify({'message': 'Timetable entry deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete timetable error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@faculty_bp.route('/subjects', methods=['GET'])
@require_faculty_auth()
def get_subjects():
    """
    Get subjects taught by faculty (only subjects created by this faculty)
    """
    try:
        from models.gecr_models import Faculty, Subject, StudentEnrollment
        
        # Get current user email - support both JWT and session auth
        current_user_email = None
        try:
            verify_jwt_in_request(optional=True)
            current_user_email = get_jwt_identity()
        except Exception:
            pass
        
        # Fall back to session
        if not current_user_email and 'user_id' in session:
            faculty_id = session.get('user_id')
            faculty = Faculty.query.filter_by(faculty_id=faculty_id).first()
            if faculty:
                current_user_email = faculty.email
        
        if not current_user_email:
            return jsonify({'error': 'Authentication failed'}), 401
        
        # Get faculty by email
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get subjects created by this faculty only
        subjects = Subject.query.filter_by(faculty_id=faculty.faculty_id).all()
        
        # Count enrolled students for each subject
        subjects_data = []
        for subject in subjects:
            enrolled_count = StudentEnrollment.query.filter_by(
                subject_id=subject.subject_id,
                status='active'
            ).count()
            
            subjects_data.append({
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'subject_code': subject.subject_code or f'SUB{subject.subject_id}',
                'semester': subject.semester,
                'department': subject.department,
                'total_students': enrolled_count,
                'credits': subject.credits or 0,
                'description': subject.description
            })
        
        return jsonify({
            'subjects': subjects_data,
            'count': len(subjects_data)
        }), 200
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"Faculty subjects error: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@faculty_bp.route('/subjects/create', methods=['POST'])
@require_faculty_auth()
def create_subject():
    """
    Create a new subject (Faculty only)
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject
        
        # Get current user email - support both JWT and session auth
        current_user_email = None
        try:
            verify_jwt_in_request(optional=True)
            current_user_email = get_jwt_identity()
        except Exception:
            pass
        
        # Fall back to session
        if not current_user_email and 'user_id' in session:
            faculty_id = session.get('user_id')
            faculty = Faculty.query.filter_by(faculty_id=faculty_id).first()
            if faculty:
                current_user_email = faculty.email
        
        if not current_user_email:
            return jsonify({'error': 'Authentication failed'}), 401
        
        # Get faculty by email
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        subject_name = data.get('subject_name')
        department = data.get('department')
        semester = data.get('semester')
        
        if not subject_name or not department or not semester:
            return jsonify({'error': 'Subject name, department, and semester are required'}), 400
        
        # Check if subject already exists for this faculty
        existing = Subject.query.filter_by(
            subject_name=subject_name,
            department=department,
            semester=semester,
            faculty_id=faculty.faculty_id
        ).first()
        
        if existing:
            return jsonify({'error': 'You already have a subject with this name in this department and semester'}), 400
        
        # Create new subject
        new_subject = Subject(
            subject_name=subject_name,
            subject_code=data.get('subject_code'),
            department=department,
            semester=semester,
            credits=data.get('credits', 0),
            description=data.get('description'),
            faculty_id=faculty.faculty_id
        )
        
        db.session.add(new_subject)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subject created successfully',
            'subject_id': new_subject.subject_id,
            'subject': {
                'subject_id': new_subject.subject_id,
                'subject_name': new_subject.subject_name,
                'subject_code': new_subject.subject_code or f'SUB{new_subject.subject_id}',
                'department': new_subject.department,
                'semester': new_subject.semester,
                'credits': new_subject.credits,
                'description': new_subject.description,
                'total_students': 0
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create subject error: {str(e)}")
        return jsonify({'error': f'Failed to create subject: {str(e)}'}), 500

@faculty_bp.route('/subjects/<int:subject_id>/update', methods=['PUT'])
@require_faculty_auth()
def update_subject(subject_id):
    """
    Update a subject (Faculty only - own subjects)
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject
        
        # Get current user email - support both JWT and session auth
        current_user_email = None
        try:
            verify_jwt_in_request(optional=True)
            current_user_email = get_jwt_identity()
        except Exception:
            pass
        
        # Fall back to session
        if not current_user_email and 'user_id' in session:
            faculty_id = session.get('user_id')
            faculty = Faculty.query.filter_by(faculty_id=faculty_id).first()
            if faculty:
                current_user_email = faculty.email
        
        if not current_user_email:
            return jsonify({'error': 'Authentication failed'}), 401
        
        # Get faculty by email
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get subject and verify ownership
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        if subject.faculty_id != faculty.faculty_id:
            return jsonify({'error': 'You can only update your own subjects'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'subject_name' in data:
            subject.subject_name = data['subject_name']
        if 'subject_code' in data:
            subject.subject_code = data['subject_code']
        if 'department' in data:
            subject.department = data['department']
        if 'semester' in data:
            subject.semester = data['semester']
        if 'credits' in data:
            subject.credits = data['credits']
        if 'description' in data:
            subject.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subject updated successfully',
            'subject': {
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'subject_code': subject.subject_code or f'SUB{subject.subject_id}',
                'department': subject.department,
                'semester': subject.semester,
                'credits': subject.credits,
                'description': subject.description
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update subject error: {str(e)}")
        return jsonify({'error': f'Failed to update subject: {str(e)}'}), 500

@faculty_bp.route('/subjects/<int:subject_id>/delete', methods=['DELETE'])
@require_faculty_auth()
def delete_subject(subject_id):
    """
    Delete a subject (Faculty only - own subjects)
    """
    try:
        from database import db
        from models.gecr_models import Faculty, Subject, StudentEnrollment
        
        # Get current user email - support both JWT and session auth
        current_user_email = None
        try:
            verify_jwt_in_request(optional=True)
            current_user_email = get_jwt_identity()
        except Exception:
            pass
        
        # Fall back to session
        if not current_user_email and 'user_id' in session:
            faculty_id = session.get('user_id')
            faculty = Faculty.query.filter_by(faculty_id=faculty_id).first()
            if faculty:
                current_user_email = faculty.email
        
        if not current_user_email:
            return jsonify({'error': 'Authentication failed'}), 401
        
        # Get faculty by email
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get subject and verify ownership
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        if subject.faculty_id != faculty.faculty_id:
            return jsonify({'error': 'You can only delete your own subjects'}), 403
        
        # Check if there are active enrollments
        enrollment_count = StudentEnrollment.query.filter_by(
            subject_id=subject_id,
            status='active'
        ).count()
        
        if enrollment_count > 0:
            return jsonify({
                'error': f'Cannot delete subject with {enrollment_count} active enrollments. Please remove students first.'
            }), 400
        
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subject deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete subject error: {str(e)}")
        return jsonify({'error': f'Failed to delete subject: {str(e)}'}), 500


@faculty_bp.route('/timetable/subject/<int:subject_id>', methods=['GET'])
def get_subject_timetable(subject_id):
    """
    Get timetable for a specific subject
    Optional query param: day (e.g., Monday, Tuesday)
    """
    try:
        from models.gecr_models import Timetable, Subject
        from database import db
        
        # Get optional day filter
        day = request.args.get('day')
        
        # Build query
        query = Timetable.query.filter_by(subject_id=subject_id)
        
        if day:
            query = query.filter_by(day_of_week=day)
        
        # Get schedule
        schedule = query.all()
        
        if not schedule:
            return jsonify({
                'success': False,
                'message': 'No schedule found'
            }), 404
        
        return jsonify({
            'success': True,
            'schedule': [s.to_dict() for s in schedule]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get timetable error: {str(e)}")
        return jsonify({'error': f'Failed to fetch timetable: {str(e)}'}), 500


# Error handlers for the faculty blueprint
@faculty_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Faculty access required'}), 403