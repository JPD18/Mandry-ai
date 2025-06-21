# services/llm.py
import os
import logging
import requests
from typing import List, Dict, Any, Union, Optional

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self,
                 base_url: Optional[str] = None,
                 model_name: Optional[str] = None,
                 timeout: int = 20):
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions")
        self.model = model_name or os.getenv("OLLAMA_MODEL", "gemma3")
        self.timeout = timeout
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def call(
        self,
        system_prompt: Optional[str] = None,
        user_message: Optional[str] = None,
        extra_params: Optional[Dict[str, Any]] = Ngione,
    ) -> str:
        """High-level convenience wrapper for chat-completion endpoints.

        Typical usage (legacy):
            call("You are…", "Hello")

        Advanced usage (new):
            messages = [...]
            call(extra_params={"messages": messages})

        If *extra_params* contains a pre-built ``messages`` list, that list will
        be sent *verbatim* and *system_prompt* / *user_message* are ignored.
        """

        extra_params = extra_params or {}

        # If caller already built the full "messages" array, trust it.
        if "messages" in extra_params:
            payload = {
                "model": self.model,
                "stream": False,
            }
            # Avoid accidental duplication of model/stream keys from extra_params
            payload.update(extra_params)
        else:
            # Legacy 2-string interface
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt or ""},
                    {"role": "user", "content": user_message or ""},
                ],
                "temperature": 0.9,
                "max_tokens": 100,
                "presence_penalty": 0.4,
                "frequency_penalty": 0.8,
                "stream": False,
            }
            # Additional OpenAI params (temperature, etc.)
            payload.update(extra_params)

        try:
            resp = requests.post(
                self.base_url, 
                json=payload, 
                headers=self.headers,
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Handle Ollama API response format
            if "message" in data:
                # Direct message response
                return data["message"]["content"].strip()
            elif "choices" in data and len(data["choices"]) > 0:
                # OpenAI-compatible format
                return data["choices"][0]["message"]["content"].strip()
            else:
                raise ValueError(f"Unexpected response format from Ollama API: {data}")
                
        except requests.exceptions.RequestException as e:
            logger.error(
                f"LLMService ➔ Request failed: {e}\n"
                f"  URL:    {self.base_url}\n"
                f"  MODEL:  {self.model}\n"
                f"  Payload:{payload}"
            )
            raise
        except (KeyError, ValueError) as e:
            logger.error(
                f"LLMService ➔ Invalid response format: {e}\n"
                f"  URL:    {self.base_url}\n"
                f"  MODEL:  {self.model}\n"
                f"  Payload:{payload}"
            )
            raise

# you can export a singleton for convenience
default_llm = LLMService() 