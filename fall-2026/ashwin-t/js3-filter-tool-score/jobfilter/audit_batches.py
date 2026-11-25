"""The brief's minimum audit sample, shown in compact blind batches (written 2026-11-25 at Ashwin's request).

    python3 -m jobfilter.audit_batches     # writes labels/audit-minimum-batches.md

The brief asks for at least 30 random rejects, the closest calls near the threshold, and a sample of what was kept.
That is four strata of the selection already saved in labels/audit-selection.json, unchanged:
random_reject (30), close_below (6), close_at (5) and kept_random (6), 47 distinct postings. The other two strata,
exclusion_check and review, are optional extras; FILTER.md section 10 also lists the exclusion check as pending.

Each row shows only the posting's own fields and verbatim excerpts picked by fixed patterns (years of experience,
clearance or "US citizen"; the bare word "citizenship" is left out because it only matched equal-opportunity
boilerplate). No filter decision, score or stratum is shown. The `n` is the row number in
labels/audit-sheet.csv, where the verdict goes. labels/audit-ai-draft.csv (Codex's proposals) is not read here.
"""
from __future__ import annotations

import json
import re

from .audit import LABELS, SELECTION
from .claims import plain
from .corpus import load
from .sheets import locations

MINIMUM_STRATA = ("random_reject", "close_below", "close_at", "kept_random")
BATCH = 10
PATTERNS = {
    "experience": re.compile(r"\b\d+\s*\+?\s*(?:[-–]|to)?\s*\d*\s*\+?\s*years?\b", re.I),
    "clearance": re.compile(r"clearance|TS/SCI|top secret|\bU\.?S\.? citizen(?!ship)", re.I),
}
CLEARANCE_RULE = ("Ashwin's labeling rule (given in chat, 2026-11-25): if a posting needs a security clearance and Supriya's "
                  "eligibility is unknown, the verdict is `?`. Being willing to get a clearance does not count as being "
                  "eligible. Supriya's persona file says nothing about citizenship or clearance, so her eligibility is unknown.")


def minimum_keys(selection: dict) -> set:
    return {k for s in MINIMUM_STRATA for k in selection["strata"][s]["selected"]}


def excerpts(text: str, pattern, limit: int = 2, width: int = 70) -> list:
    out = []
    for m in pattern.finditer(text):
        s = text[max(0, m.start() - width):m.end() + width].strip()
        if not any(m.group(0) in o for o in out):
            out.append("…" + s + "…")
        if len(out) == limit:
            break
    return out


def write_batches() -> int:
    sel = json.loads(SELECTION.read_text())
    keep = minimum_keys(sel)
    n_of = {k: i for i, k in enumerate(sel["sheet_order"], 1)}
    order = [k for k in sel["sheet_order"] if k in keep]
    by = {p["key"]: p for p in load()["postings"]}
    L = ["# Minimum reject-audit sample, in batches (blind)", "",
         f"{len(order)} postings: the brief's minimum, taken unchanged from the saved selection (seed {sel['seed']}). "
         "The filter's decision, score and the reason each was drawn are not shown. Write each verdict (Y / N / ?) in "
         "`audit-sheet.csv` on row `n`, or reply in chat with the n and the verdict. Full text: the same `n` in "
         "`audit-sheet.md`.", "",
         "Question: " + "“Would Supriya want to see this posting for a full-time early-career software/backend "
         "search, with Boston or US remote preferred and other US locations worth considering?” (FILTER.md §8)", "",
         CLEARANCE_RULE, "",
         "Excerpts are matched by fixed patterns. They are not judgments, and they can miss things.", ""]
    for b in range(0, len(order), BATCH):
        L += [f"## Batch {b // BATCH + 1} ({b + 1}–{min(b + BATCH, len(order))} of {len(order)})", "",
              "| n | Title | Board | Locations | Experience excerpts | Clearance excerpts |", "|---:|---|---|---|---|---|"]
        for k in order[b:b + BATCH]:
            p = by[k]
            text = plain(p["content"])
            cell = lambda xs: "<br>".join(x.replace("|", "/") for x in xs) or "—"
            L.append(f"| {n_of[k]} | {p['title']} | {p['board']} | {'; '.join(locations(p)) or '(none)'} | "
                     f"{cell(excerpts(text, PATTERNS['experience']))} | {cell(excerpts(text, PATTERNS['clearance']))} |")
        L.append("")
    (LABELS / "audit-minimum-batches.md").write_text("\n".join(L) + "\n")
    print(f"labels/audit-minimum-batches.md: {len(order)} postings in {-(-len(order) // BATCH)} batches")
    return len(order)




# Review cards (2026-11-25): per posting, verbatim excerpts for duties, requirements, employment type and clearance,
# found by fixed section headings. "not found" means the pattern found nothing, not that the posting is silent.
# Headings are tried in order, most specific first; the first one found wins. A bare "requirements" only counts
# when a colon follows it, because Klaviyo's opening boilerplate says "beyond the traditional job requirements".
DUTIES = [re.compile(x, re.I) for x in (r"what you'?ll do", r"what you will do", r"core responsibilities",
                                        r"responsibilities\s*:", r"the role\b", r"about the role", r"your impact",
                                        r"in this role,? you")]
REQUIRES = [re.compile(x, re.I) for x in (r"what we require", r"what you bring", r"skills you'?ll need to bring",
                                          r"who you are", r"what we'?re looking for", r"minimum qualifications",
                                          r"qualifications\s*:", r"requirements\s*:", r"you might be a (?:good|great) fit")]
EMPLOYMENT = re.compile(r"\b(full[- ]time|part[- ]time|intern(?:ship)?|contractor|contract (?:role|position)|"
                        r"contract[- ]to[- ]hire|temporary|fixed[- ]term)\b", re.I)


def _after(text: str, patterns, width: int = 260) -> str:
    for pattern in patterns:
        m = pattern.search(text)
        if m:
            return "…" + text[m.start():m.end() + width].strip() + "…"
    return ""


def card(n: int, p: dict) -> list:
    text = plain(p["content"])
    st = p.get("structured") or {}
    declared = st.get("commitment") or st.get("employmentType")
    in_text = sorted({m.group(1).lower() for m in EMPLOYMENT.finditer(p["title"] + " " + text)})
    missing = []
    duties, req = _after(text, DUTIES), _after(text, REQUIRES)
    years = excerpts(text, PATTERNS["experience"], limit=3, width=50)
    clear = excerpts(text, PATTERNS["clearance"], limit=2, width=60)
    if not duties:
        missing.append("duties heading")
    if not req:
        missing.append("requirements heading")
    if not years:
        missing.append("years of experience")
    if not declared:
        missing.append("declared employment type")
    workplace = ", ".join(f"{k} {v}" for k, v in st.items() if k in ("workplaceType", "isRemote", "country")) or "none given"
    L = [f"### {n}. {p['title']}", "",
         f"- **Board / link:** {p['provider']}/{p['board']} · {p['absolute_url']}",
         f"- **Location:** {'; '.join(locations(p)) or '(none)'} · structured: {workplace}",
         f"- **Employment type:** declared {declared or 'none'}; words in title/text: {', '.join(in_text) or 'none'}",
         f"- **Duties:** {duties or 'not found'}",
         f"- **Requirements:** {req or 'not found'}",
         f"- **Years mentioned:** {' / '.join(years) or 'none found'}",
         f"- **Clearance:** {' / '.join(clear) or 'none found'}",
         f"- **Flags:** {', '.join(missing) or 'none'}", ""]
    return [x.replace("|", "/") for x in L]


def write_cards() -> None:
    sel = json.loads(SELECTION.read_text())
    keep = minimum_keys(sel)
    n_of = {k: i for i, k in enumerate(sel["sheet_order"], 1)}
    order = [k for k in sel["sheet_order"] if k in keep]
    by = {p["key"]: p for p in load()["postings"]}
    L = ["# Review cards for the minimum audit sample (blind)", "",
         "Verbatim excerpts found by fixed headings and patterns. They can miss or mis-cut text; open the link or "
         "`audit-sheet.md` (same n) when a field says not found. No filter output and no suggested verdict is shown.", "",
         CLEARANCE_RULE, ""]
    for b in range(0, len(order), BATCH):
        L += [f"## Batch {b // BATCH + 1}", ""]
        for k in order[b:b + BATCH]:
            L += card(n_of[k], by[k])
    (LABELS / "audit-review-cards.md").write_text("\n".join(L) + "\n")
    print(f"labels/audit-review-cards.md: {len(order)} cards")


if __name__ == "__main__":
    write_batches()
    write_cards()
