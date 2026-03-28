# -*- coding: utf-8 -*-
"""Assembly module - assembly_create, assembly_add_part, assembly_add_constraint"""

import ast
from typing import Any, Dict, Optional


def _assembly_create(self, name: str) -> Dict[str, Any]:
    """Create assembly"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _asm_mock(self, "Assembly", name, "Assembly", {})

    doc = self.get_document()

    try:
        assembly = doc.addObject("App::Part", name)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Assembly",
            "label": assembly.Label
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _assembly_add_part(self, assembly_name: str, part_name: str,
                       placement: str = "[0, 0, 0]") -> Dict[str, Any]:
    """Add part to assembly"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "assembly": assembly_name,
            "part": part_name,
            "placement": placement,
            "mock": True
        }

    doc = self.get_document()

    try:
        assembly = doc.getObject(assembly_name)
        part = doc.getObject(part_name)

        if not assembly:
            return {"success": False, "error": f"Assembly not found: {assembly_name}"}
        if not part:
            return {"success": False, "error": f"Part not found: {part_name}"}

        assembly.addObject(part)

        # Set placement (use ast.literal_eval for safe parsing)
        try:
            import FreeCAD
            placement_list = ast.literal_eval(placement)
            if len(placement_list) == 3:
                part.Placement.Base = FreeCAD.Vector(*placement_list)
        except (ValueError, SyntaxError):
            pass  # Keep default position

        doc.recompute()

        return {
            "success": True,
            "assembly": assembly_name,
            "part": part_name,
            "placement": placement
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _assembly_add_constraint(self, assembly_name: str, constraint_type: str,
                             object1: str, object2: str,
                             parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Add assembly constraint"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "assembly": assembly_name,
            "constraint_type": constraint_type,
            "object1": object1,
            "object2": object2,
            "mock": True
        }

    doc = self.get_document()

    try:
        assembly = doc.getObject(assembly_name)
        if not assembly:
            return {"success": False, "error": f"Assembly not found: {assembly_name}"}

        constraint = doc.addObject("Part::Feature", f"Constraint_{constraint_type}")

        doc.recompute()

        return {
            "success": True,
            "assembly": assembly_name,
            "constraint_type": constraint_type,
            "object1": object1,
            "object2": object2
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _asm_mock(self, category: str, name: str,
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
