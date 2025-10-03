# GEC Rajkot Flask Backend

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB installed and running
- Virtual environment (recommended)

### Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory:
```env
MONGODB_URI=mongodb://localhost:27017/gec_rajkot
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_USE_TLS=True
```

4. Run the application:
```bash
python app.py
```

## API Endpoints

### Authentication
- `POST /api/auth/student/login` - Student login
- `POST /api/auth/faculty/login` - Faculty login
- `POST /api/auth/student/register` - Student registration
- `POST /api/auth/faculty/register` - Faculty registration
- `POST /api/auth/forgot-password` - Send OTP for password reset
- `POST /api/auth/verify-otp` - Verify OTP
- `POST /api/auth/reset-password` - Reset password

### Student APIs
- `GET /api/student/profile` - Get student profile
- `PUT /api/student/profile` - Update student profile
- `GET /api/student/dashboard` - Get dashboard data

### Faculty APIs
- `GET /api/faculty/profile` - Get faculty profile
- `PUT /api/faculty/profile` - Update faculty profile
- `GET /api/faculty/dashboard` - Get dashboard data

## Database Schema

### Students Collection
```json
{
  "_id": "ObjectId",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "phone": "string",
  "enrollmentNumber": "string",
  "department": "string",
  "admissionYear": "number",
  "currentSemester": "number",
  "rollNumber": "string",
  "address": "string",
  "password": "hashed_string",
  "isActive": "boolean",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### Faculty Collection
```json
{
  "_id": "ObjectId",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "phone": "string",
  "facultyId": "string",
  "department": "string",
  "designation": "string",
  "qualification": "string",
  "experience": "number",
  "specialization": "string",
  "address": "string",
  "password": "hashed_string",
  "isActive": "boolean",
  "isApproved": "boolean",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### OTP Collection
```json
{
  "_id": "ObjectId",
  "email": "string",
  "otp": "string",
  "userType": "student|faculty",
  "purpose": "password_reset",
  "expiresAt": "datetime",
  "isUsed": "boolean",
  "createdAt": "datetime"
}
```