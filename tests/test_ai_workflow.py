# -*- coding: utf-8 -*-
"""Tests for AI workflow integration"""

import pytest
from unittest.mock import MagicMock, patch


class TestAICommandParser:
    """Test AI command parser"""

    def setup_method(self):
        """Set up test fixtures"""
        from freecad_cli.ai_integration import AICommandParser
        self.parser = AICommandParser()

    def test_parse_part_box(self):
        """Test parsing part box commands"""
        result = self.parser.parse("Create a box named MyBox")
        assert result["success"] is True
        assert result["command_group"] == "part"
        assert result["command"] == "create"
        assert result["parameters"]["type"] == "Box"

    def test_parse_part_cylinder(self):
        """Test parsing part cylinder commands"""
        result = self.parser.parse("创建圆柱")
        assert result["success"] is True
        assert result["command_group"] == "part"
        assert result["command"] == "create"
        assert result["parameters"]["type"] == "Cylinder"

    def test_parse_partdesign_pad(self):
        """Test parsing pad commands"""
        result = self.parser.parse("Create a pad named MyPad")
        assert result["success"] is True
        assert result["command_group"] == "partdesign"
        assert result["command"] == "pad"

    def test_parse_partdesign_fillet(self):
        """Test parsing fillet commands"""
        result = self.parser.parse("Fillet the body with radius 2")
        assert result["success"] is True
        assert result["command_group"] == "partdesign"
        assert result["command"] == "fillet"
        assert result["parameters"]["radius"] == 2.0

    def test_parse_partdesign_chamfer(self):
        """Test parsing chamfer commands"""
        result = self.parser.parse("倒角")
        assert result["success"] is True
        assert result["command_group"] == "partdesign"
        assert result["command"] == "chamfer"

    def test_parse_mesh_from_shape(self):
        """Test parsing mesh from shape commands"""
        result = self.parser.parse("Create a mesh from shape")
        assert result["success"] is True
        assert result["command_group"] == "mesh"
        assert result["command"] == "from-shape"

    def test_parse_surface_loft(self):
        """Test parsing loft commands"""
        result = self.parser.parse("放样")
        assert result["success"] is True
        assert result["command_group"] == "surface"
        assert result["command"] == "create"
        assert result["parameters"]["type"] == "Loft"

    def test_parse_fem_analysis(self):
        """Test parsing FEM analysis commands"""
        result = self.parser.parse("创建有限元分析")
        assert result["success"] is True
        assert result["command_group"] == "fem"
        assert result["command"] == "create-analysis"

    def test_parse_path_export_gcode(self):
        """Test parsing G-code export commands"""
        result = self.parser.parse("导出 gcode")
        assert result["success"] is True
        assert result["command_group"] == "path"
        assert result["command"] == "export-gcode"

    def test_parse_boolean_union(self):
        """Test parsing union commands"""
        result = self.parser.parse("并集")
        assert result["success"] is True
        assert result["command_group"] == "boolean"
        assert result["command"] == "fuse"

    def test_parse_boolean_section(self):
        """Test parsing section commands"""
        result = self.parser.parse("截面")
        assert result["success"] is True
        assert result["command_group"] == "boolean"
        assert result["command"] == "section"

    def test_parse_failure(self):
        """Test parsing failure returns suggestion"""
        result = self.parser.parse("do something weird xyz123")
        assert result["success"] is False
        assert "suggestion" in result

    def test_command_history(self):
        """Test command history tracking"""
        self.parser.parse("Create a box")
        self.parser.parse("创建圆柱")

        assert len(self.parser.command_history) == 2
        assert self.parser.command_history[0]["command_group"] == "part"
        assert self.parser.command_history[1]["command_group"] == "part"


class TestBatchProcessor:
    """Test BatchProcessor"""

    def test_execute_batch_basic(self):
        """Test basic batch execution"""
        from freecad_cli.ai_integration import BatchProcessor

        mock_wrapper = MagicMock()
        mock_wrapper.create_part.return_value = {"success": True, "object_handle": "mock:part/Box1"}

        processor = BatchProcessor(mock_wrapper, transactional=False)

        commands = [
            {"command_group": "part", "command": "create", "parameters": {"name": "Box1", "type": "Box"}},
            {"command_group": "part", "command": "create", "parameters": {"name": "Box2", "type": "Box"}},
        ]

        results = processor.execute_batch(commands)

        assert len(results) == 2
        assert all(r.get("success") for r in results)

    def test_execute_batch_with_failure(self):
        """Test batch continues on failure (non-transactional)"""
        from freecad_cli.ai_integration import BatchProcessor

        mock_wrapper = MagicMock()
        mock_wrapper.create_part.side_effect = [
            {"success": True, "object_handle": "mock:part/Box1"},
            Exception("Simulated error"),
            {"success": True, "object_handle": "mock:part/Box2"},
        ]

        processor = BatchProcessor(mock_wrapper, transactional=False)
        results = processor.execute_batch([
            {"command_group": "part", "command": "create", "parameters": {"name": "Box1"}},
            {"command_group": "part", "command": "create", "parameters": {"name": "Box2"}},
            {"command_group": "part", "command": "create", "parameters": {"name": "Box3"}},
        ])

        assert results[0].get("success") is True
        assert results[1].get("success") is False
        assert results[2].get("success") is True

    def test_execute_batch_transactional_rollback(self):
        """Test transactional mode rolls back on failure"""
        from freecad_cli.ai_integration import BatchProcessor

        mock_wrapper = MagicMock()
        mock_wrapper.create_part.side_effect = [
            {"success": True, "object_handle": "mock:part/Box1"},
            {"success": True, "object_handle": "mock:part/Box2"},
            {"success": False, "error": "Simulated failure"},
        ]
        mock_wrapper.delete_object.return_value = {"success": True}

        processor = BatchProcessor(mock_wrapper, transactional=True)
        results = processor.execute_batch([
            {"command_group": "part", "command": "create", "parameters": {"name": "Box1"}},
            {"command_group": "part", "command": "create", "parameters": {"name": "Box2"}},
            {"command_group": "part", "command": "create", "parameters": {"name": "Box3"}},
        ])

        # First two should be rolled back
        assert results[-1].get("rolled_back") is True
        # Delete should have been called for rollback
        assert mock_wrapper.delete_object.called

    def test_get_summary(self):
        """Test batch summary generation"""
        from freecad_cli.ai_integration import BatchProcessor

        mock_wrapper = MagicMock()
        mock_wrapper.create_part.return_value = {"success": True, "object_handle": "mock:part/Box1"}

        processor = BatchProcessor(mock_wrapper)
        processor.execute_batch([
            {"command_group": "part", "command": "create", "parameters": {"name": "Box1"}},
            {"command_group": "part", "command": "create", "parameters": {"name": "Box2"}},
        ])

        summary = processor.get_summary()
        assert summary["total"] == 2
        assert summary["success"] == 2
        assert summary["failed"] == 0
        assert summary["success_rate"] == 100.0


class TestCommandGenerator:
    """Test CommandGenerator"""

    def test_generate_part_command(self):
        """Test part command generation"""
        from freecad_cli.ai_integration import CommandGenerator

        cmd = CommandGenerator.generate_part_command("MyBox", "Box", length=5, width=3)
        assert "part create" in cmd
        assert "--name" in cmd
        assert "--type Box" in cmd

    def test_generate_sketch_command(self):
        """Test sketch command generation"""
        from freecad_cli.ai_integration import CommandGenerator

        cmd = CommandGenerator.generate_sketch_command("MySketch", "XZ")
        assert "sketch create" in cmd
        assert "--name" in cmd
        assert "--plane XZ" in cmd

    def test_generate_boolean_command(self):
        """Test boolean command generation"""
        from freecad_cli.ai_integration import CommandGenerator

        cmd = CommandGenerator.generate_boolean_command("fuse", "Result", "Obj1", "Obj2")
        assert "boolean fuse" in cmd
        assert "--name" in cmd
        assert "--object1 Obj1" in cmd
        assert "--object2 Obj2" in cmd


class TestSchemaIntegration:
    """Test schema integration"""

    def test_schema_get_all_commands(self):
        """Test getting all commands via schema"""
        from freecad_cli._schema import get_schema, list_commands

        schema = get_schema()
        assert "version" in schema
        assert "command_groups" in schema
        assert len(schema["command_groups"]) > 0

        commands = list_commands()
        assert len(commands) > 0
        assert "part.create" in commands

    def test_schema_get_command(self):
        """Test getting specific command schema"""
        from freecad_cli._schema import get_command_schema

        schema = get_command_schema("part", "create")
        assert schema is not None
        assert "description" in schema
        assert "parameters" in schema
        assert "name" in schema["parameters"]

    def test_schema_command_not_found(self):
        """Test schema returns None for unknown command"""
        from freecad_cli._schema import get_command_schema

        schema = get_command_schema("nonexistent", "command")
        assert schema is None
