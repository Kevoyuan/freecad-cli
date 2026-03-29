# -*- coding: utf-8 -*-
"""Tests for enhanced mock mode"""

import pytest
from unittest.mock import MagicMock, patch


class TestMockGeometry:
    """Test MockGeometry calculations"""

    def test_box_bounding_box(self):
        """Test box bounding box calculation"""
        from freecad_cli._mock_geometry import MockGeometry

        params = {"length": 5.0, "width": 3.0, "height": 2.0}
        bb = MockGeometry.box_bounding_box(params)

        assert bb["x_min"] == 0.0
        assert bb["x_max"] == 5.0
        assert bb["y_min"] == 0.0
        assert bb["y_max"] == 3.0
        assert bb["z_min"] == 0.0
        assert bb["z_max"] == 2.0

    def test_box_volume(self):
        """Test box volume calculation"""
        from freecad_cli._mock_geometry import MockGeometry

        params = {"length": 5.0, "width": 3.0, "height": 2.0}
        volume = MockGeometry.box_volume(params)

        assert volume == 30.0

    def test_box_surface_area(self):
        """Test box surface area calculation"""
        from freecad_cli._mock_geometry import MockGeometry

        params = {"length": 5.0, "width": 3.0, "height": 2.0}
        sa = MockGeometry.box_surface_area(params)

        # 2*(lw + lh + wh) = 2*(15 + 10 + 6) = 2*31 = 62
        assert sa == 62.0

    def test_cylinder_bounding_box(self):
        """Test cylinder bounding box calculation"""
        from freecad_cli._mock_geometry import MockGeometry

        params = {"radius": 5.0, "height": 10.0}
        bb = MockGeometry.cylinder_bounding_box(params)

        assert bb["x_min"] == -5.0
        assert bb["x_max"] == 5.0
        assert bb["y_min"] == -5.0
        assert bb["y_max"] == 5.0
        assert bb["z_min"] == 0.0
        assert bb["z_max"] == 10.0

    def test_cylinder_volume(self):
        """Test cylinder volume calculation"""
        from freecad_cli._mock_geometry import MockGeometry

        import math
        params = {"radius": 5.0, "height": 10.0}
        volume = MockGeometry.cylinder_volume(params)

        assert abs(volume - (math.pi * 25 * 10)) < 0.001

    def test_sphere_bounding_box(self):
        """Test sphere bounding box calculation"""
        from freecad_cli._mock_geometry import MockGeometry

        params = {"radius": 5.0}
        bb = MockGeometry.sphere_bounding_box(params)

        assert bb["x_min"] == -5.0
        assert bb["x_max"] == 5.0
        assert bb["y_min"] == -5.0
        assert bb["y_max"] == 5.0
        assert bb["z_min"] == -5.0
        assert bb["z_max"] == 5.0


class TestMockValidators:
    """Test MockValidators"""

    def test_validate_box_params_valid(self):
        """Test valid box parameters"""
        from freecad_cli._validators import MockValidators

        params = {"length": 5.0, "width": 3.0, "height": 2.0}
        result = MockValidators.validate_part_params("Box", params)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_box_params_negative(self):
        """Test negative box parameter (strict mode)"""
        from freecad_cli._validators import MockValidators

        params = {"length": -5.0, "width": 3.0, "height": 2.0}
        result = MockValidators.validate_part_params("Box", params)

        assert result.valid is False
        assert any("length must be positive" in e for e in result.errors)

    def test_validate_box_params_zero(self):
        """Test zero box parameter (strict mode)"""
        from freecad_cli._validators import MockValidators

        params = {"length": 0.0, "width": 3.0, "height": 2.0}
        result = MockValidators.validate_part_params("Box", params)

        assert result.valid is False

    def test_validate_cylinder_params_valid(self):
        """Test valid cylinder parameters"""
        from freecad_cli._validators import MockValidators

        params = {"radius": 5.0, "height": 10.0}
        result = MockValidators.validate_part_params("Cylinder", params)

        assert result.valid is True

    def test_validate_cylinder_params_negative(self):
        """Test negative cylinder parameter"""
        from freecad_cli._validators import MockValidators

        params = {"radius": -5.0, "height": 10.0}
        result = MockValidators.validate_part_params("Cylinder", params)

        assert result.valid is False

    def test_validate_sphere_params_valid(self):
        """Test valid sphere parameters"""
        from freecad_cli._validators import MockValidators

        params = {"radius": 5.0}
        result = MockValidators.validate_part_params("Sphere", params)

        assert result.valid is True


class TestMockState:
    """Test MockState enhancements"""

    def test_add_generates_handle(self):
        """Test that add() generates a handle"""
        from freecad_cli._mock import _MockState

        state = _MockState()
        handle = state.add("Part", "Box1", "Box", {"length": 5})

        assert handle is not None
        assert handle.startswith("mock:part/")

    def test_exists(self):
        """Test exists() method"""
        from freecad_cli._mock import _MockState

        state = _MockState()
        handle = state.add("Part", "Box1", "Box", {})

        assert state.exists(handle) is True
        assert state.exists("mock:nonexistent") is False

    def test_get_object(self):
        """Test get_object() method"""
        from freecad_cli._mock import _MockState

        state = _MockState()
        handle = state.add("Part", "Box1", "Box", {"length": 5})

        obj = state.get_object(handle)
        assert obj is not None
        assert obj["name"] == "Box1"

    def test_dependency_tracking(self):
        """Test dependency tracking"""
        from freecad_cli._mock import _MockState

        state = _MockState()
        handle1 = state.add("Part", "Box1", "Box", {})
        handle2 = state.add("Part", "Box2", "Box", {}, depends_on=[handle1])

        obj2 = state.get_object(handle2)
        assert handle1 in obj2.get("depends_on", [])


class TestCreateMockResult:
    """Test create_mock_result function"""

    def test_create_mock_result_basic(self):
        """Test basic mock result creation"""
        from freecad_cli._mock import create_mock_result, _MockState
        from freecad_cli._validators import ValidationResult
        from freecad_cli._mock_geometry import MockGeometry

        state = _MockState()
        validation = ValidationResult(valid=True, errors=[], warnings=[])

        result = create_mock_result(
            "Part", "Box1", "Box",
            {"length": 5.0, "width": 3.0, "height": 2.0},
            validation, state
        )

        assert result["success"] is True
        assert result["mock"] is True
        assert "object_handle" in result
        assert "bounding_box" in result
        assert "geometry" in result

    def test_create_mock_result_with_geometry(self):
        """Test mock result includes geometry calculations"""
        from freecad_cli._mock import create_mock_result, _MockState
        from freecad_cli._validators import ValidationResult

        state = _MockState()
        validation = ValidationResult(valid=True, errors=[], warnings=[])

        result = create_mock_result(
            "Part", "Box1", "Box",
            {"length": 5.0, "width": 3.0, "height": 2.0},
            validation, state
        )

        # Check bounding box
        bb = result["bounding_box"]
        assert bb["x_max"] == 5.0
        assert bb["y_max"] == 3.0
        assert bb["z_max"] == 2.0

        # Check geometry
        geom = result["geometry"]
        assert "volume" in geom
        assert geom["volume"] == 30.0


class TestPartMockResult:
    """Test _part_mock_result function"""

    @patch('freecad_cli.freecad_integration.FREECAD_AVAILABLE', False)
    def test_part_mock_validates_params(self):
        """Test that mock validates parameters"""
        from freecad_cli._part import _part_mock_result

        # Create a mock wrapper
        mock_wrapper = MagicMock()
        mock_wrapper.get_document.return_value = None

        # Valid params should work
        result = _part_mock_result(mock_wrapper, "Part", "Box1", "Box", {"length": 5.0})
        assert result["success"] is True

        # Invalid params should fail
        result = _part_mock_result(mock_wrapper, "Part", "Box1", "Box", {"length": -5.0})
        assert result["success"] is False
        assert result.get("error_code") is not None
