"""
Simple Stateless Visa Assistant Service

This service handles visa assistance through a simple state machine approach.
Each user message advances the state by exactly one step - NO INTERNAL LOOPS.

Flow: assess_context → gather_context → intelligent_qna → end
"""

import logging
from typing import Dict, Any, List
from django.contrib.auth.models import User
from django.utils import timezone
from visa.models import UserProfile

logger = logging.getLogger(__name__)


class IntelligentVisaAssistantWorkflow:
    """Simple stateless visa assistant - NO INTERNAL LOOPS"""
    
    def __init__(self):
        # No graph needed - we'll handle state manually
        pass
    
    # All old LangGraph methods removed - using simple state machine now
    
    def _extract_context_intelligently(self, message: str, profile: UserProfile, missing_areas: List[str]) -> Dict[str, Any]:
        """Extract context information using simple keyword matching - NO LLM CALLS"""
        
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
        
        # Basic location detection
        if any(word in message_lower for word in ["live in", "living in", "currently in", "based in"]):
            # This is basic - in real app you'd want more sophisticated parsing
            extracted["current_location"] = "User mentioned current location"
        
        return extracted
    
    def _update_profile_from_extraction(self, profile: UserProfile, extraction_result: Dict[str, Any]):
        """Update profile with extracted information - SIMPLIFIED"""
        updated = False
        
        if extraction_result.get('nationality') and not profile.nationality:
            profile.nationality = extraction_result['nationality']
            updated = True
            
        if extraction_result.get('current_location') and not profile.current_location:
            profile.current_location = extraction_result['current_location']
            updated = True
            
        if extraction_result.get('visa_intent') and not profile.visa_intent:
            profile.visa_intent = extraction_result['visa_intent']
            updated = True
        
        # Only save if we actually updated something
        if updated:
            profile.save()
    
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
        """Handle context assessment step"""
        # Check if we have basic context
        has_nationality = bool(profile.nationality)
        has_intent = bool(profile.visa_intent)
        
        if has_nationality and has_intent:
            profile.context_sufficient = True
            profile.save()
            response = f"Hello! I see you're {profile.nationality} interested in {profile.visa_intent}. What specific questions do you have?"
            next_step = "intelligent_qna"
        else:
            response = "Hello! I'm your visa assistant. To get started, please tell me your nationality and what type of visa you're interested in."
            next_step = "gather_context"
        
        return response, next_step
    
    def _handle_gather_context(self, user: User, profile: UserProfile, message: str) -> tuple[str, str]:
        """Handle context gathering step"""
        # Extract info from message
        extraction_result = self._extract_context_intelligently(message, profile, [])
        self._update_profile_from_extraction(profile, extraction_result)
        
        # Check if we now have sufficient context
        has_nationality = bool(profile.nationality)
        has_intent = bool(profile.visa_intent)
        
        if has_nationality and has_intent:
            profile.context_sufficient = True
            profile.save()
            response = f"Great! I understand you're {profile.nationality} and interested in {profile.visa_intent}. What specific questions do you have?"
            next_step = "intelligent_qna"
        else:
            missing = []
            if not has_nationality: missing.append("your nationality")
            if not has_intent: missing.append("your visa goals")
            response = f"Thanks for that information! I still need to know {' and '.join(missing)} to help you better."
            next_step = "gather_context"
        
        return response, next_step
    
    def _handle_qna(self, user: User, profile: UserProfile, message: str) -> tuple[str, str]:
        """Handle Q&A step"""
        # Check for end phrases
        message_lower = message.lower()
        end_phrases = ["goodbye", "thank you", "bye", "exit", "quit", "that's all", "thanks"]
        
        if any(phrase in message_lower for phrase in end_phrases):
            response = "Thank you for using Mandry AI! Feel free to return anytime with more visa questions!"
            next_step = "end"
        else:
            # Simple response
            response = f"Thank you for your question about '{message[:50]}...'. As a {profile.nationality or 'person'} interested in {profile.visa_intent or 'visas'}, I'd recommend consulting with official visa requirements. What else would you like to know?"
            next_step = "intelligent_qna"
        
        return response, next_step


# Global instance
visa_assistant_workflow = IntelligentVisaAssistantWorkflow() 