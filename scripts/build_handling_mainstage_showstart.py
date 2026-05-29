"""Build the MainStage ShowStart handling diagram (D2).

9 nodes per the M1 spec in PLAN.md. Vertical flowchart with one loop
back from the fill-to-max scanner to the capacity check. Hebrew labels, B&W.

Run: python3 scripts/build_handling_mainstage_showstart.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _diagram_lib import seeded_rng, shape, arrow, text_el, write_doc

rng = seeded_rng(seed=102)
elements = []

# ---- Title ----
elements.append(text_el(rng, "title", "Handling: ShowStartMain", 22,
                        x=340, y=15))

# ---- Node 1: start ----
elements += shape(rng, "n1", "rectangle", 280, 60, 340, 60,
                  label="אירוע ShowStartMain מופעל\n(בזמן start מתוזמן)",
                  label_font=14, rounded=True)

elements += arrow(rng, "a1_2", 450, 120, [(0, 0), (0, 30)])

# ---- Node 2 ----
elements += shape(rng, "n2", "rectangle", 240, 150, 420, 60,
                  label="אתחל attendees = []\n(רשימה ממוינת לפי זמן כניסה)",
                  label_font=14)

elements += arrow(rng, "a2_3", 450, 210, [(0, 0), (0, 30)])

# ---- Node 3: decision ----
elements += shape(rng, "n3", "diamond", 290, 240, 320, 130,
                  label="התור לא ריק\nוגם נותרה קיבולת?", label_font=14)

# yes branch → right to the scanner loop
elements += arrow(rng, "a3_4", 610, 305, [(0, 0), (90, 0)],
                  label="כן", label_font=12)

# ---- Node 4: the scanner action (with loop back to n3) ----
elements += shape(rng, "n4", "rectangle", 700, 235, 360, 140,
                  label="סרוק את התור מההתחלה לסוף:\nאם entity.size ≤ קיבולת_נותרת\n   →  קבל את הישות (הוסף את\n        כל חבריה ל-attendees,\n        עדכן קיבולת)\nאחרת  →  דלג והמשך לסרוק",
                  label_font=13)

# Loop back: from n4 top, up, left, down into n3 top
elements += arrow(rng, "a4_3", 880, 235, [(0, 0), (0, -50), (-450, -50), (-450, 5)],
                  label="חזור לבדיקה", label_font=11)

# no branch from n3 → down
elements += arrow(rng, "a3_5", 450, 370, [(0, 0), (0, 60)],
                  label="לא", label_font=12)

# ---- Node 5 ----
elements += shape(rng, "n5", "rectangle", 220, 430, 460, 60,
                  label="תזמן ShowEndMain בזמן start + סמפול אורך_הופעה",
                  label_font=14)

elements += arrow(rng, "a5_6", 450, 490, [(0, 0), (0, 30)])

# ---- Node 6 ----
elements += shape(rng, "n6", "rectangle", 200, 520, 500, 70,
                  label="לכל ישות שהוכנסה ל-attendees:\nתזמן FarthestTenCheckpoint בזמן entry_time + 15 דק׳",
                  label_font=14)

elements += arrow(rng, "a6_7", 450, 590, [(0, 0), (0, 30)])

# ---- Node 7 ----
elements += shape(rng, "n7", "rectangle", 220, 620, 460, 60,
                  label="תזמן ShowStartMain הבא ב-showEnd + 10 דק׳ הפסקה",
                  label_font=14)

elements += arrow(rng, "a7_8", 450, 680, [(0, 0), (0, 30)])

# ---- Node 8: END ----
elements += shape(rng, "n8", "rectangle", 380, 710, 140, 50,
                  label="סיום", label_font=15, rounded=True)

# ---- Legend ----
elements.append(text_el(rng, "leg",
                        "מעגל מעוגל = התחלה / סיום   |   מלבן = פעולה   |   מעוין = החלטה",
                        13, x=240, y=820))

size = write_doc(
    Path(__file__).resolve().parent.parent / "diagrams" / "handling_mainstage_showstart.excalidraw",
    elements)
print(f"mainstage_showstart: {size} bytes, {len(elements)} elements")
