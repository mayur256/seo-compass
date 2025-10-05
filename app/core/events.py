"""Event definitions for structured logging."""

from enum import Enum


class ReportEvent(str, Enum):
    """Report lifecycle events."""
    VERSION_CREATED = "version_created"
    PACKAGING_STARTED = "packaging_started"
    PACKAGING_COMPLETED = "packaging_completed"
    UPLOAD_SUCCESS = "upload_success"
    UPLOAD_FAILED = "upload_failed"
    PRESIGNED_URL_GENERATED = "presigned_url_generated"