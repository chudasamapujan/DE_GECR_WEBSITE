import sys
from pathlib import Path
import tempfile

sys.path.insert(0, '.')
from app import create_app
from database import db
from models.gecr_models import Student
from PIL import Image
import io, os

print('Starting inline upload flow test')
app = create_app('testing')
# Use temp dir to avoid polluting repo
tmpdir = Path(tempfile.mkdtemp())
app.config['UPLOAD_FOLDER'] = str(tmpdir)

with app.app_context():
    db.create_all()
    student = Student(roll_no='2025TEST', name='Test Student', email='test@student.local', semester=1)
    student.set_password('password')
    db.session.add(student)
    db.session.commit()

    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = student.student_id
        sess['user_type'] = 'student'
        sess['user_email'] = student.email
        sess['user_name'] = student.name

    # create image
    img = Image.new('RGB', (100,100), (255,0,0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    data = {'photo': (buf, 'test.png')}
    resp = client.post('/student/upload-photo', data=data, content_type='multipart/form-data', follow_redirects=True)
    print('POST status:', resp.status_code)
    assert resp.status_code == 200

    files = os.listdir(str(tmpdir))
    print('Upload dir files:', files)
    assert any(f.startswith(f"student_{student.student_id}") for f in files)

    profile_resp = client.get('/student/profile')
    print('Profile status:', profile_resp.status_code)
    html = profile_resp.get_data(as_text=True)
    assert profile_resp.status_code == 200
    assert f"student_{student.student_id}_thumb" in html or f"student_{student.student_id}." in html

print('Inline test passed')
