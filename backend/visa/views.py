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
    from .valyu import valyu_search, get_rag_enhanced_prompt, ValyuAPIException
    
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        question = serializer.validated_data['question']
        
        try:
            # Get enhanced RAG prompt with Valyu search context
            logger.info(f"Creating RAG-enhanced prompt for question: {question}")
            enhanced_system_prompt = get_rag_enhanced_prompt(question, max_sources=3)
            
            # Get citations from search results for response
            search_results = valyu_search(question, top_k=5)
            citations = []
            for result in search_results:
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
            
            logger.info(f"RAG-verified response generated with {len(citations)} citations")
            
            return Response({
                'answer': response,
                'citations': citations,
                'rag_verified': True,
                'source_count': len(search_results)
            }, status=status.HTTP_200_OK)
            
        except ValyuAPIException as e:
            # If Valyu API fails, fall back to LLM-only response with warning
            logger.warning(f"Valyu API error: {str(e)}, falling back to LLM-only response")
            
            fallback_response = default_llm.call(
                "You are a travel assistant. IMPORTANT: Always remind users to verify information with official government sources as you don't have access to real-time official data.",
                question
            )
            
            return Response({
                'answer': f"⚠️ **Verification temporarily unavailable** - Please verify this information with official sources.\n\n{fallback_response}",
                'citations': [{
                    "title": "Please verify with official sources",
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