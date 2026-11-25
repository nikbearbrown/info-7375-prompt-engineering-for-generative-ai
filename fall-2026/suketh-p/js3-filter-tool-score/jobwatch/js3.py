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


def labels_sheet(run_dir, audit_path, out_dir):
    import hashlib

    from jobwatch import label_page, sample

    records = [json.loads(line) for line in open(audit_path, encoding="utf-8")]
    members = sample.draw(records)
    items, boards = corpus.load(run_dir)
    by_key = {(i.board, i.key): i for i in items}
    urls = {}
    for b in boards:
        if b["count"] is None:
            continue
        for job in corpus.raw_jobs(run_dir, b["board"]):
            key = str(job.get("id")) if b["board"].startswith("greenhouse/") else job.get("jobUrl")
            urls[(b["board"], key)] = job.get("absolute_url") or job.get("jobUrl") or ""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sheet = {"filter_version": screen.FILTER_VERSION, "audit": str(audit_path), "run": Path(run_dir).name,
             "seed": sample.SEED, "shuffle_seed": sample.SHUFFLE_SEED, "sizes": sample.SIZES,
             "members": members}
    text = json.dumps(sheet, indent=1, ensure_ascii=False) + "\n"
    (out / "v0.1-sample.json").write_text(text, encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    (out / "LABEL-POSTINGS.html").write_text(label_page.build(members, by_key, urls, sha), encoding="utf-8")
    counts = collections.Counter(m["stratum"] for m in members)
    print(f"{len(members)} postings drawn (seed {sample.SEED}); sample sha256 {sha}")
    for stratum, size in sample.SIZES.items():
        print(f"  {stratum:36} {counts[stratum]:3}  (pool {next(m['pool_size'] for m in members if m['stratum'] == stratum)})")
    return members


def draft_claims(run_dir, audit_path, top, out_dir, model):
    import datetime
    import hashlib

    from jobwatch import claims

    records = [json.loads(line) for line in open(audit_path, encoding="utf-8")]
    shortlist = sorted((r for r in records if r.get("rank") and r["rank"] <= top), key=lambda r: r["rank"])
    items, _ = corpus.load(run_dir)
    by_key = {(i.board, i.key): i for i in items}
    out = Path(out_dir)
    (out / "claude").mkdir(parents=True, exist_ok=True)
    (out / "shortlist.json").write_text(json.dumps(
        [{"rank": r["rank"], "board": r["board"], "key": r["key"], "score": r["score"], "fate": r["fate"]}
         for r in shortlist], indent=1) + "\n", encoding="utf-8")
    system, _ = claims.prompt_parts()
    send = claims.claude_code_send(model)
    rows, failures = [], 0
    for r in shortlist:
        item = by_key[(r["board"], r["key"])]
        system, user = claims.build_prompt(item)
        started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        result = send(system, user)
        ended = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        saved = {"rank": r["rank"], "board": r["board"], "key": r["key"], "started": started, "ended": ended,
                 "prompt_file": "prompts/claims-v1.md",
                 "prompt_sha256": hashlib.sha256(claims.PROMPT_PATH.read_bytes()).hexdigest(),
                 "user_message_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
                 "command": [c if c != system else "<prompts/claims-v1.md, # System>" for c in result["command"]],
                 "returncode": result["returncode"], "stdout": result["stdout"], "stderr": result["stderr"]}
        (out / "claude" / f"rank-{r['rank']:02d}.json").write_text(json.dumps(saved, indent=1, ensure_ascii=False) + "\n",
                                                                  encoding="utf-8")
        try:
            drafted = claims.parse_reply(result["stdout"])
        except claims.ClaimsError as error:
            failures += 1
            print(f"rank {r['rank']}: no claims ({error})")
            continue
        for row in claims.checked(item, drafted):
            row["rank"] = r["rank"]
            rows.append(row)
        print(f"rank {r['rank']}: {len(drafted)} claims")
    with open(out / "claims.jsonl", "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    checks = collections.Counter(row["quote_check"] for row in rows)
    print(f"{len(shortlist)} postings, {failures} failed replies, {len(rows)} claims; quote check: {dict(checks)}")


def claims_sheet(run_dir, shortlist_dir):
    import hashlib

    from jobwatch import label_page

    out = Path(shortlist_dir)
    shortlist = json.loads((out / "shortlist.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in open(out / "claims.jsonl", encoding="utf-8")]
    items, boards = corpus.load(run_dir)
    by_key = {(i.board, i.key): i for i in items}
    urls = {}
    for b in boards:
        if b["count"] is None:
            continue
        for job in corpus.raw_jobs(run_dir, b["board"]):
            key = str(job.get("id")) if b["board"].startswith("greenhouse/") else job.get("jobUrl")
            urls[(b["board"], key)] = job.get("absolute_url") or job.get("jobUrl") or ""
    postings = []
    for s in shortlist:
        item = by_key[(s["board"], s["key"])]
        mine = [r for r in rows if r["rank"] == s["rank"]]
        postings.append({"rank": s["rank"], "company": label_page.COMPANY.get(item.board, item.board),
                         "title": item.title, "location": item.location,
                         "text": label_page.plain_text(item.description), "url": urls.get((item.board, item.key), ""),
                         "claims": [{"id": f"R{s['rank']}-C{r['n']}", "kind": r["kind"], "claim": r["claim"],
                                     "quote": r["quote"], "source_field": r["source_field"],
                                     "quote_check": r["quote_check"]} for r in mine]})
    sha = hashlib.sha256((out / "claims.jsonl").read_bytes()).hexdigest()
    (out / "LABEL-CLAIMS.html").write_text(label_page.build_claims(postings, sha), encoding="utf-8")
    print(f"{sum(len(p['claims']) for p in postings)} claims on {len(postings)} postings; claims.jsonl sha256 {sha}")


def labels_import(pasted_path, sample_path, out_path, note):
    import hashlib

    from jobwatch import hand_labels

    pasted = Path(pasted_path).read_bytes()
    sheet = Path(sample_path).read_bytes()
    ids = [m["label_id"] for m in json.loads(sheet)["members"]]
    parsed = hand_labels.parse(pasted.decode("utf-8"), ids)
    out = {"source": str(pasted_path), "source_sha256": hashlib.sha256(pasted).hexdigest(),
           "sample": str(sample_path), "sample_sha256": hashlib.sha256(sheet).hexdigest(), "note": note, **parsed}
    Path(out_path).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = collections.Counter(v["label"] for v in parsed["labels"].values())
    print(f"{len(parsed['labels'])} labels: " + ", ".join(f"{k} {counts[k]}" for k in ("yes", "no", "cannot tell")))


def audit_dev(audit_path, sample_path, labels_path, out_dir):
    """The filter against the student's labels, development groups only (never the held-out 30)."""
    from jobwatch import hand_labels

    records = {(r["board"], r["key"]): r for r in map(json.loads, open(audit_path, encoding="utf-8"))}
    members = json.loads(Path(sample_path).read_text(encoding="utf-8"))["members"]
    labels = json.loads(Path(labels_path).read_text(encoding="utf-8"))["labels"]
    rows = hand_labels.development_rows(members, labels, records)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "dev-comparison.jsonl", "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    lines = ["# The filter against the student's hand labels: development groups only", "",
             f"Written by `python3 -m jobwatch.js3 audit-dev --audit {audit_path} --sample {sample_path} "
             f"--labels {labels_path} --out {out_dir}`. The two held-out groups are not in this file.", "",
             "Outcome: *agree*; *false exclusion* (labelled yes, the filter rejected it); *false inclusion* "
             "(labelled no, the filter kept it or held it for review); *cannot tell* (never scored).", "",
             "| ID | Group | Board | Title | Location | Fate | Score | Matched | Filter's reasons | Label | Outcome | The student's reason |",
             "| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |"]
    for row in rows:
        r = records[(row["board"], row["key"])]
        matched = "; ".join(f"{k}: {', '.join(v)}" for k, v in r["matched"].items() if v)
        why = ", ".join(r["reasons"] + [f"review: {x}" for x in r["review_reasons"]])
        lines.append("| " + " | ".join(_md_cell(c) for c in [
            row["label_id"], row["stratum"].replace("audit ", ""), row["board"], r["title"], r["location"]["text"],
            r["fate"], r["score"], matched, why, row["label"], row["outcome"], row["reason"]]) + " |")
    (out / "DEV-COMPARISON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    groups = collections.OrderedDict()
    for row in rows:
        groups.setdefault(row["stratum"], collections.Counter())[row["outcome"]] += 1
    for stratum, counts in groups.items():
        print(f"  {stratum:34} " + ", ".join(f"{k} {counts[k]}" for k in
                                             ("agree", "false exclusion", "false inclusion", "cannot tell")))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m jobwatch.js3")
    commands = parser.add_subparsers(dest="command", required=True)
    inv = commands.add_parser("inventory", help="expected versus collected, and the fields the boards sent")
    inv.add_argument("run_dir")
    inv.add_argument("--out", help="also write the inventory to this file")
    scr = commands.add_parser("screen", help="run FILTER.md on every posting; write the audit view")
    scr.add_argument("run_dir")
    scr.add_argument("--out", required=True)
    lab = commands.add_parser("labels-sheet", help="draw the hand-label sample; write the offline labelling page")
    lab.add_argument("run_dir")
    lab.add_argument("--audit", required=True)
    lab.add_argument("--out", required=True)
    dra = commands.add_parser("draft-claims", help="Claude drafts the shortlist's claims (live, Claude Code login)")
    dra.add_argument("run_dir")
    dra.add_argument("--audit", required=True)
    dra.add_argument("--top", type=int, default=8)
    dra.add_argument("--out", required=True)
    dra.add_argument("--model", default="claude-opus-5-5")
    cla = commands.add_parser("claims-sheet", help="write the offline page for labelling the shortlist's claims")
    cla.add_argument("run_dir")
    cla.add_argument("--shortlist", required=True)
    imp = commands.add_parser("labels-import", help="read the student's pasted label table into labels JSON")
    imp.add_argument("pasted")
    imp.add_argument("--sample", required=True)
    imp.add_argument("--out", required=True)
    imp.add_argument("--note", required=True, help="how the labels were entered, in one sentence")
    dev = commands.add_parser("audit-dev", help="the filter against the hand labels, development groups only")
    dev.add_argument("--audit", required=True)
    dev.add_argument("--sample", required=True)
    dev.add_argument("--labels", required=True)
    dev.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.command == "labels-import":
        labels_import(args.pasted, args.sample, args.out, args.note)
        return 0
    if args.command == "audit-dev":
        audit_dev(args.audit, args.sample, args.labels, args.out)
        return 0
    if args.command == "claims-sheet":
        claims_sheet(args.run_dir, args.shortlist)
        return 0
    if args.command == "draft-claims":
        draft_claims(args.run_dir, args.audit, args.top, args.out, args.model)
        return 0
    if args.command == "labels-sheet":
        labels_sheet(args.run_dir, args.audit, args.out)
        return 0
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
