# -*- coding: utf-8 -*-
"""
FreeCAD CLI - Decorators and Utilities
=====================================

Provides decorators and utility functions to reduce code duplication.
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('freecad_cli')


def requires_freecad(func: Callable) -> Callable:
    """
    Decorator: Ensures FreeCAD is available, otherwise returns mock result

    Usage:
        @requires_freecad
        def my_function(wrapper, ...):
            # Logic when FreeCAD is available
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from .freecad_integration import FREECAD_AVAILABLE, FreeCADWrapper

        # Check if wrapper parameter was passed
        wrapper_instance = kwargs.get('wrapper') or (args[0] if args and isinstance(args[0], FreeCADWrapper) else None)

        if not FREECAD_AVAILABLE:
            logger.debug(f"FreeCAD not available, returning mock result: {func.__name__}")
            # Return mock result
            return {
                "success": True,
                "mock": True,
                "function": func.__name__,
                "message": "FreeCAD not installed - returning mock data"
            }

        return func(*args, **kwargs)

    return wrapper


def log_operation(operation_name: str = None):
    """
    Decorator: Log operation

    Usage:
        @log_operation("Create part")
        def create_part(...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            logger.info(f"Starting operation: {op_name}")

            try:
                result = func(*args, **kwargs)

                if isinstance(result, dict):
                    if result.get('success'):
                        logger.info(f"Operation succeeded: {op_name}")
                    else:
                        logger.warning(f"Operation failed: {op_name} - {result.get('error', 'Unknown error')}")

                return result
            except Exception as e:
                logger.error(f"Operation exception: {op_name} - {str(e)}")
                raise

        return wrapper
    return decorator


def handle_errors(default_return: Any = None, error_key: str = "error"):
    """
    Decorator: Unified error handling

    Usage:
        @handle_errors(default_return={}, error_key="error")
        def risky_operation(...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Function {func.__name__} execution error: {str(e)}")
                if isinstance(default_return, dict):
                    return {
                        "success": False,
                        error_key: str(e),
                        "function": func.__name__
                    }
                return default_return

        return wrapper
    return decorator


def validate_params(**param_validators):
    """
    Decorator: Parameter validation

    Usage:
        @validate_params(
            name=str,
            length=(float, lambda x: x > 0),
            count=int
        )
        def create_object(name, length, count):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for param_name, validator in param_validators.items():
                if param_name in kwargs:
                    value = kwargs[param_name]

                    # Support type validation
                    if isinstance(validator, type):
                        if not isinstance(value, validator):
                            return {
                                "success": False,
                                "error": f"Parameter {param_name} type error, expected {validator.__name__}",
                                "received_type": type(value).__name__
                            }

                    # Support tuple (type, validation function)
                    elif isinstance(validator, tuple) and len(validator) == 2:
                        expected_type, validator_fn = validator
                        if not isinstance(value, expected_type):
                            return {
                                "success": False,
                                "error": f"Parameter {param_name} type error"
                            }
                        if not validator_fn(value):
                            return {
                                "success": False,
                                "error": f"Parameter {param_name} validation failed"
                            }

            return func(*args, **kwargs)

        return wrapper
    return decorator


class OperationTimer:
    """Operation timer context manager"""

    def __init__(self, operation_name: str, log_result: bool = True):
        self.operation_name = operation_name
        self.log_result = log_result
        self.start_time = None
        self.result = None

    def __enter__(self):
        import time
        self.start_time = time.time()
        logger.debug(f"Starting timer: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start_time

        if exc_type is None:
            logger.info(f"[{elapsed:.3f}s] {self.operation_name} completed")
        else:
            logger.error(f"[{elapsed:.3f}s] {self.operation_name} failed: {exc_val}")

        return False  # Don't swallow exceptions

    def set_result(self, result: Any):
        """Set result"""
        self.result = result


def retry_on_failure(max_attempts: int = 3, delay: float = 0.1):
    """
    Decorator: Retry on failure

    Usage:
        @retry_on_failure(max_attempts=3, delay=0.5)
        def unreliable_operation(...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time

            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}), "
                            f"retrying in {delay}s: {str(e)}"
                        )
                        time.sleep(delay)

            logger.error(f"{func.__name__} final failure: {str(last_error)}")
            raise last_error

        return wrapper
    return decorator


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """
    Configure logging system

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        root_logger.addHandler(file_handler)

    logger.info(f"Logging system configured, level: {level}")


# ============================================================================
# Custom Click Parameter Types
# ============================================================================

import click


class NonEmptyString(click.ParamType):
    """
    Click parameter type that rejects empty strings.

    Usage:
        @click.option('--name', '-n', required=True, type=NonEmptyString(), help='对象名称')
    """
    name = "TEXT"

    def convert(self, value, param, ctx):
        if isinstance(value, str) and value.strip() == "":
            self.fail(f"'{value}' 不能为空字符串，请提供有效的名称。", param, ctx)
        return value
