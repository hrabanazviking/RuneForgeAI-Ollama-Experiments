# ZO-4 — Big-model trials under the tuned config (2026-11-15, purpleraider)

Tuned config for all trials: Pass-1 drop-in (untouched: IGPU_ENABLE=1, FLASH_ATTENTION=1) + KV q8_0 (30-zo-kv.conf) + NUM_PARALLEL=4 (50-zo-parallel.conf). Protocol unchanged (Pass-1: warmup + 3× gen(256), medians; needle: ~8.8k tokens, fact at ~50% depth, think:false).

| Trial | Result | Yardstick / reference | Reading |
|---|---|---|---|
| 27B Q8_0 needle @8,809 tok | **PASS** ('417'), prompt **298.00 tok/s** | 27B Q4 f16 needle: PASS, 279.15 | best 27B needle rate measured; q8_0 KV quality intact on the Q8 weights too |
| 27B Q4_K_M gen | 12.22 tok/s (ZO-2, same config family) | yardstick 12.11 | at/above yardstick |
| 27B Q8_0 gen | 7.57 tok/s (ZO-2, same config family) | yardstick 7.65 | within ~1% |
| 40B Q8_0 gen | **5.13 tok/s** (5.13/5.12/5.13), load 16.49 s cold | yardstick 5.19 | −1.2% = noise; the 40B is weight-bandwidth-bound, KV/parallel tuning does not move solo gen — honest negative for this model |
| 40B needle @8,809 tok | **PASS** ('417'), prompt **198.50 tok/s** | first needle ever on the 40B | long-context recall intact under q8_0 KV |

Notes:
- The 40B was trialled after a service restart (clean pool, MemAvailable ~125 GB); resident size ~43 GB with its q8_0 KV at ctx 16384.
- Solo generation across the fleet is unchanged-to-slightly-better under the tuned config; the tuned config's wins are elsewhere: prompt processing (q8_0), concurrency (parallel=4), footprint (KV halved), and residency behavior (keep-alive, ZO-3).
- No trial showed a quality regression: every needle passed under the tuned config (27B Q8, 27B Q4, 40B; the 7B passed at q8_0 in ZO-2).
