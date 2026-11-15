# ZO-2 — Flash-attention + KV-cache tuning (2026-11-15, purpleraider)

## Finding first: Ollama silently middle-cuts over-long prompts (found by the needle probe)
- The needle probe (fact planted mid-prompt) failed on BOTH the 27B heretic and the clean 7B instruct at a ~17.6k-token prompt — both models answered, honestly, that the record was not in the text.
- Server log proves why: `msg="truncating input prompt" limit=8194 prompt=17627 keep=4 new=8194`. When a prompt exceeds the per-sequence context (16384 here), Ollama **cuts the middle out** (keeps head + tail halves of the budget) with only a WARN line in the journal. The planted fact sat in the cut region. Nothing in the API response tells the caller it happened.
- Why it matters for the modification project: this is a silent context-loss mechanism — anything in the middle of an over-long conversation is simply never seen by the model. Directly relevant to the Anchor Layer's reason to exist (ZO-5 bridge note will carry it).
- Probe calibration corrected: the filler pair is ≈38 tokens, not the script's assumed 26; all KV comparisons below use TARGET=6000 → **8,809–8,825 actual tokens**, fact at ~50% depth, inside the 16384 window, no truncation (verified in slot logs).

## Probe correction (recorded, OM-battery discipline)
- First 27B needle (original script) failed because the model spent its 24-token budget on visible reasoning. zo-needle.py now sends `think:false` (VM + device copies updated; device sha256 2ff1c17e…). Transfer lesson: the first redeploy via printf/base64 landed with a slipped character (sha mismatch, same size) — repaired via gadget file.write, whose whole-file sha gate verified the landing. Use file.write for tooling transfers.

## Baselines — KV f16, flash-attention ON (Pass-1 config, untouched)
| Probe | Result | Prompt tok/s |
|---|---|---|
| 7B needle @8,825 tok | PASS ('417') | 839.17 |
| 27B Q4 needle @8,809 tok | PASS ('417') | 279.15 |
| 27B Q4 resident size (ollama ps, ctx 16384) | 18 GB | — |

Gen baselines (ZO-0): 7B 45.46 · 27B Q4 12.05 · 27B Q8 7.57 tok/s.

## KV q8_0 cycle — INCOMPLETE, numbers tainted (do not cite as a verdict)
- Drop-in `30-zo-kv.conf` (OLLAMA_KV_CACHE_TYPE=q8_0) added, service restarted, env verified live. 27B KV buffer under q8_0: **1088 MiB** (K 544 + V 544, 16384 cells) — exactly half the f16 bytes by construction.
- 27B Q4 gen measured 10.99 median (11.71/10.99/10.66) vs f16 baseline 12.05 — **but the run-over-run decline tracks the aesir-gate's co-residency (see STATE.md log: the gate re-activated 05:36:56 EST and was burning ~8 cores), so this is contention, not a KV result.** The q8_0 needle run was stopped mid-flight when the gate was discovered. Cycle must be re-run on a clear machine.

## KV q8_0 cycle — CLEAN RE-RUN (2026-11-15 ~06:11–06:25 EST, resumed coordinator, clear machine)
Drop-in re-added, daemon-reload + restart, env verified live (OLLAMA_KV_CACHE_TYPE=q8_0). All runs fenced, one at a time, MemAvailable ≥87 GB throughout. Baselines are the clear-machine re-verified f16 numbers.

| Measurement | KV f16 (clean) | KV q8_0 (clean) | Reading |
|---|---|---|---|
| 27B Q8 gen tok/s | 7.57 | **7.57** (7.58/7.57/7.57) | identical |
| 27B Q4 gen tok/s | 12.28 | **12.22** (12.24/12.22/12.19) | wash (−0.5%, tight runs, no decline) |
| 27B Q4 needle @8,809 tok | PASS, prompt 279.15 | **PASS, prompt 285.15** | quality holds, prompt +2.1% |
| 7B needle @8,825 tok | PASS, prompt 839.17 | **PASS, prompt 1001.93** | quality holds, prompt +19.4% |
| 27B KV buffer @ctx 16384 | ~2176 MiB (by construction) | **1088 MiB** (verified in the first cycle) | half the bytes |

**q8_0 verdict: generation-neutral, prompt-positive (strongly on the 7B), needle quality intact, half the KV footprint.** The tainted cycle's 10.99 is confirmed as a contention artifact. q8_0 is a keeper candidate for the ZO-6 final config.

## KV q4_0 cycle — COMPLETE (2026-11-15 ~06:26–06:45 EST, clear machine)
Drop-in changed to OLLAMA_KV_CACHE_TYPE=q4_0, daemon-reload + restart, env verified live. Same protocol as the q8_0 cycle.

| Measurement | KV f16 (clean) | KV q8_0 (clean) | KV q4_0 (clean) |
|---|---|---|---|
| 27B Q8 gen tok/s | 7.57 | 7.57 | **7.57** (7.58/7.55/7.57) |
| 27B Q4 gen tok/s | 12.28 | 12.22 | **12.20** (12.22/12.19/12.20) |
| 27B Q4 needle @8,809 | PASS, 279.15 | PASS, 285.15 | **PASS, 276.91** |
| 7B needle @8,825 | PASS, 839.17 | PASS, 1001.93 | **FAIL ×2, 906.41** — answer degenerated to repetition ("It the the the…"), identical on re-run at temperature 0: deterministic |

**q4_0 verdict: REJECTED as a global default.** No speed gain over q8_0 on any measure, and it breaks the 7B's long-context behavior outright on this probe while the 27B still passes — a per-model quality cliff, invisible without a probe. Modification-project lesson (matches the idea ledger's per-model KV policy entry): **KV cache type must be a per-model choice, never one global setting** — q8_0 is the safe aggressive setting; q4_0 only where a needle-class probe has proven the specific model tolerates it.

## Flash-attention OFF comparison — COMPLETE (2026-11-15 ~06:46–07:05 EST, clear machine)
Config: KV back to f16 (30-zo-kv.conf removed), flash forced off via a later-sorting drop-in (40-zo-flash.conf, OLLAMA_FLASH_ATTENTION=0 — systemd drop-in precedence verified in the live env: single FLASH entry, =0). Same measurement set vs the f16 + flash-ON baselines.

| Measurement | Flash ON (f16) | Flash OFF (f16) | Reading |
|---|---|---|---|
| 27B Q8 gen tok/s | 7.57 | **7.54** (7.54/7.54/7.54) | wash |
| 27B Q4 gen tok/s | 12.28 | **12.19** (12.21/12.19/12.18) | wash |
| 27B Q4 needle @8,809 | PASS, 279.15 | **PASS, 279.00** | identical |
| 7B needle @8,825 | PASS, 839.17 | **PASS, 775.98** | flash ON +8.1% prompt |

**Flash verdict: KEEP flash attention ON** (Pass 1 was right). It costs nothing measurable on the 27B at these lengths and buys ~8% prompt speed on the 7B; its advantage should grow with context length.

## ZO-2 SUMMARY (complete 2026-11-15)
1. **Finding:** Ollama silently middle-cuts prompts beyond the per-sequence context (WARN only in the journal) — banked above; carried to ZO-5.
2. **KV q8_0: ADOPT** as the tuned default — generation-neutral, prompt-positive (+19% 7B needle prompt, +2% 27B), needle quality intact on both models, half the KV footprint (1088 MiB @27B/16k).
3. **KV q4_0: REJECTED as a global default** — no speed gain over q8_0, and a deterministic quality cliff on the 7B at ~8.8k tokens. KV type must be per-model policy in the modification project.
4. **Flash attention: KEEP ON.**
Tuned-config candidate for ZO-6: Pass-1 drop-in (untouched) + 30-zo-kv.conf (KV q8_0).

## Machine state left by ZO-2
Ollama service active with drop-in 30-zo-kv.conf (KV q8_0) in place — logged and reversible (delete the drop-in + restart returns the Pass-1 config). No other live-service change was made; 20-tuning.conf untouched throughout.
