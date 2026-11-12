#!/usr/bin/env python3
"""watch.py — watch one Greenhouse board; report postings NEW since the last run, each
judged by the written rule (a record) and, with --claude, by Claude (a judgment).

    python3 src/watch.py --board airbnb --resume persona/aarav-patel.resume.json \
        --state runs/state.json --out runs/ [--fixture saved.json --label seeded] [--claude]

First run is a BASELINE: every id is recorded, none is reported as new.
Exit 0 = ran; 2 = bad input (résumé, host, board); 3 = fetch failed (state NOT updated).
Standard library only (the Claude judge shells out to the `claude` CLI).
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rule  # noqa: E402

ALLOWED_HOSTS = {"boards-api.greenhouse.io"}
RESUME_REQUIRED = {"personal": dict, "education": list, "experience": list, "skills": dict}


class InputError(Exception):
    pass


# ---------------------------------------------------------------- inputs
def board_url(slug):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", slug or ""):
        raise InputError(f"board slug looks wrong: {slug!r}")
    return f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"


def check_host(url):
    host = urllib.parse.urlparse(url).hostname
    if urllib.parse.urlparse(url).scheme != "https" or host not in ALLOWED_HOSTS:
        raise InputError(f"refused: host {host!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    return url


def load_resume(path):
    """Validate shape, and refuse anything that is not a fictional persona."""
    with open(path, encoding="utf-8") as f:
        resume = json.load(f)
    for key, typ in RESUME_REQUIRED.items():
        if not isinstance(resume.get(key), typ):
            raise InputError(f"résumé missing {key} ({typ.__name__})")
    email = resume["personal"].get("email", "")
    phone = resume["personal"].get("phone", "")
    if not email.endswith("@example.com") or "555" not in phone:
        raise InputError("refused: résumé is not a fictional persona (@example.com email and 555 phone required)")
    if not rule.role_keywords(resume):
        raise InputError("résumé has no experience[].title to use as a role keyword")
    return resume


def fetch(url, timeout=30):
    """One GET to an allow-listed host. Redirects are followed only to allow-listed hosts."""
    check_host(url)

    class Guard(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            check_host(newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(Guard)
    req = urllib.request.Request(url, headers={"User-Agent": "js1-contract-and-watch/1.0 (course project)"})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


# ---------------------------------------------------------------- diff
def load_state(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def diff(state, jobs):
    """Return (new_jobs, is_baseline). Baseline when there is no state yet."""
    if state is None:
        return [], True
    seen = set(state["seen_ids"])
    return [j for j in jobs if j["id"] not in seen], False


# ---------------------------------------------------------------- report
def write_report(path, run, new_judged):
    L = [f"# Watch report — {run['board']} — {run['run_at']}", "", "## Executive summary", ""]
    if run["baseline"]:
        L.append(f"First look at the {run['board']} job board: {run['postings_seen']} postings recorded. "
                 "This run is a baseline, so nothing is reported as new. The next run reports only postings that appear after this one.")
    else:
        rel = sum(1 for v in new_judged if v["rule"]["verdict"] == "relevant")
        L.append(f"{run['new']} posting(s) are new since the last run ({run['postings_seen']} on the board now). "
                 f"By the written rule, {rel} fit the persona's résumé and {run['new'] - rel} do not. "
                 "Claude's opinion is shown beside each one as a model judgment, not as a fact. You decide what to apply to.")
    L += ["", "## Run record", "",
          f"- Board: `{run['board']}` · source: {run['source']} · label: **{run['label']}**",
          f"- Raw response: `{run['raw_file']}`", f"- State: `{run['state_file']}` (previous run: {run['previous_run'] or 'none'})",
          f"- Seen {run['postings_seen']} · new {run['new']} · removed since last run {run['removed']}", ""]
    for v in new_judged:
        r, c = v["rule"], v.get("claude")
        L += [f"### {r['posting_title']} — id {r['posting_id']}", "",
              f"- **Rule verdict (RECORD):** `{r['verdict']}`" + (f" — failed {r['failed_check']}" if r["failed_check"] else ""),
              f"- URL: {v['url']}"]
        for cite in r["citations"]:
            L.append(f"  - `{cite['resume_field']}` «{cite['resume_value']}» ↔ posting `{cite['posting_field']}` «{cite['posting_text']}» — {cite['effect']}")
        if c:
            if c["status"] == "ACCEPTED":
                L.append(f"- **Claude verdict (JUDGMENT, model):** `{c['verdict']}` — {c['reason']} (fields: {', '.join(c['resume_fields'])})")
            else:
                L.append(f"- **Claude verdict (JUDGMENT, model):** REJECTED by validator — {c['reject_reason']}")
        L.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# ---------------------------------------------------------------- main
def run(args):
    resume = load_resume(args.resume)
    url = board_url(args.board)
    now = dt.datetime.now().astimezone()
    stamp = now.strftime("%Y%m%dT%H%M%S")
    os.makedirs(args.out, exist_ok=True)

    if args.fixture:
        with open(args.fixture, encoding="utf-8") as f:
            body = f.read()
        source = f"saved response {args.fixture}"
    else:
        try:
            body = fetch(url)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"fetch failed, state not updated: {e}", file=sys.stderr)
            return 3
        source = url

    raw_file = os.path.join(args.out, f"raw-{stamp}-{args.label}.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        f.write(body)
    jobs = json.loads(body)["jobs"]

    state = load_state(args.state)
    new, baseline = diff(state, jobs)
    current = {j["id"] for j in jobs}
    removed = len(set(state["seen_ids"]) - current) if state else 0

    new_judged = []
    for job in sorted(new, key=lambda j: j["id"]):
        verdict = rule.judge(job, resume)
        rule.validate_verdict(verdict, job, resume)  # a rule verdict that fails its own validator is a bug: crash
        entry = {"rule": verdict, "url": job.get("absolute_url", "")}
        if args.claude:
            import claude_judge
            entry["claude"] = claude_judge.judge(job, resume, args.prompt)
        new_judged.append(entry)

    run_rec = {"board": args.board, "run_at": now.isoformat(timespec="seconds"), "label": args.label,
               "source": source, "raw_file": os.path.relpath(raw_file), "state_file": os.path.relpath(args.state),
               "previous_run": state["runs"][-1]["run_at"] if state else None, "baseline": baseline,
               "postings_seen": len(jobs), "new": len(new), "removed": removed,
               "new_ids": sorted(j["id"] for j in new), "judged": new_judged}
    with open(os.path.join(args.out, f"run-{stamp}-{args.label}.json"), "w", encoding="utf-8") as f:
        json.dump(run_rec, f, indent=1, ensure_ascii=False)
    write_report(os.path.join(args.out, f"report-{stamp}-{args.label}.md"), run_rec, new_judged)

    # state is written last, only after everything above succeeded
    runs = (state["runs"] if state else []) + [{"run_at": run_rec["run_at"], "label": args.label,
                                                  "seen": len(jobs), "new": len(new), "raw_file": run_rec["raw_file"]}]
    os.makedirs(os.path.dirname(os.path.abspath(args.state)), exist_ok=True)
    with open(args.state, "w", encoding="utf-8") as f:
        json.dump({"board": args.board, "seen_ids": sorted(current | set(state["seen_ids"] if state else [])),
                   "runs": runs}, f, indent=1)

    print(f"{args.label}: seen {len(jobs)}, new {len(new)}, removed {removed}" + (" (BASELINE — nothing reported)" if baseline else ""))
    for e in new_judged:
        r = e["rule"]
        line = f"  {r['posting_id']}  rule={r['verdict']:<12}"
        if "claude" in e:
            line += f" claude[judgment]={e['claude']['verdict'] or e['claude']['status']}"
        print(line + f"  {r['posting_title']}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--board", required=True)
    p.add_argument("--resume", required=True)
    p.add_argument("--state", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--fixture", help="read this saved response instead of fetching (a SEEDED run)")
    p.add_argument("--label", default="live", help="run label, e.g. live, seeded")
    p.add_argument("--claude", action="store_true", help="also ask Claude (a labelled judgment) about each new posting")
    p.add_argument("--prompt", default="baseline", help="prompt contract in prompts/ for the Claude judge")
    args = p.parse_args(argv)
    if args.fixture and args.label == "live":
        p.error("a run from --fixture must carry a non-live --label (e.g. seeded)")
    try:
        return run(args)
    except InputError as e:
        print(e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
