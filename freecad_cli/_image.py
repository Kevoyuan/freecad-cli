# -*- coding: utf-8 -*-
"""Image module - image_import, image_scale"""

from typing import Any, Dict

from ._mock import get_mock_state
from ._errors import CLIErrorCode, create_error_response


def _image_import(self, name: str, filepath: str) -> Dict[str, Any]:
    """Import image"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _img_mock(self, "Image", name, "Image", {"filepath": filepath})

    doc = self.get_document()

    try:
        image = doc.addObject("Image::ImagePlane", name)
        image.ImageFile = filepath

        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Image",
            "filepath": filepath,
            "label": image.Label
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _image_scale(self, name: str, scale_x: float = 1.0,
                 scale_y: float = 1.0) -> Dict[str, Any]:
    """Scale image"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "name": name,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "mock": True
        }

    doc = self.get_document()

    try:
        image = doc.getObject(name)
        if not image:
            return create_error_response(CLIErrorCode.OBJECT_NOT_FOUND, name=name)

        image.XSize = image.XSize * scale_x
        image.YSize = image.YSize * scale_y

        doc.recompute()

        return {
            "success": True,
            "name": name,
            "scale_x": scale_x,
            "scale_y": scale_y
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _img_mock(self, category: str, name: str,
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
