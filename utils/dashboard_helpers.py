"""
Dashboard Data Access Functions
Functions to fetch and aggregate data for student and faculty dashboards
"""

from models.gecr_models import (
    Student, Faculty, Subject, Timetable, Attendance, 
    Assignment, Submission, Message, Fee, Salary, StudentEnrollment
)
from database import db
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from collections import defaultdict


def get_student_dashboard_data(student_id):
    """
    Get comprehensive dashboard data for a student
    """
    try:
        # Get student info
        student = Student.query.get(student_id)
        if not student:
            return None
        
        # Calculate attendance percentage
        total_classes = Attendance.query.filter_by(student_id=student_id).count()
        attended_classes = Attendance.query.filter_by(
            student_id=student_id, 
            status='Present'
        ).count()
        attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Get pending assignments
        pending_assignments = Assignment.query.filter(
            ~Assignment.assignment_id.in_(
                db.session.query(Submission.assignment_id).filter_by(student_id=student_id)
            ),
            Assignment.due_date >= datetime.now()
        ).order_by(Assignment.due_date).all()
        
        # Get recent submissions
        recent_submissions = Submission.query.filter_by(
            student_id=student_id
        ).order_by(desc(Submission.submitted_at)).limit(5).all()
        
        # Get enrolled subjects (using StudentEnrollment table)
        enrolled_subjects = []
        enrollments = StudentEnrollment.query.filter_by(
            student_id=student_id,
            status='active'
        ).all()
        
        for enrollment in enrollments:
            if enrollment.subject:
                enrolled_subjects.append(enrollment.subject)
        
        # Get today's schedule (based on enrolled subjects)
        today = datetime.now().strftime('%A')
        enrolled_subject_ids = [s.subject_id for s in enrolled_subjects]
        today_schedule = []
        if enrolled_subject_ids:
            today_schedule = Timetable.query.filter(
                Timetable.subject_id.in_(enrolled_subject_ids),
                Timetable.day_of_week == today
            ).order_by(Timetable.time_slot).all()
        
        # Get recent messages/announcements
        recent_messages = Message.query.filter_by(
            receiver_type='student'
        ).order_by(desc(Message.timestamp)).limit(5).all()
        
        # Calculate average grades (mock calculation based on submissions)
        completed_submissions = Submission.query.filter_by(student_id=student_id).all()
        
        # Convert letter grades to numeric values for calculation
        grade_map = {'A+': 95, 'A': 90, 'B+': 85, 'B': 80, 'C+': 75, 'C': 70, 'D': 60}
        total_marks = sum([grade_map.get(s.grade, 0) for s in completed_submissions if s.grade])
        total_assignments = len([s for s in completed_submissions if s.grade])
        avg_grade = (total_marks / total_assignments) if total_assignments > 0 else 0
        
        # Convert to CGPA scale (assuming 10-point scale)
        cgpa = (avg_grade / 100) * 10 if avg_grade > 0 else 0
        
        # Get fees status
        fees_record = Fee.query.filter_by(student_id=student_id).first()
        fees_paid = fees_record.status == 'Paid' if fees_record else False
        
        return {
            'student': student,
            'attendance_percentage': round(attendance_percentage, 1),
            'cgpa': round(cgpa, 1),
            'pending_assignments': pending_assignments,
            'pending_assignments_count': len(pending_assignments),
            'recent_submissions': recent_submissions,
            'current_subjects': enrolled_subjects,
            'today_schedule': today_schedule,
            'recent_messages': recent_messages,
            'fees_paid': fees_paid,
            'total_classes': total_classes,
            'attended_classes': attended_classes
        }
        
    except Exception as e:
        print(f"Error fetching student dashboard data: {e}")
        return None


def get_faculty_dashboard_data(faculty_id):
    """
    Get comprehensive dashboard data for a faculty member
    """
    try:
        # Get faculty info
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return None
        
        # Get subjects taught by faculty
        faculty_subjects = Subject.query.filter_by(faculty_id=faculty_id).all()
        
        # Count total students across all subjects
        total_students = 0
        for subject in faculty_subjects:
            # Students in the subject's semester and department
            subject_students = Student.query.filter_by(
                semester=subject.semester,
                department=faculty.department
            ).count()
            total_students += subject_students
        
        # Get pending assignments to grade
        pending_assignments = Assignment.query.filter_by(faculty_id=faculty_id).all()
        total_assignments = len(pending_assignments)
        pending_submissions = []
        for assignment in pending_assignments:
            ungraded = Submission.query.filter_by(
                assignment_id=assignment.assignment_id,
                grade=None  # Ungraded submissions
            ).count()
            if ungraded > 0:
                pending_submissions.append({
                    'assignment': assignment,
                    'ungraded_count': ungraded
                })
        
        # Get today's schedule
        today = datetime.now().strftime('%A')
        today_schedule = Timetable.query.filter_by(
            faculty_id=faculty_id,
            day_of_week=today
        ).order_by(Timetable.time_slot).all()
        
        # Get recent activities (assignments created, submissions graded)
        recent_assignments = Assignment.query.filter_by(
            faculty_id=faculty_id
        ).order_by(desc(Assignment.due_date)).limit(3).all()
        
        recent_graded = Submission.query.join(Assignment).filter(
            Assignment.faculty_id == faculty_id,
            Submission.grade.isnot(None)
        ).order_by(desc(Submission.submitted_at)).limit(3).all()
        
        # Get recent messages/announcements
        recent_messages = Message.query.filter_by(
            sender_id=faculty_id,
            sender_type='faculty'
        ).order_by(desc(Message.timestamp)).limit(5).all()
        
        # Get salary information
        salary_record = Salary.query.filter_by(faculty_id=faculty_id).first()
        current_salary = salary_record.amount if salary_record else faculty.salary
        
        # Get recent activities for the dashboard
        recent_activities = get_faculty_recent_activities(faculty_id, faculty_subjects)
        
        return {
            'faculty': faculty,
            'faculty_subjects': faculty_subjects,
            'total_subjects': len(faculty_subjects),
            'total_students': total_students,
            'total_assignments': total_assignments,
            'pending_submissions': pending_submissions,
            'pending_submissions_count': len(pending_submissions),
            'today_schedule': today_schedule,
            'today_classes_count': len(today_schedule),
            'recent_assignments': recent_assignments,
            'recent_graded': recent_graded,
            'recent_messages': recent_messages,
            'current_salary': current_salary,
            'recent_activities': recent_activities
        }
        
    except Exception as e:
        print(f"Error fetching faculty dashboard data: {e}")
        return None


def get_student_attendance_data(student_id):
    """
    Get detailed attendance data for a student
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return None
        
        # Get attendance records with subject details
        attendance_records = db.session.query(
            Attendance, Subject, Faculty
        ).join(
            Subject, Attendance.subject_id == Subject.subject_id
        ).join(
            Faculty, Subject.faculty_id == Faculty.faculty_id
        ).filter(
            Attendance.student_id == student_id
        ).order_by(desc(Attendance.date)).all()
        
        # Group by subject
        subject_attendance = defaultdict(lambda: {
            'present': 0, 'total': 0, 'percentage': 0, 'subject': None
        })
        
        for attendance, subject, faculty in attendance_records:
            subject_key = subject.subject_id
            subject_attendance[subject_key]['subject'] = subject
            subject_attendance[subject_key]['faculty'] = faculty
            subject_attendance[subject_key]['total'] += 1
            if attendance.status == 'Present':
                subject_attendance[subject_key]['present'] += 1
        
        # Calculate percentages
        for subject_id in subject_attendance:
            data = subject_attendance[subject_id]
            data['percentage'] = (data['present'] / data['total'] * 100) if data['total'] > 0 else 0
        
        return {
            'student': student,
            'attendance_records': attendance_records,
            'subject_attendance': dict(subject_attendance)
        }
        
    except Exception as e:
        print(f"Error fetching student attendance data: {e}")
        return None


def get_student_grades_data(student_id):
    """
    Get grades and academic performance data for a student
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return None
        
        # Get submissions with assignment and subject details
        submissions = db.session.query(
            Submission, Assignment, Subject, Faculty
        ).join(
            Assignment, Submission.assignment_id == Assignment.assignment_id
        ).join(
            Subject, Assignment.subject_id == Subject.subject_id
        ).join(
            Faculty, Subject.faculty_id == Faculty.faculty_id
        ).filter(
            Submission.student_id == student_id
        ).order_by(desc(Submission.submitted_at)).all()
        
        # Group by subject with grade mapping
        grade_map = {'A+': 95, 'A': 90, 'B+': 85, 'B': 80, 'C+': 75, 'C': 70, 'D': 60}
        subject_grades = defaultdict(lambda: {
            'assignments': [], 'total_points': 0, 'assignment_count': 0, 'average': 0
        })
        
        for submission, assignment, subject, faculty in submissions:
            subject_key = subject.subject_id
            subject_grades[subject_key]['subject'] = subject
            subject_grades[subject_key]['faculty'] = faculty
            subject_grades[subject_key]['assignments'].append({
                'assignment': assignment,
                'submission': submission
            })
            if submission.grade and submission.grade in grade_map:
                subject_grades[subject_key]['total_points'] += grade_map[submission.grade]
                subject_grades[subject_key]['assignment_count'] += 1
        
        # Calculate averages
        for subject_id in subject_grades:
            data = subject_grades[subject_id]
            data['average'] = (data['total_points'] / data['assignment_count']) if data['assignment_count'] > 0 else 0
        
        return {
            'student': student,
            'submissions': submissions,
            'subject_grades': dict(subject_grades)
        }
        
    except Exception as e:
        print(f"Error fetching student grades data: {e}")
        return None


def get_faculty_students_data(faculty_id):
    """
    Get students data for a faculty member
    """
    try:
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return None
        
        # Get subjects taught by faculty
        faculty_subjects = Subject.query.filter_by(faculty_id=faculty_id).all()
        
        # Get students for each subject
        subject_students = {}
        all_students = set()
        
        for subject in faculty_subjects:
            # Students in the subject's semester and department
            students = Student.query.filter_by(
                semester=subject.semester,
                department=faculty.department
            ).all()
            subject_students[subject.subject_id] = {
                'subject': subject,
                'students': students
            }
            all_students.update(students)
        
        return {
            'faculty': faculty,
            'faculty_subjects': faculty_subjects,
            'subject_students': subject_students,
            'all_students': list(all_students),
            'total_students': len(all_students)
        }
        
    except Exception as e:
        print(f"Error fetching faculty students data: {e}")
        return None


def get_faculty_assignments_data(faculty_id):
    """
    Get assignments data for a faculty member
    """
    try:
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return None
        
        # Get assignments created by faculty
        assignments = Assignment.query.filter_by(
            faculty_id=faculty_id
        ).order_by(desc(Assignment.due_date)).all()
        
        # Get submission statistics for each assignment
        assignment_stats = []
        for assignment in assignments:
            total_submissions = Submission.query.filter_by(
                assignment_id=assignment.assignment_id
            ).count()
            graded_submissions = Submission.query.filter_by(
                assignment_id=assignment.assignment_id
            ).filter(Submission.grade.isnot(None)).count()
            
            assignment_stats.append({
                'assignment': assignment,
                'total_submissions': total_submissions,
                'graded_submissions': graded_submissions,
                'pending_grading': total_submissions - graded_submissions
            })
        
        return {
            'faculty': faculty,
            'assignments': assignments,
            'assignment_stats': assignment_stats
        }
        
    except Exception as e:
        print(f"Error fetching faculty assignments data: {e}")
        return None


def get_faculty_recent_activities(faculty_id, faculty_subjects):
    """
    Get recent activities for a faculty member's dashboard
    Combines attendance sessions, graded submissions, created assignments, etc.
    """
    try:
        from models.gecr_models import AttendanceSession, Attendance, Announcement, Event
        
        activities = []
        now = datetime.now()
        
        # Get subject IDs for this faculty
        subject_ids = [s.subject_id for s in faculty_subjects]
        
        # 1. Recent attendance sessions (marked attendance)
        recent_sessions = AttendanceSession.query.filter_by(
            faculty_id=faculty_id
        ).order_by(desc(AttendanceSession.created_at)).limit(5).all()
        
        for session in recent_sessions:
            # Count students who attended this session
            attendance_count = Attendance.query.filter_by(
                session_id=session.session_id,
                status='Present'
            ).count()
            
            time_diff = now - session.created_at if session.created_at else timedelta(days=0)
            
            activities.append({
                'type': 'attendance',
                'icon': 'check-circle',
                'description': f"Marked attendance for {session.subject.subject_name if session.subject else 'Unknown'}",
                'detail': f"{attendance_count} students • {format_time_ago(time_diff)}",
                'timestamp': session.created_at,
                'link': '/faculty/attendance'
            })
        
        # 2. Recently graded submissions
        recent_graded = Submission.query.join(Assignment).filter(
            Assignment.faculty_id == faculty_id,
            Submission.grade.isnot(None)
        ).order_by(desc(Submission.submitted_at)).limit(5).all()
        
        for submission in recent_graded:
            if submission.submitted_at:
                time_diff = now - datetime.combine(submission.submitted_at, datetime.min.time())
                activities.append({
                    'type': 'grading',
                    'icon': 'clipboard-check',
                    'description': f"Graded {submission.assignment.title if submission.assignment else 'Assignment'}",
                    'detail': f"Grade: {submission.grade} • {format_time_ago(time_diff)}",
                    'timestamp': datetime.combine(submission.submitted_at, datetime.min.time()),
                    'link': '/faculty/assignments'
                })
        
        # 3. Recently created assignments
        recent_assignments = Assignment.query.filter_by(
            faculty_id=faculty_id
        ).order_by(desc(Assignment.assignment_id)).limit(5).all()
        
        for assignment in recent_assignments:
            # Use due_date as proxy for creation time
            if assignment.due_date:
                # Estimate creation as a few days before due date
                estimated_created = datetime.combine(assignment.due_date, datetime.min.time()) - timedelta(days=7)
                time_diff = now - estimated_created
                activities.append({
                    'type': 'assignment',
                    'icon': 'document-add',
                    'description': f"Created assignment: {assignment.title}",
                    'detail': f"Due: {assignment.due_date.strftime('%b %d, %Y') if assignment.due_date else 'No date'} • {format_time_ago(time_diff)}",
                    'timestamp': estimated_created,
                    'link': '/faculty/assignments'
                })
        
        # 4. Recent announcements created
        try:
            recent_announcements = Announcement.query.filter_by(
                author_id=faculty_id
            ).order_by(desc(Announcement.created_at)).limit(3).all()
            
            for ann in recent_announcements:
                if ann.created_at:
                    time_diff = now - ann.created_at
                    activities.append({
                        'type': 'announcement',
                        'icon': 'speakerphone',
                        'description': f"Posted announcement: {ann.title[:30]}{'...' if len(ann.title) > 30 else ''}",
                        'detail': format_time_ago(time_diff),
                        'timestamp': ann.created_at,
                        'link': '/faculty/manage-announcements'
                    })
        except Exception:
            pass  # Announcement model may not exist
        
        # 5. Recent events created
        try:
            recent_events = Event.query.filter_by(
                created_by=faculty_id
            ).order_by(desc(Event.start_time)).limit(3).all()
            
            for event in recent_events:
                if event.start_time:
                    time_diff = now - event.start_time
                    activities.append({
                        'type': 'event',
                        'icon': 'calendar',
                        'description': f"Created event: {event.title[:30]}{'...' if len(event.title) > 30 else ''}",
                        'detail': format_time_ago(time_diff),
                        'timestamp': event.start_time,
                        'link': '/faculty/events'
                    })
        except Exception:
            pass  # Event model may not exist
        
        # Sort all activities by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min, reverse=True)
        
        # Return top 5 activities
        return activities[:5]
        
    except Exception as e:
        print(f"Error fetching recent activities: {e}")
        return []


def format_time_ago(time_diff):
    """Format a timedelta as a human-readable string"""
    if time_diff.days > 7:
        weeks = time_diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif time_diff.days > 0:
        return f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
    elif time_diff.seconds > 3600:
        hours = time_diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif time_diff.seconds > 60:
        minutes = time_diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"