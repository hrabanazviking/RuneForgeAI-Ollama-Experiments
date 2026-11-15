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

## Memory science & allocation

*(populated as OR-6 dossiers land — memory wall, roofline, allocator literature first)*

## Our own work (first-class sources)

- MimirAlloc campaigns — Pi (117/117) and Z13 (117/117): repos + campaign records,
  mined in `memory/` dossiers with their gate numbers.
- Project Aesir campaign records — mined in `aesir/`.
- Z13 unified-memory campaign records — mined in `memory/` (B7).
- Ollama Memory Forge OM-0 recon — the build campaign's baseline measurements,
  cited by the synthesis ledger where used.
