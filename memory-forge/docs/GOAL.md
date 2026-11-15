# Ollama Memory Forge — GOAL

**Commissioned:** 2026-11-15 ~00:46 EST by Volmarr (voice call). **Seat:** purplelongship (gadget homelink-61753c). All build/test/bench work runs on the laptop via device.invoke; the VM is coordination only.

## Volmarr's commission (his words)
"Take Ollama and make it so it handles memory much more efficiently — completely modify/improve it so it just works a lot better, faster, handles the memories efficiently, and also keeps the character information in the memory and doesn't lose that."

Scope expansion (2026-11-15 ~00:47 EST): **accuracy is co-equal** with speed/efficiency/robustness — "less hallucination by the way we use memory," headline bar: "super much more accurate, more fast, better, more efficient in all ways, more robust." Plus a **research mandate**: sweep all his projects (incl. the Norse game-engine research line) for memory/speed ideas before finalizing the slice plan.

## The two memory laws (from his 2026-11-14 Voxta rulings, now for Ollama itself)
1. The character prompt lives **anchored** in memory and **cannot be pushed out**, however long the chat runs.
2. Resident character context is **not reprocessed every turn**.

## Success (his terms)
Ollama on purplelongship that:
- (a) uses memory (RAM/VRAM + context) efficiently,
- (b) is measurably faster than the stock baseline (same machine) on a realistic multi-turn character-chat workload,
- (c) keeps character information resident and un-losable across arbitrarily long chats — **proven by test**,
- (d) serves robustly,
- (e) is measurably **more accurate**: fact-retention/consistency battery over long chats, identity consistency across window overflow, stable-order memory presentation. Every memory-mechanism slice states which failure it removes (lost anchor, re-ordered recall, truncated facts, stale/superseded facts presented as current).

## Laws
- No Docker ever. Repo creation is Volmarr's alone — fork trees stay local on purplelongship; report repo needs to Yrsa.
- README.md files are never overwritten anywhere.
- Never leave a discovered bug unfixed (fix in scope or record as immediate next work).
- Laptop is SHARED (Samverk + Rúnmál shell campaigns): serialize heavy runs, never disturb their processes/worktrees, keep GPU use modest (RTX 2060, 6 GB).
- Purpleraider untouched (paused; its Ollama is a different machine's tuned setup).
- Clean-room: AGPL sources (SillyTavern study) = behavior/notes only, ideas in our own words.

## State (2026-11-15 ~01:25 EST)
- OM-0 recon: COMPLETE — hidden_files/recon-om0.md. Headlines: production service silently unreachable (ghost tailnet bind; Tailscale logged out — his account action); overflow kills the character (1/6 identity probes after overflow; num_keep alone does not save her); prefix reuse collapses on any early-token edit; clean speeds ~1,010 tok/s prompt eval / ~13–14 tok/s gen (CPU, 4.6B Q2_K, shared GPU); flash attention = no-op on the CPU path.
- Research sweep: COMPLETE — research-norse-engine.md (NorseSagaEngine identified, 24 ideas), research-local-projects.md (16 ideas), research-github.md (162+2 repos swept, 62 flagged).
- IDEAS DOSSIER: FILED — hidden_files/IDEAS_DOSSIER.md. Architecture decision: session/anchor layer in front of stock Ollama first; his GitHub `ollama` fork (2026-08-14) is the second road.
- Slice plan: FILED — hidden_files/plan-om1-om8.md (OM-1 harness+battery → OM-8 speed/footprint gate).
- Next: OM-1 build.
