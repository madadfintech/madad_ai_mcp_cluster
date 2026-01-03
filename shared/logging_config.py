"""
Structured logging configuration - Fixed circular import
"""
import structlog
import logging
import sys
import os

# Use os.getenv directly to avoid circular import with config
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "console").lower()

_logging_configured = False

def setup_logging():
    """Configure structured logging for the entire application"""
    global _logging_configured
    
    if _logging_configured:
        return
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, LOG_LEVEL, logging.INFO)
    )
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    _logging_configured = True

def get_logger(name: str):
    """Get a structured logger instance"""
    if not _logging_configured:
        setup_logging()
    return structlog.get_logger(name)