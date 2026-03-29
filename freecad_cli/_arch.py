# -*- coding: utf-8 -*-
"""Arch module - create_arch_object"""

from typing import Any, Dict, Optional

from ._mock import get_mock_state
from ._errors import CLIErrorCode, create_error_response


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
            return create_error_response(
                CLIErrorCode.OBJECT_INVALID_TYPE,
                type=f"Arch {object_type}"
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


def _arch_mock_result(self, category: str, name: str,
                      sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result with unified format"""
    params = params or {}
    mock_state = get_mock_state()
    handle = mock_state.add(category, name, sub_type, params)

    # Calculate bounding box based on Arch type
    bounding_box = {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100, "z_min": 0, "z_max": 300}
    if sub_type == "Wall":
        l = params.get("length", 100)
        w = params.get("width", 20)
        h = params.get("height", 300)
        bounding_box = {"x_min": 0, "x_max": l, "y_min": 0, "y_max": w, "z_min": 0, "z_max": h}
    elif sub_type == "Structure":
        l = params.get("length", 100)
        w = params.get("width", 100)
        h = params.get("height", 200)
        bounding_box = {"x_min": 0, "x_max": l, "y_min": 0, "y_max": w, "z_min": 0, "z_max": h}
    elif sub_type == "Window":
        w = params.get("width", 100)
        h = params.get("height", 150)
        bounding_box = {"x_min": 0, "x_max": w, "y_min": 0, "y_max": 10, "z_min": 0, "z_max": h}

    return {
        "success": True,
        "mock": True,
        "category": category,
        "name": name,
        "type": sub_type,
        "object_handle": handle,
        "params": params,
        "bounding_box": bounding_box,
        "geometry": {"volume": 600000},
        "validation_warnings": [],
        "message": "FreeCAD not installed - returning mock data"
    }
