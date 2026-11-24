"""Held-out measurement for SCORE-REPORT.md section 2 (rules frozen at commit f3edf99).

CLI: python checks/score_report.py        (run from js3-filter-tool-score/)

Compares the blind hand labels in labels/heldout-sheet.csv (committed in f97f528a, before any
filter result was opened) with every rule mode: v0.1, each v0.1+Cn alone, and v0.2 combined.
Each single change is compared with v0.1 only; v0.2 is reported separately. Filter results are
computed in-process from evidence/runs/live-text-1 with the current agent/filter.py. Prints
markdown; SCORE-REPORT.md section 2 is this output verbatim (tests/test_score_report.py checks).
"""

import csv
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import filter as flt  # noqa: E402
from agent import sheets  # noqa: E402
from agent.postings import load_run  # noqa: E402

RUN = ROOT / "evidence" / "runs" / "live-text-1"
SHEET = ROOT / "labels" / "heldout-sheet.csv"
VERDICTS = ("keep", "reject", "cannot_tell")
SINGLE = tuple(f"v0.1+C{i}" for i in range(1, 7))
WHAT = {"C1": "G4: no stated experience passes", "C2": "G4: stated maximum that 0 years satisfies",
        "C3": "G4: cutoff 3 → 2", "C4": "G4: every mandatory minimum; mixed → unknown; preferred ignored",
        "C5": "topic words without \"platform\"", "C6": "G4: \"two (2) years\" forms"}


def wilson(k, n, z=1.959964):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def matrix(pairs) -> str:
    c = Counter(pairs)
    lines = ["| filter ↓ / me → | keep | reject | cannot_tell |", "|---|---|---|---|"]
    lines += [f"| **{f}** | " + " | ".join(str(c[(f, m)]) for m in VERDICTS) + " |" for f in VERDICTS]
    return "\n".join(lines)


def why(result: dict) -> str:
    """The gate or score that decided this verdict, with what it matched."""
    gate = result["first_failing_gate"] or result["first_unknown_gate"]
    if gate:
        g = result["gates"][gate]
        return f"{gate} {g['result']}" + (f" ({'; '.join(g['matched'])})" if g["matched"] else "")
    s = result["score"]
    return f"score {s['total']} (topic {', '.join(s['topic']['matched']) or '-'}; skills {', '.join(s['skills']['matched']) or '-'})"


def compute():
    postings, failures = load_run(RUN, with_blocks=True)
    assert not failures
    persona = flt.load_persona(flt.DEFAULT_PERSONA)
    by_key = {(p["board"], str(p["id"])): p for p in postings}
    rows = list(csv.DictReader(SHEET.open(newline="", encoding="utf-8")))
    assert len(rows) == 30 and all(r["my_verdict"] in VERDICTS for r in rows)
    assert not any(r["note"].startswith("[corrected") for r in rows), "held-out labels must be the blind ones"
    modes = ("v0.1", *SINGLE, "v0.2")
    everything = {m: {k: flt.evaluate(p, persona, flt.RULE_MODES[m]) for k, p in by_key.items()} for m in modes}
    results = {m: [everything[m][(r["board"], r["id"])] for r in rows] for m in modes}
    # The pool the held-out rows were drawn from: postings not on the audit sheet (agent/sheets.py).
    drawn = sheets.select(list(everything["v0.1"].values()))
    audit = set(drawn["audit"])
    pool = [k for k in by_key if k not in audit]
    assert {(r["board"], r["id"]) for r in rows} <= set(pool)
    return rows, results, everything, pool


def p_none(movable: int, pool: int, n: int = 30) -> float:
    """Probability that a random n of `pool` contains none of `movable` postings."""
    return math.comb(pool - movable, n) / math.comb(pool, n)


def report(rows, results, everything, pool) -> str:
    out = []
    labels = Counter(r["my_verdict"] for r in rows)
    out.append(f"Held-out labels (blind, commit f97f528a): {labels['keep']} keep, {labels['reject']} reject, "
               f"{labels['cannot_tell']} cannot_tell; 30 rows.\n")
    always = sum(r["my_verdict"] == "reject" for r in rows)
    out.append(f"Baseline: a filter that rejects every posting would agree on {always}/30.\n")
    out.append("### Agreement per mode\n")
    out.append("| mode | change | agree / 30 | % | Wilson 95% | rows changed vs v0.1 | of those, now agree / now disagree |")
    out.append("|---|---|---|---|---|---|---|")
    base = results["v0.1"]
    for m in ("v0.1", *SINGLE, "v0.2"):
        k = sum(res["verdict"] == r["my_verdict"] for res, r in zip(results[m], rows))
        lo, hi = wilson(k, 30)
        changed = [(r, a, b) for r, a, b in zip(rows, base, results[m]) if a["verdict"] != b["verdict"]]
        fixed = sum(b["verdict"] == r["my_verdict"] for r, _, b in changed)
        broke = sum(a["verdict"] == r["my_verdict"] for r, a, _ in changed)
        change = "—" if m == "v0.1" else ("C1–C6 combined" if m == "v0.2" else WHAT[m[5:]])
        moved = "—" if m == "v0.1" else str(len(changed))
        net = "—" if m == "v0.1" else f"{fixed} / {broke}"
        out.append(f"| {m} | {change} | {k} | {k / 30:.1%} | {lo:.1%} – {hi:.1%} | {moved} | {net} |")
    out.append("\n### Why the held-out set cannot separate the modes\n")
    pool_v01 = Counter(everything["v0.1"][k]["verdict"] for k in pool)
    out.append(f"The held-out rows were drawn at random from the {len(pool)} postings not on the audit sheet "
               f"(agent/sheets.py, seed 7375). Under v0.1 that pool holds {pool_v01['keep']} keep, "
               f"{pool_v01['reject']} reject and {pool_v01['cannot_tell']} cannot_tell, because the audit sheet "
               f"took every v0.1 keep and 10 of the 20 cannot_tell.\n")
    out.append("| mode | pool postings whose verdict differs from v0.1 | chance a random 30 of the pool includes none |")
    out.append("|---|---|---|")
    for m in (*SINGLE, "v0.2"):
        movable = sum(everything[m][k]["verdict"] != everything["v0.1"][k]["verdict"] for k in pool)
        out.append(f"| {m} | {movable} | {p_none(movable, len(pool)):.0%} |")
    gates = Counter(r["first_failing_gate"] or r["first_unknown_gate"] or "score" for r in results["v0.2"])
    out.append(f"\nIn v0.2 the 30 held-out verdicts are decided by: "
               + ", ".join(f"{g} {n}" for g, n in sorted(gates.items())) + ". "
               "C1–C4 and C6 change only G4 and C5 only the score, so a row rejected at G1, G2 or G3 cannot move.\n")
    out.append("### Held-out disagreements (identical in every mode)\n")
    out.append("| row | title | locations | me | filter (all modes) | decided by (v0.1) | decided by (v0.2) |")
    out.append("|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows):
        a, b = results["v0.1"][i], results["v0.2"][i]
        if a["verdict"] != r["my_verdict"]:
            assert all(results[m][i]["verdict"] == a["verdict"] for m in results)
            out.append(f"| {r['row']} | {r['title']} | {r['locations']} | {r['my_verdict']} | {a['verdict']} | "
                       f"{why(a)} | {why(b)} |")
    for m in ("v0.1", *SINGLE, "v0.2"):
        title = f"### {m}" + (" (combined; reported separately)" if m == "v0.2" else "")
        out.append(f"\n{title}\n")
        out.append(matrix([(res["verdict"], r["my_verdict"]) for res, r in zip(results[m], rows)]))
        if m == "v0.1":
            continue
        changed = [(r, a, b) for r, a, b in zip(rows, base, results[m]) if a["verdict"] != b["verdict"]]
        if not changed:
            out.append("\nNo held-out row changes verdict versus v0.1.")
            continue
        out.append("\n| row | title | v0.1 | " + m + " | me | v0.1 decided by | " + m + " decided by | responsible |")
        out.append("|---|---|---|---|---|---|---|---|")
        for r, a, b in changed:
            if m == "v0.2":
                movers = [s[5:] for s in SINGLE
                          if results[s][rows.index(r)]["verdict"] != a["verdict"]]
                responsible = ", ".join(movers) if movers else "only in combination"
            else:
                responsible = m[5:]
            out.append(f"| {r['row']} | {r['title']} | {a['verdict']} | {b['verdict']} | {r['my_verdict']} | "
                       f"{why(a)} | {why(b)} | {responsible} |")
    return "\n".join(out) + "\n"


def main() -> int:
    print(report(*compute()), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
