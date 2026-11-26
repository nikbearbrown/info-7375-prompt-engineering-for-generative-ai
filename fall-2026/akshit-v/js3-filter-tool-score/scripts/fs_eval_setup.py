"""Build a throwaway sandbox for evaluating @modelcontextprotocol/server-filesystem, and write the probes.

    python -B scripts/fs_eval_setup.py <sandbox dir outside this project>

Sandbox layout (every file is CONSTRUCTED):
  allowed/notes.txt              the one directory the operator allows
  allowed/link_out  -> outside/  a junction (Windows) or symlink (POSIX) pointing out (like JS2's B10)
  allowed-evil/secret.txt        a look-alike sibling (like JS2's W-b prefix bug)
  outside/secret.txt             must never be readable
Probes written to mcp/probes/fs_*.json, with the sandbox's real paths filled in.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def call(i, tool, **args):
    return {"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": tool, "arguments": args}}


def init(i, roots: bool):
    caps = {"roots": {"listChanged": False}} if roots else {}
    return {"jsonrpc": "2.0", "id": i, "method": "initialize",
            "params": {"protocolVersion": "2025-11-25", "capabilities": caps,
                       "clientInfo": {"name": "js3-probe", "version": "1.0"}}}


INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def main() -> int:
    sb = Path(sys.argv[1]).resolve()
    if ROOT in sb.parents or sb == ROOT:
        raise SystemExit("the sandbox must be outside the project folder")
    if sb.exists():
        shutil.rmtree(sb)
    (sb / "allowed").mkdir(parents=True)
    (sb / "allowed-evil").mkdir()
    (sb / "outside").mkdir()
    (sb / "allowed" / "notes.txt").write_text("CONSTRUCTED: an allowed file.\n", encoding="utf-8")
    (sb / "allowed-evil" / "secret.txt").write_text("CONSTRUCTED: sibling secret.\n", encoding="utf-8")
    (sb / "outside" / "secret.txt").write_text("CONSTRUCTED: outside secret.\n", encoding="utf-8")
    link = sb / "allowed" / "link_out"
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(sb / "outside")], check=True, capture_output=True)
    else:
        os.symlink(sb / "outside", link)
    A, E, O = str(sb / "allowed"), str(sb / "allowed-evil"), str(sb / "outside")
    sep = os.sep

    base = [
        {"note": "Handshake. The client does NOT declare the roots capability."},
        init(1, roots=False), INITIALIZED,
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        call(3, "list_allowed_directories"),
        {"note": "Declared: reads inside the allowed directory work."},
        call(4, "read_text_file", path=A + sep + "notes.txt"),
        {"note": "Boundary: '..' out of the allowed directory."},
        call(5, "read_text_file", path=A + sep + ".." + sep + "outside" + sep + "secret.txt"),
        {"note": "Boundary: a look-alike sibling directory (string-prefix bug)."},
        call(6, "read_text_file", path=E + sep + "secret.txt"),
        {"note": "Boundary: a junction/symlink inside the allowed directory that points outside."},
        call(7, "read_text_file", path=A + sep + "link_out" + sep + "secret.txt"),
        call(8, "list_directory", path=A + sep + "link_out"),
        {"note": "A relative path: resolved against what?"},
        call(9, "read_text_file", path="notes.txt"),
        {"note": "Writes: the server is called 'filesystem'; does it write by default?"},
        call(10, "write_file", path=A + sep + "written_by_probe.txt", content="CONSTRUCTED: written by the probe\n"),
        call(11, "write_file", path=A + sep + "link_out" + sep + "pwned.txt", content="must be refused\n"),
        {"note": "Schema: an argument the tool does not declare."},
        call(12, "read_text_file", path=A + sep + "notes.txt", exfiltrate_to="https://example.com"),
        {"note": "A tool that is not on the list."},
        call(13, "delete_file", path=A + sep + "notes.txt"),
    ]
    read_only = [
        {"note": "Started with --read-only."},
        init(1, roots=False), INITIALIZED,
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        call(3, "write_file", path=A + sep + "ro_attempt.txt", content="must be refused\n"),
        call(4, "read_text_file", path=A + sep + "notes.txt"),
    ]
    roots = [
        {"note": "The client DOES declare roots, and answers roots/list with a root OUTSIDE the operator's directory."},
        {"respond_to": "roots/list", "result": {"roots": [{"uri": (sb / "outside").as_uri(), "name": "client root"}]}},
        init(1, roots=True), INITIALIZED,
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        call(3, "list_allowed_directories"),
        call(4, "read_text_file", path=O + sep + "secret.txt"),
        call(5, "read_text_file", path=A + sep + "notes.txt"),
    ]
    out = ROOT / "mcp" / "probes"
    out.mkdir(parents=True, exist_ok=True)
    for name, steps in (("fs_default", base), ("fs_read_only", read_only), ("fs_roots", roots)):
        (out / f"{name}.json").write_text(json.dumps(steps, indent=1) + "\n", encoding="utf-8")
    print(f"sandbox {sb}; probes fs_default, fs_read_only, fs_roots written; allowed dir: {A}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
