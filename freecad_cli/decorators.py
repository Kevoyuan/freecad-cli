# -*- coding: utf-8 -*-
"""
FreeCAD CLI - Decorators and Utilities
=====================================

提供装饰器和工具函数，减少代码重复。
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('freecad_cli')


def requires_freecad(func: Callable) -> Callable:
    """
    装饰器：确保 FreeCAD 可用，否则返回 mock 结果

    用法:
        @requires_freecad
        def my_function(wrapper, ...):
            # FreeCAD 可用时的逻辑
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from .freecad_integration import FREECAD_AVAILABLE, FreeCADWrapper

        # 检查是否传递了 wrapper 参数
        wrapper_instance = kwargs.get('wrapper') or (args[0] if args and isinstance(args[0], FreeCADWrapper) else None)

        if not FREECAD_AVAILABLE:
            logger.debug(f"FreeCAD 不可用，返回 mock 结果: {func.__name__}")
            # 返回 mock 结果
            return {
                "success": True,
                "mock": True,
                "function": func.__name__,
                "message": "FreeCAD 未安装 - 返回模拟数据"
            }

        return func(*args, **kwargs)

    return wrapper


def log_operation(operation_name: str = None):
    """
    装饰器：记录操作日志

    用法:
        @log_operation("创建零件")
        def create_part(...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            logger.info(f"开始操作: {op_name}")

            try:
                result = func(*args, **kwargs)

                if isinstance(result, dict):
                    if result.get('success'):
                        logger.info(f"操作成功: {op_name}")
                    else:
                        logger.warning(f"操作失败: {op_name} - {result.get('error', '未知错误')}")

                return result
            except Exception as e:
                logger.error(f"操作异常: {op_name} - {str(e)}")
                raise

        return wrapper
    return decorator


def handle_errors(default_return: Any = None, error_key: str = "error"):
    """
    装饰器：统一错误处理

    用法:
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
                logger.error(f"函数 {func.__name__} 执行错误: {str(e)}")
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
    装饰器：参数验证

    用法:
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

                    # 支持类型验证
                    if isinstance(validator, type):
                        if not isinstance(value, validator):
                            return {
                                "success": False,
                                "error": f"参数 {param_name} 类型错误，期望 {validator.__name__}",
                                "received_type": type(value).__name__
                            }

                    # 支持元组 (类型, 验证函数)
                    elif isinstance(validator, tuple) and len(validator) == 2:
                        expected_type, validator_fn = validator
                        if not isinstance(value, expected_type):
                            return {
                                "success": False,
                                "error": f"参数 {param_name} 类型错误"
                            }
                        if not validator_fn(value):
                            return {
                                "success": False,
                                "error": f"参数 {param_name} 验证失败"
                            }

            return func(*args, **kwargs)

        return wrapper
    return decorator


class OperationTimer:
    """操作计时器上下文管理器"""

    def __init__(self, operation_name: str, log_result: bool = True):
        self.operation_name = operation_name
        self.log_result = log_result
        self.start_time = None
        self.result = None

    def __enter__(self):
        import time
        self.start_time = time.time()
        logger.debug(f"开始计时: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start_time

        if exc_type is None:
            logger.info(f"[{elapsed:.3f}s] {self.operation_name} 完成")
        else:
            logger.error(f"[{elapsed:.3f}s] {self.operation_name} 失败: {exc_val}")

        return False  # 不吞没异常

    def set_result(self, result: Any):
        """设置结果"""
        self.result = result


def retry_on_failure(max_attempts: int = 3, delay: float = 0.1):
    """
    装饰器：失败重试

    用法:
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
                            f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_attempts}), "
                            f"{delay}s 后重试: {str(e)}"
                        )
                        time.sleep(delay)

            logger.error(f"{func.__name__} 最终失败: {str(last_error)}")
            raise last_error

        return wrapper
    return decorator


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """
    配置日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_file: 可选的日志文件路径
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    root_logger.addHandler(console_handler)

    # 文件处理器 (可选)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        root_logger.addHandler(file_handler)

    logger.info(f"日志系统已配置，级别: {level}")
