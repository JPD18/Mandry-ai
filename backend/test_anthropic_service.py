#!/usr/bin/env python3
"""
Test the new AnthropicLLMService to ensure it works correctly
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.anthropic_service import AnthropicLLMService

def test_anthropic_service():
    print("Testing AnthropicLLMService...")
    
    # Initialize service
    service = AnthropicLLMService()
    
    if not service.api_key:
        print("❌ No API key found. Please set ANTHROPIC_API_KEY environment variable.")
        return False
    
    print(f"✅ Service initialized with model: {service.model}")
    
    try:
        # Test simple call
        print("\n🧪 Testing simple call...")
        response = service.call(
            system_prompt="You are a helpful assistant.",
            user_message="Say hello in one sentence."
        )
        print(f"✅ Response: {response}")
        
        # Test JSON call
        print("\n🧪 Testing JSON call...")
        json_response = service.call_for_json(
            system_prompt="You are a helpful assistant that responds in JSON format.",
            user_message="Create a simple greeting object with 'message' and 'language' fields."
        )
        print(f"✅ JSON Response: {json_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_anthropic_service()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
        sys.exit(1) 