"""
Script to update all HTML template URLs to remove .html extensions
Updates navigation links to use proper Flask routes
"""

import os
import re

def update_template_urls():
    """Update all template files to use proper Flask routes"""
    
    # Define URL mappings from .html to Flask routes
    url_mappings = {
        # Student URLs
        'dashboard.html': '/student/dashboard',
        'student-profile.html': '/student/profile',
    'academics.html': '/student/academics',
        'schedule.html': '/student/schedule',
    # resources removed - keep mapping empty to avoid accidental rewrites
    # resources.html removed (archived)
    # 'resources.html': '#',
        'events.html': '/student/events',
        
        # Faculty URLs  
        'faculty-dashboard.html': '/faculty/dashboard',
        '../faculty-dashboard.html': '/faculty/dashboard',
        'faculty-profile.html': '/faculty/profile',
        'faculty-subjects.html': '/faculty/subjects',
        'faculty-students.html': '/faculty/students',
        'faculty-assignments.html': '/faculty/assignments',
        'faculty-attendance.html': '/faculty/attendance',
        'faculty-grades.html': '/faculty/grades',
        'faculty-schedule.html': '/faculty/schedule',
        
        # Auth URLs
        'student.html': '/auth/login/student',
        'faculty.html': '/auth/login/faculty',
        'student-register.html': '/auth/register/student',
        'faculty-register.html': '/auth/register/faculty',
        'student-forgot.html': '/auth/forgot/student',
        'faculty-forgot.html': '/auth/forgot/faculty',
        
        # Other URLs
        'settings.html': '/shared/settings',
        'index.html': '/',
        '../../index.html': '/',
        '../index.html': '/',
    }
    
    # Directory to process
    templates_dir = 'templates'
    
    # Track changes
    updated_files = []
    total_replacements = 0
    
    # Process all HTML files in templates directory
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                
                try:
                    # Read file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    file_changes = 0
                    
                    # Apply URL mappings
                    for old_url, new_url in url_mappings.items():
                        # Pattern to match href="old_url"
                        pattern = f'href="{re.escape(old_url)}"'
                        replacement = f'href="{new_url}"'
                        
                        count = len(re.findall(pattern, content))
                        if count > 0:
                            content = re.sub(pattern, replacement, content)
                            file_changes += count
                            print(f"  ✅ {old_url} → {new_url} ({count} replacements)")
                    
                    # Write back if changes were made
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        updated_files.append(file_path)
                        total_replacements += file_changes
                        print(f"  📝 Updated {file_path} ({file_changes} changes)")
                    
                except Exception as e:
                    print(f"  ❌ Error processing {file_path}: {e}")
    
    print(f"\n{'='*60}")
    print(f"URL Update Summary:")
    print(f"📁 Files updated: {len(updated_files)}")
    print(f"🔄 Total replacements: {total_replacements}")
    print(f"\nUpdated files:")
    for file_path in updated_files:
        print(f"  ✅ {file_path}")

if __name__ == '__main__':
    update_template_urls()
    print(f"\n🎉 All HTML template URLs updated successfully!")
    print(f"💡 URLs now use Flask routes without .html extensions")