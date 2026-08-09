import time
from ..config.logger import log
from typing import Callable, Any


def log_function(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that logs the execution time of a function.

    Args:
        func (Callable[..., Any]): The function to be decorated.

    Returns:
        Callable[..., Any]: The decorated function.
    """

    def wrapper(*args: Any, **kwargs: Any):
        log.bind(operation=func.__name__)
        log.info(f"start: {func.__name__}")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            log.info(f"end: {func.__name__} ({duration:.2f}s)")
            return result
        except Exception as e:
            log.error(f"Error in {func.__name__}: {str(e)}")
            raise

    return wrapper
