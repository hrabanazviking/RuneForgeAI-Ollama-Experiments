# OR-2 Deep Dossier: Ollama

> Research Forge campaign — commissioned by Volmarr, 2026-11-15.
> Written for a future expert reader who will engineer an improved Ollama fork.
> Clean-room note: this dossier describes architecture, behaviour and ideas in our own words. No source text or code is reproduced beyond short factual labels (parameter names, endpoint paths, version numbers). Ollama's own licence is recorded in §1.

## 1. Header

- **Name:** Ollama
- **Licence:** MIT License, copyright held by Ollama (the company). The licence file is unchanged in substance from the first release through the versions examined for this dossier. The engines underneath carry their own MIT licences: llama.cpp / GGML (copyright the ggml authors) and, where used, Apple's MLX (MIT). Model weights carry separate, per-model licences shipped beside the weights in the library; Ollama's licence does not govern the weights.
- **Language(s):** The control plane, CLI, HTTP server, scheduler and model management are written in Go. Inference itself is not Go tensor code in the current shipping design: GGUF models are executed by a bundled C/C++ program (upstream `llama-server`, built on llama.cpp / GGML); safetensors models on Apple Silicon are executed by an MLX runner. Earlier eras differed — see §2.3 for the full engine timeline, including a period (2025 to mid-2026) when a substantial set of models was implemented in Go directly over GGML.
- **Repository:** `github.com/ollama/ollama`
- **Site / docs:** `ollama.com`, model library at `ollama.com/library`, documentation at `docs.ollama.com`, blog at `ollama.com/blog`
- **First release:** v0.0.1, 2023-07-08. Repository created 2023-06-26, initially under the founder's personal account.
- **As of:** 2026-11-15. Version-sensitive claims are pinned to the tags they were read at. The deepest source-level readings available to this dossier are at v0.33.1 (truncation analysis, released 2026-08-26) and v0.34.4 / v0.35.0 (architecture and defaults history, September 2026). Documentation pages were re-read live on 2026-11-15; the context-length page carries an update stamp of 2026-11-12. Where docs and shipping code disagree, this dossier says so explicitly — with Ollama, that happens often enough to be a design lesson in itself.

**Essence.** Ollama is a local model manager and inference server modelled deliberately on the Docker workflow its founders knew from building Kitematic / Docker Desktop: a registry you `pull` from, a declarative packaging file (the Modelfile, analogous to a Dockerfile), content-addressed local storage, and one-command execution (`ollama run <model>`). A Go daemon listens on loopback port 11434, exposes both a native REST API and OpenAI- and Anthropic-compatible dialects, and delegates actual token generation to a per-model runner subprocess. Its optimisation target has never been datacentre throughput; it is time-to-first-token for a single user on a single, often memory-constrained, consumer machine, with zero configuration. Almost every strength and every weakness in this dossier follows from that choice.

---

## 2. Architecture

### 2.1 The two-process split: Go control plane, runner subprocess

The single most important architectural fact: **the Go server does not perform inference.** It is a control plane. Its jobs are:

1. HTTP routing and request translation (native API, OpenAI-compatible layer, Anthropic-compatible layer).
2. Model registry work: pulling, pushing, creating, copying, showing, listing and deleting models; resolving a model name/tag to a local blob.
3. Scheduling: deciding whether a requested model is already resident, whether it fits in memory, which device(s) it should occupy, and when an idle resident model must be evicted to make room.
4. Runner lifecycle: locating the correct runner binary for the detected accelerator, spawning it as a child process on a private loopback port, health-checking it until ready, proxying completions to it, and terminating it when its keep-alive expires.
5. Prompt preparation: rendering the chat template, applying message-level truncation (see §4.3), and forwarding the rendered prompt to the runner.

The runner subprocess does everything tensor-shaped: weight loading, KV-cache allocation, prompt evaluation, sampling and token generation, streaming results back over its private HTTP interface using server-sent events.

This subprocess boundary has oscillated over the project's life (in-process via cgo → subprocess → in-process as a library → subprocess → own engines → subprocess again; see §2.3), but the current design is firmly subprocess-based for GGUF models. The benefits are real and worth stealing: a crashing or hanging inference engine does not take down the management server; runner binaries can be built per-accelerator (CUDA, ROCm, Vulkan, Metal/CPU variants) and selected at runtime; the Go binary stays free of CGO fragility. The costs are also real: every request crosses an extra HTTP serialisation hop on loopback, runner startup is a process spawn plus a health-poll loop rather than a function call, and some llama-server capabilities (its own API key, its own TLS) are simply not passed through by the parent — the runner listens on loopback with neither, because the parent assumes loopback *is* the security boundary.

On Windows, spawned runners are attached to a Job Object so that terminating the parent cannot orphan GPU-holding children. That detail matters for any fork: runner leaks are VRAM leaks.

### 2.2 Server layout (conceptual)

From the public source structure, the responsibilities divide roughly as follows (described functionally, not as a file listing to copy):

- **Routing layer** — the HTTP route table. Native routes live under `/api/…`; OpenAI routes under `/v1/…` are, importantly, *the same native handlers behind a translating middleware* (see §7.3 — this implementation choice explains several compatibility gaps). Two guards sit in front of every route: a CORS/origin check and, while bound to loopback, an allowed-host check that rejects requests whose Host header is not local (a defence against DNS-rebinding-style browser tricks). Neither guard authenticates a user; there is no local API key system (see §7.5).
- **Scheduler** (`server/sched.go` in the public tree) — owns the set of resident runners, reference counts, the pending-request queue, eviction, and the reload decision when a request's options differ from the resident runner's options.
- **LLM-server abstraction** (`llm/` in the public tree) — a single interface behind which sit the concrete runner implementations: the upstream `llama-server` wrapper for GGUF models, the MLX client for safetensors models on Apple Silicon, and an image-generation path. The scheduler talks only to the interface and never knows which engine is behind it.
- **Discovery** — GPU/device enumeration: vendor, total memory, free memory. Its numbers feed both the context-tier decision (§4.1) and the layer-placement decision (§5.3).
- **Model store** — an OCI/Docker-style content-addressed blob store under the models directory (`~/.ollama/models` on macOS, `/usr/share/ollama/.ollama/models` for the Linux system install, `%USERPROFILE%\.ollama\models` on Windows; relocatable via `OLLAMA_MODELS`), with manifests mapping a human tag to weight blobs, template, parameters and licence layers.

### 2.3 Engine lineage: llama.cpp, the Go-native engine, MLX — and back

This is the section where stale secondary writing is most dangerous, because Ollama has had **three distinct engine eras**. A dossier frozen in any one era misdescribes the others.

**Era 1 — llama.cpp wrapper (July 2023 – late 2024).** Ollama began as, in its first README's own framing, a fast inference server in Go powered by llama.cpp. The integration mechanism flipped several times in the first year alone: compiled in via cgo bindings (v0.0.1), run as a separate server-example process (from v0.0.18, September 2023), linked back in-process as a library (January–April 2024), then returned to subprocess execution (from v0.1.32, April 2024). Throughout, the division of labour was stable: GGML is the tensor library; llama.cpp builds model graphs on GGML; Ollama wraps both with management and serving ergonomics.

**Era 2 — Ollama's own engine, in Go over GGML (late 2024 – May 2026).** The break began with Llama 3.2 Vision (v0.4.0, November 2024), which shipped on an Ollama-written runner, and became a stated strategy with Gemma 3 (v0.6.0, March 2025) and the public announcement of 2025-05-15, "Ollama's new engine for multimodal models." The reasoning given at the time, paraphrased: llama.cpp treated multimodal models as a separate text decoder plus a separate vision encoder glued together by model-specific orchestration code, and that glue was becoming the bottleneck for correctness as multimodal releases accelerated. By calling GGML directly from Go, each model could be a self-contained implementation owning its own projection layer and its own attention peculiarities (the announcement names Gemma 3's sliding-window attention and Llama 4's chunked attention and 2-D rotary embeddings as cases where a faithful per-model implementation mattered, and warns that an approximately-right attention implementation degrades output progressively over long contexts). During this era, newly onboarded model families ran on the Go engine while the long tail of older families continued on llama.cpp beside it. The September 2025 scheduling overhaul (§5.4) initially applied only to new-engine models.

**Era 3 — return to upstream llama-server for GGUF, MLX for Apple Silicon (June 2026 – present, as of this dossier).** On 2026-05-29 a change removing the vendored GGML backend, the CGO runner and the Go model implementations was merged, so that GGUF models are served exclusively by a pinned upstream `llama-server` subprocess (with a small Ollama-side compatibility/patch layer applied at build time); it shipped in v0.30.0 (tagged 2026-06-01) alongside Vulkan becoming enabled by default. Separately, MLX — Apple's array framework — arrived as a preview engine on Apple Silicon in v0.19.0 (March 2026) and became the default engine on Apple Silicon for the architectures it supports in the v0.40.0 line (September 2026), leaving, in the project's own commit language of that period, the MLX runner as effectively the only remaining Go-side inference runner.

**What this means for a fork, stated plainly:** as of 2026-11-15, "Ollama is a wrapper around llama.cpp" is *again* substantially true for GGUF models on Windows and Linux — but by a different mechanism than in 2023 (a pinned, separately built `llama-server` subprocess rather than linked code), and it is *not* true on Apple Silicon for MLX-supported models. Any claim in older tutorials that Ollama's Go engine is the future, or that Ollama merely shells out to llama.cpp, is era-bound. Verify against the tag you actually fork.

*Verification note:* the Era-3 transition is established by the merge record and release history as synthesised in the dated history source in §10, cross-checked against multiple independent October–November 2026 comparisons that agree on the v0.30 return and the MLX default. This dossier did not independently re-read the full v0.40 source tree file-by-file; treat fine-grained claims about which individual model families route to which engine at v0.40.x as **not fully verified** and check the routing code at your fork point.

### 2.4 Platforms and backends

Documented support as of late 2026: macOS, Windows and Linux, plus an official container image. Acceleration paths: NVIDIA via CUDA (documented floor: compute capability 5.0+ with recent drivers; the oldest generations need a newer driver branch), AMD via ROCm on Linux (and historically more constrained on Windows — the FAQ still carries a note that Windows/Radeon defaults to a single loaded model due to VRAM-reporting limits in an older ROCm), Intel and other GPUs via Vulkan (enabled by default since v0.30 where the backend is installed), Apple Silicon via Metal historically and MLX by default now for supported models, and CPU-only execution everywhere. Cross-platform reach is a genuine strength: the same Modelfile, the same API and the same model tag work across all of them, which is precisely the property our own cross-platform law demands.

### 2.5 The cloud appendage

Since August–September 2025 Ollama also operates hosted "cloud models": tags that a signed-in local instance proxies to Ollama's datacentres for models too large for the local machine, later priced per token (tiers announced August 2026). This is architecturally separable — the local server needs no account and no key — but not entirely inert by default: the local server fetches a recommended-models list and the cloud catalogue from ollama.com at startup and periodically thereafter (roughly every four hours), with requests signed by the installation's generated key pair. A documented local-only mode (`OLLAMA_NO_CLOUD=1`, or the equivalent server config flag) disables cloud models, web search and those fetches. A fork that values a quiet network posture should default this off, or at least make the fetches visible; stock Ollama does not surface them in the UI.

---

## 3. Scheduling & batching

### 3.1 The request path

A generation request arrives at the Go server, is translated if it came in on a compatibility route, and is handed to the scheduler. The scheduler resolves the model, then:

1. If a compatible runner for that model (with matching load-time options — see §3.4) is already resident, the request is attached to it.
2. If not, the scheduler must load: it checks whether the model can fit alongside current residents; if memory is insufficient, incoming requests **queue** while resident models are given the chance to go idle and be unloaded to make room. Queued requests are processed in arrival order.
3. Once a runner exists, the request occupies a **slot** (see §3.2) for the duration of prompt evaluation plus generation, streaming tokens back through the Go server to the client.

The queue is bounded by `OLLAMA_MAX_QUEUE`, default **512**; beyond it the server rejects new requests with HTTP 503. Note the precise semantics reported in the source-level history: the bounded queue principally holds requests *waiting for a model to load*; it is not a general admission-control system for generation work.

### 3.2 Slots, not continuous batching

Ollama's concurrency unit is the **slot**: room for one in-flight request, created when the runner starts. `OLLAMA_NUM_PARALLEL` sets slots per loaded model. Its history is itself instructive — concurrency arrived experimentally in v0.1.33 (April 2024) and by default in v0.2.0 (July 2024) with an auto-selected slot count; the auto count was lowered in April 2025; and since v0.10.0 (July 2025) the default is simply **1**, with the project stating the intent that parallelism thereafter be explicit rather than dynamically guessed.

The crucial implementation fact: **a slot costs a whole context window of KV cache.** The runner is started with a total context of `num_ctx × num_parallel`, partitioned among slots. The FAQ's own arithmetic: a 2K window with 4 parallel requests becomes an 8K allocation. Weights are loaded once; only the cache multiplies. This is slot-partitioned serving in the llama.cpp tradition — it is *not* continuous batching in the vLLM sense. There is no global paged block pool shared across requests, no iteration-level admission of new requests into a running batch, and no preemption-and-resume of a running sequence to free memory under pressure. Each slot independently prefills and decodes; total throughput therefore scales far less gracefully than a paged-attention server. Independent measurement on identical hardware and weights (RTX 3090 24 GB, 4-bit Gemma-family 12B, Ollama 0.34.4 vs a paged-attention server, September–October 2026 readings reported in §10) found single-request decode within roughly 10% between the two systems, but aggregate throughput at 16 concurrent requests roughly **3.6× higher** on the paged server. That is the honest shape of the trade: at concurrency 1, Ollama gives up almost nothing; at concurrency 16, it gives up a great deal.

Two slot exceptions are documented in source-level readings: embedding models are forced to a single slot, and a named set of (eleven, at v0.34.4) architecture families — including several vision/multimodal families — are likewise held to one slot regardless of configuration, with a warning logged.

### 3.3 Multi-model residency

The second concurrency axis is how many *different* models may be resident at once: `OLLAMA_MAX_LOADED_MODELS`, default **3 × the number of GPUs** (3 for CPU inference), provided each fits in available memory. On GPU inference, a new model must fit completely in VRAM to load concurrently alongside residents. Residency is reference-counted and keep-alive governed (§5.2); under memory pressure the scheduler's remedy is to wait for, then force, the unloading of idle residents — not to partially evict a busy one.

Multi-GPU placement follows a fit-first rule: if a model fits entirely on any single GPU it is placed there (avoiding interconnect traffic); only a model that fits on no single GPU is spread across all of them. A spread override exists for operators who prefer distribution. The September 2025 scheduling work (§5.4) specifically improved the mismatched-GPU case.

### 3.4 The reload trap: options are part of runner identity

A resident runner is keyed not just by model but by its load-time options, compared by deep equality. `num_ctx` is one of those options. Consequence: two clients alternating between different explicitly-set context sizes for the same model force an **unload–reload cycle on every alternation** — full weight re-read, full KV reallocation, seconds of latency, paid by everyone sharing the host. There is one narrow escape: if *both* the resident runner and the incoming request are using the automatic (unset) context, the request adopts the resident value instead of forcing a reload. The practical law for client authors, and a design smell for fork authors: on a shared Ollama host, either everybody pins the same `num_ctx`, or nobody pins one. A fork should treat context size as a runner *capacity* (allocate a maximum, serve smaller windows inside it) rather than as runner *identity* — see §9.

### 3.5 What Ollama does not schedule

No priorities, no fairness between clients, no per-client quotas, no deadlines, no preemption. The queue is FIFO. For its intended single-user setting this is defensible simplicity; for any shared deployment it is the first thing that must change.

---
