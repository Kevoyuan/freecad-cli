# -*- coding: utf-8 -*-
"""PartDesign module - create_partdesign_body, create_pad, create_pocket,
create_hole, create_groove, create_revolution, create_fillet, create_chamfer"""

from typing import Any, Dict, Optional, Tuple


def _partdesign_body(self, name: str) -> Dict[str, Any]:
    """Create PartDesign Body"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _pd_mock(self, "PartDesign", name, "Body", {})

    doc = self.get_document()

    try:
        obj = doc.addObject("PartDesign::Body", name)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Body",
            "label": obj.Label
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _partdesign_pad(self, name: str, body_name: str,
                    sketch_name: str, length: float = 10.0,
                    direction: str = "Normal") -> Dict[str, Any]:
    """Create Pad (extrusion)"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _pd_mock(self, "Pad", name, "Pad",
                        {"body": body_name, "sketch": sketch_name,
                         "length": length, "direction": direction})

    doc = self.get_document()

    try:
        body = doc.getObject(body_name)
        sketch = doc.getObject(sketch_name)

        if not body:
            return {"success": False, "error": f"Body not found: {body_name}"}
        if not sketch:
            return {"success": False, "error": f"Sketch not found: {sketch_name}"}

        pad = doc.addObject("PartDesign::Pad", name)
        pad.Profile = sketch
        pad.Length = length

        if direction == "Reversed":
            pad.Direction = (-1, 0, 0)
        elif direction == "Double":
            pad.Length2 = length

        body.addObject(pad)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Pad",
            "body": body_name,
            "sketch": sketch_name,
            "length": length
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _partdesign_pocket(self, name: str, body_name: str,
                       sketch_name: str, length: float = 10.0,
                       pocket_type: str = "Through") -> Dict[str, Any]:
    """Create Pocket (cutout)"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _pd_mock(self, "Pocket", name, "Pocket",
                        {"body": body_name, "sketch": sketch_name,
                         "length": length, "type": pocket_type})

    doc = self.get_document()

    try:
        body = doc.getObject(body_name)
        sketch = doc.getObject(sketch_name)

        if not body:
            return {"success": False, "error": f"Body not found: {body_name}"}
        if not sketch:
            return {"success": False, "error": f"Sketch not found: {sketch_name}"}

        pocket = doc.addObject("PartDesign::Pocket", name)
        pocket.Profile = sketch
        pocket.Length = length

        if pocket_type == "Through":
            pocket.Reversed = True
        elif pocket_type == "UpToFirst":
            pocket.Type = 1

        body.addObject(pocket)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Pocket",
            "body": body_name,
            "sketch": sketch_name,
            "length": length,
            "pocket_type": pocket_type
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _partdesign_hole(self, name: str, body_name: str,
                     diameter: float = 5.0, depth: float = 10.0,
                     position: Optional[Tuple[float, float, float]] = None) -> Dict[str, Any]:
    """Create hole"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _pd_mock(self, "Hole", name, "Hole",
                         {"body": body_name, "diameter": diameter,
                          "depth": depth, "position": position})

    doc = self.get_document()

    try:
        body = doc.getObject(body_name)
        if not body:
            return {"success": False, "error": f"Body not found: {body_name}"}

        hole = doc.addObject("PartDesign::Hole", name)
        hole.Diameter = diameter
        hole.Depth = depth

        if position:
            hole.Placement.Base.x = position[0]
            hole.Placement.Base.y = position[1]
            hole.Placement.Base.z = position[2]

        body.addObject(hole)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Hole",
            "body": body_name,
            "diameter": diameter,
            "depth": depth
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _partdesign_groove(self, name: str, body_name: str,
                       angle: float = 360.0, radius: float = 5.0) -> Dict[str, Any]:
    """Create Groove (rotational cutout)"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _pd_mock(self, "Groove", name, "Groove",
                        {"body": body_name, "angle": angle, "radius": radius})

    doc = self.get_document()

    try:
        body = doc.getObject(body_name)
        if not body:
            return {"success": False, "error": f"Body not found: {body_name}"}

        groove = doc.addObject("PartDesign::Groove", name)
        groove.Angle = angle
        groove.Radius = radius

        body.addObject(groove)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Groove",
            "body": body_name,
            "angle": angle,
            "radius": radius
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _partdesign_revolution(self, name: str, body_name: str,
                           sketch_name: str, angle: float = 360.0,
                           axis: Optional[Tuple[int, int, int]] = None) -> Dict[str, Any]:
    """Create Revolution"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _pd_mock(self, "Revolution", name, "Revolution",
                        {"body": body_name, "sketch": sketch_name,
                         "angle": angle, "axis": axis})

    doc = self.get_document()

    try:
        body = doc.getObject(body_name)
        sketch = doc.getObject(sketch_name)

        if not body:
            return {"success": False, "error": f"Body not found: {body_name}"}
        if not sketch:
            return {"success": False, "error": f"Sketch not found: {sketch_name}"}

        revolution = doc.addObject("PartDesign::Revolution", name)
        revolution.Profile = sketch
        revolution.Angle = angle

        if axis:
            revolution.ReferenceAxis = axis

        body.addObject(revolution)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Revolution",
            "body": body_name,
            "sketch": sketch_name,
            "angle": angle
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _partdesign_fillet(self, name: str, body_name: str,
                       edge_radius: float = 2.0) -> Dict[str, Any]:
    """Create Fillet"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _pd_mock(self, "Fillet", name, "Fillet",
                        {"body": body_name, "radius": edge_radius})

    doc = self.get_document()

    try:
        body = doc.getObject(body_name)
        if not body:
            return {"success": False, "error": f"Body not found: {body_name}"}

        fillet = doc.addObject("PartDesign::Fillet", name)
        fillet.Radius = edge_radius

        body.addObject(fillet)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Fillet",
            "body": body_name,
            "radius": edge_radius
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _partdesign_chamfer(self, name: str, body_name: str,
                        chamfer_size: float = 1.0) -> Dict[str, Any]:
    """Create Chamfer"""
    import freecad_cli.freecad_integration as _fi
    FREECAD_AVAILABLE = _fi.FREECAD_AVAILABLE

    if not FREECAD_AVAILABLE:
        return _pd_mock(self, "Chamfer", name, "Chamfer",
                        {"body": body_name, "size": chamfer_size})

    doc = self.get_document()

    try:
        body = doc.getObject(body_name)
        if not body:
            return {"success": False, "error": f"Body not found: {body_name}"}

        chamfer = doc.addObject("PartDesign::Chamfer", name)
        chamfer.Size = chamfer_size

        body.addObject(chamfer)
        doc.recompute()

        return {
            "success": True,
            "name": name,
            "type": "Chamfer",
            "body": body_name,
            "size": chamfer_size
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _pd_mock(self, category: str, name: str,
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
