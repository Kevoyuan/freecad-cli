# -*- coding: utf-8 -*-
"""
FreeCAD CLI - Main Command Line Interface
==========================================

FreeCAD 完整的命令行接口，提供对所有 FreeCAD Python API 的命令行访问。
支持 AI 系统通过结构化命令调用 FreeCAD 的所有 CAD 功能。

支持的命令组:
- document: 文档操作
- part: Part (零件) 模块
- sketch: Sketcher (草图) 模块
- draft: Draft (绘制) 模块
- arch: Arch (建筑) 模块
- mesh: Mesh (网格) 模块
- boolean: 布尔运算
- export: 导出功能
- info: 信息查询

Author: MiniMax Agent
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

try:
    from .formatter import get_formatter, OutputFormatter
    from .freecad_integration import get_wrapper, check_freecad, FreeCADWrapper
except ImportError:
    # 支持直接运行
    from freecad_cli.formatter import get_formatter, OutputFormatter
    from freecad_cli.freecad_integration import get_wrapper, check_freecad, FreeCADWrapper


# ============================================================================
# 全局选项
# ============================================================================

@click.group()
@click.option('--format', '-f',
              type=click.Choice(['json', 'yaml', 'text', 'table']),
              default='json',
              help='输出格式 (默认: json)')
@click.option('--pretty/--no-pretty',
              default=True,
              help='美化 JSON 输出')
@click.option('--headless/--gui',
              default=True,
              help='无头模式或 GUI 模式')
@click.option('--verbose/-v',
              is_flag=True,
              help='详细输出')
@click.pass_context
def cli(ctx, format, pretty, headless, verbose):
    """
    FreeCAD CLI - FreeCAD 命令行接口

    提供对 FreeCAD 所有功能的命令行访问，支持 AI 系统调用。

    示例:
        freecad-cli part create --name MyBox --type Box --params '{"length": 10}'
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
    """格式化并输出结果"""
    formatter: OutputFormatter = ctx.obj['FORMATTER']
    click.echo(formatter.format(result, status=status, message=message))


def output_error(ctx, message: str, details: Any = None):
    """输出错误信息"""
    formatter: OutputFormatter = ctx.obj['FORMATTER']
    click.echo(formatter.error(message, details), err=True)
    sys.exit(1)


# ============================================================================
# 文档命令组
# ============================================================================

@cli.group('document')
def document_group():
    """文档操作命令"""
    pass


@document_group.command('create')
@click.option('--name', '-n', default='Unnamed', help='文档名称')
@click.pass_context
def document_create(ctx, name):
    """创建新文档"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    result = wrapper.initialize()
    output_result(ctx, result, f"文档 '{name}' 创建成功")


@document_group.command('list')
@click.pass_context
def document_list(ctx):
    """列出所有对象"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    objects = wrapper.list_objects()
    output_result(ctx, objects, f"共 {len(objects)} 个对象")


@document_group.command('info')
@click.pass_context
def document_info(ctx):
    """显示文档信息"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    init_result = wrapper.initialize()

    if not init_result.get('success'):
        output_error(ctx, "无法初始化 FreeCAD", init_result)

    doc = wrapper.get_document()
    info = {
        "name": doc.Name if doc else None,
        "objects_count": len(doc.Objects) if doc else 0,
        "available": check_freecad(),
        "headless": ctx.obj['HEADLESS']
    }
    output_result(ctx, info)


# ============================================================================
# Part (零件) 命令组
# ============================================================================

@cli.group('part')
def part_group():
    """Part (零件) 模块 - 创建基本几何体"""
    pass


@part_group.command('create')
@click.option('--name', '-n', required=True, help='对象名称')
@click.option('--type', '-t',
              type=click.Choice(['Box', 'Cylinder', 'Sphere', 'Cone', 'Torus', 'Ellipsoid']),
              default='Box',
              help='几何体类型')
@click.option('--params', '-p',
              default='{}',
              help='几何参数 (JSON 格式)')
@click.pass_context
def part_create(ctx, name, type, params):
    """创建 Part 几何体"""
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        output_error(ctx, "参数必须是有效的 JSON 格式")

    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_part(name, type, params_dict)

    if result.get('success'):
        output_result(ctx, result, f"Part '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@part_group.command('list')
@click.option('--type-filter', '-f', help='按类型过滤')
@click.pass_context
def part_list(ctx, type_filter):
    """列出所有 Part 对象"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()

    filter_str = "Part::" if type_filter else None
    objects = wrapper.list_objects(filter_str)

    output_result(ctx, objects, f"共 {len(objects)} 个 Part 对象")


@part_group.command('info')
@click.option('--name', '-n', required=True, help='对象名称')
@click.pass_context
def part_info(ctx, name):
    """获取 Part 对象信息"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.get_object_info(name)
    output_result(ctx, result)


# ============================================================================
# Sketch (草图) 命令组
# ============================================================================

@cli.group('sketch')
def sketch_group():
    """Sketcher (草图) 模块 - 2D 草图绘制"""
    pass


@sketch_group.command('create')
@click.option('--name', '-n', required=True, help='草图名称')
@click.option('--plane', '-p',
              type=click.Choice(['XY', 'XZ', 'YZ']),
              default='XY',
              help='草图平面')
@click.pass_context
def sketch_create(ctx, name, plane):
    """创建新草图"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_sketch(name, plane)

    if result.get('success'):
        output_result(ctx, result, f"草图 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@sketch_group.command('add-line')
@click.option('--sketch', '-s', required=True, help='草图名称')
@click.option('--x1', type=float, default=0.0, help='起点 X 坐标')
@click.option('--y1', type=float, default=0.0, help='起点 Y 坐标')
@click.option('--x2', type=float, default=10.0, help='终点 X 坐标')
@click.option('--y2', type=float, default=10.0, help='终点 Y 坐标')
@click.pass_context
def sketch_add_line(ctx, sketch, x1, y1, x2, y2):
    """向草图添加直线"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.add_sketch_geometry(sketch, "Line", {
        "x1": x1, "y1": y1, "x2": x2, "y2": y2
    })

    if result.get('success'):
        output_result(ctx, result, "直线添加成功")
    else:
        output_error(ctx, result.get('error', '添加失败'), result)


@sketch_group.command('add-circle')
@click.option('--sketch', '-s', required=True, help='草图名称')
@click.option('--cx', type=float, default=0.0, help='圆心 X 坐标')
@click.option('--cy', type=float, default=0.0, help='圆心 Y 坐标')
@click.option('--radius', '-r', type=float, default=5.0, help='半径')
@click.pass_context
def sketch_add_circle(ctx, sketch, cx, cy, radius):
    """向草图添加圆"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.add_sketch_geometry(sketch, "Circle", {
        "cx": cx, "cy": cy, "radius": radius
    })

    if result.get('success'):
        output_result(ctx, result, "圆添加成功")
    else:
        output_error(ctx, result.get('error', '添加失败'), result)


@sketch_group.command('list')
@click.pass_context
def sketch_list(ctx):
    """列出所有草图"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    objects = wrapper.list_objects("Sketcher")
    output_result(ctx, objects, f"共 {len(objects)} 个草图")


# ============================================================================
# Draft (绘制) 命令组
# ============================================================================

@cli.group('draft')
def draft_group():
    """Draft (绘制) 模块 - 2D 绘制和注释"""
    pass


@draft_group.command('line')
@click.option('--name', '-n', required=True, help='直线名称')
@click.option('--x1', type=float, default=0.0, help='起点 X')
@click.option('--y1', type=float, default=0.0, help='起点 Y')
@click.option('--z1', type=float, default=0.0, help='起点 Z')
@click.option('--x2', type=float, default=10.0, help='终点 X')
@click.option('--y2', type=float, default=10.0, help='终点 Y')
@click.option('--z2', type=float, default=0.0, help='终点 Z')
@click.pass_context
def draft_line(ctx, name, x1, y1, z1, x2, y2, z2):
    """创建直线"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_draft_object(name, "Line", {
        "x1": x1, "y1": y1, "z1": z1,
        "x2": x2, "y2": y2, "z2": z2
    })

    if result.get('success'):
        output_result(ctx, result, f"直线 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@draft_group.command('circle')
@click.option('--name', '-n', required=True, help='圆名称')
@click.option('--radius', '-r', type=float, default=10.0, help='半径')
@click.option('--face/--wire', default=False, help='是否创建面')
@click.pass_context
def draft_circle(ctx, name, radius, face):
    """创建圆"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_draft_object(name, "Circle", {
        "radius": radius,
        "face": face
    })

    if result.get('success'):
        output_result(ctx, result, f"圆 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@draft_group.command('rectangle')
@click.option('--name', '-n', required=True, help='矩形名称')
@click.option('--length', '-l', type=float, default=10.0, help='长度')
@click.option('--height', '-h', type=float, default=5.0, help='高度')
@click.option('--face/--wire', default=False, help='是否创建面')
@click.pass_context
def draft_rectangle(ctx, name, length, height, face):
    """创建矩形"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_draft_object(name, "Rectangle", {
        "length": length,
        "height": height,
        "face": face
    })

    if result.get('success'):
        output_result(ctx, result, f"矩形 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@draft_group.command('polygon')
@click.option('--name', '-n', required=True, help='多边形名称')
@click.option('--sides', '-s', type=int, default=6, help='边数')
@click.option('--radius', '-r', type=float, default=10.0, help='外接圆半径')
@click.pass_context
def draft_polygon(ctx, name, sides, radius):
    """创建正多边形"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_draft_object(name, "Polygon", {
        "n_sides": sides,
        "radius": radius
    })

    if result.get('success'):
        output_result(ctx, result, f"多边形 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


# ============================================================================
# Arch (建筑) 命令组
# ============================================================================

@cli.group('arch')
def arch_group():
    """Arch (建筑) 模块 - BIM 和建筑建模"""
    pass


@arch_group.command('wall')
@click.option('--name', '-n', required=True, help='墙体名称')
@click.option('--length', '-l', type=float, default=100.0, help='长度 (mm)')
@click.option('--width', '-w', type=float, default=20.0, help='宽度 (mm)')
@click.option('--height', '-h', type=float, default=300.0, help='高度 (mm)')
@click.pass_context
def arch_wall(ctx, name, length, width, height):
    """创建墙体"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_arch_object(name, "Wall", {
        "length": length,
        "width": width,
        "height": height
    })

    if result.get('success'):
        output_result(ctx, result, f"墙体 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@arch_group.command('structure')
@click.option('--name', '-n', required=True, help='结构名称')
@click.option('--length', '-l', type=float, default=100.0, help='长度')
@click.option('--width', '-w', type=float, default=100.0, help='宽度')
@click.option('--height', '-h', type=float, default=200.0, help='高度')
@click.pass_context
def arch_structure(ctx, name, length, width, height):
    """创建结构"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_arch_object(name, "Structure", {
        "length": length,
        "width": width,
        "height": height
    })

    if result.get('success'):
        output_result(ctx, result, f"结构 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@arch_group.command('window')
@click.option('--name', '-n', required=True, help='窗户名称')
@click.option('--width', '-w', type=float, default=100.0, help='宽度')
@click.option('--height', '-h', type=float, default=150.0, help='高度')
@click.pass_context
def arch_window(ctx, name, width, height):
    """创建窗户"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_arch_object(name, "Window", {
        "width": width,
        "height": height
    })

    if result.get('success'):
        output_result(ctx, result, f"窗户 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


# ============================================================================
# 布尔运算命令组
# ============================================================================

@cli.group('boolean')
def boolean_group():
    """布尔运算命令"""
    pass


@boolean_group.command('fuse')
@click.option('--name', '-n', required=True, help='结果对象名称')
@click.option('--object1', '-o1', required=True, help='第一个对象')
@click.option('--object2', '-o2', required=True, help='第二个对象')
@click.pass_context
def boolean_fuse(ctx, name, object1, object2):
    """并集运算 (Fuse)"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.boolean_operation(name, "Fuse", object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"并集 '{name}' 计算成功")
    else:
        output_error(ctx, result.get('error', '运算失败'), result)


@boolean_group.command('cut')
@click.option('--name', '-n', required=True, help='结果对象名称')
@click.option('--object1', '-o1', required=True, help='被切对象')
@click.option('--object2', '-o2', required=True, help='切削对象')
@click.pass_context
def boolean_cut(ctx, name, object1, object2):
    """差集运算 (Cut)"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.boolean_operation(name, "Cut", object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"差集 '{name}' 计算成功")
    else:
        output_error(ctx, result.get('error', '运算失败'), result)


@boolean_group.command('common')
@click.option('--name', '-n', required=True, help='结果对象名称')
@click.option('--object1', '-o1', required=True, help='第一个对象')
@click.option('--object2', '-o2', required=True, help='第二个对象')
@click.pass_context
def boolean_common(ctx, name, object1, object2):
    """交集运算 (Common)"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.boolean_operation(name, "Common", object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"交集 '{name}' 计算成功")
    else:
        output_error(ctx, result.get('error', '运算失败'), result)


@boolean_group.command('section')
@click.option('--name', '-n', required=True, help='结果对象名称')
@click.option('--object1', '-o1', required=True, help='第一个对象')
@click.option('--object2', '-o2', required=True, help='第二个对象')
@click.pass_context
def boolean_section(ctx, name, object1, object2):
    """截面运算 (Section)"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.boolean_operation(name, "Section", object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"截面 '{name}' 计算成功")
    else:
        output_error(ctx, result.get('error', '运算失败'), result)


# ============================================================================
# 导出命令组
# ============================================================================

@cli.group('export')
def export_group():
    """导出命令"""
    pass


@export_group.command('step')
@click.option('--filepath', '-f', required=True, help='导出文件路径')
@click.pass_context
def export_step(ctx, filepath):
    """导出为 STEP 格式"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.export_document(filepath, "STEP")

    if result.get('success'):
        output_result(ctx, result, f"已导出到 {filepath}")
    else:
        output_error(ctx, result.get('error', '导出失败'), result)


@export_group.command('stl')
@click.option('--filepath', '-f', required=True, help='导出文件路径')
@click.pass_context
def export_stl(ctx, filepath):
    """导出为 STL 格式"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.export_document(filepath, "STL")

    if result.get('success'):
        output_result(ctx, result, f"已导出到 {filepath}")
    else:
        output_error(ctx, result.get('error', '导出失败'), result)


@export_group.command('obj')
@click.option('--filepath', '-f', required=True, help='导出文件路径')
@click.pass_context
def export_obj(ctx, filepath):
    """导出为 OBJ 格式"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.export_document(filepath, "OBJ")

    if result.get('success'):
        output_result(ctx, result, f"已导出到 {filepath}")
    else:
        output_error(ctx, result.get('error', '导出失败'), result)


@export_group.command('iges')
@click.option('--filepath', '-f', required=True, help='导出文件路径')
@click.pass_context
def export_iges(ctx, filepath):
    """导出为 IGES 格式"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.export_document(filepath, "IGES")

    if result.get('success'):
        output_result(ctx, result, f"已导出到 {filepath}")
    else:
        output_error(ctx, result.get('error', '导出失败'), result)


# ============================================================================
# 信息查询命令
# ============================================================================

@cli.group('info')
def info_group():
    """信息查询命令"""
    pass


@info_group.command('object')
@click.option('--name', '-n', required=True, help='对象名称')
@click.pass_context
def info_object(ctx, name):
    """获取对象详细信息"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.get_object_info(name)
    output_result(ctx, result)


@info_group.command('status')
@click.pass_context
def info_status(ctx):
    """显示 FreeCAD 状态"""
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
    """列出可用模块"""
    modules = {
        "core": {
            "name": "Part",
            "description": "零件和实体建模",
            "available": True
        },
        "sketcher": {
            "name": "Sketcher",
            "description": "2D 草图约束求解器",
            "available": True
        },
        "draft": {
            "name": "Draft",
            "description": "2D 绘制和注释",
            "available": True
        },
        "arch": {
            "name": "Arch",
            "description": "建筑信息模型 (BIM)",
            "available": True
        },
        "mesh": {
            "name": "Mesh",
            "description": "网格处理",
            "available": True
        },
        "surface": {
            "name": "Surface",
            "description": "曲面建模",
            "available": True
        },
        "design": {
            "name": "PartDesign",
            "description": "零件设计工作台",
            "available": True
        }
    }
    output_result(ctx, modules)


# ============================================================================
# 对象操作命令
# ============================================================================

@cli.group('object')
def object_group():
    """对象操作命令"""
    pass


@object_group.command('delete')
@click.option('--name', '-n', required=True, help='对象名称')
@click.pass_context
def object_delete(ctx, name):
    """删除对象"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.delete_object(name)

    if result.get('success'):
        output_result(ctx, result, f"对象 '{name}' 已删除")
    else:
        output_error(ctx, result.get('error', '删除失败'), result)


@object_group.command('list')
@click.option('--type', '-t', help='类型过滤器')
@click.pass_context
def object_list(ctx, type):
    """列出所有对象"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()

    filter_str = type if type else None
    objects = wrapper.list_objects(filter_str)

    output_result(ctx, objects, f"共 {len(objects)} 个对象")


# ============================================================================
# Mesh (网格) 命令组
# ============================================================================

@cli.group('mesh')
def mesh_group():
    """Mesh (网格) 模块 - 网格处理和操作"""
    pass


@mesh_group.command('create')
@click.option('--name', '-n', required=True, help='对象名称')
@click.option('--type', '-t',
              type=click.Choice(['RegularMesh', 'Triangle', 'Grid']),
              default='RegularMesh',
              help='网格类型')
@click.option('--params', '-p',
              default='{}',
              help='网格参数 (JSON 格式)')
@click.pass_context
def mesh_create(ctx, name, type, params):
    """创建 Mesh 网格对象"""
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        output_error(ctx, "参数必须是有效的 JSON 格式")

    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_mesh_object(name, type, params_dict)

    if result.get('success'):
        output_result(ctx, result, f"Mesh '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@mesh_group.command('from-shape')
@click.option('--name', '-n', required=True, help='网格对象名称')
@click.option('--source', '-s', required=True, help='源形状对象名称')
@click.option('--deflection', '-d', type=float, default=0.1, help='网格精度')
@click.pass_context
def mesh_from_shape(ctx, name, source, deflection):
    """从形状创建网格"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.mesh_from_shape(name, source, deflection)

    if result.get('success'):
        output_result(ctx, result, f"网格 '{name}' 从形状创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@mesh_group.command('boolean')
@click.option('--name', '-n', required=True, help='结果对象名称')
@click.option('--operation', '-o',
              type=click.Choice(['Union', 'Intersection', 'Difference']),
              required=True,
              help='布尔运算类型')
@click.option('--object1', '-o1', required=True, help='第一个网格对象')
@click.option('--object2', '-o2', required=True, help='第二个网格对象')
@click.pass_context
def mesh_boolean(ctx, name, operation, object1, object2):
    """网格布尔运算"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.mesh_boolean(name, operation, object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"网格布尔运算 '{name}' 成功")
    else:
        output_error(ctx, result.get('error', '运算失败'), result)


@mesh_group.command('list')
@click.pass_context
def mesh_list(ctx):
    """列出所有 Mesh 对象"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    objects = wrapper.list_objects("Mesh")
    output_result(ctx, objects, f"共 {len(objects)} 个 Mesh 对象")


# ============================================================================
# Surface (曲面) 命令组
# ============================================================================

@cli.group('surface')
def surface_group():
    """Surface (曲面) 模块 - 曲面建模"""
    pass


@surface_group.command('create')
@click.option('--name', '-n', required=True, help='曲面对象名称')
@click.option('--type', '-t',
              type=click.Choice(['Fill', 'Sweep', 'Loft', 'Bezier']),
              default='Fill',
              help='曲面类型')
@click.option('--params', '-p',
              default='{}',
              help='曲面参数 (JSON 格式)')
@click.pass_context
def surface_create(ctx, name, type, params):
    """创建 Surface 曲面"""
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        output_error(ctx, "参数必须是有效的 JSON 格式")

    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_surface(name, type, params_dict)

    if result.get('success'):
        output_result(ctx, result, f"曲面 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@surface_group.command('from-edges')
@click.option('--name', '-n', required=True, help='曲面对象名称')
@click.option('--sketch', '-s', required=True, help='草图名称')
@click.pass_context
def surface_from_edges(ctx, name, sketch):
    """从草图边界创建曲面"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.surface_from_edges(name, sketch)

    if result.get('success'):
        output_result(ctx, result, f"曲面 '{name}' 从边界创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


# ============================================================================
# PartDesign (零件设计) 命令组
# ============================================================================

@cli.group('partdesign')
def partdesign_group():
    """PartDesign (零件设计) 模块 - 零件设计和特征"""
    pass


@partdesign_group.command('create-body')
@click.option('--name', '-n', required=True, help='Body 名称')
@click.pass_context
def partdesign_create_body(ctx, name):
    """创建 PartDesign Body"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_partdesign_body(name)

    if result.get('success'):
        output_result(ctx, result, f"Body '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@partdesign_group.command('pad')
@click.option('--name', '-n', required=True, help='Pad 名称')
@click.option('--body', '-b', required=True, help='Body 名称')
@click.option('--sketch', '-s', required=True, help='草图名称')
@click.option('--length', '-l', type=float, default=10.0, help='拉伸长度')
@click.option('--direction', '-d',
              type=click.Choice(['Normal', 'Reversed', 'Double']),
              default='Normal',
              help='拉伸方向')
@click.pass_context
def partdesign_pad(ctx, name, body, sketch, length, direction):
    """创建 Pad 拉伸特征"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_pad(name, body, sketch, length, direction)

    if result.get('success'):
        output_result(ctx, result, f"Pad '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@partdesign_group.command('pocket')
@click.option('--name', '-n', required=True, help='Pocket 名称')
@click.option('--body', '-b', required=True, help='Body 名称')
@click.option('--sketch', '-s', required=True, help='草图名称')
@click.option('--length', '-l', type=float, default=10.0, help='切除深度')
@click.option('--type', '-t',
              type=click.Choice(['Through', 'UpToFirst', 'UpToFace']),
              default='Through',
              help='切除类型')
@click.pass_context
def partdesign_pocket(ctx, name, body, sketch, length, type):
    """创建 Pocket 切除特征"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_pocket(name, body, sketch, length, type)

    if result.get('success'):
        output_result(ctx, result, f"Pocket '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@partdesign_group.command('hole')
@click.option('--name', '-n', required=True, help='孔名称')
@click.option('--body', '-b', required=True, help='Body 名称')
@click.option('--diameter', '-d', type=float, default=5.0, help='孔直径')
@click.option('--depth', '-l', type=float, default=10.0, help='孔深度')
@click.option('--position', '-p',
              help='孔位置 (x,y,z)',
              default=None)
@click.pass_context
def partdesign_hole(ctx, name, body, diameter, depth, position):
    """创建孔特征"""
    pos = None
    if position:
        try:
            pos = tuple(map(float, position.split(',')))
        except ValueError:
            output_error(ctx, "位置必须是 x,y,z 格式")

    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_hole(name, body, diameter, depth, pos)

    if result.get('success'):
        output_result(ctx, result, f"孔 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@partdesign_group.command('revolution')
@click.option('--name', '-n', required=True, help='旋转体名称')
@click.option('--body', '-b', required=True, help='Body 名称')
@click.option('--sketch', '-s', required=True, help='草图名称')
@click.option('--angle', '-a', type=float, default=360.0, help='旋转角度')
@click.pass_context
def partdesign_revolution(ctx, name, body, sketch, angle):
    """创建旋转体特征"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_revolution(name, body, sketch, angle)

    if result.get('success'):
        output_result(ctx, result, f"旋转体 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@partdesign_group.command('groove')
@click.option('--name', '-n', required=True, help='Groove 名称')
@click.option('--body', '-b', required=True, help='Body 名称')
@click.option('--angle', '-a', type=float, default=360.0, help='旋转角度')
@click.option('--radius', '-r', type=float, default=5.0, help='旋转半径')
@click.pass_context
def partdesign_groove(ctx, name, body, angle, radius):
    """创建旋转切除特征"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_groove(name, body, angle, radius)

    if result.get('success'):
        output_result(ctx, result, f"Groove '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@partdesign_group.command('fillet')
@click.option('--name', '-n', required=True, help='圆角名称')
@click.option('--body', '-b', required=True, help='Body 名称')
@click.option('--radius', '-r', type=float, default=2.0, help='圆角半径')
@click.pass_context
def partdesign_fillet(ctx, name, body, radius):
    """创建圆角特征"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_fillet(name, body, radius)

    if result.get('success'):
        output_result(ctx, result, f"圆角 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@partdesign_group.command('chamfer')
@click.option('--name', '-n', required=True, help='倒角名称')
@click.option('--body', '-b', required=True, help='Body 名称')
@click.option('--size', '-s', type=float, default=1.0, help='倒角大小')
@click.pass_context
def partdesign_chamfer(ctx, name, body, size):
    """创建倒角特征"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.create_chamfer(name, body, size)

    if result.get('success'):
        output_result(ctx, result, f"倒角 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


# ============================================================================
# TechDraw (工程图) 命令组
# ============================================================================

@cli.group('techdraw')
def techdraw_group():
    """TechDraw (工程图) 模块 - 技术图纸和标注"""
    pass


@techdraw_group.command('create-page')
@click.option('--name', '-n', required=True, help='页面名称')
@click.option('--template', '-t', default='A4_Landscape',
              help='图纸模板 (A4_Landscape, A4_Portrait, A3_Landscape)')
@click.pass_context
def techdraw_create_page(ctx, name, template):
    """创建 TechDraw 页面"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.techdraw_create_page(name, template)

    if result.get('success'):
        output_result(ctx, result, f"页面 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@techdraw_group.command('add-view')
@click.option('--page', '-p', required=True, help='页面名称')
@click.option('--source', '-s', required=True, help='源对象名称')
@click.option('--projection', '--proj', default='FirstAngle',
              type=click.Choice(['FirstAngle', 'ThirdAngle']),
              help='投影类型')
@click.pass_context
def techdraw_add_view(ctx, page, source, projection):
    """添加工程视图"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.techdraw_add_view(page, source, projection)

    if result.get('success'):
        output_result(ctx, result, f"视图创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@techdraw_group.command('add-dimension')
@click.option('--view', '-v', required=True, help='视图名称')
@click.option('--type', '-t',
              type=click.Choice(['Horizontal', 'Vertical', 'Radius', 'Diameter', 'Angle']),
              default='Horizontal',
              help='尺寸类型')
@click.pass_context
def techdraw_add_dimension(ctx, view, type):
    """添加尺寸标注"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.techdraw_add_dimension(view, type, [])

    if result.get('success'):
        output_result(ctx, result, f"尺寸标注创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@techdraw_group.command('export')
@click.option('--page', '-p', required=True, help='页面名称')
@click.option('--filepath', '-f', required=True, help='导出文件路径')
@click.option('--format', '-fmt',
              type=click.Choice(['PDF', 'SVG', 'DXF']),
              default='PDF',
              help='导出格式')
@click.pass_context
def techdraw_export(ctx, page, filepath, format):
    """导出工程图"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.techdraw_export(page, filepath, format)

    if result.get('success'):
        output_result(ctx, result, f"已导出到 {filepath}")
    else:
        output_error(ctx, result.get('error', '导出失败'), result)


# ============================================================================
# Spreadsheet (电子表格) 命令组
# ============================================================================

@cli.group('spreadsheet')
def spreadsheet_group():
    """Spreadsheet (电子表格) 模块 - 参数化表格"""
    pass


@spreadsheet_group.command('create')
@click.option('--name', '-n', required=True, help='表格名称')
@click.pass_context
def spreadsheet_create(ctx, name):
    """创建电子表格"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.spreadsheet_create(name)

    if result.get('success'):
        output_result(ctx, result, f"电子表格 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@spreadsheet_group.command('set-cell')
@click.option('--sheet', '-s', required=True, help='表格名称')
@click.option('--cell', '-c', required=True, help='单元格 (如 A1)')
@click.option('--value', '-v', required=True, help='单元格值')
@click.pass_context
def spreadsheet_set_cell(ctx, sheet, cell, value):
    """设置单元格值"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.spreadsheet_set_cell(sheet, cell, value)

    if result.get('success'):
        output_result(ctx, result, f"单元格 {cell} 设置成功")
    else:
        output_error(ctx, result.get('error', '设置失败'), result)


@spreadsheet_group.command('set-formula')
@click.option('--sheet', '-s', required=True, help='表格名称')
@click.option('--cell', '-c', required=True, help='单元格')
@click.option('--formula', '-f', required=True, help='公式 (如 =A1*2)')
@click.pass_context
def spreadsheet_set_formula(ctx, sheet, cell, formula):
    """设置单元格公式"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.spreadsheet_set_formula(sheet, cell, formula)

    if result.get('success'):
        output_result(ctx, result, f"公式设置成功")
    else:
        output_error(ctx, result.get('error', '设置失败'), result)


@spreadsheet_group.command('link')
@click.option('--sheet', '-s', required=True, help='表格名称')
@click.option('--object', '-o', required=True, help='对象名称')
@click.option('--property', '-p', required=True, help='属性名称')
@click.option('--cell', '-c', required=True, help='单元格')
@click.pass_context
def spreadsheet_link(ctx, sheet, object, property, cell):
    """链接电子表格到对象属性"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.spreadsheet_link(sheet, object, property, cell)

    if result.get('success'):
        output_result(ctx, result, f"链接创建成功")
    else:
        output_error(ctx, result.get('error', '链接失败'), result)


# ============================================================================
# Assembly (装配) 命令组
# ============================================================================

@cli.group('assembly')
def assembly_group():
    """Assembly (装配) 模块 - 装配管理"""
    pass


@assembly_group.command('create')
@click.option('--name', '-n', required=True, help='装配名称')
@click.pass_context
def assembly_create(ctx, name):
    """创建装配"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.assembly_create(name)

    if result.get('success'):
        output_result(ctx, result, f"装配 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@assembly_group.command('add-part')
@click.option('--assembly', '-a', required=True, help='装配名称')
@click.option('--part', '-p', required=True, help='零件名称')
@click.option('--placement', '-pl', default='[0, 0, 0]', help='位置 [x, y, z]')
@click.pass_context
def assembly_add_part(ctx, assembly, part, placement):
    """向装配添加零件"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.assembly_add_part(assembly, part, placement)

    if result.get('success'):
        output_result(ctx, result, f"零件 '{part}' 添加到装配成功")
    else:
        output_error(ctx, result.get('error', '添加失败'), result)


@assembly_group.command('add-constraint')
@click.option('--assembly', '-a', required=True, help='装配名称')
@click.option('--type', '-t', required=True,
              type=click.Choice(['Coincident', 'Distance', 'Angle']),
              help='约束类型')
@click.option('--object1', '-o1', required=True, help='第一个对象')
@click.option('--object2', '-o2', required=True, help='第二个对象')
@click.pass_context
def assembly_add_constraint(ctx, assembly, type, object1, object2):
    """添加装配约束"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.assembly_add_constraint(assembly, type, object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"约束添加成功")
    else:
        output_error(ctx, result.get('error', '添加失败'), result)


# ============================================================================
# Path (CAM 加工) 命令组
# ============================================================================

@cli.group('path')
def path_group():
    """Path (CAM) 模块 - CNC 加工路径"""
    pass


@path_group.command('create-job')
@click.option('--name', '-n', required=True, help='任务名称')
@click.option('--base', '-b', required=True, help='基础对象名称')
@click.pass_context
def path_create_job(ctx, name, base):
    """创建加工任务"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.path_create_job(name, base)

    if result.get('success'):
        output_result(ctx, result, f"加工任务 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@path_group.command('add-operation')
@click.option('--job', '-j', required=True, help='任务名称')
@click.option('--type', '-t',
              type=click.Choice(['Drill', 'Profile', 'Pocket', 'Slot']),
              default='Drill',
              help='操作类型')
@click.pass_context
def path_add_operation(ctx, job, type):
    """添加加工操作"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.path_add_operation(job, type)

    if result.get('success'):
        output_result(ctx, result, f"操作 '{type}' 添加成功")
    else:
        output_error(ctx, result.get('error', '添加失败'), result)


@path_group.command('export-gcode')
@click.option('--job', '-j', required=True, help='任务名称')
@click.option('--filepath', '-f', required=True, help='导出文件路径')
@click.option('--post', '-p', default='linuxcnc', help='后处理器')
@click.pass_context
def path_export_gcode(ctx, job, filepath, post):
    """导出 G-code"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.path_export_gcode(job, filepath, post)

    if result.get('success'):
        output_result(ctx, result, f"G-code 已导出到 {filepath}")
    else:
        output_error(ctx, result.get('error', '导出失败'), result)


# ============================================================================
# FEM (有限元分析) 命令组
# ============================================================================

@cli.group('fem')
def fem_group():
    """FEM (有限元分析) 模块 - 工程分析"""
    pass


@fem_group.command('create-analysis')
@click.option('--name', '-n', required=True, help='分析名称')
@click.option('--type', '-t',
              type=click.Choice(['static', 'modal', 'thermomechanical']),
              default='static',
              help='分析类型')
@click.pass_context
def fem_create_analysis(ctx, name, type):
    """创建有限元分析"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.fem_create_analysis(name, type)

    if result.get('success'):
        output_result(ctx, result, f"分析 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@fem_group.command('add-material')
@click.option('--analysis', '-a', required=True, help='分析名称')
@click.option('--material', '-m',
              type=click.Choice(['Steel', 'Aluminum', 'Copper']),
              default='Steel',
              help='材料')
@click.pass_context
def fem_add_material(ctx, analysis, material):
    """添加材料"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.fem_add_material(analysis, material)

    if result.get('success'):
        output_result(ctx, result, f"材料 '{material}' 添加成功")
    else:
        output_error(ctx, result.get('error', '添加失败'), result)


@fem_group.command('add-bc')
@click.option('--analysis', '-a', required=True, help='分析名称')
@click.option('--type', '-t',
              type=click.Choice(['Fixed', 'Force', 'Pressure']),
              required=True,
              help='边界条件类型')
@click.option('--object', '-o', required=True, help='对象名称')
@click.pass_context
def fem_add_bc(ctx, analysis, type, object):
    """添加边界条件"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.fem_add_boundary_condition(analysis, type, object, {})

    if result.get('success'):
        output_result(ctx, result, f"边界条件添加成功")
    else:
        output_error(ctx, result.get('error', '添加失败'), result)


@fem_group.command('run')
@click.option('--analysis', '-a', required=True, help='分析名称')
@click.pass_context
def fem_run(ctx, analysis):
    """运行有限元分析"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.fem_run_analysis(analysis)

    if result.get('success'):
        output_result(ctx, result, f"分析 '{analysis}' 运行完成")
    else:
        output_error(ctx, result.get('error', '运行失败'), result)


# ============================================================================
# Image (图像) 命令组
# ============================================================================

@cli.group('image')
def image_group():
    """Image (图像) 模块 - 图像处理"""
    pass


@image_group.command('import')
@click.option('--name', '-n', required=True, help='图像名称')
@click.option('--filepath', '-f', required=True, help='图像文件路径')
@click.pass_context
def image_import(ctx, name, filepath):
    """导入图像"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.image_import(name, filepath)

    if result.get('success'):
        output_result(ctx, result, f"图像 '{name}' 导入成功")
    else:
        output_error(ctx, result.get('error', '导入失败'), result)


@image_group.command('scale')
@click.option('--name', '-n', required=True, help='图像名称')
@click.option('--x', '-x', type=float, default=1.0, help='X 方向缩放')
@click.option('--y', '-y', type=float, default=1.0, help='Y 方向缩放')
@click.pass_context
def image_scale(ctx, name, x, y):
    """缩放图像"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.image_scale(name, x, y)

    if result.get('success'):
        output_result(ctx, result, f"图像 '{name}' 缩放成功")
    else:
        output_error(ctx, result.get('error', '缩放失败'), result)


# ============================================================================
# Material (材料) 命令组
# ============================================================================

@cli.group('material')
def material_group():
    """Material (材料) 模块 - 材料管理"""
    pass


@material_group.command('create')
@click.option('--name', '-n', required=True, help='材料名称')
@click.option('--density', '-d', type=float, help='密度 (kg/m³)')
@click.option('--youngs', '-y', type=float, help='杨氏模量 (MPa)')
@click.option('--poisson', '-p', type=float, help='泊松比')
@click.pass_context
def material_create(ctx, name, density, youngs, poisson):
    """创建材料"""
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
        output_result(ctx, result, f"材料 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@material_group.command('get-standard')
@click.option('--name', '-n', required=True, help='材料名称')
@click.pass_context
def material_get_standard(ctx, name):
    """获取标准材料"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.material_get_standard(name)
    output_result(ctx, result)


# ============================================================================
# Inspection (检测) 命令组
# ============================================================================

@cli.group('inspection')
def inspection_group():
    """Inspection (检测) 模块 - 检测和测量"""
    pass


@inspection_group.command('create-check')
@click.option('--name', '-n', required=True, help='检测名称')
@click.option('--object', '-o', required=True, help='检测对象')
@click.pass_context
def inspection_create_check(ctx, name, object):
    """创建检测"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.inspection_create_check(name, object)

    if result.get('success'):
        output_result(ctx, result, f"检测 '{name}' 创建成功")
    else:
        output_error(ctx, result.get('error', '创建失败'), result)


@inspection_group.command('measure-distance')
@click.option('--object1', '-o1', required=True, help='第一个对象')
@click.option('--object2', '-o2', required=True, help='第二个对象')
@click.pass_context
def inspection_measure_distance(ctx, object1, object2):
    """测量距离"""
    wrapper = get_wrapper(ctx.obj['HEADLESS'])
    wrapper.initialize()
    result = wrapper.inspection_measure_distance(object1, object2)

    if result.get('success'):
        output_result(ctx, result, f"距离测量结果")
    else:
        output_error(ctx, result.get('error', '测量失败'), result)


# ============================================================================
# 主入口
# ============================================================================

def main():
    """主入口点"""
    cli(obj={})


if __name__ == '__main__':
    main()
