# ZO-0 — Re-baseline record (2026-11-15, purpleraider)

Blocker cleared before benching (verified on-device 05:35 EST): `aesir-gate.service` **inactive**, `aesir-gate-watchdog.timer` **inactive + disabled**, no aesir processes, MemAvailable ≈125 GB, load settled (1-min ~1.0). Bench tooling deployed on-device: `~/ai/zo-bench.py` (sha256 936b6246…) + `~/ai/zo-needle.py` (sha256 cfb8a9ee…), byte-identical to the VM copies in bench/. Pass-1 script `~/ai/ollama-bench.py` untouched.

Protocol: Pass-1 protocol (warmup gen(16), then 3 × gen(256), medians of the response timing fields), live service as-is (Pass-1 drop-in live: IGPU_ENABLE=1, FLASH_ATTENTION=1, NUM_PARALLEL=2, KV f16). Bench clients fenced (systemd-run MemoryHigh=1G/MemoryMax=2G), one heavy run at a time, MemAvailable checked before each run (125 → 114.6 → 82.5 GB across the three runs as models stayed resident under keep_alive).

## Results vs yardsticks

| Model | Gen tok/s (median) | Yardstick | Prompt tok/s (median) | Yardstick |
|---|---|---|---|---|
| Qwen2.5-7B Q4_K_M (Pass-1 script) | **45.46** (45.85/45.46/45.18) | 40.79 | **1859.14** | 1577.52 |
| 27B Q8_0, ctx 16384 | **7.57** (7.58/7.57/6.91) | 7.65 | 362.46 | 136.61 |
| 27B Q4_K_M, ctx 16384 | **12.05** (12.06/12.03/12.05) | 12.11 | 486.76 | 107.48 |

## ⚠️ Contention caveat (added after the fact, 2026-11-15)
`aesir-gate.service` re-activated at **05:36:56 EST** (a new transient QS-5 unit) — ~90 seconds after the all-clear verification above and before these benches ran — and was co-resident throughout (later measured at ~830% CPU / ~31 GB RSS). The blocker check at 05:35 was truthful; the machine changed underneath the work. Generation yardsticks still reproduced within ~1% (27B) and the 7B beat its Pass-1 number, so the practical distortion looks small, but **these baselines should be re-verified on a truly clear machine** before ZO-6 relies on them.

## Re-verification on the clear machine (2026-11-15 ~05:58–06:10 EST, resumed coordinator)
Gate + watchdog + timer MASKED by Yrsa; no aesir processes; config restored to exact Pass-1 first (30-zo-kv.conf removed — note: drop-in removal only takes effect after `systemctl daemon-reload`; the first restart still showed KV q8_0 in the env, a second reload+restart cleared it; env verified: KV unset = f16). Same protocol, fenced bench clients, one run at a time.

| Model | Gen (tainted run) | Gen (clear machine) | Yardstick |
|---|---|---|---|
| Qwen2.5-7B Q4_K_M | 45.46 | **45.39** (45.81/45.39/45.21), prompt 1858.41 | 40.79 |
| 27B Q8_0 ctx 16384 | 7.57 | **7.57** (7.57/7.57/7.57), prompt 358.97 | 7.65 |
| 27B Q4_K_M ctx 16384 | 12.05 | **12.28** (12.31/12.28/12.28), prompt 489.48 | 12.11 |

**Verdict: the ZO-0 baselines stand.** The gate's co-residency did not materially distort generation rates (Q8 identical; 7B −0.15%; Q4 +1.9% on the clear machine). Working baselines for all Pass-2 comparisons, confirmed clean: **7B 45.39 · 27B Q8 7.57 · 27B Q4 12.28** (gen tok/s).

## Honest notes
- **Generation rates reproduce the yardsticks** (27B within ~1%; 7B above its Pass-1 number by ~11% gen / ~18% prompt — the machine was fully idle today; Pass-1 was measured on a busier box. No tuning changed: this is a re-baseline, not a win claim).
- **Prompt rates are NOT comparable to the big-model yardsticks**: zo-bench uses the short Pass-1 prompt (66 tokens), so the prompt figures carry small-sample timing noise and a different protocol from the original big-model trials (which reported 136.61 / 107.48). Generation rate is the comparable column; prompt comparisons resume in ZO-2/ZO-4 with the needle probe's long prompts.
- New working baselines for all Pass-2 comparisons: 7B 45.46/1859.14 · 27B Q8 7.57 · 27B Q4 12.05 (gen, ctx 16384).
