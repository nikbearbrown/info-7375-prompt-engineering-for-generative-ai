"""Claude trials for the sampling report and the prompt experiment.

Every call is a fresh `claude -p` session: a new process, no tools, run
from a temporary directory so no project files or CLAUDE.md are loaded.
Every raw reply is saved with a UTC timestamp. A reply counts only if it
passes the validator; rejected replies are kept and counted as failures.

Usage:
    python3 tools/claude_trials.py sample
    python3 tools/claude_trials.py experiment --prompt baseline --split dev
    python3 tools/claude_trials.py experiment --prompt revision --split dev
    python3 tools/claude_trials.py experiment --prompt baseline --split heldout --final
    python3 tools/claude_trials.py experiment --prompt revision --split heldout --final
"""
import argparse
import csv
import html
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

RAW = Path("data/raw/20261031T143632Z_scaleai.json")
LABELS = Path("reports/prompt_experiment/labels.csv")
PROMPTS = Path("reports/prompt_experiment/prompts")
PE_DIR = Path("reports/prompt_experiment")
SAMPLE_DIR = Path("reports/sampling")
# 5 dev postings: the 1 relevant one plus 4 that fail different conditions.
SAMPLE_IDS = ["4730836005", "4674863005", "4665557005",
              "4694861005", "4536653005"]
RUNS_PER_POSTING = 4
KEYS = {"posting_id", "verdict", "resume_fields", "posting_fields", "reason"}
CMD = ["claude", "-p", "--output-format", "text", "--tools", ""]


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clean(text, limit=12000):
    text = html.unescape(html.unescape(text or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:limit]


def load_postings():
    jobs = json.loads(RAW.read_text(encoding="utf-8"))["jobs"]
    return {str(j["id"]): j for j in jobs}


def load_labels():
    with LABELS.open(newline="", encoding="utf-8") as f:
        return {r["posting_id"]: r for r in csv.DictReader(f)}


def build_prompt(template, job):
    location = (job.get("location") or {}).get("name", "")
    return (template.replace("<<POSTING_ID>>", str(job["id"]))
            .replace("<<TITLE>>", job["title"])
            .replace("<<LOCATION>>", location)
            .replace("<<CONTENT>>", clean(job.get("content"))))


def validate(reply, posting_id):
    try:
        obj = json.loads(reply.strip())
    except json.JSONDecodeError:
        return None, "not JSON (or extra text / code fences)"
    if not isinstance(obj, dict) or set(obj) != KEYS:
        return None, "wrong keys"
    if obj["posting_id"] != int(posting_id):
        return None, "posting_id mismatch"
    if obj["verdict"] not in ("relevant", "not_relevant"):
        return None, "unknown verdict"
    for key in ("resume_fields", "posting_fields"):
        value = obj[key]
        if not isinstance(value, list) or not value or not all(
                isinstance(x, str) and x for x in value):
            return None, f"empty or invalid {key}"
    if not isinstance(obj["reason"], str) or not obj["reason"].strip():
        return None, "empty reason"
    return obj, ""


def call_claude(prompt):
    started = now()
    try:
        out = subprocess.run(CMD, input=prompt, capture_output=True,
                             text=True, timeout=300,
                             cwd=tempfile.gettempdir())
        return started, out.stdout, out.returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        return started, f"<<call failed: {exc}>>", -1


def trial(task):
    kind, prompt_name, template, job, run = task
    started, reply, code = call_claude(build_prompt(template, job))
    if code == 0:
        obj, why = validate(reply, job["id"])
    else:
        obj, why = None, f"cli exit {code}"
    return {"kind": kind, "prompt": prompt_name,
            "posting_id": str(job["id"]), "title": job["title"],
            "run": run, "called_at_utc": started,
            "valid": obj is not None, "rejected_because": why,
            "verdict": obj["verdict"] if obj else None,
            "reason": obj["reason"] if obj else None,
            "raw_reply": reply}


def run_tasks(tasks):
    with ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(trial, tasks))


def write_outputs(stem, results, table_lines):
    jsonl, md = Path(f"{stem}.jsonl"), Path(f"{stem}.md")
    with jsonl.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    version = subprocess.run(["claude", "--version"], capture_output=True,
                             text=True).stdout.strip()
    header = [f"Generated {now()} by tools/claude_trials.py",
              f"Claude Code CLI: {version or 'unknown'}",
              "Each verdict is one fresh `claude -p` call (actual runs).", ""]
    md.write_text("\n".join(header + table_lines) + "\n", encoding="utf-8")
    print("\n".join(table_lines))
    print(f"\nsaved {jsonl} and {md}")


def cmd_sample():
    stem = SAMPLE_DIR / "trials"
    if Path(f"{stem}.jsonl").exists():
        raise SystemExit(f"{stem}.jsonl exists; refusing to overwrite")
    postings, labels = load_postings(), load_labels()
    template = (PROMPTS / "baseline.txt").read_text(encoding="utf-8")
    tasks = [("sample", "baseline", template, postings[pid], run)
             for pid in SAMPLE_IDS for run in range(1, RUNS_PER_POSTING + 1)]
    results = run_tasks(tasks)
    lines = ["| posting | hand label | verdicts, runs 1-4 | matches hand label |",
             "|---|---|---|---|"]
    for pid in SAMPLE_IDS:
        rs = sorted((r for r in results if r["posting_id"] == pid),
                    key=lambda r: r["run"])
        verdicts = [r["verdict"] or "rejected" for r in rs]
        hand = labels[pid]["label"]
        hits = sum(v == hand for v in verdicts)
        lines.append(f"| {pid} {postings[pid]['title']} | {hand} | "
                     f"{', '.join(verdicts)} | {hits}/{len(verdicts)} |")
    write_outputs(stem, results, lines)


def cmd_experiment(prompt_name, split, final):
    if split == "heldout" and not final:
        raise SystemExit("refusing to run the held-out set without --final")
    stem = PE_DIR / f"results_{prompt_name}_{split}"
    if Path(f"{stem}.jsonl").exists():
        raise SystemExit(f"{stem}.jsonl exists; refusing to overwrite")
    postings, labels = load_postings(), load_labels()
    template = (PROMPTS / f"{prompt_name}.txt").read_text(encoding="utf-8")
    ids = [pid for pid, r in labels.items() if r["split"] == split]
    results = run_tasks([("experiment", prompt_name, template,
                          postings[pid], 1) for pid in ids])
    for r in results:
        r["hand_label"] = labels[r["posting_id"]]["label"]
        r["pass"] = r["valid"] and r["verdict"] == r["hand_label"]
    passed = sum(r["pass"] for r in results)
    rejected = sum(not r["valid"] for r in results)
    lines = [f"**{prompt_name} on {split}: {passed}/{len(results)} match "
             f"hand labels; {rejected} rejected by validator**", "",
             "| posting | hand label | Claude verdict | match |",
             "|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['posting_id']} {r['title']} | {r['hand_label']} | "
                     f"{r['verdict'] or 'rejected: ' + r['rejected_because']} | "
                     f"{'yes' if r['pass'] else 'no'} |")
    write_outputs(stem, results, lines)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sample")
    exp = sub.add_parser("experiment")
    exp.add_argument("--prompt", choices=["baseline", "revision"],
                     required=True)
    exp.add_argument("--split", choices=["dev", "heldout"], required=True)
    exp.add_argument("--final", action="store_true")
    args = parser.parse_args()
    if args.cmd == "sample":
        cmd_sample()
    else:
        cmd_experiment(args.prompt, args.split, args.final)


if __name__ == "__main__":
    main()
