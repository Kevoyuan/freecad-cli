# FreeCAD CLI - AI 集成指南

本文档详细说明如何让 AI 系统调用 FreeCAD CLI。

## 目录

- [基础调用方式](#基础调用方式)
- [Python API 调用](#python-api-调用)
- [自然语言处理](#自然语言处理)
- [批量操作](#批量操作)
- [工作流自动化](#工作流自动化)
- [错误处理](#错误处理)

---

## 基础调用方式

### Shell 调用

所有 CLI 命令都支持 JSON 输出，便于 AI 解析：

```bash
# 创建零件
freecad-cli --format json part create --name Box1 --type Box --params '{"length": 10, "width": 10, "height": 5}'

# 列出对象
freecad-cli --format json object list

# 获取对象信息
freecad-cli --format json info object --name Box1
```

### JSON 响应格式

```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00",
  "message": "操作描述",
  "data": {
    // 操作结果数据
  }
}
```

错误响应：
```json
{
  "status": "error",
  "timestamp": "2024-01-15T10:30:00",
  "message": "错误描述",
  "data": {
    "error": "详细错误信息"
  }
}
```

---

## Python API 调用

### 直接使用 Python 类

```python
from freecad_cli import FreeCADWrapper, OutputFormatter

# 初始化
wrapper = FreeCADWrapper(headless=True)
result = wrapper.initialize()
print(result)
# {'success': True, 'document': 'CLI_Document', 'headless': True}

# 创建零件
result = wrapper.create_part("MyBox", "Box", {
    "length": 10,
    "width": 10,
    "height": 5
})
print(result)
# {'success': True, 'name': 'MyBox', 'type': 'Box', 'bounding_box': {...}}

# 布尔运算
result = wrapper.boolean_operation("FusedBox", "Fuse", "Box1", "Box2")

# 导出
result = wrapper.export_document("output.step", "STEP")
```

### 使用格式化器

```python
from freecad_cli import OutputFormatter

formatter = OutputFormatter(output_format="json", pretty=True)

# 格式化数据
result = wrapper.create_part("Box1", "Box", {...})
output = formatter.format(result, status="success", message="创建成功")
print(output)
```

---

## 自然语言处理

### AI 命令解析器

```python
from freecad_cli import AICommandParser

parser = AICommandParser()

# 解析自然语言命令
result = parser.parse("创建一个名为 TestBox 的立方体")
print(result)
# {
#     'success': True,
#     'command_group': 'part',
#     'command': 'create',
#     'parameters': {'name': 'TestBox', 'type': 'Box'},
#     'raw_input': '创建一个名为 TestBox 的立方体'
# }

# 更多示例
parser.parse("创建一个半径为 5 的球体")
parser.parse("在 XY 平面创建一个草图")
parser.parse("绘制一个六边形")
parser.parse("创建一堵墙")
```

### 支持的自然语言模式

> AI 集成同时支持中文和英文自然语言输入。

| 输入 | 解析结果 |
|------|----------|
| "创建盒子" | part create Box |
| "创建圆柱" | part create Cylinder |
| "创建球体" | part create Sphere |
| "创建草图" | sketch create |
| "添加直线" | sketch add-line |
| "添加圆" | sketch add-circle |
| "绘制矩形" | draft rectangle |
| "绘制多边形" | draft polygon |
| "创建墙体" | arch wall |
| "合并对象" | boolean fuse |
| "减去对象" | boolean cut |
| "导出 STEP" | export step |
| 英文 "create box" | part create Box |
| 英文 "add cylinder" | part create Cylinder |
| 英文 "make sphere" | part create Sphere |

---

## 批量操作

### 批量命令处理器

```python
from freecad_cli import FreeCADWrapper, BatchProcessor

wrapper = FreeCADWrapper()
processor = BatchProcessor(wrapper)
wrapper.initialize()

# 定义批量命令
commands = [
    {
        "command_group": "part",
        "command": "create",
        "parameters": {"name": "Box1", "type": "Box", "length": 10, "width": 10, "height": 5}
    },
    {
        "command_group": "part",
        "command": "create",
        "parameters": {"name": "Box2", "type": "Box", "length": 5, "width": 5, "height": 5}
    },
    {
        "command_group": "part",
        "command": "create",
        "parameters": {"name": "Cylinder1", "type": "Cylinder", "radius": 3, "height": 10}
    },
    {
        "command_group": "boolean",
        "command": "fuse",
        "parameters": {"name": "Union", "object1": "Box1", "object2": "Box2"}
    },
    {
        "command_group": "boolean",
        "command": "cut",
        "parameters": {"name": "Final", "object1": "Union", "object2": "Cylinder1"}
    },
    {
        "command_group": "export",
        "command": "step",
        "parameters": {"filepath": "output/final_model.step"}
    }
]

# 执行批量命令
results = processor.execute_batch(commands)

# 获取执行摘要
summary = processor.get_summary()
print(f"成功: {summary['success']}/{summary['total']}")
print(f"成功率: {summary['success_rate']:.1f}%")
```

---

## 工作流自动化

### 从工作流描述生成命令

```python
from freecad_cli.ai_integration import generate_workflow_commands

workflow = """
# 设计一个简单的零件
创建一个名为 Base 的盒子，长度 100，宽度 50，高度 20
创建一个名为 Hole 的圆柱，半径 15，高度 30
合并 Base 和 Hole，结果命名为 Result
导出 Result 为 STEP 文件到 output/part.step
"""

# 生成 CLI 命令
commands = generate_workflow_commands(workflow)
for cmd in commands:
    print(cmd)
    # freecad-cli part create --name "Base" --type Box --params '{"length": 100, ...}'
    # freecad-cli part create --name "Hole" --type Cylinder --params '{"radius": 15, ...}'
    # freecad-cli boolean fuse --name "Result" --object1 Base --object2 Hole
    # freecad-cli export step --filepath "output/part.step"
```

### 完整的工作流示例

```python
import subprocess
import json

def execute_freecad_command(command: list) -> dict:
    """执行 FreeCAD CLI 命令并返回 JSON 结果"""
    result = subprocess.run(
        ["python", "-m", "freecad_cli", "--format", "json"] + command,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return {"status": "error", "message": result.stderr}

def create_simple_part():
    """创建简单零件的完整工作流"""
    workflow = [
        # 1. 创建底座
        ("part", ["create", "--name", "Base", "--type", "Box",
                  "--params", '{"length": 100, "width": 100, "height": 20}']),

        # 2. 创建凸台
        ("cylinder", ["create", "--name", "Boss", "--type", "Cylinder",
                      "--params", '{"radius": 30, "height": 40}']),

        # 3. 合并
        ("boolean", ["fuse", "--name", "Combined", "--object1", "Base", "--object2", "Boss"]),

        # 4. 导出
        ("export", ["step", "--filepath", "/tmp/part.step"])
    ]

    for step_name, command in workflow:
        print(f"执行步骤: {step_name}")
        result = execute_freecad_command(command)

        if result.get("status") != "success":
            print(f"错误: {result.get('message')}")
            return False

    print("工作流完成!")
    return True

if __name__ == "__main__":
    create_simple_part()
```

---

## 错误处理

### 命令级错误处理

```python
import subprocess
import json

def safe_execute(command: list, retries: int = 3):
    """带重试的错误处理执行"""
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ["freecad-cli", "--format", "json"] + command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                error_msg = result.stderr.strip()

                # 检查是否是可重试错误
                if "timeout" in error_msg.lower() and attempt < retries - 1:
                    print(f"重试 {attempt + 1}/{retries}...")
                    continue

                return {"status": "error", "message": error_msg}

        except subprocess.TimeoutExpired:
            if attempt < retries - 1:
                continue
            return {"status": "error", "message": "命令执行超时"}

    return {"status": "error", "message": "所有重试均失败"}

# 使用示例
result = safe_execute(["part", "create", "--name", "Test", "--type", "Box"])
if result.get("status") == "success":
    print(f"创建成功: {result['data']}")
else:
    print(f"操作失败: {result['message']}")
```

### Python API 错误处理

```python
from freecad_cli import FreeCADWrapper

wrapper = FreeCADWrapper()

try:
    # 初始化
    init_result = wrapper.initialize()
    if not init_result.get("success"):
        raise RuntimeError(f"初始化失败: {init_result.get('error')}")

    # 创建对象
    result = wrapper.create_part("Box1", "Box", {"length": 10})
    if not result.get("success"):
        raise RuntimeError(f"创建失败: {result.get('error')}")

    # 获取信息
    info = wrapper.get_object_info("Box1")
    print(f"对象信息: {info}")

except RuntimeError as e:
    print(f"运行时错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## AI 调用模板

### Claude / GPT 等 LLM 调用模板

```python
import subprocess
import json

class FreeCADAgent:
    """AI Agent 调用 FreeCAD 的封装类"""

    def __init__(self):
        self.base_command = ["freecad-cli", "--format", "json"]

    def execute(self, action: str, **kwargs) -> dict:
        """
        执行 FreeCAD 操作

        Args:
            action: 操作类型 (create_part, create_sketch, boolean, etc.)
            **kwargs: 操作参数

        Returns:
            操作结果字典
        """
        command = self.base_command.copy()

        if action == "create_part":
            command.extend(["part", "create"])
            command.extend(["--name", kwargs.get("name", "Unnamed")])
            command.extend(["--type", kwargs.get("type", "Box")])
            command.extend(["--params", json.dumps(kwargs.get("params", {}))])

        elif action == "create_sketch":
            command.extend(["sketch", "create"])
            command.extend(["--name", kwargs.get("name", "Sketch")])
            command.extend(["--plane", kwargs.get("plane", "XY")])

        elif action == "boolean":
            command.extend(["boolean", kwargs.get("operation", "fuse")])
            command.extend(["--name", kwargs.get("name", "Result")])
            command.extend(["--object1", kwargs.get("object1")])
            command.extend(["--object2", kwargs.get("object2")])

        elif action == "export":
            command.extend(["export", kwargs.get("format", "step")])
            command.extend(["--filepath", kwargs.get("filepath")])

        elif action == "list_objects":
            command.extend(["object", "list"])
            if kwargs.get("type"):
                command.extend(["--type", kwargs.get("type")])

        elif action == "get_info":
            command.extend(["info", "object"])
            command.extend(["--name", kwargs.get("name")])

        else:
            return {"status": "error", "message": f"未知操作: {action}"}

        # 执行命令
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"status": "error", "message": result.stderr}

    def create_model_workflow(self, description: str) -> dict:
        """
        根据描述自动创建模型

        这个方法可以被 AI 调用来理解自然语言需求
        """
        from freecad_cli import AICommandParser, BatchProcessor

        parser = AICommandParser()

        # 解析需求
        parsed = parser.parse(description)

        if not parsed.get("success"):
            return {"status": "error", "message": "无法解析需求"}

        # 创建处理器并执行
        from freecad_cli import get_wrapper
        wrapper = get_wrapper()
        wrapper.initialize()

        processor = BatchProcessor(wrapper)
        results = processor.execute_batch([parsed])

        return {
            "status": "success",
            "parsed_command": parsed,
            "execution_results": results,
            "summary": processor.get_summary()
        }


# 使用示例
if __name__ == "__main__":
    agent = FreeCADAgent()

    # 方式 1: 直接调用
    result = agent.execute("create_part", name="Box1", type="Box",
                          params={"length": 10, "width": 10, "height": 5})

    # 方式 2: 工作流
    result = agent.create_model_workflow("创建一个名为 TestBox 的立方体")

    print(result)
```

---

## 最佳实践

1. **总是检查返回值状态**
   ```python
   result = wrapper.create_part(...)
   if result.get("success"):
       # 处理成功
   else:
       # 处理错误
   ```

2. **使用 JSON 格式便于解析**
   ```bash
   freecad-cli --format json [command]
   ```

3. **批量操作使用事务**
   ```python
   processor = BatchProcessor(wrapper)
   results = processor.execute_batch(commands)
   summary = processor.get_summary()
   ```

4. **错误重试机制**
   ```python
   for attempt in range(max_retries):
       result = execute_command(...)
       if result.get("success"):
           break
   ```

5. **日志记录**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger("FreeCAD-CLI")
   ```

---

## 获取帮助

```bash
# 查看所有命令
freecad-cli --help

# 查看特定命令帮助
freecad-cli part --help
freecad-cli part create --help
freecad-cli sketch --help
```
