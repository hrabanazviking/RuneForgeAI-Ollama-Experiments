# Research Corpus — Index

The RuneForgeAI Ollama Experiments research library: how LLM model runners work, how memory
works, and what our own Ollama experiments should learn from both. Built 2026-11-15 onward,
at Volmarr's commission, so that hard-won field knowledge lives in one sourced, dated,
usable place.

## How this library is organised

The corpus holds **79 files** in total, counted 2026-11-15: 4 at the root, 24 in
`runners/`, 36 in `papers/`, 13 in `memory/`, 1 in `aesir/`, and 1 in `synthesis/`.
Every file is listed exactly once below, under the section where it lives.

### Root volumes (4)

- `00-INDEX.md` — this index: the corpus's front door, its organisation, discipline, and
  maintenance rules.
- `00-FIELD-MAP.md` — OR-1 field map of model runners, inference engines, and serving
  systems (Version 2, 2026-11-15; 40 enumerated entries), each with licence, language,
  backend, and a one-line essence. Living document: the sweep keeps adding finds.
- `BIBLIOGRAPHY.md` — the living bibliography for the whole corpus: full citations, with
  canonical links, for the papers and systems the dossiers rest on.
- `MASTER-COMPENDIUM.md` — the distilled state of the art: how LLMs run, and how runners
  make them fast, lean, and truthful. Living document — first full draft banked
  2026-11-15; v2 revisions in flight as of 2026-11-15.

### `runners/` — one dossier per runner (24)

Clean-room dossiers (OR-2): architecture, scheduling, KV design, memory management,
quantization, kernels, session/prefix handling — in our own words, licence recorded,
an ideas-to-steal section in each.

- `runners/aphrodite.md` — Aphrodite Engine (PygmalionAI): a datacentre engine re-aimed
  at roleplay; covers the Aphrodite era and its rename to Sonar.
- `runners/candle.md` — Candle: Hugging Face's Rust machine-learning framework
  (`candle-core`, `candle-nn`, `candle-transformers`), Rust throughout with optional
  Python bindings.
- `runners/exllamav2.md` — ExLlamaV2: the single-user speed specialist — Python
  orchestration over a PyTorch C++/CUDA extension.
- `runners/gpt4all.md` — GPT4All (Nomic AI): desktop application, embeddable inference
  library, and language bindings for running LLMs locally.
- `runners/ipex-llm.md` — Intel IPEX-LLM: Intel's LLM library for PyTorch, descended
  from BigDL via `bigdl-llm`.
- `runners/jan.md` — Jan (Jan Desktop, Menlo Research): a public-documentation behaviour
  dossier on the desktop app.
- `runners/koboldcpp.md` — KoboldCpp: a public-documentation behaviour dossier on the
  personal / character-chat runner.
- `runners/lemonade.md` — AMD Lemonade: AMD's local AI server — the `lemond` daemon and
  `lemonade` command, implemented in C++.
- `runners/llamacpp-ggml.md` — llama.cpp / ggml: the gravity well of local inference —
  the inference engine and its tensor library together.
- `runners/llamacpp-server-ecosystem.md` — the server frontends, proxies, routers, and
  packaged distributions that grew around `llama-server` and the ggml core — not the core
  itself.
- `runners/llamafile.md` — llamafile: Mozilla AI's single-executable distribution of
  llama.cpp.
- `runners/lm-studio.md` — LM Studio (Element Labs): a closed-source desktop application
  for running local LLMs.
- `runners/lmdeploy.md` — LMDeploy: a toolkit for compressing, deploying, and serving
  LLMs and vision-language models, with TurboMind and PyTorch backends.
- `runners/mistral-rs.md` — mistral.rs: a Rust inference engine whose Rust crate and
  Python package are both first-class SDKs over the same core.
- `runners/mlc-llm.md` — MLC-LLM and MLCEngine: the compile-anywhere pole of the MLC /
  Apache TVM line; its browser sibling WebLLM is covered inside the same dossier.
- `runners/mlx.md` — MLX + MLX-LM: Apple's unified-memory array framework and its LLM
  package — the unified-memory exemplar.
- `runners/ollama.md` — Ollama itself: the deep dossier at the centre of our work,
  written for the engineer of an improved Ollama fork.
- `runners/onnx-runtime-genai.md` — ONNX Runtime GenAI (ORT GenAI): Microsoft's
  generative-AI library — a C++ core with Python, C#, C/C++, Java, and Objective-C
  surfaces.
- `runners/openvino-genai.md` — OpenVINO GenAI (Intel): the generative-AI pipeline
  library built on top of the OpenVINO Runtime.
- `runners/powerinfer.md` — PowerInfer and PowerInfer-2: sparsity-aware hybrid inference.
- `runners/ramalama.md` — RamaLama: the model-as-container runner, written in Python.
- `runners/sglang.md` — SGLang: a fast inference framework for large language,
  vision-language, and diffusion models, with its SRT runtime.
- `runners/tensorrt-llm.md` — TensorRT-LLM (NVIDIA): the vendor-native, compile-first
  pole of serving.
- `runners/vllm.md` — vLLM: the serving engine whose name glosses as "virtual LLM" —
  Python engine, scheduler, and API server over C++ / CUDA / Triton kernels.

### `papers/` — one dossier per research paper (36)

Paper dossiers (OR-3): full citation, the core idea in our own words, the paper's measured
claims **as reported** (with their hardware context), and applicability notes for
Ollama-on-a-6 GB-GPU and for Project Aesir.

- `papers/awq.md` — AWQ: activation-aware weight quantization for LLM compression and
  acceleration.
- `papers/cacheblend.md` — CacheBlend: fast LLM serving for RAG with cached knowledge
  fusion, reusing precomputed KV for chunks in any position.
- `papers/deepseek-v2-mla.md` — DeepSeek-V2: a strong, economical, efficient
  mixture-of-experts model, and its Multi-head Latent Attention (MLA).
- `papers/distserve.md` — DistServe: disaggregating prefill and decoding for
  goodput-optimized LLM serving.
- `papers/eagle-3.md` — EAGLE-3: scaling up inference acceleration via training-time test.
- `papers/eagle.md` — EAGLE: speculative sampling by predicting the target's next
  feature rather than its next token.
- `papers/flashattention.md` — FlashAttention: fast, memory-efficient exact attention
  with IO-awareness.
- `papers/flashattention-2.md` — FlashAttention-2: faster attention with better
  parallelism and work partitioning.
- `papers/flashattention-3.md` — FlashAttention-3: fast, accurate attention with
  asynchrony and low precision.
- `papers/flashinfer.md` — FlashInfer: an efficient, customizable attention engine for
  LLM inference serving.
- `papers/gptq.md` — GPTQ: accurate post-training quantization for generative
  pre-trained transformers.
- `papers/gqa.md` — GQA: training generalized multi-query transformer models from
  multi-head checkpoints (grouped-query attention).
- `papers/h2o.md` — H2O: the Heavy-Hitter Oracle for efficient generative inference —
  KV eviction by accumulated attention.
- `papers/kivi.md` — KIVI: a tuning-free asymmetric 2-bit quantization for the KV cache.
- `papers/kvquant.md` — KVQuant: KV cache quantization towards 10 million context length
  inference.
- `papers/longrope.md` — LongRoPE: extending the LLM context window beyond 2 million
  tokens.
- `papers/lookahead-decoding.md` — Lookahead Decoding: breaking the sequential dependency
  of LLM inference with Jacobi-style lookahead, no draft model.
- `papers/mamba.md` — Mamba: linear-time sequence modeling with selective state spaces.
- `papers/mamba-2.md` — Mamba-2: "Transformers are SSMs" — generalized models and
  efficient algorithms through structured state space duality.
- `papers/medusa.md` — Medusa: a simple inference-acceleration framework with multiple
  decoding heads on the target model itself.
- `papers/mixtral.md` — Mixtral of Experts: the Mixtral 8×7B sparse mixture-of-experts
  language model.
- `papers/moe-infinity.md` — MoE-Infinity: efficient MoE inference on personal machines
  with a sparsity-aware expert cache.
- `papers/online-speculative-decoding.md` — Online Speculative Decoding: adapting the
  draft model to live query traffic.
- `papers/orca.md` — Orca: a distributed serving system for transformer-based generative
  models — iteration-level scheduling and selective batching.
- `papers/pagedattention-vllm.md` — PagedAttention: efficient memory management for LLM
  serving, managing the KV cache as OS-style paged memory (the vLLM paper).
- `papers/prompt-cache.md` — Prompt Cache: modular attention reuse for low-latency
  inference, from reusable prompt segments with precomputed attention states.
- `papers/pyramidkv.md` — PyramidKV: dynamic KV cache compression based on pyramidal
  information funneling.
- `papers/quip-sharp.md` — QuIP#: even better LLM quantization with Hadamard incoherence
  and lattice codebooks.
- `papers/radixattention-sglang.md` — the SGLang paper: efficient execution of structured
  language model programs, with RadixAttention's radix-tree KV reuse.
- `papers/sarathi-serve.md` — Sarathi-Serve: taming the throughput–latency tradeoff in
  LLM inference with chunked prefill and stall-free batching.
- `papers/smoothquant.md` — SmoothQuant: accurate and efficient post-training
  quantization for LLMs by smoothing activation outliers.
- `papers/snapkv.md` — SnapKV: the LLM knows what you are looking for before generation —
  prompt-selected KV compression.
- `papers/speculative-decoding.md` — the founding pair, treated as one family:
  speculative decoding and speculative sampling, introduced independently in 2023.
- `papers/splitwise.md` — Splitwise: efficient generative LLM inference using phase
  splitting of prefill and decode.
- `papers/streamingllm.md` — StreamingLLM: efficient streaming language models with
  attention sinks.
- `papers/yarn.md` — YaRN: efficient context window extension of large language models.

### `memory/` — the memory corpus (13)

The memory corpus (OR-6): memory as a science, from KV caches to DRAM to allocators,
each dossier carrying applicability notes for Ollama, for Project Aesir, and for our own
hardware.

- `memory/00-MEMORY-FIELD-MAP.md` — OR-6 memory field map: the topic tree for memory
  researched as a science in its own right (Version 1, 2026-11-15).
- `memory/MEMORY-COMPENDIUM.md` — the OR-6 crown volume: the distilled state of the art
  for memory for AI systems, for computers, and for the allocators between them. Living
  document — first full draft banked 2026-11-15; v2 revisions in flight as of 2026-11-15.
- `memory/agent-memory-architectures.md` — agent memory architectures (dossier A5): what
  persists between sessions, how it is retrieved, and how it is corrected.
- `memory/allocator-lineages.md` — allocator lineages and designs: the discipline of
  allocation itself.
- `memory/gpu-memory-internals.md` — GPU memory internals: how VRAM is actually
  allocated, moved, and fragmented beneath a runner.
- `memory/kv-cache-design.md` — KV-cache design: a synthesis dossier on the design space
  of the cache itself, drawn from the corpus's own banked dossiers.
- `memory/memory-technologies-dram-cxl.md` — memory technologies: DRAM generations and
  CXL — the datasheet layer.
- `memory/memory-wall-and-roofline.md` — the memory wall and the roofline method: why
  decode is bandwidth-bound, and how to prove it.
- `memory/mimiralloc-our-own-proven-work.md` — MimirAlloc: a first-hand record of our own
  proven allocator work — our own project, read freely, no clean-room restriction.
- `memory/npu-memory-and-dataflows.md` — NPU memory and dataflow architectures: when
  SRAM, not DRAM, is the centre of the design.
- `memory/numa.md` — NUMA: non-uniform memory access, for engineers building LLM runners
  and allocators.
- `memory/unified-memory.md` — unified memory architectures: one pool, new physics — a
  synthesis dossier with a first-hand case study.
- `memory/virtual-memory-and-caches.md` — virtual memory, paging, and the cache / TLB
  hierarchy: the classical foundations.

### `aesir/` — the Project Aesir study (1)

Project Aesir study (OR-4). Aesir is ours, so it is read freely; it is written in Mojo
while Ollama is Go, so every idea is translated into Go/Ollama terms.

- `aesir/aesir-ideas-for-ollama.md` — Project Aesir ideas dossier for Ollama (OR-4):
  the first of the Aesir study files, dated 2026-11-15.

### `synthesis/` — synthesis (1)

- `synthesis/IDEA-LEDGER.md` — the ranked idea ledger handed to the Ollama build
  campaign: the cross-corpus ranking, its rejected/deferred list, and its open
  questions. **SECOND CUT — 2026-11-15.** Living document: later dossiers and the build
  campaign's own measurements will re-rank it.

## Discipline

- Every claim carries its source and a date; the field moves fast, and a 2023 claim and a
  2026 claim are different animals.
- Other projects are studied clean-room: behaviour and ideas only, never lifted code or
  text. Each project's licence is recorded in its dossier.
- Reported numbers are always labelled with the hardware and conditions they were
  measured under. Our own measurements are labelled as ours.
- Speculation is marked as speculation.

## How this corpus is maintained

- Dossiers bank individually, as each one is finished and verified.
- The bibliography merges per wave, gathering the citations of the dossiers that landed
  in that wave.
- The compendia and the ledger are revised in dated cuts; each cut states its date and
  what it supersedes.
- Corrections are made in place, with a dated note at the point of correction — never
  silently.

*Started 2026-11-15. Status as of 2026-11-15: corpus banked — 79 files: field maps,
24 runner dossiers, 36 paper dossiers, the 13-file memory corpus, the Aesir study,
both compendia in first full draft, and the idea ledger at its second cut.*
