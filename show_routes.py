"""
Show all available routes for the GECR website
"""

routes_info = {
    "Authentication Pages": [
        "http://127.0.0.1:5000/auth/login/student",
        "http://127.0.0.1:5000/auth/login/faculty", 
        "http://127.0.0.1:5000/auth/register/student",
        "http://127.0.0.1:5000/auth/register/faculty",
        "http://127.0.0.1:5000/auth/forgot/student",
        "http://127.0.0.1:5000/auth/forgot/faculty"
    ],
    "Student Pages": [
        "http://127.0.0.1:5000/student/dashboard",
        "http://127.0.0.1:5000/student/profile", 
        "http://127.0.0.1:5000/student/attendance",
        "http://127.0.0.1:5000/student/schedule",
        "http://127.0.0.1:5000/student/events",
        "http://127.0.0.1:5000/student/settings"
    ],
    "Faculty Pages": [
        "http://127.0.0.1:5000/faculty/dashboard",
        "http://127.0.0.1:5000/faculty/profile",
        "http://127.0.0.1:5000/faculty/subjects", 
        "http://127.0.0.1:5000/faculty/students",
        "http://127.0.0.1:5000/faculty/assignments",
        "http://127.0.0.1:5000/faculty/attendance",
        "http://127.0.0.1:5000/faculty/schedule",
        "http://127.0.0.1:5000/faculty/events",
        "http://127.0.0.1:5000/faculty/settings"
    ]
}

print("🌐 GECR Website - Correct URLs")
print("=" * 60)

for category, urls in routes_info.items():
    print(f"\n📂 {category}:")
    for url in urls:
        print(f"   ✅ {url}")

print(f"\n💡 Important Notes:")
print(f"   • Don't add .html to URLs")
print(f"   • Use /student/profile NOT /student/student-profile.html") 
print(f"   • Protected pages redirect to login if not authenticated")
print(f"   • Start with: http://127.0.0.1:5000/auth/login/student")