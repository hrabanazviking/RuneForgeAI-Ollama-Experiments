# Research Corpus — Index

The RuneForgeAI Ollama Experiments research library: how LLM model runners work, how memory
works, and what our own Ollama experiments should learn from both. Built 2026-11-15 onward,
at Volmarr's commission, so that hard-won field knowledge lives in one sourced, dated,
usable place.

## How this library is organised

- `00-FIELD-MAP.md` — every significant model runner / inference engine / serving system
  we have found, with license, language, backend, and a one-line essence. Living document:
  the sweep keeps adding finds.
- `runners/` — one dossier per runner (OR-2). Clean-room: architecture, scheduling, KV
  design, memory management, quantization, kernels, session/prefix handling — in our own
  words, license recorded, ideas-to-steal section in each.
- `papers/` — one dossier per research paper (OR-3): full citation, the core idea in our
  own words, the paper's measured claims **as reported** (with their hardware context),
  and applicability notes for Ollama-on-a-6 GB-GPU and for Project Aesir.
- `BIBLIOGRAPHY.md` — the living bibliography for the whole corpus.
- `aesir/` — Project Aesir study (OR-4). Aesir is ours, so it is read freely; it is written
  in Mojo while Ollama is Go, so every idea is translated into Go/Ollama terms.
- `memory/` — the memory corpus (OR-6): memory as a science, from KV caches to DRAM to
  allocators, crowned by `memory/MEMORY-COMPENDIUM.md`.
- `synthesis/IDEA-LEDGER.md` — the ranked idea ledger handed to the Ollama build campaign.
- `MASTER-COMPENDIUM.md` — the distilled state of the art: how LLMs run, and how runners
  make them fast, lean, and truthful. Kept current as dossiers land.

## Discipline

- Every claim carries its source and a date; the field moves fast, and a 2023 claim and a
  2026 claim are different animals.
- Other projects are studied clean-room: behaviour and ideas only, never lifted code or
  text. Each project's licence is recorded in its dossier.
- Reported numbers are always labelled with the hardware and conditions they were
  measured under. Our own measurements are labelled as ours.
- Speculation is marked as speculation.

*Started 2026-11-15. Status: skeleton + field maps banked; dossiers flowing.*
