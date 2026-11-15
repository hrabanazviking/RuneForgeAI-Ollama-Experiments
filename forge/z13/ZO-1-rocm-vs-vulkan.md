# ZO-1 — ROCm vs Vulkan head-to-head (2026-11-15, purpleraider)

## Verdict: CANNOT RUN AS DESIGNED — Ollama's ROCm bundle is ROCm 7.2.1, below the gfx1151 safety floor. Vulkan stays.

## Evidence (all verified from the binaries, nothing assumed)
- Downloaded Ollama's official ROCm tarball for the installed version: `ollama-linux-amd64-rocm.tar.zst` from the v0.40.16 GitHub release (1,053,876,146 B). **sha256 verified against the release's own sha256sum.txt**: `50ba6b7d9f4ae9b143c5c20496bf82be597dab0a06a50276b637e22150226f9b` ✓. Kept at `~/ai/ollama-rocm/` on-device (tarball + sums + extracted `dist/`).
- The tarball ships **only** the backend directory `lib/ollama/rocm_v7_2/` (no binary — it is an add-on pack for the standard install).
- **Bundled ROCm version = 7.2.1**, proven three ways:
  1. Directory name: `rocm_v7_2`.
  2. Every bundled library carries AMD's 70201 build stamp (= 7.02.01): `libamdhip64.so.7.2.70201`, `librocblas.so.5.2.70201`, `libhipblas.so.3.2.70201`, `libhipblaslt.so.1.2.70201`, `libhsa-runtime64.so.1.18.70201`, `librocsolver.so.0.7.70201`, `libroctx64.so.4.1.70201`.
  3. Runtime query against the bundled lib (ctypes, no GPU work): `hipRuntimeGetVersion` → raw 70253211 (7.02 series).
- **No newer bundle exists**: v0.40.16 is Ollama's latest release (checked the releases API the same morning), so there is no Ollama ROCm pack at 7.2.3+ to substitute.

## Why no bench was run
The standing rule for this chip (Aesir campaign finding, carried in this workstream's brief): **ROCm 7.2.1 has a hipMemcpy defect on gfx1151; 7.2.3+ is the floor.** The official bundle is exactly 7.2.1. Running it would (a) risk the GPU-hang crash class this machine is known for, and (b) produce numbers that could not be trusted anyway — a memcpy defect can silently corrupt the very outputs a benchmark measures. A comparison number bought that way is worth nothing and could cost a hard crash on Volmarr's daily machine.

## Disposition
- **Vulkan remains the backend** for Ollama on the Z13 (it is also what Pass 1 shipped and what the ZO-0 baselines measure).
- The verified tarball stays on-device at `~/ai/ollama-rocm/` so the head-to-head can run the day Ollama ships a ROCm ≥7.2.3 bundle — re-check the bundled version stamps before any future run, same method as above.
- Re-open trigger: a future Ollama release whose rocm pack stamps ≥70203 (or a rocm_v7_3+ directory).
