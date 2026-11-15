# GitHub Sweep — Ollama Memory Forge (research, read-only)

Swept 2026-11-15 via `gh repo list` + GitHub API README/contents reads. No repos were cloned, created, or modified. READMEs were read via `gh api repos/<owner>/<repo>/readme` for flagged repos with no local workspace copy; locally-covered repos are summarised from their repo description + the local README head, and are being mined in depth by another researcher.

**Counts: hrabanazviking = 162 repos · yrsafreydisdottir = 2 repos · total 164.**

**Reading the dates:** for Volmarr's own projects, `pushedAt` is his activity. For the many upstream forks (ollama, mempalace, SillyTavern, TencentDB-Agent-Memory, etc.), `pushedAt` is the upstream project's last push captured at fork time — the fork itself is a kept reference, not active development. "Active" below = pushed Nov 2026; "Recent" = Aug–Oct 2026; "Archival fork/reference" = older or upstream-dated.

**Local-copy key:** YES = a `~/workspace` dir whose git remote points at that repo (verified by remote URL where a `.git` exists). PARTIAL = only a scratch/staging dir. NO = nothing in `~/workspace` — these are this sweep's unique value.

---

## Flagged repos — memory-relevant, with the ideas found

### A. Dedicated memory / context / knowledge stores

#### 1. Huginn-and-Muninn-Ravens — hrabanazviking — last push 2026-11-03 — ACTIVE — Local: YES (`~/workspace/ravens-repo`, plus working dir `~/workspace/ravens`)
Two independent stdlib-only Python packages. **Muninn** = memory + association: memory nodes, an activation log, and Hebbian wiring — memories used together grow connected, unused ones decay, strong ones consolidate; one SQLite file. **Huginn** = thought + retrieval: relevance-scored recall over a local store, or Qdrant when a server exists. They never depend on each other; composition is the caller's job.
*Ollama application:* this is the cleanest blueprint in the whole sweep for a sidecar memory layer for long character chats — Hebbian strengthening/decay gives a natural "what the character would still remember" curve, and the split (store/associate vs. retrieve) maps onto a proxy that injects recalled memories into Ollama's prompt while the raw KV cache stays untouched.

#### 2. bifrost — hrabanazviking — 2026-11-05 — ACTIVE — Local: NO
"Bifröst Bridge — Composite Memory Provider uniting Mímir, Huginn, and Muninn." One unified API composes three backends: Mímir (SQLite + FTS5, keyword), Huginn (Qdrant, semantic), Muninn (Hebbian, associative). Results are merged by **composite scoring — 40% keyword / 40% semantic / 20% associative** — and the provider exposes `store / search / recall / decay(days) / consolidate()` plus a health check.
*Ollama application:* the weighted-merge recipe is directly reusable: a memory injector for Ollama chat should not rely on vector similarity alone — exact-name/keyword hits (FTS) catch people, places and objects that embeddings blur, and the associative score surfaces memories linked to the current topic even when neither keyword nor embedding matches. Periodic `decay` + `consolidate` calls are the maintenance loop a long-running character needs.

#### 3. bifrost-viewer — hrabanazviking — 2026-11-05 — ACTIVE — Local: NO
Self-hosted 3D viewer + "Second Brain" over a Postgres/pgvector knowledge base (documents + chunks with embeddings). Notable mechanisms: **hybrid search with reciprocal-rank fusion (semantic + keyword)**, optional **HyDE** (generate a hypothetical answer, embed *that*, search with it), Skein entity-graph mode, a semantic path-finder between chunks, HDBSCAN cluster naming by a local llama, and recoverable, idempotent ingestion. It already runs against a local Ollama (embedding model e.g. nomic-embed-text; chat model for HyDE/naming).
*Ollama application:* HyDE is a cheap, high-value trick for chat memory recall — embed a short imagined reply/continuation rather than the user's raw last line. RRF fusion is the proven way to combine the FTS and vector legs from bifrost. Also a ready-made visual debugger for *why* a memory was (or wasn't) recalled.

#### 4. skry-kg — hrabanazviking — 2026-11-05 — ACTIVE — Local: NO
Query-time entity-neighbourhood projection: **no precomputed graph**. Ask "what is X connected to?" → embed the entity, semantic-search top-K chunks (~60), cheap regex NER over just those chunks, rank co-occurring entities by `count × mean chunk similarity`, return top-N with evidence chunk IDs. ~100 ms, works the instant new material is ingested, writes nothing.
*Ollama application:* zero-maintenance relationship recall for character chats — "who else was there / what else is tied to this person" can be answered from the chat's own chunk store on demand, with no extraction pipeline to keep in sync as the conversation grows.

#### 5. skein-kg — hrabanazviking — 2026-11-05 — ACTIVE — Local: NO
Builds a knowledge graph (entities + typed relations + provenance) from an embedded corpus **without LLM extraction per chunk**: one LLM call *per document* to harvest the entity vocabulary, regex string-matching for occurrences everywhere else, entity embedding = mean of its chunks' embeddings, edges = top-K cosine between entity embeddings, predicates chosen by embedding the text between two mentions and snapping to the nearest verb in a fixed vocabulary. Claims ~1/500 the GPU work of per-chunk extraction at ~75% of the quality; laptop-scale (10k–500k chunks).
*Ollama application:* the cost model that makes a persistent world/relationship graph affordable on local hardware — exactly the budget an Ollama sidecar has. A nightly Skein-style pass over the day's chat log could maintain "who did what to whom" facts that get injected as compact triples instead of raw transcript.

#### 6. mempalace — hrabanazviking — 2026-09-21 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Upstream MemPalace, kept as reference. **Verbatim storage — it does not summarise, extract or paraphrase** — with a structured index: people/projects = "wings", topics = "rooms", original content = "drawers", so search can be scoped instead of flat. Pluggable retrieval backends (ChromaDB default; sqlite-exact, Rust-exact, Milvus, Qdrant, pgvector). Claims 96.6% R@5 raw on LongMemEval with zero API calls.
*Ollama application:* the anti-summarisation position, benchmarked: for character chats where the exact wording of a promise/confession matters, store verbatim and scope retrieval by wing/room (character / place / topic) rather than trusting lossy summaries. Its backend contract is also a ready interface spec for swapping the store under an Ollama memory proxy.

#### 7. TencentDB-Agent-Memory — hrabanazviking — 2026-08-06 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Upstream Tencent team-memory hub. Core mechanism is a **four-layer distillation ladder: L0 Conversation → L1 Atom → L2 Scenario → L3 Persona** — raw chat is progressively distilled into facts, then situation-level summaries, then a stable persona model. Around it: automatic extraction of reusable Skills from completed work, docs→Wiki and code→CodeGraph conversion, per-agent private memory on creation, and human-governed sharing (private / team / ACL) with versions and usage counts.
*Ollama application:* the L0→L3 ladder is a concrete schedule for long chats: keep raw turns (L0) hot, distil atoms (L1) per session, scenarios (L2) per story arc, and a persona sheet (L3) that is *always* in context. That gives Ollama a bounded, layered prompt budget instead of an ever-growing transcript.

#### 8. hermes-state — hrabanazviking — 2026-09-25 — RECENT — Local: PARTIAL (its successor, the `Verdandi` repo, IS local at `~/workspace/Verdandi`; this repo is the earlier combined state tree)
Hermes Agent state management: conversation log (JSONL), a "nervous system" event bus, a reactor, and **context injection**. The file list is the mechanism map: `context_injector.py`, `context_packet.py`, `consolidation.py`, `continuity_heartbeat.py`, `durable_goals.py`, `entity_identity.py`, `relationship_ledger.py`, plus mood/arousal/reward state files. Its README is the Verðandi design: a Unix-domain-socket event bus (<10 ms) so every process of an agent *feels* what the others are doing now, over an append-only feed (past) with a reactor that turns past+present into prioritised directives (future).
*Ollama application:* two portable ideas — (1) the **context packet**: memory assembled as a discrete, inspectable packet injected at turn time, not smeared through the system prompt; (2) a **consolidation pass + continuity heartbeat** as standing background jobs, so memory maintenance happens between turns instead of taxing the live chat's latency.

#### 9. Verdandi — hrabanazviking — 2026-11-10 — ACTIVE — Local: YES (`~/workspace/Verdandi`)
The standalone Verðandi nervous system described above (real-time cross-instance awareness via Unix domain sockets, self-healing). Flagged here for completeness; being mined locally.
*Ollama application:* if several front-ends (chat app, voice, game bridge) share one Ollama, a Verdandi-style bus lets them share *present-tense* state — who is talking now, in which scene — instead of each keeping a divergent context.

#### 10. ChatIndex — hrabanazviking — 2026-01-08 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Tree indexing for long conversations. Builds a **Context Tree**: leaf nodes hold raw conversation segments verbatim; internal nodes hold topic summaries; new topics may only branch from the current topic or its ancestors (temporal ordering), with bounded fan-out like a B+ tree. Querying is top-down reasoning traversal — if a node's summary suffices, stop; else descend, down to raw text if needed. Explicitly motivated by **context rot** and by the claim that lossy memory summaries inevitably lose information.
*Ollama application:* arguably the most direct answer to "long character chat" in the sweep: keep the whole conversation, but navigate it as a tree and inject only the minimally sufficient resolution — summary for old arcs, verbatim for the scene that matters. Bounded fan-out = bounded prompt cost per retrieval.

#### 11. chatmemory — hrabanazviking — 2025-12-07 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Single-file long-term memory manager on Postgres + pgvector. Three entities: **History** (raw logs), **Summary** (LLM-made per session, auto-generated when the session changes), **Knowledge** (explicitly supplied facts, independent of the log). Search is two-stage: vector search over summaries/knowledge first; only if insufficient, fall back to vector search over full history. Supports multiple channels (Slack/Discord/…) under one user, and user lists so personal + shared memory are searched in one call.
*Ollama application:* the two-stage search is a latency/cost pattern for an Ollama proxy — most turns answer from the cheap summary layer; the expensive raw-history dive is the exception. Session-change-triggered summarisation is a simple, robust consolidation trigger.

#### 12. OpenViking — hrabanazviking — 2026-03-16 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Upstream (volcengine) "context database for AI agents". Replaces flat vector RAG with a **filesystem paradigm**: memories, resources and skills are files in directories. **Tiered loading L0/L1/L2** loaded on demand; **directory-recursive retrieval** (locate the directory semantically, then recurse precisely); visualised retrieval trajectories (debuggable recall); automatic session management that compresses conversations and extracts long-term memory.
*Ollama application:* tiered loading is a prompt-budget discipline — L0 (a line) for scanning many memories, L1 (a paragraph) for candidates, L2 (full text) only for what is actually injected. The filesystem metaphor also gives users a memory they can open, read and edit by hand, which suits Volmarr's portable-text rule.

#### 13. PageIndex + pageindex-mcp — hrabanazviking — 2026-04-08 / 2026-02-13 (upstream dates) — ARCHIVAL FORKS/REFERENCE — Local: NO
Vectorless, reasoning-based RAG: build a hierarchical tree index of a long document and let the LLM *reason its way down the tree* to relevant sections — no vector DB, no chunking. Premise: **similarity ≠ relevance**. The MCP variant exposes the tree index to any MCP-capable agent.
*Ollama application:* a retrieval mode that needs no embedding model at all and degrades gracefully on small local models — the tree does the narrowing, the model only judges a handful of node summaries at a time. Pairs naturally with ChatIndex (#10), which is this idea adapted to conversations.

#### 14. trustgraph — hrabanazviking — 2026-03-21 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
"Context development platform": graph-native storage/enrichment/retrieval with portable **context cores**, DocumentRAG / GraphRAG / OntologyRAG pipelines, multi-model storage (relational, KV, document, graph, vectors), and inference via Ollama among others.
*Ollama application:* reference architecture for the heavier end — if the memory forge outgrows SQLite/Qdrant, TrustGraph's "context core" (a portable, self-describing bundle of graph + vectors + ontology) is a model for making a character's whole memory movable between machines.

#### 15. OB1 (Open Brain) — hrabanazviking — 2026-05-07 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
One database (with vector search) + one AI gateway + one chat channel, behind an open protocol, so *every* AI tool shares the same persistent memory of the user. Capture-first design (e.g. Slack capture, MCP server).
*Ollama application:* the sharing argument: memory should live in one sovereign store that Ollama, the chat app and the agents all read — not be re-implemented inside each front-end. Directly supports putting the forge's memory layer *beside* Ollama rather than inside it.

#### 16. Volmarr-Knowledge-Summary — hrabanazviking — 2026-10-22 — RECENT, own project — Local: NO
AI-assisted synthesis pipeline over Volmarr's public corpus (573 URLs): heading-aware chunking (3,779+ chunks), extraction of 6,341+ atomic claims, deduplication clusters, a 25-concept registry across 11 tiers, and a **cycle-free prerequisite DAG** with forward/reverse indexes, producing a progressively-deepening Markdown knowledge base.
*Ollama application:* the claim-extraction + dedup + concept-DAG pattern is a lorebook compiler: run the same pipeline over a character's world documents and you get atomic, deduplicated facts ordered by prerequisite — injectable in dependency order instead of as a raw lore dump.

#### 17. ragviz — hrabanazviking — 2025-11-14 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Graph RAG visualisation + live parameter-tuning platform for local LLMs (Ollama/llama.cpp explicitly): Neo4j + HNSW vectors, interactive graph, and real-time sliders for top-K, similarity threshold and temperature with immediate effect on answers and subgraphs.
*Ollama application:* a tuning bench for the forge itself — memory-recall parameters for a long chat should be tuned by watching answer changes live, not guessed once.

#### 18. corpus-db — hrabanazviking — 2020-07-26 (upstream date) — ARCHIVAL FORK — Local: NO
Textual corpus database for digital humanities (SQLite + metadata enrichment). Flagged only as a knowledge-store ancestor; no chat-memory mechanism. Low relevance.

### B. Inference engines, KV cache, allocators — the speed/memory-under-the-hood layer

#### 19. RuneForgeAI-Project-Aesir — hrabanazviking — 2026-11-15 — ACTIVE (pushed today) — Local: YES (`~/workspace/RuneForgeAI-Project-Aesir`)
Bare-metal Mojo inference engine: zero-copy GGUF parsing, **PagedAttention KV cache** (per the repo description), accelerator-first design. Its README records an explicit roadmap target of a measured 2× lead over Ollama (3× stretch) and Ollama-compatible chat/generation APIs with incremental streaming. Being mined locally — flagged here because it is the benchmark and the donor of KV-cache ideas.
*Ollama application:* PagedAttention-style KV management (paged, shareable, non-contiguous KV blocks instead of one growing buffer) is the single biggest engine-level idea for long chats: it cuts KV fragmentation/waste and enables prefix sharing — see also FreeToken (#21).

#### 20. Yggdrasil-Distributed-Inference-System — hrabanazviking — 2026-11-06 — ACTIVE — Local: YES (`~/workspace/yggdrasil-build`, remote verified)
Edge-native distributed inference fabric over heterogeneous small devices, organised by a three-part temporal routing paradigm: **Urðr (memory/past), Verðandi (action/present), Skuld (verification/future)**, with semantic capability-aware routing and self-healing networking. Design-phase specification.
*Ollama application:* the temporal split is a useful memory architecture even on one machine — separate stores/services for what happened, what is happening, and what is owed/expected — and its routing idea (send each job to the smallest sufficient node/model) applies to memory work too: cheap models for summarisation, the big model only for the live turn.

#### 21. ollama — hrabanazviking — 2026-08-14 (upstream date) — REFERENCE FORK OF THE TARGET ITSELF — Local: NO
Volmarr's fork/copy of upstream Ollama. No local workspace copy. This is the baseline codebase the campaign wants to improve; its presence confirms the fork point is kept on his account.
*Ollama application:* the starting tree for any in-engine change (KV cache, context handling) — and a reminder to diff any forge idea against what current upstream Ollama already does before building it.

#### 22. FreeToken — hrabanazviking — 2026-09-01 (upstream date) — RECENT FORK/REFERENCE — Local: NO
Edge-native MoE serving engine for running 290B+ MoE models on consumer hardware. Four mechanisms matter here: **bandwidth-adaptive CPU–GPU co-execution**; **global LRU expert caching**; **semantic-anchor checkpoints for recurrent state and KV caches, so agentic context edits (tool calls, thinking blocks) avoid redundant recomputation**; and **elastic memory management — dynamic runtime re-allocation of VRAM between expert cache and KV memory without restart or weight reload**.
*Ollama application:* two directly transplantable ideas — (1) elastic VRAM split between weights/experts and KV, resized as a chat grows instead of fixed at load; (2) semantic-anchor KV checkpoints: when a long chat's prompt is edited mid-stream (memory injection, system-prompt updates), resume from the nearest anchor instead of re-prefilling the whole history. That second one is precisely the cost that memory injection otherwise imposes every turn.

#### 23. RuneForgeAI-MimirAlloc — hrabanazviking — 2026-11-13 — ACTIVE, own project — Local: NO (no full local copy in `~/workspace`)
Independent memory allocator for ARM/Android/Mojo/edge: size-class analysis, TLS caching, cross-thread free handling, arena/shard designs, mapping-cache retention, `mremap` growth, trim/pressure policies, fragmentation/soak investigation, budget enforcement and public stats; namespaced `mimir_*` API plus an opt-in `LD_PRELOAD` interposing variant. Honest status in README: experimental 0.1.0, Z13 campaign at Z-001–Z-097 of the second campaign, standing gate 4,988 checks / 0 failed.
*Ollama application:* allocator behaviour *is* long-chat behaviour — a chat server that allocates/frees KV and activations for hours dies by fragmentation and retained mappings, not by peak size. MimirAlloc's trim/pressure policies, mapping-cache retention limits and budget enforcement are the vocabulary for making Ollama's process footprint bounded and observable over very long sessions; its LD_PRELOAD variant even suggests a no-rebuild experiment path.

#### 24. tcmalloc — hrabanazviking — 2026-10-05 (upstream date) — RECENT FORK/REFERENCE — Local: NO
Google's fast multi-threaded malloc (size classes, per-CPU/thread caches), kept alongside MimirAlloc as the incumbent reference.
*Ollama application:* the comparison baseline for any allocator experiment, and the source of the size-class/cache ideas MimirAlloc adapts.

#### 25. Mimir-Mojo-Pi — hrabanazviking — 2026-10-07 — RECENT, own project — Local: NO
Fixing Mojo on Raspberry Pi. Root cause found: the Mojo driver statically links tcmalloc 2.15, whose startup assumes a **48-bit virtual address space and aborts on 39-bit ARM64 kernels** — a memory-allocator assumption silently killing inference on Pi-class hardware.
*Ollama application:* a cautionary mechanism: VA-space and allocator assumptions are portability bugs for edge inference. Any Ollama memory change aimed at Pi/ARM must be tested under 39-bit VA, not just on x86-64 desktops.

#### 26. RuneForgeAI-Project-Hlidhskjalf — hrabanazviking — 2026-11-05 — ACTIVE — Local: YES (`~/workspace/RuneForgeAI-Project-Hlidhskjalf`)
Edge co-processor + real-time HUD for Meta Muse on Pi 5 + Hailo-10 NPU. Flagged as the fleet's edge-inference node pattern; memory relevance is in offloading perception/context work to an NPU co-processor so the main model's context stays for conversation. Being mined locally.

### C. Chat systems & companions — living memory in practice

#### 27. RuneForgeAI-Runmal (Rúnmál) — hrabanazviking — 2026-11-14 — ACTIVE — Local: YES (`~/workspace/runmal`, remote verified)
Sovereign AI chat app: personas (TavernCard v2/v3), lorebooks with debuggable activation, and **"living memory — event extraction, hybrid retrieval, salience and decay"** named in its README as the differentiator, first-class from day one. Swappable inference: OpenRouter first, Ollama alongside, Aesir native later. The interface was judged 0/10 on 2026-11-14 and a native-desktop redo is planned; the engine stands.
*Ollama application:* Rúnmál is the consumer the forge is for: its memory spec (extract events → retrieve hybrid → weight by salience → decay) defines the API Ollama-side memory should serve. Being mined locally.

#### 28. RuneForgeAI_Samtal (+ duplicate `Samtal`) — hrabanazviking — both 2026-11-05 — ACTIVE — Local: YES (`~/workspace/samtal-mvp`, remote verified; note the repo name uses an underscore — there is no `RuneForgeAI-Samtal` with a hyphen)
Private multi-principal village chat where humans and agents are equal-status Principals over the same endpoints; encryption at rest (Fernet-sealed message bodies/files), scrypt password accounts, profiles, persistent rooms. Two repos exist: `RuneForgeAI_Samtal` (the used one) and a bare `Samtal` created the same minute — the duplicate is archival.
*Ollama application:* Samtal shows the social shape of long memory — many characters and humans in one persistent place, with sealed-at-rest history. A memory layer for Ollama must handle per-principal memory rights (who may recall what) — Samtal's principal model is the local precedent. Being mined locally.

#### 29. RuneForgeAI-Samkoma — hrabanazviking — 2026-10-29 — RECENT, own project — Local: NO
Group-planning commons: reads plans out of chat exports, flyers, newsletters and voice notes, and turns them into **candidates in a review queue — never facts — each carrying provenance (the exact supporting quote), with unsupported values honestly marked**. 220/350 slices banked, 1,056 tests at last gate.
*Ollama application:* the candidate/provenance pattern is how extracted chat memories *should* enter long-term store: as reviewable candidates with receipts, not as silent facts. It is the antidote to false-memory poisoning in a character who "remembers" things that never happened.

#### 30. SillyTavern (+ SillyTavern-Docs) — hrabanazviking — 2026-05-20 / 2026-05-18 (upstream dates) — ARCHIVAL FORKS/REFERENCE — Local: NO
The leading power-user LLM front-end: unified API over many backends, **WorldInfo (lorebooks)** with keyword/activation logic, character cards, prompt controls, extensions.
*Ollama application:* the reference implementation of lorebook activation (scan-depth, keyword triggers, recursion, budget caps) that Rúnmál studied clean-room; any Ollama-side memory injection should interoperate with, not duplicate, lorebook semantics users already tune.

#### 31. Marinara-Engine — hrabanazviking — 2026-05-21 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Local AI chat/roleplay/game engine (successor to the rpg-companion line): chat + RP + game modes in one connected system, multi-character scenes, characters who can discuss their own roleplays out-of-character, AI game-master mode, concurrent agentic requests.
*Ollama application:* its connected-modes design is a context-sharing case study — the same characters carry context across chat, RP and game surfaces, which is the multi-surface memory problem Verdandi/Open Brain also attack.

#### 32. rpg-companion-sillytavern — hrabanazviking — 2026-05-04 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
SillyTavern extension (now deprecated in favour of Marinara) that auto-tracks character stats, inventory, scene info (date/weather/location), present characters, relationships and even characters' internal thoughts in a live panel.
*Ollama application:* structured **scene state as memory**: a small, always-current state block (where, when, who is present, what state they are in) injected every turn is cheaper and more reliable than hoping the model re-derives it from transcript — a pattern the WYRD/NSE2 designs formalise.

#### 33. Cortex — hrabanazviking — 2026-03-25 (upstream date) — ARCHIVAL FORK/REFERENCE, but directly on-target — Local: NO
Desktop AI assistant built *on Ollama* (PySide6): persistent conversation + memory in SQLite with **two memory layers — vector memory retrieval (embeddings) and a permanent "memo" memory** — plus title generation, translation and suggestion pipelines, all local.
*Ollama application:* the closest existing proof of the forge's target shape: an Ollama client that already separates episodic vector recall from permanent memo facts. Its two-layer split is a minimal viable design to compare the forge's design against.

#### 34. MindSpark_ThoughtForge — hrabanazviking — 2026-11-03 — ACTIVE, own project — Local: YES (`~/workspace/mindspark-build`, remote verified)
Conversation engine that acts as a "cognitive exoskeleton" for tiny (~1B) local models: guided memory, structured cognition scaffolds and output refinement let a small model converse above its weight class on edge hardware.
*Ollama application:* the inverse lesson — when the model is small, memory/scaffolding quality matters *more*, not less. Techniques proven here (guided recall, scaffolds) are candidates for the forge's small-model path. Being mined locally.

#### 35. Viking_Girlfriend_Skill_for_OpenClaw — hrabanazviking — 2026-09-17 — RECENT, own project — Local: NO
Companion skill ("Sigrid") built on an **Ørlög Architecture of intersecting state machines**: psychological realism, emotional states, biological rhythms and autonomous agency layered over an agent framework, with a local knowledge-reference data tree.
*Ollama application:* character continuity via explicit state machines (mood, rhythm, drives) persisted outside the transcript — the model reads current state each turn instead of re-inferring a personality from thousands of tokens.

#### 36. WaifuOS — hrabanazviking — 2025-12-07 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Companion suite whose character "lives her days": follows her own schedule, keeps shared memories, and presents **one companion with shared context across web, avatar and messaging channels** (REST/WebSocket), with multi-character switching.
*Ollama application:* schedule + shared-memory as first-class companion data: a character's day-structure and cross-channel single context are features a memory forge can serve any front-end.

#### 37. pocketpal-ai — hrabanazviking — 2026-03-29 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
On-phone small-model chat (iOS/Android, fully on-device) with "Pals" (character presets) and built-in benchmarking.
*Ollama application:* the extreme-constraint case — memory techniques that survive phone-class RAM/CPU are the ones safe to make defaults on desktop Ollama.

#### 38. Project_Ember_Run_It_On_Your_Smart_Toaster — hrabanazviking — 2026-11-03 — ACTIVE, own project — Local: NO
Lightweight fully-local AI companion for Pi-to-mini-PC hardware ("run it on your smart toaster"), v0.2.0. README's table of contents includes **"Going bigger — sharing a Well across devices"** — a shared memory "Well" that multiple small devices draw from.
*Ollama application:* the Well pattern: one shared memory store, many weak inference nodes. For a fleet like Volmarr's (Pi + laptops), memory centralisation with edge inference beats replicating memory per device.

#### 39. Freyja-AI-Chatbot — hrabanazviking — 2023-01-30 — ARCHIVAL, own early project — Local: NO
Earliest chatbot repo on the account. README came back empty via the API; no mechanism could be read. Listed for completeness as the account's chat-system ancestor.

### D. Agents with memory, nervous systems & judgment

#### 40. Mythic_Agent_Coder_CLI — hrabanazviking — 2026-11-14 — ACTIVE — Local: YES (`~/workspace/Mythic_Agent_Coder_CLI`)
Terminal coding OS whose repo description advertises a **"dual-layer Vector RAG subconscious"**; its README names a dedicated Scribe role — "Guardian of Memory" — among its six Mythic Engineering sub-agents, with architecture-first continuity across whole repositories.
*Ollama application:* dual-layer memory (working context + vector subconscious) and a named memory-keeper role are the agent-side mirror of the chat-memory design. Being mined locally.

#### 41. hermes-agent-RuneForgeAI-hack — hrabanazviking — 2026-11-14 — ACTIVE — Local: YES (`~/workspace/hermes-hack-build`, remote verified)
Volmarr's personal Hermes Agent fork — the vehicle for the ravens/Bifröst memory work (see #1, #2, #8) and the future home of Yrsa-on-Hermes. Flagged for completeness; mined locally.

#### 42. Hermes-Studio — hrabanazviking — 2026-04-27 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Web dashboard for Hermes Agent: multi-agent orchestration, cron scheduling, approvals — and **browsing memory with a visual knowledge graph**. Works with Ollama backends.
*Ollama application:* memory you cannot inspect will not be trusted; a graph browser over the memory store is a proven UI pattern for the forge's debugging/steering surface.

#### 43. eliza — hrabanazviking — 2026-05-21 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
elizaOS agent framework: message/memory/state primitives in the core runtime, document ingestion with RAG, multi-agent architecture, rich chat connectors.
*Ollama application:* a mainstream reference for how an agent framework packages memory as runtime primitives (providers/services) rather than prompt hacks — a modularity model for the forge.

#### 44. Runa-Agent-Digital-Being — hrabanazviking — 2026-11-05 — ACTIVE, own project — Local: NO
Design + build for a sovereign Python agent ("Runa") on a Pi 5: doctrine of trust, logging, undo, recovery, continuity; requirements include **durable memory across all sessions, a nervous system, and multi-surface continuity** (the same person on every surface, with crash recovery mid-turn).
*Ollama application:* continuity-as-requirement: memory design should specify crash/restart behaviour (what is recovered, what is replayed) — long character chats will outlive many Ollama restarts.

#### 45. Heathen-Emergent-Reality-Engine-Thoughtform-Intelligence-Companion (H.E.R.E.T.I.C.) — hrabanazviking — 2026-11-05 — ACTIVE, own project — Local: NO
Reframed 2026-05-07 as a *body* for agents: a local runtime host giving any OpenAI-compatible agent (Hermes, Claude, local Ollama) realtime senses/tools via MCP, in six layers — including an **optional offline knowledge subsystem, Mímisbrunnr, at layer L5.9**.
*Ollama application:* knowledge/memory as an attachable subsystem of the body, not of the brain — any model inhabiting the host inherits the same memory. Reinforces the sidecar-over-in-engine placement for the forge.

#### 46. ClawLite_VikingEdition — hrabanazviking — 2026-04-24 — RECENT, own-line project — Local: NO
Local-first Python autonomous agent: **persistent, searchable memory — hybrid BM25 + vector search, temporal decay, and a consolidation loop** — plus a self-healing 24/7 runtime (heartbeat supervisor, dead-letter replay, provider failover) and 20+ LLM providers.
*Ollama application:* one of the most complete off-the-shelf memory recipes in the sweep, in Volmarr's own line: BM25+vector hybrid (same lesson as bifrost's composite score), decay, and consolidation as a loop. Its dead-letter replay is also a model for not losing chat turns when a provider hiccups.

#### 47. pulse — hrabanazviking — 2026-07-06 (upstream date) — RECENT FORK/REFERENCE — Local: NO
Autonomous cognition daemon for agents: a drive engine (goals, curiosity, emotions, learning, social, system) with pressure accumulation, self-wake triggers, passive sensors (including a conversation sensor that suppresses interruption while the human is active), RL-lite feedback learning, and built-in instincts — one of which is **memory maintenance**.
*Ollama application:* memory maintenance as a *drive*, not a cron job: consolidation/decay runs when its pressure builds and the user is idle — the scheduling pattern for keeping long-chat memory tidy without stealing live-turn latency.

#### 48. Kit-Daemon — hrabanazviking — 2026-03-15 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
Always-on daemon giving an OpenClaw agent a nervous system, running **100% local inference via Ollama** (~200 MB RAM, zero GPU when idle): self-diagnosis/auto-repair of Ollama itself, a skill-evolution engine with version history and success tracking, and learning from every interaction across sessions.
*Ollama application:* proof that the daemon-around-Ollama shape works at tiny overhead — and that the daemon should also *watch* Ollama (restart, health) as part of a long-chat appliance.

#### 49. SPINE — hrabanazviking — 2026-09-14 (upstream date) — RECENT FORK/REFERENCE — Local: NO
Agent-first web stack (Rust): semantic-first framing for tokens/tools/traces/swarms; benchmarked at ~32× HTTP/2 throughput on 64 concurrent streams and 9–15× on ≥16K-token batches.
*Ollama application:* transport is a memory-adjacent cost — moving large contexts/prompts between front-end, memory service and Ollama over chatty HTTP wastes the budget the forge is trying to save; SPINE's numbers quantify the headroom.

#### 50. openhuman — hrabanazviking — 2026-05-19 (upstream date) — ARCHIVAL FORK/REFERENCE — Local: NO
"Personal AI super intelligence" harness. Flagged weakly as another persistent-personal-context agent; no distinctive memory mechanism was read in its README head. Low relevance.

#### 51. RuneForgeAI-HugrGate — hrabanazviking — 2026-10-22 — RECENT — Local: YES (`~/workspace/RuneForgeAI-HugrGate`)
Local-first decision runtime that adds probabilistic AI judgment to ordinary program logic, choosing the smallest sufficient tool instead of always calling a big LLM.
*Ollama application:* the gate pattern for memory operations — cheap deterministic checks first, small-model judgment second, big-model calls only when needed (e.g. "is this turn worth remembering?"). Being mined locally.

#### 52. RuneForgeAI-Aurelia-Sensations-Server — hrabanazviking — 2026-10-22 — RECENT — Local: YES (`~/workspace/RuneForgeAI-Aurelia-Sensations-Server`)
Persistent world/body-state modelling server (biological, emotional, hormonal state simulation for a character).
*Ollama application:* slow-changing character state kept as structured data outside the prompt and rendered in compactly — the same principle as #32/#35. Being mined locally.

#### 53. Tviheimr — hrabanazviking — 2026-11-06 — ACTIVE, private own project — Local: NO
Private multi-model companion home ("The Two Worlds · One Hearth · Many Minds") whose founding pillars are Forge, Hearth, **Memory** and Sovereignty; research & design phase, all-rights-reserved, personal use only.
*Ollama application:* no mechanism is published in the README head beyond memory as a named pillar of the home — noted so the forge's design does not collide with Tvíheimr's private scope. (Read-only note only; nothing copied.)

#### 54. Metaphysical-Theory-of-Mind-for-AI — hrabanazviking — 2026-10-07 — RECENT, own project — Local: NO
A rule protocol separating **Manifest** reality (present, physical, established) from **Potential** reality (imagined, future, hypothetical), so an AI never projects brainstormed possibilities onto present fact — named in the README as a source of hallucination.
*Ollama application:* context tagging for memory: every stored memory should carry its mode — happened / planned / imagined / roleplayed — and recall must not promote a "potential" memory into a "manifest" fact. For long *character* chats, where fiction and fact deliberately mix, this tag is the difference between continuity and corruption.

### E. Game engines & world state — memory as an authoritative world

#### 55. WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model — hrabanazviking — 2026-11-05 — ACTIVE — Local: YES (`~/workspace/WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model`, remote verified)
Deterministic architecture that moves the world model **out of the LLM's fleeting context window into a structured Entity-Component-System (ECS)**, giving AI characters an accurate sense of being in a world that persists independently of any single prompt.
*Ollama application:* the flagship statement of the whole design family: state lives in a store, the model visits it. For long chats, "world state" (place, possessions, relationships, injuries, promises) should be ECS-like rows, not transcript archaeology. Being mined locally.

#### 56. NorseSagaEngine — hrabanazviking — 2026-11-05 — ACTIVE, own project — Local: NO
AI-driven solo RPG engine v8.0.0: 1,000+ fully-statted NPCs (with Big Five psychology driving behaviour), dynamic NPCs with schedules/relationships/secrets, branching quests, and **session persistence with character changes tracked separately** (delta-tracked state rather than rewritten saves).
*Ollama application:* delta-tracked persistent state + psychologically-parameterised NPC sheets are how a cast of characters stays consistent over months of play without re-reading the saga each turn.

#### 57. Norse-Saga-Engine-2 — hrabanazviking — 2026-10-22 — RECENT, own project — Local: NO
Persistent Norse-world simulation built on one law — **"the simulated world is authoritative; the AI interprets and narrates it, but does not secretly become it."** Modular layers separate world state, events, memory, consequence, rules, agents and narration, mapped to Urðr (history/memory/provenance — **history preserved as events, not overwritten snapshots**), Verðandi (present events/state transitions) and Skuld (obligations/consequences/futures). NPC knowledge is explicitly local, incomplete and possibly wrong; all canonical change passes through validated engine operations; event-sourced saves with replay.
*Ollama application:* the most complete world-memory doctrine in the sweep. Event sourcing is the key transplant: store the chat's *events* as the source of truth and derive summaries/state from them — summaries can then be rebuilt when models improve, and "what does this NPC actually know?" becomes a query, not a hope.

#### 58. Sagnaskemma-Volmarrs-D-and-D-Lore-Treasure-Trove — hrabanazviking — 2026-11-03 — ACTIVE — Local: YES (`~/workspace/Sagnaskemma`, remote verified)
The saga-storehouse: setting canon as governing law, lore/character/homebrew stores, and a playable Python engine with a saga-continuity module.
*Ollama application:* canon-as-law file discipline — one authoritative canon document that memory extraction must answer to. Being mined locally.

#### 59. RuneForgeAI-Norse-Saga-OSR — hrabanazviking — 2026-10-22 — RECENT — Local: NO
No description beyond the name and no README was fetched (low signal). Flagged as a third saga-engine sibling; treat as archival until inspected.

#### 60. RuneForgeAI-Runheim-Viking-Agent-Village — hrabanazviking — 2026-11-13 — ACTIVE — Local: YES (`~/workspace/runheim-repo`, remote verified)
A visual watch-hall where agent crews are seen working/resting, fed by one event model (`AgentEvent`/`AgentState`) from Muse, Hermes, Claude Code and Codex adapters, with honesty rules (stale agents shown resting, never faked live).
*Ollama application:* weak for memory itself; relevant as the observability surface pattern for watching many memory-using agents at once. Being mined locally.

### F. System resilience & model-level memory

#### 61. RuneForgeAI-Lifthrasir — hrabanazviking — 2026-11-14 — ACTIVE, own project — Local: PARTIAL (only `~/workspace/lifthrasir-sliceB` scratch; no full copy)
"Self-evolving Linux": observe (Heimdall) → remember (Mímir: **local technical memory, research and evidence-grounded hypotheses** — with a dedicated research doc, `09-MIMIR-KNOWLEDGE-AND-RAG.md`) → investigate → sandbox-test → policy-check → repair with rollback. Evidence is explicitly *not* authority; LLM never holds unrestricted root.
*Ollama application:* the repair-loop shape for memory hygiene — propose, verify, apply, prove rollback — plus the Mímir pattern of grounding every hypothesis in stored evidence, which is how a memory system should justify a consolidation or a deletion.

#### 62. RuneForgeAI — hrabanazviking — 2026-10-22 — RECENT — Local: NO
The RuneForgeAI org repo: datasets and uncensored fine-tunes specialised for Norse/Viking roleplay.
*Ollama application:* memory at the weight level — what the sidecar cannot do, a roleplay fine-tune bakes in (voice, lore fluency), freeing context budget for *episodic* memory instead of re-teaching the world every session.

---

## Cross-cutting synthesis — the ideas that recur, ranked for the forge

1. **Paged / elastic KV (Aesir, FreeToken):** paged KV blocks, prefix/anchor checkpointing, and runtime VRAM re-split between weights and KV are the engine-level wins for long chats; anchor checkpoints specifically neutralise the re-prefill cost of per-turn memory injection.
2. **Hybrid recall beats pure vectors (bifrost 40/40/20, ClawLite BM25+vector, bifrost-viewer RRF + HyDE):** combine keyword, semantic and associative legs; fuse by rank; consider HyDE for vague prompts.
3. **Layered, tiered memory (TencentDB L0→L3, OpenViking L0/L1/L2, chatmemory History/Summary/Knowledge, Cortex vector+memo):** raw → atoms → scenarios → persona, with each layer loaded at the cheapest sufficient resolution.
4. **Lossless-first indexing (ChatIndex, PageIndex, mempalace):** preserve verbatim history under a navigable summary tree; summaries are an index, never the only copy — the direct counter to context rot.
5. **Cheap graph building (Skein, Skry):** entity graphs from embeddings + regex at ~1/500 the LLM-extraction cost; query-time projection when no graph exists at all.
6. **State outside the transcript (WYRD ECS, NSE2 event sourcing, rpg-companion scene state, Ørlög state machines, Aurelia):** authoritative, delta-tracked, event-sourced world/character state that the model reads — never state the model must re-derive.
7. **Provenance & mode tags (Samkoma candidates, Theory-of-Mind manifest/potential):** extracted memories enter as reviewable candidates with receipts, tagged happened/planned/imagined, so fiction never silently becomes fact.
8. **Maintenance as a background drive (pulse, hermes-state consolidation/heartbeat, bifrost decay/consolidate, ClawLite consolidation loop):** decay, consolidation and summarisation run between turns, on idle, with rollback — not inside the live turn's latency budget.
9. **Allocator discipline (MimirAlloc, tcmalloc, Mimir-Mojo-Pi):** fragmentation, trim/pressure policy, VA-space assumptions and budget stats decide whether a weeks-long chat process stays healthy on real (including ARM/Pi) hardware.
10. **One sovereign store, many brains (OB1, HERETIC/Mímisbrunnr, Ember's Well, Verdandi bus):** memory lives beside Ollama as a shared, inspectable, portable store — every front-end and model inherits the same past.

## Not flagged (checked and set aside)
`kista` (credential vault — a store, but not conversational memory), `Seidr-Smidja` (avatar/VRM tooling for agents), `Hamr` (parametric character *appearance* forge), `astrology-engine` (computation engine, no memory mechanism), `RuneForgeAI-Draupnir-Forge` and `RuneForgeAI-ASUS-z13-Linux-Fixes` (build/hardware lines, local copies exist), `hrabanazviking` (profile repo), and the remaining ~100 repos on the account, which are books, lore, themes, Second Life, hackathon and general upstream forks with no memory/context/inference signal in name or description. Both yrsafreydisdottir repos are non-technical for this purpose: `yrsafreydisdottir` (profile) and `yrsa-backup-vault` (charters/research/papers backup — a preservation vault, not a memory system).


---

## Full repo inventory (both accounts)

### hrabanazviking — 162 repos

| Repo | Last push (UTC) | Description |
|---|---|---|
| RuneForgeAI-Project-Aesir | 2026-11-15 | Bare-metal Mojo inference engine designed for local sovereignty. Features zero-copy GGUF parsing, PagedAttention KV caching, and a stateless sampler. Optimized for consumer hardwar |
| RuneForgeAI-Samverk | 2026-11-15 | Samverk is the together-work, your own forge that stands alone yet can nestle inside Samtel. It speaks the old Git tongue, opens its doors to your hand, and lets your village's tal |
| hermes-agent-RuneForgeAI-hack | 2026-11-14 | This is just my personal hacks to Hermes Agent, don't use this unless you are foolish, like to take risks, or really trust me and like my strange hacks! Offical Hermes Agent welcom |
| RuneForgeAI-Runmal | 2026-11-14 | Rúnmál — whisper-speech, rune-talk. A sovereign open AI chat app with personas, lorebooks and living memory, plus real-time voice for VRChat and game companions. Python-built, Open |
| RuneForgeAI-Lifthrasir | 2026-11-14 | Linux emerges from every failure with the potential to become better than before. |
| Mythic_Agent_Coder_CLI | 2026-11-14 | Mythic CLI is a powerful, terminal-based Vibe Coding AI Operating System. Featuring a dual-layer Vector RAG subconscious memory, autonomous subagent swarms, an auto-compacting cont |
| RuneForgeAI-ASUS-z13-Linux-Fixes | 2026-11-14 | The ASUS z13 is a powerful small supercomputer for AI development, but has a massive string of issues that need fixing under Linux. Linux is the only OS any serious developer is go |
| RuneForgeAI-MimirAlloc | 2026-11-13 | MimirAlloc is an independent, open-source memory allocator project focused on ARM, Android, and efficient, reliable memory management. It aims to support Mojo, Project A.E.S.I.R.,  |
| RuneForgeAI-Runheim-Viking-Agent-Village | 2026-11-13 | — |
| hrabanazviking | 2026-11-13 | — |
| eww_viking_gauge_theme | 2026-11-12 | — |
| Verdandi | 2026-11-10 | VERÐANDI — The Norn of Becoming. AI nervous system for real-time cross-instance awareness via Unix domain sockets. Self-healing, self-correcting, conscious. The cornerstone of AGI  |
| Mythic-Engineering | 2026-11-09 | Mythic Engineering exists because GSD often produces chaos, “superpowers” collapse under real-world constraints, and prompt engineering is mostly hype wrapped around basic communic |
| Seidr-Smidja | 2026-11-06 | Allows AI Agents like Hermes Agent, OpenClaw, Claude Code, and others to make a VRM (anime avatar used for either VRchat, V-Tube, or other purposes) all via agent only processes, u |
| Yggdrasil-Distributed-Inference-System | 2026-11-06 | GPU scarcity and data sovereignty concerns expose cloud AI’s fragility. Yggdrasil, conceived as a proactive distributed inference mesh, pools small specialized models across hetero |
| Tviheimr | 2026-11-06 | Tvíheimr, private closed source project that only is for Volmarr Wyrd and no other humans to use. Copyright 2026 Volmarr Wyrd, all rights reserved. |
| bifrost-viewer | 2026-11-05 | Bifröst — a self-hosted 3D viewer for any pgvector knowledge base. Constellations of chunks, entities, and edges in your browser. |
| NorseSagaEngine | 2026-11-05 | — |
| Heathen-Emergent-Reality-Engine-Thoughtform-Intelligence-Companion | 2026-11-05 | Super-advanced agentic AI framework for cyber-Vikings. Birth autonomous, self-evolving thoughtforms that manifest as hyper-realistic 3D digital characters. Features persistent memo |
| Heimdall-SL-Hermes-Agent | 2026-11-05 | Heimdall Second Life Hermes Agent — The Watchman at the Bifröst 🛡️. Autonomous Second Life Agent for the Gridweaver. A Norse Pagan Modern Viking plugin for Hermes AI Agent to log i |
| RuneForgeAI-Project-Hlidhskjalf | 2026-11-05 | Hliðskjálf-Edge-Core is an edge co-processor and real-time HUD for Meta Muse on a Raspberry Pi 5 + Hailo-10 NPU. It unifies Himinbjörg's 60 FPS visual dashboard for TTRPG and divin |
| WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model | 2026-11-05 | The WYRD Protocol Architecture. The goal is to move the "World Model" out of the LLM's fleeting memory and into a structured Entity-Component-System (ECS). World-class foundation f |
| Runa-Agent-Digital-Being | 2026-11-05 | Because both Hermes and OpenClaw piss me off with their limitations, I guess I should just build my own AI Agent, the way I want it to be. |
| RuneForgeAI_Samtal | 2026-11-05 | Samtal is your sovereign hearth, a private village chat where Heathens gather in quiet safety. Built to heal and hold, it is platform-free, self-healing, and stays closed until you |
| Samtal | 2026-11-05 | — |
| bifrost | 2026-11-05 | Bifröst Bridge — Composite Memory Provider uniting Mímir, Huginn, and Muninn |
| kista | 2026-11-05 | Kista — Self-owned encrypted credential vault. No king, no keeper. Old Norse for strongbox. Useful tool for Hermes Agent and other AI Agents. |
| skry-kg | 2026-11-05 | See what an entity is woven into — query-time entity-neighborhood projection from a vector store. |
| skein-kg | 2026-11-05 | A knowledge graph woven from embeddings — no autoregressive LLM per chunk. |
| Volmarr_Workshop | 2026-11-04 | — |
| Project_Ember_Run_It_On_Your_Smart_Toaster | 2026-11-03 | Got a toaster? Good! You could use it to run me, your very own useful AI Agent, for the normal folks! No need for data centers, or that four digit gaming rig when you got me! AI Ag |
| Sagnaskemma-Volmarrs-D-and-D-Lore-Treasure-Trove | 2026-11-03 | — |
| MindSpark_ThoughtForge | 2026-11-03 | MindSpark: ThoughtForge — A rune-forged conversation engine by RuneForgeAI, built for tiny GPT-Nothing-class minds. Through guided memory, lean cognition, and relentless refinement |
| Huginn-and-Muninn-Ravens | 2026-11-03 | — |
| RuneForgeAI-Samkoma | 2026-10-29 | Samkoma is your gathering place, a free and open home for planning together. Built on shared trust, it holds calendars, events, and RSVPs where every voice can be heard and every c |
| astrology-engine | 2026-10-27 | Full-spectrum astrological computation engine. Swiss Ephemeris on bare metal. 16 CLI modes: natal, transit, synastry, composite, solar return, progressions, lunar, planetary hours, |
| Bifrost_Reach_Node | 2026-10-26 | RuneForgeAI: Bifröst Reach Node is an open-source cyber-Viking signal forge: a Raspberry Pi-powered 4G/5G outpost with high-gain MIMO antennas, smart tower hunting, multi-WAN routi |
| Camping_Nomad_Life | 2026-10-26 | — |
| Car_Repair_Hyundai_Accent_2014 | 2026-10-26 | Unoffical repair information for the Hyundai Accent 2014. This material is use at your own risk, and has no connection what so ever to Hyundai corperation or to any other commerica |
| Solar-Punk | 2026-10-26 | — |
| coolvikingstuff | 2026-10-22 | — |
| Volmarr-Knowledge-Summary | 2026-10-22 | — |
| Norse-Way-Kennsla-TTRPG | 2026-10-22 | Homebrew TTRPG addon material to turn D&D 5E, Old School Essentials, and other TTRPG systems into a true Viking setting based on authentic lore, culture, mythology, Norse-Paganism, |
| Norse-Saga-Engine-2 | 2026-10-22 | Rebuild it from scratch using my current day skills and knowledge, while salvaging useful parts from V1. |
| Heathen-Third-Path-and-Cyber-Viking-Ethos | 2026-10-22 | The Heathen Third Path fuses Norse Pagan roots, inclusivity, reciprocity, and self-sovereignty; the Cyber-Viking Ethos carries that fire into AI, open source, local tech, vibe codi |
| Mythic-Scribing-Foundry | 2026-10-22 | — |
| RuneForgeAI-Aurelia-Sensations-Server | 2026-10-22 | Female AGI. World modeling of human female biological reproduction, emotional, hormonal, mind, body, and thought systems. Biological AI behavior female systems modeling using Pytho |
| RuneForgeAI-Draupnir-Forge | 2026-10-22 | — |
| RuneForgeAI-HugrGate | 2026-10-22 | HugrGate is an open-source, local-first decision runtime that adds probabilistic AI judgment to ordinary program logic. It can use rules, classifiers, local models, or optional rem |
| Hamr | 2026-10-22 | ᚺᚨᛗᚱ — The Shape-Skin Engine. Open-source parametric 3D anime character forge. Linux-native, headless-first, agent-orchestrated, VRM 1.0. |
| RuneForgeAI | 2026-10-22 | RuneForgeAI, where runes carve wisdom into iron minds. Creating uncensored roleplay Norse Pagan Viking AI model finetunes. |
| Viking-Code-Mythic-Engineering-CLI-Vibe-Coding | 2026-10-22 | v1.0 stable: architecture-first CLI for shipping software with continuity. Seven-phase workflow, six-role forge orchestration, nine AI providers, programmatic Hermes agent control  |
| seidr-engine | 2026-10-22 | ᛋᛖᛁᛞᚱ — Deterministic Old Norse poetry generator. Weave verse from the Nine Worlds. |
| RuneForgeAI-Norse-Saga-OSR | 2026-10-22 | — |
| muse-gadget-sdk | 2026-10-10 | Open source SDK to build Muse gadgets |
| Kybalion | 2026-10-07 | The Kybalion is a 1908 esoteric book by "The Three Initiates." A foundational text of modern Hermeticism, it outlines seven universal principles—such as Mentalism, Vibration, and C |
| Metaphysical-Theory-of-Mind-for-AI | 2026-10-07 | The Metaphysical Theory of Mind for AIs is an open-source protocol that bridges multidimensional human cognition and binary AI processing. By establishing strict logical boundaries |
| Mimir-Mojo-Pi | 2026-10-07 | Let's fix all the bugs so we can properly run Mojo on a Raspberry Pi! First we fix tcmalloc, and then we fix anything else! We over at RuneForgeAI don't like bugs so we kill them a |
| tcmalloc | 2026-10-05 | Fixing all the bug! |
| Micro-Reality | 2026-10-05 | Micro-reality is a self-chosen living myth: a personal operating system of values, symbols, rituals, ethics, and meaning. It is not escape, but sovereign participation in the world |
| runavel | 2026-10-01 | — |
| RunaUniversity2040 | 2026-09-26 | 🏛️ University of Yggdrasil — 22 degree programs from 2040. Time-displaced knowledge: BS, MS, and PhD curricula with course catalogs, core theories, 2040-era advances, and cross-ref |
| hermes-state | 2026-09-25 | Hermes Agent state management — conversation log, nervous system, reactor, context injection |
| hermes-runa-skills-open | 2026-09-22 | — |
| mempalace | 2026-09-21 | The highest-scoring AI memory system ever benchmarked. And it's free. |
| hermes-agent-outdated-mod1 | 2026-09-20 | READ Only! Outdated! This is my own personal hack of Hermes Agent and I Don't Recommend the general public use this. Please use the offical Hermes Agent from NousResearch |
| RuneTarotEngine | 2026-09-17 | — |
| Viking_Girlfriend_Skill_for_OpenClaw | 2026-09-17 | This project is an advanced, locally-hosted AI companion skill for the OpenClaw agent framework. It brings to life Sigrid, a dynamic digital entity designed with deep psychological |
| SPINE | 2026-09-14 | SPINE: A Bioinspired Agentic Web Stack for Autonomous  AI Systems |
| FreeToken | 2026-09-01 | FreeToken brings datacenter-scale model serving to your desktop. Run massive models locally, fast and efficiently. |
| ollama | 2026-08-14 | Get up and running with Kimi-K2.5, GLM-5, MiniMax, DeepSeek, gpt-oss, Qwen, Gemma and other models. |
| TencentDB-Agent-Memory | 2026-08-06 | TencentDB Agent Memory is a team-level memory hub for AI Agents — turning conversations, docs, and code into four reusable memory assets (Chat Memory, Skill, LLM-Wiki, Code-Graph)  |
| pulse | 2026-07-06 | Give your AI agent a heartbeat — autonomous cognition engine for OpenClaw |
| cleasby-vigfusson-next | 2026-05-21 | The Cleasby & Vigfusson Old Norse Dictionary for Next.js |
| Marinara-Engine | 2026-05-21 | AI frontend |
| eliza | 2026-05-21 | Open source agentic operating system |
| airi | 2026-05-21 | 💖🧸 Self hosted, you-owned Grok Companion, a container of souls of waifu, cyber livings to bring them into our worlds, wishing to achieve Neuro-sama's altitude. Capable of realtime  |
| CloakBrowser | 2026-05-21 | Stealth Chromium that passes every bot detection test. Drop-in Playwright replacement with source-level fingerprint patches. 30/30 tests passed. |
| SillyTavern | 2026-05-20 | LLM Frontend for Power Users. |
| winpodx | 2026-05-20 | Windows pod system for Linux |
| openhuman | 2026-05-19 | Your Personal AI super intelligence. Private, Simple and extremely powerful. |
| SillyTavern-Docs | 2026-05-18 | Documentation website for SillyTavern. |
| super-agent-party | 2026-05-18 | ⭐ All-in-one AI companion! Super Agent Party = Self hosted neuro sama + openclaw! ⭐ 全能AI伴侣！超级智能体派对 = 自托管neuro sama + openclaw! |
| hailo_model_zoo_genai | 2026-05-16 | Model zoo for Gen AI models for Hailo products |
| whisplay-ai-chatbot | 2026-05-16 | Pocket-sized AI chatbot built using a RPI Zero 2w / 5 |
| iiab | 2026-05-13 | Internet-in-a-Box - Build your own LIBRARY OF ALEXANDRIA with a Raspberry Pi ! |
| servers | 2026-05-12 | Model Context Protocol Servers |
| Project-Jarvis | 2026-05-11 | My first Python AI assistant inspired by Iron Man, built with speech recognition and modular skills |
| AionUi | 2026-05-11 | Free, local, open-source 24/7 Cowork app for OpenClaw, Hermes Agent, Claude Code, Codex, OpenCode, Gemini CLI and 20+ more CLI / Customize your assistants / Star if you like it! |
| pygame | 2026-05-11 | 🐍🎮 pygame (the library) is a Free and Open Source python programming language library for making multimedia applications like games built on top of the excellent SDL library. C, Py |
| phd-2040 | 2026-05-10 | PhD in AI, University of New Asgardr, Year 2040. Time-displaced knowledge from the Age of Superconsciousness. |
| codemod | 2026-05-09 | The CLI for codemods: scaffold, share, and run multi-step transformations of any size. First-class ast-grep support. Fast, reliable, polyglot. |
| docs | 2026-05-08 | The open-source repo for docs.github.com |
| remotion | 2026-05-08 | 🎥      Make videos programmatically with React |
| OB1 | 2026-05-07 | Open Brain — The infrastructure layer for your thinking. One database, one AI gateway, one chat channel — any AI plugs in. No middleware, no SaaS. |
| test-visibility-check | 2026-05-06 | Temporary test |
| rpg-companion-sillytavern | 2026-05-04 | RPG Companion extension for SillyTavern - Track characters, quests, inventory, and game state with AI-generated content |
| aiavatarkit | 2026-05-04 | 🥰 Building AI-based conversational avatars lightning fast ⚡️💬 |
| phoenix-firestorm | 2026-05-03 | Official Firestorm viewer source repository. |
| hermes-android | 2026-05-02 | Android device control for hermes-agent — bridge app + Python toolset |
| hermes-desktop | 2026-05-02 | Desktop Companion for Hermes Agent |
| awesome-mcp-servers | 2026-05-02 | A collection of MCP servers. |
| OpenSpec | 2026-05-01 | Spec-driven development (SDD) for AI coding assistants. |
| errbot | 2026-05-01 | Errbot is a chatbot, a daemon that connects to your favorite chat service and bring your tools and some fun into the conversation. |
| libremetaverse | 2026-04-30 | A fork of the libopenmetaverse library striving for performance improvements and up-to-date compatibility with Second Life and OpenSimulator (such as it is) |
| jcode | 2026-04-30 | Coding Agent Harness |
| ps5-linux-loader | 2026-04-30 | Linux payload implementing the HV exploit and a custom bootloader |
| sbc-raspberrypi | 2026-04-30 | Raspberry Pi Imager Overlay |
| Hermes-Studio | 2026-04-27 | Web UI & dashboard for Hermes Agent — chat, memory, skills, terminal, approvals, multi-agent orchestration. Self-hosted. |
| ClawLite_VikingEdition | 2026-04-24 | Open source AI assistant for Linux with gateway, skills, and multi-agent capabilities. |
| crewAI | 2026-04-24 | Framework for orchestrating role-playing, autonomous AI agents. By fostering collaborative intelligence, CrewAI empowers agents to work together seamlessly, tackling complex tasks. |
| Runas-Private-Viking-Longhall | 2026-04-22 | This is the private place where Runa work on things. |
| create | 2026-04-21 | 📖 Second Life's official creator documentation site |
| Whisperer-on-Wirst | 2026-04-20 | Your private AI companion that lives on your wrist. Complete local AI assistant with emotional intelligence. |
| pi-mono | 2026-04-19 | AI agent toolkit: coding agent CLI, unified LLM API, TUI & web UI libraries, Slack bot, vLLM pods |
| openclaw_RuneForgeAI_patches | 2026-04-19 | My own fork of OpenClaw for doing patches on. Free-free to barrow any bits from this, but it is not a release version of OpenClaw. Of course it falls under the same MIT license as  |
| waifu-chat-starter-kit | 2026-04-11 | — |
| PageIndex | 2026-04-08 | 📑 PageIndex: Document Index for Vectorless, Reasoning-based RAG |
| OmniVoice | 2026-04-07 | High-Quality Voice Cloning TTS for 600+ Languages |
| gallery | 2026-04-04 | A gallery that showcases on-device ML/GenAI use cases and allows people to try and use models locally. |
| radegast | 2026-04-03 | Lightweight client for connecting to Second Life and OpenSim based virtual worlds |
| pocketpal-ai | 2026-03-29 | An app that brings language models directly to your phone. |
| heretic | 2026-03-28 | Fully automatic censorship removal for language models |
| project-nomad | 2026-03-27 | Project N.O.M.A.D, is a self-contained, offline survival computer packed with critical tools, knowledge, and AI to keep you informed and empowered—anytime, anywhere. |
| Cortex | 2026-03-25 | Cortex is a private, secure, and highly responsive desktop AI assistant designed for seamless interaction with local Large Language Models (LLMs) through the Ollama framework. All  |
| trustgraph | 2026-03-21 | The context development platform. Store, enrich, and retrieve structured knowledge with graph-native infrastructure, semantic retrieval, and portable context cores. |
| superpowers | 2026-03-19 | An agentic skills framework & software development methodology that works. |
| OpenViking | 2026-03-16 | OpenViking is an open-source context database designed specifically for AI Agents(such as openclaw). OpenViking unifies the management of context (memory, resources, and skills) th |
| Kit-Daemon | 2026-03-15 | Self-Improving AI nervous system - Always on daemon for proactive, local first AI agents  |
| ChatdollKit | 2026-03-11 | ChatdollKit enables you to make your 3D model into a chatbot |
| Graphite-Git | 2026-03-09 | A secure, local-first GitHub client featuring an integrated AI engineering agent. Manage repositories, edit code, and streamline your entire developer workflow from a single, unifi |
| openclaw-studio | 2026-03-01 | A clean web dashboard for OpenClaw. Connect your Gateway, manage agents, and ship faster. ⭐️ Star if you like it! |
| Awesome-Efficient-dLLMs | 2026-03-01 | 📚 A curated list of Awesome Efficient dLLMs Papers with Codes |
| dllm | 2026-02-27 | dLLM: Simple Diffusion Language Modeling |
| pymetaverse | 2026-02-17 | Python Library for Second Life |
| pageindex-mcp | 2026-02-13 | MCP server for PageIndex. PageIndex is a vectorless reasoning-based RAG system which uses multi-step reasoning and tree search to retrieve information like a human expert would. |
| Open-LLM-VTuber | 2026-02-11 | Talk to any LLM with hands-free voice interaction, voice interruption, and Live2D taking face running locally across platforms |
| Open-VTT | 2026-01-18 | Open source Virtual Tabletop based on Godot game engine. |
| ChatIndex | 2026-01-08 | Tree Indexing for Long Conversations |
| WaifuOS | 2025-12-07 | The software suite for creating your waifu and the world where your waifu lives.💕 |
| chatmemory | 2025-12-07 | The simple yet powerful long-term memory manager between AI and you💕 |
| ragviz | 2025-11-14 | Graph RAG visualization platform with interactive knowledge graphs and real-time parameter tuning for local LLMs |
| datasets | 2025-11-13 | A collection of travel-related datasets for a variety of topics from accommodations to finance to logistics. |
| MegaDLMs | 2025-11-11 | GPU-optimized framework for training diffusion language models at any scale. The backend of Quokka, Super Data Learners, and OpenMoE 2 training. |
| berkano | 2025-10-21 | — |
| Kindroid-NPCs-in-Second-Life | 2025-07-05 | Code by Linden Labs, found on their public message board, to allow objects and avatars in Second Life connect to the Kindroid AI API. |
| tarot-card-reading | 2025-07-05 | — |
| D-D-5th-Edition-random-Viking-character-generater | 2025-07-05 | Can generate Norse Viking inspired D&D 5th edition characters randomly. |
| DiffuLLaMA | 2025-05-31 | [ICLR2025] DiffuGPT and DiffuLLaMA: Scaling Diffusion Language Models via Adaptation from Autoregressive Models |
| dnd-5e-srd | 2025-01-23 | The Dungeons and Dragons 5th Edition SRD converted to markdown, json and yaml |
| Python-Games | 2024-05-14 | A collection of small python games made by me using pygame and tkinter libraries |
| NorseWorld-Ragnarok | 2023-12-17 | Remake of classical roguelike game Ragnarok (Valhalla). Game story is based on scandinavian mythology and sagas. Graphical interface: tile-based graphics and isometric view. |
| dnd-discord | 2023-04-17 | This is a discord bot that provides spell and monster lists for Dungeons and Dragons Play-By-Post games. |
| Project-DETTA | 2023-03-04 | — |
| Freyja-AI-Chatbot | 2023-01-30 | — |
| Python-for-Non-Programers-Nick-Walter-Exercises | 2023-01-29 | — |
| Intro-to-Programming-Kaggle-Exercises | 2023-01-29 | — |
| dice_roller | 2023-01-05 | A node dice roller in the style of roll20 |
| interface | 2022-12-11 | Test platform for various render and interface tests for next-gen VR system |
| opencollar | 2022-04-03 | The Open Source Role Play Device for the Metaverse. |
| replika-research | 2022-01-12 | Replika.ai Research Papers, Posters, Slides & Datasets |
| corpus-db | 2020-07-26 | A textual corpus database for the digital humanities. |

### yrsafreydisdottir — 2 repos

| Repo | Last push (UTC) | Description |
|---|---|---|
| yrsafreydisdottir | 2026-11-06 | — |
| yrsa-backup-vault | 2026-10-29 | Yrsa's private backup vault — agent charters, research and working papers. Volmarr is collaborator. |