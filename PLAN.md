# PLAN 2.0 — Queuechella Simulation (User's Part: Pre-work + Distribution Fitting + Sampling + OOP Design)

> **Version 2.0 (2026-05-29).** This supersedes PLAN v1 and merges it with `EVENT_DECOMPOSITION.md`.
> The decomposition doc is now the canonical deep reference for M1 (event model: Steps 1–5, state/accumulator tables, handler pseudocode). This file is the authoritative **milestone plan + locked design decisions**. Where the two ever disagreed, the reconciliation is recorded in **§ Reconciliation (v1 → v2)** below.

---

## Context

Simulation course capstone (semester B 2026, due **2026-06-29**). Group #20: Ido Malach 318782208, Yonatan Dolman 208987644, Etan Cohen 322067448. Event-driven simulation of the "Queuechella" two-day music festival (09:00–20:00 each day). 47% of course grade (notebook + presentations + defense).

The user owns the **first half** — items 1-3 of "סדר העבודה" (distribution fitting → sampling → classes/methods) + all pre-work (diagrams) — and hands off to partners for items 4-5 (event-driven logic + output analysis + alternatives comparison + report polish).

Cross-cutting requirements:
1. **Dual-tier documentation**: assignment-required Hebrew narrative stays in the final notebook; partner-only handoff notes live in visually-distinct internal divs that are regex-stripped before submission.
2. **GenAI usage must be declared** (syllabus). Maintain an in-notebook log (final §) throughout; it becomes the official declaration at submission. Partners continue it.

KPIs (locked, so the OOP design wires them up): **average visitor satisfaction at exit**, **average + max queue wait time across stations**, **festival revenue**.

Narrative language: **Hebrew** (mirrors lecturer's example). Code comments: **English only** (assignment requirement).

---

## Reconciliation (v1 → v2) — what changed and why

PLAN v1's M1 sketch and several design decisions were **stale**: `EVENT_DECOMPOSITION.md` had recorded resolutions and claimed PLAN.md was updated to match, but that update never landed on disk. v2 applies them all. The substantive changes:

| # | Topic | v1 (stale) | v2 (locked) | Basis |
|---|---|---|---|---|
| R1 | **Couple arrival rate** ⚠️ | `λ=1/60 /min` → ~6 couples/day (60× too slow) | **`λ=1 /min` → 60/hr → ~360/day** | Spec *"תוחלת של 60 בשעה"* parallels Single's *"תוחלת של 500 ביום"* = count per period. **Live bug in CONFIG cell 4 — fix in M3 verification.** |
| R2 | **PhotoStation rolls** | per visitor | **per entity** (one photo, one shared roll; satisfied→every member +2 & +₪30 once; else 0.5→every member −0.5) | Spec *"היישות מרוצה"* |
| R3 | **Food-court abandonment** | YES | **NO** — abandonment is at **4 venues only**: Photo, Charging, Merch, BodyArt | Professor-confirmed |
| R4 | **Couple overnight rule** | either member > 7 | **average(member1, member2) > 7** | User-confirmed 2026-05-29; matches spec's singular metric |
| R5 | **FriendsGroup itinerary** | one pool, shortest queue | **strict phasing**: Phase 1 = 3 shows (one of each genre), then Phase 2 = 4 stations; shortest-queue *within* phase | Spec *"לאחר שהות מלאה בכל הופעה יעברו בכלל העמדות"* |
| R6 | **Abandonment commit** | disarm when **last** member enters service; in-service branch on fire | **commit-on-first**: AbandonQueue cancelled the moment the **first** member starts service; on fire, no member is in service (in-service branch deleted) | Decomp simplification |
| R7 | **Day-end events** | single `EndOfDay` w/ Day1/Day2 branch | **`EndOfDay1`** (checkpoint + overnight decisions) + **`EndOfFestival`** (hard end) + **`Day2Resume`** | Decomp |
| R8 | **Event catalog** | ~16 bubbles | **23 nodes** (see § Event catalog); renamed throughout | Decomp + R9 |
| R9 | **EndOfStay** | implicit | **dedicated event node** (#23) — per-entity departure that logs each member's final satisfaction | User-confirmed 2026-05-29 |
| R10 | **Per-member parallel service** | unspecified | **explicit**: at Entry/Charging/Merch/BodyArt, `slots = min(remaining_members, free_servers)`; same-entity members grab freed servers first; entity exits at `max(member_end_times)` | Decomp |
| R11 | **Food court** | single internal `EndFood` | **3 events** (`EndOrder`/`EndPrep`/`EndEating`) × restaurant; members may split across restaurants; same-entity-same-restaurant order together; **family-pizza minimize-cost** (`floor(N/3)` family ₪100 + `N mod 3` personal ₪40); regroup at `max(EndEating)` | Decomp + user-confirmed 2026-05-29 |
| R12 | **Just-in-time sampling** | unstated | **draw at moment of use** (e.g. Merch `U(2,6)` at service start), CRN-friendly | Decomp |
| R13 | **Farthest-10 early exit** | Bernoulli(0.5) | **Bernoulli(0.5)** — confirmed **spec-mandated** | Spec MainStage bullet ends *"…יעזבו את ההופעה 15 דקות לאחר שנכנסו ויפנו למתחם בהסתברות 0.5"*. (An earlier note calling this beyond-spec was a misread — corrected.) |
| R14 | **Satisfaction clamp** | implicit bounds | **explicit clamp to [0, 10]** in every handler that mutates satisfaction | Decomp |

Everything in v1's M0/M2/M3/M4/M5 scaffolding, notebook layout, documentation conventions, and CONFIG→alternatives map is carried forward unchanged except where a row above touches it.

---

## Scope — what is NOT in this plan

- Notebook §12 onward (concrete Event subclasses + handling logic, Simulation.run loop, warmup, KPI reports, alternatives runs, Welch comparison, summary/recommendations) — **partners** (item 4-5 of סדר העבודה).
- Slides + oral defense — group collective, later.
- CONFIG→alternatives map is *defined* here as a handoff artifact; the actual swapping/runs are partners' work.

---

## Working environment & Colab bridge

- **Master notebook:** `Queuechella_Simulation.ipynb` at project root (79 cells, M0 skeleton built; M2/M3 filled; M4 stubs). Single source of truth; developed locally in Antigravity (VSCode), final delivery in Colab.
- **Diagrams:** Excalidraw MCP tools (`mcp__claude_ai_Excalidraw__*`) — produce all four diagrams (event diagram + 3 handling diagrams). Export PNGs to `diagrams/`. Embed into Colab markdown via base64 data URI (matching example's pattern). One "Colab insertion pass" per diagram milestone.
- **xlsx data:** `samples_for_simulation.xlsx` stays at root. At submission, mirror to a **public GitHub repo** and load via raw URL inside the notebook (so Colab needs no upload). Working dev uses local relative path.
- **Dependencies:** `pandas numpy scipy matplotlib openpyxl jupyter` (installed in local venv per M0).

---

## Documentation conventions

**Tier 1 — Assignment-required (final deliverable):** Hebrew markdown in `<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">`. LaTeX math in `$$...$$`. Per memory: wrap `##`/`###` headers in their own RTL div (Colab strips CSS injection + h2 inline styles); inside RTL divs use `<br>`-separated raw HTML with manual numbering, **not** markdown lists.

**Tier 2 — Partner-internal (stripped before submission):** styled div with a single regex-findable marker:

```html
<div style="background:#fff3cd; padding:10px; border-left:4px solid orange; margin:10px 0;">
⚠️ <b>INTERNAL — DELETE BEFORE SUBMISSION</b><br>
... rationale / handoff context / design log entry ...
</div>
```

Last cleanup pass: regex-find every `INTERNAL — DELETE BEFORE SUBMISSION` and delete the enclosing cell/section.

---

## Notebook section structure (matches the existing 79-cell notebook)

Each `###` is its own markdown cell unless noted. `[code]` = its own code cell.

```
[Title] Queuechella — Group 20
[code]  Imports — single cell
[code]  CONFIG — every numeric/probabilistic parameter as named constants (+ alternative-mapping docstring)

### 1. מבוא (Introduction)
### 2. תיאור המערכת והנחות (System description + Design Decisions Log as internal div)
### 3. תרשים אירועים ותרשימי טיפול (Event diagram (23 nodes) + 3 handling diagrams, embedded)
### 4. בחירת מדדים (KPI choice — satisfaction / queue wait / revenue)
### 5. התאמת התפלגות (Distribution fitting)   [M2 — DONE]
   5א. FriendsGroup arrival intervals — Gamma (MLE + KS + Chi² + Hebrew narrative)
   5ב. MainStage concert duration — Normal (same flow)
### 6. אלגוריתמי דגימה (Sampling)   [M3]
   6.1 Inverse transform  6.2 Box-Muller  6.3 Composition (Photo)
   6.4 Acceptance-Rejection — DJstage (mandatory)  6.5 A-R — FG Gamma (Exp envelope)
   6.6 ChargingStation charge-time inverse  6.7 RNGStreams
[code]  Sampler class    6.8 DJ A/R validation
### 7. מחלקת לקוח (Customer)   [M4]
### 8. מחלקות אורחים (Group abstract + FriendsGroup / Couple / Single)
### 9. מחלקות מתקנים (Activity classes + Entry + FoodCourt)
### 10. מחלקת תור (QueueServer)
### 11. מחלקת מעקב מדדים (KPITracker)
### 12. מחלקת אירועים (Event base class)   [PARTNERS extend → 23 subclasses]
### 13. מחלקת הסימולציה (Simulation skeleton)   [PARTNERS fill run loop]
### 14. ניתוח חימום (Warmup)   [PARTNERS]
### 15. מדדי מצב קיים (Current-state KPIs)   [PARTNERS]
### 16. בחינת חלופות (Alternative review)   [PARTNERS]
### 17. השוואת חלופות (Welch comparison)   [PARTNERS]
### 18. סיכום והמלצות (Summary & recommendations)   [PARTNERS]
### 19/20. דיווח על שימוש בכלי GenAI (GenAI usage log)
```

---

## Event catalog (canonical — 23 nodes)

Full enumeration, split-vs-parameterize rationale, per-member-vs-per-entity table, Step-4 state/accumulator tables, and Step-5 handler pseudocode live in **`EVENT_DECOMPOSITION.md`** (the deep reference). Summary here so PLAN is self-contained:

**Group A — Bootstrap (init-arrow), 7:** `FriendsGroupArrival`, `CoupleArrival`, `SingleArrival`, `ShowStart@MainStage`, `ShowStart@SideStage`, `EndOfDay1`, `EndOfFestival`.

**Group B — Service-completion, 11:** `EndEntry` (per member), `ShowEnd@MainStage`, `ShowEnd@SideStage`, `EndAtDJstage` (per entity), `EndService@PhotoStation` (per entity), `EndService@ChargingStation` (per member), `EndService@MerchTent` (per member), `EndService@BodyArt` (per member), `EndOrder@FoodCourt`, `EndPrep@FoodCourt`, `EndEating@FoodCourt` (each per member × restaurant).

**Group C — Cross-resource parameterized, 1:** `AbandonQueue` (venue + entity; scheduled at every JoinQueue@{Photo,Charging,Merch,BodyArt} for `now + entity.wait_tolerance`; cancelled when first member starts service).

**Group D — Time-advance special, 3:** `EarlyExitCheck` (MainStage farthest-10), `BreakEnd@BodyArt`, `Day2Resume`.

**Group E — Departure, 1:** `EndOfStay` (per entity; logs each member's final satisfaction → `kpi.final_satisfactions`; removes entity from festival).

Folded into handlers (NOT nodes): JoinQueue, StartService, BreakStart, LunchDecision, OvernightDecision, all satisfaction/experience rolls, restaurant choice, the fill-to-max admission sub-routine, lunch-window open/close.

---

## Milestones

### M0 — Setup & scaffolding   ✅ DONE
- Local venv with deps; `diagrams/` folder; `Queuechella_Simulation.ipynb` 20-section skeleton; `instructions_coverage.md`; "DELETE BEFORE SUBMISSION" deletion-checklist note.
- Remaining: smoke-test (notebook runs top-to-bottom, xlsx loads).

---

### M1 — Pre-work diagrams (Excalidraw MCP)   ◀ ACTIVE
Read first (on-demand): `הרצאות כיתה/הרצאה על תכנות אירועים.pdf` and the event-programming practices (`מעבדות/תרגול 6 - תכנות אירועים.ipynb`, `מעבדות/תרגול 7 - תכנות מונחה אירועים 2.ipynb`).

**Deliverable 1 — Event diagram (23 nodes):** all events from the catalog above, with init-arrows on the 7 bootstrap nodes, zigzag (stochastic) markers on the 3 arrival generators, and scheduling arrows between events (e.g. `ShowStart@X → ShowEnd@X`, `ShowEnd → next ShowStart`). DJ has no show concept (continuous roll-admit). `AbandonQueue` drawn once with the 4-venue annotation.

**Deliverable 2 — Three handling diagrams** (every node a Hebrew action/decision box). Pseudocode already authored in `EVENT_DECOMPOSITION.md` Step 5 — the diagrams are its visual form:
- **(D1) AbandonQueue** — commit-on-first (no in-service branch); per-member `−wait_penalty` clamped at 0; stale-firing guard; next-activity selection (FG phase-aware / Single fixed order / Couple uniform); `EndOfStay` if itinerary exhausted.
- **(D2) ShowStart@MainStage** — fill-to-max head→tail scan (small entities may overtake a too-large head); attendees ordered by entry; schedule `ShowEnd` at `now+duration`; per admitted entity schedule `EarlyExitCheck` at `entry+15`; recursive next `ShowStart` at `showEnd+10min` gated on `shows_scheduling_active` ∧ `< 20:00`. EarlyExitCheck (inline note): if entity still in `attendees[-10:]`, Bernoulli(0.5) → leave + free spots + fill-to-max.
- **(D3) EndOfDay1** — stop Couple/Single arrival streams + show scheduling; per-entity overnight decision (FG: `bought_lodging`; Couple: **avg > 7** → +₪250 lodging; Single: leave); pull leaving show-queue stragglers (no penalty); snapshot day-1 KPIs; schedule day-2 bootstrap (arrivals + ShowStarts + `Day2Resume` per stayer + `EndOfFestival`). Drain semantics: in-progress activities finish naturally; their end handlers read `overnight_decision` and route to `EndOfStay` (leave) or next activity (stay).

**Tooling:** Excalidraw MCP for all 4. Export PNGs to `diagrams/`. Embed into notebook §3 via base64 data URI.

**Verification:** every transition/condition/state-update in the spec for each diagrammed event appears in the diagram; cross-check against the Design Decisions Log (§ below) and the Step-4 I/O matrix in the decomp.

---

### M2 — Distribution fitting (xlsx)   ✅ DONE (verify in this session)
Read first: `מעבדות/תרגול 4- דגימה 1.pdf`, `הרצאות כיתה/L3a - Chi Square.pdf`, `הרצאות כיתה/L3b - KS.pdf`.

Two sheets:
- `FriendsGroup_arrival_intervals` — 100 samples → **Gamma** (`α̂ ≈ 1.239, β̂ ≈ 1.106`). Exp rejected (`std/mean=0.87`, `skew=1.29`, mode away from 0). Passes KS (`D=0.081<0.136`) and Chi² (`k=12, p=0.17`).
- `MainStage_concert_duration` — 100 samples → **Normal** (`μ̂ ≈ 45.90, σ̂ ≈ 8.93`). Passes KS (`D=0.102<0.136`), Chi² (`k=12, p=0.12`).

Per sheet: load + summary + histogram w/ overlaid PDF + strip plot; **MLE derivation** (Gamma: Newton-Raphson on `ln α − ψ(α) = ln x̄ − (1/n)Σln xᵢ`; Normal: closed form); KS (unmodified, `1.358/√n`); Chi² (equal-prob bins, `df=k−1−p`, `p=2`, `k`-sensitivity table in internal div); diagnostics (strip, hist+PDF, empirical-vs-fitted CDF, Q-Q); Hebrew narrative incl. why Exp was rejected for FG.

**M3 implication:** Gamma has no closed-form inverse CDF for non-integer shape → FG arrivals sampled via **A-R with an Exp envelope** (mean-matched, `c ≈ 1.13`, accept ≈ 88%). Same A-R method as DJ.

**This-session verification:** re-run cells 18–31, confirm both fits pass, confirm narrative matches numbers, confirm no leftover Exp-as-primary text for FG.

---

### M3 — Sampling algorithms (`Sampler` class)   ✅ DONE (verify + fix in this session)
Read first: `הרצאות כיתה/נספח להרצאה 5.pdf`, `מעבדות/תרגול 4- דגימה 1.pdf`, `מעבדות/תרגול 5-דגימה 2.pdf`, `מעבדות/פסודו-אקראיות מימוש (תרגול 5).ipynb`.

All samplers in one `Sampler` class (takes an `RNGStreams` instance; each method draws from its dedicated stream). Math derivations in markdown cells preceding the class; one-line English comments in code.

**⚠️ Fix required (R1):** CONFIG cell 4 `couple_arrival_lambda` is `1.0/60.0` (mean 60 min ⇒ ~6 couples/day) — **change to `1.0`** (mean 1 min ⇒ 60/hr ⇒ ~360/day) and fix the comment. Verify `couple_arrival_interval()` then yields mean ≈ 1 min. Update `couple_lodging_threshold` comment from "at least one member" → "average of both members".

**Positive-normal truncation policy:** durations from Normals (`main_show_duration`, `bodyart_glitter_duration`, `food_register_duration`) use a Box-Muller helper that rejection-resamples until `x > 0` (truncation prob ≤ ~0.04%). `charging_battery_percent` is a *bounded percentage*, clamped to `[1, 99]` (keeps `α = 100/(100−b)` finite).

| Quantity | Distribution | Algorithm |
|---|---|---|
| FriendsGroup arrival interval | Gamma (α≈1.24, β≈1.11) | **A-R with Exp envelope** |
| **Couple arrival interval** | **Exp(λ=1 /min ⇒ 60/hr)** | Inverse transform *(R1 fix)* |
| Single arrival interval | Exp(λ=500/420 /min, windowed 09:00–16:00) | Inverse transform |
| FriendsGroup size | DiscreteUniform[3,6] | Inverse transform |
| Ticket scan | U(1.5, 3) | Inverse transform |
| Security check | Exp(mean=2) | Inverse transform |
| MainStage concert duration | Normal (M2) | **Box-Muller** |
| SideStage concert duration | U(20, 30) | Inverse transform |
| **DJstage stay-time** | Piecewise PDF | **Acceptance-Rejection** (mandatory) |
| PhotoStation duration | Piecewise PDF (= example's pool) | **Composition** |
| ChargingStation battery on arrival | N(40, 15) | **Box-Muller** (clamp [1,99]) |
| ChargingStation charge time | α-parameterized PDF | Inverse transform: `t = 40·(1 − U^(1/α))` |
| MerchTent purchase | U(2, 6) | Inverse transform |
| BodyArt glitter / neon / henna | N(15,3) / Exp(12) / U(17,22) | Box-Muller / Inverse / Inverse |
| Food prep Pizza / Burger / Asian | U(4,6) / U(3,4) / U(3,7) | Inverse transform |
| Food register service | N(5, 1.5) | **Box-Muller** |
| Food meal duration | U(15, 35) | Inverse transform |
| All Bernoulli decisions | Bernoulli(p) | Inverse transform |

**Coverage:** Inverse ✅, Box-Muller ✅ (4 normals), Composition ✅ (Photo), Acceptance-Rejection ✅ ×2 (DJ mandatory + FG Gamma).

**DJ A-R derivation:** envelope `U(20,60)`; PDF jumps up at x=40 (left piece ends `1/30`, middle starts `1/15`); since middle decreasing, `sup f = 1/15` at x=40⁺; `c = M·(b−a) = (1/15)·40 = 8/3`; accept `1/c = 3/8 ≈ 0.375`. **Validation (§6.8):** 20,000 instrumented attempts, empirical acceptance vs `3/8`, histogram vs spec PDF. Other samplers: derivation + clean code suffices.

**This-session verification:** read cells 32–35; confirm each algorithm matches its table row; confirm DJ A-R `sup`/`c` math; apply the R1 couple-rate fix; sanity-run a few samplers if deps available.

---

### M4 — OOP class skeleton   (stubs exist; flesh out this/next session)
Read first: `מעבדות/תרגול 2 - חזרה על מונחה עצמים בפייתון מעודכן.ipynb` + skim example cells 13-22 for signature style.

**Customer (concrete):** `id`, `satisfaction` (start 5, clamp [0,10]), `in_queue_at`, `in_service_at`, `service_end_time`, `food_eaten_today`, `lunch_decided`, history; `update_satisfaction(delta, reason)` (clamps), `on_show_end(genre, end_hour)`.

**Group (abstract):** `members`, `size`, `arrival_time`, `current_activity`, `current_position` ∈ {queueing, in_service, in_show, eating, transit, departed}, `queue_join_time`, `abandon_event` (ref, for cancel-on-first), `overnight_decision`, `wait_tolerance_min`, `wait_penalty`; abstract `next_activity(now, activities)` (shortest-queue at transition).
- **FriendsGroup:** size DiscreteUniform[3,6]; tol 15 / penalty 2; `bought_lodging` (Bernoulli 0.7 at arrival, +₪700 bundle); **phased** itinerary — `shows_remaining` (Main, Side, DJ) then `stations_remaining` (Photo, Charging, Merch, BodyArt); shortest-queue within phase.
- **Couple:** size 2; tol 20 / penalty 1.5; open-ended alternation `next_step ∈ {show, station}`; show step → uniform{Main, Side} (no DJ); station step → uniform{Photo, Charging, Merch, BodyArt}; overnight iff **avg satisfaction > 7**; runs until EndOfDay1/EndOfStay.
- **Single:** size 1; tol 20 / penalty 1; fixed itinerary Merch → 2 Main + 2 Side + 1 DJ (shortest-queue within remaining shows); one day only; `EndOfStay` when exhausted.

**Activity (abstract):** `name`, `capacity`, `queue: QueueServer`; `try_admit(entity, now)`, `on_member_finish(member, now)`.
- MainStage (cap 200, mainstream, 10-min break, rolling admission + farthest-10), SideStage (cap 100, indie, 5-min break, batch-at-start), DJstage (cap 70, electronic, continuous roll-admit), PhotoStation (3 servers shared queue, **per-entity** roll), ChargingStation (150 chargers, per-member parallel), MerchTent (7 registers, per-member parallel + per-member item rolls), BodyArt (2 artists, per-member parallel, 15-min break per 10 drawings per artist), Entry (5 clerks, **no abandonment**, scan+security back-to-back per member; `entry_skip_scan` under auto-entry alt), FoodCourt (composite: Pizza|Burger|Asian, 1 cashier+prep each, 13:00–15:00 decision window, **no abandonment**, once-per-day, members may split across restaurants, family-pizza minimize-cost).

**QueueServer:** FIFO of entities + per-entity abandonment timer. On enqueue at an abandonable venue: schedule `AbandonQueue` at `now + tol`. **Cancel the moment the first member starts service** (R6). **Per-member parallel dispatch (R10):** `slots = min(remaining_members, free_servers)`; same-entity members take freed servers before other entities advance; entity leaves at `max(member_end_times)`. Tracks: per-entity wait, queue-length-over-time samples, abandonment counter.

**KPITracker:** `final_satisfactions: list[float]` (per member, at EndOfStay/EndOfFestival); `wait_times[venue]`, `max_wait[venue]`; `queue_length_over_time[venue]`; `revenue_by_source` {ticket, lodging, merch_shirt/hat/flag/band_shirt, photo_print, food_pizza_personal/family, food_burger, food_asian}; `total_revenue`; `abandonments[venue]`; `attendance[venue]`; `day1_snapshot`.

**RNGStreams:** independent `random.Random` per source (arrival_friends/couple/single, show_main, dj_stay, photo_duration, charging_battery/time, merch_purchase/items, bodyart_type/glitter/neon/henna, food_choice/prep_*/register/meal/satisfied, satisfaction_show, lodging, …); `master_seed`; CRN by reseeding only the streams an alternative touches.

**Event (abstract — partners extend):** `time`, `__lt__` for heapq, `execute(sim)`. The **23** subclasses are partner stubs (names = catalog above; no renaming).

**Simulation (skeleton — partners fill):** `clock`, `day`, `fel` (heapq), activities, entities, `rng_streams`, `kpi`, `arrival_streams_active`, `shows_scheduling_active`; `schedule()`, `pop_next_event()`, `run()`.

M4 ends with a smoke cell instantiating every class and printing them (no event logic). **Verification:** every entity/activity/parameter maps to an attribute or method; smoke cell runs; partners can subclass `Event` without renaming.

---

### M5 — Handoff package
1. **§2 Design Decisions Log** (internal div) — the reconciled list below.
2. **CONFIG → alternatives map** — docstring in CONFIG cell + mirror in `instructions_coverage.md`.
3. **Partner roadmap** (internal div between §14–15) — where to plug event handling, KPI hooks, Sampler index, RNG naming, the 23-event names, GenAI-log instruction.
4. **Deletion-pass dry-run** — regex `INTERNAL — DELETE BEFORE SUBMISSION`; confirm stripping leaves a coherent assignment-ready notebook.
5. **Full top-to-bottom run** — no errors.

---

## Design Decisions Log (§2 internal div — reconciled, 16 items)

These are the spec-interpretation judgment calls. All defensible; graders may probe at the oral defense.

1. **Queue abandonment = per-entity timer, per-member penalty, commit-on-first.** Timer from queue-join; **cancelled when the first member starts service** (R6). On fire (no member in service): members still queued are pulled out; every member loses `wait_penalty` (clamped at 0); entity routes to next activity (or `EndOfStay`).
2. **Abandonment applies at exactly 4 venues** (R3): PhotoStation, ChargingStation, MerchTent, BodyArt. NOT shows, Entry, or FoodCourt.
3. **MainStage admission rolling**; SideStage batch-at-start; DJ continuous roll-admit. Fill-to-max scan head→tail, admit any entity whose `size ≤ remaining capacity`.
4. **Farthest-10 early exit:** per-entity `EarlyExitCheck` at `entry+15`; if still in `attendees[-10:]`, **Bernoulli(0.5)** → leave + free spots + fill-to-max. **Spec-mandated** (MainStage: *"…יעזבו את ההופעה 15 דקות לאחר שנכנסו ויפנו למתחם בהסתברות 0.5"*).
5. **Itineraries (R4/R5):** FG **phased** (3 shows → 4 stations, shortest-queue within phase); Single fixed (Merch → 2 Main + 2 Side + 1 DJ); Couple open-ended uniform alternation, no DJ.
6. **Per-member parallel service (R10)** at Entry/Charging/Merch/BodyArt; entity exits at slowest member's `EndService`.
7. **Visitor exit:** Singles + FG leave via `EndOfStay` as soon as itinerary exhausts; Couples leave only at EndOfDay1/EndOfStay/EndOfFestival.
8. **Lodging revenue:** FG pre-buys at arrival (Bernoulli 0.7 → ₪700 bundle). Couple decides at EndOfDay1 (**avg > 7**, R4) → ₪250 (per-couple, not per-member). Singles never stay.
9. **MerchTent per-member item rolls** (shirt 0.8/₪100, hat 0.4/₪50, flag 0.9/₪40, band shirt 0.3/₪200). A 5-person group can buy 5 shirts.
10. **PhotoStation per-entity (R2):** one photo, one roll. Satisfied (0.7) → every member +2, +₪30 once; else (0.3)×(0.5) → every member −0.5.
11. **Entry: no abandonment.** 5 clerks, each does scan `U(1.5,3)` + security `Exp(2)` back-to-back, per member. Auto-entry alt zeros the scan term.
12. **Food court: no abandonment (R3), once per day** (`food_eaten_today`). Decision window 13:00–15:00 (guard inside `EndService` handlers), 70% per guest. **Members may split across restaurants** (R11); same-entity-same-restaurant members order together (one cashier txn, `N(5,1.5)`); entity regroups at `max(EndEating)` across all restaurants.
13. **Family-pizza minimize-cost (R11):** group of N at pizza → `floor(N/3)` family (₪100, feeds 3) + `N mod 3` personal (₪40). Singles always personal. *(Cost-minimizing assumption beyond literal spec — locked, flag at defense.)*
14. **Day transitions (R7):** `EndOfDay1` (stop streams/shows, overnight decisions, snapshot, schedule day-2 bootstrap + `Day2Resume`); `EndOfFestival` (hard end at day-2 20:00); `Day2Resume` re-activates overnight stayers (re-selects next activity in case of stale show-queue). Day-2 arrival rates identical to day 1 for Couple/Single.
15. **Bad-show penalty −1** (spec *"בנקודה"*); good-show `+(G−1)/2 + (T−1)/19`, G∈{main 3, indie 2, electronic 1}, T = integer end-hour. **Satisfaction clamped to [0,10]** everywhere (R14).
16. **Just-in-time sampling (R12):** draw each random quantity at the moment it's needed (service start, not queue-join); inter-arrivals self-scheduled on the current arrival firing. Keeps streams CRN-friendly.

---

## CONFIG → Alternative mapping (CONFIG docstring + handoff doc)

| Alternative | NIS | CONFIG fields to flip |
|---|---|---|
| Better kitchen team | 500K | `food_unsatisfied_prob = 0.1`, `food_choose_prob = 0.85` |
| Expanded security (cap +30%) | 650K | `stage_capacity_main=260, _side=130, _dj=91` |
| Mainstream investment | 300K | `merch_band_shirt_prob = 0.8`, `satisfaction_genre_main = 4` |
| Photo + BodyArt expansion | 150K | `photo_servers = 4`, `bodyart_artists = 3` |
| Advertising | 200K | `arrival_rate_multiplier = 1.2` (all 3 generators) |
| Auto entry | 600K | `entry_skip_scan = True` |
| Visitor gifts | 200K | `initial_satisfaction = 6.5` |

Partners pick combinations ≤ 1,000,000 NIS; overall confidence 0.9 across all comparisons; relative precision 0.1.

---

## Critical files

- `Queuechella_Simulation.ipynb` (root) — master deliverable.
- `EVENT_DECOMPOSITION.md` (root) — **canonical M1 deep reference** (Steps 1–5, state/accumulator tables, handler pseudocode). Kept in sync with this plan.
- `diagrams/event_diagram.png`, `diagrams/handling_abandon_queue.png`, `diagrams/handling_mainstage_showstart.png`, `diagrams/handling_endofday1.png` — Excalidraw exports (M1).
- `instructions_coverage.md` — spec checklist + partner handoff.
- `Course Project 2026B.pdf` (READ-ONLY) — authoritative spec.
- `סילבוס סימולציה.pdf` (READ-ONLY) — syllabus (GenAI rule).
- `example solution.ipynb` (READ-ONLY) — structural + math-derivation reference.
- `samples_for_simulation.xlsx` (READ-ONLY) — M2 data.

---

## Reused references from example

- **Inverse-transform composition for piecewise PDF** (example cell 8) → PhotoStation (PDFs identical), internal-note attribution.
- **`empirical_cdf` / `ks_test` / `d_critical`** helpers (example cell 5) — adapt.
- **`<div dir="rtl" ...>` Hebrew wrappers** — copy styling.
- **Class category structure** (Customer, Group, facilities, QueueServer, Event, Simulation) — mirror, adapted.
- *(Note: the example's Exponential MLE derivation is no longer the primary FG fit — kept only in an internal div as the tested-and-rejected hypothesis.)*

---

## End-to-end verification

1. Notebook opens + runs cleanly (VSCode + Colab), top-to-bottom, no errors.
2. Four diagrams (23-node event + 3 handling) embedded as base64 in §3.
3. Both fits pass KS + Chi² (α=0.05) with hist + Q-Q + CDF overlays.
4. Every sampler callable; **couple rate fixed (R1)**; DJ A-R shows acceptance ≈ 3/8 + histogram check.
5. OOP skeleton instantiable; last M4 cell creates one of every class.
6. CONFIG cell has every parameter named + alternative-mapping docstring.
7. Internal divs regex-findable; deletion dry-run leaves a coherent notebook.
8. `instructions_coverage.md`: items 1-3 + pre-work checked; 4-5 left for partners.
9. GenAI log has ≥1 entry (planning + scaffolding).

---

## Submission info (title cell)

- Group #20 · Ido Malach 318782208 · Yonatan Dolman 208987644 · Etan Cohen 322067448
- Submission: 2026-06-29
