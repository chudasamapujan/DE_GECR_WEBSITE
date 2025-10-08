"""
Database Migration Script
Migrate from old complex schema to new simplified GECR schema
Preserves existing user data and creates new structure
"""

from database import db
from models.gecr_models import Student, Faculty
import os
from datetime import datetime


def backup_existing_data():
    """Backup existing data before migration"""
    print("Creating backup of existing data...")
    
    # Import old models
    try:
        from models.student_model import Student as OldStudent
        from models.faculty_model import Faculty as OldFaculty
        
        old_students = OldStudent.query.all()
        old_faculty = OldFaculty.query.all()
        
        backup_data = {
            'students': [student.to_dict() for student in old_students],
            'faculty': [faculty.to_dict() for faculty in old_faculty],
            'migration_date': datetime.now().isoformat()
        }
        
        # Write backup to file
        import json
        with open('data_backup.json', 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"Backed up {len(old_students)} students and {len(old_faculty)} faculty")
        return backup_data
        
    except Exception as e:
        print(f"Could not backup existing data: {e}")
        return None


def migrate_student_data(old_students):
    """Migrate student data to new schema"""
    print("Migrating student data...")
    
    migrated_count = 0
    for old_student in old_students:
        try:
            # Extract roll number from email or use enrollment number
            roll_no = getattr(old_student, 'enrollment_number', None)
            if not roll_no:
                # Try to extract from email
                email_parts = old_student.email.split('@')
                roll_no = email_parts[0] if email_parts else f"STU{old_student.id}"
            
            # Create new student record
            new_student = Student(
                roll_no=roll_no,
                name=old_student.full_name,
                email=old_student.email,
                department=getattr(old_student, 'department', 'Computer Engineering'),
                semester=getattr(old_student, 'current_semester', 1),
                dob=getattr(old_student, 'date_of_birth', None),
                address=getattr(old_student, 'address', None),
                phone=getattr(old_student, 'phone', None),
                fees_paid=False  # Default value
            )
            
            # Set password (copy existing hash or set default)
            if hasattr(old_student, 'password_hash'):
                new_student.password = old_student.password_hash
            else:
                new_student.set_password('password123')  # Default password
            
            db.session.add(new_student)
            migrated_count += 1
            
        except Exception as e:
            print(f"Error migrating student {old_student.email}: {e}")
    
    print(f"Migrated {migrated_count} students")
    return migrated_count


def migrate_faculty_data(old_faculty):
    """Migrate faculty data to new schema"""
    print("Migrating faculty data...")
    
    migrated_count = 0
    for old_fac in old_faculty:
        try:
            # Create new faculty record
            new_faculty = Faculty(
                name=old_fac.full_name,
                email=old_fac.email,
                department=getattr(old_fac, 'department', 'Computer Engineering'),
                designation=getattr(old_fac, 'designation', 'Professor'),
                salary=0,  # Default value
                phone=getattr(old_fac, 'phone', None)
            )
            
            # Set password (copy existing hash or set default)
            if hasattr(old_fac, 'password_hash'):
                new_faculty.password = old_fac.password_hash
            else:
                new_faculty.set_password('password123')  # Default password
            
            db.session.add(new_faculty)
            migrated_count += 1
            
        except Exception as e:
            print(f"Error migrating faculty {old_fac.email}: {e}")
    
    print(f"Migrated {migrated_count} faculty")
    return migrated_count


def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    
    # Check if test users already exist
    if not Student.find_by_email("test.student@students.gecrajkot.ac.in"):
        test_student = Student(
            roll_no="test.student",
            name="Test Student",
            email="test.student@students.gecrajkot.ac.in",
            department="Computer Engineering",
            semester=5,
            phone="9999999999",
            fees_paid=True
        )
        test_student.set_password("password123")
        db.session.add(test_student)
        print("Created test student")
    
    if not Faculty.find_by_email("test.faculty@faculty.gecrajkot.ac.in"):
        test_faculty = Faculty(
            name="Test Faculty",
            email="test.faculty@faculty.gecrajkot.ac.in",
            department="Computer Engineering",
            designation="Professor",
            salary=50000,
            phone="8888888888"
        )
        test_faculty.set_password("password123")
        db.session.add(test_faculty)
        print("Created test faculty")


def run_migration(app):
    """Run the complete migration"""
    with app.app_context():
        print("=== Starting Database Migration ===")
        
        # Step 1: Backup existing data
        backup_data = backup_existing_data()
        
        # Step 2: Drop old tables and create new ones
        print("Dropping old tables and creating new schema...")
        db.drop_all()
        db.create_all()
        print("New database schema created")
        
        # Step 3: Migrate data if backup exists
        if backup_data:
            try:
                # Import old models for migration
                from models.student_model import Student as OldStudent
                from models.faculty_model import Faculty as OldFaculty
                
                old_students = OldStudent.query.all()
                old_faculty = OldFaculty.query.all()
                
                migrate_student_data(old_students)
                migrate_faculty_data(old_faculty)
                
            except Exception as e:
                print(f"Could not migrate old data: {e}")
                print("Creating fresh sample data instead...")
        
        # Step 4: Create sample data
        create_sample_data()
        
        # Step 5: Commit all changes
        try:
            db.session.commit()
            print("Migration completed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")
            raise
        
        print("=== Migration Complete ===")


if __name__ == "__main__":
    # This can be run directly for migration
    from app import create_app
    
    app = create_app()
    run_migration(app)