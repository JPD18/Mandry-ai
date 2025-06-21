from rest_framework import serializers
from .models import Appointment


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000)


class ScheduleSerializer(serializers.Serializer):
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