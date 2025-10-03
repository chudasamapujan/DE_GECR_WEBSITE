# Frontend Integration Guide

## Connecting Frontend to Backend API

Your existing frontend forms are ready to integrate with the Flask backend. Here's how to connect them:

### 1. Update Base URL

Add this to your `js/main.js`:

```javascript
// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api',
    HEADERS: {
        'Content-Type': 'application/json'
    }
};

// Get auth token from localStorage
const getAuthToken = () => localStorage.getItem('authToken');

// Add auth header if token exists
const getAuthHeaders = () => {
    const token = getAuthToken();
    return token ? {
        ...API_CONFIG.HEADERS,
        'Authorization': `Bearer ${token}`
    } : API_CONFIG.HEADERS;
};
```

### 2. Update Login Forms

Replace the existing login form handlers:

#### Student Login (`login/student.html`)
```javascript
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const loginData = {
        email: formData.get('email'),
        password: formData.get('password'),
        userType: 'student'
    };
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/auth/login`, {
            method: 'POST',
            headers: API_CONFIG.HEADERS,
            body: JSON.stringify(loginData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Store token and redirect
            localStorage.setItem('authToken', result.data.access_token);
            localStorage.setItem('userType', result.data.user_type);
            localStorage.setItem('userId', result.data.user_id);
            
            ToastManager.show('Login successful!', 'success');
            setTimeout(() => {
                window.location.href = '../student-profile.html';
            }, 1500);
        } else {
            ToastManager.show(result.message, 'error');
        }
    } catch (error) {
        ToastManager.show('Login failed. Please try again.', 'error');
        console.error('Login error:', error);
    }
});
```

#### Faculty Login (`login/faculty.html`)
```javascript
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const loginData = {
        email: formData.get('email'),
        password: formData.get('password'),
        userType: 'faculty'
    };
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/auth/login`, {
            method: 'POST',
            headers: API_CONFIG.HEADERS,
            body: JSON.stringify(loginData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            localStorage.setItem('authToken', result.data.access_token);
            localStorage.setItem('userType', result.data.user_type);
            localStorage.setItem('userId', result.data.user_id);
            
            ToastManager.show('Login successful!', 'success');
            setTimeout(() => {
                window.location.href = '../dashboard.html';
            }, 1500);
        } else {
            ToastManager.show(result.message, 'error');
        }
    } catch (error) {
        ToastManager.show('Login failed. Please try again.', 'error');
        console.error('Login error:', error);
    }
});
```

### 3. Update Registration Forms

#### Student Registration (`login/student-register.html`)
```javascript
document.getElementById('registrationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const registrationData = {
        firstName: formData.get('firstName'),
        lastName: formData.get('lastName'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        dob: formData.get('dob'),
        address: formData.get('address'),
        enrollmentNumber: formData.get('enrollmentNumber'),
        department: formData.get('department'),
        admissionYear: parseInt(formData.get('admissionYear')),
        currentSemester: parseInt(formData.get('currentSemester')),
        rollNumber: formData.get('rollNumber'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/auth/register/student`, {
            method: 'POST',
            headers: API_CONFIG.HEADERS,
            body: JSON.stringify(registrationData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            localStorage.setItem('authToken', result.data.access_token);
            localStorage.setItem('userType', result.data.user_type);
            localStorage.setItem('userId', result.data.user_id);
            
            ToastManager.show('Registration successful!', 'success');
            setTimeout(() => {
                window.location.href = '../student-profile.html';
            }, 1500);
        } else {
            ToastManager.show(result.message, 'error');
        }
    } catch (error) {
        ToastManager.show('Registration failed. Please try again.', 'error');
        console.error('Registration error:', error);
    }
});
```

#### Faculty Registration (`login/faculty-register.html`)
```javascript
document.getElementById('registrationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const registrationData = {
        firstName: formData.get('firstName'),
        lastName: formData.get('lastName'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        dateOfBirth: formData.get('dateOfBirth'),
        address: formData.get('address'),
        facultyId: formData.get('facultyId'),
        department: formData.get('department'),
        designation: formData.get('designation'),
        qualification: formData.get('qualification'),
        experience: parseInt(formData.get('experience')),
        specialization: formData.get('specialization'),
        dateOfJoining: formData.get('dateOfJoining'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/auth/register/faculty`, {
            method: 'POST',
            headers: API_CONFIG.HEADERS,
            body: JSON.stringify(registrationData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            ToastManager.show('Registration submitted for approval!', 'success');
            setTimeout(() => {
                window.location.href = '../login/faculty.html';
            }, 2000);
        } else {
            ToastManager.show(result.message, 'error');
        }
    } catch (error) {
        ToastManager.show('Registration failed. Please try again.', 'error');
        console.error('Registration error:', error);
    }
});
```

### 4. Update Forgot Password Forms

#### Student Forgot Password (`login/student-forgot.html`)
```javascript
// Send OTP
document.getElementById('forgotPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/auth/forgot-password`, {
            method: 'POST',
            headers: API_CONFIG.HEADERS,
            body: JSON.stringify({
                email: email,
                userType: 'student'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            ToastManager.show('OTP sent to your email!', 'success');
            // Show OTP verification step
            showOtpStep();
        } else {
            ToastManager.show(result.message, 'error');
        }
    } catch (error) {
        ToastManager.show('Failed to send OTP. Please try again.', 'error');
        console.error('Forgot password error:', error);
    }
});

// Reset Password
document.getElementById('resetPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const resetData = {
        email: formData.get('email'),
        otp: formData.get('otp'),
        newPassword: formData.get('newPassword'),
        userType: 'student'
    };
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/auth/reset-password`, {
            method: 'POST',
            headers: API_CONFIG.HEADERS,
            body: JSON.stringify(resetData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            ToastManager.show('Password reset successful!', 'success');
            setTimeout(() => {
                window.location.href = 'student.html';
            }, 1500);
        } else {
            ToastManager.show(result.message, 'error');
        }
    } catch (error) {
        ToastManager.show('Password reset failed. Please try again.', 'error');
        console.error('Reset password error:', error);
    }
});
```

### 5. Add Authentication Check

Add this to the beginning of protected pages (dashboard, profile pages):

```javascript
// Check authentication on page load
document.addEventListener('DOMContentLoaded', async () => {
    const token = getAuthToken();
    
    if (!token) {
        window.location.href = 'login/index.html';
        return;
    }
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/auth/verify-token`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (!result.success) {
            localStorage.clear();
            window.location.href = 'login/index.html';
            return;
        }
        
        // Load user data
        loadUserData(result.data.user);
        
    } catch (error) {
        console.error('Auth check error:', error);
        localStorage.clear();
        window.location.href = 'login/index.html';
    }
});
```

### 6. Dashboard Data Loading

#### Student Dashboard (`student-profile.html`)
```javascript
async function loadStudentDashboard() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/student/dashboard`, {
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            
            // Update welcome message
            document.getElementById('welcomeMessage').textContent = data.welcome_message;
            
            // Update student info
            const studentInfo = data.student_info;
            document.getElementById('studentName').textContent = studentInfo.name;
            document.getElementById('enrollmentNumber').textContent = studentInfo.enrollmentNumber;
            document.getElementById('branch').textContent = studentInfo.branch;
            document.getElementById('semester').textContent = studentInfo.semester;
            
            // Update stats
            const stats = data.quick_stats;
            document.getElementById('totalSubjects').textContent = stats.total_subjects;
            document.getElementById('attendancePercentage').textContent = `${stats.attendance_percentage}%`;
            document.getElementById('pendingAssignments').textContent = stats.pending_assignments;
            document.getElementById('upcomingExams').textContent = stats.upcoming_exams;
            
            // Load recent activities
            loadRecentActivities(data.recent_activities);
            
            // Load announcements
            loadAnnouncements(data.announcements);
        }
    } catch (error) {
        console.error('Dashboard loading error:', error);
        ToastManager.show('Failed to load dashboard data', 'error');
    }
}
```

#### Faculty Dashboard (`dashboard.html`)
```javascript
async function loadFacultyDashboard() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/faculty/dashboard`, {
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            
            // Update welcome message
            document.getElementById('welcomeMessage').textContent = data.welcome_message;
            
            // Update faculty info
            const facultyInfo = data.faculty_info;
            document.getElementById('facultyName').textContent = facultyInfo.name;
            document.getElementById('facultyId').textContent = facultyInfo.facultyId;
            document.getElementById('department').textContent = facultyInfo.department;
            document.getElementById('designation').textContent = facultyInfo.designation;
            
            // Update stats
            const stats = data.quick_stats;
            document.getElementById('totalSubjects').textContent = stats.total_subjects;
            document.getElementById('totalStudents').textContent = stats.total_students;
            document.getElementById('pendingAssignments').textContent = stats.pending_assignments;
            document.getElementById('upcomingClasses').textContent = stats.upcoming_classes;
            
            // Load today's schedule
            loadTodaySchedule(data.today_schedule);
        }
    } catch (error) {
        console.error('Dashboard loading error:', error);
        ToastManager.show('Failed to load dashboard data', 'error');
    }
}
```

### 7. Logout Functionality

Add this to all authenticated pages:

```javascript
document.getElementById('logoutBtn').addEventListener('click', async () => {
    try {
        await fetch(`${API_CONFIG.BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.clear();
        window.location.href = 'login/index.html';
    }
});
```

### 8. Error Handling

Add global error handling:

```javascript
// Global error handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    
    if (event.reason?.status === 401) {
        localStorage.clear();
        window.location.href = 'login/index.html';
    }
});
```

### 9. Starting the Backend

Before testing the frontend integration:

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`

4. Start MongoDB

5. Run the Flask server:
   ```bash
   python app.py
   ```

The backend will be available at `http://localhost:5000`

### 10. Testing Integration

1. Start the backend server
2. Open your frontend in a browser
3. Try the registration flow
4. Test login functionality
5. Check dashboard data loading
6. Test logout functionality

Your frontend is now fully integrated with the Flask backend! All form validations will be handled by the server, and data will be stored in MongoDB.