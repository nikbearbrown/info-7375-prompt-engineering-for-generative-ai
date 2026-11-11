"""Action-surface comparison data (brief Step 4.3, R27-R29): the same judgment, given to Claude three ways.

Why one script: the three surfaces differ only in what Claude is allowed to touch, so the question
(prompt v1 + one posting + Aarav's résumé and profile) is kept identical and only access changes:
  1. chat   — everything pasted as text, no tools (what pasting into a chat window gives Claude)
  2. file   — the same material as files in an empty folder, and only the Read tool
  3. agent  — the agent's own Run 2 verdict for the same posting (it fetched the board and wrote state)
Posting 8336819 is used because Run 2's agent judged it as a new posting, so all three exist.
Run: .venv/bin/python reports/action_surface.py   -> reports/action_surface/results.json
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_agent import inputs                    # noqa: E402
from job_agent.common.paths import Paths        # noqa: E402
from job_agent.judges import claude, claude_cli  # noqa: E402
from job_agent.judges.words import strip_html   # noqa: E402
from job_agent.watch.boards import greenhouse   # noqa: E402

POSTING = 8336819
RAW = ROOT / "evidence/raw/2026-10-31T225910Z/stripe_content.json"      # submitted Run 2 fetch
RUN2 = ROOT / "runs/2026-10-31T225910Z/verdicts.json"
OUT = ROOT / "reports" / "action_surface"


def cli(args: list[str], stdin: str, cwd: str) -> dict:
    """claude -p with the same isolation as the agent's judge (no settings, no MCP, no session), plus whatever tools args add."""
    env = {k: v for k, v in os.environ.items() if k not in claude_cli._DROP_ENV}
    exe = claude_cli.find_claude()
    base = [exe, "-p", "--model", claude.MODEL, "--no-session-persistence", "--setting-sources", "",
            "--strict-mcp-config", "--output-format", "json"]
    proc = subprocess.run(base + args, input=stdin, capture_output=True, text=True, cwd=cwd, env=env, timeout=300)
    out = json.loads(proc.stdout)
    return {"result": out.get("result"), "stop_reason": out.get("stop_reason"), "num_turns": out.get("num_turns"),
            "permission_denials": out.get("permission_denials"), "model": list(out.get("modelUsage") or {})}


def main() -> None:
    paths = Paths()
    criteria = inputs.load_criteria(paths.default_resume, paths.default_profile, paths)
    prompt = paths.prompt("claude_judge.v1").read_text()
    post = {p.id: p for p in greenhouse.parse(RAW.read_bytes())}[POSTING]
    results = {"posting_id": POSTING, "title": post.title, "prompt": "claude_judge.v1"}

    with tempfile.TemporaryDirectory(prefix="surface-chat-") as d:
        # 1. chat: the whole question pasted as text, no tools at all.
        results["chat"] = cli(["--tools", "", "--system-prompt", prompt], claude.user_message(post, criteria), d)

    with tempfile.TemporaryDirectory(prefix="surface-file-") as d:
        # 2. file: same material on disk; Claude may only Read, and only this folder exists for it.
        Path(d, "posting.txt").write_text(
            f"posting_id: {post.id}\ntitle: {post.title}\nlocation.name: {post.location}\n\n{strip_html(post.content).strip()}\n")
        Path(d, "resume.json").write_text(json.dumps(criteria.resume, ensure_ascii=False, indent=1))
        Path(d, "profile.json").write_text(json.dumps(criteria.profile, ensure_ascii=False, indent=1))
        ask = ("Read posting.txt, resume.json and profile.json in the current folder, then answer about that posting "
               "exactly as your instructions say.")
        results["file"] = cli(["--tools", "Read", "--allowedTools", "Read", "--system-prompt", prompt], ask, d)

    # 3. agent: what the agent itself produced in Run 2 for this posting.
    run2 = json.loads(RUN2.read_text())
    results["agent"] = [v for v in run2["verdicts"] if v["posting_id"] == POSTING]

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n")
    for k in ("chat", "file"):
        print(k, results[k]["stop_reason"], "turns", results[k]["num_turns"], "|", (results[k]["result"] or "")[:200].replace("\n", " "))
    print("agent", [(v["judge"], v["verdict"]) for v in results["agent"]])


if __name__ == "__main__":
    main()
