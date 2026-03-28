# -*- coding: utf-8 -*-
"""Surface module - create_surface, surface_from_edges"""

from typing import Any, Dict, Optional


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
            return {"success": False, "error": f"Unknown surface type: {surface_type}"}

        doc.recompute()
        return {
            "success": True,
            "name": name,
            "type": surface_type,
            "label": obj.Label
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


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
            return {"success": False, "error": f"Sketch not found: {sketch_name}"}

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
        return {"success": False, "error": str(e)}


def _surface_mock_result(self, category: str, name: str,
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
