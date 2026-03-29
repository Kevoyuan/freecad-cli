# -*- coding: utf-8 -*-
"""Draft module - create_draft_object"""

from typing import Any, Dict, Optional

from ._mock import get_mock_state
from ._validators import MockValidators
from ._errors import CLIErrorCode, create_error_response


def _draft_create(self, name: str, object_type: str,
                  params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a Draft object

    Args:
        name: Object name
        object_type: Object type (Line, Polyline, Circle, Rectangle, Polygon, Arc)
        params: Object parameters

    Returns:
        Creation result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _draft_module = _fi._draft_module

    if not FREECAD_AVAILABLE:
        return _draft_mock_result(self, "Draft", name, object_type, params)

    doc = self.get_document()
    params = params or {}

    try:
        if object_type == "Line":
            obj = _draft_module.makeLine(
                (params.get("x1", 0), params.get("y1", 0), params.get("z1", 0)),
                (params.get("x2", 10), params.get("y2", 10), params.get("z2", 0))
            )
        elif object_type == "Circle":
            obj = _draft_module.makeCircle(
                radius=params.get("radius", 10),
                face=params.get("face", False)
            )
        elif object_type == "Rectangle":
            obj = _draft_module.makeRectangle(
                length=params.get("length", 10),
                height=params.get("height", 5),
                face=params.get("face", False)
            )
        elif object_type == "Polygon":
            obj = _draft_module.makePolygon(
                n_sides=params.get("n_sides", 6),
                radius=params.get("radius", 10)
            )
        elif object_type == "Polyline":
            points = params.get("points", [(0, 0), (10, 0), (10, 10)])
            obj = _draft_module.makeWire(points, closed=params.get("closed", False))
        else:
            return create_error_response(
                CLIErrorCode.OBJECT_INVALID_TYPE,
                type=f"Draft {object_type}"
            )

        obj.Label = name
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": object_type,
            "label": obj.Label
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _draft_mock_result(self, category: str, name: str,
                       sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result with unified format"""
    params = params or {}

    # Validate draft parameters
    validation_result = MockValidators.validate_draft_params(sub_type, params)
    if not validation_result.valid:
        return {
            "success": False,
            "mock": True,
            "error_code": CLIErrorCode.VALIDATION_FAILED,
            "error": f"Parameter validation failed: {', '.join(validation_result.errors)}",
            "validation_errors": validation_result.errors,
            "validation_warnings": validation_result.warnings,
            "message": "FreeCAD not installed - validation failed"
        }

    mock_state = get_mock_state()
    handle = mock_state.add(category, name, sub_type, params)

    return {
        "success": True,
        "mock": True,
        "category": category,
        "name": name,
        "type": sub_type,
        "object_handle": handle,
        "params": params,
        "bounding_box": {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100, "z_min": 0, "z_max": 0},
        "geometry": {"area": 10000},
        "validation_warnings": validation_result.warnings,
        "message": "FreeCAD not installed - returning mock data"
    }
