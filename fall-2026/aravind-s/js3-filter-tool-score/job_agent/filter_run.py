"""The filter run (JS3): FILTER.md's filter on everything the agent collected, offline.

"Everything collected" is the newest saved answer of each board in the board list (FILTER.md Section 6, item 9):
the newest run folder holding an HTTP 200 answer for that board, and its last such attempt. Nothing is fetched.
The run writes a new folder (default js3/filter-run/<UTC time>/) with verdicts.json (every posting's record) and
report.md: counts per fate and per deciding rule, the cannot-tell list, the score distribution, the top of the
shortlist with reasons, how often each of FILTER.md Section 6's implementation choices fired, the counts FILTER.md
quoted before the build against the built ones, and the code and document fingerprints.
"""

from __future__ import annotations

import collections
import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from . import evidence, providers
from . import filter as flt
from .errors import BrokenInput, Refused

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "js3" / "filter-run"
EXAMPLES = 5
# What FILTER.md v1.0's text quoted from Claude Code's scratch script (draft 2 rules), to set beside the built counts.
QUOTED_BEFORE_BUILD = [
    ("postings measured", "1,508 (the scratch script left out OpenAI's posting with no title)"),
    ("postings with no employment type (R1)", "0 (\"None of today's 1,508 postings had a missing employment type\")"),
    ("rejected for being outside the US (R2)", "9, with R2 checked after every other hard rule"),
    ("kept postings in another US place or unclear (R2)", "0 (\"none of the other 99\")"),
    ("titles matching the annotation phrases (R8)", "0 (\"None of today's 1,508 postings matched\")"),
]


def newest_answers(runs_root: Path, boards: list) -> list:
    """For each board: the newest saved HTTP 200 answer, checked against its recorded SHA-256, or why there is none."""
    runs = sorted((p for p in Path(runs_root).iterdir() if p.is_dir() and p.name[:4].isdigit()), reverse=True) \
        if Path(runs_root).exists() else []
    found = []
    for board in boards:
        key = f"{board['system']}-{board['name']}"
        source = {"key": key, "system": board["system"], "name": board["name"], "company": board.get("company"),
                  "deliberate_failure": bool(board.get("deliberate_failure")), "run": None, "file": None,
                  "sha256": None, "why_none": "no saved HTTP 200 answer in any run"}
        for run in runs:
            folder = run / "boards" / key
            metas = sorted(folder.glob("attempt-*.meta.json"), key=lambda p: int(p.name.split("-")[1].split(".")[0])) \
                if folder.exists() else []
            good = [m for m in metas if json.loads(m.read_text(encoding="utf-8")).get("status") == 200]
            if not good:
                continue
            meta = json.loads(good[-1].read_text(encoding="utf-8"))
            body_path = folder / meta["body_file"]
            body = gzip.decompress(body_path.read_bytes()) if body_path.suffix == ".gz" else body_path.read_bytes()
            if hashlib.sha256(body).hexdigest() != meta["sha256"]:
                raise BrokenInput(f"{body_path} does not match the SHA-256 its meta file records")
            try:  # shown relative to the repo when the runs are inside it, else as a full path
                shown = str(body_path.resolve().relative_to(REPO))
            except ValueError:
                shown = str(body_path.resolve())
            source.update(run=run.name, file=shown, sha256=meta["sha256"], why_none=None, body=body)
            break
        if source["run"]:  # other runs that saved the very same bytes for this board
            source["same_as"] = [r.name for r in runs if r.name != source["run"] and any(
                json.loads(m.read_text(encoding="utf-8")).get("sha256") == source["sha256"]
                for m in (r / "boards" / key).glob("attempt-*.meta.json"))]
        found.append(source)
    return found


def run(*, runs_root: Path, boards_path: Path, out_root: Path = DEFAULT_OUT, rules_path: Path = flt.FILTER_MD,
        profile: dict = None, profile_label: str = "persona/jane-doe.json (Jane Doe, fictional)", now=None,
        rules_version: str = None) -> dict:
    """Filter every posting of the newest saved answers; write verdicts.json and report.md; return the summary."""
    rules = flt.load_rules(rules_path, version=rules_version)  # None: the newest version in FILTER.md
    profile = profile if profile is not None else flt.load_profile()
    flt.check_profile(profile)
    boards = json.loads(Path(boards_path).read_text(encoding="utf-8"))["boards"]
    started = (now or (lambda: datetime.now(timezone.utc)))()
    run_id = evidence.run_id_for(started)
    out = Path(out_root) / run_id
    if out.exists():
        raise Refused(f"refused: {out} already exists; a filter run never overwrites another")
    sources = newest_answers(runs_root, boards)
    records = []
    for source in sources:
        if source["run"] is None:
            continue
        postings = providers.read(source["system"], 200, source.pop("body"))
        source["postings"] = len(postings)
        records += [flt.judge(p, profile, rules, board=source["key"]) for p in postings]
    chosen = flt.shortlist(records, rules)
    summary = _summary(records, chosen, rules)
    meta = {"run_id": run_id, "started_at": started.isoformat(timespec="seconds"), "filter_version": rules["version"],
            "filter_md_sha256": hashlib.sha256(Path(rules_path).read_bytes()).hexdigest(),
            "code_fingerprint": evidence.code_fingerprint(), "git_head": evidence.git_head(),
            "profile": profile_label, "sources": [{k: v for k, v in s.items() if k != "body"} for s in sources]}
    out.mkdir(parents=True)
    (out / "verdicts.json").write_text(json.dumps(
        {"meta": meta, "summary": summary, "shortlist": [_key(r) for r in chosen["top"]],
         "duplicates_removed": [_key(r) for r in chosen["duplicates_removed"]], "records": records},
        indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "report.md").write_text(report(meta, summary, records, chosen, rules), encoding="utf-8")
    return {"out": out, "meta": meta, "summary": summary, "records": records, "shortlist": chosen}


def _key(record: dict) -> dict:
    return {"board": record["board"], "id": record["id"], "title": record["title"]}


def _summary(records: list, chosen: dict, rules: dict) -> dict:
    fates = collections.Counter(r["fate"] for r in records)
    by_board = collections.defaultdict(collections.Counter)
    for r in records:
        by_board[r["board"]][r["fate"]] += 1
    deciding = collections.Counter(r["deciding_rule"] for r in records if r["fate"] == "rejected")
    failing_at_all = collections.Counter(rule for r in records for rule in r["failed_rules"])
    only_one = collections.Counter(r["failed_rules"][0] for r in records if len(r["failed_rules"]) == 1)
    flags_kept, flags_all = collections.Counter(), collections.Counter()
    for r in records:
        for f in r["flags"]:
            label = f["rule"] + (f" {r['location_category']}" if f["rule"] == "R2" else "")
            flags_all[label] += 1
            if r["fate"] == "kept":
                flags_kept[label] += 1
    kept = [r for r in records if r["fate"] == "kept"]
    return {
        "postings": len(records), "fates": dict(fates), "by_board": {b: dict(c) for b, c in sorted(by_board.items())},
        "deciding_rule": {k: deciding.get(k, 0) for k in flt.HARD_RULES},
        "failing_at_all": {k: failing_at_all.get(k, 0) for k in flt.HARD_RULES},
        "failed_exactly_one": {k: only_one.get(k, 0) for k in flt.HARD_RULES},
        "flags_kept": dict(sorted(flags_kept.items())), "flags_all": dict(sorted(flags_all.items())),
        "score_distribution": dict(sorted(collections.Counter(r["score"] for r in kept).items())),
        "at_or_above_cutoff": chosen["eligible"], "duplicates_removed": len(chosen["duplicates_removed"]),
        "shortlist_size": len(chosen["top"]),
        "cannot_tell": [{"board": r["board"], "id": r["id"], "why": r["cannot_tell"]} for r in records
                        if r["fate"] == "cannot_tell"],
        "section6": section6_counts(records, rules), "built_counts": built_counts(records),
    }


def section6_counts(records: list, rules: dict) -> dict:
    """How often each of FILTER.md Section 6's implementation choices fired, with examples (for the audit to test)."""
    words = {w: [] for w in rules["years_company_words"]}
    seasons, merges, us_remote_other = [], [], []
    for r in records:
        for hit in r["section6"]["company_words"]:
            words[hit["word"]].append({"board": r["board"], "id": r["id"], "title": r["title"],
                                       "years": hit["years"], "sentence": hit["sentence"], "fate": r["fate"]})
        for hit in r["section6"]["season_rule"]:
            seasons.append({"board": r["board"], "id": r["id"], "title": r["title"], **hit})
        for sentence in r["section6"]["dec_merges"]:
            merges.append({"board": r["board"], "id": r["id"], "title": r["title"], "sentence": sentence,
                           "has_start": "start" in sentence.lower()})
        if r["location_category"] == "other_us" and any("remote" in t.lower() for t in r["locations"]):
            us_remote_other.append({"board": r["board"], "id": r["id"], "title": r["title"],
                                    "locations": r["locations"], "fate": r["fate"]})
    return {
        "company_words": {w: {"count": len(h), "postings": len({(x["board"], x["id"]) for x in h}),
                              "examples": h[:EXAMPLES]} for w, h in words.items()},
        "season_rule": {"count": len(seasons), "outcomes": dict(collections.Counter(s["outcome"] for s in seasons)),
                        "examples": seasons[:EXAMPLES]},
        "dec_merges": {"count": len(merges), "with_start": sum(1 for m in merges if m["has_start"]),
                       "examples": merges[:EXAMPLES]},
        "us_remote_counted_other_us": {"count": len(us_remote_other), "examples": us_remote_other[:EXAMPLES]},
    }


def built_counts(records: list) -> list:
    """The built counts for the numbers FILTER.md quoted before the build (QUOTED_BEFORE_BUILD), in the same order."""
    titled = [r for r in records if r["cannot_tell"] != "the posting has no title"]
    r2_only = sum(1 for r in records if r["failed_rules"] == ["R2"])
    r2_any = sum(1 for r in records if "R2" in r["failed_rules"])
    kept_soft = sum(1 for r in records if r["fate"] == "kept" and r["location_category"] in ("other_us", "unclear"))
    r8_titles = sum(1 for r in records for c in r["rules"] if c["rule"] == "R8" and c["result"] == "reject"
                    and c["why"].startswith("the title contains"))
    return [
        f"{len(records)} read ({len(titled)} with a title; {len(records) - len(titled)} without)",
        f"{sum(1 for r in records if not r.get('employmentType'))}",
        f"{r2_only} fail R2 and no other hard rule; {r2_any} fail R2 at all",
        f"{kept_soft}",
        f"{r8_titles}",
    ]


def report(meta: dict, summary: dict, records: list, chosen: dict, rules: dict) -> str:
    rank = rules["ranking"]
    lines = [f"# Filter run {meta['run_id']}", "",
             f"FILTER.md v{meta['filter_version']} applied offline to the newest saved answer of each board (FILTER.md "
             f"Section 6, item 9). Profile: {meta['profile']}. Every number below is computed from verdicts.json in "
             "this folder.", "", "## Sources", "", "| Board | Run folder | Saved answer | SHA-256 | Postings |",
             "|---|---|---|---|---:|"]
    for s in meta["sources"]:
        if s["run"]:
            lines.append(f"| {s['key']} | `{s['run']}` | `{s['file']}` | `{s['sha256'][:16]}...` | {s.get('postings', '')} |")
        else:
            lines.append(f"| {s['key']} | none | {s['why_none']} | | |")
    same = [f"{s['key']} (also saved by {', '.join(s['same_as'])})" for s in meta["sources"] if s.get("same_as")]
    if same:
        lines += ["", "Byte-identical answers saved by other runs: " + "; ".join(same) + "."]
    fates = summary["fates"]
    lines += ["", "## Fates", "",
              f"{summary['postings']} postings: **{fates.get('kept', 0)} kept**, {fates.get('rejected', 0)} rejected, "
              f"{fates.get('cannot_tell', 0)} \"I cannot tell\".", "", "| Board | Kept | Rejected | I cannot tell |",
              "|---|---:|---:|---:|"]
    for board, c in summary["by_board"].items():
        lines.append(f"| {board} | {c.get('kept', 0)} | {c.get('rejected', 0)} | {c.get('cannot_tell', 0)} |")
    lines += ["", "## Rejected, by rule", "",
              "The deciding rule is the first that failed, in the order R1 to R8; every rule ran on every posting.", "",
              "| Rule | Deciding | Failed at all | The only rule that failed |", "|---|---:|---:|---:|"]
    for k in flt.HARD_RULES:
        lines.append(f"| {k} {flt.RULE_NAMES[k]} | {summary['deciding_rule'][k]} | {summary['failing_at_all'][k]} | "
                     f"{summary['failed_exactly_one'][k]} |")
    lines += ["", "## \"I cannot tell\"", "", "For a whole posting (never shortlisted):", ""]
    lines += [f"- {c['board']} `{c['id']}`: {c['why']}" for c in summary["cannot_tell"]] or ["- none"]
    lines += ["", "For one rule, on kept postings (each costs the penalty in Section 1):", ""]
    lines += [f"- {k}: {v}" for k, v in summary["flags_kept"].items()] or ["- none"]
    lines += ["", "The same flags across every posting, rejected ones included (no score is given to those):", ""]
    lines += [f"- {k}: {v}" for k, v in summary["flags_all"].items()] or ["- none"]
    lines += ["", "## Scores of the kept postings", "", "| Score | Postings |", "|---:|---:|"]
    lines += [f"| {s} | {n} |" for s, n in summary["score_distribution"].items()]
    lines += ["", f"{summary['at_or_above_cutoff']} kept postings score {rank['shortlist_min']} or more; "
              f"{summary['duplicates_removed']} duplicate copies were removed (same board and normalized title; "
              f"the newest kept); the shortlist holds the top {summary['shortlist_size']}.", "",
              f"## The shortlist (top {rank['shortlist_size']})", ""]
    for n, r in enumerate(chosen["top"], 1):
        terms = "; ".join(f"{label} {points:+d}" for label, points in r["score_terms"])
        topics = ", ".join(f"{g} ({t['term']})" for g, t in r["topics"].items())
        lines += [f"{n}. **{r['title']}** ({r['board']}), score {r['score']}: {terms}",
                  f"   - Topics: {topics or 'none'}",
                  f"   - Locations: {'; '.join(r['locations']) or 'none'}; posted {r['publishedAt'] or 'no date'}",
                  f"   - {r['jobUrl']}"]
    s6 = summary["section6"]
    lines += ["", "## How often Section 6's implementation choices fired", "",
              "Claude Code made these choices for FILTER.md v1.0. Counted here so the audit can test them instead of "
              "assuming them.", "", "**R7 company words** (a years sentence above the person's years that names the "
              "company counts as \"cannot tell\", not a requirement):", "", "| Word | Sentences | Postings |",
              "|---|---:|---:|"]
    lines += [f"| {w} | {v['count']} | {v['postings']} |" for w, v in s6["company_words"].items()]
    for w, v in s6["company_words"].items():
        for ex in v["examples"]:
            lines.append(f"- *{w}*, {ex['board']} \"{ex['title']}\" ({ex['years']} years, {ex['fate']}): "
                         f"\"{ex['sentence'][:300]}\"")
    sr = s6["season_rule"]
    lines += ["", f"**The season or quarter start rule:** {sr['count']} mentions in start sentences; outcomes "
              f"{sr['outcomes'] or 'none'}."]
    lines += [f"- {ex['board']} \"{ex['title']}\": {ex['season']} -> {ex['outcome']}: \"{ex['sentence'][:300]}\""
              for ex in sr["examples"]]
    dm = s6["dec_merges"]
    lines += ["", f"**The \"Dec.\" splitter fix:** kept {dm['count']} month abbreviations with their year; "
              f"{dm['with_start']} of those sentences contain \"start\"."]
    lines += [f"- {ex['board']} \"{ex['title']}\": \"{ex['sentence'][:300]}\"" for ex in dm["examples"]]
    ur = s6["us_remote_counted_other_us"]
    lines += ["", f"**US remote spellings that are not one of the person's remote phrases** (Section 6, item 5 counts "
              f"them as another US place, minus 15): {ur['count']}."]
    lines += [f"- {ex['board']} \"{ex['title']}\": {'; '.join(ex['locations'])}" for ex in ur["examples"]]
    lines += ["", "## Counts FILTER.md quoted before the build, and the built counts", "",
              "FILTER.md's note says its counts came from Claude Code's scratch script on the second draft of the "
              "rules; these are the built filter's counts on the answers above.", "",
              "| What | Quoted before the build | Built |", "|---|---|---|"]
    for (what, quoted), built in zip(QUOTED_BEFORE_BUILD, summary["built_counts"]):
        lines.append(f"| {what} | {quoted} | {built} |")
    lines += ["", "## Fingerprints", "",
              f"Run {meta['run_id']} started {meta['started_at']}; FILTER.md SHA-256 `{meta['filter_md_sha256']}`; "
              f"code fingerprint `{meta['code_fingerprint']}`; git HEAD `{meta['git_head']}` (the commit checked out "
              "when the run started; uncommitted changes, if any, are covered by the code fingerprint).", ""]
    return "\n".join(lines)
