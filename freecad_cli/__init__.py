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

# 核心 CLI
from .core import cli

# 格式化器
from .formatter import OutputFormatter, get_formatter

# FreeCAD 集成
from .freecad_integration import FreeCADWrapper, get_wrapper, check_freecad

# AI 集成
from .ai_integration import AICommandParser, BatchProcessor, CommandGenerator

__all__ = [
    # 核心
    "cli",

    # 格式化
    "OutputFormatter",
    "get_formatter",

    # FreeCAD 集成
    "FreeCADWrapper",
    "get_wrapper",
    "check_freecad",

    # AI 集成
    "AICommandParser",
    "BatchProcessor",
    "CommandGenerator",
]
