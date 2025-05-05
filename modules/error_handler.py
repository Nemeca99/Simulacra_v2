from typing import Callable, TypeVar, Any, Optional
from functools import wraps
import traceback
from datetime import datetime

from modules.logger import logger

T = TypeVar('T')

class GameError(Exception):
    """Base class for game-specific exceptions"""
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ConfigError(GameError):
    """Configuration related errors"""
    pass

class ValidationError(GameError):
    """Data validation errors"""
    pass

def handle_error(error: Exception, context: str = "") -> None:
    """Central error handling function"""
    if isinstance(error, GameError):
        logger.error(f"{context}: {error.message}")
        if hasattr(error, 'code') and error.code:
            logger.debug(f"Error code: {error.code}")
    else:
        logger.error(f"Unexpected error in {context}: {str(error)}")

def handle_errors(
    default_return: Any = None,
    log_level: str = "error",
    include_stack: bool = True,
    silent: bool = False
) -> Callable:
    """Enhanced error handling decorator with stack traces"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not silent:
                    log_func = getattr(logger, log_level, logger.error)
                    error_msg = f"{func.__name__} failed: {str(e)}"
                    if include_stack:
                        stack_trace = traceback.format_exc()
                        error_msg = f"{error_msg}\nStack trace:\n{stack_trace}"
                    log_func(error_msg)
                return default_return
        return wrapper
    return decorator

def safe_operation(operation: Callable[..., T]) -> Optional[T]:
    """Context manager for safe operation execution"""
    try:
        return operation()
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        return None