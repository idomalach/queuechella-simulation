# Instructions Coverage — Queuechella Simulation (Group 20)

Tracker that mirrors `Course Project 2026B.pdf`. Every spec bullet → one checkbox.
Owner tag: **[USER]** = Ido (milestones M0–M5), **[PARTNERS]** = Yonatan + Etan (items 4–5 in סדר העבודה).

---

## 📌 Partner handoff — read this first

When you (Yonatan / Etan) pick up this notebook, please:

1. **Maintain the GenAI usage log** in §20 of the notebook. Every time you use a GenAI tool, add a row (date, tool, purpose, short description). This becomes the source for the official declaration form at submission.
2. **Check off items below** as you complete them.
3. **Consult §2 of the notebook** — the "13-item Design Decisions Log" (inside a yellow internal div) documents every spec ambiguity that was resolved during planning. If you hit a question about spec interpretation, look there first.
4. **CONFIG cell** at the top of the notebook documents the alternatives ↔ parameter mapping. Flip the relevant fields when implementing alternatives in §17.
5. **Sampler index** is in §6 — every sampler is in the `Sampler` class, called via `sampler.<name>()`. RNG stream naming is in §12 (`RNGStreams`).
6. **Internal yellow divs** (marked `INTERNAL — DELETE BEFORE SUBMISSION`) must be regex-stripped before final submission. There's a deletion checklist at the top of the notebook.

---

## M0 — Setup [USER]

- [x] Install Python deps (`pandas numpy scipy matplotlib openpyxl jupyter`) — venv at `~/venvs/Simulation_Project/` (never inside the iCloud-synced project dir).
- [x] Create `diagrams/` folder.
- [x] Create `Queuechella_Simulation.ipynb` with full 20-section skeleton.
- [x] Create this file (`instructions_coverage.md`).
- [ ] Smoke-test: notebook executes top-to-bottom without error; xlsx loads.

---

## Spec §"להלן כמה דגשים חשובים" — Project framing

- [ ] **[USER M3]** Implement sampling algorithm before sampling random numbers (Box-Muller for normal, inverse transform, composition, OR acceptance-rejection).
- [x] **[USER M2]** Fit distributions for the two sheets in `samples_for_simulation.xlsx` — FriendsGroup arrivals: **Gamma**(r≈1.239, λ≈0.904) — switched from Exp after moment-based analysis; MainStage duration: **Normal**(μ≈45.90, σ≈8.93). Both pass KS + Chi²(k=12) at α=0.05.
- [ ] **[PARTNERS]** Event-driven modeling of current state; modular + readable code (OOP, Top-Down).
- [ ] **[PARTNERS]** Choose 2–3 KPIs (we've pre-chosen: satisfaction at exit / avg+max queue wait / revenue — confirm in §4).
- [ ] **[PARTNERS]** Test alternatives within 1,000,000 NIS budget; justify statistically + logically.

### סדר העבודה
- [x] **[USER M2]** 1. התאמת התפלגות. (FG/Gamma + MS/Normal — נוטבוק §5)
- [ ] **[USER M3]** 2. אלגוריתמי דגימה.
- [ ] **[USER M4]** 3. מחלקות ושיטות.
- [ ] **[PARTNERS]** 4. לוגיקה (תכנות מונחה אירועים) — after week 6/7.
- [ ] **[PARTNERS]** 5. חישוב מספר הרצות + השוואה סטטיסטית — after week 10.

### Pre-work diagrams (required *before* implementing current state)
- [ ] **[USER M1]** Event diagram (תרשים אירועים) — all event types as bubbles. Embed PNG in notebook §3.
- [ ] **[USER M1]** Handling diagram #1 — QueueAbandonment.
- [ ] **[USER M1]** Handling diagram #2 — MainStage_ShowStart.
- [ ] **[USER M1]** Handling diagram #3 — EndOfDay.

---

## Spec §"דרישת העבודה" — Deliverables

- [ ] **[USER+PARTNERS]** Single COLAB notebook with:
  - [ ] **[USER+PARTNERS]** (a) Code blocks with English-only code comments; OOP, Top-Down, efficient, correct.
  - [ ] **[USER+PARTNERS]** (b) Text in appropriate places forming a written simulation report: intro, system description with flow/process diagram, mathematical explanations (formulas) for distribution fitting + sampling algorithms, event-programming implementation + event diagram + assumptions, explanation of chosen alternatives + implementation, run-count calculation, alternative comparison, recommendations, summary.
- [ ] **[PARTNERS+USER]** Summary presentation (7 min + 3 min Q&A; all team members present).
- [ ] **[PARTNERS+USER]** 10-min defense — all members show command of code + work.
- [ ] **Submission deadline:** 2026-06-29 (Sunday of week 13). Defenses + presentations happen this week.

---

## Spec §"מצב קיים" — Current state baseline

### General
- [ ] **[PARTNERS]** Festival operates 2 days, 09:00–20:00 each day.
- [ ] **[USER M4]** Each visitor has a personal satisfaction score: initial=5, max=10, min=0.

### Visitor types — entities

**1. FriendsGroup**
- [ ] **[USER M3]** Group size: DiscreteUniform[3,6].
- [x] **[USER M2]** / [ ] **[USER M3]** Arrival rate: from xlsx — Gamma(r≈1.239, λ≈0.904) fitted (M2 done). M3 will sample via **Acceptance-Rejection with an Exponential envelope** (Gamma has no closed-form inverse CDF for non-integer shape; A-R is course-taught + mandatory for DJ stage anyway).
- [ ] **[PARTNERS]** Arrive 09:00–13:00, Day 1 only.
- [ ] **[USER M4]** With p=0.7, group stays overnight (continues to Day 2).
- [ ] **[PARTNERS]** Itinerary: one show of each genre + all stations, shortest-queue priority.

**2. Couple**
- [ ] **[USER M3]** Arrival rate: Exp(mean=60/hr).
- [ ] **[PARTNERS]** Arrive 10:00–16:00, both days allowed.
- [ ] **[PARTNERS]** If Day 1 and satisfaction>7 at day end → stay overnight (250 NIS).
- [ ] **[PARTNERS]** Alternate show↔station; uniform random; no electronic music.

**3. Single**
- [ ] **[USER M3]** Arrival rate: Exp(mean=500/day).
- [ ] **[PARTNERS]** Arrive 09:00–16:00, either day.
- [ ] **[PARTNERS]** Itinerary: MerchTent → 2 mainstream + 2 indie + 1 electronic shows (full), shortest-queue.
- [ ] **[PARTNERS]** One day only.

### Facility types

**1. MainStage**
- [ ] **[USER M4]** Mainstream genre. 10-min break between shows.
- [x] **[USER M2]** / [ ] **[USER M3]** Show duration: from xlsx — Normal(μ≈45.90, σ≈8.93) fitted (M2 done). M3 will sample via Box-Muller.
- [ ] **[USER M4]** Capacity 200 per show.
- [ ] **[PARTNERS]** Entry order → spatial position (first in = closest to stage).
- [ ] **[PARTNERS]** Farthest 10 entities leave 15 min after entering with p=0.5.
- [ ] **[PARTNERS]** Rolling admission — if a spot opens during the show, queue head can enter.

**2. SideStage**
- [ ] **[USER M4]** Indie genre. 5-min break between shows.
- [ ] **[USER M3]** Show duration: U(20, 30).
- [ ] **[USER M4]** Capacity 100 per show.

**3. DJstage**
- [ ] **[USER M4]** Electronic music continuously throughout festival hours.
- [ ] **[USER M4]** Capacity 70 at any instant.
- [ ] **[USER M3]** Stay duration: piecewise PDF — **must be sampled via acceptance-rejection** (mandatory).

**4. PhotoStation**
- [ ] **[USER M4]** 3 stations, shared queue.
- [ ] **[USER M3]** Photo duration: piecewise PDF (identical to example) — **composition** (notebook §6.3: one recycled *u* selects the segment + inverts within it via the global piecewise CDF; equivalently a piecewise inverse transform).
- [ ] **[USER M4]** With p=0.7, satisfied → satisfaction +2, buy print 30 NIS.
- [ ] **[USER M4]** Else with p=0.5, satisfaction −0.5.

**5. ChargingStation**
- [ ] **[USER M4]** 150 chargers.
- [ ] **[USER M3]** Battery on arrival: N(40, 15) — Box-Muller.
- [ ] **[USER M3]** Charge duration: f(t) = (α/40^α)(40−t)^(α−1), α = 100/(100−b) — inverse transform on derived CDF.

**6. MerchTent**
- [ ] **[USER M4]** 7 registers.
- [ ] **[USER M3]** Service time: U(2, 6).
- [ ] **[USER M4]** Per visitor purchases (independent Bernoullis): shirt p=0.8/100 NIS, hat p=0.4/50 NIS, flag p=0.9/40 NIS, band shirt p=0.3/200 NIS.

**7. BodyArt**
- [ ] **[USER M4]** 2 artists.
- [ ] **[USER M4]** Art choice: glitter p=0.3 / neon p=0.3 / henna p=0.4.
- [ ] **[USER M4]** Satisfaction outcomes per art: glitter satisfied p=0.7 / +0.8; neon satisfied p=0.6 / +1.2; henna satisfied p=0.8 / +0.7.
- [ ] **[USER M3]** Duration: glitter N(15, 3) Box-Muller; neon Exp(12); henna U(17, 22).
- [ ] **[USER M4]** Artist 15-min break per 10 drawings.

### Important notes

- [ ] **[USER M4]** Abandonment tolerances + penalties: FriendsGroup 15 min / −2; Couple 20 min / −1.5; Single 20 min / −1.
- [ ] **[PARTNERS]** Entity moves as a group — no member proceeds until all finish current activity.
- [ ] **[PARTNERS]** Post-show satisfaction update: w.p. 0.5, score = (G−1)/2 + (T−1)/19 with G ∈ {3=main, 2=indie, 1=electronic} and T = end hour. W.p. 0.5, satisfaction −1.
- [ ] **[USER M4]** Entry station: 5 clerks. Ticket scan U(1.5, 3) min. Security check Exp(mean=2) min.
- [ ] **[USER M4]** Costs: entry 500 NIS; lodging add 250 NIS; entry+lodging combo 700 NIS.
- [ ] **[PARTNERS]** Fill-to-max admission policy (scan queue head→tail, admit any entity whose size ≤ remaining capacity).

### Food court (13:00–15:00 only)

- [ ] **[USER M4]** Restaurants: Pizza, Burger, Asian.
- [ ] **[PARTNERS]** Choice probability: 70% of visitors finishing activity in window will eat.
- [ ] **[USER M3]** Pizza prep: U(4, 6); personal 40 NIS; family tray 100 NIS (≥3 people).
- [ ] **[USER M4]** Singles only order personal pizza.
- [ ] **[USER M3]** Burger prep: U(3, 4); meal 100 NIS (with chips + drink).
- [ ] **[USER M3]** Asian prep: U(3, 7); meal 65 NIS.
- [ ] **[USER M3]** Restaurant preference: Burger 3/8, Pizza 1/4, Asian remaining.
- [ ] **[USER M4]** 1 register per restaurant; service time N(5, 1.5) Box-Muller.
- [ ] **[USER M3]** Meal duration (food→back to park): U(15, 35).
- [ ] **[USER M4]** W.p. 0.4, dissatisfied with meal → satisfaction −0.6.

---

## Spec §"חלופות" — Alternatives (budget 1,000,000 NIS)

- [ ] **[PARTNERS]** Choose ≥2 combinations within budget, **using most of the ₪1M** (spec: *"המטרה היא להשתמש ברובו"*). Justify based on current state.
- [ ] **[PARTNERS]** Compute required **run count** (terminating: N independent replications of the full 2-day run, **no warmup deletion**); compare alternatives↔baseline with a **paired t-test** (CRN); overall confidence 0.9 (**Bonferroni-split** across metric×comparison tests); relative precision 0.1.
- [ ] **[PARTNERS]** Final recommendations with statistical + logical justification.

Alternative roster (handled by partners; CONFIG cell at top of notebook documents which CONFIG fields each one flips):
- [ ] **[PARTNERS]** Better kitchen team — 500K NIS (bad-dish prob 0.4→**0.1** [spec "קטנה ל-0.1" = drops *to* 0.1, same `ל` as eat-share "יעלה ל-85" = *to* 85%; corrected 2026-05-30, was 0.3]; eat-share →85%).
- [ ] **[PARTNERS]** Expanded security (capacity +30%) — 650K NIS.
- [ ] **[PARTNERS]** Mainstream investment — 300K NIS.
- [ ] **[PARTNERS]** Photo + BodyArt expansion — 150K NIS.
- [ ] **[PARTNERS]** Advertising — 200K NIS.
- [ ] **[PARTNERS]** Auto entry — 600K NIS.
- [ ] **[PARTNERS]** Visitor gifts — 200K NIS.

---

## Cross-cutting deliverable hygiene

- [ ] **[USER+PARTNERS]** GenAI usage log in §20 — every tool/use logged with date, tool, purpose, description.
- [ ] **[USER+PARTNERS]** Internal yellow divs stripped before submission (regex `INTERNAL — DELETE BEFORE SUBMISSION`).
- [ ] **[USER]** Local xlsx path → public GitHub raw URL before Colab handoff.
- [ ] **[USER+PARTNERS]** Final notebook runs top-to-bottom in Colab without errors.
