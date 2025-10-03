from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import random
import string
from validators import StudentRegistrationSchema, FacultyRegistrationSchema, LoginSchema, ForgotPasswordSchema, ResetPasswordSchema
from models import Student, Faculty, OTP
from utils import send_email, format_response

auth_bp = Blueprint('auth', __name__)

# Initialize schemas
student_registration_schema = StudentRegistrationSchema()
faculty_registration_schema = FacultyRegistrationSchema()
login_schema = LoginSchema()
forgot_password_schema = ForgotPasswordSchema()
reset_password_schema = ResetPasswordSchema()

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    """Register a new student"""
    try:
        # Validate request data
        data = student_registration_schema.load(request.json)
        
        # Check if student already exists
        if Student.find_by_email(data['email']):
            return format_response(False, 'Student with this email already exists', 400)
        
        if Student.find_by_enrollment(data['enrollmentNumber']):
            return format_response(False, 'Student with this enrollment number already exists', 400)
        
        # Create student
        student_id = Student.create(data)
        
        # Create access token
        access_token = create_access_token(
            identity=str(student_id),
            additional_claims={'user_type': 'student'},
            expires_delta=timedelta(days=1)
        )
        
        return format_response(
            True, 
            'Student registered successfully',
            200,
            {
                'access_token': access_token,
                'user_type': 'student',
                'user_id': str(student_id)
            }
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@auth_bp.route('/register/faculty', methods=['POST'])
def register_faculty():
    """Register a new faculty member"""
    try:
        # Validate request data
        data = faculty_registration_schema.load(request.json)
        
        # Check if faculty already exists
        if Faculty.find_by_email(data['email']):
            return format_response(False, 'Faculty with this email already exists', 400)
        
        if Faculty.find_by_faculty_id(data['facultyId']):
            return format_response(False, 'Faculty with this ID already exists', 400)
        
        # Create faculty
        faculty_id = Faculty.create(data)
        
        # Send approval notification to admin
        try:
            send_email(
                to=current_app.config['ADMIN_EMAIL'],
                subject='New Faculty Registration - Approval Required',
                template='faculty_approval_required.html',
                **data
            )
        except Exception as email_error:
            current_app.logger.error(f"Failed to send approval email: {email_error}")
        
        return format_response(
            True, 
            'Faculty registration submitted. Waiting for admin approval.',
            200,
            {
                'user_id': str(faculty_id),
                'message': 'Your registration has been submitted for approval. You will be notified once approved.'
            }
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login for both students and faculty"""
    try:
        # Validate request data
        data = login_schema.load(request.json)
        email = data['email']
        password = data['password']
        user_type = data['userType']
        
        user = None
        user_id = None
        
        if user_type == 'student':
            user = Student.find_by_email(email)
            if user and Student.verify_password(password, user['password']):
                user_id = str(user['_id'])
            else:
                return format_response(False, 'Invalid email or password', 401)
                
        elif user_type == 'faculty':
            user = Faculty.find_by_email(email)
            if user and Faculty.verify_password(password, user['password']):
                if not user.get('isApproved', False):
                    return format_response(False, 'Your account is pending approval', 403)
                user_id = str(user['_id'])
            else:
                return format_response(False, 'Invalid email or password', 401)
        else:
            return format_response(False, 'Invalid user type', 400)
        
        if not user.get('isActive', True):
            return format_response(False, 'Your account has been deactivated', 403)
        
        # Create access token
        access_token = create_access_token(
            identity=user_id,
            additional_claims={'user_type': user_type},
            expires_delta=timedelta(days=1)
        )
        
        return format_response(
            True,
            'Login successful',
            200,
            {
                'access_token': access_token,
                'user_type': user_type,
                'user_id': user_id,
                'user': {
                    'name': user.get('firstName', '') + ' ' + user.get('lastName', ''),
                    'email': user['email']
                }
            }
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send OTP for password reset"""
    try:
        # Validate request data
        data = forgot_password_schema.load(request.json)
        email = data['email']
        user_type = data['userType']
        
        # Check if user exists
        user = None
        if user_type == 'student':
            user = Student.find_by_email(email)
        elif user_type == 'faculty':
            user = Faculty.find_by_email(email)
        else:
            return format_response(False, 'Invalid user type', 400)
        
        if not user:
            return format_response(False, 'User not found', 404)
        
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store OTP
        OTP.create(email, otp, user_type, 'password_reset', 10)
        
        # Send OTP email
        try:
            send_email(
                to=email,
                subject='Password Reset OTP - GEC Rajkot',
                template='password_reset_otp.html',
                otp=otp,
                name=user.get('firstName', '') + ' ' + user.get('lastName', ''),
                user_type=user_type.title()
            )
        except Exception as email_error:
            current_app.logger.error(f"Failed to send OTP email: {email_error}")
            return format_response(False, 'Failed to send OTP. Please try again later.', 500)
        
        return format_response(
            True,
            'OTP sent to your email address',
            200,
            {'message': 'Please check your email for the OTP'}
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using OTP"""
    try:
        # Validate request data
        data = reset_password_schema.load(request.json)
        email = data['email']
        otp = data['otp']
        new_password = data['newPassword']
        user_type = data['userType']
        
        # Verify OTP
        if not OTP.verify(email, otp, user_type, 'password_reset'):
            return format_response(False, 'Invalid or expired OTP', 400)
        
        # Update password
        success = False
        if user_type == 'student':
            result = Student.update_password(email, new_password)
            success = result.modified_count > 0
        elif user_type == 'faculty':
            result = Faculty.update_password(email, new_password)
            success = result.modified_count > 0
        else:
            return format_response(False, 'Invalid user type', 400)
        
        if not success:
            return format_response(False, 'Failed to update password', 500)
        
        return format_response(
            True,
            'Password reset successfully',
            200,
            {'message': 'Your password has been reset successfully'}
        )
        
    except Exception as e:
        return format_response(False, str(e), 400)

@auth_bp.route('/verify-token', methods=['POST'])
@jwt_required()
def verify_token():
    """Verify JWT token and return user info"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt_identity()
        
        # Get additional claims
        from flask_jwt_extended import get_jwt
        jwt_data = get_jwt()
        user_type = jwt_data.get('user_type')
        
        if not user_type:
            return format_response(False, 'Invalid token', 401)
        
        # Get user data
        user = None
        if user_type == 'student':
            user = Student.find_by_id(current_user_id)
        elif user_type == 'faculty':
            user = Faculty.find_by_id(current_user_id)
        
        if not user:
            return format_response(False, 'User not found', 404)
        
        # Remove sensitive data
        user.pop('password', None)
        user['_id'] = str(user['_id'])
        
        return format_response(
            True,
            'Token verified',
            200,
            {
                'user': user,
                'user_type': user_type
            }
        )
        
    except Exception as e:
        return format_response(False, str(e), 401)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    return format_response(
        True,
        'Logged out successfully',
        200,
        {'message': 'Please remove the token from client storage'}
    )