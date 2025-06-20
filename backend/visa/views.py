import os
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import UploadedDocument, Appointment, ChatMessage
from .serializers import (
    FileUploadSerializer, 
    QuestionSerializer, 
    ScheduleSerializer,
    UploadedDocumentSerializer
)

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
        
        # For MVP, return a stub answer
        # In production, this would integrate with LangChain and OpenAI
        answer = f"Thank you for your question about '{question}'. This is a stub response for the MVP. In the full implementation, this would use AI to provide detailed visa and immigration guidance based on uploaded documents and official sources."
        
        # Save chat message
        chat_message = ChatMessage.objects.create(
            question=question,
            answer=answer
        )
        
        # Mock citations for MVP
        citations = [
            {"source": "Official Immigration Website", "url": "#"},
            {"source": "Visa Requirements Document", "url": "#"}
        ]
        
        return Response({
            'answer': answer,
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