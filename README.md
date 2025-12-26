# GEC Rajkot - AI & Data Science Department Website

A comprehensive web application for the AI & Data Science department at Government Engineering College, Rajkot. Features separate portals for students and faculty with modern design, QR-based attendance system, and robust backend functionality.

## ⚡ Quick Start

### Automated Setup (Recommended)

```powershell
# 1. Clone or download the project
# 2. Open PowerShell in project directory
# 3. Allow script execution (first time only)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Run setup script
.\setup.ps1

# 5. Configure environment
# Edit .env file with your settings

# 6. Run the application
.\run.ps1

# 7. Open browser
# Navigate to http://localhost:5000
```

### Manual Setup

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
Copy-Item .env.example .env
# Edit .env with your settings

# Run application
python app.py
```

### Verify Installation

```powershell
# Check environment setup
.\check-env.ps1
```

📖 **Full installation guide**: See [INSTALLATION.md](INSTALLATION.md)

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

<<<<<<< HEAD
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
=======
>>>>>>> fbbba73cba07f62472468dae4cba4159d64e9650

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

<<<<<<< HEAD
For support or queries, contact the GEC Rajkot IT department.
=======
### Backend Architecture
- **SQLAlchemy ORM** - Database abstraction with model-based approach
- **Blueprint Structure** - Modular route organization
- **Model Separation** - Individual model files for different entities
- **SQLite Database** - Lightweight, file-based database (easy deployment)

## �🔗 API Integration

The frontend is designed to integrate seamlessly with the Flask backend. See `FRONTEND_INTEGRATION.md` for detailed integration instructions.

### Key API Endpoints
- `POST /api/auth/register/student` - Student registration
- `POST /api/auth/register/faculty` - Faculty registration
- `POST /api/auth/login` - User login
- `POST /api/auth/forgot-password` - Password reset request
- `GET /api/student/dashboard` - Student dashboard data
- `GET /api/faculty/dashboard` - Faculty dashboard data

## 🗄️ Database Schema

### Students Table (SQLAlchemy Model)
```python
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    enrollment_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    admission_year = db.Column(db.Integer, nullable=False)
    current_semester = db.Column(db.Integer, nullable=False)
    roll_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Faculty Table (SQLAlchemy Model)
```python
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    faculty_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    date_of_joining = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### OTPs Table (SQLAlchemy Model)
```python
class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(10), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## 🎨 Design Features

### Visual Elements
- **Glass Morphism Effects** - Translucent cards with backdrop blur
- **Gradient Backgrounds** - Beautiful color transitions
- **Floating Animations** - Subtle movement effects
- **Interactive Buttons** - Hover and click animations
- **Progress Indicators** - Multi-step form progress
- **Toast Notifications** - User feedback system

### Responsive Design
- **Mobile First** - Optimized for mobile devices
- **Tablet Support** - Perfect layout on tablets
- **Desktop Enhanced** - Full features on larger screens
- **Cross Browser** - Compatible with modern browsers

## 🔒 Security Features

- **Password Hashing** - bcrypt for secure password storage
- **JWT Authentication** - Stateless token-based auth
- **Input Validation** - Server-side validation for all forms
- **CORS Protection** - Controlled cross-origin requests
- **OTP Verification** - Email-based password reset
- **Session Management** - Secure token handling

## 📧 Email System

Professional email templates for:
- Password reset OTP verification
- Faculty registration approval notifications
- System notifications and alerts

## 🔧 Development

### Code Structure
- **Modular Design** - Separated concerns for maintainability
- **Reusable Components** - Shared CSS and JavaScript utilities
- **Clean Architecture** - Well-organized file structure
- **Documentation** - Comprehensive code comments

### Customization
- **Color Scheme** - Easy to modify CSS custom properties
- **Branding** - Simple logo and text replacement
- **Features** - Modular components for easy extension
- **Styling** - Organized CSS with clear naming conventions

## 📱 Browser Support

- **Chrome** 88+
- **Firefox** 85+
- **Safari** 14+
- **Edge** 88+
- **Mobile Browsers** - iOS Safari, Chrome Mobile

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is developed for Government Engineering College, Rajkot. All rights reserved.

## 📞 Support

For technical support or questions:
- **Email**: support@gec.ac.in
- **Documentation**: See `API_DOCUMENTATION.md` for backend details
- **Integration Guide**: See `FRONTEND_INTEGRATION.md` for setup instructions

## 🎯 Future Enhancements

- [ ] Mobile app development
- [ ] Real-time notifications
- [ ] Video conferencing integration
- [ ] Advanced analytics dashboard
- [ ] Document management system
- [ ] Online examination system
- [ ] Fee payment integration
- [ ] Library management system

---

**Developed with ❤️ for Government Engineering College, Rajkot**
>>>>>>> fbbba73cba07f62472468dae4cba4159d64e9650
