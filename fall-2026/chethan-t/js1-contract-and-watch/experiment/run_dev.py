"""Dev experiment: rule vs my labels, Claude sampling, baseline prompt on dev.

Run from the project folder (makes 30 claude -p calls, up to 120 s each):
    python3 experiment/run_dev.py

Postings come from raw/klaviyo_20261031T175121.json only (no fetching).
experiment/labels.csv is read, never written. Claude is never called on a
heldout row.

Part 1  rule.judge on all 20 labeled postings      -> rule_vs_labels.md
Part 2  first 5 dev rows x 4 fresh Claude calls     -> SAMPLING_REPORT.md
Part 3  all 10 dev rows x 1 call, baseline prompt   -> PROMPT_EXPERIMENT.md
"""

import csv
import hashlib
import json
import shutil
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

EXP = Path(__file__).resolve().parent
PROJECT = EXP.parent
sys.path.insert(0, str(PROJECT))

from agent import claude_judge, rule  # noqa: E402
from agent.resume import load_resume  # noqa: E402

RAW_PATH = PROJECT / "raw" / "klaviyo_20261031T175121.json"
LABELS_PATH = EXP / "labels.csv"
RULE_REPORT = EXP / "rule_vs_labels.md"
SAMPLING_REPORT = EXP / "SAMPLING_REPORT.md"
SAMPLING_RAW = EXP / "sampling" / "raw"
PROMPT_REPORT = EXP / "PROMPT_EXPERIMENT.md"
BASELINE_RAW = EXP / "prompt_experiment" / "raw" / "baseline_dev"

LABELS = {"relevant", "not_relevant"}
SETS = {"dev", "heldout"}
N_ROWS, N_SAMPLED, N_RUNS = 20, 5, 4
CONCLUSION = "## My conclusion"
INVALID = "invalid"


# ---- Inputs and checks ----

def load_labels():
    """Read labels.csv; stop unless it has 20 rows, each fully labeled."""
    with LABELS_PATH.open(newline="") as f:
        rows = list(csv.DictReader(f))
    problems = []
    if len(rows) != N_ROWS:
        problems.append(f"expected {N_ROWS} rows, found {len(rows)}")
    for line, row in enumerate(rows, start=2):
        label = (row.get("my_label") or "").strip()
        if label not in LABELS:
            problems.append(f"line {line} (id {row.get('id')}): my_label is {row.get('my_label')!r}")
        if row.get("set") not in SETS:
            problems.append(f"line {line} (id {row.get('id')}): set is {row.get('set')!r}")
        row["my_label"] = label  # in memory only
    if problems:
        sys.exit("labels.csv is not ready; nothing was run:\n  " + "\n  ".join(problems))
    return rows


def load_postings(rows):
    jobs = {j["id"]: j for j in json.loads(RAW_PATH.read_text())["jobs"]}
    missing = [r["id"] for r in rows if int(r["id"]) not in jobs]
    if missing:
        sys.exit(f"ids not in {RAW_PATH.name}; nothing was run: {', '.join(missing)}")
    return {r["id"]: jobs[int(r["id"])] for r in rows}


def check_conclusion_not_written():
    """Refuse to overwrite a SAMPLING_REPORT.md whose conclusion I've written."""
    if not SAMPLING_REPORT.exists():
        return
    _, _, after = SAMPLING_REPORT.read_text().partition(CONCLUSION)
    if after.strip():
        sys.exit(f"{SAMPLING_REPORT.name} already has your conclusion; move it aside first. Nothing was run.")


def prompt_info():
    path = claude_judge.PROMPT_PATH
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return f"`{path.relative_to(PROJECT)}` (sha256 {digest})"


# ---- Helpers ----

def cell(text):
    return " ".join(str(text).split()).replace("|", "\\|")


def ask_claude(row, posting, resume, raw_dir, label):
    """One fresh claude -p call through claude_judge.judge; raw reply saved under raw_dir."""
    assert row["set"] == "dev", "heldout rows are never sent to Claude"
    claude_judge.RESPONSES_DIR = raw_dir
    start = time.monotonic()
    j = claude_judge.judge(posting, resume)
    outcome = j["verdict"] if j["status"] == "ok" else INVALID
    raw = str((raw_dir.parent / j["raw_file"]).relative_to(EXP)) if j.get("raw_file") else "—"
    note = "" if outcome != INVALID else f"  [{j['status']}{': ' + j['error'] if j.get('error') else ''}]"
    print(f"  {label}: {outcome} ({time.monotonic() - start:.1f}s){note}", flush=True)
    return {
        "outcome": outcome,
        "status": j["status"],
        "reason": j.get("reason") or j.get("error") or "",
        "raw": raw,
    }


# ---- Part 1: rule vs my labels ----

def part1(rows, postings, resume, started):
    print(f"Part 1: rule vs my labels ({len(rows)} postings)", flush=True)
    results = [(row, rule.judge(postings[row["id"]], resume)) for row in rows]
    agree = [rec["verdict"] == row["my_label"] for row, rec in results]

    lines = [
        "# Rule vs my labels", "",
        f"Run: {started}  ",
        f"Postings: {RAW_PATH.relative_to(PROJECT)}  ",
        f"Labels: {LABELS_PATH.relative_to(PROJECT)}", "",
        f"**Agreement: {sum(agree)}/{len(rows)}**", "",
    ]
    for s in ("dev", "heldout"):
        n = [a for (row, _), a in zip(results, agree) if row["set"] == s]
        lines.append(f"- {s}: {sum(n)}/{len(n)}")
    lines += ["", "| id | title | set | my_label | rule verdict | match |", "|---|---|---|---|---|---|"]
    for (row, rec), ok in zip(results, agree):
        lines.append(f"| {row['id']} | {cell(row['title'])} | {row['set']} | {row['my_label']} "
                     f"| {rec['verdict']} | {'yes' if ok else 'no'} |")
    lines += ["", "## Disagreements", ""]
    misses = [(row, rec) for (row, rec), ok in zip(results, agree) if not ok]
    for row, rec in misses:
        lines.append(f"- **{row['id']}** {cell(row['title'])} ({row['set']}): my label "
                     f"`{row['my_label']}`, rule `{rec['verdict']}`. Rule's reason: {cell(rec['reason'])}")
    if not misses:
        lines.append("None.")
    RULE_REPORT.write_text("\n".join(lines) + "\n")
    print(f"  agreement {sum(agree)}/{len(rows)} -> {RULE_REPORT.relative_to(PROJECT)}", flush=True)


# ---- Part 2: sampling ----

def part2(dev, postings, resume, started):
    sampled = dev[:N_SAMPLED]
    print(f"Part 2: sampling, {len(sampled)} dev postings x {N_RUNS} runs", flush=True)
    per_posting = []
    for i, row in enumerate(sampled, start=1):
        runs = [ask_claude(row, postings[row["id"]], resume, SAMPLING_RAW,
                           f"posting {i}/{len(sampled)} (id {row['id']}) run {k}/{N_RUNS}")
                for k in range(1, N_RUNS + 1)]
        per_posting.append((row, runs))

    run_cols = " | ".join(f"run {k}" for k in range(1, N_RUNS + 1))
    lines = [
        "# Sampling report", "",
        f"Run: {started}  ",
        f"Prompt: {prompt_info()}  ",
        f"Postings: first {len(sampled)} dev rows of {LABELS_PATH.name}, "
        f"{N_RUNS} fresh `claude -p` calls each", "",
        "*agree* = runs giving the most common verdict (invalid replies are not a verdict).", "",
        f"| id | title | {run_cols} | agree | my label | matched my label |",
        "|---|---|" + "---|" * N_RUNS + "---|---|---|",
    ]
    invalid = 0
    for row, runs in per_posting:
        outcomes = [r["outcome"] for r in runs]
        invalid += outcomes.count(INVALID)
        valid = Counter(o for o in outcomes if o != INVALID)
        agree = max(valid.values()) if valid else 0
        matched = outcomes.count(row["my_label"])
        lines.append(f"| {row['id']} | {cell(row['title'])} | " + " | ".join(outcomes)
                     + f" | {agree}/{N_RUNS} | {row['my_label']} | {matched}/{N_RUNS} |")
    total = len(per_posting) * N_RUNS
    lines += ["", f"**Invalid replies: {invalid}/{total}**", "", "## Details", ""]
    for row, runs in per_posting:
        lines.append(f"### {row['id']} {cell(row['title'])} (my label: {row['my_label']})")
        lines.append("")
        for k, r in enumerate(runs, start=1):
            lines.append(f"- run {k}: `{r['outcome']}` ({r['status']}) {cell(r['reason'])} — `{r['raw']}`")
        lines.append("")
    lines += [CONCLUSION, ""]
    SAMPLING_REPORT.write_text("\n".join(lines) + "\n")
    print(f"  invalid {invalid}/{total} -> {SAMPLING_REPORT.relative_to(PROJECT)}", flush=True)


# ---- Part 3: baseline prompt on dev ----

def part3(dev, postings, resume, started):
    print(f"Part 3: baseline prompt, {len(dev)} dev postings x 1 run", flush=True)
    results = [(row, ask_claude(row, postings[row["id"]], resume, BASELINE_RAW,
                                f"posting {i}/{len(dev)} (id {row['id']})"))
               for i, row in enumerate(dev, start=1)]
    passed = [r["outcome"] == row["my_label"] for row, r in results]

    rate = f"{sum(passed)}/{len(dev)} ({100 * sum(passed) / len(dev):.0f}%)"
    lines = [
        "# Prompt experiment: baseline on dev", "",
        f"Date: {started}  ",
        f"Prompt: {prompt_info()}  ",
        f"Raw replies: `{BASELINE_RAW.relative_to(EXP)}/`", "",
        "Pass = Claude's verdict equals my label; an invalid reply is a fail.", "",
        f"**Dev pass rate: {rate}**", "",
        "| id | title | my label | Claude verdict | pass |", "|---|---|---|---|---|",
    ]
    for (row, r), ok in zip(results, passed):
        lines.append(f"| {row['id']} | {cell(row['title'])} | {row['my_label']} | {r['outcome']} "
                     f"| {'yes' if ok else 'no'} |")
    lines += ["", "## Failures", ""]
    fails = [(row, r) for (row, r), ok in zip(results, passed) if not ok]
    for row, r in fails:
        lines.append(f"- **{row['id']}** {cell(row['title'])}: my label `{row['my_label']}`, "
                     f"Claude `{r['outcome']}` ({r['status']}). {cell(r['reason'])} — `{r['raw']}`")
    if not fails:
        lines.append("None.")
    PROMPT_REPORT.write_text("\n".join(lines) + "\n")
    print(f"  dev pass rate {rate} -> {PROMPT_REPORT.relative_to(PROJECT)}", flush=True)


def main():
    rows = load_labels()
    postings = load_postings(rows)
    config = json.loads((PROJECT / "config.json").read_text())
    resume = load_resume(PROJECT / config["resume"])
    dev = [r for r in rows if r["set"] == "dev"]  # heldout rows are skipped from here on
    if len(dev) < N_SAMPLED:
        sys.exit(f"need at least {N_SAMPLED} dev rows, found {len(dev)}; nothing was run")
    check_conclusion_not_written()
    if shutil.which("claude") is None:
        sys.exit("claude command not found; Parts 2-3 need it. Nothing was run.")

    started = datetime.now().astimezone().isoformat(timespec="seconds")
    calls = N_SAMPLED * N_RUNS + len(dev)
    print(f"Started {started}: {len(rows)} labeled rows, {len(dev)} dev, {calls} Claude calls ahead", flush=True)
    part1(rows, postings, resume, started)
    part2(dev, postings, resume, started)
    part3(dev, postings, resume, started)
    print("Done.", flush=True)


if __name__ == "__main__":
    main()
