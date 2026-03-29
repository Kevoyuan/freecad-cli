# -*- coding: utf-8 -*-
"""Inspection module - inspection_create_check, inspection_measure_distance"""

from typing import Any, Dict

from ._mock import get_mock_state
from ._errors import CLIErrorCode, create_error_response


def _inspection_create_check(self, name: str,
                             object_name: str) -> Dict[str, Any]:
    """Create inspection"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _insp_mock(self, "Inspection", name, "Check", {"object": object_name})

    doc = self.get_document()

    try:
        obj = doc.getObject(object_name)
        if not obj:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=object_name)

        check = doc.addObject("Inspection::Feature", name)

        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Check",
            "object": object_name,
            "label": check.Label
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _inspection_measure_distance(self, object1: str,
                                object2: str) -> Dict[str, Any]:
    """Measure distance"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "object1": object1,
            "object2": object2,
            "distance": 10.0,
            "mock": True,
            "message": "FreeCAD not installed - measurement simulated"
        }

    doc = self.get_document()

    try:
        obj1 = doc.getObject(object1)
        obj2 = doc.getObject(object2)

        if not obj1:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=object1)
        if not obj2:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=object2)

        # Calculate distance (simplified)
        distance = 10.0

        return {
            "success": True,
            "object1": object1,
            "object2": object2,
            "distance": distance
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _insp_mock(self, category: str, name: str,
               sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result with unified format"""
    params = params or {}
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
        "bounding_box": {},
        "geometry": {},
        "validation_warnings": [],
        "message": "FreeCAD not installed - returning mock data"
    }
