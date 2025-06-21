"""
Intelligent Visa Assistant Service with Anthropic AI

This service handles visa assistance through a simple state machine approach
enhanced with intelligent AI responses using Anthropic's Claude.
Each user message advances the state by exactly one step - NO INTERNAL LOOPS.

Flow: assess_context → gather_context → intelligent_qna → end
"""

import logging
from typing import Dict, Any, List
from django.contrib.auth.models import User
from django.utils import timezone
from visa.models import UserProfile
from .anthropic_service import anthropic_llm

logger = logging.getLogger(__name__)


class IntelligentVisaAssistantWorkflow:
    """Simple stateless visa assistant - NO INTERNAL LOOPS"""
    
    def __init__(self):
        # No graph needed - we'll handle state manually
        pass
    
    # All old LangGraph methods removed - using simple state machine now
    
    def _extract_context_intelligently(self, message: str, profile: UserProfile, missing_areas: List[str]) -> Dict[str, Any]:
        """Extract context information using AI-powered analysis"""
        
        try:
            # Create extraction prompt
            system_prompt = """You are an expert visa consultant's assistant. Extract key information from user messages.

Analyze the user's message and extract the following information if present:
- nationality: The user's nationality/citizenship
- visa_intent: The type of visa they want (work, student, tourist, family, business, etc.)
- current_location: Where they currently live/are located
- destination_country: Which country they want to visit/move to
- timeline: When they plan to travel/apply
- specific_concerns: Any specific questions or concerns mentioned

Only extract information that is clearly stated or strongly implied. Don't make assumptions."""

            user_prompt = f"""User message: "{message}"

Current profile context:
- Current nationality: {profile.nationality or 'Not specified'}
- Current visa intent: {profile.visa_intent or 'Not specified'}
- Current location: {profile.current_location or 'Not specified'}

Extract any new information from this message."""

            # Use AI to extract information
            extraction_result = anthropic_llm.call_for_json(
                system_prompt=system_prompt,
                user_message=user_prompt,
                extra_params={"max_tokens": 500, "temperature": 0.3}
            )
            
            # Validate and clean the extraction result
            cleaned_result = {}
            if isinstance(extraction_result, dict):
                for key in ["nationality", "visa_intent", "current_location", "destination_country", "timeline", "specific_concerns"]:
                    if key in extraction_result and extraction_result[key] and extraction_result[key].lower() not in ["not specified", "none", "n/a", ""]:
                        cleaned_result[key] = extraction_result[key]
            
            return cleaned_result
            
        except Exception as e:
            logger.warning(f"AI extraction failed, falling back to keyword matching: {e}")
            
            # Fallback to keyword matching
            message_lower = message.lower()
            extracted = {}
            
            # Basic nationality detection
            nationalities = {
                "ukrainian": "Ukrainian", "ukraine": "Ukrainian",
                "american": "American", "usa": "American", "us": "American",
                "indian": "Indian", "india": "Indian",
                "british": "British", "uk": "British",
                "canadian": "Canadian", "canada": "Canadian",
                "australian": "Australian", "australia": "Australian",
                "german": "German", "germany": "German",
                "french": "French", "france": "French",
                "chinese": "Chinese", "china": "Chinese",
                "japanese": "Japanese", "japan": "Japanese"
            }
            
            for keyword, nationality in nationalities.items():
                if keyword in message_lower:
                    extracted["nationality"] = nationality
                    break
            
            # Basic intent detection
            if any(word in message_lower for word in ["work", "job", "employment", "working", "career"]):
                extracted["visa_intent"] = "Work visa"
            elif any(word in message_lower for word in ["study", "university", "education", "student", "studying", "school"]):
                extracted["visa_intent"] = "Student visa"
            elif any(word in message_lower for word in ["visit", "travel", "tourism", "tourist", "vacation", "holiday"]):
                extracted["visa_intent"] = "Tourist visa"
            elif any(word in message_lower for word in ["family", "spouse", "partner", "marry", "marriage"]):
                extracted["visa_intent"] = "Family visa"
            elif any(word in message_lower for word in ["business", "investor", "investment"]):
                extracted["visa_intent"] = "Business visa"
            
            return extracted
    
    def _update_profile_from_extraction(self, profile: UserProfile, extraction_result: Dict[str, Any]):
        """Update profile with extracted information from AI analysis"""
        updated = False
        
        # Update nationality if not already set
        if extraction_result.get('nationality') and not profile.nationality:
            profile.nationality = extraction_result['nationality']
            updated = True
            
        # Update current location if not already set
        if extraction_result.get('current_location') and not profile.current_location:
            profile.current_location = extraction_result['current_location']
            updated = True
            
        # Update visa intent if not already set
        if extraction_result.get('visa_intent') and not profile.visa_intent:
            profile.visa_intent = extraction_result['visa_intent']
            updated = True
        
        # Update destination country if not already set
        if extraction_result.get('destination_country') and not profile.destination_country:
            profile.destination_country = extraction_result['destination_country']
            updated = True
        
        # Add specific concerns to conversation insights (if not already present)
        if extraction_result.get('specific_concerns'):
            concern = extraction_result['specific_concerns']
            if concern not in (profile.conversation_insights or ''):
                if profile.conversation_insights:
                    profile.conversation_insights += f"\n- {concern}"
                else:
                    profile.conversation_insights = f"- {concern}"
                updated = True
        
        # Add timeline information to insights
        if extraction_result.get('timeline'):
            timeline = extraction_result['timeline']
            timeline_info = f"Timeline: {timeline}"
            if timeline_info not in (profile.conversation_insights or ''):
                if profile.conversation_insights:
                    profile.conversation_insights += f"\n- {timeline_info}"
                else:
                    profile.conversation_insights = f"- {timeline_info}"
                updated = True
        
        # Only save if we actually updated something
        if updated:
            profile.save()
            logger.info(f"Updated profile for user {profile.user.id} with: {extraction_result}")
    
    # Removed complex LLM methods to prevent 400 errors and infinite loops
    
    def process_message(self, user_id: int, message: str, current_state: Dict = None) -> Dict[str, Any]:
        """Process a user message - ONE STEP ONLY, NO LOOPS"""
        
        try:
            # Get user and profile
            user = User.objects.get(id=user_id)
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Determine current step
            current_step = current_state.get("current_step", "assess_context") if current_state else "assess_context"
            
            # Restore message history
            message_history = current_state.get("message_history", []) if current_state else []
            
            # Add user message to history
            message_history.append({"type": "human", "content": message})
            
            # Process based on current step - EXACTLY ONE STEP
            if current_step == "assess_context":
                response, next_step = self._handle_assess_context(user, profile, message)
            elif current_step == "gather_context":
                response, next_step = self._handle_gather_context(user, profile, message)
            elif current_step == "intelligent_qna":
                response, next_step = self._handle_qna(user, profile, message)
            else:
                response = "Thank you for using Mandry AI!"
                next_step = "end"
            
            # Add AI response to history
            message_history.append({"type": "ai", "content": response})
            
            return {
                "response": response,
                "current_step": next_step,
                "context_sufficient": profile.context_sufficient,
                "missing_context_areas": [],
                "session_data": {
                    "profile_id": profile.id,
                    "context_completeness": profile.get_context_completeness()
                },
                "message_history": message_history
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I'm having trouble right now. Could you please try again?",
                "current_step": "error",
                "context_sufficient": False,
                "missing_context_areas": [],
                "session_data": {},
                "message_history": []
            }
    
    def _handle_assess_context(self, user: User, profile: UserProfile, message: str) -> tuple[str, str]:
        """Handle context assessment step with intelligent welcome"""
        # Check if we have basic context
        has_nationality = bool(profile.nationality)
        has_intent = bool(profile.visa_intent)
        
        # Check if this is a completely new user (empty profile)
        is_new_user = not any([profile.nationality, profile.visa_intent, profile.current_location, profile.conversation_insights])
        
        if has_nationality and has_intent:
            profile.context_sufficient = True
            profile.save()
            try:
                # Generate personalized welcome message for returning users
                response = self._generate_welcome_message(profile, message)
            except Exception as e:
                logger.warning(f"AI welcome generation failed: {e}")
                response = f"Hello! I see you're {profile.nationality} interested in {profile.visa_intent}. What specific questions do you have?"
            next_step = "intelligent_qna"
        elif is_new_user:
            try:
                # Generate visa-focused welcome message for brand new users
                response = self._generate_new_user_welcome(message)
            except Exception as e:
                logger.warning(f"AI new user welcome failed: {e}")
                response = "Welcome to Mandry AI! 🌍 I'm your personal visa and travel assistant. Whether you're planning to work, study, visit family, or explore new destinations, I'm here to guide you through the visa process. What kind of travel or visa assistance can I help you with today?"
            next_step = "gather_context"
        else:
            try:
                # Generate intelligent initial assessment for users with partial info
                response = self._generate_initial_assessment(profile, message)
            except Exception as e:
                logger.warning(f"AI initial assessment failed: {e}")
                response = "Hello! I'm Mandry AI, your visa and travel assistant. I can help you with work visas, student visas, tourist visas, family visas, and more. To provide you with the best guidance, please tell me your nationality and what type of visa or travel assistance you need."
            next_step = "gather_context"
        
        return response, next_step
    
    def _generate_new_user_welcome(self, message: str) -> str:
        """Generate visa-focused welcome message for brand new users"""
        
        system_prompt = """You are Mandry AI, a friendly and professional visa and travel consultant assistant.
        
        Generate a warm welcome message for a first-time user that:
        1. Welcomes them to Mandry AI
        2. Clearly explains you specialize in visa and travel assistance
        3. Mentions the types of visa/travel help you provide (work, study, tourism, family, business visas)
        4. Asks what specific visa or travel assistance they need
        5. Uses an encouraging, professional tone with appropriate emojis
        
        Keep it engaging but concise (2-3 sentences). Make it clear this is specifically for visa/travel help."""
        
        user_prompt = f"""User's first message: "{message}"

Generate a welcoming message that introduces Mandry AI as a visa and travel assistant and asks what kind of visa/travel help they need."""
        
        response = anthropic_llm.call(
            system_prompt=system_prompt,
            user_message=user_prompt,
            extra_params={"max_tokens": 200, "temperature": 0.8}
        )
        
        return response
    
    def _generate_welcome_message(self, profile: UserProfile, message: str) -> str:
        """Generate personalized welcome message for users with complete context"""
        
        system_prompt = """You are Mandry AI, a friendly and professional visa consultant assistant. 
        
        Generate a warm, personalized welcome message for a returning user or someone whose profile you already know. 
        Be conversational, acknowledge their specific situation, and invite them to ask questions.
        Keep it concise (1-2 sentences) and professional yet friendly."""
        
        user_prompt = f"""User Profile:
- Nationality: {profile.nationality}
- Visa Interest: {profile.visa_intent}
- Current Location: {profile.current_location or 'Not specified'}

User's current message: "{message}"

Generate a personalized welcome message."""
        
        response = anthropic_llm.call(
            system_prompt=system_prompt,
            user_message=user_prompt,
            extra_params={"max_tokens": 150, "temperature": 0.8}
        )
        
        return response
    
    def _generate_initial_assessment(self, profile: UserProfile, message: str) -> str:
        """Generate intelligent initial assessment and information gathering for users with partial info"""
        
        system_prompt = """You are Mandry AI, a friendly visa and travel consultant assistant.
        
        The user has some profile information but it's incomplete. Generate a response that:
        1. Acknowledges what you already know about them
        2. Shows you understand their visa/travel inquiry
        3. Asks for the missing information you need to provide better assistance
        4. Emphasizes your expertise in visa and travel matters
        5. Keeps them engaged and confident in your help
        
        Keep it conversational and encouraging (2-3 sentences). Focus on visa/travel assistance."""
        
        user_prompt = f"""Current Profile Information:
- Nationality: {profile.nationality or 'Not provided'}
- Visa Interest: {profile.visa_intent or 'Not provided'}
- Current Location: {profile.current_location or 'Not provided'}

User's message: "{message}"

Generate an appropriate response that acknowledges their partial profile and asks for missing visa/travel information."""
        
        response = anthropic_llm.call(
            system_prompt=system_prompt,
            user_message=user_prompt,
            extra_params={"max_tokens": 200, "temperature": 0.8}
        )
        
        return response
    
    def _handle_gather_context(self, user: User, profile: UserProfile, message: str) -> tuple[str, str]:
        """Handle context gathering step with intelligent follow-up"""
        # Extract info from message
        extraction_result = self._extract_context_intelligently(message, profile, [])
        self._update_profile_from_extraction(profile, extraction_result)
        
        # Check if we now have sufficient context
        has_nationality = bool(profile.nationality)
        has_intent = bool(profile.visa_intent)
        
        if has_nationality and has_intent:
            profile.context_sufficient = True
            profile.save()
            try:
                # Generate intelligent transition to Q&A
                response = self._generate_context_complete_message(profile, message, extraction_result)
            except Exception as e:
                logger.warning(f"AI context complete message failed: {e}")
                response = f"Great! I understand you're {profile.nationality} and interested in {profile.visa_intent}. What specific questions do you have?"
            next_step = "intelligent_qna"
        else:
            try:
                # Generate intelligent follow-up questions
                response = self._generate_context_follow_up(profile, message, extraction_result)
            except Exception as e:
                logger.warning(f"AI context follow-up failed: {e}")
                missing = []
                if not has_nationality: missing.append("your nationality")
                if not has_intent: missing.append("your visa goals")
                response = f"Thanks for that information! I still need to know {' and '.join(missing)} to help you better."
            next_step = "gather_context"
        
        return response, next_step
    
    def _generate_context_complete_message(self, profile: UserProfile, message: str, extraction_result: Dict[str, Any]) -> str:
        """Generate intelligent message when context gathering is complete"""
        
        system_prompt = """You are Mandry AI, a visa consultant assistant. The user has provided enough basic information to start helping them.
        
        Generate a response that:
        1. Acknowledges what they've shared
        2. Confirms your understanding of their situation
        3. Transitions smoothly to offering specific help
        4. Sounds natural and encouraging
        
        Keep it conversational and professional (2-3 sentences)."""
        
        user_prompt = f"""User Profile:
- Nationality: {profile.nationality}
- Visa Interest: {profile.visa_intent}
- Current Location: {profile.current_location or 'Not specified'}

User's latest message: "{message}"

Information just extracted: {extraction_result}

Generate a response confirming you understand their situation and are ready to help with specific questions."""
        
        response = anthropic_llm.call(
            system_prompt=system_prompt,
            user_message=user_prompt,
            extra_params={"max_tokens": 200, "temperature": 0.7}
        )
        
        return response
    
    def _generate_context_follow_up(self, profile: UserProfile, message: str, extraction_result: Dict[str, Any]) -> str:
        """Generate intelligent follow-up questions for missing context"""
        
        system_prompt = """You are Mandry AI, a visa consultant assistant gathering information from a new user.
        
        Generate a response that:
        1. Acknowledges what they've shared so far
        2. Naturally asks for the missing information you need
        3. Explains briefly why you need this information
        4. Keeps them engaged and comfortable
        
        Be conversational and encouraging (2-3 sentences)."""
        
        missing_info = []
        if not profile.nationality:
            missing_info.append("nationality/citizenship")
        if not profile.visa_intent:
            missing_info.append("type of visa you're interested in")
        
        user_prompt = f"""Current Profile:
- Nationality: {profile.nationality or 'Not provided'}
- Visa Interest: {profile.visa_intent or 'Not provided'}
- Current Location: {profile.current_location or 'Not provided'}

User's latest message: "{message}"
Information just extracted: {extraction_result}
Still missing: {', '.join(missing_info)}

Generate a natural follow-up response asking for the missing information."""
        
        response = anthropic_llm.call(
            system_prompt=system_prompt,
            user_message=user_prompt,
            extra_params={"max_tokens": 200, "temperature": 0.7}
        )
        
        return response
    
    def _handle_qna(self, user: User, profile: UserProfile, message: str) -> tuple[str, str]:
        """Handle Q&A step with intelligent AI responses"""
        # Check for end phrases
        message_lower = message.lower()
        end_phrases = ["goodbye", "thank you", "bye", "exit", "quit", "that's all", "thanks"]
        
        if any(phrase in message_lower for phrase in end_phrases):
            response = "Thank you for using Mandry AI! Feel free to return anytime with more visa questions!"
            next_step = "end"
        else:
            try:
                # Generate intelligent response using AI
                response = self._generate_intelligent_response(profile, message)
                next_step = "intelligent_qna"
            except Exception as e:
                logger.warning(f"AI response generation failed: {e}")
                # Fallback to simple response
                response = f"Thank you for your question about '{message[:50]}...'. As a {profile.nationality or 'person'} interested in {profile.visa_intent or 'visas'}, I'd recommend consulting with official visa requirements. What else would you like to know?"
                next_step = "intelligent_qna"
        
        return response, next_step
    
    def _generate_intelligent_response(self, profile: UserProfile, user_question: str) -> str:
        """Generate intelligent, contextual responses using AI"""
        
        # Build comprehensive context
        context_info = []
        if profile.nationality:
            context_info.append(f"Nationality: {profile.nationality}")
        if profile.visa_intent:
            context_info.append(f"Visa type of interest: {profile.visa_intent}")
        if profile.current_location:
            context_info.append(f"Current location: {profile.current_location}")
        if profile.destination_country:
            context_info.append(f"Destination country: {profile.destination_country}")
        
        # Add conversation insights for context
        if profile.conversation_insights:
            context_info.append(f"Previous concerns/topics: {profile.conversation_insights}")
        
        context_str = "\n".join(context_info) if context_info else "Limited profile information available"
        
        system_prompt = """You are Mandry AI, an expert visa consultant assistant. You provide helpful, accurate, and personalized visa guidance.

Guidelines for responses:
1. Be conversational and empathetic
2. Provide specific, actionable advice when possible
3. Always mention that official sources should be consulted for final decisions
4. If you don't have enough information, ask clarifying questions
5. Keep responses concise but informative (2-4 sentences)
6. Use the user's profile context to personalize your advice
7. Be encouraging and supportive throughout the visa process
8. Reference previous conversation topics when relevant
9. Provide step-by-step guidance when appropriate

Important: Always remind users to verify information with official government sources or qualified immigration lawyers for their specific situation."""

        user_prompt = f"""User Profile Context:
{context_str}

User's Current Question: "{user_question}"

Provide a helpful, personalized response addressing their question. Use their profile context to give specific advice. If you need more information to give better advice, ask specific follow-up questions."""

        response = anthropic_llm.call(
            system_prompt=system_prompt,
            user_message=user_prompt,
            extra_params={"max_tokens": 400, "temperature": 0.7}
        )
        
        return response


# Global instance
visa_assistant_workflow = IntelligentVisaAssistantWorkflow() 