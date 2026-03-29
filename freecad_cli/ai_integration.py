# -*- coding: utf-8 -*-
"""
AI Integration Module
=====================

Provides AI-friendly interfaces including:
- Natural language command parsing
- Command history tracking
- Batch operation support
- Auto-completion generation
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CommandSpec:
    """Command specification class"""
    command: str
    description: str
    parameters: Dict[str, Dict[str, Any]]
    examples: List[str]
    category: str


class AICommandParser:
    """AI command parser - converts natural language to CLI commands"""

    # Command template library
    COMMAND_TEMPLATES = {
        # Part related
        r"创建.*?(box|立方体)|(make|create|add).*?(box|part)" : ("part", "create", {"type": "Box"}),
        r"创建.*?圆柱|(make|create|add).*?cylinder" : ("part", "create", {"type": "Cylinder"}),
        r"创建.*?球|(make|create|add).*?sphere" : ("part", "create", {"type": "Sphere"}),
        r"创建.*?圆锥|(make|create|add).*?cone" : ("part", "create", {"type": "Cone"}),
        r"创建.*?圆环|(make|create|add).*?torus" : ("part", "create", {"type": "Torus"}),
        r"创建.*?椭球|(make|create|add).*?ellipsoid" : ("part", "create", {"type": "Ellipsoid"}),

        # Sketch related
        r"创建.*?草图|(make|create|add).*?sketch" : ("sketch", "create", {}),
        r"添加.*?直线|add.*?line" : ("sketch", "add-line", {}),
        r"添加.*?圆|add.*?circle" : ("sketch", "add-circle", {}),

        # Draft related
        r"绘制.*?线|draw.*?line" : ("draft", "line", {}),
        r"绘制.*?圆|draw.*?circle" : ("draft", "circle", {}),
        r"绘制.*?矩形|draw.*?rectangle" : ("draft", "rectangle", {}),
        r"绘制.*?多边形|draw.*?polygon" : ("draft", "polygon", {}),

        # Arch related
        r"创建.*?墙|(make|create|add).*?wall" : ("arch", "wall", {}),
        r"创建.*?结构|(make|create|add).*?structure" : ("arch", "structure", {}),
        r"创建.*?窗户|(make|create|add).*?window" : ("arch", "window", {}),

        # Boolean operations
        r"并集|合并|union|merge|fuse" : ("boolean", "fuse", {}),
        r"差集|减去|difference|subtract|cut" : ("boolean", "cut", {}),
        r"交集|共同|intersection|common" : ("boolean", "common", {}),
        r"截面|section" : ("boolean", "section", {}),

        # Export
        r"导出.*?step|export.*?step" : ("export", "step", {}),
        r"导出.*?stl|export.*?stl" : ("export", "stl", {}),
        r"导出.*?obj|export.*?obj" : ("export", "obj", {}),
        r"导出.*?iges|export.*?iges" : ("export", "iges", {}),

        # PartDesign
        r"创建.*?body|创建.*?零件|(make|create).*?body" : ("partdesign", "create-body", {}),
        r"拉伸|创建.*?拉伸|extrude|pad" : ("partdesign", "pad", {}),
        r"开槽|开孔|pocket|hole" : ("partdesign", "pocket", {}),
        r"打孔|钻孔|hole" : ("partdesign", "hole", {}),
        r"旋转|revolution" : ("partdesign", "revolution", {}),
        r"开槽.*?旋转|groove" : ("partdesign", "groove", {}),
        r"倒圆角|fillet|round" : ("partdesign", "fillet", {}),
        r"倒角|chamfer" : ("partdesign", "chamfer", {}),

        # Mesh
        r"创建.*?网格|mesh" : ("mesh", "create", {}),
        r"网格.*?从.*?形状|mesh.*?from.*?shape" : ("mesh", "from-shape", {}),
        r"网格.*?布尔|mesh.*?boolean" : ("mesh", "boolean", {}),

        # Surface
        r"创建.*?曲面|surface" : ("surface", "create", {}),
        r"放样|loft" : ("surface", "create", {"type": "Loft"}),
        r"扫掠|sweep" : ("surface", "create", {"type": "Sweep"}),
        r"曲面.*?从.*?边|surface.*?from.*?edges" : ("surface", "from-edges", {}),

        # TechDraw
        r"创建.*?图纸|techdraw.*?page" : ("techdraw", "create-page", {}),
        r"添加.*?视图|add.*?view" : ("techdraw", "add-view", {}),
        r"添加.*?尺寸|add.*?dimension" : ("techdraw", "add-dimension", {}),

        # Spreadsheet
        r"创建.*?电子表格|spreadsheet" : ("spreadsheet", "create", {}),
        r"设置.*?单元格|set.*?cell" : ("spreadsheet", "set-cell", {}),
        r"设置.*?公式|set.*?formula" : ("spreadsheet", "set-formula", {}),

        # Assembly
        r"创建.*?装配|assembly" : ("assembly", "create", {}),
        r"添加.*?零件.*?装配|add.*?part.*?assembly" : ("assembly", "add-part", {}),
        r"添加.*?约束|add.*?constraint" : ("assembly", "add-constraint", {}),

        # Path/CAM
        r"创建.*?加工程序|path.*?job" : ("path", "create-job", {}),
        r"添加.*?操作|path.*?operation" : ("path", "add-operation", {}),
        r"导出.*?gcode|export.*?gcode" : ("path", "export-gcode", {}),

        # FEM
        r"创建.*?有限元|创建.*?分析|fem.*?analysis" : ("fem", "create-analysis", {}),
        r"添加.*?材料|fem.*?material" : ("fem", "add-material", {}),
        r"添加.*?边界条件|fem.*?bc|fem.*?boundary" : ("fem", "add-bc", {}),
        r"运行.*?分析|fem.*?run" : ("fem", "run", {}),

        # Document
        r"创建.*?文档|document" : ("document", "create", {}),
        r"列出.*?对象|list.*?objects?" : ("object", "list", {}),
        r"删除.*?|delete|remove" : ("object", "delete", {}),
    }

    def __init__(self):
        self.command_history: List[Dict] = []

    def parse(self, natural_language: str) -> Dict[str, Any]:
        """
        Parse natural language into structured command

        Args:
            natural_language: Natural language input

        Returns:
            Parsed command dictionary
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

                # Extract parameters
                self._extract_parameters(nl, result["parameters"])

                # Add to history
                self.command_history.append(result)

                return result

        return {
            "success": False,
            "error": "Unable to parse command",
            "raw_input": natural_language,
            "suggestion": "Please use explicit commands like: 'create box' or 'draw circle'"
        }

    def _extract_parameters(self, text: str, params: Dict):
        """Extract parameters from text"""
        # Extract size parameters
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

        # Extract name
        name_patterns = [
            r"名[称叫]([a-zA-Z0-9_]+)",
            r"叫\s*([a-zA-Z0-9_]+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                params["name"] = match.group(1)
                break

        # Extract number of sides
        sides_match = re.search(r"(\d+)\s*[边角]", text)
        if sides_match:
            params["sides"] = int(sides_match.group(1))


class BatchProcessor:
    """Batch command processor with optional transaction support"""

    def __init__(self, wrapper, transactional: bool = False):
        """
        Initialize BatchProcessor

        Args:
            wrapper: FreeCADWrapper instance
            transactional: If True, rollback on failure
        """
        self.wrapper = wrapper
        self.transactional = transactional
        self.results: List[Dict] = []
        self.executed: List[Tuple[Dict, Dict]] = []  # (command, result) pairs

    def execute_batch(self, commands: List[Dict]) -> List[Dict]:
        """
        Execute commands in batch

        Args:
            commands: List of commands

        Returns:
            List of execution results
        """
        results = []
        executed = []

        for cmd in commands:
            group = cmd.get("command_group")
            action = cmd.get("command")
            params = cmd.get("parameters", {})

            try:
                result = self._execute_single(group, action, params)
                results.append(result)
                executed.append((cmd, result))

                if self.transactional and not result.get("success"):
                    # Rollback on failure
                    self._rollback(executed)
                    results[-1] = {
                        "success": False,
                        "error": "Transaction rolled back",
                        "rolled_back": True,
                        "failed_command": cmd
                    }
                    break
            except Exception as e:
                result = {"success": False, "error": str(e)}
                results.append(result)
                executed.append((cmd, result))

                if self.transactional:
                    self._rollback(executed)
                    results[-1] = {
                        "success": False,
                        "error": "Transaction rolled back",
                        "rolled_back": True,
                        "failed_command": cmd
                    }
                    break

        self.results = results
        self.executed = executed
        return results

    def _execute_single(self, group: str, action: str, params: Dict) -> Dict:
        """Execute a single command"""
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
            else:
                result = {"success": False, "error": f"Unknown sketch action: {action}"}
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
        elif group == "boolean":
            result = self.wrapper.boolean_operation(
                params.get("name", "Boolean"),
                action,
                params.get("object1"),
                params.get("object2")
            )
        elif group == "mesh":
            if action == "create":
                result = self.wrapper.create_mesh_object(
                    params.get("name", "Mesh"),
                    params.get("type", "RegularMesh"),
                    params
                )
            elif action == "from-shape":
                result = self.wrapper.mesh_from_shape(
                    params.get("name", "Mesh"),
                    params.get("source"),
                    params.get("deflection", 0.1)
                )
            elif action == "boolean":
                result = self.wrapper.mesh_boolean(
                    params.get("name", "Mesh"),
                    params.get("operation"),
                    params.get("object1"),
                    params.get("object2")
                )
            else:
                result = {"success": False, "error": f"Unknown mesh action: {action}"}
        elif group == "surface":
            result = self.wrapper.create_surface(
                params.get("name", "Surface"),
                params.get("type", "Fill"),
                params
            )
        elif group == "partdesign":
            if action == "create-body":
                result = self.wrapper.create_partdesign_body(
                    params.get("name", "Body")
                )
            elif action == "pad":
                result = self.wrapper.create_pad(
                    params.get("name", "Pad"),
                    params.get("body"),
                    params.get("sketch"),
                    params.get("length", 10.0),
                    params.get("direction", "Normal")
                )
            elif action == "pocket":
                result = self.wrapper.create_pocket(
                    params.get("name", "Pocket"),
                    params.get("body"),
                    params.get("sketch"),
                    params.get("length", 10.0),
                    params.get("type", "Through")
                )
            elif action == "hole":
                result = self.wrapper.create_hole(
                    params.get("name", "Hole"),
                    params.get("body"),
                    params.get("diameter", 5.0),
                    params.get("depth", 10.0),
                    params.get("position")
                )
            elif action == "revolution":
                result = self.wrapper.create_revolution(
                    params.get("name", "Revolution"),
                    params.get("body"),
                    params.get("sketch"),
                    params.get("angle", 360.0)
                )
            elif action == "groove":
                result = self.wrapper.create_groove(
                    params.get("name", "Groove"),
                    params.get("body"),
                    params.get("angle", 360.0),
                    params.get("radius", 5.0)
                )
            elif action == "fillet":
                result = self.wrapper.create_fillet(
                    params.get("name", "Fillet"),
                    params.get("body"),
                    params.get("radius", 2.0)
                )
            elif action == "chamfer":
                result = self.wrapper.create_chamfer(
                    params.get("name", "Chamfer"),
                    params.get("body"),
                    params.get("size", 1.0)
                )
            else:
                result = {"success": False, "error": f"Unknown partdesign action: {action}"}
        elif group == "techdraw":
            if action == "create-page":
                result = self.wrapper.techdraw_create_page(
                    params.get("name", "Page"),
                    params.get("template", "A4_Landscape")
                )
            elif action == "add-view":
                result = self.wrapper.techdraw_add_view(
                    params.get("page"),
                    params.get("source"),
                    params.get("projection", "FirstAngle")
                )
            elif action == "add-dimension":
                result = self.wrapper.techdraw_add_dimension(
                    params.get("view"),
                    params.get("type", "Horizontal"),
                    []
                )
            elif action == "export":
                result = self.wrapper.techdraw_export(
                    params.get("page"),
                    params.get("filepath"),
                    params.get("format", "PDF")
                )
            else:
                result = {"success": False, "error": f"Unknown techdraw action: {action}"}
        elif group == "spreadsheet":
            if action == "create":
                result = self.wrapper.spreadsheet_create(
                    params.get("name", "Spreadsheet")
                )
            elif action == "set-cell":
                result = self.wrapper.spreadsheet_set_cell(
                    params.get("sheet"),
                    params.get("cell"),
                    params.get("value")
                )
            elif action == "set-formula":
                result = self.wrapper.spreadsheet_set_formula(
                    params.get("sheet"),
                    params.get("cell"),
                    params.get("formula")
                )
            else:
                result = {"success": False, "error": f"Unknown spreadsheet action: {action}"}
        elif group == "assembly":
            if action == "create":
                result = self.wrapper.assembly_create(
                    params.get("name", "Assembly")
                )
            elif action == "add-part":
                result = self.wrapper.assembly_add_part(
                    params.get("assembly"),
                    params.get("part"),
                    params.get("placement", "[0, 0, 0]")
                )
            elif action == "add-constraint":
                result = self.wrapper.assembly_add_constraint(
                    params.get("assembly"),
                    params.get("type"),
                    params.get("object1"),
                    params.get("object2")
                )
            else:
                result = {"success": False, "error": f"Unknown assembly action: {action}"}
        elif group == "path":
            if action == "create-job":
                result = self.wrapper.path_create_job(
                    params.get("name", "Job"),
                    params.get("base")
                )
            elif action == "add-operation":
                result = self.wrapper.path_add_operation(
                    params.get("job"),
                    params.get("type", "Drill")
                )
            elif action == "export-gcode":
                result = self.wrapper.path_export_gcode(
                    params.get("job"),
                    params.get("filepath"),
                    params.get("post", "linuxcnc")
                )
            else:
                result = {"success": False, "error": f"Unknown path action: {action}"}
        elif group == "fem":
            if action == "create-analysis":
                result = self.wrapper.fem_create_analysis(
                    params.get("name", "Analysis"),
                    params.get("type", "static")
                )
            elif action == "add-material":
                result = self.wrapper.fem_add_material(
                    params.get("analysis"),
                    params.get("material", "Steel")
                )
            elif action == "add-bc":
                result = self.wrapper.fem_add_boundary_condition(
                    params.get("analysis"),
                    params.get("type"),
                    params.get("object"),
                    {}
                )
            elif action == "run":
                result = self.wrapper.fem_run_analysis(
                    params.get("analysis")
                )
            else:
                result = {"success": False, "error": f"Unknown fem action: {action}"}
        elif group == "export":
            result = self.wrapper.export_document(
                params.get("filepath"),
                action.upper()
            )
        elif group == "document":
            if action == "create":
                result = self.wrapper.initialize()
            else:
                result = {"success": False, "error": f"Unknown document action: {action}"}
        elif group == "object":
            if action == "delete":
                result = self.wrapper.delete_object(params.get("name"))
            elif action == "list":
                result = {"success": True, "objects": self.wrapper.list_objects()}
            else:
                result = {"success": False, "error": f"Unknown object action: {action}"}
        else:
            result = {"success": False, "error": f"Unknown command group: {group}"}

        return result

    def _rollback(self, executed: List[Tuple[Dict, Dict]]) -> None:
        """Rollback executed commands in reverse order"""
        for cmd, result in reversed(executed):
            if result.get("success") and "object_handle" in result:
                # Try to delete the created object
                try:
                    handle = result["object_handle"]
                    self.wrapper.delete_object(handle)
                except Exception:
                    pass  # Best effort rollback

    def get_summary(self) -> Dict[str, Any]:
        """Get batch execution summary"""
        if not self.results:
            return {"total": 0, "success": 0, "failed": 0}

        success_count = sum(1 for r in self.results if r.get("success"))
        rolled_back = any(r.get("rolled_back") for r in self.results if isinstance(r, dict))

        return {
            "total": len(self.results),
            "success": success_count,
            "failed": len(self.results) - success_count,
            "success_rate": success_count / len(self.results) * 100 if self.results else 0,
            "rolled_back": rolled_back,
            "transactional": self.transactional
        }


class CommandGenerator:
    """Command generator - generates CLI commands from requirements"""

    @staticmethod
    def generate_part_command(name: str, shape: str, **kwargs) -> str:
        """Generate Part command"""
        params = json.dumps(kwargs, ensure_ascii=False)
        return f'freecad-cli part create --name "{name}" --type {shape} --params \'{params}\''

    @staticmethod
    def generate_sketch_command(name: str, plane: str = "XY") -> str:
        """Generate Sketch command"""
        return f'freecad-cli sketch create --name "{name}" --plane {plane}'

    @staticmethod
    def generate_draft_command(draft_type: str, name: str, **kwargs) -> str:
        """Generate Draft command"""
        parts = [f'freecad-cli draft {draft_type.lower()} --name "{name}"']
        for key, value in kwargs.items():
            parts.append(f"--{key} {value}")
        return " ".join(parts)

    @staticmethod
    def generate_boolean_command(operation: str, name: str,
                                 obj1: str, obj2: str) -> str:
        """Generate boolean operation command"""
        return f'freecad-cli boolean {operation.lower()} --name "{name}" --object1 {obj1} --object2 {obj2}'

    @staticmethod
    def generate_export_command(format_type: str, filepath: str) -> str:
        """Generate export command"""
        return f'freecad-cli export {format_type.lower()} --filepath "{filepath}"'


def generate_workflow_commands(workflow: str) -> List[str]:
    """
    Generate command list from workflow description

    Args:
        workflow: Workflow description

    Returns:
        List of CLI commands
    """
    commands = []

    # Parse workflow
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
                cmd = f"# {line} (unrecognized)"

            commands.append(cmd)

    return commands
