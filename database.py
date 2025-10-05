"""
Database Configuration for GEC Rajkot Website
SQLite database setup with SQLAlchemy
Author: GEC Rajkot Development Team
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def init_database(app):
    """
    Initialize database with Flask app
    """
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gec_rajkot.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False  # Set to True for SQL debugging
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    return db

def create_tables(app):
    """
    Create all database tables
    """
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def drop_tables(app):
    """
    Drop all database tables (use with caution!)
    """
    with app.app_context():
        db.drop_all()
        print("All database tables dropped!")

def reset_database(app):
    """
    Reset database by dropping and recreating all tables
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset completed!")

# Database utility functions
def get_db_stats():
    """
    Get database statistics
    """
    try:
        # Import models here to avoid circular imports
        from models import Student, Faculty, OTP
        
        stats = {
            'students': Student.query.count(),
            'faculty': Faculty.query.count(),
            'active_otps': OTP.query.filter_by(is_used=False, is_expired=False).count(),
            'total_otps': OTP.query.count()
        }
        return stats
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return None

def cleanup_expired_data():
    """
    Cleanup expired data from database
    """
    try:
        from models import OTP
        cleaned_otps = OTP.cleanup_expired_otps()
        print(f"Cleaned up {cleaned_otps} expired OTP records")
        return cleaned_otps
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return 0