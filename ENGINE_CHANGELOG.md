# Engine & Analysis — Fixes Applied (2026-06-24)

This session finalized the notebook for submission. The §12–13 run loop and §14–18 analysis
were rewritten for correctness and to enforce our design decisions. Verified by executing the
full notebook end-to-end (0 errors) and sweeping 112 seeds (no crashes, no leaks, every member
recorded exactly once, reproducible).

## Correctness fixes (run loop)
- **Overnight stayers now participate on day 2.** `Day2Resume` sets the entity back to `transit`
  before routing (was a no-op — the `"night"` guard returned immediately). Honors B10.
- **Day length is CONFIG-derived (660 min, 20:00).** Was hardcoded `EndOfDay1(600)` (19:00).
- **Day-2 show satisfaction fixed.** `end_hour` is reduced within the day; shows score via
  `Customer.on_show_end` (was `int(time/60)+9`, which blew up on day 2).
- **Clean termination, no leaks.** `EndOfFestival` is now init-seeded at the day-2 close and drains
  all remaining entities (M7/M8); `EndOfDay1` no longer hard-clears queues. Run ends ~t=2145
  (a short in-flight drain past 2100) instead of running for 13 extra hours.
- **Commit-on-first abandonment.** A stale `AbandonQueue` from a prior stop can no longer fire:
  only the entity's current armed timer is honored (`abandon_event is self`), and a timer is
  defused once any member of the entity starts service (`in_service_entities`). This was the
  root cause of a seed-dependent crash (entity in two venues at once).
- **BodyArt breaks now actually take an artist offline.** Added a per-server `available` flag to
  `QueueServer`; the artist is taken offline before the next customer can be dispatched and comes
  back at `BreakEnd_BodyArt`.
- **Food court closes at its 15:00 window.** Unserved queued guests give up (no purchase); revenue
  books at the register (payment), not on intent. Bounds the food drain and reflects the 3-register
  bottleneck honestly.
- **`detach()` frees busy servers**, so a lingering `EndService` can't revive a departed entity
  (was double-counting ~40 departures/run).
- **Stage holding lines can no longer strand across the overnight gap.** A FriendsGroup/Single in
  the farthest-10 that early-exits a show re-queued the Main stage even after the day had closed
  (a show can finish past close under drain, so `EarlyExitCheck` fires *after* `EndOfDay1`'s sweep).
  The stranded entity then sat through the 780-min closed gap and was admitted by the day-2
  `ShowStart`, recording a ~770-min wait (impossible — longer than any day). Now an entity re-queues
  only while `clock < day_close`; after close it routes onward (overnight/exit). Surfaced by the
  §20 demo's max-wait readout. Max Main wait: **754 → ~85 min**; 0 cross-day stage admissions.

## Design decisions enforced
- **No magic numbers** — every time bound derives from CONFIG (`festival_open/close_hour`,
  `festival_days`, `minutes_per_calendar_day`, the per-stream window hours); prices from CONFIG.
- **Satisfaction goes through the OOP layer** (`Customer.update_satisfaction` / `on_show_end`).
- **§14 N-runs is honest.** The relative-precision formula gives N_req = 1 for all three KPIs
  (CV ≈ 2–3%), so the binding constraint is the CLT floor of 30. We now report this instead of
  reverse-justifying 30.
- **CRN** is documented: baseline and both alternatives share `seed_base`, so per-stream seeds
  align and the §17 paired differences are low-variance.
- Removed `from __main__` imports, the nested `Day2Start` class, and leftover dev comments.

## Alternatives (§16)
Two budget-constrained combinations (both fix the dominant Entry bottleneck first):
- **Combination 1 — "Operations Fix" (₪950k):** auto-entry + Photo/BodyArt expansion + visitor gift.
- **Combination 2 — "Growth Engine" (₪950k):** auto-entry + advertising (+20%) + Photo/BodyArt expansion.
  (The visitor gift is now Combo-1-only, so the two combinations are genuinely distinct.)

Result (N=30, paired-t, CRN): both cut the Entry wait and raise revenue significantly. Combo 1 improves
all three KPIs (satisfaction 4.84→6.02, entry 214→125 min, revenue +₪104k). Combo 2 maximizes revenue
(+₪426k, ~4× Combo 1) but satisfaction stays flat and even dips slightly (4.84→4.77 — small but
significant regression), entry 214→151 min: pure revenue, no experience gain. §18 recommends **Combo 1**
(the only combination that significantly improves all three; protects the reputation of a recurring event).

## Notebook housekeeping
- D2/D3 handling diagrams embedded as PNGs in §3 with tone-matched Hebrew explanations.
- All internal `⚠️ DELETE BEFORE SUBMISSION` cells removed; pip install moved into the setup
  section (title is now the first cell); GenAI log updated.
- The §20 demo section was removed (redundant with §15's baseline run; it had served only to
  surface the stage-strand bug above). §19 (GenAI log) is now the final section.
- Title cell: the members list was converted from `<br>`-separated lines to blank-line markdown.
- Removed the stale, unused `SECTION_12_13_EXPLANATION.md` (it described an earlier engine and
  said arrivals were Exponential/Uniform; FriendsGroup arrivals are Gamma).
