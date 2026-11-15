# OM-8 — Speed & footprint gate (PARTIAL, 2026-11-15, purplelongship)

**Run:** keeper tick, fenced transient unit `omf-om8-gate.service`
(MemoryHigh=6G/MemoryMax=8G), harness `om8_gate.py`. Conditions were NOT quiet:
load average reached 7.56 with the Samverk full suite co-resident (running since
06:11) — absolute prompt-eval rates below are same-conditions comparisons only,
not quiet-machine absolutes, and are flagged as such wherever quoted.

## Completed legs

**Long-prompt eval + generation** (warm page cache, unseen measure prompt,
model gemma4viking4b, CPU path):
- Stock (:11499 direct): 969 prompt tok at **82.9 tok/s**; generation sample too
  small to quote (2 tok).
- Layer v3 (:11500): 1,749 prompt tok at **132.9 tok/s** (the layer leg's count
  includes its assembled warm-turn + anchor context); generation 32 tok at
  **14.07 tok/s** — inside OM-0's stock baseline band (12.5–14.4 tok/s):
  **no generation regression from the layer.**
- Both legs' prompt-eval rates sit far below OM-0's ~1,010 tok/s — the shared
  contention above is the standing explanation (both legs suffered it; the
  layer still evaluated ~1.6× faster than stock under identical conditions).
  A quiet-window absolute re-measurement remains owed and is named below.

**Multi-turn latency** (stateless resend pattern, 8 turns, wall seconds):
- Stock: turn 1 = 3.56 s, turn 8 = 3.58 s (flat — stock prefix reuse works when
  the prefix is untouched, exactly as OM-0 found).
- Layer: turn 1 = 3.74 s, turn 8 = 4.40 s (flat-ish; small assembly overhead on
  short turns under contention; the layer's reuse win lives in the OM-3/OM-7
  paired-duration numbers, not in this short-turn wall clock).

**Footprint (pre-run, measured):** layer process RSS 27,028 kB; scratch Ollama
RSS 34,688 kB (before model load). GPU retest: NOT freed — 4,538 MiB of the
6,144 MiB card still held by other campaigns' serves, 1,201 MiB free; the
CPU-path verdict from OM-0/OM-6 stands unchanged.

## Interrupted leg — and why

The 100-turn footprint/shedding leg died at 07:12:28 EST with
`RemoteDisconnected`: **at ~07:11 EST Volmarr ruled that no agent-made service
may live on his machines** (the no-permanent-services law), and the main session
struck OM-6's user services (omf-scratch / omf-layer / omf-health) on the spot —
stopped, disabled, unit files removed, :11500 closed, verified by this keeper
at 07:13 EST (production Ollama PID 2703 untouched). The gate script died with
its upstream; `om8-results.json` was never written, so per-turn multiturn detail
beyond the journal summary lines above does not exist and is not reconstructed here.

Per the clarified law, the campaign now runs its layer/scratch as **plain
per-tick processes** (started for the job, stopped after). The keeper did NOT
restart anything this tick — the strike was minutes old and the main session
was mid-rewrite of the campaign's orders.

## Named remainders (immediate next work, in order)
1. OM-8 footprint leg re-run under the plain-process pattern: start scratch +
   layer as plain processes, run the 100-turn shedding leg + RSS/KV/store
   measurements, stop both after. Includes the v4 trailing-note follow-up note
   for the close-out report.
2. Quiet-window absolute prompt-eval re-measurement (stock vs layer) when the
   shared machine is calm, to replace the contention-flagged figures above.
3. OM-8 close-out report (final campaign report) once 1–2 land.
OM-6's deployment form is superseded by the 2026-11-15 no-services law: its
health-probe idea survives only as a per-tick plain-process check; the LAN
exposure step is moot until a client need and Volmarr's word revive it.
