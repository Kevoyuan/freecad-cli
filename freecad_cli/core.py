# -*- coding: utf-8 -*-
"""
FreeCAD CLI - Main Command Line Interface
==========================================

FreeCAD's complete command line interface providing command line access to all FreeCAD Python APIs.
Supports AI systems to invoke all FreeCAD CAD functionality through structured commands.

Supported command groups:
- document: Document operations
- part: Part (component) module
- sketch: Sketcher module
- draft: Draft module
- arch: Arch (architectural) module
- mesh: Mesh module
- boolean: Boolean operations
- export: Export functionality
- info: Information queries

Author: MiniMax Agent
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

# Exit codes
EXIT_GENERAL = 1
EXIT_USAGE = 2
EXIT_FREECAD = 3

try:
    from .formatter import get_formatter, OutputFormatter
    from .freecad_integration import get_wrapper, check_freecad, FreeCADWrapper
    from .decorators import NonEmptyString
except ImportError:
    # Support running directly
    from freecad_cli.formatter import get_formatter, OutputFormatter
    from freecad_cli.freecad_integration import get_wrapper, check_freecad, FreeCADWrapper
    from freecad_cli.decorators import NonEmptyString


# ============================================================================
# Global Options
# ============================================================================

@click.group()
@click.option('--format', '-f',
              type=click.Choice(['json', 'yaml', 'text', 'table']),
              default='json',
              help='Output format (default: json)')
@click.option('--pretty/--no-pretty',
              default=True,
              help='Pretty print JSON output')
@click.option('--headless/--gui',
              default=True,
              help='Headless mode or GUI mode')
@click.option('--verbose/-v',
              is_flag=True,
              help='Verbose output')
@click.pass_context
def cli(ctx, format, pretty, headless, verbose):
    """
    FreeCAD CLI - FreeCAD Command Line Interface

    Provides command line access to all FreeCAD functionality, supporting AI system invocation.

    Global options (such as --format, --pretty, --verbose) must be placed before subcommands.

    Examples:
        freecad-cli --format json part create --name MyBox --type Box
        freecad-cli --pretty part create --name MyBox --type Box
        freecad-cli sketch create --name MySketch
        freecad-cli list
    """
    ctx.ensure_object(dict)
    ctx.obj['FORMAT'] = format
    ctx.obj['PRETTY'] = pretty
    ctx.obj['HEADLESS'] = headless
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['FORMATTER'] = get_formatter(format, pretty)


def output_result(ctx, result: Any, message: str = "", status: str = "success"):
    """Format and output result"""
    formatter: OutputFormatter = ctx.obj['FORMATTER']
    click.echo(formatter.format(result, status=status, message=message))


def output_error(ctx, message: str, details: Any = None, exit_code: int = EXIT_GENERAL):
    """Output error message"""
    formatter: OutputFormatter = ctx.obj['FORMATTER']
    click.echo(formatter.error(message, details), err=True)
    sys.exit(exit_code)


def output_freecad_error(ctx, message: str, details: Any = None):
    """Output FreeCAD-specific error message"""
    output_error(ctx, message, details, exit_code=EXIT_FREECAD)


# ============================================================================
# Document Command Group
# ============================================================================

@cli.group('document')
def document_group():
    """Document operation commands"""
    pass


@document_group.command('create')
@click.option('--name', '-n', default='Unnamed', type=NonEmptyString(), help='Document name')
@click.pass_context
def document_create(ctx, name):
    """Create a new document"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    result = wrapper.initialize()
    output_result(ctx, result, f"Document '{name}' created successfully")


@document_group.command('list')
@click.pass_context
def document_list(ctx):
    """List all objects"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    objects = wrapper.list_objects()
    output_result(ctx, objects, f"Total {len(objects)} objects")


@document_group.command('info')
@click.pass_context
def document_info(ctx):
    """Display document information"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    init_result = wrapper.initialize()

    if not init_result.get('success'):
        output_freecad_error(ctx, "Failed to initialize FreeCAD", init_result)

    doc = wrapper.get_document()
    info = {
        "name": doc.Name if doc else None,
        "objects_count": len(doc.Objects) if doc else 0,
        "available": check_freecad(),
        "headless": ctx.obj['HEADLESS']
    }
    output_result(ctx, info)


# ============================================================================
# Part (Component) Command Group
# ============================================================================

@cli.group('part')
def part_group():
    """Part (component) module - Create basic geometry"""
    pass


@part_group.command('create')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Object name')
@click.option('--type', '-t',
              type=click.Choice(['Box', 'Cylinder', 'Sphere', 'Cone', 'Torus', 'Ellipsoid']),
              default='Box',
              help='Geometry type')
@click.option('--params', '-p',
              default='{}',
              help='Geometry parameters (JSON format)')
@click.pass_context
def part_create(ctx, name, type, params):
    """Create a Part geometry"""
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        output_error(ctx, "Parameters must be valid JSON format", exit_code=EXIT_USAGE)

    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_part(name, type, params_dict)

    if result.get('success'):
        output_result(ctx, result, f"Part '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@part_group.command('list')
@click.option('--type-filter', '-f', help='Filter by type')
@click.pass_context
def part_list(ctx, type_filter):
    """List all Part objects"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()

    filter_str = "Part::" if type_filter else None
    objects = wrapper.list_objects(filter_str)

    output_result(ctx, objects, f"Total {len(objects)} Part objects")


@part_group.command('info')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Object name')
@click.pass_context
def part_info(ctx, name):
    """Get Part object information"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.get_object_info(name)
    output_result(ctx, result)


# ============================================================================
# Sketch Command Group
# ============================================================================

@cli.group('sketch')
def sketch_group():
    """Sketcher module - 2D sketch drawing"""
    pass


@sketch_group.command('create')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Sketch name')
@click.option('--plane', '-p',
              type=click.Choice(['XY', 'XZ', 'YZ']),
              default='XY',
              help='Sketch plane')
@click.pass_context
def sketch_create(ctx, name, plane):
    """Create a new sketch"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_sketch(name, plane)

    if result.get('success'):
        output_result(ctx, result, f"Sketch '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@sketch_group.command('add-line')
@click.option('--sketch', '-s', required=True, help='Sketch name')
@click.option('--x1', type=float, default=0.0, help='Start point X coordinate')
@click.option('--y1', type=float, default=0.0, help='Start point Y coordinate')
@click.option('--x2', type=float, default=10.0, help='End point X coordinate')
@click.option('--y2', type=float, default=10.0, help='End point Y coordinate')
@click.pass_context
def sketch_add_line(ctx, sketch, x1, y1, x2, y2):
    """Add a line to a sketch"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.add_sketch_geometry(sketch, "Line", {
        "x1": x1, "y1": y1, "x2": x2, "y2": y2
    })

    if result.get('success'):
        output_result(ctx, result, "Line added successfully")
    else:
        output_error(ctx, result.get('error', 'Addition failed'), result)


@sketch_group.command('add-circle')
@click.option('--sketch', '-s', required=True, help='Sketch name')
@click.option('--cx', type=float, default=0.0, help='Circle center X coordinate')
@click.option('--cy', type=float, default=0.0, help='Circle center Y coordinate')
@click.option('--radius', '-r', type=float, default=5.0, help='Radius')
@click.pass_context
def sketch_add_circle(ctx, sketch, cx, cy, radius):
    """Add a circle to a sketch"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.add_sketch_geometry(sketch, "Circle", {
        "cx": cx, "cy": cy, "radius": radius
    })

    if result.get('success'):
        output_result(ctx, result, "Circle added successfully")
    else:
        output_error(ctx, result.get('error', 'Addition failed'), result)


@sketch_group.command('list')
@click.pass_context
def sketch_list(ctx):
    """List all sketches"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    objects = wrapper.list_objects("Sketcher")
    output_result(ctx, objects, f"Total {len(objects)} sketches")


# ============================================================================
# Draft Command Group
# ============================================================================

@cli.group('draft')
def draft_group():
    """Draft module - 2D drawing and annotations"""
    pass


@draft_group.command('line')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Line name')
@click.option('--x1', type=float, default=0.0, help='Start X')
@click.option('--y1', type=float, default=0.0, help='Start Y')
@click.option('--z1', type=float, default=0.0, help='Start Z')
@click.option('--x2', type=float, default=10.0, help='End X')
@click.option('--y2', type=float, default=10.0, help='End Y')
@click.option('--z2', type=float, default=0.0, help='End Z')
@click.pass_context
def draft_line(ctx, name, x1, y1, z1, x2, y2, z2):
    """Create a line"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_draft_object(name, "Line", {
        "x1": x1, "y1": y1, "z1": z1,
        "x2": x2, "y2": y2, "z2": z2
    })

    if result.get('success'):
        output_result(ctx, result, f"Line '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@draft_group.command('circle')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Circle name')
@click.option('--radius', '-r', type=float, default=10.0, help='Radius')
@click.option('--face/--wire', default=False, help='Whether to create a face')
@click.pass_context
def draft_circle(ctx, name, radius, face):
    """Create a circle"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_draft_object(name, "Circle", {
        "radius": radius,
        "face": face
    })

    if result.get('success'):
        output_result(ctx, result, f"Circle '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@draft_group.command('rectangle')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Rectangle name')
@click.option('--length', '-l', type=float, default=10.0, help='Length')
@click.option('--height', '-h', type=float, default=5.0, help='Height')
@click.option('--face/--wire', default=False, help='Whether to create a face')
@click.pass_context
def draft_rectangle(ctx, name, length, height, face):
    """Create a rectangle"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_draft_object(name, "Rectangle", {
        "length": length,
        "height": height,
        "face": face
    })

    if result.get('success'):
        output_result(ctx, result, f"Rectangle '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@draft_group.command('polygon')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Polygon name')
@click.option('--sides', '-s', type=int, default=6, help='Number of sides')
@click.option('--radius', '-r', type=float, default=10.0, help='Circumradius')
@click.pass_context
def draft_polygon(ctx, name, sides, radius):
    """Create a regular polygon"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_draft_object(name, "Polygon", {
        "n_sides": sides,
        "radius": radius
    })

    if result.get('success'):
        output_result(ctx, result, f"Polygon '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


# ============================================================================
# Arch (Architectural) Command Group
# ============================================================================

@cli.group('arch')
def arch_group():
    """Arch module - BIM and architectural modeling"""
    pass


@arch_group.command('wall')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Wall name')
@click.option('--length', '-l', type=float, default=100.0, help='Length (mm)')
@click.option('--width', '-w', type=float, default=20.0, help='Width (mm)')
@click.option('--height', '-h', type=float, default=300.0, help='Height (mm)')
@click.pass_context
def arch_wall(ctx, name, length, width, height):
    """Create a wall"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_arch_object(name, "Wall", {
        "length": length,
        "width": width,
        "height": height
    })

    if result.get('success'):
        output_result(ctx, result, f"Wall '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@arch_group.command('structure')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Structure name')
@click.option('--length', '-l', type=float, default=100.0, help='Length')
@click.option('--width', '-w', type=float, default=100.0, help='Width')
@click.option('--height', '-h', type=float, default=200.0, help='Height')
@click.pass_context
def arch_structure(ctx, name, length, width, height):
    """Create a structure"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_arch_object(name, "Structure", {
        "length": length,
        "width": width,
        "height": height
    })

    if result.get('success'):
        output_result(ctx, result, f"Structure '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@arch_group.command('window')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Window name')
@click.option('--width', '-w', type=float, default=100.0, help='Width')
@click.option('--height', '-h', type=float, default=150.0, help='Height')
@click.pass_context
def arch_window(ctx, name, width, height):
    """Create a window"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_arch_object(name, "Window", {
        "width": width,
        "height": height
    })

    if result.get('success'):
        output_result(ctx, result, f"Window '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


# ============================================================================
# Boolean Command Group
# ============================================================================

@cli.group('boolean')
def boolean_group():
    """Boolean operation commands"""
    pass


@boolean_group.command('fuse')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Result object name')
@click.option('--object1', '-o1', required=True, help='First object')
@click.option('--object2', '-o2', required=True, help='Second object')
@click.pass_context
def boolean_fuse(ctx, name, object1, object2):
    """Union operation (Fuse)"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.boolean_operation(name, "Fuse", object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"Union '{name}' computed successfully")
    else:
        output_error(ctx, result.get('error', 'Operation failed'), result)


@boolean_group.command('cut')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Result object name')
@click.option('--object1', '-o1', required=True, help='Object to cut')
@click.option('--object2', '-o2', required=True, help='Cutting object')
@click.pass_context
def boolean_cut(ctx, name, object1, object2):
    """Subtraction operation (Cut)"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.boolean_operation(name, "Cut", object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"Subtraction '{name}' computed successfully")
    else:
        output_error(ctx, result.get('error', 'Operation failed'), result)


@boolean_group.command('common')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Result object name')
@click.option('--object1', '-o1', required=True, help='First object')
@click.option('--object2', '-o2', required=True, help='Second object')
@click.pass_context
def boolean_common(ctx, name, object1, object2):
    """Intersection operation (Common)"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.boolean_operation(name, "Common", object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"Intersection '{name}' computed successfully")
    else:
        output_error(ctx, result.get('error', 'Operation failed'), result)


@boolean_group.command('section')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Result object name')
@click.option('--object1', '-o1', required=True, help='First object')
@click.option('--object2', '-o2', required=True, help='Second object')
@click.pass_context
def boolean_section(ctx, name, object1, object2):
    """Section operation (Section)"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.boolean_operation(name, "Section", object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"Section '{name}' computed successfully")
    else:
        output_error(ctx, result.get('error', 'Operation failed'), result)


# ============================================================================
# Export Command Group
# ============================================================================

@cli.group('export')
def export_group():
    """Export commands"""
    pass


@export_group.command('step')
@click.option('--filepath', '-f', required=True, help='Export file path')
@click.pass_context
def export_step(ctx, filepath):
    """Export to STEP format"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.export_document(filepath, "STEP")

    if result.get('success'):
        output_result(ctx, result, f"Exported to {filepath}")
    else:
        output_error(ctx, result.get('error', 'Export failed'), result)


@export_group.command('stl')
@click.option('--filepath', '-f', required=True, help='Export file path')
@click.pass_context
def export_stl(ctx, filepath):
    """Export to STL format"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.export_document(filepath, "STL")

    if result.get('success'):
        output_result(ctx, result, f"Exported to {filepath}")
    else:
        output_error(ctx, result.get('error', 'Export failed'), result)


@export_group.command('obj')
@click.option('--filepath', '-f', required=True, help='Export file path')
@click.pass_context
def export_obj(ctx, filepath):
    """Export to OBJ format"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.export_document(filepath, "OBJ")

    if result.get('success'):
        output_result(ctx, result, f"Exported to {filepath}")
    else:
        output_error(ctx, result.get('error', 'Export failed'), result)


@export_group.command('iges')
@click.option('--filepath', '-f', required=True, help='Export file path')
@click.pass_context
def export_iges(ctx, filepath):
    """Export to IGES format"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.export_document(filepath, "IGES")

    if result.get('success'):
        output_result(ctx, result, f"Exported to {filepath}")
    else:
        output_error(ctx, result.get('error', 'Export failed'), result)


# ============================================================================
# Information Command Group
# ============================================================================

# ============================================================================
# Schema Command Group
# ============================================================================

@cli.group('schema')
def schema_group():
    """Schema commands - AI agent command definitions"""
    pass


@schema_group.command('get')
@click.option('--format', '-f',
              type=click.Choice(['json', 'yaml']),
              default='json',
              help='Output format')
@click.pass_context
def schema_get(ctx, format):
    """Get complete command schema"""
    from ._schema import get_schema

    schema = get_schema()

    if format == 'yaml':
        import yaml
        output = yaml.dump(schema, default_flow_style=False)
        click.echo(output)
    else:
        import json
        click.echo(json.dumps(schema, indent=2))


@schema_group.command('command')
@click.option('--group', '-g', required=True, help='Command group')
@click.option('--command', '-c', required=True, help='Command name')
@click.pass_context
def schema_command(ctx, group, command):
    """Get schema for a specific command"""
    from ._schema import get_command_schema

    schema = get_command_schema(group, command)

    if schema:
        import json
        click.echo(json.dumps({
            "group": group,
            "command": command,
            "schema": schema
        }, indent=2))
    else:
        output_error(ctx, f"Command not found: {group}.{command}", exit_code=EXIT_USAGE)


@schema_group.command('list')
@click.pass_context
def schema_list(ctx):
    """List all available commands"""
    from ._schema import list_commands

    commands = list_commands()
    click.echo("\n".join(commands))


# ============================================================================
# Info Command Group
# ============================================================================

@cli.group('info')
def info_group():
    """Information query commands"""
    pass


@info_group.command('object')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Object name')
@click.pass_context
def info_object(ctx, name):
    """Get detailed object information"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.get_object_info(name)
    output_result(ctx, result)


@info_group.command('status')
@click.pass_context
def info_status(ctx):
    """Display FreeCAD status"""
    freecad_available = check_freecad()
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    init_result = wrapper.initialize()

    status = {
        "freecad_available": freecad_available,
        "freecad_installed": freecad_available,
        "headless_mode": ctx.obj['HEADLESS'],
        "initialized": init_result.get('success', False),
        "version": None
    }

    if freecad_available:
        try:
            import FreeCAD
            status["version"] = FreeCAD.Version()
        except:
            pass

    output_result(ctx, status)


@info_group.command('modules')
@click.pass_context
def info_modules(ctx):
    """List available modules"""
    modules = {
        "core": {
            "name": "Part",
            "description": "Part and solid modeling",
            "available": True
        },
        "sketcher": {
            "name": "Sketcher",
            "description": "2D sketch constraint solver",
            "available": True
        },
        "draft": {
            "name": "Draft",
            "description": "2D drawing and annotations",
            "available": True
        },
        "arch": {
            "name": "Arch",
            "description": "Building Information Modeling (BIM)",
            "available": True
        },
        "mesh": {
            "name": "Mesh",
            "description": "Mesh processing",
            "available": True
        },
        "surface": {
            "name": "Surface",
            "description": "Surface modeling",
            "available": True
        },
        "design": {
            "name": "PartDesign",
            "description": "Part design workbench",
            "available": True
        }
    }
    output_result(ctx, modules)


# ============================================================================
# Object Operation Commands
# ============================================================================

@cli.group('object')
def object_group():
    """Object operation commands"""
    pass


@object_group.command('delete')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Object name')
@click.pass_context
def object_delete(ctx, name):
    """Delete an object"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.delete_object(name)

    if result.get('success'):
        output_result(ctx, result, f"Object '{name}' deleted")
    else:
        output_error(ctx, result.get('error', 'Deletion failed'), result)


@object_group.command('list')
@click.option('--type', '-t', help='Type filter')
@click.pass_context
def object_list(ctx, type):
    """List all objects"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()

    filter_str = type if type else None
    objects = wrapper.list_objects(filter_str)

    output_result(ctx, objects, f"Total {len(objects)} objects")


# ============================================================================
# Mesh Command Group
# ============================================================================

@cli.group('mesh')
def mesh_group():
    """Mesh module - Mesh processing and operations"""
    pass


@mesh_group.command('create')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Object name')
@click.option('--type', '-t',
              type=click.Choice(['RegularMesh', 'Triangle', 'Grid']),
              default='RegularMesh',
              help='Mesh type')
@click.option('--params', '-p',
              default='{}',
              help='Mesh parameters (JSON format)')
@click.pass_context
def mesh_create(ctx, name, type, params):
    """Create a Mesh object"""
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        output_error(ctx, "Parameters must be valid JSON format", exit_code=EXIT_USAGE)

    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_mesh_object(name, type, params_dict)

    if result.get('success'):
        output_result(ctx, result, f"Mesh '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@mesh_group.command('from-shape')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Mesh object name')
@click.option('--source', '-s', required=True, help='Source shape object name')
@click.option('--deflection', '-d', type=float, default=0.1, help='Mesh precision')
@click.pass_context
def mesh_from_shape(ctx, name, source, deflection):
    """Create mesh from shape"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.mesh_from_shape(name, source, deflection)

    if result.get('success'):
        output_result(ctx, result, f"Mesh '{name}' created from shape successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@mesh_group.command('boolean')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Result object name')
@click.option('--operation', '-o',
              type=click.Choice(['Union', 'Intersection', 'Difference']),
              required=True,
              help='Boolean operation type')
@click.option('--object1', '-o1', required=True, help='First mesh object')
@click.option('--object2', '-o2', required=True, help='Second mesh object')
@click.pass_context
def mesh_boolean(ctx, name, operation, object1, object2):
    """Mesh boolean operation"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.mesh_boolean(name, operation, object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"Mesh boolean operation '{name}' succeeded")
    else:
        output_error(ctx, result.get('error', 'Operation failed'), result)


@mesh_group.command('list')
@click.pass_context
def mesh_list(ctx):
    """List all Mesh objects"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    objects = wrapper.list_objects("Mesh")
    output_result(ctx, objects, f"Total {len(objects)} Mesh objects")


# ============================================================================
# Surface Command Group
# ============================================================================

@cli.group('surface')
def surface_group():
    """Surface module - Surface modeling"""
    pass


@surface_group.command('create')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Surface object name')
@click.option('--type', '-t',
              type=click.Choice(['Fill', 'Sweep', 'Loft', 'Bezier']),
              default='Fill',
              help='Surface type')
@click.option('--params', '-p',
              default='{}',
              help='Surface parameters (JSON format)')
@click.pass_context
def surface_create(ctx, name, type, params):
    """Create a Surface"""
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        output_error(ctx, "Parameters must be valid JSON format", exit_code=EXIT_USAGE)

    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_surface(name, type, params_dict)

    if result.get('success'):
        output_result(ctx, result, f"Surface '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@surface_group.command('from-edges')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Surface object name')
@click.option('--sketch', '-s', required=True, help='Sketch name')
@click.pass_context
def surface_from_edges(ctx, name, sketch):
    """Create surface from sketch edges"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.surface_from_edges(name, sketch)

    if result.get('success'):
        output_result(ctx, result, f"Surface '{name}' created from edges successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


# ============================================================================
# PartDesign Command Group
# ============================================================================

@cli.group('partdesign')
def partdesign_group():
    """PartDesign module - Part design and features"""
    pass


@partdesign_group.command('create-body')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Body name')
@click.pass_context
def partdesign_create_body(ctx, name):
    """Create a PartDesign Body"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_partdesign_body(name)

    if result.get('success'):
        output_result(ctx, result, f"Body '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@partdesign_group.command('pad')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Pad name')
@click.option('--body', '-b', required=True, help='Body name')
@click.option('--sketch', '-s', required=True, help='Sketch name')
@click.option('--length', '-l', type=float, default=10.0, help='Extrusion length')
@click.option('--direction', '-d',
              type=click.Choice(['Normal', 'Reversed', 'Double']),
              default='Normal',
              help='Extrusion direction')
@click.pass_context
def partdesign_pad(ctx, name, body, sketch, length, direction):
    """Create a Pad extrusion feature"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_pad(name, body, sketch, length, direction)

    if result.get('success'):
        output_result(ctx, result, f"Pad '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@partdesign_group.command('pocket')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Pocket name')
@click.option('--body', '-b', required=True, help='Body name')
@click.option('--sketch', '-s', required=True, help='Sketch name')
@click.option('--length', '-l', type=float, default=10.0, help='Cut depth')
@click.option('--type', '-t',
              type=click.Choice(['Through', 'UpToFirst', 'UpToFace']),
              default='Through',
              help='Cut type')
@click.pass_context
def partdesign_pocket(ctx, name, body, sketch, length, type):
    """Create a Pocket cut feature"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_pocket(name, body, sketch, length, type)

    if result.get('success'):
        output_result(ctx, result, f"Pocket '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@partdesign_group.command('hole')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Hole name')
@click.option('--body', '-b', required=True, help='Body name')
@click.option('--diameter', '-d', type=float, default=5.0, help='Hole diameter')
@click.option('--depth', '-l', type=float, default=10.0, help='Hole depth')
@click.option('--position', '-p',
              help='Hole position (x,y,z)',
              default=None)
@click.pass_context
def partdesign_hole(ctx, name, body, diameter, depth, position):
    """Create a hole feature"""
    pos = None
    if position:
        try:
            pos = tuple(map(float, position.split(',')))
        except ValueError:
            output_error(ctx, "Position must be in x,y,z format", exit_code=EXIT_USAGE)

    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_hole(name, body, diameter, depth, pos)

    if result.get('success'):
        output_result(ctx, result, f"Hole '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@partdesign_group.command('revolution')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Revolution name')
@click.option('--body', '-b', required=True, help='Body name')
@click.option('--sketch', '-s', required=True, help='Sketch name')
@click.option('--angle', '-a', type=float, default=360.0, help='Revolution angle')
@click.pass_context
def partdesign_revolution(ctx, name, body, sketch, angle):
    """Create a revolution feature"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_revolution(name, body, sketch, angle)

    if result.get('success'):
        output_result(ctx, result, f"Revolution '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@partdesign_group.command('groove')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Groove name')
@click.option('--body', '-b', required=True, help='Body name')
@click.option('--angle', '-a', type=float, default=360.0, help='Revolution angle')
@click.option('--radius', '-r', type=float, default=5.0, help='Revolution radius')
@click.pass_context
def partdesign_groove(ctx, name, body, angle, radius):
    """Create a groove cut feature"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_groove(name, body, angle, radius)

    if result.get('success'):
        output_result(ctx, result, f"Groove '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@partdesign_group.command('fillet')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Fillet name')
@click.option('--body', '-b', required=True, help='Body name')
@click.option('--radius', '-r', type=float, default=2.0, help='Fillet radius')
@click.pass_context
def partdesign_fillet(ctx, name, body, radius):
    """Create a fillet feature"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_fillet(name, body, radius)

    if result.get('success'):
        output_result(ctx, result, f"Fillet '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@partdesign_group.command('chamfer')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Chamfer name')
@click.option('--body', '-b', required=True, help='Body name')
@click.option('--size', '-s', type=float, default=1.0, help='Chamfer size')
@click.pass_context
def partdesign_chamfer(ctx, name, body, size):
    """Create a chamfer feature"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_chamfer(name, body, size)

    if result.get('success'):
        output_result(ctx, result, f"Chamfer '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


# ============================================================================
# TechDraw Command Group
# ============================================================================

@cli.group('techdraw')
def techdraw_group():
    """TechDraw module - Technical drawings and annotations"""
    pass


@techdraw_group.command('create-page')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Page name')
@click.option('--template', '-t', default='A4_Landscape',
              help='Drawing template (A4_Landscape, A4_Portrait, A3_Landscape)')
@click.pass_context
def techdraw_create_page(ctx, name, template):
    """Create a TechDraw page"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.techdraw_create_page(name, template)

    if result.get('success'):
        output_result(ctx, result, f"Page '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@techdraw_group.command('add-view')
@click.option('--page', '-p', required=True, help='Page name')
@click.option('--source', '-s', required=True, help='Source object name')
@click.option('--projection', '--proj', default='FirstAngle',
              type=click.Choice(['FirstAngle', 'ThirdAngle']),
              help='Projection type')
@click.pass_context
def techdraw_add_view(ctx, page, source, projection):
    """Add an engineering view"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.techdraw_add_view(page, source, projection)

    if result.get('success'):
        output_result(ctx, result, f"View created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@techdraw_group.command('add-dimension')
@click.option('--view', '-v', required=True, help='View name')
@click.option('--type', '-t',
              type=click.Choice(['Horizontal', 'Vertical', 'Radius', 'Diameter', 'Angle']),
              default='Horizontal',
              help='Dimension type')
@click.pass_context
def techdraw_add_dimension(ctx, view, type):
    """Add a dimension annotation"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.techdraw_add_dimension(view, type, [])

    if result.get('success'):
        output_result(ctx, result, f"Dimension annotation created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@techdraw_group.command('export')
@click.option('--page', '-p', required=True, help='Page name')
@click.option('--filepath', '-f', required=True, help='Export file path')
@click.option('--format', '-fmt',
              type=click.Choice(['PDF', 'SVG', 'DXF']),
              default='PDF',
              help='Export format')
@click.pass_context
def techdraw_export(ctx, page, filepath, format):
    """Export drawing"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.techdraw_export(page, filepath, format)

    if result.get('success'):
        output_result(ctx, result, f"Exported to {filepath}")
    else:
        output_error(ctx, result.get('error', 'Export failed'), result)


# ============================================================================
# Spreadsheet Command Group
# ============================================================================

@cli.group('spreadsheet')
def spreadsheet_group():
    """Spreadsheet module - Parametric spreadsheets"""
    pass


@spreadsheet_group.command('create')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Spreadsheet name')
@click.pass_context
def spreadsheet_create(ctx, name):
    """Create a spreadsheet"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.spreadsheet_create(name)

    if result.get('success'):
        output_result(ctx, result, f"Spreadsheet '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@spreadsheet_group.command('set-cell')
@click.option('--sheet', '-s', required=True, help='Spreadsheet name')
@click.option('--cell', '-c', required=True, help='Cell (e.g. A1)')
@click.option('--value', '-v', required=True, help='Cell value')
@click.pass_context
def spreadsheet_set_cell(ctx, sheet, cell, value):
    """Set cell value"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.spreadsheet_set_cell(sheet, cell, value)

    if result.get('success'):
        output_result(ctx, result, f"Cell {cell} set successfully")
    else:
        output_error(ctx, result.get('error', 'Setting failed'), result)


@spreadsheet_group.command('set-formula')
@click.option('--sheet', '-s', required=True, help='Spreadsheet name')
@click.option('--cell', '-c', required=True, help='Cell')
@click.option('--formula', '-f', required=True, help='Formula (e.g. =A1*2)')
@click.pass_context
def spreadsheet_set_formula(ctx, sheet, cell, formula):
    """Set cell formula"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.spreadsheet_set_formula(sheet, cell, formula)

    if result.get('success'):
        output_result(ctx, result, f"Formula set successfully")
    else:
        output_error(ctx, result.get('error', 'Setting failed'), result)


@spreadsheet_group.command('link')
@click.option('--sheet', '-s', required=True, help='Spreadsheet name')
@click.option('--object', '-o', required=True, help='Object name')
@click.option('--property', '-p', required=True, help='Property name')
@click.option('--cell', '-c', required=True, help='Cell')
@click.pass_context
def spreadsheet_link(ctx, sheet, object, property, cell):
    """Link spreadsheet to object property"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.spreadsheet_link(sheet, object, property, cell)

    if result.get('success'):
        output_result(ctx, result, f"Link created successfully")
    else:
        output_error(ctx, result.get('error', 'Link failed'), result)


# ============================================================================
# Assembly Command Group
# ============================================================================

@cli.group('assembly')
def assembly_group():
    """Assembly module - Assembly management"""
    pass


@assembly_group.command('create')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Assembly name')
@click.pass_context
def assembly_create(ctx, name):
    """Create an assembly"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.assembly_create(name)

    if result.get('success'):
        output_result(ctx, result, f"Assembly '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@assembly_group.command('add-part')
@click.option('--assembly', '-a', required=True, help='Assembly name')
@click.option('--part', '-p', required=True, help='Part name')
@click.option('--placement', '-pl', default='[0, 0, 0]', help='Position [x, y, z]')
@click.pass_context
def assembly_add_part(ctx, assembly, part, placement):
    """Add a part to an assembly"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.assembly_add_part(assembly, part, placement)

    if result.get('success'):
        output_result(ctx, result, f"Part '{part}' added to assembly successfully")
    else:
        output_error(ctx, result.get('error', 'Addition failed'), result)


@assembly_group.command('add-constraint')
@click.option('--assembly', '-a', required=True, help='Assembly name')
@click.option('--type', '-t', required=True,
              type=click.Choice(['Coincident', 'Distance', 'Angle']),
              help='Constraint type')
@click.option('--object1', '-o1', required=True, help='First object')
@click.option('--object2', '-o2', required=True, help='Second object')
@click.pass_context
def assembly_add_constraint(ctx, assembly, type, object1, object2):
    """Add an assembly constraint"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.assembly_add_constraint(assembly, type, object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"Constraint added successfully")
    else:
        output_error(ctx, result.get('error', 'Addition failed'), result)


# ============================================================================
# Path (CAM) Command Group
# ============================================================================

@cli.group('path')
def path_group():
    """Path (CAM) module - CNC machining paths"""
    pass


@path_group.command('create-job')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Job name')
@click.option('--base', '-b', required=True, help='Base object name')
@click.pass_context
def path_create_job(ctx, name, base):
    """Create a machining job"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.path_create_job(name, base)

    if result.get('success'):
        output_result(ctx, result, f"Machining job '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@path_group.command('add-operation')
@click.option('--job', '-j', required=True, help='Job name')
@click.option('--type', '-t',
              type=click.Choice(['Drill', 'Profile', 'Pocket', 'Slot']),
              default='Drill',
              help='Operation type')
@click.pass_context
def path_add_operation(ctx, job, type):
    """Add a machining operation"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.path_add_operation(job, type)

    if result.get('success'):
        output_result(ctx, result, f"Operation '{type}' added successfully")
    else:
        output_error(ctx, result.get('error', 'Addition failed'), result)


@path_group.command('export-gcode')
@click.option('--job', '-j', required=True, help='Job name')
@click.option('--filepath', '-f', required=True, help='Export file path')
@click.option('--post', '-p', default='linuxcnc', help='Post processor')
@click.pass_context
def path_export_gcode(ctx, job, filepath, post):
    """Export G-code"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.path_export_gcode(job, filepath, post)

    if result.get('success'):
        output_result(ctx, result, f"G-code exported to {filepath}")
    else:
        output_error(ctx, result.get('error', 'Export failed'), result)


# ============================================================================
# FEM (Finite Element Analysis) Command Group
# ============================================================================

@cli.group('fem')
def fem_group():
    """FEM (Finite Element Analysis) module - Engineering analysis"""
    pass


@fem_group.command('create-analysis')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Analysis name')
@click.option('--type', '-t',
              type=click.Choice(['static', 'modal', 'thermomechanical']),
              default='static',
              help='Analysis type')
@click.pass_context
def fem_create_analysis(ctx, name, type):
    """Create a finite element analysis"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.fem_create_analysis(name, type)

    if result.get('success'):
        output_result(ctx, result, f"Analysis '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@fem_group.command('add-material')
@click.option('--analysis', '-a', required=True, help='Analysis name')
@click.option('--material', '-m',
              type=click.Choice(['Steel', 'Aluminum', 'Copper']),
              default='Steel',
              help='Material')
@click.pass_context
def fem_add_material(ctx, analysis, material):
    """Add material"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.fem_add_material(analysis, material)

    if result.get('success'):
        output_result(ctx, result, f"Material '{material}' added successfully")
    else:
        output_error(ctx, result.get('error', 'Addition failed'), result)


@fem_group.command('add-bc')
@click.option('--analysis', '-a', required=True, help='Analysis name')
@click.option('--type', '-t',
              type=click.Choice(['Fixed', 'Force', 'Pressure']),
              required=True,
              help='Boundary condition type')
@click.option('--object', '-o', required=True, help='Object name')
@click.pass_context
def fem_add_bc(ctx, analysis, type, object):
    """Add boundary condition"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.fem_add_boundary_condition(analysis, type, object, {})

    if result.get('success'):
        output_result(ctx, result, f"Boundary condition added successfully")
    else:
        output_error(ctx, result.get('error', 'Addition failed'), result)


@fem_group.command('run')
@click.option('--analysis', '-a', required=True, help='Analysis name')
@click.pass_context
def fem_run(ctx, analysis):
    """Run finite element analysis"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.fem_run_analysis(analysis)

    if result.get('success'):
        output_result(ctx, result, f"Analysis '{analysis}' run completed")
    else:
        output_error(ctx, result.get('error', 'Run failed'), result)


# ============================================================================
# Image Command Group
# ============================================================================

@cli.group('image')
def image_group():
    """Image module - Image processing"""
    pass


@image_group.command('import')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Image name')
@click.option('--filepath', '-f', required=True, help='Image file path')
@click.pass_context
def image_import(ctx, name, filepath):
    """Import an image"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.image_import(name, filepath)

    if result.get('success'):
        output_result(ctx, result, f"Image '{name}' imported successfully")
    else:
        output_error(ctx, result.get('error', 'Import failed'), result)


@image_group.command('scale')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Image name')
@click.option('--x', '-x', type=float, default=1.0, help='X scale')
@click.option('--y', '-y', type=float, default=1.0, help='Y scale')
@click.pass_context
def image_scale(ctx, name, x, y):
    """Scale an image"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.image_scale(name, x, y)

    if result.get('success'):
        output_result(ctx, result, f"Image '{name}' scaled successfully")
    else:
        output_error(ctx, result.get('error', 'Scale failed'), result)


# ============================================================================
# Material Command Group
# ============================================================================

@cli.group('material')
def material_group():
    """Material module - Material management"""
    pass


@material_group.command('create')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Material name')
@click.option('--density', '-d', type=float, help='Density (kg/m³)')
@click.option('--youngs', '-y', type=float, help='Youngs modulus (MPa)')
@click.option('--poisson', '-p', type=float, help='Poisson ratio')
@click.pass_context
def material_create(ctx, name, density, youngs, poisson):
    """Create a material"""
    properties = {}
    if density:
        properties['Density'] = f"{density} kg/m^3"
    if youngs:
        properties['YoungsModulus'] = f"{youngs} MPa"
    if poisson:
        properties['PoissonRatio'] = str(poisson)

    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.material_create(name, properties)

    if result.get('success'):
        output_result(ctx, result, f"Material '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@material_group.command('get-standard')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Material name')
@click.pass_context
def material_get_standard(ctx, name):
    """Get standard material"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.material_get_standard(name)
    output_result(ctx, result)


# ============================================================================
# Inspection Command Group
# ============================================================================

@cli.group('inspection')
def inspection_group():
    """Inspection module - Inspection and measurement"""
    pass


@inspection_group.command('create-check')
@click.option('--name', '-n', required=True, type=NonEmptyString(), help='Check name')
@click.option('--object', '-o', required=True, help='Object to check')
@click.pass_context
def inspection_create_check(ctx, name, object):
    """Create an inspection"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.inspection_create_check(name, object)

    if result.get('success'):
        output_result(ctx, result, f"Inspection '{name}' created successfully")
    else:
        output_error(ctx, result.get('error', 'Creation failed'), result)


@inspection_group.command('measure-distance')
@click.option('--object1', '-o1', required=True, help='First object')
@click.option('--object2', '-o2', required=True, help='Second object')
@click.pass_context
def inspection_measure_distance(ctx, object1, object2):
    """Measure distance"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.inspection_measure_distance(object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"Distance measurement result")
    else:
        output_error(ctx, result.get('error', 'Measurement failed'), result)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    cli(obj={})


if __name__ == '__main__':
    main()
