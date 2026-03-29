# -*- coding: utf-8 -*-
"""
Mock Geometry Module
===================

Provides realistic mock geometry calculations for when FreeCAD is not available.
Computes bounding boxes, volumes, and surface areas based on shape parameters.
"""

import math
from typing import Any, Dict, Optional


class MockGeometry:
    """
    Computes mock geometry data based on shape parameters.
    All calculations are simplified approximations for testing purposes.
    """

    # Threshold for "unusually large" dimensions (triggers warning but still valid)
    LARGE_DIMENSION_THRESHOLD = 10000.0

    @staticmethod
    def box_bounding_box(params: Dict[str, float]) -> Dict[str, float]:
        """Calculate bounding box for a Box"""
        l = params.get('length', 10.0)
        w = params.get('width', 10.0)
        h = params.get('height', 10.0)
        return {
            "x_min": 0.0,
            "x_max": l,
            "y_min": 0.0,
            "y_max": w,
            "z_min": 0.0,
            "z_max": h
        }

    @staticmethod
    def box_volume(params: Dict[str, float]) -> float:
        """Calculate volume for a Box"""
        return (
            params.get('length', 10.0) *
            params.get('width', 10.0) *
            params.get('height', 10.0)
        )

    @staticmethod
    def box_surface_area(params: Dict[str, float]) -> float:
        """Calculate surface area for a Box"""
        l = params.get('length', 10.0)
        w = params.get('width', 10.0)
        h = params.get('height', 10.0)
        return 2.0 * (l * w + w * h + h * l)

    @staticmethod
    def cylinder_bounding_box(params: Dict[str, float]) -> Dict[str, float]:
        """Calculate bounding box for a Cylinder"""
        r = params.get('radius', 5.0)
        h = params.get('height', 10.0)
        return {
            "x_min": -r,
            "x_max": r,
            "y_min": -r,
            "y_max": r,
            "z_min": 0.0,
            "z_max": h
        }

    @staticmethod
    def cylinder_volume(params: Dict[str, float]) -> float:
        """Calculate volume for a Cylinder"""
        r = params.get('radius', 5.0)
        h = params.get('height', 10.0)
        return math.pi * r * r * h

    @staticmethod
    def cylinder_surface_area(params: Dict[str, float]) -> float:
        """Calculate surface area for a Cylinder (including top/bottom)"""
        r = params.get('radius', 5.0)
        h = params.get('height', 10.0)
        # Lateral surface area + 2 * base area
        return 2 * math.pi * r * h + 2 * math.pi * r * r

    @staticmethod
    def sphere_bounding_box(params: Dict[str, float]) -> Dict[str, float]:
        """Calculate bounding box for a Sphere"""
        r = params.get('radius', 5.0)
        return {
            "x_min": -r,
            "x_max": r,
            "y_min": -r,
            "y_max": r,
            "z_min": -r,
            "z_max": r
        }

    @staticmethod
    def sphere_volume(params: Dict[str, float]) -> float:
        """Calculate volume for a Sphere"""
        r = params.get('radius', 5.0)
        return (4.0 / 3.0) * math.pi * r * r * r

    @staticmethod
    def sphere_surface_area(params: Dict[str, float]) -> float:
        """Calculate surface area for a Sphere"""
        r = params.get('radius', 5.0)
        return 4.0 * math.pi * r * r

    @staticmethod
    def cone_bounding_box(params: Dict[str, float]) -> Dict[str, float]:
        """Calculate bounding box for a Cone"""
        r1 = params.get('radius1', 5.0)
        r2 = params.get('radius2', 2.0)
        h = params.get('height', 10.0)
        r = max(r1, r2)  # Use larger radius
        return {
            "x_min": -r,
            "x_max": r,
            "y_min": -r,
            "y_max": r,
            "z_min": 0.0,
            "z_max": h
        }

    @staticmethod
    def cone_volume(params: Dict[str, float]) -> float:
        """Calculate volume for a Cone (frustum)"""
        r1 = params.get('radius1', 5.0)
        r2 = params.get('radius2', 2.0)
        h = params.get('height', 10.0)
        # Frustum volume: (1/3) * pi * h * (r1^2 + r2^2 + r1*r2)
        return (math.pi * h * (r1*r1 + r2*r2 + r1*r2)) / 3.0

    @staticmethod
    def cone_surface_area(params: Dict[str, float]) -> float:
        """Calculate surface area for a Cone (frustum)"""
        r1 = params.get('radius1', 5.0)
        r2 = params.get('radius2', 2.0)
        h = params.get('height', 10.0)
        # Slant height
        s = math.sqrt(h*h + (r1 - r2)*(r1 - r2))
        # Lateral area + top + bottom
        return math.pi * s * (r1 + r2) + math.pi * r1 * r1 + math.pi * r2 * r2

    @staticmethod
    def torus_bounding_box(params: Dict[str, float]) -> Dict[str, float]:
        """Calculate bounding box for a Torus"""
        r1 = params.get('radius1', 10.0)
        r2 = params.get('radius2', 2.0)
        return {
            "x_min": -(r1 + r2),
            "x_max": r1 + r2,
            "y_min": -(r1 + r2),
            "y_max": r1 + r2,
            "z_min": -r2,
            "z_max": r2
        }

    @staticmethod
    def torus_volume(params: Dict[str, float]) -> float:
        """Calculate volume for a Torus"""
        r1 = params.get('radius1', 10.0)
        r2 = params.get('radius2', 2.0)
        # Volume = (2 * pi * r1) * (pi * r2^2)
        return (2.0 * math.pi * r1) * (math.pi * r2 * r2)

    @staticmethod
    def torus_surface_area(params: Dict[str, float]) -> float:
        """Calculate surface area for a Torus"""
        r1 = params.get('radius1', 10.0)
        r2 = params.get('radius2', 2.0)
        # Surface area = (2 * pi * r1) * (2 * pi * r2)
        return (2.0 * math.pi * r1) * (2.0 * math.pi * r2)

    @staticmethod
    def ellipsoid_bounding_box(params: Dict[str, float]) -> Dict[str, float]:
        """Calculate bounding box for an Ellipsoid"""
        r1 = params.get('radius1', 5.0)
        r2 = params.get('radius2', 3.0)
        r3 = params.get('radius3', 4.0)
        return {
            "x_min": -r1,
            "x_max": r1,
            "y_min": -r2,
            "y_max": r2,
            "z_min": -r3,
            "z_max": r3
        }

    @staticmethod
    def ellipsoid_volume(params: Dict[str, float]) -> float:
        """Calculate volume for an Ellipsoid"""
        r1 = params.get('radius1', 5.0)
        r2 = params.get('radius2', 3.0)
        r3 = params.get('radius3', 4.0)
        # Volume = (4/3) * pi * r1 * r2 * r3
        return (4.0 / 3.0) * math.pi * r1 * r2 * r3

    @staticmethod
    def get_bounding_box(shape_type: str, params: Dict[str, float]) -> Dict[str, float]:
        """Get bounding box for any supported shape type"""
        calculators = {
            "Box": MockGeometry.box_bounding_box,
            "Cylinder": MockGeometry.cylinder_bounding_box,
            "Sphere": MockGeometry.sphere_bounding_box,
            "Cone": MockGeometry.cone_bounding_box,
            "Torus": MockGeometry.torus_bounding_box,
            "Ellipsoid": MockGeometry.ellipsoid_bounding_box,
        }
        calc = calculators.get(shape_type, MockGeometry.box_bounding_box)
        return calc(params)

    @staticmethod
    def get_volume(shape_type: str, params: Dict[str, float]) -> float:
        """Get volume for any supported shape type"""
        calculators = {
            "Box": MockGeometry.box_volume,
            "Cylinder": MockGeometry.cylinder_volume,
            "Sphere": MockGeometry.sphere_volume,
            "Cone": MockGeometry.cone_volume,
            "Torus": MockGeometry.torus_volume,
            "Ellipsoid": MockGeometry.ellipsoid_volume,
        }
        calc = calculators.get(shape_type, MockGeometry.box_volume)
        return calc(params)

    @staticmethod
    def get_surface_area(shape_type: str, params: Dict[str, float]) -> float:
        """Get surface area for any supported shape type"""
        calculators = {
            "Box": MockGeometry.box_surface_area,
            "Cylinder": MockGeometry.cylinder_surface_area,
            "Sphere": MockGeometry.sphere_surface_area,
            "Cone": MockGeometry.cone_surface_area,
            "Torus": MockGeometry.torus_surface_area,
        }
        calc = calculators.get(shape_type, MockGeometry.box_surface_area)
        return calc(params)

    @staticmethod
    def get_geometry(shape_type: str, params: Dict[str, float]) -> Dict[str, float]:
        """Get all geometry data for a shape"""
        return {
            "volume": MockGeometry.get_volume(shape_type, params),
            "surface_area": MockGeometry.get_surface_area(shape_type, params)
        }
