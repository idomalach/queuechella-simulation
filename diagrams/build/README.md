# Diagram build pipeline (M1)

Tooling that generates the Excalidraw event/handling diagrams from a Python description
of nodes + edges. Lets us regenerate cleanly when the node/edge spec changes.

## Pipeline
1. **`gen_excali_event.py`** — the editable source of truth for the event diagram.
   Holds `NODES` (id → center coords + label), `SELF`, `INIT`, `SCHED`, `BIDIR`, `ROUTED`.
   Emits the *simplified* Excalidraw element list → `event_excali.json`.
2. **`to_native_min.py`** — converts a simplified element list into a *minimal native*
   Excalidraw scene (bound text children, focus/gap bindings, boundElements) that
   `excalidraw.com` can open. Usage: `python3 to_native_min.py IN.json OUT.json`.
3. **`event_layout_mock.py`** — matplotlib mock that renders the layout AND auto-checks
   that no edge passes through a non-endpoint node (run it after any coordinate change;
   it prints VIOLATIONS — keep it at 0). View `/tmp/event_layout_mock.png`.
4. Export: paste the native JSON into the `export_to_excalidraw` MCP tool → share URL.
   (The MCP renders to a checkpoint only; the URL is how a human views/downloads the PNG.)

Run with the project venv: `~/venvs/Simulation_Project/bin/python3`.

## MCP gotchas (learned the hard way — read before touching the Excalidraw MCP)
- **`create_view` is NOT visible to the user** — it only writes an internal checkpoint and returns a
  `checkpointId`. The human sees the diagram only via the `export_to_excalidraw` share URL. So the
  loop is: build elements → `to_native_min.py` → `export_to_excalidraw` → give the user the URL.
- **`export_to_excalidraw` needs NATIVE format, not the simplified `create_view` format.** Passing
  simplified elements (inline `label`, `fixedPoint`, no `boundElements`) → **blank board**. That is
  why `to_native_min.py` exists (simplified → native: separate bound-`text` children w/ `containerId`,
  `startBinding`/`endBinding` `{elementId,focus,gap}`, and `boundElements` back-refs on each node).
- **You must INLINE the native JSON as the `json` param** (no file path arg). Keep it small —
  `to_native_min.py` drops every Excalidraw-default field (restore() back-fills them) so the v1 scene
  is ~29 KB and inlines fine. A full-fat native scene (~72 KB) gets persisted by Bash and is painful
  to inline. `cat` the minimal file, then paste.
- **Self-loops are left UNBOUND** (a single arrow bound to the same node on both ends glitches in
  Excalidraw). `to_native_min.py` detects same-element start/end and drops the binding. Trade-off: a
  self-loop won't follow if you drag its node. Round look = `roundness:{type:2}` + an arc `points`
  list (preserved by the converter).
- **Bindings need both halves:** the arrow's `startBinding`/`endBinding` AND the node's
  `boundElements` list must reference each other, or dragging won't move the arrow.
- Validate geometry in `event_layout_mock.py` (VIOLATIONS=0) BEFORE exporting — you can't see the
  Excalidraw render, so the mock is your only pre-flight check.

## Conventions (locked) — see PLAN.md §10/M1
- Event graph: circles only; **solid arrow** = scheduling; **zigzag arrow** = init (seed
  FEL at t=0, 7 events); double-headed = mutual; **no condition/time labels**. Black & white.
- Handling diagrams (D1/D2/D3) are flowcharts (rounded-rect actions + decision diamonds), RTL Hebrew.

## State (2026-05-29)
- Event diagram v1 built & exported. Layout/abstraction approved by user; arrows had known errors.
- **Node + edge validation DONE** → `EVENT_NODE_EDGE_SPEC.md` (this folder) is the authoritative
  v2.0 spec: 23-node audit, full decision log (C/C2/D3/D4/D5/R1–R4/E1–E5), per-handler edge list,
  the `STATIONS` super-node + fan-in drawing structure, and the build delta. Read it before editing.
- Handling diagrams D1/D2/D3: **not yet built**.

## v2.0 plan
1. ✅ (done) Node set validated + **complete edge spec** authored in `EVENT_NODE_EDGE_SPEC.md`
   (NOT in PLAN.md, by user request; PLAN edits to fold in later are in that file's §8).
2. (diagram session) Apply `EVENT_NODE_EDGE_SPEC.md` §7 build-delta to `gen_excali_event.py` — the
   big change is wrapping the 4 stations + `EndOfStay` in a labeled **box** and re-binding routing
   edges to the box (any-station) vs specific nodes; rerun `event_layout_mock.py` until VIOLATIONS=0,
   regenerate native, re-export.
3. Build D1/D2/D3 flowcharts; export; embed all four PNGs (base64) into notebook §3 (cell 11).
