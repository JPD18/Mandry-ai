from django.contrib import admin
from .models import UploadedDocument, Appointment


@admin.register(UploadedDocument)
class UploadedDocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['filename']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'appointment_type', 'scheduled_date', 'created_at']
    list_filter = ['appointment_type', 'scheduled_date']
    search_fields = ['user_name']


