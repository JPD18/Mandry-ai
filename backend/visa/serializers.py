from rest_framework import serializers
from .models import UploadedDocument, Appointment


class UploadedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDocument
        fields = ['id', 'filename', 'uploaded_at', 'file_type']


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'user_name', 'appointment_type', 'scheduled_date', 'notes']



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