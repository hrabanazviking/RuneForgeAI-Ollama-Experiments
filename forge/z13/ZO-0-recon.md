# ZO-0 — Recon record (2026-11-15, purpleraider)

## Verified live today (device clock 05:26–05:34 EST)
- **Ollama 0.40.16**, `/usr/local/bin/ollama`; service **active + enabled**, MainPID 2813 (running since Nov 14 boot).
- **Pass-1 drop-in is LIVE** in the running process env: `OLLAMA_IGPU_ENABLE=1`, `OLLAMA_FLASH_ATTENTION=true`, `OLLAMA_NUM_PARALLEL=2`, `OLLAMA_MODELS=/mnt/vault/models/ollama`, `OLLAMA_KV_CACHE_TYPE` unset (f16 default). Drop-in files on disk unchanged: `20-tuning.conf` (Nov 13) + `override.conf` (models path). Stock unit untouched.
- **GPU detection (this boot, Nov 14 19:59):** `inference compute … library=Vulkan … "AMD Radeon 8060S Graphics (RADV STRIX_HALO)" type=iGPU total="104.0 GiB" available="103.7 GiB"` — the 100 GiB GTT cap showing as 104 GiB total. `OLLAMA_VULKAN:true` in server config.
- **Shipped backends:** `cuda_v12/`, `cuda_v13/`, `vulkan/` — **no ROCm/HIP backend in this build** (identical to Pass 1 census). ggml 0.29.0 / llama 0.9.0.
- **System ROCm presence (for ZO-1):** `/usr/bin/rocminfo` exists; HIP libs in `/usr/lib/x86_64-linux-gnu/` report `libamdhip64.so.7.15.0` (version string to be verified against any Ollama ROCm tarball's bundled libs — never assumed). ZO-1 must source Ollama's separate ROCm build; known trap: ROCm 7.2.1 gfx1151 hipMemcpy bug → need 7.2.3+.
- **Model store** (`/mnt/vault/models/ollama`, vault 3.3T free): `qwen3.8-27b-heretic` Q8_0 28 GB · `qwen3.8-27b-heretic-q4` 16 GB · `qwen3.8-40b-heretic` 41 GB · `qwen2.5:7b-instruct-q4_K_M` 4.7 GB (Pass-1 mule) · `qwen2.5:0.5b` 397 MB.
- **Machine:** up 9h35m at last check (booted Nov 14 ~19:59 EST); MemAvailable ~120 GB throughout; GTT cap 100 GiB in force.
- **Bench tooling staged:** Pass-1 script `~/ai/ollama-bench.py` intact on-device; generalized `zo-bench.py` + needle probe `zo-needle.py` written (VM copies in this folder's bench/; deploy on-device when benching opens).

## Re-baseline: BLOCKED (stop condition, not a failure)
The brief's rule: confirm aesir-gate fully inactive before any bench; never kill it; Aesir is not this workstream's to touch.
- 05:26 EST: `aesir-gate.service` **active**, serve PID 543130 (started 05:26 — after the pause order; `aesir-gate-watchdog.timer` still armed/active, fires every 2 min), burning ~10 cores, 31.2 GB RSS; `qs5-soak.service` also active. Load ~10.
- 05:29–05:31: qs5-soak went **inactive**; gate still active, RSS 31.7 GB.
- 05:34: gate process instantaneous CPU = **0 jiffies over 10 s** (fully idle), load 1-min down to 2.34 — but the unit is still `active` and the watchdog timer still armed, so the serve is resident and revivable, **not fully inactive**.
- **Unblock (parent's hand only):** the Aesir stop completes — `aesir-gate.service` stopped and its watchdog timer disabled so it cannot revive — then ZO-0 re-baseline runs immediately: 7B mule via the untouched Pass-1 script, 27B Q8_0/Q4_K_M via zo-bench at ctx 16384, all against the yardsticks (7B 40.79/1577.52; 27B Q8 7.65/136.61; 27B Q4 12.11/107.48).
