from rest_framework import serializers
from .models import UploadedDocument, Appointment, UserProfile


class UploadedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDocument
        fields = ['id', 'filename', 'uploaded_at', 'file_type']


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'user_name', 'appointment_type', 'scheduled_date', 'notes']


class UserProfileSerializer(serializers.ModelSerializer):
    context_completeness = serializers.SerializerMethodField()
    core_context = serializers.SerializerMethodField()
    context_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'nationality', 'current_location', 'visa_intent',
            'structured_data', 'profile_context', 'conversation_insights',
            'missing_context', 'context_sufficient', 'context_completeness',
            'core_context', 'context_summary', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'context_completeness', 'core_context', 'context_summary',
            'created_at', 'updated_at'
        ]
    
    def get_context_completeness(self, obj):
        return obj.get_context_completeness()
    
    def get_core_context(self, obj):
        return obj.get_core_context()
    
    def get_context_summary(self, obj):
        return obj.get_context_summary()



class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000)


class ScheduleSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=50)
    iso_date = serializers.DateTimeField()


class UserSignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class LangGraphChatSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    session_state = serializers.JSONField(required=False, allow_null=True) 