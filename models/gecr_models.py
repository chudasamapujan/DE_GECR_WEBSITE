"""
GECR Database Models
Redesigned database schema for Government Engineering College Rajkot
Simple and efficient structure for academic management
"""

from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date


class Student(db.Model):
    """Students table - simplified student information"""
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50))
    semester = db.Column(db.Integer)
    dob = db.Column(db.Date)
    address = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    fees_paid = db.Column(db.Boolean, default=False)
    email_notifications_enabled = db.Column(db.Boolean, default=True)  # Email notification preference
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    submissions = db.relationship('Submission', backref='student', lazy=True)
    fees_records = db.relationship('Fee', backref='student', lazy=True)
    enrollments = db.relationship('StudentEnrollment', backref='student', lazy=True)
    
    def get_enrolled_subjects(self):
        """Get all subjects this student is enrolled in"""
        from models.gecr_models import StudentEnrollment
        enrollments = StudentEnrollment.query.filter_by(student_id=self.student_id, status='active').all()
        return [enrollment.subject for enrollment in enrollments]
    
    def is_enrolled_in_subject(self, subject_id):
        """Check if student is enrolled in a specific subject"""
        from models.gecr_models import StudentEnrollment
        enrollment = StudentEnrollment.query.filter_by(
            student_id=self.student_id,
            subject_id=subject_id,
            status='active'
        ).first()
        return enrollment is not None
    
    def set_password(self, password):
        """Set password hash"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password, password)
    
    @classmethod
    def find_by_email(cls, email):
        """Find student by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_roll_no(cls, roll_no):
        """Find student by roll number"""
        return cls.query.filter_by(roll_no=roll_no).first()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'student_id': self.student_id,
            'roll_no': self.roll_no,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'semester': self.semester,
            'dob': self.dob.isoformat() if self.dob else None,
            'address': self.address,
            'phone': self.phone,
            'fees_paid': self.fees_paid
        }


class Faculty(db.Model):
    """Faculty table - simplified faculty information"""
    __tablename__ = 'faculty'
    
    faculty_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50))
    designation = db.Column(db.String(50))
    salary = db.Column(db.Integer, default=0)
    phone = db.Column(db.String(15))
    
    # Relationships
    subjects = db.relationship('Subject', backref='faculty', lazy=True)
    timetable_slots = db.relationship('Timetable', backref='faculty', lazy=True)
    assignments = db.relationship('Assignment', backref='faculty', lazy=True)
    salary_records = db.relationship('Salary', backref='faculty', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password, password)
    
    @classmethod
    def find_by_email(cls, email):
        """Find faculty by email"""
        return cls.query.filter_by(email=email).first()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'faculty_id': self.faculty_id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'designation': self.designation,
            'salary': self.salary,
            'phone': self.phone
        }


class Subject(db.Model):
    """Subjects table"""
    __tablename__ = 'subjects'
    
    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50))
    semester = db.Column(db.Integer)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'))
    
    # Relationships
    timetable_slots = db.relationship('Timetable', backref='subject', lazy=True)
    attendance_records = db.relationship('Attendance', backref='subject', lazy=True)
    assignments = db.relationship('Assignment', backref='subject', lazy=True)
    enrollments = db.relationship('StudentEnrollment', backref='subject', lazy=True)
    
    def get_enrolled_students(self):
        """Get all students enrolled in this subject"""
        from models.gecr_models import StudentEnrollment, Student
        enrollments = StudentEnrollment.query.filter_by(subject_id=self.subject_id).all()
        return [enrollment.student for enrollment in enrollments]
    
    def get_enrollment_count(self):
        """Get count of enrolled students"""
        from models.gecr_models import StudentEnrollment
        return StudentEnrollment.query.filter_by(subject_id=self.subject_id).count()
    
    def is_student_enrolled(self, student_id):
        """Check if a student is enrolled in this subject"""
        from models.gecr_models import StudentEnrollment
        enrollment = StudentEnrollment.query.filter_by(
            subject_id=self.subject_id,
            student_id=student_id
        ).first()
        return enrollment is not None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'subject_id': self.subject_id,
            'subject_name': self.subject_name,
            'department': self.department,
            'semester': self.semester,
            'faculty_id': self.faculty_id,
            'faculty_name': self.faculty.name if self.faculty else None,
            'enrollment_count': self.get_enrollment_count()
        }


class StudentEnrollment(db.Model):
    """Student-Subject Enrollment table - links students to subjects they are enrolled in"""
    __tablename__ = 'student_enrollments'
    
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    academic_year = db.Column(db.String(20))  # e.g., "2024-2025"
    status = db.Column(db.String(20), default='active')  # active, dropped, completed
    
    # Unique constraint to prevent duplicate enrollments
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', name='unique_student_subject'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'enrollment_id': self.enrollment_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'student_roll_no': self.student.roll_no if self.student else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.subject_name if self.subject else None,
            'enrollment_date': self.enrollment_date.strftime('%Y-%m-%d') if self.enrollment_date else None,
            'academic_year': self.academic_year,
            'status': self.status
        }


class Timetable(db.Model):
    """Timetable table"""
    __tablename__ = 'timetable'
    
    timetable_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department = db.Column(db.String(50))
    semester = db.Column(db.Integer)
    day_of_week = db.Column(db.String(10))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'))
    time_slot = db.Column(db.String(20))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'timetable_id': self.timetable_id,
            'department': self.department,
            'semester': self.semester,
            'day_of_week': self.day_of_week,
            'subject_id': self.subject_id,
            'faculty_id': self.faculty_id,
            'time_slot': self.time_slot,
            'subject_name': self.subject.subject_name if self.subject else None,
            'faculty_name': self.faculty.name if self.faculty else None
        }


class Attendance(db.Model):
    """Attendance table"""
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))
    date = db.Column(db.Date)
    status = db.Column(db.String(10))  # Present, Absent, Late
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'attendance_id': self.attendance_id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'student_name': self.student.name if self.student else None,
            'subject_name': self.subject.subject_name if self.subject else None
        }


class Announcement(db.Model):
    """Announcements for dashboard and site-wide notices"""
    __tablename__ = 'announcements'

    announcement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'announcement_id': self.announcement_id,
            'title': self.title,
            'message': self.message,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


class Event(db.Model):
    """Upcoming events for the dashboard"""
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=True)

    def to_dict(self):
        return {
            'event_id': self.event_id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,
            'created_by': self.created_by
        }


class EventRegistration(db.Model):
    """Registrations for events by students"""
    __tablename__ = 'event_registrations'

    registration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    event = db.relationship('Event', backref='registrations', lazy=True)
    student = db.relationship('Student', backref='event_registrations', lazy=True)

    def to_dict(self):
        return {
            'registration_id': self.registration_id,
            'event_id': self.event_id,
            'student_id': self.student_id,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'student_name': self.student.name if self.student else None,
            'event_title': self.event.title if self.event else None
        }


class Activity(db.Model):
    """Recent activities (audit-like) for dashboards"""
    __tablename__ = 'activities'

    activity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50))
    title = db.Column(db.String(200))
    details = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'activity_id': self.activity_id,
            'type': self.type,
            'title': self.title,
            'details': self.details,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Assignment(db.Model):
    """Assignments table"""
    __tablename__ = 'assignments'
    
    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'))
    due_date = db.Column(db.Date)
    
    # Relationships
    submissions = db.relationship('Submission', backref='assignment', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'assignment_id': self.assignment_id,
            'title': self.title,
            'description': self.description,
            'subject_id': self.subject_id,
            'faculty_id': self.faculty_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'subject_name': self.subject.subject_name if self.subject else None,
            'faculty_name': self.faculty.name if self.faculty else None
        }


class Submission(db.Model):
    """Submissions table"""
    __tablename__ = 'submissions'
    
    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    submitted_at = db.Column(db.Date)
    file_path = db.Column(db.String(200))
    grade = db.Column(db.String(5))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'submission_id': self.submission_id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'file_path': self.file_path,
            'grade': self.grade,
            'student_name': self.student.name if self.student else None,
            'assignment_title': self.assignment.title if self.assignment else None
        }


class Message(db.Model):
    """Messages table"""
    __tablename__ = 'messages'
    
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer)
    sender_type = db.Column(db.String(10))  # student, faculty
    receiver_id = db.Column(db.Integer)
    receiver_type = db.Column(db.String(10))  # student, faculty
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'sender_type': self.sender_type,
            'receiver_id': self.receiver_id,
            'receiver_type': self.receiver_type,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Fee(db.Model):
    """Fees table"""
    __tablename__ = 'fees'
    
    fee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    amount = db.Column(db.Integer)
    status = db.Column(db.String(10))  # Paid, Pending, Overdue
    due_date = db.Column(db.Date)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'fee_id': self.fee_id,
            'student_id': self.student_id,
            'amount': self.amount,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'student_name': self.student.name if self.student else None
        }


class Salary(db.Model):
    """Salary table"""
    __tablename__ = 'salary'
    
    salary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'))
    month = db.Column(db.String(10))
    amount = db.Column(db.Integer)
    status = db.Column(db.String(10))  # Paid, Pending
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'salary_id': self.salary_id,
            'faculty_id': self.faculty_id,
            'month': self.month,
            'amount': self.amount,
            'status': self.status,
            'faculty_name': self.faculty.name if self.faculty else None
        }


class Notification(db.Model):
    """Notifications for students - announcements, events, updates"""
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)  # Student or Faculty ID
    user_type = db.Column(db.String(20), nullable=False)  # 'student' or 'faculty'
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # 'announcement', 'event', 'attendance', 'assignment', 'general'
    link = db.Column(db.String(200))  # Optional link to related content
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'link': self.link,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
