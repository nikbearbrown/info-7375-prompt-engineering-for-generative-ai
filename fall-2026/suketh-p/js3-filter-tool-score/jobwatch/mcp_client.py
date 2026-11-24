"""A scripted client harness for stdio tool servers, with a capability record.

  python3 -m jobwatch.mcp_client --script transcripts/scripts/NAME.json --log transcripts/NAME.jsonl -- CMD...

It starts the server under a Python audit hook (when CMD is a Python program), sends each
scripted message as one line, waits up to --timeout seconds for the response to every request
(a notification gets no wait), and records both directions with UTC times. The audit hook
writes every file open, socket, process start and file deletion the server makes to standard
error; the harness keeps those lines in the same log, so the capability ledger can cite them.

This is a harness that stands in for a client (Chapter 8: "an explicit harness that represents
the client's obligations"). It is not Claude Code, and its messages are CONSTRUCTED."""

import argparse
import datetime
import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = PROJECT_ROOT / "transcripts"

# Installed before the server's own code runs. Reports what the process touches.
BOOTSTRAP = r"""
import json, os, runpy, sys
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
WATCH = ("open", "os.remove", "os.rename", "os.rmdir", "os.mkdir", "shutil.rmtree", "shutil.copyfile",
         "socket.connect", "socket.bind", "socket.getaddrinfo", "socket.sendto", "subprocess.Popen",
         "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.kill", "urllib.Request")
def hook(event, args):
    if event not in WATCH:
        return
    detail = {"event": event}
    if event == "open":
        path, mode, flags = args
        detail["path"] = str(path)
        writes = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (isinstance(flags, int) and flags & WRITE_FLAGS)
        detail["access"] = "write" if writes else "read"
    else:
        detail["args"] = repr(args)[:300]
    sys.stderr.write("AUDIT " + json.dumps(detail) + "\n")
    sys.stderr.flush()
sys.addaudithook(hook)
target = sys.argv[1]
sys.argv = sys.argv[1:]
if target == "-m":
    module = sys.argv[1]; sys.argv = sys.argv[1:]
    runpy.run_module(module, run_name="__main__", alter_sys=True)
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(target)))
    runpy.run_path(target, run_name="__main__")
"""


def allowed_log(path):
    resolved = (Path(path) if Path(path).is_absolute() else Path.cwd() / path).resolve()
    if resolved.parent != TRANSCRIPTS.resolve() or resolved.suffix != ".jsonl" or resolved.exists():
        raise SystemExit(f"refused: the log must be a new .jsonl file directly inside {TRANSCRIPTS}")
    return resolved


def run(command, script, log_path, timeout=10.0, cwd=PROJECT_ROOT, audit=True):
    original = list(command)
    audit = audit and command[:1] == ["python3"]
    if audit:
        command = ["python3", "-B", "-c", BOOTSTRAP] + command[1:]
    log = open(log_path, "x", encoding="utf-8")
    seq = [0]
    lock = threading.Lock()

    def record(direction, line):
        with lock:
            seq[0] += 1
            stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")
            log.write(json.dumps({"seq": seq[0], "at": stamp, "direction": direction, "line": line.rstrip("\n")},
                                 ensure_ascii=False) + "\n")
            log.flush()

    record("harness", "start " + json.dumps({"command": original, "cwd": Path(cwd).name,
                                             "audit_hook": audit, "python_flags": ["-B"] if audit else []}))
    child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, bufsize=1, cwd=cwd)
    responses = queue.Queue()

    def read_stdout():
        for line in child.stdout:
            record("server->client", line)
            responses.put(line)

    def read_stderr():
        for line in child.stderr:
            record("server-stderr", line)

    threads = [threading.Thread(target=read_stdout, daemon=True), threading.Thread(target=read_stderr, daemon=True)]
    for t in threads:
        t.start()
    for step in script:
        line = step["raw"] if "raw" in step else json.dumps(step["message"], ensure_ascii=False)
        record("client->server", line)
        child.stdin.write(line + "\n")
        child.stdin.flush()
        if step.get("expect_response", True):
            try:
                responses.get(timeout=timeout)
            except queue.Empty:
                record("harness", f"no response within {timeout} s")
    child.stdin.close()
    code = child.wait(timeout=timeout)
    for t in threads:
        t.join(timeout=timeout)
    child.stdout.close()
    child.stderr.close()
    record("harness", f"input closed; server exited with code {code}")
    log.close()
    return code


def capability_report(log_path, project_marker="js3-filter-tool-score"):
    """What the audit hook saw in one harness log: reads, writes, network, processes."""
    with open(log_path, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh]
    events =[json.loads(r["line"][len("AUDIT "):]) for r in rows
              if r["direction"] == "server-stderr" and r["line"].startswith("AUDIT ")]
    report = {"reads": [], "writes": [], "network": [], "processes": [], "other": []}
    for e in events:
        if e["event"] == "open":
            report["writes" if e["access"] == "write" else "reads"].append(e["path"])
        elif e["event"].startswith("socket") or e["event"].startswith("urllib"):
            report["network"].append(e)
        elif e["event"] in ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.kill"):
            report["processes"].append(e)
        else:
            report["other"].append(e)
    report["reads_in_project"] = sorted({p.split(project_marker + "/", 1)[1] for p in report["reads"] if project_marker + "/" in p})
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m jobwatch.mcp_client")
    parser.add_argument("--script", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--cwd", default=str(PROJECT_ROOT))
    parser.add_argument("server", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.server[1:] if args.server[:1] == ["--"] else args.server
    script = json.loads(Path(args.script).read_text(encoding="utf-8"))
    return run(command, script, allowed_log(args.log), timeout=args.timeout, cwd=args.cwd)


if __name__ == "__main__":
    sys.exit(main())
