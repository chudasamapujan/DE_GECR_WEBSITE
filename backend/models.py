from datetime import datetime, timedelta
from database import Database
import bcrypt
from bson import ObjectId

class Student:
    collection = None
    
    @classmethod
    def get_collection(cls):
        if cls.collection is None:
            cls.collection = Database.get_collection('students')
        return cls.collection
    
    @classmethod
    def create(cls, data):
        """Create a new student"""
        # Hash password
        data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        data['isActive'] = True
        data['createdAt'] = datetime.utcnow()
        data['updatedAt'] = datetime.utcnow()
        
        result = cls.get_collection().insert_one(data)
        return result.inserted_id
    
    @classmethod
    def find_by_email(cls, email):
        """Find student by email"""
        return cls.get_collection().find_one({'email': email})
    
    @classmethod
    def find_by_enrollment(cls, enrollment_number):
        """Find student by enrollment number"""
        return cls.get_collection().find_one({'enrollmentNumber': enrollment_number})
    
    @classmethod
    def find_by_id(cls, student_id):
        """Find student by ID"""
        return cls.get_collection().find_one({'_id': ObjectId(student_id)})
    
    @classmethod
    def update_password(cls, email, new_password):
        """Update student password"""
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return cls.get_collection().update_one(
            {'email': email},
            {'$set': {'password': hashed_password, 'updatedAt': datetime.utcnow()}}
        )
    
    @classmethod
    def verify_password(cls, password, hashed_password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @classmethod
    def update_profile(cls, student_id, data):
        """Update student profile"""
        data['updatedAt'] = datetime.utcnow()
        return cls.get_collection().update_one(
            {'_id': ObjectId(student_id)},
            {'$set': data}
        )

class Faculty:
    collection = None
    
    @classmethod
    def get_collection(cls):
        if cls.collection is None:
            cls.collection = Database.get_collection('faculty')
        return cls.collection
    
    @classmethod
    def create(cls, data):
        """Create a new faculty member"""
        # Hash password
        data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        data['isActive'] = True
        data['isApproved'] = False  # Faculty needs approval
        data['createdAt'] = datetime.utcnow()
        data['updatedAt'] = datetime.utcnow()
        
        result = cls.get_collection().insert_one(data)
        return result.inserted_id
    
    @classmethod
    def find_by_email(cls, email):
        """Find faculty by email"""
        return cls.get_collection().find_one({'email': email})
    
    @classmethod
    def find_by_faculty_id(cls, faculty_id):
        """Find faculty by faculty ID"""
        return cls.get_collection().find_one({'facultyId': faculty_id})
    
    @classmethod
    def find_by_id(cls, faculty_id):
        """Find faculty by ID"""
        return cls.get_collection().find_one({'_id': ObjectId(faculty_id)})
    
    @classmethod
    def update_password(cls, email, new_password):
        """Update faculty password"""
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return cls.get_collection().update_one(
            {'email': email},
            {'$set': {'password': hashed_password, 'updatedAt': datetime.utcnow()}}
        )
    
    @classmethod
    def verify_password(cls, password, hashed_password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @classmethod
    def update_profile(cls, faculty_id, data):
        """Update faculty profile"""
        data['updatedAt'] = datetime.utcnow()
        return cls.get_collection().update_one(
            {'_id': ObjectId(faculty_id)},
            {'$set': data}
        )

class OTP:
    collection = None
    
    @classmethod
    def get_collection(cls):
        if cls.collection is None:
            cls.collection = Database.get_collection('otps')
        return cls.collection
    
    @classmethod
    def create(cls, email, otp, user_type, purpose='password_reset', expiry_minutes=10):
        """Create a new OTP"""
        data = {
            'email': email,
            'otp': otp,
            'userType': user_type,
            'purpose': purpose,
            'expiresAt': datetime.utcnow() + timedelta(minutes=expiry_minutes),
            'isUsed': False,
            'createdAt': datetime.utcnow()
        }
        
        # Invalidate existing OTPs for this email and purpose
        cls.get_collection().update_many(
            {'email': email, 'purpose': purpose, 'isUsed': False},
            {'$set': {'isUsed': True}}
        )
        
        result = cls.get_collection().insert_one(data)
        return result.inserted_id
    
    @classmethod
    def verify(cls, email, otp, user_type, purpose='password_reset'):
        """Verify OTP"""
        otp_doc = cls.get_collection().find_one({
            'email': email,
            'otp': otp,
            'userType': user_type,
            'purpose': purpose,
            'isUsed': False,
            'expiresAt': {'$gt': datetime.utcnow()}
        })
        
        if otp_doc:
            # Mark OTP as used
            cls.get_collection().update_one(
                {'_id': otp_doc['_id']},
                {'$set': {'isUsed': True}}
            )
            return True
        return False
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired OTPs"""
        return cls.get_collection().delete_many({
            'expiresAt': {'$lt': datetime.utcnow()}
        })