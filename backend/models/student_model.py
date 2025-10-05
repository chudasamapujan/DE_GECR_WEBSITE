"""
Student Model for GEC Rajkot Website
SQLAlchemy model for student data management
Author: GEC Rajkot Development Team
"""

from datetime import datetime
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Student(db.Model):
    __tablename__ = 'students'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    blood_group = db.Column(db.String(5))
    
    # Guardian Information
    guardian_name = db.Column(db.String(100))
    guardian_phone = db.Column(db.String(15))
    emergency_contact = db.Column(db.String(15))
    
    # Academic Information
    enrollment_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    department = db.Column(db.String(50), nullable=False)
    admission_year = db.Column(db.Integer, nullable=False)
    current_semester = db.Column(db.Integer, nullable=False)
    roll_number = db.Column(db.String(20), nullable=False)
    
    # Account Information
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    # assignment_submissions = db.relationship('AssignmentSubmission', backref='student', lazy=True)
    # grades = db.relationship('Grade', backref='student', lazy=True)

    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])

    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def current_academic_year(self):
        """Calculate current academic year based on admission year and semester"""
        return self.admission_year + ((self.current_semester - 1) // 2)

    def to_dict(self, include_sensitive=False):
        """Convert student object to dictionary"""
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'address': self.address,
            'blood_group': self.blood_group,
            'guardian_name': self.guardian_name,
            'guardian_phone': self.guardian_phone,
            'emergency_contact': self.emergency_contact,
            'enrollment_number': self.enrollment_number,
            'department': self.department,
            'admission_year': self.admission_year,
            'current_semester': self.current_semester,
            'current_academic_year': self.current_academic_year,
            'roll_number': self.roll_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data

    def update_from_dict(self, data):
        """Update student from dictionary data"""
        updatable_fields = [
            'first_name', 'last_name', 'phone', 'address', 'blood_group',
            'guardian_name', 'guardian_phone', 'emergency_contact',
            'current_semester'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
        
        self.updated_at = datetime.utcnow()

    @classmethod
    def find_by_email(cls, email):
        """Find student by email"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_enrollment(cls, enrollment_number):
        """Find student by enrollment number"""
        return cls.query.filter_by(enrollment_number=enrollment_number).first()

    @classmethod
    def find_active_students(cls):
        """Get all active students"""
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def find_by_department(cls, department):
        """Find students by department"""
        return cls.query.filter_by(department=department, is_active=True).all()

    @classmethod
    def find_by_semester(cls, semester):
        """Find students by current semester"""
        return cls.query.filter_by(current_semester=semester, is_active=True).all()

    @classmethod
    def search_students(cls, query, department=None, semester=None):
        """Search students by name, enrollment number, or email"""
        base_query = cls.query.filter_by(is_active=True)
        
        if department:
            base_query = base_query.filter_by(department=department)
        
        if semester:
            base_query = base_query.filter_by(current_semester=semester)
        
        if query:
            search_filter = db.or_(
                cls.first_name.ilike(f'%{query}%'),
                cls.last_name.ilike(f'%{query}%'),
                cls.enrollment_number.ilike(f'%{query}%'),
                cls.email.ilike(f'%{query}%')
            )
            base_query = base_query.filter(search_filter)
        
        return base_query.all()

    def __repr__(self):
        return f'<Student {self.enrollment_number}: {self.full_name}>'