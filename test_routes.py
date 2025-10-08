"""
Test script to check what routes are registered in the Flask app
"""
from app import create_app

def test_routes():
    """Test what routes are available in the Flask app"""
    app = create_app()
    
    print("Registered Routes:")
    print("=" * 50)
    
    with app.app_context():
        for rule in app.url_map.iter_rules():
            methods = ', '.join(rule.methods)
            print(f"{rule.rule:<30} {methods:<20} {rule.endpoint}")
    
    print("\n" + "=" * 50)
    print(f"Total routes: {len(list(app.url_map.iter_rules()))}")

if __name__ == '__main__':
    test_routes()