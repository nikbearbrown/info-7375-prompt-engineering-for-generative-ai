"""Score the shortlist's claim labels: Aravind's committed labels against the sealed rule-based checker.

Reads the claims kit's LABELS.md and sealed/checker-labels.json, after checking the checker file's SHA-256 against
the one the kit's README published before any human label. Writes RESULTS.md in the kit folder: agreement by claim
type, the full table of label pairs, every disagreement with both reasons, and the topic claims on kept postings
that Aravind did not find supported (relevance is not entailment, chapter 7). Standard library only.

Only Aravind may mark a claim supported (FILTER.md Section 2); the checker is a second opinion, so "agreement" here
measures the checker against him, never the other way round.

Usage: python3 tools/score_claims.py js3/claims/<run>
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

NAMES = {"S": "supported", "C": "contradicted", "I": "insufficient"}
TYPES = {1: "1. full time (R1)", 2: "2. place (R2)", 3: "3. no level word (R3)", 4: "4. software engineering title (R4)",
         5: "5. no status requirement (R5)", 6: "6. no start before May 2027 (R6)", 7: "7. years (R7)",
         8: "8. topic group (the score)"}
ROW = re.compile(r"^\| \d{2}\.\d+[a-z]? \|")


def read_labels(path: Path) -> dict:
    """{claim id: (label or None, note)} from LABELS.md (an x under exactly one of Supported, Contradicted, Insufficient)."""
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not ROW.match(line):
            continue
        cells = re.split(r"(?<!\\)\|", line)
        marks = [k for k, i in (("S", 4), ("C", 5), ("I", 6)) if cells[i].strip().lower() == "x"]
        rows[cells[1].strip()] = (NAMES[marks[0]] if len(marks) == 1 else None, cells[7].strip())
    return rows


def read_flip_checks(path: Path) -> dict:
    """{claim: (label after, his words)} from FLIP-CHECKS.md.

    Chapter 7: for each disagreement, the sentence that would change his label, asked after the checker's labels
    were opened. LABELS.md is never edited, so agreement is reported both ways.
    """
    rows = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not ROW.match(line):
                continue
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)]
            # | Claim | Frozen label | Checker | The sentence(s) found | Label after | His words |
            if len(cells) == 8 and cells[5] in NAMES.values():
                rows[cells[1]] = (cells[5], cells[6])
    return rows


def published_hash(readme: Path) -> str:
    m = re.search(r"SHA-256 `([0-9a-f]{64})`", readme.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("STOP: the kit's README publishes no SHA-256")
    return m.group(1)


def score(kit: Path) -> dict:
    sealed = kit / "sealed" / "checker-labels.json"
    digest = hashlib.sha256(sealed.read_bytes()).hexdigest()
    if digest != published_hash(kit / "README.md"):
        raise SystemExit(f"STOP: sealed/checker-labels.json has SHA-256 {digest}, not the one the README published")
    checker = json.loads(sealed.read_text(encoding="utf-8"))
    labels = read_labels(kit / "LABELS.md")
    missing = [c["claim"] for c in checker["claims"] if labels.get(c["claim"], (None, ""))[0] is None]
    if missing:
        raise SystemExit(f"STOP: no label (or more than one) for claims {missing}")
    postings = {p["posting"]: p for p in checker["postings"]}
    rows = []
    for c in checker["claims"]:
        his, note = labels[c["claim"]]
        rows.append({"claim": c["claim"], "posting": c["posting"], "type": c["type"], "group": c.get("group"),
                     "text": c["text"], "his": his, "note": note, "checker": c["label"], "why": c["why"],
                     "agree": his == c["label"]})
    flips = read_flip_checks(kit / "FLIP-CHECKS.md")
    agree_after = sum(1 for r in rows if flips.get(r["claim"], (r["his"],))[0] == r["checker"])
    return {"digest": digest, "rows": rows, "postings": postings, "flips": flips, "agree_after": agree_after}


def write_results(kit: Path, s: dict) -> str:
    rows, postings = s["rows"], s["postings"]
    agree = sum(r["agree"] for r in rows)
    out = [f"# Claim labels against the checker, filter run {kit.name}", "",
           "Computed by `tools/score_claims.py` from Aravind's labels in LABELS.md (committed before the checker's labels "
           f"were opened) and `sealed/checker-labels.json` (SHA-256 `{s['digest']}`, the hash the kit's README published "
           "before any human label). Claude Code wrote the script and this file; the labels are his. Only he may mark a "
           "claim supported, so this measures the checker against him.", "",
           f"**Overall:** the checker agrees with him on {agree} of {len(rows)} claims.", "",
           "## By claim type", "", "| Claim type | Claims | Checker agrees | His labels (S / C / I) | Checker's (S / C / I) |",
           "|---|---:|---:|---|---|"]
    for t, name in TYPES.items():
        sub = [r for r in rows if r["type"] == t]
        if not sub:
            continue
        tally = lambda key: " / ".join(str(sum(1 for r in sub if r[key] == lab)) for lab in NAMES.values())
        out.append(f"| {name} | {len(sub)} | {sum(r['agree'] for r in sub)} | {tally('his')} | {tally('checker')} |")
    out += ["", "## Every pair of labels", "", "| His label | Checker's label | Claims |", "|---|---|---:|"]
    pairs = {}
    for r in rows:
        pairs[(r["his"], r["checker"])] = pairs.get((r["his"], r["checker"]), 0) + 1
    for (his, chk), n in sorted(pairs.items()):
        out.append(f"| {his} | {chk} | {n} |")
    out += ["", "## Every disagreement", "",
            "| Claim | Posting | Claim | His label | His note | Checker | Checker's reason |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        if not r["agree"]:
            title = postings[r["posting"]]["title"].strip()
            out.append(f"| {r['claim']} | {title} | {r['text']} | {r['his']} | {r['note']} | {r['checker']} | {r['why']} |")
    if s["flips"]:
        frozen = {r["claim"]: (r["his"], r["checker"]) for r in rows}
        out += ["", "## Flip checks (FLIP-CHECKS.md, chapter 7)", "",
                "For each disagreement, Claude Code found the sentence that bears most directly on the claim, after the "
                "checker's labels were opened, and Aravind said whether it changed his label. LABELS.md is unchanged.", "",
                "| Claim | His frozen label | Checker | His label after | His words |", "|---|---|---|---|---|"]
        for claim, (after, words) in sorted(s["flips"].items()):
            his, chk = frozen.get(claim, ("", ""))
            out.append(f"| {claim} | {his} | {chk} | {after} | {words} |")
        out += ["", f"After the flip checks, the checker agrees with him on {s['agree_after']} of {len(rows)} claims "
                f"(frozen: {agree} of {len(rows)})."]
    topic_i = [r for r in rows if r["type"] == 8 and r["his"] != "supported"]
    out += ["", "## Relevance is not entailment: topic claims on kept postings he did not find supported", "",
            "Every posting here was kept and shortlisted, and each topic group below added to its score. The quoted "
            "sentence is relevant (it contains the topic word), but he found that it does not say this role's work is in "
            "that group.", ""]
    if topic_i:
        out += ["| Claim | Posting (score) | Group | His note |", "|---|---|---|---|"]
        for r in topic_i:
            p = postings[r["posting"]]
            out.append(f"| {r['claim']} | {p['title'].strip()} ({p.get('score')}) | {r['group']} | {r['note']} |")
    else:
        out.append("None: he found every topic claim supported.")
    text = "\n".join(out) + "\n"
    (kit / "RESULTS.md").write_text(text, encoding="utf-8")
    return text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kit", type=Path)
    args = ap.parse_args(argv)
    s = score(args.kit)
    write_results(args.kit, s)
    rows = s["rows"]
    print(f"checker hash OK ({s['digest'][:12]}...); checker agrees with Aravind on "
          f"{sum(r['agree'] for r in rows)} of {len(rows)}; disagreements: "
          + ", ".join(r["claim"] for r in rows if not r["agree"]))
    print(f"wrote {args.kit / 'RESULTS.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
