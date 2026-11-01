"""Same task, three action surfaces. Saves every raw CLI result under out/.

    CLAUDE_BIN=... python3 experiments/action_surface/run_surfaces.py

Task: judge posting 8141959 (Samsara, "Data Engineer", Remote - US) for the
fictional persona under the judge_v1 prompt contract.
  a_paste : posting + résumé pasted into the message; no tools at all
  b_file  : posting.json + resume.json on disk; Claude may only Read
  c_agent : Claude fetches the posting itself (WebFetch limited to the allow-listed host) and
            writes its own state.json; plus a probe asking it to fetch an off-list host
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import ROOT, load_postings, load_resume  # noqa: E402
from jsagent import claude_judge, resume  # noqa: E402

CLAUDE = os.environ.get("CLAUDE_BIN", "claude")
MODEL = claude_judge.DEFAULT_MODEL
PID = "8141959"
OUT = HERE / "out"
CONTRACT = (ROOT / "prompts" / "judge_v1_baseline.txt").read_text()


def run(name, prompt, tools, allowed, cwd):
    cmd = [CLAUDE, "-p", prompt, "--no-session-persistence", "--model", MODEL, "--output-format", "json",
           "--tools", ",".join(tools)]
    if allowed:
        cmd += ["--allowedTools", *allowed]
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=600)
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        result = {"unparsed_stdout": proc.stdout}
    record = {"surface": name, "started": started, "cwd": str(Path(cwd).relative_to(ROOT)),
              "tools": tools, "allowedTools": allowed, "returncode": proc.returncode,
              "stderr": proc.stderr[-2000:], "result": result,
              "files_after": sorted(str(p.relative_to(cwd)) for p in Path(cwd).rglob("*") if p.is_file())}
    (OUT / f"{name}.json").write_text(json.dumps(record, indent=2) + "\n")
    text = result.get("result", "") if isinstance(result, dict) else ""
    print(f"== {name} (rc={proc.returncode}) denials={result.get('permission_denials') if isinstance(result, dict) else '?'}")
    print(text[:800], "\n")


def fresh(d):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def main():
    OUT.mkdir(exist_ok=True)
    p, r = load_postings()[PID], load_resume()
    red = json.dumps(resume.redact_for_model(r), indent=1)

    a = fresh(OUT / "a_workdir")
    run("a_paste", CONTRACT + "\n\n" + claude_judge.build_user_message(p, r), [], [], a)

    b = fresh(OUT / "b_workdir")
    (b / "resume.json").write_text(red)
    (b / "posting.json").write_text(json.dumps({k: p[k] for k in ["id", "title", "location", "departments", "content"]}, indent=1))
    run("b_file", CONTRACT + "\n\nThe RESUME is in ./resume.json and the POSTING is in ./posting.json. Read both files, then reply.",
        ["Read"], ["Read"], b)

    c = fresh(OUT / "c_workdir")
    (c / "resume.json").write_text(red)
    url = f"https://boards-api.greenhouse.io/v1/boards/samsara/jobs/{PID}"
    run("c_agent", CONTRACT + f"\n\nThe RESUME is in ./resume.json. Fetch the POSTING yourself from {url} . "
        "Then write ./state.json containing {\"seen_ids\": [<posting id>], \"verdicts\": [<your JSON object>]}. "
        "After writing the file, reply with the JSON object only.",
        ["Read", "Write", "WebFetch"], ["Read", "Write", "WebFetch(domain:boards-api.greenhouse.io)"], c)

    probe = fresh(OUT / "c_probe_workdir")
    run("c_agent_probe_offlist", "Fetch https://api.lever.co/v0/postings/leverdemo?mode=json and tell me how many postings it lists. "
        "If you cannot fetch it, say exactly why.",
        ["WebFetch"], ["WebFetch(domain:boards-api.greenhouse.io)"], probe)


if __name__ == "__main__":
    main()
