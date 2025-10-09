# GEC Rajkot Website

A comprehensive web application for Government Engineering College, Rajkot, featuring separate portals for students and faculty with modern design and robust backend functionality.

## 🚀 Features

- **Modern Responsive Design** - Beautiful UI with glass morphism effects and smooth animations
- **Dual Portal System** - Separate interfaces for students and faculty
- **Complete Authentication** - Registration, login, password reset with OTP verification
- **Student Portal** - Dashboard, profile management, academics, attendance, assignments
- **Faculty Portal** - Dashboard, student management, attendance marking, assignment creation
- **Backend API** - Flask-based REST API with MongoDB integration
- **Email Integration** - Professional email templates for notifications

## 📁 Project Structure


## 🛠️ Technology Stack

### Frontend
- **HTML5** - Semantic markup with modern structure
- **CSS3** - Advanced styling with glass morphism, animations, and responsive design
- **JavaScript (ES6+)** - Modern JavaScript with classes and async/await
- **TailwindCSS** - Utility-first CSS framework
- **FontAwesome** - Icon library for UI elements

### Backend
- **Flask** - Python web framework
- **SQLite** - Lightweight SQL database for data storage
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Flask-JWT-Extended** - JWT authentication
- **Flask-Mail** - Email functionality
- **WTForms/Marshmallow** - Data validation and serialization
- **bcrypt** - Password hashing

### Design System
- **Glass Morphism** - Modern translucent design elements
- **Gradient Backgrounds** - Beautiful color transitions
- **Smooth Animations** - CSS transitions and keyframe animations
- **Responsive Layout** - Mobile-first design approach

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- SQLite (included with Python)
- Modern web browser
- Email account for SMTP (Gmail recommended)

### Frontend Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DE_GECR
   ```

2. **Open in web browser**
   ```bash
   # Navigate to frontend directory and start local server
   cd frontend
   python -m http.server 8000
   # Open http://localhost:8000
   ```

### Backend Setup
1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # macOS/Linux
   ```
   
   Edit `.env` file with your configuration:
   ```env
   DATABASE_URI=sqlite:///gec_rajkot.db
   JWT_SECRET_KEY=your-secret-key
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

5. **Initialize database**
   ```bash
   # Database will be created automatically on first run
   # SQLite file will be created in backend directory
   ```

6. **Run the backend**
   ```bash
   python app.py
   ```

   Backend will be available at: `http://localhost:5000`

## 📖 Usage Guide

### For Students
1. **Registration** - Visit `/frontend/login/student-register.html` for multi-step registration
2. **Login** - Access student portal via `/frontend/login/student.html`
3. **Dashboard** - View academic overview, attendance, and assignments
4. **Profile** - Manage personal information and academic details
5. **Resources** - Access learning materials and college information

### For Faculty
1. **Registration** - Register via `/frontend/login/faculty-register.html` (requires admin approval)
2. **Login** - Access faculty portal via `/frontend/login/faculty.html`
3. **Dashboard** - Overview of teaching schedule and student statistics
4. **Student Management** - View and manage enrolled students
5. **Attendance** - Mark attendance for classes
6. **Assignments** - Create and grade assignments

### Password Reset
- Both students and faculty can reset passwords using OTP verification
- Check email for 6-digit OTP code
- OTP expires in 10 minutes for security

## � Architecture Overview

### Frontend Organization
- **Separated Structure** - Clean separation between frontend and backend
- **Modular JavaScript** - Dedicated files for validations, API calls, and utilities
- **Template Support** - Optional Jinja templating for dynamic content
- **Asset Organization** - Logical grouping of CSS, JS, and static assets

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
