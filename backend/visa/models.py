from django.db import models
from django.contrib.auth.models import User


class UploadedDocument(models.Model):
    file = models.FileField(upload_to='documents/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=10)  # pdf, png, jpg
    
    def __str__(self):
        return self.filename


class Appointment(models.Model):
    APPOINTMENT_TYPES = [
        ('consultation', 'Consultation'),
        ('document_review', 'Document Review'),
        ('application_submission', 'Application Submission'),
        ('interview_prep', 'Interview Preparation'),
    ]
    
    user_name = models.CharField(max_length=100)
    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPES)
    scheduled_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user_name} - {self.appointment_type} on {self.scheduled_date}"


