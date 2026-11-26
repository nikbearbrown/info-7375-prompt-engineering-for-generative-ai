"""Propose company-boilerplate candidates for my review (FILTER.md Rule 4).

A candidate is a sentence that appears word for word, after cleaning, in at least
5% of one board's postings and contains a Rule 2 topic phrase or a Rule 3 skill.

This script writes rules/boilerplate.json. It never labels a sentence and never
changes a label I have written: existing labels, review dates and notes are kept.
The filter removes a sentence only after I label it 'company boilerplate' and add
the date I reviewed it.

    python3 propose_boilerplate.py [--js2 PATH]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

import job_filter as J
import postings as P

HERE = Path(__file__).resolve().parent


def candidates(all_postings, rules):
    share = rules["filter"]["boilerplate"]["candidate_share_of_board_postings"]
    phrases = [w for cat, ws in rules["filter"]["topics"].items() if not cat.startswith("_") for w in ws]
    phrases += rules["skills"]
    by_board = collections.defaultdict(list)
    for p in all_postings:
        by_board[p["board"]].append(p)
    out = []
    for board in sorted(by_board):
        ps = by_board[board]
        count = collections.Counter()
        for p in ps:
            for text in {s["text"] for s in P.sentences(p["markup"])}:
                count[text] += 1
        for text, n in sorted(count.items(), key=lambda x: (-x[1], x[0])):
            if n >= share * len(ps):
                hits = [w for w in phrases if J.has(w, text)]
                if hits:
                    out.append({"board": board, "sentence": text, "postings_containing": n,
                                "board_postings": len(ps), "share": round(n / len(ps), 4),
                                "matched_phrases": hits})
    return out


def merge(existing, found):
    """Keep every label I wrote; add new candidates with blank labels."""
    old = {(s["board"], s["sentence"]): s for s in existing.get("sentences", [])}
    merged = []
    for c in found:
        prev = old.pop((c["board"], c["sentence"]), {})
        merged.append({**c, "label": prev.get("label", ""), "reviewed_on": prev.get("reviewed_on", ""),
                       "note": prev.get("note", "")})
    for s in old.values():  # labeled entries that are no longer candidates stay
        if s.get("label") or s.get("note"):
            merged.append({**s, "still_a_candidate": False})
    return merged


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--js2", default=str(P.DEFAULT_JS2))
    args = ap.parse_args(argv)
    all_postings, _ = P.load_saved_postings(args.js2)
    persona, _ = P.load_persona(args.js2)
    rules = J.load_rules(persona=persona)
    path = HERE / "rules" / "boilerplate.json"
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    doc = {
        "_comment": ("FILTER.md Rule 4, Version 1.1. Candidates are proposed by propose_boilerplate.py. "
                     "A sentence is removed before scoring ONLY when I set label to 'company boilerplate' "
                     "and reviewed_on to the date I reviewed it. A blank or 'job-specific' label keeps the "
                     "sentence in the job-specific text. The script never fills these fields."),
        "version": "1.1",
        "label_values": ["company boilerplate", "job-specific"],
        "sentences": merge(existing, candidates(all_postings, rules)),
    }
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    n_labeled = sum(1 for s in doc["sentences"] if s["label"])
    print(f"{len(doc['sentences'])} sentences in {path.relative_to(HERE)} ({n_labeled} labeled)")
    for s in doc["sentences"]:
        print(f"  {s['board']:10} {s['postings_containing']:4} postings  label={s['label'] or '(blank)'}  {s['sentence'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
