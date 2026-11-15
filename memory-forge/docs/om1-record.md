# OM-1 record — measurement harness + accuracy battery v1 (2026-11-15)

## Built
- Harness: purplelongship `~/ollama-memory-forge/harness/omf_harness.py` (sha256 6415a698…), results `battery-<label>.json` beside it. Scenarios: control (8 turns, in-window), overflow (12 turns at num_ctx=1024), frontedit. Six keyword-scored fact probes (name, ship, sister, food, wreck, teacher) against the Sigrid character card.
- The battery pins `num_gpu=0` per request: deterministic CPU inference, immune to other campaigns' VRAM churn (recon baselines were CPU in substance — 0/36 layers offloaded). Found the hard way: with only 143 MiB VRAM free, a q8_0-KV load died allocating a 141 MiB GPU compute buffer (HTTP 500) — the shared-machine condition, recorded, not fought.

## Stock baseline through the formal harness (battery-stock.json)
- control: **3/6** (ship ✓, food ✓, teacher ✓; name/sister/wreck returned EMPTY even in-window)
- overflow: **1/6** (only food survived) — reproduces the recon ad-hoc result exactly.
- frontedit: turn-3 evaluated 432 → next turn with a one-word system edit 529 (metric confounded by turn growth; paired-session fix owed in OM-3).

## Reading of the control score (important for OM-7 targets)
The model itself (4.6B Q2_K, baked temperature 1.0 + presence_penalty 1.5 — a penalty that
actively suppresses context words like names) misses facts in-window. The battery measures
model + sampling + memory handling together, stock vs forged under identical sampling.
**OM-7's fairness rule: the forged stack wins by holding its control-level score past
overflow and across long chats — not by retuning sampling.** Targets: forged overflow ≈
forged control ≥ stock control (3/6), and forged long-chat retention ≫ stock.

## Fixes owed
- frontedit scenario: paired identical sessions (edit vs no-edit from the same state) — OM-3.
- Battery v2 (OM-7): add long-chat scenario at production-like ctx, contradiction scenario,
  and the seeded-store recall suite.
