# -*- coding: utf-8 -*-
"""
Pytest configuration — shared fixtures and markers.
"""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: tests that require FreeCAD to be installed and running"
    )
