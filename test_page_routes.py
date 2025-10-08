"""
Test script to verify all page routes are working
"""
import requests
import sys

def test_page_routes():
    """Test all main page routes to see if they're accessible"""
    base_url = "http://127.0.0.1:5000"
    
    # List of routes to test
    routes = [
        "/",
        "/auth/login/student",
        "/auth/login/faculty", 
        "/auth/register/student",
        "/auth/register/faculty",
        "/auth/forgot/student",
        "/auth/forgot/faculty",
        "/student/dashboard",
        "/faculty/dashboard",
        "/student/profile",
        "/student/attendance", 
        "/student/schedule",
        "/student/events",
        "/faculty/profile",
        "/faculty/subjects",
        "/faculty/students",
        "/faculty/assignments",
    "/faculty/attendance",
    "/faculty/schedule"
    ]
    
    print("Testing Page Routes:")
    print("=" * 60)
    
    working_routes = []
    failing_routes = []
    
    for route in routes:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            status = response.status_code
            
            if status == 200:
                print(f"✅ {route:<25} Status: {status}")
                working_routes.append(route)
            elif status == 302:
                print(f"🔀 {route:<25} Status: {status} (Redirect - likely needs auth)")
                working_routes.append(route)
            else:
                print(f"❌ {route:<25} Status: {status}")
                failing_routes.append(route)
                
        except requests.exceptions.ConnectionError:
            print(f"💥 {route:<25} Connection Error - Server not running?")
            failing_routes.append(route)
        except requests.exceptions.Timeout:
            print(f"⏰ {route:<25} Timeout")
            failing_routes.append(route)
        except Exception as e:
            print(f"❌ {route:<25} Error: {str(e)}")
            failing_routes.append(route)
    
    print("\n" + "=" * 60)
    print(f"✅ Working routes: {len(working_routes)}/{len(routes)}")
    print(f"❌ Failing routes: {len(failing_routes)}/{len(routes)}")
    
    if failing_routes:
        print(f"\nFailed routes:")
        for route in failing_routes:
            print(f"  - {route}")
    
    return len(failing_routes) == 0

if __name__ == '__main__':
    success = test_page_routes()
    sys.exit(0 if success else 1)