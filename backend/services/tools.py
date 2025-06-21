from __future__ import annotations

"""Lightweight wrappers that expose core capabilities as plain
Python functions returning JSON-serialisable data.  These functions
are intentionally free of Django models and side-effects so they can
be registered directly as LangGraph tools in the future.
"""

from typing import List, Dict, Any

from .search_service import default_search_service
from .document_service import default_document_service
from .schedule_service import default_schedule_service

# ----------------------------------------------------------------------------
# Search / RAG tools
# ----------------------------------------------------------------------------

def tool_valyu_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Perform Valyu search and return a list of normalised results."""
    return default_search_service.valyu_search(query, top_k)


def tool_get_rag_context(question: str, max_sources: int = 3) -> str:
    """Return a formatted context block derived from official sources suitable for LLM prompts."""
    return default_search_service.get_rag_context(question, max_sources)

# ----------------------------------------------------------------------------
# Document processing tools
# ----------------------------------------------------------------------------

def tool_validate_document_text(text: str, document_type: str = "document") -> Dict[str, Any]:
    """Validate arbitrary text content using the LLM-based validator."""
    return default_document_service.validate_document_with_llm(text, document_type)

# We do not want to persist the original file; callers should read the file
# content themselves and pass it in as bytes if required.

def tool_process_document(file_bytes: bytes, filename: str, document_type: str = "document") -> Dict[str, Any]:
    """End-to-end document processing from raw bytes.

    NOTE: The file content is never written to disk – it is handled fully
    in-memory to honour the no-storage policy.
    """
    import io, os
    ext = os.path.splitext(filename)[1].lstrip('.').lower()
    file_obj = io.BytesIO(file_bytes)
    return default_document_service.process_document(file_obj, ext, document_type=document_type)

# ----------------------------------------------------------------------------
# Scheduling tools
# ----------------------------------------------------------------------------

def tool_create_reminder(user_id: int, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create reminders for a given user (caller must ensure auth)."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)
    return default_schedule_service.create_reminder(user, reminder_data)


def tool_get_due_reminders(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch reminders whose reminder_date is in the past and email not yet sent."""
    return default_schedule_service.get_due_reminders(limit)


def tool_process_due_reminders() -> Dict[str, Any]:
    """Process and send any reminders due as of now."""
    return default_schedule_service.process_due_reminders() 