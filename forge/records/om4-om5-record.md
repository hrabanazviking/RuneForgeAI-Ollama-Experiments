# OM-4 + OM-5 record — summary band + fact ledger (2026-11-15, keeper tick 05:31 EST)

## Verdict — battery v3 protocol, overflow scenario (num_ctx 1024, think:false, temp-0 probes)

| build | S-facts (system) | H-facts (early history) |
|---|---|---|
| stock (v3) | 5/5 correct, 0 wrong | **0/4 correct, 4 wrong** |
| layer v1 (OM-2) | 5/5 correct, 0 wrong | **0/4 correct, 4 wrong** |
| **layer v2 (OM-4+OM-5)** | **5/5 correct, 0 wrong** | **4/4 correct, 0 wrong** |

Result file on purplelongship: `~/ollama-memory-forge/harness/battery2-layer-v2b.json`
(base http://127.0.0.1:11501, label layer-v2b). This meets the slice success bar
from the keeper commission exactly: early-history facts 0/4→4/4, wrong 4→0,
system facts held at 5/5.

## Built
- Layer v2: purplelongship `~/ollama-memory-forge/layer/omf_layer_v2.py`
  (sha256 a2848ab7…), stdlib-only, now the live layer on 127.0.0.1:11500
  (v1 retired from the seat after the proof; v1 file kept on disk).
- Assembly: [anchor] → [memory band] → [recent turns verbatim] → [final turn]
  → [post-history core]. Before any turn is shed it is distilled into:
  - **OM-5 fact ledger** — subject-keyed facts with value identity (name/place/
    object). A later statement with a new value for the same subject replaces
    the current line; the superseded line is kept, marked `[superseded]`,
    exactly once. Restatements carrying the same value in other words are
    no-ops. Ledger + compact prose summary are injected as one system band
    right after the anchor.
  - **OM-4 summary band** — the prose summary line in the same band.
- Shedding is batched down to ~70% of the token budget. If distillation of a
  turn throws, the raw turn is kept rather than losing data; raw shed turns
  also stay in the session store (`raw_shed`).

## Bugs found and fixed in-slice (never-leave-a-bug rule)
1. **Ledger churn blow-up (first v2 battery run):** stateless-resend clients
   re-distill the same turns every request; wording-keyed facts flipped
   current↔superseded on every pass (superseded count hit 106, band ballooned
   to ~1,998 est. tokens in a 1,024-token window, server context-shift then
   truncated the prompt; score regressed to S 3/5, H 0/4). Fixed by keying
   facts on (subject, value) instead of wording — re-distillation is now
   idempotent (live run: ledger_facts steady 4, superseded steady 0,
   assembled 528–633 est. tokens vs 872–932 budget).
2. Case-sensitive extraction missed sentence-initial "My dog is called…" /
   "My mother lives in…" — patterns now match case-insensitively.
- Unit proofs (VM + on-device): all 4 H-facts extracted; triple re-apply +
  assistant-restatement re-apply = zero superseded entries; a genuine change
  (dog Bran→Fenris) supersedes exactly once, old line kept marked.

## Still open
- OM-3 paired frontedit metric (next slice in plan order).
- Control-scenario full run through v2 not yet done (by construction v2 is
  identical to v1 when nothing sheds — band stays empty in-window; a full
  control battery is owed at OM-7's full gate).
- Ledger extraction is pattern-based (deterministic, no model cost); the
  plan's model-written per-turn summaries (WHO/WHAT/WHEN/WHERE/WHY/HOW)
  remain a later refinement if OM-7 shows the need.
- Z13 front: ZO-0 still blocked — aesir-gate.service is ACTIVE again on
  purpleraider (PID 543130, started 05:26 EST, ~31 GB RSS, ~960% CPU;
  watchdog timer armed revives it). Per orders Aesir is not touched by this
  campaign; no Z13 bench runs until the gate is fully inactive and load settles.
