"""A scripted MCP client (standard library only) that drives a stdio server through a fixed sequence.

    python mcp_server/client.py --target js3          # this folder's server (mcp_server/server.py)
    python mcp_server/client.py --target reference    # the course server, lessons/08-mcp-from-scratch/code/main.py

The client starts the server as a subprocess, sends one JSON-RPC message per line, waits for the
reply to every request (never for a notification), and logs both directions with timestamps to
mcp_server/transcripts/<date>-client-side-<target>.jsonl. The sequence includes error cases on purpose.
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]   # mcp_server -> js3-filter-tool-score -> nishant-u -> fall-2026 -> repo
TARGETS = {
    "js3": {"command": [sys.executable, str(HERE / "server.py")],
            "good": {"posting_id": "greenhouse:faire:8806617002"},
            "missing": {"posting_id": "greenhouse:faire:999"},
            "path": {"posting_id": "../../x"}},
    "reference": {"command": [sys.executable, str(REPO / "lessons" / "08-mcp-from-scratch" / "code" / "main.py"), "--stdio"],
                  "good": {"key": "office"},
                  "missing": {"key": "missing"},
                  "path": {"key": "../../x"}},
}
CLIENT_INFO = {"name": "js3-scripted-client", "version": "1.0.0"}


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")


def sequence(tool, t):
    """(label, raw line, expects a reply)."""
    def msg(m):
        return json.dumps(m)
    return [
        ("tools/list before initialize (should be refused)", msg({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}), True),
        ("initialize", msg({"jsonrpc": "2.0", "id": 2, "method": "initialize",
                            "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": CLIENT_INFO}}), True),
        ("notifications/initialized", msg({"jsonrpc": "2.0", "method": "notifications/initialized"}), False),
        ("tools/list", msg({"jsonrpc": "2.0", "id": 3, "method": "tools/list"}), True),
        ("tools/call, good arguments", msg({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                                           "params": {"name": tool, "arguments": t["good"]}}), True),
        ("tools/call, unknown record (should be isError)", msg({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                                                               "params": {"name": tool, "arguments": t["missing"]}}), True),
        ("tools/call, path-like argument", msg({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                                               "params": {"name": tool, "arguments": t["path"]}}), True),
        ("tools/call, bad params (should be -32602)", msg({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                                                          "params": {"name": tool, "arguments": {"wrong": 1}}}), True),
        ("unknown method (should be -32601)", msg({"jsonrpc": "2.0", "id": 8, "method": "resources/list"}), True),
        ("malformed JSON (should be -32700)", '{"jsonrpc": "2.0", "id": 9, "method": ', True),
    ]


def run(target, log_dir=HERE / "transcripts"):
    t = TARGETS[target]
    proc = subprocess.Popen(t["command"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            cwd=str(HERE.parent))
    # Log the command relative to the repository, never as an absolute machine path.
    shown = [Path(c).resolve().relative_to(REPO).as_posix() if Path(c).is_absolute() else c for c in t["command"][1:]]
    records = [{"ts": now(), "dir": "meta", "target": target, "command": ["python"] + shown}]
    tool = None
    try:
        for label, line, expects_reply in sequence("?", t):
            if tool is None and label.startswith("tools/call"):
                raise RuntimeError("no tool discovered")
            if label.startswith("tools/call"):
                line = line.replace('"name": "?"', json.dumps({"name": tool})[1:-1])
            proc.stdin.write((line + "\n").encode("utf-8"))
            proc.stdin.flush()
            records.append({"ts": now(), "dir": "out", "label": label, "raw": line})
            print(f">>> {label}\n    {line}")
            if expects_reply:
                reply = proc.stdout.readline().decode("utf-8").rstrip("\r\n")
                records.append({"ts": now(), "dir": "in", "label": label, "raw": reply})
                print(f"<<< {reply[:300]}{'...' if len(reply) > 300 else ''}")
                if label == "tools/list":
                    tool = json.loads(reply)["result"]["tools"][0]["name"]
    except (OSError, ValueError) as exc:
        records.append({"ts": now(), "dir": "meta", "client_error": repr(exc)})
        print(f"client stopped: {exc!r}")
    finally:
        try:
            proc.stdin.close()
        except OSError:
            pass
        proc.wait(timeout=10)
        records.append({"ts": now(), "dir": "meta", "exit_code": proc.returncode,
                        "stderr": proc.stderr.read().decode("utf-8", errors="replace")})
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        path = log_dir / f"{datetime.date.today().isoformat()}-client-side-{target}.jsonl"
        with open(path, "a", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"client-side transcript: {path}")
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--target", choices=sorted(TARGETS), required=True)
    run(parser.parse_args().target)


if __name__ == "__main__":
    main()
