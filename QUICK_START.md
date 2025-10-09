# 🚀 Quick Start Guide - Student Management System

## Start the System

```bash
# 1. Start Flask app
python app.py

# 2. Open browser
http://127.0.0.1:5000
```

---

## Test Credentials

### Faculty:
```
Email: test.faculty@gecr.edu
Password: faculty123
```

### Student:
```
Roll No: TEST001
Email: test.student@gecr.edu
Password: student123
```

---

## Quick Actions

### As Faculty:

1. **View All Students**
   - Login → Students page
   - See list with attendance %

2. **Upload Students (Excel)**
   - Click "Upload Excel" button
   - Select .xlsx file with columns:
     - Roll No (required)
     - Name (required)
     - Email (required)
     - Password, Department, Semester, Phone (optional)
   - Click Upload
   - Students appear immediately

3. **Add Single Student**
   - Click "Add Student" button
   - Fill form
   - Submit
   - Student added with welcome notification

4. **Search/Filter**
   - Search box: Type name/roll/email
   - Subject filter: Show students in specific subject
   - Semester filter: Filter by semester

### As Student:

1. **View Dashboard**
   - Login → Dashboard shows:
     - Enrolled subjects count
     - Overall attendance %
     - Total classes
     - Notification count
     - List of enrolled subjects

2. **View Attendance**
   - Go to Attendance page
   - See overall stats
   - See subject-wise breakdown
   - Filter by subject or date

3. **View Subjects**
   - Dashboard shows enrolled subjects
   - Each subject shows:
     - Subject code and name
     - Faculty name
     - Attendance percentage

---

## API Endpoints

### Faculty:
```
GET  /api/faculty/students              # List all students
POST /api/faculty/students              # Add single student
POST /api/faculty/students/upload       # Upload Excel
```

### Student:
```
GET  /api/student/profile               # Profile + enrolled subjects
GET  /api/student/subjects              # Subjects with attendance
GET  /api/student/attendance            # Detailed attendance
```

---

## Excel Format

| Roll No | Name | Email | Password | Department | Semester | Phone |
|---------|------|-------|----------|------------|----------|-------|
| 2024001 | John | john@gecr.edu | student123 | Computer Engineering | 5 | 9876543210 |

**Required:** Roll No, Name, Email  
**Optional:** Password (defaults to 'student123'), Department, Semester, Phone

---

## Troubleshooting

### Students not showing?
```bash
# Check database
python -c "from models.gecr_models import Student; from app import create_app; app = create_app(); ctx = app.app_context(); ctx.push(); print(Student.query.count(), 'students')"
```

### Create test users
```bash
python create_test_users.py
```

### Create test enrollments
```bash
python setup_enrollments.py
```

### Test all endpoints
```bash
python test_complete_flow.py
```

---

## Features at a Glance

✅ Faculty can upload students (Excel or manual)  
✅ Students appear immediately in list  
✅ Real-time attendance tracking  
✅ Subject-wise attendance breakdown  
✅ Search and filter functionality  
✅ Welcome notifications for new students  
✅ Color-coded attendance percentages  
✅ Progress bars for visual feedback  
✅ Responsive design (mobile-friendly)  
✅ No static data - all from database  

---

## Quick Test

```bash
# 1. Start app
python app.py

# 2. Create test data
python create_test_users.py
python setup_enrollments.py

# 3. Test in browser
# Login as faculty: test.faculty@gecr.edu / faculty123
# Go to Students → Upload or Add student
# Login as student: TEST001 / student123
# View dashboard and attendance

# 4. Or test via API
python test_complete_flow.py
```

---

## File Structure

```
DE_GECR_WEBSITE/
├── app.py                          # Main Flask app
├── models/
│   └── gecr_models.py             # Database models
├── routes/
│   ├── faculty_routes.py          # Faculty endpoints
│   └── student_routes.py          # Student endpoints
├── templates/
│   ├── faculty/
│   │   └── students.html          # Student list with upload
│   └── student/
│       ├── dashboard.html         # Real-time dashboard
│       └── attendance.html        # Attendance tracking
├── utils/
│   └── student_parser.py          # Excel parser
└── instance/
    └── gec_rajkot.db             # SQLite database
```

---

## Color Codes

**Attendance Percentages:**
- 🟢 Green: ≥85% (Good)
- 🟡 Yellow: 75-85% (Warning)
- 🔴 Red: <75% (Critical)

**Status:**
- ✓ Present (Green)
- ✗ Absent (Red)
- ⚠ Late (Yellow)

---

## That's It! 🎉

Everything is connected to the database.  
Upload students → They appear immediately.  
No more static data!
