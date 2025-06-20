from rest_framework import serializers
from .models import UploadedDocument, Appointment, ChatMessage


class UploadedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDocument
        fields = ['id', 'filename', 'uploaded_at', 'file_type']


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'user_name', 'appointment_type', 'scheduled_date', 'notes']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'question', 'answer', 'created_at']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000)


class ScheduleSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=50)
    iso_date = serializers.DateTimeField() 