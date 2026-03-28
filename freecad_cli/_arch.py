# -*- coding: utf-8 -*-
"""Arch module - create_arch_object"""

from typing import Any, Dict, Optional


def _arch_create(self, name: str, object_type: str,
                 params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create an Arch object

    Args:
        name: Object name
        object_type: Object type (Wall, Structure, Window, Door, Roof, Stairs)
        params: Object parameters

    Returns:
        Creation result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _arch_module = _fi._arch_module

    if not FREECAD_AVAILABLE:
        return _arch_mock_result(self, "Arch", name, object_type, params)

    doc = self.get_document()
    params = params or {}

    try:
        if object_type == "Wall":
            obj = _arch_module.makeWall(
                length=params.get("length", 100),
                width=params.get("width", 20),
                height=params.get("height", 300)
            )
        elif object_type == "Structure":
            obj = _arch_module.makeStructure(
                length=params.get("length", 100),
                width=params.get("width", 100),
                height=params.get("height", 200)
            )
        elif object_type == "Window":
            obj = _arch_module.makeWindow(
                width=params.get("width", 100),
                height=params.get("height", 150)
            )
        elif object_type == "Roof":
            obj = _arch_module.makeRoof(
                base=params.get("base", None),
                angle=params.get("angle", 25)
            )
        else:
            return {"success": False, "error": f"Unknown Arch type: {object_type}"}

        obj.Label = name
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": object_type,
            "label": obj.Label
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _arch_mock_result(self, category: str, name: str,
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
