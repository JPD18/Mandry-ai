"""
Anthropic LLM Service for Claude API

This service provides integration with Anthropic's Claude API for intelligent
conversation and context processing.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class AnthropicLLMService:
    """Service for interacting with Anthropic's Claude API"""
    
    def __init__(self, api_key: str = None, model: str = None, timeout: int = 30):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.timeout = timeout
        self.base_url = "https://api.anthropic.com/v1/messages"
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
        
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
    
    def call(
        self,
        system_prompt: str = None,
        user_message: str = None,
        extra_params: Dict[str, Any] = None,
    ) -> str:
        """
        Make a call to Anthropic's Claude API
        
        Args:
            system_prompt: System prompt to set context
            user_message: User's message 
            extra_params: Additional parameters for the API call
        
        Returns:
            The AI response as a string
        """
        extra_params = extra_params or {}
        
        # Build messages array
        messages = []
        
        # Add user message (combining system and user if needed)
        if user_message:
            messages.append({
                "role": "user",
                "content": user_message
            })
        elif system_prompt:
            # If only system prompt, treat it as user message
            messages.append({
                "role": "user", 
                "content": system_prompt
            })
        
        # Build payload
        payload = {
            "model": self.model,
            "max_tokens": extra_params.get("max_tokens", 1000),
            "temperature": extra_params.get("temperature", 0.7),
            "messages": messages
        }
        
        # Add system prompt if provided and we have a user message
        if system_prompt and user_message:
            payload["system"] = system_prompt
        
        try:
            logger.info(f"Making request to Anthropic API with model: {self.model}")
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract content from Claude's response format
            if 'content' in data and len(data['content']) > 0:
                return data['content'][0]['text'].strip()
            else:
                raise ValueError(f"Unexpected response format from Anthropic API: {data}")
                
        except requests.exceptions.RequestException as e:
            logger.error(
                f"AnthropicLLMService ➔ Request failed: {e}\n"
                f"  URL:    {self.base_url}\n"
                f"  MODEL:  {self.model}\n"
                f"  Payload: {json.dumps(payload, indent=2)}"
            )
            raise
        except (KeyError, ValueError, IndexError) as e:
            logger.error(
                f"AnthropicLLMService ➔ Invalid response format: {e}\n"
                f"  URL:    {self.base_url}\n"
                f"  MODEL:  {self.model}\n"
                f"  Response: {response.text if 'response' in locals() else 'No response'}"
            )
            raise
    
    def call_with_messages(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Make a call with pre-formatted messages
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters
        
        Returns:
            The AI response as a string
        """
        extra_params = kwargs
        
        # Filter out system messages and handle them separately
        system_content = None
        user_messages = []
        
        for msg in messages:
            if msg.get('role') == 'system':
                system_content = msg.get('content', '')
            elif msg.get('role') in ['user', 'assistant']:
                user_messages.append(msg)
        
        payload = {
            "model": self.model,
            "max_tokens": extra_params.get("max_tokens", 1000),
            "temperature": extra_params.get("temperature", 0.7),
            "messages": user_messages
        }
        
        if system_content:
            payload["system"] = system_content
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'content' in data and len(data['content']) > 0:
                return data['content'][0]['text'].strip()
            else:
                raise ValueError(f"Unexpected response format: {data}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Anthropic API request failed: {e}")
            raise
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Invalid Anthropic API response: {e}")
            raise
    
    def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON from Claude's response, handling various formats
        
        Args:
            response: The raw response from Claude
            
        Returns:
            Parsed JSON as dictionary
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
                # Remove 'json' prefix if present
                if json_str.startswith("json"):
                    json_str = json_str[4:].strip()
            else:
                # Try to find JSON-like content
                json_str = response.strip()
            
            # Parse JSON
            return json.loads(json_str)
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to extract JSON from response: {e}")
            logger.warning(f"Response was: {response}")
            raise ValueError(f"Could not parse JSON from response: {e}")
    
    def call_for_json(
        self,
        system_prompt: str,
        user_message: str = "",
        extra_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make a call expecting JSON response and parse it
        
        Args:
            system_prompt: System prompt requesting JSON response
            user_message: User message
            extra_params: Additional parameters
            
        Returns:
            Parsed JSON response as dictionary
        """
        response = self.call(system_prompt, user_message, extra_params)
        return self.extract_json_from_response(response)


# Create default instance
try:
    anthropic_llm = AnthropicLLMService()
    logger.info("Anthropic LLM service initialized successfully")
except ValueError as e:
    logger.warning(f"Could not initialize Anthropic LLM service: {e}")
    anthropic_llm = None 