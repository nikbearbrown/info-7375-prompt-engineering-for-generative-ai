"""Replay the client->server lines of a recorded transcript into another stdio server, and record both ways.

    python3 -I scripts/mcp_replay.py --from transcripts/B-claude-code-<UTC>.jsonl \\
        --server-cmd "python3 -I other-server/main.py --stdio" --name C2-teaching-server-replay-of-B

Used to ask: would the teaching server have survived Claude Code's real handshake? The replayed lines are
Claude Code's recorded bytes, re-sent by this script (a replay, not a live Claude Code session); the
server's replies are new and real. Writes transcripts/<name>-<UTC>.jsonl and .md. No network.
"""
from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
import mcp_record  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--server-cmd", required=True)
    ap.add_argument("--name", required=True)
    args = ap.parse_args(argv)
    src = Path(args.src)
    sent = [json.loads(x)["raw"] for x in src.read_text(encoding="utf-8").splitlines()
            if json.loads(x)["dir"] == "client->server"]
    cmd = shlex.split(args.server_cmd)
    stamp = mcp_record.utc("%Y-%m-%dT%H-%M-%SZ")
    stem = mcp_record.TRANSCRIPTS / f"{args.name}-{stamp}"
    pipe = mcp_record.Pipe(cmd)
    rows = [{"ts": mcp_record.utc(), "dir": "meta", "raw": None,
             "note": f"replay of client->server lines from {src.name}; server: {shlex.join(cmd)}"}]
    table = []
    for i, line in enumerate(sent, 1):
        rows.append({"ts": mcp_record.utc(), "dir": "client->server", "raw": line, "step": i})
        pipe.send(line)
        got = pipe.collect(3.0 if '"id"' in line else 0.8, 0.15)
        rows += [{"ts": ts, "dir": "server->client", "raw": r, "step": i} for ts, r in got]
        try:
            m = json.loads(line)
            what = m.get("method", "?") + ("" if "id" in m else " (notification)")
        except ValueError:
            what = "(unparseable)"
        obs = []
        for _, r in got:
            o = json.loads(r)
            obs.append(f"error {o['error']['code']}: {o['error'].get('message')}" if "error" in o else
                       "result" + (" isError " + str(o["result"].get("isError")).lower() if "isError" in o["result"] else ""))
        table.append((i, what, "; ".join(obs) or "no reply"))
    code = pipe.close()
    rows.append({"ts": mcp_record.utc(), "dir": "meta", "raw": None, "note": f"stdin closed; server exit code {code}"})
    with open(str(stem) + ".jsonl", "x", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    md = [f"# {stem.name}", "", f"Recorded {stamp} by `scripts/mcp_replay.py`: the {len(sent)} client->server lines of "
          f"`{src.name}` (Claude Code's real bytes) re-sent by a script to `{shlex.join(cmd)}`. A replay, not a live "
          f"Claude Code session. Server exit code {code}. Raw lines: `{stem.name}.jsonl`.", "",
          "| # | Replayed message | Server reply |", "|---|---|---|"]
    md += [f"| {i} | {w} | {o} |" for i, w, o in table]
    md += ["", "Server stderr (verbatim):", "", "```text", pipe.stderr.decode("utf-8", "replace").rstrip() or "(empty)", "```", ""]
    Path(str(stem) + ".md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {stem}.jsonl/.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
