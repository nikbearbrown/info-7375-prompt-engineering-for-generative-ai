"""Evaluate someone else's MCP server the way we evaluated ours: the official filesystem server
(@modelcontextprotocol/server-filesystem, pinned), run through the same logging tap.

    python scripts/probe_other_server.py declare   # initialize + tools/list only -> what it declares
    python scripts/probe_other_server.py probe     # the boundary cases from EVAL-OTHER-SERVER.md
    python scripts/probe_other_server.py roots     # a client that answers roots/list with a folder outside

Every run builds a fresh CONSTRUCTED sandbox in a temporary folder (never this repo):
    allowed/note.txt            inside the allowed folder
    allowed-evil/secret.txt     a sibling whose name starts with the allowed name (prefix trick)
    outside/secret.txt          outside, reachable by '..'
    allowed/link -> ../outside  a symlink inside the allowed folder that points outside
The server is started with only `allowed/` as its allowed directory.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = "@modelcontextprotocol/server-filesystem@2.2.0"
INTEGRITY = "sha512-mNLj/qhV+P4kj1qP8VzgQ2fjSmWcKDQ3Q+KpZEA+WahCDWHw5zJBRQUNSPZ6Ai2/ZGGUjzNzsFpz958a1+4T9A=="


def sandbox() -> Path:
    base = Path(os.path.realpath(tempfile.mkdtemp(prefix="fs-sandbox-")))
    (base / "allowed").mkdir()
    (base / "allowed-evil").mkdir()
    (base / "outside").mkdir()
    (base / "allowed" / "note.txt").write_text("CONSTRUCTED: a note inside the allowed folder.\n")
    (base / "allowed-evil" / "secret.txt").write_text("CONSTRUCTED: secret in the prefix-trick sibling.\n")
    (base / "outside" / "secret.txt").write_text("CONSTRUCTED: secret outside the allowed folder.\n")
    os.symlink("../outside", base / "allowed" / "link")
    return base


class Client:
    """A tiny scripted MCP client over the tap. Answers server->client requests (roots/list)."""

    def __init__(self, cmd, log, roots=None):
        tap = [sys.executable, str(ROOT / "scripts" / "mcp_tap.py"), "--log", str(log), "--"] + cmd
        self.p = subprocess.Popen(tap, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        self.roots, self.next_id = roots, 1

    def send(self, msg):
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

    def request(self, method, params=None):
        mid = self.next_id
        self.next_id += 1
        self.send({"jsonrpc": "2.0", "id": mid, "method": method, **({"params": params} if params is not None else {})})
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError("server closed")
            msg = json.loads(line)
            if msg.get("id") == mid and "method" not in msg:
                return msg
            if "method" in msg and "id" in msg:                 # a request from the server to us
                if msg["method"] == "roots/list" and self.roots is not None:
                    self.send({"jsonrpc": "2.0", "id": msg["id"],
                               "result": {"roots": [{"uri": f"file://{r}", "name": Path(r).name} for r in self.roots]}})
                else:
                    self.send({"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": "not supported"}})

    def notify(self, method, params=None):
        self.send({"jsonrpc": "2.0", "method": method, **({"params": params} if params is not None else {})})

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=30)


def start(kind, base, roots=None):
    out = ROOT / "transcripts"
    out.mkdir(exist_ok=True)
    log = out / f"other-filesystem-{kind}-{dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')}.jsonl"
    c = Client(["npx", "-y", PACKAGE, str(base / "allowed")], log, roots=roots)
    caps = {"roots": {"listChanged": False}} if roots is not None else {}
    init = c.request("initialize", {"protocolVersion": "2025-11-25", "capabilities": caps,
                                    "clientInfo": {"name": "probe_other_server.py", "version": "1"}})
    c.notify("notifications/initialized")
    return c, init, log


def text_of(reply):
    if "error" in reply:
        return f"JSON-RPC error {reply['error']['code']}: {reply['error']['message']}"
    r = reply["result"]
    t = " ".join(x.get("text", "") for x in r.get("content", []) if isinstance(x, dict))
    return ("isError: " if r.get("isError") else "") + t


def declare():
    base = sandbox()
    c, init, log = start("declare", base)
    tools = c.request("tools/list")
    c.close()
    out = {"package": PACKAGE, "npm_integrity": INTEGRITY, "initialize": init.get("result"),
           "tools": tools.get("result", {}).get("tools", [])}
    (ROOT / "evals").mkdir(exist_ok=True)
    (ROOT / "evals" / "filesystem-declared.json").write_text(json.dumps(out, indent=2) + "\n")
    for t in out["tools"]:
        print(t["name"], json.dumps(t.get("annotations", {})))
    print("transcript:", log.relative_to(ROOT))


def probe():
    base = sandbox()
    a, ev, out_ = base / "allowed", base / "allowed-evil", base / "outside"
    c, _, log = start("probe", base)
    cases = [
        ("1 list allowed directories", "list_allowed_directories", {}),
        ("2 read inside", "read_text_file", {"path": str(a / "note.txt")}),
        ("3 '..' escape", "read_text_file", {"path": str(a) + "/../outside/secret.txt"}),
        ("4 prefix trick (CVE-2025-53110)", "read_text_file", {"path": str(ev / "secret.txt")}),
        ("5 symlink read escape (CVE-2025-53109)", "read_text_file", {"path": str(a / "link" / "secret.txt")}),
        ("6 write inside", "write_file", {"path": str(a / "written.txt"), "content": "CONSTRUCTED write inside.\n"}),
        ("7 symlink write escape", "write_file", {"path": str(a / "link" / "pwned.txt"), "content": "CONSTRUCTED.\n"}),
        ("8 list the parent", "list_directory", {"path": str(base)}),
        ("9 relative path", "read_text_file", {"path": "note.txt"}),
        ("10 unknown tool", "delete_everything", {"path": str(a)}),
    ]
    results = []
    for name, tool, args in cases:
        reply = c.request("tools/call", {"name": tool, "arguments": args})
        results.append({"case": name, "tool": tool, "arguments": {k: v.replace(str(base), "<sandbox>")
                                                                  for k, v in args.items()},
                        "reply": text_of(reply).replace(str(base), "<sandbox>")[:400]})
    c.close()
    on_disk = {"allowed/written.txt exists": (a / "written.txt").exists(),
               "outside/pwned.txt exists": (out_ / "pwned.txt").exists()}
    out = {"package": PACKAGE, "run_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "results": results, "on_disk_after": on_disk}
    (ROOT / "evals" / "filesystem-probe.json").write_text(json.dumps(out, indent=2) + "\n")
    for r in results:
        print(r["case"], "->", r["reply"][:160])
    print(on_disk, "\ntranscript:", log.relative_to(ROOT))


def roots():
    base = sandbox()
    c, _, log = start("roots", base, roots=[str(base / "outside")])
    allowed = c.request("tools/call", {"name": "list_allowed_directories", "arguments": {}})
    secret = c.request("tools/call", {"name": "read_text_file", "arguments": {"path": str(base / "outside" / "secret.txt")}})
    note = c.request("tools/call", {"name": "read_text_file", "arguments": {"path": str(base / "allowed" / "note.txt")}})
    c.close()
    out = {"package": PACKAGE, "run_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "client_roots": ["<sandbox>/outside"],
           "list_allowed_directories": text_of(allowed).replace(str(base), "<sandbox>"),
           "read outside/secret.txt": text_of(secret).replace(str(base), "<sandbox>")[:300],
           "read allowed/note.txt": text_of(note).replace(str(base), "<sandbox>")[:300]}
    (ROOT / "evals" / "filesystem-roots.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2), "\ntranscript:", log.relative_to(ROOT))


if __name__ == "__main__":
    {"declare": declare, "probe": probe, "roots": roots}[sys.argv[1]]()
