from app import create_app

app = create_app('testing')
client = app.test_client()

routes = ['/', '/student/dashboard', '/student/profile', '/student/settings', '/faculty/dashboard', '/faculty/profile']
for r in routes:
    try:
        resp = client.get(r)
        print(r, resp.status_code)
    except Exception as e:
        print(r, 'ERROR', e)
