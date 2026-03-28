# -*- coding: utf-8 -*-
"""
AI Integration Module - AI 集成模块
====================================

提供 AI 友好的接口，包括：
- 自然语言命令解析
- 命令历史记录
- 批量操作支持
- 自动补全生成
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CommandSpec:
    """命令规范类"""
    command: str
    description: str
    parameters: Dict[str, Dict[str, Any]]
    examples: List[str]
    category: str


class AICommandParser:
    """AI 命令解析器 - 将自然语言转换为 CLI 命令"""

    # 命令模板库
    COMMAND_TEMPLATES = {
        # Part 相关
        r"创建.*?(box|立方体)" : ("part", "create", {"type": "Box"}),
        r"创建.*?圆柱" : ("part", "create", {"type": "Cylinder"}),
        r"创建.*?球" : ("part", "create", {"type": "Sphere"}),
        r"创建.*?圆锥" : ("part", "create", {"type": "Cone"}),
        r"创建.*?圆环" : ("part", "create", {"type": "Torus"}),

        # Sketch 相关
        r"创建.*?草图" : ("sketch", "create", {}),
        r"添加.*?直线" : ("sketch", "add-line", {}),
        r"添加.*?圆" : ("sketch", "add-circle", {}),

        # Draft 相关
        r"绘制.*?线" : ("draft", "line", {}),
        r"绘制.*?圆" : ("draft", "circle", {}),
        r"绘制.*?矩形" : ("draft", "rectangle", {}),
        r"绘制.*?多边形" : ("draft", "polygon", {}),

        # Arch 相关
        r"创建.*?墙" : ("arch", "wall", {}),
        r"创建.*?结构" : ("arch", "structure", {}),
        r"创建.*?窗户" : ("arch", "window", {}),

        # Boolean 操作
        r"并集|合并" : ("boolean", "fuse", {}),
        r"差集|减去" : ("boolean", "cut", {}),
        r"交集|共同" : ("boolean", "common", {}),

        # Export
        r"导出.*?step" : ("export", "step", {}),
        r"导出.*?stl" : ("export", "stl", {}),
        r"导出.*?obj" : ("export", "obj", {}),

        # Info
        r"列出.*?对象" : ("object", "list", {}),
        r"删除.*?" : ("object", "delete", {}),
    }

    def __init__(self):
        self.command_history: List[Dict] = []

    def parse(self, natural_language: str) -> Dict[str, Any]:
        """
        将自然语言解析为结构化命令

        Args:
            natural_language: 自然语言输入

        Returns:
            解析后的命令字典
        """
        nl = natural_language.lower()

        for pattern, (group, cmd, default_params) in self.COMMAND_TEMPLATES.items():
            if re.search(pattern, nl):
                result = {
                    "success": True,
                    "command_group": group,
                    "command": cmd,
                    "parameters": default_params.copy(),
                    "raw_input": natural_language
                }

                # 提取参数
                self._extract_parameters(nl, result["parameters"])

                # 添加到历史
                self.command_history.append(result)

                return result

        return {
            "success": False,
            "error": "无法解析命令",
            "raw_input": natural_language,
            "suggestion": "请使用明确的命令，如: '创建盒子' 或 '绘制圆形'"
        }

    def _extract_parameters(self, text: str, params: Dict):
        """从文本中提取参数"""
        # 提取尺寸参数
        size_patterns = [
            (r"长\s*(\d+\.?\d*)", "length"),
            (r"宽\s*(\d+\.?\d*)", "width"),
            (r"高\s*(\d+\.?\d*)", "height"),
            (r"半径\s*(\d+\.?\d*)", "radius"),
            (r"尺寸\s*(\d+\.?\d*)", "size"),
        ]

        for pattern, param_name in size_patterns:
            match = re.search(pattern, text)
            if match:
                params[param_name] = float(match.group(1))

        # 提取名称
        name_patterns = [
            r"名[称叫]([a-zA-Z0-9_]+)",
            r"叫\s*([a-zA-Z0-9_]+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                params["name"] = match.group(1)
                break

        # 提取边数
        sides_match = re.search(r"(\d+)\s*[边角]", text)
        if sides_match:
            params["sides"] = int(sides_match.group(1))


class BatchProcessor:
    """批量命令处理器"""

    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.results: List[Dict] = []

    def execute_batch(self, commands: List[Dict]) -> List[Dict]:
        """
        批量执行命令

        Args:
            commands: 命令列表

        Returns:
            执行结果列表
        """
        results = []

        for cmd in commands:
            group = cmd.get("command_group")
            action = cmd.get("command")
            params = cmd.get("parameters", {})

            try:
                if group == "part":
                    result = self.wrapper.create_part(
                        params.get("name", "Unnamed"),
                        params.get("type", "Box"),
                        params
                    )
                elif group == "sketch":
                    if action == "create":
                        result = self.wrapper.create_sketch(
                            params.get("name", "Sketch"),
                            params.get("plane", "XY")
                        )
                    elif action == "add-line":
                        result = self.wrapper.add_sketch_geometry(
                            params.get("sketch"), "Line", params
                        )
                    elif action == "add-circle":
                        result = self.wrapper.add_sketch_geometry(
                            params.get("sketch"), "Circle", params
                        )
                elif group == "draft":
                    result = self.wrapper.create_draft_object(
                        params.get("name", "Draft"),
                        action,
                        params
                    )
                elif group == "arch":
                    result = self.wrapper.create_arch_object(
                        params.get("name", "Arch"),
                        action,
                        params
                    )
                else:
                    result = {"success": False, "error": f"未知命令组: {group}"}

                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})

        self.results = results
        return results

    def get_summary(self) -> Dict[str, Any]:
        """获取批量执行摘要"""
        if not self.results:
            return {"total": 0, "success": 0, "failed": 0}

        success_count = sum(1 for r in self.results if r.get("success"))
        return {
            "total": len(self.results),
            "success": success_count,
            "failed": len(self.results) - success_count,
            "success_rate": success_count / len(self.results) * 100
        }


class CommandGenerator:
    """命令生成器 - 根据需求生成 CLI 命令"""

    @staticmethod
    def generate_part_command(name: str, shape: str, **kwargs) -> str:
        """生成 Part 命令"""
        params = json.dumps(kwargs, ensure_ascii=False)
        return f'freecad-cli part create --name "{name}" --type {shape} --params \'{params}\''

    @staticmethod
    def generate_sketch_command(name: str, plane: str = "XY") -> str:
        """生成 Sketch 命令"""
        return f'freecad-cli sketch create --name "{name}" --plane {plane}'

    @staticmethod
    def generate_draft_command(draft_type: str, name: str, **kwargs) -> str:
        """生成 Draft 命令"""
        parts = [f'freecad-cli draft {draft_type.lower()} --name "{name}"']
        for key, value in kwargs.items():
            parts.append(f"--{key} {value}")
        return " ".join(parts)

    @staticmethod
    def generate_boolean_command(operation: str, name: str,
                                 obj1: str, obj2: str) -> str:
        """生成布尔运算命令"""
        return f'freecad-cli boolean {operation.lower()} --name "{name}" --object1 {obj1} --object2 {obj2}'

    @staticmethod
    def generate_export_command(format_type: str, filepath: str) -> str:
        """生成导出命令"""
        return f'freecad-cli export {format_type.lower()} --filepath "{filepath}"'


def generate_workflow_commands(workflow: str) -> List[str]:
    """
    根据工作流描述生成命令列表

    Args:
        workflow: 工作流描述

    Returns:
        CLI 命令列表
    """
    commands = []

    # 解析工作流
    lines = workflow.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parser = AICommandParser()
        result = parser.parse(line)

        if result.get("success"):
            generator = CommandGenerator()

            if result["command_group"] == "part":
                cmd = generator.generate_part_command(
                    result["parameters"].get("name", "Part"),
                    result["parameters"].get("type", "Box"),
                    **result["parameters"]
                )
            elif result["command_group"] == "sketch":
                cmd = generator.generate_sketch_command(
                    result["parameters"].get("name", "Sketch"),
                    result["parameters"].get("plane", "XY")
                )
            elif result["command_group"] == "draft":
                cmd = generator.generate_draft_command(
                    result["command"],
                    result["parameters"].get("name", "Draft"),
                    **result["parameters"]
                )
            else:
                cmd = f"# {line} (未识别)"

            commands.append(cmd)

    return commands
