# Battery correction — the thinking-truncation artifact (2026-11-15 ~02:10 EST)

## What was wrong

The bench model (gemma4viking4b, a gemma-4 Q2_K) is a THINKING model. Every chat
response carries a hidden `thinking` field. With the battery's num_predict=60, the
model spent the entire generation budget on hidden reasoning and returned EMPTY
content with done_reason="length" — in stock AND layer configurations alike
(proven by a four-way A/B on a single short request, raw JSON inspected).

- think:false → clean answer in 18 eval tokens, done_reason=stop.
- thinking on, num_predict=300 → same answer after 228 eval tokens (813 chars of
  hidden thinking). **Hidden thinking costs ~12× the generation tokens on simple
  recall answers** — itself a campaign-relevant speed finding; Volmarr's production
  drop-in already sets OLLAMA_NO_THINK=true, and the scratch instance lacked it.

## What this invalidates

- Battery v1/v2 "empty" verdicts in DRIVEN scenarios (incl. stock overflow 0/9 and
  layer overflow S 1/5) are CONTAMINATED: empties there are explained by thinking
  truncation (longer, messier context → longer thinking → never reaches content),
  and cannot be cited as memory-loss proof. Those runs are superseded by battery v3
  (harness sends think:false, matching the production configuration; probe
  num_predict raised to 120).

## What still stands (independent of the artifact)

- The runner's context-shift behavior: n_keep=4 default discards from the front on
  the continuous path (runner logs, recon §3.4) — a log fact, not a probe inference.
- The single-shot fit test at num_predict=120 (thinking completed, content WAS
  produced): at num_ctx=1024 the model confabulated replacements for lost early
  history facts (brother "Bjorn", dog "Fjord") while system facts survived; at 4096
  all facts were correct. Genuine memory-loss + hallucination evidence.
- Prefix-cache counters (cached n_tokens), the frontedit re-evaluation counts, the
  clean ~1,010 tok/s prompt-eval baseline, and the unreachable-production-service
  finding (Tailscale logged out; service bound to the ghost tailnet address).

## Rule adopted

Every battery number from here on states its thinking configuration; probes run
think:false (production parity) unless a run is explicitly labelled thinking-on.
