"""Draw the JS3 blind-audit sample from the saved filter results (offline, reproducible).

    python3 make_audit_sample.py

Reads runs/filter-2026-11-17T21-47-06-167440-0500/results.json (committed in
beb8a26) and the raw responses it names. With the fixed seed below it writes,
once (never overwriting):
  audit/selection.json  the IDs, groups, seed and method (NOT blind: open it only after judging)
  audit/AUDIT.csv       the blind sheet: row, board, posting id, title, location, reading file,
                        my_verdict and my_reason left blank; rows shuffled
  audit/read/*.txt      one reading file per posting: title, location and the full description
                        as plain text, from the exact saved raw response; no filter output
Groups (approved by Swathi, 2026-11-17): both "not shortlisted"; 4 rejected only by R4;
4 rejected only by R5; 4 "I cannot tell"; all 4 shortlisted; then 30 rejected drawn
from the rejected postings not already chosen. Each pool is sorted by (board, posting id)
before random.Random(SEED).sample, so the draw does not depend on file order.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import random

import descriptions
import parsers

HERE = Path(__file__).resolve().parent
RESULTS = Path("runs/filter-2026-11-17T21-47-06-167440-0500/results.json")
SEED = 20261117
AUDIT = HERE / "audit"


def key(r):
    return (r["board"], r["posting_id"])


def draw(results, rng):
    by = lambda pred: sorted((r for r in results if pred(r)), key=key)
    groups = {}
    groups["close: not shortlisted (all)"] = by(lambda r: r["verdict"] == "not shortlisted")
    groups["close: rejected only by R4"] = rng.sample(by(lambda r: r["reason"] == "fails R4"), 4)
    groups["close: rejected only by R5"] = rng.sample(by(lambda r: r["reason"] == "fails R5"), 4)
    groups["I cannot tell"] = rng.sample(by(lambda r: r["verdict"] == "I cannot tell"), 4)
    groups["shortlisted (all)"] = by(lambda r: r["verdict"] == "shortlisted")
    taken = {key(r) for g in groups.values() for r in g}
    groups["rejected, random (after close calls)"] = rng.sample(
        by(lambda r: r["verdict"] == "rejected" and key(r) not in taken), 30)
    return groups


def reading_text(board, posting, raw_file, raw_sha):
    return "\n".join([
        f"Title: {posting['title']}",
        f"Location: {posting['location']}",
        f"Board: {board}",
        f"Posting ID: {posting['id']}",
        f"Posting URL: {posting['url']}",
        f"Source: {raw_file} (sha256 {raw_sha}), saved LIVE run 2026-11-17 21:47 EST",
        "Description: the full description from that raw response, HTML converted to plain text",
        "(one line per paragraph, heading or list item); nothing removed or summarized.",
        "-" * 70,
        descriptions.html_to_text(posting["description_html"]),
        "",
    ])


def main():
    out = json.loads((HERE / RESULTS).read_text(encoding="utf-8"))
    results = out["results"]
    groups = draw(results, random.Random(SEED))
    chosen = [(g, r) for g, rows in groups.items() for r in rows]
    assert len(chosen) == 48 and len({key(r) for _, r in chosen}) == 48

    postings = {}
    for board, b in out["boards"].items():
        if b["status"] != "ok":
            continue
        raw = (HERE / b["raw_file"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == b["raw_sha256"]
        for p in parsers.PARSERS["ashby" if board == "plaid" else "greenhouse"](raw, include_description=True)[0]:
            postings[(board, p["id"])] = (p, b["raw_file"], b["raw_sha256"])

    (AUDIT / "read").mkdir(parents=True, exist_ok=False)
    rows = []
    for _, r in chosen:
        p, raw_file, raw_sha = postings[key(r)]
        path = Path("audit") / "read" / f"{r['board']}-{r['posting_id']}.txt"
        with open(HERE / path, "x", encoding="utf-8") as f:
            f.write(reading_text(r["board"], p, raw_file, raw_sha))
        rows.append([r["board"], r["posting_id"], p["title"], p["location"], path.as_posix()])
    random.Random(SEED + 1).shuffle(rows)

    sheet = io.StringIO()
    writer = csv.writer(sheet, lineterminator="\n")
    writer.writerow(["row", "board", "posting_id", "title", "location", "reading_file", "my_verdict", "my_reason"])
    for i, row in enumerate(rows, 1):
        writer.writerow([i] + row + ["", ""])
    with open(AUDIT / "AUDIT.csv", "x", encoding="utf-8") as f:
        f.write(sheet.getvalue())

    selection = {
        "note": "NOT blind: groups reveal the filter's verdicts. Open only after filling in AUDIT.csv.",
        "source_results": {"path": RESULTS.as_posix(), "commit": "beb8a26",
                           "sha256": hashlib.sha256((HERE / RESULTS).read_bytes()).hexdigest()},
        "seed": SEED, "shuffle_seed": SEED + 1,
        "method": ("Each pool sorted by (board, posting_id); random.Random(seed).sample in this order: "
                   "4 of 'fails R4' only, 4 of 'fails R5' only, 4 of 'I cannot tell'; all 'not shortlisted' and "
                   "all 'shortlisted' taken whole; then 30 from rejected postings not already chosen. "
                   "AUDIT.csv rows shuffled with random.Random(shuffle_seed). Script: make_audit_sample.py."),
        "pool_sizes": {"not shortlisted": sum(r["verdict"] == "not shortlisted" for r in results),
                       "rejected only by R4": sum(r["reason"] == "fails R4" for r in results),
                       "rejected only by R5": sum(r["reason"] == "fails R5" for r in results),
                       "I cannot tell": sum(r["verdict"] == "I cannot tell" for r in results),
                       "shortlisted": sum(r["verdict"] == "shortlisted" for r in results),
                       "rejected": sum(r["verdict"] == "rejected" for r in results)},
        "groups": {g: [{"board": r["board"], "posting_id": r["posting_id"]} for r in rows_]
                   for g, rows_ in groups.items()},
        "total": len(chosen),
    }
    with open(AUDIT / "selection.json", "x", encoding="utf-8") as f:
        json.dump(selection, f, indent=2)
    print(f"wrote {len(chosen)} reading files, audit/AUDIT.csv and audit/selection.json")


if __name__ == "__main__":
    main()
