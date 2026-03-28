# -*- coding: utf-8 -*-
"""
FreeCAD CLI - Direct Execution Entry Point
===========================================

Allows running directly with `python -m freecad_cli`
"""

import sys
from pathlib import Path

# Add parent directory to path to make freecad_cli importable as a package
_package_dir = Path(__file__).parent
_parent_dir = _package_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

from freecad_cli.core import main

if __name__ == '__main__':
    main()
