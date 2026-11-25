"""SHORTLIST.md: Tushar's claim labels vs Claude's proposed labels, entailment, abstention.

CLI: python checks/shortlist_report.py --section a|b|c|d|e        (run from js3-filter-tool-score/)

Inputs (all committed):
- labels/claims-sheet.csv: Tushar's labels, entered directly in the CSV as s/c/i (commit aaf850a0),
  committed before Claude's proposed labels were read. These are the reference.
- evidence/claims/claims-v1.jsonl: the live claim run (commit 65c97a2e); proposed_label is Claude's
  model judgment, not ground truth.
- labels/claims-texts/<posting_id>.txt: the posting text the labels were made against.
out/claims-key.json is gitignored; when present it is cross-checked, never required.

Rules are FILTER.md at f3edf99, unchanged. Section d applies the "I cannot tell" bullet "A shortlist
claim that the verdict depends on is insufficient" with the verdict-critical kinds role, location,
experience, sponsorship (agent/claims.py REQUIRED_KINDS). Each section prints markdown;
SHORTLIST.md holds each one verbatim (tests/test_shortlist_report.py checks).
"""

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import claims as cl  # noqa: E402
from agent import filter as flt  # noqa: E402

SHEET = ROOT / "labels" / "claims-sheet.csv"
RECORDS = ROOT / "evidence" / "claims" / "claims-v1.jsonl"
TEXTS = ROOT / "labels" / "claims-texts"
KEY = ROOT / "out" / "claims-key.json"  # optional cross-check only

LETTERS = {"s": "supported", "c": "contradicted", "i": "insufficient"}
LABELS = cl.LABELS  # supported, contradicted, insufficient
KINDS = cl.KINDS
CRITICAL = cl.REQUIRED_KINDS  # role, location, experience, sponsorship
SECTIONS = ("a", "b", "c", "d", "e")

# Section c: a claim's key words are FILTER.md's words for its kind. Role: the words of the G1
# titles. Seniority: the G2 words plus early-career words (hand-set for this report only; no rule
# uses them). Experience: "year(s)", "YOE", "experience". Location: any G3 US marker (the claim
# names the US; a quote names a US place). Sponsorship: the G5 phrases plus "sponsor(ship)",
# "visa". Skill: the persona skills the claim itself names, with "Postgres" for PostgreSQL.
ROLE_WORDS = ("Software", "Engineer", "Developer", "Backend", "Back-End", "Full Stack", "Full-Stack",
              "AI", "Machine Learning", "ML")
EARLY_CAREER_WORDS = ("junior", "entry-level", "entry level", "early career", "early-career",
                      "new grad", "new graduate")
SENIORITY_WORDS = flt.G2_EXCLUDED + EARLY_CAREER_WORDS
EXPERIENCE_WORDS = ("year", "YOE", "experience")
SPONSORSHIP_WORDS = flt.G5_PHRASES + ("sponsor", "sponsorship", "visa")
SKILL_ALIASES = {"PostgreSQL": ("PostgreSQL", "Postgres")}


def _cell(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _words_in(text: str, words) -> list[str]:
    """Each word found whole-word and case-insensitive; a trailing "s" (plural) also matches."""
    return [w for w in words
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(w)}s?(?![A-Za-z0-9])", text, re.IGNORECASE)]


def key_words(kind: str, claim: str, quote: str, skills) -> list[str]:
    """The claim's key words (see above) that occur in the quote, each once, in list order."""
    if kind == "location":
        found = flt.us_matches(quote)
    elif kind == "skill":
        named = [s for s in skills if _words_in(claim, SKILL_ALIASES.get(s, (s,)))]
        found = [w for s in named for w in _words_in(quote, SKILL_ALIASES.get(s, (s,)))]
    else:
        vocab = {"role": ROLE_WORDS, "seniority": SENIORITY_WORDS, "experience": EXPERIENCE_WORDS,
                 "sponsorship": SPONSORSHIP_WORDS}[kind]
        found = _words_in(quote, vocab)
    return list(dict.fromkeys(found))


def wilson(k, n, z=1.959964):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def _pct(k, n) -> str:
    if not n:
        return "–"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {100 * k / n:.1f}% (95% Wilson {100 * lo:.1f}–{100 * hi:.1f}%)"


# ---------------------------------------------------------------- loading

def load(sheet: Path = SHEET, records_path: Path = RECORDS, texts: Path = TEXTS, key: Path = KEY):
    """(rows, postings): one row per sheet line joined to its Claude claim; postings in sheet order."""
    with open(sheet, newline="", encoding="utf-8") as fh:
        sheet_rows = list(csv.DictReader(fh))
    records = cl.load_records(records_path)
    flat = [(r, i, c) for r in records if r["status"] == "ok" for i, c in enumerate(r["claims"])]
    if len(flat) != len(sheet_rows):
        raise ValueError(f"{len(sheet_rows)} sheet rows but {len(flat)} claims in {records_path.name}")
    key_rows = json.loads(key.read_text(encoding="utf-8"))["rows"] if key.exists() else None
    rows, postings = [], {}
    for n, (srow, (rec, i, c)) in enumerate(zip(sheet_rows, flat), start=1):
        if (int(srow["row"]), srow["posting_id"], srow["kind"], srow["claim"], srow["quote"]) != \
                (n, rec["posting_id"], c["kind"], c["claim"], c["quote"]):
            raise ValueError(f"sheet row {srow['row']} does not match claim {i} of {rec['posting_id']}")
        if key_rows is not None:
            k = key_rows[n - 1]
            if (k["row"], k["posting_id"], k["claim_index"], k["proposed_label"]) != \
                    (n, rec["posting_id"], i, c["proposed_label"]):
                raise ValueError(f"out/claims-key.json row {n} does not match {records_path.name}")
        letter = srow["my_label"].strip()
        if letter not in LETTERS:
            raise ValueError(f"sheet row {n}: my_label {letter!r} is not one of {sorted(LETTERS)}")
        rows.append({"row": n, "board": rec["board"], "posting_id": rec["posting_id"], "title": rec["title"],
                     "kind": c["kind"], "claim": c["claim"], "quote": c["quote"], "quote_found": c["quote_found"],
                     "me": LETTERS[letter], "claude": c["proposed_label"], "note": srow["note"]})
        if rec["posting_id"] not in postings:
            text_file = (texts / f"{rec['posting_id']}.txt").read_text(encoding="utf-8")
            head = dict(line.split(": ", 1) for line in text_file.split(cl.TEXT_MARKER)[0].splitlines() if ": " in line)
            postings[rec["posting_id"]] = {"board": rec["board"], "posting_id": rec["posting_id"],
                                           "title": rec["title"], "locations": head.get("locations", ""),
                                           "text": text_file.split(cl.TEXT_MARKER, 1)[1]}
    return rows, postings


def _skills():
    return flt.load_persona(flt.DEFAULT_PERSONA)["skills"]


# ---------------------------------------------------------------- computations

def agreement(rows) -> dict:
    by_kind = {k: [r for r in rows if r["kind"] == k] for k in KINDS}
    quoted = [r for r in rows if r["quote"] != ""]
    agree = lambda rs: sum(r["me"] == r["claude"] for r in rs)  # noqa: E731
    return {"overall": (agree(rows), len(rows)), "quoted": (agree(quoted), len(quoted)),
            "empty": (agree([r for r in rows if r["quote"] == ""]), len(rows) - len(quoted)),
            "by_kind": {k: (agree(rs), len(rs)) for k, rs in by_kind.items()},
            "matrix": Counter((r["me"], r["claude"]) for r in rows)}


def relevance_not_entailment(rows, skills) -> list[dict]:
    """Quote found and holds a key word of the claim, yet Tushar labeled it insufficient or contradicted."""
    out = []
    for r in rows:
        if r["quote_found"] is True and r["me"] in ("insufficient", "contradicted"):
            words = key_words(r["kind"], r["claim"], r["quote"], skills)
            if words:
                out.append({**r, "key_words": words})
    return out


def abstention(rows, postings) -> list[dict]:
    """Per posting: Tushar's label for each critical kind and the verdict the evidence rule gives."""
    out = []
    for pid, p in postings.items():
        mine = [r for r in rows if r["posting_id"] == pid]
        crit = {k: [r["me"] for r in mine if r["kind"] == k] for k in CRITICAL}
        insufficient = [k for k in CRITICAL if "insufficient" in crit[k]]
        contradicted = [k for k in CRITICAL if "contradicted" in crit[k]]
        out.append({**p, "critical": crit, "insufficient": insufficient, "contradicted": contradicted,
                    "verdict": "cannot_tell" if insufficient else "keep",
                    "sponsorship_words_in_text": _words_in(p["text"], SPONSORSHIP_WORDS)})
    return out


# ---------------------------------------------------------------- sections

def section_a(rows, postings) -> str:
    out = []
    for pid, p in postings.items():
        out += [f"#### {_cell(p['title'])} · {p['board']} · `{pid}`", "",
                f"Location fields: {_cell(p['locations'])}", "",
                "| row | claim | kind | quote | my label | Claude's label | agree? | my note |",
                "|---|---|---|---|---|---|---|---|"]
        for r in rows:
            if r["posting_id"] == pid:
                quote = f"\"{_cell(r['quote'])}\"" if r["quote"] else "*(empty)*"
                out.append(f"| {r['row']} | {_cell(r['claim'])} | {r['kind']} | {quote} | {r['me']} | "
                           f"{r['claude']} | {'yes' if r['me'] == r['claude'] else '**no**'} | {_cell(r['note'])} |")
        out.append("")
    return "\n".join(out)


def section_b(rows) -> str:
    a = agreement(rows)
    out = [f"- **Overall:** {_pct(*a['overall'])}.",
           f"- **Claims with a quote:** {_pct(*a['quoted'])}.",
           f"- **Claims with an empty quote:** {_pct(*a['empty'])}. The prompt contract forces an empty "
           "quote to be proposed insufficient, so this agreement is mechanical, not judgment.",
           "", "| kind | claims | agree | agreement |", "|---|---|---|---|"]
    for k in KINDS:
        agree, n = a["by_kind"][k]
        out.append(f"| {k} | {n} | {agree} | {100 * agree / n:.1f}% |" if n else f"| {k} | 0 | – | – |")
    m = a["matrix"]
    out += ["", "Confusion matrix (rows: my label, the reference; columns: Claude's proposed label):", "",
            "| me ↓ / Claude → | " + " | ".join(LABELS) + " | total |", "|---|---|---|---|---|"]
    for mine in LABELS:
        out.append(f"| **{mine}** | " + " | ".join(str(m[(mine, c)]) for c in LABELS)
                   + f" | {sum(m[(mine, c)] for c in LABELS)} |")
    out.append("| **total** | " + " | ".join(str(sum(m[(x, c)] for x in LABELS)) for c in LABELS)
               + f" | {len(rows)} |")
    dis = [r for r in rows if r["me"] != r["claude"]]
    pairs = Counter((r["me"], r["claude"]) for r in dis)
    out += ["", f"Disagreements: {len(dis)} (rows {', '.join(str(r['row']) for r in dis)}). "
            + "; ".join(f"me {x}, Claude {y}: {n}" for (x, y), n in sorted(pairs.items())) + "."]
    return "\n".join(out)


def section_c(rows, skills) -> str:
    found = relevance_not_entailment(rows, skills)
    out = [f"{len(found)} claims have a found quote that holds a key word of the claim, yet my label is "
           f"insufficient ({sum(r['me'] == 'insufficient' for r in found)}) or contradicted "
           f"({sum(r['me'] == 'contradicted' for r in found)}).", "",
           "| row | posting | kind | claim | quote | key words in quote | my label | Claude's label |",
           "|---|---|---|---|---|---|---|---|"]
    for r in found:
        out.append(f"| {r['row']} | {_cell(r['title'])} | {r['kind']} | {_cell(r['claim'])} | \"{_cell(r['quote'])}\" | "
                   f"{', '.join(r['key_words'])} | {r['me']} | {r['claude']} |")
    return "\n".join(out)


def section_d(rows, postings) -> str:
    ab = abstention(rows, postings)
    keep = [p for p in ab if p["verdict"] == "keep"]
    out = [f"- **Shortlisted postings:** {len(ab)} (every v0.2 keep).",
           f"- **Stay keep:** {len(keep)}.",
           f"- **Become cannot_tell:** {len(ab) - len(keep)}.", "",
           "| posting | role | location | experience | sponsorship | insufficient critical kinds | verdict |",
           "|---|---|---|---|---|---|---|"]
    for p in ab:
        cells = [", ".join(p["critical"][k]) for k in CRITICAL]
        out.append(f"| {_cell(p['title'])} `{p['posting_id']}` | " + " | ".join(cells)
                   + f" | {', '.join(p['insufficient']) or '–'} | {p['verdict']} |")
    n = {k: sum(k in p["insufficient"] for p in ab) for k in CRITICAL}
    out += ["", "Postings with each critical kind insufficient: "
            + ", ".join(f"{k} {n[k]}" for k in CRITICAL) + "."]
    contra = [p for p in ab if p["contradicted"]]
    out += ["", f"Postings with a contradicted critical claim: {len(contra)}"
            + (" (" + ", ".join(f"`{p['posting_id']}` {'/'.join(p['contradicted'])}" for p in contra) + ")" if contra else "")
            + ". FILTER.md's evidence rules say what an insufficient critical claim does, not what a contradicted "
            "one does; all of these are already cannot_tell through an insufficient claim, so the count above "
            "does not depend on that gap."]
    return "\n".join(out)


def section_e(rows, postings) -> str:
    ab = abstention(rows, postings)
    out = ["| posting | location fields (G3 reads these) | sponsorship words anywhere in the text | "
           "insufficient critical kinds | supported critical kinds |", "|---|---|---|---|---|"]
    for p in ab:
        supported = [k for k in CRITICAL if "supported" in p["critical"][k]]
        out.append(f"| {_cell(p['title'])} `{p['posting_id']}` | {_cell(p['locations'])} | "
                   f"{', '.join(p['sponsorship_words_in_text']) or 'none'} | {', '.join(p['insufficient']) or '–'} | "
                   f"{', '.join(supported) or '–'} |")
    silent = sum(not p["sponsorship_words_in_text"] for p in ab)
    all_supported = [p for p in ab if all(p["critical"][k] and set(p["critical"][k]) == {"supported"} for k in CRITICAL)]
    out += ["", f"Postings silent on sponsorship (no G5 phrase, \"sponsor\", \"sponsorship\" or \"visa\"): {silent} of {len(ab)}.",
            f"Postings with every critical claim supported: {len(all_supported)}."]
    return "\n".join(out)


def render(section: str) -> str:
    rows, postings = load()
    if section == "a":
        return section_a(rows, postings) + "\n"
    if section == "b":
        return section_b(rows) + "\n"
    if section == "c":
        return section_c(rows, _skills()) + "\n"
    if section == "d":
        return section_d(rows, postings) + "\n"
    return section_e(rows, postings) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python checks/shortlist_report.py", description=__doc__.splitlines()[0])
    parser.add_argument("--section", choices=SECTIONS, required=True)
    args = parser.parse_args(argv)
    sys.stdout.write(render(args.section))
    return 0


if __name__ == "__main__":
    sys.exit(main())
