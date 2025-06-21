from rest_framework import serializers

from .models import  Appointment, Reminder


class ReminderSerializer(serializers.ModelSerializer):
    """Serializer for the new Reminder model"""
    class Meta:
        model = Reminder
        fields = [
            'id', 'title', 'description', 'reminder_type', 'target_date', 
            'reminder_date', 'status', 'priority', 'email_sent', 'email_sent_at',
            'created_at', 'updated_at', 'notes'
        ]
        read_only_fields = ['id', 'email_sent', 'email_sent_at', 'created_at', 'updated_at']


class CreateReminderSerializer(serializers.Serializer):
    """Serializer for creating new reminders"""
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    reminder_type = serializers.ChoiceField(choices=Reminder.REMINDER_TYPES)
    target_date = serializers.DateTimeField()
    priority = serializers.ChoiceField(choices=Reminder.PRIORITY_CHOICES, default='medium')
    notes = serializers.CharField(required=False, allow_blank=True)
    custom_intervals = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        help_text="Custom reminder intervals in days before target date"
    )


class UpdateReminderStatusSerializer(serializers.Serializer):
    """Serializer for updating reminder status"""
    status = serializers.ChoiceField(choices=Reminder.STATUS_CHOICES)


# Keep existing serializers for backward compatibility
class AppointmentSerializer(serializers.ModelSerializer):
    """Deprecated - Use ReminderSerializer instead"""
    class Meta:
        model = Appointment
        fields = ['id', 'user_name', 'appointment_type', 'scheduled_date', 'notes']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000)


# Deprecated - Use CreateReminderSerializer instead
class ScheduleSerializer(serializers.Serializer):
    """Deprecated - Use CreateReminderSerializer instead"""
    user = serializers.CharField(max_length=100)
    type = serializers.ChoiceField(choices=[
        'consultation', 'document_review', 'application_submission', 'interview_prep'
    ])
    iso_date = serializers.DateTimeField()


class UserSignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField()


class DocumentProcessSerializer(serializers.Serializer):
    file = serializers.FileField()
    document_type = serializers.CharField(max_length=100, required=False, default='document')


class TextValidationSerializer(serializers.Serializer):
    text = serializers.CharField()
    document_type = serializers.CharField(max_length=100, required=False, default='document') 