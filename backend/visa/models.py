from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Flexible, context-aware user profile for visa assistance"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='visa_profile')
    
    # Core context - what we always try to understand first
    nationality = models.CharField(max_length=100, blank=True, help_text="User's nationality/citizenship")
    current_location = models.CharField(max_length=100, blank=True, help_text="Where user currently lives")
    destination_country = models.CharField(max_length=100, blank=True, help_text="Country user wants to visit/move to")
    visa_intent = models.TextField(blank=True, help_text="What user wants to do (travel, work, study, etc.)")
    
    # Structured data that emerges from conversation
    structured_data = models.JSONField(default=dict, blank=True, help_text="Key-value pairs extracted from conversation")
    
    # Unstructured context and notes
    profile_context = models.TextField(blank=True, help_text="Rich context about user's situation")
    conversation_insights = models.TextField(blank=True, help_text="Insights gathered during conversation")
    
    # What information is still needed (determined by LLM)
    missing_context = models.JSONField(default=list, blank=True, help_text="List of context areas LLM thinks are needed")
    
    # Profile readiness
    context_sufficient = models.BooleanField(default=False, help_text="LLM assessment of whether context is sufficient")
    last_context_assessment = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Context Profile"
    
    def get_core_context(self):
        """Get the essential context string for LLM"""
        context_parts = []
        if self.nationality:
            context_parts.append(f"Nationality: {self.nationality}")
        if self.current_location:
            context_parts.append(f"Currently in: {self.current_location}")
        if self.destination_country:
            context_parts.append(f"Destination: {self.destination_country}")
        if self.visa_intent:
            context_parts.append(f"Intent: {self.visa_intent}")
        
        if self.structured_data:
            for key, value in self.structured_data.items():
                if value:
                    context_parts.append(f"{key.title()}: {value}")
        
        return " | ".join(context_parts) if context_parts else "No context established yet"
    
    def get_context_summary(self):
        """Get a comprehensive context summary"""
        summary = self.get_core_context()
        if self.profile_context:
            summary += f"\n\nAdditional Context: {self.profile_context}"
        if self.conversation_insights:
            summary += f"\n\nInsights: {self.conversation_insights}"
        return summary
    
    def add_structured_data(self, key, value):
        """Add or update structured data"""
        if not self.structured_data:
            self.structured_data = {}
        self.structured_data[key] = value
        self.save()
    
    def add_context_insight(self, insight):
        """Add to conversation insights (avoid duplicates)"""
        if not insight or insight.strip() == "":
            return
            
        # Check if this insight already exists
        if self.conversation_insights and insight in self.conversation_insights:
            return
            
        if self.conversation_insights:
            # Limit to last 5 insights to avoid system prompt bloat
            insights = self.conversation_insights.split('\n• ')
            insights = [i.strip('• ') for i in insights if i.strip()]
            if len(insights) >= 5:
                insights = insights[-4:]  # Keep last 4, add new one
            insights.append(insight)
            self.conversation_insights = '\n• '.join([''] + insights).strip()
        else:
            self.conversation_insights = f"• {insight}"
        self.save()
    
    def update_missing_context(self, missing_areas):
        """Update what context is still needed"""
        self.missing_context = missing_areas if isinstance(missing_areas, list) else [missing_areas]
        self.save()
    
    def get_context_completeness(self):
        """Get context completeness percentage based on core elements"""
        score = 0
        if self.nationality: score += 25
        if self.visa_intent: score += 25
        if self.current_location: score += 15
        if self.destination_country: score += 15
        
        # Additional context: conversation_insights OR structured_data OR profile_context
        additional_context = bool(
            (self.conversation_insights and self.conversation_insights.strip()) or
            (self.structured_data and len(self.structured_data) > 0) or
            (self.profile_context and self.profile_context.strip())
        )
        if additional_context: score += 20
        
        return min(score, 100)
    
    def is_complete(self):
        """Check if profile has all required information for Q&A mode"""
        # Core fields required: nationality, visa_intent, current_location, destination_country
        core_complete = bool(
            self.nationality and 
            self.visa_intent and 
            self.current_location and 
            self.destination_country
        )
        
        # Additional context required: at least one of conversation_insights, structured_data, or profile_context
        additional_context = bool(
            (self.conversation_insights and self.conversation_insights.strip()) or
            (self.structured_data and len(self.structured_data) > 0) or
            (self.profile_context and self.profile_context.strip())
        )
        
        return core_complete and additional_context





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



