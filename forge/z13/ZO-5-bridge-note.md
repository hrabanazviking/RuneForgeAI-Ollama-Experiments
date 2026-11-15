# ZO-5 — Bridge design note: the Anchor Layer on purpleraider (2026-11-15)

**Status: DESIGN ONLY.** Nothing built, nothing deployed. The layer's fact-ledger half (OM-4/OM-5) is still in flight on purplelongship; this note designs the Z13 deployment so the build slice can start the day the purplelongship battery proves the ledger.

## What already exists (purplelongship, OM-2)
A stdlib-only Python HTTP service (`omf_layer.py`) sitting in front of a stock Ollama. Per chat request it assembles: **[pinned anchor = all system content] → [history, whole turns shed from the front-middle under a token budget] → [final user turn] → [post-history identity core: first 280 chars of the anchor, as a trailing system message]**, and sets num_keep ≥ anchor tokens + 16 so the runner's front-shift can never evict the anchor. It keeps a canonical session copy (extension adopt / rewind reset / divergence adopt), estimates tokens conservatively (chars/3.5 + 6/msg), relays streaming, passes non-chat paths through untouched, and answers /omf/health. Proven there: character/system facts hold 5/5 through window overflow where stock Ollama confabulated 4/4 early-history facts.

## The Z13 finding this design must answer (ZO-2)
When a prompt exceeds the per-sequence context, **stock Ollama cuts the middle out itself** — keeps head + tail, drops the center, WARN line in the journal only (`truncating input prompt limit=8194 prompt=17627 keep=4`), nothing in the API response. Both test models then answered, honestly, that the (cut) fact was never in the text.

Design consequences:
1. **The layer must own the budget end-to-end.** Its assembled prompt must always fit the negotiated num_ctx with margin, because the stock fallback shedding policy is the worst one possible: silent, position-based, fact-blind — and it would cut exactly the region where the layer places its ledger/summary band. Rule: assembled_tokens ≤ num_ctx − reserve (reserve ≥ 512) is a hard invariant, enforced by the layer's own estimator before every send.
2. **The layer gains a second job: truncation guard.** Even for requests it does not assemble (direct API clients), a front proxy can measure the prompt against the window and refuse/flag overflow loudly (log + response header) instead of letting the runner silently middle-cut. Silent context loss becomes a visible event.
3. **num_ctx negotiation is part of the contract.** Clients that never set num_ctx get the server default; the layer should pin an explicit num_ctx per session from its own budget table (below), not inherit whatever a client happened to send.

## Why the Z13 changes the budgets, not the design
The layer's mechanisms are machine-independent; its budgets are not. purplelongship works around a 6 GB discrete GPU. purpleraider has ~128 GB unified memory, a 100 GiB GTT cap, and — per ZO-2/ZO-3 — q8_0 KV at ≈1088 MiB per 16k-context slot on the 27B (≈2176 MiB at 32k, ≈4352 MiB at 64k), with the whole three-model fleet resident in ~57 GB. Consequences:
- A **32k working window is cheap** here (27B KV ~2.2 GB at q8_0); 64k is affordable for a single chat slot. The shedding threshold that dominates purplelongship design barely binds here — the ledger band triggers later and less often, but the anchor law matters just as much: overflow still arrives in any long-enough conversation, and the middle-cut is waiting when it does.
- NUM_PARALLEL=4 (ZO-3) means up to four assembled sessions concurrently; the layer's per-session canonical copies must be keyed and isolated accordingly (they already are, by session reconciliation).
- Keep-alive 30m (ZO-3) + layer-held sessions align: neither the weights nor the conversation state should evaporate between messages.

## Proposed deployment shape (when built)
- A real systemd unit `ollama-anchor-layer.service` (this machine's proven pattern — never a transient unit), running the layer as user volmarr, listening on **127.0.0.1:11500** (same port as purplelongship, for one mental model), upstream = the production Ollama at 127.0.0.1:11434. Production Ollama itself is **not modified** — the layer is a pure proxy in front; the tuned drop-ins stay as they are.
- Clients (Voxta's OpenAI-compatible service entry) point at the layer's port instead of 11434. Rollback = repoint the client back to 11434 and stop the unit; nothing else to undo.
- Failure posture (decision for the build slice, recommendation recorded): non-chat paths already pass through. For chat paths, if the layer itself fails mid-request it should **surface the error, not silently bypass** — a silent bypass recreates the exact unanchored failure the layer exists to prevent. Availability is protected by systemd Restart=on-failure + the /omf/health endpoint, not by quiet degradation.
- Resource fence like every service on this box: MemoryHigh/MemoryMax sized to the layer's session store, and the session store itself bounded (max sessions + max tokens per canonical copy, LRU eviction with a log line — never silent).

## Build gates (all required before a Z13 build slice opens)
1. OM-4/OM-5 proven on the purplelongship battery: overflow early-history facts 4/4 correct / 0 wrong, system facts 5/5 held.
2. The zo-needle battery re-run **through** the layer on purpleraider (the probe is port-agnostic; point it at :11500), including a deliberate over-window probe proving the truncation guard fires and the anchor survives.
3. Volmarr's word — deploying the layer changes what Voxta talks to, which is his call, in a sitting where he can test the chat himself.

## Open questions for the build slice
- Session identity: how does the layer key sessions for Voxta's OpenAI-compatible calls (which may not send a stable session id)? Fallback: key by (model + anchor hash) with the divergence-adopt rule — needs a proof against Voxta's actual request pattern.
- Estimator calibration for the heretic models' tokenizer (chars/3.5 was calibrated on the purplelongship bench model; re-derive against the 27B's real prompt_eval_count, which zo-needle already reports).
- Does the truncation guard belong in the layer or in the eventual fork? (Layer first — it is deployable without touching stock Ollama; the fork inherits the rule later.)
