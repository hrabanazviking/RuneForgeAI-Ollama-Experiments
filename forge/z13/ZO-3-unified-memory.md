# ZO-3 — Unified-memory tuning (2026-11-15, purpleraider)

Base config for all ZO-3 work: Pass-1 drop-in (untouched) + KV q8_0 (ZO-2 verdict). All changes via NEW drop-ins, daemon-reload + restart, env verified live before measuring. Bench clients fenced, one heavy run at a time.

## NUM_PARALLEL sweep (27B Q4_K_M, ctx 16384, 256-token generations)
Solo reference (ZO-2, q8_0): 12.22 tok/s.

| NUM_PARALLEL | Streams fired | Per-request tok/s | Aggregate tok/s | Wall |
|---|---|---|---|---|
| 1 | 2 | 12.28 (serialized) | 12.17 | 42.06 s |
| 2 (Pass-1) | 2 | 11.33 | 22.14 | 23.12 s |
| 2 (Pass-1) | 4 | 11.40 | 22.41 | 45.70 s (two waves) |
| **4** | **4** | **9.81** | **37.27** | **27.47 s** |

**Verdict: NUM_PARALLEL=4.** Aggregate throughput triples vs solo at a −20% per-request cost; at parallel=2 the same 4-stream job takes 66% longer. Memory cost is not a constraint here: q8_0 KV ≈1088 MiB per 16k slot → 4 slots ≈ 4.4 GB of the 100 GiB GTT cap. For a machine that serves chats + agents concurrently, 4 is the right default; a single-user latency purist could stay at 2 (per-request 11.3–11.4 vs 9.81) — the final config takes 4, and the trade is stated in the tuning record.

## Co-residency (MAX_LOADED_MODELS at default)
All three working models resident at once, no eviction: 7B 7.0 GB + 27B Q4 19.4 GB + 27B Q8 30.9 GB ≈ **57.3 GB** in the unified pool, MemAvailable ~68 GB left over. Warm load times: 0.88 s / 2.30 s / 5.35 s. The whole working fleet fits with room to spare — model-swapping is a non-issue on this machine at these sizes.

## Keep-alive behavior
Verified mechanically: a request with keep_alive=10s unloaded the 7B on schedule (gone from /api/ps at 25 s) while 5-minute models stayed; warm reload cost 1.03 s (7B). Reload costs measured today: 7B ~1 s warm · 27B Q4 ~2.3 s warm · 27B Q8 5.35 s warm / 11.13 s cold (post-restart). With the default 5-minute expiry, an idle chat model pays that tax on the next message — the exact silence-before-first-word pain seen with Voxta. **Recommendation carried to the final config: OLLAMA_KEEP_ALIVE=30m** — on a 128 GB machine whose whole fleet is ~57 GB, holding models resident is nearly free and removes the reload tax from conversation.

## mmap / mlock — negative finding (verified, not assumed)
Enumerated the binary's own config surface (`strings` on /usr/local/bin/ollama, 0.40.16): the OLLAMA_* env family contains **no mmap or mlock knob** (present: CONTEXT_LENGTH, FLASH_ATTENTION, GPU_OVERHEAD, HOST, IGPU_ENABLE, KEEP_ALIVE, KV_CACHE_TYPE, LOAD_TIMEOUT, MAX_LOADED_MODELS, MAX_QUEUE, MODELS, NOHISTORY, NOPRUNE, NUM_PARALLEL, SCHED_SPREAD, VULKAN, …). The runner manages mapping internally; there is nothing to tune and no per-request option resurrects it in this version. Closed as not-applicable.

## Not measured, deliberately
- OLLAMA_SCHED_SPREAD: multi-GPU placement; this machine has exactly one iGPU — a no-op by construction.
- OLLAMA_MAX_QUEUE: no queue saturation observed at 4 streams/parallel 4; left at default.
- OLLAMA_GPU_OVERHEAD: default reservation behavior caused no failure at any load tested (fleet + 40B trials in ZO-4 exercise it further).

## ZO-3 verdicts carried to ZO-6
1. NUM_PARALLEL=4 (drop-in 50-zo-parallel.conf).
2. OLLAMA_KEEP_ALIVE=30m recommended for the final config (to be added at ZO-6 as a drop-in, then proven by the final-gate measurements).
3. KV q8_0 (from ZO-2) + flash ON (Pass-1) stand.
