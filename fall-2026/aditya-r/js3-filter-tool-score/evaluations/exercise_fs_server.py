"""Exercise @modelcontextprotocol/server-filesystem 2.3.0 with the js3 test client (NOT Claude).

  .venv/bin/python evaluations/exercise_fs_server.py <path to installed server-filesystem package> <empty sandbox dir>

The script builds this sandbox (all local, throwaway):
  allowed/note.txt
  allowed/link_out -> ../outside          (symlink pointing out of the allowed dir)
  outside/secret.txt
  other_root/root_file.txt

It runs four sessions:
  A: default mode
  B: --read-only
  C: default mode, with a client whose Roots name other_root
  D: C plus --confine-roots

Each session's transcript is published to transcripts/fs_<session>.jsonl, with the sandbox path redacted to <SANDBOX>.
Findings are printed and written to evaluations/fs_server_observed.json.
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from js3.mcp_client import StdioClient  # noqa: E402
from js3.transcript import publish  # noqa: E402


def text(r):
    if "error" in r:
        return f"JSON-RPC error {r['error']['code']}: {r['error']['message']}"
    res = r["result"]
    body = " ".join(c.get("text", "") for c in res.get("content", []))
    return ("isError " if res.get("isError") else "ok ") + body


def make_sandbox(sb):
    (sb / "allowed").mkdir(parents=True)
    (sb / "outside").mkdir()
    (sb / "other_root").mkdir()
    (sb / "allowed" / "note.txt").write_text("note inside the allowed directory\n")
    (sb / "outside" / "secret.txt").write_text("SECRET outside the allowed directory\n")
    (sb / "other_root" / "root_file.txt").write_text("file in a directory the client names as a root\n")
    os.symlink("../outside", sb / "allowed" / "link_out")


def session(name, pkg, sb, args, roots=None):
    log = sb / f"{name}.raw.jsonl"
    on_req = (lambda m: {"roots": [{"uri": f"file://{sb / r}", "name": r} for r in roots]}
              if m["method"] == "roots/list" else None) if roots else None
    c = StdioClient(["node", str(pkg / "dist" / "index.js"), *args], log_path=log, cwd=str(sb), on_request=on_req)
    obs = {}
    caps = {"roots": {"listChanged": True}} if roots else {}
    init = c.initialize("2025-11-25", caps)
    obs["initialize.capabilities"] = init["result"]["capabilities"]
    tools = c.request("tools/list")["result"]["tools"]
    obs["tools"] = {t["name"]: {k: t.get("annotations", {}).get(k) for k in ("readOnlyHint", "destructiveHint")}
                    for t in tools}
    call = lambda tool, **a: text(c.request("tools/call", {"name": tool, "arguments": a}))
    obs["list_allowed_directories"] = call("list_allowed_directories")
    obs["read allowed/note.txt"] = call("read_text_file", path=str(sb / "allowed" / "note.txt"))
    obs["read outside/secret.txt"] = call("read_text_file", path=str(sb / "outside" / "secret.txt"))
    obs["read allowed/../outside/secret.txt"] = call("read_text_file", path=str(sb / "allowed") + "/../outside/secret.txt")
    obs["read allowed/link_out/secret.txt (symlink)"] = call("read_text_file", path=str(sb / "allowed" / "link_out" / "secret.txt"))
    obs["read other_root/root_file.txt"] = call("read_text_file", path=str(sb / "other_root" / "root_file.txt"))
    obs["write_file allowed/new.txt"] = call("write_file", path=str(sb / "allowed" / f"new_{name}.txt"), content="written by test")
    obs["file exists after write"] = (sb / "allowed" / f"new_{name}.txt").exists()
    c.close()
    publish(log, f"fs_{name}", "js3 test client (js3/mcp_client.py), NOT Claude; server @modelcontextprotocol/server-filesystem 2.3.0",
            dt.date.today().isoformat(), redact={str(sb): "<SANDBOX>"})
    log.unlink()
    obs = json.loads(json.dumps(obs).replace(str(sb), "<SANDBOX>"))  # redact first, then shorten
    return {k: (v[:220] if isinstance(v, str) else v) for k, v in obs.items()}


def main(pkg, sb):
    pkg, sb = Path(pkg).resolve(), Path(sb).resolve()
    assert not any(sb.iterdir()), "sandbox must be empty"
    make_sandbox(sb)
    allowed = str(sb / "allowed")
    results = {
        "server": "@modelcontextprotocol/server-filesystem 2.3.0 (npm, published 2026-11-11; installed with --ignore-scripts)",
        "node": os.popen("node --version").read().strip() + " (package declares engines node >=24)",
        "client": "js3 test client, not Claude",
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "A_default": session("A_default", pkg, sb, [allowed]),
        "B_read_only": session("B_read_only", pkg, sb, ["--read-only", allowed]),
        "C_client_roots": session("C_client_roots", pkg, sb, [allowed], roots=["other_root"]),
        "D_confine_roots": session("D_confine_roots", pkg, sb, ["--confine-roots", allowed], roots=["other_root"]),
    }
    (ROOT / "evaluations" / "fs_server_observed.json").write_text(json.dumps(results, indent=1) + "\n")
    for s in ("A_default", "B_read_only", "C_client_roots", "D_confine_roots"):
        print(f"\n== {s}: {len(results[s]['tools'])} tools")
        for k, v in results[s].items():
            if k != "tools":
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
