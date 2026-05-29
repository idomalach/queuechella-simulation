"""Move the RNGStreams trio (header + narrative + code) into §6 as subsection 6.7.

Sampler depends on RNGStreams, so RNGStreams must be defined before §6 executes.
Original PLAN had RNGStreams as section 12, but that placed it after §6, which
causes a NameError when §6.8 validation runs.

This script:
  1. Pops cells 50, 51, 52 (the §12 RNGStreams trio).
  2. Renumbers the section header from "## 12. ..." to "### 6.7 ...".
  3. Updates its narrative to use the 16px style (matches subsection content).
  4. Inserts the three cells just before the Sampler code cell.
  5. Renumbers every downstream section header: §13→§12 ... §20→§19.
  6. Updates the M3 validation subsection number §6.7 → §6.8 (markdown +
     code header comment).
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "Queuechella_Simulation.ipynb"


def cell_text(cell):
    src = cell["source"]
    return "".join(src) if isinstance(src, list) else src


def set_cell_text(cell, text):
    cell["source"] = text.splitlines(keepends=True)


def main():
    with NB_PATH.open() as f:
        nb = json.load(f)

    cells = nb["cells"]

    # ---- Sanity-check the three cells we're about to move ----
    assert "## 12. ניהול זרמי מספרים אקראיים" in cell_text(cells[50]), cell_text(cells[50])[:200]
    assert cells[52]["cell_type"] == "code" and "class RNGStreams" in cell_text(cells[52])

    rng_header = cells[50]
    rng_narrative = cells[51]
    rng_code = cells[52]

    # ---- Renumber: "## 12. " -> "### 6.7 " ----
    set_cell_text(
        rng_header,
        '<div dir="rtl" style="text-align: right;">\n\n'
        "### 6.7 ניהול זרמי מספרים אקראיים (RNG streams)\n\n"
        "</div>\n",
    )

    # ---- Rewrite the narrative in subsection style ----
    set_cell_text(
        rng_narrative,
        '<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">\n\n'
        "מחלקת ה-<code>Sampler</code> מקבלת בבנייה מופע של <code>RNGStreams</code> "
        "— מבנה נתונים שמחזיק <i>זרם אקראיות נפרד לכל מקור</i> במודל "
        "(מרווחי הגעה לכל סוג ישות, משכי הופעות, החלטות ברנולי, בחירות "
        "קטגוריאליות, וכו'). כל זרם הוא <code>random.Random</code> עצמאי, "
        "שמשמשו אותחל בצורה דטרמיניסטית מ-<code>master_seed</code> "
        "באמצעות <code>numpy.random.SeedSequence</code> כדי להבטיח עצמאות "
        "סטטיסטית בין הזרמים.<br><br>"
        "<b>מדוע זרמים נפרדים?</b> בשלב השוואת החלופות (מקטעים 17–18 — "
        "חלק השותפים), נשתמש בטכניקת <b>Common Random Numbers (CRN)</b> "
        "להפחתת שונות: כשמשווים בין המצב הקיים לחלופה כלשהי, כל זרם "
        "שאינו מושפע מהחלופה ינוצל באופן זהה בשתי ההרצות. כך, הפרשי "
        "המדדים נקיים מרעש משותף ודורשים פחות הרצות לזיהוי הבדל "
        "סטטיסטי משמעותי. בלי הפרדת הזרמים, שינוי פרמטר אחד היה גורם "
        "לסחיפה בכל זרם הדגימה התחתון.<br><br>"
        "המחלקה תופיע במקטע הבא; הקוד מוגדר כאן מפני שמופע "
        "<code>RNGStreams</code> דרוש כדי לבנות את <code>Sampler</code>.\n"
        "</div>\n",
    )

    # ---- Pop the trio from their original position ----
    del cells[50:53]

    # ---- Find the Sampler code cell (was at 32, still at 32 after removal because we removed from after it) ----
    sampler_idx = None
    for i, c in enumerate(cells):
        if c["cell_type"] == "code" and c["source"] and "M3: Sampler" in "".join(c["source"]):
            sampler_idx = i
            break
    assert sampler_idx is not None, "could not locate Sampler cell"
    assert sampler_idx == 32, f"unexpected Sampler index: {sampler_idx}"

    # ---- Insert the trio right before Sampler ----
    cells[sampler_idx:sampler_idx] = [rng_header, rng_narrative, rng_code]
    # Now: cells[32, 33, 34] = RNG trio; cells[35] = Sampler

    # ---- Renumber validation subsection: §6.7 -> §6.8 ----
    # Find the validation markdown header (currently labelled §6.7)
    for c in cells:
        if c["cell_type"] != "markdown":
            continue
        txt = cell_text(c)
        if "### 6.7 בדיקת תקפות" in txt:
            set_cell_text(c, txt.replace("### 6.7 בדיקת תקפות", "### 6.8 בדיקת תקפות"))
            break

    # ---- Renumber §13..§20 -> §12..§19 ----
    # The section headers we need to renumber (in any cell):
    renumbers = [
        ("## 13. מחלקת אירועים", "## 12. מחלקת אירועים"),
        ("## 14. מחלקת הסימולציה", "## 13. מחלקת הסימולציה"),
        ("## 15. ניתוח חימום", "## 14. ניתוח חימום"),
        ("## 16. מדדי מצב קיים", "## 15. מדדי מצב קיים"),
        ("## 17. בחינת חלופות", "## 16. בחינת חלופות"),
        ("## 18. השוואת חלופות", "## 17. השוואת חלופות"),
        ("## 19. סיכום והמלצות", "## 18. סיכום והמלצות"),
        ("## 20. דיווח על שימוש", "## 19. דיווח על שימוש"),
    ]
    for c in cells:
        txt = cell_text(c)
        new_txt = txt
        for old, new in renumbers:
            new_txt = new_txt.replace(old, new)
        if new_txt != txt:
            set_cell_text(c, new_txt)

    # ---- Also patch the §6 intro that mentions section 12 for RNG streams ----
    for c in cells:
        if c["cell_type"] != "markdown":
            continue
        txt = cell_text(c)
        if "מקטע 12" in txt:
            set_cell_text(c, txt.replace("מקטע 12", "מקטע 6.7"))

    with NB_PATH.open("w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(f"Done. Notebook now has {len(cells)} cells.")
    print(f"Sampler is at cell {sampler_idx + 3} (was {sampler_idx})")


if __name__ == "__main__":
    main()
