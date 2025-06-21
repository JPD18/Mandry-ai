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
        core_elements = [self.nationality, self.visa_intent]
        additional_context = bool(self.profile_context or self.structured_data)
        
        score = 0
        if self.nationality: score += 40
        if self.visa_intent: score += 40
        if additional_context: score += 20
        
        return min(score, 100)


class UploadedDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    user_name = models.CharField(max_length=100)
    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPES)
    scheduled_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user_name} - {self.appointment_type} on {self.scheduled_date}"



