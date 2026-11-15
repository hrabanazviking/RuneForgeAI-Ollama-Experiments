# IDEAS DOSSIER — Ollama Memory Forge

Distilled 2026-11-15 from the three research sweeps (full detail in research-norse-engine.md,
research-local-projects.md, research-github.md in this folder) and the OM-0 measured recon
(recon-om0.md). Each idea: source → mechanism → how it applies to Ollama here → gain → cost/risk.
The slice plan (plan-om1-om8.md) is built from these.

## The shape the evidence forces

OM-0 measured stock Ollama's failures precisely: (1) overflow discards everything after
token 4 — the character dies (identity probes 1/6 after overflow); (2) num_keep alone does
NOT save her — a torn-out middle leaves the surviving context incoherent; (3) prefix reuse
works only while the prompt's early tokens never change — one word edited in the system
block re-evaluates most of the prompt (the Voxta dynamic-injection pattern); (4) raw speeds
are fine (~1,010 tok/s prompt eval, ~13–14 tok/s gen, CPU, 4.6B Q2_K) — the pain is
repetition and loss, not throughput; (5) the production service is silently unreachable
(ghost tailnet bind) while systemd reports it healthy.

Every one of those is fixable at a **session/assembly layer in front of the stock API** —
and nearly every strong idea in Volmarr's own projects lives at exactly that layer. So the
forge builds the layer first; a source fork of Ollama (his `ollama` fork exists on GitHub,
dated 2026-08-14, the installed binary's build date) stays as the second road for anything
the layer provably cannot do. Engine-level ideas (paged KV, hybrid-state snapshots) are
Aesir's line, not a patch to Ollama's vendored llama.cpp.

## The ideas

### D1. The unpushable anchor, in two parts — Aesir HS-5 + Voxta study + NorseSagaEngine SOTG
- **Mechanism:** (a) a pinned character/system block at the front that the assembler never
  sheds; (b) a short identity core re-asserted AFTER all history every turn
  (post-history slot), composed at serve time, never stored in history, so history growth
  can never push it out. NSE's SOTG adds: a tiny always-first state card (where the scene
  is, who is present, what's unresolved) — position, not volume, keeps a chat grounded.
- **Ollama application:** the layer assembles every request: anchor → state card →
  summaries → recent turns → post-history identity core → user turn. Overflow shedding
  touches only the middle bands, in whole turns.
- **Gain:** delivers the commission's central law; kills the measured 1/6-after-overflow
  failure. **Cost/risk:** low; a few hundred tokens/turn. Keep the anchor to the true
  identity core — everything else belongs in recall.

### D2. Stable-order, append-stable memory injection — Aesir HS-7 + Voxta study
- **Mechanism:** recalled material is admitted whole, in a fixed deterministic order,
  under a token budget; new recalls append at the end instead of reshuffling by this
  turn's relevance score.
- **Ollama application:** the layer's recall band obeys this from day one; per-turn
  reused-token counters are logged so a churn regression alarms immediately.
- **Gain:** high, multiplicative with prefix reuse — it is what lets a memory system
  exist without destroying the cache every turn (OM-0 failure #3). **Cost:** discipline.

### D3. Prefix discipline + session pinning — Aesir HS-1/HS-3/HS-6
- **Mechanism:** token-exact prefix reuse with reused-vs-evaluated counters; a named
  session owns its state across turns; any edit before the tip invalidates from that
  token onward (explicit rule).
- **Ollama application:** the layer keeps one session per character chat, guarantees
  byte-identical prefixes (dynamic content — timestamps, fresh recalls — goes in the
  tail bands, never the front), sets keep-alive so the model/slot stays resident.
- **Gain:** the Voxta-pattern workload stops re-paying the full prompt per turn.
  **Cost/risk:** medium-low; resident sessions pin memory — bounded by D10 budgets.

### D4. Three-tier memory with structured per-turn summaries — NorseSagaEngine (implemented, 1,197 tests on the v2.0 line) + SillyTavern/Voxta studies
- **Mechanism:** recent turns verbatim; older turns replaced by per-turn structured
  summaries (WHO/WHAT/WHEN/WHERE/WHY/HOW + emotion + open thread); the whole session
  condensed above that. Summaries are written when turns age out, incrementally, from a
  saved read-position.
- **Ollama application:** this is what the shed middle becomes — not a hole, a summary
  band. Background summarization runs as separate Ollama calls on the same/small model,
  costed honestly against the quality bought.
- **Gain:** the only idea that answers "the middle of the conversation is gone."
  **Cost/risk:** medium-high; summaries are lossy and can entrench an early misreading —
  mitigated by D5's ledger rules and by keeping raw history in the store, retrievable.

### D5. Fact ledger with an honesty lifecycle + promotion gate — Voxta study + WYRD + NSE2
- **Mechanism:** facts are versioned records with provenance and timestamps. Updates
  supersede (old wording kept, never recalled again); covered facts are absorbed;
  pinning exempts. New extractions enter as *ephemeral candidates* and are promoted to
  canonical only on corroboration/importance thresholds; a write contradicting a
  canonical fact is quarantined, not silently merged. Per-character stores; reads are
  pure (recall never mutates the store) — the Ravens (Huginn/Muninn) disciplines.
- **Ollama application:** the layer's memory store. Canonical facts may feed the anchor;
  ephemeral facts may be recalled but never anchored. Stale-fact haunting and
  one-bad-turn poisoning both die here.
- **Gain:** high for accuracy over weeks-long relationships. **Cost:** medium; the
  extraction/merge pass (D4's pipeline) plus threshold tuning, kept conservative.

### D6. Hybrid recall, not vector-only — bifrost (40/40/20) + NSE scored retrieval + bifrost-viewer (RRF, HyDE)
- **Mechanism:** merge keyword/FTS, semantic, and associative legs by weighted score or
  reciprocal-rank fusion; NSE adds entity-overlap, location-overlap and emotional
  resonance factors with per-category decay; HyDE embeds a short imagined continuation
  when the raw last line is a poor query.
- **Ollama application:** the recall band's ranker. Exact-name hits catch what
  embeddings blur — in character chats, names are the facts that matter most.
- **Gain:** medium-high recall quality for a local, explainable cost. **Risk:** low.

### D7. Budgets before recall — NSE prompt budgeting + MimirAlloc discipline + Aesir measured-fit rule
- **Mechanism:** count tokens with the real tokenizer; reserve anchor + live exchange +
  reply first; memory channels get what remains, per-channel caps, whole entries only.
  Around everything: KV bytes/token, max resident sessions, store caps, eviction order —
  specified up front, measured against reality. No load/bench starts without a
  free-memory check and a fence.
- **Ollama application:** the layer's assembler is a budgeter first and a retriever
  second. **Gain:** prevents "better memory" from quietly meaning "the machine dies at
  hour 3." **Cost:** low as discipline.

### D8. Identity maintenance: drift detection, canonizer, continuity check — NorseSagaEngine (implemented pieces)
- **Mechanism:** every N turns, diff the character's lived history against the card and
  inject a short evolution note as a session delta (card never rewritten); entities the
  model invents are canonized into the store on first mention; a post-generation check
  flags violations of hard facts (deaths, names, boundaries) for repair.
- **Ollama application:** scheduled jobs inside the layer's pipeline. **Gain:** medium;
  attacks self-contradiction, the failure users feel most. **Cost:** low-medium.

### D9. Recall quality is a benchmark, not a vibe — NSE Sprint 5 test shapes
- **Mechanism:** seeded-store suite: precision@k ≥ 0.7, recall < 50 ms @ 1,000 memories,
  superseded facts must never surface, temporal expiry, budget-selection tests — plus
  the campaign's own chat battery (fact retention + identity across overflow).
- **Ollama application:** OM-7's acceptance gate, stock vs forged, same battery.
  **Gain:** makes "more accurate" a number. **Cost:** low.

### D10. One sovereign store beside the engine — OB1 argument + Ravens + ChatIndex/mempalace (lossless-first)
- **Mechanism:** memory lives in one inspectable, portable store that every front-end
  shares; verbatim history is kept under a navigable summary tree — summaries are an
  index, never the only copy.
- **Ollama application:** the layer's store is plain files/SQLite on purplelongship,
  user-readable and user-editable; Ollama stays the engine, the store stays his.
  **Gain:** portability + auditability, per his standing rules. **Cost:** low.

### Noted, not in the first plan
- Elastic memory windows (NSE: retrieval size scales with scene stakes, bounded
  worst case ~2,000 tok) — adopt inside D4/D6 admission if the battery shows fixed
  budgets starving big moments.
- Paged/elastic KV + semantic-anchor checkpoints (Aesir, FreeToken) — engine-level;
  Aesir's road, revisited only if a fork slice is ever opened.
- Hybrid (SSM) state snapshots (Aesir Q35-5) — matters for qwen35-class models served
  by Ollama to Voxta on purpleraider; out of this campaign's purplelongship scope,
  flagged for Yrsa.
- Depth injection (SillyTavern) — recency trick for rotating scene state; use sparingly,
  it fights D2/D3 if placed inside the committed prefix.
- Memory-write injection guard + audit log (NSE Sprint 7) — adopt cheaply in D5:
  stored text is untrusted input on every future injection.
