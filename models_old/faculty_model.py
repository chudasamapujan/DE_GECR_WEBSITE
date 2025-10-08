"""
Faculty Model for GEC Rajkot Website
SQLAlchemy model for faculty data management
Author: GEC Rajkot Development Team
"""

from datetime import datetime
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Faculty(db.Model):
    __tablename__ = 'faculty'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    
    # Professional Information
    employee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    designation = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    qualification = db.Column(db.String(200))
    specialization = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    joining_date = db.Column(db.Date, nullable=False)
    office_room = db.Column(db.String(20))
    office_hours = db.Column(db.String(100))
    
    # Research Information
    research_interests = db.Column(db.Text)
    publications = db.Column(db.Text)
    research_projects = db.Column(db.Text)
    
    # Contact Information
    office_phone = db.Column(db.String(15))
    personal_website = db.Column(db.String(200))
    linkedin_profile = db.Column(db.String(200))
    
    # Account Information
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # courses = db.relationship('Course', backref='faculty', lazy=True)
    # assignments = db.relationship('Assignment', backref='faculty', lazy=True)
    # announcements = db.relationship('Announcement', backref='faculty', lazy=True)

    def __init__(self, **kwargs):
        super(Faculty, self).__init__(**kwargs)
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
    def display_name(self):
        """Get display name with designation"""
        return f"{self.designation} {self.full_name}"

    @property
    def years_of_service(self):
        """Calculate years of service"""
        if self.joining_date:
            today = datetime.now().date()
            years = today.year - self.joining_date.year
            if today.month < self.joining_date.month or \
               (today.month == self.joining_date.month and today.day < self.joining_date.day):
                years -= 1
            return max(0, years)
        return 0

    def to_dict(self, include_sensitive=False):
        """Convert faculty object to dictionary"""
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'display_name': self.display_name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'address': self.address,
            'employee_id': self.employee_id,
            'designation': self.designation,
            'department': self.department,
            'qualification': self.qualification,
            'specialization': self.specialization,
            'experience_years': self.experience_years,
            'years_of_service': self.years_of_service,
            'joining_date': self.joining_date.isoformat() if self.joining_date else None,
            'office_room': self.office_room,
            'office_hours': self.office_hours,
            'research_interests': self.research_interests,
            'publications': self.publications,
            'research_projects': self.research_projects,
            'office_phone': self.office_phone,
            'personal_website': self.personal_website,
            'linkedin_profile': self.linkedin_profile,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data

    def update_from_dict(self, data):
        """Update faculty from dictionary data"""
        updatable_fields = [
            'first_name', 'last_name', 'phone', 'date_of_birth', 'address',
            'designation', 'qualification', 'specialization', 'experience_years',
            'office_room', 'office_hours', 'research_interests', 'publications',
            'research_projects', 'office_phone', 'personal_website', 'linkedin_profile'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
        
        self.updated_at = datetime.utcnow()

    @classmethod
    def find_by_email(cls, email):
        """Find faculty by email"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_employee_id(cls, employee_id):
        """Find faculty by employee ID"""
        return cls.query.filter_by(employee_id=employee_id).first()

    @classmethod
    def find_active_faculty(cls):
        """Get all active faculty"""
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def find_by_department(cls, department):
        """Find faculty by department"""
        return cls.query.filter_by(department=department, is_active=True).all()

    @classmethod
    def find_by_designation(cls, designation):
        """Find faculty by designation"""
        return cls.query.filter_by(designation=designation, is_active=True).all()

    @classmethod
    def find_admins(cls):
        """Get all admin faculty"""
        return cls.query.filter_by(is_admin=True, is_active=True).all()

    @classmethod
    def search_faculty(cls, query, department=None, designation=None):
        """Search faculty by name, employee ID, or email"""
        base_query = cls.query.filter_by(is_active=True)
        
        if department:
            base_query = base_query.filter_by(department=department)
        
        if designation:
            base_query = base_query.filter_by(designation=designation)
        
        if query:
            search_filter = db.or_(
                cls.first_name.ilike(f'%{query}%'),
                cls.last_name.ilike(f'%{query}%'),
                cls.employee_id.ilike(f'%{query}%'),
                cls.email.ilike(f'%{query}%'),
                cls.designation.ilike(f'%{query}%')
            )
            base_query = base_query.filter(search_filter)
        
        return base_query.all()

    def get_subjects_taught(self):
        """Get list of subjects taught by this faculty"""
        # Placeholder for relationship with Course/Subject model
        # return [course.subject_name for course in self.courses]
        return []

    def get_student_count(self):
        """Get number of students taught by this faculty"""
        # Placeholder for counting students across all courses
        # return sum([course.enrolled_students_count for course in self.courses])
        return 0

    def __repr__(self):
        return f'<Faculty {self.employee_id}: {self.full_name}>'