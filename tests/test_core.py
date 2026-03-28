# -*- coding: utf-8 -*-
"""
Unit Tests for CLI Command Layer (core.py)

Tests the Click command handlers using CliRunner.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from click.testing import CliRunner
from freecad_cli.core import cli


class TestPartCommands:
    """Tests for part command group"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_part_create_valid(self):
        """Test part create with valid name and type"""
        result = self.runner.invoke(
            cli,
            ['part', 'create', '--name', 'MyBox', '--type', 'Box']
        )
        assert result.exit_code == 0
        assert 'MyBox' in result.output

    def test_part_create_empty_name_rejected(self):
        """Test part create rejects empty name"""
        result = self.runner.invoke(
            cli,
            ['part', 'create', '--name', '', '--type', 'Box']
        )
        assert result.exit_code != 0
        assert "不能为空字符串" in result.output or "empty" in result.output.lower()

    def test_part_create_invalid_type_rejected(self):
        """Test part create rejects invalid geometry type"""
        result = self.runner.invoke(
            cli,
            ['part', 'create', '--name', 'TestPart', '--type', 'InvalidType']
        )
        assert result.exit_code != 0
        assert 'InvalidType' in result.output

    def test_part_create_all_geometry_types(self):
        """Test part create accepts all valid geometry types"""
        for geom_type in ['Box', 'Cylinder', 'Sphere', 'Cone', 'Torus', 'Ellipsoid']:
            result = self.runner.invoke(
                cli,
                ['part', 'create', '--name', f'Test{geom_type}', '--type', geom_type]
            )
            assert result.exit_code == 0, f"Failed for type {geom_type}: {result.output}"

    def test_part_list(self):
        """Test part list command"""
        result = self.runner.invoke(cli, ['part', 'list'])
        assert result.exit_code == 0

    def test_part_info_valid(self):
        """Test part info with valid name"""
        result = self.runner.invoke(
            cli,
            ['part', 'info', '--name', 'SomeBox']
        )
        assert result.exit_code == 0

    def test_part_info_empty_name_rejected(self):
        """Test part info rejects empty name"""
        result = self.runner.invoke(
            cli,
            ['part', 'info', '--name', '']
        )
        assert result.exit_code != 0


class TestSketchCommands:
    """Tests for sketch command group"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_sketch_create_valid(self):
        """Test sketch create with valid name"""
        result = self.runner.invoke(
            cli,
            ['sketch', 'create', '--name', 'MySketch']
        )
        assert result.exit_code == 0
        assert 'MySketch' in result.output

    def test_sketch_create_empty_name_rejected(self):
        """Test sketch create rejects empty name"""
        result = self.runner.invoke(
            cli,
            ['sketch', 'create', '--name', '']
        )
        assert result.exit_code != 0

    def test_sketch_create_all_planes(self):
        """Test sketch create accepts all valid planes"""
        for plane in ['XY', 'XZ', 'YZ']:
            result = self.runner.invoke(
                cli,
                ['sketch', 'create', '--name', f'Sketch_{plane}', '--plane', plane]
            )
            assert result.exit_code == 0, f"Failed for plane {plane}: {result.output}"


class TestDocumentCommands:
    """Tests for document command group"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_document_create(self):
        """Test document create"""
        result = self.runner.invoke(
            cli,
            ['document', 'create', '--name', 'MyDoc']
        )
        assert result.exit_code == 0

    def test_document_list(self):
        """Test document list"""
        result = self.runner.invoke(cli, ['document', 'list'])
        assert result.exit_code == 0


class TestGlobalFlags:
    """Tests for global flag placement and output formats"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_format_global_flag_before_command(self):
        """Test --format global flag works before subcommand"""
        result = self.runner.invoke(
            cli,
            ['--format', 'json', 'info', 'status']
        )
        assert result.exit_code == 0
        # Should be valid JSON
        import json
        try:
            json.loads(result.output)
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {result.output}")

    def test_format_json_modules(self):
        """Test --format json info modules"""
        result = self.runner.invoke(
            cli,
            ['--format', 'json', 'info', 'modules']
        )
        assert result.exit_code == 0
        import json
        try:
            data = json.loads(result.output)
            assert 'core' in data.get('data', {})
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {result.output}")

    def test_format_text_output(self):
        """Test --format text produces human-readable output"""
        result = self.runner.invoke(
            cli,
            ['--format', 'text', 'info', 'status']
        )
        assert result.exit_code == 0

    def test_format_table_output(self):
        """Test --format table produces table output"""
        result = self.runner.invoke(
            cli,
            ['--format', 'table', 'part', 'list']
        )
        assert result.exit_code == 0

    def test_help_shows_global_flag_placement_note(self):
        """Test --help documents global flag placement"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert '全局选项' in result.output or 'Global options' in result.output
        assert 'subcommand' in result.output.lower() or '子命令' in result.output


class TestDraftCommands:
    """Tests for draft command group"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_draft_line_create_valid(self):
        """Test draft line create with valid name"""
        result = self.runner.invoke(
            cli,
            ['draft', 'line', '--name', 'MyLine', '--x1', '0', '--y1', '0', '--x2', '10', '--y2', '10']
        )
        assert result.exit_code == 0

    def test_draft_line_empty_name_rejected(self):
        """Test draft line rejects empty name"""
        result = self.runner.invoke(
            cli,
            ['draft', 'line', '--name', '']
        )
        assert result.exit_code != 0

    def test_draft_circle_create(self):
        """Test draft circle create"""
        result = self.runner.invoke(
            cli,
            ['draft', 'circle', '--name', 'MyCircle', '--radius', '3']
        )
        assert result.exit_code == 0


class TestExportCommands:
    """Tests for export command group"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_export_stl(self):
        """Test export stl command"""
        result = self.runner.invoke(cli, ['export', 'stl', '--help'])
        assert result.exit_code == 0

    def test_export_step(self):
        """Test export step command"""
        result = self.runner.invoke(cli, ['export', 'step', '--help'])
        assert result.exit_code == 0

    def test_export_obj(self):
        """Test export obj command"""
        result = self.runner.invoke(cli, ['export', 'obj', '--help'])
        assert result.exit_code == 0


class TestInfoCommands:
    """Tests for info command group"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_info_status_json(self):
        """Test info status returns expected fields"""
        result = self.runner.invoke(
            cli,
            ['--format', 'json', 'info', 'status']
        )
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert 'freecad_available' in data.get('data', {})

    def test_info_modules_returns_module_list(self):
        """Test info modules returns module list"""
        result = self.runner.invoke(
            cli,
            ['--format', 'json', 'info', 'modules']
        )
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert 'core' in data.get('data', {})


class TestNonEmptyStringValidator:
    """Tests for NonEmptyString validator (decorators.py)"""

    def setup_method(self):
        self.runner = CliRunner()

    def test_whitespace_only_name_rejected(self):
        """Test that whitespace-only names are rejected"""
        result = self.runner.invoke(
            cli,
            ['part', 'create', '--name', '   ', '--type', 'Box']
        )
        # NonEmptyString checks strip() == "" so whitespace-only should also fail
        # Note: depends on implementation — adjust if trim behavior differs
        assert result.exit_code != 0

    def test_valid_name_accepted(self):
        """Test that valid names are accepted across commands"""
        commands = [
            ['part', 'create', '--name', 'ValidBox', '--type', 'Box'],
            ['sketch', 'create', '--name', 'ValidSketch'],
            ['document', 'create', '--name', 'ValidDoc'],
        ]
        for cmd in commands:
            result = self.runner.invoke(cli, cmd)
            assert result.exit_code == 0, f"Failed for {' '.join(cmd)}: {result.output}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
