# -*- coding: utf-8 -*-
"""TechDraw module - techdraw_create_page, techdraw_add_view,
techdraw_add_dimension, techdraw_export"""

from typing import Any, Dict, List, Tuple


def _techdraw_create_page(self, name: str,
                          template: str = "A4_Landscape") -> Dict[str, Any]:
    """Create TechDraw page"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _techdraw_module = _fi._techdraw_module

    if not FREECAD_AVAILABLE:
        return _td_mock(self, "TechDraw", name, "Page", {"template": template})

    doc = self.get_document()

    try:
        if _techdraw_module:
            page = doc.addObject("TechDraw::DrawPage", name)
            template_obj = doc.addObject("TechDraw::DrawTemplate", "Template")
            template_obj.Template = template
            page.Template = template_obj
        else:
            page = doc.addObject("TechDraw::DrawPage", name)

        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Page",
            "template": template,
            "label": page.Label if hasattr(page, 'Label') else name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _techdraw_add_view(self, page_name: str, source_name: str,
                       projection_type: str = "FirstAngle") -> Dict[str, Any]:
    """Add engineering view"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _td_mock(self, "TechDraw", "View", "View",
                        {"page": page_name, "source": source_name})

    doc = self.get_document()

    try:
        page = doc.getObject(page_name)
        source = doc.getObject(source_name)

        if not page:
            return {"success": False, "error": f"Page not found: {page_name}"}
        if not source:
            return {"success": False, "error": f"Source object not found: {source_name}"}

        view = doc.addObject("TechDraw::DrawViewPart", f"View_{source_name}")
        view.Source = [source]
        view.Direction = (0.0, 0.0, 1.0)
        view.ScaleType = "Automatic"
        page.addView(view)

        doc.recompute()

        return {
            "success": True,
            "name": view.Name,
            "type": "View",
            "source": source_name,
            "page": page_name,
            "projection": projection_type
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _techdraw_add_dimension(self, view_name: str, dimension_type: str,
                            points: List[Tuple[float, float]]) -> Dict[str, Any]:
    """Add dimension annotation"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _td_mock(self, "TechDraw", "Dimension", dimension_type,
                         {"view": view_name, "points": points})

    doc = self.get_document()

    try:
        view = doc.getObject(view_name)
        if not view:
            return {"success": False, "error": f"View not found: {view_name}"}

        dim = doc.addObject("TechDraw::DrawViewDimension", f"Dim_{dimension_type}")
        dim.Type = dimension_type
        dim.References2D = [(view, view.Shape.Vertexes[0])]

        if hasattr(view, 'Symbol'):
            dim.Symbol = view.Symbol

        doc.recompute()

        return {
            "success": True,
            "name": dim.Name,
            "type": "Dimension",
            "dimension_type": dimension_type,
            "view": view_name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _techdraw_export(self, page_name: str, filepath: str,
                     format_type: str = "PDF") -> Dict[str, Any]:
    """Export engineering drawing"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _freecad_module = _fi._freecad_module

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "page": page_name,
            "filepath": filepath,
            "format": format_type,
            "mock": True
        }

    doc = self.get_document()

    try:
        page = doc.getObject(page_name)
        if not page:
            return {"success": False, "error": f"Page not found: {page_name}"}

        _freecad_module.export([page], filepath)

        return {
            "success": True,
            "page": page_name,
            "filepath": filepath,
            "format": format_type
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _td_mock(self, category: str, name: str,
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
