import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from app.core.config import settings

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Convert string log level to logging constant
def get_log_level(level_str: str) -> int:
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    return level_map.get(level_str.upper(), logging.INFO)

# Configure logging
def setup_logging():
    # Get log levels from settings
    file_level = get_log_level(settings.LOG_FILE_LEVEL)
    console_level = get_log_level(settings.LOG_CONSOLE_LEVEL)
    root_level = get_log_level(settings.LOG_LEVEL)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create handlers
    # Daily rotating file handler for all logs
    daily_handler = logging.handlers.TimedRotatingFileHandler(
        filename=logs_dir / "app.log",
        when="midnight",
        interval=1,
        backupCount=30,  # Keep 30 days of logs  For unlimited retention put it to 0
        encoding="utf-8"
    )
    daily_handler.setLevel(file_level)
    daily_handler.setFormatter(detailed_formatter)

    # Error log handler
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=logs_dir / "error.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(simple_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(root_level)
    root_logger.addHandler(daily_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    # FastAPI logger
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(file_level)

    # SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.setLevel(logging.WARNING)

    # Uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(file_level)

    # Custom app logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(file_level)

    return app_logger

# Create logger instance
logger = setup_logging()

# Custom exception logging decorator
def log_exceptions(func):
    """Decorator to log exceptions in async functions"""
    import functools
    import traceback
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Exception in {func.__name__}: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise
    
    return wrapper

# Custom exception logging decorator for sync functions
def log_exceptions_sync(func):
    """Decorator to log exceptions in sync functions"""
    import functools
    import traceback
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Exception in {func.__name__}: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise
    
    return wrapper 