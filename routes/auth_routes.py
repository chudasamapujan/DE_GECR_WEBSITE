"""
Authentication Routes for GEC Rajkot Website
Handles login, registration, OTP verification, and password reset
Author: GEC Rajkot Development Team
"""

from flask import Blueprint, request, jsonify, current_app, session
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt
from datetime import timedelta, datetime
import re

# Import models and db
from models import Student, Faculty
from database import db
from utils.send_email import send_email

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
        user = Student.find_by_email(email) if user_type == 'student' else Faculty.find_by_email(email)

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


@auth_bp.route('/faculty/login', methods=['POST'])
def faculty_login():
    """Convenience endpoint for faculty login that sets user_type to 'faculty' and delegates to login logic."""
    try:
        data = request.get_json() or {}
        # Ensure user_type is faculty and reuse validation/login logic
        data['user_type'] = 'faculty'
        # Inject back into request context by calling the shared login() logic
        # Since login() reads request.get_json(), we call it directly after temporarily
        # setting request._cached_json. Simpler approach: call the login function after
        # replacing request.get_json via monkeypatch is fragile; instead re-run the core
        # logic here to avoid duplication issues.

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400

        # Find faculty user
        user = Faculty.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not getattr(user, 'is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 403
        if not user.check_password(password):
            return jsonify({'error': 'Invalid password'}), 401

        user_id_val = getattr(user, 'faculty_id', getattr(user, 'student_id', None))
        additional_claims = {
            'user_type': 'faculty',
            'user_id': user_id_val,
            'full_name': getattr(user, 'name', None)
        }

        access_token = create_access_token(
            identity=user.email,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=24)
        )

        # Also set session for session-based auth fallbacks used in templates/tests
        try:
            session['user_email'] = user.email
            session['user_id'] = user.faculty_id
            session['user_type'] = 'faculty'
        except Exception:
            # If session can't be set (e.g., testing config), ignore
            pass

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict(),
            'user_type': 'faculty'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Faculty login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/student/login', methods=['POST'])
def student_login():
    """Convenience endpoint for student login that sets user_type to 'student' and delegates to login logic."""
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400

        # Find student user
        user = Student.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not getattr(user, 'is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 403
        if not user.check_password(password):
            return jsonify({'error': 'Invalid password'}), 401

        user_id_val = getattr(user, 'student_id', getattr(user, 'faculty_id', None))
        additional_claims = {
            'user_type': 'student',
            'user_id': user_id_val,
            'full_name': getattr(user, 'name', None)
        }

        access_token = create_access_token(
            identity=user.email,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=24)
        )

        # Also set session for session-based auth fallbacks used in templates/tests
        try:
            session['user_email'] = user.email
            session['user_id'] = user.student_id
            session['user_type'] = 'student'
        except Exception:
            pass

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict(),
            'user_type': 'student'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Student login error: {str(e)}")
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
        
        # Check if user already exists
        existing_user = Student.find_by_email(email) if user_type == 'student' else Faculty.find_by_email(email)

        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409

        # Create OTP (imported lazily to avoid circular import if OTP model missing)
        from models import OTP
        otp = OTP.create_otp(email, 'registration', user_type, expiry_minutes=10)

        # Send OTP via SendGrid/Flask-Mail/logger via helper
        try:
            subject = 'GEC Rajkot - OTP Verification'
            html = f"<p>Your verification code is: <strong>{otp.otp_code}</strong></p><p>It expires in {otp.time_remaining()} seconds.</p>"
            send_email(email, subject, html_content=html)
        except Exception as e:
            current_app.logger.error(f"Failed to send OTP email via helper: {e}")

        return jsonify({
            'message': 'OTP sent to email for verification',
            'email': email,
            'otp_expires_in': otp.time_remaining()
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
        
        # Find valid OTP
        from models import OTP
        otp = OTP.find_valid_otp(email, purpose, user_type)
        if not otp:
            return jsonify({'error': 'No valid OTP found'}), 404

        is_valid, message = otp.verify_otp(otp_code)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Handle registration
        if purpose == 'registration':
            user_data = data.get('user_data', {})
            if not user_data:
                return jsonify({'error': 'User data required for registration'}), 400

            # Create user record
            if user_type == 'student':
                # Ensure required fields for Student model
                required = ['first_name', 'last_name', 'email', 'password', 'phone', 'date_of_birth', 'address', 'enrollment_number', 'department', 'admission_year', 'current_semester', 'roll_number']
                missing = [f for f in required if f not in user_data]
                if missing:
                    return jsonify({'error': f'Missing fields for student registration: {missing}'}), 400

                # Avoid passing raw password into SQLAlchemy constructor and filter allowed fields
                allowed = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'address', 'blood_group', 'guardian_name', 'guardian_phone', 'emergency_contact', 'enrollment_number', 'department', 'admission_year', 'current_semester', 'roll_number']
                user_kwargs = {k: v for k, v in user_data.items() if k in allowed}
                # Convert date_of_birth from string to date if present
                dob = user_kwargs.get('date_of_birth')
                if isinstance(dob, str):
                    try:
                        user_kwargs['date_of_birth'] = datetime.strptime(dob, '%Y-%m-%d').date()
                    except Exception:
                        pass
                raw_password = user_data.get('password')
                new_user = Student(**user_kwargs)
                new_user.set_password(raw_password)
            else:
                required = ['first_name', 'last_name', 'email', 'password', 'phone', 'employee_id', 'designation', 'department', 'joining_date']
                missing = [f for f in required if f not in user_data]
                if missing:
                    return jsonify({'error': f'Missing fields for faculty registration: {missing}'}), 400

                allowed = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'address', 'employee_id', 'designation', 'department', 'qualification', 'specialization', 'experience_years', 'joining_date', 'office_room', 'office_hours', 'research_interests', 'publications', 'research_projects', 'office_phone', 'personal_website', 'linkedin_profile']
                user_kwargs = {k: v for k, v in user_data.items() if k in allowed}
                # Convert joining_date from string to date if present
                jdate = user_kwargs.get('joining_date')
                if isinstance(jdate, str):
                    try:
                        user_kwargs['joining_date'] = datetime.strptime(jdate, '%Y-%m-%d').date()
                    except Exception:
                        pass
                raw_password = user_data.get('password')
                new_user = Faculty(**user_kwargs)
                new_user.set_password(raw_password)

            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                'message': 'Registration completed successfully',
                'user': new_user.to_dict()
            }), 201

        # Other purposes (forgot_password) would be handled elsewhere
        return jsonify({'message': 'OTP verified'}), 200
        
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
            from models import OTP
            otp = OTP.create_otp(email, purpose, user_type, expiry_minutes=10)

        try:
            subject = 'GEC Rajkot - OTP Verification (resend)'
            html = f"<p>Your verification code is: <strong>{otp.otp_code}</strong></p><p>It expires in {otp.time_remaining()} seconds.</p>"
            send_email(email, subject, html_content=html)
        except Exception as e:
            current_app.logger.error(f"Failed to resend OTP email via helper: {e}")

        return jsonify({
            'message': 'OTP resent successfully',
            'otp_expires_in': otp.time_remaining()
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
        
        # Generate and send OTP for password reset (do not reveal whether user exists)
            from models import OTP
            otp = OTP.create_otp(email, 'forgot_password', user_type, expiry_minutes=10)

        try:
            subject = 'GEC Rajkot - Password Reset OTP'
            html = f"<p>Your password reset code is: <strong>{otp.otp_code}</strong></p><p>It expires in {otp.time_remaining()} seconds.</p>"
            send_email(email, subject, html_content=html)
        except Exception as e:
            current_app.logger.error(f"Failed to send password reset OTP email via helper: {e}")

        return jsonify({
            'message': 'If the email exists, an OTP has been sent for password reset',
            'otp_expires_in': otp.time_remaining()
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
        
        # Verify the reset token via OTP
            from models import OTP
            otp = OTP.find_valid_otp(email, 'forgot_password', user_type)
        if not otp:
            return jsonify({'error': 'No valid reset token found'}), 404

        # Here we expect reset_token to be the otp_code
        is_valid, message = otp.verify_otp(reset_token)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Find user and update password
        user = Student.find_by_email(email) if user_type == 'student' else Faculty.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.set_password(new_password)
        db.session.commit()

        return jsonify({'message': 'Password reset successfully'}), 200
        
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
        claims = get_jwt()
        user_type = claims.get('user_type')

        user = Student.find_by_email(current_user_email) if user_type == 'student' else Faculty.find_by_email(current_user_email)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': user.to_dict(),
            'user_type': user_type
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