# -*- coding: utf-8 -*-
"""Material module - material_create, material_get_standard"""

from typing import Any, Dict


def _material_create(self, name: str,
                     properties: Dict[str, Any]) -> Dict[str, Any]:
    """Create material"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _mat_mock(self, "Material", name, "Material", properties)

    doc = self.get_document()

    try:
        material = doc.addObject("App::MaterialObjectPython", name)
        material.Material = properties

        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Material",
            "properties": properties,
            "label": material.Label
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _material_get_standard(self, material_name: str) -> Dict[str, Any]:
    """Get standard material"""
    # Standard material library (works with or without FreeCAD)
    materials = {
        "Steel": {
            "Name": "Steel",
            "Density": "7850 kg/m^3",
            "YoungsModulus": "210000 MPa",
            "PoissonRatio": "0.3",
            "YieldStrength": "250 MPa"
        },
        "Aluminum": {
            "Name": "Aluminum",
            "Density": "2700 kg/m^3",
            "YoungsModulus": "70000 MPa",
            "PoissonRatio": "0.33",
            "YieldStrength": "270 MPa"
        },
        "Copper": {
            "Name": "Copper",
            "Density": "8960 kg/m^3",
            "YoungsModulus": "130000 MPa",
            "PoissonRatio": "0.34",
            "YieldStrength": "33 MPa"
        }
    }

    if material_name in materials:
        return {
            "success": True,
            "material": material_name,
            "properties": materials[material_name]
        }
    else:
        return {
            "success": False,
            "error": f"Unknown material: {material_name}",
            "available_materials": list(materials.keys())
        }


def _mat_mock(self, category: str, name: str,
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
