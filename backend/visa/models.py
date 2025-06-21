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


class Appointment(models.Model):
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



