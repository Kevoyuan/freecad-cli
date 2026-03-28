#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FreeCAD CLI Quick Start Examples
================================

Quick start examples showing how to use various features of FreeCAD CLI.
"""

import sys
import json
from pathlib import Path

# Add package path
sys.path.insert(0, str(Path(__file__).parent.parent))

from freecad_cli import FreeCADWrapper, AICommandParser, BatchProcessor, OutputFormatter


def example_basic_part_creation():
    """Basic part creation example"""
    print("\n" + "="*60)
    print("Example 1: Basic Part Creation")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    wrapper.initialize()

    # 创建各种零件
    parts = [
        ("Box1", "Box", {"length": 10, "width": 10, "height": 5}),
        ("Cylinder1", "Cylinder", {"radius": 3, "height": 8}),
        ("Sphere1", "Sphere", {"radius": 5}),
        ("Cone1", "Cone", {"radius1": 5, "radius2": 2, "height": 10}),
    ]

    for name, shape, params in parts:
        result = wrapper.create_part(name, shape, params)
        print(f"Created {name}: {'Success' if result.get('success') else 'Failed'}")

    # List all parts
    objects = wrapper.list_objects()
    print(f"\nDocument contains {len(objects)} objects")


def example_sketch_creation():
    """Sketch creation example"""
    print("\n" + "="*60)
    print("Example 2: Sketch Creation")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    wrapper.initialize()

    # Create sketch
    result = wrapper.create_sketch("MySketch", "XY")
    print(f"Created sketch: {'Success' if result.get('success') else 'Failed'}")

    # Add geometry elements
    result = wrapper.add_sketch_geometry("MySketch", "Line", {
        "x1": 0, "y1": 0, "x2": 10, "y2": 10
    })
    print(f"Added line: {'Success' if result.get('success') else 'Failed'}")

    result = wrapper.add_sketch_geometry("MySketch", "Circle", {
        "cx": 5, "cy": 5, "radius": 3
    })
    print(f"Added circle: {'Success' if result.get('success') else 'Failed'}")


def example_draft_operations():
    """Draft operations example"""
    print("\n" + "="*60)
    print("Example 3: Draft Drawing Operations")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    wrapper.initialize()

    operations = [
        ("Line1", "Line", {"x1": 0, "y1": 0, "z1": 0, "x2": 100, "y2": 100, "z2": 0}),
        ("Circle1", "Circle", {"radius": 50, "face": False}),
        ("Rectangle1", "Rectangle", {"length": 80, "height": 40, "face": True}),
        ("Polygon1", "Polygon", {"n_sides": 6, "radius": 30}),
    ]

    for name, shape, params in operations:
        result = wrapper.create_draft_object(name, shape, params)
        print(f"Created {name}: {'Success' if result.get('success') else 'Failed'}")


def example_boolean_operations():
    """Boolean operations example"""
    print("\n" + "="*60)
    print("Example 4: Boolean Operations")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    wrapper.initialize()

    # Create two boxes for boolean operations
    wrapper.create_part("Box1", "Box", {"length": 10, "width": 10, "height": 10})
    wrapper.create_part("Box2", "Box", {"length": 5, "width": 5, "height": 15})

    # Union
    result = wrapper.boolean_operation("Union", "Fuse", "Box1", "Box2")
    print(f"Union operation: {'Success' if result.get('success') else 'Failed'}")

    # Recreate for difference operation
    wrapper.create_part("Box3", "Box", {"length": 10, "width": 10, "height": 10})
    wrapper.create_part("Cylinder1", "Cylinder", {"radius": 2, "height": 15})

    result = wrapper.boolean_operation("Cut", "Cut", "Box3", "Cylinder1")
    print(f"Difference operation: {'Success' if result.get('success') else 'Failed'}")


def example_natural_language_parsing():
    """Natural language parsing example"""
    print("\n" + "="*60)
    print("Example 5: Natural Language Command Parsing")
    print("="*60)

    parser = AICommandParser()

    commands = [
        "Create a box named TestBox",
        "Create a sphere with radius 5",
        "Create sketch on XY plane",
        "Add a line",
        "Draw a hexagon",
        "Create a wall",
    ]

    for cmd in commands:
        result = parser.parse(cmd)
        if result.get("success"):
            print(f"'{cmd}'")
            print(f"  -> Command group: {result['command_group']}")
            print(f"  -> Command: {result['command']}")
            print(f"  -> Parameters: {result.get('parameters', {})}")
        else:
            print(f"'{cmd}' -> Unable to parse")


def example_batch_processing():
    """Batch processing example"""
    print("\n" + "="*60)
    print("Example 6: Batch Command Processing")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    processor = BatchProcessor(wrapper)
    wrapper.initialize()

    # Define batch commands
    commands = [
        {
            "command_group": "part",
            "command": "create",
            "parameters": {"name": "BatchBox1", "type": "Box", "length": 10, "width": 10, "height": 5}
        },
        {
            "command_group": "part",
            "command": "create",
            "parameters": {"name": "BatchBox2", "type": "Box", "length": 5, "width": 5, "height": 5}
        },
        {
            "command_group": "part",
            "command": "create",
            "parameters": {"name": "BatchCylinder", "type": "Cylinder", "radius": 3, "height": 10}
        },
    ]

    # Execute batch commands
    print("Executing batch commands...")
    results = processor.execute_batch(commands)

    # Show result summary
    summary = processor.get_summary()
    print(f"\nExecution complete:")
    print(f"  Total commands: {summary['total']}")
    print(f"  Success: {summary['success']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Success rate: {summary['success_rate']:.1f}%")


def example_output_formatter():
    """Output formatter example"""
    print("\n" + "="*60)
    print("Example 7: Output Formatting")
    print("="*60)

    formatter = OutputFormatter(output_format="json", pretty=True)

    # 示例数据
    data = {
        "name": "TestBox",
        "type": "Box",
        "dimensions": {
            "length": 10,
            "width": 10,
            "height": 5
        },
        "volume": 500,
        "surface_area": 400
    }

    # Format output
    print("JSON format:")
    print(formatter.format(data, status="success", message="Created successfully"))

    print("\n" + "-"*40)
    print("Plain text format:")
    formatter_text = OutputFormatter(output_format="text", pretty=True)
    print(formatter_text.format(data, status="success", message="Created successfully"))

    print("\n" + "-"*40)
    print("Table format:")
    formatter_table = OutputFormatter(output_format="table", pretty=True)
    table_data = [
        {"name": "Box1", "type": "Box", "volume": 1000},
        {"name": "Cylinder1", "type": "Cylinder", "volume": 785},
        {"name": "Sphere1", "type": "Sphere", "volume": 524},
    ]
    print(formatter_table.format(table_data))


def example_export():
    """Export example"""
    print("\n" + "="*60)
    print("Example 8: Export Operations")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    wrapper.initialize()

    # Create some objects
    wrapper.create_part("ExportBox", "Box", {"length": 10, "width": 10, "height": 5})

    # Export to different formats
    formats = ["STEP", "STL", "OBJ", "IGES"]

    for fmt in formats:
        filepath = f"/tmp/test_model.{fmt.lower()}"
        result = wrapper.export_document(filepath, fmt)
        status = "Success" if result.get("success") else "Failed"
        print(f"Export {fmt}: {status}")


def example_workflow_automation():
    """Workflow automation example"""
    print("\n" + "="*60)
    print("Example 9: Workflow Automation")
    print("="*60)

    from freecad_cli.ai_integration import generate_workflow_commands

    workflow = """
    Create a box named BasePlate with length 100, width 100, height 10
    Create a cylinder named Boss with radius 25, height 20
    Merge BasePlate and Boss, name result Assembly
    Export Assembly as STEP file to output/assembly.step
    """

    print("Input workflow:")
    print(workflow)
    print("\nGenerated CLI commands:")

    commands = generate_workflow_commands(workflow)
    for i, cmd in enumerate(commands, 1):
        print(f"{i}. {cmd}")


def main():
    """Run all examples"""
    print("="*60)
    print("FreeCAD CLI Quick Start Examples")
    print("="*60)
    print("\nNote: When FreeCAD is not installed, mock data will be returned for testing.")

    # Run all examples
    example_basic_part_creation()
    example_sketch_creation()
    example_draft_operations()
    example_boolean_operations()
    example_natural_language_parsing()
    example_batch_processing()
    example_output_formatter()
    example_export()
    example_workflow_automation()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
