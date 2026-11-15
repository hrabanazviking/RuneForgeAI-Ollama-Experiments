#!/usr/bin/env python3
"""OMF forge layer v2 (OM-4 summary band + OM-5 fact ledger).

Extends v1 assembly: [anchor] -> [memory band: fact ledger + prose summary]
-> [recent turns verbatim] -> [final user turn] -> [post-history core].

Before any turn is shed it is distilled: subject-keyed facts are extracted
(later statements supersede earlier ones on the same subject; the superseded
line is kept, marked) and a compact prose summary is kept. Distilled band is
injected right after the anchor. Shedding happens in batches down to ~70%
of the token budget. If distillation fails for a turn, the raw turn is kept
rather than losing data. Raw shed turns stay in the session store.

Env: OMF_UPSTREAM, OMF_PORT, OMF_CORE, OMF_DEFAULT_CTX (as v1).
"""
import hashlib, json, math, os, re, sys, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = os.environ.get("OMF_UPSTREAM", "http://127.0.0.1:11499")
PORT = int(os.environ.get("OMF_PORT", "11500"))
CORE_MODE = os.environ.get("OMF_CORE", "post")
DEFAULT_CTX = int(os.environ.get("OMF_DEFAULT_CTX", "8192"))
CHARS_PER_TOKEN = 3.5
SESSIONS = {}

def est_tokens(text):
    return int(math.ceil(len(text) / CHARS_PER_TOKEN)) + 6

def msg_tokens(m):
    return est_tokens(m.get("content", ""))

def session_id(payload, anchor):
    sid = payload.get("omf_session")
    if sid:
        return str(sid)
    return hashlib.sha1((payload.get("model", "") + "|" + anchor).encode()).hexdigest()[:12]

# ---------- OM-5 fact extraction ----------
PATTERNS = [
    (r"my ([a-z][a-z ]{0,24}?) is named ([A-Z][a-zA-Z]+)",
     lambda m: (m.group(1).strip(), "My %s is named %s." % (m.group(1).strip(), m.group(2)), m.group(2).lower())),
    (r"my ([a-z][a-z ]{0,24}?) is called ([A-Z][a-zA-Z]+)",
     lambda m: (m.group(1).strip(), "My %s is called %s." % (m.group(1).strip(), m.group(2)), m.group(2).lower())),
    (r"my ([a-z][a-z ]{0,24}?) lives in (?:the village of )?([A-Z][a-zA-Z]+)",
     lambda m: (m.group(1).strip(), "My %s lives in %s." % (m.group(1).strip(), m.group(2)), m.group(2).lower())),
    (r"[Ii] promised to bring you an? ([a-z][a-z ]{0,40}?)(?: next| in | on |\.|,|$)",
     lambda m: ("promise", "I promised to bring you a %s." % m.group(1).strip(), m.group(1).strip().lower())),
    (r"([A-Z][a-zA-Z]+) your ([a-z]+) who ([a-z ]{0,40}?)(?:,|\.| and |$)",
     lambda m: (m.group(2).strip(), "%s, my %s, %s." % (m.group(1), m.group(2).strip(), m.group(3).strip()), m.group(1).lower())),
    (r"([A-Z][a-zA-Z]+) your ([a-z]+)(?:,|\.| and |$)",
     lambda m: (m.group(2).strip(), "%s is my %s." % (m.group(1), m.group(2).strip()), m.group(1).lower())),
]

def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def extract_facts(text):
    """Return list of (subject, statement, value). Value is the fact's identity
    (the name/place/object), so restatements in other words dedupe."""
    out = []
    seen = set()
    for sent in sentences(text):
        matched = False
        for pat, fn in PATTERNS:
            for m in re.finditer(pat, sent, re.IGNORECASE):
                subj, stmt, val = fn(m)
                key = (subj.lower(), val)
                if key not in seen:
                    seen.add(key); out.append((subj.lower(), stmt, val)); matched = True
        if not matched and re.search(r"\bmy [a-z]+", sent) and len(sent) > 15:
            mm = re.search(r"\bmy ([a-z]+)", sent)
            subj = "note:" + mm.group(1)
            if (subj, sent) not in seen:
                seen.add((subj, sent)); out.append((subj, sent, sent))
    return out

def ledger_apply(led, facts):
    """led: {'current': {subj: (stmt, value)}, 'superseded': [(subj, stmt)], 'order': [subj]}
    Idempotent: same subject + same value (any wording) is a no-op — stateless-
    resend clients re-distill the same turns on every request. Same subject +
    new value supersedes; the old line is kept, marked, exactly once."""
    for subj, stmt, val in facts:
        cur = led["current"].get(subj)
        if cur is not None:
            if cur[1] == val:
                continue
            if not subj.startswith("note:") and (subj, cur[0]) not in led["superseded"]:
                led["superseded"].append((subj, cur[0]))
        else:
            led["order"].append(subj)
        led["current"][subj] = (stmt, val)

def memory_band_text(led):
    if not led["current"]:
        return ""
    lines = ["Memory from earlier in this conversation (distilled facts, current values):"]
    for subj in led["order"]:
        if subj in led["current"]:
            lines.append("- %s: %s" % (subj, led["current"][subj][0]))
    for subj, old in led["superseded"]:
        lines.append("- [superseded] %s: %s" % (subj, old))
    summary = " ".join(led["current"][s][0] for s in led["order"] if s in led["current"])
    lines.append("Summary: " + summary)
    return "\n".join(lines)

# ---------- session handling ----------
def get_session(sid):
    return SESSIONS.setdefault(sid, {"turns": [], "ledger": {"current": {}, "superseded": [], "order": []}, "raw_shed": []})

def reconcile(sess, conv):
    old = sess["turns"]
    if len(conv) >= len(old) and conv[:len(old)] == old:
        sess["turns"] = conv
    elif len(conv) < len(old) and old[:len(conv)] == conv:
        sess["turns"] = conv
    else:
        sess["turns"] = conv
    return sess["turns"]

def assemble(payload):
    messages = payload.get("messages", [])
    systems = [m for m in messages if m.get("role") == "system"]
    conv = [m for m in messages if m.get("role") != "system"]
    anchor = "\n".join(m.get("content", "") for m in systems)
    sid = session_id(payload, anchor)
    sess = get_session(sid)
    turns = reconcile(sess, list(conv))
    opts = dict(payload.get("options") or {})
    window = int(opts.get("num_ctx") or DEFAULT_CTX)
    reserve = int(opts.get("num_predict") or 512) + 32
    budget = max(256, window - reserve)

    core = payload.get("omf_core") or anchor[:280]
    anchor_msg = {"role": "system", "content": anchor} if anchor else None
    core_msg = {"role": "system", "content": core} if (core and CORE_MODE == "post") else None
    if CORE_MODE == "front" and anchor and core:
        anchor_msg = {"role": "system", "content": anchor + "\n" + core}
        core_msg = None

    history = list(turns[:-1])
    final = turns[-1:]
    def fixed_tokens(band_text):
        f = 0
        if anchor_msg: f += msg_tokens(anchor_msg)
        if core_msg: f += msg_tokens(core_msg)
        if band_text: f += est_tokens(band_text)
        f += sum(msg_tokens(m) for m in final)
        return f

    # Distill-then-shed in batches to ~70% of budget.
    band_text = memory_band_text(sess["ledger"])
    total = fixed_tokens(band_text) + sum(msg_tokens(m) for m in history)
    shed = 0
    target = int(budget * 0.70)
    while total > budget and len(history) > 2:
        # one batch: pop oldest until under target or history floor
        batch = []
        while total > target and len(history) > 2:
            m = history.pop(0); batch.append(m)
            total -= msg_tokens(m)
        kept = []
        for m in batch:
            try:
                facts = extract_facts(m.get("content", ""))
                ledger_apply(sess["ledger"], facts)
                sess["raw_shed"].append(m)
                shed += 1
            except Exception:
                kept.append(m)  # distillation failed: keep raw, lose nothing
        if kept:
            history = kept + history
            break
        band_text = memory_band_text(sess["ledger"])
        total = fixed_tokens(band_text) + sum(msg_tokens(m) for m in history)
        if not batch:
            break

    out = []
    if anchor_msg: out.append(anchor_msg)
    if band_text: out.append({"role": "system", "content": band_text})
    out.extend(history)
    out.extend(final)
    if core_msg: out.append(core_msg)

    anchor_tokens = msg_tokens(anchor_msg) if anchor_msg else 0
    want_keep = anchor_tokens + 16
    if int(opts.get("num_keep") or 0) < want_keep:
        opts["num_keep"] = want_keep
    new_payload = dict(payload)
    new_payload.pop("omf_session", None); new_payload.pop("omf_core", None)
    new_payload["messages"] = out
    new_payload["options"] = opts
    stats = {"sid": sid, "shed": shed, "est_tokens": total, "budget": budget,
             "anchor_tokens": anchor_tokens, "msgs_in": len(messages), "msgs_out": len(out),
             "ledger_facts": len(sess["ledger"]["current"]), "superseded": len(sess["ledger"]["superseded"])}
    return new_payload, stats

def forward(path, body, stream):
    req = urllib.request.Request(UPSTREAM + path, data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req, timeout=1200)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def do_GET(self):
        if self.path == "/omf/health":
            self._json(200, {"ok": True, "sessions": len(SESSIONS), "core_mode": CORE_MODE, "version": 2})
            return
        try:
            with urllib.request.urlopen(UPSTREAM + self.path, timeout=60) as r:
                self._raw(200, r.read(), r.headers.get("Content-Type", "application/json"))
        except Exception as e:
            self._json(502, {"error": str(e)})
    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length)
        if self.path != "/api/chat":
            return self._proxy(body)
        try:
            payload = json.loads(body or b"{}")
        except Exception:
            return self._proxy(body)
        if not payload.get("messages"):
            return self._proxy(body)
        new_payload, stats = assemble(payload)
        out_body = json.dumps(new_payload).encode()
        stream = bool(payload.get("stream"))
        try:
            with forward("/api/chat", out_body, stream) as r:
                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.end_headers()
                    for line in r:
                        self.wfile.write(line); self.wfile.flush()
                else:
                    data = r.read()
                    try:
                        j = json.loads(data); stats["prompt_eval_count"] = j.get("prompt_eval_count")
                    except Exception:
                        pass
                    sys.stderr.write("OMF %s\n" % json.dumps(stats))
                    self._raw(200, data, "application/json")
        except urllib.error.HTTPError as e:
            self._raw(e.code, e.read(), "application/json")
        except Exception as e:
            self._json(502, {"error": str(e)})
    def _proxy(self, body):
        try:
            with forward(self.path, body, False) as r:
                self._raw(200, r.read(), r.headers.get("Content-Type", "application/json"))
        except urllib.error.HTTPError as e:
            self._raw(e.code, e.read(), "application/json")
        except Exception as e:
            self._json(502, {"error": str(e)})
    def _json(self, code, obj):
        self._raw(code, json.dumps(obj).encode(), "application/json")
    def _raw(self, code, data, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    sys.stderr.write("OMF layer v2 on 127.0.0.1:%d -> %s (core=%s)\n" % (PORT, UPSTREAM, CORE_MODE))
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
