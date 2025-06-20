import os
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import UploadedDocument, Appointment
from .serializers import (
    FileUploadSerializer, 
    QuestionSerializer, 
    ScheduleSerializer,
    UploadedDocumentSerializer
)
from services.llm_service import default_llm, LLMService

logger = logging.getLogger(__name__)


@api_view(['POST'])
def upload_document(request):
    """
    POST /api/upload - Accept PDF/PNG/JPG files, save to media/, return file_id
    """
    serializer = FileUploadSerializer(data=request.data)
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        
        # Check file type
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in ['pdf', 'png', 'jpg', 'jpeg']:
            return Response(
                {'error': 'Only PDF, PNG, and JPG files are allowed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save document
        document = UploadedDocument.objects.create(
            file=uploaded_file,
            filename=uploaded_file.name,
            file_type=file_extension
        )
        
        return Response({'file_id': document.id}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def ask_question(request):
    """
    POST /api/ask - Body {question}; return {answer, citations}
    """
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        question = serializer.validated_data['question']
        
        # Use the default instance
        response = default_llm.call("You are a travel assistant", question)
        
        # Mock citations for MVP
        citations = [
            {"source": "Official Immigration Website", "url": "#"},
            {"source": "Visa Requirements Document", "url": "#"}
        ]
        
        return Response({
            'answer': response,
            'citations': citations
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def schedule_appointment(request):
    """
    POST /api/schedule - Body {user, type, iso_date}; log "Reminder scheduled"
    """
    serializer = ScheduleSerializer(data=request.data)
    if serializer.is_valid():
        user_name = serializer.validated_data['user']
        appointment_type = serializer.validated_data['type']
        scheduled_date = serializer.validated_data['iso_date']
        
        # Save appointment
        appointment = Appointment.objects.create(
            user_name=user_name,
            appointment_type=appointment_type,
            scheduled_date=scheduled_date
        )
        
        # Log reminder
        logger.info(f"Reminder scheduled for {user_name} - {appointment_type} on {scheduled_date}")
        print(f"Reminder scheduled for {user_name} - {appointment_type} on {scheduled_date}")
        
        return Response({
            'message': 'Reminder scheduled successfully',
            'appointment_id': appointment.id
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 