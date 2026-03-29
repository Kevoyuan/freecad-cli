# -*- coding: utf-8 -*-
"""Surface module - create_surface, surface_from_edges"""

from typing import Any, Dict, Optional

from ._mock import get_mock_state
from ._errors import CLIErrorCode, create_error_response


def _surface_create(self, name: str, surface_type: str,
                    params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a Surface object

    Args:
        name: Object name
        surface_type: Surface type (Fill, Sweep, Loft, Bezier)
        params: Object parameters

    Returns:
        Creation result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _surface_mock_result(self, "Surface", name, surface_type, params)

    params = params or {}
    doc = self.get_document()

    try:
        if surface_type == "Fill":
            obj = doc.addObject("Surface::Fill", name)
        elif surface_type == "Sweep":
            obj = doc.addObject("Surface::Sweep", name)
            obj.Sections = params.get("sections", [])
        elif surface_type == "Loft":
            obj = doc.addObject("Surface::Loft", name)
            obj.Sections = params.get("sections", [])
        elif surface_type == "Bezier":
            obj = doc.addObject("Surface::Bezier", name)
        else:
            return create_error_response(
                CLIErrorCode.OBJECT_INVALID_TYPE,
                type=surface_type
            )

        doc.recompute()
        return {
            "success": True,
            "name": name,
            "type": surface_type,
            "label": obj.Label
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _surface_from_edges(self, name: str, sketch_name: str) -> Dict[str, Any]:
    """
    Create surface from sketch edges

    Args:
        name: Surface object name
        sketch_name: Sketch name

    Returns:
        Creation result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _surface_mock_result(self, "Surface", name, "from_edges",
                                    {"sketch": sketch_name})

    doc = self.get_document()

    try:
        sketch = doc.getObject(sketch_name)
        if not sketch:
            return create_error_response(
                CLIErrorCode.OBJECT_NOT_FOUND,
                name=sketch_name
            )

        obj = doc.addObject("Surface::Fill", name)
        obj.Source = sketch

        doc.recompute()
        return {
            "success": True,
            "name": name,
            "source_sketch": sketch_name,
            "label": obj.Label
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _surface_mock_result(self, category: str, name: str,
                         sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result with unified format"""
    params = params or {}
    mock_state = get_mock_state()
    handle = mock_state.add(category, name, sub_type, params)

    # Check dependencies
    if sub_type == "from_edges":
        sketch = params.get("sketch") if params else None
        if sketch and not mock_state.exists(sketch):
            return {
                "success": False,
                "mock": True,
                "error_code": CLIErrorCode.DEPENDENCY_NOT_FOUND,
                "error": f"Required sketch not found: {sketch}",
                "message": "FreeCAD not installed - dependency check failed"
            }

    return {
        "success": True,
        "mock": True,
        "category": category,
        "name": name,
        "type": sub_type,
        "object_handle": handle,
        "params": params,
        "bounding_box": {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100, "z_min": 0, "z_max": 100},
        "geometry": {"area": 10000},
        "validation_warnings": [],
        "message": "FreeCAD not installed - returning mock data"
    }
