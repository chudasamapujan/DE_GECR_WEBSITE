"""
Subject Management Routes
Allows faculty/admin to create and manage subjects
Author: GEC Rajkot Development Team
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from datetime import datetime
from database import db
from models.gecr_models import Subject, Faculty, Student, StudentEnrollment

# Create subject management blueprint
subject_bp = Blueprint('subjects', __name__, url_prefix='/api/subjects')


# ==================== FACULTY/ADMIN SUBJECT MANAGEMENT ====================

@subject_bp.route('/create', methods=['POST'])
def create_subject():
    """
    Create a new subject (Faculty/Admin only)
    Expects JSON: {
        "subject_name": str,
        "subject_code": str (optional),
        "department": str,
        "semester": int,
        "credits": int (optional),
        "description": str (optional)
    }
    """
    try:
        # Check if user is faculty (you can add admin check too)
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty/Admin access required'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        subject_name = data.get('subject_name')
        department = data.get('department')
        semester = data.get('semester')
        
        if not subject_name or not department or not semester:
            return jsonify({'error': 'Subject name, department, and semester are required'}), 400
        
        # Check if subject already exists
        existing = Subject.query.filter_by(
            subject_name=subject_name,
            department=department,
            semester=semester
        ).first()
        
        if existing:
            return jsonify({'error': 'Subject already exists for this department and semester'}), 400
        
        # Create new subject and assign to current faculty
        # Note: Only using fields that exist in the Subject model
        new_subject = Subject(
            subject_name=subject_name,
            department=department,
            semester=semester,
            faculty_id=session['user_id']  # Assign to creating faculty
        )
        
        db.session.add(new_subject)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subject created successfully',
            'subject': {
                'subject_id': new_subject.subject_id,
                'subject_name': new_subject.subject_name,
                'subject_code': data.get('subject_code', 'N/A'),  # Return from input but not saved
                'department': new_subject.department,
                'semester': new_subject.semester,
                'credits': data.get('credits', 0),  # Return from input but not saved
                'description': data.get('description', '')  # Return from input but not saved
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create subject: {str(e)}'}), 500


@subject_bp.route('/all', methods=['GET'])
def get_all_subjects():
    """
    Get all subjects in the system
    Optional query params: department, semester
    """
    try:
        department = request.args.get('department')
        semester = request.args.get('semester')
        
        query = Subject.query
        
        if department:
            query = query.filter_by(department=department)
        if semester:
            query = query.filter_by(semester=int(semester))
        
        subjects = query.all()
        
        subjects_data = []
        for subject in subjects:
            # Count enrollments
            enrollment_count = StudentEnrollment.query.filter_by(
                subject_id=subject.subject_id,
                status='active'
            ).count()
            
            subjects_data.append({
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'subject_code': 'N/A',  # Field doesn't exist in model
                'department': subject.department,
                'semester': subject.semester,
                'credits': 0,  # Field doesn't exist in model
                'description': '',  # Field doesn't exist in model
                'faculty_name': subject.faculty.name if subject.faculty else 'Not Assigned',
                'faculty_id': subject.faculty_id,
                'enrollment_count': enrollment_count
            })
        
        return jsonify({
            'success': True,
            'subjects': subjects_data,
            'total': len(subjects_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch subjects: {str(e)}'}), 500


@subject_bp.route('/<int:subject_id>', methods=['GET'])
def get_subject_details(subject_id):
    """
    Get detailed information about a specific subject
    """
    try:
        subject = Subject.query.get(subject_id)
        
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Get enrollment count
        enrollment_count = StudentEnrollment.query.filter_by(
            subject_id=subject_id,
            status='active'
        ).count()
        
        # Get enrolled students
        enrollments = StudentEnrollment.query.filter_by(
            subject_id=subject_id,
            status='active'
        ).all()
        
        enrolled_students = [{
            'student_id': e.student.student_id,
            'roll_no': e.student.roll_no,
            'name': e.student.name,
            'enrollment_date': e.enrollment_date.strftime('%Y-%m-%d') if e.enrollment_date else None
        } for e in enrollments]
        
        return jsonify({
            'success': True,
            'subject': {
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'subject_code': 'N/A',  # Field doesn't exist in model
                'department': subject.department,
                'semester': subject.semester,
                'credits': 0,  # Field doesn't exist in model
                'description': '',  # Field doesn't exist in model
                'faculty_name': subject.faculty.name if subject.faculty else 'Not Assigned',
                'faculty_id': subject.faculty_id,
                'enrollment_count': enrollment_count,
                'enrolled_students': enrolled_students
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch subject details: {str(e)}'}), 500


@subject_bp.route('/<int:subject_id>/update', methods=['PUT'])
def update_subject(subject_id):
    """
    Update subject details (Faculty/Admin only)
    """
    try:
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty/Admin access required'}), 401
        
        subject = Subject.query.get(subject_id)
        
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Check if faculty owns this subject
        if subject.faculty_id != session['user_id']:
            return jsonify({'error': 'Unauthorized - You can only update your own subjects'}), 403
        
        data = request.get_json()
        
        # Update only fields that exist in the Subject model
        if 'subject_name' in data:
            subject.subject_name = data['subject_name']
        if 'department' in data:
            subject.department = data['department']
        if 'semester' in data:
            subject.semester = data['semester']
        # Note: subject_code, credits, description don't exist in model
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subject updated successfully',
            'subject': {
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'subject_code': data.get('subject_code', 'N/A'),  # Return from input but not saved
                'department': subject.department,
                'semester': subject.semester,
                'credits': data.get('credits', 0),  # Return from input but not saved
                'description': data.get('description', '')  # Return from input but not saved
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update subject: {str(e)}'}), 500


@subject_bp.route('/<int:subject_id>/delete', methods=['DELETE'])
def delete_subject(subject_id):
    """
    Delete a subject (Faculty/Admin only)
    Note: This will also remove all enrollments
    """
    try:
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty/Admin access required'}), 401
        
        subject = Subject.query.get(subject_id)
        
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Check if faculty owns this subject
        if subject.faculty_id != session['user_id']:
            return jsonify({'error': 'Unauthorized - You can only delete your own subjects'}), 403
        
        # Check if there are active enrollments
        enrollment_count = StudentEnrollment.query.filter_by(
            subject_id=subject_id,
            status='active'
        ).count()
        
        if enrollment_count > 0:
            return jsonify({
                'error': f'Cannot delete subject with {enrollment_count} active enrollments. Please remove enrollments first.'
            }), 400
        
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subject deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete subject: {str(e)}'}), 500


@subject_bp.route('/departments', methods=['GET'])
def get_departments():
    """
    Get list of all departments with subjects
    """
    try:
        # Get unique departments
        departments = db.session.query(Subject.department).distinct().all()
        department_list = [dept[0] for dept in departments if dept[0]]
        
        return jsonify({
            'success': True,
            'departments': department_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch departments: {str(e)}'}), 500


# ==================== PAGE RENDERING ROUTES ====================

@subject_bp.route('/manage-page', methods=['GET'])
def manage_subjects_page():
    """
    Render subject management page (Faculty/Admin)
    """
    if 'user_id' not in session or session.get('user_type') != 'faculty':
        flash('Please log in as faculty to access this page', 'error')
        return redirect(url_for('serve_login', user_type='faculty'))
    
    faculty = Faculty.query.get(session['user_id'])
    return render_template('faculty/manage-subjects.html', faculty=faculty)


@subject_bp.route('/browse-page', methods=['GET'])
def browse_subjects_page():
    """
    Render subject browsing page (for all users)
    """
    user_type = session.get('user_type')
    
    if user_type == 'student':
        student = Student.query.get(session['user_id'])
        return render_template('student/browse-subjects.html', student=student)
    elif user_type == 'faculty':
        faculty = Faculty.query.get(session['user_id'])
        return render_template('faculty/browse-subjects.html', faculty=faculty)
    else:
        return render_template('browse-subjects.html')
