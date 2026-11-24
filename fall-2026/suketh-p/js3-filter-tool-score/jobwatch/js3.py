"""JS3 commands. Run from the js3-filter-tool-score folder.

  python3 -m jobwatch.js3 inventory runs/2026-11-24-js3-corpus
  python3 -m jobwatch.js3 screen runs/2026-11-24-js3-corpus --out audit/v0.1

Both read only the saved run; neither touches the network. `screen` prints counts only and
writes every posting's record to the --out folder (audit.jsonl, AUDIT-VIEW.md, SUMMARY.md)."""

import argparse
import collections
import json
import sys
from pathlib import Path

from jobwatch import corpus, location, screen
from jobwatch.normalize import tokens

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# The student's dated prediction (FILTER.md, "Additions before the build").
EXPECTED = {"greenhouse/anthropic": 635, "greenhouse/databricks": 895, "ashby/linear": 32}


def _md_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def inventory(run_dir):
    items, boards = corpus.load(run_dir)
    lines = ["# Corpus inventory", "",
             f"Run `{Path(run_dir).name}`, read by `python3 -m jobwatch.js3 inventory {run_dir}`.",
             "Expected counts are the student's prediction in FILTER.md, made before the run.", "",
             "| Board | Expected | Collected | Collected − expected | Captured (UTC) | Failure |",
             "| --- | ---: | ---: | ---: | --- | --- |"]
    for b in boards:
        expected = EXPECTED.get(b["board"])
        diff = (b["count"] - expected) if (b["count"] is not None and expected is not None) else "unknown"
        lines.append(f"| {b['board']} | {expected} | {b['count'] if b['count'] is not None else 'unknown'} "
                     f"| {diff} | {b.get('captured_at', '')} | {b['failure'] or ''} |")
    by_board = collections.defaultdict(list)
    for item in items:
        by_board[item.board].append(item)
    lines += ["", "## The listed fields", "",
              "| Board | Postings | Blank title | Blank location | Blank description after decoding |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for name, group in by_board.items():
        lines.append(f"| {name} | {len(group)} | {sum(not i.title.strip() for i in group)} "
                     f"| {sum(not i.location.strip() for i in group)} "
                     f"| {sum(not tokens(i.description) for i in group)} |")
    lines += ["", "## Fields the boards sent that FILTER.md does not list", "",
              "Counts are postings where the field is present and not empty.", ""]
    for b in boards:
        if b["count"] is None:
            continue
        ats_name = b["board"].split("/")[0]
        jobs = corpus.raw_jobs(run_dir, b["board"])
        counts = collections.Counter(k for job in jobs for k, v in job.items()
                                     if k not in corpus.LISTED_FIELDS[ats_name] and v not in (None, "", [], {}))
        listed = ", ".join(f"`{k}` {n}" for k, n in sorted(counts.items()))
        lines.append(f"- **{b['board']}** ({len(jobs)} postings): {listed}")
    lines += ["", "## Location fields that the location rule does not read", "",
              "\"Would change\" counts postings whose location outcome (us / outside / unresolved) would differ "
              "if the unread fields were added to the text the U.S. test reads. This only measures the gap; "
              "the filter does not read these fields.", ""]
    for b in boards:
        if b["count"] is None:
            continue
        jobs = corpus.raw_jobs(run_dir, b["board"])
        if b["board"].startswith("ashby/"):
            secondary = sum(bool(j.get("secondaryLocations")) for j in jobs)
            remote = sum(j.get("isRemote") is True for j in jobs)
            workplace = collections.Counter(str(j.get("workplaceType")) for j in jobs)
            countries = collections.Counter(
                str(((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry")) for j in jobs)
            changes = collections.Counter()
            for j in jobs:
                extra = [s.get("location", "") for s in (j.get("secondaryLocations") or []) if isinstance(s, dict)]
                extra.append(str(((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry") or ""))
                before = location.classify(j.get("location") or "")["outcome"]
                after = location.classify(" | ".join([j.get("location") or ""] + extra))["outcome"]
                if before != after:
                    changes[f"{before} → {after}"] += 1
            lines.append(f"- **{b['board']}**: `secondaryLocations` not empty in {secondary}; `isRemote` true in "
                         f"{remote}; `workplaceType` {dict(workplace)}; `address.postalAddress.addressCountry` "
                         f"{dict(countries)}. Adding `secondaryLocations` and `addressCountry` would change "
                         f"{sum(changes.values())} outcomes: {dict(changes) or 'none'}")
        else:
            multi = sum(len(j.get("offices") or []) > 1 for j in jobs)
            changes = collections.Counter()
            for j in jobs:
                text = (j.get("location") or {}).get("name") or ""
                offices = [f"{o.get('name') or ''} {o.get('location') or ''}" for o in (j.get("offices") or [])]
                before = location.classify(text)["outcome"]
                after = location.classify(" | ".join([text] + offices))["outcome"]
                if before != after:
                    changes[f"{before} → {after}"] += 1
            lines.append(f"- **{b['board']}**: more than one entry in `offices` in {multi}. Adding the office "
                         f"names and locations would change {sum(changes.values())} outcomes: "
                         f"{dict(changes) or 'none'}")
    text = "\n".join(lines) + "\n"
    print(text)
    return text


def screen_run(run_dir, out_dir):
    items, boards = corpus.load(run_dir)
    records = [screen.score(item) for item in items]
    ranked = screen.rank(records)
    position = {(r["board"], r["key"]): n for n, r in enumerate(ranked, start=1)}
    for record in records:
        record["rank"] = position.get((record["board"], record["key"]))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "audit.jsonl", "w", encoding="utf-8") as fh:
        for record in sorted(records, key=lambda r: (r["rank"] is None, r["rank"] or 0, r["board"], r["key"])):
            fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")

    fates = collections.Counter(r["fate"] for r in records)
    by_board = collections.Counter((r["board"], r["fate"]) for r in records)
    reasons = collections.Counter(reason for r in records for reason in r["reasons"])
    review = collections.Counter(reason for r in records if r["fate"] == "review" for reason in r["review_reasons"])
    scores = collections.Counter((r["score"], r["fate"]) for r in records)
    where = collections.Counter(r["location"]["outcome"] for r in records)
    summary = [f"# Audit view summary — FILTER.md {screen.FILTER_VERSION}", "",
               f"Run `{Path(run_dir).name}`, {len(records)} postings, screened by "
               f"`python3 -m jobwatch.js3 screen {run_dir} --out {out_dir}`.", "",
               "| Fate | Postings |", "| --- | ---: |"]
    summary += [f"| {fate} | {fates.get(fate, 0)} |" for fate in ("kept", "review", "rejected")]
    summary += ["", "| Board | kept | review | rejected |", "| --- | ---: | ---: | ---: |"]
    for b in boards:
        summary.append(f"| {b['board']} | {by_board[(b['board'], 'kept')]} | {by_board[(b['board'], 'review')]} "
                       f"| {by_board[(b['board'], 'rejected')]} |")
    summary += ["", "Rejection reasons (a posting can have several): " +
                ", ".join(f"{k} {v}" for k, v in sorted(reasons.items())),
                "", "Review reasons: " + ", ".join(f"{k} {v}" for k, v in sorted(review.items())),
                "", "Location outcomes, all postings: " + ", ".join(f"{k} {v}" for k, v in sorted(where.items())),
                "", "| Score | kept | review | rejected |", "| ---: | ---: | ---: | ---: |"]
    for s in sorted({s for s, _ in scores}):
        summary.append(f"| {s} | {scores[(s, 'kept')]} | {scores[(s, 'review')]} | {scores[(s, 'rejected')]} |")
    (out / "SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    view = [f"# Audit view — every posting, FILTER.md {screen.FILTER_VERSION}", "",
            "Ranked postings first (kept and review, in rank order), then every rejected posting. "
            "Score = role + title topic + description topic.", "",
            "| Rank | Board | Key | Title | Location → outcome | Score | Matched | Fate | Reasons |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for record in sorted(records, key=lambda r: (r["rank"] is None, r["rank"] or 0, r["board"], r["key"])):
        p, m = record["parts"], record["matched"]
        matched = "; ".join(f"{k}: {', '.join(v)}" for k, v in m.items() if v)
        why = ", ".join(record["reasons"] + record["review_reasons"])
        view.append(f"| {record['rank'] or ''} | {record['board']} | {_md_cell(record['key'])} | "
                    f"{_md_cell(record['title'])} | {_md_cell(record['location']['text'])} → "
                    f"{record['location']['outcome']} | {record['score']} ({p['role']}+{p['title_topic']}+"
                    f"{p['description_topic']}) | {_md_cell(matched)} | {record['fate']} | {why} |")
    (out / "AUDIT-VIEW.md").write_text("\n".join(view) + "\n", encoding="utf-8")
    print("\n".join(summary))
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m jobwatch.js3")
    commands = parser.add_subparsers(dest="command", required=True)
    inv = commands.add_parser("inventory", help="expected versus collected, and the fields the boards sent")
    inv.add_argument("run_dir")
    inv.add_argument("--out", help="also write the inventory to this file")
    scr = commands.add_parser("screen", help="run FILTER.md on every posting; write the audit view")
    scr.add_argument("run_dir")
    scr.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.command == "inventory":
        text = inventory(args.run_dir)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(text, encoding="utf-8")
        return 0
    if args.command == "screen":
        screen_run(args.run_dir, args.out)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
