"""
Main Flask Application for GEC Rajkot Website
Backend API server with authentication and user management
Author: GEC Rajkot Development Team
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from datetime import datetime, timedelta
import os
import logging
from logging.handlers import RotatingFileHandler

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