"""Structured logging utilities for production-ready API clients."""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class StructuredLogger:
    """
    Structured logger that outputs JSON-formatted logs.
    
    Perfect for:
    - Production debugging
    - Log aggregation systems (ELK, DataDog, etc.)
    - Request tracing
    
    Usage:
        logger = StructuredLogger(name="ai_client")
        logger.log_request(
            request_id="req_123",
            url="https://api.example.com/chat",
            method="POST",
            status=200,
            latency_ms=234.5
        )
    """
    
    def __init__(self, name: str = "ai_utils", level: int = logging.INFO):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create console handler with JSON formatting
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def _format_log(self, **kwargs) -> str:
        """Format log entry as JSON string."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs
        }
        return json.dumps(log_entry, default=str)
    
    def log_request(
        self,
        request_id: str,
        url: str,
        method: str = "GET",
        status: Optional[int] = None,
        latency_ms: Optional[float] = None,
        error: Optional[str] = None,
        **extra
    ):
        """
        Log an API request with structured data.
        
        Args:
            request_id: Unique request identifier
            url: Request URL
            method: HTTP method
            status: HTTP status code
            latency_ms: Request latency in milliseconds
            error: Error message if request failed
            **extra: Additional fields to include
        """
        log_data = {
            "event": "api_request",
            "request_id": request_id,
            "url": url,
            "method": method,
            **extra
        }
        
        if status is not None:
            log_data["status"] = status
        
        if latency_ms is not None:
            log_data["latency_ms"] = round(latency_ms, 2)
        
        if error:
            log_data["error"] = error
            self.logger.error(self._format_log(**log_data))
        else:
            self.logger.info(self._format_log(**log_data))
    
    def log_retry(
        self,
        request_id: str,
        attempt: int,
        max_attempts: int,
        error: str,
        delay_seconds: float
    ):
        """
        Log a retry attempt.
        
        Args:
            request_id: Unique request identifier
            attempt: Current attempt number
            max_attempts: Maximum number of attempts
            error: Error that triggered retry
            delay_seconds: Delay before next retry
        """
        log_data = {
            "event": "retry_attempt",
            "request_id": request_id,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "error": error,
            "delay_seconds": delay_seconds
        }
        self.logger.warning(self._format_log(**log_data))
    
    def log_rate_limit(self, request_id: str, wait_time_seconds: float):
        """
        Log rate limiting event.
        
        Args:
            request_id: Unique request identifier
            wait_time_seconds: Time waited due to rate limiting
        """
        log_data = {
            "event": "rate_limited",
            "request_id": request_id,
            "wait_time_seconds": round(wait_time_seconds, 3)
        }
        self.logger.info(self._format_log(**log_data))
    
    def info(self, message: str, **extra):
        """Log info message with optional structured data."""
        self.logger.info(self._format_log(event="info", message=message, **extra))
    
    def warning(self, message: str, **extra):
        """Log warning message with optional structured data."""
        self.logger.warning(self._format_log(event="warning", message=message, **extra))
    
    def error(self, message: str, **extra):
        """Log error message with optional structured data."""
        self.logger.error(self._format_log(event="error", message=message, **extra))


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return f"req_{uuid.uuid4().hex[:12]}"

