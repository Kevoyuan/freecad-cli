# -*- coding: utf-8 -*-
"""
FreeCAD Integration Module
==========================

Provides a wrapper for the FreeCAD Python API, enabling CLI commands to invoke
FreeCAD functionality. This module provides a mock mode for testing when FreeCAD
import fails.

Architecture: domain methods are split into private sub-modules
(_part.py, _sketch.py, etc.) and imported here for assignment to FreeCADWrapper.
"""

import sys
import os
import ast
import threading
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

# Thread-safety lock for global module state
_lock = threading.Lock()

# FreeCAD import status tracking
FREECAD_AVAILABLE = False
_freecad_module = None
_part_module = None
_draft_module = None
_arch_module = None
_sketcher_module = None
_mesh_module = None
_surface_module = None
_techdraw_module = None
_spreadsheet_module = None
_path_module = None
_fem_module = None
_image_module = None

# Common FreeCAD installation paths per platform
_FREECAD_PATHS = {
    "darwin": "/Applications/FreeCAD.app/Contents/Resources",
    "linux": "/usr/lib/freecad-python3",
    "win32": r"C:\Program Files\FreeCAD 0.19\bin",
}


def _configure_freecad_env() -> bool:
    """
    Auto-detect and configure FreeCAD environment variables.

    FreeCAD's Python modules are bundled in the app/Resources/lib directory,
    not in the standard Python path. This function tries common install locations
    and sets up the environment so FreeCAD can be imported.

    Returns:
        True if FreeCAD environment was auto-configured, False otherwise.
    """
    import platform

    system = platform.system().lower()
    freecad_base = _FREECAD_PATHS.get(system)

    if not freecad_base or not Path(freecad_base).exists():
        # Try to find FreeCAD.app on macOS
        if system == "darwin":
            app_path = Path("/Applications/FreeCAD.app/Contents/Resources")
            if app_path.exists():
                freecad_base = str(app_path)

    if not freecad_base or not Path(freecad_base).exists():
        return False

    lib_dir = Path(freecad_base) / "lib"
    if not lib_dir.exists():
        return False

    # Add lib directory to PYTHONPATH if not already there
    if str(lib_dir) not in sys.path:
        sys.path.insert(0, str(lib_dir))

    # Set library path for dynamic linker (Linux/macOS)
    if system == "darwin":
        os.environ.setdefault("DYLD_LIBRARY_PATH", str(lib_dir))
        os.environ.setdefault("LD_LIBRARY_PATH", str(lib_dir))
    elif system == "linux":
        os.environ.setdefault("LD_LIBRARY_PATH", str(lib_dir))

    # Set PYTHONHOME if not set
    os.environ.setdefault("PYTHONHOME", freecad_base)
    os.environ.setdefault("PYTHONPATH", str(lib_dir))

    return True


def check_freecad() -> bool:
    """Check if FreeCAD is available"""
    global FREECAD_AVAILABLE, _freecad_module, _part_module, _draft_module
    global _arch_module, _sketcher_module, _mesh_module, _surface_module
    global _techdraw_module, _spreadsheet_module, _path_module, _fem_module
    global _image_module

    with _lock:
        if FREECAD_AVAILABLE:
            return True

        # Auto-configure FreeCAD environment (sets PYTHONPATH, library paths)
        _configure_freecad_env()

        try:
            import FreeCAD as fc
            import Part
            import Sketcher
            import Mesh
            import Surface

            # Check FreeCAD version >= 0.19.0
            version = fc.Version()
            if isinstance(version, tuple):
                if version < (0, 19, 0):
                    return False
            elif isinstance(version, list):
                # FreeCAD 1.x returns ['major', 'minor', 'patch', ...]
                try:
                    major, minor, patch = int(version[0]), int(version[1]), int(version[2])
                    if (major, minor, patch) < (0, 19, 0):
                        return False
                except (ValueError, IndexError):
                    # If we can't parse version, assume it's recent enough
                    pass
            else:
                # String version
                if version < "0.19.0":
                    return False

            _freecad_module = fc
            _part_module = Part
            _sketcher_module = Sketcher
            _mesh_module = Mesh
            _surface_module = Surface

            # Draft and Arch require PySide6/Qt GUI bindings — optional for CLI
            try:
                import Draft
                _draft_module = Draft
            except ImportError:
                _draft_module = None

            try:
                import Arch
                _arch_module = Arch
            except ImportError:
                _arch_module = None

            # Try to import optional modules
            try:
                import TechDraw
                _techdraw_module = TechDraw
            except ImportError:
                _techdraw_module = None

            try:
                import Spreadsheet
                _spreadsheet_module = Spreadsheet
            except ImportError:
                _spreadsheet_module = None

            try:
                import Path
                _path_module = Path
            except ImportError:
                _path_module = None

            try:
                import Fem
                _fem_module = Fem
            except ImportError:
                _fem_module = None

            try:
                import Image
                _image_module = Image
            except ImportError:
                _image_module = None

            FREECAD_AVAILABLE = True
            return True
        except ImportError:
            FREECAD_AVAILABLE = False
            return False


# Import domain methods from sub-modules and bind to FreeCADWrapper
from ._part import (
    _part_create_part,
    _part_mock_result as _mock_result,
)
from ._sketch import (
    _sketch_create_sketch,
    _sketch_add_geometry,
)
from ._draft import _draft_create
from ._arch import _arch_create
from ._boolean import _boolean_op
from ._mesh import _mesh_create, _mesh_from_shape, _mesh_boolean
from ._surface import _surface_create, _surface_from_edges
from ._partdesign import (
    _partdesign_body,
    _partdesign_pad,
    _partdesign_pocket,
    _partdesign_hole,
    _partdesign_groove,
    _partdesign_revolution,
    _partdesign_fillet,
    _partdesign_chamfer,
)
from ._export import (
    _export_document,
    _export_get_object_info as get_object_info,
    _export_list_objects as list_objects,
    _export_delete_object as delete_object,
)
from ._techdraw import (
    _techdraw_create_page,
    _techdraw_add_view,
    _techdraw_add_dimension,
    _techdraw_export,
)
from ._spreadsheet import (
    _spreadsheet_create,
    _spreadsheet_set_cell,
    _spreadsheet_set_formula,
    _spreadsheet_link,
)
from ._assembly import (
    _assembly_create,
    _assembly_add_part,
    _assembly_add_constraint,
)
from ._path import (
    _path_create_job,
    _path_add_operation,
    _path_export_gcode,
)
from ._fem import (
    _fem_create_analysis,
    _fem_add_material,
    _fem_add_bc as fem_add_boundary_condition,
    _fem_run as fem_run_analysis,
)
from ._image import _image_import, _image_scale
from ._material import _material_create, _material_get_standard
from ._inspection import _inspection_create_check, _inspection_measure_distance


class FreeCADWrapper:
    """FreeCAD functionality wrapper class"""

    # Cache TTL in seconds - short enough for responsiveness, long enough to avoid repeated doc traversal
    _OBJECTS_CACHE_TTL = 1.0

    def __init__(self, headless: bool = True):
        """
        Initialize FreeCAD wrapper

        Args:
            headless: Whether to use headless mode (no GUI)
        """
        self.headless = headless
        self._doc = None
        self._initialized = False
        # Objects list cache to avoid expensive doc.Objects traversal on every call
        self._objects_cache = {}  # key: filter_type (None for all), value: (list, timestamp)
        self._objects_cache_lock = threading.Lock()

    # -------------------------------------------------------------------------
    # Core / Document
    # -------------------------------------------------------------------------

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize FreeCAD environment

        Returns:
            Initialization status information
        """
        if not check_freecad():
            return {
                "success": False,
                "error": "FreeCAD is not installed or cannot be imported",
                "available": False
            }

        try:
            # Reuse existing document if already initialized
            if self._doc is None:
                self._doc = _freecad_module.newDocument("CLI_Document")

            self._initialized = True
            return {
                "success": True,
                "document": self._doc.Name if self._doc else None,
                "headless": self.headless,
                "available": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "available": True
            }

    def get_document(self):
        """Get the current document object"""
        if not self._doc:
            self.initialize()
        return self._doc

    # -------------------------------------------------------------------------
    # Part module
    # -------------------------------------------------------------------------
    create_part = _part_create_part

    # -------------------------------------------------------------------------
    # Sketch module
    # -------------------------------------------------------------------------
    create_sketch = _sketch_create_sketch
    add_sketch_geometry = _sketch_add_geometry

    # -------------------------------------------------------------------------
    # Draft module
    # -------------------------------------------------------------------------
    create_draft_object = _draft_create

    # -------------------------------------------------------------------------
    # Arch module
    # -------------------------------------------------------------------------
    create_arch_object = _arch_create

    # -------------------------------------------------------------------------
    # Boolean module
    # -------------------------------------------------------------------------
    boolean_operation = _boolean_op

    # -------------------------------------------------------------------------
    # Mesh module
    # -------------------------------------------------------------------------
    create_mesh_object = _mesh_create
    mesh_from_shape = _mesh_from_shape
    mesh_boolean = _mesh_boolean

    # -------------------------------------------------------------------------
    # Surface module
    # -------------------------------------------------------------------------
    create_surface = _surface_create
    surface_from_edges = _surface_from_edges

    # -------------------------------------------------------------------------
    # PartDesign module
    # -------------------------------------------------------------------------
    create_partdesign_body = _partdesign_body
    create_pad = _partdesign_pad
    create_pocket = _partdesign_pocket
    create_hole = _partdesign_hole
    create_groove = _partdesign_groove
    create_revolution = _partdesign_revolution
    create_fillet = _partdesign_fillet
    create_chamfer = _partdesign_chamfer

    # -------------------------------------------------------------------------
    # Export / Document operations
    # -------------------------------------------------------------------------
    export_document = _export_document

    # -------------------------------------------------------------------------
    # TechDraw module
    # -------------------------------------------------------------------------
    techdraw_create_page = _techdraw_create_page
    techdraw_add_view = _techdraw_add_view
    techdraw_add_dimension = _techdraw_add_dimension
    techdraw_export = _techdraw_export

    # -------------------------------------------------------------------------
    # Spreadsheet module
    # -------------------------------------------------------------------------
    spreadsheet_create = _spreadsheet_create
    spreadsheet_set_cell = _spreadsheet_set_cell
    spreadsheet_set_formula = _spreadsheet_set_formula
    spreadsheet_link = _spreadsheet_link

    # -------------------------------------------------------------------------
    # Assembly module
    # -------------------------------------------------------------------------
    assembly_create = _assembly_create
    assembly_add_part = _assembly_add_part
    assembly_add_constraint = _assembly_add_constraint

    # -------------------------------------------------------------------------
    # Path module
    # -------------------------------------------------------------------------
    path_create_job = _path_create_job
    path_add_operation = _path_add_operation
    path_export_gcode = _path_export_gcode

    # -------------------------------------------------------------------------
    # FEM module
    # -------------------------------------------------------------------------
    fem_create_analysis = _fem_create_analysis
    fem_add_material = _fem_add_material
    fem_add_boundary_condition = fem_add_boundary_condition
    fem_run_analysis = fem_run_analysis

    # -------------------------------------------------------------------------
    # Image module
    # -------------------------------------------------------------------------
    image_import = _image_import
    image_scale = _image_scale

    # -------------------------------------------------------------------------
    # Material module
    # -------------------------------------------------------------------------
    material_create = _material_create
    material_get_standard = _material_get_standard

    # -------------------------------------------------------------------------
    # Inspection module
    # -------------------------------------------------------------------------
    inspection_create_check = _inspection_create_check
    inspection_measure_distance = _inspection_measure_distance

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _get_bounding_box(self, obj) -> Dict[str, float]:
        """Get bounding box of object"""
        try:
            if hasattr(obj, 'Shape') and obj.Shape:
                bb = obj.Shape.BoundBox
                return {
                    "x_min": bb.XMin,
                    "x_max": bb.XMax,
                    "y_min": bb.YMin,
                    "y_max": bb.YMax,
                    "z_min": bb.ZMin,
                    "z_max": bb.ZMax
                }
        except:
            pass
        return {}

    def _invalidate_objects_cache(self):
        """Invalidate the objects list cache - call after creating or deleting objects"""
        with self._objects_cache_lock:
            self._objects_cache.clear()

    def _get_cached_objects(self, filter_type: Optional[str]) -> Tuple[Optional[List], bool]:
        """
        Get cached objects list if valid.

        Returns:
            Tuple of (cached_list or None, is_valid)
        """
        import time
        with self._objects_cache_lock:
            cache_key = filter_type
            if cache_key in self._objects_cache:
                cached_list, timestamp = self._objects_cache[cache_key]
                if time.time() - timestamp < self._OBJECTS_CACHE_TTL:
                    return cached_list, True
            return None, False

    def _set_cached_objects(self, filter_type: Optional[str], objects: List):
        """Store objects list in cache"""
        import time
        with self._objects_cache_lock:
            self._objects_cache[filter_type] = (objects, time.time())

    # -------------------------------------------------------------------------
    # Public document operations (imported from _export)
    # -------------------------------------------------------------------------
    get_object_info = staticmethod(lambda self, name: _export_get_object_info(self, name))
    list_objects = staticmethod(lambda self, ft=None: _export_list_objects(self, ft))
    delete_object = staticmethod(lambda self, name: _export_delete_object(self, name))


# Fix the bound methods properly
FreeCADWrapper.get_object_info = lambda self, name: get_object_info(self, name)
FreeCADWrapper.list_objects = lambda self, ft=None: list_objects(self, ft)
FreeCADWrapper.delete_object = lambda self, name: delete_object(self, name)


# ---------------------------------------------------------------------------
# Re-export mock state helper
# ---------------------------------------------------------------------------
from ._mock import get_mock_state


# Global wrapper instance
_wrapper = None


def get_wrapper(headless: bool = True) -> FreeCADWrapper:
    """Get global wrapper instance"""
    global _wrapper
    with _lock:
        if _wrapper is None:
            _wrapper = FreeCADWrapper(headless=headless)
        return _wrapper
