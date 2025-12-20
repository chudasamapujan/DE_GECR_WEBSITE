# GEC Rajkot - AI & Data Science Department Website

A comprehensive web application for the AI & Data Science department at Government Engineering College, Rajkot. Features separate portals for students and faculty with modern design, QR-based attendance system, and robust backend functionality.

## 🚀 Features

- **Modern Responsive Design** - Beautiful UI with Tailwind CSS and glass morphism effects
- **Dual Portal System** - Separate interfaces for students and faculty
- **Complete Authentication** - Registration, login with secure password hashing
- **QR Attendance System** - Faculty generates QR codes, students scan with photo verification
- **Student Portal** - Dashboard, profile, academics, attendance tracking, subject enrollment
- **Faculty Portal** - Dashboard, student management, QR attendance, subject management
- **Backend API** - Flask-based REST API with SQLite database
- **Email Integration** - Gmail OAuth2 for notifications

## 📁 Project Structure

```
DE_GECR_WEBSITE/
├── app.py                      # Main Flask application
├── database.py                 # Database configuration
├── dashboard_data.py           # Dashboard data utilities
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── config/                     # Configuration files
│
├── models/
│   ├── __init__.py
│   └── gecr_models.py          # SQLAlchemy models (Student, Faculty, Subject, etc.)
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py          # Authentication endpoints
│   ├── student_routes.py       # Student API endpoints
│   ├── faculty_routes.py       # Faculty API endpoints
│   ├── attendance_routes.py    # Attendance management
│   ├── qr_attendance_routes.py # QR-based attendance system
│   ├── enrollment_routes.py    # Subject enrollment
│   └── subject_routes.py       # Subject management
│
├── templates/
│   ├── index.html              # Landing page
│   ├── auth/login/             # Authentication pages
│   ├── student/                # Student portal templates
│   └── faculty/                # Faculty portal templates
│
├── static/
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   ├── images/                 # Static images
│   ├── qr_codes/               # Generated QR codes
│   └── attendance_photos/      # Student attendance photos
│
├── utils/
│   ├── email_notification.py   # Email utilities
│   ├── excel_parser.py         # Excel file parsing
│   ├── send_email.py           # Email sending functions
│   └── student_parser.py       # Student data parsing
│
└── instance/
    └── gec_rajkot.db           # SQLite database
```

## 🛠️ Technology Stack

- **Backend**: Flask, Python 3.13, SQLAlchemy
- **Database**: SQLite
- **Frontend**: Jinja2 templates, Tailwind CSS, JavaScript
- **QR System**: qrcode[pil], html5-qrcode
- **Email**: Gmail OAuth2

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** (create `.env` file):
   ```
   SECRET_KEY=your_secret_key
   GMAIL_CLIENT_ID=your_gmail_client_id
   GMAIL_CLIENT_SECRET=your_gmail_client_secret
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the website**:
   - Open http://127.0.0.1:5000 in your browser

## 📱 Features by Portal

### Faculty Portal
- Dashboard with real-time statistics
- QR Code attendance generation
- Subject management
- Student management and enrollment
- Attendance reports

### Student Portal
- Dashboard with academic overview
- QR attendance scanning with photo verification
- Subject enrollment
- Attendance tracking
- Profile management

## 🎯 Department Focus

This application is configured for the **AI & Data Science** department at GEC Rajkot.

## 📧 Contact

For support or queries, contact the GEC Rajkot IT department.
