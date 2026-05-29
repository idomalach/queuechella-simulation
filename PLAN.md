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
- **Diagrams:** Excalidraw MCP tools (`mcp__claude_ai_Excalidraw__*`) — the event diagram + 3 handling diagrams. Build → `export_to_excalidraw` share URL → download PNGs manually into `diagrams/` → base64-embed into notebook §3. (The MCP renders to the UI and shares a URL; it does not write PNG files directly.)
- **xlsx data:** `samples_for_simulation.xlsx` at root. At submission, mirror to a **public GitHub raw URL** for Colab (no upload needed); dev uses the local relative path.
- **Dependencies:** `pandas numpy scipy matplotlib openpyxl jupyter` (in a venv under `~/venvs/`, never inside this iCloud-synced folder).

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
[code]  Sampler  ·  6.8 DJ A/R validation
### 7. מחלקת לקוח · 8. מחלקות אורחים · 9. מחלקות מתקנים · 10. תור · 11. מעקב מדדים  [M4]
### 12. מחלקת אירועים (Event base) [PARTNERS extend → 23 subclasses]
### 13. הסימולציה (skeleton) [PARTNERS fill run loop]
### 14. חימום · 15. מדדי מצב קיים · 16. בחינת חלופות · 17. השוואת חלופות · 18. סיכום והמלצות  [PARTNERS]
### 19/20. דיווח GenAI
```

---

## 5. The festival model

### 5.1 Setting
- Two days, 09:00–20:00 each. Every **guest** (individual) carries a satisfaction score: start 5, max 10, min 0, **clamped to [0, 10]** wherever mutated.
- Alternatives budget ₪1,000,000; compare at 90% overall confidence (α=0.1), relative precision γ=0.1.

### 5.2 Entities (3 types)

| Entity | Arrival | Window | Days | Size |
|---|---|---|---|---|
| **FriendsGroup** | from xlsx → **Gamma**(α≈1.24, β≈1.11), sampled via A-R | 09:00–13:00 | **Day 1 only**; stays overnight w.p. 0.7 | DiscreteUniform[3,6] |
| **Couple** | **Exp, 60/hour ⇒ λ=1/min, mean inter-arrival 1 min** | 10:00–16:00 | Day 1 or 2; stays iff **avg satisfaction > 7** at end of day 1 | 2 |
| **Single** | Exp, 500/day (windowed over 09:00–16:00 ⇒ λ≈500/420 per min) | 09:00–16:00 | one day only (1 or 2) | 1 |

> **Couple rate is the one easy-to-get-wrong number.** Spec *"תוחלת של 60 בשעה"* parallels Single's *"תוחלת של 500 ביום"* (= count per period) ⇒ **60 couples/hour**, mean inter-arrival **1 minute** (~360/day). Not 1/hour. CONFIG must set `couple_arrival_lambda = 1.0` (it currently reads `1.0/60.0` — a live bug to fix in M3).

**Per-entity behavior:**
- **FriendsGroup** — strict two-phase itinerary: **Phase 1** = one show of each genre (Main, Side, DJ); **Phase 2** = all 4 stations (Photo, Charging, Merch, BodyArt). Shortest-queue pick *within* the current phase. (Spec: *"לאחר שהות מלאה בכל הופעה יעברו בכלל העמדות"*.)
- **Couple** — open-ended alternation show→station→show→…; show step = uniform{Main, Side} (no DJ — couples dislike electronic); station step = uniform{Photo, Charging, Merch, BodyArt}. Runs until EndOfDay1/EndOfStay.
- **Single** — fixed itinerary: Merch first, then 2 Main + 2 Side + 1 DJ shows (shortest-queue among remaining required shows). Leaves when itinerary exhausts.
- **Group movement:** members move as one unit — nobody proceeds to the next activity until all finish the current one. **Food court is the only exception** (members split across restaurants; see §5.5).

### 5.3 Resources (11 venues)

| Resource | Capacity | Service mode | Notes |
|---|---|---|---|
| Entry | 5 booths | **per-member, parallel** | scan `U(1.5,3)` + security `Exp(mean 2)` back-to-back, one `EndEntry` per member. **No abandonment.** Auto-entry alt zeros the scan term. |
| MainStage | 200 | per-entity | mainstream; show duration **Normal**(M2) via Box-Muller; 10-min break; spatial order = entry order; **farthest-10 early exit**; rolling admission. |
| SideStage | 100 | per-entity | indie; show `U(20,30)`; 5-min break; batch admission at show start. |
| DJstage | 70 | per-entity | electronic; continuous (no shows); stay-time piecewise PDF, **A-R sampling**; roll-admit as capacity frees. |
| PhotoStation | 3, shared queue | **per-entity** | one photo per visit; one shared satisfaction roll. |
| ChargingStation | 150 | per-member, parallel | battery on arrival `N(40,15)`; charge time `f(t)` with α=100/(100−battery). |
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

**One food stop per entity per day.** An entity becomes eligible the first time it **finishes an activity during 13:00–15:00** with its entity-level gate `food_done_today` still False. At that moment the gate is **set to True immediately** (so it cannot re-fire, even between the food-court sub-steps), and the entity makes its single food stop: **per member independently**, roll **hungry (70%)**; if hungry, pick a food type — **burger 3/8, pizza 1/4, asian 3/8**. After the stop the entity never returns to the food court that day — **even members who declined get no second chance**, and "just finished eating" can't loop back into another food visit. If no member is hungry, the stop still counts as made (the gate stays set). The gate **resets at day 2** for overnight stayers (via `Day2Resume`).

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
| Show, good experience (w.p. 0.5) | `+(G−1)/2 + (T−1)/19`, G∈{main 3, indie 2, electronic 1}, T = integer end-hour | per-member |
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
| Entry ticket | ₪500 |
| Overnight add-on | ₪250 · Bundle (ticket + overnight) | ₪700 |
| Merch: t-shirt 0.8 / hat 0.4 / flag 0.9 / band-shirt 0.3 (per member) | ₪100 / ₪50 / ₪40 / ₪200 |
| Photo print (w.p. 0.7, per entity) | ₪30 |
| Food: individual pizza / family pizza / burger / asian | ₪40 / ₪100 (×`ceil(P/3)`) / ₪100 (per burger member) / ₪65 (per asian member) |

---

## 6. Event catalog (23 nodes)

Built by passing each candidate event through two tests — **time-advance** (does it advance the clock, or just gate a decision happening now?) and **split-vs-parameterize** (split on independent scheduling sources or different downstream graphs; parameterize when only numbers differ).

### Group A — Bootstrap (zigzag init-arrow), 7
`FriendsGroupArrival`, `CoupleArrival`, `SingleArrival` (zigzag init + solid self-loop scheduling the next arrival) · `ShowStart@MainStage`, `ShowStart@SideStage` (zigzag init at 09:00; each `ShowEnd` schedules the next after the break) · `EndOfDay1` (zigzag init, clock-fixed 20:00 day 1) · `EndOfFestival` (zigzag init, clock-fixed 20:00 day 2). **All 7 get a zigzag arrow because their first instance must be seeded into the FEL at t=0 for the sim to run** — see the convention block in §10/M1.

> Multi-day streams: when a Couple/Single inter-arrival would cross today's window-end and tomorrow-arrivals remain, schedule for tomorrow's window-start. Shows: if the next `ShowStart` would fall after 20:00 on day 1, schedule it for 09:00 day 2.

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
| 20 | `EarlyExitCheck` | per entity entering MainStage, at `entry+15` | if entity still in `attendees[-10:]`, **Bernoulli(0.5)** → leave, free `entity.size` spots, roll-admit. **Spec-mandated 0.5** (*"…יעזבו את ההופעה 15 דקות לאחר שנכנסו ויפנו למתחם בהסתברות 0.5"*). |
| 21 | `BreakEnd@BodyArt` | `EndService@BodyArt` when count %10==0 | artist available; dispatch next. |
| 22 | `Day2Resume` | `EndOfDay1` per overnight stayer, at 09:00 day 2 | reset `food_done_today` (new food stop allowed); re-evaluate next activity (in case stuck in a stale show queue). |

### Group E — Departure, 1
**23. `EndOfStay`** (per entity) — scheduled (usually at `now`) when a visit ends: itinerary exhausted (FG/Single), `overnight_decision == "leave"` at the moment the current activity completes, or `EndOfFestival` for day-2 stragglers. Logs every member's final satisfaction into `kpi.final_satisfactions`, marks the entity departed, frees any held resources.

### What is NOT a separate node (folded into handlers)
`JoinQueue`, `StartService`, `BreakStart`, `LunchDecision`, `OvernightDecision`, every satisfaction/experience roll, food-type choice, **fill-to-max admission** (a sub-routine called from each `ShowEnd`/`EndService`/`EarlyExitCheck`/`BreakEnd`), lunch-window open/close. None advance time independently.

### Termination patterns used
A — hard end at fixed time (`EndOfDay1`, `EndOfFestival`: init-arrows). B — stop source, drain (arrival streams stop self-scheduling at window-end; lunch window is a guard). C — service-completion (`ShowStart`→`ShowEnd`; `EndService@BodyArt`→`BreakEnd`; MainStage entry→`EarlyExitCheck`).

---

## 7. State variables vs accumulators

> **This is a *seed* for the M4 class design, not the finished state model.** The split (state = what determines what happens next; accumulator = what's carried only for the final report) tells us which fields go on which class. Building the classes will surface more — e.g. `member.done_awaiting_regroup`, `member.wants_food`, `member.food_choice`, `entity.pizza_count`, per-restaurant single-register state, explicit server-slot objects (`.busy`, `.member`). Expand this section during M4.

### 7.1 State

**System:** `clock` · `day` (1/2) · `fel` (min-heap) · `arrival_streams_active[stream]` · `shows_scheduling_active[stage]`.

**Per entity:** `id` · `type` · `size` · `members` · `arrival_time` · `bought_lodging` (FG) · `itinerary_remaining` (FG: `shows_remaining`+`stations_remaining` by phase; Single: ordered list; Couple: `next_step`) · `itinerary_phase` (FG) · `current_activity` · `current_position` ∈ {queueing, in_service, in_show, eating, transit, departed} · `queue_join_time` · `abandon_event` (ref, for commit-on-first cancel) · `overnight_decision` · **`food_done_today`** (entity-level once-per-day food gate; reset at day 2).

**Per member (Customer):** `id` · `satisfaction` (gates couple overnight; feeds final-satisfaction KPI) · `in_service_at` · `service_end_time` · `done_awaiting_regroup` · `wants_food` · `food_choice` (set during the entity's single food stop).

**Per resource:** `queue` (FIFO of entities; length drives shortest-queue) · `servers` (slots: `.busy`, `.member`) · `in_service_entities`.

**Per stage:** `attendees` (entry-ordered; MainStage uses `attendees[-10:]`) · `spots_used` · `current_show.{genre, end_time}` · `next_show_event`.

**Per BodyArt artist:** `drawings_since_break` · `on_break` · `break_end_event`.

**Per restaurant (×3):** `cashier_busy` · `register_queue` (food-units) · `prep_in_flight` · `eating_in_flight`.

### 7.2 Accumulators (KPI)

`final_satisfactions: list[float]` (per member, at `EndOfStay`/`EndOfFestival`) · `wait_times[venue]`, `max_wait[venue]` (at StartService + AbandonQueue) · `queue_length_over_time[venue]` · `revenue_by_source` {ticket, lodging, merch_*, photo_print, food_*} · `total_revenue` · `abandonments[venue]` · `attendance[venue]` · `day1_snapshot`.

### 7.3 Event → I/O matrix (R = reads state, W = writes state, A = accumulates)

| Event | Reads | Writes | Accumulates |
|---|---|---|---|
| `*Arrival` | clock, stream active | create entity, entry-queue join | revenue[ticket], [lodging] (FG) |
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
| `EndOfDay1` | all live entities, clock | stop streams/shows; per-entity overnight decision; pull leaving show-queue stragglers; schedule day-2 bootstrap | revenue[lodging], day1_snapshot |
| `EndOfFestival` | live entities | iterate EndOfStay for stragglers | finalize final_satisfactions |
| `Day2Resume` | entity ref | re-select next activity | — |
| `EndOfStay` | members' satisfaction | mark departed; free resources | final_satisfactions |

---

## 8. Handler pseudocode — the 3 diagrammed events (M1)

These are the M1 handling-diagram deliverables (the other 20 handlers are partners' Step-5 work, same template). Conventions: `now` = clock; `E` = entity; `V` = venue; `kpi.*` = accumulator.

### D1 — AbandonQueue(E, V)   [V ∈ {Photo, Charging, Merch, BodyArt}]
```
TRIGGER: scheduled at JoinQueue@V for now + E.wait_tolerance; CANCELLED when E's first member starts service.
         ⇒ on fire, no member of E is in service at V.
1. if E ∉ V.queue: return                              # stale firing
2. V.queue.remove(E); E.current_position ← "transit"; E.queue_join_time ← None
3. for m in E.members: m.satisfaction ← clamp(m.satisfaction − E.wait_penalty, 0, 10)
4. next ← select_next_activity(E)                      # FG phase-aware shortest-queue / Single fixed / Couple uniform
5. if next is None: schedule EndOfStay(E) at now; return
6. next.queue.append(E); E.current_activity ← next; E.queue_join_time ← now
   if next ∈ {Photo, Charging, Merch, BodyArt}: E.abandon_event ← schedule AbandonQueue(E, next) at now + E.wait_tolerance
   try_admit(next, now)
ACCUMULATE: abandonments[V] += 1; queue_length_over_time[V] and [next] sampled.
```
*No "members in service" branch — commit-on-first guarantees none. Penalty clamps at 0.*

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
5. for E in admitted: schedule EarlyExitCheck(E) at now + 15
6. next_start ← now + duration + 10; if shows_scheduling_active ∧ next_start < day_end(day): schedule ShowStart@MainStage at next_start
ACCUMULATE: attendance[Main] += Σ size; wait/max_wait per admitted; queue-length.
```
*EarlyExitCheck: at fire, if E ∈ attendees[-10:], Bernoulli(0.5) → leave + free size + try_admit + schedule E's next activity; else no-op (pushed off the back by later arrivals).*

### D3 — EndOfDay1
```
TRIGGER: init-arrow, fires at clock = 20:00 day 1.
1. arrival_streams_active[Couple,Single] ← False  (FG already off since 13:00); shows_scheduling_active[Main,Side] ← False
2. for E in entities_live:
     FG     → overnight = "stay" if E.bought_lodging else "leave"
     Couple → if mean(m.satisfaction) > 7: overnight="stay"; revenue[lodging] += 250  else "leave"
     Single → overnight = "leave"
     if leaving ∧ queueing for a show: remove from show queue (no penalty); advance_itinerary_or_exit(E)
     if staying: stayers.append(E)
3. kpi.day1_snapshot ← freeze(kpi)
4. schedule day-2 bootstrap: ArrivalCouple@10:00, ArrivalSingle@09:00, ShowStart@Main/Side@09:00
   (EndOfFestival is seeded at init, NOT scheduled here — both day-boundary events are init/zigzag events, so EndOfDay1 must not also schedule EndOfFestival or it would double-schedule. FriendsGroupArrival is day-1-only, so it is not re-bootstrapped.)
5. for E in stayers: schedule Day2Resume(E) at 09:00 day 2
DRAIN: in-progress activities finish naturally; their end handlers read overnight_decision → EndOfStay (leave) or next activity (stay).
NOTE: lodging ₪250 is per-couple (parallels FG's per-group ₪700 bundle).
```

---

## 9. Design decisions (locked)

Spec-interpretation judgment calls; all defensible, graders may probe at the defense.

1. **Queue abandonment — per-entity timer, per-member penalty, commit-on-first.** Timer from queue-join; cancelled when the first member starts service. On fire, queued members are pulled, every member loses `wait_penalty` (clamp 0), entity → next/EndOfStay.
2. **Abandonment at exactly 4 venues** (Photo, Charging, Merch, BodyArt); not shows/Entry/Food (professor-confirmed).
3. **MainStage rolling** admission; SideStage batch-at-start; DJ continuous. Fill-to-max scan head→tail.
4. **Farthest-10 early exit:** `EarlyExitCheck` at entry+15; if still in `attendees[-10:]`, **Bernoulli(0.5)** → leave. **Spec-mandated** (*"…ויפנו למתחם בהסתברות 0.5"*).
5. **Per-member parallel service** (Entry/Charging/Merch/BodyArt): finished members free their server immediately; the entity's next-activity decision waits for the last member (§5.4).
6. **Itineraries:** FG phased (3 shows → 4 stations); Single fixed (Merch → 2 Main + 2 Side + 1 DJ); Couple open-ended uniform alternation, no DJ.
7. **Exit:** Singles + FG leave via `EndOfStay` when itinerary exhausts; Couples only at EndOfDay1/EndOfStay/EndOfFestival.
8. **Lodging revenue:** FG pre-buys at arrival (Bernoulli 0.7 → ₪700 bundle); Couple decides at EndOfDay1 (**avg > 7**) → ₪250 (per-couple); Singles never stay.
9. **Merch per-member item rolls** (0.8/0.4/0.9/0.3). A 5-person group can buy 5 shirts.
10. **PhotoStation per-entity:** one photo, one roll. Satisfied (0.7) → every member +2, +₪30 once; else (0.3)×(0.5) → every member −0.5. (Spec *"היישות מרוצה"*.)
11. **Entry: no abandonment**; 5 booths, scan+security per member; auto-entry alt zeros the scan.
12. **Food court (§5.5):** no abandonment; **one food stop per entity per day** — entity-level gate `food_done_today` set the moment the entity first finishes an activity in 13:00–15:00, so it never loops back (even members who declined get no second chance, even if nobody ate). 70% hungry per member; members may split across restaurants; parallel kitchen; **pizza consolidation** (individual = 1 person; P≥2 → `ceil(P/3)` family pizzas, one queuer + one sample-set each, covering up to 3); regroup at `max(EndEating)`; gate resets day 2.
13. **Day transitions:** `EndOfDay1` (stop streams/shows, overnight decisions, snapshot, schedule day-2 bootstrap + `Day2Resume`); `EndOfFestival` (hard end); day-2 arrival rates = day-1 for Couple/Single.
14. **Show satisfaction:** good (0.5) `+(G−1)/2+(T−1)/19`, G∈{3,2,1}, T=integer end-hour; bad (0.5) −1. Clamp [0,10].
15. **Just-in-time sampling:** draw each quantity at the moment of use (service start, not queue-join); inter-arrivals self-scheduled on the current arrival firing. CRN-friendly.
16. **Satisfaction clamped to [0,10]** in every mutating handler.

---

## 10. Milestones

### M0 — Setup ✅ (smoke-test pending)
Venv + deps; `diagrams/`; notebook skeleton; `instructions_coverage.md`; deletion-checklist note. Remaining: top-to-bottom smoke run, xlsx loads.

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

**Build state (2026-05-29):** event diagram **v1** built & exported (Excalidraw); layout + B&W conventions approved. **Arrows have known errors** (missing / reversed / spurious) — root cause: §6/§8 specify edges in prose, not as an explicit list. **Next (v2.0):** (1) validate the node set vs the spec, (2) author a **complete directed-edge table** here in §6/§8 (source→target, type ∈ schedule/init/self/mutual), (3) regenerate via `diagrams/build/` (pipeline: `gen_excali_event.py` → `event_layout_mock.py` check → `to_native_min.py` → `export_to_excalidraw`). Handling diagrams D1/D2/D3 not yet built.

### M2 — Distribution fitting ✅ (verify this session)
- `FriendsGroup_arrival_intervals` → **Gamma** (α̂≈1.239, β̂≈1.106). Exp rejected (std/mean=0.87, skew=1.29, mode>0). KS D=0.081<0.136; Chi²(k=12) p=0.17.
- `MainStage_concert_duration` → **Normal** (μ̂≈45.90, σ̂≈8.93). KS D=0.102<0.136; Chi²(k=12) p=0.12.
- Per sheet: MLE derivation (Gamma via Newton-Raphson on `ln α − ψ(α) = ln x̄ − mean(ln xᵢ)`; Normal closed form), KS (unmodified `1.358/√n`), Chi² (equal-prob bins, df=k−1−2, k-sensitivity table), diagnostics (strip / hist+PDF / CDF / Q-Q), Hebrew narrative incl. why Exp was rejected.
- **Implication:** Gamma has no closed-form inverse CDF → FG arrivals sampled via A-R with Exp envelope (mean-matched, c≈1.13, accept ≈88%).

### M3 — Sampling (`Sampler` class) ✅ (verify + fix this session)
One `Sampler` class taking an `RNGStreams` instance; math in preceding markdown; one-line English code comments.
- **⚠️ Fix (live bug):** CONFIG `couple_arrival_lambda` `1.0/60.0` → **`1.0`** (60/hr, mean 1 min); fix its comment; update `couple_lodging_threshold` comment "at least one member" → "average".
- **Positive-normal truncation:** Box-Muller helper rejection-resamples until x>0 for the three Normal *durations* (main show, glitter, food register; trunc ≤~0.04%); `charging_battery` clamps to [1,99] (keeps α=100/(100−b) finite).

| Quantity | Distribution | Algorithm |
|---|---|---|
| FG arrival | Gamma | **A-R, Exp envelope** |
| Couple arrival | **Exp(λ=1/min ⇒ 60/hr)** | Inverse |
| Single arrival | Exp(λ≈500/420/min) | Inverse |
| FG size | DiscreteUniform[3,6] | Inverse |
| Ticket scan / security | U(1.5,3) / Exp(2) | Inverse |
| MainStage / SideStage show | Normal / U(20,30) | **Box-Muller** / Inverse |
| **DJstage stay** | piecewise | **Acceptance-Rejection** (mandatory) |
| Photo duration | piecewise (= example pool) | **Composition** |
| Charging battery / charge time | N(40,15) / α-PDF | **Box-Muller** / Inverse (`t=40(1−U^{1/α})`) |
| Merch / BodyArt glitter,neon,henna | U(2,6) / N(15,3),Exp(12),U(17,22) | Inverse / BM,Inv,Inv |
| Food prep pizza/burger/asian; register; meal | U(4,6)/U(3,4)/U(3,7); N(5,1.5); U(15,35) | Inverse / **Box-Muller** / Inverse |
| All Bernoulli decisions | Bernoulli(p) | Inverse |

Coverage: Inverse ✅, Box-Muller ✅ (4 normals), Composition ✅ (Photo), A-R ✅ ×2 (DJ mandatory + FG Gamma).
- **DJ A-R:** envelope U(20,60); PDF jumps up at 40 (sup f = 1/15 at 40⁺); c = (1/15)·40 = 8/3; accept 3/8 ≈ 0.375. **Validation §6.8:** 20,000 attempts, empirical vs 3/8 + histogram vs PDF.

### M4 — OOP class skeleton (stubs exist; flesh out)
Read first: OOP-refresher lab (`תרגול 2`) + example cells 13-22 for style.
- **Customer** (concrete): id, satisfaction (clamp), in_queue_at, in_service_at, service_end_time, food_eaten_today, lunch_decided, done_awaiting_regroup, wants_food, food_choice; `update_satisfaction`, `on_show_end`.
- **Group** (abstract) + FriendsGroup / Couple / Single (sizes, tolerances/penalties, itinerary logic per §5.2).
- **Activity** (abstract) + MainStage / SideStage / DJstage / PhotoStation / ChargingStation / MerchTent / BodyArt / Entry / FoodCourt (per §5.3).
- **QueueServer**: FIFO + per-entity abandonment timer (commit-on-first cancel); per-member parallel dispatch (§5.4); tracks wait, queue-length, abandonment.
- **KPITracker** (§7.2), **RNGStreams** (one Random per source; master_seed; CRN by reseeding only affected streams).
- **Event** (abstract) — 23 subclasses are partner stubs (names = §6). **Simulation** (skeleton) — partners fill `run()`.
- Expand §7 state per class as needed (§7 is a seed). M4 ends with a smoke cell instantiating every class.

### M5 — Handoff
§2 Design Decisions Log (internal div) · CONFIG→alternatives docstring · partner roadmap (event hooks, KPI hooks, Sampler index, RNG names, GenAI log) · deletion-pass dry-run · full top-to-bottom run.

---

## 11. CONFIG → alternatives mapping

| Alternative | NIS | CONFIG fields |
|---|---|---|
| Better kitchen team | 500K | `food_unsatisfied_prob=0.1`, `food_choose_prob=0.85` |
| Expanded security (cap +30%) | 650K | `stage_capacity_main=260, _side=130, _dj=91` |
| Mainstream investment | 300K | `merch_band_shirt_prob=0.8`, `satisfaction_genre_main=4` |
| Photo + BodyArt expansion | 150K | `photo_servers=4`, `bodyart_artists=3` |
| Advertising | 200K | `arrival_rate_multiplier=1.2` (all 3 generators) |
| Auto entry | 600K | `entry_skip_scan=True` |
| Visitor gifts | 200K | `initial_satisfaction=6.5` |

Partners pick combinations ≤ ₪1,000,000; overall confidence 0.9; relative precision 0.1.

---

## 12. Files, references, verification, submission

**Files:** `Queuechella_Simulation.ipynb` (deliverable) · `PLAN.md` (this) · `instructions_coverage.md` (spec checklist + handoff) · `Course Project 2026B.pdf` (spec, read-only) · `samples_for_simulation.xlsx` (M2 data) · `example solution.ipynb` (structural + report reference) · `diagrams/` (M1 diagrams + M2 plots).

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
