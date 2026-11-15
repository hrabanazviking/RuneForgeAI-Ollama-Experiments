#!/usr/bin/env python3
"""OM-3 re-instrumentation — duration-based paired prefix-reuse metric.

Why: omf_paired.py (v1) showed prompt_eval_count does NOT discriminate
prefix reuse on this build (stock warm == noedit == 632). This harness
captures prompt_eval_duration (server-side, ns) for every leg and repeats
each measurement, reporting medians. If the runner reuses the cached
prefix, a no-edit resend evaluates only the new tail (~121 tok) and its
prompt_eval_duration must fall far below the warm leg's; a one-word front
edit on stock must stay near warm (near-full re-eval); on the layer the
same edit is quarantined to the tail band, so its duration must stay at
the tail-only level. An exact-resend leg gives the pure cache floor.

Legs (per base URL), REPS repetitions, medians reported:
  warm      H+Uw                       (full eval expected)
  resend    H+Uw again, byte-identical (cache floor)
  noedit    H+Unext                    (tail-only if reuse works)
  frontedit H'+Unext (1-word system edit, same size)
  dynfront  3 turns, fresh timestamp line in system each turn
  dyntail   3 turns, timestamp in the final user turn instead

Usage: omf_paired2.py <base_url> <label> [reps]
Results -> paired2-<label>.json beside this script.
"""
import json, statistics, sys, time, urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:11499"
LABEL = sys.argv[2] if len(sys.argv) > 2 else "stock"
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 3
MODEL = "gemma4viking4b:latest"
SESSION = "om3-paired2-" + LABEL + "-" + str(int(time.time()))

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
            "prompt_eval_ms": round((r.get("prompt_eval_duration") or 0) / 1e6, 1),
            "total_ms": round((r.get("total_duration") or 0) / 1e6, 1),
            "eval_count": r.get("eval_count"),
            "wall_s": round(time.time() - t0, 2)}

def med(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return statistics.median(vals) if vals else None

def paired(session):
    H = [{"role": "system", "content": SYSTEM}] + history(3)
    H2 = [{"role": "system", "content": SYSTEM.replace("Bergen", "Bergen town", 1)}] + history(3)
    warm_msgs = H + [{"role": "user", "content": FILLER + "(warm)"}]
    next_msgs = H + [{"role": "user", "content": FILLER + "(next)"}]
    edit_msgs = H2 + [{"role": "user", "content": FILLER + "(next)"}]
    legs = {"warm": [], "resend": [], "noedit": [], "frontedit": []}
    for rep in range(REPS):
        legs["warm"].append(chat(warm_msgs, session))
        legs["resend"].append(chat(warm_msgs, session))
        legs["noedit"].append(chat(next_msgs, session))
        chat(warm_msgs, session)  # re-warm unedited prefix before the edit leg
        legs["frontedit"].append(chat(edit_msgs, session))
        print("rep", rep + 1, {k: (v[-1]["prompt_eval_ms"], v[-1]["prompt_eval_count"]) for k, v in legs.items()}, flush=True)
    summary = {}
    for k, rows in legs.items():
        summary[k] = {"prompt_eval_ms_median": med(rows, "prompt_eval_ms"),
                      "prompt_eval_count_median": med(rows, "prompt_eval_count"),
                      "rows": rows}
    return summary

def dyn(session, tail):
    out = []
    hist = history(2)
    for t in range(1, 4):
        stamp = "Current local time is 06:2%d. The tide is turning." % t
        if tail:
            msgs = [{"role": "system", "content": SYSTEM}] + hist + \
                   [{"role": "user", "content": stamp + " " + FILLER + "(dyn %d)" % t}]
        else:
            msgs = [{"role": "system", "content": SYSTEM + " " + stamp}] + hist + \
                   [{"role": "user", "content": FILLER + "(dyn %d)" % t}]
        r = chat(msgs, session)
        out.append({"turn": t, "prompt_eval_ms": r["prompt_eval_ms"],
                    "prompt_eval_count": r["prompt_eval_count"], "wall_s": r["wall_s"]})
        hist = hist + [{"role": "user", "content": FILLER + "(dyn %d)" % t},
                       {"role": "assistant", "content": FIXED_REPLY}]
    return out

use_session = "layer" in LABEL
results = {"label": LABEL, "base": BASE, "model": MODEL, "session": use_session,
           "session_id": SESSION if use_session else None, "reps": REPS,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
results["paired"] = paired(use_session)
print("paired medians:", json.dumps({k: v["prompt_eval_ms_median"] for k, v in results["paired"].items()}))
results["dynfront"] = dyn(use_session, tail=False)
print("dynfront:", json.dumps(results["dynfront"]))
results["dyntail"] = dyn(use_session, tail=True)
print("dyntail:", json.dumps(results["dyntail"]))

out_path = "/home/volmarr/ollama-memory-forge/harness/paired2-%s.json" % LABEL
with open(out_path, "w") as f:
    json.dump(results, f, indent=1)
print("WROTE", out_path)
