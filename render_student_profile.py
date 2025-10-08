from app import create_app
from flask import render_template

app = create_app()

with app.app_context():
    # Create a fake student dict to render
    student = {
        'name': 'Test Student',
        'email': 'test@student.com',
        'roll_no': '21CE999',
        'branch': 'Computer Engineering',
        'semester': 6,
        'phone': '+91 90000 00000',
        'date_of_birth': '01/01/2003',
        'address': 'Rajkot',
        'parent_contact': '+91 90000 00001',
        'admission_year': 2021,
        'cgpa': 8.7
    }

    html = render_template('student/student-profile.html', student=student, active_page='profile')
    print(html[:1000])
