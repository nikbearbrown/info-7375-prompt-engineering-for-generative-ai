"""Source-grounded shortlist: each kept posting's justification is split into claims, and each claim is labeled
supported / contradicted / insufficient against that posting's own text (FILTER.md §2).

  .venv/bin/python -m js3.shortlist --filter <version>   -> shortlist/SHORTLIST.md and shortlist/claims.json

Who labels what:
- ROLE, TOPIC: labeled by rule. Supported iff the phrase occurs, with the verbatim quote.
- LEVEL, LOCATION: labeled by rule, using the FILTER.md §2 evidence rules as written.
- DUTY: labeled by a reader, from shortlist/reader_labels.json (js3/reader_labels.py). Each entry records who labeled it.
- A reader check may override a rule-labeled LEVEL claim. Both labels are kept (rule_label, then label).
Every quote is checked to occur verbatim in the named field. A claim whose quote fails the check is an error.
Aditya's audit label, when the posting was on his sheet, is shown next to the verdict.
"""
import argparse
import json
import re
from pathlib import Path

from inherited.rules import contains_phrase, normalize

from .corpus import load_corpus
from .filter import load_filter, score_posting
from .text import quote_for, readable

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "shortlist"
LEVEL_WORDS = None  # taken from the filter file


def field_text(p, field):
    return {"posting.title": p["title"], "posting.description": readable(p["text"]),
            "posting.location": p["location"] or ""}[field]


def verify(p, claim):
    for ev in claim.get("evidence", []):
        if ev["quote"] not in field_text(p, ev["field"]):
            raise ValueError(f"{p['key']}: quote not verbatim in {ev['field']}: {ev['quote'][:80]!r}")


def level_claim(p, r, cfg):
    """LEVEL: 'open to someone with Priya's experience (one 8-month co-op; under 1 year full-time)'."""
    P = r["parts"]
    ev = []
    if P["S"]["match"]:
        m = P["S"]["match"]
        return "contradicted", [{"field": m["field"], "quote": m["quote"], "why": f"level word '{m['phrase']}' in title"}]
    years = [y for y in P["Y"]["matches"] if int(y["normalized"].split()[0]) >= 2]
    if years:
        ev = [{"field": "posting.description", "quote": y["quote"], "why": f"'{y['normalized']}' (N >= 2)"} for y in years]
        lab = "contradicted"
    else:
        lab = None
    if P["E"]["match"]:
        m = P["E"]["match"]
        ev.append({"field": m["field"], "quote": m["quote"], "why": f"early-career phrase '{m['phrase']}'"})
        lab = lab or "supported"
    return (lab or "insufficient"), ev


def location_claim(p):
    loc = p["location"] or ""
    n = normalize(loc)
    if not n:
        return "insufficient", []
    ev = [{"field": "posting.location", "quote": loc}]
    if contains_phrase(n, "boston"):
        return "supported", ev
    if contains_phrase(n, "remote") and any(contains_phrase(n, w) for w in ("us", "usa", "united states")):
        return "supported", ev
    if n in ("remote", "united states", "us", "usa", "north america"):
        return "insufficient", ev   # country-wide or unscoped: Boston/remote-US cannot be told from this field
    return "contradicted", ev


def build(version):
    cfg = load_filter(version)
    corpus = load_corpus()
    reader = json.loads((OUT / "reader_labels.json").read_text()) if (OUT / "reader_labels.json").exists() else {}
    aud = {}
    for f in ("dev_labels.csv", "heldout2_labels.csv"):
        path = ROOT / "labels" / f
        if path.exists():
            import csv
            with path.open(encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    aud[row["key"]] = f"{row['label']} ({row['reason']})" if row["reason"] else row["label"]
    entries = []
    for key, p in sorted(corpus.items()):
        r = score_posting(p, cfg)
        if r["verdict"] != "keep":
            continue
        P = r["parts"]
        claims = []
        m = P["R"]["match"]
        claims.append({"type": "ROLE", "claim": f"The title names a {P['R']['tier']} role ('{m['phrase']}').",
                       "label": "supported", "labeled_by": "rule", "evidence": [{"field": m["field"], "quote": m["quote"]}]})
        for g in P["T"]["groups"]:
            gname = g["group"].split(" ", 1)[1]
            claims.append({"type": "TOPIC", "claim": f"The posting mentions {gname} ('{g['phrase']}').",
                           "label": "supported", "labeled_by": "rule", "evidence": [{"field": g["field"], "quote": g["quote"]}]})
            d = reader.get(key, {}).get("DUTY", {}).get(g["group"])
            if d:
                claims.append({"type": "DUTY", "claim": f"The role itself involves {gname} work.", "label": d["label"],
                               "labeled_by": d["labeled_by"], "evidence": d.get("evidence", []), "note": d.get("note", "")})
            else:
                claims.append({"type": "DUTY", "claim": f"The role itself involves {gname} work.", "label": "unlabeled",
                               "labeled_by": None, "evidence": []})
        lab, ev = level_claim(p, r, cfg)
        level = {"type": "LEVEL", "claim": "The role is open to someone with Priya's experience (under 1 year full-time).",
                 "label": lab, "labeled_by": "rule (FILTER.md §2 C1)", "evidence": ev}
        rc = reader.get(key, {}).get("LEVEL")
        if rc:
            if rc.get("replace_rule_evidence"):  # rule label kept, its citation replaced; rule's quote stays on record
                level.update({"rule_label": lab, "rule_evidence": ev, "label": rc["label"],
                              "labeled_by": f"rule said {lab} (wrong citation) -> {rc['labeled_by']}",
                              "evidence": rc["evidence"], "note": rc["note"] + " Rule's original citation: " +
                              "; ".join(f"“{x['quote']}”" for x in ev)})
            else:
                level.update({"rule_label": lab, "label": rc["label"], "labeled_by": f"rule said {lab} -> {rc['labeled_by']}",
                              "evidence": ev + rc["evidence"], "note": rc["note"]})
        claims.append(level)
        lab, ev = location_claim(p)
        claims.append({"type": "LOCATION", "claim": "The role is in Boston or remote within the US.",
                       "label": lab, "labeled_by": "rule (FILTER.md §2)", "evidence": ev})
        for c in claims:
            verify(p, c)
        cannot = [c["type"] for c in claims if c["label"] == "insufficient" and c["type"] in ("LEVEL", "LOCATION")]
        entries.append({"key": key, "title": p["title"], "location": p["location"], "url": p["url"],
                        "score": r["score"], "arithmetic": r["arithmetic"], "aditya_label": aud.get(key),
                        "i_cannot_tell": cannot, "claims": claims})
    OUT.mkdir(exist_ok=True)
    (OUT / "claims.json").write_text(json.dumps({"filter": version, "entries": entries}, indent=1, ensure_ascii=False) + "\n")
    (OUT / "SHORTLIST.md").write_text(render(version, entries), encoding="utf-8")
    return entries


def render(version, entries):
    L = [f"# Shortlist: filter {version}", "",
         f"{len(entries)} kept postings. Each claim has a label, a source field and an exact quote. "
         "The quotes are verified verbatim by `js3/shortlist.py`, and any mismatch is an error. "
         "Labels by **rule** are mechanical, following FILTER.md §2. **DUTY** labels were made by a reader, "
         "who is named on each one. 'Aditya' is his blind audit label, where the posting was on his sheet.", ""]
    for e in entries:
        L += [f"## `{e['key']}`: {e['title']}", "",
              f"- score: `{e['arithmetic']}` → keep · location: {e['location']!r}",
              f"- Aditya: **{e['aditya_label'] or 'not on his sheet'}**"]
        for t in e["i_cannot_tell"]:
            L.append(f"- **I cannot tell** from this posting: {'whether it is open to her level' if t == 'LEVEL' else 'whether it is in Boston or remote-US'}")
        L += ["", "| claim | label | by | field: quote |", "|---|---|---|---|"]
        for c in e["claims"]:
            ev = "<br>".join(f"{x['field']}: “{_md(x['quote'][:220])}”" + (f" ({x['why']})" if x.get("why") else "")
                             for x in c["evidence"]) or ("—" if c["label"] != "insufficient" else "no span found")
            note = f" — {c['note']}" if c.get("note") else ""
            L.append(f"| {c['type']}: {c['claim']} | **{c['label']}** | {c['labeled_by'] or '—'} | {ev}{_md(note)} |")
        L.append("")
    return "\n".join(L)


def _md(s):
    return s.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", default="v1.0")
    a = ap.parse_args()
    es = build(a.filter)
    print(f"{len(es)} entries; claims: {sum(len(e['claims']) for e in es)}")
