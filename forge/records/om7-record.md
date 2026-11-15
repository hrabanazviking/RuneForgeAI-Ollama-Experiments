# OM-7 — Full gate: stock vs forged (battery v3 + OM-3 paired duration rerun)

**Run:** 2026-11-15 keeper tick, purplelongship. Runner: `omf-om7-gate.service`
(fenced transient user unit, MemoryHigh=6G/MemoryMax=8G), sequential legs:
battery v3 vs stock (:11499), battery v3 vs layer v3 (:11500), paired2 vs
stock, paired2 vs layer. Machine shared as usual (Samverk fullsuite
co-resident) — absolute millisecond figures carry contention noise; the
battery scores are the robust gate.

## Battery v3 — the headline accuracy proof, fresh full run

| leg | control S | control H | overflow S | overflow H |
|---|---|---|---|---|
| stock | 5/5 correct | 4/4 correct | 5/5 correct | **0/4 correct / 4 wrong** |
| layer v3 | 5/5 correct | 4/4 correct | 5/5 correct | **4/4 correct / 0 wrong** |

Stock reproduces its baseline exactly: through window overflow it loses
every early-history fact (confabulates all four) while system facts survive.
The forged layer holds everything — system facts 5/5 and early-history facts
4/4 with zero wrong answers in both scenarios. This is the OM-4/OM-5 result
re-proven end-to-end in the OM-7 gate configuration (managed services,
CPU-pinned scratch), not a replay of the earlier ad-hoc runs.
Files: battery2-stock-om7.json, battery2-layer-om7.json.

## Paired2 duration rerun (OM-3 quiet-window item, folded in per plan)

Medians of 3 reps, prompt_eval_ms; first-exposure = rep 1 where the cache
state makes medians misleading (stock reps 2–3 often hit the cache the
first rep created).

- Resend floor (byte-identical): stock 73.8 ms · layer 70.5 ms — same floor.
- No-edit continuation: stock median 6461 ms (bimodal: 155 / 6461 / 6890) ·
  layer median 983.5 ms, consistent across reps (946–1018). The layer's
  tail-band discipline gives a *predictable* tail-only cost where stock
  usually re-evaluates nearly everything.
- Front edit, first exposure: stock 7317 ms · layer 3203 ms — a ~56% cut,
  matching the OM-3 re-instrumentation figure (6.91 s → 3.03 s); layer reps
  are consistent (3203 / 3203 / 3385).
- Dynamic-front injection, turn 3: stock 9413.5 ms vs its own dyntail
  2982.1 ms (front injection costs ~3.2×) · layer dynfront 4155.9 ms vs
  dyntail 3890.5 ms (equalized, ~7% apart) — layer dynfront turn 3 is
  ~2.3× faster than stock's, reproducing the OM-3 headline. One noisy
  layer dynfront turn-2 rep (8464 ms) is contention, noted not hidden.
Files: paired2-stock-om7.json, paired2-layer-om7.json.

## Verdict

OM-7 PASSES. Accuracy: forged layer is strictly better than stock on the
only axis stock fails (overflow fact retention: 4/4 vs 0/4, zero wrong in
both scenarios) and identical everywhere else. Reuse: the layer's win is
partial but real and now reproduced twice — front-edit reprocessing cut
~56% on first exposure, dynamic-front injection equalized with tail;
not yet tail-only on front edits (~3.2 s remains, the v4 trailing-note
design from the OM-3 re-instrumentation record is the named follow-up,
folded into OM-8 close-out notes rather than a new slice).

Next: OM-8 speed/footprint gate + close-out.
