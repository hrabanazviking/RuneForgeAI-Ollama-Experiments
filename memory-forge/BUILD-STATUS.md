# Ollama Memory Forge — build status of the banked modifications

**Snapshot date:** 2026-11-15. Banked on Volmarr's direct order (voice call,
2026-11-15 ~05:30 EST: "take our modifications so far and push them up to that
repo — so that's there"). This branch (`yrsa/memory-forge-build`) is a banked
snapshot of the modifications built so far. The living originals remain on
purplelongship (`~/ollama-memory-forge/`); the campaign records live on the VM
(`~/workspace/goals/ollama-memory-forge/`). Copies of those records are under
`docs/` here.

## What the modifications are

**Anchor Layer v1** — `code/layer/omf_layer.py`. A stdlib-only Python HTTP
service that sits in front of a stock Ollama (dev seat: layer on
127.0.0.1:11500, upstream scratch Ollama on 127.0.0.1:11499; the production
Ollama service is untouched). For each chat request it assembles the prompt as:

1. **Pinned anchor** — all system content, always first, never shed.
2. **History** — whole turns shed from the front-middle under a token budget
   when the conversation outgrows the window.
3. **Final user turn.**
4. **Post-history identity core** — the first 280 chars of the anchor repeated
   as a trailing system message (placement is switchable: `OMF_CORE=post|front|off`).

It sets `num_keep ≥ anchor tokens + 16` (stock Ollama's continuous-path
`n_keep=4` front-shift is the anchor-killer this addresses), keeps a canonical
copy of each session and reconciles client resends (extension adopt / rewind
reset / divergence adopt), estimates tokens conservatively at chars/3.5 + 6
per message, assembles streaming requests before relaying them, and proxies
all non-chat paths untouched. Health endpoint: `/omf/health`.

**Measurement harnesses** — `code/harness/`:

- `omf_harness.py` — battery v1: control (8 turns, in-window), overflow
  (12 turns at num_ctx=1024), and frontedit scenarios; six keyword-scored fact
  probes (name, ship, sister, food, wreck, teacher) against the Sigrid
  character card. Results: `battery-stock.json`, `battery-stock-t0.json`,
  `battery-layer-v1.json`.
- `omf_harness2.py` — battery v2: system facts (S) vs early-history facts (H),
  two phrasings per fact, temperature-0 probes, correct/empty/wrong scoring.
  Results: `battery2-stock-v2.json`, `battery2-layer-v2.json`,
  `battery2-layer-v2-fresh.json`, `battery2-stock-v3.json`,
  `battery2-layer-v3.json`.

## What is proven (battery v3, clean harness)

Battery v3 runs with `think:false` (production parity with Volmarr's
`OLLAMA_NO_THINK=true` drop-in) and probe `num_predict` 120. The earlier
v1/v2 "empty" results were a thinking-truncation artifact and are withdrawn —
see `docs/battery-correction-2026-11-15.md`.

| scenario | stock Ollama | Anchor Layer v1 |
|---|---|---|
| control (fits window) | S 5/5, H 4/4, wrong 0 | S 5/5, H 4/4, wrong 0 |
| overflow (num_ctx 1024, stateless resend) | S 5/5, H 0/4 correct, **4 wrong** | S 5/5, H 0/4 correct, **4 wrong** |

In plain words: driven past its context window, stock Ollama keeps the
character/system block but silently drops everything the user said early and
confabulates replacements at a 100% rate. The Anchor Layer holds the anchor
exactly as designed (system facts 5/5 through overflow, no in-window
regression), but v1 sheds early turns without carrying their facts forward,
so it scores the same as stock on early-history facts. That failure is
precisely what the next two slices exist to fix.

## Hash verification of this snapshot

Files were pulled read-only from purplelongship as a tarball (sha256 matched
on-device before transfer) and every file's sha256 was re-verified after
extraction. Outcomes for the two record-named files:

- `code/layer/omf_layer.py` — sha256
  `801f479a92c8028db2a05cb55526a8c7ab439b7eeee738f7a3f12d451a819912` —
  **matches** the OM-2 record exactly; the layer is unchanged since it was built.
- `code/harness/omf_harness.py` — sha256
  `cfbccd65e40f969f400074407022e861dcbc401976c07c1b8c4a3188636a6374` —
  **advanced** from the OM-1 record's `6415a698…`: the in-flight campaign work
  has moved the harness since that record was written. Banked as-is, current
  version.
- `code/harness/omf_harness2.py` — sha256
  `e8f56f95b5fb150d0a500e830bfda7387860b0fe3b81fbde92658248454de7b7` —
  new since the OM-1/OM-2 records (the battery-v2 harness above).

## What is still in flight

OM-4 (summary band) and OM-5 (fact ledger) are being built on purplelongship
now: before any turn is shed, shed turns are distilled into a subject-keyed
fact ledger plus a compact prose summary, injected right after the anchor.
Their success criterion on the battery-v3 overflow scenario is early-history
facts moving from 0/4 correct / 4 wrong toward 4/4 correct / 0 wrong with
system facts held at 5/5. Because that work is in flight, this snapshot may
predate it. Also still owed after that: OM-3's paired frontedit metric, OM-6
robust deployment, OM-7 full gate with repeats, OM-8 speed/footprint gate.
