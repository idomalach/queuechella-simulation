# Queuechella event diagram v2.0 — node + edge spec & decision log

**Authoritative spec for the v2.0 event diagram AND a partner-handoff reference.** Produced in the
2026-05-29 validation session (Ido). Validated against `Course Project 2026B.pdf` (ground truth)
and PLAN.md §5–§9 + Appendix A.

> ⚠️ **PARTIALLY SUPERSEDED (banner added 2026-05-30).** This file was authored **2026-05-29**, *before*
> the 2026-05-30 audit decisions. **Where it conflicts with PLAN.md, PLAN.md wins.** The deltas are
> folded in as inline `[2026-05-30]` notes below; the load-bearing ones for partners:
> - **A1-2 — FriendsGroups are EXEMPT from `EarlyExitCheck`** (the MainStage farthest-10). The +15
>   timer is armed **only for non-FG** entities (Couple/Single), on **every** admission path (batch /
>   walk-in / rolling). Read every `EarlyExitCheck` mention below as **non-FG**. The original routing
>   matrix §6 `EarlyExitCheck` row has been corrected to drop FG.
> - **A2-6 — overnight stayers (FG *and* Couple) restart a FRESH day-2 itinerary** via `Day2Resume`
>   (finished or not; any day-1 remainder is discarded). The E4 "confirm with the team" question is
>   **RESOLVED: restart at a show, do not exit.**
> - **B2 — routing is centralized in the 2-step drain-aware helper `advance_itinerary_or_exit(E)`**
>   (PLAN §8): Step 1 = next *performable* activity (festival-open ∧ itinerary-remaining), else Step 2 =
>   park (stayer) / `EndOfStay` (leaver / final day). Every completion handler routes through it.

> **Not in PLAN.md, by request** — all session decisions live here. §8 lists the PLAN edits to fold
> in later (only when editing PLAN is approved). The diagram session consumes §5 + §7; the partners
> (handlers/helpers) consume §1 + §3 + §4.

---

## 0. How to use this file

- **§1 — Decision log:** every locked decision, its rationale, and **what it means for the code**
  (the event handlers + helper functions the partners build in M4/the run loop). Read this first.
- **§2 — Node audit:** why all 23 events are correct and complete.
- **§3 — Methodology principles:** the 3 rules that decide "is this a node? an edge? a box?" — use
  them when extending the model.
- **§4 — Final edge spec by source event:** one block per event = that handler's scheduling
  behaviour. This is the per-handler contract for partners.
- **§5 — Drawing structure:** how §4 maps to the drawn diagram (the `STATIONS` box, fan-ins, init/
  self) — for the diagram session.
- **§6 — Per-entity routing matrix:** completeness/defense reference.
- **§7 — Build delta** (`gen_excali_event.py`) · **§8 — PLAN edits to fold in later.**

---

## 1. Master decision log (with code/handler implications)

> ⚠️ **The single most important handoff note:** the `STATIONS` box, the `station↔box` edges, the
> fan-ins and "any-member" abbreviations are **DIAGRAM constructs only**. **There is no "cluster"
> object in code.** Routing is per-entity, computed by `select_next_activity(E)`, which returns a
> *specific* venue. An arrow on the diagram = "this handler *may schedule* that event"; it never
> means an entity flows through a box. Do not build a STATIONS aggregate in the simulation.

| ID | Decision | Why | Implication for partners' handlers/helpers |
|---|---|---|---|
| **N0** | **All 23 nodes confirmed**, none added/removed/merged/re-split. | Passed both Appendix-A tests vs the PDF (see §2). | The 23 `Event` subclasses in PLAN §6 are the final set; names are stable. |
| **C** | **`EndOfFestival` is a 7th INIT (zigzag), NOT scheduled by `EndOfDay1`.** | Fixed-clock terminal event (20:00 d2), symmetric to `EndOfDay1`; no causal dependency on day-1 processing; removes double-schedule risk. | Seed `EndOfFestival` into the FEL at t=0. `EndOfDay1`'s handler must **not** schedule it. |
| **C2** | **`EndOfFestival` DRAINS** (not a hard stop). | Consistency with the day-1 drain; avoids scoring the same mid-activity situation differently on d2 vs d1. | At 20:00 d2 let in-flight events finish (clock runs past 20:00); their end-handlers route to `EndOfStay`. `EndOfFestival`'s handler is a **safety-net sweep**: send to `EndOfStay` only entities with *no pending completion* (idle / stuck in a show queue). Run loop must keep popping the FEL until drained. |
| **D3** | **Mid-show walk-in admission, BOTH stages.** An entity routed to a running show with free capacity enters immediately (doesn't wait for the next `ShowStart`). Shows may also start under-capacity. | Realistic; spec only specified the vacated-spot rule, this generalizes it. | `try_admit_show(E, stage)` helper: if a show is running and `spots_used < cap`, admit now (walk-in); else queue for the next `ShowStart`. **MainStage walk-in must schedule the entrant's `EarlyExitCheck(+15)`** (`[2026-05-30]` non-FG only — A1-2); SideStage walk-in schedules nothing (no farthest-10). Batch admit at `ShowStart` + vacated-spot rolling admit still apply. |
| **D4** | **Eating is never the first festival activity.** No `EndEntry → EndOrder`. | The food detour fires only after a *real* itinerary activity completes in-window; clearing Entry doesn't count. | The food-gate check (`maybe_start_food(E)`) runs at activity-completion handlers (shows/stations/DJ/abandon), **not** at `EndEntry`. Gate `food_done_today` is entity-level, set True on first in-window eligibility. |
| **D5** | **`EndOfStay` is a receive-only member of the `STATIONS` box.** Arrows point only *into* it. | Lets every `X→box` edge fold in `X→EndOfStay`, collapsing the 8-edge exit fan-in to ~2 drawn things. Sound because every router that reaches the cluster can also end a visit (audited, §4). | **Diagram only.** In code `EndOfStay` is an ordinary terminal event; `select_next_activity` returns `None` → schedule `EndOfStay`. The one exception drawn separately is `EndOfFestival → EndOfStay` (node-specific), because `EndOfFestival` never schedules a station. |
| **R1** | **Routing core drawn as a `STATIONS` super-node box** {Photo, Charge, Merch, Body (+`EndOfStay` per D5)}. | Collapses the cluster-internal all-to-all (K₄) and the many-to-many cluster-entry into readable bundles. | None (diagram device). Code routes per-entity. |
| **R2** | **`station↔box` mutual edges abbreviate the K₄; arrow = potential to *schedule*, not flow.** | 4 edges vs 6; makes all-to-all visible; consistent with event-graph semantics. | None (diagram). Reminder: a handler schedules a *specific* `EndService@X`, not "the box." |
| **R3** | **Specific-node-vs-box rule:** bind an edge to the box only when the source/target reaches *any* member; bind to a specific node when only one member is involved. | Prevents false "any-member" claims. | Node-specific edges (the only ones): `EndEntry→EndService@Merch`, `EndService@Merch→EndAtDJstage`, `EndOfFestival→EndOfStay`. Tells partners exactly which transitions are single-target. |
| **R4** | **Honest fan-ins, NO representative edges.** | Edge labels are forbidden by the convention, so a drawn subset would read as a false/complete claim. Every drawn edge is real; completeness lives in §6 + handling diagrams. | Handlers must actually implement every listed transition; none are illustrative. |
| **E1** | **`ShowStart ↔ ShowEnd` mutual — the next `ShowStart` is scheduled by `ShowEnd`** (at `now+break`), not by `ShowStart`. | Break demonstrably begins at show-end; avoids double-specifying the cycle. | In `ShowEnd@*` handler: if `shows_active ∧ start<20:00`, schedule next `ShowStart@same` at `now+break` (10 main / 5 side). `ShowStart` does **not** self-schedule. (PLAN §8 D2 step 6 to be removed — §8.) |
| **E2** | **`EarlyExitCheck → EarlyExitCheck` self-loop (recommended).** | When an early-leaver frees a main spot, rolling admission pulls the queue head *into the show*; per spec it gets its own +15 timer. | In `EarlyExitCheck` handler, after a Bernoulli(0.5) leave frees spots: roll-admit queue head → schedule its `EarlyExitCheck(+15)`. (Same +15 also scheduled by walk-in and by `ShowStart` batch.) **`[2026-05-30]` Every +15 timer is armed for non-FG entrants only — A1-2.** |
| **E3** | **`EndEntry → EndService@Merch`** (fix; v1 had a spurious `EndEntry → EndService@BodyArt`). | No entity's first activity is BodyArt; Single's first stop is Merch. | `EndEntry` (last member) routes Single → Merch. FG/Couple first stop = a show (queue/walk-in). |
| **E4** | **`Day2Resume` is incoming-only** (from `EndOfDay1`); resets `food_done_today` and resumes the stayer at a **concert** (undrawn show-queue join). Does NOT route to stations. | FG/Couple begin a day at a show; Singles never stay. | `Day2Resume(E)` handler: `food_done_today=False`; re-select next activity (a show) and join its queue. **`[2026-05-30]` RESOLVED (A2-6):** an FG that bought lodging **restarts a fresh day-2 itinerary** (at a show) whether or not its day-1 itinerary finished; any day-1 remainder is discarded. This applies to *all* overnight stayers (FG and Couple). (The earlier "confirm with the team" is settled — restart, not exit.) |
| **E5** | **One DJ node:** `EndAtDJstage` (PLAN/spec name) = `EndDJ` (id in `gen_excali_event.py`). | Avoid the two-node confusion. | Single DJ completion event class. |

---

## 2. Node audit verdict — all 23 confirmed (user-approved 2026-05-29)

Two Appendix-A tests: **(1) time-advance** — does it advance the clock vs. gate a decision now?
**(2) split-vs-parameterize** — split on independent scheduling sources or different downstream
graphs; parameterize when only numbers differ.

**Group A — bootstrap (7):** `FriendsGroupArrival`, `CoupleArrival`, `SingleArrival`,
`ShowStart@MainStage`, `ShowStart@SideStage`, `EndOfDay1`, `EndOfFestival`.
- 3 arrivals split — independent RNG streams + distributions + windows, and different downstream
  (FG day-1-only & not re-seeded; Couple both days + overnight; Single one-day).
- Main vs Side `ShowStart`/`ShowEnd` split — independent recurring cycles; Main alone schedules
  `EarlyExitCheck` + rolling admission (different downstream graph). DJ has **no** ShowStart/ShowEnd
  (continuous; roll-admit via `EndAtDJstage`).
- `EndOfDay1`/`EndOfFestival` are fixed-clock time-advance events (pattern A). See C, C2.

**Group B — service-completion (11):** `EndEntry`, `ShowEnd@Main`, `ShowEnd@Side`, `EndAtDJstage`,
`EndService@{Photo,Charging,Merch,BodyArt}`, `EndOrder/EndPrep/EndEating@FoodCourt`.
- 4 station completions split by resource×phase. `EndService@BodyArt` *must* be separate (schedules
  `BreakEnd`); `EndService@Photo` differs in granularity (per-entity, shared roll, ₪30).
- Food = 3 phase nodes parameterized by restaurant (3 moments separated by elapsed time, not 9
  nodes).

**Group C — cross-resource (1):** `AbandonQueue` — 1 node parameterized by venue+entity (not 4).

**Group D — time-advance special (3):** `EarlyExitCheck` (entry+15), `BreakEnd@BodyArt` (15-min
break = elapsed time → its own node), `Day2Resume` (09:00 d2, future instant).

**Group E — departure (1):** `EndOfStay` — usually zero-delay, kept because it is the single
*distinct departure moment* consolidating exit logic shared by ~10 sources; folding it would
duplicate that logic and erase the convergence node.

**No missing nodes** (lunch window = guard off `now`; inter-show breaks = edge delays; JoinQueue /
StartService / OvernightDecision / LunchDecision / fill-to-max / rolls = folded). **No redundant
nodes.**

---

## 3. Methodology principles (the rules partners apply when extending the model)

**P1 — state change ≠ event.** *Every* event changes state, and all state mutations happen inside
handlers — the clock only sits at event times. So "does state change?" is always yes and is not the
test. The test is **time-advance**: does this require the clock to advance to a *new* scheduled
moment on the FEL? Change at the same instant as an already-firing event → folded into that handler
(not a node). Change at a future time something must schedule → a node.
*Worked example:* an entity walking into a running show changes occupancy (`spots_used++`), but at
the *same instant* as the routing event that sent it — so it is folded, like `fill-to-max`,
`JoinQueue`, `StartService`. Promoting every state change to a node would force a node per occupancy
tick — the spaghetti the split exists to prevent.

**P2 — an arrow is the potential to *schedule (create)* an event, never entity flow.** `A → B`
means "when A fires it *may* schedule B (condition in the handler)." It is *not* "an entity moves
from A to B." Consequences used throughout this spec:
- Routing into a **show** creates no event (the entity joins a queue; `ShowEnd` already exists,
  admission waits for `ShowStart`) ⇒ **no edge** — *except* a MainStage walk-in, which creates
  `EarlyExitCheck` ⇒ edge.
- Routing into a **roll-admit/parallel venue** (DJ, stations, food register) *may* create that
  venue's completion event (when a server is free) ⇒ a (conditional) edge.

**P3 — the box is an abbreviation for a *set of events*, not a flow container.** `X → box` = "X may
schedule the completion of *some* member"; `box → Y` = "*some* member may schedule Y." Bind to a
**specific node** instead of the box when only one member is involved (R3). `EndOfStay` is a
receive-only member (D5): arrows only into it.

---

## 4. Final directed-edge spec — by source event (the per-handler contract)

Notation: **[init]** seeded at t=0 · **[self]** schedules its own next instance · **→** schedules
(one-way) · **↔** mutual · **⇢ (undrawn)** entity joins a show queue, no event created (P2) ·
*(node-specific)* binds to a node inside the box, not the box (R3). All conditions are handler-side
(not drawn).

**Bootstrap / arrivals**
1. `FriendsGroupArrival` [init] — **[self]** next FG arrival (stop self-scheduling at 13:00 d1);
   **→ `EndEntry`** (try_admit booths). *Day-1 only; never re-seeded.*
2. `CoupleArrival` [init] — **[self]** next (Exp; window 10:00–16:00); **→ `EndEntry`**.
3. `SingleArrival` [init] — **[self]** next (Exp; window 09:00–16:00); **→ `EndEntry`**.

**Entry**
4. `EndEntry` — **[self]** free booth → admit next same-entity member, else next entity;
   on **last** member route to first activity: **→ `EndService@Merch`** *(node-specific; Single)*;
   **→ `EndAtDJstage`** (FG first-pick = DJ); **→ `EarlyExitCheck`** (Couple first = Main, walk-in,
   D3 — `[2026-05-30]` FG also walks into Main but is **EarlyExit-exempt, A1-2**, so no +15 timer);
   **⇢ Main/Side queue (undrawn)**. *No `→EndOrder` (D4).*

**Show cycles**
5. `ShowStart@MainStage` [init] — **↔ `ShowEnd@MainStage`** (schedules this show's end; the reverse
   schedules the next start after the 10-min break, E1); **→ `EarlyExitCheck`** (batch-admitted +15
   timers).
6. `ShowStart@SideStage` [init] — **↔ `ShowEnd@SideStage`** (5-min break). *No EarlyExit (no
   farthest-10).*
7. `ShowEnd@MainStage` — **↔ `ShowStart@MainStage`** (next show, E1); **→ box** (route to a station;
   `EndOfStay` folded in via the box member, D5); **→ `EndAtDJstage`** (next show = DJ);
   **→ `EarlyExitCheck`** (walk-in to another running main, narrow); **→ `EndOrder`** (in-window food);
   **⇢ Side/other show queue (undrawn)**.
8. `ShowEnd@SideStage` — symmetric to #7 (`↔ ShowStart@SideStage`, → box, → `EndAtDJstage`,
   → `EarlyExitCheck`, → `EndOrder`, ⇢ queue).

**DJ**
9. `EndAtDJstage` (= `EndDJ`) — **[self]** roll-admit freed `size` spots; **→ box** (FG phase 1→2 →
   station; `EndOfStay` folded for Single's last-show case); **→ `EarlyExitCheck`** (walk-in main);
   **→ `EndOrder`** (food); **⇢ Main/Side queue (undrawn)**.

**Stations (the box members)** — all four share: **[self]** roll-admit/parallel dispatch ·
**↔ box** (K₄ all-to-all; `EndOfStay` folded) · **↔ `AbandonQueue`** (entry arms timer / abandon
routes back) · **→ `EndOrder`** (in-window food) · **→ `EarlyExitCheck`** (Couple station→Main
walk-in) · **⇢ show queue (undrawn)** (Couple alternation).
10. `EndService@PhotoStation` — as above (3 servers, shared queue, per-entity).
11. `EndService@ChargingStation` — as above (parallel per-member).
12. `EndService@MerchTent` — as above **plus → `EndAtDJstage`** *(node-specific; Single Merch→DJ)*.
13. `EndService@BodyArt` — as above **plus ↔ `BreakEnd@BodyArt`** (every 10th drawing schedules a
    15-min break; `BreakEnd` dispatches the next member). [self] is suppressed while on break.

**Food chain** (per food-unit; parameterized by restaurant)
14. `EndOrder@FoodCourt` — **[self]** free register → next food-unit in that register's queue;
    **→ `EndPrep`**.
15. `EndPrep@FoodCourt` — **→ `EndEating`** (parallel kitchen → eat `U(15,35)`). *No self.*
16. `EndEating@FoodCourt` — regroup at `max(EndEating)` then route next: **→ box** (resume a station;
    `EndOfStay` folded); **→ `EarlyExitCheck`** (resume Main, walk-in); **→ `EndAtDJstage`** (resume
    DJ); **⇢ show queue (undrawn)**. *No self; no `→EndOrder` (already ate).*

**Abandonment**
17. `AbandonQueue` — **↔ box** (armed when a station queue is joined; on fire routes to another
    station; `EndOfStay` folded); **→ `EndAtDJstage`** (Single abandons Merch → DJ);
    **→ `EndOrder`** (in-window food); **⇢ show queue (undrawn)**. *Commit-on-first: cancelled when
    the entity's first member starts service.*

**MainStage farthest-10** (`[2026-05-30]` armed for **non-FG entrants only** — FriendsGroups are exempt, A1-2)
18. `EarlyExitCheck` — **[self]** (E2, vacated-spot roll-admit → new entrant's +15); on a
    Bernoulli(0.5) leave, route next: **→ box** (station; `EndOfStay` folded); **→ `EndAtDJstage`**;
    **→ `EndOrder`** (food); **⇢ show queue (undrawn)**. **Incoming fan-in** (D3 walk-in + batch +
    rolling): `ShowStart@Main` (batch), [self] (rolling), and `{EndEntry, ShowEnd@Main, ShowEnd@Side,
    EndAtDJstage, EndEating, box, AbandonQueue}` (walk-in, conditional on a main show running
    under-cap). *This is the densest fan-in — see §5 note.*
19. `BreakEnd@BodyArt` — **↔ `EndService@BodyArt`** (artist free → dispatch next member). *No other
    edges.*

**Day boundary & departure**
20. `EndOfDay1` [init] — **→ `CoupleArrival`**, **→ `SingleArrival`** (re-seed day-2 streams),
    **→ `ShowStart@MainStage`**, **→ `ShowStart@SideStage`** (re-seed day-2 cycles),
    **→ `Day2Resume`** (per overnight stayer). ✗ **never** `→EndOfFestival` (C) or
    `→FriendsGroupArrival` (day-1 only).
21. `Day2Resume` — resets `food_done_today`; **⇢ concert/show queue (undrawn)** (E4). *No drawn
    outgoing.*
22. `EndOfFestival` [init] — **→ `EndOfStay`** *(node-specific into the box member; direct, NOT via
    the box — `EndOfFestival` never schedules a station)*. Drain sweep of entities with no pending
    completion (C2).
23. `EndOfStay` — **terminal sink, no outgoing.** Incoming: `box → EndOfStay` (any station ends the
    visit; folds in the exit-intent of every `→box` source per D5) + the direct `EndOfFestival →
    EndOfStay`. Logs `final_satisfactions`, frees held resources, marks departed. **Not** reachable
    from `EndEntry` (every entity has ≥1 activity) or `Day2Resume` (stayers restart at a concert).

---

## 5. Drawing structure (for the diagram session)

Conventions (locked): circles only (+ the one box) · solid = schedule · double-head = mutual ·
zigzag = init · **no edge labels** · black & white.

**INIT (7 zigzag, no source):** the 3 arrivals, `ShowStart@Main`, `ShowStart@Side`, `EndOfDay1`,
`EndOfFestival`.

**SELF (10 + 1):** 3 arrivals, `EndEntry`, `EndAtDJstage`, `EndService@{Photo,Charging,Merch,BodyArt}`,
`EndOrder`, and (recommended, E2) `EarlyExitCheck`. None on `EndPrep`/`EndEating`/`ShowEnd@*`.

**The `STATIONS` box** (relabel from "STATIONS" → e.g. **"Stations (all-to-all, shortest-queue) +
exit"**):
- Members: `EndService@{Photo,Charging,Merch,BodyArt}` drawn mutually to the box (4 `station↔box`
  edges = the K₄ abbreviation, R2) + each station's self-loop; **`EndOfStay` as a 5th receive-only
  member** (single-headed arrows IN only, D5).
- INTO box (any-station): `ShowEnd@Main`, `ShowEnd@Side`, `EndAtDJstage`, `EarlyExitCheck`,
  `EndEating` → box.
- OUT of box (any-station): box → `EndOrder`, box → `EarlyExitCheck`; **box → `EndOfStay`** (internal
  member sink); **box ↔ `AbandonQueue`** (mutual).
- Node-specific (bind to the node, not the box, R3): `EndEntry → EndService@Merch`;
  `EndService@Merch → EndAtDJstage`; `EndOfFestival → EndOfStay`.

**Peripheral single-node fan-ins** (honest, no representatives, R4) — place these at the periphery so
the convergent stars read cleanly:
- **`EndOrder`** (food): from `box, ShowEnd@Main, ShowEnd@Side, EndAtDJstage, EarlyExitCheck,
  AbandonQueue` (in-window; **not** `EndEntry`, D4). Then `EndOrder→EndPrep→EndEating`.
- **`EndAtDJstage`** (DJ): from `EndEntry` (FG first), `ShowEnd@Main`, `ShowEnd@Side`,
  `EarlyExitCheck`, `Merch` (node-specific), `AbandonQueue`, `EndEating`.
- **`EarlyExitCheck`**: see #18 — the densest fan-in. **Layout/clutter note:** if the mock is too
  busy, this walk-in fan-in is the first candidate to relegate to the handling diagram (keep
  `ShowStart@Main→EarlyExit` + the self-loop on the event graph, move the walk-in routers to D2).
- **`EndOfStay`**: box → it (member) + `EndOfFestival` → it (direct). All other exit-intent is folded
  into the `→box` edges (D5).

**Day boundary:** `EndOfDay1 → {CoupleArrival, SingleArrival, ShowStart@Main, ShowStart@Side,
Day2Resume}` (drawn routed for layout). `Day2Resume` has only its incoming edge.

**Negative constraints (must NOT appear):** `EndOfDay1 ✗→ EndOfFestival`; `EndOfDay1 ✗→
FriendsGroupArrival`; no scheduling edge *into* `ShowStart@Main/Side` except init, the mutual `SS↔SE`,
and the day-2 re-seed; `EndEntry ✗→ EndOrder`; `EndEntry ✗→ box` (it's `→Merch` only); `Day2Resume
✗→ stations`; no edge *out of* `EndOfStay`; `EndOfStay` member has no `→box` back-arrow.

---

## 6. Per-entity routing matrix (completeness / defense)

`select_next_activity(E)` over the three itineraries (**F**=FriendsGroup, **C**=Couple, **S**=Single).
Cell = entity types making the move; **(q)** = undrawn show queue-join; **✦** = also gated by
13:00–15:00 (and `food_done_today=False`).

| From ↓ \ To → | Main (q) | Side (q) | DJ | Photo | Charge | Merch | Body | Food ✦ | EndOfStay |
|---|---|---|---|---|---|---|---|---|---|
| `EndEntry` | F,C | F,C | F | — | — | S | — | — | — |
| `ShowEnd@Main` | S | F,C,S | F,S | F,C | F,C | F,C | F,C | F,C,S | C,S |
| `ShowEnd@Side` | F,C,S | S | F,S | F,C | F,C | F,C | F,C | F,C,S | C,S |
| `EndAtDJstage` | F,S | F,S | — | F | F | F | F | F,S | S |
| `EndService@Photo` | C | C | — | — | F | F | F | F,C | F,C |
| `EndService@Charge` | C | C | — | F | — | F | F | F,C | F,C |
| `EndService@Merch` | C,S | C,S | **S** | F | F | — | F | F,C,S | F,C |
| `EndService@Body` | C | C | — | F | F | F | — | F,C | F,C |
| `EndEating@Food` | F,C,S | F,C,S | F,S | F,C | F,C | F,C | F,C | — | F,C |
| `EarlyExitCheck` | S | S | S | C | C | C | C | C,S | rare |
| `AbandonQueue` | C,S | C,S | S | F | F | F | F | F,C,S | F,C,S |
| `Day2Resume` | F,C | F,C | F | — | — | — | — | — | — |

Couples never use DJ; Singles' only station is Merch (done first). Union ≈ all-to-all among the
non-show venues — which is why the box + fan-ins exist. **`[2026-05-30]` The `EarlyExitCheck` row
holds no `F`: FriendsGroups are exempt from the farthest-10 early exit (A1-2), so they never fire it.**

---

## 7. Build delta vs the current v1 (`gen_excali_event.py`)

The v1 build used a 4-edge station ring + representative edges; v2.0 replaces the cluster. Steps:
1. **Node fixes:** delete `("EndEntry","End_Body")`; the `EndEntry` first-activity edges are
   `("EndEntry","End_Merch")` *(node)* and `("EndEntry","EndDJ")`.
2. **Show cycles:** make `SS_Main↔SE_Main` and `SS_Side↔SE_Side` mutual (`BIDIR`), not two one-way
   `SCHED` arrows (E1).
3. **Add** `EarlyExit` self-loop (E2).
4. **`STATIONS` box (the big change):**
   - Add a `rectangle` element around the 4 station centres **and `EndOfStay`** (D5); relabel
     "Stations (all-to-all) + exit".
   - **Delete** the v1 station ring (`BIDIR` Photo↔Charge↔Merch↔Body↔Photo).
   - Draw 4 `station↔STATIONS` mutual edges (K₄ abbreviation) + keep each station self-loop.
   - Draw `EndOfStay` as a receive-only member (single-headed arrows in: `box→EndOfStay` +
     `EndOfFestival→EndOfStay`).
   - Re-bind external routing edges to the **box boundary** (any-station) vs **specific node**
     (`EndEntry→Merch`, `Merch→EndDJ`) per §5.
   - Build mechanics: arrows bind to the box's element id (or the inner node's id for node-specific);
     `to_native_min.py` may need a rectangle container; re-run `event_layout_mock.py` until
     `VIOLATIONS=0`.
5. **Fan-ins:** wire the `EndOrder`, `EndAtDJstage`, `EarlyExitCheck`, `EndOfStay` fan-ins per §5
   (every real edge, no representatives). Place the four sinks at the periphery.
6. **Day boundary:** `EndOfDay1 → {Cpl_Arr, Sgl_Arr, SS_Main, SS_Side, Day2Resume}`; `Day2Resume`
   incoming-only (drop the v1 `Day2Resume→Charging`).

---

## 8. PLAN.md corrections to fold in later (NOT applied this session — per user)

- **§8 D2 step 6:** remove "schedule next `ShowStart`" from the *ShowStart* handler; the next start
  is owned by `ShowEnd@*` at `now+break` (E1).
- **§7/§8:** `EndOfFestival` = **drain** (C2), not the current hard-stop wording.
- **§5.3/§8:** add **mid-show walk-in** (D3) to both stages; MainStage walk-in schedules
  `EarlyExitCheck`; SideStage relaxes "batch admission".
- **§5.5/§8:** record **D4** (eating ≠ first activity).
- **§6/§8:** fold in the node audit, decisions C/C2/D3/D4/D5, the routing matrix, and the edge spec;
  fix `EndEntry→Merch` (E3); `Day2Resume` incoming-only (E4); DJ one-node note (E5).
