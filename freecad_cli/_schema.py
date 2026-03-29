# -*- coding: utf-8 -*-
"""Schema module - Generate command schemas for AI agents"""

from typing import Any, Dict, List, Optional


# Command schemas organized by group
COMMAND_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "document": {
        "description": "Document operations",
        "commands": {
            "create": {
                "description": "Create a new document",
                "parameters": {
                    "name": {"type": "string", "required": False, "default": "Unnamed"}
                }
            },
            "list": {
                "description": "List all objects",
                "parameters": {}
            },
            "info": {
                "description": "Display document information",
                "parameters": {}
            }
        }
    },
    "part": {
        "description": "Part (component) module - Create basic geometry",
        "commands": {
            "create": {
                "description": "Create a Part geometry",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "type": {
                        "type": "enum",
                        "values": ["Box", "Cylinder", "Sphere", "Cone", "Torus", "Ellipsoid"],
                        "required": True,
                        "default": "Box"
                    },
                    "params": {"type": "object", "required": False, "default": {}}
                }
            },
            "list": {
                "description": "List all Part objects",
                "parameters": {
                    "type_filter": {"type": "string", "required": False}
                }
            },
            "info": {
                "description": "Get Part object information",
                "parameters": {
                    "name": {"type": "string", "required": True}
                }
            }
        }
    },
    "sketch": {
        "description": "Sketcher module - 2D sketch drawing",
        "commands": {
            "create": {
                "description": "Create a new sketch",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "plane": {
                        "type": "enum",
                        "values": ["XY", "XZ", "YZ"],
                        "required": False,
                        "default": "XY"
                    }
                }
            },
            "add-line": {
                "description": "Add a line to a sketch",
                "parameters": {
                    "sketch": {"type": "string", "required": True},
                    "x1": {"type": "float", "required": False, "default": 0.0},
                    "y1": {"type": "float", "required": False, "default": 0.0},
                    "x2": {"type": "float", "required": False, "default": 10.0},
                    "y2": {"type": "float", "required": False, "default": 10.0}
                }
            },
            "add-circle": {
                "description": "Add a circle to a sketch",
                "parameters": {
                    "sketch": {"type": "string", "required": True},
                    "cx": {"type": "float", "required": False, "default": 0.0},
                    "cy": {"type": "float", "required": False, "default": 0.0},
                    "radius": {"type": "float", "required": False, "default": 5.0}
                }
            },
            "list": {
                "description": "List all sketches",
                "parameters": {}
            }
        }
    },
    "draft": {
        "description": "Draft module - 2D drawing and annotations",
        "commands": {
            "line": {
                "description": "Create a line",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "x1": {"type": "float", "required": False, "default": 0.0},
                    "y1": {"type": "float", "required": False, "default": 0.0},
                    "z1": {"type": "float", "required": False, "default": 0.0},
                    "x2": {"type": "float", "required": False, "default": 10.0},
                    "y2": {"type": "float", "required": False, "default": 10.0},
                    "z2": {"type": "float", "required": False, "default": 0.0}
                }
            },
            "circle": {
                "description": "Create a circle",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "radius": {"type": "float", "required": False, "default": 10.0},
                    "face": {"type": "boolean", "required": False, "default": False}
                }
            },
            "rectangle": {
                "description": "Create a rectangle",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "length": {"type": "float", "required": False, "default": 10.0},
                    "height": {"type": "float", "required": False, "default": 5.0},
                    "face": {"type": "boolean", "required": False, "default": False}
                }
            },
            "polygon": {
                "description": "Create a regular polygon",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "sides": {"type": "integer", "required": False, "default": 6},
                    "radius": {"type": "float", "required": False, "default": 10.0}
                }
            }
        }
    },
    "arch": {
        "description": "Arch module - BIM and architectural modeling",
        "commands": {
            "wall": {
                "description": "Create a wall",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "length": {"type": "float", "required": False, "default": 100.0},
                    "width": {"type": "float", "required": False, "default": 20.0},
                    "height": {"type": "float", "required": False, "default": 300.0}
                }
            },
            "structure": {
                "description": "Create a structure",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "length": {"type": "float", "required": False, "default": 100.0},
                    "width": {"type": "float", "required": False, "default": 100.0},
                    "height": {"type": "float", "required": False, "default": 200.0}
                }
            },
            "window": {
                "description": "Create a window",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "width": {"type": "float", "required": False, "default": 100.0},
                    "height": {"type": "float", "required": False, "default": 150.0}
                }
            }
        }
    },
    "boolean": {
        "description": "Boolean operation commands",
        "commands": {
            "fuse": {
                "description": "Union operation (Fuse)",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "object1": {"type": "string", "required": True},
                    "object2": {"type": "string", "required": True}
                }
            },
            "cut": {
                "description": "Subtraction operation (Cut)",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "object1": {"type": "string", "required": True},
                    "object2": {"type": "string", "required": True}
                }
            },
            "common": {
                "description": "Intersection operation (Common)",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "object1": {"type": "string", "required": True},
                    "object2": {"type": "string", "required": True}
                }
            },
            "section": {
                "description": "Section operation (Section)",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "object1": {"type": "string", "required": True},
                    "object2": {"type": "string", "required": True}
                }
            }
        }
    },
    "mesh": {
        "description": "Mesh module - Mesh processing and operations",
        "commands": {
            "create": {
                "description": "Create a Mesh object",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "type": {
                        "type": "enum",
                        "values": ["RegularMesh", "Triangle", "Grid"],
                        "required": False,
                        "default": "RegularMesh"
                    },
                    "params": {"type": "object", "required": False, "default": {}}
                }
            },
            "from-shape": {
                "description": "Create mesh from shape",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "source": {"type": "string", "required": True},
                    "deflection": {"type": "float", "required": False, "default": 0.1}
                }
            },
            "boolean": {
                "description": "Mesh boolean operation",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "operation": {
                        "type": "enum",
                        "values": ["Union", "Intersection", "Difference"],
                        "required": True
                    },
                    "object1": {"type": "string", "required": True},
                    "object2": {"type": "string", "required": True}
                }
            },
            "list": {
                "description": "List all Mesh objects",
                "parameters": {}
            }
        }
    },
    "surface": {
        "description": "Surface module - Surface modeling",
        "commands": {
            "create": {
                "description": "Create a Surface",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "type": {
                        "type": "enum",
                        "values": ["Fill", "Sweep", "Loft", "Bezier"],
                        "required": False,
                        "default": "Fill"
                    },
                    "params": {"type": "object", "required": False, "default": {}}
                }
            },
            "from-edges": {
                "description": "Create surface from sketch edges",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "sketch": {"type": "string", "required": True}
                }
            }
        }
    },
    "partdesign": {
        "description": "PartDesign module - Part design and features",
        "commands": {
            "create-body": {
                "description": "Create a PartDesign Body",
                "parameters": {
                    "name": {"type": "string", "required": True}
                }
            },
            "pad": {
                "description": "Create a Pad extrusion feature",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "body": {"type": "string", "required": True},
                    "sketch": {"type": "string", "required": True},
                    "length": {"type": "float", "required": False, "default": 10.0},
                    "direction": {
                        "type": "enum",
                        "values": ["Normal", "Reversed", "Double"],
                        "required": False,
                        "default": "Normal"
                    }
                }
            },
            "pocket": {
                "description": "Create a Pocket cut feature",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "body": {"type": "string", "required": True},
                    "sketch": {"type": "string", "required": True},
                    "length": {"type": "float", "required": False, "default": 10.0},
                    "type": {
                        "type": "enum",
                        "values": ["Through", "UpToFirst", "UpToFace"],
                        "required": False,
                        "default": "Through"
                    }
                }
            },
            "hole": {
                "description": "Create a hole feature",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "body": {"type": "string", "required": True},
                    "diameter": {"type": "float", "required": False, "default": 5.0},
                    "depth": {"type": "float", "required": False, "default": 10.0},
                    "position": {"type": "string", "required": False}
                }
            },
            "revolution": {
                "description": "Create a revolution feature",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "body": {"type": "string", "required": True},
                    "sketch": {"type": "string", "required": True},
                    "angle": {"type": "float", "required": False, "default": 360.0}
                }
            },
            "groove": {
                "description": "Create a groove cut feature",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "body": {"type": "string", "required": True},
                    "angle": {"type": "float", "required": False, "default": 360.0},
                    "radius": {"type": "float", "required": False, "default": 5.0}
                }
            },
            "fillet": {
                "description": "Create a fillet feature",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "body": {"type": "string", "required": True},
                    "radius": {"type": "float", "required": False, "default": 2.0}
                }
            },
            "chamfer": {
                "description": "Create a chamfer feature",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "body": {"type": "string", "required": True},
                    "size": {"type": "float", "required": False, "default": 1.0}
                }
            }
        }
    },
    "techdraw": {
        "description": "TechDraw module - Technical drawings and annotations",
        "commands": {
            "create-page": {
                "description": "Create a TechDraw page",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "template": {"type": "string", "required": False, "default": "A4_Landscape"}
                }
            },
            "add-view": {
                "description": "Add an engineering view",
                "parameters": {
                    "page": {"type": "string", "required": True},
                    "source": {"type": "string", "required": True},
                    "projection": {
                        "type": "enum",
                        "values": ["FirstAngle", "ThirdAngle"],
                        "required": False,
                        "default": "FirstAngle"
                    }
                }
            },
            "add-dimension": {
                "description": "Add a dimension annotation",
                "parameters": {
                    "view": {"type": "string", "required": True},
                    "type": {
                        "type": "enum",
                        "values": ["Horizontal", "Vertical", "Radius", "Diameter", "Angle"],
                        "required": False,
                        "default": "Horizontal"
                    }
                }
            },
            "export": {
                "description": "Export drawing",
                "parameters": {
                    "page": {"type": "string", "required": True},
                    "filepath": {"type": "string", "required": True},
                    "format": {
                        "type": "enum",
                        "values": ["PDF", "SVG", "DXF"],
                        "required": False,
                        "default": "PDF"
                    }
                }
            }
        }
    },
    "spreadsheet": {
        "description": "Spreadsheet module - Parametric spreadsheets",
        "commands": {
            "create": {
                "description": "Create a spreadsheet",
                "parameters": {
                    "name": {"type": "string", "required": True}
                }
            },
            "set-cell": {
                "description": "Set cell value",
                "parameters": {
                    "sheet": {"type": "string", "required": True},
                    "cell": {"type": "string", "required": True},
                    "value": {"type": "string", "required": True}
                }
            },
            "set-formula": {
                "description": "Set cell formula",
                "parameters": {
                    "sheet": {"type": "string", "required": True},
                    "cell": {"type": "string", "required": True},
                    "formula": {"type": "string", "required": True}
                }
            },
            "link": {
                "description": "Link spreadsheet to object property",
                "parameters": {
                    "sheet": {"type": "string", "required": True},
                    "object": {"type": "string", "required": True},
                    "property": {"type": "string", "required": True},
                    "cell": {"type": "string", "required": True}
                }
            }
        }
    },
    "assembly": {
        "description": "Assembly module - Assembly management",
        "commands": {
            "create": {
                "description": "Create an assembly",
                "parameters": {
                    "name": {"type": "string", "required": True}
                }
            },
            "add-part": {
                "description": "Add a part to an assembly",
                "parameters": {
                    "assembly": {"type": "string", "required": True},
                    "part": {"type": "string", "required": True},
                    "placement": {"type": "string", "required": False, "default": "[0, 0, 0]"}
                }
            },
            "add-constraint": {
                "description": "Add an assembly constraint",
                "parameters": {
                    "assembly": {"type": "string", "required": True},
                    "type": {
                        "type": "enum",
                        "values": ["Coincident", "Distance", "Angle"],
                        "required": True
                    },
                    "object1": {"type": "string", "required": True},
                    "object2": {"type": "string", "required": True}
                }
            }
        }
    },
    "path": {
        "description": "Path (CAM) module - CNC machining paths",
        "commands": {
            "create-job": {
                "description": "Create a machining job",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "base": {"type": "string", "required": True}
                }
            },
            "add-operation": {
                "description": "Add a machining operation",
                "parameters": {
                    "job": {"type": "string", "required": True},
                    "type": {
                        "type": "enum",
                        "values": ["Drill", "Profile", "Pocket", "Slot"],
                        "required": False,
                        "default": "Drill"
                    }
                }
            },
            "export-gcode": {
                "description": "Export G-code",
                "parameters": {
                    "job": {"type": "string", "required": True},
                    "filepath": {"type": "string", "required": True},
                    "post": {"type": "string", "required": False, "default": "linuxcnc"}
                }
            }
        }
    },
    "fem": {
        "description": "FEM (Finite Element Analysis) module - Engineering analysis",
        "commands": {
            "create-analysis": {
                "description": "Create a finite element analysis",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "type": {
                        "type": "enum",
                        "values": ["static", "modal", "thermomechanical"],
                        "required": False,
                        "default": "static"
                    }
                }
            },
            "add-material": {
                "description": "Add material",
                "parameters": {
                    "analysis": {"type": "string", "required": True},
                    "material": {
                        "type": "enum",
                        "values": ["Steel", "Aluminum", "Copper"],
                        "required": False,
                        "default": "Steel"
                    }
                }
            },
            "add-bc": {
                "description": "Add boundary condition",
                "parameters": {
                    "analysis": {"type": "string", "required": True},
                    "type": {
                        "type": "enum",
                        "values": ["Fixed", "Force", "Pressure"],
                        "required": True
                    },
                    "object": {"type": "string", "required": True}
                }
            },
            "run": {
                "description": "Run finite element analysis",
                "parameters": {
                    "analysis": {"type": "string", "required": True}
                }
            }
        }
    },
    "image": {
        "description": "Image module - Image processing",
        "commands": {
            "import": {
                "description": "Import an image",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "filepath": {"type": "string", "required": True}
                }
            },
            "scale": {
                "description": "Scale an image",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "x": {"type": "float", "required": False, "default": 1.0},
                    "y": {"type": "float", "required": False, "default": 1.0}
                }
            }
        }
    },
    "material": {
        "description": "Material module - Material management",
        "commands": {
            "create": {
                "description": "Create a material",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "density": {"type": "float", "required": False},
                    "youngs": {"type": "float", "required": False},
                    "poisson": {"type": "float", "required": False}
                }
            },
            "get-standard": {
                "description": "Get standard material",
                "parameters": {
                    "name": {"type": "string", "required": True}
                }
            }
        }
    },
    "inspection": {
        "description": "Inspection module - Inspection and measurement",
        "commands": {
            "create-check": {
                "description": "Create an inspection",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "object": {"type": "string", "required": True}
                }
            },
            "measure-distance": {
                "description": "Measure distance",
                "parameters": {
                    "object1": {"type": "string", "required": True},
                    "object2": {"type": "string", "required": True}
                }
            }
        }
    },
    "export": {
        "description": "Export commands",
        "commands": {
            "step": {
                "description": "Export to STEP format",
                "parameters": {
                    "filepath": {"type": "string", "required": True}
                }
            },
            "stl": {
                "description": "Export to STL format",
                "parameters": {
                    "filepath": {"type": "string", "required": True}
                }
            },
            "obj": {
                "description": "Export to OBJ format",
                "parameters": {
                    "filepath": {"type": "string", "required": True}
                }
            },
            "iges": {
                "description": "Export to IGES format",
                "parameters": {
                    "filepath": {"type": "string", "required": True}
                }
            }
        }
    },
    "info": {
        "description": "Information query commands",
        "commands": {
            "object": {
                "description": "Get detailed object information",
                "parameters": {
                    "name": {"type": "string", "required": True}
                }
            },
            "status": {
                "description": "Display FreeCAD status",
                "parameters": {}
            },
            "modules": {
                "description": "List available modules",
                "parameters": {}
            }
        }
    },
    "object": {
        "description": "Object operation commands",
        "commands": {
            "delete": {
                "description": "Delete an object",
                "parameters": {
                    "name": {"type": "string", "required": True}
                }
            },
            "list": {
                "description": "List all objects",
                "parameters": {
                    "type": {"type": "string", "required": False}
                }
            }
        }
    }
}


def get_schema(version: str = "1.0") -> Dict[str, Any]:
    """Get complete command schema"""
    return {
        "version": version,
        "command_groups": COMMAND_SCHEMAS
    }


def get_command_schema(group: str, command: str) -> Optional[Dict[str, Any]]:
    """Get schema for a specific command"""
    group_schema = COMMAND_SCHEMAS.get(group)
    if not group_schema:
        return None
    return group_schema.get("commands", {}).get(command)


def list_commands() -> List[str]:
    """List all available command paths (group.command)"""
    commands = []
    for group, group_data in COMMAND_SCHEMAS.items():
        for cmd in group_data.get("commands", {}).keys():
            commands.append(f"{group}.{cmd}")
    return sorted(commands)
