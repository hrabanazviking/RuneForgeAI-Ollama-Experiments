# OM-6 — Robust service deployment (purplelongship) — CORE LANDED

**Date:** 2026-11-15 keeper tick (~06:33–06:45 EST). **Seat:** purplelongship.
**Scope honoured:** production Ollama (system service, tailnet-bound
100.67.240.22:11434) untouched; Tailscale login remains Volmarr's own
action. The forge stack (scratch instance + layer) is what got deployed.

## Before
Scratch Ollama (:11499) and layer v3 (:11500) were bare processes (PPID 1,
no restart on failure, no health probing). Five orphaned llama-server
runners from dead scratch parents (00:59–01:54 era) held ~1.0 GiB VRAM +
~14 GiB RAM between them.

## Landed
- **Managed user services** (linger=yes, enabled, Restart=on-failure):
  `omf-scratch.service` (ollama serve, OLLAMA_HOST=127.0.0.1:11499,
  KV q8_0, OLLAMA_CONTEXT_LENGTH=16384 — the env this build actually
  reads, per plan; OLLAMA_NO_THINK=true matching production) and
  `omf-layer.service` (layer v3, OMF_UPSTREAM/OMF_PORT/OMF_BIND env).
  Unit files banked under forge/deploy/.
- **API-level health probe**: `omf-health.sh` + `omf-health.timer`
  (every 2 min) curls scratch /api/version and layer /omf/health —
  answers, not process liveness (the ghost-bind lesson).
- **OMF_BIND**: layer bind address is now env-driven (default
  127.0.0.1, byte-compatible behaviour); the LAN-exposure step below
  uses it.
- **Orphan cleanup**: the 5 dead-parent forge runners were terminated;
  no other campaign's process was touched (the two large VRAM holders
  are Aesir serves on :18434/:18435 — left alone).

## Found + fixed in-slice: GPU OOM on the shared card
First smoke through the service-managed scratch died: cudaMalloc OOM
allocating a 125 MiB compute buffer. VRAM audit: 6,144 MiB total,
4,538 MiB held by the two Aesir serves + orphans, 143 MiB free. The
forge's OM-1…OM-5 numbers were always produced on CPU runners
(paired2 runner: -ngl 0, --load-mode none). Fix: the scratch service
pins **CUDA_VISIBLE_DEVICES=** (CPU path) — deterministic benching on
a shared 6 GiB card; GPU offload retest stays in OM-8 per the plan,
if VRAM has freed by then.

## Proof
- Both services active + enabled; layer `systemctl --user restart`
  → /omf/health ok again (restart resilience).
- End-to-end chat through :11500 (service-managed): done in 14.0 s
  including 8.8 s cold CPU model load; prompt_eval 49 tok / 3.51 s,
  generation 36 tok / 1.70 s (~21 tok/s). Correct in-character reply.
- omf-health.sh: "OK scratch+layer answering".

## Remaining OM-6 step (named, not hidden)
LAN exposure of the layer for real clients: set OMF_BIND to the LAN
address (192.168.50.40) — trade-off to settle first: Python's
ThreadingHTTPServer binds ONE address, so a LAN-only bind breaks the
loopback health probe (probe would move to the LAN address), while
0.0.0.0 keeps both but widens exposure to every interface. Mechanism
is built; the choice is one env line + restart when Volmarr's client
need calls for it. Everything else in OM-6 is done.

## Next
OM-7 full gate (stock vs forged battery, incl. the OM-3 quiet-window
duration rerun folded in), then OM-8 speed/footprint gate.
