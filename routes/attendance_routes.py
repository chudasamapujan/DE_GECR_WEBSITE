"""
Attendance Management Routes
Complete attendance module for faculty and students
Author: GEC Rajkot Development Team
"""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from datetime import datetime, date
from werkzeug.utils import secure_filename
import os
import pandas as pd
from database import db
from models.gecr_models import Student, Faculty, Subject, Attendance, StudentEnrollment

# Create attendance blueprint
attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

# Configuration for Excel uploads
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Ensure upload folder exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def calculate_attendance_percentage(student_id, subject_id=None):
    """
    Calculate attendance percentage for a student
    If subject_id is provided, calculate for that subject only
    Otherwise, calculate overall attendance
    """
    if subject_id:
        # Subject-specific attendance
        total_classes = Attendance.query.filter_by(
            student_id=student_id,
            subject_id=subject_id
        ).count()
        
        attended_classes = Attendance.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            status='Present'
        ).count()
    else:
        # Overall attendance
        total_classes = Attendance.query.filter_by(student_id=student_id).count()
        attended_classes = Attendance.query.filter_by(
            student_id=student_id,
            status='Present'
        ).count()
    
    if total_classes == 0:
        return 0.0
    
    return round((attended_classes / total_classes) * 100, 2)


# ==================== FACULTY ROUTES ====================

@attendance_bp.route('/faculty/mark', methods=['POST'])
def faculty_mark_attendance():
    """
    Mark attendance manually for students
    Expects JSON: {
        "subject_id": int,
        "date": "YYYY-MM-DD",
        "attendance": [{"student_id": int, "status": "Present|Absent|Late"}, ...]
    }
    """
    try:
        # Check if user is faculty
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty login required'}), 401
        
        data = request.get_json()
        subject_id = data.get('subject_id')
        attendance_date = data.get('date')
        attendance_list = data.get('attendance', [])
        
        # Validate input
        if not subject_id or not attendance_date or not attendance_list:
            return jsonify({'error': 'Subject ID, date, and attendance list are required'}), 400
        
        # Parse date
        try:
            attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Verify faculty teaches this subject
        subject = Subject.query.get(subject_id)
        if not subject or subject.faculty_id != session['user_id']:
            return jsonify({'error': 'You are not authorized to mark attendance for this subject'}), 403
        
        marked_count = 0
        duplicate_count = 0
        errors = []
        
        # Mark attendance for each student
        for record in attendance_list:
            student_id = record.get('student_id')
            status = record.get('status', 'Absent')
            
            if not student_id:
                errors.append('Student ID missing in attendance record')
                continue
            
            # Validate status
            if status not in ['Present', 'Absent', 'Late']:
                errors.append(f'Invalid status for student {student_id}: {status}')
                continue
            
            # Check for duplicate entry (same student, subject, date)
            existing = Attendance.query.filter_by(
                student_id=student_id,
                subject_id=subject_id,
                date=attendance_date
            ).first()
            
            if existing:
                # Update existing record instead of creating duplicate
                existing.status = status
                duplicate_count += 1
            else:
                # Create new attendance record
                new_attendance = Attendance(
                    student_id=student_id,
                    subject_id=subject_id,
                    date=attendance_date,
                    status=status
                )
                db.session.add(new_attendance)
                marked_count += 1
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Attendance marked successfully',
            'marked': marked_count,
            'updated': duplicate_count,
            'errors': errors if errors else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to mark attendance: {str(e)}'}), 500


@attendance_bp.route('/faculty/upload', methods=['POST'])
def faculty_upload_attendance():
    """
    Upload attendance via Excel file
    Excel format: Columns: student_id OR roll_no, subject_id OR subject_name, date, status
    """
    try:
        # Check if user is faculty
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty login required'}), 401
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Only .xlsx and .xls allowed'}), 400
        
        # Save file temporarily
        ensure_upload_folder()
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Read Excel file using pandas
        try:
            df = pd.read_excel(filepath)
        except Exception as e:
            os.remove(filepath)  # Clean up file
            return jsonify({'error': f'Failed to read Excel file: {str(e)}'}), 400
        
        # Validate required columns
        required_cols = ['date', 'status']
        if not all(col in df.columns for col in required_cols):
            os.remove(filepath)
            return jsonify({'error': f'Excel must contain columns: {", ".join(required_cols)}, and either student_id/roll_no and subject_id/subject_name'}), 400
        
        # Check for student identifier
        if 'student_id' not in df.columns and 'roll_no' not in df.columns:
            os.remove(filepath)
            return jsonify({'error': 'Excel must contain either student_id or roll_no column'}), 400
        
        # Check for subject identifier
        if 'subject_id' not in df.columns and 'subject_name' not in df.columns:
            os.remove(filepath)
            return jsonify({'error': 'Excel must contain either subject_id or subject_name column'}), 400
        
        success_count = 0
        duplicate_count = 0
        error_count = 0
        errors = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Get student
                if 'student_id' in df.columns and pd.notna(row['student_id']):
                    student = Student.query.get(int(row['student_id']))
                elif 'roll_no' in df.columns and pd.notna(row['roll_no']):
                    student = Student.query.filter_by(roll_no=str(row['roll_no'])).first()
                else:
                    errors.append(f'Row {index + 2}: No valid student identifier')
                    error_count += 1
                    continue
                
                if not student:
                    errors.append(f'Row {index + 2}: Student not found')
                    error_count += 1
                    continue
                
                # Get subject
                if 'subject_id' in df.columns and pd.notna(row['subject_id']):
                    subject = Subject.query.get(int(row['subject_id']))
                elif 'subject_name' in df.columns and pd.notna(row['subject_name']):
                    subject = Subject.query.filter_by(subject_name=str(row['subject_name'])).first()
                else:
                    errors.append(f'Row {index + 2}: No valid subject identifier')
                    error_count += 1
                    continue
                
                if not subject:
                    errors.append(f'Row {index + 2}: Subject not found')
                    error_count += 1
                    continue
                
                # Verify faculty teaches this subject
                if subject.faculty_id != session['user_id']:
                    errors.append(f'Row {index + 2}: You are not authorized to mark attendance for {subject.subject_name}')
                    error_count += 1
                    continue
                
                # Parse date
                if pd.notna(row['date']):
                    if isinstance(row['date'], str):
                        attendance_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    else:
                        attendance_date = row['date'].date() if hasattr(row['date'], 'date') else row['date']
                else:
                    errors.append(f'Row {index + 2}: Invalid date')
                    error_count += 1
                    continue
                
                # Get status
                status = str(row['status']).strip().capitalize()
                if status not in ['Present', 'Absent', 'Late']:
                    errors.append(f'Row {index + 2}: Invalid status "{status}". Must be Present, Absent, or Late')
                    error_count += 1
                    continue
                
                # Check for duplicate
                existing = Attendance.query.filter_by(
                    student_id=student.student_id,
                    subject_id=subject.subject_id,
                    date=attendance_date
                ).first()
                
                if existing:
                    # Update existing record
                    existing.status = status
                    duplicate_count += 1
                else:
                    # Create new record
                    new_attendance = Attendance(
                        student_id=student.student_id,
                        subject_id=subject.subject_id,
                        date=attendance_date,
                        status=status
                    )
                    db.session.add(new_attendance)
                    success_count += 1
                
            except Exception as e:
                errors.append(f'Row {index + 2}: {str(e)}')
                error_count += 1
        
        # Commit all changes
        db.session.commit()
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': f'Attendance upload completed',
            'inserted': success_count,
            'updated': duplicate_count,
            'errors': error_count,
            'error_details': errors if errors else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        # Clean up file if exists
        try:
            if 'filepath' in locals():
                os.remove(filepath)
        except:
            pass
        return jsonify({'error': f'Failed to upload attendance: {str(e)}'}), 500


@attendance_bp.route('/faculty/subjects', methods=['GET'])
def faculty_get_subjects():
    """
    Get all subjects taught by the faculty with enrolled student count
    """
    try:
        # Check if user is faculty
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty login required'}), 401
        
        # Get all subjects for this faculty
        subjects = Subject.query.filter_by(faculty_id=session['user_id']).all()
        
        subjects_data = []
        for subject in subjects:
            # Get enrolled students
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
            'subjects': subjects_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch subjects: {str(e)}'}), 500


@attendance_bp.route('/faculty/check', methods=['GET'])
def faculty_check_attendance():
    """
    Check if attendance has already been marked for a specific session
    Query params: subject_id, date, time_slot (optional)
    """
    try:
        # Check if user is faculty
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty login required'}), 401
        
        subject_id = request.args.get('subject_id', type=int)
        date_str = request.args.get('date')
        time_slot = request.args.get('time_slot')
        
        if not subject_id or not date_str:
            return jsonify({'error': 'subject_id and date are required'}), 400
        
        # Parse date
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Verify faculty teaches this subject
        subject = Subject.query.get(subject_id)
        if not subject or subject.faculty_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if attendance exists
        query = Attendance.query.filter_by(
            subject_id=subject_id,
            date=attendance_date
        )
        
        # Filter by time slot if provided
        if time_slot:
            query = query.filter_by(time_slot=time_slot)
        
        existing_attendance = query.all()
        
        if existing_attendance:
            # Return existing attendance data
            attendance_data = []
            for att in existing_attendance:
                attendance_data.append({
                    'student_id': att.student_id,
                    'status': att.status
                })
            
            return jsonify({
                'already_marked': True,
                'count': len(existing_attendance),
                'attendance': attendance_data
            }), 200
        else:
            return jsonify({
                'already_marked': False
            }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to check attendance: {str(e)}'}), 500


@attendance_bp.route('/faculty/students/<int:subject_id>', methods=['GET'])
def faculty_get_students_for_subject(subject_id):
    """
    Get all students enrolled in a specific subject
    """
    try:
        # Check if user is faculty
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            return jsonify({'error': 'Unauthorized - Faculty login required'}), 401
        
        # Verify faculty teaches this subject
        subject = Subject.query.get(subject_id)
        if not subject or subject.faculty_id != session['user_id']:
            return jsonify({'error': 'Unauthorized - You do not teach this subject'}), 403
        
        # Get enrolled students
        enrollments = StudentEnrollment.query.filter_by(
            subject_id=subject_id,
            status='active'
        ).all()
        
        students_data = []
        for enrollment in enrollments:
            student = enrollment.student
            
            # Calculate attendance percentage for this subject
            attendance_percentage = calculate_attendance_percentage(student.student_id, subject_id)
            
            students_data.append({
                'student_id': student.student_id,
                'roll_no': student.roll_no,
                'name': student.name,
                'department': student.department,
                'semester': student.semester,
                'attendance_percentage': attendance_percentage
            })
        
        return jsonify({
            'success': True,
            'subject': {
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name
            },
            'students': students_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch students: {str(e)}'}), 500


# ==================== STUDENT ROUTES ====================

@attendance_bp.route('/student/overview', methods=['GET'])
def student_attendance_overview():
    """
    Get attendance overview for the logged-in student
    Returns overall percentage and subject-wise breakdown
    """
    try:
        # Check if user is student
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({'error': 'Unauthorized - Student login required'}), 401
        
        student_id = session['user_id']
        
        # Calculate overall attendance
        overall_percentage = calculate_attendance_percentage(student_id)
        
        # Get subject-wise attendance
        enrollments = StudentEnrollment.query.filter_by(
            student_id=student_id,
            status='active'
        ).all()
        
        subjects_data = []
        for enrollment in enrollments:
            subject = enrollment.subject
            
            # Calculate subject attendance
            total_classes = Attendance.query.filter_by(
                student_id=student_id,
                subject_id=subject.subject_id
            ).count()
            
            attended = Attendance.query.filter_by(
                student_id=student_id,
                subject_id=subject.subject_id,
                status='Present'
            ).count()
            
            absent = Attendance.query.filter_by(
                student_id=student_id,
                subject_id=subject.subject_id,
                status='Absent'
            ).count()
            
            late = Attendance.query.filter_by(
                student_id=student_id,
                subject_id=subject.subject_id,
                status='Late'
            ).count()
            
            percentage = calculate_attendance_percentage(student_id, subject.subject_id)
            
            subjects_data.append({
                'subject_id': subject.subject_id,
                'subject_name': subject.subject_name,
                'total_classes': total_classes,
                'attended': attended,
                'absent': absent,
                'late': late,
                'percentage': percentage
            })
        
        return jsonify({
            'success': True,
            'overall_percentage': overall_percentage,
            'subjects': subjects_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch attendance: {str(e)}'}), 500


@attendance_bp.route('/student/records', methods=['GET'])
def student_attendance_records():
    """
    Get detailed attendance records for student
    Supports filtering by subject_id and date range
    Query params: subject_id (optional), start_date (optional), end_date (optional)
    """
    try:
        # Check if user is student
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({'error': 'Unauthorized - Student login required'}), 401
        
        student_id = session['user_id']
        
        # Build query
        query = Attendance.query.filter_by(student_id=student_id)
        
        # Filter by subject if provided
        subject_id = request.args.get('subject_id', type=int)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        # Filter by date range if provided
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date >= start_date)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date <= end_date)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        
        # Get records, ordered by date (most recent first)
        records = query.order_by(Attendance.date.desc()).all()
        
        records_data = []
        for record in records:
            records_data.append({
                'attendance_id': record.attendance_id,
                'subject_id': record.subject_id,
                'subject_name': record.subject.subject_name if record.subject else None,
                'date': record.date.isoformat() if record.date else None,
                'status': record.status
            })
        
        return jsonify({
            'success': True,
            'total_records': len(records_data),
            'records': records_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch records: {str(e)}'}), 500


# ==================== PAGE RENDERING ROUTES ====================
# These routes serve HTML pages (not API endpoints)

@attendance_bp.route('/faculty/page', methods=['GET'])
def faculty_attendance_page():
    """
    Render faculty attendance page
    """
    if 'user_id' not in session or session.get('user_type') != 'faculty':
        flash('Please log in as faculty to access this page', 'error')
        return redirect(url_for('serve_login', user_type='faculty'))
    
    faculty = Faculty.query.get(session['user_id'])
    subjects = Subject.query.filter_by(faculty_id=session['user_id']).all()
    
    return render_template('faculty/attendance.html', faculty=faculty, subjects=subjects)


@attendance_bp.route('/student/page', methods=['GET'])
def student_attendance_page():
    """
    Render student attendance page
    """
    if 'user_id' not in session or session.get('user_type') != 'student':
        flash('Please log in as student to access this page', 'error')
        return redirect(url_for('serve_login', user_type='student'))
    
    student = Student.query.get(session['user_id'])
    
    # Get student's subjects
    enrollments = StudentEnrollment.query.filter_by(
        student_id=session['user_id'],
        status='active'
    ).all()
    
    subjects = [enrollment.subject for enrollment in enrollments]
    
    return render_template('student/attendance.html', student=student, subjects=subjects)
