# ZO-6 — Final gate + Pass-2 tuning record (2026-11-15, purpleraider)

**Final tuned config (live on-device, env verified 2026-11-15 ~07:06 EST by the keeper):**
- `20-tuning.conf` — Pass-1, UNTOUCHED: OLLAMA_IGPU_ENABLE=1, OLLAMA_FLASH_ATTENTION=1, OLLAMA_NUM_PARALLEL=2 (overridden below).
- `30-zo-kv.conf` — OLLAMA_KV_CACHE_TYPE=q8_0 (ZO-2).
- `50-zo-parallel.conf` — OLLAMA_NUM_PARALLEL=4 (ZO-3).
- `60-zo-keepalive.conf` — OLLAMA_KEEP_ALIVE=30m (ZO-3 recommendation, added at ZO-6 start with the restart logged in STATE.md before it happened).
- Running env confirmed: IGPU_ENABLE=1, FLASH_ATTENTION=1, NUM_PARALLEL=4, KV_CACHE_TYPE=q8_0, KEEP_ALIVE=30m, MODELS=/mnt/vault/models/ollama.
- Rollback for all of Pass 2 = delete the three ZO drop-ins + daemon-reload + restart. Nothing else was changed.

## Final measurement set (run under exactly this config, 2026-11-15 06:36–06:40 EST)
Protocol unchanged: Pass-1 warmup + 3 × gen(256), medians of the bench tool's own
MEDIAN lines (journal units zo-final-7b / zo-final-q4 / zo-final-q8, re-read by the
keeper this tick). An earlier 7.52 tok/s figure for the 27B Q8 was a slot-timing
reading; the bench median 7.58 governs.

| Model | Pass-1 yardstick gen | Clean ZO-0 baseline gen | FINAL tuned gen | Final prompt |
|---|---|---|---|---|
| Qwen2.5-7B Q4_K_M | 40.79 | 45.39 | **44.91** (45.41/44.91/44.81) | 1831.35 |
| 27B Q4_K_M ctx 16384 | 12.11 | 12.28 | **12.24** (12.26/12.24/12.22) | 482.79 |
| 27B Q8_0 ctx 16384 | 7.65 | 7.57 | **7.58** (7.58/7.58/7.55) | 351.32 |

Solo generation under the final config reproduces the clean baselines within ~1%
(7B −1.1%, Q4 −0.3%, Q8 +0.1%) — the tuned config costs nothing on solo gen, as
designed: its wins are concurrency, prompt processing, footprint, and residency.

## Pass-1 vs tuned — where the wins actually are
| Axis | Pass-1 | Tuned (Pass-2) | Source |
|---|---|---|---|
| 4-stream aggregate (27B Q4) | 22.41 tok/s (parallel=2, two waves) | **37.27 tok/s** (parallel=4) | ZO-3 |
| KV footprint @27B ctx 16384 | ~2176 MiB (f16) | **1088 MiB (q8_0)** — halved | ZO-2 |
| 7B needle prompt rate | 839.17 tok/s (f16) | **1001.93 tok/s (q8_0, +19%)** | ZO-2 |
| Idle-model reload tax | 5m keep-alive: cold-ish reloads in chat | **30m keep-alive**; warm reload 1.03 s (7B) / 5.35 s (27B Q8) | ZO-3 |
| Needle quality | f16 baselines PASS | q8_0: 7B / 27B Q4 / 27B Q8 / 40B all PASS | ZO-2/3/4 |
| Solo gen | yardsticks above | unchanged within noise (bandwidth-bound) | ZO-4/6 |

## Honest negatives (kept, not buried)
- **ZO-1: ROCm cannot run.** Ollama's official ROCm pack bundles ROCm 7.2.1, below the 7.2.3 gfx1151 safety floor. Vulkan stays; re-open when Ollama ships ≥7.2.3.
- **KV q4_0 rejected** as a global default: deterministic 7B needle failure (degenerate repetition at temperature 0). KV type must be per-model policy.
- **40B is tuning-neutral:** gen 5.13 vs yardstick 5.19 — weight-bandwidth-bound; no Pass-2 lever moves solo gen on this machine.
- **Flash attention stays ON** (Pass-1 was right): OFF was a gen wash and slower on the 7B needle prompt (775.98 vs 839.17).
- **Silent middle-cut found (ZO-2):** stock Ollama truncates over-long prompts in the middle with only a journal WARN (`truncating input prompt, keep=4`) — carried into the ZO-5 bridge note as a design requirement for the Anchor Layer.

## ZO road verdict
ZO-0…ZO-6 COMPLETE. The Z13's Ollama is left in the final tuned config above.
The remaining bridge work (deploying the Anchor Layer on this machine) is gated
by ZO-5's own build gates, including Volmarr's word — it is not part of this road.
Aesir pause guard at this tick: all three units MASKED, *.qs5-paused preserved,
no aesir/qs5 processes — no guard action needed.
