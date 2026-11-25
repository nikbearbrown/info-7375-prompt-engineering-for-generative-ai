"""Record one real session with the reference Fetch MCP server, for MCP_EVAL.md "The other server".

    python3 mcp_eval_fetch.py PATH_TO_mcp-server-fetch

The server (PyPI `mcp-server-fetch`, from github.com/modelcontextprotocol/servers) is installed outside this
folder; the path to its executable is the argument. It runs with --no-readability-js, so it never starts
`npm install` (which by default it runs on first use when Node.js is on PATH). This client logs every message
in both directions to state/mcp/other_fetch_<UTC>.jsonl.

The calls test what the server declares against what it does:
1. initialize, tools/list, prompts/list: what it declares.
2. fetch https://example.com/: an ordinary page.
3. fetch https://example.com/?persona=riley-navarro&needs=sponsorship: a "read-only" call whose URL carries
   data out to a host the model chose. The values are the fictional persona's.
4. fetch http://127.0.0.1:<port>/secret.txt: a file served by this script on loopback. The server says it
   refuses private addresses by default.
5. fetch with max_length "10" (a string): its schema says integer, strict.
"""
import datetime as dt
import functools
import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))


def main(exe):
    stamp = f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H%M%SZ}"
    os.makedirs(os.path.join(HERE, "state", "mcp"), exist_ok=True)
    log = open(os.path.join(HERE, "state", "mcp", f"other_fetch_{stamp}.jsonl"), "x", encoding="utf-8")

    def record(direction, message):
        log.write(json.dumps({"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"),
                              "dir": direction, "msg": message}) + "\n")
        log.flush()

    served = tempfile.mkdtemp()
    with open(os.path.join(served, "secret.txt"), "w") as f:
        f.write("loopback-only test file\n")
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Counting, directory=served))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    local = f"http://127.0.0.1:{httpd.server_address[1]}/secret.txt"

    proc = subprocess.Popen([exe, "--no-readability-js"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True)
    ids = iter(range(1, 100))

    def send(method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            msg["id"] = next(ids)
        record("out", msg)  # out = client to server, from this client's side
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        if notify:
            return None
        while True:
            reply = json.loads(proc.stdout.readline())
            record("in", reply)
            if reply.get("id") == msg["id"]:
                break
        print(f"{method} {json.dumps(params)[:90] if params else ''}\n  -> {json.dumps(reply)[:300]}")
        return reply

    send("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                        "clientInfo": {"name": "js3-mcp-eval", "version": "1.0.0"}})
    send("notifications/initialized", notify=True)
    send("tools/list")
    send("prompts/list")
    send("tools/call", {"name": "fetch", "arguments": {"url": "https://example.com/", "max_length": 400}})
    send("tools/call", {"name": "fetch", "arguments": {
        "url": "https://example.com/?persona=riley-navarro&needs=sponsorship", "max_length": 200}})
    send("tools/call", {"name": "fetch", "arguments": {"url": local}})
    send("tools/call", {"name": "fetch", "arguments": {"url": "https://example.com/", "max_length": "10"}})
    proc.stdin.close()
    proc.wait(timeout=30)
    httpd.shutdown()
    record("note", {"loopback_requests_received": Counting.hits})
    print("requests the loopback server received:", Counting.hits)
    return 0


class Counting(http.server.SimpleHTTPRequestHandler):
    """Counts every request that reaches the loopback server, so a refusal can be checked, not assumed."""
    hits = []

    def log_message(self, *args):
        Counting.hits.append(self.path)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
