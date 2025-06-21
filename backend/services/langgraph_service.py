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
        logger.info(f"🔍 EXTRACT_CONTEXT - Message: '{message[:50]}...', Current Profile: Nationality={profile.nationality}, Intent={profile.visa_intent}")
        
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
- background: Educational/professional background, experience, qualifications
- purpose_details: Specific purpose or reason for the visa application
- duration: How long they plan to stay
- previous_experience: Any previous visa applications or travel history

Only extract information that is clearly stated or strongly implied. Don't make assumptions.
Focus on capturing any additional context that would help understand their visa situation better."""

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
                for key in ["nationality", "visa_intent", "current_location", "destination_country", "timeline", "specific_concerns", "background", "purpose_details", "duration", "previous_experience"]:
                    if key in extraction_result and extraction_result[key] and extraction_result[key].lower() not in ["not specified", "none", "n/a", ""]:
                        cleaned_result[key] = extraction_result[key]
            
            logger.info(f"✅ AI EXTRACTION SUCCESS: {cleaned_result}")
            return cleaned_result
            
        except Exception as e:
            logger.warning(f"AI extraction failed, falling back to keyword matching: {e}")
            
            # Fallback to keyword matching
            logger.info(f"🔄 FALLBACK TO KEYWORD EXTRACTION")
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
            
            logger.info(f"✅ KEYWORD EXTRACTION RESULT: {extracted}")
            return extracted
    
    def _update_profile_from_extraction(self, profile: UserProfile, extraction_result: Dict[str, Any]):
        """Update profile with extracted information from AI analysis"""
        logger.info(f"📝 UPDATE_PROFILE - User: {profile.user.username}, Extraction: {extraction_result}")
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
        
        # Build profile context from any additional details provided
        additional_fields = ['timeline', 'specific_concerns', 'background', 'purpose_details', 'duration', 'previous_experience']
        if any(extraction_result.get(field) for field in additional_fields):
            # If we have additional context details, build profile context
            context_parts = []
            if extraction_result.get('timeline'):
                context_parts.append(f"Timeline: {extraction_result['timeline']}")
            if extraction_result.get('specific_concerns'):
                context_parts.append(f"Concerns: {extraction_result['specific_concerns']}")
            if extraction_result.get('background'):
                context_parts.append(f"Background: {extraction_result['background']}")
            if extraction_result.get('purpose_details'):
                context_parts.append(f"Purpose: {extraction_result['purpose_details']}")
            if extraction_result.get('duration'):
                context_parts.append(f"Duration: {extraction_result['duration']}")
            if extraction_result.get('previous_experience'):
                context_parts.append(f"Experience: {extraction_result['previous_experience']}")
            
            if context_parts and not profile.profile_context:
                profile.profile_context = "; ".join(context_parts)
                updated = True
            elif context_parts and profile.profile_context:
                # Append new context to existing
                new_context = "; ".join(context_parts)
                if new_context not in profile.profile_context:
                    profile.profile_context += f"; {new_context}"
                    updated = True
        
        # Only save if we actually updated something
        if updated:
            profile.save()
            logger.info(f"✅ PROFILE UPDATED - User: {profile.user.username}, Changes: {extraction_result}")
        else:
            logger.info(f"🔄 NO PROFILE CHANGES - No new information to update")
    
    # Removed complex LLM methods to prevent 400 errors and infinite loops
    
    def process_message(self, user_id: int, message: str, current_state: Dict = None) -> Dict[str, Any]:
        """Process a user message - ONE STEP ONLY, NO LOOPS"""
        
        logger.info(f"🔄 PROCESS_MESSAGE ENTRY - User {user_id}, Message: '{message[:50]}...', Current State: {current_state.get('current_step') if current_state else 'None'}")
        
        try:
            # Get user and profile
            user = User.objects.get(id=user_id)
            profile, created = UserProfile.objects.get_or_create(user=user)
            logger.info(f"📊 Profile Status - User: {user.username}, Nationality: {profile.nationality or 'None'}, Intent: {profile.visa_intent or 'None'}, Context Sufficient: {profile.context_sufficient}")
            
            # Determine current step
            current_step = current_state.get("current_step", "assess_context") if current_state else "assess_context"
            logger.info(f"🎯 Current Step Determined: {current_step}")
            
            # Restore message history
            message_history = current_state.get("message_history", []) if current_state else []
            
            # Add user message to history
            message_history.append({"type": "human", "content": message})
            
            # Process based on current step - EXACTLY ONE STEP
            logger.info(f"🚀 ROUTING TO HANDLER: {current_step}")
            if current_step == "assess_context":
                response, next_step = self._handle_assess_context(user, profile, message)
            elif current_step == "gather_context":
                response, next_step = self._handle_gather_context(user, profile, message)
            elif current_step == "intelligent_qna":
                response, next_step = self._handle_qna(user, profile, message)
            else:
                logger.info(f"🏁 END STATE REACHED: {current_step}")
                response = "Thank you for using Mandry AI!"
                next_step = "end"
            
            logger.info(f"✅ HANDLER COMPLETED - Response Length: {len(response)}, Next Step: {next_step}")
            
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
        logger.info(f"🔍 ASSESS_CONTEXT HANDLER - User: {user.username}, Message: '{message[:30]}...'")
        
        # Check if we have basic context
        has_nationality = bool(profile.nationality)
        has_intent = bool(profile.visa_intent)
        has_location = bool(profile.current_location)
        has_destination = bool(profile.destination_country)
        has_additional_context = bool(profile.profile_context) or bool(profile.structured_data)
        
        logger.info(f"📋 Context Check - Nationality: {has_nationality}, Intent: {has_intent}, Location: {has_location}, Destination: {has_destination}, Additional: {has_additional_context}")
        
        # Check if this is a completely new user (empty profile)
        is_new_user = not any([profile.nationality, profile.visa_intent, profile.current_location, profile.conversation_insights])
        logger.info(f"👤 User Status - Is New User: {is_new_user}")
        
        # Check if profile is 100% complete (all core fields + additional context)
        profile_complete = (has_nationality and has_intent and has_location and has_destination and has_additional_context)
        
        if profile_complete:
            logger.info(f"✅ PROFILE 100% COMPLETE - Moving to Q&A mode")
            profile.context_sufficient = True
            profile.save()
            try:
                # Generate personalized welcome message for returning users
                response = self._generate_welcome_message(profile, message)
            except Exception as e:
                logger.warning(f"AI welcome generation failed: {e}")
                response = f"Perfect! I have all the information I need. What specific questions do you have about your {profile.visa_intent}?"
            next_step = "intelligent_qna"
        elif is_new_user:
            logger.info(f"🆕 NEW USER - Generating welcome message")
            try:
                # Generate visa-focused welcome message for brand new users
                response = self._generate_new_user_welcome(message)
            except Exception as e:
                logger.warning(f"AI new user welcome failed: {e}")
                response = "👋 Welcome to Mandry AI! I will help you with visa and travel planning assistance.\n\nI will ask you a few questions to understand your plans and intents clearly. There might be multiple questions to best understand your case and needs.\n\nWhat specific visa or travel help do you need?"
            next_step = "gather_context"
        else:
            logger.info(f"📝 PARTIAL CONTEXT - Generating initial assessment")
            try:
                # Generate intelligent initial assessment for users with partial info
                response = self._generate_initial_assessment(profile, message)
            except Exception as e:
                logger.warning(f"AI initial assessment failed: {e}")
                response = "What's your nationality and what type of visa do you need?"
            next_step = "gather_context"
        
        logger.info(f"🔚 ASSESS_CONTEXT RESULT - Next Step: {next_step}")
        return response, next_step
    
    def _generate_new_user_welcome(self, message: str) -> str:
        """Generate visa-focused welcome message for brand new users"""
        logger.info(f"🆕 GENERATE_NEW_USER_WELCOME - Message: '{message[:30]}...'")
        
        system_prompt = """You are Mandry AI, a direct and professional visa and travel consultant assistant.
        
        Generate a welcome message for a first-time user that:
        1. Welcomes them to Mandry AI
        2. Clearly states you will help them with visa and travel planning assistance
        3. Explains that you will ask questions to understand their plans and intents clearly
        4. Mentions there might be multiple questions to best understand their case and needs
        5. Asks what specific visa or travel help they need
        6. Uses a direct, professional tone - no lengthy explanations
        
        Keep it direct and concise (2-3 sentences). Be straightforward about the process."""
        
        user_prompt = f"""User's first message: "{message}"

Generate a welcoming message that introduces Mandry AI as a visa and travel assistant and asks what kind of visa/travel help they need."""
        
        response = anthropic_llm.call(
            system_prompt=system_prompt,
            user_message=user_prompt,
            extra_params={"max_tokens": 200, "temperature": 0.8}
        )
        
        logger.info(f"✅ NEW USER WELCOME GENERATED - Length: {len(response)}")
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
        
        system_prompt = """You are Mandry AI, a direct visa and travel consultant assistant.
        
        The user has some profile information but it's incomplete. Generate a response that:
        1. Directly asks for the missing information you need
        2. Be specific about what information is needed (nationality, visa type, location)
        3. Keep it very brief and to the point
        4. No explanations about your expertise or reassurances
        5. No mention of "from the information you've provided"
        
        Keep it direct and concise (1-2 sentences maximum). Just ask for what you need."""
        
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
        logger.info(f"📝 GATHER_CONTEXT HANDLER - User: {user.username}, Message: '{message[:30]}...'")
        
        # Extract info from message
        extraction_result = self._extract_context_intelligently(message, profile, [])
        logger.info(f"🔍 EXTRACTION RESULT: {extraction_result}")
        self._update_profile_from_extraction(profile, extraction_result)
        
        # Check if we now have sufficient context
        has_nationality = bool(profile.nationality)
        has_intent = bool(profile.visa_intent)
        has_location = bool(profile.current_location)
        has_destination = bool(profile.destination_country)
        has_additional_context = bool(profile.profile_context) or bool(profile.structured_data)
        
        logger.info(f"📊 UPDATED CONTEXT - Nationality: {has_nationality}, Intent: {has_intent}, Location: {has_location}, Destination: {has_destination}, Additional: {has_additional_context}")
        
        # Check if profile is 100% complete (all core fields + additional context)
        profile_complete = (has_nationality and has_intent and has_location and has_destination and has_additional_context)
        
        if profile_complete:
            logger.info(f"✅ PROFILE NOW 100% COMPLETE - Moving to Q&A")
            profile.context_sufficient = True
            profile.save()
            try:
                # Generate intelligent transition to Q&A
                response = self._generate_context_complete_message(profile, message, extraction_result)
            except Exception as e:
                logger.warning(f"AI context complete message failed: {e}")
                response = f"Perfect! I have all the information I need. What specific questions do you have about your {profile.visa_intent}?"
            next_step = "intelligent_qna"
        else:
            logger.info(f"⏳ CONTEXT STILL INCOMPLETE - Generating follow-up")
            try:
                # Generate intelligent follow-up questions
                response = self._generate_context_follow_up(profile, message, extraction_result)
            except Exception as e:
                logger.warning(f"AI context follow-up failed: {e}")
                missing = []
                if not has_nationality: missing.append("nationality")
                if not has_intent: missing.append("visa type")
                if not has_location: missing.append("current location")
                if not has_destination: missing.append("destination country")
                if not has_additional_context: missing.append("more details about your situation")
                
                if len(missing) == 1:
                    response = f"What's your {missing[0]}?"
                elif len(missing) == 2:
                    response = f"What's your {missing[0]} and {missing[1]}?"
                else:
                    response = f"I still need: {', '.join(missing[:-1])}, and {missing[-1]}."
            next_step = "gather_context"
        
        logger.info(f"🔚 GATHER_CONTEXT RESULT - Next Step: {next_step}")
        return response, next_step
    
    def _generate_context_complete_message(self, profile: UserProfile, message: str, extraction_result: Dict[str, Any]) -> str:
        """Generate intelligent message when context gathering is complete"""
        
        system_prompt = """You are Mandry AI, a direct visa consultant assistant. The user has provided enough basic information to start helping them.
        
        Generate a response that:
        1. Briefly confirms their situation (nationality and visa type)
        2. Directly asks what specific questions they have
        3. No lengthy acknowledgments or explanations
        4. Keep it very brief and to the point
        
        Keep it direct and concise (1-2 sentences maximum)."""
        
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
        
        # Determine what's specifically missing
        missing_info = []
        if not profile.nationality:
            missing_info.append("nationality")
        if not profile.visa_intent:
            missing_info.append("visa type")
        if not profile.current_location:
            missing_info.append("current location")
        if not profile.destination_country:
            missing_info.append("destination country")
        if not (profile.profile_context or profile.structured_data):
            missing_info.append("additional details")
        
        # Generate specific question based on what's missing
        if "additional details" in missing_info and len(missing_info) == 1:
            # Only additional context missing - ask for specific details about their situation
            return "Tell me more about your specific situation - when do you plan to apply, what's your background, any specific concerns?"
        elif "nationality" in missing_info:
            return "What's your nationality?"
        elif "visa type" in missing_info:
            return "What type of visa do you need?"
        elif "current location" in missing_info:
            return "Where are you currently located?"
        elif "destination country" in missing_info:
            return "Which country do you want to go to?"
        
        # Fallback to AI generation for complex cases
        system_prompt = """You are Mandry AI, a direct visa consultant assistant gathering information from a new user.
        
        Ask ONLY for the specific missing information. Be direct and brief (1 sentence maximum).
        Do NOT repeat questions about information already provided."""
        
        user_prompt = f"""Current Profile:
- Nationality: {profile.nationality or 'Missing'}
- Visa Interest: {profile.visa_intent or 'Missing'}
- Current Location: {profile.current_location or 'Missing'}
- Destination Country: {profile.destination_country or 'Missing'}
- Additional Details: {'Provided' if (profile.profile_context or profile.structured_data) else 'Missing'}

Still missing: {', '.join(missing_info)}

Ask for the specific missing information. Do not repeat questions about information already provided."""
        
        response = anthropic_llm.call(
            system_prompt=system_prompt,
            user_message=user_prompt,
            extra_params={"max_tokens": 200, "temperature": 0.7}
        )
        
        return response
    
    def _handle_qna(self, user: User, profile: UserProfile, message: str) -> tuple[str, str]:
        """Handle Q&A step with intelligent AI responses"""
        logger.info(f"💬 QNA HANDLER - User: {user.username}, Message: '{message[:30]}...'")
        
        # Check for end phrases
        message_lower = message.lower()
        end_phrases = ["goodbye", "thank you", "bye", "exit", "quit", "that's all", "thanks"]
        
        if any(phrase in message_lower for phrase in end_phrases):
            logger.info(f"👋 END PHRASE DETECTED - Ending conversation")
            response = "Thank you for using Mandry AI! Feel free to return anytime with more visa questions!"
            next_step = "end"
        else:
            logger.info(f"🤖 GENERATING AI RESPONSE")
            try:
                # Generate intelligent response using AI
                response = self._generate_intelligent_response(profile, message)
                next_step = "intelligent_qna"
            except Exception as e:
                logger.warning(f"AI response generation failed: {e}")
                # Fallback to simple response
                response = f"Thank you for your question about '{message[:50]}...'. As a {profile.nationality or 'person'} interested in {profile.visa_intent or 'visas'}, I'd recommend consulting with official visa requirements. What else would you like to know?"
                next_step = "intelligent_qna"
        
        logger.info(f"🔚 QNA RESULT - Next Step: {next_step}")
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