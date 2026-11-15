# OM-2 record — the Anchor Layer core (2026-11-15)

## Battery v3 verdict (CLEAN harness: think:false = production parity, probe num_predict 120)

| scenario | stock | layer v1 |
|---|---|---|
| control (fits window) | S 5/5, H 4/4, wrong 0 | S 5/5, H 4/4, wrong 0 |
| overflow (1024, resend) | S 5/5, **H 0/4 correct, 4 WRONG** | S 5/5, **H 0/4 correct, 4 WRONG** |

- The anchor law holds on the resend path (S-facts 5/5 through overflow, both builds —
  stock's own fitting also preserves the system block there; the continuous-path
  n_keep=4 shift remains the anchor-killer the layer's num_keep raise addresses).
- **The open wound is H-facts: early-history facts are silently dropped by BOTH
  builds and the model confabulates replacements for all of them (4/4 wrong).**
  That is the accuracy failure OM-4 (summary band) + OM-5 (fact ledger) must kill.
- Earlier v1/v2 battery empties were a thinking-truncation artifact — see
  battery-correction-2026-11-15.md. v3 supersedes them.

## Built
- Forge layer v1: purplelongship `~/ollama-memory-forge/layer/omf_layer.py` (sha256 801f479a…), stdlib-only Python HTTP service. Dev seat: 127.0.0.1:11500 → upstream stock Ollama scratch on 127.0.0.1:11499 (production service untouched).
- Assembly: [pinned anchor = all system content] → [history with whole turns shed from the front-middle under a token budget] → [final user turn] → [post-history identity core = first 280 chars of the anchor, as a trailing system message]. Sets num_keep ≥ anchor tokens + 16. Session reconciliation keeps a canonical copy per session (extension adopt / rewind reset / divergence adopt). Token estimator: chars/3.5 + 6/msg (conservative). Streaming requests: assembled then relayed. All non-chat paths proxy untouched. Health: /omf/health.
- Core placement is switchable (OMF_CORE=post|front|off) for A/B.

## First battery (battery-layer-v1.json, sampled probes)
- control **3/6** (= stock control 3/6 — no in-window regression)
- overflow **2/6** (stock 1/6) — name and ship now survive overflow; sister/food/wreck/teacher still empty.
- BUT the passing probe SET churns between runs in both stock and layer control (stock: ship/food/teacher; layer: ship/sister/wreck) — at temperature 1.0 + presence_penalty 1.5 on a 4.6B Q2_K, individual probes flip on sampling luck, and empty answers occur even in-window. v1's numbers are therefore indicative, not decisive.

## Battery correction (applied immediately, per never-leave-a-flaw rule)
Probes now run at **temperature 0** (drive turns keep model sampling) — the battery measures memory, not luck; identical for stock and forged. Re-runs: battery-stock-t0.json and battery-layer-v1-t0.json (results appended when they land).

## Still open in OM-2/OM-3
- If deterministic probes still show overflow < control, the suspects in order: (a) trailing-system core rendering in this model's template; try OMF_CORE=front; (b) estimator over-shedding; (c) probe-context interference from filler tail. A/B before any redesign.
- Streaming chat through real clients (Voxta) untested — OM-6 deployment territory.
- Frontedit paired-session metric — OM-3.
