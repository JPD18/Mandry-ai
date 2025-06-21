#!/usr/bin/env python3
"""
Test the improved user flow for different profile scenarios
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mandry_ai.settings')

import django
django.setup()

from services.langgraph_service import visa_assistant_workflow
from django.contrib.auth.models import User
from visa.models import UserProfile

def test_user_flows():
    """Test different user flow scenarios"""
    
    print("🧪 Testing User Flow Scenarios\n")
    
    # Create test users
    try:
        # Scenario 1: Brand new user (empty profile)
        print("📋 Scenario 1: Brand New User (Empty Profile)")
        print("=" * 50)
        
        user1, created = User.objects.get_or_create(username='test_new_user', defaults={'email': 'new@test.com'})
        if not created:
            # Clear the profile to simulate new user
            profile1 = UserProfile.objects.get(user=user1)
            profile1.nationality = None
            profile1.visa_intent = None
            profile1.current_location = None
            profile1.conversation_insights = None
            profile1.context_sufficient = False
            profile1.save()
        
        result1 = visa_assistant_workflow.process_message(
            user_id=user1.id,
            message="Hello, I need help with visas"
        )
        
        print(f"Response: {result1['response']}")
        print(f"Next Step: {result1['current_step']}")
        print()
        
        # Scenario 2: User with partial info
        print("📋 Scenario 2: User with Partial Information")
        print("=" * 50)
        
        user2, created = User.objects.get_or_create(username='test_partial_user', defaults={'email': 'partial@test.com'})
        profile2, created = UserProfile.objects.get_or_create(user=user2)
        profile2.nationality = "American"  # Has nationality but no visa intent
        profile2.visa_intent = None
        profile2.current_location = None
        profile2.context_sufficient = False
        profile2.save()
        
        result2 = visa_assistant_workflow.process_message(
            user_id=user2.id,
            message="I want to work abroad"
        )
        
        print(f"Response: {result2['response']}")
        print(f"Next Step: {result2['current_step']}")
        print()
        
        # Scenario 3: User with complete context
        print("📋 Scenario 3: User with Complete Context")
        print("=" * 50)
        
        user3, created = User.objects.get_or_create(username='test_complete_user', defaults={'email': 'complete@test.com'})
        profile3, created = UserProfile.objects.get_or_create(user=user3)
        profile3.nationality = "Canadian"
        profile3.visa_intent = "Student visa"
        profile3.current_location = "Toronto"
        profile3.context_sufficient = True
        profile3.save()
        
        result3 = visa_assistant_workflow.process_message(
            user_id=user3.id,
            message="What documents do I need?"
        )
        
        print(f"Response: {result3['response']}")
        print(f"Next Step: {result3['current_step']}")
        print()
        
        print("✅ All scenarios tested successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_flows() 