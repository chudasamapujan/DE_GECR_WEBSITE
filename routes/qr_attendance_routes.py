"""
QR-Based Attendance Routes
Faculty generates QR codes, students scan to mark attendance with photo
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from database import db
from models.gecr_models import AttendanceSession, Attendance, Subject, Student, StudentEnrollment
from datetime import datetime, timedelta, date, time
import qrcode
from io import BytesIO
import base64
import os
import secrets
import json

qr_attendance_bp = Blueprint('qr_attendance', __name__, url_prefix='/api/qr-attendance')

# Helper function to check faculty auth (reuse from faculty_routes)
def get_current_user_email():
    """Get current user email from session or JWT"""
    from flask import session
    from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
    
    try:
        verify_jwt_in_request(optional=True)
        email = get_jwt_identity()
        if email:
            return email
    except:
        pass
    
    return session.get('user_email')

def require_faculty_auth():
    """Decorator to ensure faculty authentication"""
    from functools import wraps
    from flask import session
    from flask_jwt_extended import verify_jwt_in_request, get_jwt
    
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Try JWT first
            try:
                verify_jwt_in_request(optional=True)
                claims = get_jwt()
                if claims and claims.get('user_type') == 'faculty':
                    return f(*args, **kwargs)
            except Exception:
                pass
            
            # Fall back to session-based auth
            if 'user_id' in session and session.get('user_type') == 'faculty':
                return f(*args, **kwargs)
            
            return jsonify({'error': 'Faculty authentication required'}), 401
        return wrapper
    return decorator


@qr_attendance_bp.route('/generate', methods=['POST'])
@require_faculty_auth()
def generate_qr_session():
    """
    Generate a new QR code session for attendance
    Expected JSON: {
        subject_id: int,
        session_date: 'YYYY-MM-DD',
        session_time: 'HH:MM',
        duration_minutes: int (default 30),
        require_photo: bool (default true),
        require_location: bool (default false)
    }
    """
    try:
        from models.gecr_models import Faculty
        
        data = request.get_json()
        current_user_email = get_current_user_email()
        
        # Get faculty
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Validate input
        subject_id = data.get('subject_id')
        session_date_str = data.get('session_date')
        session_time_str = data.get('session_time')
        duration_minutes = data.get('duration_minutes', 30)
        require_photo = data.get('require_photo', True)
        require_location = data.get('require_location', False)
        
        if not all([subject_id, session_date_str, session_time_str]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify subject exists and faculty owns it
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Check if this subject belongs to the current faculty
        if subject.faculty_id != faculty.faculty_id:
            return jsonify({'error': 'You can only create QR sessions for your own subjects'}), 403
        
        # Parse date and time
        session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
        session_time = datetime.strptime(session_time_str, '%H:%M').time()
        
        # Generate unique code
        unique_code = secrets.token_urlsafe(32)
        
        # Calculate expiry
        session_datetime = datetime.combine(session_date, session_time)
        expires_at = session_datetime + timedelta(minutes=duration_minutes)
        
        # Create session
        new_session = AttendanceSession(
            faculty_id=faculty.faculty_id,
            subject_id=subject_id,
            session_date=session_date,
            session_time=session_time,
            unique_code=unique_code,
            expires_at=expires_at,
            status='active',
            require_photo=require_photo,
            require_location=require_location
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        # Generate QR code
        qr_data = json.dumps({
            'session_id': new_session.session_id,
            'code': unique_code,
            'subject': subject.subject_name,
            'date': session_date_str,
            'time': session_time_str
        })
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code image
        qr_filename = f"qr_{new_session.session_id}_{unique_code[:8]}.png"
        qr_path = os.path.join('static', 'qr_codes', qr_filename)
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        img.save(qr_path)
        
        # Update session with QR path
        new_session.qr_image_path = f'/static/qr_codes/{qr_filename}'
        db.session.commit()
        
        # Also return base64 encoded QR for immediate display
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'message': 'QR session created successfully',
            'session': new_session.to_dict(),
            'qr_code_base64': qr_base64,
            'qr_code_url': new_session.qr_image_path
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Generate QR error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to generate QR session', 'details': str(e)}), 500


@qr_attendance_bp.route('/sessions', methods=['GET'])
@require_faculty_auth()
def get_faculty_sessions():
    """Get all QR sessions created by the current faculty"""
    try:
        from models.gecr_models import Faculty
        
        current_user_email = get_current_user_email()
        faculty = Faculty.query.filter_by(email=current_user_email).first()
        
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Get sessions
        status_filter = request.args.get('status')  # active, expired, closed
        date_filter = request.args.get('date')  # YYYY-MM-DD
        
        query = AttendanceSession.query.filter_by(faculty_id=faculty.faculty_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if date_filter:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(session_date=filter_date)
        
        sessions = query.order_by(AttendanceSession.created_at.desc()).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get sessions error: {str(e)}")
        return jsonify({'error': 'Failed to fetch sessions'}), 500


@qr_attendance_bp.route('/sessions/<int:session_id>', methods=['GET'])
@require_faculty_auth()
def get_session_details(session_id):
    """Get detailed information about a specific session including attendance"""
    try:
        session = AttendanceSession.query.get(session_id)
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get attendance records for this session
        attendance_records = Attendance.query.filter_by(session_id=session_id).all()
        
        return jsonify({
            'session': session.to_dict(),
            'attendance': [record.to_dict() for record in attendance_records],
            'total_present': len(attendance_records)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get session details error: {str(e)}")
        return jsonify({'error': 'Failed to fetch session details'}), 500


@qr_attendance_bp.route('/sessions/<int:session_id>/close', methods=['POST'])
@require_faculty_auth()
def close_session(session_id):
    """Close a QR session manually"""
    try:
        session = AttendanceSession.query.get(session_id)
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        session.status = 'closed'
        db.session.commit()
        
        return jsonify({
            'message': 'Session closed successfully',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Close session error: {str(e)}")
        return jsonify({'error': 'Failed to close session'}), 500


@qr_attendance_bp.route('/verify', methods=['POST'])
def verify_qr_code():
    """
    Verify QR code and mark attendance (called by students)
    Expected JSON: {
        session_id: int,
        code: string,
        student_email: string,
        photo: base64_string,
        latitude: float (optional),
        longitude: float (optional)
    }
    """
    try:
        data = request.get_json()
        
        session_id = data.get('session_id')
        code = data.get('code')
        student_email = data.get('student_email')
        photo_base64 = data.get('photo')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Validate input
        if not all([session_id, code, student_email]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get session
        session = AttendanceSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Verify code
        if session.unique_code != code:
            return jsonify({'error': 'Invalid QR code'}), 403
        
        # Check if session is valid
        if not session.is_valid():
            return jsonify({'error': 'Session has expired or is closed'}), 403
        
        # Get student
        student = Student.query.filter_by(email=student_email).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Check if student is enrolled in the subject
        enrollment = StudentEnrollment.query.filter_by(
            student_id=student.student_id,
            subject_id=session.subject_id,
            status='active'
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'You are not enrolled in this subject'}), 403
        
        # Check if already marked
        existing_attendance = Attendance.query.filter_by(
            student_id=student.student_id,
            subject_id=session.subject_id,
            session_id=session_id
        ).first()
        
        if existing_attendance:
            return jsonify({'error': 'Attendance already marked for this session'}), 400
        
        # Save photo if provided
        photo_path = None
        if photo_base64 and session.require_photo:
            try:
                # Decode base64 image
                photo_data = base64.b64decode(photo_base64.split(',')[1] if ',' in photo_base64 else photo_base64)
                
                # Generate filename
                photo_filename = f"attendance_{student.student_id}_{session_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                photo_full_path = os.path.join('static', 'attendance_photos', photo_filename)
                
                # Save photo
                os.makedirs(os.path.dirname(photo_full_path), exist_ok=True)
                with open(photo_full_path, 'wb') as f:
                    f.write(photo_data)
                
                photo_path = f'/static/attendance_photos/{photo_filename}'
            except Exception as photo_error:
                current_app.logger.error(f"Photo save error: {str(photo_error)}")
                if session.require_photo:
                    return jsonify({'error': 'Failed to save photo'}), 500
        
        # Create attendance record
        attendance = Attendance(
            student_id=student.student_id,
            subject_id=session.subject_id,
            date=session.session_date,
            status='present',
            session_id=session_id,
            photo_path=photo_path,
            latitude=latitude,
            longitude=longitude,
            marked_at=datetime.now()
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'message': 'Attendance marked successfully',
            'attendance': attendance.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Verify QR error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to mark attendance', 'details': str(e)}), 500


@qr_attendance_bp.route('/student/sessions', methods=['GET'])
def get_available_sessions():
    """Get active QR sessions available for the current student"""
    try:
        student_email = request.args.get('email')
        
        if not student_email:
            return jsonify({'error': 'Email required'}), 400
        
        student = Student.query.filter_by(email=student_email).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get student's enrolled subjects
        enrollments = StudentEnrollment.query.filter_by(
            student_id=student.student_id,
            status='active'
        ).all()
        
        enrolled_subject_ids = [e.subject_id for e in enrollments]
        
        # Get active sessions for these subjects
        now = datetime.now()
        active_sessions = AttendanceSession.query.filter(
            AttendanceSession.subject_id.in_(enrolled_subject_ids),
            AttendanceSession.status == 'active',
            AttendanceSession.expires_at > now
        ).order_by(AttendanceSession.created_at.desc()).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in active_sessions]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get available sessions error: {str(e)}")
        return jsonify({'error': 'Failed to fetch sessions'}), 500
