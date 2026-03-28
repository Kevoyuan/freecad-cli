# -*- coding: utf-8 -*-
"""Sketch module - create_sketch, add_sketch_geometry"""

from typing import Any, Dict, List, Optional


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

        # Set sketch plane
        if plane == "XY":
            obj.Support = [(doc.getObject("XY_Plane"), '')]
        elif plane == "XZ":
            obj.Support = [(doc.getObject("XZ_Plane"), '')]
        elif plane == "YZ":
            obj.Support = [(doc.getObject("YZ_Plane"), '')]

        doc.recompute()
        return {
            "success": True,
            "name": name,
            "plane": plane,
            "constraints": 0,
            "geometry": 0
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


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
            return {"success": False, "error": f"Sketch not found: {sketch_name}"}

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
            return {"success": False, "error": f"Unsupported geometry type: {geometry_type}"}

        doc.recompute()
        return {
            "success": True,
            "geometry_id": geo_id,
            "type": geometry_type
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _sketch_mock_result(self, category: str, name: str,
                        sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result"""
    from ._mock import get_mock_state
    get_mock_state().add(category, name, sub_type, params)
    return {
        "success": True,
        "mock": True,
        "category": category,
        "name": name,
        "type": sub_type,
        "params": params,
        "message": "FreeCAD not installed - returning mock data"
    }
