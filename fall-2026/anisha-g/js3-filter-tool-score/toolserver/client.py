"""My scripted MCP client (written from scratch). Starts a server as a subprocess, sends a fixed script of messages over
stdio and records BOTH directions, client-side, to transcripts/client-<name>-<ts>.jsonl. Used for my own server and for
the other server I evaluate.   Run:  python3 toolserver/client.py <name> <script.json> -- <server command...>"""
import json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

def main():
    name, script = sys.argv[1], json.loads(Path(sys.argv[2]).read_text())
    cmd = sys.argv[sys.argv.index("--") + 1:]
    out = Path("transcripts") / f"client-{name}-{datetime.now().strftime('%Y%m%dT%H%M%S')}.jsonl"
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    def log(d, **kw):
        with out.open("a") as f: f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "dir": d, **kw}) + "\n")
    for step in script:
        line = step["raw"] if "raw" in step else json.dumps(step["msg"])
        log("client->server", **({"raw": line} if "raw" in step else {"msg": step["msg"]}), note=step.get("note", ""))
        p.stdin.write(line + "\n"); p.stdin.flush()
        if step.get("expect_reply", True):
            reply = p.stdout.readline()
            try: log("server->client", msg=json.loads(reply))
            except json.JSONDecodeError: log("server->client", raw=reply)
            print(f"{step.get('note',''):55s} -> {reply.strip()[:150]}")
        else:
            time.sleep(0.2)
    p.stdin.close(); p.wait(timeout=10)
    print(f"transcript: {out}")

if __name__ == "__main__": main()
