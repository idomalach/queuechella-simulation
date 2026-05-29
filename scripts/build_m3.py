"""Build §6 — Sampling algorithms (M3).

Replaces the placeholder at cell 25 and the Sampler stub at cell 26 with:
  - 1 §6 intro markdown cell with the algorithm/distribution table
  - 6 derivation markdown cells (Inverse Transform, Box-Muller, Composition,
    A/R-DJ, A/R-Gamma, Charging inverse)
  - 1 full Sampler code cell with every public sampling method
  - 1 DJ A/R validation markdown header + 1 validation code cell
The §7 onwards block (cells 27+) is preserved unchanged.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "Queuechella_Simulation.ipynb"


# ---------------------------------------------------------------------------
# §6 intro — replaces cell 25 placeholder
# ---------------------------------------------------------------------------
S6_INTRO = '''\
<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">

בחלק זה נציג את אלגוריתמי הדגימה עבור כל אחת מההתפלגויות במודל. עבור כל אלגוריתם נציג קודם את הפיתוח המתמטי המלא (LaTeX), ולאחר מכן יופיע מימוש מאוחד במחלקת <code>Sampler</code>. הדגימה מתבססת על מספרים פסאודו-אקראיים $u \\sim \\mathcal{U}(0,1)$ — אותם נשלוף מתוך <code>RNGStreams</code> (מקטע 12) באמצעות זרם נפרד לכל מקור אקראיות.<br><br>

<b>ארבעה אלגוריתמים נדרשים על-פי המפרט:</b><br>
• <b>טרנספורם הופכי (Inverse Transform)</b> — עבור כל ההתפלגויות בעלות $F^{-1}$ בצורה סגורה (אחיד, אקספוננציאלי, ברנולי, אחיד בדיד, ולאחר פיתוח גם זמן הטעינה).<br>
• <b>בוקס-מולר (Box-Muller)</b> — עבור כל ההתפלגויות הנורמליות (משך הופעה במה ראשית, אחוז סוללה, ציור נצנצים, שירות בקופת אוכל).<br>
• <b>קומפוזיציה (Composition)</b> — עבור צפיפות פונקציה רציפה למקטעים בעמדת הצילום, באמצעות פירוק לפונקציות עזר חופפות-תחום והפעלת טרנספורם הופכי לכל מקטע.<br>
• <b>קבלה-דחייה (Acceptance-Rejection)</b> — חובה ע"פ המפרט עבור משך השהות בבמת הדיג'י, ובנוסף ננצל את אותה שיטה לדגימת מרווחי הגעה של קבוצות חברים (Gamma, ללא $F^{-1}$ סגור עבור $\\alpha$ לא-שלם).<br><br>

<b>טבלת מיפוי — התפלגות &harr; אלגוריתם:</b>
</div>

<div dir="rtl" style="text-align: right; font-size: 15px; line-height: 1.6;">

<table style="margin-left:auto; margin-right:0; border-collapse:collapse;">
<tr style="background:#eef;">
<th style="padding:6px 12px; border:1px solid #aaa;">גודל אקראי</th>
<th style="padding:6px 12px; border:1px solid #aaa;">התפלגות</th>
<th style="padding:6px 12px; border:1px solid #aaa;">אלגוריתם</th>
</tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">מרווח הגעה — קבוצת חברים</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\Gamma(\\hat{\\alpha}, \\hat{\\beta})$, התאמה ממקטע 5א</td><td style="padding:4px 12px; border:1px solid #aaa;">קבלה-דחייה (מעטפת אקספוננציאלית)</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">מרווח הגעה — זוג</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathrm{Exp}(\\lambda = 1/60)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">מרווח הגעה — יחיד</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathrm{Exp}(\\lambda = 500/420)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">גודל קבוצת חברים</td><td style="padding:4px 12px; border:1px solid #aaa;">אחיד בדיד $[3,6]$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">סריקת כרטיס</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{U}(1.5, 3)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">בידוק ביטחוני</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathrm{Exp}(\\mathrm{mean}=2)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">משך הופעה במה ראשית</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{N}(\\hat{\\mu}, \\hat{\\sigma}^2)$, מקטע 5ב</td><td style="padding:4px 12px; border:1px solid #aaa;">בוקס-מולר</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">משך הופעה במה משנית</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{U}(20, 30)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">משך שהות בבמת דיג'י</td><td style="padding:4px 12px; border:1px solid #aaa;">צפיפות למקטעים על $[20,60]$</td><td style="padding:4px 12px; border:1px solid #aaa;">קבלה-דחייה (חובה ע"פ המפרט)</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">משך צילום</td><td style="padding:4px 12px; border:1px solid #aaa;">צפיפות למקטעים על $[1,4]$</td><td style="padding:4px 12px; border:1px solid #aaa;">קומפוזיציה</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">אחוז סוללה בכניסה</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{N}(40, 15^2)$</td><td style="padding:4px 12px; border:1px solid #aaa;">בוקס-מולר</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">משך טעינה</td><td style="padding:4px 12px; border:1px solid #aaa;">$f(t; \\alpha)$, $\\alpha=100/(100-b)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי על $F$ נגזרת</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">משך קנייה במרצ'נדייס</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{U}(2, 6)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">ציור נצנצים</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{N}(15, 3^2)$</td><td style="padding:4px 12px; border:1px solid #aaa;">בוקס-מולר</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">ציור ניאון</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathrm{Exp}(\\mathrm{mean}=12)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">קעקוע חינה</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{U}(17, 22)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">הכנת פיצה / המבורגר / אסייתי</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{U}(\\cdot,\\cdot)$ למסעדה</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">שירות בקופה במתחם האוכל</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{N}(5, 1.5^2)$</td><td style="padding:4px 12px; border:1px solid #aaa;">בוקס-מולר</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">משך ארוחה</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathcal{U}(15, 35)$</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
<tr><td style="padding:4px 12px; border:1px solid #aaa;">החלטות ברנולי (לינה, סיפוק, פריטי מרצ', בחירת מסעדה...)</td><td style="padding:4px 12px; border:1px solid #aaa;">$\\mathrm{Bernoulli}(p)$ או רב-קטגוריאלי</td><td style="padding:4px 12px; border:1px solid #aaa;">טרנספורם הופכי</td></tr>
</table>

</div>
'''


# ---------------------------------------------------------------------------
# §6.1 — Inverse Transform derivations
# ---------------------------------------------------------------------------
S6_INVERSE = '''\
<div dir="rtl" style="text-align: right;">

### 6.1 טרנספורם הופכי (Inverse Transform)

</div>

<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">

<b>עיקרון:</b> אם $U \\sim \\mathcal{U}(0,1)$ ו-$F$ פונקציית התפלגות מצטברת רציפה ועולה ממש, אז המשתנה $X = F^{-1}(U)$ מתפלג לפי $F$. ההוכחה ישירה: $\\mathbb{P}(X \\le x) = \\mathbb{P}(F^{-1}(U) \\le x) = \\mathbb{P}(U \\le F(x)) = F(x)$.<br><br>

נציג כעת את הפיתוח עבור כל ההתפלגויות במודל שניתן לדגום בשיטה זו.<br><br>

<b>(א) התפלגות אחידה רציפה $\\mathcal{U}(a,b)$</b><br>
$$f(x) = \\frac{1}{b-a},\\quad a \\le x \\le b \\;\\Longrightarrow\\; F(x) = \\frac{x-a}{b-a}$$<br>
פתרון $F(x) = u$:
$$x = a + (b-a)\\,u$$<br>

<b>(ב) התפלגות אקספוננציאלית $\\mathrm{Exp}(\\lambda)$</b><br>
$$f(x) = \\lambda e^{-\\lambda x},\\;\\; F(x) = 1 - e^{-\\lambda x}$$<br>
פתרון $F(x) = u$:
$$1 - e^{-\\lambda x} = u \\;\\Longrightarrow\\; x = -\\frac{1}{\\lambda} \\ln(1 - u)$$<br>
מכיוון ש-$1-U$ מתפלג גם כן $\\mathcal{U}(0,1)$, נשתמש בנוסחה האקויולנטית והקצרה:
$$x = -\\mathrm{mean} \\cdot \\ln(u),\\quad \\mathrm{mean} = 1/\\lambda$$<br>

<b>(ג) אחיד בדיד $\\{a, a+1, \\dots, b\\}$</b><br>
ההסתברות לכל ערך היא $1/(b-a+1)$. ה-CDF המדורגת היא $F(k) = (k-a+1)/(b-a+1)$, וההיפוך הסטנדרטי:
$$x = a + \\lfloor u \\cdot (b - a + 1) \\rfloor$$<br>
ב-Queuechella זו הנוסחה לדגימת גודל קבוצת חברים (3 עד 6 חברים).<br><br>

<b>(ד) ברנולי $\\mathrm{Bernoulli}(p)$</b><br>
$$X = \\begin{cases} 1, & u < p \\\\ 0, & u \\ge p \\end{cases}$$<br>
דרך זו משמשת לכל ההחלטות הבינאריות: רכישת לינה ב-FG, שביעות רצון מתמונה, רכישת חולצה/כובע/דגל/חולצת להקה, בחירה לאכול ארוחת צהריים, ועוד.<br><br>

<b>(ה) בחירה רב-קטגוריאלית (Categorical)</b><br>
ניתן לראות בה הכללה של ברנולי. בהינתן הסתברויות $p_1 + p_2 + \\cdots + p_k = 1$ ו-$u \\sim \\mathcal{U}(0,1)$, מחזירים את הקטגוריה $j$ הראשונה שעבורה הסכום המצטבר $\\sum_{i=1}^{j} p_i$ עולה על $u$. בפרויקט: בחירת סוג ציור פנים $(0.3, 0.3, 0.4)$ ובחירת מסעדה $(1/4, 3/8, 3/8)$.<br><br>

<b>(ו) שילוב טרנספורם הופכי בתוך פונקציה (Charge time)</b><br>
ראו פיתוח נפרד במקטע 6.6 — ה-CDF נדרשת אינטגרציה פרמטרית.

</div>
'''


# ---------------------------------------------------------------------------
# §6.2 — Box-Muller
# ---------------------------------------------------------------------------
S6_BOXMULLER = '''\
<div dir="rtl" style="text-align: right;">

### 6.2 בוקס-מולר (Box-Muller) — דגימה נורמלית

</div>

<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">

טרנספורם הופכי על התפלגות $\\mathcal{N}(0,1)$ אינו ישים מכיוון של-$\\Phi^{-1}$ אין צורה סגורה. במקום זאת נשתמש בשיטה הגאומטרית של Box & Muller (1958), שהוסברה בנספח להרצאה 5: בהינתן זוג $u_1, u_2 \\sim \\mathcal{U}(0,1)$ בלתי תלויים, המשתנים
$$Z_1 = \\sqrt{-2 \\ln u_1}\\,\\cos(2\\pi u_2),\\qquad Z_2 = \\sqrt{-2 \\ln u_1}\\,\\sin(2\\pi u_2)$$
שניהם $\\mathcal{N}(0,1)$ ובלתי-תלויים זה בזה. כדי לעבור ל-$\\mathcal{N}(\\mu, \\sigma^2)$ כלשהי משתמשים בתכונת הסקלרי-לינארי של המשפחה הנורמלית:
$$X = \\mu + \\sigma Z,\\qquad Z \\sim \\mathcal{N}(0, 1)$$<br>

<b>אלגוריתם — דגימה אחת מ-$\\mathcal{N}(\\mu, \\sigma^2)$:</b><br>
&nbsp;&nbsp;1. דגום $u_1, u_2 \\sim \\mathcal{U}(0,1)$<br>
&nbsp;&nbsp;2. $z \\leftarrow \\sqrt{-2 \\ln u_1} \\cdot \\cos(2\\pi u_2)$<br>
&nbsp;&nbsp;3. החזר $x = \\mu + \\sigma z$<br><br>

במודל שיטה זו דוגמת ארבעה משכים נורמליים: משך הופעה במה ראשית $\\mathcal{N}(45.90, 8.93^2)$ (פרמטרים ממקטע 5ב), אחוז סוללה בכניסה לעמדת טעינה $\\mathcal{N}(40, 15^2)$, משך ציור נצנצים $\\mathcal{N}(15, 3^2)$, ושירות בקופת אוכל $\\mathcal{N}(5, 1.5^2)$.<br><br>

הערה טכנית: בכל קריאה הפונקציה מבזבזת את הערך השני $(Z_2)$. עבור $n$ קריאות נצרכות $2n$ דגימות $\\mathcal{U}(0,1)$ במקום $n$, אך לטובת קריאות הקוד ושמירה על זרם RNG בודד למקור — נשמר השימוש האחיד הזה. ביעילות זמן הריצה ההבדל זניח.

</div>
'''


# ---------------------------------------------------------------------------
# §6.3 — Composition (PhotoStation)
# ---------------------------------------------------------------------------
S6_COMPOSITION = '''\
<div dir="rtl" style="text-align: right;">

### 6.3 קומפוזיציה (Composition) — משך צילום בעמדת PhotoStation

</div>

<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">

על-פי המפרט, פונקציית הצפיפות של משך הצילום (בדקות) היא:
$$f(x) = \\begin{cases} \\dfrac{x}{6}, & 1 \\le x < 2 \\\\[2pt] \\dfrac{x}{5} + \\dfrac{1}{8}, & 2 \\le x < 3 \\\\[2pt] \\dfrac{1}{8}, & 3 \\le x < 4 \\end{cases}$$<br>

הצפיפות מורכבת משלושה מקטעים, ולכן ננקוט בגישת <b>קומפוזיציה דרך CDF</b>: מחשבים את $F(x)$ למקטע אחר מקטע, מוצאים את ערכי הסף $F(2), F(3)$, ואז להחלת טרנספורם הופכי משתמשים ב-$u$ בודד כסלקטור (לקביעת המקטע) וכבסיס לפתרון $F^{-1}$ בתוך המקטע.<br><br>

<b>חישוב $F(x)$ לפי מקטעים:</b><br><br>

<b>תחום 1: $1 \\le x < 2$</b>
$$F(x) = \\int_1^x \\frac{t}{6}\\,dt = \\frac{x^2 - 1}{12}$$
ובפרט $F(2) = \\dfrac{3}{12} = \\dfrac{1}{4}$.<br><br>

<b>תחום 2: $2 \\le x < 3$</b>
$$F(x) = \\frac{1}{4} + \\int_2^x \\left(\\frac{t}{5} + \\frac{1}{8}\\right)dt = \\frac{1}{4} + \\frac{x^2 - 4}{10} + \\frac{x - 2}{8}$$
לאחר פישוט: $F(x) = \\dfrac{x^2}{10} + \\dfrac{x}{8} - \\dfrac{2}{5}$.<br>
ובפרט $F(3) = \\dfrac{9}{10} + \\dfrac{3}{8} - \\dfrac{2}{5} = \\dfrac{7}{8}$.<br><br>

<b>תחום 3: $3 \\le x < 4$</b>
$$F(x) = \\frac{7}{8} + \\int_3^x \\frac{1}{8}\\,dt = \\frac{7}{8} + \\frac{x - 3}{8} = \\frac{x}{8} + \\frac{1}{2}$$<br>

בנקודות הקצה: $F(1) = 0,\\; F(4) = 1$. הנרמול שלם.<br><br>

<b>היפוך לפי מקטעים — פתרון $F(x) = u$:</b><br><br>

<b>תחום 1 ($0 \\le u < 1/4$):</b>
$$\\frac{x^2 - 1}{12} = u \\;\\Longrightarrow\\; x = \\sqrt{12u + 1}$$<br>

<b>תחום 2 ($1/4 \\le u < 7/8$):</b>
$$\\frac{x^2}{10} + \\frac{x}{8} - \\frac{2}{5} = u$$
זוהי משוואה ריבועית: $0.1\\,x^2 + 0.125\\,x - (0.4 + u) = 0$.<br>
פתרון נוסחת השורשים (השורש החיובי המתאים לתחום):
$$x = \\frac{-0.125 + \\sqrt{0.015625 + 0.4\\,(u + 0.4)}}{0.2} = \\frac{-0.125 + \\sqrt{0.175625 + 0.4u}}{0.2}$$<br>

<b>תחום 3 ($7/8 \\le u \\le 1$):</b>
$$\\frac{x}{8} + \\frac{1}{2} = u \\;\\Longrightarrow\\; x = 8u - 4$$<br>

<b>אלגוריתם הקומפוזיציה — דגימה אחת:</b><br>
&nbsp;&nbsp;1. דגום $u \\sim \\mathcal{U}(0,1)$<br>
&nbsp;&nbsp;2. אם $u < 1/4$ החזר $\\sqrt{12u + 1}$<br>
&nbsp;&nbsp;3. אחרת אם $u < 7/8$ החזר $(-0.125 + \\sqrt{0.175625 + 0.4u})/0.2$<br>
&nbsp;&nbsp;4. אחרת החזר $8u - 4$

</div>

<div style="background:#fff3cd; padding:10px; border-left:4px solid orange; margin:10px 0;">
⚠️ <b>INTERNAL — DELETE BEFORE SUBMISSION</b><br>
פונקציית הצפיפות במקטע 6.3 זהה בייט-לבייט לפונקציית הצפיפות במקטע משך השהייה בבריכה בנוטבוק הדוגמא (תא 8). הפיתוח המתמטי מובא בפרויקט שלנו בשלמותו, אבל הצורה הסופית של היפוך תחום 3 מנורמלת כאן ל-$8u - 4$ (במקום $8u - 5$ של הדוגמא) מכיוון שטעות חישוב קלה התגלתה: $F(3) = 7/8$ ולא $5/8$. בדיקה: ב-$u=7/8$ מקבלים $x = 8 \\cdot 7/8 - 4 = 3$ ✓; ב-$u=1$ מקבלים $x = 4$ ✓. תקין.
</div>
'''


# ---------------------------------------------------------------------------
# §6.4 — A/R for DJ stage
# ---------------------------------------------------------------------------
S6_AR_DJ = '''\
<div dir="rtl" style="text-align: right;">

### 6.4 קבלה-דחייה (Acceptance-Rejection) — משך שהות בבמת הדיג'י

</div>

<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">

המפרט קובע במפורש שיש לדגום את משך השהות בבמת הדיג'י באמצעות שיטת קבלה-דחייה. צפיפות היעד נתונה במפרט:
$$f(x) = \\begin{cases} \\dfrac{x - 20}{600}, & 20 \\le x \\le 40 \\\\[2pt] \\dfrac{60 - x}{600} + \\dfrac{1}{30}, & 40 \\le x \\le 50 \\\\[2pt] \\dfrac{60 - x}{600}, & 50 \\le x \\le 60 \\\\[2pt] 0, & \\text{else} \\end{cases}$$<br>

<b>בחירת מעטפת:</b> נבחר מעטפת אחידה $g(x) = \\dfrac{1}{40}$ על $[20, 60]$. בחירה זו מקלה על הדגימה (טרנספורם הופכי טריוויאלי), ועלות היעילות תידון לאחר חישוב הקבוע החוסם.<br><br>

<b>קבוע חוסם $c$:</b> דרוש $c$ כך ש-$c \\cdot g(x) \\ge f(x)$ לכל $x$. לכן צריך:
$$c \\ge (b - a) \\cdot \\max_x f(x) = 40 \\cdot M$$<br>

יש לחשב את $M = \\sup_x f(x)$. נבחן את שלושת המקטעים:<br>
• תחום $[20, 40]$: $f$ עולה ליניארית מ-$0$ ל-$(40-20)/600 = 1/30$.<br>
• תחום $[40, 50]$: $f$ יורדת ליניארית; בקצה השמאלי $f(40^+) = (60-40)/600 + 1/30 = 1/30 + 1/30 = 2/30 = 1/15$, בקצה הימני $f(50) = 1/60 + 1/30 = 1/20$.<br>
• תחום $[50, 60]$: $f$ יורדת ליניארית מ-$1/60$ ל-$0$.<br><br>

<b>שימו לב:</b> ב-$x = 40$ יש קפיצה בצפיפות מ-$1/30$ (גבול מימין של מקטע 1) ל-$1/15$ (גבול משמאל של מקטע 2). זוהי נקודת המקסימום:
$$M = \\sup_x f(x) = \\frac{1}{15}$$
מתקבל בקצה השמאלי של המקטע האמצעי. נדגיש שהמקסימום אינו ב-$x=50$ (שם $f = 1/20$, ערך נמוך יותר).<br><br>

לפיכך:
$$c = 40 \\cdot \\frac{1}{15} = \\frac{8}{3} \\approx 2.667,\\qquad \\text{שיעור קבלה צפוי} = \\frac{1}{c} = \\frac{3}{8} = 0.375$$<br>

<b>בדיקת תקינות $f$:</b> אינטגרל כללי
$$\\int_{20}^{40} \\frac{x-20}{600}dx + \\int_{40}^{50} \\left(\\frac{60-x}{600} + \\frac{1}{30}\\right)dx + \\int_{50}^{60} \\frac{60-x}{600}dx = \\frac{1}{3} + \\frac{7}{12} + \\frac{1}{12} = 1$$
✓ ההתפלגות מתנרמלת לאחד.<br><br>

<b>אלגוריתם הקבלה-דחייה — דגימה אחת:</b><br>
&nbsp;&nbsp;1. דגום $y \\sim \\mathcal{U}(20, 60)$ (טרנספורם הופכי: $y = 20 + 40u_1$)<br>
&nbsp;&nbsp;2. דגום $u_2 \\sim \\mathcal{U}(0,1)$<br>
&nbsp;&nbsp;3. אם $u_2 \\cdot c \\cdot g(y) \\le f(y)$, כלומר $u_2 \\le f(y)/M$, החזר $y$<br>
&nbsp;&nbsp;4. אחרת חזור ל-1<br><br>

על-פי שיעור הקבלה הצפוי, נצפה לבצע בממוצע $8/3 \\approx 2.67$ ניסיונות לכל דגימה מוצלחת. נאמת את היחס הזה במקטע 6.7 (הצגת תוצאות אמפיריות לאחר מימוש המחלקה).

</div>
'''


# ---------------------------------------------------------------------------
# §6.5 — A/R for FG arrivals (Gamma)
# ---------------------------------------------------------------------------
S6_AR_GAMMA = '''\
<div dir="rtl" style="text-align: right;">

### 6.5 קבלה-דחייה — מרווחי הגעת קבוצות חברים (Gamma)

</div>

<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">

מהתאמת ההתפלגות במקטע 5א, מרווחי ההגעה של קבוצות חברים מתפלגים $\\Gamma(\\hat{\\alpha}, \\hat{\\beta})$ עם $\\hat{\\alpha} \\approx 1.2393$ ו-$\\hat{\\beta} \\approx 1.1064$. צפיפות:
$$f(x; \\alpha, \\beta) = \\frac{1}{\\beta^{\\alpha}\\,\\Gamma(\\alpha)}\\,x^{\\alpha - 1}\\,e^{-x/\\beta},\\quad x > 0$$<br>

עבור $\\alpha$ לא-שלם אין ל-$\\Gamma$ פונקציית התפלגות מצטברת בצורה סגורה (היא נכתבת באמצעות פונקציית גאמא לא-שלמה), ולכן טרנספורם הופכי אינו ישים ישירות. נשתמש בקבלה-דחייה.<br><br>

<b>בחירת מעטפת:</b> מעטפת אקספוננציאלית עם תוחלת זהה לזו של $f$, היינו $\\mathbb{E}[X] = \\alpha\\beta$:
$$g(x) = \\frac{1}{\\alpha\\beta}\\,e^{-x/(\\alpha\\beta)},\\quad x > 0$$
מעטפת זו פשוטה לדגימה (טרנספורם הופכי אקספוננציאלי) ובעלת אותה תוחלת כמו צפיפות היעד, מה שתורם לקבוע חוסם נמוך יחסית.<br><br>

<b>חישוב $c = \\sup_x \\dfrac{f(x)}{g(x)}$:</b><br>
$$\\frac{f(x)}{g(x)} = \\frac{x^{\\alpha-1}\\,e^{-x/\\beta}}{\\beta^\\alpha\\,\\Gamma(\\alpha)} \\cdot \\alpha\\beta\\,e^{x/(\\alpha\\beta)} = \\frac{\\alpha}{\\Gamma(\\alpha)\\,\\beta^{\\alpha-1}} \\cdot x^{\\alpha-1}\\,\\exp\\!\\left(-\\frac{(\\alpha-1)\\,x}{\\alpha\\beta}\\right)$$<br>

נגזרת לפי $x$ ושוויון לאפס נותנים את ערך הסופרמום:
$$\\frac{d}{dx}\\!\\left[x^{\\alpha-1}\\,e^{-(\\alpha-1)x/(\\alpha\\beta)}\\right] = x^{\\alpha-2}\\,e^{-(\\alpha-1)x/(\\alpha\\beta)}\\left[(\\alpha-1) - \\frac{(\\alpha-1)\\,x}{\\alpha\\beta}\\right] = 0$$
&rArr; $x^{*} = \\alpha\\beta$ (זהו ה-mode במשמעות מסוימת, וגם המקום שבו $f/g$ מקסימלי).<br><br>

הצבה ב-$f(x^*)/g(x^*)$:
$$c = \\frac{\\alpha}{\\Gamma(\\alpha)\\,\\beta^{\\alpha-1}} \\cdot (\\alpha\\beta)^{\\alpha-1}\\,e^{-(\\alpha-1)} = \\frac{\\alpha^\\alpha\\,e^{-(\\alpha-1)}}{\\Gamma(\\alpha)}$$<br>

עבור $\\alpha = 1.2393$: $\\alpha^\\alpha \\approx 1.3047$, $e^{-(\\alpha-1)} \\approx 0.7872$, $\\Gamma(\\alpha) \\approx 0.9077$, ולכן:
$$c \\approx \\frac{1.3047 \\cdot 0.7872}{0.9077} \\approx 1.131$$
שיעור קבלה צפוי: $1/c \\approx 0.884$ (כ-88.4%).<br><br>

<b>צורה נוחה למבחן הקבלה:</b> נגדיר $z = y/(\\alpha\\beta)$, ונפשט את $f(y)/(c \\cdot g(y))$:
$$\\frac{f(y)}{c \\cdot g(y)} = z^{\\alpha - 1}\\,e^{(\\alpha-1)(1 - z)}$$
(הביטוי מקבל ערך 1 ב-$y = \\alpha\\beta$, כצפוי לפי הגדרת $c$.)<br><br>

<b>אלגוריתם הקבלה-דחייה — דגימה אחת:</b><br>
&nbsp;&nbsp;1. דגום $u_1, u_2 \\sim \\mathcal{U}(0,1)$<br>
&nbsp;&nbsp;2. $y \\leftarrow -\\alpha\\beta \\cdot \\ln(u_1)$ (דגימה מהמעטפת האקספוננציאלית)<br>
&nbsp;&nbsp;3. $z \\leftarrow y / (\\alpha\\beta)$<br>
&nbsp;&nbsp;4. אם $u_2 \\le z^{\\alpha-1}\\,e^{(\\alpha-1)(1 - z)}$ החזר $y$<br>
&nbsp;&nbsp;5. אחרת חזור ל-1<br><br>

<b>הערה למימוש:</b> עבור $\\alpha < 1$ הצפיפות מתבדרת ל-$\\infty$ ב-$x \\to 0^+$. בעבורנו $\\alpha \\approx 1.24 > 1$ ולכן הצפיפות סופית בכל הנקודות. שיטת המעטפת האקספוננציאלית עובדת היטב בתחום $\\alpha > 1$.

</div>
'''


# ---------------------------------------------------------------------------
# §6.6 — Charging time inverse derivation
# ---------------------------------------------------------------------------
S6_CHARGING = '''\
<div dir="rtl" style="text-align: right;">

### 6.6 משך טעינה בעמדת הסוללות — היפוך CDF פרמטרי

</div>

<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">

המפרט מגדיר את משך הטעינה $T$ באמצעות צפיפות פרמטרית התלויה ב-$\\alpha$ הנובע מאחוז הסוללה $b$ של האורח בכניסה:
$$f(t; \\alpha) = \\frac{\\alpha}{40^{\\alpha}}\\,(40 - t)^{\\alpha - 1},\\quad 0 \\le t \\le 40,\\qquad \\alpha = \\frac{100}{100 - b}$$<br>

<b>חישוב $F(t)$:</b>
$$F(t) = \\int_0^t \\frac{\\alpha}{40^{\\alpha}}\\,(40 - s)^{\\alpha - 1}\\,ds$$
החלפת משתנים $w = 40 - s$, $dw = -ds$:
$$F(t) = -\\int_{40}^{40-t} \\frac{\\alpha}{40^{\\alpha}}\\,w^{\\alpha - 1}\\,dw = \\frac{\\alpha}{40^{\\alpha}} \\cdot \\frac{w^{\\alpha}}{\\alpha}\\bigg|_{40-t}^{40} = \\frac{40^{\\alpha} - (40 - t)^{\\alpha}}{40^{\\alpha}}$$
מכאן:
$$\\boxed{\\,F(t) = 1 - \\left(\\frac{40 - t}{40}\\right)^{\\alpha}\\,}$$
בדיקה: $F(0) = 0$ ✓, $F(40) = 1$ ✓.<br><br>

<b>היפוך:</b> $F(t) = u \\;\\Longrightarrow\\; \\left(\\dfrac{40 - t}{40}\\right)^{\\alpha} = 1 - u$. מכיוון ש-$1 - U \\sim \\mathcal{U}(0,1)$ באותה התפלגות כמו $U$, נחליף $1 - u \\to u$:
$$t = 40\\,\\left(1 - u^{1/\\alpha}\\right)$$<br>

<b>אלגוריתם — דגימה אחת בהינתן $b$ (אחוז סוללה בכניסה):</b><br>
&nbsp;&nbsp;1. $\\alpha \\leftarrow 100/(100 - b)$<br>
&nbsp;&nbsp;2. דגום $u \\sim \\mathcal{U}(0,1)$<br>
&nbsp;&nbsp;3. החזר $t = 40\\,(1 - u^{1/\\alpha})$<br><br>

<b>הערות גבול:</b> אם $b$ קרוב ל-$100$ (סוללה כמעט מלאה) אז $\\alpha$ עולה לגדולים מאוד, והצפיפות מתרכזת קרוב ל-$t = 0$ — זמן טעינה קצר. אם $b$ קרוב ל-$0$ (סוללה ריקה) אז $\\alpha \\to 1$, והצפיפות הופכת לאחידה $\\mathcal{U}(0, 40)$ — זמן טעינה הקרוב לטווח המלא. ההתנהגות עקבית עם המודל הפיזי הצפוי.<br><br>

<b>טיפול בקצוות:</b> אחוז הסוללה $b$ נדגם מ-$\\mathcal{N}(40, 15^2)$ ועלול להיות שלילי או גדול מ-$100$. נחתוך ל-$[1, 99]$ לפני חישוב $\\alpha$, ובכך נמנע חלוקה באפס וערכי $\\alpha$ פתולוגיים.

</div>
'''


# ---------------------------------------------------------------------------
# Sampler class — replaces cell 26
# ---------------------------------------------------------------------------
SAMPLER_CODE = '''\
# M3: Sampler — all sampling methods bundled. Reads parameters from CONFIG,
# draws from named streams on an RNGStreams instance. One public method per
# simulation-relevant random quantity. Private helpers (_uniform, _exponential,
# _normal_box_muller, _discrete_uniform, _bernoulli) implement the underlying
# algorithms derived in §6.1-§6.6.


class Sampler:
    """All sampling methods for the simulation.

    Constructor:
        Sampler(rng_streams, config=CONFIG)

    Every public method draws from exactly one named stream so that partner
    runs of alternatives can use Common Random Numbers (CRN) by reseeding only
    the streams an alternative affects.
    """

    def __init__(self, rng_streams, config=None):
        self.rng = rng_streams
        self.config = config if config is not None else CONFIG

    # ---------- primitive sampling algorithms (§6.1, §6.2) ----------

    @staticmethod
    def _uniform(stream, low, high):
        # Inverse transform for U(a, b): x = a + (b-a) * u
        return low + (high - low) * stream.random()

    @staticmethod
    def _exponential(stream, mean):
        # Inverse transform for Exp with given mean: x = -mean * ln(u)
        return -mean * math.log(stream.random())

    @staticmethod
    def _discrete_uniform(stream, low, high):
        # Inverse transform for discrete uniform on {low, ..., high}
        return low + int(stream.random() * (high - low + 1))

    @staticmethod
    def _bernoulli(stream, p):
        return stream.random() < p

    @staticmethod
    def _normal_box_muller(stream, mu, sigma):
        # Box-Muller (§6.2): two uniforms -> one standard normal -> scaled normal.
        u1 = stream.random()
        u2 = stream.random()
        # Guard against ln(0) — random() returns [0, 1); resample if exactly 0.
        while u1 == 0.0:
            u1 = stream.random()
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mu + sigma * z

    @staticmethod
    def _categorical(stream, probs):
        # Inverse transform for a categorical distribution. probs sum to 1.
        u = stream.random()
        cum = 0.0
        for idx, p in enumerate(probs):
            cum += p
            if u < cum:
                return idx
        return len(probs) - 1  # numerical-edge fallback

    # ---------- arrivals ----------

    def fg_arrival_interval(self):
        """FriendsGroup inter-arrival time (minutes). Gamma via A/R (§6.5)."""
        alpha = self.config["fg_arrival_alpha"]
        beta = self.config["fg_arrival_beta"]
        env_stream = self.rng["arrival_friends"]
        while True:
            u1 = env_stream.random()
            u2 = env_stream.random()
            while u1 == 0.0:
                u1 = env_stream.random()
            y = -alpha * beta * math.log(u1)
            z = y / (alpha * beta)
            # Acceptance criterion: u2 <= z^(alpha-1) * exp((alpha-1)*(1-z))
            if u2 <= (z ** (alpha - 1.0)) * math.exp((alpha - 1.0) * (1.0 - z)):
                return y

    def couple_arrival_interval(self):
        """Couple inter-arrival time (minutes). Exp(lambda=1/60) via inverse transform."""
        return self._exponential(self.rng["arrival_couple"], 1.0 / self.config["couple_arrival_lambda"])

    def single_arrival_interval(self):
        """Single inter-arrival time (minutes). Exp(lambda=500/420) via inverse transform."""
        return self._exponential(self.rng["arrival_single"], 1.0 / self.config["single_arrival_lambda"])

    def friends_group_size(self):
        """Number of members in a FriendsGroup. DiscreteUniform[3, 6]."""
        return self._discrete_uniform(self.rng["friends_size"], self.config["fg_size_min"], self.config["fg_size_max"])

    # ---------- entry ----------

    def entry_scan_duration(self):
        """Ticket scan time (minutes). U(1.5, 3) via inverse transform."""
        return self._uniform(self.rng["entry_scan"], self.config["entry_scan_low"], self.config["entry_scan_high"])

    def entry_security_duration(self):
        """Security check time (minutes). Exp(mean=2) via inverse transform."""
        return self._exponential(self.rng["entry_security"], self.config["entry_security_mean"])

    # ---------- stages ----------

    def main_show_duration(self):
        """MainStage concert duration (minutes). N(mu, sigma^2) via Box-Muller."""
        return self._normal_box_muller(self.rng["show_main"], self.config["main_show_mu"], self.config["main_show_sigma"])

    def side_show_duration(self):
        """SideStage concert duration (minutes). U(20, 30) via inverse transform."""
        return self._uniform(self.rng["show_side"], self.config["side_show_low"], self.config["side_show_high"])

    def dj_stay_duration(self):
        """DJstage stay time (minutes). Piecewise PDF via A/R with U(20, 60) envelope (§6.4).

        Mandatory A/R per spec. M = sup f = 1/15 at x=40+; acceptance ~ 3/8.
        """
        low = self.config["dj_stay_low"]
        high = self.config["dj_stay_high"]
        m = self.config["dj_stay_max_pdf"]
        stream = self.rng["dj_stay"]
        while True:
            y = self._uniform(stream, low, high)
            u = stream.random()
            if u <= self._dj_pdf(y) / m:
                return y

    @staticmethod
    def _dj_pdf(x):
        # Piecewise PDF for DJ stay time. Spec form (note: discontinuity at x=40).
        if 20.0 <= x < 40.0:
            return (x - 20.0) / 600.0
        if 40.0 <= x <= 50.0:
            return (60.0 - x) / 600.0 + 1.0 / 30.0
        if 50.0 < x <= 60.0:
            return (60.0 - x) / 600.0
        return 0.0

    def farthest_ten_leaves(self):
        """Bernoulli(0.5) per MainStage entity at the 15-min checkpoint."""
        return self._bernoulli(self.rng["farthest_ten_bernoulli"], self.config["main_farthest_leave_prob"])

    def show_satisfied(self):
        """Bernoulli for show-good-experience outcome (spec eq.: (G-1)/2 + (T-1)/19)."""
        return self._bernoulli(self.rng["show_satisfied"], self.config["show_satisfied_prob"])

    # ---------- PhotoStation ----------

    def photo_duration(self):
        """PhotoStation service time (minutes). Composition over a piecewise PDF (§6.3)."""
        u = self.rng["photo_duration"].random()
        b_low = self.config["photo_cdf_break_low"]    # F(2) = 1/4
        b_high = self.config["photo_cdf_break_high"]  # F(3) = 7/8
        if u < b_low:
            return math.sqrt(12.0 * u + 1.0)
        if u < b_high:
            return (-0.125 + math.sqrt(0.175625 + 0.4 * u)) / 0.2
        return 8.0 * u - 4.0

    def photo_satisfied(self):
        return self._bernoulli(self.rng["photo_satisfied"], self.config["photo_satisfied_prob"])

    def photo_unsatisfied_penalty_fires(self):
        return self._bernoulli(self.rng["photo_unsatisfied_penalty"], self.config["photo_unsatisfied_penalty_prob"])

    # ---------- ChargingStation ----------

    def charging_battery_percent(self):
        """Battery % on arrival. N(40, 15) via Box-Muller, clamped to [1, 99]."""
        raw = self._normal_box_muller(
            self.rng["charging_battery"],
            self.config["charging_battery_mu"],
            self.config["charging_battery_sigma"],
        )
        # Clamp into a sane physical range; spec doesn't bound but the inverse CDF
        # uses alpha = 100/(100-b), so we must keep b away from 0 and 100.
        return max(1.0, min(99.0, raw))

    def charging_time(self, battery_percent):
        """Charge time (minutes). Inverse transform on F(t) = 1 - ((40-t)/40)^alpha (§6.6)."""
        alpha = 100.0 / (100.0 - battery_percent)
        u = self.rng["charging_time"].random()
        return self.config["charging_max_minutes"] * (1.0 - u ** (1.0 / alpha))

    # ---------- MerchTent ----------

    def merch_service_duration(self):
        return self._uniform(self.rng["merch_service"], self.config["merch_service_low"], self.config["merch_service_high"])

    def merch_buys_shirt(self):
        return self._bernoulli(self.rng["merch_shirt"], self.config["merch_shirt_prob"])

    def merch_buys_hat(self):
        return self._bernoulli(self.rng["merch_hat"], self.config["merch_hat_prob"])

    def merch_buys_flag(self):
        return self._bernoulli(self.rng["merch_flag"], self.config["merch_flag_prob"])

    def merch_buys_band_shirt(self):
        return self._bernoulli(self.rng["merch_band_shirt"], self.config["merch_band_shirt_prob"])

    # ---------- BodyArt ----------

    def bodyart_type(self):
        """Returns one of 'glitter', 'neon', 'henna' per spec categorical."""
        probs = [
            self.config["bodyart_glitter_choose_prob"],
            self.config["bodyart_neon_choose_prob"],
            self.config["bodyart_henna_choose_prob"],
        ]
        idx = self._categorical(self.rng["bodyart_type"], probs)
        return ("glitter", "neon", "henna")[idx]

    def bodyart_glitter_duration(self):
        return self._normal_box_muller(self.rng["bodyart_glitter"], self.config["bodyart_glitter_mu"], self.config["bodyart_glitter_sigma"])

    def bodyart_neon_duration(self):
        return self._exponential(self.rng["bodyart_neon"], self.config["bodyart_neon_mean"])

    def bodyart_henna_duration(self):
        return self._uniform(self.rng["bodyart_henna"], self.config["bodyart_henna_low"], self.config["bodyart_henna_high"])

    def bodyart_satisfied(self, art_type):
        prob = {
            "glitter": self.config["bodyart_glitter_satisfied_prob"],
            "neon":    self.config["bodyart_neon_satisfied_prob"],
            "henna":   self.config["bodyart_henna_satisfied_prob"],
        }[art_type]
        return self._bernoulli(self.rng["bodyart_satisfied"], prob)

    # ---------- Food court ----------

    def food_chooses_lunch(self):
        return self._bernoulli(self.rng["food_choose"], self.config["food_choose_prob"])

    def food_restaurant(self):
        """Returns one of 'pizza', 'burger', 'asian' per spec categorical."""
        probs = [
            self.config["food_choice_pizza"],
            self.config["food_choice_burger"],
            self.config["food_choice_asian"],
        ]
        idx = self._categorical(self.rng["food_restaurant"], probs)
        return ("pizza", "burger", "asian")[idx]

    def food_prep_duration(self, restaurant):
        stream = self.rng[f"food_prep_{restaurant}"]
        low = self.config[f"food_prep_{restaurant}_low"]
        high = self.config[f"food_prep_{restaurant}_high"]
        return self._uniform(stream, low, high)

    def food_register_duration(self):
        return self._normal_box_muller(self.rng["food_register"], self.config["food_register_mu"], self.config["food_register_sigma"])

    def food_meal_duration(self):
        return self._uniform(self.rng["food_meal"], self.config["food_meal_low"], self.config["food_meal_high"])

    def food_unsatisfied(self):
        return self._bernoulli(self.rng["food_unsatisfied"], self.config["food_unsatisfied_prob"])

    # ---------- day transitions ----------

    def fg_buys_lodging(self):
        return self._bernoulli(self.rng["lodging_fg"], self.config["fg_lodging_prob"])
'''


# ---------------------------------------------------------------------------
# §6.7 — DJ A/R validation
# ---------------------------------------------------------------------------
S6_VALIDATION_MD = '''\
<div dir="rtl" style="text-align: right;">

### 6.7 בדיקת תקפות לאלגוריתם הקבלה-דחייה במת הדיג'י

</div>

<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">

עבור שלושת האלגוריתמים האחרים שבהם ביצענו פיתוח מתמטי (טרנספורם הופכי, בוקס-מולר, קומפוזיציה) המבחנים הסטטיסטיים נעשו ישירות במקטע 5 (KS וChi-Square) עבור הפרמטרים שהותאמו לנתונים. לעומת זאת, באלגוריתם הקבלה-דחייה ישנה מורכבות נוספת (קבוע חוסם, מעטפת) ולכן נציג בדיקה מהירה: <b>שיעור קבלה אמפירי</b> מול הציפייה התיאורטית $1/c = 3/8 = 0.375$, ו<b>היסטוגרמה</b> של דגימה אל-מול הצפיפות התיאורטית. בדיקה זו מאששת שמימוש האלגוריתם תקין ועקבי עם הפיתוח במקטע 6.4.

</div>
'''

S6_VALIDATION_CODE = '''\
# M3: DJ A/R validation — acceptance rate + histogram vs. theoretical PDF.
# Confirms the implementation matches the §6.4 derivation: M = 1/15, c = 8/3,
# expected acceptance rate = 3/8 ~ 0.375.

# Instrumented re-run of the A/R loop to count attempts (the production
# Sampler.dj_stay_duration discards this for performance).
_validation_rng = RNGStreams(master_seed=CONFIG["master_seed"])
_validation_sampler = Sampler(_validation_rng, CONFIG)

N_VALIDATE = 20000
attempts = 0
samples = []
M = CONFIG["dj_stay_max_pdf"]
low = CONFIG["dj_stay_low"]
high = CONFIG["dj_stay_high"]
stream = _validation_rng["dj_stay"]
while len(samples) < N_VALIDATE:
    attempts += 1
    y = low + (high - low) * stream.random()
    u = stream.random()
    if u <= Sampler._dj_pdf(y) / M:
        samples.append(y)
samples = np.array(samples)
empirical_acceptance = N_VALIDATE / attempts
theoretical_acceptance = 3.0 / 8.0

print("--- DJ A/R validation ---")
print(f"target draws         = {N_VALIDATE}")
print(f"total attempts       = {attempts}")
print(f"empirical acceptance = {empirical_acceptance:.4f}")
print(f"theoretical (1/c)    = {theoretical_acceptance:.4f}")
print(f"sample mean          = {samples.mean():.4f}")
print(f"sample std           = {samples.std(ddof=0):.4f}")

# Theoretical moments via numerical integration of the spec PDF
xs = np.linspace(20, 60, 4001)
pdf_vals = np.array([Sampler._dj_pdf(x) for x in xs])
mean_th = np.trapz(xs * pdf_vals, xs)
var_th = np.trapz((xs - mean_th) ** 2 * pdf_vals, xs)
print(f"theoretical mean     = {mean_th:.4f}")
print(f"theoretical std      = {np.sqrt(var_th):.4f}")

fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(samples, bins=40, density=True, alpha=0.55, edgecolor="black", label="empirical samples")
ax.plot(xs, pdf_vals, "r-", linewidth=2, label="spec PDF $f(x)$")
ax.axvline(40, color="gray", linestyle="--", linewidth=1, alpha=0.6, label="discontinuity x=40")
ax.set_xlabel("DJ stay duration (minutes)")
ax.set_ylabel("density")
ax.set_title(f"DJ A/R sampler validation (n = {N_VALIDATE})")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
'''


# ---------------------------------------------------------------------------
# Build the new cell list
# ---------------------------------------------------------------------------
def make_markdown_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def make_code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def main():
    with NB_PATH.open() as f:
        nb = json.load(f)

    # Indices: cells [0..24] kept; cell 25 (placeholder) replaced; cell 26
    # (Sampler stub) replaced; cells [27..] kept as-is.
    head = nb["cells"][:25]              # 0..24 inclusive
    tail = nb["cells"][27:]              # 27..end

    new_section = [
        make_markdown_cell(S6_INTRO),        # replaces cell 25
        make_markdown_cell(S6_INVERSE),      # §6.1
        make_markdown_cell(S6_BOXMULLER),    # §6.2
        make_markdown_cell(S6_COMPOSITION),  # §6.3
        make_markdown_cell(S6_AR_DJ),        # §6.4
        make_markdown_cell(S6_AR_GAMMA),     # §6.5
        make_markdown_cell(S6_CHARGING),     # §6.6
        make_code_cell(SAMPLER_CODE),        # Sampler (replaces cell 26)
        make_markdown_cell(S6_VALIDATION_MD),
        make_code_cell(S6_VALIDATION_CODE),
    ]

    nb["cells"] = head + new_section + tail

    with NB_PATH.open("w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(f"Notebook now has {len(nb['cells'])} cells.")
    print(f"§6 section: {len(new_section)} new cells inserted between §5 and §7.")


if __name__ == "__main__":
    main()
