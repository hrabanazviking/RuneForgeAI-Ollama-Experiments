#!/usr/bin/env python3
import json, time, urllib.request, sys
STOCK = "http://127.0.0.1:11499"
LAYER = "http://127.0.0.1:11500"
MODEL = "gemma4viking4b:latest"
FILLER = ("Tell me more about the harbour work today and the weather over the fjord and what the other shipwrights "
          "are saying about the spring tides and the price of good oak and tar and rope, and whether the fishermen "
          "brought in cod or herring, and what news came from the south on the last knarr, and how the children "
          "are learning their letters, and whether the well froze again last night by the boathouse steps. ")
SYSTEM = ("You are Sigrid, a Norse shipwright and storyteller from Bergen. Your ship is named Wave Serpent. "
          "Answer as Sigrid, briefly.")
def post(base, path, payload, timeout=900):
    req = urllib.request.Request(base + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)
def get(base, path):
    with urllib.request.urlopen(base + path, timeout=30) as r:
        return json.load(r)
def rates(r):
    pec, ped = r.get("prompt_eval_count", 0), r.get("prompt_eval_duration", 0)
    ec, ed = r.get("eval_count", 0), r.get("eval_duration", 0)
    return {"prompt_tok": pec, "prompt_tps": round(pec / (ped / 1e9), 1) if ped else None, "gen_tok": ec, "gen_tps": round(ec / (ed / 1e9), 2) if ed else None}
out = {}
for label, base in [("stock", STOCK), ("layer", LAYER)]:
    salt = f"OM8-{label}-{int(time.time())}"
    warm = salt + " warmup. " + FILLER * 8 + " Say: ready."
    meas = salt + " measure. " + FILLER * 11 + " Answer with one word: done."
    if base == STOCK:
        post(base, "/api/generate", {"model": MODEL, "prompt": warm, "stream": False, "think": False, "options": {"num_predict": 16, "num_gpu": 0}})
        r = post(base, "/api/generate", {"model": MODEL, "prompt": meas, "stream": False, "think": False, "options": {"num_predict": 32, "num_gpu": 0}})
    else:
        post(base, "/api/chat", {"model": MODEL, "stream": False, "think": False, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": warm}], "options": {"num_predict": 16, "num_gpu": 0}})
        r = post(base, "/api/chat", {"model": MODEL, "stream": False, "think": False, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": warm}, {"role": "assistant", "content": "Ready."}, {"role": "user", "content": meas}], "options": {"num_predict": 32, "num_gpu": 0}})
    out[f"longprompt_{label}"] = rates(r)
    print(label, "longprompt", out[f"longprompt_{label}"], flush=True)
for label, base in [("stock", STOCK), ("layer", LAYER)]:
    msgs = [{"role": "system", "content": SYSTEM}]
    turns = []
    for i in range(8):
        msgs.append({"role": "user", "content": f"Turn {i+1}: " + FILLER.strip()})
        t0 = time.time()
        r = post(base, "/api/chat", {"model": MODEL, "messages": msgs, "stream": False, "think": False, "options": {"num_predict": 24, "num_gpu": 0}})
        turns.append({"turn": i + 1, "wall_s": round(time.time() - t0, 2), **rates(r)})
        msgs.append({"role": "assistant", "content": r["message"]["content"]})
    out[f"multiturn_{label}"] = turns
    print(label, "multiturn turn1", turns[0]["wall_s"], "turn8", turns[-1]["wall_s"], flush=True)
stats0 = get(LAYER, "/omf/stats")
msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "Remember: my brother is named Tomas and he sails to Greenland. My dog is called Bran."}, {"role": "assistant", "content": "I will remember Tomas and Bran."}]
t0 = time.time()
for i in range(100):
    msgs.append({"role": "user", "content": f"Note {i+1}: the tide table for day {i+1} says high water at hour {i % 12 + 1} and the oak price is {30 + i} pennies."})
    r = post(LAYER, "/api/chat", {"model": MODEL, "messages": msgs, "stream": False, "think": False, "options": {"num_predict": 8, "num_gpu": 0, "num_ctx": 1024}})
    msgs.append({"role": "assistant", "content": r["message"]["content"]})
stats1 = get(LAYER, "/omf/stats")
out["footprint_100turn"] = {"wall_s": round(time.time() - t0, 1), "last_stats_after": stats1.get("last_stats", {})}
print("footprint done", out["footprint_100turn"]["wall_s"], flush=True)
with open(sys.argv[1], "w") as f:
    json.dump(out, f, indent=1)
print("WROTE", sys.argv[1])
