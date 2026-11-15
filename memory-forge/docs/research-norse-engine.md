# Research: "That One Game Norse Engine" — Memory Experiments Mined for the Ollama Memory Forge

*Read-only research run, 2026-11-15. Nothing outside this file was modified.*

---

## (a) Identification of the project

### The project is **NorseSagaEngine** — high confidence, not a guess

**What it is:** Volmarr's first coding project — a fully AI-driven, solo Norse Viking tabletop RPG (D&D 5E mechanics + Mythic GME oracle + Elder Futhark rune magic) in Python, where an LLM narrates the world, plays every NPC, and handles all mechanics invisibly. Local ingest copy's README identifies it as **Norse Saga Engine v8.0.0**; a repo filename records **81,676 lines of code as of March 8, 2026**, and the README claims a 1,000+ character database.

**Why this is unambiguously the right one — the memory problem is its founding wound:**

- Saved memory (memory/2026-10-10.md, reinforced 2026-11-03) records that NorseSagaEngine was *created because Friends and Fables lost continuity/plot after roughly a dozen turns*. The engine exists to solve LLM long-session memory failure — exactly the problem the Ollama Memory Forge attacks for long character chats.
- Saved memory (2026-10-10 / 2026-11-04) records that Volmarr conceived **memory-based cognitive functions modeled on Yggdrasil, the Nine Worlds, and Odin's ravens (Huginn/Muninn)** inside this line of work, that retrofitting it into the already-large project was "a mess," and that the idea became the foundation of his later advanced projects. That Yggdrasil cognitive architecture lives *inside* NorseSagaEngine (see `yggdrasil/` below).
- `ENGINE_INTENT.md` states the design question outright: the memory systems answer *"What has happened, and what matters?"* — and the architecture is explicitly "structured after Norse cosmology: Yggdrasil connects all, the Norns tend the Wells of Fate, Huginn and Muninn retrieve and store memory. The metaphor is not decoration – it shapes the actual engineering."
- The repo is saturated with memory research: a 29,934-byte memory consolidation plan, a memory-hardening plan, a context-optimizer plan, a knowledge-graph plan, a memory-maturity sprint doc, five separate implemented memory subsystems, and an entire vendored `ollama/` source tree (directly relevant to this campaign).

**Where it lives (all three verified this run):**

1. **GitHub (canonical):** `hrabanazviking/NorseSagaEngine` — **private**, created 2026-02-07, default branch `Development`, ~533 MB repo size, last pushed 2026-11-05.
2. **VM workspace (full local copy, mined for this report):** `~/workspace/your_files/repos-ingest/NorseSagaEngine/` — 419 top-level entries.
3. **purplelongship (Volmarr's laptop, verified live via device.invoke this run):** `/home/volmarr/Documents/GitHub/NorseSagaEngine`.

**Close relatives that are NOT the target (covered briefly in section c):**

- **Norse-Saga-Engine-2** (`hrabanazviking/Norse-Saga-Engine-2`, private, created 2026-09-29) — Volmarr's from-scratch redesign of the same game, "salvaging useful parts from V1." Its memory design is so distinct it gets its own numbered entry (#22) plus a section-c listing.
- **Yggdrasil Distributed Inference System** (the paused 244-slice project; `~/workspace/yggdrasil-build`) — a *distributed inference mesh*, not a game. It inherited the memory-graph ideas (its roadmap Part V is "Urðr memory graph") but it is a descendant, not the game-engine research itself.
- **Sagnaskemma** (`~/workspace/Sagnaskemma`, with `engine/saga.py` etc.) — the Norse D&D lore/engine Volmarr designated as Samtal's game heart. A sibling game engine, but the memory-experiment density is in NorseSagaEngine.

**Status honesty note:** NorseSagaEngine mixes *implemented* systems (real Python modules in `systems/`, `session/`, `yggdrasil/`) with *planned* designs (the T3 plans and Sprint 5–7 docs). Each entry below is labeled. Most numbers in the plan documents are **targets, not measured results** — flagged as such. The clearest measured results found: **Memory System v2.0 — all 10 packages built, 1,197 tests passing** (MASTER_TODO.md), and **Eir v1.0 consolidation pipeline — 11 tests passing** (MASTER_TODO.md).

Key source documents mined: `MEMORY_CONSOLIDATION_PLAN_v4.7.0.md` + `MEMORY_CONSOLIDATION_EXECUTIVE_SUMMARY.md`, `PLAN_T3A_context_optimizer_identity_protocol.md`, `PLAN_T3B_memory_hardening.md`, `PLAN_T3D_knowledge_graph.md`, `SPRINT_5_MEMORY_MATURITY.md`, `Building the Yggdrasil Cognitive Architecture in Python_ A Step-by-Step Guide.md`, `Technical Design Document for the Yggdrasil Cognitive Architecture, Integrating the Huginn (Thought) and Muninn (Memory) Subsystems.txt`, `YGGDRASIL_MANIFESTO.md`, `ENGINE_INTENT.md`, `ARCHITECTURE.md`, and the module docstrings of the implemented systems named below.

---

## (b) The memory ideas / experiments

### The five competing memory systems (the starting mess)

The consolidation plan's problem statement is itself a finding: the engine grew **five** memory systems that duplicated the same events in different formats with inconsistent retrieval — (1) `MemoryManager` (session/story), (2) `MemorySystemV3` (turn-based + vectors), (3) `EnhancedMemoryManager` (AI summaries, long-term), (4) `Muninn` (graph/hierarchical, Yggdrasil), (5) `CharacterMemoryRAG` (per-character RAG). Much of the research below is the attempt to discipline that sprawl.

---

1. **Three-tier turn memory fed by per-turn AI summaries** — *Implemented* (`systems/memory_system.py` MemorySystemV3, `systems/enhanced_memory.py`).
   - **Mechanism:** Short-term = last 5 turns at full detail; medium-term = last 20 turns summarized; long-term = whole session highly condensed. Every turn, the AI writes a structured summary of that turn — WHO was involved, WHAT happened, WHEN (turn + time of day), WHERE, WHY (motivation), HOW (method/outcome) — replacing vague auto-events like "Mystical event occurred." Those summaries, not raw transcripts, are what get passed back into context each turn.
   - **Problem attacked:** Raw history outgrows the window and vague event labels are useless for recall; this was the direct fix for the founding "lost the plot after ~12 turns" failure.
   - **Numbers:** Memory System v2.0 (the 10-package predecessor line) is recorded at **1,197 tests, all passing**.
   - **Ollama application:** For long character chats, store a structured per-exchange summary (who/what/emotion/place/open thread) as the unit of memory instead of raw turns — Ollama-side memory should summarize *into a schema*, not just truncate.

2. **Muninn (store) / Huginn (retrieve) raven split** — *Implemented* (`yggdrasil/ravens/muninn.py`, `huginn.py`, `raven_rag.py`).
   - **Mechanism:** Storage and retrieval are separate agents. Muninn owns persistent, hierarchical memory: nodes with a tree path (e.g. `characters/npcs/merchants`), a type (fact/entity/event/relationship/rule), importance 1–10, access count, timestamps, tags — with "self-healing data structures" and sync to a Helheim archive. Huginn owns retrieval: dynamic query routing, hierarchical search, **context compression of what it brings back**, multi-hop reasoning, adaptive search — it "brings back only what is needed for the current thought" so the main model is never flooded with the whole world. Muninn is explicitly framed as the anti-drift anchor: when the AI drifts, Muninn is "the weight of accumulated wisdom that says, *No, this is who we are. Look at the root.*"
   - **Problem attacked:** One undifferentiated memory blob both bloats context and lets the model's persona/world drift; separating the librarian from the scout keeps recall selective and grounding authoritative.
   - **Numbers:** None measured in the docs; design targets for access speed appear under #5.
   - **Ollama application:** Split Ollama memory handling into a writer/store service and a retriever that returns a *compressed, query-shaped* packet — never dump the store into the prompt.

3. **Nine Realms as typed memory partitions** — *Implemented as modules* (`yggdrasil/worlds/`: `helheim.py`, `niflheim.py`, `muspelheim.py`, `midgard.py`, `asgard.py`, `vanaheim.py`, `alfheim.py`, `jotunheim.py`, `svartalfheim.py`); unification *planned* in the consolidation plan.
   - **Mechanism:** Memory is partitioned by *kind of thing remembered*, each with its own contents and processing: Helheim = deep storage (summaries, world snapshots, completed-quest archives); Niflheim = emotional memory (states, stress/trauma, bond evolution); Muspelheim = narrative memory (arcs, themes, symbolic patterns, "mythic echoes"); Midgard = current context (live scene, present relationships, immediate objectives); Asgard = character development (skills, reputation, growth milestones); Vanaheim = world dynamics (location histories, cultural/seasonal/economic change); Alfheim = aesthetic memory (descriptive language, poetic phrases, tone); Jotunheim = combat memory (tactics, enemy profiles); Svartalfheim = craft/trade memory. The consolidated design adds ~16 typed memory records (`turn_event`, `emotional_state`, `relationship_update`, `skill_progression`, `quest_milestone`, `world_event`, `mythic_echo`, …) on one enriched node schema carrying game timestamp, location context, involved characters, emotional context, importance, confidence, compression level, and causal links (`causes`/`effects`).
   - **Problem attacked:** A single flat store can't prioritize — the scene you're in, a character's trauma, and a trade route should not compete for recall on equal terms.
   - **Numbers:** Consolidation plan targets a **10× increase in tracked data points** (target, not measured).
   - **Ollama application:** Partition chat memory by type (scene state / relationship state / character facts / open plot threads / tone) and give each partition its own retrieval rule, instead of one similarity search over everything.

4. **Per-character memory RAG + write-through persistence facade** — *Implemented* (`systems/character_memory_rag.py`, `systems/unified_memory_facade.py`).
   - **Mechanism:** Each character gets their *own* memory store (YAML-persisted folders) holding typed entries — interaction, observation, event, relationship, backstory — with importance 1–5, related characters, location, tags, session/turn stamps, so a character "remembers" past encounters and accretes an emergent backstory across sessions. The later `UnifiedMemoryFacade` wraps the fast in-session manager and this persistent store behind one API and **write-throughs any memory with importance ≥ 3** to the persistent tier, merging in-memory + persistent context on read.
   - **Problem attacked:** Session memory dies at session end; characters forgot the player between sittings. (Honest status recorded in the facade docstring: the RAG store was previously *orphaned — 0 call sites in the engine* — until the facade wired it in.)
   - **Numbers:** Write-through threshold = importance ≥ 3 (of 5).
   - **Ollama application:** Give each long-running character/persona its own durable memory file, and persist selectively by importance threshold so Ollama chats resume with the character's own history, not a global soup.

5. **The 5→1 consolidation ("Muninn Enhanced") with tiered storage** — *Planned* (`MEMORY_CONSOLIDATION_PLAN_v4.7.0.md`, 16-week, 5-phase plan); partially realized via #4's facade.
   - **Mechanism:** Collapse all five systems into one graph-based core with the realm partitions of #3, a unified query engine (turn context / character development / world state queries), an `EnhancedContextBuilder` that assembles labeled prompt blocks (recent history, emotional context, narrative momentum, world state), and four storage tiers: Hot (RAM, current turn, <1 ms), Warm (SSD, last ~100 turns, 5–10 ms), Cold (disk, >100 turns, 50–100 ms), Archival (compressed, >1,000 turns, 200–500 ms).
   - **Problem attacked:** Duplication, inconsistent retrieval, storage overhead, and maintenance burden of five overlapping systems.
   - **Numbers (ALL targets, not measured):** hot access <10 ms, cold <100 ms; **50% storage-footprint reduction**; 10× faster complex queries; 30% improvement in context relevance; 95% of queries <50 ms; memory footprint <2 GB for a 1,000-turn session; migration >1,000 records/minute at 100% integrity.
   - **Ollama application:** The tier model maps directly onto Ollama deployments: keep the live KV/session hot, recent-chat summaries warm on local disk, and deep history cold/compressed — with explicit latency budgets per tier.

6. **Graduated memory compression levels** — *Planned* (consolidation plan Phase 5, `MemoryCompressionEngine` design).
   - **Mechanism:** Every memory carries a compression level: 0 = raw, 1 = summary (key facts preserved), 2 = theme (emotional/narrative essence only), 3 = statistical (numerical trends only). Compressing a batch of turn events keeps verbatim only events with importance ≥ 7, and preserves the batch's emotional trend and narrative progression alongside the survivors.
   - **Problem attacked:** Old memories must shrink without the *shape* of what happened (how feelings moved, where the story was heading) being lost with the details.
   - **Numbers:** Importance ≥ 7 = the verbatim-survival threshold.
   - **Ollama application:** Age-based lossy compression for chat history where the fallback representation is a trend/essence sketch, not a hard delete — long chats degrade gracefully instead of hitting a cliff.

7. **Scored multi-factor retrieval with decay profiles** — *Implemented* (`systems/memory_retrieval.py`, weights in `data/charts/memory_scoring_weights.yaml`, decay in `memory_decay_profiles.yaml`).
   - **Mechanism:** Retrieval is a weighted score, not pure similarity: recency + textual relevance + **emotional resonance** + **entity overlap** (are the remembered people in the current scene?) + **location overlap**, with per-category decay profiles and full provenance attached to every returned memory ("Muninn weighs memory threads and returns top-k with provenance").
   - **Problem attacked:** Vector similarity alone resurfaces textually-similar but situationally-irrelevant memories, and misses emotionally-central ones phrased differently.
   - **Numbers:** Weights/decay are data-driven YAML, tunable without code; no benchmark results recorded.
   - **Ollama application:** Rank candidate memories for injection by who/where/emotion match with the current exchange, not embedding distance alone — cheap, local, and explainable.

8. **SOTG scene anchor — the MEMO context optimizer (T7)** — *Implemented* (`systems/context_optimizer.py`, Plan T3-A, based on arXiv:2603.09022).
   - **Mechanism:** A compact "State of the Game" block — turn, chaos factor, location, time of day, weather, ambient notes, who is physically present, active quests — is rebuilt every turn and **prepended at the very top of every prompt**, after the (2,500+ line) prompt assembly and before the model call, with a fail-safe that passes the prompt through unchanged if anchor-building throws.
   - **Problem attacked:** The physical scene anchor was buried mid-prompt after GM mindset, values, runes, RAG, memories, and emotional state; after a few dialogue-heavy turns the model statistically lost track of where it was and who was present.
   - **Numbers:** NPC list in the anchor capped at 6 by config; the problem it fixes was observed in a prompt builder of 2,500+ lines.
   - **Ollama application:** Pin a tiny, always-first "state card" (who the character is, where the scene is, what's unresolved) at the top of every Ollama request — position, not volume, is what keeps a long chat grounded.

9. **Identity-Aware Protocol — anti-persona-blending wrappers (T8)** — *Designed* (Plan T3-A, based on arXiv:2603.08852; an `yggdrasil/identity.py` module exists in the tree).
   - **Mechanism:** Every character's context block is wrapped in hard identity delimiters (`<|NPC_Yrsa_Start|> … <|NPC_Yrsa_End|>`), and a pre-send validation pass scans the assembled prompt for cross-contamination (one character's block opening inside another's) before generation.
   - **Problem attacked:** In multi-character scenes the model "bleeds" one NPC's personality, knowledge, or voice into another because all character context is concatenated as one flat string with no parse boundaries.
   - **Numbers:** Failure mode noted as acute in scenes with 3+ NPCs.
   - **Ollama application:** For multi-persona or character-plus-narrator Ollama chats, delimit each identity's memory/knowledge block and validate the assembled prompt — persona bleed is a formatting bug before it is a model bug.

10. **Identity Drift Detection (T6)** — *Implemented* (`systems/memory_hardening.py`, wired into `systems/enhanced_memory.py`; Plan T3-B, based on arXiv:2603.09043).
    - **Mechanism:** Every 20 turns, take a character's last 30 memory events and score behavioral keywords against personality dimensions (charged/fled/cowered → courage; betrayed/defended → loyalty; healed/tortured → agreeableness; etc., deltas of ±0.05–0.15 per signal). If total drift magnitude ≥ 0.25, log a drift event at importance 8, write a **session-delta override** (base character YAML is *never* modified), and inject a `[CHARACTER EVOLUTION NOTE]` into the prompt ("Thorbjorn has been growing more loyal; growing less aggressive… Reflect this evolution in his dialogue and behaviour").
    - **Problem attacked:** Static character sheets vs lived history: after 50 turns of a "cowardly" NPC acting bravely, the model kept narrating the stale sheet trait, breaking long-horizon coherence. Identity must be *reconciled with accumulated memory*, not just asserted once.
    - **Numbers:** Check interval 20 turns; lookback 30 turns; significance threshold 0.25; acceptance test: detect "15 coward events in 30 turns."
    - **Ollama application:** Periodically diff a character's stored persona against what the chat history says they've actually done/been, and inject a short evolution note — the single most transferable idea here for keeping long character chats self-consistent without rewriting the character card.

11. **Elastic Memory Windows (T2)** — *Implemented* (`systems/memory_hardening.py`; Plan T3-B, based on arXiv:2603.09716).
    - **Mechanism:** Retrieval size is dynamic instead of fixed (`max_items=15` everywhere before). A calculator multiplies a base window of 15 by scene type (idle 0.5×, travel 0.6×, commerce 0.7×, dialogue 1.0×, ritual 1.5×, combat/oath 1.8×, revelation 2.0×, betrayal 2.2×, **death 2.5×**), chaos factor (0.8–1.4×), dominant emotional intensity (0.9–1.3×), and turn-to-turn rate of change (0.95–1.2×), clamped to 5–40 items. Scene type is auto-inferred from keyword sets when not supplied.
    - **Problem attacked:** Fixed windows waste tokens on idle turns and starve pivotal scenes of the history they need.
    - **Numbers:** Window range 5–40 items; worst case (death scene, max) ≈ 40 items × ~50 tokens ≈ **2,000 tokens** — the budget blow-up is bounded by design.
    - **Ollama application:** Scale how much memory Ollama injects by the *stakes of the current moment* in the chat (quiet talk vs confession/breakup/fight) instead of a fixed top-k — more recall exactly when continuity matters most.

12. **Prompt budgeting with real token counting** — *Implemented* (`systems/prompt_budgeter.py`); channel-allocation design in Sprint 5 (T5-1).
    - **Mechanism:** Count tokens exactly with tiktoken (cl100k_base) when available, falling back to ~4 chars/token, and allocate the window deliberately. The Sprint 5 design formalizes it: reserve system prompt (~4,000), current message (~2,000), and response (~4,000) off a 128k window first, then split the remainder across memory channels — **episodic 25%, semantic 35%, procedural 15%, spatial 10%, heuristic 15%** — filling each channel by importance, then access count, and stopping hard at the channel cap.
    - **Problem attacked:** Memory injection that overflows or crowds out the actual conversation; unbudgeted recall is how long chats silently lose their system prompt/persona.
    - **Numbers:** Ratios and reserves as above; selection is importance-descending with no overflow permitted.
    - **Ollama application:** Give Ollama's memory injector a hard per-channel budget computed from the model's actual context size — persona/system and the live exchange are reserved *first*, memory gets what remains, by type.

13. **Temporal validity & supersession — memories that can stop being true** — *Designed with schema + tests* (Sprint 5, T5-2, for the Mímir Well line of the same architecture).
    - **Mechanism:** Facts carry `valid_from` / `valid_until`, a `superseded_by` pointer, and an `is_current` flag. Updating a fact ("I'm vegetarian" → "I eat fish now") stores the new fact and marks the old one superseded rather than deleting or duplicating it; recall queries filter to current-and-in-window facts only. Time-bounded facts ("staying at Hotel Viking until Friday") expire on their own.
    - **Problem attacked:** Append-only memory resurrects stale facts forever; contradictory old/new preferences both get injected and the model flip-flops.
    - **Numbers:** Recall-quality test specified: superseded memories must never appear in current recall.
    - **Ollama application:** Any Ollama memory layer needs update semantics, not just append — supersede-with-provenance keeps long chats from being haunted by facts the user/character has moved past.

14. **Formal memory typing: episodic / semantic / procedural / implicit** — *Designed* (Sprint 5, T5-3).
    - **Mechanism:** A `memory_type` column auto-inferred from category, with a *different selection strategy per type*: episodic = recent + high emotional valence; semantic = high importance + frequently accessed; procedural = always include when task-relevant; implicit = inject as behavioral nudges, not explicit text.
    - **Problem attacked:** Treating a cherished moment, a stable preference, and a learned behavior as interchangeable rows makes recall both noisy and tone-deaf.
    - **Numbers:** Category→type map covers the engine's live categories (e.g. `preference`/`knowledge` → semantic, `lesson` → procedural, saga moments → episodic).
    - **Ollama application:** Type Ollama chat memories at write time (moment vs fact vs habit) — retrieval and injection style should differ by type, especially "implicit" traits that should steer tone without being quoted back.

15. **Automated compression/consolidation (the Eir pipeline pattern)** — *Partially implemented* (Eir v1.0 consolidation pipeline recorded in MASTER_TODO with 11 tests; auto-compress step designed as Sprint 5 T5-4).
    - **Mechanism:** A background consolidation pass clusters 3+ low-importance (≤6) episodic memories sharing category/tags within a 7-day window, replaces them with one semantic summary (importance = cluster max + 1), and marks originals superseded — **recoverable, not deleted**. Guardrails: never compress importance ≥ 7, never compress semantic/procedural memories, log every compression. The Sprint 5 gap analysis also records the surrounding machinery as already-done in this architecture: **Hebbian learning (Muninn STDP — co-recalled memories strengthen each other)** and **Eir decay** of unreinforced memories, on a three-tier "Three Wells" base (Urðr/Mímir/Hvergelmir).
    - **Problem attacked:** Memory stores grow monotonically; without consolidation, recall drowns in trivia and storage balloons over long campaigns.
    - **Numbers:** Cluster threshold ≥3 memories, importance ≤6; Eir v1.0 shipped with 11 passing tests.
    - **Ollama application:** Run consolidation as a between-sessions job for Ollama chats — compress trivia clusters into summaries, keep originals recoverable, and let co-retrieval strengthen associations (Hebbian) while unreinforced trivia decays.

16. **Web of Wyrd — knowledge graph + Graph-RAG over flat vector RAG** — *Planned* (Plan T3-D, high complexity; a SQL edge-layer variant is designed in Sprint 6).
    - **Mechanism:** Unify scattered state (character YAMLs, 100+ lore charts, the live relationship graph, session memory, location connections) into one directed graph: entities (Character, Location, Faction, Item, Concept) and typed edges (kinship, loyalty, rivalry, resides_in, controls, connected_to, **witnessed**, holds_quest, debt, oath, enemy, ally). Retrieval = depth-limited BFS from the focal entities (NPCs present + player + location; max depth 2, max ~15 nodes) plus Leiden community detection, rendered by a `WyrdContextAssembler` into a structured prompt block that *replaces* flat vector-RAG lore. The Sprint 6 variant stores edges in SQL (`wyrd_edges` with strength 0–10) and traverses multi-hop in both directions.
    - **Problem attacked:** Flat RAG returns isolated, textually-similar facts; the model can't know that the forge connects to the barracks, or that an NPC *witnessed* the player's betrayal three sessions ago — relationships are where continuity actually lives.
    - **Numbers:** Justification cited: Microsoft GraphRAG (2024) — graph retrieval outperforms vector RAG on correctness because it retrieves *connected* context. No in-engine benchmark recorded.
    - **Ollama application:** For character chats, a small entity/relationship graph (who knows whom, who saw what, who owes what) traversed from the current scene's participants will beat pure embedding search for the callbacks that make a character feel like they remember.

17. **Entity Canonizer — "If the AI names it, it becomes real"** — *Implemented* (`session/entity_canonizer.py`).
    - **Mechanism:** Scan every AI response for newly-invented entities (characters, locations, items, factions); automatically create persistent stub data files for them. Stubs start minimal and grow through subsequent play, so an offhand invented name becomes a tracked, recallable part of the world instead of a one-turn hallucination that later contradicts itself.
    - **Problem attacked:** Generative drift: the model invents people/places, forgets them, then re-invents them differently — a top source of continuity breaks in long generative sessions.
    - **Numbers:** None recorded.
    - **Ollama application:** Canonize entities a character invents mid-chat into the memory store on first mention — cheap insurance against the model contradicting its own inventions 200 turns later.

18. **Saga Gravity — memories that gain weight with age** — *Implemented* (`systems/saga_gravity.py`, Myth Engine v4.2.0).
    - **Mechanism:** Significant events become narrative "anchors." Each anchor's gravity **grows 5% per turn (exponential)**; re-mentioning a theme reinforces its anchor (+0.5); the set is capped at 20 anchors, culled to the strongest 15. Old, heavy anchors naturally resurface in narration and NPC behavior — the opposite of recency decay.
    - **Problem attacked:** Pure recency/decay models make long stories forget their founding traumas, oaths, and debts — the very things a saga (or a long relationship chat) should keep circling back to.
    - **Numbers:** Growth rate 1.05×/turn; reinforcement +0.5; cap 20 → cull 15.
    - **Ollama application:** Counterweight to decay: let a few user-chosen or high-importance chat events *appreciate* in retrieval priority over time, so a long-running character keeps returning to what actually matters in the relationship.

19. **Saga Continuity Validator — pre/post-turn constraint checking** — *Implemented* (`systems/saga_continuity.py`).
    - **Mechanism:** Before narration, gather canonical constraints from the memory store (current location, time of day, **dead characters**, …). After generation, check the output against the constraint set, score violations with severity weights, and flag `needs_repair` when the score demands it.
    - **Problem attacked:** Retrieval alone doesn't stop the model from resurrecting the dead or teleporting the scene; continuity needs a *verifier*, not just better context.
    - **Numbers:** Severity weights/thresholds are data-driven YAML; no violation-rate statistics recorded.
    - **Ollama application:** A lightweight post-generation check against hard facts in memory (names, deaths/breakups, established boundaries) with a repair/regenerate trigger is a memory-*enforcement* layer Ollama stacks usually lack.

20. **Emotional memory as first-class data** — *Implemented in part* (`systems/emotional_engine.py`, emotional context on memory nodes); cascade/dissonance parts are *design docs* (`Fate-Weaver_Protocol…md`, the 174,619-byte `AI Viking TTRPG Emotional Engine Modeling Theory.md`).
    - **Mechanism:** Memories carry an emotional-context vector (e.g. fear 0.3 / joy 0.7); context building surfaces each present character's dominant emotion with intensity. The Fate-Weaver design extends this: emotional states *propagate through memory* — an anger spike toward a character automatically degrades their trust vector over time (organic rivalries/betrayals), and a Cognitive Dissonance Engine tracks friction between a character's core values and their recent remembered actions, generating stress that can force behavior shifts.
    - **Problem attacked:** Fact-only memory produces characters who remember *what* happened but not *how it felt*, so emotional continuity (grudges, gratitude, trauma) evaporates between sessions.
    - **Numbers:** Emotional resonance is also one of the five scored retrieval factors in #7.
    - **Ollama application:** Tag Ollama chat memories with the emotional state at the time and let strong emotions bias both retrieval and later relationship values — how a character *feels about* the past is the memory users actually notice.

21. **Hierarchical memory tree with symbolic links + cross-domain linking** — *Implemented* (`yggdrasil/cognition/hierarchical_memory.py`, `domain_crosslinker.py`, `gap_analyzer.py`, `huginn_advanced.py`, unified by `memory_orchestrator.py`).
    - **Mechanism:** Instead of flat RAG, memories live in a tree hierarchy with **symbolic links connecting related memories across domains**, so one retrieval can pull a large, coherent, cross-domain context set with its semantic relationships intact. An orchestrator exposes store/retrieve/update/link/traverse/search/analyze as one interface, and a gap analyzer looks for missing links/knowledge.
    - **Problem attacked:** Flat stores can't represent "this memory belongs to three stories at once"; hierarchy + links preserve structure that chunking destroys.
    - **Numbers:** 26 memory node types enumerated in the tree's type system (fact, entity, event, relationship, rule, protocol, character, location, quest, dialogue, narrative, emotion, combat, prophecy, summary, …).
    - **Ollama application:** A folder-tree memory store with cross-links (human-browsable, git-friendly) is a viable local-first alternative to a vector DB for Ollama — and the user can inspect and correct what the character "remembers."

22. **NSE2 redesign: truth vs belief, provenance, rumor mutation, principled forgetting, event sourcing** — *Design only* (`Norse-Saga-Engine-2` docs `02_WYRD_WORLD_MODEL.md`, `04_URDR_HISTORY_MEMORY_AND_KNOWLEDGE.md`, `05_SKULD…`, `10_EVENT_SOURCING_SAVES_AND_REPLAY.md`; 15 design docs, no engine code yet).
    - **Mechanism:** Five linked ideas. (i) **Canonical truth and per-character belief are separate record types that may contradict** — "Erik killed Björn" (canonical, confidence 1.0) coexists with Astrid's belief "Olaf killed Björn" (confidence 0.72, source: rumor from Ingrid); confidence ≠ truth, so characters can be confidently wrong. (ii) **Every knowledge claim carries provenance** — direct witness, trusted witness, rumor, legal judgment, traveler, written record, ritual revelation, inference, or deliberate deception — and history queries respect it (`who_witnessed(event)`, `why_does(entity, believe=X)`, `conflicting_claims_about(subject)`). (iii) **Rumors are modeled as transmission**: event → witness memory → conversation → rumor copy → *mutation/simplification* → reputation effect → retelling. (iv) **Forgetting is a designed function** of time, salience, relationship relevance, trauma, repetition, ritual/legal importance, and personal goals — with critical promises and kin deaths explicitly decay-resistant. (v) **Event sourcing**: an append-only event log is the authority; current world state (ECS-style "WYRD") is rebuilt by a reducer over events, snapshots are *caches only*, and the log enables replay, branching ("what-if" sandboxes that can't touch the canonical branch), and explainability — a "Why does Astrid hate me?" query traces evt_811 insult → resentment +0.30, evt_845 broken oath → trust −0.25, evt_901 rumor → current resentment 0.71. Governing law: *"The simulated world is authoritative. The AI interprets and narrates it, but does not secretly become it"* — narration never writes state directly; only validated engine operations do.
    - **Problem attacked:** V1's memory couldn't represent *who knows what, how they learned it, or whether it's even true* — so NPC knowledge was omniscient and uniform, contradictions corrupted the world, and emergent behavior was unexplainable.
    - **Numbers:** Worked examples use concrete deltas (resentment +0.30, trust −0.25); relationship state is multi-dimensional (affection, trust, fear, respect, desire, resentment, obligation, kinship closeness, political alignment, commercial reliance) rather than one friendship score.
    - **Ollama application:** The deepest transferable set for character chats: keep an append-only event log as ground truth (state = fold over events), track *per-character beliefs with sources* instead of one global truth, and make forgetting a tuned function — this is how a local Ollama character stays consistent, fallible, and debuggable over months of chat.

23. **Memory security: injection guard, audit trail, per-user namespacing** — *Designed* (Sprint 7, T7-1–T7-3).
    - **Mechanism:** Validate memory *writes* against prompt-injection patterns ("ignore previous instructions", "you are now…", fake system tags) and length caps before anything enters the store; sanitize stored content; log every store/update/delete/supersede/compress action with source, timestamp, and a SHA-256 of the content; add a `user_id` namespace column (default single-user) so multi-user isolation needs no later schema surgery.
    - **Problem attacked:** Memory is an attack surface — poisoned memories persist and re-inject themselves every session; without an audit trail you can't tell what entered the well or when.
    - **Numbers:** Content cap 10,000 chars per memory in the guard design.
    - **Ollama application:** Any persistent Ollama memory must treat stored text as untrusted input on every future injection — guard at write, audit always; this matters more, not less, for always-on local companions.

24. **Recall quality as a measurable benchmark** — *Designed as a test suite* (Sprint 5, T5-5).
    - **Mechanism:** Treat retrieval like a product metric: precision@k on seeded stores, recall latency under load, superseded-facts-must-not-surface tests, temporal-expiry tests, budget-selection tests (highest-importance first, never over budget).
    - **Problem attacked:** Memory systems are usually vibe-tested; regressions in recall quality ship silently.
    - **Numbers (test thresholds):** precision ≥ 0.7 at k=10; recall < 50 ms over a 1,000-memory store.
    - **Ollama application:** The Forge should adopt these exact acceptance shapes — a seeded-store precision/latency/staleness suite is the difference between "memory feels better" and "memory *is* better."

*Also present in the tree, noted without full entries:* `systems/dormant_registry.py` (dormant entities kept out of active context until reactivated), `systems/fate_threads.py` (open narrative threads tracked until resolved), `systems/relationship_graph.py` (live runtime relationship graph feeding #16), `core/dream_system.py` + `systems/world_dreams.py` (off-line "dream" processing of world/memory state), and `Mímir-Vörðr_The_Warden_of_the_Well.md` (a guardian/steering concept for the memory well).

---

## (c) Other game / engine / world projects found with memory-relevant material

1. **Norse-Saga-Engine-2** — `hrabanazviking/Norse-Saga-Engine-2` (private; local copy `~/workspace/your_files/repos-ingest/Norse-Saga-Engine-2/`). The from-scratch redesign; mined as entry #22 above (Urðr history/belief layer, WYRD ECS present-state, Skuld consequence/obligation layer, Verðandi event bus, event-sourced saves/replay). Design docs only.
2. **WYRD Protocol — World-Yielding Real-time Data AI world model** — `~/workspace/WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model/` (also `hrabanazviking/WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model`). Core memory idea: **memory externalization** — move the world model out of the LLM's fleeting context into a deterministic Entity-Component-System ground truth, explicitly to cut hallucinations about location/object state and keep the world consistent "even when the LLM's memory fluctuates." The direct ancestor/generalization of NSE2's WYRD layer.
3. **Yggdrasil Distributed Inference System** — `hrabanazviking/Yggdrasil-Distributed-Inference-System`; build tree `~/workspace/yggdrasil-build`, roadmap `~/workspace/your_files/yggdrasil/YGGDRASIL_BUILD_ROADMAP_2026-10-30.md` (244 slices). Not a game, but its Part V is an **Urðr memory graph**, flanked by a Verðandi scheduler and Skuld verifier/projection — the NSE Norn-memory triad scaled into infrastructure. Also relevant: `hrabanazviking/RuneForgeAI-Project-Hlidhskjalf`, whose description credits "Yggdrasil's autonomous cognitive engine for causal world modeling, **persistent memory**, and local neural voice synthesis."
4. **Heathen Emergent Reality Engine / H.E.R.E.T.I.C.** — `hrabanazviking/Heathen-Emergent-Reality-Engine-Thoughtform-Intelligence-Companion` (local copy in `~/workspace/your_files/repos-ingest/`). Agentic thoughtform characters with **persistent memory**, VR/Unity embodiment; its task series includes dedicated persistent-memory work (`TASK_HERETIC_v0.6.3_VERKMINNI.md`, `v0.6.3.1_PERSISTENT_VERKMINNI` — *verkminni* = work-memory).
5. **MindSpark: ThoughtForge** — `hrabanazviking/MindSpark_ThoughtForge` (local build `~/workspace/mindspark-build`). A conversation engine for tiny "GPT-Nothing-class" local models built on **guided memory and lean cognition** — the same memory problem attacked from the opposite end: how much continuity can you fake for a model too small to hold context, on edge hardware. Highly relevant to small-model Ollama use.
6. **Mythic Agent Coder CLI** — `hrabanazviking/Mythic_Agent_Coder_CLI`. Coding tool, not a game, but its headline features are a **dual-layer Vector RAG "subconscious" memory** and an **auto-compacting context engine** — Volmarr's memory ideas applied to agent tooling, and a useful compaction reference.
7. **The Mímir Well / Eir / fact_store ecosystem** (Hermes-side agent OS, referenced throughout `SPRINT_5_MEMORY_MATURITY.md` as running code on the Pi at `/home/pi/mimir-well/`, `/home/pi/eir/`). This is where several NSE-lineage ideas (Three Wells tiers, Hebbian STDP, Eir decay/consolidation, 3,537+ stored facts) are recorded as *already done* for the agent herself rather than for game NPCs — the Sprint 5–7 entries (#12–15, #23, #24) are its forward plan. Worth a follow-up mine of its own if the Forge wants the agent-OS variant.
8. **Sagnaskemma** — `~/workspace/Sagnaskemma` (GitHub: `Sagnaskemma-Volmarrs-D-and-D-Lore-Treasure-Trove`). The Norse D&D lore trove + Python engine (`engine/saga.py` chronicle, `wyrd.py`, `skald.py`) designated as Samtal's game heart; memory material is lighter (saga chronicle as persistent record) compared with NorseSagaEngine.

---

## Caveats

- NorseSagaEngine's plan documents are aspirational in places: every figure labeled "target" above comes from a plan's success-metrics section, **not** from a benchmark run found in the repo. Implemented-vs-planned labels follow the presence/absence of real modules in the local copy and each plan's own status line (T3-A/T3-B say "PLANNED" in their headers, yet their modules — `context_optimizer.py`, `memory_hardening.py` — exist in `systems/` and are wired into `enhanced_memory.py`, so they are reported as implemented; T3-D and the Sprint 5–7 items have no corresponding modules in the NSE tree and are reported as designed/planned).
- The local VM copy is an ingest snapshot; the GitHub repo (private, default branch `Development`) may hold newer material not present locally.
