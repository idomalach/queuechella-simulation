# Decision Inventory — Queuechella Simulation (Group 20)

**Scope.** Every judgment call we made because the spec (`Course Project 2026B.pdf`) was **silent, ambiguous, or needed an implementation interpretation.** Facts the spec states verbatim (capacities, prices, printed probabilities, named distributions, windows, costs) are **excluded** — they are listed in the boundary note at the end. Deduplicated, one entry per decision, with all citation sites. Doc-vs-doc conflicts are flagged inline and summarised at the end.

Citation keys: `PLAN` = `PLAN.md`; `EDGE` = `EVENT_NODE_EDGE_SPEC.md`; `M4B` = `M4_CLASSES_SESSION_BRIEF.md` (removed; folded into `PARTNER_HANDOFF.md`); `COV` = `instructions_coverage.md`; `NB cell N` = `Queuechella_Simulation.ipynb` cell N; `m4` = `m4_classes.py` (retired; classes now live in notebook §7–§13, the F-flags in `PARTNER_HANDOFF.md`).

---

## Behavioral

**B1. FriendsGroup two-phase itinerary.**
*Spec basis:* ambiguous — *"מעוניינות לראות הופעה אחת מכל סוג... לאחר שהות מלאה בכל הופעה יעברו בכלל העמדות... העדיפות לפי התור הקצר ביותר"* (order of shows-vs-stations not pinned).
*Our choice:* strict two phases — Phase 1 = one show of each genre {Main, Side, DJ}; Phase 2 = all 4 stations {Photo, Charging, Merch, BodyArt}; shortest-queue pick **within the current phase**.
*Found in:* PLAN §5.2 L87, §9 #6 L354; M4B §4 L125; EDGE §6 matrix; m4 `FriendsGroup` L392.
*Alternative reading:* freely interleave shows and stations by one global shortest-queue rule.

**B2. Couple itinerary = forced show↔station alternation, no DJ.**
*Spec basis:* ambiguous — *"זוגות הולכות להופעות ולעמדות... לא אוהבים מוזיקה אלקטרונית... ההסתברות לפעילות הבאה שווה"* (open-ended; "alternation" not stated).
*Our choice:* open-ended alternation show→station→show→…; show step uniform{Main, Side} (never DJ); station step uniform{Photo, Charging, Merch, BodyArt}; runs until EndOfDay1/EndOfStay.
*Found in:* PLAN §5.2 L88, §9 #6; M4B §4 L126; EDGE §6.
*Alternative reading:* each step a free uniform choice over all venues (no forced alternation), still excluding DJ.

**B3. Single itinerary = Merch first, then count-based shortest-queue over 2 Main + 2 Side + 1 DJ.**
*Spec basis:* ambiguous — *"ילכו ישירות לאוהל המרצ'נדייס ולאחר מכן יוכלו לראות 2 הופעות מיינסטרים, 2 אינדי, והופעה 1 אלקטרונית (באופן מלא)"* (order among the 5 shows unspecified).
*Our choice:* Merch fixed first, then pick by shortest-queue among the **remaining required show-counts** (a count dict, not a fixed sequence).
*Found in:* PLAN §5.2 L89, §9 #6; M4B §4 L127; EDGE §6 + R3; m4 flag S3 L48, `Single` L471.
*Alternative reading:* a fixed predetermined show order.

**B4. A FriendsGroup that abandons a station's queue SKIPS that station (no retry).**
*Spec basis:* silent — abandonment says *"ימשיכו לפעילות הבאה"*; doesn't say whether the skipped station is revisited.
*Our choice:* the itinerary slot is consumed on **selection**, so an abandoned activity is dropped and the entity advances to the next remaining one (it is never re-queued).
*Found in:* m4 flag F2 L26-29; EDGE §6 matrix (abandon→next station); PLAN §8 D1 L286-296 (routes via `advance_itinerary_or_exit`).
*Alternative reading:* re-insert the abandoned station later in the itinerary.

**B5. Shortest-queue = queue **length in people**, ties broken deterministically by canonical venue order.**
*Spec basis:* silent — *"העדיפות לפי התור הקצר ביותר"* doesn't define the metric or tie-break.
*Our choice:* compare the number of people waiting (sum of entity sizes, `QueueServer.people_waiting()`); break ties by a fixed canonical venue order (deterministic, so no RNG stream is needed for tie-breaking). **[Updated 2026-06-02: was entity-count; switched to people-count, which better reflects the actual wait — a queue of two 6-person groups is a longer wait than three singles.]**
*Found in:* PLAN §7.1 L248 ("length drives shortest-queue"); m4 flag F1 L21-25 + L332; EDGE §1 (`select_next_activity`).
*Alternative reading:* entity-count (the original implementation); random tie-break; or expected-wait instead of head-count.

**B6. Food court is the sole exception to "move as one unit."**
*Spec basis:* given that *"חבר קבוצה/אחד מבני הזוג לא ימשיך לפעילות הבאה עד שכלל חבריו סיימו"*; **silent** on whether members may split anywhere.
*Our choice:* at the food court only, members split (independent hungry roll + independent restaurant per member) and regroup at `max(EndEating)`; everywhere else the entity moves together.
*Found in:* PLAN §5.2 L90, §5.4 L119, §5.5 L131; M4B §4.
*Alternative reading:* the whole entity goes to one restaurant together (no split).

**B7. The MainStage farthest-10 early exit applies to ALL entities; full-show entities (FriendsGroup, Single) retry the show on a leave, Couples move on.**
*Spec basis:* ambiguous — FG *"שהות מלאה בכל הופעה"* and Single's *"(באופן מלא)"* require a full show, vs the farthest-10 *"עשרת הישויות... יעזבו 15 דקות לאחר שנכנסו בהסתברות 0.5"*.
*Our choice:* every admitted entity gets an `EarlyExitCheck`(+15). On a Bernoulli(0.5) leave, FriendsGroups and Singles have not completed the required full show, so they re-queue it and do not advance their itinerary until the show part is done; Couples (no full-show requirement) proceed to their next activity.
*Found in:* notebook §8 (decision) + §9 `MainStage.early_exit_applies`; PLAN §5.3 / §9; EDGE banner A1-2 + §6 matrix note.
*Rationale (updated 2026-06-02 from the earlier "FG exempt" reading):* exempting the full-show entities would leave MainStage with almost no turnover, gutting the spec's farthest-10 dynamic; retry-to-complete keeps the turnover, honors the full-show requirement, and is robust to whether Single's "fully" means the DJ show or all shows.
*Alternative reading:* exempt the full-show entities entirely (the earlier call — rejected for the turnover problem); or apply the leave with no retry (full-show entities lose the show).

**B8. Couple overnight decision uses the AVERAGE of the two members' satisfaction (> 7).**
*Spec basis:* ambiguous — *"מדד שביעות הרצון גבוה מ-7"* but satisfaction is per-person.
*Our choice:* `mean(member.satisfaction) > 7`.
*Found in:* PLAN §9 #8 L356, §8 D3 L331; Appendix B L515; M4B §4 L126; m4 `Couple.decide_overnight` L462.
*Alternative reading:* at least one member > 7; or both members > 7.

**B9. FriendsGroup overnight is a flat Bernoulli(0.7) drawn AT ARRIVAL.**
*Spec basis:* silent on *when* the stay is decided — *"בסיכוי של 0.7 קבוצות יישארו לישון... וימשיכו ליום הבא"*.
*Our choice:* draw the 0.7 stay at arrival and pre-commit; justified because the FG stay probability is unconditional (independent of day-1 dynamics), unlike the couple's end-of-day gate.
*Found in:* PLAN §9 #8 L356 (timing note), §5.2 L87; M4B §4; m4 `FriendsGroup` L39.
*Alternative reading:* realize the stay decision at end of day 1.

**B10. ALL overnight stayers (FG and Couple) restart a FRESH day-2 itinerary; any unfinished day-1 remainder is discarded.**
*Spec basis:* silent — *"וימשיכו ליום הבא"* doesn't say resume vs restart.
*Our choice:* `Day2Resume` re-inits a fresh itinerary and resumes the stayer at a show; an FG-with-lodging that finishes its day-1 itinerary does **not** exit (A2-6).
*Found in:* PLAN §9 #7 L355, §5.2 E4 L87, §6 L211, §8 D3 L338; EDGE E4 L66 + banner A2-6.
*Alternative reading:* FG exits at itinerary-end even with lodging; or resume the unfinished day-1 itinerary.

**B11. Day-2 arrival rates equal day-1 rates (Couple/Single).**
*Spec basis:* silent on day-2 intensity.
*Our choice:* identical rates on both days.
*Found in:* PLAN §9 #13 L361.
*Alternative reading:* a different day-2 arrival rate.

**B12. Lunch eligibility is keyed on the activity-COMPLETION boundary inside 13:00–15:00 (and eating is never the first activity).**
*Spec basis:* *"לכל אורח שמסיים פעילות בין 13:00-15:00 תהיה הבחירה... 70% יבחרו"* — keyed on finishing an activity in the window; the event-driven insertion point is our reading.
*Our choice:* check the food gate at activity-completion handlers (shows/DJ/stations/abandon), **not** at `EndEntry` (D4). Practically equivalent (any non-degenerate itinerary completes ≥1 activity in the 2-h window).
*Found in:* PLAN §5.5 L129 (A1-3), §9 #12 L360, §9 #18 L366; EDGE D4 L57.
*Alternative reading:* make a guest eligible by merely *being* in the window (e.g. mid-activity spanning it, or just-entered).

**B13. One food stop per ENTITY per day (entity-level gate), no second chance, resets day 2.**
*Spec basis:* ambiguous granularity — *"70% מכלל אורחי הפסטיבל יבחרו לאכול"* (per guest, but the entity moves as a unit elsewhere; "once" vs repeatable unstated).
*Our choice:* an entity-level `food_done_today` gate set the moment the entity first finishes an in-window activity; even members who declined get no second chance; no loop-back; gate resets via `Day2Resume`.
*Found in:* PLAN §5.5 L129, §9 #12 L360; M4B §5 L165.
*Alternative reading:* a per-member gate; or allow multiple food visits within the window.

**B14. Hungry roll (70%) is per MEMBER independently; members may pick different restaurants.**
*Spec basis:* *"70% מכלל אורחי הפסטיבל"* — "guests" (people), but entities otherwise move as a unit.
*Our choice:* each member rolls hungry(0.7) and chooses a restaurant independently (the food split of B6).
*Found in:* PLAN §5.5 L129/L131, §5.4 L119.
*Alternative reading:* a single entity-level lunch decision (whole group eats, one restaurant).

**B15. Pizza consolidation — "יחידים" read as a LONE PERSON, not the Single entity-type.**
*Spec basis:* ambiguous — *"מנה אישית – 40 ₪; מגש משפחתי (לשלושה) – 100 ₪; יחידים בלבד יזמינו מנה אישית"*.
*Our choice:* read *"יחידים"* as a lone pizza-eater (P=1 → one ₪40 personal); for P≥2 in any entity, order `ceil(P/3)` family trays (₪100 each), one queuer + one sample-set per tray.
*Found in:* PLAN §5.5 L139-143, §9 #12 L360, Appendix B L515.
*Conflict:* **CONFIG comment (NB cell 22 L313, "Single only")** and **COV L148-149 ("Singles only order personal pizza")** still encode the rejected reading — they say only the Single *type* orders personal portions.
*Alternative reading:* *"יחידים"* = the Single entity-type → only Single entities order personal; every group orders family trays.

**B16. Farthest-N = the last N ENTITIES to enter (`attendees[-10:]`), anchored at each entrant's entry-time + 15 min.**
*Spec basis:* *"מיקום הישות תלוי בסדר הכניסה... עשרת הישויות במיקומים הרחוקים... יעזבו 15 דקות לאחר שנכנסו למתחם בהסתברות 0.5"* — entry-order = position is given; "after they entered" anchor and the rolling last-10 reading are ours.
*Our choice:* a per-entrant check at entry+15 against `attendees[-10:]`; later arrivals push earlier entrants out of the last-10. (A2-4: the 15-min anchor is "after entering the area," not "after the show" — verified vs PDF p.3.)
*Found in:* PLAN §9 #4 L352, §8 D2 L319-323, §7.1; m4 flag F3 L30-32; Appendix B rejected-finding L513.
*Alternative reading:* the 10 farthest **people** (not entities); or a single check 15 min after show start.

**B17. PhotoStation is PER-ENTITY — one photo, one shared satisfaction roll applied to every member.**
*Spec basis:* *"בהסתברות 0.7 הישות מרוצה... יעלה ב-2... במידה והישות לא מרוצה, בהסתברות 0.5 יירד ב-0.5"* — singular *"הישות"*.
*Our choice:* one roll per visit → satisfied (0.7): +2 to every member (and one ₪30 print, see R3); unsatisfied (0.3)×bad(0.5): −0.5 to every member.
*Found in:* PLAN §9 #10 L358, §5.6 L157-158, §5.4 L115; M4B §5.
*Alternative reading:* an independent photo/roll per member.

**B18. Per-guest meal-satisfaction roll (including family-pizza coverees).**
*Spec basis:* *"בהסתברות 0.4 לקוחות לא יהיו מרוצים... יורד ב-0.6"* — "לקוחות" (customers/people).
*Our choice:* every guest who ate rolls 0.4 → −0.6, including members who shared a family pizza they didn't queue for. (Flagged for defense since granularity is debatable.)
*Found in:* PLAN §5.5 L145, §5.6 L160.
*Alternative reading:* one meal-satisfaction roll per food-unit / per order.

**B19. Couple arrival rate "תוחלת של 60 בשעה" read as 60 couples/hour (count per period).**
*Spec basis:* ambiguous — parallels Single's *"תוחלת של 500 ביום"* (count per period).
*Our choice:* 60 couples/hour ⇒ λ=1/min, mean inter-arrival 1 min (~360/day). (Was a real bug: CONFIG once had `1.0/60.0` ⇒ ~6/day; fixed in M3, verified mean 1.002 min.)
*Found in:* PLAN §5.2 L81-84, §10/M3 L411/L419; CONFIG NB cell 22 L197-199; NB §6 table L843; COV L81-82; M4B §3.
*Alternative reading:* mean 60 minutes between arrivals (i.e. 1/hour ⇒ ~6/day).

**B20. Single arrival rate "500/day" windowed over the 09:00–16:00 (7 h) arrival window.**
*Spec basis:* ambiguous — *"תוחלת של 500 ביום"* with arrival window 09:00–16:00; "ביום" could mean the 11 h operating day or the 7 h arrival window.
*Our choice:* 500 expected arrivals spread over 420 min ⇒ λ≈500/420 per min.
*Found in:* PLAN §5.2 L82, §10/M3 L420, Appendix B open item L521; CONFIG NB cell 22 L200-201; NB §6 table L844.
*Alternative reading:* 500 over the full 11-hour operating day (λ≈500/660).

---

## Revenue / accounting

**R1. Entry ticket revenue counted PER PERSON (₪500 × entity.size).**
*Spec basis:* *"כרטיס כניסה – 500 ₪"* (price given); per-person vs per-entity application is unstated.
*Our choice:* ₪500 per member (entry is processed per person; a festival ticket is inherently per-person).
*Found in:* PLAN §5.7 L169, §9 #8 L356, §8 D3 L340, §7.3 L264; M4B §5 L164.
*Alternative reading:* ₪500 per entity (one ticket per group) — undercounts the dominant revenue source ~avg-size×.

**R2. Overnight revenue per person; FG pre-buys the ₪700 bundle, Couple pays a ₪250×size add-on.**
*Spec basis:* prices given (*"לינה 250; כניסה+לינה 700"*); per-person application AND the FG bundle-vs-(500+250) timing are unstated.
*Our choice:* per person — FG pre-commits ₪700×size at arrival (replacing the ₪500 ticket); Couple pays ₪250×size (=₪500/couple) at EndOfDay1.
*Found in:* PLAN §5.7 L170, §9 #8 L356, §8 D3 L331/L340.
*Alternative reading:* per-entity; or FG realises ₪500 ticket + ₪250 add-on = ₪750 at end of day (differs +₪50 per staying group).

**R3. PhotoStation print (₪30) counted PER ENTITY (once per visit), not per member.**
*Spec basis:* *"ותירכוש עותק מודפס ב30 ₪"* tied to the (per-entity) satisfied photo.
*Our choice:* one ₪30 per satisfied entity (consistent with one shared photo, B17).
*Found in:* PLAN §5.7 L172, §9 #10 L358, §9 #8 L356; M4B §5.
*Alternative reading:* ₪30 per member.

**R4. Merch purchases rolled & charged PER MEMBER.**
*Spec basis:* per-buyer probabilities given (0.8/0.4/0.9/0.3); "buyer" granularity unstated.
*Our choice:* each member independently rolls all four items (a 5-person group can buy 5 shirts).
*Found in:* PLAN §5.7 L171, §9 #9 L357, §5.4 L117; M4B §5.
*Alternative reading:* one set of item rolls per entity.

**R5. Food revenue booked per food-unit with pizza consolidation.**
*Spec basis:* prices given; the per-food-unit + consolidated-pizza accounting follows B14/B15.
*Our choice:* individual pizza ₪40 / family pizza ₪100×`ceil(P/3)` / burger ₪100 per member / asian ₪65 per member.
*Found in:* PLAN §5.7 L173, §5.5 L133-143.
*Alternative reading:* per-entity food billing (see B15 alt).

---

## Distribution-fitting

**D1. FriendsGroup arrival intervals fitted as GAMMA, rejecting the initial Exponential hypothesis.**
*Spec basis:* spec supplies the data and requires a goodness-of-fit test; the family is our call.
*Our choice:* Gamma(α̂≈1.239, β̂≈1.106) after moment diagnostics ruled out Exp (std/mean 0.87 vs 1.0, skew 1.29 vs 2.0, mode>0; Chi² rejected Exp for k∈{5,7,8,10}).
*Found in:* PLAN §10/M2 L404; NB cell 26 internal div L372-381, cells 29-31; COV L34/L75.
*Alternative reading:* Exponential (memoryless inter-arrivals — the original plan's hypothesis).

**D2. MainStage concert duration fitted as NORMAL.**
*Spec basis:* data supplied; family choice ours (Normal is the natural symmetric pick but still a tested hypothesis).
*Our choice:* Normal(μ̂≈45.90, σ̂≈8.93); KS D=0.102, Chi²(df=9)=14.0, both pass; mild left skew (≈−0.54) judged not disqualifying.
*Found in:* PLAN §10/M2 L405; NB cells 33-38; COV L34/L96.
*Alternative reading:* a skewed family (lognormal / Gamma) to capture the left tail.

**D3. Goodness-of-fit methodology: MLE + KS + equal-probability-bin Chi² at α=0.05.**
*Spec basis:* a fit test is required; the estimator, tests, and binning are unspecified.
*Our choice:* MLE (Gamma via Newton-Raphson on the digamma equation; Normal closed-form), KS *and* Chi² with **equal-probability** bins, df = k−1−2.
*Found in:* PLAN §10/M2 L406; NB cells 28/29/35/36.
*Alternative reading:* method-of-moments; a single test; fixed-width bins.

**D4. Chi-square bin count k = 12.**
*Spec basis:* silent on k.
*Our choice:* k=12 (inside 10–15, satisfies Cochran E_i=100/12≈8.33≥5; k=10,11 reject, k=12–15 pass — chosen by Cochran's rule, not k-shopping).
*Found in:* PLAN §10/M2 L406 (k-sensitivity); NB cell 29 `K_BINS_FG=12` L536 + cell 31 internal div L621-627.
*Alternative reading:* k=10/11 (which would reject the Gamma fit).

**D5. KS uses the unmodified critical value 1.358/√n despite estimating parameters from the same data.**
*Spec basis:* silent.
*Our choice:* unmodified asymptotic KS critical (anti-conservative simplification, not Lilliefors).
*Found in:* PLAN §10/M2 L406; NB cell 29 L515.
*Alternative reading:* Lilliefors / bootstrap critical values that account for estimated parameters.

---

## Sampling-algorithm

**S1. FG Gamma arrivals sampled via Acceptance-Rejection with a mean-matched Exponential envelope.**
*Spec basis:* methods listed with *"או"* (or); A-R mandatory only for DJ; Gamma has no closed-form inverse CDF for non-integer shape.
*Our choice:* A-R, Exp envelope, derived c=α^α e^{−(α−1)}/Γ(α)≈1.131, accept≈88.4%.
*Found in:* PLAN §10/M3 L407/L418/L431; NB §6.5 cell 50; COV L75.
*Alternative reading:* numerical inverse-CDF (scipy ppf) or Marsaglia-Tsang.

**S2. DJ stay sampled via Acceptance-Rejection (mandatory) with a U(20,60) envelope, M = sup f = 1/15 at x=40⁺.**
*Spec basis:* A-R is mandated; the envelope and the discontinuity reading are ours.
*Our choice:* uniform envelope, M=1/15 (jump-up at x=40), c=8/3, accept=3/8≈0.375; validated at 20,000 draws.
*Found in:* PLAN §10/M3 L424/L432; NB §6.4 cell 48 + §6.7 cell 57; CONFIG NB cell 22 L237-243.
*Conflict (historical):* the CONFIG comment notes PLAN.md *initially* claimed M=1/30; reconciled to 1/15 (now consistent).
*Alternative reading:* a different envelope; or (the corrected error) M=1/30.

**S3. PhotoStation duration sampled via COMPOSITION (presented as the 4th named method).**
*Spec basis:* method unspecified; composition is a listed option.
*Our choice:* one recycled `u` selects the segment of the piecewise CDF and inverts within it — numerically identical to a piecewise inverse transform, but framed as composition to cover all four named methods. (Supersedes the earlier C1-n1 "composition not used" call.)
*Found in:* PLAN §10/M3 L425/L431/L449; NB §6.3 cell 46 + `Sampler.photo_duration` L1322; COV L114.
*Alternative reading:* label it a plain piecewise inverse transform (leaving "composition" unused and losing that method's coverage credit).

**S4. Box-Muller for all four Normal draws, discarding the second variate.**
*Spec basis:* Box-Muller listed; which normals use it is unstated.
*Our choice:* Box-Muller for main-show, battery, glitter, and food-register normals; discard Z₂ to keep one RNG stream per source.
*Found in:* PLAN §10/M3 L423/L427/L428; NB §6.2 cell 44 L924; `Sampler._normal_box_muller`.
*Alternative reading:* cache Z₂ (polar/Marsaglia) for 2× fewer uniforms.

**S5. Positive-truncation on the three Normal DURATIONS only; battery is clamped, not truncated.**
*Spec basis:* silent (Normals can go negative; durations can't).
*Our choice:* rejection-resample until x>0 for main-show, glitter, and food-register N(5,1.5) (~0.045% negatives); battery N(40,15) is clamped to [0,99] instead (see E2).
*Found in:* PLAN §10/M3 L412, Appendix B L509; `Sampler` L1208-1222/L1279/L1389/L1427.
*Alternative reading:* clamp durations at 0; or leave them untruncated.

**S6. Just-in-time sampling (draw at moment of use), for CRN-friendliness.**
*Spec basis:* silent.
*Our choice:* every quantity drawn at service start (not queue-join); inter-arrivals self-scheduled on each arrival firing.
*Found in:* PLAN §9 #15 L363, §5.4 L125.
*Alternative reading:* pre-sample durations at queue-join / entity creation.

**S7. Charge-time sampled by inverse transform on an analytically-derived CDF.**
*Spec basis:* the PDF `f(t;α)` is given; F and its inverse are not (one sensible method, but the derivation is ours).
*Our choice:* derived F(t)=1−((40−t)/40)^α ⇒ t=40(1−U^{1/α}).
*Found in:* PLAN §10/M3 L426; NB §6.6 cell 52 + `Sampler.charging_time` L1353.
*Alternative reading:* none material (numerical inversion is the only competitor).

---

## Simulation-mechanics (event graph)

**M1. The model decomposes into a 23-event catalog (7 + 11 + 1 + 3 + 1).**
*Spec basis:* silent — we decompose the system into events.
*Our choice:* 7 bootstrap + 11 service-completion + 1 cross-resource (`AbandonQueue`) + 3 time-advance + 1 departure; all 23 confirmed via the time-advance and split-vs-parameterize tests. Sub-decisions: `AbandonQueue` is **one** node parameterized by venue+entity (not 4); the food chain is **3** phase nodes parameterized by restaurant (not 9); the **3 arrivals are split** (independent streams/windows/downstreams); `EndOfStay` is a single convergence node.
*Found in:* PLAN §6 L177-232, Appendix A; EDGE §2 L71-104, N0 L53.
*Alternative reading:* per-venue abandonment nodes; per-restaurant food nodes; a merged arrival node.

**M2. AbandonQueue mechanics — per-entity timer from queue-join, "commit-on-first," per-member penalty.**
*Spec basis:* tolerances/penalties given; the timer mechanics are silent.
*Our choice:* one timer per entity from queue-join; **cancelled the moment the first member starts service** (so no member is in service when it fires); on fire, pull all queued members, apply −penalty to each (clamp 0), route onward. No "members-in-service" branch exists.
*Found in:* PLAN §9 #1 L349, §8 D1 L286-296; EDGE §1 (`AbandonQueue`); M4B §5.
*Alternative reading:* per-member timers; commit only when *all* members are in service; penalty only to still-queued members.

**M3. Abandonment applies at EXACTLY 4 venues (Photo, Charging, Merch, BodyArt).**
*Spec basis:* *"מספר דקות שמוכן להמתין בעמדות (לא כולל הופעות)"* excludes shows; Entry and FoodCourt are not addressed (resolved with the professor).
*Our choice:* abandonment at the 4 service stations only; none at shows, Entry, or FoodCourt (professor-confirmed).
*Found in:* PLAN §9 #2 L350, §5.3 L106; M4B §5.
*Alternative reading:* include FoodCourt (and/or Entry) abandonment.

**M4. Per-member parallel service at Entry/Charging/Merch/BodyArt.**
*Spec basis:* *"במקומות מסוימים יש מקום למספר מסוים של אורחים (בני אדם)"* flags person-capacity venues; the dispatch mechanics are ours.
*Our choice:* an entity at the front occupies `min(remaining_members, free_servers)`; a finished member frees its server immediately (handed to the next same-entity member, else the next entity); the entity's next-activity decision waits for the LAST member.
*Found in:* PLAN §5.4 L121-125, §9 #5 L353; M4B §5; m4 flags S1/S2 L43-47.
*Alternative reading:* serialise members one at a time; or hold all seized servers until the whole entity finishes.

**M5. DJ "70 בכל רגע נתון" modeled as max-capacity 70 + continuous roll-admit (no shows).**
*Spec basis:* the number 70 is given; the continuous/roll-admit mechanism is interpretation.
*Our choice:* capacity 70, continuous occupancy, roll-admit as spots free; no ShowStart/ShowEnd. (Conscious side-effect: with no DJ abandonment, a required DJ stop can queue until the day-end drain.)
*Found in:* PLAN §5.3 L99, Appendix B L515; EDGE §2.
*Alternative reading:* discrete DJ "sessions" of 70.

**M6. MainStage rolling/mid-show walk-in admission; both stages may start under-cap; SideStage batch + walk-in.**
*Spec basis:* the spec gives only the MainStage vacated-spot seating rule; walk-ins, under-cap starts, and SideStage admission are silent.
*Our choice:* MainStage admits batch-at-start + mid-show walk-in (if under-cap) + vacated-spot rolling; SideStage batch-at-start + mid-show walk-in; shows may start under capacity (generalizes the spec's vacated-spot rule).
*Found in:* PLAN §9 #3 L351, §9 #17 L365, §5.3 L97-98; EDGE D3 L56.
*Alternative reading:* strict batch admission only at ShowStart for both stages.

**M7. Day-boundary drain semantics (EndOfFestival and EndOfDay1 DRAIN, not hard-stop).**
*Spec basis:* the festival "ends" at 20:00; handling of in-flight activities at 20:00 is silent.
*Our choice:* in-flight events finish (the clock runs past 20:00); their handlers route to `EndOfStay`; the boundary handler only sweeps idle/stuck entities.
*Found in:* PLAN §6 L220, §9 #13 L361, §8 D3 L339; EDGE C2 L55.
*Alternative reading:* a hard stop at 20:00 that truncates in-flight activities.

**M8. Multi-day bootstrapping — EndOfDay1 is the SOLE day-2 re-seeder; streams stop self-scheduling at window-end; EndOfFestival is init-seeded.**
*Spec basis:* silent (a two-day event-driven run needs a re-seeding architecture).
*Our choice:* arrival streams stop self-scheduling at their window-end (don't cross midnight); EndOfDay1 re-enables the day-2 stream/show flags and re-seeds day-2 arrivals/shows + `Day2Resume`; EndOfFestival is seeded at t=0 (not by EndOfDay1) to avoid double-scheduling; FG is day-1-only (not re-seeded).
*Found in:* PLAN §6 L184, §9 #13 L361, §8 D3 L336-337; EDGE C L54 + §4 #20.
*Alternative reading:* let streams self-schedule across the boundary; or have EndOfDay1 schedule EndOfFestival.

**M9. ShowEnd owns the next ShowStart (at now+break: 10 main / 5 side); ShowStart never self-schedules.**
*Spec basis:* the 10/5-min breaks are given; which event schedules the next show is a modeling choice.
*Our choice:* `ShowEnd ↔ ShowStart` mutual cycle, scheduled from ShowEnd.
*Found in:* PLAN §9 #19 L367, §8 D2 step 6 L320; EDGE E1 L63.
*Alternative reading:* ShowStart self-schedules the next start.

**M10. EndOfStay is a single convergence/terminal node consolidating exit from ~10 sources.**
*Spec basis:* silent.
*Our choice:* one departure event; drawn receive-only on the diagram (every `→stations` edge folds in `→EndOfStay`); an ordinary terminal event in code (`select_next_activity → None`).
*Found in:* PLAN §9 #20 L368; EDGE D5 L58.
*Alternative reading:* inline exit logic at each completion handler (no convergence node).

**M11. STATIONS super-node box on the event diagram (diagram device only).**
*Spec basis:* silent (a presentation choice for the K₄ all-to-all routing).
*Our choice:* draw the 4 stations + `EndOfStay` as a box with 4 `station↔box` edges abbreviating the K₄; **no cluster object exists in code** (routing is per-entity via `select_next_activity`).
*Found in:* EDGE R1/R2/R3 L59-61, §5; PLAN §6 L229.
*Alternative reading:* enumerate all 6 station-to-station edges explicitly.

**M12. Routing fixes — EndEntry→Merch (Single's first stop), DJ is one node.**
*Spec basis:* spec gives the itineraries; the diagram's edge set is ours.
*Our choice:* Single's first stop after Entry is Merch (the v1 `EndEntry→BodyArt` was spurious, E3); DJ completion is a single `EndAtDJstage` node (E5).
*Found in:* PLAN §9 #22 L370; EDGE E3/E5 L65/L67.
*Alternative reading:* (the v1 errors) EndEntry→BodyArt; two DJ nodes.

**M13. Event-diagram notation conventions + the three handling diagrams chosen.**
*Spec basis:* the spec requires an event diagram + handling diagrams for "three events of your choice," but the notation rules are ours (the lecturer's slides are terse).
*Our choice:* circles only; zigzag = init arrow for the 7 FEL-seeded events only (not a generic stochastic marker); solid = scheduling; no condition/delay labels on arrows; handling diagrams are flowcharts. The three diagrammed events: **AbandonQueue (D1), ShowStart@MainStage (D2), EndOfDay1 (D3)**.
*Found in:* PLAN §10/M1 L382-393, §8; COV L48-50.
*Alternative reading:* a different notation, or a different choice of three events.

---

## Output-analysis

**O1. KPIs chosen: avg satisfaction at exit; avg + max queue wait across stations; festival revenue.**
*Spec basis:* *"בחרו 2-3 מדדים שתרצו לייעל"* (choose 2-3).
*Our choice:* these three (using the upper end of the 2-3 range).
*Found in:* PLAN §1 L15; NB §1 cell 4 L44 + §4; COV L36.
*Alternative reading:* a different metric set (e.g. abandonment rate, throughput).

**O2. Terminating simulation — N independent replications, no warmup deletion, Bonferroni-split α.**
*Spec basis:* *"חישוב מספר הרצות"* is required; terminating-vs-steady-state and warmup are unspecified.
*Our choice:* model as terminating (hard 2-day start/stop, opens empty); N replications of the full run with **no warmup deletion**; N sized for relative precision γ=0.1; α=0.1 Bonferroni-split across metric×comparison tests.
*Found in:* PLAN §5.1 L74, §10/M3 C2-M1 L451; NB §15 cells 81-83; COV L162.
*Alternative reading:* steady-state with warmup deletion (the example notebook's 15-day-warmup hotel — judged not transferable).

**O3. Alternatives compared via a PAIRED t-test under CRN (not Welch).**
*Spec basis:* *"השוואה סטטיסטית... ביטחון 0.9, דיוק 0.1"* — the test is unspecified.
*Our choice:* paired-difference CI / paired t-test on CRN-matched per-replication diffs; Welch kept only as a fallback if CRN is dropped.
*Found in:* PLAN §9 #15 L363, §5.1 L74, §10/M3 C2-M2 L452; NB §18 cells 90-92; COV L162.
*Alternative reading:* Welch two-sample t-test on independent runs (invalid under CRN; discards the variance reduction).

**O4. Common Random Numbers — one RNG stream per source, reseed only affected streams.**
*Spec basis:* silent.
*Our choice:* `RNGStreams` gives each random source its own `random.Random` (seeded via `SeedSequence.spawn`); alternatives reseed only the streams they touch. (The dead `lodging_couple` stream was dropped — couple lodging is a deterministic mean>7 test.)
*Found in:* PLAN §10/M3 L440, Appendix B L520; NB `RNGStreams` cell 53; M4B §3.
*Alternative reading:* a single global RNG (no variance reduction).

---

## Edge-case / numeric

**E1. Satisfaction clamped to [0,10] after every mutating delta.**
*Spec basis:* the bounds 0/10 are given, but clamping every intermediate value (vs only at read-out) is a modeling choice.
*Our choice:* clamp to [0,10] in every handler that mutates satisfaction.
*Found in:* PLAN §5.6 L163, §9 #16 L364; M4B §5; `Customer.update_satisfaction`.
*Alternative reading:* let deltas accumulate unbounded and clamp only at exit.

**E2. ChargingStation battery clamped to [0,99].**
*Spec basis:* battery ~ N(40,15); out-of-range tails are unaddressed.
*Our choice:* clamp [0,99] — only b<100 is mathematically required (α=100/(100−b) divides by zero at 100); b=0 is valid (α=1 → Uniform(0,40)); ~0.38% of mass piles at 0.
*Found in:* PLAN §9 #21 L369, §5.3 L101; NB §6.6 cell 52 L1093 + `Sampler` L1351; m4 L213.
*Alternative reading:* clamp to [0,100); reject-and-resample the ≥100 / <0 tails; or a different cap.

**E3. Show-score time term T = integer HOUR-OF-DAY of show end (9–20).**
*Spec basis:* *"T (Time) – הזמן (בשעות בלבד) שבו נגמרה ההופעה"* — ambiguous: hour-of-day vs elapsed-since-start.
*Our choice:* integer hour-of-day (9–20); the /19 divisor is tuned so T=20→1.0, and a day-2 elapsed clock would overshoot.
*Found in:* PLAN §5.6 L155, §9 #14 L362; CONFIG NB cell 22 L325-326.
*Alternative reading:* elapsed hours since festival start.

**E4. Kitchen alternative read as "drops TO 0.1 / rises TO 85%."**
*Spec basis:* *"ההסתברות למנה לא טובה קטנה ל-0.1 ואחוז המבקרים... יעלה ל-85"* — the preposition `ל` ("to").
*Our choice:* `food_unsatisfied_prob = 0.1`, `food_choose_prob = 0.85` (the `ל` matches the eat-share's "יעלה ל-85" = to 85%). **Corrected 2026-05-30** (an earlier read had "by 0.1" ⇒ 0.3).
*Found in:* PLAN §11 L462, Appendix B L510; CONFIG NB cell 22 L161/L318; COV L166.
*Alternative reading:* drops *by* 0.1 ⇒ 0.3 (the rejected misread).

---

## Counts per category

| Category | Count |
|---|---|
| Behavioral | 20 (B1–B20) |
| Revenue / accounting | 5 (R1–R5) |
| Distribution-fitting | 5 (D1–D5) |
| Sampling-algorithm | 7 (S1–S7) |
| Simulation-mechanics (event graph) | 13 (M1–M13) |
| Output-analysis | 4 (O1–O4) |
| Edge-case / numeric | 4 (E1–E4) |
| **Total** | **58** |

---

## Doc-vs-doc inconsistencies flagged (must reconcile before submission)

1. **The §2 "Design Decisions Log" (the old 13-item NB cell 7) was replaced by prose narrative** (current §2 reflects the locked decisions); the stale-log warnings have been removed from this inventory.
2. **Pizza "יחידים" reading split (B15):** PLAN reads *lone person*; the CONFIG comment (NB cell 22 L313 "Single only") and COV L148-149 still encode the rejected *Single-type* reading.
3. **DJ A-R M value (S2):** the CONFIG comment records that PLAN.md *initially* claimed M=1/30; reconciled to 1/15 — now consistent, kept here as provenance.
4. **EVENT_NODE_EDGE_SPEC.md** was reconciled with the 2026-05-30 audit (the MainStage early-exit model, E4 resolved) via inline `[2026-05-30]` notes; the notebook/PLAN win on any residual conflict.

---

## Boundary check — items that look like decisions but are SPEC-GIVEN (excluded)

Verbatim numbers used as printed (not decisions): MainStage cap 200, SideStage 100, DJ 70, Photo 3, Charging 150, Merch 7, BodyArt 2, Entry 5 booths; all prices (entry 500 / lodging add 250 / combo 700 / merch 100·50·40·200 / photo 30 / pizza 40·100 / burger 100 / asian 65); photo-satisfied 0.7 (+2) & unsatisfied 0.5 (−0.5); merch probs 0.8/0.4/0.9/0.3; BodyArt choose 0.3/0.3/0.4, satisfied 0.7/0.6/0.8, bonus 0.8/1.2/0.7; food-unsatisfied 0.4 (−0.6) & food-choose 0.7; FG lodging 0.7; show good/bad split 0.5/0.5; farthest-10 leave prob 0.5; all windows (festival 09:00–20:00, FG 09:00–13:00, couple 10:00–16:00, single 09:00–16:00); satisfaction init 5 / max 10 / min 0; 2-day structure; abandonment minutes & penalties (FG 15/−2, Couple 20/−1.5, Single 20/−1); all named distributions (side U(20,30), DJ & photo piecewise PDFs, charging N(40,15) + α-PDF with α=100/(100−b), merch U(2,6), bodyart glitter N(15,3)/neon Exp(12)/henna U(17,22), food prep U(4,6)/U(3,4)/U(3,7), register N(5,1.5), meal U(15,35), scan U(1.5,3), security Exp(2)); food split 3/8 burger · 1/4 pizza · rest asian; the score formula with G∈{3,2,1} and divisors /2, /19; all 7 alternatives' costs and effect parameters; budget ₪1,000,000, confidence 0.9, precision 0.1.

**Near-given (mild readings, not promoted to full entries):** bad-show penalty −1 and Single abandonment −1 read from *"בנקודה"* (= 1 point — the only sensible reading); the fill-to-max "scan head→tail, capacity counts people, a smaller entity may complete the last slots" policy is the spec's own 99-in-a-100-cap worked example; "use most of the budget" reads *"המטרה היא להשתמש ברובו"*; choosing exactly 2 alternative combinations is the spec's *"בלפחות 2 קומבינציות"* floor. These are flagged here so the spec/decision boundary can be sanity-checked.