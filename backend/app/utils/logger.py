import logging
import sys
from typing import Optional

from app.core.config import settings

def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """Setup application logging configuration."""
    
    log_level = level or settings.log_level
    log_format = format_string or (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        stream=sys.stdout
    )
    
    # Configure specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)
