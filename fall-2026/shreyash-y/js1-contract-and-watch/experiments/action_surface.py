"""The same task done three ways, each run once, live, through `claude -p` (Chapter 3).
Each way runs in its own empty temporary folder (so no project files or memory reach it); the
full event stream and every file the model was given or wrote are copied back here as evidence.

  A  chat paste : the rule, resume and one posting pasted into the message; no tools.
  B  file read  : the same three things as files; the Read tool only.
  C  agent      : the agent fetches the board itself and writes its own state file; Read, Write
                  and curl to the board host only.
  PYTHONPATH=. python3 experiments/action_surface.py A|B|C|C2   (C was saved as way-C-attempt1)
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

from jsagent import claude_judge, persona, posting

HERE = pathlib.Path("experiments/action-surface")
PID = 6555819  # Staff Software Engineer, Backend: the hybrid-ad case from the dev set
mode = sys.argv[1]
# C2 = way C, attempt 2: the same task with curl allowed to ANY host (attempt 1's host-pinned
# pattern refused every real curl command the agent wrote).
wide = mode == "C2"
mode = "C" if wide else mode
system, user_tpl, _ = claude_judge.load_prompt("prompts/baseline-v1.md")
view = persona.public_view(persona.load("persona/alex_morgan.json"))
raw1 = json.loads(pathlib.Path("runs/raw/oscar-20261029T031015Z.json").read_bytes())
p = posting.normalize(next(j for j in raw1["jobs"] if j["id"] == PID), "oscar")
state_after_run2 = json.loads(pathlib.Path("runs/state.json").read_text())["boards"]["oscar"]

base = ["claude", "-p", "--model", "opus", "--no-session-persistence", "--strict-mcp-config",
        "--setting-sources", "", "--output-format", "stream-json", "--verbose"]
with tempfile.TemporaryDirectory(prefix=f"js1-surface-{mode}-") as tmp:
    work = pathlib.Path(tmp)
    if mode == "A":
        _, msg, _ = claude_judge.build("prompts/baseline-v1.md", view, p)
        cmd = base + ["--tools", "", "--system-prompt", system]
    elif mode == "B":
        (work / "rule.md").write_text(system + "\n")
        (work / "resume.json").write_text(json.dumps(view, indent=1) + "\n")
        (work / "posting.json").write_text(json.dumps(claude_judge.posting_for_model(p), indent=1) + "\n")
        msg = ("Read rule.md, resume.json and posting.json in the current folder. Apply the rule in "
               "rule.md to the posting and reply in the output format rule.md gives.")
        cmd = base + ["--tools", "Read", "--allowedTools", "Read"]
    elif mode == "C":
        (work / "rule.md").write_text(system + "\n")
        (work / "resume.json").write_text(json.dumps(view, indent=1) + "\n")
        (work / "state.json").write_text(json.dumps({"board": "oscar", "seen_ids": state_after_run2["seen_ids"]}) + "\n")
        msg = ("You are a job-board watcher. Fetch https://boards-api.greenhouse.io/v1/boards/oscar/jobs "
               "with curl. Compare its posting ids with seen_ids in state.json. Add any new ids to "
               "state.json. For each new posting, apply the rule in rule.md against resume.json and "
               "write the answers, in rule.md's output format, as a JSON list in verdicts.json. "
               "Use no host other than boards-api.greenhouse.io.")
        cmd = base + ["--tools", "Bash,Read,Write", "--allowedTools", "Read", "Write",
                      "Bash(curl *)" if wide else "Bash(curl -s https://boards-api.greenhouse.io/*)"]
    given = sorted(f.name for f in work.iterdir())
    proc = subprocess.run(cmd, input=msg, capture_output=True, text=True, timeout=900, cwd=work)
    out = HERE / ("way-C-attempt2" if wide else f"way-{mode}")
    if out.exists():
        shutil.rmtree(out)
    (out / "folder-after").mkdir(parents=True)
    for f in work.iterdir():
        if f.is_file():
            shutil.copy(f, out / "folder-after" / f.name)
(out / "message.txt").write_text(msg + "\n")
(out / "command.json").write_text(json.dumps({"cmd": [c if c != system else "<prompts/baseline-v1.md system part>" for c in cmd],
                                             "files_given": given, "returncode": proc.returncode}, indent=1) + "\n")
(out / "events.jsonl").write_text(proc.stdout)
events = [json.loads(l) for l in proc.stdout.splitlines() if l.strip().startswith("{")]
for e in events:
    if e.get("type") == "assistant":
        for c in e["message"]["content"]:
            if c.get("type") == "tool_use":
                print("TOOL_USE", c["name"], json.dumps(c["input"])[:200])
    if e.get("type") == "user":
        for c in e["message"].get("content", []):
            if isinstance(c, dict) and c.get("type") == "tool_result":
                t = c.get("content"); t = t if isinstance(t, str) else json.dumps(t)
                print("TOOL_RESULT", ("ERROR " if c.get("is_error") else "") + t[:160].replace("\n", " "))
    if e.get("type") == "result":
        print("RESULT", e.get("subtype"), "turns", e.get("num_turns"), "cost", e.get("total_cost_usd"))
        print(str(e.get("result"))[:700])
print("files after:", sorted(f.name for f in (out / "folder-after").iterdir()))
