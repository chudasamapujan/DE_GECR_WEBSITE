"""
Subject Enrollment Routes
Allows students to enroll in subjects and faculty to manage enrollments
Author: GEC Rajkot Development Team
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from datetime import datetime
from database import db
from models.gecr_models import Student, Faculty, Subject, StudentEnrollment, Notification

# Create enrollment blueprint
enrollment_bp = Blueprint('enrollment', __name__, url_prefix='/api/enrollment')


# ==================== DEBUG ROUTE ====================

@enrollment_bp.route('/debug/all-subjects', methods=['GET'])
def debug_all_subjects():
    """
    Debug endpoint to see all subjects in database
    """
    try:
        all_subjects = Subject.query.all()
        
        subjects_list = [{
            'subject_id': s.subject_id,
            'subject_name': s.subject_name,
            'department': s.department,
            'semester': s.semester,
            'faculty_id': s.faculty_id,
            'faculty_name': s.faculty.name if s.faculty else None
        } for s in all_subjects]
        
        # Get current student info if logged in
        student_info = None
        if 'user_id' in session and session.get('user_type') == 'student':
            student = Student.query.get(session['user_id'])
            if student:
                student_info = {
                    'student_id': student.student_id,
                    'name': student.name,
                    'department': student.department,
                    'semester': student.semester,
                    'roll_no': student.roll_no
                }
        
        return jsonify({
            'total_subjects': len(all_subjects),
            'subjects': subjects_list,
            'student_info': student_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== STUDENT ENROLLMENT ROUTES ====================

@enrollment_bp.route('/student/info', methods=['GET'])
def get_student_info():
    """
    Get current student information for enrollment page header
    """
    try:
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({'error': 'Unauthorized - Student login required'}), 401
        
        student = Student.query.get(session['user_id'])
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Count enrolled subjects
        enrolled_count = StudentEnrollment.query.filter_by(
            student_id=student.student_id,
            status='active'
        ).count()
        
        return jsonify({
            'success': True,
            'student': {
                'student_id': student.student_id,
                'name': student.name,
                'roll_no': student.roll_no,
                'email': student.email,
                'department': student.department,
                'semester': student.semester,
                'enrolled_count': enrolled_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch student info: {str(e)}'}), 500


@enrollment_bp.route('/student/available-subjects', methods=['GET'])
def get_available_subjects():
    """
    Get ALL available subjects for student enrollment requests
    Students can request to enroll in any subject, faculty approval required
    """
    try:
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({'error': 'Unauthorized - Student login required'}), 401
        
        student = Student.query.get(session['user_id'])
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get ALL subjects from database
        available_subjects = Subject.query.all()
        
        # Get enrollment status for all subjects
        enrollments = StudentEnrollment.query.filter_by(
            student_id=student.student_id
        ).all()
        
        # Create mapping of subject_id to enrollment status
        enrollment_status_map = {
            e.subject_id: e.status for e in enrollments
        }
        
        subjects_data = []
        for subject in available_subjects:
            enrollment_status = enrollment_status_map.get(subject.subject_id, None)
            
            subjects_data.append({
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'subject_code': subject.subject_code or f'SUB{subject.subject_id}',
                'department': subject.department,
                'semester': subject.semester,
                'faculty_name': subject.faculty.name if subject.faculty else 'Not Assigned',
                'faculty_id': subject.faculty_id,
                'enrolled_count': StudentEnrollment.query.filter_by(
                    subject_id=subject.subject_id,
                    status='active'
                ).count(),
                'enrollment_status': enrollment_status  # None, 'pending', 'active', 'rejected'
            })
        
        return jsonify({
            'success': True,
            'student': {
                'student_id': student.student_id,
                'name': student.name,
                'department': student.department,
                'semester': student.semester
            },
            'subjects': subjects_data,
            'total_subjects': len(available_subjects),
            'message': 'Showing all available subjects. Request enrollment for any subject.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch subjects: {str(e)}'}), 500


@enrollment_bp.route('/student/enroll', methods=['POST'])
def enroll_in_subject():
    """
    Request enrollment in a subject (requires faculty approval)
    Expects JSON: {"subject_id": int}
    """
    try:
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({'error': 'Unauthorized - Student login required'}), 401
        
        data = request.get_json()
        subject_id = data.get('subject_id')
        
        if not subject_id:
            return jsonify({'error': 'Subject ID is required'}), 400
        
        student = Student.query.get(session['user_id'])
        subject = Subject.query.get(subject_id)
        
        if not student or not subject:
            return jsonify({'error': 'Student or Subject not found'}), 404
        
        # Check if already has an enrollment/request
        existing = StudentEnrollment.query.filter_by(
            student_id=student.student_id,
            subject_id=subject_id
        ).first()
        
        if existing:
            if existing.status == 'active':
                return jsonify({'error': 'Already enrolled in this subject'}), 400
            elif existing.status == 'pending':
                return jsonify({'error': 'Enrollment request already pending approval'}), 400
            elif existing.status == 'rejected':
                # Allow re-request if previously rejected
                existing.status = 'pending'
                existing.enrollment_date = datetime.utcnow()
                message = 'Enrollment request resubmitted for approval'
            else:
                # Reactivate enrollment
                existing.status = 'pending'
                existing.enrollment_date = datetime.utcnow()
                message = 'Enrollment request submitted for approval'
        else:
            # Create new enrollment request with pending status
            new_enrollment = StudentEnrollment(
                student_id=student.student_id,
                subject_id=subject_id,
                enrollment_date=datetime.utcnow(),
                academic_year=f"{datetime.now().year}-{datetime.now().year + 1}",
                status='pending'  # Pending faculty approval
            )
            db.session.add(new_enrollment)
            message = 'Enrollment request sent to faculty for approval'
        
        # Create notification for faculty
        if subject.faculty_id:
            notification = Notification(
                user_id=subject.faculty_id,
                user_type='faculty',
                title='New Enrollment Request',
                message=f'{student.name} ({student.roll_no}) has requested to enroll in {subject.subject_name}',
                notification_type='enrollment_request',
                link=f'/faculty/enrollments',
                read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'enrollment': {
                'student_name': student.name,
                'subject_name': subject.subject_name,
                'faculty_name': subject.faculty.name if subject.faculty else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to enroll: {str(e)}'}), 500


@enrollment_bp.route('/student/unenroll', methods=['POST'])
def unenroll_from_subject():
    """
    Unenroll (drop) student from a subject
    Expects JSON: {"subject_id": int}
    """
    try:
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({'error': 'Unauthorized - Student login required'}), 401
        
        data = request.get_json()
        subject_id = data.get('subject_id')
        
        if not subject_id:
            return jsonify({'error': 'Subject ID is required'}), 400
        
        enrollment = StudentEnrollment.query.filter_by(
            student_id=session['user_id'],
            subject_id=subject_id,
            status='active'
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this subject'}), 404
        
        # Mark as dropped instead of deleting
        enrollment.status = 'dropped'
        
        # Notify faculty
        subject = Subject.query.get(subject_id)
        student = Student.query.get(session['user_id'])
        
        if subject and subject.faculty_id:
            notification = Notification(
                user_id=subject.faculty_id,
                user_type='faculty',
                title='Student Dropped Subject',
                message=f'{student.name} ({student.roll_no}) has dropped {subject.subject_name}',
                notification_type='enrollment',
                link=f'/faculty/subjects',
                read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Successfully unenrolled from subject'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to unenroll: {str(e)}'}), 500


@enrollment_bp.route('/student/my-enrollments', methods=['GET'])
def get_my_enrollments():
    """
    Get all active enrollments for logged-in student
    """
    try:
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({'error': 'Unauthorized - Student login required'}), 401
        
        enrollments = StudentEnrollment.query.filter_by(
            student_id=session['user_id'],
            status='active'
        ).all()
        
        enrollments_data = []
        for enrollment in enrollments:
            subject = enrollment.subject
            enrollments_data.append({
                'enrollment_id': enrollment.enrollment_id,
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'subject_code': subject.subject_code or f'SUB{subject.subject_id}',
                'department': subject.department,
                'semester': subject.semester,
                'faculty_name': subject.faculty.name if subject.faculty else 'Not Assigned',
                'enrollment_date': enrollment.enrollment_date.strftime('%Y-%m-%d') if enrollment.enrollment_date else None,
                'academic_year': enrollment.academic_year
            })
        
        return jsonify({
            'success': True,
            'enrollments': enrollments_data,
            'total': len(enrollments_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch enrollments: {str(e)}'}), 500


# ==================== FACULTY ENROLLMENT ROUTES ====================

@enrollment_bp.route('/faculty/subject-enrollments/<int:subject_id>', methods=['GET'])
def get_subject_enrollments(subject_id):
    """
    Get all students enrolled in a specific subject (for faculty)
    """
    try:
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty login required'}), 401
        
        # Verify faculty teaches this subject
        subject = Subject.query.get(subject_id)
        if not subject or subject.faculty_id != session['user_id']:
            return jsonify({'error': 'Unauthorized - You do not teach this subject'}), 403
        
        enrollments = StudentEnrollment.query.filter_by(
            subject_id=subject_id,
            status='active'
        ).all()
        
        students_data = []
        for enrollment in enrollments:
            student = enrollment.student
            students_data.append({
                'enrollment_id': enrollment.enrollment_id,
                'student_id': student.student_id,
                'roll_no': student.roll_no,
                'name': student.name,
                'email': student.email,
                'department': student.department,
                'semester': student.semester,
                'enrollment_date': enrollment.enrollment_date.strftime('%Y-%m-%d') if enrollment.enrollment_date else None,
                'academic_year': enrollment.academic_year
            })
        
        return jsonify({
            'success': True,
            'subject': {
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'department': subject.department,
                'semester': subject.semester
            },
            'enrollments': students_data,
            'total': len(students_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch enrollments: {str(e)}'}), 500


@enrollment_bp.route('/faculty/all-enrollments', methods=['GET'])
def get_all_faculty_enrollments():
    """
    Get enrollment summary for all subjects taught by faculty
    """
    try:
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty login required'}), 401
        
        subjects = Subject.query.filter_by(faculty_id=session['user_id']).all()
        
        subjects_data = []
        for subject in subjects:
            enrolled_count = StudentEnrollment.query.filter_by(
                subject_id=subject.subject_id,
                status='active'
            ).count()
            
            subjects_data.append({
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'department': subject.department,
                'semester': subject.semester,
                'enrolled_students': enrolled_count
            })
        
        return jsonify({
            'success': True,
            'subjects': subjects_data,
            'total_subjects': len(subjects_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch enrollments: {str(e)}'}), 500


# ==================== PAGE RENDERING ROUTES ====================

@enrollment_bp.route('/student/enroll-page', methods=['GET'])
def student_enrollment_page():
    """
    Render student subject enrollment page
    """
    if 'user_id' not in session or session.get('user_type') != 'student':
        flash('Please log in as student to access this page', 'error')
        return redirect(url_for('serve_login', user_type='student'))
    
    student = Student.query.get(session['user_id'])
    return render_template('student/enroll-subjects.html', student=student)


@enrollment_bp.route('/faculty/enrollments-page', methods=['GET'])
def faculty_enrollments_page():
    """
    Render faculty enrollment management page
    """
    if 'user_id' not in session or session.get('user_type') != 'faculty':
        flash('Please log in as faculty to access this page', 'error')
        return redirect(url_for('serve_login', user_type='faculty'))
    
    faculty = Faculty.query.get(session['user_id'])
    subjects = Subject.query.filter_by(faculty_id=session['user_id']).all()
    
    return render_template('faculty/enrollments.html', faculty=faculty, subjects=subjects)
