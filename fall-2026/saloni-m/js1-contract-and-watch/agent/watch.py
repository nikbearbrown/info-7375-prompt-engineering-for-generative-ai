"""The watch: allow-listed fetch, raw evidence, new-since-last-run by posting id.

Usage (from this folder):
    python3 -m agent.watch --resume personas/priya-nair.resume.json
    python3 -m agent.watch --resume ... --from-file evidence/raw/<saved>.json --label seeded
    python3 -m agent.watch --resume ... --claude          # also ask Claude (a judgment)
"""
import argparse
import datetime as dt
import json
import os
import urllib.parse
import urllib.request

from agent.resume import load_resume
from agent.rule import judge_rule

ALLOWED_HOSTS = {"boards-api.greenhouse.io"}
USER_AGENT = "INFO7375-JS1-student-watcher/1.0 (one GET per run; no login)"


class HostNotAllowed(PermissionError):
    pass


def board_url(board):
    return f"https://boards-api.greenhouse.io/v1/boards/{urllib.parse.quote(board)}/jobs?content=true"


def check_allowed(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
        raise HostNotAllowed(f"refused: {parts.hostname!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")


def fetch(url, opener=urllib.request.urlopen):
    check_allowed(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener(req, timeout=30) as resp:
        return resp.read()


def load_state(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def diff_new(postings, state):
    """Return postings whose id is not in state. A missing state is a baseline: nothing is new."""
    if state is None:
        return []
    seen = set(state["seen_ids"])
    return [p for p in postings if p["id"] not in seen]


def update_state(postings, state, run_meta):
    seen = set(state["seen_ids"]) if state else set()
    seen.update(p["id"] for p in postings)
    runs = (state or {}).get("runs", []) + [run_meta]
    return {"board": run_meta["board"], "seen_ids": sorted(seen), "runs": runs}


def judge_all(new_postings, resume, with_claude=False, prompt_path=None):
    results = []
    for posting in new_postings:
        entry = {"id": posting["id"], "title": posting.get("title"), "rule": judge_rule(posting, resume)}
        if with_claude:
            from agent.claude_judge import judge_claude
            entry["claude"] = judge_claude(posting, resume, prompt_path=prompt_path)
        results.append(entry)
    return results


def print_report(report):
    print(f"run {report['run']['run_id']} ({report['run']['label']}): "
          f"{report['run']['postings']} postings, {len(report['new'])} new")
    for e in report["new"]:
        r = e["rule"]
        print(f"- [{e['id']}] {e['title']}")
        print(f"    Rule (record):     {r['verdict']:<13} cites {r['resume_fields']} + {r['posting_fields']}: {r['reason']}")
        if "claude" in e:
            c = e["claude"]
            if c["status"] == "ok":
                print(f"    Claude (judgment): {c['verdict']:<13} cites {c['resume_fields']} + {c['posting_fields']}: {c['reason']}")
            else:
                print(f"    Claude (judgment): REJECTED by validator: {c['error']}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default="anthropic")
    ap.add_argument("--resume", required=True)
    ap.add_argument("--state", default="state/seen_ids.json")
    ap.add_argument("--evidence", default="evidence/raw")
    ap.add_argument("--reports", default="evidence/reports")
    ap.add_argument("--from-file", help="use a saved raw response instead of fetching (label the run)")
    ap.add_argument("--label", default="live")
    ap.add_argument("--claude", action="store_true")
    ap.add_argument("--prompt", default="prompts/v1_baseline.md")
    args = ap.parse_args(argv)

    resume = load_resume(args.resume)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    url = board_url(args.board)

    if args.from_file:
        with open(args.from_file, "rb") as f:
            raw = f.read()
        source = args.from_file
    else:
        raw = fetch(url)
        os.makedirs(args.evidence, exist_ok=True)
        source = os.path.join(args.evidence, f"{args.board}-{run_id}.json")
        with open(source, "wb") as f:
            f.write(raw)

    postings = json.loads(raw)["jobs"]
    state = load_state(args.state)
    new = diff_new(postings, state)
    meta = {"run_id": run_id, "board": args.board, "url": url, "label": args.label,
            "source": source, "postings": len(postings), "new": len(new), "baseline": state is None}

    report = {"run": meta, "new": judge_all(new, resume, args.claude, args.prompt)}
    os.makedirs(os.path.dirname(args.state) or ".", exist_ok=True)
    with open(args.state, "w", encoding="utf-8") as f:
        json.dump(update_state(postings, state, meta), f, indent=2)
    os.makedirs(args.reports, exist_ok=True)
    with open(os.path.join(args.reports, f"run-{run_id}-{args.label}.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print_report(report)
    return report


if __name__ == "__main__":
    main()
