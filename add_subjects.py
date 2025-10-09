"""
Quick script to add sample subjects to the database
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from models.gecr_models import Subject
from app import create_app

app = create_app()

with app.app_context():
    print("Adding sample subjects to database...")
    
    subjects = [
        {'subject_name': 'Database Management Systems', 'department': 'Computer Engineering', 'semester': 5},
        {'subject_name': 'Software Engineering', 'department': 'Computer Engineering', 'semester': 7},
        {'subject_name': 'Data Structures and Algorithms', 'department': 'Computer Engineering', 'semester': 5},
        {'subject_name': 'Web Technologies', 'department': 'Computer Engineering', 'semester': 7},
        {'subject_name': 'Programming Fundamentals', 'department': 'Computer Engineering', 'semester': 1},
    ]
    
    for subj_data in subjects:
        existing = Subject.query.filter_by(subject_name=subj_data['subject_name']).first()
        if not existing:
            subj = Subject(**subj_data)
            db.session.add(subj)
            print(f"✓ Added: {subj_data['subject_name']}")
        else:
            print(f"  Skip: {subj_data['subject_name']} - already exists")
    
    db.session.commit()
    print("\n✅ Subjects added successfully!")
    
    # Show all subjects
    print("\nAll subjects in database:")
    all_subjects = Subject.query.all()
    for s in all_subjects:
        print(f"  ID: {s.subject_id}, Name: {s.subject_name}")
