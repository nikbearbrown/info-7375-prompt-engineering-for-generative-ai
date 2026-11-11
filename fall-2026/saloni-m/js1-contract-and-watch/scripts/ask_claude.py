"""Ask Claude (fresh `claude -p` conversation per call) about experiment postings; append every call.

    python3 scripts/ask_claude.py sampling --repeats 4              # first 5 dev postings x 4, v1 prompt
    python3 scripts/ask_claude.py experiment --split dev --prompt prompts/v1_baseline.md
    python3 scripts/ask_claude.py experiment --split heldout --prompt prompts/v2_revision.md

Every call (including validator rejections) is appended to results/<mode>/calls.jsonl with its
UTC time, the CLI session id, the raw text Claude returned, and the validator status.
"""
import argparse
import datetime as dt
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, ".")
from agent.claude_judge import judge_claude  # noqa: E402
from agent.resume import load_resume  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["sampling", "experiment"])
ap.add_argument("--split", default="dev")
ap.add_argument("--prompt", default="prompts/v1_baseline.md")
ap.add_argument("--repeats", type=int, default=1)
ap.add_argument("--workers", type=int, default=4)
args = ap.parse_args()

resume = load_resume("personas/priya-nair.resume.json")
spec = json.load(open("labels/experiment_set.json", encoding="utf-8"))
jobs = {j["id"]: j for j in json.load(open(spec["source"], encoding="utf-8"))["jobs"]}
chosen = [p for p in spec["postings"] if p["split"] == ("dev" if args.mode == "sampling" else args.split)]
if args.mode == "sampling":
    chosen = chosen[:5]
tasks = [(p, k) for p in chosen for k in range(args.repeats)]


def one(task):
    p, k = task
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    try:
        out = judge_claude(jobs[p["id"]], resume, prompt_path=args.prompt)
    except Exception as e:  # CLI/auth/timeouts are recorded, never silently retried
        out = {"id": p["id"], "kind": "judgment", "prompt": args.prompt, "status": "error", "error": str(e)}
    out.update({"repeat": k, "split": p["split"], "title": p["title"], "asked_at": started})
    return out


os.makedirs(f"results/{args.mode}", exist_ok=True)
log = f"results/{args.mode}/calls.jsonl"
with ThreadPoolExecutor(args.workers) as pool, open(log, "a", encoding="utf-8") as f:
    for out in pool.map(one, tasks):
        f.write(json.dumps(out) + "\n")
        f.flush()
        print(out["status"], out.get("verdict", out.get("error", ""))[:80], "|", out["title"][:50])
print(f"appended {len(tasks)} calls to {log}")
