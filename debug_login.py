from app import create_app
import json

app = create_app('development')
with app.app_context():
    with app.test_client() as client:
        resp = client.post('/api/auth/faculty/login', json={'email':'faculty@test.com','password':'password123'})
        print('status', resp.status_code)
        try:
            print(resp.get_json())
        except Exception:
            print(resp.data)
        # Print session cookie
        print('cookies:', client.cookie_jar)
