# 🔔 Notification System Implementation Guide

## Overview
The GEC Rajkot portal now has a fully functional notification system that automatically alerts students when faculty members post announcements, events, or other activities.

---

## ✅ Features Implemented

### 1. Database Model
**Location:** `models/gecr_models.py`

```python
class Notification(db.Model):
    notification_id = Integer (Primary Key, Auto-increment)
    user_id = Integer (Foreign Key to Student/Faculty ID)
    user_type = String ('student' or 'faculty')
    title = String (Notification title, max 200 chars)
    message = Text (Notification body/content)
    notification_type = String ('announcement', 'event', 'attendance', 'assignment', 'general')
    link = String (Optional URL to related content)
    read = Boolean (Default: False)
    created_at = DateTime (Auto-set on creation)
```

### 2. Auto-Creation on Faculty Actions
**Location:** `routes/faculty_routes.py`

#### Helper Function:
```python
create_notifications_for_students(title, message, notification_type, link=None)
```
- Fetches all students from database
- Creates notification object for each student
- Uses `bulk_save_objects()` for efficient database insertion
- Returns count of notifications created

#### Integration Points:
- **Announcements**: When faculty posts announcement → Creates notification for all students
  - Title: "📢 New Announcement: {announcement_title}"
  - Message: First 200 characters of announcement
  - Type: 'announcement'
  - Link: '/student/dashboard'

- **Events**: When faculty creates event → Creates notification for all students
  - Title: "📅 New Event: {event_title}"
  - Message: Event description + formatted date/time + location
  - Type: 'event'
  - Link: '/student/events'

### 3. Student API Endpoints
**Location:** `routes/student_routes.py`

#### GET `/api/student/notifications`
**Query Parameters:**
- `unread_only` (optional, boolean) - Filter to show only unread notifications
- `limit` (optional, integer, default=20) - Limit number of results

**Response:**
```json
{
  "notifications": [
    {
      "notification_id": 1,
      "title": "📢 New Announcement: Mid-term Exam Schedule",
      "message": "Mid-term exams will be conducted from...",
      "notification_type": "announcement",
      "link": "/student/dashboard",
      "read": false,
      "created_at": "2025-01-15T10:30:00"
    }
  ],
  "unread_count": 5
}
```

#### POST `/api/student/notifications/<id>/mark-read`
Marks a single notification as read.

**Response:**
```json
{
  "message": "Notification marked as read"
}
```

#### POST `/api/student/notifications/mark-all-read`
Marks all notifications for the current student as read.

**Response:**
```json
{
  "message": "All notifications marked as read",
  "count": 12
}
```

### 4. Student Dashboard UI
**Location:** `templates/student/dashboard.html`

#### Visual Components:
1. **Notification Bell Icon** (Top right of page)
   - Bell icon (🔔) with hover effect
   - Badge showing unread count (hidden when 0)
   - Click to toggle dropdown

2. **Notification Dropdown**
   - Width: 320px
   - Max height: 384px (scrollable)
   - Shows up to 20 most recent notifications
   - Each notification displays:
     - Icon (based on type: 📢 📅 ✓ 📝 📌)
     - Title (bold)
     - Message (truncated if too long)
     - Relative timestamp ("2 hours ago")
   - Visual distinction:
     - Unread: Blue background (bg-blue-50)
     - Read: Gray text, semi-transparent (opacity-60)

3. **Mark All Read Button**
   - Located at bottom of dropdown
   - Gray button with hover effect
   - Marks all notifications as read

#### JavaScript Functions:

**`loadNotifications()`**
- Fetches notifications from `/api/student/notifications`
- Updates badge with unread count
- Renders notification items in dropdown
- Applies click handlers for individual notifications

**`markNotificationRead(notificationId)`**
- Sends POST to `/api/student/notifications/<id>/mark-read`
- Updates UI to reflect read status
- Decrements unread count badge

**`markAllNotificationsRead()`**
- Sends POST to `/api/student/notifications/mark-all-read`
- Reloads notifications
- Updates badge to 0

**`getTimeAgo(dateString)`**
- Converts ISO timestamp to relative time
- Examples: "Just now", "5 minutes ago", "3 hours ago", "2 days ago"

**Polling Mechanism:**
- Auto-refreshes notifications every 30 seconds
- Uses `setInterval(loadNotifications, 30000)`
- Ensures students see new notifications without manual refresh

#### Event Handlers:
- **Bell click**: Toggles dropdown visibility
- **Outside click**: Closes dropdown if open
- **Notification click**: Marks as read and navigates to link (if provided)
- **Mark all button**: Marks all as read

---

## 🚀 How It Works (End-to-End Flow)

### Faculty Posts Announcement:
1. Faculty opens "Manage Announcements" page
2. Fills form (title, message, expiry date)
3. Clicks "Create Announcement"
4. **Backend**:
   - Saves announcement to database
   - Calls `create_notifications_for_students()`
   - Creates notification for each registered student
   - Returns success response
5. Announcement appears in faculty's list

### Student Receives Notification:
1. Student dashboard loads
2. **JavaScript calls** `loadNotifications()` on page load
3. **Backend** returns notifications + unread count
4. **UI updates**:
   - Badge shows number like "3"
   - Dropdown populated with notification items
5. **Polling**: Every 30 seconds, `loadNotifications()` runs again
   - If new notifications exist, badge updates
   - New items appear in dropdown

### Student Reads Notification:
1. Student clicks bell icon → Dropdown opens
2. Student sees list of notifications (unread highlighted in blue)
3. Student clicks a notification
4. **Backend** marks notification as read
5. **UI updates**:
   - Notification text grays out
   - Badge decrements (e.g., "3" → "2")
6. If link exists, browser navigates to that page

### Student Marks All as Read:
1. Student clicks "Mark all as read" button
2. **Backend** updates all student's notifications to read=True
3. **UI updates**:
   - All notifications gray out
   - Badge disappears (count = 0)

---

## 🧪 Testing

### Manual Testing Steps:

1. **Start Server**:
   ```bash
   python app.py
   ```

2. **Create Test Data** (if needed):
   ```bash
   python create_sample_data.py
   ```

3. **Test Faculty Flow**:
   - Open browser: http://127.0.0.1:5000
   - Login as faculty
   - Navigate to "Manage Announcements"
   - Create new announcement
   - Check server logs for "Created N notifications for announcement"

4. **Test Student Flow**:
   - Open incognito/private window
   - Login as student
   - Check notification bell badge (should show count)
   - Click bell to open dropdown
   - Verify notifications are listed
   - Click a notification to mark as read
   - Verify badge count decreases

5. **Test Polling**:
   - Keep student dashboard open
   - In another window, login as faculty and create announcement
   - Wait 30 seconds
   - Student dashboard badge should update automatically

### Automated Tests:

Run the test scripts:
```bash
# Test notification model
python test_create_notification.py

# Test bulk creation
python test_bulk_notifications.py

# Test end-to-end flow (requires server running)
python test_notification_flow.py
```

---

## 📊 Database Verification

Check notifications in database:
```bash
python -c "from app import create_app; from models.gecr_models import Notification; app = create_app('development'); app.app_context().push(); notifs = Notification.query.all(); print(f'Total notifications: {len(notifs)}'); [print(f'  {n.notification_id}: {n.title} (Read: {n.read})') for n in notifs]"
```

---

## 🔧 Configuration

### Notification Types:
- `announcement` - Faculty posts announcement
- `event` - Faculty creates event
- `attendance` - Attendance marked
- `assignment` - New assignment posted
- `general` - General notifications

### Polling Interval:
Current: 30 seconds (30000 ms)

To change, edit in `templates/student/dashboard.html`:
```javascript
setInterval(loadNotifications, 30000); // Change 30000 to desired milliseconds
```

### Notification Icons:
Edit in `templates/student/dashboard.html` `loadNotifications()` function:
```javascript
const icons = {
    'announcement': '📢',
    'event': '📅',
    'attendance': '✓',
    'assignment': '📝',
    'general': '📌'
};
```

---

## 📝 Future Enhancements

### Planned Features:
1. **Browser Push Notifications**
   - Web Push API integration
   - Service Workers for background notifications
   - User opt-in/opt-out preferences

2. **Email Notifications**
   - Send email for critical notifications
   - Daily digest option
   - Email preferences in settings

3. **Notification Filtering**
   - Filter by type in dropdown
   - Search notifications
   - Date range filters

4. **Priority Levels**
   - Urgent/High/Normal/Low priority
   - Color-coded badges
   - Sound alerts for urgent notifications

5. **Notification History**
   - Dedicated notifications page
   - Pagination for old notifications
   - Archive functionality

6. **Faculty Notifications**
   - Student submissions
   - Assignment deadlines
   - System alerts

---

## 🐛 Troubleshooting

### Notifications not appearing for students:
1. Check if students exist in database
2. Verify notification creation logs in terminal
3. Check browser console for JavaScript errors
4. Verify student is logged in (check session)

### Badge not updating:
1. Check browser console for API errors
2. Verify polling is running (`setInterval` active)
3. Check network tab - should see `/api/student/notifications` every 30s
4. Clear browser cache and refresh

### "Mark as read" not working:
1. Check student is logged in
2. Verify notification belongs to current student (user_id match)
3. Check server logs for 403 Forbidden errors
4. Verify session authentication is working

### Duplicate notifications:
1. Check if `create_notifications_for_students()` called multiple times
2. Verify `db.session.commit()` not called in loop
3. Use `bulk_save_objects()` instead of individual `add()` calls

---

## 📚 Code References

### Key Files:
- **Model**: `models/gecr_models.py` - Notification class (lines 180-220)
- **Database**: `database.py` - Model registration (lines 25, 58, 92)
- **Faculty Routes**: `routes/faculty_routes.py` 
  - Helper function (lines 18-52)
  - Announcement endpoint (lines 554-580)
  - Event endpoint (lines 600-650)
- **Student Routes**: `routes/student_routes.py`
  - GET notifications (lines 200-230)
  - Mark as read (lines 235-260)
  - Mark all as read (lines 265-285)
- **Student UI**: `templates/student/dashboard.html`
  - HTML structure (lines 50-120)
  - JavaScript (lines 250-400)

### Dependencies:
- Flask (session management, routing)
- SQLAlchemy (ORM, database operations)
- JavaScript Fetch API (AJAX requests)
- Tailwind CSS (UI styling)

---

## ✅ Checklist

**Implementation Complete:**
- [x] Notification database model
- [x] Auto-creation on faculty actions
- [x] Student API endpoints (GET, POST mark-read, POST mark-all-read)
- [x] UI notification bell with badge
- [x] Dropdown with notification list
- [x] Mark as read functionality (individual + bulk)
- [x] Real-time polling (30-second intervals)
- [x] Relative timestamps
- [x] Visual distinction (unread/read)
- [x] Icons based on notification type
- [x] Documentation

**Ready for Production:**
- [x] Code tested and working
- [x] No syntax errors
- [x] Database schema finalized
- [x] API endpoints documented
- [x] UI components responsive
- [x] Error handling in place

**Next Steps:**
- [ ] Add browser push notifications
- [ ] Implement email alerts
- [ ] Create notification preferences page
- [ ] Add notification filtering
- [ ] Build notification history page

---

*Last Updated: January 2025*
*Version: 1.0.0*
*Status: ✅ Complete and Ready for Use*
