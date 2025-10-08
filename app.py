"""
Main Flask Application for GEC Rajkot Website
Backend API server with authentication and user management
Author: GEC Rajkot Development Team
"""

from flask import Flask, jsonify, request, send_from_directory, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from datetime import datetime, timedelta
import os
import logging
from logging.handlers import RotatingFileHandler
import glob
from werkzeug.utils import secure_filename

# Import configurations and routes
from database import init_database, create_tables
from routes import auth_bp, student_bp, faculty_bp

def create_app(config_name='development'):
    """
    Application factory pattern
    Creates and configures Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.update(get_config(config_name))
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup logging
    setup_logging(app)
    
    # Create database tables
    with app.app_context():
        create_tables(app)
    
    return app

def get_config(config_name):
    """
    Get configuration based on environment
    """
    config = {
        # Basic Flask configuration
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'gec-rajkot-dev-secret-key-2024'),
        'DEBUG': config_name == 'development',
        
        # Database configuration
        'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'sqlite:///gec_rajkot.db'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ECHO': config_name == 'development',
        
        # JWT configuration
        'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', 'gec-rajkot-jwt-secret-2024'),
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=24),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
        'JWT_ALGORITHM': 'HS256',
        
        # Mail configuration (for OTP emails)
        'MAIL_SERVER': os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
        'MAIL_PORT': int(os.environ.get('MAIL_PORT', 587)),
        'MAIL_USE_TLS': True,
        'MAIL_USE_SSL': False,
        'MAIL_USERNAME': os.environ.get('MAIL_USERNAME', ''),
        'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD', ''),
        'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@gecrajkot.ac.in'),
        
        # CORS configuration
        'CORS_ORIGINS': ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:8080'],
        
        # File upload configuration
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
        'UPLOAD_FOLDER': 'uploads',
        
        # College information
        'COLLEGE_NAME': 'Government Engineering College, Rajkot',
        'COLLEGE_ADDRESS': 'Rajkot-Bhavnagar Highway, Rajkot - 360005, Gujarat, India',
        'COLLEGE_PHONE': '+91-281-2470501',
        'COLLEGE_EMAIL': 'info@gecrajkot.ac.in',
        'COLLEGE_WEBSITE': 'www.gecrajkot.ac.in',
        
        # API configuration
        'API_VERSION': 'v1',
        'API_TITLE': 'GEC Rajkot API',
        'API_DESCRIPTION': 'Backend API for GEC Rajkot Student and Faculty Portal',
    }
    
    if config_name == 'production':
        config.update({
            'DEBUG': False,
            'TESTING': False,
            'SQLALCHEMY_ECHO': False,
        })
    elif config_name == 'testing':
        config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
        })
    
    return config

def init_extensions(app):
    """
    Initialize Flask extensions
    """
    # Initialize database
    init_database(app)
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authentication required'}), 401
    
    # Initialize Mail
    mail = Mail(app)
    
    # Store mail instance in app for access in routes
    app.mail = mail

def register_blueprints(app):
    """
    Register application blueprints
    """
    # Authentication routes
    app.register_blueprint(auth_bp)
    
    # Student routes
    app.register_blueprint(student_bp)
    
    # Faculty routes
    app.register_blueprint(faculty_bp)

def register_error_handlers(app):
    """
    Register error handlers
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({'error': 'File too large'}), 413
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({'error': 'Unprocessable entity'}), 422
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({'error': 'Too many requests'}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

def setup_logging(app):
    """
    Setup application logging
    """
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup file handler with rotation
        file_handler = RotatingFileHandler(
            'logs/gec_rajkot.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('GEC Rajkot application startup')

    # Register main application routes
    register_main_routes(app)
    
    return app

def register_main_routes(app):
    """
    Register main application routes
    """
    @app.route('/')
    def index():
        """
        API root endpoint
        """
        # If the request accepts HTML, render the frontend index page so
        # buttons and links open the login/register templates directly.
        if request.accept_mimetypes.accept_html and not request.is_json:
            return render_template('index.html')

        return jsonify({
            'message': 'GEC Rajkot API Server',
            'version': app.config['API_VERSION'],
            'title': app.config['API_TITLE'],
            'description': app.config['API_DESCRIPTION'],
            'college': app.config['COLLEGE_NAME'],
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'authentication': '/api/auth',
                'student': '/api/student',
                'faculty': '/api/faculty',
                'health': '/api/health',
                'docs': '/api/docs'
            }
        })

    @app.route('/api/health')
    def health_check():
        """
        Health check endpoint
        """
        try:
            # Check database connection
            from database import get_db_stats
            db_stats = get_db_stats()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': app.config['API_VERSION'],
                'database': 'connected' if db_stats else 'disconnected',
                'database_stats': db_stats,
                'uptime': 'N/A'  # Could implement actual uptime tracking
            })
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500

    @app.route('/api/docs')
    def api_docs():
        """
        API documentation endpoint
        """
        return jsonify({
            'title': app.config['API_TITLE'],
            'description': app.config['API_DESCRIPTION'],
            'version': app.config['API_VERSION'],
            'base_url': request.base_url.replace('/api/docs', ''),
            'endpoints': {
                'auth': {
                    'login': 'POST /api/auth/login',
                    'register': 'POST /api/auth/register',
                    'verify_otp': 'POST /api/auth/verify-otp',
                    'forgot_password': 'POST /api/auth/forgot-password',
                    'reset_password': 'POST /api/auth/reset-password',
                    'profile': 'GET /api/auth/profile',
                    'logout': 'POST /api/auth/logout'
                },
                'student': {
                    'dashboard': 'GET /api/student/dashboard',
                    'profile': 'GET|PUT /api/student/profile',
                    'attendance': 'GET /api/student/attendance',
                    'assignments': 'GET /api/student/assignments',
                    'grades': 'GET /api/student/grades',
                    'schedule': 'GET /api/student/schedule',
                    'events': 'GET /api/student/events',
                    'resources': 'GET /api/student/resources'
                },
                'faculty': {
                    'dashboard': 'GET /api/faculty/dashboard',
                    'profile': 'GET|PUT /api/faculty/profile',
                    'students': 'GET /api/faculty/students',
                    'attendance': 'GET|POST /api/faculty/attendance',
                    'assignments': 'GET|POST /api/faculty/assignments',
                    'grades': 'POST /api/faculty/grades',
                    'schedule': 'GET /api/faculty/schedule',
                    'subjects': 'GET /api/faculty/subjects'
                }
            },
            'authentication': 'Bearer token required for protected endpoints',
            'college_info': {
                'name': app.config['COLLEGE_NAME'],
                'address': app.config['COLLEGE_ADDRESS'],
                'phone': app.config['COLLEGE_PHONE'],
                'email': app.config['COLLEGE_EMAIL'],
                'website': app.config['COLLEGE_WEBSITE']
            }
        })

    # Static file serving for frontend
    @app.route('/frontend/<path:filename>')
    def serve_frontend(filename):
        """
        Serve frontend static files
        """
        return send_from_directory('../frontend', filename)


    # Simple routes to serve login/register forms from templates
    @app.route('/auth/login/<user_type>')
    def serve_login(user_type):
        user_type = (user_type or '').lower()
        if user_type not in ['student', 'faculty']:
            return "Not found", 404

        tpl = f'auth/login/{user_type}.html'
        return render_template(tpl)

    @app.route('/auth/register/<user_type>')
    def serve_register(user_type):
        user_type = (user_type or '').lower()
        if user_type == 'faculty':
            tpl = 'auth/login/faculty-register.html'
        else:
            tpl = 'auth/login/student-register.html'
        return render_template(tpl)

    @app.route('/auth/forgot/<user_type>')
    def serve_forgot(user_type):
        """
        Serve forgot-password pages for student/faculty
        """
        user_type = (user_type or '').lower()
        if user_type == 'faculty':
            tpl = 'auth/login/faculty-forgot.html'
        elif user_type == 'student':
            tpl = 'auth/login/student-forgot.html'
        else:
            return "Not found", 404
        return render_template(tpl)

    @app.route('/auth/verify')
    def serve_verify():
        return render_template('otp_verification.html')

    @app.route('/student/dashboard')
    def serve_student_dashboard():
        """
        Serve the student dashboard page with real database data
        Requires active session authentication
        """
        from dashboard_data import get_student_dashboard_data
        
        if 'user_id' not in session or session.get('user_type') != 'student':
            flash('Please log in to access the student dashboard', 'error')
            return redirect(url_for('serve_login', user_type='student'))
        
        # Get dashboard data from database
        dashboard_data = get_student_dashboard_data(session['user_id'])
        if not dashboard_data:
            flash('Error loading dashboard data', 'error')
            return redirect(url_for('serve_login', user_type='student'))
        
        return render_template('student/dashboard.html', **dashboard_data)

    @app.route('/faculty/dashboard')
    def serve_faculty_dashboard():
        """
        Serve the faculty dashboard page with real database data
        Requires active session authentication
        """
        from dashboard_data import get_faculty_dashboard_data
        
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            flash('Please log in to access the faculty dashboard', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        # Get dashboard data from database
        dashboard_data = get_faculty_dashboard_data(session['user_id'])
        if not dashboard_data:
            flash('Error loading dashboard data', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        return render_template('faculty/dashboard.html', **dashboard_data)

    # Student pages with database connectivity
    @app.route('/student/profile')
    def serve_student_profile():
        """Serve student profile page with database data"""
        from flask import session, redirect, url_for, flash
        
        if 'user_id' not in session or session.get('user_type') != 'student':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='student'))
        
        from models.gecr_models import Student
        student = Student.query.get(session['user_id'])

        # Try to find an uploaded profile photo for this student in UPLOAD_FOLDER
        upload_dir = os.path.join(app.root_path, app.config.get('UPLOAD_FOLDER', 'uploads'))
        photo_filename = None
        try:
            # Prefer thumbnail if available (student_<id>_thumb.*), fall back to original
            thumb_pattern = os.path.join(upload_dir, f"student_{student.student_id}_thumb.*")
            matches = glob.glob(thumb_pattern)
            if matches:
                photo_filename = os.path.basename(matches[0])
            else:
                pattern = os.path.join(upload_dir, f"student_{student.student_id}.*")
                matches = glob.glob(pattern)
                if matches:
                    photo_filename = os.path.basename(matches[0])
        except Exception:
            photo_filename = None

        return render_template('student/student-profile.html', student=student, photo_filename=photo_filename)

    @app.route('/student/attendance')
    def serve_student_attendance():
        """Serve student attendance page with database data"""
        from flask import session, redirect, url_for, flash
        from dashboard_data import get_student_attendance_data
        
        if 'user_id' not in session or session.get('user_type') != 'student':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='student'))
        
        attendance_data = get_student_attendance_data(session['user_id'])
        if not attendance_data:
            flash('Error loading attendance data', 'error')
            return redirect(url_for('serve_student_dashboard'))
        
        return render_template('student/attendance.html', **attendance_data)

    @app.route('/student/schedule')
    def serve_student_schedule():
        """Serve student schedule page with database data"""
        from flask import session, redirect, url_for, flash
        from models.gecr_models import Student, Subject, Timetable
        from database import db
        
        if 'user_id' not in session or session.get('user_type') != 'student':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='student'))
        
        student = Student.query.get(session['user_id'])
        # Get schedule for student's semester
        schedule = db.session.query(Timetable, Subject).join(
            Subject, Timetable.subject_id == Subject.subject_id
        ).filter(Subject.semester == student.semester).all()
        
        return render_template('student/schedule.html', student=student, schedule=schedule)

    @app.route('/student/events')
    def serve_student_events():
        """Serve student events page"""
        from flask import session, redirect, url_for, flash
        from models.gecr_models import Student
        
        if 'user_id' not in session or session.get('user_type') != 'student':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='student'))
        
        student = Student.query.get(session['user_id'])
        return render_template('student/events.html', student=student)

    # Faculty pages with database connectivity
    @app.route('/faculty/profile')
    def serve_faculty_profile():
        """Serve faculty profile page with database data"""
        from flask import session, redirect, url_for, flash
        from models.gecr_models import Faculty
        
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        faculty = Faculty.query.get(session['user_id'])
        return render_template('faculty/profile.html', faculty=faculty)

    @app.route('/faculty/subjects')
    def serve_faculty_subjects():
        """Serve faculty subjects page with database data"""
        from flask import session, redirect, url_for, flash
        from models.gecr_models import Faculty, Subject
        
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        faculty = Faculty.query.get(session['user_id'])
        subjects = Subject.query.filter_by(faculty_id=session['user_id']).all()
        return render_template('faculty/subjects.html', faculty=faculty, subjects=subjects)

    @app.route('/faculty/students')
    def serve_faculty_students():
        """Serve faculty students page with database data"""
        from flask import session, redirect, url_for, flash
        from dashboard_data import get_faculty_students_data
        
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        students_data = get_faculty_students_data(session['user_id'])
        if not students_data:
            flash('Error loading students data', 'error')
            return redirect(url_for('serve_faculty_dashboard'))
        
        return render_template('faculty/students.html', **students_data)

    @app.route('/faculty/assignments')
    def serve_faculty_assignments():
        """Serve faculty assignments page with database data"""
        from flask import session, redirect, url_for, flash
        from dashboard_data import get_faculty_assignments_data
        
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        assignments_data = get_faculty_assignments_data(session['user_id'])
        if not assignments_data:
            flash('Error loading assignments data', 'error')
            return redirect(url_for('serve_faculty_dashboard'))
        
        return render_template('faculty/assignments.html', **assignments_data)

    @app.route('/faculty/attendance')
    def serve_faculty_attendance():
        """Serve faculty attendance page with database data"""
        from flask import session, redirect, url_for, flash
        from models.gecr_models import Faculty, Subject, Student, Attendance
        from database import db
        
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        faculty = Faculty.query.get(session['user_id'])
        subjects = Subject.query.filter_by(faculty_id=session['user_id']).all()
        
        # Get attendance records for faculty's subjects
        attendance_records = []
        for subject in subjects:
            records = db.session.query(Attendance, Student).join(
                Student, Attendance.student_id == Student.student_id
            ).filter(Attendance.subject_id == subject.subject_id).all()
            attendance_records.extend([(record[0], record[1], subject) for record in records])
        
        return render_template('faculty/attendance.html', 
                             faculty=faculty, subjects=subjects, attendance_records=attendance_records)

    @app.route('/faculty/schedule')
    def serve_faculty_schedule():
        """Serve faculty schedule page with database data"""
        from flask import session, redirect, url_for, flash
        from models.gecr_models import Faculty, Timetable, Subject
        from database import db
        
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        faculty = Faculty.query.get(session['user_id'])
        
        # Get faculty's schedule
        schedule = db.session.query(Timetable, Subject).join(
            Subject, Timetable.subject_id == Subject.subject_id
        ).filter(Timetable.faculty_id == session['user_id']).all()
        
        return render_template('faculty/schedule.html', faculty=faculty, schedule=schedule)

    @app.route('/faculty/events')
    def serve_faculty_events():
        """Serve faculty events page"""
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        from models.gecr_models import Faculty
        faculty = Faculty.query.get(session['user_id'])
        
        # For now, render a basic events page - you can add event data later
        return render_template('faculty/events.html', faculty=faculty, events=[])

    @app.route('/faculty/settings')
    def serve_faculty_settings():
        """Serve faculty settings page"""
        if 'user_id' not in session or session.get('user_type') != 'faculty':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='faculty'))
        
        from models.gecr_models import Faculty
        faculty = Faculty.query.get(session['user_id'])
        
        return render_template('faculty/settings.html', faculty=faculty)

    @app.route('/student/settings')
    def serve_student_settings():
        """Serve student settings page"""
        if 'user_id' not in session or session.get('user_type') != 'student':
            flash('Please log in to access this page', 'error')
            return redirect(url_for('serve_login', user_type='student'))
        
        from models.gecr_models import Student
        student = Student.query.get(session['user_id'])
        
        return render_template('student/settings.html', student=student)

    @app.route('/student/upload-photo', methods=['POST'])
    def student_upload_photo():
        """Handle student profile photo upload from settings page"""
        if 'user_id' not in session or session.get('user_type') != 'student':
            flash('Please log in to upload a photo', 'error')
            return redirect(url_for('serve_login', user_type='student'))

        if 'photo' not in request.files:
            flash('No file provided', 'error')
            return redirect(url_for('serve_student_settings'))

        file = request.files['photo']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('serve_student_settings'))

        filename = secure_filename(file.filename)
        _, ext = os.path.splitext(filename)
        dest_name = f"student_{session['user_id']}{ext}"

        upload_dir = os.path.join(app.root_path, app.config.get('UPLOAD_FOLDER', 'uploads'))
        os.makedirs(upload_dir, exist_ok=True)

        dest_path = os.path.join(upload_dir, dest_name)
        try:
            # Save original
            file.save(dest_path)

            # Create thumbnail using Pillow if available
            try:
                from PIL import Image
                thumb_size = (300, 300)
                img = Image.open(dest_path)
                img = img.convert('RGB')
                img.thumbnail(thumb_size)
                base, _ = os.path.splitext(dest_name)
                thumb_name = f"{base}_thumb.jpg"
                thumb_path = os.path.join(upload_dir, thumb_name)
                img.save(thumb_path, format='JPEG', quality=85)
            except Exception as e:
                # Pillow may not be installed or image processing failed; continue gracefully
                app.logger.info(f"Thumbnail creation skipped or failed: {e}")

            flash('Profile photo uploaded successfully', 'success')
        except Exception as e:
            app.logger.error(f"Failed to save uploaded photo: {e}")
            flash('Failed to upload photo', 'error')

        return redirect(url_for('serve_student_settings'))

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files (profile photos) from upload folder"""
        upload_dir = os.path.join(app.root_path, app.config.get('UPLOAD_FOLDER', 'uploads'))
        return send_from_directory(upload_dir, filename)

    @app.route('/auth/login/<user_type>', methods=['POST'])
    def auth_login(user_type):
        """
        Handle server-side login authentication
        """
        from models.gecr_models import Student, Faculty
        from flask import session, flash, redirect, url_for
        
        user_type = user_type.lower()
        if user_type not in ['student', 'faculty']:
            flash('Invalid user type', 'error')
            return redirect(url_for('serve_login', user_type='student'))
        
        if user_type == 'student':
            enrollment = request.form.get('enrollment', '').strip()
            password = request.form.get('password', '')
            
            if not enrollment or not password:
                flash('Enrollment number and password are required', 'error')
                return redirect(url_for('serve_login', user_type='student'))
            
            # Try to find student by roll number first, then by email
            user = Student.find_by_roll_no(enrollment)
            if not user:
                user = Student.find_by_email(enrollment)
            
            if not user or not user.check_password(password):
                flash('Invalid enrollment number or password', 'error')
                return redirect(url_for('serve_login', user_type='student'))
            
            # Store user info in session
            session['user_id'] = user.student_id
            session['user_type'] = 'student'
            session['user_email'] = user.email
            session['user_name'] = user.name
            
            flash(f'Welcome {user.name}!', 'success')
            return redirect(url_for('serve_student_dashboard'))
            
        else:  # faculty
            faculty_email = request.form.get('facultyId', '').strip()
            password = request.form.get('password', '')
            
            if not faculty_email or not password:
                flash('Email and password are required', 'error')
                return redirect(url_for('serve_login', user_type='faculty'))
            
            # Find faculty by email
            user = Faculty.find_by_email(faculty_email)
            
            if not user or not user.check_password(password):
                flash('Invalid email or password', 'error')
                return redirect(url_for('serve_login', user_type='faculty'))
            
            # Store user info in session
            session['user_id'] = user.faculty_id
            session['user_type'] = 'faculty'
            session['user_email'] = user.email
            session['user_name'] = user.name
            
            flash(f'Welcome {user.name}!', 'success')
            return redirect(url_for('serve_faculty_dashboard'))

    @app.route('/auth/logout')
    def auth_logout():
        """
        Handle user logout
        """
        from flask import session, flash, redirect, url_for
        session.clear()
        flash('You have been logged out successfully', 'info')
        return redirect(url_for('index'))

    @app.route('/auth/register/<user_type>', methods=['POST'])
    def auth_register(user_type):
        """
        Handle server-side user registration
        """
        from models.gecr_models import Student, Faculty
        from database import db
        from flask import session, flash, redirect, url_for
        from datetime import datetime
        
        user_type = user_type.lower()
        if user_type not in ['student', 'faculty']:
            flash('Invalid user type', 'error')
            return redirect(url_for('serve_register', user_type='student'))
        
        if user_type == 'student':
            # Get student registration data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirmPassword', '')
            roll_no = request.form.get('rollNo', '').strip()
            department = request.form.get('department', '').strip()
            semester = request.form.get('semester', '')
            phone = request.form.get('phone', '').strip()
            
            # Validation
            if not all([name, email, password, roll_no, department]):
                flash('Name, email, password, roll number, and department are required', 'error')
                return redirect(url_for('serve_register', user_type='student'))
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('serve_register', user_type='student'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return redirect(url_for('serve_register', user_type='student'))
            
            # Check if user already exists
            if Student.find_by_email(email):
                flash('Email already registered', 'error')
                return redirect(url_for('serve_register', user_type='student'))
            
            if Student.find_by_roll_no(roll_no):
                flash('Roll number already registered', 'error')
                return redirect(url_for('serve_register', user_type='student'))
            
            # Create new student
            try:
                new_student = Student(
                    roll_no=roll_no,
                    name=name,
                    email=email,
                    department=department,
                    semester=int(semester) if semester else 1,
                    phone=phone,
                    fees_paid=False
                )
                new_student.set_password(password)
                
                db.session.add(new_student)
                db.session.commit()
                
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('serve_login', user_type='student'))
                
            except Exception as e:
                db.session.rollback()
                flash('Registration failed. Please try again.', 'error')
                return redirect(url_for('serve_register', user_type='student'))
            
        else:  # faculty
            # Get faculty registration data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirmPassword', '')
            department = request.form.get('department', '').strip()
            designation = request.form.get('designation', '').strip()
            phone = request.form.get('phone', '').strip()
            
            # Validation
            if not all([name, email, password, department, designation]):
                flash('Name, email, password, department, and designation are required', 'error')
                return redirect(url_for('serve_register', user_type='faculty'))
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('serve_register', user_type='faculty'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return redirect(url_for('serve_register', user_type='faculty'))
            
            # Check if user already exists
            if Faculty.find_by_email(email):
                flash('Email already registered', 'error')
                return redirect(url_for('serve_register', user_type='faculty'))
            
            # Create new faculty
            try:
                new_faculty = Faculty(
                    name=name,
                    email=email,
                    department=department,
                    designation=designation,
                    phone=phone,
                    salary=0  # Default salary
                )
                new_faculty.set_password(password)
                
                db.session.add(new_faculty)
                db.session.commit()
                
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('serve_login', user_type='faculty'))
                
            except Exception as e:
                db.session.rollback()
                flash('Registration failed. Please try again.', 'error')
                return redirect(url_for('serve_register', user_type='faculty'))

    # Serve logo from static if available, otherwise fallback to templates folder
    @app.route('/logo.png')
    def serve_logo():
        static_path = os.path.join(app.root_path, 'static', 'logo.png')
        if os.path.exists(static_path):
            return send_from_directory(os.path.join(app.root_path, 'static'), 'logo.png')

        # Fallback to templates folder
        tpl_path = os.path.join(app.root_path, 'templates', 'logo.png')
        if os.path.exists(tpl_path):
            return send_from_directory(os.path.join(app.root_path, 'templates'), 'logo.png')

        # If not found, return 204 No Content to reduce 404 noise
        return ('', 204)

    @app.route('/favicon.ico')
    def favicon():
        # Prefer static favicon
        fav = os.path.join(app.root_path, 'static', 'favicon.ico')
        if os.path.exists(fav):
            return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')
        return ('', 204)

    # Context processor to inject current avatar URLs into all templates
    @app.context_processor
    def inject_current_avatar():
        from flask import session, url_for
        avatar_url = None
        avatar_thumb = None
        try:
            if 'user_id' in session and session.get('user_type') == 'student':
                uid = session['user_id']
                upload_dir = os.path.join(app.root_path, app.config.get('UPLOAD_FOLDER', 'uploads'))
                # prefer thumb
                pattern = os.path.join(upload_dir, f"student_{uid}_thumb.*")
                matches = glob.glob(pattern)
                if matches:
                    avatar_thumb = url_for('uploaded_file', filename=os.path.basename(matches[0]))
                else:
                    pattern2 = os.path.join(upload_dir, f"student_{uid}.*")
                    matches2 = glob.glob(pattern2)
                    if matches2:
                        avatar_url = url_for('uploaded_file', filename=os.path.basename(matches2[0]))
            elif 'user_id' in session and session.get('user_type') == 'faculty':
                # you can add faculty-specific avatar logic here if implemented
                pass
        except Exception:
            avatar_url = None
            avatar_thumb = None

        return dict(current_avatar_url=avatar_url, current_avatar_thumb_url=avatar_thumb)

    # File upload endpoint
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """
        General file upload endpoint
        """
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Create upload directory if it doesn't exist
        upload_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Save file (you might want to add more validation and security)
        filename = file.filename
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'file_path': file_path
        })

if __name__ == '__main__':
    # Create Flask application
    app = create_app()
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )