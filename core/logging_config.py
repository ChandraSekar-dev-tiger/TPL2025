import logging
import sys
from typing import Optional

def setup_logging(log_level: Optional[str] = "INFO") -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: The logging level to use (default: INFO)
    """
    # Create a formatter that includes timestamp, level, and message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add our console handler
    root_logger.addHandler(console_handler)

    # Set up specific loggers for our modules
    loggers = [
        'agents',
        'pipelines',
        'core',
        'prompts'
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))
        # Don't propagate to root logger to avoid duplicate messages
        logger.propagate = False
        logger.addHandler(console_handler) 