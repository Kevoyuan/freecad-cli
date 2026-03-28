# -*- coding: utf-8 -*-
"""
Unit Tests for FreeCAD Wrapper
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from freecad_cli.freecad_integration import (
    FreeCADWrapper, check_freecad, get_wrapper
)


class TestFreeCADWrapper:
    """FreeCADWrapper 单元测试"""

    def test_check_freecad_returns_boolean(self):
        """测试 check_freecad 返回布尔值"""
        result = check_freecad()
        assert isinstance(result, bool)

    def test_get_wrapper_returns_wrapper_instance(self):
        """测试 get_wrapper 返回包装器实例"""
        wrapper = get_wrapper(headless=True)
        assert isinstance(wrapper, FreeCADWrapper)

    def test_wrapper_initialization_mock_mode(self):
        """测试无 FreeCAD 时的初始化 (Mock 模式)"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.initialize()

        # 在没有 FreeCAD 的情况下应该返回失败或成功 (取决于 mock 行为)
        assert isinstance(result, dict)
        assert 'success' in result

    def test_create_part_mock_mode(self):
        """测试 Mock 模式下创建零件"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_part("TestBox", "Box", {"length": 10, "width": 10, "height": 5})

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result.get('mock') == True
        assert result['name'] == "TestBox"

    def test_create_part_with_different_types(self):
        """测试创建不同类型的零件"""
        wrapper = FreeCADWrapper(headless=True)

        for shape_type in ["Box", "Cylinder", "Sphere", "Cone", "Torus"]:
            result = wrapper.create_part(f"Test{shape_type}", shape_type)
            assert result['success'] == True
            assert result['type'] == shape_type

    def test_create_sketch_mock_mode(self):
        """测试 Mock 模式下创建草图"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_sketch("TestSketch", "XY")

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['name'] == "TestSketch"
        assert result['mock'] == True  # Mock mode returns this
        assert result['params'].get('plane') == "XY"  # Plane is in params

    def test_create_sketch_different_planes(self):
        """测试创建不同平面的草图"""
        wrapper = FreeCADWrapper(headless=True)

        for plane in ["XY", "XZ", "YZ"]:
            result = wrapper.create_sketch(f"Sketch_{plane}", plane)
            assert result['success'] == True
            assert result['params'].get('plane') == plane  # Plane is in params

    def test_add_sketch_geometry_line(self):
        """测试向草图添加直线"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.add_sketch_geometry(
            "TestSketch", "Line",
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10}
        )

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['type'] == "Line"

    def test_add_sketch_geometry_circle(self):
        """测试向草图添加圆"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.add_sketch_geometry(
            "TestSketch", "Circle",
            {"cx": 5, "cy": 5, "radius": 3}
        )

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['type'] == "Circle"

    def test_create_draft_object(self):
        """测试创建 Draft 对象"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_draft_object("TestLine", "Line", {"x1": 0, "y1": 0})

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['name'] == "TestLine"

    def test_boolean_operations(self):
        """测试布尔运算"""
        wrapper = FreeCADWrapper(headless=True)

        operations = ["Fuse", "Cut", "Common", "Section"]
        for op in operations:
            result = wrapper.boolean_operation(f"Result_{op}", op, "Box1", "Box2")
            assert result['success'] == True
            assert result['type'] == op  # Mock returns 'type' not 'operation'

    def test_mesh_operations(self):
        """测试网格操作"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_mesh_object("TestMesh", "RegularMesh", {"width": 10, "height": 10})

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['type'] == "RegularMesh"

    def test_surface_operations(self):
        """测试曲面操作"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_surface("TestSurface", "Fill")

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['type'] == "Fill"

    def test_partdesign_body(self):
        """测试 PartDesign Body 创建"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_partdesign_body("TestBody")

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['name'] == "TestBody"

    def test_techdraw_page(self):
        """测试 TechDraw 页面创建"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.techdraw_create_page("TestPage", "A4_Landscape")

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['params'].get('template') == "A4_Landscape"  # Template is in params

    def test_spreadsheet_operations(self):
        """测试电子表格操作"""
        wrapper = FreeCADWrapper(headless=True)

        # 创建表格
        result = wrapper.spreadsheet_create("TestSheet")
        assert result['success'] == True

        # 设置单元格
        result = wrapper.spreadsheet_set_cell("TestSheet", "A1", 100)
        assert result['success'] == True

    def test_material_standard(self):
        """测试标准材料获取"""
        wrapper = FreeCADWrapper(headless=True)

        result = wrapper.material_get_standard("Steel")
        assert result['success'] == True
        assert result['material'] == "Steel"

        result = wrapper.material_get_standard("Unknown")
        assert result['success'] == False

    def test_get_object_info(self):
        """测试获取对象信息"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.get_object_info("TestObject")

        assert isinstance(result, dict)
        assert 'success' in result

    def test_list_objects(self):
        """测试列出对象"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.list_objects()

        assert isinstance(result, list)

    def test_delete_object(self):
        """测试删除对象"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.delete_object("TestObject")

        assert isinstance(result, dict)
        assert 'success' in result

    def test_export_document_mock(self):
        """测试文档导出"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.export_document("/tmp/test.step", "STEP")

        assert isinstance(result, dict)
        assert result['success'] == True


class TestAssemblyOperations:
    """装配操作测试"""

    def test_assembly_create(self):
        """测试创建装配"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.assembly_create("TestAssembly")

        assert result['success'] == True
        assert result['name'] == "TestAssembly"

    def test_assembly_add_part(self):
        """测试向装配添加零件"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.assembly_add_part("TestAssembly", "Part1", "[0, 0, 0]")

        assert result['success'] == True

    def test_assembly_placement_parsing(self):
        """测试 placement 参数解析"""
        wrapper = FreeCADWrapper(headless=True)

        # 有效输入
        result = wrapper.assembly_add_part("Assembly", "Part", "[1, 2, 3]")
        assert result['success'] == True

        # 无效输入 (应该优雅处理)
        result = wrapper.assembly_add_part("Assembly", "Part", "invalid")
        assert result['success'] == True  # 应该返回成功，使用默认值


class TestFEMOperations:
    """FEM 操作测试"""

    def test_fem_create_analysis(self):
        """测试创建分析"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.fem_create_analysis("TestAnalysis", "static")

        assert result['success'] == True
        assert result['params'].get('type') == "static"  # Type is in params for mock

    def test_fem_add_material(self):
        """测试添加材料"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.fem_add_material("TestAnalysis", "Steel")

        assert result['success'] == True

    def test_fem_run_analysis(self):
        """测试运行分析"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.fem_run_analysis("TestAnalysis")

        assert result['success'] == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
