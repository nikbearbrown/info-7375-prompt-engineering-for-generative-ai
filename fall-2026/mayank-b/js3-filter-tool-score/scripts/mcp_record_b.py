"""Transcript B: Claude Code as a real MCP client of src/jsa3/mcp_server.py, one non-interactive run.

    python3 -I scripts/mcp_record_b.py --corpus <run dir>

Writes, all under transcripts/ and all named B-claude-code-<UTC>.*:
  .mcp-config.json       the exact host configuration passed with --mcp-config (no secrets in it)
  .jsonl                 the server's own --log: every raw stdio line, both directions
  .client-output.json    Claude Code's stdout (--output-format json), verbatim
  .client-stderr.txt     Claude Code's stderr, verbatim, plus the exit code
  .md                    the command, `claude --version`, the methods the client sent, and a mechanical
                         check of whether the tool's verdict and reason appear verbatim in Claude's answer

This makes one Claude Code request on Mayank's account (costs a few cents). The server itself makes no
network request; Claude Code does (to Anthropic's API), which is the host's traffic, not the tool's.
The only tool allowed is mcp__jsa3__score_posting; every built-in tool is disabled with --tools "".
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
sys.path.insert(0, str(PROJECT / "src"))

import mcp_record  # noqa: E402
from jsa3 import corpus as corpus_mod  # noqa: E402

T = PROJECT / "transcripts"
PROMPT = ("Use the score_posting tool to score posting id {pid} and report the verdict and reason exactly "
          "as the tool returned them.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--config", default=str(PROJECT / "config" / "filter.json"))
    ap.add_argument("--posting-id", help="default: the same pick as scripts/mcp_record.py")
    ap.add_argument("--claude", default="claude")
    args = ap.parse_args(argv)

    corpus_dir = str(Path(args.corpus).resolve())
    corpus = corpus_mod.load(corpus_dir)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    pid, why = (args.posting_id, "given with --posting-id") if args.posting_id else mcp_record.pick_posting(corpus, cfg)
    stamp = mcp_record.utc("%Y-%m-%dT%H-%M-%SZ")
    stem = T / f"B-claude-code-{stamp}"
    log, conf = Path(str(stem) + ".jsonl"), Path(str(stem) + ".mcp-config.json")
    server_args = ["-I", str(PROJECT / "src" / "jsa3" / "mcp_server.py"), "--corpus", corpus_dir,
                   "--config", str(Path(args.config).resolve()), "--log", str(log)]
    conf.write_text(json.dumps({"mcpServers": {"jsa3": {"type": "stdio", "command": "python3", "args": server_args}}},
                               indent=2) + "\n", encoding="utf-8")
    version = subprocess.run([args.claude, "--version"], capture_output=True, text=True).stdout.strip()
    cmd = [args.claude, "-p", PROMPT.format(pid=pid), "--mcp-config", str(conf.relative_to(PROJECT)),
           "--strict-mcp-config", "--allowedTools", "mcp__jsa3__score_posting", "--tools", "",
           "--no-session-persistence", "--output-format", "json"]
    p = subprocess.run(cmd, cwd=str(PROJECT), capture_output=True, timeout=600)
    Path(str(stem) + ".client-output.json").write_bytes(p.stdout)
    Path(str(stem) + ".client-stderr.txt").write_bytes(p.stderr + f"\nexit={p.returncode}\n".encode())

    rows = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    sent = []
    tool = None
    for r in rows:
        if r["dir"] == "client->server":
            try:
                m = json.loads(r["raw"])
                sent.append(m.get("method", "(response)") + ("" if "id" in m else " (notification)"))
            except ValueError:
                sent.append("(unparseable)")
        elif r["dir"] == "server->client":
            try:
                sc = json.loads(r["raw"]).get("result", {}).get("structuredContent")
            except ValueError:
                sc = None
            if sc:
                tool = sc["record"]
    try:
        answer = json.loads(p.stdout.decode("utf-8")).get("result", "")
    except ValueError:
        answer = ""
    lines = [f"# Transcript {stem.name}", "",
             f"Recorded {stamp} by `scripts/mcp_record_b.py`. Real client: Claude Code `{version}`.", "",
             "Command (cwd = project root):", "", "```bash", shlex.join(cmd), "```", "",
             f"- Host config: `{conf.name}`; server stdio log: `{log.name}`",
             f"- Posting id: `{pid}` ({why}); corpus run `{corpus['run']}`",
             f"- SHA-256 of src/jsa3/mcp_server.py at record time: `{hashlib.sha256((PROJECT / 'src/jsa3/mcp_server.py').read_bytes()).hexdigest()}`",
             f"- Claude Code exit code: {p.returncode}",
             f"- Methods the client sent, in order: {', '.join(sent) or '(none: the server log is empty)'}",
             f"- Server log rows: {len(rows)}; last row: `{rows[-1]['dir'] if rows else '-'}`"]
    if tool:
        lines += [f"- Tool returned verdict `{tool['verdict']}`, reason `{tool['reason']}`",
                  f"- Mechanical string check (not a judgment of the answer): verdict appears verbatim in "
                  f"Claude's answer: **{tool['verdict'] in answer}**; reason appears verbatim: **{tool['reason'] in answer}**"]
    else:
        lines += ["- No tool result with structuredContent appears in the server log."]
    lines += ["", "Claude's final answer (the `result` field of the client output, verbatim):", "", "```text",
              answer or "(empty)", "```", ""]
    Path(str(stem) + ".md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {stem}.*  (claude exit {p.returncode}; tool called: {tool is not None})")
    return 0 if p.returncode == 0 and tool else 1


if __name__ == "__main__":
    sys.exit(main())
