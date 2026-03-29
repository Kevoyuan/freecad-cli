# FreeCAD CLI

FreeCAD command-line interface — gives AI systems full access to FreeCAD CAD functionality.

[English](README_EN.md) | [中文](README.md)

## Features

- **Complete API Coverage**: Supports all FreeCAD core modules (Part, Sketcher, Draft, Arch, Mesh, etc.)
- **AI-Friendly Output**: Native JSON/YAML output, easy for AI systems to parse
- **Natural Language Parsing**: Converts natural language commands into structured CLI calls (Chinese and English)
- **Batch Operations**: Supports batch command execution with transaction handling
- **Multi-Format Export**: STEP, STL, OBJ, IGES and other major formats

## Installation

### Prerequisites

- Python 3.8+
- FreeCAD 0.19+ (FreeCAD Python module must be installed)
- Node.js 16+ (for npm installation)

### npm (recommended)

```bash
npm install freecad-cli
npx freecad-cli --help
```

### pip

```bash
pip install freecad-cli
freecad-cli --help
```

### From source

```bash
git clone https://github.com/Kevoyuan/freecad-cli.git
cd freecad-cli
pip install -e .
```

## Quick Start

### Basic Commands

```bash
# View help
freecad-cli --help

# Check FreeCAD status
freecad-cli info status

# View available modules
freecad-cli info modules
```

### Part Module (Solid Modeling)

```bash
# Create a box
freecad-cli part create --name MyBox --type Box --params '{"length": 10, "width": 10, "height": 5}'

# Create a cylinder
freecad-cli part create --name MyCylinder --type Cylinder --params '{"radius": 5, "height": 20}'

# Create a sphere
freecad-cli part create --name MySphere --type Sphere --params '{"radius": 8}'

# List all Part objects
freecad-cli part list

# View object info
freecad-cli part info --name MyBox
```

### Sketch Module

```bash
# Create a sketch
freecad-cli sketch create --name MySketch --plane XY

# Add a line
freecad-cli sketch add-line --sketch MySketch --x1 0 --y1 0 --x2 10 --y2 10

# Add a circle
freecad-cli sketch add-circle --sketch MySketch --cx 5 --cy 5 --radius 3

# List all sketches
freecad-cli sketch list
```

### Draft Module (2D Drawing)

```bash
# Create a line
freecad-cli draft line --name MyLine --x1 0 --y1 0 --z1 0 --x2 100 --y2 100 --z2 0

# Create a circle
freecad-cli draft circle --name MyCircle --radius 50

# Create a rectangle
freecad-cli draft rectangle --name MyRect --length 80 --height 40

# Create a polygon
freecad-cli draft polygon --name MyHex --sides 6 --radius 30
```

### Arch Module (BIM)

```bash
# Create a wall
freecad-cli arch wall --name MainWall --length 500 --width 20 --height 300

# Create a structure
freecad-cli arch structure --name Column --length 50 --width 50 --height 400

# Create a window
freecad-cli arch window --name Window1 --width 120 --height 150
```

### Mesh Module

```bash
# Create a regular mesh
freecad-cli mesh create --name MyMesh --type RegularMesh --params '{"width": 10, "height": 10}'

# Create a triangle mesh
freecad-cli mesh create --name TriMesh --type Triangle --params '{"points": [[0,0,0], [10,0,0], [5,10,0]]}'

# Create mesh from shape
freecad-cli mesh from-shape --name MeshFromShape --source MyBox --deflection 0.1

# Mesh boolean (union)
freecad-cli mesh boolean --name MeshUnion --operation Union --object1 Mesh1 --object2 Mesh2

# List all mesh objects
freecad-cli mesh list
```

### Surface Module

```bash
# Create a fill surface
freecad-cli surface create --name MySurface --type Fill

# Create a sweep surface
freecad-cli surface create --name SweepSurface --type Sweep --params '{"sections": ["sketch1", "sketch2"]}'

# Create a loft surface
freecad-cli surface create --name LoftSurface --type Loft --params '{"sections": ["sketch1", "sketch2"]}'

# Create a Bezier surface
freecad-cli surface create --name BezierSurface --type Bezier

# Create surface from edges
freecad-cli surface from-edges --name SurfaceFromEdges --sketch MySketch
```

### PartDesign Module

```bash
# Create a Body
freecad-cli partdesign create-body --name MyBody

# Create a Pad (extrusion)
freecad-cli partdesign pad --name MyPad --body MyBody --sketch MySketch --length 20

# Create a Pocket (cutout)
freecad-cli partdesign pocket --name MyPocket --body MyBody --sketch MySketch --length 10

# Create a hole
freecad-cli partdesign hole --name MyHole --body MyBody --diameter 5 --depth 15

# Create a revolution
freecad-cli partdesign revolution --name MyRevolution --body MyBody --sketch MySketch --angle 360

# Create a groove (rotational cutout)
freecad-cli partdesign groove --name MyGroove --body MyBody --angle 360 --radius 10

# Create a fillet
freecad-cli partdesign fillet --name MyFillet --body MyBody --radius 2

# Create a chamfer
freecad-cli partdesign chamfer --name MyChamfer --body MyBody --size 1
```

### TechDraw Module (Engineering Drawings)

```bash
# Create a drawing page
freecad-cli techdraw create-page --name DrawPage --template A4_Landscape

# Add a view
freecad-cli techdraw add-view --page DrawPage --source MyPart --projection FirstAngle

# Add a dimension
freecad-cli techdraw add-dimension --view View --type Horizontal

# Export drawing
freecad-cli techdraw export --page DrawPage --filepath output/drawing.pdf --format PDF
```

### Spreadsheet Module

```bash
# Create a spreadsheet
freecad-cli spreadsheet create --name Params

# Set cell value
freecad-cli spreadsheet set-cell --sheet Params --cell A1 --value 10

# Set formula
freecad-cli spreadsheet set-formula --sheet Params --cell B1 --formula "=A1*2"

# Link to object property
freecad-cli spreadsheet link --sheet Params --object MyBox --property Length --cell A1
```

### Assembly Module

```bash
# Create an assembly
freecad-cli assembly create --name MyAssembly

# Add a part
freecad-cli assembly add-part --assembly MyAssembly --part Part1 --placement [0,0,0]

# Add a constraint
freecad-cli assembly add-constraint --assembly MyAssembly --type Coincident --object1 Part1 --object2 Part2
```

### Path Module (CAM)

```bash
# Create a machining job
freecad-cli path create-job --name Job1 --base MyPart

# Add an operation
freecad-cli path add-operation --job Job1 --type Drill

# Export G-code
freecad-cli path export-gcode --job Job1 --filepath output/gcode.nc --post linuxcnc
```

### FEM Module (Finite Element Analysis)

```bash
# Create an analysis
freecad-cli fem create-analysis --name Analysis --type static

# Add material
freecad-cli fem add-material --analysis Analysis --material Steel

# Add boundary condition
freecad-cli fem add-bc --analysis Analysis --type Fixed --object MyPart

# Run analysis
freecad-cli fem run --analysis Analysis
```

### Image Module

```bash
# Import an image
freecad-cli image import --name MyImage --filepath photo.png

# Scale image
freecad-cli image scale --name MyImage --x 2.0 --y 2.0
```

### Material Module

```bash
# Create a material
freecad-cli material create --name CustomSteel --density 7850 --youngs 210000 --poisson 0.3

# Get standard material
freecad-cli material get-standard --name Steel
```

### Inspection Module

```bash
# Create an inspection
freecad-cli inspection create-check --name Check1 --object MyPart

# Measure distance
freecad-cli inspection measure-distance --object1 Part1 --object2 Part2
```

### Boolean Operations

```bash
# Union (merge)
freecad-cli boolean fuse --name Union --object1 Box1 --object2 Box2

# Cut (difference)
freecad-cli boolean cut --name Cut --object1 Box1 --object2 Cylinder1

# Common (intersection)
freecad-cli boolean common --name Common --object1 Box1 --object2 Sphere1

# Section
freecad-cli boolean section --name Section --object1 Box1 --object2 Plane1
```

### Export

```bash
# Export as STEP
freecad-cli export step --filepath output/model.step

# Export as STL
freecad-cli export stl --filepath output/model.stl

# Export as OBJ
freecad-cli export obj --filepath output/model.obj

# Export as IGES
freecad-cli export iges --filepath output/model.iges
```

## Output Formats

### JSON (default)

```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00",
  "message": "Part 'MyBox' created successfully",
  "data": {
    "name": "MyBox",
    "type": "Box",
    "label": "MyBox",
    "bounding_box": {
      "x_min": 0,
      "x_max": 10,
      "y_min": 0,
      "y_max": 10,
      "z_min": 0,
      "z_max": 5
    }
  }
}
```

### Other Formats

```bash
# YAML format
freecad-cli --format yaml part create --name MyBox --type Box

# Table format
freecad-cli --format table object list

# Plain text
freecad-cli --format text info status
```

## AI Integration

### Python API

```python
from freecad_cli import FreeCADWrapper, AICommandParser

# Initialize
wrapper = FreeCADWrapper(headless=True)
wrapper.initialize()

# Create objects
result = wrapper.create_part("MyBox", "Box", {"length": 10, "width": 10, "height": 5})
print(result)

# Natural language parsing
parser = AICommandParser()
result = parser.parse("Create a cube named TestBox")
print(result)  # {'command_group': 'part', 'command': 'create', 'parameters': {...}}
```

### Batch Operations

```python
from freecad_cli import FreeCADWrapper, BatchProcessor

wrapper = FreeCADWrapper()
processor = BatchProcessor(wrapper)
wrapper.initialize()

commands = [
    {"command_group": "part", "command": "create", "parameters": {"name": "Box1", "type": "Box"}},
    {"command_group": "part", "command": "create", "parameters": {"name": "Box2", "type": "Box"}},
    {"command_group": "boolean", "command": "fuse", "parameters": {"name": "Union", "object1": "Box1", "object2": "Box2"}},
]

results = processor.execute_batch(commands)
summary = processor.get_summary()
print(f"Success: {summary['success']}/{summary['total']}")
```

## Architecture

```
freecad_cli/
├── __init__.py                # Package init
├── core.py                    # Main CLI entry and command definitions
├── formatter.py               # Output formatter (JSON/YAML/text/table)
├── freecad_integration.py      # FreeCAD API wrapper (core)
├── ai_integration.py           # AI integration (NL parsing)
├── decorators.py               # Decorators and NonEmptyString validator
├── _mock.py                  # Mock state tracking (for testing)
├── _part.py                  # Part module (Box, Cylinder, Sphere, ...)
├── _sketch.py                # Sketch module (sketches, geometry)
├── _draft.py                 # Draft module (2D drawing)
├── _arch.py                  # Arch module (BIM)
├── _boolean.py               # Boolean module (Fuse, Cut, Common, ...)
├── _mesh.py                  # Mesh module
├── _surface.py               # Surface module
├── _partdesign.py            # PartDesign module (Pad, Pocket, Hole, ...)
├── _export.py                # Export module (STEP, STL, OBJ, ...)
├── _techdraw.py              # TechDraw module (engineering drawings)
├── _spreadsheet.py           # Spreadsheet module
├── _assembly.py              # Assembly module
├── _path.py                  # Path module (CAM)
├── _fem.py                   # FEM module (finite element analysis)
├── _image.py                 # Image module
├── _material.py              # Material module
├── _inspection.py            # Inspection module
└── __main__.py              # Direct execution entry
```

## Supported Modules

| Module | Function | Status |
|--------|----------|--------|
| Part | Solid modeling, basic geometry | ✅ |
| Sketcher | 2D constrained sketches | ✅ |
| Draft | 2D drawing and annotation | ✅ |
| Arch | Building Information Modeling (BIM) | ✅ |
| Mesh | Mesh processing | ✅ |
| Surface | Surface modeling | ✅ |
| PartDesign | Part design | ✅ |
| TechDraw | Engineering drawings | ✅ |
| Spreadsheet | Spreadsheets, parametric | ✅ |
| Assembly | Assembly management | ✅ |
| Path | CAM machining paths | ✅ |
| FEM | Finite element analysis | ✅ |
| Image | Image processing | ✅ |
| Material | Material management | ✅ |
| Inspection | Inspection and measurement | ✅ |

## Contributing

Issues and Pull Requests are welcome!

## License

LGPL 2.1+

## Contact

- GitHub Issues: https://github.com/MiniMax-AI/freecad-cli/issues
