"""
Build Excalidraw JSON for the 4 M1 diagrams. Each function emits a JSON
string suitable for the `elements` parameter of the Excalidraw MCP
`create_view` tool. Saves to `diagrams/<name>.excalidraw.json`.

Workflow:
  1. python build_excalidraw_diagrams.py
  2. Read each JSON file, pass to create_view(elements=<content>)
  3. User opens the rendered diagram in excalidraw.com and exports PNG to
     diagrams/<name>.png (the .json file stays for reproducibility)
"""
from __future__ import annotations
import json
from pathlib import Path

DIAGRAMS = Path(__file__).parent / "diagrams"
DIAGRAMS.mkdir(exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
# Excalidraw element helpers
# ──────────────────────────────────────────────────────────────────────────────

def camera(x: int, y: int, width: int = 1600, height: int = 1200) -> dict:
    return {"type": "cameraUpdate", "x": x, "y": y, "width": width, "height": height}


def event_circle(eid: str, cx: int, cy: int, label: str, r: int = 75) -> dict:
    """Event bubble: circle with centered label. cx,cy = center coords."""
    return {
        "type": "ellipse",
        "id": eid,
        "x": cx - r,
        "y": cy - r,
        "width": 2 * r,
        "height": 2 * r,
        "backgroundColor": "#dbe4ff",
        "fillStyle": "solid",
        "strokeColor": "#4a9eed",
        "strokeWidth": 2,
        "label": {"text": label, "fontSize": 20},
    }


def self_loop(eid: str, cx: int, cy: int, r: int = 75, color: str = "#1e3a8a") -> dict:
    """Self-loop arrow on top of a circle (upside-down U)."""
    # Start at top-right of circle, go up, left, down to top-left
    start_x = cx + int(r * 0.35)
    start_y = cy - int(r * 0.94)
    up = -45
    over = -int(r * 0.7)  # negative = leftward
    return {
        "type": "arrow",
        "id": eid,
        "x": start_x,
        "y": start_y,
        "width": abs(over),
        "height": abs(up),
        "points": [[0, 0], [0, up], [over, up], [over, 0]],
        "strokeColor": color,
        "strokeWidth": 2,
        "endArrowhead": "arrow",
    }


def zigzag_in(eid: str, cx: int, cy: int, r: int = 75, color: str = "#1e3a8a") -> dict:
    """Squiggly arrow coming in from upper-left (self-generating marker)."""
    # End at upper-left edge of circle (approx 135° on the circle)
    import math
    end_x = cx + int(r * math.cos(math.radians(135)))
    end_y = cy + int(r * math.sin(math.radians(-135)))  # y inverted in screen coords
    # Start ~120px to upper-left of end
    sx = end_x - 100
    sy = end_y - 70
    # Zigzag path relative to (sx, sy)
    pts = [
        [0, 0],
        [18, 12],
        [36, -2],
        [54, 14],
        [72, 0],
        [end_x - sx, end_y - sy],
    ]
    return {
        "type": "arrow",
        "id": eid,
        "x": sx,
        "y": sy,
        "width": end_x - sx,
        "height": end_y - sy,
        "points": pts,
        "strokeColor": color,
        "strokeWidth": 2,
        "endArrowhead": "arrow",
    }


def connect(eid: str, from_id: str, to_id: str,
            from_fp: list[float] = (0.5, 1.0),
            to_fp: list[float] = (0.5, 0.0),
            color: str = "#475569", style: str = "solid", lw: int = 2) -> dict:
    """Bound arrow between two elements at given anchor fractions.
    fixedPoint: top=[0.5,0] right=[1,0.5] bottom=[0.5,1] left=[0,0.5]."""
    return {
        "type": "arrow",
        "id": eid,
        "x": 0, "y": 0, "width": 0, "height": 0,
        "points": [[0, 0], [100, 0]],  # placeholder; bindings drive the actual line
        "strokeColor": color,
        "strokeWidth": lw,
        "strokeStyle": style,
        "endArrowhead": "arrow",
        "startBinding": {"elementId": from_id, "fixedPoint": list(from_fp)},
        "endBinding": {"elementId": to_id, "fixedPoint": list(to_fp)},
    }


def text(tid: str, x: int, y: int, txt: str, size: int = 28, color: str = "#1e1e1e") -> dict:
    return {"type": "text", "id": tid, "x": x, "y": y, "text": txt, "fontSize": size, "strokeColor": color}


# ──────────────────────────────────────────────────────────────────────────────
# Diagram 1 — Event diagram
# ──────────────────────────────────────────────────────────────────────────────

def build_event_diagram() -> list[dict]:
    # Event positions: (cx, cy, self_init, self_loop, label)
    events = [
        ("aFG",      215, 145,  True,  True,  "Arrival\nFG"),
        ("aCoup",    495, 145,  True,  True,  "Arrival\nCouple"),
        ("aSing",    775, 145,  True,  True,  "Arrival\nSingle"),
        ("entry",    495, 375,  False, False, "EndEntry"),
        ("ssMain",   125, 585,  True,  False, "ShowStart\nMain"),
        ("seMain",   305, 585,  False, False, "ShowEnd\nMain"),
        ("ft10",     495, 585,  False, False, "Farthest\nTen"),
        ("ssSide",   705, 585,  True,  False, "ShowStart\nSide"),
        ("seSide",   885, 585,  False, False, "ShowEnd\nSide"),
        ("eDJ",      125, 825,  False, True,  "EndDJ"),
        ("ePhoto",   265, 825,  False, True,  "EndPhoto"),
        ("eCharge",  405, 825,  False, True,  "EndCharge"),
        ("eMerch",   545, 825,  False, True,  "EndMerch"),
        ("eBody",    685, 825,  False, True,  "EndBody\nArt"),
        ("eFood",    825, 825,  False, True,  "EndFood"),
        ("qAb",      985, 665,  False, False, "Queue\nAbandon"),
        ("eDay",    1165, 375,  True,  True,  "EndOfDay"),
        ("eStay",   1165, 825,  False, False, "EndOfStay"),
    ]

    R = 75
    els: list[dict] = []
    els.append(camera(x=-50, y=-30, width=1600, height=1200))
    els.append(text("title", 480, 10, "Queuechella — תרשים אירועים", size=32))

    # Circles + zigzag + self-loop per event
    for eid, cx, cy, is_zz, is_sl, label in events:
        els.append(event_circle(eid, cx, cy, label, r=R))
        if is_zz:
            els.append(zigzag_in(f"zz_{eid}", cx, cy, r=R))
        if is_sl:
            els.append(self_loop(f"sl_{eid}", cx, cy, r=R))

    # ── Cross-event arrows ────────────────────────────────────────────────────
    aid = 0
    def A(*args, **kwargs):
        nonlocal aid
        aid += 1
        return connect(f"a{aid}", *args, **kwargs)

    # Arrivals → EndEntry
    els.append(A("aFG",   "entry", from_fp=(0.5, 1.0), to_fp=(0.15, 0.0)))
    els.append(A("aCoup", "entry", from_fp=(0.5, 1.0), to_fp=(0.5,  0.0)))
    els.append(A("aSing", "entry", from_fp=(0.5, 1.0), to_fp=(0.85, 0.0)))

    # EndEntry → first activities (light gray = entity transition)
    light = {"color": "#94a3b8", "lw": 1}
    for tgt, fp in [("ssMain", (0.5, 0.0)), ("ssSide", (0.5, 0.0)), ("eDJ", (0.5, 0.0)),
                    ("ePhoto", (0.5, 0.0)), ("eCharge", (0.5, 0.0)),
                    ("eMerch", (0.5, 0.0)), ("eBody", (0.5, 0.0))]:
        els.append(A("entry", tgt, from_fp=(0.5, 1.0), to_fp=fp, **light))
    # EndEntry → QueueAbandon
    els.append(A("entry", "qAb", from_fp=(1.0, 0.5), to_fp=(0.5, 0.0), **light))

    # ShowStart ↔ ShowEnd cycle
    els.append(A("ssMain", "seMain", from_fp=(1.0, 0.5), to_fp=(0.0, 0.5)))
    els.append(A("seMain", "ssMain", from_fp=(0.0, 1.0), to_fp=(1.0, 1.0)))  # back loop
    els.append(A("ssSide", "seSide", from_fp=(1.0, 0.5), to_fp=(0.0, 0.5)))
    els.append(A("seSide", "ssSide", from_fp=(0.0, 1.0), to_fp=(1.0, 1.0)))

    # ShowStartMain → FarthestTen
    els.append(A("ssMain", "ft10", from_fp=(1.0, 0.3), to_fp=(0.0, 0.3)))

    # FarthestTen → activity ends (entity leaves stage)
    for tgt in ["ePhoto", "eMerch", "eBody"]:
        els.append(A("ft10", tgt, from_fp=(0.5, 1.0), to_fp=(0.5, 0.0), **light))

    # ShowEnd → activity ends + EndOfStay (post-show transitions)
    for src in ["seMain", "seSide"]:
        els.append(A(src, "eDJ",  from_fp=(0.5, 1.0), to_fp=(0.5, 0.0), **light))
        els.append(A(src, "eStay", from_fp=(1.0, 0.7), to_fp=(0.0, 0.3), **light))

    # Activity ends → EndOfStay (itinerary complete)
    for src in ["eDJ", "ePhoto", "eCharge", "eMerch", "eBody", "eFood"]:
        els.append(A(src, "eStay", from_fp=(1.0, 0.5), to_fp=(0.0, 0.5), **light))

    # Activity ends ↔ QueueAbandon (purple = queue interaction)
    queue = {"color": "#8b5cf6", "lw": 1}
    for src in ["eDJ", "ePhoto", "eCharge", "eMerch", "eBody", "eFood"]:
        els.append(A(src, "qAb", from_fp=(0.7, 0.0), to_fp=(0.3, 1.0), **queue))

    # EndOfDay → EndOfStay (forced exit)
    els.append(A("eDay", "eStay", from_fp=(0.5, 1.0), to_fp=(0.5, 0.0)))

    # EndOfDay → fresh arrivals (Day 2) — orange dashed
    day2 = {"color": "#f97316", "lw": 2, "style": "dashed"}
    els.append(A("eDay", "aCoup", from_fp=(0.0, 0.3), to_fp=(1.0, 0.5), **day2))
    els.append(A("eDay", "aSing", from_fp=(0.0, 0.5), to_fp=(1.0, 0.7), **day2))

    return els


# ──────────────────────────────────────────────────────────────────────────────
# Convert simplified format → real Excalidraw file format
# (The simplified format works for create_view; excalidraw.com needs the real
# format with seed/versionNonce/roughness/etc. per element, label→bound-text
# pair conversion, and a wrapper with type/version/source/appState/files.)
# ──────────────────────────────────────────────────────────────────────────────

def to_excalidraw_file(simple_elements: list[dict]) -> dict:
    """Resolve bound arrows to actual coordinates as part of the conversion.
    Excalidraw stores arrow geometry in (x, y, width, height, points) and uses
    bindings only for drag-time attachment — it does NOT auto-compute geometry
    from bindings on file load. So we precompute the start/end points from each
    binding's fixedPoint fraction relative to its container's box."""
    import random, time
    rng = random.Random(42)  # deterministic seeds for diff-friendly output
    now_ms = int(time.time() * 1000)

    # Build a lookup of container element boxes for binding resolution.
    boxes: dict[str, tuple[float, float, float, float]] = {}
    for e in simple_elements:
        if e.get("type") in ("rectangle", "ellipse", "diamond"):
            boxes[e["id"]] = (e["x"], e["y"], e["width"], e["height"])

    def bind_to_point(binding: dict | None) -> tuple[float, float] | None:
        if not binding or binding.get("elementId") not in boxes:
            return None
        x, y, w, h = boxes[binding["elementId"]]
        fp = binding.get("fixedPoint", [0.5, 0.5])
        return (x + fp[0] * w, y + fp[1] * h)

    def common(eid: str) -> dict:
        return {
            "id": eid,
            "angle": 0,
            "strokeColor": "#1e1e1e",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": rng.randint(1, 2**31 - 1),
            "versionNonce": rng.randint(1, 2**31 - 1),
            "version": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": now_ms,
            "link": None,
            "locked": False,
            "index": None,
        }

    out: list[dict] = []
    for e in simple_elements:
        t = e.get("type")
        if t == "cameraUpdate":
            continue  # pseudo-element, not in real Excalidraw schema

        eid = e.get("id") or f"el_{len(out)}"
        full = {**common(eid)}
        # Copy element fields, drop the "label" key (handled separately below).
        for k, v in e.items():
            if k != "label":
                full[k] = v

        # Arrow-specific defaults + resolve bindings → actual coordinates
        if t == "arrow":
            full.setdefault("startArrowhead", None)
            full.setdefault("endArrowhead", "arrow")
            full.setdefault("elbowed", False)
            full.setdefault("lastCommittedPoint", None)
            # Augment bindings with focus/gap if missing
            for binding_key in ("startBinding", "endBinding"):
                b = full.get(binding_key)
                if b is not None:
                    b.setdefault("focus", 0.0)
                    b.setdefault("gap", 1)
            # If both bindings present, override placeholder geometry with
            # actual start/end coordinates computed from the bound boxes.
            sp = bind_to_point(full.get("startBinding"))
            ep = bind_to_point(full.get("endBinding"))
            if sp and ep:
                sx, sy = sp
                ex, ey = ep
                full["x"] = sx
                full["y"] = sy
                full["points"] = [[0, 0], [ex - sx, ey - sy]]
                full["width"] = abs(ex - sx)
                full["height"] = abs(ey - sy)

        # Shape with label → bound text element
        if "label" in e and t in ("rectangle", "ellipse", "diamond"):
            label = e["label"]
            text_id = f"{eid}__label"
            full["boundElements"] = [{"type": "text", "id": text_id}]
            out.append(full)
            font_size = label.get("fontSize", 20)
            text_el = {
                **common(text_id),
                "type": "text",
                "x": e["x"],
                "y": e["y"],
                "width": e["width"],
                "height": e["height"],
                "text": label["text"],
                "originalText": label["text"],
                "fontSize": font_size,
                "fontFamily": 5,  # Excalifont (default Excalidraw sans)
                "textAlign": "center",
                "verticalAlign": "middle",
                "containerId": eid,
                "lineHeight": 1.25,
                "baseline": int(font_size * 0.8),
                "autoResize": True,
            }
            out.append(text_el)
            continue

        # Standalone text
        if t == "text":
            full.setdefault("originalText", e.get("text", ""))
            full.setdefault("fontFamily", 5)
            full.setdefault("textAlign", "left")
            full.setdefault("verticalAlign", "top")
            full.setdefault("lineHeight", 1.25)
            full.setdefault("width", max(80, int(len(e.get("text", "")) * e.get("fontSize", 20) * 0.6)))
            full.setdefault("height", int(e.get("fontSize", 20) * 1.25))
            full.setdefault("baseline", int(e.get("fontSize", 20) * 0.8))
            full.setdefault("containerId", None)
            full.setdefault("autoResize", True)

        out.append(full)

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": out,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

DIAGRAM_BUILDERS = {
    "event_diagram": build_event_diagram,
}

if __name__ == "__main__":
    for name, builder in DIAGRAM_BUILDERS.items():
        elements = builder()
        # Simplified format (for create_view debugging / source of truth)
        simple_path = DIAGRAMS / f"{name}.simple.json"
        simple_path.write_text(json.dumps(elements, ensure_ascii=False, indent=1))
        # Real Excalidraw file format (for export_to_excalidraw / upload)
        real = to_excalidraw_file(elements)
        real_path = DIAGRAMS / f"{name}.excalidraw"
        real_path.write_text(json.dumps(real, ensure_ascii=False, indent=1))
        print(f"wrote {simple_path} ({len(elements)} simple elements)")
        print(f"wrote {real_path} ({len(real['elements'])} real elements)")
