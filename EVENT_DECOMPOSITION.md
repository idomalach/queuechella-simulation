# EVENT_DECOMPOSITION — Methodology + Queuechella decisions

Working document. Part 1 is the general process for decomposing any event-based simulation problem; Part 2 captures every decision made so far about the Queuechella project so a future session can resume cleanly.

---

# Part 1 — The decomposition process (general)

## The conceptual foundation

The single most useful distinction in event-based simulation is between **state** and **statistics**:

- **State variables** = the minimum information needed to determine what the system does *next*. State is about the **future**.
- **Statistical accumulators** = information carried only so you can report performance measures at the end. Accumulators are about the **past**.

A useful mental test, with a caveat: "if the simulation crashed, what would I need to resume from this exact moment?" — that captures both buckets at once (state + accumulators), because to resume *and* still get correct final statistics you'd need both. For thinking about events specifically, focus on the narrower definition: state = what determines what happens next.

Concrete example from average waiting time:
- While a customer is in the queue, their `arrival_time` is effectively state — you need it to compute their wait when service starts, and the *ordering* of arrivals determines who's next under FIFO.
- Once they leave, their individual `arrival_time` is no longer state. It's been absorbed into a running sum (an accumulator).

In OOP terms (the gym/festival projects' modelling style): on a `Visitor` object, `is_currently_in_class` is state; `total_classes_attended_this_month` is an accumulator. Same object, two different roles.

## The dependency chain

You cannot define state until you know what's in the system. The order matters:

```
Entities & Resources → Events → State variables → Event handlers → Accumulators
       ↑                                                                 ↑
   slide 12 step                                              KPI-driven, comes last
```

If you skip the first step, you end up listing state variables that don't connect to anything physical, and your event logic gets confused.

## The five-step method

### Step 1 — Identify entities, resources, attributes

**Entity** = anything that flows through the system and is the subject of events ("X arrives", "X starts service", "X leaves"). Tag every noun that *moves*.

**Resource** = anything entities compete for and that has finite capacity. Tag every noun with a capacity number.

**Attribute** = a property carried by an individual entity instance. Anything that varies between instances of the same type and affects future behavior is an attribute.

A judgment call worth being explicit about: things that *look like* entities but have no behavior of their own (e.g., a "show" at a stage) are usually cleaner as attributes of a resource. Fewer classes, same expressive power.

### Step 2 — Trace each entity lifecycle end-to-end

Pick one entity, narrate its journey moment by moment. Every time you'd say "and then X starts" or "and then X ends" or "and then X decides", that's a candidate event. If you can't walk an entity through your model in plain English without getting stuck, your event diagram has holes.

Three observations that fall out of doing this:

1. **Event types are determined by resource × phase, not by entity type.** Different entity types often share the same event set. Their differences live in attributes (what they do *when* an event fires), not in which events exist.
2. **Decision events are real events too.** A "lunch decision" or "overnight decision" is an event even though it doesn't fit the arrival → service → departure pattern. They're triggered by time crossing a threshold or by another event firing.
3. **"Fill-to-max" admission and similar policies are sub-routines, not events.** When a service-end frees a spot, the *same* handler should check the queue and admit the next entity. No separate event needed.

### Step 3 — Build the event catalog (split vs. parameterize)

For each candidate event from Step 2, decide whether it's one event or several. The litmus test:

> Split an event into multiple types when it has **independent scheduling sources** or **different downstream consequences**. Parameterize when only the numbers differ.

- **Arrivals from independent streams** → split. Three different distributions, three different windows, three different self-scheduling rules ⇒ three event types.
- **Abandonment with different timeouts per entity type** → one event, parameterized. Same upstream cause, same downstream graph, only the threshold and penalty differ.
- **Overnight-stay decision with different rules per entity type** → one event. Same downstream branches (stay or depart); the rule that picks between them is a per-type method.

### Step 4 — Separate state variables from accumulators

For each piece of information you'd want the system to track, ask: does this determine what happens next, or does it only matter for the final report?

- **State**: queue contents, server-busy flags, current location of each in-system entity, in-flight scheduled events, satisfaction (because it gates the overnight decision), counters that influence future scheduling (BodyArt drawings-since-break).
- **Accumulators**: total revenue, total satisfaction sum, number of abandonments, average waiting time, fraction of unsatisfied visitors.

The diagram doesn't show either of these directly, but the split determines what fields go on your classes and which variables get updated where.

### Step 5 — Specify event handler logic

For each event in the catalog, write down:
1. What state variables it modifies.
2. What new events it schedules (with what delay).
3. What accumulator updates it triggers (as a side effect).

This is the spec for both the event diagram and the implementation.

## Termination patterns

Three ways an event can "end" something. Each looks different on the diagram:

| Pattern | When to use | Diagram representation |
|---|---|---|
| **A — Hard end at predetermined time** | Stop or do one-shot cleanup at a fixed clock time | Init-arrow into the end event, scheduled at sim start |
| **B — Stop source, let system drain** | Stop accepting new entries at time T, but in-progress work continues | No explicit event. The source stops self-scheduling past T (or gating is done on arrows leaving other events) |
| **C — Service-completion ending** | A single service has a fixed/drawn duration | `Start` event schedules its own `End` event at `now + duration`. No init-arrow |

## Two principles worth memorizing

> **Does it cause time to advance, or does it just gate a decision at a moment that's already happening?**
> If time advances → it's an event (a node on the diagram). If it gates an existing moment → it's a guard inside a handler (an `if` in code, or an annotation on an arrow).

> **One node per distinct moment in time, not per outcome.**
> Two effects at the same simulation clock instant belong in the same event handler. Two effects separated by elapsed time belong in two events.

---

# Part 2 — Queuechella decisions made so far

## Setting

- Two-day music festival, 09:00–20:00 each day.
- Every visitor has a satisfaction score: initial = 5, max = 10, min = 0.
- Budget for alternatives evaluation: ₪1,000,000.
- Confidence level for comparing alternatives: 90% overall (α = 0.1), relative precision γ = 0.1.

## Entities (3 types)

| Entity | Arrival distribution | Window | Days | Group movement rule |
|---|---|---|---|---|
| **FriendsGroup** | from xlsx file | 09:00–13:00 | Day 1 only; 0.7 prob stays overnight | Members move as one unit; no one proceeds until all finish current activity |
| **Couple** | Exp(mean 60/hr)* | 10:00–16:00 | Day 1 or 2; stays overnight iff satisfaction > 7 at end of day 1 | Members move as one unit |
| **Single** | Exp(mean 500/day) | 09:00–16:00 | Day 1 OR 2 (one day only); no overnight decision | N/A (1 person) |

*The "mean 60/hr" wording is ambiguous in the spec — flagged below.

Per-entity behavior:
- **FriendsGroup**: 3–6 members (Uniform discrete). Wants to see one show of each type, then visit all stations (shortest-queue priority).
- **Couple**: Alternates show → station → show → station. Does NOT attend DJstage (no electronic music). Equal probability over remaining options.
- **Single**: Goes directly to MerchTent first. Then sees exactly 2 mainstream + 2 indie + 1 electronic shows (shortest-queue priority among required types).

## Resources (11 venues)

| Resource | Capacity | Service mode | Notes |
|---|---|---|---|
| Entry booths | 5 servers | Per-member, parallel | Card scan U(1.5, 3) + security check Exp(mean 2) bundled into one `EndEntry` event per member |
| MainStage | 200 spots | Per-entity | Fill-to-max; 10-min break between shows; 10-farthest early-exit rule (Bernoulli 0.5 verified at check time) |
| SideStage | 100 spots | Per-entity | Fill-to-max; U(20, 30) min show; 5-min break |
| DJstage | 70 spots | Per-entity | Fill-to-max with permanently-open admission (no show concept); duration ~ piecewise PDF; AR sampling required |
| PhotoStation | 3 stations, 1 shared queue | Per-entity | One photo per entity, service ~ piecewise PDF |
| ChargingStation | 150 chargers | Per-member, parallel | Each member's battery on arrival ~ N(40, 15); each member's duration ~ f(t) with α dependent on battery |
| MerchTent | 7 cashiers | Per-member, parallel | Each member's service U(2, 6); per-member item-purchase rolls |
| BodyArt | 2 artists | Per-member, parallel | Three art types (glitter / neon / henna); each artist breaks 15 min after every 10 drawings |
| FoodCourt — Pizza | 1 cashier + prep | Per-member (entity sub-group orders together with family-pizza rule) | Prep U(4, 6); individual ₪40 / family ₪100 (3+ members ordering pizza together get family-pizza math) |
| FoodCourt — Burger | 1 cashier + prep | Per-member (entity sub-group orders together) | Prep U(3, 4); meal ₪100 |
| FoodCourt — Asian | 1 cashier + prep | Per-member (entity sub-group orders together) | Prep U(3, 7); dish + drink ₪65 |

All food court cashiers: service ~ N(5, 1.5) per combined sub-order. Eating duration U(15, 35) per member. Lunch decision in 13:00–15:00 window, 70% probability **per guest**.

## Event-modelling decisions

### Splits and parameterizations

| Event | Decision | Why |
|---|---|---|
| **Arrival** | **SPLIT into 3** (`FriendsGroupArrival`, `CoupleArrival`, `SingleArrival`) | Independent streams, different distributions, different windows, different bootstrap timings. Each handler self-schedules its own next arrival. |
| **AbandonQueue** | **ONE event, parameterized by venue and entity** | Same upstream cause (JoinQueue), same downstream graph; only threshold (15/20/20 min) and penalty (−2/−1.5/−1) differ. Applies at **4 venues only**: PhotoStation, ChargingStation, MerchTent, BodyArt. Does NOT apply at shows, entry, or food court (confirmed by professor). **Cancel condition**: cancelled when the entity's first member starts service. Once first member is in, the entity is committed. |
| **OvernightDecision** | **ONE event, parameterized** | Same downstream branches (stay or depart); per-type method determines which. |
| **BodyArt break** | **ONE new event node — `BreakEnd` only** | `BreakStart` happens at the same instant as `EndService@BodyArt` (when count % 10 == 0), so it's folded into that handler. `BreakEnd` is a separate node because time advances 15 min and new state changes happen there. |
| **MainStage 10-farthest early leave** | **ONE new event node — `EarlyExitCheck`** | Per-entity scheduled at `entry_time + 15` for every entity that enters MainStage. Handler verifies "is this entity still in the 10-farthest set right now?" — if yes, roll Bernoulli(0.5) and leave if positive; if no, no-op. "Farthest 10" = the 10 most-recently-entered entities currently in the show. Name avoids "abandon" since that term is reserved for queue-leaves. **Note:** the Bernoulli(0.5) is **spec-mandated** — the MainStage bullet ends *"…יעזבו את ההופעה 15 דקות לאחר שנכנסו ויפנו למתחם בהסתברות 0.5"*. |

### Termination patterns applied

| Situation | Pattern | Diagram representation |
|---|---|---|
| End of festival (20:00 day 2) | A — Hard end | Init-arrow into `EndOfFestival`; simulation halts. (Alternative: cascade from `EndOfDay1`. Either is defensible; init-arrow is symmetric with `EndOfDay1`.) |
| End of day 1 (20:00 day 1) | A — Hard end (checkpoint) | Init-arrow into `EndOfDay1`; simulation continues to day 2. Handler applies overnight rules per entity. |
| End of show | C — Service-completion | `ShowStart` schedules `ShowEnd` at `now + duration` |
| Lunch window close (15:00) | B — Stop source | No explicit event. The 13:00–15:00 check sits as a guard on the arrow from each `EndService*` to `LunchDecision`. |
| BodyArt break end | C — Service-completion | `EndService@BodyArt` conditionally schedules `BreakEnd` 15 min later when count hits multiple of 10 |
| MainStage early-exit window | C — Service-completion | Every entity entering MainStage gets `EarlyExitCheck` scheduled 15 min later. Handler verifies "still in farthest 10?" before rolling the Bernoulli(0.5). |

### Other modelling decisions

- **A "show" is not its own entity** — it's modelled as state on the Stage resource (current show genre, current show end time). Shows have no behaviour of their own.
- **The three food court restaurants are three separate resources**, not one. Separate queues, separate cashiers, separate prep distributions.
- **A "group member" is not its own entity** — the group is the entity. Member count is an attribute used for capacity arithmetic (a FriendsGroup of 5 occupies 5 spots in a stage). Events that drive movement and queue position fire at the entity level. Events that drive per-member service (e.g., `EndEntry`, `EndService@MerchTent`) fire per-member — see the per-member vs per-entity table below.
- **Satisfaction is per-guest, not per-entity, and member trajectories diverge** — spec uses "אורח" (guest = individual). A FriendsGroup of 5 contributes 5 independent satisfaction values to the population. Implementation: each guest needs their own satisfaction attribute, because some events generate per-member outcomes (see table below).
- **Per-entity vs per-member events** — movement and queue position fire at the entity level; per-member service venues fire `EndService` per member; satisfaction and some purchases happen at the member level:

  | Activity | Per-entity (one shared outcome) | Per-member (independent per guest) |
  |---|---|---|
  | Shows (Main / Side / DJ) | Show attendance, fill-to-max, show duration | Good/bad experience roll |
  | PhotoStation | Whole transaction — one photo, one satisfaction roll, one ₪30 revenue event | — |
  | ChargingStation | Queue position | Battery on arrival, duration, parallel-server occupancy |
  | MerchTent | Queue position | Cashier service time `U(2, 6)`, each of 4 item-purchase rolls (0.8 / 0.4 / 0.9 / 0.3), parallel-cashier occupancy |
  | BodyArt | Queue position (entity waits together as one queue entry) | Art-type choice, service time draw, satisfaction roll, parallel-artist occupancy |
  | FoodCourt | Lunch-decision window guard | Decide-to-eat (70%), restaurant choice, prep time, eating duration, meal-satisfaction roll. Same-entity members at same restaurant order together (one combined cashier transaction with family-pizza math at pizza). |
  | Queue abandonment | Entity leaves together; commit-on-first-member rule | Penalty (−2 / −1.5 / −1) applied to every member |
- **Fill-to-max admission is a sub-routine**, called from `ShowEnd`, `EndService` at venues with queues, `EarlyExitCheck`, and `BreakEnd` — anywhere a spot frees up.
- **Entry is bundled per member** — one `EndEntry` event per member (not per entity), with `service_time = U(1.5, 3) + Exp(2)`. Card scan and security are not separate events. The "auto-entry stations" alternative simply zeros out the `U(1.5, 3)` term in the handler. Entry uses the parallel-service rule across 5 booths.
- **Couple overnight decision uses the average** of the two members' satisfaction. Couple stays overnight iff `(member1.satisfaction + member2.satisfaction) / 2 > 7` at end of day 1.
- **Abandonment commits once first member is in service** — the `AbandonQueue` event is cancelled the moment the entity's first member starts service at the venue. Subsequent members are not subject to the abandonment timer.
- **Parallel service at per-member venues** — when an entity reaches the front of a per-member venue (Entry, BodyArt, ChargingStation, MerchTent), it occupies as many servers as it can immediately get: `slots_occupied = min(remaining_members, free_servers)`. As each member finishes, the next waiting member of the *same entity* takes the freed server. Other entities in the queue cannot advance until all of this entity's members are in-service or done.
- **Entity exits at `max(member_end_times)`** — at any per-member venue, the entity-exit moment is when the slowest member's service ends. Each member's `EndService` is drawn and scheduled independently when they start service. The `EndService` handler that fires last (i.e., the one for which no other members of this entity are still in-service or waiting) closes out the entity's visit and schedules the move to the next activity. All earlier `EndService` firings for that entity are bookkeeping only.
- **FoodCourt is the one exception to "members move together"** — each member independently decides whether to eat (70% prob per guest), independently picks a restaurant (3/8 burger, 1/4 pizza, 3/8 asian), and goes through their own order / prep / eating cycle. Members of the same entity may be at different restaurants simultaneously. **The entity regroups when `max(EndEating)` fires across ALL eating members across ALL restaurants they chose** — the slowest eater gates the entity's next activity.
- **Sub-orders within food court** — members of the same entity who pick the same restaurant order together as one combined cashier transaction (single `EndOrder` event for the sub-group). Each member still has their own prep and eating events. Cashier service time `N(5, 1.5)` is per combined order, not per member.
- **Family pizza rule** — for an entity with `N` members at the pizza restaurant: order `floor(N/3)` family pizzas (₪100 each, feeds 3) + `N mod 3` individual pizzas (₪40 each). Examples: N=3 → 1 family. N=4 → 1 family + 1 individual. N=5 → 1 family + 2 individuals. N=6 → 2 families.
- **Just-in-time sampling** — random samples are drawn at the moment they are needed, not earlier. The MerchTent service time `U(2, 6)` is drawn when a member's service actually starts at a cashier, not when the entity arrives at MerchTent and not when joining the queue. Exception: the inter-arrival for the *next* arrival event is drawn when the current arrival fires (standard self-scheduling). Just-in-time draws keep the random-number stream predictable and CRN-friendly.

### Per-member vs per-entity service across venues

| Venue | Service mode | Implication |
|---|---|---|
| Entry | Per-member, parallel across 5 booths | A FriendsGroup of 5 with 5 booths free starts all members simultaneously |
| MainStage, SideStage, DJstage | Per-entity | Whole entity watches one show, one experience roll per member but one occupancy event |
| PhotoStation | Per-entity | One photo, one shared satisfaction roll |
| ChargingStation | Per-member, parallel across 150 chargers | Each member's battery and duration drawn independently |
| MerchTent | Per-member, parallel across 7 cashiers | Each member's service time `U(2, 6)` drawn independently; per-member item-purchase rolls |
| BodyArt | Per-member, parallel across 2 artists | Each member's art type and duration drawn independently |
| FoodCourt | Per-member; members may split across restaurants | Each eating member independently picks restaurant; within a restaurant, same-entity members order together (one cashier transaction with the family/individual pizza split); each member has own prep and eating; entity regroups at `max(EndEating)` across all restaurants |

## Full event catalog (23 nodes)

Built by passing every candidate event from the lifecycle traces through the time-advance test and the split-vs-parameterize test. **Update (2026-05-29):** `EndOfStay` promoted from a folded departure to a dedicated event node (Group E, #23) — user-confirmed. It is the per-entity departure event that logs each member's final satisfaction into the KPI accumulator and removes the entity from the festival. Catalog count 22 → 23.

### Group A — Bootstrap (init-arrow) events — 7 nodes

| # | Event | Why it needs an init-arrow |
|---|---|---|
| 1 | `FriendsGroupArrival` | First arrival of the FriendsGroup stream. Self-schedules thereafter. |
| 2 | `CoupleArrival` | First Couple arrival. Self-schedules thereafter. |
| 3 | `SingleArrival` | First Single arrival. Self-schedules thereafter. |
| 4 | `ShowStart@MainStage` | First show at 09:00 day 1. Subsequent shows scheduled by previous `ShowEnd@MainStage` + 10-min break. |
| 5 | `ShowStart@SideStage` | First show at 09:00 day 1. Same self-scheduling pattern, 5-min break. |
| 6 | `EndOfDay1` | Clock-fixed at 20:00 day 1. Not triggered by any other event. |
| 7 | `EndOfFestival` | Clock-fixed at 20:00 day 2. Init-arrow (alternative: cascade from `EndOfDay1`). |

Note on multi-day streams: Couple and Single arrive both days. Cleanest handler logic — when self-scheduling, if the next inter-arrival would push past today's window AND the stream has tomorrow-arrivals, schedule for tomorrow's window-start + inter-arrival. Keeps one init-arrow per stream.

Note on shows on day 2: same pattern — `ShowEnd` handler checks if next `ShowStart` would fall after 20:00; if so and we're on day 1, schedule for 09:00 day 2.

### Group B — Service-completion events — 11 nodes

| # | Event | Parameters carried | Scheduled by |
|---|---|---|---|
| 8 | `EndEntry` | which booth, which member, which entity | Fires **per member**. Arrival event (no-wait) OR previous `EndEntry`/queue-dispatch freeing a booth. Handler: free booth, admit next waiting member of same entity if any; else if all members of this entity done, exit entity from venue. |
| 9 | `ShowEnd@MainStage` | (the show) | Fires **per show, per entity** (all entities in the show exit at the same instant; handler is one fire per show). Scheduled by `ShowStart@MainStage` at `now + duration`. |
| 10 | `ShowEnd@SideStage` | (the show) | Fires **per show**. Scheduled by `ShowStart@SideStage` at `now + U(20, 30)`. |
| 11 | `EndAtDJstage` | which entity | Fires **per entity**. Scheduled when entity enters DJstage with duration drawn via AR from the piecewise PDF. |
| 12 | `EndService@PhotoStation` | which entity, which booth | Fires **per entity** (one photo per entity). Event that brought entity here (no-wait) OR previous `EndService@PhotoStation` (with-wait). |
| 13 | `EndService@ChargingStation` | which member, which entity, which charger | Fires **per member** (parallel service rule). Same dispatch logic as `EndEntry`. |
| 14 | `EndService@MerchTent` | which member, which entity, which cashier | Fires **per member** (parallel service across 7 cashiers). Service time `U(2, 6)` drawn at member's service start. Same dispatch logic as `EndEntry`. |
| 15 | `EndService@BodyArt` | which member, which entity, which artist, art type chosen | Fires **per member** (parallel service across 2 artists). Same dispatch logic as `EndEntry`. Additionally: on every fire, increment that artist's drawing count; if `count % 10 == 0`, schedule `BreakEnd@BodyArt` 15 min later. |
| 16 | `EndOrder@FoodCourt` | which member, which entity, which restaurant | Fires **per member**. When member reaches cashier. Handler schedules `EndPrep` at `now + prep_time_for_chosen_dish`. |
| 17 | `EndPrep@FoodCourt` | which member, which entity, which restaurant | Fires **per member**, scheduled by `EndOrder@FoodCourt`. Handler schedules `EndEating` at `now + U(15, 35)`. |
| 18 | `EndEating@FoodCourt` | which member, which entity, which restaurant | Fires **per member**, scheduled by `EndPrep`. Handler: roll meal-satisfaction (0.4 unsatisfied → −0.6 for this member). Check if all eating members of this entity are done; if yes, entity regroups and proceeds to next activity. |

Food court is three events (Order/Prep/Eating), each parameterized by which restaurant — three separate resources, identical event structure.

### Group C — Parameterized cross-resource event — 1 node

| # | Event | Parameters carried | Where it can be triggered |
|---|---|---|---|
| 19 | `AbandonQueue` | which venue, which entity | Scheduled at every `JoinQueue@<venue>` for `now + entity.abandon_threshold`. Cancelled when the entity's **first member** starts service at this venue. Applies at **4 venues only**: PhotoStation, ChargingStation, MerchTent, BodyArt. Not at shows, entry, or food court. |

### Group D — Time-advance special events — 3 nodes

| # | Event | Scheduled by | What it does |
|---|---|---|---|
| 20 | `EarlyExitCheck` | Scheduled for every entity entering MainStage, at `entry_time + 15` | Verify: is this entity still in the 10-farthest set right now? If yes → Bernoulli(0.5); if positive, entity leaves, spots freed (= member count), fill-to-max admission runs. If no → no-op (entity stays). |
| 21 | `BreakEnd@BodyArt` | `EndService@BodyArt` when artist's drawing count hits a multiple of 10 | Artist becomes available. Dispatch next-in-queue. |
| 22 | `Day2Resume` | `EndOfDay1` for each overnight stayer | At 09:00 day 2: put entity back in their activity-selection loop. |

### Group E — Departure event — 1 node

| # | Event | Parameters carried | Scheduled by |
|---|---|---|---|
| 23 | `EndOfStay` | which entity | Scheduled (usually at `now`) by whatever ends the entity's visit: itinerary exhausted (FG/Single), `overnight_decision == "leave"` at the moment its current activity completes, or `EndOfFestival` for day-2 stragglers. Handler: log each member's final `satisfaction` into `kpi.final_satisfactions`; mark entity `departed`; free any resources it still holds. **Promoted to a node (was folded as "Departure") so final-satisfaction logging lives in exactly one place — user-confirmed 2026-05-29.** |

## What is NOT a separate event node (and why)

Knowing what to leave out is half the catalog discipline. Almost every "thing that happens" in the spec is not a separate node — it's an effect inside another handler.

| Action | Why it's not a node | Where its logic lives |
|---|---|---|
| `JoinQueue@<venue>` | Happens at the same instant as the upstream event (previous `EndService` or Arrival). No time advance. | Folded into the upstream event handler. |
| `StartService@<venue>` | Happens either at JoinQueue moment (no wait) or at the previous `EndService` moment (wait). Always co-located in time with another event. | Folded into whichever event triggered it. |
| `BreakStart@BodyArt` | Same instant as `EndService@BodyArt` when count hits multiple of 10. No time advance. | Folded into `EndService@BodyArt`. |
| `LunchDecision` | Same instant as the `EndService@<venue>` that triggers the decision-window check. | Guard inside each `EndService` handler: if `13:00 ≤ now ≤ 15:00`, branch on the 70% probability. |
| `OvernightDecision` | Same instant as `EndOfDay1`. | Branch inside `EndOfDay1` handler, applies per-entity-type rule. |
| `Show experience` (good/bad roll) | Same instant as `ShowEnd`. | Branch inside `ShowEnd` handler. |
| `Photo satisfaction roll` | Same instant as `EndService@PhotoStation`. | Branch inside that handler. |
| `BodyArt type selection` | Same instant as service starting (i.e., when `EndService@BodyArt` is being scheduled). | The draw happens when `EndService@BodyArt` is being scheduled. |
| `Food meal satisfaction roll` | Same instant as `EndEating`. | Branch inside that handler. |
| `Departure` | ~~Folded~~ — **promoted to the `EndOfStay` node (#23) as of 2026-05-29** so final-satisfaction logging lives in one place. Still scheduled at `now` by the upstream handler that ends the visit, so no time advances; the node exists for logging clarity, not for time advance. | `EndOfStay` handler (Group E). |
| `LunchWindow opens / closes` | Not events at all — they're just times that handlers check against. | No code change required; the 13:00–15:00 check happens inside `EndService` handlers. |
| `Spot freed → admit next` | Always co-located with the event that freed the spot. | Sub-routine called from each `EndService`, `EarlyExitCheck`, `BreakEnd`. |

## Satisfaction-update rules (from spec)

| Trigger | Δ satisfaction | Applied to |
|---|---|---|
| After show, good experience (prob 0.5) | `+(G−1)/2 + (T−1)/19` where G ∈ {mainstream=3, indie=2, electronic=1}, T = hour show ended | Per-member |
| After show, bad experience (prob 0.5) | −1 | Per-member |
| PhotoStation, satisfied (prob 0.7) | +2 (and buys print ₪30) | Per-entity (one shared roll) |
| PhotoStation, not satisfied and bad outcome (prob 0.5 of remaining 0.3) | −0.5 | Per-entity |
| BodyArt glitter, satisfied (prob 0.7) | +0.8 | Per-member |
| BodyArt neon, satisfied (prob 0.6) | +1.2 | Per-member |
| BodyArt henna, satisfied (prob 0.8) | +0.7 | Per-member |
| Food, unsatisfied with meal (prob 0.4) | −0.6 | Per-member |
| Queue abandonment | −2 / −1.5 / −1 (FriendsGroup / Couple / Single) | Per-member (every member of the abandoning entity) |

## Revenue events

| Source | Amount |
|---|---|
| Entry ticket | ₪500 |
| Add overnight | ₪250 |
| Bundle (entry + overnight) | ₪700 |
| MerchTent: t-shirt (prob 0.8 per member) | ₪100 |
| MerchTent: hat (prob 0.4 per member) | ₪50 |
| MerchTent: flag (prob 0.9 per member) | ₪40 |
| MerchTent: band shirt (prob 0.3 per member) | ₪200 |
| PhotoStation print (prob 0.7 per entity) | ₪30 |
| Food — individual pizza | ₪40 |
| Food — family pizza (per family pizza ordered: `floor(N_pizza_members/3)`) | ₪100 |
| Food — burger meal (per member at burger) | ₪100 |
| Food — asian meal (per member at asian) | ₪65 |

## Resolutions from coherence audit (2026-05-28)

A coherence pass against the project spec (`Course Project 2026B.pdf`) and `PLAN.md` resolved the original 6 open items and surfaced 3 additional conflicts between docs. All resolved decisions are locked here. **Note (2026-05-29):** an earlier note claimed PLAN.md was updated to match in the same session — that update never landed on disk, so PLAN v1 stayed stale. **PLAN 2.0 now incorporates every resolution below** (see PLAN.md § "Reconciliation (v1 → v2)"). This decomp remains the canonical deep reference for the event model.

### Spec-interpretation decisions (locked)

1. **FriendsGroup arrival distribution** — Gamma. M2 distribution-fitting in PLAN evaluated the xlsx sample (`std/mean = 0.87`, `skew = 1.29`, mode away from 0) and rejected Exponential in favor of Gamma (`α̂ ≈ 1.24, β̂ ≈ 1.11`), passing KS at `D = 0.081 < 0.136` and Chi-Square at `p = 0.17`. **Implication for sampling**: Gamma has no closed-form inverse CDF for non-integer shape, so FG arrivals must be sampled via Acceptance-Rejection with an Exponential envelope (mean-matched, `c ≈ 1.13`, acceptance ≈ 89%). This is in addition to the spec-mandated A-R for DJstage.
2. **Couple arrival rate** — 60 arrivals per hour, i.e., `λ = 1 per minute` mean inter-arrival ≈ 1 min. Parallels Single's spec wording `"תוחלת של 500 ביום"` = 500 arrivals per day. Resulting daily scale (~360 couples × 2 = ~720 visitors + 500 singles + ~175 FG × 4.5 = ~790 visitors ≈ 2,000 visitors/day) is appropriately congested vs. stage capacities (200/100/70).
3. **Couple overnight rule** — average of both members' satisfaction > 7 at 20:00 day 1. Matches the spec's singular `"מדד שביעות הרצון"` while honoring that satisfaction lives per-member.
4. **FriendsGroup itinerary order** — strict phasing: Phase 1 = 3 shows (one of each genre: Main, Side, DJ); Phase 2 = 4 stations (Photo, Charging, Merch, BodyArt). Within each phase, pick by shortest queue. Dominant reading of `"לאחר שהות מלאה בכל הופעה יעברו בכלל העמדות"` — the "shortest queue" qualifier in the spec applies to stations specifically.
5. **End-of-day mid-activity handling** — at 20:00 (EndOfDay1 fires), arrival generators stop and **no new entities enter**, but *everything already in the system continues*: entities in service finish, entities in queue stay in queue and will be served, shows in progress play out. The overnight decision is evaluated per entity at 20:00; "leaving" entities exit via `EndOfStay` the moment their current activity finishes (no penalty), "staying" entities continue their itinerary normally. Shows are not scheduled past 20:00 — entities still in show queues when shows stop will simply skip the show and proceed (or exit). At 09:00 day 2, arrival generators restart for Couple and Single (FG only day 1) and shows resume.
6. **Day 2 behavior for overnight stayers** — falls out cleanly from (5): Couples continue alternation (open-ended); FG stayers continue itinerary from where they left off. FGs who completed their itinerary on day 1 have already exited via EndOfStay regardless of `bought_lodging` — the overnight payment is a sunk cost if itinerary completes early. Revenue is locked at arrival.
7. **EndOfFestival** — init-arrow at 20:00 day 2 (locked, was open #6 in the original list). Symmetric with EndOfDay1. Same end-of-day mechanics as (5) apply to day 2 termination, except no overnight decision — all remaining entities log final satisfaction and depart via EndOfStay.

### Doc-conflict resolutions (decomp wins)

8. **PhotoStation = per-entity, not per-member.** Spec uses `"הישות מרוצה"` (the entity is satisfied). One photo per visit, one shared roll for the entity. If satisfied (p=0.7): every member of the entity gets +2 satisfaction; revenue += ₪30 (one print). If unsatisfied (p=0.3) × bad-outcome (p=0.5): every member gets −0.5 satisfaction. PLAN.md previously said "per visitor"; corrected to per-entity in this merge.
9. **Food court = NO abandonment.** Decomp's professor-confirmed reading wins. Abandonment applies at 4 venues only: PhotoStation, ChargingStation, MerchTent, BodyArt. PLAN.md Design Decision #12 previously said yes; corrected in this merge.
10. **22-node event catalog** is canonical. PLAN.md's M1 sketch (~16 bubbles, treating `EndFood` and `EndEntry` as single bubbles) was the original draft; superseded by this decomp's catalog. PLAN.md's M1 was updated to reference this catalog rather than restate it.

### What changes in the model from these resolutions

- **Couple class**: arrival inter-arrival now `Exp(λ = 1/min)`, mean 1 min. Overnight rule uses `mean(member1.satisfaction, member2.satisfaction) > 7`.
- **FriendsGroup class**: `itinerary_remaining` is partitioned by phase. `next_activity()` only considers Phase 2 (stations) once Phase 1 (shows) is exhausted. Shortest-queue selection within phase.
- **PhotoStation handler**: rolls once, applies result to all members. No per-member rolls.
- **AbandonQueue event**: never scheduled when entity joins food-court queue.
- **EndOfDay1 handler**: stops arrival generators (Couple, Single — FG already stopped at 13:00), evaluates overnight decision per entity, tags each entity `overnight_decision = stay | leave`. No entity is forcibly ejected — they continue current activity. Show-scheduling logic in `ShowEnd@Stage` handlers gates next show: if `now > 20:00`, do not schedule next show. Entities exiting their current activity check their `overnight_decision`: if `leave`, schedule `EndOfStay`; if `stay`, proceed with itinerary.
- **Sampler**: must include A-R for Gamma (FG arrivals) in addition to A-R for DJstage piecewise.

## Open items (remaining)

None blocking for Step 4. All 6 original open items + 3 new doc conflicts resolved above.

## Step 4 — State variables vs. accumulators

Walked the 22 service/bootstrap/special events and asked, for each: what does this event read or modify? Aggregated below. (`EndOfStay`, node #23, was promoted later — its I/O is simple: reads each member's `satisfaction`, writes `entity.departed`, accumulates `kpi.final_satisfactions`; see that accumulator's row.)

The split principle: **state** = anything needed to determine what happens next (queue contents, who-is-where, in-flight scheduled events, counters that gate future scheduling). **Accumulators** = anything carried only to compute end-of-run KPIs (sums, lists indexed for later analysis, abandonment counts).

A few items live in both worlds. For example, `member.satisfaction` is **state** because it gates the Couple overnight decision at 20:00; at EndOfStay its final value is *also* logged into the accumulator `kpi.final_satisfactions`. The same value plays both roles at different moments.

### State variables (by scope)

**System-level**

| Variable | Type | Notes |
|---|---|---|
| `clock` | float (minutes since festival start) | Current simulation time. Read by every handler. |
| `day` | int (1 or 2) | Toggled by EndOfDay1 → Day2Resume |
| `fel` | min-heap of events | Future event list |
| `arrival_streams_active[stream]` | dict[str, bool] | Per-stream gate; flipped off at window-end (13:00 for FG; 16:00 for Couple/Single) and at EndOfFestival |
| `shows_scheduling_active[stage]` | dict[str, bool] | Set false at EndOfDay1 to stop next-show scheduling past 20:00; reset at Day2Resume |

**Per entity** (FriendsGroup, Couple, Single)

| Variable | Notes |
|---|---|
| `entity.id` | Unique identifier |
| `entity.type` | "FG", "Couple", "Single" |
| `entity.size` | 3–6 for FG (sampled at arrival), 2 for Couple, 1 for Single |
| `entity.members` | list[Customer] |
| `entity.arrival_time` | float (entry into festival) |
| `entity.bought_lodging` | bool, FG-only, drawn Bernoulli(0.7) at arrival |
| `entity.itinerary_remaining` | set / list. For FG: split by phase (`shows_remaining`, `stations_remaining`). For Single: ordered list. For Couple: phase tracker (`next_step = "show" or "station"`) — itinerary is open-ended. |
| `entity.itinerary_phase` | FG only: "shows" or "stations" |
| `entity.current_activity` | reference to Activity or None |
| `entity.current_position` | "queueing", "in_service", "in_show", "eating", "transit", "departed" |
| `entity.queue_join_time` | float — start of current queue wait |
| `entity.abandon_event` | reference to scheduled `AbandonQueue` for cancellation when first member starts service |
| `entity.overnight_decision` | set at EndOfDay1: "stay" or "leave" |

**Per member** (Customer)

| Variable | Notes |
|---|---|
| `member.id` | Unique within entity |
| `member.satisfaction` | float, gates Couple overnight decision and feeds final-satisfaction KPI |
| `member.in_service_at` | reference to server slot (booth/charger/cashier/artist) or None |
| `member.service_end_time` | float, scheduled `EndService*` event time |
| `member.food_eaten_today` | bool, prevents re-entry to food court (once per day) |
| `member.lunch_decided` | bool, set when the 70%-eat-vs-skip roll has been made for the current decision window |

**Per resource** (general)

| Variable | Notes |
|---|---|
| `resource.queue` | FIFO list of entities; length is the input for FG/Single shortest-queue selection |
| `resource.servers` | list of slots, each with `.busy` and `.member_in_service` |
| `resource.in_service_entities` | set of entities currently being served (used to know when entity exits the venue) |

**Per stage** (special — MainStage, SideStage, DJstage)

| Variable | Notes |
|---|---|
| `stage.attendees` | ordered list of entities by entry-time. MainStage uses `attendees[-10:]` for the EarlyExitCheck "farthest 10" set. |
| `stage.spots_used` | sum of `entity.size` for entities in `attendees` |
| `stage.current_show.genre` | "mainstream" / "indie" / "electronic" — gates show-experience satisfaction formula |
| `stage.current_show.end_time` | float |
| `stage.next_show_event` | scheduled `ShowStart` event reference |

**Per BodyArt artist**

| Variable | Notes |
|---|---|
| `artist.drawings_since_break` | int counter, triggers break when `% 10 == 0` |
| `artist.on_break` | bool |
| `artist.break_end_event` | scheduled `BreakEnd@BodyArt` reference |

**Per food-court restaurant** (3 restaurants)

| Variable | Notes |
|---|---|
| `restaurant.cashier_busy` | bool — single cashier per restaurant |
| `restaurant.order_queue` | FIFO list of sub-orders (one per same-entity-same-restaurant group) |
| `restaurant.prep_in_flight` | set of `EndPrep` events scheduled |
| `restaurant.eating_in_flight` | set of `EndEating` events scheduled (members still eating) |

### Accumulators (KPI-only)

| Accumulator | Type | Updated by |
|---|---|---|
| `kpi.final_satisfactions` | list[float] (per-member values at exit) | `EndOfStay` (logs every member's satisfaction); `EndOfFestival` (logs anyone still in the festival at day 2 close) |
| `kpi.wait_times[venue]` | dict[str, list[float]] (per-entity wait at each abandonable venue) | `StartService` moment inside upstream handler — `wait = now − entity.queue_join_time` |
| `kpi.max_wait[venue]` | dict[str, float] | Same moment as above; `max_wait[venue] = max(max_wait[venue], wait)` |
| `kpi.queue_length_over_time[venue]` | dict[str, list[(t, length)]] | Sampled on queue join and queue leave (StartService + AbandonQueue) at every venue |
| `kpi.revenue_by_source` | dict[str, float] | Multiple sources: ticket (Arrival), lodging (Arrival or EndOfDay1), merch items (EndService@MerchTent), photo print (EndService@PhotoStation), food (EndOrder@FoodCourt) |
| `kpi.total_revenue` | float | Sum of `revenue_by_source.values()` |
| `kpi.abandonments[venue]` | dict[str, int] | `AbandonQueue` |
| `kpi.attendance[venue]` | dict[str, int] (count of entities served) | `StartService` (or one-per-entity at each show ShowEnd) |
| `kpi.day1_snapshot` | frozen copy of all of the above | `EndOfDay1` |

### Event → state/accumulator I/O matrix (compact)

For each event, what does it READ (R), WRITE (W), or APPEND-TO-ACCUMULATOR (A):

| Event | Reads (state) | Writes (state) | Accumulates |
|---|---|---|---|
| `FriendsGroupArrival` | `clock`, `arrival_streams_active[FG]` | entity created (full attr set); `entity.bought_lodging`; entry-queue join | `revenue_by_source[ticket]`, `[lodging]` |
| `CoupleArrival` | `clock`, `arrival_streams_active[Couple]` | entity created (2 members); entry-queue join | `revenue_by_source[ticket]` |
| `SingleArrival` | `clock`, `arrival_streams_active[Single]` | entity created (1 member); entry-queue join | `revenue_by_source[ticket]` |
| `ShowStart@MainStage` | stage queue, capacity, `clock` | `stage.attendees`, `stage.current_show.*`, queue-pop | `attendance[MainStage]`, `queue_length_over_time` |
| `ShowStart@SideStage` | stage queue, capacity | `stage.attendees`, `stage.current_show.*`, queue-pop | same |
| `EndOfDay1` | all entities, `clock` (=20:00 day 1) | `day → 2`, `arrival_streams_active[*]`, `shows_scheduling_active[*]`, `entity.overnight_decision` per entity | `day1_snapshot` (freeze copy) |
| `EndOfFestival` | all entities still in festival | mark sim complete; iterate `EndOfStay` for stragglers | finalize `final_satisfactions` |
| `EndEntry` (per member) | booth busy, entity's remaining members in entry queue | free booth; if entity done with entry, set `entity.current_activity = first_activity`, queue join | `wait_times[Entry]`, queue-length sample |
| `ShowEnd@MainStage` | `stage.attendees`, `stage.current_show.genre`, `clock` | per-member satisfaction roll (`+(G-1)/2 + (T-1)/19` good, `-1` bad); attendees → next activity (or EndOfStay if overnight=leave); `next ShowStart` scheduled if `shows_scheduling_active[Main]` | attendance count |
| `ShowEnd@SideStage` | same as MainStage | same as MainStage (no EarlyExit consideration) | same |
| `EndAtDJstage` (per entity) | `stage.spots_used`, entity itinerary | spots_used -= entity.size; per-member experience roll; entity → next activity; fill-to-max from DJ queue | queue-length sample |
| `EndService@PhotoStation` (per entity) | photo-booth busy, queue | one shared satisfaction roll → ±2 to every member OR −0.5 to every member; entity → next activity; fill-to-max from photo queue | `revenue_by_source[photo_print]`, `wait_times[Photo]` |
| `EndService@ChargingStation` (per member) | charger busy | free charger; if entity still has waiting members, dispatch; if entity done, → next activity | `wait_times[Charging]` |
| `EndService@MerchTent` (per member) | cashier busy | free cashier; 4 per-member item rolls; if entity done, → next activity | 4 × `revenue_by_source[merch_*]`; `wait_times[Merch]` |
| `EndService@BodyArt` (per member) | artist busy, `artist.drawings_since_break` | free artist; per-member satisfaction roll; increment `drawings_since_break`; if `%10==0` schedule `BreakEnd`; if entity done, → next activity | `wait_times[BodyArt]` |
| `EndOrder@FoodCourt` (per member) | restaurant cashier busy | free cashier; schedule `EndPrep` at `now + prep_time` | `revenue_by_source[food_*]` (with family-pizza math at pizza restaurant) |
| `EndPrep@FoodCourt` (per member) | (none beyond entity ref) | schedule `EndEating` at `now + U(15, 35)` | — |
| `EndEating@FoodCourt` (per member) | entity members still eating across all restaurants | per-member meal-satisfaction roll (`p=0.4` → −0.6); if all entity members done eating, entity regroups → next activity | — |
| `AbandonQueue` (parameterized by venue, entity) | entity still in queue at this venue? | remove entity from venue queue; per-member −penalty satisfaction; entity → next activity | `abandonments[venue]` |
| `EarlyExitCheck` (MainStage) | `stage.attendees[-10:]` | if entity in last-10: Bernoulli(0.5) → leave (free `entity.size` spots, fill-to-max); else no-op | — |
| `BreakEnd@BodyArt` | `artist.on_break` | `artist.on_break = False`; fill-to-max dispatch | — |
| `Day2Resume` (per overnight stayer) | entity reference | reset `entity` to next-activity selection if itinerary remaining | — |

The matrix above is the source of truth for what each Event handler will need to access — directly informs Step 5 (handler logic spec) and the eventual class design.

### Validation against KPI choices

PLAN's locked KPIs are: **(a)** average member satisfaction at exit, **(b)** average + max queue wait time across stations, **(c)** festival revenue. All three are covered:

- (a) → `kpi.final_satisfactions` (logged at every `EndOfStay`)
- (b) → `kpi.wait_times` and `kpi.max_wait` (logged at every `StartService` and `AbandonQueue`)
- (c) → `kpi.revenue_by_source` and `kpi.total_revenue` (logged at every revenue-generating event)

No KPI requires state we haven't already enumerated. Step 4 closes cleanly.

## Step 5 (partial) — Handler pseudocode for the 3 diagrammed events

Full Step 5 (pseudocode for all 23 handlers) is partners' work (item 4 of "סדר העבודה"). The 3 handlers below correspond to the M1 deliverable diagrams in `PLAN.md` (D1, D2, D3) — having textual pseudocode alongside the diagrams sharpens the spec, simplifies the eventual Python implementation, and gives the user oral-exam material for these 3 events specifically. Partners can adapt the same template for the other 20.

Conventions used below:
- `now` = current simulation clock (minutes).
- `E` = entity (FriendsGroup / Couple / Single).
- `V` = venue (an Activity subclass instance).
- `kpi.*` = accumulator (only-for-final-report fields).
- Anything not in `kpi.*` is state.
- Sampling helpers (`sample_show_duration_main()`, etc.) live on the `Sampler` class — see M3.

### Handler 1 — QueueAbandonment(E, V)

```
TRIGGER:    Scheduled by the upstream handler that put E into V.queue, at now + E.wait_tolerance_min.
            V ∈ {PhotoStation, ChargingStation, MerchTent, BodyArt} only.
            CANCELLED (removed from FEL) the moment the first member of E starts service at V.
            ⇒ When this handler fires, no member of E is in service at V.

PRECONDITIONS READ:
            V.queue ; E.members ; E.itinerary_remaining ; E.itinerary_phase (FG only)
            queue lengths of E's remaining itinerary venues (for shortest-queue selection)

PROCEDURE:
  1. if E ∉ V.queue:
         return                                   # stale firing — already abandoned via another path

  2. V.queue.remove(E)
     E.current_position ← "transit"
     E.queue_join_time  ← None

  3. for each m in E.members:                     # every member feels the penalty,
         m.satisfaction ← max(0, m.satisfaction − E.wait_penalty)   # clamp at 0 per spec

  4. next ← select_next_activity(E)
     # FG: shortest queue among E.itinerary_remaining WITHIN current phase.
     #     If phase 1 just emptied, promote E.itinerary_phase = "stations" and re-select.
     # Single: next item in fixed order (Merch → 2 Main → 2 Side → 1 DJ; shortest-queue within shows).
     # Couple: uniform random over allowed activities for the next phase step.

  5. if next is None:                             # itinerary exhausted (FG / Single only)
         schedule EndOfStay(E) at now
         return

  6. next.queue.append(E)
     E.current_activity   ← next
     E.current_position   ← "queueing"
     E.queue_join_time    ← now
     if next supports abandonment (next ∈ {Photo, Charging, Merch, BodyArt}):
         E.abandon_event ← schedule AbandonQueue(E, next) at now + E.wait_tolerance_min
     try_admit(next, now)                         # fill-to-max if servers free; may trigger StartService

ACCUMULATOR UPDATES:
            kpi.abandonments[V] += 1
            kpi.queue_length_over_time[V].append((now, len(V.queue)))
            kpi.queue_length_over_time[next].append((now, len(next.queue)))   # if step 6 ran

NOTES / EDGE CASES:
  • Commit-on-first guarantee ⇒ no "members already in service" branch needed. Earlier draft
    of D1 carried that branch; simplified here.
  • Satisfaction clamp: spec says member.satisfaction ∈ [0, 10]. The penalty (−2 / −1.5 / −1)
    can drive a low-satisfaction member below 0 if uncapped; clamp at 0.
  • FG phase promotion: only relevant if the abandoning entity finishes phase 1 by the act
    of abandoning the 3rd show — extremely rare (abandonment doesn't apply at shows). Including
    the check defensively.
```

### Handler 2 — ShowStart@MainStage

```
TRIGGER:    Init-arrow at 09:00 day 1.
            Recursive: scheduled by the previous ShowEnd@MainStage at now + 10 min break,
            CONDITIONAL on shows_scheduling_active[MainStage] AND start would fit before 20:00.

PRECONDITIONS READ:
            MainStage.queue ; MainStage.spots_used ; MainStage.attendees
            shows_scheduling_active[MainStage] ; clock ; day

PROCEDURE:
  1. duration ← sample_show_duration_main()       # Normal(M2-fit) via Box-Muller
     genre    ← "mainstream"

  2. # Fill-to-max scan from queue head→tail. NOT FIFO-strict — small entities can
     # overtake a too-large head if remaining capacity won't fit the head.
     admitted_now ← [ ]
     i ← 0
     while i < len(MainStage.queue) and MainStage.spots_used < 200:
         E ← MainStage.queue[i]
         remaining ← 200 − MainStage.spots_used
         if E.size ≤ remaining:
             MainStage.queue.pop(i)               # do NOT increment i
             MainStage.attendees.append(E)        # ordered by entry → enables farthest-10 logic
             MainStage.spots_used += E.size
             for m in E.members: m.in_show_at ← MainStage
             E.current_activity ← MainStage
             E.current_position ← "in_show"
             wait ← now − E.queue_join_time
             kpi.wait_times[MainStage].append(wait)
             kpi.max_wait[MainStage] ← max(kpi.max_wait[MainStage], wait)
             admitted_now.append(E)
         else:
             i += 1                               # skip and continue scanning

  3. MainStage.current_show ← {genre: "mainstream", start_time: now, end_time: now + duration}

  4. schedule ShowEnd@MainStage at now + duration

  5. for each E in admitted_now:
         E.early_exit_event ← schedule EarlyExitCheck(E) at now + 15

  6. # Recursive scheduling of the NEXT show
     next_start ← now + duration + 10            # 10-min break
     if shows_scheduling_active[MainStage] and next_start < day_end_clock(day):   # day_end = 20:00 of current day
         schedule ShowStart@MainStage at next_start

ACCUMULATOR UPDATES:
            kpi.attendance[MainStage] += sum(E.size for E in admitted_now)
            kpi.wait_times[MainStage], kpi.max_wait[MainStage] (per admitted E above)
            kpi.queue_length_over_time[MainStage].append((now, len(MainStage.queue)))

NOTES / EDGE CASES:
  • Empty queue: ShowEnd is still scheduled (a no-attendance show plays out and the
    cycle continues). Allows fill-to-max admission mid-show via EarlyExit-driven free spots.
  • Mid-show admission: EarlyExitCheck or natural ShowEnd are NOT the only ways spots free.
    If we add a mid-show fill-to-max trigger anywhere, this handler's logic still applies via
    `try_admit(MainStage, now)`; current model assumes only EarlyExitCheck frees mid-show.
  • Last show of day: shows_scheduling_active flips to False at EndOfDay1 → no next ShowStart
    scheduled past 20:00. Entities still in MainStage.queue when shows stop: handled by EndOfDay1
    (see Handler 3 step 2).
  • EarlyExitCheck (separate event, not diagrammed): at fire time, if E ∈ MainStage.attendees[-10:],
    sample Bernoulli(0.5); if true, remove E from attendees, free E.size spots, run try_admit,
    schedule E's next-activity event. Else: no-op (E was pushed off the back by later arrivals).
```

### Handler 3 — EndOfDay1

```
TRIGGER:    Init-arrow scheduled at simulation start, fires at clock = 20:00 of day 1.

PRECONDITIONS READ:
            arrival_streams_active[*] ; shows_scheduling_active[*]
            all entities currently in festival (entities_live)
            for each entity: type, members' satisfaction, bought_lodging, current_position, current_activity

PROCEDURE:
  1. # Stop arrival streams and show scheduling for the remainder of day 1
     arrival_streams_active["Couple"]  ← False
     arrival_streams_active["Single"]  ← False    # ["FG"] already False since 13:00
     shows_scheduling_active["MainStage"] ← False
     shows_scheduling_active["SideStage"] ← False

  2. # Per-entity overnight decision + immediate exit for show-queue stragglers who are leaving
     stayers ← [ ]
     for each E in entities_live:
         if E.type == "FG":
             E.overnight_decision ← "stay" if E.bought_lodging else "leave"
         elif E.type == "Couple":
             avg_sat ← mean(m.satisfaction for m in E.members)
             if avg_sat > 7:
                 E.overnight_decision ← "stay"
                 kpi.revenue_by_source["lodging"] += 250
             else:
                 E.overnight_decision ← "leave"
         elif E.type == "Single":
             E.overnight_decision ← "leave"

         # Show-queue stragglers who are leaving: no shows tomorrow they'll catch — exit now.
         if E.overnight_decision == "leave" \
                and E.current_position == "queueing" \
                and E.current_activity ∈ {MainStage, SideStage}:
             E.current_activity.queue.remove(E)
             # No penalty (this is end-of-day, not abandonment).
             advance_itinerary_or_exit(E, now)
             # helper: if itinerary remaining can still be fulfilled (FG phase 2 stations, Single Merch),
             # route to next; else schedule EndOfStay at now.
             # For Single with remaining shows: route to EndOfStay (their remaining shows are unreachable).

         if E.overnight_decision == "stay":
             stayers.append(E)

  3. # Snapshot KPIs for day-1 vs day-2 comparison
     kpi.day1_snapshot ← freeze_copy(kpi)

  4. # Schedule day-2 bootstrap events
     d2_morning_09 ← clock_at(09:00, day=2)
     d2_morning_10 ← clock_at(10:00, day=2)
     d2_evening_20 ← clock_at(20:00, day=2)

     schedule ArrivalCouple at d2_morning_10 + sample_couple_interval()
     schedule ArrivalSingle at d2_morning_09 + sample_single_interval()
     # Each ArrivalX handler re-enables its own stream when it fires.

     schedule ShowStart@MainStage at d2_morning_09
     schedule ShowStart@SideStage at d2_morning_09
     # Each ShowStart re-enables shows_scheduling_active for its stage.

  5. # Wake-up events for stayers: re-evaluates their next activity if they were stuck in a stale
     # show queue, otherwise no-op.
     for each E in stayers:
         schedule Day2Resume(E) at d2_morning_09

  6. # EndOfFestival init-arrow (if not already on FEL from sim start)
     if EndOfFestival not in scheduled_events:
         schedule EndOfFestival at d2_evening_20

ACCUMULATOR UPDATES:
            kpi.revenue_by_source["lodging"] += 250 × (count of qualifying Couples)
            kpi.day1_snapshot ← freeze_copy(kpi)

NOTES / EDGE CASES:
  • Drain semantics: this handler does NOT eject entities currently in service / in show / in queue
    at non-show venues. They finish their current activity normally. Their natural endpoint
    handler (ShowEnd*, EndService*, EndAtDJstage, EndEating*) reads E.overnight_decision and routes:
      decision "leave"  → schedule EndOfStay(E) at the moment the activity completes
      decision "stay"   → proceed to next-activity selection per itinerary
  • Show-queue stragglers are the one exception (step 2 above) — they have no scheduled show
    to wait for if they're leaving, so they're pulled now.
  • Stay-entity show-queue stragglers: they keep their queue position; Day2Resume re-evaluates
    next activity at 09:00 day 2 (the entity may prefer a now-shorter queue elsewhere — without
    Day2Resume they'd silently rot in the original queue until day 2 shows start).
  • day field is derived from clock (clock < day_length ⇒ day 1, else day 2). Not a separately
    written state variable.
  • Cost of the 250 NIS lodging revenue line: spec doesn't disambiguate whether the 250 is the
    couple total or per-member. Reading "הוספת לינה – 250 ₪" as per-couple (one couple = one lodging),
    matching the FG's "כרטיס כניסה + לינה – 700 ₪" being per-group. Lock as per-couple.
```

### What partners inherit from this template

For the other 20 events, partners should follow the same structure: trigger, preconditions read, numbered procedure with explicit state writes, scheduled events, accumulator updates, edge cases. The Step 4 I/O matrix already enumerates reads/writes/accumulators per event — Step 5 expansion is just filling in the procedure body and the edge cases.

Recommended order for partners doing the other 20: bootstrap events first (the 7 arrivals + ShowStarts + EndOfFestival), then service-completion events (the 11 in Group B), then the 3 special events (EarlyExitCheck, BreakEndBodyArt, Day2Resume). Build the FEL skeleton from bootstrap, get fill-to-max admission working, then the service-completion handlers fall out naturally from the diagrams + I/O matrix.

## Where we are in the 5-step process

- ✅ **Step 1** — Entities, resources, attributes (Batch 1)
- ✅ **Step 2** — Lifecycle traces for all 3 entity types (Batch 2)
- ✅ **Step 3** — Event catalog: 23 nodes (22 from Batch 3 + `EndOfStay` promoted 2026-05-29), full enumeration, split-vs-parameterize and per-member-vs-per-entity decisions all made
- ✅ **Step 4** — State variables aggregated; accumulators enumerated; event → state I/O matrix built (2026-05-28)
- 🟡 **Step 5 (partial)** — Handler pseudocode for the 3 user-diagrammed events (D1 QueueAbandonment, D2 ShowStart@MainStage, D3 EndOfDay1). The other 20 are partners' scope (item 4 of "סדר העבודה") and intentionally not authored here.
- ⏸️ **Then** — Draw the event diagram + 3 treatment diagrams (M1 deliverable in `PLAN.md`).

## How to resume next session

Open this file at Part 1 to re-anchor on the methodology, then Part 2 for the locked-in decisions. The event catalog (23 nodes) is the authoritative reference for what's in the system. The "What is NOT a separate event node" section is the authoritative reference for what to leave out. The Resolutions and State/Accumulator tables are the authoritative reference for design decisions and what each event reads/writes.

**Step 5 next.** For each of the 23 events, write the handler in pseudocode: precondition (what state is checked), state updates (which variables are written), events scheduled (with delays), and accumulator updates. The I/O matrix at the end of Step 4 is the skeleton — Step 5 fleshes it out with the actual control flow. Cross-reference the "Satisfaction-update rules" and "Revenue events" tables for the formulas inside each handler.

After Step 5, draw the diagrams (PLAN.md M1) — pick 3 events for treatment diagrams. The candidates were `QueueAbandonment`, `ShowStart@MainStage`, and `EndOfDay1` in PLAN.md's draft; with the new resolutions these stay viable choices but `EndOfDay1` is now richer (overnight decision per entity + show-scheduling gate), worth checking it still fits the diagram size budget.

## Cross-reference

- Project spec: `פרוייקט/Course Project 2026B.pdf` (alias — open in Finder)
- Sample data: `פרוייקט/samples_for_simulation.xlsx`
- Example notebook: `פרוייקט/example solution.ipynb`
- Full project breakdown by tier: `PROJECT_TIERS.md`
- Course tier files: `LECTURE_TIERS.md`, `PRACTICE_TIERS.md`, `THE_BIG_PICTURE.md`
- Conversation rules for this project: `CLAUDE_RULES.md`
