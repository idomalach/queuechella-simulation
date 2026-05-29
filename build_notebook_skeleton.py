"""
One-shot scaffolding script: builds Queuechella_Simulation.ipynb with the full
20-section skeleton per PLAN.md.

This script is a build artifact — once the notebook is generated and committed,
the script can be retained for reproducibility or deleted.
"""
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "Queuechella_Simulation.ipynb"

# --- helpers ----------------------------------------------------------------

def _cid() -> str:
    return uuid.uuid4().hex[:12]

def md(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "id": _cid(),
        "metadata": {},
        "source": text.splitlines(keepends=True) or [""],
    }

def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "id": _cid(),
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True) or [""],
    }

# Hebrew RTL wrapper — Tier 1 (assignment-required, kept in final deliverable)
def rtl(content: str) -> str:
    return (
        '<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">\n\n'
        + content.strip()
        + "\n\n</div>"
    )

# Section header helpers — wrap a markdown `##`/`###` inside an RTL div so the
# div's `text-align: right` cascades into the h2/h3 markdown generates. This is
# the only approach that gives us BOTH right-alignment AND TOC entries in Colab:
# inline `style=` on `<h2>` loses to Colab's default h2 stylesheet, and
# `display(HTML(<style>))` gets sandboxed into the cell's output iframe so it
# can't reach other cells. The blank lines around `##` are required — otherwise
# markdown leaves the `##` line as raw text inside the HTML block.
def h2_rtl(text: str) -> str:
    return f'<div dir="rtl" style="text-align: right;">\n\n## {text}\n\n</div>'

def h3_rtl(text: str) -> str:
    return f'<div dir="rtl" style="text-align: right;">\n\n### {text}\n\n</div>'

# Internal note — Tier 2 (stripped before submission, regex-findable).
# Option B: no yellow background — Colab strips both inline backgrounds and Bootstrap
# alert classes from markdown cells. Distinguished from deliverable cells only by the
# literal marker text at the top. Cleanup pass uses regex on that marker string.
def internal(content: str) -> str:
    return (
        '<div dir="rtl" style="text-align: right; font-size: 15px; line-height: 1.8;">\n\n'
        '<b>⚠️ INTERNAL — DELETE BEFORE SUBMISSION</b><br><br>\n\n'
        + content.strip()
        + "\n\n</div>"
    )

# Render a numbered list as raw-HTML `<br>`-separated items (NOT markdown `1.`).
# Markdown lists inside RTL divs get wrapped in <ol><li> with LTR-defaulted styling,
# which fights the parent dir="rtl". This helper keeps everything inline.
def numbered_html(items: list[str]) -> str:
    return "<br>\n".join(f"{i+1}. {item}" for i, item in enumerate(items))

# --- cells ------------------------------------------------------------------

cells = []

# Title — markdown # so Colab's Table of Contents picks it up.
# Header alignment is handled by the CSS-injection code cell below.
cells.append(md("# Queuechella — סימולציית פסטיבל מוזיקה"))

# Group info — separate RTL-wrapped markdown cell so the title stays as a clean #-heading.
cells.append(md(
    '<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">\n\n'
    "<b>קבוצה 20</b> — סמסטר ב' 2026<br><br>\n"
    "עידו מלאך — 318782208<br>\n"
    "יונתן דולמן — 208987644<br>\n"
    "איתן כהן — 322067448<br><br>\n"
    "<b>תאריך הגשה:</b> 2026-06-29\n\n"
    "</div>"
))

# Top-of-notebook internal deletion checklist
cells.append(md(internal(
    "<b>צ'קליסט מחיקה לפני הגשה (חיפוש regex: <code>INTERNAL — DELETE BEFORE SUBMISSION</code>)</b><br><br>\n"
    + numbered_html([
        "למחוק את כל התאים בעלי הסימון הצהוב (כולל תא זה).",
        "לאמת שמקטע 20 (יומן שימוש ב-GenAI) מעודכן.",
        "לאמת שכל ארבעת התרשימים מוטמעים כתמונות ב-base64 במקטע 3.",
        "הרצה מקצה-לקצה לפני הגשה.",
        "החלפת נתיב xlsx מקומי לכתובת raw של GitHub (לטעינה ב-Colab).",
    ])
)))

# Imports cell — single cell, all imports for the entire notebook.
# (RTL alignment of section headers is handled per-cell by `h2_rtl`/`h3_rtl`
# wrapping; global CSS injection via display(HTML(<style>)) is sandboxed by
# Colab into the cell's output iframe and doesn't reach other cells.)
cells.append(code(
    "# Imports — single cell, all imports for the entire notebook\n"
    "import math\n"
    "import heapq\n"
    "import random\n"
    "from enum import Enum\n"
    "from collections import defaultdict\n"
    "from dataclasses import dataclass, field\n"
    "\n"
    "import numpy as np\n"
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import scipy.stats as stats\n"
    "from scipy.stats import probplot\n"
    "from IPython.display import display, HTML\n"
))

# CONFIG cell
cells.append(code(
    '"""CONFIG — every numeric / probabilistic parameter from the spec as named constants.\n'
    "\n"
    "Alternatives mapping (partners flip these for §17 alternatives review):\n"
    "  Better kitchen team        -> food_unsatisfied_prob = 0.1, food_choose_prob = 0.85\n"
    "  Expanded security (+30%)   -> stage_capacity = {main: 260, side: 130, dj: 91}\n"
    "  Mainstream investment      -> merch_band_shirt_prob = 0.8, satisfaction_genre_weight['main'] = 4\n"
    "  Photo + BodyArt expansion  -> photo_stations = 4, body_art_artists = 3\n"
    "  Advertising                -> arrival_rate_multiplier = 1.2\n"
    "  Auto entry                 -> entry_skip_scan = True\n"
    "  Visitor gifts              -> initial_satisfaction = 6.5\n"
    'Budget cap: 1,000,000 NIS combined.\n"""\n'
    "\n"
    "# TODO M2/M3: fill from distribution fits + spec values. Placeholder constants below\n"
    "# are illustrative only — populated during milestones M2 (distributions) and M4 (OOP).\n"
    "CONFIG = {\n"
    '    "initial_satisfaction": 5,\n'
    '    "arrival_rate_multiplier": 1.0,\n'
    '    "entry_skip_scan": False,\n'
    "    # ... see PLAN.md §M4 + the alternatives table above for full list\n"
    "}\n"
))

# --- §1 Introduction ---
cells.append(md(h2_rtl("1. מבוא")))
cells.append(md(rtl(
    "<i>[להשלים: מבוא קצר על פסטיבל Queuechella — מטרת הסימולציה, מה נמדד, מה נבחן.]</i>"
)))

# --- §2 System description + Design Decisions Log ---
cells.append(md(h2_rtl("2. תיאור המערכת והנחות")))
cells.append(md(rtl(
    "<i>[להשלים: תיאור מילולי של המערכת — סוגי מבקרים, מתקנים, אירועים, מבנה הימים.]</i>"
)))
cells.append(md(internal(
    "<b>יומן החלטות תכנון (13 פרשנויות מפתח של המפרט)</b><br>\n"
    "מקור: PLAN.md, מקטע \"Key technical decisions\". כל אחת מההחלטות הללו ניתנת להגנה ע\"פ המפרט, אך עשויות לעלות בהגנה אורלית.<br><br>\n"
    + numbered_html([
        "<b>נטישת תור:</b> טיימר פר-יחות, קנס סיפוק פר-חבר. כל חברי היחות (כולל אלה שכבר בשירות) מאבדים <code>wait_penalty</code>. חברים שבשירות עדיין מקבלים בונוס סיפוק מהפעילות.",
        "<b>MainStage:</b> כניסה מתגלגלת (rolling), fill-to-max — סורק תור head→tail ומכניס כל יחות שגודלה ≤ מקום פנוי.",
        "<b>SideStage:</b> כניסה אצווה (batch) — רק ב-ShowStart.",
        "<b>DJ:</b> ללא הופעות, רציף, כניסה מתגלגלת.",
        "<b>מנגנון 10 הרחוקים:</b> Bernoulli(0.5) פר-יחות, מתוזמן 15 דק' אחרי הכניסה. בודק אם היחות עדיין ב-<code>attendees[-10:]</code>.",
        "<b>איטינררים:</b> בחירת פעילות הבאה ברגע המעבר לפי תור-קצר-ביותר, לא מחושב מראש.",
        "<b>יציאה:</b> Single ו-FriendsGroup יוצאים מיד עם סיום האיטינררי. זוגות יוצאים רק ב-EndOfDay/EndOfStay.",
        "<b>הכנסות לינה:</b> FriendsGroup קונה בהגעה (Bernoulli(0.7) ב-700 ש\"ח). Couple מחליט ב-EndOfDay (חבר אחד עם סיפוק>7 → 250 ש\"ח). Single לא ישן.",
        "<b>MerchTent:</b> כל חבר מגלגל באופן עצמאי לכל פריט (חולצה 0.8, כובע 0.4, דגל 0.9, חולצת להקה 0.3).",
        "<b>PhotoStation:</b> Bernoulli(0.7) מרוצה → +2 סיפוק + 30 ש\"ח. אחרת Bernoulli(0.5) → -0.5 סיפוק. גלגול פר-מבקר.",
        "<b>Entry:</b> ללא נטישה — המבקרים שילמו על כרטיסים. 5 פקידים, סריקה+אבטחה ברצף. Auto-entry alternative מסיר את הסריקה.",
        "<b>FoodCourt:</b> כן יש נטישה. נטישה = דילוג על אוכל + קנס + המשך איטינררי. פעם אחת ביום פר-מבקר.",
        "<b>קצב הגעה ביום 2:</b> זהה ליום 1 עבור Couple/Single. זוגות שלנו ממשיכים, חדשים מגיעים.",
    ])
)))

# --- §3 Diagrams ---
cells.append(md(h2_rtl("3. תרשים אירועים ותרשימי טיפול")))
cells.append(md(rtl(
    "<i>[להשלים M1: ארבעה תרשימים מוטמעים כתמונות base64 — תרשים אירועים כללי + 3 תרשימי טיפול (QueueAbandonment, MainStage_ShowStart, EndOfDay). PNG-ים מקוריים ב-<code>diagrams/</code>.]</i>"
)))

# --- §4 KPI ---
cells.append(md(h2_rtl("4. בחירת מדדים")))
cells.append(md(rtl(
    "<i>[להשלים: נימוק לבחירת שלושת המדדים — סיפוק מבקרים ממוצע ביציאה, זמן המתנה ממוצע + מקסימלי בתורים, הכנסות הפסטיבל.]</i>"
)))

# --- §5 Distribution fitting ---
cells.append(md(h2_rtl("5. התאמת התפלגות")))

cells.append(md(h3_rtl("5א. זמני הגעה בין קבוצות חברים — Exponential")))
cells.append(md(rtl(
    "<i>[להשלים M2: היסטוגרמה + צפיפות עם פיתוח MLE מלא ב-LaTeX, מבחני KS ו-Chi-Square, Q-Q plot, נראטיב בעברית.]</i>"
)))
cells.append(code(
    "# M2: load FriendsGroup arrival intervals + fit exponential\n"
    "# Placeholder — populated in M2\n"
))

cells.append(md(h3_rtl("5ב. משך הופעות MainStage — Normal")))
cells.append(md(rtl(
    "<i>[להשלים M2: אותו זרימה עבור התפלגות נורמלית — פיתוח MLE עבור μ ו-σ², KS, Chi-Square, Q-Q.]</i>"
)))
cells.append(code(
    "# M2: load MainStage concert duration + fit normal\n"
    "# Placeholder — populated in M2\n"
))

# --- §6 Sampling ---
cells.append(md(h2_rtl("6. אלגוריתמי דגימה")))
cells.append(md(rtl(
    "<i>[להשלים M3: פיתוחים מתמטיים ב-LaTeX לפני מחלקת ה-Sampler — Inverse Transform, Box-Muller, Composition (Photo, מאומץ מהדוגמה), Acceptance-Rejection (DJ — חובה ע\"פ המפרט).]</i>"
)))
cells.append(code(
    "# M3: Sampler class — all sampling methods bundled\n"
    "# Placeholder — populated in M3\n"
    "class Sampler:\n"
    "    \"\"\"All sampling methods for the simulation. Accepts an RNGStreams instance.\"\"\"\n"
    "    def __init__(self, rng_streams):\n"
    "        self.rng = rng_streams\n"
))

# --- §7 Customer ---
cells.append(md(h2_rtl("7. מחלקת לקוח (Customer)")))
cells.append(md(rtl(
    "<i>[להשלים M4: תיאור קצר של מחלקת המבקר היחיד — סיפוק אישי, היסטוריית פעילויות, מצב תור/שירות.]</i>"
)))
cells.append(code(
    "# M4: Customer class\n"
    "class Customer:\n"
    "    \"\"\"Single visitor — personal satisfaction, activity history, queue/service state.\"\"\"\n"
    "    pass\n"
))

# --- §8 Groups ---
cells.append(md(h2_rtl("8. מחלקות אורחים (Group ותתי-מחלקות)")))
cells.append(md(rtl(
    "<i>[להשלים M4: מחלקת Group מופשטת + FriendsGroup, Couple, Single. כולל wait_tolerance, wait_penalty, איטינררי, ובחירת פעילות הבאה.]</i>"
)))
cells.append(code(
    "# M4: Group hierarchy\n"
    "class Group:\n"
    "    \"\"\"Abstract base for visiting entities (FriendsGroup, Couple, Single).\"\"\"\n"
    "    pass\n"
    "\n"
    "class FriendsGroup(Group):\n"
    "    pass\n"
    "\n"
    "class Couple(Group):\n"
    "    pass\n"
    "\n"
    "class Single(Group):\n"
    "    pass\n"
))

# --- §9 Activities / Facilities ---
cells.append(md(h2_rtl("9. מחלקות מתקנים (Activities)")))
cells.append(md(rtl(
    "<i>[להשלים M4: Activity מופשטת + MainStage, SideStage, DJstage, PhotoStation, ChargingStation, MerchTent, BodyArt, Entry, FoodCourt.]</i>"
)))
cells.append(code(
    "# M4: Activity hierarchy\n"
    "class Activity:\n"
    "    \"\"\"Abstract base for festival facilities.\"\"\"\n"
    "    pass\n"
    "\n"
    "class MainStage(Activity):    pass\n"
    "class SideStage(Activity):    pass\n"
    "class DJstage(Activity):      pass\n"
    "class PhotoStation(Activity): pass\n"
    "class ChargingStation(Activity): pass\n"
    "class MerchTent(Activity):    pass\n"
    "class BodyArt(Activity):      pass\n"
    "class Entry(Activity):        pass\n"
    "class FoodCourt(Activity):    pass\n"
))

# --- §10 QueueServer ---
cells.append(md(h2_rtl("10. מחלקת תור (QueueServer)")))
cells.append(md(rtl(
    "<i>[להשלים M4: תור FIFO עם טיימר נטישה פר-יחות, מעקב זמני המתנה, ספירת נטישות.]</i>"
)))
cells.append(code(
    "# M4: QueueServer\n"
    "class QueueServer:\n"
    "    \"\"\"FIFO queue with per-entity abandonment timer and wait-time tracking.\"\"\"\n"
    "    pass\n"
))

# --- §11 KPI tracker ---
cells.append(md(h2_rtl("11. מחלקת מעקב מדדים (KPITracker)")))
cells.append(md(rtl(
    "<i>[להשלים M4: איסוף סיפוק סופי, זמני המתנה, מקסימום המתנה, הכנסות לפי מקור, snapshot יומי.]</i>"
)))
cells.append(code(
    "# M4: KPITracker\n"
    "class KPITracker:\n"
    "    \"\"\"Collects satisfaction, wait times, revenue across the simulation run.\"\"\"\n"
    "    pass\n"
))

# --- §12 RNGStreams ---
cells.append(md(h2_rtl("12. ניהול זרמי מספרים אקראיים (RNGStreams)")))
cells.append(md(rtl(
    "<i>[להשלים M4: random.Random נפרד לכל מקור (arrival_friends, arrival_couple, show_main, dj_stay, photo, ...). master_seed לשחזור. שותפים מאתחלים זרמים ספציפיים בלבד עבור CRN בחלופות.]</i>"
)))
cells.append(code(
    "# M4: RNGStreams\n"
    "class RNGStreams:\n"
    "    \"\"\"Independent random.Random streams per source for CRN-friendly variance reduction.\"\"\"\n"
    "    pass\n"
))

# --- §13 Event base class ---
cells.append(md(h2_rtl("13. מחלקת אירועים (Event)")))
cells.append(md(internal(
    "<b>הערה לשותפים:</b> מקטע זה מכיל את מחלקת Event הבסיסית בלבד. תתי-המחלקות (ArrivalFriendsGroup, EndEntry, ShowStartMain, ShowEndMain, FarthestTenCheckpoint, ...) ממומשות על-ידי השותפים בשלב הבא — ראו רשימה מלאה ב-PLAN.md §M4.\n"
)))
cells.append(md(rtl(
    "<i>[להשלים M4: מחלקת Event מופשטת — time, __lt__ ל-heapq, execute(simulation). תתי-מחלקות יעוצבו ע\"י השותפים.]</i>"
)))
cells.append(code(
    "# M4: Event base class — partners extend with concrete subclasses\n"
    "class Event:\n"
    "    \"\"\"Abstract base for FEL entries. Subclasses implement execute(simulation).\"\"\"\n"
    "    pass\n"
))

# --- §14 Simulation skeleton ---
cells.append(md(h2_rtl("14. מחלקת הסימולציה (Simulation)")))
cells.append(md(internal(
    "<b>הערה לשותפים:</b> סקלטון בלבד עם hook-ים ל-KPI. לולאת ה-run ממומשת ע\"י השותפים.\n"
)))
cells.append(md(rtl(
    "<i>[להשלים M4: שלד Simulation עם clock, day, fel, activities, entities, rng_streams, kpi. שיטות schedule/pop_next_event. run() — השותפים.]</i>"
)))
cells.append(code(
    "# M4: Simulation skeleton — partners fill the run loop\n"
    "class Simulation:\n"
    "    \"\"\"Event-driven festival simulation. Run loop is implemented by partners.\"\"\"\n"
    "    pass\n"
))

# --- Partner-owned sections (15-19) ---
partner_sections = [
    ("15. ניתוח חימום", "Warmup analysis"),
    ("16. מדדי מצב קיים", "Current-state KPIs"),
    ("17. בחינת חלופות", "Alternative review"),
    ("18. השוואת חלופות (Welch)", "Welch comparison"),
    ("19. סיכום והמלצות", "Summary & recommendations"),
]
for he_title, en_title in partner_sections:
    cells.append(md(h2_rtl(he_title)))
    cells.append(md(internal(
        f"<b>מקטע השותפים — {en_title}.</b> ראה PLAN.md לפירוט הדרישות. לעדכן את <code>instructions_coverage.md</code> עם סיום.\n"
    )))
    cells.append(md(rtl(f"<i>[להשלים ע\"י השותפים: {en_title}.]</i>")))

# --- §20 GenAI declaration log ---
cells.append(md(h2_rtl("20. דיווח על שימוש בכלי GenAI")))
cells.append(md(rtl(
    "להלן יומן השימוש בכלי בינה מלאכותית יוצרת במהלך עבודת הפרויקט, כנדרש ע\"פ הסילבוס. היומן מתעדכן באופן רציף — על השותפים להוסיף ערכים חדשים בהתאם.\n"
    "\n"
    "| תאריך | כלי | מטרה | תיאור השימוש |\n"
    "|---|---|---|---|\n"
    "| 2026-05-26 | Claude (Anthropic) | תכנון ושלד | תכנון מפת הדרכים של הפרויקט, בניית שלד ה-notebook, יצירת קובץ <code>instructions_coverage.md</code>. הקוד והנראטיב הסופיים נכתבים ונבדקים ע\"י הסטודנטים. |\n"
)))
cells.append(md(internal(
    "<b>הערה לשותפים:</b> להוסיף שורה לטבלה לעיל בכל פעם שנעשה שימוש בכלי GenAI — תאריך, כלי, מטרה (תכנון/קוד/ניסוח), ותיאור קצר. זהו המקור עבור טופס ההצהרה הרשמי.\n"
)))

# --- assemble & write ------------------------------------------------------

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.13",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1))
print(f"wrote {OUT} ({len(cells)} cells)")
