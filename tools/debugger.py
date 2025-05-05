from functools import wraps
import inspect
import traceback
from typing import Any, Callable
import logging

logger = logging.getLogger('debug')


def debug_method(func: Callable) -> Callable:

    @wraps(func)
    def wrapper(*args, **kwargs):
        call_args = inspect.signature(func).bind(*args, **kwargs)
        call_args.apply_defaults()

        logger.debug(
            f"Calling {func.__name__} with args: {dict(call_args.arguments)}"
        )

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(
                f"Error in {func.__name__}: {e}\n{traceback.format_exc()}"
            )
            raise

    return wrapper
