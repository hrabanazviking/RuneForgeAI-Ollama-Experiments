# Slice plan — Ollama Memory Forge (OM-1…OM-8)

Filed 2026-11-15 after OM-0 recon (recon-om0.md) and the IDEAS DOSSIER (IDEAS_DOSSIER.md).
Architecture decision: **a session/anchor layer in front of stock Ollama** (working name:
the forge layer), deployed on purplelongship; stock binary untouched until a slice proves
a need it cannot meet. His `ollama` GitHub fork (2026-08-14) is the fork point if that day
comes. Each slice names the failure it removes (per Volmarr's accuracy ruling).

**OM-1 — Measurement harness + accuracy battery v1.**
A canonical test assembler + runner (Python, on purplelongship): per-turn block-by-block
token counts, evaluated-vs-reused tokens, latency; the Sigrid battery formalized —
identity/fact probes before overflow, after overflow, and after long chats; stock scores
recorded as the baseline (pre-overflow 3/3; post-overflow 1/6).
*Failure removed:* unmeasured claims — every later slice proves itself against this.

**OM-2 — The Anchor Layer core.**
The forge layer: a small local HTTP service that accepts Ollama-style /api/chat, owns
sessions, and assembles prompts as: [pinned anchor: character + system] → [state card] →
[summary band] → [recent turns verbatim] → [post-history identity core] → [new user
turn]. Token-budgeted with the real tokenizer; overflow sheds whole oldest turns from
the middle band only — never the anchor, never the recent tail; sets num_ctx/num_keep
per request; passes everything else through to stock Ollama untouched.
*Failures removed:* lost anchor; incoherent overflow (the torn middle).

**OM-3 — Prefix-reuse guarantee.**
Session pinning + byte-identical prefix discipline: dynamic content (fresh recalls,
timestamps) admitted only into tail bands in stable order (D2); per-turn reuse counters
surfaced in the layer's log; Voxta-pattern test — dynamic injection per turn — must show
reuse preserved where stock collapsed (363/~570 re-evaluated on a one-word front edit).
*Failure removed:* per-turn reprocessing of resident context (Volmarr's law 2).

**OM-4 — Three-tier memory.**
Turns aging out of the verbatim band are replaced by structured per-turn summaries
(WHO/WHAT/WHEN/WHERE/WHY/HOW + emotion + open thread), written incrementally by a
background pass (same model, costed); session condensate above them; raw history kept
in the store, retrievable (lossless-first).
*Failure removed:* the gone middle — long chats degrade into summary, not amnesia.

**OM-5 — Fact ledger with honesty lifecycle.**
Extraction from summaries into a per-character fact store: provenance + timestamps,
supersede/absorb semantics, ephemeral→canonical promotion gate with contradiction
quarantine, pure reads, write-guard + audit log. Canonical facts may reinforce the
anchor; ephemeral ones may only be recalled. Includes drift-note and entity-canonizer
rules from D8 if the battery shows the need.
*Failures removed:* stale/superseded facts presented as current; hallucinated facts
canonized; cross-character bleed.

**OM-6 — Robust service deployment.**
Layer + Ollama as managed services on purplelongship: Ollama bound to localhost with
the correct context env for this build (OLLAMA_CONTEXT_LENGTH, not the ignored
OLLAMA_NUM_CTX), the layer exposed on the tailnet/LAN address clients actually use;
health checks that probe the API and answer, not just process liveness (the ghost-bind
lesson); keep-alive/session policy set deliberately; rollback = restore stock drop-ins.
NOTE: Tailscale being logged out is Volmarr's account action — the slice works around
it (localhost + LAN), never logs him in.
*Failure removed:* silent unreachability — "active" service serving nobody.

**OM-7 — Accuracy battery, full run: stock vs forged.**
Fact retention over long chats; identity consistency across overflow (headline proof:
drive a chat well past the window — stock scored 1/6; the forged layer must hold the
character intact); contradiction handling (a fact changes mid-chat; only the new one is
ever asserted); seeded-store recall suite (precision ≥ 0.7 @ k=10, < 50 ms @ 1,000
memories, superseded facts never surface).
*Failure removed:* accuracy by vibes — his "super much more accurate" becomes numbers.

**OM-8 — Speed & footprint gate + close-out.**
OM-0 workloads re-run against the forged stack: Voxta-pattern multi-turn latency
(stock per-turn ~5.3 s at ~1,000 tok assembled, CPU), cold long-prompt eval (~1,010
tok/s), generation (~13–14 tok/s — must not regress); memory footprint before/after
(RAM, KV bytes at working contexts, store growth per 100 turns); GPU-offload retest if
VRAM has freed. Final report with all numbers, and the repo question put to Yrsa if a
fork is ever needed (repo creation is Volmarr's alone).
*Failure removed:* a faster-but-wrong or heavier-but-quiet build shipping as "better."

Flow: OM-1 → OM-2 → OM-3 → OM-4 → OM-5 → OM-6 → OM-7 → OM-8, banking each slice's
proofs in hidden_files/ as it lands. Reporting moments per the commission: first
measured improvement, character-retention proof, first accuracy-battery result,
completion, blockers.
