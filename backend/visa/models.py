from django.db import models
from django.contrib.auth.models import User





class ActivityLog(models.Model):
    """
    Log of document processing activities without storing sensitive data
    Only stores metadata about what happened, not the actual content
    """
    ACTIVITY_TYPES = [
        ('document_processed', 'Document Processed'),
        ('document_validation', 'Document Validation'),
        ('text_extraction', 'Text Extraction'),
        ('processing_error', 'Processing Error'),
    ]
    
    VALIDATION_RESULTS = [
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Non-sensitive metadata only
    file_type = models.CharField(max_length=10, blank=True)  # pdf, png, jpg, etc.
    document_type = models.CharField(max_length=50, blank=True)  # document, passport, visa, etc.
    file_size_kb = models.IntegerField(null=True, blank=True)  # File size in KB
    text_length = models.IntegerField(null=True, blank=True)  # Length of extracted text (character count)
    validation_result = models.CharField(max_length=10, choices=VALIDATION_RESULTS, blank=True)
    processing_successful = models.BooleanField(default=False)
    
    # Error information (if applicable)
    error_type = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"


class Reminder(models.Model):
    """Enhanced model for all types of reminders"""
    
    REMINDER_TYPES = [
        ('visa_appointment', 'Visa Appointment'),
        ('visa_expiry', 'Visa Expiry'),
        ('document_deadline', 'Document Deadline'),
        ('consultation', 'Consultation'),
        ('document_review', 'Document Review'),
        ('application_submission', 'Application Submission'),
        ('interview_prep', 'Interview Preparation'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sent', 'Reminder Sent'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    reminder_type = models.CharField(max_length=50, choices=REMINDER_TYPES)
    target_date = models.DateTimeField(help_text="The date/time this reminder is for")
    reminder_date = models.DateTimeField(help_text="When to send the reminder")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Email tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['reminder_date', 'priority']
        indexes = [
            models.Index(fields=['user', 'status', 'reminder_date']),
            models.Index(fields=['reminder_date', 'email_sent']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_reminder_type_display()} on {self.target_date.strftime('%Y-%m-%d')}"


# Keep the old Appointment model for backward compatibility, but mark as deprecated
class Appointment(models.Model):
    """Deprecated - Use Reminder model instead"""
    APPOINTMENT_TYPES = [
        ('consultation', 'Consultation'),
        ('document_review', 'Document Review'),
        ('application_submission', 'Application Submission'),
        ('interview_prep', 'Interview Preparation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    user_name = models.CharField(max_length=100)
    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPES)
    scheduled_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user_name} - {self.appointment_type} on {self.scheduled_date}"



