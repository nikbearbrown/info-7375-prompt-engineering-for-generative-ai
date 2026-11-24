"""Development measurement of FILTER.md v0.2 on the AUDIT sheet only, plus the infrastructure check.

CLI: python audit/audit_v02.py            (run from js3-filter-tool-score/)

Every rule mode is evaluated in-process on evidence/runs/live-text-1 with the current
agent/filter.py (the same code `python -m agent.filter --rules MODE` runs). Labels come from
audit/audit-sheet.csv only. The held-out sheet and the "heldout" part of the sheet key are never
read. Blind labels are recovered from the labeler's correction history in each note
("[corrected DATE: was X ...]"); rows without that history were never corrected.
"""

import csv
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import filter as flt  # noqa: E402
from agent.postings import load_run  # noqa: E402
from agent.text import word_pattern  # noqa: E402

RUN = ROOT / "evidence" / "runs" / "live-text-1"
KEY = ROOT / "out" / "filter-v0.1" / "sheet-key.json"
SHEET = ROOT / "audit" / "audit-sheet.csv"
VERDICTS = ("keep", "reject", "cannot_tell")
MODES = ("v0.1", "v0.1+C1", "v0.1+C2", "v0.1+C3", "v0.1+C4", "v0.1+C5", "v0.1+C6", "v0.2")
_CORRECTED = re.compile(r"^\[corrected [^:]+: was (keep|reject|cannot_tell)[ \],]")

# Company-description sentences ("About Stripe"), chosen by reading every sentence containing
# "infrastructure" that repeats in 4+ postings. Sentences about the role are not boilerplate.
INFRA_BOILERPLATE = (
    "Stripe is a financial infrastructure platform for businesses.",
    "is a financial infrastructure platform for businesses.",
    "We build entirely new pieces of financial infrastructure to enable new ideas.",
    "The most ambitious companies in the world use Stripe as core infrastructure to grow faster.",
    "And our significant advances in risk and fraud infrastructure over many years are making the "
    "internet economy safer and more accessible.",
    "We build programmable financial infrastructure, rethinking from first principles how financial "
    "services should work, to make it easier and cheaper for any business to start and scale.",
)


def key(board, pid):
    return board, str(pid)


def wilson(k, n, z=1.959964):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def labels():
    rows = list(csv.DictReader(SHEET.open(newline="", encoding="utf-8")))
    for r in rows:
        m = _CORRECTED.match(r["note"])
        r["blind"] = m.group(1) if m else r["my_verdict"]
        r["corrected"] = bool(m)
    return rows


def main() -> int:
    postings, failures = load_run(RUN, with_blocks=True)
    assert not failures
    persona = flt.load_persona(flt.DEFAULT_PERSONA)
    results = {m: {key(p["board"], p["id"]): flt.evaluate(p, persona, flt.RULE_MODES[m]) for p in postings}
               for m in MODES}
    strata = {key(a["board"], a["id"]): a["stratum"] for a in json.loads(KEY.read_text())["audit"]}
    rows = labels()
    assert len(rows) == 48

    print("## Verdict counts per mode (979 postings)\n")
    print("| mode | keep | reject | cannot_tell |\n|---|---|---|---|")
    for m in MODES:
        c = Counter(r["verdict"] for r in results[m].values())
        print(f"| {m} | {c['keep']} | {c['reject']} | {c['cannot_tell']} |")

    print("\n## Random-reject misses (v0.1 rejects; 30 random of 951)\n")
    rr = [r for r in rows if strata[key(r["board"], r["id"])] == "reject"]
    for name, field in (("blind labels (commit f97f528a)", "blind"),
                        ("after post-unblinding corrections", "my_verdict")):
        mine = Counter(r[field] for r in rr)
        k = mine["keep"] + mine["cannot_tell"]
        lo, hi = wilson(k, len(rr))
        print(f"- {name}: {k}/{len(rr)} not reject ({dict(mine)}); Wilson 95% [{lo:.1%}, {hi:.1%}] "
              f"≈ {lo * 951:.0f}–{hi * 951:.0f} of 951")
    print(f"- corrected rows: {[r['row'] for r in rows if r['corrected']]}")

    print("\n## Agreement on the audit sheet (48 rows; development data)\n")
    print("| mode | agree, blind labels | agree, corrected labels | keep | reject | cannot_tell |")
    print("|---|---|---|---|---|---|")
    for m in MODES:
        v = [results[m][key(r["board"], r["id"])]["verdict"] for r in rows]
        blind = sum(a == r["blind"] for a, r in zip(v, rows))
        corr = sum(a == r["my_verdict"] for a, r in zip(v, rows))
        c = Counter(v)
        print(f"| {m} | {blind}/48 | {corr}/48 | {c['keep']} | {c['reject']} | {c['cannot_tell']} |")

    print("\n## v0.2 confusion vs corrected labels (filter rows, me columns)\n")
    pairs = Counter((results["v0.2"][key(r["board"], r["id"])]["verdict"], r["my_verdict"]) for r in rows)
    print("| filter ↓ / me → | keep | reject | cannot_tell |\n|---|---|---|---|")
    for f in VERDICTS:
        print(f"| **{f}** | " + " | ".join(str(pairs[(f, mm)]) for mm in VERDICTS) + " |")

    print("\n## Audit rows whose verdict changes, v0.1 → v0.2\n")
    print("| row | title | v0.1 | v0.2 | v0.2 G4 | me (corrected) | changes that move it alone |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        k = key(r["board"], r["id"])
        a, b = results["v0.1"][k], results["v0.2"][k]
        if a["verdict"] != b["verdict"]:
            movers = [m[5:] for m in MODES[1:-1] if results[m][k]["verdict"] != a["verdict"]]
            print(f"| {r['row']} | {r['title']} | {a['verdict']} | {b['verdict']} | "
                  f"{b['gates']['G4']['result']}: {'; '.join(b['gates']['G4']['matched']) or '-'} | "
                  f"{r['my_verdict']} | {', '.join(movers) or 'only in combination'} |")

    print("\n## C4 preferred-heading amendment (2026-11-23): what it changed\n")
    print("Pre-amendment C4 = the same code with block kinds removed (no headings; own sentence only).\n")
    audit_rows = {key(r["board"], r["id"]): r["row"] for r in rows}
    for m in ("v0.1+C4", "v0.2"):
        rules = flt.RULE_MODES[m]
        before = {key(p["board"], p["id"]): flt.evaluate({k: v for k, v in p.items() if k != "block_kinds"},
                                                         persona, rules) for p in postings}
        after = results[m]
        g4 = [k for k in after if before[k]["gates"]["G4"] != after[k]["gates"]["G4"]]
        flips = [k for k in g4 if before[k]["gates"]["G4"]["result"] != after[k]["gates"]["G4"]["result"]]
        verdicts = [k for k in after if before[k]["verdict"] != after[k]["verdict"]]
        deciders = Counter(after[k]["first_failing_gate"] or after[k]["first_unknown_gate"] or "scored" for k in g4)
        print(f"- {m}: G4 output changed in {len(g4)} postings, G4 result changed in {len(flips)}, "
              f"verdict changed in {len(verdicts)}; the verdict of every G4-changed posting is decided by: "
              f"{dict(deciders)}")
        for k in g4:
            if k in audit_rows:
                print(f"  - audit row {audit_rows[k]} {after[k]['title']!r}: G4 {before[k]['gates']['G4']['result']} "
                      f"{before[k]['gates']['G4']['matched']} -> {after[k]['gates']['G4']['result']} "
                      f"{after[k]['gates']['G4']['matched']}; verdict {after[k]['verdict']} (unchanged)")
        if m == "v0.2":
            for k in flips:
                print(f"  - {k[0]} {k[1]} {after[k]['title']!r}: G4 {before[k]['gates']['G4']['result']} -> "
                      f"{after[k]['gates']['G4']['result']} {after[k]['gates']['G4']['matched']}; "
                      f"verdict {after[k]['verdict']} via {after[k]['first_failing_gate']}")

    print("\n## Infrastructure check (no rule change)\n")
    pat = word_pattern("infrastructure")
    only_boiler, examples = [], []
    for p in postings:
        text = p["text"] or ""
        if not pat.search(text):
            continue
        stripped = text
        for s in INFRA_BOILERPLATE:
            stripped = stripped.replace(s, " ")
        if not pat.search(stripped):
            only_boiler.append(p)
    with_word = sum(1 for p in postings if pat.search(p["text"] or ""))
    print(f"- postings containing 'infrastructure': {with_word}; only in company boilerplate: {len(only_boiler)}")
    print(f"- by board: {dict(Counter(p['board'] for p in only_boiler))}")
    for m in ("v0.1", "v0.2"):
        scored = [p for p in postings if results[m][key(p["board"], p["id"])]["score"] is not None]
        hit = [p for p in scored if p in only_boiler]
        keeps = [p for p in hit if results[m][key(p["board"], p["id"])]["verdict"] == "keep"]
        tipping = [p for p in keeps if results[m][key(p["board"], p["id"])]["score"]["topic"]["points"] - 1
                   + results[m][key(p["board"], p["id"])]["score"]["skills"]["points"] < flt.KEEP_THRESHOLD]
        print(f"- {m}: scored postings {len(scored)}; infrastructure point only from boilerplate {len(hit)}; "
              f"of those kept {len(keeps)}; keeps that would fall below 2 without that point {len(tipping)}"
              + (f" ({', '.join(repr(p['title']) for p in tipping)})" if tipping else ""))
    seen = set()
    for p in only_boiler:  # one example per boilerplate sentence, in INFRA_BOILERPLATE order
        for s in INFRA_BOILERPLATE:
            if s in p["text"] and s not in seen and not any(s in t for t in seen):
                seen.add(s)
                examples.append(f"  - {p['board']} {p['id']} {p['title']!r}: \"{s}\"")
                break
    examples = examples[:4]
    print("- examples:\n" + "\n".join(examples))
    return 0


if __name__ == "__main__":
    sys.exit(main())
