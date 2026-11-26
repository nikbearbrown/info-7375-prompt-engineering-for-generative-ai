"""Command line. `python3 -m agent watch` (one real run), `watch --wrong-version 3` (the labelled demonstration),
`check RUN_DIR` (the independent check)."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import audit, check, claims_page, collection, judge, shortlist, config, filter as filt, loop, resume, wrong_versions
from .policy import Policy


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m agent")
    commands = parser.add_subparsers(dest="command", required=True)
    w = commands.add_parser("watch", help="one bounded run over config/boards.json")
    w.add_argument("--wrong-version", type=int, choices=sorted(wrong_versions.VERSIONS),
                   help="run a deliberate wrong version (labelled WRONG, its own state file); for the demonstration only")
    c = commands.add_parser("check", help="compare a run's report with its saved raw responses")
    c.add_argument("run_dir")
    f = commands.add_parser("filter", help="run a filter file on everything one watch run collected (offline)")
    f.add_argument("--run", help="the watch run folder (default: the latest real run)")
    f.add_argument("--filter", default="filters/v1.0.json", help="the filter file (default: filters/v1.0.json)")
    commands.add_parser("shortlist", help="ask Claude for a justification of each shortlisted posting (real calls; filter v1.1) and label every claim")
    commands.add_parser("audit", help="score my hand labels against filter v1.0 on the tuning sets (never the held-out set)")
    m = commands.add_parser("measure", help="compare filter files on the held-out set only")
    m.add_argument("filters", nargs="+", help="filter files, the baseline first")
    j = commands.add_parser("judge", help="real Claude calls: Claude's verdict on each held-out posting, with one context")
    j.add_argument("context", choices=judge.CONTEXTS)
    commands.add_parser("reread-page", help="build the careful re-read page: every engineering posting in the tuning sets")
    commands.add_parser("draw-sample", help="draw the audit sample from the v1.0 decisions and build the blind labelling page")
    args = parser.parse_args(argv)

    policy = Policy()
    if args.command == "filter":
        return run_filter(args, policy)
    if args.command == "shortlist":
        return run_shortlist(policy)
    if args.command == "audit":
        return run_audit(policy)
    if args.command == "measure":
        return run_measure(args, policy)
    if args.command == "judge":
        return run_judge(args, policy)
    if args.command == "reread-page":
        return reread_page(policy)
    if args.command == "draw-sample":
        return draw_sample(policy)
    if args.command == "check":
        problems, notes = check.check(Path(args.run_dir).resolve(), config.ROOT, policy)
        for note in notes:
            print(f"note: {note}")
        if any(not p.startswith(check.SUSPICIOUS) for p in problems):
            print("CHECK FAILED")
            for p in problems:
                print(f"- {p}")
            return 1
        if problems:
            print("NEEDS REVIEW: nothing is proven wrong, but this is suspicious")
            for p in problems:
                print(f"- {p}")
            return 2
        print("check passed: the report matches the saved raw responses")
        return 0

    persona = resume.load(policy.check_read(config.RESUME))  # refuses a non-fictional résumé before any request
    now = datetime.now(timezone.utc).replace(microsecond=0)
    tag = f"-WRONG-V{args.wrong_version}" if args.wrong_version else ""
    state_path = config.STATE.with_name(f"seen_ids{tag}.json") if tag else config.STATE
    if tag and not state_path.exists():
        state_path = config.STATE  # start the demonstration from the real state, but never write back to it
    state = json.loads(policy.check_read(state_path).read_text(encoding="utf-8")) if state_path.exists() else {}
    hooks = wrong_versions.VERSIONS[args.wrong_version] if args.wrong_version else None

    boards, budgets = (json.loads(policy.check_read(config.CONFIG_DIR / f"{n}.json").read_text(encoding="utf-8"))
                       for n in ("boards", "budgets"))
    result = loop.run(boards, budgets, policy, persona, state, config.RAW_DIR,
                      now=now, hooks=hooks, tag=tag)

    run_dir = config.RUNS_DIR / f"{now.strftime('%Y%m%dT%H%M%SZ')}{tag}"
    label = f" (WRONG VERSION {args.wrong_version}, deliberate: see FINISHED-WRONG.md)" if tag else ""
    policy.write_text(run_dir / "trace.jsonl", loop.trace_jsonl(result))
    policy.write_text(run_dir / "report.json", json.dumps(loop.summary(result), indent=2, ensure_ascii=False) + "\n")
    policy.write_text(run_dir / "report.md", loop.report_markdown(result, label))
    if result.status != "error":
        state.setdefault("runs", []).append({"at": result.started_at, "status": result.status, "run": run_dir.name})
        policy.write_text(config.STATE.with_name(f"seen_ids{tag}.json"), json.dumps(state, indent=2) + "\n")
    print(loop.report_markdown(result, label))
    print(f"(trace, report and raw responses saved under {run_dir.relative_to(config.ROOT)}/ and evidence/raw/)")
    return 0 if result.status == "finished" else 3


def run_filter(args, policy):
    persona = resume.load(policy.check_read(config.RESUME))
    run_dir = policy.check_read(args.run) if args.run else collection.latest_run(policy)
    spec = filt.load_filter(policy.check_read(args.filter))
    postings, failed = collection.load_run(run_dir, policy)
    decisions = filt.decide_all(postings, persona, spec)
    out = run_dir / f"filter-v{spec['version']}"
    policy.write_text(out / "decisions.jsonl",
                      "".join(json.dumps(d.to_dict(), ensure_ascii=False) + "\n" for d in decisions))
    text = filter_summary(run_dir, spec, decisions, failed)
    policy.write_text(out / "summary.md", text)
    print(text)
    print(f"(decisions saved under {out.relative_to(config.ROOT)}/)")
    return 0


def run_shortlist(policy):
    """Real Claude Code calls, one per shortlisted posting of filter v1.1 on the latest real run."""
    run_dir = collection.latest_run(policy)
    spec = filt.load_filter(policy.check_read("filters/v1.1.json"))
    decisions = [json.loads(line) for line in
                 policy.check_read(run_dir / "filter-v1.1" / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    postings, _ = collection.load_run(run_dir, policy)
    jobs = {f"{board}:{job['id']}": job for board, job in postings}
    persona = resume.load(policy.check_read(config.RESUME))
    template = policy.check_read("prompts/justify-v1.txt").read_text(encoding="utf-8")
    out = run_dir / "shortlist-v1.1"

    def save_raw(key, text):
        policy.write_text(out / "claude" / (key.replace(":", "-") + ".json"), text)

    entries = shortlist.build(decisions, jobs, spec, persona, template, save_raw)
    policy.write_text(out / "shortlist.json", json.dumps(entries, indent=2, ensure_ascii=False) + "\n")
    policy.write_text("audit/claim-sheet.html",
                      claims_page.build(entries, {k: audit.plain(j) for k, j in jobs.items()}, about="role"))
    for e in entries:
        print(f"{e['key']} {e['title']}: " + ("INVALID " + e["invalid_reason"] if not e["valid"] else
              ", ".join(f"{c['about']}={c['machine_label']}" for c in e["claims"])))
    print(f"(saved under {out.relative_to(config.ROOT)}/)")
    return 0


LABELS = "audit/hand-labels.csv"


def _audit_inputs(policy):
    sample = json.loads(policy.check_read("audit/sample.json").read_text(encoding="utf-8"))
    # My labels; two were corrected afterwards (non-US yes -> no), and the file keeps each original label (AUDIT.md).
    labels = audit.read_labels(policy.check_read(LABELS).read_text(encoding="utf-8"))
    run_dir = policy.check_read(config.RUNS_DIR / sample["run"])
    return sample, labels, run_dir


def run_audit(policy):
    sample, labels, run_dir = _audit_inputs(policy)
    decisions = [json.loads(line) for line in
                 policy.check_read(run_dir / "filter-v1.0" / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    by_key = {audit.key(d): d for d in decisions}
    text = (f"# Audit results: filter v1.0 on run {sample['run']} against my hand labels\n\n"
            "Generated by `python3 -m agent audit` from audit/hand-labels.csv (with the two location corrections in "
            "AUDIT.md). The held-out set is not read.\n\n"
            + audit.audit_report(sample, by_key, labels))
    policy.write_text("audit/results.md", text)
    print(text)
    return 0


def run_measure(args, policy):
    sample, labels, run_dir = _audit_inputs(policy)
    postings, _ = collection.load_run(run_dir, policy)
    jobs = {f"{b}:{j['id']}": (b, j) for b, j in postings}
    persona = resume.load(policy.check_read(config.RESUME))
    specs = [(p, filt.load_filter(policy.check_read(p))) for p in args.filters]
    rows = audit.measure(specs, sample["sets"]["held_out"], jobs, persona, labels)
    for r in rows:
        print(f"{r['filter']}: agrees with my label on {r['agree']} of {r['judged']} "
              f"(95% Wilson {audit.pct(r['interval'])}); keeps {r['kept']} of {len(sample['sets']['held_out'])}; "
              f"false keeps {len(r['false_keeps'])} {r['false_keeps']}; false rejects {len(r['false_rejects'])} {r['false_rejects']}")
    return 0


def run_judge(args, policy):
    """One real Claude call per held-out posting (4 at a time), then the score against my held-out labels."""
    from concurrent.futures import ThreadPoolExecutor
    sample, labels, run_dir = _audit_inputs(policy)
    postings, _ = collection.load_run(run_dir, policy)
    jobs = {f"{b}:{j['id']}": j for b, j in postings}
    template = policy.check_read("prompts/judge-v1.txt").read_text(encoding="utf-8")
    keys = sample["sets"]["held_out"]
    out = run_dir / f"judge-{args.context}"

    def ask(key):
        raw = shortlist.call_claude(judge.build_prompt(template, jobs[key], args.context))
        policy.write_text(out / "claude" / (key.replace(":", "-") + ".json"), raw)
        try:
            return key, judge.parse(raw)
        except judge.InvalidVerdict as e:
            return key, (None, f"INVALID: {e}")

    with ThreadPoolExecutor(max_workers=4) as pool:
        answers = dict(pool.map(ask, keys))
    results = {k: v[0] for k, v in answers.items()}
    scored = judge.score(results, labels)
    policy.write_text(out / "verdicts.json", json.dumps({"context": args.context, "answers": answers, "score": scored},
                                                        indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(scored, indent=2))
    return 0


def reread_page(policy):
    sample, _, run_dir = _audit_inputs(policy)
    decisions = [json.loads(line) for line in
                 policy.check_read(run_dir / "filter-v1.0" / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    by_key = {audit.key(d): d for d in decisions}
    keys = audit.reread_keys(sample, by_key)
    postings, _ = collection.load_run(run_dir, policy)
    jobs = {f"{b}:{j['id']}": j for b, j in postings}
    extra = ("<p><b>Careful re-read.</b> Open each description and read it before you choose. Judge the same question: "
             "is this posting worth Rohan's time? Your earlier labels are not shown.</p>")
    page = audit.label_page({"sheet_order": keys}, jobs, by_key, store="js3-careful-labels-v1",
                            filename="careful-labels.csv", heading="JS3 careful re-read", extra=extra)
    policy.write_text("audit/reread.json", json.dumps({"seed": audit.REREAD_SEED, "keys": keys}, indent=2) + "\n")
    policy.write_text("audit/reread-sheet.html", page)
    print(f"{len(keys)} postings in audit/reread-sheet.html")
    return 0


def draw_sample(policy):
    """The audit sample, drawn once from filter v1.0 on the latest real run, before any hand label exists."""
    run_dir = collection.latest_run(policy)
    spec = filt.load_filter(policy.check_read("filters/v1.0.json"))
    path = run_dir / "filter-v1.0" / "decisions.jsonl"
    decisions = [json.loads(line) for line in policy.check_read(path).read_text(encoding="utf-8").splitlines()]
    sample = audit.draw_sample(decisions, spec["threshold"])
    sample = {"run": run_dir.name, "filter": "filters/v1.0.json", **sample}
    postings, _ = collection.load_run(run_dir, policy)
    jobs = {f"{board}:{job['id']}": job for board, job in postings}
    by_key = {audit.key(d): d for d in decisions}
    policy.write_text("audit/sample.json", json.dumps(sample, indent=2) + "\n")
    policy.write_text("audit/label-sheet.html", audit.label_page(sample, jobs, by_key))
    print(json.dumps({k: sample[k] for k in ("run", "seed", "sizes", "held_out_pool")}, indent=2))
    print(f"labelling sheet: {len(sample['sheet_order'])} postings in audit/label-sheet.html (blind: no verdict, score or set)")
    return 0


def filter_summary(run_dir, spec, decisions, failed):
    from collections import Counter
    count = Counter(d.verdict for d in decisions)
    lines = [f"# Filter v{spec['version']} on run {run_dir.name}", "",
             f"- Postings read from saved raw responses: {len(decisions)} (no request was made)",
             f"- keep {count[filt.KEEP]} · reject {count[filt.REJECT]} · cannot tell {count[filt.CANNOT_TELL]}",
             f"- Close calls (every gate passed, score in {spec['close_call_scores']}): {sum(d.close_call for d in decisions)}"]
    for board, reason in failed:
        lines.append(f"- Board {board} failed ({reason}): none of its postings were filtered or counted as rejected")
    lines += ["", "| Board | Postings | keep | reject | cannot tell |", "|---|---|---|---|---|"]
    for board in dict.fromkeys(d.board for d in decisions):
        c = Counter(d.verdict for d in decisions if d.board == board)
        lines.append(f"| {board} | {sum(c.values())} | {c[filt.KEEP]} | {c[filt.REJECT]} | {c[filt.CANNOT_TELL]} |")
    gate_fail = Counter(n for d in decisions for n, g in d.gates.items() if not g["passed"])
    lines += ["", "Gate failures (a posting can fail more than one): "
              + ", ".join(f"{n} {gate_fail[n]}" for n in sorted(gate_fail)), ""]
    for title, rows in (("Kept", [d for d in decisions if d.verdict == filt.KEEP]),
                        ("Close calls", [d for d in decisions if d.close_call])):
        lines += [f"## {title}", "", "| Board | Job ID | Title | Score | Verdict | Skills |", "|---|---|---|---|---|---|"]
        for d in sorted(rows, key=lambda d: -d.score):
            lines.append(f"| {d.board} | {d.job_id} | {d.title.strip()} | {d.score} | {d.verdict} | "
                         f"{', '.join(d.parts['S2 skills']['skills'])} |")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
