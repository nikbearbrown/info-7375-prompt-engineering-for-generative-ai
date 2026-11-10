"""Copy-paste Claude judge for claude.ai chats: same prompt builder and validator as agent/judge.py, no API calls."""

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from agent.judge import MAX_ATTEMPTS, build_posting_payload, build_prompt, build_resume_payload, validate_reply
from agent.resume import load_resume

ROOT = Path(__file__).parent.parent
PROMPTS_DIR = ROOT / "prompts"
RUNS_DIR = ROOT / "runs"
LABELS_FILE = ROOT / "labels" / "labels.csv"
RESULT_COLUMNS = ("timestamp", "posting_id", "version", "attempt", "model_label", "valid", "verdict", "error")
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


def _safe(name: str, what: str) -> str:
    # Names become path parts; refuse anything that could leave runs/.
    if not SAFE_NAME.match(name) or name in (".", ".."):
        raise SystemExit(f"error: {what} {name!r} may contain only letters, digits, '.', '_' and '-'")
    return name


def _template(version: str) -> Path:
    path = PROMPTS_DIR / f"judge_{_safe(version, 'version')}.txt"
    if not path.is_file():
        raise SystemExit(f"error: prompt template {path.relative_to(ROOT)} does not exist")
    return path


def _attempt(value: str) -> int:
    attempt = int(value)
    if not 1 <= attempt <= MAX_ATTEMPTS:
        raise argparse.ArgumentTypeError(f"attempt must be between 1 and {MAX_ATTEMPTS}")
    return attempt


def _run_dir(experiment: str, version: str) -> Path:
    return RUNS_DIR / _safe(experiment, "experiment") / _safe(version, "version")


def _stem(posting_id: str, attempt: int) -> str:
    return f"{_safe(posting_id, 'posting id')}_a{attempt}"


def _find_posting(evidence: Path, posting_id: str) -> dict:
    jobs = json.loads(evidence.read_text(encoding="utf-8"))["jobs"]
    for job in jobs:
        if isinstance(job, dict) and str(job.get("id")) == posting_id:
            return job
    raise SystemExit(f"error: posting {posting_id} not found in {evidence}")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_results(experiment: str) -> list:
    path = RUNS_DIR / experiment / "results.csv"
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _append_result(experiment: str, row: dict) -> Path:
    path = RUNS_DIR / experiment / "results.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)
    return path


def cmd_prompt(args) -> None:
    template = _template(args.version)
    # Same identity check as a live run, before anything is handed to Claude.
    resume = load_resume(args.resume)
    posting = _find_posting(Path(args.evidence), args.posting)
    prompt = build_prompt(posting, resume, template)

    run_dir = _run_dir(args.experiment, args.version)
    run_dir.mkdir(parents=True, exist_ok=True)
    stem = _stem(args.posting, args.attempt)
    prompt_path = run_dir / f"{stem}_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    # check needs the same inputs to rebuild the validator's payloads.
    meta = {
        "posting_id": args.posting,
        "version": args.version,
        "attempt": args.attempt,
        "template": str(template.relative_to(ROOT)),
        "evidence": args.evidence,
        "resume": args.resume,
        "prompt_sha256": _sha256(prompt),
    }
    (run_dir / f"{stem}_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(prompt_path)


def cmd_check(args) -> None:
    run_dir = _run_dir(args.experiment, args.version)
    stem = _stem(args.posting, args.attempt)
    meta_path, reply_path = run_dir / f"{stem}_meta.json", run_dir / f"{stem}_reply.txt"
    if not meta_path.exists():
        raise SystemExit(f"error: {meta_path.relative_to(ROOT)} not found; run the prompt subcommand first")
    if not reply_path.exists():
        raise SystemExit(f"error: paste Claude's reply into {reply_path.relative_to(ROOT)} first")

    earlier = {
        int(r["attempt"]): r
        for r in _read_results(args.experiment)
        if r["posting_id"] == args.posting and r["version"] == args.version
    }
    if args.attempt in earlier:
        raise SystemExit(f"error: attempt {args.attempt} for {args.posting} ({args.version}) is already recorded")
    if args.attempt > 1:
        previous = earlier.get(args.attempt - 1)
        if previous is None:
            raise SystemExit(f"error: attempt {args.attempt - 1} must be checked before attempt {args.attempt}")
        if previous["valid"] == "true":
            raise SystemExit(f"error: attempt {args.attempt - 1} was valid; the contract allows a retry only after an invalid reply")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    resume = load_resume(meta["resume"])
    posting = _find_posting(Path(meta["evidence"]), args.posting)
    if _sha256(build_prompt(posting, resume, ROOT / meta["template"])) != meta["prompt_sha256"]:
        raise SystemExit("error: the template, evidence or résumé changed since the prompt was built; rebuild it")

    reply = reply_path.read_text(encoding="utf-8")
    try:
        data = validate_reply(reply, build_resume_payload(resume), build_posting_payload(posting))
        valid, verdict, error = True, data["verdict"], ""
    except ValueError as e:
        valid, verdict, error = False, "invalid", str(e)

    _append_result(args.experiment, {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "posting_id": args.posting,
        "version": args.version,
        "attempt": args.attempt,
        "model_label": args.model_label,
        "valid": "true" if valid else "false",
        "verdict": verdict,
        "error": error,
    })

    if valid:
        print(f"VALID: verdict={verdict}")
    else:
        print(f"INVALID: {error}")
        if args.attempt < MAX_ATTEMPTS:
            print(f"Retry once in a NEW chat: prompt --attempt {args.attempt + 1}")
        else:
            print("Final judgment for this posting is: invalid")


def _final_verdicts(experiment: str, version: str) -> dict:
    final = {}
    for row in _read_results(experiment):
        if row["version"] != version:
            continue
        current = final.get(row["posting_id"])
        if current is None or int(row["attempt"]) > int(current["attempt"]):
            final[row["posting_id"]] = row
    return final


def cmd_score(args) -> None:
    _safe(args.experiment, "experiment")
    _safe(args.version, "version")
    with open(LABELS_FILE, newline="", encoding="utf-8") as f:
        labels = [r for r in csv.DictReader(f) if r["split"] == args.split]
    if not labels:
        raise SystemExit(f"error: no postings in split {args.split!r}")

    final = _final_verdicts(args.experiment, args.version)
    rows, passes, invalid, warnings = [], 0, 0, []
    for label in labels:
        pid = label["posting_id"]
        result = final.get(pid)
        if result is None:
            verdict, note = "missing", "no attempt recorded"
            warnings.append(pid)
        else:
            verdict, note = result["verdict"], f"attempt {result['attempt']}"
            if verdict == "invalid" and int(result["attempt"]) < MAX_ATTEMPTS:
                note += ", retry not yet done"
                warnings.append(pid)
        if verdict == "invalid":
            invalid += 1
        ok = verdict == label["my_label"]
        passes += ok
        rows.append((pid, label["title"], label["my_label"], verdict, "pass" if ok else "fail", note))

    n = len(labels)
    baseline = sum(label["my_label"] == "not_relevant" for label in labels)
    lines = [
        f"# Score: {args.experiment} / {args.version} / {args.split}",
        "",
        f"- Postings: {n}",
        f"- Pass: {passes}/{n} ({passes / n:.0%})",
        f"- Invalid (counted as fail): {invalid}",
        f"- Always-not_relevant baseline: {baseline}/{n} ({baseline / n:.0%})",
    ]
    if warnings:
        lines.append(f"- Incomplete (counted as fail): {', '.join(warnings)}")
    lines += [
        "",
        "| posting_id | title | my_label | judgment | result | note |",
        "|---|---|---|---|---|---|",
    ]
    lines += [f"| {' | '.join(cell.replace('|', '/') for cell in row)} |" for row in rows]
    text = "\n".join(lines) + "\n"

    out = RUNS_DIR / args.experiment / f"score_{args.version}_{args.split}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Written to {out.relative_to(ROOT)}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="python -m agent.manual_judge")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("prompt", help="build the prompt to paste into a new claude.ai chat")
    p.add_argument("--posting", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--resume", required=True)
    p.add_argument("--experiment", required=True)
    p.add_argument("--attempt", type=_attempt, required=True)
    p.set_defaults(func=cmd_prompt)

    c = sub.add_parser("check", help="validate the pasted reply and record it")
    c.add_argument("--posting", required=True)
    c.add_argument("--version", required=True)
    c.add_argument("--experiment", required=True)
    c.add_argument("--attempt", type=_attempt, required=True)
    c.add_argument("--model-label", required=True)
    c.set_defaults(func=cmd_check)

    s = sub.add_parser("score", help="compare final judgments with my_label")
    s.add_argument("--experiment", required=True)
    s.add_argument("--version", required=True)
    s.add_argument("--split", required=True)
    s.set_defaults(func=cmd_score)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
