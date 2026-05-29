"""Build the EndOfDay handling diagram (D3).

10 nodes per the M1 spec in PLAN.md. Vertical flow with a Day-1/Day-2
split at the top and a 3-way fan-out on entity type within the Day-1
branch. Hebrew labels, B&W.

Run: python3 scripts/build_handling_endofday.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _diagram_lib import seeded_rng, shape, arrow, text_el, write_doc

rng = seeded_rng(seed=103)
elements = []

# ---- Title ----
elements.append(text_el(rng, "title", "Handling: EndOfDay", 22, x=520, y=15))

# ---- Node 1: start ----
elements += shape(rng, "n1", "rectangle", 480, 60, 360, 60,
                  label="אירוע EndOfDay מופעל (20:00)",
                  label_font=15, rounded=True)

elements += arrow(rng, "a1_2", 660, 120, [(0, 0), (0, 30)])

# ---- Node 2 ----
elements += shape(rng, "n2", "rectangle", 480, 150, 360, 60,
                  label="עצור את כל גנרטורי ההגעות",
                  label_font=15)

elements += arrow(rng, "a2_3", 660, 210, [(0, 0), (0, 30)])

# ---- Node 3: Day 1 / Day 2 decision ----
elements += shape(rng, "n3", "diamond", 510, 240, 300, 120,
                  label="היום הנוכחי?", label_font=15)

# Day 2 → right
elements += arrow(rng, "a3_d2", 810, 300, [(0, 0), (110, 0)],
                  label="יום 2", label_font=12)

# Day 2 action box
elements += shape(rng, "n_d2", "rectangle", 930, 250, 360, 100,
                  label="לכל ביקר שעדיין בפסטיבל:\nרשום שביעות רצון סופית ל-KPI,\nתזמן EndOfStay לכל אחד",
                  label_font=14)

# Day 2 → END
elements += arrow(rng, "a_d2_end", 1110, 350, [(0, 0), (0, 40)])
elements += shape(rng, "end_d2", "rectangle", 1040, 390, 140, 50,
                  label="סיום", label_font=15, rounded=True)

# Day 1 → down
elements += arrow(rng, "a3_4", 660, 360, [(0, 0), (0, 50)],
                  label="יום 1", label_font=12)

# ---- Node 4: walk all entities ----
elements += shape(rng, "n4", "rectangle", 460, 410, 400, 60,
                  label="לכל ישות שעדיין בפסטיבל:",
                  label_font=15)

elements += arrow(rng, "a4_5", 660, 470, [(0, 0), (0, 30)])

# ---- Node 5: entity type decision (3-way fan-out) ----
elements += shape(rng, "n5", "diamond", 510, 500, 300, 120,
                  label="סוג הישות?", label_font=16)

# Left → FriendsGroup
elements += arrow(rng, "a5_fg", 510, 560, [(0, 0), (-220, 0), (-220, 50)],
                  label="FriendsGroup", label_font=11)

# Center → Couple
elements += arrow(rng, "a5_cp", 660, 620, [(0, 0), (0, 30)],
                  label="Couple", label_font=11)

# Right → Single
elements += arrow(rng, "a5_sg", 810, 560, [(0, 0), (220, 0), (220, 50)],
                  label="Single", label_font=11)

# ---- FriendsGroup branch ----
elements += shape(rng, "n_fg", "rectangle", 60, 650, 400, 110,
                  label="אם bought_lodging = True (נקבע ב-Bernoulli(0.7)\nבזמן הגעה)  →  נשאר ללילה\nאחרת  →  תזמן EndOfStay עכשיו",
                  label_font=13)

# ---- Couple branch ----
elements += shape(rng, "n_cp", "rectangle", 480, 650, 360, 110,
                  label="אם לפחות חבר אחד עם satisfaction > 7:\n   שלם 250 NIS ללינה (revenue += 250)\n   ונשאר ללילה.\nאחרת  →  תזמן EndOfStay עכשיו.",
                  label_font=13)

# ---- Single branch ----
elements += shape(rng, "n_sg", "rectangle", 870, 650, 400, 110,
                  label="תזמן EndOfStay תמיד\n(Singles הם חד-יומיים תמיד)",
                  label_font=14)

# Bottom join: all three converge to node 9
# FG branch down then right
elements += arrow(rng, "a_fg_9", 260, 760, [(0, 0), (0, 30), (400, 30), (400, 60)])
# Couple straight down
elements += arrow(rng, "a_cp_9", 660, 760, [(0, 0), (0, 90)])
# Single down then left
elements += arrow(rng, "a_sg_9", 1070, 760, [(0, 0), (0, 30), (-410, 30), (-410, 60)])

# ---- Node 9: schedule next day artifacts ----
elements += shape(rng, "n9", "rectangle", 380, 850, 560, 110,
                  label="תזמן ArrivalCouple + ArrivalSingle חדשים מ-09:00 יום 2.\nתזמן EndOfDay הבא ל-20:00 יום 2.\nשמור snapshot KPI של היום.",
                  label_font=14)

elements += arrow(rng, "a9_end", 660, 960, [(0, 0), (0, 30)])

# ---- End ----
elements += shape(rng, "end_d1", "rectangle", 590, 990, 140, 50,
                  label="סיום", label_font=15, rounded=True)

# ---- Legend ----
elements.append(text_el(rng, "leg",
                        "מעגל מעוגל = התחלה / סיום   |   מלבן = פעולה   |   מעוין = החלטה",
                        13, x=420, y=1070))

size = write_doc(
    Path(__file__).resolve().parent.parent / "diagrams" / "handling_endofday.excalidraw",
    elements)
print(f"endofday: {size} bytes, {len(elements)} elements")
