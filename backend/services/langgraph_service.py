"""
Intelligent LangGraph Visa Assistant Workflow Service

This service creates a context-aware conversation flow that adapts to each user's
unique situation and intelligently determines what information is needed.

Example: Ukrainian user wanting to apply for visas -> LLM determines what context
is needed (marital status, education, timeline, etc.) based on their specific situation.
"""

import logging
import json
from typing import Dict, Any, List, TypedDict, Annotated
from datetime import datetime
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from django.contrib.auth.models import User
from django.utils import timezone
from visa.models import UserProfile
from .llm_service import default_llm

logger = logging.getLogger(__name__)


class VisaAssistantState(TypedDict):
    """State schema for the intelligent visa assistant workflow"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: int
    current_step: str
    context_sufficient: bool
    missing_context_areas: List[str]
    session_data: Dict[str, Any]


class IntelligentVisaAssistantWorkflow:
    """Context-aware LangGraph workflow for visa assistance"""
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the intelligent LangGraph workflow"""
        workflow = StateGraph(VisaAssistantState)
        
        # Add nodes - simplified but more intelligent
        workflow.add_node("assess_context", self.assess_context)
        workflow.add_node("gather_context", self.gather_context)
        workflow.add_node("intelligent_qna", self.intelligent_qna)
        workflow.add_node("end", self.end)
        
        # Define edges
        workflow.add_edge(START, "assess_context")
        
        # Conditional edges based on context sufficiency
        workflow.add_conditional_edges(
            "assess_context",
            self._decide_after_context_assessment,
            {
                "gather_context": "gather_context",
                "intelligent_qna": "intelligent_qna"
            }
        )
        
        workflow.add_conditional_edges(
            "gather_context", 
            self._decide_after_context_gathering,
            {
                "gather_context": "gather_context",
                "intelligent_qna": "intelligent_qna"
            }
        )
        
        workflow.add_conditional_edges(
            "intelligent_qna",
            self._decide_after_qna,
            {
                "intelligent_qna": "intelligent_qna",
                "end": "end"
            }
        )
        
        workflow.add_edge("end", END)
        
        return workflow.compile()
    
    def assess_context(self, state: VisaAssistantState) -> VisaAssistantState:
        """
        Intelligently assess what context we have and what we might need
        """
        logger.info(f"Assessing context for user {state['user_id']}")
        
        try:
            user = User.objects.get(id=state['user_id'])
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Get current context summary
            current_context = profile.get_context_summary()
            
            # Use LLM to assess context sufficiency
            context_assessment = self._get_intelligent_context_assessment(current_context, profile)
            
            # Update profile with assessment
            profile.context_sufficient = context_assessment.get('sufficient', False)
            profile.update_missing_context(context_assessment.get('missing_areas', []))
            profile.last_context_assessment = timezone.now()
            profile.save()
            
            # Create response message
            if context_assessment.get('sufficient', False):
                message = AIMessage(content=f"Great! I understand your situation: {profile.get_core_context()}. What specific visa questions do you have?")
            else:
                message = AIMessage(content=context_assessment.get('message', 'Let me learn about your situation to provide better assistance.'))
            
            # Update state
            new_state = state.copy()
            new_state["messages"] = state["messages"] + [message]
            new_state["current_step"] = "assess_context"
            new_state["context_sufficient"] = context_assessment.get('sufficient', False)
            new_state["missing_context_areas"] = context_assessment.get('missing_areas', [])
            new_state["session_data"] = {
                "profile_id": profile.id,
                "context_completeness": profile.get_context_completeness(),
                "created_profile": created,
                "assessment": context_assessment
            }
            
            return new_state
            
        except Exception as e:
            logger.error(f"Error assessing context: {e}")
            error_message = AIMessage(content="Let's start fresh - tell me about your visa situation!")
            new_state = state.copy()
            new_state["messages"] = state["messages"] + [error_message]
            new_state["current_step"] = "gather_context"
            new_state["context_sufficient"] = False
            new_state["missing_context_areas"] = ["basic_situation"]
            return new_state
    
    def gather_context(self, state: VisaAssistantState) -> VisaAssistantState:
        """
        Intelligently gather contextual information based on conversation
        """
        logger.info(f"Gathering context for user {state['user_id']}")
        
        try:
            user = User.objects.get(id=state['user_id'])
            profile = user.visa_profile
            
            # Get the last human message
            last_human_message = None
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    last_human_message = msg.content
                    break
            
            if last_human_message and last_human_message.strip():
                # Extract insights from the message
                extraction_result = self._extract_context_intelligently(
                    last_human_message, 
                    profile, 
                    state["missing_context_areas"]
                )
                
                # Update profile with new information
                self._update_profile_from_extraction(profile, extraction_result)
                
                # Re-assess context sufficiency
                context_assessment = self._get_intelligent_context_assessment(
                    profile.get_context_summary(), 
                    profile
                )
                
                profile.context_sufficient = context_assessment.get('sufficient', False)
                profile.update_missing_context(context_assessment.get('missing_areas', []))
                profile.save()
                
                # Generate response
                if context_assessment.get('sufficient', False):
                    response = f"Perfect! Now I understand your situation. {context_assessment.get('message', 'What specific questions do you have?')}"
                else:
                    response = context_assessment.get('message', 'Please tell me more about your situation.')
                
            else:
                # Generate intelligent questions
                response = self._generate_intelligent_questions(profile, state["missing_context_areas"])
                context_assessment = {'sufficient': False}
            
            ai_message = AIMessage(content=response)
            
            new_state = state.copy()
            new_state["messages"] = state["messages"] + [ai_message]
            new_state["current_step"] = "gather_context"
            new_state["context_sufficient"] = context_assessment.get('sufficient', False)
            new_state["missing_context_areas"] = context_assessment.get('missing_areas', state["missing_context_areas"])
            new_state["session_data"]["context_completeness"] = profile.get_context_completeness()
            
            return new_state
            
        except Exception as e:
            logger.error(f"Error gathering context: {e}")
            error_message = AIMessage(content="Could you tell me briefly about your visa situation?")
            new_state = state.copy()
            new_state["messages"] = state["messages"] + [error_message]
            return new_state
    
    def intelligent_qna(self, state: VisaAssistantState) -> VisaAssistantState:
        """
        Provide intelligent, context-aware visa assistance
        """
        logger.info(f"Intelligent Q&A session for user {state['user_id']}")
        
        try:
            user = User.objects.get(id=state['user_id'])
            profile = user.visa_profile
            
            # Get the last human message
            last_human_message = None
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    last_human_message = msg.content
                    break
            
            if not last_human_message:
                response = "Now that I understand your situation, what specific visa questions do you have? I can provide personalized guidance."
            else:
                # Generate highly personalized response
                response = self._generate_intelligent_visa_advice(profile, last_human_message)
            
            ai_message = AIMessage(content=response)
            
            new_state = state.copy()
            new_state["messages"] = state["messages"] + [ai_message]
            new_state["current_step"] = "intelligent_qna"
            
            return new_state
            
        except Exception as e:
            logger.error(f"Error in intelligent Q&A: {e}")
            error_message = AIMessage(content="Please try asking your question again.")
            new_state = state.copy()
            new_state["messages"] = state["messages"] + [error_message]
            return new_state
    
    def end(self, state: VisaAssistantState) -> VisaAssistantState:
        """End the interaction"""
        end_message = AIMessage(content="Thank you for using Mandry AI! Feel free to return anytime with more visa questions!")
        
        new_state = state.copy()
        new_state["messages"] = state["messages"] + [end_message]
        new_state["current_step"] = "end"
        
        return new_state
    
    # Decision functions
    def _decide_after_context_assessment(self, state: VisaAssistantState) -> str:
        return "intelligent_qna" if state["context_sufficient"] else "gather_context"
    
    def _decide_after_context_gathering(self, state: VisaAssistantState) -> str:
        return "intelligent_qna" if state["context_sufficient"] else "gather_context"
    
    def _decide_after_qna(self, state: VisaAssistantState) -> str:
        # Check for end phrases
        last_human_message = ""
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                last_human_message = msg.content.lower()
                break
        
        end_phrases = ["goodbye", "thank you", "bye", "exit", "quit", "that's all", "thanks"]
        if any(phrase in last_human_message for phrase in end_phrases):
            return "end"
        
        return "intelligent_qna"
    
    # Intelligent helper methods
    def _get_intelligent_context_assessment(self, current_context: str, profile: UserProfile) -> Dict[str, Any]:
        """Use LLM to assess context sufficiency and determine what's needed"""
        
        system_prompt = f"""
        You are an intelligent visa consultant analyzing a user's context.
        
        Current context: {current_context}
        
        Assess if there's sufficient context to provide meaningful visa advice.
        Consider: nationality (essential), visa intent (essential), personal circumstances, timeline.
        
        Return JSON:
        {{
            "sufficient": boolean,
            "missing_areas": ["area1", "area2"],
            "message": "What to say to user"
        }}
        """
        
        try:
            response = default_llm.call(system_prompt, "", {"max_tokens": 200, "temperature": 0.2})
            
            # Clean and parse JSON
            response = response.strip()
            if "```" in response:
                response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            
            assessment = json.loads(response.strip())
            return assessment
        except Exception as e:
            logger.warning(f"Failed context assessment: {e}")
            # Fallback logic
            has_nationality = bool(profile.nationality)
            has_intent = bool(profile.visa_intent)
            
            if has_nationality and has_intent:
                return {
                    "sufficient": True,
                    "missing_areas": [],
                    "message": "I have good context about your situation."
                }
            else:
                missing = []
                if not has_nationality:
                    missing.append("nationality")
                if not has_intent:
                    missing.append("visa_intent")
                
                return {
                    "sufficient": False,
                    "missing_areas": missing,
                    "message": "I need to understand your nationality and visa goals."
                }
    
    def _extract_context_intelligently(self, message: str, profile: UserProfile, missing_areas: List[str]) -> Dict[str, Any]:
        """Extract context information intelligently from user message"""
        
        system_prompt = f"""
        Extract relevant visa consultation information from this message.
        
        Current context: {profile.get_context_summary()}
        Missing: {missing_areas}
        
        Message: {message}
        
        Return JSON with any relevant info:
        {{
            "nationality": "if mentioned",
            "current_location": "if mentioned", 
            "visa_intent": "what they want to do",
            "structured_data": {{"key": "value"}},
            "insights": ["insight1"],
            "context": "additional context"
        }}
        """
        
        try:
            response = default_llm.call(system_prompt, "", {"max_tokens": 300, "temperature": 0.1})
            
            # Clean and parse JSON
            response = response.strip()
            if "```" in response:
                response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            
            extracted = json.loads(response.strip())
            return extracted
        except Exception as e:
            logger.warning(f"Failed extraction: {e}")
            # Simple fallback
            message_lower = message.lower()
            extracted = {}
            
            # Basic nationality detection
            if "ukrainian" in message_lower:
                extracted["nationality"] = "Ukrainian"
            elif "american" in message_lower:
                extracted["nationality"] = "American"
            elif "indian" in message_lower:
                extracted["nationality"] = "Indian"
            
            # Basic intent detection
            if any(word in message_lower for word in ["work", "job", "employment"]):
                extracted["visa_intent"] = "Work/employment"
            elif any(word in message_lower for word in ["study", "university", "education"]):
                extracted["visa_intent"] = "Study/education"
            elif any(word in message_lower for word in ["visit", "travel", "tourism"]):
                extracted["visa_intent"] = "Visit/tourism"
            
            return extracted
    
    def _update_profile_from_extraction(self, profile: UserProfile, extraction_result: Dict[str, Any]):
        """Update profile with extracted information"""
        if extraction_result.get('nationality'):
            profile.nationality = extraction_result['nationality']
            
        if extraction_result.get('current_location'):
            profile.current_location = extraction_result['current_location']
            
        if extraction_result.get('visa_intent'):
            profile.visa_intent = extraction_result['visa_intent']
        
        if extraction_result.get('context'):
            profile.profile_context = extraction_result['context']
        
        if extraction_result.get('structured_data'):
            for key, value in extraction_result['structured_data'].items():
                profile.add_structured_data(key, value)
        
        if extraction_result.get('insights'):
            for insight in extraction_result['insights']:
                profile.add_context_insight(insight)
        
        profile.save()
    
    def _generate_intelligent_questions(self, profile: UserProfile, missing_areas: List[str]) -> str:
        """Generate intelligent questions based on context"""
        
        system_prompt = f"""
        Generate friendly questions to understand a user's visa situation better.
        
        Current context: {profile.get_context_summary()}
        Missing: {missing_areas}
        
        Ask 1-2 natural questions to understand their nationality, visa goals, and situation.
        Be conversational and helpful.
        """
        
        try:
            response = default_llm.call(system_prompt, "", {"max_tokens": 150, "temperature": 0.4})
            return response
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return "Could you tell me about your nationality and what you're hoping to achieve with visas?"
    
    def _generate_intelligent_visa_advice(self, profile: UserProfile, question: str) -> str:
        """Generate intelligent, personalized visa advice"""
        
        system_prompt = f"""
        You are an expert UK visa consultant providing personalized advice.
        
        User context: {profile.get_context_summary()}
        
        Question: {question}
        
        Provide specific, actionable advice based on their unique situation.
        Consider their nationality, intent, and circumstances.
        Be encouraging but realistic with practical next steps.
        """
        
        try:
            response = default_llm.call(system_prompt, question, {"max_tokens": 400, "temperature": 0.3})
            return response
        except Exception as e:
            logger.error(f"Error generating advice: {e}")
            return "I'd like to help with your visa question. Could you please rephrase it?"
    
    def process_message(self, user_id: int, message: str, current_state: Dict = None) -> Dict[str, Any]:
        """Process a user message through the intelligent workflow"""
        try:
            # Initialize state
            if current_state:
                state = VisaAssistantState(
                    messages=[],
                    user_id=user_id,
                    current_step=current_state.get("current_step", "assess_context"),
                    context_sufficient=current_state.get("context_sufficient", False),
                    missing_context_areas=current_state.get("missing_context_areas", []),
                    session_data=current_state.get("session_data", {})
                )
                # Restore message history
                for msg_data in current_state.get("message_history", []):
                    if msg_data["type"] == "human":
                        state["messages"].append(HumanMessage(content=msg_data["content"]))
                    else:
                        state["messages"].append(AIMessage(content=msg_data["content"]))
            else:
                state = VisaAssistantState(
                    messages=[],
                    user_id=user_id,
                    current_step="assess_context",
                    context_sufficient=False,
                    missing_context_areas=[],
                    session_data={}
                )
            
            # Add current message
            state["messages"].append(HumanMessage(content=message))
            
            # Run workflow
            result = self.graph.invoke(state)
            
            # Get latest AI response
            ai_response = ""
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    ai_response = msg.content
                    break
            
            return {
                "response": ai_response,
                "current_step": result["current_step"],
                "context_sufficient": result["context_sufficient"],
                "missing_context_areas": result["missing_context_areas"],
                "session_data": result["session_data"],
                "message_history": [
                    {
                        "type": "human" if isinstance(msg, HumanMessage) else "ai",
                        "content": msg.content
                    }
                    for msg in result["messages"]
                ]
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


# Global instance
visa_assistant_workflow = IntelligentVisaAssistantWorkflow() 