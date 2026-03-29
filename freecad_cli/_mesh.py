# -*- coding: utf-8 -*-
"""Mesh module - create_mesh_object, mesh_from_shape, mesh_boolean"""

from typing import Any, Dict, Optional

from ._mock import get_mock_state
from ._errors import CLIErrorCode, create_error_response


def _mesh_create(self, name: str, object_type: str,
                 params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a Mesh object

    Args:
        name: Object name
        object_type: Object type (RegularMesh, Triangle, Grid)
        params: Object parameters

    Returns:
        Creation result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _mesh_module = _fi._mesh_module

    if not FREECAD_AVAILABLE:
        return _mesh_mock_result(self, "Mesh", name, object_type, params)

    params = params or {}
    doc = self.get_document()

    try:
        if object_type == "RegularMesh":
            mesh = _mesh_module.Mesh()
            segment_length = params.get("segment_length", 1.0)
            for i in range(int(params.get("width", 10))):
                for j in range(int(params.get("height", 10))):
                    p1 = (i * segment_length, j * segment_length, 0)
                    p2 = ((i + 1) * segment_length, j * segment_length, 0)
                    p3 = ((i + 1) * segment_length, (j + 1) * segment_length, 0)
                    p4 = (i * segment_length, (j + 1) * segment_length, 0)
                    mesh.addFacet(_mesh_module.MeshPoint(*p1),
                                  _mesh_module.MeshPoint(*p2),
                                  _mesh_module.MeshPoint(*p3))
                    mesh.addFacet(_mesh_module.MeshPoint(*p1),
                                  _mesh_module.MeshPoint(*p3),
                                  _mesh_module.MeshPoint(*p4))

            obj = doc.addObject("Mesh::Feature", name)
            obj.Mesh = mesh

        elif object_type == "Triangle":
            mesh = _mesh_module.Mesh()
            points = params.get("points", [(0, 0, 0), (10, 0, 0), (5, 10, 0)])
            if len(points) >= 3:
                mesh.addFacet(_mesh_module.MeshPoint(*points[0]),
                              _mesh_module.MeshPoint(*points[1]),
                              _mesh_module.MeshPoint(*points[2]))
            obj = doc.addObject("Mesh::Feature", name)
            obj.Mesh = mesh

        elif object_type == "Grid":
            mesh = _mesh_module.Mesh()
            obj = doc.addObject("Mesh::Feature", name)
            obj.Mesh = mesh

        else:
            return create_error_response(
                CLIErrorCode.OBJECT_INVALID_TYPE,
                type=object_type
            )

        doc.recompute()
        return {
            "success": True,
            "name": name,
            "type": object_type,
            "label": obj.Label,
            "vertex_count": mesh.countVertices() if hasattr(mesh, 'countVertices') else 0,
            "face_count": mesh.countFacets() if hasattr(mesh, 'countFacets') else 0
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _mesh_from_shape(self, name: str, source_name: str,
                     deflection: float = 0.1) -> Dict[str, Any]:
    """
    Create mesh from shape

    Args:
        name: Mesh object name
        source_name: Source shape object name
        deflection: Mesh deflection value (precision)

    Returns:
        Creation result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _mesh_module = _fi._mesh_module

    if not FREECAD_AVAILABLE:
        return _mesh_mock_result(self, "Mesh", name, "from_shape",
                                 {"source": source_name, "deflection": deflection})

    doc = self.get_document()

    try:
        source = doc.getObject(source_name)
        if not source:
            return create_error_response(
                CLIErrorCode.OBJECT_NOT_FOUND,
                name=source_name
            )

        if not hasattr(source, 'Shape'):
            return create_error_response(
                CLIErrorCode.INVALID_PARAM,
                param="source",
                detail="Source object does not have Shape property"
            )

        mesh = _mesh_module.Mesh(source.Shape, deflection)

        obj = doc.addObject("Mesh::Feature", name)
        obj.Mesh = mesh

        doc.recompute()
        return {
            "success": True,
            "name": name,
            "source": source_name,
            "deflection": deflection,
            "vertex_count": mesh.countVertices(),
            "face_count": mesh.countFacets()
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _mesh_boolean(self, name: str, operation: str,
                  object1: str, object2: str) -> Dict[str, Any]:
    """
    Mesh boolean operation

    Args:
        name: Result object name
        operation: Operation type (Union, Intersection, Difference)
        object1: First mesh object
        object2: Second mesh object

    Returns:
        Operation result information
    """
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _mesh_mock_result(self, "MeshBoolean", name, operation,
                                 {"obj1": object1, "obj2": object2})

    doc = self.get_document()

    try:
        mesh1_obj = doc.getObject(object1)
        mesh2_obj = doc.getObject(object2)

        if not mesh1_obj or not mesh2_obj:
            return create_error_response(
                CLIErrorCode.OBJECT_NOT_FOUND,
                name=object1 if not mesh1_obj else object2
            )

        mesh1 = mesh1_obj.Mesh
        mesh2 = mesh2_obj.Mesh

        if operation == "Union":
            result_mesh = mesh1 + mesh2
        elif operation == "Intersection":
            result_mesh = mesh1.intersect(mesh2)
        elif operation == "Difference":
            result_mesh = mesh1.subtract(mesh2)
        else:
            return create_error_response(
                CLIErrorCode.INVALID_PARAM,
                param="operation",
                detail=f"Unknown operation: {operation}"
            )

        obj = doc.addObject("Mesh::Feature", name)
        obj.Mesh = result_mesh

        doc.recompute()
        return {
            "success": True,
            "name": name,
            "operation": operation,
            "vertex_count": result_mesh.countVertices(),
            "face_count": result_mesh.countFacets()
        }
    except Exception as e:
        return create_error_response(
            CLIErrorCode.COMMAND_EXECUTE_FAILED,
            detail=str(e)
        )


def _mesh_mock_result(self, category: str, name: str,
                      sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result with unified format"""
    params = params or {}
    mock_state = get_mock_state()
    handle = mock_state.add(category, name, sub_type, params)

    # Check dependencies
    if sub_type == "from_shape":
        source = params.get("source") if params else None
        if source and not mock_state.exists(source):
            return {
                "success": False,
                "mock": True,
                "error_code": CLIErrorCode.DEPENDENCY_NOT_FOUND,
                "error": f"Required object not found: {source}",
                "message": "FreeCAD not installed - dependency check failed"
            }
    elif sub_type in ("Union", "Intersection", "Difference"):
        obj1 = params.get("obj1") if params else None
        obj2 = params.get("obj2") if params else None
        if obj1 and not mock_state.exists(obj1):
            return {
                "success": False,
                "mock": True,
                "error_code": CLIErrorCode.DEPENDENCY_NOT_FOUND,
                "error": f"Required object not found: {obj1}",
                "message": "FreeCAD not installed - dependency check failed"
            }
        if obj2 and not mock_state.exists(obj2):
            return {
                "success": False,
                "mock": True,
                "error_code": CLIErrorCode.DEPENDENCY_NOT_FOUND,
                "error": f"Required object not found: {obj2}",
                "message": "FreeCAD not installed - dependency check failed"
            }

    return {
        "success": True,
        "mock": True,
        "category": category,
        "name": name,
        "type": sub_type,
        "object_handle": handle,
        "params": params,
        "bounding_box": {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100, "z_min": 0, "z_max": 100},
        "geometry": {"vertex_count": 100, "face_count": 200},
        "validation_warnings": [],
        "message": "FreeCAD not installed - returning mock data"
    }
