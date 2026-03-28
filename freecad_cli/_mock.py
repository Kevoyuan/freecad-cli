# -*- coding: utf-8 -*-
"""
Mock State Module
=================

Provides _MockState for tracking mock objects when FreeCAD is not installed.
Used by FreeCADWrapper to give consistent, stateful mock responses across
a single Python process session.
"""

from typing import Any, Dict, List, Optional


# Global mock state instance
_mock_state = None


class _MockState:
    """
    Tracks mock objects across CLI invocations so `list_objects`,
    `get_object_info`, and `delete_object` reflect what was actually created
    during the session.
    """

    def __init__(self) -> None:
        self._objects: Dict[str, Dict[str, Any]] = {}

    def add(self, category: str, name: str, sub_type: str = "",
            params: Optional[Dict] = None, label: str = "") -> None:
        """Record a newly created mock object."""
        self._objects[name] = {
            "category": category,
            "type": sub_type,
            "params": params or {},
            "label": label or name,
        }

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
        }

    def delete(self, name: str) -> bool:
        """Remove a tracked object. Returns True if it existed."""
        if name in self._objects:
            del self._objects[name]
            return True
        return False

    def clear(self) -> None:
        """Clear all tracked objects."""
        self._objects.clear()

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


def get_mock_state() -> _MockState:
    """Get or create the global mock state instance."""
    global _mock_state
    if _mock_state is None:
        _mock_state = _MockState()
    return _mock_state
