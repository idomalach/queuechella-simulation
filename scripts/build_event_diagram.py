"""Build event_diagram.excalidraw in B&W banded layout.

Run: python3 scripts/build_event_diagram.py
Writes: diagrams/event_diagram.excalidraw (Excalidraw JSON, full schema).
"""

import json
import random
import time
from pathlib import Path

random.seed(42)
NOW = int(time.time() * 1000)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "diagrams" / "event_diagram.excalidraw"

STROKE = "#1e1e1e"
FILL = "#ffffff"


def _defaults():
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
        "seed": random.randint(1, 2**31),
        "version": 1,
        "versionNonce": random.randint(1, 2**31),
        "isDeleted": False,
        "boundElements": [],
        "updated": NOW,
        "link": None,
        "locked": False,
    }


def _text_size(text, font):
    lines = text.split("\n")
    char_w = font * 0.6
    line_h = font * 1.25
    w = max((len(l) for l in lines), default=1) * char_w
    h = len(lines) * line_h
    return w, h


def text_el(tid, text, font, container_id=None, cx=None, cy=None, x=None, y=None, color=STROKE):
    w, h = _text_size(text, font)
    if container_id is not None:
        tx = cx - w / 2
        ty = cy - h / 2
    else:
        tx = x
        ty = y
    return {
        **_defaults(),
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


def shape(eid, kind, x, y, w, h, label=None, label_font=15, rounded=False):
    el = {
        **_defaults(),
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
        tel = text_el(tid, label, label_font, container_id=eid, cx=cx, cy=cy)
        el["boundElements"] = [{"id": tid, "type": "text"}]
        out.append(tel)
    return out


def arrow(eid, x, y, points, dashed=False, label=None, label_font=11,
          start_id=None, start_pt=None, end_id=None, end_pt=None, width_override=None):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    el = {
        **_defaults(),
        "id": eid,
        "type": "arrow",
        "x": x,
        "y": y,
        "width": w if w else 1,
        "height": h if h else 1,
        "strokeWidth": width_override if width_override else 1.5,
        "points": [list(p) for p in points],
        "lastCommittedPoint": None,
        "startArrowhead": None,
        "endArrowhead": "arrow",
        "elbowed": False,
    }
    if dashed:
        el["strokeStyle"] = "dashed"
    if start_id and start_pt is not None:
        el["startBinding"] = {"elementId": start_id, "focus": 0, "gap": 4, "fixedPoint": list(start_pt)}
    else:
        el["startBinding"] = None
    if end_id and end_pt is not None:
        el["endBinding"] = {"elementId": end_id, "focus": 0, "gap": 4, "fixedPoint": list(end_pt)}
    else:
        el["endBinding"] = None
    out = [el]
    if label:
        tid = f"t_{eid}"
        mx = x + (points[0][0] + points[-1][0]) / 2
        my = y + (points[0][1] + points[-1][1]) / 2
        # nudge label up a bit so it sits above the arrow line
        tel = text_el(tid, label, label_font, container_id=eid, cx=mx, cy=my - 6)
        el["boundElements"] = [{"id": tid, "type": "text"}]
        out.append(tel)
    return out


elements = []

# ---- Title ----
elements.append(
    text_el("title", "Queuechella  -  תרשים אירועים", 26,
            x=370, y=15)
)

# ---- Row 1: Arrivals (y=75) + EndOfDay top-right ----
elements += shape("aFG", "ellipse", 100, 75, 110, 110, label="Arrival\nFG", label_font=15)
elements += shape("aCoup", "ellipse", 300, 75, 110, 110, label="Arrival\nCouple", label_font=15)
elements += shape("aSing", "ellipse", 500, 75, 110, 110, label="Arrival\nSingle", label_font=15)
elements += shape("eod", "ellipse", 820, 75, 110, 110, label="EndOfDay", label_font=15)

# Stochastic zigzag arrows above arrivals
for aid, ax in [("zzFG", 135), ("zzCp", 335), ("zzSg", 535)]:
    elements += arrow(aid, ax, 25,
                      [(0, 0), (10, 8), (20, -4), (30, 8), (40, 50)])

# ---- Row 2: Entry (y=240) ----
elements += shape("entry", "ellipse", 275, 240, 120, 120, label="End\nEntry", label_font=16)

# Arrival → Entry
elements += arrow("af_e", 190, 185, [(0, 0), (140, 55)])
elements += arrow("ac_e", 355, 185, [(0, 0), (-20, 55)])
elements += arrow("as_e", 520, 185, [(0, 0), (-140, 55)])

# ---- Row 3: Show controls (y=380) ----
elements += shape("ssMain", "ellipse", 40, 380, 110, 110, label="ShowStart\nMain", label_font=13)
elements += shape("seMain", "ellipse", 180, 380, 110, 110, label="ShowEnd\nMain", label_font=13)
elements += shape("ft", "ellipse", 320, 380, 110, 110, label="Farthest\nTen", label_font=13)
elements += shape("ssSide", "ellipse", 460, 380, 110, 110, label="ShowStart\nSide", label_font=13)
elements += shape("seSide", "ellipse", 600, 380, 110, 110, label="ShowEnd\nSide", label_font=13)

# Main show cycle
elements += arrow("sm_em", 150, 435, [(0, 0), (30, 0)])
elements += arrow("em_sm", 235, 380, [(0, 0), (0, -30), (-140, -30), (-140, 0)],
                  label="+10 min", label_font=11)
elements += arrow("sm_ft", 150, 460, [(0, 0), (170, -20)],
                  dashed=True, label="per entity", label_font=11)

# Side show cycle
elements += arrow("ss_es", 570, 435, [(0, 0), (30, 0)])
elements += arrow("es_ss", 655, 380, [(0, 0), (0, -30), (-140, -30), (-140, 0)],
                  label="+5 min", label_font=11)

# ---- Row 4: Activity ends (y=540) ----
elements += shape("eDJ", "ellipse", 40, 540, 110, 110, label="EndDJ", label_font=16)
elements += shape("ePhoto", "ellipse", 180, 540, 110, 110, label="EndPhoto", label_font=14)
elements += shape("eCharge", "ellipse", 320, 540, 110, 110, label="EndCharge", label_font=14)
elements += shape("eMerch", "ellipse", 460, 540, 110, 110, label="EndMerch", label_font=14)
elements += shape("eBody", "ellipse", 600, 540, 110, 110, label="EndBody\nArt", label_font=13)
elements += shape("eFood", "ellipse", 740, 540, 110, 110, label="EndFood", label_font=14)

# ---- Row 5: Router + queue abandon + end-of-stay ----
elements += shape("nextAct", "rectangle", 220, 710, 340, 60,
                  label="next activity (shortest queue)", label_font=15, rounded=True)
elements.append(
    text_el("loopLbl", "(re-enters activity area per itinerary)", 12,
            x=255, y=780)
)
elements += shape("qab", "ellipse", 600, 690, 110, 110, label="Queue\nAbandon", label_font=13)
elements += shape("eos", "ellipse", 760, 690, 110, 110, label="EndOfStay", label_font=14)

# Entry → nextAct (L-route on left margin)
elements += arrow("e_next", 275, 300,
                  [(0, 0), (-265, 0), (-265, 440), (-55, 440)],
                  label="first activity", label_font=12)

# Show-row → nextAct
elements += arrow("sem_n", 235, 490, [(0, 0), (80, 220)])
elements += arrow("ft_n", 375, 490, [(0, 0), (15, 220)])
elements += arrow("ses_n", 655, 490, [(0, 0), (-180, 220)])

# Activity-ends → nextAct
elements += arrow("dj_n", 95, 650, [(0, 0), (150, 60)])
elements += arrow("ph_n", 235, 650, [(0, 0), (50, 60)])
elements += arrow("ch_n", 375, 650, [(0, 0), (-15, 60)])
elements += arrow("mr_n", 515, 650, [(0, 0), (-80, 60)])
elements += arrow("bd_n", 655, 650, [(0, 0), (-145, 60)])
elements += arrow("fd_n", 795, 650, [(0, 0), (-265, 60)])

# nextAct ↔ qab
elements += arrow("n_qab", 560, 730, [(0, 0), (40, 0)],
                  label="enq", label_font=11)
elements += arrow("qab_n", 600, 755, [(0, 0), (-40, 0)],
                  dashed=True, label="abandon", label_font=11)

# nextAct → eos (route below qab to avoid crossing)
elements += arrow("n_eos", 560, 740, [(0, 0), (0, 80), (275, 80), (275, 60)],
                  label="itinerary done", label_font=11)

# EndOfDay → arrivals (dashed, looping back over the top)
elements += arrow("eod_cp", 820, 110, [(0, 0), (0, -50), (-410, -50), (-410, 0)],
                  dashed=True, label="Day 2 generator", label_font=11)
elements += arrow("eod_sg", 820, 155, [(0, 0), (-210, -25)], dashed=True)

# EndOfDay → EndOfStay (right margin)
elements += arrow("eod_eos", 880, 185, [(0, 0), (0, 505), (-65, 505)],
                  dashed=True, label="mass exit", label_font=11)

# EndOfDay self-loop (next day)
elements += arrow("eod_self", 930, 100, [(0, 0), (45, 0), (45, 70), (0, 70)],
                  dashed=True, label="next day", label_font=11)

# ---- Legend ----
elements.append(text_el("l1", "wavy = stochastic arrival", 13, x=40, y=835))
elements.append(text_el("l2", "dashed = scheduled later / conditional", 13, x=270, y=835))
elements.append(text_el("l3", "circle = event   /   rounded rect = router note", 13, x=560, y=835))

# ---- File envelope ----
doc = {
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

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(elements)} elements)")
