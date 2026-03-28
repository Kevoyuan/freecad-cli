# -*- coding: utf-8 -*-
"""Boolean module - boolean_operation"""

from typing import Any, Dict


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
            return {"success": False, "error": "Specified object not found"}

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
        return {"success": False, "error": str(e)}


def _boolean_mock_result(self, category: str, name: str,
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
