# GEC Rajkot Backend Server

A comprehensive Flask backend for the Government Engineering College Rajkot student and faculty management system.

## Features

- **Authentication System**
  - Student and Faculty registration
  - JWT-based authentication
  - Password reset with OTP verification
  - Email notifications

- **Student Portal**
  - Profile management
  - Dashboard with academic overview
  - Attendance tracking
  - Assignment submission
  - Grade viewing

- **Faculty Portal**
  - Profile management
  - Student management
  - Attendance marking
  - Assignment creation and grading
  - Dashboard with teaching overview

- **Security**
  - Password hashing with bcrypt
  - JWT tokens with expiration
  - Input validation with Marshmallow
  - CORS configuration
  - Email OTP verification

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MongoDB 4.4 or higher
- Gmail account for email services (or SMTP server)

### Installation

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   
   Copy `.env.example` to `.env` and configure:
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env  # macOS/Linux
   ```

   Update `.env` with your values:
   ```env
   # Database
   MONGODB_URI=mongodb://localhost:27017/gec_rajkot
   
   # JWT Configuration
   JWT_SECRET_KEY=your-super-secret-jwt-key-here
   
   # Email Configuration (Gmail)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   
   # Admin Configuration
   ADMIN_EMAIL=admin@gec.ac.in
   
   # Development
   FLASK_ENV=development
   DEBUG=true
   ```

5. **Start MongoDB**
   
   Make sure MongoDB is running on your system:
   ```bash
   # Windows (if MongoDB is installed as service)
   net start MongoDB
   
   # Manual start
   mongod --dbpath "C:\data\db"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5000`

## API Documentation

### Authentication Endpoints

#### Register Student
```http
POST /api/auth/register/student
Content-Type: application/json

{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@student.gec.ac.in",
    "phone": "9876543210",
    "dob": "2000-01-15",
    "address": "123 Main St, Rajkot",
    "enrollmentNumber": "220001",
    "department": "computer",
    "admissionYear": 2022,
    "currentSemester": 5,
    "rollNumber": "22001",
    "password": "securePassword123"
}
```

#### Register Faculty
```http
POST /api/auth/register/faculty
Content-Type: application/json

{
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane.smith@gec.ac.in",
    "phone": "9876543211",
    "dateOfBirth": "1980-05-20",
    "address": "456 Faculty St, Rajkot",
    "facultyId": "FAC001",
    "department": "Computer Engineering",
    "designation": "Assistant Professor",
    "qualification": "Ph.D. Computer Science",
    "experience": 10,
    "specialization": "Machine Learning",
    "dateOfJoining": "2020-07-01",
    "password": "facultyPassword123"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "email": "john.doe@student.gec.ac.in",
    "password": "securePassword123",
    "userType": "student"
}
```

#### Forgot Password
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
    "email": "john.doe@student.gec.ac.in",
    "userType": "student"
}
```

#### Reset Password
```http
POST /api/auth/reset-password
Content-Type: application/json

{
    "email": "john.doe@student.gec.ac.in",
    "otp": "123456",
    "newPassword": "newSecurePassword123",
    "userType": "student"
}
```

### Student Endpoints

All student endpoints require JWT authentication header:
```http
Authorization: Bearer <jwt_token>
```

#### Get Student Profile
```http
GET /api/student/profile
```

#### Update Student Profile
```http
PUT /api/student/profile
Content-Type: application/json

{
    "phone": "9876543210",
    "address": "Updated address",
    "bloodGroup": "O+",
    "guardianName": "Parent Name",
    "guardianPhone": "9876543211"
}
```

#### Get Dashboard
```http
GET /api/student/dashboard
```

#### Get Subjects
```http
GET /api/student/subjects
```

#### Get Attendance
```http
GET /api/student/attendance?page=1&per_page=10
```

#### Get Assignments
```http
GET /api/student/assignments?status=pending
```

#### Get Grades
```http
GET /api/student/grades?semester=5
```

### Faculty Endpoints

All faculty endpoints require JWT authentication header:
```http
Authorization: Bearer <jwt_token>
```

#### Get Faculty Profile
```http
GET /api/faculty/profile
```

#### Update Faculty Profile
```http
PUT /api/faculty/profile
Content-Type: application/json

{
    "phone": "9876543211",
    "address": "Updated faculty address",
    "qualification": "Ph.D. Computer Science",
    "experience": 12,
    "specialization": "Artificial Intelligence"
}
```

#### Get Dashboard
```http
GET /api/faculty/dashboard
```

#### Get Students
```http
GET /api/faculty/students?subject_id=1&page=1&per_page=20
```

#### Mark Attendance
```http
POST /api/faculty/attendance
Content-Type: application/json

{
    "subject_id": "1",
    "date": "2024-01-10",
    "attendance_data": [
        {"student_id": "1", "status": "present"},
        {"student_id": "2", "status": "absent"}
    ]
}
```

#### Create Assignment
```http
POST /api/faculty/assignments
Content-Type: application/json

{
    "title": "Database Design Project",
    "subject_id": "1",
    "due_date": "2024-01-20",
    "total_marks": 50,
    "description": "Create a comprehensive database design",
    "instructions": "Follow the given requirements"
}
```

## Response Format

All API responses follow this format:

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Response data
    }
}
```

### Error Response
```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        // Validation errors (if any)
    }
}
```

## Database Schema

### Students Collection
```javascript
{
    _id: ObjectId,
    firstName: String,
    lastName: String,
    email: String (unique),
    phone: String,
    dob: Date,
    address: String,
    enrollmentNumber: String (unique),
    department: String,
    admissionYear: Number,
    currentSemester: Number,
    rollNumber: String,
    password: String (hashed),
    isActive: Boolean,
    createdAt: Date,
    updatedAt: Date
}
```

### Faculty Collection
```javascript
{
    _id: ObjectId,
    firstName: String,
    lastName: String,
    email: String (unique),
    phone: String,
    dateOfBirth: Date,
    address: String,
    facultyId: String (unique),
    department: String,
    designation: String,
    qualification: String,
    experience: Number,
    specialization: String,
    dateOfJoining: Date,
    password: String (hashed),
    isActive: Boolean,
    isApproved: Boolean,
    createdAt: Date,
    updatedAt: Date
}
```

### OTPs Collection
```javascript
{
    _id: ObjectId,
    email: String,
    otp: String,
    userType: String,
    purpose: String,
    expiresAt: Date,
    isUsed: Boolean,
    createdAt: Date
}
```

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development  # macOS/Linux
set FLASK_ENV=development     # Windows

python app.py
```

### Testing the API

You can test the API using tools like:
- Postman
- cURL
- VS Code REST Client
- Frontend application

### Email Configuration

For Gmail, you need to:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in `MAIL_PASSWORD`

For other email providers, update the SMTP settings accordingly.

## Production Deployment

### Environment Variables
Set all environment variables securely in production:
- Use strong JWT secret keys
- Configure proper MongoDB connection
- Set up production email service
- Disable debug mode

### Security Considerations
- Use HTTPS in production
- Configure proper CORS origins
- Set up rate limiting
- Use environment-specific configurations
- Regular security updates

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check connection string in `.env`

2. **Email Not Sending**
   - Verify email credentials
   - Check SMTP settings
   - Ensure less secure app access (Gmail)

3. **Import Errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Activate virtual environment

4. **JWT Token Issues**
   - Check JWT secret key configuration
   - Verify token expiration settings

### Logs

The application logs important events. Check console output for debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper testing
4. Submit a pull request

## License

This project is developed for Government Engineering College, Rajkot.

## Support

For technical support, contact the development team or submit an issue in the project repository.