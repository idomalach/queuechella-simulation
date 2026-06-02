# Partner Handoff — Queuechella Simulation

**Start here.** The pre-work is done: distribution fitting (§5), sampling algorithms (§6), the OOP class layer (§7–§11), and the Event/Simulation scaffold (§12–§13). **What's left is the event logic and the analysis** — the run loop, the event subclasses, and the §14–§18 sections. This page is the map; the details live in the files it points to.

---

## 1. Notebook map (`Queuechella_Simulation.ipynb`)

| § | Section | State |
|---|---|---|
| 1–4 | Intro, system & assumptions, event diagram + handling, KPIs | ✅ done |
| הכנות | Imports + CONFIG | ✅ done |
| 5 | Distribution fitting (Gamma arrivals, Normal show) | ✅ done |
| 6 | Sampling algorithms + `RNGStreams` + `Sampler` | ✅ done |
| 7–11 | `Customer` / `Group` / `Activity` / `QueueServer` / `KPITracker` | ✅ done (code + decisions) |
| 12 | `Event` (abstract FEL base) | ✅ scaffold — **you add the 23 subclasses** |
| 13 | `Simulation` (clock + FEL + handles) | ✅ scaffold — **you implement `run()`** |
| 14 | Number of runs | ⬜ partner |
| 15 | Current-state KPIs | ⬜ partner |
| 16 | Alternatives review | ⬜ partner |
| 17 | Comparison (paired t-test, CRN) | ⬜ partner |
| 18 | Summary & recommendations | ⬜ partner |
| 19 | GenAI declaration | ✅ ongoing (add a row per AI use) |

---

## 2. Architecture in one picture

```
CONFIG  ── one dict; read every parameter as CONFIG["key"], never hardcode numbers
  │
RNGStreams(master_seed)  ── one independent random stream per source  →  rng["name"]
  │
Sampler(rng, CONFIG)     ── EVERY random draw goes through here (durations, choices, rolls)

model objects (created per run, inside Simulation):
  Customer             one guest: satisfaction (clamped [0,10]) + service state
  Group +subclasses    the moving entity + its itinerary  →  select_next_activity(venues)
  Activity +9 venues   capacity/queue holders             →  make_venues(CONFIG) = registry
  QueueServer          FIFO + per-member dispatch + abandonment
  KPITracker           output accumulators

Event(ABC)   ── FEL entries; ordered by time (FIFO tie-break); subclass + execute(sim)
Simulation   ── owns clock + FEL + all the above; schedule()/pop_next_event() ready; YOU write run()
```

---

## 3. Where to start (build order)

1. **`Event` subclasses (the 23-event catalog).** Each one: `super().__init__(time)`, then `execute(self, sim)` mutates state through the classes above and schedules follow-ups via `sim.schedule(...)`. The catalog + what each does: `EVENT_NODE_EDGE_SPEC.md` §2 and PLAN.md §6/§8.
2. **`Simulation.run()`** (§13). The scaffold is ready — `schedule()`, `pop_next_event()` (pops earliest, advances `self.clock`), and the `rng/sampler/activities/kpi` handles. The loop is roughly: seed the bootstrap events → `while self.fel: ev = self.pop_next_event(); ev.execute(self)` → stop at day/festival end. Routing per entity uses `entity.select_next_activity(self.activities)`.
3. **Analysis §14–§18.** Terminating sim, **no warmup deletion**, N sized for relative precision 0.1 with Bonferroni-split α; alternatives compared with a **paired t-test under CRN** (reseed only the streams an alternative touches — see §4). Requirements: PLAN.md §5.1, §9.

**Tick off `instructions_coverage.md` as you complete each section.**

---

## 4. The interface you call (signatures are in notebook §7–§13)

- **`Simulation`** — `.clock`, `.day`, `.fel`, `.rng`, `.sampler`, `.activities` (venue dict), `.entities`, `.kpi`; `schedule(event)`, `pop_next_event()`. You write `run()`.
- **`Event`** — subclass it; `__init__(self, time)` (call `super().__init__(time)`), implement `execute(self, simulation)`.
- **`Sampler`** — one method per random quantity: `main_show_duration()`, `side_show_duration()`, `dj_stay_duration()`, `fg/couple/single_arrival_interval()`, `friends_group_size()`, `entry_scan/security_duration()`, `photo_duration()`, `charging_battery_percent()`, `charging_time(b)`, `merch_*`, `bodyart_*`, `food_*`, `*_satisfied()`, … (full list in §6).
- **`RNGStreams`** — `rng["name"]` → a `random.Random`; `rng.reseed(names, base_seed)` for CRN.
- **`Group`** — `select_next_activity(venues) → Activity|None` (None ⇒ exit), `decide_overnight()`, `reset_for_day2()`; `.members`, `.size`, `.wait_tolerance`, `.wait_penalty`, `mean_satisfaction()`.
- **`Activity`** (venues) — `queue_length()` (**people waiting**), `free_slots()`, `is_full()`; stages: `can_admit/admit/release`; `MainStage.farthest_entities()` + `early_exit_applies(e)`; `BodyArt.record_drawing/begin_break/end_break`; `FoodCourt.pizza_plan(members)`, `in_window(hour)`; each venue's `.queue` is its `QueueServer`.
- **`QueueServer`** — `join(entity, now)`, `try_dispatch(now)`, `on_service_end(unit, now)`, `abandon(entity, now)`. Each **returns what to schedule** (records, follow-ups) — it never touches the clock; that's your loop's job.
- **`KPITracker`** — `record_wait/queue_length/revenue/abandonment/attendance/departure`, `snapshot_day1()`, `summary()`.

---

## 5. Open decisions to settle (in the run loop)

- **F1** structural picks (couple's show/station, tie-break) use named streams directly — wrap in `Sampler` or keep in `Group`.
- **F2** an abandoned station is dropped, not retried (the itinerary slot is consumed on selection).
- **F3** MainStage farthest-N = `attendees[-N:]` (last N *entities*).
- **F4** `Customer.on_show_end` takes the satisfied roll as a parameter (run loop passes `sampler.show_satisfied()`).
- **F5** FoodCourt registers are lightweight holders, not `QueueServer`s; prep/eating dispatch is run-loop-owned.
- **F6** `FriendsGroup` draws size + lodging in `__init__` if not passed.

---

## 6. Rules the run loop must honor (graders probe these)

Per-member parallel service at Entry/Charging/Merch/BodyArt (a finished member frees its server immediately; the entity advances only when its **last** member finishes); abandonment at exactly the 4 service stations, **commit-on-first** (cancel the timer when the entity's first member starts service); the MainStage farthest-10 applies to **all entities** (on a leave, full-show entities — FG/Single — re-queue the show and don't advance until it's done; Couples move on, so a show counts as completed only on full attendance); satisfaction clamped to [0,10] on every change; shortest-queue measured in **people**; food gate **once per entity per day**. The full reasoning is in the notebook §7–§11 decision write-ups and `DECISIONS_INVENTORY.md` (58 decisions).

---

## 7. References

- **Design** — `PLAN.md` (post-audit source of truth; §-numbers are PLAN's own, not the notebook's).
- **Event catalog + routing matrix** — `EVENT_NODE_EDGE_SPEC.md`.
- **Decisions** — notebook §7–§11 (prose) + `DECISIONS_INVENTORY.md` (full, cited).
- **Class source** — notebook §7–§13 (`Customer` … `Simulation`).
- **Spec** — `Course Project 2026B.pdf`.

*(This file supersedes the former build-session briefs `M4_CLASSES_SESSION_BRIEF.md` and `DECISIONS_INVENTORY_BRIEF.md`, now removed.)*
