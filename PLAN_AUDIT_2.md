# PLAN_AUDIT_2 — Logic & Consistency Audit (Queuechella, Group 20)

**Auditor role:** logic / internal-contradiction / overlooked-requirement / mis-modeling hunter (fresh eyes).
**Date:** 2026-05-30.
**Sources read end-to-end:** `Course Project 2026B.pdf` (8 pp, Hebrew ground truth) · `PLAN.md` (all 12 §+Appendix A) · `instructions_coverage.md` · `diagrams/build/EVENT_NODE_EDGE_SPEC.md` · notebook CONFIG (cell 4), `Sampler` (cell 33), `RNGStreams` (cell 32), M4 stub cells (41, 60).
**Did NOT read:** `PLAN_AUDIT.md` (by design — fresh eyes).
**Executed:** full notebook via `nbconvert --execute` to a **temp** output dir (`EXIT=0`, runs clean top-to-bottom). The real notebook and all protected files were **not** modified.
**Protected files edited:** none. This report (`PLAN_AUDIT_2.md`) is the only file written. No commit.
**Out of scope (taken as given):** M2 distribution fits and M3 sampler numerics (MLEs, KS/Chi², inverse/Box-Muller/A-R math). Samplers were checked only for **wiring**, not correctness.

Resolution legend: **[clear fix]** orchestrator can apply · **[sign-off]** changes a spec interpretation / locked §9 decision · **[FYI]** defensible judgment call.

---

## Severity summary

| ID | Sev | Category | One-liner |
|---|---|---|---|
| A1-1 | **major** | mis-modeled / claim-vs-code | "Better kitchen" sets `food_unsatisfied_prob=0.1`; spec says decrease **by** 0.1 → **0.3** |
| A2-1 | **major** | internal-contradiction / sequencing | Day-boundary drain double-handles staying entities; day-2 drain has no EndOfStay gate |
| A2-2 | **major** | logical-error / overlooked | Day-2 `*_active` flags set False at EndOfDay1, never reset True → only 1 arrival/show on day 2 |
| A2-3 | **major** | internal-contradiction | §7.3 books ticket **and** FG bundle (₪1200×size); decision #8 says bundle **replaces** ticket (₪700) |
| A1-2 | minor | mis-modeled / sign-off | "full stay" (FG) **and** "(באופן מלא)" (Single) argue against farthest-10 for those types; only FG addressed |
| A1-3 | minor | missed-requirement | Food eligibility keyed to *completing* an in-window activity, not *having* activity in-window |
| A2-4 | minor | internal-contradiction | Decision #4/D2 cite a farthest-10 spec quote not present in the PDF |
| A2-5 | minor | internal-contradiction / sequencing | Day-2 arrival re-seed described in two places → double-seed risk |
| A2-6 | minor | edge-case / sign-off | Day2Resume for an FG with an **unfinished** day-1 itinerary is unspecified (wipe vs continue) |
| A1-4 | minor | mis-modeled / sign-off | Couple overnight uses **mean** satisfaction; spec is singular "מדד שביעות הרצון" |
| A2-7 | nit | edge-case | Show-score `T` must be hour-of-day (9–20), not absolute elapsed hour (breaks on day 2 / drain) |
| A2-8 | nit | edge-case | FEL tie-break at equal clock unspecified → nondeterminism at boundaries / under CRN |
| A2-9 | nit | edge-case | No abandonment at DJ + DJ required for Single/FG → unbounded DJ-queue stalls possible |
| A2-10 | nit | edge-case | Wait-KPI mixes per-member / per-food-unit / per-entity samples (uneven weighting) |
| A1-5 | nit | mis-modeled / sign-off | Pizza "יחידים בלבד" lone-person vs Single-type (already locked #12) |
| A3-2 | nit | claim-vs-code | `lodging_couple` RNG stream likely dead (couple lodging is deterministic) |

---

## AXIS 1 — PLAN vs INSTRUCTIONS

### A1-1 · **MAJOR** · mis-modeled / claim-vs-code-drift · **[clear fix]**
**Location:** CONFIG docstring (cell 4, "Alternatives mapping"), PLAN §11 table, `instructions_coverage.md:166`.
**Evidence (spec p.7, חלופה "צוות מטבחה טוב יותר"):** *"…ההסתברות למנה לא טובה **קטנה ב-0.1** ואחוז המבקרים שיבחרו לאכול **יעלה ל-85%**"* = "the probability of a not-good dish **decreases by 0.1**, and the share of visitors who choose to eat **rises to 85%**."
The base `food_unsatisfied_prob = 0.4`. "קטנה **ב**-0.1" (the preposition **ב** = *by*) ⇒ 0.4 − 0.1 = **0.3**. But CONFIG/PLAN set the alternative to **`food_unsatisfied_prob = 0.1`** — i.e. they read "ב-0.1" as "*to* 0.1." (They got the sibling clause right: "יעלה **ל**-85%", preposition **ל** = *to*, → 0.85.)
**Why it matters:** the alternatives comparison is the project's core deliverable. A bad-dish prob of 0.1 (a 75% reduction) vs the intended 0.3 (a 25% reduction) makes the ₪500K kitchen alternative look dramatically more effective than the spec defines — it will distort every satisfaction/recommendation conclusion that touches food.
**Fix:** alternative value `food_unsatisfied_prob = 0.3` (base − 0.1). Update the CONFIG docstring line, PLAN §11, and coverage line 166. (Consider expressing it as `0.4 - 0.1` in the docstring to make the "by" semantics self-documenting.)

### A1-2 · **MINOR** · mis-modeled · **[sign-off]**
**Location:** PLAN §9 decision #4 (farthest-10 "venue-general, applies to FriendsGroups too"); §5.2.
**Evidence:** Two spec phrases push the *other* way:
- FG (p.2): *"…ולאחר **שהות מלאה בכל הופעה** יעברו בכלל העמדות"* = "after a **full stay in each performance** they move through all stations."
- Single (p.3): *"…לראות 2 הופעות מיינסטרים, 2 הופעות אינדי והופעה אחת אלקטרונית **(באופן מלא)**"* = "see 2 mainstream, 2 indie and one electronic show **(in full)**."
Decision #4 reads FG's "שהות מלאה" as merely "shows-before-stations ordering" and applies the MainStage farthest-10 early-exit to FGs. The **more natural** reading of both phrases is "watches the show to the end" → **exempt** FG (and Single) from the farthest-10 leave. The PLAN argues the FG case but **never addresses the Single "(באופן מלא)"**, which is the same evidence for a second entity type.
**Why it matters:** if FG/Single are exempt, only Couples are subject to farthest-10 — materially changing MainStage occupancy churn and satisfaction. This is a genuine interpretive fork.
**Fix:** decide explicitly (with the team) whether "full stay"/"(באופן מלא)" exempts FG **and** Single from the farthest-10; record the Single clause in decision #4 either way. (PLAN already flags "a grader may probe" — but only for FG.)

### A1-3 · **MINOR** · missed-requirement · **[FYI]**
**Location:** PLAN §5.5 / decision #12 ("eligible the first time it **finishes** a real itinerary activity during 13:00–15:00").
**Evidence (spec p.6):** *"**לכל אורח שתהיה פעילות** בין השעות 13:00-15:00 תהיה הבחירה האם ללכת לרכוש ארוחת צהריים"* = "for every guest **who has activity** between 13:00–15:00 there is the choice whether to buy lunch."
The spec keys eligibility on *having activity* in the window; the PLAN keys it on *completing* an activity in the window. A guest active during 13:00–15:00 but with no *completion* in-window (e.g. parked in a show queue — shows have no abandonment, so it never completes or abandons) is never offered lunch.
**Why it's minor:** practically unreachable — any non-degenerate itinerary completes ≥1 activity inside a 2-hour window (max single activity ≈ a show ~73 min or a 40-min charge). Noting it so the team can defend the "completion-boundary" modeling as the only event-driven place to insert the decision.

### A1-4 · **MINOR** · mis-modeled · **[sign-off]** (already locked #8)
**Location:** PLAN §5.2 / decision #8 / D3 step 2 ("`if mean(m.satisfaction) > 7`").
**Evidence (spec p.3):** *"…ועמד **מדד שביעות הרצון** גבוה מ-7 בסוף היום"* — singular "the satisfaction measure," but a couple has two members each with their own measure. PLAN takes the **mean**; "both > 7" or "either > 7" are equally available readings of a singular noun applied to a 2-person entity. Locked, defensible; flagging that the chosen aggregation is an assumption, not spec-given.

### A1-5 · **NIT** · mis-modeled · **[sign-off]** (already locked #12)
**Location:** decision #12. *"יחידים בלבד יזמינו מנה אישית"* read as *lone person (P=1)* vs *Single entity-type*. Divergence is narrow (only differs for a **single pizza-eater inside a couple/group**: lone-person → ₪40 personal; literal → ₪100 family tray). Already acknowledged; no action beyond keeping the defense note.

---

## AXIS 2 — PLAN INTERNAL CONSISTENCY (the heart of the audit)

### A2-1 · **MAJOR** · internal-contradiction / sequencing · **[needs sign-off then clear fix]**
**Location:** PLAN §8 D3 (step 2 + DRAIN note), §6 "Termination patterns," decision #13, §9 #7.
**The contradiction.** D3 step 2 iterates **all** `entities_live` and `if staying: stayers.append(E)` → each stayer gets a `Day2Resume` (step 5). But the DRAIN note says in-flight activities finish and *"their end handlers read overnight_decision → … **next activity (stay)**."* An entity that is **in a show / in service at 20:00 and staying** is therefore handled **twice**:
1. its post-20:00 `ShowEnd`/`EndService` routes it to a **next activity on day 1 after close** (≈20:30, festival shut), and
2. `Day2Resume` restarts it at 09:00 day 2.

**Concrete scenario.** A lodging FG is inside a MainStage show at 20:00 (show started 19:55, ends 20:41). EndOfDay1 marks it "stay," appends to `stayers`, schedules `Day2Resume@09:00 d2`. At 20:41 `ShowEnd@Main` fires (drain) and — per the DRAIN note — routes it to "next activity (stay)," so it joins a station queue at 20:41 **day 1** and may be served past closing. It is now both queued on day 1 **and** scheduled to restart on day 2.

**Symmetric day-2 gap.** At `EndOfFestival` (20:00 d2) there is **no overnight decision**, so a day-2 entity's drain `ShowEnd@20:30 d2` has **no `overnight_decision="leave"` gate** to stop it — it would route to a *next activity* after the festival ends, instead of `EndOfStay`. Decision #13/C2 asserts "end-handlers route to EndOfStay," but the **mechanism that forces that on day 2 is unspecified** (the day-1 mechanism is `overnight_decision`, which day-2 arrivals never receive).

**Fix (one rule covers both boundaries):** completion handlers must consult the clock/day, not just `overnight_decision`:
- `clock ≥ close` on the **final** day → route to `EndOfStay`.
- `clock ≥ close` on **day 1** → **park** stayers (do **not** route to a next activity; `Day2Resume` is their sole restart) and `EndOfStay` leavers.
Then `stayers`/`Day2Resume` and the in-flight completions stop colliding. Extend `advance_itinerary_or_exit` (or add a sibling guard) to cover the **"still has itinerary but past close"** case — today it only parks the *itinerary-exhausted* FG case.

### A2-2 · **MAJOR** · logical-error / overlooked · **[clear fix]**
**Location:** PLAN §8 D3 steps 1 & 4; §7.1 state (`arrival_streams_active`, `shows_scheduling_active`).
**Evidence.** D3 step 1: *"`arrival_streams_active[Couple,Single] ← False`; … `shows_scheduling_active[Main,Side] ← False`."* D3 step 4 re-seeds `ArrivalCouple@10:00`, `ArrivalSingle@09:00`, `ShowStart@Main/Side@09:00` for day 2 — but **no step resets the two flags back to True.**
**Consequence (concrete).** The day-2 `ArrivalCouple@10:00` fires and creates a couple, but its **self-loop** ("stop self-scheduling at window-end" gates on `arrival_streams_active[Couple]`) sees `False` → schedules no successor ⇒ **exactly one couple all day 2.** Same for Single. For shows, `ShowEnd@Main` schedules the next `ShowStart` only *"IF `shows_scheduling_active` ∧ start<20:00"* (§8 D2 trigger, E1) → `False` ⇒ **one show per stage on day 2.** Day-2 dynamics collapse.
**Fix:** add to D3 step 4 (day-2 bootstrap): `arrival_streams_active[Couple,Single] ← True; shows_scheduling_active[Main,Side] ← True`. (FG stays off — day-1 only, correct.)

### A2-3 · **MAJOR** · internal-contradiction · **[clear fix]**
**Location:** PLAN §7.3 I/O matrix, `*Arrival` row vs §5.7 / decision #8 / D3 NOTE.
**Evidence.** §7.3 `*Arrival` "Accumulates": *"`revenue[ticket]=₪500×size`; `[lodging]=₪700×size` (FG bundle, w.p. 0.7)."* Read literally, a lodging FG books **₪500×size + ₪700×size = ₪1200×size.** But decision #8 says the FG bundle *"(replaces the ₪500 ticket)"* → total should be **₪700×size.** The I/O matrix (what partners code from) contradicts the locked rule.
**Why it matters:** revenue is a KPI. Phantom inflation ≈ ₪500 × size × (0.7 of all FGs) ≈ hundreds of thousands of ₪/day — it will swamp real revenue differences between alternatives.
**Fix:** rewrite the `*Arrival` accumulate cell so the ₪700 bundle **replaces** (not adds to) the ₪500 ticket for lodging FGs; non-lodging FG = ₪500 ticket. (Couples are fine: ₪500 ticket at arrival + ₪250 lodging add-on at EndOfDay1 = ₪750 = spec add-on pricing, correctly additive and distinct from the FG ₪700 combo.)

### A2-4 · **MINOR** · internal-contradiction (claim vs source) · **[sign-off]**
**Location:** PLAN §9 #4 and §8 D2 cite *"…יעזבו את ההופעה 15 דקות **לאחר שנכנסו ויפנו למתחם** בהסתברות 0.5."*
**Evidence:** the PDF (p.3, MainStage) actually reads *"עשרת הישיבות במיקומים הרחוקים ביותר יעזבו את ההופעה 15 דקות **לאחר ההופעה** בהסתברות 0.5"* = "…15 minutes **after the show [start]**…". The quoted "לאחר שנכנסו" (after they **entered**) does **not** appear in the PDF.
**Why it matters:** the PLAN's design — a `+15` timer **per admission from each entrant's entry time**, with a dynamic `attendees[-10:]` — is justified by the "after they entered" wording. The PDF wording ("after the show") more naturally implies a **single show-start+15 checkpoint** over whoever is in the back-10 then; under that reading a walk-in admitted 30 min in would never be checked.
**Fix:** if "לאחר שנכנסו" came from a binding **forum answer** (spec p.1 makes forum answers obligations), cite it in #4 and you're done. If it's a paraphrase, re-derive the `+15` anchor (entry-time vs show-start) and the rolling/walk-in `EarlyExitCheck` arming against the actual wording.

### A2-5 · **MINOR** · internal-contradiction / sequencing · **[clear fix]**
**Location:** PLAN §6 Group-A "Multi-day streams" note vs §8 D3 step 4.
**Evidence.** §6: *"when a Couple/Single inter-arrival would cross today's window-end and tomorrow-arrivals remain, **schedule for tomorrow's window-start**."* D3 step 4 **also** schedules `ArrivalCouple@10:00`/`ArrivalSingle@09:00` for day 2. If both mechanisms are implemented, **two** arrival chains start on day 2 ⇒ ≈2× couples/singles on day 2.
**Fix:** state once that the stream **stops** at window-end (no cross-boundary self-schedule) and **only `EndOfDay1`** re-seeds day 2; delete/clarify the §6 "schedule for tomorrow's window-start" phrasing so it can't be read as a stream self-schedule. (Pairs with A2-2.)

### A2-6 · **MINOR** · edge-case / under-specified · **[sign-off]**
**Location:** §9 #7, §5.2 (FG "restarts a fresh itinerary on day 2"); EVENT_NODE_EDGE_SPEC E4 ("Handler nuance **to confirm**").
**Gap.** #7 specifies the FINISHED case (FG completed day-1 itinerary, bought lodging → restart fresh). For an overnight FG that **did not finish** its day-1 itinerary by 20:00, `Day2Resume` "re-inits" would **wipe the remaining itinerary** and start a fresh full 3-shows-then-4-stations run. Whether an unfinished stayer should **continue** its remaining itinerary or **restart** is unspecified (and EVENT_NODE_EDGE_SPEC E4 itself flags it "confirm with the team"). Also note: a fresh day-2 itinerary means overnight FGs do up to **double** the activity volume — confirm that matches "וימשיכו ליום הבא" (continue to the next day).
**Fix:** decide and document the unfinished-stayer rule (continue vs restart) for both FG and Couple in #7 / E4.

### Axis-2 nits (real but low-impact; mostly partner-implementation traps the PLAN should pin down)

- **A2-7 · NIT · edge-case** — **Show-score `T` (integer end-hour, §5.6/#14)** must be the **hour-of-day (9–20)**, not an absolute/continuous elapsed hour. The divisor 19 is tuned so `T=20 → (T−1)/19 = 1.0`; a continuous clock would give a day-2 show `T≈33` and `(T−1)/19 > 1`. Drain shows ending after 20:00 also give `T≥20` (≥1.0, clamp saves it). Document `T = hour-of-day` and confirm the clock representation (`§7.1 clock`+`day`) supports it. **[clear fix — doc]**
- **A2-8 · NIT · edge-case** — **FEL tie-break unspecified** (§7.1 "fel (min-heap)"). Simultaneous events at one clock value (e.g. a `ShowEnd@Main` and `EndOfDay1` both at 20:00, or two arrivals) need a deterministic secondary key, both for correct boundary semantics (does the ShowEnd route before or after EndOfDay1 sets overnight decisions?) and for CRN reproducibility. Specify a tie-break (e.g. by event-class priority then insertion order). **[clear fix]**
- **A2-9 · NIT · edge-case** — **No abandonment at DJ** (decision #2 treats it as a performance) yet DJ has a finite queue (cap 70, roll-admit) and is a **required** stop for Single (1 electronic) and FG (Phase-1 genre). An entity can wait unboundedly in the DJ queue, released only by the day-end drain — a possible itinerary stall. Defensible under the "performance ⇒ no abandonment" reading; flag so it's a conscious choice, not an oversight. **[FYI]**
- **A2-10 · NIT · edge-case** — **Wait-time KPI mixes granularities** (§7.2): per-member at Entry/Charging/Merch/BodyArt, per-food-unit at Food, per-entity at Main/Side/DJ/Photo. A group of 6 contributes 6 Merch wait samples but 1 show wait sample, so a pooled "average wait across stations" weights member- and entity-level waits unequally. Documented already; confirm the intended aggregation (report per-venue, or weight consistently). **[FYI]**

---

## AXIS 3 — PLAN vs PARTIAL IMPLEMENTATION (logical drift only)

### A3-1 · **MAJOR** — same as **A1-1** (CONFIG `food_unsatisfied_prob=0.1` is the code manifestation). Cross-referenced; one fix resolves both.

### A3-2 · **NIT** · claim-vs-code (dead config) · **[FYI]**
**Location:** `RNGStreams.STREAM_NAMES` (cell 32) defines `lodging_couple`.
The couple overnight decision is a **deterministic** `mean(satisfaction) > 7` test (D3 step 2) — no Bernoulli — so `lodging_couple` is likely never drawn. (`couple_choice`, `itinerary_tiebreak` are legitimately reserved for the stubbed run loop.) Confirm `lodging_couple` is needed; if not, drop it to avoid a misleading "every decision has a stream" impression.

### A3-3 · **INFO** (not a defect)
- M4 classes (`Customer`/`Group`/`Activity`/`QueueServer`/`KPITracker`/`Event`/`Simulation`) are bare `pass` stubs — **expected** partner work. Behavioral CONFIG keys (genre scores, prices, tolerances, penalties, lodging prices) are **not yet consumed** because the run loop is unbuilt — this is **not** dead config.
- **Sampler wiring verified correct:** every public sampler reads the matching CONFIG key(s) and draws from exactly one named stream; **all** Sampler-referenced streams exist in `STREAM_NAMES`; `arrival_rate_multiplier` is divided into all three arrival means (Advertising functional); positive-truncation is applied to exactly the three Normal **durations** (main show, glitter, food register) and **not** to `charging_battery` (clamped [0,99] instead, per #21); DJ uses A-R (mandatory). No sampler is wired to the wrong venue/parameter.
- Notebook executes clean (`nbconvert` EXIT=0).

---

## Cross-check — verified internally consistent (no action)

- **6 of 7 alternative mappings are correct:** security ×1.3 (260/130/91, applied only to the three במות/stages — not stations, matching "מתחמי הבמות"); mainstream band-shirt 0.3→0.8 + `genre_score_main` 3→4; photo 3→4 + artists 2→3; advertising 1.2; auto-entry skip-scan (leaves only security Exp(2)); gifts `initial_satisfaction` 6.5. Only kitchen is wrong (A1-1). All combinations ≤ ₪1M is partner-checked; "use most of budget" captured in §11.
- **Per-entity vs per-member granularity (§5.4) matches the spec's wording at every venue:** Photo per-**entity** (spec "הישות"), Charging/Merch/BodyArt/Entry per-**member** (spec "האורח"/"כל אורח"), shows = per-entity attendance/duration + per-**member** experience roll (spec "כל אורח"/"לאורח הייתה חוויה"), food per-member with entity-level gate/regroup. This is a real strength.
- **Satisfaction triggers are complete and exclusive:** shows (±), Photo (+2 / −0.5), BodyArt (+0.8/+1.2/+0.7, **no** unsatisfied penalty — correct, spec gives none), Food (−0.6), abandonment (−2/−1.5/−1). No missing or invented delta; Photo correctly *does* have a penalty, BodyArt correctly does not; clamp [0,10] everywhere.
- **Revenue sources complete:** ticket, lodging, merch×4, photo print (per-entity, once, only when satisfied), food. Charging/BodyArt/DJ/shows correctly free. Couple ₪750 (₪500+₪250 add-on) vs FG ₪700 (combo) both match spec pricing — only the FG **double-count** in §7.3 (A2-3) is wrong.
- **Arrival interpretations self-consistent & spec-faithful:** Couple 60/hr (`couple_arrival_lambda=1.0`, mean 1 min, ≈360/day over 10:00–16:00); Single 500/day over the 7-h window (λ≈500/420); FG Gamma inter-arrival from data. The couple "count-per-period" reading parallels Single's correctly.
- **Fill-to-max head→tail scan** correctly reproduces the spec's worked example (99 in a 100-cap side stage with only couples/groups left ⇒ stays 99) and skips over-sized heads; shows count **people**, not entities (the important-notes clarification is honored).
- **23-node count reconciles** (7+11+1+3+1); §6 catalog vs EVENT_NODE_EDGE_SPEC §4 edges are consistent (init set of 7, self-loops, `ShowStart↔ShowEnd` mutual, STATIONS box is diagram-only, `EndEntry→Merch` E3, DJ single node E5). No event with no handler/state; no handler reading absent state (modulo the day-2 flag-reset gap A2-2).
- **Abandonment** at exactly the 4 service venues, commit-on-first cancel, per-member penalty, FG/Couple/Single 15/20/20 min — matches the spec note "(לא כולל הופעות)" with DJ/Entry/Food professor-confirmed exclusions.
- **DJ as electronic performance** for the show-satisfaction roll (G=1) is consistent with the score formula listing אלקטרוני=1.
- **Food chain** order (register N(5,1.5) order+payment → parallel-kitchen prep U → eat U(15,35)), pizza consolidation, and 3/8·1/4·3/8 restaurant split are internally consistent and spec-faithful.

*Could not fully verify (run loop unbuilt):* clock-unit handling for `T`/day boundaries (A2-7), FEL tie-break (A2-8), and the day-2 drain routing mechanism (A2-1) — all live in partner code; flagged at the PLAN/pseudocode level where the specification gaps exist.

---

## Triage outcome (orchestrator, 2026-05-30)

Every finding verified against the spec/PLAN before action; two interpretive majors re-checked against the PDF directly.

**APPLIED — non-diagram fixes (commit a9a39e6):**
- A1-1 [confirmed vs PDF p.7 "קטנה ב-0.1" = *by*]: kitchen `food_unsatisfied_prob` 0.1 → **0.3** (CONFIG + §11 + coverage).
- A2-3: §7.3 `*Arrival` — FG ₪700 bundle **replaces** the ₪500 ticket (was ambiguously additive).
- A2-7: §5.6 / #14 — `T` = integer **hour-of-day** (9–20), not elapsed.
- A2-8: §7.1 — deterministic FEL tie-break (time, event-class priority, insertion seq).
- A1-3: §5.5 — note (eligibility keyed to the completion boundary; practically equivalent).

**REJECTED:**
- A2-4: audit claimed spec says "15 min after the show." **PDF p.3 actually reads "…לאחר שנכנסו למתחם…"** (after they **entered the area**). PLAN's per-entry +15 design is correct. Only the PLAN *quote* was inaccurate (had a stray "ויפנו") — fixed in §9 #4 / §6 #20.

**APPLIED — D2/D3 batch per user decisions 2026-05-30 (this commit). D2 + D3 diagrams must be REBUILT from corrected §8:**
- A1-2 [DECIDED: exempt FG only]: `EarlyExitCheck` never armed for FriendsGroups (full-stay). Couples + Singles still subject. Reverses the earlier C2-m7 call. (§9 #4, §6 #20, §8 D2 step 5 + footnote, §5.3, §9 #17.)
- A2-2 [clear bug]: EndOfDay1 re-enables `arrival_streams_active`/`shows_scheduling_active` to True for day 2 (else 1 arrival/show all day). (§8 D3 step 4, §7.3, §9 #13.)
- A2-1 [bug + design]: past-close guard — a staying entity completing an activity after 20:00 **parks** (awaits Day2Resume) instead of being routed to a new day-1 activity; leavers / final-day → EndOfStay. Kills the double-handling. (§8 D3 DRAIN + helper, §9 #7/#13.)
- A2-5 [clear bug]: EndOfDay1 is the **sole** day-2 re-seeder; streams don't self-schedule across the boundary. (§6 multi-day note, §8 D3 step 4.)
- A2-6 [DECIDED: restart fresh, uniform]: Day2Resume re-inits a fresh itinerary for **every** stayer, finished or not. (§8 D3 step 5, §9 #7/#13.)
- A1-4 [DECIDED: keep mean > 7]: couple overnight aggregation unchanged (#8); confirmed as a chosen assumption.

**FYI / no action:**
- A2-9 (no abandonment at DJ — conscious "performance" reading; possible stall noted), A2-10 (wait-KPI mixed granularity — documented in §7.2), A1-5 (pizza lone-person — locked #12).
- A3-2 (RNG stream `lodging_couple` likely dead — couple lodging is deterministic): optional notebook cleanup; **left in place pending confirmation** (harmless; partners may repurpose).

**M1 coordination:** the event diagram and D1 are unaffected by this audit. **D2 (farthest-10 now FG-exempt) and D3 (EndOfDay1 rewritten) must be rebuilt** from the corrected §8.
