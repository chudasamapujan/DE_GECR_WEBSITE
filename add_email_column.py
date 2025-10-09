"""
Add email_notifications_enabled column to existing students table
Run this to update the database schema without losing data
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'instance' / 'gec_rajkot.db'

def add_email_notification_column():
    """Add email_notifications_enabled column to students table"""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        print("   Run 'python app.py' first to create the database")
        return False
    
    print(f"📊 Updating database: {DB_PATH}")
    print()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(students)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'email_notifications_enabled' in columns:
            print("✅ Column 'email_notifications_enabled' already exists!")
            conn.close()
            return True
        
        print("🔧 Adding 'email_notifications_enabled' column...")
        
        # Add the new column with default value TRUE (1)
        cursor.execute("""
            ALTER TABLE students 
            ADD COLUMN email_notifications_enabled BOOLEAN DEFAULT 1
        """)
        
        conn.commit()
        print("✅ Column added successfully!")
        print()
        
        # Count students
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        
        print(f"✅ {count} existing student(s) now have email notifications ENABLED by default")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.close()
        return False


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("   Add Email Notifications Column to Students Table")
    print("=" * 60)
    print()
    
    success = add_email_notification_column()
    
    print()
    if success:
        print("✅ Database updated successfully!")
        print()
        print("📚 Next Steps:")
        print("1. Restart your Flask server (Ctrl+C, then 'python app.py')")
        print("2. Login should now work without errors")
        print("3. Run 'python test_gmail_auth.py' to set up Gmail")
    else:
        print("❌ Update failed")
        print()
        print("💡 Try running: python recreate_db.py")
        print("   (Warning: This will delete all existing data)")
    print()
