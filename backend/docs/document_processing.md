# Document Processing Service

A modular document upload and text extraction system that processes documents without storing them, extracts text content, and validates documents using LLM.

## Features

- ✅ **Document Upload & Processing**: Upload PDF, PNG, JPG, JPEG files
- ✅ **Text Extraction**: Extract text from PDFs and images (OCR)
- ✅ **LLM Validation**: AI-powered document validation
- ✅ **No Storage**: Documents are processed in memory only
- ✅ **Modular Design**: Easy to extend and maintain
- ✅ **Error Handling**: Comprehensive error handling and fallbacks

## API Endpoints

### 1. Process Document
**POST** `/api/process-document/`

Process an uploaded document, extract text, and validate it.

**Request:**
```javascript
// Form data
{
  "file": <file_object>,
  "document_type": "passport" // Optional, defaults to "document"
}
```

**Response:**
```json
{
  "is_valid": true,
  "reason": "Document contains coherent text with proper structure",
  "extracted_text": "Full text content extracted from the document...",
  "metadata": {
    "file_type": "pdf",
    "document_type": "passport",
    "text_length": 1234,
    "processing_successful": true
  },
  "processing_successful": true
}
```

### 2. Validate Text
**POST** `/api/validate-text/`

Validate text content using LLM without file upload.

**Request:**
```json
{
  "text": "Your text content here...",
  "document_type": "visa_document" // Optional
}
```

**Response:**
```json
{
  "is_valid": true,
  "reason": "Document contains coherent text with proper structure"
}
```

## Supported File Types

- **PDF**: `.pdf` - Text extraction using PyPDF2
- **Images**: `.png`, `.jpg`, `.jpeg` - OCR using Tesseract

## File Size Limits

- Maximum file size: **10MB**
- Larger files will be rejected with an error

## Usage Examples

### JavaScript Frontend
```javascript
// Process document
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('document_type', 'passport');

const response = await fetch('/api/process-document/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${userToken}`
  },
  body: formData
});

const result = await response.json();
if (result.is_valid) {
  console.log('Document is valid:', result.reason);
  console.log('Extracted text:', result.extracted_text);
} else {
  console.log('Document is invalid:', result.reason);
}
```

### Python Backend Usage
```python
from services.document_service import default_document_service

# Process complete document
result = default_document_service.process_document(
    file_obj, 
    'pdf', 
    'visa_document'
)

# Just extract text
text = default_document_service.extract_text_from_file(file_obj, 'pdf')

# Just validate text
validation = default_document_service.validate_document_with_llm(
    text, 
    'passport'
)
```

## Architecture

### Service Layer (`services/document_service.py`)
- **DocumentService**: Main service class
- **Text Extraction**: PDF and image processing
- **LLM Validation**: AI-powered document validation
- **Error Handling**: Custom exceptions and fallbacks

### API Layer (`visa/views.py`)
- **process_document**: Complete document processing endpoint
- **validate_text**: Text-only validation endpoint
- Authentication required (Token-based)

### Exception Handling
- **DocumentProcessingException**: Custom exception for processing errors
- **Fallback Validation**: Basic validation when LLM is unavailable
- **Graceful Degradation**: Service continues working even if OCR fails

## Configuration

### Required Dependencies
```python
# requirements.txt
PyPDF2==3.0.1      # PDF text extraction
pytesseract==0.3.10 # OCR for images
Pillow==10.1.0      # Image processing
```

### Tesseract Installation
For OCR functionality, install Tesseract:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/tesseract-ocr/tesseract

**macOS:**
```bash
brew install tesseract
```

## Error Responses

### File Upload Errors
```json
{
  "error": "Only PDF, PNG, and JPG files are allowed",
  "processing_successful": false
}
```

### Processing Errors
```json
{
  "error": "No readable text found in PDF",
  "processing_successful": false
}
```

### Size Limit Errors
```json
{
  "error": "File too large. Maximum size is 10MB",
  "processing_successful": false
}
```

## Extending the Service

### Adding New File Types
```python
class DocumentService:
    SUPPORTED_NEW_TYPES = ['docx', 'txt']
    
    def _extract_text_from_docx(self, file_obj):
        # Implementation for DOCX files
        pass
```

### Custom Validation Logic
```python
def validate_specific_document_type(self, text: str, doc_type: str):
    # Custom validation logic for specific document types
    if doc_type == 'passport':
        # Passport-specific validation
        pass
```

## Testing

Run the test demo:
```bash
cd backend
python services/test_document_service.py
```

## Security Considerations

- Documents are **never stored** on disk
- All processing happens in memory
- Files are validated before processing
- Size limits prevent DoS attacks
- Authentication required for all endpoints

## Performance Notes

- PDF processing: Very fast, direct text extraction
- Image OCR: Slower, depends on image quality and size
- LLM validation: Moderate, uses local LLM service
- Memory usage: Temporary, files not stored

## Troubleshooting

### OCR Not Working
- Install Tesseract OCR
- Check image quality and resolution
- Ensure text is clearly readable in images

### LLM Validation Failing
- Check if LLM service is running
- Service falls back to basic validation
- Check logs for specific error messages

### Large Files Failing
- Check file size (10MB limit)
- For larger files, consider chunking or compression 