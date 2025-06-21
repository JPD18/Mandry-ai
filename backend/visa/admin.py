from django.contrib import admin
from .models import Appointment, ActivityLog


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


