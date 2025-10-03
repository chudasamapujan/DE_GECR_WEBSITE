from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from config import Config
from database import Database
from routes.auth import auth_bp
from routes.student import student_bp
from routes.faculty import faculty_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:5500"])
    JWTManager(app)
    Mail(app)
    
    # Initialize database
    Database.initialize()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(faculty_bp, url_prefix='/api/faculty')
    
    @app.route('/')
    def index():
        return {'message': 'GEC Rajkot Backend API', 'status': 'running'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'database': 'connected'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)