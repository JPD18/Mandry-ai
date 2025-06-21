import os
import logging
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from .models import UploadedDocument, Appointment
from .serializers import (
    FileUploadSerializer, 
    QuestionSerializer, 
    ScheduleSerializer,
    UploadedDocumentSerializer,
    UserSignupSerializer,
    UserLoginSerializer
)
from services.llm_service import default_llm, LLMService
from services.document_service import default_document_service, DocumentProcessingException

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    POST /api/signup - Create new user account
    """
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'User created successfully',
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/login - Authenticate user and return token
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        if user:
            # Get or create token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Login successful',
                'token': token.key,
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
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
        
        # Save document associated with the authenticated user
        document = UploadedDocument.objects.create(
            user=request.user,
            file=uploaded_file,
            filename=uploaded_file.name,
            file_type=file_extension
        )
        
        return Response({'file_id': document.id}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ask_question(request):
    """
    POST /api/ask - Body {question}; return {answer, citations}
    RAG-verified with Valyu Search API against gov.uk and other official sources
    """
    from .valyu import get_rag_enhanced_prompt_with_sources, ValyuAPIException
    
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        question = serializer.validated_data['question']
        
        try:
            # Get enhanced RAG prompt AND the sources used for context
            # This ensures citations match exactly what the LLM used for context
            logger.info(f"Creating RAG-enhanced prompt for question: {question}")
            enhanced_system_prompt, context_sources = get_rag_enhanced_prompt_with_sources(
                question, max_sources=3
            )
            
            # Build citations from the same sources used for LLM context
            citations = []
            for result in context_sources:
                citations.append({
                    "title": result.get('title', 'Official Source'),
                    "url": result.get('url', '#'),
                    "snippet": result.get('snippet', '')[:200] + "..." if len(result.get('snippet', '')) > 200 else result.get('snippet', '')
                })

            # Get LLM response with RAG-enhanced context (no user message needed since it's in system prompt)
            response = default_llm.call(enhanced_system_prompt, "", extra_params={
                "max_tokens": 500,
                "temperature": 0.3  # Lower temperature for more factual responses
            })
            
            # If no search results were found, add a fallback citation
            if not citations:
                citations = [{
                    "title": "Official Government Sources",
                    "url": "https://gov.uk",
                    "snippet": "Please verify information with official government websites"
                }]
            
            logger.info(f"RAG-verified response generated with {len(citations)} citations matching LLM context sources")
            
            return Response({
                'answer': response,
                'citations': citations,
                'rag_verified': True,
                'source_count': len(context_sources)
            }, status=status.HTTP_200_OK)
            
        except ValyuAPIException as e:
            # If Valyu API fails, fall back to LLM-only response with warning
            logger.warning(f"Valyu API error: {str(e)}, falling back to LLM-only response")
            
            fallback_response = default_llm.call(
                "You are a travel assistant for the United Kingdom. IMPORTANT: Always remind users to verify information with official UK government sources as you don't have access to real-time official data.",
                question
            )
            
            return Response({
                'answer': f"⚠️ **Verification temporarily unavailable** - Please verify this information with official UK government sources.\n\n{fallback_response}",
                'citations': [{
                    "title": "Please verify with official UK sources",
                    "url": "https://gov.uk",
                    "snippet": "Real-time verification temporarily unavailable"
                }],
                'rag_verified': False,
                'error': 'verification_unavailable'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Unexpected error in ask_question: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred while processing your question'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def schedule_appointment(request):
    """
    POST /api/schedule - Body {user, type, iso_date}; log "Reminder scheduled"
    """
    serializer = ScheduleSerializer(data=request.data)
    if serializer.is_valid():
        user_name = serializer.validated_data['user']
        appointment_type = serializer.validated_data['type']
        scheduled_date = serializer.validated_data['iso_date']
        
        # Save appointment associated with the authenticated user
        appointment = Appointment.objects.create(
            user=request.user,
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


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    POST /api/logout - Delete user's auth token
    """
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Failed to logout'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def process_document(request):
    """
    POST /api/process-document - Process uploaded document without storing
    Extracts text and validates document using LLM
    Body: {file, document_type (optional)}
    Returns: {is_valid, reason, extracted_text, metadata}
    """
    try:
        # Check if file is provided
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        document_type = request.data.get('document_type', 'document')
        
        # Validate file type
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in ['pdf', 'png', 'jpg', 'jpeg']:
            return Response(
                {'error': 'Only PDF, PNG, and JPG files are allowed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process document using the document service
        logger.info(f"Processing {file_extension} document for user {request.user.username}")
        
        result = default_document_service.process_document(
            uploaded_file, 
            file_extension,
            document_type
        )
        
        # Return processing results
        response_data = {
            'is_valid': result['validation']['is_valid'],
            'reason': result['validation']['reason'],
            'extracted_text': result['extracted_text'],
            'metadata': result['metadata'],
            'processing_successful': True
        }
        
        logger.info(f"Document processing completed for user {request.user.username}. Valid: {result['validation']['is_valid']}")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except DocumentProcessingException as e:
        logger.error(f"Document processing failed: {str(e)}")
        return Response(
            {
                'error': str(e),
                'processing_successful': False
            }, 
            status=e.status_code
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in document processing: {str(e)}")
        return Response(
            {
                'error': 'Internal server error during document processing',
                'processing_successful': False
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def validate_text(request):
    """
    POST /api/validate-text - Validate text content using LLM
    Body: {text, document_type (optional)}
    Returns: {is_valid, reason}
    """
    try:
        # Check if text is provided
        if 'text' not in request.data:
            return Response(
                {'error': 'No text provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        text_content = request.data['text']
        document_type = request.data.get('document_type', 'document')
        
        # Validate text length
        if not text_content.strip():
            return Response(
                {'error': 'Empty text provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use document service to validate text
        logger.info(f"Validating text content for user {request.user.username}")
        
        validation_result = default_document_service.validate_document_with_llm(
            text_content, 
            document_type
        )
        
        logger.info(f"Text validation completed for user {request.user.username}. Valid: {validation_result['is_valid']}")
        
        return Response(validation_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Text validation failed: {str(e)}")
        return Response(
            {
                'error': 'Text validation failed',
                'is_valid': False,
                'reason': 'Validation service temporarily unavailable'
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 