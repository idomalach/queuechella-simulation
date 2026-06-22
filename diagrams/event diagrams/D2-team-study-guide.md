# מדריך פנימי לצוות — תרשים D2: ShowStart@MainStage
## לא להגשה — הכנה לשאלות המרצה

---

## מה זה ShowStart@MainStage ולמה הוא קיים?

ShowStart@MainStage הוא האירוע שמפעיל כל הופעה בבמה הראשית.
הוא אחראי על שלושה דברים: קביעת משך ההופעה, קבלת קהל מהתור, ותזמון EarlyExitCheck לכל מי שנכנס.
הוא לא מתזמן את עצמו הלאה — זו אחריות של ShowEnd.

---

## פירוט קוד לכל צומת

### צומת 2 — Box-Muller לדגימת משך ההופעה

**למה Box-Muller?** כי Python's `random.normalvariate` משתמש בשיטה זו פנימית.
אנחנו קוראים ישירות ל-`sim.sampler.main_show_duration()` שמחזיר ערך נורמלי עם μ ו-σ מ-CONFIG.

```python
duration = sim.sampler.main_show_duration()
# duration ~ Normal(μ=CONFIG["main_show_mean"], σ=CONFIG["main_show_std"])
# מוצמד מינימום ל-CONFIG["main_show_min"] כדי למנוע הופעה שלילית
```

**שאלה:** למה לא פואסון?
**תשובה:** משך הופעה הוא כמות רציפה סביב ממוצע קבוע — לא תהליך מניין. נורמל מתאים יותר לפי ניתוח הנתונים.

---

### צומת 3-6 — לולאת מילוי הבמה (fill-to-max)

```python
admitted = []
queue = sim.activities["MainStage"].queue

for entity in list(queue.entities):  # עותק כדי לא לשנות בזמן iteration
    if sim.activities["MainStage"].is_full():
        break
    if sim.activities["MainStage"].free_slots() >= entity.size:
        queue.remove(entity)
        sim.activities["MainStage"].admit(entity)
        sim.kpi.record_wait(entity, sim.clock)
        admitted.append(entity)
    # אם לא מתאים — מדלגים, לא מסירים מהתור
```

**שאלה:** למה לא נוקטים בפשוט — פשוט לקחת את הראשון?
**תשובה:** כי קבוצת חברים עשויה להיות גדולה מהמקום שנשאר. אם לא נדלג עליה, נפסיד קבלת זוגות ויחידים שיכולים להיכנס. הלולאה ממשיכה לבדוק את כולם.

**שאלה:** מה קורה לישות שדילגו עליה?
**תשובה:** היא נשארת בתור ותוכל להיכנס להופעה הבאה.

---

### צומת 7 — תזמון ShowEnd

```python
sim.schedule(ShowEnd_MainStage(time=sim.clock + duration))
sim.activities["MainStage"].current_show = {
    "start": sim.clock,
    "duration": duration,
    "admitted": admitted
}
```

**שאלה:** למה ShowStart לא מתזמנת את עצמה הלאה?
**תשובה:** החלטה M9 — ShowEnd מתזמן את ShowStart הבאה עם הפסקה (10 דקות). כך הפסקה בין הופעות נשלטת במקום אחד בלבד.

---

### צומת 8 — EarlyExitCheck לכל ישות שנכנסה

```python
for entity in admitted:
    sim.schedule(EarlyExitCheck(
        entity=entity,
        time=sim.clock + 15  # 15 דקות מתחילת ההופעה
    ))
```

**מה זה EarlyExitCheck?**
אירוע נפרד (#20 מתוך 23) שבודק אם הישות נמצאת בעשרת האחרונים שנכנסו (farthest-10).
אם כן — מטיל Bernoulli(0.5): עם הסתברות 50% הישות עוזבת מוקדם.

**שאלה:** למה 15 דקות?
**תשובה:** זה הזמן שלפיו מישהו שעומד "בפינה" מרגיש שמספיק לו ויוצא. מוגדר ב-CONFIG כ-`early_exit_check_delay`.

**שאלה:** האם EarlyExitCheck הוא חלק מ-ShowStart?
**תשובה:** לא. הוא אירוע עצמאי שמופעל 15 דקות אחרי. ShowStart רק מתזמן אותו. כשהוא מופעל — ShowStart כבר סיים ואינו רלוונטי.

**שאלה:** מה קורה לישות שעוזבת מוקדם?
**תשובה:**
- FriendsGroup או Single — מנסים שוב להיכנס להופעה (re-queue)
- Couple — ממשיך למסלול הבא ב-itinerary שלו

---

## הנחות ושאלות מתגרות

**"למה farthest-10 ולא farthest-5 או farthest-20?"**
10 הוא פרמטר CONFIG — `early_exit_n`. הוא נקבע לפי שיקול מציאותי: בהופעה גדולה, מי שנכנס אחרון עומד הכי רחוק ויש לו סיכוי יותר גבוה לצאת. בחרנו 10 כ-default ואחת החלופות בוחנת ערך שונה.

**"מה ה-farthest-10 בדיוק?"**
`sim.activities["MainStage"].attendees[-10:]` — עשרת הישויות האחרונות שנכנסו. לא לפי מיקום פיזי אלא לפי סדר כניסה.

**"מה קורה אם פחות מ-10 ישויות בהופעה?"**
הבדיקה חלה על כולן — `attendees[-10:]` פשוט יחזיר את כולן.

**"למה לא לבדוק יציאה מוקדמת מיד בהתחלה?"**
כי אנשים לא עוזבים הופעה בדקה הראשונה. 15 דקות מדמים את הזמן שלוקח להחליט שהמקום לא מספיק טוב.

**"מה יקרה אם הבמה תמיד מלאה?"**
ישויות יצטברו בתור. עם זמן המתנה ארוך — AbandonQueue יופעל לאחר 15-20 דקות (לפי סוג הישות) ויוציא אותן מהתור עם קנס סיפוק.

**"האם ShowStart יכול לקרות כשהבמה ריקה לגמרי?"**
כן — אם כולם עזבו מוקדם דרך EarlyExitCheck או אם התור היה ריק. ההופעה מתחילה עם 0 נוכחים, ShowEnd יתוזמן, והחיים ממשיכים.

---

## ציר הזמן של אירועי הבמה הראשית

```
t=0        ShowStart מוזרע לרשימת האירועים ל-09:00
t=540      ShowStart@Main מופעל
           ← דגימת משך (לדוגמה: 60 דקות)
           ← קבלת קהל
           ← EarlyExitCheck מתוזמן לכולם ל-t=555
           ← ShowEnd מתוזמן ל-t=600
t=555      EarlyExitCheck מופעל — farthest-10 בודקים
t=600      ShowEnd מופעל
           ← קהל משוחרר
           ← ShowStart הבאה מתוזמנת ל-t=610 (הפסקה 10 דקות)
t=610      ShowStart@Main מופעל שוב
```
