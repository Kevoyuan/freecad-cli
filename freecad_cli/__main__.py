# -*- coding: utf-8 -*-
"""
FreeCAD CLI - Direct Execution Entry Point
===========================================

允许直接使用 `python -m freecad_cli` 运行
"""

import sys
from pathlib import Path

# 添加父目录到路径，使 freecad_cli 作为包可导入
_package_dir = Path(__file__).parent
_parent_dir = _package_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

from freecad_cli.core import main

if __name__ == '__main__':
    main()
