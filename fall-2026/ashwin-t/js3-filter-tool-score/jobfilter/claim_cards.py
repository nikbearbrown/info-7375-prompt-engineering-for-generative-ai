"""Claim review cards for Ashwin's S / C / I labels (written 2026-11-25 at Ashwin's request).

    python3 -m jobfilter.claim_cards        # writes shortlist/claim-review-cards.md (batches of 10)

Each card shows the exact claim and quote from shortlist/claim-sheet.csv. It adds the quote in context from the named
field, so the reader can judge it against the posting. For an "I cannot tell" claim (no quote), it adds verbatim
excerpts that fixed patterns find on that topic. No mechanical result and no suggested label is shown.
"""
from __future__ import annotations

import csv
import re

from .claims import ABSTAIN, OUT, _match_form, plain
from .corpus import load
from .sheets import locations

BATCH = 10
DEFINITIONS = [
    "- **S** (supported): the posting explicitly states the claim, or a faithful paraphrase of it.",
    "- **C** (contradicted): the posting states something incompatible with the claim.",
    "- **I** (insufficient): the posting is silent or ambiguous, or has only a related word without establishing the claim.",
    "- For an **\"I cannot tell\"** claim: **S** if the posting really does not settle the question, **C** if it does "
    "settle it (the abstention was wrong). FILTER.md section 5 has the full rules.",
]
TOPICS = {
    "experience": re.compile(r"\b\d+\s*\+?\s*(?:[-–]|to)?\s*\d*\s*\+?\s*years?\b|new grad|entry[- ]level|early career|"
                             r"all levels|recent(?:ly)? (?:graduate|completed)|junior|senior|seniority", re.I),
    "remote": re.compile(r"remote|hybrid|on-?site|in[- ]office|in person|work from|relocat", re.I),
}


def context(text: str, quote: str, width: int = 160) -> str:
    """The quote in its surrounding text, located in the same normalized form the mechanical check uses."""
    t, q = _match_form(text), _match_form(quote)
    i = t.find(q)
    if i < 0:
        return ""
    return "…" + t[max(0, i - width):i + len(q) + width] + "…"


def topic_excerpts(text: str, claim: str, limit: int = 3, width: int = 90) -> list:
    topic = "remote" if re.search(r"remote", claim, re.I) else "experience"
    out = []
    for m in TOPICS[topic].finditer(text):
        s = "…" + text[max(0, m.start() - width):m.end() + width].strip() + "…"
        if not any(m.group(0) in o for o in out):
            out.append(s)
        if len(out) == limit:
            break
    return out


def write_cards() -> int:
    rows = list(csv.DictReader((OUT / "claim-sheet.csv").open()))  # labels are not shown on the cards
    by = {p["key"]: p for p in load()["postings"]}
    L = ["# Claim review cards (90 claims, batches of 10)", "",
         "Claims Claude wrote on 2026-11-25 for the 18 shortlisted postings, in `claim-sheet.csv` order. Write S, C "
         "or I for each claim number, or reply in chat. No suggested label is shown.", ""] + DEFINITIONS + [""]
    for i, r in enumerate(rows, 1):
        if (i - 1) % BATCH == 0:
            L += [f"## Batch {(i - 1) // BATCH + 1} (claims {i}–{min(i + BATCH - 1, len(rows))})", ""]
        p = by[r["key"]]
        field = {"title": p["title"], "location": "; ".join(locations(p)), "content": plain(p["content"])}[r["field"]]
        st = p.get("structured") or {}
        L += [f"### {i}. `{r['claim_id']}` · {p['title']} · {'; '.join(locations(p))}", "",
              f"- **Claim:** {r['claim']}",
              "- **Structured fields (not shown to Claude):** "
              + (", ".join(f"{k} {v}" for k, v in st.items()) or "none")]
        if r["claim"].startswith(ABSTAIN):
            ex = topic_excerpts(plain(p["content"]), r["claim"])
            L += ["- **Quote:** none (abstention)",
                  "- **What the posting says on this topic (pattern excerpts):** " + (" / ".join(ex) if ex else "none found")]
        else:
            ctx = context(field, r["quote"])
            L += [f"- **Quote ({r['field']}):** \"{r['quote']}\"",
                  f"- **In context (lowercased for matching):** {ctx or 'the quote was not found in this field'}"]
            if re.search(r"remote|experience|years|level|new grad", r["claim"], re.I):
                ex = topic_excerpts(plain(p["content"]), r["claim"])
                L.append("- **Posting text on this topic (pattern excerpts):** " + (" / ".join(ex) if ex else "none found"))
        L += [f"- **Full posting:** {p['absolute_url']}", ""]
    (OUT / "claim-review-cards.md").write_text("\n".join(x.replace("|", "/") for x in L) + "\n")
    print(f"shortlist/claim-review-cards.md: {len(rows)} claims")
    return len(rows)


if __name__ == "__main__":
    write_cards()
