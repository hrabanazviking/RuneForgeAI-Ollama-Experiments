# Ollama Memory Forge — Local-Projects Research Dossier

Read-only mining of Volmarr's own projects on this VM, 2026-11-15.
Clean-room law honoured throughout: mechanisms restated in our own words,
no code or text lifted from any studied project (SillyTavern is AGPL —
behaviour/notes only). Ordered by expected value for this campaign:
long character chats in Ollama where (a) resident character context is
not reprocessed each turn, (b) character/system information can never
be truncated away, (c) hallucination drops through better memory use,
and (d) recalled memory is presented in a stable order.

Baseline disease this dossier is against (measured, not assumed):
Ollama-via-Voxta re-evaluating a ~14,712-token prompt from cold took
52.1 s before the first word, while generation itself ran at a healthy
12.11 tok/s (Q4) / 7.65 tok/s (Q8_0). The problem is prompt re-processing
and context loss, not decode speed.
Evidence: `~/memory/2026-11-14.md` VOXTA QUICK-FIX ROUND (~08:22 EST)
and HS-3 bench entry (~10:25 EST).

---

## 1. Exact-prefix KV reuse — process the stable prefix once

- **Source:** Project Aesir, HIP-serve line HS-1/HS-3.
  Evidence: `~/memory/2026-11-14.md` §1789–1791 (engine audit + MAP),
  §2015 (HS-1/HS-3 banked: HS-1 `1a092c1d`, HS-3 `73d4482e`);
  Aesir source named there: `core/prompt_prefix.mojo`
  (`reusable_prompt_prefix()`), `tests/test_cuda_prompt_prefix.mojo`.
- **Mechanism (own words):** Keep the token stream a session has already
  committed. On the next turn, find the longest token-exact prefix the
  new prompt shares with that stream, keep its KV entries in place, and
  only evaluate the suffix. The final shared token is always recomputed
  (a boundary-safety rule). The serve reports reused vs. evaluated
  tokens separately, so the saving is measured, not claimed.
- **Apply to Ollama:** This is the campaign's core question about
  Ollama's own prefix/KV reuse across the stateless full-resend pattern
  Voxta-style clients use. Verify what Ollama already reuses when the
  same prefix is resent, then make the chat path guarantee it: same
  model, same runner/session, byte-identical prefix bytes (see #4), and
  no per-turn reordering or re-templating ahead of the history. Where
  Ollama's reuse is only within a loaded model's lifetime, pair with
  keep-alive / session pinning for the active character chat.
- **Expected gain:** Highest in the dossier. HS-3's small proof: turn 2
  reused 46 tokens, 610 ms vs. 825 ms turn 1 — at toy scale. At Voxta
  scale the prize is avoiding most of a 14.7k-token, 52 s re-chew
  every turn.
- **Cost/risk:** Low–medium. Mostly verification + prompt discipline;
  a fork change only if Ollama discards reusable KV on resend
  boundaries. Risk: silent template drift (whitespace, date stamps,
  reordered blocks) makes prefixes differ and reuse silently vanish —
  needs a reused-token counter surfaced per turn as the regression alarm.

## 2. Token-level session residency — no seam loss between turns

- **Source:** Project Aesir HS-6 (banked `23ee96d7`).
  Evidence: `~/memory/2026-11-14.md` §2015 (seam finding), §2135
  (HS COMPLETE: "token-level session residency — seam loss gone by
  construction"), §1790 (SessionManager was bookkeeping only; real
  residency had to be built as per-session KV arenas behind it).
- **Mechanism:** A named session owns its KV arena across requests.
  Resending a conversation that extends past a generation seam
  previously lost ~6 tokens at the seam; holding the actual token-level
  state in the session removes that class of loss by construction —
  the model continues from state, not from a re-serialized transcript.
- **Apply to Ollama:** Prefer a long-lived session/runner per active
  character chat over cold per-request reconstruction; if the client
  must resend history, reconcile against the session's committed token
  count rather than trusting the resent text to re-tokenize identically.
  Add a seam test: multi-turn chat split at awkward boundaries must
  produce the same tokens as the uninterrupted run.
- **Expected gain:** Correctness as much as speed — eliminates a subtle
  drift/hallucination source at every turn boundary in long chats.
- **Cost/risk:** Medium. Resident sessions pin KV memory per chat
  (see #6, #16 for bounding). Risk: stale session vs. edited history
  (user edits/deletes a message) — needs an explicit invalidation rule:
  any edit before the tip invalidates from that token onward.

## 3. The unpushable post-history anchor — identity that cannot be truncated

- **Source:** Project Aesir HS-5 (banked `8f98b2a5`); Voxta study;
  SillyTavern study; proven live in Voxta on 2026-11-14.
  Evidence: `~/memory/2026-11-14.md` §1790 point (4), §2135;
  `~/workspace/your_files/studies/voxta/03-prompt-and-formatting.md`
  (assembly order, PostHistoryInstructions rendered after all history);
  `~/workspace/your_files/studies/sillytavern/02-prompt-assembly.md`
  (post-history slot is the last instruction before generation);
  live fix: `~/memory/2026-11-14.md` VOXTA QUICK-FIX ROUND — the
  character's identity core was moved into PostHistoryInstructions,
  "re-asserted after all history every turn — structurally unpushable."
- **Mechanism:** Reserve a slot that is composed *after* the entire
  conversation history, at serve/session composition time. It is never
  written into stored history and never part of the committed prefix
  stream, so (a) history growth and head-truncation can never push it
  out, and (b) it does not churn the cached prefix (#1). It carries the
  short identity core: who the character is, voice guard, hard facts
  that must never be contradicted.
- **Apply to Ollama:** Ollama itself has no post-history slot — this
  lives in the layer that assembles the request (client, proxy, or a
  forked serve path). Implement as: stored history → anchor appended
  last, every turn, from the character definition (not from chat
  state). Prove it with the campaign's own planned test: a chat driven
  past the context window must still answer identity questions
  correctly from the anchor alone.
- **Expected gain:** Directly delivers campaign goal (b). Cheap
  insurance against the classic long-chat failure where the character
  forgets who she is once the system prompt scrolls out.
- **Cost/risk:** Low. A few dozen–few hundred tokens per turn,
  deliberately uncached-tail cost. Risk: over-stuffing the anchor
  (it is re-read at full attention every turn — keep it to the true
  identity core; everything else belongs in recall, #7–#10).

## 4. Stable-order memory injection under a token budget

- **Source:** Project Aesir HS-7 (banked `fd53cc8c`); Voxta study.
  Evidence: `~/memory/2026-11-14.md` §1753, §1790 point (5), §2135;
  `~/workspace/your_files/studies/voxta/04-memory-system.md`
  (Recall mechanics: ranked, taken until a token budget fills,
  "rendered in a stable order — explicitly so the prompt prefix stays
  cache-friendly across turns").
- **Mechanism:** When recalled entries are injected, admit whole
  blocks in a fixed, deterministic order until a token budget is
  spent, and make admission append-stable: a newly recalled entry
  goes at the end rather than reshuffling everything already sent.
  Reordering recalled memories every turn destroys prefix caching
  even when the memories themselves barely change.
- **Apply to Ollama:** Any memory/lore injection layer in front of
  Ollama must sort by a stable key (e.g. pinned first, then a fixed
  entry order — never by this turn's raw relevance score alone),
  admit whole entries only, and log per-turn reuse counters (#1) so
  a churn regression is visible immediately.
- **Expected gain:** High and multiplicative with #1: it is what makes
  prefix reuse survive the presence of a memory system at all.
- **Cost/risk:** Low. Discipline, not machinery. Trade-off accepted:
  marginally less "perfect" relevance ordering in exchange for a
  cacheable prefix — the right trade at 14k-token scale.

## 5. Hybrid-state snapshots — checkpoint *all* of the model's state, not just KV

- **Source:** Project Aesir Qwen35 adapter line, Q35-5 (banked
  `88c71564`).
  Evidence: `~/memory/2026-11-14.md` §2289–2293 (Q35-5 entry):
  snapshot restores bit-exact (SSM / conv / KV diffs 0.0); a stateless
  resend reused 72 of 90 tokens via snapshots *after residency was
  destroyed*; store bound of 4 snapshots per session; each 27B
  snapshot ≈158.9 MB of recurrent + convolution state plus KV.
  Context: `~/workspace/CURRENT_STATE.md` HIP-serve line (the 27B is
  a hybrid `qwen35` model — most layers are recurrent, only some are
  attention; its state is not a KV cache).
- **Mechanism:** For hybrid architectures (recurrent/SSM layers +
  attention layers), a reusable checkpoint must capture every kind
  of per-token state — recurrent state, convolution state, and KV —
  as one snapshot keyed to a token position. Restoring it lets even a
  fully stateless resend skip re-processing the covered prefix.
- **Apply to Ollama:** Critical if the campaign's target models
  include hybrid Qwen-family models (the 27B/40B Heretic line Ollama
  currently serves to Voxta is exactly this kind). Check whether
  Ollama's KV-cache reuse covers recurrent state at all for such
  models, or silently reprocesses / mis-restores. If it does not,
  this is the deepest fork-level item in the dossier — and the one
  most likely to explain unexplained long-chat slowness or drift
  on hybrid models specifically.
- **Expected gain:** Potentially the difference between prefix reuse
  existing and not existing on the campaign's flagship model class.
- **Cost/risk:** High. Snapshot storage is real (≈159 MB × bounded
  count per session for a 27B — the bound of 4 is part of the design,
  not an afterthought), and restore must be proven bit-exact per
  state component, as Aesir proved it, before it is trusted.

## 6. Resident-format loading + a measured-fit rule — never materialize a bigger copy

- **Source:** Project Aesir Q35-3r (Q8_0-resident load path, banked
  at `efa400d6`) and the Q35 parent gate.
  Evidence: `~/memory/2026-11-14.md` §2293 (parent gate ruling),
  §2330, §2871–2873; `~/workspace/CURRENT_STATE.md` (27B now served
  in "Q8_0-resident CPU config", `weight_load_mode q8_0_resident`).
- **Mechanism:** The naive loader converted weights to a wider
  in-memory format, pricing a 27B load at ~57 GB peak for a ~28.6 GB
  model. Loading and keeping weights in their stored quantized
  format halves residency. Around it sits a hard operational rule:
  never attempt a load unless measured free memory ≥ expected peak
  + a margin (8 GB in the ruling), with the attempt fenced so a
  failure kills only itself and never evicts a live service.
- **Apply to Ollama:** Audit Ollama's load path on the Z13-class
  unified-memory machine for any widening/materialization step, and
  for what coexists with the KV cache at `num_ctx 16384`. Adopt the
  measured-fit rule operationally for the forge's own benches:
  no bench or load test starts without a free-memory check and a
  fence — doubly important on unified memory shared with the desktop.
- **Expected gain:** Frees tens of GB that can instead hold KV,
  snapshots (#5), and longer context — memory efficiency in the
  most literal sense.
- **Cost/risk:** Medium to audit, low to adopt as an operating rule.
  Risk: resident-format compute paths can be slower per token;
  Aesir's own record keeps this honest (its Q8_0-resident config was
  chosen for the serve; its HIP decode stayed "experimental, not
  chosen") — measure decode before and after, do not assume.

## 7. Memory honesty lifecycle — superseded and absorbed, never silently dropped

- **Source:** Voxta study (Rúnmál dossier).
  Evidence: `~/workspace/your_files/studies/voxta/04-memory-system.md`
  (Layer 2); restated as an adoption in
  `~/workspace/your_files/studies/voxta/08-runmal-implications.md` #6.
- **Mechanism:** Extracted facts are versioned records, not prompt
  text. When a fact stops being true, the new wording *supersedes*
  it: only the new wording is recalled, the old stays in the record
  as history. When a standing model of the person now covers a fact,
  the fact is *absorbed*: kept, no longer separately recalled.
  Pinning exempts a fact from absorption. Every item carries its
  source chat and timestamps, and all of it is user-visible and
  user-editable.
- **Apply to Ollama:** Ollama has no memory store — this is the
  specification for the memory layer the forge builds beside it.
  The anti-hallucination value is direct: a model that is fed both
  "she lives in X" and the superseded "she lived in Y" as equal
  facts will eventually assert the wrong one. Recall must only ever
  surface current, uncovered facts, while nothing is ever deleted
  silently enough to become un-auditable.
- **Expected gain:** High for accuracy in long-running character
  relationships, where facts genuinely change over weeks of chat.
- **Cost/risk:** Medium. Needs an extraction/merge step (#10) and a
  small store with provenance. Risk: a wrong supersession buries a
  true fact — mitigated by keeping the old wording visible and
  reversible, which is the point of the design.

## 8. Memories vs. Understanding — events recalled, people always present

- **Source:** Voxta study, Layer 3.
  Evidence: `~/workspace/your_files/studies/voxta/04-memory-system.md`
  (Layer 3: subject models "always injected… memories answer 'what
  happened'; understanding answers 'who is this person'");
  Aesir scope note confirming the split stays app-layer:
  `~/memory/2026-11-14.md` §1753.
- **Mechanism:** Two different kinds of memory with two different
  physics. Episodic facts are recalled selectively by relevance.
  A compact standing model of each person (dispositions, how they
  like to be treated, sensitivities — and the character's model of
  herself) is rewritten occasionally, versioned, and injected on
  every turn without recall, because it is small and always relevant.
- **Apply to Ollama:** In the forge's memory layer, keep the standing
  model inside (or immediately beside) the anchored character block
  (#3) — it inherits the anchor's cannot-be-truncated guarantee —
  and keep episodic recall on the stable-order budgeted path (#4).
  Do not let a relevance ranker decide whether the model knows who
  the user *is* this turn.
- **Expected gain:** High for character consistency: the failures
  users experience as "she forgot who I am / who she is" are
  understanding failures, not event-recall failures.
- **Cost/risk:** Low–medium. The standing model needs an occasional
  rewrite pass (#10) and a size cap; a stale standing model is worse
  than none, so its update provenance (which message last changed
  it) must be recorded, as in the source design.

## 9. Lorebook state machine — timing, groups, and whole-entry budgets

- **Source:** SillyTavern study (behaviour only, restated in our
  words; AGPL — nothing lifted).
  Evidence: `~/workspace/your_files/studies/sillytavern/03-memory-and-lorebooks.md`
  (entry anatomy + activation algorithm);
  `~/workspace/your_files/studies/sillytavern/10-runmal-implications.md` #5.
- **Mechanism:** Keyword-triggered lore entries carry a small
  per-chat state machine: once triggered an entry can stay active
  for a few further messages (sticky), then refuse to re-trigger
  for a while (cooldown), cannot fire before the chat is long
  enough (delay), fires only probabilistically if set, and competes
  inside mutual-exclusion groups so only one of several related
  entries fires. Admission is by a budget expressed as a share of
  total context, and entries are admitted whole or not at all —
  never truncated mid-entry. Triggered entries' text can itself
  trigger further entries, bounded by a recursion-step cap.
- **Apply to Ollama:** This is the specification for any lore/world
  layer feeding Ollama prompts. Without the timing layer, keyword
  lore feels like a broken record (the same entry re-injected every
  turn, eating budget and churn-risk); with it, lore is woven in
  occasionally and predictably — and whole-entry admission under a
  percentage budget guarantees lore can never eat the conversation
  or break the prefix discipline (#4) with a half-entry.
- **Expected gain:** Medium–high for world-rich character chats;
  prevents a whole class of repetition and budget blow-outs.
- **Cost/risk:** Low. Small, deterministic, local matching code.
  Main risk is authoring complexity — keep the common case
  (keywords + constant + pinned) one step, the state machine opt-in.

## 10. Three recall layers + an incremental summarization pipeline

- **Source:** SillyTavern study (three layers) + Voxta study
  (pipeline shape).
  Evidence: `~/workspace/your_files/studies/sillytavern/03-memory-and-lorebooks.md`
  (cumulative summary; vector recall over ~400-token chunks queried
  by the last messages; keyword lore);
  `~/workspace/your_files/studies/voxta/04-memory-system.md`
  (pipeline: summarize new range → merge into chapters → extract
  facts from the *summary* → merge facts (#7) → update standing
  models (#8); chat row records how far the pipeline has read, so
  it is resumable and incremental; summaries re-enter the prompt
  in a dedicated slot, replacing the raw history they cover).
- **Mechanism:** Three recall physics, deliberately separate:
  deterministic keyword lore (#9), semantic vector recall of old
  chat chunks, and one cumulative summary that rewrites and expands
  itself on an interval under a word cap instead of stacking
  summaries. The pipeline that maintains them runs in the
  background on a cheaper/faster model role where possible, works
  incrementally from a saved read-position, and extracts facts from
  the condensed narrative rather than per message.
- **Apply to Ollama:** This is how a chat longer than any context
  window stays coherent in front of Ollama: raw history fills what
  fits, the summary slot carries the compressed middle, vector
  recall resurfaces specific old scenes by meaning, and lore
  carries world facts. Background passes can be separate Ollama
  calls on a small model — the forge should bench that cost
  honestly against the foreground quality bought.
- **Expected gain:** High for very long chats; it is the only item
  here that addresses "the middle of the conversation is gone."
- **Cost/risk:** Medium–high. Summaries are lossy and can entrench
  an early misreading; extraction-from-summary inherits that bias
  (the source design names this trade openly). Mitigations: keep
  raw history retrievable (vector layer), make the summary
  user-editable/lockable, and never let the summary slot displace
  the anchor (#3).

## 11. Depth injection — pin a fact near the live end of the conversation

- **Source:** SillyTavern study.
  Evidence: `~/workspace/your_files/studies/sillytavern/02-prompt-assembly.md`
  (absolute/in-chat injection at a chosen depth with its own order
  and trigger; the card's built-in depth prompt, default 4 messages
  back; the author's note with depth + every-Nth-message frequency).
- **Mechanism:** Any injectable text can alternatively be spliced
  into the history a fixed number of messages back from the end, in
  a chosen role, instead of living at the top of the prompt where
  long history pushes it out of effective attention. A note can
  also pulse — included every Nth turn rather than every turn.
- **Apply to Ollama:** A complement to the anchor (#3), not a
  substitute: the anchor guarantees *presence*; depth injection
  buys *recency* for one rotating reminder (current scene state,
  an ongoing condition, "she is currently injured/travelling").
  In an Ollama-facing assembler this is cheap string placement —
  but note the tension: anything spliced into history changes the
  token stream and can break prefix reuse (#1/#2) unless the
  session layer, not the resent text, owns it. Prefer depth
  injection only for genuinely changing state, and keep it out of
  the committed prefix where the architecture allows.
- **Expected gain:** Medium. Outsized effect per token for
  long-chat coherence in the source ecosystem.
- **Cost/risk:** Low to implement, medium in interaction with
  caching — flagged above; use sparingly and measure reuse counters.

## 12. Ordered named-block assembly + an itemized "what we sent" inspector

- **Source:** SillyTavern study; Voxta study (formatter registry).
  Evidence: `~/workspace/your_files/studies/sillytavern/02-prompt-assembly.md`
  (default block order; fill-down greedy token budgeting — reserve
  reply length, reserve fixed blocks, fill history backwards newest
  first; per-block token counts with the model's real tokenizer;
  an itemized inspector of the last generation);
  `~/workspace/your_files/studies/sillytavern/10-runmal-implications.md` #1–2;
  `~/workspace/your_files/studies/voxta/03-prompt-and-formatting.md`
  (wire format per model family as small template files + a
  registry row — adding a family is data, not code).
- **Mechanism:** The prompt is an explicit ordered list of named
  blocks, each toggleable, each token-counted with the actual
  tokenizer, packed by a stated greedy rule, and inspectable after
  the fact block by block. Truncation, when it happens, is therefore
  a visible policy outcome (oldest history falls off), never a
  surprise.
- **Apply to Ollama:** Before forging Ollama internals, the forge
  needs this as its *measurement harness*: a canonical assembler
  for test chats that logs, per turn, block-by-block tokens,
  evaluated vs. reused tokens (#1), and exactly what was truncated.
  Every other idea in this dossier becomes provable or disprovable
  through that inspector. The formatter-registry point matters too:
  a wrong chat template for a model family is a silent quality bug
  that looks like a memory failure.
- **Expected gain:** Medium directly, high indirectly — it is the
  difference between tuning memory and guessing about it.
- **Cost/risk:** Low. Logging and discipline around calls the
  campaign already has to make.

## 13. The Ravens pattern — associative strengthening/decay + vector thought, pure reads

- **Source:** Huginn/Muninn ravens (Volmarr's own packages, v1.0.0).
  Evidence: `~/workspace/ravens/BUILD_NOTES.md` §1–2;
  `~/workspace/goals/huginn-and-muninn-ravens/GOAL.md`;
  publication record in `~/memory/2026-10-31.md` (Muninn = Hebbian
  associative memory; Huginn = vector-search retrieval; both
  stdlib-first, SQLite WAL, crash/self-healing tested).
- **Mechanism (own words):** Two cooperating stores. One keeps
  memory nodes linked by associations that strengthen when memories
  are used together and weaken with disuse; an explicit decay pass
  fades the unused and a consolidation pass merges redundancies —
  "sleep" for the memory store. The other does vector search over
  stored content for semantic retrieval. Two disciplines are the
  transferable core: (a) reads are *pure* — merely recalling a memory
  never silently rewrites the store; reinforcement happens only
  through explicitly named write operations; (b) each profile/user
  gets its own store — a shared default store that let one
  profile's memories bleed into another's was measured and ruled
  NO-GO in the Hermes integration.
- **Apply to Ollama:** If the forge builds episodic memory beside
  Ollama (#7, #10), this is the in-house, already-proven substrate
  to build it on instead of inventing a new one: associative
  strengthening gives "what reminds her of what" for free, decay/
  consolidation keep the store from growing into noise, per-chat
  stores prevent cross-character contamination, and pure reads keep
  recall compatible with stable-order injection (#4) — recall that
  mutates on read cannot promise a stable prefix.
- **Expected gain:** Medium–high, mostly by not re-inventing memory
  storage badly. Hallucination angle: consolidation + decay are a
  principled answer to stale-fact pile-up alongside #7.
- **Cost/risk:** Low–medium. Packages exist and are tested; live
  vector-server and embedder paths were honestly NOT PROVEN at
  publication (local fallback backend is the proven path) — bench
  the embedder choice before depending on semantic quality.

## 14. Continuity ledger + write-back distillation — memory survives the session

- **Source:** Heimdall research, Mind-Bridge continuity design;
  Samtal pattern it borrows from.
  Evidence: `~/workspace/heimdall-research/05-mind-bridge-continuity-and-voice.md`
  §2 (presence ledger, state packets, memory write-back pipeline,
  integrity rule) and §5 (Samtal borrowings: persistent message log
  as memory of record; seat identity independent of any connection).
- **Mechanism:** Continuity is a durable thread, not a live context
  window. A raw ledger records everything first, unsummarized.
  Later, a separate distillation pass turns raw episodes into dated
  notes, significant people/places get their own pages, and only
  reviewed, durable facts are promoted to the long-term record —
  raw → distilled → promoted, never straight from raw to canon.
  Two integrity rules ride along: every outbound action carries an
  *origin* marker (deliberate vs. reflexive), and only what was
  actually delivered counts as "said" (played-prefix accounting in
  the voice design) — the system must never remember saying words
  nobody heard. Before a new session, relevant people/place notes
  are pre-loaded so continuity is proven in the greeting.
- **Apply to Ollama:** For character chats that live across Ollama
  restarts and model swaps, the chat's memory of record must be a
  store outside Ollama (#7/#13), with this promotion discipline
  deciding what reaches the prompt. The origin/"actually said"
  rules map to a real Ollama-chat hazard: regenerated/swiped
  replies, interrupted generations, and unplayed drafts must not
  be distilled into memory as things the character said. Pre-load
  on session start is the write-side twin of recall (#10).
- **Expected gain:** Medium–high for multi-session characters;
  prevents false memories, which are hallucinations with a
  database behind them.
- **Cost/risk:** Medium. A distillation pass (background model
  calls, #10) plus editorial discipline. Samtal's own lighter
  version — a persistent hall log plus a bounded in-context history
  window (`~/workspace/samtal-mvp/samtal_agent.py`, history deque
  capped by `context_messages`) — is the minimal viable form.

## 15. Promotion with contradiction detection — ephemeral facts must earn canon

- **Source:** WYRD (world-model project), Phase 2 persistent memory.
  Evidence: `~/workspace/WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model/TASK_PHASE2_PERSISTENT_MEMORY.md`
  (SQLite + full-text-search memory store; a promotion engine moving
  facts EPHEMERAL → CANONICAL by scored thresholds; a contradiction
  detector on fact writes, with quarantine; a writeback engine
  turning turn output into store writes; thresholds in config).
  Note: that task file marks the build IN PROGRESS / unchecked —
  treat this as a proven *design*, not a proven implementation.
- **Mechanism:** New facts enter as ephemeral. A scoring pass
  promotes only facts that clear stated thresholds (repetition,
  corroboration, importance) to canonical status; a write that
  contradicts an existing canonical fact is detected at write time
  and quarantined for resolution instead of silently coexisting.
- **Apply to Ollama:** Pairs with #7 as the gate in front of it:
  #7 governs what happens when facts change; this governs whether
  a freshly extracted "fact" (possibly a model hallucination from
  the extraction pass itself) deserves to become memory at all.
  For character chats, canonical facts are what the anchor (#3)
  and standing model (#8) may draw on; ephemeral facts may be
  recalled (#4) but never anchored.
- **Expected gain:** Medium. Directly anti-hallucination: it stops
  one bad turn from permanently poisoning the character's memory.
- **Cost/risk:** Low–medium. Threshold tuning is the work; set
  them conservative (canon is hard to enter, easy to inspect).

## 16. Bounded per-session arenas + allocation discipline for KV/snapshot stores

- **Source:** MimirAlloc campaign (allocator research) read
  alongside Aesir HS-6/Q35-5's concrete bounds.
  Evidence: `~/workspace/goals/mimiralloc-forge/GOAL.md` and
  `~/workspace/goals/mimiralloc-z13-forge/GOAL.md` (clean-room
  allocator, contract-first, measurement-first, honestly graded
  WIN/TIE/LOSS against the system allocator — the Pi campaign was
  honestly graded as *losing* to glibc overall, which is itself the
  lesson: allocator cleverness must be measured, not assumed);
  concrete bounds from `~/memory/2026-11-14.md` §1790 (per-session
  KV arenas behind the session manager) and §2291 (snapshot store
  bound: 4 per session).
- **Mechanism:** Long-lived per-session state (KV arenas, hybrid
  snapshots) is allocated from a bounded, per-session pool with an
  explicit cap and an eviction order, rather than from the general
  heap where it fragments and competes with everything else on a
  unified-memory machine. Caps are part of the design contract
  (snapshots per session, context per session, sessions total),
  and any claim that a custom allocation strategy helps is benched
  against the stock one before adoption.
- **Apply to Ollama:** The forge's memory-efficiency work should
  specify, up front: KV bytes per token at the chosen context and
  KV quantization, max resident sessions, snapshot/cache caps, and
  what is evicted first under pressure — then measure Ollama's
  actual footprint against that budget on the target machine
  (flash-attention and KV-cache quantization settings belong in
  this audit; they were already named in Volmarr's earlier Ollama-
  on-Z13 scope, `~/memory/2026-11-14.md` §1176). Do not import a
  custom allocator; import the *budgeting discipline*.
- **Expected gain:** Medium. Prevents the failure mode where
  "better memory" quietly means "the machine swaps/dies at hour 3
  of a chat" — a live risk on unified memory (see #6).
- **Cost/risk:** Low as discipline; high (and not recommended) if
  read as "write an allocator for Ollama."

---

## Also skimmed — one line each

- **Second Brain** (`~/workspace/goals/second-brain-read-only-plug-and-auto-ingest/GOAL.md`):
  a read-only knowledge plug that auto-ingests new documents and
  reconciles them so only one copy of each idea is kept — the
  dedup/reconciliation rule is the transferable idea for lore and
  document banks feeding Ollama: one canonical copy, consulted
  read-only, never forked into the chat store.
- **Sagnaskemma** (`~/workspace/your_files/sagnaskemma/SAGNASKEMMA_TABLE_ROADMAP_2026-10-30.md`):
  a state-owner pattern worth copying for the memory layer — each
  domain owns its state, saves are atomic and revision-checked,
  and per-seat views are computed from truth inside the engine
  (a seat is only ever sent what it may know) — the same
  serve-views-never-truth rule a multi-character memory store needs.
- **Samtal** (`~/workspace/samtal-mvp/`): beyond #14, its durable
  lesson is self-healing presence (the Astrid Law in the Heimdall
  doc §5): a memory/session service that finds itself shut out
  must heal *out loud* and log it — silent memory failure is worse
  than loud failure, because the chat keeps going on false premises.
- **Rúnmál engine itself** (`~/workspace/goals/sovereign-ai-chat-app-clean-room/`):
  the studies above were commissioned for it, and its implication
  lists (`studies/*/10` and `08`) are the house's own ranked
  restatements — the forge should treat any disagreement between
  this dossier and those lists as a question to resolve, not a
  coincidence to ignore.

## Suggested campaign order implied by this dossier

1. Measure first: block inspector + reused-token counters (#12, #1).
2. Guarantee the anchor (#3) and stable order (#4) — cheap, proven
   at home on 2026-11-14, directly on the campaign's stated goals.
3. Prove/disprove prefix reuse and hybrid-state handling in Ollama
   for the actual target models (#1, #5), with resident-format and
   measured-fit discipline (#6, #16) around every bench.
4. Build the beside-Ollama memory layer on the honesty lifecycle
   (#7, #8, #15) over the Ravens substrate (#13), fed by the
   three-layer pipeline (#10, #9), with ledger/write-back
   integrity (#14) across sessions.
