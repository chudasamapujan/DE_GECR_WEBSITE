import io
import os
from PIL import Image
import tempfile

from app import create_app
from database import init_database, create_tables, db
from models.gecr_models import Student


def make_test_image_bytes():
    # create a small red PNG in-memory
    img = Image.new('RGB', (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def setup_test_db(app):
    # Ensure fresh in-memory DB
    with app.app_context():
        # Rebind db
        create_tables(app)


def test_student_photo_upload_and_profile(tmp_path, monkeypatch):
    # Create app in testing mode
    app = create_app('testing')
    upload_dir = os.path.join(app.root_path, app.config.get('UPLOAD_FOLDER', 'uploads'))

    # Ensure uploads dir is a temp directory inside tmp_path
    tmp_upload = tmp_path / 'uploads'
    tmp_upload.mkdir()

    # Monkeypatch app upload folder to temp
    monkeypatch.setitem(app.config, 'UPLOAD_FOLDER', str(tmp_upload))

    with app.app_context():
        # Create DB tables
        from database import db
        db.create_all()

        # Create a sample student
        student = Student(roll_no='2025TEST', name='Test Student', email='test@student.local', semester=1)
        student.set_password('password')
        db.session.add(student)
        db.session.commit()

        # Use test client and set session for logged-in student
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user_id'] = student.student_id
            sess['user_type'] = 'student'
            sess['user_email'] = student.email
            sess['user_name'] = student.name

        # prepare in-memory image
        img_buf = make_test_image_bytes()
        data = {
            'photo': (img_buf, 'test.png')
        }

        # POST upload
        resp = client.post('/student/upload-photo', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert resp.status_code == 200

        # Check files in upload dir
        files = os.listdir(str(tmp_upload))
        assert any(f.startswith(f"student_{student.student_id}") for f in files)

        # Request profile page and ensure image URL is present
        profile_resp = client.get('/student/profile')
        assert profile_resp.status_code == 200
        html = profile_resp.get_data(as_text=True)
        # thumbnail filename should be referenced
        assert f"student_{student.student_id}_thumb" in html or f"student_{student.student_id}." in html
