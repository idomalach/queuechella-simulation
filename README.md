# Queuechella — Festival Simulation (Group 20)

Event-driven simulation of the two-day **Queuechella** music festival, for the Simulation course (semester B 2026). The festival runs 09:00–20:00 each day; we model visitor flow through stages, stations and food courts to evaluate service quality and recommend budget-constrained improvements.

- **Submission:** 2026-06-29 (notebook + 7-min presentation + 10-min defense).
- **Deliverable:** a single Colab notebook (`Queuechella_Simulation.ipynb`) — OOP, top-down, English code comments, Hebrew report narrative.

## Group
- Ido Malach — 318782208
- Yonatan Dolman — 208987644
- Etan Cohen — 322067448

## Repository layout
| Path | What it is |
|---|---|
| `Queuechella_Simulation.ipynb` | **The deliverable.** Master notebook (developed locally, delivered in Colab). |
| `PLAN.md` | **Single source of truth** — event model, design decisions, milestones, sampling/OOP plan. Read this first. |
| `instructions_coverage.md` | Spec checklist (every spec bullet → a checkbox) + partner handoff notes. |
| `Course Project 2026B.pdf` | The authoritative assignment spec. |
| `samples_for_simulation.xlsx` | Empirical data for distribution fitting (2 sheets). |
| `example solution.ipynb` | Lecturer's example — structural + report-style reference. |
| `EVENT_NODE_EDGE_SPEC.md` | Detailed event node/edge reference (partially superseded by PLAN — see its top banner). |
| `diagrams/` | Distribution-fit plots; `diagrams/event diagrams/` holds the built event diagram + D1 handling diagram. |

## Status
- **M0** setup, **M2** distribution fitting (Gamma + Normal), **M3** sampling (`Sampler`) — done.
- **M1** pre-work diagrams — event diagram + D1 built **and embedded** in notebook §3; D2 + D3 still to build/embed.
- **M4** OOP class skeleton — stubs in place, being fleshed out.
- **M5** handoff package, then partners take the event-logic run loop, KPIs, alternatives, and report polish.

See **`PLAN.md`** for the full plan and every locked design decision.
