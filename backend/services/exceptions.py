from __future__ import annotations

"""Centralised exception hierarchy for service layer.

Creating a common base allows the API layer to treat all service
failures uniformly (e.g. catching ``ServiceException``) while keeping
service-specific subclasses for granular logging / HTTP status codes.
"""
from rest_framework import status
from rest_framework.exceptions import APIException


class ServiceException(APIException):
    """Top-level parent for all service errors."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal service error."
    default_code = "service_error"


# Concrete subclasses can override only what differs.

class SearchServiceException(ServiceException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Search service temporarily unavailable."
    default_code = "search_service_error"


class DocumentServiceException(ServiceException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Document processing failed."
    default_code = "document_processing_error"


class ScheduleServiceException(ServiceException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Schedule service operation failed."
    default_code = "schedule_service_error" 