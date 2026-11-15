# OM-3 re-instrumentation — duration-based paired metric (omf_paired2.py)

**Date:** 2026-11-15 keeper tick (~06:25–06:30 EST). **Seat:** purplelongship.
**Question carried from om3-record.md:** prompt_eval_count cannot see prefix
reuse on this build (stock warm == noedit == 632). Does a discriminating
signal exist, and what does it say about stock vs layer v3?

## Instrument: prompt_eval_duration discriminates — VALIDATED
omf_paired2.py (sha256 9f555aed…) captures prompt_eval_duration (server-side)
per leg, 3 reps, medians reported, plus an exact-resend leg as the cache
floor. On stock (:11499): first-exposure warm **6788.6 ms** vs byte-identical
resend **76.3 ms** — a ~90x separation where the count showed none. The v1
instrument is superseded; all reuse claims below rest on durations.

## Paired legs (prompt_eval_ms)
| leg | stock rep1 | stock median | layer reps | layer median |
|---|---|---|---|---|
| warm | 6788.6 | 155.2 | 7753.4 / 1959.4 / 1981.6 | 1981.6 |
| resend (identical) | 76.3 | 74.8 | 73.1 / 72.1 / 80.2 | 73.1 |
| noedit | 161.3 | 161.3 | 891.7 / 950.6 / 929.9 | 929.9 |
| frontedit (1-word) | **6911.8** | 152.8 | 3091.2 / 3034.8 / 3015.2 | **3034.8** |

Readings:
- **Stock first-exposure front edit = full re-eval** (6911.8 ≈ warm 6788.6).
  The OM-3 failure is real, now measured with a discriminating instrument.
- Stock frontedit reps 2–3 collapse to 139–153 ms because the runner's
  multi-entry prompt cache had already cached the edited prefix in rep 1.
  In real chat every front edit is novel (timestamps/recalls change every
  turn), so **first-exposure is the honest comparator**; medians across
  reps would hide the effect and are not used for the verdict.
- **Layer frontedit ≈ 3.0 s on every rep** (its assembled form is stable,
  so there is no rep-1 anomaly): ~**56% below** stock's first-exposure
  6911.8 ms. The quarantine works — but the win is partial, not tail-only:
  layer noedit is 929.9 ms, so ~2.1 s of the frontedit cost remains. Named
  cause: the dynamic band sits just before the final user turn, so the
  band + final turn always re-evaluate, and the quarantined copy adds
  assembled tokens (789 vs 700 count). A future v4 could append dynamic
  content after the final user turn (trailing note) to approach tail-only
  cost — recorded as a design note, not built here.
- Layer resend floor 73.1 ms == stock 74.8 ms: layer assembly is
  byte-deterministic for identical input; the layer itself costs no cache.

## Dynamic-injection legs (prompt_eval_ms per turn)
| leg | turn 1 | turn 2 | turn 3 |
|---|---|---|---|
| stock dynfront | 5732.4 | 7300.9 | 8759.9 |
| stock dyntail | 5812.5 | 7355.2 | 2824.9 |
| layer dynfront | 6743.8 | 8263.2 | **3794.9** |
| layer dyntail | 6666.3 | 8212.8 | 3706.7 |

- Layer dynfront ≈ dyntail on every turn: quarantine equalizes front vs
  tail injection (matches the v1 count finding).
- Stock dynfront never gets relief (turn 3 still 8759.9); layer dynfront
  turn 3 is 3794.9 — **2.3x faster** once the assembled prefix stabilizes.
- Named artifact (both legs, both instruments): the harness resends
  FIXED_REPLY as the assistant turn while the runner cached the model's
  generated tokens; the divergence inflates turns 1–2 everywhere equally.
  It does not change the front-vs-tail comparison.

## Caveats
Shared box: load rose ~1.9 (stock run) → ~6.5 (layer run, Samverk active),
so cross-leg absolute values are load-contaminated; the verdict rests on
first-exposure legs, within-run ratios, and the resend floor. A
quiet-window confirmation rerun remains desirable and folds into OM-7's
full gate.

## OM-3 status after this record
Mechanism live (v3 on :11500) + reuse win **partially proven**: front-edit
reprocessing cut ~56% (6.91 s → 3.03 s) and dynamic-front injection
equalized with tail injection; not yet tail-only. Remaining proof
(quiet-window rerun) folds into OM-7. Next slice: **OM-6** robust
deployment (Tailscale login remains Volmarr's own action; the slice works
around it via localhost + LAN per the plan).
