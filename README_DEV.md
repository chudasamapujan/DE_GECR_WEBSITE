Developer notes — GEC Rajkot Website

Project structure (key files):
- app.py — Flask application factory and main routes
- models/gecr_models.py — SQLAlchemy models
- templates/ — Jinja2 templates for student and faculty UIs
- static/ — CSS, JS and image assets
- uploads/ — runtime uploads (profile photos)
- tests/ — pytest tests (see tests/test_upload_flow.py)

Running tests (Windows PowerShell):
1. Create a virtualenv and install requirements:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

2. Run pytest from project root:
   pytest -q

Test details:
- tests/test_upload_flow.py creates an in-memory PNG, posts it to `/student/upload-photo` using Flask's test client, and verifies the uploaded file and thumbnail exist and the profile page references the image.

Notes:
- Tests run the app in `testing` config (uses in-memory SQLite). They monkeypatch the `UPLOAD_FOLDER` to a temporary directory.
- Running the real app will recreate `__pycache__` and `.pyc` files.
