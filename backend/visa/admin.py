from django.contrib import admin
from .models import UploadedDocument, Appointment, ChatMessage


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


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['question', 'answer']
    
    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question' 