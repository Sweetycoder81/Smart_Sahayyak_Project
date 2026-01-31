"""
Logging utility for TriSense AI
Centralized logging configuration and utilities
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional

def setup_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Setup and configure logger for TriSense AI modules
    
    Args:
        name: Logger name (usually module name)
        log_level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional - create logs directory if needed)
    try:
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, f'trisense_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get existing logger or create new one"""
    return logging.getLogger(name)

class LoggerMixin:
    """Mixin class to add logging capability to other classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger

def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """Log exception with context information"""
    error_msg = f"{context}: {type(exception).__name__}: {str(exception)}"
    logger.error(error_msg, exc_info=True)

def log_system_info(logger: logging.Logger):
    """Log system information for debugging"""
    import platform
    import sys
    
    logger.info("=== System Information ===")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info("=== End System Info ===")
