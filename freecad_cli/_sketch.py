# -*- coding: utf-8 -*-
"""Sketch module - create_sketch, add_sketch_geometry"""

from typing import Any, Dict, List, Optional

from ._mock import get_mock_state, create_mock_result
from ._validators import MockValidators
from ._errors import CLIErrorCode, create_error_response


def _sketch_create_sketch(self, name: str, plane: str = "XY") -> Dict[str, Any]:
    """
    Create a sketch object

    Args:
        name: Sketch name
        plane: Sketch plane (XY, XZ, YZ)

    Returns:
        Creation result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _sketch_mock_result(self, "Sketch", name, params={"plane": plane})

    doc = self.get_document()

    try:
        obj = doc.addObject("Sketcher::SketchObject", name)

        # Set sketch placement based on plane
        # FreeCAD 1.x removed Support attribute — use Placement instead
        if plane == "XY":
            pass  # Default XY plane, no placement change needed
        elif plane == "XZ":
            import FreeCAD as fc
            rot = fc.Rotation(fc.Vector(1, 0, 0), 90)  # Rotate to XZ plane
            obj.Placement = fc.Placement(fc.Vector(0, 0, 0), rot)
        elif plane == "YZ":
            import FreeCAD as fc
            rot = fc.Rotation(fc.Vector(0, 1, 0), -90)  # Rotate to YZ plane
            obj.Placement = fc.Placement(fc.Vector(0, 0, 0), rot)

        doc.recompute()
        return {
            "success": True,
            "name": name,
            "plane": plane,
            "constraints": 0,
            "geometry": 0
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _sketch_add_geometry(self, sketch_name: str,
                         geometry_type: str,
                         params: Dict[str, float]) -> Dict[str, Any]:
    """
    Add geometry element to sketch

    Args:
        sketch_name: Sketch name
        geometry_type: Geometry type (Line, Circle, Arc, Rectangle, Polygon)
        params: Geometry parameters

    Returns:
        Addition result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _sketcher_module = _fi._sketcher_module

    if not FREECAD_AVAILABLE:
        return _sketch_mock_result(self, "Geometry", sketch_name, geometry_type, params)

    doc = self.get_document()

    try:
        sketch = doc.getObject(sketch_name)
        if not sketch:
            return create_error_response(
                CLIErrorCode.OBJECT_NOT_FOUND,
                name=sketch_name
            )

        geo_id = -1

        if geometry_type == "Line":
            geo = _sketcher_module.Geometry(
                params.get("x1", 0), params.get("y1", 0),
                params.get("x2", 10), params.get("y2", 10)
            )
            geo_id = sketch.addGeometry(geo)
        elif geometry_type == "Circle":
            geo = _sketcher_module.Geometry(
                params.get("cx", 0), params.get("cy", 0),
                params.get("radius", 5)
            )
            geo_id = sketch.addGeometry(geo)
        elif geometry_type == "Rectangle":
            p1 = (params.get("x1", 0), params.get("y1", 0))
            p2 = (params.get("x2", 10), params.get("y2", 10))
            # Add four edges of rectangle
            for i in range(4):
                geo_id = sketch.addGeometry(_sketcher_module.LineSegment(*p1, *p2))
        else:
            return create_error_response(
                CLIErrorCode.OBJECT_INVALID_TYPE,
                type=geometry_type
            )

        doc.recompute()
        return {
            "success": True,
            "geometry_id": geo_id,
            "type": geometry_type
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _sketch_mock_result(self, category: str, name: str,
                        sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result with unified format"""
    params = params or {}

    # Validate sketch parameters
    validation_result = MockValidators.validate_sketch_params(params)
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

    # Add to mock state
    mock_state = get_mock_state()
    handle = mock_state.add(category, name, sub_type, params)

    # Get bounding box for sketch (2D, so z=0)
    plane = params.get("plane", "XY")
    if plane == "XY":
        bounding_box = {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100, "z_min": 0, "z_max": 0}
    elif plane == "XZ":
        bounding_box = {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 0, "z_min": 0, "z_max": 100}
    else:  # YZ
        bounding_box = {"x_min": 0, "x_max": 0, "y_min": 0, "y_max": 100, "z_min": 0, "z_max": 100}

    return {
        "success": True,
        "mock": True,
        "category": category,
        "name": name,
        "type": sub_type,
        "object_handle": handle,
        "params": params,
        "bounding_box": bounding_box,
        "geometry": {"area": 10000},  # Placeholder 2D area
        "validation_warnings": validation_result.warnings,
        "message": "FreeCAD not installed - returning mock data"
    }
