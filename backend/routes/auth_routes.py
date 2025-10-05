"""
Authentication Routes for GEC Rajkot Website
Handles login, registration, OTP verification, and password reset
Author: GEC Rajkot Development Team
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import check_password_hash
from datetime import timedelta
import re

# Import models (will be available once database is set up)
# from models import Student, Faculty, OTP
# from database import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Password validation regex (min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char)
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

def validate_email(email):
    """Validate email format"""
    return EMAIL_REGEX.match(email) is not None

def validate_password(password):
    """Validate password strength"""
    return PASSWORD_REGEX.match(password) is not None

def validate_phone(phone):
    """Validate phone number (Indian format)"""
    phone_regex = re.compile(r'^[6-9]\d{9}$')
    return phone_regex.match(phone.replace('+91', '').replace('-', '').replace(' ', '')) is not None

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    Expected JSON: {
        "email": "user@example.com",
        "password": "password123",
        "user_type": "student" or "faculty"
    }
    """
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        user_type = data.get('user_type', '').strip().lower()
        
        # Validate required fields
        if not all([email, password, user_type]):
            return jsonify({'error': 'Email, password, and user type are required'}), 400
        
        # Validate user type
        if user_type not in ['student', 'faculty']:
            return jsonify({'error': 'Invalid user type. Must be student or faculty'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Find user based on type
        user = None
        if user_type == 'student':
            # user = Student.find_by_email(email)
            pass  # Placeholder
        else:
            # user = Faculty.find_by_email(email)
            pass  # Placeholder
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Login endpoint ready',
            'email': email,
            'user_type': user_type,
            'note': 'Database models not yet connected'
        }), 200
        
        # Uncomment when models are available:
        """
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        if not user.check_password(password):
            return jsonify({'error': 'Invalid password'}), 401
        
        # Create access token
        additional_claims = {
            'user_type': user_type,
            'user_id': user.id,
            'full_name': user.full_name
        }
        
        access_token = create_access_token(
            identity=user.email,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict(),
            'user_type': user_type
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint
    Expected JSON varies by user_type (student/faculty)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_type = data.get('user_type', '').strip().lower()
        
        if user_type not in ['student', 'faculty']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        # Common validation
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        
        # Validate required fields
        if not all([email, password, first_name, last_name, phone]):
            return jsonify({'error': 'All basic fields are required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if not validate_password(password):
            return jsonify({
                'error': 'Password must be at least 8 characters with uppercase, lowercase, digit, and special character'
            }), 400
        
        # Validate phone number
        if not validate_phone(phone):
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Registration endpoint ready',
            'user_type': user_type,
            'email': email,
            'note': 'Database models not yet connected. OTP verification would follow.'
        }), 200
        
        # Uncomment when models are available:
        """
        # Check if user already exists
        existing_user = None
        if user_type == 'student':
            existing_user = Student.find_by_email(email)
        else:
            existing_user = Faculty.find_by_email(email)
        
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Generate and send OTP
        otp = OTP.create_otp(email, 'registration', user_type)
        
        # Here you would send the OTP via email
        # send_otp_email(email, otp.otp_code, 'registration')
        
        return jsonify({
            'message': 'OTP sent to email for verification',
            'email': email,
            'otp_expires_in': otp.time_remaining()
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    OTP verification endpoint
    Expected JSON: {
        "email": "user@example.com",
        "otp": "123456",
        "purpose": "registration" or "forgot_password",
        "user_type": "student" or "faculty",
        "user_data": {...} // Required for registration
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        otp_code = data.get('otp', '').strip()
        purpose = data.get('purpose', '').strip()
        user_type = data.get('user_type', '').strip().lower()
        
        # Validate required fields
        if not all([email, otp_code, purpose, user_type]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Validate values
        if user_type not in ['student', 'faculty']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        if purpose not in ['registration', 'forgot_password']:
            return jsonify({'error': 'Invalid purpose'}), 400
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'OTP verification endpoint ready',
            'email': email,
            'purpose': purpose,
            'user_type': user_type,
            'note': 'Database models not yet connected'
        }), 200
        
        # Uncomment when models are available:
        """
        # Find and verify OTP
        otp = OTP.find_valid_otp(email, purpose, user_type)
        
        if not otp:
            return jsonify({'error': 'No valid OTP found'}), 404
        
        is_valid, message = otp.verify_otp(otp_code)
        
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Handle different purposes
        if purpose == 'registration':
            user_data = data.get('user_data', {})
            if not user_data:
                return jsonify({'error': 'User data required for registration'}), 400
            
            # Create new user
            if user_type == 'student':
                new_user = Student(**user_data)
            else:
                new_user = Faculty(**user_data)
            
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'message': 'Registration completed successfully',
                'user': new_user.to_dict()
            }), 201
        
        elif purpose == 'forgot_password':
            return jsonify({
                'message': 'OTP verified. You can now reset your password.',
                'reset_token': otp.id  # You might want to create a separate reset token
            }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"OTP verification error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """
    Resend OTP endpoint
    Expected JSON: {
        "email": "user@example.com",
        "purpose": "registration" or "forgot_password",
        "user_type": "student" or "faculty"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        purpose = data.get('purpose', '').strip()
        user_type = data.get('user_type', '').strip().lower()
        
        # Validate required fields
        if not all([email, purpose, user_type]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Validate values
        if user_type not in ['student', 'faculty']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        if purpose not in ['registration', 'forgot_password']:
            return jsonify({'error': 'Invalid purpose'}), 400
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'OTP resend endpoint ready',
            'email': email,
            'purpose': purpose,
            'user_type': user_type,
            'note': 'Database models not yet connected'
        }), 200
        
        # Uncomment when models are available:
        """
        # Generate new OTP
        otp = OTP.create_otp(email, purpose, user_type)
        
        # Send OTP via email
        # send_otp_email(email, otp.otp_code, purpose)
        
        return jsonify({
            'message': 'OTP resent successfully',
            'otp_expires_in': otp.time_remaining()
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"OTP resend error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Forgot password endpoint
    Expected JSON: {
        "email": "user@example.com",
        "user_type": "student" or "faculty"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        user_type = data.get('user_type', '').strip().lower()
        
        # Validate required fields
        if not all([email, user_type]):
            return jsonify({'error': 'Email and user type are required'}), 400
        
        # Validate user type
        if user_type not in ['student', 'faculty']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Forgot password endpoint ready',
            'email': email,
            'user_type': user_type,
            'note': 'Database models not yet connected'
        }), 200
        
        # Uncomment when models are available:
        """
        # Check if user exists
        user = None
        if user_type == 'student':
            user = Student.find_by_email(email)
        else:
            user = Faculty.find_by_email(email)
        
        if not user:
            # Don't reveal whether user exists or not for security
            return jsonify({
                'message': 'If the email exists, an OTP will be sent for password reset'
            }), 200
        
        # Generate and send OTP
        otp = OTP.create_otp(email, 'forgot_password', user_type)
        
        # Send OTP via email
        # send_otp_email(email, otp.otp_code, 'forgot_password')
        
        return jsonify({
            'message': 'OTP sent to email for password reset',
            'otp_expires_in': otp.time_remaining()
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password endpoint
    Expected JSON: {
        "email": "user@example.com",
        "new_password": "newpassword123",
        "reset_token": "token_from_otp_verification",
        "user_type": "student" or "faculty"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        new_password = data.get('new_password', '')
        reset_token = data.get('reset_token', '')
        user_type = data.get('user_type', '').strip().lower()
        
        # Validate required fields
        if not all([email, new_password, reset_token, user_type]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Validate password strength
        if not validate_password(new_password):
            return jsonify({
                'error': 'Password must be at least 8 characters with uppercase, lowercase, digit, and special character'
            }), 400
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Password reset endpoint ready',
            'email': email,
            'user_type': user_type,
            'note': 'Database models not yet connected'
        }), 200
        
        # Uncomment when models are available:
        """
        # Verify reset token (could be OTP ID or separate token)
        # This is a simplified version - you might want more secure token handling
        
        # Find user
        user = None
        if user_type == 'student':
            user = Student.find_by_email(email)
        else:
            user = Faculty.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'message': 'Password reset successfully'
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user profile (requires authentication)
    """
    try:
        current_user_email = get_jwt_identity()
        
        # Placeholder response until models are connected
        return jsonify({
            'message': 'Profile endpoint ready',
            'email': current_user_email,
            'note': 'Database models not yet connected'
        }), 200
        
        # Uncomment when models are available:
        """
        # Get user type from JWT claims
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        user_type = claims.get('user_type')
        
        # Find user
        user = None
        if user_type == 'student':
            user = Student.find_by_email(current_user_email)
        else:
            user = Faculty.find_by_email(current_user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'user_type': user_type
        }), 200
        """
        
    except Exception as e:
        current_app.logger.error(f"Profile error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    User logout endpoint
    Note: With JWT, logout is mainly client-side token removal
    You might want to implement token blacklisting for enhanced security
    """
    try:
        return jsonify({
            'message': 'Logout successful. Please remove the token from client storage.'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers for the auth blueprint
@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@auth_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@auth_bp.errorhandler(409)
def conflict(error):
    return jsonify({'error': 'Conflict'}), 409

@auth_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500