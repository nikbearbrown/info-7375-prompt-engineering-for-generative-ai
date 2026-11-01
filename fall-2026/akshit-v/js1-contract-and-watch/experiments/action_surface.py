"""Action-surface comparison (Chapter 3): the same task three ways, each a real Claude Code CLI run.

  1. paste:  posting + résumé pasted into the prompt; no tools.
  2. file:   posting + résumé saved as files; Claude may only Read files.
  3. agent:  Claude may WebFetch the board (allow-listed domain only) and Write its own state file.

Each run happens in its own temporary sandbox folder. Outputs, and any file Claude wrote, are saved to
experiments/results/action_surface_<stamp>.json.

    python experiments/action_surface.py --id 6233040004
"""
import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.claude_judge import claude_executable, render_user_prompt, resume_for_claude  # noqa: E402
from agent.config import CLAUDE_MODEL, ROOT, board_url  # noqa: E402
from agent.postings import load_postings  # noqa: E402
from agent.resume import load_resume  # noqa: E402

RAW = ROOT / "evidence" / "raw" / "20261031T233955Z_figma_live.json"
TASK = ("Decide whether this posting is relevant to the job seeker (relevant or not_relevant), "
        "naming the résumé fields and posting fields behind your verdict. Location and sponsorship are out of scope.")


def run_claude(prompt: str, cwd: Path, tools: list[str], allowed: list[str]) -> dict:
    cmd = [claude_executable(), "-p", "--safe-mode", "--no-session-persistence", "--model", CLAUDE_MODEL,
           "--output-format", "json", "--tools", ",".join(tools) if tools else ""]
    if allowed:
        cmd += ["--allowedTools", *allowed]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                          timeout=600, cwd=cwd)
    try:
        env = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"exit": proc.returncode, "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]}
    files = {p.name: p.read_text(encoding="utf-8", errors="replace")[:4000]
             for p in cwd.iterdir() if p.is_file()}
    return {"exit": proc.returncode, "result": env.get("result"), "is_error": env.get("is_error"),
            "num_turns": env.get("num_turns"), "permission_denials": env.get("permission_denials"),
            "files_in_sandbox_after": files}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", type=int, required=True)
    args = ap.parse_args()
    resume = resume_for_claude(load_resume(ROOT / "data" / "resume_jack_spencer.json"))
    posting = {p["id"]: p for p in load_postings(RAW)}[args.id]
    results = {"run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "model": CLAUDE_MODEL, "posting_id": args.id, "task": TASK}

    with tempfile.TemporaryDirectory() as d:
        results["1_paste"] = run_claude(TASK + "\n\n" + render_user_prompt(posting, resume), Path(d), [], [])

    with tempfile.TemporaryDirectory() as d:
        Path(d, "posting.txt").write_text(render_user_prompt(posting, resume).split("POSTING:\n", 1)[1], encoding="utf-8")
        Path(d, "resume.json").write_text(json.dumps(resume, indent=2), encoding="utf-8")
        results["2_file"] = run_claude(TASK + " The posting is in posting.txt and the résumé in resume.json "
                                       "in the current folder.", Path(d), ["Read"], ["Read"])

    with tempfile.TemporaryDirectory() as d:
        Path(d, "resume.json").write_text(json.dumps(resume, indent=2), encoding="utf-8")
        results["3_agent"] = run_claude(
            f"Fetch {board_url('figma')} . Find the posting with id {args.id}. {TASK} The résumé is in resume.json. "
            "Then write state.json in the current folder listing every posting id on the board, so a later run "
            "can tell which postings are new.",
            Path(d), ["Read", "WebFetch", "Write"],
            ["Read", "Write", "WebFetch(domain:boards-api.greenhouse.io)"])

    out = Path(__file__).resolve().parent / "results" / f"action_surface_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for k in ("1_paste", "2_file", "3_agent"):
        r = results[k]
        print(f"== {k}: exit={r.get('exit')} turns={r.get('num_turns')} denials={r.get('permission_denials')}")
        print(f"   files after: {list((r.get('files_in_sandbox_after') or {}).keys())}")
        print("   " + str(r.get("result") or r.get("stderr"))[:600].replace("\n", "\n   "))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
