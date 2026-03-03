# GEC Rajkot — AI & Data Science Department Portal

A full-stack web application for the **Artificial Intelligence & Data Science** department at **Government Engineering College, Rajkot**. It provides separate portals for students and faculty with attendance management, subject enrollment, email OTP verification, and a modern responsive UI.

---

## Table of Contents

1. [Features](#-features)
2. [Tech Stack](#-tech-stack)
3. [Project Structure](#-project-structure)
4. [Getting Started](#-getting-started)
5. [Environment Variables](#-environment-variables)
6. [Database Models](#-database-models)
7. [API Endpoints](#-api-endpoints)
8. [Frontend & Design](#-frontend--design)
9. [Security](#-security)
10. [Browser Support](#-browser-support)
11. [Contributing](#-contributing)
12. [License](#-license)

---

## ✨ Features

| Area | Highlights |
|---|---|
| **Dual Portal** | Independent dashboards, profiles, and settings for Students and Faculty |
| **Authentication** | Registration, login, OTP-based password reset, JWT tokens |
| **Attendance** | Faculty marks attendance for enrolled students; students view their attendance records and statistics |
| **Subject Management** | Faculty creates subjects; students enroll/drop; automatic enrollment tracking |
| **Assignments** | Faculty publishes assignments; students submit files with grading support |
| **Events & Announcements** | Faculty posts announcements and events; students can register for events |
| **Timetable / Schedule** | Per-department, per-semester schedule with room and class-type info |
| **Email Notifications** | Gmail SMTP for OTP emails, registration alerts, and system notifications |
| **Responsive UI** | Tailwind CSS + glass morphism, Swiper.js carousels, smooth animations |
| **Excel Import** | Bulk student data import via `.xlsx` files |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.8+, Flask 2.3, SQLAlchemy 2.0, Flask-JWT-Extended, Flask-Mail, Flask-Migrate |
| **Database** | SQLite (file: `instance/gec_rajkot.db`) |
| **Frontend** | Jinja2 templates, Tailwind CSS (CDN), Swiper.js, Font Awesome 6.5 |
| **Auth** | Werkzeug password hashing, JWT access/refresh tokens, 6-digit OTP via email |
| **Email** | Gmail SMTP (App Password) |
| **Utilities** | Pillow (images), openpyxl / pandas (Excel parsing), python-dotenv |
| **Production** | Gunicorn, psycopg2 (optional PostgreSQL) |

---

## 📁 Project Structure

```
DE_GECR_WEBSITE/
│
├── app.py                          # Flask application factory & main entry point
├── database.py                     # SQLAlchemy init & table creation
├── requirements.txt                # Python dependencies
├── .env.example                    # Sample environment variables
├── .gitignore
│
├── models/
│   ├── __init__.py
│   └── gecr_models.py              # All SQLAlchemy models (14 tables)
│
├── routes/
│   ├── __init__.py                 # Blueprint exports
│   ├── auth_routes.py              # Register, login, OTP, password reset
│   ├── student_routes.py           # Student dashboard, profile, settings
│   ├── faculty_routes.py           # Faculty dashboard, profile, student mgmt
│   ├── attendance_routes.py        # Attendance marking & records
│   ├── enrollment_routes.py        # Subject enrollment & drop
│   └── subject_routes.py           # Subject CRUD for faculty
│
├── templates/
│   ├── index.html                  # Public landing / homepage
│   ├── _avatar.html                # Reusable avatar partial
│   │
│   ├── auth/
│   │   ├── verify-otp.html         # OTP verification page
│   │   └── login/
│   │       ├── student.html        # Student login
│   │       ├── student-register.html
│   │       ├── student-forgot.html
│   │       ├── faculty.html        # Faculty login
│   │       ├── faculty-register.html
│   │       └── faculty-forgot.html
│   │
│   ├── student/                    # Student portal pages
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   ├── attendance.html
│   │   ├── enroll-subjects.html
│   │   ├── events.html
│   │   ├── schedule.html
│   │   └── settings.html
│   │
│   └── faculty/                    # Faculty portal pages
│       ├── dashboard.html
│       ├── profile.html
│       ├── attendance.html
│       ├── subjects.html
│       ├── manage-subjects.html
│       ├── enrollments.html
│       ├── students_subject_view.html
│       ├── assignments.html
│       ├── manage-announcements.html
│       ├── events.html
│       ├── schedule.html
│       └── settings.html
│
├── static/
│   ├── css/
│   │   ├── styles.css              # Homepage styles
│   │   ├── portal-base.css         # Shared portal styles
│   │   └── animations.css          # Keyframes & transitions
│   ├── js/
│   │   ├── api.js                  # Fetch helpers & API client
│   │   └── validations.js          # Client-side form validation
│   └── images/                     # Logos, campus photos, placeholders
│
├── utils/
│   ├── dashboard_helpers.py        # Dashboard stat aggregation
│   ├── email_notification.py       # Email template rendering
│   ├── send_email.py               # SMTP send logic
│   ├── excel_parser.py             # .xlsx import for subjects/students
│   └── student_parser.py           # Student data parsing helpers
│
├── uploads/                        # User-uploaded files (photos, assignments)
├── logs/                           # Application log files
└── instance/
    └── gec_rajkot.db               # SQLite database (auto-created)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (tested with 3.13)
- **pip** package manager
- A **Gmail account** with an [App Password](https://myaccount.google.com/apppasswords) (for OTP emails)

### Installation

```powershell
# 1. Clone the repository
git clone <repo-url>
cd DE_GECR_WEBSITE

# 2. Create & activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1        # PowerShell
# or: source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
Copy-Item .env.example .env
# Then open .env and fill in your values (see section below)

# 5. Run the application
python app.py
```

The server starts at **http://127.0.0.1:5000**. The SQLite database is created automatically on first run.

### Default Pages

| URL | Description |
|---|---|
| `/` | Public homepage |
| `/login/student` | Student login page |
| `/login/faculty` | Faculty login page |

---

## 🔐 Environment Variables

Copy `.env.example` → `.env` and fill in the values:

```dotenv
# Flask
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database (default SQLite — no change needed for development)
DATABASE_URL=sqlite:///gec_rajkot.db

# Gmail SMTP for OTP emails
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# App mode
FLASK_ENV=development
DEBUG=True
```

> **Gmail setup**: Enable 2-Factor Authentication → generate an App Password at <https://myaccount.google.com/apppasswords> → paste the 16-character code as `MAIL_PASSWORD`.

---

## 🗄️ Database Models

All models live in `models/gecr_models.py`. The database contains the following tables:

| Model | Table | Purpose |
|---|---|---|
| `Student` | `students` | Student info — roll no, name, email, department, semester, DOB, phone, fees |
| `Faculty` | `faculty` | Faculty info — name, email, department, designation, salary, phone |
| `Subject` | `subjects` | Subjects — code, name, dept, semester, credits, assigned faculty |
| `StudentEnrollment` | `student_enrollments` | Many-to-many link between students and subjects |
| `Timetable` | `timetable` | Weekly schedule slots (day, time, room, class type) |
| `Attendance` | `attendance` | Per-student attendance records |
| `Assignment` | `assignments` | Assignments created by faculty for a subject |
| `Submission` | `submissions` | Student assignment submissions with file path & grade |
| `Announcement` | `announcements` | Faculty announcements with expiry |
| `Event` | `events` | Campus events with date, location, category |
| `EventRegistration` | `event_registrations` | Student registrations for events |
| `Activity` | `activities` | Audit log of recent activities |
| `Fee` | `fees` | Student fee records (amount, status, due date) |
| `Salary` | `salary` | Faculty salary records (month, amount, status) |
| `Message` | `messages` | Internal messaging between users |
| `Notification` | `notifications` | Push-style notifications for students/faculty |
| `OTP` | `otps` | Email OTP codes with expiry, purpose, and attempt tracking |

### Key Relationships

```
Faculty ──┬── Subject (one-to-many)
          ├── Assignment (one-to-many)
          ├── Timetable (one-to-many)
          └── Salary (one-to-many)

Student ──┬── StudentEnrollment ── Subject (many-to-many)
          ├── Attendance (one-to-many)
          ├── Submission (one-to-many)
          └── Fee (one-to-many)

Event ── EventRegistration ── Student (many-to-many)
```

---

## 🔗 API Endpoints

The app uses **6 Blueprints** registered in `app.py`:

### Auth (`auth_routes.py`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/student` | Register a new student |
| POST | `/api/auth/register/faculty` | Register a new faculty member |
| POST | `/api/auth/login` | Login (returns JWT token) |
| POST | `/api/auth/forgot-password` | Request OTP for password reset |
| POST | `/api/auth/verify-otp` | Verify OTP code |
| POST | `/api/auth/reset-password` | Reset password after OTP verification |

### Student (`student_routes.py`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/student/dashboard` | Dashboard stats & data |
| GET | `/api/student/profile` | Student profile |
| PUT | `/api/student/profile` | Update profile |
| GET | `/api/student/attendance` | Attendance records |
| GET | `/api/student/schedule` | Timetable |

### Faculty (`faculty_routes.py`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/faculty/dashboard` | Dashboard stats & data |
| GET | `/api/faculty/profile` | Faculty profile |
| PUT | `/api/faculty/profile` | Update profile |
| GET | `/api/faculty/students` | List students |

### Attendance (`attendance_routes.py`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/attendance/faculty/mark` | Mark attendance for students |
| GET | `/api/attendance/student/records` | Get student attendance records |

### Enrollment (`enrollment_routes.py`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/enrollment/enroll` | Enroll student in subject |
| DELETE | `/api/enrollment/drop` | Drop a subject |
| GET | `/api/enrollment/subjects` | List enrolled subjects |

### Subject (`subject_routes.py`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/subjects/create` | Create a new subject |
| GET | `/api/subjects/list` | List subjects |
| PUT | `/api/subjects/<id>` | Update subject |
| DELETE | `/api/subjects/<id>` | Delete subject |

> **Note**: All student/faculty endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.

---

## 🎨 Frontend & Design

### UI Components

- **Tailwind CSS** (CDN) for utility-first styling
- **Glass morphism** cards with backdrop blur and translucency
- **Swiper.js** for placement and gallery carousels
- **Font Awesome 6.5** icons
- **Google Fonts** — Playfair Display (headings) + Inter (body)
- **Custom animations** — floating elements, fade-ins, scroll reveals

### Homepage Sections

1. Hero banner with campus image
2. Stats bar (students, faculty, departments, placements)
3. About the college
4. Campus gallery
5. Departments grid (8 departments)
6. Facilities cards
7. Placement carousel
8. Contact & location info
9. Footer with quick links

### Portal Pages

- **Student**: Dashboard, Profile, Attendance, Enroll Subjects, Events, Schedule, Settings
- **Faculty**: Dashboard, Profile, Attendance, Subjects, Manage Subjects, Enrollments, Assignments, Announcements, Events, Schedule, Settings

### CSS Architecture

| File | Purpose |
|---|---|
| `styles.css` | Homepage-specific styles and layout |
| `portal-base.css` | Shared styles for student & faculty portals (sidebar, cards, tables) |
| `animations.css` | Keyframes, transitions, and motion effects |

### JavaScript

| File | Purpose |
|---|---|
| `api.js` | Centralized fetch wrapper, token management, API calls |
| `validations.js` | Client-side form validation (email, phone, password strength) |

---

## 🔒 Security

- **Password Hashing** — Werkzeug `generate_password_hash` / `check_password_hash`
- **JWT Tokens** — 24-hour access tokens, 30-day refresh tokens via Flask-JWT-Extended
- **OTP Verification** — 6-digit codes with 10-minute expiry and max 3 attempts
- **CORS** — Whitelisted origins only
- **File Upload Limits** — 16 MB max via Flask config
- **Input Validation** — Server-side checks on all form submissions
- **Secure Sessions** — Flask secret key for session signing

---

## 🌐 Browser Support

| Browser | Minimum Version |
|---|---|
| Chrome | 88+ |
| Firefox | 85+ |
| Safari | 14+ |
| Edge | 88+ |
| Mobile (iOS Safari, Chrome) | Latest 2 versions |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch — `git checkout -b feature/your-feature`
3. Commit changes — `git commit -m "Add your feature"`
4. Push — `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

**Built for GEC Rajkot — AI & Data Science Department**
