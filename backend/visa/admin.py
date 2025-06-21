from django.contrib import admin
from .models import Appointment, ActivityLog, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nationality', 'visa_intent_short', 'context_sufficient', 'context_completeness_display']
    list_filter = ['context_sufficient', 'nationality']
    search_fields = ['user__username', 'nationality', 'visa_intent']
    readonly_fields = ['created_at', 'updated_at', 'last_context_assessment']
    
    fieldsets = (
        ('Core Context', {
            'fields': ('user', 'nationality', 'current_location', 'visa_intent')
        }),
        ('Dynamic Context', {
            'fields': ('structured_data', 'profile_context', 'conversation_insights')
        }),
        ('Assessment', {
            'fields': ('missing_context', 'context_sufficient', 'last_context_assessment')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def visa_intent_short(self, obj):
        return obj.visa_intent[:50] + "..." if len(obj.visa_intent) > 50 else obj.visa_intent
    visa_intent_short.short_description = "Intent"
    
    def context_completeness_display(self, obj):
        return f"{obj.get_context_completeness()}%"
    context_completeness_display.short_description = "Context %"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'file_type', 'document_type', 'text_length', 'validation_result', 'processing_successful', 'timestamp']
    list_filter = ['activity_type', 'file_type', 'document_type', 'validation_result', 'processing_successful', 'timestamp']
    search_fields = ['user__username', 'error_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        # Activity logs are created automatically, not manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Activity logs should not be editable
        return False


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'appointment_type', 'scheduled_date', 'created_at']
    list_filter = ['appointment_type', 'scheduled_date']
    search_fields = ['user_name']


