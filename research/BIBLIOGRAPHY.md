# Bibliography — living

*Started 2026-11-15. Every paper dossier in `papers/` adds its full citation here.
Claims in dossiers are only as good as these sources; links are to the canonical
record (arXiv / venue / publisher).*

## Runner & serving systems

- Kwon, W., Li, Z., Zhuang, S., Sheng, Y., Zheng, L., Yu, C. H., Gonzalez, J. E., Zhang, H., & Stoica, I. (2023). *Efficient Memory Management for Large Language Model Serving with PagedAttention.* SOSP '23, 611–626. arXiv:2309.06180. https://arxiv.org/abs/2309.06180 — KV cache managed as OS-style paged memory (fixed blocks + block tables + copy-on-write sharing) removes fragmentation waste and lifts serving throughput 2–4×. Dossier: `papers/pagedattention-vllm.md`.
- Yu, G.-I., Jeong, J. S., Kim, G.-W., Kim, S., & Chun, B.-G. (2022). *Orca: A Distributed Serving System for Transformer-Based Generative Models.* OSDI '22, 521–538. https://www.usenix.org/conference/osdi22/presentation/yu — iteration-level scheduling (continuous batching) plus selective batching. (No arXiv version.) Dossier: `papers/orca.md`.
- Zheng, L., Yin, L., Xie, Z., Sun, C., Huang, J., Yu, C. H., Cao, S., Kozyrakis, C., Stoica, I., Gonzalez, J. E., Barrett, C., & Sheng, Y. (2024). *SGLang: Efficient Execution of Structured Language Model Programs.* NeurIPS 37. arXiv:2312.07104. https://arxiv.org/abs/2312.07104 — RadixAttention keeps finished requests' KV in an LRU radix tree keyed by tokens, so shared prefixes are reused automatically, with cache-aware scheduling on top. Dossier: `papers/radixattention-sglang.md`.

## KV cache, attention, decoding

- Gim, I., Chen, G., Lee, S.-s., Sarda, N., Khandelwal, A., & Zhong, L. (2024). *Prompt Cache: Modular Attention Reuse for Low-Latency Inference.* MLSys 2024. arXiv:2311.04934. https://arxiv.org/abs/2311.04934 — reusable prompt segments declared as modules with precomputed attention states, spliced into new prompts to cut TTFT; largest gains on CPU. Dossier: `papers/prompt-cache.md`.
- Yao, J., Li, H., Liu, Y., Ray, S., Cheng, Y., Zhang, Q., Du, K., Lu, S., & Jiang, J. (2025). *CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion.* EuroSys '25. DOI: 10.1145/3689031.3696098. arXiv:2405.16444. https://arxiv.org/abs/2405.16444 — reuses precomputed KV for chunks in any position and repairs cross-attention by recomputing only the highest-deviation ~15% of tokens. Dossier: `papers/cacheblend.md`.
- Xiao, G., Tian, Y., Chen, B., Han, S., & Lewis, M. (2024). *Efficient Streaming Language Models with Attention Sinks.* ICLR 2024. arXiv:2309.17453. https://arxiv.org/abs/2309.17453 — permanently pinning ~4 initial tokens' KV (attention sinks) plus a sliding window gives constant-memory, stable streaming. Directly supports our character-anchor law. Dossier: `papers/streamingllm.md`.
- Zhang, Z., Sheng, Y., Zhou, T., Chen, T., Zheng, L., Cai, R., Song, Z., Tian, Y., Ré, C., Barrett, C., Wang, Z., & Chen, B. (2023). *H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models.* NeurIPS 36, 34661–34710. arXiv:2306.14048. https://arxiv.org/abs/2306.14048 — a fixed KV budget split between heavy-hitter tokens (by accumulated attention) and recent tokens preserves quality at ~20% of the full cache. Dossier: `papers/h2o.md`.

### Speculative decoding (wave 2)

- Leviathan, Y., Kalman, M., & Matias, Y. (2023). *Fast Inference from Transformers via Speculative Decoding.* ICML 2023, PMLR 202, 19274–19286. arXiv:2211.17192. https://arxiv.org/abs/2211.17192 — a small model drafts γ tokens; the target verifies them in one pass under modified rejection sampling that provably preserves the target distribution (2–3×, T5-XXL, TPU-v4). Dossier: `papers/speculative-decoding.md`.
- Chen, C., Borgeaud, S., Irving, G., Lespiau, J.-B., Sifre, L., & Jumper, J. (2023). *Accelerating Large Language Model Decoding with Speculative Sampling.* arXiv:2302.01318. https://arxiv.org/abs/2302.01318 — the independent DeepMind arrival at the same algorithm, scaled to Chinchilla 70B with a purpose-shaped 4B draft (2–2.5×). Dossier: `papers/speculative-decoding.md`.
- Cai, T., Li, Y., Geng, Z., Peng, H., Lee, J. D., Chen, D., & Dao, T. (2024). *Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads.* ICML 2024. arXiv:2401.10774. https://arxiv.org/abs/2401.10774 — extra decoding heads on the target's own hidden state + tree attention; no separate draft model (2.2–2.8×, Vicuna-7B). Dossier: `papers/medusa.md`.
- Li, Y., Wei, F., Zhang, C., & Zhang, H. (2024). *EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty.* ICML 2024. arXiv:2401.15077. https://arxiv.org/abs/2401.15077 — draft at the feature level with a shifted token input; lossless 2.7–3.5× on LLaMA2-Chat 70B. Dossier: `papers/eagle.md`.
- Li, Y., Wei, F., Zhang, C., & Zhang, H. (2025). *EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test.* NeurIPS 2025. arXiv:2503.01840. https://arxiv.org/abs/2503.01840 — direct token prediction + multi-layer feature fusion + training-time test; up to 6.5×. Dossier: `papers/eagle-3.md`.
- Fu, Y., Bailis, P., Stoica, I., & Zhang, H. (2024). *Break the Sequential Dependency of LLM Inference Using Lookahead Decoding.* ICML 2024. arXiv:2402.02057. https://arxiv.org/abs/2402.02057 — Jacobi-iteration n-grams verified in the same pass; no draft model or training (1.8× MT-Bench, A100; heavy extra FLOPs). Dossier: `papers/lookahead-decoding.md`.
- Liu, X., Hu, L., Bailis, P., Cheung, A., Deng, Z., Stoica, I., & Zhang, H. (2024). *Online Speculative Decoding.* ICML 2024, PMLR 235, 31131–31146. arXiv:2310.07177. https://arxiv.org/abs/2310.07177 — the draft model retrains continually on live traffic from rejection points; acceptance +0.1–0.65, latency ÷1.42–2.17 (final ICML figures). Dossier: `papers/online-speculative-decoding.md`.

## Memory science & allocation

- Wulf, W. A., & McKee, S. A. (1995). *Hitting the Memory Wall: Implications of the Obvious.* ACM SIGARCH Computer Architecture News 23(1). — DRAM latency improving ~7%/yr against CPU ~80%/yr: the wall as the founding observation of memory-centric design. Dossier: `memory/memory-wall-and-roofline.md`.
- McKee, S. A. (2004). *Reflections on the Memory Wall.* — the wall revisited a decade on. Dossier: `memory/memory-wall-and-roofline.md`.
- Williams, S., Waterman, A., & Patterson, D. (2009). *Roofline: An Insightful Visual Performance Model for Multicore Architectures.* Communications of the ACM 52(4). — attainable performance = min(peak compute, bandwidth × arithmetic intensity); the working method for judging whether a kernel is memory-bound. Dossier: `memory/memory-wall-and-roofline.md`.
- McCalpin, J. D. STREAM benchmark + machine-balance literature — sustained bandwidth (not peak) as the honest denominator; latency ≠ bandwidth. Dossier: `memory/memory-wall-and-roofline.md`.
- Yuan, Z., et al. (2024). *LLM Inference Unveiled: Survey and Roofline Model Insights.* arXiv:2402.16363. — GEMM-vs-GEMV arithmetic intensity for LLM inference; batching raises intensity toward the compute roof. Dossier: `memory/memory-wall-and-roofline.md`.
- MimirAlloc campaigns (ours, 2026). Pi campaign final gate 4,590 run / 0 failed; Z13 campaign final gate 4,988 passed / 0 failed / 77 skipped; both 117/117 slices. Records: campaign goal folders + keeper logs, mined in `memory/mimiralloc-our-own-proven-work.md`.

## Our own work (first-class sources)

- MimirAlloc campaigns — Pi (117/117) and Z13 (117/117): repos + campaign records,
  mined in `memory/` dossiers with their gate numbers.
- Project Aesir campaign records — mined in `aesir/`.
- Z13 unified-memory campaign records — mined in `memory/` (B7).
- Ollama Memory Forge OM-0 recon — the build campaign's baseline measurements,
  cited by the synthesis ledger where used.
