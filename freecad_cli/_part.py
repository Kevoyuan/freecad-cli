# -*- coding: utf-8 -*-
"""Part module - create_part, get_document"""

from typing import Any, Dict, Optional


def _part_create_part(self, name: str, shape_type: str = "Box",
                      params: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Create a Part object

    Args:
        name: Object name
        shape_type: Shape type (Box, Cylinder, Sphere, Cone, Torus)
        params: Shape parameters

    Returns:
        Creation result information
    """
    # Import globals from parent
    FREECAD_AVAILABLE = self.__class__.__module__.split('.')[0]
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _part_mock_result(self, "Part", name, shape_type, params)

    doc = self.get_document()
    params = params or {}

    try:
        if shape_type == "Box":
            obj = doc.addObject("Part::Box", name)
            obj.Length = params.get("length", 10.0)
            obj.Width = params.get("width", 10.0)
            obj.Height = params.get("height", 10.0)
        elif shape_type == "Cylinder":
            obj = doc.addObject("Part::Cylinder", name)
            obj.Radius = params.get("radius", 5.0)
            obj.Height = params.get("height", 10.0)
        elif shape_type == "Sphere":
            obj = doc.addObject("Part::Sphere", name)
            obj.Radius = params.get("radius", 5.0)
        elif shape_type == "Cone":
            obj = doc.addObject("Part::Cone", name)
            obj.Radius1 = params.get("radius1", 5.0)
            obj.Radius2 = params.get("radius2", 2.0)
            obj.Height = params.get("height", 10.0)
        elif shape_type == "Torus":
            obj = doc.addObject("Part::Torus", name)
            obj.Radius1 = params.get("radius1", 10.0)
            obj.Radius2 = params.get("radius2", 2.0)
        else:
            return {"success": False, "error": f"Unknown shape type: {shape_type}"}

        doc.recompute()
        return {
            "success": True,
            "name": name,
            "type": shape_type,
            "label": obj.Label,
            "bounding_box": self._get_bounding_box(obj)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _part_mock_result(self, category: str, name: str,
                      sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result (used when FreeCAD is not installed)"""
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
