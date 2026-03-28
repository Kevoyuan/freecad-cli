# -*- coding: utf-8 -*-
"""
Unit Tests for OutputFormatter (formatter.py)
"""

import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from freecad_cli.formatter import OutputFormatter, get_formatter


class TestJSONFormatting:
    """Tests for JSON output format"""

    def setup_method(self):
        self.fmt = OutputFormatter(output_format="json", pretty=True)

    def test_json_success(self):
        result = self.fmt.format({"key": "value"}, status="success", message="ok")
        data = json.loads(result)
        assert data["status"] == "success"
        assert data["message"] == "ok"
        assert data["data"]["key"] == "value"

    def test_json_pretty(self):
        result = self.fmt.format({"a": 1})
        # Pretty output contains newlines and indentation
        assert "\n" in result or " " in result

    def test_json_no_pretty(self):
        fmt = OutputFormatter(output_format="json", pretty=False)
        result = fmt.format({"a": 1})
        # Compact JSON has no extra whitespace
        parsed = json.loads(result)
        assert parsed["data"]["a"] == 1

    def test_json_error(self):
        result = self.fmt.error("something went wrong", {"code": 500})
        data = json.loads(result)
        assert data["status"] == "error"
        assert "something went wrong" in result

    def test_json_unicode(self):
        result = self.fmt.format({"name": "中文名称", "emoji": "🎂"})
        data = json.loads(result)
        assert data["data"]["name"] == "中文名称"

    def test_json_special_chars(self):
        result = self.fmt.format({"msg": "line1\nline2\ttab"})
        data = json.loads(result)
        assert "line1" in data["data"]["msg"]

    def test_json_timestamp_present(self):
        result = self.fmt.format({"x": 1})
        data = json.loads(result)
        assert "timestamp" in data

    def test_json_metadata(self):
        result = self.fmt.format({"x": 1}, metadata={"version": "1.0"})
        data = json.loads(result)
        assert data.get("metadata", {}).get("version") == "1.0"


class TestYAMLFormatting:
    """Tests for YAML output format"""

    def setup_method(self):
        self.fmt = OutputFormatter(output_format="yaml", pretty=True)

    def test_yaml_success(self):
        result = self.fmt.format({"key": "value"})
        assert "key: value" in result

    def test_yaml_nested(self):
        result = self.fmt.format({"outer": {"inner": 42}})
        # Data is wrapped in {"status":..., "data": {"outer":...}}, so outer is indented
        assert "outer" in result
        assert "inner" in result

    def test_yaml_list(self):
        result = self.fmt.format({"items": ["a", "b"]})
        assert "items:" in result
        assert "a" in result

    def test_yaml_status_and_message(self):
        result = self.fmt.format({"x": 1}, status="success", message="it worked")
        assert "status: success" in result
        assert "message: it worked" in result


class TestTextFormatting:
    """Tests for plain text output format"""

    def setup_method(self):
        self.fmt = OutputFormatter(output_format="text", pretty=True)

    def test_text_includes_status(self):
        result = self.fmt.format({"key": "val"})
        assert "Status:" in result

    def test_text_includes_data(self):
        result = self.fmt.format({"key": "val"})
        assert "Data:" in result

    def test_text_nested_dict(self):
        result = self.fmt.format({"outer": {"inner": 1}})
        assert "outer" in result
        assert "inner" in result

    def test_text_empty_data(self):
        result = self.fmt.format(None)
        assert "Data:" in result

    def test_text_message(self):
        result = self.fmt.format({"x": 1}, message="hello")
        assert "hello" in result


class TestTableFormatting:
    """Tests for table output format"""

    def setup_method(self):
        self.fmt = OutputFormatter(output_format="table", pretty=True)

    def test_table_header(self):
        result = self.fmt.format([
            {"name": "Box1", "type": "Box"},
            {"name": "Box2", "type": "Box"},
        ])
        assert "name" in result
        assert "type" in result

    def test_table_rows(self):
        result = self.fmt.format([
            {"name": "Box1", "type": "Box"},
        ])
        assert "Box1" in result
        assert "Box" in result

    def test_table_single_object(self):
        result = self.fmt.format({"name": "Solo", "type": "Cylinder"})
        # Single dict not treated as table rows — returns string
        assert "Solo" in result

    def test_table_empty_list(self):
        result = self.fmt.format([])
        # Empty list should return empty or handle gracefully
        assert result == ""

    def test_table_column_alignment(self):
        result = self.fmt.format([
            {"name": "A", "value": 1},
            {"name": "LongName", "value": 2},
        ])
        # Longer column value should widen the column for shorter ones too
        assert "name" in result
        assert "A" in result


class TestGetFormatter:
    """Tests for get_formatter factory function"""

    def test_json_formatter(self):
        fmt = get_formatter("json")
        assert fmt.output_format == "json"

    def test_yaml_formatter(self):
        fmt = get_formatter("yaml")
        assert fmt.output_format == "yaml"

    def test_text_formatter(self):
        fmt = get_formatter("text")
        assert fmt.output_format == "text"

    def test_table_formatter(self):
        fmt = get_formatter("table")
        assert fmt.output_format == "table"

    def test_pretty_default(self):
        fmt = get_formatter("json")
        assert fmt.pretty is True


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def setup_method(self):
        self.fmt = OutputFormatter(output_format="json", pretty=True)

    def test_unknown_format_fallback(self):
        fmt = OutputFormatter(output_format="unknown", pretty=True)
        result = fmt.format({"x": 1})
        assert "x" in result

    def test_none_data(self):
        result = self.fmt.format(None)
        data = json.loads(result)
        assert data["data"] is None

    def test_list_as_data(self):
        result = self.fmt.format([1, 2, 3])
        data = json.loads(result)
        assert data["data"] == [1, 2, 3]

    def test_boolean_data(self):
        result = self.fmt.format(True)
        data = json.loads(result)
        assert data["data"] is True

    def test_numeric_data(self):
        result = self.fmt.format(42)
        data = json.loads(result)
        assert data["data"] == 42


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
