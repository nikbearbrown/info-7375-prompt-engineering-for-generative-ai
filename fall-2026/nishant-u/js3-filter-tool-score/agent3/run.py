"""Run FILTER.md v1 over every posting the JS2 loop saved. Offline: reads saved raw bodies only.

    python -m agent3.run --filter-version 1      # -> out3/filter-run (the v1 run)
    python -m agent3.run --filter-version 2      # -> out3/filter-run-v2 (the default)

Every *.body under <raw-root>/**/raw/ with its .meta.json is read. Postings are deduplicated
by system:board:id; when a posting appears in several saved responses, the copy from the
latest fetched_at is used (ties: the later path). A board whose run report marks it
unverified-empty is recorded as a board-level abstention. No network call is made.
"""
import argparse
import hashlib
import json
from pathlib import Path

from agent3 import filter as flt
from agent3 import shortlist as sl

ROOT = Path(__file__).resolve().parents[1]


def board_statuses(raw_root):
    statuses = {}
    for report in sorted(Path(raw_root).glob("**/report.json")):
        data = json.loads(report.read_text(encoding="utf-8"))
        for entry in data.get("boards") or []:
            key = f"{entry.get('system')}:{entry.get('board')}"
            statuses.setdefault(key, set()).add(entry.get("status"))
    return statuses


def collect(raw_root):
    """(postings, sources): one posting per system:board:id, and every raw file read."""
    raw_root = Path(raw_root)
    statuses = board_statuses(raw_root)
    best, sources = {}, []
    for body in sorted(raw_root.glob("**/raw/*.body")):
        meta = json.loads(body.with_name(body.name[:-5] + ".meta.json").read_text(encoding="utf-8"))
        raw = body.read_bytes()
        rel = body.relative_to(raw_root).as_posix()
        record = {"file": rel, "system": meta["system"], "board": meta["board"],
                  "http_status": meta.get("http_status"), "fetched_at": meta.get("fetched_at"),
                  "sha256": hashlib.sha256(raw).hexdigest(), "postings": 0}
        sources.append(record)
        if meta.get("http_status") != 200:
            continue
        jobs = json.loads(raw).get("jobs") or []
        record["postings"] = len(jobs)
        key = f"{meta['system']}:{meta['board']}"
        status = "unverified-empty" if "unverified-empty" in statuses.get(key, ()) else "ok"
        for job in jobs:
            posting = flt.make_posting(meta["system"], meta["board"], job, board_status=status, source=rel)
            order = (meta.get("fetched_at") or "", rel)
            held = best.get(posting["posting_id"])
            if held is None or order > held[0]:
                best[posting["posting_id"]] = (order, posting)
    postings = [p for _, p in sorted(best.values(), key=lambda item: item[1]["posting_id"])]
    unverified = sorted(k for k, v in statuses.items() if "unverified-empty" in v)
    return postings, sources, unverified


def run(raw_root, out_dir, resume_path, version=1):
    from agent.resume import load_resume
    skills = flt.shipped_skills(load_resume(resume_path))
    postings, sources, unverified = collect(raw_root)
    results = []
    for p in postings:
        v = flt.evaluate(p, skills, version=version)
        results.append({"posting_id": p["posting_id"], "board": f"{p['system']}:{p['board']}",
                        "title": p["title"], "location": p["location"], "verdict": v["verdict"],
                        "abstain": v["abstain"], "rule": v["rule"], "field": v["field"],
                        "reason": v["reason"], "skills_found": v["skills_found"],
                        "text_chars": v["text_chars"], "url": p["url"], "source": p["source"]})
        if version >= 2:
            results[-1]["practices_found"] = v["practices_found"]
    counts = {"postings": len(results)}
    for r in results:
        key = r["verdict"] if r["verdict"] != "reject" else f"reject_{r['rule']}"
        counts[key] = counts.get(key, 0) + 1
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = {"filter": f"FILTER.md v{version}", "skills": skills, "counts": counts,
           "board_abstentions": [{"board": b, "verdict": "abstain",
                                  "reason": f"{flt.ABSTAIN} (board {b} is unverified-empty; 0 postings)"}
                                 for b in unverified],
           "sources": sources, "results": results}
    (out_dir / "results.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    entries = sl.build_shortlist(postings, skills, version=version)
    (out_dir / "shortlist.md").write_text(render_shortlist(entries, counts, version), encoding="utf-8")
    if version >= 2:
        # Machine-readable twin of shortlist.md (read by mcp_server/); v1's output folder is left as run.
        rows = [{"rank": n, "posting_id": e["posting_id"], "title": e["posting"]["title"],
                 "location": e["posting"]["location"], "url": e["posting"]["url"], "claims": e["claims"]}
                for n, e in enumerate(entries, 1)]
        (out_dir / "shortlist.json").write_text(
            json.dumps({"filter": f"FILTER.md v{version}", "shortlist": rows}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    return counts, entries


def render_shortlist(entries, counts, version=1):
    lines = [f"# Shortlist — FILTER.md v{version} over the saved JS2 postings", "",
             f"{len(entries)} accepted of {counts['postings']} unique postings. Generated by "
             + ("`python -m agent3.run`" if version == 1 else f"`python -m agent3.run --filter-version {version}`")
             + "; labels are computed by agent3/shortlist.py from the posting "
             "text only. Not reviewed by hand: every row below is \"computed\", not checked.", "",
             "Ranked by supported claims, then fewest contradicted, then posting id.", ""]
    for n, e in enumerate(entries, 1):
        p = e["posting"]
        supported = sum(c["label"] == "supported" for c in e["claims"])
        lines += [f"## {n}. {p['title']} — `{p['posting_id']}`", "",
                  f"Location: {p['location']}  ", f"URL: {p['url']}  ",
                  f"Supported claims: {supported}", "",
                  "| Claim | Label | Field | Quote |", "| --- | --- | --- | --- |"]
        for c in e["claims"]:
            quote = c["quote"].replace("|", "\\|")
            lines.append(f"| {c['claim']} {c['text']} | {c['label']} | {c['field']} | {quote} |")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw-root", default=str(ROOT / "out"))
    parser.add_argument("--filter-version", type=int, choices=sorted(flt.VERSIONS), default=2)
    parser.add_argument("--out", default=None,
                        help="default: out3/filter-run for v1, out3/filter-run-v<N> otherwise")
    parser.add_argument("--resume", default=str(ROOT / "data" / "resume.example.json"))
    args = parser.parse_args(argv)
    out = args.out or str(ROOT / "out3" / ("filter-run" if args.filter_version == 1 else f"filter-run-v{args.filter_version}"))
    counts, entries = run(args.raw_root, out, args.resume, version=args.filter_version)
    print(json.dumps(counts, indent=2))
    print(f"shortlist: {len(entries)} postings -> {Path(out) / 'shortlist.md'}")


if __name__ == "__main__":
    main()
