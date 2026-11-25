"""Draw the held-out set and the audit set, and write blind labeling sheets.

    python3 -m js3.sample --decisions out/filter/v1.0/decisions.jsonl

Fixed seed 7375. One random.Random(seed) is used for both draws, in this
order:

a. HELD-OUT, first, from the whole corpus regardless of filter decision:
   16 postings whose title contains "engineer" or "scientist" (whole word,
   case-insensitive) and 8 from all other postings, shuffled together.
b. AUDIT, excluding every held-out id: 30 random rejected postings, then up
   to 10 random close calls (score 3 or 4, any decision) not already drawn,
   then 10 random kept postings not already drawn, shuffled together.

Pools are sorted by (board, id) before drawing, so the draw depends only on
the seed and the data, not on file order. If a pool is smaller than asked,
all of it is taken and the shortfall is printed and recorded.

Sheets are BLIND: row number, board, id, title, location, url and the first
800 characters of body_text. No scores, decisions or strata.
"""

import argparse
import csv
import json
import random
import re
import sys
from pathlib import Path

from js3 import corpus

SEED = 7375
HELDOUT_TITLE = 16
HELDOUT_OTHER = 8
AUDIT_REJECTED = 30
AUDIT_CLOSE = 10
AUDIT_KEPT = 10
BODY_CHARS = 800
CLOSE_CALL_SCORES = (3, 4)
VERDICT_COLUMNS = ("id", "verdict", "reason")

TITLE_STRATUM = "title_engineer_or_scientist"
OTHER_STRATUM = "title_other"

_TITLE_WORDS = re.compile(r"(?<![0-9A-Za-z_])(engineer|scientist)"
                          r"(?![0-9A-Za-z_])", re.IGNORECASE)


def _key(item):
    return (item["board"], item["id"])


def _draw(rng, pool, k, label, shortfalls):
    pool = sorted(pool, key=_key)
    if len(pool) < k:
        shortfalls[label] = {"requested": k, "available": len(pool)}
        k = len(pool)
    return rng.sample(pool, k)


def draw_heldout(postings, rng):
    """Return (rows, shortfalls). Each row is the posting plus "stratum"."""
    shortfalls = {}
    titled = [p for p in postings if _TITLE_WORDS.search(p["title"] or "")]
    other = [p for p in postings if not _TITLE_WORDS.search(p["title"] or "")]
    rows = [dict(p, stratum=TITLE_STRATUM)
            for p in _draw(rng, titled, HELDOUT_TITLE, TITLE_STRATUM,
                           shortfalls)]
    rows += [dict(p, stratum=OTHER_STRATUM)
             for p in _draw(rng, other, HELDOUT_OTHER, OTHER_STRATUM,
                            shortfalls)]
    rng.shuffle(rows)
    return rows, shortfalls


def draw_audit(decisions, heldout_ids, rng):
    """Return (rows, shortfalls). Each row is the decision plus "stratum"."""
    shortfalls = {}
    taken = set(heldout_ids)
    rows = []

    def take(pool, k, stratum):
        pool = [d for d in pool if d["id"] not in taken]
        for d in _draw(rng, pool, k, stratum, shortfalls):
            taken.add(d["id"])
            rows.append(dict(d, stratum=stratum))

    take([d for d in decisions if d["decision"] == "rejected"],
         AUDIT_REJECTED, "rejected")
    take([d for d in decisions if d["score"] in CLOSE_CALL_SCORES],
         AUDIT_CLOSE, "close_call")
    if "close_call" in shortfalls:
        shortfalls["close_call"]["note"] = "up to 10 requested"
    take([d for d in decisions if d["decision"] == "kept"],
         AUDIT_KEPT, "kept")
    rng.shuffle(rows)
    return rows, shortfalls


def draw(postings, decisions, seed=SEED):
    """Held-out first, then audit, from one RNG seeded with `seed`."""
    rng = random.Random(seed)
    heldout, held_short = draw_heldout(postings, rng)
    audit, audit_short = draw_audit(decisions, [p["id"] for p in heldout],
                                    rng)
    return heldout, held_short, audit, audit_short


def render_sheet(title, verdicts_file, postings):
    """Blind sheet: only posting fields, never filter output."""
    lines = [
        f"# {title}",
        "",
        f"Write one line per row in `{verdicts_file}`: "
        "`id,verdict,reason`, verdict one of relevant / not / unsure.",
        f"Body text is cut at {BODY_CHARS} characters; open the url for "
        "the full posting.",
        "",
    ]
    for number, p in enumerate(postings, 1):
        body = (p.get("body_text") or "")[:BODY_CHARS]
        lines += [
            f"## {number}",
            "",
            f"- board: {p['board']}",
            f"- id: {p['id']}",
            f"- title: {p['title']}",
            f"- location: {p['location']}",
            f"- url: {p['url']}",
            "",
            "~~~~text",
            body if body else "(no body text)",
            "~~~~",
            "",
        ]
    return "\n".join(lines)


def write_verdict_template(path, ids):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(VERDICT_COLUMNS)
        for pid in ids:
            writer.writerow([pid, "", ""])


def load_decisions(path):
    decisions = []
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if line.strip():
                row = json.loads(line)
                for field in ("board", "id", "decision", "score"):
                    if field not in row:
                        raise ValueError(f"{path} line {number}: no {field}")
                decisions.append(row)
    return decisions


def check_same_corpus(postings, decisions):
    p_keys = [_key(p) for p in postings]
    d_keys = [_key(d) for d in decisions]
    if len(set(p_keys)) != len(p_keys):
        raise ValueError("corpus has duplicate (board, id) pairs")
    ids = [k[1] for k in p_keys]
    if len(set(ids)) != len(ids):
        raise ValueError("an id appears on two boards; verdict files are "
                         "keyed by id alone")
    if sorted(p_keys) != sorted(d_keys):
        raise ValueError("decisions file does not cover exactly the frozen "
                         "corpus; re-run js3.run_filter")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--labels", default="labels",
                        help="output folder (default: labels)")
    parser.add_argument("--root", default=str(corpus.ROOT))
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing sheets, ids and key files "
                             "(verdict CSVs are never overwritten)")
    args = parser.parse_args(argv)

    labels = Path(args.labels)
    generated = [labels / n for n in ("heldout_ids.json", "heldout_sheet.md",
                                      "audit_sheet.md", "audit_key.json")]
    existing = [str(p) for p in generated if p.exists()]
    if existing and not args.force:
        print("refusing to overwrite: " + ", ".join(existing)
              + " (use --force)", file=sys.stderr)
        return 2

    decisions = load_decisions(args.decisions)
    corpus_data = corpus.load(args.root)
    postings = corpus_data["postings"]
    check_same_corpus(postings, decisions)
    by_key = {_key(p): p for p in postings}

    heldout, held_short, audit, audit_short = draw(postings, decisions)

    labels.mkdir(parents=True, exist_ok=True)
    (labels / "heldout_ids.json").write_text(json.dumps({
        "seed": SEED,
        "requested": {TITLE_STRATUM: HELDOUT_TITLE,
                      OTHER_STRATUM: HELDOUT_OTHER},
        "shortfalls": held_short,
        "ids": [p["id"] for p in heldout],
        "strata": {p["id"]: p["stratum"] for p in heldout},
    }, indent=2) + "\n", "utf-8")
    (labels / "heldout_sheet.md").write_text(render_sheet(
        "Held-out labeling sheet", "labels/heldout_verdicts.csv", heldout),
        "utf-8")

    audit_postings = [by_key[_key(d)] for d in audit]
    (labels / "audit_sheet.md").write_text(render_sheet(
        "Audit labeling sheet", "labels/audit_verdicts.csv", audit_postings),
        "utf-8")
    (labels / "audit_key.json").write_text(json.dumps({
        "seed": SEED,
        "decisions_file": str(args.decisions),
        "config_version": audit[0].get("config_version") if audit else None,
        "requested": {"rejected": AUDIT_REJECTED, "close_call": AUDIT_CLOSE,
                      "kept": AUDIT_KEPT},
        "shortfalls": audit_short,
        "key": {d["id"]: {"row": n, "board": d["board"],
                          "stratum": d["stratum"],
                          "decision": d["decision"], "score": d["score"]}
                for n, d in enumerate(audit, 1)},
    }, indent=2) + "\n", "utf-8")

    for name, ids in (("heldout_verdicts.csv", [p["id"] for p in heldout]),
                      ("audit_verdicts.csv", [d["id"] for d in audit])):
        path = labels / name
        if path.exists():
            print(f"kept existing {path} (verdict files are never "
                  "overwritten)")
        else:
            write_verdict_template(path, ids)

    print(f"held-out: {len(heldout)} postings; audit: {len(audit)} postings")
    for label, short in {**held_short, **audit_short}.items():
        print(f"SHORTFALL {label}: {short}")
    print(f"wrote sheets and keys in {labels}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
