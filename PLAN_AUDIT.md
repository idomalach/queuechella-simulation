# PLAN.md Red-Team Audit — Queuechella Simulation (Group 20)

**Date:** 2026-05-29 · **Scope:** read-only audit of `PLAN.md` cross-checked against the spec
(`Course Project 2026B.pdf`), `diagrams/build/EVENT_NODE_EDGE_SPEC.md`, `Queuechella_Simulation.ipynb`,
`instructions_coverage.md`, the course labs (תרגול 9/10), and the `example solution.ipynb`.
**No protected files were edited.**

**Verification performed:** the notebook was executed top-to-bottom headlessly (0 errors); M2 fits and
M3 samplers were reproduced from the xlsx and from first principles.

**Findings are sorted into three ownership buckets** (per Ido's request):
- **Category 1 — IN my part** (my deliverables: pre-work diagrams, distribution fitting, sampling,
  OOP classes, PLAN/coverage docs, the notebook skeleton). *I fix these.*
- **Category 2 — partners' part, caused by my decisions/ambiguities** (output-analysis scaffold,
  model decisions, handoff references). *I fix these before handoff.*
- **Category 3 — only partners' part** (their statistics/run-loop execution). *No action from me —
  surface in the handoff.*

Decision-required items have been resolved with Ido and the chosen solution is baked in below
(marked **DECIDED**).

---

## What's solid (read this first)

1. **M2/M3 are correct and reproduce exactly.** Gamma MLE (α̂=1.239321, β̂=1.106439) and Normal MLE
   (μ̂=45.902765, σ̂=8.927433) reproduce to the digit; KS/Chi² pass; the notebook runs clean
   end-to-end. Samplers verified: **DJ A-R acceptance 0.374 ≈ 3/8**, FG Gamma A-R ≈ 88.6%, the Photo
   sampler inverts the *exact* spec PDF, charge-time inverse-CDF and all draws match. Couple rate
   (60/hr ⇒ λ=1/min) resolved correctly.
2. **Spec parameters are overwhelmingly accurate** — capacities, prices, probabilities, windows,
   tolerances/penalties, the score formula, and all 7 alternatives + costs. PLAN got the
   Hebrew-preposition traps right (Asian `U(3,7)`; food-unsatisfied drops *to* 0.1; farthest-10 keeps
   `בהסתברות 0.5` and uses entry+15).
3. **The event decomposition is sound** — the 23-node catalog, the §4/§6 edge contract, and the
   §5↔§6↔§9 model layers are internally consistent and at the right abstraction level.

The findings cluster in **output-analysis methodology** (copied from a mismatched example),
**revenue/rule granularity**, and **documentation drift**.

---

# CATEGORY 1 — Problems IN my part (I fix)

### C1-M5 — `arrival_rate_multiplier` (Advertising alternative) is defined but never consumed by the Sampler
- **Severity:** major · **Category:** gap (latent dead-config) · **Owner:** me (M3 Sampler)
- **Location:** CONFIG `"arrival_rate_multiplier": 1.0` + docstring; the three `Sampler.*_arrival_interval`
  methods.
- **Evidence:** none of `fg_arrival_interval / couple_arrival_interval / single_arrival_interval`
  reference `arrival_rate_multiplier` — its only 2 occurrences in the notebook are the CONFIG key and the
  docstring. Flipping it to 1.2 changes nothing, so the Advertising alternative would silently return a
  baseline result.
- **Fix (non-negotiable):** apply the multiplier inside the three arrival samplers — divide the mean
  inter-arrival by `arrival_rate_multiplier` (rate ↑20% ⇒ interval ↓): e.g.
  `mean = (1/λ) / config["arrival_rate_multiplier"]`. The Sampler is the right home (PLAN convention:
  "Sampler draws all numerics from CONFIG"). Re-run the smoke cell after wiring.

### C1-m2 — PLAN §4's notebook section map is offset from the actual notebook
- **Severity:** minor · **Category:** stale · **Owner:** me (PLAN §4 / skeleton)
- **Location:** PLAN §4 lists *"§12 מחלקת אירועים (Event base) … §14 חימום … §17 השוואת חלופות"*.
- **Evidence:** actual notebook is §12 RNGStreams, §13 Event, §14 Simulation, §15 warmup, §16 KPIs,
  §17 alternatives, §18 Welch, §19 summary, §20 GenAI — a 1–2 section shift.
- **Fix:** re-sync the §4 map to the real headers (and note GenAI is §20, not "19/20").

### C1-m4 — `instructions_coverage.md` claims a project-root `.venv`
- **Severity:** minor · **Category:** contradiction · **Owner:** me (coverage doc)
- **Location:** coverage line 23 *"local `.venv` at project root"*.
- **Evidence:** contradicts PLAN §2 (*"in a venv under `~/venvs/`"*) and the actual
  `~/venvs/Simulation_Project/`. (Also matches the standing rule: venvs never inside the iCloud folder.)
- **Fix:** update the line to `~/venvs/Simulation_Project/`.

### C1-m6 — Single "500/day over a 7-h window" is an undocumented assumption (+ stale CONFIG comment)
- **Severity:** minor · **Category:** unverified / stale · **Owner:** me (M3 sampler / CONFIG / assumptions)
- **Location:** PLAN §5.2 *"Exp, 500/day (windowed over 09:00–16:00 ⇒ λ≈500/420 per min)"*; CONFIG
  comment *"See PLAN.md note: PLAN's denominator (11h) does not match the spec window."*
- **Evidence:** spec line 132 *"תוחלת של 500 ביום"* — packing all 500 into the 7-h window (vs the 11-h
  festival day) is a modeling choice that belongs in the §2 assumptions narrative. The CONFIG comment
  describes an *old* PLAN and is now stale (current PLAN already uses 7 h).
- **Fix:** state the windowing assumption in §2; delete the stale "(11h)" CONFIG comment.

### C1-n1 — Photo sampler labeled "Composition" but is a piecewise inverse-transform  **[DECIDED]**
- **Severity:** nit · **Category:** error (label) · **Owner:** me (M3 Sampler / PLAN M3 table)
- **Location:** `photo_duration` docstring "Composition (§6.3)"; PLAN M3 table "Composition ✅ (Photo)".
- **Evidence:** it draws a single u and inverts the global piecewise CDF — that's inverse-transform (the
  example labels the identical routine `inverse_transform_PD`). Composition is **not** required (spec
  lists methods with *"או"*; only A-R is mandatory, satisfied by DJ).
- **DECIDED fix:** **relabel** to "piecewise inverse-transform" (no code change). Update the docstring,
  the PLAN M3 table, and the coverage line. Method coverage is unaffected.

### C1-n3 — Battery clamp piles mass at the bounds (documented; defense note)
- **Severity:** nit · **Category:** unverified (minor distortion) · **Owner:** me (M3 Sampler, decision #21)
- **Location:** `charging_battery_percent` clamps `N(40,15)` to `[0,99]`.
- **Evidence:** clamping (vs the rejection-truncation used for Normal *durations*) piles ≈0.38% of mass
  at exactly 0 and a negligible tail at 99 — a small distribution distortion. Deliberate and documented.
- **Fix:** none required; keep a one-line defense note explaining clamp-vs-truncate is intentional.

### C1-n4 — Orphan "## 12. RNGStreams" header in the notebook M4 region
- **Severity:** nit · **Category:** stale · **Owner:** me (notebook skeleton)
- **Evidence:** the class was hoisted to before the Sampler; the §12 header now has no code under it.
  PLAN §10 M3 already calls it "leftover scaffolding".
- **Fix:** delete the empty §12 header (and renumber, tied to C1-m2).

### C1-n5 — DJ "70 at every moment" modeled as capacity 70 (defensible interpretation)
- **Severity:** nit · **Category:** unverified · **Owner:** me (model, §5.3)
- **Evidence:** spec line 186 *"כמות האורחים … הינה 70 בכל רגע נתון"* reads as constant occupancy; PLAN
  uses max-capacity 70 + roll-admit (you can't force exactly 70 when fewer are present).
- **Fix:** none; note it as an interpretation in §2 assumptions.

---

# CATEGORY 2 — Partners' part, caused by my decisions/ambiguities (I fix before handoff)

### C2-M1 — Output-analysis scaffold is STEADY-STATE (warmup); Queuechella is TERMINATING
- **Severity:** major · **Category:** error / gap · **Owner:** me (scaffold + PLAN); partners execute (→ C3)
- **Location:** notebook **§15 "## 15. ניתוח חימום"** (`[להשלים: Warmup analysis]`); PLAN §4 *"§14 חימום"*.
- **Evidence:** תרגול 9 defines warmup as a **non-terminating** concept (line 34 *"משך זמן החימום
  (למערכת לא מסתיימת)"*; the Terminating/Non-Terminating table sets warmup **= 0** and run-length by the
  stop condition for terminating systems, with the worked example *"סניף בנק פתוח כל יום 8:00–16:00"* —
  exactly the festival's shape). The `example solution.ipynb` uses 15-day warmup + 120-day run because it
  models a **non-terminating hotel**; that does not transfer. The spec also **requires** *"חישוב מספר
  הרצות"* but the notebook has **no replication-count section** (`replication`/`מספר הרצות` = 0 hits) and
  the method (Bonferroni split, run-count formula) is never stated (`Bonferroni`/`בונפרוני` = 0).
- **Fix before handoff (non-negotiable):** replace the §15 "ניתוח חימום" scaffold with a
  **replication-count** section framed as terminating — N independent replications of the full 2-day run,
  **no warmup deletion**. Add the method skeleton: run-count for relative precision γ=0.1 with a
  Bonferroni-split confidence αᵢ = 0.1 / (#metrics × #comparisons) (תרגול 9 line 106; example cell 27).
  Update PLAN §4 and §5.1/§10 to state the terminating framing explicitly.

### C2-M2 — §18 comparison is "Welch", but my CRN design requires a PAIRED t-test
- **Severity:** major · **Category:** contradiction · **Owner:** me (CRN design + scaffold); partners execute (→ C3)
- **Location:** notebook **§18 "## 18. השוואת חלופות (Welch)"**; my CRN setup (RNGStreams.reseed; PLAN
  §9 #15 "CRN-friendly", §10 M3 "CRN by reseeding only affected streams").
- **Evidence:** תרגול 10 is explicit — line 16 *"בוצע CRN … קיימת תלות בין החלופות"*; line 105
  *"כיוון שיש מתאם … נרצה לבצע מבחן טי מזווג"*; the table (lines 135–138) Welch = *"לא ניתן להשתמש אם בוצע
  CRN"* vs paired-t = *"ניתן להשתמש אם בוצע CRN"*; line 142 *"בעבודה נבצע CRN"*. The notebook mentions only
  `Welch` (3×), never `paired`/`מזווג` (0×). Welch on CRN-paired runs is invalid and discards the
  variance reduction. (The example uses Welch because *its* runs are independent — same example-mismatch
  as C2-M1.)
- **Fix before handoff (non-negotiable):** rename §18 to a **paired t-test / paired-difference CI** on the
  CRN-matched per-replication differences (baseline − alternative). Note in PLAN §9. (Keep Welch only as a
  fallback *if* the team ever drops CRN — which would contradict §9 #15.)

### C2-M3 — Pizza "individual = 1 person": keep current (per-person reading)  **[DECIDED]**
- **Severity:** minor · **Category:** unverified (interpretation) · **Owner:** me (model decision PLAN §5.5/§9 #12)
- **Location:** PLAN §5.5 *"an individual pizza is only ever ordered by a single person … P=1 → 1
  individual pizza (₪40)"* applied to *"every entity — couples and groups alike"*; §9 #12.
- **Tension:** spec line 349 *"יחידים בלבד יזמינו מנה אישית"* uses *"יחידים"*, which elsewhere in the
  spec is the **defined Single visitor type** (*"מבקרים יחידים – Single"*). A literal reading would
  restrict the ₪40 personal portion to Single *entities* only, sending a couple/group's lone pizza-eater
  to a ₪100 family tray.
- **DECIDED (per Ido):** **keep current** — read *"יחידים"* here as *single persons*, so **any** entity's
  P=1 pizza-eater orders a ₪40 personal portion; P≥2 → `ceil(P/3)` family trays. Rationale: the sentence
  governs portion *sizing* (1 serving vs a 3-serving tray), and ordering a 3-person tray for one person is
  wasteful/illogical. **Action:** record this as an explicit §9 judgment call and be ready to defend the
  *"יחידים = lone person"* reading at the defense (a grader may read it as the Single type). No code change.

### C2-M4 — Entry tickets + lodging must be charged PER-PERSON (not per-entity)  **[DECIDED]**
- **Severity:** major · **Category:** error (revenue) · **Owner:** me (revenue model PLAN §5.7/§7.3/§8)
- **Location:** PLAN §5.7 *"Entry ticket ₪500"* (no granularity); §7.3 `*Arrival → revenue[ticket]`
  (once/entity); §8 D3 NOTE *"lodging ₪250 is per-couple … FG's per-group ₪700 bundle"*.
- **Evidence:** prices (₪500/₪250/₪700) are flat in the spec, but entry is processed **per member**
  (§5.3) and merch/food are per-member; billing one ticket per *group* undercounts the dominant revenue
  source ≈ (avg entity size)× and skews every alternative comparison (revenue is a KPI).
- **DECIDED fix (per Ido):** **all entry prices are per-person.** Set:
  - `revenue[ticket] += 500 × entity.size` at arrival;
  - FG that pre-buys lodging → `700 × entity.size` (bundle, per person) instead of the ₪500 ticket;
  - Couple that stays (EndOfDay1) → `revenue[lodging] += 250 × entity.size` (= ₪500 for a couple);
  - **PhotoStation stays per-ENTITY** — one ₪30 print and one satisfaction roll per entity (unchanged;
    do **not** convert photos to per-person).
  - Update §5.7, §7.3, and rewrite the §8 D3 NOTE (drop "per-couple/per-group").

### C2-m3 — PLAN §11 names a CONFIG field that doesn't exist
- **Severity:** minor · **Category:** error (claim-vs-code) · **Owner:** me (PLAN §11 handoff reference)
- **Location:** PLAN §11 *"Mainstream investment | `satisfaction_genre_main=4`"*.
- **Evidence:** the real CONFIG key is **`genre_score_main`** (`satisfaction_genre_main` = 0 hits). A
  partner flipping the documented name would set a no-op key.
- **Fix:** PLAN §11 → `genre_score_main=4`.

### C2-m5 — Spec's "≥2 combinations" and "use most of the ₪1M budget" aren't surfaced
- **Severity:** minor · **Category:** gap · **Owner:** me (PLAN §11 / coverage — partner-facing handoff)
- **Location:** PLAN §11 *"Partners pick combinations ≤ ₪1,000,000"*; §5.1.
- **Evidence:** spec line 384 *"בחרו בלפחות 2 קומבינציות של חלופות"* and line 386 *"המטרה היא להשתמש
  ברובו"* (use most of the budget). PLAN states neither explicitly.
- **Fix:** add to PLAN §11 / coverage: **≥2 alternative combinations**, each using **most** of the ₪1M.

### C2-m7 — FriendsGroups remain subject to the farthest-10 early-exit  **[DECIDED]**
- **Severity:** minor · **Category:** unverified (interpretation) · **Owner:** me (model decision)
- **Location:** PLAN applies `EarlyExitCheck` to every MainStage entity, incl. FGs (§6 #20, §9 #4).
- **Evidence:** spec's farthest-10 rule (line 164) is venue-general; FG's *"שהות מלאה בכל הופעה"* (line
  112) could be read to exempt FGs.
- **DECIDED (per Ido):** **keep current** — the venue rule applies to all entities incl. FG; "full stay"
  describes the FG itinerary order (shows before stations), not an exemption. **Action:** add a one-line
  §9 note recording this interpretation so it's defensible at the defense (no code change).

---

# CATEGORY 3 — Only partners' part (no action from me — surface in handoff)

These are the partner-owned execution sides of the scaffold fixes above. I set them up correctly; the
partners own the statistics and the run-loop. **Flag them in the handoff note:**

- **C3-a (from C2-M1):** partners must run the output analysis as a **terminating** simulation —
  N independent replications of the full 2-day run, **no warmup deletion** — and compute the required
  **replication count** via the relative-precision formula with a **Bonferroni-split** confidence
  αᵢ = 0.1 / (#metrics × #comparisons), per תרגול 9.
- **C3-b (from C2-M2):** partners must compare alternatives to the baseline with a **paired t-test**
  (CRN is on), not Welch.
- **C3-c (from C2-m5):** partners must select **≥2 alternative combinations**, each using **most** of the
  ₪1,000,000 budget, and justify statistically + logically (spec requirement).

*(No standalone defects were found in partner-only code — the run loop / KPI / comparison cells are
stubs, so there is nothing for the partners to fix yet beyond executing the above correctly.)*

---

## Cross-check status (confirmed consistent)

- **Spec ↔ PLAN numbers:** all distributions, probabilities, prices, capacities, windows, tolerances,
  penalties, the score formula, and the 7 alternatives (params + costs) verified correct.
- **PLAN §6 ↔ EVENT_NODE_EDGE_SPEC §4/§6:** consistent (init=7, self=10+1, routing matrix, node-specific
  edges, E1–E5). *Note:* the edge-spec **§8 "PLAN corrections to fold in later" and its "not in PLAN"
  header are now stale* — those decisions are already folded into PLAN §6/§9 (minor cleanup, my doc,
  Category 1 — fold into the M1 diagram session).
- **PLAN ↔ notebook (claim-vs-code):** CONFIG matches PLAN's claimed values
  (`couple_arrival_lambda=1.0`, battery clamp [0,99], single λ=500/420, all alt fields) **except** the
  `genre_score_main` name (C2-m3) and the unwired `arrival_rate_multiplier` (C1-M5). Sampler matches the
  M3 algorithm table; M2 fits reproduce exactly; the notebook executes top-to-bottom with 0 errors.
- **Coverage:** every spec bullet is represented somewhere **except** the replication-count *method* and
  the "≥2 combinations / use most of budget" requirements (C2-M1, C2-m5).

---

## Triage outcome (orchestrator, 2026-05-29)

Every finding cross-checked against the Hebrew spec independently before action. All claim-vs-code findings
verified against the live notebook (headers, CONFIG keys, `arrival_rate_multiplier` usage, `photo_duration`
body). Audit confirmed high-quality and impartial — no additional spec errors found, and "What's solid"
re-verified (couple rate, farthest-10 `בהסתברות 0.5`, photo PDF integrates to 1, bad-show `−1` = `בנקודה`,
Asian `U(3,7)`, food prefs). Dispositions:

**APPLIED to PLAN.md + instructions_coverage.md (this commit):**
- **C1-m2** — PLAN §4 section map re-synced to real notebook headers (§12=RNGStreams orphan, …, §20=GenAI).
- **C1-m4** — coverage venv line `.venv@root` → `~/venvs/Simulation_Project/`.
- **C1-n1** [DECIDED] — Photo relabeled "Composition" → "piecewise inverse-transform" in PLAN M3 table +
  coverage (verified: one `u`, global piecewise CDF; = example's `inverse_transform_PD`). Composition is
  not required (spec "או"; only A-R mandatory, satisfied by DJ) — coverage line updated to say so.
- **C2-m3** — PLAN §11 `satisfaction_genre_main` → `genre_score_main` (verified real CONFIG key).
- **C2-m5** — PLAN §11 + coverage now state ≥2 combinations, using most of the ₪1M.
- **C2-M3** [DECIDED] — pizza `יחידים=lone person` reading recorded as an explicit §9 #12 defense note (no model change).
- **C2-m7** [DECIDED] — FG-not-exempt from farthest-10 recorded as a §9 #4 defense note (no model change).
- **C2-M4** [CONFIRMED w/ user, reverses §9 #8] — entry/lodging revenue now **per-person**: ticket ₪500×size,
  FG bundle ₪700×size, couple lodging ₪250×size; PhotoStation print stays per-entity. Updated §5.7, §7.3,
  §8 D3 (step 2 + NOTE), §9 #8.
- **C2-M1** [CONFIRMED w/ user — terminating] — PLAN §5.1 now states the terminating framing (N independent
  replications of the full 2-day run, no warmup deletion; N for γ=0.1 with Bonferroni-split α=0.1); §4 + §10
  M5 + coverage flag the §15 reframe. *User had not seen תרגול 9; difference explained and confirmed.*
- **C2-M2** [CONFIRMED w/ user — paired-t] — PLAN §9 #15 now states alternatives are compared via a paired
  t-test under CRN (Welch invalid under CRN); §4 + §10 M5 + coverage flag the §18 rename.

**NOTEBOOK FIXES — APPLIED 2026-05-30** (M1 confirmed to write only to `diagrams/`, so the notebook was
free; smoke run passes top-to-bottom, 0 errors): ✅ C1-M5 (`arrival_rate_multiplier` wired into the 3 arrival
samplers), ✅ C1-n1 (photo docstring → piecewise inverse-transform), ✅ C1-m6 (stale "(11h)" CONFIG comment
deleted), ✅ C2-M1 (§15 warmup → replication-count / terminating), ✅ C2-M2 (§18 Welch → paired t-test).
**Still deferred (NOT M1-related):** ⏸ C1-n4 (orphan §12 header — batched into the final renumber pass to
avoid churning §-numbers + PLAN cross-refs mid-development), ⏸ C2-M4 (per-person revenue — lands when the
run-loop code exists), and C1-m6's §2-narrative restatement (when the §2 assumptions section is written).
**Net: every currently-actionable audit item is resolved; the 2 remaining are gated on future work, not M1.**

**NO ACTION (keep as defense notes):** C1-n3 (battery clamp piles ~0.38% mass at 0 — deliberate, documented
in §9 #21), C1-n5 (DJ "70 at every moment" modeled as capacity 70 — defensible interpretation).

**Partner handoff flags (C3-a/b/c):** carried forward — terminating replication-count, paired-t under CRN,
≥2 combinations using most of the budget. Now reflected in PLAN §5.1/§9/§10/§11 and coverage.

**EVENT_NODE_EDGE_SPEC.md §8 stale-header cleanup** (noted in the cross-check) — left for the M1 diagram
session that owns `diagrams/build/`.
