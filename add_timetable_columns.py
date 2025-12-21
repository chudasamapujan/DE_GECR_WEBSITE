"""
Database migration script to add room and class_type columns to timetable table
"""

import sqlite3
import os

# Database path
DB_PATH = os.path.join('instance', 'gec_rajkot.db')

def add_columns():
    """Add room and class_type columns to timetable table"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Adding columns to timetable table...")
        
        # Add room column
        try:
            cursor.execute("ALTER TABLE timetable ADD COLUMN room VARCHAR(100)")
            print("✓ Added 'room' column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("  'room' column already exists")
            else:
                raise
        
        # Add class_type column
        try:
            cursor.execute("ALTER TABLE timetable ADD COLUMN class_type VARCHAR(20) DEFAULT 'Lecture'")
            print("✓ Added 'class_type' column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("  'class_type' column already exists")
            else:
                raise
        
        # Commit changes
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
        # Verify columns
        cursor.execute("PRAGMA table_info(timetable)")
        columns = cursor.fetchall()
        print("\nCurrent timetable columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        raise

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        print("Please make sure the database exists.")
    else:
        add_columns()
