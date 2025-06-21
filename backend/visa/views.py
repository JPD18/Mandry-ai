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
from .models import UploadedDocument, Appointment, UserProfile
from .serializers import (
    FileUploadSerializer, 
    QuestionSerializer, 
    ScheduleSerializer,
    UploadedDocumentSerializer,
    UserSignupSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    LangGraphChatSerializer
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


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    GET /api/profile - Get user profile
    PUT /api/profile - Update user profile
    DELETE /api/profile - Clear user profile
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Clear all profile data while keeping the profile object
        profile.nationality = ''
        profile.current_location = ''
        profile.destination_country = ''
        profile.visa_intent = ''
        profile.structured_data = {}
        profile.profile_context = ''
        profile.conversation_insights = ''
        profile.missing_context = []
        profile.context_sufficient = False
        profile.last_context_assessment = None
        profile.save()
        
        return Response({
            'message': 'Profile cleared successfully'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def langgraph_chat(request):
    """
    POST /api/chat - LangGraph-powered visa assistant chat
    Body: {message, session_state?}
    Returns: {response, current_step, profile_complete, session_state}
    """
    from services.langgraph_service import visa_assistant_workflow
    
    serializer = LangGraphChatSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.validated_data['message']
        session_state = serializer.validated_data.get('session_state')
        
        try:
            # Handle special "start" message for initial bot greeting
            if message.lower() == "start":
                # Convert to a more natural initial message that triggers greeting
                message = "Hello, I'm new here and need help with visa information."
            
            # Process message through LangGraph workflow
            result = visa_assistant_workflow.process_message(
                user_id=request.user.id,
                message=message,
                current_state=session_state
            )
            
            # Build session_state for client to send back next time
            session_state_out = {
                'current_step': result['current_step'],
                'message_history': result['message_history']
            }
            if result.get('last_question'):
                session_state_out['last_question'] = result['last_question']

            return Response({
                'response': result['response'],
                'current_step': result['current_step'],
                'context_sufficient': result['context_sufficient'],
                'missing_context_areas': result['missing_context_areas'],
                'session_data': result['session_data'],
                'session_state': session_state_out,
                'message_history': result['message_history']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"LangGraph chat error: {e}")
            return Response({
                'error': 'Sorry, I encountered an error processing your message. Please try again.',
                'current_step': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 