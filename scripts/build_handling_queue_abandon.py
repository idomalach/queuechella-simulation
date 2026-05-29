"""Build the QueueAbandonment handling diagram (D1).

9 nodes per the M1 spec in PLAN.md. Vertical flowchart with one right-side
branch from each of two decision diamonds. Hebrew labels, B&W.

Run: python3 scripts/build_handling_queue_abandon.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _diagram_lib import seeded_rng, shape, arrow, text_el, write_doc

rng = seeded_rng(seed=101)
elements = []

# ---- Title ----
elements.append(text_el(rng, "title", "Handling: QueueAbandonment", 22,
                        x=320, y=15))

# ---- Node 1: start (entry) ----
elements += shape(rng, "n1", "rectangle", 260, 60, 380, 70,
                  label="אירוע QueueAbandonment מופעל\nעבור ישות E בפעילות A",
                  label_font=15, rounded=True)

# ---- arrow down ----
elements += arrow(rng, "a1_2", 450, 130, [(0, 0), (0, 30)])

# ---- Node 2 ----
elements += shape(rng, "n2", "rectangle", 220, 160, 460, 60,
                  label="זהה חברים של E שעדיין בתור של A  →  pulled_out",
                  label_font=14)

elements += arrow(rng, "a2_3", 450, 220, [(0, 0), (0, 30)])

# ---- Node 3: decision ----
elements += shape(rng, "n3", "diamond", 320, 250, 260, 130,
                  label="האם pulled_out\nריק?", label_font=15)

# yes → right branch (node 4: stale timer end)
elements += arrow(rng, "a3_4", 580, 315, [(0, 0), (90, 0)],
                  label="כן", label_font=12)
elements += shape(rng, "n4", "rectangle", 670, 285, 260, 60,
                  label="טיימר ישן — אין פעולה. סיום.",
                  label_font=14, rounded=True)

# no → down
elements += arrow(rng, "a3_5", 450, 380, [(0, 0), (0, 50)],
                  label="לא", label_font=12)

# ---- Node 5 ----
elements += shape(rng, "n5", "rectangle", 280, 430, 340, 60,
                  label="הסר את pulled_out מהתור של A",
                  label_font=14)

elements += arrow(rng, "a5_6", 450, 490, [(0, 0), (0, 30)])

# ---- Node 6 ----
elements += shape(rng, "n6", "rectangle", 200, 520, 500, 70,
                  label="לכל חבר של E (גם pulled_out וגם בשירות):\nהחסר wait_penalty משביעות הרצון האישית",
                  label_font=14)

elements += arrow(rng, "a6_7", 450, 590, [(0, 0), (0, 30)])

# ---- Node 7: decision ----
elements += shape(rng, "n7", "diamond", 290, 620, 320, 130,
                  label="האם נותרו חברי E\nבשירות?", label_font=15)

# yes → right branch (node 8a: defer to End*)
elements += arrow(rng, "a7_8a", 610, 685, [(0, 0), (90, 0)],
                  label="כן", label_font=12)
elements += shape(rng, "n8a", "rectangle", 700, 645, 360, 90,
                  label="סמן את E כממתינה לאיחוד.\nה-End* האחרון יקבע\nאת הפעילות הבאה. סיום.",
                  label_font=14, rounded=True)

# no → down
elements += arrow(rng, "a7_8b", 450, 750, [(0, 0), (0, 40)],
                  label="לא", label_font=12)

# ---- Node 8b ----
elements += shape(rng, "n8b", "rectangle", 260, 790, 380, 70,
                  label="קבע את הפעילות הבאה ב-itinerary של E\n(תור קצר ביותר ברגע זה)",
                  label_font=14)

elements += arrow(rng, "a8_9", 450, 860, [(0, 0), (0, 30)])

# ---- Node 9: end ----
elements += shape(rng, "n9", "rectangle", 240, 890, 420, 70,
                  label="תזמן את אירוע הפעילות הבאה\n(או EndOfStay אם ה-itinerary התרוקן). סיום.",
                  label_font=14, rounded=True)

# ---- Legend ----
elements.append(text_el(rng, "leg",
                        "מעגל מעוגל = התחלה / סיום   |   מלבן = פעולה   |   מעוין = החלטה",
                        13, x=240, y=995))

size = write_doc(
    Path(__file__).resolve().parent.parent / "diagrams" / "handling_queue_abandon.excalidraw",
    elements)
print(f"queue_abandon: {size} bytes, {len(elements)} elements")
