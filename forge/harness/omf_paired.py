#!/usr/bin/env python3
"""OM-3 paired prefix-reuse metric (Ollama Memory Forge).

Fixes the OM-1 frontedit confound (turn growth mixed into the edit cost) with
PAIRED sends: identical assembled size, identical tail turn, the ONLY
difference is a one-word edit near the front vs no edit. History is synthetic
and byte-identical across legs (fixed assistant replies), so any difference
in prompt_eval_count is the edit's fault, not sampling or growth.

Legs (each against a base URL):
  noedit    warm H+Uw, then measure H+Unext          -> tail-only eval expected
  frontedit warm H+Uw, then measure H'+Unext (1-word system edit)
                                                     -> near-full re-eval on stock
  dynfront  3 turns, system gains a fresh timestamp line every turn (Voxta
            pattern: dynamic content near the front) -> eval per turn
  dyntail   same 3 turns, timestamp carried in the final user turn instead
                                                     -> tail-only eval expected

Run against stock (scratch :11499) and against the layer (:11501/:11500).
The layer legs send a fixed omf_session so the layer can pin the anchor.
Usage: omf_paired.py <base_url> <label>
Results -> paired-<label>.json beside this script.
"""
import json, sys, time, urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:11499"
LABEL = sys.argv[2] if len(sys.argv) > 2 else "stock"
MODEL = "gemma4viking4b:latest"
SESSION = "om3-paired-" + LABEL

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
FIXED_REPLY = "The harbour is busy and the wind is fair; the shipwrights argue about oak prices as always."

def history(turns):
    h = [dict(m) for m in SETUP]
    for t in range(1, turns + 1):
        h.append({"role": "user", "content": FILLER + "(day %d)" % t})
        h.append({"role": "assistant", "content": FIXED_REPLY})
    return h

def post(path, payload, timeout=900):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def chat(msgs, session=False):
    payload = {"model": MODEL, "messages": msgs, "stream": False, "think": False,
               "options": {"num_predict": 16, "num_gpu": 0, "temperature": 0}}
    if session:
        payload["omf_session"] = SESSION
    t0 = time.time()
    r = post("/api/chat", payload)
    return {"prompt_eval_count": r.get("prompt_eval_count"),
            "eval_count": r.get("eval_count"),
            "wall_s": round(time.time() - t0, 2)}

def paired(session):
    """Warm with H, measure no-edit vs one-word front edit at equal size."""
    H = [{"role": "system", "content": SYSTEM}] + history(3)
    warm = chat(H + [{"role": "user", "content": FILLER + "(warm)"}], session)
    noedit = chat(H + [{"role": "user", "content": FILLER + "(next)"}], session)
    # re-warm the unedited prefix (the noedit send left the slot holding H+next)
    warm2 = chat(H + [{"role": "user", "content": FILLER + "(warm)"}], session)
    H2 = [{"role": "system", "content": SYSTEM.replace("Bergen", "Bergen town", 1)}] + history(3)
    frontedit = chat(H2 + [{"role": "user", "content": FILLER + "(next)"}], session)
    return {"warm_eval": warm["prompt_eval_count"],
            "noedit_eval": noedit["prompt_eval_count"],
            "rewarm_eval": warm2["prompt_eval_count"],
            "frontedit_eval": frontedit["prompt_eval_count"]}

def dyn(session, tail):
    """3 turns of Voxta-pattern dynamic injection; eval per turn."""
    out = []
    hist = history(2)
    for t in range(1, 4):
        stamp = "Current local time is 05:5%d. The tide is turning." % t
        if tail:
            msgs = [{"role": "system", "content": SYSTEM}] + hist + \
                   [{"role": "user", "content": stamp + " " + FILLER + "(dyn %d)" % t}]
        else:
            msgs = [{"role": "system", "content": SYSTEM + " " + stamp}] + hist + \
                   [{"role": "user", "content": FILLER + "(dyn %d)" % t}]
        r = chat(msgs, session)
        out.append({"turn": t, "prompt_eval_count": r["prompt_eval_count"], "wall_s": r["wall_s"]})
        hist = hist + [{"role": "user", "content": FILLER + "(dyn %d)" % t},
                       {"role": "assistant", "content": FIXED_REPLY}]
    return out

use_session = "layer" in LABEL
results = {"label": LABEL, "base": BASE, "model": MODEL, "session": use_session}
results["paired"] = paired(use_session)
print("paired:", json.dumps(results["paired"]))
results["dynfront"] = dyn(use_session, tail=False)
print("dynfront:", json.dumps(results["dynfront"]))
results["dyntail"] = dyn(use_session, tail=True)
print("dyntail:", json.dumps(results["dyntail"]))

out_path = "/home/volmarr/ollama-memory-forge/harness/paired-%s.json" % LABEL
with open(out_path, "w") as f:
    json.dump(results, f, indent=1)
print("WROTE", out_path)
