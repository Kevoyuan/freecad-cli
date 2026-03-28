# -*- coding: utf-8 -*-
"""Path module (CAM machining) - path_create_job, path_add_operation, path_export_gcode"""

from typing import Any, Dict, Optional


def _path_create_job(self, name: str, base_name: str) -> Dict[str, Any]:
    """Create machining job"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _path_mock(self, "Path", name, "Job", {"base": base_name})

    doc = self.get_document()

    try:
        base = doc.getObject(base_name)
        if not base:
            return {"success": False, "error": f"Base object not found: {base_name}"}

        job = doc.addObject("Path::Job", name)
        job.Base = base

        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Job",
            "base": base_name,
            "label": job.Label
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _path_add_operation(self, job_name: str, operation_type: str,
                        parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Add machining operation"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "job": job_name,
            "operation_type": operation_type,
            "parameters": parameters,
            "mock": True
        }

    doc = self.get_document()

    try:
        job = doc.getObject(job_name)
        if not job:
            return {"success": False, "error": f"Job not found: {job_name}"}

        operation = doc.addObject("Path::Feature", f"Op_{operation_type}")
        job.addObject(operation)

        doc.recompute()

        return {
            "success": True,
            "name": operation.Name,
            "type": "Operation",
            "operation_type": operation_type,
            "job": job_name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _path_export_gcode(self, job_name: str, filepath: str,
                       post_processor: str = "linuxcnc") -> Dict[str, Any]:
    """Export G-code"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE
    _freecad_module = _fi._freecad_module

    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "job": job_name,
            "filepath": filepath,
            "post_processor": post_processor,
            "mock": True
        }

    doc = self.get_document()

    try:
        job = doc.getObject(job_name)
        if not job:
            return {"success": False, "error": f"Job not found: {job_name}"}

        _freecad_module.export([job], filepath)

        return {
            "success": True,
            "job": job_name,
            "filepath": filepath,
            "post_processor": post_processor
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _path_mock(self, category: str, name: str,
               sub_type: str = "", params: Any = None) -> Dict[str, Any]:
    """Return mock result"""
    from ._mock import get_mock_state
    get_mock_state().add(category, name, sub_type, params)
    return {
        "success": True,
        "mock": True,
        "category": category,
        "name": name,
        "type": sub_type,
        "params": params,
        "message": "FreeCAD not installed - returning mock data"
    }
