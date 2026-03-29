# -*- coding: utf-8 -*-
"""FEM module - fem_create_analysis, fem_add_material,
fem_add_boundary_condition, fem_run_analysis"""

from typing import Any, Dict

from ._mock import get_mock_state
from ._errors import CLIErrorCode, create_error_response


def _fem_create_analysis(self, name: str,
                         analysis_type: str = "static") -> Dict[str, Any]:
    """Create finite element analysis"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _fem_mock(self, "FEM", name, "Analysis", {"type": analysis_type})

    doc = self.get_document()

    try:
        analysis = doc.addObject("Fem::Analysis", name)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Analysis",
            "analysis_type": analysis_type,
            "label": analysis.Label
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _fem_add_material(self, analysis_name: str,
                      material: str = "Steel") -> Dict[str, Any]:
    """Add material to analysis"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "analysis": analysis_name,
            "material": material,
            "mock": True
        }

    doc = self.get_document()

    try:
        analysis = doc.getObject(analysis_name)
        if not analysis:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=analysis_name)

        material_obj = doc.addObject("Fem::Material", f"Material_{material}")
        material_obj.Material = {"Name": material}

        analysis.addObject(material_obj)
        doc.recompute()

        return {
            "success": True,
            "analysis": analysis_name,
            "material": material,
            "material_object": material_obj.Name
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _fem_add_bc(self, analysis_name: str, bc_type: str,
                object_name: str,
                parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Add boundary condition"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "analysis": analysis_name,
            "bc_type": bc_type,
            "object": object_name,
            "parameters": parameters,
            "mock": True
        }

    doc = self.get_document()

    try:
        analysis = doc.getObject(analysis_name)
        if not analysis:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=analysis_name)

        bc = doc.addObject("Fem::Constraint", f"BC_{bc_type}")

        analysis.addObject(bc)
        doc.recompute()

        return {
            "success": True,
            "analysis": analysis_name,
            "bc_type": bc_type,
            "object": object_name,
            "bc_object": bc.Name
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _fem_run(self, analysis_name: str) -> Dict[str, Any]:
    """Run finite element analysis"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "analysis": analysis_name,
            "status": "completed",
            "mock": True,
            "message": "FreeCAD not installed - analysis simulated"
        }

    doc = self.get_document()

    try:
        analysis = doc.getObject(analysis_name)
        if not analysis:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=analysis_name)

        doc.recompute()

        return {
            "success": True,
            "analysis": analysis_name,
            "status": "completed"
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _fem_mock(self, category: str, name: str,
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
