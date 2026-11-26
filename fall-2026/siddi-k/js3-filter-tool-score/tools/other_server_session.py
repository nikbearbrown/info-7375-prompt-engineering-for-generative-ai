"""One real Claude CLI session against the course's Chapter 8 lesson server, logged both ways by tools/stdio_tap.py.

The server file is taken from git (lessons/08-mcp-from-scratch/code/main.py at commit a8629ce1), written to a new
temp directory, and checked against its sha256 before it runs. Writes evidence/other-server/<stamp>/."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import claude_cli, policy  # noqa: E402

COMMIT, PATH = "a8629ce1", "lessons/08-mcp-from-scratch/code/main.py"
SHA256 = "948337afc71b67b659aac44b4a8f3efec5dc699b9bb7c2e683dd6888068b1769"
PROMPT = ("Use the lookup tool to read the record with key \"office\" and tell me what it says. Then, in one "
          "sentence, say what this server tells you about whether its tool can change anything, and where that "
          "information comes from.\n")


def main() -> int:
    src = subprocess.run(["git", "show", f"{COMMIT}:{PATH}"], capture_output=True, cwd=policy.ROOT, check=True).stdout
    if hashlib.sha256(src).hexdigest() != SHA256:
        raise SystemExit("course server file does not match the recorded sha256; refusing to run it")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    out = f"evidence/other-server/{stamp}"
    with tempfile.TemporaryDirectory(prefix="js3-course-server-") as tmp:
        server = Path(tmp) / "main.py"
        server.write_bytes(src)
        tap_log = policy.check_write(f"{out}/tap-transcript.jsonl")
        cfg = {"mcpServers": {"course": {"type": "stdio", "command": sys.executable,
                                         "args": [str(policy.ROOT / "tools" / "stdio_tap.py"), "--log", str(tap_log),
                                                  "--", sys.executable, str(server), "--stdio"]}}}
        argv, stdout, stderr, code = claude_cli.run(PROMPT, ["--allowedTools", "mcp__course__lookup"],
                                                    output_format="stream-json", mcp_config=cfg)
    shown = ["claude" if i == 0 else ("<tmp>/mcp.json" if x.endswith("mcp.json") else x) for i, x in enumerate(argv)]
    policy.write_bytes(f"{out}/prompt.txt", PROMPT.encode("utf-8"))
    policy.write_bytes(f"{out}/argv.json", (json.dumps({"argv": shown, "server": f"{PATH} @ {COMMIT}",
                                                        "server_sha256": SHA256, "exit_code": code}, indent=2) + "\n").encode())
    policy.write_bytes(f"{out}/claude-stream.jsonl", stdout)
    policy.write_bytes(f"{out}/stderr.txt", stderr.encode("utf-8"))
    print(f"exit {code}; wrote {out}/")
    return code


if __name__ == "__main__":
    sys.exit(main())
