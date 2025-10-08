"""
Test script to debug the "Not found" error
"""
import requests

def test_endpoints():
    base_url = "http://127.0.0.1:5000"
    
    print("Testing endpoints to debug 'Not found' error:")
    print("=" * 50)
    
    # Test basic endpoints
    endpoints = [
        "/",
        "/auth/login/student",
        "/student/dashboard",
        "/faculty/dashboard"
    ]
    
    for endpoint in endpoints:
        try:
            resp = requests.get(f"{base_url}{endpoint}")
            print(f"{endpoint}:")
            print(f"  Status: {resp.status_code}")
            print(f"  Content: {resp.text[:100]}...")
            print()
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")
            print()

if __name__ == "__main__":
    test_endpoints()