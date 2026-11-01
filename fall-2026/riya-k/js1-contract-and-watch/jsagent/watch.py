"""The watch: fetch one Greenhouse board, save the raw response, report only postings new since last run.

    python3 -m jsagent.watch --board databricks --resume persona/arya-sahni.json \
        --state runs/databricks.state.json --out runs/ [--fixture FILE --label seeded] [--claude]
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import rules
from .contract import ContractError, validate_resume, validate_verdict

ALLOWED_HOSTS = {"boards-api.greenhouse.io"}


def board_url(board):
    return f"https://boards-api.greenhouse.io/v1/boards/{urllib.parse.quote(board)}/jobs?content=true"


def fetch(url):
    host = urllib.parse.urlparse(url).hostname
    if urllib.parse.urlparse(url).scheme != "https" or host not in ALLOWED_HOSTS:
        raise ContractError(f"refused: host {host!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    req = urllib.request.Request(url, headers={"User-Agent": "INFO7375-js1-student-watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def load_state(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else {"board": None, "seen_ids": [], "runs": []}


def new_postings(jobs, seen_ids):
    """Postings whose id was never seen. Keyed by id only, never by title or position."""
    seen = set(seen_ids)
    return [j for j in jobs if j["id"] not in seen]


def attach_verdicts(postings, judge_fn):
    """One verdict per posting, each checked against its own posting id."""
    out = []
    for p in postings:
        v = judge_fn(p)
        validate_verdict(v, p["id"])
        out.append(v)
    return out


def unused_path(path):
    """Evidence is never overwritten: two runs in the same second get -2, -3, ... suffixes."""
    n, candidate = 1, path
    while candidate.exists():
        n += 1
        candidate = path.with_name(f"{path.stem}-{n}{path.suffix}")
    return candidate


def run(board, resume_path, state_path, out_dir, fixture=None, label="live", use_claude=False, now=None):
    resume = validate_resume(json.loads(Path(resume_path).read_text()))
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    out = Path(out_dir)
    (out / "raw").mkdir(parents=True, exist_ok=True)

    url = board_url(board)
    raw = Path(fixture).read_bytes() if fixture else fetch(url)
    raw_path = unused_path(out / "raw" / f"{board}-{stamp}-{label}.json")
    raw_path.write_bytes(raw)
    jobs = json.loads(raw)["jobs"]

    state = load_state(state_path)
    baseline = not state["seen_ids"]
    fresh = [] if baseline else new_postings(jobs, state["seen_ids"])
    current_ids = {j["id"] for j in jobs}
    removed = sorted(set(state["seen_ids"]) - current_ids)

    rule_verdicts = attach_verdicts(fresh, lambda p: rules.judge(p, resume))
    claude_verdicts = []
    if use_claude:
        from . import claude_judge
        for p in fresh:
            v, reply, err = claude_judge.judge(p, resume)
            if v:
                v.update(title=p.get("title", ""), location=(p.get("location") or {}).get("name", ""),
                         url=p.get("absolute_url", ""))
            claude_verdicts.append(v or {"id": p["id"], "judge": "claude", "kind": "judgment",
                                         "rejected": err, "raw_reply": reply})

    record = {
        "run_at": now.isoformat(timespec="seconds"), "label": label, "board": board,
        "source": fixture or url, "raw_response": str(raw_path), "baseline": baseline,
        "postings_on_board": len(jobs), "new": len(fresh), "removed_since_last": len(removed),
        "rule_verdicts": rule_verdicts, "claude_verdicts": claude_verdicts,
    }
    report_path = unused_path(out / f"report-{stamp}-{label}.json")
    report_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    report_path.with_suffix(".md").write_text(markdown(record))

    state["board"] = board
    state["seen_ids"] = sorted(set(state["seen_ids"]) | current_ids)
    state["runs"].append({"run_at": record["run_at"], "label": label, "raw_response": str(raw_path),
                          "postings_on_board": len(jobs), "new": len(fresh), "baseline": baseline})
    Path(state_path).write_text(json.dumps(state, indent=1) + "\n")
    return record


def markdown(r):
    lines = [f"# Watch report: {r['board']} ({r['label']})", "",
             f"- Run at: {r['run_at']}", f"- Source: `{r['source']}`", f"- Raw response: `{r['raw_response']}`",
             f"- Postings on board: {r['postings_on_board']}",
             f"- New since last run: {'baseline run, none reported' if r['baseline'] else r['new']}",
             f"- Removed since last run: {r['removed_since_last']}", ""]
    if r["rule_verdicts"]:
        claude = {v["id"]: v for v in r["claude_verdicts"]}
        lines += ["| id | title | rule verdict (record) | Claude verdict (judgment) |", "|---|---|---|---|"]
        for v in r["rule_verdicts"]:
            c = claude.get(v["id"])
            cv = "not run" if c is None else c.get("verdict", "REJECTED by validator")
            lines.append(f"| {v['id']} | {v['title']} | {v['verdict']} | {cv} |")
        lines += ["", "## Justifications", ""]
        for v in r["rule_verdicts"]:
            lines.append(f"- **{v['id']}** rule (record): {v['justification']}")
            c = claude.get(v["id"])
            if c and "verdict" in c:
                lines.append(f"  - Claude (judgment, not a fact): {c['justification']}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--board", required=True)
    ap.add_argument("--resume", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fixture", help="read a saved response instead of fetching (label the run 'seeded')")
    ap.add_argument("--label", default=None)
    ap.add_argument("--claude", action="store_true", help="also ask Claude for a judgment on each new posting")
    a = ap.parse_args(argv)
    label = a.label or ("seeded" if a.fixture else "live")
    try:
        r = run(a.board, a.resume, a.state, a.out, a.fixture, label, a.claude)
    except ContractError as e:
        sys.exit(f"REFUSED: {e}")
    print(f"{r['run_at']} {r['board']} [{r['label']}]: {r['postings_on_board']} on board, "
          + ("baseline (none reported as new)" if r["baseline"] else f"{r['new']} new"))
    for v in r["rule_verdicts"]:
        print(f"  {v['id']}  {v['verdict']:<13} {v['title']}")


if __name__ == "__main__":
    main()
