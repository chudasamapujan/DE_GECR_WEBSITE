"""
OTP Model for GEC Rajkot Website
SQLAlchemy model for OTP verification management
Author: GEC Rajkot Development Team
"""

from datetime import datetime, timedelta
from database import db
import secrets
import string

class OTP(db.Model):
    __tablename__ = 'otps'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # OTP Information
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # 'registration', 'forgot_password', 'email_verification'
    user_type = db.Column(db.String(20), nullable=False)  # 'student', 'faculty'
    
    # Status and Validation
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    is_expired = db.Column(db.Boolean, default=False, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    max_attempts = db.Column(db.Integer, default=3, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    
    # Additional Data
    additional_data = db.Column(db.Text)  # JSON string for storing extra info if needed

    def __init__(self, email, purpose, user_type, expiry_minutes=10, **kwargs):
        super(OTP, self).__init__(**kwargs)
        self.email = email
        self.purpose = purpose
        self.user_type = user_type
        self.otp_code = self.generate_otp()
        self.expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))

    def verify_otp(self, provided_otp):
        """Verify the provided OTP"""
        # Check if OTP is already used
        if self.is_used:
            return False, "OTP has already been used"
        
        # Check if OTP is expired
        if self.is_expired or datetime.utcnow() > self.expires_at:
            self.is_expired = True
            db.session.commit()
            return False, "OTP has expired"
        
        # Check if max attempts exceeded
        if self.attempts >= self.max_attempts:
            self.is_expired = True
            db.session.commit()
            return False, "Maximum verification attempts exceeded"
        
        # Increment attempts
        self.attempts += 1
        
        # Check if OTP matches
        if self.otp_code == provided_otp:
            self.is_used = True
            self.used_at = datetime.utcnow()
            db.session.commit()
            return True, "OTP verified successfully"
        else:
            db.session.commit()
            remaining_attempts = self.max_attempts - self.attempts
            if remaining_attempts > 0:
                return False, f"Invalid OTP. {remaining_attempts} attempts remaining"
            else:
                self.is_expired = True
                db.session.commit()
                return False, "Invalid OTP. Maximum attempts exceeded"

    def is_valid(self):
        """Check if OTP is still valid"""
        return (not self.is_used and 
                not self.is_expired and 
                datetime.utcnow() <= self.expires_at and 
                self.attempts < self.max_attempts)

    def time_remaining(self):
        """Get remaining time for OTP validity in seconds"""
        if self.expires_at > datetime.utcnow():
            return int((self.expires_at - datetime.utcnow()).total_seconds())
        return 0

    def mark_expired(self):
        """Mark OTP as expired"""
        self.is_expired = True
        db.session.commit()

    def to_dict(self, include_sensitive=False):
        """Convert OTP object to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'purpose': self.purpose,
            'user_type': self.user_type,
            'is_used': self.is_used,
            'is_expired': self.is_expired,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'time_remaining': self.time_remaining(),
            'is_valid': self.is_valid()
        }
        
        if include_sensitive:
            data['otp_code'] = self.otp_code
            data['additional_data'] = self.additional_data
            
        return data

    @classmethod
    def find_latest_otp(cls, email, purpose, user_type):
        """Find the latest OTP for given email, purpose, and user_type"""
        return cls.query.filter_by(
            email=email,
            purpose=purpose,
            user_type=user_type
        ).order_by(cls.created_at.desc()).first()

    @classmethod
    def find_valid_otp(cls, email, purpose, user_type):
        """Find a valid (unused and not expired) OTP"""
        otp = cls.find_latest_otp(email, purpose, user_type)
        if otp and otp.is_valid():
            return otp
        return None

    @classmethod
    def cleanup_expired_otps(cls):
        """Remove expired OTPs from database (cleanup task)"""
        expired_otps = cls.query.filter(
            db.or_(
                cls.expires_at < datetime.utcnow(),
                cls.is_expired == True,
                cls.is_used == True
            )
        ).filter(
            cls.created_at < datetime.utcnow() - timedelta(days=1)  # Keep for 1 day for audit
        )
        
        count = expired_otps.count()
        expired_otps.delete()
        db.session.commit()
        return count

    @classmethod
    def get_otp_stats(cls, email=None, user_type=None, purpose=None):
        """Get OTP usage statistics"""
        query = cls.query
        
        if email:
            query = query.filter_by(email=email)
        if user_type:
            query = query.filter_by(user_type=user_type)
        if purpose:
            query = query.filter_by(purpose=purpose)
        
        total = query.count()
        used = query.filter_by(is_used=True).count()
        expired = query.filter_by(is_expired=True).count()
        valid = query.filter(
            cls.is_used == False,
            cls.is_expired == False,
            cls.expires_at > datetime.utcnow()
        ).count()
        
        return {
            'total': total,
            'used': used,
            'expired': expired,
            'valid': valid,
            'success_rate': (used / total * 100) if total > 0 else 0
        }

    @classmethod
    def create_otp(cls, email, purpose, user_type, expiry_minutes=10):
        """Create a new OTP and invalidate previous ones"""
        # Mark any existing valid OTPs as expired
        existing_otps = cls.query.filter_by(
            email=email,
            purpose=purpose,
            user_type=user_type,
            is_used=False,
            is_expired=False
        ).all()
        
        for otp in existing_otps:
            otp.mark_expired()
        
        # Create new OTP
        new_otp = cls(
            email=email,
            purpose=purpose,
            user_type=user_type,
            expiry_minutes=expiry_minutes
        )
        
        db.session.add(new_otp)
        db.session.commit()
        
        return new_otp

    def __repr__(self):
        return f'<OTP {self.email}: {self.purpose} ({self.user_type})>'