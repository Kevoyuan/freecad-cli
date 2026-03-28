# -*- coding: utf-8 -*-
"""
FreeCAD CLI - Command Line Interface for FreeCAD
=================================================

A comprehensive CLI tool that exposes all FreeCAD Python API functions
as command line arguments, making it easy for AI systems to interact
with FreeCAD's CAD capabilities.

Author: MiniMax Agent
License: LGPL 2.1+
"""

__version__ = "1.0.0"
__author__ = "MiniMax Agent"

# Core CLI
from .core import cli

# Formatter
from .formatter import OutputFormatter, get_formatter

# FreeCAD integration
from .freecad_integration import FreeCADWrapper, get_wrapper, check_freecad

# AI integration
from .ai_integration import AICommandParser, BatchProcessor, CommandGenerator

__all__ = [
    # Core
    "cli",

    # Formatter
    "OutputFormatter",
    "get_formatter",

    # FreeCAD integration
    "FreeCADWrapper",
    "get_wrapper",
    "check_freecad",

    # AI integration
    "AICommandParser",
    "BatchProcessor",
    "CommandGenerator",
]
