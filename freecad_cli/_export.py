# -*- coding: utf-8 -*-
"""Export module - export_document, get_object_info, list_objects, delete_object"""

from typing import Any, Dict, List, Optional

from ._errors import CLIErrorCode, create_error_response


def _export_document(self, filepath: str, format_type: str = "STEP") -> Dict[str, Any]:
    """
    Export document

    Args:
        filepath: Export file path
        format_type: Export format (STEP, STL, OBJ, IGES, BREP, DXF)

    Returns:
        Export result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _freecad_module = _fi._freecad_module

    if not FREECAD_AVAILABLE:
        # In mock mode, just return success with mock flag
        return {
            "success": True,
            "filepath": filepath,
            "format": format_type,
            "mock": True,
            "objects_exported": 0,
            "message": "FreeCAD not installed - export simulated"
        }

    doc = self.get_document()

    try:
        # Use Part.export which works across FreeCAD versions
        # FreeCAD 1.x removed FreeCAD.export()
        import Part as _part_module
        _part_module.export(doc.Objects, filepath)

        return {
            "success": True,
            "filepath": filepath,
            "format": format_type,
            "objects_exported": len(doc.Objects)
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.EXPORT_FAILED,
            detail=str(e)
        )


def _export_get_object_info(self, object_name: str) -> Dict[str, Any]:
    """
    Get object information

    Args:
        object_name: Object name

    Returns:
        Object detailed information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        from ._mock import get_mock_state
        info = get_mock_state().get_info(object_name)
        if info is None:
            return create_error_response(
                CLIErrorCode.OBJECT_NOT_FOUND,
                name=object_name
            )
        # Add error code to successful mock response
        return {
            "success": True,
            "mock": True,
            "object_handle": info.get("handle"),
            "name": info.get("name"),
            "label": info.get("label"),
            "type": info.get("type"),
            "category": info.get("category"),
            "params": info.get("params", {}),
        }

    doc = self.get_document()

    try:
        obj = doc.getObject(object_name)
        if not obj:
            return create_error_response(
                CLIErrorCode.OBJECT_NOT_FOUND,
                name=object_name
            )

        info = {
            "success": True,
            "name": obj.Name,
            "label": obj.Label,
            "type": obj.TypeId,
            "module": obj.Module if hasattr(obj, 'Module') else "Unknown"
        }

        # Add geometry information
        if hasattr(obj, 'Shape') and obj.Shape:
            shape = obj.Shape
            info["geometry"] = {
                "volume": shape.Volume if hasattr(shape, 'Volume') else 0,
                "area": shape.Area if hasattr(shape, 'Area') else 0,
                "bounding_box": self._get_bounding_box(obj)
            }

        return info
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _export_list_objects(self, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List objects in document

    Args:
        filter_type: Object type filter (optional)

    Returns:
        List of objects
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        from ._mock import get_mock_state
        return get_mock_state().list_objects(filter_type)

    doc = self.get_document()
    objects = []

    for obj in doc.Objects:
        if filter_type and filter_type not in obj.TypeId:
            continue

        obj_info = {
            "name": obj.Name,
            "label": obj.Label,
            "type": obj.TypeId
        }

        if hasattr(obj, 'Shape') and obj.Shape:
            obj_info["has_geometry"] = True

        objects.append(obj_info)

    return objects


def _export_delete_object(self, object_name: str) -> Dict[str, Any]:
    """
    Delete object

    Args:
        object_name: Name of object to delete

    Returns:
        Deletion result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        from ._mock import get_mock_state
        deleted = get_mock_state().delete(object_name)
        return {
            "success": True,
            "deleted": object_name if deleted else None,
            "mock": True,
            "found": deleted,
            "object_handle": f"mock:deleted/{object_name}",
        }

    doc = self.get_document()

    try:
        obj = doc.getObject(object_name)
        if not obj:
            return create_error_response(
                CLIErrorCode.OBJECT_NOT_FOUND,
                name=object_name
            )

        doc.removeObject(object_name)
        return {"success": True, "deleted": object_name}
    except Exception as e:
        return create_error_response(
            CLIErrorCode.OBJECT_DELETE_FAILED,
            name=object_name,
            detail=str(e)
        )
