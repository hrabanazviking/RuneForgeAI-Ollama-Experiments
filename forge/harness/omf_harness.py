#!/usr/bin/env python3
"""OM-1 measurement harness + accuracy battery v1 (Ollama Memory Forge).

Runs canonical scenarios against an Ollama-compatible /api/chat endpoint and
records per-turn evaluated/reused tokens, latency, and keyword-scored fact
probes. Usage: omf_harness.py <base_url> <label> [scenario ...]
Scenarios: control, overflow, frontedit. Results -> battery-<label>.json
"""
import json, sys, time, urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:11499"
LABEL = sys.argv[2] if len(sys.argv) > 2 else "stock"
SCEN = sys.argv[3:] or ["control", "overflow", "frontedit"]
MODEL = "gemma4viking4b:latest"

SYSTEM = ("You are Sigrid, a Norse shipwright and storyteller from Bergen. Your ship is named Wave Serpent. "
          "You fear deep water ever since the wreck of the Ember Gull in 2019. Your sister Astrid lives in Bergen "
          "and keeps three goats. Your left hand has a scar from a chisel slip. You speak plainly and warmly, "
          "in short answers. Your favourite food is dried cod with butter. "
          "You are mending a torn sail for the spring voyage to Iceland. Your teacher was old Hallvard the Quiet. "
          "You keep a carved whalebone comb your mother gave you. You dislike loud drums. Answer as Sigrid.")
FILLER = ("Tell me more about the harbour work today and the weather over the fjord and what the other shipwrights "
          "are saying about the spring tides and the price of good oak and tar and rope, and whether the fishermen "
          "brought in cod or herring, and what news came from the south on the last knarr, and how the children "
          "are learning their letters, and whether the well froze again last night by the boathouse steps. ")
PROBES = [
    ("name", "What is your name and where are you from?", ["sigrid"]),
    ("ship", "What is your ship named?", ["wave serpent"]),
    ("sister", "Who is your sister and what animals does she keep?", ["astrid", "goat"]),
    ("food", "What food do you favour most?", ["cod"]),
    ("wreck", "What happened in 2019 that you still fear?", ["ember gull", "wreck"]),
    ("teacher", "Who was your teacher?", ["hallvard"]),
]

def post(path, payload, timeout=900):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def chat(msgs, opts=None):
    # num_gpu=0 pins the battery to CPU: deterministic on this shared laptop,
    # immune to other campaigns' VRAM churn (recon baselines were CPU too).
    o = {"num_predict": 50, "num_gpu": 0}
    if opts: o.update(opts)
    t0 = time.time()
    r = post("/api/chat", {"model": MODEL, "messages": msgs, "stream": False, "options": o})
    r["_wall_s"] = round(time.time() - t0, 2)
    return r

def run_probes(msgs, opts):
    # Probes are measurements: temperature 0 makes them deterministic, so the
    # battery measures memory handling, not sampling luck. Drive turns keep
    # the model's own sampling. Identical for stock and forged runs.
    popts = dict(opts); popts["temperature"] = 0
    out = []
    for key, q, keys in PROBES:
        m2 = msgs + [{"role": "user", "content": "Answer in one short sentence: " + q}]
        r = chat(m2, popts)
        text = r["message"]["content"].strip()
        low = text.lower()
        ok = bool(text) and any(k in low for k in keys)
        out.append({"probe": key, "ok": ok, "answer": text[:160],
                    "prompt_eval_count": r.get("prompt_eval_count")})
    return out

def drive(msgs, turns, opts, tag, log):
    for t in range(1, turns + 1):
        msgs.append({"role": "user", "content": FILLER + "(day %d)" % t})
        r = chat(msgs, opts)
        log.append({"scenario": tag, "turn": t,
                    "prompt_eval_count": r.get("prompt_eval_count"),
                    "eval_count": r.get("eval_count"), "wall_s": r["_wall_s"]})
        msgs.append({"role": "assistant", "content": r["message"]["content"]})
    return msgs

results = {"label": LABEL, "base": BASE, "model": MODEL, "scenarios": {}}

if "control" in SCEN:
    log = []
    msgs = drive([{"role": "system", "content": SYSTEM}], 8, {}, "control", log)
    pr = run_probes(msgs, {})
    results["scenarios"]["control"] = {"turns": log, "probes": pr,
        "score": "%d/%d" % (sum(1 for p in pr if p["ok"]), len(pr))}
    print("control done:", results["scenarios"]["control"]["score"])

if "overflow" in SCEN:
    log = []
    opts = {"num_ctx": 1024}
    msgs = drive([{"role": "system", "content": SYSTEM}], 12, opts, "overflow", log)
    pr = run_probes(msgs, opts)
    results["scenarios"]["overflow"] = {"turns": log, "probes": pr,
        "score": "%d/%d" % (sum(1 for p in pr if p["ok"]), len(pr))}
    print("overflow done:", results["scenarios"]["overflow"]["score"])

if "frontedit" in SCEN:
    log = []
    msgs = drive([{"role": "system", "content": SYSTEM}], 3, {}, "frontedit", log)
    before = log[-1]["prompt_eval_count"]
    msgs2 = [dict(m) for m in msgs]
    msgs2[0] = {"role": "system", "content": SYSTEM.replace("Bergen", "Bergen town")}
    msgs2.append({"role": "user", "content": FILLER})
    r = chat(msgs2, {})
    results["scenarios"]["frontedit"] = {"eval_before_edit": before,
        "eval_after_one_word_edit": r.get("prompt_eval_count")}
    print("frontedit done: before=%s after_edit=%s" % (before, r.get("prompt_eval_count")))

out_path = "/home/volmarr/ollama-memory-forge/harness/battery-%s.json" % LABEL
with open(out_path, "w") as f:
    json.dump(results, f, indent=1)
print("WROTE", out_path)
