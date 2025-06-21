import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class ScheduleServiceException(APIException):
    """Custom exception for schedule service errors"""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Schedule service operation failed.'
    default_code = 'schedule_service_error'


class ScheduleService:
    """
    Comprehensive service for managing reminders, appointments, and email notifications
    """
    
    # Default reminder intervals (in days before target date)
    DEFAULT_REMINDER_INTERVALS = {
        'visa_appointment': [7, 1],  # 1 week and 1 day before
        'visa_expiry': [30, 7, 1],  # 1 month, 1 week, 1 day before
        'document_deadline': [7, 3, 1],  # 1 week, 3 days, 1 day before
        'consultation': [3, 1],  # 3 days and 1 day before
        'document_review': [2, 1],  # 2 days and 1 day before
        'application_submission': [7, 3, 1],  # 1 week, 3 days, 1 day before
        'interview_prep': [7, 1],  # 1 week and 1 day before
    }
    
    def __init__(self):
        self.email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@mandry.ai')
        self.email_enabled = self._check_email_configuration()
        
    def _check_email_configuration(self) -> bool:
        """Check if email is properly configured"""
        try:
            # Check basic email settings
            email_backend = getattr(settings, 'EMAIL_BACKEND', None)
            if not email_backend:
                logger.warning("EMAIL_BACKEND not configured")
                return False
                
            # For development, we'll use console backend
            if 'console' in email_backend.lower():
                logger.info("Using console email backend for development")
                return True
                
            # Check SMTP settings if using SMTP backend
            if 'smtp' in email_backend.lower():
                host = getattr(settings, 'EMAIL_HOST', None)
                port = getattr(settings, 'EMAIL_PORT', None)
                if not host or not port:
                    logger.warning("SMTP email settings incomplete")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Email configuration check failed: {str(e)}")
            return False
    
    def create_reminder(self, user: User, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new reminder with automatic reminder scheduling
        
        Args:
            user: User object
            reminder_data: Dictionary containing reminder details
            
        Returns:
            Dict containing the created reminder details
        """
        from visa.models import Reminder
        
        try:
            # Validate required fields
            required_fields = ['title', 'reminder_type', 'target_date']
            for field in required_fields:
                if field not in reminder_data:
                    raise ScheduleServiceException(f"Missing required field: {field}")
            
            # Parse target date
            target_date = self._parse_datetime(reminder_data['target_date'])
            if target_date <= timezone.now():
                raise ScheduleServiceException("Target date must be in the future")
            
            # Calculate reminder dates based on type
            reminder_dates = self._calculate_reminder_dates(
                target_date, 
                reminder_data['reminder_type'],
                reminder_data.get('custom_intervals')
            )
            
            reminders_created = []
            
            # Create multiple reminders based on intervals
            for i, reminder_date in enumerate(reminder_dates):
                if reminder_date > timezone.now():  # Only create future reminders
                    reminder = Reminder.objects.create(
                        user=user,
                        title=reminder_data['title'],
                        description=reminder_data.get('description', ''),
                        reminder_type=reminder_data['reminder_type'],
                        target_date=target_date,
                        reminder_date=reminder_date,
                        priority=reminder_data.get('priority', 'medium'),
                        notes=reminder_data.get('notes', '')
                    )
                    
                    reminders_created.append({
                        'id': reminder.id,
                        'reminder_date': reminder_date.isoformat(),
                        'days_before': (target_date - reminder_date).days
                    })
            
            if not reminders_created:
                raise ScheduleServiceException("No future reminder dates could be scheduled")
            
            logger.info(f"Created {len(reminders_created)} reminders for user {user.username}")
            
            return {
                'success': True,
                'reminders_created': len(reminders_created),
                'reminder_details': reminders_created,
                'target_date': target_date.isoformat(),
                'type': reminder_data['reminder_type']
            }
            
        except ScheduleServiceException:
            raise
        except Exception as e:
            logger.error(f"Failed to create reminder: {str(e)}")
            raise ScheduleServiceException(f"Failed to create reminder: {str(e)}")
    
    def _parse_datetime(self, date_input: Any) -> datetime:
        """Parse datetime from various input formats"""
        if isinstance(date_input, datetime):
            return timezone.make_aware(date_input) if timezone.is_naive(date_input) else date_input
        
        if isinstance(date_input, str):
            try:
                # Try ISO format first
                return timezone.make_aware(datetime.fromisoformat(date_input.replace('Z', '+00:00')))
            except ValueError:
                try:
                    # Try parsing common formats
                    return timezone.make_aware(datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S'))
                except ValueError:
                    return timezone.make_aware(datetime.strptime(date_input, '%Y-%m-%d'))
        
        raise ScheduleServiceException(f"Invalid date format: {date_input}")
    
    def _calculate_reminder_dates(self, target_date: datetime, reminder_type: str, custom_intervals: Optional[List[int]] = None) -> List[datetime]:
        """Calculate when reminders should be sent"""
        intervals = custom_intervals or self.DEFAULT_REMINDER_INTERVALS.get(reminder_type, [1])
        reminder_dates = []
        
        for days_before in intervals:
            reminder_date = target_date - timedelta(days=days_before)
            reminder_dates.append(reminder_date)
        
        return sorted(reminder_dates)
    
    def get_due_reminders(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get reminders that are due to be sent"""
        from visa.models import Reminder
        
        try:
            now = timezone.now()
            
            due_reminders = Reminder.objects.filter(
                reminder_date__lte=now,
                email_sent=False,
                status='active'
            ).select_related('user').order_by('priority', 'reminder_date')[:limit]
            
            reminder_list = []
            for reminder in due_reminders:
                reminder_list.append({
                    'id': reminder.id,
                    'user_id': reminder.user.id,
                    'user_email': reminder.user.email,
                    'title': reminder.title,
                    'description': reminder.description,
                    'reminder_type': reminder.reminder_type,
                    'target_date': reminder.target_date,
                    'reminder_date': reminder.reminder_date,
                    'priority': reminder.priority
                })
            
            logger.info(f"Found {len(reminder_list)} due reminders")
            return reminder_list
            
        except Exception as e:
            logger.error(f"Failed to get due reminders: {str(e)}")
            return []
    
    def send_reminder_email(self, reminder_data: Dict[str, Any]) -> bool:
        """Send reminder email to user"""
        if not self.email_enabled:
            logger.warning("Email not configured, skipping email send")
            return False
        
        try:
            user_email = reminder_data['user_email']
            subject = self._generate_email_subject(reminder_data)
            message = self._generate_email_content(reminder_data)
            html_message = self._generate_html_email_content(reminder_data)
            
            # Send email
            if html_message:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=self.email_from,
                    to=[user_email]
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
            else:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=self.email_from,
                    recipient_list=[user_email],
                    fail_silently=False
                )
            
            # Mark reminder as sent
            self._mark_reminder_sent(reminder_data['id'])
            
            logger.info(f"Reminder email sent successfully to {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send reminder email: {str(e)}")
            return False
    
    def _generate_email_subject(self, reminder_data: Dict[str, Any]) -> str:
        """Generate email subject based on reminder type"""
        reminder_type = reminder_data['reminder_type']
        title = reminder_data['title']
        
        subject_templates = {
            'visa_appointment': f"Reminder: {title} - Visa Appointment",
            'visa_expiry': f"⚠️ Important: {title} - Visa Expiry Alert",
            'document_deadline': f"Action Required: {title} - Document Deadline",
            'consultation': f"Upcoming: {title} - Consultation",
            'document_review': f"Reminder: {title} - Document Review",
            'application_submission': f"Deadline: {title} - Application Submission",
            'interview_prep': f"Prepare: {title} - Interview Preparation"
        }
        
        return subject_templates.get(reminder_type, f"Reminder: {title}")
    
    def _generate_email_content(self, reminder_data: Dict[str, Any]) -> str:
        """Generate plain text email content"""
        content = f"""
Hello,

This is a friendly reminder about: {reminder_data['title']}

Type: {reminder_data['reminder_type'].replace('_', ' ').title()}
Date: {reminder_data['target_date'].strftime('%B %d, %Y at %I:%M %p')}
Priority: {reminder_data['priority'].title()}

{reminder_data.get('description', '')}

Please make sure you're prepared for this important date.

Best regards,
Mandry AI Team
        """.strip()
        
        return content
    
    def _generate_html_email_content(self, reminder_data: Dict[str, Any]) -> str:
        """Generate HTML email content"""
        try:
            # Create a simple HTML template
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c5aa0;">Reminder: {reminder_data['title']}</h2>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Type:</strong> {reminder_data['reminder_type'].replace('_', ' ').title()}</p>
                        <p><strong>Date:</strong> {reminder_data['target_date'].strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Priority:</strong> <span style="color: {'#dc3545' if reminder_data['priority'] == 'urgent' else '#28a745' if reminder_data['priority'] == 'low' else '#ffc107'};">{reminder_data['priority'].title()}</span></p>
                    </div>
                    
                    {f'<p>{reminder_data["description"]}</p>' if reminder_data.get('description') else ''}
                    
                    <p>Please make sure you're prepared for this important date.</p>
                    
                    <hr style="margin: 30px 0;">
                    <p style="font-size: 12px; color: #666;">
                        Best regards,<br>
                        Mandry AI Team
                    </p>
                </div>
            </body>
            </html>
            """
            return html_content
            
        except Exception as e:
            logger.warning(f"Failed to generate HTML email: {str(e)}")
            return None
    
    def _mark_reminder_sent(self, reminder_id: int) -> None:
        """Mark a reminder as sent"""
        from visa.models import Reminder
        
        try:
            reminder = Reminder.objects.get(id=reminder_id)
            reminder.email_sent = True
            reminder.email_sent_at = timezone.now()
            reminder.status = 'sent'
            reminder.save()
            
        except Reminder.DoesNotExist:
            logger.error(f"Reminder {reminder_id} not found")
        except Exception as e:
            logger.error(f"Failed to mark reminder as sent: {str(e)}")
    
    def get_user_reminders(self, user: User, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get reminders for a specific user"""
        from visa.models import Reminder
        
        try:
            query = Reminder.objects.filter(user=user)
            
            if status:
                query = query.filter(status=status)
            
            reminders = query.order_by('-created_at')[:limit]
            
            reminder_list = []
            for reminder in reminders:
                reminder_list.append({
                    'id': reminder.id,
                    'title': reminder.title,
                    'description': reminder.description,
                    'reminder_type': reminder.reminder_type,
                    'target_date': reminder.target_date.isoformat(),
                    'reminder_date': reminder.reminder_date.isoformat(),
                    'status': reminder.status,
                    'priority': reminder.priority,
                    'email_sent': reminder.email_sent,
                    'created_at': reminder.created_at.isoformat()
                })
            
            return reminder_list
            
        except Exception as e:
            logger.error(f"Failed to get user reminders: {str(e)}")
            return []
    
    def update_reminder_status(self, reminder_id: int, status: str, user: User = None) -> bool:
        """Update reminder status"""
        from visa.models import Reminder
        
        try:
            query = Reminder.objects.filter(id=reminder_id)
            if user:
                query = query.filter(user=user)
            
            reminder = query.first()
            if not reminder:
                raise ScheduleServiceException("Reminder not found")
            
            valid_statuses = ['active', 'sent', 'completed', 'cancelled']
            if status not in valid_statuses:
                raise ScheduleServiceException(f"Invalid status: {status}")
            
            reminder.status = status
            reminder.save()
            
            logger.info(f"Updated reminder {reminder_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update reminder status: {str(e)}")
            return False
    
    def process_due_reminders(self) -> Dict[str, Any]:
        """Process all due reminders and send emails - main method for background tasks"""
        try:
            due_reminders = self.get_due_reminders()
            
            if not due_reminders:
                return {
                    'success': True,
                    'processed': 0,
                    'sent': 0,
                    'failed': 0,
                    'message': 'No due reminders found'
                }
            
            sent_count = 0
            failed_count = 0
            
            for reminder in due_reminders:
                try:
                    if self.send_reminder_email(reminder):
                        sent_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Failed to process reminder {reminder['id']}: {str(e)}")
                    failed_count += 1
            
            result = {
                'success': True,
                'processed': len(due_reminders),
                'sent': sent_count,
                'failed': failed_count,
                'message': f"Processed {len(due_reminders)} reminders: {sent_count} sent, {failed_count} failed"
            }
            
            logger.info(result['message'])
            return result
            
        except Exception as e:
            logger.error(f"Failed to process due reminders: {str(e)}")
            return {
                'success': False,
                'processed': 0,
                'sent': 0,
                'failed': 0,
                'error': str(e)
            }


# Create default instance for easy import
default_schedule_service = ScheduleService() 