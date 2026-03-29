# -*- coding: utf-8 -*-
"""
Validators Module
================

Provides parameter validation for mock mode (and optionally real mode).
Ensures parameters are valid before creating mock objects.
"""

from typing import Any, Dict, List, Tuple, Optional

from ._errors import CLIErrorCode, get_error_message


class ValidationResult:
    """Result of parameter validation"""

    def __init__(self, valid: bool = True, errors: Optional[List[str]] = None,
                 warnings: Optional[List[str]] = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


class MockValidators:
    """
    Validates parameters for CAD operations in mock mode.
    Returns (valid, errors, warnings) tuples.
    """

    # Threshold for "unusually large" dimensions (triggers warning but still valid)
    LARGE_DIMENSION_THRESHOLD = 10000.0

    # Threshold for "unusually small" dimensions (triggers warning)
    SMALL_DIMENSION_THRESHOLD = 0.001

    @classmethod
    def validate_part_params(cls, shape_type: str,
                              params: Dict[str, float]) -> ValidationResult:
        """
        Validate Part geometry parameters.

        Returns:
            ValidationResult with valid=True/False, errors list, warnings list
        """
        result = ValidationResult()
        params = params or {}

        if shape_type == "Box":
            return cls._validate_box(params)
        elif shape_type == "Cylinder":
            return cls._validate_cylinder(params)
        elif shape_type == "Sphere":
            return cls._validate_sphere(params)
        elif shape_type == "Cone":
            return cls._validate_cone(params)
        elif shape_type == "Torus":
            return cls._validate_torus(params)
        elif shape_type == "Ellipsoid":
            return cls._validate_ellipsoid(params)
        else:
            result.valid = False
            result.errors.append(f"Unknown shape type: {shape_type}")
            return result

    @classmethod
    def _validate_dimension(cls, dim_name: str, value: float,
                            allow_zero: bool = False) -> Tuple[bool, List[str], List[str]]:
        """Validate a single dimension parameter"""
        errors = []
        warnings = []

        if value is None:
            return True, errors, warnings  # Optional param

        if not isinstance(value, (int, float)):
            errors.append(f"{dim_name} must be a number")
            return False, errors, warnings

        if not allow_zero and value <= 0:
            errors.append(f"{dim_name} must be positive, got {value}")
            return False, errors, warnings

        if value > cls.LARGE_DIMENSION_THRESHOLD:
            warnings.append(f"{dim_name}={value} is unusually large (> {cls.LARGE_DIMENSION_THRESHOLD})")

        if 0 < value < cls.SMALL_DIMENSION_THRESHOLD:
            warnings.append(f"{dim_name}={value} is unusually small (< {cls.SMALL_DIMENSION_THRESHOLD})")

        return True, errors, warnings

    @classmethod
    def _validate_box(cls, params: Dict[str, float]) -> ValidationResult:
        """Validate Box parameters"""
        result = ValidationResult()

        for dim in ['length', 'width', 'height']:
            if dim in params:
                valid, errors, warnings = cls._validate_dimension(dim, params[dim])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        return result

    @classmethod
    def _validate_cylinder(cls, params: Dict[str, float]) -> ValidationResult:
        """Validate Cylinder parameters"""
        result = ValidationResult()

        if 'radius' in params:
            valid, errors, warnings = cls._validate_dimension('radius', params['radius'])
            if not valid:
                result.valid = False
                result.errors.extend(errors)
            result.warnings.extend(warnings)

        if 'height' in params:
            valid, errors, warnings = cls._validate_dimension('height', params['height'])
            if not valid:
                result.valid = False
                result.errors.extend(errors)
            result.warnings.extend(warnings)

        return result

    @classmethod
    def _validate_sphere(cls, params: Dict[str, float]) -> ValidationResult:
        """Validate Sphere parameters"""
        result = ValidationResult()

        if 'radius' in params:
            valid, errors, warnings = cls._validate_dimension('radius', params['radius'])
            if not valid:
                result.valid = False
                result.errors.extend(errors)
            result.warnings.extend(warnings)

        return result

    @classmethod
    def _validate_cone(cls, params: Dict[str, float]) -> ValidationResult:
        """Validate Cone parameters"""
        result = ValidationResult()

        for dim in ['radius1', 'radius2', 'height']:
            if dim in params:
                valid, errors, warnings = cls._validate_dimension(dim, params[dim])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        return result

    @classmethod
    def _validate_torus(cls, params: Dict[str, float]) -> ValidationResult:
        """Validate Torus parameters"""
        result = ValidationResult()

        for dim in ['radius1', 'radius2']:
            if dim in params:
                valid, errors, warnings = cls._validate_dimension(dim, params[dim])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        return result

    @classmethod
    def _validate_ellipsoid(cls, params: Dict[str, float]) -> ValidationResult:
        """Validate Ellipsoid parameters"""
        result = ValidationResult()

        for dim in ['radius1', 'radius2', 'radius3']:
            if dim in params:
                valid, errors, warnings = cls._validate_dimension(dim, params[dim])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        return result

    @classmethod
    def validate_sketch_params(cls, params: Dict[str, Any]) -> ValidationResult:
        """Validate Sketch parameters"""
        result = ValidationResult()

        if 'plane' in params:
            valid_planes = ['XY', 'XZ', 'YZ']
            if params['plane'] not in valid_planes:
                result.valid = False
                result.errors.append(f"Invalid plane: {params['plane']}. Must be one of {valid_planes}")

        return result

    @classmethod
    def validate_draft_params(cls, draft_type: str,
                               params: Dict[str, Any]) -> ValidationResult:
        """Validate Draft object parameters"""
        result = ValidationResult()

        if draft_type == "Line":
            for dim in ['x1', 'y1', 'z1', 'x2', 'y2', 'z2']:
                if dim in params:
                    if not isinstance(params[dim], (int, float)):
                        result.valid = False
                        result.errors.append(f"{dim} must be a number")

        elif draft_type == "Circle":
            if 'radius' in params:
                valid, errors, warnings = cls._validate_dimension('radius', params['radius'])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        elif draft_type == "Rectangle":
            for dim in ['length', 'height']:
                if dim in params:
                    valid, errors, warnings = cls._validate_dimension(dim, params[dim])
                    if not valid:
                        result.valid = False
                        result.errors.extend(errors)
                    result.warnings.extend(warnings)

        elif draft_type == "Polygon":
            if 'n_sides' in params:
                sides = params['n_sides']
                if not isinstance(sides, int) or sides < 3 or sides > 100:
                    result.valid = False
                    result.errors.append(f"n_sides must be an integer between 3 and 100, got {sides}")
            if 'radius' in params:
                valid, errors, warnings = cls._validate_dimension('radius', params['radius'])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        return result

    @classmethod
    def validate_partdesign_params(cls, feature_type: str,
                                    params: Dict[str, Any]) -> ValidationResult:
        """Validate PartDesign feature parameters"""
        result = ValidationResult()

        if feature_type in ["Pad", "Pocket"]:
            if 'length' in params:
                valid, errors, warnings = cls._validate_dimension('length', params['length'])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        elif feature_type == "Hole":
            if 'diameter' in params:
                valid, errors, warnings = cls._validate_dimension('diameter', params['diameter'])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)
            if 'depth' in params:
                valid, errors, warnings = cls._validate_dimension('depth', params['depth'])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        elif feature_type in ["Fillet", "Chamfer"]:
            if 'radius' in params:
                valid, errors, warnings = cls._validate_dimension('radius', params['radius'])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        elif feature_type == "Groove":
            if 'angle' in params:
                angle = params['angle']
                if not isinstance(angle, (int, float)) or angle <= 0 or angle > 360:
                    result.valid = False
                    result.errors.append(f"angle must be between 0 and 360, got {angle}")
            if 'radius' in params:
                valid, errors, warnings = cls._validate_dimension('radius', params['radius'])
                if not valid:
                    result.valid = False
                    result.errors.extend(errors)
                result.warnings.extend(warnings)

        return result
