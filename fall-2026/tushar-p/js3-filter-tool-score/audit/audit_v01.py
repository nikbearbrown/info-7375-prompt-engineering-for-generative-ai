"""Reject audit of filter v0.1 against the blind hand labels (audit sheet only).

CLI: python audit/audit_v01.py            (run from js3-filter-tool-score/)

Reads audit/audit-sheet.csv, out/filter-v0.1/results.jsonl, the "audit" part of
out/filter-v0.1/sheet-key.json, and the posting text from evidence/runs/live-text-1.
Prints the numbers that audit/AUDIT-RESULTS.md reports. It never reads the held-out sheet
or the "heldout" part of the key, and it never changes the filter. The "what-if" counts in
the rule-gap section patch module constants in memory for this process only.
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
RESULTS = ROOT / "out" / "filter-v0.1" / "results.jsonl"
KEY = ROOT / "out" / "filter-v0.1" / "sheet-key.json"
SHEET = ROOT / "audit" / "audit-sheet.csv"
PERSONA = flt.DEFAULT_PERSONA

VERDICTS = ("keep", "reject", "cannot_tell")
STRATA = (("reject", "random rejects"), ("near_threshold", "near-threshold"),
          ("keep", "keeps"), ("cannot_tell", "cannot_tell"))
FALSE_FRIENDS = ("training", "agent", "pipeline", "model", "platform")
BOILERPLATE = {
    "Stripe": "Stripe is a financial infrastructure platform for businesses.",
    "Linear": "Linear has become the platform of choice",
}


def key(board, pid) -> tuple[str, str]:
    return board, str(pid)


def load():
    posts, failures = load_run(RUN)
    assert not failures, failures
    by_key = {key(p["board"], p["id"]): p for p in posts}
    results = {key(r["board"], r["id"]): r for r in map(json.loads, RESULTS.open(encoding="utf-8"))}
    audit_key = json.loads(KEY.read_text())["audit"]  # the held-out list is never read
    strata = {key(a["board"], a["id"]): a["stratum"] for a in audit_key}
    rows = list(csv.DictReader(SHEET.open(newline="", encoding="utf-8")))
    return posts, by_key, results, strata, rows


def deciding(result: dict) -> str:
    gate = result["first_failing_gate"] or result["first_unknown_gate"]
    if gate:
        g = result["gates"][gate]
        return f"{gate} {g['result']}" + (f": {', '.join(g['matched'])}" if g["matched"] else "")
    s = result["score"]
    return (f"score {s['total']} (topic {', '.join(s['topic']['matched']) or '-'}; "
            f"skills {', '.join(s['skills']['matched']) or '-'})")


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def matrix(pairs) -> str:
    counts = Counter(pairs)
    lines = ["| filter ↓ / me → | keep | reject | cannot_tell | total |", "|---|---|---|---|---|"]
    for f in VERDICTS:
        cells = [counts[(f, m)] for m in VERDICTS]
        lines.append(f"| **{f}** | " + " | ".join(map(str, cells)) + f" | {sum(cells)} |")
    cols = [sum(counts[(f, m)] for f in VERDICTS) for m in VERDICTS]
    lines.append("| total | " + " | ".join(map(str, cols)) + f" | {sum(cols)} |")
    return "\n".join(lines)


def sentence(text: str, start: int, end: int, width: int = 240) -> str:
    """The sentence around a match, cut to about `width` characters around it."""
    left = max(text.rfind(s, 0, start) for s in (". ", "? ", "! "))
    left = 0 if left < 0 else left + 2
    rights = [i for i in (text.find(s, end) for s in (". ", "? ", "! ")) if i >= 0]
    right = (min(rights) + 1) if rights else len(text)
    s = text[left:right]
    if len(s) > width:
        off = start - left
        s = "…" + s[max(0, off - width // 2): off + width // 2] + "…"
    return s


def section_rows(rows, results, strata):
    print("## a. Per-row table\n")
    print("| row | board | title | sample group | filter | deciding gate or score | me | note | agree |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        k = key(r["board"], r["id"])
        f = results[k]
        agree = "agree" if f["verdict"] == r["my_verdict"] else "**disagree**"
        print(f"| {r['row']} | {r['board']} | {r['title']} | {dict(STRATA)[strata[k]]} | {f['verdict']} | "
              f"{deciding(f)} | {r['my_verdict']} | {r['note'] or ''} | {agree} |")
    print()


def section_matrices(rows, results, strata):
    print("## b. Confusion matrices\n")
    pairs = [(results[key(r['board'], r['id'])]["verdict"], r["my_verdict"]) for r in rows]
    agree = sum(f == m for f, m in pairs)
    print(f"### Overall ({len(pairs)} rows, {agree} agree)\n\n{matrix(pairs)}\n")
    for stratum, name in STRATA:
        sub = [(results[key(r['board'], r['id'])]["verdict"], r["my_verdict"]) for r in rows
               if strata[key(r["board"], r["id"])] == stratum]
        print(f"### {name} ({len(sub)} rows, {sum(f == m for f, m in sub)} agree)\n\n{matrix(sub)}\n")


def section_random_rejects(rows, results, strata, n_rejects):
    print("## c. Random rejects\n")
    sub = [r for r in rows if strata[key(r["board"], r["id"])] == "reject"]
    mine = Counter(r["my_verdict"] for r in sub)
    gates = Counter(results[key(r["board"], r["id"])]["first_failing_gate"] for r in sub)
    k = mine["keep"] + mine["cannot_tell"]
    print(f"rows: {len(sub)}; my labels: {dict(mine)}; first failing gate: {dict(gates)}")
    for label, kk in (("not reject (keep or cannot_tell)", k), ("keep only", mine["keep"])):
        lo, hi = wilson(kk, len(sub))
        print(f"{label}: {kk}/{len(sub)} = {kk / len(sub):.1%}; Wilson 95% [{lo:.1%}, {hi:.1%}] "
              f"≈ {lo * n_rejects:.0f}–{hi * n_rejects:.0f} of {n_rejects} rejects")
    print()


def boilerplate_free(text: str) -> str:
    for s in BOILERPLATE.values():
        text = text.replace(s, " ")
    return text


def section_false_friends(posts, results, rows):
    print("## e. False-friend counts (whole-word, case-insensitive, as the filter matches)\n")
    audit_keys = {key(r["board"], r["id"]) for r in rows}
    print("| word | v0.1 term? | postings matched | stripe | notion | linear | audit rows | plural only |")
    print("|---|---|---|---|---|---|---|---|")
    for w in FALSE_FRIENDS + ("infrastructure", "AI"):
        pat, plural = word_pattern(w), word_pattern(w + "s")
        hits = [p for p in posts if pat.search(p["text"])]
        by = Counter(p["board"].split("/")[1] for p in hits)
        plural_only = sum(1 for p in posts if plural.search(p["text"]) and not pat.search(p["text"]))
        term = "topic word" if w in flt.TOPIC_WORDS else "no"
        n_audit = sum(1 for p in hits if key(p["board"], p["id"]) in audit_keys)
        print(f"| {w} | {term} | {len(hits)} | {by['stripe']} | {by['notion']} | {by['linear']} | "
              f"{n_audit} | {plural_only} |")
    print()
    for name, s in BOILERPLATE.items():
        n = sum(1 for p in posts if s in p["text"])
        print(f"boilerplate {name!r} ({s!r}): {n} postings")
    only_boiler = {w: 0 for w in ("platform", "infrastructure")}
    for p in posts:
        clean = boilerplate_free(p["text"])
        for w in only_boiler:
            if word_pattern(w).search(p["text"]) and not word_pattern(w).search(clean):
                only_boiler[w] += 1
    print(f"postings where the word appears ONLY in that boilerplate: {only_boiler}")
    gh_ai = sum(1 for p in posts if p["board"].startswith("greenhouse") and word_pattern("AI").search(p["text"]))
    print(f"greenhouse postings containing 'AI': {gh_ai} of "
          f"{sum(p['board'].startswith('greenhouse') for p in posts)}")
    print("\nscored postings (all gates pass) with and without the boilerplate sentences:")
    persona = flt.load_persona(PERSONA)
    for p in posts:
        r = results[key(p["board"], p["id"])]
        if r["score"] is None:
            continue
        s2 = flt.score(boilerplate_free(p["text"]), persona["skills"])
        print(f"  {p['board']} {p['id']} {p['title']!r}: score {r['score']['total']} "
              f"-> {s2['total']} without boilerplate (topic {s2['topic']['matched']})")
    print()


# ---------- rule gaps: forms present, and what-if counts ----------

_YEAR_1 = re.compile(r"(?<![\d.,])1\s*\+?\s*year(?![A-Za-z0-9])", re.I)
_PAREN_N = re.compile(r"\(\s*\d+\s*\)\s*\+?\s*(?:[-–—]\s*\S+\s*)?years?(?![A-Za-z0-9])", re.I)
def g4_whatif(singular: bool, parenthetical: bool) -> re.Pattern:
    """FILTER.md's four G4 forms, widened only by the one gap being tested."""
    n = r"(?<![\d.,])\(?(\d+)\)?" if parenthetical else r"(?<![\d.,])(\d+)"
    m = r"\(?\d+\)?" if parenthetical else r"\d+"
    yrs = r"years?" if singular else r"years"
    return re.compile(
        r"at\s+least\s+" + n + r"\s*\+?\s*" + yrs + r"(?![A-Za-z0-9])"
        r"|" + n + r"\s*\+?\s*[-–—]\s*" + m + r"\s*\+?\s*" + yrs + r"(?![A-Za-z0-9])"
        r"|" + n + r"\s*\+\s*" + yrs + r"(?![A-Za-z0-9])"
        r"|" + n + r"\s+" + yrs + r"\s+of(?![A-Za-z0-9])",
        re.I,
    )


def verdicts_with(posts, persona, **patches) -> dict:
    saved = {name: getattr(flt, name) for name in patches}
    try:
        for name, value in patches.items():
            setattr(flt, name, value)
        return {key(p["board"], p["id"]): flt.evaluate(p, persona) for p in posts}
    finally:
        for name, value in saved.items():
            setattr(flt, name, value)


def section_gaps(posts, results, rows):
    print("## f. Known rule gaps\n")
    persona = flt.load_persona(PERSONA)
    audit_keys = {key(r["board"], r["id"]): r["row"] for r in rows}
    gaps = {
        "Intern vs Internship (G2, title)": (
            lambda p: bool(word_pattern("Internship").search(p["title"] or ""))
            and not word_pattern("Intern").search(p["title"] or ""),
            {"G2_EXCLUDED": flt.G2_EXCLUDED + ("Internship",)}),
        "API vs APIs (topic word)": (
            lambda p: bool(word_pattern("APIs").search(p["text"])) and not word_pattern("API").search(p["text"]),
            {"TOPIC_WORDS": flt.TOPIC_WORDS + ("APIs",)}),
        "LLM vs LLMs (topic word)": (
            lambda p: bool(word_pattern("LLMs").search(p["text"])) and not word_pattern("LLM").search(p["text"]),
            {"TOPIC_WORDS": flt.TOPIC_WORDS + ("LLMs",)}),
        'G4 "1 year"': (lambda p: bool(_YEAR_1.search(p["text"])), {"_G4_PATTERN": g4_whatif(True, False)}),
        'G4 "two (2) years"': (lambda p: bool(_PAREN_N.search(p["text"])), {"_G4_PATTERN": g4_whatif(False, True)}),
    }
    for name, (has_form, patch) in gaps.items():
        present = [p for p in posts if has_form(p)]
        after = verdicts_with(posts, persona, **patch)
        gate_changed, verdict_changed = [], []
        for p in present:
            k = key(p["board"], p["id"])
            before, now = results[k], after[k]
            if any(before["gates"][g]["result"] != now["gates"][g]["result"] for g in flt.GATES) \
                    or (before["score"] or {}).get("total") != (now["score"] or {}).get("total"):
                gate_changed.append(p)
            if before["verdict"] != now["verdict"]:
                verdict_changed.append(p)
        in_audit = [f"row {audit_keys[key(p['board'], p['id'])]}" for p in present
                    if key(p["board"], p["id"]) in audit_keys]
        print(f"- {name}: form present in {len(present)} postings; what-if changes a gate result or "
              f"score in {len(gate_changed)}; changes the verdict in {len(verdict_changed)}; "
              f"audit rows with the form: {', '.join(in_audit) or 'none'}")
        for p in verdict_changed:
            k = key(p["board"], p["id"])
            print(f"    verdict change: {p['board']} {p['id']} {p['title']!r} "
                  f"{results[k]['verdict']} -> {after[k]['verdict']}")
        for p in present:
            m = (_YEAR_1 if "1 year" in name else _PAREN_N).search(p["text"]) if "G4" in name else None
            if m:
                print(f"    e.g. {p['board']} {p['id']} {p['title']!r} (G4 {results[key(p['board'], p['id'])]['gates']['G4']['result']}): "
                      f"{sentence(p['text'], m.start(), m.end(), 200)}")
            elif "G2" in name:
                print(f"    e.g. {p['board']} {p['id']} {p['title']!r} -> {results[key(p['board'], p['id'])]['verdict']} "
                      f"(first failing gate {results[key(p['board'], p['id'])]['first_failing_gate']})")
    print()


def main() -> int:
    posts, by_key, results, strata, rows = load()
    assert len(rows) == 48 and all(r["my_verdict"] in VERDICTS for r in rows)
    n_rejects = sum(r["verdict"] == "reject" for r in results.values())
    print(f"postings {len(posts)}; filter verdicts {dict(Counter(r['verdict'] for r in results.values()))}\n")
    section_rows(rows, results, strata)
    section_matrices(rows, results, strata)
    section_random_rejects(rows, results, strata, n_rejects)
    section_false_friends(posts, results, rows)
    section_gaps(posts, results, rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
