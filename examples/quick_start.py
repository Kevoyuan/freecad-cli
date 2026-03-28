#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FreeCAD CLI Quick Start Examples
================================

快速开始示例，展示如何使用 FreeCAD CLI 的各种功能。
"""

import sys
import json
from pathlib import Path

# 添加包路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from freecad_cli import FreeCADWrapper, AICommandParser, BatchProcessor, OutputFormatter


def example_basic_part_creation():
    """基础零件创建示例"""
    print("\n" + "="*60)
    print("示例 1: 基础零件创建")
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
        print(f"创建 {name}: {'成功' if result.get('success') else '失败'}")

    # 列出所有零件
    objects = wrapper.list_objects()
    print(f"\n当前文档共有 {len(objects)} 个对象")


def example_sketch_creation():
    """草图创建示例"""
    print("\n" + "="*60)
    print("示例 2: 草图创建")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    wrapper.initialize()

    # 创建草图
    result = wrapper.create_sketch("MySketch", "XY")
    print(f"创建草图: {'成功' if result.get('success') else '失败'}")

    # 添加几何元素
    result = wrapper.add_sketch_geometry("MySketch", "Line", {
        "x1": 0, "y1": 0, "x2": 10, "y2": 10
    })
    print(f"添加直线: {'成功' if result.get('success') else '失败'}")

    result = wrapper.add_sketch_geometry("MySketch", "Circle", {
        "cx": 5, "cy": 5, "radius": 3
    })
    print(f"添加圆: {'成功' if result.get('success') else '失败'}")


def example_draft_operations():
    """Draft 操作示例"""
    print("\n" + "="*60)
    print("示例 3: Draft 绘制操作")
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
        print(f"创建 {name}: {'成功' if result.get('success') else '失败'}")


def example_boolean_operations():
    """布尔运算示例"""
    print("\n" + "="*60)
    print("示例 4: 布尔运算")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    wrapper.initialize()

    # 创建两个盒子用于布尔运算
    wrapper.create_part("Box1", "Box", {"length": 10, "width": 10, "height": 10})
    wrapper.create_part("Box2", "Box", {"length": 5, "width": 5, "height": 15})

    # 并集
    result = wrapper.boolean_operation("Union", "Fuse", "Box1", "Box2")
    print(f"并集运算: {'成功' if result.get('success') else '失败'}")

    # 重新创建用于差集
    wrapper.create_part("Box3", "Box", {"length": 10, "width": 10, "height": 10})
    wrapper.create_part("Cylinder1", "Cylinder", {"radius": 2, "height": 15})

    result = wrapper.boolean_operation("Cut", "Cut", "Box3", "Cylinder1")
    print(f"差集运算: {'成功' if result.get('success') else '失败'}")


def example_natural_language_parsing():
    """自然语言解析示例"""
    print("\n" + "="*60)
    print("示例 5: 自然语言命令解析")
    print("="*60)

    parser = AICommandParser()

    commands = [
        "创建一个名为 TestBox 的立方体",
        "创建一个半径为 5 的球体",
        "在 XY 平面创建草图",
        "添加一条直线",
        "绘制一个六边形",
        "创建一个墙体",
    ]

    for cmd in commands:
        result = parser.parse(cmd)
        if result.get("success"):
            print(f"'{cmd}'")
            print(f"  -> 命令组: {result['command_group']}")
            print(f"  -> 命令: {result['command']}")
            print(f"  -> 参数: {result.get('parameters', {})}")
        else:
            print(f"'{cmd}' -> 无法解析")


def example_batch_processing():
    """批量处理示例"""
    print("\n" + "="*60)
    print("示例 6: 批量命令处理")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    processor = BatchProcessor(wrapper)
    wrapper.initialize()

    # 定义批量命令
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

    # 执行批量命令
    print("执行批量命令...")
    results = processor.execute_batch(commands)

    # 显示结果摘要
    summary = processor.get_summary()
    print(f"\n执行完成:")
    print(f"  总命令数: {summary['total']}")
    print(f"  成功: {summary['success']}")
    print(f"  失败: {summary['failed']}")
    print(f"  成功率: {summary['success_rate']:.1f}%")


def example_output_formatter():
    """输出格式化示例"""
    print("\n" + "="*60)
    print("示例 7: 输出格式化")
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

    # 格式化输出
    print("JSON 格式:")
    print(formatter.format(data, status="success", message="创建成功"))

    print("\n" + "-"*40)
    print("纯文本格式:")
    formatter_text = OutputFormatter(output_format="text", pretty=True)
    print(formatter_text.format(data, status="success", message="创建成功"))

    print("\n" + "-"*40)
    print("表格格式:")
    formatter_table = OutputFormatter(output_format="table", pretty=True)
    table_data = [
        {"name": "Box1", "type": "Box", "volume": 1000},
        {"name": "Cylinder1", "type": "Cylinder", "volume": 785},
        {"name": "Sphere1", "type": "Sphere", "volume": 524},
    ]
    print(formatter_table.format(table_data))


def example_export():
    """导出示例"""
    print("\n" + "="*60)
    print("示例 8: 导出操作")
    print("="*60)

    wrapper = FreeCADWrapper(headless=True)
    wrapper.initialize()

    # 创建一些对象
    wrapper.create_part("ExportBox", "Box", {"length": 10, "width": 10, "height": 5})

    # 导出为不同格式
    formats = ["STEP", "STL", "OBJ", "IGES"]

    for fmt in formats:
        filepath = f"/tmp/test_model.{fmt.lower()}"
        result = wrapper.export_document(filepath, fmt)
        status = "成功" if result.get("success") else "失败"
        print(f"导出 {fmt}: {status}")


def example_workflow_automation():
    """工作流自动化示例"""
    print("\n" + "="*60)
    print("示例 9: 工作流自动化")
    print("="*60)

    from freecad_cli.ai_integration import generate_workflow_commands

    workflow = """
    创建一个名为 BasePlate 的盒子，长度 100，宽度 100，高度 10
    创建一个名为 Boss 的圆柱，半径 25，高度 20
    合并 BasePlate 和 Boss，结果命名为 Assembly
    导出 Assembly 为 STEP 文件到 output/assembly.step
    """

    print("输入工作流:")
    print(workflow)
    print("\n生成的 CLI 命令:")

    commands = generate_workflow_commands(workflow)
    for i, cmd in enumerate(commands, 1):
        print(f"{i}. {cmd}")


def main():
    """运行所有示例"""
    print("="*60)
    print("FreeCAD CLI 快速开始示例")
    print("="*60)
    print("\n注意: FreeCAD 未安装时，将返回模拟数据进行测试。")

    # 运行所有示例
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
    print("所有示例执行完成!")
    print("="*60)


if __name__ == "__main__":
    main()
