"""`replay RUN_DIR`: CONTRACT.md Interfaces › replay, and Amendments A9 and A14.

Offline, needs no key, writes nothing. Rebuilds the report from the saved raw response,
state_before.json and the saved Claude responses, re-validates the responses, and exits 1 on any
difference or sha256 mismatch.

Not recomputable from files, so taken from the saved report.json: `generated_at`, and the
`reason` and `called_at` of an sdk `error` judgment (no response, so nothing else records them).
A claude-cli call records its error in response.meta.json, so it is recomputed.
"""
import json
from pathlib import Path

from jobwatch.errors import OK, OTHER, Stop
from jobwatch.evidence import RUNS_DIR, sha256_hex
from jobwatch.inputs import load_resume
from jobwatch.backends import make_judge
from jobwatch.judge import not_available, stopped_judgment
from jobwatch.postings import location_name, parse_body, posting_document
from jobwatch.prompt import load_prompt
from jobwatch.report import agreement, build_report, render_text
from jobwatch.rule import apply_rule
from jobwatch.state import parse_state
from jobwatch.validator import Invalid, check_verdict

A1_FIELDS = ("source", "from_file", "from_file_sha256")


class Mismatch(Exception):
    """A difference that stops the replay before the report can be rebuilt."""


def _read(path):
    try:
        return Path(path).read_bytes()
    except OSError:
        raise Mismatch(f"cannot read {Path(path).as_posix()}") from None


def _json(path):
    try:
        return json.loads(_read(path))
    except ValueError:
        raise Mismatch(f"{Path(path).as_posix()} is not valid JSON") from None


def _check_sha(what, data, expected):
    if sha256_hex(data) != expected:
        raise Mismatch(f"sha256 mismatch: {what}")


def _rebuild(run_dir, manifest, saved_report, notes):
    run_id, token = manifest["run_id"], manifest["board"]
    judge = make_judge(manifest.get("judge_backend", "sdk"))

    if not manifest.get("raw_path"):
        raise Mismatch("the manifest names no raw response")
    body = _read(manifest["raw_path"])
    _check_sha(manifest["raw_path"], body, manifest.get("sha256"))
    if len(body) != manifest.get("byte_length"):
        raise Mismatch(f"byte_length differs: {manifest['raw_path']}")
    if manifest.get("source") == "file" and manifest.get("from_file_sha256") != manifest.get("sha256"):
        raise Mismatch("from_file_sha256 differs from the raw response's sha256")

    state_file = run_dir / "state_before.json"
    if manifest.get("state_before_sha256") is None:
        if state_file.exists():
            raise Mismatch("state_before.json exists but the manifest records a baseline run")
        seen, baseline = set(), True
    else:
        raw_state = _read(state_file)
        _check_sha("state_before.json", raw_state, manifest["state_before_sha256"])
        try:
            seen = parse_state(raw_state, token, state_file.as_posix()).seen_ids
        except Stop as e:
            raise Mismatch(str(e)) from None
        baseline = False

    _check_sha(manifest["resume_path"], _read(manifest["resume_path"]), manifest.get("resume_sha256"))
    resume, _ = load_resume(manifest["resume_path"])
    prompt = None
    if manifest.get("prompt_sha256") is not None:
        _check_sha(manifest["prompt_path"], _read(manifest["prompt_path"]), manifest["prompt_sha256"])
        prompt = load_prompt(manifest["prompt_path"])

    parsed = parse_body(body)
    new = [] if baseline else [(p, j) for p, j in parsed.judgeable() if p not in seen]
    saved_records = {r.get("posting_id"): r for r in saved_report.get("records", []) if isinstance(r, dict)}
    claude = run_dir / "claude"
    requested = {f.name[: -len(".request.json")] for f in claude.glob("*.request.json")} if claude.is_dir() else set()

    records, errors, called, stopped = [], [], set(), False
    for pid, job in new:
        doc = posting_document(job)
        verdict = apply_rule(resume, job)
        try:
            check_verdict(verdict, resume, doc)
        except Invalid as e:
            raise Mismatch(f"the rule's verdict for {pid} is invalid ({e.reason})") from None
        if prompt is None:
            judgment = not_available(judge)
        elif stopped:
            judgment = stopped_judgment()
        else:
            called.add(pid)
            if pid not in requested:
                raise Mismatch(f"no saved request for posting {pid}")
            if _json(claude / f"{pid}.request.json") != judge.request(prompt, manifest["model"], resume, pid, doc):
                raise Mismatch(f"claude/{pid}.request.json differs from the request rebuilt from the prompt")
            raw_path = (RUNS_DIR / run_id / "claude" / f"{pid}.response.txt").as_posix()
            judgment = judge.saved(run_dir, pid, pid, resume, doc, raw_path)
            if judgment is None and judge.name == "claude-cli":
                raise Mismatch(f"claude/{pid}.response.meta.json is missing")
            if judgment is None:
                was = (saved_records.get(pid) or {}).get("judgment") or {}
                judgment = {"status": "error", "reason": was.get("reason"), "verdict": None, "citations": None,
                            "model": manifest["model"], "called_at": was.get("called_at"), "raw_path": None}
                errors.append(pid)
            stopped = judge.name == "claude-cli" and judgment["status"] == "error"
        records.append({
            "posting_id": pid,
            "title": job.get("title"),
            "absolute_url": job.get("absolute_url"),
            "location": location_name(job),
            "record": verdict,
            "judgment": judgment,
            "agreement": agreement(verdict, judgment),
        })
    if requested != called:
        raise Mismatch(f"saved Claude requests are for {sorted(requested)}, expected {sorted(called)}")
    if errors:
        notes.append(f"error judgment(s) {', '.join(errors)}: reason and called_at taken from report.json "
                     "(no response was saved)")

    label = "baseline" if baseline else ("seeded" if manifest.get("source") == "file" else "live")
    return build_report(
        run_id=run_id,
        label=label,
        board=token,
        source=manifest.get("source"),
        from_file=manifest.get("from_file"),
        from_file_sha256=manifest.get("from_file_sha256"),
        generated_at=saved_report.get("generated_at"),
        parsed=parsed,
        previously_seen=sum(p in seen for p, _ in parsed.kept),
        records=records,
        judge={"status": "run" if prompt else "not_run", "backend": judge.name, "model": manifest["model"],
               "prompt_sha256": manifest.get("prompt_sha256")},
    )


def _differences(rebuilt, saved):
    out = []
    for key in sorted(set(rebuilt) | set(saved)):
        if key == "records" and isinstance(saved.get(key), list) and len(saved[key]) == len(rebuilt[key]):
            for i, (r, s) in enumerate(zip(rebuilt[key], saved[key])):
                for field in sorted(set(r) | set(s if isinstance(s, dict) else {})):
                    if not isinstance(s, dict) or r.get(field) != s.get(field):
                        out.append(f"records[{i}].{field}")
        elif rebuilt.get(key) != saved.get(key) or (key in rebuilt) != (key in saved):
            out.append(key)
    return out


def replay(args):
    run_dir = Path(args.run_dir)
    notes = []
    try:
        manifest = _json(run_dir / "manifest.json")
        if not (run_dir / "report.json").exists():
            raise Mismatch("no report.json: the run stopped before its report (Amendment A4)")
        saved_report = _json(run_dir / "report.json")
        saved_text = _read(run_dir / "report.txt").decode("utf-8")
        rebuilt = _rebuild(run_dir, manifest, saved_report, notes)
    except Mismatch as e:
        print(f"replay {run_dir.as_posix()}: DIFFERENCE: {e}")
        return OTHER

    if "backend" not in (saved_report.get("judge") or {}):
        del rebuilt["judge"]["backend"]
        notes.append("report.json predates Amendment A14: the judge backend was not compared")
    text = render_text(rebuilt)
    if not any(k in saved_report for k in A1_FIELDS):
        for k in A1_FIELDS:
            del rebuilt[k]
        lines = text.splitlines(keepends=True)
        text = "".join(lines[:1] + lines[2:])
        notes.append("report.json predates Amendment A1: source taken from manifest.json; "
                     "A1 fields (source, from_file, from_file_sha256) not compared")

    differences = _differences(rebuilt, saved_report)
    if text != saved_text:
        differences.append("report.txt")
    for note in notes:
        print(f"replay {run_dir.as_posix()}: {note}")
    if differences:
        print(f"replay {run_dir.as_posix()}: DIFFERENCE in {', '.join(differences)}")
        return OTHER
    judged = sum(r["judgment"]["raw_path"] is not None for r in rebuilt["records"])
    checked = ["raw response"] + (["state_before.json"] if manifest.get("state_before_sha256") else []) + ["résumé"] \
        + (["prompt"] if manifest.get("prompt_sha256") else [])
    listed = ", ".join(checked[:-1]) + " and " + checked[-1]
    print(f"replay {run_dir.as_posix()}: ok. sha256 of {listed} match the manifest; "
          f"{len(rebuilt['records'])} record(s) rebuilt, {judged} saved response(s) re-validated; "
          "report.json and report.txt match")
    return OK
