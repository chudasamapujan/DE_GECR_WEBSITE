# Quick Start Guide - Excel Attendance Upload

## For Faculty Users

### Step 1: Prepare Your Excel File

Create an Excel file with this format:

| Roll No | 15/01/2024 | 16/01/2024 | 17/01/2024 |
|---------|------------|------------|------------|
| 2020001 | P          | P          | A          |
| 2020002 | A          | P          | P          |
| 2020003 | P          | L          | P          |

**Key Points:**
- **First Column**: Must be labeled "Roll No" with student roll numbers
- **Date Columns**: Dates in DD/MM/YYYY or YYYY-MM-DD format
- **Attendance Values**:
  - `P` = Present
  - `A` = Absent
  - `L` = Late

### Step 2: Upload to System

1. Login to faculty portal
2. Go to **Attendance** page
3. Scroll to **"Upload Attendance from Excel"** section
4. Select **Subject** from dropdown
5. Click **"Choose File"** and select your Excel file
6. Click **"Upload Attendance"** button
7. Wait for success message

### Step 3: Verify Upload

Check the success message for:
- ✅ Number of records inserted
- 🔄 Number of records updated
- ⏭️ Number of records skipped
- 📅 Dates processed
- 👥 Total students affected

## For Developers

### Quick Setup

```bash
# 1. Install dependencies
pip install openpyxl pandas

# 2. Add sample subjects (if needed)
python add_subjects.py

# 3. Test the parser
python test_attendance_upload.py

# 4. Start Flask app
python app.py
```

### API Usage

```python
import requests

# Login first
session = requests.Session()
session.post('http://localhost:5000/api/auth/faculty/login', 
    json={'email': 'faculty@gecr.edu', 'password': 'password'})

# Upload Excel
with open('attendance.xlsx', 'rb') as f:
    files = {'file': f}
    data = {'subject_id': '1'}
    response = session.post(
        'http://localhost:5000/api/faculty/attendance/upload',
        files=files, 
        data=data
    )
    
print(response.json())
```

### Testing Locally

```python
# Create test file
from test_attendance_upload import create_sample_attendance_excel
create_sample_attendance_excel('test.xlsx')

# Parse it
from utils.excel_parser import parse_attendance_excel
result = parse_attendance_excel('test.xlsx')
print(f"Found {len(result['records'])} attendance records")
```

## Troubleshooting

### Common Errors

**"No valid date columns found"**
- ✅ Fix: Ensure date columns are formatted as dates in Excel
- ✅ Fix: Use DD/MM/YYYY or YYYY-MM-DD format

**"Could not find 'Roll No' column"**
- ✅ Fix: First column header must be exactly "Roll No"

**"Student with roll number X not found"**
- ✅ Fix: Verify student exists in database with that roll number
- ✅ Fix: Check for typos in roll numbers

**"Invalid file format"**
- ✅ Fix: Only .xlsx and .xls files are supported
- ✅ Fix: Save Excel file in correct format

### Getting Help

1. Check `ATTENDANCE_UPLOAD_IMPLEMENTATION.md` for full documentation
2. Review error messages in upload response
3. Check browser console for JavaScript errors
4. Verify subject_id exists in database

## Sample Data

### Students in Test Database
- Roll No: 2020001 (Test Student)
- Roll No: 230200143013 (CHUDASAMA PUJAN)

### Subjects Available
1. Database Management Systems (ID: 1)
2. Software Engineering (ID: 2)
3. Data Structures and Algorithms (ID: 3)
4. Web Technologies (ID: 4)
5. Programming Fundamentals (ID: 5)

## File Locations

```
project/
├── utils/
│   └── excel_parser.py          # Excel parsing logic
├── routes/
│   └── faculty_routes.py        # Upload endpoint
├── templates/
│   └── faculty/
│       └── attendance.html      # Upload UI
├── tests/
│   ├── test_attendance_upload.py
│   └── test_attendance_integration.py
└── temp_uploads/                # Temporary file storage
```

## Quick Commands

```bash
# Create sample Excel
python -c "from test_attendance_upload import create_sample_attendance_excel; create_sample_attendance_excel('attendance.xlsx')"

# Test parser only
python -c "from utils.excel_parser import parse_attendance_excel; result = parse_attendance_excel('attendance.xlsx'); print(f'Parsed {len(result[\"records\"])} records')"

# Add subjects to database
python add_subjects.py

# Check database
python -c "from app import create_app; from models.gecr_models import Student, Subject; app = create_app(); 
with app.app_context(): print(f'Students: {Student.query.count()}, Subjects: {Subject.query.count()}')"
```

---

**Need More Help?** See full documentation in `ATTENDANCE_UPLOAD_IMPLEMENTATION.md`
