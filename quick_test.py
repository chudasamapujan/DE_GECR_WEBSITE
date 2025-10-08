import requests

routes = [
    '/',
    '/auth/login/student', 
    '/auth/login/faculty',
    '/student/dashboard',
    '/faculty/dashboard',
    '/student/attendance',
    '/faculty/assignments'
]

print("Testing key routes:")
for route in routes:
    try:
        resp = requests.get(f'http://127.0.0.1:5000{route}')
        print(f'{route}: {resp.status_code}')
    except Exception as e:
        print(f'{route}: ERROR - {e}')