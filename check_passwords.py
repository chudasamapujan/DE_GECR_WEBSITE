from models.gecr_models import Faculty, Student
from app import create_app

app = create_app()
with app.app_context():
    print("Checking Faculty Passwords:")
    print("="*50)
    faculties = Faculty.query.all()
    for f in faculties:
        print(f"Email: {f.email}")
        print(f"  - password 'faculty123': {f.check_password('faculty123')}")
        print(f"  - password 'test': {f.check_password('test')}")
        print(f"  - password '123456': {f.check_password('123456')}")
        print()
    
    print("\nChecking Student Passwords:")
    print("="*50)
    students = Student.query.all()
    for s in students:
        print(f"Roll No: {s.roll_no} - {s.name}")
        print(f"  - password 'student123': {s.check_password('student123')}")
        print(f"  - password 'test': {s.check_password('test')}")
        print()
