import os
import logging
import tempfile
from typing import Dict, Any, Optional, Tuple
import io
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader
from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class DocumentProcessingException(APIException):
    """Custom exception for document processing errors"""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Document processing failed.'
    default_code = 'document_processing_error'


class DocumentService:
    """
    Service for processing documents - extracting text and validating content
    """
    
    # Supported file types
    SUPPORTED_PDF_TYPES = ['pdf']
    SUPPORTED_IMAGE_TYPES = ['png', 'jpg', 'jpeg']
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        
    def extract_text_from_file(self, file_obj, file_type: str) -> str:
        """
        Extract text from uploaded file based on file type
        Args:
            file_obj: Django uploaded file object
            file_type: string indicating file type (pdf, png, jpg, jpeg)
        Returns:
            str: Extracted text content
        """
        try:
            file_type = file_type.lower()
            
            # Check file size
            if hasattr(file_obj, 'size') and file_obj.size > self.max_file_size:
                raise DocumentProcessingException(
                    detail=f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB"
                )
            
            if file_type in self.SUPPORTED_PDF_TYPES:
                return self._extract_text_from_pdf(file_obj)
            elif file_type in self.SUPPORTED_IMAGE_TYPES:
                return self._extract_text_from_image(file_obj)
            else:
                raise DocumentProcessingException(
                    detail=f"Unsupported file type: {file_type}"
                )
                
        except DocumentProcessingException:
            raise
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise DocumentProcessingException(
                detail=f"Failed to extract text: {str(e)}"
            )
    
    def _extract_text_from_pdf(self, file_obj) -> str:
        """Extract text from PDF file"""
        try:
            # Read PDF content
            pdf_reader = PdfReader(file_obj)
            text_content = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                    continue
            
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                raise DocumentProcessingException(
                    detail="No readable text found in PDF"
                )
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text.strip()
            
        except DocumentProcessingException:
            raise
        except Exception as e:
            logger.error(f"PDF text extraction error: {str(e)}")
            raise DocumentProcessingException(
                detail="Failed to process PDF file"
            )
    
    def _extract_text_from_image(self, file_obj) -> str:
        """Extract text from image using OCR"""
        try:
            # Open image
            image = Image.open(file_obj)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            try:
                extracted_text = pytesseract.image_to_string(image, lang='eng')
            except Exception as e:
                # Fallback if tesseract is not installed or configured
                logger.warning(f"OCR extraction failed: {str(e)}")
                raise DocumentProcessingException(
                    detail="OCR processing unavailable. Please ensure text is machine-readable."
                )
            
            if not extracted_text.strip():
                raise DocumentProcessingException(
                    detail="No readable text found in image"
                )
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from image")
            return extracted_text.strip()
            
        except DocumentProcessingException:
            raise
        except Exception as e:
            logger.error(f"Image text extraction error: {str(e)}")
            raise DocumentProcessingException(
                detail="Failed to process image file"
            )
    
    def validate_document_with_llm(self, extracted_text: str, document_type: str = "document") -> Dict[str, Any]:
        """
        Use LLM to validate if the extracted text appears to be a valid document
        Args:
            extracted_text: The text content extracted from the document
            document_type: Type of document being validated (for context)
        Returns:
            Dict containing validation result and reasoning
        """
        from services.llm_service import default_llm
        
        try:
            # Truncate text if too long (keep first 2000 chars for validation)
            text_for_validation = extracted_text[:2000] if len(extracted_text) > 2000 else extracted_text
            
            validation_prompt = f"""You are a document validation expert. Analyze the following text extracted from a {document_type} and determine if it appears to be a valid, readable document.

VALIDATION CRITERIA:
1. Does the text contain coherent, meaningful content?
2. Is the text properly formatted and readable?
3. Does it appear to be a legitimate document (not gibberish or corrupted)?
4. Is there sufficient content to be considered a valid document?

TEXT TO VALIDATE:
{text_for_validation}

INSTRUCTIONS:
- Respond with ONLY a JSON object
- Include "is_valid" (true/false) and "reason" (brief explanation)
- Keep the reason concise and helpful
- Example: {{"is_valid": true, "reason": "Document contains coherent text with proper structure"}}

Response:"""

            response = default_llm.call(
                validation_prompt,
                "",
                extra_params={
                    "max_tokens": 150,
                    "temperature": 0.1  # Low temperature for consistent validation
                }
            )
            
            # Parse LLM response
            try:
                import json
                result = json.loads(response.strip())
                
                # Validate response format
                if not isinstance(result, dict) or 'is_valid' not in result:
                    raise ValueError("Invalid response format")
                
                # Ensure boolean type for is_valid
                result['is_valid'] = bool(result.get('is_valid', False))
                result['reason'] = result.get('reason', 'No reason provided')
                
                logger.info(f"Document validation completed: {result['is_valid']} - {result['reason']}")
                return result
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse LLM validation response: {response}, error: {str(e)}")
                # Fallback validation based on text length and basic checks
                return self._fallback_validation(extracted_text)
                
        except Exception as e:
            logger.error(f"LLM validation failed: {str(e)}")
            # Fallback to basic validation
            return self._fallback_validation(extracted_text)
    
    def _fallback_validation(self, text: str) -> Dict[str, Any]:
        """Fallback validation when LLM is unavailable"""
        text_length = len(text.strip())
        
        # Basic validation criteria
        if text_length < 50:
            return {
                "is_valid": False,
                "reason": "Document contains insufficient text content"
            }
        
        # Check for mostly non-alphabetic characters (might indicate OCR errors)
        alphabetic_chars = sum(1 for c in text if c.isalpha())
        if alphabetic_chars / len(text) < 0.3:
            return {
                "is_valid": False,
                "reason": "Document appears to contain corrupted or unreadable text"
            }
        
        return {
            "is_valid": True,
            "reason": "Document appears to contain valid text content"
        }
    
    def process_document(self, file_obj, file_type: str, document_type: str = "document") -> Dict[str, Any]:
        """
        Complete document processing pipeline:
        1. Extract text from file
        2. Validate with LLM
        3. Return results
        
        Args:
            file_obj: Django uploaded file object
            file_type: string indicating file type
            document_type: type of document for context
            
        Returns:
            Dict with extracted_text, validation_result, and metadata
        """
        try:
            # Step 1: Extract text
            logger.info(f"Starting document processing for {file_type} file")
            extracted_text = self.extract_text_from_file(file_obj, file_type)
            
            # Step 2: Validate with LLM
            validation_result = self.validate_document_with_llm(extracted_text, document_type)
            
            # Step 3: Prepare response
            result = {
                "extracted_text": extracted_text,
                "validation": validation_result,
                "metadata": {
                    "file_type": file_type,
                    "document_type": document_type,
                    "text_length": len(extracted_text),
                    "processing_successful": True
                }
            }
            
            logger.info(f"Document processing completed successfully. Valid: {validation_result['is_valid']}")
            return result
            
        except DocumentProcessingException:
            raise
        except Exception as e:
            logger.error(f"Document processing pipeline failed: {str(e)}")
            raise DocumentProcessingException(
                detail=f"Processing failed: {str(e)}"
            )


# Create default instance for easy import
default_document_service = DocumentService() 