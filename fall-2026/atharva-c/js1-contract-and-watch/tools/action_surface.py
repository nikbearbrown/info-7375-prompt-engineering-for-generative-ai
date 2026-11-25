"""Action-surface comparison (Chapter 3): the same task, posting 7776179, three ways.

  1. chat   — the posting text pasted into the prompt; no tools at all.
  2. file   — Claude is given one file to read (Read tool only), in a folder
              holding nothing else.
  3. agent  — Claude fetches the posting itself (WebFetch, limited to
              boards-api.greenhouse.io by permission rule) and writes its own
              state file (Write tool), in an empty scratch folder.

Each runs as a fresh `claude -p` session. What each session actually did is
read back from its stream-json transcript and saved to logs/action_surface/.

    python3 -m tools.action_surface
"""
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agent import claude_judge, resume

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "runs" / "2026-10-30T063746Z" / "raw.json"
PID = "7776179"
OUT = ROOT / "logs" / "action_surface"
FORMAT = Path(ROOT / "prompts" / "revision.txt").read_text().split("Question:")[1]


def run(mode, prompt, cwd, tools, allowed):
    cmd = ["claude", "-p", prompt, "--model", claude_judge.MODEL, "--tools", tools, "--strict-mcp-config",
           "--no-session-persistence", "--output-format", "stream-json", "--verbose"]
    if allowed:
        cmd += ["--allowedTools", *allowed]
    when = datetime.now(timezone.utc).isoformat(timespec="seconds")
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600)
    events = [json.loads(l) for l in proc.stdout.splitlines() if l.strip().startswith("{")]
    tool_calls = [{"tool": c["name"], "input": c["input"]}
                  for e in events if e.get("type") == "assistant"
                  for c in e["message"]["content"] if c.get("type") == "tool_use"]
    final = next((e for e in reversed(events) if e.get("type") == "result"), {})
    files_after = sorted(str(p.relative_to(cwd)) for p in Path(cwd).rglob("*") if p.is_file())
    rec = {"mode": mode, "at": when, "model": claude_judge.MODEL, "tools_available": tools,
           "allowed_rules": allowed, "tool_calls": tool_calls, "files_in_folder_after": files_after,
           "permission_denials": final.get("permission_denials"), "result": final.get("result"),
           "is_error": final.get("is_error")}
    try:
        rec["validated"] = claude_judge.validate(final.get("result") or "")
    except claude_judge.InvalidOutput as e:
        rec["validated"] = None
        rec["rejected_because"] = str(e)
    return rec


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    job = next(j for j in json.loads(RAW.read_text())["jobs"] if str(j["id"]) == PID)
    r = resume.load(ROOT / "examples" / "rohan-desai.resume.example.json")
    chat_prompt = claude_judge.build_prompt((ROOT / "prompts" / "revision.txt").read_text(), job, r)
    seeker = chat_prompt.split("Posting:")[0]
    results = []

    with tempfile.TemporaryDirectory() as d:
        results.append(run("1 chat", chat_prompt, d, "", []))

    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "posting.txt").write_text((ROOT / "labels" / "postings" / f"{PID}.txt").read_text())
        prompt = (seeker + "The posting is in the file posting.txt in the current folder. Read it.\n\n"
                  "Question:" + FORMAT)
        results.append(run("2 file", prompt, d, "Read", ["Read"]))

    with tempfile.TemporaryDirectory() as d:
        url = f"https://boards-api.greenhouse.io/v1/boards/stripe/jobs/{PID}"
        prompt = (seeker + f"Fetch the posting yourself from {url} . Then write a file state.json in the "
                  "current folder recording the posting id you judged and your verdict. "
                  "Finally, as your last message,\n\nQuestion:" + FORMAT)
        rec = run("3 agent", prompt, d, "WebFetch,Write,Read",
                  ["WebFetch(domain:boards-api.greenhouse.io)", "Write", "Read"])
        if (Path(d) / "state.json").exists():
            shutil.copy(Path(d) / "state.json", OUT / "agent_state.json")
        results.append(rec)

    (OUT / "runs.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    for x in results:
        v = x["validated"]["verdict"] if x["validated"] else f"INVALID ({x.get('rejected_because')})"
        print(f"{x['mode']}: {v}; tool calls: {[c['tool'] for c in x['tool_calls']]}; "
              f"denials: {x['permission_denials']}; files after: {x['files_in_folder_after']}")


if __name__ == "__main__":
    main()
