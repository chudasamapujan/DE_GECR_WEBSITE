from marshmallow import Schema, fields, validate, ValidationError
import re

class StudentRegistrationSchema(Schema):
    firstName = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    lastName = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Regexp(r'^[6-9]\d{9}$', error="Invalid phone number"))
    dob = fields.Date(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=10, max=200))
    enrollmentNumber = fields.Str(required=True, validate=validate.Regexp(r'^\d{10,12}$', error="Invalid enrollment number"))
    department = fields.Str(required=True, validate=validate.OneOf([
        'computer', 'electronics', 'mechanical', 'electrical', 
        'civil', 'robotics', 'ai', 'instrumentation'
    ]))
    admissionYear = fields.Int(required=True, validate=validate.Range(min=2020, max=2030))
    currentSemester = fields.Int(required=True, validate=validate.Range(min=1, max=8))
    rollNumber = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    password = fields.Str(required=True, validate=validate.Length(min=8))

# Profile update validators
class StudentProfileUpdateSchema(Schema):
    firstName = fields.Str(validate=validate.Length(min=2, max=50))
    lastName = fields.Str(validate=validate.Length(min=2, max=50))
    phone = fields.Str(validate=validate.Regexp(r'^\d{10}$', error='Phone number must be 10 digits'))
    address = fields.Str(validate=validate.Length(max=200))
    dateOfBirth = fields.Date()
    bloodGroup = fields.Str(validate=validate.OneOf(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']))
    guardianName = fields.Str(validate=validate.Length(max=100))
    guardianPhone = fields.Str(validate=validate.Regexp(r'^\d{10}$', error='Guardian phone must be 10 digits'))
    emergencyContact = fields.Str(validate=validate.Regexp(r'^\d{10}$', error='Emergency contact must be 10 digits'))

class FacultyProfileUpdateSchema(Schema):
    firstName = fields.Str(validate=validate.Length(min=2, max=50))
    lastName = fields.Str(validate=validate.Length(min=2, max=50))
    phone = fields.Str(validate=validate.Regexp(r'^\d{10}$', error='Phone number must be 10 digits'))
    address = fields.Str(validate=validate.Length(max=200))
    dateOfBirth = fields.Date()
    qualification = fields.Str(validate=validate.Length(max=100))
    experience = fields.Int(validate=validate.Range(min=0, max=50))
    specialization = fields.Str(validate=validate.Length(max=100))
    researchInterests = fields.List(fields.Str())
    publications = fields.List(fields.Dict())
    achievements = fields.List(fields.Str())

class FacultyRegistrationSchema(Schema):
    firstName = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    lastName = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Regexp(r'^[6-9]\d{9}$', error="Invalid phone number"))
    dob = fields.Date(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=10, max=200))
    facultyId = fields.Str(required=True, validate=validate.Regexp(r'^[A-Z]{2,3}\d{3,5}$', error="Invalid faculty ID"))
    department = fields.Str(required=True, validate=validate.OneOf([
        'computer', 'electronics', 'mechanical', 'electrical', 
        'civil', 'robotics', 'ai', 'instrumentation'
    ]))
    designation = fields.Str(required=True, validate=validate.OneOf([
        'professor', 'associate-professor', 'assistant-professor', 
        'lecturer', 'visiting-faculty'
    ]))
    qualification = fields.Str(required=True, validate=validate.OneOf([
        'phd', 'mtech', 'me', 'msc', 'btech', 'be'
    ]))
    experience = fields.Int(required=True, validate=validate.Range(min=0, max=50))
    specialization = fields.Str(required=True, validate=validate.Length(min=5, max=100))
    password = fields.Str(required=True, validate=validate.Length(min=8))

class LoginSchema(Schema):
    email = fields.Email()
    enrollmentNumber = fields.Str(validate=validate.Regexp(r'^\d{10,12}$'))
    facultyId = fields.Str(validate=validate.Regexp(r'^[A-Z]{2,3}\d{3,5}$'))
    password = fields.Str(required=True, validate=validate.Length(min=1))
    
    def validate_identifier(self, data, **kwargs):
        if not any([data.get('email'), data.get('enrollmentNumber'), data.get('facultyId')]):
            raise ValidationError("One of email, enrollmentNumber, or facultyId is required")

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)
    enrollmentNumber = fields.Str(validate=validate.Regexp(r'^\d{10,12}$'))
    facultyId = fields.Str(validate=validate.Regexp(r'^[A-Z]{2,3}\d{3,5}$'))
    department = fields.Str(validate=validate.OneOf([
        'computer', 'electronics', 'mechanical', 'electrical', 
        'civil', 'robotics', 'ai', 'instrumentation'
    ]))
    userType = fields.Str(required=True, validate=validate.OneOf(['student', 'faculty']))

class VerifyOTPSchema(Schema):
    email = fields.Email(required=True)
    otp = fields.Str(required=True, validate=validate.Length(equal=6))
    userType = fields.Str(required=True, validate=validate.OneOf(['student', 'faculty']))

class ResetPasswordSchema(Schema):
    email = fields.Email(required=True)
    otp = fields.Str(required=True, validate=validate.Length(equal=6))
    newPassword = fields.Str(required=True, validate=validate.Length(min=8))
    userType = fields.Str(required=True, validate=validate.OneOf(['student', 'faculty']))

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"