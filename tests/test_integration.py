# -*- coding: utf-8 -*-
"""
Integration Tests for FreeCAD Wrapper

These tests invoke real FreeCAD APIs and are skipped when FreeCAD
is not installed. Run with: pytest tests/test_integration.py -v

CI tip — run all tests including integration:
    pytest tests/ -m ""
  or explicitly include:
    pytest tests/ -m integration
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from freecad_cli.freecad_integration import (
    FreeCADWrapper,
    check_freecad,
    FREECAD_AVAILABLE,
)


# Skip all tests in this module if FreeCAD is not available
pytestmark = pytest.mark.skipif(
    not FREECAD_AVAILABLE,
    reason="FreeCAD not installed — install FreeCAD 0.19+ to run these tests"
)


class TestFreeCADIntegration:
    """Tests that invoke real FreeCAD APIs — requires FreeCAD installed."""

    def test_check_freecad_returns_true(self):
        """check_freecad() should return True when FreeCAD is installed."""
        assert check_freecad() is True

    def test_wrapper_initialization_real(self):
        """Wrapper should initialize successfully with real FreeCAD."""
        wrapper = FreeCADWrapper(headless=True)
        result = wrapper.initialize()
        assert result.get("success") is True
        assert result.get("available") is True

    def test_create_part_real_freecad(self):
        """Creating a real Part box should succeed."""
        wrapper = FreeCADWrapper(headless=True)
        wrapper.initialize()
        result = wrapper.create_part("TestBox", "Box", {"length": 10, "width": 5, "height": 3})
        assert result.get("success") is True
        assert result.get("mock") is not True

    def test_create_sketch_real(self):
        """Creating a real sketch should succeed."""
        wrapper = FreeCADWrapper(headless=True)
        wrapper.initialize()
        result = wrapper.create_sketch("TestSketch", "XY")
        assert result.get("success") is True
        assert result.get("mock") is not True

    def test_document_has_real_objects(self):
        """Document should contain objects created in this session."""
        wrapper = FreeCADWrapper(headless=True)
        wrapper.initialize()
        wrapper.create_part("Box1", "Box", {})
        objects = wrapper.list_objects()
        assert any(o["name"] == "Box1" for o in objects)

    def test_delete_real_object(self):
        """Deleting a real object should succeed."""
        wrapper = FreeCADWrapper(headless=True)
        wrapper.initialize()
        wrapper.create_part("ToDelete", "Box", {})
        result = wrapper.delete_object("ToDelete")
        assert result.get("success") is True

    def test_partdesign_body_real(self):
        """PartDesign Body creation should work with real FreeCAD."""
        wrapper = FreeCADWrapper(headless=True)
        wrapper.initialize()
        result = wrapper.create_partdesign_body("TestBody")
        assert result.get("success") is True

    def test_fem_analysis_real(self):
        """FEM analysis creation should work with real FreeCAD."""
        wrapper = FreeCADWrapper(headless=True)
        wrapper.initialize()
        result = wrapper.fem_create_analysis("TestAnalysis", "static")
        assert result.get("success") is True

    def test_export_document_real(self, tmp_path):
        """Exporting a document should produce a valid STEP file."""
        wrapper = FreeCADWrapper(headless=True)
        wrapper.initialize()
        wrapper.create_part("ExportBox", "Box", {})
        output_path = str(tmp_path / "test_export.step")
        result = wrapper.export_document(output_path, "STEP")
        assert result.get("success") is True
        assert os.path.exists(output_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
