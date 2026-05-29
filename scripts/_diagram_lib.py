"""Shared helpers for generating Excalidraw JSON in the proper schema.

Used by build_event_diagram.py and the three build_handling_*.py scripts.
"""

import json
import random
import time

STROKE = "#1e1e1e"
FILL = "#ffffff"
NOW = int(time.time() * 1000)


def seeded_rng(seed=42):
    return random.Random(seed)


def defaults(rng):
    return {
        "angle": 0,
        "strokeColor": STROKE,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": rng.randint(1, 2**31),
        "version": 1,
        "versionNonce": rng.randint(1, 2**31),
        "isDeleted": False,
        "boundElements": [],
        "updated": NOW,
        "link": None,
        "locked": False,
    }


def text_size(text, font):
    lines = text.split("\n")
    char_w = font * 0.6
    line_h = font * 1.25
    w = max((len(l) for l in lines), default=1) * char_w
    h = len(lines) * line_h
    return w, h


def text_el(rng, tid, text, font, container_id=None, cx=None, cy=None, x=None, y=None, color=STROKE):
    w, h = text_size(text, font)
    if container_id is not None:
        tx = cx - w / 2
        ty = cy - h / 2
    else:
        tx = x
        ty = y
    return {
        **defaults(rng),
        "id": tid,
        "type": "text",
        "x": tx,
        "y": ty,
        "width": w,
        "height": h,
        "strokeColor": color,
        "text": text,
        "originalText": text,
        "fontSize": font,
        "fontFamily": 1,
        "textAlign": "center" if container_id else "left",
        "verticalAlign": "middle" if container_id else "top",
        "lineHeight": 1.25,
        "containerId": container_id,
        "autoResize": True,
    }


def shape(rng, eid, kind, x, y, w, h, label=None, label_font=15, rounded=False):
    el = {
        **defaults(rng),
        "id": eid,
        "type": kind,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "backgroundColor": FILL,
        "fillStyle": "solid",
    }
    if rounded:
        el["roundness"] = {"type": 3}
    out = [el]
    if label:
        tid = f"t_{eid}"
        cx, cy = x + w / 2, y + h / 2
        tel = text_el(rng, tid, label, label_font, container_id=eid, cx=cx, cy=cy)
        el["boundElements"] = [{"id": tid, "type": "text"}]
        out.append(tel)
    return out


def arrow(rng, eid, x, y, points, dashed=False, label=None, label_font=11, width=1.5):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    el = {
        **defaults(rng),
        "id": eid,
        "type": "arrow",
        "x": x,
        "y": y,
        "width": w if w else 1,
        "height": h if h else 1,
        "strokeWidth": width,
        "points": [list(p) for p in points],
        "lastCommittedPoint": None,
        "startArrowhead": None,
        "endArrowhead": "arrow",
        "elbowed": False,
        "startBinding": None,
        "endBinding": None,
    }
    if dashed:
        el["strokeStyle"] = "dashed"
    out = [el]
    if label:
        tid = f"t_{eid}"
        # Place label at midpoint of the first segment, nudged perpendicular
        mx = x + (points[0][0] + points[-1][0]) / 2
        my = y + (points[0][1] + points[-1][1]) / 2
        tel = text_el(rng, tid, label, label_font, container_id=eid, cx=mx, cy=my - 6)
        el["boundElements"] = [{"id": tid, "type": "text"}]
        out.append(tel)
    return out


def envelope(elements):
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": 20,
            "gridStep": 5,
            "gridModeEnabled": False,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }


def write_doc(path, elements):
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(envelope(elements), ensure_ascii=False, indent=1))
    return p.stat().st_size
