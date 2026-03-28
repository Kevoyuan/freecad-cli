#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FreeCAD CLI Benchmark
====================

Measures the performance of FreeCAD CLI operations.
Can be run directly with Python without Node.js.

Usage:
    python benchmark.py
    python -m pytest tests/benchmark.py -v
"""

import time
import statistics
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from freecad_cli.freecad_integration import FreeCADWrapper, get_wrapper


def benchmark_operation(func, name, iterations=100):
    """Benchmark a single operation"""
    print(f"\n📊 Testing: {name}")
    print("-" * 50)

    times = []
    wrapper = get_wrapper(headless=True)
    wrapper.initialize()

    for i in range(iterations):
        start = time.perf_counter()
        func(wrapper)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    # Calculate statistics
    avg = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0

    print(f"  ✅ {iterations} iterations completed")
    print(f"     Average: {avg:.2f} ms")
    print(f"     Min: {min_time:.2f} ms")
    print(f"     Max: {max_time:.2f} ms")
    print(f"     Std Dev: {std_dev:.2f} ms")

    return {
        "name": name,
        "avg": avg,
        "min": min_time,
        "max": max_time,
        "std_dev": std_dev
    }


def run_benchmark():
    """Run all benchmarks"""
    print("\n" + "=" * 60)
    print("🧪 FreeCAD CLI Benchmark (Python)")
    print("=" * 60)

    iterations = 100

    # Test cases
    tests = [
        ("Part Creation (Box)", lambda w: w.create_part("Box", "Box", {"length": 10})),
        ("Part Creation (Cylinder)", lambda w: w.create_part("Cyl", "Cylinder", {"radius": 5})),
        ("Sketch Creation", lambda w: w.create_sketch("Sketch", "XY")),
        ("Sketch Line", lambda w: w.add_sketch_geometry("Sketch", "Line", {"x1": 0, "y1": 0, "x2": 10, "y2": 10})),
        ("Sketch Circle", lambda w: w.add_sketch_geometry("Sketch", "Circle", {"cx": 5, "cy": 5, "radius": 3})),
        ("Draft Line", lambda w: w.create_draft_object("Line", "Line", {"x1": 0, "y1": 0})),
        ("Draft Circle", lambda w: w.create_draft_object("Circle", "Circle", {"radius": 5})),
        ("Mesh Creation", lambda w: w.create_mesh_object("Mesh", "RegularMesh", {"width": 10, "height": 10})),
        ("Surface Creation", lambda w: w.create_surface("Surf", "Fill")),
        ("PartDesign Body", lambda w: w.create_partdesign_body("Body")),
        ("TechDraw Page", lambda w: w.techdraw_create_page("Page")),
        ("Spreadsheet Create", lambda w: w.spreadsheet_create("Sheet")),
        ("Assembly Create", lambda w: w.assembly_create("Assy")),
        ("FEM Analysis", lambda w: w.fem_create_analysis("Analysis")),
        ("Material Get Standard", lambda w: w.material_get_standard("Steel")),
        ("List Objects", lambda w: w.list_objects()),
        ("Get Object Info", lambda w: w.get_object_info("Test")),
        ("Boolean Fuse", lambda w: w.boolean_operation("Fuse", "Fuse", "Box1", "Box2")),
    ]

    results = []

    for name, func in tests:
        try:
            result = benchmark_operation(func, name, iterations)
            results.append(result)
        except Exception as e:
            print(f"  ❌ Failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("📈 Summary")
    print("=" * 60)

    # Sort by average time
    results.sort(key=lambda x: x["avg"])

    print(f"\n{'Rank':<6} {'Operation':<30} {'Avg (ms)':<12} {'Min':<10} {'Max':<10}")
    print("-" * 70)

    for i, r in enumerate(results, 1):
        print(f"{i:<6} {r['name']:<30} {r['avg']:<12.2f} {r['min']:<10.2f} {r['max']:<10.2f}")

    print("\n" + "=" * 60)
    print("✅ Benchmark complete!")
    print("=" * 60 + "\n")


def run_single_operation_benchmark():
    """Run a quick benchmark of a single operation"""
    print("\n🔥 Quick Performance Test")
    print("-" * 40)

    iterations = 1000
    wrapper = get_wrapper(headless=True)
    wrapper.initialize()

    # Quick test
    start = time.perf_counter()
    for _ in range(iterations):
        wrapper.create_part("Box", "Box", {})
    end = time.perf_counter()

    total_time = (end - start) * 1000
    avg_time = total_time / iterations

    print(f"  {iterations} Part creations:")
    print(f"    Total: {total_time:.2f} ms")
    print(f"    Average: {avg_time:.4f} ms/op")
    print(f"    Throughput: {1000/avg_time:.0f} ops/sec")


if __name__ == "__main__":
    run_benchmark()
    run_single_operation_benchmark()
