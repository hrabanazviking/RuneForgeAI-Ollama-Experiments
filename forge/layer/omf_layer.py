#!/usr/bin/env python3
"""OMF forge layer v1 (OM-2): session/anchor layer in front of stock Ollama.

Accepts Ollama-style /api/chat, assembles prompts as:
  [pinned anchor: all system content] -> [recent history, whole turns shed
  from the front-middle under a token budget] -> [final user turn] ->
  [post-history identity core]
Sets num_keep to cover the anchor. Everything else proxies untouched.

Env: OMF_UPSTREAM (default http://127.0.0.1:11499), OMF_PORT (11500),
OMF_CORE = post|front|off (identity-core placement, default post),
OMF_DEFAULT_CTX (8192).
"""
import hashlib, json, math, os, sys, urllib.request, urllib.error
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

def reconcile(sid, conv):
    """Keep a canonical copy of the conversation per session.
    Extension -> adopt. Shorter restart -> reset. Divergence -> adopt."""
    s = SESSIONS.setdefault(sid, {"turns": []})
    old = s["turns"]
    if len(conv) >= len(old) and conv[:len(old)] == old:
        s["turns"] = conv
    elif len(conv) < len(old) and old[:len(conv)] == conv:
        s["turns"] = conv  # client rewound / new chat with same anchor
    else:
        s["turns"] = conv  # divergence (edit): client text wins in v1
    return s["turns"]

def assemble(payload):
    messages = payload.get("messages", [])
    systems = [m for m in messages if m.get("role") == "system"]
    conv = [m for m in messages if m.get("role") != "system"]
    anchor = "\n".join(m.get("content", "") for m in systems)
    sid = session_id(payload, anchor)
    turns = reconcile(sid, conv)
    opts = dict(payload.get("options") or {})
    window = int(opts.get("num_ctx") or DEFAULT_CTX)
    reserve = int(opts.get("num_predict") or 512) + 32
    budget = max(256, window - reserve)

    core = payload.get("omf_core") or anchor[:280]
    anchor_msg = {"role": "system", "content": anchor} if anchor else None
    core_msg = {"role": "system", "content": core} if (core and CORE_MODE == "post") else None

    fixed = 0
    if anchor_msg: fixed += msg_tokens(anchor_msg)
    if core_msg: fixed += msg_tokens(core_msg)
    if CORE_MODE == "front" and anchor and core:
        anchor_msg = {"role": "system", "content": anchor + "\n" + core}
        fixed = msg_tokens(anchor_msg)

    history = list(turns[:-1])
    final = turns[-1:]  # newest message (normally the new user turn)
    fixed += sum(msg_tokens(m) for m in final)
    # Shed oldest history first, in whole messages, keeping at least 2.
    shed = 0
    total = fixed + sum(msg_tokens(m) for m in history)
    while total > budget and len(history) > 2:
        total -= msg_tokens(history.pop(0))
        shed += 1

    out = []
    if anchor_msg: out.append(anchor_msg)
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
             "anchor_tokens": anchor_tokens, "msgs_in": len(messages), "msgs_out": len(out)}
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
            self._json(200, {"ok": True, "sessions": len(SESSIONS), "core_mode": CORE_MODE})
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
                        self.wfile.write(line)
                        self.wfile.flush()
                else:
                    data = r.read()
                    try:
                        j = json.loads(data)
                        stats["prompt_eval_count"] = j.get("prompt_eval_count")
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
    sys.stderr.write("OMF layer on 127.0.0.1:%d -> %s (core=%s)\n" % (PORT, UPSTREAM, CORE_MODE))
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
