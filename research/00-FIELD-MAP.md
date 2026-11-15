# OR-1 — Field Map: Model Runners, Inference Engines, Serving Systems

*Version 1, 2026-11-15. Living document — the sweep keeps adding finds. "Essence" lines are
one-breath summaries in our own words. Licence/language/backend facts are as stated in each
project's own repository/docs as of the date noted; every entry is re-verified when its
full dossier (OR-2) is written. Status key: **mapped** = this line only; **dossier** = full
dossier banked (see `runners/`).*

## The centre of our work

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| Ollama | MIT | Go (runner layer over ggml/llama.cpp lineage; a native Go engine for some models arrived in 2025) | CUDA, ROCm, Vulkan, Metal, CPU | The friendliest local runner: one binary, a model library, an API — the patient our own campaign operates on | mapped — deep dossier first priority |
| Project Aesir (ours) | ours | Mojo, bare metal, no libraries | CUDA, HIP/ROCm, Hailo NPU, CPU | Volmarr's own from-scratch universal runner; studied freely in `aesir/`, ideas translated to Go terms | mapped — see OR-4 |

## The ggml / llama.cpp constellation

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| llama.cpp / ggml | MIT | C/C++ | CPU, CUDA, ROCm, Vulkan, Metal, SYCL | The gravity well of local inference: GGUF format, hand-tuned kernels, runs everywhere | mapped |
| KoboldCpp | AGPL-3.0 | C++/Python (llama.cpp fork) | CUDA, Vulkan, CPU | Storyteller-focused llama.cpp fork with a full creative-writing UI stack | mapped |
| GPT4All | MIT | C++/Qt (llama.cpp-based) | CPU-first, Vulkan | Nomic's desktop local-chat app; proved CPU local chat for non-technical users | mapped |
| LocalAI | MIT | Go | llama.cpp family + others | OpenAI-compatible local API server, multi-backend, Go — a close cousin to study for Ollama-in-Go design | mapped |
| Jan | AGPL-3.0 (verify at dossier) | TypeScript/Rust | llama.cpp-based | Desktop chat app with local models | mapped |
| LM Studio | Proprietary (closed) | — | llama.cpp-derived (llml) + MLX | Polished closed desktop runner; public docs/behaviour only | mapped |

## The datacentre serving engines

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| vLLM | Apache-2.0 | Python + C++/CUDA kernels | CUDA, ROCm, TPU, others | PagedAttention's home; the throughput king that redefined serving economics | mapped |
| SGLang | Apache-2.0 | Python + kernels | CUDA, ROCm | RadixAttention prefix-tree serving; programs-as-prompts; extremely strong on shared-prefix workloads | mapped |
| TensorRT-LLM | Apache-2.0 | C++/Python | NVIDIA CUDA only | NVIDIA's own compiled-graph serving; peak NVIDIA performance at peak complexity | mapped |
| FasterTransformer | Apache-2.0 | C++/CUDA | NVIDIA | TRT-LLM's ancestor; historically important kernel/scheduling ideas | mapped |
| LMDeploy | Apache-2.0 | Python/C++ | CUDA | SenseTime/InternLM serving; TurboMind engine, persistent batch + blocked KV | mapped |
| Aphrodite Engine | AGPL-3.0 | Python (vLLM lineage fork) | CUDA, ROCm | Community vLLM fork aimed at roleplay/consumer use — licence differs sharply from vLLM's; note it | mapped |
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
| MLC-LLM | Apache-2.0 | Python/C++ on Apache TVM | CUDA, Vulkan, Metal, WebGPU | Compile the model to the device: universal deployment via TVM | mapped |
| WebLLM | Apache-2.0 | TypeScript on MLC | WebGPU | In-browser LLM inference; proof of the compile-anywhere thesis | mapped |
| ONNX Runtime GenAI | MIT | C++ | CUDA, DirectML, CPU | Microsoft's ONNX-native generative runtime | mapped |
| OpenVINO GenAI | Apache-2.0 | C++ | Intel CPU/GPU/NPU | Intel's stack; the NPU-serving reference point | mapped |
| ExecuTorch | BSD-style (verify) | C++ | mobile/edge | PyTorch's on-device runtime; edge deployment discipline | mapped |

## The Rust / Apple / specialist family

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| mistral.rs | MIT | Rust | CUDA, Metal, CPU | Fast Rust runner with broad quant support and paged attention | mapped |
| Candle | Apache-2.0 / MIT | Rust | CUDA, Metal, CPU | Hugging Face's minimalist Rust framework underneath several runners | mapped |
| MLX + MLX-LM | MIT | C++/Python | Apple Silicon (unified memory) | Apple's array framework; the unified-memory design exemplar — directly relevant to our Z13 unified-memory work | mapped |
| ExLlamaV2 | MIT | Python + CUDA kernels | NVIDIA CUDA | GPTQ/EXL2 specialist; extremely fast single-user NVIDIA inference | mapped |
| PowerInfer | MIT (verify) | C++ | CPU+GPU hybrid | Exploits activation sparsity: hot neurons on GPU, cold on CPU — a memory-hierarchy idea worth its dossier | mapped |
| FlashInfer | Apache-2.0 | C++/CUDA kernels | NVIDIA (+AMD work) | A kernel library, not a runner — the attention-kernel substrate others build on | mapped |

## The minimal / educational lineage

| Runner | Licence | Language | Backends | Essence | Status |
|---|---|---|---|---|---|
| llama2.c | MIT | C (one file) | CPU | Karpathy's 700-line inference; the clearest possible statement of what a runner minimally is | mapped |
| llm.c | MIT | C/CUDA | CPU, CUDA | Karpathy's training twin; read for kernel-education value, not serving design | mapped |

## Sweep notes

- The map is deliberately wider than "things like Ollama": serving economics, kernel
  libraries, and compiler stacks all hold ideas our Go runner can steal.
- Known gaps the sweep continues into: vendor NPU stacks (Qualcomm Genie, MediaTek
  NeuroPilot), llama.cpp server front-ends (e.g. RamaLama — verify), AMD's Lemonade
  SDK server, Intel's IPEX-LLM (Apache-2.0, BigDL lineage), and any 2026 newcomers.
- Licence discipline matters commercially and legally: AGPL entries (KoboldCpp,
  Aphrodite, Jan) are studied for behaviour/ideas only — nothing of theirs is ever
  carried into code.

*Next: dossiers in priority order — Ollama (deep), llama.cpp/ggml, vLLM, SGLang,
MLX (unified memory), PowerInfer (memory hierarchy), ExLlamaV2, mistral.rs.*
