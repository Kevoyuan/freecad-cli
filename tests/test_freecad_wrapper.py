# -*- coding: utf-8 -*-
"""
Unit Tests for FreeCAD Wrapper

These tests run in mock mode (FreeCAD not required).
To also run integration tests (requires FreeCAD installed):
    pytest tests/ -m integration

FreeCAD integration tests are automatically skipped when FreeCAD is not available.
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
    """FreeCADWrapper unit tests"""

    def test_check_freecad_returns_boolean(self):
        """Test check_freecad returns boolean"""
        result = check_freecad()
        assert isinstance(result, bool)

    def test_get_wrapper_returns_wrapper_instance(self):
        """Test get_wrapper returns wrapper instance"""
        wrapper = get_wrapper(headless=True)
        assert isinstance(wrapper, FreeCADWrapper)

    def test_wrapper_initialization_mock_mode(self):
        """Test initialization without FreeCAD (Mock mode)"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.initialize()

        # Without FreeCAD, should return failure or success (depends on mock behavior)
        assert isinstance(result, dict)
        assert 'success' in result

    def test_create_part_mock_mode(self):
        """Test creating part in Mock mode"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_part("TestBox", "Box", {"length": 10, "width": 10, "height": 5})

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result.get('mock') == True
        assert result['name'] == "TestBox"

    def test_create_part_with_different_types(self):
        """Test creating different types of parts"""
        wrapper = FreeCADWrapper(headless=True)

        for shape_type in ["Box", "Cylinder", "Sphere", "Cone", "Torus"]:
            result = wrapper.create_part(f"Test{shape_type}", shape_type)
            assert result['success'] == True
            assert result['type'] == shape_type

    def test_create_sketch_mock_mode(self):
        """Test creating sketch in Mock mode"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_sketch("TestSketch", "XY")

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['name'] == "TestSketch"
        assert result['mock'] == True  # Mock mode returns this
        assert result['params'].get('plane') == "XY"  # Plane is in params

    def test_create_sketch_different_planes(self):
        """Test creating sketches on different planes"""
        wrapper = FreeCADWrapper(headless=True)

        for plane in ["XY", "XZ", "YZ"]:
            result = wrapper.create_sketch(f"Sketch_{plane}", plane)
            assert result['success'] == True
            assert result['params'].get('plane') == plane  # Plane is in params

    def test_add_sketch_geometry_line(self):
        """Test adding line to sketch"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.add_sketch_geometry(
            "TestSketch", "Line",
            {"x1": 0, "y1": 0, "x2": 10, "y2": 10}
        )

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['type'] == "Line"

    def test_add_sketch_geometry_circle(self):
        """Test adding circle to sketch"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.add_sketch_geometry(
            "TestSketch", "Circle",
            {"cx": 5, "cy": 5, "radius": 3}
        )

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['type'] == "Circle"

    def test_create_draft_object(self):
        """Test creating Draft object"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_draft_object("TestLine", "Line", {"x1": 0, "y1": 0})

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['name'] == "TestLine"

    def test_boolean_operations(self):
        """Test boolean operations"""
        wrapper = FreeCADWrapper(headless=True)

        operations = ["Fuse", "Cut", "Common", "Section"]
        for op in operations:
            result = wrapper.boolean_operation(f"Result_{op}", op, "Box1", "Box2")
            assert result['success'] == True
            assert result['type'] == op  # Mock returns 'type' not 'operation'

    def test_mesh_operations(self):
        """Test mesh operations"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_mesh_object("TestMesh", "RegularMesh", {"width": 10, "height": 10})

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['type'] == "RegularMesh"

    def test_surface_operations(self):
        """Test surface operations"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_surface("TestSurface", "Fill")

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['type'] == "Fill"

    def test_partdesign_body(self):
        """Test PartDesign Body creation"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.create_partdesign_body("TestBody")

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['name'] == "TestBody"

    def test_techdraw_page(self):
        """Test TechDraw page creation"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.techdraw_create_page("TestPage", "A4_Landscape")

        assert isinstance(result, dict)
        assert result['success'] == True
        assert result['params'].get('template') == "A4_Landscape"  # Template is in params

    def test_spreadsheet_operations(self):
        """Test spreadsheet operations"""
        wrapper = FreeCADWrapper(headless=True)

        # Create spreadsheet
        result = wrapper.spreadsheet_create("TestSheet")
        assert result['success'] == True

        # Set cell value
        result = wrapper.spreadsheet_set_cell("TestSheet", "A1", 100)
        assert result['success'] == True

    def test_material_standard(self):
        """Test getting standard materials"""
        wrapper = FreeCADWrapper(headless=True)

        result = wrapper.material_get_standard("Steel")
        assert result['success'] == True
        assert result['material'] == "Steel"

        result = wrapper.material_get_standard("Unknown")
        assert result['success'] == False

    def test_get_object_info(self):
        """Test getting object info"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.get_object_info("TestObject")

        assert isinstance(result, dict)
        assert 'success' in result

    def test_list_objects(self):
        """Test listing objects"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.list_objects()

        assert isinstance(result, list)

    def test_delete_object(self):
        """Test deleting object"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.delete_object("TestObject")

        assert isinstance(result, dict)
        assert 'success' in result

    def test_export_document_mock(self):
        """Test document export"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.export_document("/tmp/test.step", "STEP")

        assert isinstance(result, dict)
        assert result['success'] == True


class TestAssemblyOperations:
    """Assembly operations tests"""

    def test_assembly_create(self):
        """Test creating assembly"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.assembly_create("TestAssembly")

        assert result['success'] == True
        assert result['name'] == "TestAssembly"

    def test_assembly_add_part(self):
        """Test adding part to assembly"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.assembly_add_part("TestAssembly", "Part1", "[0, 0, 0]")

        assert result['success'] == True

    def test_assembly_placement_parsing(self):
        """Test placement parameter parsing"""
        wrapper = FreeCADWrapper(headless=True)

        # Valid input
        result = wrapper.assembly_add_part("Assembly", "Part", "[1, 2, 3]")
        assert result['success'] == True

        # Invalid input (should handle gracefully)
        result = wrapper.assembly_add_part("Assembly", "Part", "invalid")
        assert result['success'] == True  # Should return success with default value


class TestFEMOperations:
    """FEM operations tests"""

    def test_fem_create_analysis(self):
        """Test creating analysis"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.fem_create_analysis("TestAnalysis", "static")

        assert result['success'] == True
        assert result['params'].get('type') == "static"  # Type is in params for mock

    def test_fem_add_material(self):
        """Test adding material"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.fem_add_material("TestAnalysis", "Steel")

        assert result['success'] == True

    def test_fem_run_analysis(self):
        """Test running analysis"""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.fem_run_analysis("TestAnalysis")

        assert result['success'] == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
