"""Chapter 3: the same task done three ways, each in a fresh scratch folder.

    python3 action-surface/run_three_ways.py POSTING_ID RAW_RESPONSE.json

1 paste:  claude -p, no tools; the posting and résumé are pasted into the prompt.
2 file:   claude -p --tools Read; posting.json + resume.json are in its cwd.
3 agent:  claude -p --tools WebFetch,Read,Write; it fetches the board itself and keeps
          its own state.json. WebFetch is allowed only for boards-api.greenhouse.io.
Everything Claude returns, and every file it leaves behind, is saved under action-surface/runs/."""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from jsagent import claude_judge, persona  # noqa: E402

OUT = os.path.join(ROOT, "action-surface", "runs")
BASE = ["claude", "-p", "--model", "sonnet", "--output-format", "json", "--setting-sources", "",
        "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence"]
CONTRACT = open(os.path.join(ROOT, "prompts", "baseline.txt"), encoding="utf-8").read()
FORMAT = CONTRACT[CONTRACT.index("OUTPUT CONTRACT."):]


def run(name, extra, prompt, files):
    d = tempfile.mkdtemp(prefix=f"surface-{name}-")
    for fn, obj in files.items():
        with open(os.path.join(d, fn), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1)
    before = set(os.listdir(d))
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    p = subprocess.run(BASE + extra, input=prompt, capture_output=True, text=True, cwd=d, timeout=900)
    env = json.loads(p.stdout) if p.stdout.strip().startswith("{") else {"stdout": p.stdout, "stderr": p.stderr}
    dest = os.path.join(OUT, name)
    os.makedirs(dest, exist_ok=True)
    left = sorted(set(os.listdir(d)) - before)
    for fn in left:
        shutil.copy(os.path.join(d, fn), os.path.join(dest, "left-behind-" + fn))
    with open(os.path.join(dest, "envelope.json"), "w", encoding="utf-8") as f:
        json.dump({"asked_at": at, "cmd": BASE + extra, "files_given": sorted(files),
                   "files_left_behind": left, "envelope": env}, f, indent=1)
    shutil.rmtree(d)
    return at, env, left


def main(pid, raw):
    with open(raw, encoding="utf-8") as f:
        posting = {str(j["id"]): j for j in json.load(f)["jobs"]}[pid]
    resume = persona.load(os.path.join(ROOT, "persona", "aarav-patel.example.json"))
    shown_resume = persona.for_model(resume)
    shown_posting = claude_judge.posting_for_model(posting)
    rows = []

    # 1. paste: exactly the agent's own prompt contract, no tools
    at, env, left = run("1-paste", ["--tools", ""], claude_judge.build_prompt(CONTRACT, posting, resume), {})
    rows.append(("1-paste", at, env, left))

    # 2. file: same task, but Claude must open the files itself
    p2 = ("Read resume.json and posting.json in the current directory. Decide whether the posting is "
          "relevant for this candidate: is it a job they should spend time applying to?\n\n"
          + FORMAT.replace("{{POSTING_ID}}", pid))
    at, env, left = run("2-file", ["--tools", "Read", "--allowedTools", "Read"], p2,
                        {"resume.json": shown_resume, "posting.json": shown_posting})
    rows.append(("2-file", at, env, left))

    # 3. agent: fetches the board itself and writes its own state file
    p3 = ("You are a job-board watcher. Fetch https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs . "
          "Keep a state file state.json in the current directory listing every posting id you have seen "
          "(create it if it does not exist; this is the first run). Then judge posting " + pid +
          " for the candidate in resume.json. Your final reply must follow this contract.\n\n"
          + FORMAT.replace("{{POSTING_ID}}", pid))
    at, env, left = run("3-agent", ["--tools", "WebFetch,Read,Write",
                                    "--allowedTools", "WebFetch(domain:boards-api.greenhouse.io)", "Read", "Write"],
                        p3, {"resume.json": shown_resume})
    rows.append(("3-agent", at, env, left))

    for name, at, env, left in rows:
        parsed, why = claude_judge.validate(env.get("result", ""), pid)
        print(json.dumps({"surface": name, "asked_at": at, "is_error": env.get("is_error"),
                          "turns": env.get("num_turns"), "cost_usd": env.get("total_cost_usd"),
                          "models": sorted((env.get("modelUsage") or {}).keys()),
                          "valid": parsed is not None, "verdict": parsed and parsed["verdict"],
                          "rejection": why, "files_left_behind": left}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
