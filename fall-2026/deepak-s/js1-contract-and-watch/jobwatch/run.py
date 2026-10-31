"""One `run`, step by step as in CONTRACT.md Order of operations."""
import sys
from datetime import datetime, timezone
from pathlib import Path

from jobwatch.backends import make_judge
from jobwatch.errors import BAD_RULE_VERDICT, NETWORK, OK, OTHER, Stop
from jobwatch.evidence import RunDir, new_run_id, sha256_hex, utc_iso
from jobwatch.fetch import FetchFailed, board_url, check_url, default_opener, fetch
from jobwatch.inputs import check_token, load_resume
from jobwatch.judge import not_available, stopped_judgment
from jobwatch.postings import location_name, parse_body, posting_document
from jobwatch.prompt import load_prompt
from jobwatch.report import agreement, build_report, render_text
from jobwatch.rule import apply_rule
from jobwatch.state import load_state, write_state
from jobwatch.validator import Invalid, check_verdict


def run(args, *, opener=None, client=None, now=None):
    clock = (lambda: now) if now is not None else (lambda: datetime.now(timezone.utc))
    started = clock()
    token = args.board

    # 1-3: inputs and state. Nothing is requested or written before these pass.
    check_token(token)
    resume, resume_raw = load_resume(args.resume)
    judge = make_judge(args.judge, client)
    judging = judge.available()
    prompt = load_prompt(args.prompt) if judging else None
    state = load_state(token)
    label = "baseline" if not state.exists else ("seeded" if args.from_file else "live")

    # 4: the one board request, or the saved file in a seeded run.
    url, response, failure, from_file_sha = None, None, None, None
    if args.from_file:
        try:
            body = Path(args.from_file).read_bytes()
        except OSError:
            raise Stop(OTHER, f"cannot read --from-file {args.from_file}") from None
        from_file_sha = sha256_hex(body)
    else:
        url = board_url(token)
        check_url(url)
        try:
            response = fetch(url, opener or default_opener())
            body = response.body
        except FetchFailed as e:
            failure, body = e.kind, None
    fetched_at = utc_iso(clock())

    # 5: raw bytes and manifest, before the status is judged.
    run_dir = RunDir(new_run_id(started, token))
    raw_path = run_dir.write_raw(body) if body is not None else None
    manifest = {
        "run_id": run_dir.run_id,
        "label": label,
        "board": token,
        "source": "file" if args.from_file else "network",
        "url": url,
        "from_file": args.from_file,
        "from_file_sha256": from_file_sha,
        "method": "GET",
        "http_status": response.status if response else None,
        "fetched_at": fetched_at,
        "sha256": sha256_hex(body) if body is not None else None,
        "byte_length": len(body) if body is not None else None,
        "raw_path": raw_path,
        "resume_path": args.resume,
        "resume_sha256": sha256_hex(resume_raw),
        "state_before_sha256": sha256_hex(state.raw) if state.exists else None,
        "prompt_path": prompt.path if prompt else None,
        "prompt_sha256": prompt.sha256 if prompt else None,
        "model": args.model,
        "judge_backend": judge.name,
    }
    if response is not None and 300 <= response.status < 400:
        manifest["location_header"] = response.headers.get("Location")
    if failure:
        manifest["error"] = failure
    run_dir.write_json("manifest.json", manifest)
    if state.exists:
        run_dir.write("state_before.json", state.raw)

    # 6: any 3xx or non-200 ends the run; the state is untouched.
    if failure:
        raise Stop(NETWORK, f"board fetch failed ({failure}); state unchanged")
    if response is not None and response.status != 200:
        raise Stop(NETWORK, f"board answered HTTP {response.status}; not followed, state unchanged")

    # 7-8: parse, then new = judgeable ids not yet seen (none on a baseline run).
    parsed = parse_body(body)
    new = [] if not state.exists else [(p, j) for p, j in parsed.judgeable() if p not in state.seen_ids]

    # 9: the rule and its validator, then the judge and its validator. A claude-cli failure stops
    # the judge; the postings after it are not judged (Amendment A14).
    records = []
    for pid, job in new:
        doc = posting_document(job)
        verdict = apply_rule(resume, job)
        try:
            check_verdict(verdict, resume, doc)
        except Invalid as e:
            raise Stop(BAD_RULE_VERDICT, f"the rule produced an invalid verdict for {pid} ({e.reason})") from None
        if not judging:
            judgment = not_available(judge)
        elif judge.stopped:
            judgment = stopped_judgment()
        else:
            judgment = judge.call(prompt, args.model, resume, pid, doc, run_dir, clock)
        records.append({
            "posting_id": pid,
            "title": job.get("title"),
            "absolute_url": job.get("absolute_url"),
            "location": location_name(job),
            "record": verdict,
            "judgment": judgment,
            "agreement": agreement(verdict, judgment),
        })

    # 10: the report, saved and printed.
    report = build_report(
        run_id=run_dir.run_id,
        label=label,
        board=token,
        source=manifest["source"],
        from_file=args.from_file,
        from_file_sha256=from_file_sha,
        generated_at=utc_iso(clock()),
        parsed=parsed,
        previously_seen=sum(p in state.seen_ids for p, _ in parsed.kept),
        records=records,
        judge={"status": "run" if judging else "not_run", "backend": judge.name, "model": args.model,
               "prompt_sha256": prompt.sha256 if prompt else None},
    )
    run_dir.write_json("report.json", report)
    text = render_text(report)
    run_dir.write("report.txt", text)
    print(text, end="")

    # 11: every id ever seen, written atomically.
    write_state(token, state.seen_ids | {p for p, _ in parsed.kept}, utc_iso(clock()), run_dir.run_id)
    if judge.stopped:
        print(f"jobwatch: judge stopped: {judge.stopped['reason']} on posting {judge.stopped['posting_id']}; "
              "later postings were not judged; report and state written", file=sys.stderr)
        return OTHER
    return OK
