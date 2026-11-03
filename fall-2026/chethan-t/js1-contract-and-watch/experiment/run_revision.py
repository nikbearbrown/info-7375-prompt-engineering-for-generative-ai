"""Revision-prompt experiment. Appends results to experiment/PROMPT_EXPERIMENT.md.

Run from the project folder, one mode at a time:
    python3 experiment/run_revision.py --dev       # revision prompt, 10 dev postings (10 calls)
    python3 experiment/run_revision.py --heldout   # baseline AND revision, 10 heldout postings (20 calls)

Same rules as run_dev.py: postings from raw/klaviyo_20261031T175121.json only,
labels.csv read only, every claude -p call from a fresh neutral folder, every
raw reply saved, an invalid reply counts as a fail.

--heldout refuses to run unless prompts/revision.txt and prompts/baseline.txt
are committed and unchanged since, and runs only once: it refuses if
PROMPT_EXPERIMENT.md already has a heldout section.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

EXP = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP))

from run_dev import (  # noqa: E402
    CONCLUSION, INVALID, PROJECT, PROMPT_REPORT, cell, load_labels, load_postings, prompt_info,
)
from agent import claude_judge  # noqa: E402
from agent.resume import load_resume  # noqa: E402

PROMPTS = {
    "baseline": PROJECT / "prompts" / "baseline.txt",
    "revision": PROJECT / "prompts" / "revision.txt",
}
RAW_ROOT = EXP / "prompt_experiment" / "raw"
HELDOUT_MARK = "<!-- heldout run -->"


# ---- Checks ----

def git(*args):
    return subprocess.run(["git", *args], cwd=PROJECT, capture_output=True, text=True)


def check_committed(path):
    """Stop unless path is committed with no changes since; return its last commit hash."""
    rel = str(path.relative_to(PROJECT))
    if git("ls-files", "--error-unmatch", rel).returncode != 0:
        sys.exit(f"{rel} is not committed; commit it before the heldout run. Nothing was run.")
    if git("diff", "--quiet", "HEAD", "--", rel).returncode != 0:
        sys.exit(f"{rel} has changed since its last commit; commit or revert it first. Nothing was run.")
    return git("log", "-1", "--format=%h", "--", rel).stdout.strip()


def check_heldout_not_run():
    if PROMPT_REPORT.exists() and HELDOUT_MARK in PROMPT_REPORT.read_text():
        sys.exit(f"{PROMPT_REPORT.name} already has a heldout run; heldout is used once. Nothing was run.")


# ---- Claude calls ----

def ask(prompt_name, row, posting, resume, raw_dir, label, allowed_set):
    assert row["set"] == allowed_set, f"{row['set']} row sent in a {allowed_set} run"
    claude_judge.PROMPT_PATH = PROMPTS[prompt_name]
    claude_judge.RESPONSES_DIR = raw_dir
    start = time.monotonic()
    j = claude_judge.judge(posting, resume)
    outcome = j["verdict"] if j["status"] == "ok" else INVALID
    raw = str((raw_dir.parent / j["raw_file"]).relative_to(EXP)) if j.get("raw_file") else "—"
    note = "" if outcome != INVALID else f"  [{j['status']}{': ' + j['error'] if j.get('error') else ''}]"
    print(f"  {label} [{prompt_name}]: {outcome} ({time.monotonic() - start:.1f}s){note}", flush=True)
    return {
        "outcome": outcome,
        "status": j["status"],
        "reason": j.get("reason") or j.get("error") or "",
        "raw": raw,
        "pass": outcome == row["my_label"],
    }


def run(set_name, prompt_names, rows, postings, resume):
    """One call per posting per prompt; prompts interleaved per posting."""
    chosen = [r for r in rows if r["set"] == set_name]
    print(f"{set_name}: {len(chosen)} postings x {len(prompt_names)} prompt(s)", flush=True)
    results = []
    for i, row in enumerate(chosen, start=1):
        per_prompt = {
            name: ask(name, row, postings[row["id"]], resume, RAW_ROOT / f"{name}_{set_name}",
                      f"posting {i}/{len(chosen)} (id {row['id']})", set_name)
            for name in prompt_names
        }
        results.append((row, per_prompt))
    return results


# ---- Report ----

def section(set_name, prompt_names, results, started, commits):
    n = len(results)
    title = f"## Revision experiment: {set_name} ({', '.join(prompt_names)})"
    lines = [title, ""]
    if set_name == "heldout":
        lines += [HELDOUT_MARK, ""]
    lines += [f"Date: {started}  "]
    for name in prompt_names:
        claude_judge.PROMPT_PATH = PROMPTS[name]
        commit = f", commit {commits[name]}" if commits.get(name) else ""
        lines.append(f"Prompt ({name}): {prompt_info()}{commit}  ")
    lines.append(f"Raw replies: " + ", ".join(f"`{(RAW_ROOT / f'{p}_{set_name}').relative_to(EXP)}/`"
                                              for p in prompt_names))
    lines += ["", "Pass = Claude's verdict equals my label; an invalid reply is a fail.", "",
              "| prompt | set | pass rate | invalid |", "|---|---|---|---|"]
    for name in prompt_names:
        passed = sum(p[name]["pass"] for _, p in results)
        invalid = sum(p[name]["outcome"] == INVALID for _, p in results)
        lines.append(f"| {name} | {set_name} | {passed}/{n} ({100 * passed / n:.0f}%) | {invalid}/{n} |")

    header = "| id | title | my label | " + " | ".join(f"{p} | pass" for p in prompt_names) + " |"
    lines += ["", header, "|---|---|---|" + "---|---|" * len(prompt_names)]
    for row, per in results:
        cols = " | ".join(f"{per[p]['outcome']} | {'yes' if per[p]['pass'] else 'no'}" for p in prompt_names)
        lines.append(f"| {row['id']} | {cell(row['title'])} | {row['my_label']} | {cols} |")

    lines += ["", f"### Failures ({set_name})", ""]
    any_fail = False
    for name in prompt_names:
        for row, per in results:
            r = per[name]
            if not r["pass"]:
                any_fail = True
                lines.append(f"- [{name}] **{row['id']}** {cell(row['title'])}: my label `{row['my_label']}`, "
                             f"Claude `{r['outcome']}` ({r['status']}). {cell(r['reason'])} — `{r['raw']}`")
    if not any_fail:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def append_to_report(text):
    """Insert before '## My conclusion' if present (keeping what I wrote); else append and add it."""
    current = PROMPT_REPORT.read_text() if PROMPT_REPORT.exists() else "# Prompt experiment\n"
    before, mark, after = current.partition(CONCLUSION)
    if mark:
        updated = before.rstrip("\n") + "\n\n" + text + "\n" + mark + after
    else:
        updated = current.rstrip("\n") + "\n\n" + text + "\n" + CONCLUSION + "\n"
    PROMPT_REPORT.write_text(updated)


def main():
    parser = argparse.ArgumentParser(prog="python3 experiment/run_revision.py")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dev", action="store_true", help="revision prompt on the 10 dev postings")
    mode.add_argument("--heldout", action="store_true", help="baseline and revision on the 10 heldout postings")
    args = parser.parse_args()

    rows = load_labels()
    postings = load_postings(rows)
    config = json.loads((PROJECT / "config.json").read_text())
    resume = load_resume(PROJECT / config["resume"])
    for path in PROMPTS.values():
        if not path.exists():
            sys.exit(f"{path.relative_to(PROJECT)} not found. Nothing was run.")

    commits = {}
    if args.heldout:
        check_heldout_not_run()
        commits = {name: check_committed(path) for name, path in PROMPTS.items()}
        set_name, prompt_names = "heldout", ["baseline", "revision"]
    else:
        set_name, prompt_names = "dev", ["revision"]
    if shutil.which("claude") is None:
        sys.exit("claude command not found. Nothing was run.")

    started = datetime.now().astimezone().isoformat(timespec="seconds")
    calls = sum(r["set"] == set_name for r in rows) * len(prompt_names)
    print(f"Started {started}: {set_name}, prompts {', '.join(prompt_names)}, {calls} Claude calls ahead", flush=True)
    results = run(set_name, prompt_names, rows, postings, resume)
    append_to_report(section(set_name, prompt_names, results, started, commits))
    for name in prompt_names:
        passed = sum(p[name]["pass"] for _, p in results)
        invalid = sum(p[name]["outcome"] == INVALID for _, p in results)
        print(f"  {name} {set_name}: pass {passed}/{len(results)}, invalid {invalid}", flush=True)
    print(f"Appended to {PROMPT_REPORT.relative_to(PROJECT)}", flush=True)


if __name__ == "__main__":
    main()
