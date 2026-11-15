# OR-1 — Field Map: Model Runners, Inference Engines, Serving Systems

*Version 3, 2026-11-15 (v1 and v2 same day; updated by OR-1 field-map sweep #2 — see the
sweep log at the end). Living document — the sweep keeps adding finds. "Essence" lines are
one-breath summaries in our own words. Licence/language/backend facts are as stated in each
project's own repository/docs as of the date noted; every entry is re-verified when its
full dossier (OR-2) is written. Status key: **mapped** = this line only; **dossier** = full
dossier banked (see `runners/`).*

*Entry count, stated honestly: **47 enumerated entries** as of this version. Version 2
enumerated **40**. Sweep #2 adds 7 verified entries (see sweep log), moving the true
count 40 → 47. No existing entry was removed; three entries the sweep brief described as
missing (Hugging Face TGI, NVIDIA Triton Inference Server, Xinference) were in fact
already enumerated in v2 — sweep #2 verified and expanded them in place rather than
duplicating them.*

## The centre of our work

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| Ollama | MIT | Go (runner layer over ggml/llama.cpp lineage; a native Go engine for some models arrived in 2025) | CUDA, ROCm, Vulkan, Metal, CPU | The friendliest local runner: one binary, a model library, an API — the patient our own campaign operates on | dossier |
| Project Aesir (ours) | ours | Mojo, bare metal, no libraries | CUDA, HIP/ROCm, Hailo NPU, CPU | Volmarr's own from-scratch universal runner; studied freely in `aesir/`, ideas translated to Go terms | mapped — see OR-4 |

## The ggml / llama.cpp constellation

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| llama.cpp / ggml | MIT | C/C++ | CPU, CUDA, ROCm, Vulkan, Metal, SYCL | The gravity well of local inference: GGUF format, hand-tuned kernels, runs everywhere. Newer serving companion verified 2026-11-15: `llama-server` **router mode** (announced 2025-12-11, Hugging Face blog by the ggml-org team) — started with no model, it dynamically loads/unloads/switches multiple models, one process per model, Ollama-style model management inside llama.cpp itself | dossier |
| KoboldCpp | AGPL-3.0 | C++/Python (llama.cpp fork) | CUDA, Vulkan, CPU | Storyteller-focused llama.cpp fork with a full creative-writing UI stack | dossier |
| GPT4All | MIT | C++/Qt (llama.cpp-based) | CPU-first, Vulkan | Nomic's desktop local-chat app; proved CPU local chat for non-technical users. Currency-checked 2026-11-15: repository not archived, licence still MIT per its own repo — no verified change, entry otherwise untouched | mapped |
| LocalAI | MIT | Go | llama.cpp family + others | OpenAI-compatible local API server, multi-backend, Go — a close cousin to study for Ollama-in-Go design | mapped |
| Jan | Apache-2.0 (current, verified 2026-11-15); AGPL-3.0 historically (earlier era — exact relicensing point not verified; see dossier) | TypeScript/Rust (Tauri shell) | llama.cpp-based (+ experimental MLX engine) | Desktop chat app with local models; the AGPL era is historical — do not cite Jan as AGPL today. Currency-checked again in sweep #2 (2026-11-15): its own README still states "Apache 2.0", repository active and not archived — no verified change | dossier |
| LM Studio | Proprietary (closed) | — | llama.cpp-derived (llml) + MLX | Polished closed desktop runner; public docs/behaviour only | mapped |
| RamaLama | MIT | Python | OCI containers (Podman/Docker) wrapping llama.cpp / vLLM images — CUDA, ROCm, Vulkan, Intel GPU, MLX (macOS), CPU | Red Hat / containers project: models treated as container images; pulls an accelerator-matched image and runs it isolated (rootless, no network by default) | mapped (added 2026-11-15) |
| llamafile | Apache-2.0 (its changes to llama.cpp remain MIT, as upstream) | C/C++ (Cosmopolitan Libc) | CPU across OS/arch from one file; llama.cpp GPU paths | Mozilla.ai: model weights + a llama.cpp runtime packaged as a single executable that runs anywhere — distribution as the feature | mapped (added 2026-11-15) |
| llama-swap | MIT (verified 2026-11-15, project repo `mostlygeek/llama-swap`) | Go | Any OpenAI/Anthropic-compatible upstream server — llama.cpp and forks, vLLM, others (per project README) | The llama.cpp ecosystem's model-swap proxy: one binary + one config, hot-swaps local servers on demand behind one endpoint — the external companion that router mode (above) now partly absorbs upstream | mapped (added 2026-11-15, sweep #2) |

## The datacentre serving engines

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| vLLM | Apache-2.0 | Python + C++/CUDA kernels | CUDA, ROCm, TPU, others | PagedAttention's home; the throughput king that redefined serving economics | dossier |
| SGLang | Apache-2.0 | Python + kernels | CUDA, ROCm | RadixAttention prefix-tree serving; programs-as-prompts; extremely strong on shared-prefix workloads | dossier |
| TensorRT-LLM | Apache-2.0 | C++/Python | NVIDIA CUDA only | NVIDIA's own compiled-graph serving; peak NVIDIA performance at peak complexity | dossier |
| FasterTransformer | Apache-2.0 | C++/CUDA | NVIDIA | TRT-LLM's ancestor; historically important kernel/scheduling ideas | mapped |
| LMDeploy | Apache-2.0 | Python/C++ | CUDA | SenseTime/InternLM serving; TurboMind engine, persistent batch + blocked KV | dossier |
| Sonar (formerly Aphrodite Engine) | AGPL-3.0 | Python (vLLM lineage fork) | CUDA, ROCm | Community vLLM fork aimed at roleplay/consumer use — licence differs sharply from vLLM's; note it. Renamed Aphrodite Engine → **Sonar** on 2026-11-07/08; repository moved from PygmalionAI to the dphnAI organisation (same project, same AGPL-3.0) | dossier |
| LightLLM | Apache-2.0 | Python | CUDA | Lightweight token-wise serving design | mapped |
| DeepSpeed-FastGen / DeepSpeed-MII | Apache-2.0 | Python | CUDA | Microsoft's serving line; Dynamic SplitFuse scheduling idea | mapped |
| Hugging Face TGI (Text Generation Inference) | Apache-2.0 (verified 2026-11-15, project repo licence field) | Rust + Python + gRPC (as the project itself describes it) | CUDA, ROCm, plus Inferentia / Intel GPU / Gaudi / TPU variants listed in its own README | HF's production server, used at HF for Hugging Chat / Inference API / Inference Endpoints — **now in maintenance mode as of 2025-12-11** (HF's own TGI docs, dated): only minor bug-fix, documentation and lightweight-maintenance PRs accepted; its repo README says the downstream engines HF contributes to and recommends going forward are **vLLM and SGLang**, plus local engines llama.cpp / MLX, and HF's Inference Endpoints docs recommend vLLM or SGLang as alternatives; repository shown as **archived (public archive)** when checked 2026-11-15. Its flash-attention / transformers-architecture integration lessons remain, in a frozen codebase | mapped (expanded 2026-11-15, sweep #2) |
| FastChat | Apache-2.0 | Python | multi | The Vicuna-era serving controller; multi-model routing lineage | mapped |
| NVIDIA Triton Inference Server | BSD-3-Clause (verified 2026-11-15, project repo licence field — matches the v2 entry) | C++ | multi-backend (TensorRT, PyTorch, ONNX, OpenVINO, Python and more, per project README) | General inference serving chassis (not LLM-specific); ensemble/scheduling ideas. Currency-checked 2026-11-15: active, not archived; README names current release 2.74.0 / 26.10 container | mapped |
| Ray Serve (LLM) | Apache-2.0 | Python | multi | Cluster-scale serving orchestration layer | mapped |
| Xinference | Apache-2.0 (verified 2026-11-15, project repo licence field) | Python | vLLM, SGLang, TensorRT-LLM, Transformers, llama.cpp, MLX engines (per project README) — CPU, GPU, Apple Silicon, MLU vary by engine | Model-serving platform with broad model-type coverage (300+ built-in models across language/vision/embedding/rerank/image/audio/video per its README). Currency-checked 2026-11-15: active, not archived | mapped |
| GPUStack | Apache-2.0 (verified 2026-11-15, project repo licence field + README licence section) | Python | Orchestrates vLLM, SGLang, TensorRT-LLM or custom engines; NVIDIA, AMD, Ascend NPU, Hygon DCU, Moore Threads, Iluvatar, MetaX, Cambricon MLU, T-Head PPU (per project README) | Open-source GPU cluster manager for AI model serving: pools heterogeneous GPUs/machines under one control plane and configures the engine for you — the cluster-manager layer Ollama never tries to be | mapped (added 2026-11-15, sweep #2) |
| OpenLLM (BentoML) | Apache-2.0 (verified 2026-11-15, project repo licence field + README licence badge) | Python | vLLM as production backend, served via BentoML (per project README acknowledgements) | Run any open-source LLM as an OpenAI-compatible API with one command (`openllm serve …`), with built-in chat UI and BentoCloud/Docker/Kubernetes deployment path | mapped (added 2026-11-15, sweep #2) |
| NVIDIA Dynamo | Apache-2.0 (verified 2026-11-15, project LICENSE file: "The rest of this codebase is licensed under the Apache License 2.0" — a bundled DeepSeek test-data subset is MIT, noted in the same file; GitHub's sidebar summarises this mixed file as NOASSERTION) | Rust + Python ("Built in Rust for performance, Python for extensibility" — project README) | Orchestration above vLLM, SGLang, TensorRT-LLM; NVIDIA datacentre GPUs / multi-node | NVIDIA's 2025 datacentre-scale distributed inference framework (repo created 2025-03-03): disaggregated prefill/decode, KV-aware routing, multi-tier KV cache and SLA-driven scaling — an orchestration layer, not an engine replacement | mapped (added 2026-11-15, sweep #2) |
| llm-d | Apache-2.0 (verified 2026-11-15, project repo licence field + README licence section) | Go (core router components; `llm-d-router` is a Go module per its own repo) on Kubernetes | Above vLLM / SGLang model servers; multi-accelerator, multi-cloud (per project README) | Kubernetes-native distributed inference stack founded 2025 by Red Hat, Google Cloud, IBM Research, CoreWeave and NVIDIA (repo created 2025-04-29; CNCF Sandbox per project README): prefix-cache/load-aware routing, tiered KV offloading and prefill/decode disaggregation as a cluster layer | mapped (added 2026-11-15, sweep #2) |

## The compiler / portable-runtime family

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| MLC-LLM | Apache-2.0 | Python/C++ on Apache TVM | CUDA, Vulkan, Metal, WebGPU | Compile the model to the device: universal deployment via TVM. Currency-checked 2026-11-15: repository not archived, licence still Apache-2.0 per its own repo — no verified change, entry otherwise untouched | dossier |
| WebLLM | Apache-2.0 | TypeScript on MLC | WebGPU | In-browser LLM inference; proof of the compile-anywhere thesis. Covered inside the MLC dossier (`runners/mlc-llm.md`) — no separate WebLLM dossier | dossier (within mlc-llm) |
| ONNX Runtime GenAI | MIT | C++ | CUDA, DirectML, CPU | Microsoft's ONNX-native generative runtime | dossier |
| OpenVINO GenAI | Apache-2.0 | C++ | Intel CPU/GPU/NPU | Intel's stack; the NPU-serving reference point | dossier |
| ExecuTorch | **BSD-3-Clause** (verified 2026-11-15 — see note below) | C++ | mobile/edge | PyTorch's on-device runtime; edge deployment discipline | mapped |
| Modular MAX (MAX Serve) | Mixed, exactly as the project states it (verified 2026-11-15, `modular/modular` README, License section): Mojo is Apache License v2.0 with LLVM Exceptions; "Portions of the MAX source code and its binary distribution are licensed under the MAX_LICENSE, with the remainder of the source under the Apache License v2.0 with LLVM Exceptions" — **not** a single-licence project, do not cite it as plain Apache-2.0 | Mojo + Python | GPU via the MAX graph compiler / kernels (a compatible GPU is required for its generate path, per project README) | Modular's graph-compiled inference platform with an OpenAI-compatible inference server (`max/python/max/serve`, open-sourced May 2025 per project README): one Mojo kernel codebase serving models across vendors — directly relevant to our own Mojo work | mapped (added 2026-11-15, sweep #2) |
| NVIDIA TensorRT Edge-LLM | Apache-2.0 (verified 2026-11-15, project repo licence field + README licence section) | C++ | NVIDIA Jetson, DRIVE and DGX Spark (TensorRT/CUDA), per project README/docs | NVIDIA's 2025 edge runtime (repo created 2025-10-02): lightweight C++ LLM/VLM inference for embedded automotive/robotics — TensorRT-LLM's ideas rebuilt for Thor-class edge hardware, with EAGLE speculative decoding and NVFP4 | mapped (added 2026-11-15, sweep #2) |

*ExecuTorch licence note (sweep #2, verified 2026-11-15): the project's own README states
"ExecuTorch is BSD licensed. See LICENSE." The LICENSE file in `pytorch/executorch` is a
three-clause BSD licence (redistribution conditions 1–2 plus the clause 3 bar on using the
name Meta or contributor names for endorsement), headed "BSD License — For 'ExecuTorch'
software", with copyright holders Meta Platforms, Inc. and affiliates, Arm, Qualcomm
Innovation Center, Apple, MediaTek, NXP, Samsung Electronics and Intel. GitHub's repo
sidebar summarises the licence as "Other (NOASSERTION)" — that is GitHub failing to match
the multi-holder file to a single SPDX template, not a different licence. The verified
fact replacing the old "[verify]" is therefore: **BSD-3-Clause**.*

## The Rust / Apple / specialist family

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| mistral.rs | MIT | Rust | CUDA, Metal, CPU | Fast Rust runner with broad quant support and paged attention | dossier |
| Candle | Apache-2.0 / MIT | Rust | CUDA, Metal, CPU | Hugging Face's minimalist Rust framework underneath several runners | dossier |
| MLX + MLX-LM | MIT | C++/Python | Apple Silicon (unified memory) | Apple's array framework; the unified-memory design exemplar — directly relevant to our Z13 unified-memory work | dossier |
| ExLlamaV2 | MIT | Python + CUDA kernels | NVIDIA CUDA | GPTQ/EXL2 specialist; extremely fast single-user NVIDIA inference | dossier |
| PowerInfer | MIT (verified 2026-11-15, per dossier) | C++ | CPU+GPU hybrid | Exploits activation sparsity: hot neurons on GPU, cold on CPU — a memory-hierarchy idea worth its dossier | dossier |
| FlashInfer | Apache-2.0 | C++/CUDA kernels | NVIDIA (+AMD work) | **Infrastructure, not a runner** — a kernel library: the attention-kernel substrate others build on | dossier (papers/flashinfer.md) — infrastructure |

## The vendor stacks (NPU / platform runtimes)

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| AMD Lemonade | Apache-2.0 | C++ | llama.cpp backends (CPU, CUDA, Vulkan, ROCm, Metal), FastFlowLM on AMD XDNA2 NPU, ONNX Runtime GenAI | AMD-sponsored local AI server (project started 2025): OpenAI/Anthropic/Ollama-compatible APIs on one port; the Ryzen AI NPU+GPU serving reference | mapped (added 2026-11-15) |
| Intel IPEX-LLM | Apache-2.0 | Python (PyTorch library) | Intel CPU, iGPU, Arc dGPU, NPU | BigDL-lineage PyTorch library for low-bit local LLM inference/fine-tuning on Intel XPU; integrates with llama.cpp, Ollama, vLLM. **ARCHIVED — verified 2026-11-15:** its own README now opens "THIS PROJECT IS ARCHIVED — Intel will not provide or guarantee development of or support for this project, including but not limited to, maintenance, bug fixes, new releases or updates. Patches to this project are no longer accepted by Intel." and the repository is a public archive; its last README news item is 2025/05 and its last release noted there is 2.2.0 (2025/04). Treat as a frozen reference, not a living stack | mapped (added 2026-11-15; archived status added 2026-11-15, sweep #2) |
| Qualcomm Genie | Proprietary (ships inside Qualcomm's QAIRT / AI Engine Direct SDK under Qualcomm SDK terms; no open-source licence) | C/C++ | Snapdragon Hexagon HTP NPU, Adreno GPU, CPU (QNN backends) | Qualcomm's GenAI inference engine: dialog-style LLM runtime for Snapdragon, models prepared via Qualcomm AI Hub | mapped (added 2026-11-15; public facts only — SDK-gated) |
| MediaTek NeuroPilot | Proprietary (MediaTek SDK; public-fact level only) | C/C++ (Neuron Runtime API) + TFLite-based tooling | MediaTek APU/NPU (MDLA), GPU, CPU | MediaTek's AI SDK stack for Dimensity: compiles models to proprietary .dla binaries for the APU; the current LLM path runs through the LiteRT NeuroPilot Accelerator | mapped (added 2026-11-15; public facts only — SDK-gated) |

## The minimal / educational lineage

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| llama2.c | MIT | C (one file) | CPU | Karpathy's 700-line inference; the clearest possible statement of what a runner minimally is | mapped |
| llm.c | MIT | C/CUDA | CPU, CUDA | Karpathy's training twin; read for kernel-education value, not serving design | mapped |

## Sweep notes

- The map is deliberately wider than "things like Ollama": serving economics, kernel
  libraries, and compiler stacks all hold ideas our Go runner can steal.
- Gaps closed by the 2026-11-15 sweep update: Qualcomm Genie and MediaTek NeuroPilot
  (public-fact entries; both SDKs are licence-gated, so internals beyond public
  documentation stay out of reach), RamaLama, AMD Lemonade, Intel IPEX-LLM, and
  llamafile are now enumerated entries rather than named gaps.
- Gaps closed by sweep #2 (2026-11-15): the ExecuTorch licence "[verify]" is resolved
  (BSD-3-Clause, see the note in the compiler family); TGI's maintenance-mode status is
  recorded with HF's own date and recommendation; IPEX-LLM's archival is recorded;
  GPUStack, OpenLLM, NVIDIA Dynamo, llm-d, llama-swap, Modular MAX and TensorRT
  Edge-LLM are enumerated.
- Still named gaps: Genie/NeuroPilot behaviour beyond the public documentation
  (SDK-gated); any 2026 newcomers the sweep has not yet reached.
- Licence discipline matters commercially and legally: AGPL entries (KoboldCpp,
  Sonar/Aphrodite) are studied for behaviour/ideas only — nothing of theirs is ever
  carried into code. Jan is **no longer** on that list: its AGPL-3.0 era is historical
  and its current licence is Apache-2.0 (verified 2026-11-15, per `runners/jan.md`).

*Next: dossiers in priority order — GPT4All and LM Studio (in flight), then the
vendor stacks (Lemonade first — it is the Strix Halo NPU reference), LocalAI,
and the remaining mapped serving engines.*

## Sweep log

- **2026-11-15 — OR-1 sweep update (v1 → v2).**
  - **Rename:** Aphrodite Engine → **Sonar** (renamed 2026-11-07/08; PygmalionAI →
    dphnAI organisation; AGPL-3.0 unchanged). Source: banked dossier
    `runners/aphrodite.md`.
  - **Licence correction:** Jan — AGPL-3.0 is historical; current licence is
    **Apache-2.0** (verified 2026-11-15 against Jan's own documentation; the exact
    relicensing point could not be verified and the entry says so). Source: banked
    dossier `runners/jan.md`. Jan removed from the AGPL behaviour-only list above.
  - **Count repair:** v1 recounted row by row = **34** entries (the
    MASTER-COMPENDIUM's figure; campaign reporting of 38 was wrong). With the 6
    additions below, this version enumerates **40**.
  - **Status updates:** every banked dossier in `runners/` is now marked
    **dossier** (17 dossiers: ollama, llamacpp-ggml, vllm, sglang, mlx, powerinfer,
    exllamav2, mistral-rs, tensorrt-llm, mlc-llm, lmdeploy, koboldcpp,
    onnx-runtime-genai, openvino-genai, candle, aphrodite/sonar, jan). GPT4All and
    LM Studio dossiers were still in flight when the tree was read — both stay
    **mapped**. PowerInfer's "[verify]" dropped: MIT verified per its dossier.
    WebLLM's entry now records that it is covered inside the MLC dossier.
    FlashInfer is explicitly tagged **infrastructure** (kernel library, dossier at
    `papers/flashinfer.md`).
  - **Entries added (6), each verified 2026-11-15:**
    - *RamaLama* — MIT, Python, container-wrapped llama.cpp/vLLM. Source: project
      repository `containers/ramalama` on GitHub, opened 2026-11-15 (licence field,
      README hardware/runtime tables).
    - *llamafile* — Apache-2.0. Source: llamafile licence/openness fact review
      (reviewed 2026-10-01; Mozilla.ai organisation, single-executable design,
      llama.cpp changes MIT).
    - *AMD Lemonade* — Apache-2.0, C++. Source: project repository
      `lemonade-sdk/lemonade` on GitHub, opened 2026-11-15 (licence field, README
      supported-configurations table: llama.cpp backends, FastFlowLM NPU, ONNX
      Runtime GenAI).
    - *Intel IPEX-LLM* — Apache-2.0, Python/PyTorch, BigDL lineage. Source: GitHub
      API licence field for the ipex-llm repository (SPDX Apache-2.0) and Intel's
      Open Edge Platform IPEX-LLM documentation, both read 2026-11-15.
    - *Qualcomm Genie* — proprietary, inside the QAIRT / AI Engine Direct SDK.
      Sources: Qualcomm's own AI developer-workflow documentation (docs.qualcomm.com,
      "Qualcomm GenAI Inference Engine (Genie)") and Qualcomm support-forum answers
      describing the Genie SDK for LLM work, read 2026-11-15. Public facts only.
    - *MediaTek NeuroPilot* — proprietary SDK, public-fact level. Sources:
      MediaTek Dimensity Developer Center NeuroPilot documentation (Neuron SDK /
      Neuron Runtime API, .dla compiled binaries) and the Google Developers Blog
      post on the LiteRT NeuroPilot Accelerator (2025-12-08), read 2026-11-15.
  - **Already present, confirmed not gaps:** DeepSpeed-FastGen (datacentre table),
    llama2.c / llm.c (minimal lineage), FlashInfer (specialist table, now tagged
    infrastructure), WebLLM (compiler family, MLC-dossier coverage noted).

- **2026-11-15 — OR-1 field-map sweep #2 (v2 → v3, 40 → 47 entries).**
  All facts below were checked 2026-11-15 against each project's own repository,
  LICENSE file, README or official docs — never listicles alone.
  - **ExecuTorch licence — "[verify]" RESOLVED:** **BSD-3-Clause.** Sources:
    `pytorch/executorch` README ("ExecuTorch is BSD licensed. See LICENSE.") and its
    LICENSE file (three-clause BSD text, multi-holder copyright list), both opened
    2026-11-15. GitHub's sidebar "Other (NOASSERTION)" summary is explained in the
    entry note. No "[verify]" remains anywhere in this map.
  - **Hugging Face TGI — already enumerated in v2, expanded in place (not a new
    entry):** Apache-2.0, Rust + Python + gRPC, CUDA/ROCm + other hardware variants
    per its README. Status, dated from HF's own sources: HF's TGI documentation
    states "Text Generation Inference is in maintenance mode as of 12/11/2025" and
    that only minor bug-fix / documentation / lightweight-maintenance PRs will be
    accepted; the repo README's caution banner names vLLM and SGLang as the engines
    HF contributes to and recommends going forward, plus llama.cpp / MLX locally;
    HF's Inference Endpoints docs recommend vLLM or SGLang as alternatives; the
    GitHub repository was shown as a public archive when checked 2026-11-15.
  - **Entries added (7), each verified 2026-11-15 from its own repo:**
    - *GPUStack* (`gpustack/gpustack`) — Apache-2.0, Python, orchestrates
      vLLM/SGLang/TensorRT-LLM/custom engines across nine accelerator families.
    - *OpenLLM* (`bentoml/OpenLLM`) — Apache-2.0, Python, vLLM backend via BentoML.
    - *NVIDIA Dynamo* (`ai-dynamo/dynamo`, repo created 2025-03-03) — Apache-2.0
      per its LICENSE file (with an MIT-licensed bundled test-data subset noted in
      that file), Rust + Python, orchestration above vLLM/SGLang/TensorRT-LLM.
    - *llm-d* (`llm-d/llm-d`, repo created 2025-04-29) — Apache-2.0, Go core
      components on Kubernetes, above vLLM/SGLang; CNCF Sandbox per its README.
    - *llama-swap* (`mostlygeek/llama-swap`) — MIT, Go, model-swap proxy for
      llama.cpp/vLLM-class local servers.
    - *Modular MAX* (`modular/modular`) — mixed licence exactly as its README
      states it (MAX_LICENSE portions + Apache-2.0 with LLVM Exceptions remainder;
      Mojo Apache-2.0 with LLVM Exceptions), Mojo + Python, MAX Serve
      OpenAI-compatible server open-sourced May 2025 per its README.
    - *NVIDIA TensorRT Edge-LLM* (`NVIDIA/TensorRT-Edge-LLM`, repo created
      2025-10-02) — Apache-2.0, C++, Jetson/DRIVE/DGX Spark edge runtime.
  - **Already present, verified and expanded (not re-added):** *NVIDIA Triton
    Inference Server* — BSD-3-Clause confirmed against its repo licence field,
    active, README current release 2.74.0; *Xinference* — Apache-2.0 confirmed,
    active, engine list (vLLM/SGLang/TensorRT-LLM/Transformers/llama.cpp/MLX) taken
    from its README.
  - **llama.cpp serving companions checked:** `llama-server` **router mode** —
    verified from the ggml-org team's Hugging Face blog post "New in llama.cpp:
    Model Management", published 2025-12-11 (dynamic load/unload/switch, multi-process,
    no restart) and recorded inside the existing llama.cpp entry, not as a separate
    entry; *llama-swap* — added as its own entry (above).
  - **Existing entries amended (verified changes only):**
    - *Intel IPEX-LLM* — **archived**: README banner "THIS PROJECT IS ARCHIVED"
      (Intel: no development/support, patches no longer accepted) + public-archive
      repository status, checked 2026-11-15; last README news 2025/05.
    - *Hugging Face TGI* — maintenance-mode status + HF recommendation + archive
      status (above).
    - *ExecuTorch* — licence "[verify]" → BSD-3-Clause (above).
    - *llama.cpp* — router-mode companion note (above).
  - **Currency pass — checked, no verified change, left untouched:** *Jan*
    (README still states Apache 2.0; repo active, not archived), *GPT4All*
    (MIT per repo licence field; not archived), *MLC-LLM* (Apache-2.0 per repo
    licence field; not archived). *Sonar/Aphrodite* rename was already recorded
    in v2 and was not re-litigated.
  - **Candidates checked and REJECTED (one line each, with reason):**
    - *KServe* (`kserve/kserve`, Apache-2.0 verified) — rejected: a Kubernetes
      orchestration platform, not an inference engine/runner itself; it delegates
      to vLLM/llm-d-class runtimes already mapped — duplicate of the orchestration
      layer this sweep already covers with llm-d/Dynamo/Ray Serve.
    - *Cloudflare Infire* — rejected: a real Rust LLM engine (Cloudflare's own
      blog, 2025-08-27) but internal to Workers AI with no public repository or
      licence found in Cloudflare's own material — no public presence /
      unverifiable licence.
    - *ik_llama.cpp* (`ikawrakow/ik_llama.cpp`) — rejected: a llama.cpp fork
      (extra quant types/kernels; it also ships inside llama-swap's unified
      image) — duplicate-of-entry, the fork pattern already covered by
      llama.cpp/KoboldCpp.
    - *Mooncake / LMCache* — rejected: KV-cache transfer/storage infrastructure
      surfaced in newcomer searches, not a runner or serving system.
    - *KAITO, SIE and similar Kubernetes wrappers* — rejected for this sweep:
      surfaced only in third-party listicles; not verified from their own
      repositories, so no licence/status fact could be stated honestly.
