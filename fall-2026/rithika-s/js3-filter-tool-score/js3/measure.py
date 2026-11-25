"""Compare filter decisions with hand verdicts.

    python3 -m js3.measure --decisions out/filter/v1.0/decisions.jsonl \
        --verdicts labels/audit_verdicts.csv [--key labels/audit_key.json]

Verdicts: relevant / not / unsure. A missing, blank or unrecognised verdict
is "unlabeled" and is never counted as agreement or disagreement.

Without --key, every id in the verdicts file is measured. With --key, the
ids in the key are measured (an id missing from the verdicts file is
unlabeled) and errors are reported per stratum with a Wilson 95% interval.
"""

import argparse
import csv
import json
import math
import sys
from collections import Counter

from js3.sample import load_decisions

VERDICTS = ("relevant", "not", "unsure")
CATEGORIES = ("kept&relevant", "kept&not", "rejected&relevant",
              "rejected&not", "unsure", "abstain", "unlabeled")
DISAGREE = ("kept&not", "rejected&relevant")
Z95 = 1.959963984540054


def wilson(errors, n, z=Z95):
    """Wilson score interval for errors/n. Returns (low, high)."""
    if n <= 0:
        raise ValueError("Wilson interval needs n > 0")
    p = errors / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def load_verdicts(path):
    """Return ({id: verdict or None}, problems). None means unlabeled."""
    verdicts, problems = {}, []
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in ("id", "verdict") if c not in
                   (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing column(s) {missing}")
        for number, row in enumerate(reader, 2):
            pid = (row.get("id") or "").strip()
            if not pid:
                continue
            if pid in verdicts:
                raise ValueError(f"{path} line {number}: id {pid} twice")
            value = (row.get("verdict") or "").strip().lower()
            if value and value not in VERDICTS:
                problems.append(f"line {number}: id {pid}: verdict "
                                f"{value!r} is not relevant/not/unsure; "
                                "treated as unlabeled")
                value = ""
            verdicts[pid] = value or None
    return verdicts, problems


def categorise(decision, verdict):
    if verdict is None:
        return "unlabeled"
    if decision == "abstain":
        return "abstain"
    if verdict == "unsure":
        return "unsure"
    return f"{decision}&{verdict}"


def measure(decisions, verdicts, key=None):
    """Return a result dict; see main() for how it is printed."""
    by_id = {}
    for d in decisions:
        if d["id"] in by_id:
            raise ValueError(f"decisions file has id {d['id']} twice")
        by_id[d["id"]] = d
    ids = list(key) if key is not None else list(verdicts)
    notes = []
    if key is not None:
        extra = [pid for pid in verdicts if pid not in key]
        if extra:
            notes.append(f"{len(extra)} verdict id(s) not in the key, "
                         f"ignored: {', '.join(extra)}")

    rows, unknown = [], []
    for pid in ids:
        d = by_id.get(pid)
        if d is None:
            unknown.append(pid)
            continue
        if key is not None and (key[pid]["decision"] != d["decision"]
                                or key[pid]["score"] != d["score"]):
            notes.append(f"id {pid}: decisions file says {d['decision']} "
                         f"(score {d['score']}), key says "
                         f"{key[pid]['decision']} (score {key[pid]['score']})"
                         "; measuring the decisions file")
        verdict = verdicts.get(pid)
        rows.append({"id": pid, "board": d["board"], "title": d["title"],
                     "decision": d["decision"], "score": d["score"],
                     "verdict": verdict,
                     "category": categorise(d["decision"], verdict),
                     "stratum": key[pid]["stratum"] if key else None})

    counts = Counter(r["category"] for r in rows)
    result = {
        "counts": {c: counts[c] for c in CATEGORIES},
        "disagreements": [r for r in rows if r["category"] in DISAGREE],
        "unlabeled": [r["id"] for r in rows if r["category"] == "unlabeled"],
        "unknown_ids": unknown,
        "notes": notes,
        "strata": None,
    }
    if key is not None:
        strata = {}
        for stratum in dict.fromkeys(v["stratum"] for v in key.values()):
            sr = [r for r in rows if r["stratum"] == stratum]
            judged = [r for r in sr if r["category"] in
                      ("kept&relevant", "kept&not", "rejected&relevant",
                       "rejected&not")]
            errors = sum(1 for r in judged if r["category"] in DISAGREE)
            sc = Counter(r["category"] for r in sr)
            entry = {"drawn": len(sr), "n": len(judged), "errors": errors,
                     "unsure": sc["unsure"], "abstain": sc["abstain"],
                     "unlabeled": sc["unlabeled"], "wilson95": None}
            if judged:
                entry["wilson95"] = wilson(errors, len(judged))
            strata[stratum] = entry
        result["strata"] = strata
    return result


def report(result):
    out = ["Counts:"]
    for c in CATEGORIES:
        out.append(f"  {c:<18} {result['counts'][c]}")
    out.append("")
    out.append(f"Disagreements ({len(result['disagreements'])}):")
    for r in result["disagreements"]:
        out.append(f"  {r['id']} [{r['board']}] {r['title']!r}: filter "
                   f"{r['decision']} (score {r['score']}), verdict "
                   f"{r['verdict']}")
    if result["unlabeled"]:
        out.append("")
        out.append(f"Unlabeled ({len(result['unlabeled'])}), not counted: "
                   + ", ".join(result["unlabeled"]))
    if result["unknown_ids"]:
        out.append("")
        out.append("Ids not in the decisions file, not counted: "
                   + ", ".join(result["unknown_ids"]))
    if result["strata"] is not None:
        out.append("")
        out.append("Errors per audit stratum:")
        for stratum, e in result["strata"].items():
            line = (f"  {stratum}: {e['errors']} error(s) of {e['n']} "
                    f"labeled relevant/not (drawn {e['drawn']}; unsure "
                    f"{e['unsure']}, abstain {e['abstain']}, unlabeled "
                    f"{e['unlabeled']})")
            if e["wilson95"] is None:
                line += "; no interval: nothing labeled relevant/not"
            else:
                low, high = e["wilson95"]
                line += (f"; Wilson 95% [{low:.3f}, {high:.3f}], sample "
                         f"estimate (n={e['n']}), not a measured rate for "
                         "all postings")
            out.append(line)
    for note in result["notes"]:
        out.append(f"NOTE: {note}")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--verdicts", required=True)
    parser.add_argument("--key")
    args = parser.parse_args(argv)

    decisions = load_decisions(args.decisions)
    verdicts, problems = load_verdicts(args.verdicts)
    key = None
    if args.key:
        with open(args.key, encoding="utf-8") as handle:
            key = json.load(handle)["key"]
    result = measure(decisions, verdicts, key)
    result["notes"] = problems + result["notes"]
    print(report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
