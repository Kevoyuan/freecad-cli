# -*- coding: utf-8 -*-
"""Spreadsheet module - spreadsheet_create, spreadsheet_set_cell,
spreadsheet_set_formula, spreadsheet_link"""

from typing import Any, Dict

from ._mock import get_mock_state
from ._errors import CLIErrorCode, create_error_response


def _spreadsheet_create(self, name: str) -> Dict[str, Any]:
    """Create spreadsheet"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _ss_mock(self, "Spreadsheet", name, "Sheet", {})

    doc = self.get_document()

    try:
        sheet = doc.addObject("Spreadsheet::Sheet", name)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Sheet",
            "label": sheet.Label
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _spreadsheet_set_cell(self, sheet_name: str, cell: str,
                          value: Any) -> Dict[str, Any]:
    """Set cell value"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "sheet": sheet_name,
            "cell": cell,
            "value": value,
            "mock": True
        }

    doc = self.get_document()

    try:
        sheet = doc.getObject(sheet_name)
        if not sheet:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=sheet_name)

        sheet.set(cell, str(value))
        doc.recompute()

        return {
            "success": True,
            "sheet": sheet_name,
            "cell": cell,
            "value": value
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _spreadsheet_set_formula(self, sheet_name: str, cell: str,
                             formula: str) -> Dict[str, Any]:
    """Set cell formula"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "sheet": sheet_name,
            "cell": cell,
            "formula": formula,
            "mock": True
        }

    doc = self.get_document()

    try:
        sheet = doc.getObject(sheet_name)
        if not sheet:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=sheet_name)

        sheet.set(cell, formula)
        doc.recompute()

        return {
            "success": True,
            "sheet": sheet_name,
            "cell": cell,
            "formula": formula
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _spreadsheet_link(self, sheet_name: str, object_name: str,
                      property_name: str, cell: str) -> Dict[str, Any]:
    """Link spreadsheet to object property"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "sheet": sheet_name,
            "object": object_name,
            "property": property_name,
            "cell": cell,
            "mock": True
        }

    doc = self.get_document()

    try:
        sheet = doc.getObject(sheet_name)
        obj = doc.getObject(object_name)

        if not sheet:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=sheet_name)
        if not obj:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=object_name)

        sheet.set(cell, f"{object_name}.{property_name}")
        doc.recompute()

        return {
            "success": True,
            "sheet": sheet_name,
            "object": object_name,
            "property": property_name,
            "cell": cell
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _ss_mock(self, category: str, name: str,
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
