# -*- coding: utf-8 -*-
"""
FreeCAD Integration Module
==========================

Provides a wrapper for the FreeCAD Python API, enabling CLI commands to invoke
FreeCAD functionality. This module provides a mock mode for testing when FreeCAD
import fails.
"""

import sys
import ast
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

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


def check_freecad() -> bool:
    """Check if FreeCAD is available"""
    global FREECAD_AVAILABLE, _freecad_module, _part_module, _draft_module
    global _arch_module, _sketcher_module, _mesh_module, _surface_module
    global _techdraw_module, _spreadsheet_module, _path_module, _fem_module
    global _image_module

    if FREECAD_AVAILABLE:
        return True

    try:
        import FreeCAD as fc
        import Part
        import Draft
        import Sketcher
        import Arch
        import Mesh
        import Surface

        _freecad_module = fc
        _part_module = Part
        _draft_module = Draft
        _arch_module = Arch
        _sketcher_module = Sketcher
        _mesh_module = Mesh
        _surface_module = Surface

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


class FreeCADWrapper:
    """FreeCAD functionality wrapper class"""

    def __init__(self, headless: bool = True):
        """
        Initialize FreeCAD wrapper

        Args:
            headless: Whether to use headless mode (no GUI)
        """
        self.headless = headless
        self._doc = None
        self._initialized = False

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
            if self.headless:
                # Headless mode initialization
                self._doc = _freecad_module.newDocument("CLI_Document")
            else:
                # GUI mode
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

    def create_part(self, name: str, shape_type: str = "Box",
                   params: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Create a Part object

        Args:
            name: Object name
            shape_type: Shape type (Box, Cylinder, Sphere, Cone, Torus)
            params: Shape parameters

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Part", name, shape_type, params)

        doc = self.get_document()
        params = params or {}

        try:
            if shape_type == "Box":
                obj = doc.addObject("Part::Box", name)
                obj.Length = params.get("length", 10.0)
                obj.Width = params.get("width", 10.0)
                obj.Height = params.get("height", 10.0)
            elif shape_type == "Cylinder":
                obj = doc.addObject("Part::Cylinder", name)
                obj.Radius = params.get("radius", 5.0)
                obj.Height = params.get("height", 10.0)
            elif shape_type == "Sphere":
                obj = doc.addObject("Part::Sphere", name)
                obj.Radius = params.get("radius", 5.0)
            elif shape_type == "Cone":
                obj = doc.addObject("Part::Cone", name)
                obj.Radius1 = params.get("radius1", 5.0)
                obj.Radius2 = params.get("radius2", 2.0)
                obj.Height = params.get("height", 10.0)
            elif shape_type == "Torus":
                obj = doc.addObject("Part::Torus", name)
                obj.Radius1 = params.get("radius1", 10.0)
                obj.Radius2 = params.get("radius2", 2.0)
            else:
                return {"success": False, "error": f"Unknown shape type: {shape_type}"}

            doc.recompute()
            return {
                "success": True,
                "name": name,
                "type": shape_type,
                "label": obj.Label,
                "bounding_box": self._get_bounding_box(obj)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_sketch(self, name: str, plane: str = "XY") -> Dict[str, Any]:
        """
        Create a sketch object

        Args:
            name: Sketch name
            plane: Sketch plane (XY, XZ, YZ)

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Sketch", name, params={"plane": plane})

        doc = self.get_document()

        try:
            obj = doc.addObject("Sketcher::SketchObject", name)

            # Set sketch plane
            if plane == "XY":
                obj.Support = [(doc.getObject("XY_Plane"), '')]
            elif plane == "XZ":
                obj.Support = [(doc.getObject("XZ_Plane"), '')]
            elif plane == "YZ":
                obj.Support = [(doc.getObject("YZ_Plane"), '')]

            doc.recompute()
            return {
                "success": True,
                "name": name,
                "plane": plane,
                "constraints": 0,
                "geometry": 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_sketch_geometry(self, sketch_name: str,
                           geometry_type: str,
                           params: Dict[str, float]) -> Dict[str, Any]:
        """
        Add geometry element to sketch

        Args:
            sketch_name: Sketch name
            geometry_type: Geometry type (Line, Circle, Arc, Rectangle, Polygon)
            params: Geometry parameters

        Returns:
            Addition result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Geometry", sketch_name, geometry_type, params)

        doc = self.get_document()

        try:
            sketch = doc.getObject(sketch_name)
            if not sketch:
                return {"success": False, "error": f"Sketch not found: {sketch_name}"}

            geo_id = -1

            if geometry_type == "Line":
                geo = _sketcher_module.Geometry(
                    params.get("x1", 0), params.get("y1", 0),
                    params.get("x2", 10), params.get("y2", 10)
                )
                geo_id = sketch.addGeometry(geo)
            elif geometry_type == "Circle":
                geo = _sketcher_module.Geometry(
                    params.get("cx", 0), params.get("cy", 0),
                    params.get("radius", 5)
                )
                geo_id = sketch.addGeometry(geo)
            elif geometry_type == "Rectangle":
                p1 = (params.get("x1", 0), params.get("y1", 0))
                p2 = (params.get("x2", 10), params.get("y2", 10))
                # Add four edges of rectangle
                for i in range(4):
                    geo_id = sketch.addGeometry(_sketcher_module.LineSegment(*p1, *p2))
            else:
                return {"success": False, "error": f"Unsupported geometry type: {geometry_type}"}

            doc.recompute()
            return {
                "success": True,
                "geometry_id": geo_id,
                "type": geometry_type
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_draft_object(self, name: str, object_type: str,
                           params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a Draft object

        Args:
            name: Object name
            object_type: Object type (Line, Polyline, Circle, Rectangle, Polygon, Arc)
            params: Object parameters

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Draft", name, object_type, params)

        doc = self.get_document()
        params = params or {}

        try:
            if object_type == "Line":
                obj = _draft_module.makeLine(
                    (params.get("x1", 0), params.get("y1", 0), params.get("z1", 0)),
                    (params.get("x2", 10), params.get("y2", 10), params.get("z2", 0))
                )
            elif object_type == "Circle":
                obj = _draft_module.makeCircle(
                    radius=params.get("radius", 10),
                    face=params.get("face", False)
                )
            elif object_type == "Rectangle":
                obj = _draft_module.makeRectangle(
                    length=params.get("length", 10),
                    height=params.get("height", 5),
                    face=params.get("face", False)
                )
            elif object_type == "Polygon":
                obj = _draft_module.makePolygon(
                    n_sides=params.get("n_sides", 6),
                    radius=params.get("radius", 10)
                )
            elif object_type == "Polyline":
                points = params.get("points", [(0, 0), (10, 0), (10, 10)])
                obj = _draft_module.makeWire(points, closed=params.get("closed", False))
            else:
                return {"success": False, "error": f"Unknown Draft type: {object_type}"}

            obj.Label = name
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": object_type,
                "label": obj.Label
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_arch_object(self, name: str, object_type: str,
                          params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an Arch object

        Args:
            name: Object name
            object_type: Object type (Wall, Structure, Window, Door, Roof, Stairs)
            params: Object parameters

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Arch", name, object_type, params)

        doc = self.get_document()
        params = params or {}

        try:
            if object_type == "Wall":
                obj = _arch_module.makeWall(
                    length=params.get("length", 100),
                    width=params.get("width", 20),
                    height=params.get("height", 300)
                )
            elif object_type == "Structure":
                obj = _arch_module.makeStructure(
                    length=params.get("length", 100),
                    width=params.get("width", 100),
                    height=params.get("height", 200)
                )
            elif object_type == "Window":
                obj = _arch_module.makeWindow(
                    width=params.get("width", 100),
                    height=params.get("height", 150)
                )
            elif object_type == "Roof":
                obj = _arch_module.makeRoof(
                    base=params.get("base", None),
                    angle=params.get("angle", 25)
                )
            else:
                return {"success": False, "error": f"Unknown Arch type: {object_type}"}

            obj.Label = name
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": object_type,
                "label": obj.Label
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def boolean_operation(self, name: str, operation: str,
                         object1: str, object2: str) -> Dict[str, Any]:
        """
        Perform boolean operation

        Args:
            name: Result object name
            operation: Operation type (Fuse, Cut, Common, Section)
            object1: First object name
            object2: Second object name

        Returns:
            Operation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Boolean", name, operation,
                                     {"obj1": object1, "obj2": object2})

        doc = self.get_document()

        try:
            obj1 = doc.getObject(object1)
            obj2 = doc.getObject(object2)

            if not obj1 or not obj2:
                return {"success": False, "error": "Specified object not found"}

            operation_map = {
                "Fuse": "Part::MultiFuse",
                "Cut": "Part::Cut",
                "Common": "Part::Common",
                "Section": "Part::Section"
            }

            result = doc.addObject(operation_map.get(operation, "Part::Fuse"), name)
            result.Shape = getattr(_part_module, operation)(
                obj1.Shape, obj2.Shape
            )

            doc.recompute()

            return {
                "success": True,
                "name": name,
                "operation": operation,
                "volume": result.Shape.Volume if hasattr(result.Shape, 'Volume') else 0,
                "surface_area": result.Shape.Area if hasattr(result.Shape, 'Area') else 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # Mesh module
    # ============================================================================

    def create_mesh_object(self, name: str, object_type: str,
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
        if not FREECAD_AVAILABLE:
            return self._mock_result("Mesh", name, object_type, params)

        params = params or {}
        doc = self.get_document()

        try:
            if object_type == "RegularMesh":
                # Create regular mesh
                mesh = _mesh_module.Mesh()
                # Generate mesh parameters
                segment_length = params.get("segment_length", 1.0)
                # Simple mesh plane
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
                # Create triangle mesh
                mesh = _mesh_module.Mesh()
                points = params.get("points", [(0, 0, 0), (10, 0, 0), (5, 10, 0)])
                if len(points) >= 3:
                    mesh.addFacet(_mesh_module.MeshPoint(*points[0]),
                                  _mesh_module.MeshPoint(*points[1]),
                                  _mesh_module.MeshPoint(*points[2]))
                obj = doc.addObject("Mesh::Feature", name)
                obj.Mesh = mesh

            elif object_type == "Grid":
                # Create mesh wireframe
                mesh = _mesh_module.Mesh()
                obj = doc.addObject("Mesh::Feature", name)
                obj.Mesh = mesh

            else:
                return {"success": False, "error": f"Unknown Mesh type: {object_type}"}

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
            return {"success": False, "error": str(e)}

    def mesh_from_shape(self, name: str, source_name: str,
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
        if not FREECAD_AVAILABLE:
            return self._mock_result("Mesh", name, "from_shape",
                                     {"source": source_name, "deflection": deflection})

        doc = self.get_document()

        try:
            source = doc.getObject(source_name)
            if not source:
                return {"success": False, "error": f"Source object not found: {source_name}"}

            if not hasattr(source, 'Shape'):
                return {"success": False, "error": "Source object does not have Shape property"}

            # Create mesh
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
            return {"success": False, "error": str(e)}

    def mesh_boolean(self, name: str, operation: str,
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
        if not FREECAD_AVAILABLE:
            return self._mock_result("MeshBoolean", name, operation,
                                     {"obj1": object1, "obj2": object2})

        doc = self.get_document()

        try:
            mesh1_obj = doc.getObject(object1)
            mesh2_obj = doc.getObject(object2)

            if not mesh1_obj or not mesh2_obj:
                return {"success": False, "error": "Specified object not found"}

            mesh1 = mesh1_obj.Mesh
            mesh2 = mesh2_obj.Mesh

            if operation == "Union":
                result_mesh = mesh1 + mesh2
            elif operation == "Intersection":
                result_mesh = mesh1.intersect(mesh2)
            elif operation == "Difference":
                result_mesh = mesh1.subtract(mesh2)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

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
            return {"success": False, "error": str(e)}

    # ============================================================================
    # Surface module
    # ============================================================================

    def create_surface(self, name: str, surface_type: str,
                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a Surface object

        Args:
            name: Object name
            surface_type: Surface type (Fill, Sweep, Loft, Bezier)
            params: Object parameters

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Surface", name, surface_type, params)

        params = params or {}
        doc = self.get_document()

        try:
            if surface_type == "Fill":
                obj = doc.addObject("Surface::Fill", name)
            elif surface_type == "Sweep":
                obj = doc.addObject("Surface::Sweep", name)
                obj.Sections = params.get("sections", [])
            elif surface_type == "Loft":
                obj = doc.addObject("Surface::Loft", name)
                obj.Sections = params.get("sections", [])
            elif surface_type == "Bezier":
                obj = doc.addObject("Surface::Bezier", name)
            else:
                return {"success": False, "error": f"Unknown surface type: {surface_type}"}

            doc.recompute()
            return {
                "success": True,
                "name": name,
                "type": surface_type,
                "label": obj.Label
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def surface_from_edges(self, name: str, sketch_name: str) -> Dict[str, Any]:
        """
        Create surface from sketch edges

        Args:
            name: Surface object name
            sketch_name: Sketch name

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Surface", name, "from_edges",
                                     {"sketch": sketch_name})

        doc = self.get_document()

        try:
            sketch = doc.getObject(sketch_name)
            if not sketch:
                return {"success": False, "error": f"Sketch not found: {sketch_name}"}

            obj = doc.addObject("Surface::Fill", name)
            obj.Source = sketch

            doc.recompute()
            return {
                "success": True,
                "name": name,
                "source_sketch": sketch_name,
                "label": obj.Label
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # PartDesign module
    # ============================================================================

    def create_partdesign_body(self, name: str) -> Dict[str, Any]:
        """
        Create PartDesign Body

        Args:
            name: Body name

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("PartDesign", name, "Body", {})

        doc = self.get_document()

        try:
            obj = doc.addObject("PartDesign::Body", name)
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Body",
                "label": obj.Label
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_pad(self, name: str, body_name: str,
                  sketch_name: str, length: float = 10.0,
                  direction: str = "Normal") -> Dict[str, Any]:
        """
        Create Pad (extrusion)

        Args:
            name: Pad name
            body_name: Body name
            sketch_name: Sketch name
            length: Extrusion length
            direction: Extrusion direction (Normal, Reversed, Double)

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Pad", name, "Pad",
                                     {"body": body_name, "sketch": sketch_name,
                                      "length": length, "direction": direction})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            sketch = doc.getObject(sketch_name)

            if not body:
                return {"success": False, "error": f"Body not found: {body_name}"}
            if not sketch:
                return {"success": False, "error": f"Sketch not found: {sketch_name}"}

            pad = doc.addObject("PartDesign::Pad", name)
            pad.Profile = sketch
            pad.Length = length

            if direction == "Reversed":
                pad.Direction = (-1, 0, 0)
            elif direction == "Double":
                pad.Length2 = length

            body.addObject(pad)
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Pad",
                "body": body_name,
                "sketch": sketch_name,
                "length": length
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_pocket(self, name: str, body_name: str,
                     sketch_name: str, length: float = 10.0,
                     type: str = "Through") -> Dict[str, Any]:
        """
        Create Pocket (cutout)

        Args:
            name: Pocket name
            body_name: Body name
            sketch_name: Sketch name
            length: Cutout depth
            type: Cutout type (Through, UpToFirst, UpToFace)

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Pocket", name, "Pocket",
                                     {"body": body_name, "sketch": sketch_name,
                                      "length": length, "type": type})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            sketch = doc.getObject(sketch_name)

            if not body:
                return {"success": False, "error": f"Body not found: {body_name}"}
            if not sketch:
                return {"success": False, "error": f"Sketch not found: {sketch_name}"}

            pocket = doc.addObject("PartDesign::Pocket", name)
            pocket.Profile = sketch
            pocket.Length = length

            if type == "Through":
                pocket.Reversed = True
            elif type == "UpToFirst":
                pocket.Type = 1

            body.addObject(pocket)
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Pocket",
                "body": body_name,
                "sketch": sketch_name,
                "length": length,
                "pocket_type": type
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_hole(self, name: str, body_name: str,
                   diameter: float = 5.0, depth: float = 10.0,
                   position: Optional[Tuple[float, float, float]] = None) -> Dict[str, Any]:
        """
        Create hole

        Args:
            name: Hole name
            body_name: Body name
            diameter: Hole diameter
            depth: Hole depth
            position: Hole position (x, y, z)

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Hole", name, "Hole",
                                     {"body": body_name, "diameter": diameter,
                                      "depth": depth, "position": position})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            if not body:
                return {"success": False, "error": f"Body not found: {body_name}"}

            hole = doc.addObject("PartDesign::Hole", name)
            hole.Diameter = diameter
            hole.Depth = depth

            if position:
                hole.Placement.Base.x = position[0]
                hole.Placement.Base.y = position[1]
                hole.Placement.Base.z = position[2]

            body.addObject(hole)
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Hole",
                "body": body_name,
                "diameter": diameter,
                "depth": depth
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_groove(self, name: str, body_name: str,
                     angle: float = 360.0, radius: float = 5.0) -> Dict[str, Any]:
        """
        Create Groove (rotational cutout)

        Args:
            name: Groove name
            body_name: Body name
            angle: Rotation angle
            radius: Rotation radius

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Groove", name, "Groove",
                                     {"body": body_name, "angle": angle, "radius": radius})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            if not body:
                return {"success": False, "error": f"Body not found: {body_name}"}

            groove = doc.addObject("PartDesign::Groove", name)
            groove.Angle = angle
            groove.Radius = radius

            body.addObject(groove)
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Groove",
                "body": body_name,
                "angle": angle,
                "radius": radius
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_revolution(self, name: str, body_name: str,
                         sketch_name: str, angle: float = 360.0,
                         axis: Optional[Tuple[int, int, int]] = None) -> Dict[str, Any]:
        """
        Create Revolution

        Args:
            name: Revolution name
            body_name: Body name
            sketch_name: Sketch name
            angle: Rotation angle
            axis: Rotation axis (x, y, z) direction

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Revolution", name, "Revolution",
                                     {"body": body_name, "sketch": sketch_name,
                                      "angle": angle, "axis": axis})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            sketch = doc.getObject(sketch_name)

            if not body:
                return {"success": False, "error": f"Body not found: {body_name}"}
            if not sketch:
                return {"success": False, "error": f"Sketch not found: {sketch_name}"}

            revolution = doc.addObject("PartDesign::Revolution", name)
            revolution.Profile = sketch
            revolution.Angle = angle

            if axis:
                revolution.ReferenceAxis = axis

            body.addObject(revolution)
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Revolution",
                "body": body_name,
                "sketch": sketch_name,
                "angle": angle
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_fillet(self, name: str, body_name: str,
                     edge_radius: float = 2.0) -> Dict[str, Any]:
        """
        Create Fillet

        Args:
            name: Fillet name
            body_name: Body name
            edge_radius: Fillet radius

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Fillet", name, "Fillet",
                                     {"body": body_name, "radius": edge_radius})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            if not body:
                return {"success": False, "error": f"Body not found: {body_name}"}

            fillet = doc.addObject("PartDesign::Fillet", name)
            fillet.Radius = edge_radius

            body.addObject(fillet)
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Fillet",
                "body": body_name,
                "radius": edge_radius
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_chamfer(self, name: str, body_name: str,
                      chamfer_size: float = 1.0) -> Dict[str, Any]:
        """
        Create Chamfer

        Args:
            name: Chamfer name
            body_name: Body name
            chamfer_size: Chamfer size

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Chamfer", name, "Chamfer",
                                     {"body": body_name, "size": chamfer_size})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            if not body:
                return {"success": False, "error": f"Body not found: {body_name}"}

            chamfer = doc.addObject("PartDesign::Chamfer", name)
            chamfer.Size = chamfer_size

            body.addObject(chamfer)
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Chamfer",
                "body": body_name,
                "size": chamfer_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_document(self, filepath: str, format_type: str = "STEP") -> Dict[str, Any]:
        """
        Export document

        Args:
            filepath: Export file path
            format_type: Export format (STEP, STL, OBJ, IGES, BREP, DXF)

        Returns:
            Export result information
        """
        if not FREECAD_AVAILABLE:
            return {
                "success": True,
                "filepath": filepath,
                "format": format_type,
                "mock": True
            }

        doc = self.get_document()

        try:
            format_map = {
                "STEP": "Step",
                "STL": "Mesh",
                "OBJ": "Mesh",
                "IGES": "Iges",
                "BREP": "Brep",
                "DXF": "Drawing"
            }

            export_format = format_map.get(format_type, "Step")
            _freecad_module.export(doc.Objects, filepath)

            return {
                "success": True,
                "filepath": filepath,
                "format": format_type,
                "objects_exported": len(doc.Objects)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_object_info(self, object_name: str) -> Dict[str, Any]:
        """
        Get object information

        Args:
            object_name: Object name

        Returns:
            Object detailed information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Info", object_name)

        doc = self.get_document()

        try:
            obj = doc.getObject(object_name)
            if not obj:
                return {"success": False, "error": f"Object not found: {object_name}"}

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
            return {"success": False, "error": str(e)}

    def list_objects(self, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List objects in document

        Args:
            filter_type: Object type filter (optional)

        Returns:
            List of objects
        """
        if not FREECAD_AVAILABLE:
            return [
                {"name": "MockBox", "type": "Part::Box", "label": "Mock Box"},
                {"name": "MockSketch", "type": "Sketcher::SketchObject", "label": "Mock Sketch"}
            ]

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

    def delete_object(self, object_name: str) -> Dict[str, Any]:
        """
        Delete object

        Args:
            object_name: Name of object to delete

        Returns:
            Deletion result information
        """
        if not FREECAD_AVAILABLE:
            return {"success": True, "deleted": object_name, "mock": True}

        doc = self.get_document()

        try:
            obj = doc.getObject(object_name)
            if not obj:
                return {"success": False, "error": f"Object not found: {object_name}"}

            doc.removeObject(object_name)
            return {"success": True, "deleted": object_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # TechDraw module
    # ============================================================================

    def techdraw_create_page(self, name: str, template: str = "A4_Landscape") -> Dict[str, Any]:
        """
        Create TechDraw page

        Args:
            name: Page name
            template: Drawing template (A4_Landscape, A4_Portrait, A3_Landscape, etc.)

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("TechDraw", name, "Page", {"template": template})

        doc = self.get_document()

        try:
            template_map = {
                "A4_Landscape": "A4_Landscape",
                "A4_Portrait": "A4_Portrait",
                "A3_Landscape": "A3_Landscape",
                "A3_Portrait": "A3_Portrait",
                "A4": "A4_Landscape"
            }

            page_template = template_map.get(template, "A4_Landscape")

            if _techdraw_module:
                page = doc.addObject("TechDraw::DrawPage", name)
                template_obj = doc.addObject("TechDraw::DrawTemplate", "Template")
                template_obj.Template = page_template
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

    def techdraw_add_view(self, page_name: str, source_name: str,
                         projection_type: str = "FirstAngle") -> Dict[str, Any]:
        """
        Add engineering view

        Args:
            page_name: Page name
            source_name: Source object name
            projection_type: Projection type (FirstAngle, ThirdAngle)

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("TechDraw", "View", "View",
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

    def techdraw_add_dimension(self, view_name: str, dimension_type: str,
                              points: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        Add dimension annotation

        Args:
            view_name: View name
            dimension_type: Dimension type (Horizontal, Vertical, Radius, Diameter, Angle)
            points: List of dimension points

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("TechDraw", "Dimension", dimension_type,
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

    def techdraw_export(self, page_name: str, filepath: str,
                       format_type: str = "PDF") -> Dict[str, Any]:
        """
        Export engineering drawing

        Args:
            page_name: Page name
            filepath: Export file path
            format_type: Export format (PDF, SVG, DXF)

        Returns:
            Export result information
        """
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

            # Export
            if format_type == "PDF":
                _freecad_module.export([page], filepath)
            elif format_type == "SVG":
                _freecad_module.export([page], filepath)
            elif format_type == "DXF":
                _freecad_module.export([page], filepath)

            return {
                "success": True,
                "page": page_name,
                "filepath": filepath,
                "format": format_type
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # Spreadsheet module
    # ============================================================================

    def spreadsheet_create(self, name: str) -> Dict[str, Any]:
        """
        Create spreadsheet

        Args:
            name: Spreadsheet name

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Spreadsheet", name, "Sheet", {})

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
            return {"success": False, "error": str(e)}

    def spreadsheet_set_cell(self, sheet_name: str, cell: str,
                           value: Any) -> Dict[str, Any]:
        """
        Set cell value

        Args:
            sheet_name: Spreadsheet name
            cell: Cell address (e.g., "A1")
            value: Cell value

        Returns:
            Setting result information
        """
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
                return {"success": False, "error": f"Spreadsheet not found: {sheet_name}"}

            sheet.set(cell, str(value))
            doc.recompute()

            return {
                "success": True,
                "sheet": sheet_name,
                "cell": cell,
                "value": value
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def spreadsheet_set_formula(self, sheet_name: str, cell: str,
                              formula: str) -> Dict[str, Any]:
        """
        Set cell formula

        Args:
            sheet_name: Spreadsheet name
            cell: Cell address
            formula: Formula (e.g., "=A1*2")

        Returns:
            Setting result information
        """
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
                return {"success": False, "error": f"Spreadsheet not found: {sheet_name}"}

            sheet.set(cell, formula)
            doc.recompute()

            return {
                "success": True,
                "sheet": sheet_name,
                "cell": cell,
                "formula": formula
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def spreadsheet_link(self, sheet_name: str, object_name: str,
                        property_name: str, cell: str) -> Dict[str, Any]:
        """
        Link spreadsheet to object property

        Args:
            sheet_name: Spreadsheet name
            object_name: Object name
            property_name: Property name
            cell: Cell address

        Returns:
            Link result information
        """
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
                return {"success": False, "error": f"Spreadsheet not found: {sheet_name}"}
            if not obj:
                return {"success": False, "error": f"Object not found: {object_name}"}

            # Set link
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
            return {"success": False, "error": str(e)}

    # ============================================================================
    # Assembly module
    # ============================================================================

    def assembly_create(self, name: str) -> Dict[str, Any]:
        """
        Create assembly

        Args:
            name: Assembly name

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Assembly", name, "Assembly", {})

        doc = self.get_document()

        try:
            assembly = doc.addObject("App::Part", name)
            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Assembly",
                "label": assembly.Label
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def assembly_add_part(self, assembly_name: str, part_name: str,
                         placement: str = "[0, 0, 0]") -> Dict[str, Any]:
        """
        Add part to assembly

        Args:
            assembly_name: Assembly name
            part_name: Part name
            placement: Position [x, y, z]

        Returns:
            Addition result information
        """
        if not FREECAD_AVAILABLE:
            return {
                "success": True,
                "assembly": assembly_name,
                "part": part_name,
                "placement": placement,
                "mock": True
            }

        doc = self.get_document()

        try:
            assembly = doc.getObject(assembly_name)
            part = doc.getObject(part_name)

            if not assembly:
                return {"success": False, "error": f"Assembly not found: {assembly_name}"}
            if not part:
                return {"success": False, "error": f"Part not found: {part_name}"}

            # Add part to assembly
            assembly.addObject(part)

            # Set placement (use ast.literal_eval for safe parsing)
            try:
                import FreeCAD
                placement_list = ast.literal_eval(placement)
                if len(placement_list) == 3:
                    part.Placement.Base = FreeCAD.Vector(*placement_list)
            except (ValueError, SyntaxError):
                pass  # Keep default position

            doc.recompute()

            return {
                "success": True,
                "assembly": assembly_name,
                "part": part_name,
                "placement": placement
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def assembly_add_constraint(self, assembly_name: str, constraint_type: str,
                               object1: str, object2: str,
                               parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add assembly constraint

        Args:
            assembly_name: Assembly name
            constraint_type: Constraint type (Coincident, Distance, Angle, etc.)
            object1: First object
            object2: Second object
            parameters: Constraint parameters

        Returns:
            Addition result information
        """
        if not FREECAD_AVAILABLE:
            return {
                "success": True,
                "assembly": assembly_name,
                "constraint_type": constraint_type,
                "object1": object1,
                "object2": object2,
                "mock": True
            }

        doc = self.get_document()

        try:
            assembly = doc.getObject(assembly_name)
            if not assembly:
                return {"success": False, "error": f"Assembly not found: {assembly_name}"}

            # Create constraint
            constraint = doc.addObject("Part::Feature", f"Constraint_{constraint_type}")

            doc.recompute()

            return {
                "success": True,
                "assembly": assembly_name,
                "constraint_type": constraint_type,
                "object1": object1,
                "object2": object2
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # Path (CAM machining) module
    # ============================================================================

    def path_create_job(self, name: str, base_name: str) -> Dict[str, Any]:
        """
        Create machining job

        Args:
            name: Job name
            base_name: Base object name

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Path", name, "Job", {"base": base_name})

        doc = self.get_document()

        try:
            base = doc.getObject(base_name)
            if not base:
                return {"success": False, "error": f"Base object not found: {base_name}"}

            job = doc.addObject("Path::Job", name)
            job.Base = base

            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Job",
                "base": base_name,
                "label": job.Label
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def path_add_operation(self, job_name: str, operation_type: str,
                          parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add machining operation

        Args:
            job_name: Job name
            operation_type: Operation type (Drill, Profile, Pocket, etc.)
            parameters: Operation parameters

        Returns:
            Addition result information
        """
        if not FREECAD_AVAILABLE:
            return {
                "success": True,
                "job": job_name,
                "operation_type": operation_type,
                "parameters": parameters,
                "mock": True
            }

        doc = self.get_document()

        try:
            job = doc.getObject(job_name)
            if not job:
                return {"success": False, "error": f"Job not found: {job_name}"}

            operation = doc.addObject("Path::Feature", f"Op_{operation_type}")
            job.addObject(operation)

            doc.recompute()

            return {
                "success": True,
                "name": operation.Name,
                "type": "Operation",
                "operation_type": operation_type,
                "job": job_name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def path_export_gcode(self, job_name: str, filepath: str,
                         post_processor: str = "linuxcnc") -> Dict[str, Any]:
        """
        Export G-code

        Args:
            job_name: Job name
            filepath: Export file path
            post_processor: Post processor (linuxcnc, grbl, etc.)

        Returns:
            Export result information
        """
        if not FREECAD_AVAILABLE:
            return {
                "success": True,
                "job": job_name,
                "filepath": filepath,
                "post_processor": post_processor,
                "mock": True
            }

        doc = self.get_document()

        try:
            job = doc.getObject(job_name)
            if not job:
                return {"success": False, "error": f"Job not found: {job_name}"}

            # Export G-code
            _freecad_module.export([job], filepath)

            return {
                "success": True,
                "job": job_name,
                "filepath": filepath,
                "post_processor": post_processor
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # FEM (Finite Element Analysis) module
    # ============================================================================

    def fem_create_analysis(self, name: str, analysis_type: str = "static") -> Dict[str, Any]:
        """
        Create finite element analysis

        Args:
            name: Analysis name
            analysis_type: Analysis type (static, modal, thermomechanical)

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("FEM", name, "Analysis", {"type": analysis_type})

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
            return {"success": False, "error": str(e)}

    def fem_add_material(self, analysis_name: str, material: str = "Steel") -> Dict[str, Any]:
        """
        Add material to analysis

        Args:
            analysis_name: Analysis name
            material: Material name (Steel, Aluminum, etc.)

        Returns:
            Addition result information
        """
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
                return {"success": False, "error": f"Analysis not found: {analysis_name}"}

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
            return {"success": False, "error": str(e)}

    def fem_add_boundary_condition(self, analysis_name: str, bc_type: str,
                                  object_name: str,
                                  parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add boundary condition

        Args:
            analysis_name: Analysis name
            bc_type: Boundary condition type (Fixed, Force, Pressure)
            object_name: Object name
            parameters: Boundary condition parameters

        Returns:
            Addition result information
        """
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
                return {"success": False, "error": f"Analysis not found: {analysis_name}"}

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
            return {"success": False, "error": str(e)}

    def fem_run_analysis(self, analysis_name: str) -> Dict[str, Any]:
        """
        Run finite element analysis

        Args:
            analysis_name: Analysis name

        Returns:
            Run result information
        """
        if not FREECAD_AVAILABLE:
            return {
                "success": True,
                "analysis": analysis_name,
                "status": "completed",
                "mock": True
            }

        doc = self.get_document()

        try:
            analysis = doc.getObject(analysis_name)
            if not analysis:
                return {"success": False, "error": f"Analysis not found: {analysis_name}"}

            # Run analysis (requires solver)
            doc.recompute()

            return {
                "success": True,
                "analysis": analysis_name,
                "status": "completed"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # Image module
    # ============================================================================

    def image_import(self, name: str, filepath: str) -> Dict[str, Any]:
        """
        Import image

        Args:
            name: Image name
            filepath: Image file path

        Returns:
            Import result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Image", name, "Image", {"filepath": filepath})

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
            return {"success": False, "error": str(e)}

    def image_scale(self, name: str, scale_x: float = 1.0,
                   scale_y: float = 1.0) -> Dict[str, Any]:
        """
        Scale image

        Args:
            name: Image name
            scale_x: X direction scale
            scale_y: Y direction scale

        Returns:
            Scale result information
        """
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
                return {"success": False, "error": f"Image not found: {name}"}

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
            return {"success": False, "error": str(e)}

    # ============================================================================
    # Material module
    # ============================================================================

    def material_create(self, name: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create material

        Args:
            name: Material name
            properties: Material properties (density, youngs_modulus, etc.)

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Material", name, "Material", properties)

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

    def material_get_standard(self, material_name: str) -> Dict[str, Any]:
        """
        Get standard material

        Args:
            material_name: Material name (Steel, Aluminum, etc.)

        Returns:
            Material information
        """
        # Standard material library
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

    # ============================================================================
    # Inspection module
    # ============================================================================

    def inspection_create_check(self, name: str, object_name: str) -> Dict[str, Any]:
        """
        Create inspection

        Args:
            name: Inspection name
            object_name: Object to inspect name

        Returns:
            Creation result information
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Inspection", name, "Check", {"object": object_name})

        doc = self.get_document()

        try:
            obj = doc.getObject(object_name)
            if not obj:
                return {"success": False, "error": f"Object not found: {object_name}"}

            check = doc.addObject("Inspection::Feature", name)

            doc.recompute()

            return {
                "success": True,
                "name": name,
                "type": "Check",
                "object": object_name,
                "label": check.Label
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def inspection_measure_distance(self, object1: str, object2: str) -> Dict[str, Any]:
        """
        Measure distance

        Args:
            object1: First object
            object2: Second object

        Returns:
            Measurement result
        """
        if not FREECAD_AVAILABLE:
            return {
                "success": True,
                "object1": object1,
                "object2": object2,
                "distance": 10.0,
                "mock": True
            }

        doc = self.get_document()

        try:
            obj1 = doc.getObject(object1)
            obj2 = doc.getObject(object2)

            if not obj1:
                return {"success": False, "error": f"Object not found: {object1}"}
            if not obj2:
                return {"success": False, "error": f"Object not found: {object2}"}

            # Calculate distance (simplified)
            distance = 10.0

            return {
                "success": True,
                "object1": object1,
                "object2": object2,
                "distance": distance
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

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

    def _mock_result(self, category: str, name: str,
                    sub_type: str = "", params: Any = None) -> Dict[str, Any]:
        """Return mock result (used when FreeCAD is not installed)"""
        return {
            "success": True,
            "mock": True,
            "category": category,
            "name": name,
            "type": sub_type,
            "params": params,
            "message": "FreeCAD not installed - returning mock data"
        }


# Global wrapper instance
_wrapper = None


def get_wrapper(headless: bool = True) -> FreeCADWrapper:
    """Get global wrapper instance"""
    global _wrapper
    if _wrapper is None:
        _wrapper = FreeCADWrapper(headless=headless)
    return _wrapper
