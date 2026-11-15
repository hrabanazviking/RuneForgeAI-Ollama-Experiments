# OM-3 — Prefix-reuse discipline (paired frontedit metric) — record

**Date:** 2026-11-15 keeper tick (~06:02–06:20 EST). **Seat:** purplelongship.
**State:** layer v3 DEPLOYED and PROMOTED to the live port 127.0.0.1:11500
(PID 3424337, health version 3). v2 retired from :11500 after v3 passed the
battery regression identically. Paired metric run end-to-end on both legs.
**OM-3 verdict: mechanism live, reuse win NOT yet proven — the paired metric
as instrumented cannot see prefix reuse on this build (finding below).**

## What v3 adds over v2 (omf_layer_v3.py, sha256 20562556…)
- Session anchor pinning: the first anchor seen for a session (client-sent
  `omf_session`, else derived from anchor bytes) is pinned byte-identical for
  the session's life.
- Dynamic-front quarantine: later system content that diverges from the
  pinned anchor (per-turn timestamps, recall injections, one-word front
  edits) is moved to a "Dynamic context" band placed just before the final
  user turn, so the cached prefix (anchor + memory band + history) is never
  poisoned by front churn.
- Reuse counters surfaced at GET /omf/stats (prompt_eval_count from the
  runner, assembled estimate, reused estimate).
- OM-4 summary band + OM-5 fact ledger carried over unchanged.

## Paired metric (omf_paired.py, sha256 52b0bbd7…; paired-stock.json / paired-layer.json)
Identical assembled size, identical tail turn; only difference is a one-word
front edit. Fixed synthetic history, temp 0, model gemma4viking4b.

| leg | warm | noedit | rewarm | frontedit |
|---|---|---|---|---|
| stock (:11499) prompt_eval_count | 632 | 632 | 632 | 633 |
| layer v3 (:11501) prompt_eval_count | 700 | 700 | 700 | 789 |

Dynamic-injection legs (prompt_eval_count per turn): stock dynfront ==
dyntail exactly (529/650/771). Layer dynfront runs +12/turn over dyntail
(609/730/851 vs 597/718/839) — the quarantined band + post-history core
overhead, visible and small.

## Finding: prompt_eval_count does not discriminate reuse on this build
On stock, the no-edit leg evaluates the same count as the warm leg (632 ==
632) — if prefix reuse were visible in this counter, noedit would show only
the new tail (~121). Either the scratch build reports total prompt tokens
regardless of cache hits, or reuse is not happening across these stateless
resends; the counter cannot distinguish the two, so OM-3's headline claim
(per-turn reprocessing removed) is **not proven by this instrument**. The
layer's own reused_est inherits the same flaw (it is arithmetic on the same
counter). Wall times on this shared box are too noisy to substitute (stock
dyntail turn 3: 771 tokens in 4.33 s vs turn 1: 529 in 7.22 s).

**Next step for OM-3 (immediate next work, recorded per the no-unfixed-bug
law):** re-instrument with a discriminating signal — prompt_eval_duration /
per-token eval timing in a quiet window, and/or the runner's cache counters —
then re-run the paired legs. Until then OM-3 stays "mechanism live, win
unproven," and no speed claim is made from these numbers.

## Battery regression (gate for promotion)
Battery v3 (omf_harness2.py) against layer v3 on :11501:
control S 5/5, H 4/4 correct / 0 wrong; overflow S 5/5, H 4/4 correct /
0 wrong — identical to layer v2's banked scores. No regression; promotion
to :11500 justified on the strength of pinning + quarantine being live for
real clients, with the reuse quantification still owed.

## Transfer note
v3 + paired harness were built on the VM in the 05:51 tick but never
deployed (transfer halted). This tick moved them via chunked file.write
(372-byte pieces, per-chunk byte-count verified, whole-file sha256 verified
on-device; .py sha256s match the VM originals). One gzip segment
deterministically expanded in re-emission at a fixed offset; regenerating
with `gzip -n` shifted the bytes and the transfer went clean — worth
remembering for future crossings.
