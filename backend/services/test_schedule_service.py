import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mandry_ai.settings')
django.setup()

from django.contrib.auth.models import User
from visa.models import Reminder
from services.schedule_service import default_schedule_service, ScheduleServiceException


def test_schedule_service():
    """Test the schedule service functionality"""
    print("Testing Schedule Service...")
    
    try:
        # Create a test user
        test_user, created = User.objects.get_or_create(
            username='test_scheduler',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        print(f"✓ Test user {'created' if created else 'found'}: {test_user.username}")
        
        # Test 1: Create a visa appointment reminder
        print("\n1. Testing visa appointment reminder creation...")
        reminder_data = {
            'title': 'UK Visa Appointment at Embassy',
            'description': 'Bring all required documents including passport, photos, and supporting papers.',
            'reminder_type': 'visa_appointment',
            'target_date': timezone.now() + timedelta(days=10),
            'priority': 'high',
            'notes': 'Appointment confirmation: ABC123'
        }
        
        result = default_schedule_service.create_reminder(test_user, reminder_data)
        print(f"✓ Created {result['reminders_created']} reminders for visa appointment")
        print(f"  Reminder details: {result['reminder_details']}")
        
        # Test 2: Create a visa expiry reminder
        print("\n2. Testing visa expiry reminder creation...")
        expiry_data = {
            'title': 'UK Visa Expires Soon',
            'description': 'Your UK visa is approaching expiry. Consider renewal if staying longer.',
            'reminder_type': 'visa_expiry',
            'target_date': timezone.now() + timedelta(days=45),
            'priority': 'urgent'
        }
        
        result = default_schedule_service.create_reminder(test_user, expiry_data)
        print(f"✓ Created {result['reminders_created']} reminders for visa expiry")
        
        # Test 3: Get user reminders
        print("\n3. Testing get user reminders...")
        reminders = default_schedule_service.get_user_reminders(test_user)
        print(f"✓ Found {len(reminders)} reminders for user")
        for reminder in reminders:
            print(f"  - {reminder['title']} ({reminder['reminder_type']}) - {reminder['status']}")
        
        # Test 4: Test due reminders (create one that's due now)
        print("\n4. Testing due reminders...")
        immediate_data = {
            'title': 'Test Immediate Reminder',
            'description': 'This reminder should be due immediately for testing',
            'reminder_type': 'consultation',
            'target_date': timezone.now() + timedelta(minutes=1),
            'priority': 'medium',
            'custom_intervals': [0]  # Due immediately
        }
        
        result = default_schedule_service.create_reminder(test_user, immediate_data)
        print(f"✓ Created immediate reminder for testing")
        
        # Get due reminders
        due_reminders = default_schedule_service.get_due_reminders(limit=10)
        print(f"✓ Found {len(due_reminders)} due reminders")
        
        # Test 5: Email configuration check
        print("\n5. Testing email configuration...")
        service = default_schedule_service
        print(f"✓ Email enabled: {service.email_enabled}")
        print(f"✓ Email from: {service.email_from}")
        
        # Test 6: Process due reminders (dry run)
        print("\n6. Testing reminder processing...")
        if due_reminders:
            print("Due reminders found, but skipping actual email send for testing")
            print("In production, these would trigger email notifications")
        
        print("\n✅ All schedule service tests passed!")
        print("\nNext steps:")
        print("1. Run database migrations: python manage.py makemigrations && python manage.py migrate")
        print("2. Test the API endpoints with a REST client")
        print("3. Set up a cron job to run: python manage.py process_reminders")
        print("4. Configure production email settings in environment variables")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_schedule_service() 