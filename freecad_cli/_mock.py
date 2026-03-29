# -*- coding: utf-8 -*-
"""
Mock State Module
=================

Provides _MockState for tracking mock objects when FreeCAD is not installed.
Used by FreeCADWrapper to give consistent, stateful mock responses across
a single Python process session.

Provides:
- Object tracking with type information
- Dependency tracking between objects
- Unified mock result generation with geometry data
"""

from typing import Any, Dict, List, Optional

from ._mock_geometry import MockGeometry


# Global mock state instance
_mock_state: Optional["_MockState"] = None


class _MockState:
    """
    Tracks mock objects across CLI invocations so `list_objects`,
    `get_object_info`, and `delete_object` reflect what was actually created
    during the session.

    Enhanced with:
    - Dependency tracking between objects
    - Unified result generation with geometry data
    - TypeId mapping for all FreeCAD types
    """

    def __init__(self) -> None:
        self._objects: Dict[str, Dict[str, Any]] = {}
        self._dependencies: Dict[str, Dict[str, Any]] = {}
        self._next_handle: int = 0

    def _generate_handle(self, category: str, name: str) -> str:
        """Generate a unique mock handle for an object"""
        self._next_handle += 1
        return f"mock:{category.lower()}/{name}"

    def add(self, category: str, name: str, sub_type: str = "",
            params: Optional[Dict] = None, label: str = "",
            dependencies: Optional[List[str]] = None) -> str:
        """
        Record a newly created mock object.

        Returns:
            The generated mock handle for this object
        """
        handle = self._generate_handle(category, name)
        self._objects[name] = {
            "category": category,
            "type": sub_type,
            "params": params or {},
            "label": label or name,
            "handle": handle,
            "dependencies": dependencies or [],
        }

        # Track dependencies
        self._dependencies[handle] = {
            "name": name,
            "created_by": None,  # Will be set by caller
            "depends_on": dependencies or [],
        }

        return handle

    def list_objects(self, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return all tracked objects, optionally filtered by type."""
        objects = []
        for name, v in self._objects.items():
            fc_type = self._type_freecad(name)
            if filter_type is None or filter_type in fc_type:
                objects.append({
                    "name": name,
                    "type": fc_type,
                    "label": v["label"],
                    "handle": v["handle"],
                })
        return objects

    def get_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Return info for a tracked object, or None if not found."""
        if name not in self._objects:
            return None
        v = self._objects[name]
        return {
            "name": name,
            "label": v["label"],
            "type": self._type_freecad(name),
            "category": v["category"],
            "handle": v["handle"],
            "params": v["params"],
        }

    def get_by_handle(self, handle: str) -> Optional[Dict[str, Any]]:
        """Get object info by mock handle"""
        for v in self._objects.values():
            if v.get("handle") == handle:
                return v
        return None

    def exists(self, name: str) -> bool:
        """Check if an object exists in mock state"""
        return name in self._objects

    def delete(self, name: str) -> bool:
        """Remove a tracked object. Returns True if it existed."""
        if name in self._objects:
            del self._objects[name]
            return True
        return False

    def clear(self) -> None:
        """Clear all tracked objects."""
        self._objects.clear()
        self._dependencies.clear()

    def _type_freecad(self, name: str) -> str:
        """Map category to FreeCAD TypeId string."""
        v = self._objects.get(name, {})
        cat = v.get("category", "Part")
        mapping = {
            "Part": "Part::Feature",
            "Sketch": "Sketcher::SketchObject",
            "Draft": "Draft::Feature",
            "Mesh": "Mesh::Feature",
            "Surface": "Surface::Feature",
            "Arch": "Arch::Feature",
            "Boolean": "Part::Boolean",
            "PartDesign": "PartDesign::Body",
            "TechDraw": "TechDraw::Page",
            "Spreadsheet": "Spreadsheet::Sheet",
            "FEM": "Fem::FemAnalysis",
            "Assembly": "Assembly::Assembly",
            "Path": "Path::Profile",
            "Image": "Image::ImagePlane",
            "Material": "Material::StandardMaterial",
            "Inspection": "Inspection::Feature",
            "Info": "Info::Object",
        }
        return mapping.get(cat, "Part::Feature")

    def get_dependencies(self, name: str) -> List[str]:
        """Get list of objects this object depends on"""
        if name not in self._objects:
            return []
        return self._objects[name].get("dependencies", [])


def get_mock_state() -> _MockState:
    """Get or create the global mock state instance."""
    global _mock_state
    if _mock_state is None:
        _mock_state = _MockState()
    return _mock_state


def reset_mock_state() -> None:
    """Reset the global mock state (mainly for testing)"""
    global _mock_state
    if _mock_state is not None:
        _mock_state.clear()
    _mock_state = _MockState()


def create_mock_result(category: str, name: str, sub_type: str = "",
                       params: Optional[Dict] = None,
                       validation_result: Optional[Any] = None) -> Dict[str, Any]:
    """
    Create a unified mock result with geometry data.

    This is the standard format for all mock responses when FreeCAD is not available.

    Args:
        category: Object category (Part, Sketch, Draft, etc.)
        name: Object name
        sub_type: Specific type (Box, Cylinder, etc.)
        params: Creation parameters
        validation_result: Optional ValidationResult from MockValidators

    Returns:
        Standardized mock result dictionary
    """
    params = params or {}

    # Calculate geometry if applicable
    geometry = {}
    bounding_box = {}

    if category == "Part" and sub_type in MockGeometry.__dict__:
        bounding_box = MockGeometry.get_bounding_box(sub_type, params)
        geometry = MockGeometry.get_geometry(sub_type, params)

    # Generate handle
    handle = f"mock:{category.lower()}/{name}"

    # Get validation info
    warnings = []
    if validation_result and hasattr(validation_result, 'warnings'):
        warnings = validation_result.warnings

    result = {
        "success": True,
        "mock": True,
        "category": category,
        "name": name,
        "type": sub_type,
        "object_type": _MockState()._type_freecad(name) if hasattr(_MockState(), '_type_freecad') else "Part::Feature",
        "object_handle": handle,
        "params": params,
        "bounding_box": bounding_box,
        "geometry": geometry,
        "validation_warnings": warnings,
        "message": "FreeCAD not installed - returning mock data"
    }

    return result
