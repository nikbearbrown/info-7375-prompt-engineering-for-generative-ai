"""Watch one public Greenhouse board and report only postings new since the last run.

    python3 watch.py run [--from-file RAW --label LABEL] [--claude]
    python3 watch.py validate-claude RUN_DIR

See README.md for the full commands and CONTRACT.md for what this may and may not do.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

import judge
import persona
import rule

HERE = os.path.dirname(os.path.abspath(__file__))
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
BOARD = "abacusinsights"
BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
# v2 won the prompt experiment (PROMPT_EXPERIMENT.md). Run 2026-10-31T175126Z was recorded with v1.
PROMPT = os.path.join(HERE, "prompts", "v2_path_syntax.txt")


class RefusedHost(Exception):
    pass


class RefusedPath(Exception):
    pass


def check_allowed(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
        raise RefusedHost(f"refusing {url}: host {parts.hostname!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")


class _AllowListRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_allowed(newurl)  # a redirect may not leave the allow-list either
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url):
    check_allowed(url)
    opener = urllib.request.build_opener(_AllowListRedirect)
    request = urllib.request.Request(url, headers={"User-Agent": "info7375-js1-watch (read-only)"})
    with opener.open(request, timeout=30) as response:
        return response.read()


def _inside(path, root):
    path, root = os.path.realpath(path), os.path.realpath(root)
    if os.path.commonpath([path, root]) != root:
        raise RefusedPath(f"refusing to write {path}: outside {root}")
    return path


def load_state(state_path):
    if not os.path.exists(state_path):
        return None
    with open(state_path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def _write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def run(board=BOARD, runs_dir=None, state_path=None, persona_path=None, from_file=None,
        label=None, use_claude=False, now=None, allowed_root=HERE):
    runs_dir = _inside(runs_dir or os.path.join(HERE, "runs"), allowed_root)
    state_path = _inside(state_path or os.path.join(HERE, "state", "seen_ids.json"), allowed_root)
    resume = persona.load(persona_path or os.path.join(HERE, "persona", "resume.json"))
    problems = persona.validate(resume)
    if problems:
        raise ValueError("persona résumé failed validation: " + "; ".join(problems))

    url = BOARD_URL.format(board=board)
    if from_file:
        with open(from_file, "rb") as f:
            raw = f.read()
    else:
        raw = fetch(url)
    jobs = json.loads(raw)["jobs"]

    now = now or dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H%M%SZ")
    run_dir = os.path.join(runs_dir, stamp + (f"_{label}" if label else ""))
    os.makedirs(run_dir, exist_ok=False)
    with open(os.path.join(run_dir, "raw.json"), "wb") as f:
        f.write(raw)

    state = load_state(state_path)
    baseline = state is None
    seen = set() if baseline else set(state["seen_ids"])
    new = [] if baseline else [j for j in jobs if j["id"] not in seen]

    rule_records = [rule.judge(j, resume) for j in new]
    _write_jsonl(os.path.join(run_dir, "rule_verdicts.jsonl"), rule_records)
    prompt_dir = os.path.join(run_dir, "claude_prompts")
    os.makedirs(prompt_dir)
    for j in new:
        with open(os.path.join(prompt_dir, f"{j['id']}.txt"), "w", encoding="utf-8") as f:
            f.write(judge.build_prompt(PROMPT, j, resume))
    if use_claude and new:
        raw_dir = os.path.join(run_dir, "claude_raw")
        os.makedirs(raw_dir)
        for j in new:
            with open(os.path.join(raw_dir, f"{j['id']}.txt"), "w", encoding="utf-8") as f:
                f.write(judge.call_cli(judge.build_prompt(PROMPT, j, resume)))

    meta = {
        "run": os.path.basename(run_dir),
        "started_at": now.isoformat(),
        "board": board,
        "source": f"file {os.path.relpath(from_file, HERE)}" if from_file else f"live {url}",
        "label": label,
        "baseline": baseline,
        "postings_in_response": len(jobs),
        "seen_before_run": len(seen),
        "new_ids": [j["id"] for j in new],
    }
    _write_json(os.path.join(run_dir, "run.json"), meta)

    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    history = [] if baseline else state["runs"]
    _write_json(state_path, {
        "board": board,
        "seen_ids": sorted(seen | {j["id"] for j in jobs}),
        "runs": history + [{"run": meta["run"], "label": label, "baseline": baseline, "new": len(new)}],
    })
    validate_claude(run_dir, resume)
    return run_dir, meta


def validate_claude(run_dir, resume=None):
    """Validate whatever raw Claude outputs exist for a run, however they were produced,
    and write claude_verdicts.jsonl plus the run's report.md."""
    resume = resume or persona.load(os.path.join(HERE, "persona", "resume.json"))
    with open(os.path.join(run_dir, "raw.json"), "rb") as f:
        jobs = {j["id"]: j for j in json.loads(f.read())["jobs"]}
    with open(os.path.join(run_dir, "run.json"), encoding="utf-8") as f:
        meta = json.load(f)
    raw_dir = os.path.join(run_dir, "claude_raw")
    claude_records = []
    for pid in meta["new_ids"]:
        path = os.path.join(raw_dir, f"{pid}.txt")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            out = f.read()
        verdict, errors = judge.validate(out, jobs[pid], resume)
        claude_records.append({
            "posting_id": pid, "judge": "claude", "kind": "judgment", "valid": not errors,
            "verdict": verdict["verdict"] if verdict else None,
            "cites": verdict["cites"] if verdict else None,
            "reason": verdict["reason"] if verdict else None,
            "errors": errors, "raw_file": os.path.relpath(path, run_dir),
        })
    _write_jsonl(os.path.join(run_dir, "claude_verdicts.jsonl"), claude_records)
    _write_report(run_dir, meta, jobs, claude_records)
    return claude_records


def _write_report(run_dir, meta, jobs, claude_records):
    with open(os.path.join(run_dir, "rule_verdicts.jsonl"), encoding="utf-8") as f:
        rules = {r["posting_id"]: r for r in map(json.loads, f)}
    by_claude = {c["posting_id"]: c for c in claude_records}
    lines = [f"# Run {meta['run']}", ""]
    if meta["label"]:
        lines += [f"**Label: {meta['label']}.** See `run.json` for the source of this response.", ""]
    lines += [f"- Source: {meta['source']}", f"- Postings in response: {meta['postings_in_response']}",
              f"- Seen before this run: {meta['seen_before_run']}",
              f"- Baseline: {'yes, so nothing is reported as new' if meta['baseline'] else 'no'}",
              f"- New postings: {len(meta['new_ids'])}", ""]
    if meta["new_ids"]:
        lines += ["| Posting | Title | Rule verdict (record) | Claude verdict (judgment) |", "|---|---|---|---|"]
        for pid in meta["new_ids"]:
            c = by_claude.get(pid)
            claude_cell = "not run" if c is None else (c["verdict"] if c["valid"] else "invalid output, rejected")
            lines.append(f"| {pid} | {jobs[pid]['title']} | {rules[pid]['verdict']} | {claude_cell} |")
        lines += ["", "Rule verdicts are records: recompute them with `rule.py`. Claude verdicts are judgments, "
                      "not facts. Justifications are in `rule_verdicts.jsonl` and `claude_verdicts.jsonl`."]
    with open(os.path.join(run_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p_run = sub.add_parser("run", help="fetch (or load) the board and report new postings")
    p_run.add_argument("--from-file", help="use a saved response instead of fetching; requires --label")
    p_run.add_argument("--label", help='label for this run, for example "seeded-baseline"')
    p_run.add_argument("--state", help="state file inside state/ (default state/seen_ids.json)")
    p_run.add_argument("--claude", action="store_true", help="also ask Claude via `claude -p` (needs a logged-in CLI)")
    p_val = sub.add_parser("validate-claude", help="validate raw Claude outputs saved in RUN_DIR/claude_raw/")
    p_val.add_argument("run_dir")
    args = parser.parse_args(argv)
    if args.command == "run":
        if args.from_file and not args.label:
            parser.error("--from-file needs --label so a seeded run is never mistaken for a live one")
        state_path = os.path.join(HERE, args.state) if args.state else None
        run_dir, meta = run(state_path=state_path, from_file=args.from_file, label=args.label, use_claude=args.claude)
        print(f"{meta['run']}: {meta['postings_in_response']} postings, "
              f"{'baseline' if meta['baseline'] else str(len(meta['new_ids'])) + ' new'} -> {os.path.relpath(run_dir, HERE)}/report.md")
    else:
        records = validate_claude(os.path.abspath(args.run_dir))
        print(f"{sum(r['valid'] for r in records)} valid, {sum(not r['valid'] for r in records)} rejected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
