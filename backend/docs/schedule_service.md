# Enhanced Schedule Service Documentation

## Overview

The Enhanced Schedule Service is a comprehensive, modular reminder system designed for visa applications and appointments. It follows the same architectural patterns as the document service, providing reliable email notifications for various visa-related deadlines.

## Features

### 🚀 Core Functionality
- **Multiple Reminder Types**: Visa appointments, visa expiry, document deadlines, consultations, etc.
- **Intelligent Scheduling**: Automatic multiple reminders based on type (e.g., 30 days, 7 days, 1 day before)
- **Email Notifications**: HTML and plain text emails with customizable templates
- **Priority System**: Low, medium, high, urgent priority levels
- **Status Tracking**: Active, sent, completed, cancelled statuses

### 🏗️ Architecture
- **Modular Design**: Self-contained service with clear interfaces
- **Exception Handling**: Custom exceptions with appropriate HTTP status codes
- **Logging**: Comprehensive logging for debugging and monitoring
- **Database Optimization**: Indexed queries and efficient data retrieval

## API Endpoints

### Create Reminder
```http
POST /api/reminders/create/
Authorization: Token <your-token>
Content-Type: application/json

{
  "title": "UK Visa Appointment at Embassy",
  "description": "Bring all required documents including passport, photos, and supporting papers.",
  "reminder_type": "visa_appointment",
  "target_date": "2024-02-15T10:00:00Z",
  "priority": "high",
  "notes": "Appointment confirmation: ABC123",
  "custom_intervals": [7, 1]  // Optional: custom reminder intervals in days
}
```

**Response:**
```json
{
  "success": true,
  "reminders_created": 2,
  "reminder_details": [
    {
      "id": 1,
      "reminder_date": "2024-02-08T10:00:00Z",
      "days_before": 7
    },
    {
      "id": 2,
      "reminder_date": "2024-02-14T10:00:00Z",
      "days_before": 1
    }
  ],
  "target_date": "2024-02-15T10:00:00Z",
  "type": "visa_appointment"
}
```

### Get User Reminders
```http
GET /api/reminders/list/?status=active&limit=50
Authorization: Token <your-token>
```

**Response:**
```json
{
  "reminders": [
    {
      "id": 1,
      "title": "UK Visa Appointment at Embassy",
      "description": "Bring all required documents...",
      "reminder_type": "visa_appointment",
      "target_date": "2024-02-15T10:00:00Z",
      "reminder_date": "2024-02-08T10:00:00Z",
      "status": "active",
      "priority": "high",
      "email_sent": false,
      "created_at": "2024-02-01T12:00:00Z"
    }
  ],
  "count": 1
}
```

### Update Reminder Status
```http
PUT /api/reminders/{id}/status/
Authorization: Token <your-token>
Content-Type: application/json

{
  "status": "completed"
}
```

### Process Due Reminders (Admin/Testing)
```http
POST /api/process-reminders/
Authorization: Token <your-token>
```

## Reminder Types

| Type | Default Intervals | Use Case |
|------|------------------|----------|
| `visa_appointment` | 7, 1 days | Embassy/consulate appointments |
| `visa_expiry` | 30, 7, 1 days | Visa expiration warnings |
| `document_deadline` | 7, 3, 1 days | Document submission deadlines |
| `consultation` | 3, 1 days | Legal consultations |
| `document_review` | 2, 1 days | Document review appointments |
| `application_submission` | 7, 3, 1 days | Application deadlines |
| `interview_prep` | 7, 1 days | Interview preparation |

## Email Templates

The service generates both HTML and plain text emails:

### Subject Templates
- **Visa Appointment**: "Reminder: {title} - Visa Appointment"
- **Visa Expiry**: "⚠️ Important: {title} - Visa Expiry Alert"
- **Document Deadline**: "Action Required: {title} - Document Deadline"

### Email Content
- Professional HTML templates with responsive design
- Priority-based color coding
- Clear call-to-action messaging
- Branding consistent with Mandry AI

## Database Schema

### Reminder Model
```python
class Reminder(models.Model):
    user = ForeignKey(User)
    title = CharField(max_length=200)
    description = TextField()
    reminder_type = CharField(choices=REMINDER_TYPES)
    target_date = DateTimeField()
    reminder_date = DateTimeField()
    status = CharField(choices=STATUS_CHOICES)
    priority = CharField(choices=PRIORITY_CHOICES)
    email_sent = BooleanField(default=False)
    email_sent_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    notes = TextField()
```

## Setup Instructions

### 1. Database Migration
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 2. Email Configuration

#### Development (Console Backend)
Emails will be displayed in the console - no additional setup required.

#### Production (SMTP)
Set environment variables:
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@mandry.ai
```

### 3. Background Task Setup

#### Option A: Cron Job (Recommended)
Add to your crontab:
```bash
# Process reminders every 5 minutes
*/5 * * * * cd /path/to/your/project && python manage.py process_reminders

# Or every hour
0 * * * * cd /path/to/your/project && python manage.py process_reminders
```

#### Option B: Manual Processing
```bash
# Dry run to see what would be processed
python manage.py process_reminders --dry-run

# Actually process and send emails
python manage.py process_reminders

# Limit processing to 50 reminders
python manage.py process_reminders --limit 50
```

## Usage Examples

### Create a Visa Expiry Reminder
```python
from services.schedule_service import default_schedule_service

reminder_data = {
    'title': 'UK Student Visa Expires',
    'description': 'Your Tier 4 student visa expires soon. Apply for extension if needed.',
    'reminder_type': 'visa_expiry',
    'target_date': datetime(2024, 6, 30, 23, 59),
    'priority': 'urgent',
    'notes': 'Visa number: ABC123456789'
}

result = default_schedule_service.create_reminder(user, reminder_data)
```

### Get User's Active Reminders
```python
active_reminders = default_schedule_service.get_user_reminders(
    user=request.user,
    status='active',
    limit=20
)
```

### Mark Reminder as Completed
```python
success = default_schedule_service.update_reminder_status(
    reminder_id=123,
    status='completed',
    user=request.user
)
```

## Testing

### Run the Test Suite
```bash
cd backend/services
python test_schedule_service.py
```

### Test API Endpoints
Use tools like Postman, curl, or httpie to test the endpoints:

```bash
# Create a reminder
curl -X POST http://localhost:8000/api/reminders/create/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Appointment",
    "reminder_type": "consultation",
    "target_date": "2024-02-15T10:00:00Z",
    "priority": "medium"
  }'
```

## Monitoring and Troubleshooting

### Check Email Configuration
```python
from services.schedule_service import default_schedule_service
print(f"Email enabled: {default_schedule_service.email_enabled}")
```

### View Due Reminders
```python
due_reminders = default_schedule_service.get_due_reminders(limit=10)
for reminder in due_reminders:
    print(f"{reminder['title']} - {reminder['user_email']}")
```

### Process Reminders Manually
```python
result = default_schedule_service.process_due_reminders()
print(f"Processed: {result['processed']}, Sent: {result['sent']}, Failed: {result['failed']}")
```

## Error Handling

The service uses custom exceptions:

```python
from services.schedule_service import ScheduleServiceException

try:
    result = default_schedule_service.create_reminder(user, invalid_data)
except ScheduleServiceException as e:
    print(f"Schedule service error: {e}")
    # e.status_code contains the HTTP status code
```

## Integration with Frontend

### React Example
```javascript
// Create reminder
const createReminder = async (reminderData) => {
  const response = await fetch('/api/reminders/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${userToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(reminderData)
  });
  
  if (response.ok) {
    const result = await response.json();
    console.log(`Created ${result.reminders_created} reminders`);
  }
};

// Get user reminders
const getUserReminders = async () => {
  const response = await fetch('/api/reminders/list/', {
    headers: {
      'Authorization': `Token ${userToken}`,
    }
  });
  
  if (response.ok) {
    const data = await response.json();
    return data.reminders;
  }
};
```

## Security Considerations

1. **Authentication Required**: All endpoints require token authentication
2. **User Isolation**: Users can only access their own reminders
3. **Input Validation**: All inputs are validated through serializers
4. **Rate Limiting**: Consider implementing rate limiting for production
5. **Email Security**: Use app passwords for Gmail SMTP

## Performance Optimization

1. **Database Indexes**: Key fields are indexed for fast queries
2. **Query Optimization**: Select_related used to minimize database hits
3. **Batch Processing**: Process multiple reminders efficiently
4. **Email Throttling**: Built-in limits prevent spam

## Migration from Legacy System

The old `schedule_appointment` endpoint is maintained for backward compatibility:
- Automatically creates both old Appointment and new Reminder records
- Includes deprecation notices in responses
- Gradual migration path for existing clients

## Future Enhancements

- SMS notifications via Twilio integration
- Push notifications for mobile apps
- Calendar integration (Google Calendar, Outlook)
- Advanced scheduling (business days only, timezone support)
- Reminder templates for common scenarios
- Analytics and reporting dashboard 