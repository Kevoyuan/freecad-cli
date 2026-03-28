# FreeCAD CLI - AI Integration Guide

This document describes how to integrate AI systems with FreeCAD CLI.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Python API](#python-api)
- [Natural Language Processing](#natural-language-processing)
- [Batch Operations](#batch-operations)
- [Workflow Automation](#workflow-automation)
- [Error Handling](#error-handling)

---

## Basic Usage

### Shell Commands

All CLI commands support JSON output for easy AI parsing:

```bash
# Create a part
freecad-cli --format json part create --name Box1 --type Box --params '{"length": 10, "width": 10, "height": 5}'

# List objects
freecad-cli --format json object list

# Get object info
freecad-cli --format json info object --name Box1
```

### JSON Response Format

```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00",
  "message": "Operation description",
  "data": {
    // Operation result data
  }
}
```

Error response:
```json
{
  "status": "error",
  "timestamp": "2024-01-15T10:30:00",
  "message": "Error description",
  "data": {
    "error": "Detailed error information"
  }
}
```

---

## Python API

### Using Python Classes Directly

```python
from freecad_cli import FreeCADWrapper, OutputFormatter

# Initialize
wrapper = FreeCADWrapper(headless=True)
result = wrapper.initialize()
print(result)
# {'success': True, 'document': 'CLI_Document', 'headless': True}

# Create a part
result = wrapper.create_part("MyBox", "Box", {
    "length": 10,
    "width": 10,
    "height": 5
})
print(result)
# {'success': True, 'name': 'MyBox', 'type': 'Box', 'bounding_box': {...}}

# Boolean operations
result = wrapper.boolean_operation("FusedBox", "Fuse", "Box1", "Box2")

# Export
result = wrapper.export_document("output.step", "STEP")
```

### Using Formatters

```python
from freecad_cli import OutputFormatter

formatter = OutputFormatter(output_format="json", pretty=True)

# Format data
result = wrapper.create_part("Box1", "Box", {...})
output = formatter.format(result, status="success", message="Created successfully")
print(output)
```

---

## Natural Language Processing

### AI Command Parser

```python
from freecad_cli import AICommandParser

parser = AICommandParser()

# Parse natural language commands
result = parser.parse("Create a cube named TestBox")
print(result)
# {
#     'success': True,
#     'command_group': 'part',
#     'command': 'create',
#     'parameters': {'name': 'TestBox', 'type': 'Box'},
#     'raw_input': 'Create a cube named TestBox'
# }

# More examples
parser.parse("Create a sphere with radius 5")
parser.parse("Create a sketch on XY plane")
parser.parse("Draw a hexagon")
parser.parse("Create a wall")
```

### Supported Natural Language Patterns

| Input | Parsed Result |
|-------|---------------|
| "Create box" | part create Box |
| "Create cylinder" | part create Cylinder |
| "Create sphere" | part create Sphere |
| "Create sketch" | sketch create |
| "Add line" | sketch add-line |
| "Add circle" | sketch add-circle |
| "Draw rectangle" | draft rectangle |
| "Draw polygon" | draft polygon |
| "Create wall" | arch wall |
| "Merge objects" | boolean fuse |
| "Subtract objects" | boolean cut |
| "Export STEP" | export step |

---

## Batch Operations

### Batch Command Processor

```python
from freecad_cli import FreeCADWrapper, BatchProcessor

wrapper = FreeCADWrapper()
processor = BatchProcessor(wrapper)
wrapper.initialize()

# Define batch commands
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

# Execute batch commands
results = processor.execute_batch(commands)

# Get execution summary
summary = processor.get_summary()
print(f"Success: {summary['success']}/{summary['total']}")
print(f"Success rate: {summary['success_rate']:.1f}%")
```

---

## Workflow Automation

### Generate Commands from Workflow Descriptions

```python
from freecad_cli.ai_integration import generate_workflow_commands

workflow = """
# Design a simple part
Create a box named Base with length 100, width 50, height 20
Create a cylinder named Hole with radius 15, height 30
Merge Base and Hole, name the result Result
Export Result as STEP file to output/part.step
"""

# Generate CLI commands
commands = generate_workflow_commands(workflow)
for cmd in commands:
    print(cmd)
    # freecad-cli part create --name "Base" --type Box --params '{"length": 100, ...}'
    # freecad-cli part create --name "Hole" --type Cylinder --params '{"radius": 15, ...}'
    # freecad-cli boolean fuse --name "Result" --object1 Base --object2 Hole
    # freecad-cli export step --filepath "output/part.step"
```

### Complete Workflow Example

```python
import subprocess
import json

def execute_freecad_command(command: list) -> dict:
    """Execute FreeCAD CLI command and return JSON result"""
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
    """Complete workflow to create a simple part"""
    workflow = [
        # 1. Create base
        ("part", ["create", "--name", "Base", "--type", "Box",
                  "--params", '{"length": 100, "width": 100, "height": 20}']),

        # 2. Create boss
        ("cylinder", ["create", "--name", "Boss", "--type", "Cylinder",
                      "--params", '{"radius": 30, "height": 40}']),

        # 3. Merge
        ("boolean", ["fuse", "--name", "Combined", "--object1", "Base", "--object2", "Boss"]),

        # 4. Export
        ("export", ["step", "--filepath", "/tmp/part.step"])
    ]

    for step_name, command in workflow:
        print(f"Executing step: {step_name}")
        result = execute_freecad_command(command)

        if result.get("status") != "success":
            print(f"Error: {result.get('message')}")
            return False

    print("Workflow complete!")
    return True

if __name__ == "__main__":
    create_simple_part()
```

---

## Error Handling

### Command-Level Error Handling

```python
import subprocess
import json

def safe_execute(command: list, retries: int = 3):
    """Execute with retry on error"""
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

                # Check for retryable errors
                if "timeout" in error_msg.lower() and attempt < retries - 1:
                    print(f"Retry {attempt + 1}/{retries}...")
                    continue

                return {"status": "error", "message": error_msg}

        except subprocess.TimeoutExpired:
            if attempt < retries - 1:
                continue
            return {"status": "error", "message": "Command execution timeout"}

    return {"status": "error", "message": "All retries failed"}

# Usage example
result = safe_execute(["part", "create", "--name", "Test", "--type", "Box"])
if result.get("status") == "success":
    print(f"Created successfully: {result['data']}")
else:
    print(f"Operation failed: {result['message']}")
```

### Python API Error Handling

```python
from freecad_cli import FreeCADWrapper

wrapper = FreeCADWrapper()

try:
    # Initialize
    init_result = wrapper.initialize()
    if not init_result.get("success"):
        raise RuntimeError(f"Initialization failed: {init_result.get('error')}")

    # Create object
    result = wrapper.create_part("Box1", "Box", {"length": 10})
    if not result.get("success"):
        raise RuntimeError(f"Creation failed: {result.get('error')}")

    # Get info
    info = wrapper.get_object_info("Box1")
    print(f"Object info: {info}")

except RuntimeError as e:
    print(f"Runtime error: {e}")
except Exception as e:
    print(f"Unknown error: {e}")
```

---

## AI Calling Templates

### Claude / GPT and Other LLM Calling Templates

```python
import subprocess
import json

class FreeCADAgent:
    """Wrapper class for AI Agent to call FreeCAD"""

    def __init__(self):
        self.base_command = ["freecad-cli", "--format", "json"]

    def execute(self, action: str, **kwargs) -> dict:
        """
        Execute FreeCAD operation

        Args:
            action: Operation type (create_part, create_sketch, boolean, etc.)
            **kwargs: Operation parameters

        Returns:
            Operation result dictionary
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
            return {"status": "error", "message": f"Unknown action: {action}"}

        # Execute command
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"status": "error", "message": result.stderr}

    def create_model_workflow(self, description: str) -> dict:
        """
        Auto-create model from description

        This method can be called by AI to understand natural language requirements
        """
        from freecad_cli import AICommandParser, BatchProcessor

        parser = AICommandParser()

        # Parse requirements
        parsed = parser.parse(description)

        if not parsed.get("success"):
            return {"status": "error", "message": "Failed to parse requirements"}

        # Create processor and execute
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


# Usage examples
if __name__ == "__main__":
    agent = FreeCADAgent()

    # Method 1: Direct call
    result = agent.execute("create_part", name="Box1", type="Box",
                          params={"length": 10, "width": 10, "height": 5})

    # Method 2: Workflow
    result = agent.create_model_workflow("Create a cube named TestBox")

    print(result)
```

---

## Best Practices

1. **Always Check Return Value Status**
   ```python
   result = wrapper.create_part(...)
   if result.get("success"):
       # Handle success
   else:
       # Handle error
   ```

2. **Use JSON Format for Easy Parsing**
   ```bash
   freecad-cli --format json [command]
   ```

3. **Use Transactions for Batch Operations**
   ```python
   processor = BatchProcessor(wrapper)
   results = processor.execute_batch(commands)
   summary = processor.get_summary()
   ```

4. **Error Retry Mechanism**
   ```python
   for attempt in range(max_retries):
       result = execute_command(...)
       if result.get("success"):
           break
   ```

5. **Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger("FreeCAD-CLI")
   ```

---

## Getting Help

```bash
# View all commands
freecad-cli --help

# View specific command help
freecad-cli part --help
freecad-cli part create --help
freecad-cli sketch --help
```
