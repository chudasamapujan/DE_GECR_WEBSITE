"""
Database Configuration for GEC Rajkot Website
SQLite database setup with SQLAlchemy - GECR Schema
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
    
    # Import all models to ensure they are registered
    from models.gecr_models import (
        Student, Faculty, Subject, Timetable, 
        Attendance, Assignment, Submission, 
        Message, Fee, Salary, Announcement, Event, Activity, Notification
    )
    
    return db

def create_tables(app):
    """
    Create all database tables
    """
    with app.app_context():
        # Import models
        from models.gecr_models import (
            Student, Faculty, Subject, Timetable, 
            Attendance, Assignment, Submission, 
            Message, Fee, Salary, Announcement, Event, Activity, Notification
        )
        
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
        # Import models
        from models.gecr_models import (
            Student, Faculty, Subject, Timetable, 
            Attendance, Assignment, Submission, 
            Message, Fee, Salary, Announcement, Event, Activity, Notification
        )
        
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
        from models.gecr_models import Student, Faculty
        
        stats = {
            'students': Student.query.count(),
            'faculty': Faculty.query.count(),
            'total_users': Student.query.count() + Faculty.query.count()
        }
        return stats
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return None