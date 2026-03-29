# -*- coding: utf-8 -*-
"""
Error Codes Module
==================

Defines standardized error codes for freecad-cli.
All errors include machine-readable codes for AI agent consumption.
"""

from typing import Any, Dict, Optional


# Error code definitions
class CLIErrorCode:
    """Standard error codes for freecad-cli"""

    # General errors (FREECAD_0XX)
    SUCCESS = "FREECAD_000"
    UNKNOWN_ERROR = "FREECAD_001"

    # Object errors (FREECAD_1XX)
    OBJECT_NOT_FOUND = "FREECAD_101"
    OBJECT_ALREADY_EXISTS = "FREECAD_102"
    OBJECT_DELETE_FAILED = "FREECAD_103"
    OBJECT_INVALID_TYPE = "FREECAD_104"

    # Parameter errors (FREECAD_2XX)
    INVALID_PARAM = "FREECAD_201"
    MISSING_REQUIRED_PARAM = "FREECAD_202"
    INVALID_PARAM_TYPE = "FREECAD_203"
    PARAM_OUT_OF_RANGE = "FREECAD_204"

    # Dependency errors (FREECAD_3XX)
    DEPENDENCY_NOT_FOUND = "FREECAD_301"
    DEPENDENCY_NOT_MET = "FREECAD_302"
    CIRCULAR_DEPENDENCY = "FREECAD_303"

    # Validation errors (FREECAD_4XX)
    VALIDATION_WARNING = "FREECAD_401"
    VALIDATION_FAILED = "FREECAD_402"

    # FreeCAD errors (FREECAD_5XX)
    FREECAD_NOT_AVAILABLE = "FREECAD_501"
    FREECAD_INIT_FAILED = "FREECAD_502"
    FREECAD_VERSION_INCOMPATIBLE = "FREECAD_503"

    # Export/Import errors (FREECAD_6XX)
    EXPORT_FAILED = "FREECAD_601"
    IMPORT_FAILED = "FREECAD_602"
    UNSUPPORTED_FORMAT = "FREECAD_603"

    # Document errors (FREECAD_7XX)
    DOCUMENT_NOT_FOUND = "FREECAD_701"
    DOCUMENT_CREATE_FAILED = "FREECAD_702"

    # Command errors (FREECAD_8XX)
    COMMAND_NOT_FOUND = "FREECAD_801"
    COMMAND_PARSE_FAILED = "FREECAD_802"
    COMMAND_EXECUTE_FAILED = "FREECAD_803"


# Error message templates
ERROR_MESSAGES: Dict[str, str] = {
    CLIErrorCode.SUCCESS: "Operation completed successfully",
    CLIErrorCode.UNKNOWN_ERROR: "An unknown error occurred: {detail}",

    CLIErrorCode.OBJECT_NOT_FOUND: "Object '{name}' not found",
    CLIErrorCode.OBJECT_ALREADY_EXISTS: "Object '{name}' already exists",
    CLIErrorCode.OBJECT_DELETE_FAILED: "Failed to delete object '{name}'",
    CLIErrorCode.OBJECT_INVALID_TYPE: "Invalid object type: {type}",

    CLIErrorCode.INVALID_PARAM: "Invalid parameter: {param} = {value}",
    CLIErrorCode.MISSING_REQUIRED_PARAM: "Missing required parameter: {param}",
    CLIErrorCode.INVALID_PARAM_TYPE: "Parameter '{param}' must be of type {expected}, got {actual}",
    CLIErrorCode.PARAM_OUT_OF_RANGE: "Parameter '{param}' value {value} is out of range [{min}, {max}]",

    CLIErrorCode.DEPENDENCY_NOT_FOUND: "Required dependency '{name}' not found",
    CLIErrorCode.DEPENDENCY_NOT_MET: "Dependency not met for operation: {detail}",
    CLIErrorCode.CIRCULAR_DEPENDENCY: "Circular dependency detected: {detail}",

    CLIErrorCode.VALIDATION_WARNING: "Validation warning: {detail}",
    CLIErrorCode.VALIDATION_FAILED: "Validation failed: {detail}",

    CLIErrorCode.FREECAD_NOT_AVAILABLE: "FreeCAD is not installed or cannot be imported",
    CLIErrorCode.FREECAD_INIT_FAILED: "Failed to initialize FreeCAD: {detail}",
    CLIErrorCode.FREECAD_VERSION_INCOMPATIBLE: "FreeCAD version {version} is incompatible. Required: >= {required}",

    CLIErrorCode.EXPORT_FAILED: "Export failed: {detail}",
    CLIErrorCode.IMPORT_FAILED: "Import failed: {detail}",
    CLIErrorCode.UNSUPPORTED_FORMAT: "Unsupported format: {format}",

    CLIErrorCode.DOCUMENT_NOT_FOUND: "Document '{name}' not found",
    CLIErrorCode.DOCUMENT_CREATE_FAILED: "Failed to create document: {detail}",

    CLIErrorCode.COMMAND_NOT_FOUND: "Command not found: {command}",
    CLIErrorCode.COMMAND_PARSE_FAILED: "Failed to parse command: {detail}",
    CLIErrorCode.COMMAND_EXECUTE_FAILED: "Command execution failed: {detail}",
}


def get_error_message(error_code: str, **kwargs: Any) -> str:
    """
    Get formatted error message for an error code.

    Args:
        error_code: The error code (e.g., "FREECAD_001")
        **kwargs: Format arguments for the message template

    Returns:
        Formatted error message string
    """
    template = ERROR_MESSAGES.get(error_code, f"Unknown error: {error_code}")
    try:
        return template.format(**kwargs)
    except (KeyError, ValueError):
        return template


def create_error_response(error_code: str, detail: Optional[str] = None,
                          **kwargs: Any) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.

    Args:
        error_code: The error code
        detail: Additional error details
        **kwargs: Format arguments for the message

    Returns:
        Error response dictionary
    """
    message = get_error_message(error_code, detail=detail or "", **kwargs)
    return {
        "success": False,
        "error_code": error_code,
        "error": message,
        "detail": detail,
        "recoverable": error_code not in [
            CLIErrorCode.UNKNOWN_ERROR,
            CLIErrorCode.FREECAD_VERSION_INCOMPATIBLE,
            CLIErrorCode.CIRCULAR_DEPENDENCY,
        ]
    }


def create_success_response(**kwargs: Any) -> Dict[str, Any]:
    """
    Create a standardized success response dictionary.

    Args:
        **kwargs: Fields to include in the response

    Returns:
        Success response dictionary
    """
    response = {"success": True, "error_code": CLIErrorCode.SUCCESS}
    response.update(kwargs)
    return response
