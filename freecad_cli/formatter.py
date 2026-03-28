# -*- coding: utf-8 -*-
"""
JSON Output Formatter for AI-friendly responses
================================================

Provides structured output formatting for AI consumption,
including JSON, YAML, and pretty-printed text formats.
"""

import json
import sys
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class OutputFormatter:
    """Output formatter - supports multiple output formats"""

    def __init__(self, output_format: str = "json", pretty: bool = True):
        """
        Initialize formatter

        Args:
            output_format: Output format (json/yaml/text/table)
            pretty: Whether to beautify output
        """
        self.output_format = output_format
        self.pretty = pretty
        self._indent = 2 if pretty else None

    def format(self, data: Any, status: str = "success",
               message: str = "", metadata: Optional[Dict] = None) -> str:
        """
        Format output data

        Args:
            data: Data to format
            status: Operation status (success/error/warning)
            message: Additional message
            metadata: Metadata

        Returns:
            Formatted string
        """
        wrapper = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "data": data,
        }

        if metadata:
            wrapper["metadata"] = metadata

        if self.output_format == "json":
            return self._format_json(wrapper)
        elif self.output_format == "yaml":
            return self._format_yaml(wrapper)
        elif self.output_format == "text":
            return self._format_text(wrapper)
        elif self.output_format == "table":
            return self._format_table(data)
        else:
            return str(data)

    def _format_json(self, data: Dict) -> str:
        """JSON formatting"""
        if self.pretty:
            return json.dumps(data, indent=self._indent, ensure_ascii=False, default=str)
        return json.dumps(data, ensure_ascii=False, default=str)

    def _format_yaml(self, data: Dict) -> str:
        """YAML formatting (simplified implementation)"""
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def _format_text(self, data: Dict) -> str:
        """Plain text formatting"""
        lines = [f"Status: {data['status']}", f"Time: {data['timestamp']}"]
        if data.get("message"):
            lines.append(f"Message: {data['message']}")
        lines.append(f"\nData:")
        lines.append(self._dict_to_text(data.get("data", {}), indent=0))
        return "\n".join(lines)

    def _format_table(self, data: Any) -> str:
        """Table formatting"""
        if isinstance(data, list):
            if not data:
                return ""
            if data and isinstance(data[0], dict):
                keys = list(data[0].keys())
                col_widths = {k: len(k) for k in keys}

                for item in data:
                    for k in keys:
                        val_len = len(str(item.get(k, "")))
                        col_widths[k] = max(col_widths[k], val_len)

                header = " | ".join(k.ljust(col_widths[k]) for k in keys)
                separator = "-+-".join("-" * col_widths[k] for k in keys)
                rows = []
                for item in data:
                    row = " | ".join(str(item.get(k, "")).ljust(col_widths[k]) for k in keys)
                    rows.append(row)

                return "\n".join([header, separator] + rows)
        return str(data)

    def _dict_to_text(self, data: Any, indent: int = 0) -> str:
        """Recursively convert to indented text"""
        lines = []
        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(self._dict_to_text(value, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                lines.append(f"{prefix}[{i}]:")
                lines.append(self._dict_to_text(item, indent + 1))
        else:
            lines.append(f"{prefix}{data}")

        return "\n".join(lines)

    def error(self, message: str, error_details: Any = None) -> str:
        """Format error output"""
        data = {
            "error": message,
            "details": error_details
        }
        return self.format(data, status="error", message=message)

    def success(self, data: Any, message: str = "") -> str:
        """Format success output"""
        return self.format(data, status="success", message=message)

    def warning(self, data: Any, message: str = "") -> str:
        """Format warning output"""
        return self.format(data, status="warning", message=message)


def get_formatter(format_type: str = "json", pretty: bool = True) -> OutputFormatter:
    """
    Get formatter instance

    Args:
        format_type: Output format type
        pretty: Whether to beautify output

    Returns:
        OutputFormatter instance
    """
    return OutputFormatter(output_format=format_type, pretty=pretty)
