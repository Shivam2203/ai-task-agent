"""
Logging configuration using structlog for structured logging.

Provides consistent logging across the application with JSON formatting
for production and human-readable formatting for development.
"""
import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add application context to log entries.
    
    Args:
        logger: Logger instance
        method_name: Name of the logging method
        event_dict: Event dictionary
        
    Returns:
        Updated event dictionary with app context
    """
    event_dict["app"] = "ai-task-agent"
    return event_dict


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )
    
    # Define processors for structlog
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]
    
    # Add appropriate renderer based on environment
    if sys.stderr.isatty():
        # Development: human-readable console output
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Production: JSON output
        processors.append(structlog.processors.JSONRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Create logger instance
logger = structlog.get_logger()


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)

# Made with Bob
