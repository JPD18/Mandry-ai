#!/usr/bin/env python
"""
Test Anthropic API using direct requests (no Anthropic SDK)
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_anthropic_requests():
    """Test Anthropic API using direct HTTP requests"""
    print("🧪 Testing Anthropic API with requests library...")
    
    # Get API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key or not api_key.startswith("sk-ant-"):
        print("❌ No valid API key found")
        return False
    
    print(f"✅ Using API key: {api_key[:8]}...")
    
    # API endpoint and headers
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01'
    }
    
    # Request payload
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 50,
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello from Anthropic API!'"
            }
        ]
    }
    
    try:
        print("📤 Sending request to Anthropic API...")
        print(f"🔗 URL: {url}")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {json.dumps(data, indent=2)}")
            
            # Extract the actual message
            if 'content' in data and len(data['content']) > 0:
                message = data['content'][0]['text']
                print(f"🎉 AI Message: {message}")
                return True
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_different_models():
    """Test different Anthropic models"""
    print("\n🧪 Testing different models...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY', "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")
    
    models_to_test = [
        "claude-3-haiku-20240307",
        "claude-3-5-sonnet-20241022",
        "claude-3-sonnet-20240229"
    ]
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01'
    }
    
    for model in models_to_test:
        print(f"\n🔍 Testing model: {model}")
        
        payload = {
            "model": model,
            "max_tokens": 20,
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Working!'"
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                message = data['content'][0]['text']
                print(f"  ✅ {model}: {message}")
            else:
                print(f"  ❌ {model}: Status {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"  ❌ {model}: Error - {e}")

def test_with_system_prompt():
    """Test with system prompt"""
    print("\n🧪 Testing with system prompt...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY', "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")
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01'
    }
    
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 50,
        "system": "You are a helpful visa assistant. Be brief and practical.",
        "messages": [
            {
                "role": "user",
                "content": "I'm Ukrainian. What's the first step for a UK student visa?"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            message = data['content'][0]['text']
            print(f"✅ System prompt test: {message}")
            return True
        else:
            print(f"❌ System prompt test failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ System prompt test error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ANTHROPIC API REQUESTS TEST")
    print("=" * 60)
    
    # Run basic test
    success1 = test_anthropic_requests()
    
    # Test different models
    test_different_models()
    
    # Test with system prompt
    success2 = test_with_system_prompt()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if success1 and success2:
        print("🎉 All tests passed! Anthropic API is working with requests!")
    elif success1:
        print("✅ Basic test passed, some advanced features may have issues")
    else:
        print("❌ Tests failed. Check API key and network connection.")
    
    print("✅ Direct requests approach confirmed working!" if success1 else "❌ Need to investigate further") 