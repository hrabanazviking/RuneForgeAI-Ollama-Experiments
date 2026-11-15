# OR-1 — Field Map: Model Runners, Inference Engines, Serving Systems

*Version 2, 2026-11-15 (v1 same day; updated by the OR-1 sweep update — see the sweep log
at the end). Living document — the sweep keeps adding finds. "Essence" lines are
one-breath summaries in our own words. Licence/language/backend facts are as stated in each
project's own repository/docs as of the date noted; every entry is re-verified when its
full dossier (OR-2) is written. Status key: **mapped** = this line only; **dossier** = full
dossier banked (see `runners/`).*

*Entry count, stated honestly: **40 enumerated entries** as of this version. Version 1
enumerated **34** (recounted row by row for this update); campaign reporting that spoke of
38 was wrong — the MASTER-COMPENDIUM's count of 34 for v1 was the correct one. This update
adds 6 verified entries (see sweep log), moving the true count 34 → 40.*

## The centre of our work

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| Ollama | MIT | Go (runner layer over ggml/llama.cpp lineage; a native Go engine for some models arrived in 2025) | CUDA, ROCm, Vulkan, Metal, CPU | The friendliest local runner: one binary, a model library, an API — the patient our own campaign operates on | dossier |
| Project Aesir (ours) | ours | Mojo, bare metal, no libraries | CUDA, HIP/ROCm, Hailo NPU, CPU | Volmarr's own from-scratch universal runner; studied freely in `aesir/`, ideas translated to Go terms | mapped — see OR-4 |

## The ggml / llama.cpp constellation

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| llama.cpp / ggml | MIT | C/C++ | CPU, CUDA, ROCm, Vulkan, Metal, SYCL | The gravity well of local inference: GGUF format, hand-tuned kernels, runs everywhere | dossier |
| KoboldCpp | AGPL-3.0 | C++/Python (llama.cpp fork) | CUDA, Vulkan, CPU | Storyteller-focused llama.cpp fork with a full creative-writing UI stack | dossier |
| GPT4All | MIT | C++/Qt (llama.cpp-based) | CPU-first, Vulkan | Nomic's desktop local-chat app; proved CPU local chat for non-technical users | mapped |
| LocalAI | MIT | Go | llama.cpp family + others | OpenAI-compatible local API server, multi-backend, Go — a close cousin to study for Ollama-in-Go design | mapped |
| Jan | Apache-2.0 (current, verified 2026-11-15); AGPL-3.0 historically (earlier era — exact relicensing point not verified; see dossier) | TypeScript/Rust (Tauri shell) | llama.cpp-based (+ experimental MLX engine) | Desktop chat app with local models; the AGPL era is historical — do not cite Jan as AGPL today | dossier |
| LM Studio | Proprietary (closed) | — | llama.cpp-derived (llml) + MLX | Polished closed desktop runner; public docs/behaviour only | mapped |
| RamaLama | MIT | Python | OCI containers (Podman/Docker) wrapping llama.cpp / vLLM images — CUDA, ROCm, Vulkan, Intel GPU, MLX (macOS), CPU | Red Hat / containers project: models treated as container images; pulls an accelerator-matched image and runs it isolated (rootless, no network by default) | mapped (added 2026-11-15) |
| llamafile | Apache-2.0 (its changes to llama.cpp remain MIT, as upstream) | C/C++ (Cosmopolitan Libc) | CPU across OS/arch from one file; llama.cpp GPU paths | Mozilla.ai: model weights + a llama.cpp runtime packaged as a single executable that runs anywhere — distribution as the feature | mapped (added 2026-11-15) |

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
| Hugging Face TGI | Apache-2.0 | Rust + Python | CUDA, ROCm | HF's production server; now in maintenance — its flash-attention integration lessons remain | mapped |
| FastChat | Apache-2.0 | Python | multi | The Vicuna-era serving controller; multi-model routing lineage | mapped |
| NVIDIA Triton Inference Server | BSD-3-Clause | C++ | multi-backend | General inference serving chassis (not LLM-specific); ensemble/scheduling ideas | mapped |
| Ray Serve (LLM) | Apache-2.0 | Python | multi | Cluster-scale serving orchestration layer | mapped |
| Xinference | Apache-2.0 | Python | multi | Model-serving platform with broad model-type coverage | mapped |

## The compiler / portable-runtime family

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| MLC-LLM | Apache-2.0 | Python/C++ on Apache TVM | CUDA, Vulkan, Metal, WebGPU | Compile the model to the device: universal deployment via TVM | dossier |
| WebLLM | Apache-2.0 | TypeScript on MLC | WebGPU | In-browser LLM inference; proof of the compile-anywhere thesis. Covered inside the MLC dossier (`runners/mlc-llm.md`) — no separate WebLLM dossier | dossier (within mlc-llm) |
| ONNX Runtime GenAI | MIT | C++ | CUDA, DirectML, CPU | Microsoft's ONNX-native generative runtime | dossier |
| OpenVINO GenAI | Apache-2.0 | C++ | Intel CPU/GPU/NPU | Intel's stack; the NPU-serving reference point | dossier |
| ExecuTorch | BSD-style (verify) | C++ | mobile/edge | PyTorch's on-device runtime; edge deployment discipline | mapped |

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
| Intel IPEX-LLM | Apache-2.0 | Python (PyTorch library) | Intel CPU, iGPU, Arc dGPU, NPU | BigDL-lineage PyTorch library for low-bit local LLM inference/fine-tuning on Intel XPU; integrates with llama.cpp, Ollama, vLLM | mapped (added 2026-11-15) |
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
- Still named gaps: Genie/NeuroPilot behaviour beyond the public documentation
  (SDK-gated); the ExecuTorch licence line still carries "(verify)"; any 2026
  newcomers the sweep has not yet reached.
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
    **mapped**. PowerInfer's "(verify)" dropped: MIT verified per its dossier.
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
