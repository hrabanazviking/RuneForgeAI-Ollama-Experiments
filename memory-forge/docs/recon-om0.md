# OM-0 Recon — Ollama on purplelongship (measured 2026-11-15, ~00:47–01:10 EST)

All numbers measured live on purplelongship this session unless marked otherwise. Bench harness scripts: /tmp/omf_bench.py, /tmp/omf_overflow.py, /tmp/omf_probe3.py, /tmp/omf_fa.py on the laptop; outputs in /tmp/omf_*_out.log.

## 1. What exists today

- **Binary:** /usr/local/bin/ollama, 51 MB ELF, built Aug 14 (from source — `/api/version` reports **"0.0.0"**, i.e. an unstamped dev build). Source vintage ≈ late-2025 Ollama: Go server + in-process llama.cpp slot runner (`slot operator()`, `model_recommendations.go`, web_search/web_fetch experimental routes in the route table).
- **Service:** systemd `ollama.service`, enabled, running since 2026-11-01 (PID 2703). Drop-ins set:
  - `OLLAMA_HOST=100.67.240.22:11434` (tailnet-only bind)
  - `OLLAMA_NUM_CTX=131072`, `OLLAMA_KV_CACHE_TYPE=q8_0`
  - `OLLAMA_NO_THINK=true`
- **ROBUSTNESS FAILURE #1 (found, not fixed — production service):** Tailscale on purplelongship is **logged out**; the tailnet IPv4 address no longer exists on any interface, so the service is bound to a ghost address and **completely unreachable** (TCP connect fails; journal shows last real traffic 2026-11-14 06:37, only internal cache-sleep lines since). The process looks "up" to systemd while serving nobody. Also: the server-config log of a fresh instance shows `OLLAMA_CONTEXT_LENGTH:0` — the `OLLAMA_NUM_CTX` env in the drop-in does **not** map to this build's context-length setting, so the "128k" tuning is very likely **not in effect** (embed slots in the Nov 14 journal ran at n_ctx_slot=2048; the chat model ran at its baked 16000).
- **Models** (~/.ollama/models, 32 GB blobs): b1olmoe 6.9B Q4_K_M (olmoe MoE); two gemma-4-12B Q4_K_M (7.38 GB each); gemma-4-E4B Q8_0 (8.03 GB); and one shared 3.01 GB blob — gemma 4.6B **Q2_K** — wearing four names: gemma4viking, gemma4viking4b, heretic-8k, tripolskypetr/gemma4-uncensored-aggressive. gemma4viking bakes num_ctx=16000, temp 1, top_k 20, top_p 0.95, presence_penalty 1.5.
- **Hardware:** Ryzen 9 4900HS (16 threads), 38 GB RAM (25 GB available at recon), RTX 2060 6 GB — **4.5 GB of VRAM is held by two Aesir serve processes from other campaigns** (do not disturb). 572 GB disk free. No Go toolchain installed; gcc 15.2, cmake 4.2.3, git 2.53 present. No Ollama source tree on the laptop.
- **Actual use:** journal (Nov 14) shows /api/embed traffic (322–524-token prompts, n_ctx_slot 2048) and chat use via the tailnet address — i.e. clients (Voxta et al.) reach it over tailnet when tailnet is up.

## 2. Baselines (scratch instance of the SAME binary on 127.0.0.1:11499, KV cache q8_0 to match production config; production service untouched)

Bench model: **gemma4viking4b** (4.6B Q2_K, 3.01 GB). Load result: **offloaded 0/36 layers to GPU** (the auto-fit found only ~1.1 GB usable VRAM beside the Aesir processes) → all figures below are **CPU inference** on the 4900HS. Stated plainly: this is the honest shared-machine condition at recon time.

| Measurement | Result |
|---|---|
| Generation speed | **12.5–14.4 tok/s** |
| Long-prompt eval, warm page cache, uncached prompt (1,894 tok) | **~1,010 tok/s** (A/B: FA off 1015.5, FA on 1008.5 — see §5) |
| Long-prompt eval, very first prompt after model load (cold page-in) | 56.7 tok/s — a page-in artifact, NOT steady state; do not quote as the baseline |
| Multi-turn chat, full history re-sent each turn (stateless /api/chat), turn 1 | 240 tok evaluated, 5.2 s total |
| Same, turn 8 (~1,000 tok assembled) | per-turn evaluated grows only ~100 tok/turn while prefix is untouched — see §3 |
| Identity probe before overflow (ship / sister / favourite food) | **3/3 correct** |

## 3. How stock actually handles memory (behavior, measured)

1. **Prefix caching works — narrowly.** Consecutive /api/chat turns with a byte-identical prefix reuse the slot KV: per-turn `prompt_eval_count` grew only ~100 tok/turn (the new material), and a later probe showed `cached n_tokens = 940` of 971. Turn-over-turn reprocessing is therefore NOT the stock behavior *when the prefix is untouched and the same slot serves*.
2. **Any early-token change destroys reuse.** Changing ONE word in the system prompt (the Voxta pattern: dynamic memory/recall injected near the front, reordered blocks, timestamps) raised re-evaluation to 363 of ~570 assembled tokens — prefix matching is strictly ordered; everything after the first changed token is re-evaluated. (Nov 14 purpleraider evidence agrees: slot sim scores 0.002–0.003 vs the 0.100 threshold → cached n_tokens = 0, full re-eval, 52.1 s for 14,712 tok.)
3. **Interleaving is survivable on this build** (probe A): an unrelated /api/generate between chat turns did not cause catastrophic re-eval (289 vs 217) — the runner retained usable cache. Not the main failure.
4. **Overflow kills the character — the central failure.** At num_ctx=1024, once the conversation outgrew the window the slot performed a context shift: `n_keep = 4` (later 5), discarding **509 tokens starting immediately after token 4** — exactly where the character/system block lives. After overflow, identity probes scored **1/6** (five empty answers, one correct). The window sheds its middle-front, never protecting the anchor, and the surviving context is left incoherent (positions shifted, turns vanished mid-stream).
5. **`num_keep` alone does NOT save it.** Repeating the overflow run with `num_keep=320` (the shift log confirms the first 320 tokens were preserved, discarding 351 from the middle) still produced **empty answers to all identity probes**. Physical presence of the character text in the window is not enough once the middle has been torn out and positions remapped — the fix must prevent incoherent overflow, not just pin tokens: shed whole old turns at assembly time, keep anchor + recent turns intact, keep ordering stable.
6. **n_keep default is 4** — four tokens of protection for the entire character card, system prompt, and instructions.
7. **KV cache shifting is disabled for this model** ("KV cache shifting is not supported for this context", gemma4 hybrid/sliding-window) — overflow handling options are narrower than for plain architectures.
8. **Config levers present in this build:** OLLAMA_FLASH_ATTENTION (default **false** — production runs it off), OLLAMA_KV_CACHE_TYPE (production q8_0), OLLAMA_NUM_PARALLEL=1, OLLAMA_KEEP_ALIVE=5m, per-request options num_ctx / num_keep / num_predict, LLAMA_ARG_FIT auto-fit for GPU layers.

## 4. Extension points (where a fix can live)

- **Per-request options** (num_ctx, num_keep) — usable by any client/layer today; insufficient alone (see §3.5).
- **Modelfile parameters** — bake per-model defaults (the viking models already bake num_ctx).
- **Server env/config** — flash attention, KV type, parallel slots, keep-alive, context length (correct env name this build: OLLAMA_CONTEXT_LENGTH).
- **A residency/anchor layer in front of the API** — session-aware prompt assembly: pinned anchor block, stable ordering, whole-turn middle shedding before the prompt ever reaches the runner, three-tier memory (recent turns verbatim / summarized middle / condensed session), fact ledger with supersession. No fork required; works with the stock binary; directly implements both of Volmarr's laws at the level where they can actually be enforced.
- **Source fork of Ollama** (Go server + llama.cpp runner): could pin n_keep per chat, make truncation anchor-aware inside the runner, add session slots. Cost: needs a Go toolchain install + source matching this dev build (version is unstamped 0.0.0 — exact source revision unknown; the vendored ollama/ tree inside NorseSagaEngine may help identify vintage). Heavier; keep as the second road if the layer hits a wall.
- **llama.cpp runner knobs**: cache reuse thresholds, slot policy — reachable only via fork/env, not per-request.

## 4b. ADDENDUM (2026-11-15 ~01:40 EST) — the two overflow paths fail DIFFERENTLY; battery v1 corrected

A decisive follow-up test (one stateless resend whose messages total 1,258 tokens, asked
for system-facts + turn-1 history-facts in a single question, temperature 0):
- At num_ctx=4096 (fits): **all facts correct** (brother Tomas→Greenland, dog Bran, ship, food).
- At num_ctx=1024 (fitted to 1,006 evaluated tokens): the model answered with
  **confabulated replacements** — brother "Bjorn", dog "Fjord" — while ship/food
  (system facts) stayed right.

Refined diagnosis:
- **Stateless resend path (the Voxta pattern):** Ollama's own fitting keeps the
  system/character block and the recent tail, and silently drops early/middle HISTORY.
  The model then hallucinates plausible substitutes for the lost facts — confident false
  memories, worse than silence. This is the accuracy failure Volmarr named.
- **Continuous path (one growing slot conversation):** the §3.4 context shift
  (n_keep=4, discard from the front) tears the character out, as measured.
- **Battery v1 flaw found by its own numbers:** its probes asked only system facts,
  which the resend path preserves — so at temperature-0 probes, stock overflow (2/6)
  matched stock control (2/6) and the scenario stopped discriminating. Battery v2
  (harness/omf_harness2.py) splits S-facts (system) from H-facts (stated in the first
  exchange), uses 2 phrasings per fact, and scores correct / empty / **wrong**
  separately. The layer's OM-4 summary band and OM-5 fact ledger are what must recover
  H-facts; OM-2's anchor work is judged on S-facts + the continuous path.

## 5. Flash-attention A/B (clean protocol: fresh instance per leg, page-in warmup prompt, measure prompt never before seen by that instance)

- FA **off**: warmup long (1,364 tok) 912 tok/s; MEASURE (1,894 tok) **1015.5 tok/s**; gen ~13.
- FA **on**: warmup long 916 tok/s; MEASURE **1008.5 tok/s**; gen ~13.
- **Verdict: flash attention is a no-op on this CPU path** (within noise). It may matter on GPU offload; retest if/when VRAM frees. Two contaminated readings were caught and discarded during recon (a 56.7 tok/s "cold" figure that was really mmap page-in, and a 3,129 tok/s figure that was really a same-instance prompt-cache hit) — the table in §2 uses only the clean protocol.
- Corollary: at ~1,000 tok/s CPU eval, a full 14,712-token re-eval (the Voxta failure case) costs ~15 s on this model class — the pain is real but comes from *how often* full re-evals happen (prefix collapse, §3.2) and from overflow loss (§3.4), not from raw eval throughput. On the 12B models also present, scale accordingly (~3× slower per token).
