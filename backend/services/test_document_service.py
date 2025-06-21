"""
Test/Demo file for Document Service
This file demonstrates how to use the document processing service
"""

import os
import sys
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO

# Add the parent directory to the path so we can import Django modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mandry_ai.settings')
django.setup()

from services.document_service import default_document_service, DocumentProcessingException


def test_document_service():
    """
    Simple test function to demonstrate document service usage
    """
    print("Document Service Test Demo")
    print("=" * 50)
    
    # Test 1: Validate a simple text
    print("\n1. Testing text validation:")
    test_text = "This is a valid document with proper content and structure. It contains meaningful information."
    try:
        validation_result = default_document_service.validate_document_with_llm(test_text, "test document")
        print(f"   Text: '{test_text[:50]}...'")
        print(f"   Valid: {validation_result['is_valid']}")
        print(f"   Reason: {validation_result['reason']}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 2: Validate invalid text
    print("\n2. Testing invalid text validation:")
    invalid_text = "asd123!@#$%^&*()"
    try:
        validation_result = default_document_service.validate_document_with_llm(invalid_text, "test document")
        print(f"   Text: '{invalid_text}'")
        print(f"   Valid: {validation_result['is_valid']}")
        print(f"   Reason: {validation_result['reason']}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 3: Simulate file processing (without actual file)
    print("\n3. Testing supported file types:")
    supported_types = default_document_service.SUPPORTED_PDF_TYPES + default_document_service.SUPPORTED_IMAGE_TYPES
    print(f"   Supported file types: {', '.join(supported_types)}")
    
    print("\n4. Testing file size limits:")
    print(f"   Maximum file size: {default_document_service.max_file_size // (1024*1024)}MB")
    
    print("\nDocument Service Test Complete!")
    print("=" * 50)


def demo_usage():
    """
    Demo showing typical usage patterns
    """
    print("\nDocument Service Usage Examples")
    print("=" * 50)
    
    print("""
# Example 1: Basic text validation
from services.document_service import default_document_service

text = "Your document text here..."
result = default_document_service.validate_document_with_llm(text, "passport")
is_valid = result['is_valid']
reason = result['reason']

# Example 2: Complete document processing (in Django view)
def process_document_view(request):
    uploaded_file = request.FILES['file']
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    result = default_document_service.process_document(
        uploaded_file, 
        file_type, 
        "visa_document"
    )
    
    return JsonResponse({
        'valid': result['validation']['is_valid'],
        'reason': result['validation']['reason'],
        'text': result['extracted_text']
    })

# Example 3: Text extraction only
text = default_document_service.extract_text_from_file(file_obj, 'pdf')

# Example 4: Validation only (if you already have text)
validation = default_document_service.validate_document_with_llm(text, 'document')
""")


if __name__ == "__main__":
    try:
        test_document_service()
        demo_usage()
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc() 