# -*- coding: utf-8 -*-
"""Boolean module - boolean_operation"""

from typing import Any, Dict

from ._mock import get_mock_state
from ._errors import CLIErrorCode, create_error_response


def _boolean_op(self, name: str, operation: str,
                object1: str, object2: str) -> Dict[str, Any]:
    """
    Perform boolean operation

    Args:
        name: Result object name
        operation: Operation type (Fuse, Cut, Common, Section)
        object1: First object name
        object2: Second object name

    Returns:
        Operation result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _part_module = _fi._part_module

    if not FREECAD_AVAILABLE:
        return _boolean_mock_result(self, "Boolean", name, operation,
                                    {"obj1": object1, "obj2": object2})

    doc = self.get_document()

    try:
        obj1 = doc.getObject(object1)
        obj2 = doc.getObject(object2)

        if not obj1 or not obj2:
            return create_error_response(
                CLIErrorCode.OBJECT_NOT_FOUND,
                name=object1 if not obj1 else object2
            )

        operation_map = {
            "Fuse": "Part::MultiFuse",
            "Cut": "Part::Cut",
            "Common": "Part::Common",
            "Section": "Part::Section"
        }

        result = doc.addObject(operation_map.get(operation, "Part::Fuse"), name)
        result.Shape = getattr(_part_module, operation)(
            obj1.Shape, obj2.Shape
        )

        doc.recompute()

        return {
            "success": True,
            "name": name,
            "operation": operation,
            "volume": result.Shape.Volume if hasattr(result.Shape, 'Volume') else 0,
            "surface_area": result.Shape.Area if hasattr(result.Shape, 'Area') else 0
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _boolean_mock_result(self, category: str, name: str,
                         sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result with unified format"""
    from ._mock import create_mock_result

    # Check if dependent objects exist in mock state
    mock_state = get_mock_state()
    obj1 = params.get("obj1") if params else None
    obj2 = params.get("obj2") if params else None

    warnings = []
    if obj1 and not mock_state.exists(obj1):
        return {
            "success": False,
            "mock": True,
            "error_code": CLIErrorCode.DEPENDENCY_NOT_FOUND,
            "error": f"Required object not found: {obj1}",
            "message": "FreeCAD not installed - dependency check failed"
        }
    if obj2 and not mock_state.exists(obj2):
        return {
            "success": False,
            "mock": True,
            "error_code": CLIErrorCode.DEPENDENCY_NOT_FOUND,
            "error": f"Required object not found: {obj2}",
            "message": "FreeCAD not installed - dependency check failed"
        }

    # Calculate mock geometry (simplified)
    # For boolean ops, we just use placeholder values
    handle = mock_state.add(category, name, sub_type, params)

    return {
        "success": True,
        "mock": True,
        "category": category,
        "name": name,
        "type": sub_type,
        "object_handle": handle,
        "params": params,
        "bounding_box": {"x_min": 0, "x_max": 20, "y_min": 0, "y_max": 20, "z_min": 0, "z_max": 20},
        "geometry": {"volume": 4000, "surface_area": 1200},
        "validation_warnings": warnings,
        "message": "FreeCAD not installed - returning mock data"
    }
