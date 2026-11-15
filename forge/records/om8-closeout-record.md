# OM-8 — Close-out (COMPLETE, 2026-11-15, purplelongship)

**Run:** keeper tick 07:21–07:38 EST. The OM-8 remainders named in
om8-record.md were executed under the plain-process pattern required by
Volmarr's 2026-11-15 no-permanent-services law: scratch Ollama (:11499)
and layer v3 (:11500) were started as plain per-tick processes with the
exact env of the struck OM-6 units (scratch: OLLAMA_HOST=127.0.0.1:11499,
OLLAMA_KV_CACHE_TYPE=q8_0, OLLAMA_CONTEXT_LENGTH=16384,
OLLAMA_NO_THINK=true, CUDA_VISIBLE_DEVICES= for the CPU path; layer:
OMF_PORT=11500, OMF_UPSTREAM=http://127.0.0.1:11499, OMF_BIND=127.0.0.1),
health-probed OK (omf-health.sh), and STOPPED when the work finished —
ports :11500/:11499 verified closed, production Ollama (PID 2703,
tailnet-bound) untouched throughout. No service, timer, or watchdog was
created. Harness: om8_gate.py, results in om8-results-plain.json.

**Conditions, stated honestly:** not a quiet window. Load was 2.24 at
gate start and 8–9 during the footprint leg; the Samverk full suite
(PID 3410643, running since 06:11) was co-resident the whole run, and
the gate's own CPU prompt-eval is itself multi-threaded load. The
prompt-eval absolutes below are therefore same-conditions comparisons,
exactly as flagged in the partial record — but they are now reproduced
across two independent runs under comparable contention, which is what
the re-measurement remainder asked for. A true quiet-window absolute
remains obtainable only when the shared machine is idle; it is named
below as an optional remainder, not silently claimed.

## Remainder 1 — 100-turn footprint leg (plain-process re-run): DONE

- 100 turns completed in 745.8 s wall (~7.5 s/turn at num_ctx 1024
  under the load above). The leg that died at 07:12 in the partial run
  ran to completion; om8-results-plain.json was written.
- Shedding works as designed: 180 messages shed across the leg; the
  client-sent history grew to 202 messages while the layer's assembled
  prompt stayed FLAT — est_tokens observed 674–688 at every sample
  (final 674) against a budget of 984, msgs_out held at 24–25.
- The seeded facts survived the whole leg in the ledger
  (ledger_facts=2: brother Tomas, dog Bran), superseded=0, and the
  anchor (42 tokens) stayed pinned (anchor_pinned=true) — never shed.
- Footprint after the leg: layer RSS 29,608 kB (24,164 kB before model
  load — ~5.4 MB of session-store growth over 100 turns); scratch
  serve RSS 76,708 kB; the llama-server runner RSS 4,579,764 kB
  holding the 3,449,961,838-byte model plus KV at ctx 1024,
  size_vram=0 (CPU path confirmed end to end).
- GPU retest: still not possible — 4,538 MiB of the 6,144 MiB card
  remains held by other campaigns' serves, 1,201 MiB free (unchanged
  from the partial run). The OM-0/OM-6 CPU-path verdict stands.

## Remainder 2 — Prompt-eval re-measurement: DONE (reproduced)

Long-prompt leg, this run vs the partial run's contended figures:

| leg | partial run | this run |
|---|---|---|
| stock prompt eval | 969 tok @ 82.9 tok/s | 969 tok @ 87.4 tok/s |
| layer prompt eval | 1,749 tok @ 132.9 tok/s | 1,749 tok @ 134.7 tok/s |
| layer generation | 14.07 tok/s | 12.84 tok/s |

- The layer evaluates ~1.54x faster than stock under identical
  conditions, reproduced. Layer generation 12.84 tok/s sits inside
  OM-0's stock baseline band (12.5–14.4 tok/s): no generation
  regression from the layer, confirmed a second time.
- Multi-turn (8 turns, wall): stock 3.41 s → 3.57 s (flat); layer
  3.60 s → 4.22 s (flat-ish; per-turn detail in the results JSON —
  layer turns 2–5 ran ~5 s at peak load, settling back). Multi-turn
  generation rates: stock 13.5–14.7 tok/s, layer 14.3–14.9 tok/s.
- OM-0's ~1,010 tok/s headline was a different recon protocol (warm
  short-prompt); neither OM-8 run reproduces it for the long-prompt
  leg on this shared machine, and no OM-8 claim rests on it.

## Remainder 3 — Close-out report: THIS RECORD

OM-8 is COMPLETE. With it, the OM road OM-1…OM-8 is complete, and
with the Z13 front's ZO road already complete, the Ollama Memory
Forge campaign's two commissioned roads are both done.

Campaign verdict against Volmarr's success terms (purplelongship):
(a) memory efficiency — assembled context held flat (~0.68k tokens)
across a 100-turn chat at a 1k budget while history grew unbounded;
KV q8_0 on the scratch instance; layer store growth ~5.4 MB per
100 turns. (b) speed — no generation regression (12.84–14.07 tok/s
vs the 12.5–14.4 stock band); prompt eval ~1.54x stock same-conditions;
the OM-3/OM-7 reuse win (front-edit reprocessing cut ~56%,
dynfront turn 3 2.3x) stands as the headline speed proof. (c) character
kept — battery v3 overflow: stock loses the early facts (0/4 correct /
4 wrong) while the layer holds S 5/5 + H 4/4 correct / 0 wrong
(OM-7 full gate), and the anchor stayed pinned through all 100
footprint turns. (d) robustness — the stack now runs as tidy
plain-process start/stop under the no-services law; the health probe
is an API-level check run per tick, not a resident timer. (e) accuracy
— the OM-7 gate numbers above; the fact ledger's supersede lifecycle
kept marked history, with 0 superseded-as-current incidents in any run.

## Named remainders (not blockers; Volmarr's word or a quiet window)

1. v4 trailing-note design (from om3-reinstrument-record.md): the
   quarantined dynamic band still costs ~2.1 s of reprocessing on
   first exposure; a v4 could append dynamic content AFTER the final
   user turn (trailing note) to approach tail-only cost. Design note
   only — not built.
2. A true quiet-window absolute prompt-eval measurement, only when
   purplelongship is genuinely idle (no co-resident suite).
3. OM-6's LAN-exposure step stays moot under the no-services law
   until a client need and Volmarr's word revive it.
4. The ZO-5 bridge build (Anchor Layer on purpleraider) stays gated
   on Volmarr's word, as recorded in z13/STATE.md.
