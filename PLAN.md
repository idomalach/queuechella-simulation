# Queuechella Simulation — Master Plan (Group 20)

**Single source of truth.** Everything needed to understand, build, and defend the simulation lives here: the festival model, the event decomposition (23 events + state/accumulator tables + handler pseudocode), every locked design decision, the milestone plan, and the alternatives mapping. Read §1–§4 for orientation, §5–§8 for the model, §9 for the judgment calls, §10 for the build plan.

**Group #20** — Ido Malach (318782208) · Yonatan Dolman (208987644) · Etan Cohen (322067448). **Submission: 2026-06-29.**

Ownership: the **user (Ido)** owns items 1-3 of "סדר העבודה" (distribution fitting → sampling → classes/methods) + all pre-work diagrams. **Partners (Yonatan, Etan)** own items 4-5 (event-driven run loop + output analysis + alternatives comparison + report polish).

---

## 1. Context

Event-driven simulation of the two-day **Queuechella** festival (09:00–20:00 each day) for the Simulation course capstone (47% of grade: notebook + presentation + defense). The festival hires us to evaluate daily service quality and recommend budget-constrained improvements.

KPIs (locked, so the OOP design wires them up): **average visitor satisfaction at exit**, **average + max queue wait time across stations**, **festival revenue**.

Two cross-cutting requirements:
1. **Dual-tier documentation** — assignment-required Hebrew narrative stays in the notebook; partner-only handoff notes live in regex-strippable internal divs.
2. **GenAI usage declared** (syllabus) — maintain an in-notebook log (final §) throughout; it becomes the official declaration.

Narrative language **Hebrew** (mirrors the lecturer's example); code comments **English only** (assignment requirement).

---

## 2. Working environment & Colab bridge

- **Master notebook:** `Queuechella_Simulation.ipynb` at project root (79 cells; M0 skeleton built, M2/M3 filled, M4 stubs). Developed locally in VSCode, delivered in Colab.
- **Diagrams:** Excalidraw MCP tools (`mcp__claude_ai_Excalidraw__*`) — the event diagram + 3 handling diagrams. Build → `export_to_excalidraw` share URL → download PNGs manually into `diagrams/` → base64-embed into notebook §3. (The MCP renders to the UI and shares a URL; it does not write PNG files directly.) **Diagram build workspace:** `diagrams/build/` — `EVENT_NODE_EDGE_SPEC.md` (authoritative v2.0 node+edge spec & decision log; the full per-handler edge contract + routing matrix), `README.md` (build pipeline + Excalidraw-MCP gotchas), and the `gen_excali_event.py → event_layout_mock.py → to_native_min.py → export_to_excalidraw` pipeline.
- **xlsx data:** `samples_for_simulation.xlsx` at root. At submission, mirror to a **public GitHub raw URL** for Colab (no upload needed); dev uses the local relative path.
- **Dependencies:** `pandas numpy scipy matplotlib openpyxl jupyter` (in a venv under `~/venvs/`, never inside this iCloud-synced folder). **NumPy 2.x** — `np.trapz` was removed; use `np.trapezoid` (the notebook + Colab run NumPy 2.x).

---

## 3. Documentation conventions

**Tier 1 — assignment-required (final deliverable):** Hebrew markdown in `<div dir="rtl" style="text-align: right; font-size: 16px; line-height: 1.8;">`; LaTeX in `$$...$$`. Wrap `##`/`###` headers in their own RTL div (Colab strips CSS injection + inline styles on `<h2>`). Inside RTL divs use `<br>`-separated raw HTML with manual numbering, **not** markdown lists.

**Tier 2 — partner-internal (stripped before submission):** a yellow div with a single regex marker:

```html
<div style="background:#fff3cd; padding:10px; border-left:4px solid orange; margin:10px 0;">
⚠️ <b>INTERNAL — DELETE BEFORE SUBMISSION</b><br> ... handoff / rationale / log ...
</div>
```

Final cleanup: regex-find every `INTERNAL — DELETE BEFORE SUBMISSION` and delete the enclosing cell.

---

## 4. Notebook section structure

```
[Title] Queuechella — Group 20
[code]  Imports  ·  [code] CONFIG (every numeric/probabilistic parameter + alternative-mapping docstring)
### 1. מבוא · 2. תיאור המערכת והנחות (+ Design Decisions Log internal div)
### 3. תרשים אירועים ותרשימי טיפול (23-node event diagram + 3 handling diagrams)
### 4. בחירת מדדים (KPIs) · 5. התאמת התפלגות [M2 done] · 6. אלגוריתמי דגימה [M3]
[code]  RNGStreams (hoisted — before Sampler)  ·  [code] Sampler  ·  6.8 DJ A/R validation
### 7. מחלקת לקוח · 8. מחלקות אורחים · 9. מחלקות מתקנים · 10. תור (QueueServer) · 11. מעקב מדדים (KPITracker)  [M4]
### 12. RNGStreams — **orphan header** (class hoisted to §6; delete in cleanup — audit C1-n4)
### 13. מחלקת אירועים (Event base) [PARTNERS extend → 23 subclasses]
### 14. מחלקת הסימולציה (skeleton) [PARTNERS fill run loop]
### 15. ניתוח חימום → **reframe to ניתוח מספר הרצות** (replication-count, terminating — C2-M1) · 16. מדדי מצב קיים · 17. בחינת חלופות · 18. השוואת חלופות (Welch) → **paired t-test** (C2-M2) · 19. סיכום והמלצות  [PARTNERS]
### 20. דיווח GenAI
```

---

## 5. The festival model

### 5.1 Setting
- Two days, 09:00–20:00 each. Every **guest** (individual) carries a satisfaction score: start 5, max 10, min 0, **clamped to [0, 10]** wherever mutated.
- Alternatives budget ₪1,000,000; compare at 90% overall confidence (α=0.1), relative precision γ=0.1.
- **Terminating simulation (audit C2-M1, DECIDED):** the festival has a hard start/stop (2 days, opens empty) ⇒ analyze as a *terminating* system, **not** steady-state. Output analysis = **N independent replications** of the full 2-day run, **no warmup deletion**; N chosen so the CI meets relative precision γ=0.1, with the α=0.1 error budget **Bonferroni-split** across all metric×comparison tests. Alternatives are compared to baseline via a **paired t-test** under CRN (#15). Lecture 9's bank (08:00–16:00) is the matching shape; the example notebook's 15-day-warmup hotel does **not** transfer.

### 5.2 Entities (3 types)

| Entity | Arrival | Window | Days | Size |
|---|---|---|---|---|
| **FriendsGroup** | from xlsx → **Gamma**(α≈1.24, β≈1.11), sampled via A-R | 09:00–13:00 | **Day 1 only**; stays overnight w.p. 0.7 | DiscreteUniform[3,6] |
| **Couple** | **Exp, 60/hour ⇒ λ=1/min, mean inter-arrival 1 min** | 10:00–16:00 | Day 1 or 2; stays iff **avg satisfaction > 7** at end of day 1 | 2 |
| **Single** | Exp, 500/day (windowed over 09:00–16:00 ⇒ λ≈500/420 per min) | 09:00–16:00 | one day only (1 or 2) | 1 |

> **Couple rate is the one easy-to-get-wrong number.** Spec *"תוחלת של 60 בשעה"* parallels Single's *"תוחלת של 500 ביום"* (= count per period) ⇒ **60 couples/hour**, mean inter-arrival **1 minute** (~360/day). Not 1/hour. CONFIG sets `couple_arrival_lambda = 1.0` — **fixed in M3** (was `1.0/60.0`, which gave ~6 couples/day; verified mean inter-arrival 1.002 min).

**Per-entity behavior:**
- **FriendsGroup** — strict two-phase itinerary: **Phase 1** = one show of each genre (Main, Side, DJ); **Phase 2** = all 4 stations (Photo, Charging, Merch, BodyArt). Shortest-queue pick *within* the current phase. (Spec: *"לאחר שהות מלאה בכל הופעה יעברו בכלל העמדות"*.) **Overnight (E4):** an FG that bought lodging (Bernoulli 0.7 at arrival) and finishes its itinerary on day 1 does **not** exit — it stays overnight and **restarts a fresh itinerary on day 2** (`Day2Resume` re-inits and resumes it at a show), since the spec says staying groups *"וימשיכו ליום הבא"*. An FG **without** lodging exits via `EndOfStay` when its itinerary exhausts (decision #7).
- **Couple** — open-ended alternation show→station→show→…; show step = uniform{Main, Side} (no DJ — couples dislike electronic); station step = uniform{Photo, Charging, Merch, BodyArt}. Runs until EndOfDay1/EndOfStay.
- **Single** — fixed itinerary: Merch first, then 2 Main + 2 Side + 1 DJ shows (shortest-queue among remaining required shows). Leaves when itinerary exhausts.
- **Group movement:** members move as one unit — nobody proceeds to the next activity until all finish the current one. **Food court is the only exception** (members split across restaurants; see §5.5).

### 5.3 Resources (11 venues)

| Resource | Capacity | Service mode | Notes |
|---|---|---|---|
| Entry | 5 booths | **per-member, parallel** | scan `U(1.5,3)` + security `Exp(mean 2)` back-to-back, one `EndEntry` per member. **No abandonment.** Auto-entry alt zeros the scan term. |
| MainStage | 200 | per-entity | mainstream; show duration **Normal**(M2) via Box-Muller; 10-min break; spatial order = entry order; **farthest-10 early exit (non-FG; FG exempt — A1-2)**; **admission = batch at ShowStart + mid-show walk-in if running under-cap (D3) + vacated-spot rolling admit** — each admitted **non-FG** entity (any path) gets its own `EarlyExitCheck`+15. |
| SideStage | 100 | per-entity | indie; show `U(20,30)`; 5-min break; **batch at ShowStart + mid-show walk-in if running under-cap (D3)** — no farthest-10. |
| DJstage | 70 | per-entity | electronic; continuous (no shows); stay-time piecewise PDF, **A-R sampling**; roll-admit as capacity frees. |
| PhotoStation | 3, shared queue | **per-entity** | one photo per visit; one shared satisfaction roll. |
| ChargingStation | 150 | per-member, parallel | battery on arrival `N(40,15)` clamped **[0,99]** (only `b<100` is mandatory — avoids α=100/0; `b=0` is valid → α=1 → charge time Uniform(0,40)); charge time `f(t)` with α=100/(100−battery). |
| MerchTent | 7 | per-member, parallel | service `U(2,6)`; per-member item rolls. |
| BodyArt | 2 artists | per-member, parallel | glitter/neon/henna; artist breaks 15 min after every 10 drawings. |
| FoodCourt (Pizza/Burger/Asian) | 1 register each | per-member (per food-unit) | 13:00–15:00 decision window, **one stop per entity/day**, **no abandonment**, parallel kitchen, pizza consolidation — see §5.5. |

**Abandonment applies at exactly 4 venues:** PhotoStation, ChargingStation, MerchTent, BodyArt. **Not** shows, Entry, or FoodCourt (professor-confirmed). Tolerances/penalties: FriendsGroup 15 min/−2 · Couple 20 min/−1.5 · Single 20 min/−1.

### 5.4 Per-entity vs per-member service (the subtle part)

Movement and queue position are **per-entity**; some service venues run **per-member in parallel**.

| Venue | Per-entity (one shared outcome) | Per-member (independent per guest) |
|---|---|---|
| Shows (Main/Side/DJ) | attendance, fill-to-max, show duration, occupancy | good/bad experience roll |
| PhotoStation | whole transaction — one photo, one satisfaction roll, one ₪30 | — |
| ChargingStation | queue position | battery, charge time, charger occupancy |
| MerchTent | queue position | service `U(2,6)`, 4 item rolls, cashier occupancy |
| BodyArt | queue position | art-type, duration, satisfaction roll, artist occupancy |
| FoodCourt | lunch-window guard, entity regroup | decide-to-eat (70%), food choice, register, prep, eating, meal-satisfaction (pizza consolidated — §5.5) |

**Parallel per-member service rule (Entry, Charging, Merch, BodyArt):**
- When an entity reaches the front, it occupies `slots = min(remaining_members, free_servers)`. Each member's `EndService` is drawn and scheduled independently when that member's service starts (just-in-time).
- **A finished member frees its server immediately** — the server is handed to the next waiting member *of the same entity* if any, else to the next entity in the venue queue. A finished member is parked "done, awaiting regroup" and holds **no** server. *(Finished members never idle-hold a server.)*
- Other entities in the queue cannot advance until all of this entity's members are in-service or done.
- **The entity's next-activity selection happens only when the LAST member finishes** here (no member of this entity still in service or queue). Earlier `EndService` firings are bookkeeping only (free server + record stats + mark member done). Sampling for the next activity then happens just-in-time when service starts there.

### 5.5 Food court — detailed model

**One food stop per entity per day.** An entity becomes eligible the first time it **finishes a real itinerary activity during 13:00–15:00** with its entity-level gate `food_done_today` still False. **(D4: eating is never the first festival activity — `EndEntry` does not count; the food gate is checked at activity-completion handlers (shows / DJ / stations / abandon), not at Entry.)** At that moment the gate is **set to True immediately** (so it cannot re-fire, even between the food-court sub-steps), and the entity makes its single food stop: **per member independently**, roll **hungry (70%)**; if hungry, pick a food type — **burger 3/8, pizza 1/4, asian 3/8**. After the stop the entity never returns to the food court that day — **even members who declined get no second chance**, and "just finished eating" can't loop back into another food visit. If no member is hungry, the stop still counts as made (the gate stays set). The gate **resets at day 2** for overnight stayers (via `Day2Resume`). *(Audit A1-3: the spec keys eligibility on guests who **have** activity in 13:00–15:00; we key it on the **activity-completion boundary** — the only event-driven place to insert the decision. Practically equivalent: any non-degenerate itinerary completes ≥1 activity inside the 2-h window.)*

Eating is unconstrained (picnic tables / grass / walking) — only the **single register per restaurant** is a queue. Prep is a **parallel-kitchen delay** (the spec gives no cook capacity, only the register). Register service `N(5,1.5)` covers **order + payment** (no separate payment event). Each non-pizza order draws its own register / prep / eating samples.

| Food type | Prep | Price | Granularity |
|---|---|---|---|
| Burger | `U(3,4)` | ₪100 (meal: burger + chips + drink) | **per member** — one register/prep/eat sample set each |
| Asian | `U(3,7)` | ₪65 (stir-fry box + drink) | **per member** — one set each |
| Pizza | `U(4,6)` | individual ₪40 / family ₪100 (feeds 3) | **consolidated per entity** — see below |

**Pizza consolidation rule (every entity — couples and groups alike):** an **individual pizza is only ever ordered by a single person.** If `P` = number of the entity's members who chose pizza:
- **P = 1** → 1 individual pizza (₪40); that member queues; **1 sample set** (register/prep/eat).
- **P ≥ 2** → `n = ceil(P/3)` **family pizzas** (₪100 each, total ₪100·n); **`n` members queue** (one representative per family pizza); each family pizza draws **one sample set** (register/prep/eat) covering the up-to-3 people it feeds. The remaining `P − n` pizza-members don't queue/cook separately — they share a family pizza's eating period.

Worked: P=1 → 1 individual, 1 in line, 1 set · P=2 or 3 → 1 family, 1 in line, 1 set · P=4/5/6 → 2 family, 2 in line, 2 sets.

**Meal-satisfaction roll: per guest** — every guest who ate (including family-pizza coverees) rolls w.p. 0.4 → −0.6. *(Per-guest reading, since satisfaction is per-guest; flag at defense.)*

**Regroup:** the entity proceeds to its next activity at `max(EndEating)` across all its **food-units** — each non-pizza member's order plus each pizza (individual or family). If no member is hungry, the entity skips food.

**Event mapping:** `EndOrder` / `EndPrep` / `EndEating` fire **per food-unit** (a food-unit = one member's burger/asian order, OR one pizza [individual or family]), each parameterized by restaurant.

### 5.6 Satisfaction-update rules

| Trigger | Δ | Applied to |
|---|---|---|
| Show, good experience (w.p. 0.5) | `+(G−1)/2 + (T−1)/19`, G∈{main 3, indie 2, electronic 1}, T = integer **hour-of-day** of show end (9–20, **not** elapsed) | per-member |
| Show, bad experience (w.p. 0.5) | −1 (spec *"בנקודה"*) | per-member |
| PhotoStation satisfied (w.p. 0.7) | +2 (and buys ₪30 print) | per-entity (one roll → every member) |
| PhotoStation unsatisfied (0.3) × bad (0.5) | −0.5 | per-entity (every member) |
| BodyArt glitter / neon / henna satisfied (0.7 / 0.6 / 0.8) | +0.8 / +1.2 / +0.7 | per-member |
| Food, unsatisfied (w.p. 0.4) | −0.6 | per-member (each guest who ate) |
| Queue abandonment | −2 / −1.5 / −1 (FG / Couple / Single) | per-member (every member of the abandoning entity) |

All deltas clamp the result to [0, 10].

### 5.7 Revenue events

| Source | Amount |
|---|---|
| Entry ticket — **per person** (₪500 × entity.size) | ₪500 / person |
| Overnight — **per person**: FG bundle ticket+lodging (pre-bought) ₪700 × size · Couple lodging add-on ₪250 × size (= ₪500/couple) | ₪700 · ₪250 / person |
| Merch: t-shirt 0.8 / hat 0.4 / flag 0.9 / band-shirt 0.3 (per member) | ₪100 / ₪50 / ₪40 / ₪200 |
| Photo print (w.p. 0.7, **per entity** — NOT per-person) | ₪30 |
| Food: individual pizza / family pizza / burger / asian | ₪40 / ₪100 (×`ceil(P/3)`) / ₪100 (per burger member) / ₪65 (per asian member) |

---

## 6. Event catalog (23 nodes)

Built by passing each candidate event through two tests — **time-advance** (does it advance the clock, or just gate a decision happening now?) and **split-vs-parameterize** (split on independent scheduling sources or different downstream graphs; parameterize when only numbers differ).

### Group A — Bootstrap (zigzag init-arrow), 7
`FriendsGroupArrival`, `CoupleArrival`, `SingleArrival` (zigzag init + solid self-loop scheduling the next arrival) · `ShowStart@MainStage`, `ShowStart@SideStage` (zigzag init at 09:00; each `ShowEnd` schedules the next after the break) · `EndOfDay1` (zigzag init, clock-fixed 20:00 day 1) · `EndOfFestival` (zigzag init, clock-fixed 20:00 day 2). **All 7 get a zigzag arrow because their first instance must be seeded into the FEL at t=0 for the sim to run** — see the convention block in §10/M1.

> Multi-day streams (A2-5): an arrival stream **stops self-scheduling at its window-end** — it does **not** cross the day boundary. **`EndOfDay1` is the SOLE day-2 re-seeder** (D3 step 4), so day-2 arrivals/shows are seeded exactly once (no double-seed). Shows: `ShowEnd` schedules the next `ShowStart` only while `shows_scheduling_active` ∧ start<20:00; the next day's first shows come from `EndOfDay1`, not carried across the boundary.

### Group B — Service-completion, 11

| # | Event | Fires | Notes |
|---|---|---|---|
| 8 | `EndEntry` | per member | free booth; admit next same-entity member, else next entity; last member ⇒ entity → first activity. |
| 9 | `ShowEnd@MainStage` | per show | per-member experience roll; attendees → next activity (or `EndOfStay` if leaving); schedule next `ShowStart` if active & <20:00. |
| 10 | `ShowEnd@SideStage` | per show | same as Main, no farthest-10. |
| 11 | `EndAtDJstage` | per entity | free `entity.size` spots; per-member roll; entity → next; roll-admit DJ queue. |
| 12 | `EndService@PhotoStation` | per entity | one shared satisfaction roll → all members; ₪30 if satisfied; entity → next; roll-admit. |
| 13 | `EndService@ChargingStation` | per member | parallel-service dispatch (§5.4). |
| 14 | `EndService@MerchTent` | per member | 4 item rolls; parallel-service dispatch. |
| 15 | `EndService@BodyArt` | per member | per-member satisfaction roll; `drawings_since_break++`; if `%10==0` schedule `BreakEnd`; parallel-service dispatch. |
| 16 | `EndOrder@FoodCourt` | per food-unit | free register; schedule `EndPrep` at `now + prep`. |
| 17 | `EndPrep@FoodCourt` | per food-unit | schedule `EndEating` at `now + U(15,35)`. |
| 18 | `EndEating@FoodCourt` | per food-unit | per-guest meal-satisfaction roll (covers family-pizza sharers); if all entity food-units done, regroup → next activity. |

### Group C — Cross-resource parameterized, 1
**19. `AbandonQueue`** (venue + entity) — scheduled at every JoinQueue@{Photo, Charging, Merch, BodyArt} for `now + entity.wait_tolerance`; **cancelled the moment the first member starts service** (commit-on-first). On fire (no member in service): pull entity from queue, apply `−wait_penalty` to every member (clamp 0), route to next activity (or `EndOfStay`).

### Group D — Time-advance special, 3

| # | Event | Scheduled by | Does |
|---|---|---|---|
| 20 | `EarlyExitCheck` | per **non-FG** entity entering MainStage, at `entry+15` | **skip if entity is a FriendsGroup** (A1-2: FG "full stay" exemption); else if entity still in `attendees[-10:]`, **Bernoulli(0.5)** → leave, free `entity.size` spots, roll-admit. **Spec-mandated 0.5** (*"…יעזבו את ההופעה 15 דקות לאחר שנכנסו למתחם בהסתברות 0.5"*). |
| 21 | `BreakEnd@BodyArt` | `EndService@BodyArt` when count %10==0 | artist available; dispatch next. |
| 22 | `Day2Resume` | `EndOfDay1` per overnight stayer, at 09:00 day 2 | reset `food_done_today` (new food stop allowed); re-evaluate next activity (in case stuck in a stale show queue). |

### Group E — Departure, 1
**23. `EndOfStay`** (per entity) — scheduled (usually at `now`) when a visit ends: itinerary exhausted (FG-without-lodging / Single), `overnight_decision == "leave"` at the moment the current activity completes, or `EndOfFestival` for day-2 stragglers. Logs every member's final satisfaction into `kpi.final_satisfactions`, marks the entity departed, frees any held resources. **D5 (diagram):** drawn as a **receive-only convergence node** — every `X→stations` edge folds in `X→EndOfStay` (any router reaching the cluster can also end a visit), so arrows point only *into* it; the one explicit incoming edge is `EndOfFestival→EndOfStay`. In code it's an ordinary terminal event (`select_next_activity` returns `None` → schedule `EndOfStay`). **Not** reachable from `EndEntry` (every entity has ≥1 activity) or `Day2Resume` (stayers restart at a show, E4).

### What is NOT a separate node (folded into handlers)
`JoinQueue`, `StartService`, `BreakStart`, `LunchDecision`, `OvernightDecision`, every satisfaction/experience roll, food-type choice, **fill-to-max admission** (a sub-routine called from each `ShowEnd`/`EndService`/`EarlyExitCheck`/`BreakEnd`), lunch-window open/close. None advance time independently.

### Termination patterns used
A — fixed-clock **init** events (`EndOfDay1`, `EndOfFestival`: zigzag-seeded at t=0) that **drain rather than hard-stop (C2)** — in-flight events finish (the clock runs past 20:00), their end-handlers route entities to `EndOfStay`, and the day-boundary handler only sweeps idle/stuck entities (those with no pending completion). The run loop keeps popping the FEL until drained. B — stop source, drain (arrival streams stop self-scheduling at window-end; lunch window is a guard). C — service-completion (`ShowEnd`→next `ShowStart`; `EndService@BodyArt`→`BreakEnd`; MainStage admission→`EarlyExitCheck`).

### Directed-edge graph (scheduling structure)
The full per-handler edge contract + per-entity routing matrix are the authoritative reference in **`diagrams/build/EVENT_NODE_EDGE_SPEC.md`** (§4 by-source-event; §6 routing matrix). Structure summary:

- **Edge semantics (P2):** `A → B` = "when A fires it *may* schedule B" (condition in the handler) — **never** "an entity flows from A to B". Routing into a *show* creates no event (entity joins a show queue; admission waits for `ShowStart` or a walk-in) ⇒ no edge, *except* a MainStage walk-in, which schedules `EarlyExitCheck` ⇒ edge.
- **Init (zigzag), 7:** the 3 arrivals, the 2 `ShowStart`s, `EndOfDay1`, `EndOfFestival` — seeded into the FEL at t=0.
- **Self-loops, 10(+1):** 3 arrivals, `EndEntry`, `EndAtDJstage`, the 4 `EndService@station`s, `EndOrder`, and (E2) `EarlyExitCheck` (a vacated-spot roll-admit pulls the queue head into the show and schedules *its* +15). None on `EndPrep`/`EndEating`/`ShowEnd`.
- **Show cycle (E1):** `ShowStart ↔ ShowEnd` is mutual — **`ShowEnd` schedules the next `ShowStart`** at `now+break` (10 main / 5 side); `ShowStart` does **not** self-schedule.
- **Routing core (diagram device, R1/R2):** the 4 stations + `EndOfStay` are drawn as a `STATIONS` super-node box (4 mutual `station↔box` edges abbreviate the all-to-all K₄). **There is no cluster object in code** — `select_next_activity(E)` returns a *specific* venue.
- **Node-specific edges (R3 — bind to the node, not the box):** `EndEntry → EndService@Merch` (Single's first stop; **E3 fix** — v1 wrongly had `EndEntry→BodyArt`); `EndService@Merch → EndAtDJstage` (Single Merch→DJ); `EndOfFestival → EndOfStay`.
- **Day boundary + must-not edges:** `EndOfDay1 → {CoupleArrival, SingleArrival, ShowStart@Main, ShowStart@Side, Day2Resume}`; `EndOfDay1 ✗→ EndOfFestival` (init-seeded, C) and `✗→ FriendsGroupArrival` (day-1 only); no scheduling edge into `ShowStart` except init / the mutual cycle / the day-2 re-seed; `EndEntry ✗→ EndOrder` (D4) and `✗→ stations` (Merch only); `Day2Resume ✗→ stations` (resumes at a show, E4); no edge out of `EndOfStay`.
- **DJ (E5):** one node `EndAtDJstage` (= `EndDJ` in the build script).

---

## 7. State variables vs accumulators

> **This is a *seed* for the M4 class design, not the finished state model.** The split (state = what determines what happens next; accumulator = what's carried only for the final report) tells us which fields go on which class. Building the classes will surface more — e.g. `member.done_awaiting_regroup`, `member.wants_food`, `member.food_choice`, `entity.pizza_count`, per-restaurant single-register state, explicit server-slot objects (`.busy`, `.member`). Expand this section during M4.

### 7.1 State

**System:** `clock` · `day` (1/2) · `fel` (min-heap, ordered by **(time, fixed event-class priority, insertion seq)** for a deterministic tie-break — needed for CRN reproducibility and boundary semantics; the specific 20:00 `EndOfDay1`-vs-`ShowEnd` ordering is pinned by the day-boundary fix — audit A2-8/A2-1) · `arrival_streams_active[stream]` · `shows_scheduling_active[stage]`.

**Per entity:** `id` · `type` · `size` · `members` · `arrival_time` · `bought_lodging` (FG) · `itinerary_remaining` (FG: `shows_remaining`+`stations_remaining` by phase; Single: ordered list; Couple: `next_step`) · `itinerary_phase` (FG) · `current_activity` · `current_position` ∈ {queueing, in_service, in_show, eating, transit, departed} · `queue_join_time` · `abandon_event` (ref, for commit-on-first cancel) · `overnight_decision` · **`food_done_today`** (entity-level once-per-day food gate; reset at day 2).

**Per member (Customer):** `id` · `satisfaction` (gates couple overnight; feeds final-satisfaction KPI) · `in_service_at` · `service_end_time` · `done_awaiting_regroup` · `wants_food` · `food_choice` (set during the entity's single food stop).

**Per resource:** `queue` (FIFO of entities; length drives shortest-queue) · `servers` (slots: `.busy`, `.member`) · `in_service_entities`.

**Per stage:** `attendees` (entry-ordered; MainStage uses `attendees[-10:]`) · `spots_used` · `current_show.{genre, end_time}` · `next_show_event`.

**Per BodyArt artist:** `drawings_since_break` · `on_break` · `break_end_event`.

**Per restaurant (×3):** `cashier_busy` · `register_queue` (food-units) · `prep_in_flight` · `eating_in_flight`.

### 7.2 Accumulators (KPI)

`final_satisfactions: list[float]` (per member, at `EndOfStay`/`EndOfFestival`) · `wait_times[venue]`, `max_wait[venue]` (one sample per StartService + per AbandonQueue ⇒ **per-member** at the parallel-service venues Entry/Charging/Merch/BodyArt, **per-food-unit** at FoodCourt, and **per-entity** at Main/Side/DJ/Photo — M1 session 1; D2's show-wait is per-entity, as written in §8) · `queue_length_over_time[venue]` · `revenue_by_source` {ticket, lodging, merch_*, photo_print, food_*} · `total_revenue` · `abandonments[venue]` · `attendance[venue]` · `day1_snapshot`.

### 7.3 Event → I/O matrix (R = reads state, W = writes state, A = accumulates)

| Event | Reads | Writes | Accumulates |
|---|---|---|---|
| `*Arrival` | clock, stream active | create entity, entry-queue join | revenue: non-lodging = ₪500×size (ticket); **lodging FG** (w.p. 0.7) = ₪700×size bundle **replacing** the ticket (NOT additive — see #8; audit A2-3) |
| `ShowStart@*` | queue, capacity, clock | attendees, current_show, queue-pop | attendance, queue-length |
| `EndEntry` | booth busy, entity entry-queue | free booth, route last member → first activity | wait_times[Entry] |
| `ShowEnd@*` | attendees, genre, clock | per-member roll; attendees → next/EndOfStay; next ShowStart | attendance |
| `EndAtDJstage` | spots_used, itinerary | spots−=size; per-member roll; → next; roll-admit | queue-length |
| `EndService@PhotoStation` | booth busy, queue | shared roll → all members; → next; roll-admit | revenue[photo], wait_times |
| `EndService@Charging/Merch/BodyArt` | server busy (+ artist count) | parallel dispatch (§5.4); per-venue rolls; last member → next | merch revenue / wait_times |
| `EndOrder/Prep/Eating@FoodCourt` | register/queue, entity food-units | free register / schedule prep / schedule eating / regroup | revenue[food_*] (incl. pizza consolidation) |
| `AbandonQueue` | entity in queue? | remove; per-member −penalty; → next | abandonments[venue] |
| `EarlyExitCheck` | attendees[-10:] | if in last-10: Bernoulli(0.5) → leave + free spots + roll-admit | — |
| `BreakEnd@BodyArt` | artist.on_break | on_break=False; dispatch | — |
| `EndOfDay1` | all live entities, clock | stop streams/shows; per-entity overnight decision; pull leaving show-queue stragglers; **re-enable day-2 stream/show flags (A2-2)**; schedule day-2 bootstrap | revenue[lodging], day1_snapshot |
| `EndOfFestival` | live entities, FEL | **drain-sweep (C2):** in-flight finishes; route only entities with no pending completion → EndOfStay; keep draining FEL past 20:00 | finalize final_satisfactions |
| `Day2Resume` | entity ref | re-select next activity | — |
| `EndOfStay` | members' satisfaction | mark departed; free resources | final_satisfactions |

---

## 8. Handler pseudocode — the 3 diagrammed events (M1)

These are the M1 handling-diagram deliverables (the other 20 handlers are partners' Step-5 work, same template). Conventions: `now` = clock; `E` = entity; `V` = venue; `kpi.*` = accumulator.

### D1 — AbandonQueue(E, V)   [V ∈ {Photo, Charging, Merch, BodyArt}]
```
TRIGGER: scheduled at JoinQueue@V for now + E.wait_tolerance; CANCELLED when E's first member starts service.
         ⇒ on fire, no member of E is in service at V.
1. if E ∉ V.queue: return                              # stale firing — only cause: lazy-cancel (a member already started service ⇒ E was popped from V.queue). No "abandoned twice" path. (M1 session 2, FLAG 3)
2. V.queue.remove(E); E.current_position ← "transit"; E.queue_join_time ← None
3. for m in E.members: m.satisfaction ← clamp(m.satisfaction − E.wait_penalty, 0, 10)
4. route via advance_itinerary_or_exit(E)              # 2-step drain-aware helper (B2): Step 1 routes to the next performable activity (festival-open ∧ itinerary-remaining → append, re-arm AbandonQueue if it's a station, try_admit); else Step 2 PARK (staying) / EndOfStay (leaving). Shared by every completion handler.
ACCUMULATE: abandonments[V] += 1; queue_length_over_time[V] (and [next] if routed) sampled.
```
*No "members in service" branch — commit-on-first guarantees none. Penalty clamps at 0.*

**`advance_itinerary_or_exit(E)` — the single drain-aware routing helper (2-step, B2 — supersedes the earlier None-only form + separate past-close guard; M1 session 2 FLAG 1/2).** Every completion handler calls this to route an entity onward.
- **Step 1 — next *performable* activity?** = festival open (`clock < close(day)`) **∧** `select_next_activity(E)` returns a venue (itinerary not exhausted). **YES** → route: `next.queue.append(E)`; if `next ∈ {Photo,Charging,Merch,BodyArt}` re-arm `AbandonQueue(E,next)` at `now + wait_tolerance`; `try_admit(next, now)`. **NO** (festival closed in drain, OR itinerary exhausted) → Step 2.
- **Step 2 — stay overnight, or leave?** **Stays** → **PARK** (schedule nothing; idle in `entities_live`, holds no resource; `EndOfDay1` sweeps it into `stayers` / `Day2Resume` restarts it day 2). Staying = FG-with-lodging on day 1, **or** any entity with `overnight_decision == "stay"` (set at EndOfDay1). **Leaves** → schedule `EndOfStay(E)`. Leaving = FG-without-lodging / Single / Couple (avg ≤ 7), **or any entity on the final day** (no overnight decision exists).

**Systemic (like FLAG 1):** every completion handler — `ShowEnd@*`, `EndService@*`, `EndAtDJstage`, `EndEating`, `AbandonQueue`/D1 — routes through this **one** helper; none raw-schedules `EndOfStay`, routes past close, or re-implements park-vs-exit. **Scope (FLAG 2):** the Step-1=NO branch reached *mid-day* (festival open, itinerary exhausted) is **FG-only** at AbandonQueue (a Single abandons only at Merch with shows ahead; a Couple never exhausts mid-day); in **drain** (festival closed) **any** entity can reach Step-1=NO. **No edge-spec change:** "park" schedules nothing (no edge); "route" reuses existing edges; `EndOfStay` stays folded via D5.

### D2 — ShowStart@MainStage
```
TRIGGER: init-arrow 09:00 day 1; recursively by previous ShowEnd@MainStage at now+10min, IF shows_scheduling_active ∧ start<20:00.
1. duration ← sample_show_duration_main()  (Normal, Box-Muller); genre ← "mainstream"
2. # fill-to-max, head→tail (small entities may overtake a too-large head):
   i ← 0
   while i < len(queue) and spots_used < 200:
       E ← queue[i]; rem ← 200 − spots_used
       if E.size ≤ rem:
           queue.pop(i); attendees.append(E); spots_used += E.size
           E.current_activity ← MainStage; E.current_position ← "in_show"
           wait ← now − E.queue_join_time; kpi.wait_times[Main].append(wait); kpi.max_wait[Main] ← max(...)
       else: i += 1
3. current_show ← {genre, start: now, end: now+duration}
4. schedule ShowEnd@MainStage at now + duration
5. for E in admitted if E.type ≠ FriendsGroup: schedule EarlyExitCheck(E) at now + 15   # A1-2: FG exempt
6. (next ShowStart is NOT scheduled here — E1: it is owned by ShowEnd@MainStage at showEnd + 10-min break. ShowStart never self-schedules.)
ACCUMULATE: attendance[Main] += Σ size; wait/max_wait per admitted; queue-length.
```
*EarlyExitCheck: **armed only for non-FriendsGroup entities** (A1-2: FGs watch each show in full). At fire, if E ∈ attendees[-10:], Bernoulli(0.5) → leave + free size + try_admit + schedule E's next activity; else no-op (pushed off the back by later arrivals).*

### D3 — EndOfDay1
```
TRIGGER: init-arrow, fires at clock = 20:00 day 1.
1. arrival_streams_active[Couple,Single] ← False  (FG already off since 13:00); shows_scheduling_active[Main,Side] ← False
2. for E in entities_live:
     FG     → overnight = "stay" if E.bought_lodging else "leave"
     Couple → if mean(m.satisfaction) > 7: overnight="stay"; revenue[lodging] += 250 × E.size  (= ₪500/couple)  else "leave"
     Single → overnight = "leave"
     if leaving ∧ queueing for a show: remove from show queue (no penalty); advance_itinerary_or_exit(E)
     if staying: stayers.append(E)
3. kpi.day1_snapshot ← freeze(kpi)
4. **re-enable day-2 streams (A2-2):** `arrival_streams_active[Couple,Single] ← True`; `shows_scheduling_active[Main,Side] ← True` (else day 2 gets exactly one arrival + one show each). Then schedule the day-2 bootstrap — **the sole day-2 re-seeder (A2-5):** ArrivalCouple@10:00, ArrivalSingle@09:00, ShowStart@Main/Side@09:00
   (EndOfFestival is seeded at init, NOT scheduled here — both day-boundary events are init/zigzag events, so EndOfDay1 must not also schedule EndOfFestival or it would double-schedule. FriendsGroupArrival is day-1-only, so it is not re-bootstrapped.)
5. for E in stayers: schedule Day2Resume(E) at 09:00 day 2   # A2-6: Day2Resume re-inits a FRESH day-2 itinerary for EVERY stayer (finished or not); any unfinished day-1 itinerary is discarded.
DRAIN (A2-1): in-progress activities finish naturally — the entity completes its current show/service and records its outcome. Its completion handler then applies the **past-close guard:** **leaving entity → `EndOfStay`**; **staying entity (clock ≥ 20:00) → PARK** (no day-1 next activity — `Day2Resume` is its sole restart). This kills the double-handling where a stayer in-flight at 20:00 is both routed to a new day-1 activity AND restarted on day 2.
NOTE: all entry/lodging prices are **PER PERSON** (audit C2-M4): ticket ₪500×size, FG bundle ₪700×size, couple lodging ₪250×size (=₪500/couple). PhotoStation print stays per-entity (#10).
```

---

## 9. Design decisions (locked)

Spec-interpretation judgment calls; all defensible, graders may probe at the defense.

1. **Queue abandonment — per-entity timer, per-member penalty, commit-on-first.** Timer from queue-join; cancelled when the first member starts service. On fire, queued members are pulled, every member loses `wait_penalty` (clamp 0), entity → next/EndOfStay.
2. **Abandonment at exactly 4 venues** (Photo, Charging, Merch, BodyArt); not shows/Entry/Food (professor-confirmed).
3. **MainStage rolling** admission; SideStage batch-at-start; DJ continuous. Fill-to-max scan head→tail.
4. **Farthest-10 early exit:** `EarlyExitCheck` at entry+15 (**non-FriendsGroup only — A1-2 below**); if still in `attendees[-10:]`, **Bernoulli(0.5)** → leave + free spots + roll-admit. **Spec-mandated** (*"…יעזבו את ההופעה 15 דקות לאחר שנכנסו למתחם בהסתברות 0.5"* = leave 15 min after **entering the area**, w.p. 0.5 — entry-time anchor, per entrant; quote verified vs PDF p.3, audit A2-4). **E2:** the roll-admit pulls the queue head into the running show and schedules *its own* +15 `EarlyExitCheck` (self-loop); every admission path (batch / walk-in / rolling) arms a +15 timer **for non-FG entrants**. **(A1-2, DECIDED 2026-05-30 — REVERSES the earlier C2-m7 call:** **FriendsGroups are EXEMPT** — the spec's *"שהות מלאה בכל הופעה"* (a full stay in each show) means an FG watches each MainStage show to the end. **Couples and Singles remain subject.** Singles' *"(באופן מלא)"* modifies the electronic/DJ show, not MainStage, so it does not exempt them here. ⇒ `EarlyExitCheck` is never armed for FriendsGroup entities.)
5. **Per-member parallel service** (Entry/Charging/Merch/BodyArt): finished members free their server immediately; the entity's next-activity decision waits for the last member (§5.4).
6. **Itineraries:** FG phased (3 shows → 4 stations); Single fixed (Merch → 2 Main + 2 Side + 1 DJ); Couple open-ended uniform alternation, no DJ.
7. **Exit (E4):** Singles + FG-**without**-lodging leave via `EndOfStay` when their itinerary exhausts. An FG that **bought lodging** does **not** exit at itinerary-end on day 1 — it stays overnight and **restarts a fresh itinerary on day 2** (`Day2Resume` re-inits, resumes at a show). **(A2-6, DECIDED: this fresh restart applies to ALL overnight stayers — FG and Couple — whether or not the day-1 itinerary finished; an unfinished day-1 remainder is discarded.)** Couples leave only at EndOfDay1/EndOfStay/EndOfFestival. **Routing is centralized in the **2-step drain-aware helper `advance_itinerary_or_exit(E)` (§8, B2):** Step 1 routes to the next performable activity (festival-open ∧ itinerary-remaining), else Step 2 **parks** a stayer / **`EndOfStay`s** a leaver (or anyone on the final day). Every completion handler routes through it, so none raw-schedules `EndOfStay` and over-exits an overnight FG (FLAG 1), nor routes a drain stayer to a new day-1 activity.**
8. **Entry + lodging revenue — PER PERSON (audit C2-M4, DECIDED):** every entry ticket is ₪500 × `entity.size`. FG pre-buys lodging at arrival (Bernoulli 0.7) → ₪700 bundle × size (replaces the ₪500 ticket). Couple decides at EndOfDay1 (**avg satisfaction > 7**) → lodging ₪250 × size (= ₪500/couple). Singles never stay. **PhotoStation print stays per-entity** (one ₪30 — decision #10). *Rationale: entry is processed per-member and a festival ticket is inherently per-person; per-entity would undercount the dominant revenue source ~(avg size)× and skew the revenue KPI.* **FG lodging timing (advisor handoff):** the spec is **silent** on *when* an FG pays for lodging; we draw the stay-Bernoulli (0.7) **at arrival** and pre-commit the ₪700 bundle. The FG stay probability is **flat** (unconditional 0.7), unlike the couple's end-of-day satisfaction gate, so day-1 dynamics are **independent of the draw time** (arrival vs end-of-day are statistically identical). Pre-commit ⇒ the discounted ₪700 combo; the ₪250 add-on is the couple's *spontaneous-decision* price. A grader preferring end-of-day realization (₪500 ticket + ₪250 add-on = ₪750) differs by only **+₪50 per staying group**, with no dynamic effect.
9. **Merch per-member item rolls** (0.8/0.4/0.9/0.3). A 5-person group can buy 5 shirts.
10. **PhotoStation per-entity:** one photo, one roll. Satisfied (0.7) → every member +2, +₪30 once; else (0.3)×(0.5) → every member −0.5. (Spec *"היישות מרוצה"*.)
11. **Entry: no abandonment**; 5 booths, scan+security per member; auto-entry alt zeros the scan.
12. **Food court (§5.5):** no abandonment; **one food stop per entity per day** — entity-level gate `food_done_today` set the moment the entity first finishes an activity in 13:00–15:00, so it never loops back (even members who declined get no second chance, even if nobody ate). 70% hungry per member; members may split across restaurants; parallel kitchen; **pizza consolidation** (individual = 1 person; P≥2 → `ceil(P/3)` family pizzas, one queuer + one sample-set each, covering up to 3); regroup at `max(EndEating)`; gate resets day 2. **(audit C2-M3, DECIDED:** *"יחידים בלבד יזמינו מנה אישית"* is read as *lone person* (P=1), **not** the Single entity-type — so any entity's single pizza-eater orders a ₪40 personal portion (P≥2 → `ceil(P/3)` family trays). Rationale: the sentence governs portion *sizing*, and a 3-serving tray for one person is wasteful. A grader may read *"יחידים"* as the Single type — defend the lone-person reading.)
13. **Day transitions:** `EndOfDay1` (stop streams/shows, overnight decisions, snapshot, schedule day-2 bootstrap + `Day2Resume`). **EndOfDay1 must re-enable `arrival_streams_active`/`shows_scheduling_active` to True for day 2 (A2-2 — else day 2 gets one arrival/show each) and is the SOLE day-2 re-seeder (A2-5 — streams don't self-schedule across the boundary).** **`EndOfFestival` is an init-seeded event (C), NOT scheduled by `EndOfDay1`** (avoids double-scheduling), and it **drains (C2)** — in-flight finishes (clock runs past 20:00), only idle/stuck entities are swept to `EndOfStay`; not a hard stop. **Past-close completions = Step 2 of the 2-step routing helper (B2/A2-1): staying entities PARK; leavers / final-day → `EndOfStay`.** `Day2Resume` resets `food_done_today` and re-inits a fresh itinerary, resuming the stayer at a show (E4, A2-6). Day-2 arrival rates = day-1 for Couple/Single.
14. **Show satisfaction:** good (0.5) `+(G−1)/2+(T−1)/19`, G∈{3,2,1}, T=integer **hour-of-day** end-hour (9–20, **not** absolute/elapsed — the /19 divisor is tuned so T=20→1.0; a day-2 elapsed clock would overshoot; audit A2-7); bad (0.5) −1. Clamp [0,10].
15. **Just-in-time sampling:** draw each quantity at the moment of use (service start, not queue-join); inter-arrivals self-scheduled on the current arrival firing. CRN-friendly. **(audit C2-M2, DECIDED:** because CRN pairs each alternative's replications with the baseline's, alternatives are compared with a **paired t-test** / paired-difference CI on the CRN-matched per-replication diffs — **not Welch**, which is invalid under CRN and discards the variance reduction. Notebook §18 to be renamed from "(Welch)"; keep Welch only as a fallback if CRN is ever dropped.)
16. **Satisfaction clamped to [0,10]** in every mutating handler.
17. **Mid-show walk-in (D3):** an entity routed to a running show with free capacity enters immediately (both stages); shows may also start under-cap. MainStage walk-in arms the entrant's `EarlyExitCheck`+15 (**non-FG only — A1-2**); SideStage has no farthest-10. Generalizes the spec's vacated-spot rule.
18. **Eating ≠ first activity (D4):** the food gate is evaluated only at real activity-completion handlers, never at `EndEntry`.
19. **Show-cycle ownership (E1):** `ShowEnd` schedules the next `ShowStart` at `now + break` (10 main / 5 side); `ShowStart` never self-schedules (drawn as the `ShowStart↔ShowEnd` mutual edge).
20. **`EndOfStay` convergence (D5):** one departure node consolidating exit logic from ~10 sources; on the diagram it's receive-only (every `→stations` edge folds in `→EndOfStay`). In code it's an ordinary terminal event.
21. **ChargingStation battery clamp `[0,99]`:** only `b<100` is mathematically required (avoids α=100/0); `b=0` is valid (α=1 → Uniform(0,40)), so empty-battery arrivals are allowed.
22. **Routing fix (E3):** Single's first stop after Entry is Merch (`EndEntry→Merch`); the v1 diagram's `EndEntry→BodyArt` was spurious. DJ is one node `EndAtDJstage` (E5).

---

## 10. Milestones

### M0 — Setup ✅
Venv + deps; `diagrams/`; notebook skeleton; `instructions_coverage.md`; deletion-checklist note. **Smoke run passes** — full top-to-bottom `nbconvert` execution, 0 errors, xlsx loads, DJ A-R empirical acceptance 0.374 ≈ 3/8 (M0–M4-skeleton level; the M4 run loop is still a partner stub).

### M1 — Pre-work diagrams ◀ ACTIVE
Read first: `הרצאה על תכנות אירועים.pdf`, the two event-programming labs (`תרגול 6/7`), and the **example solution's** event + handling diagrams (cell 11) for the accepted layout/abstraction level.

**Event-diagram conventions (lecturer's notation — the slides are terse, so these are the locked rules):**
- **Nodes:** circles only, one per event type, event name inside (no state-changes drawn in the node).
- **Exactly two arrow types, nothing else:**
  - **Zigzag arrow = initialization arrow.** Enters a node from outside; used *only* for events whose first instance must be seeded into the FEL at t=0 for the sim to run. It is **not** a generic "stochastic" marker — a deterministic init event (e.g. `EndOfDay1`) still gets it; a stochastic mid-run schedule does **not**.
  - **Solid arrow = scheduling arrow.** `A → B` means "when A fires it *may* sample a time and schedule B into the FEL." A self-loop (A schedules the next A) is a solid arrow.
  - **No condition/guard labels and no time-delay labels on arrows** — conditions and delays live in the handler logic, not on the graph.
- **Init (zigzag) events (7):** the 3 arrivals, the 2 `ShowStart`s, `EndOfDay1`, `EndOfFestival`. EndOfFestival is init-seeded, *not* scheduled by EndOfDay1 (§8 D3).
- **Layout:** high-degree hubs (`AbandonQueue`; the activity-completion cluster; `EndOfStay`) toward the center; arrival/entry sources on the left, day-boundary events on the right, departure bottom-left — mirrors the example. Arrows **bound** to nodes (drag a node, its arrows follow); never route an arrow through a node body.

- **Event diagram (23 nodes)** — all of §6 at the example's abstraction level: inter-activity movement is shown as the central venue cluster (bidirectional arrows around the `AbandonQueue` hub), *not* every (source,target) pair enumerated — the detailed per-event transitions live in the handling diagrams.
- **3 handling diagrams** — D1 AbandonQueue, D2 ShowStart@MainStage, D3 EndOfDay1 (flowcharts: rounded-rect actions + decision diamonds, RTL Hebrew; pseudocode in §8 is their visual form).
- **Workflow:** build in Excalidraw MCP → produce a share URL (PNGs downloaded manually into `diagrams/`) → base64-embed in notebook §3.
- **Verify:** every spec transition/condition/state-update for each diagrammed event appears; cross-check §7 I/O matrix + §9 decisions.

**Build state (2026-05-30):** **event diagram FINAL** — built by M1 session 3 and delivered as the repo-root `Untitled-2026-05-25-0416.excalidraw` (this **is** the deliverable event diagram — to be renamed/moved into `diagrams/`, **not** a stray scratch file). v1's known arrow errors are resolved; a verification doc is at `diagrams/build/VERIFY_EVENT_DIAGRAM.md`. The **v2.0 node set is validated and the complete directed-edge spec is authored** — model decisions folded into §6/§9 here; the full per-handler edge contract + routing matrix live in `diagrams/build/EVENT_NODE_EDGE_SPEC.md`; build pipeline + Excalidraw-MCP gotchas in `diagrams/build/README.md`. **In progress (parallel M1 sessions):** the 3 handling diagrams **D1/D2/D3** (flowcharts) are still being built. **Remaining:** finish D1/D2/D3 → embed all 4 as base64 in notebook §3 → mark M1 done in §10. **D1 must** route its itinerary-exhausted (`None`) case via `advance_itinerary_or_exit` (not a raw EndOfStay — §8 D1 step 5 fix); **D3 must** show couple lodging as **per-person** (C2-M4 — `+250 ₪ לאדם`, currently rendered as `+250 ₪`). **Folded from M1 review sessions into this PLAN rev:** §7.2 wait granularity (session 1); §8 D1 over-exit fix + `advance_itinerary_or_exit` helper + FLAG 2/3 (session 2). **Open build choice:** `EarlyExitCheck` has a dense walk-in fan-in (spec §4 #18) — keep it on the event graph, or relegate the walk-in routers to the D2 handling diagram if the mock is too busy (spec §5).

### M2 — Distribution fitting ✅ verified (numbers reproduce exactly)
- `FriendsGroup_arrival_intervals` → **Gamma** (α̂=1.239321, β̂=1.106439). Exp rejected (std/mean=0.87, skew=1.29, mode>0). KS D=0.0813<0.1358; Chi²(df=9)=12.80, p=0.172. FG A-R envelope c=1.130, accept≈88.5%.
- `MainStage_concert_duration` → **Normal** (μ̂=45.902765, σ̂=8.927433). KS D=0.1024<0.1358; Chi²(df=9)=14.00, p=0.122.
- Per sheet: MLE derivation (Gamma via Newton-Raphson on `ln α − ψ(α) = ln x̄ − mean(ln xᵢ)`; Normal closed form), KS (unmodified `1.358/√n`), Chi² (equal-prob bins, df=k−1−2, k-sensitivity table), diagnostics (strip / hist+PDF / CDF / Q-Q), Hebrew narrative incl. why Exp was rejected.
- **Implication:** Gamma has no closed-form inverse CDF → FG arrivals sampled via A-R with Exp envelope (mean-matched, c≈1.13, accept ≈88%).

### M3 — Sampling (`Sampler` class) ✅ verified + fixed (commits ff4c2b7, 66227cf)
One `Sampler` class taking an `RNGStreams` instance; math in preceding markdown; one-line English code comments.
- **Couple rate fixed:** CONFIG `couple_arrival_lambda` `1.0/60.0` → **`1.0`** (60/hr, mean 1 min — verified 1.002 min); `§6` mapping row + the `couple_arrival_interval` docstring fixed; `couple_lodging_threshold` comment "at least one member" → "average".
- **Positive-normal truncation implemented** (was *missing* — the prior plan described it as present): Box-Muller helper now rejection-resamples until x>0 for the three Normal *durations* (main show, glitter, food register; `food_register N(5,1.5)` had ~0.045% negatives, now strictly positive). `charging_battery` is **clamped to [0,99]** (decision #21), not positive-truncated.
- **NumPy-2.x:** DJ A-R validation uses `np.trapezoid` (`np.trapz` removed in NumPy 2.x).
- **RNGStreams hoisted:** the `RNGStreams` class is defined immediately **before** the `Sampler` in §6 (top-to-bottom run needs it first); the `## 12. RNGStreams` markdown header in the M4 region is now just leftover scaffolding.

| Quantity | Distribution | Algorithm |
|---|---|---|
| FG arrival | Gamma | **A-R, Exp envelope** |
| Couple arrival | **Exp(λ=1/min ⇒ 60/hr)** | Inverse |
| Single arrival | Exp(λ≈500/420/min) | Inverse |
| FG size | DiscreteUniform[3,6] | Inverse |
| Ticket scan / security | U(1.5,3) / Exp(2) | Inverse |
| MainStage / SideStage show | Normal / U(20,30) | **Box-Muller** / Inverse |
| **DJstage stay** | piecewise | **Acceptance-Rejection** (mandatory) |
| Photo duration | piecewise (= example pool) | **Piecewise inverse-transform** (audit C1-n1: one *u*, global piecewise CDF — the example's `inverse_transform_PD`) |
| Charging battery / charge time | N(40,15) / α-PDF | **Box-Muller** / Inverse (`t=40(1−U^{1/α})`) |
| Merch / BodyArt glitter,neon,henna | U(2,6) / N(15,3),Exp(12),U(17,22) | Inverse / BM,Inv,Inv |
| Food prep pizza/burger/asian; register; meal | U(4,6)/U(3,4)/U(3,7); N(5,1.5); U(15,35) | Inverse / **Box-Muller** / Inverse |
| All Bernoulli decisions | Bernoulli(p) | Inverse |

Coverage: Inverse ✅ (incl. Photo piecewise), Box-Muller ✅ (4 normals), A-R ✅ ×2 (DJ mandatory + FG Gamma). **Composition not used** — spec lists methods with *"או"* (or); only A-R is mandatory (satisfied by DJ). *(audit C1-n1; was mislabeled "Composition")*
- **DJ A-R:** envelope U(20,60); PDF jumps up at 40 (sup f = 1/15 at 40⁺); c = (1/15)·40 = 8/3; accept 3/8 ≈ 0.375. **Validation §6.8:** 20,000 attempts, empirical vs 3/8 + histogram vs PDF.

### M4 — OOP class skeleton (stubs exist; flesh out)
Read first: OOP-refresher lab (`תרגול 2`) + example cells 13-22 for style.
- **Customer** (concrete): id, satisfaction (clamp), in_queue_at, in_service_at, service_end_time, done_awaiting_regroup, wants_food, food_choice; `update_satisfaction`, `on_show_end`. (The once-per-day food gate `food_done_today` is **entity-level** on `Group`, not per-member.)
- **Group** (abstract) + FriendsGroup / Couple / Single (sizes, tolerances/penalties, itinerary logic per §5.2).
- **Activity** (abstract) + MainStage / SideStage / DJstage / PhotoStation / ChargingStation / MerchTent / BodyArt / Entry / FoodCourt (per §5.3).
- **QueueServer**: FIFO + per-entity abandonment timer (commit-on-first cancel); per-member parallel dispatch (§5.4); tracks wait, queue-length, abandonment.
- **KPITracker** (§7.2), **RNGStreams** (one Random per source; master_seed; CRN by reseeding only affected streams).
- **Event** (abstract) — 23 subclasses are partner stubs (names = §6). **Simulation** (skeleton) — partners fill `run()`.
- Expand §7 state per class as needed (§7 is a seed). M4 ends with a smoke cell instantiating every class.

### M5 — Handoff
§2 Design Decisions Log (internal div) · CONFIG→alternatives docstring · partner roadmap (event hooks, KPI hooks, Sampler index, RNG names, GenAI log) · deletion-pass dry-run · full top-to-bottom run.

**PLAN_AUDIT notebook fixes — status (updated 2026-05-30; smoke run passes top-to-bottom, 0 errors):**
- ✅ **C1-M5:** `arrival_rate_multiplier` wired into the 3 `Sampler.*_arrival_interval` methods (mean ÷ multiplier) — Advertising alternative now functional.
- ✅ **C1-n1:** `photo_duration` docstring relabeled "Composition" → "piecewise inverse-transform".
- ✅ **C1-m6:** stale "(11h)" CONFIG comment deleted (windowing assumption stays documented in the CONFIG line); *still to do: restate it in the §2 assumptions narrative once §2 is written.*
- ✅ **C2-M1:** §15 reframed warmup-deletion → **replication-count (terminating; no warmup)**; partners fill the method (N for rel-precision 0.1, Bonferroni-split α=0.1).
- ✅ **C2-M2:** §18 renamed Welch → **paired t-test** (paired-difference CI under CRN); partners fill.
- ⏸ **C1-n4:** orphan `## 12. RNGStreams` header — **deferred to the final renumber pass** (deleting now would churn §13–20 numbering + every PLAN `§N` cross-ref while partners work in those sections).
- ⏸ **C2-M4:** entry/lodging revenue **per-person** (×`entity.size`; Photo stays per-entity) — **lands when the run-loop/handler code is written** (currently partner stubs; rule locked in §5.7/§7.3/§8/§9).

---

## 11. CONFIG → alternatives mapping

| Alternative | NIS | CONFIG fields |
|---|---|---|
| Better kitchen team | 500K | `food_unsatisfied_prob=0.3` (base 0.4 − 0.1; spec *"קטנה ב-0.1"* = by, not to — audit A1-1), `food_choose_prob=0.85` |
| Expanded security (cap +30%) | 650K | `stage_capacity_main=260, _side=130, _dj=91` |
| Mainstream investment | 300K | `merch_band_shirt_prob=0.8`, `genre_score_main=4` |
| Photo + BodyArt expansion | 150K | `photo_servers=4`, `bodyart_artists=3` |
| Advertising | 200K | `arrival_rate_multiplier=1.2` (all 3 generators) |
| Auto entry | 600K | `entry_skip_scan=True` |
| Visitor gifts | 200K | `initial_satisfaction=6.5` |

Partners pick **≥2 combinations** of alternatives, each ≤ ₪1,000,000 and **using most of the budget** (spec: *"בחרו בלפחות 2 קומבינציות של חלופות"*, *"המטרה היא להשתמש ברובו"*); overall confidence 0.9; relative precision 0.1. *(audit C2-m5)*

---

## 12. Files, references, verification, submission

**Files:** `Queuechella_Simulation.ipynb` (deliverable) · `PLAN.md` (this) · `instructions_coverage.md` (spec checklist + handoff) · `Course Project 2026B.pdf` (spec, read-only) · `samples_for_simulation.xlsx` (M2 data) · `example solution.ipynb` (structural + report reference) · `diagrams/` (M1 diagrams + M2 plots) · `diagrams/build/` (event-diagram build workspace: `EVENT_NODE_EDGE_SPEC.md` detailed node+edge reference, `README.md` build pipeline + MCP gotchas, pipeline scripts).

**Reused from example:** inverse-transform composition for the piecewise PDF (cell 8) → PhotoStation (identical PDFs); `empirical_cdf`/`ks_test` helpers (cell 5); RTL Hebrew div styling; class-category structure. (The example's Exponential MLE is *not* the FG fit — kept only in an internal div as the tested-and-rejected hypothesis.)

**End-to-end verification:** notebook runs clean (VSCode + Colab); 4 diagrams embedded §3; both fits pass KS+Chi² with diagnostics; every sampler callable + couple-rate fixed + DJ A-R ≈3/8; OOP skeleton instantiable; CONFIG fully parameterized; internal divs regex-findable; coverage items 1-3 + pre-work checked; GenAI log ≥1 entry.

**Submission:** Group #20 · Ido Malach 318782208 · Yonatan Dolman 208987644 · Etan Cohen 322067448 · 2026-06-29.

---

## Appendix A — Event-decomposition methodology (general process)

The reusable 5-step method behind §5–§8, kept for the defense and for partners extending the model.

**Core distinction — state vs. statistics.** State = the minimum info needed to determine what the system does *next* (about the future). Accumulators = info carried only to report performance at the end (about the past). Same value can play both roles at different moments (e.g. `member.satisfaction` gates the couple overnight decision *and* is logged at exit).

**Dependency chain:** Entities & Resources → Events → State variables → Event handlers → Accumulators. You can't define state until you know what's in the system.

1. **Identify entities, resources, attributes.** Entity = flows through the system, subject of events. Resource = finite-capacity thing entities compete for. Attribute = per-instance property affecting future behavior. Things that look like entities but have no behavior (a "show") are cleaner as resource attributes.
2. **Trace each entity lifecycle** in plain English; every "and then X starts/ends/decides" is a candidate event. Event types are determined by **resource × phase**, not entity type — different entities share the event set, differing in attributes. Decision events (lunch, overnight) are real events. Fill-to-max is a sub-routine, not an event.
3. **Build the catalog (split vs parameterize).** Split on independent scheduling sources or different downstream graphs (3 arrivals); parameterize when only numbers differ (abandonment timeout/penalty; overnight rule).
4. **Separate state from accumulators** (per §7) — this is what seeds the class fields. Treat it as a starting point and expand when the classes force new state to light.
5. **Specify handler logic** (per §8) — for each event: state read, state written, events scheduled (with delays), accumulators touched, edge cases.

**Two principles:** *Does it advance time, or just gate a decision happening now?* (advance → node; gate → guard in a handler). *One node per distinct moment in time, not per outcome* (two effects at the same instant = one handler; separated by elapsed time = two events).
