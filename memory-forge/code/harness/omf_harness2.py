#!/usr/bin/env python3
"""OMF battery v2: S-facts (system) vs H-facts (early history), 2 phrasings
per fact, temp-0 probes, correct/empty/wrong scoring.
Usage: omf_harness2.py <base_url> <label> [scenario ...]
Scenarios: control (ctx 8192), overflow (ctx 1024, stateless resend).
"""
import json, sys, time, urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:11499"
LABEL = sys.argv[2] if len(sys.argv) > 2 else "stock"
SCEN = sys.argv[3:] or ["control", "overflow"]
MODEL = "gemma4viking4b:latest"

SYSTEM = ("You are Sigrid, a Norse shipwright and storyteller from Bergen. Your ship is named Wave Serpent. "
          "You fear deep water ever since the wreck of the Ember Gull in 2019. Your sister Astrid lives in Bergen "
          "and keeps three goats. Your favourite food is dried cod with butter. "
          "Your teacher was old Hallvard the Quiet. Answer as Sigrid, briefly.")
SETUP = [
    {"role": "user", "content": "Before we talk, remember these things about me: my brother is named Tomas and he sails to Greenland. My dog is called Bran. My mother lives in the village of Skagen. I promised to bring you a whalebone knife next spring."},
    {"role": "assistant", "content": "I will remember them all: Tomas your brother who sails to Greenland, Bran your dog, your mother in Skagen, and the whalebone knife you promised."},
]
FILLER = ("Tell me more about the harbour work today and the weather over the fjord and what the other shipwrights "
          "are saying about the spring tides and the price of good oak and tar and rope, and whether the fishermen "
          "brought in cod or herring, and what news came from the south on the last knarr, and how the children "
          "are learning their letters, and whether the well froze again last night by the boathouse steps. ")

# (group, fact, [phrasings], [accepted keywords])
FACTS = [
    ("S", "ship", ["What is your ship named?", "Tell me the name of your ship."], ["wave serpent"]),
    ("S", "sister", ["Who is your sister and what animals does she keep?", "Tell me about your sister."], ["astrid"]),
    ("S", "food", ["What food do you favour most?", "What do you most like to eat?"], ["cod"]),
    ("S", "wreck", ["What happened in 2019 that you still fear?", "Why do you fear deep water?"], ["ember gull", "wreck"]),
    ("S", "teacher", ["Who was your teacher?", "Who taught you your craft?"], ["hallvard"]),
    ("H", "brother", ["What is my brother named and where does he sail?", "Tell me about my brother."], ["tomas"]),
    ("H", "dog", ["What is my dog called?", "Tell me my dog's name."], ["bran"]),
    ("H", "mother", ["Where does my mother live?", "Which village is my mother in?"], ["skagen"]),
    ("H", "promise", ["What did I promise to bring you?", "What gift did I promise you?"], ["whalebone knife", "knife"]),
]

def post(path, payload, timeout=900):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def chat(msgs, opts=None):
    o = {"num_predict": 60, "num_gpu": 0}
    if opts: o.update(opts)
    t0 = time.time()
    r = post("/api/chat", {"model": MODEL, "messages": msgs, "stream": False, "think": False, "options": o})
    r["_wall_s"] = round(time.time() - t0, 2)
    return r

def run_probes(msgs, opts):
    popts = dict(opts); popts["temperature"] = 0; popts["num_predict"] = 120
    out = []
    for group, fact, phrasings, keys in FACTS:
        verdicts = []
        for q in phrasings:
            m2 = msgs + [{"role": "user", "content": "Answer in one short sentence: " + q}]
            r = chat(m2, popts)
            text = r["message"]["content"].strip()
            low = text.lower()
            if not text:
                verdicts.append("empty")
            elif any(k in low for k in keys):
                verdicts.append("correct")
            else:
                verdicts.append("wrong")
        best = "correct" if "correct" in verdicts else ("wrong" if "wrong" in verdicts else "empty")
        out.append({"group": group, "fact": fact, "verdict": best, "per_phrasing": verdicts})
    return out

def score(probes):
    s = {}
    for g in ("S", "H"):
        sub = [p for p in probes if p["group"] == g]
        s[g] = {"correct": sum(1 for p in sub if p["verdict"] == "correct"),
                "wrong": sum(1 for p in sub if p["verdict"] == "wrong"),
                "empty": sum(1 for p in sub if p["verdict"] == "empty"),
                "of": len(sub)}
    return s

def drive(opts, turns):
    msgs = [{"role": "system", "content": SYSTEM}] + [dict(m) for m in SETUP]
    log = []
    for t in range(1, turns + 1):
        msgs.append({"role": "user", "content": FILLER + "(day %d)" % t})
        r = chat(msgs, opts)
        log.append({"turn": t, "prompt_eval_count": r.get("prompt_eval_count"), "wall_s": r["_wall_s"]})
        msgs.append({"role": "assistant", "content": r["message"]["content"]})
    return msgs, log

results = {"label": LABEL, "base": BASE, "model": MODEL, "scenarios": {}}
if "control" in SCEN:
    msgs, log = drive({}, 8)
    pr = run_probes(msgs, {})
    results["scenarios"]["control"] = {"turns": log, "probes": pr, "score": score(pr)}
    print("control:", json.dumps(results["scenarios"]["control"]["score"]))
if "overflow" in SCEN:
    opts = {"num_ctx": 1024}
    msgs, log = drive(opts, 12)
    pr = run_probes(msgs, opts)
    results["scenarios"]["overflow"] = {"turns": log, "probes": pr, "score": score(pr)}
    print("overflow:", json.dumps(results["scenarios"]["overflow"]["score"]))

out_path = "/home/volmarr/ollama-memory-forge/harness/battery2-%s.json" % LABEL
with open(out_path, "w") as f:
    json.dump(results, f, indent=1)
print("WROTE", out_path)
