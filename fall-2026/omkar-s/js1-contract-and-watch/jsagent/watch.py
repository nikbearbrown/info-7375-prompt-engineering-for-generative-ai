"""The watch: fetch one board, save the raw response, report only postings new since
the last run, and judge each new one twice (rule = record, Claude = judgment).

    python3 -m jsagent.watch --board klaviyo --resume persona/aarav-patel.example.json \
        --state runs/klaviyo.state.json --out runs/ [--fixture FILE] [--claude]

The first run (no state file) is a baseline: it records every id and reports none.
--fixture replays a saved response instead of fetching; that run is labelled SEEDED.
"""
import argparse
import datetime as _dt
import json
import os
import shutil
import sys

from . import claude_judge, fetch, persona, rule


def load_state(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_state(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, path)


def diff_new(postings, state):
    """Postings whose id is not in the state's seen set. No state = baseline = none new."""
    if state is None:
        return []
    seen = set(state["seen_ids"])
    return [p for p in postings if p["id"] not in seen]


def attach_verdicts(new_postings, resume):
    """One record per new posting, keyed by that posting's own id."""
    return [{"posting_id": p["id"], "title": p.get("title"), "absolute_url": p.get("absolute_url"),
             "rule": rule.judge(p, resume)} for p in new_postings]


def run(board, resume_path, state_path, out_dir, fixture=None, use_claude=False,
        prompt_path=None, now=None, claude_caller=None):
    resume = persona.load(resume_path)  # refuses a non-fictional résumé before any I/O
    now = now or _dt.datetime.now(_dt.timezone.utc)
    run_id = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    os.makedirs(out_dir, exist_ok=True)

    raw_path = os.path.join(out_dir, f"raw-{board}-{run_id}.json")
    if fixture:
        shutil.copyfile(fixture, raw_path)
        source = {"type": "seeded", "fixture": fixture,
                  "note": "SEEDED: replayed a saved earlier response; no network request was made"}
    else:
        url = fetch.board_url(board)
        body, status = fetch.fetch(url)
        with open(raw_path, "wb") as f:
            f.write(body)
        source = {"type": "live", "url": url, "http_status": status}
    with open(raw_path, encoding="utf-8") as f:
        postings = json.load(f)["jobs"]

    state = load_state(state_path)
    baseline = state is None
    new = diff_new(postings, state)
    records = attach_verdicts(new, resume)

    if use_claude and records:
        with open(prompt_path, encoding="utf-8") as f:
            template = f.read()
        by_id = {p["id"]: p for p in new}
        for r in records:
            r["claude"] = claude_judge.judge(
                by_id[r["posting_id"]], resume, template,
                caller=claude_caller or claude_judge.call_claude,
                raw_dir=os.path.join(out_dir, "claude-raw"), tag=f"{run_id}-")

    current_ids = sorted(p["id"] for p in postings)
    prev_ids = set(state["seen_ids"]) if state else set()
    removed = sorted(prev_ids - set(current_ids))
    if state is None:
        state = {"board": board, "seen_ids": [], "runs": []}
    state["seen_ids"] = sorted(prev_ids | set(current_ids))
    state["runs"].append({"run_id": run_id, "source": source["type"], "raw": os.path.basename(raw_path),
                          "postings": len(postings), "new": len(records), "baseline": baseline})
    save_state(state_path, state)

    result = {"run_id": run_id, "board": board, "baseline": baseline, "source": source,
              "raw_response": os.path.basename(raw_path), "postings_in_response": len(postings),
              "new_since_last_run": len(records), "removed_since_last_run": removed,
              "resume": os.path.basename(resume_path), "records": records}
    stem = os.path.join(out_dir, f"run-{board}-{run_id}{'-baseline' if baseline else ''}")
    with open(stem + ".json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    with open(stem + ".md", "w", encoding="utf-8") as f:
        f.write(render(result))
    return result


def render(result):
    kind = "BASELINE" if result["baseline"] else "WATCH"
    src = result["source"]
    lines = [f"# {result['board']} — {kind} run {result['run_id']}", ""]
    if src["type"] == "seeded":
        lines += [f"> **{src['note']}** (`{src['fixture']}`).", ""]
    else:
        lines += [f"> Live fetch of `{src['url']}` (HTTP {src['http_status']}).", ""]
    lines += [f"- Raw response saved: `{result['raw_response']}`",
              f"- Postings in response: {result['postings_in_response']}",
              f"- New since last run: **{result['new_since_last_run']}**"
              + (" (baseline: every id recorded, none reported)" if result["baseline"] else ""),
              f"- Removed since last run: {len(result['removed_since_last_run'])}", ""]
    for r in result["records"]:
        lines += [f"## {r['title']} (`{r['posting_id']}`)", f"<{r['absolute_url']}>", "",
                  f"**Record — written rule (recomputable): {r['rule']['verdict']}**", ""]
        lines += [f"- {j}" for j in r["rule"]["justification"]]
        c = r.get("claude")
        if c:
            lines += ["", f"**Judgment — {c['label']} ({', '.join(c['models']) or 'model unknown'},"
                          f" asked {c['asked_at']}): "
                          + (c["verdict"] if c["status"] == "valid" else f"REJECTED by validator: {c['rejection']}")
                          + "**", ""]
            if c["status"] == "valid":
                lines += [f"- cites résumé: {', '.join(c['resume_fields'])}",
                          f"- cites posting: {', '.join(c['posting_fields'])}",
                          f"- reason (Claude's words): {c['reason']}",
                          f"- agrees with the record: {'yes' if c['verdict'] == r['rule']['verdict'] else 'NO'}"]
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", required=True)
    ap.add_argument("--resume", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fixture", help="replay a saved response (SEEDED run) instead of fetching")
    ap.add_argument("--claude", action="store_true", help="also ask Claude (judgment) for each new posting")
    ap.add_argument("--prompt", default="prompts/baseline.txt")
    a = ap.parse_args(argv)
    try:
        res = run(a.board, a.resume, a.state, a.out, fixture=a.fixture, use_claude=a.claude, prompt_path=a.prompt)
    except (fetch.RefusedFetch, persona.RefusedResume) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    print(render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
