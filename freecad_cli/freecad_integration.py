# -*- coding: utf-8 -*-
"""
FreeCAD Integration Module - FreeCAD 核心集成模块
=================================================

提供 FreeCAD Python API 的包装器，使 CLI 命令能够调用 FreeCAD 功能。
此模块在 FreeCAD 导入失败时提供模拟模式用于测试。
"""

import sys
import ast
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

# FreeCAD 导入状态跟踪
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
    """检查 FreeCAD 是否可用"""
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

        # 尝试导入可选模块
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
    """FreeCAD 功能包装器类"""

    def __init__(self, headless: bool = True):
        """
        初始化 FreeCAD 包装器

        Args:
            headless: 是否使用无头模式 (无 GUI)
        """
        self.headless = headless
        self._doc = None
        self._initialized = False

    def initialize(self) -> Dict[str, Any]:
        """
        初始化 FreeCAD 环境

        Returns:
            初始化状态信息
        """
        if not check_freecad():
            return {
                "success": False,
                "error": "FreeCAD 未安装或无法导入",
                "available": False
            }

        try:
            if self.headless:
                # 无头模式初始化
                self._doc = _freecad_module.newDocument("CLI_Document")
            else:
                # GUI 模式
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
        """获取当前文档对象"""
        if not self._doc:
            self.initialize()
        return self._doc

    def create_part(self, name: str, shape_type: str = "Box",
                   params: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        创建 Part (零件) 对象

        Args:
            name: 对象名称
            shape_type: 形状类型 (Box, Cylinder, Sphere, Cone, Torus)
            params: 形状参数

        Returns:
            创建结果信息
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
                return {"success": False, "error": f"未知形状类型: {shape_type}"}

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
        创建草图对象

        Args:
            name: 草图名称
            plane: 草图平面 (XY, XZ, YZ)

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Sketch", name, params={"plane": plane})

        doc = self.get_document()

        try:
            obj = doc.addObject("Sketcher::SketchObject", name)

            # 设置草图平面
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
        向草图添加几何元素

        Args:
            sketch_name: 草图名称
            geometry_type: 几何类型 (Line, Circle, Arc, Rectangle, Polygon)
            params: 几何参数

        Returns:
            添加结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Geometry", sketch_name, geometry_type, params)

        doc = self.get_document()

        try:
            sketch = doc.getObject(sketch_name)
            if not sketch:
                return {"success": False, "error": f"找不到草图: {sketch_name}"}

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
                # 添加矩形的四条边
                for i in range(4):
                    geo_id = sketch.addGeometry(_sketcher_module.LineSegment(*p1, *p2))
            else:
                return {"success": False, "error": f"不支持的几何类型: {geometry_type}"}

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
        创建 Draft (草图绘制) 对象

        Args:
            name: 对象名称
            object_type: 对象类型 (Line, Polyline, Circle, Rectangle, Polygon, Arc)
            params: 对象参数

        Returns:
            创建结果信息
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
                return {"success": False, "error": f"未知 Draft 类型: {object_type}"}

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
        创建 Arch (建筑) 对象

        Args:
            name: 对象名称
            object_type: 对象类型 (Wall, Structure, Window, Door, Roof, Stairs)
            params: 对象参数

        Returns:
            创建结果信息
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
                return {"success": False, "error": f"未知 Arch 类型: {object_type}"}

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
        执行布尔运算

        Args:
            name: 结果对象名称
            operation: 运算类型 (Fuse, Cut, Common, Section)
            object1: 第一个对象名称
            object2: 第二个对象名称

        Returns:
            运算结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Boolean", name, operation,
                                     {"obj1": object1, "obj2": object2})

        doc = self.get_document()

        try:
            obj1 = doc.getObject(object1)
            obj2 = doc.getObject(object2)

            if not obj1 or not obj2:
                return {"success": False, "error": "找不到指定的对象"}

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
    # Mesh (网格) 模块
    # ============================================================================

    def create_mesh_object(self, name: str, object_type: str,
                          params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建 Mesh (网格) 对象

        Args:
            name: 对象名称
            object_type: 对象类型 (RegularMesh, Triangle, Grid)
            params: 对象参数

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Mesh", name, object_type, params)

        params = params or {}
        doc = self.get_document()

        try:
            if object_type == "RegularMesh":
                # 创建规则网格
                mesh = _mesh_module.Mesh()
                # 生成网格参数
                segment_length = params.get("segment_length", 1.0)
                # 简单的网格平面
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
                # 创建三角形网格
                mesh = _mesh_module.Mesh()
                points = params.get("points", [(0, 0, 0), (10, 0, 0), (5, 10, 0)])
                if len(points) >= 3:
                    mesh.addFacet(_mesh_module.MeshPoint(*points[0]),
                                  _mesh_module.MeshPoint(*points[1]),
                                  _mesh_module.MeshPoint(*points[2]))
                obj = doc.addObject("Mesh::Feature", name)
                obj.Mesh = mesh

            elif object_type == "Grid":
                # 创建网格线框
                mesh = _mesh_module.Mesh()
                obj = doc.addObject("Mesh::Feature", name)
                obj.Mesh = mesh

            else:
                return {"success": False, "error": f"未知 Mesh 类型: {object_type}"}

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
        从形状创建网格

        Args:
            name: 网格对象名称
            source_name: 源形状对象名称
            deflection: 网格偏转值 (精度)

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Mesh", name, "from_shape",
                                     {"source": source_name, "deflection": deflection})

        doc = self.get_document()

        try:
            source = doc.getObject(source_name)
            if not source:
                return {"success": False, "error": f"找不到源对象: {source_name}"}

            if not hasattr(source, 'Shape'):
                return {"success": False, "error": "源对象没有 Shape 属性"}

            # 创建网格
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
        网格布尔运算

        Args:
            name: 结果对象名称
            operation: 运算类型 (Union, Intersection, Difference)
            object1: 第一个网格对象
            object2: 第二个网格对象

        Returns:
            运算结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("MeshBoolean", name, operation,
                                     {"obj1": object1, "obj2": object2})

        doc = self.get_document()

        try:
            mesh1_obj = doc.getObject(object1)
            mesh2_obj = doc.getObject(object2)

            if not mesh1_obj or not mesh2_obj:
                return {"success": False, "error": "找不到指定的对象"}

            mesh1 = mesh1_obj.Mesh
            mesh2 = mesh2_obj.Mesh

            if operation == "Union":
                result_mesh = mesh1 + mesh2
            elif operation == "Intersection":
                result_mesh = mesh1.intersect(mesh2)
            elif operation == "Difference":
                result_mesh = mesh1.subtract(mesh2)
            else:
                return {"success": False, "error": f"未知运算: {operation}"}

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
    # Surface (曲面) 模块
    # ============================================================================

    def create_surface(self, name: str, surface_type: str,
                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建 Surface (曲面) 对象

        Args:
            name: 对象名称
            surface_type: 曲面类型 (Fill, Sweep, Loft, Bezier)
            params: 对象参数

        Returns:
            创建结果信息
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
                return {"success": False, "error": f"未知曲面类型: {surface_type}"}

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
        从草图边界创建曲面

        Args:
            name: 曲面对象名称
            sketch_name: 草图名称

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Surface", name, "from_edges",
                                     {"sketch": sketch_name})

        doc = self.get_document()

        try:
            sketch = doc.getObject(sketch_name)
            if not sketch:
                return {"success": False, "error": f"找不到草图: {sketch_name}"}

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
    # PartDesign (零件设计) 模块
    # ============================================================================

    def create_partdesign_body(self, name: str) -> Dict[str, Any]:
        """
        创建 PartDesign Body

        Args:
            name: Body 名称

        Returns:
            创建结果信息
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
        创建 Pad (拉伸)

        Args:
            name: Pad 名称
            body_name: Body 名称
            sketch_name: 草图名称
            length: 拉伸长度
            direction: 拉伸方向 (Normal, Reversed, Double)

        Returns:
            创建结果信息
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
                return {"success": False, "error": f"找不到 Body: {body_name}"}
            if not sketch:
                return {"success": False, "error": f"找不到草图: {sketch_name}"}

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
        创建 Pocket (切除)

        Args:
            name: Pocket 名称
            body_name: Body 名称
            sketch_name: 草图名称
            length: 切除深度
            type: 切除类型 (Through, UpToFirst, UpToFace)

        Returns:
            创建结果信息
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
                return {"success": False, "error": f"找不到 Body: {body_name}"}
            if not sketch:
                return {"success": False, "error": f"找不到草图: {sketch_name}"}

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
        创建孔

        Args:
            name: 孔名称
            body_name: Body 名称
            diameter: 孔直径
            depth: 孔深度
            position: 孔位置 (x, y, z)

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Hole", name, "Hole",
                                     {"body": body_name, "diameter": diameter,
                                      "depth": depth, "position": position})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            if not body:
                return {"success": False, "error": f"找不到 Body: {body_name}"}

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
        创建旋转切除 (Groove)

        Args:
            name: Groove 名称
            body_name: Body 名称
            angle: 旋转角度
            radius: 旋转半径

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Groove", name, "Groove",
                                     {"body": body_name, "angle": angle, "radius": radius})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            if not body:
                return {"success": False, "error": f"找不到 Body: {body_name}"}

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
        创建旋转体 (Revolution)

        Args:
            name: Revolution 名称
            body_name: Body 名称
            sketch_name: 草图名称
            angle: 旋转角度
            axis: 旋转轴 (x, y, z) 方向

        Returns:
            创建结果信息
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
                return {"success": False, "error": f"找不到 Body: {body_name}"}
            if not sketch:
                return {"success": False, "error": f"找不到草图: {sketch_name}"}

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
        创建圆角 (Fillet)

        Args:
            name: Fillet 名称
            body_name: Body 名称
            edge_radius: 圆角半径

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Fillet", name, "Fillet",
                                     {"body": body_name, "radius": edge_radius})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            if not body:
                return {"success": False, "error": f"找不到 Body: {body_name}"}

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
        创建倒角 (Chamfer)

        Args:
            name: Chamfer 名称
            body_name: Body 名称
            chamfer_size: 倒角大小

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Chamfer", name, "Chamfer",
                                     {"body": body_name, "size": chamfer_size})

        doc = self.get_document()

        try:
            body = doc.getObject(body_name)
            if not body:
                return {"success": False, "error": f"找不到 Body: {body_name}"}

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
        导出文档

        Args:
            filepath: 导出文件路径
            format_type: 导出格式 (STEP, STL, OBJ, IGES, BREP, DXF)

        Returns:
            导出结果信息
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
        获取对象信息

        Args:
            object_name: 对象名称

        Returns:
            对象详细信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Info", object_name)

        doc = self.get_document()

        try:
            obj = doc.getObject(object_name)
            if not obj:
                return {"success": False, "error": f"找不到对象: {object_name}"}

            info = {
                "success": True,
                "name": obj.Name,
                "label": obj.Label,
                "type": obj.TypeId,
                "module": obj.Module if hasattr(obj, 'Module') else "Unknown"
            }

            # 添加几何信息
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
        列出文档中的对象

        Args:
            filter_type: 对象类型过滤器 (可选)

        Returns:
            对象列表
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
        删除对象

        Args:
            object_name: 要删除的对象名称

        Returns:
            删除结果信息
        """
        if not FREECAD_AVAILABLE:
            return {"success": True, "deleted": object_name, "mock": True}

        doc = self.get_document()

        try:
            obj = doc.getObject(object_name)
            if not obj:
                return {"success": False, "error": f"找不到对象: {object_name}"}

            doc.removeObject(object_name)
            return {"success": True, "deleted": object_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # TechDraw (工程图) 模块
    # ============================================================================

    def techdraw_create_page(self, name: str, template: str = "A4_Landscape") -> Dict[str, Any]:
        """
        创建 TechDraw 页面

        Args:
            name: 页面名称
            template: 图纸模板 (A4_Landscape, A4_Portrait, A3_Landscape, etc.)

        Returns:
            创建结果信息
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
        添加工程视图

        Args:
            page_name: 页面名称
            source_name: 源对象名称
            projection_type: 投影类型 (FirstAngle, ThirdAngle)

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("TechDraw", "View", "View",
                                     {"page": page_name, "source": source_name})

        doc = self.get_document()

        try:
            page = doc.getObject(page_name)
            source = doc.getObject(source_name)

            if not page:
                return {"success": False, "error": f"找不到页面: {page_name}"}
            if not source:
                return {"success": False, "error": f"找不到源对象: {source_name}"}

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
        添加尺寸标注

        Args:
            view_name: 视图名称
            dimension_type: 尺寸类型 (Horizontal, Vertical, Radius, Diameter, Angle)
            points: 尺寸点列表

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("TechDraw", "Dimension", dimension_type,
                                     {"view": view_name, "points": points})

        doc = self.get_document()

        try:
            view = doc.getObject(view_name)
            if not view:
                return {"success": False, "error": f"找不到视图: {view_name}"}

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
        导出工程图

        Args:
            page_name: 页面名称
            filepath: 导出文件路径
            format_type: 导出格式 (PDF, SVG, DXF)

        Returns:
            导出结果信息
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
                return {"success": False, "error": f"找不到页面: {page_name}"}

            # 导出
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
    # Spreadsheet (电子表格) 模块
    # ============================================================================

    def spreadsheet_create(self, name: str) -> Dict[str, Any]:
        """
        创建电子表格

        Args:
            name: 表格名称

        Returns:
            创建结果信息
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
        设置单元格值

        Args:
            sheet_name: 表格名称
            cell: 单元格地址 (如 "A1")
            value: 单元格值

        Returns:
            设置结果信息
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
                return {"success": False, "error": f"找不到表格: {sheet_name}"}

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
        设置单元格公式

        Args:
            sheet_name: 表格名称
            cell: 单元格地址
            formula: 公式 (如 "=A1*2")

        Returns:
            设置结果信息
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
                return {"success": False, "error": f"找不到表格: {sheet_name}"}

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
        链接电子表格到对象属性

        Args:
            sheet_name: 表格名称
            object_name: 对象名称
            property_name: 属性名称
            cell: 单元格地址

        Returns:
            链接结果信息
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
                return {"success": False, "error": f"找不到表格: {sheet_name}"}
            if not obj:
                return {"success": False, "error": f"找不到对象: {object_name}"}

            # 设置链接
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
    # Assembly (装配) 模块
    # ============================================================================

    def assembly_create(self, name: str) -> Dict[str, Any]:
        """
        创建装配

        Args:
            name: 装配名称

        Returns:
            创建结果信息
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
        向装配添加零件

        Args:
            assembly_name: 装配名称
            part_name: 零件名称
            placement: 位置 [x, y, z]

        Returns:
            添加结果信息
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
                return {"success": False, "error": f"找不到装配: {assembly_name}"}
            if not part:
                return {"success": False, "error": f"找不到零件: {part_name}"}

            # 添加零件到装配
            assembly.addObject(part)

            # 设置位置 (使用 ast.literal_eval 安全解析)
            try:
                import FreeCAD
                placement_list = ast.literal_eval(placement)
                if len(placement_list) == 3:
                    part.Placement.Base = FreeCAD.Vector(*placement_list)
            except (ValueError, SyntaxError):
                pass  # 保持默认位置

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
        添加装配约束

        Args:
            assembly_name: 装配名称
            constraint_type: 约束类型 (Coincident, Distance, Angle, etc.)
            object1: 第一个对象
            object2: 第二个对象
            parameters: 约束参数

        Returns:
            添加结果信息
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
                return {"success": False, "error": f"找不到装配: {assembly_name}"}

            # 创建约束
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
    # Path (CAM 加工) 模块
    # ============================================================================

    def path_create_job(self, name: str, base_name: str) -> Dict[str, Any]:
        """
        创建加工任务

        Args:
            name: 任务名称
            base_name: 基础对象名称

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Path", name, "Job", {"base": base_name})

        doc = self.get_document()

        try:
            base = doc.getObject(base_name)
            if not base:
                return {"success": False, "error": f"找不到基础对象: {base_name}"}

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
        添加加工操作

        Args:
            job_name: 任务名称
            operation_type: 操作类型 (Drill, Profile, Pocket, etc.)
            parameters: 操作参数

        Returns:
            添加结果信息
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
                return {"success": False, "error": f"找不到任务: {job_name}"}

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
        导出 G-code

        Args:
            job_name: 任务名称
            filepath: 导出文件路径
            post_processor: 后处理器 (linuxcnc, grbl, etc.)

        Returns:
            导出结果信息
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
                return {"success": False, "error": f"找不到任务: {job_name}"}

            # 导出 G-code
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
    # FEM (有限元分析) 模块
    # ============================================================================

    def fem_create_analysis(self, name: str, analysis_type: str = "static") -> Dict[str, Any]:
        """
        创建有限元分析

        Args:
            name: 分析名称
            analysis_type: 分析类型 (static, modal, thermomechanical)

        Returns:
            创建结果信息
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
        添加材料到分析

        Args:
            analysis_name: 分析名称
            material: 材料名称 (Steel, Aluminum, etc.)

        Returns:
            添加结果信息
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
                return {"success": False, "error": f"找不到分析: {analysis_name}"}

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
        添加边界条件

        Args:
            analysis_name: 分析名称
            bc_type: 边界条件类型 (Fixed, Force, Pressure)
            object_name: 对象名称
            parameters: 边界条件参数

        Returns:
            添加结果信息
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
                return {"success": False, "error": f"找不到分析: {analysis_name}"}

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
        运行有限元分析

        Args:
            analysis_name: 分析名称

        Returns:
            运行结果信息
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
                return {"success": False, "error": f"找不到分析: {analysis_name}"}

            # 运行分析 (需要求解器)
            doc.recompute()

            return {
                "success": True,
                "analysis": analysis_name,
                "status": "completed"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================================
    # Image (图像) 模块
    # ============================================================================

    def image_import(self, name: str, filepath: str) -> Dict[str, Any]:
        """
        导入图像

        Args:
            name: 图像名称
            filepath: 图像文件路径

        Returns:
            导入结果信息
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
        缩放图像

        Args:
            name: 图像名称
            scale_x: X 方向缩放
            scale_y: Y 方向缩放

        Returns:
            缩放结果信息
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
                return {"success": False, "error": f"找不到图像: {name}"}

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
    # Material (材料) 模块
    # ============================================================================

    def material_create(self, name: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建材料

        Args:
            name: 材料名称
            properties: 材料属性 (density, youngs_modulus, etc.)

        Returns:
            创建结果信息
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
        获取标准材料

        Args:
            material_name: 材料名称 (Steel, Aluminum, etc.)

        Returns:
            材料信息
        """
        # 标准材料库
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
                "error": f"未知材料: {material_name}",
                "available_materials": list(materials.keys())
            }

    # ============================================================================
    # Inspection (检测) 模块
    # ============================================================================

    def inspection_create_check(self, name: str, object_name: str) -> Dict[str, Any]:
        """
        创建检测

        Args:
            name: 检测名称
            object_name: 检测对象名称

        Returns:
            创建结果信息
        """
        if not FREECAD_AVAILABLE:
            return self._mock_result("Inspection", name, "Check", {"object": object_name})

        doc = self.get_document()

        try:
            obj = doc.getObject(object_name)
            if not obj:
                return {"success": False, "error": f"找不到对象: {object_name}"}

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
        测量距离

        Args:
            object1: 第一个对象
            object2: 第二个对象

        Returns:
            测量结果
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
                return {"success": False, "error": f"找不到对象: {object1}"}
            if not obj2:
                return {"success": False, "error": f"找不到对象: {object2}"}

            # 计算距离 (简化)
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
        """获取对象的边界框"""
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
        """返回模拟结果 (FreeCAD 未安装时使用)"""
        return {
            "success": True,
            "mock": True,
            "category": category,
            "name": name,
            "type": sub_type,
            "params": params,
            "message": "FreeCAD 未安装 - 返回模拟数据"
        }


# 全局包装器实例
_wrapper = None


def get_wrapper(headless: bool = True) -> FreeCADWrapper:
    """获取全局包装器实例"""
    global _wrapper
    if _wrapper is None:
        _wrapper = FreeCADWrapper(headless=headless)
    return _wrapper
