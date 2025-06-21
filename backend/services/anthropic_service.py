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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AnthropicLLMService:
    """Service for interacting with Anthropic's Claude API"""
    
    def __init__(self, api_key: str = None, model_name: str = None, timeout: int = 30):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model_name or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        self.timeout = timeout
        self.base_url = "https://api.anthropic.com/v1/messages"
        
        if not self.api_key:
            logger.warning("Could not initialize Anthropic LLM service: Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
            return
        
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
    
    def call(
        self,
        system_prompt: Optional[str] = None,
        user_message: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """High-level convenience wrapper for Anthropic chat-completion endpoints.

        Typical usage (legacy):
            call("You are…", "Hello")

        Advanced usage (new):
            messages = [...]
            call(extra_params={"messages": messages})

        If *extra_params* contains a pre-built ``messages`` list, that list will
        be sent *verbatim* and *system_prompt* / *user_message* are ignored.
        """
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")

        extra_params = extra_params or {}

        # If caller already built the full "messages" array, trust it.
        if "messages" in extra_params:
            payload = {
                "model": self.model,
                "max_tokens": extra_params.get("max_tokens", 1000),
                "temperature": extra_params.get("temperature", 0.7),
            }
            # Use the pre-built messages
            payload["messages"] = extra_params["messages"]
            
            # Handle system prompt if provided separately
            if "system" in extra_params:
                payload["system"] = extra_params["system"]
            elif system_prompt:
                payload["system"] = system_prompt
                
        else:
            # Legacy 2-string interface
            
            # Handle cases where user_message is None but system_prompt is present
            final_user_message = user_message
            final_system_prompt = system_prompt
            
            if not final_user_message and final_system_prompt:
                # Anthropic requires a user message to process a system prompt.
                # If no user message is given, we can treat the system prompt as the first user message.
                final_user_message = final_system_prompt
                final_system_prompt = None

            payload = {
                "model": self.model,
                "max_tokens": extra_params.get("max_tokens", 1000),
                "temperature": extra_params.get("temperature", 0.7),
                "messages": [
                    {"role": "user", "content": final_user_message or ""}
                ]
            }
            
            # Add system prompt if it exists
            if final_system_prompt:
                payload["system"] = final_system_prompt
            
            # Override with any extra params (but preserve messages structure)
            for key, value in extra_params.items():
                if key not in ["messages", "system"]:
                    payload[key] = value

        try:
            logger.info(f"Making request to Anthropic API with model: {self.model}")
            
            resp = requests.post(
                self.base_url, 
                json=payload, 
                headers=self.headers,
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Handle Anthropic API response format
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
                f"  Response: {resp.text if 'resp' in locals() else 'No response'}"
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
        Extract JSON from Anthropic's response, handling various formats
        
        Args:
            response: The raw response from Anthropic
            
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
            
            # Try to parse as JSON
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            logger.error(f"Response was: {response}")
            # Return a default structure
            return {"error": "Failed to parse JSON", "raw_response": response}
    
    def call_for_json(
        self,
        system_prompt: str,
        user_message: str = "",
        extra_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a call expecting JSON response from Anthropic
        
        Args:
            system_prompt: System prompt to set context
            user_message: User's message 
            extra_params: Additional parameters for the API call
        
        Returns:
            Parsed JSON as dictionary
        """
        extra_params = extra_params or {}
        
        # Enhance system prompt to request JSON
        json_system_prompt = f"{system_prompt}\n\nPlease respond with valid JSON only."
        
        response = self.call(
            system_prompt=json_system_prompt,
            user_message=user_message,
            extra_params=extra_params
        )
        
        return self.extract_json_from_response(response)


# Export a singleton for convenience
anthropic_llm = AnthropicLLMService()

# Create default instance
try:
    anthropic_llm = AnthropicLLMService()
    logger.info("Anthropic LLM service initialized successfully")
except ValueError as e:
    logger.warning(f"Could not initialize Anthropic LLM service: {e}")
    anthropic_llm = None 