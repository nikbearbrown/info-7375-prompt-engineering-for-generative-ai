"""Action-surface modes 2 and 3 (Chapter 3), run for real with the Claude Code CLI.

Mode 2: Claude may only READ two local files (posting + résumé skills) in an empty temp dir.
Mode 3: Claude may FETCH the posting itself (WebFetch limited to boards-api.greenhouse.io) and
        WRITE its own state file in the temp dir.
Mode 1 (paste into chat) is performed by hand in claude.ai; see action_surface/mode1_*.

The event streams are saved with the CLI's init event reduced to tools/model/permission fields
(the full init block carries local environment details).
"""
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import judge  # noqa: E402
from agent.resume import load_resume  # noqa: E402
from agent.rules import resume_skill_entries  # noqa: E402

POSTING_ID = 6865698002
URL = f"https://boards-api.greenhouse.io/v1/boards/databricks/jobs/{POSTING_ID}?content=true"
OUT = ROOT / "action_surface"
COMMON = ["--model", judge.MODEL, "--effort", judge.EFFORT, "--strict-mcp-config", "--setting-sources", "",
          "--disable-slash-commands", "--no-session-persistence", "--output-format", "stream-json", "--verbose"]


def run(mode, tools, allowed, task, files):
    work = Path(tempfile.mkdtemp(prefix=f"js1-{mode}-"))
    for name, content in files.items():
        (work / name).write_text(content)
    system, sha = judge.load_prompt("v1")
    argv = ["claude", "-p", "--tools", ",".join(tools), "--allowedTools", *allowed, *COMMON,
            "--system-prompt", system]
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    proc = subprocess.run(argv, input=task, capture_output=True, text=True, timeout=600, cwd=work)
    events = []
    for line in proc.stdout.splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "system" and e.get("subtype") == "init":
            e = {k: e.get(k) for k in ("type", "subtype", "tools", "model", "permissionMode", "mcp_servers")}
        events.append(e)
    written = {p.name: p.read_text() for p in work.iterdir() if p.name not in files}
    shutil.rmtree(work, ignore_errors=True)
    rec = {"mode": mode, "started_at_utc": started, "tools_enabled": tools, "allowed_rules": allowed,
           "prompt_version": "v1", "prompt_sha256": sha, "task": task, "input_files": sorted(files),
           "returncode": proc.returncode, "files_created_by_claude": written, "events": events,
           "stderr_tail": proc.stderr[-2000:]}
    (OUT / f"{mode}_run.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False))
    tool_calls = [c for e in events if e.get("type") == "assistant"
                  for c in (e.get("message") or {}).get("content", []) if c.get("type") == "tool_use"]
    final = next((e.get("result") for e in reversed(events) if e.get("type") == "result"), None)
    print(f"== {mode}: rc={proc.returncode} tool calls={[(c['name'], c['input']) for c in tool_calls]}")
    print("files created:", list(written))
    print("final:", (final or "")[:800])


def main():
    resume = load_resume(ROOT / "resume/priya-nair.resume.example.json")
    dev = {p["id"]: p for p in json.loads((ROOT / "experiments/sample/dev_postings.json").read_text())}
    skills = json.dumps(resume_skill_entries(resume), indent=1)
    which = sys.argv[1:] or ["mode2_file", "mode3_agent"]
    if "mode2_file" in which:
        run("mode2_file", ["Read"], ["Read"],
            "Read ./posting.json (a Greenhouse posting object; the description is in the HTML-escaped "
            "`content` field) and ./resume_skills.json, apply the rule, and reply with the JSON object only.",
            {"posting.json": json.dumps(dev[POSTING_ID], ensure_ascii=False), "resume_skills.json": skills})
    if "mode3_agent" in which:
        run("mode3_agent", ["WebFetch", "Read", "Write"],
            ["WebFetch(domain:boards-api.greenhouse.io)", "Read", "Write"],
            f"Fetch the posting at {URL} yourself, read ./resume_skills.json, apply the rule, then write "
            "./state.json recording the posting id as seen together with your JSON judgment. "
            "Finally reply with the JSON judgment object only.",
            {"resume_skills.json": skills})


if __name__ == "__main__":
    main()
